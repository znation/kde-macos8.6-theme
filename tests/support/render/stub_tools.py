"""Shared shell-stub harness for the render CLI suites.

Used by ``tests/test_render_failure_paths.py``, ``tests/test_render_live_capture.py``,
``tests/test_render_session_modes.py``, ``tests/test_render_output_cli.py`` and
``tests/test_render_environment.py``.
"""

from __future__ import annotations

import os
import shutil
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401
from support.cli_fixtures import call_main
from tools import render_surface
from tools.png.write import encode_png


class StubTools(unittest.TestCase):
    """Base for tests that run the render CLI against shell stubs."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="render-surface-test-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.real_make = shutil.which("make")
        self.real_sleep = shutil.which("sleep")
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.scratch_parent = self.root / "tmp"
        self.scratch_parent.mkdir()
        self.stub("make", "exit 0")
        for name in render_surface.REQUIRED_TOOLS:
            if name != "make":
                self.stub(name, "exit 0")
        path = f"{self.bin}{os.pathsep}{os.environ['PATH']}"
        patches = (
            mock.patch.dict(os.environ, {"PATH": path}),
            mock.patch.object(tempfile, "tempdir", str(self.scratch_parent)),
            mock.patch.object(render_surface, "applet_problem", return_value=None),
        )
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)

    def stub(self, name, body):
        """Write an executable stub named *name* that runs *body*."""
        path = self.bin / name
        path.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def run_main(self, *extra):
        """Run ``main`` on ``out.png`` with *extra* and return its result."""
        output = self.root / "out.png"
        status, stderr = call_main(render_surface.main, str(output), *extra)
        return status, stderr, output

    def assert_scratch_removed(self):
        """Assert the scratch parent holds no leftover entries."""
        self.assertEqual([], os.listdir(self.scratch_parent))

    def assert_failed_run(self, status, stderr, output, expected_status, *diagnostics):
        """Assert a failed render's status, diagnostics, output and cleanup.

        Shared by the 24 failure-path tails: 12 in
        :mod:`tests.test_render_failure_paths`, 7 in
        :mod:`tests.test_render_live_capture` and 5 in
        :mod:`tests.test_render_session_modes`.
        """
        self.assertEqual(expected_status, status)
        for diagnostic in diagnostics:
            self.assertIn(diagnostic, stderr)
        self.assertNotIn("Traceback", stderr)
        self.assertFalse(output.exists())
        self.assert_scratch_removed()

    def hidden_files(self):
        """Return the dot-prefixed entries left in the scratch root."""
        return [name for name in os.listdir(self.root) if name.startswith(".")]

    def stub_capture(self, fill=0xDD):
        """Make the stubbed session write a valid 320x240 PNG where spectacle would.

        *fill* is the byte every colour channel holds; the default is the
        theme's painted window face, while 0 gives the all-black surface of a
        session that has not painted yet.
        """
        fixture = self.root / "capture.png"
        fixture.write_bytes(
            encode_png(320, 240, bytes([fill]) * (320 * 240 * 3))
        )
        # The session's argv ends with the shlex-joined `sh -c` line whose
        # positional parameters are the settle seconds, the surface path and
        # then the client: the capture stub extracts the surface path between
        # them, so the fixture lands where spectacle would have written it.
        self.stub(
            "dbus-run-session",
            'for a; do :; done; '
            "dest=$(printf '%s\\n' \"$a\" | sed -n "
            "'s/.* sh [^ ]* \\([^ ]*\\) plasmawindowed.*/\\1/p'); "
            f'cp "{fixture}" "$dest"',
        )
        return fixture
