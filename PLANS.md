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


### Firefox Platinum preferences search field: paint about:preferences' search box as the Platinum line edit through the `moz-input-search` tokens (planned 2026-10-27 by the plan role; independent of the waiting analog-clock plan — the two touch disjoint files (`theme/firefox/org.macos8.desktop/chrome/userContent.css` and its suite versus `theme/desktoptheme/org.macos8.desktop/widgets/clock.svg` and its suites), so either order merges; it is part 4 of the about:preferences series, whose parts 1 (category navigation rows), 2 (sidebar separators) and 3 (page background and heading bands) landed 2026-10-27 — the panes' remaining controls (the group cards, push buttons and checkboxes) stay Firefox's for later parts)

**Goal.** The landed parts left every control inside `#mainPrefPane` Firefox's, and the panes' most visible one is the search field: `preferences.xhtml` builds it as `html:moz-input-search#searchInput` (in the installed Firefox ESR 153.5.1, `chrome/browser/content/browser/preferences/preferences.xhtml` line ~237), a shadow-DOM custom element whose inner `#input` is styled by `chrome/toolkit/content/global/elements/moz-input-text.css` exclusively through tokens — `border: var(--input-text-border)`, `border-radius: var(--input-text-border-radius)`, `background-color: var(--input-text-background-color)`, `color: var(--input-text-color)` — with the magnifier icon filled by `var(--icon-color)` through `-moz-context-properties` and no `::part()` exposed. Its token defaults come from `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` (read 2026-10-27): a 1px rounded grey border (`--input-text-border: var(--border-width) solid var(--input-text-border-color)`, `--input-text-border-radius: var(--border-radius-medium)`), a box face and grey `--icon-color`, so the field reads as a rounded Adwaita pill on the white page part 3 painted. Paint it as the Platinum line edit — white face, 1px black square border, black text, black icon — by overriding the tokens on the host element, the exact route part 1's headless run of 2026-10-27 verified (outer-sheet custom properties override the shadow `:host`/inherited defaults). No reference screenshot shows Firefox's about:preferences; the field adapts this theme's `widgets/lineedit.svg` recipe — a platform colour adaptation. One deliberate limitation: the line edit's sunken bevel (`inset 1px 1px #999999`, the sheet's `FIELD_RULE`) cannot be delivered here, because `moz-input-text.css` reads no shadow token — the field ships as the outline, face, text and icon only, and the sheet's provenance records that as this theme's own choice. Geometry (`min-height`, padding), the disabled state and any focus indicator stay Firefox's.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userContent.css`, inside the existing `@-moz-document url("about:preferences")` block, immediately after the `.subcategory` rule, add one rule:

    moz-input-search#searchInput {
      --input-text-border: 1px solid #000000 !important;
      --input-text-border-radius: 0 !important;
      --input-text-background-color: #FFFFFF !important;
      --input-text-color: #000000 !important;
      --icon-color: #000000 !important;
    }

Overriding the composed `--input-text-border` (not just `--input-text-border-color`) pins width, style and colour in one declaration instead of leaving the width tied to `--border-width`; the rule touches only custom properties on the light-DOM host, so the shadow `#input` keeps its single box (no double border from host background/border paint) and the search icon's fill turns black while its own `--input-background-icon` image stays. Extend the leading comment's about:preferences paragraph to name the field, the three files above (read 2026-10-27), the five overridden tokens, the token route reusing part 1's headless verification, the absent shadow token as the reason there is no sunken bevel, the missing reference surface, and that only `#FFFFFF` and `#000000` are used (`tests/test_firefox_content_theme.py::TestFirefoxContentTheme::test_palette_is_exact` already pins the sheet's exact set — it must not gain a new literal).

In `tests/test_firefox_content_theme.py`: rename the module constant `REQUIRED_PREFERENCES_NAV_RULES` to `REQUIRED_PREFERENCES_RULES` and add the `SEARCH = "moz-input-search#searchInput"` entry with the exact declarations above, so `TestFirefoxPreferencesNavTheme::test_required_rules` and `test_parsed_rules_are_exactly_the_nav_rules` keep holding for the now six-rule `about:preferences` body; keep `TestFirefoxPreferencesNavTheme::test_host_rule_sets_only_custom_properties` and `test_nav_rule_sets_only_custom_properties` scoped to their own two selectors (the search rule's property names must not be forced through the `--page-nav-` check). Add `TestFirefoxPreferencesSearchTheme(SheetCase)` with `AT_RULE_URL = "about:preferences"` holding: `test_search_field_rule_sets_only_custom_properties` — every property of the `SEARCH` rule starts `--input-text-` or equals `--icon-color`, and every value ends `!important`; `test_search_field_is_the_line_edit` — the rule equals the pinned dict above (border `1px solid #000000 !important`, radius `0 !important`, background `#FFFFFF !important`, text `#000000 !important`, icon `#000000 !important`) and the rule's values contain no hex beyond `WHITE` and `BLACK`; `test_search_field_selector_avoids_page_chrome` — the selector avoids every `FORBIDDEN_PAGE_CHROME` token and names the element and the id (`moz-input-search#searchInput`) so it cannot leak to other pages' `moz-input-search` hosts; and `test_header_names_search_provenance` — the header names `moz-input-search#searchInput`, `moz-input-text.css`, `tokens-shared.css`, `--icon-color`, the no-`::part()` route, the absent sunken bevel, `preferences.xhtml`, `2026-10-27` and `platform colour adaptation 2026-10-27` (pattern: `TestFirefoxPreferencesNavTheme::test_header_names_preferences_provenance`).

In `docs/invariants.md`, append a row to the `## firefox` table: the about:preferences search field (`moz-input-search#searchInput`) is a white face with a square 1px black outline, black text and a black magnifier icon, delivered through the five `--input-text-*`/`--icon-color` tokens on the host element, with the sunken bevel, geometry, disabled and focus states Firefox's. Test column: `tests/test_firefox_content_theme.py::TestFirefoxPreferencesSearchTheme` (all four tests) plus `TestFirefoxContentTheme::test_palette_is_exact`. Provenance: no reference screenshot shows the page; the token names and defaults are read 2026-10-27 from `moz-input-text.css` and `tokens-shared.css`; the token route reuses part 1's headless verification of the sheet's reach; the missing sunken bevel follows from the shadow stylesheet reading no shadow token (this theme's own choice); declaration checks do not establish rendered pixels. `tests/support/invariants.py` stays green.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userContent.css`, `tests/test_firefox_content_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The `about:preferences` block gains exactly one rule, `moz-input-search#searchInput`, setting exactly the five pinned custom properties with `!important`; no other rule, selector or colour changes anywhere in the sheet, and the sheet's palette stays exactly the pinned set (`#FFFFFF`/`#000000` were already members).
- `TestFirefoxPreferencesSearchTheme`'s four tests pass; `TestFirefoxPreferencesNavTheme`'s exact-set, custom-property and provenance tests pass against the renamed `REQUIRED_PREFERENCES_RULES`; `TestFirefoxContentTheme` stays green over the unchanged downloads and config bodies.
- `docs/invariants.md`'s new `## firefox` row cites the new test class and records the provenance exception and the bevel limitation; `tests/support/invariants.py` stays green.
- `make check` passes.

## Done
