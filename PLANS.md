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
(startup splash, desktop layout, defaults); the desktop theme (twenty-five widget SVGs under
`widgets/`, including the `widgets/margins-highlight.svg` panel edit-mode margin highlight,
plus `dialogs/background.svg`; the panel resize and slider handles in
`widgets/containment-controls.svg` still come from the default theme); the Aurorae window decoration (frame, close, zoom and
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
NW-SE and NE-SW diagonal resize arrows, crosshair and circle-slash, not traced from Apple's
artwork), it
has landed inside the icon theme package with its provenance exception recorded in
`docs/invariants.md`, and `make apply-cursor`/`make remove-cursor` link it into the Xcursor path
and select it; drag-and-drop (`dnd-*`), grab, help, progress, zoom and the separate
`forbidden`/`no-drop` pointers still come from the fallback cursor theme; **system sounds** are out
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

### Platinum cursor set, part 3: ship the drag-and-drop, grab and forbidden pointers (planned 2026-10-23 by the plan role; follows the landed resize/diagonal/crosshair/not-allowed set)

**Goal.** The icon theme's `cursors/` covers the arrow, text I-beam, pointing hand, busy
hourglass, move cross, the four resize arrows, the crosshair and the circle-slash, and README
records that drag-and-drop (`dnd-*`), grab, the separate `forbidden`/`no-drop` pointers, help,
progress, zoom and pencil still come from the fallback cursor theme. Add the drag-and-drop and
grab pointers: a new `dnd-copy` (white-outlined black copy plus), the landed four-way cross as
`dnd-move`, the landed arrow as `dnd-none`, the landed circle-slash as
`dnd-no-drop`/`no-drop`/`forbidden`, and the new `grab` (open hand) and `grabbing` (closed fist)
cursors. `help`, `progress`, `pencil`, `zoom-in` and `zoom-out` stay on the fallback theme and
are a later entry. No reference screenshot shows a pointer, so the art stays our own
`#000000`-face/`#FFFFFF`-outline drawing; the canonical names are X/KDE-required, taken from the
installed Breeze cursor set (`/usr/share/icons/breeze_cursors/cursors` ships exactly the four
`dnd-copy`/`dnd-move`/`dnd-no-drop`/`dnd-none` drag names, plus `forbidden`, `no-drop`, `grab` and
`grabbing`). The alias grouping is this theme's choice: Breeze's own byte groups are not copied.

**Approach.**
- `tools/make_cursors.py`: add three 16x16 grids in the existing `#` face / `.` white / space
transparent vocabulary and wire them into `CURSORS`; `cursor_bytes`, `NOMINAL_SIZES` and `main`
need no change.
  - `DND_COPY_HOTSPOT = (7, 7)`; `DND_COPY_GRID` -- a symmetric black plus whose vertical bar is
column 7 on rows 2-12 and horizontal bar is row 7 on columns 2-12, one white outline cell around
every black edge, transparent corners; `(7, 7)` is black and `(6, 7)` is white.
  - `GRAB_HOTSPOT = (7, 7)`; `GRAB_GRID` -- an open hand: four 1px black fingers at columns 3, 6,
9 and 12 on rows 2-9, separated by white outline columns, over a black palm on rows 10-13 with a
white outline along its sides and bottom; the fingertips are black at row 2 and the palm is black
at `(7, 12)`, its left edge white at `(1, 12)`.
  - `GRABBING_HOTSPOT = (7, 7)`; `GRABBING_GRID` -- the same hand closed into a fist: a black block
on rows 5-13 with a white outline around it and the thumb folded across; row 2 is transparent (no
raised fingers) and the palm is black at `(7, 12)`, its left edge white at `(1, 12)`.
  - Append `("dnd-copy", DND_COPY_GRID, DND_COPY_HOTSPOT, ())`, `("grab", GRAB_GRID,
GRAB_HOTSPOT, ())` and `("grabbing", GRABBING_GRID, GRABBING_HOTSPOT, ())` to `CURSORS`; extend the
existing tuples so `fleur` also carries `dnd-move`, `left_ptr` also carries `dnd-none`, and
`not-allowed` also carries `forbidden`, `no-drop` and `dnd-no-drop` (byte-identical aliases).
  - Update the module docstring: the package ships fourteen canonical cursors, not eleven, and
