"""Print the RGB and hex value of one pixel in a reference screenshot.

The reference screenshots are the source of truth for the theme's palette and
metrics, and PLANS.md samples their pixels by hand to pin each value. This
tool makes that sampling a command: it reads the image through ``tools/png.py``
so the same LFS-aware ``read_png`` and bounds-checked ``pixel_at`` apply, then
prints the pixel in the two forms the theme files use -- the ``R,G,B`` triple
copied into a ``.colors`` file and the ``#RRGGBB`` literal copied into an SVG
or QML file.
"""

from __future__ import annotations

import argparse
import sys

if __package__:
    from tools.png import PngError, pixel_at, read_png
    from tools.terminal import escape_controls
else:  # run directly: python3 tools/sample.py
    from png import PngError, pixel_at, read_png
    from terminal import escape_controls


class _ArgumentParser(argparse.ArgumentParser):
    """ArgumentParser whose error diagnostics escape control characters.

    argparse formats some of its own errors (notably ``unrecognized
    arguments: ...``) from raw argv. A path or coordinate carrying an ESC or
    newline must not reach the operator's terminal unescaped, so the message
    is escaped here at the output boundary.
    """

    def error(self, message: str) -> None:
        super().error(escape_controls(message))


def _coordinate(value: str, name: str) -> int:
    """Return *value* as an integer coordinate, rejecting Python-only text.

    ``int()`` accepts forms a command-line coordinate should not: underscore
    digit separators (``1_0`` is 10), non-ASCII decimal digits and surrounding
    whitespace. Each silently names a different pixel than the operator wrote,
    so the text is checked before it is parsed.
    """
    if not value.isascii() or "_" in value or value != value.strip():
        raise argparse.ArgumentTypeError(
            f"{name} must be a plain ASCII integer: {value!r}"
        )
    try:
        return int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"{name} must be an integer: {value!r}"
        ) from exc


def _hex(rgb: tuple[int, int, int]) -> str:
    """Return the ``#RRGGBB`` form of *rgb*, zero-padding each channel."""
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def main(argv: list[str] | None = None) -> int:
    """Run the sampling CLI; *argv* is the argument list without a program name.

    Following ``argparse`` and the sibling ``tools/fidelity.py``, ``None``
    reads ``sys.argv``.
    """
    parser = _ArgumentParser(
        prog="sample",
        description="Print a reference screenshot pixel's RGB and hex value.",
        epilog="exit status: 0 on success, 2 usage or read error",
    )
    parser.add_argument("image", help="reference image (PNG)")
    parser.add_argument(
        "x", type=lambda value: _coordinate(value, "x"), help="pixel column"
    )
    parser.add_argument(
        "y", type=lambda value: _coordinate(value, "y"), help="pixel row"
    )
    args = parser.parse_args(argv)

    try:
        image = read_png(args.image)
    except PngError as exc:
        print(f"sample: error: {escape_controls(str(exc))}", file=sys.stderr)
        return 2
    # pixel_at rejects a coordinate outside the image; it is operator input
    # here, not a caller bug, so report it as an error rather than a traceback.
    try:
        rgb = pixel_at(image, args.x, args.y)
    except ValueError as exc:
        print(f"sample: error: {escape_controls(str(exc))}", file=sys.stderr)
        return 2

    print(f"image: {escape_controls(args.image)}  {image.width}x{image.height}")
    print(f"pixel ({args.x}, {args.y}): {rgb[0]},{rgb[1]},{rgb[2]}  {_hex(rgb)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
