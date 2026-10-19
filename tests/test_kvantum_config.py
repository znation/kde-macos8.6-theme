"""Validate the org.macos8.desktop Kvantum style's palette and metrics.

The Platinum palette grounded in the MacOS8 color scheme, the scroll metrics,
the 2px/1px frame margins, and the checks that every `.kvconfig` section and
setting is pinned by a table in `support.kvantum_config_spec`. The element
each core control, track/value and container/text surface section draws is
pinned in `test_kvantum_config_elements.py`. The global theme selects this
style (`widgetStyle=kvantum`) as of part 4/4, but nothing here asserts that
selection.
"""

from __future__ import annotations

import unittest

from support.kde_config import read as read_kde_config
from support.kvantum_config_spec import (
    COLOR_ROLES,
    CORE_CONTROL_CONFIG,
    CORE_FRAME_MARGINS,
    FRAMELESS_SECTIONS,
    PALETTE_ROLES,
    SPECIAL_FRAME_MARGINS,
    SURFACE_CONTROL_CONFIG,
    TRACK_CONTROL_CONFIG,
    VALUE_KEYS,
    _assert_pins_resolve,
    _resolved,
    _scheme_hex,
)
from support.kvantum_fixtures import COLOR_SCHEME, KVCONFIG


class TestGeneralColors(unittest.TestCase):
    def setUp(self):
        self.kvconfig = read_kde_config(KVCONFIG)
        self.scheme = read_kde_config(COLOR_SCHEME)

    def test_every_colour_is_grounded_in_the_scheme_or_the_palette(self):
        for key, (section, name) in COLOR_ROLES.items():
            with self.subTest(key=key):
                self.assertEqual(
                    self.kvconfig.get("GeneralColors", key),
                    _scheme_hex(self.scheme, section, name),
                )
        for key, value in PALETTE_ROLES.items():
            with self.subTest(key=key):
                self.assertEqual(self.kvconfig.get("GeneralColors", key), value)

    def test_declares_exactly_the_mapped_colours(self):
        self.assertEqual(
            set(self.kvconfig.options("GeneralColors")),
            set(COLOR_ROLES) | set(PALETTE_ROLES),
        )


class TestGeneral(unittest.TestCase):
    def test_scroll_metrics_match_the_desktop_theme(self):
        parser = read_kde_config(KVCONFIG)
        self.assertEqual(parser.get("%General", "scroll_width"), "16")
        self.assertEqual(parser.get("%General", "scroll_arrows"), "true")

    def test_scrollbar_indicator_sizes_are_pinned(self):
        parser = read_kde_config(KVCONFIG)
        self.assertEqual(_resolved(parser, "Scrollbar", "indicator.size"), "16")
        self.assertEqual(
            _resolved(parser, "ScrollbarSlider", "indicator.size"), "13"
        )


class TestFrameMargins(unittest.TestCase):
    def test_every_core_section_resolves_to_the_expected_frame_margin(self):
        parser = read_kde_config(KVCONFIG)
        for section, margin in CORE_FRAME_MARGINS.items():
            for side in ("top", "bottom", "left", "right"):
                with self.subTest(section=section, side=side):
                    self.assertEqual(
                        _resolved(parser, section, f"frame.{side}"),
                        str(margin),
                    )

    def test_special_frame_margins_are_pinned(self):
        parser = read_kde_config(KVCONFIG)
        for section, margins in SPECIAL_FRAME_MARGINS.items():
            for side, margin in margins.items():
                with self.subTest(section=section, side=side):
                    self.assertEqual(
                        _resolved(parser, section, f"frame.{side}"),
                        str(margin),
                    )

    def test_menu_bar_margins_are_pinned(self):
        parser = read_kde_config(KVCONFIG)
        margins = {"top": 0, "bottom": 0, "left": 2, "right": 2}
        for side, margin in margins.items():
            with self.subTest(side=side):
                self.assertEqual(
                    _resolved(parser, "MenuBar", f"frame.{side}"), str(margin)
                )


class TestSectionCoverage(unittest.TestCase):
    """Every section in the `.kvconfig` is pinned by one of the tables.

    The per-section tests only look at the sections their table names, so a
    section absent from every table (``[Scrollbar]``'s element mapping and
    ``[TabBarFrame]``'s framelessness were, before this test) shipped
    unchecked. This keeps the tables exhaustive over the config, so a new
    section without a pin fails here.
    """

    def test_every_section_is_pinned(self):
        parser = read_kde_config(KVCONFIG)
        covered = (
            set(CORE_CONTROL_CONFIG)
            | set(TRACK_CONTROL_CONFIG)
            | set(SURFACE_CONTROL_CONFIG)
            | set(FRAMELESS_SECTIONS)
        )
        # `%General` holds the scroll metrics and `[GeneralColors]` the
        # palette; neither names an element, and their own tests pin them.
        metadata = {"%General", "GeneralColors"}
        self.assertEqual(set(parser.sections()) - covered - metadata, set())

    def test_every_frameless_section_suppresses_its_frame(self):
        _assert_pins_resolve(self, FRAMELESS_SECTIONS)


class TestValueKeys(unittest.TestCase):
    """Pin the `.kvconfig` settings that name no element and no frame margin.

    The element, frame-margin and frameless tables pin which art a section
    draws and where; the indicator sizes, label colours, text margins,
    `min_height`, `text.shadow` flags and `composite` still drive the rendered
    control and were pinned by nothing. `test_every_key_is_pinned` keeps the
    tables exhaustive over the config, so a new setting without a pin fails
    here.
    """

    def test_every_value_key_is_pinned(self):
        parser = read_kde_config(KVCONFIG)
        for section, expected in VALUE_KEYS.items():
            for key, value in expected.items():
                with self.subTest(section=section, key=key):
                    self.assertEqual(parser.get(section, key), value)

    def test_every_key_is_pinned(self):
        parser = read_kde_config(KVCONFIG)
        sides = ("top", "bottom", "left", "right")
        pinned = set()
        for table in (
            CORE_CONTROL_CONFIG,
            TRACK_CONTROL_CONFIG,
            SURFACE_CONTROL_CONFIG,
            FRAMELESS_SECTIONS,
            VALUE_KEYS,
        ):
            for section, values in table.items():
                pinned.update((section, key) for key in values)
        for section in CORE_FRAME_MARGINS:
            pinned.update((section, f"frame.{side}") for side in sides)
        for section, margins in SPECIAL_FRAME_MARGINS.items():
            pinned.update((section, f"frame.{side}") for side in margins)
        pinned.update(("MenuBar", f"frame.{side}") for side in sides)
        # TestGeneral pins these two sizes and the scroll metrics.
        pinned.update(
            {
                ("Scrollbar", "indicator.size"),
                ("ScrollbarSlider", "indicator.size"),
                ("%General", "scroll_width"),
                ("%General", "scroll_arrows"),
            }
        )
        # `author` and `comment` are metadata, not styling. `inherits` is
        # structural: a wrong target resolves every element and margin key
        # above to a different value, so the tables catch it.
        pinned.update(("%General", key) for key in ("author", "comment"))
        # `[GeneralColors]` is pinned exactly by
        # `TestGeneralColors.test_declares_exactly_the_mapped_colours`.
        actual = {
            (section, key)
            for section in parser.sections()
            if section != "GeneralColors"
            for key in parser.options(section)
            if key != "inherits"
        }
        self.assertEqual(actual - pinned, set())


if __name__ == "__main__":
    unittest.main()
