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

### Firefox Platinum chrome: Library window series, part 6/6: paint the details pane's bookmark fields, folder dropdown and tag selector as the Platinum line edits, push-button menulist and sunken list field (planned 2026-10-27 by the plan role; "requires part 5/6 landed" — this part appends after and edits the tail of part 5's downloads-view paint, and it narrows the stock stay-Firefox sentences that parts 1, 2 and 4 land and part 5 keeps; this is the series' last part and nothing waits behind it)

**Goal.** After the landed parts, the Library window's details pane is still Firefox's: the bookmark fields, the folder dropdown and the tag selector read as the platform skin, not Platinum. In `chrome/browser/content/browser/places/places.xhtml` (read 2026-10-27 from the installed Firefox ESR 153.5.1's `browser/omni.ja`), `vbox#detailsPane` holds `vbox#itemsCountBox` and `vbox#infoBox`, and `#infoBox` embeds the bookmark editor's `#editBookmarkPanelContent` markup: labels, `html:input#editBMPanel_namePicker`, `html:input#editBMPanel_locationField`, an `hbox.editBMPanel_folderRow` holding `menulist#editBMPanel_folderMenuList.folder-icon` and `button#editBMPanel_foldersExpander.expander-down.panel-button`, `vbox#editBMPanel_folderTreeRow` holding `button#editBMPanel_newFolderButton`, `html:input#editBMPanel_tagsField` (an autocomplete input with `#editBMPanel_tagsAutocomplete` and `button#editBMPanel_tagsSelectorExpander`), `div#editBMPanel_tagsSelectorRow` holding `richlistbox#editBMPanel_tagsSelector`, and `html:input#editBMPanel_keywordField`. The same ids live in `browser.xhtml`'s `#editBookmarkPanel`, whose landed sheet section already paints its copies with `#editBookmarkPanel`-prefixed rules, and a grep of the omni's chrome markup (`*.xhtml`/`*.html`) finds a `detailsPane` element only in places.xhtml — so the Library rules must scope through `#detailsPane` and cannot touch the panel's copies. `chrome/browser/skin/classic/browser/places/organizer-shared.css` owns the pane's layout (`#detailsPane` `min-height: 16em`/`padding: 5px`, the `#editBookmarkPanelContent` grid, `#editBMPanel_tagsSelector` `margin: 4px`); `editBookmarkPanel.css`'s expander, field and focus paints are all `#editBookmarkPanel`-scoped, so the Library's expander buttons keep the toolkit's global button face; and `chrome/toolkit/skin/classic/global/global-shared.css`, `button.css`, `menulist.css` and `richlistbox.css` supply the stock field, button, menulist and listbox faces. Paint the four fields as this sheet's Platinum line edit, the folder menulist as its Platinum push-button menulist and the tags selector as its Platinum sunken list field — the byte-recipes the landed `#editBookmarkPanel` field and menulist rules and the landed `#placesList`/`#contentAreaDownloadsView #downloadsListBox:not(:empty)` list-field rules carry (platform colour adaptations), with square rows and a flat `#CCCCFF` selected row in the tag selector and no hover rule anywhere (the landed field and list recipes have none). The pane's remaining anatomy stays Firefox's, the same choice the landed bookmark editor's section makes for these widgets: the two expander buttons, the New Folder button, the folder tree, the labels and caption labels, `#itemsCountBox`, `#editBMPanel_itemsCountText`, the tags autocomplete panel, the menulist's popup list and the stock margins.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, after part 5's landed `toolbar#placesToolbar toolbarbutton#clearDownloadsButton:not([disabled]):hover` rule (then the sheet's last rules), with a short comment naming the adaptations and the `#detailsPane`-only scoping reason, append six rules and nothing else:

    /* The Library details pane's bookmark fields, folder dropdown and tag
       selector adapt the sheet's landed line-edit, push-button and sunken
       list-field recipes. The same editBMPanel ids live in browser.xhtml's
       #editBookmarkPanel, whose landed rules paint its copies, and a
       detailsPane element exists only in places.xhtml, so these rules scope
       through #detailsPane. The expander buttons, the New Folder button,
       the folder tree, the labels and the popup lists stay Firefox's, as
       the landed bookmark editor's section does. */
    #detailsPane #editBMPanel_namePicker,
    #detailsPane #editBMPanel_locationField,
    #detailsPane #editBMPanel_tagsField,
    #detailsPane #editBMPanel_keywordField {
      background-color: #FFFFFF !important;
      color: #000000 !important;
      border: 1px solid #000000 !important;
      border-radius: 0 !important;
      box-shadow: inset 1px 1px #999999 !important;
    }

    #detailsPane #editBMPanel_folderMenuList {
      background-color: #DDDDDD !important;
      color: #000000 !important;
      border: 1px solid #000000 !important;
      border-radius: 0 !important;
      box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA !important;
    }

    #detailsPane #editBMPanel_folderMenuList:hover:not([disabled]) {
      background-color: #CCCCFF !important;
      color: #000000 !important;
      box-shadow: none !important;
    }

    #detailsPane richlistbox#editBMPanel_tagsSelector {
      appearance: none !important;
      background-color: #FFFFFF !important;
      color: #000000 !important;
      border: 1px solid #000000 !important;
      border-radius: 0 !important;
      box-shadow: inset 1px 1px #999999 !important;
    }

    #detailsPane richlistbox#editBMPanel_tagsSelector > richlistitem {
      border-radius: 0 !important;
    }

    #detailsPane richlistbox#editBMPanel_tagsSelector > richlistitem[selected] {
      background-color: #CCCCFF !important;
      color: #000000 !important;
    }

