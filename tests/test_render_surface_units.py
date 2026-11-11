"""Tests for the render CLI and throwaway render workflow units.

The render's end-to-end capture and its failure orchestration live in
``tests/test_render_surface.py``, and the output publication in
``tests/test_render_output.py``; this module covers the units they are built
from: ``render_surface.main``'s argument validation and workflow delegation,
scratch environment and KWin session command construction in ``tools/render_session.py`` and
theme installation/configuration in ``tools/render_setup.py``, plus the
dialog argv recipes in ``tools/render_clients.py``.
"""

from __future__ import annotations

import contextlib
import io
import os
import re
import shlex
import stat
import sys
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import tmp_dir
from support.cli_fixtures import _call_capturing, assert_missing_tool_named, call_main  # noqa: E402
from tools import (
    apply_theme,
    render_session,
    render_setup,
    render_surface,
    render_workflow,
    theme_apply_optional,
)  # noqa: E402
from tools.render_clients import (
    calendar_dialog_client,
    checkbox_dialog_client,
    color_dialog_client,
    combobox_dialog_client,
    gtk_dialog_client,
    icon_dialog_client,
    lineedit_dialog_client,
    menu_dialog_client,
    progressbar_dialog_client,
    radio_dialog_client,
    slider_dialog_client,
    textbox_dialog_client,
)  # noqa: E402
from tools.gtk_selection import ConfigError as _ConfigError  # noqa: E402
from tools.gtk_selection import installed_sheet  # noqa: E402
from tools.gtk_user_files import GTK4_CSS_MARKER  # noqa: E402


class TestCapturePaintCheck(unittest.TestCase):
    def test_empty_rgb_plane_is_unpainted(self):
        self.assertTrue(render_workflow._capture_is_unpainted(b""))

    def test_any_nonblack_rgb_byte_marks_capture_as_painted(self):
        self.assertFalse(render_workflow._capture_is_unpainted(b"\x00\x00\x01"))


