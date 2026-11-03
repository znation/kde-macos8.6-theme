"""Argument construction and validators for the reference pixel sampler."""

from __future__ import annotations

import argparse
if __package__:
    from tools.argument_parsing import EscapingArgumentParser, plain_number, positive_int
    from tools.sample_validators import (color_fraction, max_color_fraction, color_tolerance, match_alpha,
                                        color_offset, match_pixel_offset, match_pixels, rgb_argument)
else:
    from argument_parsing import EscapingArgumentParser, plain_number, positive_int
    from sample_validators import (color_fraction, max_color_fraction, color_tolerance, match_alpha,
                                   color_offset, match_pixel_offset, match_pixels, rgb_argument)


def option_error(args: argparse.Namespace) -> str | None:
    """Return the first incompatible option combination, if any."""
    if args.top_colors is not None and not args.histogram:
        return "--top-colors requires --histogram"
    if getattr(args, "color_offset", None) is not None and args.top_colors is None:
        return "--color-offset requires --top-colors"
    if args.min_color_count is not None and not args.histogram:
        return "--min-color-count requires --histogram"
    if args.max_color_count is not None and not args.histogram:
        return "--max-color-count requires --histogram"
    if args.min_color_fraction is not None and not args.histogram:
        return "--min-color-fraction requires --histogram"
    if args.max_color_fraction is not None and not args.histogram:
        return "--max-color-fraction requires --histogram"
    if getattr(args, "exclude_colors", None) and not args.histogram:
        return "--exclude-color requires --histogram"
    if getattr(args, "include_colors", None) and not args.histogram:
        return "--include-color requires --histogram"
    if args.min_run_length is not None and not args.runs:
        return "--min-run-length requires --runs"
    if args.max_run_length is not None and not args.runs:
        return "--max-run-length requires --runs"
    if getattr(args, "run_colors", None) and not args.runs:
        return "--run-color requires --runs"
    if getattr(args, "excluded_run_colors", None) and not args.runs:
        return "--exclude-run-color requires --runs"
    if args.color_bounds and not args.histogram:
        return "--color-bounds requires --histogram"
    if args.color_fractions and not args.histogram:
        return "--color-fractions requires --histogram"
    if args.color_positions and not args.histogram:
        return "--color-positions requires --histogram"
    if args.color_centroids and not args.histogram:
        return "--color-centroids requires --histogram"
    if args.color_tolerance is not None and args.find_color is None:
        return "--color-tolerance requires --find-color"
    if args.match_alpha is not None and args.find_color is None:
        return "--match-alpha requires --find-color"
    if args.match_pixels is not None and args.find_color is None:
        return "--match-pixels requires --find-color"
    if args.match_pixel_offset is not None and args.match_pixels is None:
        return "--match-pixel-offset requires --match-pixels"
    if args.match_fraction and args.find_color is None:
        return "--match-fraction requires --find-color"
    if args.match_centroid and args.find_color is None:
        return "--match-centroid requires --find-color"
    if args.match_runs and args.find_color is None:
        return "--match-runs requires --find-color"
    if args.min_match_run_length is not None and not args.match_runs:
        return "--min-match-run-length requires --match-runs"
    if args.max_match_run_length is not None and not args.match_runs:
        return "--max-match-run-length requires --match-runs"
    if args.longest_match_run and args.find_color is None:
        return "--longest-match-run requires --find-color"
    if args.longest_match_column_run and args.find_color is None:
        return "--longest-match-column-run requires --find-color"
    if args.match_column_runs and args.find_color is None:
        return "--match-column-runs requires --find-color"
    if args.min_match_column_run_length is not None and not args.match_column_runs:
        return "--min-match-column-run-length requires --match-column-runs"
    if args.max_match_column_run_length is not None and not args.match_column_runs:
        return "--max-match-column-run-length requires --match-column-runs"
    if args.match_rows and args.find_color is None:
        return "--match-rows requires --find-color"
    if args.match_columns and args.find_color is None:
        return "--match-columns requires --find-color"
    if args.match_row_bounds and args.find_color is None:
        return "--match-row-bounds requires --find-color"
    if args.match_column_bounds and args.find_color is None:
        return "--match-column-bounds requires --find-color"
    if args.runs and args.width > 1 and args.height > 1 and args.run_axis is None:
        return "--runs requires a single row or column unless --run-axis is given"
    if args.run_axis is not None and not args.runs:
        return "--run-axis requires --runs"
    if args.alpha and args.find_color is not None:
        return "--alpha cannot be combined with --find-color"
    return None


def region_error(args: argparse.Namespace, image_width: int, image_height: int) -> str | None:
    """Return the bounds diagnostic for a parsed pixel or region, if invalid."""
    if args.width == 1 and args.height == 1:
        if not (0 <= args.x < image_width and 0 <= args.y < image_height):
            return f"pixel ({args.x}, {args.y}) is outside the {image_width}x{image_height} image"
    elif (args.x < 0 or args.y < 0 or args.x + args.width > image_width
          or args.y + args.height > image_height):
        return (
            f"region ({args.x}, {args.y}) {args.width}x{args.height} "
            f"is outside the {image_width}x{image_height} image"
        )
    return None


