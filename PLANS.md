# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-18 by the clean role):** The initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (twenty-three widget SVGs under
`widgets/` plus `dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
collapse boxes); the desktop wallpaper package; the `org.macos8.desktop` icon theme (our own
final, non-infringing 32x32 Platinum-style art for the desktop's hard-disk, folder, document and
Trash icons, plus the menu bar's kicker logo `start-here-kde-symbolic`, our own mark rather than
Apple's; `PLACEHOLDERS.md` is empty); and the render and fidelity tooling
that checks them against `macos8.6-screenshots/`. README.md describes the reference set as the
source of truth for "menu bar, window chrome, widget metrics, icons and colour palette". The
prompt's surfaces the theme does not ship are each tracked here (updated 2026-10-18 by the plan
role): a **Qt widget style** for KDE applications (the desktop theme styles only Plasma shell
widgets, so a KDE app's own buttons, menus and scroll bars would keep the Breeze look) is served
by the global theme's selection of our Kvantum theme: the user answered
2026-10-18 that a pixel-matched Platinum style should ship as a Kvantum theme (a new
dependency) — shipped as the four-part "Mac OS 8.6 Kvantum widget style" series (each part
waited on the one before); a **cursor theme** is out of scope (no reference screenshot shows a
cursor, so no pixel ground truth exists to match); and **system sounds** are out of scope (not a
visual surface, so the reference set cannot ground them). The shipped work should not be treated
as the whole of the prompt.

### Mac OS 8.6 Platinum translucent applet background: ship `widgets/translucentbackground.svg` (planned 2026-10-18 by the plan role)

**Goal.** `BasicAppletContainer.qml` — the Plasma applet container the desktop containment uses for
applets placed on the desktop — picks its background from the applet's
`effectiveBackgroundHints`: the `TranslucentBackground` bit resolves to
`imagePath: "widgets/translucentbackground"`. The desktop theme ships no such file, so KSvg falls
back to the default theme's Breeze `translucentbackground.svgz`, a rounded translucent rectangle
that clashes with Platinum. Ship the Platinum body so those applet containers are Platinum too.

**Grounding.** `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/private/containmentlayoutmanager/BasicAppletContainer.qml`
chooses the path in `background.imagePath`: `effectiveBackgroundHints & TranslucentBackground` →
`widgets/translucentbackground`, else `& StandardBackground` → `widgets/background` (already
shipped), else `""`. The same item sets `prefix: blurEnabled ? "blurred" : ""`; `blurEnabled`
requires the `StandardBackground` bit, so a translucent-hint container reads the **unprefixed**
elements. The installed applets that set the bit are those with `PlasmaCore.Types.DefaultBackground`
(`= StandardBackground | TranslucentBackground`) — `org.kde.plasma.weather`, `org.kde.plasma.comic`
and `org.kde.plasma.systemmonitor` each set `Plasmoid.backgroundHints: PlasmaCore.Types.DefaultBackground
| PlasmaCore.Types.ConfigurableBackground`, and `BasicAppletContainer` tests `TranslucentBackground`
first, so they take the translucent path. Mac OS 8.6 has no translucent applet surface: no reference
screenshot shows one and every Platinum body is opaque, so the KDE-required translucent-hint surface
takes the same opaque Platinum body as the standard hint. No new palette value: the file is a
byte-identical copy of `widgets/background.svg` (the Platinum body the standard hint already draws),
exactly as `solid/widgets/tooltip.svg` copies `widgets/tooltip.svg`.

**Approach.**
- Add `theme/desktop-themes/org.macos8.desktop/widgets/translucentbackground.svg`, byte-identical to
`theme/desktop-themes/org.macos8.desktop/widgets/background.svg` (no header change, so the copy test
compares bytes).
- `tests/support/desktoptheme_paths.py`: add `TRANSLUCENT_BACKGROUND_SVG = os.path.join(PACKAGE,
"widgets", "translucentbackground.svg")` beside `BACKGROUND_SVG`.
- `tests/test_desktoptheme.py`: import `TRANSLUCENT_BACKGROUND_SVG`, add
`("translucentbackground.svg", TRANSLUCENT_BACKGROUND_SVG, 16, 16)` to `SVG_CANVASES` (so the
registry, canvas, id and self-containment tests cover it) and
`os.path.join("widgets", "translucentbackground.svg")` to `TestInstall.INSTALLED_FILES`.
- `tests/test_desktoptheme_background.py`: import `TRANSLUCENT_BACKGROUND_SVG` and add
`test_translucent_copy_is_identical` to `TestBackground`, opening `BACKGROUND_SVG` and
`TRANSLUCENT_BACKGROUND_SVG` in binary and asserting equal bytes (mirroring
`TestTooltip::test_solid_copy_is_identical`).
- `docs/invariants.md`: extend the desktop-themes `widgets/background.svg` row's guarantee to "…and
its `widgets/translucentbackground.svg` copy is byte-identical." The row already names
`TestBackground`, which holds the new test.
- `README.md`: in the `widgets/background.svg` sentence, add that a byte-identical copy ships at
`widgets/translucentbackground.svg`, where `BasicAppletContainer.qml` looks for a translucent-hint
applet container's background.

**Files touched.** `theme/desktop-themes/org.macos8.desktop/widgets/translucentbackground.svg`
(new), `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme.py`,
`tests/test_desktoptheme_background.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `widgets/translucentbackground.svg` is byte-identical to `widgets/background.svg`, asserted by
`TestBackground::test_translucent_copy_is_identical`.
- `test_registry_covers_every_shipped_svg` passes with the new file in `SVG_CANVASES`, and
`test_root_canvas_matches_the_artwork_layout`, `test_every_svg_declares_unique_ids` and
`test_every_svg_is_self_contained` cover it (its 16x16 canvas, unique ids, no style/script or
external reference).
- `TestInstall` still passes with the new file listed in `INSTALLED_FILES`.
- `make check` exits 0, including `tests/test_readme_theme_files.py` (the README prose names the
file) and `tests/test_invariants.py`.
- Removing `widgets/translucentbackground.svg` makes `test_translucent_copy_is_identical` fail (the
open raises) and `test_registry_covers_every_shipped_svg` fail (the shipped set no longer equals
the registry).

## Done

### Mac OS 8.6 grey menu body: ground `widgets/background.svg` in the open Apple menu (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** `theme/desktop-themes/org.macos8.desktop/widgets/background.svg` paints the body of every
`PlasmaComponents.Menu` (context menus and combo-box dropdowns), `Drawer`, `Popup` and planar
applet container as a flat `#FFFFFF` face, and its comment justifies that with
`[Colors:View] BackgroundNormal`. But the open Apple menu in the retail screenshot
`macos8.6-screenshots/desktop_archiveorg8.6hd.png` — the same image
`tests/test_colorscheme_reference.py::TestReferenceAnchors` samples the menu-bar face from — has a
flat `#DDDDDD` body, the Platinum face, not white. Ship the reference's grey menu body and pin it
to the reference pixels.

**Reference.** The Apple menu is open in `desktop_archiveorg8.6hd.png`, dropping from the top-left
(its body spans roughly x=6..160, y=16..355). The menu's empty right margin, clear of item text and
icons, is flat `#DDDDDD`: (150, 60) = (221, 221, 221) and (150, 200) = (221, 221, 221). The Finder
window's content in the same image is white at (470, 300) — already the `[Colors:View]` anchor —
so the menu body is a distinct grey, not the View background. (The image is stored with Git LFS,
so a clone without it must skip this test, as `test_colorscheme_reference` does.)

