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

### Firefox Platinum chrome, part 4 of a Library window series: paint the Library toolbar band as the Platinum toolbar and its Organize/View/Maintenance menu titles as the Platinum menu titles (planned 2026-10-27 by the plan role; independent of the waiting about:preferences part 8 plan — the two touch disjoint sheet and test files (`theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme_library.py` and `tests/support/firefox_chrome_cases.py` versus `theme/firefox/org.macos8.desktop/chrome/userContent.css` and `tests/test_firefox_content_theme.py`), and their `docs/invariants.md` edits touch different rows (the prefs plan only appends its own new row; this plan trims the landed places-trees row's stay-Firefox list and appends its own new row), so either order merges; it is part 4 of the Firefox Library window series, whose parts 1 (the two places trees as the Platinum sunken list field), 2 (the toolbar search box as the Platinum line edit) and 3 (the content tree's column headers as the Platinum raised header buttons) landed 2026-10-27 and whose base recipes this part reuses without touching their rules — the `richlistbox#downloadsListBox` downloads view and the `#detailsPane` bookmark-details fields are later parts that wait behind this one)

**Goal.** The landed parts left the Library window's toolbar band Firefox's and its three dropdown menu titles Firefox's. In `chrome/browser/content/browser/places/places.xhtml` (read 2026-10-27 from the installed Firefox ESR 153.5.1's `browser/omni.ja`), `toolbox#placesToolbox` holds `toolbar#placesToolbar.chromeclass-toolbar` with `toolbarbutton#back-button` and `toolbarbutton#forward-button` (both starting `disabled="true"`) and `menubar#placesMenu nonnative="true"` with the three `menu.menu-iconic` titles `#organizeButton`, `#viewMenu` and `#maintenanceButton`, each opening a `menupopup` (`#organizeButtonPopup`, `#viewMenuPopup`, plus the maintenance popup). `chrome/toolkit/skin/classic/global/toolbar.css` (root `omni.ja`, read 2026-10-27) paints the Linux `toolbar` band `background-color: -moz-headerbar` with `-moz-headerbartext` text (and `-moz-headerbarinactive`/`-moz-headerbarinactivetext` when the window is inactive) — a grey-blue band reading as nothing Platinum under the sheet's white trees. `chrome/browser/skin/classic/browser/places/organizer.css` gives `#placesMenu > menu` `appearance: auto` with `-moz-default-appearance: toolbarbutton`, `min-height: var(--button-min-height)`, `:hover`/`:hover:active`/`[open]` `-moz-buttonhovertext`/`-moz-buttonactivetext` colour changes and the `::after` `arrow-down-12.svg` dropmarker drawn `currentColor`, and `chrome/toolkit/skin/classic/global/menu.css`'s Linux `menubar > menu` block paints the titles transparent with `0.25em 0.5em` padding, a 1px bottom pad and a 3px transparent bottom border, `[open]` boxing an `AccentColor` underline — so at rest the titles hover as unanchored text with no fill, and an open one underlines in the platform accent, nothing Platinum. The two toolbarbuttons need no new rule: at rest their native toolbarbutton paint is transparent over the band and the sheet's landed generic `toolbarbutton:hover:not([disabled="true"])` and `toolbarbutton:hover:active:not([disabled="true"])` bevel rules (the app-toolbar recipe appended when the main-toolbox plan landed) already shape their hover and press, in this same sheet, in the Library window too. Paint the toolbar band as the Platinum toolbar — `#DDDDDD` face, black text, the `1px solid #888888` bottom rule with the `inset 0 -1px #FFFFFF` etched highlight, the byte-recipe the landed `#toolbar-menubar` band rule carries in this same sheet — and the three menu titles as the landed `#toolbar-menubar` menu-title recipe: the `3px 7px 0` padding over Firefox's retained 3px transparent stock bottom border, and `[open]` flat `#CCCCFF` with the border-bottom filled `#CCCCFF`. No reference screenshot shows the Firefox Library window; the band reuses this sheet's reference-grounded toolbar recipe and the menu titles adapt `widgets/menubaritem.svg`'s flat-pressed title (platform colour adaptations). The two back/forward toolbarbuttons' icons, enabled/disabled states and the sheet-generic hover/active bevels, organizer.css's `--button-min-height` and native `toolbarbutton` appearance on the menus, the `::after` dropmarker arrow drawn `currentColor` black, the three `--menuitem-icon` icons, the menu popups (already token-painted by the sheet's landed `menupopup` rule), the window body and the two later surfaces (downloads rich list, details pane) keep their paint.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, after the landed `treecols#placeContentColumns` header rules (currently the sheet's last rules), with a short comment naming the adaptation, append three rules and nothing else:

    /* The Library window's toolbar band and menu titles adapt the sheet's
       toolbar and menubar-title recipes (see the header's provenance
       paragraph). */
    toolbar#placesToolbar {
      background-color: #DDDDDD !important;
      color: #000000 !important;
      border-bottom: 1px solid #888888 !important;
      box-shadow: inset 0 -1px #FFFFFF !important;
    }

    menubar#placesMenu > menu {
      padding: 3px 7px 0 !important;
    }

    menubar#placesMenu > menu[open] {
      background-color: #CCCCFF !important;
      border-bottom-color: #CCCCFF !important;
    }