class TestArguments(unittest.TestCase):
    def test_cli_delegates_validated_options_to_render_workflow(self):
        with (
            mock.patch.object(render_surface, "report_missing_tool", return_value=None),
            mock.patch.object(render_surface, "output_problem", return_value=None),
            mock.patch.object(render_surface, "render", return_value=7) as workflow,
            mock.patch.object(render_surface, "exit_on_termination"),
        ):
            status = render_surface.main(("out.png", "--applet", "test.applet"))

        self.assertEqual(7, status)
        args = workflow.call_args.args[0]
        self.assertEqual("test.applet", args.applet)
        self.assertEqual((320, 240), (args.width, args.height))
        self.assertIs(render_workflow.render, render_surface.render)

    def test_cli_delegates_the_settle_and_timeout_to_the_workflow(self):
        # render() reads args.settle and args.timeout to build the session
        # command and its supervision timeout, so a non-default value must
        # reach it parsed, not fall back to the parser defaults.
        with (
            mock.patch.object(render_surface, "report_missing_tool", return_value=None),
            mock.patch.object(render_surface, "output_problem", return_value=None),
            mock.patch.object(render_surface, "render", return_value=0) as workflow,
            mock.patch.object(render_surface, "exit_on_termination"),
        ):
            render_surface.main(("out.png", "--settle", "1.25", "--timeout", "33"))

        args = workflow.call_args.args[0]
        self.assertEqual(1.25, args.settle)
        self.assertEqual(33.0, args.timeout)

    def test_cli_delegates_the_lineedit_dialog_capture_size(self):
        # A plain --lineedit-dialog run captures at the 480x360 the widget
        # gate byte-compares, not the applet's 320x240 default.
        with (
            mock.patch.object(render_surface, "report_missing_tool", return_value=None),
            mock.patch.object(render_surface, "output_problem", return_value=None),
            mock.patch.object(render_surface, "render", return_value=0) as workflow,
            mock.patch.object(render_surface, "exit_on_termination"),
        ):
            render_surface.main(("out.png", "--lineedit-dialog"))

        args = workflow.call_args.args[0]
        self.assertEqual((480, 360), (args.width, args.height))
        self.assertEqual("org.kde.plasma.calculator", args.applet)

    def test_rejects_an_applet_with_the_lineedit_dialog(self):
        # The dialog render opens its own kdialog client; a plasmoid id
        # combined with it has no window to open it in.
        self.assert_usage_error(
            "out.png", "--lineedit-dialog", "--applet", "x"
        )

    def test_rejects_a_capture_size_with_the_lineedit_dialog(self):
        # The gate byte-compares the dialog capture at 480x360; any other
        # size makes the pinned crops wrong before the render runs.
        self.assert_usage_error(
            "out.png", "--lineedit-dialog", "--height", "240"
        )

    def test_rejects_two_dialog_modes_names_the_lineedit_dialog_too(self):
        # The two-mode refusal lists the flags involved, so a lineedit mode
        # flag missing from that list would print a refusal without its name.
        for left, right in (
            ("--lineedit-dialog", "--checkbox-dialog"),
            ("--lineedit-dialog", "--menu-dialog"),
        ):
            with self.subTest(left=left, right=right):
                stderr = self.assert_usage_error("out.png", left, right)
                self.assertIn(left, stderr)
                self.assertIn(right, stderr)

    def test_the_lineedit_dialog_requires_kdialog(self):
        # With kdialog absent the CLI names it instead of starting a session.
        tools = render_surface.REQUIRED_TOOLS + ("kdialog",)
        assert_missing_tool_named(
            self, render_surface.main, tools, ("out.png", "--lineedit-dialog")
        )

    def test_cli_delegates_the_menu_dialog_capture_size(self):
        # A plain --menu-dialog run captures at the 480x360 the widget gate
        # byte-compares, not the applet's 320x240 default.
        with (
            mock.patch.object(render_surface, "report_missing_tool", return_value=None),
            mock.patch.object(render_surface, "output_problem", return_value=None),
            mock.patch.object(render_surface, "render", return_value=0) as workflow,
            mock.patch.object(render_surface, "exit_on_termination"),
        ):
            render_surface.main(("out.png", "--menu-dialog"))

        args = workflow.call_args.args[0]
        self.assertEqual((480, 360), (args.width, args.height))
        self.assertEqual("org.kde.plasma.calculator", args.applet)

    def test_a_single_custom_dimension_keeps_the_other_default(self):
        for option, value, expected in (
            ("--width", "640", (640, 240)),
            ("--height", "480", (320, 480)),
        ):
            with self.subTest(option=option):
                with (
                    mock.patch.object(render_surface, "report_missing_tool", return_value=None),
                    mock.patch.object(render_surface, "output_problem", return_value=None),
                    mock.patch.object(render_surface, "render", return_value=0) as workflow,
                    mock.patch.object(render_surface, "exit_on_termination"),
                ):
                    render_surface.main(("out.png", option, value))

                args = workflow.call_args.args[0]
                self.assertEqual(expected, (args.width, args.height))

    def assert_usage_error(self, *argv):
        """Assert a usage error (exit 2) and return its stderr."""
        status, stderr = call_main(render_surface.main, *argv)
        self.assertEqual(2, status)
        return stderr

    def test_rejects_non_positive_and_non_plain_sizes(self):
        for option in ("--width", "--height"):
            for value in ("0", "-3", "1_0", "abc", "1.5"):
                with self.subTest(option=option, value=value):
                    self.assertIn(
                        option, self.assert_usage_error("out.png", option, value)
                    )

    def test_rejects_bad_durations(self):
        for argv in (
            ("--settle", "-1"),
            ("--settle", "nan"),
            ("--settle", "inf"),
            ("--timeout", "0"),
            ("--timeout", "1_0"),
        ):
            with self.subTest(argv=argv):
                self.assertIn(argv[0], self.assert_usage_error("out.png", *argv))

    def test_rejects_a_timeout_not_longer_than_settle(self):
        # The session sleeps for --settle before it asks for the capture, so a
        # timeout at or below it can never capture: refuse rather than wait
        # out the timeout and report "render timed out" without naming the
        # option that cannot work.
        for settle, timeout in (("10", "10"), ("10", "9.5"), ("10", "1")):
            with self.subTest(settle=settle, timeout=timeout):
                stderr = self.assert_usage_error(
                    "out.png", "--settle", settle, "--timeout", timeout
                )
                self.assertIn("--timeout", stderr)
                self.assertIn("--settle", stderr)
                self.assertIn("must be longer than", stderr)

    def test_rejects_option_like_applet(self):
        self.assertIn(
            "--applet", self.assert_usage_error("out.png", "--applet=--help-all")
        )

    def test_rejects_empty_applet(self):
        # ``--applet=`` passes the empty string to the type; the guard rejects
        # it with the same diagnostic as the option-like half, so an empty
        # plasmoid id never reaches the render session.
        self.assertIn("--applet", self.assert_usage_error("out.png", "--applet="))

    def test_requires_an_output_path(self):
        self.assert_usage_error()

    def test_cli_delegates_the_slider_dialog_capture_size(self):
        # A plain --slider-dialog run captures at the 480x360 the widget
        # gate byte-compares, not the applet's 320x240 default.
        with (
            mock.patch.object(render_surface, "report_missing_tool", return_value=None),
            mock.patch.object(render_surface, "output_problem", return_value=None),
            mock.patch.object(render_surface, "render", return_value=0) as workflow,
            mock.patch.object(render_surface, "exit_on_termination"),
        ):
            render_surface.main(("out.png", "--slider-dialog"))

        args = workflow.call_args.args[0]
        self.assertEqual((480, 360), (args.width, args.height))
        self.assertEqual("org.kde.plasma.calculator", args.applet)

    def test_rejects_an_applet_with_the_slider_dialog(self):
        # The slider mode opens its own kdialog client; a plasmoid id
        # combined with it has no window to open it in.
        self.assertIn(
            "--slider-dialog",
            self.assert_usage_error("out.png", "--slider-dialog", "--applet", "x"),
        )

    def test_rejects_a_capture_size_with_the_slider_dialog(self):
        # The gate byte-compares the slider capture at 480x360; any other
        # size moves the dialog window the comparison crops assume.
        stderr = self.assert_usage_error(
            "out.png", "--slider-dialog", "--width", "320"
        )
        self.assertIn("480x360", stderr)

    def test_rejects_two_dialog_modes_names_the_slider_dialog_too(self):
        # The two-mode refusal lists the flags involved, so a slider mode
        # flag missing from that list would print a refusal without its
        # name.
        for left, right in (
            ("--slider-dialog", "--checkbox-dialog"),
            ("--slider-dialog", "--gtk-dialog"),
        ):
            with self.subTest(left=left, right=right):
                stderr = self.assert_usage_error("out.png", left, right)
                self.assertIn(left, stderr)
                self.assertIn(right, stderr)

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
        # With kdialog absent the CLI names it instead of starting a session.
        tools = render_surface.REQUIRED_TOOLS + ("kdialog",)
        assert_missing_tool_named(
            self, render_surface.main, tools, ("out.png", "--slider-dialog")
        )

    def test_cli_delegates_the_progressbar_dialog_capture_size(self):
        # A plain --progressbar-dialog run captures at the 480x360 the widget
        # gate byte-compares, not the applet's 320x240 default.
        with (
            mock.patch.object(render_surface, "report_missing_tool", return_value=None),
            mock.patch.object(render_surface, "output_problem", return_value=None),
            mock.patch.object(render_surface, "render", return_value=0) as workflow,
            mock.patch.object(render_surface, "exit_on_termination"),
        ):
            render_surface.main(("out.png", "--progressbar-dialog"))

        args = workflow.call_args.args[0]
        self.assertEqual((480, 360), (args.width, args.height))
        self.assertEqual("org.kde.plasma.calculator", args.applet)

    def test_rejects_an_applet_with_the_progressbar_dialog(self):
        # The progressbar mode opens its own dialog client; a plasmoid id
        # combined with it has no window to open it in.
        self.assertIn(
            "--progressbar-dialog",
            self.assert_usage_error("out.png", "--progressbar-dialog", "--applet", "x"),
        )

    def test_rejects_a_capture_size_with_the_progressbar_dialog(self):
        # The gate byte-compares the progress meter capture at 480x360; any
        # other size moves the dialog window the comparison crops assume.
        stderr = self.assert_usage_error(
            "out.png", "--progressbar-dialog", "--height", "240"
        )
        self.assertIn("480x360", stderr)

    def test_rejects_two_dialog_modes_names_the_progressbar_dialog_too(self):
        # The two-mode refusal lists the flags involved, so a progressbar
        # mode flag missing from that list would print a refusal without
        # its name.
        for left, right in (
            ("--progressbar-dialog", "--checkbox-dialog"),
            ("--progressbar-dialog", "--gtk-dialog"),
        ):
            with self.subTest(left=left, right=right):
                stderr = self.assert_usage_error("out.png", left, right)
                self.assertIn(left, stderr)
                self.assertIn(right, stderr)

    def test_the_progressbar_dialog_requires_kdialog(self):
        # With kdialog absent the CLI names it instead of starting a session;
        # the progress dialog's helper daemon ships with kdialog, so the
        # requirement list still names the package's own tool.
        tools = render_surface.REQUIRED_TOOLS + ("kdialog",)
        assert_missing_tool_named(
            self, render_surface.main, tools, ("out.png", "--progressbar-dialog")
        )

    def test_cli_delegates_the_textbox_dialog_capture_size(self):
        # A plain --textbox-dialog run captures at the 480x360 the widget
        # gate byte-compares, not the applet's 320x240 default.
        with (
            mock.patch.object(render_surface, "report_missing_tool", return_value=None),
            mock.patch.object(render_surface, "output_problem", return_value=None),
            mock.patch.object(render_surface, "render", return_value=0) as workflow,
            mock.patch.object(render_surface, "exit_on_termination"),
        ):
            render_surface.main(("out.png", "--textbox-dialog"))

        args = workflow.call_args.args[0]
        self.assertEqual((480, 360), (args.width, args.height))
        self.assertEqual("org.kde.plasma.calculator", args.applet)

    def test_rejects_an_applet_with_the_textbox_dialog(self):
        # The textbox mode opens its own kdialog client; a plasmoid id
        # combined with it has no window to open it in.
        self.assertIn(
            "--textbox-dialog",
            self.assert_usage_error("out.png", "--textbox-dialog", "--applet", "x"),
        )

    def test_rejects_a_capture_size_with_the_textbox_dialog(self):
        # The gate byte-compares the scrollbar capture at 480x360; any other
        # size moves the dialog window the comparison crops assume.
        stderr = self.assert_usage_error(
            "out.png", "--textbox-dialog", "--height", "240"
        )
        self.assertIn("480x360", stderr)

    def test_rejects_two_dialog_modes_names_the_textbox_dialog_too(self):
        # The two-mode refusal lists the flags involved, so a textbox mode
        # flag missing from that list would print a refusal without its
        # name.
        for left, right in (
            ("--textbox-dialog", "--checkbox-dialog"),
            ("--textbox-dialog", "--gtk-dialog"),
        ):
            with self.subTest(left=left, right=right):
                stderr = self.assert_usage_error("out.png", left, right)
                self.assertIn(left, stderr)
                self.assertIn(right, stderr)

    def test_the_textbox_dialog_requires_kdialog(self):
        tools = render_surface.REQUIRED_TOOLS + ("kdialog",)
        assert_missing_tool_named(
            self, render_surface.main, tools, ("out.png", "--textbox-dialog")
        )

    def test_the_help_text_names_the_textbox_dialog(self):
        # --help lists every dialog mode; a flag missing from that help
        # would leave the mode unusable by anyone reading the CLI.
        _, stdout, _ = _call_capturing(lambda: render_surface.main(["--help"]))
        self.assertIn("--textbox-dialog", stdout)

    def test_rejects_an_applet_with_the_checkbox_dialog(self):
        # The dialog render opens its own kdialog client; a plasmoid id
        # combined with it would silently draw nothing.
        self.assertIn(
            "--checkbox-dialog",
            self.assert_usage_error("out.png", "--checkbox-dialog", "--applet", "x"),
        )

    def test_rejects_a_capture_size_with_the_checkbox_dialog(self):
        # The gate byte-compares the dialog capture at 480x360; any other
        # size moves the KDialog window the comparison crops assume.
        stderr = self.assert_usage_error(
            "out.png", "--checkbox-dialog", "--width", "320"
        )
        self.assertIn("480x360", stderr)

    def test_rejects_two_dialog_modes(self):
        # Each dialog mode opens its own kdialog client; two flags cannot
        # pick one client, so the CLI refuses the combination by name.
        stderr = self.assert_usage_error(
            "out.png", "--checkbox-dialog", "--combobox-dialog"
        )
        self.assertIn("--checkbox-dialog", stderr)
        self.assertIn("--combobox-dialog", stderr)

    def test_rejects_an_applet_with_the_combobox_dialog(self):
        self.assertIn(
            "--combobox-dialog",
            self.assert_usage_error("out.png", "--combobox-dialog", "--applet", "x"),
        )

    def test_rejects_a_capture_size_with_the_combobox_dialog(self):
        stderr = self.assert_usage_error(
            "out.png", "--combobox-dialog", "--height", "240"
        )
        self.assertIn("480x360", stderr)

    def test_the_combobox_dialog_requires_kdialog(self):
        tools = render_surface.REQUIRED_TOOLS + ("kdialog",)
        assert_missing_tool_named(
            self, render_surface.main, tools, ("out.png", "--combobox-dialog")
        )

    def test_rejects_an_applet_with_the_menu_dialog(self):
        # The menu mode opens its own kdialog client; a plasmoid id combined
        # with it would silently draw nothing.
        self.assertIn(
            "--menu-dialog",
            self.assert_usage_error("out.png", "--menu-dialog", "--applet", "x"),
        )

    def test_rejects_a_capture_size_with_the_menu_dialog(self):
        # The gate byte-compares the menu capture at 480x360; any other size
        # moves the KDialog window the comparison crops assume.
        stderr = self.assert_usage_error(
            "out.png", "--menu-dialog", "--height", "240"
        )
        self.assertIn("480x360", stderr)

    def test_rejects_two_dialog_modes_names_the_menu_dialog_too(self):
        # The two-mode refusal lists the flags involved, so a menu mode flag
        # missing from that list would print a refusal without its name.
        for left, right in (
            ("--menu-dialog", "--checkbox-dialog"),
            ("--menu-dialog", "--combobox-dialog"),
        ):
            with self.subTest(left=left, right=right):
                stderr = self.assert_usage_error("out.png", left, right)
                self.assertIn(left, stderr)
                self.assertIn(right, stderr)

    def test_the_menu_dialog_requires_kdialog(self):
        # With kdialog absent the CLI names it instead of starting a session.
        tools = render_surface.REQUIRED_TOOLS + ("kdialog",)
        assert_missing_tool_named(
            self, render_surface.main, tools, ("out.png", "--menu-dialog")
        )

    def test_cli_delegates_the_radiolist_dialog_capture_size(self):
        # A plain --radiolist-dialog run captures at the 480x360 the widget
        # gate byte-compares, not the applet's 320x240 default.
        with (
            mock.patch.object(render_surface, "report_missing_tool", return_value=None),
            mock.patch.object(render_surface, "output_problem", return_value=None),
            mock.patch.object(render_surface, "render", return_value=0) as workflow,
            mock.patch.object(render_surface, "exit_on_termination"),
        ):
            render_surface.main(("out.png", "--radiolist-dialog"))

        args = workflow.call_args.args[0]
        self.assertEqual((480, 360), (args.width, args.height))
        self.assertEqual("org.kde.plasma.calculator", args.applet)

    def test_rejects_an_applet_with_the_radiolist_dialog(self):
        # The radio-list mode opens its own kdialog client; a plasmoid id
        # combined with it has no window to open it in.
        self.assertIn(
            "--radiolist-dialog",
            self.assert_usage_error("out.png", "--radiolist-dialog", "--applet", "x"),
        )

    def test_rejects_a_capture_size_with_the_radiolist_dialog(self):
        # The gate byte-compares the radio-list capture at 480x360; any
        # other size moves the KDialog window the comparison crops assume.
        stderr = self.assert_usage_error(
            "out.png", "--radiolist-dialog", "--height", "240"
        )
        self.assertIn("480x360", stderr)

    def test_rejects_two_dialog_modes_names_the_radiolist_dialog_too(self):
        # The two-mode refusal lists the flags involved, so a radio-list
        # mode flag missing from that list would print a refusal without
        # its name.
        for left, right in (
            ("--radiolist-dialog", "--checkbox-dialog"),
            ("--radiolist-dialog", "--menu-dialog"),
        ):
            with self.subTest(left=left, right=right):
                stderr = self.assert_usage_error("out.png", left, right)
                self.assertIn(left, stderr)
                self.assertIn(right, stderr)

    def test_the_radiolist_dialog_requires_kdialog(self):
        # With kdialog absent the CLI names it instead of starting a session.
        tools = render_surface.REQUIRED_TOOLS + ("kdialog",)
        assert_missing_tool_named(
            self, render_surface.main, tools, ("out.png", "--radiolist-dialog")
        )

    def test_the_help_text_names_the_radiolist_dialog(self):
        # --help lists every dialog mode; a flag missing from that help
        # would leave the mode unusable by anyone reading the CLI.
        _, stdout, _ = _call_capturing(lambda: render_surface.main(["--help"]))
        self.assertIn("--radiolist-dialog", stdout)

    def test_cli_delegates_the_calendar_dialog_capture_size(self):
        # A plain --calendar-dialog run captures at the 480x360 the widget
        # gate byte-compares, not the applet's 320x240 default.
        with (
            mock.patch.object(render_surface, "report_missing_tool", return_value=None),
            mock.patch.object(render_surface, "output_problem", return_value=None),
            mock.patch.object(render_surface, "render", return_value=0) as workflow,
            mock.patch.object(render_surface, "exit_on_termination"),
        ):
            render_surface.main(("out.png", "--calendar-dialog"))

        args = workflow.call_args.args[0]
        self.assertEqual((480, 360), (args.width, args.height))
        self.assertEqual("org.kde.plasma.calculator", args.applet)

    def test_rejects_an_applet_with_the_calendar_dialog(self):
        # The calendar mode opens its own kdialog client; a plasmoid id
        # combined with it would silently draw nothing.
        self.assertIn(
            "--calendar-dialog",
            self.assert_usage_error("out.png", "--calendar-dialog", "--applet", "x"),
        )

    def test_rejects_a_capture_size_with_the_calendar_dialog(self):
        # The gate byte-compares the calendar capture at 480x360; any other
        # size moves the dialog window the comparison crops assume.
        stderr = self.assert_usage_error(
            "out.png", "--calendar-dialog", "--height", "240"
        )
        self.assertIn("480x360", stderr)

    def test_rejects_two_dialog_modes_names_the_calendar_dialog_too(self):
        # The two-mode refusal lists the flags involved, so a calendar mode
        # flag missing from that list would print a refusal without its
        # name.
        for left, right in (
            ("--calendar-dialog", "--checkbox-dialog"),
            ("--calendar-dialog", "--gtk-dialog"),
        ):
            with self.subTest(left=left, right=right):
                stderr = self.assert_usage_error("out.png", left, right)
                self.assertIn(left, stderr)
                self.assertIn(right, stderr)

    def test_the_calendar_dialog_requires_kdialog(self):
        # With kdialog absent the CLI names it instead of starting a session.
        tools = render_surface.REQUIRED_TOOLS + ("kdialog",)
        assert_missing_tool_named(
            self, render_surface.main, tools, ("out.png", "--calendar-dialog")
        )

    def test_the_help_text_names_the_calendar_dialog(self):
        # --help lists every dialog mode; a flag missing from that help
        # would leave the mode unusable by anyone reading the CLI.
        _, stdout, _ = _call_capturing(lambda: render_surface.main(["--help"]))
        self.assertIn("--calendar-dialog", stdout)

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
        # A plain --color-dialog run captures at the 480x360 the widget
        # gate byte-compares, not the applet's 320x240 default.
        with (
            mock.patch.object(render_surface, "report_missing_tool", return_value=None),
            mock.patch.object(render_surface, "output_problem", return_value=None),
            mock.patch.object(render_surface, "render", return_value=0) as workflow,
            mock.patch.object(render_surface, "exit_on_termination"),
        ):
            render_surface.main(("out.png", "--color-dialog"))

        args = workflow.call_args.args[0]
        self.assertEqual((480, 360), (args.width, args.height))
        self.assertEqual("org.kde.plasma.calculator", args.applet)

    def test_rejects_an_applet_with_the_color_dialog(self):
        # The color mode opens its own kdialog client; a plasmoid id
        # combined with it would silently draw nothing.
        self.assertIn(
            "--color-dialog",
            self.assert_usage_error("out.png", "--color-dialog", "--applet", "x"),
        )

    def test_rejects_a_capture_size_with_the_color_dialog(self):
        # The gate byte-compares the color capture at 480x360; any other
        # size moves the dialog window the comparison crops assume.
        stderr = self.assert_usage_error(
            "out.png", "--color-dialog", "--width", "320"
        )
        self.assertIn("480x360", stderr)

    def test_rejects_two_dialog_modes_names_the_color_dialog_too(self):
        # The two-mode refusal lists the flags involved, so a color mode
        # flag missing from that list would print a refusal without its
        # name.
        for left, right in (
            ("--color-dialog", "--checkbox-dialog"),
            ("--color-dialog", "--gtk-dialog"),
            ("--calendar-dialog", "--color-dialog"),
        ):
            with self.subTest(left=left, right=right):
                stderr = self.assert_usage_error("out.png", left, right)
                self.assertIn(left, stderr)
                self.assertIn(right, stderr)

    def test_the_color_dialog_requires_kdialog(self):
        # With kdialog absent the CLI names it instead of starting a session.
        tools = render_surface.REQUIRED_TOOLS + ("kdialog",)
        assert_missing_tool_named(
            self, render_surface.main, tools, ("out.png", "--color-dialog")
        )

    def test_the_help_text_names_the_color_dialog(self):
        # --help lists every dialog mode; a flag missing from that help
        # would leave the mode unusable by anyone reading the CLI.
        _, stdout, _ = _call_capturing(lambda: render_surface.main(["--help"]))
        self.assertIn("--color-dialog", stdout)

    def test_cli_delegates_the_icon_dialog_capture_size(self):
        # A plain --icon-dialog run captures at the 480x360 the widget
        # gate byte-compares, not the applet's 320x240 default.
        with (
            mock.patch.object(render_surface, "report_missing_tool", return_value=None),
            mock.patch.object(render_surface, "output_problem", return_value=None),
            mock.patch.object(render_surface, "render", return_value=0) as workflow,
            mock.patch.object(render_surface, "exit_on_termination"),
        ):
            render_surface.main(("out.png", "--icon-dialog"))

        args = workflow.call_args.args[0]
        self.assertEqual((480, 360), (args.width, args.height))
        self.assertEqual("org.kde.plasma.calculator", args.applet)

    def test_rejects_an_applet_with_the_icon_dialog(self):
        # The icon mode opens its own kdialog client; a plasmoid id
        # combined with it would silently draw nothing.
        self.assertIn(
            "--icon-dialog",
            self.assert_usage_error("out.png", "--icon-dialog", "--applet", "x"),
        )

    def test_rejects_a_capture_size_with_the_icon_dialog(self):
        # The gate byte-compares the icon capture at 480x360; any other
        # size moves the dialog window the comparison crops assume.
        stderr = self.assert_usage_error(
            "out.png", "--icon-dialog", "--width", "320"
        )
        self.assertIn("480x360", stderr)

    def test_rejects_two_dialog_modes_names_the_icon_dialog_too(self):
        # The two-mode refusal lists the flags involved, so an icon mode
        # flag missing from that list would print a refusal without its
        # name.
        for left, right in (
            ("--icon-dialog", "--checkbox-dialog"),
            ("--icon-dialog", "--gtk-dialog"),
            ("--color-dialog", "--icon-dialog"),
        ):
            with self.subTest(left=left, right=right):
                stderr = self.assert_usage_error("out.png", left, right)
                self.assertIn(left, stderr)
                self.assertIn(right, stderr)

    def test_the_icon_dialog_requires_kdialog(self):
        # With kdialog absent the CLI names it instead of starting a session.
        tools = render_surface.REQUIRED_TOOLS + ("kdialog",)
        assert_missing_tool_named(
            self, render_surface.main, tools, ("out.png", "--icon-dialog")
        )

    def test_the_help_text_names_the_icon_dialog(self):
        # --help lists every dialog mode; a flag missing from that help
        # would leave the mode unusable by anyone reading the CLI.
        _, stdout, _ = _call_capturing(lambda: render_surface.main(["--help"]))
        self.assertIn("--icon-dialog", stdout)

    def test_the_checkbox_dialog_requires_kdialog(self):
        # The default applet render cannot need every tool the dialog mode
        # needs, so the dialog requirement is refused per mode: with kdialog
        # absent the CLI names it instead of starting a session.
        tools = render_surface.REQUIRED_TOOLS + ("kdialog",)
        assert_missing_tool_named(
            self, render_surface.main, tools, ("out.png", "--checkbox-dialog")
        )


