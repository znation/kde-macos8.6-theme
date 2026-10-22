"""Generate the Mac OS 8.6 wallpaper package's images from the reference desktop.

The retail desktop screenshot ``desktop_betawiki.png`` shows the default desktop
pattern as a 128x128 tile anchored at screen (0, 0). This tool cuts one clean
tile out of a stretch of bare desktop and writes it tiled to full-screen PNGs,
one per resolution, under the wallpaper package's ``contents/images/``. Plasma
picks the image nearest the screen size, so a matching screen shows the tile 1:1.

Run ``python3 tools/make_wallpaper.py`` from anywhere; the output is
deterministic, so re-running rewrites identical bytes.

The reference screenshot is a repository file, and a checked-in symlink can
point anywhere on the machine. A reference that resolves outside the
repository is refused by name before it is decoded, so a private file's pixels
cannot be copied into the wallpaper package. The images directory the
generator writes into is a repository path as well, so one that resolves
outside the repository (a checked-in symlink) is refused by name before
anything is written: the wallpaper images stay in the wallpaper package.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

if __package__:
    from tools.containment import require_within_repo
    from tools.diagnostics import report_error
    from tools.png import Image, PngError, read_png
    from tools.png.write import encode_png
else:  # run directly: python3 tools/make_wallpaper.py
    from containment import require_within_repo
    from diagnostics import report_error
    from png import Image, PngError, read_png
    from png.write import encode_png

TOOL = "make_wallpaper"
ROOT = Path(__file__).resolve().parents[1]
REFERENCE = "macos8.6-screenshots/desktop_betawiki.png"
TILE_ORIGIN = (0, 128)
TILE_SIZE = 128
RESOLUTIONS = (
    (1024, 768),
    (1280, 800),
    (1280, 1024),
    (1366, 768),
    (1440, 900),
    (1600, 900),
    (1680, 1050),
    (1920, 1080),
    (1920, 1200),
    (2560, 1440),
    (2560, 1600),
    (3840, 2160),
)
PACKAGE_DIR = "theme/wallpapers/org.macos8.desktop"


def tile_from_reference(image: Image) -> bytes:
    """Return the 128x128 RGB block of *image* at ``TILE_ORIGIN``."""
    x0, y0 = TILE_ORIGIN
    if x0 + TILE_SIZE > image.width or y0 + TILE_SIZE > image.height:
        raise ValueError(
            f"the {TILE_SIZE}x{TILE_SIZE} tile at {TILE_ORIGIN} does not fit "
            f"in the {image.width}x{image.height} image"
        )
    rows = []
    for y in range(y0, y0 + TILE_SIZE):
        start = (y * image.width + x0) * 3
        rows.append(bytes(image.rgb[start : start + TILE_SIZE * 3]))
    return b"".join(rows)


def tiled_rgb(tile: bytes, width: int, height: int) -> bytes:
    """Return a *width* x *height* RGB image where pixel (x, y) is tile[y % 128][x % 128]."""
    row_bytes = TILE_SIZE * 3
    if len(tile) != TILE_SIZE * row_bytes:
        raise ValueError(
            f"tile has {len(tile)} bytes; a {TILE_SIZE}x{TILE_SIZE} RGB tile "
            f"needs {TILE_SIZE * row_bytes}"
        )
    repeats = -(-width // TILE_SIZE)
    rows = [
        (tile[i * row_bytes : (i + 1) * row_bytes] * repeats)[: width * 3]
        for i in range(TILE_SIZE)
    ]
    return b"".join(rows[y % TILE_SIZE] for y in range(height))


def _write_atomic(path: Path, data: bytes) -> None:
    """Write *data* to *path* so *path* is the old file or the whole new one.

    The bytes go to a sibling temporary file that is renamed over *path*, so a
    crash mid-write leaves the previous wallpaper rather than a truncated PNG
    that a later ``make install`` would ship. The temporary file is removed
    when the write fails.

    The temporary file's name is picked by :func:`tempfile.mkstemp`, which
    creates it exclusively: a fixed, guessable name would let another local
    user who can write the images directory park a symlink there first and
    make the write clobber whatever file it names. The bytes go through the
    file descriptor ``mkstemp`` returned rather than the path being reopened
    by name, so a path swapped after the exclusive create cannot redirect
    them.
    """
    descriptor, partial_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}-", suffix=".tmp"
    )
    partial = Path(partial_name)
    try:
        with os.fdopen(descriptor, "wb") as destination:
            # mkstemp opens the file 0600; the plain write this replaces
            # created it with the process umask applied, so restore that mode
            # before the rename leaves the image owner-only.
            umask = os.umask(0)
            os.umask(umask)
            os.chmod(destination.fileno(), 0o666 & ~umask)
            destination.write(data)
        os.replace(partial, path)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise


def main() -> int:
    """Write the tiled wallpaper PNG for every resolution; return 0, or 2 on error."""
    reference = ROOT / REFERENCE
    try:
        # The reference screenshot is a repository file, and a checked-in
        # symlink can point anywhere on the machine. Reading it through such a
        # symlink would decode a private file and copy its pixels into the
        # wallpaper package, which the next commit would publish. The shared
        # guard refuses a repository path that resolves outside the repository
        # before the image is decoded.
        require_within_repo(reference, ROOT)
        tile = tile_from_reference(read_png(reference))
    except (PngError, ValueError) as exc:
        return report_error(TOOL, str(exc))
    images = ROOT / PACKAGE_DIR / "contents" / "images"
    try:
        # The images directory is a repository path too, and a checked-in
        # symlink can point anywhere on the machine: writing through it would
        # put the wallpaper images outside the wallpaper package, into a
        # directory a contributor names, and overwrite same-named files
        # there. The shared guard refuses a repository path that resolves
        # outside the repository before anything is written.
        require_within_repo(images, ROOT, action="write")
    except ValueError as exc:
        return report_error(TOOL, str(exc))
    try:
        images.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return report_error(TOOL, f"cannot create {images}: {exc}")
    for width, height in RESOLUTIONS:
        data = encode_png(width, height, tiled_rgb(tile, width, height))
        target = images / f"{width}x{height}.png"
        try:
            _write_atomic(target, data)
        except OSError as exc:
            return report_error(TOOL, f"cannot write {target}: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
