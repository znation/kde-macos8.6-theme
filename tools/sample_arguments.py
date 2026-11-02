"""Argument construction and validators for the reference pixel sampler."""

from __future__ import annotations

import argparse
import re

if __package__:
    from tools.argument_parsing import EscapingArgumentParser, plain_number, positive_int
else:
    from argument_parsing import EscapingArgumentParser, plain_number, positive_int


def rgb_argument(value: str) -> tuple[int, int, int]:
    """Parse a six-digit RGB color, optionally prefixed by ``#``."""
    digits = value[1:] if value.startswith("#") else value
    if not re.fullmatch(r"[0-9A-Fa-f]{6}", digits, flags=re.ASCII):
        raise argparse.ArgumentTypeError(
            f"expected six hexadecimal digits, optionally prefixed by #: {value!r}"
        )
    return tuple(int(digits[i:i + 2], 16) for i in (0, 2, 4))


def color_tolerance(value: str) -> int:
    """Parse a plain ASCII RGB channel tolerance from 0 through 255."""
    parsed = plain_number(value, "--color-tolerance", "integer", "an", int)
    if not 0 <= parsed <= 255:
        raise argparse.ArgumentTypeError("--color-tolerance must be between 0 and 255")
    return parsed


def match_alpha(value: str) -> int:
    """Parse an exact PNG alpha byte from 0 through 255."""
    parsed = plain_number(value, "--match-alpha", "integer", "an", int)
    if not 0 <= parsed <= 255:
        raise argparse.ArgumentTypeError("--match-alpha must be between 0 and 255")
    return parsed


def match_pixels(value: str) -> int:
    """Parse a bounded count of matching positions to report."""
    parsed = plain_number(value, "--match-pixels", "integer", "an", int)
    if not 1 <= parsed <= 1000:
        raise argparse.ArgumentTypeError("--match-pixels must be between 1 and 1000")
    return parsed


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
    parser.add_argument("--top-colors", type=positive_int("--top-colors"), metavar="N", help="with --histogram, show only the N most frequent colors")
    parser.add_argument("--color-bounds", action="store_true", help="with --histogram, report bounds for each emitted color")
    parser.add_argument("--color-tolerance", type=color_tolerance, metavar="N", help="with --find-color, allow up to N difference in each RGB channel")
    parser.add_argument("--match-alpha", type=match_alpha, metavar="N", help="with --find-color, require exact PNG alpha N")
    parser.add_argument("--match-pixels", type=match_pixels, metavar="N", help="with --find-color, list up to N matching coordinates")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--histogram", action="store_true", help="count RGB colors, or RGBA colors with --alpha, in the sampled region")
    modes.add_argument("--runs", action="store_true", help="group adjacent RGB colors, or RGBA with --alpha, along one row or column")
    modes.add_argument("--find-color", type=rgb_argument, metavar="RRGGBB", help="locate an RGB color in the sampled region")
    return parser
