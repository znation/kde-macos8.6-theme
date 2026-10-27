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


### Kvantum Platinum toolbox tabs: paint a QToolBox's tabs with the reference-grounded Platinum tab face (planned 2026-10-26 by the plan role; independent of the waiting downloads-panel-buttons chrome plan) — done 2026-10-26 by the feature role

**Goal.** Make a Qt toolbox's tabs read as Platinum. `org.macos8.desktop.kvconfig` defines no `[ToolboxTab]` section, so a `QToolBox` falls back to Kvantum's compiled-in tab paint instead of the reference-grounded tab face the config already draws for `[Tab]`. Add the section and point it at the existing `[Tab]` surface, so a toolbox's selected and unselected tabs use the same Platinum `#CCCCCC`/`#EEEEEE` tab art, 2px frame margin and 8px side text margins as the theme's tab bars.

**Grounding.** No reference screenshot shows a Qt `QToolBox`, so the `[ToolboxTab]` section name is Kvantum-required: the installed KvantumAlt theme defines `[ToolboxTab]` with `inherits=PanelButtonCommand` in `/usr/share/Kvantum/KvantumAlt/KvantumAlt.kvconfig`. Drawing it from the existing tab surface adapts the reference-grounded System Profiler tab face (`tests/test_kvantum_tab_reference.py::TestTabReference`) rather than introducing new art or a new palette value.

**Approach.** In `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`, insert the section immediately after `[Tab]` and before `[TabFrame]`, with `inherits=Tab` as its only key, and extend the container/text-surface comment paragraph to say tabs (including Qt toolbox tabs) draw the same raised Platinum face. In `tests/support/kvantum_config_spec.py`, add `"ToolboxTab": 2` to `CORE_FRAME_MARGINS` immediately after `"Tab"`, and add this entry to `SURFACE_CONTROL_CONFIG` immediately after `"Tab"`:

```python
"ToolboxTab": {
    "frame.element": "tab",
    "interior.element": "tab",
    "indicator.element": "tab",
},
```

No SVG, palette or value-key change: every mapping and margin resolves through `inherits=Tab` to the existing pinned values.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`, `tests/support/kvantum_config_spec.py`, `tests/test_kvantum_config_elements.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- The `.kvconfig` has exactly one `[ToolboxTab]` section, positioned between `[Tab]` and `[TabFrame]`, whose options are exactly `{"inherits": "Tab"}`; the container/text-surface comment names toolbox tabs.
- `CORE_FRAME_MARGINS` contains `"ToolboxTab": 2` and `SURFACE_CONTROL_CONFIG` contains the `"ToolboxTab"` mapping above. The existing `TestSectionCoverage.test_every_section_is_pinned`, `TestCoreControlElements.test_every_core_section_mapping_is_pinned`, `TestSurfaceElements.test_every_surface_section_maps_to_its_element`, `TestFrameMargins.test_every_core_section_resolves_to_the_expected_frame_margin` and `TestValueKeys.test_every_key_is_pinned` pass unchanged, because the new section adds no non-`inherits` key.
- New `TestToolboxTabSurface.test_toolbox_tab_inherits_the_tab_surface` in `tests/test_kvantum_config_elements.py`, placed after `TestSurfaceElements`, reads `KVCONFIG` through `support.kde_config.read` and asserts `parser.get("ToolboxTab", "inherits") == "Tab"`, `set(parser.options("ToolboxTab")) == {"inherits"}`, and that for `frame.element`, `interior.element`, `indicator.element`, the four `frame.*` margins and `text.margin.left`/`text.margin.right`, `_resolved(parser, "ToolboxTab", key)` equals `_resolved(parser, "Tab", key)`.
- `docs/invariants.md` gains a row in `## kvantum` immediately after the row beginning "The tab face is the reference System Profiler tabs'": the Qt toolbox tab (`[ToolboxTab]`) draws the same reference-grounded Platinum tab face as `[Tab]`, inheriting its frame, interior and indicator art, 2px frame margin and 8px side text margins. Its test column names `tests/test_kvantum_config_elements.py::TestToolboxTabSurface`, `tests/test_kvantum_config_elements.py::TestSurfaceElements`, `tests/test_kvantum_config.py::TestSectionCoverage` and `tests/test_kvantum_config.py::TestFrameMargins`; its provenance records that no reference screenshot shows a Qt QToolBox, that `[ToolboxTab]` is Kvantum-required (the installed KvantumAlt theme defines it), that the mapping adapts the reference-grounded tab face pinned by `tests/test_kvantum_tab_reference.py::TestTabReference`, and that config checks do not establish rendered Qt pixels. `tests/invariants.py` stays green.
- `README.md`: in the Kvantum paragraph's control list, add toolbox tabs alongside the toolbar buttons, toolbar combo boxes and line edits, split-button dropdowns, tree-view expanders and status bar that map onto the shipped Platinum art.
- `make check` passes, and every existing Kvantum section, element, frame-margin and palette assertion keeps its expected value.