In `tests/support/firefox_chrome_cases.py`: extend the shared `REQUIRED_RULES` dict after the `"menubar#placesMenu > menu[open]"`-sibling phrase with three new entries placed after the `"treecols#placeContentColumns"` group the current dict ends with (keep the dict's footer comment accurate) — `"toolbar#placesToolbar"`, `"menubar#placesMenu > menu"` and `"menubar#placesMenu > menu[open]"` — each the byte-recipe of the landed `"#toolbar-menubar"`, `"#toolbar-menubar menubar > menu"` and `"#toolbar-menubar menubar > menu[open]"` entries respectively, spelled explicitly with the shared palette constants rather than aliased (yes, the first entry is the same mapping as `"#toolbar-menubar"`).

In `tests/test_firefox_theme_library.py`: add a module constant after `HEADER_HOVER_ARMS` — `TOOLBAR_RULES = ("toolbar#placesToolbar", "menubar#placesMenu > menu", "menubar#placesMenu > menu[open]")` — and add `class TestFirefoxLibraryToolbarChrome(FirefoxChromeTestCase)` after `TestFirefoxLibraryHeaderChrome`, holding: `test_toolbar_and_menubar_rules_match_the_required_rules` — each of the three arms equals its `REQUIRED_RULES` entry byte-for-byte and every declaration ends `!important`; `test_toolbar_band_is_scoped_to_the_library_toolbar` — via `support.selector_matching`'s `element`/`matches`, `toolbar#placesToolbar` matches `element("toolbar", "placesToolbar")` and never `element("toolbar", "nav-bar")`, and `menubar#placesMenu > menu` matches `element("menu", "organizeButton", parent=element("menubar", "placesMenu", parent=element("toolbar", "placesToolbar")))` (and the same with the other two ids, one with `attrs={"open": "true"}` matching the open arm and without matching only the padding arm) but never a `menu` whose parent `menubar` lacks the `placesMenu` id (the `#toolbar-menubar` menubar's titles included), and `test_header_names_toolbar_provenance` (pattern: `TestFirefoxLibraryHeaderChrome`'s final test) asserting the header names the strings below. Extend the assertions of `TestFirefoxLibraryChrome::test_library_tree_provenance` and `TestFirefoxLibrarySearchChrome::test_header_names_search_provenance` for the two narrowed sentences below.

The header comment gains exactly one paragraph, between the column-headers paragraph and the closing `*/`, naming: no reference screenshot shows the Firefox Library window; the toolbar band reuses this sheet's landed `#toolbar-menubar` recipe (`#DDDDDD` face, black text, the `#888888` bottom rule and the `inset 0 -1px #FFFFFF` etched highlight), grounded in the reference toolbars and pinned by `tests/test_firefox_theme_shell.py::TestFirefoxChromeShell::test_required_rules`; the open menu title's flat `#CCCCFF` fill comes from `widgets/menubaritem.svg`'s pressed slices with no hover highlight (platform colour adaptation 2026-10-27), pinned by `tests/test_desktoptheme_menubaritem.py::TestMenuBarItem.test_menubaritem_pressed_is_flat_selection_colour` and `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_selection_background`; the anatomy is read 2026-10-27 from the installed Firefox ESR 153.5.1 — `places.xhtml`'s `toolbox#placesToolbox` with `toolbar#placesToolbar.chromeclass-toolbar` holding `toolbarbutton#back-button` and `toolbarbutton#forward-button` (both starting `disabled="true"`) and `menubar#placesMenu nonnative="true"` with the three `menu.menu-iconic` titles `#organizeButton`, `#viewMenu` and `#maintenanceButton`; `chrome/toolkit/skin/classic/global/toolbar.css` paints the Linux `toolbar` band `-moz-headerbar`/`-moz-headerbartext` with the `-moz-headerbarinactive` inactive pair; `organizer.css` gives `#placesMenu > menu` `appearance: auto` with `-moz-default-appearance: toolbarbutton`, `min-height: var(--button-min-height)`, the `-moz-buttonhovertext`/`-moz-buttonactivetext` hover/open colour changes and the `::after` `arrow-down-12.svg` dropmarker drawn `currentColor`; `menu.css`'s Linux `menubar > menu` block owns the transparent rest paint, the `0.25em 0.5em`/1px bottom padding the rules override and the 3px transparent bottom border they keep, with the `[open]` `AccentColor` underline they replace; and the intentionally unscoped surfaces — the two back/forward toolbarbuttons (already shaped by the sheet's generic `toolbarbutton:hover`/`:hover:active` bevel rules, rest state Firefox's), organizer.css's `--button-min-height` and native appearance on the menus, the `::after` dropmarker, the three `--menuitem-icon` icons, the popup lists (the landed `menupopup` token rule), the window body, the downloads rich list and the details pane; plus that only the padding is overridden on the titles, with a zero bottom pad, so the retained stock border completes the 3px bottom margin and stays the open title's `#CCCCFF` underline; and that declaration checks do not establish rendered pixels.

In the header's two earlier paragraphs, narrow the stay-Firefox sentences: the trees paragraph's sentence becomes "The toolbar's back and forward buttons, downloads rich list and details pane stay Firefox's for the later parts of this series (the content-tree column headers, the toolbar's search filter and the toolbar's menu titles have their own paragraphs below)." and the search paragraph's sentence becomes "The toolbar's back and forward buttons, the downloads rich list and the details pane stay Firefox's for the later parts of this series." — keeping the asserted substrings `The toolbar's back and forward buttons` and `downloads rich list and details pane stay Firefox's` contiguous, and refreshing `test_library_tree_provenance`'s corresponding assertions.

In `docs/invariants.md`, in the `## firefox` table: trim the landed places-trees row's stay-Firefox list from "the row icons, twisties, toolbar buttons and the Organize/View/Maintenance menus, downloads rich list and details pane stay Firefox's" to "the row icons, twisties, the toolbar's back and forward buttons, downloads rich list and details pane stay Firefox's" (the series precedent when a part takes over a surface), and append a new row immediately after the column-headers row: the Library window's toolbar band `toolbar#placesToolbar` is the Platinum toolbar — `#DDDDDD` face with black text, a `1px solid #888888` bottom rule and the `inset 0 -1px #FFFFFF` etched highlight — and its Organize/View/Maintenance titles (`menubar#placesMenu > menu`) take the Platinum menu-title padding with an open title flat `#CCCCFF` and the stock bottom border filled the same, while the back/forward toolbarbuttons' icons and sheet-generic hover bevels, the menus' `min-height` and native appearance, the `::after` dropmarker, the three icons, the popup lists, the window body, the downloads rich list and the details pane stay Firefox's; the row's provenance records the `#toolbar-menubar`/`menubaritem.svg` reuse and the `places.xhtml`/`toolbar.css`/`organizer.css`/`menu.css` chain read 2026-10-27 with `TestFirefoxLibraryToolbarChrome` plus `TestFirefoxChromeShell::test_palette_is_exact` in the test column. `tests/invariants.py` is structural and stays green.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/support/firefox_chrome_cases.py`, `tests/test_firefox_theme_library.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The sheet gains exactly the three rules above after the `treecols#placeContentColumns` header rules, introducing no hex outside `{#DDDDDD, #000000, #888888, #FFFFFF, #CCCCFF}` (all pre-existing sheet members); `TestFirefoxChromeShell::test_palette_is_exact` passes untouched, and no landed rule's text changes other than the narrowed header sentences.
- `TestFirefoxLibraryToolbarChrome`'s tests pass; the three new `REQUIRED_RULES` entries make `TestFirefoxChromeShell::test_required_rules` and every other chrome suite's per-selector tests pass without edits (no incumbent test asserts the sheet rule count, and `TestFirefoxLibraryChrome`'s named-places-tree filter excludes all three new selectors); every other `tests/test_firefox_theme_library.py` class (trees, search, headers) keeps green against unchanged rule text.
- The header gains exactly one paragraph between the column-headers paragraph and `*/` carrying the provenance strings above (pinned by `test_header_names_toolbar_provenance`); the two earlier paragraphs' sentences are narrowed exactly as specified, with the asserted substrings contiguous.
- `docs/invariants.md` trims the places-trees row's stay-Firefox list as specified and gains the toolbar-and-menu-titles row after the column-headers row, with `TestFirefoxLibraryToolbarChrome` named in its test column and no other row's wording changed; `tests/invariants.py` stays green.
- `make check` passes.

### Firefox Platinum chrome: Library window series, part 5/6: paint the downloads view's rich list as the Platinum sunken list field and its Clear Downloads button as the Platinum push button (planned 2026-10-27 by the plan role; "requires part 4/6 landed" — this part appends after and edits the tail of part 4's toolbar-band paint and narrows the stock stay-Firefox sentences that part 4 rewrites; parts 1 (the two places trees), 2 (the toolbar search box) and 3 (the content tree's column headers) landed 2026-10-27 and this part reuses their base recipes without touching their rules, and the `#detailsPane` bookmark-details fields with their expander-up/down buttons are the last part that waits behind this one)

**Goal.** After the landed parts, the Library window's Downloads view is still Firefox's: the list field, its rows and the toolbar's Clear Downloads button read as the platform skin, not Platinum. In `chrome/browser/content/browser/places/places.xhtml` (read 2026-10-27 from the installed Firefox ESR 153.5.1's `browser/omni.ja`), `vbox#placesViewsBox` holds `tree#placeContent`'s sibling `richlistbox#downloadsListBox` (`class="allDownloadsListBox"`, `seltype="multiple"`, starting `hidden="true"`, row context `#downloadsContextMenu`), and `toolbar#placesToolbar` holds `toolbarbutton#clearDownloadsButton.tabbable` bound to `downloadsCmd_clearDownloads` beside `#libraryToolbarSpacer`. The id `#downloadsListBox` is not Library-unique: `browser.xhtml`'s `#downloadsPanel` carries the same id and its landed userChrome rules scoped through `#downloadsPanel`, and `contentAreaDownloadsView.xhtml`'s copy is painted by the landed `about:downloads` userContent rules under `@-moz-document url("about:downloads")` — so the Library rules must scope through Library-only ancestors (`#placesViewsBox`, `toolbar#placesToolbar`). `chrome/toolkit/skin/classic/global/richlistbox.css` paints `richlistbox` with `appearance: auto`/`-moz-default-appearance: listbox`, `background-color: Field`, `color: FieldText`, `border: 1px solid ThreeDShadow` and `margin: 2px 4px`, and paints `richlistitem[selected="true"]` `-moz-cellhighlight`/`-moz-cellhighlighttext` (or `SelectedItem`/`SelectedItemText` when the box is focused) and a multiple-selection focus `outline: var(--default-focusring)` in `SelectedItem`; `chrome/browser/skin/classic/browser/downloads/allDownloadsView.css` (imported by `places.xhtml`) sets `#downloadsListBox > richlistitem { min-height: 4.5em }` and, with `allDownloadsView.inc.css`, paints `--downloads-item-*` geometry and the per-row `.downloadButton` action buttons, and paints no row hover background. Paint the list as the sheet's Platinum sunken list field — `appearance: none`, `#FFFFFF` face, black text, square `1px solid #000000` outline and the `inset 1px #999999` top-left shadow, the byte-recipe the landed `#placesList`/`#placeContent` trees and the landed `#contentAreaDownloadsView #downloadsListBox:not(:empty)` userContent rule for the same widget class carry — with square rows, a flat `#CCCCFF` selected row in black text, no hover rule (the browser skin paints none and Chrome OS 8 lists have no hover: `widgets/listitem.svg` ships no hover state), and the toolbar's Clear Downloads button as the landed userChrome push button — `#DDDDDD` face, black text, square `1px solid #000000` outline and the ``inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA`` raised bevel, flat `#CCCCFF` on hover, disabled paint left to Firefox. No reference screenshot shows the Firefox Library window; the list reuses the reference-grounded line-edit field, the button reuses the reference-grounded push button (platform colour adaptations). The rows' own geometry and contents keep Firefox's: the 4.5em min-height, the `.downloadTypeIcon` 32px type icon, the `.downloadTarget`/`.downloadDetails` text layout and progress meters, the per-row `.downloadButton` action buttons (the landed about:downloads userContent rule chose the same for the twin rich list), the `richlistbox` `margin: 2px 4px` and the `--default-focusring` current-item outline.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, after the landed `menubar#placesMenu > menu[open]` title rule (part 4's appended tail, currently the sheet's last rules), with short comments naming the adaptations, append five rules and nothing else:

    /* The Library window's downloads list adapts the sheet's sunken
       list-field and row recipes (see the header's provenance
       paragraph); the browser skin paints no row hover, so there is
       no hover rule. */
    #placesViewsBox richlistbox#downloadsListBox {
      appearance: none !important;
      background-color: #FFFFFF !important;
      color: #000000 !important;
      border: 1px solid #000000 !important;
      border-radius: 0 !important;
      box-shadow: inset 1px 1px #999999 !important;
    }

    #placesViewsBox richlistbox#downloadsListBox > richlistitem {
      border-radius: 0 !important;
    }

    #placesViewsBox richlistbox#downloadsListBox > richlistitem[selected] {
      background-color: #CCCCFF !important;
      color: #000000 !important;
    }

    /* The Library's Clear Downloads button adapts the sheet's push
       button; disabled ones keep Firefox's paint. */
    toolbar#placesToolbar toolbarbutton#clearDownloadsButton:not([disabled]) {
      background-color: #DDDDDD !important;
      color: #000000 !important;
      border: 1px solid #000000 !important;
      border-radius: 0 !important;
      box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA !important;
    }

    toolbar#placesToolbar toolbarbutton#clearDownloadsButton:not([disabled]):hover {
      background-color: #CCCCFF !important;
      color: #000000 !important;
      box-shadow: none !important;
    }

