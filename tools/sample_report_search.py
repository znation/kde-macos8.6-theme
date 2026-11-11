"""Color-search reports for the reference pixel sampler."""

from __future__ import annotations

import json

if __package__:
    from tools.sample_report_common import report_context
    from tools.sample_report_pixels import (
        compact_json, hex, positioned_region_column_pixels,
        positioned_region_pixels, region_alpha, print_region_line,
    )
    from tools.sample_match_runs import ColumnRuns, MatchRuns
else:  # run directly: python3 tools/sample.py
    from sample_report_common import report_context
    from sample_report_pixels import (
        compact_json, hex, positioned_region_column_pixels,
        positioned_region_pixels, region_alpha, print_region_line,
    )
    from sample_match_runs import ColumnRuns, MatchRuns


def _extend_match_bound(bounds, index: int, position: int,
                        coordinate_key: str, length_key: str) -> None:
    """Open the bound at *index* on the first match and stretch it to *position*."""
    bound = bounds[index]
    if bound is None:
        bounds[index] = {coordinate_key: position, length_key: 1}
    else:
        bound[length_key] = position - bound[coordinate_key] + 1


def _pixel_matches(alphas, rgb, target, tolerance, match_alpha) -> bool:
    """Evaluate one pixel against the exact-alpha and RGB-tolerance predicate;
    the row-major and capped column-major scans share it."""
    return (alphas is None or next(alphas) == match_alpha) and \
        max(abs(channel - wanted) for channel, wanted in zip(rgb, target)) <= tolerance


def _search_match(args, image) -> dict:
    """Assemble the find-color report's match mapping: count and bound the
    region's matching pixels, tally the requested rows, columns and bounds,
    and fill the pixel, run, cap and longest-run fields the match options
    request."""
    target = args.find_color
    tolerance = args.color_tolerance if args.color_tolerance is not None else 0
    capped_columns = getattr(args, "max_match_column_runs", None) is not None
    count = 0
    sum_x = sum_y = 0
    matched_pixels = []
    matching_rows = [0] * args.height if args.match_rows else None
    matching_columns = [0] * args.width if args.match_columns else None
    matching_row_bounds = [None] * args.height if args.match_row_bounds else None
    matching_column_bounds = [None] * args.width if args.match_column_bounds else None
    intervals = MatchRuns(
        args.x, args.y, args.width, args.height,
        horizontal=args.match_runs or args.longest_match_run or args.match_run_count,
        vertical=(args.match_column_runs or args.match_column_run_count or
                  args.longest_match_column_run),
        summarize=args.longest_match_run,
        collect_runs=args.match_runs,
        min_run_length=args.min_match_run_length,
        max_run_length=args.max_match_run_length,
        run_limit=getattr(args, "max_match_runs", None),
        run_offset=getattr(args, "match_run_offset", None) or 0,
        summarize_columns=args.longest_match_column_run,
        collect_column_runs=(not capped_columns and args.match_column_runs))
    min_x, min_y, max_x, max_y = args.x + args.width, args.y + args.height, -1, -1
    column_collector = ColumnRuns(
        args.x, args.y, args.width, args.height,
        min_run_length=args.min_match_column_run_length,
        max_run_length=args.max_match_column_run_length,
        run_limit=args.max_match_column_runs,
        run_offset=getattr(args, "match_column_run_offset", None) or 0)
    alphas = iter(region_alpha(image, args.x, args.y, args.width, args.height)) if args.match_alpha is not None else None
    for x, y, rgb in positioned_region_pixels(image, args.x, args.y, args.width, args.height):
        matches = _pixel_matches(alphas, rgb, target, tolerance, args.match_alpha)
        intervals.observe(x, y, matches)
        if matches:
            count += 1
            if matching_rows is not None:
                matching_rows[y - args.y] += 1
            if matching_columns is not None:
                matching_columns[x - args.x] += 1
            if matching_row_bounds is not None:
                _extend_match_bound(
                    matching_row_bounds, y - args.y, x, "x", "width")
            if matching_column_bounds is not None:
                _extend_match_bound(
                    matching_column_bounds, x - args.x, y, "y", "height")
            if args.match_centroid:
                sum_x += x
                sum_y += y
            offset = args.match_pixel_offset or 0
            if (args.match_pixels is not None and count > offset
                    and len(matched_pixels) < args.match_pixels):
                matched_pixels.append({"x": x, "y": y})
            min_x, min_y = min(min_x, x), min(min_y, y)
            max_x, max_y = max(max_x, x), max(max_y, y)
    matched_runs, matched_column_runs = intervals.finish()
    if capped_columns:
        column_alphas = None
        if args.match_alpha is not None:
            # region_alpha yields row-major, but the column scan below walks
            # the region column-major: serve alphas in the scan's order so each
            # pixel keeps its own alpha value.
            region_alphas = list(region_alpha(image, args.x, args.y, args.width, args.height))
            column_alphas = iter(
                region_alphas[(row - args.y) * args.width + column - args.x]
                for column in range(args.x, args.x + args.width)
                for row in range(args.y, args.y + args.height))
        for x, y, rgb in positioned_region_column_pixels(
                image, args.x, args.y, args.width, args.height):
            column_collector.observe(
                x, y, _pixel_matches(column_alphas, rgb, target, tolerance,
                                     args.match_alpha))
        matched_column_runs = column_collector.finish()
    omitted_runs = None
    run_offset = getattr(args, "match_run_offset", None)
    if getattr(args, "max_match_runs", None) is not None:
        omitted_runs = intervals.eligible_run_count - len(matched_runs)
    omitted_column_runs = None
    column_run_offset = getattr(args, "match_column_run_offset", None)
    if capped_columns:
        omitted_column_runs = (column_collector.eligible_run_count
                               - len(matched_column_runs))
    else:
        if args.min_match_column_run_length is not None:
            matched_column_runs = [run for run in matched_column_runs
                                   if run["length"] >= args.min_match_column_run_length]
        if args.max_match_column_run_length is not None:
            matched_column_runs = [run for run in matched_column_runs
                                   if run["length"] <= args.max_match_column_run_length]
    bounds = None if count == 0 else {"x": min_x, "y": min_y,
        "width": max_x - min_x + 1, "height": max_y - min_y + 1}
    return {"rgb": list(target), "hex": hex(target), "count": count,
            "bounds": bounds,
            **({"fraction": count / (args.width * args.height)} if args.match_fraction else {}),
            **({"centroid": None if count == 0 else {"x": sum_x / count, "y": sum_y / count}}
               if args.match_centroid else {}),
            **({"pixels": matched_pixels, "omitted_pixels": count - len(matched_pixels)}
               if args.match_pixels is not None else {}),
            **({"pixel_offset": args.match_pixel_offset}
               if args.match_pixel_offset is not None else {}),
            **({"runs": matched_runs} if args.match_runs else {}),
            **({"omitted_runs": omitted_runs} if omitted_runs is not None else {}),
            **({"run_offset": run_offset} if run_offset is not None else {}),
            **({"run_count": intervals.run_count} if args.match_run_count else {}),
            **({"longest_run": intervals.longest_run} if args.longest_match_run else {}),
            **({"column_runs": matched_column_runs} if args.match_column_runs else {}),
            **({"omitted_column_runs": omitted_column_runs}
               if omitted_column_runs is not None else {}),
            **({"column_run_offset": column_run_offset}
               if column_run_offset is not None else {}),
            **({"column_run_count": intervals.column_run_count}
               if args.match_column_run_count else {}),
            **({"longest_column_run": intervals.longest_column_run}
               if args.longest_match_column_run else {}),
            **({"rows": matching_rows} if matching_rows is not None else {}),
            **({"columns": matching_columns} if matching_columns is not None else {}),
            **({"row_bounds": matching_row_bounds} if matching_row_bounds is not None else {}),
            **({"column_bounds": matching_column_bounds} if matching_column_bounds is not None else {}),
            **({"tolerance": tolerance} if args.color_tolerance is not None else {}),
            **({"alpha": args.match_alpha} if args.match_alpha is not None else {})}


