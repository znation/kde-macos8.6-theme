# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; landed-plan facts re-trimmed 2026-10-23
by the clean role; validation scope clarified 2026-10-25 by the steward role):** The
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
selected by `apply-gtk`; `make install` copies no GTK files); and the render and fidelity tooling.
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
landed, while its profile install is part 2/2, which has landed).

_None yet._

### Firefox Platinum chrome: paint the app-menu rows like a Platinum menu (planned 2026-10-26 by the plan role)

**Goal.** Make the toolbar app menu (`#appMenu-popup`) read as a Mac OS 8.6 menu: each row is square, and an enabled row under the pointer takes the flat `#CCCCFF` menu-item highlight with black text and no toolbar bevel. The app menu's disabled and focus states, separators, panel headers and check glyphs stay Firefox's, as do the library, history and identity arrow panels.

**Grounding.** No reference screenshot shows Firefox chrome or its app menu. The highlight adapts the reference-grounded `widgets/viewitem.svg`, whose `hover`/`selected`/`selected+hover` slices are each a flat square `#CCCCFF` with no bevel or outline (`tests/test_desktoptheme_viewitem.py::TestViewItem.test_viewitem_highlights_are_flat_selection_colour`), and reuses the sheet's existing `menupopup > menuitem:hover` mapping of that menu-item highlight. `#CCCCFF` is the project's sampled `[Colors:Selection]` token pinned by `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_selection_background`; the reference's open Apple menu shows no highlighted item, so the menu-item highlight has no per-pixel sample. Record the missing Firefox app-menu reference and the dated adaptation in the sheet header and the invariants row.

In the installed Firefox ESR 153.5.1, `browser/omni.ja` `chrome/browser/content/browser/browser.xhtml` defines `<panel id="appMenu-popup" type="arrow">` around `<panelmultiview id="appMenu-multiView">`, whose views' `.panel-subview-body` hold `toolbarbutton.subviewbutton` rows (e.g. `#appMenu-new-tab-button2`, `#appMenu-passwords-button`, `#appMenu-settings-button`). `browser/omni.ja` `chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css` gives `.subviewbutton` `border-radius: var(--panel-menuitem-border-radius)` and gives `toolbarbutton.subviewbutton:not([disabled]):hover` the ghost tokens `--button-text-color-ghost-hover` and `--button-background-color-ghost-hover`, with a pressed `box-shadow`; toolkit `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` defines `--panel-menuitem-border-radius: var(--border-radius-small)` (4px) and maps the ghost hover to the violet `--button-background-color-hover`. The sheet's generic `toolbarbutton:hover:not([disabled="true"])` rule also adds its raised bevel, and the `#appMenu-popup` panel is already a `panel[type="arrow"]`, so the `#DDDDDD` face and black text tokens apply but the rows' radius and hover are still Firefox's.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, immediately after the `toolbarbutton:hover:active:not([disabled="true"])` rule and before the `/* The all-tabs panel rows ... */` comment, add two rules with a short comment:

```css
#appMenu-popup .subviewbutton {
  border-radius: 0 !important;
}

#appMenu-popup .subviewbutton:hover:not([disabled]) {
  background-color: #CCCCFF !important;
  color: #000000 !important;
  box-shadow: none !important;
}
```

Square the rows directly rather than overriding `--panel-menuitem-border-radius`, because `panelUI-shared.css` applies that token to every `.subviewbutton` in every panel, including the all-tabs panel's mute and close controls and the library/history panels, which stay Firefox's. The hover rule excludes disabled rows, so a disabled row keeps Firefox's dimmed paint; because it matches while `:active` too and out-specifies Firefox's pressed ghost rule, a pressed row stays `#CCCCFF` with no pressed shadow. Add no margin, padding, border, font, separator or panel-header declaration, and do not touch `:focus-visible`.

