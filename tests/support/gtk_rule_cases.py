"""Reusable GTK and Firefox sheet rule assertions and shared control cases.

The seven GTK sheet rule-cases classes parse their shipped stylesheet
through :class:`GtkSheetRuleCases`'s shared ``setUpClass``; the Firefox
sheet suite parses its own sheet, and these classes hold the rule
assertion all three use and the control rules the two GTK suites both
satisfy. The Platinum spec values they assert live in the sibling
``tests/support/gtk_theme_spec.py``.

:class:`SheetRuleAssertions` holds the rule assertions all three suites
use (the single-rule check and the grouped whole-rule check).
:class:`GtkSheetRuleCases` holds the control assertions the two GTK suites
share, and :class:`GtkSharedControlCases` holds the control test cases each
suite runs once against its own parsed sheet (suite-level test classes
inherit it so those cases do not repeat per split-out module).
GTK 3 and GTK 4 spell the same nodes differently, so the link, calendar,
infobar, progress-bar, level-bar, scale, switch, spin-button field,
menu-separator, menu-bar-title, frame, tree-header, expander-arrow,
submenu-arrow, text-selection, view-background, disabled-text, rubberband
and title-button assertions take
the suite's own selectors; the spinner assertion takes the rotation
transform instead, the color-swatch assertion takes the suite's overlay
relationship, and the standalone separators and paned handles are spelled
alike in both, so their assertions take none.
"""

from __future__ import annotations

import re
from pathlib import Path

from support import gtk_css
from support.colorscheme_fixtures import load_scheme
from support.desktoptheme_paths import MENUBARITEM_SVG
from support.gtk_css import parse_css
from support.repo_root import ROOT
from support.gtk_theme_spec import (
    BUTTON_BEVEL,
    CALENDAR_SELECTED_DAY,
    CHECK,
    CHECK_GLYPH,
    COMBO_ARROW,
    DISABLED_TEXT,
    ENTRY_FIELD,
    EXPANDER_COLLAPSED,
    EXPANDER_EXPANDED,
    FRAME,
    INFOBAR,
    INVERTED_BUTTON_BEVEL,
    LEVELBAR_TROUGH,
    LINK,
    LINK_BUTTON,
    LINK_TEXT,
    MENU_SEPARATOR,
    MENU_CHECK,
    MIXED_GLYPH,
    PANED_HANDLE_HORIZONTAL,
    PANED_HANDLE_VERTICAL,
    PROGRESSBAR_PROGRESS,
    PROGRESSBAR_TROUGH,
    RADIO,
    RADIO_GLYPH,
    RAISED_BEVEL,
    ROW_HOVER,
    ROW_SELECTED,
    RUBBERBAND,
    SCALE_EMPTY_FILL,
    SCALE_THUMB,
    SCALE_TROUGH,
    SEPARATOR_HORIZONTAL,
    SEPARATOR_VERTICAL,
    SPINNER_RULES,
    SUBMENU_ARROW,
    SWITCH_GLYPH,
    SWITCH_THUMB,
    SWITCH_THUMB_DISABLED,
    SWITCH_TRACK,
    SWITCH_TRACK_CHECKED,
    SWITCH_TRACK_DISABLED,
    TAB_STATES,
    TEXT_SELECTION,
    TITLE_BUTTON,
    TOOLTIP,
    TOOLTIP_BACKGROUND,
    TREE_HEADER,
    TREE_HEADER_ACTIVE,
    TREE_HEADER_HOVER,
    TREE_HEADER_LAST,
    VIEW_BACKGROUND,
    VISITED_LINK,
    VISITED_TEXT,
)
from support.platinum_palette import (
    BLACK,
    FACE,
    GREY,
    INACTIVE_OUTLINE,
    hex_colour,
)
from support.svg_case import parse_svg
from svg_assertions import rect_geometry


