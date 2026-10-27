"""Tests for ``tools/firefox_user_js.py`` -- the marker-delimited preference block.

The transform is pure text in and out, so these cases need no profile
directory. The install that writes the block into a real ``user.js`` is pinned
in ``tests/test_install_firefox.py``.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from support import containment
from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from test_firefox_content_theme import MARKER as CONTENT_MARKER
from tools import firefox_user_js, install_firefox

SHEET_PATH = Path(repo_root.ROOT) / install_firefox.SHEET
CONTENT_SHEET_PATH = Path(repo_root.ROOT) / install_firefox.CONTENT_SHEET

class TestUserJs(unittest.TestCase):
    def test_shipped_marker_and_preference_are_pinned(self):
        self.assertEqual(
            "/* org.macos8.desktop Firefox chrome, standalone userChrome.css",
            install_firefox.CSS_MARKER,
        )
        self.assertEqual(
            "/* org.macos8.desktop Firefox content, standalone userContent.css",
            install_firefox.CONTENT_CSS_MARKER,
        )
        self.assertEqual(CONTENT_MARKER, install_firefox.CONTENT_CSS_MARKER)
        self.assertEqual(
            "// org.macos8.desktop Firefox Platinum userChrome",
            firefox_user_js.USER_JS_MARKER,
        )
        self.assertEqual(
            'user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);',
            firefox_user_js.PREF_LINE,
        )
        for path, marker in (
            (SHEET_PATH, install_firefox.CSS_MARKER),
            (CONTENT_SHEET_PATH, install_firefox.CONTENT_CSS_MARKER),
        ):
            with self.subTest(sheet=path.name):
                self.assertTrue(path.is_file())
                first_line = containment.read_bytes(
                    path, repo_root.ROOT
                ).decode("utf-8").splitlines()[0]
                self.assertEqual(marker, first_line)

    def test_new_file_gets_one_marker_and_pref_block(self):
        self.assertEqual(
            firefox_user_js.USER_JS_MARKER
            + "\n"
            + firefox_user_js.PREF_LINE
            + "\n",
            firefox_user_js.set_user_js(""),
        )

    def test_repeat_install_leaves_exactly_one_block(self):
        once = firefox_user_js.set_user_js("")
        self.assertEqual(once, firefox_user_js.set_user_js(once))
        self.assertEqual(1, once.count(firefox_user_js.USER_JS_MARKER))
        self.assertEqual(1, once.count(firefox_user_js.PREF_LINE))

    def test_foreign_lines_keep_their_crlf_and_terminated_last_line(self):
        foreign = (
            'user_pref("browser.tabs.inTitlebar", 0);\r\n'
            'user_pref("browser.startup.homepage", "about:blank");'
        )
        self.assertEqual(
            foreign
            + "\r\n"
            + firefox_user_js.USER_JS_MARKER
            + "\r\n"
            + firefox_user_js.PREF_LINE
            + "\r\n",
            firefox_user_js.set_user_js(foreign),
        )

    def test_foreign_setting_of_the_same_pref_survives_before_our_line(self):
        foreign = firefox_user_js.PREF_LINE + "\n"
        updated = firefox_user_js.set_user_js(foreign)
        self.assertEqual(2, updated.count(firefox_user_js.PREF_LINE))
        self.assertTrue(updated.startswith(foreign))
        self.assertTrue(
            updated.endswith(
                firefox_user_js.USER_JS_MARKER
                + "\n"
                + firefox_user_js.PREF_LINE
                + "\n"
            )
        )

    def test_remove_deletes_only_the_marker_pair(self):
        foreign = 'user_pref("a", 1);\n'
        text = (
            foreign
            + firefox_user_js.USER_JS_MARKER
            + "\n"
            + firefox_user_js.PREF_LINE
            + "\n"
        )
        self.assertEqual(foreign, firefox_user_js.remove_user_js(text))

    def test_remove_leaves_a_foreign_pref_and_missing_final_newline(self):
        foreign = firefox_user_js.PREF_LINE + "\nuser_pref(\"last\", 1);"
        self.assertEqual(foreign, firefox_user_js.remove_user_js(foreign))
        self.assertEqual(
            'user_pref("last", 1);',
            firefox_user_js.remove_user_js('user_pref("last", 1);'),
        )

    def test_a_bom_before_our_marker_still_matches_the_block(self):
        # A UTF-8 BOM is valid at the start of a JavaScript file and some
        # editors add one. It must not hide our marker block: a repeat install
        # must not append a second copy, and a removal must delete the pair.
        block = (
            firefox_user_js.USER_JS_MARKER
            + "\n"
            + firefox_user_js.PREF_LINE
            + "\n"
        )
        text = "\ufeff" + block
        self.assertEqual(block, firefox_user_js.set_user_js(text))
        self.assertEqual("", firefox_user_js.remove_user_js(text))

    def test_a_bom_before_a_foreign_first_line_stays(self):
        # Only a marker line ignores the BOM; a foreign first line keeps it
        # byte for byte through an install and a removal.
        foreign = '\ufeffuser_pref("a", 1);\n'
        updated = firefox_user_js.set_user_js(foreign)
        self.assertTrue(updated.startswith(foreign))
        self.assertEqual(foreign, firefox_user_js.remove_user_js(foreign))

    def test_bom_tolerance_is_limited_to_one_bom_on_the_first_line(self):
        marker = firefox_user_js.USER_JS_MARKER
        pref = firefox_user_js.PREF_LINE
        block = marker + "\r\n" + pref + "\r\n"
        for foreign in (
            '// foreign header\r\n\ufeff' + block,
            '\ufeff\ufeff' + block,
        ):
            with self.subTest(foreign=foreign):
                # These are foreign marker lookalikes, so neither their
                # comments nor the preference following them may be deleted.
                self.assertEqual(foreign, firefox_user_js.remove_user_js(foreign))
                installed = firefox_user_js.set_user_js(foreign)
                self.assertEqual(foreign + block, installed)
                self.assertEqual(installed, firefox_user_js.set_user_js(installed))
                self.assertEqual(foreign, firefox_user_js.remove_user_js(installed))

    def test_first_line_stops_at_cr_lf_or_crlf_only(self):
        # The installer decides whether a file is ours from this line, so it
        # must end at the same breaks the block editor uses and keep a BOM.
        first_line = firefox_user_js.first_line
        self.assertEqual("", first_line(""))
        self.assertEqual("", first_line("\nrest"))
        self.assertEqual("a", first_line("a"))
        self.assertEqual("a", first_line("a\nb"))
        self.assertEqual("a", first_line("a\r\nb"))
        self.assertEqual("a", first_line("a\rb"))
        self.assertEqual("a\x0bb c", first_line("a\x0bb c\nd"))
        self.assertEqual("\ufeffa", first_line("\ufeffa\nb"))

    def test_remove_is_repeatable_and_keeps_crlf(self):
        foreign = 'user_pref("a", 1);\r\n'
        text = (
            foreign
            + firefox_user_js.USER_JS_MARKER
            + "\r\n"
            + firefox_user_js.PREF_LINE
            + "\r\n"
        )
        once = firefox_user_js.remove_user_js(text)
        self.assertEqual(foreign, once)
        self.assertEqual(once, firefox_user_js.remove_user_js(once))

    def test_remove_drops_a_marker_with_no_pref_line_after_it(self):
        # The block is exactly the marker plus the pref line immediately after
        # it, so a marker whose next line is foreign must not take that line
        # with it: losing a user preference is worse than leaving a comment.
        foreign = 'user_pref("a", 1);\n'
        following = 'user_pref("b", 2);\n'
        text = foreign + firefox_user_js.USER_JS_MARKER + "\n" + following
        self.assertEqual(foreign + following, firefox_user_js.remove_user_js(text))

    def test_install_removes_every_earlier_block(self):
        # A hand-edited user.js can hold two copies of our block; the docstring
        # promises exactly one at the end, and every foreign line survives
        # once, whatever the number of earlier pairs.
        foreign = 'user_pref("a", 1);\n'
        block = (
            firefox_user_js.USER_JS_MARKER
            + "\n"
            + firefox_user_js.PREF_LINE
            + "\n"
        )
        updated = firefox_user_js.set_user_js(foreign + block + foreign + block)
        self.assertEqual(foreign + foreign + block, updated)

    def test_dominant_ending_tie_keeps_the_earliest_ending(self):
        # One CRLF and one LF line tie; the block must use the ending the file
        # opened with rather than sorting or taking the last one seen, and the
        # foreign lines must keep their own endings either way.
        foreign = 'user_pref("a", 1);\r\nuser_pref("b", 2);\n'
        self.assertEqual(
            foreign
            + firefox_user_js.USER_JS_MARKER
            + "\r\n"
            + firefox_user_js.PREF_LINE
            + "\r\n",
            firefox_user_js.set_user_js(foreign),
        )

    def test_foreign_lines_keep_lone_cr_endings(self):
        # A user.js written with classic-Mac lone-CR line endings keeps every
        # foreign line's CR, the unterminated last line gains the file's own
        # ending, and the appended block uses CR too.
        foreign = 'user_pref("a", 1);\ruser_pref("b", 2);'
        self.assertEqual(
            foreign
            + "\r"
            + firefox_user_js.USER_JS_MARKER
            + "\r"
            + firefox_user_js.PREF_LINE
            + "\r",
            firefox_user_js.set_user_js(foreign),
        )

    def test_remove_keeps_lone_cr_endings(self):
        foreign = 'user_pref("a", 1);\r'
        text = (
            foreign
            + firefox_user_js.USER_JS_MARKER
            + "\r"
            + firefox_user_js.PREF_LINE
            + "\r"
        )
        self.assertEqual(foreign, firefox_user_js.remove_user_js(text))
        self.assertEqual(foreign, firefox_user_js.remove_user_js(foreign))

    def test_only_cr_and_lf_end_a_line(self):
        # A foreign line carrying another Unicode line separator (VT, FF,
        # U+0085 or U+2028) is content, not an ending: splitting there would
        # move our block into the middle of that line and a removal could
        # leave an extra line break behind.
        foreign = 'user_pref("a", "x\u2028y\u0085z\v\f");'
        self.assertEqual(
            foreign
            + "\n"
            + firefox_user_js.USER_JS_MARKER
            + "\n"
            + firefox_user_js.PREF_LINE
            + "\n",
            firefox_user_js.set_user_js(foreign),
        )
        self.assertEqual(foreign + "\n", firefox_user_js.remove_user_js(foreign + "\n"))


if __name__ == "__main__":
    unittest.main()
