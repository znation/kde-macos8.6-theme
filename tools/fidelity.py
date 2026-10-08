"""Objective fidelity comparison for the Mac OS 8.6 Plasma theme.

The project's acceptance bar is "pixel-perfect", but a rendered surface cannot
be confirmed against its Mac OS 8.6 reference without a repeatable measurement.
This tool supplies that measurement: it decodes two PNG images, compares them
pixel by pixel, and reports objective difference metrics -- mean absolute error
(MAE), per-channel mean absolute error (R, G, B), root-mean-square error
(RMSE), the worst per-channel delta and the coordinate where it occurs, and the
fraction of pixels whose worst channel differs by more than a tolerance.

PNG decoding lives in the sibling module ``tools/png.py``; this file holds the
comparison math and the command-line entry point. Only PNG is read, so the
harness crops a reference screenshot to a surface and saves it as PNG before
comparing. The tool uses only the Python standard library, keeping the check
self-contained and deterministic. The Plasma render step that produces the
candidate image is outside this tool.

Usage::

    python3 tools/fidelity.py CANDIDATE REFERENCE [--crop X,Y,W,H]
        [--max-mae F] [--max-frac F] [--tolerance N]

Exit status: 0 within tolerance, 1 outside tolerance, 2 usage or read error.
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass

if __package__:
    from tools.png import Image, PngError, read_png
else:  # run directly: python3 tools/fidelity.py
    from png import Image, PngError, read_png


class FidelityError(Exception):
    """A candidate and reference image could not be compared."""


# value -> the low and high bytes of value squared.  A byte string's sum of
# squares is then ``sum(low bytes) + (sum(high bytes) << 8)``: two C-level
# ``bytes.translate`` passes instead of a Python call per byte.
_SQUARES_LOW = bytes((value * value) & 0xFF for value in range(256))
_SQUARES_HIGH = bytes((value * value) >> 8 for value in range(256))


def _sum_squares(channel: bytes) -> int:
    """Return the sum of the squares of one channel's byte values.

    ``bytes.map`` over a per-byte lookup is the obvious spelling, but it
    makes a Python-level call per byte.  Splitting each square into its low
    and high byte tables keeps the work inside ``bytes.translate`` and
    ``sum``, which run at C speed; the result is identical because
    ``value**2 == (value**2 & 0xFF) + ((value**2 >> 8) << 8)``.
    """
    return sum(channel.translate(_SQUARES_LOW)) + (
        sum(channel.translate(_SQUARES_HIGH)) << 8
    )


def _abs_diff(a: bytes, b: bytes) -> bytes:
    """Return the per-byte absolute difference of two equal-length byte strings.

    ``bytes(map(abs, map(sub, a, b)))`` is the obvious spelling, but it makes a
    Python-level call per byte.  This computes the same bytes with a handful of
    big-integer operations: the input is packed two bytes per 16-bit lane, each
    lane gets a guard bit so a subtraction cannot borrow into its neighbour,
    and the absolute value is selected from the two per-lane differences.  On
    screenshot-sized inputs it is ~2.7x faster than the ``map()`` form and
    returns byte-identical output.
    """
    length = len(a)
    if length == 0:
        return b""
    if length & 1:
        # Pad to a whole number of 16-bit lanes; the extra byte is dropped by
        # ``to_bytes(length)`` at the end.
        a = a + b"\x00"
        b = b + b"\x00"
    lanes = len(a) // 2
    # 0xFF in the low byte of every lane, and the guard bit (bit 8) of every
    # lane -- the lane-parallel equivalents of a scalar mask.
    low = int.from_bytes(b"\xff\x00" * lanes, "little")
    guard_bit = int.from_bytes(b"\x00\x01" * lanes, "little")
    x = int.from_bytes(a, "little")
    y = int.from_bytes(b, "little")
    # Split each string into its even- and odd-indexed bytes, each already
    # sitting in the low byte of its own 16-bit lane.
    even_x, odd_x = x & low, (x >> 8) & low
    even_y, odd_y = y & low, (y >> 8) & low

    def lane_abs(u: int, v: int) -> int:
        # With the guard bit set, ``u - v`` is 256 + u - v in [1, 511], so the
        # subtraction never borrows across a lane and bit 8 is set exactly when
        # u >= v.  That lane's low byte is then |u - v| already, so the result
        # picks the low byte of whichever of the two differences is >= 256.
        ge = (u | guard_bit) - v
        lt = (v | guard_bit) - u
        higher = ge & guard_bit
        ge_mask = higher - (higher >> 8)  # 0xFF in lanes where u >= v
        return ((ge & low) & ge_mask) | ((lt & low) & (low ^ ge_mask))

    # Lane j of the even/odd halves carries byte 2j / 2j+1, so interleaving the
    # two lane-packed results reconstructs the original byte order.
    return (lane_abs(even_x, even_y) | (lane_abs(odd_x, odd_y) << 8)).to_bytes(
        length, "little"
    )


def _escape_controls(text: str) -> str:
    """Render *text* with control characters escaped for terminal output.

    The documented workflow passes a reference file from
    ``macos8.6-screenshots/`` on the command line, so the path can carry a
    contributor-supplied filename; a shell glob hands it to this tool
    unchanged. Printed raw, an ESC or newline in that name would drive the
    operator's terminal or forge an extra output line, so every control
    character becomes a visible ``\\uXXXX`` escape before the path is shown.
    """
    return "".join(
        ch if ch.isprintable() else f"\\u{ord(ch):04x}" for ch in text
    )


class _ArgumentParser(argparse.ArgumentParser):
    """ArgumentParser whose error diagnostics escape control characters.

    argparse formats some of its own errors (notably ``unrecognized
    arguments: ...``) from raw argv. The documented workflow fills argv from a
    shell glob over the contributor-owned screenshot directory, so those bytes
    never pass through ``main``'s escaping of the candidate and reference
    paths; escaping the message here closes that gap at the output boundary.
    """

    def error(self, message: str) -> None:
        super().error(_escape_controls(message))


@dataclass(frozen=True)
class Metrics:
    """Per-pixel difference between two equally sized images.

    ``mae`` is averaged over all channels; ``mae_r``/``mae_g``/``mae_b`` average
    one channel each, so a systematic colour cast shows up as one channel's MAE
    standing out from the other two. ``max_x``/``max_y`` locate the first pixel
    whose worst channel delta equals ``max_delta``; both are 0 when the images
    are identical.
    """

    width: int
    height: int
    pixels: int
    mae: float
    mae_r: float
    mae_g: float
    mae_b: float
    rmse: float
    max_delta: int
    max_x: int
    max_y: int
    differing: int
    frac_differing: float


def _crop_rect_problem(x: int, y: int, width: int, height: int) -> str | None:
    """Return why ``(x, y, width, height)`` is not a valid crop rectangle."""
    if x < 0 or y < 0 or width <= 0 or height <= 0:
        return (
            f"crop rectangle must have positive size and origin: "
            f"x={x} y={y} w={width} h={height}"
        )
    return None


def crop(image: Image, x: int, y: int, width: int, height: int) -> Image:
    """Return the ``width x height`` region of ``image`` at ``(x, y)``."""
    problem = _crop_rect_problem(x, y, width, height)
    if problem is not None:
        raise FidelityError(problem)
    if x + width > image.width or y + height > image.height:
        raise FidelityError(
            f"crop rectangle x={x} y={y} w={width} h={height} falls outside "
            f"the {image.width}x{image.height} image"
        )
    rows = []
    for row in range(y, y + height):
        start = (row * image.width + x) * 3
        rows.append(image.rgb[start : start + width * 3])
    return Image(width, height, b"".join(rows))


def compare(candidate: Image, reference: Image, tolerance: int = 0) -> Metrics:
    """Compare a candidate image against a reference image.

    Both must be the same size; ``tolerance`` is a per-channel delta.
    """
    if candidate.width != reference.width or candidate.height != reference.height:
        raise FidelityError(
            f"size mismatch: candidate {candidate.width}x{candidate.height} "
            f"vs reference {reference.width}x{reference.height}"
        )
    pa, pb = candidate.rgb, reference.rgb
    # Compare one channel at a time: a strided slice picks a channel,
    # ``_abs_diff`` turns it into that channel's absolute deltas as a byte
    # string, and integer sums feed the metrics.  The equivalent per-byte
    # Python loop dominated runtime on screenshot-sized inputs (tens of
    # millions of bytes).
    dr = _abs_diff(pa[0::3], pb[0::3])
    dg = _abs_diff(pa[1::3], pb[1::3])
    db = _abs_diff(pa[2::3], pb[2::3])

    total_abs_r = sum(dr)
    total_abs_g = sum(dg)
    total_abs_b = sum(db)
    total_sq = _sum_squares(dr) + _sum_squares(dg) + _sum_squares(db)

    max_delta = max(max(dr), max(dg), max(db))
    max_x = 0
    max_y = 0
    if max_delta:
        # Locate the first pixel whose worst channel equals the maximum: the
        # smallest per-channel offset at which any channel reaches max_delta.
        # A channel's byte offset equals its pixel offset, because the three
        # slices are the same length.
        first = min(
            offset
            for offset in (
                dr.find(max_delta),
                dg.find(max_delta),
                db.find(max_delta),
            )
            if offset != -1
        )
        max_x = first % candidate.width
        max_y = first // candidate.width

    # A pixel differs when any channel exceeds tolerance.  Translate each
    # channel to a 0/1 flag byte, OR the three flag strings as one big integer,
    # and popcount it, so a pixel with several differing channels counts once.
    over = bytes(1 if value > tolerance else 0 for value in range(256))
    differing = (
        int.from_bytes(dr.translate(over), "little")
        | int.from_bytes(dg.translate(over), "little")
        | int.from_bytes(db.translate(over), "little")
    ).bit_count()

    pixels = candidate.width * candidate.height
    channels = pixels * 3
    return Metrics(
        width=candidate.width,
        height=candidate.height,
        pixels=pixels,
        mae=(total_abs_r + total_abs_g + total_abs_b) / channels,
        mae_r=total_abs_r / pixels,
        mae_g=total_abs_g / pixels,
        mae_b=total_abs_b / pixels,
        rmse=(total_sq / channels) ** 0.5,
        max_delta=max_delta,
        max_x=max_x,
        max_y=max_y,
        differing=differing,
        frac_differing=differing / pixels,
    )


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
    for part in parts:
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


def _finite_float(value: str, option: str) -> float:
    if not _is_plain_ascii_number(value):
        raise argparse.ArgumentTypeError(
            f"{option} must be a plain ASCII number: {value!r}"
        )
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"{option} must be a number: {value!r}"
        ) from exc
    if not math.isfinite(number):
        raise argparse.ArgumentTypeError(f"{option} must be finite: {value!r}")
    return number


def _max_mae(value: str) -> float:
    number = _finite_float(value, "--max-mae")
    if number < 0:
        raise argparse.ArgumentTypeError(
            f"--max-mae must not be negative: {value!r}"
        )
    if number > 255:
        raise argparse.ArgumentTypeError(
            f"--max-mae must be at most 255 (a per-channel mean): {value!r}"
        )
    return number


def _max_frac(value: str) -> float:
    number = _finite_float(value, "--max-frac")
    if not 0.0 <= number <= 1.0:
        raise argparse.ArgumentTypeError(
            f"--max-frac must be between 0 and 1: {value!r}"
        )
    return number


def _tolerance(value: str) -> int:
    if not _is_plain_ascii_number(value):
        raise argparse.ArgumentTypeError(
            f"--tolerance must be a plain ASCII integer: {value!r}"
        )
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"--tolerance must be an integer: {value!r}"
        ) from exc
    if number < 0:
        raise argparse.ArgumentTypeError(
            f"--tolerance must not be negative: {value!r}"
        )
    if number > 255:
        raise argparse.ArgumentTypeError(
            f"--tolerance must be at most 255 (a per-channel delta): {value!r}"
        )
    return number


def main(argv: list[str] | None = None) -> int:
    parser = _ArgumentParser(
        prog="fidelity",
        description="Measure a rendered PNG surface against a reference PNG.",
        epilog=(
            "exit status: 0 within tolerance, 1 outside tolerance, "
            "2 usage or read error"
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
        default=0.0,
        help="fail when mean absolute error exceeds this (0-255, default 0)",
    )
    parser.add_argument(
        "--max-frac",
        type=_max_frac,
        default=0.0,
        help="fail when the differing-pixel fraction exceeds this (default 0)",
    )
    args = parser.parse_args(argv)

    try:
        candidate = read_png(args.candidate)
        reference = read_png(args.reference)
        if args.crop is not None:
            reference = crop(reference, *args.crop)
        metrics = compare(candidate, reference, tolerance=args.tolerance)
    except (PngError, FidelityError) as exc:
        print(f"fidelity: error: {_escape_controls(str(exc))}", file=sys.stderr)
        return 2

    ok = metrics.mae <= args.max_mae and metrics.frac_differing <= args.max_frac
    print(
        f"candidate: {_escape_controls(args.candidate)}  "
        f"{candidate.width}x{candidate.height}"
    )
    print(
        f"reference: {_escape_controls(args.reference)}  "
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
    print(
        f"{verdict}: max-mae={args.max_mae:.4f} max-frac={args.max_frac:.6f} "
        f"tolerance={args.tolerance}"
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