**Approach.**
- `widgets/background.svg`: change the face — the centre tile and the interiors of the four edge
tiles — from `#FFFFFF` to `#DDDDDD`, keeping the 1px `#000000` outline and the 3px/10px nine-slice
contract. Rewrite the header comment's face paragraph: the body is the Platinum grey `#DDDDDD`
sampled from the open Apple menu in `desktop_archiveorg8.6hd.png`, not `[Colors:View]`; drop the
"flat white" wording.
- `tests/test_desktoptheme_background.py`: `test_background_pixels` passes `FACE` instead of
`WHITE` to `assert_face_bevel`; `test_background_colours` expects `{BLACK, FACE}`; import `FACE`
from `support.platinum_palette` (it is already `#DDDDDD`). Add a reference case, mirroring the
`ReferenceScreenshotMixin` use in `tests/test_desktoptheme_panel.py` and
`tests/test_desktoptheme_menubaritem.py`, whose `REFERENCE` is
`macos8.6-screenshots/desktop_archiveorg8.6hd.png` and which compares `pixel(150, 60)` and
`pixel(150, 200)` to the artwork's own rendered face, skipping when the LFS image is not
materialized.
- `README.md`: the `widgets/background.svg` sentence at the desktop-theme paragraph says the
Platinum grey menu body instead of "the flat white Platinum body".
- `docs/invariants.md`: the desktop-themes `background.svg` row's guarantee ("draws the Platinum
menu body") still holds; no provenance exception is needed now that the face is reference-sampled.

**Acceptance criteria.**
- `background.svg`'s parsed fill set is exactly `{#000000, #DDDDDD}`, its 10x10 centre and four
edge tiles are `#DDDDDD`, and its outline is 1px `#000000` with no bevel.
- The new reference test compares the artwork's own rendered face to the two `#DDDDDD` pixels
from `desktop_archiveorg8.6hd.png` and skips when the image is missing, exactly as the other
reference-screenshot cases do.
- `background.svg`'s comment names the reference and the sampled pixels and no longer derives the
face from `[Colors:View]`.
- README.md no longer calls the menu body white.
- `make check` is green.

### Fidelity gate for the rendered window's title-bar boxes (close, zoom, collapse) (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** The rendered-window fidelity gate byte-compares the title-bar's middle strip and the
side and bottom borders, but not the three Platinum title-bar boxes, so a regression in how
Aurorae places or sizes them renders unnoticed. Extend `tests/test_render_surface.py::TestRender`
to byte-compare the close, zoom and collapse box regions of the render against the reference
screenshots.

**Grounding (verified 2026-10-18 with `tools/render_surface.py --settle 3` on this tree and
`tools/png`).** The 320x240 render puts the window at the capture's origin, and each box region is
byte-identical to the reference (0 differing pixels):
- close box: render `(4,4,13,13)` vs `aboutsystem_betawiki.png` `(11,29,13,13)`;
- collapse box: render `(303,4,13,13)` vs `aboutsystem_betawiki.png` `(343,29,13,13)`;
- zoom box: render `(282,4,21,13)` vs `systemprofiler_betawiki.png` `(776,26,21,13)`.
The close and collapse boxes use `aboutsystem_betawiki.png` (its collapse box at x=343); the zoom
box uses `systemprofiler_betawiki.png`, the only reference whose window shows a zoom box
(`aboutsystem`'s window cannot be zoomed, as `tests/support/aurorae_fixtures.py` records), with
`ZOOM_BOX_X = 5` matching the 21px gap-plus-box canvas. The title-bar strip gate deliberately
starts at x=30 to clear the close box, so these three regions are currently ungated at render
time.

**Approach.**
- `tests/test_render_surface.py`: beside the existing border crops, add
  `PROFILER_REFERENCE = str(repo_root.ROOT / "macos8.6-screenshots" / "systemprofiler_betawiki.png")`
  and the six crop tuples `CLOSE_CANDIDATE`/`CLOSE_REFERENCE`,
  `COLLAPSE_CANDIDATE`/`COLLAPSE_REFERENCE`, `ZOOM_CANDIDATE`/`ZOOM_REFERENCE` with the values
  above.
- Generalize `TestRender.assert_strip_pixels_match` to take a `reference_path=REFERENCE`
  argument and load that image with `support.reference_image.read_reference` +
  `skip_unless_materialized` (so the zoom test skips when the profiler LFS image is absent), then
  add `test_title_bar_boxes_match_the_reference` iterating the three
  `(candidate_crop, reference_crop, reference_path)` triples. It reuses the render `setUpClass`
  already makes, so no second render runs.
- `docs/invariants.md`: add a `tooling` row `| The rendered window's title-bar boxes are
  byte-identical to the same regions of the reference screenshots. |
  tests/test_render_surface.py::TestRender::test_title_bar_boxes_match_the_reference | none |`.
- `README.md`: in the Fidelity checking paragraph, name the box regions beside the title-bar and
  border strips.

**Files touched.** `tests/test_render_surface.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `TestRender.test_title_bar_boxes_match_the_reference` passes where the render tools and both
  references are materialized, and skips when either reference is an unmaterialized LFS pointer.
- Each region is pinned to zero differing pixels: shifting any crop by one pixel, or changing the
  box art or the Aurorae box geometry in `org.macos8.desktoprc`, makes the test fail.
- `docs/invariants.md` resolves the new `tooling` row, and `make check` is green.

### Mac OS 8.6 opaque menu bar: ship the `solid/widgets/panel-background.svg` copy (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** `Panel.qml` draws an opaque panel from `solid/widgets/panel-background`, but the
desktop theme ships only `widgets/panel-background.svg`, so the menu bar loses its Platinum bevel
whenever the panel is opaque. Ship the solid copy so the opaque menu bar is Platinum too.

**Grounding.** `/usr/share/plasma/shells/org.kde.plasma.desktop/contents/views/Panel.qml` gives
its two opaque items (`opaqueItem`, `floatingOpaqueItem`) `imagePath:
"solid/widgets/panel-background"`, while the two translucent items use
`widgets/panel-background`. Plasma 6's default panel opacity mode is Adaptive
(`PanelConfiguration.qml`'s opacity combo defaults to index 0), and in Adaptive mode a window
touching the panel (`screenCovered`) drives `panelOpacity` to 1, which hides the translucent item
and shows the opaque one; choosing the Opaque mode does the same always. KSvg does not map
`solid/widgets/panel-background` onto `widgets/panel-background` — the same behaviour
`tests/test_desktoptheme_tooltip.py::TestTooltip::test_solid_copy_is_identical` records for
`PlasmaComponents.ToolTip`'s hardcoded `solid/widgets/tooltip` — so today the opaque menu bar
resolves to the default theme's Breeze `solid/widgets/panel-background.svgz` (the default theme
ships a solid copy; ours ships only `solid/widgets/tooltip.svg`). `widgets/panel-background.svg`
is already fully opaque (its fills are the solid `#FFFFFF`/`#DDDDDD`/`#999999`/`#000000` with no
alpha), so a byte-identical copy is the correct solid variant. Out of scope: a
`solid/widgets/background.svg` (the default theme ships one, but no installed QML requests it —
`DialogBackground.qml` hardcodes `widgets/background` and `libPlasmaQuick` carries no `solid/`
path), so it is not shipped here.

