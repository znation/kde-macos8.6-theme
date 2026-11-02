"""Report assembly and rendering for ``tools/fidelity.py``.

Owns the comparison report's shape: the budget-to-verdict rule, the worst
records' source-position translation, the worst-pixel explanation, and the
JSON object and text lines a run reports. Every entry point receives the
already-computed values -- images, crop rectangles, metrics, thresholds and
the optional records -- as explicit arguments, so this module performs no
image reads and no comparison work; the CLI's orchestration, argument
handling and exit-status selection stay in ``tools/fidelity.py``.
"""

from __future__ import annotations

import json
from dataclasses import asdict

if __package__:
    from tools.png import pixel_at
    from tools.terminal import escape_controls
else:  # imported as a top-level module through tools/fidelity.py's direct run
    from png import pixel_at
    from terminal import escape_controls


def budget_verdict(metrics, max_mae: float | None = None,
                   max_frac: float | None = None,
                   max_rmse: float | None = None,
                   max_delta: int | None = None) -> bool:
    """Return whether *metrics* meets the caller-set budgets.

    Every threshold the caller set is a budget that must be met. With no
    budget set the verdict falls back to the strictest one: no pixel
    differing by more than ``--tolerance``. ``--max-mae`` and ``--max-frac``
    therefore replace the default gate rather than silently defaulting to
    zero, which would require byte-exactness no matter what ``--tolerance``
    says.
    """
    budgets = []
    if max_mae is not None:
        budgets.append(metrics.mae <= max_mae)
    if max_frac is not None:
        budgets.append(metrics.frac_differing <= max_frac)
    if max_rmse is not None:
        budgets.append(metrics.rmse <= max_rmse)
    if max_delta is not None:
        budgets.append(metrics.max_delta <= max_delta)
    return all(budgets) if budgets else metrics.frac_differing <= 0.0


def locate_worst_pixels(records, candidate_crop, reference_crop):
    """Add each crop-relative record's candidate and reference positions.

    *records* come from ``tools/fidelity_pixels.py::worst_pixels``, whose
    ``x``/``y`` are relative to the compared, cropped surfaces; this appends
    the ``candidate_position`` and ``reference_position`` keys that point
    into the original images by adding each crop's origin (an omitted crop
    has origin 0,0). Returns *records* for chaining.
    """
    candidate_origin = candidate_crop[:2] if candidate_crop else (0, 0)
    reference_origin = reference_crop[:2] if reference_crop else (0, 0)
    for pixel in records:
        pixel["candidate_position"] = [pixel["x"] + candidate_origin[0],
                                        pixel["y"] + candidate_origin[1]]
        pixel["reference_position"] = [pixel["x"] + reference_origin[0],
                                        pixel["y"] + reference_origin[1]]
    return records


def explain_worst_pixel(candidate, reference, metrics, candidate_crop,
                        reference_crop):
    """Return source colors and coordinates for the comparator's worst pixel."""
    x, y = metrics.max_x, metrics.max_y
    candidate_rgb = pixel_at(candidate, x, y)
    reference_rgb = pixel_at(reference, x, y)
    candidate_alpha = candidate.alpha[y * candidate.width + x] if candidate.alpha is not None else 255
    reference_alpha = reference.alpha[y * reference.width + x] if reference.alpha is not None else 255
    candidate_rgba = [*candidate_rgb, candidate_alpha]
    reference_rgba = [*reference_rgb, reference_alpha]
    candidate_origin = (candidate_crop[0], candidate_crop[1]) if candidate_crop else (0, 0)
    reference_origin = (reference_crop[0], reference_crop[1]) if reference_crop else (0, 0)
    return {
        "position": [x, y],
        "candidate_position": [x + candidate_origin[0], y + candidate_origin[1]],
        "reference_position": [x + reference_origin[0], y + reference_origin[1]],
        "candidate_rgba": candidate_rgba,
        "reference_rgba": reference_rgba,
        "absolute_delta": [abs(a - b) for a, b in zip(candidate_rgba, reference_rgba)],
    }


def source_bounds(difference_bounds, crop_rect):
    """Translate a difference rectangle into source-image coordinates.

    *difference_bounds* is the compared, crop-relative rectangle from
    ``Metrics.difference_bounds`` (or ``None``), and *crop_rect* the crop
    it was found under (or ``None``, whose origin is 0,0).
    """
    if difference_bounds is None:
        return None
    x, y, width, height = difference_bounds
    origin_x, origin_y = crop_rect[:2] if crop_rect else (0, 0)
    return [x + origin_x, y + origin_y, width, height]


