"""The SVG parse-once mixin must refuse a symlink that escapes the repository.

Every desktop-theme widget test parses its shipped SVG through
``SvgCase.setUp``. A checked-in symlink at that SVG's path points at a private
file, and the widget assertions echo attribute values into a failing test's
diagnostic, so ``setUp`` must refuse the escape before ``ET.parse`` reads it.
The parse input is contributor-supplied as well, so it is bounded at the
shared reader's cap and refuses an XML DTD or entity declaration.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import svg_case
from support.svg_case import SvgCase
from support.symlink_fixtures import symlinked_repo
from tools import containment as containment_impl


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


class TestSvgCaseInputLimits(unittest.TestCase):
    """A contributor-supplied SVG cannot make the parser use unbounded memory."""

    def test_refuses_an_oversize_svg_instead_of_loading_it_whole(self):
        # The shared read bounds every other contributor-file reader; the SVG
        # parser must use the same cap instead of handing expat a file of any
        # size. Before the fix a multi-gigabyte SVG was loaded whole.
        body = b"x" * (containment_impl._MAX_READ_BYTES + 1)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "huge.svg"
            path.write_bytes(
                b'<svg xmlns="http://www.w3.org/2000/svg">'
                + body
                + b"</svg>"
            )
            with self.assertRaises(ValueError) as caught:
                svg_case.parse_svg(path)
        self.assertIn(str(path), str(caught.exception))
        self.assertIn("larger than", str(caught.exception))

    def test_refuses_a_dtd_or_entity_before_the_parser_expands_it(self):
        # Expat expands internal entities, so a sub-megabyte DTD can allocate
        # many times its size. The declaration must be refused before the
        # parser sees it, including when a UTF-16 document hides it from an
        # ASCII byte scan.
        xml = (
            '<?xml version="1.0" encoding="{encoding}"?>\n'
            '<!DOCTYPE svg [<!ENTITY big "' + ("A" * 1000) + '">]>\n'
            '<svg xmlns="http://www.w3.org/2000/svg"><text>'
            + ("&big;" * 100)
            + "</text></svg>"
        )
        encoded = {
            "utf-8": xml.format(encoding="utf-8").encode("utf-8"),
            "utf-16-le": b"\xff\xfe"
            + xml.format(encoding="utf-16").encode("utf-16-le"),
            "utf-16-be": b"\xfe\xff"
            + xml.format(encoding="utf-16").encode("utf-16-be"),
        }
        for name, data in encoded.items():
            with self.subTest(encoding=name):
                with tempfile.TemporaryDirectory() as tmp:
                    path = Path(tmp) / "entity.svg"
                    path.write_bytes(data)
                    with self.assertRaises(ValueError) as caught:
                        svg_case.parse_svg(path)
                self.assertIn(str(path), str(caught.exception))
                self.assertIn("DTD or entity", str(caught.exception))


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

    def test_a_failed_read_is_not_cached(self):
        # The cache stores only a successfully parsed tree. A path whose read
        # is refused (here: past the shared contributor-file cap) must retry
        # on the next call instead of serving a stale entry, and the first
        # valid parse after the failure is cached like any other.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "viewitem.svg"
            # One byte past the shared contributor-file cap, the same shape
            # the input-limit test uses, so the read fails before the parser
            # runs.
            path.write_text(
                "<svg id='oversize'>" + "x" * (containment_impl._MAX_READ_BYTES)
                + "</svg>",
                encoding="utf-8",
            )
            with mock.patch.object(
                svg_case.ET, "parse", wraps=svg_case.ET.parse
            ) as parse:
                with self.assertRaises(ValueError):
                    svg_case.parse_svg(path)
                self.assertEqual(parse.call_count, 0)
                path.write_text("<svg id='fixed'/>", encoding="utf-8")
                first = svg_case.parse_svg(path)
                second = svg_case.parse_svg(path)
        self.assertIs(first, second)
        self.assertEqual(parse.call_count, 1)

    def test_a_refused_dtd_parse_is_not_cached(self):
        # Same promise on the parse arm: the DTD refusal happens before the
        # parser is involved, and nothing about the failed call is kept, so
        # reparsing after the file is fixed produces a cached tree.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "viewitem.svg"
            path.write_text(
                "<!DOCTYPE svg [<!ENTITY big 'x'>]><svg id='dtd'/>\n",
                encoding="utf-8",
            )
            with mock.patch.object(
                svg_case.ET, "parse", wraps=svg_case.ET.parse
            ) as parse:
                with self.assertRaises(ValueError) as caught:
                    svg_case.parse_svg(path)
                self.assertEqual(parse.call_count, 0)
                path.write_text("<svg id='fixed'/>", encoding="utf-8")
                first = svg_case.parse_svg(path)
                second = svg_case.parse_svg(path)
        self.assertIn("DTD or entity", str(caught.exception))
        self.assertIs(first, second)
        self.assertEqual(parse.call_count, 1)

    def test_a_file_that_cannot_be_statted_is_never_cached(self):
        # A fingerprint of None means the file cannot be statted, so the cache
        # must not key an entry on it: every call reparses, and once the file
        # can be statted again the next parse caches it normally.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "viewitem.svg"
            path.write_text("<svg id='nostat'/>", encoding="utf-8")
            with mock.patch.object(
                svg_case, "fingerprint_or_none", return_value=None
            ), mock.patch.object(
                svg_case.ET, "parse", wraps=svg_case.ET.parse
            ) as parse:
                first = svg_case.parse_svg(path)
                second = svg_case.parse_svg(path)
        self.assertIsNot(first, second)
        self.assertEqual(first.getroot().get("id"), "nostat")
        self.assertEqual(parse.call_count, 2)

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
