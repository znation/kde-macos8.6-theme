"""Shared GTK 4 stylesheet fixture and assertions for split suites."""

from __future__ import annotations

from pathlib import Path

from support.gtk_rule_cases import GtkSharedControlCases
from support.gtk_theme_spec import (
    BASE_DEFINED_COLOURS,
    BUTTON_BEVEL,
    DISABLED_TEXT,
    INVERTED_BUTTON_BEVEL,
)
from support.platinum_palette import BLACK, FACE, SELECTION, WHITE
from support.repo_root import ROOT

# The scale slider anchors the sheet's focus colour and its transition policy:
# every control that states an outline colour or a transition repeats the
# value the scale states, and these two selectors stay together.
THEME_ID = "org.macos8.desktop"

THEME_DIR = Path(ROOT) / "theme" / "gtk" / THEME_ID

CSS = THEME_DIR / "gtk-4.0" / "gtk.css"

DEFINED_COLOURS = {
    **BASE_DEFINED_COLOURS,
    "accent_bg_color": SELECTION,
    "accent_fg_color": BLACK,
    "theme_unfocused_selected_bg_color": SELECTION,
    "theme_unfocused_selected_fg_color": BLACK,
    "theme_unfocused_bg_color": FACE,
    "theme_unfocused_fg_color": BLACK,
    "theme_unfocused_base_color": WHITE,
    "theme_unfocused_text_color": BLACK,
    "window_bg_color": FACE,
    "window_fg_color": BLACK,
    "view_bg_color": WHITE,
    "view_fg_color": BLACK,
    "headerbar_bg_color": FACE,
    "headerbar_fg_color": BLACK,
    "headerbar_border_color": BLACK,
    "headerbar_backdrop_color": FACE,
    "popover_bg_color": FACE,
    "popover_fg_color": BLACK,
    "card_bg_color": FACE,
    "card_fg_color": BLACK,
    "dialog_bg_color": FACE,
    "dialog_fg_color": BLACK,
    "sidebar_bg_color": FACE,
    "sidebar_fg_color": BLACK,
    "sidebar_backdrop_color": FACE,
    "sidebar_border_color": BLACK,
    "secondary_sidebar_bg_color": FACE,
    "secondary_sidebar_fg_color": BLACK,
    "secondary_sidebar_backdrop_color": FACE,
    "secondary_sidebar_border_color": BLACK,
    "thumbnail_bg_color": WHITE,
    "thumbnail_fg_color": BLACK,
    "scrollbar_outline_color": BLACK,
}

SCALE_FOCUS = "scale:focus:focus-visible > trough > slider"

SCALE_SLIDER = "scale > trough > slider"

# The button family a header-style bar (headerbar, toolbar, actionbar,
# searchbar) hosts. Each bar's focus test prefixes these with its own
# container selector, so the family is spelled once here.
BAR_FAMILY_FOCUS_SUFFIXES = (
    "menubutton.suggested-action > button:focus:focus-visible:not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque)",
    "menubutton.opaque > button:focus:focus-visible:not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque)",
    "menubutton:not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque).image-button > button:focus:focus-visible",
    "button.arrow-button:focus:focus-visible:not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque)",
    "button.image-button:focus:focus-visible:not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque)",
    "button.image-text-button:focus:focus-visible:not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque)",
    "splitbutton:not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque) > button:focus:focus-visible",
    "splitbutton:not(.raised):not(.suggested-action):not(.destructive-action):not(.opaque) > menubutton > button:focus:focus-visible",
)

def _rgb(hexc):
    """Return the byte triple a palette hex spells, as a child pins it."""
    return tuple(int(hexc[i:i + 2], 16) for i in (1, 3, 5))



