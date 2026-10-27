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


### Firefox Platinum chrome: paint the Page Info permission list like a Platinum list (planned 2026-10-26 by the plan role; independent of the waiting Kvantum toolbox-tab plan, whose done stamp still sits in `## Planned` awaiting the move to PLANS-DONE.md)

**Goal.** Make the Permissions panel's permission list read as a Platinum list: the `vbox#permList` container becomes the opaque `#FFFFFF` sunken field the deck's display fields use — square corners, a 1px `#000000` outline and the `inset 1px 1px #999999` top-left shadow — with the native listbox frame dropped and black text; a hovered `.permission` row keeps the field's face with a transparent background and black text instead of Firefox's `-moz-dialog` wash, honouring the reference theme's no-hover-highlight list behaviour. The rows' bold labels, use-default checkboxes, per-state radios, dotted bottom separators, padding and geometry stay Firefox's. The deck's trees, media preview, display fields, security tables and the landed top-bar, tab and button paints are untouched.

**Grounding.** No reference screenshot shows Firefox's Page Info permission list, so the paint adapts this theme's Platinum list (platform colour adaptation 2026-10-26). The `#FFFFFF` face and `#999999` sunken shadow adapt `widgets/lineedit.svg` (`tests/test_desktoptheme_lineedit.py::TestLineEdit` and `TestLineEditReference`), grounded in `macos8.6-screenshots/firstboot_betawiki.png`, and are the exact recipe the sheet's landed `#mainDeck input` rule already ships; `#permList` is the deck's second list-shaped surface after that field rule, so the same face applies. The transparent hover and plain rows adapt `widgets/listitem.svg` (`tests/test_desktoptheme_listitem.py::TestListItem`), whose comment records that Mac OS 8.6 lists have no hover highlight, matching the GTK sheets' row mapping and this sheet's about:config table, whose `#prefs > tr:hover` rule paints hovered rows transparent. Dropping the native frame reuses the sheet's `#viewGroup > radio` precedent (`appearance: none !important`).

In the installed Firefox ESR 153.5.1, `chrome/browser/content/browser/pageinfo/pageInfo.xhtml` defines `vbox#permPanel` holding the empty `vbox#permList`, and `chrome/browser/content/browser/pageinfo/permissions.js`'s `createRow` builds each permission row at runtime as a `vbox.permission` containing `label.permissionLabel`, a `hbox` with a `native` checkbox and a horizontal `radiogroup`, appending it to `permList`; rows have no selectable or selected state. `chrome/browser/skin/classic/browser/pageInfo.css` gives `#permList` `appearance: auto` (`-moz-default-appearance: listbox`), `-moz-dialog`-independent `Field` background, `FieldText` text, a 1px `ThreeDShadow` border and `0.5em` margins, paints `.permission` with `6px 7px` padding and a dotted `ThreeDShadow` bottom border, and paints `.permission:hover` with `-moz-dialog` background and `-moz-DialogText` text. `#permList` is page-info-only, so the rules cannot leak into browser chrome. Declaration checks do not establish rendered pixels.

**Approach.** Append at the very end of `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, after the `#mainDeck input` rule, one short comment naming the adaptation and these two rules:

```css
#permList {
  appearance: none !important;
  background-color: #FFFFFF !important;
  color: #000000 !important;
  border: 1px solid #000000 !important;
  border-radius: 0 !important;
  box-shadow: inset 1px 1px #999999 !important;
}

#permList .permission:hover {
  background-color: transparent !important;
  color: #000000 !important;
}
```

