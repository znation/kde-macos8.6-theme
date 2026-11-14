"""Validate the GTK 3 Platinum sheet's entry fields and their embedded parts.

This module owns the entry slice split out of ``tests/test_gtk_theme_controls.py``:
the entry's progress strip (the declaration and the drawn two-pixel strip), the
focus outline, the error and warning colour classes, the plain state faces, the
embedded icon inks and the tag chip faces. The declaration tests read the
stripped CSS through ``GtkSheetRuleCases``; the drawn-strip test renders with a
real GTK 3 in a child interpreter (see ``_run_gtk_child``), so the suite process
itself imports no GTK.
"""

import unittest
from pathlib import Path

from support.gtk_child_probe import (
    _GTK3_PIXEL_HEAD,
    _GTK3_SHEET_AND_WINDOW,
    _GTK3_SHEET_PROLOGUE,
    Gtk3ChildProbeCases,
)
from support.gtk_css import strip_comments
from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import (
    DISABLED_TEXT,
    ENTRY_FIELD,
    ENTRY_PROGRESS,
)
from support.platinum_palette import (
    BLACK,
    SELECTION,
    WHITE,
)
from support.repo_root import ROOT

THEME_DIR = Path(ROOT) / "theme" / "gtk" / "org.macos8.desktop"
CSS = THEME_DIR / "gtk-3.0" / "gtk.css"


