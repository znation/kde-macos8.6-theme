"""Run a tools/ CLI's ``main`` in-process and capture its output.

The tool CLIs parse arguments with argparse, which exits through ``SystemExit``
for ``--help`` (0) and for a usage error (2), while ``main`` returns its status
otherwise. Tests that read only the exit status and printed diagnostics call
``main`` in-process instead of spawning ``python3 tools/<tool>.py``, exercising
the same parsing, output and statuses without paying interpreter startup and
module import per assertion. The script entry point itself stays covered once
per CLI by a ``test_script_entry_point``.
"""

import contextlib
import io
import subprocess
import unittest
from pathlib import Path


def run_main(main, program, args):
    """Call *main* with *args* and capture stdout/stderr as a CompletedProcess.

    *program* names the tool in the returned process's ``args``, so a failure
    message reads like the ``python3 tools/<program>.py`` invocation. A
    ``SystemExit`` becomes the process return code, as the script wrapper's
    ``sys.exit`` would report it: ``None`` is 0 and a non-int code is 1.
    """
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        try:
            returncode = main(list(args))
        except SystemExit as exc:
            returncode = 0 if exc.code is None else exc.code
            if not isinstance(returncode, int):
                returncode = 1
    return subprocess.CompletedProcess(
        [program, *args], returncode, stdout.getvalue(), stderr.getvalue()
    )


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
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def _assert_usage_error(
        self, result: subprocess.CompletedProcess, *needles: str
    ) -> None:
        """Assert *result* is a clean exit-2 usage error naming *needles*."""
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        for needle in needles:
            self.assertIn(needle, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
