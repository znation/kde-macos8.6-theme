"""PNG reading for the Mac OS 8.6 fidelity tooling.

Decodes 8-bit, non-interlaced PNG images (color types 0, 2, 3, 4 and 6) into
tightly packed RGB bytes, using only the Python standard library. The fidelity
comparison in ``tools/fidelity.py`` is the only consumer today; keeping the
reader separate lets a future capture or render step read PNGs without pulling
in the comparison and CLI layers.

Raises :class:`PngError` for a malformed or unsupported PNG.
"""

from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass
from pathlib import Path

_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

# color_type -> channels per pixel at bit depth 8
_CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}

# Cap on declared pixels. A PNG's IDAT can be arbitrarily smaller than the
# scanlines it expands to, so a few KB can demand gigabytes (a decompression
# bomb). 64 MP is far above any screenshot this tool compares and still bounds
# one decode to a few hundred MB.
_MAX_PIXELS = 64_000_000


class PngError(Exception):
    """A PNG file could not be read or decoded."""


@dataclass(frozen=True)
class Image:
    """An 8-bit RGB image with tightly packed ``width * height * 3`` bytes."""

    width: int
    height: int
    rgb: bytes


def _iter_chunks(data: bytes):
    pos = len(_PNG_SIGNATURE)
    while pos + 8 <= len(data):
        (length,) = struct.unpack(">I", data[pos : pos + 4])
        ctype = data[pos + 4 : pos + 8]
        payload = data[pos + 8 : pos + 8 + length]
        if len(payload) != length:
            raise PngError(
                f"truncated PNG chunk {ctype.decode('ascii', 'replace')!r} at "
                f"offset {pos}: declared {length} payload bytes, only "
                f"{len(payload)} present"
            )
        checksum = data[pos + 8 + length : pos + 12 + length]
        if len(checksum) != 4:
            raise PngError(
                f"truncated PNG chunk {ctype.decode('ascii', 'replace')!r} CRC "
                f"at offset {pos + 8 + length}: expected 4 bytes, got "
                f"{len(checksum)}"
            )
        (expected,) = struct.unpack(">I", checksum)
        actual = zlib.crc32(ctype + payload) & 0xFFFFFFFF
        if actual != expected:
            raise PngError(
                f"PNG chunk {ctype.decode('ascii', 'replace')!r} has a bad CRC"
            )
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
        raise PngError(
            f"PNG image data is shorter than its header declares: got "
            f"{len(raw)} bytes, expected {expected} for a {width}x{height} image"
        )
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
            raise PngError(f"unsupported PNG filter type {ftype}")
        out[dst : dst + stride] = line
        dst += stride
        prev = line
    return bytes(out)


def _to_rgb(color_type: int, samples: bytes, palette: bytes | None) -> bytes:
    if color_type == 2:  # truecolor RGB
        return samples
    if color_type == 6:  # truecolor + alpha, alpha ignored
        # Drop every 4th (alpha) byte with one C-level slice deletion; a
        # per-pixel Python generator here costs tens of millions of bytecode
        # steps on a megapixel image.
        out = bytearray(samples)
        del out[3::4]
        return bytes(out)
    if color_type == 0:  # grayscale
        return bytes(b for g in samples for b in (g, g, g))
    if color_type == 4:  # grayscale + alpha, alpha ignored
        return bytes(b for i in range(0, len(samples), 2) for b in (samples[i],) * 3)
    if color_type == 3:  # palette
        if palette is None:
            raise PngError("palette PNG has no PLTE chunk")
        out = bytearray()
        for index in samples:
            base = index * 3
            if base + 3 > len(palette):
                raise PngError(
                    f"palette PNG index {index} is outside PLTE "
                    f"(palette has {len(palette)} bytes)"
                )
            out += palette[base : base + 3]
        return bytes(out)
    raise PngError(f"unsupported PNG color type {color_type}")


def decode_png(data: bytes) -> Image:
    """Decode an 8-bit, non-interlaced PNG into an :class:`Image`."""
    if not data.startswith(_PNG_SIGNATURE):
        raise PngError("not a PNG file")
    header = None
    palette = None
    idat = bytearray()
    for ctype, payload in _iter_chunks(data):
        if ctype == b"IHDR":
            header = payload
        elif ctype == b"PLTE":
            if len(payload) % 3 or not 3 <= len(payload) <= 768:
                raise PngError(
                    f"PLTE chunk is {len(payload)} bytes; expected a multiple "
                    "of 3 between 3 and 768 (1-256 palette entries)"
                )
            palette = payload
        elif ctype == b"IDAT":
            idat += payload
        elif ctype == b"IEND":
            break
    if header is None:
        raise PngError("PNG has no IHDR chunk")
    if len(header) != 13:
        raise PngError(
            f"IHDR chunk has {len(header)} bytes, expected 13"
        )
    width, height, depth, color_type, compression, filt, interlace = struct.unpack(
        ">IIBBBBB", header
    )
    if depth != 8:
        raise PngError(f"unsupported PNG bit depth {depth} (need 8)")
    if interlace != 0:
        raise PngError("interlaced PNG is not supported")
    if compression != 0:
        raise PngError(
            f"unsupported PNG compression method {compression} (need 0)"
        )
    if filt != 0:
        raise PngError(f"unsupported PNG filter method {filt} (need 0)")
    if color_type not in _CHANNELS:
        raise PngError(f"unsupported PNG color type {color_type}")
    if width == 0 or height == 0:
        raise PngError("PNG has zero width or height")
    channels = _CHANNELS[color_type]
    # Bound the work by the header before zlib sees any data: reject an image
    # too large to be a screenshot, then decompress at most the exact unfiltered
    # byte count the header declares, so an oversized stream cannot be expanded.
    if width * height > _MAX_PIXELS:
        raise PngError(
            f"PNG declares {width}x{height} ({width * height} pixels), larger "
            f"than the {_MAX_PIXELS}-pixel limit"
        )
    expected_raw = height * (width * channels + 1)
    if not idat:
        # A PNG truncated before its IDAT chunk, or one whose IDAT is empty,
        # reaches zlib with no compressed data; zlib then reports an opaque
        # "incomplete or truncated stream" that names neither the chunk nor
        # the missing data.
        raise PngError("PNG has no IDAT image data")
    decompressor = zlib.decompressobj()
    try:
        raw = decompressor.decompress(bytes(idat), expected_raw)
    except zlib.error as exc:
        raise PngError(f"corrupt PNG image data: {exc}") from exc
    if decompressor.unconsumed_tail:
        raise PngError(
            f"PNG image data decompresses to more than the {expected_raw} bytes "
            f"its {width}x{height} header declares"
        )
    if not decompressor.eof:
        # A stream cut before its end marker can still yield exactly
        # expected_raw bytes; without this the adler32 trailer that
        # zlib.decompress used to verify would be dropped silently.
        raise PngError(
            "PNG image data is truncated: the compressed stream ends before "
            "its final block"
        )
    samples = _unfilter(raw, width, height, channels)
    return Image(width, height, _to_rgb(color_type, samples, palette))


def read_png(path: str | Path) -> Image:
    try:
        data = Path(path).read_bytes()
    except OSError as exc:
        raise PngError(f"cannot read {path}: {exc}") from exc
    try:
        return decode_png(data)
    except PngError as exc:
        raise PngError(f"cannot decode {path}: {exc}") from exc

