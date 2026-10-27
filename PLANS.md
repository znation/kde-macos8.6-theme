# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._


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

### Firefox Platinum chrome: paint the Page Info dialog's meta and image trees as Platinum list rows (planned 2026-10-27 by the plan role; independent of the waiting Page Info media-preview plan — both append at the very end of `userChrome.css`, insert their provenance paragraphs before the header's closing `*/` and trim only their own words from the shared stay-Firefox sentences, so either order merges)

**Goal.** Make the General panel's meta table and the Media panel's image list read as Platinum lists: the `tree#metatree` and `tree#imagetree` containers become the opaque `#FFFFFF` sunken field the landed `#permList` recipe uses — square corners, a 1px `#000000` outline, the `inset 1px 1px #999999` top-left shadow and black text — with rows left transparent over the field so no skin hover wash paints, a selected row flat `#CCCCFF` with black text (the theme's flat selection), and the Media panel's broken-image rows keeping their stock italic `graytext`. No `appearance: none` is needed: the trees are painted with plain declarations, no `-moz-default-appearance`. The trees' stock geometry stays Firefox's — the `tree { margin: 0.5em }` and `tree { margin: 0 4px }` margins, `#imagetree`'s `min-height: 10em` and `margin-block: 2px 0`, the rows' `1px solid transparent` border and `max(24px, 1.3em)` min-height, the cells, twisties, sort direction and `hidecolumnpicker` behaviour. The column headers (`treecol` and the column-picker button, painted `-moz-ColHeader` with a `ThreeDLightShadow` divider) stay Firefox's stock paint and are named as untouched. The deck's permission list, display fields, media preview, security tables and the landed top-bar, tab and button paints are untouched. The tree rows need `::-moz-tree-row`/`::-moz-tree-cell-text` pseudo-element selectors that `tests/support/selector_matching` does not evaluate (only `#id`, `.class`, `[attribute]`, `:hover` and `:not(...)` are in its subset), so the new tests are rule-name and declaration assertions, with element matching used only for the two container selectors.

**Grounding.** No reference screenshot shows Firefox's Page Info trees, so the paint adapts this theme's Platinum list surfaces (platform colour adaptation 2026-10-27). The `#FFFFFF` face and `#999999` sunken shadow adapt `widgets/lineedit.svg` (`tests/test_desktoptheme_lineedit.py::TestLineEdit` and `TestLineEditReference`), grounded in `macos8.6-screenshots/firstboot_betawiki.png`, and are the exact recipe the sheet's landed `#mainDeck input` and `#permList` rules already ship; `#metatree`/`#imagetree` are the deck's remaining list-shaped surfaces. The transparent rows and no hover highlight adapt `widgets/listitem.svg` (`tests/test_desktoptheme_listitem.py::TestListItem`), whose comment records that Mac OS 8.6 lists have no hover highlight, and the flat `#CCCCFF` black-text selection adapts `widgets/viewitem.svg` (`tests/test_desktoptheme_viewitem.py::TestViewItem`), pinned by `test_selection_background` — the same reading the sheet's `#prefs > tr:hover` and the downloads panel's `richlistitem[selected]` rules already paint. In the installed Firefox ESR 153.5.1, `chrome/browser/content/browser/pageinfo/pageInfo.xhtml` defines `tree#metatree` inside `vbox#metaTags` (`hidecolumnpicker="true"`, columns `#meta-name`/`#meta-content`) and `tree#imagetree` in `vbox#mediaPanel` (columns `#image-address`, `#image-type` and their siblings), and neither tree carries a `multicol` attribute, so the global skin's `treechildren::-moz-tree-row(multicol, odd)` odd-row paint never applies to them. `chrome/toolkit/skin/classic/global/tree/tree.css` paints `tree` with plain declarations (`background-color: Field`, `color: FieldText`, `border: 1px solid ThreeDShadow`, `margin: 0 4px`) and paints rows through `treechildren::-moz-tree-row(hover)` (an `hsla(0, 0%, 50%, 0.15)` wash), `::-moz-tree-row(selected)` (`-moz-cellhighlight`) and `::-moz-tree-row(selected, focus)` (`SelectedItem`), with cell text through `::-moz-tree-cell-text` (`color: inherit`) and `::-moz-tree-cell-text(selected)`/`(selected, focus)` (`-moz-cellhighlighttext`/`SelectedItemText`), so every overridden paint is a plain declaration and no `appearance` declaration is needed; the pageinfo skin `chrome/browser/skin/classic/browser/pageInfo.css` adds only `tree { margin: 0.5em }`, `#imagetree { min-height: 10em; margin-block: 2px 0 }` and `treechildren::-moz-tree-cell-text(broken) { font-style: italic; color: graytext }`. Both ids appear only in page-info files, so the rules cannot leak into browser chrome. Declaration checks do not establish rendered pixels.

**Approach.** Append at the very end of `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, after the `#permList .permission:hover` rule (or after the `#imagecontainerbox` rule when the media-preview plan has landed), one short comment naming the adaptation and these five rules in this order (the later selected rule paints a hovered selected row):

```css
#metatree,
#imagetree {
  background-color: #FFFFFF !important;
  color: #000000 !important;
  border: 1px solid #000000 !important;
  border-radius: 0 !important;
  box-shadow: inset 1px 1px #999999 !important;
}

tree#metatree treechildren::-moz-tree-row(hover),
tree#imagetree treechildren::-moz-tree-row(hover) {
  background-color: transparent !important;
}

tree#metatree treechildren::-moz-tree-row(selected),
tree#imagetree treechildren::-moz-tree-row(selected) {
  background-color: #CCCCFF !important;
}

tree#metatree treechildren::-moz-tree-cell-text,
tree#imagetree treechildren::-moz-tree-cell-text {
  color: #000000 !important;
}

tree#imagetree treechildren::-moz-tree-cell-text(broken) {
  color: graytext !important;
}
```

Each `!important` declaration beats the skin's normal ones, so one `(selected)` rule covers `(selected, focus)` and one cell-text rule covers `(selected)`/`(selected, focus)`; the `(broken)` rule re-asserts `graytext` because the black cell-text rule would otherwise recolour the broken rows. Keep the stock margins, `#imagetree`'s min-height and margin-block, the rows' transparent border and min-height, and every cell, twisty, splitter and sort behaviour. Add no rule for `treecol`, `.tree-columnpicker-button`, `.treecol-text` or the sort direction (headers keep Firefox's paint), for `treechildren::-moz-tree-row(multicol, odd)` (both page-info trees lack a `multicol` attribute, verified in `pageInfo.xhtml`), for the `dropOn`/`current`/`editing` states (a page-info tree is never edited or a drop target) or for `#metaTags`, `#mediaPanel` or any label, and change no existing selector. In the header comment block, insert a tree provenance paragraph immediately before the closing `*/` (after the permission-list paragraph, and after the media-preview paragraph when that plan has landed): no reference shows Firefox's Page Info trees; the `#FFFFFF` face and `#999999` sunken shadow adapt `widgets/lineedit.svg` and the `#mainDeck input`/`#permList` recipes, the transparent rows honour `widgets/listitem.svg`'s no-hover-highlight list reading and the flat `#CCCCFF` black-text selected row adapts `widgets/viewitem.svg` pinned by `test_selection_background`; `pageInfo.xhtml` defines `tree#metatree` and `tree#imagetree` with no `multicol` attribute and `chrome/toolkit/skin/classic/global/tree/tree.css` plus the pageinfo skin's `pageInfo.css` own the stock `Field`/`ThreeDShadow` paint, the row hover wash, the `-moz-cellhighlight`/`SelectedItem` selection, the `-moz-cellhighlighttext`/`SelectedItemText` selected text and the broken rows' italic `graytext`; the column headers stay Firefox's; declaration checks do not establish rendered pixels (platform colour adaptation 2026-10-27). Also trim the trees from the stay-Firefox surface lists in the existing Page Info texts — the header's top-bar provenance paragraph drops `meta and image trees` ("…the dialog body, media preview, security tables, description labels and focus rings stay Firefox's…"), the `#topBar` rule's leading comment drops `trees` ("…the dialog body, fields, media preview, security tables and labels keep Firefox's own paint…"), and the `docs/invariants.md` Page Info top-bar, fields and permission-list rows drop the trees from their stay-Firefox lists — leaving every other word unchanged (the waiting media-preview plan trims `media preview` from the same sentences; whichever lands first, the other's words are still present to trim).

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/support/firefox_chrome_cases.py`, `tests/test_firefox_theme_page_info.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `userChrome.css` gains exactly the five new rules above: the two container selectors `#metatree` and `#imagetree` (one block, split by the test parser's selector-list splitting in `tests/support/gtk_css.py::parse_css`), the two hover row selectors, the two selected row selectors, the two cell-text selectors and the one `(broken)` cell-text selector. Every existing selector keeps its declarations, and `test_palette_is_exact` keeps its expected hex set because the rules introduce no new hex literal (`graytext` is a system colour, not a hex literal; the `#CCCCFF` is the palette's `SELECTION`).
- `REQUIRED_RULES` in `tests/support/firefox_chrome_cases.py` gains, appended immediately after the last existing Page Info assignment (after `REQUIRED_RULES["#permList .permission:hover"]`, or after the `#imagecontainerbox` assignment when the media-preview plan has landed): `"#metatree"` and `"#imagetree"` mapping to `background-color: {WHITE} !important`, `color: {BLACK} !important`, `border: 1px solid {BLACK} !important`, `border-radius: 0 !important` and `box-shadow: inset 1px 1px {GREY} !important`; the two hover row selectors mapping to `background-color: transparent !important`; the two selected row selectors mapping to `background-color: {SELECTION} !important`; the two cell-text selectors mapping to `color: {BLACK} !important`; and `"tree#imagetree treechildren::-moz-tree-cell-text(broken)"` mapping to `color: graytext !important` — with the constants `support.platinum_palette` already exports, and no container entry carrying an `appearance` declaration.
- New `TestFirefoxPageInfo.test_page_info_tree_paint_is_scoped_to_page_info`, placed immediately after `test_page_info_permission_list_paint_is_scoped_to_page_info` (or after `test_page_info_media_preview_paint_is_scoped_to_page_info` when the media-preview plan has landed): asserts the rule names containing `metatree` or `imagetree` are exactly those eight selector names, each equals its `REQUIRED_RULES` entry, the pseudo-element names contain `::-moz-tree-row(hover)`, `::-moz-tree-row(selected)` and `::-moz-tree-cell-text`, and no rule name contains `treecol` or `tree-columnpicker`. Element matching (`support.selector_matching.element`/`matches`) covers only the containers: build `window` holding `deck#mainDeck` with `vbox#metaTags` containing `tree#metatree` and `vbox#mediaPanel` containing `tree#imagetree`, plus a stray `tree` with no id in another panel and the bookmark panel's `tree#editBMPanel_folderTree`; assert `tree#metatree` and `tree#imagetree` each match their own container selector and not the other's, and the stray trees match none of the eight names.
- New `TestFirefoxPageInfo.test_page_info_tree_provenance`, placed immediately after the scope test, asserts the leading comment names `"No reference shows Firefox's Page Info trees"`, `"widgets/lineedit.svg"`, `"firstboot_betawiki.png"`, `"tests/test_desktoptheme_lineedit.py::TestLineEdit"`, `"TestLineEditReference"`, `"#mainDeck input"`, `"#permList"`, `"widgets/listitem.svg"`, `"tests/test_desktoptheme_listitem.py::TestListItem"`, `"no hover highlight"`, `"widgets/viewitem.svg"`, `"tests/test_desktoptheme_viewitem.py::TestViewItem"`, `"test_selection_background"`, `"pageInfo.xhtml"`, `"multicol"`, `"chrome/toolkit/skin/classic/global/tree/tree.css"`, `"pageInfo.css"`, `"Field"`, `"ThreeDShadow"`, `"-moz-cellhighlight"`, `"SelectedItem"`, `"-moz-cellhighlighttext"`, `"SelectedItemText"`, `"graytext"`, `"column headers stay Firefox's"`, `"Declaration checks do not establish rendered pixels"` and `"platform colour adaptation 2026-10-27"`. Leave `test_page_info_provenance`, `test_page_info_permission_list_provenance`, and the field and (when landed) media-preview provenance tests untouched so this plan does not edit their tuples.
- `docs/invariants.md` gains a row appended at the end of the `## firefox` table, after the last Page Info row and before `## gtk`: the Page Info dialog's meta and image trees (`tree#metatree`, `tree#imagetree`) are the opaque `#FFFFFF` sunken list field — square corners, a 1px `#000000` outline, the `inset 1px 1px #999999` top-left shadow and black text — with rows transparent over the field so no hover wash paints, a selected row flat `#CCCCFF` with black text, and the Media panel's broken-image rows keeping their italic `graytext`, while the column headers, the rows' stock border and min-height, the cells, twisties, splitters, sort direction and column-picker behaviour and the trees' stock margins and `#imagetree` min-height stay Firefox's, and the permission list, display fields, media preview and security tables stay their own paints. Its test column names the new scope test, and its provenance records the missing Page Info trees reference, the `widgets/lineedit.svg` (grounded in `firstboot_betawiki.png`, pinned by `tests/test_desktoptheme_lineedit.py`), `widgets/listitem.svg` and `widgets/viewitem.svg` (`test_selection_background`) anchors, the installed Firefox ESR 153.5.1 `pageInfo.xhtml`, global `tree.css` and pageinfo skin `pageInfo.css` files, the no-`multicol` fact, and that declaration checks do not establish rendered pixels. `tests/invariants.py` stays green.
- `make check` passes, and the existing `userChrome.css` rules (including the `#viewGroup`, `#mainDeck`, `#mainDeck input`, `#permList` and, when it has landed, `#imagecontainerbox` paints), the Firefox install and their tests keep their declarations and scope.

