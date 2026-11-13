"""Command-line fidelity comparison for the Mac OS 8.6 Plasma theme.

Compares a rendered PNG surface against a reference screenshot and reports the
comparison metrics from the sibling ``tools/fidelity_metrics.py``: mean
absolute error, per-channel mean absolute error (R, G, B, A), RMSE, the worst
per-channel delta and where it occurs, and the fraction of differing pixels.

This entry point owns orchestration only: parsing and option validation
via the sibling ``tools/fidelity_cli_parser.py``, the reads and
comparison, the scan selection for each requested report, and the
exit-status selection. The report's data assembly and
JSON/text rendering live in the sibling ``tools/fidelity_rendering.py``,
the difference-run families' paging and filtering in
``tools/fidelity_run_family.py``, and
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
    from tools.fidelity_cli_parser import build_parser, validate_options
    from tools.fidelity_sources import read_source as _read_source
    from tools.diagnostics import report_error
    from tools.fidelity_geometry import FidelityError, crop
    from tools.fidelity_metrics import compare
    from tools.fidelity_pixels import channel_deltas, worst_pixels, channel_counts, channel_bias, channel_maxima, delta_histogram
    from tools.fidelity_spatial import differing_flags, difference_rows, difference_columns, difference_row_bounds, difference_column_bounds, difference_centroid
    from tools.fidelity_run_family import (COLUMN_RUN_CALLS,
                                           collect_run_family,
                                           HORIZONTAL_RUN_CALLS)
    from tools.fidelity_reports import (
        budget_verdict,
        delta_percentiles,
        explain_worst_pixel,
        locate_worst_pixels,
        report_data,
    )
    from tools.fidelity_rendering import render_json, render_text
    from tools.png import PngError
else:  # run directly: python3 tools/fidelity.py
    from fidelity_cli_parser import build_parser, validate_options
    from fidelity_sources import read_source as _read_source
    from diagnostics import report_error
    from fidelity_geometry import FidelityError, crop
    from fidelity_metrics import compare
    from fidelity_pixels import channel_deltas, worst_pixels, channel_counts, channel_bias, channel_maxima, delta_histogram
    from fidelity_spatial import differing_flags, difference_rows, difference_columns, difference_row_bounds, difference_column_bounds, difference_centroid
    from fidelity_run_family import (COLUMN_RUN_CALLS,
                                     collect_run_family,
                                     HORIZONTAL_RUN_CALLS)
    from fidelity_reports import (
        budget_verdict,
        delta_percentiles,
        explain_worst_pixel,
        locate_worst_pixels,
        report_data,
    )
    from fidelity_rendering import render_json, render_text
    from png import PngError


def main(argv: list[str] | None = None) -> int:
    """Run the comparison CLI; *argv* is the argument list without a program name.

    Following ``argparse`` and the sibling ``tools/check_references.py``,
    ``None`` reads ``sys.argv``.
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    validate_options(parser, args)

    try:
        candidate = _read_source(args.candidate, args.candidate_crop)
        reference = _read_source(args.reference, args.crop)
        if args.candidate_crop is not None:
            candidate = crop(candidate, *args.candidate_crop)
        if args.crop is not None:
            reference = crop(reference, *args.crop)
        wants_flags = (
            args.difference_rows or args.difference_columns
            or args.difference_row_bounds or args.difference_column_bounds
            or args.difference_runs or args.difference_run_count
            or args.longest_difference_run or args.difference_column_runs
            or args.difference_column_run_count
            or args.longest_difference_column_run or args.difference_centroid
        )
        # One channel-delta pass serves the metrics comparison and every
        # pixel report plus the flag scan for the spatial reports: it derives
        # each pixel's per-channel deltas once and ``compare`` -- which would
        # otherwise build the same list a second time -- reads the same
        # strings. Any requested pixel or spatial option turns it on; the
        # default output, which reads none of them and only the metrics,
        # pays nothing.
        wants_deltas = (wants_flags or args.worst_pixels is not None
                        or args.channel_counts or args.channel_maxima
                        or args.delta_histogram or args.delta_percentiles)
        deltas = channel_deltas(candidate, reference) if wants_deltas else None
        metrics = compare(candidate, reference, tolerance=args.tolerance,
                          deltas=deltas)
        worst = (worst_pixels(candidate, reference, args.tolerance,
                              args.worst_pixels,
                              offset=args.worst_pixel_offset,
                              deltas=deltas)
                 if args.worst_pixels is not None else None)
        # The optional records' source positions are report data, so they are
        # translated beside the rendering, not next to the scan.
        if worst is not None:
            worst = locate_worst_pixels(worst, args.candidate_crop, args.crop)
        # The per-channel count scan only runs when it was asked for: it adds
        # a whole-image pass, so the default output must not pay for it.
        channels = (channel_counts(candidate, reference, args.tolerance,
                                   deltas=deltas)
                    if args.channel_counts else None)
        bias = channel_bias(candidate, reference) if args.channel_bias else None
        maxima = (channel_maxima(candidate, reference, deltas=deltas)
                  if args.channel_maxima else None)
        # One flags pass serves every spatial report the run requested: it
        # consumes the shared channel-delta list derived above -- spatial
        # and pixel families read the same per-channel strings -- and each
        # scanline report reads the same string. Any requested spatial
        # option turns it on; the default output, which reads none of them,
        # pays nothing.
        flags = (differing_flags(candidate, reference, args.tolerance,
                                 deltas=deltas)
                 if wants_flags else None)
        rows = (difference_rows(candidate, reference, args.tolerance, flags=flags)
                if args.difference_rows else None)
        columns = (difference_columns(candidate, reference, args.tolerance, flags=flags)
                   if args.difference_columns else None)
        row_bounds = (difference_row_bounds(candidate, reference, args.tolerance,
                                            flags=flags)
                      if args.difference_row_bounds else None)
        column_bounds = (difference_column_bounds(candidate, reference, args.tolerance,
                                                  flags=flags)
                         if args.difference_column_bounds else None)
        # The horizontal and vertical difference-run families share one
        # assembly recipe; the sibling tools/fidelity_run_family.py owns it.
        horizontal = collect_run_family(
            candidate, reference, args.tolerance, flags, HORIZONTAL_RUN_CALLS,
            enabled=args.difference_runs,
            minimum=args.min_difference_run_length,
            maximum=args.max_difference_run_length,
            cap=args.max_difference_runs,
            offset=args.difference_run_offset,
            wants_count=args.difference_run_count,
            wants_longest=args.longest_difference_run)
        column = collect_run_family(
            candidate, reference, args.tolerance, flags, COLUMN_RUN_CALLS,
            enabled=args.difference_column_runs,
            minimum=args.min_difference_column_run_length,
            maximum=args.max_difference_column_run_length,
            cap=args.max_difference_column_runs,
            offset=args.difference_column_run_offset,
            wants_count=args.difference_column_run_count,
            wants_longest=args.longest_difference_column_run)
        centroid = (difference_centroid(candidate, reference, args.tolerance,
                                        flags=flags)
                    if args.difference_centroid else None)
        histogram = (delta_histogram(candidate, reference, deltas=deltas)
                     if args.delta_histogram or args.delta_percentiles else None)
        explanation = (explain_worst_pixel(candidate, reference, metrics,
                                             args.candidate_crop, args.crop)
                       if args.explain_worst else None)
    except (PngError, FidelityError, ValueError) as exc:
        return report_error("fidelity", str(exc))

    ok = budget_verdict(metrics, args.max_mae, args.max_frac,
                        max_rmse=args.max_rmse, max_delta=args.max_delta,
                        max_differing=args.max_differing)
    if args.quiet:
        return 0 if ok else 1
    result = report_data(args.candidate, args.reference, args.candidate_crop,
                         args.crop, args.tolerance, args.max_mae, args.max_frac,
                         metrics, worst=worst, channels=channels,
                         bias=bias,
                         maxima=maxima,
                         rows=rows,
                         columns=columns,
                         row_bounds=row_bounds,
                         column_bounds=column_bounds,
                         runs=horizontal.runs,
                         omitted_difference_runs=horizontal.omitted,
                         difference_run_offset=args.difference_run_offset,
                         run_count=horizontal.count,
                         column_run_count=column.count,
                         column_runs=column.runs,
                         omitted_difference_column_runs=column.omitted,
                         difference_column_run_offset=args.difference_column_run_offset,
                         explanation=explanation,
                         histogram=histogram if args.delta_histogram else None,
                         percentiles=(delta_percentiles(histogram)
                                      if args.delta_percentiles else None),
                         passed=ok, max_rmse=args.max_rmse,
                         max_delta=args.max_delta,
                         max_differing=args.max_differing,
                         centroid=centroid,
                         include_centroid=args.difference_centroid,
                         longest_run=horizontal.longest,
                         include_longest_run=args.longest_difference_run,
                         longest_column_run=column.longest,
                         include_longest_column_run=args.longest_difference_column_run)
    if args.json:
        print(render_json(result))
        return 0 if ok else 1
    for line in render_text(result, candidate, reference):
        print(line)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
