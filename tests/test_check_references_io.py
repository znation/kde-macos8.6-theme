"""Filesystem-failure and containment tests for tools/check_references.py.

Every read, listing, and containment resolution the checker performs must
surface as a problem line rather than a traceback, and a checked-in symlink
must not let it read outside the reference directory.
"""

import unittest

from check_references_fixtures import (
    load_checker,
    path_method_raises,
    reference_set,
    symlinked_reference,
)


class TestUnreadableImage(unittest.TestCase):
    """A permission-denied image named in sources.txt is reported, not raised.

    The checker reads each declared image's leading bytes to confirm it is a
    raster, so an unreadable file must become a problem line rather than
    abort the whole check with a traceback.
    """

    def test_unreadable_image_is_reported_not_raised(self):
        module = load_checker()
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
        self.assertTrue(
            any("locked.png" in p and "could not be read" in p for p in problems),
            problems,
        )


class TestUnreadableUndeclaredImage(unittest.TestCase):
    """An unreadable file with no sources entry is reported, not raised.

    The undeclared-image scan reads each unlisted file's leading bytes to
    decide whether it is an image, so a permission-denied stray in the
    reference directory must surface as a problem line instead of aborting
    the whole check with a traceback. This is the unlisted counterpart of
    ``TestUnreadableImage`` (which covers a file named in ``sources.txt``).
    """

    def test_unreadable_undeclared_file_is_reported_not_raised(self):
        module = load_checker()
        with reference_set(module, "", {"stray.bin": module.PNG_MAGIC}) as root:
            stray = root / "stray.bin"
            with path_method_raises(
                "open", stray, PermissionError, 13, "Permission denied"
            ):
                problems = module.check_references(root)
        self.assertTrue(
            any("stray.bin" in p and "could not be read" in p for p in problems),
            problems,
        )


class TestUnreadableSources(unittest.TestCase):
    """An unreadable sources.txt is reported, not raised.

    The provenance record can be present but unreadable (a permissions
    problem, say); the checker must return a problem line rather than let the
    OSError escape and abort the check.
    """

    def test_unreadable_sources_file_is_reported_not_raised(self):
        module = load_checker()
        with reference_set(
            module,
            "good.png | https://example.test/g.png | label\n",
            {"good.png": module.PNG_MAGIC},
        ) as root:
            sources = root / module.SOURCES_NAME
            with path_method_raises(
                "read_text", sources, PermissionError, 13, "Permission denied"
            ):
                problems = module.check_references(root)
        self.assertTrue(
            any(str(sources) in p and "could not be read" in p for p in problems),
            problems,
        )


class TestUndecodableSources(unittest.TestCase):
    """A sources.txt that is not valid UTF-8 is reported, not raised."""

    def test_non_utf8_sources_is_reported_not_raised(self):
        module = load_checker()
        # Latin-1 e-acute: a corrupt download or an editor that saved the
        # provenance record in a non-UTF-8 encoding.
        with reference_set(
            module, b"caf\xe9.png | https://example.test/x.png | label\n"
        ) as root:
            sources = root / module.SOURCES_NAME
            problems = module.check_references(root)
        self.assertTrue(
            any(str(sources) in p and "UTF-8" in p for p in problems), problems
        )


class TestUnreadableDirectory(unittest.TestCase):
    """A reference directory that cannot be listed is reported, not raised.

    The undeclared-image scan lists the directory, so a listing failure must
    surface as a problem line instead of a traceback.
    """

    def test_unreadable_directory_is_reported_not_raised(self):
        module = load_checker()
        with reference_set(module, "") as root:
            with path_method_raises(
                "iterdir", root, PermissionError, 13, "Permission denied"
            ):
                problems = module.check_references(root)
        self.assertTrue(
            any("could not be listed" in p for p in problems), problems
        )


class TestSymlinkEscape(unittest.TestCase):
    """A checked-in symlink must not make the checker read outside the directory.

    The reference directory is contributor-supplied, and git stores symlinks.
    A ``sources.txt`` symlink to a private file would make the checker read
    that file and print its lines as diagnostics, disclosing a file outside
    the reference set.
    """

    def test_sources_symlink_outside_directory_is_not_read(self):
        module = load_checker()
        with symlinked_reference(
            module, module.SOURCES_NAME, b"SECRET_TOKEN_abc123\n"
        ) as ref:
            problems = module.check_references(ref)
        joined = "\n".join(problems)
        self.assertNotIn("SECRET_TOKEN_abc123", joined)
        self.assertTrue(any("outside" in p for p in problems), problems)

    def test_declared_image_symlink_outside_directory_is_reported(self):
        module = load_checker()
        with symlinked_reference(
            module,
            "link.png",
            module.PNG_MAGIC + b"secret",
            "link.png | https://example.test/l.png | label\n",
        ) as ref:
            problems = module.check_references(ref)
        self.assertTrue(any("outside" in p for p in problems), problems)

    def test_undeclared_image_symlink_outside_directory_is_not_read(self):
        """The undeclared-file scan must not sniff a symlink's outside target.

        The scan reads a file's leading bytes to catch an image saved without
        an image extension, and it must apply the same containment check the
        declared-entry loop does before opening a symlink. The name below has
        no image suffix, so the escape can only be reported by the containment
        check, not by the content sniff it replaces.
        """
        module = load_checker()
        with symlinked_reference(
            module, "leak", module.PNG_MAGIC + b"secret", ""
        ) as ref:
            problems = module.check_references(ref)
        joined = "\n".join(problems)
        self.assertIn("outside", joined, problems)
        self.assertNotIn("image has no entry", joined, problems)


class TestResolveFailureIsFailClosed(unittest.TestCase):
    """A path that cannot be resolved must be treated as escaping the directory.

    ``_resolves_within`` calls ``Path.resolve()`` to keep every read inside the
    reference directory, and resolving can raise ``OSError`` on a filesystem
    failure. The containment check must fail closed: an unresolvable path is
    not assumed to be inside the directory, so the checker reports it instead
    of letting the ``OSError`` escape and abort the run with a traceback.
    ``Path.resolve()`` does not raise for a real symlink loop on this runtime,
    so the branch is driven by making the resolution itself raise.
    """

    def test_unresolvable_sources_path_is_reported_not_raised(self):
        module = load_checker()
        with reference_set(
            module,
            "good.png | https://example.test/g.png | label\n",
            {"good.png": module.PNG_MAGIC},
        ) as root:
            sources = root / module.SOURCES_NAME
            with path_method_raises(
                "resolve",
                sources,
                OSError,
                40,
                "Too many levels of symbolic links",
            ):
                problems = module.check_references(root)
        self.assertTrue(
            any(str(sources) in p and "outside" in p for p in problems),
            problems,
        )


if __name__ == "__main__":
    unittest.main()
