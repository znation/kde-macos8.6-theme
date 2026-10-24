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
(startup splash, desktop layout, defaults); the desktop theme (twenty-seven widget SVGs under
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

### Platinum virtual-desktop pager: ship `widgets/pager.svg` for the optional Pager applet (planned 2026-10-23 by the plan role)

**Goal.** The optional Pager (`org.kde.plasma.pager`; `org.kde.plasma.activitypager` shares its QML through `X-Plasma-RootPath`) draws every virtual-desktop cell with `KSvg.FrameSvgItem imagePath: "widgets/pager"` in `contents/ui/main.qml`, one frame per prefix `normal`, `hover` and `active`. The theme ships no `widgets/pager.svg`, so KSvg falls back to Breeze's pager frames and a Pager added to the Platinum menu bar draws Breeze's cells. Add a Platinum pager frame: an idle desktop as a thin grey outline, a hovered desktop as the pale grey view trough, and the current desktop as the lavender selection fill. The reference set shows no virtual-desktop pager, so this is our own Platinum art; the three prefixes are KDE-required and the colours reuse grounded palette tokens.

**Approach.**
- Add `theme/desktoptheme/org.macos8.desktop/widgets/pager.svg` on a 12x9 canvas: a 1px border around a 10x7 centre tile. It declares exactly these ids: `hint-tile-center`; for each prefix `normal`, `hover` and `active`, the four `-hint-{top,bottom,left,right}-margin` rects and the nine `-{top,bottom,left,right,center,topleft,topright,bottomleft,bottomright}` slice groups (39 ids besides `hint-tile-center`).
- Hints: `hint-tile-center` at (1,1,10,7); top/bottom margins at (1,0,10,1)/(1,8,10,1); left/right margins at (0,1,1,7)/(11,1,1,7). Slice groups translate to (1,0), (1,8), (0,1), (11,1), (1,1), (0,0), (11,0), (0,8) and (11,8).
- Paint the states as follows: `normal` is a 1px `#999999` border on its eight edge and corner tiles with a transparent 0.01-opacity `#FFFFFF` placeholder for the centre (an idle desktop is an outlined cell on the panel face); `hover` is the same `#999999` border around a flat `#EEEEEE` centre; `active` is a 1px `#000000` border around a flat `#CCCCFF` centre. Each colour is a `fill` attribute; the centre placeholder uses `style` plus `fill-opacity="0.01"`, the menubaritem convention, so the parsed fill set stays the art colours.
- `tests/support/desktoptheme_paths.py`: add `PAGER_SVG = os.path.join(PACKAGE, "widgets", "pager.svg")`.
- `tests/test_desktoptheme.py`: import `PAGER_SVG` and add `("pager.svg", PAGER_SVG, 12, 9)` to `SVG_CANVASES`, so the shared root-canvas, unique-id, self-containment and registry tests cover the new file.
- Add `tests/test_desktoptheme_pager.py` with `TestPager(NineSliceCase)`: set `SVG_PATH = PAGER_SVG` and `PREFIXES = ("normal", "hover", "active")`; pin the exact 40-id set and the exact hint map with `rect_geometry`; pin `normal`'s eight `#999999` edge tiles plus its fill-less centre (`fill-opacity` set exactly `{"0.01"}`); pin every `hover` tile to `#999999` on the border and `#EEEEEE` in the centre; pin every `active` tile to `#000000` on the border and `#CCCCFF` in the centre; pin the parsed `fill` set to exactly `{"#000000", "#999999", "#CCCCFF", "#EEEEEE"}`. Use `nine_slice_tile_sizes(12, 9, 1, 1, 1, 1)` and `assert_slice_pixels` so a one-pixel-short rect or a recoloured tile fails.
- `README.md`: after the `widgets/menubaritem.svg` sentence, add that `widgets/pager.svg` draws the optional Pager's virtual-desktop cells: an idle `#999999` outline, a hovered `#EEEEEE` fill and the current desktop's `#CCCCFF` selection, as one 1px-border nine-slice shared by such a panel applet.
- `docs/invariants.md`: add a `## desktoptheme` row for `widgets/pager.svg`, citing `tests/test_desktoptheme_pager.py::TestPager`; its provenance exception records that no reference screenshot shows a virtual-desktop pager, the `normal`/`hover`/`active` prefixes are KDE-required (read from the installed Pager's `contents/ui/main.qml`), the 12x9 tile is this theme's own, and the colours reuse the grounded bevel, trough, outline and selection anchors.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/pager.svg`, `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme.py`, new `tests/test_desktoptheme_pager.py`, `README.md`, `docs/invariants.md`.

**Acceptance criteria.**
- `pager.svg` exists on a 12x9 canvas and declares exactly the id set above; `tests/test_desktoptheme.py`'s registry sees it, and a missing or extra prefix, hint or slice id fails the id-set test.
- Every prefix's four hints and nine slice groups sit at the geometry above; moving a group or hint off its tile fails `NineSliceCase.test_tiles_placed_by_margins` or the hint-map test.
- `normal` renders eight `#999999` border tiles around a fill-less centre, `hover` renders `#999999` borders around an `#EEEEEE` centre, and `active` renders `#000000` borders around an `#CCCCFF` centre; changing one pixel, dropping a state or recolouring a slice fails the pixel tests.
- The README names the new widget and its three states, and `tests/invariants.py` accepts the new `## desktoptheme` row.
- `make check` is green.

### Platinum pointer roles: ship the context-menu pointer and alias the resize, hand and cell roles (planned 2026-10-23 by the plan role; independent of the waiting pager plan)

**Goal.** The icon theme's `cursors/` names the Platinum pointers for the arrow, text, hand, busy, move, resize, crosshair, forbidden, drag-and-drop, help, progress, pencil and zoom roles, but several common Xcursor names still come from the fallback Breeze set: right-click uses `context-menu`, table and splitter borders use `col-resize`/`split_h` and `row-resize`/`split_v`, panning uses `openhand`/`closedhand`, and cell selection uses `cell`/`plus`. Add one new Platinum pointer for `context-menu` (the arrow beside a small menu panel) and alias the role-equivalent names to the already-shipped resize, grab and copy-plus art, so those roles stop changing shape when the Platinum cursor theme is selected. No reference screenshot shows a pointer, so the art stays our own `#000000`-face/`#FFFFFF`-outline drawing; the names and their Breeze byte groups are X/KDE-required values read from `/usr/share/icons/breeze_cursors/cursors` (`alias` and `link` share one file there, as do `cell` and `plus`, `col-resize` and `split_h`, `row-resize` and `split_v`, `openhand` and `grab`, and `closedhand` and `grabbing`).

**Approach.**
- `tools/cursor_art.py`: add `CONTEXT_MENU_HOTSPOT = (1, 1)` and `CONTEXT_MENU_GRID`, the arrow with a white-faced, black-bordered menu panel at x=8..14, y=9..14 carrying two black text bars:

  ```python
  CONTEXT_MENU_GRID = (
      "...             ",
      ".#..            ",
      ".##..           ",
      ".###..          ",
      ".####..         ",
      ".#####..        ",
      ".######..       ",
      ".#######..      ",
      ".########.      ",
      "   .##..#######.",
      "   .##..#.....#.",
      "   .##..#.###.#.",
      "   .##..#.....#.",
      "   .##..#.##..#.",
      "   .##..#######.",
      "   ....         ",
  )
  ```

  Append `("context-menu", CONTEXT_MENU_GRID, CONTEXT_MENU_HOTSPOT, ())` to `CURSORS`, and extend the existing alias tuples: `size_hor` gains `col-resize` and `split_h`; `size_ver` gains `row-resize` and `split_v`; `dnd-copy` gains `cell` and `plus`; `grab` gains `openhand`; `grabbing` gains `closedhand`. Update the module docstring: the package ships twenty canonical pointers, and list `context-menu` and the new aliases.
- Run `python3 tools/make_cursors.py` to write `theme/icons/org.macos8.desktop/cursors/context-menu` and the eight new alias files. The alias files must be byte-identical to their canonical cursor, and the existing files must keep their bytes.
- `tests/test_cursors_theme.py`: add `context-menu` to `CANONICAL`, `ALIASES` (empty), `HOTSPOTS` (16 `(1, 1)`, 24 `(2, 2)`, 32 `(2, 2)`) and `PINNED_PIXELS` (face `(1, 1)`, outline `(0, 0)`); add the new aliases to the matching `ALIASES` tuples. Leave `TRANSPARENT_CORNER_CURSORS` unchanged: like `help` and `progress`, the context-menu pointer keeps the arrow's white top-left corner. Add `test_context_menu_pins_the_menu_panel`: at 16px black at `(1, 1)`, `(8, 9)`, `(8, 10)`, `(14, 10)`, `(10, 11)` and `(8, 14)`; white at `(0, 0)`, `(7, 10)`, `(9, 10)` and `(15, 10)`. Extend `test_dnd_aliases_reuse_the_landed_glyphs` with `cell`/`plus` -> `dnd-copy`, `col-resize`/`split_h` -> `size_hor`, `row-resize`/`split_v` -> `size_ver`, `openhand` -> `grab` and `closedhand` -> `grabbing`.
- `tests/test_icon_theme.py`: add `context-menu` and the eight new alias names to `SHIPPED_CURSORS`, so the installed-package inventory test sees them.
- `README.md`: in the cursor sentence, name the new `context-menu` pointer and add each new alias to its existing group (`cell`, `plus` with `dnd-copy`; `col-resize`, `split_h` with `size_hor`; `row-resize`, `split_v` with `size_ver`; `openhand` with `grab`; `closedhand` with `grabbing`), and narrow the fallback sentence to the roles the theme still does not name.
- `docs/invariants.md`: extend the `icons` cursor row's canonical and alias lists with the new names; keep the provenance exception that no reference screenshot shows a pointer and that the names and byte groups are X/KDE-required.

**Files touched.** `tools/cursor_art.py`, `theme/icons/org.macos8.desktop/cursors/context-menu` and eight new alias files (generated), `tests/test_cursors_theme.py`, `tests/test_icon_theme.py`, `README.md`, `docs/invariants.md`.

**Acceptance criteria.**
- `cursors/context-menu` exists at nominal sizes 16, 24 and 32, with the hotspot at the arrow tip and a fresh-generator result; the focused pixel test fails if the menu panel or its text bars move.
- `cell`, `plus`, `col-resize`, `split_h`, `row-resize`, `split_v`, `openhand` and `closedhand` are byte-identical to `dnd-copy`, `size_hor`, `size_ver`, `grab` and `grabbing` as mapped above, and `tests/test_icon_theme.py` sees every new file.
- The README and the `icons` invariant row name the new pointer and aliases, `tests/invariants.py` accepts the row, and `make check` is green.

## Done