### Firefox Platinum chrome: paint the Page Info dialog's view tabs and action buttons as Platinum controls (planned 2026-10-26 by the plan role; independent of the waiting Kvantum toolbox-tab plan)

**Goal.** Make Firefox's Page Info window read as Platinum: its top band (`#topBar`) becomes the grey `#DDDDDD` Platinum toolbar with the etched `#888888`/`#FFFFFF` bottom rule; its three view-tab states (`#viewGroup > radio`) become the sheet's Platinum tab faces — unselected raised `#DDDDDD` with black text, a square 1px black outline and the white/`#999999` bevel; selected flat `#EEEEEE` with its bottom border merged into the face; an unselected hovered tab flat `#EEEEEE`. Its plain action buttons — the `.help-button` in each panel, the media panel's `#selectallbutton`, `#imagesaveasbutton` and `#mediasaveasbutton`, and the security panel's `#security-view-qwac`, `#security-view-cert`, `#security-clear-sitedata` and `#security-view-password` — become square `#DDDDDD` push buttons with a black outline and the reference's white/`#AAAAAA` raised bevel; an enabled hovered one is flat `#CCCCFF` with black text and no bevel, while a disabled one keeps Firefox's disabled face. The dialog body, readonly `input` fields, meta/image trees, permission list, media preview, security tables, description labels, permission rows and focus rings stay Firefox's.

**Grounding.** No reference screenshot shows Firefox's Page Info window, so the paint adapts this theme's Platinum controls (platform adaptation 2026-10-26). The tab face and top band copy the sheet's existing `.tab-background` and `#nav-bar`/`#TabsToolbar` recipes: the raised face adapts the reference-grounded `widgets/tabbar.svg` (`tests/test_desktoptheme_tabbar.py::TestTabBar`, `tests/test_desktoptheme_tabbar.py::TestTabBarReference`), the `#EEEEEE` trough is the pinned `[Colors:View] BackgroundAlternate` (`tests/test_colorscheme_reference.py::TestReferenceAnchors::test_view_background_alternate`), and the etched pair is re-derived by `tests/test_desktoptheme_line.py::TestLineReference`. The push-button face, outline and white/`#AAAAAA` bevel adapt `widgets/button.svg` (`tests/test_desktoptheme_button.py::TestButton`, `tests/test_desktoptheme_button_reference.py::TestButtonReference`), and the flat `#CCCCFF` hover adapts `widgets/viewitem.svg` (`tests/test_desktoptheme_viewitem.py::TestViewItem`, `tests/test_colorscheme_reference.py::TestReferenceAnchors::test_selection_background`).

In the installed Firefox ESR 153.5.1, `chrome/browser/content/browser/pageinfo/pageInfo.xhtml` defines `vbox#topBar` holding `radiogroup#viewGroup.chromeclass-toolbar` with the `radio` tabs `#generalTab`, `#mediaTab` (hidden by default), `#permTab` and `#securityTab`; `deck#mainDeck` holds `#generalPanel`, `#mediaPanel`, `#permPanel` and `#securityPanel`; each panel ends in a `button.help-button` carrying `command="cmd_help"`, the media panel adds `#selectallbutton`, `#imagesaveasbutton` and `#mediasaveasbutton`, and the security panel adds `#security-view-qwac`, `#security-view-cert`, `#security-clear-sitedata` and `#security-view-password`. `chrome/browser/content/browser/pageinfo/pageInfo.js` selects a view by setting `selected` on its tab and swapping the deck, and `chrome/browser/skin/classic/browser/pageInfo.css` gives the non-macOS Linux build `#topBar` the Field background and ThreeDShadow bottom border and `#viewGroup > radio` `appearance: none`, a 4.5em minimum width, 3px padding and black `FieldText`, painting `#viewGroup > radio[selected]` with SelectedItem; the native anonymous radio glyph is already suppressed there. The sheet is loaded in every chrome document, so the new rules are scoped through the page-info-only ids `#topBar`, `#viewGroup` and `#mainDeck`. Declaration checks do not establish rendered pixels.

