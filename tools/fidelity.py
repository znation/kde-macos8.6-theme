"""Command-line fidelity comparison for the Mac OS 8.6 Plasma theme.

Compares a rendered PNG surface against a reference screenshot and reports the
comparison metrics from the sibling ``tools/fidelity_metrics.py``: mean
absolute error, per-channel mean absolute error (R, G, B), RMSE, the worst
per-channel delta and where it occurs, and the fraction of differing pixels.

Only PNG is read, so the harness crops a reference screenshot to a surface and
saves it as PNG before comparing. The Plasma render step that produces the
candidate image is outside this tool.

Usage::

    python3 tools/fidelity.py CANDIDATE REFERENCE [--crop X,Y,W,H]
        [--max-mae F] [--max-frac F] [--tolerance N]

The verdict passes when every threshold set with ``--max-mae``/``--max-frac``
is met; when neither is set it passes only when no pixel differs from the
reference by more than ``--tolerance``.

Exit status: 0 when the comparison passes, 1 when it fails, 2 usage or
read error.
"""

from __future__ import annotations

import argparse
import math
import sys
from collections.abc import Callable
from typing import TypeVar

if __package__:
    from tools.fidelity_metrics import (
        FidelityError,
        _crop_rect_problem,
        compare,
        crop,
    )
    from tools.png import PngError, read_png
    from tools.terminal import escape_controls
else:  # run directly: python3 tools/fidelity.py
    from fidelity_metrics import FidelityError, _crop_rect_problem, compare, crop
    from png import PngError, read_png
    from terminal import escape_controls


class _ArgumentParser(argparse.ArgumentParser):
    """ArgumentParser whose error diagnostics escape control characters.

    argparse formats some of its own errors (notably ``unrecognized
    arguments: ...``) from raw argv. The documented workflow fills argv from a
    shell glob over the contributor-owned screenshot directory, so those bytes
    never pass through ``main``'s escaping of the candidate and reference
    paths; escaping the message here closes that gap at the output boundary.
    """

    def error(self, message: str) -> None:
        super().error(escape_controls(message))


def _is_plain_ascii_number(value: str) -> bool:
    """Return True when *value* is ASCII numeric text with no Python extras.

    ``int()``/``float()`` accept forms a command-line number should not:
    underscore digit separators (``1_0`` is 10), non-ASCII decimal digits
    (``\u0661\u0662`` is 12), and surrounding whitespace. Each silently turns
    a stray character into a different value, so the CLI checks the text
    before parsing it. Callers that parse a structured value (the crop
    rectangle) strip each field first, so this whitespace rule applies to the
    scalar options.
    """
    return value.isascii() and "_" not in value and value == value.strip()


def _parse_crop(value: str) -> tuple[int, int, int, int]:
    # Strip each field before the plain-number check: whitespace around a
    # comma-separated field ("0, 0, 10, 10") is the conventional way to write
    # the rectangle, not a stray character that changes the value, so accept
    # it here. The scalar options still reject surrounding whitespace through
    # _is_plain_ascii_number, where it signals a quoting mistake.
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
        if not _is_plain_ascii_number(part):
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
    problem = _crop_rect_problem(x, y, width, height)
    if problem is not None:
        raise argparse.ArgumentTypeError(problem)
    return x, y, width, height


_Number = TypeVar("_Number", int, float)


def _plain_number(
    value: str,
    option: str,
    noun: str,
    article: str,
    parse: Callable[[str], _Number],
) -> _Number:
    """Return ``parse(value)``, rejecting Python-only numeric text.

    ``int()``/``float()`` accept forms a command-line number should not --
    underscore digit separators, non-ASCII decimal digits and surrounding
    whitespace -- so the text is checked before parsing. *noun* names the
    value in the diagnostics ("number" for a float option, "integer" for an
    int one) and *article* is its indefinite article ("a" or "an"); *parse*
    is the stdlib constructor whose ``ValueError`` becomes the option-named
    rejection.
    """
    if not _is_plain_ascii_number(value):
        raise argparse.ArgumentTypeError(
            f"{option} must be a plain ASCII {noun}: {value!r}"
        )
    try:
        return parse(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"{option} must be {article} {noun}: {value!r}"
        ) from exc


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
    number = _plain_number(value, option, "number", "a", float)
    if not math.isfinite(number):
        raise argparse.ArgumentTypeError(f"{option} must be finite: {value!r}")
    return number


