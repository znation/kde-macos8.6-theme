"""Tests for tools/make_sheets.py: partial concatenation, validation, containment and the freshness gate."""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.cli_fixtures import run_main  # noqa: E402
from support.tmp_dir import make_tmp_dir
from tools import make_sheets  # noqa: E402
from tools.repo_root import ROOT  # noqa: E402

MAX_PARTIAL_LINES = 500


def write(path: Path, text: str) -> Path:
    """Create *path* with *text*, making its parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def firefox_header_problems(text: str) -> list[str]:
    """Return what is wrong with a Firefox ``000-header.css``, empty when it is sound.

    The header must open with a comment, hold exactly one comment, and end
    with that comment's closing ``*/`` line, so no rule follows it.
    """
    problems = []
    nonblank = [line for line in text.splitlines() if line.strip()]
    if not nonblank or not nonblank[0].startswith("/*"):
        problems.append("does not start with a comment")
    if text.count("/*") != 1 or text.count("*/") != 1:
        problems.append("does not hold exactly one comment")
    if not nonblank or not nonblank[-1].rstrip().endswith("*/"):
        problems.append("last non-blank line is not */")
    return problems


class TestShippedSheetIsFresh(unittest.TestCase):
    """The shipped sheets are the concatenation of their checked-in partials."""

    def test_each_shipped_sheet_equals_its_partials(self):
        for source, shipped in make_sheets.SHEETS:
            with self.subTest(source=source):
                expected = make_sheets.sheet_bytes(ROOT / source)
                actual = (ROOT / shipped).read_bytes()
                self.assertEqual(
                    actual,
                    expected,
                    f"{shipped} is out of date with its partials in {source}; "
                    "edit the partials and run `python3 tools/make_sheets.py`",
                )

    def test_every_gtk_partial_is_at_most_500_lines_and_starts_at_top_level(self):
        for family in ("gtk-3.0", "gtk-4.0"):
            source = ROOT / "theme/gtk/src" / family
            partials = sorted(source.glob("*.css"))
            self.assertTrue(partials, f"no GTK partials under {source}")
            for partial in partials:
                with self.subTest(partial=partial.relative_to(ROOT).as_posix()):
                    lines = partial.read_text(encoding="utf-8").splitlines()
                    self.assertLessEqual(len(lines), MAX_PARTIAL_LINES)
                    first = lines[0]
                    self.assertTrue(
                        first.startswith("/*") or (first and not first[0].isspace() and first[0] != "}"),
                        f"{partial.name} does not start at a top-level comment or rule",
                    )

    def test_every_firefox_partial_starts_at_top_level_and_is_capped_except_the_header(self):
        for sheet in ("userChrome", "userContent"):
            source = ROOT / "theme/firefox/src" / sheet
            partials = sorted(source.glob("*.css"))
            self.assertTrue(partials, f"no Firefox partials under {source}")
            for partial in partials:
                with self.subTest(partial=partial.relative_to(ROOT).as_posix()):
                    self._assert_partial_shape(partial)

    def _assert_partial_shape(self, partial):
        text = partial.read_text(encoding="utf-8")
        if partial.name == "000-header.css":
            self.assertEqual(firefox_header_problems(text), [])
            return
        lines = text.splitlines()
        self.assertLessEqual(len(lines), MAX_PARTIAL_LINES)
        first = lines[0]
        self.assertTrue(
            first.startswith("/*") or (first and not first[0].isspace() and first[0] != "}"),
            f"{partial.name} does not start at a top-level comment or rule",
        )

    def test_a_firefox_header_with_a_rule_after_its_comment_is_rejected(self):
        header = "/* sheet header */\n\ntooltip {\n  color: #000000 !important;\n}\n"
        problems = firefox_header_problems(header)
        self.assertTrue(problems, "a rule after the header comment must be reported")
        self.assertIn("last non-blank line is not */", problems)

    def test_a_firefox_header_holding_only_its_comment_is_accepted(self):
        self.assertEqual(firefox_header_problems("/* one\n   two */\n\n"), [])


class TestSheetBytes(unittest.TestCase):
    """sheet_bytes joins the partials in sorted order and validates them."""

    def setUp(self):
        self.root = make_tmp_dir(self)
        self.source = self.root / "src"
        self.source.mkdir()

    def test_joins_partials_in_sorted_order_regardless_of_creation_order(self):
        write(self.source / "020-b.css", "b {}\n")
        write(self.source / "000-a.css", "a {}\n")
        write(self.source / "010-mid.css", "m {}\n")
        self.assertEqual(make_sheets.sheet_bytes(self.source), b"a {}\nm {}\nb {}\n")

    def test_nothing_is_inserted_between_partials(self):
        write(self.source / "000-a.css", "a {\n}\n")
        write(self.source / "010-b.css", "b {}\n")
        self.assertEqual(make_sheets.sheet_bytes(self.source), b"a {\n}\nb {}\n")

    def test_ignores_files_that_are_not_css(self):
        write(self.source / "000-a.css", "a {}\n")
        write(self.source / "notes.txt", "not a partial\n")
        write(self.source / "README.md", "# not a partial\n")
        self.assertEqual(make_sheets.sheet_bytes(self.source), b"a {}\n")

    def test_a_directory_with_no_partial_is_rejected_naming_it(self):
        write(self.source / "notes.txt", "x\n")
        with self.assertRaises(ValueError) as caught:
            make_sheets.sheet_bytes(self.source)
        self.assertIn(str(self.source), str(caught.exception))

    def test_an_empty_partial_is_rejected_naming_it(self):
        write(self.source / "000-a.css", "a {}\n")
        write(self.source / "010-empty.css", "")
        with self.assertRaises(ValueError) as caught:
            make_sheets.sheet_bytes(self.source)
        self.assertIn("010-empty.css", str(caught.exception))

    def test_a_partial_without_a_trailing_newline_is_rejected_naming_it(self):
        write(self.source / "000-a.css", "a {}\n")
        write(self.source / "010-open.css", "b {}")
        with self.assertRaises(ValueError) as caught:
            make_sheets.sheet_bytes(self.source)
        self.assertIn("010-open.css", str(caught.exception))

    def test_a_dangling_css_symlink_is_rejected_naming_it_not_dropped(self):
        write(self.source / "000-a.css", "a {}\n")
        os.symlink(self.root / "nowhere.css", self.source / "010-gone.css")
        with self.assertRaises(ValueError) as caught:
            make_sheets.sheet_bytes(self.source)
        self.assertIn("010-gone.css", str(caught.exception))

    def test_a_directory_named_like_a_partial_is_rejected_naming_it(self):
        write(self.source / "000-a.css", "a {}\n")
        (self.source / "010-dir.css").mkdir()
        with self.assertRaises(ValueError) as caught:
            make_sheets.sheet_bytes(self.source)
        self.assertIn("010-dir.css", str(caught.exception))


class TestMain(unittest.TestCase):
    """The CLI validates every pair, then writes the shipped sheets."""

    def setUp(self):
        self.root = make_tmp_dir(self)
        self.source = self.root / "theme/src"
        self.shipped = self.root / "theme/out/gtk.css"
        patches = (
            mock.patch.object(make_sheets, "ROOT", self.root),
            mock.patch.object(
                make_sheets,
                "SHEETS",
                (("theme/src", "theme/out/gtk.css"),),
            ),
        )
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)

    def test_help_prints_usage_and_exits_zero(self):
        result = run_main(make_sheets.main, "make_sheets", ["--help"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage: make_sheets", result.stdout)

    def test_unknown_argument_is_a_usage_error_and_writes_nothing(self):
        write(self.source / "000-a.css", "a {}\n")
        result = run_main(make_sheets.main, "make_sheets", ["--bogus"])
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.shipped.exists())

    def test_writes_the_concatenation_to_the_shipped_sheet(self):
        write(self.source / "000-a.css", "a {}\n")
        write(self.source / "010-b.css", "b {}\n")
        self.assertEqual(make_sheets.main([]), 0)
        self.assertEqual(self.shipped.read_bytes(), b"a {}\nb {}\n")

    def test_a_bad_partial_writes_nothing_and_exits_2_naming_it(self):
        write(self.source / "000-a.css", "a {}\n")
        write(self.source / "010-open.css", "b {}")
        result = run_main(make_sheets.main, "make_sheets", [])
        self.assertEqual(result.returncode, 2)
        self.assertIn("010-open.css", result.stderr)
        self.assertFalse(self.shipped.exists())

    def test_a_sheet_directory_symlinked_outside_the_repository_is_refused(self):
        outside = make_tmp_dir(self)
        write(self.source / "000-a.css", "a {}\n")
        self.shipped.parent.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(outside, self.shipped.parent)
        result = run_main(make_sheets.main, "make_sheets", [])
        self.assertEqual(result.returncode, 2)
        self.assertFalse((outside / "gtk.css").exists())

    def test_rerun_rewrites_identical_bytes(self):
        write(self.source / "000-a.css", "a {}\n")
        make_sheets.main([])
        first = self.shipped.read_bytes()
        make_sheets.main([])
        self.assertEqual(self.shipped.read_bytes(), first)


if __name__ == "__main__":
    unittest.main()