class TestSessionSetup(unittest.TestCase):
    def test_creates_the_scratch_layout_and_removes_it(self):
        with render_session.Session.create() as session:
            root = session.root
            self.assertTrue(root.name.startswith("render-surface-"))
            for directory in (session.runtime, session.config, session.data, session.home):
                with self.subTest(directory=directory.name):
                    self.assertTrue(directory.is_dir())
            self.assertEqual(0o700, stat.S_IMODE(session.runtime.stat().st_mode))
            self.assertEqual(session.root / "surface.png", session.surface)

    def test_creation_leaves_the_themes_link_to_link_kvantum_themes(self):
        # `link_kvantum_themes` is the one place the scratch home's themes
        # link is made, and only after `make install` has populated the data
        # home's `themes/`: at creation there is nothing to link, so creation
        # leaves no `.local` tree behind either.
        with render_session.Session.create() as session:
            self.assertFalse((session.home / ".local").exists())

    def test_links_the_scratch_homes_themes_for_the_kvantum_lookups(self):
        # Kvantum searches its theme under the literal
        # `$HOME/.local/share/themes/` path, which no `XDG_DATA_HOME` a
        # throwaway install targets satisfies: the session links the two, so
        # a Qt client in the session reads the installed theme directory.
        with render_session.Session.create() as session:
            error, themes = render_setup.link_kvantum_themes(session)
            self.assertIsNone(error)
            self.assertTrue(themes.is_symlink())
            self.assertEqual(str(session.data / "themes"), os.readlink(themes))
            # A session is linked once, so a second call is refused with the
            # first link still in place: the CLI reports it to the caller
            # rather than overwrite a working session link.
            second, link = render_setup.link_kvantum_themes(session)
            self.assertIsInstance(second, FileExistsError)
            self.assertTrue(link.is_symlink())

    def test_the_settings_and_scripts_paths_are_reported(self):
        with render_session.Session.create() as session:
            self.assertEqual(session.root / "install.log", session.install_log)
            self.assertEqual(session.root / "render.log", session.render_log)

    def test_environment_points_at_the_scratch_homes(self):
        with render_session.Session.create() as session:
            self.assertEqual(
                str(session.home), session.environment["HOME"]
            )
            self.assertEqual(
                str(session.runtime), session.environment["XDG_RUNTIME_DIR"]
            )
            self.assertEqual(
                str(session.config), session.environment["XDG_CONFIG_HOME"]
            )
            self.assertEqual(str(session.data), session.environment["XDG_DATA_HOME"])

    def test_environment_disables_kwin_screenshot_authorization(self):
        # The nested compositor cannot map its clients to a desktop-file
        # identity, and KWin 6.6 rejects an unauthorized ScreenShot2 call
        # before Spectacle can write the capture. The switch must reach KWin
        # through the session environment, so the capture still works there.
        with render_session.Session.create() as session:
            self.assertEqual(
                "1",
                session.environment["KWIN_SCREENSHOT_NO_PERMISSION_CHECKS"],
            )

    def test_environment_forces_spectacles_null_video_platform(self):
        # Spectacle would otherwise build its Wayland video platform even for
        # a still capture and wait on a nonexistent PipeWire/screencast
        # service before the capture starts.
        with render_session.Session.create() as session:
            self.assertEqual(
                "VideoPlatformNull",
                session.environment["SPECTACLE_VIDEO_PLATFORM"],
            )

    def test_environment_forces_dbus_services_to_use_offscreen_qt(self):
        # D-Bus-activated Qt services inherit this environment before the
        # nested Wayland socket is ready, so they must not try that display.
        with mock.patch.dict(os.environ, {"QT_QPA_PLATFORM": "wayland"}):
            with render_session.Session.create() as session:
                self.assertEqual("offscreen", session.environment["QT_QPA_PLATFORM"])

    def test_environment_drops_the_callers_session(self):
        ambient = {
            "WAYLAND_DISPLAY": "wl",
            "DISPLAY": ":9",
            "DESTDIR": "/stage",
            "MAKEFLAGS": "-- DESTDIR=/stage",
            "XDG_CONFIG_DIRS": "/ambient",
        }
        with mock.patch.dict(os.environ, ambient):
            with render_session.Session.create() as session:
                environment = session.environment
        # The host display is replaced, not inherited: the nested session
        # must point at its own compositor socket.
        self.assertEqual(render_session.SOCKET, environment["WAYLAND_DISPLAY"])
        self.assertNotEqual("wl", environment["WAYLAND_DISPLAY"])
        for key in ambient:
            if key == "WAYLAND_DISPLAY":
                continue
            with self.subTest(key=key):
                self.assertNotIn(key, environment)

    def test_a_setup_failure_removes_the_partial_scratch_root(self):
        # Session.create promises to remove the scratch root when setup fails.
        # A file where the runtime directory belongs makes the first mkdir
        # fail after mkdtemp has created the root, so the except arm is the
        # only thing that can remove it.
        prepared = tmp_dir.make_tmp_dir(self) / "render-surface-fixed"
        prepared.mkdir()
        (prepared / "rt").write_bytes(b"in the way")

        with mock.patch.object(
            render_session.tempfile, "mkdtemp", return_value=str(prepared)
        ):
            with self.assertRaises(FileExistsError):
                render_session.Session.create()

        self.assertFalse(prepared.exists())

    def test_a_failure_after_the_layout_is_created_removes_the_scratch_root(self):
        # The runtime directory's mode is the last setup step; if it fails
        # after all three directories exist, the whole root must still go.
        prepared = tmp_dir.make_tmp_dir(self) / "render-surface-fixed"
        prepared.mkdir()

        with mock.patch.object(
            render_session.tempfile, "mkdtemp", return_value=str(prepared)
        ), mock.patch.object(
            render_session.os, "chmod", side_effect=PermissionError("denied")
        ):
            with self.assertRaises(PermissionError):
                render_session.Session.create()

        self.assertFalse(prepared.exists())


