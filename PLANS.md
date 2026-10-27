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

### Firefox Platinum chrome, part 1 of a Library window series: paint the two places trees as the Platinum sunken list field (planned 2026-10-27 by the plan role; independent of the waiting about:preferences pane push-buttons plan — the two touch disjoint files (`theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/support/firefox_chrome_cases.py` and the new `tests/test_firefox_theme_library.py` versus `theme/firefox/org.macos8.desktop/chrome/userContent.css`, `tests/test_firefox_content_theme.py` and its support) so either order merges, `docs/invariants.md` gaining only append-only rows in both; it is part 1 of a Firefox Library window series — the toolbar's chrome buttons and three Organize/View/Maintenance menus, the `moz-input-search#searchFilter` box, the content tree's column headers, the `richlistbox#downloadsListBox` downloads view and the `#detailsPane` bookmark-details fields are later parts that wait behind this one, which establishes the window's base recipe) 

**Goal.** The Library window (`chrome/browser/content/browser/places/places.xhtml`, `window#places`, `windowtype="Places:Organizer"`) keeps Firefox's paint everywhere: its two XUL trees — the left sidebar folder tree `tree#placesList.placesTree` (one `treecol`, `hideheader="true"`, `seltype="single"`) and the content list `tree#placeContent.placesTree` (seven sortable `treecol` columns and its `treecols#placeContentColumns`) — draw from `chrome/toolkit/skin/classic/global/tree/tree.css` (read from the installed `/usr/lib/firefox-esr/omni.ja` 2026-10-27): `tree { background-color: Field; color: FieldText; border: 1px solid ThreeDShadow; }`, the rows `1px solid transparent` with `treechildren::-moz-tree-row(multicol, odd)` striped `-moz-oddtreerow`, a hovered row washed `hsla(0, 0%, 50%, 0.15)`, and a selected row `-moz-cellhighlight` (or `SelectedItem` focused); the browser-side `chrome/browser/content/browser/places/places.css` strips the stock frame itself (`.placesTree { appearance: none; margin: 0; border: 0; }`) and the browser skin's `places/organizer.css` paints `#placesView { background-color: Window; }` — so on the white window face the trees read as grey-field bordered boxes. Paint both trees as the sheet's established Platinum sunken list field — the byte-recipe `#metatree`/`#imagetree` already carry (opaque `#FFFFFF` face, square 1px `#000000` outline, the `#999999` sunken top-left inner shadow, rows transparent over the field so no skin hover wash paints, a selected row flat `#CCCCFF` with black text) plus the odd-row stripe floated back onto the field face — the same field every tree and list in this theme reads as. No reference screenshot shows the Firefox Library window; the faces adapt this theme's `widgets/lineedit.svg` and `widgets/viewitem.svg` (a platform colour adaptation).

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, append at the very end, after the security-groupbox block, one scope comment plus the metatree/imagetree recipe applying to both trees:

    /* Library window places trees: the Platinum sunken list field with
       transparent rows, a flat #CCCCFF selected row and the odd-row
       stripe floated back onto the field (see the header's provenance
       paragraph). */
    #placesList,
    #placeContent {
      background-color: #FFFFFF !important;
      color: #000000 !important;
      border: 1px solid #000000 !important;
      border-radius: 0 !important;
      box-shadow: inset 1px 1px #999999 !important;
    }

    tree#placesList treechildren::-moz-tree-row(hover),
    tree#placeContent treechildren::-moz-tree-row(hover) {
      background-color: transparent !important;
    }

    tree#placesList treechildren::-moz-tree-row(selected),
    tree#placeContent treechildren::-moz-tree-row(selected) {
      background-color: #CCCCFF !important;
    }

    tree#placesList treechildren::-moz-tree-cell-text,
    tree#placeContent treechildren::-moz-tree-cell-text {
      color: #000000 !important;
    }

    tree#placeContent treechildren::-moz-tree-row(multicol, odd) {
      background-color: transparent !important;
    }

Nothing else in the sheet changes: no `window#places` prefix is needed because `placesList` and `placeContent` are IDs unique to the Library window in chrome (the `#metatree`/`#imagetree` prefixing precedent), the `(selected)` row pseudo matches the selected,focus case (`#metatree` recipe), rows, twisties, expander triangles, cell icons, the column headers and the content tree between-column `tree-splitter` grippies stay Firefox's, and the last rule is written only against `tree#placeContent` because a single-column tree (`#placesList`) draws no multicol odd stripe. The rules introduce no hex literal outside `{WHITE, BLACK, GREY, SELECTION }`, which `TestFirefoxChromeShell::test_palette_is_exact` already pins.

