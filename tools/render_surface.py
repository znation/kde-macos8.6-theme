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
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

if __package__:
    from tools.cli import EscapingArgumentParser, plain_number, report_error
    from tools.png import PngError, read_png
    from tools.terminal import escape_controls
else:  # run directly: python3 tools/render_surface.py
    from cli import EscapingArgumentParser, plain_number, report_error
    from png import PngError, read_png
    from terminal import escape_controls

TOOL = "render_surface"
ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = (
    ROOT / "theme" / "look-and-feel" / "org.macos8.desktop" / "contents" / "defaults"
)
REQUIRED_TOOLS = (
    "make",
    "dbus-run-session",
    "kwin_wayland",
    "plasma-apply-colorscheme",
    "plasmawindowed",
    "spectacle",
)
# The config files the global theme's defaults feed that `plasma-apply-colorscheme`
# does not write; the rest of the defaults are applied inside the session.
CONFIG_FILES = ("kwinrc", "plasmarc")
COLOR_SCHEME = "MacOS8"
SOCKET = "render-surface"
INSTALL_TIMEOUT = 60.0

_FILE_GROUP = re.compile(r"\[([^\[\]]+)\]\[([^\[\]]+)\]$")
_ANY_HEADING = re.compile(r"\[[^\]]*\]")
_LOG_TAIL_LINES = 12


def _defaults_groups(path: Path = DEFAULTS) -> dict[tuple[str, str], dict[str, str]]:
    """Return ``{(file, group): {key: value}}`` for the ``[file][group]`` sections.

    The global theme's ``contents/defaults`` names each target config file in
    the first bracket pair (``[kwinrc][org.kde.kdecoration2]``). A plain
    ``[Wallpaper]`` section names no file and is skipped.
    """
    groups: dict[tuple[str, str], dict[str, str]] = {}
    current: dict[str, str] | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if _ANY_HEADING.match(line):
            match = _FILE_GROUP.match(line)
            current = groups.setdefault(match.groups(), {}) if match else None
        elif current is not None and "=" in line:
            key, value = line.split("=", 1)
            current[key.strip()] = value.strip()
    return groups


def _write_configs(config_home: Path) -> None:
    groups = _defaults_groups()
    for name in CONFIG_FILES:
        lines: list[str] = []
        for (file, group), values in groups.items():
            if file != name:
                continue
            lines.append(f"[{group}]")
            lines.extend(f"{key}={value}" for key, value in values.items())
            lines.append("")
        (config_home / name).write_text("\n".join(lines), encoding="utf-8")


def _kill_group(process: subprocess.Popen) -> None:
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except OSError:
        pass


def _run(argv: list[str], env: dict[str, str], log: Path, timeout: float) -> int | None:
    """Run *argv* in its own session logging to *log*; None means it timed out.

    Output goes to a file, not a pipe, so a descendant that outlives the
    child cannot keep the wait open. The whole process group is killed on the
    way out, whatever happened.
    """
    with log.open("wb") as sink:
        process = subprocess.Popen(
            argv,
            cwd=ROOT,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=sink,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            return None
        finally:
            _kill_group(process)
            process.wait()


def _failure(message: str, log: Path | None = None) -> int:
    text = f"{TOOL}: error: {escape_controls(message)}"
    if log is not None and log.is_file():
        tail = log.read_text(encoding="utf-8", errors="replace").splitlines()
        for line in tail[-_LOG_TAIL_LINES:]:
            text += f"\n  {escape_controls(line)}"
    print(text, file=sys.stderr)
    return 1


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

        env = {
            key: value
            for key, value in os.environ.items()
            if key not in ("WAYLAND_DISPLAY", "DISPLAY", "DESTDIR")
        }
        env.update(
            XDG_RUNTIME_DIR=str(runtime),
            XDG_CONFIG_HOME=str(config),
            XDG_DATA_HOME=str(data),
        )

        install_log = scratch / "install.log"
        status = _run(
            ["make", "install", f"XDG_DATA_HOME={data}"],
            env,
            install_log,
            INSTALL_TIMEOUT,
        )
        if status != 0:
            reason = "timed out" if status is None else f"exited {status}"
            return _failure(f"make install {reason}", install_log)

        _write_configs(config)

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
        status = _run(
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
        )
        if status is None:
            return _failure(f"render timed out after {args.timeout:g}s", render_log)
        if status != 0:
            return _failure(f"render session exited {status}", render_log)

        try:
            image = read_png(str(surface))
        except (PngError, OSError) as exc:
            return _failure(f"capture is not a readable PNG: {exc}", render_log)
        if (image.width, image.height) != (args.width, args.height):
            return _failure(
                f"capture is {image.width}x{image.height}, "
                f"expected {args.width}x{args.height}",
                render_log,
            )
        try:
            shutil.copyfile(surface, output)
        except OSError as exc:
            return _failure(f"cannot write {output}: {exc}")
        return 0
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def _positive_int(option: str):
    def parse(value: str) -> int:
        number = plain_number(value, option, "integer", "an", int)
        if number < 1:
            raise argparse.ArgumentTypeError(f"{option} must be at least 1: {value!r}")
        return number

    return parse


def _seconds(option: str, minimum: float):
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
            "capture failed, 2 usage error or missing external tool"
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
        type=_positive_int("--width"),
        default=320,
        help="output width in pixels (default 320)",
    )
    parser.add_argument(
        "--height",
        type=_positive_int("--height"),
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

    for tool in REQUIRED_TOOLS:
        if shutil.which(tool) is None:
            return report_error(TOOL, f"required tool not found on PATH: {tool}")
    return _render(args)


if __name__ == "__main__":
    sys.exit(main())
