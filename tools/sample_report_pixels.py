"""Ordinary pixel and rectangle reports for the reference sampler."""

from __future__ import annotations

import json

if __package__:
    from tools.sample_report_common import (
        hex, positioned_region_pixels, print_report_header, region_alpha,
        report_context,
    )
else:  # run directly: python3 tools/sample.py
    from sample_report_common import (
        hex, positioned_region_pixels, print_report_header, region_alpha,
        report_context,
    )


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
    print_report_header(header, args)
    for pixel in _pixel_records(args, image):
        r, g, b = pixel["rgb"]
        suffix = f"  alpha={pixel['alpha']}" if args.alpha else ""
        print(f"({pixel['x']}, {pixel['y']}): {r},{g},{b}  {pixel['hex']}{suffix}")
