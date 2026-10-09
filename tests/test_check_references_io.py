"""Filesystem-failure and containment tests for tools/check_references.py.

Every read, listing, and containment resolution the checker performs must
surface as a problem line rather than a traceback, and a checked-in symlink
must not let it read outside the reference directory.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from allocation_fixtures import peak_allocation
from check_references_fixtures import (
    CheckerTestCase,
    assert_problem,
    assert_sources_failure,
    path_method_raises,
    reference_set,
    symlinked_reference,
)


class TestUnreadableImage(CheckerTestCase):
    """A permission-denied image named in sources.txt is reported, not raised.

    The checker reads each declared image's leading bytes to confirm it is a
    raster, so an unreadable file must become a problem line rather than
    abort the whole check with a traceback.
    """

    def test_unreadable_image_is_reported_not_raised(self):
        module = self.checker
        with reference_set(
            module,
            "locked.png | https://example.test/l.png | label\n",
            {"locked.png": module.PNG_MAGIC},
        ) as root:
            image = root / "locked.png"
            with path_method_raises(
                "open", image, PermissionError, 13, "Permission denied"
            ):
                problems = module.check_references(root)
        assert_problem(self, problems, "locked.png", "could not be read")


class TestUnreadableUndeclaredImage(CheckerTestCase):
    """An unreadable file with no sources entry is reported, not raised.

    The undeclared-image scan reads each unlisted file's leading bytes to
    decide whether it is an image, so a permission-denied stray in the
    reference directory must surface as a problem line instead of aborting
    the whole check with a traceback. This is the unlisted counterpart of
    ``TestUnreadableImage`` (which covers a file named in ``sources.txt``).
    """

    def test_unreadable_undeclared_file_is_reported_not_raised(self):
        module = self.checker
        with reference_set(module, "", {"stray.bin": module.PNG_MAGIC}) as root:
            stray = root / "stray.bin"
            with path_method_raises(
                "open", stray, PermissionError, 13, "Permission denied"
            ):
                problems = module.check_references(root)
        assert_problem(self, problems, "stray.bin", "could not be read")


class TestUnreadableSources(CheckerTestCase):
    """An unreadable sources.txt is reported, not raised.

    The provenance record can be present but unreadable (a permissions
    problem, say); the checker must return a problem line rather than let the
    OSError escape and abort the check.
    """

    def test_unreadable_sources_file_is_reported_not_raised(self):
        assert_sources_failure(
            self,
            "open",
            PermissionError,
            13,
            "Permission denied",
            "could not be read",
        )


class TestOversizeSources(CheckerTestCase):
    """An oversized sources.txt is rejected before it is loaded whole.

    The provenance record is contributor-supplied, so a multi-gigabyte
    ``sources.txt`` must surface as a problem line instead of being read into
    memory and exhausting it. The checker stops reading one byte past its cap
    and reports the file, the way ``read_png`` rejects an oversize image.
    """

    def test_oversize_sources_is_reported_without_reading_it_all(self):
        module = self.checker
        limit = 4096
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / module.SOURCES_NAME).write_bytes(b"#" * (limit + 1))
            with mock.patch.object(module, "_MAX_SOURCES_BYTES", limit):
                problems, peak = peak_allocation(
                    lambda: module.check_references(root)
                )
        assert_problem(
            self, problems, str(root / module.SOURCES_NAME), "larger than"
        )
        self.assertLess(peak, limit + 1024 * 1024)


class TestUndecodableSources(CheckerTestCase):
    """A sources.txt that is not valid UTF-8 is reported, not raised."""

    def test_non_utf8_sources_is_reported_not_raised(self):
        module = self.checker
        # Latin-1 e-acute: a corrupt download or an editor that saved the
        # provenance record in a non-UTF-8 encoding.
        with reference_set(
            module, b"caf\xe9.png | https://example.test/x.png | label\n"
        ) as root:
            sources = root / module.SOURCES_NAME
            problems = module.check_references(root)
        assert_problem(self, problems, str(sources), "UTF-8")


class TestUnreadableDirectory(CheckerTestCase):
    """A reference directory that cannot be listed is reported, not raised.

    The undeclared-image scan lists the directory, so a listing failure must
    surface as a problem line instead of a traceback.
    """

    def test_unreadable_directory_is_reported_not_raised(self):
        module = self.checker
        with reference_set(module, "") as root:
            with path_method_raises(
                "iterdir", root, PermissionError, 13, "Permission denied"
            ):
                problems = module.check_references(root)
        assert_problem(self, problems, "could not be listed")


class TestSymlinkEscape(CheckerTestCase):
    """A checked-in symlink must not make the checker read outside the directory.

    The reference directory is contributor-supplied, and git stores symlinks.
    A ``sources.txt`` symlink to a private file would make the checker read
    that file and print its lines as diagnostics, disclosing a file outside
    the reference set.
    """

    def test_sources_symlink_outside_directory_is_not_read(self):
        module = self.checker
        with symlinked_reference(
            module, module.SOURCES_NAME, b"SECRET_TOKEN_abc123\n"
        ) as ref:
            problems = module.check_references(ref)
        joined = "\n".join(problems)
        self.assertNotIn("SECRET_TOKEN_abc123", joined)
        assert_problem(self, problems, "outside")

    def test_declared_image_symlink_outside_directory_is_reported(self):
        module = self.checker
        with symlinked_reference(
            module,
            "link.png",
            module.PNG_MAGIC + b"secret",
            "link.png | https://example.test/l.png | label\n",
        ) as ref:
            problems = module.check_references(ref)
        assert_problem(self, problems, "outside")

    def test_undeclared_image_symlink_outside_directory_is_not_read(self):
        """The undeclared-file scan must not sniff a symlink's outside target.

        The scan reads a file's leading bytes to catch an image saved without
        an image extension, and it must apply the same containment check the
        declared-entry loop does before opening a symlink. The name below has
        no image suffix, so the escape can only be reported by the containment
        check, not by the content sniff it replaces.
        """
        module = self.checker
        with symlinked_reference(
            module, "leak", module.PNG_MAGIC + b"secret", ""
        ) as ref:
            problems = module.check_references(ref)
        joined = "\n".join(problems)
        self.assertIn("outside", joined, problems)
        self.assertNotIn("image has no entry", joined, problems)


class TestUndeclaredDanglingImageSymlink(CheckerTestCase):
    """A dangling symlink named like an image is reported, not skipped.

    ``Path.is_file()`` follows the link and returns False when the target is
    gone, so the undeclared-image scan used to skip a ``*.png`` symlink whose
    target was deleted. The set then looked consistent although a ``.png``
    name on disk had no provenance entry. The checker must report the name
    without opening it (opening a FIFO or device would block).
    """

    def test_dangling_image_symlink_is_reported(self):
        module = self.checker
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / module.SOURCES_NAME).write_text("", encoding="utf-8")
            os.symlink(root / "gone.png", root / "dangling.png")
            problems = module.check_references(root)
        assert_problem(self, problems, "dangling.png", "no entry")


class TestResolveFailureIsFailClosed(CheckerTestCase):
    """A path that cannot be resolved must be treated as escaping the directory.

    ``_resolves_within`` calls ``Path.resolve()`` to keep every read inside the
    reference directory, and resolving can raise ``OSError`` on a filesystem
    failure or ``RuntimeError`` on the symlink loop Python before 3.13 reports.
    The containment check must fail closed: an unresolvable path is not assumed
    to be inside the directory, so the checker reports it instead of letting
    the exception escape and abort the run with a traceback. ``Path.resolve()``
    does not raise for a real symlink loop on this runtime, so each branch is
    driven by making the resolution itself raise.
    """

    def test_unresolvable_sources_path_is_reported_not_raised(self):
        assert_sources_failure(
            self,
            "resolve",
            OSError,
            40,
            "Too many levels of symbolic links",
            "outside",
        )

    def test_symlink_loop_sources_path_is_reported_not_raised(self):
        assert_sources_failure(
            self,
            "resolve",
            RuntimeError,
            40,
            "Symlink loop from sources.txt",
            "outside",
        )


if __name__ == "__main__":
    unittest.main()
