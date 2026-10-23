"""Validate the icon theme package's Platinum Xcursor pointer set.

The cursors are our own Platinum-style drawings (no reference screenshot shows
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
CANONICAL = ("left_ptr", "xterm", "hand2", "watch", "fleur")
ALIASES = {
    "left_ptr": ("arrow", "default", "top_left_arrow"),
    "xterm": ("text", "ibeam"),
    "hand2": ("hand1", "pointer", "pointing_hand"),
    "watch": ("wait",),
    "fleur": ("move", "all-scroll", "size_all"),
}
CURSOR_FILES = tuple(
    name for canonical in CANONICAL for name in (canonical, *ALIASES[canonical])
)
HOTSPOTS = {
    "left_ptr": {16: (1, 1), 24: (2, 2), 32: (2, 2)},
    "xterm": {16: (7, 7), 24: (11, 11), 32: (14, 14)},
    "hand2": {16: (7, 2), 24: (11, 3), 32: (14, 4)},
    "watch": {16: (7, 5), 24: (11, 8), 32: (14, 10)},
    "fleur": {16: (7, 7), 24: (11, 11), 32: (14, 14)},
}
# A grid pixel that must be black (the face) and one that must be white (the
# outline) at the same place in every nominal size.
PINNED_PIXELS = {
    "left_ptr": {"face": (1, 1), "outline": (0, 0)},
    "xterm": {"face": (7, 7), "outline": (6, 7)},
    "hand2": {"face": (7, 2), "outline": (7, 1)},
    "watch": {"face": (7, 5), "outline": (6, 5)},
    "fleur": {"face": (7, 7), "outline": (7, 0)},
}
# The arrow's top-left corner is its white outline pixel; the other cursors
# leave all four corners transparent.
TRANSPARENT_CORNER_CURSORS = ("xterm", "hand2", "watch", "fleur")
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
TRANSPARENT = (0, 0, 0, 0)


def _pixel(rgba, width, x, y):
    """Return pixel (*x*, *y*) of packed *rgba* as an RGBA tuple."""
    start = (y * width + x) * 4
    return tuple(rgba[start : start + 4])


def _scaled(x, y, size):
    """Return grid pixel (*x*, *y*) at the first destination pixel it covers."""
    return ((x * size + 15) // 16, (y * size + 15) // 16)


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
                self.assertEqual(hotspot, HOTSPOTS["left_ptr"][image.nominal_size])
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
        for name in ALIASES["left_ptr"]:
            with self.subTest(name=name):
                self.assertEqual((CURSORS / name).read_bytes(), expected)

    def test_committed_artifact_is_a_fresh_generator_result(self):
        self.assertEqual(LEFT_PTR.read_bytes(), make_cursors.cursor_bytes())

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


class TestCursorSet(unittest.TestCase):
    """Pin every canonical pointer, its aliases and the generator's output."""

    def test_every_cursor_parses_to_three_chunks_at_the_nominal_sizes(self):
        for name in CANONICAL:
            cursor = _read_cursor(CURSORS / name)
            with self.subTest(name=name):
                self.assertEqual(
                    tuple(image.nominal_size for image in cursor.images), SIZES
                )

    def test_every_frame_pins_its_hotspot_face_and_outline(self):
        for name in CANONICAL:
            cursor = _read_cursor(CURSORS / name)
            face = PINNED_PIXELS[name]["face"]
            outline = PINNED_PIXELS[name]["outline"]
            for image in cursor.images:
                size = image.nominal_size
                with self.subTest(name=name, size=size):
                    width, _, rgba = decode_rgba(image.png)
                    self.assertEqual(
                        (image.hotspot_x, image.hotspot_y),
                        HOTSPOTS[name][size],
                    )
                    self.assertEqual(
                        _pixel(rgba, width, *_scaled(*face, size)), BLACK
                    )
                    self.assertEqual(
                        _pixel(rgba, width, *_scaled(*outline, size)), WHITE
                    )

    def test_each_new_cursor_has_transparent_corners(self):
        for name in TRANSPARENT_CORNER_CURSORS:
            cursor = _read_cursor(CURSORS / name)
            for image in cursor.images:
                width, height, rgba = decode_rgba(image.png)
                with self.subTest(name=name, size=image.nominal_size):
                    for x, y in (
                        (0, 0),
                        (width - 1, 0),
                        (0, height - 1),
                        (width - 1, height - 1),
                    ):
                        self.assertEqual(_pixel(rgba, width, x, y), TRANSPARENT)

    def test_every_alias_is_byte_identical_to_its_canonical(self):
        for name in CANONICAL:
            expected = (CURSORS / name).read_bytes()
            for alias in ALIASES[name]:
                with self.subTest(name=name, alias=alias):
                    self.assertEqual((CURSORS / alias).read_bytes(), expected)

    def test_every_committed_cursor_is_a_fresh_generator_result(self):
        for canonical, rows, hotspot, aliases in make_cursors.CURSORS:
            expected = make_cursors.cursor_bytes(
                rows=rows, hotspot=hotspot, name=canonical
            )
            for name in (canonical, *aliases):
                with self.subTest(name=name):
                    self.assertEqual((CURSORS / name).read_bytes(), expected)

    def test_each_new_grid_differs_from_the_arrow_grid(self):
        for name, rows, _, _ in make_cursors.CURSORS[1:]:
            with self.subTest(name=name):
                self.assertNotEqual(rows, make_cursors.ARROW_GRID)

    def test_generator_writes_every_file_deterministically_in_a_temp_directory(self):
        tmp = make_tmp_dir(self)
        with mock.patch.object(make_cursors, "ROOT", tmp):
            self.assertEqual(make_cursors.main([]), 0)
            directory = tmp / make_cursors.PACKAGE_DIR / make_cursors.CURSORS_DIR
            self.assertEqual(
                sorted(path.name for path in directory.iterdir()),
                sorted(CURSOR_FILES),
            )
            first = {
                name: (directory / name).read_bytes() for name in CURSOR_FILES
            }
            self.assertEqual(make_cursors.main([]), 0)
            second = {
                name: (directory / name).read_bytes() for name in CURSOR_FILES
            }
        self.assertEqual(first, second)
        for name, data in first.items():
            with self.subTest(name=name):
                self.assertEqual(data, (CURSORS / name).read_bytes())

    def test_a_corrupted_grid_dropped_size_or_moved_hotspot_changes_each_glyph(self):
        for canonical, rows, hotspot, _ in make_cursors.CURSORS:
            committed = (CURSORS / canonical).read_bytes()
            mutated = list(rows)
            y = next(index for index, row in enumerate(mutated) if "#" in row)
            x = mutated[y].index("#")
            mutated[y] = mutated[y][:x] + "." + mutated[y][x + 1 :]
            variants = {
                "corrupted grid": make_cursors.cursor_bytes(
                    rows=tuple(mutated), hotspot=hotspot, name=canonical
                ),
                "dropped size": make_cursors.cursor_bytes(
                    rows=rows,
                    sizes=(16, 24),
                    hotspot=hotspot,
                    name=canonical,
                ),
                "moved hotspot": make_cursors.cursor_bytes(
                    rows=rows,
                    hotspot=(hotspot[0] + 1, hotspot[1]),
                    name=canonical,
                ),
            }
            for variant, data in variants.items():
                with self.subTest(glyph=canonical, variant=variant):
                    self.assertNotEqual(data, committed)

    def test_an_unknown_cell_names_the_glyph(self):
        for canonical, rows, hotspot, _ in make_cursors.CURSORS:
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


class TestGridValidation(unittest.TestCase):
    """The grid checks turn a bad contributor edit into a named ValueError."""

    def test_refuses_a_grid_with_the_wrong_row_count(self):
        for name, rows, _, _ in make_cursors.CURSORS:
            with self.subTest(name=name):
                with self.assertRaises(ValueError) as caught:
                    make_cursors._checked_rows(rows[:-1], name)
                self.assertIn(
                    f"the {name} grid must have 16 rows, not 15",
                    str(caught.exception),
                )

    def test_refuses_a_row_that_is_not_a_grid_width_string(self):
        for name, rows, _, _ in make_cursors.CURSORS:
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


class TestGeneratorValidation(unittest.TestCase):
    """Pin the size and hotspot refusals ``cursor_bytes`` builds on."""

    def test_render_rgba_refuses_a_size_that_is_not_a_positive_integer(self):
        for size in (0, -1, True, 1.5):
            with self.subTest(size=size):
                with self.assertRaises(ValueError) as caught:
                    make_cursors.render_rgba(make_cursors.ARROW_GRID, size)
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


if __name__ == "__main__":
    unittest.main()
