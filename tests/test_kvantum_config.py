"""Validate the org.macos8.desktop Kvantum style's `.kvconfig` settings.

The Platinum palette grounded in the MacOS8 color scheme, the scroll metrics,
the 2px/1px frame margins, and the SVG element each core control, track/value
and container/text surface section draws. Part 1 of the Kvantum series ships
the core controls, part 2 the track and value controls, and part 3 the
container and text surfaces; these tests pin each section's mapping so a wrong
element name that happens to exist elsewhere in the SVG fails here rather than
rendering the wrong control. The global theme selects this style
(`widgetStyle=kvantum`) as of part 4/4, but nothing here asserts that
selection.
"""

from __future__ import annotations

import unittest

from support.kde_config import read as read_kde_config
from support.kvantum_fixtures import COLOR_SCHEME, KVCONFIG
from support.platinum_palette import GREY, WHITE, hex_colour

# Every `[GeneralColors]` key mapped to the MacOS8 color scheme role it copies.
# The test re-derives the hex value from the scheme, so changing either side
# alone fails.
COLOR_ROLES = {
    "window.color": ("Window", "BackgroundNormal"),
    "button.color": ("Button", "BackgroundNormal"),
    "mid.color": ("Button", "BackgroundNormal"),
    "mid.light.color": ("Button", "BackgroundNormal"),
    "base.color": ("View", "BackgroundNormal"),
    "alt.base.color": ("View", "BackgroundAlternate"),
    "highlight.color": ("Selection", "BackgroundNormal"),
    "inactive.highlight.color": ("Selection", "BackgroundNormal"),
    "text.color": ("Window", "ForegroundNormal"),
    "window.text.color": ("Window", "ForegroundNormal"),
    "button.text.color": ("Button", "ForegroundNormal"),
    "tooltip.text.color": ("Tooltip", "ForegroundNormal"),
    "highlight.text.color": ("Selection", "ForegroundNormal"),
    "disabled.text.color": ("Button", "ForegroundInactive"),
    "tooltip.base.color": ("Tooltip", "BackgroundNormal"),
    "link.color": ("Window", "ForegroundLink"),
    "link.visited.color": ("Window", "ForegroundVisited"),
}

# The bevel roles come from the Platinum palette the desktop-theme art uses,
# not from a color-scheme role.
PALETTE_ROLES = {
    "light.color": WHITE,
    "dark.color": GREY,
}

# The core sections the plan names and the frame margin each resolves to
# (following `inherits`), in pixels. Kvantum's default uses 2px frames and a
# 1px focus ring.
CORE_FRAME_MARGINS = {
    "PanelButtonCommand": 2,
    "PanelButtonTool": 2,
    "LineEdit": 2,
    "ComboBox": 2,
    "CheckBox": 2,
    "RadioButton": 2,
    "Focus": 1,
    "GenericFrame": 2,
    "IndicatorArrow": 2,
    "ScrollbarSlider": 2,
    "Slider": 2,
    "Progressbar": 2,
    "IndicatorSpinBox": 2,
    "Tab": 2,
    "TabFrame": 2,
    "MenuBarItem": 2,
    "Menu": 2,
    "GroupBox": 2,
    "ToolTip": 2,
    "ItemView": 2,
    "HeaderSection": 2,
    "Toolbar": 2,
}

# The core controls added in part 1/4: the SVG element Kvantum draws for each
# core section's frame, interior and indicator, following `inherits`. The
# generic art-existence check cannot see these: a wrong element name that
# happens to exist elsewhere in the SVG still passes it, while Kvantum renders
# the wrong control (a check box drawn from the radio art, say). The
# track/value and surface sections have their own tables below, and
# `test_every_core_section_mapping_is_pinned` keeps the three tables together
# covering every section in CORE_FRAME_MARGINS.
CORE_CONTROL_CONFIG = {
    "PanelButtonCommand": {
        "frame.element": "button",
        "interior.element": "button",
        "indicator.element": "arrow",
    },
    "PanelButtonTool": {
        "frame.element": "button",
        "interior.element": "button",
    },
    "LineEdit": {
        "frame.element": "lineedit",
        "interior.element": "lineedit",
    },
    "ComboBox": {
        "frame.element": "button",
        "interior.element": "button",
        "indicator.element": "arrow",
    },
    "CheckBox": {
        "frame.element": "button",
        "interior.element": "checkbox",
    },
    "RadioButton": {
        "frame.element": "button",
        "interior.element": "radio",
    },
    "Focus": {
        "frame.element": "focus",
    },
    "GenericFrame": {
        "frame.element": "common",
        "interior.element": "common",
    },
    "IndicatorArrow": {
        "indicator.element": "arrow",
    },
}

# The sections the plan slices differently from the 2px raised face: the
# splitter is a thin line (0/1) and the scrollbar groove is the trough (0/4).
SPECIAL_FRAME_MARGINS = {
    "Splitter": {"top": 0, "bottom": 0, "left": 1, "right": 1},
    "ScrollbarGroove": {"top": 0, "bottom": 0, "left": 4, "right": 4},
}

