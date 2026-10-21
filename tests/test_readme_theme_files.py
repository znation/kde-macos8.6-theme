"""README's list of shipped theme SVGs must match the files on disk.

README names every SVG the desktop theme and the window decoration ship, in
backticks, so a contributor can find the artwork for a surface. Adding a widget
SVG without naming it, or deleting one and leaving its name behind, makes that
list lie; these tests derive both sides and fail when they disagree.
"""

from __future__ import annotations

import glob
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import containment
from support.desktoptheme_paths import PACKAGE
from support.repo_root import ROOT

_DESKTOP_TOKEN = re.compile(r"`((?:widgets|dialogs)/[^`/]+\.svg)`")
_AURORAE_TOKEN = re.compile(r"`([^`/]+\.svg)`")
AURORAE_DIR = os.path.join(ROOT, "theme", "aurorae", "themes", "org.macos8.desktop")


def readme_text():
    """Return the UTF-8 text of the repository's ``README.md``.

    ``README.md`` is contributor-supplied, and a checked-in symlink at its
    path can point at a private file. The backticked SVG names this reader
    extracts are echoed by the ``assertEqual`` diagnostics below, so a path
    that resolves outside the repository is refused before it is opened.
    """
    path = os.path.join(ROOT, "README.md")
    containment.require_within_repo(path, ROOT)
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def shipped(package, pattern):
    """Paths of *package*'s SVGs matching *pattern*, relative to *package*."""
    return {
        os.path.relpath(path, package)
        for path in glob.glob(os.path.join(package, pattern), recursive=True)
    }


class TestReadmeThemeFiles(unittest.TestCase):
    def _assert_every_svg_is_named(self, token, package, pattern, label):
        """Fail when a shipped *label* SVG is absent from README's backticks."""
        named = set(token.findall(readme_text()))
        on_disk = shipped(package, pattern)
        self.assertTrue(on_disk, "no %s SVGs found under %s" % (label, package))
        self.assertEqual(
            set(),
            on_disk - named,
            "%s SVGs README does not name in backticks" % label,
        )

    def test_every_desktop_theme_svg_is_named_in_readme(self):
        self._assert_every_svg_is_named(
            _DESKTOP_TOKEN, PACKAGE, "*/*.svg", "desktop theme"
        )

    def test_readme_names_no_missing_desktop_theme_svg(self):
        named = set(_DESKTOP_TOKEN.findall(readme_text()))
        self.assertEqual(
            set(),
            named - shipped(PACKAGE, "*/*.svg"),
            "README names desktop theme SVGs that are not shipped",
        )

    def test_every_aurorae_svg_is_named_in_readme(self):
        self._assert_every_svg_is_named(
            _AURORAE_TOKEN, AURORAE_DIR, "*.svg", "Aurorae"
        )


class TestReadmeTextContainment(unittest.TestCase):
    """The README read refuses a symlink that escapes the repository.

    A checked-in symlink at ``README.md`` can point at a private file, and the
    SVG names parsed from it reach ``assertEqual`` diagnostics that echo the
    sets; the read must refuse such a path before it is opened rather than
    leak the private file's backticked tokens.
    """

    def test_rejects_a_symlink_that_escapes_the_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = tmp / "repo"
            root.mkdir()
            secret = tmp / "secret.md"
            secret.write_text(
                "`widgets/private.svg`\n", encoding="utf-8"
            )
            link = root / "README.md"
            link.symlink_to(secret)
            with mock.patch.object(sys.modules[__name__], "ROOT", root):
                with self.assertRaises(ValueError) as caught:
                    readme_text()
        self.assertIn(str(link), str(caught.exception))

    def test_allows_a_symlink_that_stays_within_the_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = tmp / "repo"
            root.mkdir()
            target = root / "actual-readme.md"
            target.write_text("`widgets/a.svg`\n", encoding="utf-8")
            link = root / "README.md"
            link.symlink_to(target)
            with mock.patch.object(sys.modules[__name__], "ROOT", root):
                self.assertEqual(readme_text(), "`widgets/a.svg`\n")


class TestReadmeTokenParsing(unittest.TestCase):
    """Pin the token rules on synthetic text."""

    def test_desktop_token_requires_a_widgets_or_dialogs_directory(self):
        text = "`widgets/a.svg` `dialogs/b.svg` `c.svg` `other/d.svg` `widgets/e/f.svg`"
        self.assertEqual(
            ["widgets/a.svg", "dialogs/b.svg"], _DESKTOP_TOKEN.findall(text)
        )

    def test_aurorae_token_is_a_bare_file_name(self):
        text = "`a.svg` `widgets/b.svg` `c.png`"
        self.assertEqual(["a.svg"], _AURORAE_TOKEN.findall(text))


if __name__ == "__main__":
    unittest.main()