class TestSessionScript(unittest.TestCase):
    """The in-session shell script applies the scheme and captures the applet.

    It is the only place the colour scheme is applied inside the throwaway
    session and the only place ``spectacle`` is told what to capture. A
    dropped flag or a wrong positional parameter there renders an unthemed or
    empty surface, which the fidelity gate then reports as a pixel difference
    rather than as the renderer's own bug.
    """

    def test_applies_the_scheme_before_opening_the_client(self):
        script = render_session.session_script()
        # The installed scheme id, applied inside the session; `|| exit 1`
        # aborts the session on a failed apply instead of capturing an
        # unthemed window. The client opens before the settle sleep, so the
        # sleep is the wait for it to paint.
        self.assertIn(
            f"plasma-apply-colorscheme {render_session.COLOR_SCHEME} || exit 1",
            script,
        )
        self.assertLess(script.index('"$@"'), script.index("sleep"))

    def test_pins_the_clients_to_the_nested_wayland_platform(self):
        # A headless caller has no XDG_SESSION_TYPE, so Qt otherwise falls
        # through to xcb and aborts without a display. The export lives in
        # this session shell, after KWin has started, so it reaches only the
        # clients and the scheme apply.
        script = render_session.session_script()
        self.assertTrue(
            script.startswith("export QT_QPA_PLATFORM=wayland; "),
            "the session must export the nested Wayland platform first",
        )

    def test_captures_to_the_capture_positional_with_spectacle(self):
        # `-b` runs without a GUI, `-n` suppresses the notification, `-f`
        # captures the full screen, and `-o` writes the surface path that the
        # session command passes as the second positional parameter.
        self.assertIn(
            'spectacle -b -n -f -o "$capture"', render_session.session_script()
        )

    def test_stops_the_client_and_exits_with_the_capture_status(self):
        script = render_session.session_script()
        self.assertIn('kill "$client"', script)
        self.assertIn('wait "$client"', script)
        self.assertIn("exit $status", script)
        # A client that ignores SIGTERM must not hold the session past its
        # capture; the bounded wait escalates to SIGKILL before reaping.
        self.assertIn("waited=0; ", script)
        self.assertIn('kill -9 "$client"', script)
        self.assertLess(
            script.index('kill "$client"'), script.index('kill -9 "$client"')
        )
        self.assertLess(
            script.index('kill -9 "$client"'), script.index('wait "$client"')
        )
        # Reap the killed child before exiting; the wait's status must not
        # replace the capture status saved above.
        self.assertLess(
            script.index('kill "$client"'), script.index('wait "$client"')
        )

    def test_waits_for_client_termination_and_preserves_capture_status(self):
        root = tmp_dir.make_tmp_dir(self)
        apply = root / "plasma-apply-colorscheme"
        apply.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        apply.chmod(0o755)
        environment = dict(os.environ, PATH=f"{root}:{os.environ['PATH']}")
        ready = root / "ready"
        stopped = root / "stopped"
        client = root / "client.py"
        client.write_text(
            "import signal, sys, time\n"
            "from pathlib import Path\n"
            "def stop(*args):\n"
            "    time.sleep(0.2)\n"
            "    Path(sys.argv[2]).write_text('terminated')\n"
            "    sys.exit(23)\n"
            "signal.signal(signal.SIGTERM, stop)\n"
            "signal.alarm(5)\n"
            "Path(sys.argv[1]).touch()\n"
            "signal.pause()\n",
            encoding="utf-8",
        )
        # Replace only the desktop commands. The real shell launches, signals
        # and waits for a real child whose termination deliberately takes time.
        # run_logged tears down descendants when the shell exits, so omitting
        # wait prevents the child from recording its completed termination.
        poll = (
            "import time, sys; from pathlib import Path; "
            "deadline = time.monotonic() + 3\n"
            "while not Path(sys.argv[1]).exists():\n"
            "    if time.monotonic() > deadline: sys.exit(1)\n"
            "    time.sleep(0.01)\n"
        )
        for capture_status in (0, 7):
            with self.subTest(capture_status=capture_status):
                ready.unlink(missing_ok=True)
                stopped.unlink(missing_ok=True)
                prefix = (
                    f'sleep() {{ if [ "$1" = 0 ]; then {shlex.join([sys.executable, "-c", poll, str(ready)])}; else command sleep "$@"; fi; }}; '
                    f"spectacle() {{ return {capture_status}; }}; "
                )
                status = render_workflow.run_logged(
                    ["sh", "-c", prefix + render_session.session_script(),
                     "sh", "0", str(root / "capture.png"), sys.executable,
                     str(client), str(ready), str(stopped)],
                    environment, root / "session.log", 5, root,
                )
                self.assertEqual(capture_status, status)
                self.assertTrue(stopped.exists(), "session exited before client termination")


