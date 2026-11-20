"""Validate GTK 3 Platinum OSD scale-thumb declarations."""

import unittest

from support.gtk_rule_cases import GtkSheetRuleCases
from support.gtk_theme_spec import SCALE_THUMB
from support.platinum_palette import BLACK, FACE, GREY
from support.repo_root import ROOT


class TestGtkThemeOsdScale(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"

    def test_osd_scale_slider(self):
        """Pin the six restated stock OSD scale thumb arms.

        No collected reference screenshot shows a scale thumb inside a GTK
        OSD overlay, so the sheet restates the toolkit resource's six
        ``.osd scale slider`` arms with the existing plain scale-thumb recipes
        (``SCALE_THUMB`` in ``support.gtk_theme_spec.py``) plus two
        clearances the stock arms claim: the white-on-dark text and icon
        shadows, cleared, and a black focus-outline colour in place of the
        stock rgba(238,238,236,0.3). Stock's background-clip stays omitted
        and the stateless arms carry the plain thumb's ``-5px`` margin. The
        arm selectors and states come from gtk-contained.css in
        /usr/lib/x86_64-linux-gnu/libgtk-3.so.0 (libgtk-3 3.24.49); the
        plain ``scale slider`` rules keep governing size and every state an
        arm does not restate.
        """
        face = {
            **SCALE_THUMB,
            "outline-color": BLACK,
            "text-shadow": "none",
            "-gtk-icon-shadow": "none",
        }
        base = {**face, "margin": "-5px"}
        disabled = {
            "background-color": FACE,
            "border": f"1px solid {GREY}",
            "box-shadow": "none",
        }
        raised_states = ("", ":hover", ":active", ":backdrop")
        for state in raised_states:
            with self.subTest(state=state):
                self.assertEqual(
                    self.rules[f".osd scale slider{state}"],
                    base if state in ("", ":backdrop") else face,
                )
        for state in (":disabled", ":backdrop:disabled"):
            with self.subTest(state=state):
                self.assertEqual(
                    self.rules[f".osd scale slider{state}"], disabled
                )
        self.assertEqual(
            self.rules[".osd scale slider:disabled"],
            self.rules["scale slider:disabled"],
        )
        # The plain knob's existing no-fade amendment is specific to the bare
        # arm's stock animating members; stock's .osd thumb arms claim no
        # transition, so the shared recipe excludes that one member.
        self.assertEqual(
            self.rules[".osd scale slider"],
            {
                **{
                    name: value
                    for name, value in self.rules["scale slider"].items()
                    if name != "transition"
                },
                "outline-color": BLACK,
                "text-shadow": "none",
                "-gtk-icon-shadow": "none",
            },
        )
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if ".osd scale slider" in selector
            },
            {
                f".osd scale slider{state}"
                for state in raised_states + (":disabled", ":backdrop:disabled")
            },
        )


if __name__ == "__main__":
    unittest.main()
