"""Validate the GTK 3 Platinum sheet's progress bar and meter faces.

This module owns the progress slice split out of the former GTK 3 controls suite:
the progress bar and its trough, the meter geometry (horizontal and vertical arms
    and the corner-armed fill), the meter label ink, the drawn fill span over the
    trough, and the meter state and backdrop faces. Treeview progress-cell
    declarations live in ``test_gtk_theme_treeview_progress.py``. The
declaration tests read the stripped CSS through ``GtkSheetRuleCases``; the drawn
probe renders with a real GTK 3 in a child interpreter (see ``_run_gtk_child``),
so the suite process itself imports no GTK.
"""

import unittest
from pathlib import Path

from support.gtk_child_probe import (
    _GTK3_SHEET_PROLOGUE,
    _GTK3_SHEET_PROVIDER,
    Gtk3ChildProbeCases,
)
from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import RAISED_BEVEL
from support.platinum_palette import (
    BLACK,
    FACE,
    GREY,
    TROUGH,
)
from support.repo_root import ROOT

THEME_DIR = Path(ROOT) / "theme" / "gtk" / "org.macos8.desktop"
CSS = THEME_DIR / "gtk-3.0" / "gtk.css"


class TestGtkThemeProgress(Gtk3ChildProbeCases, GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = CSS

    def test_progressbar(self):
        self.assert_progressbar(
            trough="progressbar trough",
            progress="progressbar progress",
            disabled="progressbar progress:disabled",
        )

    def test_meter_geometry(self):
        """A meter's class-armed and corner-armed geometry keeps the existing values,
        and the scale trough carries the existing scale:focus focus shape."""
        self.assert_rule_group(
            {
                "progressbar.horizontal trough": {"min-height": "10px"},
                "progressbar.vertical trough": {"min-width": "10px"},
                "progressbar.horizontal progress": {"margin": "0", "min-height": "10px"},
                "progressbar.vertical progress": {"margin": "0", "min-width": "10px"},
                "progressbar progress.left": {"border-radius": "0"},
                "progressbar progress.right": {"border-radius": "0"},
                "progressbar progress.top": {"border-radius": "0"},
                "progressbar progress.bottom": {"border-radius": "0"},
            }
        )
        self.assert_rule(
            "scale trough",
            {
                "outline": f"1px dotted {BLACK}",
                "outline-offset": "0",
                "-gtk-outline-radius": "0",
            },
        )
        self.assertEqual(self.selectors.count("scale trough"), 1)
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith(("progressbar.horizontal", "progressbar.vertical"))
            },
            {
                "progressbar.horizontal trough",
                "progressbar.vertical trough",
                "progressbar.horizontal progress",
                "progressbar.vertical progress",
            },
        )
        self.assertEqual(
            {s for s in self.selectors if s.startswith("progressbar progress.")},
            {
                "progressbar progress.left",
                "progressbar progress.right",
                "progressbar progress.top",
                "progressbar progress.bottom",
            },
        )
        top = self.css.index("progressbar progress:disabled {")
        bottom = self.css.index("entry progress {")
        for spelling in (
            "progressbar.horizontal trough",
            "progressbar.vertical trough",
            "progressbar.horizontal progress",
            "progressbar.vertical progress",
            "progressbar progress.left",
            "progressbar progress.right",
            "progressbar progress.top",
            "progressbar progress.bottom",
        ):
            position = self.css.index(spelling + " {")
            self.assertGreater(position, top, spelling)
            self.assertLess(position, bottom, spelling)

    def test_meter_label_ink(self):
        """A meter's show-text percentage label keeps the existing window ink."""
        self.assert_rule_group({"progressbar": {"color": BLACK}})
        self.assert_rule_after("progressbar trough {", "progressbar {")
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith("progressbar")
                and not s.startswith(("progressbar ", "progressbar.", "progressbar:"))
            },
            {"progressbar"},
        )

    def test_progressbar_fill_spans_the_trough(self):
        # GTK 3 centres a fill of its own preferred size in the trough, so
        # the oriented fill rules' min-height/min-width is what makes the
        # fill span the trough interior. Each bar renders in its own
        # offscreen window; see _run_gtk_child for why this runs in a child.
        program = (
            _GTK3_SHEET_PROLOGUE
            + _GTK3_SHEET_PROVIDER
            + r'''

def render(bar, width, height, sensitive=True):
    window = Gtk.OffscreenWindow()
    bar.set_fraction(0.5)
    bar.set_sensitive(sensitive)
    window.add(bar)
    window.set_default_size(width, height)
    window.show_all()
    while Gtk.events_pending():
        Gtk.main_iteration()
    pixbuf = window.get_pixbuf()
    pixels, stride, n = pixbuf.get_pixels(), pixbuf.get_rowstride(), pixbuf.get_n_channels()
    window.destroy()

    def at(x, y):
        red, green, blue = pixels[y * stride + x * n:][:3]
        return f"#{red:02X}{green:02X}{blue:02X}"

    return at

def column(at, x, ys):
    return [at(x, y) for y in ys]

def row(at, y, xs):
    return [at(x, y) for x in xs]

BLACK, FILL, GREY, FACE = "#000000", "#CCCCFF", "#999999", "#EEEEEE"

at = render(Gtk.ProgressBar(), 100, 10)
assert column(at, 25, range(12)) == [BLACK] + [FILL] * 10 + [BLACK], column(at, 25, range(12))
assert column(at, 75, range(12)) == [BLACK, GREY] + [FACE] * 9 + [BLACK], column(at, 75, range(12))

at = render(Gtk.ProgressBar(), 100, 10, sensitive=False)
assert column(at, 25, range(1, 11)) == [GREY] * 10, column(at, 25, range(1, 11))
assert column(at, 75, range(12)) == [BLACK, GREY] + [FACE] * 9 + [BLACK], column(at, 75, range(12))

at = render(Gtk.ProgressBar(orientation=Gtk.Orientation.VERTICAL), 12, 100)
assert row(at, 25, range(1, 11)) == [FILL] * 10, row(at, 25, range(1, 11))
assert row(at, 75, range(1, 11)) == [GREY] + [FACE] * 9, row(at, 75, range(1, 11))
print("progress bar: the 0.5 fill spans trough rows 1-10 and columns 1-10 on the horizontal and vertical bars")
'''
        )
        self._run_gtk_child(program, str(CSS))

    def test_meter_state_and_backdrop_faces(self):
        """Disabled, selected-row and unfocused-window meters keep the existing
        faces, and no meter repaint fades over the stock 200ms."""
        self.assert_rule_group(
            {
                "progressbar trough:disabled": {"background-color": TROUGH},
                "scale trough:disabled": {"background-color": TROUGH},
                "progressbar trough:backdrop": {
                    "background-color": TROUGH,
                    "border-color": BLACK,
                    "transition": "none",
                },
                "scale trough:backdrop": {
                    "background-color": TROUGH,
                    "border-color": BLACK,
                    "transition": "none",
                },
                "progressbar trough:backdrop:disabled": {
                    "background-color": TROUGH,
                },
                "scale trough:backdrop:disabled": {
                    "background-color": TROUGH,
                },
                "row:selected progressbar trough": {"border-color": BLACK},
                "progressbar row:selected trough": {"border-color": BLACK},
                "row:selected scale trough": {"border-color": BLACK},
                "scale row:selected trough": {"border-color": BLACK},
                "scale fill:backdrop": {"background-color": "transparent"},
                "scale slider:backdrop": {
                    "background-color": FACE,
                    "background-image": "none",
                    "border-color": BLACK,
                    "box-shadow": RAISED_BEVEL,
                    "transition": "none",
                },
                "scale slider:backdrop:disabled": {
                    "background-color": FACE,
                    "background-image": "none",
                    "border-color": GREY,
                    "box-shadow": "none",
                    "transition": "none",
                },
                "row:selected scale slider:disabled": {"border-color": BLACK},
                "row:selected scale slider": {"border-color": BLACK},
            }
        )
        # The single amendment to the existing bare knob group: the existing
        # assert_scale reads that group per-property, so only an added,
        # altered or duplicated transition member dies here.
        self.assert_rule("scale slider", {"transition": "none"})
        self.assertEqual(self.selectors.count("scale slider"), 1)
        # Family sweep: the trough keeps the existing face in exactly the six
        # stock state spellings. A stray state trough spelling, a renamed
        # member or a pale trough face leaking onto a disabled fill dies.
        self.assertEqual(
            {
                s
                for s in self.selectors
                if (s.startswith("progressbar trough")
                    or s.startswith("scale trough"))
                and (":disabled" in s or ":backdrop" in s)
            },
            {
                "progressbar trough:disabled",
                "scale trough:disabled",
                "progressbar trough:backdrop",
                "scale trough:backdrop",
                "progressbar trough:backdrop:disabled",
                "scale trough:backdrop:disabled",
            },
        )
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith("scale slider:backdrop")
            },
            {"scale slider:backdrop", "scale slider:backdrop:disabled"},
        )
        # Exactly the six selected-row meter members restated: no selected-row
        # fill or highlight rim (inert over the zero-width border), and no
        # spelling drift on the odd disabled-first slider group.
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith(
                    (
                        "row:selected scale",
                        "row:selected progressbar",
                        "scale row:selected",
                        "progressbar row:selected",
                    )
                )
            },
            {
                "row:selected progressbar trough",
                "progressbar row:selected trough",
                "row:selected scale trough",
                "scale row:selected trough",
                "row:selected scale slider:disabled",
                "row:selected scale slider",
            },
        )
        # Every non-.osd meter backdrop spelling is accounted for: a dropped
        # rule or a stray twin outside the state block dies. The existing .osd
        # and treeview progressbar backdrop spellings carry a prefix neither
        # a scale nor a progressbar root, so neither joins; the existing one-sided
        # marked-scale record (test_marked_scale_thumb_arms) contributes its
        # eight backdropped slider spellings, verbatim from the fresh parse.
        self.assertEqual(
            {
                s
                for s in self.selectors
                if s.startswith(("scale", "progressbar"))
                and ":backdrop" in s
                and ".osd" not in s
            },
            {
                "scale fill:backdrop",
                "progressbar trough:backdrop",
                "scale trough:backdrop",
                "progressbar trough:backdrop:disabled",
                "scale trough:backdrop:disabled",
                "scale slider:backdrop",
                "scale slider:backdrop:disabled",
                "progressbar:backdrop",
                "scale.horizontal.marks-after:not(.marks-before) slider:backdrop",
                "scale.horizontal.marks-after:not(.marks-before) slider:backdrop:disabled",
                "scale.horizontal.marks-before:not(.marks-after) slider:backdrop",
                "scale.horizontal.marks-before:not(.marks-after) slider:backdrop:disabled",
                "scale.vertical.marks-after:not(.marks-before) slider:backdrop",
                "scale.vertical.marks-after:not(.marks-before) slider:backdrop:disabled",
                "scale.vertical.marks-before:not(.marks-after) slider:backdrop",
                "scale.vertical.marks-before:not(.marks-after) slider:backdrop:disabled",
            },
        )
        # Source-order pin: the nine rules sit between the existing
        # scale fill/highlight and bare knob groups, so each wins its
        # equal-specificity tie by later user-sheet source order.
        # Both anchors get a line-start bolt: the new row:selected slider
        # group's "row:selected scale slider {" spelling would otherwise
        # satisfy the bare "scale slider {" substring.
        top = self.css.index("\nscale fill, scale highlight {")
        bottom = self.css.index("\nscale slider {")
        # Comma groups pin by their full byte-equal spelling (the parser
        # stores each member individually); solo rules by their selector.
        for spelling in (
            "progressbar trough:disabled, scale trough:disabled",
            "progressbar trough:backdrop, scale trough:backdrop",
            "progressbar trough:backdrop:disabled, scale trough:backdrop:disabled",
            "row:selected progressbar trough, progressbar row:selected trough,"
            " row:selected scale trough, scale row:selected trough",
            "scale fill:backdrop",
            "scale slider:backdrop",
            "scale slider:backdrop:disabled",
            "row:selected scale slider:disabled, row:selected scale slider",
            "progressbar:backdrop",
        ):
            # A line-start bolt keeps treeview's existing
            # treeview.view.progressbar:backdrop spelling out of this search.
            position = self.css.index(
                ("\n" + spelling if spelling == "progressbar:backdrop"
                 else spelling) + " {"
            )
            self.assertGreater(position, top, spelling)
            self.assertLess(position, bottom, spelling)


if __name__ == "__main__":
    unittest.main()