class TestSessionCommand(unittest.TestCase):
    @contextlib.contextmanager
    def _dialog_command(self, client_builder):
        """Yield ``(session, command)`` for one dialog client's render command.

        The three dialog clients share the render's dialog geometry, settle
        and supervision timeout, and each puts the ``kdialog`` word into the
        in-session script, so one context manager drives the three wording
        tests: each passes its client builder and asserts the words specific
        to that dialog. The shared surface geometry and time values are the
        dialog render's, so this helper must not serve the non-dialog case
        with its own window size.
        """
        with render_session.Session.create() as session:
            command = render_session.session_command(
                session,
                list(client_builder(session)),
                2.5,
                480,
                360,
                9.5,
            )
            self.assertIn("kdialog", command.argv[-1])
            yield session, command

    def test_carries_the_geometry_the_script_and_the_surface_path(self):
        with render_session.Session.create() as session:
            command = render_session.session_command(
                session, ["plasmawindowed", "a b"], 2.5, 64, 48, 9.5
            )
            self.assertEqual(session.render_log, command.log)
            self.assertEqual(9.5, command.timeout)
            self.assertEqual(
                [
                    "dbus-run-session",
                    "--",
                    "kwin_wayland",
                    "--virtual",
                    "--no-lockscreen",
                    "--width",
                    "64",
                    "--height",
                    "48",
                    "--socket",
                    render_session.SOCKET,
                    "--exit-with-session",
                ],
                command.argv[:-1],
            )
            self.assertIn(str(session.surface), command.argv[-1])
            self.assertIn(render_session.session_script(), command.argv[-1])
            # The client words are positional parameters of the in-session
            # `sh -c`, so their space cannot become shell syntax.
            self.assertIn("'a b'", command.argv[-1])
            # After `sh -c <script> sh`, the positional parameters carry the
            # settle seconds first, the capture path second and the client
            # words from the third on: the script reads `settle="$1"` and
            # `capture="$2"`, so a dropped or swapped value here would sleep
            # on the surface path or put the client where the capture goes.
            self.assertEqual(
                [
                    "2.5",
                    str(session.surface),
                    "plasmawindowed",
                    "a b",
                ],
                shlex.split(command.argv[-1])[4:],
            )

    def test_client_words_with_shell_syntax_and_empty_words_stay_positional(self):
        client = ["client", "two words", "quote'and $HOME; $(false)", ""]
        with render_session.Session.create() as session:
            command = render_session.session_command(
                session, client, 1, 64, 48, 9.5
            )

            self.assertEqual(
                ["1", str(session.surface), *client],
                shlex.split(command.argv[-1])[4:],
            )

    def test_carries_the_checkbox_dialog_client_words(self):
        with self._dialog_command(checkbox_dialog_client) as (session, command):
            # The dontagain config file lands in the scratch config home, so
            # the client never writes the caller's configuration. Recovering
            # the shell words also pins the warning, prompt and flag order.
            self.assertEqual(
                (
                    "kdialog",
                    "--title",
                    "Test",
                    "--warningyesno",
                    "Delete?",
                    "--dontagain",
                    f"{session.config / 'kde-dontagain'}:widgets",
                ),
                tuple(shlex.split(command.argv[-1])[-7:]),
            )

    def test_carries_the_combobox_dialog_client_words(self):
        with self._dialog_command(combobox_dialog_client) as (_, command):
            # The chooser's items travel as separate positional words of the
            # in-session script, so a space inside one cannot become shell
            # syntax.
            self.assertEqual(
                [
                    "kdialog",
                    "--title",
                    "Test",
                    "--combobox",
                    "Choose a disk:",
                    "Macintosh HD",
                    "Zip Disk",
                ],
                list(combobox_dialog_client(None)),
            )
            words = shlex.split(command.argv[-1])
            self.assertEqual(
                list(combobox_dialog_client(None)),
                words[-len(combobox_dialog_client(None)) :],
            )

    def test_carries_the_lineedit_dialog_client_words(self):
        with self._dialog_command(lineedit_dialog_client) as (session, command):
            # The input box's prompt travels as one quoted word despite its
            # space, and no initial value follows it: the empty field keeps
            # the caret at the field's left padding, which the gate's crop
            # stays clear of.
            self.assertEqual(
                [
                    "kdialog",
                    "--title",
                    "Test",
                    "--inputbox",
                    "Choose a name:",
                ],
                list(lineedit_dialog_client(session)),
            )
            self.assertIn("'Choose a name:'", command.argv[-1])
            words = shlex.split(command.argv[-1])
            self.assertEqual(
                list(lineedit_dialog_client(session)),
                words[len(words) - len(lineedit_dialog_client(session)) :],
            )

    def test_carries_the_icon_dialog_client_words(self):
        with self._dialog_command(icon_dialog_client) as (_, command):
            # The icon chooser's category default travels as its own quoted
            # word: the empty string keeps the chooser on the application
            # group's default listing, so no chooser-state pin can enter a
            # capture. shlex quotes nothing, so the words stay script text.
            client = list(icon_dialog_client(None))
            self.assertEqual(
                [
                    "kdialog",
                    "--title",
                    "Test",
                    "--geticon",
                    "application",
                    "",
                ],
                client,
            )
            self.assertTrue(command.argv[-1].endswith(shlex.join(client)))
            # And shell word-splitting of the script's arguments -- what the
            # script's `$@` hands kdialog -- recovers exactly that argv, so
            # the empty category word is still its own word.
            self.assertEqual(client, shlex.split(command.argv[-1])[-len(client) :])

    def test_gtk_dialog_client_opens_a_zenity_text_entry(self):
        self.assertEqual(
            ("zenity", "--title", "Test", "--entry", "--text", "Choose a name:"),
            gtk_dialog_client(None),
        )


    def test_carries_the_slider_dialog_client_words(self):
        with self._dialog_command(slider_dialog_client) as (_, command):
            # The slider's prompt, minimum, maximum and step travel as
            # separate quoted words of the in-session script, so a space in
            # the prompt cannot become shell syntax. Value zero rests the
            # thumb at the trough's left end in its resting state.
            client = list(slider_dialog_client(None))
            self.assertEqual(
                [
                    "kdialog",
                    "--title",
                    "Test",
                    "--slider",
                    "Brightness:",
                    "0",
                    "100",
                    "10",
                ],
                client,
            )
            self.assertTrue(command.argv[-1].endswith(shlex.join(client)))
            # And shell word-splitting of the script's arguments -- what the
            # script's `"$@"` hands kdialog -- recovers exactly that argv, so
            # each number is still its own word (the prompt carries no space,
            # so shlex quotes nothing).
            self.assertEqual(client, shlex.split(command.argv[-1])[-len(client) :])

    def test_carries_the_progressbar_dialog_client_words(self):
        with self._dialog_command(progressbar_dialog_client) as (_, command):
            # The helper daemon's prompt travels as its own word, and the
            # meter never moves: no D-Bus call follows the printed
            # reference, so no striped progress-pattern tile or busy
            # animation enters any capture. shlex.join never quotes a
            # colon, so the Working: prompt stays unquoted script text.
            client = list(progressbar_dialog_client(None))
            self.assertEqual(
                [
                    "kdialog_progress_helper",
                    "--title",
                    "Test",
                    "--progressbar",
                    "Working:",
                ],
                client,
            )
            self.assertTrue(command.argv[-1].endswith(shlex.join(client)))
            # And shell word-splitting of the script's arguments -- what the
            # script's `"$@"` hands the helper -- recovers exactly that
            # argv, so the colon-tailed prompt is still its own word.
            self.assertEqual(client, shlex.split(command.argv[-1])[-len(client) :])

    def test_carries_the_calendar_dialog_client_words(self):
        with self._dialog_command(calendar_dialog_client) as (_, command):
            # The calendar's prompt, pinned default date and date format
            # travel as separate quoted words of the in-session script. The
            # pinned date is load-bearing: without --dateformat kdialog
            # ignores --default and opens today's month, with it the view
            # never contains today's date and the gate's bands stay
            # clock-independent.
            client = list(calendar_dialog_client(None))
            self.assertEqual(
                [
                    "kdialog",
                    "--title",
                    "Test",
                    "--calendar",
                    "Calendar:",
                    "--default",
                    "1970-01-07",
                    "--dateformat",
                    "yyyy-MM-dd",
                ],
                client,
            )
            self.assertTrue(command.argv[-1].endswith(shlex.join(client)))
            self.assertEqual(client, shlex.split(command.argv[-1])[-len(client) :])

    def test_carries_the_color_dialog_client_words(self):
        with self._dialog_command(color_dialog_client) as (session, command):
            # The prompt name travels as its own quoted word of the in-session
            # script. The dialog shows no clock-dependent content -- no date
            # and no clock-driven selection can enter any capture -- so the
            # client carries no default pin.
            client = list(color_dialog_client(session))
            self.assertEqual(
                ["kdialog", "--title", "Test", "--getcolor"],
                client,
            )
            self.assertTrue(command.argv[-1].endswith(shlex.join(client)))
            self.assertEqual(client, shlex.split(command.argv[-1])[-len(client) :])

    def test_carries_the_menu_dialog_client_words(self):
        with self._dialog_command(menu_dialog_client) as (session, command):
            # The whole client suffix serializes exactly as built, with the
            # prompt kept as one quoted word despite its space.
            client = list(menu_dialog_client(session))
            self.assertTrue(command.argv[-1].endswith(shlex.join(client)))
            self.assertIn("'Pick an item:'", command.argv[-1])
            # And shell word-splitting of the script's arguments -- what the
            # script's `"$@"` hands kdialog -- recovers exactly that argv, so
            # each menu item and its tag is still a separate word.
            words = shlex.split(command.argv[-1])
            self.assertEqual(client, words[len(words) - len(client) :])

    def test_carries_the_radiolist_dialog_client_words(self):
        with self._dialog_command(radio_dialog_client) as (session, command):
            # The whole client suffix serializes exactly as built, with the
            # prompt kept as one quoted word despite its space. The ``on``
            # status pins the checked item as a fixed default, so the
            # selection never depends on clock, network or input.
            client = list(radio_dialog_client(session))
            self.assertTrue(command.argv[-1].endswith(shlex.join(client)))
            self.assertIn("'Pick an item:'", command.argv[-1])
            # And shell word-splitting of the script's arguments -- what the
            # script's `"$@"` hands kdialog -- recovers exactly that argv,
            # so each radio item's tag, label and status is still a separate
            # word.
            words = shlex.split(command.argv[-1])
            self.assertEqual(client, words[len(words) - len(client) :])

    def test_carries_the_textbox_dialog_client_words(self):
        with self._dialog_command(textbox_dialog_client) as (session, command):
            # The scratch text file's path travels as its own word under the
            # session root the render's context manager removes, and the
            # file exists by the time the client argv is built (the text
            # view's scrollbar geometry depends on its 40 lines).
            client = list(textbox_dialog_client(session))
            self.assertEqual(
                [
                    "kdialog",
                    "--title",
                    "Test",
                    "--textbox",
                    str(session.root / "textbox.txt"),
                ],
                client,
            )
            self.assertTrue((session.root / "textbox.txt").is_file())
            self.assertTrue(command.argv[-1].endswith(shlex.join(client)))
            self.assertEqual(client, shlex.split(command.argv[-1])[-len(client) :])


