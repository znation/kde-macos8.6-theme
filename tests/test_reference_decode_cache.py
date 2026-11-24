"""Tests for support/reference_decode_cache.py's cross-process decode cache."""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from unittest import mock

from support import reference_decode_cache
from tools import png
from tools.png.write import encode_png, encode_rgba_png  # noqa: E402


_BLANK_2X2 = bytes(12)


def _read(path, alpha=False, max_rows=None):
    """Decode *path* through the real reader, as a decode callable would."""
    return png.read_png(path, max_rows=max_rows, alpha=alpha)


def _decode_spy():
    """Return ``(decode, calls)``: a decode callable recording its paths."""
    calls = []

    def decode(png_path):
        calls.append(png_path)
        return _read(png_path)

    return decode, calls


def _write_png(directory, name, data, rgba=None):
    """Write a tiny PNG into *directory* and return its path."""
    path = os.path.join(directory, name)
    with open(path, "wb") as handle:
        handle.write(encode_rgba_png(2, 2, rgba) if rgba else encode_png(2, 2, data))
    return path


class _FreshCacheHome:
    """Point the decode cache at a fresh, empty XDG cache home per test."""

    def setUp(self):
        cache_home = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, cache_home, True)
        patcher = mock.patch.dict(os.environ, {"XDG_CACHE_HOME": cache_home})
        patcher.start()
        self.addCleanup(patcher.stop)
        super().setUp()