### Firefox Platinum chrome: paint the Page Info security panel's groupbox frames and headers as the Platinum group frame (planned 2026-10-27 by the plan role; independent of the waiting Page Info meta/image-trees plan — both append at the very end of `userChrome.css`, insert their provenance paragraphs before the header's closing `*/` and trim only their own words from the shared stay-Firefox sentences, so either order merges)

**Goal.** Make the security panel's three group frames read as Platinum group boxes: each `groupbox` child of `vbox#securityPanel` gets the reference's etched group frame — a 1px `#888888` rectangle carrying the same `#888888`/`#FFFFFF` etched pair the sheet's rules already pin, drawn as the 1px highlight copy offset one pixel right and down (the light half running inside the dark top and left, outside the dark bottom and right) — over a transparent interior that keeps the dialog body face, square corners, `2px 8px` interior padding, and a `1em` face gap between stacked frames; each frame's `label.header` keeps Firefox's heading weight but takes the black Platinum text colour. The frames' contents — the identity table's readonly inputs (still the `#mainDeck input` paint), the `#securityTable` rows, the `#security-technical-*` labels and descriptions — and the security panel's already-painted buttons keep their own paints, as do the General and Media panels' `.header` labels (`#metaTagsCaption`, `html:input#hostText`) which sit outside `#securityPanel`.

