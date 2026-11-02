"""Ordinary pixel and rectangle reports for the reference sampler."""

from __future__ import annotations

import json


def _hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def _region_pixels(image, x: int, y: int, width: int, height: int):
    rgb = image.rgb
    image_width = image.width
    for row in range(y, y + height):
        offset = (row * image_width + x) * 3
        for offset in range(offset, offset + width * 3, 3):
            yield (rgb[offset], rgb[offset + 1], rgb[offset + 2])


def _positioned_region_pixels(image, x: int, y: int, width: int, height: int):
    """Yield each RGB pixel in a rectangle with its absolute image position."""
    for index, rgb in enumerate(_region_pixels(image, x, y, width, height)):
        yield x + index % width, y + index // width, rgb


def _region_alpha(image, x: int, y: int, width: int, height: int):
    alpha = image.alpha
    for row in range(y, y + height):
        offset = row * image.width + x
        for index in range(offset, offset + width):
            yield 255 if alpha is None else alpha[index]


def report_pixels(args, image, width: int, height: int, header: str) -> None:
    """Print the ordinary single-pixel or rectangle report."""
    region = {"x": args.x, "y": args.y, "width": args.width, "height": args.height}
    if args.json:
        pixels = []
        alphas = iter(_region_alpha(image, args.x, args.y, args.width, args.height)) if args.alpha else None
        for x, y, rgb in _positioned_region_pixels(
            image, args.x, args.y, args.width, args.height
        ):
            pixel = {"x": x, "y": y, "rgb": list(rgb), "hex": _hex(rgb)}
            if alphas is not None:
                pixel["alpha"] = next(alphas)
            pixels.append(pixel)
        print(json.dumps({"image": args.image, "image_width": width, "image_height": height,
            "region": region, "pixels": pixels}, ensure_ascii=True))
        return
    if args.width == 1 and args.height == 1:
        rgb = tuple(image.rgb[(args.y * image.width + args.x) * 3 + i] for i in range(3))
        suffix = f"  alpha={next(_region_alpha(image, args.x, args.y, 1, 1))}" if args.alpha else ""
        print(header)
        print(f"pixel ({args.x}, {args.y}): {rgb[0]},{rgb[1]},{rgb[2]}  {_hex(rgb)}{suffix}")
        return
    print(header)
    print(f"region ({args.x}, {args.y}) {args.width}x{args.height}:")
    alphas = iter(_region_alpha(image, args.x, args.y, args.width, args.height)) if args.alpha else None
    for x, y, (r, g, b) in _positioned_region_pixels(
        image, args.x, args.y, args.width, args.height
    ):
        suffix = f"  alpha={next(alphas)}" if alphas is not None else ""
        print(f"({x}, {y}): {r},{g},{b}  {_hex((r, g, b))}{suffix}")
