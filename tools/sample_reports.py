"""Output formatting and report handlers for the reference pixel sampler."""

from __future__ import annotations

if __package__:
    from tools.sample_report_histogram import report_histogram
    from tools.sample_report_search import report_search
    from tools.sample_report_runs import report_runs
    from tools.sample_report_pixels import report_pixels
else:  # run directly: python3 tools/sample.py
    from sample_report_histogram import report_histogram
    from sample_report_search import report_search
    from sample_report_runs import report_runs
    from sample_report_pixels import report_pixels


def report(args, image, width: int, height: int, header: str) -> None:
    if args.runs:
        report_runs(args, image, width, height, header)
        return

    if args.histogram:
        report_histogram(args, image, width, height, header)
        return

    if args.find_color is not None:
        report_search(args, image, width, height, header)
        return

    report_pixels(args, image, width, height, header)
