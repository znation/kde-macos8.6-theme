"""Command-line fidelity comparison for the Mac OS 8.6 Plasma theme.

Compares a rendered PNG surface against a reference screenshot and reports the
comparison metrics from the sibling ``tools/fidelity_metrics.py``: mean
absolute error, per-channel mean absolute error (R, G, B, A), RMSE, the worst
per-channel delta and where it occurs, and the fraction of differing pixels.

This entry point owns orchestration only: parsing via the sibling
``tools/fidelity_cli_parser.py``, the reads and comparison, and the exit-status
selection. The report's data assembly and
JSON/text rendering live in the sibling ``tools/fidelity_reports.py``, and
the metrics themselves in ``tools/fidelity_metrics.py``.

Only PNG is read, so the harness crops a reference screenshot to a surface and
saves it as PNG before comparing. The Plasma render step that produces the
candidate image is outside this tool; ``tools/render_surface.py`` does it.

Usage::

    python3 tools/fidelity.py CANDIDATE REFERENCE [--candidate-crop X,Y,W,H]
        [--crop X,Y,W,H] [--max-mae F] [--max-frac F] [--max-rmse F]
        [--max-delta N] [--max-differing N] [--tolerance N]

    The verdict passes when every threshold set with ``--max-mae``/``--max-frac``/``--max-rmse``/``--max-delta``/``--max-differing``
is met; when neither is set it passes only when no pixel differs from the
reference by more than ``--tolerance``.

Exit status: 0 when the comparison passes, 1 when it fails, 2 usage or
read error.
"""

from __future__ import annotations

import sys

if __package__:
    from tools.fidelity_cli_parser import build_parser
    from tools.fidelity_sources import read_source as _read_source
    from tools.diagnostics import report_error
    from tools.fidelity_metrics import (
        FidelityError,
        compare,
        crop,
    )
    from tools.fidelity_pixels import worst_pixels, channel_counts, channel_bias, channel_maxima, delta_histogram, difference_rows, difference_columns, difference_row_bounds, difference_column_bounds, difference_runs, difference_column_runs
    from tools.fidelity_reports import (
        budget_verdict,
        delta_percentiles,
        explain_worst_pixel,
        locate_worst_pixels,
        report_data,
        render_json,
        render_text,
    )
    from tools.png import PngError
else:  # run directly: python3 tools/fidelity.py
    from fidelity_cli_parser import build_parser
    from fidelity_sources import read_source as _read_source
    from diagnostics import report_error
    from fidelity_metrics import FidelityError, compare, crop
    from fidelity_pixels import worst_pixels, channel_counts, channel_bias, channel_maxima, delta_histogram, difference_rows, difference_columns, difference_row_bounds, difference_column_bounds, difference_runs, difference_column_runs
    from fidelity_reports import (
        budget_verdict,
        delta_percentiles,
        explain_worst_pixel,
        locate_worst_pixels,
        report_data,
        render_json,
        render_text,
    )
    from png import PngError


def main(argv: list[str] | None = None) -> int:
    """Run the comparison CLI; *argv* is the argument list without a program name.

    Following ``argparse`` and the sibling ``tools/check_references.py``,
    ``None`` reads ``sys.argv``.
    """
    args = build_parser().parse_args(argv)

    try:
        candidate = _read_source(args.candidate, args.candidate_crop)
        reference = _read_source(args.reference, args.crop)
        if args.candidate_crop is not None:
            candidate = crop(candidate, *args.candidate_crop)
        if args.crop is not None:
            reference = crop(reference, *args.crop)
        metrics = compare(candidate, reference, tolerance=args.tolerance)
        worst = (worst_pixels(candidate, reference, args.tolerance, args.worst_pixels)
                 if args.worst_pixels is not None else None)
        # The optional records' source positions are report data, so they are
        # translated beside the rendering, not next to the scan.
        if worst is not None:
            worst = locate_worst_pixels(worst, args.candidate_crop, args.crop)
        # The per-channel count scan only runs when it was asked for: it adds
        # a whole-image pass, so the default output must not pay for it.
        channels = (channel_counts(candidate, reference, args.tolerance)
                    if args.channel_counts else None)
        bias = channel_bias(candidate, reference) if args.channel_bias else None
        maxima = channel_maxima(candidate, reference) if args.channel_maxima else None
        rows = difference_rows(candidate, reference, args.tolerance) if args.difference_rows else None
        columns = difference_columns(candidate, reference, args.tolerance) if args.difference_columns else None
        row_bounds = (difference_row_bounds(candidate, reference, args.tolerance)
                      if args.difference_row_bounds else None)
        column_bounds = (difference_column_bounds(candidate, reference, args.tolerance)
                         if args.difference_column_bounds else None)
        runs = difference_runs(candidate, reference, args.tolerance) if args.difference_runs else None
        column_runs = (difference_column_runs(candidate, reference, args.tolerance)
                       if args.difference_column_runs else None)
        histogram = (delta_histogram(candidate, reference)
                     if args.delta_histogram or args.delta_percentiles else None)
        explanation = (explain_worst_pixel(candidate, reference, metrics,
                                             args.candidate_crop, args.crop)
                       if args.explain_worst else None)
    except (PngError, FidelityError, ValueError) as exc:
        return report_error("fidelity", str(exc))

    ok = budget_verdict(metrics, args.max_mae, args.max_frac,
                        max_rmse=args.max_rmse, max_delta=args.max_delta,
                        max_differing=args.max_differing)
    result = report_data(args.candidate, args.reference, args.candidate_crop,
                         args.crop, args.tolerance, args.max_mae, args.max_frac,
                         metrics, worst=worst, channels=channels,
                         bias=bias,
                         maxima=maxima,
                         rows=rows,
                         columns=columns,
                         row_bounds=row_bounds,
                         column_bounds=column_bounds,
                         runs=runs,
                         column_runs=column_runs,
                         explanation=explanation,
                         histogram=histogram if args.delta_histogram else None,
                         percentiles=(delta_percentiles(histogram)
                                      if args.delta_percentiles else None),
                         passed=ok, max_rmse=args.max_rmse,
                         max_delta=args.max_delta,
                         max_differing=args.max_differing)
    if args.json:
        print(render_json(result))
        return 0 if ok else 1
    for line in render_text(result, candidate, reference):
        print(line)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
