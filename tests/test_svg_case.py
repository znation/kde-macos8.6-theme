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
from support.symlink_fixtures import symlinked_repo


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
            root, link = symlinked_repo(
                tmp, "viewitem.svg", "<svg><path d='private'/></svg>\n"
            )
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
            root, link = symlinked_repo(
                tmp, "link.svg", "<svg id='ok'/>\n", target="theme/viewitem.svg"
            )
            case = _Case()
            case.SVG_PATH = link
            with mock.patch.object(svg_case, "ROOT", root):
                case.setUp()
        self.assertEqual(case.tree.getroot().get("id"), "ok")


class TestSvgCaseCache(unittest.TestCase):
    """An unchanged SVG parses once, but a changed or escaping one does not reuse."""

    def test_reuses_the_tree_of_an_unchanged_file(self):
        # Every widget test method parses its SVG in setUp, and the Kvantum
        # pixel classes parse the same file again; one parse per unchanged
        # path is the point of the cache.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "viewitem.svg"
            path.write_text("<svg id='cached'/>\n", encoding="utf-8")
            with mock.patch.object(
                svg_case.ET, "parse", wraps=svg_case.ET.parse
            ) as parse:
                first = svg_case.parse_svg(path)
                second = svg_case.parse_svg(path)
        self.assertIs(first, second)
        self.assertEqual(parse.call_count, 1)

    def test_rewritten_file_is_parsed_again(self):
        # The fingerprint must notice a file rewritten in place, or a test
        # that changes artwork would keep asserting against the old tree.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "viewitem.svg"
            path.write_text("<svg id='first'/>\n", encoding="utf-8")
            first = svg_case.parse_svg(path)
            path.write_text("<svg id='second'/>\n", encoding="utf-8")
            second = svg_case.parse_svg(path)
        self.assertIsNot(first, second)
        self.assertEqual(second.getroot().get("id"), "second")

    def test_a_cached_path_is_rechecked_before_its_tree_is_reused(self):
        # The containment guard runs before the cache lookup, so swapping a
        # parsed in-repo link for one that escapes the repository cannot serve
        # the cached tree of the private target.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = tmp / "repo"
            (root / "theme").mkdir(parents=True)
            real = root / "theme" / "viewitem.svg"
            real.write_text("<svg id='ok'/>\n", encoding="utf-8")
            link = root / "viewitem.svg"
            link.symlink_to(real)
            secret = tmp / "secret.svg"
            secret.write_text("<svg id='private'/>\n", encoding="utf-8")
            with mock.patch.object(svg_case, "ROOT", root):
                first = svg_case.parse_svg(link)
                link.unlink()
                link.symlink_to(secret)
                with self.assertRaises(ValueError):
                    svg_case.parse_svg(link)
        self.assertEqual(first.getroot().get("id"), "ok")


if __name__ == "__main__":
    unittest.main()
