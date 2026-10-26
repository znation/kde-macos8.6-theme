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

### Kvantum Platinum size grip: draw the reference's grow-box diamond (planned 2026-10-26 by the plan role; independent of the Firefox site-information panel plan)

**Goal.** Make a Qt size grip (`QSizeGrip`, which Kvantum draws from its `[SizeGrip]` section) read as a Mac OS 8.6 grow box. `org.macos8.desktop.kvconfig` defines no `[SizeGrip]` section, so a KDE/Qt window's bottom-right resize grip falls back to Kvantum's compiled-in art instead of the Platinum grow box the reference windows show. Add the section and draw its indicator from the reference: a white and `#777777` checker diamond with the three `#AAAAAA` pixels the reference shows along its lower-left edge, with a transparent surround so the grip sits on whatever face the widget draws.

**Grounding.** No reference screenshot shows a KDE/Qt size grip, so the section and element names are Kvantum-required and the art adapts the grow box in a reference window. In `macos8.6-screenshots/systemprofiler_betawiki.png` (the retail Japanese 8.6 System Profiler window whose tabs already ground `test_kvantum_tab_reference.py`), the window's bottom-right grow box occupies the 12x11 rectangle x=796..807, y=748..758 on the window-frame `#CCCCCC` face. Its 132 pixels are 90 `#CCCCCC`, 21 `#FFFFFF`, 18 `#777777` and three `#AAAAAA` (at 797/754, 799/756 and 801/758); the diamond's non-background pixels are the pinned pattern. `#777777` is a new sampled fill, so add `SIZEGRIP_DARK = "#777777"` to `tests/support/platinum_palette.py`; the `#AAAAAA` edge pixels reuse the existing `BUTTON_SHADOW` value already allowed by `TestSvg.test_uses_exactly_the_platinum_palette`. The installed Kvantum themes ship `[SizeGrip]` with only `indicator.element=sizegrip` (for example `/usr/share/Kvantum/KvantumAlt/KvantumAlt.kvconfig`) or `indicator.element=resize-grip`, and name the art `<element>-normal`/`<element>-focused`; `[SizeGrip]` and those state suffixes are Kvantum-required. The reference's `#CCCCCC` is the surrounding window frame, not part of the indicator, so the shipped art draws no background rect.

