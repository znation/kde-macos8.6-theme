"""Tests for ``tools/make_cursors.py``'s generator and command entry point.

These pin the grid and size refusals ``cursor_bytes`` builds on, the cache's
documented bounds and canonicalization, and ``main``'s failure reporting. The
committed pointer package those builders produce stays in
``tests/test_cursors_theme.py``, where ``TestCursorArtifact`` and
``TestCursorSet`` validate it.
"""

from __future__ import annotations

import contextlib
import dataclasses
import io
import os
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import xcursor as xcursor_reader  # noqa: E402
from support.tmp_dir import make_tmp_dir  # noqa: E402
from tools import cursor_art, cursor_art_pointers, make_cursors  # noqa: E402
from tools.cursor_vector import VectorCursor  # noqa: E402
from tools.png import decode_rgba  # noqa: E402

SIZES = (16, 24, 32)


def _grid_cursors():
    """Yield the ``CURSORS`` entries drawn as pixel grids.

    The grid checks (row count, row width, cell glyphs) do not apply to the
    arrow's ``VectorCursor`` art, which TestVectorArrow and the committed-file
    checks cover instead.
    """
    for entry in cursor_art.CURSORS:
        if not isinstance(entry[1], VectorCursor):
            yield entry


class TestGridValidation(unittest.TestCase):
    """The grid checks turn a bad contributor edit into a named ValueError."""

    def test_refuses_a_grid_with_the_wrong_row_count(self):
        for name, rows, _, _ in _grid_cursors():
            with self.subTest(name=name):
                with self.assertRaises(ValueError) as caught:
                    make_cursors._checked_rows(rows[:-1], name)
                self.assertIn(
                    f"the {name} grid must have 16 rows, not 15",
                    str(caught.exception),
                )

    def test_refuses_a_row_that_is_not_a_grid_width_string(self):
        for name, rows, _, _ in _grid_cursors():
            short = list(rows)
            short[0] = short[0][:-1]
            non_text = list(rows)
            non_text[0] = 1
            for rows, width in ((short, "15"), (non_text, "int")):
                with self.subTest(name=name, width=width):
                    self._assert_row_refused(name, rows, width)

    def _assert_row_refused(self, name, rows, width):
        """Pin a malformed first row's ValueError naming *width*."""
        with self.assertRaises(ValueError) as caught:
            make_cursors._checked_rows(rows, name)
        self.assertIn(
            f"{name} grid row 0 must be a 16-character string, "
            f"not {width}",
            str(caught.exception),
        )

    def test_generator_refuses_a_grid_with_an_unknown_cell(self):
        rows = list(cursor_art.ARROW_GRID)
        rows[3] = "x" + rows[3][1:]
        with self.assertRaises(ValueError) as caught:
            make_cursors.cursor_bytes(
                rows=tuple(rows), hotspot=cursor_art.HOTSPOT
            )
        self.assertIn("(0, 3)", str(caught.exception))

    def test_an_unknown_cell_names_the_glyph(self):
        for canonical, rows, hotspot, _ in _grid_cursors():
            mutated = list(rows)
            mutated[0] = "x" + mutated[0][1:]
            with self.subTest(name=canonical):
                with self.assertRaises(ValueError) as caught:
                    make_cursors.cursor_bytes(
                        rows=tuple(mutated), hotspot=hotspot, name=canonical
                    )
                self.assertIn(
                    f"{canonical} grid cell (0, 0)", str(caught.exception)
                )


