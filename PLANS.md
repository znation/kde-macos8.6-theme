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

### Firefox Platinum chrome: paint the permission popup's clear buttons and permission dropdown as Platinum controls (planned 2026-10-26 by the plan role; independent of the landed protections-panel plan)

**Goal.** Make Firefox's permission popup (`#permission-popup`, the site-permissions panel whose rows show a site's granted permissions) read as Mac OS 8.6 chrome: each row's clear-permission button (`button.permission-popup-permission-remove-button`) is a square `#DDDDDD` push button with a 1px black outline and the reference push button's raised white/`#AAAAAA` bevel, and an enabled one under the pointer is flat `#CCCCFF` with black text and no bevel; the popup/autoplay permission dropdown (`#permission-popup-menulist`) wears the same square face, outline, bevel and hover. The permission rows (`hbox.permission-popup-permission-item`), their icons, name labels, state labels and remove-button boxes, the storage-access hint and learn-more link, the panel header, the separator, the reload hint and the panel body stay Firefox's.

**Grounding.** No reference screenshot shows Firefox chrome or its permission popup. The control art adapts the reference-grounded `widgets/button.svg`: its normal/pressed push button has a `#DDDDDD` face, a 1px `#000000` outline, a `#FFFFFF` top/left highlight and the reference's `#AAAAAA` bottom/right shadow (`tests/test_desktoptheme_button.py::TestButton`, `tests/test_desktoptheme_button_reference.py::TestButtonReference`). The hover fill and black text adapt the reference-grounded `widgets/viewitem.svg` and the sheet's menu-item mapping, with `#CCCCFF` pinned by `tests/test_desktoptheme_viewitem.py::TestViewItem` and `tests/test_colorscheme_reference.py::TestReferenceAnchors::test_selection_background`.

In the installed Firefox ESR 153.5.1, `browser/omni.ja` `chrome/browser/content/browser/browser.xhtml` defines `<html:template id="template-permission-popup">` with `<panel id="permission-popup" class="panel-no-padding">`, its `#permission-popup-multiView`, the `#permission-popup-mainView` panelview whose `#permission-popup-mainView-panel-header` is a plain `.panel-header` (an `html:h1` around `#permission-popup-mainView-panel-header-span`), a `toolbarseparator`, and the `#permission-popup-permission-list` that holds `#permission-popup-permission-list-default-anchor`, the `anchorfor="3rdPartyStorage"` anchor, `#permission-popup-storage-access-permission-list-header` (`.permission-popup-permission-header-label`), `#permission-popup-storage-access-permission-learn-more`, and `#permission-popup-permission-reload-hint`. `chrome/browser/content/browser/browser-sitePermissionPanel.js` `_createPermissionItem` builds each row as an `hbox.permission-popup-permission-item` holding a `.permission-popup-permission-icon`, a `.permission-popup-permission-label` and either a `#permission-popup-menulist` (for `popup` and `autoplay-media`, disabled when the popup preference is locked) or a `.permission-popup-permission-state-label` and the `button.permission-popup-permission-remove-button` built by `_createPermissionClearButton`. `chrome/browser/skin/classic/browser/controlcenter/panel.css` owns the popup layout, gives the remove button `var(--button-background-color)`, `var(--button-border)` and `var(--button-border-radius)` plus a `:hover`/`:hover:active` recolour, and gives `#permission-popup-menulist` its padding and locked-state dimming; `chrome/toolkit/skin/classic/global/button.css` supplies the plain XUL button's `ButtonFace`/`ButtonBorder` paint, `chrome/toolkit/skin/classic/global/menulist.css` gives the non-native menulist host its `--button-background-color`, `--button-border-radius` and hover/active recolour, and `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` declares those button tokens. Nothing in the sheet targets `#permission-popup`, so today the remove button and dropdown keep Firefox's rounded control paint.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, after the all-tabs rules and before the global `menupopup > menuitem:hover` rule, add four rules with a short comment (each selector on one line so the parsed text matches the test's expectation):

```css
#permission-popup .permission-popup-permission-remove-button {
  background-color: #DDDDDD !important;
  color: #000000 !important;
  border: 1px solid #000000 !important;
  border-radius: 0 !important;
  box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA !important;
}

#permission-popup .permission-popup-permission-remove-button:hover:not([disabled]) {
  background-color: #CCCCFF !important;
  color: #000000 !important;
  box-shadow: none !important;
}

#permission-popup-menulist {
  background-color: #DDDDDD !important;
  color: #000000 !important;
  border: 1px solid #000000 !important;
  border-radius: 0 !important;
  box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA !important;
}

#permission-popup-menulist:hover:not([disabled]) {
  background-color: #CCCCFF !important;
  color: #000000 !important;
  box-shadow: none !important;
}
```

Paint the controls directly rather than overriding `--button-background-color`, `--button-border-color` or `--button-border-radius`, because those tokens paint every Firefox button and menulist. The `:hover:not([disabled])` rules override the stock `panel.css` and menulist `:host` hover/active paint through the user-origin `!important` declarations and keep a locked popup dropdown's dimmed state (Firefox's `[disabled]` opacity and no-pointer rule is left alone). Add no rule for the row containers, labels, state labels, icons, the storage-access link or hint, the header, the separator or the panel body, and do not change the `#appMenu-popup`, `#widget-overflow`, `#allTabsMenu-allTabsView`, `#unified-extensions-panel`, `#identity-popup` or `#protections-popup` selectors.

