"""Tests for ``tools/make_cursors.py``'s generator and command entry point.

These pin the grid and size refusals ``cursor_bytes`` builds on, the cache's
documented bounds and canonicalization, and ``main``'s failure reporting. The
committed pointer package those builders produce stays in
``tests/test_cursors_theme.py``, where ``TestCursorArtifact`` and
``TestCursorSet`` validate it.
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
from tools import cursor_art, make_cursors  # noqa: E402

SIZES = (16, 24, 32)


class TestGridValidation(unittest.TestCase):
    """The grid checks turn a bad contributor edit into a named ValueError."""

    def test_refuses_a_grid_with_the_wrong_row_count(self):
        for name, rows, _, _ in cursor_art.CURSORS:
            with self.subTest(name=name):
                with self.assertRaises(ValueError) as caught:
                    make_cursors._checked_rows(rows[:-1], name)
                self.assertIn(
                    f"the {name} grid must have 16 rows, not 15",
                    str(caught.exception),
                )

    def test_refuses_a_row_that_is_not_a_grid_width_string(self):
        for name, rows, _, _ in cursor_art.CURSORS:
            short = list(rows)
            short[0] = short[0][:-1]
            non_text = list(rows)
            non_text[0] = 1
            for rows, width in ((short, "15"), (non_text, "int")):
                with self.subTest(name=name, width=width):
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
            make_cursors.cursor_bytes(rows=tuple(rows))
        self.assertIn("(0, 3)", str(caught.exception))

    def test_an_unknown_cell_names_the_glyph(self):
        for canonical, rows, hotspot, _ in cursor_art.CURSORS:
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
                    sizes=(size,), hotspot=(15, 15)
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
                            sizes=(size,), hotspot=hotspot
                        )
                    )
                    image = xcursor_reader.read_cursor(path).images[0]
                    self.assertEqual(image.nominal_size, size)
                    self.assertEqual(
                        (image.hotspot_x, image.hotspot_y), expected
                    )


class TestMainErrors(unittest.TestCase):
    """``main`` must report a creation or write failure and stop, exiting 2."""

    def test_reports_a_cursors_path_that_is_a_file(self):
        tmp = make_tmp_dir(self)
        blocked = tmp / make_cursors.PACKAGE_DIR / make_cursors.CURSORS_DIR
        blocked.parent.mkdir(parents=True)
        blocked.write_text("occupied", encoding="utf-8")
        stderr = io.StringIO()
        with mock.patch.object(make_cursors, "ROOT", tmp):
            with contextlib.redirect_stderr(stderr):
                status = make_cursors.main([])
        self.assertEqual(status, 2)
        self.assertIn(f"cannot create {blocked}", stderr.getvalue())
        self.assertEqual("occupied", blocked.read_text(encoding="utf-8"))

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
            first = make_cursors.cursor_bytes()
            second = make_cursors.cursor_bytes()
        self.assertEqual(first, second)
        self.assertEqual(render.call_count, len(SIZES))

    def test_a_different_generation_request_is_built_separately(self):
        with mock.patch.object(
            make_cursors, "render_rgba", wraps=make_cursors.render_rgba
        ) as render:
            default = make_cursors.cursor_bytes()
            moved = make_cursors.cursor_bytes(hotspot=(2, 2))
        self.assertNotEqual(default, moved)
        self.assertEqual(render.call_count, 2 * len(SIZES))

    def test_list_sizes_and_hotspot_are_canonicalized_before_the_lookup(self):
        # ``cursor_bytes`` has always accepted lists for both arguments. The
        # cache key is built from the checked tuples, so a list request must
        # neither raise "unhashable type" nor miss the cached tuple request.
        with mock.patch.object(
            make_cursors, "render_rgba", wraps=make_cursors.render_rgba
        ) as render:
            listed = make_cursors.cursor_bytes(sizes=[16, 24], hotspot=[1, 1])
            tupled = make_cursors.cursor_bytes(sizes=(16, 24), hotspot=(1, 1))
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
                make_cursors.cursor_bytes(rows=tuple(rows))
            self.assertIn("(0, 3)", str(caught.exception))

    def test_a_bad_size_is_refused_after_a_cached_build(self):
        make_cursors.cursor_bytes()
        for sizes in ((16.0, 24.0, 32.0), (True,), ([16], 24, 32)):
            with self.subTest(sizes=sizes):
                with self.assertRaises(ValueError) as caught:
                    make_cursors.cursor_bytes(sizes=sizes)
                self.assertIn(
                    "nominal size must be a positive integer",
                    str(caught.exception),
                )

    def test_a_bad_hotspot_is_refused_after_a_cached_build(self):
        make_cursors.cursor_bytes()
        for hotspot in ((1.0, 1.0), (True, True), ([1], 1)):
            with self.subTest(hotspot=hotspot):
                with self.assertRaises(ValueError) as caught:
                    make_cursors.cursor_bytes(hotspot=hotspot)
                self.assertIn(
                    "hotspot must be two integers", str(caught.exception)
                )


if __name__ == "__main__":
    unittest.main()
