"""Objective fidelity comparison for the Mac OS 8.6 Plasma theme.

The project's acceptance bar is "pixel-perfect", but a rendered surface cannot
be confirmed against its Mac OS 8.6 reference without a repeatable measurement.
This tool supplies that measurement: it decodes two PNG images, compares them
pixel by pixel, and reports objective difference metrics -- mean absolute error
(MAE), root-mean-square error (RMSE), the worst per-channel delta, and the
fraction of pixels whose worst channel differs by more than a tolerance.

Only PNG is read, so the harness crops a reference screenshot to a surface and
saves it as PNG before comparing. The tool uses only the Python standard
library, keeping the check self-contained and deterministic. The Plasma render
step that produces the candidate image is outside this tool.

Usage::

    python3 tools/fidelity.py CANDIDATE REFERENCE [--crop X,Y,W,H]
        [--max-mae F] [--max-frac F] [--tolerance N]

Exit status: 0 within tolerance, 1 outside tolerance, 2 usage or read error.
"""

from __future__ import annotations

import argparse
import struct
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path

_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

# color_type -> channels per pixel at bit depth 8
_CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}


class FidelityError(Exception):
    """A candidate or reference image could not be read or compared."""


@dataclass(frozen=True)
class Image:
    """An 8-bit RGB image with tightly packed ``width * height * 3`` bytes."""

    width: int
    height: int
    rgb: bytes


@dataclass(frozen=True)
class Metrics:
    """Per-pixel difference between two equally sized images."""

    width: int
    height: int
    pixels: int
    mae: float
    rmse: float
    max_delta: int
    differing: int
    frac_differing: float


def _iter_chunks(data: bytes):
    pos = len(_PNG_SIGNATURE)
    while pos + 8 <= len(data):
        (length,) = struct.unpack(">I", data[pos : pos + 4])
        ctype = data[pos + 4 : pos + 8]
        payload = data[pos + 8 : pos + 8 + length]
        if len(payload) != length:
            raise FidelityError("truncated PNG chunk")
        yield ctype, payload
        pos += 12 + length


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def _unfilter(raw: bytes, width: int, height: int, channels: int) -> bytes:
    stride = width * channels
    expected = height * (stride + 1)
    if len(raw) < expected:
        raise FidelityError("PNG image data is shorter than its header declares")
    out = bytearray(height * stride)
    prev = bytearray(stride)
    src = 0
    dst = 0
    for _ in range(height):
        ftype = raw[src]
        src += 1
        line = bytearray(raw[src : src + stride])
        src += stride
        if ftype == 1:
            for i in range(channels, stride):
                line[i] = (line[i] + line[i - channels]) & 0xFF
        elif ftype == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif ftype == 3:
            for i in range(stride):
                a = line[i - channels] if i >= channels else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif ftype == 4:
            for i in range(stride):
                a = line[i - channels] if i >= channels else 0
                c = prev[i - channels] if i >= channels else 0
                line[i] = (line[i] + _paeth(a, prev[i], c)) & 0xFF
        elif ftype != 0:
            raise FidelityError(f"unsupported PNG filter type {ftype}")
        out[dst : dst + stride] = line
        dst += stride
        prev = line
    return bytes(out)


def _to_rgb(color_type: int, samples: bytes, palette: bytes | None) -> bytes:
    if color_type == 2:  # truecolor RGB
        return samples
    if color_type == 6:  # truecolor + alpha, alpha ignored
        return bytes(
            b for i in range(0, len(samples), 4) for b in samples[i : i + 3]
        )
    if color_type == 0:  # grayscale
        return bytes(b for g in samples for b in (g, g, g))
    if color_type == 4:  # grayscale + alpha, alpha ignored
        return bytes(b for i in range(0, len(samples), 2) for b in (samples[i],) * 3)
    if color_type == 3:  # palette
        if palette is None:
            raise FidelityError("palette PNG has no PLTE chunk")
        out = bytearray()
        for index in samples:
            base = index * 3
            if base + 3 > len(palette):
                raise FidelityError("palette PNG index is outside PLTE")
            out += palette[base : base + 3]
        return bytes(out)
    raise FidelityError(f"unsupported PNG color type {color_type}")


