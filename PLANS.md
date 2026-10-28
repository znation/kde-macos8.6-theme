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

### Firefox Platinum content: paint about:networking's category sidebar rows, the DNS-lookup host field and the autorefresh checkbox as the landed nav-row, line-edit and check-box recipes (planned 2026-10-27 by the plan role; extends the landed about:networking plan in PLANS-DONE.md, whose header paragraph records these three surfaces as "the natural subjects of a later plan"; independent of the queued GTK path-bar plan — it touches only the Firefox sheet and its tests)

**Goal.** The landed about:networking plan painted the page's ten `.main-content` tables and four buttons and recorded that `#categories` (its eight `.category` rows), the DNS-lookup tool's `#host` text field and the autorefresh `#autorefcheck` checkbox stay Firefox's, naming them "the natural subjects of a later plan; this is decided here so no design question is left open". This is that later plan: the same `@-moz-document url("about:networking")` body gains four more rule groups — the sidebar rows as the landed about:preferences nav-row paint (flat transparent rest, flat `#CCCCFF` black-text hover/active and selected faces, square corners), `#host` as the landed Platinum line edit, and `#autorefcheck` as the landed preferences check box face with the shipped check-mark data URI — reusing only values the sheet and tests already pin, so no new constant and no new hex beyond the landed `#888888` checkbox-bevel arm is introduced, and no landed rule text changes.

