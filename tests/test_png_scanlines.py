"""Direct tests for tools/png/scanlines.py's raw scanline handling.

The decode tests reach this module through ``decode_png`` with complete, valid
image data. These tests call it directly so its own contracts are pinned: the
declared byte count (the one formula both the decompression bound and the
truncation check use), the row bound's skip arithmetic, and the raw layout
``drop_alpha`` returns. The chunk framing and colour expansion live in
``test_png_chunks`` and ``test_png_decode``.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import unittest
import zlib

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.png_fixtures import make_png  # noqa: E402
from tools.png.chunks import iter_chunks  # noqa: E402
from tools.png.scanlines import (  # noqa: E402
    drop_alpha,
    raw_byte_length,
    unfilter,
)


def _inflated_raw(width, height, rows, color_type, filter_types=None):
    """Return the filtered scanline stream ``make_png`` would compress.

    Inflating the fixture's IDAT gives the exact raw layout
    ``tools/png/scanlines.py`` consumes: one filter-type byte plus the
    filtered samples per row.
    """
    data = make_png(
        width,
        height,
        rows,
        color_type=color_type,
        filter_types=filter_types,
    )
    idat = b"".join(
        payload for ctype, payload in iter_chunks(data) if ctype == b"IDAT"
    )
    return zlib.decompress(idat)


class TestRawByteLength(unittest.TestCase):
    def test_counts_one_filter_byte_per_row_for_every_channel_count(self):
        # raw_byte_length is the single formula behind both the decode-time
        # decompression bound and the later truncation check. Pin it against
        # the bytes make_png actually writes for one-, two-, three- and
        # four-channel colour types, so an off-by-one in either the filter
        # byte or the stride cannot hide behind a decode that never asks for
        # its value directly.
        width, height = 3, 2
        for channels, color_type in ((1, 0), (2, 4), (3, 2), (4, 6)):
            rows = [
                bytes(range(row * width * channels, (row + 1) * width * channels))
                for row in range(height)
            ]
            with self.subTest(channels=channels):
                raw = _inflated_raw(width, height, rows, color_type)
                self.assertEqual(
                    len(raw), raw_byte_length(width, height, channels)
                )

    def test_empty_image_has_no_filter_bytes(self):
        self.assertEqual(raw_byte_length(0, 0, 4), 0)


class TestUnfilterRowBound(unittest.TestCase):
    def test_bound_returns_the_unbounded_prefix_for_every_filter_type(self):
        # The decode-level bound test uses filter type 0 rows, so it never
        # exercises a predictor under truncation. Use one row per filter type
        # (0 None, 1 Sub, 2 Up, 3 Average, 4 Paeth): every bound must return
        # exactly the unbounded decode's top rows, which is only true when
        # each kept row unfilters against the previous kept row.
        width, channels = 3, 4
        rows = [
            bytes((row * 37 + i * 11) % 256 for i in range(width * channels))
            for row in range(5)
        ]
        raw = _inflated_raw(
            width, len(rows), rows, color_type=6, filter_types=[0, 1, 2, 3, 4]
        )
        full = unfilter(raw, width, len(rows), channels)
        self.assertEqual(full, b"".join(rows))
        for bound in range(1, len(rows) + 1):
            with self.subTest(bound=bound):
                self.assertEqual(
                    unfilter(raw, width, len(rows), channels, max_rows=bound),
                    full[: bound * width * channels],
                )

    def test_skipped_rows_still_advance_past_their_filter_byte(self):
        # With a bound, the rows past it are not unfiltered but their filter
        # type is still checked, so the skip must advance by the payload
        # stride *after* the filter byte was consumed. Every payload byte here
        # is above 4: a skip that landed on one would be rejected as a bad
        # filter type (or, if it silently accepted it, return the wrong row).
        raw = bytes([0, 0xAA, 1, 0xBB, 2, 0xCC])
        self.assertEqual(unfilter(raw, 1, 3, 1, max_rows=1), b"\xAA")
        # The same stream without a bound reconstructs all three rows.
        self.assertEqual(
            unfilter(raw, 1, 3, 1), bytes([0xAA, 0xBB, (0xCC + 0xBB) & 0xFF])
        )


class TestUnfilterColumnBound(unittest.TestCase):
    def test_bound_returns_the_unbounded_prefix_for_every_filter_type(self):
        # As with the row bound, every predictor must reproduce the full
        # decode's row prefix: Sub and Paeth carry the left neighbour, Up
        # carries the above byte, and Average both. A column bound that read
        # only the prefix's payload without skipping the rest of the source
        # row would misalign the next row's filter byte and fail here.
        width, channels = 4, 3
        rows = [
            bytes((row * 37 + i * 11) % 256 for i in range(width * channels))
            for row in range(5)
        ]
        raw = _inflated_raw(
            width, len(rows), rows, color_type=2, filter_types=[0, 1, 2, 3, 4]
        )
        full = unfilter(raw, width, len(rows), channels)
        self.assertEqual(full, b"".join(rows))
        for cols in range(1, width + 1):
            with self.subTest(cols=cols):
                expected = b"".join(
                    full[row * width * channels : row * width * channels + cols * channels]
                    for row in range(len(rows))
                )
                self.assertEqual(
                    unfilter(
                        raw, width, len(rows), channels, max_cols=cols
                    ),
                    expected,
                )

    def test_a_column_bound_above_the_width_decodes_every_column(self):
        raw = bytes([0, 1, 2, 3, 4])
        self.assertEqual(unfilter(raw, 2, 1, 2, max_cols=9), raw[1:])


class TestDropAlpha(unittest.TestCase):
    def test_keeps_each_rows_filter_byte_and_removes_every_alpha_byte(self):
        # Four distinct pixels across two rows, each row with its own filter
        # type, so a dropped filter byte or an off-by-one in a later row's
        # destination offset changes the result rather than passing by
        # coincidence.
        raw = bytes(
            [3, 1, 2, 3, 4, 5, 6, 7, 8, 1, 9, 10, 11, 12, 13, 14, 15, 16]
        )
        self.assertEqual(
            drop_alpha(raw, 2, 2),
            bytes([3, 1, 2, 3, 5, 6, 7, 1, 9, 10, 11, 13, 14, 15]),
        )

    def test_a_column_bound_keeps_only_each_rows_prefix(self):
        # One pixel per row after the filter byte, so a bound that forgot the
        # alpha byte's position or the source stride would return the wrong
        # pixel (or the second row's filter byte) here.
        raw = bytes([3, 1, 2, 3, 4, 5, 6, 7, 8, 1, 9, 10, 11, 12, 13, 14, 15, 16])
        self.assertEqual(
            drop_alpha(raw, 2, 2, max_cols=1), bytes([3, 1, 2, 3, 1, 9, 10, 11])
        )


class TestPaethEqualNeighbours(unittest.TestCase):
    def test_equal_above_and_above_left_predict_the_left_byte(self):
        # When a Paeth row's above and above-left bytes are equal, pa=|b-c|=0
        # wins outright and the predictor is always the left byte -- even when
        # the left byte differs from both. Pin that branch directly: a fast
        # path predicting the above byte (or the above-left one) instead would
        # reconstruct 9 at positions 2 and 3 here rather than 200 and 99.
        raw = bytes([0, 5, 9, 9, 9, 4, 95, 100, 155, 164])
        self.assertEqual(unfilter(raw, 4, 2, 1), bytes([5, 9, 9, 9, 100, 200, 99, 7]))

    def test_equal_neighbours_beside_unequal_ones_decode_both_ways(self):
        # The same real row against an above row whose last byte differs:
        # positions 0, 1 and 3 have b != c and must still take the delta-table
        # branch (predicting 5, 100 and 99), so a fast path that ate every
        # byte would misdecode them.
        raw = bytes([0, 5, 9, 9, 5, 4, 95, 100, 155, 164])
        self.assertEqual(unfilter(raw, 4, 2, 1), bytes([5, 9, 9, 5, 100, 200, 99, 7]))


if __name__ == "__main__":
    unittest.main()
