"""Validate the GTK title-button box assets against their Aurorae sources.

The three assets in the GTK theme package's ``assets`` directory crop the
reference-grounded Aurorae title-bar widgets: ``window-close.svg`` and
``window-minimize.svg`` copy the ``close.svg`` and ``shade.svg``
``active-center`` groups whole, and ``window-maximize.svg`` takes the
``maximize.svg`` zoom box (its canvas x=5..17) shifted onto a 13x13 canvas.
Each ships only that group, because a plain SVG renderer draws every group in
a file and the Aurorae inactive art would cover the active box. The artwork
is re-derived from the Aurorae files, so this suite needs no reference image
and does not skip when the LFS set is absent.
"""

from __future__ import annotations

import os
import unittest

from support.aurorae_fixtures import AURORAE_DIR, ZOOM_BOX_X
from support.gtk_fixtures import PACKAGE
from support.svg_case import parse_svg
from svg_assertions import (
    assert_no_script_elements,
    assert_no_style_elements,
    assert_root_canvas,
    assert_unique_ids,
    groups_with_id,
    render_slices,
)

ASSETS = os.path.join(PACKAGE, "assets")
CLOSE_SVG = os.path.join(ASSETS, "window-close.svg")
MINIMIZE_SVG = os.path.join(ASSETS, "window-minimize.svg")
MAXIMIZE_SVG = os.path.join(ASSETS, "window-maximize.svg")

AURORAE_CLOSE = os.path.join(AURORAE_DIR, "close.svg")
AURORAE_SHADE = os.path.join(AURORAE_DIR, "shade.svg")
AURORAE_MAXIMIZE = os.path.join(AURORAE_DIR, "maximize.svg")

BUTTON_SVGS = (CLOSE_SVG, MINIMIZE_SVG, MAXIMIZE_SVG)


class TestTitleButtonAssets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.trees = {path: parse_svg(path) for path in BUTTON_SVGS}

    def test_assets_stand_alone(self):
        for tree in self.trees.values():
            assert_no_script_elements(self, tree)
            assert_no_style_elements(self, tree)
            assert_unique_ids(self, tree)

    def test_assets_span_a_13px_canvas(self):
        for tree in self.trees.values():
            assert_root_canvas(self, tree, 13, 13)

    def test_assets_hold_only_the_active_group(self):
        for path, tree in self.trees.items():
            self.assertEqual(
                [group.get("id") for group in groups_with_id(tree)],
                ["active-center"],
                path,
            )

    def test_close_and_minimize_copy_the_aurorae_active_boxes(self):
        for asset, source in (
            (CLOSE_SVG, AURORAE_CLOSE),
            (MINIMIZE_SVG, AURORAE_SHADE),
        ):
            with self.subTest(asset=os.path.basename(asset)):
                self.assertEqual(
                    render_slices(self.trees[asset])["active-center"],
                    render_slices(parse_svg(source))["active-center"],
                )

    def test_maximize_crops_the_aurorae_zoom_box(self):
        zoom = render_slices(parse_svg(AURORAE_MAXIMIZE))["active-center"]
        expected = {
            (x - ZOOM_BOX_X, y): fill
            for (x, y), fill in zoom.items()
            if ZOOM_BOX_X <= x < ZOOM_BOX_X + 13
        }
        self.assertEqual(
            render_slices(self.trees[MAXIMIZE_SVG])["active-center"],
            expected,
        )


if __name__ == "__main__":
    unittest.main()
