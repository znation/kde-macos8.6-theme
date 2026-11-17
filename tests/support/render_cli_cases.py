"""Shared ``render_surface.main`` argument assertions for the per-mode CLI tests.

The render CLI's per-mode argument tests in ``tests/test_render_surface_units.py``
and ``tests/test_render_fixed_client_modes.py`` call these helpers to pin what
``main`` delegates, which flags it refuses together, and which tool it names
when one is missing. They start no session.
"""

from __future__ import annotations

from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.cli_fixtures import _call_capturing, assert_missing_tool_named, call_main  # noqa: E402
from tools import render_surface  # noqa: E402


def delegated_render_args(case, argv, status=0):
    """Patch the render collaborators away, run *argv*, return the mode args.

    Six tests and ``assert_delegated_capture_size`` call this: with the missing-tool preflight, the
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
