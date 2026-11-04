"""Scalar argument validators for the reference pixel sampler."""

from __future__ import annotations

import argparse
import math
import re

if __package__:
    from tools.argument_parsing import plain_number
else:
    from argument_parsing import plain_number


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
        raise argparse.ArgumentTypeError(
            f"--color-tolerance must be between 0 and 255: {value!r}"
        )
    return parsed


def match_alpha(value: str) -> int:
    """Parse an exact PNG alpha byte from 0 through 255."""
    parsed = plain_number(value, "--match-alpha", "integer", "an", int)
    if not 0 <= parsed <= 255:
        raise argparse.ArgumentTypeError(
            f"--match-alpha must be between 0 and 255: {value!r}"
        )
    return parsed


def match_pixels(value: str) -> int:
    """Parse a bounded count of matching positions to report."""
    parsed = plain_number(value, "--match-pixels", "integer", "an", int)
    if not 1 <= parsed <= 1000:
        raise argparse.ArgumentTypeError(
            f"--match-pixels must be between 1 and 1000: {value!r}"
        )
    return parsed


def match_pixel_offset(value: str) -> int:
    """Parse a nonnegative plain ASCII match-coordinate offset."""
    parsed = plain_number(value, "--match-pixel-offset", "integer", "a", int)
    if parsed < 0:
        raise argparse.ArgumentTypeError(
            f"--match-pixel-offset must be nonnegative: {value!r}"
        )
    return parsed


def color_offset(value: str) -> int:
    """Parse a nonnegative plain ASCII histogram color offset."""
    parsed = plain_number(value, "--color-offset", "integer", "an", int)
    if parsed < 0:
        raise argparse.ArgumentTypeError(
            f"--color-offset must be nonnegative: {value!r}"
        )
    return parsed


def color_fraction(value: str) -> float:
    """Parse a finite histogram fraction from zero through one."""
    parsed = plain_number(value, "--min-color-fraction", "number", "a", float)
    if not math.isfinite(parsed) or not 0 <= parsed <= 1:
        raise argparse.ArgumentTypeError(
            f"--min-color-fraction must be between 0 and 1: {value!r}"
        )
    return parsed


def max_color_fraction(value: str) -> float:
    """Parse a finite maximum histogram fraction from zero through one."""
    parsed = plain_number(value, "--max-color-fraction", "number", "a", float)
    if not math.isfinite(parsed) or not 0 <= parsed <= 1:
        raise argparse.ArgumentTypeError(
            f"--max-color-fraction must be between 0 and 1: {value!r}"
        )
    return parsed
