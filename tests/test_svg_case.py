"""The SVG parse-once mixin must refuse a symlink that escapes the repository.

Every desktop-theme widget test parses its shipped SVG through
``SvgCase.setUp``. A checked-in symlink at that SVG's path points at a private
file, and the widget assertions echo attribute values into a failing test's
diagnostic, so ``setUp`` must refuse the escape before ``ET.parse`` reads it.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import svg_case
from support.svg_case import SvgCase


class _Case(SvgCase):
    """A concrete `SvgCase` whose `SVG_PATH` the tests point at a symlink."""

    SVG_PATH = None


class TestSvgCaseContainment(unittest.TestCase):
    def test_rejects_a_symlink_that_escapes_the_repository(self):
        # A shipped SVG is contributor-supplied, and a checked-in symlink can
        # point at a private file; ET.parse reads the target and the widget
        # assertions echo attribute values into the diagnostic, so following
        # the symlink would leak that file's content. A path that resolves
        # outside the repository must be refused before it is opened.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = tmp / "repo"
            root.mkdir()
            secret = tmp / "secret.svg"
            secret.write_text(
                "<svg><path d='private'/></svg>\n", encoding="utf-8"
            )
            link = root / "viewitem.svg"
            link.symlink_to(secret)
            case = _Case()
            case.SVG_PATH = link
            with mock.patch.object(svg_case, "ROOT", root):
                with self.assertRaises(ValueError) as caught:
                    case.setUp()
        self.assertIn(str(link), str(caught.exception))

    def test_allows_a_symlink_that_stays_within_the_repository(self):
        # The guard must refuse only escapes, not a legitimate repository path
        # that happens to be reached through a symlink inside the repository.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = tmp / "repo"
            (root / "theme").mkdir(parents=True)
            target = root / "theme" / "viewitem.svg"
            target.write_text("<svg id='ok'/>\n", encoding="utf-8")
            link = root / "link.svg"
            link.symlink_to(target)
            case = _Case()
            case.SVG_PATH = link
            with mock.patch.object(svg_case, "ROOT", root):
                case.setUp()
        self.assertEqual(case.tree.getroot().get("id"), "ok")


if __name__ == "__main__":
    unittest.main()