ROW_SELECTED_BUTTON_ARM_SIDEBAR = (
    "row:selected button.sidebar-button"
    ":not(:active):not(:checked):not(:hover):not(disabled):not(:disabled)"
)
ROW_SELECTED_BUTTON_ARM_FLAT = (
    "row:selected button.flat"
    ":not(:active):not(:checked):not(:hover):not(disabled):not(:disabled)"
)
ROW_SELECTED_BUTTON_ARM_SIDEBAR_BACKDROP = ROW_SELECTED_BUTTON_ARM_SIDEBAR + ":backdrop"
ROW_SELECTED_BUTTON_ARM_FLAT_BACKDROP = ROW_SELECTED_BUTTON_ARM_FLAT + ":backdrop"
ROW_SELECTED_BUTTON_ARM_SELECTORS = frozenset((
    "row:selected button",
    ROW_SELECTED_BUTTON_ARM_SIDEBAR,
    ROW_SELECTED_BUTTON_ARM_FLAT,
    ROW_SELECTED_BUTTON_ARM_SIDEBAR_BACKDROP,
    ROW_SELECTED_BUTTON_ARM_FLAT_BACKDROP,
))


class SheetRuleAssertions:
    """Rule assertions for suites that store the parsed sheet in ``self.rules``."""

    def assert_rule_group(self, expected):
        """Assert every selector in *expected* carries exactly its mapped rule, once.

        For each selector key: the parsed sheet counts it exactly once in
        ``self.selectors`` (as the mixing suites' ``setUpClass`` parses the
        selector list) and its whole declaration dictionary equals the mapped
        value byte-for-byte — the spelling and no extra declarations.
        """
        for selector, declarations in expected.items():
            with self.subTest(selector=selector):
                self.assertEqual(self.selectors.count(selector), 1, selector)
                self.assertEqual(self.rules[selector], declarations, selector)

    def assert_rule_after(self, later, earlier):
        """Assert *later* first appears after *earlier* in the parsed sheet.

        The GTK suites pin cascade precedence as a source-order comparison:
        an existing restatement beats a stock arm of equal specificity only by
        coming later in the sheet text, so a rule-order pin asserts which of
        two substrings ``self.css`` holds first. The two-operand pins across
        the GTK 3 and GTK 4 suites route through here; loop-anchor and
        offset-search probes keep their bespoke forms.
        """
        self.assertGreater(
            self.css.index(later),
            self.css.index(earlier),
            f"{later!r} does not follow {earlier!r} in the sheet",
        )

    def assert_rule(self, selector, expected):
        """Assert *selector* exists and carries each declaration in *expected*."""
        self.assertIn(selector, self.rules, f"missing rule for {selector}")
        for name, value in expected.items():
            self.assertEqual(
                self.rules[selector].get(name),
                value,
                f"{selector}: expected {name}: {value}",
            )


