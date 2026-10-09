"""Tests for tools/png_filters.py's scanline-filter internals -- the Sub/Up
lane arithmetic and the Paeth delta table.

The Sub/Up round-trip below decodes through ``tools/png.py``, which imports
these primitives; the lane and table helpers themselves live in
``tools/png_filters.py``.

Run with the project's check harness (stdlib unittest):
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import random
import unittest
from unittest import mock

import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools import png
from tools import png_filters
from error_assertions import assert_rejects_unequal_lengths  # noqa: E402
from png_fixtures import _paeth, make_png, rgb_from_rows  # noqa: E402


class TestUnfilterLanes(unittest.TestCase):
    """The Sub and Up scanline filters reconstruct rows with big-integer lane
    operations; pin those against a per-byte oracle and an encode/decode
    round-trip so a carry or a truncated scan step cannot slip through."""

    def test_byte_add_matches_oracle(self):
        rng = random.Random(0x86)
        for length in (0, 1, 2, 3, 7, 8, 255, 256, 1024):
            with self.subTest(length=length):
                a = bytes(rng.randrange(256) for _ in range(length))
                b = bytes(rng.randrange(256) for _ in range(length))
                expected = bytes((x + y) & 0xFF for x, y in zip(a, b))
                self.assertEqual(png_filters._byte_add(a, b), expected)

    def test_byte_add_unequal_lengths_raise(self):
        assert_rejects_unequal_lengths(self, png_filters._byte_add)

    def test_byte_add_wraps_without_carrying_between_bytes(self):
        # 0xFF + 0x01 must wrap to 0x00 without carrying into the next byte;
        # a leaked carry would turn the following byte into 0x01 instead.
        self.assertEqual(
            png_filters._byte_add(bytes([0xFF, 0x00, 0xFF]), bytes([0x01, 0x00, 0x01])),
            bytes([0x00, 0x00, 0x00]),
        )

    def test_prefix_sum_matches_oracle(self):
        rng = random.Random(0x1999)
        for length in (0, 1, 2, 3, 7, 8, 100, 255, 256, 1024):
            with self.subTest(length=length):
                channel = bytes(rng.randrange(256) for _ in range(length))
                out = bytearray(channel)
                for i in range(1, len(out)):
                    out[i] = (out[i] + out[i - 1]) & 0xFF
                self.assertEqual(png_filters._prefix_sum(channel), bytes(out))

    def test_sub_and_up_filters_roundtrip_random_rows(self):
        # Encode random rows using only Sub and Up filters and decode them
        # back; any per-byte carry or truncated scan step shows up as a
        # mismatched pixel. Widths include 1 so the scan length is 1.
        rng = random.Random(0x8_6)
        for width, color_type in (
            (1, 0),
            (2, 2),
            (3, 2),
            (5, 2),
            (3, 4),
            (4, 6),
            (9, 6),
        ):
            channels = {0: 1, 2: 3, 4: 2, 6: 4}[color_type]
            rows = [
                bytes(rng.randrange(256) for _ in range(width * channels))
                for _ in range(6)
            ]
            data = make_png(
                width,
                len(rows),
                rows,
                color_type=color_type,
                filter_types=[1, 2, 1, 2, 1, 2],
            )
            expected = rgb_from_rows(rows, color_type)
            with self.subTest(width=width, color_type=color_type):
                self.assertEqual(png.decode_png(data).rgb, expected)


class TestPaethDeltaTable(unittest.TestCase):
    """The Paeth delta table is filled from a closed-form block layout rather
    than a predictor call per cell; pin every cell against the per-entry
    predictor so a wrong block boundary cannot decode a row to a plausible but
    wrong value."""

    def test_table_matches_per_entry_oracle(self):
        expected = bytearray(511 * 512)
        for da in range(-255, 256):
            base = (da + 255) << 9
            for db in range(-255, 256):
                expected[base + db + 255] = _paeth(da, db, 0) & 0xFF
        # The table is memoized in a module global; clear it so this call
        # rebuilds it, and `patch.object` restores the original afterwards.
        with mock.patch.object(png_filters, "_PAETH_DELTA", None):
            table = png_filters._paeth_delta_table()
        self.assertEqual(table, bytes(expected))

    def test_table_is_built_once_and_reused(self):
        with mock.patch.object(png_filters, "_PAETH_DELTA", None):
            first = png_filters._paeth_delta_table()
            self.assertIs(png_filters._paeth_delta_table(), first)