def report_search(args, image, width: int, height: int, header: str) -> None:
    """Print the find-color report: the region's match for the requested color, as JSON or plain text."""
    match = _search_match(args, image)
    count = match["count"]
    bounds = match["bounds"]
    color_hex = match["hex"]
    if args.json:
        print(json.dumps({**report_context(args, width, height), "match": match}, ensure_ascii=True))
        return
    print(header)
    print_region_line(args)
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
        if args.match_pixel_offset is not None:
            print(f"pixel offset: {args.match_pixel_offset}")
        print(f"matching pixels: {len(match['pixels'])}")
        for pixel in match["pixels"]:
            print(f"pixel ({pixel['x']}, {pixel['y']})")
        print(f"omitted pixels: {match['omitted_pixels']}")
    if args.match_runs:
        if args.match_run_count:
            print(f"matching run count: {match['run_count']}")
        if "run_offset" in match:
            print(f"matching run offset: {match['run_offset']}")
        print(f"matching runs: {compact_json(match['runs'])}")
        if "omitted_runs" in match:
            print(f"omitted matching runs: {match['omitted_runs']}")
    elif args.match_run_count:
        print(f"matching run count: {match['run_count']}")
    if args.match_column_run_count:
        print(f"matching column run count: {match['column_run_count']}")
    if args.match_column_runs:
        if "column_run_offset" in match:
            print(f"matching column run offset: {match['column_run_offset']}")
        print(f"matching column runs: {compact_json(match['column_runs'])}")
        if "omitted_column_runs" in match:
            print(f"omitted matching column runs: {match['omitted_column_runs']}")
    if args.match_rows:
        print(f"matching rows: {compact_json(match['rows'])}")
    if args.match_columns:
        print(f"matching columns: {compact_json(match['columns'])}")
    if args.match_row_bounds:
        print(f"matching row bounds: {compact_json(match['row_bounds'])}")
    if args.match_column_bounds:
        print(f"matching column bounds: {compact_json(match['column_bounds'])}")
    if args.longest_match_run:
        run = match["longest_run"]
        print("longest matching run: none" if run is None else
              f"longest matching run: {run['x']},{run['y']},{run['length']}")
    if args.longest_match_column_run:
        run = match["longest_column_run"]
        print("longest matching column run: none" if run is None else
              f"longest matching column run: {run['x']},{run['y']},{run['length']}")
