"""Tests for tools/make_wallpaper.py's tile bounds check and main() entry point."""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import repo_root  # noqa: F401
from tools import make_wallpaper, png  # noqa: E402
from tools.png_write import encode_png  # noqa: E402

TILE = make_wallpaper.TILE_SIZE
X0, Y0 = make_wallpaper.TILE_ORIGIN
SMALL_RESOLUTIONS = ((130, 3), (5, 2))


def gradient(width, height):
    return bytes((i * 5 + i // 251) % 256 for i in range(width * height * 3))


class TestTileFromReferenceBounds(unittest.TestCase):
    def image(self, width, height):
        return png.Image(width, height, bytes(width * height * 3))

    def test_image_one_pixel_short_in_either_axis_is_rejected(self):
        for width, height in ((X0 + TILE - 1, Y0 + TILE), (X0 + TILE, Y0 + TILE - 1)):
            with self.subTest(size=(width, height)):
                with self.assertRaises(ValueError) as caught:
                    make_wallpaper.tile_from_reference(self.image(width, height))
                self.assertIn("does not fit", str(caught.exception))
                self.assertIn(f"{width}x{height}", str(caught.exception))

    def test_image_exactly_fitting_the_tile_is_accepted(self):
        width, height = X0 + TILE, Y0 + TILE
        rgb = gradient(width, height)
        tile = make_wallpaper.tile_from_reference(png.Image(width, height, rgb))
        self.assertEqual(len(tile), TILE * TILE * 3)
        self.assertEqual(tile[:3], rgb[(Y0 * width + X0) * 3 :][:3])
        self.assertEqual(tile[-3:], rgb[-3:])


class TestMain(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        patches = (
            mock.patch.object(make_wallpaper, "ROOT", self.root),
            mock.patch.object(make_wallpaper, "RESOLUTIONS", SMALL_RESOLUTIONS),
        )
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)
        self.images = self.root / make_wallpaper.PACKAGE_DIR / "contents" / "images"

    def write_reference(self, width, height):
        rgb = gradient(width, height)
        path = self.root / make_wallpaper.REFERENCE
        path.parent.mkdir(parents=True)
        path.write_bytes(encode_png(width, height, rgb))
        return rgb

    def run_main(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            status = make_wallpaper.main()
        return status, err.getvalue()

    def test_writes_one_tiled_image_per_resolution_from_the_reference_tile(self):
        width, height = X0 + TILE, Y0 + TILE
        rgb = self.write_reference(width, height)
        tile = make_wallpaper.tile_from_reference(png.Image(width, height, rgb))
        status, err = self.run_main()
        self.assertEqual((status, err), (0, ""))
        self.assertEqual(
            sorted(p.name for p in self.images.iterdir()),
            sorted(f"{w}x{h}.png" for w, h in SMALL_RESOLUTIONS),
        )
        for w, h in SMALL_RESOLUTIONS:
            with self.subTest(size=(w, h)):
                image = png.read_png(self.images / f"{w}x{h}.png")
                self.assertEqual((image.width, image.height), (w, h))
                self.assertEqual(image.rgb, make_wallpaper.tiled_rgb(tile, w, h))

    def test_rerun_rewrites_identical_bytes(self):
        self.write_reference(X0 + TILE, Y0 + TILE)
        self.run_main()
        first = {p.name: p.read_bytes() for p in self.images.iterdir()}
        self.run_main()
        self.assertEqual({p.name: p.read_bytes() for p in self.images.iterdir()}, first)

    def test_missing_reference_exits_2_naming_it_and_writes_nothing(self):
        status, err = self.run_main()
        self.assertEqual(status, 2)
        self.assertTrue(err.startswith("make_wallpaper: error: "))
        self.assertIn(make_wallpaper.REFERENCE, err)
        self.assertFalse(self.images.exists())

    def test_reference_too_small_for_the_tile_exits_2_and_writes_nothing(self):
        self.write_reference(TILE, TILE)
        status, err = self.run_main()
        self.assertEqual(status, 2)
        self.assertIn("does not fit", err)
        self.assertFalse(self.images.exists())


if __name__ == "__main__":
    unittest.main()
