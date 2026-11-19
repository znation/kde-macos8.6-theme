"""Direct tests for the optional-selection boundary in tools/apply_optional."""

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


class TestOptionalSelectionHelpers(unittest.TestCase):
    """Pin direct optional helper behavior against a narrowed PATH."""

    def test_run_optional_selections_notes_both_missing_tools_and_returns_0(self):
        root = Path(tempfile.mkdtemp(prefix="theme-apply-optional-test-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        empty_bin = root / "bin"
        empty_bin.mkdir()
        env = {"PATH": str(empty_bin)}
        stderr = io.StringIO()
        with mock.patch.dict(os.environ, env, clear=False):
            with contextlib.redirect_stderr(stderr):
                status = apply_optional.run_optional_selections(
                    root, dict(os.environ), 60.0
                )
        self.assertEqual(0, status)
        text = stderr.getvalue()
        self.assertIn("apply_theme: note:", text)
        self.assertIn("kvantummanager is not on PATH", text)
        self.assertIn("neither qdbus6 nor qdbus is on PATH", text)

    def test_run_best_effort_success_prints_nothing(self):
        root = Path(tempfile.mkdtemp(prefix="theme-apply-optional-test-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        stub_bin = root / "bin"
        stub_bin.mkdir()
        stub = stub_bin / "tool"
        stub.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
        stderr = io.StringIO()
        with mock.patch.dict(os.environ, {"PATH": str(stub_bin)}, clear=False):
            with contextlib.redirect_stderr(stderr):
                apply_optional.run_best_effort(
                    root,
                    dict(os.environ),
                    ["tool"],
                    "tool.log",
                    60.0,
                    label="tool call",
                    consequence="nothing happens",
                )
        self.assertEqual("", stderr.getvalue())
        self.assertTrue((root / "tool.log").exists())


if __name__ == "__main__":
    unittest.main()
