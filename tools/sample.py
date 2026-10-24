"""Print the RGB and hex value of one pixel in a reference screenshot.

The reference screenshots are the source of truth for the theme's palette and
metrics, so each palette or metric value is pinned by reading a pixel from
one. This tool makes that sampling a command: it reads the image through
``tools/png/loader.py`` so the same LFS-aware ``read_png`` and bounds-checked
``pixel_at`` apply, decoding only the rows through the sampled rectangle, then
prints the pixel in the two forms the theme files use -- the ``R,G,B`` triple
copied into a ``.colors`` file and the ``#RRGGBB`` literal copied into an SVG
or QML file. ``--width``/``--height`` extend that
from one pixel to a rectangle (default 1x1), printed row-major, so grounding a
title bar's column or a widget's box takes one command instead of one per
pixel. The header is read first and the requested pixel or region is validated
against the declared size, so an out-of-bounds request never reaches the row
decoder; only the rows through a valid rectangle are decoded, and the full
height printed in the header comes from ``read_png_size``. An image path
inside the repository is checked through the shared containment guard, so a
checked-in symlink that escapes the repository is refused instead of sampling
a private image's pixels.

Exit status: 0 on success (and for ``--help``/``-h``), 2 for a usage error, a
missing or unreadable PNG, a repository image path that resolves outside the
repository, or a coordinate or region outside the image.
"""

from __future__ import annotations

import os
from pathlib import Path

import sys

if __package__:
    from tools.argument_parsing import (
        EscapingArgumentParser,
        plain_number,
        positive_int,
    )
    from tools.containment import resolves_within
    from tools.diagnostics import report_error
    from tools.png import PngError, pixel_at, read_png, read_png_size
    from tools.repo_root import ROOT
    from tools.terminal import escape_controls
else:  # run directly: python3 tools/sample.py
    from argument_parsing import (
        EscapingArgumentParser,
        plain_number,
        positive_int,
    )
    from containment import resolves_within
    from diagnostics import report_error
    from png import PngError, pixel_at, read_png, read_png_size
    from repo_root import ROOT
    from terminal import escape_controls


def _hex(rgb: tuple[int, int, int]) -> str:
    """Return the ``#RRGGBB`` form of *rgb*, zero-padding each channel."""
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def main(argv: list[str] | None = None) -> int:
    """Run the sampling CLI; *argv* is the argument list without a program name.

    Following ``argparse`` and the sibling ``tools/fidelity.py``, ``None``
    reads ``sys.argv``.
    """
    parser = EscapingArgumentParser(
        prog="sample",
        description="Print a reference screenshot pixel's RGB and hex value.",
        epilog="exit status: 0 on success, 2 usage or read error",
    )
    parser.add_argument("image", help="reference image (PNG)")
    parser.add_argument(
        "x",
        type=lambda value: plain_number(value, "x", "integer", "an", int),
        help="pixel column",
    )
    parser.add_argument(
        "y",
        type=lambda value: plain_number(value, "y", "integer", "an", int),
        help="pixel row",
    )
    parser.add_argument(
        "--width",
        type=positive_int("--width"),
        default=1,
        metavar="W",
        help="pixels to sample to the right of x (default 1)",
    )
    parser.add_argument(
        "--height",
        type=positive_int("--height"),
        default=1,
        metavar="H",
        help="pixels to sample below y (default 1)",
    )
    args = parser.parse_args(argv)

    # The documented workflow samples a name in the contributor-supplied
    # reference directory, and git stores symlinks. Opening a checked-in link
    # that resolves outside the repository would read a private image and
    # print its pixels, so refuse such a path before either read. The path is
    # deliberately not normalized (``..`` is kept, as the OS follows it after
    # resolving the links before it), and any ancestor that is the checkout
    # itself, through an alias or not, marks it a repository path. A path
    # outside the repository (a test's temporary image) is left alone.
    image = Path(os.path.join(os.getcwd(), args.image))
    for ancestor in (image, *image.parents):
        try:
            in_repo = os.path.samefile(ancestor, ROOT)
        except OSError:
            continue
        if in_repo:
            if not resolves_within(ROOT, image):
                return report_error(
                    "sample",
                    f"{args.image} resolves outside {ROOT} (a symlink "
                    "escape); refusing to read it",
                )
            break

    try:
        width, height = read_png_size(args.image)
    except PngError as exc:
        return report_error("sample", str(exc))

    header = f"image: {escape_controls(args.image)}  {width}x{height}"
    if args.width == 1 and args.height == 1:
        # Validate the coordinate against the size the header declares before
        # calling the row decoder; the message matches pixel_at's out-of-image
        # diagnostic.
        if not (0 <= args.x < width and 0 <= args.y < height):
            return report_error(
                "sample",
                f"pixel ({args.x}, {args.y}) is outside the "
                f"{width}x{height} image",
            )
    # Validate the whole rectangle before sampling any pixel: a region whose
    # origin is negative or that runs past the right or bottom edge must
    # produce one region diagnostic, not a pixel diagnostic for its origin and
    # not a partial dump followed by pixel_at's error on a later coordinate.
    elif (
        args.x < 0
        or args.y < 0
        or args.x + args.width > width
        or args.y + args.height > height
    ):
        return report_error(
            "sample",
            f"region ({args.x}, {args.y}) "
            f"{args.width}x{args.height} is outside the "
            f"{width}x{height} image",
        )

    try:
        # Decode only through the rectangle's bottom row; the sampled pixels
        # are all in the top y+height rows, so the rest of a large reference
        # need not be unfiltered. The validation above guarantees y is
        # non-negative, so the bound is at least one row.
        image = read_png(args.image, max_rows=args.y + args.height)
    except PngError as exc:
        return report_error("sample", str(exc))

    if args.width == 1 and args.height == 1:
        rgb = pixel_at(image, args.x, args.y)
        print(header)
        print(
            f"pixel ({args.x}, {args.y}): "
            f"{rgb[0]},{rgb[1]},{rgb[2]}  {_hex(rgb)}"
        )
        return 0

    print(header)
    print(f"region ({args.x}, {args.y}) {args.width}x{args.height}:")
    for y in range(args.y, args.y + args.height):
        for x in range(args.x, args.x + args.width):
            r, g, b = pixel_at(image, x, y)
            print(f"({x}, {y}): {r},{g},{b}  {_hex((r, g, b))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
