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

### Firefox Platinum chrome: paint the Page Info media preview like a Platinum sunken field (planned 2026-10-26 by the plan role; independent of the waiting Page Info permission-list plan — both append at the very end of `userChrome.css`, insert their provenance paragraphs before the header's closing `*/` and trim only their own word from the shared stay-Firefox lists, so either order merges)

**Goal.** Make the Media panel's preview pane read as a Platinum sunken field: the `vbox#imagecontainerbox` container — the pane holding the embedded preview and the broken-image placeholder — becomes the opaque `#FFFFFF` field the deck's display fields use, with square corners, a 1px `#000000` outline, the `inset 1px 1px #999999` top-left shadow and black text, replacing Firefox's `Field` background and `1px ThreeDLightShadow` border. The pane is a static preview surface, so there is no hover, focus or selected variant. The embedded `browser#mediaBrowser`, the `hbox#brokenimagecontainer`/`image#brokenimage` placeholder, the media table's inputs (already covered by the landed `#mainDeck input` rule), the save buttons, the pane's stock `margin: 0.5em` and `overflow: auto` and all geometry stay Firefox's. The deck's trees, permission list, display fields, security tables and the landed top-bar, tab and button paints are untouched.

**Grounding.** No reference screenshot shows Firefox's Page Info media preview, so the paint adapts this theme's Platinum line-edit field (platform colour adaptation 2026-10-26). The `#FFFFFF` face, 1px `#000000` outline, `#999999` sunken shadow and black text adapt `widgets/lineedit.svg` (`tests/test_desktoptheme_lineedit.py::TestLineEdit` and `TestLineEditReference`), grounded in `macos8.6-screenshots/firstboot_betawiki.png`, and are the exact recipe the sheet's landed `#mainDeck input` rule already ships; `#imagecontainerbox` is the deck's preview-shaped surface, so the same field recipe applies. In the installed Firefox ESR 153.5.1, `chrome/browser/content/browser/pageinfo/pageInfo.xhtml` defines `vbox#imagecontainerbox` (flex child of `vbox#mediaPreviewBox` in the Media panel) holding `hbox#theimagecontainer` with `browser#mediaBrowser` and collapsed `hbox#brokenimagecontainer` with `image#brokenimage`; `chrome/browser/skin/classic/browser/pageInfo.css` gives it `margin: 0.5em`, a `Field` background, `overflow: auto` and a `1px solid ThreeDLightShadow` border with no `-moz-default-appearance`, so the CSS declarations override the stock paint with no `appearance` declaration needed; the content copy `chrome/browser/content/browser/pageinfo/pageInfo.css` only sets its `min-width`/`min-height`. `#imagecontainerbox` appears only in page-info files, so the rule cannot leak into browser chrome. Declaration checks do not establish rendered pixels.

**Approach.** Append at the very end of `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, after the `#mainDeck input` rule, one short comment naming the adaptation and this rule:

```css
#imagecontainerbox {
  background-color: #FFFFFF !important;
  color: #000000 !important;
  border: 1px solid #000000 !important;
  border-radius: 0 !important;
  box-shadow: inset 1px 1px #999999 !important;
}
```