class TestGeneratorValidation(unittest.TestCase):
    """Pin the size and hotspot refusals ``cursor_bytes`` builds on."""

    def test_render_rgba_refuses_a_size_that_is_not_a_positive_integer(self):
        for size in (0, -1, True, 1.5):
            with self.subTest(size=size):
                with self.assertRaises(ValueError) as caught:
                    make_cursors.render_rgba(cursor_art.ARROW_GRID, size)
                self.assertIn(
                    f"size must be a positive integer: size={size!r}",
                    str(caught.exception),
                )

    def test_scaled_hotspot_refuses_one_that_is_not_two_integers(self):
        for hotspot in ((1,), (1, 2, 3), ("a", 1), (1.5, 1)):
            with self.subTest(hotspot=hotspot):
                with self.assertRaises(ValueError) as caught:
                    make_cursors._scaled_hotspot(16, hotspot)
                self.assertIn(
                    f"hotspot must be two integers: hotspot={hotspot!r}",
                    str(caught.exception),
                )

    def test_scaled_hotspot_refuses_one_outside_the_grid(self):
        for hotspot in ((-1, 1), (16, 1), (1, -1), (1, 16)):
            with self.subTest(hotspot=hotspot):
                with self.assertRaises(ValueError) as caught:
                    make_cursors._scaled_hotspot(16, hotspot)
                self.assertIn(
                    f"hotspot {hotspot} lies outside the 16x16 grid",
                    str(caught.exception),
                )

    def test_cursor_bytes_refuses_a_bad_nominal_size(self):
        for sizes in ((0,), (True,)):
            with self.subTest(sizes=sizes):
                with self.assertRaises(ValueError) as caught:
                    make_cursors.cursor_bytes(sizes=sizes)
                self.assertIn(
                    f"nominal size must be a positive integer: size={sizes[0]!r}",
                    str(caught.exception),
                )

    def test_cursor_bytes_requires_at_least_one_size(self):
        with self.assertRaises(ValueError) as caught:
            make_cursors.cursor_bytes(sizes=())
        self.assertIn("at least one nominal size is required", str(caught.exception))

    def test_cursor_bytes_names_a_non_iterable_sizes_argument(self):
        with self.assertRaises(ValueError) as caught:
            make_cursors.cursor_bytes(sizes=None)
        self.assertIn(
            "nominal sizes must be an iterable, not NoneType",
            str(caught.exception),
        )

    def test_a_nominal_size_above_the_xcursor_frame_limit_is_refused(self):
        # 0x7FFF is the Xcursor image-dimension limit the writer enforces; the
        # generator must refuse it before render_rgba allocates size * size * 4
        # bytes.
        with self.assertRaises(ValueError) as caught:
            make_cursors._checked_sizes((0x8000,))
        self.assertIn(
            "nominal size must be at most 32767 (the Xcursor frame limit): "
            "size=32768",
            str(caught.exception),
        )

    def test_render_rgba_refuses_a_size_above_the_xcursor_frame_limit(self):
        with self.assertRaises(ValueError) as caught:
            make_cursors.render_rgba(cursor_art.ARROW_GRID, 0x8000)
        self.assertIn(
            "size must be at most 32767 (the Xcursor frame limit): "
            "size=32768",
            str(caught.exception),
        )

    def test_a_size_below_the_grid_keeps_its_hotspot_inside_the_frame(self):
        # Below the grid the downscale skips source pixel 15, so its ceiling
        # lands on ``size`` and must be clamped to ``size - 1``, the last
        # rendered pixel.
        for size, expected in ((1, 0), (8, 7), (15, 14)):
            with self.subTest(size=size):
                data = make_cursors.cursor_bytes(
                    rows=cursor_art.ARROW_GRID, sizes=(size,), hotspot=(15, 15)
                )
                path = make_tmp_dir(self) / f"arrow-{size}"
                path.write_bytes(data)
                images = xcursor_reader.read_cursor(path).images
                self.assertEqual(len(images), 1)
                self.assertEqual(images[0].nominal_size, size)
                self.assertEqual(
                    (images[0].hotspot_x, images[0].hotspot_y),
                    (expected, expected),
                )

    def test_a_size_below_the_grid_maps_each_hotspot_to_its_first_covered_pixel(
        self,
    ):
        # Nearest-neighbour sends destination pixel ``d`` to source
        # ``d * 16 // size``, so at a size below the grid some source rows and
        # columns are skipped. The hotspot must round up to the first
        # destination pixel whose source is at or past the grid hotspot -- not
        # down, which would name a pixel before it -- and only a hotspot no
        # destination reaches clamps to the last rendered pixel. Pinning the
        # symmetric (15, 15) case alone cannot tell a ceiling from a floor.
        tmp = make_tmp_dir(self)
        for size in (5, 8, 15):
            reached = tuple(
                destination * make_cursors.GRID_SIZE // size
                for destination in range(size)
            )
            for hotspot in ((0, 0), (1, 14), (7, 8), (14, 15), (15, 15)):
                with self.subTest(size=size, hotspot=hotspot):
                    expected = tuple(
                        next(
                            (
                                destination
                                for destination, source in enumerate(reached)
                                if source >= coordinate
                            ),
                            size - 1,
                        )
                        for coordinate in hotspot
                    )
                    path = tmp / f"arrow-{size}-{hotspot[0]}-{hotspot[1]}"
                    path.write_bytes(
                        make_cursors.cursor_bytes(
                            rows=cursor_art.ARROW_GRID, sizes=(size,), hotspot=hotspot
                        )
                    )
                    image = xcursor_reader.read_cursor(path).images[0]
                    self.assertEqual(image.nominal_size, size)
                    self.assertEqual(
                        (image.hotspot_x, image.hotspot_y), expected
                    )


