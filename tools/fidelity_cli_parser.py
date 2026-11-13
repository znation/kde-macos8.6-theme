"""The fidelity comparison command line's argument surface.

``build_parser`` constructs the parser; ``validate_options`` cross-checks
the parsed option values and refuses contradictory or dependent
combinations before any image read.
"""

from __future__ import annotations

if __package__:
    from tools.argument_parsing import EscapingArgumentParser, positive_int
    from tools.fidelity_arguments import (
        max_delta,
        max_differing,
        max_frac,
        max_mae,
        max_rmse,
        parse_crop,
        tolerance,
        worst_pixel_offset,
        worst_pixel_limit,
        difference_run_offset,
        difference_column_run_offset,
    )
else:  # run directly: python3 tools/fidelity.py
    from argument_parsing import EscapingArgumentParser, positive_int
    from fidelity_arguments import (
        max_delta,
        max_differing,
        max_frac,
        max_mae,
        max_rmse,
        parse_crop,
        tolerance,
        worst_pixel_offset,
        worst_pixel_limit,
        difference_run_offset,
        difference_column_run_offset,
    )


def validate_options(parser: EscapingArgumentParser, args) -> None:
    """Refuse contradictory or dependent option combinations via *parser*.

    Every check reads only the parsed values, so a refusal happens before
    any image read: a contradictory filter window or an offset without its
    count cap would otherwise exit 0 with an empty or unbounded report
    beside full metrics, indistinguishable from a genuine measurement.
    """
    if args.min_difference_run_length is not None and not args.difference_runs:
        parser.error("--min-difference-run-length requires --difference-runs")
    if args.max_difference_run_length is not None and not args.difference_runs:
        parser.error("--max-difference-run-length requires --difference-runs")
    _validate_run_length_window(
        parser, args.min_difference_run_length, args.max_difference_run_length,
        "--min-difference-run-length", "--max-difference-run-length")
    if args.max_difference_runs is not None and not args.difference_runs:
        parser.error("--max-difference-runs requires --difference-runs")
    if args.difference_run_offset is not None and args.max_difference_runs is None:
        parser.error("--difference-run-offset requires --max-difference-runs")
    if args.min_difference_column_run_length is not None and not args.difference_column_runs:
        parser.error("--min-difference-column-run-length requires --difference-column-runs")
    if args.max_difference_column_run_length is not None and not args.difference_column_runs:
        parser.error("--max-difference-column-run-length requires --difference-column-runs")
    _validate_run_length_window(
        parser, args.min_difference_column_run_length,
        args.max_difference_column_run_length,
        "--min-difference-column-run-length",
        "--max-difference-column-run-length")
    if args.max_difference_column_runs is not None and not args.difference_column_runs:
        parser.error("--max-difference-column-runs requires --difference-column-runs")
    if args.difference_column_run_offset is not None and args.max_difference_column_runs is None:
        parser.error("--difference-column-run-offset requires --max-difference-column-runs")
    if args.worst_pixel_offset is not None and args.worst_pixels is None:
        parser.error("--worst-pixel-offset requires --worst-pixels")


def _validate_run_length_window(parser, minimum, maximum,
                                minimum_flag: str, maximum_flag: str) -> None:
    """Reject a contradictory run-length window with its CLI flag names."""
    if minimum is not None and maximum is not None and minimum > maximum:
        parser.error(
            f"{minimum_flag} must not exceed {maximum_flag} "
            f"({minimum} > {maximum})")


def build_parser() -> EscapingArgumentParser:
    """Return a fresh parser for the fidelity comparison CLI."""
    parser = EscapingArgumentParser(
        prog="fidelity",
        description="Measure a rendered PNG surface against a reference PNG.",
        epilog=(
            "exit status: 0 when the comparison passes, 1 when it fails, "
            "2 usage or read error; passes when every --max-mae/--max-frac/--max-rmse/--max-delta/--max-differing "
            "threshold set is met, and otherwise when no pixel differs "
            "beyond --tolerance"
        ),
    )
    parser.add_argument("candidate", help="rendered surface image (PNG)")
    parser.add_argument("reference", help="reference image (PNG)")
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--json", action="store_true", help="emit comparison as JSON")
    output.add_argument("--quiet", action="store_true",
                        help="print no report; use the exit status as the verdict")
    parser.add_argument("--worst-pixels", type=worst_pixel_limit, metavar="N",
                        help="list up to N worst differing pixels (1-1000)")
    parser.add_argument("--worst-pixel-offset", type=worst_pixel_offset, metavar="K",
                        default=None, help="skip the first K ranked pixels (requires --worst-pixels)")
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
    parser.add_argument("--difference-run-count", action="store_true",
                        help="count horizontal mismatch runs without listing them")
    parser.add_argument("--difference-column-run-count", action="store_true",
                        help="count vertical mismatch runs without listing them")
    parser.add_argument("--min-difference-run-length", type=positive_int("--min-difference-run-length"),
                        default=None, metavar="N",
                        help="omit horizontal difference runs shorter than N (requires --difference-runs)")
    parser.add_argument("--max-difference-run-length", type=positive_int("--max-difference-run-length"),
                        default=None, metavar="N",
                        help="omit horizontal difference runs longer than N (requires --difference-runs)")
    parser.add_argument("--max-difference-runs", type=positive_int("--max-difference-runs"),
                        default=None, metavar="N",
                        help="report at most N horizontal difference runs (requires --difference-runs)")
    parser.add_argument("--difference-run-offset", type=difference_run_offset,
                        default=None, metavar="K",
                        help="skip the first K eligible horizontal difference runs (requires --max-difference-runs)")
    parser.add_argument("--difference-column-runs", action="store_true",
                        help="locate disjoint vertical runs of pixels differing beyond --tolerance")
    parser.add_argument("--min-difference-column-run-length", type=positive_int("--min-difference-column-run-length"),
                        default=None, metavar="N",
                        help="omit vertical difference runs shorter than N (requires --difference-column-runs)")
    parser.add_argument("--max-difference-column-run-length", type=positive_int("--max-difference-column-run-length"),
                        default=None, metavar="N",
                        help="omit vertical difference runs longer than N (requires --difference-column-runs)")
    parser.add_argument("--max-difference-column-runs", type=positive_int("--max-difference-column-runs"),
                        default=None, metavar="N",
                        help="report at most N vertical difference runs (requires --difference-column-runs)")
    parser.add_argument("--difference-column-run-offset", type=difference_column_run_offset,
                        default=None, metavar="K",
                        help="skip the first K eligible vertical difference runs (requires --max-difference-column-runs)")
    parser.add_argument("--difference-centroid", action="store_true",
                        help="report the centroid of pixels differing beyond --tolerance")
    parser.add_argument("--longest-difference-run", action="store_true",
                        help="report the longest horizontal run differing beyond --tolerance")
    parser.add_argument("--longest-difference-column-run", action="store_true",
                        help="report the longest vertical run differing beyond --tolerance")
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
    parser.add_argument(
        "--max-differing", type=max_differing, default=None, metavar="N",
        help=("fail when more than N pixels differ beyond --tolerance; "
              "when set, replaces the default no-differing-pixel gate"),
    )
    return parser
