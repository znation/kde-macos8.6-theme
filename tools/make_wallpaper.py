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

import sys
from pathlib import Path

if __package__:
    from tools.argument_parsing import EscapingArgumentParser
    from tools.atomic_write import write_atomically
    from tools.containment import require_within_repo
    from tools.diagnostics import report_error
    from tools.png import Image, PngError, read_png
    from tools.png.write import encode_png
    from tools.ints import is_plain_int
    from tools.repo_root import ROOT
else:  # run directly: python3 tools/make_wallpaper.py
    from argument_parsing import EscapingArgumentParser
    from atomic_write import write_atomically
    from containment import require_within_repo
    from diagnostics import report_error
    from png import Image, PngError, read_png
    from png.write import encode_png
    from ints import is_plain_int
    from repo_root import ROOT

TOOL = "make_wallpaper"
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
    if not isinstance(image, Image):
        raise ValueError(
            f"tile_from_reference image must be an Image, not "
            f"{type(image).__name__}"
        )
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
    for name, value in (("width", width), ("height", height)):
        if not is_plain_int(value) or value < 1:
            raise ValueError(
                f"tiled_rgb {name} must be a positive integer: {name}={value!r}"
            )
    # ``tile`` must be a byte buffer: a str or list of the right length
    # would slice into the wrong type and fail later inside ``bytes.join``
    # with an opaque TypeError that named neither the field nor its type.
    # ``bytes`` and ``bytearray`` are both accepted, matching ``Image.rgb``.
    if not isinstance(tile, (bytes, bytearray)):
        raise ValueError(
            f"tiled_rgb tile must be bytes or bytearray, not "
            f"{type(tile).__name__}"
        )
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

    A crash mid-write leaves the previous wallpaper rather than a truncated
    PNG that a later ``make install`` would ship; see
    :func:`tools.atomic_write.write_atomically`.
    """
    write_atomically(path, lambda destination: destination.write(data))


def main(argv: list[str] | None = None) -> int:
    """Run the generator CLI; *argv* is the argument list without a program name.

    Following ``argparse`` and the sibling tools, ``None`` reads
    ``sys.argv``. The generator takes no options, but its command line is
    still parsed so a mistaken argument (``--help``, a typo, an old flag) is
    a diagnostic instead of being silently ignored while every checked-in
    wallpaper image is rewritten.
    """
    parser = EscapingArgumentParser(
        prog=TOOL,
        description=(
            "Regenerate the wallpaper package's images from the reference "
            "desktop screenshot."
        ),
        epilog=(
            "exit status: 0 when every image was written, "
            "2 on a usage or read/write error"
        ),
    )
    parser.parse_args(argv)
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
