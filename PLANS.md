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
(startup splash, desktop layout, defaults); the desktop theme (twenty-six widget SVGs under
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

### Platinum task-manager buttons: ship `widgets/tasks.svg` for the optional Task Manager applet (planned 2026-10-23 by the plan role; independent of the waiting icon series)

**Goal.** The default layout draws the window list with `widgets/menubaritem.svg`, but the optional Task Manager (`org.kde.plasma.taskmanager`) draws every task through `KSvg.FrameSvgItem imagePath: "widgets/tasks"` (`Task.qml`, `main.qml`, `TaskProgressOverlay.qml`, `GroupExpanderOverlay.qml`). The theme ships no `widgets/tasks.svg`, so KSvg falls back to Breeze's task backgrounds and a Task Manager added to the Platinum menu bar draws Breeze task items instead of Platinum ones. Add the missing nine-slice and its four group-expander arrows. The reference set shows no KDE task manager, so this is our own Platinum art; the element names are KDE-required and the colours reuse the already-grounded tokens (#CCCCFF selection, #FFFFCC tooltip, #999999 bevel, #FFFFFF placeholder).

**Approach.**
- Add `theme/desktoptheme/org.macos8.desktop/widgets/tasks.svg` on the same 20x12 canvas and 7px left/right, 3px top/bottom, 6x6-centre contract as `widgets/menubaritem.svg`. It declares exactly these ids: `hint-tile-center`; for each prefix `normal`, `hover`, `focus`, `attention`, `minimized` and `progress`, the four `-hint-{top,bottom,left,right}-margin` rects and the nine `-{top,bottom,left,right,center,topleft,topright,bottomleft,bottomright}` slice groups; and `group-expander-{top,bottom,left,right}`.
- Every prefix's hints and slices use the menubaritem geometry: `hint-tile-center` at (7,3,6,6); top/bottom hints at (7,0,6,3)/(7,9,6,3); left/right hints at (0,3,7,6)/(13,3,7,6); slice groups translated to (7,0), (7,9), (0,3), (13,3), (7,3), (0,0), (13,0), (0,9) and (13,9).
- Paint the states as follows: `normal` is the transparent 0.01-opacity #FFFFFF placeholder in all nine tiles (an idle task shows the menu-bar face); `hover` and `focus` are flat #CCCCFF in every tile; `attention` is flat #FFFFCC in every tile; `minimized` is the placeholder in six tiles, but `minimized-bottom`, `minimized-bottomleft` and `minimized-bottomright` each paint a 2px #999999 rule at the bottom of their 3px band (local y=1, height 2; the bottom tile is 6px wide, the corner tiles 7px wide); `progress` is the same six placeholders with a 2px #CCCCFF bottom rule. The transparent states keep the `fill-opacity="0.01"` placeholder convention so the existing no-fill helpers read them as empty.
- Ship only the bare state prefixes. `TaskTools.taskPrefix` in the installed task manager's `code/tools.js` returns `[edge-prefixed, bare]` for every state, and `taskPrefixHovered` appends `hover` before the base state, so the bare `normal`/`hover`/`focus`/`attention`/`minimized`/`progress` elements resolve on a top, bottom, left or right panel without duplicating the art four ways. The group overlay is the exception: it names `elementId: "group-expander-<edge>"` directly, so ship all four arrows.
- Draw each group expander as an 8x8 black triangle: top `M1 6 L4 3 L7 6 Z`, bottom `M1 2 L4 5 L7 2 Z`, left `M6 1 L3 4 L6 7 Z`, right `M2 1 L5 4 L2 7 Z`.
- `tests/support/desktoptheme_paths.py`: add `TASKS_SVG = os.path.join(PACKAGE, "widgets", "tasks.svg")`.
- `tests/test_desktoptheme.py`: import `TASKS_SVG` and add `("tasks.svg", TASKS_SVG, 20, 12)` to `SVG_CANVASES`, so the shared root-canvas, unique-id, self-containment and registry tests cover the new file.
- Add `tests/test_desktoptheme_tasks.py` with `TestTasks(NineSliceCase)`: set `SVG_PATH = TASKS_SVG`, `PREFIXES = ("normal", "hover", "focus", "attention", "minimized", "progress")` and `EXTRA_GROUPS` mapping the four expander ids to (0,0); pin the exact hint map, the exact id set, the flat fills (`hover`/`focus` #CCCCFF, `attention` #FFFFCC), the `normal` placeholders, the minimized/progress bottom rules pixel by pixel, and each expander's path and fill.
- `README.md`: in the desktop-theme widget list, after the `widgets/menubaritem.svg` sentence, add that `widgets/tasks.svg` draws an optional Task Manager's idle (transparent), hover/focus (#CCCCFF), attention (#FFFFCC), minimized (#999999 rule) and progress (#CCCCFF rule) task faces as one 7px/3px nine-slice shared by every panel edge, plus the four group-expander arrows.
- `docs/invariants.md`: add a `## desktoptheme` row for `widgets/tasks.svg`, citing `tests/test_desktoptheme_tasks.py::TestTasks`; its provenance exception records that no reference screenshot shows a KDE task manager, the six state prefixes and four expander ids are KDE-required (read from the installed task manager's `Task.qml`, `TaskProgressOverlay.qml` and `GroupExpanderOverlay.qml`), and the colours reuse the grounded selection, tooltip and bevel tokens.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/tasks.svg`, `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme.py`, new `tests/test_desktoptheme_tasks.py`, `README.md`, `docs/invariants.md`.

**Acceptance criteria.**
- `tasks.svg` exists on a 20x12 canvas and declares exactly the id set above; `tests/test_desktoptheme.py`'s registry sees it, and a missing or extra prefix, hint or slice id fails the id-set test.
- Every prefix's four hints and nine slice groups sit at the menubaritem geometry; moving a group or hint off its tile fails `NineSliceCase.test_tiles_placed_by_margins` or the hint-map test.
- `normal` renders no fill (0.01-opacity #FFFFFF placeholders), `hover` and `focus` render flat #CCCCFF, `attention` flat #FFFFCC, and `minimized`/`progress` render a 2px #999999/#CCCCFF rule across the bottom band with transparent tiles above it; changing one pixel, dropping a state or recolouring a slice fails the pixel tests.
- The four `group-expander-*` elements are 8x8 black triangles with the paths above; removing or repointing one fails.
- The README names the new widget and its five states, and `tests/invariants.py` accepts the new `## desktoptheme` row.
- `make check` is green.

### Platinum virtual-desktop pager: ship `widgets/pager.svg` for the optional Pager applet (planned 2026-10-23 by the plan role; independent of the waiting task-manager plan)

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

## Done
