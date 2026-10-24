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

### Platinum icon theme: draw the standard XDG places as the Platinum folder (planned 2026-10-23 by the plan role)

**Goal.** The icon theme ships `places/folder.svg`, `places/inode-directory.svg`, `places/user-home.svg`, `places/user-desktop.svg`, `places/user-trash.svg` and `places/user-trash-full.svg` at 32x32, 22x22 and 16x16, so a Home, Desktop or generic directory draws the Platinum folder. KDE's places model in the installed `libKF6KIOCore.so.6` names its standard folder places with eight more icons — `folder-documents` (Documents), `folder-download` (Downloads), `folder-music` (Music), `folder-pictures` (Pictures), `folder-videos` (Videos), `folder-templates` (Templates), `folder-public` (Public) and `folder-temp` (Temporary Files) — and the package ships none of them, so Dolphin's Places sidebar and every place menu draw Breeze's blue folders beside the Platinum ones. Ship the eight names at 32x32, 22x22 and 16x16 as the matching size's Platinum folder, exactly as `inode-directory` already aliases `folder`, so every standard place draws one Platinum folder. No reference screenshot shows these places; the art is the existing folder drawing rather than new art and introduces no palette value. The installed KIO core names `folder-public`, not Breeze's older `folder-publicshare`, and no `folder-downloads` plural, so ship only the names KIO actually resolves.

**Approach.**
- Add `theme/icons/org.macos8.desktop/{32x32,22x22,16x16}/places/` files for the eight names above, each drawing the matching `folder.svg`'s root children in the same document order with the same `d`, geometry and `fill` attributes. Each comment names the place it draws and says it shares the folder geometry because Mac OS 8.6 draws one folder shape for a directory; only the comment differs from `folder.svg`.
- `theme/icons/org.macos8.desktop/index.theme`: no change; `32x32/places`, `22x22/places` and `16x16/places` are already declared with their `Size`, `Context=Places` and `Type=Fixed` sections.
- `tests/test_icon_theme.py`: define `STANDARD_PLACES = ("folder-documents", "folder-download", "folder-music", "folder-pictures", "folder-videos", "folder-templates", "folder-public", "folder-temp")` beside `SHIPPED_ICONS`; extend `SHIPPED_ICONS` with one comprehension over `("16x16", "22x22", "32x32")` and `STANDARD_PLACES`, so the inventory carries the 24 paths without 24 hand-written literals; extend the existing `ICON_SHAPES` alias loop's alias tuple with `*STANDARD_PLACES`, so each new path maps to its size's `folder.svg` tuple; and extend `test_the_folder_alias_shares_the_folder_art` (rename it to `test_every_place_alias_shares_the_folder_art`) to iterate the same alias tuple at all three sizes.
- `README.md`: in the icon-theme sentence that names the hard-disk, folder, document, Trash and full-Trash icons and the Home and Desktop places as the same Platinum folder, name the standard Documents, Downloads, Music, Pictures, Videos, Templates, Public and Temporary Files places as that same folder.
- `docs/invariants.md`: extend the `## icons` geometry row ("the `inode-directory`, `user-home` and `user-desktop` aliases share the folder art") to name the eight standard place names and cite the same test; keep the provenance exception that the art is our own and the reference set has no pixel ground truth, adding that the eight names are KDE-required values read from the installed KIO core's places model and the shared folder shape is this theme's own choice.

**Files touched.** Twenty-four new SVGs under `theme/icons/org.macos8.desktop/{32x32,22x22,16x16}/places/` (`folder-documents.svg`, `folder-download.svg`, `folder-music.svg`, `folder-pictures.svg`, `folder-videos.svg`, `folder-templates.svg`, `folder-public.svg`, `folder-temp.svg`), `tests/test_icon_theme.py`, `README.md`, `docs/invariants.md`.

**Acceptance criteria.**
- Each of the 24 new icons is a square SVG of its declared size whose drawing elements equal the matching `folder.svg`'s in document order, and the alias test compares the `inode-directory`, `user-home` and `user-desktop` aliases plus all eight standard places at 16x16, 22x22 and 32x32.
- The shipped-icon inventory and the `ICON_SHAPES` registry both include the 24 paths and remain equal; the palette, structure, placeholder and index-directory tests pass with no new hex literal and no `index.theme` edit.
- The README names the standard places as the Platinum folder, the `## icons` row names the eight place names and their KIO provenance, `tests/invariants.py` accepts the row, and `make check` is green.

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

## Done
