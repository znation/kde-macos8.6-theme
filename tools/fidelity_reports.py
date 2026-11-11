"""Report assembly and diagnostic helpers for ``tools/fidelity.py``.

Owns the comparison report's shape: the budget-to-verdict rule, the worst
records' source-position translation, the worst-pixel explanation, and the
JSON report object. Every entry point receives the
already-computed values -- images, crop rectangles, metrics, thresholds and
the optional records -- as explicit arguments, so this module performs no
image reads and no comparison work. Text and JSON rendering live in
``tools/fidelity_rendering.py``; CLI orchestration, argument handling and
exit-status selection stay in ``tools/fidelity.py``.
"""

from __future__ import annotations

from dataclasses import asdict

if __package__:
    from tools.png import pixel_at
else:  # imported as a top-level module through tools/fidelity.py's direct run
    from png import pixel_at


def budget_verdict(metrics, max_mae: float | None = None,
                   max_frac: float | None = None,
                   max_rmse: float | None = None,
                   max_delta: int | None = None,
                   max_differing: int | None = None) -> bool:
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
    if max_differing is not None:
        budgets.append(metrics.differing <= max_differing)
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
                max_delta: int | None = None, max_differing: int | None = None,
                rows=None, columns=None, row_bounds=None,
                column_bounds=None, runs=None, column_runs=None,
                centroid=None, include_centroid: bool = False,
                longest_run=None, include_longest_run: bool = False,
                run_count: int | None = None,
                omitted_difference_runs: int | None = None,
                difference_run_offset: int | None = None,
                omitted_difference_column_runs: int | None = None,
                difference_column_run_offset: int | None = None,
                longest_column_run=None, include_longest_column_run: bool = False,
                column_run_count: int | None = None):
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
    if max_differing is not None:
        result["thresholds"]["max_differing"] = max_differing
    diagnostics = (
        ("channel_counts", channels),
        ("channel_bias", bias),
        ("channel_maxima", maxima),
        ("difference_rows", rows),
        ("difference_columns", columns),
        ("difference_row_bounds", row_bounds),
        ("difference_column_bounds", column_bounds),
        ("difference_runs", runs),
        ("difference_column_runs", column_runs),
        ("delta_histogram", histogram),
        ("delta_percentiles", percentiles),
        ("worst_pixels", worst),
        ("worst_pixel", explanation),
    )
    for key, value in diagnostics:
        if value is not None:
            result[key] = value
    if include_centroid:
        result["difference_centroid"] = centroid
    if include_longest_run:
        result["longest_difference_run"] = longest_run
    if run_count is not None:
        result["difference_run_count"] = run_count
    if column_run_count is not None:
        result["difference_column_run_count"] = column_run_count
    if omitted_difference_runs is not None:
        result["omitted_difference_runs"] = omitted_difference_runs
    if difference_run_offset is not None:
        result["difference_run_offset"] = difference_run_offset
    if omitted_difference_column_runs is not None:
        result["omitted_difference_column_runs"] = omitted_difference_column_runs
    if difference_column_run_offset is not None:
        result["difference_column_run_offset"] = difference_column_run_offset
    if include_longest_column_run:
        result["longest_difference_column_run"] = longest_column_run
    return result


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


__all__ = ["budget_verdict", "delta_percentiles", "explain_worst_pixel",
           "locate_worst_pixels", "report_data", "source_bounds"]

# The JSON and text serializers are owned by fidelity_rendering.