class TestSessionThemeSources(unittest.TestCase):
    """``install_theme``, ``write_session_configs`` and the Kvantum selection
    source the session.

    The pipeline tests stub ``make`` or observe only ``kwinrc``'s decoration
    block through the session, so a wiring mistake in these three calls -- the
    install staged outside the scratch data home, ``plasmarc`` or its
    theme-defaults section dropped, or a Kvantum selection with the wrong
    theme id -- would be invisible to the offline suite and surface only in
    the slow real render. These tests drive the functions directly against a
    real scratch session.
    """

    def test_install_theme_installs_the_theme_into_the_scratch_data_home(self):
        # Run the real `make install` with the session's environment: it is a
        # fast copy into the scratch data home, so this is the visible result
        # of the wiring (argv, environment, cwd) rather than a re-derivation.
        with render_session.Session.create() as session:
            status, install_log = render_setup.install_theme(session)
            self.assertEqual(0, status)
            self.assertTrue(install_log.exists(), "the install log is missing")
            for artifact in (
                "color-schemes/MacOS8.colors",
                "aurorae/themes/org.macos8.desktop",
                "themes/org.macos8.desktop/Kvantum/org.macos8.desktop.kvconfig",
                "plasma/look-and-feel/org.macos8.desktop",
                "fonts/org.macos8.desktop",
                "wallpapers",
            ):
                with self.subTest(artifact=artifact):
                    self.assertTrue(
                        (session.data / artifact).exists(),
                        f"{artifact} did not land in the scratch data home",
                    )

    def test_write_session_configs_writes_both_themed_configs_into_the_config_home(self):
        with render_session.Session.create() as session:
            render_setup.write_session_configs(session)
            written = sorted(
                path.name for path in session.config.iterdir() if path.is_file()
            )
            kwinrc = (session.config / "kwinrc").read_text(encoding="utf-8")
            plasmarc = (session.config / "plasmarc").read_text(encoding="utf-8")
        # Exactly the two files the session's in-session commands read; extra
        # files here would also end up in the caller-visible default config.
        self.assertEqual(["kwinrc", "plasmarc"], written)
        self.assertIn("theme=org.macos8.desktop", kwinrc)
        self.assertEqual("[Theme]\nname=org.macos8.desktop\n", plasmarc)

    def test_write_kvantum_selection_names_the_theme_for_qt_clients(self):
        # kdialog and other Qt clients style through the engine, which reads
        # the selected theme name from this file; without it the scratch
        # render shows the engine's compiled-in default theme, and the
        # pipeline tests (which read only kwinrc) would stay green.
        with render_session.Session.create() as session:
            render_setup.write_kvantum_selection(session)
            selection = (
                session.config / "Kvantum" / "kvantum.kvconfig"
            ).read_text(encoding="utf-8")
        self.assertEqual("[General]\ntheme=org.macos8.desktop\n", selection)

    def test_write_kvantum_selection_overwrites_a_stale_selection(self):
        # The scratch config home starts empty, but the function still has to
        # cope with an existing Kvantum directory and file in one call, so a
        # stale selection cannot survive a rewritten session.
        with render_session.Session.create() as session:
            directory = session.config / "Kvantum"
            directory.mkdir()
            (directory / "kvantum.kvconfig").write_text(
                "[General]\ntheme=Another\n", encoding="utf-8"
            )
            render_setup.write_kvantum_selection(session)
            selection = (
                directory / "kvantum.kvconfig"
            ).read_text(encoding="utf-8")
        self.assertEqual("[General]\ntheme=org.macos8.desktop\n", selection)

    def test_write_kvantum_selection_keeps_previous_file_when_publication_fails(self):
        with render_session.Session.create() as session:
            directory = session.config / "Kvantum"
            directory.mkdir()
            target = directory / "kvantum.kvconfig"
            target.write_text("previous selection\n", encoding="utf-8")
            def fail_publication(source, destination):
                self.assertEqual(target, destination)
                self.assertEqual(
                    b"[General]\ntheme=org.macos8.desktop\n", source.read_bytes()
                )
                self.assertEqual("previous selection\n", target.read_text(encoding="utf-8"))
                raise OSError("disk full")

            with mock.patch("tools.atomic_write.os.replace", side_effect=fail_publication):
                with self.assertRaisesRegex(OSError, "disk full"):
                    render_setup.write_kvantum_selection(session)
            self.assertEqual("previous selection\n", target.read_text(encoding="utf-8"))
            self.assertEqual([target], list(directory.iterdir()))

    @staticmethod
    def stage_installed_sheets(session, versions):
        """Stage the installed GTK *versions*' sheets in *session*'s data home."""
        for version in versions:
            sheet = installed_sheet(session.data, version)
            sheet.parent.mkdir(parents=True, exist_ok=True)
            sheet.write_text("", encoding="utf-8")

    def test_install_gtk_selection_publishes_both_settings_and_the_user_css(
        self,
    ):
        # The lone --gtk-dialog pipeline test stubs this function, so without
        # a direct drive a swapped sheet path, a dropped settings version or
        # a Kvantum-facing theme id in the published CSS would reach the
        # scratch session unobserved and fail only in the slow real render.
        with render_session.Session.create() as session:
            self.stage_installed_sheets(session, ("gtk-4.0", "gtk-3.0"))

            render_setup.install_gtk_selection(session)

            for version in ("gtk-4.0", "gtk-3.0"):
                with self.subTest(version=version):
                    settings = (
                        session.config / version / "settings.ini"
                    ).read_text(encoding="utf-8")
                    self.assertIn("gtk-theme-name=org.macos8.desktop", settings)
            css = (session.config / "gtk-4.0" / "gtk.css").read_text(
                encoding="utf-8"
            )
            expected_sheet = installed_sheet(session.data, "gtk-4.0")
            self.assertEqual(
                f'{GTK4_CSS_MARKER}\n@import url("{expected_sheet.as_uri()}");\n',
                css,
                "the user CSS must be marker-led and import the gtk-4.0 sheet",
            )

    def test_install_gtk_selection_raises_naming_a_missing_sheet(self):
        # `installed_sheets` reports the first missing sheet and returns None,
        # which this function must turn into the `--gtk-dialog` workflow's
        # ConfigError so `main` reports the failure and removes the scratch
        # session instead of starting an unthemed zenity client.
        with render_session.Session.create() as session:
            # Only gtk-3.0 is present, so the report must name gtk-4.0,
            # the version `installed_sheets` checks first.
            self.stage_installed_sheets(session, ("gtk-3.0",))
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                with self.assertRaises(_ConfigError) as caught:
                    render_setup.install_gtk_selection(session)
            self.assertIn(
                "installed gtk-4.0 sheet is missing", stderr.getvalue()
            )
            self.assertEqual(
                "the scratch install left a GTK sheet missing; the zenity "
                "client would start unthemed",
                str(caught.exception),
            )

    def test_the_session_selection_names_the_theme_id_the_cli_pins(self):
        # The session's Kvantum selection and `make apply`'s best-effort
        # selection are two modules each holding the theme id: a drift
        # between them would leave `make render` on the engine's compiled-in
        # default while `make apply` selects the real theme, with the
        # scratch session's reference gates comparing against the wrong
        # engine output. The id must also be the shipped package directory
        # `make install` copies, which tests/test_apply_theme.py pins from
        # the apply side.
        self.assertEqual(
            render_setup.KVANTUM_THEME, theme_apply_optional.KVANTUM_THEME
        )
        self.assertTrue(
            (apply_theme.ROOT / "theme" / "kvantum" / render_setup.KVANTUM_THEME)
            .is_dir(),
            "the session's Kvantum id is not the shipped package directory",
        )


if __name__ == "__main__":
    unittest.main()