`appearance: none` drops the stock `-moz-default-appearance: listbox` native frame, so the CSS border stands in. Keep the stock `margin: 0.5em` and `overflow: auto`, the rows' `6px 7px` padding and `1px dotted ThreeDShadow` bottom separators, and every row's label, checkbox, radios and geometry. Add no rule for `.permissionLabel`, the checkbox, the radios, `#permPanel`'s labels, `#hostText` (already covered by `#mainDeck input`), the trees, the media preview or the security tables, add no selected or pressed variant (rows have none), and change no existing selector. In the header comment block, insert a permission-list provenance paragraph immediately after the Page Info fields paragraph and before the closing `*/`: no reference shows Firefox's Page Info permission list; the `#FFFFFF` face and `#999999` sunken shadow adapt `widgets/lineedit.svg` and the `#mainDeck input` recipe, the transparent hover honours `widgets/listitem.svg`'s no-hover-highlight list reading, `permissions.js`'s `createRow` builds the rows and `pageInfo.css` owns the stock `-moz-default-appearance: listbox` paint and the `-moz-dialog` hover wash; declaration checks do not establish rendered pixels (platform colour adaptation 2026-10-26). Also trim the word `permission list` from the stay-Firefox surface lists in the two existing Page Info texts — the header's top-bar provenance paragraph ("…the dialog body, meta and image trees, permission list, media preview, security tables, description labels and focus rings stay Firefox's…") and the `#topBar` rule's leading comment ("…the dialog body, fields, trees, permission list, media preview, security tables and labels keep Firefox's own paint…") — leaving every other word of both lists unchanged.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `userChrome.css` gains exactly two new selectors, `#permList` and `#permList .permission:hover`, carrying exactly the declarations above (including `#permList`'s `appearance: none !important`); every existing selector keeps its declarations, and `test_palette_is_exact` keeps its expected hex set because the rules introduce no new hex literal (`transparent` and the existing palette constants only).
- `REQUIRED_RULES` in `tests/test_firefox_theme.py` gains, appended after the `"#mainDeck input"` entry, `"#permList"` mapping to `appearance: none !important`, `background-color: {WHITE} !important`, `color: {BLACK} !important`, `border: 1px solid {BLACK} !important`, `border-radius: 0 !important` and `box-shadow: inset 1px 1px {GREY} !important`, and `"#permList .permission:hover"` mapping to `background-color: transparent !important` and `color: {BLACK} !important`, with the constants `support.platinum_palette` already exports.
- New `TestFirefoxChrome.test_page_info_permission_list_paint_is_scoped_to_page_info`, placed immediately after `test_page_info_field_provenance`: asserts the rule names containing `permList` or `.permission` are exactly those two, each equals its `REQUIRED_RULES` entry, and the hover selector carries `:hover` with no bevel declaration. Using `support.selector_matching.element`/`matches`, build `window` holding `deck#mainDeck` with `vbox#permPanel`, inside it `vbox#permList` and one `vbox.permission` row containing `label.permissionLabel` and a `radiogroup`, plus `vbox#securityPanel` holding `input#hostText`. Assert the row matches `#permList .permission:hover` only when `hover` is true (with and without, it matches no `#permList` container rule, which is a container selector), `#hostText` matches `#mainDeck input` and neither perm-list rule, and a `vbox.permission` row inside a `vbox#otherList` that is not `#permList` matches neither rule.
- New `TestFirefoxChrome.test_page_info_permission_list_provenance`, placed immediately after the scope test, asserts the leading comment names `"No reference shows Firefox's Page Info permission list"`, `"widgets/lineedit.svg"`, `"firstboot_betawiki.png"`, `"tests/test_desktoptheme_lineedit.py::TestLineEdit"`, `"TestLineEditReference"`, `"#mainDeck input"`, `"widgets/listitem.svg"`, `"tests/test_desktoptheme_listitem.py::TestListItem"`, `"no hover highlight"`, `"#prefs > tr:hover"`, `"permissions.js"`, `"createRow"`, `"pageInfo.css"`, `"-moz-default-appearance: listbox"`, `"-moz-dialog"`, `"#permList"`, `".permission"` and `"platform colour adaptation 2026-10-26"`. Leave `test_page_info_provenance` and `test_page_info_field_provenance` untouched so this plan does not edit their tuples.
- `docs/invariants.md` gains a row appended at the end of the `## firefox` table, after the Page Info fields row and before `## gtk`: the Permissions panel's permission list (`vbox#permList`) is the opaque `#FFFFFF` sunken list field — square corners, a 1px `#000000` outline, the `inset 1px 1px #999999` top-left shadow and black text, with no native listbox frame — and a hovered `.permission` row keeps the field's face with a transparent background and black text instead of the `-moz-dialog` wash, while rows keep Firefox's dotted bottom separators, padding, bold labels, use-default checkboxes and per-state radios, and the trees, media preview, display fields and security tables stay Firefox's. Its test column names the new scope test, and its provenance records the missing Page Info permission-list reference, the `widgets/lineedit.svg` (grounded in `firstboot_betawiki.png` and pinned by `tests/test_desktoptheme_lineedit.py`) and `widgets/listitem.svg` anchors, the installed Firefox ESR 153.5.1 `pageInfo.xhtml`, `permissions.js` (`createRow`) and `pageInfo.css` files, and that declaration checks do not establish rendered pixels. In the `## firefox` table's Page Info top-bar row, drop the permission list from the list of surfaces whose guarantee says they stay Firefox's. `tests/invariants.py` stays green.
- `make check` passes, and the existing `userChrome.css` rules (including the `#viewGroup`, `#mainDeck` and `#mainDeck input` paints), the Firefox install and their tests keep their declarations and scope.
## Done