**Verified facts (checked 2026-10-27, installed Firefox ESR 153.5.1).** `chrome/toolkit/content/global/aboutNetworking.html` is the light-DOM page at about:networking (the landed paragraph's established `attachShadow` count 0): `div#categories` holds eight `div.category.category-no-icon` children each wrapping `span.category-name`, the first carrying `selected="true"`; `aboutNetworking.js` (line ~358–360 of that file) flips the selection only through the `selected` attribute — `current_button.removeAttribute("selected"); button.setAttribute("selected", "true")` — never a class, so the row handle is `#categories > .category[selected]`. The stock row paint comes from `chrome/toolkit/skin/classic/global/in-content/common-shared.css`: `#categories > .category` is a button-like row (`border: var(--button-border)`, `border-radius: var(--border-radius-small)`, `transition: background-color 150ms`), `:hover` and `:hover:active` paint `--button-background-color-hover`/`-active` faces with hover accent colours, and `#categories > .category[selected], #categories > .category.selected` recolour the text to `--color-accent-primary` while `[selected]:not(:hover)` clears the background — a keyboard `:focus-visible` outline stays stock. `#dnslookuptool` holds `input[type="text"]#host` between its label and `#dnsLookupButton` (already painted), and `#refreshDiv` holds `input#autorefcheck[type="checkbox"]` with its l10n `span` beside it; `common-shared.css`'s `html|input:where([type="checkbox"], [type="radio"])` block sizes both native inputs `height/width: var(--checkbox-size)`, so the box keeps that stock size under `appearance: none` and no metric is added. The landed sheet body the plan extends is the file's last `@-moz-document url("about:networking")` block; `tests/test_firefox_content_theme.py` presses it through `SheetCase` (`self.rules`, `self.selectors`, `self.bodies`), the module register `REQUIRED_NETWORKING_RULES`/`NETWORKING_SELECTORS`, and `FORBIDDEN_PAGE_CHROME = ("body", "h1", "hgroup", "main-content-title")`. `tests/support/selector_matching.py`'s matcher (docstring, `matches`) supports tag/id/class/attribute selectors and `:hover` only — no `:checked` — so the `:checked` and `:hover:active` arms stay pinned by selector text and the exact-register test exactly as the landed `:nth-child(2n)` zebra arm already is.

**Grounding (platform adaptation, steward clarification 2026-10-25).** No reference screenshot shows Firefox's about:networking (established by the landed paragraph) — these rules sample no reference pixel: the sidebar rows reuse the landed about:preferences nav-row values (transparent rest, flat `#CCCCFF` hover/active/selected, black text, radius 0) whose `#CCCCFF` is the pinned `[Colors:Selection]` of `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_selection_background` and whose squareness extends the landed list-row `border-radius: 0` of the sheet's own downloads/list recipes; `#host` reuses the landed line-edit field byte-recipe (`#FFFFFF` face, black text, square `1px solid #000000`, `inset 1px 1px #999999` — `FIELD_RULE` in the test register, grounded in `widgets/lineedit.svg` and pinned by `tests/test_desktoptheme_lineedit.py::TestLineEdit` and `TestLineEditReference`); `#autorefcheck` reuses the landed about:preferences check-box face (`#DDDDDD` face, square `1px solid #000000`, `inset 1px 1px #FFFFFF, inset -1px -1px #888888`, whose raised bevel owns the Kvantum check-box provenance) and its checked arm's shipped check-mark data URI, pinned by `tests/test_firefox_content_theme.py`'s `CHECKBOX_FACE_RULE`/`CHECKBOX_GLYPH_RULE`. The `#categories`, `.category`, `[selected]`, `input#autorefcheck`, `input[type="text"]#host`, `:hover`/`:hover:active`/`:checked` arms and the stock `--checkbox-size` sizing are Firefox-required; the sidebar keeps Firefox's non-selected-row stock hover cleared only where our paint lands, and the `:focus-visible` outline stays Firefox's.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userContent.css`, inside the landed `@-moz-document url("about:networking")` body, after the `#dnsLookupButton:hover:not(:disabled)` rule (the body's last), append a comment naming the three reused recipes and the recorded later-plan decision, then exactly the rule blocks shown — the sidebar's rest, hover and selected rules, the `#host` rule and the `#autorefcheck` face and `:checked` rules — and nothing else:

```css
  /* The sidebar rows, the DNS-lookup field and the autorefresh checkbox
     are the recorded natural subjects of a later plan: the rows take the
     landed about:preferences nav-row paint, the field the landed line
     edit and the checkbox the landed preferences check box face with its
     shipped check-mark glyph. */
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

  #categories > .category[selected],
  #categories > .category[selected]:hover,
  #categories > .category[selected]:hover:active {
    background-color: #CCCCFF !important;
    color: #000000 !important;
  }

  /* The DNS-lookup field: the Platinum line edit (see the header's
     provenance paragraph). */
  #host {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #000000 !important;
    border-radius: 0 !important;
    box-shadow: inset 1px 1px #999999 !important;
  }

  /* The autorefresh checkbox: the landed preferences check box face and
     its shipped check-mark glyph (see the header's provenance
     paragraph). */
  #autorefcheck {
    appearance: none !important;
    background-color: #DDDDDD !important;
    border: 1px solid #000000 !important;
    border-radius: 0 !important;
    box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #888888 !important;
  }

  #autorefcheck:checked {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 16 16'%3E%3Cpath d='M 3.5 8.5 L 6.5 11.5 L 12.5 5.5' fill='none' stroke='rgb(0, 0, 0)' stroke-width='2' stroke-linecap='square' stroke-linejoin='miter'/%3E%3C/svg%3E") !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
  }
```

The data URI's text is byte-for-byte the landed about:preferences checked-arm's `background-image` value (verified against the sheet's `#mainPrefPane checkbox:not([disabled])[checked] .checkbox-check` rule). Our `!important` arms beat the stock `common-shared.css` declarations, and within our arms specificity settles it: the `[selected]` and `:hover`/`:hover:active` pseudo-classes outrank the plain rest arm, so a selected row stays `#CCCCFF` under hover and press and the stock hover face never shows through.

In the same sheet's header comment, rewrite the landed about:networking section's "stay Firefox's" sentence — replacing `The #categories sidebar of .category divs, the #host field, the #autorefcheck checkbox, the #sectionTitle heading, the four hrs and the about-logging link paragraph stay Firefox's (the sidebar, field and checkbox are the natural subjects of a later plan; this is decided here so no design question is left open).` — with one paragraph naming: the sidebar rows, the `#host` field and the `#autorefcheck` checkbox are the recorded natural subjects of a later plan and are painted by the appended rules — the rows reuse the landed about:preferences nav-row values (the pinned `#CCCCFF` selection of `test_selection_background` and the list-row `border-radius: 0`, selected-by-attribute only in `aboutNetworking.js`), the field reuses the landed line-edit recipe (`widgets/lineedit.svg`, `tests/test_desktoptheme_lineedit.py::TestLineEdit` and `TestLineEditReference`), and the checkbox reuses the landed about:preferences check-box face and its shipped check-mark data URI (`#DDDDDD` face with the `inset 1px 1px #FFFFFF, inset -1px -1px #888888` bevel, whose provenance the landing checkbox paragraph records; `#autorefcheck`'s stock `--checkbox-size` sizing stays Firefox's); keep the phrases `#categories`, `#host`, `#autorefcheck`, `in-content/common-shared.css` and the `[selected]`-attribute statement, keep the closing note that `#sectionTitle`, the four hrs and the about-logging link paragraph stay Firefox's, and leave the landed headless sentence (`"headless"`, `"URL match"`) untouched.

In `tests/test_firefox_content_theme.py`, extend the networking register after `NETWORKING_BUTTONS_HOVER` —

```python
NETWORKING_CATEGORY = "#categories > .category"
NETWORKING_CATEGORY_HOVER = (
    "#categories > .category:hover",
    "#categories > .category:hover:active",
)
NETWORKING_CATEGORY_SELECTED = (
    "#categories > .category[selected]",
    "#categories > .category[selected]:hover",
    "#categories > .category[selected]:hover:active",
)
NETWORKING_HOST = "#host"
NETWORKING_CHECK = "#autorefcheck"
NETWORKING_CHECK_CHECKED = NETWORKING_CHECK + ":checked"

NETWORKING_CATEGORY_RULE = {
    "background-color": "transparent !important",
    "color": f"{BLACK} !important",
    "border-radius": "0 !important",
}
NETWORKING_ROW_HIGHLIGHT = {
    "background-color": f"{SELECTION} !important",
    "color": f"{BLACK} !important",
}
NETWORKING_CHECK_RULE = {
    "appearance": "none !important",
    "background-color": f"{FACE} !important",
    "border": f"1px solid {BLACK} !important",
    "border-radius": "0 !important",
    "box-shadow": f"inset 1px 1px {WHITE}, inset -1px -1px {ETCH_DARK} !important",
}
NETWORKING_CHECK_CHECKED_RULE = {
    "background-image": "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 16 16'%3E%3Cpath d='M 3.5 8.5 L 6.5 11.5 L 12.5 5.5' fill='none' stroke='rgb(0, 0, 0)' stroke-width='2' stroke-linecap='square' stroke-linejoin='miter'/%3E%3C/svg%3E\") !important",
    "background-repeat": "no-repeat !important",
    "background-position": "center !important",
}
```

then extend `REQUIRED_NETWORKING_RULES` with `NETWORKING_CATEGORY: NETWORKING_CATEGORY_RULE`, each `NETWORKING_CATEGORY_HOVER` and `NETWORKING_CATEGORY_SELECTED` arm mapped to `NETWORKING_ROW_HIGHLIGHT`, `NETWORKING_HOST: FIELD_RULE`, `NETWORKING_CHECK: NETWORKING_CHECK_RULE` and `NETWORKING_CHECK_CHECKED: NETWORKING_CHECK_CHECKED_RULE`, and extend `NETWORKING_SELECTORS` in sheet order after `*NETWORKING_BUTTONS_HOVER` with `(NETWORKING_CATEGORY, *NETWORKING_CATEGORY_HOVER, *NETWORKING_CATEGORY_SELECTED, NETWORKING_HOST, NETWORKING_CHECK, NETWORKING_CHECK_CHECKED)` so `test_parsed_rules_are_exactly_the_networking_rules` keeps passing against the appended rules; make sure `required` mapping registration ordering matches `NETWORKING_SELECTORS` so there is one expectation per parsed selector.

In `tests/test_firefox_content_theme.py::TestFirefoxNetworkingTheme`:

- extend `test_networking_rules_scope_to_the_main_content_div`'s docstring pinning note (`:nth-child(2n)`, the comma-list arms and now the `:checked` and `:hover:active` arms are outside the matcher's subset and pinned by their selector text and the exact-register test) and add: with `categories = element("div", "categories")`, `element("div", None, classes=("category", "category-no-icon"), parent=categories)` matches `NETWORKING_CATEGORY` idle, `NETWORKING_CATEGORY_HOVER[0]` only with `hover=True` (never idle), and `NETWORKING_CATEGORY_SELECTED[0]` only with `attrs={"selected": "true"}`; the same `.category` row under `element("div", "othersidebar")` matches none of the three selectors, and a plain `element("button", "category-http")` with no `#categories` parent matches none either; `element("input", "host", attrs={"type": "text"}, parent=element("div", "dnslookuptool", parent=main_content))` matches `NETWORKING_HOST` while an `element("input")` without that id under `.main-content` does not; the existing `FORBIDDEN_PAGE_CHROME` loop over `self.selectors` needs no change.
- extend `test_networking_rules_use_the_pinned_palette`: the allowed set and the body-wide `set(HEX.findall(body))` assertion both gain `ETCH_DARK` (the checkbox bevel's dark arm, byte-equal to the landed preferences `.checkbox-check` declarations), keeping the rest of the assertion untouched.
- add `test_checked_glyph_uri_pins_the_checkmarks_glyph` for the `#autorefcheck:checked` arm — move the landed `TestFirefoxPreferencesCheckboxTheme` decode body (data-URI prefix strip, `unquote`, `xml.etree.ElementTree.fromstring`, the width/height/`d`/fill/stroke/width/linecap/linejoin assertions and the `#`-absence check) into a module-level helper `decodes_to_the_shipped_checkmark(value)` placed beside `at_rule_bodies`, call it from the new networking test against `self.rules[NETWORKING_CHECK_CHECKED]["background-image"]`, and refactor `TestFirefoxPreferencesCheckboxTheme::test_checked_glyph_uri_pins_the_checkmarks_glyph` to call the same helper — so the landed preferences test changes no assertions and both pages pin the same glyph through one function.
- extend `test_header_names_networking_provenance`'s token tuple: it keeps every landed token (including `"a later plan"`, still satisfied by the rewritten sentence) and gains `"in-content/common-shared.css"`, `"#autorefcheck:checked"`... (match the actual rule text chosen), `"about:preferences"` (the nav-row and check-box recipe source) and `"aboutNetworking.js"` (already present) — name the exact added tokens in the implementation so `assert_header_names` stays honest.

No other test asserts the sheet body rule count per at-rule: `TestFirefoxContentTheme::test_sheet_has_the_downloads_config_preferences_support_and_networking_at_rules` asserts only the five-body set and `stripped.count("@") == 5`, unchanged because this plan appends inside an existing body; `test_networking_rules_match_the_required_rules` and `test_parsed_rules_are_exactly_the_networking_rules` need no source edits (they iterate the register).

In `docs/invariants.md`, in the `## firefox` table's about:networking row (the row whose guarantee names the ten tables and four buttons): extend the guarantee sentence to add that the page's `#categories` sidebar rows (selected by attribute) take the landed nav-row paint — transparent rest, flat `#CCCCFF` black-text hover/active and selected, square corners — the DNS-lookup `#host` field the landed line-edit paint and the `#autorefcheck` checkbox the landed preferences check-box face with its shipped check-mark glyph, and trim the stay-Firefox list to `#sectionTitle`, the four hrs, the about-logging link paragraph and page chrome; extend the row's provenance exception with one sentence naming the reused recipes and their pinned tests (`TestReferenceAnchors.test_selection_background`, `TestLineEdit`/`TestLineEditReference`, the checkboxes' `CHECKBOX_FACE_RULE`/`CHECKBOX_GLYPH_RULE`) and the Firefox-required `[selected]`-attribute selection from `aboutNetworking.js` and the stock `--checkbox-size` sizing; keep the landed headless sentence, and trim no landed row. `tests/support/invariants.py`'s register stays in step with the row's test column (the networking class is already registered).

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userContent.css`, `tests/test_firefox_content_theme.py`, `docs/invariants.md`.

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
