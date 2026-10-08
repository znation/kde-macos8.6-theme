"""Regression tests for the reference checker's self-test diagnostics."""

import contextlib
import importlib.util
import io
import os
import tempfile
import unittest
import unittest.mock
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKER = os.path.join(ROOT, "tools", "check_references.py")


def load_checker():
    spec = importlib.util.spec_from_file_location("check_references", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestSelfTestDiagnostics(unittest.TestCase):
    def test_failure_names_the_case_not_the_last_image(self):
        module = load_checker()
        # Force every fixture to fail so _self_test prints its diagnostics.
        module.check_references = lambda directory: ["boom"]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = module._self_test()
        self.assertEqual(code, 1)
        printed = out.getvalue()
        self.assertIn("self-test 'undeclared image'", printed)
        self.assertNotIn("self-test 'extra.png'", printed)


class TestSelfTestPasses(unittest.TestCase):
    """The checker's fixtures must pass under the default `make check`.

    The other tests here mock ``check_references`` (diagnostics) or deny a
    read (error paths), so the core checks -- missing file, duplicate, LFS
    pointer, non-image payload, undeclared image -- run only in the tool's
    built-in self-test, which `make check` does not otherwise invoke.
    """

    def test_built_in_fixtures_all_pass(self):
        module = load_checker()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = module._self_test()
        self.assertEqual(code, 0, out.getvalue())


class TestUnreadableImage(unittest.TestCase):
    def test_unreadable_image_is_reported_not_raised(self):
        module = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / module.SOURCES_NAME).write_text(
                "locked.png | https://example.test/l.png | label\n",
                encoding="utf-8",
            )
            image = root / "locked.png"
            image.write_bytes(module.PNG_MAGIC)
            real_open = Path.open

            def deny_locked(self, *args, **kwargs):
                if self == image:
                    raise PermissionError(13, "Permission denied", str(self))
                return real_open(self, *args, **kwargs)

            with unittest.mock.patch.object(Path, "open", deny_locked):
                problems = module.check_references(root)
        self.assertTrue(
            any("locked.png" in p and "could not be read" in p for p in problems),
            problems,
        )


class TestUnreadableSources(unittest.TestCase):
    def test_unreadable_sources_file_is_reported_not_raised(self):
        module = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = root / module.SOURCES_NAME
            sources.write_text(
                "good.png | https://example.test/g.png | label\n",
                encoding="utf-8",
            )
            (root / "good.png").write_bytes(module.PNG_MAGIC)
            real_read_text = Path.read_text

            def deny_sources(self, *args, **kwargs):
                if self == sources:
                    raise PermissionError(13, "Permission denied", str(self))
                return real_read_text(self, *args, **kwargs)

            with unittest.mock.patch.object(Path, "read_text", deny_sources):
                problems = module.check_references(root)
        self.assertTrue(
            any(str(sources) in p and "could not be read" in p for p in problems),
            problems,
        )


class TestUnreadableDirectory(unittest.TestCase):
    def test_unreadable_directory_is_reported_not_raised(self):
        module = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / module.SOURCES_NAME).write_text("", encoding="utf-8")
            real_iterdir = Path.iterdir

            def deny_iterdir(self):
                if self == root:
                    raise PermissionError(13, "Permission denied", str(self))
                return real_iterdir(self)

            with unittest.mock.patch.object(Path, "iterdir", deny_iterdir):
                problems = module.check_references(root)
        self.assertTrue(
            any("could not be listed" in p for p in problems), problems
        )


class TestFilenameMustBeBare(unittest.TestCase):
    def test_nested_filename_is_rejected_even_when_the_file_exists(self):
        module = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / module.SOURCES_NAME).write_text(
                "sub/good.png | https://example.test/g.png | label\n",
                encoding="utf-8",
            )
            (root / "sub").mkdir()
            (root / "sub" / "good.png").write_bytes(module.PNG_MAGIC)
            problems = module.check_references(root)
        self.assertTrue(
            any("sub/good.png" in p and "bare filename" in p for p in problems),
            problems,
        )

    def test_parent_traversal_is_rejected_even_when_the_file_exists(self):
        module = load_checker()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "refs"
            root.mkdir()
            (root / module.SOURCES_NAME).write_text(
                "../escape.png | https://example.test/e.png | label\n",
                encoding="utf-8",
            )
            (root.parent / "escape.png").write_bytes(module.PNG_MAGIC)
            problems = module.check_references(root)
        self.assertTrue(
            any("../escape.png" in p and "bare filename" in p for p in problems),
            problems,
        )


class TestAcceptedImageFormats(unittest.TestCase):
    """The checker must accept every raster format the reference set uses.

    The built-in self-test exercises only the PNG and WebP signatures, so a
    regression in the JPEG or GIF handling would flag the reference set's 9
    JPEG and 1 GIF files as non-images without any test noticing.
    """

    def _problems_for(self, module, filename, content):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / module.SOURCES_NAME).write_text(
                f"{filename} | https://example.test/x | label\n",
                encoding="utf-8",
            )
            (root / filename).write_bytes(content)
            return module.check_references(root)

    def test_jpeg_signature_is_accepted(self):
        module = load_checker()
        # A JPEG begins ff d8 ff; the bytes after it are not part of the check.
        problems = self._problems_for(
            module, "photo.jpg", b"\xff\xd8\xff\xe1" + b"\x00" * 8
        )
        self.assertEqual(problems, [])

    def test_gif87a_signature_is_accepted(self):
        module = load_checker()
        problems = self._problems_for(module, "anim.gif", b"GIF87a" + b"\x00" * 6)
        self.assertEqual(problems, [])

    def test_gif89a_signature_is_accepted(self):
        module = load_checker()
        problems = self._problems_for(module, "anim.gif", b"GIF89a" + b"\x00" * 6)
        self.assertEqual(problems, [])

    def test_riff_container_that_is_not_webp_is_rejected(self):
        module = load_checker()
        # A RIFF/WAVE payload shares the RIFF prefix but is not an image; the
        # WEBP marker at bytes 8-11 is what makes it a WebP.
        problems = self._problems_for(
            module, "sound.png", b"RIFF\x24\x00\x00\x00WAVEfmt "
        )
        self.assertTrue(
            any(
                "sound.png" in p and "not a PNG, JPEG, GIF or WebP" in p
                for p in problems
            ),
            problems,
        )


if __name__ == "__main__":
    unittest.main()