def decode_png(data: bytes) -> Image:
    """Decode an 8-bit, non-interlaced PNG into an :class:`Image`."""
    if not data.startswith(_PNG_SIGNATURE):
        raise FidelityError("not a PNG file")
    header = None
    palette = None
    idat = bytearray()
    for ctype, payload in _iter_chunks(data):
        if ctype == b"IHDR":
            header = payload
        elif ctype == b"PLTE":
            palette = payload
        elif ctype == b"IDAT":
            idat += payload
        elif ctype == b"IEND":
            break
    if header is None:
        raise FidelityError("PNG has no IHDR chunk")
    if len(header) != 13:
        raise FidelityError(
            f"IHDR chunk has {len(header)} bytes, expected 13"
        )
    width, height, depth, color_type, compression, filt, interlace = struct.unpack(
        ">IIBBBBB", header
    )
    if depth != 8:
        raise FidelityError(f"unsupported PNG bit depth {depth} (need 8)")
    if interlace != 0:
        raise FidelityError("interlaced PNG is not supported")
    if compression != 0 or filt != 0:
        raise FidelityError("unsupported PNG compression or filter method")
    if color_type not in _CHANNELS:
        raise FidelityError(f"unsupported PNG color type {color_type}")
    if width == 0 or height == 0:
        raise FidelityError("PNG has zero width or height")
    try:
        raw = zlib.decompress(bytes(idat))
    except zlib.error as exc:
        raise FidelityError(f"corrupt PNG image data: {exc}") from exc
    channels = _CHANNELS[color_type]
    samples = _unfilter(raw, width, height, channels)
    return Image(width, height, _to_rgb(color_type, samples, palette))


def read_png(path: str | Path) -> Image:
    try:
        data = Path(path).read_bytes()
    except OSError as exc:
        raise FidelityError(f"cannot read {path}: {exc}") from exc
    return decode_png(data)


def crop(image: Image, x: int, y: int, width: int, height: int) -> Image:
    """Return the ``width x height`` region of ``image`` at ``(x, y)``."""
    if x < 0 or y < 0 or width <= 0 or height <= 0:
        raise FidelityError("crop rectangle must have positive size and origin")
    if x + width > image.width or y + height > image.height:
        raise FidelityError("crop rectangle falls outside the image")
    rows = []
    for row in range(y, y + height):
        start = (row * image.width + x) * 3
        rows.append(image.rgb[start : start + width * 3])
    return Image(width, height, b"".join(rows))


def compare(a: Image, b: Image, tolerance: int = 0) -> Metrics:
    """Compare two equally sized images. ``tolerance`` is a per-channel delta."""
    if a.width != b.width or a.height != b.height:
        raise FidelityError(
            f"size mismatch: {a.width}x{a.height} vs {b.width}x{b.height}"
        )
    pa, pb = a.rgb, b.rgb
    total_abs = 0
    total_sq = 0
    max_delta = 0
    differing = 0
    for i in range(0, len(pa), 3):
        dr = pa[i] - pb[i]
        dg = pa[i + 1] - pb[i + 1]
        db = pa[i + 2] - pb[i + 2]
        ar, ag, ab = abs(dr), abs(dg), abs(db)
        total_abs += ar + ag + ab
        total_sq += dr * dr + dg * dg + db * db
        worst = max(ar, ag, ab)
        if worst > max_delta:
            max_delta = worst
        if worst > tolerance:
            differing += 1
    pixels = a.width * a.height
    channels = pixels * 3
    return Metrics(
        width=a.width,
        height=a.height,
        pixels=pixels,
        mae=total_abs / channels,
        rmse=(total_sq / channels) ** 0.5,
        max_delta=max_delta,
        differing=differing,
        frac_differing=differing / pixels,
    )


def _parse_crop(value: str) -> tuple[int, int, int, int]:
    parts = value.split(",")
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("crop must be X,Y,W,H")
    try:
        x, y, width, height = (int(part) for part in parts)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("crop values must be integers") from exc
    return x, y, width, height


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="fidelity",
        description="Measure a rendered PNG surface against a reference PNG.",
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
        type=int,
        default=0,
        help="per-channel delta at or below which a pixel is not 'differing'",
    )
    parser.add_argument(
        "--max-mae",
        type=float,
        default=0.0,
        help="fail when mean absolute error exceeds this (default 0)",
    )
    parser.add_argument(
        "--max-frac",
        type=float,
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
    except FidelityError as exc:
        print(f"fidelity: error: {exc}", file=sys.stderr)
        return 2

    ok = metrics.mae <= args.max_mae and metrics.frac_differing <= args.max_frac
    print(f"candidate: {args.candidate}  {candidate.width}x{candidate.height}")
    print(f"reference: {args.reference}  {reference.width}x{reference.height}")
    print(f"pixels compared: {metrics.pixels}")
    print(f"mean absolute error: {metrics.mae:.4f}")
    print(f"RMSE: {metrics.rmse:.4f}")
    print(f"max channel delta: {metrics.max_delta}")
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
