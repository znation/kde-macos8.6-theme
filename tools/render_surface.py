"""Render a themed Plasma surface headlessly and capture it as a PNG.

Starts a virtual KWin Wayland session with no display server, applies the
Mac OS 8.6 theme inside it, opens one Plasma applet window and screenshots the
output, producing the candidate image ``tools/fidelity.py`` compares against a
reference screenshot.

Everything runs against a throwaway scratch root: ``make install`` targets its
``data/`` directory, and the window decoration and desktop theme keys that the
global theme's ``contents/defaults`` names are written to its ``cfg/``. The
user's real configuration and session are never touched, and the scratch root
is removed afterwards.

Usage::

    python3 tools/render_surface.py OUTPUT [--applet ID] [--width W]
        [--height H] [--settle SECONDS] [--timeout SECONDS]
        [--checkbox-dialog | --combobox-dialog | --color-dialog
        | --icon-dialog | --lineedit-dialog | --menu-dialog
        | --radiolist-dialog
        | --calendar-dialog | --progressbar-dialog | --slider-dialog
        | --textbox-dialog | --gtk-dialog]

Exit status: 0 when OUTPUT was written, 1 when the render or capture failed,
2 for a usage error, an unwritable OUTPUT, a missing external tool, a command
this tool starts directly (``make`` or ``dbus-run-session``) that cannot be
started, or a scratch session directory that cannot be created, and 128 plus
the signal number when a SIGTERM or SIGHUP ends the run.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from pathlib import Path

if __package__:
    from tools.argument_parsing import (
        EscapingArgumentParser,
        plain_number,
        positive_int,
    )
    from tools.diagnostics import report_error, report_missing_tool
    from tools.process_group import exit_on_termination
    from tools.render_dialogs import DIALOG_MODES
    from tools.render_output import output_problem
    from tools.render_workflow import render
else:  # run directly: python3 tools/render_surface.py
    from argument_parsing import (
        EscapingArgumentParser,
        plain_number,
        positive_int,
    )
    from diagnostics import report_error, report_missing_tool
    from process_group import exit_on_termination
    from render_dialogs import DIALOG_MODES
    from render_output import output_problem
    from render_workflow import render

TOOL = "render_surface"
REQUIRED_TOOLS = (
    "make",
    "dbus-run-session",
    "kwin_wayland",
    "plasma-apply-colorscheme",
    "plasmawindowed",
    "spectacle",
)
# The default applet, which the dialog modes refuse to combine with.
_DEFAULT_APPLET = "org.kde.plasma.calculator"
# The dialog capture's size, the size the widget gate byte-compares.
_DIALOG_CAPTURE = (480, 360)


def _seconds(option: str, minimum: float) -> Callable[[str], float]:
    """Return a parser for *option*, a finite value of at least *minimum* seconds."""
    def parse(value: str) -> float:
        number = plain_number(value, option, "number", "a", float)
        # `not number >= minimum` also rejects NaN.
        if not number >= minimum or number == float("inf"):
            raise argparse.ArgumentTypeError(
                f"{option} must be a finite number of seconds, "
                f"at least {minimum:g}: {value!r}"
            )
        return number

    return parse


def _applet(value: str) -> str:
    """Accept a plasmoid id argument value, refusing empty, option-like or
    NUL-carrying text."""
    if not value or value.startswith("-") or "\0" in value:
        raise argparse.ArgumentTypeError(
            f"--applet must be a plasmoid id without NUL, not empty or option-like: {value!r}"
        )
    return value


def main(argv: list[str] | None = None) -> int:
    """Run the render CLI; *argv* is the argument list without a program name."""
    parser = EscapingArgumentParser(
        prog="render_surface",
        description=(
            "Render a themed Plasma applet window in a headless KWin session "
            "and write a screenshot PNG."
        ),
        epilog=(
            "exit status: 0 when OUTPUT was written, 1 when the render or "
            "capture failed, 2 usage error, unwritable OUTPUT, missing external "
            "tool, an unstartable make or dbus-run-session, or a scratch "
            "session directory that cannot be created, and 128 plus the signal "
            "number when a SIGTERM or SIGHUP ends the run"
        ),
    )
    parser.add_argument("output", help="PNG file to write")
    parser.add_argument(
        "--applet",
        type=_applet,
        default=_DEFAULT_APPLET,
        help=f"plasmoid id to open (default {_DEFAULT_APPLET})",
    )
    for mode in DIALOG_MODES:
        parser.add_argument(mode.flag, action="store_true", help=mode.help)
    parser.add_argument(
        "--width",
        type=positive_int("--width"),
        default=None,
        help="output width in pixels (default 320, or 480 with a --*-dialog)",
    )
    parser.add_argument(
        "--height",
        type=positive_int("--height"),
        default=None,
        help="output height in pixels (default 240, or 360 with a --*-dialog)",
    )
    parser.add_argument(
        "--settle",
        type=_seconds("--settle", 0.0),
        default=8.0,
        help="seconds to wait for the window to paint before capturing (default 8)",
    )
    parser.add_argument(
        "--timeout",
        type=_seconds("--timeout", 1.0),
        default=90.0,
        help=(
            "seconds before the render session is killed (default 90); must "
            "be longer than --settle"
        ),
    )
    args = parser.parse_args(argv)
    dialog_flags = [
        mode.flag for mode in DIALOG_MODES if getattr(args, mode.attr)
    ]
    if len(dialog_flags) > 1:
        parser.error(
            "the dialog modes open one dialog client each: give one of "
            f"{', '.join(dialog_flags)}, not more than one"
        )
    if dialog_flags:
        flag = dialog_flags[0]
        if args.applet != _DEFAULT_APPLET:
            parser.error(
                f"{flag} opens its own dialog client: do not combine it "
                "with --applet"
            )
        if args.width is not None or args.height is not None:
            parser.error(
                f"{flag} captures at 480x360, the size the widget gate "
                "byte-compares: do not combine it with --width/--height"
            )
        args.width, args.height = _DIALOG_CAPTURE
    else:
        if args.width is None:
            args.width = 320
        if args.height is None:
            args.height = 240
    if args.timeout <= args.settle:
        # The session sleeps for --settle before it asks for the capture, so a
        # timeout at or below it always kills the session first: the run would
        # wait out the whole timeout and report "render timed out" without
        # naming the option that cannot work.
        parser.error(
            f"--timeout ({args.timeout:g}s) must be longer than --settle "
            f"({args.settle:g}s): the session must survive the settle before "
            "it can capture"
        )

    # Each dialog flag requires its own client by name, so the first missing
    # tool the diagnostic names is the client the requested mode opens.
    dialog_clients: tuple[str, ...] = ()
    for mode in DIALOG_MODES:
        if getattr(args, mode.attr) and mode.client_tool not in dialog_clients:
            dialog_clients += (mode.client_tool,)
    requirements = REQUIRED_TOOLS + dialog_clients
    missing = report_missing_tool(TOOL, requirements)
    if missing is not None:
        return missing
    problem = output_problem(Path(args.output).absolute())
    if problem is not None:
        return report_error(TOOL, f"cannot write {args.output!r}: {problem}")
    with exit_on_termination():
        return render(args)


if __name__ == "__main__":
    sys.exit(main())
