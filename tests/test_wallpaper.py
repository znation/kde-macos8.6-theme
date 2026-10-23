"""Validate the org.macos8.desktop wallpaper package and its generator."""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

from support import containment
from support.install_failure_cases import FailedInstallPreservesPackage
from support.symlink_fixtures import symlinked_repo
from support.install_lifecycle_cases import InstallLifecycleCases
from support.kpackage_install_case import KPackageInstallCase
from support.package_metadata import PackageMetadata
from support.reference_image import skip_unless_materialized
from support.installed_paths import installed_wallpaper, installed_wallpaper_dir
from support.repo_root import ROOT

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


def read_shipped_png(path, **kwargs):
    """Read a shipped PNG, refusing a path that escapes the repository.

    The wallpaper images and the reference screenshots are contributor-supplied
    theme assets, and a checked-in symlink at either path can point at a private
    PNG outside the repository. The suite decodes these images and echoes a
    mismatched image's RGB bytes in ``assertEqual``, so following such a symlink
    would print the private file's pixels in a failing test's diagnostic. The
    shared containment guard refuses the escape before :func:`png.read_png`
    opens the path; a path outside the repository (a test's temporary output) is
    read as before.
    """
    containment.require_within_repo(path, ROOT)
    return png.read_png(path, **kwargs)


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
                cls.images[(width, height)] = read_shipped_png(
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


class TestImageReadContainment(unittest.TestCase):
    """The suite's shipped-PNG reads refuse a repository symlink escape.

    The wallpaper images are contributor-supplied, and a checked-in symlink at
    one can point at a private PNG outside the repository. The suite echoes a
    mismatched image's RGB bytes in ``assertEqual``, so the read must refuse the
    escape before it is decoded, the same guard the other theme readers apply.
    """

    def test_image_reads_refuse_a_symlink_that_escapes_the_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, link = symlinked_repo(
                tmp, "images/1024x768.png", png.encode_png(2, 2, bytes(12))
            )
            # Drive the real setUpClass through a per-test subclass, so a
            # failure here cannot clear the images the shipped suite loaded.
            case = type("ContainmentCase", (TestImages,), {})
            with mock.patch.object(sys.modules[__name__], "ROOT", root), \
                    mock.patch.object(
                        sys.modules[__name__], "IMAGES", str(root / "images")
                    ):
                with self.assertRaises(ValueError) as caught:
                    case.setUpClass()
        self.assertIn(str(link), str(caught.exception))
        self.assertIn("resolves outside", str(caught.exception))


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

    def test_a_non_byte_tile_is_rejected(self):
        with self.assertRaises(ValueError) as caught:
            make_wallpaper.tiled_rgb("not bytes", 4, 4)
        self.assertIn("bytes or bytearray", str(caught.exception))


class TestReferenceTile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = None
        cls.reference_error = None
        cls.shipped = None
        try:
            cls.reference = read_shipped_png(REFERENCE)
            cls.shipped = read_shipped_png(
                os.path.join(IMAGES, "1024x768.png")
            )
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


class TestInstall(
    FailedInstallPreservesPackage, InstallLifecycleCases, unittest.TestCase
):
    KIND = "wallpapers"
    MAKE_PACKAGES = "wallpaper"
    PACKAGE_ID = WALLPAPER_ID
    PACKAGE_DIR = PACKAGE
    INSTALLED_FILES = ("metadata.json",) + tuple(
        f"contents/images/{width}x{height}.png"
        for width, height in make_wallpaper.RESOLUTIONS
    )
    COPY_FAILURE_GLOB = "*/wallpapers/*"

    def installed_parent(self, tmp):
        """Return the directory holding the installed wallpapers."""
        return installed_wallpaper_dir(tmp)

    def installed_package_dir(self, tmp):
        """Return the installed wallpaper package's own directory."""
        return installed_wallpaper(tmp, self.PACKAGE_ID)


if __name__ == "__main__":
    unittest.main()