# The track and value controls added in part 2/4: the SVG element Kvantum
# draws for each section's frame, interior and indicator, the two sections
# that ship no frame, and the progress bar's label styling. The generic
# art-existence check cannot see these: a wrong element name that happens to
# exist elsewhere in the SVG still passes it, while Kvantum renders the wrong
# control.
TRACK_CONTROL_CONFIG = {
    "ScrollbarSlider": {
        "frame.element": "scrollbarslider",
        "interior.element": "scrollbarslider",
        "indicator.element": "grip",
    },
    "ScrollbarGroove": {
        "frame.element": "slider",
        "interior.element": "slider",
    },
    "Slider": {
        "frame.element": "slider",
        "interior.element": "slider",
    },
    "SliderCursor": {
        "frame": "false",
        "interior.element": "slidercursor",
    },
    "Progressbar": {
        "frame.element": "progress",
        "interior.element": "progress",
        "text.focus.color": "white",
        "text.bold": "true",
    },
    "ProgressbarContents": {
        "frame": "false",
        "interior.element": "progress-pattern",
    },
    "IndicatorSpinBox": {
        "frame.element": "spin",
        "interior.element": "spin",
        "indicator.element": "arrow",
    },
    "Splitter": {
        "frame.element": "splitter",
        "interior.element": "splitter",
        "indicator.element": "splitter-grip",
    },
}

# Part 3's container and text surface sections: the SVG element Kvantum draws
# for each section's frame, interior and indicator. A wrong element name that
# happens to exist elsewhere still passes the generic art-existence check
# while Kvantum renders the wrong control, so these pin the mapping -- in
# particular `[MenuBarItem]`'s frame, which would otherwise inherit `button`
# from `PanelButtonCommand` and frame menu-bar titles with the button art.
SURFACE_CONTROL_CONFIG = {
    "Tab": {
        "frame.element": "tab",
        "interior.element": "tab",
        "indicator.element": "tab",
    },
    "TabFrame": {
        "frame.element": "tabframe",
        "interior.element": "common",
    },
    "MenuItem": {
        "frame": "false",
        "interior.element": "menuitem",
        "indicator.element": "menuitem",
    },
    "MenuBarItem": {
        "frame.element": "menubaritem",
        "interior.element": "menubaritem",
    },
    "MenuBar": {
        "frame.element": "menuitem",
        "interior.element": "menuitem",
    },
    "Menu": {
        "frame.element": "menu",
        "interior.element": "menu",
    },
    "GroupBox": {
        "frame.element": "group",
        "interior.element": "group",
    },
    "ToolTip": {
        "frame.element": "tooltip",
        "interior.element": "tooltip",
    },
    "ItemView": {
        "frame.element": "itemview",
        "interior.element": "itemview",
    },
    "HeaderSection": {
        "frame.element": "button",
    },
    "Toolbar": {
        "frame.element": "toolbar",
        "interior.element": "toolbar",
        "indicator.element": "toolbar",
        "indicator.size": "5",
    },
}


def _scheme_hex(parser, section, name):
    """Return the `#RRGGBB` form of a MacOS8 color-scheme role."""
    value = parser.get(f"Colors:{section}", name)
    return hex_colour(tuple(int(part) for part in value.split(",")))


def _resolved(parser, section, key):
    """Return *section*'s *key* following `inherits` until it is found."""
    while section is not None:
        if parser.has_option(section, key):
            return parser.get(section, key)
        if parser.has_option(section, "inherits"):
            section = parser.get(section, "inherits")
        else:
            return None
    return None


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


class TestCoreControlElements(unittest.TestCase):
    """Pin which SVG element each core control section draws.

    The core sections (``CORE_FRAME_MARGINS``) previously had only their frame
    margins pinned, so a `frame.element`/`interior.element`/`indicator.element`
    pointing at another element that exists in the SVG (CheckBox drawn from
    `radio`) passed every test while Kvantum rendered the wrong control. The
    track/value and surface sections have their own tables; together the three
    cover every core section.
    """

    def test_every_core_section_mapping_is_pinned(self):
        # The three element-mapping tables must cover every core section, so a
        # section added to CORE_FRAME_MARGINS without an element pin fails
        # here instead of shipping unchecked.
        covered = (
            set(CORE_CONTROL_CONFIG)
            | set(TRACK_CONTROL_CONFIG)
            | set(SURFACE_CONTROL_CONFIG)
        )
        self.assertEqual(set(CORE_FRAME_MARGINS) - covered, set())

    def test_every_core_control_section_maps_to_its_element(self):
        parser = read_kde_config(KVCONFIG)
        for section, expected in CORE_CONTROL_CONFIG.items():
            for key, value in expected.items():
                with self.subTest(section=section, key=key):
                    self.assertEqual(_resolved(parser, section, key), value)


class TestTrackAndValueElements(unittest.TestCase):
    """Pin which SVG element each track/value control section draws."""

    def test_every_track_and_value_section_maps_to_its_element(self):
        parser = read_kde_config(KVCONFIG)
        for section, expected in TRACK_CONTROL_CONFIG.items():
            for key, value in expected.items():
                with self.subTest(section=section, key=key):
                    self.assertEqual(_resolved(parser, section, key), value)


class TestSurfaceElements(unittest.TestCase):
    """Pin which SVG element each container/text surface section draws."""

    def test_every_surface_section_maps_to_its_element(self):
        parser = read_kde_config(KVCONFIG)
        for section, expected in SURFACE_CONTROL_CONFIG.items():
            for key, value in expected.items():
                with self.subTest(section=section, key=key):
                    self.assertEqual(_resolved(parser, section, key), value)


if __name__ == "__main__":
    unittest.main()
