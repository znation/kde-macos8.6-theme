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
names them.

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
import errno
import fcntl
import os
import sys
import time
from collections.abc import Iterator
from pathlib import Path

if __package__:
    from tools import xdg_homes
    from tools.argument_parsing import EscapingArgumentParser
    from tools.diagnostics import report_error, report_failure, report_note
    from tools.gtk_settings import GTK_ID, remove_theme_name, set_theme_name
    from tools.gtk_staging import commit, stage_all
    from tools.gtk_user_files import (
        ConfigError,
        MAX_CONFIG_FILE_BYTES,
        read_config_text,
        settings_path,
        user_css_remove,
        user_css_write,
    )
    from tools.symlink_refusal import refuse_symlink
else:  # run directly: python3 tools/apply_gtk.py
    import xdg_homes
    from argument_parsing import EscapingArgumentParser
    from diagnostics import report_error, report_failure, report_note
    from gtk_settings import GTK_ID, remove_theme_name, set_theme_name
    from gtk_staging import commit, stage_all
    from gtk_user_files import (
        ConfigError,
        MAX_CONFIG_FILE_BYTES,
        read_config_text,
        settings_path,
        user_css_remove,
        user_css_write,
    )
    from symlink_refusal import refuse_symlink

TOOL = "apply_gtk"
# A whole apply or removal is short (a few small config files), so a second
# run normally waits well under a second for the first to finish. The bound
# only exists so a holder stopped with SIGSTOP cannot block every later run
# forever; it matches the install lock's default.
LOCK_TIMEOUT = 60.0
_LOCK_POLL = 0.05


def _note(message: str) -> None:
    """Print ``apply_gtk: note: <message>`` on stdout."""
    report_note(TOOL, message)


@contextlib.contextmanager
def _exclusive_flock(lock_dir: Path, holder: str) -> Iterator[None]:
    """Hold an exclusive flock on *lock_dir* for the body's duration.

    The directory must already exist; an open that fails (a vanished or
    unopenable directory) raises :class:`ConfigError` naming it. The wait for
    a holder is bounded: another run that keeps the lock past ``LOCK_TIMEOUT``
    -- stopped with SIGSTOP, say -- raises :class:`ConfigError` naming *holder*
    instead of blocking every later run forever. A non-contention flock error
    (a directory the caller may not open, for example) is a :class:`ConfigError`
    too; closing the descriptor releases the lock even when the body raised,
    and the kernel releases it when the process dies, SIGKILL included.
    """
    try:
        descriptor = os.open(
            lock_dir, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        )
    except OSError as exc:
        raise ConfigError(
            f"cannot lock {lock_dir} for the GTK selection: {exc}"
        ) from exc
    try:
        deadline = time.monotonic() + LOCK_TIMEOUT
        while True:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError as exc:
                if exc.errno == errno.EINTR:
                    continue
                if exc.errno not in (errno.EACCES, errno.EAGAIN):
                    raise ConfigError(
                        f"cannot lock {lock_dir} for the GTK selection: "
                        f"{exc}"
                    ) from exc
                if time.monotonic() >= deadline:
                    raise ConfigError(
                        f"gave up after {LOCK_TIMEOUT:g}s waiting for "
                        f"{holder}; nothing was changed"
                    )
                time.sleep(_LOCK_POLL)
        yield
    finally:
        # Closing the descriptor releases the lock even when the body raised.
        os.close(descriptor)


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
    with _exclusive_flock(
        lock_dir,
        f"another apply-gtk/remove-gtk to finish with {config_home}",
    ):
        yield


@contextlib.contextmanager
def _data_lock(data_home: Path) -> Iterator[None]:
    """Serialize an apply's sheet check and selection with make install/uninstall.

    ``make install`` and ``make uninstall`` hold an exclusive flock on the
    data home for their whole run (the Makefile's ``run_locked``). An apply
    checks that both installed sheets exist and then publishes a selection
    naming them; without this lock an uninstall running concurrently could
    remove the sheets between the check and the write, and the apply would
    still report success while the selection named sheets that no longer
    exist. Locking the data home itself -- the same inode the Makefile locks
    -- makes an install or uninstall wait for the whole apply, and the
    re-check under the lock catches sheets an uninstall removed before this
    run took the lock. The data home already exists here (the sheet check
    found both sheets under it); a data home that vanishes anyway refuses the
    lock rather than being created. The timeout and error behavior are the
    config lock's.
    """
    with _exclusive_flock(
        data_home, f"another install or uninstall to finish with {data_home}"
    ):
        yield


def _installed_sheet(data_home: Path, version: str) -> Path:
    """Return the installed GTK *version* sheet below *data_home*."""
    return data_home / "themes" / GTK_ID / version / "gtk.css"