**Approach.**
- Add `theme/desktop-themes/org.macos8.desktop/solid/widgets/panel-background.svg`, byte-identical
to `widgets/panel-background.svg` (no header change, so the copy test compares bytes), matching
the existing `solid/widgets/tooltip.svg`.
- `tests/support/desktoptheme_paths.py`: add `SOLID_PANEL_SVG = os.path.join(PACKAGE, "solid",
"widgets", "panel-background.svg")` beside `SOLID_TOOLTIP_SVG`.
- `tests/test_desktoptheme.py`: import `SOLID_PANEL_SVG`, add `("solid/widgets/panel-background.svg",
SOLID_PANEL_SVG, 12, 22)` to `SVG_CANVASES` (so the registry, canvas, id and self-containment
tests cover it), add `"solid/widgets/panel-background.svg": ("",)` to `ORIGIN_STATES` (its
unprefixed margin rects sit at the origin of the canvas grown to hold the 22px-tall `north-`
state, like `panel-background.svg`), and add
`os.path.join("solid", "widgets", "panel-background.svg")` to `TestInstall.INSTALLED_FILES`.
- `tests/test_desktoptheme_panel.py`: import `SOLID_PANEL_SVG` and add
`test_solid_copy_is_identical` to `TestPanelBackground`, opening `PANEL_SVG` and `SOLID_PANEL_SVG`
in binary and asserting equal bytes (mirroring `TestTooltip::test_solid_copy_is_identical`).
- `docs/invariants.md`: extend the desktop-themes `widgets/panel-background.svg` row's guarantee
to "`widgets/panel-background.svg` draws the menu bar, including its top-panel north state, and
its `solid/` copy is byte-identical." The row already names `TestPanelBackground`, which holds
the new test.
- `README.md`: in the `widgets/panel-background.svg` sentence, add that a byte-identical copy
ships at `solid/widgets/panel-background.svg`, where `Panel.qml` looks for an opaque panel's
background.

