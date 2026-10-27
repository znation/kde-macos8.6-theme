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


### Firefox Platinum chrome, part 3 of a Library window series: paint the content tree's column headers as the Platinum raised header buttons (planned 2026-10-27 by the plan role; independent of the waiting about:preferences radios plan — the two touch disjoint sheet and test files (`theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme_library.py` and `tests/support/firefox_chrome_cases.py` versus `theme/firefox/org.macos8.desktop/chrome/userContent.css` and `tests/test_firefox_content_theme.py`), and their `docs/invariants.md` edits touch different rows (the radios plan only appends its own new row; this plan trims the landed places-trees row's stay-Firefox list and appends its own new row), so either order merges; it is part 3 of the Firefox Library window series, whose parts 1 (the two places trees as the Platinum sunken list field) and 2 (the toolbar search box as the Platinum line edit) landed 2026-10-27 and whose base recipes this part reuses without touching their rules — the toolbar's chrome buttons and the three Organize/View/Maintenance menus, the `richlistbox#downloadsListBox` downloads view and the `#detailsPane` bookmark-details fields are later parts that wait behind this one)

**Goal.** The landed parts 1 and 2 left the content tree's column headers Firefox's. `chrome/browser/content/browser/places/places.xhtml` (read 2026-10-27 from the installed Firefox ESR 153.5.1's `browser/omni.ja`, `treecols id="placeContentColumns"`, ~line 584) authors the header row as seven sortable `treecol` columns (`placesContentTitle`, `placesContentTags`, `placesContentUrl`, `placesContentDate`, `placesContentVisitCount`, `placesContentDateAdded` and the primary title column) separated by `.tree-splitter` grippies — three of them start `hidden="true"` and paint nothing until shown — and the `treecolpicker` the toolkit appends when it is missing. `chrome/toolkit/content/global/elements/tree.js` (read 2026-10-27 from the installed `omni.ja`) defines `customElements.define("treecols", MozTreecols)` whose markup appends `<treecolpicker fixed="true">` as the `treecols`' last child when absent, and `MozTreecolPicker`'s light-DOM fragment `<button class="tree-columnpicker-button"/>`; `MozTreecol`'s light-DOM fragment appends `label.treecol-text` and `image.treecol-sortdirection` inside each `treecol`, so an author sheet matches the `treecol` hosts directly. `chrome/toolkit/skin/classic/global/tree/tree.css` paints every header stock: `treecol, .tree-columnpicker-button { background-color: -moz-ColHeader; color: -moz-ColHeaderText; … border-inline-start: 1px solid ThreeDLightShadow; box-shadow: inset 0 -1px ThreeDLightShadow; }` with `:hover`/`:hover:active` washing `-moz-ColHeaderHover`/`-moz-ColHeaderActive` — Adwaita-flavoured system-colour greys on the Library's white face that read as nothing Platinum. On parts 1's white `#placeContent` field the header row is the one chrome band over the list that this theme does not own. Paint the header row as the theme's raised Platinum buttons — the byte-recipe the landed `#editBookmarkPanelDoneButton`/`#editBookmarkPanelRemoveButton` and permission-popup remove-button rules carry (`#DDDDDD` face, black text, square corners, `inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA` raised bevel) — with the theme's flat `#CCCCFF` hover/pressed fill and no bevel (the landed `#mainPrefPane button:hover` recipe), keeping Firefox's stock `border-inline-start` `ThreeDLightShadow` column divider and its `treecol:where([ordinal="1"])` divider omission, so the header row reads as a run of Platinum buttons separated by thin columns. No reference screenshot shows the Firefox Library window; the header face adapts the reference-grounded `widgets/button.svg` and the hover/pressed fill `widgets/viewitem.svg` (a platform colour adaptation). Firefox's `min-height: max(24px, 1.3em)`, `padding: 0 4px`, `.treecol-text` margins, `sort-asc.svg`/`sort-dsc.svg` sort-direction arrows (they draw `currentColor`, so they follow the header's black text through `fill: currentColor` with `-moz-context-properties`), the picker button's `columnpicker.svg` icon (also `currentColor`), the `treecol[dragging="true"]` `Graytext` drag colour and the `treecol[hideheader="true"]` hide (the `placesList` sidebar's one column, inside the unnamed `treecols`; its ancestor scoping already excludes it) stay Firefox's.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, after the landed `moz-input-search#searchFilter` rule (currently the sheet's last rule), append two rules and nothing else — the block-end append point keeps the part independently mergeable with the radios plan and with this series' later parts:

    /* Library content-tree column headers: the Platinum raised
       header buttons (see the header's provenance paragraph). */
    treecols#placeContentColumns > treecol,
    treecols#placeContentColumns .tree-columnpicker-button {
      background-color: #DDDDDD !important;
      color: #000000 !important;
      border-radius: 0 !important;
      box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA !important;
    }

    treecols#placeContentColumns > treecol:hover,
    treecols#placeContentColumns > treecol:hover:active,
    treecols#placeContentColumns .tree-columnpicker-button:hover,
    treecols#placeContentColumns .tree-columnpicker-button:hover:active {
      background-color: #CCCCFF !important;
      color: #000000 !important;
      box-shadow: none !important;
    }

The `treecols#placeContentColumns` ancestor needs no `:not([hideheader="true"])` predicate: the only `hideheader` treecol in the Library lives under the sidebar's unnamed `treecols` (``places.xhtml`` ~line 567), which the id scoping already excludes, and `placeContentColumns` is an id no other chrome file carries (grep of the installed `browser/omni.ja` 2026-10-27 names one file). The `.tree-columnpicker-button` arm is a descendant (not a child) selector because `MozTreecolPicker` appends the button inside its own `treecolpicker` element. The face rule overrides the bevel-relevant declarations only and leaves the stock `border-inline-start: 1px solid ThreeDLightShadow` divider (a system colour, no hex literal) and the `ordinal="1"` first-column omission standing, so the buttons run as a bevelled band divided by thin stock lines. The rules introduce no hex literal outside the pinned `{FACE, WHITE, BLACK, BUTTON_SHADOW (#AAAAAA), SELECTION (#CCCCFF)}` set, all already sheet members, so `TestFirefoxChromeShell::test_palette_is_exact` passes untouched. The three initially `hidden="true"` columns match the face rule but paint nothing while hidden; no separate rule is needed.

Extend the header comment's provenance block with a column-headers paragraph inserted into the landed Library-search paragraph's stay-Firefox sentence and a new paragraph before the header's closing `*/`: first, in the two existing sentences that list the stay-Firefox surfaces, drop the column headers — the trees paragraph becomes "The toolbar buttons and the Organize, View and Maintenance menus, downloads rich list and details pane stay Firefox's for the later parts of this series (the content-tree column headers and the toolbar's search filter have their own paragraphs below)." — keeping the asserted substrings `The toolbar buttons and the Organize, View` and `downloads rich list and details pane stay Firefox's` contiguous — and the search paragraph's corresponding sentence drops "the content tree's column headers," (leaving "The toolbar buttons and the Organize, View and Maintenance menus, the downloads rich list and the details pane stay Firefox's for the later parts of this series."). Second, append a new paragraph naming: no reference screenshot shows the Firefox Library window; the header face is the reference-grounded raised push button — `widgets/button.svg` (`#DDDDDD` face, black outline, `#FFFFFF`/`#AAAAAA` bevel), pinned by `tests/test_desktoptheme_button.py::TestButton` and `tests/test_desktoptheme_button_reference.py::TestButtonReference` — and the flat `#CCCCFF` no-bevel hover/pressed fill adapts `widgets/viewitem.svg`, pinned by `tests/test_desktoptheme_viewitem.py::TestViewItem` and `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_selection_background` (a platform colour adaptation 2026-10-27); the anatomy is read 2026-10-27 from the installed Firefox ESR 153.5.1 — `places.xhtml`'s `treecols#placeContentColumns` with its seven `treecol` columns (three starting `hidden="true"`) and `.tree-splitter` grippies, `tree.js`'s `MozTreecols` appending `<treecolpicker fixed="true">` when absent with `MozTreecolPicker`'s light-DOM `.tree-columnpicker-button` button and `MozTreecol`'s light-DOM `label.treecol-text`/`image.treecol-sortdirection` children; `tree.css` paints the stock header (`-moz-ColHeader`/`-moz-ColHeaderText` face and text, the `ThreeDLightShadow` `border-inline-start` divider and inset bottom shadow it keeps (no hex literal), the `-moz-ColHeaderHover`/`-moz-ColHeaderActive` hover/active washes this plan replaces, `min-height: max(24px, 1.3em)`, `padding: 0 4px`, the `ordinal="1"` divider omission, `sort-asc.svg`/`sort-dsc.svg` arrows drawn `currentColor`, the `columnpicker.svg` picker icon, and `treecol[dragging="true"]`'s `Graytext`); the intentionally unscoped surfaces — the `placesList` sidebar column (`hideheader="true"`), every other chrome window's tree-headers, the tree-splitter grippies and the `tree.css` `@media (-moz-platform: macos)` dotted-outline block — and that the sheet gains only these six selector arms; declaration checks do not establish rendered pixels.

In `tests/support/firefox_chrome_cases.py`, after the `moz-input-search#searchFilter` block (after the `--icon-color` entry), append two pinned dicts and register their arms:

    # The Library content tree's column headers: the Platinum raised
    # header buttons, the byte-recipe of the landed edit-bookmark
    # footer buttons, with the flat #CCCCFF hover/pressed fill and no
    # bevel (see the header's provenance paragraph).
    HEADER_FACE = {
        "background-color": f"{FACE} !important",
        "color": f"{BLACK} !important",
        "border-radius": "0 !important",
        "box-shadow":
            f"inset 1px 1px {WHITE} !important, "
            f"inset -1px -1px {BUTTON_SHADOW} !important",
    }
    HEADER_HOVER = {
        "background-color": f"{SELECTION} !important",
        "color": f"{BLACK} !important",
        "box-shadow": "none !important",
    }
    for _header_arm in (
        "treecols#placeContentColumns > treecol",
        "treecols#placeContentColumns .tree-columnpicker-button",
    ):
        REQUIRED_RULES[_header_arm] = HEADER_FACE
    for _header_arm in (
        "treecols#placeContentColumns > treecol:hover",
        "treecols#placeContentColumns > treecol:hover:active",
        "treecols#placeContentColumns .tree-columnpicker-button:hover",
        "treecols#placeContentColumns .tree-columnpicker-button:hover:active",
    ):
        REQUIRED_RULES[_header_arm] = HEADER_HOVER

(imports `FACE` and `BUTTON_SHADOW` join the module's existing palette import — check the module's current `from support.platinum_palette import …` line and add the missing names). `parse_css` splits the sheet's comma lists into one `rules` key per arm, so trailing-`!important`-pinned declaration dicts register arm-by-arm exactly as the landed `#placesList`/`#placeContent` pair already does; `TestFirefoxChromeShell::test_required_rules`, which iterates every `REQUIRED_RULES` entry against the sheet, picks the six arms up with no edit.

In `tests/test_firefox_theme_library.py`: add module constants beside `SEARCH_RULE` — `HEADER_FACE_ARMS` and `HEADER_HOVER_ARMS`, the two tuples above in sheet order — and a new class after `TestFirefoxLibrarySearchChrome`, `class TestFirefoxLibraryHeaderChrome(FirefoxChromeTestCase)`, holding: `test_header_rules_are_the_sheet_recipe` — for each of the six arms, `self.rules[arm]` equals its `REQUIRED_RULES[arm]` entry byte-for-byte and every value ends `!important`; `test_header_face_is_the_raised_button` — the two face arms carry exactly `background-color: #DDDDDD`, `color: #000000`, `border-radius: 0` and the two-part `box-shadow` bevel, and the four hover arms exactly `background-color: #CCCCFF`, `color: #000000`, `box-shadow: none`; `test_header_rules_scope_to_the_content_tree` — with `support.selector_matching.matches`, `treecols#placeContentColumns > treecol` matches a `treecol` child of `element("treecols", "placeContentColumns", parent=element("tree", "placeContent", ("placesTree",)))` and never a `treecol` under an id-less `treecols` (the `placesList` sidebar's, `hideheader="true"`), `treecols#placeContentColumns .tree-columnpicker-button` matches an `element("button", None, ("tree-columnpicker-button",), parent=element("treecolpicker", None, parent=<the placeContentColumns treecols>))` and never the same button under an id-less `treecols`, and the `:hover` arms match their fixtures with `hover=True` fixed (the matcher reads no `:active`, so the `hover:active` arms are pinned by the selector text alone, like the `::-moz-tree-*` pseudo-elements); and `test_header_provenance` — the comment header names `widgets/button.svg`, `tests/test_desktoptheme_button.py::TestButton`, `TestButtonReference`, `widgets/viewitem.svg`, `test_selection_background`, `tree.js`, `treecols#placeContentColumns`, `tree.css`, `-moz-ColHeader`, `ThreeDLightShadow`, `-moz-ColHeaderHover`, `sort-asc.svg`, `columnpicker.svg`, `Graytext`, `hideheader`, `No reference screenshot shows the Firefox Library window`, `Declaration checks do not establish rendered pixels` and `platform colour adaptation 2026-10-27` (pattern: `TestFirefoxLibrarySearchChrome::test_header_names_search_provenance`). Two incumbent adjustments in this module: `TestFirefoxLibraryChrome::test_library_tree_paint_is_scoped_to_the_places_trees` narrows its forbidden-stock tuple from `("twisty", "splitter", "treecol", "columnpicker")` to `("twisty", "splitter")` and its comment to say the column headers now carry their own rules under `TestFirefoxLibraryHeaderChrome`, additionally asserting that the sheet's rule names starting `treecols` are exactly the six header arms; and the twin comment inside `test_library_tree_provenance`'s body (the "column headers" wording at its stride through `twisty, splitter, treecol or column picker`) is trimmed the same way.

In `docs/invariants.md`, in the `## firefox` table: trim `column headers, ` from the landed places-trees row's stay-Firefox list (row `#placesList`, leaving every other word of that row unchanged), and append a row of its own after the search-box row (the register keeps one row per landed part): the Library content tree's header row (`treecols#placeContentColumns`'s seven columns and the column-picker button) is a run of Platinum raised header buttons — `#DDDDDD` face, black text, square corners, the `inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA` bevel — over the Firefox stock `ThreeDLightShadow` column divider, a hovered or pressed header flat `#CCCCFF` with no bevel, while the sort-direction arrows, picker icon, column drag colour, geometry and the `placesList` sidebar column stay Firefox's; the row's provenance records the `widgets/button.svg`/`widgets/viewitem.svg` adaptation and the `tree.js`/`tree.css`/`places.xhtml` paint chain read 2026-10-27 with `TestFirefoxLibraryHeaderChrome` plus `TestFirefoxChromeShell::test_palette_is_exact` in the test column, and declaration checks do not establish rendered pixels. `tests/invariants.py` is structural and stays green.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme_library.py`, `tests/support/firefox_chrome_cases.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The sheet's last block is the landed `moz-input-search#searchFilter` rule followed by only the two header rules above, whose six arms introduce no colour outside `{#DDDDDD, #FFFFFF, #000000, #AAAAAA, #CCCCFF}`; `TestFirefoxChromeShell::test_palette_is_exact` passes untouched and every other sheet-hygiene test over `self.rules` (scoping, token ones in `TestFirefoxChromeShell`) keeps green.
- `TestFirefoxLibraryHeaderChrome`'s four tests pass; the six arms equal their `REQUIRED_RULES` entries; `TestFirefoxChromeShell::test_required_rules` passes over the extended dict.
- The trimmed `TestFirefoxLibraryChrome` guard passes with `treecol`/`columnpicker` released to the new header rules and the `treecols`-prefix assertion holding; `TestFirefoxLibrarySearchChrome` and the byte-unchanged places-tree rules keep green against the still-unchanged trees/search text.
- The header's provenance block drops the column headers from the two stay-Firefox sentences (asserted substrings kept contiguous) and names the strings above; `test_header_provenance` pins them.
- `docs/invariants.md` carries the trimmed places-trees row and the new headers row with `TestFirefoxLibraryHeaderChrome` in its test column; `tests/invariants.py` stays green.
- `make check` passes.

### Firefox Platinum preferences, part 8: paint the panes' entry fields as the Platinum sunken line edit and their menulists as the Platinum raised push buttons (planned 2026-10-27 by the plan role; independent of the waiting Firefox Library column-headers plan — the two touch disjoint sheet and test files (`theme/firefox/org.macos8.desktop/chrome/userContent.css` and `tests/test_firefox_content_theme.py` versus `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/support/firefox_chrome_cases.py` and `tests/test_firefox_theme_library.py`), and their `docs/invariants.md` edits touch different rows (the Library plan trims the landed places-trees row and appends its own; this plan only appends its own row), so either order merges; it is part 8 of the about:preferences series, whose parts 1 (category navigation rows), 2 (sidebar separators), 3 (page background and heading bands), 4 (search field), 5 (pane push buttons), 6 (checkboxes) and 7 (radio groups) landed 2026-10-27) — this entry covers the panes' entry fields and menulists together because the two append inside the same `@-moz-document url("about:preferences")` block and extend the same `REQUIRED_PREFERENCES_RULES` dict and its ordered-rule assertions, so the two halves cannot merge independently (the pane push-buttons part recorded the same coupling against the search field); no further pane control waits beyond it — the panes' sub-dialogs are separate documents this sheet does not reach)

**Goal.** The landed parts left about:preferences' text entry fields and dropdown menulists Firefox's. `chrome/browser/content/browser/preferences/preferences.xhtml` (read 2026-10-27 from the installed Firefox ESR 153.5.1's `browser/omni.ja`; `vbox#mainPrefPane` opens ~line 243) authors both surfaces as ordinary light-DOM elements inside the pane: four `html:input[type="text"]` fields (`#homePageUrl` ~line 512, `#dohEnabledInputField` ~1352, `#dohStrictInputField` ~1389, and `#fxaSyncComputerName` ~1563 which starts `disabled="true"`) and eight XUL `menulist` elements (`#primaryBrowserLocale` ~335, `#homeMode` ~500, `#newTabMode` ~551, `#blockCookiesMenu` ~940, `#trackingProtectionMenu` ~967, `#fingerprintingProtectionMenu` ~995, `#dohEnabledResolverChoices` ~1349, `#dohStrictResolverChoices` ~1386) — no `html:textarea` exists in the pane. `chrome/toolkit/skin/classic/global/in-content/common-shared.css` (root `omni.ja`, read 2026-10-27) paints the fields `border: 1px solid var(--border-color)`, `border-radius: var(--border-radius-medium)`, `background-color: var(--background-color-box)`, `color: inherit` — rounded grey boxes reading as nothing Platinum on the white page part 3 painted — and paints the menulists like buttons (`button, …, xul|menulist` sharing the token `--button-*` pill recipe from `tokens-shared.css`/`tokens-brand.css`) with `:hover`/`[open="true"]`/disabled recolours; `chrome/toolkit/skin/classic/global/menulist.css` gives the menulist's shadow-tree `dropmarker` element its `content: url(chrome://global/skin/icons/arrow-down-12.svg)` drawn `currentColor` and owns the non-native focus outline. Paint the four enabled fields as the sheet's Platinum sunken line edit — white face, black text, square 1px black outline, `inset 1px 1px #999999` sunken shadow, the byte-recipe the landed about:config `#about-config-search` rule carries in this same sheet — and the eight enabled menulists as the landed `#mainPrefPane button` push-button recipe with the landed `#mainPrefPane button:hover` flat `#CCCCFF` no-bevel recipe extended to the open state. No reference screenshot shows Firefox's about:preferences; the field adapts this theme's `widgets/lineedit.svg` and the menulist face the reference-grounded `widgets/button.svg` (platform colour adaptations). The disabled `#fxaSyncComputerName` keeps Firefox's whole disabled paint (the push buttons' and radios' `:not([disabled])` choice). Geometry (`min-height`, `padding`, `margin`, font), the field focus outline, the `:user-invalid` error ring, the menulists' `dropmarker` arrow (it already follows `currentColor` black), the dropdown `menupopup` lists and their stock styling stay Firefox's.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userContent.css`, inside the existing `@-moz-document url("about:preferences")` block after the landed `radio:not([disabled])[selected] .radio-check` rule (currently the block's last rule), append three rules and nothing else:

    /* The panes' entry fields and menulists: the Platinum sunken line
       edit and raised push button (see the header's provenance
       paragraph). */
    #mainPrefPane input[type="text"]:not([disabled]) {
      background-color: #FFFFFF !important;
      color: #000000 !important;
      border: 1px solid #000000 !important;
      border-radius: 0 !important;
      box-shadow: inset 1px 1px #999999 !important;
    }

    #mainPrefPane menulist:not([disabled]) {
      background-color: #DDDDDD !important;
      color: #000000 !important;
      border: 1px solid #000000 !important;
      border-radius: 0 !important;
      box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA !important;
    }

    #mainPrefPane menulist:not([disabled]):hover,
    #mainPrefPane menulist[open="true"]:not([disabled]) {
      background-color: #CCCCFF !important;
      color: #000000 !important;
      box-shadow: none !important;
    }

The field rule carries `[type="text"]` step so it can never widen to the element name `input` beyond the authored population, and the plain `input`/`menulist` type selectors match without an `@namespace` because the sheet declares none (the landed `button`/`checkbox`/`radio` rules rely on the same). The menulist face rule out-specifies the stock `xul|menulist` token rules through the `#mainPrefPane` prefix, and the hover rule's two arms cover the stock `:hover` recolour and the `[open="true"]` active recolour `common-shared.css` applies. `parse_css` splits the comma list into one key per arm. The rules introduce no hex literal outside the pinned set `{#FFFFFF, #000000, #999999, #DDDDDD, #AAAAAA, #CCCCFF}` — every value already a sheet member — so `TestFirefoxContentTheme::test_palette_is_exact` passes untouched.

Extend the header comment's provenance block with an entry-fields-and-menulists paragraph inserted immediately after the landed radios paragraph and before the header's closing `*/`, and edit the radios paragraph's stay-Firefox sentence from "as do the panes' entry fields and menulists (later parts);" to "(the panes' entry fields and menulists have their own paragraph below);" keeping the rest of that sentence unchanged. The new paragraph names: no reference screenshot shows Firefox's about:preferences; the field is the sheet's Platinum sunken line edit, the byte-recipe of the landed about:config `#about-config-search` rule, adapting `widgets/lineedit.svg`, pinned by `tests/test_desktoptheme_lineedit.py::TestLineEdit` and `TestLineEditReference`; the menulist face is the landed `#mainPrefPane button` recipe adapting `widgets/button.svg`, pinned by `tests/test_desktoptheme_button.py::TestButton` and `tests/test_desktoptheme_button_reference.py::TestButtonReference`, and the flat `#CCCCFF` hover/open fill adapts `widgets/viewitem.svg`, pinned by `tests/test_desktoptheme_viewitem.py::TestViewItem` and `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_selection_background` (platform colour adaptations 2026-10-27); the anatomy read 2026-10-27 from the installed Firefox ESR 153.5.1 — `preferences.xhtml`'s four `html:input[type="text"]` fields (`#homePageUrl`, `#dohEnabledInputField`, `#dohStrictInputField`, `#fxaSyncComputerName`) and eight `menulist` elements (`#primaryBrowserLocale`, `#homeMode`, `#newTabMode`, `#blockCookiesMenu`, `#trackingProtectionMenu`, `#fingerprintingProtectionMenu`, `#dohEnabledResolverChoices`, `#dohStrictResolverChoices`) inside `#mainPrefPane` as authored light-DOM elements, `common-shared.css`'s stock field paint (`--border-color`, `--border-radius-medium`, `--background-color-box`, `color: inherit`, focus outline, `user-invalid` ring, disabled opacity 0.4) and token pill menu paint (`tokens-shared.css`/`tokens-brand.css`), and `menulist.css`'s shadow `dropmarker` with `arrow-down-12.svg` drawn `currentColor` — all packages `omni.ja` reads marked for the toolkit file and `browser/omni.ja` for `preferences.xhtml`; the intentionally unscoped surfaces — the disabled `#fxaSyncComputerName` (`:not([disabled])`), the menus' `menupopup` dropdown lists, the field focus outline and error ring, the dropmarker geometry and the panes' sub-dialogs (separate documents); and that there is no field hover rule because `widgets/lineedit.svg` ships no hover state; declaration checks do not establish rendered pixels.

In `tests/test_firefox_content_theme.py`: add module constants after `RADIO_FACE`/`RADIO_DOT` — `PANEFIELD = "#mainPrefPane input[type=\"text\"]:not([disabled])"`, `PANE_MENULIST = "#mainPrefPane menulist:not([disabled])"` and `PANE_MENULIST_HOVER = "#mainPrefPane menulist:not([disabled]):hover"` plus `PANE_MENULIST_OPEN = "#mainPrefPane menulist[open=\"true\"]:not([disabled])"` — pinned dicts `PANEFIELD_RULE` (the byte-recipe of this module's `FIELD_RULE`, spelled explicitly rather than aliased) and `PANE_MENULIST_RULE`/`PANE_MENULIST_HOVER_RULE` (the byte-recipes of `PANE_BUTTON_RULE`/`BUTTON_HOVER_RULE` above, spelled explicitly), extend `REQUIRED_PREFERENCES_RULES` with `PANEFIELD`, `PANE_MENULIST` and `PANE_MENULIST_HOVER` mapped to `PANEFIELD_RULE`, `PANE_MENULIST_RULE` and the `PANE_MENULIST_HOVER_RULE` shared by both hover arms, and add `class TestFirefoxPreferencesFieldsTheme(SheetCase)` with `AT_RULE_URL = "about:preferences"` after `TestFirefoxPreferencesRadioTheme`, holding: `test_field_and_menulist_rules_are_the_sheet_recipe` — each of the five `#mainPrefPane` field/menulist arms equals its pinned dict byte-for-byte, the dict entries and the `REQUIRED_PREFERENCES_RULES` entries being the same mapping; `test_field_and_menulist_rules_extend_the_ordered_rule_register` — `TestFirefoxPreferencesNavTheme::test_required_rules` (which asserts `set(self.rules) == set(REQUIRED_PREFERENCES_RULES)` and `self.selectors == list(REQUIRED_PREFERENCES_RULES)`) passes over the extended dict, proving the three rules are the block's last in sheet order so no earlier rule moved; `test_field_and_menulist_rules_scope_to_the_pane` — every arm starts `#mainPrefPane`, the field arm carries `[type="text"]` and `:not([disabled])` and no `moz-input-search`, the menulist face arm carries `:not([disabled])`, one hover arm carries `:hover` and the other `[open="true"]`, and no selector names `menupopup`, `#dialogTemplate` or `subdialog`; and `test_field_and_menulist_rules_use_the_pinned_palette` — every declaration carries `!important` and each arm's hex set is `input`: `{WHITE, BLACK, GREY}`, `menulist face`: `{WHITE, BLACK, FACE, BUTTON_SHADOW}`, `hover arms`: `{SELECTION, BLACK}`; matching through `support.selector_matching.matches` — the field arm matches `element("input", "homePageUrl", attrs={"type": "text"}, parent=element("html", None, parent=element("vbox", "mainPrefPane")))` and never the same fixture with `attrs={"type": "text", "disabled": "true"}` or `attrs={"type": "range"}`, the menulist face arm matches `element("menulist", "homeMode", parent=element("vbox", "mainPrefPane"))` and never a `menulist` under an element("vbox", "dialogTemplate") parent, and the two hover arms match their fixtures with `hover=True` and `attrs={"open": "true"}` respectively (matcher text gives attribute support); and `test_header_names_field_provenance` — the header names the strings above (pattern: `TestFirefoxPreferencesRadioTheme::test_header_names_radio_provenance`). No incumbent test edits beyond the extended dict: the palette, custom-property and other per-selector tests keep to their own selectors, and nothing in `FORBIDDEN_PAGE_CHROME`, `CONFIG_*` or the downloads/`about:config` case classes names `input`/`menulist`.

In `docs/invariants.md`, in the `## firefox` table, append a row of its own immediately after the landed radios row (the register keeps one row per landed part; the new plan only appends — no existing row's word changes): the about:preferences enabled entry fields (the four `html:input[type="text"]` inside `#mainPrefPane`) are the Platinum sunken line edit — white face, black text, square 1px black outline, the `inset 1px 1px #999999` shadow — and the enabled menulists (the eight `menulist` inside `#mainPrefPane`) are square `#DDDDDD` push buttons with a black outline and the white/`#AAAAAA` raised bevel, a hovered (or `[open="true"]`) one flat `#CCCCFF` with black text and no bevel, while the disabled `#fxaSyncComputerName`, dropdown `menupopup` lists, dropmarker arrow, field focus outline, error ring and geometry stay Firefox's; the row's provenance records the `widgets/lineedit.svg`/`widgets/button.svg`/`widgets/viewitem.svg` adaptations and the `preferences.xhtml`/`common-shared.css`/`menulist.css`/`tokens-shared.css` paint chain read 2026-10-27 with `TestFirefoxPreferencesFieldsTheme` plus `TestFirefoxContentTheme::test_palette_is_exact` in the test column, and declaration checks do not establish rendered pixels. `tests/invariants.py` is structural and stays green.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userContent.css`, `tests/test_firefox_content_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The `about:preferences` block gains exactly the three rules above after the radio-selected rule (five selector arms), introducing no hex outside `{#FFFFFF, #000000, #999999, #DDDDDD, #AAAAAA, #CCCCFF}` (all pre-existing sheet members); `TestFirefoxContentTheme::test_palette_is_exact` passes untouched.
- `TestFirefoxPreferencesFieldsTheme`'s tests pass; `TestFirefoxPreferencesNavTheme::test_required_rules` and `test_parsed_rules_are_exactly_the_nav_rules` hold over the extended `REQUIRED_PREFERENCES_RULES` with the five new arms last in sheet order; every other `tests/test_firefox_content_theme.py` class (downloads, `about:config`, sidebar/search, buttons, checkboxes, radios) keeps green against unchanged text.
- The header comment drops the radios paragraph's later-parts clause (the replacement sentence above) and carries the new provenance paragraph naming the strings above; `test_header_names_field_provenance` pins them.
- `docs/invariants.md` gains the entry-fields-and-menulists row after the radios row with `TestFirefoxPreferencesFieldsTheme` named in its test column and no other row's wording changed; `tests/invariants.py` stays green.
- `make check` passes.

## Done
