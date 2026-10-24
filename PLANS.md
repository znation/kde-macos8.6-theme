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

### Platinum GTK control glyphs, part 2/2: paint the combo box and menu scroll arrows from shipped assets (planned 2026-10-23 by the plan role; "requires part 1/2 landed")

**Goal.** After part 1/2 both sheets ship the shared `assets/` directory and the check and radio glyphs, but `GtkComboBox`'s dropdown indicator (and, in GTK 3, a long menu's scroll arrows) still draw the toolkit's icon-theme chevrons, because the sheets never set `-gtk-icon-source` on those nodes. Paint them with the solid black Platinum triangles the desktop theme already pins in `widgets/arrows.svg`: the `down-arrow` path `M 4,5 L 12,5 L 8,11 Z` and the `up-arrow` path `M 4,11 L 12,11 L 8,5 Z`. Ship the two glyphs beside the check and radio assets and point the sheets' `-gtk-icon-source` at them. No reference screenshot shows a GTK widget, so the triangle geometry is the desktop theme's pinned shape and the 16x16 size is the installed default sheet's combo-arrow size. Spin-button arrows stay out of scope: GTK draws them from the icon theme rather than from a CSS `-gtk-icon-source` the sheet can redirect, so pointing the sheet at an asset would only repaint their faces and leave a stock chevron beside them.

**Approach.**
- New `theme/gtk/org.macos8.desktop/assets/arrow-down.svg` and `assets/arrow-up.svg`: standalone 16x16 SVGs with no script, style or id, each one `<path>` with `fill="#000000"` and the corresponding path above.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: after the part 1/2 check/radio rules add `combobox arrow` with `-gtk-icon-source: url("../assets/arrow-down.svg")`, `min-height: 16px` and `min-width: 16px`; add `menu > arrow.top, .menu > arrow.top, .context-menu > arrow.top` with `-gtk-icon-source: url("../assets/arrow-up.svg")`; add the matching `menu > arrow.bottom, .menu > arrow.bottom, .context-menu > arrow.bottom` group with the down URL. Extend the sheet's header provenance paragraph to name the two arrow glyphs and state that spin-button arrows stay from the icon theme.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: add `combobox arrow, dropdown arrow` with the down URL and the same 16px min size, and extend its header provenance paragraph the same way. GTK 4 has no `menu > arrow.top`/`bottom` scroll nodes (its menus scroll inside a popover), so the GTK 4 sheet names only the combo and dropdown arrows.
- `Makefile` (the `install_gtk` define and the uninstall recipe): add `assets/arrow-down.svg` and `assets/arrow-up.svg` to the part 1/2 two-phase sequence (stage every file, then rename every file), add both staging paths to the `trap`, and on uninstall remove the two assets and their staging siblings, then `rmdir` the emptied `assets/` after removing the part 1/2 glyphs. Add no `.old` rollback phase, for the same reason as part 1/2.
- `README.md`: the GTK install paragraph that names the shared glyph assets gains the two arrow glyphs, and the `make uninstall` sentence keeps naming the emptied `assets` directory beside `gtk-3.0`/`gtk-4.0`.
- `tests/support/gtk_fixtures.py`: add `assets/arrow-down.svg` and `assets/arrow-up.svg` to `SHIPPED_FILES`, so the package-coverage, repeat-install, failed-install and uninstall tests iterate them.
- `tests/support/gtk_theme_spec.py`: add `COMBO_ARROW = {"-gtk-icon-source": 'url("../assets/arrow-down.svg")', "min-height": "16px", "min-width": "16px"}` and a `test_combobox_arrow` case in `GtkSheetRuleCases` asserting it on `combobox arrow`, which both sheets spell the same way.
- `tests/test_gtk_theme.py`: assert the three `.top` selectors carry the up URL and the three `.bottom` selectors the down URL; add a `TestArrowGlyphs` case (modelled on part 1/2's `TestCheckGlyphs`) that parses both assets through `support.svg_case.parse_svg` and pins each root's 16x16 `viewBox`, each path's `d` and `fill="#000000"`, the `{#000000}` fill set and the absence of script and style elements; add a `test_icon_sources_point_at_shipped_assets` that collects every `url(...)` value in the sheet and asserts it is one of the four shipped `../assets/` paths (checkmark, bullet, arrow-down, arrow-up).
- `tests/test_gtk4_theme.py`: assert the shared `combobox arrow` rule and the GTK 4-only `dropdown arrow` rule; change `test_stands_alone`'s URL allowlist, which part 1/2 narrowed to the two check/radio paths, to the three paths the GTK 4 sheet names (checkmark, bullet, arrow-down).
- `docs/invariants.md`: extend both `## gtk` control rows to name the combo box dropdown arrow and the GTK 3 menu scroll arrows, with the provenance exception that no reference screenshot shows a GTK widget, the triangles are the desktop theme's pinned `widgets/arrows.svg` shapes, the 16px size and selectors are GTK-required (read from the installed default sheet), and spin-button arrows are not redirected because GTK draws them from the icon theme; extend the opt-in install row to copy and remove the two arrow assets and say they are this theme's own.

**Files touched.** `theme/gtk/org.macos8.desktop/assets/arrow-down.svg`, `theme/gtk/org.macos8.desktop/assets/arrow-up.svg` (both new), `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `Makefile`, `README.md`, `tests/support/gtk_fixtures.py`, `tests/support/gtk_theme_spec.py`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- Both sheets' `combobox arrow` (and GTK 4's `dropdown arrow`) carry the down asset URL and the 16px min size, and the GTK 3 menu `.top`/`.bottom` groups carry the up/down URLs; no new hex literal appears in either sheet.
- Each arrow asset is a 16x16 standalone SVG with its pinned path and `#000000` fill, and the GTK 3 sheet's `url(...)` values are exactly the four shipped asset paths.
- The opt-in install copies the seven package files byte-for-byte (index, two sheets, four assets), a failure while staging any file leaves the previous files intact with no staging sibling, and uninstall removes only those files and the emptied `assets`, `gtk-3.0` and `gtk-4.0` directories, leaving `Kvantum/`.
- The GTK 3 and GTK 4 suites pass (including the narrowed `test_stands_alone`), `tests/invariants.py` accepts the updated `## gtk` rows, and `make check` is green.

### Platinum icon theme: draw the standard XDG places as the Platinum folder (planned 2026-10-23 by the plan role; independent of the waiting GTK glyph series)

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

## Done
