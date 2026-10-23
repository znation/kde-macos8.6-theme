"""The PNG chunk-stream reader: validate a stream and collect its payloads.

Turns a PNG's chunk stream into the pieces the decoders and the size-only file
reader need: the validated IHDR payload, the optional PLTE palette, the
concatenated IDAT image data, the optional tRNS transparency payload and
whether that tRNS came before any PLTE chunk. It refuses a misordered or
duplicate IHDR, duplicate PLTE or tRNS, a PLTE or tRNS chunk after the image
data, a tRNS chunk the header's color type or palette cannot carry, a tRNS
chunk before a PLTE chunk that is present, a PLTE chunk on a greyscale
color type, non-consecutive IDAT
chunks, a malformed PLTE
length, an unknown critical chunk, a chunk after IEND, a missing IEND and a
missing IHDR, so
every caller sees the same diagnosis. :func:`parse_ihdr` validates the header
fields, :func:`check_plte` refuses a palette the header's color type cannot
carry, :func:`check_trns` validates transparency against that header and
:func:`check_pixel_limit` bounds the declared size;
``tools/png/chunks.py`` does the lower-level framing and CRC checks this
builds on.

The inflated stream is decoded by ``tools/png/read.py``, which calls
:func:`collect_chunks`, and the file reader ``tools/png/loader.py`` reuses
:func:`parse_ihdr` and :func:`check_pixel_limit` for a size-only read.
"""

from __future__ import annotations

import struct

try:
    from tools.ints import is_plain_int
except ImportError:  # imported as the top-level package `png` by a directly run tool
    from ints import is_plain_int

from .chunks import chunk_name, iter_chunks
from .image import PngError
from .trns import check_palette_trns_length, check_sample_trns_length

# color_type -> channels per pixel at bit depth 8
CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}

# Cap on declared pixels. A PNG's IDAT can be arbitrarily smaller than the
# scanlines it expands to, so a few KB can demand gigabytes (a decompression
# bomb). 64 MP is far above any screenshot this tool compares and still bounds
# one decode to a few hundred MB.
MAX_PIXELS = 64_000_000


def validate_max_rows(max_rows: int | None) -> None:
    """Raise :class:`PngError` unless *max_rows* is None or a positive int.

    ``bool`` is rejected even though it is an ``int`` subclass: ``True`` would
    pass as 1 and silently select a different row bound. This lives apart from
    :func:`tools.png.read.decode_png` so a caller that serves an already-decoded
    image (the test reference cache) can apply the same bound check without
    decoding.
    """
    if max_rows is None:
        return
    if not is_plain_int(max_rows):
        raise PngError(
            f"max_rows must be an integer or None: max_rows={max_rows!r}"
        )
    if max_rows < 1:
        raise PngError(f"max_rows must be positive: max_rows={max_rows}")


def parse_ihdr(header: bytes) -> tuple[int, int, int]:
    """Validate a 13-byte IHDR payload, returning ``(width, height, color_type)``.

    Both :func:`tools.png.read.decode_png` and
    :func:`tools.png.loader.read_png_size` use this so a size-only read rejects
    the same malformed or unsupported headers the decoder does.
    """
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
        raise PngError(
            "interlaced PNG is not supported; re-export it without "
            "interlacing"
        )
    if compression != 0:
        raise PngError(
            f"unsupported PNG compression method {compression} (need 0)"
        )
    if filt != 0:
        raise PngError(f"unsupported PNG filter method {filt} (need 0)")
    if color_type not in CHANNELS:
        # Name the set the decoder handles, the way the bit-depth,
        # compression and filter messages name their required value, so the
        # operator does not have to look up which PNG color types are valid.
        supported = ", ".join(str(value) for value in sorted(CHANNELS))
        raise PngError(
            f"unsupported PNG color type {color_type} "
            f"(need one of {supported})"
        )
    if width == 0 or height == 0:
        # Name the declared dimensions so the operator can tell which field is
        # zero (and in which header) instead of having to dump the bytes.
        raise PngError(
            f"PNG header declares zero width or height: {width}x{height}; "
            "both dimensions must be positive"
        )
    return width, height, color_type


