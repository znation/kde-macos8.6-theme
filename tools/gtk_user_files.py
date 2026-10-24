"""The GTK settings and user-CSS files the selection reads and writes.

The opt-in GTK selection touches three files under the user's config home:
``gtk-3.0/settings.ini`` and ``gtk-4.0/settings.ini``, whose
``gtk-theme-name`` line is edited, and ``gtk-4.0/gtk.css``, the libadwaita
user stylesheet that imports the installed GTK 4 sheet. This module holds
where those files live, the bounded non-blocking read they share, and the
marker policy for the user stylesheet: an empty file is adopted, our
marker-led file is rewritten, and a foreign file is left untouched.

:class:`ConfigError` is the GTK selection's refusal type: every read, write
and removal below raises it, and so do the staging and workflow modules, so
``main`` can report one ``apply_gtk: error:`` line instead of letting a bare
``OSError`` or ``UnicodeDecodeError`` traceback escape. The text transforms
live in ``tools/gtk_settings.py``, the staged publication in
``tools/gtk_staging.py`` and the selection workflow in ``tools/apply_gtk.py``.
"""

from __future__ import annotations

import errno
import os
import stat
from collections.abc import Callable
from pathlib import Path


class ConfigError(Exception):
    """A GTK settings or user-CSS file could not be read or written.

    The message names the offending path and the underlying error, so
    ``main`` can report it as the one-line diagnostic instead of letting a
    bare ``OSError`` or ``UnicodeDecodeError`` traceback escape. A decoder's
    own error names the byte that failed but not the file it came from.
    """


# GTK settings and user CSS are small user files; anything larger is refused
# rather than loaded, so a corrupt or hostile file cannot exhaust memory.
MAX_CONFIG_FILE_BYTES = 1 << 20

GTK4_CSS_MARKER = "/* org.macos8.desktop GTK 4 user CSS */"


def read_config_text(path: Path) -> str | None:
    """Return *path*'s UTF-8 text, or ``None`` when nothing occupies it.

    The read opens *path* once and inspects the opened descriptor: a regular
    file swapped for a FIFO before the open still returns at once because of
    ``O_NONBLOCK``, and is then refused as not a regular file instead of
    blocking or being consumed. A directory returns ``None`` so the staging
    step reports it as an unwritable target instead of this read path
    refusing it.

    The bytes are decoded directly rather than through ``Path.read_text``,
    whose universal-newline mode would turn CRLF and lone CR into LF before
    the transforms see them; every line ending must stay intact for a rewrite.
    At most one byte past ``MAX_CONFIG_FILE_BYTES`` is read, so an oversize
    file is refused by name instead of being loaded whole.
    """
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
    except (FileNotFoundError, NotADirectoryError):
        return None
    except OSError as exc:
        # Some platforms refuse to open a directory for reading at all.
        if exc.errno == errno.EISDIR:
            return None
        raise ConfigError(f"cannot read {path}: {exc}") from exc
    try:
        mode = os.fstat(descriptor).st_mode
        if stat.S_ISDIR(mode):
            return None
        if not stat.S_ISREG(mode):
            raise ConfigError(f"cannot read {path}: not a regular file")
        chunks = []
        remaining = MAX_CONFIG_FILE_BYTES + 1
        while remaining > 0:
            chunk = os.read(descriptor, min(remaining, 65536))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        data = b"".join(chunks)
        if len(data) > MAX_CONFIG_FILE_BYTES:
            raise ConfigError(
                f"{path} is larger than the {MAX_CONFIG_FILE_BYTES}-byte "
                "limit this tool reads; refusing to load it whole"
            )
        return data.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ConfigError(f"cannot read {path}: {exc}") from exc
    finally:
        os.close(descriptor)


def settings_path(config_home: Path, version: str) -> Path:
    """Return the ``gtk-3.0`` or ``gtk-4.0`` settings file below *config_home*."""
    return config_home / version / "settings.ini"


def user_css_path(config_home: Path) -> Path:
    """Return the libadwaita user stylesheet below *config_home*."""
    return config_home / "gtk-4.0" / "gtk.css"


def user_css_write(
    config_home: Path, sheet: Path, note: Callable[[str], None]
) -> tuple[Path, str] | None:
    """Return the ``(path, text)`` user-CSS write, or None to leave it alone.

    A foreign ``gtk.css`` is read and left untouched, and *note* reports that
    decision through the calling tool's own note channel. An empty file has
    no foreign content to preserve, so it is adopted (filled with our marker
    and import) instead of being mistaken for a foreign sheet. The read
    happens here, before any settings write, so an unreadable file changes
    nothing.
    """
    path = user_css_path(config_home)
    existing = read_config_text(path)
    if existing:
        first = existing.splitlines()
        if not first or first[0] != GTK4_CSS_MARKER:
            note(f"{path} exists but is not our user CSS; leaving it untouched")
            return None
    content = f'{GTK4_CSS_MARKER}\n@import url("{sheet.as_uri()}");\n'
    return path, content


def user_css_remove(config_home: Path) -> Path | None:
    """Return the marker-led user CSS to delete, or None to keep the file.

    The file is read here, before any settings write, so an unreadable
    ``gtk.css`` changes nothing.
    """
    path = user_css_path(config_home)
    existing = read_config_text(path)
    if existing is None:
        return None
    first = existing.splitlines()
    if first and first[0] == GTK4_CSS_MARKER:
        return path
    return None


def unlink(path: Path) -> None:
    """Delete *path*, reporting a failure by path."""
    try:
        path.unlink()
    except OSError as exc:
        raise ConfigError(f"cannot remove {path}: {exc}") from exc