In the header, append a provenance paragraph after the all-tabs paragraph (the one beginning `No reference shows Firefox's all-tabs panel;`) and before the closing `*/`: no reference shows Firefox's app menu; the row highlight adapts `widgets/viewitem.svg` and the sheet's menu-item mapping (platform colour adaptation 2026-10-26); Firefox's `chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css` gives `.subviewbutton` its `--panel-menuitem-border-radius` and its `--button-background-color-ghost-hover` violet hover, `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` defines those tokens, `chrome/browser/content/browser/browser.xhtml` defines `#appMenu-popup`, and the sheet suppresses the ghost hover and toolbar bevel on these rows only; declaration checks do not establish rendered pixels.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `REQUIRED_RULES` in `tests/test_firefox_theme.py` gains the two selectors `#appMenu-popup .subviewbutton` (`border-radius: 0 !important`) and `#appMenu-popup .subviewbutton:hover:not([disabled])` (`background-color: #CCCCFF !important`, `color: #000000 !important`, `box-shadow: none !important`), after the all-tabs entries, using `SELECTION` and `BLACK` from `support.platinum_palette`.
- New `TestFirefoxChrome.test_app_menu_row_paint_is_scoped_to_the_app_menu` asserts the selectors naming `appMenu` are exactly the radius and hover rules, each starts with `#appMenu-popup .subviewbutton`, each equals its `REQUIRED_RULES` entry, the hover selector carries `:not([disabled])` and `:hover`, the radius rule carries no declaration besides `border-radius`, and no rule in the sheet overrides `--panel-menuitem-border-radius`.
- `test_header_names_provenance_and_preference` gains the new paragraph's strings: `"No reference shows Firefox's app menu"`, `"widgets/viewitem.svg"`, `"tests/test_desktoptheme_viewitem.py::TestViewItem"`, `"chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css"`, `"#appMenu-popup"`, `"toolbarbutton.subviewbutton"`, `"--panel-menuitem-border-radius"`, `"--button-background-color-ghost-hover"` and `"platform colour adaptation 2026-10-26"`.
- `docs/invariants.md` gains a row in the `## firefox` table after the all-tabs row: the app-menu rows (`#appMenu-popup .subviewbutton`) are square and a hovered enabled row is flat `#CCCCFF` with black text and no bevel, while disabled rows, focus rings, separators, panel headers and check glyphs stay Firefox's; its test column names the new test; its provenance records the missing Firefox app-menu reference, the `widgets/viewitem.svg` adaptation, the installed Firefox ESR 153.5.1 selectors and tokens above, and that declaration checks do not establish rendered pixels.
- `make check` passes; the generic `toolbarbutton` rules, the menu, tab, downloads-panel, all-tabs, sidebar, address-bar, find-bar and tooltip rules keep their declarations, and no rule is added for a non-`#appMenu-popup` panel.

### Firefox Platinum chrome, part 1/2: ship a `userContent.css` painting the about:downloads list like a Platinum list (planned 2026-10-26 by the plan role; independent of the waiting app-menu row plan; the opt-in profile install is its own later run)

**Goal.** Ship a standalone `userContent.css` that gives Firefox's `about:downloads` page a Mac OS 8.6 item-view field: a non-empty downloads list is white with black text, a square 1px black outline and the sunken `#999999` top-left shadow, every row is square, and a selected row is a flat `#CCCCFF` fill with black text. The empty-list state, the page background and text, each row's `.downloadButton` action button, the `#downloadsContextMenu` context menu and every other page stay Firefox's. This part ships and tests the sheet; the opt-in profile install is part 2/2, planned separately because extending the installer's atomic install/rollback and its tests is its own run.

**Grounding.** No reference screenshot shows Firefox chrome. The list face adapts the pinned white view background (`tests/test_colorscheme_reference.py::TestReferenceAnchors.test_window_view_background`) with the desktop theme's sunken field: `widgets/lineedit.svg`'s `#FFFFFF` face, `#000000` outline and `#999999` shadow (`tests/test_desktoptheme_lineedit.py::TestLineEdit.test_lineedit_face_is_white` and `test_lineedit_colours`), the same paint the Firefox sheet's `findbar .findbar-textbox` rule already applies. The selected row adapts the reference-grounded `widgets/listitem.svg`: flat `#CCCCFF`, square corners and no hover highlight (`tests/test_desktoptheme_listitem.py::TestListItem.test_listitem_selection_is_flat_selection_colour`, `test_listitem_normal_has_no_fill` and `test_listitem_hint_geometry`); `#CCCCFF` is the pinned `[Colors:Selection]` token (`tests/test_colorscheme_reference.py::TestReferenceAnchors.test_selection_background`).

In the installed Firefox ESR 153.5.1, `browser/omni.ja` `chrome/browser/content/browser/downloads/contentAreaDownloadsView.xhtml` defines `<window id="contentAreaDownloadsView">` around `<richlistbox id="downloadsListBox" class="allDownloadsListBox">`, and `chrome/browser/content/browser/downloads/allDownloadsView.js` builds each row as a `richlistitem` with the `download` and `download-state` classes. `chrome/browser/skin/classic/browser/downloads/allDownloadsView.inc.css` sets `#downloadsListBox > richlistitem { min-height: 4.5em }` and paints no row hover background, leaving the `.downloadButton` its own hover. `chrome/toolkit/skin/classic/global/richlistbox.css` paints `richlistbox` with `appearance: auto`, `background-color: Field`, `color: FieldText` and `border: 1px solid ThreeDShadow`, and paints `richlistitem[selected="true"]` with `-moz-cellhighlight`/`SelectedItem`; `chrome/browser/content/browser/downloads/contentAreaDownloadsView.css` makes an empty `#downloadsListBox` transparent. `browser/omni.ja` `defaults/preferences/firefox.js` sets `browser.tabs.remote.separatePrivilegedContentProcess` true, so about:downloads runs in a content process where `userContent.css` applies. A headless run of this ESR with a temporary profile whose `userContent.css` held `@-moz-document url("about:downloads") { #contentAreaDownloadsView { background-color: #FF0000 !important } }` rendered the page red, confirming both the URL match and the sheet's reach; declaration checks do not establish rendered list pixels.

