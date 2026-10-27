# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; landed-plan facts re-trimmed 2026-10-23
by the clean role; validation scope clarified 2026-10-25 by the steward role; Firefox artifact
and content-surface status updated 2026-10-26 by the steward role):** The
initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (twenty-eight widget SVGs under
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
sheet under `theme/firefox/` (its `userChrome.css` copied and its profile preference written
only by the opt-in `install-firefox` target); and the render and fidelity tooling.
The live reference-comparison gate in `tests/test_render_surface.py` checks Aurorae window-chrome
regions when its render prerequisites are available (README.md, "Fidelity checking").
Firefox's `tests/test_firefox_theme.py::TestFirefoxChrome` checks stylesheet declarations;
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

### Firefox Platinum content: paint about:config's preference table, search field and buttons as Platinum controls (planned 2026-10-26 by the plan role; independent of the waiting notification-doorhanger plan)

**Goal.** Make Firefox's `about:config` page read as Platinum: the preference table (`#prefs:not(:empty)`) becomes a white square field with black text, a 1px black outline and the sunken `#999999` top-left shadow; its alternate rows are `#EEEEEE`; its stock hover wash is removed, so a hovered odd row stays `#EEEEEE` and a hovered even row keeps the field's white, both with black text. The search field (`#about-config-search`) becomes the white square sunken field, and the Show All ghost button (`#show-all`) and the warning page's primary button (`#warningButton`) become square `#DDDDDD` push buttons with a black outline and the reference's white/`#AAAAAA` raised bevel, an enabled hovered one being flat `#CCCCFF` with black text and no bevel. The warning page's copy, checkbox and background illustration, the help text, the Show Only Modified checkbox, the rows' name/value text and their `has-user-value`, `locked` and `deleted` styling, the per-row add/edit/save/reset buttons and the page background and toolbar band stay Firefox's.

**Grounding.** No reference screenshot shows Firefox's `about:config` page, so the paint adapts this theme's Platinum controls (platform colour adaptation 2026-10-26). The table field and search field adapt the reference-grounded `widgets/lineedit.svg` (`tests/test_desktoptheme_lineedit.py::TestLineEdit`), and the alternate row `#EEEEEE` is the pinned `[Colors:View] BackgroundAlternate` trough (`tests/test_colorscheme_reference.py::TestReferenceAnchors::test_view_background_alternate`). The rows adapt `widgets/listitem.svg` (`tests/test_desktoptheme_listitem.py::TestListItem`), which has no hover highlight, and the flat `#CCCCFF` hover adapts `widgets/viewitem.svg` (`tests/test_desktoptheme_viewitem.py::TestViewItem`, `tests/test_colorscheme_reference.py::TestReferenceAnchors::test_selection_background`). The push buttons adapt `widgets/button.svg` (`tests/test_desktoptheme_button.py::TestButton`) and its reference `#AAAAAA` bevel (`tests/test_desktoptheme_button_reference.py::TestButtonReference`).

In the installed Firefox ESR 153.5.1, `chrome/toolkit/content/global/aboutconfig/aboutconfig.html` defines `#warningButton` (`.primary`), `#showWarningNextTime`, `#about-config-search`, `#about-config-show-only-modified`, `table#prefs` and `#show-all` (`.ghost-button`). `chrome/toolkit/content/global/aboutconfig/aboutconfig.js`'s `PrefRow` builds each row as a `tr` with a `th` name cell and `td.cell-value`/`td.cell-edit`/`td.cell-reset`, `refreshClass` adds the `odd`, `has-user-value`, `locked` and `deleted` classes, and `loadPrefs` disables the `info-pages.css` sheet (`[...document.styleSheets].find(s => s.title == "infop").disabled = true;`), so the main page's table is painted by `aboutconfig.css` and `common-shared.css`, not the warning page's `info-pages.css`. `chrome/toolkit/content/global/aboutconfig/aboutconfig.css` paints `#prefs`, `#prefs > tr.odd` and `#prefs > tr:hover`; `chrome/toolkit/skin/classic/global/in-content/common-shared.css` gives `html|input[type="text"]` its rounded `--border-color`/`--background-color-box` face and paints `button`/`button.primary` from the `--button-*` tokens and `.ghost-button` transparent; `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` declares those tokens. A headless run of this ESR with a temporary profile whose `userContent.css` painted `about:config`'s body red rendered the page red, and a second run with the candidate block below and `browser.aboutConfig.showWarning=false` rendered the search field's square black border and the Show All button's `#DDDDDD` face. Declaration checks do not establish rendered row pixels.

**Approach.** Append this block at the very end of `theme/firefox/org.macos8.desktop/chrome/userContent.css`, after the existing `about:downloads` block, with a short comment naming the adaptation:

```css
@-moz-document url("about:config") {
  #prefs:not(:empty) {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #000000 !important;
    border-radius: 0 !important;
    box-shadow: inset 1px 1px #999999 !important;
  }

  #prefs > tr.odd {
    background-color: #EEEEEE !important;
  }

  #prefs > tr:hover {
    background-color: transparent !important;
    color: #000000 !important;
  }

  #prefs > tr.odd:hover {
    background-color: #EEEEEE !important;
  }

  #about-config-search {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #000000 !important;
    border-radius: 0 !important;
    box-shadow: inset 1px 1px #999999 !important;
  }

  #show-all,
  #warningButton {
    background-color: #DDDDDD !important;
    color: #000000 !important;
    border: 1px solid #000000 !important;
    border-radius: 0 !important;
    box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA !important;
  }

  #show-all:hover:not(:disabled),
  #warningButton:hover:not(:disabled) {
    background-color: #CCCCFF !important;
    color: #000000 !important;
    box-shadow: none !important;
  }
}
```

Use `#prefs:not(:empty)` so the initial page, whose table has no rows, draws no field line; leave the empty table, the warning page's checkbox and copy, the Show Only Modified checkbox, the `#toolbar` band, `.config-background`, `.config-help-text` and the per-row cell buttons alone. Do not add an `outline` rule: the search field keeps Firefox's `:focus` outline and the buttons keep their `:focus-visible` ring. Do not change the existing `about:downloads` block or `userChrome.css`. In the `userContent.css` header comment, append an about:config provenance paragraph after the downloads provenance and before the closing `*/`: no reference shows Firefox's about:config; the field and rows adapt `widgets/lineedit.svg`, `widgets/listitem.svg` and the pinned `#EEEEEE`/`#CCCCFF` anchors, and the buttons adapt `widgets/button.svg` and its `#AAAAAA` bevel; `aboutconfig.html` defines the ids, `aboutconfig.js` builds the rows and disables the `infop` sheet, `aboutconfig.css` and `common-shared.css` own the stock paint; a headless run reached the page; declaration checks do not establish rendered row pixels.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userContent.css`, `tests/test_firefox_content_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `userContent.css` contains exactly the two `@-moz-document` blocks: the existing `about:downloads` block byte-unchanged and the new `about:config` block with the seven rules above (nine parsed selectors after the grouped selectors are split). `test_palette_is_exact` in `tests/test_firefox_content_theme.py` expects the expanded set `{WHITE, BLACK, GREY, SELECTION, FACE, TROUGH, BUTTON_SHADOW}` imported from `support.platinum_palette`.
- `tests/test_firefox_content_theme.py` gains a general `@-moz-document url("...")` reader that returns the block bodies by URL. `TestFirefoxContentTheme` parses only the `about:downloads` body, keeps its three-rule assertions, and renames `test_sheet_is_one_about_downloads_at_rule` to `test_sheet_has_the_downloads_and_config_at_rules` and `test_parsed_rules_are_exactly_the_three_list_rules` to `test_downloads_rules_are_exactly_the_three_list_rules`; the shared marker, palette, no-`@import`/Adwaita, no-universal-selector and downloads provenance tests stay. New `TestFirefoxConfigTheme` parses the `about:config` body and asserts: `test_required_rules` pins the nine selectors' exact declarations; `test_parsed_rules_are_exactly_the_config_rules` pins the selector set and order; `test_config_rules_are_scoped_to_the_prefs_table_and_controls` requires every selector to start with `#prefs`, `#about-config-search`, `#show-all` or `#warningButton` and names none of `.config-background`, `.config-help-text`, `#about-config-show-only-modified`, `.cell-edit`, `.cell-reset` or `.button-`; `test_config_selector_guards_the_empty_table` requires `:not(:empty)` on `#prefs`; `test_header_names_config_provenance` requires the header to name `"No reference shows Firefox's about:config"`, `"widgets/lineedit.svg"`, `"widgets/listitem.svg"`, `"widgets/button.svg"`, `"tests/test_desktoptheme_button_reference.py::TestButtonReference"`, `"test_view_background_alternate"`, `"test_selection_background"`, `"aboutconfig.html"`, `"aboutconfig.js"`, `"aboutconfig.css"`, `"common-shared.css"`, `"#prefs"`, `"#about-config-search"`, `"#show-all"`, `"#warningButton"` and `"platform colour adaptation 2026-10-26"`.
- `docs/invariants.md` gains a row inserted after the existing `about:downloads` content row and before `## gtk`: the `about:config` preference table (`#prefs:not(:empty)`) is a white square field with black text, a 1px black outline and the sunken `#999999` top-left shadow, its alternate rows are `#EEEEEE`, and a hovered odd row stays `#EEEEEE` while a hovered even row keeps the field's white, both with black text; the search field is the same white sunken field; Show All and the warning page's primary button are square `#DDDDDD` controls with a black outline and the reference's white/`#AAAAAA` raised bevel, an enabled hovered one being flat `#CCCCFF` with black text and no bevel; the warning copy, checkbox, background illustration, help text, Show Only Modified checkbox, row `has-user-value`/`locked`/`deleted` styling, per-row cell buttons and page background stay Firefox's. Its test column names the new config tests and `test_palette_is_exact`, and its provenance records the missing about:config reference, the `widgets/lineedit.svg`, `widgets/listitem.svg` and `widgets/button.svg` anchors, the installed ESR 153.5.1 files and the `infop`-sheet disabling, the headless reach run, and that declaration checks do not establish rendered row pixels. The existing downloads row's test column is updated for the two renamed tests. `tests/invariants.py` stays green.
- Repeat the headless reach check against the edited sheet with `browser.aboutConfig.showWarning=false` and record what it renders; declaration checks do not establish rendered row pixels.
- `make check` passes, and the existing `userChrome.css` rules, the Firefox install and their tests keep their declarations and scope.

### Firefox Platinum chrome: paint the downloads panel's footer and action buttons as Platinum push buttons (planned 2026-10-26 by the plan role; independent of the waiting about:config content plan)

**Goal.** Make the downloads panel's buttons read as Platinum: in `#downloadsPanel`, the Show All Downloads footer button (`#downloadsHistory`), each row's action button (`button.downloadButton`), and the blocked and private subviews' footer buttons (`html:moz-button-group#downloadsPanel-blockedSubview-buttons .footer-button` and the two `.footer-button`s in `#downloadsPanel-privateBrowsing`) become square `#DDDDDD` push-button faces with a 1px black outline and the reference's white/`#AAAAAA` raised bevel; an enabled hovered one is flat `#CCCCFF` with black text and no bevel. Disabled buttons keep Firefox's disabled paint, and the panel rows, `.downloadMainArea`, the downloads summary, the panel header, the subview copy and the content-area downloads list stay as they are.

**Grounding.** No reference screenshot shows Firefox's downloads panel buttons, so the paint adapts this theme's Platinum controls (platform colour adaptation 2026-10-26). The `#DDDDDD` face, 1px black outline and white/`#AAAAAA` raised bevel adapt the reference-grounded `widgets/button.svg` (`tests/test_desktoptheme_button.py::TestButton`, `tests/test_desktoptheme_button_reference.py::TestButtonReference`), and the flat `#CCCCFF` hover adapts `widgets/viewitem.svg` (`tests/test_desktoptheme_viewitem.py::TestViewItem`, `tests/test_colorscheme_reference.py::TestReferenceAnchors::test_selection_background`). The landed downloads-panel row plan deliberately left these buttons to Firefox, so this entry completes that panel.

In the installed Firefox ESR 153.5.1, `browser/omni.ja` `chrome/browser/content/browser/browser.xhtml` defines `<panel id="downloadsPanel" type="arrow">` with `<vbox id="downloadsFooter">`, `#downloadsFooterButtons` and `<button id="downloadsHistory" class="downloadsPanelFooterButton subviewbutton panel-subview-footer-button toolbarbutton-1">`; its `#downloadsPanel-blockedSubview` holds `<html:moz-button-group id="downloadsPanel-blockedSubview-buttons" class="panel-footer">` with `button#downloadsPanel-blockedSubview-unblockButton.footer-button` and `button#downloadsPanel-blockedSubview-deleteButton.footer-button` (`default`), and `#downloadsPanel-privateBrowsing` holds `.footer-button.secondary` and `.footer-button.primary` (`default`). `moz-src/browser/components/downloads/DownloadsViewUI.sys.mjs` builds each row's `button.downloadButton`. `chrome/browser/skin/classic/browser/downloads/downloads.inc.css` gives `.downloadButton` an `appearance: none`, 32px box, transparent border, ghost background and `--border-radius-small`, and paints `.downloadButton:hover:not(:active)` and `.downloadsPanelFooterButton:hover` from the ghost hover tokens; `chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css` gives `.subviewbutton` its `appearance: none`, transparent background and `--panel-menuitem-border-radius`; and `chrome/toolkit/skin/classic/global/global-shared.css` paints `.footer-button` from the `--button-*` tokens. The sheet has no rule targeting `.downloadButton`, `.downloadsPanelFooterButton` or a `.footer-button` inside `#downloadsPanel`.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, insert these two grouped rules immediately after the existing `#downloadsPanel #downloadsListBox > richlistitem[selected]` rule and before the `panel[type="arrow"]` rule, with a short comment naming the adaptation:

```css
/* The downloads panel's footer, subview and per-row action buttons adapt the
   desktop theme's push button; disabled ones keep Firefox's paint. */
#downloadsPanel .downloadsPanelFooterButton:not([disabled]),
#downloadsPanel .downloadButton:not([disabled]),
#downloadsPanel .footer-button:not([disabled]) {
  background-color: #DDDDDD !important;
  color: #000000 !important;
  border: 1px solid #000000 !important;
  border-radius: 0 !important;
  box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA !important;
}

#downloadsPanel .downloadsPanelFooterButton:not([disabled]):hover,
#downloadsPanel .downloadButton:not([disabled]):hover,
#downloadsPanel .footer-button:not([disabled]):hover {
  background-color: #CCCCFF !important;
  color: #000000 !important;
  box-shadow: none !important;
}
```

Use `:not([disabled])` on both rules so a disabled button keeps Firefox's disabled background and text; keep the stock button geometry, padding, margins, icon and font, and add no declaration for `.downloadMainArea`, `#downloadsSummary`, `#downloadsSummaryProgress`, `#downloadsPanel-blockedSubview-title`, the panel header or the content-area downloads view. Do not add a pressed-state rule; like the sheet's other Platinum push buttons, a pressed enabled button keeps the flat `#CCCCFF` hover face with no bevel. In the header comment block, insert a downloads-panel-buttons provenance paragraph between the downloads-panel-rows paragraph (ending "declaration checks do not establish rendered pixels.") and the bookmark-editor paragraph (starting "No reference shows Firefox's bookmark editor"): no reference shows Firefox's downloads panel buttons; the `#DDDDDD`/`#CCCCFF` faces, black outline and white/`#AAAAAA` bevel adapt `widgets/button.svg` and `widgets/viewitem.svg` with the anchors above; `browser.xhtml` defines `#downloadsHistory` and the subview `.footer-button`s, `DownloadsViewUI.sys.mjs` builds the row `.downloadButton`s, `downloads.inc.css`, `panelUI-shared.css` and `global-shared.css` own the stock paint, disabled buttons keep Firefox's paint, and declaration checks do not establish rendered pixels.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `userChrome.css` contains exactly the two grouped rules above (six parsed selectors after the comma lists are split). `test_palette_is_exact` keeps its expected hex set because the rules introduce no new literal.
- `REQUIRED_RULES` in `tests/test_firefox_theme.py` gains six entries inserted after the three downloads-row entries and before the `.tab-background` entry, with `FACE`, `SELECTION`, `BLACK`, `WHITE` and `BUTTON_SHADOW` built from the constants the module imports: the three normal selectors carry `background-color: FACE`, `color: BLACK`, `border: 1px solid BLACK`, `border-radius: 0` and `box-shadow: BUTTON_BEVEL`; the three hover selectors carry `background-color: SELECTION`, `color: BLACK` and `box-shadow: none`.
- New `TestFirefoxChrome.test_downloads_panel_button_paint_is_scoped_to_the_panel`, placed immediately after `test_downloads_panel_row_paint_is_scoped_to_the_panel_list`, asserts the rule names containing `downloadButton`, `downloadsPanelFooterButton` or `footer-button` are exactly those six, each starts with `#downloadsPanel `, and each equals its `REQUIRED_RULES` entry; the normal selectors carry `:not([disabled])` and no `:hover`, and the hover selectors carry `:not([disabled]):hover`. Using `support.selector_matching.element`/`matches`, build a `panel#downloadsPanel` (`attrs={"type": "arrow"}`) with a `panelview#downloadsPanel-mainView` holding `richlistbox#downloadsListBox` with a `richlistitem` containing `hbox.downloadMainArea` and `button.downloadButton`, a `vbox#downloadsFooter` holding `button#downloadsHistory.downloadsPanelFooterButton.subviewbutton.panel-subview-footer-button.toolbarbutton-1`, a `panelview#downloadsPanel-blockedSubview` holding `moz-button-group#downloadsPanel-blockedSubview-buttons.panel-footer` with `button#downloadsPanel-blockedSubview-unblockButton.footer-button` and `button#downloadsPanel-blockedSubview-deleteButton.footer-button` (`attrs={"default": ""}`), and a `panelview#downloadsPanel-privateBrowsing` holding `button.footer-button.secondary` and `button.footer-button.primary`. The footer button, row action button and all four subview footer buttons match their normal selector with and without `hover`, match their hover selector only when hovered, and a `[disabled]` button matches neither; `#downloadsSummary`, `#downloadsSummaryProgress`, `.downloadMainArea`, `#downloadsPanel-blockedSubview-title` and the panel header match none; a `.downloadButton` in a `richlistbox#downloadsListBox` outside `#downloadsPanel` matches none; and `button#editBookmarkPanelDoneButton.footer-button` under `#editBookmarkPanel` matches none.
- Extend `test_header_names_provenance_and_preference` with the new strings after the downloads-row provenance entries and before the bookmark-editor strings: `"No reference shows Firefox's downloads panel buttons"`, `"widgets/button.svg"`, `"tests/test_desktoptheme_button.py::TestButton"`, `"tests/test_desktoptheme_button_reference.py::TestButtonReference"`, `"widgets/viewitem.svg"`, `"tests/test_desktoptheme_viewitem.py::TestViewItem"`, `"test_selection_background"`, `"downloadsPanelFooterButton"`, `"downloadButton"`, `"footer-button"`, `"DownloadsViewUI.sys.mjs"`, `"panelUI-shared.css"`, `"global-shared.css"`, `"disabled buttons keep Firefox's paint"` and `"platform colour adaptation 2026-10-26"`.
- `docs/invariants.md`: in the existing downloads-panel row under `## firefox`, drop the clause that the row's action button and footer button stay Firefox's from its guarantee, and end its provenance at "on the panel rows only" instead of leaving those buttons to Firefox. Add a row immediately after it whose guarantee is: the downloads panel's footer button (`#downloadsPanel .downloadsPanelFooterButton`), row action buttons (`#downloadsPanel .downloadButton`) and blocked/private subview footer buttons (`#downloadsPanel .footer-button`) are square `#DDDDDD` faces with a 1px black outline and the reference's white/`#AAAAAA` raised bevel, an enabled hovered one being flat `#CCCCFF` with black text and no bevel, while disabled buttons and the panel rows, summary, header, subview copy and content-area list stay Firefox's. Its test column names the new scope test, and its provenance records the missing downloads-panel-buttons reference, the `widgets/button.svg` and `widgets/viewitem.svg` anchors, the installed Firefox ESR 153.5.1 files named above, the disabled-button guard, and that declaration checks do not establish rendered pixels. `tests/invariants.py` stays green.
- `make check` passes, and the existing sheet rules, the downloads panel rows, the Firefox install and their tests keep their declarations and scope.

## Done