**Approach.**
- In `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`, after `[HeaderSection]`, add `[SizeGrip]` with the single setting `indicator.element=sizegrip` and a short comment naming the provenance exception (no reference shows a KDE/Qt size grip; the art adapts the window grow box, platform adaptation 2026-10-26).
- In `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`, after the branch arrows, add `sizegrip-normal` and `sizegrip-focused` groups, each with one 1x1 `<rect>` for every non-`#CCCCCC` pixel of the sampled 12x11 region, at that pixel's relative coordinate and with that pixel's sampled fill (`#FFFFFF`, `#777777` or `#AAAAAA`). Ship no rect for the 90 background pixels. Put the groups at the next two 60px slots and raise the root canvas height by 120. Update the header comment to name the sampled grow box, its origin and the three fills.
- In `tests/support/kvantum_config_spec.py`, add `"SizeGrip": {"indicator.element": "sizegrip"}` to `FRAMELESS_SECTIONS` so `test_every_section_is_pinned`, `test_every_frameless_section_resolves_its_pins` and `test_every_key_is_pinned` cover the new section and setting.
- In `tests/support/platinum_palette.py`, add the sampled `SIZEGRIP_DARK` constant with a comment naming the reference and its pixel anchors.
- In `tests/test_kvantum_svg.py`, add `sizegrip` to the palette test's `extra` set through `SIZEGRIP_DARK` (the `#AAAAAA` fill is already covered by `BUTTON_SHADOW`), and add a test that both `sizegrip-normal` and `sizegrip-focused` exist and that every child of each group is a 1x1 rect at a distinct coordinate with a fill from the three sampled values.
- Add `tests/test_kvantum_sizegrip_reference.py`. It uses `ReferenceScreenshotMixin` with `REFERENCE = PROFILER_REFERENCE`, its own `MAX_ROWS = 760` (the grow box is below `PROFILER_ROWS`' 256), and the origin/width/height constants above. One test re-derives the 12x11 reference region and asserts its exact colour map (including the three `#AAAAAA` pixels) and the `#CCCCCC` corner. A second test composes the shipped `sizegrip-normal` and `sizegrip-focused` rects onto the sampled `#CCCCCC` background and asserts both maps equal the reference map, so a hand-drawn symmetric diamond, a missing edge pixel, a wrong fill or a stray background rect fails.
- `README.md`: in the Kvantum paragraph, add that a Qt size grip draws the reference grow box's white/`#777777` diamond.
- `docs/invariants.md`: add a `## kvantum` row: the size grip draws the reference grow box's 12x11 diamond on a transparent surround, with the three sampled fills, while the section has no frame or interior; its test column names `tests/test_kvantum_sizegrip_reference.py::TestSizeGripReference` and `tests/test_kvantum_svg.py::TestSvg`, and its provenance records that no reference screenshot shows a KDE/Qt size grip, the art adapts the window grow box in `systemprofiler_betawiki.png` at x=796..807, y=748..758 (platform adaptation 2026-10-26), the `#777777`/`#AAAAAA` fills, and that SVG checks do not establish rendered Qt pixels. `tests/invariants.py` stays green.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`, `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`, `tests/support/kvantum_config_spec.py`, `tests/support/platinum_palette.py`, `tests/test_kvantum_svg.py`, `tests/test_kvantum_sizegrip_reference.py`, `README.md`, `docs/invariants.md`.

**Acceptance criteria.**
- `[SizeGrip]` resolves `indicator.element` to `sizegrip` and declares no frame, interior or other unpinned setting; `TestSectionCoverage` and `TestValueKeys` pin it through `FRAMELESS_SECTIONS`.
- `sizegrip-normal` and `sizegrip-focused` each exist and contain one 1x1 rect per non-background reference pixel (42 rects), with no two rects at the same coordinate and no background rect; their fills are exactly `#FFFFFF`, `#777777` and `#AAAAAA`.
- `TestSizeGripReference.test_reference_grow_box_pattern` re-derives the 12x11 region and asserts the 90 `#CCCCCC`, 21 `#FFFFFF`, 18 `#777777` and three `#AAAAAA` pixels at their coordinates (including 797/754, 799/756 and 801/758).
- `TestSizeGripReference.test_shipped_size_grip_paints_the_reference_pattern` composes both shipped state groups onto the sampled background and asserts each equals the reference pixel map; a symmetric white/`#777777` diamond without the edge pixels, a misplaced pixel or a re-coloured fill fails.
- `TestSvg.test_uses_exactly_the_platinum_palette` accepts `SIZEGRIP_DARK`, and `TestSvg` pins both size-grip states and their 1x1-rect children.
- `docs/invariants.md` carries the new `## kvantum` row with its test columns and provenance, and `tests/invariants.py` is green.
- `make check` passes, and the existing Kvantum config, palette, SVG and reference tests keep their assertions.

### Firefox Platinum chrome: paint the protections panel rows like a Platinum menu (planned 2026-10-26 by the plan role; independent of the waiting Kvantum size-grip plan)

**Goal.** Make Firefox's protections panel (`#protections-popup`, the shield menu that shows the site's tracking-protection state and blocked categories) read as a Mac OS 8.6 menu: each `.subviewbutton` row is square, and an enabled one under the pointer takes the flat `#CCCCFF` fill with black text and no toolbar bevel. The panel header (including PanelMultiView's generated back buttons), the tracking-protection toggle, the dynamically built tracker/cookie list rows, separators, icons and the panel body stay Firefox's.

**Grounding.** No reference screenshot shows Firefox chrome or its protections panel. The row fill adapts the reference-grounded `widgets/viewitem.svg`, whose `hover`/`selected`/`selected+hover` slices are each a flat square `#CCCCFF` with no bevel or outline (`tests/test_desktoptheme_viewitem.py::TestViewItem`), and reuses the sheet's existing menu-item mapping (`menupopup > menuitem:hover`). `#CCCCFF` is the project's sampled `[Colors:Selection]` token pinned by `tests/test_colorscheme_reference.py::TestReferenceAnchors::test_selection_background`.

In the installed Firefox ESR 153.5.1, `browser/omni.ja` `chrome/browser/content/browser/browser.xhtml` defines `<html:template id="template-protections-popup">` with `<panel id="protections-popup" class="panel-no-padding">`, its `<panelmultiview id="protections-popup-multiView" mainViewId="protections-popup-mainView">`, the main `<panelview id="protections-popup-mainView" class="PanelUI-subView" mainview-with-header="true" has-custom-header="true">`, and the custom header `<box id="protections-popup-mainView-panel-header" class="panel-header panel-header-with-additional-element panel-header-with-info-button">` holding `#protections-popup-info-button` (class `panel-info-button`) and the two toast buttons. The main view's `<vbox id="protections-popup-main-body" class="panel-subview-body">` holds `#protections-popup-tp-switch` (`html:moz-toggle`), `#protections-popup-report-broken-site-button` (`.subviewbutton .subviewbutton-nav`, `disabled` by default) and `#protections-popup-category-list` with the category rows `#protections-popup-category-trackers`, `-socialblock`, `-cookies`, `-cryptominers` and `-fingerprinters` (each `.protections-popup-category .subviewbutton .subviewbutton-iconic`); the footer `<vbox id="protections-popup-footer" class="panel-subview-footer-button">` holds `#protections-popup-settings-button` and `#protections-popup-show-report-button` (`.subviewbutton .protections-popup-footer-button`), and the same view holds `#protections-popup-milestones-content` (`.subviewbutton`) and `#protections-popup-cookie-banner-switch` (`.subviewbutton .subviewbutton-nav`). The trackers/cookies/social-block subviews each hold a `#protections-popup-<name>View` panelview whose footer is a `.subviewbutton .panel-subview-footer-button` (for example `#protections-popup-trackersView-settings-button`). `chrome/browser/content/browser/browser-siteProtections.js` builds each tracker/cookie list row as an HTML `<div class="protections-popup-list-item">` (with no `.subviewbutton`), marks undetected categories `disabled`, and the CSS hides `[uidisabled]` rows. `moz-src/browser/components/customizableui/PanelMultiView.sys.mjs` builds a subview header's back button with `subviewbutton subviewbutton-iconic subviewbutton-back` inside a `.panel-header`. `chrome/browser/skin/classic/browser/controlcenter/panel.css` owns the protections panel layout and its category/footer hover paint; `chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css` gives `.subviewbutton` `border-radius: var(--panel-menuitem-border-radius)` and the ghost hover tokens `--button-text-color-ghost-hover` / `--button-background-color-ghost-hover`; `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` defines `--panel-menuitem-border-radius`. The sheet's generic `toolbarbutton:hover:not([disabled="true"])` adds the raised bevel, and nothing in the sheet targets `#protections-popup`, so today a row keeps Firefox's violet wash and rounded corners and the footer rows keep the toolbar bevel.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, after the site-information panel rules and before the all-tabs comment, add two rules with a short comment (each selector on one line so the parsed text matches the test's expectation):

```css
#protections-popup .subviewbutton:not(.panel-header .subviewbutton) {
  border-radius: 0 !important;
}

#protections-popup .subviewbutton:not(.panel-header .subviewbutton):hover:not([disabled]) {
  background-color: #CCCCFF !important;
  color: #000000 !important;
  box-shadow: none !important;
}
```

Square the rows directly rather than overriding `--panel-menuitem-border-radius`, because that token is shared with the app-menu, overflow, all-tabs, unified-extensions and identity rows. The `.subviewbutton` selector covers the report-broken-site row, the five category rows, the milestones and cookie-banner rows, the two footer rows and each subview's footer row. Excluding `.panel-header .subviewbutton` leaves PanelMultiView's generated back buttons Firefox's. The hover rule excludes disabled rows (including the not-found categories the script marks `disabled`) and paints while `:active` too, so it out-specifies the stock category/footer hover and the generic toolbar bevel. Add no rule for the `moz-toggle` tracking switch, the header info button, the `.protections-popup-list-item` tracker rows, separators, icons or the panel body. Do not change the `#appMenu-popup`, `#widget-overflow`, `#allTabsMenu-allTabsView`, `#unified-extensions-panel` or `#identity-popup` selectors.

In the header comment block, append a provenance paragraph after the site-information paragraph and before the closing `*/`: no reference shows Firefox's protections panel; the row fill adapts `widgets/viewitem.svg` and the sheet's menu-item mapping (platform colour adaptation 2026-10-26); `chrome/browser/skin/classic/browser/controlcenter/panel.css` owns the protections panel layout and its category/footer hover, `chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css` gives `.subviewbutton` its `--panel-menuitem-border-radius` and ghost hover, `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` defines those tokens, `chrome/browser/content/browser/browser.xhtml` defines the `template-protections-popup` elements above, `chrome/browser/content/browser/browser-siteProtections.js` builds the `.protections-popup-list-item` rows and disables undetected categories, and `moz-src/browser/components/customizableui/PanelMultiView.sys.mjs` creates the `.panel-header` back button; the sheet squares and recolours the `.subviewbutton` rows only, leaving the header, the `moz-toggle` switch, the tracker list rows, separators and the panel body Firefox's; declaration checks do not establish rendered pixels.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `REQUIRED_RULES` in `tests/test_firefox_theme.py` gains the two selectors above (one entry each): the square selector with `border-radius: 0 !important`, the hover selector with `background-color: #CCCCFF !important` (via `SELECTION`), `color: #000000 !important` (via `BLACK`) and `box-shadow: none !important`.
- New `TestFirefoxChrome.test_protections_popup_row_paint_is_scoped_to_the_protections_popup` asserts the selectors naming `protections-popup` are exactly those two, each starts with `#protections-popup`, each equals its `REQUIRED_RULES` entry, the square selector carries no declaration besides `border-radius`, the hover selector carries `:hover` and `:not([disabled])`, both exclude `.panel-header .subviewbutton`, and no rule in the sheet overrides `--panel-menuitem-border-radius`. Using `support.selector_matching.matches`, a category row, `#protections-popup-report-broken-site-button`, `#protections-popup-settings-button`, `#protections-popup-milestones-content`, `#protections-popup-cookie-banner-switch` and a trackers-subview footer button each match both rules; a disabled such row matches neither hover rule; a `.panel-header` back `toolbarbutton.subviewbutton.subviewbutton-iconic.subviewbutton-back`, `#protections-popup-info-button` (`panel-info-button`), the `html:moz-toggle#protections-popup-tp-switch`, a `div.protections-popup-list-item` and a `toolbarbutton.toolbarbutton-1` under `#nav-bar` each match neither rule.
- `test_header_names_provenance_and_preference` gains the strings `"No reference shows Firefox's protections panel"`, `"widgets/viewitem.svg"`, `"tests/test_desktoptheme_viewitem.py::TestViewItem"`, `"test_selection_background"`, `"chrome/browser/skin/classic/browser/controlcenter/panel.css"`, `"chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css"`, `"chrome/browser/content/browser/browser.xhtml"`, `"chrome/browser/content/browser/browser-siteProtections.js"`, `"moz-src/browser/components/customizableui/PanelMultiView.sys.mjs"`, `"#protections-popup"`, `"protections-popup-mainView-panel-header"`, `"protections-popup-main-body"`, `"protections-popup-category-trackers"`, `"protections-popup-report-broken-site-button"`, `"protections-popup-settings-button"`, `"protections-popup-milestones-content"`, `"protections-popup-cookie-banner-switch"`, `"protections-popup-list-item"`, `"subviewbutton-back"`, `"--panel-menuitem-border-radius"`, `"--button-background-color-ghost-hover"` and `"platform colour adaptation 2026-10-26"`.
- `docs/invariants.md` gains a row in the `## firefox` table after the site-information row: the protections panel rows (`#protections-popup .subviewbutton` outside `.panel-header`) are square, and an enabled hovered row is flat `#CCCCFF` with black text and no toolbar bevel, while the generated back buttons, the `moz-toggle` tracking switch, the `.protections-popup-list-item` tracker rows, the header, separators and panel body stay Firefox's; its test column names the new test, and its provenance records the missing Firefox protections-panel reference, the `widgets/viewitem.svg` and menu-item mapping with the pinned anchors, the installed Firefox ESR 153.5.1 files, elements and tokens above, and that declaration checks do not establish rendered pixels. `tests/invariants.py` stays green.
- `make check` passes, and the existing sheet rules, the install and their tests keep their declarations and scope.

## Done
