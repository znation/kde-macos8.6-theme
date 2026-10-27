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

### Firefox Platinum chrome: paint the notification doorhanger's primary button as a Platinum control (planned 2026-10-26 by the plan role; queued after the waiting bookmark-editor plan's `userChrome.css` edits)

**Goal.** Make the primary action button of Firefox's generic notification doorhanger read as Platinum: in `#notification-popup`, the `html:moz-button.popup-notification-primary-button` (`type="primary"`) becomes a square `#DDDDDD` face with a 1px black outline and a black label, and an enabled hovered or active one becomes a flat `#CCCCFF` face with black text and the same black outline. The secondary split/close button, the header, icon, description, checkbox, learn-more link, panel body and the `moz-button-group.panel-footer` wrapper stay Firefox's.

**Grounding.** No reference screenshot shows Firefox's notification doorhanger, so the paint adapts this theme's Platinum controls (platform colour adaptation 2026-10-26). The `#DDDDDD` face and 1px black outline adapt `widgets/button.svg` (`tests/test_desktoptheme_button.py::TestButton`), and the flat `#CCCCFF` hover adapts `widgets/viewitem.svg` (`tests/test_desktoptheme_viewitem.py::TestViewItem`, `tests/test_colorscheme_reference.py::TestReferenceAnchors::test_selection_background`). In the installed Firefox ESR 153.5.1, `chrome/toolkit/content/global/elements/popupnotification.js` renders the footer as an `html:moz-button-group.panel-footer` holding an `html:moz-button.popup-notification-secondary-button` (`type="split"`) and an `html:moz-button.popup-notification-primary-button` (`type="primary"`), `chrome/browser/content/browser/browser.xhtml` defines the `#notification-popup` arrow panel, and `chrome/browser/skin/classic/browser/browser-shared.css` gives the primary host a translucent grey face, white text and a small radius. `chrome/toolkit/content/global/elements/moz-button.css` paints the shadow-DOM `.button-background` from the `--button-background-color-primary*`, `--button-border`, `--button-border-color-primary*`, `--button-text-color-primary*` and `--button-border-radius` tokens, which `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` declares and whose radius defaults to `--border-radius-medium`; there is no inner-shadow or bevel token, so the raised white/`#AAAAAA` bevel is not reproduced and a flat face stands in (platform geometry adaptation 2026-10-26).

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, insert one rule immediately after the permission-popup rules and before the `menupopup > menuitem:hover` group:

```css
#notification-popup .popup-notification-primary-button {
  --button-background-color-primary: #DDDDDD !important;
  --button-background-color-primary-hover: #CCCCFF !important;
  --button-background-color-primary-active: #CCCCFF !important;
  --button-border: 1px solid !important;
  --button-border-color-primary: #000000 !important;
  --button-text-color-primary: #000000 !important;
  --border-radius-medium: 0 !important;
  background-color: transparent !important;
  color: #000000 !important;
  border-radius: 0 !important;
}
```

The host's transparent background exposes the arrow panel's existing `#DDDDDD` body; the shadow face's `--button-border-color-primary` is black in every state because Firefox's hover, active, selected and disabled border tokens default to it, so only the base token is set. Set `--border-radius-medium` rather than `--button-border-radius` so the permission-popup test's token-scope assertion keeps its empty set. Do not add a rule for the secondary split/close button, the `moz-button-group` footer, the header, icon, description, checkbox, learn-more link or panel body, and do not change `:root`, the arrow-panel token rules or any existing selector. In the header comment block, append a notification-doorhanger provenance paragraph immediately after the permission-popup paragraph (before the trust-panel paragraph): no reference shows Firefox's notification doorhanger; the flat `#DDDDDD`/`#CCCCFF` face with a 1px black outline adapts `widgets/button.svg` and `widgets/viewitem.svg` with the anchors above; `popupnotification.js` builds the `moz-button` footer, `browser.xhtml` defines `#notification-popup`, `browser-shared.css` paints the primary host, and `moz-button.css`/`tokens-shared.css` consume the `--button-*` tokens with no bevel token; declaration checks do not establish rendered pixels.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `REQUIRED_RULES` in `tests/test_firefox_theme.py` gains one entry, keyed `#notification-popup .popup-notification-primary-button` and inserted after the permission-popup entries and before the `menupopup > menuseparator` entries, whose declarations are exactly the ten above, with `FACE`, `SELECTION` and `BLACK` built from the constants the module already imports. `test_palette_is_exact` keeps its expected hex set unchanged because the rule introduces no new hex literal.
- New `TestFirefoxChrome.test_notification_popup_primary_button_paint_is_scoped_to_the_notification_popup`, placed immediately after `test_permission_popup_control_paint_is_scoped_to_the_permission_popup`, asserts the rule names containing `notification-popup` are exactly that selector, the rule equals its `REQUIRED_RULES` entry, no rule defines `--button-background-color`, `--button-border-color` or `--button-border-radius` exactly, and `--border-radius-medium` appears only on that selector. Using `support.selector_matching.element`/`matches`, build a `panel#notification-popup` (`popup-notification-panel`, `attrs={"type": "arrow"}`) with a `moz-button-group.panel-footer` holding `moz-button.popup-notification-primary-button` (`attrs={"type": "primary"}`) and `moz-button.popup-notification-secondary-button` (`attrs={"type": "split"}`); the primary matches with and without `hover`, while the secondary, the footer group, a plain `button` with that class, and the same primary classes under `#trustpanel-popup` match none.
- New `TestFirefoxChrome.test_notification_popup_provenance`, placed immediately after the scope test, asserts the leading comment names `"No reference shows Firefox's notification doorhanger"`, `"widgets/button.svg"`, `"tests/test_desktoptheme_button.py::TestButton"`, `"widgets/viewitem.svg"`, `"tests/test_desktoptheme_viewitem.py::TestViewItem"`, `"test_selection_background"`, `"#notification-popup"`, `"popup-notification-primary-button"`, `"popup-notification-secondary-button"`, `"popupnotification.js"`, `"browser.xhtml"`, `"browser-shared.css"`, `"moz-button.css"`, `"tokens-shared.css"`, `"--button-border"` and `"platform adaptation 2026-10-26"`. Leave `test_header_names_provenance_and_preference` untouched.
- `docs/invariants.md` gains a row inserted after the permission popup row and before the trust panel row in the `## firefox` table: the notification doorhanger's primary button (`#notification-popup .popup-notification-primary-button`) is a square `#DDDDDD` face with a 1px `#000000` outline and black label, and an enabled hovered or active one is flat `#CCCCFF` with black text, while the secondary split/close button, header, icon, description, checkbox, learn-more link, panel body and footer group stay Firefox's; its test column names the new scope test and its provenance records the missing notification-doorhanger reference, the `widgets/button.svg` and `widgets/viewitem.svg` anchors, the installed Firefox ESR 153.5.1 files and tokens above, the absent inner-shadow/bevel token, and that declaration checks do not establish rendered pixels. `tests/invariants.py` stays green.
- `make check` passes, and the existing sheet rules, the Firefox install and their tests keep their declarations and scope.

## Done
