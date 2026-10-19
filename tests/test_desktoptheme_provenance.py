"""Tests that desktop-theme provenance comments name their reference.

Three widget SVGs once justified a palette-only value by claiming the
reference set shows no such surface; the set does show it, so each header
comment must cite the screenshot its claim actually rests on instead of the
false phrase.
"""

from __future__ import annotations

import os
import re
import unittest

from support.desktoptheme_paths import ARROWS_SVG, MENUBARITEM_SVG, VIEWITEM_SVG


HEADER_COMMENT = re.compile(r"<!--(.*?)-->", re.DOTALL)


def header_comment(path):
    """Return the leading XML comment of an SVG file, or "" when absent."""
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    match = HEADER_COMMENT.search(text)
    return match.group(1) if match else ""


class TestProvenance(unittest.TestCase):
    # (SVG path, reference filename the comment must cite, false phrase it
    # must not contain).
    CASES = (
        (VIEWITEM_SVG, "desktop_archiveorg8.6hd.png", "no open-menu screenshot"),
        (MENUBARITEM_SVG, "desktop_archiveorg8.6hd.png", "no menu-open screenshot"),
        (
            ARROWS_SVG,
            "systeminfo_betawiki.png",
            "no reference screenshot shows a combo box",
        ),
    )

    def test_provenance_comments_cite_their_reference(self):
        for path, required, forbidden in self.CASES:
            with self.subTest(svg=os.path.basename(path)):
                comment = header_comment(path)
                self.assertIn(required, comment)
                self.assertNotIn(forbidden, comment)


if __name__ == "__main__":
    unittest.main()
