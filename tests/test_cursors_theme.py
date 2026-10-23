"""Validate the icon theme package's Platinum Xcursor arrow artifact.

The cursor is our own Platinum-style drawing (no reference screenshot shows
the pointer), so these tests pin the Xcursor container, every frame's decoded
pixels, the alias bytes and the generator's deterministic output. The
test-side reader is independent of ``tools/xcursor.py``; see
``tests/support/xcursor.py``.
"""

from __future__ import annotations

import contextlib
import io
import os
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import xcursor as xcursor_reader  # noqa: E402
from support.tmp_dir import make_tmp_dir  # noqa: E402
from tools import make_cursors  # noqa: E402
from tools.png import decode_rgba  # noqa: E402

PACKAGE = make_cursors.ROOT / make_cursors.PACKAGE_DIR
CURSORS = PACKAGE / make_cursors.CURSORS_DIR
LEFT_PTR = CURSORS / "left_ptr"
SIZES = (16, 24, 32)
ALIASES = ("arrow", "default", "top_left_arrow")
CURSOR_FILES = ("left_ptr",) + ALIASES
HOTSPOTS = {16: (1, 1), 24: (2, 2), 32: (2, 2)}


def _pixel(rgba, width, x, y):
    """Return pixel (*x*, *y*) of packed *rgba* as an RGBA tuple."""
    start = (y * width + x) * 4
    return tuple(rgba[start : start + 4])


def _read_cursor(path):
    """Read *path* through the independent test-side reader."""
    return xcursor_reader.read_cursor(path)


class TestCursorArtifact(unittest.TestCase):
    """Pin the committed ``left_ptr`` artifact and its alias bytes."""

    def setUp(self):
        self.cursor = _read_cursor(LEFT_PTR)

    def test_parser_accepts_three_image_chunks_at_the_nominal_sizes(self):
        self.assertEqual(
            tuple(image.nominal_size for image in self.cursor.images), SIZES
        )
        for image in self.cursor.images:
            with self.subTest(size=image.nominal_size):
                self.assertIn(image.nominal_size, SIZES)

    def test_each_chunk_png_decodes_at_its_nominal_size(self):
        for image in self.cursor.images:
            with self.subTest(size=image.nominal_size):
                width, height, rgba = decode_rgba(image.png)
                self.assertEqual((width, height), (image.nominal_size,) * 2)
                self.assertEqual((image.width, image.height), (width, height))
                self.assertEqual(len(rgba), width * height * 4)

    def test_each_frame_pins_the_hotspot_outline_tip_and_transparency(self):
        for image in self.cursor.images:
            with self.subTest(size=image.nominal_size):
                width, height, rgba = decode_rgba(image.png)
                hotspot = (image.hotspot_x, image.hotspot_y)
                self.assertEqual(hotspot, HOTSPOTS[image.nominal_size])
                self.assertEqual(
                    _pixel(rgba, width, 0, 0), (255, 255, 255, 255)
                )
                self.assertEqual(
                    _pixel(rgba, width, *hotspot), (0, 0, 0, 255)
                )
                self.assertEqual(
                    _pixel(rgba, width, width - 1, height - 1),
                    (0, 0, 0, 0),
                )

    def test_aliases_are_byte_identical_to_left_ptr(self):
        expected = LEFT_PTR.read_bytes()
        for name in ALIASES:
            with self.subTest(name=name):
                self.assertEqual((CURSORS / name).read_bytes(), expected)

    def test_committed_artifact_is_a_fresh_generator_result(self):
        self.assertEqual(LEFT_PTR.read_bytes(), make_cursors.cursor_bytes())

    def test_generator_is_deterministic_in_a_temp_directory(self):
        tmp = make_tmp_dir(self)
        with mock.patch.object(make_cursors, "ROOT", tmp):
            self.assertEqual(make_cursors.main([]), 0)
            directory = tmp / make_cursors.PACKAGE_DIR / make_cursors.CURSORS_DIR
            first = {
                name: (directory / name).read_bytes()
                for name in CURSOR_FILES
            }
            self.assertEqual(make_cursors.main([]), 0)
            second = {
                name: (directory / name).read_bytes()
                for name in CURSOR_FILES
            }
        self.assertEqual(first, second)
        for name, data in first.items():
            with self.subTest(name=name):
                self.assertEqual(data, LEFT_PTR.read_bytes())

    def test_a_corrupted_grid_dropped_size_or_moved_hotspot_changes_the_artifact(self):
        rows = list(make_cursors.ARROW_GRID)
        rows[1] = rows[1][0] + "." + rows[1][2:]
        variants = {
            "corrupted grid": make_cursors.cursor_bytes(rows=tuple(rows)),
            "dropped size": make_cursors.cursor_bytes(sizes=(16, 24)),
            "moved hotspot": make_cursors.cursor_bytes(hotspot=(2, 2)),
        }
        expected = LEFT_PTR.read_bytes()
        for name, data in variants.items():
            with self.subTest(variant=name):
                self.assertNotEqual(data, expected)

    def test_reader_rejects_a_truncated_or_corrupted_copy(self):
        tmp = make_tmp_dir(self)
        truncated = tmp / "truncated"
        truncated.write_bytes(LEFT_PTR.read_bytes()[:20])
        corrupted = tmp / "corrupted"
        corrupted.write_bytes(b"Xcur" + b"\xff" * 28)
        for name, path in (("truncated", truncated), ("corrupted", corrupted)):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    _read_cursor(path)

    def test_generator_refuses_a_grid_with_an_unknown_cell(self):
        rows = list(make_cursors.ARROW_GRID)
        rows[3] = "x" + rows[3][1:]
        with self.assertRaises(ValueError) as caught:
            make_cursors.cursor_bytes(rows=tuple(rows))
        self.assertIn("(0, 3)", str(caught.exception))

    def test_generator_refuses_a_cursors_directory_that_escapes_the_repository(self):
        tmp = make_tmp_dir(self)
        outside = make_tmp_dir(self)
        directory = tmp / make_cursors.PACKAGE_DIR / make_cursors.CURSORS_DIR
        directory.parent.mkdir(parents=True)
        os.symlink(outside, directory)
        stderr = io.StringIO()
        with mock.patch.object(make_cursors, "ROOT", tmp):
            with contextlib.redirect_stderr(stderr):
                status = make_cursors.main([])
        self.assertEqual(status, 2)
        self.assertIn(str(directory), stderr.getvalue())
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
