"""Pin the SVG element each Kvantum `.kvconfig` section draws.

The core controls, track and value controls, and container and text surfaces
each have a table; these tests pin every section's element mapping so a wrong
element name that happens to exist elsewhere in the SVG fails here rather than
rendering the wrong control. The palette, metrics and config-wide pin checks
live in `test_kvantum_config.py`.
"""

from __future__ import annotations

import unittest

from support.kde_config import read
from support.kvantum_fixtures import KVCONFIG
from support.kvantum_config_spec import (
    CORE_CONTROL_CONFIG,
    CORE_FRAME_MARGINS,
    SURFACE_CONTROL_CONFIG,
    TRACK_CONTROL_CONFIG,
    _assert_pins_resolve,
    _resolved,
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
        _assert_pins_resolve(self, CORE_CONTROL_CONFIG)


class TestTrackAndValueElements(unittest.TestCase):
    """Pin which SVG element each track/value control section draws."""

    def test_every_track_and_value_section_maps_to_its_element(self):
        _assert_pins_resolve(self, TRACK_CONTROL_CONFIG)


class TestSurfaceElements(unittest.TestCase):
    """Pin which SVG element each container/text surface section draws."""

    def test_every_surface_section_maps_to_its_element(self):
        _assert_pins_resolve(self, SURFACE_CONTROL_CONFIG)


class TestToolboxTabSurface(unittest.TestCase):
    """Pin the Qt toolbox tab's mapping onto the reference tab surface.

    `[ToolboxTab]` is Kvantum-required (no reference screenshot shows a Qt
    `QToolBox`; the installed KvantumAlt theme defines the section), and it
    must stay a bare `inherits=Tab` so a toolbox tab draws the same
    reference-grounded System Profiler tab face as `[Tab]` rather than a
    drifting copy of it.
    """

    def test_toolbox_tab_inherits_the_tab_surface(self):
        parser = read(KVCONFIG)
        self.assertEqual(parser.get("ToolboxTab", "inherits"), "Tab")
        self.assertEqual(set(parser.options("ToolboxTab")), {"inherits"})
        keys = (
            "frame.element",
            "interior.element",
            "indicator.element",
            "frame.top",
            "frame.bottom",
            "frame.left",
            "frame.right",
            "text.margin.left",
            "text.margin.right",
        )
        for key in keys:
            with self.subTest(key=key):
                self.assertEqual(
                    _resolved(parser, "ToolboxTab", key),
                    _resolved(parser, "Tab", key),
                )


class TestDockSurface(unittest.TestCase):
    """Pin the Qt dock's docking area and title band.

    `[Dock]` and `[DockTitle]` are Kvantum-required (no reference screenshot
    shows a Qt `QDockWidget`; the installed KvantumAlt and KvAdapta themes
    define both sections), so the pin holds the theme's own adaptation: the
    docking area draws nothing, leaving the dock panel's body the bare
    #DDDDDD window face, and the title band resolves to the `dock` element
    whose bottom 2px hold the etched rule, while its 0 top, left and right
    margins leave the band's face and label unpainted by the frame.
    """

    def test_dock_draws_nothing(self):
        parser = read(KVCONFIG)
        self.assertEqual(parser.get("Dock", "inherits"), "PanelButtonCommand")
        self.assertEqual(parser.get("Dock", "frame"), "false")
        self.assertEqual(parser.get("Dock", "interior"), "false")

    def test_dock_title_resolves_the_dock_band(self):
        parser = read(KVCONFIG)
        self.assertEqual(_resolved(parser, "DockTitle", "frame.element"), "dock")
        self.assertEqual(parser.get("DockTitle", "frame.bottom"), "2")
        for key in ("frame.top", "frame.left", "frame.right"):
            with self.subTest(key=key):
                self.assertEqual(parser.get("DockTitle", key), "0")


class TestTitleBarSurface(unittest.TestCase):
    """Pin the QMdiSubWindow's interior title band.

    `[TitleBar]` is Kvantum-required (no reference screenshot shows a
    `QMdiSubWindow`; the four installed Kvantum themes define the
    section), so the pin holds the theme's own adaptation: the band is
    the bare #DDDDDD window face with a plain black label in both the
    normal and the focused state, no frame and no rule. Every installed
    theme paints a light focused label, so the black focused label is
    this theme's own choice consistent with Platinum's always-black text.
    """

    def test_titlebar_resolves_the_bare_window_face(self):
        parser = read(KVCONFIG)
        self.assertEqual(parser.get("TitleBar", "frame"), "false")
        self.assertEqual(
            _resolved(parser, "TitleBar", "interior.element"), "titlebar"
        )

    def test_titlebar_names_the_mdi_indicator(self):
        parser = read(KVCONFIG)
        # The window-button element and size match the engine's compiled-in
        # default [TitleBar] (Kvantum/style/themeconfig/default.kvconfig,
        # read 2026-10-27; KvantumAlt's section carries the same pair), so the
        # keys pin what the engine already resolves onto the theme's own eight
        # `mdi` SVG groups.
        self.assertEqual(parser.get("TitleBar", "indicator.element"), "mdi")
        self.assertEqual(parser.get("TitleBar", "indicator.size"), "12")

    def test_titlebar_label_is_black_in_both_states(self):
        parser = read(KVCONFIG)
        for key in ("text.normal.color", "text.focus.color"):
            with self.subTest(key=key):
                self.assertEqual(parser.get("TitleBar", key), "#000000")

    def test_titlebar_text_margins_are_2_2_3_3(self):
        parser = read(KVCONFIG)
        margins = {
            "text.margin.top": "2",
            "text.margin.bottom": "2",
            "text.margin.left": "3",
            "text.margin.right": "3",
        }
        for key, value in margins.items():
            with self.subTest(key=key):
                self.assertEqual(parser.get("TitleBar", key), value)


if __name__ == "__main__":
    unittest.main()
