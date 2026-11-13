"""Scalar argument validators for the reference pixel sampler."""

from __future__ import annotations

import argparse
import math
import re

if __package__:
    from tools.argument_parsing import plain_number
else:
    from argument_parsing import plain_number


def _number_in_range(value: str, option: str, noun: str, low: int | float,
                     high: int | float, parse):
    """Parse a finite plain number and enforce an inclusive option range."""
    article = "an" if noun == "integer" else "a"
    parsed = plain_number(value, option, noun, article, parse)
    if not math.isfinite(parsed) or not low <= parsed <= high:
        raise argparse.ArgumentTypeError(
            f"{option} must be between {low} and {high}: {value!r}"
        )
    return parsed


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
    return _number_in_range(value, "--color-tolerance", "integer", 0, 255, int)


def match_alpha(value: str) -> int:
    """Parse an exact PNG alpha byte from 0 through 255."""
    return _number_in_range(value, "--match-alpha", "integer", 0, 255, int)


def match_pixels(value: str) -> int:
    """Parse a bounded count of matching positions to report."""
    return _number_in_range(value, "--match-pixels", "integer", 1, 1000, int)


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
    return _number_in_range(value, "--min-color-fraction", "number", 0, 1, float)


def nonnegative_offset(option: str):
    """Return a parser accepting *option* only as a nonnegative integer.

    The ``--run-offset``, ``--match-run-offset`` and ``--match-column-run-offset``
    paging indexes each count eligible steps from the start of the ranked list,
    so Python's parsing and slicing would silently map a negative value onto a
    different page instead of reporting the rejection. The returned parser
    checks the value the way ``color_offset`` does for the histogram offset.
    """

    def parse(value: str) -> int:
        parsed = plain_number(value, option, "integer", "a nonnegative", int)
        if parsed < 0:
            raise argparse.ArgumentTypeError(
                f"{option} must be nonnegative: {value!r}"
            )
        return parsed

    return parse


def max_color_fraction(value: str) -> float:
    """Parse a finite maximum histogram fraction from zero through one."""
    return _number_in_range(value, "--max-color-fraction", "number", 0, 1, float)
