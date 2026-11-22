"""Command-line parser declaration groups for the reference pixel sampler."""

from __future__ import annotations

import argparse

if __package__.startswith("tools"):
    from tools.argument_parsing import EscapingArgumentParser, plain_number, positive_int
    from tools.sample_lib.validators import (
        color_fraction, max_color_fraction, color_tolerance, match_alpha,
        color_offset, match_pixel_offset, match_pixels, nonnegative_offset,
        rgb_argument)
else:
    from argument_parsing import EscapingArgumentParser, plain_number, positive_int
    from sample_lib.validators import (
        color_fraction, max_color_fraction, color_tolerance, match_alpha,
        color_offset, match_pixel_offset, match_pixels, nonnegative_offset,
        rgb_argument)


def _add_region_arguments(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("image", help="reference image (PNG, or JPEG decoded with ImageMagick)")
        parser.add_argument("x",
                            type=lambda value: plain_number(value, "x", "integer", "an", int),
                            help="pixel column")
        parser.add_argument("y",
                            type=lambda value: plain_number(value, "y", "integer", "an", int),
                            help="pixel row")
        parser.add_argument("--width", type=positive_int("--width"), default=1, metavar="W",
                            help="pixels to sample to the right of x (default 1)")
        parser.add_argument("--height", type=positive_int("--height"), default=1, metavar="H",
                            help="pixels to sample below y (default 1)")
        parser.add_argument("--json", action="store_true", help="print structured JSON")
        parser.add_argument("--alpha", action="store_true",
                            help="include alpha in pixel samples, histogram colors and run grouping")


def _add_histogram_arguments(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--top-colors", type=positive_int("--top-colors"), metavar="N",
                            help="with --histogram, show only the N most frequent colors")
        parser.add_argument("--color-offset", type=color_offset, metavar="K",
                            help="with --top-colors, skip the first K ranked colors")
        parser.add_argument("--min-color-count", type=positive_int("--min-color-count"), metavar="N",
                            help="with --histogram, omit colors occurring fewer than N times")
        parser.add_argument("--max-color-count", type=positive_int("--max-color-count"), metavar="N",
                            help="with --histogram, omit colors occurring more than N times")
        parser.add_argument("--min-color-fraction", type=color_fraction, metavar="F",
                            help="with --histogram, omit colors below fraction F of the region")
        parser.add_argument("--max-color-fraction", type=max_color_fraction, metavar="F",
                            help="with --histogram, omit colors above fraction F of the region")
        parser.add_argument("--exclude-color", dest="exclude_colors", type=rgb_argument,
                            action="append", default=None, metavar="RRGGBB",
                            help="with --histogram, omit this RGB color (repeatable)")
        parser.add_argument("--include-color", dest="include_colors", type=rgb_argument,
                            action="append", default=None, metavar="RRGGBB",
                            help="with --histogram, include this RGB color (repeatable)")
        parser.add_argument("--color-bounds", action="store_true",
                            help="with --histogram, report bounds for each emitted color")
        parser.add_argument("--color-fractions", action="store_true",
                            help="with --histogram, report each color's fraction of the region")
        parser.add_argument("--color-cumulative-fractions", action="store_true",
                            help="with --histogram, report each color's cumulative share of the "
                                 "region across the displayed page")
        parser.add_argument("--color-positions", action="store_true",
                            help="with --histogram, report each color's first row-major position")
        parser.add_argument("--color-centroids", action="store_true",
                            help="with --histogram, report each color's mean pixel coordinate")
        parser.add_argument("--row-color-counts", action="store_true",
                            help="with --histogram, report each region row's distinct-color count")
        parser.add_argument("--column-color-counts", action="store_true",
                            help="with --histogram, report each region column's distinct-color count")


def _add_run_arguments(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--run-axis", choices=("horizontal", "vertical"),
                            help="scan each row or column of a --runs rectangle")
        parser.add_argument("--min-run-length", type=positive_int("--min-run-length"), metavar="N",
                            help="with --runs, omit color runs shorter than N pixels")
        parser.add_argument("--max-run-length", type=positive_int("--max-run-length"), metavar="N",
                            help="with --runs, omit color runs longer than N pixels")
        parser.add_argument("--max-runs", type=positive_int("--max-runs"), metavar="N",
                            help="with --runs, display at most N eligible color runs")
        parser.add_argument("--run-offset", type=nonnegative_offset("--run-offset"), metavar="K",
                            help="with --runs and --max-runs, skip K eligible runs before "
                                 "displaying the page")
        parser.add_argument("--run-color", dest="run_colors", type=rgb_argument,
                            action="append", default=None, metavar="RRGGBB",
                            help="with --runs, retain this RGB color (repeatable)")
        parser.add_argument("--exclude-run-color", dest="excluded_run_colors",
                            type=rgb_argument, action="append", default=None, metavar="RRGGBB",
                            help="with --runs, omit this RGB color (repeatable)")
        parser.add_argument("--run-count", action="store_true",
                            help="with --runs, report the total number of scanline color "
                                 "runs before filters")
        parser.add_argument("--scanline-run-counts", action="store_true",
                            help="with --runs, report each scanline's color-run count "
                                 "before filters")
        parser.add_argument("--longest-run", action="store_true",
                            help="with --runs, report the longest scanline color run "
                                 "before filters")


def _add_find_color_arguments(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--color-tolerance", type=color_tolerance, metavar="N",
                            help="with --find-color, allow up to N difference in each RGB channel")
        parser.add_argument("--match-alpha", type=match_alpha, metavar="N",
                            help="with --find-color, require exact PNG alpha N")
        parser.add_argument("--match-pixels", type=match_pixels, metavar="N",
                            help="with --find-color, list up to N matching coordinates")
        parser.add_argument("--match-pixel-offset", type=match_pixel_offset, metavar="N",
                            help="with --match-pixels, skip the first N matches")
        parser.add_argument("--match-fraction", action="store_true",
                            help="with --find-color, report the matching fraction of the region")
        parser.add_argument("--match-centroid", action="store_true",
                            help="with --find-color, report the centroid of matching pixel "
                                 "coordinates")
        parser.add_argument("--match-runs", action="store_true",
                            help="with --find-color, report contiguous horizontal matching segments")
        parser.add_argument("--match-run-count", action="store_true",
                            help="with --find-color, report the number of horizontal matching "
                                 "segments")
        parser.add_argument("--min-match-run-length",
                            type=positive_int("--min-match-run-length"), metavar="N",
                            help="with --match-runs, omit matching segments shorter than N pixels")
        parser.add_argument("--max-match-run-length",
                            type=positive_int("--max-match-run-length"), metavar="N",
                            help="with --match-runs, omit matching segments longer than N pixels")
        parser.add_argument("--max-match-runs", type=positive_int("--max-match-runs"), metavar="N",
                            help="with --match-runs, report at most N matching segments")
        parser.add_argument("--match-run-offset",
                            type=nonnegative_offset("--match-run-offset"), metavar="K",
                            help="with --match-runs and --max-match-runs, skip K eligible segments "
                                 "after length filters")
        parser.add_argument("--longest-match-run", action="store_true",
                            help="with --find-color, report the longest horizontal matching segment")
        parser.add_argument("--longest-match-column-run", action="store_true",
                            help="with --find-color, report the longest vertical matching segment")
        parser.add_argument("--match-column-runs", action="store_true",
                            help="with --find-color, report contiguous vertical matching segments")
        parser.add_argument("--match-column-run-count", action="store_true",
                            help="with --find-color, report the number of vertical matching "
                                 "segments")
        parser.add_argument("--min-match-column-run-length",
                            type=positive_int("--min-match-column-run-length"), metavar="N",
                            help="with --match-column-runs, omit matching segments shorter than "
                                 "N pixels")
        parser.add_argument("--max-match-column-run-length",
                            type=positive_int("--max-match-column-run-length"), metavar="N",
                            help="with --match-column-runs, omit matching segments longer than "
                                 "N pixels")
        parser.add_argument("--max-match-column-runs",
                            type=positive_int("--max-match-column-runs"), metavar="N",
                            help="with --match-column-runs, report at most N eligible matching "
                                 "vertical segments")
        parser.add_argument("--match-column-run-offset",
                            type=nonnegative_offset("--match-column-run-offset"), metavar="K",
                            help="with --match-column-runs and --max-match-column-runs, skip K "
                                 "eligible segments after length filters")
        parser.add_argument("--match-rows", action="store_true",
                            help="with --find-color, count matches in each row")
        parser.add_argument("--match-columns", action="store_true",
                            help="with --find-color, count matches in each column")
        parser.add_argument("--match-row-bounds", action="store_true",
                            help="with --find-color, report enclosing match bounds in each row")
        parser.add_argument("--match-column-bounds", action="store_true",
                            help="with --find-color, report enclosing match bounds in each column")


def build_parser() -> argparse.ArgumentParser:
    """Build the sample tool's command-line argument parser."""
    parser = EscapingArgumentParser(
        prog="sample",
        description="Print a reference screenshot pixel's RGB and hex value.",
        epilog="exit status: 0 on success, 2 usage or read error",
    )

    _add_region_arguments(parser)
    _add_run_arguments(parser)
    _add_histogram_arguments(parser)
    _add_find_color_arguments(parser)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--histogram", action="store_true",
                       help="count RGB colors, or RGBA colors with --alpha, in the sampled region")
    modes.add_argument("--runs", action="store_true",
                       help="group adjacent RGB colors, or RGBA with --alpha, along one row "
                            "or column")
    modes.add_argument("--find-color", type=rgb_argument, metavar="RRGGBB",
                       help="locate an RGB color in the sampled region")

    return parser