Keep the stock `margin: 0.5em` and `overflow: auto` and every child's own paint. Add no rule for `#mediaPreviewBox`, `#theimagecontainer`, `#mediaBrowser`, `#brokenimagecontainer`, `#brokenimage`, `#mediaTable`, the media panel's labels, inputs or buttons, and change no existing selector. In the header comment block, insert a media-preview provenance paragraph immediately before the closing `*/`: no reference shows Firefox's Page Info media preview; the `#FFFFFF` face, 1px `#000000` outline, `#999999` sunken shadow and black text adapt `widgets/lineedit.svg` (grounded in `firstboot_betawiki.png` and pinned by `tests/test_desktoptheme_lineedit.py::TestLineEdit` and `TestLineEditReference`) and reuse the landed `#mainDeck input` recipe; `pageInfo.xhtml` defines the pane holding `#mediaBrowser` and the `#brokenimagecontainer` placeholder and the skin's `pageInfo.css` owns the stock `Field` background and `ThreeDLightShadow` border; declaration checks do not establish rendered pixels (platform colour adaptation 2026-10-26). Also trim the words `media preview` from the stay-Firefox surface lists in the two existing Page Info texts — the header's top-bar provenance paragraph ("…the dialog body, meta and image trees, permission list, media preview, security tables, description labels and focus rings stay Firefox's…") and the `#topBar` rule's leading comment ("…the dialog body, fields, trees, permission list, media preview, security tables and labels keep Firefox's own paint…") — leaving every other word of both lists unchanged (the waiting permission-list plan trims `permission list` from the same sentences; whichever lands first, the other's word is still present to trim).

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `userChrome.css` gains exactly one new selector, `#imagecontainerbox`, carrying exactly the five declarations above; every existing selector keeps its declarations, and `test_palette_is_exact` keeps its expected hex set because the rule introduces no new hex literal (the constants the rules already use only).
- `REQUIRED_RULES` in `tests/test_firefox_theme.py` gains, appended immediately after the `REQUIRED_RULES["#mainDeck input"]` assignment, `REQUIRED_RULES["#imagecontainerbox"]` mapping to `background-color: {WHITE} !important`, `color: {BLACK} !important`, `border: 1px solid {BLACK} !important`, `border-radius: 0 !important` and `box-shadow: inset 1px 1px {GREY} !important`, using the constants `support.platinum_palette` already exports.
- New `TestFirefoxChrome.test_page_info_media_preview_paint_is_scoped_to_page_info`, placed immediately after `test_page_info_field_paint_is_scoped_to_page_info`: asserts `self.rules["#imagecontainerbox"]` equals its `REQUIRED_RULES` entry. Using `support.selector_matching.element`/`matches`, build `window` holding `deck#mainDeck` with `vbox#mediaPreviewBox`, inside it `vbox#imagecontainerbox` holding `hbox#theimagecontainer` with `browser#mediaBrowser` and `hbox#brokenimagecontainer` with `image#brokenimage`. Assert the container matches with and without `hover: true` (no hover or focus variant), `#mediaBrowser` and `#brokenimage` match no selector whose name contains `imagecontainerbox`, and stray surfaces — a `textbox` in the findbar, `input#editBMPanel_locationField`, `input#searchbar-textbox` and `input#urltext` — match none of the rule names containing `imagecontainerbox`. Assert the rule names containing `imagecontainerbox` are exactly `["#imagecontainerbox"]`, and that no `"#imagecontainerbox:hover"`, `"#imagecontainerbox:focus"` or `"#mediaPreviewBox"` selector exists in `self.rules`.
- New `TestFirefoxChrome.test_page_info_media_preview_provenance`, placed immediately after `test_page_info_field_provenance`, asserts the leading comment names `"No reference shows Firefox's Page Info media preview"`, `"#imagecontainerbox"`, `"widgets/lineedit.svg"`, `"firstboot_betawiki.png"`, `"tests/test_desktoptheme_lineedit.py::TestLineEdit"`, `"TestLineEditReference"`, `"#mainDeck input"`, `"pageInfo.xhtml"`, `"#mediaBrowser"`, `"#brokenimagecontainer"`, `"pageInfo.css"`, `"Field"`, `"ThreeDLightShadow"`, `"no hover, focus or selected variant"`, `"platform colour adaptation 2026-10-26"` and `"Declaration checks do not establish rendered pixels"`. Leave `test_page_info_provenance`, `test_page_info_field_paint_is_scoped_to_page_info` and `test_page_info_field_provenance` untouched so this plan does not edit their bodies.
- `docs/invariants.md` gains a row appended at the end of the `## firefox` table, after the last Page Info row and before `## gtk`: the Media panel's preview pane (`vbox#imagecontainerbox`) is the opaque `#FFFFFF` sunken field — square corners, a 1px `#000000` outline, the `inset 1px 1px #999999` top-left shadow and black text, with no stock `ThreeDLightShadow` border and no hover, focus or selected variant — while the embedded `#mediaBrowser`, the `#brokenimagecontainer` placeholder, the media table's inputs (still the `#mainDeck input` paint), labels and save buttons stay Firefox's, and the trees, permission list, display fields and security tables stay Firefox's. Its test column names the new scope test, and its provenance records the missing Page Info media-preview reference, the `widgets/lineedit.svg` anchor (grounded in `firstboot_betawiki.png` and pinned by `tests/test_desktoptheme_lineedit.py`), the installed Firefox ESR 153.5.1 `pageInfo.xhtml` and skin `pageInfo.css` files, and that declaration checks do not establish rendered pixels. In the `## firefox` table's Page Info top-bar row and Page Info fields row, drop `media preview` from the lists of surfaces whose guarantees say they stay Firefox's. `tests/invariants.py` stays green.
- `make check` passes, and the existing `userChrome.css` rules (including the `#viewGroup`, `#mainDeck`, `#mainDeck input` and, if it has landed, `#permList` paints), the Firefox install and their tests keep their declarations and scope.

## Done