**Approach.** Append at the very end of `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, after the bookmark-editor rules, one short comment naming the adaptation and these rules, each selector on one line:

```css
#topBar {
  background-color: #DDDDDD !important;
  border-bottom: 1px solid #888888 !important;
  box-shadow: inset 0 -1px #FFFFFF !important;
}

#viewGroup > radio {
  appearance: none !important;
  background-color: #DDDDDD !important;
  color: #000000 !important;
  border: 1px solid #000000 !important;
  border-radius: 0 !important;
  box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #999999 !important;
}

#viewGroup > radio[selected] {
  background-color: #EEEEEE !important;
  border-bottom-color: #EEEEEE !important;
}

#viewGroup > radio:not([selected]):hover {
  background-color: #EEEEEE !important;
}

#mainDeck .help-button:not([disabled]),
#mainDeck #selectallbutton:not([disabled]),
#mainDeck #imagesaveasbutton:not([disabled]),
#mainDeck #mediasaveasbutton:not([disabled]),
#mainDeck #security-view-qwac:not([disabled]),
#mainDeck #security-view-cert:not([disabled]),
#mainDeck #security-clear-sitedata:not([disabled]),
#mainDeck #security-view-password:not([disabled]) {
  background-color: #DDDDDD !important;
  color: #000000 !important;
  border: 1px solid #000000 !important;
  border-radius: 0 !important;
  box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA !important;
}

