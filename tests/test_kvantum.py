"""Validate the org.macos8.desktop Kvantum widget style package.

Part 1 of the Kvantum series ships the Platinum palette, the grounded frame
geometry and our own SVG art for the core Qt controls: push and tool buttons,
line edits, the generic frame, check boxes, radio buttons, the focus ring and
the indicator arrows. Part 2 adds the track and value controls: the scroll bar
slider and grip, the slider/scrollbar trough, the slider cursor, the progress
bar frame and pattern, the spin box and the splitter and its grip. Part 3 adds
the container and text surfaces: tabs and their frame, menus and the menu bar,
group boxes, tooltips, item views, toolbars and the menu item interiors. These
tests pin the palette against the MacOS8 color scheme, the 2px/1px frame
margins, the SVG's ids, palette and safety, and the install/uninstall
lifecycle. The style is installed but not selected until part 4/4, so nothing
here asserts a `widgetStyle` selection.
"""

from __future__ import annotations

import os
import unittest
import xml.etree.ElementTree as ET

from support.kde_config import read as read_kde_config
from support.platinum_palette import (
    FACE,
    GREY,
    SELECTION,
    TOOLTIP_FACE,
    TROUGH,
    WHITE,
    assert_fill_palette,
    hex_colour,
)
from support.process_assertions import assert_succeeded
from support.shipped_files import shipped_files
from svg_assertions import (
    assert_no_external_references,
    assert_no_script_elements,
    assert_no_style_elements,
    assert_slice_pixels,
    assert_unique_ids,
    attribute_values,
    pixel_map,
    render_slices,
)
from support.theme_install import (
    ROOT,
    XDG_DATA_HOME,
    assert_files_identical,
    install,
    installed_destdir,
    uninstall,
)

KVANTUM_ID = "org.macos8.desktop"
PACKAGE = os.path.join(ROOT, "theme", "kvantum", KVANTUM_ID)
KVCONFIG = os.path.join(PACKAGE, KVANTUM_ID + ".kvconfig")
SVG = os.path.join(PACKAGE, KVANTUM_ID + ".svg")
COLOR_SCHEME = os.path.join(ROOT, "theme", "color-schemes", "MacOS8.colors")

SHIPPED_FILES = (KVANTUM_ID + ".kvconfig", KVANTUM_ID + ".svg")

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

# The nine-sliced frame elements and the states the SVG ships. Kvantum names
# the centre `<element>-<state>` and each slice `<element>-<state>-<slice>`.
# `menuitem` is a frame here because `[MenuBar]` names it as its frame element
# and an interior because `[MenuItem]` names it as its interior; its centre id
# serves both. `menubaritem` is the same: `[MenuBarItem]` names it as both its
# frame and its interior, and Kvantum draws that frame only in the pressed and
# toggled states, so those are the states it ships slices for.
FRAME_STATES = {
    "button": ("normal", "pressed", "focused", "toggled"),
    "lineedit": ("normal", "focused"),
    "common": ("normal", "focused"),
    "scrollbarslider": ("normal", "focused", "pressed"),
    "slider": ("normal", "toggled"),
    "progress": ("normal",),
    "spin": ("normal", "focused", "pressed"),
    "splitter": ("normal", "focused", "pressed"),
    "tab": ("normal", "focused", "toggled"),
    "tabframe": ("normal",),
    "menu": ("normal",),
    "group": ("normal",),
    "tooltip": ("normal",),
    "itemview": ("normal", "focused", "pressed", "toggled"),
    "toolbar": ("normal",),
    "menuitem": ("normal", "pressed", "toggled"),
    "menubaritem": ("pressed", "toggled"),
}
SLICE_NAMES = (
    "top", "bottom", "left", "right",
    "topleft", "topright", "bottomleft", "bottomright",
)

