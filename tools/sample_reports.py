"""Output formatting and report handlers for the reference pixel sampler."""

from __future__ import annotations

import json
from collections import Counter
from heapq import nsmallest


def _hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def _region_pixels(image, x: int, y: int, width: int, height: int):
    rgb = image.rgb
    image_width = image.width
    for row in range(y, y + height):
        offset = (row * image_width + x) * 3
        for offset in range(offset, offset + width * 3, 3):
            yield (rgb[offset], rgb[offset + 1], rgb[offset + 2])


def _color_runs(image, x: int, y: int, width: int, height: int):
    horizontal = height == 1
    segments = []
    for offset, rgb in enumerate(_region_pixels(image, x, y, width, height)):
        px, py = (x + offset, y) if horizontal else (x, y + offset)
        if segments and segments[-1]["rgb"] == rgb:
            segments[-1]["length"] += 1
        else:
            segments.append({"x": px, "y": py, "length": 1, "rgb": rgb})
    return ("horizontal" if horizontal else "vertical"), segments


def report(args, image, width: int, height: int, header: str) -> None:
    region = {"x": args.x, "y": args.y, "width": args.width, "height": args.height}
    if args.runs:
        axis, runs = _color_runs(image, args.x, args.y, args.width, args.height)
        if args.json:
            print(json.dumps({"image": args.image, "image_width": width, "image_height": height,
                "region": region, "axis": axis, "runs": [
                    {**run, "rgb": list(run["rgb"]), "hex": _hex(run["rgb"])} for run in runs
                ]}, ensure_ascii=True))
            return
        print(header)
        print(f"region ({args.x}, {args.y}) {args.width}x{args.height}:")
        print(f"axis: {axis}")
        for run in runs:
            rgb = run["rgb"]
            print(f"({run['x']}, {run['y']}): {rgb[0]},{rgb[1]},{rgb[2]}  {_hex(rgb)}  length={run['length']}")
        return

    if args.histogram:
        counts = Counter(_region_pixels(image, args.x, args.y, args.width, args.height))
        if args.top_colors is not None:
            total_colors = len(counts)
            colors = nsmallest(
                args.top_colors,
                counts.items(),
                key=lambda item: (-item[1], item[0]),
            )
            omitted_pixels = args.width * args.height - sum(count for _, count in colors)
        else:
            colors = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        if args.json:
            result = {"image": args.image, "image_width": width, "image_height": height,
                "region": region, "colors": [
                    {"rgb": list(rgb), "hex": _hex(rgb), "count": count} for rgb, count in colors
                ]}
            if args.top_colors is not None:
                result["total_colors"] = total_colors
                result["omitted_pixels"] = omitted_pixels
            print(json.dumps(result, ensure_ascii=True))
            return
        print(header)
        print(f"region ({args.x}, {args.y}) {args.width}x{args.height}:")
        for rgb, count in colors:
            print(f"{rgb[0]},{rgb[1]},{rgb[2]}  {_hex(rgb)}  count={count}")
        if args.top_colors is not None:
            print(f"total colors: {total_colors}")
            print(f"omitted pixels: {omitted_pixels}")
        return

    if args.find_color is not None:
        target = args.find_color
        tolerance = args.color_tolerance if args.color_tolerance is not None else 0
        count = 0
        min_x, min_y, max_x, max_y = args.x + args.width, args.y + args.height, -1, -1
        for index, rgb in enumerate(_region_pixels(image, args.x, args.y, args.width, args.height)):
            x, y = args.x + index % args.width, args.y + index // args.width
            if max(abs(channel - wanted) for channel, wanted in zip(rgb, target)) <= tolerance:
                count += 1
                min_x, min_y = min(min_x, x), min(min_y, y)
                max_x, max_y = max(max_x, x), max(max_y, y)
        bounds = None if count == 0 else {"x": min_x, "y": min_y,
            "width": max_x - min_x + 1, "height": max_y - min_y + 1}
        color_hex = _hex(target)
        if args.json:
            print(json.dumps({"image": args.image, "image_width": width, "image_height": height,
                "region": region, "match": {"rgb": list(target), "hex": color_hex,
                "count": count, "bounds": bounds,
                **({"tolerance": tolerance} if args.color_tolerance is not None else {})}}, ensure_ascii=True))
            return
        print(header)
        print(f"region ({args.x}, {args.y}) {args.width}x{args.height}:")
        print(f"color: {color_hex}")
        if args.color_tolerance is not None:
            print(f"tolerance: {tolerance}")
        print(f"count: {count}")
        print("bounds: none" if bounds is None else
              f"bounds: {bounds['x']},{bounds['y']},{bounds['width']},{bounds['height']}")
        return

    if args.json:
        pixels = []
        for index, rgb in enumerate(_region_pixels(image, args.x, args.y, args.width, args.height)):
            x, y = args.x + index % args.width, args.y + index // args.width
            pixels.append({"x": x, "y": y, "rgb": list(rgb), "hex": _hex(rgb)})
        print(json.dumps({"image": args.image, "image_width": width, "image_height": height,
            "region": region, "pixels": pixels}, ensure_ascii=True))
        return
    if args.width == 1 and args.height == 1:
        rgb = (image.rgb[(args.y * image.width + args.x) * 3 + i] for i in range(3))
        rgb = tuple(rgb)
        print(header)
        print(f"pixel ({args.x}, {args.y}): {rgb[0]},{rgb[1]},{rgb[2]}  {_hex(rgb)}")
        return
    print(header)
    print(f"region ({args.x}, {args.y}) {args.width}x{args.height}:")
    for index, (r, g, b) in enumerate(_region_pixels(image, args.x, args.y, args.width, args.height)):
        x, y = args.x + index % args.width, args.y + index // args.width
        print(f"({x}, {y}): {r},{g},{b}  {_hex((r, g, b))}")
