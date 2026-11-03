"""Color-search reports for the reference pixel sampler."""

from __future__ import annotations

import json

if __package__:
    from tools.sample_report_pixels import _hex, _positioned_region_pixels, _region_alpha
else:  # run directly: python3 tools/sample.py
    from sample_report_pixels import _hex, _positioned_region_pixels, _region_alpha


def report_search(args, image, width: int, height: int, header: str) -> None:
    region = {"x": args.x, "y": args.y, "width": args.width, "height": args.height}
    target = args.find_color
    tolerance = args.color_tolerance if args.color_tolerance is not None else 0
    count = 0
    sum_x = sum_y = 0
    matched_pixels = []
    matched_runs = []
    run_start = None
    run_y = None
    column_starts = {}
    matched_column_runs = []
    min_x, min_y, max_x, max_y = args.x + args.width, args.y + args.height, -1, -1
    alphas = iter(_region_alpha(image, args.x, args.y, args.width, args.height)) if args.match_alpha is not None else None
    for x, y, rgb in _positioned_region_pixels(image, args.x, args.y, args.width, args.height):
        if args.match_runs and run_start is not None and y != run_y:
            matched_runs.append({"x": run_start, "y": run_y,
                                 "length": args.x + args.width - run_start})
            run_start = None
        alpha_matches = alphas is None or next(alphas) == args.match_alpha
        matches = alpha_matches and max(abs(channel - wanted) for channel, wanted in zip(rgb, target)) <= tolerance
        if args.match_column_runs:
            if matches:
                column_starts.setdefault(x, y)
            elif x in column_starts:
                start = column_starts.pop(x)
                matched_column_runs.append({"x": x, "y": start, "length": y - start})
        if matches:
            if args.match_runs and run_start is None:
                run_start, run_y = x, y
            count += 1
            if args.match_centroid:
                sum_x += x
                sum_y += y
            if args.match_pixels is not None and len(matched_pixels) < args.match_pixels:
                matched_pixels.append({"x": x, "y": y})
            min_x, min_y = min(min_x, x), min(min_y, y)
            max_x, max_y = max(max_x, x), max(max_y, y)
        elif args.match_runs and run_start is not None:
            matched_runs.append({"x": run_start, "y": run_y, "length": x - run_start})
            run_start = None
    if args.match_runs and run_start is not None:
        matched_runs.append({"x": run_start, "y": run_y, "length": args.x + args.width - run_start})
    matched_column_runs.extend(
        {"x": x, "y": start, "length": args.y + args.height - start}
        for x, start in column_starts.items()
    )
    matched_column_runs.sort(key=lambda run: (run["x"], run["y"]))
    bounds = None if count == 0 else {"x": min_x, "y": min_y,
        "width": max_x - min_x + 1, "height": max_y - min_y + 1}
    color_hex = _hex(target)
    if args.json:
        print(json.dumps({"image": args.image, "image_width": width, "image_height": height,
            "region": region, "match": {"rgb": list(target), "hex": color_hex,
            "count": count, "bounds": bounds,
            **({"fraction": count / (args.width * args.height)} if args.match_fraction else {}),
            **({"centroid": None if count == 0 else {"x": sum_x / count, "y": sum_y / count}}
               if args.match_centroid else {}),
            **({"pixels": matched_pixels, "omitted_pixels": count - len(matched_pixels)}
               if args.match_pixels is not None else {}),
            **({"runs": matched_runs} if args.match_runs else {}),
            **({"column_runs": matched_column_runs} if args.match_column_runs else {}),
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
    if args.match_centroid:
        print("centroid: none" if count == 0 else f"centroid: {sum_x / count},{sum_y / count}")
    if args.match_pixels is not None:
        print(f"matching pixels: {len(matched_pixels)}")
        for pixel in matched_pixels:
            print(f"pixel ({pixel['x']}, {pixel['y']})")
        print(f"omitted pixels: {count - len(matched_pixels)}")
    if args.match_runs:
        print(f"matching runs: {json.dumps(matched_runs, separators=(',', ':'))}")
    if args.match_column_runs:
        print(f"matching column runs: {json.dumps(matched_column_runs, separators=(',', ':'))}")