list the new names and aliases.
- `tests/test_cursors_theme.py`: extend `CANONICAL` with `dnd-copy`, `grab` and `grabbing`, and
`ALIASES` with the three new canonical names (no aliases) plus `dnd-move` under `fleur`, `dnd-none`
under `left_ptr`, and `forbidden`/`no-drop`/`dnd-no-drop` under `not-allowed`. Add the three new
names to `HOTSPOTS` (`(7, 7)` at 16, `(11, 11)` at 24, `(14, 14)` at 32) and to `PINNED_PIXELS`
(face `(7, 7)` / outline `(6, 7)` for `dnd-copy`; face `(7, 12)` / outline `(1, 12)` for `grab` and
`grabbing`). Add `dnd-copy`, `grab` and `grabbing` to `TRANSPARENT_CORNER_CURSORS`. The existing
`TestCursorSet` loops then cover the new files, aliases, hotspots, face/outline pixels and
determinism. Add focused tests:
  - `test_dnd_copy_is_a_centred_plus`: at 16px, black at `(7, 2)`, `(7, 12)`, `(2, 7)`, `(12, 7)`
and `(7, 7)`; white at `(6, 7)` and `(7, 1)`; every corner transparent.
  - `test_grab_and_grabbing_pin_open_and_closed_hands`: at 16px both have black `(7, 12)` and white
`(1, 12)`; `grab` is black at the fingertip `(3, 2)` while `grabbing` is transparent there; the two
grids differ.
  - `test_dnd_aliases_reuse_the_landed_glyphs`: `dnd-move` is byte-identical to `fleur`, `dnd-none`
to `left_ptr`, and `forbidden`, `no-drop` and `dnd-no-drop` to `not-allowed`.
- Regenerate the artifacts with `python3 tools/make_cursors.py` (deterministic output).
- `tests/test_icon_theme.py`: add the eight new X names (`dnd-copy`, `dnd-move`, `dnd-none`,
`dnd-no-drop`, `forbidden`, `no-drop`, `grab`, `grabbing`) to `SHIPPED_CURSORS`, so the shipped-file
registry and the shared install-lifecycle list cover them.
- `README.md`: in the cursor sentence name the new pointers and aliases, and narrow the fallback
sentence to the `help`, `progress`, `pencil`, `zoom-in` and `zoom-out` pointers.
- `docs/invariants.md`: extend the `## icons` cursor row to name all fourteen canonical files and
every alias, still citing `tests/test_cursors_theme.py::TestCursorArtifact` and
`::TestCursorSet`. Extend the provenance exception: no reference screenshot shows the pointer; the
drag-and-drop, grab and forbidden names are X/KDE-required and taken from the installed Breeze set,
while grouping `dnd-move` with `fleur`, `dnd-none` with `left_ptr` and
`dnd-no-drop`/`no-drop`/`forbidden` with `not-allowed` is this theme's own choice.
- `PLANS.md`: in the scope-drift paragraph, add the drag-and-drop, grab and forbidden pointers to
the shipped cursor clause, and state that `help`, `progress`, `pencil`, `zoom-in` and `zoom-out`
still fall back.

**Files touched.** `tools/make_cursors.py`, `tests/test_cursors_theme.py`,
`tests/test_icon_theme.py`, the new binaries under `theme/icons/org.macos8.desktop/cursors/`
(three canonical names and five alias names), `README.md`, `docs/invariants.md`, `PLANS.md`.

