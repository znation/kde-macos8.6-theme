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


def report_runs(args, image, width: int, height: int, header: str) -> None:
    region = {"x": args.x, "y": args.y, "width": args.width, "height": args.height}
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
