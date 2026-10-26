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

### Firefox Platinum chrome: give a tab in a multi-selection the selected tab face (planned 2026-10-26 by the plan role; independent of the waiting open menu-bar title paint)

**Goal.** Repaint a ctrl-clicked tab in a multi-selection with the selected tab's `#EEEEEE` face and open `#EEEEEE` bottom edge, so every tab in the selection reads as selected. The sheet's base `.tab-background` rule paints every tab face `#DDDDDD` with `!important`, and the sheet repaints only the active `.tabbrowser-tab[selected] .tab-background`; Firefox marks the other tabs of a multi-selection with the `multiselected` attribute (a ctrl-click on a non-active tab calls `addToMultiSelectedTabs`, which sets `multiselected` without `selected`, and `tab.js` mirrors it onto `.tab-background`), so those tabs keep the plain face even though Firefox's own `.tab-background:is([selected], [multiselected])` rule paints them.

**Grounding.** No reference screenshot shows Firefox chrome, or tabs and multi-selection at all. The face is the sheet's existing selected-tab `#EEEEEE` trough (`TROUGH`), already pinned by `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_view_background_alternate` and `tests/test_desktoptheme_scrollbar.py::TestScrollbarReference`; this plan adds no colour literal. Firefox's `chrome/browser/skin/classic/browser/tabbrowser/tabs.css` paints `.tab-background:is([selected], [multiselected])` with `--tab-background-color-selected`, and its `chrome/browser/content/browser/tabbrowser/tab.js` sets `multiselected` on the tab itself and, through `inheritedAttributes`, on `.tab-background` (`selected=visuallyselected`, `multiselected`); the sheet's selector keys off the tab's own attributes so the existing `[selected]` behaviour is unchanged. Record the missing reference and the dated platform adaptation (2026-10-26) in the sheet header.

**Approach and files touched.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: change the existing `.tabbrowser-tab[selected] .tab-background` selector to `.tabbrowser-tab:is([selected], [multiselected]) .tab-background`, keeping `background-color: #EEEEEE !important` and `border-bottom-color: #EEEEEE !important` and its position between the base `.tab-background` rule and the hover comment. Add no colour, geometry, text or close-button rule. Append the provenance paragraph at the end of the leading comment, immediately before its closing `*/`, after the install-instructions paragraph (the waiting menu-bar plan inserts between the optional-search-field and find-field notes): no reference shows Firefox multi-selection; the multiselected face reuses the sheet's `#EEEEEE` selected-tab trough rather than a screenshot sample; Firefox's `tabs.css` consumes `--tab-background-color-selected` on `.tab-background:is([selected], [multiselected])` and `tab.js` sets the tab's `selected` and `multiselected` attributes (`selected=visuallyselected` is mirrored onto `.tab-background`); declaration checks do not establish rendered pixels.
- `tests/test_firefox_theme.py`: re-key the `REQUIRED_RULES` entry from `.tabbrowser-tab[selected] .tab-background` to `.tabbrowser-tab:is([selected], [multiselected]) .tab-background`, keeping its two declarations. Update the exact selector set and the assertion loop in `TestFirefoxChrome.test_tab_hover_paint_is_scoped_to_unselected_tabs` to the new key. Add `TestFirefoxChrome.test_selected_face_covers_multiselected_tabs`: the selected-face selector contains both `[selected]` and `[multiselected]` and no `[selected]`-only tab rule paints a face; its declarations equal its `REQUIRED_RULES` entry; the only other parsed selector containing `multiselected` is the hover selector; the face and bottom border are `#EEEEEE` with `!important`. Insert `"No reference shows Firefox multi-selected tabs"` and `"selected=visuallyselected"` in `test_header_names_provenance_and_preference` after `"not-found and flash states stay"` and before `"platform colour adaptation 2026-10-26"`.
- `docs/invariants.md`: extend the existing standalone-sheet row under `## firefox` (the row naming the hovered-tab guarantee) with "a tab in a multi-selection (`[multiselected]`) paints the same `#EEEEEE` selected face and open bottom border as the active tab", the new test, and the dated provenance exception naming the missing Firefox multi-selection reference, Firefox's `tabs.css` consumer and `tab.js`'s tab attributes (`multiselected`, and `selected=visuallyselected` mirrored onto `.tab-background`); keep the row's caveat that declaration checks do not establish rendered pixels and add multi-selected tabs to that list.

**Acceptance criteria.**
- `REQUIRED_RULES` validation fails when the selected-face rule is missing, either declaration is not `#EEEEEE`, or either loses `!important`.
- The scope test fails when the selector drops `[selected]` or `[multiselected]`, when a separate selected-only rule paints a tab face, or when the face is applied to any selector beyond the selected/multiselected tab background; the hover test's exact set fails on any extra `tab-background` selector.
- A hovered unselected tab stays `#EEEEEE` and remains guarded from selected and multiselected tabs; a multiselected tab's face and bottom border are `#EEEEEE`; the active face, tab border, bevel, radius, tab text, close button, pinned and vertical tabs, and find-bar states stay as they are.
- `make check` passes without Firefox or a new dependency, the palette hex set is unchanged, and implementation stays within these three files. Report declaration validation separately from live browser rendering.

## Done
