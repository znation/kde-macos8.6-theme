"""Shared image and region helpers for the sampler's report modules."""

from __future__ import annotations

import json

if __package__:
    from tools.terminal import escape_controls
else:
    from terminal import escape_controls


def format_image_header(image: str, width: int, height: int) -> str:
    """Format the sampler's escaped image name and decoded dimensions."""
    return f"image: {escape_controls(image)}  {width}x{height}"


def region_from_args(args) -> dict:
    """Return the region the report's args define, as the {"x", "y", "width", "height"}
    dict every sample report result and JSON document carries. One call site: report_context,
    which the pixels, runs, histogram and find-color-search report handlers all share."""
    return {"x": args.x, "y": args.y, "width": args.width, "height": args.height}


def report_context(args, width: int, height: int) -> dict:
    """Return the common image and requested-region fields used by reports."""
    return {
        "image": args.image,
        "image_width": width,
        "image_height": height,
        "region": region_from_args(args),
    }


def hex(rgb: tuple[int, int, int]) -> str:
    """Format one RGB triple as the reports' ``#RRGGBB`` text."""
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def print_region_line(args) -> None:
    """Print the plain-text region line each sample report prints before its rows.
    Four call sites: the pixels, runs, histogram and find-color-search report handlers."""
    print(f"region ({args.x}, {args.y}) {args.width}x{args.height}:")


def print_report_header(header: str, args) -> None:
    """Print the shared heading and region lines for plain-text reports."""
    print(header)
    print_region_line(args)


def compact_json(obj) -> str:
    """Serialize obj as compact JSON, the format the sample reports embed list and
    mapping fields inside their plain-text lines. Eight call sites: six in the
    find-color-search report and two in the histogram report."""
    return json.dumps(obj, separators=(",", ":"))


def region_pixels(image, x: int, y: int, width: int, height: int):
    """Yield each RGB pixel in a rectangle, row-major."""
    rgb = image.rgb
    image_width = image.width
    for row in range(y, y + height):
        offset = (row * image_width + x) * 3
        for offset in range(offset, offset + width * 3, 3):
            yield (rgb[offset], rgb[offset + 1], rgb[offset + 2])


def positioned_region_pixels(image, x: int, y: int, width: int, height: int):
    """Yield each RGB pixel in a rectangle with its absolute image position."""
    for index, rgb in enumerate(region_pixels(image, x, y, width, height)):
        yield x + index % width, y + index // width, rgb


def positioned_region_column_pixels(image, x: int, y: int, width: int, height: int):
    """Yield each RGB pixel in a rectangle with its absolute image position,
    column-major. Column-major twin of positioned_region_pixels; it re-reads
    the already-decoded buffers and owns one call site: the capped vertical
    match-run collector"""
    rgb, image_width = image.rgb, image.width
    for column in range(x, x + width):
        for row in range(y, y + height):
            offset = (row * image_width + column) * 3
            yield (column, row,
                   (rgb[offset], rgb[offset + 1], rgb[offset + 2]))


def region_alpha(image, x: int, y: int, width: int, height: int):
    """Yield each pixel's alpha value in a rectangle, row-major; an image
    without an alpha channel yields 255."""
    alpha = image.alpha
    for row in range(y, y + height):
        offset = row * image.width + x
        for index in range(offset, offset + width):
            yield 255 if alpha is None else alpha[index]


def positioned_region_column_alpha(image, x: int, y: int,
                                  width: int, height: int):
    """Yield alpha bytes in column-major region order without copying them."""
    alpha = image.alpha
    image_width = image.width
    for column in range(x, x + width):
        for row in range(y, y + height):
            index = row * image_width + column
            yield 255 if alpha is None else alpha[index]
