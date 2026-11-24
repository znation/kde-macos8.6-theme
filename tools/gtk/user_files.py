"""The GTK settings and user-CSS files the selection reads and writes.

The GTK selection touches three files under the user's config home:
``gtk-3.0/settings.ini`` and ``gtk-4.0/settings.ini``, whose
``gtk-theme-name`` line is edited, and ``gtk-4.0/gtk.css``, the libadwaita
user stylesheet that imports the installed GTK 4 sheet. This module holds
where those files live, and the marker policy for the user stylesheet: an
empty file is adopted, our marker-led file is rewritten, and a foreign file
is copied to an unused ``.bak`` sibling before it is replaced.

:class:`~tools.config_read.ConfigError` is the selection's refusal type,
shared with the Kvantum selection and the render session: every read and
write below raises it, and so do the staging and workflow modules, so
``main`` can report one ``apply_gtk: error:`` line instead of letting a bare
``OSError`` or ``UnicodeDecodeError`` traceback escape. The bounded
non-blocking read the settings files share lives in
``tools/config_read.py``, the text transforms in
``tools/gtk/settings.py``, the staged publication in
``tools/gtk/staging.py`` and the selection workflow in
``tools/gtk/selection.py``.
"""

from __future__ import annotations

import os
from pathlib import Path

if __package__ == "tools.gtk":
    from tools.config_read import ConfigError, read_config_text
    from tools.text_lines import has_first_line_marker
else:  # imported from a directly run tool
    from config_read import ConfigError, read_config_text
    from text_lines import has_first_line_marker

GTK4_CSS_MARKER = "/* org.macos8.desktop GTK 4 user CSS */"

# A foreign stylesheet is copied beside itself under this suffix before it is
# replaced. The plain name is tried first; an existing backup is never
# overwritten, so later suffixes (``gtk.css.bak.1`` and up) keep every copy
# the user already has.
USER_CSS_BACKUP_SUFFIX = ".bak"
_BACKUP_NAME_ATTEMPTS = 100


def _is_our_user_css(text: str) -> bool:
    """Return whether *text*'s first line is our marker.

    A UTF-8 BOM is valid in CSS and some editors add one, so it must not hide
    the marker and make our own generated stylesheet look foreign. Lines end
    at LF, CR and CRLF only (``tools/text_lines.py``): an exotic Unicode
    separator inside the first line is part of that line, so text whose
    first line merely starts with our marker text is not the marker-led
    file. ``split_lines`` never returns an empty list, so an empty text is
    an empty first line, not the marker.
    """
    return has_first_line_marker(text, GTK4_CSS_MARKER)


def settings_path(config_home: Path, version: str) -> Path:
    """Return the ``gtk-3.0`` or ``gtk-4.0`` settings file below *config_home*."""
    return config_home / version / "settings.ini"


def user_css_path(config_home: Path) -> Path:
    """Return the libadwaita user stylesheet below *config_home*."""
    return config_home / "gtk-4.0" / "gtk.css"


def _backup_failure(path: Path, backup: Path, exc: OSError) -> ConfigError:
    """Return the refusal for a failed copy of *path* into *backup*.

    Used for the three write failures in :func:`user_css_backup` (opening
    the exclusive backup, wrapping its descriptor, and writing the bytes).
    """
    return ConfigError(f"cannot back up {path} to {backup}: {exc}")


def _discard_backup(path: Path) -> str | None:
    """Remove a partial backup, returning a diagnostic if it remains."""
    try:
        path.unlink()
    except FileNotFoundError:
        return None
    except OSError as exc:
        return f"cannot remove partial backup {path}: {exc}"
    return None


def _backup_failure_after_cleanup(
    path: Path, backup: Path, exc: OSError
) -> ConfigError:
    """Report the copy error and any partial-backup cleanup failure."""
    failure = _backup_failure(path, backup, exc)
    cleanup = _discard_backup(backup)
    if cleanup is not None:
        return ConfigError(f"{failure}; {cleanup}")
    return failure


def _close_quietly(descriptor: int) -> None:
    """Close *descriptor*, ignoring a close that fails."""
    try:
        os.close(descriptor)
    except OSError:
        pass


def user_css_backup(path: Path) -> Path:
    """Copy the user stylesheet at *path* to an unused ``.bak`` sibling.

    The copy is byte-for-byte (the text read is decoded as UTF-8 and encoded
    back, which round-trips a BOM and every line ending), so the backup is
    exactly what the apply replaced. The sibling is created exclusively at
    its final name, so a backup the user already keeps is never replaced; the
    next free ``.bak.N`` name is used instead. A failed copy removes the
    partial file and leaves *path* untouched.

    This is a copy, not a hard link: editing the live stylesheet afterwards
    must not change the backup.
    """
    text = read_config_text(path)
    if text is None:
        raise ConfigError(f"cannot back up {path}: it disappeared before the copy")
    data = text.encode("utf-8")
    for index in range(_BACKUP_NAME_ATTEMPTS):
        suffix = "" if index == 0 else f".{index}"
        backup = path.with_name(f"{path.name}{USER_CSS_BACKUP_SUFFIX}{suffix}")
        try:
            descriptor = os.open(
                backup, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666
            )
        except FileExistsError:
            continue
        except OSError as exc:
            raise _backup_failure(path, backup, exc) from exc
        try:
            destination = os.fdopen(descriptor, "wb")
        except OSError as exc:
            _close_quietly(descriptor)
            raise _backup_failure_after_cleanup(path, backup, exc) from exc
        except BaseException:
            _close_quietly(descriptor)
            _discard_backup(backup)
            raise
        try:
            with destination:
                destination.write(data)
        except OSError as exc:
            raise _backup_failure_after_cleanup(path, backup, exc) from exc
        except BaseException:
            _discard_backup(backup)
            raise
        return backup
    raise ConfigError(f"cannot find an unused backup name for {path}")


def user_css_write(
    config_home: Path, sheet: Path
) -> tuple[Path, str, Path | None] | None:
    """Return the ``(path, text, backup)`` user-CSS write, or None.

    A foreign ``gtk.css`` is replaced after it is copied, so *backup* names
    the file :func:`user_css_backup` must copy first; the caller does that
    after its symlink checks, so a refused link is never copied. An empty
    file has no foreign content to preserve, so it is adopted (filled with our
    marker and import) instead of being mistaken for a foreign sheet, and an
    absent file needs no backup; *backup* is ``None`` for both. The read
    happens here, before any settings write, so an unreadable file changes
    nothing.
    """
    path = user_css_path(config_home)
    existing = read_config_text(path)
    backup = path if existing and not _is_our_user_css(existing) else None
    content = f'{GTK4_CSS_MARKER}\n@import url("{sheet.as_uri()}");\n'
    return path, content, backup


def user_css_remove(config_home: Path) -> Path | None:
    """Return the marker-led user CSS to delete, or None to keep the file.

    The file is read here, before any settings write, so an unreadable
    ``gtk.css`` changes nothing.
    """
    path = user_css_path(config_home)
    existing = read_config_text(path)
    if existing is None:
        return None
    return path if _is_our_user_css(existing) else None
