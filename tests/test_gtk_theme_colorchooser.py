"""Validate the GTK 3 Platinum sheet's color chooser swatches.

This module owns the color-chooser slice of
``tests/test_gtk_theme.py``'s split: the palette swatch overlays and their
borders, hover and selection marks, the add-color button and its label, and
the color-button swatch. No reference screenshot shows the chooser, so
every value is the sheet's own adaptation and the sheet's comment blocks
carry the provenance.
"""

import unittest
from pathlib import Path

from support.gtk_rule_cases import GtkSheetRuleCases
from support.platinum_palette import (
    BLACK,
    FACE,
    SELECTION,
    WHITE,
)
from support.repo_root import ROOT

THEME_DIR = Path(ROOT) / "theme" / "gtk" / "org.macos8.desktop"
CSS = THEME_DIR / "gtk-3.0" / "gtk.css"

ADD_COLOR_OVERLAYS = (
    "colorswatch#add-color-button overlay",
    "colorswatch#add-color-button overlay:hover",
    "colorswatch#add-color-button overlay:backdrop",
    "colorswatch#add-color-button overlay:backdrop:hover",
)


class TestGtkThemeColorChooser(GtkSheetRuleCases, unittest.TestCase):
    CSS_PATH = CSS

    def assert_add_color_overlays(self, declarations):
        """Assert every add-color overlay selector carries *declarations*.

        The sheet restates the four add-color overlay selectors together
        wherever a property is barred, so this module pins them in one
        pass: the seven ``assert_rule`` loops below route through here,
        and the corners pin keys its declaration dictionary from the
        ``ADD_COLOR_OVERLAYS`` constant directly.
        """
        for selector in ADD_COLOR_OVERLAYS:
            with self.subTest(selector=selector):
                self.assert_rule(selector, declarations)

    def test_color_swatch_corners(self):
        self.assert_color_swatch_corners(
            " overlay",
            {
                **{
                    selector: {
                        "background-color": FACE,
                        "background-image": "none",
                        "box-shadow": "none",
                        "border-color": BLACK,
                        "color": BLACK,
                        "outline-color": BLACK,
                        "text-shadow": "none",
                        "-gtk-icon-shadow": "none",
                    }
                    for selector in ADD_COLOR_OVERLAYS
                },
                "button.color colorswatch:only-child": {"box-shadow": "none"},
                "row:selected colorswatch": {"box-shadow": f"0 0 0 2px {BLACK}"},
                "colorswatch overlay:hover": {"box-shadow": "none"},
                "colorswatch overlay": {"border-color": BLACK},
                "colorswatch.light overlay:hover": {"border-color": BLACK},
                "colorswatch.dark overlay:hover": {"border-color": BLACK},
                "colorswatch overlay:backdrop": {"border-color": BLACK},
                "colorswatch overlay:backdrop:hover": {"border-color": BLACK},
                "colorswatch:disabled overlay": {"border-color": BLACK},
                "colorswatch:drop(active).light overlay": {
                    "border-color": SELECTION,
                    "box-shadow": f"inset 0 0 0 2px {BLACK}, inset 0 0 0 1px {SELECTION}",
                },
                "colorswatch:drop(active).dark overlay": {
                    "border-color": SELECTION,
                    "box-shadow": f"inset 0 0 0 2px {BLACK}, inset 0 0 0 1px {SELECTION}",
                },
                "colorswatch.light": {"outline-color": BLACK},
                "colorswatch.dark": {"outline-color": BLACK},
                "colorswatch.light overlay:backdrop": {"color": BLACK},
                "colorswatch.dark overlay:backdrop": {"color": WHITE},
            },
        )

    def test_selected_row_color_swatch_ring(self):
        expected = {"box-shadow": f"0 0 0 2px {BLACK}"}
        self.assertEqual(1, self.selectors.count("row:selected colorswatch"))
        self.assert_rule("row:selected colorswatch", expected)
        self.assertEqual(1, self.selectors.count("row:selected colorswatch"))
        self.assertEqual(
            BLACK, self.rules["frame > border"]["border"].split()[-1]
        )
        self.assert_rule("button.color colorswatch:only-child", {"box-shadow": "none"})

    def test_color_swatch_backdrop_foregrounds(self):
        self.assert_rule("colorswatch.light overlay:backdrop", {"color": BLACK})
        self.assert_rule("colorswatch.dark overlay:backdrop", {"color": WHITE})
        for selector in (
            "colorswatch#add-color-button overlay:backdrop",
            "colorswatch#add-color-button overlay:backdrop:hover",
        ):
            with self.subTest(selector=selector):
                self.assert_rule(selector, {"color": BLACK})

    def test_color_swatch_outline_colors(self):
        for selector in ("colorswatch.light", "colorswatch.dark"):
            with self.subTest(selector=selector):
                self.assert_rule(selector, {"outline-color": BLACK})
        self.assertEqual(
            BLACK, self.rules["frame > border"]["border"].split()[-1]
        )

    def test_color_swatch_drop_target(self):
        expected = {
            "border-color": SELECTION,
            "box-shadow": f"inset 0 0 0 2px {BLACK}, inset 0 0 0 1px {SELECTION}",
        }
        for selector in (
            "colorswatch:drop(active).light overlay",
            "colorswatch:drop(active).dark overlay",
        ):
            with self.subTest(selector=selector):
                self.assert_rule(selector, expected)
        self.assertEqual(
            SELECTION,
            self.rules["list row.activatable:selected"]["background-color"],
        )
        self.assertEqual(
            BLACK, self.rules["frame > border"]["border"].split()[-1]
        )

    def test_add_color_border_colors(self):
        self.assert_add_color_overlays({"border-color": BLACK})
        self.assertEqual(
            self.rules[ADD_COLOR_OVERLAYS[0]]["border-color"],
            self.rules["frame > border"]["border"].split()[-1],
        )

    def test_add_color_outline_colors(self):
        self.assert_add_color_overlays({"outline-color": BLACK})
        self.assertEqual(
            BLACK, self.rules["colorswatch.light"]["outline-color"]
        )

    def test_color_swatch_hover_shadow(self):
        expected = {"box-shadow": "none"}
        self.assert_rule("colorswatch overlay:hover", expected)
        self.assertEqual(
            self.rules["colorswatch overlay:hover"],
            self.rules["button.color colorswatch:only-child"],
        )

    def test_color_swatch_border_colors(self):
        selectors = (
            "colorswatch overlay",
            "colorswatch.light overlay:hover",
            "colorswatch.dark overlay:hover",
            "colorswatch overlay:backdrop",
            "colorswatch overlay:backdrop:hover",
            "colorswatch:disabled overlay",
        )
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector]["border-color"], BLACK)
        self.assertEqual(
            self.rules[selectors[0]]["border-color"],
            self.rules["frame > border"]["border"].split()[-1],
        )
        for selector in (
            "colorswatch:drop(active).light overlay",
            "colorswatch:drop(active).dark overlay",
        ):
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector]["border-color"], SELECTION)

    def test_color_button_swatch_shadow(self):
        self.assert_rule(
            "button.color colorswatch:only-child", {"box-shadow": "none"}
        )

    def test_add_color_background_images(self):
        self.assert_add_color_overlays(
            {"background-image": "none", "box-shadow": "none", "color": BLACK}
        )
        self.assertEqual(
            self.rules["colorswatch#add-color-button overlay"]["background-image"],
            self.rules["button"]["background-image"],
        )

    def test_add_color_background_colors(self):
        self.assert_add_color_overlays({"background-color": FACE})
        self.assertEqual(
            self.rules["colorswatch#add-color-button overlay"]["background-color"],
            self.rules["button"]["background-color"],
        )
        # Chosen-color swatches carry no fill: their rule clears only the
        # decorative shadow, so this face applies to the add-color action alone.
        self.assert_rule(
            "button.color colorswatch:only-child", {"box-shadow": "none"}
        )

    def test_add_color_box_shadows(self):
        self.assert_add_color_overlays({"box-shadow": "none"})

    def test_add_color_label_shadows(self):
        self.assert_add_color_overlays(
            {"text-shadow": "none", "-gtk-icon-shadow": "none"}
        )

    def test_add_color_foregrounds(self):
        self.assert_add_color_overlays({"color": BLACK})
        self.assertEqual(
            self.rules[ADD_COLOR_OVERLAYS[0]]["color"],
            self.rules["window"]["color"],
        )


if __name__ == "__main__":
    unittest.main()