def _max_mae(value: str) -> float:
    number = _finite_float(value, "--max-mae")
    return _channel_amount(value, number, "--max-mae", "mean")


def _max_frac(value: str) -> float:
    number = _finite_float(value, "--max-frac")
    if not 0.0 <= number <= 1.0:
        raise argparse.ArgumentTypeError(
            f"--max-frac must be between 0 and 1: {value!r}"
        )
    return number


def _tolerance(value: str) -> int:
    number = _plain_number(value, "--tolerance", "integer", "an", int)
    return _channel_amount(value, number, "--tolerance", "delta")


def main(argv: list[str] | None = None) -> int:
    """Run the comparison CLI; *argv* is the argument list without a program name.

    Following ``argparse`` and the sibling ``tools/check_references.py``,
    ``None`` reads ``sys.argv``.
    """
    parser = _ArgumentParser(
        prog="fidelity",
        description="Measure a rendered PNG surface against a reference PNG.",
        epilog=(
            "exit status: 0 when the comparison passes, 1 when it fails, "
            "2 usage or read error; passes when every --max-mae/--max-frac "
            "threshold set is met, and otherwise when no pixel differs "
            "beyond --tolerance"
        ),
    )
    parser.add_argument("candidate", help="rendered surface image (PNG)")
    parser.add_argument("reference", help="reference image (PNG)")
    parser.add_argument(
        "--crop",
        type=_parse_crop,
        metavar="X,Y,W,H",
        help="crop the reference to this region before comparing",
    )
    parser.add_argument(
        "--tolerance",
        type=_tolerance,
        default=0,
        help="per-channel delta (0-255) at or below which a pixel is not 'differing'",
    )
    parser.add_argument(
        "--max-mae",
        type=_max_mae,
        default=None,
        help=(
            "fail when mean absolute error exceeds this (0-255); when set, "
            "replaces the default no-differing-pixel gate"
        ),
    )
    parser.add_argument(
        "--max-frac",
        type=_max_frac,
        default=None,
        help=(
            "fail when the differing-pixel fraction exceeds this (0-1); when "
            "set, replaces the default no-differing-pixel gate"
        ),
    )
    args = parser.parse_args(argv)

    try:
        candidate = read_png(args.candidate)
        reference = read_png(args.reference)
        if args.crop is not None:
            reference = crop(reference, *args.crop)
        metrics = compare(candidate, reference, tolerance=args.tolerance)
    except (PngError, FidelityError) as exc:
        print(f"fidelity: error: {escape_controls(str(exc))}", file=sys.stderr)
        return 2

    # Every threshold the caller set is a budget that must be met. With no
    # budget set the verdict falls back to the strictest one: no pixel
    # differing by more than --tolerance. --max-mae and --max-frac therefore
    # replace the default gate rather than silently defaulting to zero, which
    # would require byte-exactness no matter what --tolerance says.
    budgets = []
    if args.max_mae is not None:
        budgets.append(metrics.mae <= args.max_mae)
    if args.max_frac is not None:
        budgets.append(metrics.frac_differing <= args.max_frac)
    ok = all(budgets) if budgets else metrics.frac_differing <= 0.0
    print(
        f"candidate: {escape_controls(args.candidate)}  "
        f"{candidate.width}x{candidate.height}"
    )
    print(
        f"reference: {escape_controls(args.reference)}  "
        f"{reference.width}x{reference.height}"
    )
    print(f"pixels compared: {metrics.pixels}")
    print(f"mean absolute error: {metrics.mae:.4f}")
    print(
        f"per-channel MAE (R, G, B): {metrics.mae_r:.4f} "
        f"{metrics.mae_g:.4f} {metrics.mae_b:.4f}"
    )
    print(f"RMSE: {metrics.rmse:.4f}")
    print(
        f"max channel delta: {metrics.max_delta} "
        f"at ({metrics.max_x}, {metrics.max_y})"
    )
    print(
        f"differing pixels: {metrics.differing} / {metrics.pixels} "
        f"({metrics.frac_differing:.6f})"
    )
    verdict = "PASS" if ok else "FAIL"
    max_mae = "unset" if args.max_mae is None else f"{args.max_mae:.4f}"
    max_frac = "unset" if args.max_frac is None else f"{args.max_frac:.6f}"
    print(
        f"{verdict}: max-mae={max_mae} max-frac={max_frac} "
        f"tolerance={args.tolerance}"
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
