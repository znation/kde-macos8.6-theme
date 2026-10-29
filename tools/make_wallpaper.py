"""Generate the Platinum wallpaper package's original neutral placeholder.

The tool writes a 128x128 solid ``#CCCCCC`` tile tiled to full-screen PNGs,
one per resolution, under the wallpaper package's ``contents/images/``. Plasma
picks the image nearest the screen size, so a matching screen shows the tile 1:1.

Run ``python3 tools/make_wallpaper.py`` from anywhere; the output is
deterministic, so re-running rewrites identical bytes.

The images directory the generator writes into is a repository path; one that
resolves outside the repository (a checked-in symlink) is refused by name
before anything is written.

Exit status: 0 when every image was written (and for ``--help``/``-h``), 2 for
a usage error, a reference or images directory that resolves outside the
repository, or a reference, directory or file that cannot be read, created or
written.
"""

from __future__ import annotations

import sys

if __package__:
    from tools.argument_parsing import EscapingArgumentParser
    from tools.generated_files import write_generated_files
    from tools.png.write import encode_png
    from tools.ints import is_plain_int
    from tools.repo_root import ROOT
else:  # run directly: python3 tools/make_wallpaper.py
    from argument_parsing import EscapingArgumentParser
    from generated_files import write_generated_files
    from png.write import encode_png
    from ints import is_plain_int
    from repo_root import ROOT

TOOL = "make_wallpaper"
TILE_SIZE = 128
TILE_ORIGIN = (0, 128)  # legacy test fixture coordinates; generation does not read them
REFERENCE = "macos8.6-screenshots/desktop_betawiki.png"
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


TILE_RGB = bytes((0xCC, 0xCC, 0xCC)) * (TILE_SIZE * TILE_SIZE)


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
        description="Regenerate the original neutral placeholder wallpaper images.",
        epilog=(
            "exit status: 0 when every image was written, "
            "2 on a usage or read/write error"
        ),
    )
    parser.parse_args(argv)
    images = ROOT / PACKAGE_DIR / "contents" / "images"
    # The images directory is a repository path, and a checked-in symlink
    # can point anywhere on the machine: writing through it would put the
    # wallpaper images outside the wallpaper package, into a directory a
    # contributor names, and overwrite same-named files there. The shared
    # publisher refuses a repository path that resolves outside the
    # repository before anything is written.
    files = [
        (
            images / f"{width}x{height}.png",
            encode_png(width, height, tiled_rgb(TILE_RGB, width, height)),
        )
        for width, height in RESOLUTIONS
    ]
    return write_generated_files(TOOL, ROOT, images, files)


if __name__ == "__main__":
    sys.exit(main())
