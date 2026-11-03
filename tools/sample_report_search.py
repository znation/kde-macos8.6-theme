"""Color-search reports for the reference pixel sampler."""

from __future__ import annotations

import json

if __package__:
    from tools.sample_report_pixels import _hex, _positioned_region_pixels, _region_alpha
    from tools.sample_match_runs import _MatchRuns
else:  # run directly: python3 tools/sample.py
    from sample_report_pixels import _hex, _positioned_region_pixels, _region_alpha
    from sample_match_runs import _MatchRuns


def _search_match(args, image) -> dict:
    target = args.find_color
    tolerance = args.color_tolerance if args.color_tolerance is not None else 0
    count = 0
    sum_x = sum_y = 0
    matched_pixels = []
    matching_rows = [0] * args.height if args.match_rows else None
    intervals = _MatchRuns(args.x, args.y, args.width, args.height,
                           args.match_runs, args.match_column_runs)
    min_x, min_y, max_x, max_y = args.x + args.width, args.y + args.height, -1, -1
    alphas = iter(_region_alpha(image, args.x, args.y, args.width, args.height)) if args.match_alpha is not None else None
    for x, y, rgb in _positioned_region_pixels(image, args.x, args.y, args.width, args.height):
        alpha_matches = alphas is None or next(alphas) == args.match_alpha
        matches = alpha_matches and max(abs(channel - wanted) for channel, wanted in zip(rgb, target)) <= tolerance
        intervals.observe(x, y, matches)
        if matches:
            count += 1
            if matching_rows is not None:
                matching_rows[y - args.y] += 1
            if args.match_centroid:
                sum_x += x
                sum_y += y
            if args.match_pixels is not None and len(matched_pixels) < args.match_pixels:
                matched_pixels.append({"x": x, "y": y})
            min_x, min_y = min(min_x, x), min(min_y, y)
            max_x, max_y = max(max_x, x), max(max_y, y)
    matched_runs, matched_column_runs = intervals.finish()
    bounds = None if count == 0 else {"x": min_x, "y": min_y,
        "width": max_x - min_x + 1, "height": max_y - min_y + 1}
    return {"rgb": list(target), "hex": _hex(target), "count": count,
            "bounds": bounds,
            **({"fraction": count / (args.width * args.height)} if args.match_fraction else {}),
            **({"centroid": None if count == 0 else {"x": sum_x / count, "y": sum_y / count}}
               if args.match_centroid else {}),
            **({"pixels": matched_pixels, "omitted_pixels": count - len(matched_pixels)}
               if args.match_pixels is not None else {}),
            **({"runs": matched_runs} if args.match_runs else {}),
            **({"column_runs": matched_column_runs} if args.match_column_runs else {}),
            **({"rows": matching_rows} if matching_rows is not None else {}),
            **({"tolerance": tolerance} if args.color_tolerance is not None else {}),
            **({"alpha": args.match_alpha} if args.match_alpha is not None else {})}


def report_search(args, image, width: int, height: int, header: str) -> None:
    region = {"x": args.x, "y": args.y, "width": args.width, "height": args.height}
    match = _search_match(args, image)
    count = match["count"]
    bounds = match["bounds"]
    color_hex = match["hex"]
    if args.json:
        print(json.dumps({"image": args.image, "image_width": width, "image_height": height,
            "region": region, "match": match}, ensure_ascii=True))
        return
    print(header)
    print(f"region ({args.x}, {args.y}) {args.width}x{args.height}:")
    print(f"color: {color_hex}")
    if args.color_tolerance is not None:
        print(f"tolerance: {match['tolerance']}")
    if args.match_alpha is not None:
        print(f"alpha: {args.match_alpha}")
    print(f"count: {count}")
    if "fraction" in match:
        print(f"fraction: {match['fraction']}")
    print("bounds: none" if bounds is None else
          f"bounds: {bounds['x']},{bounds['y']},{bounds['width']},{bounds['height']}")
    if "centroid" in match:
        centroid = match["centroid"]
        print("centroid: none" if centroid is None else f"centroid: {centroid['x']},{centroid['y']}")
    if args.match_pixels is not None:
        print(f"matching pixels: {len(match['pixels'])}")
        for pixel in match["pixels"]:
            print(f"pixel ({pixel['x']}, {pixel['y']})")
        print(f"omitted pixels: {match['omitted_pixels']}")
    if args.match_runs:
        print(f"matching runs: {json.dumps(match['runs'], separators=(',', ':'))}")
    if args.match_column_runs:
        print(f"matching column runs: {json.dumps(match['column_runs'], separators=(',', ':'))}")
    if args.match_rows:
        print(f"matching rows: {json.dumps(match['rows'], separators=(',', ':'))}")
