"""Clear the Kvantum selection ``make apply`` published.

``make apply`` selects the widget style with ``kvantummanager --set
org.macos8.desktop`` when the manager is installed, which stores the choice
as ``[General] theme=org.macos8.desktop`` in the user's
``$XDG_CONFIG_HOME/Kvantum/kvantum.kvconfig``. ``make uninstall`` removes the
installed widget style but must not touch that selection (a theme chosen
through System Settings survives an uninstall), so a leftover selection
names a theme that no longer exists and Qt applications silently draw
Kvantum's compiled-in default. ``make remove-kvantum`` runs this module: it
deletes only our ``theme`` line under ``[General]`` and rewrites the file,
leaving every other line — a foreign theme name, other keys and sections,
comments and each line's own ending — byte-identical. An absent ``Kvantum/``
directory, an absent file or a selection not naming our id is left alone,
with a note saying so, and nothing is created.

The line surgery reuses the generic ``tools/gtk_settings`` ini scanners
through ``remove_key_from_section`` — the same BOM, ending and key parsing
the GTK tests pin — so the behaviour matches the file ``kvantummanager``
writes. The runs serialize on the same
bounded-wait config-home flock as ``tools/apply_gtk`` and publish through
``tools/atomic_write``, so a mid-run failure leaves the previous file
intact.

Usage::

    python3 tools/kvantum_selection.py
    python3 -m tools.kvantum_selection

Exit status: 0 when the selection was cleared or nothing of ours was there
to clear, 2 for a usage error, an unresolvable config home, another run
holding the config-home lock past the timeout, a ``Kvantum`` directory or
``kvantum.kvconfig`` path that is a symbolic link, or a kvconfig that
cannot be read or written.
"""

from __future__ import annotations

import contextlib
import os
import sys
from collections.abc import Iterator
from pathlib import Path

if __package__:
    from tools import xdg_homes
    from tools.argument_parsing import EscapingArgumentParser
    from tools.atomic_write import write_bytes_atomically
    from tools.diagnostics import report_error, report_note
    from tools.file_lock import parent_dir_lock
    from tools.gtk_settings import remove_key_from_section
    from tools.gtk_user_files import ConfigError, read_config_text
    from tools.symlink_refusal import refuse_symlink
else:  # run directly: python3 tools/kvantum_selection.py
    import xdg_homes
    from argument_parsing import EscapingArgumentParser
    from atomic_write import write_bytes_atomically
    from diagnostics import report_error, report_note
    from file_lock import parent_dir_lock
    from gtk_settings import remove_key_from_section
    from gtk_user_files import ConfigError, read_config_text
    from symlink_refusal import refuse_symlink

__all__ = ["KVANTUM_ID", "TOOL", "main", "remove_theme"]

TOOL = "remove_kvantum"
# The id `kvantummanager --set` writes (the same id the Makefile's
# KVANTUM_ID and tools/theme_apply_optional.py::KVANTUM_THEME name).
KVANTUM_ID = "org.macos8.desktop"
# A whole removal touches one small user file, so a second run normally
# waits well under a second for the first to finish. The bound only exists
# so a holder stopped with SIGSTOP cannot block every later run forever; it
# matches the apply-gtk lock's default.
LOCK_TIMEOUT = 60.0


def remove_theme(text: str) -> tuple[str, bool]:
    """Remove our ``theme`` lines from *text*'s ``[General]`` section.

    Returns ``(new_text, removed)``; the surgery, its byte-identical line
    keeping and its no-match no-rewrite contract are
    :func:`tools.gtk_settings.remove_key_from_section` applied to the
    ``[General]`` ``theme`` key and :data:`KVANTUM_ID`.
    """
    return remove_key_from_section(text, "General", "theme", KVANTUM_ID)


def _note(message: str) -> None:
    """Print ``remove_kvantum: note: <message>`` on stdout."""
    report_note(TOOL, message)


@contextlib.contextmanager
def _config_lock(config_home: Path) -> Iterator[None]:
    """Serialize removals on a lock over *config_home*'s directory.

    The containing directory is created if needed so the removal has an
    inode to lock, the same way the apply-gtk lock does; the config home
    itself stays untouched. The lock adds no lock file to the user's
    configuration and is released by the kernel when the process dies,
    SIGKILL included.
    """
    with parent_dir_lock(
        config_home,
        "for the Kvantum selection",
        f"another remove-kvantum to finish with {config_home}",
        timeout=LOCK_TIMEOUT,
        error=ConfigError,
    ):
        yield


def _clear_selection(config_home: Path) -> int:
    """Clear our selection from *config_home*'s Kvantum kvconfig.

    Touches only ``config_home/Kvantum/kvantum.kvconfig``, never the data
    home or the installed theme files, and never adds or removes any other
    kvconfig key — ``kvantummanager``, not this tool, owns the rest of that
    file. An absent file, directory or selection succeeds without writing
    or creating anything.
    """
    directory = config_home / "Kvantum"
    path = directory / "kvantum.kvconfig"
    # A symlinked config path is the user's link: refuse it before anything
    # is read through it, so the link and its target are left untouched.
    refuse_symlink(directory, "write", ConfigError)
    refuse_symlink(path, "write", ConfigError)
    text = read_config_text(path)
    if text is None:
        # ``None`` covers true absence and occupied-but-unreadable alike, so
        # the occupied cases are separated out: reporting a directory or a
        # fouled ``Kvantum`` path as absent would tell the operator the
        # selection is gone when nothing could be read where
        # ``kvantummanager`` writes it (the GTK staging code refuses such a
        # target as an error, not a note).
        if path.is_dir():
            raise ConfigError(
                f"cannot read {path}: it is a directory, not a regular file"
            )
        if directory.exists():
            raise ConfigError(
                f"cannot read {path}: {directory} is not a directory, so "
                "nothing occupies the path below it"
            )
        _note(f"nothing to clear: {path} is absent")
        return 0
    updated, removed = remove_theme(text)
    if not removed:
        _note(
            f"left {path} untouched: it does not select {KVANTUM_ID}"
        )
        return 0
    write_bytes_atomically(path, updated.encode("utf-8"))
    _note(f"cleared the {KVANTUM_ID} selection from {path}")
    _note("restart running Qt applications to pick up the removal")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the Kvantum selection removal CLI; *argv* excludes the name."""
    parser = EscapingArgumentParser(
        prog=TOOL,
        description=(
            "Clear the Kvantum widget-theme selection `make apply` "
            "published."
        ),
    )
    parser.parse_args(argv)

    try:
        config_home = xdg_homes.require_home(
            xdg_homes.config_home(os.environ),
            os.environ,
            "XDG_CONFIG_HOME",
            "$HOME/.config",
            error=ConfigError,
        )
        with _config_lock(config_home):
            status = _clear_selection(config_home)
    except ConfigError as exc:
        return report_error(TOOL, str(exc))
    return status


if __name__ == "__main__":
    sys.exit(main())