#mainDeck .help-button:not([disabled]):hover,
#mainDeck #selectallbutton:not([disabled]):hover,
#mainDeck #imagesaveasbutton:not([disabled]):hover,
#mainDeck #mediasaveasbutton:not([disabled]):hover,
#mainDeck #security-view-qwac:not([disabled]):hover,
#mainDeck #security-view-cert:not([disabled]):hover,
#mainDeck #security-clear-sitedata:not([disabled]):hover,
#mainDeck #security-view-password:not([disabled]):hover {
  background-color: #CCCCFF !important;
  color: #000000 !important;
  box-shadow: none !important;
}
```

Leave the tabs' stock minimum width and padding in place and set no `outline`, so focus keeps Firefox's ring. Add no rule for the deck, panels, `input` fields, trees, permission list, media preview, security tables or labels, and do not change the `:root` block, the `.tab-background` rules or any existing selector. In the leading comment block, append a Page Info provenance paragraph before the closing `*/`: no reference shows Firefox's Page Info window; the tab and top band adapt `widgets/tabbar.svg` and the pinned `#EEEEEE` trough, and the buttons adapt `widgets/button.svg` and its white/`#AAAAAA` bevel, with the flat `#CCCCFF` hover from `widgets/viewitem.svg`; `pageInfo.xhtml` defines the ids, `pageInfo.js` swaps the deck and `pageInfo.css` owns the stock paint; declaration checks do not establish rendered pixels.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `userChrome.css` gains exactly the twenty selectors above (one `#topBar`, three `#viewGroup` tab rules, eight button rules and eight hover rules) and no other new selector. Every existing selector keeps its declarations.
- `REQUIRED_RULES` in `tests/test_firefox_theme.py` gains those twenty selectors, appended at the end of the dict and built from the constants the module already imports: `#topBar` is exactly `background-color: FACE !important`, `border-bottom: 1px solid ETCH_DARK !important` and `box-shadow: inset 0 -1px WHITE !important`; the base tab rule is exactly `appearance: none !important`, `background-color: FACE !important`, `color: BLACK !important`, `border: 1px solid BLACK !important`, `border-radius: 0 !important` and `box-shadow: RAISED_BEVEL !important`; the selected rule is exactly `background-color: TROUGH !important` and `border-bottom-color: TROUGH !important`; the hover rule is exactly `background-color: TROUGH !important`; each of the eight button selectors is exactly `background-color: FACE !important`, `color: BLACK !important`, `border: 1px solid BLACK !important`, `border-radius: 0 !important` and `box-shadow: BUTTON_BEVEL !important`; each of the eight hover selectors is exactly `background-color: SELECTION !important`, `color: BLACK !important` and `box-shadow: none !important`. `test_palette_is_exact` keeps its expected hex set unchanged because the rules introduce no new hex literal.
- New `TestFirefoxChrome.test_page_info_control_paint_is_scoped_to_page_info`, placed immediately before `test_readme_names_the_sheet`, asserts the rule names containing `#topBar`, `#viewGroup` or `#mainDeck` are exactly those twenty, each equals its `REQUIRED_RULES` entry, and the selected and hover rules do not paint the wrong state. Using `support.selector_matching.element`/`matches`, build a page-info tree: a window holding `vbox#topBar` with `radiogroup#viewGroup.chromeclass-toolbar` and the four `radio` tabs, and `deck#mainDeck` holding panels with a `.help-button`, the three media ids and the four security ids. Assert every tab matches the base rule, a selected tab matches the selected rule, a hovered unselected tab matches the hover rule, a selected hovered tab does not match the hover rule, each button matches its enabled selector and, when hovered, its hover selector but not when idle, and a disabled button matches neither. Assert the deck's `input#titletext`, `input#urltext`, `tree#metatree`, `tree#imagetree`, permission rows and labels match none of the twenty, and that an identically named `#selectallbutton` or `.help-button` outside `#mainDeck` and a `#navigator-toolbox` outside `#topBar` match none.
- New `TestFirefoxChrome.test_page_info_provenance`, placed immediately after the scope test, asserts the leading comment names `"No reference shows Firefox's Page Info window"`, `"widgets/tabbar.svg"`, `"tests/test_desktoptheme_tabbar.py::TestTabBar"`, `"tests/test_desktoptheme_tabbar.py::TestTabBarReference"`, `"tests/test_desktoptheme_line.py::TestLineReference"`, `"test_view_background_alternate"`, `"widgets/button.svg"`, `"tests/test_desktoptheme_button.py::TestButton"`, `"tests/test_desktoptheme_button_reference.py::TestButtonReference"`, `"widgets/viewitem.svg"`, `"tests/test_desktoptheme_viewitem.py::TestViewItem"`, `"test_selection_background"`, `"pageInfo.xhtml"`, `"pageInfo.js"`, `"pageInfo.css"`, `"#topBar"`, `"#viewGroup"`, `"#mainDeck"`, `"#generalTab"`, `"#selectallbutton"`, `"#security-view-qwac"` and `"platform adaptation 2026-10-26"`. Leave `test_header_names_provenance_and_preference` untouched so this plan and the waiting toolbox-tab plan do not edit the same tuple.
- `docs/invariants.md` gains a row appended at the end of the `## firefox` table, after the bookmark-editor row and before `## gtk`: the Page Info window's `#topBar` is the grey `#DDDDDD` Platinum toolbar with the etched `#888888`/`#FFFFFF` bottom rule, its `#viewGroup` view tabs are the Platinum tab faces (unselected raised `#DDDDDD` with black text, a square 1px black outline and the white/`#999999` bevel; selected flat `#EEEEEE` with the bottom border merged; unselected hovered flat `#EEEEEE`), and its `.help-button` and eight media/security action ids are square `#DDDDDD` push buttons with a black outline and the white/`#AAAAAA` bevel, an enabled hovered one being flat `#CCCCFF` with black text and no bevel, while a disabled button, the dialog body, fields, trees, permission list, media preview, security tables and labels stay Firefox's. Its test column names the new scope test, and its provenance records the missing Page Info reference, the `widgets/tabbar.svg`, `widgets/button.svg` and `widgets/viewitem.svg` anchors, the installed Firefox ESR 153.5.1 files above, and that declaration checks do not establish rendered pixels. `tests/invariants.py` stays green.
- `make check` passes, and the existing `userChrome.css` rules, the Firefox install and their tests keep their declarations and scope.

## Done