In `tests/support/firefox_chrome_cases.py`: extend the shared `REQUIRED_RULES` dict after part 5's landed `toolbar#placesToolbar toolbarbutton#clearDownloadsButton` hover entry (keep the dict's footer comment accurate), in this order — `"#detailsPane #editBMPanel_namePicker"`, `"#detailsPane #editBMPanel_locationField"`, `"#detailsPane #editBMPanel_tagsField"` and `"#detailsPane #editBMPanel_keywordField"` (the byte-recipes of the landed `#editBookmarkPanel #editBMPanel_namePicker` field entry: `WHITE` face, `BLACK` text, `1px solid {BLACK}`, radius 0, `inset 1px 1px {GREY}`), `"#detailsPane #editBMPanel_folderMenuList"` and its `:hover:not([disabled])` arm (the byte-recipes of the landed `#editBookmarkPanel #editBMPanel_folderMenuList` entries: `{FACE}` face, `BLACK` text, `1px solid {BLACK}`, radius 0, `BUTTON_BEVEL`; hover `{SELECTION}` face, `BLACK` text, `box-shadow: none`), and `"#detailsPane richlistbox#editBMPanel_tagsSelector"` (the landed `#placesList` mapping plus `"appearance": "none !important"`), `"#detailsPane richlistbox#editBMPanel_tagsSelector > richlistitem"` (`{"border-radius": "0 !important"}`) and `"#detailsPane richlistbox#editBMPanel_tagsSelector > richlistitem[selected]"` (the byte-recipe of part 5's landed downloads selected-row entry) — each spelled explicitly with the shared constants.

In `tests/test_firefox_theme_library.py`: add module constants after part 5's `CLEAR_BUTTON_RULES` — `DETAILS_FIELD_RULES` (the four `#detailsPane` field selectors), `DETAILS_MENULIST_RULES` (the menulist's two arms) and `DETAILS_TAGS_RULES` (the tags selector's three arms) — and add `class TestFirefoxLibraryDetailsPaneChrome(FirefoxChromeTestCase)` after part 5's `TestFirefoxLibraryDownloadsChrome`, holding:

- `test_details_pane_rules_match_the_required_rules` — each of the nine arms equals its `REQUIRED_RULES` entry byte-for-byte and every declaration ends `!important`;
- `test_details_pane_rules_scoped_to_the_details_pane` — via `support.selector_matching`'s `element`/`matches`: build a `window#places` holding `vbox#detailsPane` holding `vbox#infoBox` holding `div#editBookmarkPanelContent` with the four fields, the folder `hbox` (menulist, `#editBMPanel_foldersExpander`) and tags `hbox` (`#editBMPanel_tagsField`, `#editBMPanel_tagsSelectorExpander`), the New Folder button and the tags `richlistbox`; beside it in the same window a `panel#editBookmarkPanel` (`attrs={"type": "arrow"}`) holding copies of the four fields, the menulist and the tags richlistbox, plus a stray id-less `html:input` and an id-less `richlistbox`. Assert the four fields match their selectors with and without hover; the menulist matches its normal arm idle and hovered but its hover arm only with `hover=True` and never when carrying a `disabled` attribute; the tags selector matches its three arms with a `richlistitem` child (its `[selected]` copy matching the selected arm); and the `#editBookmarkPanel` copies, the two expander buttons, the New Folder button, the stray input and the stray richlistbox match none of the nine selectors;
- `test_details_pane_selector_set_is_exact` — the sheet's whole set of rule names containing `detailsPane` is exactly the nine new selectors, and the whole set containing `editBMPanel` is exactly those nine plus the landed ten `#editBookmarkPanel`-prefixed ones (the four fields, the folder menulist, the Done/Remove buttons and their three hover arms);
- `test_header_names_details_pane_provenance` (pattern: `TestFirefoxLibraryDownloadsChrome`'s provenance test) asserting the header names the strings below.

Extend the assertions of `test_library_tree_provenance` and `test_header_names_search_provenance` for the two narrowed sentences below, and in the landed `TestFirefoxLibraryToolbarChrome::test_header_names_toolbar_provenance` refresh the fragments it names from the landed toolbar paragraph (whose stay-Firefox list drops the details pane as the narrowed sentences do). Leave every other class's tests to pass over unchanged rule text.

The header gains exactly one paragraph, after part 5's landed downloads paragraph and before the closing `*/`, naming: no reference screenshot shows the Firefox Library window; the fields reuses this sheet's landed `#editBookmarkPanel` line-edit recipe (`#FFFFFF` face, black text, square `1px solid #000000` outline, `inset 1px 1px #999999` shadow) and the folder menulist its landed push-button menulist recipe (`#DDDDDD` face, black outline, the ``inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA`` raised bevel, flat `#CCCCFF` hover), grounded in `widgets/lineedit.svg` and `widgets/button.svg` and pinned by `tests/test_desktoptheme_lineedit.py::TestLineEdit`, `TestLineEditReference`, `tests/test_desktoptheme_button.py::TestButton` and `tests/test_desktoptheme_button_reference.py::TestButtonReference`; the tag selector reuses the landed `#placesList` sunken list-field recipe with the selected row's `widgets/viewitem.svg` highlight, pinned by `tests/test_desktoptheme_viewitem.py::TestViewItem` and `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_selection_background`; no hover rule exists on the fields or the tag selector's rows because the landed recipes have none (the menulist's hover arm is the landed menulist recipe's own); the rules scope through `#detailsPane` because the same `editBMPanel` ids live in `browser.xhtml`'s `#editBookmarkPanel` (whose landed `#editBookmarkPanel`-prefixed rules paint its copies) and `#bookmarkpropertiesdialog`, and a grep of the omni's chrome markup finds a `detailsPane` element only in places.xhtml; the anatomy is read 2026-10-27 from the installed Firefox ESR 153.5.1 — `places.xhtml`'s `vbox#detailsPane` holding `#itemsCountBox` and `#infoBox` with the embedded `#editBookmarkPanelContent` markup listed in the goal, `organizer-shared.css` owning the pane's `min-height: 16em`/`padding: 5px` and the `#editBookmarkPanelContent` grid and the `#editBMPanel_tagsSelector` `margin: 4px`, `editBookmarkPanel.css`'s expander and focus paints being `#editBookmarkPanel`-scoped, and the toolkit's `global-shared.css`, `button.css`, `menulist.css` and `richlistbox.css` supplying the stock faces; and the intentionally unchanged paint — the two expander buttons, the New Folder button, the folder tree, the labels and caption labels, `#itemsCountBox` and `#editBMPanel_itemsCountText`, the tags autocomplete panel, the menulist's popup list and the stock margins — plus that declaration checks do not establish rendered pixels.

In the header's earlier paragraphs, narrow the stay-Firefox sentences the landed text carries to drop the details pane: the trees paragraph's sentence becomes "The toolbar's back and forward buttons stay Firefox's (the content-tree column headers, the toolbar's search filter and the toolbar's menu titles have their own paragraphs below)." and the search paragraph's sentence becomes "The toolbar's back and forward buttons stay Firefox's." — keeping the asserted substring `The toolbar's back and forward buttons stay Firefox's` contiguous — and the toolbar paragraph's stay-Firefox list drops "and the details pane" after the window body.

In `docs/invariants.md`, in the `## firefox` table: trim the landed places-trees row's stay-Firefox list from "the row icons, twisties, the toolbar's back and forward buttons and the details pane stay Firefox's" to "the row icons, twisties and the toolbar's back and forward buttons stay Firefox's", trim part 4's landed toolbar row's stay-Firefox list to drop "and the details pane" the same way, and append a new row immediately after part 5's landed downloads row: the Library window's details pane (`#detailsPane` in `places.xhtml`) paints its bookmark fields (`#editBMPanel_namePicker`, `#editBMPanel_locationField`, `#editBMPanel_tagsField`, `#editBMPanel_keywordField`) as the white square Platinum line edit with black text and the `#999999` top-left inner shadow, its folder dropdown (`#editBMPanel_folderMenuList`) as the square `#DDDDDD` Platinum push-button menulist with an enabled hovered state flat `#CCCCFF`, black text and no bevel, and its tag selector (`richlistbox#editBMPanel_tagsSelector`) as the opaque `#FFFFFF` Platinum sunken list field with square rows and a flat `#CCCCFF` selected row, while the two expander buttons, the New Folder button, the folder tree, the labels, `#itemsCountBox` and the popup lists stay Firefox's; the row's provenance records the landed `#editBookmarkPanel` and `#placesList` recipe reuse grounded in `widgets/lineedit.svg`, `widgets/button.svg` and `widgets/viewitem.svg` and pinned by `TestLineEdit`, `TestLineEditReference`, `TestButton`, `TestButtonReference`, `TestViewItem` and `test_selection_background` (platform colour adaptations 2026-10-27), the `#detailsPane`-only scoping fact and the `places.xhtml`/`organizer-shared.css`/`editBookmarkPanel.css`/toolkit chain read 2026-10-27 with `TestFirefoxLibraryDetailsPaneChrome` plus `TestFirefoxChromeShell::test_palette_is_exact` in the test column, and that declaration checks do not establish rendered pixels. `tests/invariants.py` is structural and stays green.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/support/firefox_chrome_cases.py`, `tests/test_firefox_theme_library.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The sheet gains exactly the six rules above after the `clearDownloadsButton` hover rule, introducing no hex outside the pre-existing sheet member set (`{#DDDDDD, #000000, #888888, #999999, #FFFFFF, #AAAAAA, #CCCCFF, #EEEEEE}`); `TestFirefoxChromeShell::test_palette_is_exact` passes untouched, and no landed rule's text changes other than the narrowed header sentences.
- `TestFirefoxLibraryDetailsPaneChrome`'s tests pass; the nine new `REQUIRED_RULES` entries make `TestFirefoxChromeShell::test_required_rules` pass without edits (order-insensitive per its `for selector, expected in REQUIRED_RULES.items()` loop); every other `tests/test_firefox_theme_library.py` class (trees, search, headers, toolbar, downloads) keeps green against unchanged rule text with the refreshed provenance fragments, and the landed class-level exact-selector-set tests keep passing because the nine new selectors carry none of their pinned tokens (`placeList`, `placeContent`, `searchFilter`, `placeContentColumns`, `placesToolbar`, `clearDownloadsButton`, `placesMenu`).
- The header gains exactly one paragraph after part 5's downloads paragraph and before `*/`, carrying the provenance strings above (pinned by `test_header_names_details_pane_provenance`); the earlier paragraphs' sentences are narrowed exactly as specified, with the asserted substring contiguous, and the toolbar provenance test's corresponding fragments are refreshed in the same edit.
- `docs/invariants.md` trims the two stay-Firefox lists as specified and gains the details-pane row after part 5's downloads row, with `TestFirefoxLibraryDetailsPaneChrome` named in its test column and no other row's wording changed; `tests/invariants.py` stays green.
- `make check` passes.

### Firefox Platinum content: paint about:support's tables, column-header cells and buttons as the Platinum sunken list field, raised headers and push buttons (planned 2026-10-27 by the plan role; independent of the waiting Library parts 5/6 and 6/6 — those touch `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/support/firefox_chrome_cases.py`, `tests/test_firefox_theme_library.py` and only trim/append in `docs/invariants.md`, while this plan touches `theme/firefox/org.macos8.desktop/chrome/userContent.css` and `tests/test_firefox_content_theme.py` and only appends its own new row in `docs/invariants.md`, so either order merges; no other content surface or page waits behind it)

**Goal.** After the landed content adaptations (about:downloads, about:config, the about:preferences series), the troubleshooting page Firefox builds at `about:support` is stock: its tables keep `chrome/toolkit/skin/classic/global/in-content/info-pages.css`'s hairline-bordered `--table-*` paint and rounded `var(--border-radius-small)` corners, and its ten buttons keep the stock button face. This plan repaints the page as the Platinum window body's content: each `#contents` table as the landed sunken list field with `#EEEEEE` alternate rows, each `th` header cell as the Library content-tree's raised column-header face, and every page button as the landed Platinum push button. The page body, its `h1`/`h2` section headings, the loaded-about paragraphs, the pre-existing `.action-box` card, the codec table's supported/unsupported washes and the `tree`, `details` and generated sub-table helpers stay Firefox's.

**Verified facts (checked 2026-10-27 against the installed Firefox ESR 153.5.1, browser/toolkit `omni.ja`).**
- `chrome/toolkit/content/global/aboutSupport.xhtml` is the page loaded at `about:support` (its `aboutSupport.js` self-references `about:support` in its error paths) — one light-DOM HTML document: `grep -c attachShadow` returns 0 for both `aboutSupport.xhtml` and `aboutSupport.js`, so every node the rules touch is reachable from a document-level rule (unlike `about:logins` and `about:addons`, whose rows and search fields live in shadow roots with no `::part`, so they are out of this plan — recorded here so the next plan run does not re-open them).
- The markup defines exactly ten `<button id="…">` elements: `#copy-raw-data-to-clipboard` and `#copy-to-clipboard` in the page header, `#reset-box-button`, `#restart-in-safe-mode-button` and `#clear-startup-cache-button` inside `.action-box`, and `#profile-dir-button`, `#enumerate-database-button`, `#verify-place-integrity-button`, `#place-database-stats-toggle` and `#support-printing-clear-settings-button` inside `#contents`. Its tables are plain `<table>` elements inside `div#contents` (26 `<table>` tags statically — most rows are built by `aboutSupport.js`'s `$.new` helper with no row classes — with 59 `th class="column"` header cells plus four `th class="name"`/`th class="value"`), and and `chrome/toolkit/skin/classic/global/aboutSupport.css` styles `#codec-table`'s cells with green/cream supported/unsupported washes painted on the `td`s themselves.
- `info-pages.css` (the page's imported skin base) paints `table { background-color: var(--table-background-color); … border-radius: var(--border-radius-small); border-spacing: 0; }`, `th { background-color: var(--table-header-background-color); border: 1px solid var(--table-border-color); }` and `td { border: 1px solid var(--table-border-color); }` — rules the sheet must override per arm; `body.wide-container` paints no background of its own, so `body` stays Firefox's and this plan paints no page-background rule (the landed about:config and about:downloads precedents likewise paint widget faces only).

**Grounding (platform adaptation, steward clarification 2026-10-25).** No reference screenshot in `macos8.6-screenshots/` shows any Firefox surface, so this page samples no reference pixel: the face, outline and sunken shadow adapt `widgets/lineedit.svg`'s line-edit recipe, pinned by `tests/test_desktoptheme_lineedit.py::TestLineEdit` and `TestLineEditReference` (grounded in `macos8.6-screenshots/firstboot_betawiki.png`); the `#EEEEEE` alternate rows reuse the pinned `[Colors:View] BackgroundAlternate` trough, re-derived by `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_view_background_alternate`; the `th` header face and bevel copy the landed Library column-header recipe byte-for-byte, whose raise is `widgets/tabbar.svg`'s raised tab face, pinned by `tests/test_desktoptheme_tabbar.py::TestTabBar` and `TestTabBarReference`; the `#CCCCFF` selected/hover wash reuses the pinned `[Colors:Selection]`, re-derived by `TestReferenceAnchors.test_selection_background`; and the push-button face/bevel is the shared `widgets/button.svg` recipe, pinned by `tests/test_desktoptheme_button.py::TestButton` and `tests/test_desktoptheme_button_reference.py::TestButtonReference`.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userContent.css`, after the landed `@-moz-document url("about:preferences")` block (the file's last control adaptation), add the block comment `/* about:support tables and buttons adaptation 2026-10-27 (see the header's provenance paragraph) */` and then exactly this block:

```css
@-moz-document url("about:support") {
  #contents table {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #000000 !important;
    border-radius: 0 !important;
    box-shadow: inset 1px 1px #999999 !important;
  }

  #contents table tr:nth-child(2n) {
    background-color: #EEEEEE !important;
  }

  #contents table th,
  #contents table td {
    border: 0 !important;
    border-radius: 0 !important;
  }

  #contents table th {
    background-color: #DDDDDD !important;
    color: #000000 !important;
    box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA !important;
  }

  #contents table th:hover {
    background-color: #CCCCFF !important;
    color: #000000 !important;
    box-shadow: none !important;
  }

  #copy-raw-data-to-clipboard,
  #copy-to-clipboard,
  .action-box button,
  #profile-dir-button,
  #enumerate-database-button,
  #verify-place-integrity-button,
  #place-database-stats-toggle,
  #support-printing-clear-settings-button {
    background-color: #DDDDDD !important;
    color: #000000 !important;
    border: 1px solid #000000 !important;
    border-radius: 0 !important;
    box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA !important;
  }

  #copy-raw-data-to-clipboard:hover:not(:disabled),
  #copy-to-clipboard:hover:not(:disabled),
  .action-box button:hover:not(:disabled),
  #profile-dir-button:hover:not(:disabled),
  #enumerate-database-button:hover:not(:disabled),
  #verify-place-integrity-button:hover:not(:disabled),
  #place-database-stats-toggle:hover:not(:disabled),
  #support-printing-clear-settings-button:hover:not(:disabled) {
    background-color: #CCCCFF !important;
    color: #000000 !important;
    box-shadow: none !important;
  }
}
```

The zebra arm lands beneath the codec table's own `td` washes, so `#codec-table`'s supported/unsupported cells keep their status colours while their outer face and outline become the field's; the header paragraph states this. The last two `th`-adjacent cells (`th.name`/`th.value`) take the same header face, so the whole palette paints one raised header run.