In `tests/support/firefox_chrome_cases.py`: extend the shared `REQUIRED_RULES` dict after the three toolbar entries part 4 lands (keep the dict's footer comment accurate), in this order — `"#placesViewsBox richlistbox#downloadsListBox"` (five declarations above through the shared palette constants, spelled explicitly rather than aliased: at rest it is the same mapping as `"#placesList"` plus `appearance`), `"#placesViewsBox richlistbox#downloadsListBox > richlistitem"` (`{"border-radius": "0 !important"}`, the same mapping as the landed `#downloadsPanel` row entry), `"#placesViewsBox richlistbox#downloadsListBox > richlistitem[selected]"` (the byte-recipe of the landed `#downloadsPanel` selected-row entry), `"toolbar#placesToolbar toolbarbutton#clearDownloadsButton:not([disabled])"` and its `:hover` arm (the byte-recipes of the landed `#downloadsPanel .downloadsPanelFooterButton:not([disabled])` and its hover arm) — each spelled explicitly with the shared constants.

In `tests/test_firefox_theme_library.py`: add module constants after part 4's `TOOLBAR_RULES` — `DOWNLOADS_RULES = ("#placesViewsBox richlistbox#downloadsListBox", "#placesViewsBox richlistbox#downloadsListBox > richlistitem", "#placesViewsBox richlistbox#downloadsListBox > richlistitem[selected]")` and `CLEAR_BUTTON_RULES = ("toolbar#placesToolbar toolbarbutton#clearDownloadsButton:not([disabled])", "toolbar#placesToolbar toolbarbutton#clearDownloadsButton:not([disabled]):hover")` — and add `class TestFirefoxLibraryDownloadsChrome(FirefoxChromeTestCase)` after part 4's `TestFirefoxLibraryToolbarChrome`, holding:

- `test_downloads_rules_match_the_required_rules` — each of the five arms equals its `REQUIRED_RULES` entry byte-for-byte and every declaration ends `!important`;
- `test_downloads_list_rules_scoped_to_the_places_views_box` — via `support.selector_matching`'s `element`/`matches`: the face arm matches `element("richlistbox", "downloadsListBox", parent=element("vbox", "placesViewsBox", parent=element("vbox", "contentView")))` and never the same `richlistbox` under `element("vbox", None, parent=element("panelview", "downloadsPanel-mainView"))` (the `#downloadsPanel` list) nor under a `#contentAreaDownloadsView` ancestor; the row arm matches a plain `richlistitem` child and the selected arm matches it only with `attrs={"selected": "true"}`; and the sheet's whole set of `downloadsListBox`-naming rules is exactly the landed three `#downloadsPanel` arms plus `DOWNLOADS_RULES`;
- `test_clear_button_rules_scoped_to_the_library_toolbar` — the arms match `element("toolbarbutton", "clearDownloadsButton", parent=element("toolbar", "placesToolbar"))` and never the same button under another toolbar, never `element("toolbarbutton", "back-button", parent=element("toolbar", "placesToolbar"))` or any other toolbarbutton in that toolbar, and the hover arm only with `hover=True`; and the sheet's whole set of `clearDownloadsButton`-naming rules is exactly `CLEAR_BUTTON_RULES`, while the whole set of `placesToolbar`-naming rules is exactly `("toolbar#placesToolbar",) + CLEAR_BUTTON_RULES`;
- `test_header_names_downloads_provenance` (pattern: `TestFirefoxLibraryToolbarChrome`'s final test) asserting the header names the strings below.

Extend the assertions of `test_library_tree_provenance` and `test_header_names_search_provenance` for the two narrowed sentences below, in the landed `TestFirefoxLibraryToolbarChrome::test_header_names_toolbar_provenance` refresh the fragments it names from the landed toolbar paragraph (whose stay-Firefox list drops the downloads rich list as the narrowed sentences do), and leave every other class's tests to pass over unchanged rule text.

The header comment gains exactly one paragraph, between the toolbar paragraph and the closing `*/`, naming: no reference screenshot shows the Firefox Library window; the downloads list reuses this sheet's landed `#placesList`/`#placeContent` sunken list-field recipe (`#FFFFFF` face, black text, square `1px solid #000000` outline, `inset 1px 1px #999999` shadow) and the landed `#contentAreaDownloadsView #downloadsListBox:not(:empty)` userContent rule for the same widget class, grounded in `widgets/lineedit.svg` and `widgets/viewitem.svg` and pinned by `tests/test_desktoptheme_lineedit.py::TestLineEdit`, `tests/test_desktoptheme_viewitem.py::TestViewItem` and `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_selection_background`; the Clear Downloads button reuses the landed `#downloadsPanel` push-button recipe grounded in `widgets/button.svg`, pinned by `tests/test_desktoptheme_button.py::TestButton` and `tests/test_desktoptheme_button_reference.py::TestButtonReference` (platform colour adaptation 2026-10-27); no row hover rule exists because the browser skin paints none and `widgets/listitem.svg` ships no hover state; the `#downloadsListBox` id also occurring on `#downloadsPanel` and on the content-area view is why the rules scope through `#placesViewsBox` and `toolbar#placesToolbar`; the anatomy is read 2026-10-27 from the installed Firefox ESR 153.5.1 — `places.xhtml`'s `vbox#placesViewsBox` holding `richlistbox#downloadsListBox.allDownloadsListBox` (`seltype="multiple"`, starting `hidden="true"`, rows built by the downloads commands context `#downloadsContextMenu`) and `toolbar#placesToolbar` holding `toolbarbutton#clearDownloadsButton.tabbable` bound to `downloadsCmd_clearDownloads` beside `#libraryToolbarSpacer`; `chrome/toolkit/skin/classic/global/richlistbox.css` paints the listbox `appearance: auto`/`Field`/`FieldText`/`1px solid ThreeDShadow`/`margin: 2px 4px` with `richlistitem[selected="true"]` `-moz-cellhighlight`/`SelectedItem` and the `--default-focusring` multiple-selection outline; `chrome/browser/skin/classic/browser/downloads/allDownloadsView.css` and `allDownloadsView.inc.css` own the rows' `min-height: 4.5em`, the `.downloadTypeIcon`/`.downloadTarget`/`.downloadDetails` layout and the `.downloadButton` action buttons; and the intentionally unchanged paint — the rows' geometry and per-row action buttons plus progress meters (the landed about:downloads rule's same choice), the `richlistbox` `margin: 2px 4px`, the selected-row and multiple-selection focus-ring states Firefox paints beyond the flat `#CCCCFF`, `#libraryToolbarSpacer`, the `#downloadsPanel` and content-area copies (their own scoped rules) — plus that declaration checks do not establish rendered pixels.

In the header's two earlier paragraphs, narrow the stay-Firefox sentences the landed text carries to drop the downloads rich list: the trees paragraph's sentence becomes "The toolbar's back and forward buttons and the details pane stay Firefox's for the later parts of this series (the content-tree column headers, the toolbar's search filter and the toolbar's menu titles have their own paragraphs below)." and the search paragraph's sentence becomes "The toolbar's back and forward buttons and the details pane stay Firefox's for the later parts of this series." — keeping the asserted substrings `The toolbar's back and forward buttons and the details pane stay Firefox's` contiguous.

In `docs/invariants.md`, in the `## firefox` table: trim the landed places-trees row's stay-Firefox list from "the row icons, twisties, the toolbar's back and forward buttons, downloads rich list and details pane stay Firefox's" to "the row icons, twisties, the toolbar's back and forward buttons and the details pane stay Firefox's", trim part 4's landed toolbar row's stay-Firefox list to drop "the downloads rich list" the same way, and append a new row immediately after the toolbar row: the Library window's downloads view (`#placesViewsBox richlistbox#downloadsListBox`) is the opaque `#FFFFFF` Platinum sunken list field — square `1px #000000` outline, `#999999` top-left inner shadow, black text, `appearance: none`, square rows and a flat `#CCCCFF` selected row — and `toolbar#placesToolbar`'s enabled Clear Downloads button (`toolbarbutton#clearDownloadsButton`) takes the Platinum push button (`#DDDDDD` face, black outline, the ``inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA`` raised bevel, flat `#CCCCFF` hover, disabled paint Firefox's), with no row hover rule, the browser skin paints no row hover, because the scrollbar skin paints none, while the rows' 4.5em min-height, type icon, target/details layout, progress meters and per-row `.downloadButton` action buttons, the `richlistbox` margins and the multiple-selection focus outline, `#libraryToolbarSpacer`, and the `#downloadsPanel` and content-area copies stay Firefox's; the row's provenance records the `#placesList`/`#contentAreaDownloadsView`/`#downloadsPanel` recipe reuse and the `places.xhtml`/`allDownloadsView.css`/`richlistbox.css` chain read 2026-10-27 with `TestFirefoxLibraryDownloadsChrome` plus `TestFirefoxChromeShell::test_palette_is_exact` in the test column. `tests/invariants.py` is structural and stays green.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/support/firefox_chrome_cases.py`, `tests/test_firefox_theme_library.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The sheet gains exactly the five rules above after the `menubar#placesMenu > menu[open]` title rule, introducing no hex outside the pre-existing sheet member set (`{#DDDDDD, #000000, #888888, #999999, #FFFFFF, #AAAAAA, #CCCCFF, #EEEEEE}` and the palette the header's provenance already names); `TestFirefoxChromeShell::test_palette_is_exact` passes untouched, and no landed rule's text changes other than the narrowed header sentences.
- `TestFirefoxLibraryDownloadsChrome`'s tests pass; the five new `REQUIRED_RULES` entries make `TestFirefoxChromeShell::test_required_rules` pass without edits (order-insensitive per its `for selector, expected in REQUIRED_RULES.items()` loop); every other `tests/test_firefox_theme_library.py` class (trees, search, headers, toolbar) keeps green against unchanged rule text with the refreshed provenance fragments, and `TestFirefoxLibraryChrome`'s named-places-tree filter excludes all five new selectors.
- The header gains exactly one paragraph between the toolbar paragraph and `*/` carrying the provenance strings above (pinned by `test_header_names_downloads_provenance`); the two earlier paragraphs' sentences are narrowed exactly as specified, with the asserted substrings contiguous, and the toolbar provenance test's corresponding fragments are refreshed in the same edit.
- `docs/invariants.md` trims the two stay-Firefox lists as specified and gains the downloads-list row after part 4's toolbar row, with `TestFirefoxLibraryDownloadsChrome` named in its test column and no other row's wording changed; `tests/invariants.py` stays green.
- `make check` passes.

## Done
