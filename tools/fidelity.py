"""Command-line fidelity comparison for the Mac OS 8.6 Plasma theme.

Compares a rendered PNG surface against a reference screenshot and reports the
comparison metrics from the sibling ``tools/fidelity_metrics.py``: mean
absolute error, per-channel mean absolute error (R, G, B, A), RMSE, the worst
per-channel delta and where it occurs, and the fraction of differing pixels.

This entry point owns orchestration only: argument handling, the reads and
comparison, and the exit-status selection. The report's data assembly and
JSON/text rendering live in the sibling ``tools/fidelity_reports.py``, and
the metrics themselves in ``tools/fidelity_metrics.py``.

Only PNG is read, so the harness crops a reference screenshot to a surface and
saves it as PNG before comparing. The Plasma render step that produces the
candidate image is outside this tool; ``tools/render_surface.py`` does it.

Usage::

    python3 tools/fidelity.py CANDIDATE REFERENCE [--candidate-crop X,Y,W,H]
        [--crop X,Y,W,H] [--max-mae F] [--max-frac F] [--max-rmse F]
        [--max-delta N] [--tolerance N]

    The verdict passes when every threshold set with ``--max-mae``/``--max-frac``/``--max-rmse``/``--max-delta``
is met; when neither is set it passes only when no pixel differs from the
reference by more than ``--tolerance``.

Exit status: 0 when the comparison passes, 1 when it fails, 2 usage or
read error.
"""

from __future__ import annotations

import sys
import argparse

if __package__:
    from tools.argument_parsing import EscapingArgumentParser
    from tools.fidelity_arguments import parse_crop, max_mae, max_frac, max_rmse, max_delta, tolerance
    from tools.containment import require_within_repo
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
    from tools.png import PngError, read_png
    from tools.repo_root import ROOT
else:  # run directly: python3 tools/fidelity.py
    from argument_parsing import EscapingArgumentParser
    from fidelity_arguments import parse_crop, max_mae, max_frac, max_rmse, max_delta, tolerance
    from containment import require_within_repo
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
    from png import PngError, read_png
    from repo_root import ROOT


def _read_source(path: str, crop_rect: tuple[int, int, int, int] | None):
    """Read *path*, decoding only the scanlines *crop_rect* needs when given.

    ``crop`` slices the decoded pixel rows afterwards, so rows below the crop's
    bottom edge would be decoded and thrown away. Passing ``max_rows`` lets the
    PNG decoder skip their predictor work while still inflating and validating
    the whole stream, which saves seconds on a large Paeth-filtered reference.
    The bound shortens the returned height, so a rectangle that overflows the
    image sideways is re-read whole; ``crop`` then reports it against the real
    width and height as before. A rectangle that overflows vertically is
    already read whole because the decoder clamps the bound to the height.
    The alpha plane is decoded too, so a transparent candidate cannot compare
    equal to an opaque reference.

    A repository path that resolves outside the repository (a checked-in
    symlink) is refused before it is read: the report's worst-delta values and
    the pass/fail status would otherwise let a private image be probed against
    a known candidate.
    """
    require_within_repo(path, ROOT)
    if crop_rect is None:
        return read_png(path, alpha=True)
    x, y, width, height = crop_rect
    image = read_png(path, max_rows=y + height, alpha=True)
    if x + width > image.width:
        # The crop is rejected either way; re-read unbounded only so its
        # diagnostic names the file's real height rather than the bound's.
        return read_png(path, alpha=True)
    return image


