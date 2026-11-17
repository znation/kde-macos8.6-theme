"""Tests for the render CLI's calculator applet preflight.

``render_surface.main`` refuses a calculator render whose applet package is
missing, before any session starts, and the ``--menu-dialog`` and ``--desktop``
modes never consult that check. The class was moved out of
``tests/test_render_surface_units.py``. The unit-level applet finder tests
live in ``tests/test_render_applet.py``.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.cli_fixtures import call_main  # noqa: E402
from tools import render_surface  # noqa: E402


class TestAppletPreflight(unittest.TestCase):
    """The calculator preflight refuses a missing applet package, before any
    session; the dialog modes never consult it."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="render-preflight-test-")
        self.addCleanup(self.tmp.cleanup)
        self.scratch = Path(self.tmp.name)

    def _run_with_roots(self, *data_dirs, render_result=None):
        """Run ``main(["out.png"])`` with the XDG roots pinned to the scratch
        tree; returns (status, stderr, render seam).

        The render seam fails loudly unless *render_result* names the value
        it returns instead, for the test that must reach it.
        """
        home = self.scratch / "first"
        home.mkdir(exist_ok=True)
        env_patches = {
            "XDG_DATA_HOME": str(home),
            "XDG_DATA_DIRS": os.pathsep.join(str(root) for root in data_dirs),
        }
        if render_result is None:
            render_patch = mock.patch.object(
                render_surface,
                "render",
                side_effect=AssertionError("render must not run"),
            )
        else:
            render_patch = mock.patch.object(
                render_surface, "render", return_value=render_result
            )
        with (
            mock.patch.dict(os.environ, env_patches),
            mock.patch.object(render_surface, "report_missing_tool", return_value=None),
            mock.patch.object(render_surface, "output_problem", return_value=None),
            mock.patch.object(render_surface, "exit_on_termination"),
            render_patch as render_seam,
        ):
            status, stderr = call_main(render_surface.main, "out.png")
        return status, stderr, render_seam

    def test_a_missing_applet_refuses_before_any_session(self):
        status, stderr, render_seam = self._run_with_roots(self.scratch / "second")
        self.assertEqual(2, status, stderr)
        self.assertIn("org.kde.plasma.calculator", stderr)
        self.assertIn(
            "plasma/plasmoids/org.kde.plasma.calculator/metadata.json", stderr
        )
        self.assertFalse(render_seam.called)

    def test_an_installed_scratch_applet_passes_the_preflight(self):
        package = (
            self.scratch / "first" / "plasma" / "plasmoids"
            / "org.kde.plasma.calculator"
        )
        package.mkdir(parents=True)
        (package / "metadata.json").write_text("{}", encoding="utf-8")
        status, stderr, render_seam = self._run_with_roots(
            self.scratch / "second", render_result=0
        )
        self.assertEqual(0, status, stderr)
        self.assertTrue(render_seam.called)
        self.assertEqual("", stderr)

    def test_a_dialog_run_never_consults_the_applet_check(self):
        # The dialog modes open their own clients and never touch the
        # applet, so a host without the calculator package must still render
        # its dialogs; the refusal here comes from the existing missing-tool
        # path, and the applet check seam is never entered.
        home = self.scratch / "first"
        home.mkdir()
        env_patches = {
            "XDG_DATA_HOME": str(home),
            "XDG_DATA_DIRS": str(self.scratch / "second"),
        }
        with (
            mock.patch.dict(os.environ, env_patches),
            mock.patch.object(render_surface, "report_missing_tool", return_value=2),
            mock.patch.object(render_surface, "applet_problem") as applet_seam,
        ):
            status, stderr = call_main(
                render_surface.main, "out.png", "--menu-dialog"
            )
        self.assertEqual(2, status, stderr)
        self.assertFalse(applet_seam.called)

    def test_a_desktop_run_never_consults_the_applet_check(self):
        # The desktop capture opens plasmashell, which needs no applet
        # package, so a host without the calculator package must still
        # render the menu bar; the refusal here comes from the existing
        # missing-tool path, and the applet check seam is never entered.
        home = self.scratch / "first"
        home.mkdir()
        env_patches = {
            "XDG_DATA_HOME": str(home),
            "XDG_DATA_DIRS": str(self.scratch / "second"),
        }
        with (
            mock.patch.dict(os.environ, env_patches),
            mock.patch.object(render_surface, "report_missing_tool", return_value=2),
            mock.patch.object(render_surface, "applet_problem") as applet_seam,
        ):
            status, stderr = call_main(render_surface.main, "out.png", "--desktop")
        self.assertEqual(2, status, stderr)
        self.assertFalse(applet_seam.called)


if __name__ == "__main__":
    unittest.main()
