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

### Platinum icon theme, part 1/2: ship 16x16 and 22x22 renditions of the folder, directory and Trash icons (planned 2026-10-23 by the plan role; part 2/2 adds the hard-disk and document renditions)

**Goal.** `theme/icons/org.macos8.desktop/index.theme` declares `16x16/places` and `22x22/places`, but those directories hold no `folder`, `inode-directory`, `user-trash` or `user-trash-full` file: the package ships those four names only at 32x32. Add eight pixel-aligned renditions so a menu, tree view or small desktop icon can draw a dedicated Platinum shape at its own size instead of relying on the 32x32 art. The 32x32 art is our own drawing, and `docs/invariants.md`'s `## icons` row records that the reference set has no pixel ground truth for the icon theme; these renditions are our own simplified redraws using only the four pinned palette fills (`#000000` outline, `#DDDDDD` face, `#FFFFFF` top/left bevel, `#999999` bottom/right bevel), not traced from Apple's artwork.

**Approach.**
- Add these files, each an `<svg>` whose `width`, `height` and `viewBox` are the directory's declared size:
  - `theme/icons/org.macos8.desktop/16x16/places/folder.svg` (six elements, in order): path `M1 4 h5 l2 2 h6 v7 H1 Z` `#000000`; path `M2 5 h4 l2 2 h5 v4 H2 Z` `#DDDDDD`; path `M2 5 h4 l2 2 h5 v1 h-5 l-2 -2 h-4 Z` `#FFFFFF`; rect `x=2 y=5 width=1 height=6` `#FFFFFF`; rect `x=2 y=11 width=11 height=1` `#999999`; rect `x=12 y=8 width=1 height=3` `#999999`.
  - `theme/icons/org.macos8.desktop/22x22/places/folder.svg` (six elements): path `M2 6 h7 l3 3 h8 v9 H2 Z` `#000000`; path `M3 7 h6 l3 3 h7 v6 H3 Z` `#DDDDDD`; path `M3 7 h6 l3 3 h7 v1 h-7 l-3 -3 h-6 Z` `#FFFFFF`; rect `x=3 y=7 width=1 height=8` `#FFFFFF`; rect `x=3 y=15 width=16 height=1` `#999999`; rect `x=18 y=10 width=1 height=5` `#999999`.
  - `theme/icons/org.macos8.desktop/16x16/places/inode-directory.svg` and `22x22/places/inode-directory.svg`: the same drawing elements as the matching `folder.svg`, in the same order; only the comment differs, saying the alias shares the folder geometry because Mac OS 8.6 draws one folder shape for both names.
  - `theme/icons/org.macos8.desktop/16x16/places/user-trash.svg` (ten elements): rect `x=6 y=1 width=4 height=2` `#000000`; rect `x=7 y=2 width=2 height=1` `#DDDDDD`; rect `x=3 y=3 width=10 height=3` `#000000`; rect `x=4 y=4 width=8 height=2` `#DDDDDD`; rect `x=4 y=4 width=8 height=1` `#FFFFFF`; rect `x=4 y=5 width=8 height=1` `#999999`; path `M5 6 h6 l-1 9 H6 Z` `#000000`; path `M6 7 h4 l-1 7 H7 Z` `#DDDDDD`; rect `x=8 y=8 width=1 height=5` `#999999`; rect `x=9 y=8 width=1 height=5` `#FFFFFF`.
  - `theme/icons/org.macos8.desktop/22x22/places/user-trash.svg` (twelve elements): rect `x=8 y=1 width=6 height=3` `#000000`; rect `x=9 y=2 width=4 height=2` `#DDDDDD`; rect `x=4 y=4 width=14 height=4` `#000000`; rect `x=5 y=5 width=12 height=3` `#DDDDDD`; rect `x=5 y=5 width=12 height=1` `#FFFFFF`; rect `x=5 y=7 width=12 height=1` `#999999`; path `M7 8 h8 l-2 12 H8 Z` `#000000`; path `M8 9 h6 l-2 10 H9 Z` `#DDDDDD`; rect `x=9 y=11 width=1 height=8` `#999999`; rect `x=10 y=11 width=1 height=8` `#FFFFFF`; rect `x=12 y=11 width=1 height=8` `#999999`; rect `x=13 y=11 width=1 height=8` `#FFFFFF`.
  - `theme/icons/org.macos8.desktop/16x16/places/user-trash-full.svg` (ten elements): the two paper paths path `M6 0 l2 1 l2 -1 l1 4 h-6 Z` `#000000` and path `M7 1 l1 1 l1 -1 l1 3 h-4 Z` `#FFFFFF`, then the `user-trash.svg` elements from its rim outline through its white rib (elements 3-10 above), in the same order.
  - `theme/icons/org.macos8.desktop/22x22/places/user-trash-full.svg` (fourteen elements): the two paper paths path `M8 0 l3 2 l3 -2 l1 6 h-8 Z` `#000000` and path `M9 1 l2 1 l2 -1 l1 4 h-6 Z` `#FFFFFF`, then the `22x22/places/user-trash.svg` elements from its rim outline through its last white rib (elements 3-12 above), in the same order.
- `theme/icons/org.macos8.desktop/index.theme`: no change; `16x16/places` and `22x22/places` are already declared with `Size=16`/`Size=22`, `Context=Places` and `Type=Fixed`.
- `tests/test_icon_theme.py`: add the eight new paths to `SHIPPED_ICONS`; add each file to `ICON_SHAPES` with the exact element tuple listed above, using the existing `_shape` helper and the same document order. Extend `TestIconGeometry.test_the_folder_alias_shares_the_folder_art` to compare the `folder.svg` and `inode-directory.svg` drawings at 16x16, 22x22 and 32x32, so the alias cannot drift at a new size.
- `README.md` and `docs/invariants.md`: no change here. The existing README sentence names the icon art without claiming a size, and the existing `## icons` guarantee (`Every shipped icon draws its pinned drawing elements in document order`) already covers these files because `TestIconGeometry.test_the_geometry_registry_covers_every_shipped_icon` requires `ICON_SHAPES` to equal `SHIPPED_ICONS`. Part 2/2 updates the README sentence once the complete set of renditions ships.

**Files touched.** `tests/test_icon_theme.py` and eight new SVGs under `theme/icons/org.macos8.desktop/16x16/places/` and `22x22/places/`.

**Acceptance criteria.**
- The eight files exist; each parses as an SVG whose width, height and viewBox equal 16 or 22, each fill is one of the four `PLATINUM_FILLS`, and each has no script, style, external reference or duplicate id.
- `TestIndex` sees the eight files in its declared directories, `TestIconGeometry.test_the_geometry_registry_covers_every_shipped_icon` sees `ICON_SHAPES` equal to the shipped set, and every new file's drawing elements equal the tuple above in document order.
- The `inode-directory` drawing elements equal the matching `folder` elements at 16x16, 22x22 and 32x32.
- Deleting an element, changing a coordinate or fill, moving an element, dropping a size, or drawing an alias differently from its folder fails a test.
- `make check` is green.

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

## Done