# Check boxes and radio buttons are single interior elements Kvantum renders
# whole, so they carry a state id, not a nine-slice. `menuitem` and
# `menubaritem` are the menu-item interiors; their centre ids also serve as the
# frame art above, so both are frames and interiors at once.
INTERIOR_STATES = {
    "checkbox": ("normal", "focused", "checked-normal", "checked-focused"),
    "radio": ("normal", "focused", "checked-normal", "checked-focused"),
    "slidercursor": ("normal", "focused", "pressed", "disabled"),
    "progress-pattern": ("normal", "focused", "toggled", "disabled"),
    "splitter-grip": ("normal", "focused", "pressed"),
    "grip": ("normal", "focused", "pressed"),
    "menuitem": ("normal", "pressed", "toggled"),
    "menubaritem": ("normal", "pressed", "toggled"),
}
ARROW_DIRECTIONS = ("up", "down", "left", "right")
ARROW_STATES = ("normal", "focused", "pressed", "disabled")

# Each button state's bevel direction. Kvantum draws the `button-pressed` and
# `button-toggled` ids for a sunken and an on (toggled) button, so those
# states must paint the sunken bevel -- a #999999 shadow inside the top/left
# outline and a #FFFFFF highlight inside the bottom/right one -- rather than
# repeat the raised art of the resting and focused button.
BUTTON_BEVELS = {
    "normal": "raised",
    "focused": "raised",
    "pressed": "sunken",
    "toggled": "sunken",
}
BUTTON_FACE = FACE
BUTTON_SIZE = 30

# The four 2px corner slices of a button, per bevel, row-major in
# slice-local coordinates.
BUTTON_CORNERS = {
    "raised": {
        "topleft": ("#000000", "#000000", "#000000", "#FFFFFF"),
        "topright": ("#000000", "#000000", "#999999", "#000000"),
        "bottomleft": ("#000000", "#FFFFFF", "#000000", "#000000"),
        "bottomright": ("#999999", "#000000", "#000000", "#000000"),
    },
    "sunken": {
        "topleft": ("#000000", "#000000", "#000000", "#999999"),
        "topright": ("#000000", "#000000", "#FFFFFF", "#000000"),
        "bottomleft": ("#000000", "#999999", "#000000", "#000000"),
        "bottomright": ("#FFFFFF", "#000000", "#000000", "#000000"),
    },
}

# Part 3's frame elements, the bevel each state paints and the colour of its
# centre. `raised` and `sunken` paint the eight bevel slices and four corners
# `_button_edge_maps`/`BUTTON_CORNERS` describe; `flat` paints every slice as
# a solid fill with no outline or bevel, the project's flat-selection art for
# a highlighted item. The pixel test renders each state's nine slices, so a
# `menubaritem-pressed` that gains a bevel, or a `menu` drawn with a sunken
# bevel, fails here rather than passing on ids alone. The selected tab keeps
# the raised bevel the desktop theme's active tab paints.
SURFACE_STATES = {
    "tab": {
        "normal": ("raised", FACE),
        "focused": ("raised", FACE),
        "toggled": ("raised", FACE),
    },
    "tabframe": {"normal": ("raised", FACE)},
    "menu": {"normal": ("raised", FACE)},
    "group": {"normal": ("raised", FACE)},
    "tooltip": {"normal": ("raised", TOOLTIP_FACE)},
    "itemview": {
        "normal": ("sunken", WHITE),
        "focused": ("sunken", WHITE),
        "pressed": ("flat", SELECTION),
        "toggled": ("flat", SELECTION),
    },
    "toolbar": {"normal": ("raised", FACE)},
    "menuitem": {
        "normal": ("raised", FACE),
        "pressed": ("flat", SELECTION),
        "toggled": ("flat", SELECTION),
    },
    "menubaritem": {
        "pressed": ("flat", SELECTION),
        "toggled": ("flat", SELECTION),
    },
}