**Grounding.** Unlike the sheet's other Page Info surfaces, this frame IS in the lossless reference set: `macos8.6-screenshots/systemprofiler_betawiki.png` (the retail Japanese 8.6 System Profiler) draws the framed group box for the first Software-overview section as a dark 1px `#888888` rectangle spanning x=241..678, y=103..153 with the 1px `#FFFFFF` copy offset one pixel right and down (top row y=104 and left column x=242 inside the dark lines, right column x=679 and bottom row y=154 outside), whose bottom rule and left edge `tests/test_desktoptheme_line.py::TestLineReference` already re-derives as the etched pair — `test_horizontal_rule_matches_reference` pins this box's bottom rule ((260,153) dark, (260,154) light) and `test_vertical_rule_matches_reference` its left edge ((241,128) dark, (242,128) light). The same screenshot grounds the black text: the reference's header glyphs (the section label beside its disclosure triangle, above the frame at y=80..86) sample pure `#000000`, the shared Platinum foreground. The reference header sits above the frame with a disclosure triangle, which this plan does not reproduce: `pageInfo.xhtml`'s groupboxes carry no disclosure control and the label is the groupbox's first child inside the frame, so the headers stay in Firefox's markup order and only their colour is adapted. In the installed Firefox ESR 153.5.1, `chrome/browser/content/browser/pageinfo/pageInfo.xhtml` opens `vbox#securityPanel` with three `groupbox` elements, each headed by a `label.header` (the `security-view-identity`, `security-view-privacy` and `security-view-technical` l10n ids) and holding the pane's table or descriptions; `chrome/toolkit/content/global/xul.css` gives `groupbox` only `flex-direction: column` and no `-moz-default-appearance`, and neither `chrome/toolkit/skin/classic/global/global.css` (whose `global-shared.css` supplies only the `.header` font weight and the stock label margins) nor the pageinfo skin's `pageInfo.css` paints any groupbox border, so the sheet adds the whole frame with plain declarations and no `appearance: none` is needed (`!important` keeps the sheet's convention). `#securityPanel` appears in no chrome file outside page info (`pageInfo.xhtml`, `pageInfo.js`, `pageInfo.css`), so the `#securityPanel >` scoping cannot leak into browser chrome. The between-frames gap is not re-derivable from the reference set — the lossless PNG shows one framed box and no second frame, and the lossy `apps_macrumors8.6.jpg` shows the English 8.6 Profiler's stacked framed sections but is not pixel ground — so the `1em` face gap reuses `pageInfo.css`'s own `#securityPanel table { margin-bottom: 1em }` spacing unit (platform geometry adaptation 2026-10-27); the reference renders no pad value usable as a CSS literal either, and `2px 8px` keeps the first content rows about 8px clear of the light half (the box's interior content starts at x≈250, seven pixels inside the x=242 light column, and six rows below the y=104 light row) within the stock label margins.

