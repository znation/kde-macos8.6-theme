# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned


**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; landed-plan facts re-trimmed 2026-10-23
by the clean role; validation scope clarified 2026-10-25 by the steward role; Firefox artifact
and content-surface status updated 2026-10-26 by the steward role; install-firefox
file list corrected 2026-10-27 by the steward role; shipped-SVG count updated
2026-10-27 by the feature role):** The
initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (thirty-one widget SVGs under
`widgets/`, including the `widgets/margins-highlight.svg` panel edit-mode margin highlight and the
`widgets/containment-controls.svg` panel resize and slider handles, plus
`dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
collapse boxes); the desktop wallpaper package; the `org.macos8.desktop` icon theme (our own
final, non-infringing 32x32 Platinum-style art for the desktop's hard-disk, folder, document,
Trash and full-Trash icons, plus the menu bar's kicker logo `start-here-kde-symbolic` and the
`go-next-symbolic` submenu arrow, our own marks rather than Apple's;
`PLACEHOLDERS.md` records no remaining placeholders); the `org.macos8.desktop` Kvantum widget
style (Platinum palette and core-control art); the
`org.macos8.desktop` Lato font package (Lato Regular and Bold, the Debian copyright file
carrying the upstream SIL OFL 1.1 body, and the provenance record; installed by `make install`,
and the global theme selects its `Lato` family for the general, menu, toolbar, smallest-readable
and window-title fonts, while monospaced text keeps the user's fixed font); the GTK 3 and GTK 4
Platinum stylesheets under `theme/gtk/` (installed by the opt-in `install-gtk` target and
selected by `apply-gtk`; `make install` copies no GTK files); the standalone Firefox Platinum
sheets under `theme/firefox/` (its `userChrome.css` and `userContent.css` copied, and its
profile preference written, only by the opt-in `install-firefox` target); and the render and
fidelity tooling.
The live reference-comparison gate in `tests/test_render_surface.py` checks Aurorae window-chrome
regions when its render prerequisites are available (README.md, "Fidelity checking").
Firefox's `tests/test_firefox_theme_*.py` modules check stylesheet declarations;
those checks do not establish rendered Firefox pixels. Keep this distinction when assessing
progress toward pixel-perfect application chrome. README.md describes the reference set as the
source of truth for "menu bar, window chrome, widget metrics, icons and colour palette". The
prompt's surfaces and their status are each tracked here (updated 2026-10-21 by the
steward role): a **Qt widget style** for KDE applications (the desktop theme styles only
Plasma shell widgets, so a KDE app's own buttons, menus and scroll bars would keep the Breeze look) is served
by the global theme's selection of our Kvantum theme: the user answered
2026-10-18 that a pixel-matched Platinum style should ship as a Kvantum theme (a new
dependency) — shipped as the four-part "Mac OS 8.6 Kvantum widget style" series (each part
waited on the one before); a **cursor theme** was out of scope on 2026-10-17 because no reference
screenshot shows a cursor, so no pixel ground truth exists to match; on 2026-10-23 the plan role
queued it anyway as the theme's own Platinum-style pointer set (black-face, white-outline arrow,
text I-beam, pointing hand, busy hourglass, move cross, horizontal and vertical resize arrows,
NW-SE and NE-SW diagonal resize arrows, crosshair, circle-slash, drag-and-drop copy plus,
open and closed hands, the help question-mark arrow, the progress arrow with a small hourglass,
a pencil, the `zoom-in`/`zoom-out` magnifiers, and the drag-and-drop/forbidden aliases, not
traced from Apple's artwork), it
has landed inside the icon theme package with its provenance exception recorded in
`docs/invariants.md`, and `make apply-cursor`/`make remove-cursor` link it into the Xcursor path
and select it; Xcursor roles the theme does not name still come from the fallback cursor
theme; **system sounds** are out
of scope (not a visual surface, so the reference set cannot ground them); and a **lock screen** is
out of scope unless a broader login/lock-screen plan is taken up (QUESTIONS.md, answered
2026-10-21). The
shipped work should not be treated as the whole of the prompt.

Two answers on 2026-10-19 widen the scope again, and both are being implemented in series.
**GTK applications and Firefox** are in scope (QUESTIONS.md, answered 2026-10-19) as a
four-part series: parts 1/4 (GTK 3 Platinum theme) and 2/4 (GTK 4/libadwaita stylesheet) have
landed, and part 3/4 has landed as three entries — the opt-in install (parts 1/3 and 2/3) and
the selection (part 3/3) — while part 4/4 is split into two runs: part 1/2 (the
Firefox `userChrome.css` stylesheet) has landed and part 2/2 (the profile install plus the
preference) has landed. **The UI font** is to be vendored
(QUESTIONS.md, answered 2026-10-19) as a three-part series: part 1/3 vendors Lato as the
Charcoal-style body face and has landed (installed and selected by the global theme); part 2/3
(a Chicago-style menu face, whose redistribution licence is still unresolved) is not planned
yet; and part 3/3 (selecting the installed family in KDE/Plasma/Qt) has landed for the Lato
body face only, because Lato is the only family the package installs. KDE, Plasma and Qt
applications now use Lato for the general, menu, toolbar, smallest-readable and window-title
fonts, and monospaced text keeps the user's fixed font; GTK and Firefox
applications keep their own chrome unless the opt-in GTK targets or the Firefox userChrome
install are used (the GTK entries have landed, and Firefox chrome is part 1/2, which has
landed, while its profile install is part 2/2, which has landed). Firefox work since that
series landed as single-surface chrome plans (the downloads-panel and all-tabs rows, the
sidebar frame, the menu-bar title box, the tab faces and the app-menu rows), and it now
reaches a content page: the `userContent.css` sheet paints the about:downloads
list (part 1/2), and its opt-in profile install as part 2/2 has also landed. That is an
extension of the
2026-10-19 "style Firefox" answer rather than the brief's KDE/Plasma desktop UI, so it is
recorded here to keep the scope deliberate.

_None yet._

### Firefox Platinum content: paint about:telemetry's page furniture — the category sidebar rows, the section-filter search field and store menu and the ping-picker panel — with the landed nav-row, line-edit, menulist and panel recipes (planned 2026-10-27 by the plan role; the recorded first half of the about:telemetry work — the data payloads, the sections' tables, the histogram bars, the copy buttons and the raw-JSON viewers, are the natural subjects of a later plan whose reuse of this plan's furniture recipes and this page's remaining surfaces is decided then, so no design question is left open here; independent of the queued about:networking sidebar plan — the two touch the same sheet and test module, so all anchors below are rule texts and symbol names, never line numbers)

**Goal.** The landed `userContent.css` sheet paints the about:downloads list, the about:config field, the about:preferences pane, the about:support tables and buttons and the about:networking tables and buttons; Firefox's about:telemetry page keeps its stock paint entirely. This plan paints the page's furniture: its `#categories` sidebar rows (including the dynamically added `.category-subsection` rows), the `.header` strip's `#search` filter field and `#stores` store menu, and the floating `#ping-picker` panel each take the landed recipe byte-for-byte, reusing only values the sheet and test module already pin, so no new constant and no new hex is introduced and no landed rule changes. The sections' data payloads stay stock here.

**Verified facts (checked 2026-10-27, Firefox ESR 153.5.1; probe scratch at `/tmp/tum-scratch-omz/omni`).** `chrome/toolkit/content/global/aboutTelemetry.xhtml` is the light-DOM page (no `attachShadow` in it, its `.css` or its `.js`): `div#categories` holds fourteen static `div.category.category-no-icon` rows each wrapping `span.category-name`, the first carrying `class="category category-no-icon has-data selected"` at load, and `aboutTelemetry.css`'s `.category:not(.has-data) { display: none }` hides every row until data exists, so the paint need not special-case the badge. `aboutTelemetry.js` flips the selection with the CLASS, never an attribute (unlike about:networking's `[selected]`-attribute-only rule): `current_button = document.querySelector(".category.selected"); current_button.classList.remove("selected"); selected.classList.add("selected")`, and `showSubSection` does the same with `.category-subsection.selected`; the subsection rows appear only when JS adds them (aboutTelemetry.css gives `.category.selected > .category-subsection { display: block }`), so the handles are `#categories > .category.selected` and `#categories .category-subsection.selected`. The stock row paint comes from `chrome://global/skin/classic/global/in-content/common-shared.css`, whose `#categories > .category`, `:hover`, `:hover:active`, `.category.selected` and `:focus-visible` arms are the very arms the sheet's landing about:networking body already overrides with `!important`. The `.header` strip (aboutTelemetry.css) holds `h1#sectionTitle`, `label#storesLabel`, `select#stores` (hidden until the JS displays a store list) and `input[type="text"]#search` in `div#sectionFilters`; `#search` sits outside `.main-content`, so the landing table-field arm does not reach it. `#ping-picker` is a fixed-position panel `aboutTelemetry.css` paints `--background-color-box` on `--border-color` with `border-radius: 2px` and `box-shadow: 0 1px 3px 0 rgba(0,0,0,.25)`; it is stock white-on-white in the light scheme and our square black outline replaces that shadow. Grep for `telemetry` in `theme/firefox/`, `tests/`, `PLANS.md`, `PLANS-DONE.md`, `BUGS.md` and `BUGS-FIXED.md` returns nothing: neither a landed nor a planned entry covers this page. `tests/test_firefox_content_theme.py::TestFirefoxContentTheme::test_sheet_has_the_downloads_config_preferences_support_and_networking_at_rules` asserts the five-body body set and `stripped.count("@") == 5`, so this plan's sixth body must extend that test; its `test_no_rule_paints_page_chrome` iterates every body's selectors against `FORBIDDEN_PAGE_CHROME = ("body", "h1", "hgroup", "main-content-title")`, which the furniture selectors below avoid, and `test_palette_is_exact` already contains every hex below, so neither needs edits.