**Acceptance criteria.**
- `python3 tools/make_cursors.py` writes the three new canonical files and the five aliases;
running it twice leaves every committed cursor byte-identical, and each new canonical parses to
three chunks at nominal sizes 16/24/32 with its pinned hotspot, black face pixel, white outline
pixel and transparent corners.
- `dnd-copy` draws the pinned centred plus, `grab` draws the open hand with black fingertips and
`grabbing` the closed fist with transparent finger cells; deleting a grid, dropping a size,
moving a hotspot, redrawing the plus off-centre or making `grabbing` a copy of `grab` fails a test.
- `dnd-move`, `dnd-none`, `forbidden`, `no-drop` and `dnd-no-drop` are byte-identical to their
canonical files; the generator writes exactly the eight new names into a temp directory.
- `tests/test_icon_theme.py`'s shipped-file registry and install lifecycle include all eight new
names, README and `docs/invariants.md` name them, and `tests/invariants.py` accepts the updated
`## icons` row; the scope-drift clause names only help, progress, pencil and zoom as fallback.
- `make check` is green.

### Platinum panel edit-mode chrome, part 2/2: ship the panel resize and slider handles (planned 2026-10-23 by the plan role; follows the landed part 1/2 margin highlight)

**Goal.** The desktop theme ships no `widgets/containment-controls.svg`, so while a panel is in
edit mode its offset, minimum and maximum drag handles and its centre indicators come from the
default theme's blue-grey artwork. Ship our own `widgets/containment-controls.svg` for the
fourteen element ids the installed panel configuration resolves, drawn as raised Platinum
thumbs with lavender centre lines. No reference screenshot shows panel edit mode, so the art is
our own: the ids and natural indicator sizes are KDE-required (taken from the installed default
theme and the two consumers), while the colours reuse the grounded Platinum face/bevel palette
and the `#CCCCFF` selection anchor.

**Approach.**
- New `theme/desktoptheme/org.macos8.desktop/widgets/containment-controls.svg`: a `<svg
width="42" height="42" viewBox="0 0 42 42">` whose fourteen consumers are id-bearing `<g>`
elements at the origin, each holding rects with 0-based coordinates so KSvg reads that group's
bounding box as its natural size. Open with a comment naming the consumers
(`PanelConfiguration.qml` sets the north/south/east/west prefix, `Ruler.qml` asks for the two
centre indicators, and `SliderHandle.qml` builds `prefix + '-' + graphicElementName`), the ids,
and the provenance exception.
  - The twelve slider groups are `north-offsetslider`, `north-minslider`, `north-maxslider`,
`north` repeated for `south`, `east` and `west`. Each is a 9x9 raised Platinum thumb painted in
this document order (later rects override earlier ones, the slider.svg rule):
`<rect width="9" height="9" fill="#DDDDDD"/>`; `<rect y="1" width="9" height="1"
fill="#FFFFFF"/>`; `<rect y="7" width="9" height="1" fill="#999999"/>`; `<rect x="1"
width="1" height="9" fill="#FFFFFF"/>`; `<rect x="7" width="1" height="9"
fill="#999999"/>`; then the four outline rects `<rect width="9" height="1"
fill="#000000"/>`, `<rect y="8" width="9" height="1" fill="#000000"/>`, `<rect width="1"
height="9" fill="#000000"/>` and `<rect x="8" width="1" height="9" fill="#000000"/>`.
  - The grip is the last rect of each slider group: the three offset sliders carry a 3x3 black
