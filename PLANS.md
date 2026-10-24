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

### Platinum GTK rows: paint the list and tree selection and drop the hover wash (planned 2026-10-23 by the plan role; independent of the waiting icon-theme plan)

**Goal.** Both opt-in GTK sheets paint windows, header bars, buttons, entries, tabs, menus, scroll bars, meters, scales, check and radio faces, arrows, tooltips, separators and frames, but they name no row rule. GTK 4's installed Default theme paints a selected tree-view, column-view or list row in its accent blue (`#3584e4`) and gives an activatable list row a grey hover wash (`row.activatable:hover`); a GTK 3 application gets whatever its fallback sheet supplies. Mac OS 8.6's list row is the reference-grounded Platinum row pinned in `theme/desktoptheme/org.macos8.desktop/widgets/listitem.svg`: the unselected row is the view background, a hovered row stays pixel-identical to an unselected one, and the selected row is a flat `#CCCCFF` fill with square corners, no bevel and black text. Paint that row in both sheets for `GtkTreeView` and `GtkListBox`, and in GTK 4 for `GtkColumnView` and `GtkListView`. No reference screenshot shows a GTK widget, so the geometry is this theme's adaptation of the grounded `listitem.svg` row; the fill reuses the pinned `SELECTION` value and introduces no hex literal.

**Approach.**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: after the `frame > border, .frame` rule and before `scrollbar`, add `treeview.view:hover` and `list row.activatable:hover` with `background-color: transparent`; then `treeview.view:selected, treeview.view:selected:hover` and `list row.activatable:selected, list row.activatable:selected:hover` with `background-color: #CCCCFF`, `color: #000000` and `border-radius: 0`. The list-row rules name `.activatable` because the toolkit's fallback row rules select that class, so a plain `list row:selected` would lose to `row.activatable:selected`. Extend the header provenance paragraph to name the row rules and say they adapt the grounded `widgets/listitem.svg` row.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: after the `frame > border, .frame` rule and before `scrollbar > range > trough`, add the same hover and selection rules, plus `listview > row.activatable:hover`, `columnview.view:selected, columnview.view:selected:hover` and `listview > row.activatable:selected, listview > row.activatable:selected:hover`. Extend its header provenance paragraph the same way.
- `tests/support/gtk_theme_spec.py`: add `ROW_HOVER = {"background-color": "transparent"}` and `ROW_SELECTED = {"background-color": SELECTION, "color": BLACK, "border-radius": "0"}` beside the other shared specs; add `test_row_hover` (asserting `treeview.view:hover` and `list row.activatable:hover`) and `test_row_selection` (asserting `treeview.view:selected`, `treeview.view:selected:hover`, `list row.activatable:selected` and `list row.activatable:selected:hover`) to `GtkSheetRuleCases`, so both sheet suites run them.
- `tests/test_gtk4_theme.py`: add `test_columnview_and_listview_rows` asserting `ROW_HOVER` on `listview > row.activatable:hover` and `ROW_SELECTED` on `columnview.view:selected`, `columnview.view:selected:hover`, `listview > row.activatable:selected` and `listview > row.activatable:selected:hover`.
- `docs/invariants.md`: extend both `## gtk` control rows to name the tree, column, list-view and list-box row hover and selection rules, with the provenance exception that no reference screenshot shows a GTK widget, the row's no-hover and flat `#CCCCFF` selection adapt the reference-grounded `widgets/listitem.svg` row, and the node and class names are GTK-required.

**Files touched.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/support/gtk_theme_spec.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- Both sheets carry the row hover and selection rules above; every selected-row rule paints `#CCCCFF` with `#000000` text and square corners, every hover rule is transparent, and no new hex literal appears in either sheet.
- The shared `GtkSheetRuleCases` row cases pass for both sheets, the GTK 4-only column-view and list-view case passes, and `test_only_palette_hex_literals` still accepts both sheets unchanged.
- Both `## gtk` rows name the row rules and their `listitem.svg` provenance, `tests/invariants.py` accepts them, and `make check` is green.

### Platinum GTK headers: paint the tree and column headers as raised Platinum buttons (planned 2026-10-23 by the plan role; independent of the waiting GTK row plan)