class TestGtkThemeEntry(Gtk3ChildProbeCases, GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = CSS

    def test_entry_progress(self):
        self.assert_rule("entry progress", ENTRY_PROGRESS)

    def test_entry_progress_draws_a_two_pixel_strip(self):
        # GTK 3 ignores min-height on this node, so pin the drawn pixels.
        # The GTK work runs in a child interpreter; see _run_gtk_child for
        # why it never runs in this one.
        program = (
            _GTK3_SHEET_PROLOGUE
            + _GTK3_SHEET_AND_WINDOW
            + '''entry = Gtk.Entry()
entry.set_progress_fraction(0.5)
window.add(entry)
window.set_default_size(120, 21)
'''
            + _GTK3_PIXEL_HEAD
            + '''bottom = pixbuf.get_height() - 1
assert at(90, bottom) == "#000000", at(90, bottom)
strip = [at(30, bottom - d) for d in (1, 2)]
assert strip == ["#CCCCFF"] * 2, strip
assert at(30, bottom - 3) == "#FFFFFF", at(30, bottom - 3)
assert at(90, bottom - 1) == "#FFFFFF", at(90, bottom - 1)
print("entry progress: the 0.5 fraction leaves the #CCCCFF strip one and two pixels above the bottom border, #FFFFFF below it")
'''
        )
        self._run_gtk_child(program, str(CSS))

    def test_entry_focus_outline(self):
        self.assert_dotted_focus_outline("entry:focus")

    def test_entry_error_warning_colour_classes(self):
        # The existing entry policy takes no colour class: the sheet
        # restates the stock colour-class arms with byte-equal twins
        # declaring the existing faces, so an entry, spin-button field or
        # label carrying the `error` or `warning` class paints the existing
        # recipe instead of the toolkit resource's red or orange. The
        # label's disabled twins both take the existing insensitive grey
        # with no backdrop dim (the existing sheet carries no label backdrop
        # dim, matching the existing GTK 4 label colour-class record); the
        # selection arms restate only the fill, the existing element-level
        # selection groups owning the ink; the focus arms restate only the
        # etch and the border colour, the existing dotted outlines cascading
        # unchanged; and stock's late colour-only repeat of the error
        # field base arm needs no twin of its own.
        expected = {
            "label.error": {"color": BLACK},
            "label.error:disabled": DISABLED_TEXT,
            "label.error:disabled:backdrop": DISABLED_TEXT,
            "spinbutton.error:not(.vertical)": {
                "color": BLACK,
                "border-color": BLACK,
            },
            "entry.error": {"color": BLACK, "border-color": BLACK},
            "spinbutton.error:focus:not(.vertical)": {
                "box-shadow": ENTRY_FIELD["box-shadow"],
                "border-color": BLACK,
            },
            "entry.error:focus": {
                "box-shadow": ENTRY_FIELD["box-shadow"],
                "border-color": BLACK,
            },
            "spinbutton.error:not(.vertical) selection": {
                "background-color": SELECTION,
            },
            "entry.error selection": {"background-color": SELECTION},
            "spinbutton.warning:not(.vertical)": {
                "color": BLACK,
                "border-color": BLACK,
            },
            "entry.warning": {"color": BLACK, "border-color": BLACK},
            "spinbutton.warning:focus:not(.vertical)": {
                "box-shadow": ENTRY_FIELD["box-shadow"],
                "border-color": BLACK,
            },
            "entry.warning:focus": {
                "box-shadow": ENTRY_FIELD["box-shadow"],
                "border-color": BLACK,
            },
            "spinbutton.warning:not(.vertical) selection": {
                "background-color": SELECTION,
            },
            "entry.warning selection": {"background-color": SELECTION},
        }
        self.assert_rule_group(expected)
        # No other error or warning selector exists in the sheet: the
        # family sweep kills renamed, dropped and stray class spellings
        # alike.
        self.assertEqual(
            {s for s in self.rules if ".error" in s or ".warning" in s},
            set(expected),
        )
        # Every restated spelling sits after the existing field rule, so the
        # equal-specificity ties resolve the existing face's way under either
        # cascade reading the existing records accept.
        uncommented = strip_comments(self.css)
        anchor = uncommented.index("entry, spinbutton:not(.vertical) {")
        for selector in expected:
            self.assertEqual(self.selectors.count(selector), 1, selector)
            self.assertGreater(uncommented.index(selector), anchor, selector)

    def test_entry_state_faces(self):
        # The toolkit resource's own plain entry and spin-button state arms
        # (focus, disabled, backdrop, backdrop-disabled, drop-active, the
        # vertical spin button's colour-only twins, the nested horizontal
        # spin-button field and the treeview editable cell) otherwise paint
        # foreign faces on the existing spellings: an accent ring on focus,
        # greige borders and off-white fills with no etch on the insensitive
        # and unfocused-window states, a green drag rim, an accent border on
        # focused editable cells, and a duplicate existing etch on the nested
        # field the resource itself clears. Each rule restates its stock
        # twin's declarations with the existing faces (the field etch and hard
        # border, the insensitive grey, the no-motion backdrop policy the
        # existing button:backdrop record states) in place of the foreign
        # inks, so the later user-sheet spellings win every equal-specificity
        # tie.
        etch = ENTRY_FIELD["box-shadow"]
        expected = {
            "entry:focus": {
                "outline": "1px dotted #000000",
                "outline-offset": "0",
                "-gtk-outline-radius": "0",
                "box-shadow": etch,
                "border-color": BLACK,
            },
            "spinbutton:focus:not(.vertical)": {
                "outline": "1px dotted #000000",
                "outline-offset": "0",
                "-gtk-outline-radius": "0",
                "box-shadow": etch,
                "border-color": BLACK,
            },
            "entry:disabled": {
                "color": DISABLED_TEXT["color"],
                "border-color": BLACK,
                "background-color": WHITE,
                "box-shadow": etch,
            },
            "spinbutton:disabled:not(.vertical)": {
                "color": DISABLED_TEXT["color"],
                "border-color": BLACK,
                "background-color": WHITE,
                "box-shadow": etch,
            },
            "entry:backdrop": {
                "color": BLACK,
                "border-color": BLACK,
                "background-color": WHITE,
                "box-shadow": etch,
                "transition": "none",
            },
            "spinbutton:backdrop:not(.vertical)": {
                "color": BLACK,
                "border-color": BLACK,
                "background-color": WHITE,
                "box-shadow": etch,
                "transition": "none",
            },
            "entry:backdrop:disabled": {
                "color": DISABLED_TEXT["color"],
                "border-color": BLACK,
                "background-color": WHITE,
                "box-shadow": etch,
            },
            "spinbutton:backdrop:disabled:not(.vertical)": {
                "color": DISABLED_TEXT["color"],
                "border-color": BLACK,
                "background-color": WHITE,
                "box-shadow": etch,
            },
            "spinbutton.vertical:disabled": {
                "color": DISABLED_TEXT["color"],
            },
            "spinbutton.vertical:backdrop:disabled": {
                "color": DISABLED_TEXT["color"],
            },
            "spinbutton:drop(active):not(.vertical)": {
                "border-color": BLACK,
                "box-shadow": etch,
            },
            "entry:drop(active):focus": {
                "border-color": BLACK,
                "box-shadow": etch,
            },
            "entry:drop(active)": {
                "border-color": BLACK,
                "box-shadow": etch,
            },
            "spinbutton.vertical:drop(active)": {
                "border-color": "transparent",
                "box-shadow": "none",
            },
            ".osd spinbutton:not(.vertical) entry": {
                "min-width": "28px",
                "margin": "0",
                "background": "none",
                "background-color": "transparent",
                "border": "none",
                "border-radius": "0",
                "box-shadow": "none",
            },
            "spinbutton:not(.vertical) entry": {
                "min-width": "28px",
                "margin": "0",
                "background": "none",
                "background-color": "transparent",
                "border": "none",
                "border-radius": "0",
                "box-shadow": "none",
            },
            "spinbutton:not(.vertical) entry:backdrop:disabled": {
                "background-color": "transparent",
            },
            "treeview entry": {
                "background-color": WHITE,
                "background-image": "none",
                "border-radius": "0",
            },
            "treeview entry.flat": {
                "background-color": WHITE,
                "background-image": "none",
                "border-radius": "0",
            },
            "treeview entry:focus:dir(rtl)": {
                "background-color": WHITE,
                "transition-property": "none",
            },
            "treeview entry:focus:dir(ltr)": {
                "background-color": WHITE,
                "transition-property": "none",
            },
            "treeview entry.flat:focus": {
                "border-color": BLACK,
            },
            "treeview entry:focus": {
                "border-color": BLACK,
            },
        }
        # Three spellings pre-exist in the existing sheet — the existing focus
        # rules and the existing label/entry/spin-button insensitive group —
        # so each lands with exactly two declarations in the sheet (count 2)
        # and the rest with exactly one.
        existing_counts = {
            "entry:focus": 2,
            "spinbutton:focus:not(.vertical)": 2,
            "entry:disabled": 2,
        }
        for selector, declarations in expected.items():
            self.assertEqual(
                self.selectors.count(selector),
                existing_counts.get(selector, 1),
                selector,
            )
            self.assertEqual(self.rules[selector], declarations, selector)
        # No other unlinked entry or spin-button drop-active selector exists:
        # the family sweep kills renamed, stray and linked leftovers alike.
        self.assertEqual(
            {
                s
                for s in self.rules
                if ":drop(active)" in s
                and ("entry" in s or "spinbutton" in s)
                and ".linked" not in s
            },
            {
                "spinbutton:drop(active):not(.vertical)",
                "entry:drop(active):focus",
                "entry:drop(active)",
                "spinbutton.vertical:drop(active)",
            },
        )
        # Every restated spelling sits after the existing field rule, so the
        # equal-specificity ties resolve the existing face's way under either
        # cascade reading the existing records accept.
        uncommented = strip_comments(self.css)
        anchor = uncommented.index("entry, spinbutton:not(.vertical) {")
        for selector in expected:
            self.assertGreater(uncommented.index(selector), anchor, selector)

    def test_entry_image_inks(self):
        # The existing entry recipe never names the icon child GTK embeds
        # inside a field or spin button, so the toolkit resource paints
        # its own inks on it: a foreign grey-green at rest, a dark grey
        # under hover, the accent hue while pressed or keyboard-active
        # and a pale grey inside an unfocused window, plus a 6px gap
        # between each side icon and the field's text that the existing
        # sheet owns nowhere. Every colour arm restates its stock twin
        # with the existing field's black ink (no collected reference
        # screenshot shows an embedded icon, so the existing text-ink
        # record stands in; the backdrop twin keeps that face per the
        # existing button:backdrop policy since Platinum's model is
        # active=frontmost), and the two margin twins keep stock's own
        # spacing byte-equal.
        expected = {
            "spinbutton:not(.vertical) image.left": {"margin-right": "6px"},
            "entry image.left": {"margin-right": "6px"},
            "spinbutton:not(.vertical) image.right": {"margin-left": "6px"},
            "entry image.right": {"margin-left": "6px"},
            "spinbutton:not(.vertical) image": {"color": BLACK},
            "entry image": {"color": BLACK},
            "spinbutton:not(.vertical) image:hover": {"color": BLACK},
            "entry image:hover": {"color": BLACK},
            "spinbutton:not(.vertical) image:active": {"color": BLACK},
            "entry image:active": {"color": BLACK},
            "spinbutton:not(.vertical) image:backdrop": {"color": BLACK},
            "entry image:backdrop": {"color": BLACK},
        }
        for selector, declarations in expected.items():
            self.assertEqual(self.selectors.count(selector), 1, selector)
            self.assertEqual(self.rules[selector], declarations, selector)
        # No other spelling in the family exists: the token sweep kills
        # renamed, stray and dropped twins alike.
        self.assertEqual(
            {
                s
                for s in self.rules
                if s.startswith("spinbutton:not(.vertical) image")
                or s.startswith("entry image")
            },
            set(expected),
        )
        # Every restated spelling sits after the existing field rule, so
        # the equal-specificity ties resolve the existing face's way under
        # either cascade reading.
        uncommented = strip_comments(self.css)
        anchor = uncommented.index("entry, spinbutton:not(.vertical) {")
        for selector in expected:
            self.assertGreater(uncommented.index(selector), anchor, selector)

    def test_entry_tag_faces(self):
        # The existing entry recipe never names the tag chips a tagged
        # entry embeds at its tail, so the toolkit resource paints its
        # own chip: a foreign accent-blue fill with white ink at rest,
        # a lighter accent under hover, a pale-repeat twin inside an
        # unfocused window and a dimmed translucent white close-button
        # ink with an accent ring and fill under hover and press. The
        # chip restates the palette's flat selection fill with the
        # existing field's black ink (no collected reference screenshot
        # shows an entry tag, so the selection-surface and text-ink
        # records stand in; the backdrop twin keeps that face per the
        # existing button:backdrop policy since Platinum's model is
        # active=frontmost, and the dimmed close-button inks rise to
        # full strength per the existing hover-erase precedents), keeps
        # stock's own padding, vertical margins and border and keeps
        # the two direction margin twins byte-equal and mirrored.
        expected = {
            ".entry-tag": {
                "padding": "5px",
                "margin-top": "2px",
                "margin-bottom": "2px",
                "border-style": "none",
                "color": BLACK,
                "background-color": SELECTION,
            },
            ":dir(ltr) .entry-tag": {"margin-left": "8px", "margin-right": "-5px"},
            ":dir(rtl) .entry-tag": {"margin-left": "-5px", "margin-right": "8px"},
            ".entry-tag:hover": {"background-color": SELECTION},
            ":backdrop .entry-tag": {"color": BLACK, "background-color": SELECTION},
            ".entry-tag.button": {"background-color": "transparent", "color": BLACK},
            ":not(:backdrop) .entry-tag.button:hover": {
                "border": f"1px solid {BLACK}",
                "color": BLACK,
            },
            ":not(:backdrop) .entry-tag.button:active": {
                "background-color": SELECTION,
                "color": BLACK,
            },
        }
        for selector, declarations in expected.items():
            self.assertEqual(self.selectors.count(selector), 1, selector)
            self.assertEqual(self.rules[selector], declarations, selector)
        # No other spelling in the family exists: the token sweep kills
        # renamed, stray and dropped twins alike.
        self.assertEqual(
            {s for s in self.rules if "entry-tag" in s}, set(expected)
        )
        # The whole chip block sits after the existing entry-image block's
        # opener, so the equal-specificity ties resolve the existing
        # face's way under either cascade reading.
        uncommented = strip_comments(self.css)
        anchor = uncommented.index("spinbutton:not(.vertical) image, entry image {")
        for selector in expected:
            self.assertGreater(uncommented.index(selector), anchor, selector)


if __name__ == "__main__":
    unittest.main()
