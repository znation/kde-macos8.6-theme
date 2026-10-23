"""Tests for tools/make_wallpaper.py's tile bounds check, main() entry point and reference guard."""

from __future__ import annotations

import contextlib
import errno
import io
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.cli_fixtures import run_main  # noqa: E402
from support.close_tracking import failing_fdopen  # noqa: E402
from support.tmp_dir import make_tmp_dir
from tools import atomic_write, make_wallpaper, png  # noqa: E402
from tools.png.write import encode_png  # noqa: E402

TILE = make_wallpaper.TILE_SIZE
X0, Y0 = make_wallpaper.TILE_ORIGIN
SMALL_RESOLUTIONS = ((130, 3), (5, 2))


def gradient(width, height):
    """Return a deterministic *width* x *height* RGB byte string."""
    return bytes((i * 5 + i // 251) % 256 for i in range(width * height * 3))


class TestTileFromReferenceBounds(unittest.TestCase):
    def image(self, width, height):
        """Return a zero-filled *width* x *height* image."""
        return png.Image(width, height, bytes(width * height * 3))

    def test_image_one_pixel_short_in_either_axis_is_rejected(self):
        for width, height in ((X0 + TILE - 1, Y0 + TILE), (X0 + TILE, Y0 + TILE - 1)):
            with self.subTest(size=(width, height)):
                with self.assertRaises(ValueError) as caught:
                    make_wallpaper.tile_from_reference(self.image(width, height))
                self.assertIn("does not fit", str(caught.exception))
                self.assertIn(f"{width}x{height}", str(caught.exception))

    def test_non_image_is_rejected(self):
        for bad in (b"abc", 1, None):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError) as caught:
                    make_wallpaper.tile_from_reference(bad)
                self.assertIn("must be an Image", str(caught.exception))

    def test_image_exactly_fitting_the_tile_is_accepted(self):
        width, height = X0 + TILE, Y0 + TILE
        rgb = gradient(width, height)
        tile = make_wallpaper.tile_from_reference(png.Image(width, height, rgb))
        self.assertEqual(len(tile), TILE * TILE * 3)
        self.assertEqual(tile[:3], rgb[(Y0 * width + X0) * 3 :][:3])
        self.assertEqual(tile[-3:], rgb[-3:])


class TestArguments(unittest.TestCase):
    """The generator has no options, but must not silently ignore its argv.

    The tool rewrites the checked-in wallpaper images, so an argument it does
    not understand (a typo, an old flag, ``--help``) must be a usage
    diagnostic before anything is written, not an ignored word followed by a
    full rewrite.
    """

    def setUp(self):
        self.root = make_tmp_dir(self)
        patch = mock.patch.object(make_wallpaper, "ROOT", self.root)
        patch.start()
        self.addCleanup(patch.stop)
        self.images = self.root / make_wallpaper.PACKAGE_DIR / "contents" / "images"

    def test_help_prints_usage_and_exits_zero(self):
        result = run_main(make_wallpaper.main, "make_wallpaper", ["--help"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage: make_wallpaper", result.stdout)
        self.assertIn(
            "exit status: 0 when every image was written", result.stdout
        )
        self.assertFalse(self.images.exists())

    def test_unknown_argument_is_a_usage_error_and_writes_nothing(self):
        result = run_main(make_wallpaper.main, "make_wallpaper", ["--dry-run"])
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("unrecognized arguments: --dry-run", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse(self.images.exists())


class TestMain(unittest.TestCase):
    def setUp(self):
        self.root = make_tmp_dir(self)
        patches = (
            mock.patch.object(make_wallpaper, "ROOT", self.root),
            mock.patch.object(make_wallpaper, "RESOLUTIONS", SMALL_RESOLUTIONS),
        )
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)
        self.images = self.root / make_wallpaper.PACKAGE_DIR / "contents" / "images"

    def write_reference(self, width, height):
        """Write a gradient reference PNG and return its RGB bytes."""
        rgb = gradient(width, height)
        path = self.root / make_wallpaper.REFERENCE
        path.parent.mkdir(parents=True)
        path.write_bytes(encode_png(width, height, rgb))
        return rgb

    def run_main(self):
        """Run ``main`` and return ``(status, stderr)``."""
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            status = make_wallpaper.main([])
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

    def test_a_write_that_dies_midway_keeps_the_previous_image_and_no_partial(self):
        self.write_reference(X0 + TILE, Y0 + TILE)
        width, height = SMALL_RESOLUTIONS[0]
        first = self.images / f"{width}x{height}.png"
        first.parent.mkdir(parents=True, exist_ok=True)
        first.write_bytes(b"previous good wallpaper")

        def crashing_fdopen(descriptor, *args, **kwargs):
            handle = real_fdopen(descriptor, *args, **kwargs)

            class CrashingWriter:
                def __getattr__(self, name):
                    return getattr(handle, name)

                def __enter__(self):
                    return self

                def __exit__(self, *exc_info):
                    handle.close()
                    return False

                def write(self, data):
                    handle.write(data[: len(data) // 2])
                    raise OSError(errno.ENOSPC, "No space left on device")

            return CrashingWriter()

        real_fdopen = os.fdopen
        with mock.patch.object(os, "fdopen", crashing_fdopen):
            status, err = self.run_main()
        self.assertEqual(status, 2)
        self.assertIn("cannot write", err)
        self.assertEqual(first.read_bytes(), b"previous good wallpaper")
        self.assertEqual([p.name for p in self.images.iterdir()], [first.name])

    def test_unwritable_images_directory_exits_2_naming_it(self):
        # `main` promises "0, or 2 on error", and every other failure path is
        # caught; the images directory itself must not raise a traceback when
        # it cannot be created (a read-only checkout, a `contents` file).
        self.write_reference(X0 + TILE, Y0 + TILE)
        with mock.patch.object(
            Path, "mkdir", side_effect=OSError(errno.EROFS, "Read-only file system")
        ):
            status, err = self.run_main()
        self.assertEqual(status, 2)
        self.assertIn("cannot create", err)
        self.assertIn(str(self.images), err)

    def test_missing_reference_exits_2_naming_it_and_writes_nothing(self):
        status, err = self.run_main()
        self.assertEqual(status, 2)
        self.assertTrue(err.startswith("make_wallpaper: error: "))
        self.assertIn(make_wallpaper.REFERENCE, err)
        self.assertFalse(self.images.exists())

    def test_a_control_character_in_the_reference_path_is_escaped(self):
        # A checkout path can carry a control character, and read_png embeds
        # the path in its error message. The tool must route that message
        # through the shared escaped diagnostic instead of printing the raw
        # ESC to the operator's terminal.
        with mock.patch.object(
            make_wallpaper, "REFERENCE", "\x1b[31mhidden.png"
        ):
            status, err = self.run_main()
        self.assertEqual(status, 2)
        self.assertTrue(err.startswith("make_wallpaper: error: "))
        self.assertNotIn("\x1b", err)
        self.assertIn("\\u001b", err)

    def test_reference_too_small_for_the_tile_exits_2_and_writes_nothing(self):
        self.write_reference(TILE, TILE)
        status, err = self.run_main()
        self.assertEqual(status, 2)
        self.assertIn("does not fit", err)
        self.assertFalse(self.images.exists())


class TestReferenceContainment(unittest.TestCase):
    """The reference screenshot is a repository file; a symlink out of it is refused.

    A checked-in symlink can point anywhere on the machine, and the generator
    copies what it reads into the wallpaper package inside the repository, so
    reading a private file through such a symlink would publish its pixels
    with the next commit.
    """

    def setUp(self):
        self.root = make_tmp_dir(self)
        self.outside = make_tmp_dir(self)
        patches = (
            mock.patch.object(make_wallpaper, "ROOT", self.root),
            mock.patch.object(make_wallpaper, "RESOLUTIONS", SMALL_RESOLUTIONS),
        )
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)
        self.images = self.root / make_wallpaper.PACKAGE_DIR / "contents" / "images"
        self.reference = self.root / make_wallpaper.REFERENCE

    def test_a_reference_symlinked_outside_the_repository_is_refused(self):
        # The symlink points at a valid PNG outside the repository, so a
        # generator that follows it decodes the file and writes its pixels
        # into the package; the guard must refuse it before the decode.
        width, height = X0 + TILE, Y0 + TILE
        secret = self.outside / "private.png"
        secret.write_bytes(encode_png(width, height, gradient(width, height)))
        self.reference.parent.mkdir(parents=True)
        self.reference.symlink_to(secret)

        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            status = make_wallpaper.main([])

        self.assertEqual(status, 2)
        self.assertTrue(err.getvalue().startswith("make_wallpaper: error: "))
        self.assertIn("symlink escape", err.getvalue())
        self.assertFalse(self.images.exists())

    def test_a_reference_inside_the_repository_is_still_read(self):
        # The guard must not refuse the ordinary case: the shipped reference
        # lives in the repository, and its pixels are the wallpaper's tile.
        width, height = X0 + TILE, Y0 + TILE
        rgb = gradient(width, height)
        self.reference.parent.mkdir(parents=True)
        self.reference.write_bytes(encode_png(width, height, rgb))

        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            status = make_wallpaper.main([])

        self.assertEqual((status, err.getvalue()), (0, ""))
        for w, h in SMALL_RESOLUTIONS:
            with self.subTest(size=(w, h)):
                image = png.read_png(self.images / f"{w}x{h}.png")
                self.assertEqual(
                    image.rgb,
                    make_wallpaper.tiled_rgb(
                        make_wallpaper.tile_from_reference(
                            png.Image(width, height, rgb)
                        ),
                        w,
                        h,
                    ),
                )


class TestOutputContainment(unittest.TestCase):
    """The images directory is a repository path; a symlink out of it is refused.

    The generator writes the wallpaper images into the package's
    ``contents/images`` directory. A checked-in symlink at that path points
    anywhere on the machine, so writing through it would put the images
    outside the wallpaper package, into a directory a contributor names, and
    overwrite same-named files there.
    """

    def setUp(self):
        self.root = make_tmp_dir(self)
        self.outside = make_tmp_dir(self)
        patches = (
            mock.patch.object(make_wallpaper, "ROOT", self.root),
            mock.patch.object(make_wallpaper, "RESOLUTIONS", SMALL_RESOLUTIONS),
        )
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)
        self.images = self.root / make_wallpaper.PACKAGE_DIR / "contents" / "images"
        self.reference = self.root / make_wallpaper.REFERENCE

    def write_reference(self):
        """Write a gradient reference PNG at the repository's reference path."""
        width, height = X0 + TILE, Y0 + TILE
        self.reference.parent.mkdir(parents=True)
        self.reference.write_bytes(encode_png(width, height, gradient(width, height)))

    def run_main(self):
        """Run ``main`` and return ``(status, stderr)``."""
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            status = make_wallpaper.main([])
        return status, err.getvalue()

    def test_an_images_directory_symlinked_outside_the_repository_is_refused(self):
        # The symlink points at a directory outside the repository, so a
        # generator that writes through it puts the wallpaper images there;
        # the guard must refuse it before the first write.
        self.write_reference()
        self.images.parent.mkdir(parents=True)
        self.images.symlink_to(self.outside, target_is_directory=True)

        status, err = self.run_main()

        self.assertEqual(status, 2)
        self.assertTrue(err.startswith("make_wallpaper: error: "))
        self.assertIn("symlink escape", err)
        self.assertIn(str(self.images), err)
        self.assertEqual(list(self.outside.iterdir()), [])

    def test_an_images_directory_inside_the_repository_is_still_written(self):
        # The guard must not refuse the ordinary case: the package's images
        # directory lives in the repository, and the wallpaper belongs there.
        self.write_reference()

        status, err = self.run_main()

        self.assertEqual((status, err), (0, ""))
        self.assertEqual(
            sorted(p.name for p in self.images.iterdir()),
            sorted(f"{w}x{h}.png" for w, h in SMALL_RESOLUTIONS),
        )


class TestWriteAtomic(unittest.TestCase):
    def test_a_planted_symlink_does_not_redirect_the_write(self):
        # A local user who can write the images directory can create a
        # symlink at the fixed temporary name the tool used to build. The
        # write must not follow it: the tool has to pick its own fresh
        # temporary name.
        root = make_tmp_dir(self)
        target = root / "1280x800.png"
        victim = root / "victim.txt"
        victim.write_bytes(b"do not overwrite")
        planted = target.with_name(f".{target.name}-{os.getpid()}.tmp")
        planted.symlink_to(victim)

        make_wallpaper._write_atomic(target, b"new wallpaper")

        self.assertEqual(b"do not overwrite", victim.read_bytes())
        self.assertEqual(b"new wallpaper", target.read_bytes())

    def test_a_swap_after_the_exclusive_create_does_not_redirect_the_write(self):
        # ``mkstemp`` creates the temporary file exclusively, but another local
        # user who can write the images directory can still unlink it and park
        # a symlink at the name between the create and the write. The bytes
        # must go through the descriptor ``mkstemp`` returned, not the path, so
        # the symlink's target is left alone.
        root = make_tmp_dir(self)
        target = root / "1280x800.png"
        victim = root / "victim.txt"
        victim.write_bytes(b"do not overwrite")

        real_mkstemp = tempfile.mkstemp

        def swapping_mkstemp(*args, **kwargs):
            descriptor, name = real_mkstemp(*args, **kwargs)
            os.unlink(name)
            os.symlink(victim, name)
            return descriptor, name

        with mock.patch.object(atomic_write.tempfile, "mkstemp", swapping_mkstemp):
            make_wallpaper._write_atomic(target, b"new wallpaper")

        self.assertEqual(b"do not overwrite", victim.read_bytes())

    def test_output_mode_matches_the_process_umask(self):
        # mkstemp opens the temporary file 0600; the plain write this replaces
        # created the image with the process umask applied, so the rename must
        # leave that mode rather than an owner-only file.
        root = make_tmp_dir(self)
        target = root / "1280x800.png"
        previous = os.umask(0o027)
        self.addCleanup(os.umask, previous)

        make_wallpaper._write_atomic(target, b"new wallpaper")

        self.assertEqual(b"new wallpaper", target.read_bytes())
        self.assertEqual(0o640, stat.S_IMODE(target.stat().st_mode))


class TestWriteAtomicFdopen(unittest.TestCase):
    def test_failed_fdopen_closes_descriptor(self):
        import tempfile
        directory = tempfile.mkdtemp(prefix="make-wallpaper-fdopen-")
        root = Path(directory)
        target = root / "out.png"
        with failing_fdopen() as closed:
            with self.assertRaises(OSError):
                make_wallpaper._write_atomic(target, b"data")
        self.assertEqual(1, len(closed))

class TestTiledRgbValidation(unittest.TestCase):
    def test_invalid_dimensions_are_rejected(self):
        tile = bytes(make_wallpaper.TILE_SIZE * make_wallpaper.TILE_SIZE * 3)
        cases = (0, -1, True, False, 1.0, "1", None)
        for value in cases:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    make_wallpaper.tiled_rgb(tile, value, 2)
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    make_wallpaper.tiled_rgb(tile, 2, value)

    def test_valid_dimensions_accepted(self):
        tile = bytes(make_wallpaper.TILE_SIZE * make_wallpaper.TILE_SIZE * 3)
        out = make_wallpaper.tiled_rgb(tile, 2, 2)
        self.assertEqual(len(out), 2 * 2 * 3)


if __name__ == "__main__":
    unittest.main()