class GtkSheetRuleCases(SheetRuleAssertions):
    """The shared sheet setup and the control assertions the GTK sheets satisfy.

    A rule-cases class binds the setup to its shipped sheet with a
    ``CSS_PATH`` class attribute and inherits the parse; the six classes that
    carry no other class state set it alone, and the index-reader in
    tests/test_gtk_theme.py overrides this setup and chains to it with
    ``super`` (the one suite whose ``setUpClass`` loads a second file).

    Suites run their sheet's own parsed ``self.rules``. Selectors
    and values that differ between the sheets
    (window, notebook header, scrollbar, popover, toolbar) stay in the suite
    that owns them. GTK 3 and GTK 4 spell the same nodes differently, so the
    link, calendar, infobar, progress-bar, level-bar, scale, switch,
    spin-button field, menu-separator, menu-bar-title, frame, tree-header,
    expander-arrow, submenu-arrow, text-selection, view-background,
    disabled-text, rubberband and title-button assertions take the suite's
    own selectors; :meth:`assert_spinner` takes the rotation transform
    instead, :meth:`assert_color_swatch_corners` takes the suite's overlay
    relationship, and the standalone separators and paned handles are
    spelled alike in both, so ``assert_separators`` and
    ``assert_paned_handles`` take none.
    """

    @classmethod
    def setUpClass(cls):
        """Parse the sheet at ``cls.CSS_PATH`` onto cls.css/colours/rules/selectors.

        The seven GTK sheet classes each parse one shipped ``gtk.css`` into
        the same four class attributes: ``cls.css`` (the sheet text) and
        ``cls.colours``, ``cls.rules`` and ``cls.selectors`` (the parsed
        maps). This setup reads the file once per class and names it to
        ``parse_css`` by its repository-root-relative path, spelled exactly
        as the seven per-suite setups it replaces spelled it.
        """
        cls.css = gtk_css.read_theme_text(cls.CSS_PATH)
        cls.colours, cls.rules, cls.selectors = parse_css(
            cls.css, source=str(Path(cls.CSS_PATH).relative_to(ROOT))
        )

    def assert_row_selection_backdrop(self, selectors):
        for selector in selectors:
            self.assert_rule(selector, ROW_SELECTED)

    def assert_selected_row_button_arms(self, flat_stock_backdrop):
        """Assert the sheet-tail selected-row push-button arm block.

        A push button inside a selected row keeps reading black on the
        existing lavender fill with the existing raised and flat treatments:
        stock's three selected-row arms would paint an opaque button with
        a blue border and a flat button with a white label on the existing
        light selection fill and recolour the flat label near white in
        backdrop. The border arm ties stock by later source order; the
        label arms add :not(:disabled) and win by specificity, preserving
        deferred disabled states: stock's :not(disabled) excludes a node
        name, not a state. The block is spelled
        identically in both shipped sheets. Both suites run this whole assertion; the only
        suite-owned input is *flat_stock_backdrop*, each toolkit's own
        spelling of the plain flat-backdrop selector.
        """
        self.assert_rule("row:selected button", {"border-color": BLACK})
        for selector in (
            ROW_SELECTED_BUTTON_ARM_SIDEBAR,
            ROW_SELECTED_BUTTON_ARM_FLAT,
        ):
            self.assert_rule(selector, {"color": BLACK, "border-color": BLACK})
        for selector in (
            ROW_SELECTED_BUTTON_ARM_SIDEBAR_BACKDROP,
            ROW_SELECTED_BUTTON_ARM_FLAT_BACKDROP,
        ):
            self.assert_rule(selector, {"color": BLACK})
        self.assertEqual(
            self.rules[ROW_SELECTED_BUTTON_ARM_FLAT_BACKDROP]["color"],
            self.rules[flat_stock_backdrop]["color"],
        )
        self.assertEqual(
            {
                selector
                for selector in self.rules
                if selector.startswith("row:selected button")
            },
            ROW_SELECTED_BUTTON_ARM_SELECTORS,
        )

    def assert_button_disabled_and_backdrop(self):
        """Assert the existing insensitive and unfocused-window button faces.

        Unfocused windows dim no existing push button: the suites'
        backdrop states restate the existing raised and sunken bevels with
        black labels and no transition, and the six-member disabled group
        keeps the raised bevel with :data:`DISABLED_TEXT`'s insensitive
        grey label and no backdrop state of its own. Both suites run this
        whole assertion; nothing in it is suite-owned.
        """
        self.assert_rule(
            "button:backdrop",
            {
                "background-image": "none",
                "border-color": BLACK,
                "box-shadow": BUTTON_BEVEL,
                "color": BLACK,
                "transition": "none",
            },
        )
        for selector in ("button:backdrop:active", "button:backdrop:checked"):
            self.assert_rule(
                selector,
                {
                    "background-image": "none",
                    "border-color": BLACK,
                    "box-shadow": INVERTED_BUTTON_BEVEL,
                    "color": BLACK,
                    "transition": "none",
                },
            )
        for selector in (
            "button:disabled",
            "button:disabled:active",
            "button:disabled:checked",
            "button:backdrop:disabled",
            "button:backdrop:disabled:active",
            "button:backdrop:disabled:checked",
        ):
            self.assert_rule(
                selector,
                {
                    "background-image": "none",
                    "border-color": BLACK,
                    "box-shadow": BUTTON_BEVEL,
                    "color": DISABLED_TEXT["color"],
                },
            )

    def assert_tab_faces(self, forms=None):
        """Assert each tab state's Platinum notebook-face rule.

        Every selected tab state (``base``, ``hover``, ``checked``,
        ``checked+hover``, ``backdrop``, ``backdrop+checked`` in
        :data:`TAB_STATES`) carries the same face: the raised bevel on the
        unselected states, and on the checked states a bottom border merged
        into the face with the bevel dropped. When *forms* is given, it
        maps a subset of those state names to the selectors to check for
        each — the suites' path-bar and stack-switcher tabs spell their own
        selectors and skip the states their widget lacks; without it every
        :data:`TAB_STATES` selector is checked, as the plain tabs are
        spelled alike in both sheets.
        """
        for state, selectors, checked in TAB_STATES:
            if forms is not None and state not in forms:
                continue
            expected = {
                "background-color": FACE,
                "background-image": "none",
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
            }
            if checked:
                expected["border-bottom-color"] = FACE
                expected["box-shadow"] = "none"
            else:
                expected["box-shadow"] = RAISED_BEVEL
            for selector in (forms[state] if forms is not None else selectors):
                with self.subTest(state=state, selector=selector):
                    self.assert_rule(selector, expected)

    def assert_dotted_focus_outline(self, selector, anchor="button:focus"):
        """Assert *selector* carries the sheet's dotted focus outline.

        The GTK 3 sheet gives every focusable control the same
        ``1px dotted`` outline; thirteen ``:focus`` selectors copy
        ``button:focus`` (or a sibling rule passed as *anchor*), and each
        badge pins the literal declarations and the copy through this
        helper. The scale and button focus tests stay inline because each
        ties additional properties to other rules.
        """
        self.assert_rule(
            selector,
            {
                "outline": f"1px dotted {BLACK}",
                "outline-offset": "0",
                "-gtk-outline-radius": "0",
            },
        )
        for property_name in ("outline", "outline-offset", "-gtk-outline-radius"):
            self.assertEqual(
                self.rules[selector][property_name],
                self.rules[anchor][property_name],
            )

    def assert_color_swatch_corners(self, overlay_suffix, extra_declarations=None):
        """Check square swatch rules using the suite's overlay relationship."""
        roots = (
            "colorswatch",
            "colorswatch.top",
            "colorswatch.bottom",
            "colorswatch.left",
            "colorswatch.right",
            "colorswatch:first-child:not(.top)",
            "colorswatch:last-child:not(.bottom)",
            "colorswatch#add-color-button",
            "colorswatch#add-color-button:only-child",
            "colorswatch#editor-color-sample",
        )
        expected = set(roots) | {root + overlay_suffix for root in roots}
        corner_selectors = expected.copy()
        extra_declarations = extra_declarations or {}
        expected.update(extra_declarations)
        self.assertEqual(
            {selector for selector in self.rules if "colorswatch" in selector},
            expected,
        )
        for selector in sorted(expected):
            with self.subTest(selector=selector):
                declarations = (
                    {"border-radius": "0"} if selector in corner_selectors else {}
                )
                declarations.update(extra_declarations.get(selector, {}))
                self.assertEqual(self.rules[selector], declarations)

    def assert_progressbar(self, trough, progress, disabled):
        """Assert the shared progress-bar spec against this sheet's selectors."""
        self.assert_rule(trough, PROGRESSBAR_TROUGH)
        self.assert_rule(progress, PROGRESSBAR_PROGRESS)
        self.assert_rule(disabled, {"background-color": GREY})

    def assert_levelbar(self, trough, filled, empty, disabled, horizontal, vertical):
        """Assert the level bar paints as the progress bar, sized by its blocks."""
        self.assert_rule(trough, LEVELBAR_TROUGH)
        for prop in ("min-height", "min-width"):
            self.assertNotIn(prop, self.rules[trough])
        self.assert_rule(filled, PROGRESSBAR_PROGRESS)
        self.assert_rule(empty, SCALE_EMPTY_FILL)
        self.assert_rule(disabled, {"background-color": GREY})
        self.assert_rule(horizontal, {"min-height": "10px"})
        self.assert_rule(vertical, {"min-width": "10px"})

    def assert_spinner(self, transform):
        """Assert a running spinner rotates the icon theme's icon, a stopped one hides."""
        for selector, spec in SPINNER_RULES.items():
            self.assert_rule(selector, spec)
        # parse_css files a nested keyframe block under a bare ``to`` selector,
        # so the keyframe is checked against the raw text.
        self.assertRegex(
            gtk_css.strip_comments(self.css),
            r"@keyframes\s+spin\s*\{\s*to\s*\{\s*"
            + re.escape(transform)
            + r"\s*:\s*rotate\(1turn\)\s*;?\s*\}\s*\}",
        )

    def assert_separators(self):
        """Assert the etched standalone separators in both orientations."""
        for selector, spec in (
            ("separator.horizontal", SEPARATOR_HORIZONTAL),
            ("separator.vertical", SEPARATOR_VERTICAL),
        ):
            self.assert_rule(selector, spec)
            self.assertNotIn("margin", self.rules[selector])

    def assert_paned_handles(self):
        """Assert the etched paned split handles in both orientations."""
        self.assert_rule("paned.horizontal > separator", PANED_HANDLE_HORIZONTAL)
        self.assert_rule("paned.vertical > separator", PANED_HANDLE_VERTICAL)

    def assert_menu_separator(self, selectors):
        """Assert the Platinum etched menu separator against *selectors*."""
        for selector in selectors:
            self.assert_rule(selector, MENU_SEPARATOR)

    def assert_frame(self, selectors):
        """Assert the sunken frame bevel against *selectors*."""
        for selector in selectors:
            self.assert_rule(selector, FRAME)

    def assert_text_selection(self, selectors):
        """Assert the selected-text fill against *selectors*."""
        for selector in selectors:
            self.assert_rule(selector, TEXT_SELECTION)

    def assert_view_background(self, selectors):
        """Assert the white view fill against the view *selectors*."""
        for selector in selectors:
            self.assert_rule(selector, VIEW_BACKGROUND)

    def assert_disabled_text(self, selectors):
        """Assert the inactive grey against *selectors*, and re-derive it."""
        for selector in selectors:
            self.assert_rule(selector, DISABLED_TEXT)
        self._assert_inactive_grey_from_scheme()

    def _assert_inactive_grey_from_scheme(self):
        rgb = load_scheme().get("Colors:Button", "ForegroundInactive")
        self.assertEqual(
            hex_colour([int(part) for part in rgb.split(",")]),
            DISABLED_TEXT["color"],
        )

    def assert_calendar(self, selected, other_month):
        """Assert the calendar's selected-day fill and other-month grey."""
        for selector in selected:
            self.assert_rule(selector, CALENDAR_SELECTED_DAY)
        for selector in other_month:
            self.assert_rule(selector, DISABLED_TEXT)
        self._assert_inactive_grey_from_scheme()

    def assert_scheme_link_colours(self):
        """Assert the colour scheme carries the GTK link colours in Window.

        The sheets pin the link and visited inks to the scheme's Window
        ForegroundLink and ForegroundVisited roles (Kvantum's link.color and
        link.visited.color too), so the link suites re-derive both here.
        """
        scheme = load_scheme()
        for key, expected in (
            ("ForegroundLink", LINK),
            ("ForegroundVisited", VISITED_LINK),
        ):
            rgb = scheme.get("Colors:Window", key)
            self.assertEqual(
                hex_colour([int(part) for part in rgb.split(",")]), expected
            )

    def assert_links(self, button, link, visited, underline):
        """Assert faceless link buttons and the coloured link text.

        *button*, *link* and *visited* are selector tuples; *underline* is the
        toolkit's underline declaration. Both colours are re-derived from the
        colour scheme.
        """
        self.assert_scheme_link_colours()
        for selector in button:
            self.assert_rule(selector, LINK_BUTTON)
        for selector in link:
            self.assert_rule(selector, {**LINK_TEXT, **underline})
        for selector in visited:
            self.assert_rule(selector, VISITED_TEXT)

    def assert_rubberband(self, selectors):
        """Assert the dotted, unfilled marquee against *selectors*."""
        for selector in selectors:
            self.assert_rule(selector, RUBBERBAND)

    def assert_infobar(self, selectors):
        """Assert the menu-bar band's infobar paint against *selectors*."""
        for selector in selectors:
            self.assert_rule(selector, INFOBAR)

    def assert_spin_button_field(self, selectors):
        """Assert the entry field against the spin-button *selectors*."""
        for selector in selectors:
            self.assert_rule(selector, ENTRY_FIELD)

    def assert_scale(
        self, trough, fill, slider, horizontal, vertical, disabled
    ):
        """Assert the shared scale spec against this sheet's selectors.

        *fill* is a tuple of the empty-fill selectors; the slider's hover and
        active states are derived from *slider*.
        """
        self.assert_rule(trough, SCALE_TROUGH)
        for selector in fill:
            self.assert_rule(selector, SCALE_EMPTY_FILL)
        self.assert_rule(slider, {**SCALE_THUMB, "margin": "-5px"})
        self.assert_rule(horizontal, {"min-width": "12px", "min-height": "16px"})
        self.assert_rule(vertical, {"min-width": "16px", "min-height": "12px"})
        for selector in (f"{slider}:hover", f"{slider}:active"):
            self.assert_rule(selector, SCALE_THUMB)
        self.assert_rule(
            disabled,
            {
                "background-color": FACE,
                "border": f"1px solid {GREY}",
                "box-shadow": "none",
            },
        )

    def assert_scale_popup_buttons(self):
        """Assert the GTK 3 OSD suite's scale-popup button pins here.

        The GTK 3 OSD suite carries the sheet's two ``scale-popup``
        button pins: the flat pop-up member squared with a solid border,
        the hover member armed with the existing ``FACE`` and a square
        radius, and the member inventory naming those two
        ``scale-popup`` button spellings and nothing else. (The GTK 4
        suite's own case restates the full push-button recipe at each
        arm, because the GTK 4 sheet has no restated ``.osd
        button.flat`` family, so its pins live inline there.) The suite
        resolves to this body through its one-line named wrapper.
        """
        self.assertEqual(
            self.rules[".osd .scale-popup button.flat"],
            {"border-style": "solid", "border-radius": "0"},
        )
        self.assertEqual(
            self.rules[".scale-popup button:hover"],
            {"background-color": FACE, "border-radius": "0"},
        )
        self.assertEqual(
            {selector for selector in self.rules
             if "scale-popup" in selector and "button" in selector},
            {".osd .scale-popup button.flat", ".scale-popup button:hover"},
        )

    def assert_switch(self, slider, disabled_slider, glyph):
        """Assert the shared switch spec against this sheet's selectors."""
        self.assert_rule("switch", SWITCH_TRACK)
        self.assert_rule("switch:checked", SWITCH_TRACK_CHECKED)
        self.assert_rule("switch:disabled", SWITCH_TRACK_DISABLED)
        self.assert_rule(slider, SWITCH_THUMB)
        self.assert_rule(disabled_slider, SWITCH_THUMB_DISABLED)
        self.assert_rule(glyph, SWITCH_GLYPH)

    def assert_title_button(self, selector, asset):
        """Assert the Aurorae box in a 16px hit area with *asset* behind it."""
        self.assert_rule(selector, TITLE_BUTTON)
        self.assert_rule(
            selector, {"background-image": f'url("../assets/{asset}")'}
        )

    def assert_tree_header(self, selectors):
        """Assert the raised header face, its states and the last-column grid."""
        for selector in selectors:
            self.assert_rule(selector, TREE_HEADER)
            self.assert_rule(f"{selector}:hover", TREE_HEADER_HOVER)
            self.assert_rule(f"{selector}:active", TREE_HEADER_ACTIVE)
            self.assert_rule(f"{selector}:last-child", TREE_HEADER_LAST)

    def assert_expander_arrows(self, collapsed, expanded):
        """Assert the right (collapsed) and down (checked) disclosure arrows."""
        for selector in collapsed:
            self.assert_rule(selector, EXPANDER_COLLAPSED)
        for selector in expanded:
            self.assert_rule(selector, EXPANDER_EXPANDED)

    def assert_submenu_arrow(self, selectors, sized):
        """Assert the submenu arrow icon, and the 16px box when *sized*."""
        for selector in selectors:
            self.assert_rule(selector, SUBMENU_ARROW)
            if sized:
                self.assert_rule(
                    selector, {"min-width": "16px", "min-height": "16px"}
                )

    def assert_menubar_titles(self, selector):
        """Assert *selector* pads a title with the menubaritem SVG's margins."""
        geometry = rect_geometry(parse_svg(MENUBARITEM_SVG))
        top = geometry["normal-hint-top-margin"][3]
        left = geometry["normal-hint-left-margin"][2]
        self.assert_rule(selector, {"padding": f"{top}px {left}px"})