def report_data(candidate_path, reference_path, candidate_crop, reference_crop,
                tolerance, max_mae, max_frac, metrics, worst=None,
                channels=None, bias=None, explanation=None, histogram=None,
                percentiles=None, maxima=None,
                passed: bool = False, *, max_rmse: float | None = None,
                max_delta: int | None = None, rows=None, columns=None, row_bounds=None,
                column_bounds=None, runs=None, column_runs=None):
    """Assemble the comparison's JSON result object.

    Paths, crop rectangles and the three thresholds are echoed as given;
    *metrics* is serialized field for field through ``dataclasses.asdict``.
    The optional records appear only when they were requested, so a default
    run's object carries none of their keys.
    """
    result = {
        "candidate": candidate_path,
        "reference": reference_path,
        "candidate_crop": candidate_crop,
        "reference_crop": reference_crop,
        "thresholds": {"tolerance": tolerance, "max_mae": max_mae, "max_frac": max_frac},
        "metrics": asdict(metrics),
        "candidate_difference_bounds": source_bounds(metrics.difference_bounds, candidate_crop),
        "reference_difference_bounds": source_bounds(metrics.difference_bounds, reference_crop),
        "passed": passed,
    }
    if max_rmse is not None:
        result["thresholds"]["max_rmse"] = max_rmse
    if max_delta is not None:
        result["thresholds"]["max_delta"] = max_delta
    if channels is not None:
        result["channel_counts"] = channels
    if bias is not None:
        result["channel_bias"] = bias
    if maxima is not None:
        result["channel_maxima"] = maxima
    if rows is not None:
        result["difference_rows"] = rows
    if columns is not None:
        result["difference_columns"] = columns
    if row_bounds is not None:
        result["difference_row_bounds"] = row_bounds
    if column_bounds is not None:
        result["difference_column_bounds"] = column_bounds
    if runs is not None:
        result["difference_runs"] = runs
    if column_runs is not None:
        result["difference_column_runs"] = column_runs
    if histogram is not None:
        result["delta_histogram"] = histogram
    if percentiles is not None:
        result["delta_percentiles"] = percentiles
    if worst is not None:
        result["worst_pixels"] = worst
    if explanation is not None:
        result["worst_pixel"] = explanation
    return result


def render_json(result: dict) -> str:
    """Return the assembled result as one ASCII-escaped JSON line."""
    return json.dumps(result, ensure_ascii=True)


def delta_percentiles(histogram):
    """Return nearest-rank p50, p95 and p99 from ascending histogram bins."""
    total = sum(item["count"] for item in histogram)
    if total <= 0:
        raise ValueError("delta histogram must contain at least one pixel")
    result = {}
    for percentile in (50, 95, 99):
        rank = (percentile * total + 99) // 100
        cumulative = 0
        for item in histogram:
            cumulative += item["count"]
            if cumulative >= rank:
                result[f"p{percentile}"] = item["delta"]
                break
    return result