class TestLoad(_FreshCacheHome, unittest.TestCase):
    """``load`` returns exactly what a fresh decode of the shape produces."""

    def test_a_second_load_serves_the_planes_without_decoding(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_png(tmp, "reference.png", _BLANK_2X2)
            decode, first_calls = _decode_spy()
            first = reference_decode_cache.load(path, alpha=False,
                                                max_rows=None, max_cols=None,
                                                decode=lambda: decode(path))
            self.assertEqual(1, len(first_calls))
            decode, second_calls = _decode_spy()
            second = reference_decode_cache.load(path, alpha=False,
                                                 max_rows=None, max_cols=None,
                                                 decode=lambda: decode(path))
            self.assertEqual([], second_calls)
        self.assertEqual(first.rgb, second.rgb)
        self.assertEqual(first.alpha, second.alpha)
        self.assertEqual((first.width, first.height), (second.width, second.height))
        self.assertIsNone(second.alpha)

    def test_an_alpha_decode_is_served_with_its_alpha_plane(self):
        rgba = b"".join(bytes((value, value, value, 40 + value))
                        for value in range(4))
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_png(tmp, "reference-rgba.png", None, rgba)
            first = reference_decode_cache.load(path, alpha=True,
                                                max_rows=None, max_cols=None,
                                                decode=lambda: _read(path, True))
            second = reference_decode_cache.load(path, alpha=True,
                                                 max_rows=None, max_cols=None,
                                                 decode=lambda: _read(path, True))
        self.assertIsNotNone(second.alpha)
        self.assertEqual(first.alpha, second.alpha)
        self.assertEqual(4, len(second.alpha))
        self.assertEqual(png.pixel_at(first, 1, 1), png.pixel_at(second, 1, 1))

    def test_each_shape_gets_its_own_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_png(tmp, "reference.png", _BLANK_2X2)
            one = reference_decode_cache.load(
                path, alpha=False, max_rows=1, max_cols=None,
                decode=lambda: _read(path, max_rows=1))
            two = reference_decode_cache.load(
                path, alpha=False, max_rows=2, max_cols=None,
                decode=lambda: _read(path, max_rows=2))
            # The third load repeats the first shape, so the entry written
            # for it serves the planes without a third decode.
            decode, calls = _decode_spy()
            three = reference_decode_cache.load(
                path, alpha=False, max_rows=1, max_cols=None,
                decode=lambda: decode(path))
        self.assertEqual([], calls)
        self.assertEqual(1, one.height)
        self.assertEqual(2, two.height)
        self.assertEqual(one.rgb, three.rgb)


class TestKey(_FreshCacheHome, unittest.TestCase):
    """The entry key is the PNG's content, not its path."""

    def test_changed_content_redecodes_the_same_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_png(tmp, "reference.png", _BLANK_2X2)
            decode, calls = _decode_spy()
            reference_decode_cache.load(path, alpha=False, max_rows=None,
                                        max_cols=None,
                                        decode=lambda: decode(path))
            with open(path, "wb") as handle:
                handle.write(encode_png(3, 2, bytes(18)))
            reference_decode_cache.load(path, alpha=False, max_rows=None,
                                        max_cols=None,
                                        decode=lambda: decode(path))
        self.assertEqual(2, len(calls))

    def test_the_same_content_at_another_path_is_a_hit(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_png(tmp, "reference.png", _BLANK_2X2)
            twin = _write_png(tmp, "twin.png", _BLANK_2X2)
            reference_decode_cache.load(path, alpha=False, max_rows=None,
                                        max_cols=None,
                                        decode=lambda: _read(path, False))
            decode, calls = _decode_spy()
            served = reference_decode_cache.load(twin, alpha=False,
                                                 max_rows=None, max_cols=None,
                                                 decode=lambda: decode(twin))
        self.assertEqual([], calls)
        self.assertEqual((2, 2), (served.width, served.height))


class TestBadStates(_FreshCacheHome, unittest.TestCase):
    """A broken cache can only cost a decode, never change the answer."""

    def test_a_corrupt_entry_falls_back_to_a_fresh_decode(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_png(tmp, "reference.png", _BLANK_2X2)
            reference_decode_cache.load(path, alpha=False, max_rows=None,
                                        max_cols=None,
                                        decode=lambda: _read(path, False))
            directory = reference_decode_cache.cache_dir()
            (entry,) = os.listdir(directory)
            with open(os.path.join(directory, entry), "wb") as handle:
                handle.write(b"KREFDC01garbage-not-planes")
            decode, calls = _decode_spy()
            served = reference_decode_cache.load(path, alpha=False,
                                                 max_rows=None, max_cols=None,
                                                 decode=lambda: decode(path))
        self.assertEqual(1, len(calls))
        self.assertEqual((2, 2), (served.width, served.height))

    def test_an_unwritable_cache_home_still_returns_the_decode(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = os.path.join(tmp, "not-a-directory")
            with open(home, "wb") as handle:
                handle.write(b"")
            with mock.patch.dict(os.environ, {"XDG_CACHE_HOME": home}):
                path = _write_png(tmp, "reference.png", _BLANK_2X2)
                decode, calls = _decode_spy()
                served = reference_decode_cache.load(path, alpha=False,
                                                     max_rows=None,
                                                     max_cols=None,
                                                     decode=lambda: decode(path))
        self.assertEqual(1, len(calls))
        self.assertEqual((2, 2), (served.width, served.height))

    def test_an_unreadable_file_falls_back_to_the_decode(self):
        # A path whose content cannot be hashed (here: a missing file) must
        # still reach the decode, whose PngError names the problem.
        from tools import png

        missing = os.path.join(tempfile.gettempdir(), "no-such-reference.png")
        with self.assertRaises(png.PngError):
            reference_decode_cache.load(missing, alpha=False, max_rows=None,
                                        max_cols=None,
                                        decode=lambda: _read(missing, False))

    def test_entries_past_the_max_age_are_pruned_on_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_png(tmp, "reference.png", _BLANK_2X2)
            reference_decode_cache.load(path, alpha=False, max_rows=None,
                                        max_cols=None,
                                        decode=lambda: _read(path, False))
            directory = reference_decode_cache.cache_dir()
            (entry,) = os.listdir(directory)
            stale = os.path.join(directory, entry)
            old = os.path.getmtime(stale) - 31 * 24 * 60 * 60
            os.utime(stale, (old, old))
            other = os.path.join(tmp, "other.png")
            with open(other, "wb") as handle:
                handle.write(encode_png(3, 2, bytes(18)))
            reference_decode_cache.load(other, alpha=False, max_rows=None,
                                        max_cols=None,
                                        decode=lambda: _read(other, False))
        self.assertFalse(os.path.exists(stale))


if __name__ == "__main__":
    unittest.main()
