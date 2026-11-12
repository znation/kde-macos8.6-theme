"""GTK 4 calendar declaration and reference-palette checks."""

import unittest

from support import gtk_css
from support.gtk_css import parse_css
from support.gtk4_sheet import CSS, DEFINED_COLOURS, Gtk4SheetRuleCases
from support.gtk_theme_spec import CALENDAR_SELECTED_DAY
from support.aurorae_fixtures import PROFILER_REFERENCE, PROFILER_ROWS
from support.platinum_palette import BLACK, SELECTION, TROUGH, hex_colour
from support.reference_image import ReferenceScreenshotMixin


class TestGtk4Calendar(Gtk4SheetRuleCases, unittest.TestCase):
    def test_calendar(self):
        selected = "calendar > grid > label.day-number:selected"
        self.assert_rule(selected, {**CALENDAR_SELECTED_DAY, "border-radius": "0"})
        self.assert_rule("calendar > grid > label.day-number.other-month", {"color": "#888888"})
        self._assert_inactive_grey_from_scheme()
        self.assert_matches_frame(selected, "border-radius")

    def test_calendar_disabled_day_text(self):
        disabled = "calendar:disabled > grid > label.day-number"
        selected = "calendar > grid > label.day-number:selected"
        other_month = "calendar > grid > label.day-number.other-month"
        self.assert_rule(disabled, {"color": "#888888"})
        self.assertEqual(self.rules[disabled]["color"], self.rules["label:disabled"]["color"])
        self._assert_inactive_grey_from_scheme()
        self.assert_rule_after(disabled, selected)
        self.assert_rule_after(disabled, other_month)

    def test_calendar_disabled_selected_day_text(self):
        disabled_selected = "calendar > grid > label.day-number:disabled:selected"
        disabled = "calendar:disabled > grid > label.day-number"
        selected = "calendar > grid > label.day-number:selected"
        self.assert_disabled_text((disabled_selected,))
        self.assertEqual(self.rules[disabled_selected], {"color": "#888888"})
        self.assertEqual(self.rules[disabled_selected]["color"], self.rules[disabled]["color"])
        self.assertEqual(self.rules[selected]["background-color"], SELECTION)
        self.assert_rule_after(disabled_selected, selected)

    def test_calendar_today_underline(self):
        today = "calendar > grid > label.today"
        selected_today = "calendar > grid > label.today:selected"
        other_month = "calendar > grid > label.day-number.other-month"
        self.assert_rule(today, {"box-shadow": "inset 0 -2px #888888"})
        self.assert_rule(selected_today, {"box-shadow": "none"})
        self.assertEqual(self.rules[today]["box-shadow"].split()[-1], self.rules[other_month]["color"])
        self._assert_inactive_grey_from_scheme()

    def test_calendar_marked_day_corners(self):
        marked = "calendar > grid > label.day-number:checked"
        self.assert_rule(marked, {"border-radius": "0", "background-color": TROUGH})
        self.assert_matches_frame(marked, "border-radius")

    def test_calendar_marked_day_fill(self):
        marked = "calendar > grid > label.day-number:checked"
        selected = "calendar > grid > label.day-number:selected"
        trough = "scrollbar > range > trough"
        self.assertEqual(self.rules[marked]["background-color"], self.rules[trough]["background-color"])
        self.assertEqual(self.rules[selected]["background-color"], SELECTION)
        self.assert_rule_after(selected, marked)

    def test_calendar_outer_border(self):
        self.assert_rule("calendar", {"color": BLACK, "border": "1px solid #000000"})
        self.assert_matches_frame("calendar", "border")

    def test_calendar_foreground(self):
        self.assertEqual(self.rules["calendar"]["color"], BLACK)
        self.assertEqual(self.rules["calendar"]["color"], DEFINED_COLOURS["view_fg_color"])
        self.assertEqual(self.rules["calendar"]["color"], self.rules[".view"]["color"])

    def test_calendar_focus_outline(self):
        focus = "calendar > grid > label:focus"
        self.assert_rule(focus, {"outline-color": BLACK, "outline-width": "2px", "outline-offset": "-2px"})
        self.assertEqual(self.rules[focus]["outline-color"], BLACK)
        self.assertTrue(self.rules["calendar"]["border"].endswith(BLACK))

    def test_calendar_focus_transition(self):
        self.assert_rule("calendar > grid > label", {"transition": "none"})

    def test_calendar_header_separator(self):
        header = "calendar > header"
        infobar = "infobar > revealer > box"
        self.assert_rule(header, {"border-bottom": "1px solid #888888", "box-shadow": "inset 0 -1px #FFFFFF"})
        for prop in ("border-bottom", "box-shadow"):
            with self.subTest(property=prop):
                self.assertEqual(self.rules[header][prop], self.rules[infobar][prop])


class TestCalendarDisabledGreyReference(ReferenceScreenshotMixin, unittest.TestCase):
    REFERENCE = PROFILER_REFERENCE
    MAX_ROWS = PROFILER_ROWS

    def test_disabled_day_grey_matches_reference_palette_pixel(self):
        _, rules, _ = parse_css(gtk_css.read_theme_text(CSS))
        sampled = hex_colour(self.pixel(241, 103))
        for selector in (
            "calendar:disabled > grid > label.day-number",
            "calendar > grid > label.day-number:disabled:selected",
        ):
            with self.subTest(selector=selector):
                self.assertEqual(rules[selector]["color"], sampled)


if __name__ == "__main__":
    unittest.main()
