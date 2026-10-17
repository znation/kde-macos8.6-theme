"""Validate the org.macos8.desktop wallpaper package and its generator."""

from __future__ import annotations

import os
import shutil
import unittest

from kpackage_install_case import KPackageInstallCase
from package_metadata import PackageMetadata
from reference_image import skip_unless_materialized
from theme_install import ROOT

from tools import make_wallpaper, png  # noqa: E402

WALLPAPER_ID = "org.macos8.desktop"
PACKAGE = os.path.join(ROOT, "theme", "wallpapers", WALLPAPER_ID)
METADATA = os.path.join(PACKAGE, "metadata.json")
IMAGES = os.path.join(PACKAGE, "contents", "images")
REFERENCE = os.path.join(ROOT, make_wallpaper.REFERENCE)
TILE = make_wallpaper.TILE_SIZE


def block(image, x0, y0):
    """The TILE x TILE RGB block of *image* anchored at (x0, y0)."""
    return b"".join(
        bytes(image.rgb[(y * image.width + x0) * 3 : (y * image.width + x0 + TILE) * 3])
        for y in range(y0, y0 + TILE)
    )


class TestMetadata(PackageMetadata, unittest.TestCase):
    METADATA_PATH = METADATA
    PACKAGE_STRUCTURE = "Wallpaper/Images"
    PACKAGE_ID = WALLPAPER_ID

    def test_plasma_api_version(self):
        # Wallpaper packages carry no X-Plasma-API key (the system `Next`
        # wallpaper's metadata.json has none), so the mixin's check is moot.
        self.assertFalse(
            [key for key in self.metadata if key.startswith("X-Plasma")],
            f"{METADATA}: a wallpaper package takes no X-Plasma-* key",
        )


class TestImages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.images = {}
        cls.error = None
        try:
            for width, height in make_wallpaper.RESOLUTIONS:
                cls.images[(width, height)] = png.read_png(
                    os.path.join(IMAGES, f"{width}x{height}.png")
                )
        except png.PngError as exc:
            cls.error = exc

    def setUp(self):
        skip_unless_materialized(self, IMAGES, self.error)

    def test_images_dir_holds_exactly_one_png_per_resolution(self):
        expected = sorted(f"{w}x{h}.png" for w, h in make_wallpaper.RESOLUTIONS)
        self.assertEqual(sorted(os.listdir(IMAGES)), expected)

    def test_each_image_decodes_to_its_named_size(self):
        for (width, height), image in self.images.items():
            with self.subTest(size=f"{width}x{height}"):
                self.assertEqual((image.width, image.height), (width, height))

    def test_each_image_is_the_same_tile_anchored_at_the_origin(self):
        tile = block(self.images[(1024, 768)], 0, 0)
        for (width, height), image in self.images.items():
            with self.subTest(size=f"{width}x{height}"):
                self.assertEqual(
                    image.rgb, make_wallpaper.tiled_rgb(tile, width, height)
                )


class TestTiledRgb(unittest.TestCase):
    def test_pixel_xy_is_tile_row_y_column_x_modulo_the_tile_size(self):
        tile = bytes(
            v for y in range(TILE) for x in range(TILE) for v in (x, y, (x + y) % 256)
        )
        width, height = 2 * TILE + 5, TILE + 3
        rgb = make_wallpaper.tiled_rgb(tile, width, height)
        self.assertEqual(len(rgb), width * height * 3)
        for x, y in ((0, 0), (TILE, 0), (TILE + 4, TILE + 2), (width - 1, height - 1)):
            offset = (y * width + x) * 3
            self.assertEqual(
                tuple(rgb[offset : offset + 3]),
                (x % TILE, y % TILE, (x % TILE + y % TILE) % 256),
            )

    def test_a_tile_of_the_wrong_length_is_rejected(self):
        with self.assertRaises(ValueError):
            make_wallpaper.tiled_rgb(bytes(3), 4, 4)


class TestReferenceTile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = None
        cls.reference_error = None
        cls.shipped = None
        try:
            cls.reference = png.read_png(REFERENCE)
            cls.shipped = png.read_png(os.path.join(IMAGES, "1024x768.png"))
        except png.PngError as exc:
            cls.reference_error = exc

    def setUp(self):
        skip_unless_materialized(self, REFERENCE, self.reference_error)

    def test_tile_from_reference_equals_the_shipped_tile(self):
        self.assertEqual(
            make_wallpaper.tile_from_reference(self.reference),
            block(self.shipped, 0, 0),
        )

    def test_the_tile_repeats_every_128_pixels_in_the_reference(self):
        tile = make_wallpaper.tile_from_reference(self.reference)
        self.assertEqual(block(self.reference, *make_wallpaper.TILE_ORIGIN), tile)
        for origin in ((384, 384), (768, 512)):
            with self.subTest(origin=origin):
                self.assertEqual(block(self.reference, *origin), tile)

    def test_reference_pixel_is_the_dominant_desktop_colour(self):
        pixel = png.pixel_at(self.reference, 300, 500)
        self.assertEqual(pixel, (0x63, 0x63, 0x9C))
        tile = make_wallpaper.tile_from_reference(self.reference)
        offset = ((500 % TILE) * TILE + 300 % TILE) * 3
        self.assertEqual(tuple(tile[offset : offset + 3]), pixel)


@unittest.skipUnless(shutil.which("kpackagetool6"), "needs kpackagetool6")
class TestPackageValid(KPackageInstallCase, unittest.TestCase):
    KPACKAGETOOL_TYPE = "Wallpaper/Images"
    PACKAGE_DIR = PACKAGE
    PACKAGE_ID = WALLPAPER_ID


if __name__ == "__main__":
    unittest.main()
