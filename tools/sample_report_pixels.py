"""Ordinary pixel and rectangle reports for the reference sampler."""

from __future__ import annotations

import json

if __package__:
    from tools.sample_report_common import report_context
else:  # run directly: python3 tools/sample.py
    from sample_report_common import report_context


def hex(rgb: tuple[int, int, int]) -> str:
    """Format one RGB triple as the reports' ``#RRGGBB`` text."""
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def print_region_line(args) -> None:
    """Print the plain-text region line each sample report prints before its rows.
    Four call sites: the pixels, runs, histogram and find-color-search report handlers."""
    print(f"region ({args.x}, {args.y}) {args.width}x{args.height}:")


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


def _pixel_records(args, image):
    """Yield ordinary pixel report records lazily, in row-major order."""
    alphas = iter(region_alpha(image, args.x, args.y, args.width, args.height)) if args.alpha else None
    for x, y, rgb in positioned_region_pixels(
        image, args.x, args.y, args.width, args.height
    ):
        pixel = {"x": x, "y": y, "rgb": list(rgb), "hex": hex(rgb)}
        if alphas is not None:
            pixel["alpha"] = next(alphas)
        yield pixel


def report_pixels(args, image, width: int, height: int, header: str) -> None:
    """Print the ordinary single-pixel or rectangle report."""
    if args.json:
        pixels = list(_pixel_records(args, image))
        print(json.dumps({**report_context(args, width, height), "pixels": pixels}, ensure_ascii=True))
        return
    if args.width == 1 and args.height == 1:
        pixel = next(_pixel_records(args, image))
        r, g, b = pixel["rgb"]
        suffix = f"  alpha={pixel['alpha']}" if args.alpha else ""
        print(header)
        print(f"pixel ({args.x}, {args.y}): {r},{g},{b}  {pixel['hex']}{suffix}")
        return
    print(header)
    print_region_line(args)
    for pixel in _pixel_records(args, image):
        r, g, b = pixel["rgb"]
        suffix = f"  alpha={pixel['alpha']}" if args.alpha else ""
        print(f"({pixel['x']}, {pixel['y']}): {r},{g},{b}  {pixel['hex']}{suffix}")