class GtkSharedControlCases(GtkSheetRuleCases):
    """The control test cases the two GTK suites run against their own sheets.

    Each suite-level class inherits these cases once, so a suite like the
    GTK 3 theme's ``TestGtkTheme`` runs them exactly once however many
    module-level split-out classes share its assertions; the other split
    classes subclass :class:`GtkSheetRuleCases` directly.
    """

    def assert_infobar_message_type_ban(self, selectors=None):
        """Assert no swept ``infobar`` selector names a message type.

        *selectors* defaults to this sheet's full selector inventory so
        both GTK sheets' ``test_infobar`` cases sweep everything; call
        sites may pass a narrower family instead to restate the ban over
        its own members. The ban covers infobar selectors alone because
        the restated entry colour-class twins carry ``.warning``/
        ``.error`` spellings, and only ``infobar``-containing selectors
        name no message type.
        """
        if selectors is None:
            selectors = self.selectors
        for message_type in (".info", ".question", ".warning", ".error"):
            for selector in selectors:
                if "infobar" in selector:
                    self.assertNotIn(message_type, selector, message_type)

    def test_headerbar(self):
        for selector in ("headerbar", ".titlebar"):
            self.assert_rule(
                selector,
                {
                    "background-color": FACE,
                    "background-image": "none",
                    "border": f"1px solid {BLACK}",
                    "border-radius": "0",
                    "box-shadow": "none",
                    "min-height": "22px",
                    "padding": "0 4px",
                },
            )
        self.assert_rule("headerbar", {"border-width": "0 0 1px 0"})
        for selector in ("headerbar:backdrop", ".titlebar:backdrop"):
            self.assert_rule(
                selector,
                {
                    "background-color": FACE,
                    "background-image": "none",
                    "border-color": INACTIVE_OUTLINE,
                    "box-shadow": "none",
                    "color": GREY,
                },
            )

    def test_button(self):
        self.assert_rule(
            "button",
            {
                "background-color": FACE,
                "background-image": "none",
                "border": f"1px solid {BLACK}",
                "border-radius": "0",
                "box-shadow": BUTTON_BEVEL,
            },
        )
        self.assert_rule("button:hover", {"background-color": FACE})
        for selector in ("button:active", "button:checked"):
            self.assert_rule(selector, {"box-shadow": INVERTED_BUTTON_BEVEL})

    def test_entry(self):
        self.assert_rule("entry", ENTRY_FIELD)

    def test_check_and_radio(self):
        self.assert_rule("check", CHECK)
        self.assert_rule("radio", RADIO)
        self.assert_rule("check:checked", CHECK_GLYPH)
        self.assert_rule("radio:checked", RADIO_GLYPH)
        self.assert_rule("check:indeterminate", MIXED_GLYPH)
        self.assert_rule("radio:indeterminate", MIXED_GLYPH)

        # The plain state-twin arms keep the existing face under
        # every state: each suite's sheet restates the toolkit's plain
        # element-level state arms (quoted verbatim in the sheet-tail
        # comment and in docs/invariants.md) with the existing check and
        # radio faces' fill, border colour and shadow pair -- no geometry,
        # ink, glyph, radius or clip restatement (one transition reach:
        # the no-fade rule erases the stock 200ms backdrop fade
        # on the two bare :backdrop groups). The scanned
        # parser merges each checked and indeterminate spelling's face
        # blocks into the existing glyph spelling's dictionary, so the four
        # merged keys pin the glyph union and the other spellings land in
        # one block each. The suites carry the same plain dictionaries;
        # the GTK 3 sheet adds the three plain :backdrop face arms its
        # toolkit resource declares and the GTK 4 resource lacks.
        check_face = {
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": CHECK["box-shadow"],
        }
        check_checked_face = {**check_face, "background-color": FACE}
        radio_face = {
            "background-image": "none",
            "border-color": BLACK,
            "box-shadow": "none",
        }
        expected = {
            "check:hover": check_face,
            "radio:hover": radio_face,
            "check:active": check_face,
            "radio:active": radio_face,
            "check:disabled": check_face,
            "radio:disabled": radio_face,
            "check:checked": {**CHECK_GLYPH, **check_checked_face},
            "radio:checked": {**RADIO_GLYPH, **radio_face},
            "check:checked:hover": check_checked_face,
            "radio:checked:hover": radio_face,
            "check:checked:active": check_checked_face,
            "radio:checked:active": radio_face,
            "check:checked:disabled": check_checked_face,
            "radio:checked:disabled": radio_face,
            "check:indeterminate": {**MIXED_GLYPH, **check_checked_face},
            "radio:indeterminate": {**MIXED_GLYPH, **radio_face},
            "check:indeterminate:hover": check_checked_face,
            "radio:indeterminate:hover": radio_face,
            "check:indeterminate:active": check_checked_face,
            "radio:indeterminate:active": radio_face,
            "check:indeterminate:disabled": check_checked_face,
            "radio:indeterminate:disabled": radio_face,
        }
        merged = (
            "check:checked",
            "radio:checked",
            "check:indeterminate",
            "radio:indeterminate",
        )
        if "gtk-3.0" in str(self.CSS_PATH):
            # The no-fade rule erases the stock 200ms
            # backdrop fade on the two bare :backdrop groups only, so the
            # checked and indeterminate :backdrop twins read unchanged.
            expected.update(
                {
                    "check:backdrop": {**check_face, "transition": "none"},
                    "radio:backdrop": {**radio_face, "transition": "none"},
                    "check:checked:backdrop": check_checked_face,
                    "radio:checked:backdrop": radio_face,
                    "check:indeterminate:backdrop": check_checked_face,
                    "radio:indeterminate:backdrop": radio_face,
                }
            )
        for selector, declarations in expected.items():
            with self.subTest(selector=selector):
                self.assertEqual(
                    self.selectors.count(selector),
                    2 if selector in merged else 1,
                )
                self.assertEqual(self.rules[selector], declarations)

        # The existing out-of-reach provenance stays: the suite's menu-check
        # keys keep their existing bare-glyph dictionaries and the existing OSD
        # pressed indicators keep the recipe properties their own record
        # pins (the full dictionaries differ between the two sheets'
        # stock-cleared shadow twins, so this pins the recipe surface per
        # property).
        if "gtk-3.0" in str(self.CSS_PATH):
            menu_keys = (
                "menu menuitem check",
                "menu menuitem radio",
                "popover modelbutton check",
                "popover modelbutton radio",
            )
        else:
            menu_keys = (
                "popover modelbutton check",
                "popover.background modelbutton check",
                "popover modelbutton radio",
                "popover.background modelbutton radio",
            )
        for selector in menu_keys:
            with self.subTest(selector=selector):
                self.assertEqual(self.rules[selector], MENU_CHECK)
        osd_pins = (
            (".osd check:active", CHECK),
            (".osd radio:active", RADIO),
        )
        for selector, recipe in osd_pins:
            with self.subTest(selector=selector):
                for name in ("background-color", "box-shadow", "border-radius"):
                    self.assertEqual(self.rules[selector][name], recipe[name])
                self.assertEqual(self.rules[selector]["outline-color"], BLACK)

    def test_combobox_arrow(self):
        self.assert_rule("combobox arrow", COMBO_ARROW)

    def test_tooltip(self):
        self.assert_rule("tooltip", TOOLTIP)
        self.assert_rule("tooltip.background", TOOLTIP_BACKGROUND)

    def test_row_hover(self):
        for selector in ("treeview.view:hover", "list row.activatable:hover"):
            self.assert_rule(selector, ROW_HOVER)

    def test_row_selection(self):
        for selector in (
            "treeview.view:selected",
            "treeview.view:selected:hover",
            "list row.activatable:selected",
            "list row.activatable:selected:hover",
        ):
            self.assert_rule(selector, ROW_SELECTED)

        self.assert_tab_faces()

    def test_tab_states(self):
        """Assert the plain tabs' TAB_STATES faces under their named pointer.

        The suite's invariant rows cite the named share case
        ``tests/support/gtk_rule_cases.py::GtkSharedControlCases::test_tab_states``;
        the assertion body itself lives in :meth:`assert_tab_faces`, so the
        named case and the stack-switcher/path-bar forms share one recipe and
        stay byte-identical in assertion.
        """
        self.assert_tab_faces()

    def assert_separator_label_foreground(self):
        """Assert the separator label's opaque inactive grey, once per suite.

        Both control suites carry the same ``label.separator`` pin (an
        opaque ``DISABLED_TEXT`` grey with no text shadow, one spelling)
        against their own sheets; the two wrappers live in the suites so
        each keeps its named invariant pointer, and this is where the
        assertion body itself lives.
        """
        selector = "label.separator"
        self.assert_disabled_text((selector,))
        self.assertEqual(
            self.rules[selector],
            {**DISABLED_TEXT, "opacity": "1", "text-shadow": "none"},
        )
        self.assertEqual(self.selectors.count(selector), 1)
