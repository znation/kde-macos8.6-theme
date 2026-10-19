"""Tests that desktop-theme provenance comments name their reference.

Three widget SVGs once justified a palette-only value by claiming the
reference set shows no such surface; the set does show it, so each header
comment must cite the screenshot its claim actually rests on instead of the
false phrase.
"""

from __future__ import annotations

import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from support import containment
from support.desktoptheme_paths import ARROWS_SVG, MENUBARITEM_SVG, VIEWITEM_SVG
from support.repo_root import ROOT


# The literal delimiters of an SVG/XML comment. The body is scanned with
# ``str.find`` rather than a ``<!--(.*?)-->`` regular expression: that lazy
# expression is quadratic when the closing ``-->`` is absent from a file with
# many ``<!--`` starts, because ``search`` retries at every start and rescans
# to the end of the file. A contributor-supplied artwork of a few hundred
# kilobytes would stall `make check` for minutes; finding the first opening
# and then the next closing is one left-to-right pass.
_COMMENT_OPEN = "<!--"
_COMMENT_CLOSE = "-->"


def header_comment(path):
    """Return the leading XML comment of an SVG file, or "" when absent.

    The SVG is contributor-supplied, and a checked-in symlink at its path can
    point at a private file; the returned comment is fed to ``assertIn``,
    whose failure message echoes it, so following such a symlink would leak
    that file's content into a failing test's diagnostic. A path that resolves
    outside the repository is refused before it is opened.
    """
    containment.require_within_repo(path, ROOT)
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    start = text.find(_COMMENT_OPEN)
    if start == -1:
        return ""
    start += len(_COMMENT_OPEN)
    end = text.find(_COMMENT_CLOSE, start)
    if end == -1:
        return ""
    return text[start:end]


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


class TestHeaderCommentContainment(unittest.TestCase):
    def test_rejects_a_symlink_that_escapes_the_repository(self):
        # A theme SVG is contributor-supplied, and a checked-in symlink can
        # point at a private file; the returned comment reaches assertIn,
        # whose failure message echoes it, so following the symlink would leak
        # that file's content into the test diagnostic. A path that resolves
        # outside the repository must be refused before it is opened.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = tmp / "repo"
            root.mkdir()
            secret = tmp / "secret.svg"
            secret.write_text("<!-- private -->\n", encoding="utf-8")
            link = root / "viewitem.svg"
            link.symlink_to(secret)
            with mock.patch.object(sys.modules[__name__], "ROOT", root):
                with self.assertRaises(ValueError) as caught:
                    header_comment(link)
        self.assertIn(str(link), str(caught.exception))

    def test_allows_a_symlink_that_stays_within_the_repository(self):
        # The guard must refuse only escapes, not a legitimate repository path
        # that happens to be reached through a symlink inside the repository.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = tmp / "repo"
            (root / "theme").mkdir(parents=True)
            target = root / "theme" / "viewitem.svg"
            target.write_text("<!-- ok -->\n", encoding="utf-8")
            link = root / "link.svg"
            link.symlink_to(target)
            with mock.patch.object(sys.modules[__name__], "ROOT", root):
                comment = header_comment(link)
        self.assertEqual(comment, " ok ")


class TestHeaderCommentScanning(unittest.TestCase):
    def test_header_comment_finishes_promptly_on_a_hostile_file(self):
        # A contributor-supplied SVG with many ``<!--`` starts and no closing
        # ``-->`` makes a ``<!--(.*?)-->`` regex rescan to the end of the file
        # at every start: quadratic time, so this ~24 KB file takes seconds
        # and a real artwork could stall `make check` for minutes. The scanner
        # must find no comment and finish well inside a generous bound.
        text = "<!--" * 6000
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "hostile.svg")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(text)
            started = time.monotonic()
            comment = header_comment(path)
            elapsed = time.monotonic() - started
        self.assertEqual(comment, "")
        self.assertLess(
            elapsed, 1.0, f"scanning {len(text)} bytes took {elapsed:.3f}s"
        )


if __name__ == "__main__":
    unittest.main()