In `tests/test_firefox_content_theme.py`: insert module constants and a `REQUIRED_SUPPORT_RULES` dict after the landed `REQUIRED_PREFERENCES_RULES` dict and before `class SheetCase` — `SUPPORT_LIST = "#contents table"`, `SUPPORT_ZEBRA = SUPPORT_LIST + " tr:nth-child(2n)"`, `SUPPORT_CELL = SUPPORT_LIST + " th, " + SUPPORT_LIST + " td"`, `SUPPORT_HEADER = SUPPORT_LIST + " th"`, `SUPPORT_HEADER_HOVER = SUPPORT_HEADER + ":hover"`, `SUPPORT_BUTTONS` (the eight-arm id/`.action-box button` face selector above), `SUPPORT_BUTTONS_HOVER` (its `:hover:not(:disabled)` companion) — with dict values copied from the landed `FIELD_RULE`, `BUTTON_RULE` and `BUTTON_HOVER_RULE` shared arms so the new arms are byte-identical to the landed recipes; the `SUPPORT_ZEBRA` value is `"background-color": f"{TROUGH} !important"` as `CONFIG_ODD` already records, and the `SUPPORT_CELL` value is `{"border": "0 !important", "border-radius": "0 !important"}`.

Then add `class TestFirefoxSupportTheme(SheetCase)` after the landed preferences field/menulist class, with at least: `test_support_rules_match_the_required_rules` (each arm equals its `REQUIRED_SUPPORT_RULES` entry byte-for-byte and the at-rule register gains the `about:support` body — extend whichever landed test enumerates the sheet's `@-moz-document` bodies, currently `test_sheet_has_the_downloads_config_and_preferences_at_rules`, to name the fourth URL); `test_support_table_rules_scope_to_the_contents_div` (via `support.selector_matching`'s `element`/`matches`: the selectors match a `table`/`th`/`tr` inside `#contents` and carry no token from `FORBIDDEN_PAGE_CHROME`, keeping the landed `body`/`h1` guard intact); `test_support_buttons_scope_to_the_page_ids` (the face selector matches `element("button", "copy-to-clipboard")` and the `.action-box` arm, not a chrome-scope element — and its hover arm excludes a `:disabled` button); `test_support_rules_use_the_pinned_palette` (every hex in `{BLACK, WHITE, GREY, FACE, TROUGH, SELECTION}` plus `BUTTON_SHADOW` resolves to the constants' pinned values and introduces no token outside the pre-existing sheet member set); and `test_header_names_support_provenance` (pattern: the landed `test_header_names_preferences_provenance`) asserting the new header paragraph carries the strings named below.

In the same file extend no other class's assertions: none of the landed selectors or arms change.

The header comment gains exactly one paragraph, after the landed about:preferences paragraph and before the closing `*/`, naming: `aboutSupport.xhtml`/`aboutSupport.js`'s light-DOM markup (the ten ids and the `th` classes as verified above), the recipes and pinned tests from the grounding list, the sentence that the codec table's status washes survive beneath the field Zebra, the sentences that the page body, headings, `.action-box` card and generated helper tables stay Firefox's, the note that `about:logins` and `about:addons` are shadow-DOM pages this document-level sheet cannot reach, the applicability sentence (the page loads top-level in a tab like the landed about:config, and the implementer performs the same headless ESR run with a temporary profile and a `@-moz-document url("about:support")` recolour rule the sheet's about:downloads paragraph records, stating what it showed), and the sheet's standard "declaration checks do not establish rendered pixels" close.

