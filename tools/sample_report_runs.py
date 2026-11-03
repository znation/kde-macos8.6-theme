"""Scanline run reports for the reference pixel sampler."""

from __future__ import annotations

import json

if __package__:
    from tools.sample_report_pixels import _hex, _region_alpha, _region_pixels
else:  # run directly: python3 tools/sample.py
    from sample_report_pixels import _hex, _region_alpha, _region_pixels


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


def _runs_result(args, image, width: int, height: int) -> dict:
    region = {"x": args.x, "y": args.y, "width": args.width, "height": args.height}
    axis = args.run_axis or ("horizontal" if args.height == 1 else "vertical")
    selected_colors = set(args.run_colors) if args.run_colors else None
    excluded_colors = set(args.excluded_run_colors) if args.excluded_run_colors else set()
    runs = []
    run_count = 0 if args.run_count else None
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
        if track_longest:
            for run in line_runs:
                if longest_run is None or run["length"] > longest_run["length"]:
                    longest_run = run
        runs.extend(run for run in line_runs
                    if (selected_colors is None or run["rgb"] in selected_colors)
                    if run["rgb"] not in excluded_colors
                    if (args.min_run_length is None or run["length"] >= args.min_run_length)
                    and (args.max_run_length is None or run["length"] <= args.max_run_length))
    result = {"image": args.image, "image_width": width, "image_height": height,
        "region": region, "axis": axis, "runs": [
            {**run, "rgb": list(run["rgb"]), "hex": _hex(run["rgb"])} for run in runs
        ]}
    if run_count is not None:
        result["run_count"] = run_count
    if track_longest:
        result["longest_run"] = {
            "x": longest_run["x"], "y": longest_run["y"], "length": longest_run["length"],
            "rgb": list(longest_run["rgb"]), "hex": _hex(longest_run["rgb"]),
            **({"alpha": longest_run["alpha"]} if args.alpha else {}),
        }
    return result


def report_runs(args, image, width: int, height: int, header: str) -> None:
    result = _runs_result(args, image, width, height)
    if args.json:
        print(json.dumps(result, ensure_ascii=True))
        return
    print(header)
    region = result["region"]
    print(f"region ({region['x']}, {region['y']}) {region['width']}x{region['height']}:")
    print(f"axis: {result['axis']}")
    if "longest_run" in result:
        run = result["longest_run"]
        print(f"longest run: {run['x']},{run['y']},{run['length']}")
    if "run_count" in result:
        print(f"run count: {result['run_count']}")
    for run in result["runs"]:
        rgb = run["rgb"]
        suffix = f"  alpha={run['alpha']}" if args.alpha else ""
        print(f"({run['x']}, {run['y']}): {rgb[0]},{rgb[1]},{rgb[2]}  {_hex(rgb)}  length={run['length']}{suffix}")
