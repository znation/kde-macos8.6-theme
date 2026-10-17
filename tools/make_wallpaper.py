"""Generate the Mac OS 8.6 wallpaper package's images from the reference desktop.

The retail desktop screenshot ``desktop_betawiki.png`` shows the default desktop
pattern as a 128x128 tile anchored at screen (0, 0). This tool cuts one clean
tile out of a stretch of bare desktop and writes it tiled to full-screen PNGs,
one per resolution, under the wallpaper package's ``contents/images/``. Plasma
picks the image nearest the screen size, so a matching screen shows the tile 1:1.

Run ``python3 tools/make_wallpaper.py`` from anywhere; the output is
deterministic, so re-running rewrites identical bytes.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__:
    from tools.png import Image, PngError, read_png
    from tools.png_write import encode_png
else:  # run directly: python3 tools/make_wallpaper.py
    from png import Image, PngError, read_png
    from png_write import encode_png

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


def main() -> int:
    try:
        tile = tile_from_reference(read_png(ROOT / REFERENCE))
    except (PngError, ValueError) as exc:
        print(f"make_wallpaper: error: {exc}", file=sys.stderr)
        return 2
    images = ROOT / PACKAGE_DIR / "contents" / "images"
    images.mkdir(parents=True, exist_ok=True)
    for width, height in RESOLUTIONS:
        data = encode_png(width, height, tiled_rgb(tile, width, height))
        (images / f"{width}x{height}.png").write_bytes(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