In the header comment block, append a provenance paragraph after the site-information paragraph and before the closing `*/`: no reference shows Firefox's permission popup; the control art adapts `widgets/button.svg` and the `#AAAAAA` bevel reference (citation above) and the flat `#CCCCFF` row mapping (platform colour adaptation 2026-10-26); `chrome/browser/content/browser/browser.xhtml` defines `template-permission-popup`, `chrome/browser/content/browser/browser-sitePermissionPanel.js` builds the rows and buttons via `_createPermissionItem` and `_createPermissionClearButton`, `chrome/browser/skin/classic/browser/controlcenter/panel.css` owns the permission-popup layout and control paint, `chrome/toolkit/skin/classic/global/button.css` and `chrome/toolkit/skin/classic/global/menulist.css` supply the stock button and menulist paint, and `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` declares the `--button-background-color` and `--button-border-radius` tokens; the sheet paints only the remove button and the permission menulist, leaving the rows, labels, icons, header, separator and panel body Firefox's; declaration checks do not establish rendered pixels.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `REQUIRED_RULES` in `tests/test_firefox_theme.py` gains the four selectors above (one entry each), using the existing `FACE`, `BLACK`, `SELECTION` and `WHITE` constants and `BUTTON_BEVEL` (import it from `support.gtk_theme_spec`): each normal control has `background-color: FACE`, `color: BLACK`, `border: 1px solid BLACK`, `border-radius: 0` and `box-shadow: BUTTON_BEVEL`; each hover control has `background-color: SELECTION`, `color: BLACK` and `box-shadow: none`, all with `!important`.
- New `TestFirefoxChrome.test_permission_popup_control_paint_is_scoped_to_the_permission_popup` asserts the selectors naming `permission-popup` are exactly those four, each starts with `#permission-popup`, each equals its `REQUIRED_RULES` entry, the normal rules carry no `:hover`, both hover rules carry `:hover` and `:not([disabled])`, and no rule in the sheet defines `--button-background-color`, `--button-border-color` or `--button-border-radius`. Using `support.selector_matching.matches`, a remove button inside `#permission-popup` and `#permission-popup-menulist` each match both their rules, their `[disabled]` and non-hover forms match only the normal rule, and a row `hbox.permission-popup-permission-item`, a `.permission-popup-permission-icon`, a `.permission-popup-permission-label`, a `.permission-popup-permission-state-label`, the `.panel-header` box, its `html:span`, the `toolbarseparator` and the storage-access `moz-support-link` each match neither rule; a same-class remove button outside `#permission-popup` and a menulist with another id each match neither rule.
- `test_header_names_provenance_and_preference` gains the strings `"No reference shows Firefox's permission popup"`, `"widgets/button.svg"`, `"tests/test_desktoptheme_button.py::TestButton"`, `"tests/test_desktoptheme_button_reference.py::TestButtonReference"`, `"widgets/viewitem.svg"`, `"tests/test_desktoptheme_viewitem.py::TestViewItem"`, `"test_selection_background"`, `"chrome/browser/content/browser/browser.xhtml"`, `"template-permission-popup"`, `"chrome/browser/content/browser/browser-sitePermissionPanel.js"`, `"_createPermissionItem"`, `"_createPermissionClearButton"`, `"chrome/browser/skin/classic/browser/controlcenter/panel.css"`, `"permission-popup-permission-remove-button"`, `"permission-popup-menulist"`, `"chrome/toolkit/skin/classic/global/button.css"`, `"chrome/toolkit/skin/classic/global/menulist.css"`, `"chrome/toolkit/skin/classic/global/design-system/tokens-shared.css"`, `"--button-background-color"`, `"--button-border-radius"` and `"platform colour adaptation 2026-10-26"`.
- `docs/invariants.md` gains a row in the `## firefox` table after the site-information row (after the protections-panel row once that plan has landed): the permission popup's clear button and permission menulist are square `#DDDDDD` controls with a black outline and the reference's white/`#AAAAAA` raised bevel, and an enabled hovered one is flat `#CCCCFF` with black text and no bevel, while the permission rows, labels, icons, header, separator and panel body stay Firefox's; its test column names the new test, and its provenance records the missing Firefox permission-popup reference, the `widgets/button.svg` bevel with the pinned anchors, the installed Firefox ESR 153.5.1 files and symbols above, and that declaration checks do not establish rendered pixels. `tests/invariants.py` stays green.
- `make check` passes, and the existing sheet rules, the install and their tests keep their declarations and scope.

## Done
