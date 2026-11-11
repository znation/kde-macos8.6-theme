"""Scanline run reports for the reference pixel sampler."""

from __future__ import annotations

import json

if __package__:
    from tools.sample_report_common import report_context
    from tools.sample_report_pixels import (
        hex, region_alpha, region_pixels, print_region_line,
    )
else:  # run directly: python3 tools/sample.py
    from sample_report_common import report_context
    from sample_report_pixels import (
        hex, region_alpha, region_pixels, print_region_line,
    )


def _color_runs(image, x: int, y: int, width: int, height: int, alpha_aware: bool = False):
    """Collect one rectangle's same-color run segments along its single axis:
    horizontal when the region is one scanline tall, vertical otherwise; each
    segment carries its start position, length and RGB, plus the alpha value
    each pixel compares on when *alpha_aware*, so runs do not merge across
    differing alphas."""
    horizontal = height == 1
    segments = []
    alphas = region_alpha(image, x, y, width, height) if alpha_aware else None
    for offset, rgb in enumerate(region_pixels(image, x, y, width, height)):
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


def _keeps_run(run, selected_colors, excluded_colors, args) -> bool:
    """Return whether a run passes the color and length filters."""
    if selected_colors is not None and run["rgb"] not in selected_colors:
        return False
    if run["rgb"] in excluded_colors:
        return False
    if args.min_run_length is not None and run["length"] < args.min_run_length:
        return False
    if args.max_run_length is not None and run["length"] > args.max_run_length:
        return False
    return True


def _longer_run(longest, line_runs):
    """Return the longest of *longest* and the runs of one scanline; the first wins ties."""
    for run in line_runs:
        if longest is None or run["length"] > longest["length"]:
            longest = run
    return longest


def _runs_result(args, image, width: int, height: int) -> dict:
    """Assemble one run report's result mapping: scan the rectangle row by row
    or column by column, keep only the runs the color, length, offset and cap
    options admit, and fill the requested count, offset, per-scanline and
    longest-run fields."""
    context = report_context(args, width, height)
    axis = args.run_axis or ("horizontal" if args.height == 1 else "vertical")
    selected_colors = set(args.run_colors) if args.run_colors else None
    excluded_colors = set(args.excluded_run_colors) if args.excluded_run_colors else set()
    runs = []
    omitted_runs = 0
    skipped_runs = 0
    run_count = 0 if args.run_count else None
    scanline_run_counts = [] if getattr(args, "scanline_run_counts", False) else None
    track_longest = args.longest_run
    longest_run = None
    if axis == "horizontal":
        scans = ((args.x, args.y + row, args.width, 1) for row in range(args.height))
    else:
        scans = ((args.x + column, args.y, 1, args.height) for column in range(args.width))
    for x, y, scan_width, scan_height in scans:
        _, line_runs = _color_runs(image, x, y, scan_width, scan_height, args.alpha)
        if run_count is not None:
            run_count += len(line_runs)
        if scanline_run_counts is not None:
            scanline_run_counts.append(len(line_runs))
        if track_longest:
            longest_run = _longer_run(longest_run, line_runs)
        for run in line_runs:
            if not _keeps_run(run, selected_colors, excluded_colors, args):
                continue
            if args.run_offset is not None and skipped_runs < args.run_offset:
                skipped_runs += 1
                omitted_runs += 1
            elif args.max_runs is not None and len(runs) >= args.max_runs:
                omitted_runs += 1
            else:
                runs.append(run)
    result = {**context, "axis": axis, "runs": [
            {**run, "rgb": list(run["rgb"]), "hex": hex(run["rgb"])} for run in runs
        ]}
    if run_count is not None:
        result["run_count"] = run_count
    if args.max_runs is not None:
        result["omitted_runs"] = omitted_runs
    if args.run_offset is not None:
        result["run_offset"] = args.run_offset
    if scanline_run_counts is not None:
        result["scanline_run_counts"] = scanline_run_counts
    if track_longest:
        result["longest_run"] = {
            "x": longest_run["x"], "y": longest_run["y"], "length": longest_run["length"],
            "rgb": list(longest_run["rgb"]), "hex": hex(longest_run["rgb"]),
            **({"alpha": longest_run["alpha"]} if args.alpha else {}),
        }
    return result


def report_runs(args, image, width: int, height: int, header: str) -> None:
    """Print the runs report: the region's same-color runs, as JSON or plain text."""
    result = _runs_result(args, image, width, height)
    if args.json:
        print(json.dumps(result, ensure_ascii=True))
        return
    print(header)
    print_region_line(args)
    print(f"axis: {result['axis']}")
    if "longest_run" in result:
        run = result["longest_run"]
        print(f"longest run: {run['x']},{run['y']},{run['length']}")
    if "run_count" in result:
        print(f"run count: {result['run_count']}")
    if "scanline_run_counts" in result:
        print("scanline run counts: " + ", ".join(str(count) for count in result["scanline_run_counts"]))
    if "run_offset" in result:
        print(f"run offset: {result['run_offset']}")
    for run in result["runs"]:
        rgb = run["rgb"]
        suffix = f"  alpha={run['alpha']}" if args.alpha else ""
        print(f"({run['x']}, {run['y']}): {rgb[0]},{rgb[1]},{rgb[2]}  {hex(rgb)}  length={run['length']}{suffix}")
    if "omitted_runs" in result:
        print(f"omitted runs: {result['omitted_runs']}")
