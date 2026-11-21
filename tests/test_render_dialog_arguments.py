"""Tests for dialog-mode render CLI argument validation.

These cases call the CLI without starting a render session. Shared assertions
live in ``tests/support/render/cli_cases.py``.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.render.cli_cases import (  # noqa: E402
    assert_delegated_capture_size,
    assert_dialog_requires_kdialog,
    assert_help_lists_flag,
    assert_rejects_applet_with_fixed_client,
    assert_rejects_capture_size_with_fixed_client,
    assert_two_mode_refusal_names_both,
    assert_usage_error,
)
from tools import render_surface  # noqa: E402


class TestRenderDialogArguments(unittest.TestCase):

    def setUp(self):
        # The applet preflight consults the host's XDG data roots; these
        # delegation tests pin argument handling, not package discovery, so
        # the check is pinned off and they stay host-independent.
        patcher = mock.patch.object(
            render_surface, "applet_problem", return_value=None
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_cli_delegates_the_lineedit_dialog_capture_size(self):
        assert_delegated_capture_size(self, "--lineedit-dialog", (480, 360))

    def test_rejects_an_applet_with_the_lineedit_dialog(self):
        assert_rejects_applet_with_fixed_client(self, "--lineedit-dialog")

    def test_rejects_a_capture_size_with_the_lineedit_dialog(self):
        assert_rejects_capture_size_with_fixed_client(self, "--lineedit-dialog", "480x360")

    def test_rejects_two_dialog_modes_names_the_lineedit_dialog_too(self):
        assert_two_mode_refusal_names_both(
            self, "--lineedit-dialog", ("--checkbox-dialog", "--menu-dialog"))

    def test_the_lineedit_dialog_requires_kdialog(self):
        assert_dialog_requires_kdialog(self, "--lineedit-dialog")

    def test_cli_delegates_the_menu_dialog_capture_size(self):
        assert_delegated_capture_size(self, "--menu-dialog", (480, 360))

    def assert_usage_error(self, *argv):
        return assert_usage_error(self, *argv)

    def test_cli_delegates_the_slider_dialog_capture_size(self):
        assert_delegated_capture_size(self, "--slider-dialog", (480, 360))

    def test_rejects_an_applet_with_the_slider_dialog(self):
        assert_rejects_applet_with_fixed_client(self, "--slider-dialog")

    def test_rejects_a_capture_size_with_the_slider_dialog(self):
        assert_rejects_capture_size_with_fixed_client(self, "--slider-dialog", "480x360")

    def test_rejects_two_dialog_modes_names_the_slider_dialog_too(self):
        assert_two_mode_refusal_names_both(
            self, "--slider-dialog", ("--checkbox-dialog", "--gtk-dialog"))

    def test_the_multi_mode_refusal_wording_holds_for_three_modes(self):
        # Any count over one is refused; the wording must hold when three
        # or more dialog flags arrive together, where "not both" would be
        # false about the number it refuses.
        stderr = self.assert_usage_error(
            "out.png", "--checkbox-dialog", "--slider-dialog", "--gtk-dialog"
        )
        self.assertIn("not more than one", stderr)
        self.assertNotIn("not both", stderr)
        for flag in ("--checkbox-dialog", "--slider-dialog", "--gtk-dialog"):
            self.assertIn(flag, stderr)

    def test_the_slider_dialog_requires_kdialog(self):
        assert_dialog_requires_kdialog(self, "--slider-dialog")

    def test_cli_delegates_the_progressbar_dialog_capture_size(self):
        assert_delegated_capture_size(self, "--progressbar-dialog", (480, 360))

    def test_rejects_an_applet_with_the_progressbar_dialog(self):
        assert_rejects_applet_with_fixed_client(self, "--progressbar-dialog")

    def test_rejects_a_capture_size_with_the_progressbar_dialog(self):
        assert_rejects_capture_size_with_fixed_client(self, "--progressbar-dialog", "480x360")

    def test_rejects_two_dialog_modes_names_the_progressbar_dialog_too(self):
        assert_two_mode_refusal_names_both(
            self, "--progressbar-dialog", ("--checkbox-dialog", "--gtk-dialog"))

    def test_the_progressbar_dialog_requires_kdialog(self):
        # The progress dialog's helper daemon ships with kdialog, so the
        # requirement list still names the package's own tool.
        assert_dialog_requires_kdialog(self, "--progressbar-dialog")

    def test_cli_delegates_the_textbox_dialog_capture_size(self):
        assert_delegated_capture_size(self, "--textbox-dialog", (480, 360))

    def test_rejects_an_applet_with_the_textbox_dialog(self):
        assert_rejects_applet_with_fixed_client(self, "--textbox-dialog")

    def test_rejects_a_capture_size_with_the_textbox_dialog(self):
        assert_rejects_capture_size_with_fixed_client(self, "--textbox-dialog", "480x360")

    def test_rejects_two_dialog_modes_names_the_textbox_dialog_too(self):
        assert_two_mode_refusal_names_both(
            self, "--textbox-dialog", ("--checkbox-dialog", "--gtk-dialog"))

    def test_the_textbox_dialog_requires_kdialog(self):
        assert_dialog_requires_kdialog(self, "--textbox-dialog")

    def test_the_help_text_names_the_textbox_dialog(self):
        assert_help_lists_flag(self, "--textbox-dialog")

    def test_rejects_an_applet_with_the_checkbox_dialog(self):
        assert_rejects_applet_with_fixed_client(self, "--checkbox-dialog")

    def test_rejects_a_capture_size_with_the_checkbox_dialog(self):
        assert_rejects_capture_size_with_fixed_client(self, "--checkbox-dialog", "480x360")

    def test_rejects_two_dialog_modes(self):
        assert_two_mode_refusal_names_both(
            self, "--checkbox-dialog", ("--combobox-dialog",))

    def test_rejects_an_applet_with_the_combobox_dialog(self):
        assert_rejects_applet_with_fixed_client(self, "--combobox-dialog")

    def test_rejects_a_capture_size_with_the_combobox_dialog(self):
        assert_rejects_capture_size_with_fixed_client(self, "--combobox-dialog", "480x360")

    def test_the_combobox_dialog_requires_kdialog(self):
        assert_dialog_requires_kdialog(self, "--combobox-dialog")

    def test_rejects_an_applet_with_the_menu_dialog(self):
        assert_rejects_applet_with_fixed_client(self, "--menu-dialog")

    def test_rejects_a_capture_size_with_the_menu_dialog(self):
        assert_rejects_capture_size_with_fixed_client(self, "--menu-dialog", "480x360")

    def test_rejects_two_dialog_modes_names_the_menu_dialog_too(self):
        assert_two_mode_refusal_names_both(
            self, "--menu-dialog", ("--checkbox-dialog", "--combobox-dialog"))

    def test_the_menu_dialog_requires_kdialog(self):
        assert_dialog_requires_kdialog(self, "--menu-dialog")

    def test_cli_delegates_the_radiolist_dialog_capture_size(self):
        assert_delegated_capture_size(self, "--radiolist-dialog", (480, 360))

    def test_rejects_an_applet_with_the_radiolist_dialog(self):
        assert_rejects_applet_with_fixed_client(self, "--radiolist-dialog")

    def test_rejects_a_capture_size_with_the_radiolist_dialog(self):
        assert_rejects_capture_size_with_fixed_client(self, "--radiolist-dialog", "480x360")

    def test_rejects_two_dialog_modes_names_the_radiolist_dialog_too(self):
        assert_two_mode_refusal_names_both(
            self, "--radiolist-dialog", ("--checkbox-dialog", "--menu-dialog"))

    def test_the_radiolist_dialog_requires_kdialog(self):
        assert_dialog_requires_kdialog(self, "--radiolist-dialog")

    def test_the_help_text_names_the_radiolist_dialog(self):
        assert_help_lists_flag(self, "--radiolist-dialog")

    def test_cli_delegates_the_calendar_dialog_capture_size(self):
        assert_delegated_capture_size(self, "--calendar-dialog", (480, 360))

    def test_rejects_an_applet_with_the_calendar_dialog(self):
        assert_rejects_applet_with_fixed_client(self, "--calendar-dialog")

    def test_rejects_a_capture_size_with_the_calendar_dialog(self):
        assert_rejects_capture_size_with_fixed_client(self, "--calendar-dialog", "480x360")

    def test_rejects_two_dialog_modes_names_the_calendar_dialog_too(self):
        assert_two_mode_refusal_names_both(
            self, "--calendar-dialog", ("--checkbox-dialog", "--gtk-dialog"))

    def test_the_calendar_dialog_requires_kdialog(self):
        assert_dialog_requires_kdialog(self, "--calendar-dialog")

    def test_the_help_text_names_the_calendar_dialog(self):
        assert_help_lists_flag(self, "--calendar-dialog")

    def test_usage_docstring_names_every_dialog_mode_the_parser_defines(self):
        # The module docstring's Usage block is the CLI contract a reader
        # sees before any --help run: a dialog mode registered in the
        # argument parser must appear there, and no stale name may outlive
        # its removal. The calendar gate updated the Makefile, argparse,
        # README and invariants for --calendar-dialog but left this block
        # listing its siblings without it.
        source = Path(render_surface.__file__).read_text()
        parser_modes = sorted(set(re.findall(r"--(?:[a-z]+-)+dialog", source)))
        docstring_modes = sorted(
            set(re.findall(r"--(?:[a-z]+-)+dialog", render_surface.__doc__ or ""))
        )
        self.assertEqual(
            parser_modes,
            docstring_modes,
            "render_surface's usage docstring must name exactly the dialog "
            "modes its argument parser defines",
        )

    def test_cli_delegates_the_color_dialog_capture_size(self):
        assert_delegated_capture_size(self, "--color-dialog", (480, 360))

    def test_rejects_an_applet_with_the_color_dialog(self):
        assert_rejects_applet_with_fixed_client(self, "--color-dialog")

    def test_rejects_a_capture_size_with_the_color_dialog(self):
        assert_rejects_capture_size_with_fixed_client(self, "--color-dialog", "480x360")

    def test_rejects_two_dialog_modes_names_the_color_dialog_too(self):
        assert_two_mode_refusal_names_both(
            self, "--color-dialog", ("--checkbox-dialog", "--gtk-dialog", "--calendar-dialog"))

    def test_the_color_dialog_requires_kdialog(self):
        assert_dialog_requires_kdialog(self, "--color-dialog")

    def test_the_help_text_names_the_color_dialog(self):
        assert_help_lists_flag(self, "--color-dialog")

    def test_cli_delegates_the_icon_dialog_capture_size(self):
        assert_delegated_capture_size(self, "--icon-dialog", (480, 360))

    def test_rejects_an_applet_with_the_icon_dialog(self):
        assert_rejects_applet_with_fixed_client(self, "--icon-dialog")

    def test_rejects_a_capture_size_with_the_icon_dialog(self):
        assert_rejects_capture_size_with_fixed_client(self, "--icon-dialog", "480x360")

    def test_rejects_two_dialog_modes_names_the_icon_dialog_too(self):
        assert_two_mode_refusal_names_both(
            self, "--icon-dialog", ("--checkbox-dialog", "--gtk-dialog", "--color-dialog"))

    def test_the_icon_dialog_requires_kdialog(self):
        assert_dialog_requires_kdialog(self, "--icon-dialog")

    def test_the_help_text_names_the_icon_dialog(self):
        assert_help_lists_flag(self, "--icon-dialog")

    def test_the_checkbox_dialog_requires_kdialog(self):
        assert_dialog_requires_kdialog(self, "--checkbox-dialog")

    def test_cli_delegates_the_inactive_dialog_capture_size(self):
        assert_delegated_capture_size(self, "--inactive-dialog", (480, 360))

    def test_rejects_an_applet_with_the_inactive_dialog(self):
        assert_rejects_applet_with_fixed_client(self, "--inactive-dialog")

    def test_rejects_a_capture_size_with_the_inactive_dialog(self):
        assert_rejects_capture_size_with_fixed_client(self, "--inactive-dialog", "480x360")

    def test_rejects_two_dialog_modes_names_the_inactive_dialog_too(self):
        assert_two_mode_refusal_names_both(
            self, "--inactive-dialog", ("--checkbox-dialog", "--gtk-dialog"))

    def test_the_inactive_dialog_requires_kdialog(self):
        # Both windows of the two-window client are kdialog message
        # boxes, so the mode's client tool is kdialog.
        assert_dialog_requires_kdialog(self, "--inactive-dialog")

    def test_the_help_text_names_the_inactive_dialog(self):
        assert_help_lists_flag(self, "--inactive-dialog")

    def test_cli_delegates_the_file_dialog_capture_size(self):
        assert_delegated_capture_size(self, "--file-dialog", (480, 360))

    def test_rejects_an_applet_with_the_file_dialog(self):
        assert_rejects_applet_with_fixed_client(self, "--file-dialog")

    def test_rejects_a_capture_size_with_the_file_dialog(self):
        assert_rejects_capture_size_with_fixed_client(self, "--file-dialog", "480x360")

    def test_rejects_two_dialog_modes_names_the_file_dialog_too(self):
        assert_two_mode_refusal_names_both(
            self, "--file-dialog", ("--checkbox-dialog", "--inactive-dialog"))

    def test_the_file_dialog_requires_kdialog(self):
        assert_dialog_requires_kdialog(self, "--file-dialog")

    def test_the_help_text_names_the_file_dialog(self):
        assert_help_lists_flag(self, "--file-dialog")


if __name__ == "__main__":
    unittest.main()
