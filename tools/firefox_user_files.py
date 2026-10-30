"""The Firefox profile files the installer reads and writes.

``make install-firefox`` touches three files in one opt-in Firefox profile:
``chrome/userChrome.css`` and ``chrome/userContent.css``, the two Platinum
sheets it copies, and ``user.js``, the preference file whose marker block it
adds or removes. This module holds where those files live, the bounded
non-blocking read they share, and the atomic write that publishes them.

:class:`ConfigError` is the Firefox install's refusal type: every read and
write below raises it, and so do profile discovery and the install workflow,
so ``main`` can report one ``install_firefox: error:`` line instead of letting
a bare ``OSError`` or ``UnicodeDecodeError`` traceback escape. Profile
discovery lives in ``tools/firefox_profile.py``, the ``user.js`` marker-block
transform in ``tools/firefox_user_js.py``, transaction recovery in
``tools/firefox_transaction.py`` and install/remove policy in
``tools/install_firefox.py``.
"""

from __future__ import annotations

from pathlib import Path

if __package__:
    from tools.atomic_write import write_atomically
    from tools.containment import read_capped_bytes
else:  # imported from a directly run tool
    from atomic_write import write_atomically
    from containment import read_capped_bytes


class ConfigError(Exception):
    """A profile or file cannot be used; the installer reports it by name."""


# A profile file is read only to compare its first line or to append one
# marker block, so a real userChrome.css/user.js is a few kilobytes. The path
# is the user's and can name something arbitrarily large (a generated user.js
# or a wrong file dropped in the profile); a plain read() would allocate the
# whole file, and a MemoryError is not an OSError, so it would escape as a
# traceback instead of the documented exit-2 diagnostic. Bound the read the
# way containment, reference_validation and local_hook bound theirs.
MAX_PROFILE_FILE_BYTES = 1 << 20


def user_chrome_path(profile: Path) -> Path:
    """Return *profile*'s ``chrome/userChrome.css`` path."""
    return profile / "chrome" / "userChrome.css"


def user_content_path(profile: Path) -> Path:
    """Return *profile*'s ``chrome/userContent.css`` path."""
    return profile / "chrome" / "userContent.css"


def user_js_path(profile: Path) -> Path:
    """Return *profile*'s ``user.js`` path."""
    return profile / "user.js"


def read_profile_text(path: Path) -> str | None:
    """Return *path*'s UTF-8 text, or ``None`` when it does not exist.

    The file is opened through the shared regular-file reader, so a FIFO or
    device at the path is refused by name instead of blocking the install on
    an open that waits for a writer, and the check inspects the opened
    descriptor. A directory, a non-regular file, an unreadable file and
    invalid UTF-8 are reported by name as a :class:`ConfigError` rather than
    escaping as a traceback. At most one byte past
    ``MAX_PROFILE_FILE_BYTES`` is read, so an oversize profile file is
    refused by name instead of being loaded whole.
    """
    try:
        data = read_capped_bytes(
            path,
            MAX_PROFILE_FILE_BYTES,
            "this installer reads; refusing to load it whole",
            missing_ok=True,
            error=ConfigError,
        )
    except (OSError, ValueError) as exc:
        raise ConfigError(f"cannot read {path}: {exc}") from exc
    if data is None:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ConfigError(f"cannot read {path}: {exc}") from exc


def write_profile_bytes(path: Path, data: bytes) -> None:
    """Publish *data* at *path*, reporting a write failure by path."""
    try:
        write_atomically(path, lambda handle: handle.write(data))
    except OSError as exc:
        raise ConfigError(f"cannot write {path}: {exc}") from exc


def write_profile_text(path: Path, text: str) -> None:
    """Publish *text* as UTF-8 at *path*, reporting a write failure by path."""
    write_profile_bytes(path, text.encode("utf-8"))
