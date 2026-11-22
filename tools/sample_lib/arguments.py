"""Argument construction and validators for the reference pixel sampler."""

from __future__ import annotations

import argparse
if __package__.startswith("tools"):
    from tools.sample_lib.validators import (
        color_fraction, max_color_fraction, color_tolerance, match_alpha,
        color_offset, match_pixel_offset, match_pixels, nonnegative_offset,
        rgb_argument)
else:
    from sample_lib.validators import (
        color_fraction, max_color_fraction, color_tolerance, match_alpha,
        color_offset, match_pixel_offset, match_pixels, nonnegative_offset,
        rgb_argument)

__all__ = (
    "build_parser", "option_error", "region_error", "color_fraction",
    "max_color_fraction", "color_tolerance", "match_alpha", "color_offset",
    "match_pixel_offset", "match_pixels", "nonnegative_offset", "rgb_argument",
)


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
    if args.min_color_count is not None and args.max_color_count is not None \
            and args.min_color_count > args.max_color_count:
        return (f"--min-color-count must not exceed --max-color-count "
                f"({args.min_color_count} > {args.max_color_count})")
    if args.min_color_fraction is not None and args.max_color_fraction is not None \
            and args.min_color_fraction > args.max_color_fraction:
        return (f"--min-color-fraction must not exceed --max-color-fraction "
                f"({args.min_color_fraction} > {args.max_color_fraction})")
    if getattr(args, "exclude_colors", None) and not args.histogram:
        return "--exclude-color requires --histogram"
    if getattr(args, "include_colors", None) and not args.histogram:
        return "--include-color requires --histogram"
    if args.min_run_length is not None and not args.runs:
        return "--min-run-length requires --runs"
    if args.max_run_length is not None and not args.runs:
        return "--max-run-length requires --runs"
    if args.min_run_length is not None and args.max_run_length is not None \
            and args.min_run_length > args.max_run_length:
        return (f"--min-run-length must not exceed --max-run-length "
                f"({args.min_run_length} > {args.max_run_length})")
    if getattr(args, "max_runs", None) is not None and not args.runs:
        return "--max-runs requires --runs"
    if getattr(args, "run_offset", None) is not None and args.max_runs is None:
        return "--run-offset requires --max-runs"
    if getattr(args, "run_colors", None) and not args.runs:
        return "--run-color requires --runs"
    if getattr(args, "excluded_run_colors", None) and not args.runs:
        return "--exclude-run-color requires --runs"
    if getattr(args, "longest_run", False) and not args.runs:
        return "--longest-run requires --runs"
    if getattr(args, "run_count", False) and not args.runs:
        return "--run-count requires --runs"
    if getattr(args, "scanline_run_counts", False) and not args.runs:
        return "--scanline-run-counts requires --runs"
    if args.color_bounds and not args.histogram:
        return "--color-bounds requires --histogram"
    if args.color_fractions and not args.histogram:
        return "--color-fractions requires --histogram"
    if args.color_cumulative_fractions and not args.histogram:
        return "--color-cumulative-fractions requires --histogram"
    if args.color_positions and not args.histogram:
        return "--color-positions requires --histogram"
    if args.color_centroids and not args.histogram:
        return "--color-centroids requires --histogram"
    if getattr(args, "row_color_counts", False) and not args.histogram:
        return "--row-color-counts requires --histogram"
    if getattr(args, "column_color_counts", False) and not args.histogram:
        return "--column-color-counts requires --histogram"
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
    if getattr(args, "match_run_count", False) and args.find_color is None:
        return "--match-run-count requires --find-color"
    if args.min_match_run_length is not None and not args.match_runs:
        return "--min-match-run-length requires --match-runs"
    if args.max_match_run_length is not None and not args.match_runs:
        return "--max-match-run-length requires --match-runs"
    if args.min_match_run_length is not None and args.max_match_run_length is not None \
            and args.min_match_run_length > args.max_match_run_length:
        return (f"--min-match-run-length must not exceed --max-match-run-length "
                f"({args.min_match_run_length} > {args.max_match_run_length})")
    if getattr(args, "max_match_runs", None) is not None and not args.match_runs:
        return "--max-match-runs requires --match-runs"
    if getattr(args, "match_run_offset", None) is not None and args.max_match_runs is None:
        return "--match-run-offset requires --max-match-runs"
    if args.longest_match_run and args.find_color is None:
        return "--longest-match-run requires --find-color"
    if args.longest_match_column_run and args.find_color is None:
        return "--longest-match-column-run requires --find-color"
    if args.match_column_runs and args.find_color is None:
        return "--match-column-runs requires --find-color"
    if getattr(args, "match_column_run_count", False) and args.find_color is None:
        return "--match-column-run-count requires --find-color"
    if args.min_match_column_run_length is not None and not args.match_column_runs:
        return "--min-match-column-run-length requires --match-column-runs"
    if args.max_match_column_run_length is not None and not args.match_column_runs:
        return "--max-match-column-run-length requires --match-column-runs"
    if args.min_match_column_run_length is not None \
            and args.max_match_column_run_length is not None \
            and args.min_match_column_run_length > args.max_match_column_run_length:
        return (f"--min-match-column-run-length must not exceed "
                f"--max-match-column-run-length "
                f"({args.min_match_column_run_length} > {args.max_match_column_run_length})")
    if getattr(args, "max_match_column_runs", None) is not None and not args.match_column_runs:
        return "--max-match-column-runs requires --match-column-runs"
    if getattr(args, "match_column_run_offset", None) is not None \
            and args.max_match_column_runs is None:
        return "--match-column-run-offset requires --max-match-column-runs"
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
    """Build the sample tool's command-line argument parser."""
    if __package__.startswith("tools"):
        from tools.sample_lib.parser import build_parser as parser_builder
    else:
        from sample_lib.parser import build_parser as parser_builder
    return parser_builder()
