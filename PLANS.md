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

### Firefox Platinum chrome: paint the hovered unselected tab face (planned 2026-10-26 by the plan role; independent of the Firefox find-field foreground plan)

**Goal.** Give a hovered, unselected Firefox tab the Platinum hover fill `#EEEEEE`, so the tab strip responds to the pointer again. The sheet's `.tab-background` rule paints every tab face `#DDDDDD` with `!important`, and its greater user-origin weight suppresses Firefox's own `background-color: var(--tab-background-color-hover)` rule in `chrome/browser/skin/classic/browser/tabbrowser/tabs.css` (`.tabbrowser-tab:hover > .tab-stack > .tab-background:not([selected], [multiselected])`), leaving hover with no visible feedback.

**Grounding.** No reference screenshot shows Firefox chrome or a hovered tab. The fill is the already-pinned flat trough `#EEEEEE` (`TROUGH` in `tests/support/platinum_palette.py`, painted from `[Colors:View] BackgroundAlternate`): `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_view_background_alternate` re-derives it from `setup_emaculation.png`, and `tests/test_desktoptheme_scrollbar.py::TestScrollbarReference` ties it to the desktop theme's artwork. The sheet already uses it for the selected tab face, `--toolbarbutton-background-color-hover` and the results-row hover; this adds no new colour literal. Record the hover state as a platform adaptation dated 2026-10-26, naming Firefox's consumed `--tab-background-color-hover` source and the missing reference.

**Approach and files touched.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: immediately after the `.tabbrowser-tab[selected] .tab-background` rule, add
  `.tabbrowser-tab:hover > .tab-stack > .tab-background:not([selected]):not([multiselected]) { background-color: #EEEEEE !important; }`.
  Keep the base `.tab-background` face, border, bevel and radius unchanged; the hover rule only overrides its fill. Extend the header provenance with the dated missing-surface note, the `#EEEEEE` source and the two tests named above.
- `tests/test_firefox_theme.py`: add the hover selector to `REQUIRED_RULES` directly after the selected-tab entry, with `background-color: f"{TROUGH} !important"`. Add `TestFirefoxChrome.test_tab_hover_paint_is_scoped_to_unselected_tabs`: the selectors naming `tab-background` are exactly `.tab-background`, `.tabbrowser-tab[selected] .tab-background` and the new hover selector; each declaration set equals its `REQUIRED_RULES` entry; the hover selector contains `:hover`, `:not([selected])` and `:not([multiselected])`. Extend `test_header_names_provenance_and_preference` with `"No reference shows Firefox tab hover"` and `"test_desktoptheme_scrollbar.TestScrollbarReference"`, inserted directly after the `"Provenance exception"` entry rather than appended at the tuple's end, so the waiting find-field plan's header additions do not collide with this plan's.
- `docs/invariants.md`: extend the standalone-sheet row under `## firefox` with the hovered unselected tab guarantee and the new scope test, and add the dated platform-adaptation provenance; keep the row's statement that declaration checks do not establish rendered pixels.

**Acceptance criteria.**
- `REQUIRED_RULES` validation fails when the hover fill is removed, made non-#EEEEEE or loses `!important`; the scope test fails for an unguarded `.tab-background:hover` rule, for a rule that omits the selected or multiselected guard, and for any extra selector painting a tab background.
- Selected and multiselected tabs keep the selected fill and open bottom border; the tab face, border, bevel, radius, tab text, close button, pinned and vertical tabs and find-bar states stay as they are.
- `make check` passes without Firefox or a new dependency, the palette hex set is unchanged, and implementation stays within these three files. Report declaration validation separately from live browser rendering.

### Firefox Platinum chrome: paint the open menu-bar title with the Platinum highlight (planned 2026-10-26 by the plan role; independent of the waiting hovered-tab paint)

**Goal.** When the Firefox menu bar is shown and one of its titles is open, paint that title with the Platinum selection lavender `#CCCCFF` instead of Firefox's Linux accent underline, so the open title matches the desktop theme's reference-derived menu-bar title. The sheet paints `#toolbar-menubar`'s face and etched bottom rule, but its `menubar > menu` titles keep Firefox's stock rule in `chrome/toolkit/skin/classic/global/menu.css` (Linux: transparent face and a 3px transparent bottom border, which `[open]` recolours to `AccentColor`), so an open title is underlined in the system accent colour rather than filled.

