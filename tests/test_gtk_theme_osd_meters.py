"""Validate GTK 3 Platinum OSD meter declarations."""

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import (
    PROGRESSBAR_PROGRESS,
    PROGRESSBAR_TROUGH,
    SCALE_EMPTY_FILL,
    SCALE_TROUGH,
)
from support.platinum_palette import GREY
from support.repo_root import ROOT


class TestGtkThemeOsdMeters(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_osd_progress_scale(self):
        """Pin the nine restated stock OSD trough, fill and progress arms.

        No collected reference screenshot shows a meter inside a GTK OSD
        overlay, so the sheet restates the toolkit resource's six `.osd`
        trough/fill/progress groups with the existing plain progress-bar and
        scale recipes (``PROGRESSBAR_TROUGH``, ``PROGRESSBAR_PROGRESS``,
        ``SCALE_TROUGH`` and ``SCALE_EMPTY_FILL`` in
        ``support.gtk_theme_spec.py``): the flat ``#EEEEEE`` trough face with
        its black border, zero radius and ``inset 1px 1px #999999`` etch at
        the existing minimums, the transparent scale fill and highlight face,
        and the existing ``#CCCCFF`` progress fill. The disabled groups repeat
        the existing paints byte-for-byte, and the disabled progress fill is
        the existing grey (``GREY`` from ``support.platinum_palette``). The
        arm selectors and states come from gtk-contained.css in
        /usr/lib/x86_64-linux-gnu/libgtk-3.so.0 (libgtk-3 3.24.49); the
        stock arms claim no geometry, glyph source or box-shadow, so the
        existing plain meter rules keep governing size and every state an arm
        does not restate.
        """
        trough = PROGRESSBAR_TROUGH
        scale_trough = SCALE_TROUGH
        fill = SCALE_EMPTY_FILL
        progress = PROGRESSBAR_PROGRESS
        disabled_progress = {**PROGRESSBAR_PROGRESS, "background-color": GREY}
        expected = [
            (trough, (
                ".osd progressbar trough",
                "progressbar .osd trough",
                ".osd progressbar trough:disabled",
                "progressbar .osd trough:disabled",
            )),
            (scale_trough, (
                ".osd scale trough",
                "scale .osd trough",
                ".osd scale trough:disabled",
                "scale .osd trough:disabled",
            )),
            (fill, (
                ".osd scale fill",
                "scale .osd fill",
                ".osd scale highlight",
                "scale .osd highlight",
                ".osd scale fill:disabled:backdrop",
                ".osd scale fill:disabled",
                "scale .osd fill:disabled",
                ".osd scale highlight:disabled",
                "scale .osd highlight:disabled",
            )),
            (progress, (
                ".osd progressbar progress",
                "progressbar .osd progress",
            )),
            (disabled_progress, (
                ".osd progressbar progress:disabled",
                "progressbar .osd progress:disabled",
            )),
        ]
        for declarations, selectors in expected:
            for selector in selectors:
                with self.subTest(selector=selector):
                    self.assertEqual(self.rules[selector], declarations)
        self.assertEqual(
            self.rules[".osd progressbar progress:disabled"]["background-color"],
            self.rules["progressbar progress:disabled"]["background-color"],
        )
        self.assertEqual(
            self.rules["progressbar progress:disabled"]["background-color"],
            GREY,
        )
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if ".osd" in selector
                and (
                    "trough" in selector
                    or "fill" in selector
                    or "highlight" in selector
                    or "progress" in selector
                )
            },
            {selector
             for _, selectors in expected
             for selector in selectors}
            | {"progressbar.osd trough", "progressbar.osd progress",
               "progressbar.osd progress:disabled"},
        )

    def test_osd_thin_bar(self):
        """Pin the two restated stock self-class ``.osd`` thin-bar arms.

        No collected reference screenshot shows a GTK OSD overlay, a meter
        inside one or a self-class ``.osd`` thin bar (a ``progressbar.osd``,
        the thin Epiphany-style headerbar indicator), so the sheet restates
        the toolkit resource's stock ``progressbar.osd trough`` and
        ``progressbar.osd progress`` arms with the existing plain progress-bar
        recipes (``PROGRESSBAR_TROUGH`` and ``PROGRESSBAR_PROGRESS`` in
        ``support.gtk_theme_spec.py``), the same reuse the existing GTK 4
        sheet's ``progressbar.osd > trough`` face makes (pinned by
        ``TestGtk4Progressbar::test_progressbar_osd_trough_paint``). The equal
        specificity restatements append after the toolkit resource, so they
        pre-empt exactly the stock arms they restate, and the existing
        ``.osd progressbar trough, progressbar .osd trough`` ancestor arms
        stay disjoint. The bare ``progressbar.osd`` node arm stays
        undeclared: its ``3px`` minimum is dominated by the trough's
        ``10px`` minimum and its transparent node background stays beneath
        the trough face. The arm selectors and stock claims come from
        gtk-contained.css in /usr/lib/x86_64-linux-gnu/libgtk-3.so.0
        (libgtk-3 3.24.49); no stock arm claims geometry, so the existing
        plain rules keep governing every state an arm does not restate.
        """
        with self.subTest(selector="progressbar.osd trough"):
            self.assertEqual(self.rules["progressbar.osd trough"],
                             PROGRESSBAR_TROUGH)
        with self.subTest(selector="progressbar.osd progress"):
            self.assertEqual(self.rules["progressbar.osd progress"],
                             PROGRESSBAR_PROGRESS)
        # The self-class base arm otherwise overrides the plain disabled grey.
        self.assertEqual(self.rules["progressbar.osd progress:disabled"],
                         {"background-color": GREY})


if __name__ == "__main__":
    unittest.main()