**Grounding (platform adaptation, steward clarification 2026-10-25).** No reference screenshot shows Firefox's about:telemetry (the same missing surface the landed about:networking row of `docs/invariants.md` records): the sidebar rows reuse the landed nav-row values — transparent rest, flat `#CCCCFF` black-text hover/active and selected faces, `border-radius: 0` — whose `#CCCCFF` is the pinned `[Colors:Selection]` of `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_selection_background` and whose squareness extends the landed list-row `border-radius: 0`; `#search` reuses the landed line-edit field byte-recipe (`FIELD_RULE` in `tests/test_firefox_content_theme.py`, grounded in `widgets/lineedit.svg` and pinned by `tests/test_desktoptheme_lineedit.py::TestLineEdit` and `TestLineEditReference`); `#stores` reuses the landed pane menulist byte-recipes (`PANE_MENULIST_RULE` and `PANE_MENULIST_HOVER_RULE` in the test module, spelled explicitly so the button recipes cannot silently retarget the pane); `#ping-picker` reuses the sheet's white face and black square outline over the stock rounded ember-cast panel (the Finder's plain white pop-panel shape, no `#CCCCFF` involvement). The `.selected`-class selection and the JS-added subsections are Firefox-required; the rows' stock 42px minimum height and padding, the `:focus-visible` outline and the page's `#sectionTitle` heading, `#storesLabel` label, home-section headings and links (page chrome) stay Firefox's.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userContent.css`, append after the landing about:networking body's closing rule a sixth `@-moz-document` body, in the same illustration-comment-plus-rules shape:

```css
@-moz-document url("about:telemetry") {
  /* The category sidebar rows, the section-filter field and store menu
     and the ping-picker panel take the landed flat nav-row, sunken
     line-edit, raised menulist and white panel paints; the sections'
     data payloads are the recorded natural subjects of a later plan
     (see the header's provenance paragraph). */
  #categories > .category {
    background-color: transparent !important;
    color: #000000 !important;
    border-radius: 0 !important;
  }

  #categories > .category:hover,
  #categories > .category:hover:active {
    background-color: #CCCCFF !important;
    color: #000000 !important;
  }

  #categories > .category.selected,
  #categories > .category.selected:hover,
  #categories > .category.selected:hover:active {
    background-color: #CCCCFF !important;
    color: #000000 !important;
  }

  #categories .category-subsection {
    color: #000000 !important;
  }

  #categories .category-subsection.selected {
    background-color: #CCCCFF !important;
    color: #000000 !important;
  }

  #search {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #000000 !important;
    border-radius: 0 !important;
    box-shadow: inset 1px 1px #999999 !important;
  }

  #stores {
    background-color: #DDDDDD !important;
    color: #000000 !important;
    border: 1px solid #000000 !important;
    border-radius: 0 !important;
    box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA !important;
  }

  #stores:hover {
    background-color: #CCCCFF !important;
    color: #000000 !important;
    box-shadow: none !important;
  }

  #ping-picker {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #000000 !important;
    border-radius: 0 !important;
    box-shadow: none !important;
  }
}
```

Our `!important` arms beat the stock `common-shared.css` declarations and aboutTelemetry.css's panel paint; specificity settles the rest/hover/selected order, with the selected arms the last row rules so a selected row stays `#CCCCFF` under hover and press.