def main(argv: list[str] | None = None) -> int:
    """Run the comparison CLI; *argv* is the argument list without a program name.

    Following ``argparse`` and the sibling ``tools/check_references.py``,
    ``None`` reads ``sys.argv``.
    """
    parser = EscapingArgumentParser(
        prog="fidelity",
        description="Measure a rendered PNG surface against a reference PNG.",
        epilog=(
            "exit status: 0 when the comparison passes, 1 when it fails, "
            "2 usage or read error; passes when every --max-mae/--max-frac/--max-rmse/--max-delta "
            "threshold set is met, and otherwise when no pixel differs "
            "beyond --tolerance"
        ),
    )
    parser.add_argument("candidate", help="rendered surface image (PNG)")
    parser.add_argument("reference", help="reference image (PNG)")
    parser.add_argument("--json", action="store_true", help="emit comparison as JSON")
    def worst_pixel_limit(value: str) -> int:
        if not value or not value.isascii() or not value.isdecimal():
            raise argparse.ArgumentTypeError("--worst-pixels must be an ASCII integer from 1 to 1000")
        number = int(value)
        if not 1 <= number <= 1000:
            raise argparse.ArgumentTypeError("--worst-pixels must be an ASCII integer from 1 to 1000")
        return number

    parser.add_argument("--worst-pixels", type=worst_pixel_limit, metavar="N",
                        help="list up to N worst differing pixels (1-1000)")
    parser.add_argument("--channel-counts", action="store_true",
                        help=(
                            "count the pixels each channel differs beyond "
                            "--tolerance on; the counts overlap, so they must "
                            "not be summed"
                        ))
    parser.add_argument("--channel-bias", action="store_true",
                        help="report signed mean candidate-minus-reference RGBA byte deltas")
    parser.add_argument("--channel-maxima", action="store_true",
                        help="report maximum absolute byte delta for each RGBA channel")
    parser.add_argument("--difference-rows", action="store_true",
                        help="count pixels differing beyond --tolerance in each compared row")
    parser.add_argument("--difference-columns", action="store_true",
                        help="count pixels differing beyond --tolerance in each compared column")
    parser.add_argument("--difference-row-bounds", action="store_true",
                        help="locate each row's horizontal interval of pixels differing beyond --tolerance")
    parser.add_argument("--difference-column-bounds", action="store_true",
                        help="locate each column's vertical interval of pixels differing beyond --tolerance")
    parser.add_argument("--difference-runs", action="store_true",
                        help="locate disjoint horizontal runs of pixels differing beyond --tolerance")
    parser.add_argument("--difference-column-runs", action="store_true",
                        help="locate disjoint vertical runs of pixels differing beyond --tolerance")
    parser.add_argument("--delta-histogram", action="store_true",
                        help="count compared pixels by maximum RGBA channel delta")
    parser.add_argument("--delta-percentiles", action="store_true",
                        help="report median, p95 and p99 maximum RGBA deltas")
    parser.add_argument("--explain-worst", action="store_true",
                        help="show source RGBA values at the maximum-delta pixel")
    parser.add_argument(
        "--candidate-crop",
        type=parse_crop,
        metavar="X,Y,W,H",
        help="crop the candidate to this region before comparing",
    )
    parser.add_argument(
        "--crop",
        type=parse_crop,
        metavar="X,Y,W,H",
        help="crop the reference to this region before comparing",
    )
    parser.add_argument(
        "--tolerance",
        type=tolerance,
        default=0,
        help="per-channel delta (0-255) at or below which a pixel is not 'differing'",
    )
    parser.add_argument(
        "--max-mae",
        type=max_mae,
        default=None,
        help=(
            "fail when mean absolute error exceeds this (0-255); when set, "
            "replaces the default no-differing-pixel gate"
        ),
    )
    parser.add_argument(
        "--max-frac",
        type=max_frac,
        default=None,
        help=(
            "fail when the differing-pixel fraction exceeds this (0-1); when "
            "set, replaces the default no-differing-pixel gate"
        ),
    )
    parser.add_argument(
        "--max-rmse",
        type=max_rmse,
        default=None,
        help=(
            "fail when root mean square error exceeds this (0-255); when set, "
            "replaces the default no-differing-pixel gate"
        ),
    )
    parser.add_argument(
        "--max-delta", type=max_delta, default=None, metavar="N",
        help=("fail when the worst raw RGBA channel delta exceeds this (0-255); "
              "independent of tolerance"),
    )
    args = parser.parse_args(argv)

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
                        max_rmse=args.max_rmse, max_delta=args.max_delta)
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
                         max_delta=args.max_delta)
    if args.json:
        print(render_json(result))
        return 0 if ok else 1
    for line in render_text(result, candidate, reference):
        print(line)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
