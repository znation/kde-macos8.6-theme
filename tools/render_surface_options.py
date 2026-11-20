"""Argument parsing and mode policy for the headless render CLI."""

from __future__ import annotations

import argparse
from collections.abc import Callable

if __package__:
    from tools.argument_parsing import EscapingArgumentParser, plain_number, positive_int
    from tools.render_dialogs import DIALOG_MODES
else:  # imported by a directly run render_surface.py
    from argument_parsing import EscapingArgumentParser, plain_number, positive_int
    from render_dialogs import DIALOG_MODES

REQUIRED_TOOLS = (
    "make", "dbus-run-session", "kwin_wayland", "plasma-apply-colorscheme",
    "plasmawindowed", "spectacle",
)
_DEFAULT_APPLET = "org.kde.plasma.calculator"
_DIALOG_CAPTURE = (480, 360)
_DESKTOP_CAPTURE = (640, 400)
_SPLASH_CAPTURE = (640, 400)
_DESKTOP_SETTLE = 30.0
_DESKTOP_TIMEOUT = 180.0
_SPLASH_SETTLE = 8.0
_SPLASH_TIMEOUT = 90.0


def _seconds(option: str, minimum: float) -> Callable[[str], float]:
    """Return a parser for *option*, a finite value of at least *minimum* seconds."""
    def parse(value: str) -> float:
        number = plain_number(value, option, "number", "a", float)
        if not number >= minimum or number == float("inf"):
            raise argparse.ArgumentTypeError(
                f"{option} must be a finite number of seconds, "
                f"at least {minimum:g}: {value!r}"
            )
        return number
    return parse


def _applet(value: str) -> str:
    """Accept a plasmoid id, refusing empty, option-like, path or NUL text."""
    if not value:
        raise argparse.ArgumentTypeError("--applet must be a plasmoid id, not empty")
    if value.startswith("-"):
        raise argparse.ArgumentTypeError(
            f"--applet must be a plasmoid id, not option-like: {value!r}"
        )
    if "\0" in value:
        raise argparse.ArgumentTypeError(f"--applet must be a plasmoid id without NUL: {value!r}")
    if "/" in value or "\\" in value:
        raise argparse.ArgumentTypeError(f"--applet must be a plasmoid id, not a path: {value!r}")
    return value


def _refuse_mode_overrides(parser, args, label, applet_clause, size_clause, capture):
    if args.applet != _DEFAULT_APPLET:
        parser.error(f"{label} {applet_clause}: do not combine it with --applet")
    if args.width is not None or args.height is not None:
        parser.error(f"{label} {size_clause}: do not combine it with --width/--height")
    args.width, args.height = capture


def parse_options(argv: list[str] | None = None) -> tuple[argparse.Namespace, tuple[str, ...]]:
    """Parse and validate CLI options, returning the namespace and required tools."""
    parser = EscapingArgumentParser(
        prog="render_surface",
        description=("Render a themed Plasma applet window in a headless KWin session "
                     "and write a screenshot PNG."),
        epilog=("exit status: 0 when OUTPUT was written, 1 when the render or capture failed, "
                "2 usage error, unwritable OUTPUT, missing external tool, missing applet package, "
                "an unstartable make or dbus-run-session, or a scratch session directory that "
                "cannot be created, and 128 plus the signal number when a SIGTERM or SIGHUP ends the run"),
    )
    parser.add_argument("output", help="PNG file to write")
    parser.add_argument("--applet", type=_applet, default=_DEFAULT_APPLET,
                        help=f"plasmoid id to open (default {_DEFAULT_APPLET})")
    for mode in DIALOG_MODES:
        parser.add_argument(mode.flag, action="store_true", help=mode.help)
    parser.add_argument("--desktop", action="store_true", help=(
        "capture the themed plasmashell menu bar (the 20px top panel the "
        "look-and-feel layout builds) at the fixed 640x400 desktop size"))
    parser.add_argument("--splash", action="store_true", help=(
        "capture the look-and-feel's own themed startup splash (ksplashqml) "
        "at the fixed 640x400 splash size"))
    parser.add_argument("--width", type=positive_int("--width"), default=None,
                        help="output width in pixels (default 320, or 480 with a --*-dialog, or 640 with --desktop or --splash)")
    parser.add_argument("--height", type=positive_int("--height"), default=None,
                        help="output height in pixels (default 240, or 360 with a --*-dialog, or 400 with --desktop or --splash)")
    parser.add_argument("--settle", type=_seconds("--settle", 0.0), default=None,
                        help="seconds to wait for the window to paint before capturing (default 8, or 30 with --desktop or --splash)")
    parser.add_argument("--timeout", type=_seconds("--timeout", 1.0), default=None,
                        help="seconds before the render session is killed (default 90, or 180 with --desktop or --splash); must be longer than --settle")
    args = parser.parse_args(argv)
    if args.settle is None:
        args.settle = _DESKTOP_SETTLE if args.desktop else _SPLASH_SETTLE if args.splash else 8.0
    if args.timeout is None:
        args.timeout = _DESKTOP_TIMEOUT if args.desktop else _SPLASH_TIMEOUT if args.splash else 90.0
    dialog_flags = [mode.flag for mode in DIALOG_MODES if getattr(args, mode.attr)]
    if len(dialog_flags) > 1:
        parser.error("the dialog modes open one dialog client each: give one of "
                     f"{', '.join(dialog_flags)}, not more than one")
    if args.desktop and dialog_flags:
        parser.error("--desktop captures the shell's own menu bar: do not combine it with "
                     f"{dialog_flags[0]}")
    if args.splash and (args.desktop or dialog_flags):
        partner = "--desktop" if args.desktop else dialog_flags[0]
        parser.error("--splash renders the look-and-feel's own splash: do not combine "
                     f"it with {partner}")
    if dialog_flags:
        _refuse_mode_overrides(parser, args, dialog_flags[0], "opens its own dialog client",
                               "captures at 480x360, the size the widget gate byte-compares", _DIALOG_CAPTURE)
    elif args.desktop:
        _refuse_mode_overrides(parser, args, "--desktop", "captures the shell's own menu bar, not an applet window",
                               "captures at 640x400, the menu-bar panel size the queued desktop gate crops", _DESKTOP_CAPTURE)
    elif args.splash:
        _refuse_mode_overrides(parser, args, "--splash", "opens the splash client, not an applet window",
                               "captures at 640x400, the probe framebuffer size the later splash gate crops", _SPLASH_CAPTURE)
    else:
        args.width = 320 if args.width is None else args.width
        args.height = 240 if args.height is None else args.height
    if args.timeout <= args.settle:
        parser.error(f"--timeout ({args.timeout:g}s) must be longer than --settle "
                     f"({args.settle:g}s): the session must survive the settle before it can capture")
    clients = tuple(dict.fromkeys(mode.client_tool for mode in DIALOG_MODES
                                  if getattr(args, mode.attr)))
    if args.splash:
        requirements = REQUIRED_TOOLS + ("ksplashqml",)
    elif args.desktop:
        requirements = REQUIRED_TOOLS + ("plasmashell",)
    else:
        requirements = REQUIRED_TOOLS + clients
    return args, requirements
