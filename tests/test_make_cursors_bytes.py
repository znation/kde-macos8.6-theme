"""Tests for ``tools/make_cursors.py``'s ``cursor_bytes`` build cache and vector arrow.

These pin the cache's reuse, canonicalization, entry bound and repeated refusals
(``TestCursorBytesCache``) and the arrow's ``VectorCursor`` art rendered at 16, 24
and 32 (``TestVectorArrow``). The grid, hotspot and size refusals and ``main``'s
failure reporting stay in ``tests/test_make_cursors.py``.
"""

from __future__ import annotations

import dataclasses
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import xcursor as xcursor_reader  # noqa: E402
from support.error_assertions import assert_error_names  # noqa: E402
from support.tmp_dir import make_tmp_dir  # noqa: E402
from tools import cursor_art, cursor_art_pointers, make_cursors  # noqa: E402
from tools.png import decode_rgba  # noqa: E402

SIZES = (16, 24, 32)


class TestCursorBytesCache(unittest.TestCase):
    """An unchanged generator request reuses its build; different input does not."""

    def setUp(self):
        make_cursors._cached_cursor_bytes.cache_clear()
        self.addCleanup(make_cursors._cached_cursor_bytes.cache_clear)

    def test_an_unchanged_request_is_built_once(self):
        with mock.patch.object(
            make_cursors, "render_rgba", wraps=make_cursors.render_rgba
        ) as render:
            first = make_cursors.cursor_bytes(
            rows=cursor_art.ARROW_GRID, hotspot=cursor_art.HOTSPOT
        )
            second = make_cursors.cursor_bytes(
            rows=cursor_art.ARROW_GRID, hotspot=cursor_art.HOTSPOT
        )
        self.assertEqual(first, second)
        self.assertEqual(render.call_count, len(SIZES))

    def test_a_different_generation_request_is_built_separately(self):
        with mock.patch.object(
            make_cursors, "render_rgba", wraps=make_cursors.render_rgba
        ) as render:
            default = make_cursors.cursor_bytes(
            rows=cursor_art.ARROW_GRID, hotspot=cursor_art.HOTSPOT
        )
            moved = make_cursors.cursor_bytes(
                rows=cursor_art.ARROW_GRID, hotspot=(2, 2)
            )
        self.assertNotEqual(default, moved)
        self.assertEqual(render.call_count, 2 * len(SIZES))

    def test_list_sizes_and_hotspot_are_canonicalized_before_the_lookup(self):
        # ``cursor_bytes`` has always accepted lists for both arguments. The
        # cache key is built from the checked tuples, so a list request must
        # neither raise "unhashable type" nor miss the cached tuple request.
        with mock.patch.object(
            make_cursors, "render_rgba", wraps=make_cursors.render_rgba
        ) as render:
            listed = make_cursors.cursor_bytes(
                rows=cursor_art.ARROW_GRID, sizes=[16, 24], hotspot=[1, 1]
            )
            tupled = make_cursors.cursor_bytes(
                rows=cursor_art.ARROW_GRID, sizes=(16, 24), hotspot=(1, 1)
            )
        self.assertEqual(listed, tupled)
        self.assertEqual(render.call_count, 2)

    def test_the_cache_keeps_at_most_the_documented_entry_count(self):
        # The module documents an entry-count bound so a caller generating
        # many variants cannot grow the cache without limit. Fill one entry
        # past the bound, then ask for the oldest again: it must have been
        # evicted and rebuilt, while the newest entry is still a hit.
        limit = make_cursors._MAX_CACHED_CURSORS
        with mock.patch.object(
            make_cursors,
            "_build_cursor_bytes",
            wraps=make_cursors._build_cursor_bytes,
        ) as build:
            for index in range(limit + 1):
                make_cursors.cursor_bytes(sizes=(1,), name=f"variant-{index}")
            self.assertEqual(build.call_count, limit + 1)
            make_cursors.cursor_bytes(sizes=(1,), name="variant-0")
            self.assertEqual(build.call_count, limit + 2)
            make_cursors.cursor_bytes(sizes=(1,), name=f"variant-{limit}")
            self.assertEqual(build.call_count, limit + 2)
        info = make_cursors._cached_cursor_bytes.cache_info()
        self.assertEqual(info.maxsize, limit)
        self.assertEqual(info.currsize, limit)

    def test_a_malformed_grid_is_refused_on_every_call(self):
        rows = list(cursor_art.ARROW_GRID)
        rows[3] = "x" + rows[3][1:]
        for _ in range(2):
            assert_error_names(
                self, ValueError, make_cursors.cursor_bytes,
                rows=tuple(rows), hotspot=cursor_art.HOTSPOT,
                needles=("(0, 3)",),
            )

    def test_a_bad_size_is_refused_after_a_cached_build(self):
        make_cursors.cursor_bytes(
            rows=cursor_art.ARROW_GRID, hotspot=cursor_art.HOTSPOT
        )
        for sizes in ((16.0, 24.0, 32.0), (True,), ([16], 24, 32)):
            with self.subTest(sizes=sizes):
                assert_error_names(
                    self, ValueError, make_cursors.cursor_bytes, sizes=sizes,
                    needles=("nominal size must be a positive integer",),
                )

    def test_a_bad_hotspot_is_refused_after_a_cached_build(self):
        make_cursors.cursor_bytes(
            rows=cursor_art.ARROW_GRID, hotspot=cursor_art.HOTSPOT
        )
        for hotspot in ((1.0, 1.0), (True, True), ([1], 1)):
            with self.subTest(hotspot=hotspot):
                assert_error_names(
                    self, ValueError, make_cursors.cursor_bytes,
                    rows=cursor_art.ARROW_GRID, hotspot=hotspot,
                    needles=("hotspot must be two integers",),
                )


