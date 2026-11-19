"""Tests for the render CLI's ``--desktop`` and ``--splash`` argument checks.

These two modes open a fixed plain client (``plasmashell`` and ``ksplashqml``)
instead of a ``kdialog`` or applet window, so their argument checks differ from
the dialog-mode checks. They were moved out of
``tests/test_render_surface_units.py``; dialog-mode argument checks live in
``tests/test_render_dialog_arguments.py``, and the splash client argv is pinned
in ``tests/test_render_splash_client.py``.
The shared assertions live in ``tests/support/render_cli_cases.py``.
"""

from __future__ import annotations

import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.cli_fixtures import assert_missing_tool_named  # noqa: E402
from support.render_cli_cases import (  # noqa: E402
    assert_delegated_capture_size,
    assert_help_lists_flag,
    assert_rejects_applet_with_fixed_client,
    assert_rejects_capture_size_with_fixed_client,
    assert_two_mode_refusal_names_both,
    delegated_render_args,
)
from tools import render_surface  # noqa: E402


class TestFixedClientModeArguments(unittest.TestCase):

    def setUp(self):
        # The applet preflight consults the host's XDG data roots; these
        # delegation tests pin argument handling, not package discovery, so
        # the check is pinned off and they stay host-independent.
        patcher = mock.patch.object(
            render_surface, "applet_problem", return_value=None
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_cli_delegates_the_desktop_capture_size(self):
        # The desktop capture is fixed at 640x400, the probe's
        # virtual-framebuffer size and the queued desktop gate's crop basis;
        # the applet id stays at its default, which the desktop render
        # never opens.
        assert_delegated_capture_size(self, "--desktop", (640, 400))

    def test_rejects_an_applet_with_the_desktop(self):
        # The desktop client is plasmashell, not an applet window, so an
        # applet override has no window to open in.
        assert_rejects_applet_with_fixed_client(self, "--desktop")

    def test_rejects_a_capture_size_with_the_desktop(self):
        # 640x400 is the crop basis the queued desktop gate will compare, so
        # a size override moves the menu bar the pinned crops assume.
        assert_rejects_capture_size_with_fixed_client(self, "--desktop", "640x400")

    def test_rejects_a_dialog_mode_with_the_desktop(self):
        # The desktop client opens the shell itself, so a dialog client
        # cannot ride the same session.
        assert_two_mode_refusal_names_both(
            self, "--desktop", ("--checkbox-dialog", "--file-dialog")
        )

    def test_the_desktop_requires_plasmashell(self):
        # The desktop client is a plain command, so the missing-tool
        # preflight names it instead of starting a shell-less session.
        tools = render_surface.REQUIRED_TOOLS + ("plasmashell",)
        assert_missing_tool_named(
            self, render_surface.main, tools, ("out.png", "--desktop")
        )

    def test_the_desktop_defaults_the_slower_settle_and_timeout(self):
        # plasmashell's first start imports the look-and-feel layout, so the
        # desktop mode defaults to a 30 s settle and a 180 s timeout; an
        # explicit flag still wins over the mode default.
        cases = (
            (("out.png", "--desktop"), (30.0, 180.0)),
            (
                ("out.png", "--desktop", "--settle", "5", "--timeout", "60"),
                (5.0, 60.0),
            ),
        )
        for argv, expected in cases:
            with self.subTest(argv=argv):
                args = delegated_render_args(self, argv)
                self.assertEqual(expected, (args.settle, args.timeout))

    def test_the_help_text_names_the_desktop(self):
        assert_help_lists_flag(self, "--desktop")

    def test_cli_delegates_the_splash_capture_size(self):
        # The splash capture is fixed at 640x400, the same probe
        # virtual-framebuffer size the desktop capture fixes; the applet id
        # stays at its default, which the splash render never opens.
        assert_delegated_capture_size(self, "--splash", (640, 400))

    def test_rejects_an_applet_with_the_splash(self):
        # The splash client is ksplashqml, not an applet window, so an
        # applet override has no window to open in.
        assert_rejects_applet_with_fixed_client(self, "--splash")

    def test_rejects_a_capture_size_with_the_splash(self):
        # 640x400 is the crop basis the queued splash gate will compare, so
        # a size override moves the splash the pinned crops assume. The
        # --width flag exercises the same refusal through its other half.
        assert_rejects_capture_size_with_fixed_client(
            self, "--splash", "640x400", ("--width", "320")
        )

    def test_rejects_a_dialog_mode_and_the_desktop_with_the_splash(self):
        # The splash client opens the look-and-feel's own splash, so neither
        # a dialog client nor the desktop shell can ride the same session.
        assert_two_mode_refusal_names_both(
            self,
            "--splash",
            ("--desktop", "--checkbox-dialog", "--file-dialog", "--gtk-dialog"),
        )

    def test_the_splash_requires_ksplashqml(self):
        # The splash client is a plain command, so the missing-tool
        # preflight names it instead of starting a splash-less session.
        tools = render_surface.REQUIRED_TOOLS + ("ksplashqml",)
        assert_missing_tool_named(
            self, render_surface.main, tools, ("out.png", "--splash")
        )

    def test_the_splash_defaults_the_slower_settle_and_timeout(self):
        # The --test --nofork client paints within an 8 s settle (three probe
        # runs) but deterministically exits about 10 s in, so splash mode
        # keeps the applet's 8 s settle and 90 s timeout; an explicit flag
        # still wins over the mode default.
        cases = (
            (("out.png", "--splash"), (8.0, 90.0)),
            (
                ("out.png", "--splash", "--settle", "5", "--timeout", "60"),
                (5.0, 60.0),
            ),
        )
        for argv, expected in cases:
            with self.subTest(argv=argv):
                args = delegated_render_args(self, argv)
                self.assertEqual(expected, (args.settle, args.timeout))

    def test_the_help_text_names_the_splash(self):
        assert_help_lists_flag(self, "--splash")


if __name__ == "__main__":
    unittest.main()
