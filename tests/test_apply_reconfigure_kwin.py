"""Direct stub coverage for the best-effort KWin reconfigure helper."""

from __future__ import annotations

import contextlib
import io
import os
import shutil
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools import apply_optional


class TestReconfigureKwin(unittest.TestCase):
    """Exercise qdbus selection and failure notes with isolated stub tools."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="reconfigure-kwin-test-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.bin = self.root / "bin"
        self.bin.mkdir()

    def _stub(self, name, body):
        stub = self.bin / name
        stub.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
        stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
        return stub

    def _run(self):
        stderr = io.StringIO()
        with mock.patch.dict(os.environ, {"PATH": str(self.bin)}, clear=False):
            with contextlib.redirect_stderr(stderr):
                status = apply_optional.reconfigure_kwin(
                    self.root, {"PATH": str(self.bin)}, 60.0
                )
        return status, stderr.getvalue()

    def test_a_found_qdbus6_receives_the_kwin_reconfigure_argv(self):
        self._stub("qdbus6", 'echo "$@"')
        status, text = self._run()
        self.assertEqual(0, status)
        self.assertEqual("org.kde.KWin /KWin reconfigure\n",
                         (self.root / "qdbus.log").read_text(encoding="utf-8"))
        self.assertEqual("", text)

    def test_qdbus6_is_preferred_over_qdbus(self):
        self._stub("qdbus6", "echo picked:qdbus6")
        self._stub("qdbus", "echo picked:qdbus")
        status, _ = self._run()
        self.assertEqual(0, status)
        self.assertEqual("picked:qdbus6\n",
                         (self.root / "qdbus.log").read_text(encoding="utf-8"))

    def test_only_the_qdbus_fallback_still_reaches_kwin(self):
        self._stub("qdbus", 'echo "$@"')
        status, text = self._run()
        self.assertEqual(0, status)
        self.assertEqual("org.kde.KWin /KWin reconfigure\n",
                         (self.root / "qdbus.log").read_text(encoding="utf-8"))
        self.assertEqual("", text)

    def test_a_failing_reconfigure_is_a_note_though_the_status_stays_0(self):
        self._stub("qdbus6", "exit 3")
        status, text = self._run()
        self.assertEqual(0, status)
        self.assertIn(
            "apply_theme: note: KWin reconfigure exited 3; KWin reloads the "
            "decoration on its next start",
            text,
        )


if __name__ == "__main__":
    unittest.main()
