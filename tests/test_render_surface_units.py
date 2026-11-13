"""Tests for the render CLI and throwaway render workflow units.

The render's end-to-end capture gates live in
``tests/test_render_surface.py``, ``tests/test_render_dialog_gates.py`` and
``tests/test_render_file_dialog.py``, their failure orchestration in
``tests/test_render_failure_paths.py``, and the output publication in
``tests/test_render_output.py``; this module covers the units they are built
from: ``render_surface.main``'s argument validation and workflow delegation,
scratch environment and KWin session command construction in ``tools/render_session.py`` and
theme installation/configuration in ``tools/render_setup.py``, the capture
paint check in ``tools/render_workflow.py``, plus the
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
import tempfile
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
    render_window_rules,
    render_workflow,
    apply_optional,
)  # noqa: E402
from tools.render_clients import (
    calendar_dialog_client,
    checkbox_dialog_client,
    color_dialog_client,
    combobox_dialog_client,
    file_dialog_client,
    gtk_dialog_client,
    icon_dialog_client,
    inactive_dialog_client,
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

    def test_a_non_regular_log_keeps_the_generic_diagnosis(self):
        # The bounded tail read goes through the open guard, which raises
        # ValueError -- not OSError -- for a non-regular log, so a session
        # log swapped for a FIFO must leave the black-capture diagnosis
        # with its generic verdict instead of tracebacking out of the run.
        root = tmp_dir.make_tmp_dir(self)
        fifo = root / "session.log"
        os.mkfifo(fifo)
        self.assertFalse(render_workflow._client_exited_during_capture(fifo))


def delegated_render_args(case, argv, status=0):
    """Patch the render collaborators away, run *argv*, return the mode args.

    Seven call sites share this: with the missing-tool preflight, the
    output check, the workflow and the termination guard patched away,
    ``main`` parses its argv and hands the parsed namespace to the workflow
    mock, so a test can pin what the parser delegates without starting a
    session; *status* pins the exit status the run returns (default 0).
    """
    with (
        mock.patch.object(render_surface, "report_missing_tool", return_value=None),
        mock.patch.object(render_surface, "output_problem", return_value=None),
        mock.patch.object(render_surface, "render", return_value=status) as workflow,
        mock.patch.object(render_surface, "exit_on_termination"),
    ):
        run_status = render_surface.main(argv)

    case.assertEqual(status, run_status)
    return workflow.call_args.args[0]


def assert_delegated_capture_size(case, flag, size):
    """Assert a plain *flag* run delegates a *size* capture to the workflow.

    Thirteen tests call this: a plain --*-dialog run must capture at the
    480x360 the widget gate byte-compares, and --desktop and --splash at
    the 640x400 their gates crop, each with the applet id at its default
    (which those modes never open), not the applet render's 320x240 default.
    """
    args = delegated_render_args(case, ("out.png", flag))
    case.assertEqual(size, (args.width, args.height))
    case.assertEqual("org.kde.plasma.calculator", args.applet)


def assert_rejects_applet_with_fixed_client(case, flag):
    """Assert *flag* combined with --applet is a usage error naming both.

    Fifteen tests call this: the dialog, desktop and splash modes each open
    their own client, so a plasmoid id combined with any of them has no
    window to open it in, and every refusal names the fixed flag and
    --applet.
    """
    status, stderr = call_main(render_surface.main, "out.png", flag, "--applet", "x")
    case.assertEqual(2, status)
    case.assertIn(flag, stderr)
    case.assertIn("--applet", stderr)


def assert_rejects_capture_size_with_fixed_client(
    case, flag, size_label, size_argv=("--height", "240")
):
    """Assert *flag* with a custom size is a usage error naming *size_label*.

    Fifteen tests call this: the gates byte-compare or crop the dialog
    capture at 480x360 and the desktop and splash captures at 640x400, so
    any other size moves the window the pinned comparisons assume.
    """
    status, stderr = call_main(render_surface.main, "out.png", flag, *size_argv)
    case.assertEqual(2, status)
    case.assertIn(flag, stderr)
    case.assertIn(size_label, stderr)


def assert_two_mode_refusal_names_both(case, flag, partners):
    """Assert the two-mode refusal names *flag* and each *partner* flag.

    Fourteen tests call this: the refusal lists the flags involved,
    so a flag missing from that list would print a refusal without its name.
    """
    for right in partners:
        with case.subTest(left=flag, right=right):
            status, stderr = call_main(render_surface.main, "out.png", flag, right)
            case.assertEqual(2, status)
            case.assertIn(flag, stderr)
            case.assertIn(right, stderr)


def assert_dialog_requires_kdialog(case, flag):
    """Assert a *flag* run with kdialog absent names the tool and exits 2.

    Thirteen per-mode tests call this: with kdialog absent the CLI names it
    instead of starting a session.
    """
    tools = render_surface.REQUIRED_TOOLS + ("kdialog",)
    assert_missing_tool_named(case, render_surface.main, tools, ("out.png", flag))


def assert_help_lists_flag(case, flag):
    """Assert --help's stdout lists *flag*.

    Nine tests call this: --help lists every dialog mode beside the desktop
    and splash flags, so a flag missing from that help leaves the mode
    unusable by anyone reading the CLI.
    """
    _, stdout, _ = _call_capturing(lambda: render_surface.main(["--help"]))
    case.assertIn(flag, stdout)


class TestArguments(unittest.TestCase):

    def setUp(self):
        # The applet preflight consults the host's XDG data roots; these
        # delegation tests pin argument handling, not package discovery, so
        # the check is pinned off and they stay host-independent.
        patcher = mock.patch.object(
            render_surface, "applet_problem", return_value=None
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_cli_delegates_validated_options_to_render_workflow(self):
        args = delegated_render_args(
            self, ("out.png", "--applet", "test.applet"), 7
        )
        self.assertEqual("test.applet", args.applet)
        self.assertEqual((320, 240), (args.width, args.height))
        self.assertIs(render_workflow.render, render_surface.render)

    def test_cli_delegates_the_settle_and_timeout_to_the_workflow(self):
        # render() reads args.settle and args.timeout to build the session
        # command and its supervision timeout, so a non-default value must
        # reach it parsed, not fall back to the parser defaults.
        args = delegated_render_args(
            self, ("out.png", "--settle", "1.25", "--timeout", "33")
        )
        self.assertEqual(1.25, args.settle)
        self.assertEqual(33.0, args.timeout)

    def test_accepts_the_minimum_settle_and_timeout(self):
        # The bounds are inclusive: --settle 0 (no wait before the capture)
        # and --timeout 1 are the smallest values the parser accepts. Both
        # satisfy the timeout-longer-than-settle rule (1 > 0).
        args = delegated_render_args(
            self, ("out.png", "--settle", "0", "--timeout", "1")
        )
        self.assertEqual(0.0, args.settle)
        self.assertEqual(1.0, args.timeout)

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

    def test_a_single_custom_dimension_keeps_the_other_default(self):
        for option, value, expected in (
            ("--width", "640", (640, 240)),
            ("--height", "480", (320, 480)),
        ):
            with self.subTest(option=option):
                args = delegated_render_args(self, ("out.png", option, value))
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

    def test_rejects_a_path_carrying_applet(self):
        # A plasmoid id is a dotted KPlugin id; a path separator would make a
        # later path-joining existence check read outside the plasmoids
        # directories, so the parse refuses it.
        for bad in ("a/b", "a\\b"):
            with self.subTest(bad=bad):
                self.assertIn(
                    "--applet", self.assert_usage_error("out.png", "--applet", bad)
                )

    def test_applet_refusals_name_the_actual_defect(self):
        # Each refused --applet value names the defect it carries instead of
        # one conflated wording: a path separator is answered with the path
        # refusal (not the NUL one), an option-like value with the option-like
        # refusal, and so on, so the diagnostic tells the caller what to fix.
        cases = {
            "": "not empty",
            "--help-all": "not option-like",
            "a/b": "not a path",
            "a\\b": "not a path",
            "org.example\0widget": "without NUL",
        }
        for value, expected in cases.items():
            with self.subTest(value=value):
                # The ``=`` form is the only one that carries an option-like
                # value at all: ``--applet --help-all`` reads as a missing
                # value before the type runs.
                self.assertIn(
                    expected, self.assert_usage_error("out.png", "--applet=" + value)
                )

    def test_requires_an_output_path(self):
        self.assert_usage_error()

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
        # The client that passed the settle's liveness check is frozen
        # before the capture and resumed before the termination:
        # Spectacle's unbounded startup latency must not outlive a client
        # with a finite lifetime (BUGS.md, the splash black-frame report,
        # director decision 2026-11-12). A stopped client only acts on the
        # termination signal once the resume reaches it, so the resume
        # must precede the kill.
        self.assertIn('kill -STOP "$client" 2>/dev/null; ', script)
        self.assertIn('kill -CONT "$client" 2>/dev/null; ', script)
        self.assertLess(
            script.index('"$1 exited before the capture"'),
            script.index('kill -STOP "$client"'),
        )
        self.assertLess(
            script.index('kill -STOP "$client"'),
            script.index("spectacle -b"),
        )
        self.assertLess(
            script.index('kill -CONT "$client"'),
            script.index('kill "$client"'),
        )
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

    def test_logs_the_capture_timeline_and_a_client_exit_during_the_capture(self):
        # The black-frame diagnosis needs to tell a vanished client from an
        # unpainted window, so the script stamps every stage on one wall
        # clock and, after the capture returns, records whether the client
        # that passed the settle's liveness check is still running. The stub
        # client passes the check (it is alive through the settle) and the
        # session then freezes it for the capture, so it cannot exit on its
        # own mid-capture; the spectacle stub therefore ends it with
        # SIGKILL -- the only thing that can stop a frozen client -- before
        # returning, so the session's post-capture check deterministically
        # sees a dead client; the timing stamps and the exit marker the
        # render's black-capture diagnosis greps for must all be in the
        # log, and the capture status must survive.
        root = tmp_dir.make_tmp_dir(self)
        apply = root / "plasma-apply-colorscheme"
        apply.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        apply.chmod(0o755)
        environment = dict(os.environ, PATH=f"{root}:{os.environ['PATH']}")
        ready = root / "ready"
        pidfile = root / "client.pid"
        client = root / "client.py"
        client.write_text(
            "import os, sys, time\n"
            "from pathlib import Path\n"
            "Path(sys.argv[1]).write_text(str(os.getpid()))\n"
            "Path(sys.argv[2]).touch()\n"
            "time.sleep(0.5)\n",
            encoding="utf-8",
        )
        poll = (
            "import time, sys; from pathlib import Path; "
            "deadline = time.monotonic() + 3\n"
            "while not Path(sys.argv[1]).exists():\n"
            "    if time.monotonic() > deadline: sys.exit(1)\n"
            "    time.sleep(0.01)\n"
        )
        # The settle's `sleep 0` polls until the client has started; the
        # spectacle stub then SIGKILLs the held client (a frozen client
        # cannot exit on its own) and spins until the recorded pid is gone,
        # so the client -- alive at the liveness check -- dies mid-capture.
        prefix = (
            f'sleep() {{ if [ "$1" = 0 ]; then '
            f"{shlex.join([sys.executable, '-c', poll, str(ready)])}; "
            'else command sleep "$@"; fi; }; '
            f'spectacle() {{ pid=$(cat "{pidfile}"); '
            'kill -9 "$pid" 2>/dev/null; n=0; '
            'while kill -0 "$pid" 2>/dev/null && [ $n -lt 200 ]; do '
            'command sleep 0.01; n=$((n + 1)); done; return 0; }; '
        )
        status = render_workflow.run_logged(
            ["sh", "-c", prefix + render_session.session_script(),
             "sh", "0", str(root / "capture.png"), sys.executable,
             str(client), str(pidfile), str(ready)],
            environment, root / "session.log", 10, root,
        )
        self.assertEqual(0, status)
        log = (root / "session.log").read_text(encoding="utf-8")
        for marker in (
            "render-session: client started at ",
            "render-session: settle done at ",
            "render-session: capturing at ",
            "render-session: capture status 0 at ",
            render_session.CLIENT_EXITED_DURING_CAPTURE,
        ):
            self.assertIn(marker, log)
        self.assertNotIn("client alive after the capture", log)

    def test_holds_the_client_across_the_capture_and_resumes_it_before_the_termination(
        self,
    ):
        # The client that passes the settle's liveness check is frozen with
        # SIGSTOP before the capture and resumed with SIGCONT immediately
        # before the post-capture termination, so Spectacle's unbounded
        # startup latency cannot outlive a client with a finite lifetime
        # (BUGS.md, the splash black-frame report, director decision
        # 2026-11-12). The spectacle stub records the client's scheduler
        # state at capture start, which must be "T" (stopped) while the
        # capture runs; a trapped SIGTERM that writes its own file pins the
        # resume, because a still-stopped client cannot run its termination
        # handler inside the session's bounded wait.
        root = tmp_dir.make_tmp_dir(self)
        apply = root / "plasma-apply-colorscheme"
        apply.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        apply.chmod(0o755)
        environment = dict(os.environ, PATH=f"{root}:{os.environ['PATH']}")
        ready = root / "ready"
        pidfile = root / "client.pid"
        captured_state = root / "captured-state"
        terminated = root / "terminated"
        client = root / "client.py"
        client.write_text(
            "import os, signal, sys\n"
            "from pathlib import Path\n"
            "Path(sys.argv[1]).write_text(str(os.getpid()))\n"
            "Path(sys.argv[2]).touch()\n"
            "def terminate(*args):\n"
            "    Path(sys.argv[3]).write_text('terminated')\n"
            "    sys.exit(0)\n"
            "signal.signal(signal.SIGTERM, terminate)\n"
            "signal.pause()\n",
            encoding="utf-8",
        )
        poll = (
            "import time, sys; from pathlib import Path; "
            "deadline = time.monotonic() + 3\n"
            "while not Path(sys.argv[1]).exists():\n"
            "    if time.monotonic() > deadline: sys.exit(1)\n"
            "    time.sleep(0.01)\n"
        )
        # The spectacle stub reads the client's scheduler state at capture
        # start and returns only once that state is "T" (stopped), so a
        # capture that starts without the hold cannot satisfy the test.
        state_of = 'state=$(awk \'{print $3}\' "/proc/$pid/stat" 2>/dev/null); '
        prefix = (
            f'sleep() {{ if [ "$1" = 0 ]; then '
            f"{shlex.join([sys.executable, '-c', poll, str(ready)])}; "
            'else command sleep "$@"; fi; }; '
            f'spectacle() {{ pid=$(cat "{pidfile}"); n=0; '
            f'{state_of} printf %s "$state" > "{captured_state}"; '
            'while [ "$state" != T ] && [ $n -lt 200 ]; do '
            f'command sleep 0.01; n=$((n + 1)); {state_of} done; '
            'return 0; }; '
        )
        status = render_workflow.run_logged(
            ["sh", "-c", prefix + render_session.session_script(),
             "sh", "0", str(root / "capture.png"), sys.executable,
             str(client), str(pidfile), str(ready), str(terminated)],
            environment, root / "session.log", 10, root,
        )
        self.assertEqual(0, status)
        self.assertEqual("T", captured_state.read_text(encoding="utf-8"))
        self.assertTrue(
            terminated.exists(),
            "the held client was never resumed for its termination",
        )
        log = (root / "session.log").read_text(encoding="utf-8")
        self.assertIn("render-session: client held at ", log)
        # The post-capture aliveness check runs while the client is still
        # frozen, before the resume, so a held client reads as alive.
        self.assertIn("client alive after the capture", log)
        self.assertNotIn(render_session.CLIENT_EXITED_DURING_CAPTURE, log)


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

    def test_carries_the_inactive_dialog_wrapper_words(self):
        # The two-window client is one sh -c wrapper the session script
        # backgrounds as a single client PID: it opens the to-be-inactive
        # kdialog first and the focused one last, so KWin's newest-window
        # activation lands on the second, then waits so the wrapper stays
        # the PID the script liveness-checks and reaps. The wrapper's kdialog
        # titles are the exact matches the forced-geometry kwinrulesrc pins.
        with self._dialog_command(inactive_dialog_client) as (_, command):
            script = command.argv[-1]
            self.assertIn("sh -c", script)
            # The titles travel inside double quotes in the wrapper, which
            # the outer session script shlex-quotes as one word: single
            # quotes inside the wrapper would be escaped out of recognition
            # there.
            self.assertIn(
                f'kdialog --title "{render_window_rules.INACTIVE_TITLE}"', script
            )
            self.assertIn(
                f'kdialog --title "{render_window_rules.FOCUSED_TITLE}"', script
            )
            self.assertIn("--msgbox", script)
            self.assertIn("wait", script)
            self.assertLess(
                script.index(render_window_rules.INACTIVE_TITLE),
                script.index(render_window_rules.FOCUSED_TITLE),
                "the to-be-inactive window must spawn first so KWin "
                "activates the focused one",
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

    def test_carries_the_file_dialog_client_words(self):
        with self._dialog_command(file_dialog_client) as (session, command):
            # The factory seeds the scratch home's Documents directory with
            # exactly the three fixed empty files the capture lists, so the
            # chooser opens on a deterministic listing: no caller disk, no
            # clock and no seventh file can enter a capture.
            documents = session.home / "Documents"
            self.assertEqual(
                ["alpha.txt", "bravo.txt", "delta.rtf"],
                sorted(path.name for path in documents.iterdir()),
            )
            for path in documents.iterdir():
                self.assertTrue(path.is_file())
                self.assertEqual(0, path.stat().st_size)
            self.assertEqual(
                (
                    "kdialog",
                    "--title",
                    "Test",
                    "--getopenfilename",
                    str(documents),
                ),
                tuple(file_dialog_client(session)),
            )
            words = shlex.split(command.argv[-1])
            self.assertEqual(
                list(file_dialog_client(session)),
                words[len(words) - len(file_dialog_client(session)) :],
            )

    def test_pins_the_seeded_file_dialog_files_mtime(self):
        with self._dialog_command(file_dialog_client) as (session, _):
            # KIO sizes the details view's Date column from the rendered
            # mtime text, and a live-clock touch would let that column's
            # width -- and the header band's divider, caption, sort-arrow
            # and size-text x-positions beside it -- move with the time of
            # day, so the seeding pins both timestamps to one constant the
            # gate's existing pins can re-derive against.
            documents = session.home / "Documents"
            for name in ("alpha.txt", "bravo.txt", "delta.rtf"):
                # 1104537600 = the seed epoch tools/render_clients.py pins
                # (2005-01-01 00:00:00 UTC), spelled as a literal so the
                # expectation here is independent of the code under test.
                self.assertEqual(1104537600, (documents / name).stat().st_mtime)

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

    def test_write_desktop_selection_names_the_look_and_feel(self):
        # plasmashell only builds the themed menu bar when the scratch
        # session selects the look-and-feel, so both keys the published
        # apply records must stand in the scratch config home.
        with render_session.Session.create() as session:
            render_setup.write_desktop_selection(session)
            for name in ("plasmarc", "kdeglobals"):
                text = (session.config / name).read_text(encoding="utf-8")
                with self.subTest(file=name):
                    self.assertEqual(
                        "[KDE]\nLookAndFeelPackage=org.macos8.desktop\n", text
                    )

    def test_write_desktop_selection_appends_beside_the_defaults(self):
        # The defaults writer has already published plasmarc's [Theme] name
        # when the desktop selection runs, so the selection is appended, not
        # written over it: replacing the file would drop the desktop theme
        # name the shell reads.
        with render_session.Session.create() as session:
            (session.config / "plasmarc").write_text(
                "[Theme]\nname=org.macos8.desktop\n", encoding="utf-8"
            )
            render_setup.write_desktop_selection(session)
            self.assertEqual(
                "[Theme]\nname=org.macos8.desktop\n"
                "[KDE]\nLookAndFeelPackage=org.macos8.desktop\n",
                (session.config / "plasmarc").read_text(encoding="utf-8"),
            )

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
            render_setup.KVANTUM_THEME, apply_optional.KVANTUM_THEME
        )
        self.assertTrue(
            (apply_theme.ROOT / "theme" / "kvantum" / render_setup.KVANTUM_THEME)
            .is_dir(),
            "the session's Kvantum id is not the shipped package directory",
        )


if __name__ == "__main__":
    unittest.main()