# The nine slices of a Kvantum frame element and their size in the 30px test
# tile: the centre id carries no suffix, the eight slices do. A `flat` state
# paints every one of these as a solid rectangle.
SURFACE_SLICE_SIZES = {
    "": (BUTTON_SIZE, BUTTON_SIZE),
    "top": (BUTTON_SIZE, 2),
    "bottom": (BUTTON_SIZE, 2),
    "left": (2, BUTTON_SIZE),
    "right": (2, BUTTON_SIZE),
    "topleft": (2, 2),
    "topright": (2, 2),
    "bottomleft": (2, 2),
    "bottomright": (2, 2),
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


def _button_edge_maps(bevel):
    """Return the four 2px edge slices a *bevel* paints, keyed by slice name.

    Each edge is the outer 1px #000000 outline with the bevel's 1px band
    inside it: a raised bevel highlights the top/left and shadows the
    bottom/right, and a sunken one swaps those two colours.
    """
    if bevel == "raised":
        top, bottom = ("#000000", "#FFFFFF"), ("#999999", "#000000")
        left, right = ("#000000", "#FFFFFF"), ("#999999", "#000000")
    else:
        top, bottom = ("#000000", "#999999"), ("#FFFFFF", "#000000")
        left, right = ("#000000", "#999999"), ("#FFFFFF", "#000000")
    return {
        "top": pixel_map(
            (top[0],) * BUTTON_SIZE + (top[1],) * BUTTON_SIZE, BUTTON_SIZE, 2
        ),
        "bottom": pixel_map(
            (bottom[0],) * BUTTON_SIZE + (bottom[1],) * BUTTON_SIZE, BUTTON_SIZE, 2
        ),
        "left": pixel_map(left * BUTTON_SIZE, 2, BUTTON_SIZE),
        "right": pixel_map(right * BUTTON_SIZE, 2, BUTTON_SIZE),
    }


def _installed_dir(destdir):
    """Directory `make install` writes the Kvantum theme into."""
    return os.path.join(
        destdir, XDG_DATA_HOME.lstrip("/"), "themes", KVANTUM_ID, "Kvantum"
    )


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


class TestSvg(unittest.TestCase):
    def setUp(self):
        self.tree = ET.parse(SVG)
        self.ids = attribute_values(self.tree, "id")

    def test_every_frame_element_ships_its_centre_and_eight_slices(self):
        for element, states in FRAME_STATES.items():
            for state in states:
                prefix = f"{element}-{state}"
                with self.subTest(element=element, state=state):
                    self.assertIn(prefix, self.ids)
                    for slice_name in SLICE_NAMES:
                        self.assertIn(f"{prefix}-{slice_name}", self.ids)

    def test_the_focus_ring_ships_its_centre_and_eight_slices(self):
        self.assertIn("focus", self.ids)
        for slice_name in SLICE_NAMES:
            self.assertIn(f"focus-{slice_name}", self.ids)

    def test_interior_elements_ship_every_state(self):
        for element, states in INTERIOR_STATES.items():
            for state in states:
                with self.subTest(element=element, state=state):
                    self.assertIn(f"{element}-{state}", self.ids)

    def test_indicator_arrows_ship_every_direction_and_state(self):
        for direction in ARROW_DIRECTIONS:
            for state in ARROW_STATES:
                with self.subTest(direction=direction, state=state):
                    self.assertIn(f"arrow-{direction}-{state}", self.ids)

    def test_every_element_the_config_names_has_art(self):
        parser = read_kde_config(KVCONFIG)
        names = set()
        for section in parser.sections():
            for key, value in parser.items(section):
                if key.endswith(".element"):
                    names.add(value)
        for name in names:
            with self.subTest(element=name):
                self.assertTrue(
                    any(i == name or i.startswith(name + "-") for i in self.ids),
                    f"no SVG id for config element {name!r}",
                )

    def test_uses_exactly_the_platinum_palette(self):
        assert_fill_palette(
            self,
            self.tree,
            extra=frozenset({TROUGH, TOOLTIP_FACE, SELECTION}),
        )

    def test_has_no_scripts_styles_external_refs_or_duplicate_ids(self):
        assert_no_script_elements(self, self.tree)
        assert_no_style_elements(self, self.tree)
        assert_no_external_references(self, self.tree)
        assert_unique_ids(self, self.tree)


class TestButtonBevelPixels(unittest.TestCase):
    """Pin the painted bevel of each button state, not just its ids.

    `TestSvg` checks that the state ids and the palette exist, which a pressed
    state repeating the raised art passes; these tests render each state's
    nine slices and compare them pixel for pixel, so a raised `button-pressed`
    or `button-toggled` fails here.
    """

    def setUp(self):
        self.slices = render_slices(ET.parse(SVG))

    def test_every_button_state_paints_its_bevel(self):
        centre = pixel_map(
            (BUTTON_FACE,) * (BUTTON_SIZE * BUTTON_SIZE),
            BUTTON_SIZE,
            BUTTON_SIZE,
        )
        for state, bevel in BUTTON_BEVELS.items():
            prefix = f"button-{state}"
            with self.subTest(state=state):
                assert_slice_pixels(self, self.slices, prefix, centre)
                for name, expected in _button_edge_maps(bevel).items():
                    assert_slice_pixels(
                        self, self.slices, f"{prefix}-{name}", expected
                    )
                for name, colours in BUTTON_CORNERS[bevel].items():
                    assert_slice_pixels(
                        self, self.slices, f"{prefix}-{name}", pixel_map(colours, 2, 2)
                    )


class TestSurfaceBevelPixels(unittest.TestCase):
    """Pin the painted bevel of each part-3 surface state, not just its ids.

    `TestSvg` checks that the state ids and the palette exist, which a
    `menubaritem-pressed` repeating the flat `normal` art passes; these tests
    render each state's nine slices and compare them pixel for pixel, so a
    wrong frame element or a wrong bevel fails here.
    """

    def setUp(self):
        self.slices = render_slices(ET.parse(SVG))

    def test_every_surface_state_paints_its_bevel(self):
        for element, states in SURFACE_STATES.items():
            for state, (bevel, face) in states.items():
                prefix = f"{element}-{state}"
                with self.subTest(element=element, state=state):
                    if bevel == "flat":
                        self._assert_flat_state(prefix, face)
                    else:
                        self._assert_bevel_state(prefix, bevel, face)

    def _assert_flat_state(self, prefix, face):
        for name, (width, height) in SURFACE_SLICE_SIZES.items():
            slice_id = prefix if not name else f"{prefix}-{name}"
            assert_slice_pixels(
                self,
                self.slices,
                slice_id,
                pixel_map((face,) * (width * height), width, height),
            )

    def _assert_bevel_state(self, prefix, bevel, face):
        assert_slice_pixels(
            self,
            self.slices,
            prefix,
            pixel_map(
                (face,) * (BUTTON_SIZE * BUTTON_SIZE), BUTTON_SIZE, BUTTON_SIZE
            ),
        )
        for name, expected in _button_edge_maps(bevel).items():
            assert_slice_pixels(self, self.slices, f"{prefix}-{name}", expected)
        for name, colours in BUTTON_CORNERS[bevel].items():
            assert_slice_pixels(
                self, self.slices, f"{prefix}-{name}", pixel_map(colours, 2, 2)
            )


class TestPackage(unittest.TestCase):
    def test_package_ships_exactly_the_theme_files(self):
        shipped = shipped_files(PACKAGE)
        self.assertEqual(shipped, set(SHIPPED_FILES))


class TestInstall(unittest.TestCase):
    def test_make_install_copies_both_files_byte_for_byte(self):
        with installed_destdir(self) as tmp:
            installed = _installed_dir(tmp)
            for name in SHIPPED_FILES:
                assert_files_identical(
                    self,
                    os.path.join(PACKAGE, name),
                    os.path.join(installed, name),
                    name,
                )

    def test_make_install_is_repeatable(self):
        with installed_destdir(self) as tmp:
            assert_succeeded(self, install(tmp))

    def test_make_uninstall_removes_the_installed_files(self):
        with installed_destdir(self) as tmp:
            installed = _installed_dir(tmp)
            self.assertTrue(os.path.isdir(installed), installed)
            assert_succeeded(self, uninstall(tmp))
            for name in SHIPPED_FILES:
                path = os.path.join(installed, name)
                self.assertFalse(os.path.exists(path), path)
            again = uninstall(tmp)
            assert_succeeded(self, again)

    def test_make_uninstall_removes_staging_leftovers(self):
        with installed_destdir(self) as tmp:
            installed = _installed_dir(tmp)
            staging = [
                os.path.join(installed, f".{name}.staging")
                for name in SHIPPED_FILES
            ]
            for path in staging:
                with open(path, "w", encoding="utf-8") as handle:
                    handle.write("partial")
            assert_succeeded(self, uninstall(tmp))
            for path in staging:
                self.assertFalse(os.path.exists(path), path)


if __name__ == "__main__":
    unittest.main()