class TestVectorArrow(unittest.TestCase):
    """The arrow's ``VectorCursor`` art renders natively at 16, 24 and 32."""

    def setUp(self):
        make_cursors._cached_cursor_bytes.cache_clear()
        self.addCleanup(make_cursors._cached_cursor_bytes.cache_clear)
        self.art = cursor_art_pointers.ARROW_ART
        self.hotspot = cursor_art_pointers.ARROW_HOTSPOT

    def _frames(self, data):
        path = make_tmp_dir(self) / "arrow"
        path.write_bytes(data)
        frames = {}
        for image in xcursor_reader.read_cursor(path).images:
            width, height, rgba = decode_rgba(image.png)
            self.assertEqual((width, height), (image.width, image.height))
            frames[image.nominal_size] = (
                (image.hotspot_x, image.hotspot_y),
                width,
                rgba,
            )
        return frames

    def _pixel(self, rgba, width, x, y):
        start = (y * width + x) * 4
        return tuple(rgba[start : start + 4])

    def test_frames_sit_at_the_nominal_sizes_with_scaled_hotspots(self):
        frames = self._frames(
            make_cursors.cursor_bytes(rows=self.art, hotspot=self.hotspot)
        )
        self.assertEqual(sorted(frames), [16, 24, 32])
        # The design hotspot (3, 3) on a 32-unit grid maps to (1, 1), (2, 2)
        # and (3, 3) at the three sizes.
        self.assertEqual(frames[16][0], (1, 1))
        self.assertEqual(frames[24][0], (2, 2))
        self.assertEqual(frames[32][0], (3, 3))
        for size in SIZES:
            with self.subTest(size=size):
                self.assertEqual(frames[size][1], size)

    def test_the_hotspot_pixel_is_opaque(self):
        frames = self._frames(
            make_cursors.cursor_bytes(rows=self.art, hotspot=self.hotspot)
        )
        for size in SIZES:
            with self.subTest(size=size):
                (hx, hy), width, rgba = frames[size]
                self.assertEqual(self._pixel(rgba, width, hx, hy)[3], 255)

    def test_the_face_interior_is_black_and_the_corners_are_transparent(self):
        frames = self._frames(
            make_cursors.cursor_bytes(rows=self.art, hotspot=self.hotspot)
        )
        # Design point (6, 14) lies inside the face at every size; its pixel
        # is at (6, 14) scaled by size / 32, rounded down.
        for size, (x, y) in ((16, (3, 7)), (24, (4, 10)), (32, (6, 14))):
            with self.subTest(size=size):
                _, width, rgba = frames[size]
                self.assertEqual(self._pixel(rgba, width, x, y), (0, 0, 0, 255))
                self.assertEqual(self._pixel(rgba, width, size - 1, 0), (0, 0, 0, 0))
                self.assertEqual(
                    self._pixel(rgba, width, size - 1, size - 1), (0, 0, 0, 0)
                )

    def test_the_edges_are_antialiased(self):
        frames = self._frames(
            make_cursors.cursor_bytes(rows=self.art, hotspot=self.hotspot)
        )
        for size in SIZES:
            with self.subTest(size=size):
                _, width, rgba = frames[size]
                pixels = [
                    tuple(rgba[i : i + 4]) for i in range(0, len(rgba), 4)
                ]
                self.assertTrue(any(0 < p[3] < 255 for p in pixels))
                self.assertTrue(
                    any(p[3] == 255 and 0 < p[0] < 255 for p in pixels)
                )

    def test_a_moved_face_vertex_a_dropped_size_or_a_moved_hotspot_changes_the_bytes(self):
        baseline = make_cursors.cursor_bytes(
            rows=self.art, hotspot=self.hotspot
        )
        face = list(self.art.face)
        face[6] = (18, 17.5)
        moved_vertex = dataclasses.replace(self.art, face=tuple(face))
        self.assertNotEqual(
            make_cursors.cursor_bytes(rows=moved_vertex, hotspot=self.hotspot),
            baseline,
        )
        self.assertNotEqual(
            make_cursors.cursor_bytes(
                rows=self.art, sizes=(16, 24), hotspot=self.hotspot
            ),
            baseline,
        )
        self.assertNotEqual(
            make_cursors.cursor_bytes(rows=self.art, hotspot=(4, 3)), baseline
        )

    def test_a_hotspot_outside_the_design_grid_is_refused_every_time(self):
        make_cursors.cursor_bytes(rows=self.art, hotspot=self.hotspot)
        for hotspot in ((32, 3), (-1, 3)):
            for _ in range(2):
                with self.subTest(hotspot=hotspot):
                    assert_error_names(
                        self, ValueError, make_cursors.cursor_bytes,
                        rows=self.art, hotspot=hotspot, needles=("hotspot",),
                    )

    def test_a_vector_hotspot_outside_the_design_size_is_refused_every_time(self):
        # Vector hotspots are design units in [0, design_size) = [0, 32) for
        # the arrow, not cells of the 16x16 grid, so the vector check must
        # refuse 32 (and -1) by design_size on every call, cached or not.
        make_cursors.cursor_bytes(rows=self.art, hotspot=self.hotspot)
        for hotspot, needle in (((32, 3), "hotspot x"), ((3, 32), "hotspot y"),
                                ((-1, 3), "hotspot x")):
            for _ in range(2):
                with self.subTest(hotspot=hotspot):
                    assert_error_names(
                        self, ValueError, make_cursors.cursor_bytes,
                        rows=self.art, hotspot=hotspot, needles=(needle,),
                    )

    def test_a_malformed_vector_hotspot_is_refused_after_a_valid_build(self):
        make_cursors.cursor_bytes(rows=self.art, hotspot=self.hotspot)
        for hotspot, needle in (((3,), "hotspot must be an (x, y) pair"),
                                ((3, True), "hotspot y must be a number"),
                                (("3", 3), "hotspot x must be a number")):
            with self.subTest(hotspot=hotspot):
                assert_error_names(
                    self, ValueError, make_cursors.cursor_bytes,
                    rows=self.art, hotspot=hotspot, needles=(needle,),
                )

    def test_rows_that_are_neither_a_grid_nor_vector_art_are_refused(self):
        with self.assertRaises(ValueError):
            make_cursors.cursor_bytes(rows=5)


if __name__ == "__main__":
    unittest.main()