**Approach.** Append at the very end of `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, after the `#imagecontainerbox` rule (or after the trees plan's rules when that plan has landed), one short comment naming the adaptation and these three rules in this order:

```css
#securityPanel > groupbox {
  border: 1px solid #888888 !important;
  border-radius: 0 !important;
  padding: 2px 8px !important;
  box-shadow: 1px 1px #FFFFFF, inset 1px 1px #FFFFFF !important;
}

#securityPanel > groupbox + groupbox {
  margin-top: 1em !important;
}

#securityPanel > groupbox > label.header {
  color: #000000 !important;
}
```

The border is the dark half and the two shadow halves reproduce the reference's offset highlight copy exactly: the outset `1px 1px #FFFFFF` draws the light bottom row and right column outside the border box, and the inset `1px 1px #FFFFFF` draws the light top row and left column just inside the border, so every frame edge reads dark-over-light as the reference's rectangle does, corners included. Keep the interiors transparent (no `background-color` or `color` declaration on the groupbox — the dialog body face and the stock content colours show through, and the tables' rows, readonly inputs and technical descriptions keep their paints), keep `xul.css`'s `flex-direction: column` and the labels' stock margins and bold `.header` weight, and add no rule for the frame's contents, the `hbox` help-button row, the deck's other panels' `groupbox` elements (there are none — but the selectors stay `#securityPanel`-scoped so none could leak from later Firefox markup), any hover, focus, active or disabled frame variant (a groupbox and its header are static), the disclosure triangle the reference draws (the Page Info groupboxes carry none) or any `caption` element (the markup has none), and change no existing selector. In the header comment block, insert a group-frame provenance paragraph immediately before the closing `*/` (after whichever Page Info paragraphs are present when this lands): the reference group box — `macos8.6-screenshots/systemprofiler_betawiki.png`'s framed Software-overview section at x=241..679, y=103..154, the dark `#888888` rectangle with its `#FFFFFF` highlight copy offset one pixel right and down — is re-derived edge for edge and corner by the extended `tests/test_desktoptheme_line.py::TestLineReference`, whose existing bottom-rule and left-edge pair assertions already pin this box's etched pair; `pageInfo.xhtml` supplies the three `#securityPanel` groupboxes and their `label.header` headers, `chrome/toolkit/content/global/xul.css` gives `groupbox` only `flex-direction: column` with no default appearance and no skin paints a border, so the sheet adds the whole frame; the headers stay inside the frame in Firefox's markup order and black takes the shared Platinum foreground; `1em` between frames is `pageInfo.css`'s own spacing unit because the lossless reference shows a single framed box (lossy `apps_macrumors8.6.jpg` is not pixel ground); declaration checks pin the sheet's declarations and the reference test re-derives the frame's pixels, not Firefox's rendered dialog (reference grounding 2026-10-27). Also trim the frame from the shared stay-Firefox sentences by replacing `security tables` with `security-table rows` in exactly three sheet texts — the top-bar provenance paragraph's stay list (`…the dialog body, security-table rows, description labels and focus rings…` once the trees plan has also trimmed `meta and image trees`, or carrying `meta and image trees,` before it when this lands first), the `#topBar` rule's leading comment (`…the dialog body, fields, trees, security-table rows and labels…`), and `docs/invariants.md`'s top-band, field, permission-list and media-preview rows' stay lists (`meta and image trees, security-table rows and description labels`, `the trees, security-table rows and labels`, `the deck's trees, display fields and security-table rows`, `the trees and security-table rows`) — leaving every other word unchanged (the waiting trees plan trims `meta and image trees` and `trees` from the same sentences; the words never overlap, so either order merges, and when the trees plan has landed first its new invariants row's `security tables` becomes `security-table rows` in the same edit).

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/support/firefox_chrome_cases.py`, `tests/test_firefox_theme_page_info.py`, `tests/test_desktoptheme_line.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `userChrome.css` gains exactly the three new rules above, with no rule name other than the three selectors namespaced to `groupbox` and no new hex literal (`#888888` is the sheet's existing etched `#888888`, and `#FFFFFF`/`#000000` are the palette's `WHITE`/`BLACK`), so `test_palette_is_exact` keeps its expected hex set. Every existing selector keeps its declarations, and the two shared stay-Firefox sentences change only as the trim above specifies.
- `REQUIRED_RULES` in `tests/support/firefox_chrome_cases.py` gains, appended after the last existing Page Info assignment (`REQUIRED_RULES["#permList .permission:hover"]`, or after `"tree#imagetree treechildren::-moz-tree-cell-text(broken)"` when the trees plan has landed): `"#securityPanel > groupbox"` mapping to `border: 1px solid {ETCH_DARK} !important`, `border-radius: 0 !important`, `padding: 2px 8px !important` and `box-shadow: 1px 1px {WHITE}, inset 1px 1px {WHITE} !important`; `"#securityPanel > groupbox + groupbox"` mapping to `margin-top: 1em !important`; and `"#securityPanel > groupbox > label.header"` mapping to `color: {BLACK} !important` — importing `ETCH_DARK` from `support.gtk_theme_spec` beside the existing `BUTTON_BEVEL`/`ETCH_DARK`/`RAISED_BEVEL` import, and with no entry carrying `background-color`, `color` (except the header), `font-weight` or an `appearance` declaration. The paged entry order is the CSS order above; the `+` selector needs no element matching (the `support.selector_matching` subset has no adjacent-sibling combinator), so it is assertion-only like the trees plan's pseudo-element selectors.
- New `TestFirefoxPageInfo.test_page_info_groupbox_paint_is_scoped_to_page_info`, placed immediately after the last Page Info scope test (`test_page_info_permission_list_paint_is_scoped_to_page_info`, or after `test_page_info_tree_paint_is_scoped_to_page_info` when the trees plan has landed): asserts the rule names containing `groupbox` are exactly the three selector names and each equals its `REQUIRED_RULES` entry; and element matching covers the two matchable selectors: build `window` holding `deck#mainDeck` with `vbox#securityPanel` holding three `groupbox` children whose first children are `label.header` labels, plus a stray `groupbox` with a `label.header` child elsewhere in the deck (outside `#securityPanel`); assert the three security groupboxes match `"#securityPanel > groupbox"` and the stray one matches neither that nor the `+` selector's key, the three headers match `"#securityPanel > groupbox > label.header"` and the stray header matches none of the three names.
- New `TestFirefoxPageInfo.test_page_info_groupbox_provenance`, placed immediately after the scope test, asserts the leading comment names `"systemprofiler_betawiki.png"`, `"x=241..679"`, `"y=103..154"`, `"#888888"`, `"offset one pixel right and down"`, `"tests/test_desktoptheme_line.py::TestLineReference"`, `"pageInfo.xhtml"`, `"label.header"`, `"chrome/toolkit/content/global/xul.css"`, `"flex-direction: column"`, `"-moz-default-appearance"`, `"#securityPanel"`, `"pageInfo.css"`, `"apps_macrumors8.6.jpg"`, `"1em"`, `"Declaration checks pin the sheet's declarations"` and `"reference grounding 2026-10-27"`. Leave every existing provenance test's tuple untouched so this plan edits none of them.
- `tests/test_desktoptheme_line.py::TestLineReference` gains three test methods after `test_vertical_rule_matches_reference`, reusing `assert_rule` where it applies: `test_group_box_top_rule_matches_reference` asserts the same box's top rule (`assert_rule((400, 103), (400, 104), (400, 102), (400, 105))`) and `test_group_box_right_rule_matches_reference` its right edge (`assert_rule((678, 110), (679, 110), (677, 110), (680, 110))`); `test_group_box_corners_match_reference` asserts the box's four corner blocks pixel for pixel — (241,103)/(242,103)/(241,104)/(242,104) from the top-left are `#888888`/`#888888`/`#888888`/`#FFFFFF`, (678,103)/(678,104)/(679,104)/(677,104) from the top-right are `#888888`/`#888888`/`#FFFFFF`/`#FFFFFF` with (679,103) the `#EEEEEE` body, (241,153)/(242,153)/(242,154)/(241,154) from the bottom-left are `#888888`/`#888888`/`#FFFFFF`/`#EEEEEE`, and (678,153)/(679,153)/(678,154)/(679,154) from the bottom-right are `#888888`/`#FFFFFF`/`#FFFFFF`/`#FFFFFF` — so the extended reference covers every edge and corner of the frame this sheet's rule adapts. Existing test methods stay untouched.
- `docs/invariants.md` gains a row appended at the end of the `## firefox` table, after the last Page Info row and before `## gtk`: the security panel's group frames (`#securityPanel > groupbox`) are the reference's etched group box — a 1px `#888888` rectangle with the `#FFFFFF` highlight copy offset one pixel right and down, square corners `2px 8px` interior padding and a transparent interior over the dialog body face, `1em` between stacked frames — with each frame's `label.header` black at Firefox's stock heading weight and the reference's disclosure-triangle header not reproduced (the Page Info groupboxes carry no disclosure control), while the frames' contents, the deck's other painted surfaces and the General and Media panels' `.header` labels keep their own paints. Its test column names the new scope and `TestLineReference` extension tests, and its provenance records the `systemprofiler_betawiki.png` group box at x=241..679, y=103..154 that `tests/test_desktoptheme_line.py::TestLineReference` re-derives, the installed Firefox ESR 153.5.1 `pageInfo.xhtml`/`xul.css`/`pageInfo.css` facts, the `1em` gap's pageInfo.css spacing source, and the not-reproduced disclosure header. `tests/invariants.py` stays green.
- `make check` passes, and the existing `userChrome.css` rules (including the `#topBar`, `#viewGroup`, `#mainDeck`, `#mainDeck input`, `#permList`, `#imagecontainerbox` and, when it has landed, the trees paints), the Firefox install and their tests keep their declarations and scope.

## Done
