"""Histogram reports for the reference pixel sampler."""

from __future__ import annotations

import json
from collections import Counter
from heapq import nsmallest

if __package__:
    from tools.sample_report_pixels import (
        _hex, _positioned_region_pixels, _region_alpha, _region_pixels,
    )
else:  # run directly: python3 tools/sample.py
    from sample_report_pixels import (
        _hex, _positioned_region_pixels, _region_alpha, _region_pixels,
    )


def _histogram_result(args, image, width: int, height: int) -> dict:
    """Assemble the complete histogram report without printing or mutating args."""
    region = {"x": args.x, "y": args.y, "width": args.width, "height": args.height}
    if args.alpha:
        pixels = zip(_region_pixels(image, args.x, args.y, args.width, args.height),
                     _region_alpha(image, args.x, args.y, args.width, args.height))
        counts = Counter((*rgb, alpha) for rgb, alpha in pixels)
    else:
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
    bounds_by_color = None
    positions_by_color = None
    if args.color_bounds or args.color_positions:
        positions_by_color = {} if args.color_positions else None
        if positions_by_color is not None:
            positions_by_color = {color: None for color, _ in colors}
    if args.color_bounds:
        bounds_by_color = {color: [args.x + args.width, args.y + args.height, -1, -1]
                           for color, _ in colors}
    if args.color_bounds or args.color_positions:
        alphas = iter(_region_alpha(image, args.x, args.y, args.width, args.height)) if args.alpha else None
        for x, y, rgb in _positioned_region_pixels(image, args.x, args.y, args.width, args.height):
            color = (*rgb, next(alphas)) if alphas is not None else rgb
            if positions_by_color is not None and positions_by_color.get(color) is None:
                positions_by_color[color] = {"x": x, "y": y}
            if bounds_by_color is not None and color in bounds_by_color:
                bounds = bounds_by_color[color]
                bounds[0], bounds[1] = min(bounds[0], x), min(bounds[1], y)
                bounds[2], bounds[3] = max(bounds[2], x), max(bounds[3], y)
    if bounds_by_color is not None:
        bounds_by_color = {color: {"x": bounds[0], "y": bounds[1],
            "width": bounds[2] - bounds[0] + 1, "height": bounds[3] - bounds[1] + 1}
            for color, bounds in bounds_by_color.items()}
    denominator = args.width * args.height
    result = {"image": args.image, "image_width": width, "image_height": height,
        "region": region, "colors": [
            {"rgb": list(color[:3]), "hex": _hex(color[:3]), "count": count,
             **({"alpha": color[3]} if args.alpha else {}),
             **({"fraction": count / denominator} if args.color_fractions else {}),
             **({"position": positions_by_color[color]} if positions_by_color is not None else {}),
             **({"bounds": bounds_by_color[color]} if bounds_by_color is not None else {})}
            for color, count in colors
        ]}
    if args.top_colors is not None:
        result["total_colors"] = total_colors
        result["omitted_pixels"] = omitted_pixels
    return result


def report_histogram(args, image, width: int, height: int, header: str) -> None:
    result = _histogram_result(args, image, width, height)
    if args.json:
        print(json.dumps(result, ensure_ascii=True))
        return
    print(header)
    region = result["region"]
    print(f"region ({region['x']}, {region['y']}) {region['width']}x{region['height']}:")
    for color in result["colors"]:
        rgb = color["rgb"]
        suffix = f"  alpha={color['alpha']}" if "alpha" in color else ""
        if "bounds" in color:
            bounds = color["bounds"]
            suffix += f"  bounds={bounds['x']},{bounds['y']},{bounds['width']},{bounds['height']}"
        if "fraction" in color:
            suffix += f"  fraction={color['fraction']}"
        if "position" in color:
            position = color["position"]
            suffix += f"  position={position['x']},{position['y']}"
        print(f"{rgb[0]},{rgb[1]},{rgb[2]}  {color['hex']}  count={color['count']}{suffix}")
    if args.top_colors is not None:
        print(f"total colors: {result['total_colors']}")
        print(f"omitted pixels: {result['omitted_pixels']}")
