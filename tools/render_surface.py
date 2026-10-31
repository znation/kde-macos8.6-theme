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
        [--checkbox-dialog | --combobox-dialog]

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
    from tools.diagnostics import (
        report_error,
        report_failure,
        report_missing_tool,
    )
    from tools.png import PngError, read_png
    from tools.process_group import exit_on_termination, run_logged
    from tools.render_output import output_problem, publish
    from tools.render_session import (
        Session,
        CONFIG_FILES,
        checkbox_dialog_client,
        combobox_dialog_client,
        install_theme,
        link_kvantum_themes,
        session_command,
        write_kvantum_selection,
        write_session_configs,
    )
    from tools.repo_root import ROOT
else:  # run directly: python3 tools/render_surface.py
    from argument_parsing import (
        EscapingArgumentParser,
        plain_number,
        positive_int,
    )
    from diagnostics import (
        report_error,
        report_failure,
        report_missing_tool,
    )
    from png import PngError, read_png
    from process_group import exit_on_termination, run_logged
    from render_output import output_problem, publish
    from render_session import (
        Session,
        CONFIG_FILES,
        checkbox_dialog_client,
        combobox_dialog_client,
        install_theme,
        link_kvantum_themes,
        session_command,
        write_kvantum_selection,
        write_session_configs,
    )
    from repo_root import ROOT

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


def _capture_is_unpainted(rgb: bytes) -> bool:
    """Return whether a capture's RGB plane is entirely black.

    A KWin virtual session that has not painted yet presents an all-black
    screen, so spectacle captures a correctly sized but empty surface. Such a
    capture is a render of nothing; refusing it here turns an early capture
    into one diagnostic naming the settle wait instead of a published PNG that
    later fails pixel comparisons for no visible reason.
    """
    return not any(rgb)


def _dialog_config_files() -> tuple[str, ...]:
    """Config files the dialog render applies, unlike the applet render.

    Plasma applets draw through the desktop theme, so the applet render
    leaves the ``[kdeglobals] [KDE] widgetStyle`` default unapplied. A
    ``kdialog`` client draws through the widget style, so the dialog render
    applies the ``kdeglobals`` section of the global theme's defaults too.
    """
    return CONFIG_FILES + ("kdeglobals",)


def _render(args: argparse.Namespace) -> int:
    output = Path(args.output).absolute()
    try:
        session = Session.create()
    except OSError as exc:
        # Creating the scratch session can fail before it has anything to
        # clean up (a full or unwritable TMPDIR). Report it as this tool's own
        # diagnostic instead of letting the OSError escape as a traceback.
        return report_error(
            TOOL, f"cannot create a scratch session directory: {exc}"
        )
    with session:
        try:
            status, install_log = install_theme(session)
        except OSError as exc:
            # `make` was found on PATH but cannot be started (a corrupt or
            # unexecutable binary); report it as this tool's own diagnostic
            # rather than letting the OSError escape as a traceback.
            return report_error(TOOL, f"cannot run make: {exc}")
        if status != 0:
            reason = "timed out" if status is None else f"exited {status}"
            return report_failure(TOOL, f"make install {reason}", install_log)

        problem, path = link_kvantum_themes(session)
        if problem is not None:
            return report_error(
                TOOL, f"cannot link {path}: {problem}"
            )

        dialog = args.checkbox_dialog or args.combobox_dialog
        try:
            write_session_configs(
                session, files=_dialog_config_files() if dialog else CONFIG_FILES
            )
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            return report_failure(
                TOOL, f"cannot write the session config: {exc}"
            )

        if args.checkbox_dialog:
            client = list(checkbox_dialog_client(session))
        elif args.combobox_dialog:
            client = list(combobox_dialog_client(session))
        else:
            client = ["plasmawindowed", args.applet]
        if dialog:
            try:
                write_kvantum_selection(session)
            except OSError as exc:
                return report_failure(
                    TOOL, f"cannot write the Kvantum selection: {exc}"
                )

        command = session_command(
            session,
            client,
            args.settle,
            args.width,
            args.height,
            args.timeout,
        )
        try:
            status = run_logged(
                command.argv,
                session.environment,
                command.log,
                command.timeout,
                ROOT,
            )
        except OSError as exc:
            return report_error(TOOL, f"cannot run dbus-run-session: {exc}")
        if status is None:
            return report_failure(
                TOOL, f"render timed out after {args.timeout:g}s", command.log
            )
        if status != 0:
            return report_failure(TOOL, f"render session exited {status}", command.log)

        try:
            image = read_png(str(session.surface))
        except (PngError, OSError) as exc:
            return report_failure(
                TOOL, f"capture is not a readable PNG: {exc}", command.log
            )
        if (image.width, image.height) != (args.width, args.height):
            return report_failure(
                TOOL,
                f"capture is {image.width}x{image.height}, "
                f"expected {args.width}x{args.height}",
                command.log,
            )
        if _capture_is_unpainted(image.rgb):
            return report_failure(
                TOOL,
                "capture is entirely black: the window did not paint before "
                f"the {args.settle:g}s settle; retry with a longer --settle",
                command.log,
            )
        try:
            publish(session.surface, output)
        except OSError as exc:
            return report_failure(TOOL, f"cannot write {output}: {exc}")
        return 0


def _seconds(option: str, minimum: float) -> Callable[[str], float]:
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
    if not value or value.startswith("-"):
        raise argparse.ArgumentTypeError(
            f"--applet must be a plasmoid id, not empty or option-like: {value!r}"
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
    parser.add_argument(
        "--checkbox-dialog",
        action="store_true",
        help=(
            "open a KDialog warning box whose dontagain check box the Kvantum "
            "engine draws with the theme's checkbox art, and capture it at "
            "the 480x360 size the widget gate byte-compares"
        ),
    )
    parser.add_argument(
        "--combobox-dialog",
        action="store_true",
        help=(
            "open a KDialog chooser whose combo box the Kvantum engine draws "
            "with the theme's comboarrow art, and capture it at the 480x360 "
            "size the widget gate byte-compares"
        ),
    )
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
        flag
        for flag, given in (
            ("--checkbox-dialog", args.checkbox_dialog),
            ("--combobox-dialog", args.combobox_dialog),
        )
        if given
    ]
    if len(dialog_flags) > 1:
        parser.error(
            "the dialog modes open one kdialog client each: give one of "
            f"{', '.join(dialog_flags)}, not both"
        )
    if dialog_flags:
        flag = dialog_flags[0]
        if args.applet != _DEFAULT_APPLET:
            parser.error(
                f"{flag} opens its own kdialog client: do not combine it "
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

    requirements = REQUIRED_TOOLS + (
        ("kdialog",) if args.checkbox_dialog or args.combobox_dialog else ()
    )
    missing = report_missing_tool(TOOL, requirements)
    if missing is not None:
        return missing
    problem = output_problem(Path(args.output).absolute())
    if problem is not None:
        return report_error(TOOL, f"cannot write {args.output!r}: {problem}")
    with exit_on_termination():
        return _render(args)


if __name__ == "__main__":
    sys.exit(main())
