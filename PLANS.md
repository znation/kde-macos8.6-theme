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

### Firefox Platinum chrome, part 2 of a Library window series: paint the Library toolbar's search box `moz-input-search#searchFilter` as the Platinum line edit through the `moz-input-search` tokens (planned 2026-10-27 by the plan role; independent of every other entry — it builds on the landed part 1 of the Library series, the two places trees as the Platinum sunken list field (2026-10-27), reusing the same files and base recipe without touching its rules; the toolbar's chrome buttons and the three Organize/View/Maintenance menus, the content tree's column headers, the `richlistbox#downloadsListBox` downloads view and the `#detailsPane` bookmark-details fields are later parts that wait behind this one)

**Goal.** The landed part 1 left the Library toolbar Firefox's, and its most visible control is the search box. `chrome/browser/content/browser/places/places.xhtml` (read 2026-10-27 from the installed Firefox ESR 153.5.1's `browser/omni.ja`, ~line 553) builds it as `html:moz-input-search id="searchFilter"` inside the window's toolbox `toolbar` (after `#libraryToolbarSpacer`, `aria-controls="placeContent"`), a shadow-DOM custom element whose inner `#input` is styled by `chrome/toolkit/content/global/elements/moz-input-text.css` exclusively through tokens — `border: var(--input-text-border)`, `border-radius: var(--input-text-border-radius)`, `background-color: var(--input-text-background-color)`, `color: var(--input-text-color)` — with the magnifier icon `&[type="search"]`'s `url(chrome://global/skin/icons/search-textbox.svg)` filled by `var(--icon-color)` through `-moz-context-properties`, and no `::part()` exposed. Token defaults come from `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css`: a 1px rounded grey border, a white box face, a grey icon — on the Library's white window face (part 1's `organizer.css` `#placesView` reading) the box reads as a rounded Adwaita pill. Paint it as the Platinum line edit — white face, square 1px black outline, black text, black magnifier — by overriding the five tokens on the host element, the byte-recipe the landed about:preferences part 4 shipped for `moz-input-search#searchInput` in `theme/firefox/org.macos8.desktop/chrome/userContent.css` (custom properties inherit into the shadow tree from the host; that part's headless run verified the sheet's reach). No reference screenshot shows the Firefox Library window; the field adapts this theme's `widgets/lineedit.svg` — a platform colour adaptation. One deliberate limitation, the same one part 4 records: the line edit's sunken bevel (`inset 1px 1px #999999`) cannot be delivered, because `moz-input-text.css` reads no shadow token — the provenance records that as this theme's own choice. Geometry (`min-height`, `padding-inline`, `--input-text-icon-size`), the placeholder ellipsis, the disabled state and any focus indicator stay Firefox's.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, after the landed Library places-trees block (the `tree#placeContent treechildren::-moz-tree-row(multicol, odd)` rule, currently the sheet's last rule), append one rule and nothing else:

```css
/* Library window search box: the Platinum line edit through the
   moz-input-search tokens (see the header's provenance paragraph). */
moz-input-search#searchFilter {
  --input-text-border: 1px solid #000000 !important;
  --input-text-border-radius: 0 !important;
  --input-text-background-color: #FFFFFF !important;
  --input-text-color: #000000 !important;
  --icon-color: #000000 !important;
}
```

the byte-twin of the landed `moz-input-search#searchInput` rule in userContent.css with the Library host's id. Naming element and id keeps the rule from leaking to other chrome `moz-input-search` hosts; `#searchFilter` is an id the Library window alone carries in chrome. The rule introduces no hex literal outside the already-pinned `{WHITE, BLACK}`, so `TestFirefoxChromeShell::test_palette_is_exact` passes untouched.

Extend the header comment's provenance block with a Library-search paragraph immediately after the Library-trees paragraph and before the header's closing `*/`: no reference screenshot shows the Firefox Library window; the field adapts `widgets/lineedit.svg`, grounded in `macos8.6-screenshots/firstboot_betawiki.png` and pinned by `tests/test_desktoptheme_lineedit.py::TestLineEdit` and `TestLineEditReference`, reusing the landed `moz-input-search#searchInput` token route; the token names and defaults are read 2026-10-27 from `moz-input-text.css` and `tokens-shared.css` in the installed Firefox ESR 153.5.1, `chrome/browser/content/browser/places/places.xhtml` defines `html:moz-input-search#searchFilter` in the window's toolbox toolbar with `aria-controls="placeContent"`, the shadow `#input` paints only through the `--input-text-*`/`--icon-color` tokens with no `::part()`, the magnifier is `search-textbox.svg` filled by `--icon-color`, the sunken bevel is absent because the shadow stylesheet reads no shadow token (this theme's own choice), and the toolbar buttons and Organize/View/Maintenance menus, column headers, downloads rich list and details pane stay Firefox's for the later parts; declaration checks do not establish rendered pixels (platform colour adaptation 2026-10-27).

