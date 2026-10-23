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

### Platinum icon theme, part 2/2: ship 16x16 and 22x22 renditions of the hard-disk and document icons (planned 2026-10-23 by the plan role; "requires part 1/2 landed")

**Goal.** After part 1/2 the places icons have small-size renditions, but `drive-harddisk` and `text-x-generic` still ship only at 32x32, and `index.theme` declares no 16x16 or 22x22 devices or mimetypes directory. Add four renditions and the four directory declarations so the hard disk and document icons also have purpose-drawn art at menu, tree-view and small desktop sizes. The art is our own drawing on the same four-fill Platinum palette as the places art; the reference set has no pixel ground truth for the icon theme, as `docs/invariants.md`'s `## icons` row records.

**Approach.**
- Add these files, each an `<svg>` whose `width`, `height` and `viewBox` are the declared size:
  - `theme/icons/org.macos8.desktop/16x16/devices/drive-harddisk.svg` (nine elements): rect `x=1 y=3 width=14 height=10` `#000000`; rect `x=2 y=4 width=12 height=8` `#DDDDDD`; rect `x=2 y=4 width=12 height=1` `#FFFFFF`; rect `x=2 y=4 width=1 height=8` `#FFFFFF`; rect `x=2 y=11 width=12 height=1` `#999999`; rect `x=13 y=4 width=1 height=8` `#999999`; rect `x=3 y=7 width=7 height=3` `#000000`; rect `x=4 y=8 width=5 height=1` `#FFFFFF`; circle `cx=12 cy=9 r=1` `#000000`.
  - `theme/icons/org.macos8.desktop/22x22/devices/drive-harddisk.svg` (nine elements): rect `x=2 y=4 width=18 height=15` `#000000`; rect `x=3 y=5 width=16 height=13` `#DDDDDD`; rect `x=3 y=5 width=16 height=2` `#FFFFFF`; rect `x=3 y=5 width=1 height=13` `#FFFFFF`; rect `x=3 y=17 width=16 height=1` `#999999`; rect `x=18 y=5 width=1 height=13` `#999999`; rect `x=4 y=10 width=9 height=4` `#000000`; rect `x=5 y=11 width=7 height=2` `#FFFFFF`; circle `cx=15 cy=12 r=2` `#000000`.
  - `theme/icons/org.macos8.desktop/16x16/mimetypes/text-x-generic.svg` (six elements): path `M3 1 h7 l3 3 v10 H3 Z` `#000000`; path `M4 2 h6 l3 3 v8 H4 Z` `#FFFFFF`; path `M10 2 L13 2 L13 5 Z` `#DDDDDD`; rect `x=5 y=7 width=6 height=1` `#999999`; rect `x=5 y=9 width=6 height=1` `#999999`; rect `x=5 y=11 width=4 height=1` `#999999`.
  - `theme/icons/org.macos8.desktop/22x22/mimetypes/text-x-generic.svg` (six elements): path `M4 1 h10 l4 4 v15 H4 Z` `#000000`; path `M5 2 h9 l4 4 v13 H5 Z` `#FFFFFF`; path `M14 2 L18 2 L18 6 Z` `#DDDDDD`; rect `x=7 y=10 width=8 height=1` `#999999`; rect `x=7 y=13 width=8 height=1` `#999999`; rect `x=7 y=16 width=5 height=1` `#999999`.
- `theme/icons/org.macos8.desktop/index.theme`: append `16x16/devices,16x16/mimetypes,22x22/devices,22x22/mimetypes` to `Directories`, and add four sections with `Size=16`/`Size=22`, `Context=Devices`/`Context=MimeTypes` and `Type=Fixed`.
- `tests/test_icon_theme.py`: add the four new paths to `SHIPPED_ICONS`; add each file to `ICON_SHAPES` with the exact element tuple above, using the existing `_shape` helper and document order. `TestIndex.test_every_shipped_icon_lives_in_a_declared_size_directory` then proves the four new directories are declared.
- `README.md`: in the icon-theme sentence (the lines that currently read `ships our own Platinum-style art for the desktop's hard-disk, folder, document, Trash and full-Trash icons`), add that the package draws these at 32x32 with 16x16 and 22x22 renditions. Do not touch the cursor sentence on the following line.

**Files touched.** `tests/test_icon_theme.py`, `theme/icons/org.macos8.desktop/index.theme`, `README.md`, and four new SVGs under `theme/icons/org.macos8.desktop/16x16/{devices,mimetypes}/` and `22x22/{devices,mimetypes}/`.

**Acceptance criteria.**
- The four files exist; each parses as an SVG whose width, height and viewBox equal 16 or 22, each fill is one of the four `PLATINUM_FILLS`, and each has no script, style, external reference or duplicate id.
- `index.theme` declares `16x16/devices`, `16x16/mimetypes`, `22x22/devices` and `22x22/mimetypes` in `Directories`, with the matching `Size`, `Context` and `Type` sections; `TestIndex` passes for every shipped icon.
- `ICON_SHAPES` equals `SHIPPED_ICONS`, and each new file's drawing elements equal the tuple above in document order. Deleting an element, changing a coordinate or fill, moving an element or dropping a size fails a test.
- The 32x32 art and the part 1/2 places renditions keep their pinned elements unchanged.
- `README.md` names the 16x16 and 22x22 renditions without claiming a size for the cursor set, and the cursor sentence is untouched.
- `make check` is green.

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

## Done