def _require_home(path: Path | None, variable: str, fallback: str) -> Path:
    """Return *path*, or refuse naming the unusable XDG *variable*.

    *fallback* is the ``$HOME``-relative path the XDG spec falls back to,
    included in the diagnostic so the user can see which directory could not
    be resolved. Every caller resolves its path through
    :mod:`tools.xdg_homes` and must refuse rather than guess where to write,
    so the diagnostic lives here once.
    """
    if path is None:
        raise ConfigError(
            f"{variable} is unset or not absolute and HOME cannot provide "
            f"{fallback}; set {variable} to an absolute path or export an "
            "absolute HOME"
        )
    return path


def _installed_sheets(data_home: Path) -> dict[str, Path] | None:
    """Return both installed sheets, or report the first one missing.

    Both settings files name our theme, so both sheets must exist: selecting
    a GTK 3 theme whose sheet is absent would silently leave GTK 3 unstyled.
    A missing sheet is reported here, before any lock or directory is taken,
    so a failed apply leaves no config home behind.
    """
    sheets = {}
    for version in ("gtk-4.0", "gtk-3.0"):
        sheet = _installed_sheet(data_home, version)
        if not sheet.is_file():
            report_failure(
                TOOL,
                f"installed {version} sheet is missing: {sheet}; "
                "run make install-gtk",
            )
            return None
        sheets[version] = sheet
    return sheets


def _apply(sheets: dict[str, Path], config_home: Path) -> int:
    """Select our GTK themes in both settings files and the user CSS."""
    sheet = sheets["gtk-4.0"]
    # Read every settings and user-CSS file before writing any, so an
    # unreadable file leaves every file unmodified instead of applying half
    # the selection.
    writes = []
    for version in ("gtk-3.0", "gtk-4.0"):
        path = settings_path(config_home, version)
        original = read_config_text(path) or ""
        updated = set_theme_name(original, GTK_ID)
        if updated != original:
            writes.append((path, updated))
    css = user_css_write(config_home, sheet, _note)
    if css is not None:
        writes.append(css)
    # A symlinked config path is the user's link, not ours: refuse it before
    # staging any write instead of replacing the link with a regular file.
    for path, _text in writes:
        refuse_symlink(path, "write", ConfigError)
    # A settings file at the read cap can grow past it when our longer value
    # replaces a shorter foreign one. Refuse before staging, or a later apply
    # or removal would refuse the file this run wrote.
    for path, text in writes:
        if len(text.encode("utf-8")) > MAX_CONFIG_FILE_BYTES:
            raise ConfigError(
                f"{path} would grow past the {MAX_CONFIG_FILE_BYTES}-byte "
                "limit this tool reads; refusing to write it"
            )
    # Stage every write before replacing anything: an unwritable settings
    # file or user CSS leaves all of them unmodified.
    commit(stage_all(writes))
    return 0


def _remove(config_home: Path) -> int:
    """Clear our selection from both settings files and the user CSS."""
    writes = []
    for version in ("gtk-3.0", "gtk-4.0"):
        path = settings_path(config_home, version)
        original = read_config_text(path)
        if original is None:
            continue
        updated, removed = remove_theme_name(original)
        if removed:
            writes.append((path, updated))
    css = user_css_remove(config_home)
    removals = [css] if css is not None else []
    # A symlinked config path is the user's link, not ours: refuse it before
    # staging any write or removal instead of replacing or deleting the link.
    for path, _text in writes:
        refuse_symlink(path, "remove", ConfigError)
    for path in removals:
        refuse_symlink(path, "remove", ConfigError)
    # Replace the settings and delete the user CSS in one commit: a failure in
    # either step restores every file changed so far, including the CSS.
    commit(staged=stage_all(writes), removals=removals)
    return 0


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
                xdg_homes.config_home(env),
                "XDG_CONFIG_HOME",
                "$HOME/.config",
            )
            with _config_lock(config_home):
                status = _remove(config_home)
        else:
            config_home = _require_home(
                xdg_homes.config_home(env),
                "XDG_CONFIG_HOME",
                "$HOME/.config",
            )
            data_home = _require_home(
                xdg_homes.data_home(env),
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
            with _data_lock(data_home):
                sheets = _installed_sheets(data_home)
                if sheets is None:
                    return 1
                with _config_lock(config_home):
                    status = _apply(sheets, config_home)
    except ConfigError as exc:
        return report_error(TOOL, str(exc))
    if status == 0:
        _note("restart running GTK applications to pick up the theme")
    return status


if __name__ == "__main__":
    sys.exit(main())
