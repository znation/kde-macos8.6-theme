"""Run a tools/ CLI's ``main`` in-process and capture its output.

The tool CLIs parse arguments with argparse, which exits through ``SystemExit``
for ``--help`` (0) and for a usage error (2), while ``main`` returns its status
otherwise. Tests that read only the exit status and printed diagnostics call
``main`` in-process instead of spawning ``python3 tools/<tool>.py``, exercising
the same parsing, output and statuses without paying interpreter startup and
module import per assertion. The script entry point itself stays covered once
per CLI by a ``test_script_entry_point``.
"""

from __future__ import annotations

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support.process_assertions import assert_succeeded
from support.repo_root import ROOT
from support.theme_install import run_captured
from support.tmp_dir import make_tmp_dir


def _call_capturing(call):
    """Call *call*, capturing stdout and stderr; return (status, stdout, stderr).

    A ``SystemExit`` becomes the status as the script wrapper's ``sys.exit``
    would report it: ``None`` is 0 and a non-int code is 1.
    """
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        try:
            status = call()
        except SystemExit as exc:
            status = 0 if exc.code is None else exc.code
            if not isinstance(status, int):
                status = 1
    return status, stdout.getvalue(), stderr.getvalue()


def run_main(main, program, args):
    """Call *main* with *args* and capture stdout/stderr as a CompletedProcess.

    *program* names the tool in the returned process's ``args``, so a failure
    message reads like the ``python3 tools/<program>.py`` invocation.
    """
    status, stdout, stderr = _call_capturing(lambda: main(list(args)))
    return subprocess.CompletedProcess(
        [program, *args], status, stdout, stderr
    )


def call_main(main, *args):
    """Call ``main(list(args))`` and return ``(status, stderr)``.

    Like ``run_main``, but for tests that read only the exit status and the
    diagnostics, not stdout or a ``CompletedProcess``. Passing an explicit
    list keeps a ``main(argv=None)`` from reading the test runner's own
    ``sys.argv``.
    """
    status, _, stderr = _call_capturing(lambda: main(list(args)))
    return status, stderr


def _write_tool_stub(directory, name):
    """Write an executable ``#!/bin/sh`` stub for *name* into *directory*."""
    tool = Path(directory) / name
    tool.write_text("#!/bin/sh\n", encoding="utf-8")
    tool.chmod(0o755)


def _run_without_tool(main, required, missing, argv):
    """Run *main* with a PATH holding every tool in *required* but *missing*."""
    with tempfile.TemporaryDirectory() as directory:
        for name in required:
            if name != missing:
                _write_tool_stub(directory, name)
        with mock.patch.dict(os.environ, {"PATH": directory}):
            return call_main(main, *argv)


def assert_missing_tool_named(case, main, required, argv=()):
    """Assert *main* names each tool in *required* when it alone is absent.

    *case* is the calling ``unittest.TestCase``, and *argv* is forwarded to
    *main*. For every entry in *required*, a temp directory holds executable
    stubs for the others and ``PATH`` is narrowed to it, so
    ``report_missing_tool`` sees exactly that one absent; the run must exit 2
    and print the missing tool last on stderr.
    """
    for missing in required:
        with case.subTest(missing=missing):
            status, stderr = _run_without_tool(main, required, missing, argv)
            case.assertEqual(2, status, stderr)
            case.assertTrue(stderr.rstrip().endswith(missing), stderr)


class CliTestCase(unittest.TestCase):
    """Base for a tools/ CLI's in-process test case.

    Subclasses set ``MAIN = staticmethod(<tool>.main)`` and ``PROGRAM`` to
    the tool's name, so a failure message reads like the
    ``python3 tools/<program>.py`` invocation. Every assertion in the case
    reads only the exit status and the printed diagnostics, both of which
    live in the tool's ``main``; spawning the script per assertion would pay
    interpreter startup and module import for each one. Calling ``main``
    in-process exercises the same argument parsing, output and statuses. Each
    CLI's script entry point stays covered once by its own
    ``test_script_entry_point``.
    """

    MAIN = None
    PROGRAM = None

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return run_main(self.MAIN, self.PROGRAM, args)

    def _run_script(self, *args: str) -> subprocess.CompletedProcess:
        """Spawn ``python3 tools/<PROGRAM>.py`` with *args* and capture its output.

        Every other assertion calls ``MAIN`` in-process, which covers the
        parsing, output and statuses; only a real subprocess covers the
        script's ``if __name__ == "__main__": sys.exit(main())`` wrapper and
        its direct-run import path. Each CLI covers that once, from its
        ``test_script_entry_point``.
        """
        script = ROOT / "tools" / f"{self.PROGRAM}.py"
        return run_captured([sys.executable, str(script), *args])

    def _tmp_dir(self) -> Path:
        """Return a fresh temp dir that is removed when the test ends."""
        return make_tmp_dir(self)

    def _write(self, directory: Path, name: str, data: bytes) -> str:
        path = directory / name
        path.write_bytes(data)
        return str(path)

    def _assert_success(self, result: subprocess.CompletedProcess) -> None:
        """Assert *result* is a clean exit-0 run.

        A passing run prints its report on stdout and reports a read failure
        on stderr, so both streams are attached to a failure message rather
        than only one. This is the counterpart of ``_assert_usage_error``.
        """
        assert_succeeded(self, result)

    def _assert_usage_error(
        self, result: subprocess.CompletedProcess, *needles: str
    ) -> None:
        """Assert *result* is a clean exit-2 usage error naming *needles*."""
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        for needle in needles:
            self.assertIn(needle, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
