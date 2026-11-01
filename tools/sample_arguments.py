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
    parser.add_argument("--top-colors", type=positive_int("--top-colors"), metavar="N", help="with --histogram, show only the N most frequent colors")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--histogram", action="store_true", help="count RGB colors in the sampled region")
    modes.add_argument("--runs", action="store_true", help="group adjacent RGB colors along one row or column")
    modes.add_argument("--find-color", type=rgb_argument, metavar="RRGGBB", help="locate an exact RGB color in the sampled region")
    return parser
