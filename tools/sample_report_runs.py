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
    runs = []
    if axis == "horizontal":
        scans = ((args.x, args.y + row, args.width, 1) for row in range(args.height))
    else:
        scans = ((args.x + column, args.y, 1, args.height) for column in range(args.width))
    for x, y, scan_width, scan_height in scans:
        _, line_runs = _color_runs(image, x, y, scan_width, scan_height, args.alpha)
        runs.extend(run for run in line_runs
                    if args.min_run_length is None or run["length"] >= args.min_run_length)
    return {"image": args.image, "image_width": width, "image_height": height,
        "region": region, "axis": axis, "runs": [
            {**run, "rgb": list(run["rgb"]), "hex": _hex(run["rgb"])} for run in runs
        ]}


def report_runs(args, image, width: int, height: int, header: str) -> None:
    result = _runs_result(args, image, width, height)
    if args.json:
        print(json.dumps(result, ensure_ascii=True))
        return
    print(header)
    region = result["region"]
    print(f"region ({region['x']}, {region['y']}) {region['width']}x{region['height']}:")
    print(f"axis: {result['axis']}")
    for run in result["runs"]:
        rgb = run["rgb"]
        suffix = f"  alpha={run['alpha']}" if args.alpha else ""
        print(f"({run['x']}, {run['y']}): {rgb[0]},{rgb[1]},{rgb[2]}  {_hex(rgb)}  length={run['length']}{suffix}")