In the same sheet's header comment, append one provenance paragraph after the landing about:networking paragraph: about:telemetry's furniture — the `#categories` sidebar rows, the `.category-subsection` rows, the `#search` field, the `#stores` menu and the `#ping-picker` panel — is painted by a `@-moz-document url("about:telemetry")` body whose rules aboutTelemetry.js outweigh (selection is the `.selected` class, subsections are JS-added), the rows, field, menu and panel reusing the landed about:networking/about:preferences recipes (the `#CCCCFF` selection of `test_selection_background`, the line-edit recipe of `widgets/lineedit.svg` with `TestLineEdit` and `TestLineEditReference`, the pane button/menulist byte-recipes `PANE_MENULIST_RULE` and `PANE_MENULIST_HOVER_RULE`, and the sheet's white face and black square outline for the panel, whose rounded shadowed stock shape is Firefox's own light-scheme paint and no reference screenshot shows this page); the sections' data payloads and the `#sectionTitle` heading and other page chrome stay Firefox's — the payloads being the recorded natural subjects of a later plan.

In `tests/test_firefox_content_theme.py`, extend the module register after the networking rules —

```python
TELEMETRY_ROW = "#categories > .category"
TELEMETRY_ROW_HOVER = (
    "#categories > .category:hover",
    "#categories > .category:hover:active",
)
TELEMETRY_ROW_SELECTED = (
    "#categories > .category.selected",
    "#categories > .category.selected:hover",
    "#categories > .category.selected:hover:active",
)
TELEMETRY_SUBSECTION = "#categories .category-subsection"
TELEMETRY_SUBSECTION_SELECTED = TELEMETRY_SUBSECTION + ".selected"
TELEMETRY_SEARCH = "#search"
TELEMETRY_STORES = "#stores"
TELEMETRY_STORES_HOVER = TELEMETRY_STORES + ":hover"
TELEMETRY_PING_PANEL = "#ping-picker"

TELEMETRY_ROW_RULE = {
    "background-color": "transparent !important",
    "color": f"{BLACK} !important",
    "border-radius": "0 !important",
}
TELEMETRY_ROW_HIGHLIGHT = {
    "background-color": f"{SELECTION} !important",
    "color": f"{BLACK} !important",
}
TELEMETRY_SUBSECTION_RULE = {"color": f"{BLACK} !important"}
TELEMETRY_PING_PANEL_RULE = {
    "background-color": f"{WHITE} !important",
    "color": f"{BLACK} !important",
    "border": f"1px solid {BLACK} !important",
    "border-radius": "0 !important",
    "box-shadow": "none !important",
}

REQUIRED_TELEMETRY_RULES = {
    TELEMETRY_ROW: TELEMETRY_ROW_RULE,
    **{selector: TELEMETRY_ROW_HIGHLIGHT for selector in TELEMETRY_ROW_HOVER},
    **{selector: TELEMETRY_ROW_HIGHLIGHT for selector in TELEMETRY_ROW_SELECTED},
    TELEMETRY_SUBSECTION: TELEMETRY_SUBSECTION_RULE,
    TELEMETRY_SUBSECTION_SELECTED: TELEMETRY_ROW_HIGHLIGHT,
    TELEMETRY_SEARCH: FIELD_RULE,
    TELEMETRY_STORES: PANE_MENULIST_RULE,
    TELEMETRY_STORES_HOVER: PANE_MENULIST_HOVER_RULE,
    TELEMETRY_PING_PANEL: TELEMETRY_PING_PANEL_RULE,
}
```