**Approach.** Create `theme/firefox/org.macos8.desktop/chrome/userContent.css` with the marker first line `/* org.macos8.desktop Firefox content, standalone userContent.css` and a provenance header, then one at-rule containing three rules:

```css
@-moz-document url("about:downloads") {
  #contentAreaDownloadsView #downloadsListBox:not(:empty) {
    appearance: none !important;
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border: 1px solid #000000 !important;
    border-radius: 0 !important;
    box-shadow: inset 1px 1px #999999 !important;
  }

  #contentAreaDownloadsView #downloadsListBox > richlistitem {
    border-radius: 0 !important;
  }

  #contentAreaDownloadsView #downloadsListBox > richlistitem[selected] {
    background-color: #CCCCFF !important;
    color: #000000 !important;
  }
}
```

Square the rows directly rather than overriding a Firefox radius token, because the page shares no token with the chrome panels. The `:not(:empty)` guard leaves Firefox's transparent empty-list state; the list face's `appearance: none` and colours override the toolkit listbox paint, and a non-selected row keeps the white field because no row hover is added. Add no rule for the page background, `.downloadButton`, `#downloadsHistory`, `#downloadsListEmptyDescription` or `#downloadsContextMenu`; the context menu is a popup in the content document and stays Firefox's.

The header states: no reference shows Firefox's content-area downloads page; the field adapts `widgets/lineedit.svg` and the sheet's find-field paint, the row adapts `widgets/listitem.svg`, with the pinned anchors above; the installed ESR paths, selectors and the empty-list rule above; the `browser.tabs.remote.separatePrivilegedContentProcess` content-process basis and the headless `@-moz-document` render check; that declaration checks do not establish rendered pixels; and that this sheet is not installed until part 2/2 adds it to `make install-firefox`.

**Files touched.** New `theme/firefox/org.macos8.desktop/chrome/userContent.css`, new `tests/test_firefox_content_theme.py`, `docs/invariants.md`. README.md is untouched until part 2/2 makes the sheet installable.

**Acceptance criteria.**
- `tests/test_firefox_content_theme.py` reads the sheet with `support.gtk_css.parse_css`: the first line, with a UTF-8 BOM stripped, equals the marker above; the sheet's comments-stripped text names exactly one at-keyword, `@-moz-document`, whose prelude is exactly `url("about:downloads")` and whose block encloses every rule (no selector appears before or after it).
- The parsed rules are exactly the three selectors above, each equal to its `REQUIRED_RULES` entry built from `WHITE`, `BLACK`, `GREY` and `SELECTION` in `support.platinum_palette`; the list selector carries `:not(:empty)` and `border-radius: 0`; no rule is added for a non-selected row's hover, the empty-list description, a download button or the context menu.
- The test asserts the raw sheet's hex values are exactly `{WHITE, BLACK, GREY, SELECTION}` (comments included, as the userChrome palette test does), no selector contains `*`, and the sheet neither imports nor names Adwaita.
- A header-provenance test asserts the sheet's header contains `"No reference shows Firefox's"`, `"widgets/lineedit.svg"`, `"tests/test_desktoptheme_lineedit.py::TestLineEdit"`, `"widgets/listitem.svg"`, `"tests/test_desktoptheme_listitem.py::TestListItem"`, `"test_selection_background"`, `"chrome/browser/content/browser/downloads/contentAreaDownloadsView.xhtml"`, `"contentAreaDownloadsView"`, `"contentAreaDownloadsView.css"`, `"richlistbox.css"`, `"browser.tabs.remote.separatePrivilegedContentProcess"`, `"@-moz-document"`, `"platform colour adaptation 2026-10-26"` and `"part 2/2"`.
- `docs/invariants.md` gains a row in the `## firefox` table after the all-tabs row: the content-area downloads list (`#contentAreaDownloadsView #downloadsListBox`) is a non-empty white field with black text, a square 1px black outline and the sunken `#999999` top-left shadow, its rows are square and a selected row is flat `#CCCCFF` with black text, while the empty-list state, page background, row action buttons and context menu stay Firefox's; its test column names each test in the new module; its provenance records the missing Firefox content-area reference, the `widgets/lineedit.svg`/`widgets/listitem.svg` adaptations and pinned anchors, the installed ESR selectors and the content-process basis above, and that declaration checks do not establish rendered pixels.
- `make check` passes, and the existing `userChrome.css`, its install, and their tests keep their declarations (this part changes no existing file but `docs/invariants.md`).

## Done