**Goal.** Both opt-in GTK sheets paint windows, header bars, buttons, entries, tabs, menus, scroll bars, meters, scales, check and radio faces, arrows, tooltips, separators and frames, but they name no tree-view or column-view header rule. The installed GTK 3 default sheet (`/org/gtk/libgtk/theme/Adwaita/gtk-contained.css` in `libgtk-3.so.0`) paints `treeview.view header button` white with `#979a9b` text and `#d7d2ce` right and bottom separators; the GTK 4 `Default-light.css` in `libgtk-4.so.1` paints `columnview.view > header > button` and `treeview.view > header > button` the same way and gives their `sort-indicator` the icon-theme `pan-up-symbolic` and `pan-down-symbolic` glyphs. Those selectors are more specific than the sheets' generic `button` rule, so a file list's headers keep the default white/grey cells beside the Platinum rows. Paint them as the same raised Platinum button `widgets/button.svg` pins: a `#DDDDDD` face, `#000000` text, square corners, the raised bevel and a single 1px `#000000` line between columns and under the header row. In GTK 4, replace the sort indicator's icon-theme chevrons with the already-shipped `assets/arrow-up.svg` and `assets/arrow-down.svg` black triangles. GTK 3's default sheet names no `sort-indicator` node, so this plan paints no GTK 3 sort indicator. No reference screenshot shows a GTK widget or a list header row, so the geometry is this theme's adaptation of the reference-grounded Platinum push button; the rules introduce no hex literal the sheets do not already use.

**Approach.**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: after the notebook tab rules and before `menu, .menu, popover, .popover`, add `treeview.view header button` with `background-color: #DDDDDD`, `background-image: none`, `color: #000000`, `text-shadow: none`, `border-width: 0 1px 1px 0`, `border-style: solid`, `border-color: #000000`, `border-radius: 0` and `box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA`; add `treeview.view header button:hover` with `background-color: #DDDDDD`, `color: #000000`, `text-shadow: none` and the same raised bevel; add `treeview.view header button:active` with `color: #000000`, `text-shadow: none` and the inverted `inset 1px 1px #AAAAAA, inset -1px -1px #FFFFFF` bevel. The widths, not the default's four-side border shorthand, make adjacent columns share one line, and the default sheet's `:last-child` rule still removes the last column's right line. Extend the header provenance paragraph to name the header rule and say it adapts the grounded Platinum button and that GTK 3 exposes no sort-indicator node to redirect.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: after the notebook tab rules and before `popover > contents, popover > arrow`, add the same three rule groups for the selector pair `columnview.view > header > button, treeview.view > header > button` (and each state), with the same declarations; add `columnview.view > header > button sort-indicator.ascending, treeview.view > header > button sort-indicator.ascending` with `-gtk-icon-source: url("../assets/arrow-up.svg")` and the matching `descending` pair with `url("../assets/arrow-down.svg")`. Extend its header provenance paragraph the same way, naming the two sort triangles.
- `tests/support/gtk_theme_spec.py`: add `TREE_HEADER = {background-color: FACE, background-image: none, color: BLACK, text-shadow: none, border-width: "0 1px 1px 0", border-style: solid, border-color: BLACK, border-radius: "0", box-shadow: BUTTON_BEVEL}`, `TREE_HEADER_HOVER = {background-color: FACE, color: BLACK, text-shadow: none, box-shadow: BUTTON_BEVEL}` and `TREE_HEADER_ACTIVE = {color: BLACK, text-shadow: none, box-shadow: INVERTED_BUTTON_BEVEL}` beside `FRAME`; add `assert_tree_header(self, selectors)` after `assert_scale`, which asserts the base, `:hover` and `:active` declarations on every selector.
- `tests/test_gtk_theme.py`: add `test_tree_header` calling `self.assert_tree_header(("treeview.view header button",))`.
- `tests/test_gtk4_theme.py`: add `test_tree_and_column_headers` calling `self.assert_tree_header(("columnview.view > header > button", "treeview.view > header > button"))` and asserting the up URL on both `sort-indicator.ascending` selectors and the down URL on both `sort-indicator.descending` selectors; add `"../assets/arrow-up.svg"` to `test_stands_alone`'s URL allowlist, which then names all four shipped assets.
- `docs/invariants.md`: add one new row at the end of the `## gtk` table, after the last settings row, naming the header face, the shared header case, the GTK 4 sort indicator and the GTK 3 omission. Leave the two existing `## gtk` control rows for the waiting row plan to extend.

**Files touched.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/support/gtk_theme_spec.py`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`. The install list, `Makefile` and `README.md` are untouched: no new asset ships and the README's GTK paragraphs enumerate no painted surface.

**Acceptance criteria.**
- Both sheets carry the header rules above; every base header rule paints the `#DDDDDD` face, `#000000` text with no shadow, the `0 1px 1px 0` black grid, square corners and the raised bevel, every hover rule keeps the raised bevel and black text, every active rule uses the inverted bevel, and no new hex literal appears in either sheet. The GTK 4 sheet's ascending and descending sort indicators point at the shipped up and down assets.
- The shared header case passes for both sheets, the GTK 4-only sort-indicator case passes, `test_stands_alone` accepts the four shipped asset URLs, and `test_only_palette_hex_literals` still accepts both sheets unchanged.
- The new `## gtk` invariant row names these tests and the provenance exception, `tests/invariants.py` accepts it, and `make check` is green.

## Done
