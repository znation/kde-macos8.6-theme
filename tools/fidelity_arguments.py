"""Crop and comparison-budget argument types for the fidelity CLI.

Validate CLI text using the shared numeric grammar and metric rectangle checks.
Image loading and reporting live in ``tools/fidelity.py``.
"""

from __future__ import annotations

import argparse
import math
from typing import TypeVar

if __package__:
    from tools.argument_parsing import is_plain_ascii_number, plain_number
    from tools.fidelity_metrics import crop_rect_problem
else:  # imported from a directly run tool
    from argument_parsing import is_plain_ascii_number, plain_number
    from fidelity_metrics import crop_rect_problem


def parse_crop(value: str) -> tuple[int, int, int, int]:
    """Return ``(x, y, width, height)`` parsed from an ``X,Y,W,H`` value.

    Whitespace around a field is accepted, but the four fields themselves must
    be plain ASCII integers. The rectangle must keep :func:`crop_rect_problem`'s
    contract -- a non-negative origin and a positive size -- and any rejected
    text raises ``argparse.ArgumentTypeError`` with a diagnostic.
    """
    # Strip each field before the plain-number check: whitespace around a
    # comma-separated field ("0, 0, 10, 10") is the conventional way to write
    # the rectangle, not a stray character that changes the value, so accept
    # it here. The scalar options still reject surrounding whitespace through
    # is_plain_ascii_number, where it signals a quoting mistake.
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError(f"crop must be X,Y,W,H: {value!r}")
    numbers: list[int] = []
    for position, part in enumerate(parts, 1):
        if not part:
            # A blank field ("1,,3,4") is the common typo; without this it
            # falls through to int('') and is reported as "must be integers:
            # ''", which names the empty string but not the missing field.
            raise argparse.ArgumentTypeError(
                f"crop field {position} is empty: {value!r}"
            )
        if not is_plain_ascii_number(part):
            raise argparse.ArgumentTypeError(
                f"crop values must be plain ASCII integers: {part!r}"
            )
        try:
            numbers.append(int(part))
        except ValueError as exc:
            raise argparse.ArgumentTypeError(
                f"crop values must be integers: {part!r}"
            ) from exc
    x, y, width, height = numbers
    problem = crop_rect_problem(x, y, width, height)
    if problem is not None:
        raise argparse.ArgumentTypeError(problem)
    return x, y, width, height


_Number = TypeVar("_Number", int, float)


def _channel_amount(
    value: str, number: _Number, option: str, noun: str
) -> _Number:
    """Return *number* once it is a valid 0-255 per-channel *noun*.

    A per-channel delta or mean can never be negative or exceed 255, so a
    value outside that range would silently disable the metric; both bounds
    are rejected with an option-named diagnostic.
    """
    if number < 0:
        raise argparse.ArgumentTypeError(
            f"{option} must not be negative: {value!r}"
        )
    if number > 255:
        raise argparse.ArgumentTypeError(
            f"{option} must be at most 255 (a per-channel {noun}): {value!r}"
        )
    return number


def _finite_float(value: str, option: str) -> float:
    number = plain_number(value, option, "number", "a", float)
    if not math.isfinite(number):
        raise argparse.ArgumentTypeError(f"{option} must be finite: {value!r}")
    return number


def max_mae(value: str) -> float:
    """Return a finite ``--max-mae`` value, a per-channel mean in 0..255."""
    number = _finite_float(value, "--max-mae")
    return _channel_amount(value, number, "--max-mae", "mean")


def max_frac(value: str) -> float:
    """Return a finite ``--max-frac`` differing-pixel fraction in 0..1."""
    number = _finite_float(value, "--max-frac")
    if not 0.0 <= number <= 1.0:
        raise argparse.ArgumentTypeError(
            f"--max-frac must be between 0 and 1: {value!r}"
        )
    return number


def tolerance(value: str) -> int:
    """Return a ``--tolerance`` integer per-channel delta in 0..255."""
    number = plain_number(value, "--tolerance", "integer", "an", int)
    return _channel_amount(value, number, "--tolerance", "delta")
