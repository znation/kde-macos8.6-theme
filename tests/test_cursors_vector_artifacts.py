"""Pin the committed I-beam and pointing-hand vector artifacts."""

import unittest

from support.cursor_artifact_cases import (
    BLACK,
    CURSORS,
    HOTSPOTS,
    SIZES,
    TRANSPARENT,
    WHITE,
    _pixel,
    _read_cursor,
)
from tools.png import decode_rgba


class TestVectorPointerArtifacts(unittest.TestCase):
    """Pin the committed I-beam and pointing-hand vector artifacts per size.

    Each design point maps to the pixel that contains it at a nominal size:
    ``floor(coordinate * size / 32)``. The expectations below come from the
    design coordinates in ``tools/cursor_art_pointers.py``, not from the
    rendered output.
    """

    # (name, design points that must be black, design points that must be
    # white). The hotspot is checked separately, as its alpha.
    EXPECTATIONS = {
        "xterm": {"black": ((15, 15),), "white": ((17, 15),), "grey": (24,)},
        "hand2": {"black": ((14, 8),), "white": ((17, 7),), "grey": SIZES},
    }

    def _frames(self, name):
        cursor = _read_cursor(CURSORS / name)
        for image in cursor.images:
            width, height, rgba = decode_rgba(image.png)
            yield image, width, height, rgba

    def _assert_points_show(self, rgba, width, size, coordinates, expected):
        for x, y in coordinates:
            self.assertEqual(
                _pixel(rgba, width, x * size // 32, y * size // 32), expected
            )

    def test_each_frame_has_the_pinned_hotspot_and_face_and_outline(self):
        for name, points in self.EXPECTATIONS.items():
            for image, width, _height, rgba in self._frames(name):
                with self.subTest(name=name, size=image.nominal_size):
                    self._assert_pinned_points(name, image, width, rgba, points)

    def _assert_pinned_points(self, name, image, width, rgba, points):
        size = image.nominal_size
        self.assertEqual(
            (image.hotspot_x, image.hotspot_y), HOTSPOTS[name][size]
        )
        self.assertEqual(_pixel(rgba, width, *HOTSPOTS[name][size])[3], 255)
        self._assert_points_show(rgba, width, size, points["black"], BLACK)
        self._assert_points_show(rgba, width, size, points["white"], WHITE)

    def test_each_frame_has_transparent_corners(self):
        for name in self.EXPECTATIONS:
            for image, width, height, rgba in self._frames(name):
                with self.subTest(name=name, size=image.nominal_size):
                    self._assert_corners_transparent(width, height, rgba)

    def _assert_corners_transparent(self, width, height, rgba):
        for x, y in (
            (0, 0),
            (width - 1, 0),
            (0, height - 1),
            (width - 1, height - 1),
        ):
            self.assertEqual(_pixel(rgba, width, x, y), TRANSPARENT)

    def _assert_grey_level(self, size, points, pixels):
        if size not in points["grey"]:
            return
        self.assertTrue(
            any(p[3] == 255 and 0 < p[0] < 255 for p in pixels),
            "no opaque pixel with an intermediate grey level",
        )

    def test_each_frame_is_antialiased(self):
        for name, points in self.EXPECTATIONS.items():
            for image, width, height, rgba in self._frames(name):
                size = image.nominal_size
                with self.subTest(name=name, size=size):
                    self._assert_antialiased(rgba, width, height, size, points)

    def _assert_antialiased(self, rgba, width, height, size, points):
        pixels = [
            _pixel(rgba, width, x, y)
            for y in range(height)
            for x in range(width)
        ]
        self.assertTrue(
            any(0 < p[3] < 255 for p in pixels),
            "no partly covered edge pixel",
        )
        # Only the sizes the design pins: the I-beam's stem edges
        # fall inside a pixel at 24 but on pixel boundaries at 16
        # and 32, so only its 24 frame has a grey-level edge.
        self._assert_grey_level(size, points, pixels)


if __name__ == "__main__":
    unittest.main()
