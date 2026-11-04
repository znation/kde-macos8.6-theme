"""Text and JSON rendering for fidelity comparison reports."""

from __future__ import annotations

import json

if __package__:
    from tools.terminal import escape_controls
else:  # imported as a top-level module through tools/fidelity.py's direct run
    from terminal import escape_controls


def render_json(result: dict) -> str:
    """Return the assembled result as one ASCII-escaped JSON line."""
    return json.dumps(result, ensure_ascii=True)


def render_text(result: dict, candidate, reference) -> list[str]:
    """Format the report using only report data and image dimensions."""
    metrics = result["metrics"]
    lines = [
        f"candidate: {escape_controls(result['candidate'])}  {candidate.width}x{candidate.height}",
        f"reference: {escape_controls(result['reference'])}  {reference.width}x{reference.height}",
    ]
    for key, label in (("candidate_crop", "candidate"), ("reference_crop", "reference")):
        crop = result[key]
        if crop is not None:
            lines.append(f"{label} crop: " + ",".join(map(str, crop)))
    lines.append(f"pixels compared: {metrics['pixels']}")
    lines.append(f"mean absolute error: {metrics['mae']:.4f}")
    if metrics["mae_a"] is None:
        lines.append(f"per-channel MAE (R, G, B): {metrics['mae_r']:.4f} {metrics['mae_g']:.4f} {metrics['mae_b']:.4f}")
    else:
        lines.append(f"per-channel MAE (R, G, B, A): {metrics['mae_r']:.4f} {metrics['mae_g']:.4f} {metrics['mae_b']:.4f} {metrics['mae_a']:.4f}")
    lines.extend((
        f"RMSE: {metrics['rmse']:.4f}",
        f"max channel delta: {metrics['max_delta']} at ({metrics['max_x']}, {metrics['max_y']})",
        f"differing pixels: {metrics['differing']} / {metrics['pixels']} ({metrics['frac_differing']:.6f})",
    ))
    bounds = metrics["difference_bounds"]
    lines.append("difference bounds: " + ("none" if bounds is None else ",".join(map(str, bounds))))
    for name in ("candidate", "reference"):
        bounds = result[f"{name}_difference_bounds"]
        lines.append(f"{name} difference bounds: " + ("none" if bounds is None else ",".join(map(str, bounds))))
    worst = result.get("worst_pixels")
    if worst is not None:
        lines.append(f"worst pixels: {len(worst)}")
        for pixel in worst:
            lines.append(
                f"pixel ({pixel['x']}, {pixel['y']}): candidate={','.join(map(str, pixel['candidate_rgba']))} "
                f"reference={','.join(map(str, pixel['reference_rgba']))} max_delta={pixel['max_delta']} "
                f"candidate_position={','.join(map(str, pixel['candidate_position']))} "
                f"reference_position={','.join(map(str, pixel['reference_position']))}"
            )
    explanation = result.get("worst_pixel")
    if explanation is not None:
        lines.append("worst pixel: " + json.dumps(explanation, ensure_ascii=True))
    channels = result.get("channel_counts")
    if channels is not None:
        lines.append(f"channel differing pixels (R, G, B, A): {channels['r']} {channels['g']} {channels['b']} {channels['a']}")
    bias = result.get("channel_bias")
    if bias is not None:
        lines.append("channel bias (candidate - reference): " + json.dumps(bias, ensure_ascii=True))
    maxima = result.get("channel_maxima")
    if maxima is not None:
        lines.append(f"channel maximum delta (R, G, B, A): {maxima['r']} {maxima['g']} {maxima['b']} {maxima['a']}")
    for key, label in (("delta_histogram", "delta histogram"), ("delta_percentiles", "delta percentiles"),
                       ("difference_rows", "difference rows"), ("difference_columns", "difference columns"),
                       ("difference_row_bounds", "difference row bounds"),
                       ("difference_column_bounds", "difference column bounds")):
        value = result.get(key)
        if value is not None:
            lines.append(f"{label}: " + json.dumps(value, ensure_ascii=True))
    if "difference_run_count" in result:
        lines.append(f"difference run count: {result['difference_run_count']}")
    if "difference_column_run_count" in result:
        lines.append(f"difference column run count: {result['difference_column_run_count']}")
    if result.get("difference_column_runs") is not None:
        lines.append("difference column runs: " + json.dumps(result["difference_column_runs"], ensure_ascii=True))
    if "omitted_difference_column_runs" in result:
        lines.append(f"omitted difference column runs: {result['omitted_difference_column_runs']}")
    if result.get("difference_runs") is not None:
        lines.append("difference runs: " + json.dumps(result["difference_runs"], ensure_ascii=True))
    if "omitted_difference_runs" in result:
        lines.append(f"omitted difference runs: {result['omitted_difference_runs']}")
    if "difference_centroid" in result:
        lines.append("difference centroid: " + json.dumps(result["difference_centroid"], ensure_ascii=True))
    if "longest_difference_run" in result:
        lines.append("longest difference run: " + json.dumps(result["longest_difference_run"], ensure_ascii=True))
    if "longest_difference_column_run" in result:
        lines.append("longest difference column run: " + json.dumps(result["longest_difference_column_run"], ensure_ascii=True))
    thresholds = result["thresholds"]
    verdict = "PASS" if result["passed"] else "FAIL"
    mae = "unset" if thresholds["max_mae"] is None else f"{thresholds['max_mae']:.4f}"
    fraction = "unset" if thresholds["max_frac"] is None else f"{thresholds['max_frac']:.6f}"
    rmse = thresholds.get("max_rmse")
    delta = thresholds.get("max_delta")
    differing = thresholds.get("max_differing")
    lines.append(
        f"{verdict}: max-mae={mae} max-frac={fraction} "
        f"{'' if rmse is None else f'max-rmse={rmse:.4f} '}"
        f"{'' if delta is None else f'max-delta={delta} '}"
        f"{'' if differing is None else f'max-differing={differing} '}"
        f"tolerance={thresholds['tolerance']}"
    )
    return lines
