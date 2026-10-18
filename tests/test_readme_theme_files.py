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
import unittest

from support.desktoptheme_paths import PACKAGE
from support.theme_install import ROOT

_DESKTOP_TOKEN = re.compile(r"`((?:widgets|dialogs)/[^`/]+\.svg)`")
_AURORAE_TOKEN = re.compile(r"`([^`/]+\.svg)`")
AURORAE_DIR = os.path.join(ROOT, "theme", "aurorae", "themes", "org.macos8.desktop")


def readme_text():
    with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as handle:
        return handle.read()


def shipped(package, pattern):
    """Paths of *package*'s SVGs matching *pattern*, relative to *package*."""
    return {
        os.path.relpath(path, package)
        for path in glob.glob(os.path.join(package, pattern), recursive=True)
    }


class TestReadmeThemeFiles(unittest.TestCase):
    def test_every_desktop_theme_svg_is_named_in_readme(self):
        named = set(_DESKTOP_TOKEN.findall(readme_text()))
        on_disk = shipped(PACKAGE, "*/*.svg")
        self.assertTrue(on_disk, "no desktop theme SVGs found under " + PACKAGE)
        self.assertEqual(
            set(),
            on_disk - named,
            "desktop theme SVGs README does not name in backticks",
        )

    def test_readme_names_no_missing_desktop_theme_svg(self):
        named = set(_DESKTOP_TOKEN.findall(readme_text()))
        self.assertEqual(
            set(),
            named - shipped(PACKAGE, "*/*.svg"),
            "README names desktop theme SVGs that are not shipped",
        )

    def test_every_aurorae_svg_is_named_in_readme(self):
        named = set(_AURORAE_TOKEN.findall(readme_text()))
        on_disk = shipped(AURORAE_DIR, "*.svg")
        self.assertTrue(on_disk, "no Aurorae SVGs found under " + AURORAE_DIR)
        self.assertEqual(
            set(),
            on_disk - named,
            "Aurorae SVGs README does not name in backticks",
        )


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
