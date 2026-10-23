"""Expose the shipped Xcursor pointer set and select it for the running session.

``make apply-cursor`` installs the icon theme, which carries the Platinum
pointer set under ``cursors/``, and then runs this script. Xcursor searches
``~/.icons``, not ``$XDG_DATA_HOME/icons``, so the installed theme is exposed
at ``$HOME/.icons/org.macos8.desktop`` as a symlink and selected with
``plasma-apply-cursortheme org.macos8.desktop``. ``make remove-cursor`` runs
the same script with ``--remove``: it deletes only that link, leaving a foreign
path and ``kcminputrc`` untouched.

Usage::

    python3 tools/apply_cursor.py
    python3 tools/apply_cursor.py --remove

Exit status: 0 when the selection or removal ran, 1 when the selector failed,
2 for a usage error, an unusable ``HOME``, a missing installed theme, a
foreign path at the link target, or a selector that cannot be started.
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

if __package__:
    from tools.argument_parsing import EscapingArgumentParser
    from tools.containment import read_text
    from tools.diagnostics import report_error, report_failure, report_missing_tool
    from tools.process_group import exit_on_termination, run_logged
    from tools.repo_root import ROOT
    from tools.terminal import escape_controls
else:  # run directly: python3 tools/apply_cursor.py
    from argument_parsing import EscapingArgumentParser
    from containment import read_text
    from diagnostics import report_error, report_failure, report_missing_tool
    from process_group import exit_on_termination, run_logged
    from repo_root import ROOT
    from terminal import escape_controls

TOOL = "apply_cursor"
CURSOR_THEME = "org.macos8.desktop"
SELECT_TOOL = "plasma-apply-cursortheme"
COMMAND_TIMEOUT = 60.0


class CursorError(Exception):
    """A refused path or unusable environment, reported as an error by name."""


def _note(message: str) -> None:
    """Print ``apply_cursor: note: <message>`` on stdout."""
    print(f"{TOOL}: note: {escape_controls(message)}")


def _absolute(env: dict[str, str], name: str) -> Path | None:
    """Return *name* from *env* when it is an absolute path, else ``None``."""
    value = env.get(name, "")
    return Path(value) if os.path.isabs(value) else None


def resolve_homes(env: dict[str, str]) -> tuple[Path, Path, Path]:
    """Return ``(home, data_home, config_home)`` from *env*.

    ``$HOME`` must be absolute because it is the only fallback for both XDG
    homes; a relative or unset ``HOME`` raises :class:`CursorError` naming it.
    An absolute ``$XDG_DATA_HOME`` or ``$XDG_CONFIG_HOME`` wins, otherwise the
    XDG default below ``$HOME`` is used, as ``make install`` resolves it.
    """
    home = env.get("HOME", "")
    if not os.path.isabs(home):
        raise CursorError(
            "HOME is unset or not absolute; export an absolute HOME"
        )
    home_path = Path(home)
    data_home = _absolute(env, "XDG_DATA_HOME") or home_path / ".local" / "share"
    config_home = _absolute(env, "XDG_CONFIG_HOME") or home_path / ".config"
    return home_path, data_home, config_home


def installed_theme(data_home: Path) -> Path:
    """Return the installed icon-theme directory that carries the cursor."""
    return data_home / "icons" / CURSOR_THEME


def _require_installed(data_home: Path) -> Path:
    """Return the installed theme, refusing a missing ``index.theme``/cursor.

    The icon theme's own ``index.theme`` makes the symlinked directory a valid
    cursor theme too, so both it and ``cursors/left_ptr`` must be regular files
    before the link claims to expose a theme.
    """
    theme = installed_theme(data_home)
    for path in (theme / "index.theme", theme / "cursors" / "left_ptr"):
        if not path.is_file():
            raise CursorError(
                f"installed cursor theme is missing {path}; run "
                "make install INSTALL_PACKAGES=icon-theme"
            )
    return theme


def _link_target(home: Path) -> Path:
    """Return the Xcursor-path link that exposes the installed theme."""
    return home / ".icons" / CURSOR_THEME


def _install_link(home: Path, theme: Path) -> None:
    """Create ``$HOME/.icons/org.macos8.desktop`` as a link to *theme*.

    A missing ``~/.icons`` is created. An existing link to the installed theme
    is already ours, so a repeat install changes nothing; any other symlink,
    directory or file is refused without being touched.
    """
    icons = home / ".icons"
    target = _link_target(home)
    if os.path.lexists(icons) and not icons.is_dir():
        raise CursorError(f"{icons} exists but is not a directory")
    if target.is_symlink():
        link = os.readlink(target)
        if link == str(theme):
            return
        raise CursorError(
            f"{target} is a symlink to {link}, not our installed theme; "
            "leaving it untouched"
        )
    if os.path.lexists(target):
        raise CursorError(
            f"{target} exists and is not our symlink; leaving it untouched"
        )
    try:
        icons.mkdir(parents=True, exist_ok=True)
        os.symlink(str(theme), str(target))
    except OSError as exc:
        raise CursorError(f"cannot create {target}: {exc}") from exc


def _select(env: dict[str, str]) -> int:
    """Select our cursor theme with ``plasma-apply-cursortheme``.

    A missing selector is a usage error; a timeout or non-zero exit is a
    failed command whose bounded log tail is reported. A selector that
    ``shutil.which`` found can still fail to start (a corrupt binary, or a
    script whose interpreter is missing): ``run_logged`` reports that as an
    ``OSError``, which is as unusable as a missing selector, so it becomes
    this tool's own exit-2 diagnostic instead of an escaping traceback.
    """
    missing = report_missing_tool(TOOL, [SELECT_TOOL])
    if missing is not None:
        return missing
    scratch = Path(tempfile.mkdtemp(prefix="apply-cursor-"))
    try:
        log = scratch / "plasma-apply-cursortheme.log"
        try:
            status = run_logged(
                [SELECT_TOOL, CURSOR_THEME],
                env,
                log,
                COMMAND_TIMEOUT,
                ROOT,
            )
        except OSError as exc:
            return report_error(TOOL, f"cannot run {SELECT_TOOL}: {exc}")
        if status is None:
            return report_failure(
                TOOL,
                f"{SELECT_TOOL} timed out after {COMMAND_TIMEOUT:g}s",
                log,
            )
        if status != 0:
            return report_failure(TOOL, f"{SELECT_TOOL} exited {status}", log)
        return 0
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def _apply(home: Path, data_home: Path, env: dict[str, str]) -> int:
    """Link the installed theme into the Xcursor path, then select it."""
    theme = _require_installed(data_home)
    _install_link(home, theme)
    status = _select(env)
    if status == 0:
        _note(
            "restart running applications for the new pointer to display "
            "correctly"
        )
    return status


def _cursor_theme_setting(config_home: Path) -> str | None:
    """Return ``[Mouse] cursorTheme`` from ``kcminputrc``, or ``None``.

    Only the selection note reads this file; it is never edited. A missing,
    unreadable, non-regular or non-UTF-8 file reads as no setting rather than
    failing the removal. The shared regular-file reader opens with
    ``O_NONBLOCK`` and checks the opened descriptor, so a FIFO or device at
    the path is refused at once instead of blocking the removal.
    """
    path = config_home / "kcminputrc"
    try:
        text = read_text(path, ROOT, encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError, ValueError):
        return None
    section = None
    value = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", ";")):
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped[1:-1].strip()
        elif section == "Mouse" and "=" in stripped:
            key, _, setting = stripped.partition("=")
            if key.strip() == "cursorTheme":
                value = setting.strip()
    return value


def _remove(home: Path, data_home: Path, config_home: Path) -> int:
    """Unlink only our Xcursor-path symlink; leave every foreign path alone."""
    target = _link_target(home)
    theme = installed_theme(data_home)
    if target.is_symlink():
        link = os.readlink(target)
        if link == str(theme):
            try:
                target.unlink()
            except OSError as exc:
                raise CursorError(f"cannot remove {target}: {exc}") from exc
        else:
            _note(f"{target} is not our symlink; leaving it untouched")
    elif os.path.lexists(target):
        _note(f"{target} is not our symlink; leaving it untouched")
    if _cursor_theme_setting(config_home) == CURSOR_THEME:
        _note(
            f"[Mouse] cursorTheme in {config_home / 'kcminputrc'} still names "
            f"{CURSOR_THEME}; run {SELECT_TOOL} breeze_cursors to reset"
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the cursor selection CLI; *argv* excludes the program name."""
    parser = EscapingArgumentParser(
        prog=TOOL,
        description=(
            "Expose the installed Mac OS 8.6 Xcursor pointer set at the "
            "Xcursor path and select it."
        ),
        epilog=(
            "exit status: 0 when the selection ran, 1 when the selector "
            "failed, 2 for a usage error, an unusable HOME, a missing "
            "installed theme, a foreign path at the link target, or a "
            "selector that cannot be started"
        ),
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="remove our ~/.icons symlink and leave kcminputrc untouched",
    )
    args = parser.parse_args(argv)

    try:
        home, data_home, config_home = resolve_homes(dict(os.environ))
        if args.remove:
            return _remove(home, data_home, config_home)
        with exit_on_termination():
            return _apply(home, data_home, dict(os.environ))
    except CursorError as exc:
        return report_error(TOOL, str(exc))


if __name__ == "__main__":
    sys.exit(main())