Extend the header comment's provenance block with a Library-trees paragraph immediately after the security-panel group-frame paragraph and before the header's closing `*/`: no reference screenshot shows the Firefox Library window; the field face/outlines adapt `widgets/lineedit.svg`, grounded in `macos8.6-screenshots/firstboot_betawiki.png` and pinned by `tests/test_desktoptheme_lineedit.py::TestLineEdit` and `TestLineEditReference`, reusing the landed `#metatree`/`#imagetree` recipes; the transparent rows honour `widgets/listitem.svg`'s no-hover-highlight list reading, pinned by `tests/test_desktoptheme_listitem.py::TestListItem`, and the flat `#CCCCFF` black-text selected row adapts `widgets/viewitem.svg`, pinned by `tests/test_desktoptheme_viewitem.py::TestViewItem` and `tests/test_colorscheme_reference.py::TestReferenceAnchors::test_selection_background`; in the installed Firefox ESR 153.5.1, `chrome/browser/content/browser/places/places.xhtml` defines `tree#placesList` and `tree#placeContent` inside `hbox#placesView`, `chrome/browser/content/browser/places/places.css` strips the stock `.placesTree` appearance, margin and border, `chrome/browser/skin/classic/browser/places/organizer.css` paints `#placesView` `Window`-background and sizes `#placesList`, `chrome/browser/skin/classic/browser/places/organizer-shared.css` floors the pane min-sizes, and `chrome/toolkit/skin/classic/global/tree/tree.css` owns the stock tree paint (the `Field` ground, `ThreeDShadow` border, `-moz-oddtreerow` odd stripes on multicol rows, the `hsla(0, 0%, 50%, 0.15)` hover wash and the `-moz-cellhighlight`/`SelectedItem` selection) with `chrome/browser/skin/classic/browser/places/tree-icons.css` supplying the row icons; the toolbar, search filter, content-tree column headers, downloads rich list and details pane stay Firefox's for the later parts of this series; declaration checks do not establish rendered pixels (platform colour adaptation 2026-10-27).

In `tests/support/firefox_chrome_cases.py`, append after the `#securityPanel > groupbox > label.header` entry a Library comment block adding to `REQUIRED_RULES`: `"#placesList"` and `"#placeContent"` mapping to the five field declarations above (the parser splits the sheet's selector list, the `#metatree`/`#imagetree` precedent), the four row/cell-text selectors (hover transparent, selected `SELECTION`, cell text `BLACK`) built from both `tree#placesList treechildren::…` and `tree#placeContent treechildren::…` forms, and `"tree#placeContent treechildren::-moz-tree-row(multicol, odd)"` mapping to `"background-color: transparent !important"` — reusing `WHITE`, `BLACK`, `GREY` and `SELECTION` beside the existing entries; no entry carries `appearance`, `font`, `margin`, `border-right` or `outline` declarations, and the pseudo-element selectors are assertion-only in `support.selector_matching` exactly as the trees plan's page-info selectors are.

In a new `tests/test_firefox_theme_library.py` module (pattern: `tests/test_firefox_theme_page_info.py`), add `class TestFirefoxLibraryChrome(FirefoxChromeTestCase)` with: `test_library_tree_paint_is_scoped_to_the_places_trees` — using `support.selector_matching.matches`, the `tree#placesList …` selectors match a tree element with id `placesList` (element named `tree`) and never match any tree without that id, the required selector set naming `placesList`/`placeContent` is exactly the ten rules above and every other rule key naming either tree is none; `test_library_tree_provenance` — the comment header names `"No reference screenshot shows the Firefox Library window"`, `"widgets/lineedit.svg"`, `"tests/test_desktoptheme_lineedit.py::TestLineEdit"`, `"TestLineEditReference"`, `"widgets/listitem.svg"`, `"tests/test_desktoptheme_listitem.py::TestListItem"`, `"widgets/viewitem.svg"`, `"tests/test_desktoptheme_viewitem.py::TestViewItem"`, `"test_selection_background"`, `"places.xhtml"`, `"tree#placesList"`, `"tree#placeContent"`, `"places.css"`, `"organizer.css"`, `"organizer-shared.css"`, `"chrome/toolkit/skin/classic/global/tree/tree.css"`, `"tree-icons.css"`, `-moz-oddtreerow`, `-moz-cellhighlight`, `SelectedItem`, and `"platform colour adaptation 2026-10-27"` (pattern: `TestFirefoxPageInfo::test_page_info_tree_provenance`); plus one exact-declaration test looping the required selectors against `REQUIRED_RULES` (the shell module's `test_required_rules` iterates the whole dict and needs no edit).

In `docs/invariants.md`, append one row at the end of the `## firefox` table (after the security-panel row, before `## gtk`): the Library window's two places trees (`tree#placesList`, `tree#placeContent`) are the opaque `#FFFFFF` sunken list field — square 1px `#000000` outline, `#999999` top-left inner shadow, black cell text, rows transparent over the field so no hover wash paints, a selected row flat `#CCCCFF` — with the multicol odd-row stripe floated back onto the field, while the row icons, twisties, column headers, toolbar, search filter, downloads rich list and details pane stay Firefox's. Test column: `tests/test_firefox_theme_library.py::TestFirefoxLibraryChrome` plus `TestFirefoxChromeShell::test_palette_is_exact`. Provenance: no reference screenshot shows the page — the field adapts `widgets/lineedit.svg`/`widgets/viewitem.svg` (a platform colour adaptation), the paint chain facts are read 2026-10-27 from the named installed files, and declaration checks do not establish rendered pixels. `tests/invariants.py` stays green.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/support/firefox_chrome_cases.py`, `tests/test_firefox_theme_library.py` (new), `docs/invariants.md`.

**Acceptance criteria.**
- `userChrome.css` gains exactly the six rule blocks above after the security-groupbox block; every existing selector, declaration and comment is byte-unchanged and no new hex literal appears anywhere in the sheet (`TestFirefoxChromeShell::test_palette_is_exact` passes untouched).
- `TestFirefoxLibraryChrome`'s three tests pass; `TestFirefoxChromeShell::test_required_rules` holds against the extended `REQUIRED_RULES`; `TestFirefoxChromeShell`'s hygiene tests keep green over the extended sheet.
- `docs/invariants.md` gains exactly one `## firefox` row citing the new test class and recording the stay-Firefox surfaces and the platform adaptation; `tests/invariants.py` stays green.
- `make check` passes.

## Done