In `tests/support/firefox_chrome_cases.py`, after the Library-trees block (after the `tree#placeContent treechildren::-moz-tree-row(multicol, odd)` entry), append:

```python
# The Library window's search box: the Platinum line edit through the
# moz-input-search tokens, the byte-twin of the landed
# moz-input-search#searchInput recipe (see the header's provenance
# paragraph).
REQUIRED_RULES["moz-input-search#searchFilter"] = {
    "--input-text-border": f"1px solid {BLACK} !important",
    "--input-text-border-radius": "0 !important",
    "--input-text-background-color": f"{WHITE} !important",
    "--input-text-color": f"{BLACK} !important",
    "--icon-color": f"{BLACK} !important",
}
```

In `tests/test_firefox_theme_library.py`, add `SEARCH_RULE = ("moz-input-search#searchFilter",)` beside `TREE_RULES` and a new `class TestFirefoxLibrarySearchChrome(FirefoxChromeTestCase)` holding: `test_search_field_rule_sets_only_custom_properties` — the rule's every property starts `--input-text-` or equals `--icon-color`, and every value ends `!important`; `test_search_field_is_the_line_edit` — `self.rules["moz-input-search#searchFilter"]` equals the pinned dict above byte-for-byte; `test_search_field_selector_scopes_to_the_library_box` — `support.selector_matching.matches` matches an element named `moz-input-search` with id `searchFilter` and never matches one without that id (pattern: `test_library_tree_paint_is_scoped_to_the_places_trees`); and `test_header_names_search_provenance` — the header names `moz-input-search#searchFilter`, `places.xhtml`, `moz-input-text.css`, `tokens-shared.css`, `--icon-color`, `search-textbox.svg`, the no-`::part()` route, the absent sunken bevel, `2026-10-27` and `platform colour adaptation 2026-10-27` (pattern: `test_library_tree_provenance`).

In `docs/invariants.md`, append a row at the end of the `## firefox` table (after the Library places-trees row, before `## gtk`): the Library window's search box (`moz-input-search#searchFilter`) is a white face with a square 1px black outline, black text and a black magnifier icon, delivered through the five `--input-text-*`/`--icon-color` tokens on the host element, with the sunken bevel, geometry, placeholder, disabled and focus states Firefox's. Test column: `tests/test_firefox_theme_library.py::TestFirefoxLibrarySearchChrome` plus `tests/test_firefox_theme_shell.py::TestFirefoxChromeShell::test_palette_is_exact`. Provenance: no reference screenshot shows the window; the field adapts `widgets/lineedit.svg` (a platform colour adaptation), pinned by `tests/test_desktoptheme_lineedit.py::TestLineEdit`; the token names and defaults are read 2026-10-27 from `moz-input-text.css` and `tokens-shared.css` in the installed Firefox ESR 153.5.1, and declaration checks do not establish rendered pixels. `tests/invariants.py` stays green.

**Acceptance criteria.**
- The rules body gains exactly the one rule above, appended after the Library-trees block; the header gains exactly one paragraph and still closes with `*/`; nothing already in the sheet changes.
- `TestFirefoxLibrarySearchChrome`'s four tests pass; `TestFirefoxLibraryChrome`'s tests and `TestFirefoxChromeShell::test_required_rules` keep green against the extended `REQUIRED_RULES`; `test_palette_is_exact` keeps green (no hex outside `{#FFFFFF, #000000}` in the new rule).
- `docs/invariants.md` gains one row and `tests/invariants.py` stays green.
- `make check` passes.

## Done
