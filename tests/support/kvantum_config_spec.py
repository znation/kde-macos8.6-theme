"""The `.kvconfig` pin tables shared by the Kvantum config tests.

Each table maps a `.kvconfig` section to the settings it must resolve to: the
`GeneralColors` roles and their palette values, the frame margins, the SVG
element each core, track/value and surface section draws, the frameless
sections, and the remaining value settings. The pin tests and the
exhaustiveness tests read them through the helpers here, so the tables stay in
one place while `test_kvantum_config.py` and `test_kvantum_config_elements.py`
split the checks by concern.
"""

from __future__ import annotations

from support.kde_config import read as read_kde_config
from support.kvantum_fixtures import KVCONFIG
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

# The core sections and the frame margin each resolves to
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
    "ToolboxTab": 2,
    "TabFrame": 2,
    "MenuBarItem": 2,
    "Menu": 2,
    "GroupBox": 2,
    "ToolTip": 2,
    "ItemView": 2,
    "HeaderSection": 2,
    "Toolbar": 2,
    "ToolbarButton": 2,
    "ToolbarComboBox": 2,
    "ToolbarLineEdit": 2,
    "DropDownButton": 2,
}

# The core controls: the SVG element Kvantum draws for each core section's
# frame, interior and indicator, following `inherits`. The generic art-existence check cannot see these: a wrong element name that
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
        "indicator.element": "comboarrow",
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
    "ToolbarButton": {
        "frame.element": "button",
        "interior.element": "button",
        "indicator.element": "arrow",
    },
    "ToolbarComboBox": {
        "frame.element": "button",
        "interior.element": "button",
        "indicator.element": "comboarrow",
    },
    "ToolbarLineEdit": {
        "frame.element": "lineedit",
        "interior.element": "lineedit",
    },
    "DropDownButton": {
        "frame.element": "button",
        "interior.element": "button",
        "indicator.element": "arrow-down",
    },
}

# The sections sliced differently from the 2px raised face: the
# splitter is a thin line (0/1) and the scrollbar groove is the trough (0/4).
SPECIAL_FRAME_MARGINS = {
    "Splitter": {"top": 0, "bottom": 0, "left": 1, "right": 1},
    "ScrollbarGroove": {"top": 0, "bottom": 0, "left": 4, "right": 4},
}