def check_trns(
    trns: bytes | None,
    color_type: int,
    palette: bytes | None,
    trns_before_plte: bool = False,
) -> None:
    """Refuse a *trns* payload the header's color type and palette cannot carry.

    The PNG spec allows tRNS only for greyscale (0), truecolor (2) and palette
    (3) images: color types 4 and 6 carry an alpha channel in every pixel, so
    a tRNS chunk there has no meaning. A greyscale tRNS names one 16-bit
    sample, a truecolor one three, and a palette tRNS one alpha byte for each
    of its first palette entries. A tRNS chunk must follow the PLTE chunk, if
    any, so *trns_before_plte* records that the stream put it earlier; that
    ordering is illegal whenever a PLTE is present, including a truecolor
    image's suggested palette. Both decoders call this, so the RGB path refuses
    the same malformed transparency the RGBA path would even though it discards
    alpha.
    """
    if trns is None:
        return
    if color_type in (4, 6):
        raise PngError(
            f"PNG has a tRNS chunk, but color type {color_type} carries "
            "transparency in each pixel; tRNS is only valid for color types "
            "0, 2 and 3"
        )
    if color_type == 3 and palette is None:
        # The decoder names the missing PLTE chunk; a tRNS length cannot be
        # judged until the palette that bounds it is present.
        return
    if trns_before_plte and palette is not None:
        raise PngError(
            "PNG has a tRNS chunk before its PLTE chunk; tRNS must follow "
            "the PLTE chunk, if any"
        )
    if color_type == 3:
        check_palette_trns_length(trns, len(palette) // 3)
        return
    check_sample_trns_length(trns, color_type)


def check_plte(palette: bytes | None, color_type: int) -> None:
    """Refuse a palette the header's color type does not permit.

    The PNG spec makes PLTE required for color type 3, optional as a
    suggested palette for the truecolor types 2 and 6, and prohibited for the
    greyscale types 0 and 4 (whose pixels are samples, not palette indices).
    Both decoders call this, so a file carrying a palette its color type can
    never use is refused instead of decoding as if that chunk were absent.
    """
    if palette is None or color_type in (2, 3, 6):
        return
    raise PngError(
        f"PNG has a PLTE chunk, but color type {color_type} is greyscale; "
        "PLTE is prohibited for the greyscale color types 0 and 4"
    )


def check_pixel_limit(width: int, height: int) -> None:
    """Raise :class:`PngError` when *width* x *height* exceeds ``MAX_PIXELS``."""
    if width * height > MAX_PIXELS:
        raise PngError(
            f"PNG declares {width}x{height} ({width * height} pixels), larger "
            f"than the {MAX_PIXELS}-pixel limit"
        )


def _take_ihdr(
    payload: bytes, header: bytes | None, previous_chunk: bytes | None
) -> bytes:
    """Return *payload* as the image header, refusing a misordered IHDR.

    *previous_chunk* is the first chunk already seen, or None when this is
    the first chunk. The PNG spec gives the image exactly one header and puts
    it first; a stream that reaches IDAT before its header, or carries a
    second IHDR, would otherwise decode against a header a conformant reader
    would not use and silently produce different pixels.
    """
    if header is not None:
        raise PngError(
            "PNG has more than one IHDR chunk; the image header "
            "must appear exactly once"
        )
    if previous_chunk is not None:
        raise PngError(
            f"PNG's IHDR chunk must be the first chunk, but "
            f"{chunk_name(previous_chunk)} comes before it"
        )
    return payload


def _take_plte(payload: bytes) -> bytes:
    """Return *payload* as the palette, refusing a malformed PLTE length."""
    if len(payload) % 3 or not 3 <= len(payload) <= 768:
        raise PngError(
            f"PLTE chunk is {len(payload)} bytes; expected a multiple "
            "of 3 between 3 and 768 (1-256 palette entries)"
        )
    return payload


def collect_chunks(
    data: bytes,
) -> tuple[bytes, bytes | None, bytearray, bytes | None, bool]:
    """Return ``(header, palette, idat, trns, trns_before_plte)``.

    Walks the chunks after the signature, collecting the image header, palette,
    IDAT payloads, the optional tRNS transparency payload and whether that
    tRNS appeared before any PLTE chunk (an ordering :func:`check_trns` refuses
    once a PLTE is known to be present). It refuses
    a misordered or duplicate IHDR, duplicate PLTE or tRNS, a PLTE or tRNS
    chunk after the image data, non-consecutive IDAT chunks, a malformed PLTE
    length, an unknown critical chunk, a chunk after IEND, a missing IEND and a
    missing IHDR.
    Filtering and colour expansion are the decoders' concern; this helper owns
    only the framing the rest of the decode reads.
    """
    header = None
    palette = None
    trns = None
    trns_before_plte = False
    idat = bytearray()
    saw_idat = False
    idat_closed = False
    saw_iend = False
    first_chunk = None
    for ctype, payload in iter_chunks(data):
        if saw_iend:
            # IEND ends the PNG datastream and must be last, so a complete
            # chunk after it is malformed trailing data. Without this guard
            # the break below drops that chunk, accepting a stream a
            # conformant reader refuses.
            raise PngError(
                f"PNG has a {chunk_name(ctype)} chunk after IEND; IEND "
                "must be the last chunk"
            )
        # Record the first chunk before handling it, but pass the previous
        # value to the IHDR guard: the first chunk is allowed to be IHDR, while
        # a later one is not.
        previous_first = first_chunk
        if first_chunk is None:
            first_chunk = ctype
        if ctype == b"IHDR":
            header = _take_ihdr(payload, header, previous_first)
            continue
        if ctype == b"IDAT":
            if idat_closed:
                raise PngError(
                    "PNG has an IDAT chunk after a non-IDAT chunk; IDAT "
                    "chunks must be consecutive"
                )
            saw_idat = True
            idat += payload
            continue
        # The PNG spec requires the IDAT chunks to be consecutive, so any other
        # chunk ends the image-data run: a later IDAT is misordered. Ancillary
        # chunks after the final IDAT remain allowed, which is why this only
        # closes the run rather than rejecting the chunk.
        if saw_idat:
            idat_closed = True
        if ctype == b"PLTE":
            if saw_idat:
                raise PngError(
                    "PNG has a PLTE chunk after the image data; PLTE must "
                    "precede IDAT"
                )
            if palette is not None:
                raise PngError(
                    "PNG has more than one PLTE chunk; the palette "
                    "must appear at most once"
                )
            palette = _take_plte(payload)
            continue
        if ctype == b"tRNS":
            if saw_idat:
                raise PngError(
                    "PNG has a tRNS chunk after the image data; tRNS must "
                    "precede IDAT"
                )
            # tRNS is ancillary, but it changes what the pixels mean for the
            # three non-alpha colour types, so it must be collected rather
            # than skipped with the other unknown ancillary chunks. Colour
            # types 4 and 6 carry their transparency in the pixel itself, so
            # :func:`tools.png.read.decode_rgba` ignores it for those. A second
            # tRNS would
            # silently replace the first, changing the decoded alpha, so
            # refuse it the way a second IHDR is refused.
            if trns is not None:
                raise PngError(
                    "PNG has more than one tRNS chunk; transparency "
                    "must appear at most once"
                )
            trns = payload
            if palette is None:
                # Record the ordering, not a verdict: :func:`check_trns`
                # decides once the stream has shown whether a PLTE follows.
                # tRNS before a PLTE chunk is illegal for every color type,
                # including a truecolor image's suggested palette.
                trns_before_plte = True
            continue
        if ctype == b"IEND":
            # Keep iterating rather than breaking so a chunk after IEND is
            # refused by the guard above instead of silently dropped.
            saw_iend = True
            continue
        if ctype[:1].isupper():
            # A chunk whose first byte is uppercase is critical: the decoder
            # must understand it to know how the image is interpreted. The
            # four critical chunks (IHDR, PLTE, IDAT, IEND) are all modelled
            # above, so an unknown one carries data that may change the
            # pixels. Ignoring it the way an unknown *ancillary* chunk
            # (lowercase first byte) is ignored could decode the image wrong
            # with no sign that anything was skipped, so refuse it by name.
            raise PngError(
                f"unknown critical PNG chunk {chunk_name(ctype)}"
            )
    if header is None:
        raise PngError("PNG has no IHDR chunk")
    if not saw_iend:
        # The IEND chunk terminates the chunk stream, so a file cut at a
        # chunk boundary can hold a complete IHDR and IDAT and still be
        # truncated. Without this the decoder returns the image from the
        # partial stream as if the file were whole.
        raise PngError(
            "PNG has no IEND chunk (the chunk stream may be truncated)"
        )
    return header, palette, idat, trns, trns_before_plte
