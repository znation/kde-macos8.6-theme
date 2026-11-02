"""Output formatting and report handlers for the reference pixel sampler."""

from __future__ import annotations

import json
from collections import Counter
from heapq import nsmallest

if __package__:
    from tools.sample_report_pixels import (
        _hex, _positioned_region_pixels, _region_alpha, _region_pixels, report_pixels,
    )
else:  # run directly: python3 tools/sample.py
    from sample_report_pixels import (
        _hex, _positioned_region_pixels, _region_alpha, _region_pixels, report_pixels,
    )


def _color_runs(image, x: int, y: int, width: int, height: int, alpha_aware: bool = False):
    horizontal = height == 1
    segments = []
    alphas = _region_alpha(image, x, y, width, height) if alpha_aware else None
    for offset, rgb in enumerate(_region_pixels(image, x, y, width, height)):
        alpha = next(alphas) if alphas is not None else None
        px, py = (x + offset, y) if horizontal else (x, y + offset)
        if segments and segments[-1]["rgb"] == rgb and (not alpha_aware or segments[-1]["alpha"] == alpha):
            segments[-1]["length"] += 1
        else:
            segment = {"x": px, "y": py, "length": 1, "rgb": rgb}
            if alpha_aware:
                segment["alpha"] = alpha
            segments.append(segment)
    return ("horizontal" if horizontal else "vertical"), segments


def report(args, image, width: int, height: int, header: str) -> None:
    region = {"x": args.x, "y": args.y, "width": args.width, "height": args.height}
    if args.runs:
        axis, runs = _color_runs(image, args.x, args.y, args.width, args.height, args.alpha)
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
            suffix = f"  alpha={run['alpha']}" if args.alpha else ""
            print(f"({run['x']}, {run['y']}): {rgb[0]},{rgb[1]},{rgb[2]}  {_hex(rgb)}  length={run['length']}{suffix}")
        return

    if args.histogram:
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
        if args.color_bounds:
            bounds_by_color = {color: [args.x + args.width, args.y + args.height, -1, -1]
                               for color, _ in colors}
            alphas = iter(_region_alpha(image, args.x, args.y, args.width, args.height)) if args.alpha else None
            for x, y, rgb in _positioned_region_pixels(image, args.x, args.y, args.width, args.height):
                color = (*rgb, next(alphas)) if alphas is not None else rgb
                bounds = bounds_by_color.get(color)
                if bounds is not None:
                    bounds[0], bounds[1] = min(bounds[0], x), min(bounds[1], y)
                    bounds[2], bounds[3] = max(bounds[2], x), max(bounds[3], y)
            bounds_by_color = {color: {"x": bounds[0], "y": bounds[1],
                "width": bounds[2] - bounds[0] + 1, "height": bounds[3] - bounds[1] + 1}
                for color, bounds in bounds_by_color.items()}
        if args.json:
            denominator = args.width * args.height
            result = {"image": args.image, "image_width": width, "image_height": height,
                "region": region, "colors": [
                    {"rgb": list(color[:3]), "hex": _hex(color[:3]), "count": count,
                     **({"alpha": color[3]} if args.alpha else {}),
                     **({"fraction": count / denominator} if args.color_fractions else {}),
                     **({"bounds": bounds_by_color[color]} if bounds_by_color is not None else {})}
                    for color, count in colors
                ]}
            if args.top_colors is not None:
                result["total_colors"] = total_colors
                result["omitted_pixels"] = omitted_pixels
            print(json.dumps(result, ensure_ascii=True))
            return
        print(header)
        print(f"region ({args.x}, {args.y}) {args.width}x{args.height}:")
        denominator = args.width * args.height
        for color, count in colors:
            rgb = color[:3]
            suffix = f"  alpha={color[3]}" if args.alpha else ""
            if bounds_by_color is not None:
                bounds = bounds_by_color[color]
                suffix += f"  bounds={bounds['x']},{bounds['y']},{bounds['width']},{bounds['height']}"
            if args.color_fractions:
                suffix += f"  fraction={count / denominator}"
            print(f"{rgb[0]},{rgb[1]},{rgb[2]}  {_hex(rgb)}  count={count}{suffix}")
        if args.top_colors is not None:
            print(f"total colors: {total_colors}")
            print(f"omitted pixels: {omitted_pixels}")
        return

    if args.find_color is not None:
        target = args.find_color
        tolerance = args.color_tolerance if args.color_tolerance is not None else 0
        count = 0
        matched_pixels = []
        min_x, min_y, max_x, max_y = args.x + args.width, args.y + args.height, -1, -1
        alphas = iter(_region_alpha(image, args.x, args.y, args.width, args.height)) if args.match_alpha is not None else None
        for x, y, rgb in _positioned_region_pixels(
            image, args.x, args.y, args.width, args.height
        ):
            alpha_matches = alphas is None or next(alphas) == args.match_alpha
            if alpha_matches and max(abs(channel - wanted) for channel, wanted in zip(rgb, target)) <= tolerance:
                count += 1
                if args.match_pixels is not None and len(matched_pixels) < args.match_pixels:
                    matched_pixels.append({"x": x, "y": y})
                min_x, min_y = min(min_x, x), min(min_y, y)
                max_x, max_y = max(max_x, x), max(max_y, y)
        bounds = None if count == 0 else {"x": min_x, "y": min_y,
            "width": max_x - min_x + 1, "height": max_y - min_y + 1}
        color_hex = _hex(target)
        if args.json:
            print(json.dumps({"image": args.image, "image_width": width, "image_height": height,
                "region": region, "match": {"rgb": list(target), "hex": color_hex,
                "count": count, "bounds": bounds,
                **({"fraction": count / (args.width * args.height)} if args.match_fraction else {}),
                **({"pixels": matched_pixels, "omitted_pixels": count - len(matched_pixels)}
                   if args.match_pixels is not None else {}),
                **({"tolerance": tolerance} if args.color_tolerance is not None else {}),
                **({"alpha": args.match_alpha} if args.match_alpha is not None else {})}}, ensure_ascii=True))
            return
        print(header)
        print(f"region ({args.x}, {args.y}) {args.width}x{args.height}:")
        print(f"color: {color_hex}")
        if args.color_tolerance is not None:
            print(f"tolerance: {tolerance}")
        if args.match_alpha is not None:
            print(f"alpha: {args.match_alpha}")
        print(f"count: {count}")
        if args.match_fraction:
            print(f"fraction: {count / (args.width * args.height)}")
        print("bounds: none" if bounds is None else
              f"bounds: {bounds['x']},{bounds['y']},{bounds['width']},{bounds['height']}")
        if args.match_pixels is not None:
            print(f"matching pixels: {len(matched_pixels)}")
            for pixel in matched_pixels:
                print(f"pixel ({pixel['x']}, {pixel['y']})")
            print(f"omitted pixels: {count - len(matched_pixels)}")
        return

    report_pixels(args, image, width, height, header)