class Gtk4SheetRuleCases(GtkSharedControlCases):
    """GTK 4 sheet cases with shared constants and assertion helpers."""

    CSS_PATH = CSS

    def assert_scale_focus_outline(self, focus):
        """Assert *focus* states the black outline the scale focus states."""
        self.assert_rule(focus, {"outline-color": BLACK})
        self.assertEqual(
            self.rules[focus]["outline-color"],
            self.rules[SCALE_FOCUS]["outline-color"],
        )


    def assert_black_focus_outline(self, selectors):
        """Assert each of *selectors* appears once and states only the black
        focus outline, mirroring the base button focus outline's colour.

        The file-chooser breadcrumb, sidebar and emoji-section focus tests
        share this per-selector cell; each keeps its own family scan because
        each scans a different token. The header-style bars go through
        :meth:`assert_bar_family_focus`, which uses this cell too.
        """
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assertEqual(self.selectors.count(selector), 1)
                self.assertEqual(self.rules[selector], {"outline-color": BLACK})
                self.assertEqual(
                    self.rules[selector]["outline-color"],
                    self.rules["button:focus:focus-visible"]["outline-color"],
                )

    def assert_bar_family_focus(self, prefix, scan, extra=()):
        """Assert the focus selectors under *prefix* are exactly the bar's
        button family, plus *extra* suffixes, and each states the black outline.

        *scan* is the substring that picks the bar's focus selectors out of
        ``self.selectors``; the equality below fails on any selector it picks
        up beyond the expected set. Used by the headerbar, toolbar, actionbar
        and searchbar focus tests.
        """
        selectors = {prefix + suffix for suffix in BAR_FAMILY_FOCUS_SUFFIXES}
        selectors.update(prefix + suffix for suffix in extra)
        self.assertEqual(
            {
                selector
                for selector in self.selectors
                if scan in selector and ":focus:focus-visible" in selector
            },
            selectors,
        )
        self.assert_black_focus_outline(selectors)


    def assert_scale_anchored_focus_outline(self, selectors):
        """Assert each of *selectors* occurs once and states the black focus
        outline the scale focus anchor states.

        The view-child, residual and card focus tests share this
        per-selector cell; each keeps its own family scan because each
        scans a different token.
        """
        for selector in selectors:
            with self.subTest(selector=selector):
                self.assert_rule(selector, {"outline-color": BLACK})
                self.assertEqual(
                    self.rules[selector]["outline-color"],
                    self.rules[SCALE_FOCUS]["outline-color"],
                )
                self.assertEqual(self.selectors.count(selector), 1)


    def assert_scale_slider_transition(self, selector):
        """Assert *selector* keeps the no-transition the scale slider keeps."""
        self.assert_rule(selector, {"transition": "none"})
        self.assertEqual(
            self.rules[selector]["transition"],
            self.rules[SCALE_SLIDER]["transition"],
        )


    def assert_matches_frame(self, selector, prop):
        """Assert *selector*'s *prop* value matches each frame arm's.

        The square-corner tests anchor a container's paint to both spellings
        of the landed frame rule; this drives the paired assertion for each
        spelling in turn.
        """
        for frame in ("frame > border", ".frame"):
            with self.subTest(frame=frame):
                self.assertEqual(
                    self.rules[selector][prop],
                    self.rules[frame][prop],
                )


    def assert_square_corner(self, selector):
        """Assert *selector* carries exactly the square-corner rule.

        The rule is ``border-radius: 0`` and nothing else, and its radius
        matches both frame arms via ``assert_matches_frame``. Used by the
        square-corner families that restate the landed policy one selector
        at a time.
        """
        self.assertEqual(self.rules[selector], {"border-radius": "0"}, selector)
        self.assert_matches_frame(selector, "border-radius")


    def assert_plain_action_arms(self, prefix):
        # No reference screenshot shows a GTK colour-class action button;
        # the tail arms restate the landed plain push-button recipe, so
        # every checked relationship below anchors the landed face
        # constants. (The colour-class members are restated by
        # test_action_class_flat_arms.) Exactly two call
        # sites: the suggested- and destructive-action plain families.
        self.assert_rule(
            prefix,
            {
                "background-color": FACE,
                "background-image": "none",
                "border-color": BLACK,
                "box-shadow": BUTTON_BEVEL,
                "color": BLACK,
                "outline-color": BLACK,
                "transition": "none",
            },
        )
        self.assert_rule(
            f"{prefix}:hover",
            {
                "background-color": FACE,
                "background-image": "none",
                "border-color": BLACK,
                "box-shadow": BUTTON_BEVEL,
                "color": BLACK,
                "outline-color": BLACK,
            },
        )
        sunken = {
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": INVERTED_BUTTON_BEVEL,
            "color": BLACK,
            "outline-color": BLACK,
        }
        for selector in (f"{prefix}:active", f"{prefix}:checked"):
            self.assert_rule(selector, sunken)
        insensitive = {
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": BUTTON_BEVEL,
            "color": DISABLED_TEXT["color"],
        }
        for selector in (
            f"{prefix}:disabled",
            f"{prefix}:disabled:active",
            f"{prefix}:disabled:checked",
        ):
            self.assert_rule(selector, insensitive)
        self.assert_rule(
            f"{prefix}:focus:focus-visible",
            {"outline-color": BLACK},
        )
        self.assertEqual(
            self.rules[f"{prefix}:focus:focus-visible"]["outline-color"],
            self.rules["button:focus:focus-visible"]["outline-color"],
        )
        expected_selectors = {
            prefix,
            f"{prefix}:hover",
            f"{prefix}:active",
            f"{prefix}:checked",
            f"{prefix}:disabled",
            f"{prefix}:disabled:active",
            f"{prefix}:disabled:checked",
            f"{prefix}:focus:focus-visible",
        }
        # The `.flat`-suffixed colour-class selectors land through
        # test_action_class_flat_arms, so they stay out of the plain family
        # bound here.
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if selector.startswith(prefix) and ".flat" not in selector
            },
            expected_selectors,
        )


    def _assert_toast_matches_popover(self, selector):
        """Pin the toast's box properties to its popover family's."""
        for popover in ("popover > contents", "popover > arrow"):
            for prop in (
                "background-color", "border", "border-radius", "box-shadow"
            ):
                self.assertEqual(
                    self.rules[selector][prop], self.rules[popover][prop]
                )
        self.assertEqual(
            self.rules[selector]["color"], self.rules["window"]["color"]
        )
