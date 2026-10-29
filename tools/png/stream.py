"""The PNG chunk-stream reader: order chunks and collect their payloads.

Turns a PNG's chunk stream into the pieces the decoders and the size-only file
reader need: the validated IHDR payload, the optional PLTE palette, the
concatenated IDAT image data, the optional tRNS transparency payload and
whether that tRNS came before any PLTE chunk. Header validation lives in
``tools/png/header.py``; this module refuses a misordered or
duplicate IHDR, duplicate PLTE or tRNS, a PLTE or tRNS chunk after the image
data, a tRNS chunk the header's color type or palette cannot carry, a tRNS
chunk before a PLTE chunk that is present, a PLTE chunk on a greyscale
color type, non-consecutive IDAT
chunks, a malformed PLTE
length, an unknown critical chunk, a chunk after IEND, a missing IEND and a
missing IHDR, so
every caller sees the same diagnosis.
``tools/png/chunks.py`` does the lower-level framing and CRC checks this
builds on.

The inflated stream is decoded by ``tools/png/read.py``, which calls
:func:`collect_chunks`.
"""

from __future__ import annotations

from .chunks import chunk_name, iter_chunks
from .image import PngError


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
