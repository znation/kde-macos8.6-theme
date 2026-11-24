"""The bounded reader for small user settings files, and its refusal type.

The selection and diagnostics tools read the user's small settings files
(``kdeglobals``, ``kvconfig``, the GTK ``settings.ini`` files): each read
opens the path once and inspects the opened descriptor, so a regular file
swapped for a FIFO is refused instead of blocking on a writer that never
comes, and at most one byte past ``MAX_CONFIG_FILE_BYTES`` is read, so a
corrupt or hostile file cannot exhaust memory.

:class:`ConfigError` is the shared refusal type of the tools that read or
rewrite those files and the GTK user CSS (the GTK selection and staging,
the Kvantum selection, the render session's scratch config writes): its
message names the offending path and the underlying error, so ``main``
can report one diagnostic line instead of letting a bare ``OSError`` or
``UnicodeDecodeError`` traceback escape. Each family's writer lives in its
own module (``tools/gtk/user_files.py``, ``tools/firefox/user_files.py``).
"""

from __future__ import annotations

import errno
import os
import stat
from pathlib import Path


class ConfigError(Exception):
    """A user settings or user-CSS file could not be read or written.

    The message names the offending path and the underlying error, so
    ``main`` can report it as the one-line diagnostic instead of letting a
    bare ``OSError`` or ``UnicodeDecodeError`` traceback escape. A decoder's
    own error names the byte that failed but not the file it came from.
    """


# Settings and user-CSS files are small user files; anything larger is
# refused rather than loaded, so a corrupt or hostile file cannot exhaust
# memory.
MAX_CONFIG_FILE_BYTES = 1 << 20


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
        try:
            os.close(descriptor)
        except OSError as exc:
            raise ConfigError(f"cannot close {path}: {exc}") from exc
