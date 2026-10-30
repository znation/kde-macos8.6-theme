"""Select or clear the opt-in GTK 3 and GTK 4 Platinum themes.

``make apply-gtk`` installs the GTK theme files and then runs this script.
It sets ``gtk-theme-name=org.macos8.desktop`` in the GTK 3 and GTK 4
``settings.ini`` files and writes a ``gtk-4.0/gtk.css`` user stylesheet that
imports the installed GTK 4 sheet, because libadwaita applications read user
CSS instead of the ``gtk-theme-name`` setting. ``make remove-gtk`` runs the
same script with ``--remove``: it deletes only our ``gtk-theme-name`` lines and
the marker user stylesheet, leaving foreign values and files alone. An apply
and a removal serialize on a lock over the directory containing the config
home, so two concurrent runs cannot publish a stale edit over the other's
result. An apply also holds the data-home lock that ``make install`` and
``make uninstall`` hold for their whole run, so an uninstall cannot remove
the installed sheets between the apply's sheet check and the selection that
names them. Both the config-home and the data-home lock are the bounded-wait
exclusive flock in ``tools/file_lock.py``.

Usage::

    python3 tools/apply_gtk.py
    python3 tools/apply_gtk.py --remove

Exit status: 0 when the selection or removal ran, 1 when an installed GTK 3
or GTK 4 sheet is missing, 2 for a usage error, an unresolvable config home
(or data home when applying), another run holding the config-home or data-home
lock past the timeout, a config-home directory that cannot be created or
locked, a data home that cannot be locked, a settings or user-CSS path that
is a symbolic link, or a settings or user-CSS file that cannot be read or
written.
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
    from tools.diagnostics import report_error, report_note
    from tools.file_lock import exclusive_flock, installed_data_lock
    from tools.gtk_settings import GTK_ID
    from tools.gtk_selection import (
        apply as _apply,
        installed_sheets as _installed_sheets,
        remove as _remove,
    )
    from tools.gtk_user_files import ConfigError
else:  # run directly: python3 tools/apply_gtk.py
    import xdg_homes
    from argument_parsing import EscapingArgumentParser
    from diagnostics import report_error, report_note
    from file_lock import exclusive_flock, installed_data_lock
    from gtk_settings import GTK_ID
    from gtk_selection import (
        apply as _apply,
        installed_sheets as _installed_sheets,
        remove as _remove,
    )
    from gtk_user_files import ConfigError

TOOL = "apply_gtk"
__all__ = ["GTK_ID"]
# A whole apply or removal is short (a few small config files), so a second
# run normally waits well under a second for the first to finish. The bound
# only exists so a holder stopped with SIGSTOP cannot block every later run
# forever; it matches the install lock's default.
LOCK_TIMEOUT = 60.0


def _note(message: str) -> None:
    """Print ``apply_gtk: note: <message>`` on stdout."""
    report_note(TOOL, message)


@contextlib.contextmanager
def _config_lock(config_home: Path) -> Iterator[None]:
    """Serialize apply and removal on a lock over *config_home*'s directory.

    Both runs read the settings and user CSS, edit that text, and stage the
    result; without a lock two of them can read the same original and one
    can publish a stale result after the other finished. The write from the
    process that finishes last then leaves a mixed selection (our user CSS
    beside a settings file with no theme name, or the reverse), which neither
    an apply nor a remove intends. Locking the directory that contains the
    config home, rather than the config home itself, means a removal still
    serializes when the config home does not exist yet: an apply that is
    about to create it takes the same lock first. The lock adds no lock file
    to the user's configuration and is released by the kernel when the
    process dies, SIGKILL included.

    The containing directory is created if needed, so both runs have an inode
    to lock; the config home itself is left for an apply to create.
    """
    lock_dir = config_home.parent
    try:
        lock_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ConfigError(f"cannot create {lock_dir}: {exc}") from exc
    with exclusive_flock(
        lock_dir,
        "for the GTK selection",
        f"another apply-gtk/remove-gtk to finish with {config_home}",
        timeout=LOCK_TIMEOUT,
        error=ConfigError,
    ):
        yield


def _state(env: dict[str, str], variable: str) -> str:
    """Describe the *variable* value *env* carries, for a refusal message."""
    if variable not in env:
        return "unset"
    if not env[variable]:
        return "empty"
    return f"not an absolute path ('{env[variable]}')"


def _require_home(
    path: Path | None, env: dict[str, str], variable: str, fallback: str
) -> Path:
    """Return *path*, or refuse naming the values that could not resolve.

    *fallback* is the ``$HOME``-relative path the XDG spec falls back to,
    included in the diagnostic so the user can see which directory could not
    be resolved. Every caller resolves its path through
    :mod:`tools.xdg_homes` and must refuse rather than guess where to write,
    so the diagnostic lives here once; the resolver returns ``None`` only
    when both *variable* and ``HOME`` are unusable, so both received values
    appear, in shell quoting that marks the bounds of a value (an empty one
    counts as unset, matching the resolver's own treatment), and
    ``report_error``'s escaping keeps every byte from reaching a terminal
    raw.
    """
    if path is None:
        raise ConfigError(
            f"{variable} is {_state(env, variable)} and HOME is "
            f"{_state(env, 'HOME')}, so the {fallback} fallback cannot "
            f"be used; set {variable} to an absolute path or export an "
            "absolute HOME"
        )
    return path


def main(argv: list[str] | None = None) -> int:
    """Run the GTK selection CLI; *argv* excludes the program name."""
    parser = EscapingArgumentParser(
        prog=TOOL,
        description=(
            "Select or clear the Mac OS 8.6 GTK 3 and GTK 4 Platinum themes."
        ),
        epilog=(
            "exit status: 0 when the selection or removal ran, 1 when an "
            "installed GTK 3 or GTK 4 sheet is missing, 2 for a usage error, "
            "an unresolvable config home (or data home when applying), another "
            "run holding the config-home or data-home lock past the timeout, "
            "a config-home directory that cannot be created or locked, a data "
            "home that cannot be locked, a settings or "
            "user-CSS path that is a symbolic link, or a settings or user-CSS "
            "file that cannot be read or written"
        ),
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="remove our gtk-theme-name lines and marker user CSS",
    )
    args = parser.parse_args(argv)

    env = os.environ
    try:
        if args.remove:
            # Removal touches only the config home, so it must work when no
            # data home resolves: refusing it would block clearing a
            # selection that is already installed.
            config_home = _require_home(
                xdg_homes.config_home(env), env, "XDG_CONFIG_HOME", "$HOME/.config"
            )
            with _config_lock(config_home):
                status = _remove(config_home)
        else:
            config_home = _require_home(
                xdg_homes.config_home(env), env, "XDG_CONFIG_HOME", "$HOME/.config"
            )
            data_home = _require_home(
                xdg_homes.data_home(env),
                env,
                "XDG_DATA_HOME",
                "$HOME/.local/share",
            )
            # Check the installed sheets before creating or locking any
            # directory, so an apply that refuses a missing sheet leaves the
            # config home absent as it found it.
            sheets = _installed_sheets(data_home)
            if sheets is None:
                return 1
            # Hold the data-home lock make install/uninstall hold, so an
            # uninstall cannot remove the sheets between this check and the
            # selection that names them; the re-check under the lock catches
            # sheets removed before this run took the lock.
            with installed_data_lock(
                data_home,
                "for the GTK selection",
                LOCK_TIMEOUT,
                error=ConfigError,
            ):
                sheets = _installed_sheets(data_home)
                if sheets is None:
                    return 1
                with _config_lock(config_home):
                    status = _apply(sheets, config_home, _note)
    except ConfigError as exc:
        return report_error(TOOL, str(exc))
    if status == 0:
        _note("restart running GTK applications to pick up the theme")
    return status


if __name__ == "__main__":
    sys.exit(main())