then in `TestFirefoxContentTheme` rename `test_sheet_has_the_downloads_config_preferences_support_and_networking_at_rules` to `test_sheet_has_the_downloads_config_preferences_support_networking_and_telemetry_at_rules`, extending its expected body set with `"about:telemetry"` and its count assertion to `stripped.count("@") == 6`, and add `class TestFirefoxTelemetryTheme(SheetCase)` with `AT_RULE_URL = "about:telemetry"` holding:

- `test_telemetry_rules_match_the_required_rules` (mirror of the networking register test) — `self.rules[selector] == expected` for every register key.
- `test_parsed_rules_are_exactly_the_telemetry_rules` — `self.selectors` equals the sheet-order tuple `(TELEMETRY_ROW, *TELEMETRY_ROW_HOVER, *TELEMETRY_ROW_SELECTED, TELEMETRY_SUBSECTION, TELEMETRY_SUBSECTION_SELECTED, TELEMETRY_SEARCH, TELEMETRY_STORES, TELEMETRY_STORES_HOVER, TELEMETRY_PING_PANEL)` and `set(self.rules)` equals `set(REQUIRED_TELEMETRY_RULES)`.
- `test_telemetry_rules_scope_to_page_furniture` — with `categories = element("div", "categories")`, a row `element("div", None, classes=("category", "category-no-icon"), parent=categories)` matches `TELEMETRY_ROW` idle and each `TELEMETRY_ROW_HOVER` arm only with `hover=True`, and matches each `TELEMETRY_ROW_SELECTED` arm only when its classes gain `"selected"`; the same selected row's child `element("div", None, classes=("category-subsection",), parent=selected_row)` matches `TELEMETRY_SUBSECTION` idle and `TELEMETRY_SUBSECTION_SELECTED` only when classes gain `"selected"`; a `.category` row under an `element("div", "othersidebar")` parent and a plain `element("span", None, classes=("category",))` match none of the row selectors; `element("input", "search", attrs={"type": "text"}, parent=element("div", "sectionFilters"))` matches `TELEMETRY_SEARCH` while an `element("input")` with another id does not; `element("select", "stores")` and its hover match their arms only.
- `test_telemetry_rules_use_the_pinned_palette` — the body's `set(HEX.findall(body))` is a subset of the allowed set (the landing networking palette test's set, which already holds `#CCCCFF`, `#DDDDDD`, `#AAAAAA`, `#999999`, `#FFFFFF` and `#000000`); if that test's allowed set lives in `TestFirefoxSupportTheme` or a shared helper, extend the helper rather than duplicating the set.
- `test_header_names_telemetry_provenance` — `assert_header_names` with a token tuple naming `"about:telemetry"`, `"aboutTelemetry.js"`, `".category.selected"`, `"common-shared.css"`, `"#search"`, `"#stores"`, `"#ping-picker"` and `"a later plan"`.

