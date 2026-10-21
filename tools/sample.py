"""Print the RGB and hex value of one pixel in a reference screenshot.

The reference screenshots are the source of truth for the theme's palette and
metrics, so each palette or metric value is pinned by reading a pixel from
one. This tool makes that sampling a command: it reads the image through
``tools/png/read.py`` so the same LFS-aware ``read_png`` and bounds-checked
``pixel_at`` apply, decoding only the rows through the sampled rectangle, then
prints the pixel in the two forms the theme files use -- the ``R,G,B`` triple
copied into a ``.colors`` file and the ``#RRGGBB`` literal copied into an SVG
or QML file. ``--width``/``--height`` extend that
from one pixel to a rectangle (default 1x1), printed row-major, so grounding a
title bar's column or a widget's box takes one command instead of one per
pixel. Only the rows through the sampled rectangle are decoded; the full
height printed in the header comes from ``read_png_size``.
"""

from __future__ import annotations

import sys

if __package__:
    from tools.argument_parsing import (
        EscapingArgumentParser,
        plain_number,
        positive_int,
    )
    from tools.diagnostics import report_error
    from tools.png import PngError, pixel_at, read_png, read_png_size
    from tools.terminal import escape_controls
else:  # run directly: python3 tools/sample.py
    from argument_parsing import (
        EscapingArgumentParser,
        plain_number,
        positive_int,
    )
    from diagnostics import report_error
    from png import PngError, pixel_at, read_png, read_png_size
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

    try:
        # Decode only through the rectangle's bottom row; the sampled pixels
        # are all in the top y+height rows, so the rest of a large reference
        # need not be unfiltered. A negative y makes the bound non-positive,
        # so clamp it: the rectangle's out-of-bounds diagnostic below still
        # names the full image size, and one row is enough to reach it.
        image = read_png(args.image, max_rows=max(1, args.y + args.height))
        width, height = read_png_size(args.image)
    except PngError as exc:
        return report_error("sample", str(exc))

    header = f"image: {escape_controls(args.image)}  {width}x{height}"
    if args.width == 1 and args.height == 1:
        # The decoded image is truncated at y+1, so validate the coordinate
        # against the size the header declares; the message matches pixel_at's
        # out-of-image diagnostic.
        if not (0 <= args.x < width and 0 <= args.y < height):
            return report_error(
                "sample",
                f"pixel ({args.x}, {args.y}) is outside the "
                f"{width}x{height} image",
            )
        rgb = pixel_at(image, args.x, args.y)
        print(header)
        print(
            f"pixel ({args.x}, {args.y}): "
            f"{rgb[0]},{rgb[1]},{rgb[2]}  {_hex(rgb)}"
        )
        return 0

    # Validate the whole rectangle before sampling any pixel: a region whose
    # origin is negative or that runs past the right or bottom edge must
    # produce one region diagnostic, not a pixel diagnostic for its origin and
    # not a partial dump followed by pixel_at's error on a later coordinate.
    if (
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

    print(header)
    print(f"region ({args.x}, {args.y}) {args.width}x{args.height}:")
    for y in range(args.y, args.y + args.height):
        for x in range(args.x, args.x + args.width):
            r, g, b = pixel_at(image, x, y)
            print(f"({x}, {y}): {r},{g},{b}  {_hex((r, g, b))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
