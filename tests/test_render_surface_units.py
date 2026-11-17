"""Tests for the render CLI and throwaway render workflow units.

The render's end-to-end capture gates live in
``tests/test_render_surface.py``, ``tests/test_render_dialog_gates.py`` and
``tests/test_render_file_dialog.py``, their failure orchestration in
``tests/test_render_failure_paths.py``, and the output publication in
``tests/test_render_output.py``; this module covers the units they are built
from: ``render_surface.main``'s argument validation and workflow delegation,
KWin session command construction in
``tools/render_session.py``, the capture paint check in
``tools/render_workflow.py``. The session command and dialog argv checks
live in ``tests/test_render_session_command.py``, the scratch-session
setup checks live in ``tests/test_render_session_setup.py``, and the
session theme-source checks live in ``tests/test_render_session_theme_sources.py``,
and the CLI calculator applet preflight checks live in
``tests/test_render_applet_preflight.py``.
"""

from __future__ import annotations

import os
import re
import shlex
import sys
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import tmp_dir
from support.cli_fixtures import _call_capturing, assert_missing_tool_named, call_main  # noqa: E402
from tools import (
    render_session,
    render_surface,
    render_workflow,
)  # noqa: E402


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

    def test_exports_the_client_pid_before_the_freeze(self):
        # A capture-side helper cannot learn the client pid from a pidfile
        # the client writes: under load the freeze can land before the
        # client's first instruction, and a pidfile read then sees nothing
        # (BUGS.md, the client-exit stub regression, 2026-11-12). The
        # session shell owns ``$!``, so it must publish the pid itself,
        # and it must do so before the stop that can predate any client
        # code.
        script = render_session.session_script()
        self.assertIn('export RENDER_SESSION_CLIENT_PID="$client"; ', script)
        self.assertLess(
            script.index('export RENDER_SESSION_CLIENT_PID="$client"'),
            script.index('kill -STOP "$client"'),
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
            "import os, signal, sys, time\n"
            # A slow start, longer than the one-second settle ceiling: under
            # load Python's startup can outlast a short ceiling.
            "time.sleep(2)\n"
            "from pathlib import Path\n"
            "def stop(*args):\n"
            "    time.sleep(0.2)\n"
            "    Path(sys.argv[2]).write_text('terminated')\n"
            "    sys.exit(23)\n"
            "signal.signal(signal.SIGTERM, stop)\n"
            "signal.alarm(30)\n"
            # The session waits on this ready file (settle is the ceiling),
            # so the freeze lands only after the client's handler is installed.
            "Path(os.environ['RENDER_SESSION_READY_FILE']).touch()\n"
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
        # The capture stub may take longer than the old five-second budget,
        # as a capture does under load. The session must still finish and
        # return its status, so the outer budget must cover the whole run.
        for capture_status, capture_seconds in ((0, 0), (7, 0), (0, 5.5)):
            # Each subtest's client touches the ready file, so the settle ends
            # on it. The 20 s settle is only the ceiling: a short one let a
            # slow client start outlast it, so the session froze the client
            # before its SIGTERM handler existed and the client died unhandled.
            with self.subTest(capture_status=capture_status, capture_seconds=capture_seconds):
                ready.unlink(missing_ok=True)
                stopped.unlink(missing_ok=True)
                prefix = (
                    f'sleep() {{ if [ "$1" = 0 ]; then {shlex.join([sys.executable, "-c", poll, str(ready)])}; else command sleep "$@"; fi; }}; '
                    f"spectacle() {{ command sleep {capture_seconds}; return {capture_status}; }}; "
                )
                status = render_workflow.run_logged(
                    ["sh", "-c", prefix + render_session.session_script(),
                     "sh", "20", str(root / "capture.png"), sys.executable,
                     str(client), str(ready), str(stopped)],
                    environment, root / "session.log", 30, root,
                )
                self.assertEqual(capture_status, status)
                log = (root / "session.log").read_text(encoding="utf-8", errors="replace")
                self.assertTrue(
                    stopped.exists(),
                    f"session exited before client termination; session log:\n{log}",
                )

    def test_the_settle_ends_early_once_the_client_writes_its_ready_file(self):
        # The settle budget is a ceiling, not a fixed sleep: a client that
        # writes RENDER_SESSION_READY_FILE as soon as its window is up lets
        # the capture start at once. The 15 s settle here would take far
        # longer than the 10 s bound if the script still slept it out.
        import time

        root = tmp_dir.make_tmp_dir(self)
        apply = root / "plasma-apply-colorscheme"
        apply.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        apply.chmod(0o755)
        environment = dict(os.environ, PATH=f"{root}:{os.environ['PATH']}")
        client = root / "client.py"
        client.write_text(
            "import os, signal\n"
            "from pathlib import Path\n"
            "signal.alarm(30)\n"
            "Path(os.environ['RENDER_SESSION_READY_FILE']).touch()\n"
            "signal.pause()\n",
            encoding="utf-8",
        )
        prefix = "spectacle() { return 0; }; "
        started = time.monotonic()
        status = render_workflow.run_logged(
            ["sh", "-c", prefix + render_session.session_script(),
             "sh", "15", str(root / "capture.png"), sys.executable, str(client)],
            environment, root / "session.log", 60, root,
        )
        elapsed = time.monotonic() - started
        log = (root / "session.log").read_text(encoding="utf-8")
        self.assertEqual(0, status)
        self.assertLess(elapsed, 10, "the settle slept out its full ceiling")
        self.assertIn("render-session: client ready at", log)

    def test_the_settle_waits_its_ceiling_when_the_client_never_signals(self):
        # A client that never writes the ready file keeps the old behaviour:
        # the session waits the whole settle ceiling before the capture.
        import time

        root = tmp_dir.make_tmp_dir(self)
        apply = root / "plasma-apply-colorscheme"
        apply.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        apply.chmod(0o755)
        environment = dict(os.environ, PATH=f"{root}:{os.environ['PATH']}")
        client = root / "client.py"
        client.write_text(
            "import signal\n"
            "signal.alarm(30)\n"
            "signal.pause()\n",
            encoding="utf-8",
        )
        prefix = "spectacle() { return 0; }; "
        started = time.monotonic()
        status = render_workflow.run_logged(
            ["sh", "-c", prefix + render_session.session_script(),
             "sh", "2", str(root / "capture.png"), sys.executable, str(client)],
            environment, root / "session.log", 60, root,
        )
        elapsed = time.monotonic() - started
        log = (root / "session.log").read_text(encoding="utf-8")
        self.assertEqual(0, status)
        self.assertGreaterEqual(elapsed, 2)
        self.assertIn("settle ceiling reached before a client ready file", log)

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
            "Path(os.environ['RENDER_SESSION_READY_FILE']).touch()\n"
            "time.sleep(0.5)\n",
            encoding="utf-8",
        )
        # The client writes the session's ready file, so the settle (1 s,
        # only the ceiling) ends once the client has started; the spectacle
        # stub then SIGKILLs the held client (a frozen client
        # cannot exit on its own) and spins until the recorded pid is gone,
        # so the client -- alive at the liveness check -- dies mid-capture.
        prefix = (
            # The stub reads the pid the session exports before the capture.
            'spectacle() { pid="$RENDER_SESSION_CLIENT_PID"; '
            'kill -9 "$pid" 2>/dev/null; n=0; '
            'while kill -0 "$pid" 2>/dev/null && [ $n -lt 200 ]; do '
            'command sleep 0.01; n=$((n + 1)); done; return 0; }; '
        )
        status = render_workflow.run_logged(
            ["sh", "-c", prefix + render_session.session_script(),
             "sh", "1", str(root / "capture.png"), sys.executable,
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
        # state once it has seen "T" (stopped) or spent its poll cap, which
        # must be "T" while the capture runs; a trapped SIGTERM that writes
        # its own file pins the resume, because a still-stopped client
        # cannot run its termination handler inside the session's bounded
        # wait.
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
            # The ready file ends the settle only once the handler is in, so
            # the hold cannot freeze the client before it can be resumed.
            "Path(os.environ['RENDER_SESSION_READY_FILE']).touch()\n"
            "signal.pause()\n",
            encoding="utf-8",
        )
        # The spectacle stub polls the client's scheduler state until it is
        # "T" (stopped): `kill -STOP` returns before the woken client stops,
        # so a single read at capture start can still see "R". A capture
        # that starts without the hold never reaches "T" and fails the test.
        state_of = 'state=$(awk \'{print $3}\' "/proc/$pid/stat" 2>/dev/null); '
        prefix = (
            # The stub reads the pid the session exports before the capture.
            # It records the final state and the number of polls it made, so
            # a capture that started before the stop landed names that case.
            'spectacle() { pid="$RENDER_SESSION_CLIENT_PID"; n=0; '
            f'{state_of} '
            'while [ "$state" != T ] && [ $n -lt 200 ]; do '
            f'command sleep 0.01; n=$((n + 1)); {state_of} done; '
            f'printf "%s %s" "$state" "$n" > "{captured_state}"; '
            'return 0; }; '
        )
        status = render_workflow.run_logged(
            ["sh", "-c", prefix + render_session.session_script(),
             "sh", "20", str(root / "capture.png"), sys.executable,
             str(client), str(pidfile), str(ready), str(terminated)],
            environment, root / "session.log", 30, root,
        )
        state, polls = captured_state.read_text(encoding="utf-8").split()
        self.assertEqual(
            "T", state,
            f"the client was still in state {state!r} after {polls} polls "
            "(cap 200) during the capture: the SIGSTOP had not taken effect "
            "within the stub's poll cap",
        )
        self.assertEqual(0, status)
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

    def test_keeps_the_one_window_session_free_of_the_focus_settle(self):
        # No mode but the inactive pair has a focus race: the default
        # session script must carry an empty focus path, so its settle
        # guard never fires and a one-window render runs the stages the
        # inactive mode's session runs minus the settle loop.
        script = render_session.session_script()
        self.assertIn('focus=""; ', script)

    def test_loads_the_focus_settle_before_the_settle_sleep_and_stops_it_after_the_capture(
        self,
    ):
        # The settle loop must start between the client's start and the
        # settle sleep (the re-activation must already run while the
        # windows map) and stop only after the capture status is recorded
        # (Spectacle's startup latency is unbounded under concurrent
        # renders, so the last re-run has to sit between the focused
        # window's map and the frame being read; BUGS.md, the inactive-dialog
        # focus race, 2026-11-13). The stop must precede the client's
        # resume so no re-run can land after the frame was read, and a
        # session without a settle script carries neither the loop nor its
        # stop.
        script = render_session.session_script("/scratch/inactive-dialog-focus-settle.js")
        self.assertIn("focus=/scratch/inactive-dialog-focus-settle.js; ", script)
        self.assertIn("org.kde.kwin.Scripting.loadScript", script)
        self.assertLess(
            script.index("Scripting.loadScript"),
            script.index('sleep "$settle"'),
        )
        self.assertGreater(
            script.index("capture status $status"),
            script.index("Scripting.loadScript"),
        )
        self.assertLess(
            script.index('kill "$settle_loop"'),
            script.index('kill -CONT "$client"'),
        )
        self.assertIn('focus=""; ', render_session.session_script())

    def test_runs_the_focus_settle_loop_until_the_capture_has_returned(self):
        # The inactive-dialog capture must settle the pair's focus state
        # before the frame is read: the session loads the settle script
        # into KWin once and re-runs it in a bounded loop, so a re-run
        # lands inside the capture window itself, where the newest-window
        # activation race used to catch the left window active (BUGS.md,
        # 2026-11-13). The qdbus6 stub records every invocation, tagged
        # with whether the capture was already in flight; the settle
        # script and the repeated runs must both be recorded, a run must
        # land inside the capture, the sentinel must exist after the
        # session (the loop's stop), and the capture status must survive.
        root = tmp_dir.make_tmp_dir(self)
        apply = root / "plasma-apply-colorscheme"
        apply.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        apply.chmod(0o755)
        calls = root / "qdbus-calls"
        capturing = root / "capturing"
        qdbus = root / "qdbus6"
        qdbus.write_text(
            "#!/bin/sh\n"
            f'log="{calls}"\n'
            'case "$*" in\n'
            "  *loadScript*) echo 0; printf 'loadScript\\n' >> \"$log\";;\n"
            "  *Script0*)\n"
            f'    if [ -e "{capturing}" ]; then phase=run-during-the-capture; '
            'else phase=run-before-the-capture; fi\n'
            '    printf "%s\\n" "$phase" >> "$log";;\n'
            "esac\n",
            encoding="utf-8",
        )
        qdbus.chmod(0o755)
        ready = root / "ready"
        client = root / "client.py"
        client.write_text(
            "import sys, time\n"
            "from pathlib import Path\n"
            "Path(sys.argv[1]).touch()\n"
            "time.sleep(30)\n",
            encoding="utf-8",
        )
        settle_script = root / "inactive-dialog-focus-settle.js"
        settle_script.write_text("// stub\n", encoding="utf-8")
        poll = (
            "import time, sys; from pathlib import Path; "
            "deadline = time.monotonic() + 3\n"
            "while not Path(sys.argv[1]).exists():\n"
            "    if time.monotonic() > deadline: sys.exit(1)\n"
            "    time.sleep(0.01)\n"
        )
        # The settle's `sleep 0` polls until the client has started; the
        # spectacle stub marks the capture window and holds it for 0.6s,
        # long enough for the 0.25s settle loop to re-run inside it.
        prefix = (
            f'sleep() {{ if [ "$1" = 0 ]; then '
            f"{shlex.join([sys.executable, '-c', poll, str(ready)])}; "
            'else command sleep "$@"; fi; }; '
            f'spectacle() {{ touch "{capturing}"; command sleep 0.6; return 0; }}; '
        )
        status = render_workflow.run_logged(
            ["sh", "-c", prefix + render_session.session_script(str(settle_script)),
             "sh", "0", str(root / "capture.png"), sys.executable,
             str(client), str(ready)],
            dict(os.environ, PATH=f"{root}:{os.environ['PATH']}"),
            root / "session.log", 10, root,
        )
        self.assertEqual(0, status)
        recorded = calls.read_text(encoding="utf-8").splitlines()
        self.assertIn("loadScript", recorded)
        self.assertIn("run-during-the-capture", recorded)
        self.assertTrue(
            Path(f"{settle_script}.done").exists(),
            "the focus settle loop was never stopped after the capture",
        )


if __name__ == "__main__":
    unittest.main()
