"""Cross-process on-disk cache for decoded reference PNG planes.

Every ``make check`` worker process decodes the same read-only reference
screenshots its modules sample: the in-process cache in
``support/reference_image.py`` cannot share a decode across workers, so a
bounded ``desktop_fandom.png`` decode (~0.5 s) runs once per worker that
touches it. This module stores each decode's planes under the XDG cache home
(the same home the durations cache uses), keyed by the PNG's content hash and
decode shape, so the first worker decodes and the rest read planes back.

The key hashes the file content: a reference is a read-only Git LFS asset,
but re-materialization or a changed checkout must never be served a stale
decode. Errors are not cached -- an unmaterialized LFS pointer fails fast,
caching it would buy nothing -- and every bad cache state (missing, truncated,
malformed entry) falls back to a fresh decode, so the cache can only save
time, never change what a caller sees.
"""

from __future__ import annotations

import hashlib
import os
import struct
import time
from pathlib import Path

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.atomic_write import write_bytes_atomically  # noqa: E402
from tools.xdg_homes import cache_home  # noqa: E402

from tools import png  # noqa: E402

# One entry: the magic pins the layout version, then the image geometry and
# the colour-plane length, then the packed planes. The alpha plane, when the
# decode has one, is the tail after the RGB plane.
_HEADER = struct.Struct(">8sQQQ?")
_MAGIC = b"KREFDC01"

# Cache dir, shared with the durations cache's XDG resolution (xdg_homes.cache_home).
_CACHE_DIR = ("kde-macos8.6-theme", "reference-decodes")

# Entries last written more than this long ago are pruned whenever a new one
# is written, so a changed reference set or retired decode shape cannot grow
# the cache forever. A read never touches an entry's mtime, so pruning is by
# last write: an entry read every day is still pruned (and re-decoded on its
# next read) once it is this old.
_MAX_AGE_SECONDS = 30 * 24 * 60 * 60


def cache_dir() -> str:
    """Return the decode cache's directory under the XDG cache home."""
    return str(cache_home().joinpath(*_CACHE_DIR))


def _content_hash(path) -> str:
    """Hash the PNG bytes at *path*; raises ``OSError`` when unreadable."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _entry_name(content_hash: str, alpha, max_rows, max_cols) -> str:
    """Name one (content, shape) entry; ``n`` marks an unbounded row/column."""
    row = "n" if max_rows is None else str(max_rows)
    col = "n" if max_cols is None else str(max_cols)
    return f"{content_hash}-a{int(alpha)}-r{row}-c{col}.bin"


def _pack(image: png.Image) -> bytes:
    """Serialize a decoded image's planes."""
    has_alpha = image.alpha is not None
    alpha = image.alpha or b""
    return _HEADER.pack(_MAGIC, image.width, image.height, len(image.rgb),
                        has_alpha) + image.rgb + alpha


def _unpack(data: bytes):
    """Rebuild an image from an entry, or return ``None`` for any bad state."""
    try:
        magic, width, height, rgb_len, has_alpha = _HEADER.unpack_from(data)
    except struct.error:
        return None
    if magic != _MAGIC:
        return None
    rgb_end = _HEADER.size + rgb_len
    rgb = data[_HEADER.size:rgb_end]
    alpha = data[rgb_end:] if has_alpha else None
    try:
        # ``png.Image`` rejects a plane that does not match its dimensions, so
        # a truncated or overlong entry (trailing junk included) raises here.
        return png.Image(width, height, rgb, alpha)
    except png.PngError:
        return None


def _read_entry(path: str):
    """Return the cached image at *path*, or ``None`` on any bad state."""
    try:
        with open(path, "rb") as handle:
            data = handle.read()
    except OSError:
        return None
    return _unpack(data)


def _prune_stale(directory: str) -> None:
    """Drop entries last written more than _MAX_AGE_SECONDS ago.

    Every failure is ignored; pruning is best effort.
    """
    cutoff = time.time() - _MAX_AGE_SECONDS
    try:
        with os.scandir(directory) as entries:
            for entry in entries:
                # A concurrent writer's temp file has a fresh mtime, so it is
                # never pruned; only genuinely stale entries are dropped.
                if not entry.is_file():
                    continue
                try:
                    if entry.stat().st_mtime < cutoff:
                        os.unlink(entry.path)
                except OSError:
                    continue
    except OSError:
        pass


def load(path, *, alpha, max_rows, max_cols, decode):
    """Return the decode of *path* for this shape, via the disk cache.

    *decode* is a zero-argument callable producing the image (a fresh
    ``png.read_png`` call). On a cache miss it runs and its result is stored;
    on a hit it does not run. Every cache failure falls back to *decode*, so
    the returned image is always the one a fresh decode of *path* produces.
    ``PngError`` from *decode* propagates to the caller; errors are never
    stored.
    """
    directory = cache_dir()
    try:
        content_hash = _content_hash(path)
    except OSError:
        return decode()
    entry = os.path.join(directory, _entry_name(content_hash, alpha,
                                                max_rows, max_cols))
    cached = _read_entry(entry)
    if cached is not None:
        return cached
    image = decode()
    try:
        os.makedirs(directory, exist_ok=True)
        write_bytes_atomically(Path(entry), _pack(image))
    except OSError:
        return image
    _prune_stale(directory)
    return image