class TestMainErrors(unittest.TestCase):
    """``main`` must report a creation or write failure and stop, exiting 2."""

    def _run_main_refused_before_render(self, tmp):
        """Run ``main`` rooted at *tmp*, forbidding any render; return (status, stderr)."""
        stderr = io.StringIO()
        with mock.patch.object(make_cursors, "ROOT", tmp), mock.patch.object(
            make_cursors, "cursor_bytes",
            side_effect=AssertionError("rendered before destination was accepted"),
        ):
            with contextlib.redirect_stderr(stderr):
                status = make_cursors.main([])
        return status, stderr.getvalue()

    def test_reports_a_cursors_path_that_is_a_file(self):
        tmp = make_tmp_dir(self)
        blocked = tmp / make_cursors.PACKAGE_DIR / make_cursors.CURSORS_DIR
        blocked.parent.mkdir(parents=True)
        blocked.write_text("occupied", encoding="utf-8")
        status, stderr = self._run_main_refused_before_render(tmp)
        self.assertEqual(status, 2)
        self.assertIn(f"cannot create {blocked}", stderr)
        self.assertEqual("occupied", blocked.read_text(encoding="utf-8"))

    def test_generator_refuses_a_cursors_directory_that_escapes_the_repository(self):
        tmp = make_tmp_dir(self)
        outside = make_tmp_dir(self)
        directory = tmp / make_cursors.PACKAGE_DIR / make_cursors.CURSORS_DIR
        directory.parent.mkdir(parents=True)
        os.symlink(outside, directory)
        status, stderr = self._run_main_refused_before_render(tmp)
        self.assertEqual(status, 2)
        self.assertIn(str(directory), stderr)
        self.assertEqual(list(outside.iterdir()), [])

    def test_reports_a_failed_write_and_stops_at_that_cursor(self):
        tmp = make_tmp_dir(self)
        directory = tmp / make_cursors.PACKAGE_DIR / make_cursors.CURSORS_DIR
        real_write = make_cursors.write_bytes_atomically
        attempted = []

        def flaky_write(path, data):
            attempted.append(path.name)
            if path.name == "arrow":
                raise OSError("simulated failure")
            real_write(path, data)

        stderr = io.StringIO()
        with mock.patch.object(make_cursors, "ROOT", tmp):
            with mock.patch.object(
                make_cursors, "write_bytes_atomically", flaky_write
            ):
                with contextlib.redirect_stderr(stderr):
                    status = make_cursors.main([])
        self.assertEqual(status, 2)
        self.assertIn(
            f"cannot write {directory / 'arrow'}: simulated failure",
            stderr.getvalue(),
        )
        self.assertEqual(["left_ptr", "arrow"], attempted)
        self.assertEqual(
            ["left_ptr"], sorted(path.name for path in directory.iterdir())
        )


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
            with self.assertRaises(ValueError) as caught:
                make_cursors.cursor_bytes(
                rows=tuple(rows), hotspot=cursor_art.HOTSPOT
            )
            self.assertIn("(0, 3)", str(caught.exception))

    def test_a_bad_size_is_refused_after_a_cached_build(self):
        make_cursors.cursor_bytes(
            rows=cursor_art.ARROW_GRID, hotspot=cursor_art.HOTSPOT
        )
        for sizes in ((16.0, 24.0, 32.0), (True,), ([16], 24, 32)):
            with self.subTest(sizes=sizes):
                with self.assertRaises(ValueError) as caught:
                    make_cursors.cursor_bytes(sizes=sizes)
                self.assertIn(
                    "nominal size must be a positive integer",
                    str(caught.exception),
                )

    def test_a_bad_hotspot_is_refused_after_a_cached_build(self):
        make_cursors.cursor_bytes(
            rows=cursor_art.ARROW_GRID, hotspot=cursor_art.HOTSPOT
        )
        for hotspot in ((1.0, 1.0), (True, True), ([1], 1)):
            with self.subTest(hotspot=hotspot):
                with self.assertRaises(ValueError) as caught:
                    make_cursors.cursor_bytes(
                        rows=cursor_art.ARROW_GRID, hotspot=hotspot
                    )
                self.assertIn(
                    "hotspot must be two integers", str(caught.exception)
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
                    with self.assertRaises(ValueError) as caught:
                        make_cursors.cursor_bytes(rows=self.art, hotspot=hotspot)
                    self.assertIn("hotspot", str(caught.exception))

    def test_rows_that_are_neither_a_grid_nor_vector_art_are_refused(self):
        with self.assertRaises(ValueError):
            make_cursors.cursor_bytes(rows=5)


if __name__ == "__main__":
    unittest.main()