centre dot `<rect x="3" y="3" width="3" height="3" fill="#000000"/>`; the north/south
min/max sliders carry a vertical 1x5 black bar `<rect x="4" y="2" width="1" height="5"
fill="#000000"/>`; the east/west min/max sliders carry the horizontal 5x1 bar `<rect x="2"
y="4" width="5" height="1" fill="#000000"/>`.
  - The two centre indicators are `vertical-centerindicator` (a vertical panel stretches it
across the panel width) with one `<rect width="42" height="1" fill="#CCCCFF"
fill-opacity="0.4"/>`, and `horizontal-centerindicator` (a horizontal panel stretches it down
the panel height) with one `<rect width="1" height="42" fill="#CCCCFF"
fill-opacity="0.4"/>`. The 42x1/1x42 natural geometry and the 0.4 opacity are the installed
default theme's; the colour is the grounded selection lavender.
- `tests/support/desktoptheme_paths.py`: add `CONTAINMENT_CONTROLS_SVG` pointing at
`widgets/containment-controls.svg`.
- `tests/test_desktoptheme.py`: add `("containment-controls.svg", CONTAINMENT_CONTROLS_SVG,
42, 42)` to `SVG_CANVASES` and `os.path.join("widgets", "containment-controls.svg")` to
`TestInstall.INSTALLED_FILES`, so the canvas, unique-id, self-containment, registry-completeness
and install-lifecycle checks cover the new file.
- New `tests/test_desktoptheme_containmentcontrols.py` (`SvgCase`, `SVG_PATH =
CONTAINMENT_CONTROLS_SVG`):
  - `test_containment_controls_contract`: all fourteen ids are present, ids are unique, and the
file has no script, style or external reference.
  - `test_sliders_are_raised_platinum_thumbs_with_grips`: render each of the twelve slider
groups with `render_slices` and compare its full pixel map to `raised_thumb_pixels(9, 9)` from
`support.thumb_fixtures` with the pinned grip pixels overwritten to `BLACK` -- the 3x3 dot for
the offset sliders, the vertical 1x5 bar for north/south min/max, the horizontal 5x1 bar for
east/west min/max. This pins every pixel, the 9x9 natural size and the grip orientation, so a
shifted bevel, a resized group or a swapped grip fails.
  - `test_center_indicators_are_lavender_lines`: each indicator group renders exactly 42
`SELECTION` pixels in the pinned 42x1 or 1x42 shape, and each of its rects carries
`fill-opacity="0.4"`.
  - `test_containment_controls_colours`: `assert_fill_palette(self, self.tree,
extra={SELECTION})`, so the parsed fill set is exactly the Platinum face/bevel palette plus the
selection lavender.
- `README.md`: replace the sentence that says the panel resize and slider handles still come from
the fallback theme with one naming `widgets/containment-controls.svg`, its twelve offset/min/max
sliders and its two centre indicators.
- `docs/invariants.md`: add a `## desktoptheme` row stating that the panel edit-mode sliders are
raised Platinum thumbs and the centre indicators lavender lines, pinned by
`tests/test_desktoptheme_containmentcontrols.py::TestContainmentControls`; the provenance
exception records that no reference screenshot shows panel edit mode, the fourteen ids and the
42x1/1x42 indicator geometry plus 0.4 opacity are KDE-required, and the colours reuse the
grounded Platinum and selection anchors.
- `PLANS.md`: in the scope-drift paragraph, change the widget-SVG count from twenty-five to
twenty-six, name the new containment-controls file, and drop the claim that its handles still
come from the default theme.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/containment-controls.svg` (new),
`tests/test_desktoptheme_containmentcontrols.py` (new),
`tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme.py`, `README.md`,
`docs/invariants.md`, `PLANS.md`.

**Acceptance criteria.**
- The new SVG parses as a 42x42 canvas with the fourteen pinned ids present and unique, every
slider group rendering as the pinned 9x9 raised thumb plus its orientation's grip, and the two
indicator groups rendering as the pinned 42x1 or 1x42 lavender line at 0.4 opacity.
- The parsed fill set is exactly `#000000`, `#FFFFFF`, `#999999`, `#DDDDDD` and `#CCCCFF`;
dropping an id, resizing a group, swapping a bevel colour or turning a grip the wrong way fails
a test.
- `TestSvgRootCanvas`'s registry and `TestInstall.INSTALLED_FILES` cover the new file,
`tests/invariants.py` accepts the new `## desktoptheme` row, and README and the scope-drift
paragraph name it with the scope-drift count at twenty-six.
- `make check` is green.

## Done
