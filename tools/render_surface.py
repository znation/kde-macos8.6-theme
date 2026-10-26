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

Exit status: 0 when OUTPUT was written, 1 when the render or capture failed,
2 for a usage error, an unwritable OUTPUT, a missing external tool, or a
command this tool starts directly (``make`` or ``dbus-run-session``) that
cannot be started, and 128 plus the signal number when a SIGTERM or SIGHUP
ends the run.
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
        install_theme,
        session_command,
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
        install_theme,
        session_command,
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


def _capture_is_unpainted(rgb: bytes) -> bool:
    """Return whether a capture's RGB plane is entirely black.

    A KWin virtual session that has not painted yet presents an all-black
    screen, so spectacle captures a correctly sized but empty surface. Such a
    capture is a render of nothing; refusing it here turns an early capture
    into one diagnostic naming the settle wait instead of a published PNG that
    later fails pixel comparisons for no visible reason.
    """
    return not any(rgb)


def _render(args: argparse.Namespace) -> int:
    output = Path(args.output).absolute()
    with Session.create() as session:
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

        try:
            write_session_configs(session)
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            return report_failure(
                TOOL, f"cannot write the session config: {exc}"
            )

        command = session_command(
            session,
            args.applet,
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
            "tool, or an unstartable make or dbus-run-session, and 128 plus the "
            "signal number when a SIGTERM or SIGHUP ends the run"
        ),
    )
    parser.add_argument("output", help="PNG file to write")
    parser.add_argument(
        "--applet",
        type=_applet,
        default="org.kde.plasma.calculator",
        help="plasmoid id to open (default org.kde.plasma.calculator)",
    )
    parser.add_argument(
        "--width",
        type=positive_int("--width"),
        default=320,
        help="output width in pixels (default 320)",
    )
    parser.add_argument(
        "--height",
        type=positive_int("--height"),
        default=240,
        help="output height in pixels (default 240)",
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

    missing = report_missing_tool(TOOL, REQUIRED_TOOLS)
    if missing is not None:
        return missing
    problem = output_problem(Path(args.output).absolute())
    if problem is not None:
        return report_error(TOOL, f"cannot write {args.output!r}: {problem}")
    with exit_on_termination():
        return _render(args)


if __name__ == "__main__":
    sys.exit(main())
