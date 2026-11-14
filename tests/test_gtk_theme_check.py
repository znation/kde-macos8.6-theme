"""Validate the GTK 3 Platinum sheet's check and radio indicators.

This module owns the check and radio slice split out of
``tests/test_gtk_theme_controls.py``: the mixed check's black dash probe, the
check and radio focus outlines, and the check and radio tick motion and the
backdrop, disabled and selected-row faces. The mixed-check probe renders the
shipped assets with a real GTK 3 in a child interpreter (see
``_run_gtk_child``), so the suite process itself imports no GTK; the
declaration tests read the stripped CSS through ``GtkSheetRuleCases``.
"""

import unittest
from pathlib import Path

from support.gtk_child_probe import (
    _GTK3_CHILD_HEAD,
    _GTK3_PIXEL_HEAD,
    _GTK3_SHEET_AND_WINDOW,
    Gtk3ChildProbeCases,
)
from support.gtk_css import strip_comments
from support.gtk_rule_cases import GtkSheetRuleCases
from support.platinum_palette import (
    BLACK,
)
from support.repo_root import ROOT

THEME_DIR = Path(ROOT) / "theme" / "gtk" / "org.macos8.desktop"
CSS = THEME_DIR / "gtk-3.0" / "gtk.css"


class TestGtkThemeCheck(Gtk3ChildProbeCases, GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = CSS

    def test_mixed_check_draws_a_black_dash(self):
        # The GTK work runs in a child interpreter; see _run_gtk_child for
        # why it never runs in this one.
        program = (
            "\n" + _GTK3_CHILD_HEAD
            + '''assets = sys.argv[2]
css = Path(sys.argv[1]).read_bytes().replace(
    b'url("../assets/', b'url("' + assets.encode() + b"/")
'''
            + _GTK3_SHEET_AND_WINDOW
            + '''button = Gtk.CheckButton()
button.set_can_focus(False)
button.set_inconsistent(True)
window.add(button)
'''
            + _GTK3_PIXEL_HEAD
            + '''black = [
    (x, y)
    for y in range(pixbuf.get_height())
    for x in range(pixbuf.get_width())
    if at(x, y) == "#000000"
]
xs = sorted({x for x, _ in black})
ys = sorted({y for _, y in black})
# The dash is 8px wide and 2px tall; the face's own border is not
# inside the dash's columns and rows.
dash = [(x, y) for x, y in black if 0 < x - xs[0] < 12]
inner = [p for p in dash if p[1] not in (ys[0], ys[-1])]
inner_xs = sorted({x for x, _ in inner})
inner_ys = sorted({y for _, y in inner})
assert len(inner_ys) == 2, inner_ys
assert inner_ys[1] - inner_ys[0] == 1, inner_ys
row = inner_ys[0]
run = [x for x in inner_xs if at(x, row) == "#000000" and at(x, row + 1) == "#000000"]
assert len(run) == 8, run
assert run[-1] - run[0] == 7, run
assert at(run[3], row - 1) == "#DDDDDD", at(run[3], row - 1)
assert at(run[3], row + 2) == "#DDDDDD", at(run[3], row + 2)
assert at(run[0] - 1, row) == "#DDDDDD", at(run[0] - 1, row)
print("mixed check: the inconsistent dash is 8px by 2px on the #DDDDDD face")
'''
        )
        self._run_gtk_child(program, str(CSS), str(THEME_DIR / "assets"))

    def test_checkbutton_focus_outline(self):
        self.assert_dotted_focus_outline("checkbutton:focus")

    def test_radiobutton_focus_outline(self):
        self.assert_dotted_focus_outline(
            "radiobutton:focus", anchor="checkbutton:focus"
        )

    def test_check_radio_tick_motion(self):
        """The checked and mixed marks flip with no stock transition."""
        group = (
            "radio:checked:not(:backdrop)",
            "radio:indeterminate:not(:backdrop)",
            "check:checked:not(:backdrop)",
            "check:indeterminate:not(:backdrop)",
        )
        self.assert_rule_group(dict.fromkeys(group, {"transition": "none"}))
        # The parser stores a comma group's members individually, so the
        # raw sheet pins the one byte-equal stock group: a second rule,
        # a wrongly split four-rule spelling or a stray state twin dies.
        sheet = strip_comments(self.css)
        self.assertEqual(sheet.count(", ".join(group) + " {"), 1)
        for spelling in group:
            self.assertEqual(sheet.count(spelling), 1, spelling)
        self.assertEqual(
            {s for s in self.selectors if "indeterminate:not(:backdrop)" in s},
            {"radio:indeterminate:not(:backdrop)",
             "check:indeterminate:not(:backdrop)"},
        )
        self.assertEqual(
            {s for s in self.selectors if s in group}, set(group)
        )
        # One existing tail group holds the rule last: a later append
        # keeps it behind every existing spelling it follows today.
        tail = self.selectors.index(
            "infobar > revealer > box label:link"
        )
        for spelling in group:
            self.assertGreater(
                self.selectors.index(spelling), tail, spelling
            )

    def test_check_radio_backdrop_motion_disabled_and_selected_row(self):
        """Disabled and selected-row indicators keep the existing face unfocused,
        and no ``:backdrop`` indicator repaint fades over the stock 200ms."""
        etch = "inset 1px 1px #FFFFFF, inset -1px -1px #888888"
        self.assert_rule_group(
            {
                "check:backdrop": {
                    "background-image": "none",
                    "border-color": BLACK,
                    "box-shadow": etch,
                    "transition": "none",
                },
                "radio:backdrop": {
                    "background-image": "none",
                    "border-color": BLACK,
                    "box-shadow": "none",
                    "transition": "none",
                },
            }
        )
        disabled_face = {"box-shadow": etch}
        self.assert_rule_group(
            {
                "check:backdrop:disabled": disabled_face,
                "check:checked:backdrop:disabled": disabled_face,
                "check:indeterminate:backdrop:disabled": disabled_face,
                "row:selected check": {"border-color": BLACK},
                "row:selected radio": {"border-color": BLACK},
            }
        )
        # The residue block answers the check twins only: stock's shadow
        # clear matches the existing radio face's own none, so no radio
        # backdrop-disabled spelling lands (a stray twin dies here).
        self.assertEqual(
            {s for s in self.selectors
             if ":backdrop:disabled" in s
             and (s.startswith("check") or s.startswith("radio"))},
            {"check:backdrop:disabled",
             "check:checked:backdrop:disabled",
             "check:indeterminate:backdrop:disabled"},
        )
        self.assertEqual(
            {s for s in self.selectors
             if s.startswith("row:selected check")
             or s.startswith("row:selected radio")},
            {"row:selected check", "row:selected radio"},
        )
        # The fade erasure stays bound to the two amended bare :backdrop
        # groups and the existing no-fade mark group: a stray fade on any
        # other check or radio state, a dropped amendment or a transition
        # leaking onto the existing hover, active, disabled or glyph faces
        # dies here.
        self.assertEqual(
            {s for s in self.selectors
             if (s.startswith("check") or s.startswith("radio"))
             and "transition" in self.rules[s]},
            {"check:backdrop", "radio:backdrop",
             "radio:checked:not(:backdrop)",
             "radio:indeterminate:not(:backdrop)",
             "check:checked:not(:backdrop)",
             "check:indeterminate:not(:backdrop)"},
        )
        # One existing tail block holds the five residue spellings, after
        # the amended :backdrop groups' block and before the menu record.
        top = self.css.index("radio:indeterminate:backdrop")
        bottom = self.css.index("hovered menu row")
        for spelling in (
            "check:backdrop:disabled",
            "check:checked:backdrop:disabled",
            "check:indeterminate:backdrop:disabled",
            "row:selected check, row:selected radio",
        ):
            position = self.css.index(spelling + " {")
            self.assertGreater(position, top, spelling)
            self.assertLess(position, bottom, spelling)


if __name__ == "__main__":
    unittest.main()