In `docs/invariants.md`, in the `## firefox` table: rename the landing generic row's test-column entry `test_sheet_has_the_downloads_config_preferences_support_and_networking_at_rules` to the new name, and append one row (the table's current last row before the trailing validation notes) with the guarantee in one sentence — both the about:telemetry sidebar rows (selected by the `.selected` class from `aboutTelemetry.js`), the JS-added subsection rows, the `#search` filter field, the `#stores` store menu and the `#ping-picker` panel take the landed nav-row, line-edit, menulist and white-panel paints with square corners while the sections' data payloads and page chrome stay Firefox's — with the test column naming `tests/test_firefox_content_theme.py::TestFirefoxTelemetryTheme`, `...::TestFirefoxContentTheme::test_palette_is_exact` and `...::test_no_rule_paints_page_chrome`, and the provenance-exception cell naming the missing reference surface (no reference screenshot shows Firefox's about:telemetry), the reused byte-recipes and their pinned tests (as the grounding paragraph names them), the probe where those facts come from and the rule that declaration checks establish no rendered pixel. Trim no landed row. No edit to `tests/support/invariants.py` is expected — its register parses `docs/invariants.md` and resolves test references against `tests/test_firefox_content_theme.py`, which the new row and the renamed reference satisfy through the module's existing registration of that module; run `tests/test_invariants.py` (part of the check) to confirm.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userContent.css`, `tests/test_firefox_content_theme.py`, `docs/invariants.md`.

## Done
