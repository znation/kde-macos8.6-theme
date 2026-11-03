"""Swap the left Control and Alt keys at the XKB level for this user.

``make apply`` runs this after the theme is applied. The reference places its
shortcut modifier -- the Command key -- where a PC keyboard puts Alt, while
KDE applications implement Cut, Copy, Paste and the rest with Control. The XKB
option ``ctrl:swap_lalt_lctl`` makes the physical left Alt produce Control and
the physical left Control produce Alt for every client in the session, so the
reference's shortcuts use the key in the Command position without rebinding
each application. Only the left pair is swapped; right Alt (AltGr) keeps
producing the characters it always did.

The setting is per user: it is written to ``kxkbrc`` under the same key and
group the Keyboard KCM writes, so other logged-in users, virtual terminals and
the display manager keep their own keymaps. The write preserves every other
XKB option the user configured, sets ``ResetOldOptions`` (KWin on Wayland
applies ``[Layout] Options`` only when that key is true), and emits
``org.kde.keyboard /Layouts reloadConfig`` so KWin rebuilds the keymap without
a logout. The reload is best effort: a missing signal tool, or one that fails,
only prints a note saying the swap takes effect at the next login.

Usage::

    python3 tools/apply_keymap.py

Exit status: 0 when the option was written (even if the session could not be
asked to reload it), 1 when a required command failed, 2 for a usage error, a
missing external tool, one that cannot be started, a scratch directory that
cannot be created, or a configuration value that cannot be read, and 128 plus
the signal number when a SIGTERM or SIGHUP ends the run.
"""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
from pathlib import Path

if __package__:
    from tools.argument_parsing import EscapingArgumentParser
    from tools.diagnostics import (
        create_scratch_directory,
        report_error,
        report_failure,
        report_missing_tool,
        report_note,
    )
    from tools.process_group import exit_on_termination, run_logged
    from tools.repo_root import ROOT
    from tools.required_command import run_required
    from tools.session_bus import session_env
else:  # run directly: python3 tools/apply_keymap.py
    from argument_parsing import EscapingArgumentParser
    from diagnostics import (
        create_scratch_directory,
        report_error,
        report_failure,
        report_missing_tool,
        report_note,
    )
    from process_group import exit_on_termination, run_logged
    from repo_root import ROOT
    from required_command import run_required
    from session_bus import session_env

TOOL = "apply_keymap"
OPTION = "ctrl:swap_lalt_lctl"
CONFIG_FILE = "kxkbrc"
GROUP = "Layout"
OPTIONS_KEY = "Options"
RESET_KEY = "ResetOldOptions"
COMMAND_TIMEOUT = 60.0
REQUIRED_TOOLS = ("kreadconfig6", "kwriteconfig6")
# The session tools that can emit KWin's reloadConfig signal, in preference
# order. qdbus cannot emit a signal, and KWin listens for the signal, not a
# method call.
RELOAD_COMMANDS = (
    (
        "dbus-send",
        [
            "dbus-send",
            "--session",
            "--type=signal",
            "/Layouts",
            "org.kde.keyboard.reloadConfig",
        ],
    ),
    (
        "busctl",
        [
            "busctl",
            "--user",
            "emit",
            "/Layouts",
            "org.kde.keyboard",
            "reloadConfig",
        ],
    ),
)


def merge_option(existing: str, option: str = OPTION) -> str:
    """Return *existing*'s comma-separated options with *option* present once.

    KConfig stores ``[Layout] Options`` as a comma-separated list, and XKB
    option names cannot contain a comma. Blank entries and surrounding
    whitespace are dropped so a hand-edited file still reads cleanly, and an
    option already present is not appended again.
    """
    options = []
    for part in existing.split(","):
        part = part.strip()
        if part:
            options.append(part)
    if option not in options:
        options.append(option)
    return ",".join(options)


def _note(message: str) -> None:
    """Print ``apply_keymap: note: <message>`` to stderr."""
    report_note(TOOL, message, err=True)


def _read_options(env: dict[str, str], scratch: Path) -> tuple[str, int | None]:
    """Return the current ``Options`` value and None, or an error status.

    KConfig reports a missing key as a successful, empty value, so a zero exit
    and no output both mean "the user has no options yet". Its diagnostics go
    to stderr (an invalid escape in the file produces a warning there), so
    only stdout is the value; merging the streams would turn the warning into
    an XKB option. A non-zero exit is a failed required command and its status
    is returned for the caller to propagate; a value that cannot be decoded is
    this tool's exit-2 error instead of a traceback.
    """
    log = scratch / "kreadconfig6.log"
    argv = [
        "kreadconfig6",
        "--file",
        CONFIG_FILE,
        "--group",
        GROUP,
        "--key",
        OPTIONS_KEY,
    ]
    try:
        result = subprocess.run(
            argv,
            cwd=ROOT,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=COMMAND_TIMEOUT,
            check=False,
        )
    except OSError as exc:
        return "", report_error(TOOL, f"cannot run kreadconfig6: {exc}")
    except subprocess.TimeoutExpired as exc:
        status = _report_failure(
            f"kreadconfig6 timed out after {COMMAND_TIMEOUT:g}s",
            log,
            exc.stderr,
        )
        return "", status
    if result.returncode != 0:
        if result.returncode < 0:
            number = -result.returncode
            try:
                name = signal.Signals(number).name
            except ValueError:
                name = str(number)
            message = f"kreadconfig6 killed by signal {name}"
        else:
            message = f"kreadconfig6 exited {result.returncode}"
        return "", _report_failure(
            message, log, result.stderr or result.stdout
        )
    try:
        return result.stdout.decode("utf-8").strip(), None
    except UnicodeDecodeError as exc:
        return "", report_error(
            TOOL, f"cannot read the current {OPTIONS_KEY} value: {exc}"
        )


