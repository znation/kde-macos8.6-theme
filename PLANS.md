# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; landed-plan facts re-trimmed 2026-10-23
by the clean role):** The
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
selected by `apply-gtk`; `make install` copies no GTK files); and the render and fidelity tooling
that checks them against `macos8.6-screenshots/`. README.md describes the reference set as the
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

### Firefox Platinum chrome: paint the toolbar button states, bookmark items, menu separators and the find bar (planned 2026-10-23 by the plan role; independent of the waiting GTK meters plan)

**Goal.** The Firefox sheet paints the tab strip, navigation bar, bookmarks-bar background, menus and status panel, but it leaves Firefox's own rounded hover and pressed washes on the toolbar buttons, rounded highlights on bookmarks-bar items, the stock grey menu separator, and the default find bar. Paint those surfaces with the pinned Platinum values the sheet already uses: the #EEEEEE trough as the hover wash, the #CCCCFF selection as the pressed/open fill, the raised bevel (`inset 1px 1px #FFFFFF, inset -1px -1px #999999`) on the hovered button, the etched #888888/#FFFFFF rule from `widgets/line.svg`, the #DDDDDD face for the find bar and the white sunken field with its #999999 shadow for its text box. No reference screenshot shows Firefox chrome, so the geometry is this theme's adaptation of the Platinum controls; the new rules introduce no new hex literal.

**Approach.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`:
  - Extend the `:root` block with Firefox's toolbarbutton variables: `--toolbarbutton-border-radius: 0 !important`, `--toolbarbutton-hover-background: #EEEEEE !important`, `--toolbarbutton-active-background: #CCCCFF !important`, `--toolbarbutton-hover-boxshadow: inset 1px 1px #FFFFFF, inset -1px -1px #999999 !important` and `--toolbarbutton-active-boxshadow: inset 1px 1px #999999 !important`.
  - Add one rule `#PersonalToolbar .bookmark-item:hover, #PersonalToolbar .bookmark-item[open]` with `background-color: #CCCCFF !important`, `border-radius: 0 !important` and `box-shadow: inset 1px 1px #FFFFFF !important`.
  - Add `menupopup > menuseparator` with `border-top: 1px solid #888888 !important`, `border-bottom: 1px solid #FFFFFF !important`, `padding: 0 !important` and `margin: 2px 0 !important` (the etched separator, matching `widgets/line.svg`).
  - Add `findbar` with `background-color: #DDDDDD !important` and `border-top: 1px solid #000000 !important`, and `findbar .findbar-textbox` with `background-color: #FFFFFF !important`, `border: 1px solid #000000 !important`, `border-radius: 0 !important` and `box-shadow: inset 1px 1px #999999 !important`.
  - Extend the header's provenance paragraph to name the toolbar button states, bookmark items, menu separators and find bar among the sheet's adapted surfaces.
- `tests/test_firefox_theme.py`: add the five `:root` variables to `REQUIRED_RULES[":root"]` and add `REQUIRED_RULES` entries for the bookmark-item, menuseparator, findbar and findbar-textbox selectors, reusing the imported `BLACK`, `FACE`, `GREY`, `SELECTION`, `TROUGH` and `WHITE` values and importing `RAISED_BEVEL` from `support.gtk_theme_spec`; leave `test_palette_is_exact`'s expected set unchanged (every new declaration uses a value it already accepts).
- `docs/invariants.md`: extend the `## firefox` standalone-sheet guarantee sentence to name the toolbar button states, bookmark items, menu separators and find bar; keep its no-reference-screenshot provenance exception.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The sheet carries the pinned `:root` variables and the bookmark-item, menuseparator and findbar rules, and `test_required_rules` fails if any selector or declaration changes.
- `test_palette_is_exact` still passes with the same hex set, the sheet still contains no at-rule or import, and no selector is universal.
- `tests/invariants.py` accepts the updated `## firefox` row and `make check` is green.

## Done
