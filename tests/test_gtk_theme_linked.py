"""Validate the GTK 3 Platinum sheet's linked-group border pairs and corners.

This module owns the linked slice split out of the former GTK 3 controls suite:
the trailing border each linked member strips and the last member restores,
the end-field corners of a linked group, and the path-bar and stack-switcher
outlines that linked protection keeps. None of these tests renders; the sheet
rules are read from the stripped CSS through ``GtkSheetRuleCases``.
"""

import unittest
from pathlib import Path

from support.gtk_rule_cases import GtkSheetRuleCases
from support.platinum_palette import BLACK
from support.repo_root import ROOT

THEME_DIR = Path(ROOT) / "theme" / "gtk" / "org.macos8.desktop"
CSS = THEME_DIR / "gtk-3.0" / "gtk.css"


class TestGtkThemeLinked(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = CSS

    def test_linked_members_strip_their_trailing_border(self):
        for css_class, side in ((".linked:not(.vertical)", "border-right-style"),
                                (".linked.vertical", "border-bottom-style")):
            for member in ("button", "entry", "spinbutton:not(.vertical)",
                           "combobox > box > button.combo"):
                self.assert_rule(
                    f"{css_class} > {member}",
                    {side: "none"},
                )

    def test_linked_last_member_restores_the_border(self):
        for css_class, side in ((".linked:not(.vertical)", "border-right-style"),
                                (".linked.vertical", "border-bottom-style")):
            for member in ("button:last-child", "entry:last-child",
                           "spinbutton:not(.vertical):last-child",
                           "combobox > box > button.combo:last-child"):
                self.assert_rule(
                    f"{css_class} > {member}",
                    {side: "solid"},
                )

    LINKED_FIRST_LEFT = {
        "border-top-left-radius": "0",
        "border-bottom-left-radius": "0",
        "-gtk-outline-top-left-radius": "0",
        "-gtk-outline-bottom-left-radius": "0",
    }

    LINKED_LAST_RIGHT = {
        "border-top-right-radius": "0",
        "border-bottom-right-radius": "0",
        "-gtk-outline-top-right-radius": "0",
        "-gtk-outline-bottom-right-radius": "0",
    }

    LINKED_ONLY = {
        "border-radius": "0",
        "-gtk-outline-radius": "0",
    }

    LINKED_FIRST_TOP = {
        "border-top-left-radius": "0",
        "border-top-right-radius": "0",
        "-gtk-outline-top-left-radius": "0",
        "-gtk-outline-top-right-radius": "0",
    }

    LINKED_LAST_BOTTOM = {
        "border-bottom-left-radius": "0",
        "border-bottom-right-radius": "0",
        "-gtk-outline-bottom-left-radius": "0",
        "-gtk-outline-bottom-right-radius": "0",
    }

    LINKED_HORIZONTAL_FIRST = (
        ".linked:not(.vertical) > combobox:first-child > box > button.combo",
        "combobox.linked button:nth-child(2):dir(rtl)",
        "filechooser .path-bar.linked > button:dir(rtl):last-child",
        "filechooser .path-bar.linked > button:dir(ltr):first-child",
        ".linked:not(.vertical) > spinbutton:first-child:not(.vertical)",
        ".linked:not(.vertical) > entry:first-child",
        ".inline-toolbar button:first-child",
        ".linked > button:first-child",
        "toolbar.inline-toolbar toolbutton:first-child > button.flat",
    )

    LINKED_HORIZONTAL_LAST = (
        ".linked:not(.vertical) > combobox:last-child > box > button.combo",
        "combobox.linked button:nth-child(2):dir(ltr)",
        "filechooser .path-bar.linked > button:dir(rtl):first-child",
        "filechooser .path-bar.linked > button:dir(ltr):last-child",
        ".linked:not(.vertical) > spinbutton:last-child:not(.vertical)",
        ".linked:not(.vertical) > entry:last-child",
        ".inline-toolbar button:last-child",
        ".linked > button:last-child",
        "toolbar.inline-toolbar toolbutton:last-child > button.flat",
    )

    LINKED_HORIZONTAL_ONLY = (
        ".linked:not(.vertical) > combobox:only-child > box > button.combo",
        "filechooser .path-bar.linked > button:only-child",
        ".linked:not(.vertical) > spinbutton:only-child:not(.vertical)",
        ".linked:not(.vertical) > entry:only-child",
        ".inline-toolbar button:only-child",
        ".linked > button:only-child",
        "toolbar.inline-toolbar toolbutton:only-child > button.flat",
    )

    LINKED_VERTICAL_FIRST = (
        ".linked.vertical > combobox:first-child > box > button.combo",
        ".linked.vertical > spinbutton:first-child:not(.vertical)",
        ".linked.vertical > entry:first-child",
        ".linked.vertical > button:first-child",
    )

    LINKED_VERTICAL_LAST = (
        ".linked.vertical > combobox:last-child > box > button.combo",
        ".linked.vertical > spinbutton:last-child:not(.vertical)",
        ".linked.vertical > entry:last-child",
        ".linked.vertical > button:last-child",
    )

    LINKED_VERTICAL_ONLY = (
        ".linked.vertical > combobox:only-child > box > button.combo",
        ".linked.vertical > spinbutton:only-child:not(.vertical)",
        ".linked.vertical > entry:only-child",
        ".linked.vertical > button:only-child",
    )

    def test_linked_end_field_corners(self):
        """Stock's linked-field end corners square in the shipped sheet.

        The toolkit resource rounds six linked arms — the horizontal
        first, last and only member arms and the vertical trio — cutting
        each linked group's two ends 5px and pairing matching
        `-gtk-outline-` focus-ring halves into the same arms. The sheet
        restates all thirty-seven byte-equal spellings in stock's own
        grouping, each carrying only its zeroed radius declarations.
        Three spellings coincide with the existing border-sharing groups,
        so their parsed dictionaries merge the carried border-style and
        the spelling counts twice — once as the existing group's member,
        once in the restating group.
        """
        expected = {}
        for selector in self.LINKED_HORIZONTAL_FIRST:
            expected[selector] = dict(self.LINKED_FIRST_LEFT)
        for selector in self.LINKED_HORIZONTAL_LAST:
            expected[selector] = dict(self.LINKED_LAST_RIGHT)
        expected[".linked:not(.vertical) > entry:last-child"] = {
            "border-right-style": "solid", **self.LINKED_LAST_RIGHT}
        for selector in self.LINKED_HORIZONTAL_ONLY:
            expected[selector] = dict(self.LINKED_ONLY)
        for selector in self.LINKED_VERTICAL_FIRST:
            expected[selector] = dict(self.LINKED_FIRST_TOP)
        for selector in self.LINKED_VERTICAL_LAST:
            expected[selector] = dict(self.LINKED_LAST_BOTTOM)
        for selector in (".linked.vertical > entry:last-child",
                         ".linked.vertical > button:last-child"):
            expected[selector] = {
                "border-bottom-style": "solid", **self.LINKED_LAST_BOTTOM}
        for selector in self.LINKED_VERTICAL_ONLY:
            expected[selector] = dict(self.LINKED_ONLY)
        self.assertEqual(len(expected), 37)

        merged = (".linked:not(.vertical) > entry:last-child",
                  ".linked.vertical > entry:last-child",
                  ".linked.vertical > button:last-child")
        self.assert_rule_group(
            {s: r for s, r in expected.items() if s not in merged})
        for selector in merged:
            with self.subTest(selector=selector):
                # The spelling is a member of the existing border-sharing
                # group and of this entry's restating group: the parsed
                # rules merge the border-style with the radius longhands,
                # so the whole dictionary pins both — a dropped group,
                # a stray declaration or a third spelling fails.
                self.assertEqual(self.selectors.count(selector), 2,
                                 selector)
                self.assertEqual(self.rules[selector], expected[selector],
                                 selector)

        # No stray member of the families the restatements touch and no
        # state twin stays stock: every toolbutton, combobox.linked and
        # filechooser-radius spelling this entry adds is the whole set.
        self.assertEqual(
            {s for s in self.rules if "toolbutton" in s},
            {"toolbar.inline-toolbar toolbutton:first-child > button.flat",
             "toolbar.inline-toolbar toolbutton:last-child > button.flat",
             "toolbar.inline-toolbar toolbutton:only-child > button.flat"},
        )
        self.assertEqual(
            {s for s in self.rules if "combobox.linked" in s},
            {"combobox.linked button:nth-child(2):dir(rtl)",
             "combobox.linked button:nth-child(2):dir(ltr)"},
        )
        self.assertEqual(
            {s for s in self.rules if "filechooser" in s},
            {"filechooser .path-bar.linked > button:dir(rtl):last-child",
             "filechooser .path-bar.linked > button:dir(ltr):first-child",
             "filechooser .path-bar.linked > button:dir(rtl):first-child",
             "filechooser .path-bar.linked > button:dir(ltr):last-child",
             "filechooser .path-bar.linked > button:only-child"},
        )

        # Every restatement parses after the sheet's existing tail group.
        tail = self.selectors.index("popover.emoji-picker .emoji :hover")
        for selector in expected:
            with self.subTest(selector=selector):
                if selector in merged:
                    # The merged spelling's existing group sits mid-sheet;
                    # its restatement — the second listing — follows.
                    self.assertGreater(self.selectors.index(selector, tail
                                                            + 1), tail,
                                       selector)
                else:
                    self.assertGreater(self.selectors.index(selector), tail,
                                       selector)

    def test_linked_protection_keeps_the_path_bar_and_stack_switcher_outlines(self):
        self.assert_rule(
            ".path-bar.linked > button:not(:last-child)",
            {
                "border-right-style": "solid",
                "border-bottom-style": "solid",
            },
        )
        self.assert_rule(
            "stackswitcher.linked > button:not(:last-child)",
            {
                "border-right-style": "solid",
                "border-bottom-style": "solid",
            },
        )
        self.assert_rule(
            ".path-bar > button",
            {
                "border": f"1px solid {BLACK}",
            },
        )


if __name__ == "__main__":
    unittest.main()