# The track and value controls: the SVG element Kvantum draws for each
# section's frame, interior and indicator, the two sections that ship no
# frame, and the progress bar's label styling. The generic
# art-existence check cannot see these: a wrong element name that happens to
# exist elsewhere in the SVG still passes it, while Kvantum renders the wrong
# control.
TRACK_CONTROL_CONFIG = {
    "Scrollbar": {
        "frame.element": "button",
        "interior.element": "button",
        "indicator.element": "arrow",
    },
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

# The container and text surface sections: the SVG element Kvantum draws
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
    "ToolboxTab": {
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
    "DockTitle": {
        "frame.element": "dock",
    },
    # `[TitleBar]` is the same `frame=false`-with-interior shape
    # `[MenuItem]` uses: the MDI subwindow's title band draws no frame
    # art, only the `titlebar` interior under its label.
    "TitleBar": {
        "frame": "false",
        "interior.element": "titlebar",
    },
}

# Sections that explicitly draw no frame or interior. `[TabBarFrame]` inherits
# `GenericFrame`, whose `common` element would frame the tab bar; its
# `frame=false`/`interior=false` suppress that, so removing either silently
# gives the tab bar a border. `[TreeExpander]` and `[StatusBar]` inherit
# framed sections too: the expander must draw only its branch arrow, and the
# status bar is a flat window-face bar with no bevel. `[SizeGrip]` also
# draws no frame or interior: it paints only its indicator element.
# `[Dock]` is the same flat window face: the docking area draws nothing so a
# dock panel's body keeps the bare window background. Their `inherits`
# targets are pinned here because, unlike the framed sections, their element
# mappings do not resolve through the inherited section: a wrong target
# would leave the branch indicator or window face unpinned. A section in
# neither this table nor the three element tables is unpinned, which
# `test_every_section_is_pinned` rejects.
FRAMELESS_SECTIONS = {
    "TabBarFrame": {"frame": "false", "interior": "false"},
    "TreeExpander": {
        "inherits": "PanelButtonCommand",
        "indicator.element": "arrow",
        "frame": "false",
        "interior": "false",
    },
    "StatusBar": {
        "inherits": "GenericFrame",
        "frame": "false",
        "interior": "false",
    },
    "Dock": {
        "inherits": "PanelButtonCommand",
        "frame": "false",
        "interior": "false",
    },
    "SizeGrip": {
        "indicator.element": "sizegrip",
    },
}

# The remaining settings that name no element and draw no frame margin, but
# still drive the rendered control: the indicator sizes Kvantum scales each
# arrow/grip to, the button and menu label colours, the text margins that
# place a label inside its control, the menu item's minimum height, the
# `text.shadow` flags, and `composite`. The element, frame-margin and
# frameless tables above pin what a section draws and where; these values were
# pinned by nothing, so changing one (say `indicator.size=9` to `12`, or a
# label colour) shipped unchecked. `test_every_key_is_pinned` keeps the tables
# exhaustive over the config, so a new setting without a pin fails here.
VALUE_KEYS = {
    "%General": {
        "composite": "true",
    },
    "PanelButtonCommand": {
        "frame": "true",
        "interior": "true",
        "indicator.size": "9",
        "text.normal.color": "#000000",
        "text.focus.color": "#000000",
        "text.press.color": "#000000",
        "text.toggle.color": "#000000",
    },
    "ComboBox": {
        "indicator.size": "12",
    },
    "CheckBox": {
        "text.margin.top": "2",
        "text.margin.bottom": "2",
        "text.margin.left": "3",
        "text.margin.right": "3",
    },
    "RadioButton": {
        "text.margin.top": "2",
        "text.margin.bottom": "2",
        "text.margin.left": "3",
        "text.margin.right": "3",
    },
    "Focus": {
        "interior": "false",
        "frame": "true",
    },
    "GenericFrame": {
        "frame": "true",
        "interior": "false",
    },
    "IndicatorArrow": {
        "indicator.size": "9",
    },
    "IndicatorSpinBox": {
        "indicator.size": "9",
    },
    "Splitter": {
        "indicator.size": "16",
    },
    "Tab": {
        "text.margin.left": "8",
        "text.margin.right": "8",
    },
    "MenuItem": {
        "min_height": "22",
        "text.focus.color": "#000000",
        "text.margin.top": "2",
        "text.margin.bottom": "2",
        "text.margin.left": "3",
        "text.margin.right": "3",
    },
    "MenuBarItem": {
        "text.margin.top": "2",
        "text.margin.bottom": "2",
    },
    "GroupBox": {
        "frame": "true",
        "interior": "true",
        "text.shadow": "false",
        "text.margin": "0",
    },
    "ToolTip": {
        "interior": "true",
        "text.shadow": "false",
        "text.margin": "0",
    },
    "DockTitle": {
        "frame": "true",
        "frame.top": "0",
        "frame.bottom": "2",
        "frame.left": "0",
        "frame.right": "0",
        "interior": "false",
        "text.normal.color": "#000000",
        "text.focus.color": "#000000",
        "text.margin.top": "2",
        "text.margin.bottom": "2",
        "text.margin.left": "3",
        "text.margin.right": "3",
    },
    "TitleBar": {
        "indicator.element": "mdi",
        "indicator.size": "12",
        "text.normal.color": "#000000",
        "text.focus.color": "#000000",
        "text.margin.top": "2",
        "text.margin.bottom": "2",
        "text.margin.left": "3",
        "text.margin.right": "3",
    },
}


def _scheme_hex(parser, section, name):
    """Return the `#RRGGBB` form of a MacOS8 color-scheme role."""
    value = parser.get(f"Colors:{section}", name)
    return hex_colour(tuple(int(part) for part in value.split(",")))


def _resolved(parser, section, key):
    """Return *section*'s *key* following `inherits` until it is found.

    A malformed `.kvconfig` can make the `inherits` chain loop (``[A]``
    inherits ``B`` and ``[B]`` inherits ``A``) with *key* defined by neither
    section; the walk would then never reach a leaf, hanging the suite with no
    diagnostic. The walk stops at the first repeated section and raises
    instead, naming the cycle.
    """
    seen: set[str] = set()
    while section is not None:
        if section in seen:
            raise ValueError(
                f"cyclic inherits chain in {section!r}: section reached twice "
                f"while resolving {key!r}"
            )
        seen.add(section)
        if parser.has_option(section, key):
            return parser.get(section, key)
        if parser.has_option(section, "inherits"):
            section = parser.get(section, "inherits")
        else:
            return None
    return None


def _assert_pins_resolve(case, table):
    """Assert every *table* pin resolves to its expected value.

    The core-control, track/value, surface and frameless tables all map a
    `.kvconfig` section to the keys it pins and the string each must resolve
    to; each test walks its table the same way, so this names that walk once.
    *case* is the calling ``TestCase``, so a mismatch fails against the right
    test.
    """
    parser = read_kde_config(KVCONFIG)
    for section, expected in table.items():
        for key, value in expected.items():
            with case.subTest(section=section, key=key):
                case.assertEqual(_resolved(parser, section, key), value)
