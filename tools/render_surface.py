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
2 for a usage error or a missing external tool.
"""

from __future__ import annotations

import argparse
import os
import shlex
import shutil
import sys
import tempfile
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
    from tools.theme_defaults import write_configs
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
    from theme_defaults import write_configs

TOOL = "render_surface"
ROOT = Path(__file__).resolve().parents[1]
REQUIRED_TOOLS = (
    "make",
    "dbus-run-session",
    "kwin_wayland",
    "plasma-apply-colorscheme",
    "plasmawindowed",
    "spectacle",
)
# The config files the global theme's defaults feed that `plasma-apply-colorscheme`
# does not write. The render applies the colour scheme in the session and leaves the
# `[kdeglobals][KDE] widgetStyle` default unapplied.
CONFIG_FILES = ("kwinrc", "plasmarc")
COLOR_SCHEME = "MacOS8"
SOCKET = "render-surface"
INSTALL_TIMEOUT = 60.0


def _session_script() -> str:
    # Positional parameters carry the applet, settle time and output path, so
    # none of them is ever parsed as shell syntax.
    return (
        f"plasma-apply-colorscheme {COLOR_SCHEME} || exit 1; "
        'plasmawindowed "$1" & applet=$!; '
        'sleep "$2"; '
        'spectacle -b -n -f -o "$3"; status=$?; '
        'kill "$applet" 2>/dev/null; '
        "exit $status"
    )


def _output_problem(output: Path) -> str | None:
    """Return why *output* cannot be written, or None when it looks writable."""
    if output.is_dir():
        return "is a directory"
    if not output.parent.is_dir():
        return "its directory does not exist"
    if not os.access(output.parent, os.W_OK | os.X_OK):
        return "its directory is not writable"
    return None


def _publish(source: Path, output: Path) -> None:
    """Copy *source* to *output* so *output* is either the old file or the whole new one.

    The bytes go to a fresh temporary file whose name the OS picks in
    *output*'s directory, then that file is renamed over *output*. A fixed,
    guessable name would let another local user who can write the directory
    park a symlink there first and make the copy overwrite whatever file it
    names.
    """
    descriptor, partial_name = tempfile.mkstemp(
        dir=output.parent, prefix=".render-", suffix=".tmp"
    )
    partial = Path(partial_name)
    try:
        with os.fdopen(descriptor, "wb") as destination:
            # mkstemp opens the file 0600; the plain copy this replaces
            # created it with the process umask applied, so restore that mode
            # and leave the output's permissions unchanged.
            umask = os.umask(0)
            os.umask(umask)
            os.chmod(destination.fileno(), 0o666 & ~umask)
            with source.open("rb") as origin:
                shutil.copyfileobj(origin, destination)
        os.replace(partial, output)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise


def _render(args: argparse.Namespace) -> int:
    output = Path(args.output).absolute()
    scratch = Path(tempfile.mkdtemp(prefix="render-surface-"))
    try:
        runtime = scratch / "rt"
        config = scratch / "cfg"
        data = scratch / "data"
        for directory in (runtime, config, data):
            directory.mkdir()
        runtime.chmod(0o700)
        surface = scratch / "surface.png"

        # DESTDIR must not reach the install: the theme has to land in the
        # scratch data home. It arrives both as an environment variable and,
        # when the caller ran `make DESTDIR=... render`, through MAKEFLAGS,
        # which the child make imports as a command-line override.
        env = {
            key: value
            for key, value in os.environ.items()
            if key not in ("WAYLAND_DISPLAY", "DISPLAY", "DESTDIR", "MAKEFLAGS")
        }
        env.update(
            XDG_RUNTIME_DIR=str(runtime),
            XDG_CONFIG_HOME=str(config),
            XDG_DATA_HOME=str(data),
        )

        install_log = scratch / "install.log"
        status = run_logged(
            ["make", "install", f"XDG_DATA_HOME={data}"],
            env,
            install_log,
            INSTALL_TIMEOUT,
            ROOT,
        )
        if status != 0:
            reason = "timed out" if status is None else f"exited {status}"
            return report_failure(TOOL, f"make install {reason}", install_log)

        write_configs(config, CONFIG_FILES)

        session = shlex.join(
            [
                "sh",
                "-c",
                _session_script(),
                "sh",
                args.applet,
                str(args.settle),
                str(surface),
            ]
        )
        render_log = scratch / "render.log"
        status = run_logged(
            [
                "dbus-run-session",
                "--",
                "kwin_wayland",
                "--virtual",
                "--no-lockscreen",
                "--width",
                str(args.width),
                "--height",
                str(args.height),
                "--socket",
                SOCKET,
                "--exit-with-session",
                session,
            ],
            env,
            render_log,
            args.timeout,
            ROOT,
        )
        if status is None:
            return report_failure(
                TOOL, f"render timed out after {args.timeout:g}s", render_log
            )
        if status != 0:
            return report_failure(TOOL, f"render session exited {status}", render_log)

        try:
            image = read_png(str(surface))
        except (PngError, OSError) as exc:
            return report_failure(
                TOOL, f"capture is not a readable PNG: {exc}", render_log
            )
        if (image.width, image.height) != (args.width, args.height):
            return report_failure(
                TOOL,
                f"capture is {image.width}x{image.height}, "
                f"expected {args.width}x{args.height}",
                render_log,
            )
        try:
            _publish(surface, output)
        except OSError as exc:
            return report_failure(TOOL, f"cannot write {output}: {exc}")
        return 0
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


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
            "capture failed, 2 usage error, unwritable OUTPUT or missing external tool"
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
        help="seconds before the render session is killed (default 90)",
    )
    args = parser.parse_args(argv)

    missing = report_missing_tool(TOOL, REQUIRED_TOOLS)
    if missing is not None:
        return missing
    problem = _output_problem(Path(args.output).absolute())
    if problem is not None:
        return report_error(TOOL, f"cannot write {args.output!r}: {problem}")
    with exit_on_termination():
        return _render(args)


if __name__ == "__main__":
    sys.exit(main())