def render_text(result: dict, candidate, reference) -> list[str]:
    """Return the human report's lines in print order.

    *candidate* and *reference* carry only the compared sizes the first two
    lines print; nothing here rereads or compares pixels.
    """
    metrics = result["metrics"]
    lines = [
        f"candidate: {escape_controls(result['candidate'])}  "
        f"{candidate.width}x{candidate.height}",
        f"reference: {escape_controls(result['reference'])}  "
        f"{reference.width}x{reference.height}",
    ]
    if result["candidate_crop"] is not None:
        # The candidate line names the cropped size but not the rectangle it
        # came from, so a transcript could not be replayed without the
        # original --candidate-crop argument. Echo it; the fields are plain
        # ints from parse_crop, so no escaping is needed.
        x, y, width, height = result["candidate_crop"]
        lines.append(f"candidate crop: {x},{y},{width},{height}")
    if result["reference_crop"] is not None:
        # The reference line names the cropped size but not the rectangle it
        # came from, so a transcript could not be replayed without the
        # original --crop argument. Echo it; the fields are plain ints from
        # parse_crop, so no escaping is needed.
        x, y, width, height = result["reference_crop"]
        lines.append(f"reference crop: {x},{y},{width},{height}")
    lines.append(f"pixels compared: {metrics['pixels']}")
    lines.append(f"mean absolute error: {metrics['mae']:.4f}")
    if metrics["mae_a"] is None:
        lines.append(
            f"per-channel MAE (R, G, B): {metrics['mae_r']:.4f} "
            f"{metrics['mae_g']:.4f} {metrics['mae_b']:.4f}"
        )
    else:
        lines.append(
            f"per-channel MAE (R, G, B, A): {metrics['mae_r']:.4f} "
            f"{metrics['mae_g']:.4f} {metrics['mae_b']:.4f} "
            f"{metrics['mae_a']:.4f}"
        )
    lines.append(f"RMSE: {metrics['rmse']:.4f}")
    lines.append(
        f"max channel delta: {metrics['max_delta']} "
        f"at ({metrics['max_x']}, {metrics['max_y']})"
    )
    lines.append(
        f"differing pixels: {metrics['differing']} / {metrics['pixels']} "
        f"({metrics['frac_differing']:.6f})"
    )
    if metrics["difference_bounds"] is None:
        lines.append("difference bounds: none")
    else:
        lines.append("difference bounds: " + ",".join(map(str, metrics["difference_bounds"])))
    for name, bounds in (("candidate", result["candidate_difference_bounds"]),
                         ("reference", result["reference_difference_bounds"])):
        lines.append(f"{name} difference bounds: " + ("none" if bounds is None else ",".join(map(str, bounds))))
    worst = result.get("worst_pixels")
    if worst is not None:
        lines.append(f"worst pixels: {len(worst)}")
        for pixel in worst:
            lines.append(
                f"pixel ({pixel['x']}, {pixel['y']}): "
                f"candidate={','.join(map(str, pixel['candidate_rgba']))} "
                f"reference={','.join(map(str, pixel['reference_rgba']))} "
                f"max_delta={pixel['max_delta']} "
                f"candidate_position={','.join(map(str, pixel['candidate_position']))} "
                f"reference_position={','.join(map(str, pixel['reference_position']))}"
            )
    explanation = result.get("worst_pixel")
    if explanation is not None:
        lines.append("worst pixel: " + json.dumps(explanation, ensure_ascii=True))
    channels = result.get("channel_counts")
    if channels is not None:
        # Plain ints from the count scan, so no escaping is needed.
        lines.append(
            f"channel differing pixels (R, G, B, A): {channels['r']} "
            f"{channels['g']} {channels['b']} {channels['a']}"
        )
    bias = result.get("channel_bias")
    if bias is not None:
        lines.append("channel bias (candidate - reference): " + json.dumps(bias, ensure_ascii=True))
    maxima = result.get("channel_maxima")
    if maxima is not None:
        lines.append(f"channel maximum delta (R, G, B, A): {maxima['r']} {maxima['g']} {maxima['b']} {maxima['a']}")
    histogram = result.get("delta_histogram")
    if histogram is not None:
        lines.append("delta histogram: " + json.dumps(histogram, ensure_ascii=True))
    percentiles = result.get("delta_percentiles")
    if percentiles is not None:
        lines.append("delta percentiles: " + json.dumps(percentiles, ensure_ascii=True))
    rows = result.get("difference_rows")
    if rows is not None:
        lines.append("difference rows: " + json.dumps(rows, ensure_ascii=True))
    columns = result.get("difference_columns")
    if columns is not None:
        lines.append("difference columns: " + json.dumps(columns, ensure_ascii=True))
    row_bounds = result.get("difference_row_bounds")
    if row_bounds is not None:
        lines.append("difference row bounds: " + json.dumps(row_bounds, ensure_ascii=True))
    column_bounds = result.get("difference_column_bounds")
    if column_bounds is not None:
        lines.append("difference column bounds: " + json.dumps(column_bounds, ensure_ascii=True))
    runs = result.get("difference_runs")
    if runs is not None:
        lines.append("difference runs: " + json.dumps(runs, ensure_ascii=True))
    column_runs = result.get("difference_column_runs")
    if column_runs is not None:
        lines.append("difference column runs: " + json.dumps(column_runs, ensure_ascii=True))
    thresholds = result["thresholds"]
    verdict = "PASS" if result["passed"] else "FAIL"
    mae_budget = "unset" if thresholds["max_mae"] is None else f"{thresholds['max_mae']:.4f}"
    fraction_budget = "unset" if thresholds["max_frac"] is None else f"{thresholds['max_frac']:.6f}"
    rmse_budget = thresholds.get("max_rmse")
    rmse_clause = "" if rmse_budget is None else f"max-rmse={rmse_budget:.4f} "
    delta_budget = thresholds.get("max_delta")
    delta_clause = "" if delta_budget is None else f"max-delta={delta_budget} "
    lines.append(
        f"{verdict}: max-mae={mae_budget} max-frac={fraction_budget} "
        f"{rmse_clause}"
        f"{delta_clause}"
        f"tolerance={thresholds['tolerance']}"
    )
    return lines