**Files touched.** `theme/desktop-themes/org.macos8.desktop/solid/widgets/panel-background.svg`
(new), `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme.py`,
`tests/test_desktoptheme_panel.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `solid/widgets/panel-background.svg` is byte-identical to `widgets/panel-background.svg`,
asserted by `TestPanelBackground::test_solid_copy_is_identical`.
- `test_registry_covers_every_shipped_svg` passes with the new file in `SVG_CANVASES`, and
`test_root_canvas_matches_the_artwork_layout`, `test_every_svg_declares_unique_ids` and
`test_every_svg_is_self_contained` cover it (its 12x22 canvas, unique ids, no style/script or
external reference).
- `TestInstall` still passes with the new file listed in `INSTALLED_FILES`.
- `make check` exits 0, including `tests/test_readme_theme_files.py` (its `*/*.svg` glob does not
reach the two-level `solid/` path, and the README prose names the file) and
`tests/test_invariants.py`.
- Removing `solid/widgets/panel-background.svg` makes `test_solid_copy_is_identical` fail (the
open raises) and `test_registry_covers_every_shipped_svg` fail (the shipped set no longer
equals the registry).

### Mac OS 8.6 splash: draw the reference's full "Mac OS 8.6" wordmark (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** The startup splash's wordmark draws the truncated label `Mac OS`;
`macos8.6-screenshots/boot2_betawiki.png` shows the full `Mac OS 8.6`. Draw the full label so the
login splash matches the reference.

**Grounding.** In `macos8.6-screenshots/boot2_betawiki.png` (240x180, the retail 8.6 boot screen
whose `8.6` is legible) the wordmark's black glyphs occupy `x=89..150, y=71..83` — 62 of the 80
columns of the panel's white face (`x=80..159, y=39..88`, re-derived by
`tests/test_splash_reference.py::TestSplashGeometry::test_grid_geometry`). `Splash.qml`'s
`wordmark` Text draws `text: "Mac OS"`, roughly 38 columns centred on the panel, leaving the
reference's leftmost (`x=89..~100`) and rightmost (`x=~140..150`) glyph columns blank. The
original splash plan (PLANS.md `## Done`, "Mac OS 8.6 Platinum startup splash") and
`tests/test_splash_qml.py::test_wordmark_shows_the_reference_label_at_its_grid_size` both call
`Mac OS` the reference label, which the thumbnail does not support.

**Approach.**
- `theme/look-and-feel/org.macos8.desktop/contents/splash/Splash.qml`: change the `wordmark`
  `Text`'s `text` from `"Mac OS"` to `"Mac OS 8.6"`. Leave its `y: 71 * root.unit`,
  `anchors.horizontalCenter: panel.horizontalCenter` and `font.pixelSize: 12 * root.unit`
  unchanged: the 12-row band and the panel centring already match the reference.
- `tests/test_splash_qml.py`: change `test_wordmark_shows_the_reference_label_at_its_grid_size`
  to require `text: "Mac OS 8.6"` and correct its comment, which calls `Mac OS` the reference
  label.
- `tests/test_splash_reference.py`: add `test_wordmark_spans_the_reference_band` to
  `TestSplashGeometry`. Derive the wordmark's black-pixel bounding box from the thumbnail (dark
  pixels with all three channels below a fixed threshold in the band `y=68..86`, `x=84..156`,
  which excludes the logo stem above `y=68`) and assert its width is at least 55 of the face's 80
  columns, so a reference whose label is no wider than `Mac OS` fails instead of silently passing.

**Files touched.** `theme/look-and-feel/org.macos8.desktop/contents/splash/Splash.qml`,
`tests/test_splash_qml.py`, `tests/test_splash_reference.py`.

**Acceptance criteria.**
- The `wordmark` Text's `text` is exactly `"Mac OS 8.6"`; any other string fails
  `test_wordmark_shows_the_reference_label_at_its_grid_size`.
- `test_wordmark_spans_the_reference_band` re-derives the reference wordmark bbox on
  `boot2_betawiki.png` and passes; a label that spans fewer than 55 face columns fails it.
- `make check` exits 0.
- Recorded deviation (not fixed here): the reference wordmark is a high-contrast serif (Apple's
  Garamond-family wordmark) while the QML draws the system UI font, so glyph shapes still differ;
  shipping a typeface is out of scope and the reference set has no larger boot capture to ground
  one.

### Mac OS 8.6 Platinum full-Trash icon (`32x32/places/user-trash-full.svg`) for the icon theme (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** KDE asks for the icon name `user-trash-full` whenever the Trash holds something
(`/usr/share/plasma/plasmoids/org.kde.plasma.trash/contents/ui/main.qml`:
`hasContents ? "user-trash-full" : "user-trash"`; Dolphin's Places panel and the desktop do the
same). The icon theme ships only `theme/icons/org.macos8.desktop/32x32/places/user-trash.svg`, so
the non-empty state falls through `Inherits=breeze` to Breeze's flat modern `user-trash-full.svg`
— the desktop's Trash visibly stops being Platinum the moment it holds a file. Ship our own
full-Trash art so the non-empty state stays Platinum.

**Approach.**
- Add `theme/icons/org.macos8.desktop/32x32/places/user-trash-full.svg`: our own 32x32 Platinum
drawing, the same can as `user-trash.svg` (lid, body outline/face, the two grey/white rib pairs),
with the handle replaced by a `#FFFFFF` paper sheet outlined in `#000000` rising above the lid, so
the can reads as full. Recommended drawing, in document order (the implementer may adjust the
paper shape, but the constraints below hold):
  ```xml
  <path d="M12 2 l3 2 l3 -2 l1 7 h-8 Z" fill="#000000"/>
  <path d="M13 3 l2 1 l2 -1 l1 5 h-6 Z" fill="#FFFFFF"/>
  <rect x="6" y="8" width="20" height="5" fill="#000000"/>
  <rect x="7" y="9" width="18" height="4" fill="#DDDDDD"/>
  <rect x="7" y="9" width="18" height="1" fill="#FFFFFF"/>
  <rect x="7" y="12" width="18" height="1" fill="#999999"/>
  <path d="M9 13 h14 l-2 16 H11 Z" fill="#000000"/>
  <path d="M10 14 h12 l-2 14 H12 Z" fill="#DDDDDD"/>
  <rect x="13" y="16" width="1" height="10" fill="#999999"/>
  <rect x="14" y="16" width="1" height="10" fill="#FFFFFF"/>
  <rect x="17" y="16" width="1" height="10" fill="#999999"/>
  <rect x="18" y="16" width="1" height="10" fill="#FFFFFF"/>
  ```
- Register the file in `tests/test_icon_theme.py`: add its package-relative path to `SHIPPED_ICONS`
and its exact drawing-element tuple (via the module's `_shape` helper) to `ICON_SHAPES`. The
existing `TestIndex`/`TestIcons`/`TestIconGeometry` tests then cover the new icon: it must be a
32x32 square SVG whose fills are a subset of `PLATINUM_FILLS`, with no scripts, `<style>`,
external references or duplicate ids, and every drawing element must match the pinned tuple.
`TestInstall.INSTALLED_FILES` is derived from `SHIPPED_ICONS`, so the install lifecycle covers it
with no further edit.
- `32x32/places` is already a declared directory in `theme/icons/org.macos8.desktop/index.theme`,
so the metadata does not change and no new size directory is added.
- `README.md`: in the icon-theme sentence, change "the desktop's hard-disk, folder, document and
Trash icons" to name the full-Trash art as well (e.g. "…document, Trash and full-Trash icons").
- `docs/invariants.md`: the `icons` section's "ships exactly the tracked icons" row already names
`tests/test_icon_theme.py::TestIndex`, which covers the new file; no text change.

**Files touched.** `theme/icons/org.macos8.desktop/32x32/places/user-trash-full.svg` (new),
`tests/test_icon_theme.py`, `README.md`.

**Acceptance criteria.**
- `tests/test_icon_theme.py`'s `SHIPPED_ICONS` and `ICON_SHAPES` both list the new icon, and
`test_the_geometry_registry_covers_every_shipped_icon` passes; changing one drawing element in the
SVG fails `TestIconGeometry::test_each_icon_draws_its_pinned_artwork`.
- Deleting the SVG, or removing it from either registry, fails `make check`.
- `make check` is green, and `make install XDG_DATA_HOME=<tmp>` installs the new icon
(`TestInstall` covers the installed file set).

### Record-checker mutation harness: manufacture the malformed inputs from the shipped registers so a silent accept or drop is observable (planned 2026-10-18 by the steward role; from the recurring `no-observability` validation gap in thirteen Fixed entries) — done 2026-10-18

**Goal.** Twelve Fixed entries share one mechanism: a record checker (`tests/invariants.py`'s
register parser and reference resolver, `tests/test_placeholders.py`'s marker scanner) accepted or
silently dropped malformed input that the shipped records never contain, so no test or real run
could surface the bug — each was found by reading the checker and fixed with one hand-written case.
Add a mutation harness that manufactures each malformed shape from the shipped registers
(`docs/invariants.md`, `PLACEHOLDERS.md` and the shipped placeholder markers) and asserts the
checker reports it, so the acceptance boundary is exercised by data and the next silent accept or
drop fails a test instead of waiting for a reader.

**From (the `no-observability` Fixed entries).**
- `tests/invariants.py` register checker, ten entries (all fixed 2026-10-18): accepts a class whose
locally defined base only looks like a test case; accepts a register reference that escapes the
repository; accepts a method reference into a class that is not a test case; accepts a register
reference to a class with no tests; accepts a register reference to a non-test method; accepts a
register reference with a segment after the method; accepts a register reference ending in `::`,
pinning a guarantee to no test; drops a row that does not split into three cells; drops a row whose
Test cell has no backticked reference; drops a row whose cell contains an escaped pipe.
- `tests/test_placeholders.py` marker scanner, two entries (both fixed 2026-10-18): ignores
`PLACEHOLDER:` markers in the theme's `.kvconfig` file; ignores them in the theme's `.js` and
`.desktoprc` files.
- The thirteenth `no-observability` entry, "Palette anchors are not re-derivable from the reference
screenshots" (fixed 2026-10-08), is a different mechanism — a hard-coded anchor assertion — and is
retired by the register's provenance-exception row and `TestProvenanceNote`, not by this harness.

**Approach.**
- Add `tests/support/checker_mutations.py`: one named mutation per rejection shape the two checkers
must catch, each a transform of a copy of the real register or of a scratch theme root plus the
diagnostic substring the checker must raise. Seed the table with the twelve shapes above. The
reference mutations point the register's first row at `tests/support/mutant_module.py`, a shipped
fixture holding the class shapes the shipped tests never define, and at a real test case in
`tests/test_checker_mutations.py`; the placeholder mutations name real shipped theme files, so
every path they cite exists in the tree.
- Add `tests/test_checker_mutations.py`: copy `docs/invariants.md` and the placeholder register into
a scratch root, apply each mutation, run the checker, and assert the named diagnostic; a mutation
the checker does not reject fails. Exercise the `.js`/`.desktoprc`/`.kvconfig` cases by writing one
marked file per text format the theme ships into the scratch theme root.
- Give each checker a `REJECTION_SHAPES` list naming the boundaries it must reject (the shapes its
`cross_check` docstring already enumerates), and add a test asserting the list and the mutation
table name the same rejection boundaries, so a boundary named in one without the other fails.

**Files touched.** `tests/support/checker_mutations.py` (new), `tests/test_checker_mutations.py`
(new), `tests/support/mutant_module.py` (new), `tests/invariants.py`, `tests/test_placeholders.py`
(the `REJECTION_SHAPES` lists).

**Acceptance criteria.**
- Every shape above is a mutation entry, and applying it makes the matching checker raise the named
diagnostic; a scratch run with one mutation's expected diagnostic removed demonstrates the harness
fails.
- `REJECTION_SHAPES` for both checkers is covered by the mutation table; removing a table row fails
the guard test.
- `make check` is green, with the existing hand-written rejection tests still passing.

**Implementation note (2026-10-18).** The escaped-pipe and the three placeholder-format
shapes are acceptance boundaries, not rejections: the checker must keep the row or find the
marker, so the harness pins them with an `observe` assertion instead of a diagnostic. The
`REJECTION_SHAPES` lists hold the nine invariant rejections and the three placeholder
rejections; the guard test asserts each list equals the rejection mutation names, so a name
or a mutation added without the other fails. It is a sync check between two hand-maintained
lists, not a detector of a new rejection branch added to a checker on its own.

### Fidelity gate for the rendered window frame's side and bottom borders (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** The rendered-window fidelity gate compares only the title-bar strip
(`TestRender::test_title_bar_matches_the_reference`). The frame's six-pixel left, right and
bottom borders are still pinned only by the SVG unit tests (`tests/test_aurorae_frame.py`) and the
rc test (`tests/test_aurorae_rc.py`), so nothing checks that KWin paints them at the reference
geometry. Extend the same render-and-byte-compare gate to those three border strips. It reuses
the one render `TestRender.setUpClass` already makes; no second render runs.

**Grounding (sampled 2026-10-18 with `tools/png.read_png` + `pixel_at` on a render from
`tools/render_surface.py --settle 3`).** The 320x240 render puts the window at (0,0): a 6px left
border at x=0..5, a 6px right border at x=314..319 and a 6px bottom border at y=234..239.
`aboutsystem_betawiki.png`'s window has its left outline at x=7 and top outline at y=25, so its
left border is x=7..12, its right border x=354..359 and its bottom border y=419..424. The
reference window is taller than the render, so the side strips compare only the straight part
between the title bar and the bottom border (212 rows), and the bottom strip the horizontal
border between the two corners (308 columns). Byte-exact comparisons:
- left: candidate `(0, 22, 6, 212)` vs reference `(7, 47, 6, 212)` — 0 differing of 1272;
- right: candidate `(314, 22, 6, 212)` vs reference `(354, 47, 6, 212)` — 0 differing of 1272;
- bottom: candidate `(6, 234, 308, 6)` vs reference `(13, 419, 308, 6)` — 0 differing of 1848.

**Approach.**
- `tests/test_render_surface.py`: keep `CANDIDATE_CROP`/`REFERENCE_CROP` for the title bar and add
  six module constants beside them — `LEFT_BORDER_CANDIDATE = (0, 22, 6, 212)`,
  `LEFT_BORDER_REFERENCE = (7, 47, 6, 212)`, `RIGHT_BORDER_CANDIDATE = (314, 22, 6, 212)`,
  `RIGHT_BORDER_REFERENCE = (354, 47, 6, 212)`, `BOTTOM_BORDER_CANDIDATE = (6, 234, 308, 6)`,
  `BOTTOM_BORDER_REFERENCE = (13, 419, 308, 6)`, each with its grounding row above as its comment.
  Extract the body of `test_title_bar_matches_the_reference` (the `read_reference` +
  `skip_unless_materialized` guard and the `process_runner.run` of the real `FIDELITY` CLI with
  `--candidate-crop`/`--crop`) into a helper method
  `assert_strip_matches(self, candidate_crop, reference_crop)`; the title-bar test keeps its name
  and calls the helper with its two constants. Add
  `test_frame_borders_match_the_reference`, which loops the three `(candidate, reference)` border
  pairs and calls the helper under `self.subTest`, so a failure names the strip.
- `docs/invariants.md`: add a second `tooling` row
  `| The rendered window's side and bottom border strips are byte-identical to the same strips of
  the reference screenshot. | tests/test_render_surface.py::TestRender::test_frame_borders_match_the_reference | none |`.
- `README.md`: in the Fidelity checking paragraph's `make check` sentence, extend the compared
  region from the title-bar strip to the title bar and the side and bottom borders.

**Files touched.** `tests/test_render_surface.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `make check` passes. `test_frame_borders_match_the_reference` runs (does not skip) where the
  render tools are on `PATH` and the LFS reference is materialized, and skips when the reference
  is an unmaterialized pointer; the existing title-bar test still passes.
- Each strip reports `differing pixels: 0 / 1272` (left and right) and `0 / 1848` (bottom).
- Changing `BorderLeft`, `BorderRight` or `BorderBottom` in
  `theme/aurorae/themes/org.macos8.desktop/org.macos8.desktoprc`, or the border colours in
  `decoration.svg`, makes a named test fail.
- `tests/test_invariants.py` still resolves every register row against the repository.

### Fidelity gate for the rendered window decoration: byte-compare the title-bar strip to `aboutsystem_betawiki.png` (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** `tools/render_surface.py` renders the themed window in a headless KWin session and
`tools/fidelity.py` compares a rendered PNG against a reference screenshot, but no reference crop
or threshold for a rendered surface is chosen, so nothing checks that the assembled theme renders
like the reference. This is the later plan the render entry's "Out of scope" names. Choose the
first such crop — the window title bar — add a `--candidate-crop` option so the candidate can be
cropped to the reference crop's size, and pin the whole pipeline (install, KWin, Aurorae, render)
with a `make check` test that byte-compares the strip.

**Grounding (sampled 2026-10-18 with `tools/png.read_png` + `pixel_at`).** A 320x240 render
(`tools/render_surface.py --settle 3`, `org.kde.plasma.calculator`) puts the window's title bar at
the top of the capture: row 0 is the `#000000` top outline, rows 1..20 are the Platinum pinstripes,
row 21 is the `#000000` title-bar bottom outline. `aboutsystem_betawiki.png` (retail) has the same
window chrome one row per row at `y=25..46`: row 25 the top outline, rows 26..45 the pinstripes,
row 46 the bottom outline. So the render's rows `0..21` map to the reference's rows `25..46`.
The pinstripes are horizontal, so the x offset does not matter as long as both crops stay clear of
the close box and the centered title text: the reference's close box face is x=11..22 with its
`#FFFFFF` highlight at x=23, and the title text is centered near x=180. The strip `x=30..109,
y=0..21` of the render is byte-identical to `x=30..109, y=25..46` of the reference (0 differing
pixels of 1760, max channel delta 0); the same render compared to `y=24..45` or `y=26..47` fails,
so the one-row alignment is pinned by the test.

**Approach.**
- `tools/fidelity.py`: add `--candidate-crop X,Y,W,H` (`type=_parse_crop`,
  `metavar="X,Y,W,H"`, help "crop the candidate to this region before comparing"), apply it as
  `candidate = crop(candidate, *args.candidate_crop)` before `compare` (beside the existing
  `reference = crop(reference, *args.crop)`), and print `candidate crop: X,Y,W,H` when set,
  beside the existing `reference crop:` line. Update the module docstring's usage line to
  `[--candidate-crop X,Y,W,H]`. A run without the option is byte-for-byte unchanged in
  behaviour and output.
- `tests/test_fidelity_cli.py`: cover the option in `TestCli`, mirroring the existing `--crop`
  tests: `_write_padded_surface_pair` returns a 2x2 surface and a 4x4 padded image that embeds it
  at (1,1), so pass the padded image as candidate and the surface as reference with
  `--candidate-crop 1,1,2,2` and assert it passes; the `candidate crop:` rectangle is echoed
  only when the option is given; a malformed rectangle (`1,2,3`) is a usage error naming
  `--candidate-crop`; and a rectangle outside the candidate is a read error from `crop()`.
- `tests/test_render_surface.py`: add module constants beside `SCRIPT` — `FIDELITY =
  str(repo_root.ROOT / "tools" / "fidelity.py")`, `REFERENCE =
  str(repo_root.ROOT / "macos8.6-screenshots" / "aboutsystem_betawiki.png")`,
  `CANDIDATE_CROP = (30, 0, 80, 22)` and `REFERENCE_CROP = (30, 25, 80, 22)` — and a
  `test_title_bar_matches_the_reference` method to `TestRender`. It loads `REFERENCE` with
  `support.reference_image.read_reference` + `skip_unless_materialized` (imported beside the
  other `support` imports, so it skips where the LFS image is absent, like the other reference
  tests), then runs the real CLI `[sys.executable, FIDELITY, cls.output, REFERENCE,
  "--candidate-crop", "30,0,80,22", "--crop", "30,25,80,22"]` through `process_runner` and
  asserts exit 0 and `differing pixels: 0 / 1760` in stdout. It reuses the render `setUpClass`
  already makes, so no second render runs.
- `docs/invariants.md`: add a `tooling` row
  `| The rendered window's title-bar strip is byte-identical to the same strip of the reference
  screenshot. | tests/test_render_surface.py::TestRender::test_title_bar_matches_the_reference |
  none |`.
- `README.md`: in the Fidelity checking paragraph, replace the closing sentence "no reference
  crop or threshold for a rendered surface is chosen yet" with the chosen crop: `make check`
  renders the window (`make render`) and byte-compares its title-bar strip at candidate
  `30,0,80,22` against reference `30,25,80,22` of `aboutsystem_betawiki.png`, naming
  `--candidate-crop`.

**Files touched.** `tools/fidelity.py`, `tests/test_fidelity_cli.py`, `tests/test_render_surface.py`,
`docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `python3 tools/fidelity.py <render.png> macos8.6-screenshots/aboutsystem_betawiki.png
  --candidate-crop 30,0,80,22 --crop 30,25,80,22` exits 0 and prints `differing pixels: 0 /
  1760`; without `--candidate-crop` the run still fails on the size mismatch, and a run with
  neither option is unchanged.
- `TestRender.test_title_bar_matches_the_reference` passes where the render tools and the
  materialized reference are present, and skips when the reference is an unmaterialized LFS
  pointer. Changing the Aurorae pinstripe colours, the title-bar height, or the close-box width
  (so the close box reaches x=30) makes it fail.
- The new `--candidate-crop` tests in `tests/test_fidelity_cli.py` pass, and the existing
  `--crop` tests still pass unchanged.
- `docs/invariants.md` resolves the new tooling row, and `make check` is green.

### Mac OS 8.6 Platinum desktop icon action buttons (`widgets/action-overlays.svg`) for the desktop theme (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** Ship `widgets/action-overlays.svg` so the desktop containment's folder-icon action buttons draw Platinum add/open/remove buttons instead of inheriting Breeze's. The theme ships no `widgets/action-overlays`, so `KSvg` resolves the name to the default theme's Breeze file. It is the last widget name the default session's applets reference and the theme does not ship: the layout's kicker, appmenu, systemtray, digitalclock, windowlist and desktopcontainment reference every other widget name the theme ships. Independent of every shipped widget: it adds one artwork file, one path constant, one test module and registry/README/register lines.

**Consumers (verified in the installed Plasma 6.3.6 tree).**
- `/usr/share/plasma/plasmoids/org.kde.desktopcontainment/contents/ui/FolderItemActionButton.qml` is an `SvgItem` whose `svg` is `KSvg.Svg { imagePath: "widgets/action-overlays"; multipleImages: true; size: "16x16" }`; it sets `elementId: element + "-normal"`, switching to `element + "-hover"` while the pointer is over it and `element + "-pressed"` while down. Its width and height are `Kirigami.Units.iconSizes` chosen from `Plasmoid.configuration.iconSize` (small 16, smallMedium 22, medium 32, large 48), so the 16x16 art scales.
- `/usr/share/plasma/plasmoids/org.kde.desktopcontainment/contents/ui/FolderItemDelegate.qml` instantiates it with `element: model.selected ? "remove" : "add"` (the selection toggle) and `element: "open"` (the folder-popup button); both appear on hover over a desktop icon in the layout the global theme applies. The default theme's `widgets/action-overlays.svg` ships the plain ids `add-`/`open-`/`remove-` plus `base`, and no size-prefixed ids, so the consumer resolves the plain ids.
- `main.qml` sets `imagePath: "widgets/toolbox"` on an `Svg` it never draws, and no installed desktop theme ships a `toolbox.svgz`; the toolbox is dead code, not a surface to style.

**Provenance.** No Mac OS 8.6 screenshot in the reference set shows a hover action button, so the shape and its three states are KDE-required; the fills reuse the grounded Platinum faces the other widgets ship (`#000000` outline, `#FFFFFF` highlight, `#999999` shadow, `#DDDDDD` face). No new palette constant is introduced.

**Approach.**
- New `theme/desktop-themes/org.macos8.desktop/widgets/action-overlays.svg`, a 16x16 canvas with nine groups, ids `add-normal`, `add-hover`, `add-pressed`, `open-normal`, `open-hover`, `open-pressed`, `remove-normal`, `remove-hover`, `remove-pressed` (the plain ids the consumer resolves):
  - each group opens with the invisible `0,0,16,16` `fill="none"` bounding rect, then the `actionbutton.svg` circle recipe at (8,8): a `#000000` r=7 outline circle, the two bevel half-discs of radius 6 split on the top-right to bottom-left diagonal, and the `#DDDDDD` r=5 face circle;
  - `normal` and `hover` keep the raised bevel (`#FFFFFF` top-left half, `#999999` bottom-right half) and `pressed` swaps it; the `hover` face is `#FFFFFF` (a lit Platinum button), the `normal` and `pressed` face `#DDDDDD`;
  - a `#000000` glyph over the face: `add` a plus, `remove` a minus (each a stroked path with `fill="none"`), `open` a right-pointing filled triangle, sized to fit inside the r=5 face.
- `tests/support/desktoptheme_paths.py`: add `ACTION_OVERLAYS_SVG = os.path.join(PACKAGE, "widgets", "action-overlays.svg")`.
- New `tests/test_desktoptheme_actionoverlays.py`, modelled on `tests/test_desktoptheme_actionbutton.py` (extends `SvgCase`): `TestActionOverlays` pins the nine ids (`assert_ids_present`), the parsed fill set (`PLATINUM_FILLS | {"none"}`), the stroke set (`{"#000000"}`), `assert_no_script_elements`, each group's bounds rect, each state's circle geometry and bevel order, and each kind's glyph path (`d`, `fill`, `stroke`, `stroke-width`).
- `tests/test_desktoptheme.py`: add `("action-overlays.svg", ACTION_OVERLAYS_SVG, 16, 16)` to `SVG_CANVASES` (and a clause about it to the canvas comment) and `os.path.join("widgets", "action-overlays.svg")` to `TestInstall.INSTALLED_FILES`.
- `docs/invariants.md`: add the desktop-themes row `widgets/action-overlays.svg` draws the Platinum desktop icon action buttons. | `tests/test_desktoptheme_actionoverlays.py::TestActionOverlays` | none.
- `README.md`: add `widgets/action-overlays.svg` to the desktop theme's widget inventory sentence.

**Files touched.** `theme/desktop-themes/org.macos8.desktop/widgets/action-overlays.svg` (new), `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme_actionoverlays.py` (new), `tests/test_desktoptheme.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `action-overlays.svg` parses with a 16x16 root canvas; the nine element ids are present and unique; every fill is in `PLATINUM_FILLS | {"none"}` and every stroke `#000000`.
- Every group carries the `0,0,16,16` invisible bounds rect; `normal`/`hover` paint the white-top-left/grey-bottom-right bevel and `pressed` the swapped one; the `hover` face is `#FFFFFF`, the `normal`/`pressed` face `#DDDDDD`; each kind's glyph is pinned by its `d` and its stroke/fill attributes.
- `make install` copies the SVG into the installed desktop theme and `make uninstall` removes it (through `TestInstall`), `test_registry_covers_every_shipped_svg` and the README backtick test pass, and `docs/invariants.md` resolves the new row's test.
- `make check` is green.

### Mac OS 8.6 Platinum round action button (`widgets/actionbutton.svg`) for the desktop theme (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** Ship `widgets/actionbutton.svg` so `PlasmaComponents.RoundButton` and `PlasmaComponents.Dial` draw a Platinum circle instead of inheriting Breeze's blue one. The theme ships no `widgets/actionbutton`, so `KSvg` resolves the name to the default theme's Breeze file. It is the last of the `actionbutton`/`busy`/`switch` surfaces the done plans name (`busy` and `switch` are done). Independent of every shipped widget: it adds one artwork file, one path constant, one test module and registry/README lines.

**Consumers (verified in the installed Plasma 6.3.6 tree).**
- `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/RoundButton.qml` reads `imagePath: "widgets/actionbutton"` in one `KSvg.Svg`, draws element `pressed` while down/checked else `normal` (`buttonItem`), and overlays `Private.RoundShadow` with states `hidden`/`hover`/`focus`/`shadow`.
- `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/Dial.qml` reads `imagePath: "widgets/actionbutton"`, element `pressed` while pressed else `normal`.
- `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/private/RoundShadow.qml` reads `imagePath: "widgets/actionbutton"` and draws element `hover`, `focus` and (default state) `shadow`.
- `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/RadioIndicator.qml` uses the older combination: `imagePath: "widgets/actionbutton"`, element `normal`, over `widgets/checkmarks`.
- Breeze's `actionbutton.svg` (the default theme) ships elements `normal`, `pressed`, `hover`, `focus` and no `shadow` element (verified by decoding `/usr/share/plasma/desktoptheme/default/widgets/actionbutton.svgz`); a missing `shadow` draws nothing, so the theme keeps Breeze's behaviour there. No shipped plasmoid uses `RoundButton`/`Dial`/`RoundShadow`, so this surface is not visible in the default session; it completes the widget set for third-party Plasma widgets.

**Provenance.** Mac OS 8.6 draws no round button, so the shape and its hover/focus rings are KDE-required; the fills reuse the grounded Platinum face and bevel the other widgets ship (`#000000` outline, `#FFFFFF` highlight, `#999999` shadow, `#DDDDDD` face), and the focus ring reuses `button.svg`'s 1px `#000000` ring treatment. State this in the file's header comment.

**Approach.**
- New `theme/desktop-themes/org.macos8.desktop/widgets/actionbutton.svg`, a 36x36 canvas with four `<g>` elements, each opening with an invisible 36x36 bounding rect, so `KSvg` scales all four by the same bounds:
  - `normal` (raised): a filled `#000000` circle r=17 (outline), then a `#FFFFFF` half-disc path (top-left half, r=16) and a `#999999` half-disc path (bottom-right half, r=16) painting the 1px bevel, then a filled `#DDDDDD` circle r=15 (face). Each half-disc is one `M`/`A`/`Z` path, so `path_arcs` reads one 180-degree arc.
  - `pressed` (sunken): the same circles with the bevel halves swapped — `#999999` top-left, `#FFFFFF` bottom-right.
  - `hover` and `focus`: a 1px `#000000` ring in the outermost pixel, just outside the r=17 outline, drawn as one donut path — a full r=18 circle and a full r=17 circle wound the other way, so the nonzero fill rule leaves the interior transparent and the underlying `normal` art shows through.
  - no `shadow` element (Breeze ships none).
- `tests/support/desktoptheme_paths.py`: add `ACTIONBUTTON_SVG = os.path.join(PACKAGE, "widgets", "actionbutton.svg")`.
- New `tests/test_desktoptheme_actionbutton.py`, modelled on `tests/test_desktoptheme_radiobutton.py` (circles) and `tests/test_desktoptheme_busywidget.py` (arcs):
  - `TestActionButton(SvgCase, unittest.TestCase)` with `SVG_PATH = ACTIONBUTTON_SVG`.
  - `test_actionbutton_contract`: `assert_ids_present(self, self.tree, ("normal", "pressed", "hover", "focus"))`, the parsed fill set is exactly `PLATINUM_FILLS | {"none"}`, and `assert_no_script_elements`.
  - `test_actionbutton_geometry`: for `normal`, the circles are `(18, 18, 17, "#000000")` then `(18, 18, 15, "#DDDDDD")`, and the two half-disc paths' arcs reconstruct (18,18) at r=16; their fills in document order are `#FFFFFF` then `#999999`, so the paint order pins the top-left highlight. For `pressed`, the same geometry with the two fills swapped. For `hover` and `focus`, the group holds no circle but one `#000000` donut path whose four 180-degree arcs reconstruct (18,18) at radii 18, 18, 17, 17 with the inner pair wound the other way, so a filled disc, a same-winding path or a swapped inner/outer radius fails. Every group must also hold one invisible 36x36 bounding rect, so all four scale identically.
- `tests/test_desktoptheme.py`: add `("actionbutton.svg", ACTIONBUTTON_SVG, 36, 36)` to `SVG_CANVASES` and `os.path.join("widgets", "actionbutton.svg")` to `TestInstall.INSTALLED_FILES`.
- `docs/invariants.md`: add the desktop-theme row `| widgets/actionbutton.svg draws the Platinum round action button. | tests/test_desktoptheme_actionbutton.py::TestActionButton | none |`.
- `README.md`: add `widgets/actionbutton.svg` to the desktop theme's widget inventory sentence.

**Files touched.** `theme/desktop-themes/org.macos8.desktop/widgets/actionbutton.svg` (new), `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme_actionbutton.py` (new), `tests/test_desktoptheme.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `actionbutton.svg` parses with a 36x36 root canvas and the four named groups; its parsed fills are exactly the Platinum four plus `none` (the bounding rects).
- `normal`/`pressed` are concentric circles at (18,18) with r=17/16/15 and opposite bevel orders; `hover`/`focus` are a r=17..18 `#000000` donut path with a transparent r=17 interior, all pinned by name.
- `make install` copies the file into the installed desktop theme and `make uninstall` removes it (through `TestInstall`), the SVG registry covers it (through `TestSvgRootCanvas.test_registry_covers_every_shipped_svg`), and the README and `docs/invariants.md` list it.
- `make check` is green.

- Mac OS 8.6 Platinum busy indicator (`widgets/busywidget.svg`) for the desktop theme (planned 2026-10-18, done 2026-10-18; commit b42c20a)
- Invariants register: `docs/invariants.md` pinning each subsystem's guarantee to its test (planned 2026-10-18, done 2026-10-18; commit 6dfe56b)
- Mac OS 8.6 Platinum switch widget (`widgets/switch.svg`) for the desktop theme (planned 2026-10-18, done 2026-10-18; commit 448301a)
- Mac OS 8.6 Kvantum widget style, part 4/4: select the Kvantum style from the global theme (planned 2026-10-18, done 2026-10-18; commit 1ce5330)
- Mac OS 8.6 Kvantum widget style, part 3/4: the Platinum surface controls (planned 2026-10-18, done 2026-10-18; commit d16dec4)
- Mac OS 8.6 Kvantum widget style, part 2/4: the Platinum track and value controls (planned 2026-10-18, done 2026-10-18; commit c8220b9)
- Mac OS 8.6 kicker logo: our own non-infringing `start-here-kde-symbolic` icon (planned 2026-10-18, done 2026-10-18; commit 397f190)
- Mac OS 8.6 Kvantum widget style, part 1/4: ship the `org.macos8.desktop` Kvantum theme with the Platinum palette and the core-control art (planned 2026-10-18, done 2026-10-18; commit 1e9762f)
- Mac OS 8.6 Platinum icon theme: replace the placeholder art with final non-infringing art (planned 2026-10-18, done 2026-10-18; commit ca89e96)
- Own icon art: `PLACEHOLDER:` markers and a test that keeps `PLACEHOLDERS.md` complete (planned 2026-10-18, done 2026-10-18; commit 58830a3)
- Mac OS 8.6 Platinum desktop icon theme: a minimal `org.macos8.desktop` icon package for the icons the desktop shows (planned 2026-10-18, done 2026-10-18; commit 364335d)
- Local theme apply, part 2/2: `make install-local-hook` writes an uncommitted `post-commit` hook that runs `make apply` (planned 2026-10-18, done 2026-10-18; commit e897ef0)
- Local theme apply, part 1/2: `make apply` installs and re-applies the theme to the running Plasma session (planned 2026-10-18, done 2026-10-18; commit c7c2d14)
- Mac OS 8.6 menu-bar top highlight: a `north-` panel-background state whose centre carries the white row 0 (planned 2026-10-18, done 2026-10-18; commit cdc6e60)
- Mac OS 8.6 Qt widget style: select Qt's built-in square-bevel `Windows` style from the global theme (planned 2026-10-18, done 2026-10-18; commit a318999)
- Mac OS 8.6 menu-title spacing: 7px horizontal padding in `widgets/menubaritem.svg` (planned 2026-10-18, done 2026-10-18; commit 31208c2)
- Mac OS 8.6 desktop icon labels: one line of text under each icon (planned 2026-10-18, done 2026-10-18; commit 727cde4)
- Mac OS 8.6 desktop icon arrangement: one right-aligned column of 32px icons (planned 2026-10-18, done 2026-10-18; commit aacf578)
- Mac OS 8.6 Platinum tooltip (`widgets/tooltip.svg`) for the desktop theme (planned 2026-10-17, done 2026-10-17; commit 84cdbbb)
- Mac OS 8.6 menu-bar clock format: 12-hour time with AM/PM, no date, no seconds (planned 2026-10-17, done 2026-10-17; commit dc4dfce)
- Clear the title-bar pinstripes around the zoom box, as Mac OS 8.6 does (planned 2026-10-17, done 2026-10-17; commit d59e398)
- Grow the Aurorae title-bar boxes to 13x13 with their white highlight (planned 2026-10-17, done 2026-10-17; commit 73bd870)
- Mac OS 8.6 zoom box glyph and collapse (windowshade) box for the Aurorae decoration (planned 2026-10-17, done 2026-10-17; commit ffa77e7)
- Mac OS 8.6 Platinum applet-popup heading (`widgets/plasmoidheading.svg`) for the desktop theme (planned 2026-10-17, done 2026-10-17; commit 262f2d9)
- Mac OS 8.6 Platinum etched separator (`widgets/line.svg`) for the desktop theme (planned 2026-10-17, done 2026-10-17; commit 0446a33)
- Mac OS 8.6 menu-bar desktop layout for the global theme (`contents/layouts/`) (planned 2026-10-17, done 2026-10-17; commit 76ba0c4)
- Headless Plasma render-and-capture script that feeds `tools/fidelity.py` (planned 2026-10-17, done 2026-10-17; commit 4422d20)
- Wallpaper, part 2/2: Install the Mac OS 8.6 wallpaper package and select it from the global theme (planned 2026-10-17, done 2026-10-17; commit 884c659)
- Wallpaper, part 1/2: Mac OS 8.6 default desktop pattern as a Plasma wallpaper package (planned 2026-10-17, done 2026-10-17; commit d46c4eb)
- Mac OS 8.6 Platinum progress bar widget (`widgets/bar_meter_horizontal.svg`) for the desktop theme (planned 2026-10-17, done 2026-10-17; commit a683b57)
- Mac OS 8.6 Platinum popup / dropdown arrow widget for the desktop theme (done 2026-10-17; commit 1b5c020)
- Mac OS 8.6 Platinum toolbar background widget for the desktop theme (done 2026-10-17; commit ff71c62)
- Mac OS 8.6 Platinum tab-bar highlight widget for the desktop theme (done 2026-10-17; commit c8d132b)
- Mac OS 8.6 Platinum menu-bar item widget for the desktop theme (done 2026-10-09; commit 370205e)

- Mac OS 8.6 Platinum view item widget for the desktop theme (planned 2026-10-09, done 2026-10-09; commit 1e1a455)
- Mac OS 8.6 Platinum slider widget for the desktop theme (planned 2026-10-09, done 2026-10-09; commit 698e2b2)
- Wire the Mac OS 8.6 window decoration into the global theme defaults (planned 2026-10-09, done 2026-10-09; commit 0063255)
- Mac OS 8.6 Platinum window decoration (`aurorae/themes/`) part B1: inactive frame and inactive widget state (planned 2026-10-08, done 2026-10-09; commit 91189a7)
- Mac OS 8.6 Platinum window decoration (`aurorae/themes/`) part A: active frame, close and zoom widgets (planned 2026-10-08, done 2026-10-08; commit 15bee80)
- Mac OS 8.6 Platinum startup splash (`contents/splash/`) for the global theme (planned 2026-10-08, done 2026-10-08; commit 395994f)
- Mac OS 8.6 Platinum menu / popup background (`widgets/background.svg`) for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 27b7439)
- Mac OS 8.6 Platinum dialog / applet-popup background for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 8df5661)
- Mac OS 8.6 Platinum scroll bar widget for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 9f51d5b)
- Mac OS 8.6 Platinum list item widget for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 7fe6ddc)
- Mac OS 8.6 Platinum text field widget for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 0fe5213)
- Mac OS 8.6 Platinum checkmarks widget for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 7313acd)
- Mac OS 8.6 Platinum radio button widget for the desktop theme (planned 2026-10-07, done 2026-10-07; commit a73c322)
- Mac OS 8.6 Platinum frame widget for the desktop theme (planned 2026-10-07, done 2026-10-07; commit ebb65ca)
- Mac OS 8.6 Platinum button widget for the desktop theme (planned 2026-10-07, done 2026-10-07; commit e553908)
- Mac OS 8.6 desktop theme package with the Platinum panel background (planned 2026-10-07, done 2026-10-07; commit 126538c)
- Mac OS 8.6 look-and-feel global theme package (planned 2026-10-07, done 2026-10-07; commit 0c0cd8b)
- Mac OS 8.6 Platinum color scheme and project check harness (planned 2026-10-07, done 2026-10-07; commit 2e58776)
