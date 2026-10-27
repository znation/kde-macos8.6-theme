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

### Firefox Platinum chrome: paint the bookmark editor's fields, folder dropdown and footer buttons as Platinum controls (planned 2026-10-26 by the plan role; independent of the waiting trust-panel plan)

**Goal.** Make the bookmark editor panel Firefox opens from the star / "Bookmark This Page" read as Platinum: in `#editBookmarkPanel`, the four text fields (`#editBMPanel_namePicker`, `#editBMPanel_locationField`, `#editBMPanel_tagsField`, `#editBMPanel_keywordField`) become the white square sunken field; the folder dropdown (`#editBMPanel_folderMenuList`) and the Done/Remove footer buttons (`#editBookmarkPanelDoneButton`, `#editBookmarkPanelRemoveButton`) become square `#DDDDDD` push-button faces with a black outline and the reference's white/`#AAAAAA` raised bevel; an enabled hovered dropdown or button is flat `#CCCCFF` with black text and no bevel. The panel header, labels, checkbox, folder and tag expander buttons, folder tree and its New Folder button, tag selector and tags autocomplete, separator and panel body stay Firefox's, and so does the bookmark properties dialog (`#bookmarkpropertiesdialog`), which reuses the same control ids.

**Grounding.** No reference screenshot shows Firefox's bookmark editor, so the paint adapts this theme's Platinum controls (platform adaptation 2026-10-26). The field recipe is the sheet's existing findbar text box: white face, black text, square 1px black border and `inset 1px 1px #999999` shadow, which adapts the reference-grounded `widgets/lineedit.svg` (`tests/test_desktoptheme_lineedit.py::TestLineEdit`). The push-button recipe is the harness's `#DDDDDD` face, black outline and `BUTTON_BEVEL` (`inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA`) that the sheet's permission-popup controls already use, adapting `widgets/button.svg` (`tests/test_desktoptheme_button.py::TestButton`, `tests/test_desktoptheme_button_reference.py::TestButtonReference`). The flat `#CCCCFF` hover adapts `widgets/viewitem.svg` (`tests/test_desktoptheme_viewitem.py::TestViewItem`, `tests/test_colorscheme_reference.py::TestReferenceAnchors::test_selection_background`) and matches the sheet's menu-row mapping.

In the installed Firefox ESR 153.5.1, `chrome/browser/content/browser/browser.xhtml` defines `html:template#editBookmarkPanelTemplate` with `#editBookmarkPanel` (`.panel-no-padding`, `type="arrow"`), its `.panel-header` holding `#editBookmarkPanelTitle`, `#editBookmarkHeaderSeparator`, a `.panel-subview-body` and a `div#editBookmarkPanelContent` holding the four `html:input`s above, `menulist#editBMPanel_folderMenuList` (`.folder-icon`, `size="large"`), `button#editBMPanel_foldersExpander` and `button#editBMPanel_tagsSelectorExpander` (`.expander-down.panel-button`), `button#editBMPanel_newFolderButton`, `richlistbox#editBMPanel_tagsSelector`, `checkbox#editBookmarkPanel_showForNewBookmarks`, and an `html:moz-button-group.panel-footer` holding `button#editBookmarkPanelDoneButton` (`.footer-button`, `default="true"`) and `button#editBookmarkPanelRemoveButton`. `chrome/browser/content/browser/browser-places.js` lazily instantiates that template on the first star click (`StarUI._element("editBookmarkPanelTemplate")`), and `chrome/browser/content/browser/places/editBookmark.js` fills the rows. `chrome/browser/skin/classic/browser/places/editBookmarkPanel.css` paints `#editBMPanel_newFolderButton` and `.expander-up`/`.expander-down` through `--button-*` tokens and makes the focused input's border transparent; `chrome/browser/skin/classic/browser/places/editBookmark.css` paints the folder tree, tag selector and menulist icon. `chrome/toolkit/skin/classic/global/global-shared.css` paints `html|input` from `--input-text-background-color`, `--input-border-color` and `--border-radius-medium`, and paints `.footer-button` from `--button-*` with `[default]` taking the primary accent face. `chrome/toolkit/skin/classic/global/button.css` paints a plain XUL `button` from the system `ButtonFace`/`ButtonBorder`, `chrome/toolkit/skin/classic/global/menulist.css` gives a non-native `menulist` its `--button-background-color` and `--button-border-radius`, `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` declares those tokens, and `chrome/browser/content/browser/places/bookmarkProperties.xhtml` reuses `#editBMPanel_namePicker`, `#editBMPanel_locationField` and `#editBMPanel_folderMenuList` inside `#bookmarkpropertiesdialog`. Nothing in the sheet names `#editBookmarkPanel`, `#editBMPanel_*` or `#bookmarkpropertiesdialog`, and the generic `toolbarbutton:hover` rule does not match these controls, so today the fields keep the rounded stock input face, the dropdown keeps the rounded button face and the Done button keeps the accent primary face.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, append at the very end of the sheet (after the findbar text-box rule) one short comment and three rules, each selector on one line:

```css
#editBookmarkPanel #editBMPanel_namePicker,
#editBookmarkPanel #editBMPanel_locationField,
#editBookmarkPanel #editBMPanel_tagsField,
#editBookmarkPanel #editBMPanel_keywordField {
  background-color: #FFFFFF !important;
  color: #000000 !important;
  border: 1px solid #000000 !important;
  border-radius: 0 !important;
  box-shadow: inset 1px 1px #999999 !important;
}

#editBookmarkPanel #editBMPanel_folderMenuList,
#editBookmarkPanel #editBookmarkPanelDoneButton,
#editBookmarkPanel #editBookmarkPanelRemoveButton {
  background-color: #DDDDDD !important;
  color: #000000 !important;
  border: 1px solid #000000 !important;
  border-radius: 0 !important;
  box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA !important;
}

#editBookmarkPanel #editBMPanel_folderMenuList:hover:not([disabled]),
#editBookmarkPanel #editBookmarkPanelDoneButton:hover:not([disabled]),
#editBookmarkPanel #editBookmarkPanelRemoveButton:hover:not([disabled]) {
  background-color: #CCCCFF !important;
  color: #000000 !important;
  box-shadow: none !important;
}
```

Paint the fields in every state and leave the stock `:focus-visible` outline in place (the sheet sets no `outline`), so focus keeps Firefox's ring. Scope every selector through `#editBookmarkPanel` so the bookmark properties dialog keeps Firefox's controls. Add no rule for the header, title, labels, checkbox, expander buttons, folder tree, New Folder button, tag selector, tags autocomplete, separator or panel body, and do not change the `:root` block, the `panel[type="arrow"]`/`menupopup` token rules or any existing selector. In the header comment block, append a bookmark-editor provenance paragraph immediately after the downloads-panel paragraph (before the "Install it opt-in" paragraph): no reference shows Firefox's bookmark editor; the field, push-button and hover paint adapt `widgets/lineedit.svg`, `widgets/button.svg` and `widgets/viewitem.svg` with the anchors above; `browser.xhtml` defines `template-editBookmarkPanel` and its controls, `browser-places.js` instantiates it and `places/editBookmark.js` fills it, `places/editBookmarkPanel.css` and `places/editBookmark.css` own the stock control paint, and `chrome/toolkit/skin/classic/global/global-shared.css`/`button.css`/`menulist.css` supply the input, button and menulist faces; declaration checks do not establish rendered pixels.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `REQUIRED_RULES` in `tests/test_firefox_theme.py` gains the ten selectors above (one entry each), appended at the end of the dict: each field selector is exactly `background-color: WHITE !important`, `color: BLACK !important`, `border: 1px solid BLACK !important`, `border-radius: 0 !important` and `box-shadow: inset 1px 1px GREY !important`; each dropdown/button selector is exactly `background-color: FACE !important`, `color: BLACK !important`, `border: 1px solid BLACK !important`, `border-radius: 0 !important` and `box-shadow: BUTTON_BEVEL !important`; each `:hover:not([disabled])` selector is exactly `background-color: SELECTION !important`, `color: BLACK !important` and `box-shadow: none !important`, built from the constants the module already imports. `test_palette_is_exact` keeps its expected hex set unchanged because the rules introduce no new hex literal.
- New `TestFirefoxChrome.test_bookmark_panel_control_paint_is_scoped_to_the_bookmark_panel`, placed immediately before `test_readme_names_the_sheet` (the end of the class), asserts the rule names containing `editBookmark` are exactly those ten, each equals its `REQUIRED_RULES` entry, the field and normal rules carry no `:hover`, the hover rules carry `:hover` and `:not([disabled])`, and no rule in the sheet defines `--button-border-radius`, `--input-border-color`, `--input-text-background-color` or `--border-radius-medium`. Using `support.selector_matching.element`/`matches`, build a `panel#editBookmarkPanel` (`panel-no-padding`, `attrs={"type": "arrow"}`) holding a `.panel-header` box with `h1 > span#editBookmarkPanelTitle`, a `toolbarseparator#editBookmarkHeaderSeparator`, a `vbox.panel-subview-body` with `div#editBookmarkPanelContent`, the four `input` elements with the ids above, an `hbox.editBMPanel_folderRow` holding `menulist#editBMPanel_folderMenuList` (`.folder-icon`), `button#editBMPanel_foldersExpander` and `#editBMPanel_tagsSelectorExpander` (`.expander-down.panel-button`), a `vbox#editBMPanel_folderTreeRow` holding `button#editBMPanel_newFolderButton`, an `hbox.editBMPanel_tagsRow` holding `#editBMPanel_tagsField` and `#editBMPanel_tagsSelectorExpander`, a `div#editBMPanel_tagsSelectorRow` holding `richlistbox#editBMPanel_tagsSelector`, a `panel#editBMPanel_tagsAutocomplete`, a `checkbox#editBookmarkPanel_showForNewBookmarks`, and an `html:moz-button-group.panel-footer` holding `button#editBookmarkPanelDoneButton.footer-button` (with `attrs={"default": ""}`) and `button#editBookmarkPanelRemoveButton.footer-button`. Each field matches its field selector with and without `hover`; the dropdown and both footer buttons match their normal selector and, when hovered, their hover selector but not when idle; a `[disabled]` hovered button still matches the normal rule and not the hover rule; every excluded element above matches none of the ten selectors, a `toolbarbutton.subviewbutton` under `#nav-bar` matches none, and the same four inputs plus the menulist built inside `#bookmarkpropertiesdialog` match none of the ten.
- New `TestFirefoxChrome.test_bookmark_panel_provenance`, placed immediately after the scope test, asserts the leading comment names `"No reference shows Firefox's bookmark editor"`, `"widgets/lineedit.svg"`, `"tests/test_desktoptheme_lineedit.py::TestLineEdit"`, `"widgets/button.svg"`, `"tests/test_desktoptheme_button.py::TestButton"`, `"tests/test_desktoptheme_button_reference.py::TestButtonReference"`, `"widgets/viewitem.svg"`, `"tests/test_desktoptheme_viewitem.py::TestViewItem"`, `"test_selection_background"`, `"#editBookmarkPanel"`, `"template-editBookmarkPanel"`, `"editBMPanel_namePicker"`, `"editBMPanel_locationField"`, `"editBMPanel_tagsField"`, `"editBMPanel_keywordField"`, `"editBMPanel_folderMenuList"`, `"editBookmarkPanelDoneButton"`, `"editBookmarkPanelRemoveButton"`, `"chrome/browser/content/browser/browser-places.js"`, `"chrome/browser/content/browser/places/editBookmark.js"`, `"chrome/browser/skin/classic/browser/places/editBookmarkPanel.css"`, `"chrome/browser/skin/classic/browser/places/editBookmark.css"`, `"chrome/toolkit/skin/classic/global/global-shared.css"`, `"chrome/toolkit/skin/classic/global/button.css"`, `"chrome/toolkit/skin/classic/global/menulist.css"`, `"#bookmarkpropertiesdialog"` and `"platform adaptation 2026-10-26"`. Leave `test_header_names_provenance_and_preference` untouched so this plan and the waiting trust-panel plan do not edit the same tuple.
- `docs/invariants.md` gains a row appended at the end of the `## firefox` table, after the unified-extensions panel row and before `## gtk`: the bookmark editor's fields (`#editBookmarkPanel #editBMPanel_namePicker`, `#editBMPanel_locationField`, `#editBMPanel_tagsField`, `#editBMPanel_keywordField`) are the white square sunken field with black text, and its folder dropdown (`#editBMPanel_folderMenuList`) and Done/Remove footer buttons (`#editBookmarkPanelDoneButton`, `#editBookmarkPanelRemoveButton`) are square `#DDDDDD` controls with a black outline and the reference's white/`#AAAAAA` raised bevel, an enabled hovered one being flat `#CCCCFF` with black text and no bevel, while the header, labels, checkbox, expander buttons, folder tree and New Folder button, tag selector, tags autocomplete, separator, panel body and the `#bookmarkpropertiesdialog` copies stay Firefox's; its test column names the new scope test and its provenance records the missing Firefox bookmark-editor reference, the `widgets/lineedit.svg`, `widgets/button.svg` and `widgets/viewitem.svg` anchors, the installed Firefox ESR 153.5.1 files and functions above, and that declaration checks do not establish rendered pixels. `tests/invariants.py` stays green.
- `make check` passes, and the existing sheet rules, the Firefox install and their tests keep their declarations and scope.

## Done