def _report_failure(message: str, log: Path, output: bytes | None) -> int:
    """Write *output* to *log* and return the shared failed-command status.

    A scratch log that cannot be written is this tool's exit-2 diagnostic
    rather than a traceback; the command still failed, but its output is
    unavailable, so the message carries the cause instead.
    """
    try:
        log.write_bytes(output or b"")
    except OSError as exc:
        return report_error(TOOL, f"cannot write {log.name}: {exc}")
    return report_failure(TOOL, message, log)


def _write_options(
    env: dict[str, str], scratch: Path, options: str
) -> int | None:
    """Write *options* and enable the XKB options; return an error status.

    ``ResetOldOptions`` is written after ``Options`` so a failure between the
    two leaves the options stored but still disabled, rather than enabling a
    set that does not include the swap.
    """
    steps = (
        [
            "kwriteconfig6",
            "--file",
            CONFIG_FILE,
            "--group",
            GROUP,
            "--key",
            OPTIONS_KEY,
            options,
        ],
        [
            "kwriteconfig6",
            "--file",
            CONFIG_FILE,
            "--group",
            GROUP,
            "--key",
            RESET_KEY,
            "--type",
            "bool",
            "true",
        ],
    )
    for argv in steps:
        status = run_required(
            TOOL,
            argv,
            env,
            scratch / f"{argv[0]}.log",
            COMMAND_TIMEOUT,
            ROOT,
        )
        if status is not None:
            return status
    return None


def _reload(env: dict[str, str], scratch: Path) -> None:
    """Ask KWin to rebuild its keymap; a failure is a note, never an error.

    KWin listens for the ``reloadConfig`` signal, and every available emitter
    is tried in preference order: an installed ``dbus-send`` that cannot reach
    the bus does not hide a working ``busctl``. If none succeeds, the written
    configuration still applies at the next login, so the note says so and the
    exit status stays 0.
    """
    available = [
        (name, argv)
        for name, argv in RELOAD_COMMANDS
        if shutil.which(name) is not None
    ]
    if not available:
        _note(
            "neither dbus-send nor busctl is on PATH; the key swap takes "
            "effect at the next login"
        )
        return
    failures: list[str] = []
    for name, argv in available:
        log = scratch / f"{name}.log"
        try:
            status = run_logged(argv, env, log, COMMAND_TIMEOUT, ROOT)
        except OSError as exc:
            failures.append(f"{name} could not be started: {exc}")
            continue
        if status is None:
            failures.append(f"{name} timed out after {COMMAND_TIMEOUT:g}s")
        elif status != 0:
            failures.append(f"{name} exited {status}")
        else:
            return
    _note(
        "could not ask KWin to reload the keymap ("
        + "; ".join(failures)
        + "); the key swap takes effect at the next login"
    )


def _apply(environ: dict[str, str]) -> int:
    """Read the user's options, add the swap, enable them and reload KWin."""
    scratch = create_scratch_directory(TOOL, "apply-keymap-")
    if scratch is None:
        return 2
    try:
        env = session_env(environ)
        existing, status = _read_options(env, scratch)
        if status is not None:
            return status
        status = _write_options(env, scratch, merge_option(existing))
        if status is not None:
            return status
        _reload(env, scratch)
        return 0
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    """Run the keymap CLI; *argv* is the argument list without a program name."""
    parser = EscapingArgumentParser(
        prog="apply_keymap",
        description=(
            "Swap the left Control and Alt keys for this user's Plasma "
            "session so the reference's Command-key shortcuts work."
        ),
        epilog=(
            "exit status: 0 when the option was written, 1 when a required "
            "command failed, 2 for a usage error, a missing external tool, "
            "one that cannot be started, a scratch directory that cannot be "
            "created, or a configuration value that cannot be read, and 128 "
            "plus the signal number when a SIGTERM or SIGHUP ends the run"
        ),
    )
    parser.parse_args(argv)

    missing = report_missing_tool(TOOL, REQUIRED_TOOLS)
    if missing is not None:
        return missing
    with exit_on_termination():
        return _apply(dict(os.environ))


if __name__ == "__main__":
    sys.exit(main())
