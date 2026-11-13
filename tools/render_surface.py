"""Render a themed Plasma surface headlessly and capture it as a PNG.

Starts a virtual KWin Wayland session with no display server, applies the
Mac OS 8.6 theme inside it, opens the selected mode's client (a Plasma applet
window, a dialog, the shell that draws the menu bar, or the startup splash)
and screenshots the
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
        | --icon-dialog | --inactive-dialog | --lineedit-dialog
        | --menu-dialog | --radiolist-dialog
        | --calendar-dialog | --progressbar-dialog | --slider-dialog
        | --textbox-dialog | --gtk-dialog | --file-dialog]
        [--desktop] [--splash]

Exit status: 0 when OUTPUT was written, 1 when the render or capture failed,
2 for a usage error, an unwritable OUTPUT, a missing external tool, a missing
applet package, a command
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
    from tools.render_applet import applet_problem
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
    from render_applet import applet_problem
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
# The desktop capture's size: the probe's virtual-framebuffer size, and the
# crop basis the queued desktop gate will compare.
_DESKTOP_CAPTURE = (640, 400)
# The splash capture's size: the same probe framebuffer the desktop capture
# fixes, and the crop basis the queued splash gate will compare.
_SPLASH_CAPTURE = (640, 400)
# The desktop session's paint budget: plasmashell's first start imports the
# look-and-feel layout, which the probe painted by a 20 s settle.
_DESKTOP_SETTLE = 30.0
_DESKTOP_TIMEOUT = 180.0
# The splash session's paint budget. The --test --nofork client paints
# within an 8 s settle (three probe runs) but deterministically exits about
# 10 s in (upstream's seven 2 s stages), so the splash keeps the applet's
# 8 s / 90 s defaults; a longer settle would capture an already-vanished
# splash.
_SPLASH_SETTLE = 8.0
_SPLASH_TIMEOUT = 90.0


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
    """Accept a plasmoid id argument value, refusing empty, option-like,
    path-carrying or NUL-carrying text."""
    if not value:
        raise argparse.ArgumentTypeError("--applet must be a plasmoid id, not empty")
    if value.startswith("-"):
        raise argparse.ArgumentTypeError(
            f"--applet must be a plasmoid id, not option-like: {value!r}"
        )
    if "\0" in value:
        raise argparse.ArgumentTypeError(
            f"--applet must be a plasmoid id without NUL: {value!r}"
        )
    if "/" in value or "\\" in value:
        raise argparse.ArgumentTypeError(
            f"--applet must be a plasmoid id, not a path: {value!r}"
        )
    return value


def _refuse_mode_overrides(
    parser: EscapingArgumentParser,
    args: argparse.Namespace,
    label: str,
    applet_clause: str,
    size_clause: str,
    capture: tuple[int, int],
) -> None:
    """Refuse --applet and a custom size, then fix the capture size.

    The dialog, desktop and splash modes each open their own client at a
    fixed capture size, so the three share this refusal shape: an --applet
    override has no window to open the client in, and a --width/--height
    override moves the capture the pinned gate crops assume. The messages
    differ only in the mode *label* and the two reason clauses the caller
    passes; three call sites, one per mode.
    """
    if args.applet != _DEFAULT_APPLET:
        parser.error(
            f"{label} {applet_clause}: do not combine it with --applet"
        )
    if args.width is not None or args.height is not None:
        parser.error(
            f"{label} {size_clause}: do not combine it with --width/--height"
        )
    args.width, args.height = capture


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
            "tool, missing applet package, an unstartable make or "
            "dbus-run-session, or a scratch "
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
        "--desktop",
        action="store_true",
        help=(
            "capture the themed plasmashell menu bar (the 20px top panel the "
            "look-and-feel layout builds) at the fixed 640x400 desktop size"
        ),
    )
    parser.add_argument(
        "--splash",
        action="store_true",
        help=(
            "capture the look-and-feel's own themed startup splash "
            "(ksplashqml) at the fixed 640x400 splash size"
        ),
    )
    parser.add_argument(
        "--width",
        type=positive_int("--width"),
        default=None,
        help=(
            "output width in pixels (default 320, or 480 with a --*-dialog, "
            "or 640 with --desktop or --splash)"
        ),
    )
    parser.add_argument(
        "--height",
        type=positive_int("--height"),
        default=None,
        help=(
            "output height in pixels (default 240, or 360 with a --*-dialog, "
            "or 400 with --desktop or --splash)"
        ),
    )
    parser.add_argument(
        "--settle",
        type=_seconds("--settle", 0.0),
        default=None,
        help="seconds to wait for the window to paint before capturing "
        "(default 8, or 30 with --desktop or --splash)",
    )
    parser.add_argument(
        "--timeout",
        type=_seconds("--timeout", 1.0),
        default=None,
        help=(
            "seconds before the render session is killed (default 90, or 180 "
            "with --desktop or --splash); must be longer than --settle"
        ),
    )
    args = parser.parse_args(argv)
    # The settle and timeout defaults differ per mode, so the parser leaves
    # them unset and the mode choice fills them in; an explicit flag wins.
    if args.settle is None:
        args.settle = (
            _DESKTOP_SETTLE if args.desktop
            else _SPLASH_SETTLE if args.splash
            else 8.0
        )
    if args.timeout is None:
        args.timeout = (
            _DESKTOP_TIMEOUT if args.desktop
            else _SPLASH_TIMEOUT if args.splash
            else 90.0
        )
    dialog_flags = [
        mode.flag for mode in DIALOG_MODES if getattr(args, mode.attr)
    ]
    if len(dialog_flags) > 1:
        parser.error(
            "the dialog modes open one dialog client each: give one of "
            f"{', '.join(dialog_flags)}, not more than one"
        )
    if args.desktop and dialog_flags:
        parser.error(
            "--desktop captures the shell's own menu bar: do not combine it "
            f"with {dialog_flags[0]}"
        )
    if args.splash and (args.desktop or dialog_flags):
        partner = "--desktop" if args.desktop else dialog_flags[0]
        parser.error(
            "--splash renders the look-and-feel's own splash: do not combine "
            f"it with {partner}"
        )
    if dialog_flags:
        _refuse_mode_overrides(
            parser,
            args,
            dialog_flags[0],
            "opens its own dialog client",
            "captures at 480x360, the size the widget gate byte-compares",
            _DIALOG_CAPTURE,
        )
    elif args.desktop:
        _refuse_mode_overrides(
            parser,
            args,
            "--desktop",
            "captures the shell's own menu bar, not an applet window",
            "captures at 640x400, the menu-bar panel size the queued "
            "desktop gate crops",
            _DESKTOP_CAPTURE,
        )
    elif args.splash:
        _refuse_mode_overrides(
            parser,
            args,
            "--splash",
            "opens the splash client, not an applet window",
            "captures at 640x400, the probe framebuffer size the later "
            "splash gate crops",
            _SPLASH_CAPTURE,
        )
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
    if args.splash:
        # The splash client is a plain command, so it joins the tool check.
        requirements = REQUIRED_TOOLS + ("ksplashqml",)
    elif args.desktop:
        # The desktop client is a plain command, so it joins the tool check.
        requirements = REQUIRED_TOOLS + ("plasmashell",)
    else:
        requirements = REQUIRED_TOOLS + dialog_clients
    missing = report_missing_tool(TOOL, requirements)
    if missing is not None:
        return missing
    if not dialog_flags and not args.desktop and not args.splash:
        # An applet package is not a command, so report_missing_tool cannot
        # see its absence: the default calculator render would otherwise
        # waste a full scratch session on a capture that never paints and
        # times out. The dialog modes and the desktop capture open their own
        # clients and never touch the applet, so they skip this check.
        applet = applet_problem(args.applet)
        if applet is not None:
            return report_error(TOOL, applet)
    problem = output_problem(Path(args.output).absolute())
    if problem is not None:
        return report_error(TOOL, f"cannot write {args.output!r}: {problem}")
    with exit_on_termination():
        return render(args)


if __name__ == "__main__":
    sys.exit(main())