In `docs/invariants.md`, in the `## firefox` table: append exactly one row after the last firefox row with the guarantee in one sentence (the `#contents` tables are the `#FFFFFF` sunken list field with square `1px` `#000000` outline, the `#999999` top-left shadow and `#EEEEEE` alternate rows, their `th` cells the raised `#DDDDDD` header face with the flat `#CCCCFF` hover, and the page's ten buttons plus `.action-box`'s buttons the Platinum push button with that hover while disabled buttons keep Firefox's paint) and the test column naming `tests/test_firefox_content_theme.py::TestFirefoxSupportTheme`; trim no landed row (this plan closes no other surface).

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userContent.css`, `tests/test_firefox_content_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The sheet gains exactly the seven rule blocks above inside one new `@-moz-document url("about:support")` block after the about:preferences block, introducing no hex outside the pre-existing sheet member set (`{#DDDDDD, #000000, #888888, #999999, #FFFFFF, #AAAAAA, #CCCCFF, #EEEEEE}`), changing no landed rule's text, and introducing no `body`/`h1`-scoped selector (`FORBIDDEN_PAGE_CHROME` stays green).
- `TestFirefoxSupportTheme`'s tests pass; the `REQUIRED_SUPPORT_RULES` entries and the extended at-rule enumeration test pass without edits to any landed arm.
- The header gains exactly one paragraph after the about:preferences paragraph and before `*/`, carrying the provenance strings above (pinned by `test_header_names_support_provenance`), with the headless-run sentence stating what the run showed.
- `docs/invariants.md` gains exactly one appended row after the last `## firefox` row with `TestFirefoxSupportTheme` in its test column and no landed row's wording changed; `tests/support/invariants.py`'s register stays in step.
- `make check` passes.

## Done