def build_parser() -> argparse.ArgumentParser:
    parser = EscapingArgumentParser(
        prog="sample",
        description="Print a reference screenshot pixel's RGB and hex value.",
        epilog="exit status: 0 on success, 2 usage or read error",
    )
    parser.add_argument("image", help="reference image (PNG)")
    parser.add_argument("x", type=lambda value: plain_number(value, "x", "integer", "an", int), help="pixel column")
    parser.add_argument("y", type=lambda value: plain_number(value, "y", "integer", "an", int), help="pixel row")
    parser.add_argument("--width", type=positive_int("--width"), default=1, metavar="W", help="pixels to sample to the right of x (default 1)")
    parser.add_argument("--height", type=positive_int("--height"), default=1, metavar="H", help="pixels to sample below y (default 1)")
    parser.add_argument("--json", action="store_true", help="print structured JSON")
    parser.add_argument("--alpha", action="store_true", help="include alpha in pixel samples, histogram colors and run grouping")
    parser.add_argument("--run-axis", choices=("horizontal", "vertical"), help="scan each row or column of a --runs rectangle")
    parser.add_argument("--min-run-length", type=positive_int("--min-run-length"), metavar="N", help="with --runs, omit color runs shorter than N pixels")
    parser.add_argument("--max-run-length", type=positive_int("--max-run-length"), metavar="N", help="with --runs, omit color runs longer than N pixels")
    parser.add_argument("--run-color", dest="run_colors", type=rgb_argument, action="append", default=None, metavar="RRGGBB", help="with --runs, retain this RGB color (repeatable)")
    parser.add_argument("--exclude-run-color", dest="excluded_run_colors", type=rgb_argument, action="append", default=None, metavar="RRGGBB", help="with --runs, omit this RGB color (repeatable)")
    parser.add_argument("--top-colors", type=positive_int("--top-colors"), metavar="N", help="with --histogram, show only the N most frequent colors")
    parser.add_argument("--color-offset", type=color_offset, metavar="K", help="with --top-colors, skip the first K ranked colors")
    parser.add_argument("--min-color-count", type=positive_int("--min-color-count"), metavar="N", help="with --histogram, omit colors occurring fewer than N times")
    parser.add_argument("--max-color-count", type=positive_int("--max-color-count"), metavar="N", help="with --histogram, omit colors occurring more than N times")
    parser.add_argument("--min-color-fraction", type=color_fraction, metavar="F", help="with --histogram, omit colors below fraction F of the region")
    parser.add_argument("--max-color-fraction", type=max_color_fraction, metavar="F", help="with --histogram, omit colors above fraction F of the region")
    parser.add_argument("--exclude-color", dest="exclude_colors", type=rgb_argument, action="append", default=None, metavar="RRGGBB", help="with --histogram, omit this RGB color (repeatable)")
    parser.add_argument("--include-color", dest="include_colors", type=rgb_argument, action="append", default=None, metavar="RRGGBB", help="with --histogram, include this RGB color (repeatable)")
    parser.add_argument("--color-bounds", action="store_true", help="with --histogram, report bounds for each emitted color")
    parser.add_argument("--color-fractions", action="store_true", help="with --histogram, report each color's fraction of the region")
    parser.add_argument("--color-positions", action="store_true", help="with --histogram, report each color's first row-major position")
    parser.add_argument("--color-centroids", action="store_true", help="with --histogram, report each color's mean pixel coordinate")
    parser.add_argument("--color-tolerance", type=color_tolerance, metavar="N", help="with --find-color, allow up to N difference in each RGB channel")
    parser.add_argument("--match-alpha", type=match_alpha, metavar="N", help="with --find-color, require exact PNG alpha N")
    parser.add_argument("--match-pixels", type=match_pixels, metavar="N", help="with --find-color, list up to N matching coordinates")
    parser.add_argument("--match-pixel-offset", type=match_pixel_offset, metavar="N", help="with --match-pixels, skip the first N matches")
    parser.add_argument("--match-fraction", action="store_true", help="with --find-color, report the matching fraction of the region")
    parser.add_argument("--match-centroid", action="store_true", help="with --find-color, report the centroid of matching pixel coordinates")
    parser.add_argument("--match-runs", action="store_true", help="with --find-color, report contiguous horizontal matching segments")
    parser.add_argument("--min-match-run-length", type=positive_int("--min-match-run-length"), metavar="N", help="with --match-runs, omit matching segments shorter than N pixels")
    parser.add_argument("--max-match-run-length", type=positive_int("--max-match-run-length"), metavar="N", help="with --match-runs, omit matching segments longer than N pixels")
    parser.add_argument("--longest-match-run", action="store_true", help="with --find-color, report the longest horizontal matching segment")
    parser.add_argument("--longest-match-column-run", action="store_true", help="with --find-color, report the longest vertical matching segment")
    parser.add_argument("--match-column-runs", action="store_true", help="with --find-color, report contiguous vertical matching segments")
    parser.add_argument("--min-match-column-run-length", type=positive_int("--min-match-column-run-length"), metavar="N", help="with --match-column-runs, omit matching segments shorter than N pixels")
    parser.add_argument("--max-match-column-run-length", type=positive_int("--max-match-column-run-length"), metavar="N", help="with --match-column-runs, omit matching segments longer than N pixels")
    parser.add_argument("--match-rows", action="store_true", help="with --find-color, count matches in each row")
    parser.add_argument("--match-columns", action="store_true", help="with --find-color, count matches in each column")
    parser.add_argument("--match-row-bounds", action="store_true", help="with --find-color, report enclosing match bounds in each row")
    parser.add_argument("--match-column-bounds", action="store_true", help="with --find-color, report enclosing match bounds in each column")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--histogram", action="store_true", help="count RGB colors, or RGBA colors with --alpha, in the sampled region")
    modes.add_argument("--runs", action="store_true", help="group adjacent RGB colors, or RGBA with --alpha, along one row or column")
    modes.add_argument("--find-color", type=rgb_argument, metavar="RRGGBB", help="locate an RGB color in the sampled region")
    return parser
