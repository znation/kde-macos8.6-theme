"""Print the RGB and hex value of one pixel in a reference screenshot.

The reference screenshots are the source of truth for the theme's palette and
metrics, and PLANS.md samples their pixels by hand to pin each value. This
tool makes that sampling a command: it reads the image through ``tools/png.py``
so the same LFS-aware ``read_png`` and bounds-checked ``pixel_at`` apply, then
prints the pixel in the two forms the theme files use -- the ``R,G,B`` triple
copied into a ``.colors`` file and the ``#RRGGBB`` literal copied into an SVG
or QML file. ``--width``/``--height`` extend that from one pixel to a
rectangle (default 1x1), printed row-major, so grounding a title bar's column
or a widget's box takes one command instead of one per pixel.
"""

from __future__ import annotations

import argparse
import sys

if __package__:
    from tools.cli import EscapingArgumentParser, plain_number, report_error
    from tools.png import PngError, pixel_at, read_png
    from tools.terminal import escape_controls
else:  # run directly: python3 tools/sample.py
    from cli import EscapingArgumentParser, plain_number, report_error
    from png import PngError, pixel_at, read_png
    from terminal import escape_controls


def _hex(rgb: tuple[int, int, int]) -> str:
    """Return the ``#RRGGBB`` form of *rgb*, zero-padding each channel."""
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def _extent(value: str, option: str) -> int:
    """Return the positive pixel count *value*, naming *option* otherwise.

    ``--width`` and ``--height`` count pixels, so zero and negative are
    rejected with the option named instead of producing an empty or inverted
    region.
    """
    number = plain_number(value, option, "integer", "an", int)
    if number < 1:
        raise argparse.ArgumentTypeError(
            f"{option} must be at least 1: {value!r}"
        )
    return number


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
        type=lambda value: _extent(value, "--width"),
        default=1,
        metavar="W",
        help="pixels to sample to the right of x (default 1)",
    )
    parser.add_argument(
        "--height",
        type=lambda value: _extent(value, "--height"),
        default=1,
        metavar="H",
        help="pixels to sample below y (default 1)",
    )
    args = parser.parse_args(argv)

    try:
        image = read_png(args.image)
    except PngError as exc:
        return report_error("sample", str(exc))
    # pixel_at rejects a coordinate outside the image; it is operator input
    # here, not a caller bug, so report it as an error rather than a traceback.
    try:
        rgb = pixel_at(image, args.x, args.y)
    except ValueError as exc:
        return report_error("sample", str(exc))

    header = f"image: {escape_controls(args.image)}  {image.width}x{image.height}"
    if args.width == 1 and args.height == 1:
        print(header)
        print(
            f"pixel ({args.x}, {args.y}): "
            f"{rgb[0]},{rgb[1]},{rgb[2]}  {_hex(rgb)}"
        )
        return 0

    # Validate the whole rectangle before printing any pixel: a region that
    # runs past the right or bottom edge must produce one diagnostic, not a
    # partial dump followed by pixel_at's error on the first bad coordinate.
    if (
        args.x + args.width > image.width
        or args.y + args.height > image.height
    ):
        return report_error(
            "sample",
            f"region ({args.x}, {args.y}) "
            f"{args.width}x{args.height} is outside the "
            f"{image.width}x{image.height} image",
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
