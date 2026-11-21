"""Select the installed Platinum Ghostty theme in the user's Ghostty config.

``make apply`` installs the theme file and then runs this script; ``make
apply-ghostty`` installs only the Ghostty package before doing the same.
Ghostty reads ``<config home>/ghostty/config.ghostty``, so this writes one
marker-delimited block at the end of that file that names the installed theme
by its absolute path. Every other byte of the file is preserved, and the
legacy ``<config home>/ghostty/config`` file is never opened, so a ``theme =``
line the user wrote in either file stays theirs. Explicit color keys in the
user's config override the theme, which keeps their own colors.

``make remove-ghostty`` runs the same script with ``--remove``: it deletes only
the block, and deletes the file when nothing else is left in it. The block
edit itself lives in ``tools/ghostty_config.py``; this file resolves the homes,
checks the paths and performs the atomic write.

Usage::

    python3 tools/apply_ghostty.py [--optional]
    python3 tools/apply_ghostty.py --remove

Exit status: 0 when the block was written or removed (or nothing needed
changing), 2 for a usage error, an unusable ``HOME`` or config/data home, a
missing installed theme file, a symbolic link at the config file, a config
file that cannot be read or written, or a block whose markers are unbalanced
or repeated.
"""

from __future__ import annotations

import os
import shutil
import stat
import sys
from pathlib import Path

if __package__:
    from tools import xdg_homes
    from tools.argument_parsing import EscapingArgumentParser
    from tools.atomic_write import write_atomically
    from tools.diagnostics import report_error, report_note
    from tools.ghostty_config import GhosttyConfigError, apply_block, remove_block
else:  # run directly: python3 tools/apply_ghostty.py
    import xdg_homes
    from argument_parsing import EscapingArgumentParser
    from atomic_write import write_atomically
    from diagnostics import report_error, report_note
    from ghostty_config import GhosttyConfigError, apply_block, remove_block

TOOL = "apply_ghostty"
GHOSTTY_ID = "org.macos8.desktop"
THEME_NAME = "Platinum"


def _raise_filesystem_error(action: str, target: Path, exc: OSError) -> None:
    """Raise the Ghostty config diagnostic shared by filesystem operations."""
    raise GhosttyConfigError(f"cannot {action} {target}: {exc.strerror}") from exc


def theme_file(data_home: Path) -> Path:
    """Return the installed theme file part 1/2 ships under *data_home*."""
    return data_home / "ghostty" / "themes" / GHOSTTY_ID / THEME_NAME


def config_file(config_home: Path) -> Path:
    """Return the Ghostty config file Ghostty reads under *config_home*."""
    return config_home / "ghostty" / "config.ghostty"


def _read(target: Path) -> bytes | None:
    """Return the bytes of *target*, or ``None`` when it does not exist.

    A symbolic link is refused before it is read or replaced, so the write
    cannot land on a file outside the config home.
    """
    if os.path.islink(target):
        raise GhosttyConfigError(
            f"{target} is a symbolic link; replace it with a regular file or "
            "edit the file it points to by hand"
        )
    try:
        return target.read_bytes()
    except FileNotFoundError:
        return None
    except OSError as exc:
        _raise_filesystem_error("read", target, exc)


def _write(target: Path, data: bytes, previous_mode: int | None) -> None:
    """Atomically publish *data* at *target*, keeping an existing file's mode."""
    try:
        write_atomically(
            target,
            lambda destination: destination.write(data),
            mode=previous_mode,
        )
    except OSError as exc:
        _raise_filesystem_error("write", target, exc)


def _mode_of(target: Path) -> int | None:
    """Return the permission bits of an existing *target*, else ``None``."""
    try:
        return stat.S_IMODE(os.stat(target).st_mode)
    except FileNotFoundError:
        return None


def apply(config_home: Path, data_home: Path, env: dict[str, str], optional: bool) -> int:
    """Write the Platinum block naming the installed theme into the config file."""
    if optional and shutil.which("ghostty") is None:
        report_note(
            TOOL,
            "ghostty is not on PATH; the Platinum Ghostty theme is installed "
            "but not selected",
        )
        return 0
    theme = theme_file(data_home)
    if not theme.is_file():
        raise GhosttyConfigError(
            f"the installed Ghostty theme {theme} is missing; run make install "
            "first"
        )
    target = config_file(config_home)
    data = _read(target)
    updated = apply_block(data or b"", os.fsencode(theme))
    if data is not None and updated == data:
        report_note(TOOL, f"{target} already selects the Platinum theme")
        return 0
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        _raise_filesystem_error("create", target.parent, exc)
    _write(target, updated, _mode_of(target))
    report_note(
        TOOL,
        f"selected the Platinum theme in {target}; new Ghostty windows read it, "
        "and Ghostty's reload-config binding reloads it",
    )
    return 0


def remove(config_home: Path) -> int:
    """Delete only the Platinum block; delete the file when nothing else is in it."""
    target = config_file(config_home)
    data = _read(target)
    if data is None:
        report_note(TOOL, f"no Ghostty config at {target}; nothing to remove")
        return 0
    updated = remove_block(data)
    if updated == data:
        report_note(TOOL, f"{target} has no Platinum block; left unchanged")
        return 0
    if not updated:
        try:
            target.unlink()
        except OSError as exc:
            _raise_filesystem_error("remove", target, exc)
        report_note(TOOL, f"removed {target}, which held only the Platinum block")
        return 0
    _write(target, updated, _mode_of(target))
    report_note(TOOL, f"removed the Platinum block from {target}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the Ghostty selection CLI; *argv* excludes the program name."""
    parser = EscapingArgumentParser(
        prog=TOOL,
        description=(
            "Select or clear the Platinum Ghostty theme in the Ghostty config file."
        ),
        epilog=(
            "exit status: 0 when the block was written or removed, 2 for a usage "
            "error, an unusable config or data home, a missing installed theme, "
            "a symbolic link at the config file, a config file that cannot be "
            "read or written, or a block whose markers are unbalanced"
        ),
    )
    parser.add_argument(
        "--optional",
        action="store_true",
        help="skip the selection, with a note, when ghostty is not on PATH",
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="remove only the Platinum block from the Ghostty config file",
    )
    args = parser.parse_args(argv)

    env = dict(os.environ)
    try:
        config_home = xdg_homes.require_home(
            xdg_homes.config_home(env),
            env,
            "XDG_CONFIG_HOME",
            "$HOME/.config",
            error=GhosttyConfigError,
        )
        if args.remove:
            return remove(config_home)
        data_home = xdg_homes.require_home(
            xdg_homes.data_home(env),
            env,
            "XDG_DATA_HOME",
            "$HOME/.local/share",
            error=GhosttyConfigError,
        )
        return apply(config_home, data_home, env, args.optional)
    except GhosttyConfigError as exc:
        return report_error(TOOL, str(exc))


if __name__ == "__main__":
    sys.exit(main())