**Grounding.** No reference screenshot shows Firefox chrome. The open title's fill is the already-pinned `#CCCCFF` selection: `theme/desktoptheme/org.macos8.desktop/widgets/menubaritem.svg`'s pressed slices are that flat fill, pinned by `tests/test_desktoptheme_menubaritem.py::TestMenuBarItem.test_menubaritem_pressed_is_flat_selection_colour`, and the colour itself is re-derived from `desktop_archiveorg8.6hd.png` by `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_selection_background`. The same widget's `normal` and `hover` slices paint nothing (`TestMenuBarItem.test_menubaritem_normal_and_hover_have_no_fill`), so this plan adds no hover rule. Record the missing Firefox menu-bar surface and the dated platform adaptation.

**Approach and files touched.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: after the existing `#toolbar-menubar` rule and before `.tab-background`, add
  `#toolbar-menubar menubar > menu[open] { background-color: #CCCCFF !important; border-bottom-color: #CCCCFF !important; }`
  Keep the `#toolbar-menubar` face, etched bottom border and inset white shadow unchanged, and add no hover, text-colour or geometry rule. In the header, insert the provenance paragraph between the optional-search-field note (ending "`#searchbar-new` stays Firefox's.") and the find-field note (starting "No reference shows Firefox's find field"), so it does not share an anchor with the waiting hovered-tab plan: no reference shows Firefox's menu bar; the open title's flat fill comes from `widgets/menubaritem.svg`'s pressed slices with no hover highlight; the `menubar > menu[open]` selector and its `[open]` state are Firefox's, from `chrome/toolkit/skin/classic/global/menu.css` on Linux.
- `tests/test_firefox_theme.py`: add `#toolbar-menubar menubar > menu[open]` to `REQUIRED_RULES` directly after the `#toolbar-menubar` entry, with `background-color: f"{SELECTION} !important"` and `border-bottom-color: f"{SELECTION} !important"`. Add `TestFirefoxChrome.test_menubar_open_title_paint_is_scoped_to_the_open_title`: the selectors whose text contains `menubar` are exactly `#toolbar-menubar` and the new selector; both declaration sets equal their `REQUIRED_RULES` entries; no other rule paints a menubar title. Append `"No reference shows Firefox's menu bar"`, `"TestMenuBarItem.test_menubaritem_pressed_is_flat_selection_colour"` and `"TestReferenceAnchors.test_selection_background"` at the end of the provenance tuple in `test_header_names_provenance_and_preference`, after `"platform colour adaptation 2026-10-26"`, rather than after `"Provenance exception"`, so the waiting hovered-tab plan's insertion there does not collide.
- `docs/invariants.md`: add a new row at the end of `## firefox` (not an edit of the existing standalone-sheet row) whose guarantee is "The open Firefox menu-bar title (`#toolbar-menubar menubar > menu[open]`) is a flat `#CCCCFF` fill with a `#CCCCFF` bottom border and no hover rule", whose test is the new scope test, and whose provenance exception names the missing Firefox menu-bar reference, the desktop-theme menubaritem provenance, that the selector and `[open]` state are Firefox's, and that declaration checks do not establish rendered pixels.

**Acceptance criteria.**
- `REQUIRED_RULES` validation fails when the rule is removed, its fill or bottom border is not `#CCCCFF`, or either declaration loses `!important`.
- The scope test fails when a `:hover` or `[_moz-menuactive="true"]` menubar rule is added, when the `[open]` guard is dropped, or when the new declarations are applied to any selector beyond the open title.
- A closed or hovered menu-bar title keeps Firefox's transparent face and inherited black text; the `#toolbar-menubar` face, its etched bottom rule, popup menus, toolbar buttons, tabs and find bar stay as they are.
- `make check` passes without Firefox or a new dependency, the palette hex set is unchanged, and implementation stays within these three files. Report declaration validation separately from live browser rendering.

## Done
