# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward):** The initial prompt asks for "the UI of MacOS 8.6,
getting as close as possible to pixel-perfect theming." Shipped so far: the `MacOS8` color
scheme, the `org.macos8.desktop` global theme, and the desktop theme's eight widget SVGs
(panel background, frame, button, radio button, checkmarks, lineedit, list item, scroll bar).
README.md describes the reference set as the source of truth for "menu bar, window chrome,
widget metrics, icons and colour palette", and the set includes Finder/dialog/desktop
screenshots plus five boot/splash images (`boot_*.png/jpg`, `bootwhite_archiveorg.jpg`,
`splash_macbase.gif`). The startup splash is covered by the done `contents/splash/` entry below;
the window decoration is now shipped by the two `aurorae/themes/` entries below, but there is
still no icon, cursor, or Qt widget-style theme. The widget and splash work should not be treated
as the whole of the prompt until the remaining surfaces are planned or explicitly ruled out.

_None yet._

## Done

### Mac OS 8.6 Platinum view item widget for the desktop theme (done 2026-10-09)

**Planned 2026-10-09 by plan.** Independent of the done listitem, background, and menu-bar
plans: it adds one widget file to the existing `org.macos8.desktop` desktop-theme package and one
new test module; it touches no existing SVG and needs none of them to land first.

**Goal.** Ship `widgets/viewitem.svg` in the `org.macos8.desktop` desktop theme so the Platinum
flat selection fill replaces Breeze's rounded translucent blue for the generic item highlight:
every `PlasmaComponents.MenuItem` in a `PlasmaComponents.Menu` (right-click context menus, dialog
and applet menus), `PlasmaExtras.Highlight` (icon-grid and applet-item selection), and the
kicker/quicklaunch/desktop-containment hover highlights. Today the theme ships no `viewitem.svg`,
so `KSvg` resolves the name to the default theme's Breeze file and those surfaces stay Breeze.

**Consumers (verified in installed Plasma 6.3.6 QML).**
- `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/MenuItem.qml`: its `background` is a
  `KSvg.FrameSvgItem` with `imagePath: "widgets/viewitem"` and `prefix: "hover"`, at opacity 1 when
  `controlRoot.highlighted || controlRoot.hovered || controlRoot.down`.
- `.../plasma/extras/Highlight.qml`: `imagePath: "widgets/viewitem"` with `prefix` `"selected+hover"`
  when pressed and hovered, `"selected"` when pressed, `"hover"` when hovered, else `"normal"`.
- `.../plasma/private/containmentlayoutmanager/PlaceHolder.qml`,
  `.../org.kde.desktopcontainment/contents/ui/BackButtonItem.qml` and `main.qml`,
  `.../org.kde.plasma.quicklaunch/contents/ui/IconItem.qml`, and
  `.../org.kde.plasma.kicker/contents/ui/ItemGridView.qml` also read `widgets/viewitem`.
- A missing prefix or slice renders nothing and there is no cross-theme fallback once the file
  exists, so every prefix a consumer names must ship or that consumer draws no highlight.

**Default contract.** `zcat /usr/share/plasma/desktoptheme/default/widgets/viewitem.svgz` carries
the nine-slice ids `{normal,hover,selected,selected+hover}-{center,top,bottom,left,right,topleft,
topright,bottomleft,bottomright}`, one shared `hint-tile-center`, and no per-state margin hints. Its
corners are rounded and its `selected` fill is a translucent `ColorScheme-ButtonFocus`.

**Grounding.**
- Palette: `[Colors:Selection] BackgroundNormal=204,204,255` (#CCCCFF) in
  `theme/color-schemes/MacOS8.colors`. The listitem plan already grounds that token in
  `macos8.6-screenshots/firstboot_betawiki.png` (`TestReferenceAnchors.test_selection_background`,
  the selected Setup Assistant row at y=63), and `[Colors:Selection] ForegroundNormal=0,0,0` is the
  `Kirigami.Theme.highlightedTextColor` `MenuItem.qml` switches its label to while highlighted.
- The reference set has no open-menu screenshot: the desktop and Finder shots' menu-bar rows carry
  only the menu-bar greys, and a scan of `desktop_betawiki.png` for #CCCCFF finds 164 scattered
  anti-aliasing pixels rather than a highlight block. The menu-item highlight therefore reuses the
  project's sampled `[Colors:Selection]` token by semantic role, not a per-pixel menu sample; record
  that provenance in the SVG comment, as the tooltip token already does.
- Mac OS 8.6 highlights are flat, square and un-outlined, and this theme has no hover animation or
  drop shadow, so the file follows `widgets/listitem.svg` exactly: square corners, one flat fill,
  and a transparent placeholder for the unhighlighted state.

**Approach.**
1. New file `widgets/viewitem.svg` in the `org.macos8.desktop` package: root
   `<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12">` with a
   comment naming the widget, its consumers, the four prefixes and the #CCCCFF provenance note.
   - Mirror `widgets/listitem.svg`'s 3px border / 6px centre tile on the 12x12 canvas and its
     per-prefix hint rects: `hint-tile-center` 6x6 at (3,3), plus
     `{prefix}-hint-{top,bottom,left,right}-margin` for each of `normal`, `hover`, `selected`,
     `selected+hover` (any opaque `style` colour; `KSvg` reads geometry, not colour).
   - `normal`: the nine slice groups, each a `<g transform="translate(...)">` holding one rect of
     the slice's size with `style="fill:#FFFFFF" fill-opacity="0.01"` and no `fill` attribute, so
     an unhighlighted item paints nothing perceptible but still contributes the margins.
   - `hover`, `selected`, `selected+hover`: the same nine groups at the same origins, each holding
     one rect of the slice's size with `fill="#CCCCFF"` — flat fill, square corners, no bevel and no
     outline.
   No `focus-*`, `separator`, `class="ColorScheme-*"`, `currentColor`, or `<script>`, and no element
   outside the 12x12 canvas.
2. `tests/desktoptheme_paths.py` (edit): add
   `VIEWITEM_SVG = os.path.join(PACKAGE, "widgets", "viewitem.svg")` beside `LISTITEM_SVG`.
3. New `test_desktoptheme_viewitem.py` module beside the existing `tests/test_desktoptheme_listitem.py` with
   `class TestViewItem(NineSliceCase, unittest.TestCase)`, importing `VIEWITEM_SVG` from
   `desktoptheme_paths` and `assert_hint_geometry`, `assert_slice_pixels`, `assert_slices_uniform`,
   `attribute_values`, `nine_slice_tile_sizes`, `pixel_map`, `render_slices` from `svg_assertions`.
   Set `SVG_PATH = VIEWITEM_SVG` and
   `PREFIXES = ("normal", "hover", "selected", "selected+hover")`; the `NineSliceCase` base then
   supplies `test_slice_ids_present`, `test_tiles_placed_by_margins`,
   `test_tiles_stay_within_their_margins` and `test_no_script_elements`.
   - `test_viewitem_hint_geometry`: `assert_hint_geometry(self, self.tree, self.PREFIXES, 3, 6)`.
   - `test_viewitem_normal_has_no_fill`: `assert_slices_uniform(render_slices(self.tree),
     "normal", None)` and `attribute_values(self.tree, "fill-opacity") == {"0.01"}`.
   - `test_viewitem_highlights_are_flat_selection_colour`: for each prefix in
     `("hover", "selected", "selected+hover")`, `assert_slices_uniform(render_slices(self.tree),
     prefix, "#CCCCFF")`.
   - `test_viewitem_slices_fill_their_tiles`: like `TestListItem.test_listitem_slices_fill_their_
     tiles`, pinning every slice of all four prefixes to its exact tile region (flat #CCCCFF for the
     three highlight prefixes, `None` for `normal`).
   - `test_viewitem_colours`: `attribute_values(self.tree, "fill") == {"#CCCCFF"}` (the hints and
     the normal slices use `style`, so they are excluded).
4. `tests/test_desktoptheme.py` (edit): add `("viewitem.svg", VIEWITEM_SVG, 12, 12)` to
   `SVG_CANVASES` and `os.path.join("widgets", "viewitem.svg")` to `TestInstall.INSTALLED_FILES`.
5. `README.md` (edit): add "view item" to the `tumwater:status` block's desktop-theme widget
   parenthetical, and `widgets/viewitem.svg` (the flat #CCCCFF highlight for menu items and
   icon-grid selection) to the Installing section's desktop-theme sentence.

**Files touched.** New: `viewitem.svg` in the package's `widgets/` subdirectory and
`test_desktoptheme_viewitem.py` beside `tests/test_desktoptheme_listitem.py`. Edited:
`tests/desktoptheme_paths.py` (`VIEWITEM_SVG`), `tests/test_desktoptheme.py` (`SVG_CANVASES`,
`TestInstall` `INSTALLED_FILES`), `README.md`. No change to the color scheme, the look-and-feel
package, the Makefile, or the other widgets.

**Acceptance criteria.**
- `make check` exits 0 with `TestViewItem` passing and the extended `TestInstall` byte-identity
  assertion.
- The viewitem SVG parses and contains the 36 `{normal,hover,selected,selected+hover}-{slice}` ids,
  the 16 per-prefix margin-hint ids and `hint-tile-center`; every `hover`/`selected`/`selected+hover`
  slice renders entirely #CCCCFF; every `normal` slice has no `fill` attribute and a `fill-opacity`
  of 0.01; the only parsed `fill` attribute value is #CCCCFF.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/desktoptheme/org.macos8.desktop/widgets/viewitem.svg` byte-identical to source
  (via the extended `TestInstall` tuple).
- Manual smoke test (needs a Plasma session): a right-click context menu and an applet
  `PlasmaComponents.Menu` show the hovered/highlighted row as a flat #CCCCFF rectangle with black
  text and no Breeze blue gradient or rounded corners; a selected icon-grid item shows the same flat
  highlight; every other widget is unchanged.

**Follow-up (not planned here).** `widgets/menubaritem.svg` (the appmenu title highlight, whose
`hover` state must stay transparent because Mac OS 8.6 highlights a menu-bar title only while its
menu is open), then `tabbar`, `tooltip`, and the `actionbutton`/`busy`/`switch` surfaces.

### Mac OS 8.6 Platinum slider widget for the desktop theme (done 2026-10-09)

**Planned 2026-10-09 by plan.** Independent of the done frame/button/scrollbar plans: it adds one
widget file to the existing `org.macos8.desktop` desktop-theme package and one new test module; it
touches no existing SVG and needs none of them to land first.

**Goal.** Ship `widgets/slider.svg` in the `org.macos8.desktop` desktop theme so the Platinum groove
and thumb replace Breeze's blue-tinted groove and round handle. Today `PlasmaComponents.Slider`
and `PlasmaComponents.RangeSlider` still render as Breeze — the volume applet's
`/usr/share/plasma/plasmoids/org.kde.plasma.volume/contents/ui/VolumeSlider.qml` (`PC3.Slider`) and
the brightness applet's `.../org.kde.plasma.brightness/contents/ui/BrightnessItem.qml`
(`PlasmaComponents3.Slider`) both go through it.

**Consumers (verified in installed Plasma 6.3.6 QML).** Under
`/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/`, `Slider.qml` reads
`imagePath: "widgets/slider"` for a `KSvg.Svg`, the `groove` and `groove-highlight`
`FrameSvgItem`s, and the `horizontal-slider-handle`/`vertical-slider-handle` `SvgItem`s;
`RangeSlider.qml` reads the same `imagePath` and handle ids. `Dial.qml` declares a `KSvg.Svg`
with the same `imagePath` but never references it — it paints its groove with a `Canvas` using
Kirigami theme colors — so `widgets/slider.svg` does not reach it. `hint-handle-size` is
optional: when absent, `Slider.qml` sizes the handle from the handle element's own bounding box.

**Reference and provenance.** No screenshot in `macos8.6-screenshots/` shows a slider, so the
slider's shape and metrics are KDE-required provenance, recorded here. Its colours are the grounded
Platinum values the scroll bar already ships, because a slider and a scroll bar are the same
Platinum trough-and-raised-thumb control:
- Groove (the track): the scroll bar trough recipe — a flat `#EEEEEE` bar with a 1px `#000000`
  outline, square corners (`[Colors:View] BackgroundAlternate=238,238,238`, the value
  `tests/test_desktoptheme_scrollbar.py` re-derives).
- Handle (the thumb): the scroll bar thumb recipe — a raised `#DDDDDD` face with a 1px `#000000`
  outline and a 1px bevel inside it (`#FFFFFF` top/left, `#999999` bottom/right), the same rule as
  `button.svg`'s `normal` state.
The track thickness (6px: 3px top and bottom margins) and the handle size (12x16 horizontal, 16x12
vertical) are provenance, like the scroll bar's own trough/thumb geometry.

**Approach.**
1. New `widgets/slider.svg` in the package: root
   `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">` with a
   comment naming the widget, its consumers, the `groove` prefix it ships, the omitted prefixes, and
   the provenance above.
   - Hints (id-bearing rects, any opaque `style` colour; KSvg reads geometry): `hint-tile-center`
     10x10 at (3,3); `groove-hint-top-margin` 10x3 at (3,0), `groove-hint-bottom-margin` 10x3 at
     (3,13), `groove-hint-left-margin` 3x10 at (0,3), `groove-hint-right-margin` 3x10 at (13,3). No
     `hint-handle-size` and no `-inset` hints.
   - `groove` nine-slice, identical to the scroll bar trough: each of the nine
     `<g id="groove-{slice}">` groups holds a `#EEEEEE` rect of the slice size with a 1px
     `#000000` line along each outer edge, square corners; group origins match the scroll bar's
     (top translate(3,0), bottom translate(3,13), left translate(0,3), right translate(13,3), centre
     translate(3,3), corners at (0,0)/(13,0)/(0,13)/(13,13)).
   - `horizontal-slider-handle`: a `<g>` holding rects for a 12x16 raised thumb at (0,0) — a
     `#DDDDDD` base, a 1px `#000000` outline, 1px `#FFFFFF` inside top/left, 1px `#999999` inside
     bottom/right. `vertical-slider-handle`: the same thumb rotated, 16 wide x 12 tall at (0,0),
     same bevel sides. No rect inside either group carries an id (so `rect_geometry` sees only the
     five hints) and neither group declares a transform.
   - Omitted on purpose, like `button.svg`'s `hover`/`shadow`: no `groove-highlight-*` (the filled
     portion; a prefix this file does not declare draws nothing, so the slider shows one uniform
     Platinum trough and the thumb alone marks the value), no `horizontal/vertical-slider-hover`,
     `-focus`, `-shadow`, and no `class=`, `<style>` or `<script>`.
2. `tests/desktoptheme_paths.py`: add
   `SLIDER_SVG = os.path.join(PACKAGE, "widgets", "slider.svg")` beside `SCROLLBAR_SVG`.
3. `tests/test_desktoptheme.py`: add `("slider.svg", SLIDER_SVG, 16, 16)` to `SVG_CANVASES` and
   `os.path.join("widgets", "slider.svg")` to `TestInstall.INSTALLED_FILES`.
4. New per-widget test module `tests/test_desktoptheme_slider.py` with `class TestSlider`,
   subclassing the `tests/nine_slice_case.py` `NineSliceCase` mixin (so the shared slice-id,
   tile-placement, within-tile and no-script checks run once) and importing `SLIDER_SVG`,
   `assert_face_bevel`, `assert_hint_geometry`, `assert_slice_pixels`, `assert_unique_ids`,
   `attribute_values` and `render_slices` from `svg_assertions`. Because the two handle groups
   are id-bearing `<g>` elements but not nine-slice tiles, `assert_tiles_placed_by_margins`
   gains an `extra_groups` argument and `NineSliceCase` an `EXTRA_GROUPS` attribute to pin the
   handles' origins at (0,0) (tests in the criteria below).
5. `README.md`: add "slider" to the status block's desktop-theme widget list and name
   `widgets/slider.svg` (the raised grey thumb in a flat grey trough for
   `PlasmaComponents.Slider`/`RangeSlider`) in the Installing section's desktop-theme
   inventory.

**Files touched.** New: `widgets/slider.svg` in the package, and
`tests/test_desktoptheme_slider.py`.
Edited: `tests/desktoptheme_paths.py`, `tests/test_desktoptheme.py`,
`tests/svg_assertions.py` (the `extra_groups` argument on `assert_tiles_placed_by_margins`),
`tests/nine_slice_case.py` (the `EXTRA_GROUPS` attribute), `tests/test_svg_assertions_checks.py`
(the two tests for `extra_groups`), `README.md`, `PLANS.md` (this entry). No Makefile,
color-scheme or look-and-feel change: the Makefile's `cp -r` already copies new widget files.

**Acceptance criteria.**
- `make check` exits 0; the new `TestSlider` passes and the package, install, lifecycle and other
  widget suites still pass.
- `TestSlider` inherits `NineSliceCase`: `test_slice_ids_present` runs
  `assert_slice_ids_present(self, tree, ["groove"])` and `test_no_script_elements` passes, and
  `TestSlider.test_slider_ids_are_unique` runs `assert_unique_ids`.
- `TestSlider.test_slider_hint_geometry` runs
  `assert_hint_geometry(self, tree, ["groove"], 3, 10)`, pinning exactly the five hint rects
  above (the four `groove` margins plus `hint-tile-center`): the 3px border, the 10px centre tile
  and the 6px track.
- `TestSlider.test_tiles_placed_by_margins` (inherited) runs
  `assert_tiles_placed_by_margins(self, tree, ["groove"], extra_groups={
  "horizontal-slider-handle": (0, 0), "vertical-slider-handle": (0, 0)})`, and
  `test_tiles_stay_within_their_margins` passes.
- `TestSlider.test_slider_groove_outline` runs
  `assert_face_bevel(self, render_slices(tree), "groove", "#EEEEEE", "flat", size=10)`: each edge
  slice's outer row/column is `#000000` and its other two rows/columns are `#EEEEEE`, and each
  corner has black outer edges and a `#EEEEEE` interior.
- `TestSlider.test_slider_handles_are_raised_thumbs` renders `horizontal-slider-handle` and
  `vertical-slider-handle` and asserts, for each, that the map spans 12x16 and 16x12 respectively,
  the outer ring is `#000000`, the inner top/left ring is `#FFFFFF`, the inner bottom/right ring is
  `#999999`, and every remaining pixel is `#DDDDDD`.
- `TestSlider.test_slider_colours` asserts
  `attribute_values(tree, "fill") == {"#000000", "#FFFFFF", "#999999", "#DDDDDD", "#EEEEEE"}`.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/desktoptheme/org.macos8.desktop/widgets/slider.svg` byte-identical to source
  (via the extended `TestInstall` tuple).
- Manual smoke test (needs a Plasma session): the volume and brightness applets draw a flat
  `#EEEEEE` trough with a 1px black outline and a raised `#DDDDDD` thumb with a `#FFFFFF` top/left
  and `#999999` bottom/right bevel, in both horizontal and vertical orientations, with no Breeze
  blue; every other widget is unchanged.

### Wire the Mac OS 8.6 window decoration into the global theme defaults (done 2026-10-09)

**Planned 2026-10-09 by plan.**

**Goal.** Applying the global theme (`lookandfeeltool -a org.macos8.desktop`) currently selects the
`MacOS8` color scheme, the `org.macos8.desktop` desktop theme and the Platinum splash, but leaves
the window decoration on Breeze: `contents/defaults` has only `[kdeglobals][General]` and
`[plasmarc][Theme]`, so a freshly applied global theme still wears Breeze title bars until the user
manually picks the Aurorae theme in System Settings → Window Decorations. Add the
`[kwinrc][org.kde.kdecoration2]` defaults so the global theme selects the shipped
`org.macos8.desktop` Aurorae theme and the reference's button layout (close box on the left, zoom
box on the right, no collapse box). This is the global-theme wiring Part A's Follow-ups lists but
leaves unplanned; it is independent of the part B1 inactive-artwork plan (different files, and it
uses the already-landed active theme).

**Reference.** `aboutsystem_betawiki.png` (1024x768, lossless PNG) is the clean window: the close
box sits on the left (x=11..22) and the zoom box on the right (x=343..354) and there is no collapse
box. The key names and codes are KDE-required provenance, read from the installed KWin settings
schema `/usr/share/config.kcfg/kwindecorationsettings.kcfg` (the `[org.kde.kdecoration2]` group,
`ButtonsOnLeft`/`ButtonsOnRight`; `X` = Close, `A` = Maximize).

**Approach.**
- `theme/look-and-feel/org.macos8.desktop/contents/defaults`: append a third section
  `[kwinrc][org.kde.kdecoration2]` with `library=org.kde.kwin.aurorae`,
  `theme=__aurorae__svg__org.macos8.desktop`, `ButtonsOnLeft=X`, `ButtonsOnRight=A`.
  `library` is the Aurorae decoration factory — the installed plugin is
  `…/org.kde.kdecoration3/org.kde.kwin.aurorae.so` and the kcfg's fallback plugin name is
  `org.kde.kwin.aurorae`. `theme` is the `__aurorae__svg__`-prefixed Aurorae theme id, the form the
decoration KCM writes (the `__aurorae__svg__` literal is in `kcm_auroraedecoration.so`) and the id
  Part A's smoke test already records; the Part A Follow-ups note's bare `theme=org.macos8.desktop`
  is wrong and this plan corrects it. Breeze's own `contents/defaults`
  (`/usr/share/plasma/look-and-feel/org.kde.breeze.desktop/contents/defaults`) is the working
example of the `[kwinrc][org.kde.kdecoration2]` section in an LNF package.
- `tests/test_lookandfeel.py`: extend `TestDefaults` (criteria below).
- `README.md`: the paragraph describing what the global theme applies gains one sentence that it
also selects the `org.macos8.desktop` window decoration with the close box on the left and the zoom
  box on the right.
- No `Makefile` or `test_aurorae_decoration.py` change: the decoration package already installs, and
  this only adds config that points KWin at it.

**Files touched.**
- `theme/look-and-feel/org.macos8.desktop/contents/defaults`
- `tests/test_lookandfeel.py`
- `README.md`
- `PLANS.md` (this entry)

**Acceptance criteria.**
- `make check` exits 0; the extended `test_lookandfeel.py` passes and the install, lifecycle and
  Aurorae suites still pass unchanged.
- `TestDefaults.test_the_expected_sections_and_keys_are_set` expects the three sections in file
  order (`kdeglobals][General`, `plasmarc][Theme`, `kwinrc][org.kde.kdecoration2`) with options
  `ColorScheme`; `name`; and `library`, `theme`, `ButtonsOnLeft`, `ButtonsOnRight`.
- New `TestDefaults.test_window_decoration_names_the_shipped_theme` asserts
  `library == "org.kde.kwin.aurorae"` and `theme == "__aurorae__svg__" + <the theme directory
  name>`, where the id is taken from the directory holding
  `theme/aurorae/themes/org.macos8.desktop/metadata.desktop`, via a module constant, so a rename of
  the Aurorae package fails the test instead of silently pointing KWin at a theme that is not
  installed; it also asserts that directory contains `metadata.desktop` (KWin's discovery
  requirement recorded in Part A).
- New `TestDefaults.test_titlebar_buttons_match_the_reference` asserts `ButtonsOnLeft == "X"` and
  `ButtonsOnRight == "A"` — close on the left, zoom on the right, no collapse box — the layout
  `aboutsystem_betawiki.png` shows.
- Manual smoke test (needs a Plasma session, outside `make check`): after `make install` and
  `lookandfeeltool -a org.macos8.desktop`, a new window wears the pinstriped Platinum title bar with
  the close box on the left and the zoom box on the right, with no manual Window Decorations step.

### Mac OS 8.6 Platinum window decoration (`aurorae/themes/`) part B1: inactive frame and inactive widget state (done 2026-10-09)

**Planned 2026-10-08 by plan.**

**Depends on.** Part A (now under `## Done`), which creates the `org.macos8.desktop` Aurorae theme tree and its
`test_aurorae_decoration.py` module; land Part A first. This is the first slice of the Part B work
Part A's Follow-ups list; the hover/pressed/deactivated button states, the `decoration-maximized`
frame, the collapse (`minimize.svg`) and secondary widgets, and the global-theme wiring stay
unplanned siblings.

**Goal.** Give the decoration a distinct inactive state: the flat grey Platinum title bar and the
greyed close/zoom boxes an unfocused window wears. Part A ships only the active `decoration-*`
slices and `active-center` button groups, so Aurorae reuses the active artwork for every unfocused
window and two overlapping windows look equally active. This is the front-window separation Mac OS
8.6 relies on.

**Reference.** The reference set has no clean inactive window: `aboutsystem_betawiki.png`
(1024x768, lossless) is the only clean window and it is active, `desktop_betawiki.png` shows no
window, and `desktop_fandom.png`/`desktop_archiveorg8.6hd.png` are noisy or unscannable. The
inactive values are therefore recorded as **KDE-required provenance** rather than sampled, and are
the one place this plan leaves the sampled palette:
- Inactive top tile: the active top tile's 22px geometry with its six `#FFFFFF` and six `#777777`
  pinstripe rows and its 1px `#FFFFFF` highlight row replaced by the `#CCCCCC` field sampled at
  `aboutsystem_betawiki.png` (250,27), so the bar is fully flat; the 1px `#000000` top and the 1px
  `#999999` and 1px `#000000` bottom rows are unchanged.
- Inactive left/right/bottom bevel: the active bevel's 6px geometry (sampled at y=100:
  `#000000`, `#FFFFFF`, `#CCCCCC`, `#CCCCCC`, `#999999`, `#000000`) with the `#FFFFFF` highlight
  row replaced by `#CCCCCC`.
- Inactive close/zoom box: the active box's 12x12 geometry and `#888888` top/left and `#222222`
  inner outlines (sampled at x=11..22, y=29..40) with the `#CCCCCC`→`#FFFFFF` diagonal replaced by
  a flat `#CCCCCC` face.
A later reference or a human can correct these three choices without touching the rest.

**Approach.**
- `decoration.svg`: add a second nine-slice on the `decoration-inactive` prefix —
  `decoration-inactive-{top,topleft,topright,left,right,center,bottomleft,bottom,bottomright}` —
  mirroring the active groups' geometry and rects, with the provenance greying above. The inactive
  state declares no margin-hint ids of its own: the installed `irixium` theme's
  `decoration-inactive-*` groups carry none, so reuse whatever margins the active state declares
  and add no `decoration-inactive-hint-*`.
- `close.svg`, `maximize.svg`, `restore.svg`: add an `inactive-center` group drawing the flat grey
  box, mirroring the existing `active-center` geometry.
- `org.macos8.desktoprc`: no change — Part A already sets `InactiveTextColor=153,153,153`, and
  Aurorae selects the inactive artwork by group prefix alone.
- Part A's `test_aurorae_decoration.py`: extend it, and teach the shared nine-slice test
  helpers that a state may declare no margin hints of its own: `svg_assertions`'
  `assert_slice_ids_present`, `assert_tiles_placed_by_margins` and
  `assert_slices_stay_within_their_tiles` take a `hint_aliases` map (default off) and
  `nine_slice_case.NineSliceCase` carries `HINT_ALIASES` (criteria below).

**Files touched.**
- Part A's `decoration.svg`
- Part A's `close.svg`, `maximize.svg`, `restore.svg`
- Part A's `test_aurorae_decoration.py`
- `tests/svg_assertions.py`, `tests/nine_slice_case.py`, `tests/test_svg_assertions_checks.py`
  (the `hint_aliases` mechanism and its tests)
- `PLANS.md` (this entry)

**Acceptance criteria.**
- `make check` exits 0; the extended `test_aurorae_decoration.py` passes and the install and
  desktop-theme suites still pass unchanged.
- `TestDecorationSvg.test_inactive_slices_present` parses `decoration.svg` and asserts all nine
  `decoration-inactive-*` slice ids are present, and that `assert_unique_ids` and
  `assert_no_script_elements` pass.
- `TestDecorationSvg.test_inactive_top_tile_is_flat_grey` re-derives `#CCCCCC` from
  `aboutsystem_betawiki.png` (250,27) through `tools/png.py`, composites `decoration.svg` with
  `svg_assertions.render_slices`, and asserts `decoration-inactive-top` equals the active top
  tile's geometry with every `#FFFFFF`/`#777777` row (pinstripes and the 1px highlight) filled
  `#CCCCCC` (`assert_slice_pixels`); no rect in the slice fills `#FFFFFF` or `#777777`.
- `TestDecorationSvg.test_inactive_bevel_has_no_highlight` asserts the `decoration-inactive-left`,
  `-right` and `-bottom` slices keep the active bevel's geometry and contain no `#FFFFFF` rect.
- `TestButtons.test_inactive_center_is_flat` asserts each of `close.svg`, `maximize.svg`,
  `restore.svg` carries an `inactive-center` group whose `render_slices` map keeps every
  `#888888`/`#222222` outline pixel and paints the rest of the face `#CCCCCC`, and that
  `assert_unique_ids` passes; `test_inactive_zoom_glyph_survives` pins that the 18-pixel
  `#222222` zoom glyph still differs from the inactive close box.
- Manual smoke test (needs a Plasma session, outside `make check`): with both themes installed,
  focusing and unfocusing a window switches the title bar and boxes between the pinstriped active
  artwork and the flat grey inactive artwork.

### Mac OS 8.6 Platinum window decoration (`aurorae/themes/`) part A: active frame, close and zoom widgets (done 2026-10-08)

**Planned 2026-10-08 by plan.**

**Goal.** Ship the first window decoration for the Mac OS 8.6 port: an Aurorae theme whose active
frame reproduces the Platinum title bar and whose close and zoom widgets reproduce the reference's
gradient boxes, so a window drawn by KWin stops wearing Breeze chrome. Today no `aurorae` theme tree exists and the `Makefile` installs only the color scheme and the two `plasma/` package families,
so KWin keeps Breeze. This is the window-decoration surface the steward's 2026-10-08 scope-drift
note names as uncovered. Part A is the active frame and the two widgets the clean reference shows;
the inactive frame, the hover/pressed/maximized states, the collapse widget, the secondary widgets
and the global-theme wiring are part B (see Follow-ups).

**Reference.** `macos8.6-screenshots/aboutsystem_betawiki.png` (1024x768, lossless PNG;
`sources.txt`). The "About This Computer" window's active title bar is y=25..46 at every column
clear of the caption; sampling column x=250 with `tools/sample.py` gives, top to bottom: y=25
`#000000` (1px), y=26 `#FFFFFF` (1px), y=27..28 `#CCCCCC` (2px), y=29..40 the pinstripes
alternating `#FFFFFF` (odd y) and `#777777` (even y), y=41..44 `#CCCCCC` (4px), y=45 `#999999`
(1px), y=46 `#000000` (1px). The window's side borders at y=100 are x=354 `#000000`, x=355
`#FFFFFF`, x=356..357 `#CCCCCC`, x=358 `#999999`, x=359 `#000000`, mirrored at x=7..12, with a 1px
`#AAAAAA` drop shadow outside them (x=353, and y=418 below the bottom border y=419..424). The close
box is a 12x12 gradient square at
x=11..22, y=29..40 with a 1px `#888888` top/left outline, a 1px `#222222` inner outline, a diagonal
`#999999`→`#FFFFFF` face and no glyph; the zoom box is the same square at x=343..354, y=29..40 but
carries an inner `#222222` glyph (two horizontal bars at local y=5 and y=7 spanning x=2..10, the 18
pixels that differ from the close box). The
caption's solid `#CCCCCC` plate (x≈145..225 at y=29) is a Mac OS caption background that Aurorae's
`caption` `Text` (see `/usr/share/kwin/aurorae/aurorae.qml`) cannot draw; part A leaves the
pinstripes continuous and records this as a deviation.

**Approach.**
- Add `aurorae/themes/org.macos8.desktop/` under `theme/` as a data-only Aurorae theme. The plugin
  `/usr/lib/x86_64-linux-gnu/qt6/plugins/org.kde.kdecoration3/org.kde.kwin.aurorae.so` and
  `/usr/share/kwin/aurorae/aurorae.qml` are installed, and `~/.local/share/aurorae/themes/Marge/`
  is an installed example to read the rc keys from.
  - `org.macos8.desktoprc` — `[General]` `ActiveTextColor=0,0,0`, `InactiveTextColor=153,153,153`,
    `TitleAlignment=Center`, `TitleVerticalAlignment=Center`, `Animation=0`, `Shadow=false`;
    `[Layout]` `BorderLeft=6`, `BorderRight=6`, `BorderBottom=6`, `BorderTop=22`, `TitleHeight=22`,
    `ButtonWidth=12`, `ButtonHeight=12`, `ButtonMarginTop=4`, `TitleEdgeTop=0`, `TitleEdgeLeft=4`,
    `TitleEdgeRight=5`, `ButtonSpacing=8`. The `#CCCCCC` title field and black caption are read from
    the reference; `InactiveTextColor=#999999` is the classic Platinum inactive caption colour,
    recorded as KDE-required because the clean reference used here (`aboutsystem_betawiki.png`)
    shows only an active window.
  - `decoration.svg` — a KSvg nine-slice on the `decoration` prefix: the ids `decoration-top`,
    `decoration-topleft`, `decoration-topright`, `decoration-left`, `decoration-right`,
    `decoration-center`, `decoration-bottomleft`, `decoration-bottom`, `decoration-bottomright`, the
    margin hints `decoration-hint-{top,bottom,left,right}-margin` and `hint-tile-center`. The top
    tile is the 22px title bar above (pinstripes included); the left/right/bottom tiles are the 6px
    bevel; the center is a plain `#FFFFFF` body the client paints over.
  - `close.svg`, `maximize.svg`, `restore.svg` — one 12x12 button SVG each, an `active-center`
    element drawing the reference's gradient box; `close.svg` has no glyph, while `maximize.svg`
    and `restore.svg` carry the zoom box's inner `#222222` glyph. `restore.svg` reuses the zoom
    box because the reference set has no maximized window (KDE-required provenance). The 1px
    `#AAAAAA` shadow the reference shows outside the bottom/right border is not drawn.
  - `metadata.json` — `KPackageStructure: "KWin/Aurorae"`, `Id: "org.macos8.desktop"`,
    `Name: "Mac OS 8.6"`, `License: "GPL-2.0-or-later"`, mirroring the desktop theme's fields.
  - `metadata.desktop` — the `[Desktop Entry]` `Name=Mac OS 8.6` plus the standard
    `X-KDE-PluginInfo-*` keys. KWin 6.3.6's `ThemeProvider::findAllSvgThemes`
    (`src/plugins/kdecorations/aurorae/src/aurorae.cpp`) lists an
    `aurorae/themes/<dir>` only when it contains this file, so without it the
    decoration is never offered in System Settings → Window Decorations.
  - `decoration.svgz` — `decoration.svg` gzipped. `kpackagetool6 -t KWin/Aurorae`
    (the `aurorae` KPackage structure) requires the `decoration.svgz` file
    definition, so a package without it fails to install; the Aurorae runtime
    prefers `decoration.svg` and falls back to the `.svgz`
    (`AuroraeTheme::loadTheme`), so the artwork under test stays uncompressed.
- Install the family: in the `Makefile`, add `AURORAE_ID`, `AURORAE_PACKAGE`,
  `AURORAE_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/aurorae/themes`, an `install -d` and an
  `install_package` call in `_install`, and the matching `rm -rf` (package plus `.staging`/`.old`
  siblings) in `_uninstall`.
- Teach `tests/theme_install.py` the family: `installed_aurorae_dir(destdir)`
  (`<destdir>/share/aurorae/themes`) and `installed_aurorae_theme(destdir, theme_id)`.
- Let the shared install mixins carry the family without changing their existing subclasses: add an
  `installed_parent(self, tmp)` and an `installed_package_dir(self, tmp)` hook to
  `InstallLifecycleCases` and `FailedInstallPreservesPackage` (defaulting to
  `installed_plasma_dir(tmp, self.KIND)` / `installed_package(tmp, self.KIND, self.PACKAGE_ID)`) and
  replace the direct calls with them.
- Add a new `test_aurorae_decoration.py` test module covering the package, the rc and the artwork (below).
- `README.md`: Status and Installing name the fourth artifact.

**Files touched.**
- `aurorae/themes/org.macos8.desktop/org.macos8.desktoprc` (new)
- `aurorae/themes/org.macos8.desktop/decoration.svg` (new)
- `aurorae/themes/org.macos8.desktop/close.svg`, `maximize.svg`, `restore.svg` (new)
- `aurorae/themes/org.macos8.desktop/metadata.json` (new)
- `aurorae/themes/org.macos8.desktop/metadata.desktop` (new)
- `aurorae/themes/org.macos8.desktop/decoration.svgz` (new, gzip of `decoration.svg`)
- `Makefile` (`AURORAE_*`, `_install`, `_uninstall`)
- `tests/theme_install.py` (`installed_aurorae_dir`, `installed_aurorae_theme`)
- `tests/install_lifecycle_cases.py`, `tests/install_failure_cases.py` (the two hooks)
- a new `test_aurorae_decoration.py` test module
- `tests/test_theme_install.py` (the spaced-root install test now covers the fourth artifact)
- `README.md`

**Acceptance criteria.**
- `make check` exits 0; the new `test_aurorae_decoration.py` passes and the existing install
  suites still pass with the added hooks.
- `TestInstall` (subclassing `InstallLifecycleCases` and `FailedInstallPreservesPackage` with
  `installed_parent`/`installed_package_dir` overridden) proves `make install` copies
  `aurorae/themes/org.macos8.desktop/` byte-for-byte to
  `<tmp>/share/aurorae/themes/org.macos8.desktop/`, a reinstall is repeatable, and `make uninstall`
  removes the package and its `.staging`/`.old` siblings.
- `TestRc.test_layout_metrics_match_reference` reads `aboutsystem_betawiki.png` through `tools/png.py`,
  re-derives the title-bar height (the `#000000`→`#000000` run at a clear column), the side-border
  thickness (the black→black run at y=100, excluding the 1px `#AAAAAA` drop shadow), the bottom
  border thickness and the close-box bounding box (the `#888888` pixels near `(11,29)`), and
  asserts the rc's `TitleHeight`, `BorderTop`/`BorderBottom`, `BorderLeft`/`BorderRight` and
  `ButtonWidth`/`ButtonHeight` equal them; `test_title_bar_colours_match_reference` samples
  `(250,29)`/`(250,30)`/`(250,27)` and asserts `decoration.svg`'s `decoration-top` slice uses them,
  and `test_caption_colour_matches_reference` samples the caption glyph at `(198,30)` and asserts
  the rc's `ActiveTextColor` is it.
- `TestDecorationSvg` parses `decoration.svg` and asserts the `decoration`-prefixed slice ids and
  margin hints are present (`assert_slice_ids_present`), that `assert_unique_ids` and
  `assert_no_script_elements` pass, `assert_tiles_placed_by_margins` and
  `assert_slices_stay_within_their_tiles` hold for the `decoration` prefix, and `assert_root_canvas`
  holds for the frame canvas.
- `TestButtons.test_close_box_matches_reference` re-derives every pixel of the close box from
  `aboutsystem_betawiki.png` (x=11..22, y=29..40) and asserts `close.svg`'s `active-center` is
  exactly them; `test_zoom_box_matches_reference` does the same for the zoom box (x=343..354,
  y=29..40) against `maximize.svg` and `restore.svg`, and `test_zoom_glyph_is_the_reference_glyph`
  pins the 18 `#222222` glyph pixels that differ from the close box, so a zoom widget that reuses
  the close artwork fails.
- `TestCorners.test_corners_match_reference` composites each 6x22 / 6x6 corner slice and compares
  it to the reference region, masking only the exact 12x12 close/zoom button footprints
  (frame-local x=4..5 and x=0, y=4..15) that Aurorae draws over the frame.
- `TestMetadata.test_metadata_desktop_names_the_theme` reads `metadata.desktop` and asserts its
  `Name`, the field KWin's SVG-theme discovery shows; `TestDecorationSvg.test_svgz_is_the_compressed_svg`
  pins that `decoration.svgz` decompresses to `decoration.svg`.
- `TestPackageValid` (subclassing `KPackageInstallCase` with `KPACKAGETOOL_TYPE = "KWin/Aurorae"`)
  proves `kpackagetool6 -t KWin/Aurorae -i` accepts the package and lands its `metadata.json`
  under the theme id.
- Manual smoke test (needs a Plasma session, outside `make check`): with the theme copied to
  `$XDG_DATA_HOME/aurorae/themes/`, System Settings → Window Decorations lists `Mac OS 8.6` (the
  `metadata.desktop` `Name`; its theme id is `__aurorae__svg__org.macos8.desktop`), and selecting
  it draws the pinstriped Platinum title bar and the two gradient boxes.

**Follow-ups (not planned here).** Part B adds the inactive frame (`decoration-inactive`) and
inactive button state, the hover/pressed/deactivated prefixes, the `decoration-maximized` frame,
the collapse (`minimize.svg`) and secondary widgets, and wires the global theme by adding
`[kwinrc][org.kde.kdecoration2]` (`library=org.kde.kwin.aurorae`, `theme=org.macos8.desktop`,
`ButtonsOnLeft=X`, `ButtonsOnRight=A`) to `look-and-feel/org.macos8.desktop/contents/defaults`
and extending `tests/test_lookandfeel.py::TestDefaults`.

### Mac OS 8.6 Platinum startup splash (`contents/splash/`) for the global theme (done 2026-10-08)

**Planned 2026-10-08 by plan.**

**Goal.** Ship the `org.macos8.desktop` global theme's Plasma startup splash: a full-screen
Platinum field with a centred panel carrying the Mac OS face logo, the "Mac OS" wordmark and a
progress bar that fills as Plasma starts. Today the `org.macos8.desktop` look-and-feel package holds
only `metadata.json` and `contents/defaults`, so applying the global theme leaves the Breeze
splash, and README's Status says "no ... splash assets exist yet". This is the boot/splash
surface the steward's 2026-10-08 scope-drift note names as uncovered.

**Reference.** `macos8.6-screenshots/boot2_betawiki.png` (240x180, lossless PNG; `sources.txt`
line 11 labels it "Mac OS 8.6 (boot screen)"). Sampling it with `tools/png.py` gives the values
this plan pins:
- field `(99,99,156)` = `#63639C` at `(5,5)` and `(200,150)`;
- panel face `#FFFFFF`; panel outer bevel `(221,221,221)` = `#DDDDDD` at `(74,60)`, inner rule
  `(191,191,191)` = `#BFBFBF` at `(78,60)`;
- logo darkest blue `(76,101,203)` = `#4C65CB`, lighter blue `(114,134,214)` = `#7286D6`;
- progress track `(221,221,221)` = `#DDDDDD` at `(135,96)`, fill `(173,173,173)` = `#ADADAD` at
  `(120,100)`; wordmark black.
- reference grid rectangles (240x180 pixels): the bevel is the bounding box of every pixel that
  is not the field colour, `x=71..168, y=31..106` (98x76); the panel is the `#BFBFBF` rule that
  bounds the white face, `x=78..161, y=37..90` (84x54), whose 2px border leaves the reference's
  white face `x=80..159, y=39..88` (80x50) inside it; the logo is the bounding box of the
  blue pixels, `x=107..132, y=45..65` (26x21); the progress well is the bounding box of the
  pixels darker than the panel's `#DDDDDD`, `x=101..138, y=94..102` (38x9); the wordmark sits in
  the band `y=71..85`. The reference's field is dithered (r=93..104, `b-r` in 44..61) and its
  four rounded-corner pixels are `(49,49,77)`, so "not the field colour" is the documented
  predicate `abs(r-g) <= 6 and 20 <= b-r <= 80 and r <= 130 and g <= 130`, not an exact-colour
  comparison; the thumbnail's progress fill is dithered too, so it is pinned by colour (`#ADADAD`
  at `(120,100)`) and by the `stage` binding, not by a fill rectangle. The original plan called
  the non-field bounding box the panel; re-deriving the white face shows that box is the bevel,
  and the panel is the 2px `#BFBFBF` rule around the white face, so both rectangles are recorded
  here.
The 240x180 frame is a 4:3 thumbnail of the 640x480 Mac OS 8.6 screen; the plan keeps the
reference's own grid and scales it by whole pixels rather than re-deriving 640x480 values.

**Approach.**
- Add a `Splash.qml` under the look-and-feel package's `contents/splash/`. It is a full-screen
  `Rectangle` with `color: "#63639C"` and
  `readonly property int unit: Math.max(1, Math.floor(Math.min(width / 240, height / 180)))`,
  so the reference grid scales by whole pixels and keeps its proportions on any screen. A centred
  `Item` is authored entirely in the 240x180 grid times `unit`:
  - a bevel `Rectangle` at the reference's non-field bounding box filled `#DDDDDD`, and a panel
    `Rectangle` at the `#BFBFBF` rule bounding box, `#FFFFFF` face with a 2px `#BFBFBF` border,
    so its white interior is the reference's white face;
  - an `Image` of `images/macos-logo.svg` at the logo bounding box;
  - a `Text` "Mac OS" in black on the wordmark band;
  - a progress `Rectangle` track at the reference's progress-well rectangle (`#DDDDDD`) whose
    `#ADADAD` fill width binds to the KDE splash `stage` (0..6):
    `width: track.width * Math.min(1, stage / 6)`.
  The `stage` handler and an `OpacityAnimator` intro follow
  `/usr/share/plasma/look-and-feel/org.kde.breeze.desktop/contents/splash/Splash.qml`.
- Add an `images/macos-logo.svg` under that splash directory: the Mac OS face, a periwinkle rounded rectangle
  (`#4C65CB` with a `#7286D6` highlight) traced from the reference logo rectangle. The reference
  logo is only 26x21, so this one element is traced by eye; the test pins its `viewBox`, fills and
  structure rather than every path point.
- `contents/defaults` needs no `[KSplash]` key: applying the global theme already writes
  `[KSplash] Engine=KSplashQML` / `Theme=org.macos8.desktop` into `kdedefaults/ksplashrc`
  (verified this tick with `lookandfeeltool -a org.macos8.desktop` under a throwaway
  `HOME`/`XDG_*` tree, which exited 0 and wrote that file).
- Extend `tests/test_lookandfeel.py::TestInstall.INSTALLED_FILES` with
  `contents/splash/Splash.qml` and `contents/splash/images/macos-logo.svg`, so the byte-identical
  install check covers them.

**Files touched.**
- `contents/splash/Splash.qml` in the look-and-feel package (new)
- `contents/splash/images/macos-logo.svg` in the look-and-feel package (new)
- a new `test_lookandfeel_splash.py` test module
- `tests/test_lookandfeel.py` (`INSTALLED_FILES`)
- `README.md` (Status: the global theme now ships the splash)

**Acceptance criteria.**
- `make check` exits 0; the new splash test module and the extended
  `tests/test_lookandfeel.py` pass.
- `TestSplashReference.test_field_colour_matches_reference` reads
  `macos8.6-screenshots/boot2_betawiki.png` pixel `(5,5)` through `tools/png.py` and asserts it is
  the `#63639C` literal `Splash.qml` uses; `test_panel_colours_match_reference` does the same
  for the white face at `(100,60)`, the bevel `#DDDDDD` at `(74,60)` and the rule `#BFBFBF` at
  `(78,60)`, `test_wordmark_colour_matches_reference` for the black wordmark at `(97,73)`, and
  `test_progress_colours_match_reference` for the track `#DDDDDD` at `(135,96)` and the fill
  `#ADADAD` at `(120,100)`.
- `TestSplashGeometry.test_grid_geometry` parses the bevel/panel/logo/progress grid literals out
  of `Splash.qml` and asserts they equal rectangles the test re-derives from
  `macos8.6-screenshots/boot2_betawiki.png` by colour scan (bevel = bounding box of non-field
  pixels, panel = bounding box of the `#BFBFBF` rule around the white face, logo = bounding box
  of blue pixels, progress well = bounding box of pixels darker than `#DDDDDD`), and that the
  QML's border width is the rule thickness it measured.
- `TestSplashQml.test_reference_colours_are_painted` binds each anchor colour property to the
  object whose geometry literals `test_grid_geometry` pins, so a colour that is declared but
  never painted, or painted on the wrong rectangle, fails; `test_uses_the_logo_image` asserts
  the `Image` source is `images/macos-logo.svg`, and `test_progress_fill_follows_stage` pins the
  `stage`-bound fill width. Those two need no reference image, so a clone without the LFS
  thumbnail still checks them.
- `TestLogo.test_logo_svg` parses `images/macos-logo.svg`, asserts `viewBox` is 26x21, that
  `assert_no_script_elements` and `assert_unique_ids` pass, and that the fill set is exactly
  `{#4C65CB, #7286D6}`.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/look-and-feel/org.macos8.desktop/contents/splash/Splash.qml` and its logo
  byte-identical to source, and `make uninstall` removes the package.
- Manual smoke test (the `[KSplash] Theme=org.macos8.desktop` selection was verified with
  `lookandfeeltool -a` under a throwaway `HOME`/`XDG_*`; the on-screen half still needs a Plasma
  session, outside `make check`): the startup screen shows the
  `#63639C` field, the panel and a progress bar that advances with `stage`.

### Mac OS 8.6 Platinum menu / popup background (`widgets/background.svg`) for the desktop theme (done 2026-10-08)

**Planned 2026-10-08 by plan.** The follow-up the done dialog/background plan left
unplanned. Independent of every done widget plan: it adds one artwork file to the
existing `org.macos8.desktop` desktop-theme package under `widgets/`, one path constant
in `tests/desktoptheme_paths.py`, a new `tests/test_desktoptheme_background.py` module
with the `TestBackground` class, one `TestInstall.INSTALLED_FILES` tuple entry, and the
README inventory line. It does not touch any other `widgets/*.svg`, `dialogs/background.svg`,
`metadata.json`, or the color scheme.

**Goal.** Ship `widgets/background.svg` so Plasma's menu-like surfaces —
`PlasmaComponents.Menu` (context menus and combo-box dropdowns), `PlasmaComponents.Drawer`,
`PlasmaComponents.Popup`, and planar applet containers — draw the flat white Platinum menu
body with a 1px black outline and square corners instead of inheriting Breeze's translucent
rounded `background.svgz`.

**Grounding.**
- Consumers verified in the installed Plasma 6.3.6 tree, every one `imagePath:
  "widgets/background"` with no prefix:
  - `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/Menu.qml` — the
    `background` of `T.Menu`; its `topPadding`/`leftPadding` come from `background.margins`.
  - `.../components/Drawer.qml`, `.../components/Popup.qml`, `.../components/Dialog.qml`.
  - `.../extras/private/BackgroundMetrics.qml` returns `widgets/background` when
    `Plasmoid.formFactor === PlasmaCore.Types.Planar`.
  - `.../private/containmentlayoutmanager/BasicAppletContainer.qml` uses it with
    `prefix: blurEnabled ? "blurred" : ""`, where `blurEnabled` is true only when the SVG
    defines a `blurred` element prefix (`hasElementPrefix("blurred")`); omitting that
    prefix keeps the effective prefix `""`.
- `PlasmaComponents.Dialog` is unused in the installed tree (a grep over `/usr/share/plasma`
  and `/usr/lib/x86_64-linux-gnu/qt6/qml` finds no consumer), and the PlasmaQuick dialog body
  resolves to the landed `dialogs/background` (the `dialogs/background` literal is in
  `libPlasmaQuick`), so no dialog surface takes the white body.
- Mac OS 8.6 menus are a flat white face with a 1px black outline and square corners; white
  is `[Colors:View] BackgroundNormal=255,255,255` in `theme/color-schemes/MacOS8.colors`.
  Palette-derived: this plan adds no `TestReferenceAnchors` entry.

**Approach.**
1. Add `theme/desktop-themes/org.macos8.desktop/widgets/background.svg`: one unprefixed
   frame (prefix `""`) on a 16x16 nine-slice canvas, 3px border, 10x10 centre tile, square
   corners.
   - `center`: a 10x10 `#FFFFFF` rect.
   - `top`/`bottom`/`left`/`right` edge groups: 3px of `#FFFFFF` with a 1px `#000000` rule
     on the outer edge (top `y=0`, bottom `y=2`, left `x=0`, right `x=2`).
   - four corner groups: the `flat_face_corners("#FFFFFF")` pattern (black on the two outer
     edges, white elsewhere).
   - hints: `hint-tile-center` at (3,3,10,10); `hint-{top,bottom,left,right}-margin` 3px
     each; and zero-size `hint-{top,bottom,left,right}-inset` rects exactly as
     `widgets/panel-background.svg` declares them, so the inset hints are present and
     defined.
2. Add `BACKGROUND_SVG = os.path.join(PACKAGE, "widgets", "background.svg")` to
   `tests/desktoptheme_paths.py`.
3. Add `tests/test_desktoptheme_background.py` with `TestBackground`, modelled on
   `tests/test_desktoptheme_panel.py` and `tests/test_desktoptheme_dialog.py`:
   - `test_background_slice_ids`: `assert_slice_ids_present(self, tree, [""])`.
   - `test_background_hint_geometry`: `rect_geometry(tree)` equals the exact dict of the
     tile-centre, four margin and four inset rects.
   - `test_background_tiles_placed_by_margins`: `assert_tiles_placed_by_margins(self, tree,
     [""])`.
   - `test_background_tiles_stay_within_their_margins`:
     `assert_slices_stay_within_their_tiles(self, tree, [""])`.
   - `test_background_pixels`: `assert_center_tile_is(self, slices, "center", "#FFFFFF",
     size=10)`; `assert_edge_bevels(self, slices, "", *face_edge_bands("#FFFFFF",
     "flat"), size=10)`; `assert_corner_pixels` for each entry of
     `flat_face_corners("#FFFFFF")`.
   - `test_background_colours`: `attribute_values(tree, "fill")` equals
     `{"#000000", "#FFFFFF"}`.
   - `test_no_script_elements`.
4. Add `os.path.join("widgets", "background.svg")` to `TestInstall.INSTALLED_FILES` in
   `tests/test_desktoptheme.py`.
5. Name `widgets/background.svg` in README.md's status block and Installing inventory.

**Acceptance criteria.**
- The new module's tests pass and `make check` exits 0.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/desktoptheme/org.macos8.desktop/widgets/background.svg`
  byte-identical to source (via the extended `TestInstall` tuple).
- Manual smoke test (needs a Plasma session): a right-click context menu, an application
  menu, and a combo-box dropdown draw a flat white square body with a 1px black outline; a
  planar (desktop) applet container draws the same; applet popups and dialogs keep the
  `#DDDDDD` `dialogs/background.svg` body; no other widget changes.

**Known deviations (recorded, not fixed here).**
- No `shadow-*` element set: the default theme's `widgets/background.svg` carries one, but
  the installed tree reads the `shadow` prefix only against `widgets/button`
  (`ButtonShadow.qml`) and `widgets/tooltip` (`ToolTip.qml`), so this file makes no claim
  about a themed drop shadow.
- No `blurred`/`blurred-mask` element prefixes: `BasicAppletContainer` enables blur only
  when `blurred` exists, so omitting it keeps planar applet containers opaque (prefix
  `""`), matching the flat Platinum look.

**Docs.** README.md's status block and Installing inventory name `widgets/background.svg`.

### Mac OS 8.6 Platinum dialog / applet-popup background for the desktop theme (done 2026-10-08)

**Planned 2026-10-08 by plan.** Independent of the done widget plans: it adds one
artwork file to the existing `org.macos8.desktop` desktop-theme package under a new
`dialogs/` subdirectory, one path constant in `tests/desktoptheme_paths.py`, a new
`test_desktoptheme_dialog.py` module with the `TestDialogBackground` class, and one
`TestInstall.INSTALLED_FILES` tuple entry in `tests/test_desktoptheme.py`. It does not
touch any `widgets/*.svg`, `metadata.json`, or the color scheme.

**Goal.** Ship `dialogs/background.svg` in the `org.macos8.desktop` desktop theme so the
frameless Plasma dialog surfaces — `PlasmaCore.Dialog` and `PlasmaCore.AppletPopup`
windows, the popups applets and Plasma dialogs use — draw the raised grey Platinum window
body instead of Breeze's translucent rounded rectangle, and the theme stops inheriting
`dialogs/background.svgz` from the default theme.

**Grounding.**
- Consumer verified in the installed Plasma 6.3.6 tree:
  `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/extras/private/BackgroundMetrics.qml`
  returns the literal `"dialogs/background"` when `Window.window instanceof
  PlasmaCore.AppletPopup || Window.window instanceof PlasmaCore.Dialog`, and
  `strings /usr/lib/x86_64-linux-gnu/libPlasmaQuick.so.6.3.5` contains the literal
  `dialogs/background` (PlasmaQuick paints the frameless dialog background from it).
- `ls /usr/share/plasma/desktoptheme/default/dialogs/` shows only `background.svgz`,
  so today the theme ships no `dialogs/` artwork and inherits the default's.
- Palette-derived, following the landed `widgets/scrollbar.svg` thumb and
  `widgets/button.svg` normal state: a `#DDDDDD` face
  (`[Colors:Window] BackgroundNormal=221,221,221`), a 1px `#000000` outline, and a 1px
  bevel inside it (`#FFFFFF` top/left, `#999999` bottom/right). The reference set shows
  the same grey window bodies (`about_betawiki.png`, `setup_emaculation.png`) but they
  are dithered 8-bit captures, so no single pixel is added to `TestReferenceAnchors`;
  the values are palette-derived and recorded as such here.

**Approach.**
1. Add a new `background.svg` in the desktop-theme package's new `dialogs/`
   subdirectory (beside `widgets/`): one
   unprefixed frame (prefix `""`) on a 16x16 nine-slice canvas, 3px border, 10x10 centre
   tile, square corners.
   - `center` group: a 10x10 `#DDDDDD` rect.
   - `top`/`left` edge groups, outer-to-inner: `#000000`, `#FFFFFF`, `#DDDDDD`.
   - `bottom`/`right` edge groups, outer-to-inner: `#DDDDDD`, `#999999`, `#000000`.
   - four corner groups: the 3x3 patterns of the landed scrollbar thumb corners (black
     L outline, white highlight corner, grey shadow corner).
   - hints: `hint-tile-center` at (3,3,10,10) and `hint-{top,bottom,left,right}-margin`
     3px each, i.e. `nine_slice_hint_geometry([""], 3, 10)`; no `hint-*-inset`.
2. Add `DIALOG_BACKGROUND_SVG = os.path.join(PACKAGE, "dialogs", "background.svg")` to
   `tests/desktoptheme_paths.py`.
3. Add a new `test_desktoptheme_dialog.py` module beside
   `tests/test_desktoptheme_scrollbar.py`, with `TestDialogBackground`, modelled on
   `tests/test_desktoptheme_scrollbar.py`'s `TestScrollbar` but for the single prefix
   `""`:
   - `test_dialog_slice_ids`: `assert_slice_ids_present(self, tree, [""])`.
   - `test_dialog_hint_geometry`: `rect_geometry(tree)` equals
     `nine_slice_hint_geometry([""], 3, 10)`.
   - `test_dialog_tiles_placed_by_margins`: `assert_tiles_placed_by_margins(self, tree,
     [""])`.
   - `test_dialog_frame_bevel`: `assert_center_tile_is(..., "center", "#DDDDDD", 10)`;
     `assert_edge_band_pixels` for the four edges with the outward band
     `(BLACK, WHITE, FACE)` on top/left and the mirrored `(FACE, GREY, BLACK)` on
     bottom/right, `size=10`; and `assert_corner_pixels` for the four corners.
   - `test_dialog_colours`: `attribute_values(tree, "fill")` equals
     `{"#000000", "#FFFFFF", "#999999", "#DDDDDD"}`.
   - `test_no_script_elements`.
4. Add `os.path.join("dialogs", "background.svg")` to `TestInstall.INSTALLED_FILES` in
   `tests/test_desktoptheme.py`.

**Acceptance criteria.**
- The new module's tests pass and `make check` exits 0.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/desktoptheme/org.macos8.desktop/dialogs/background.svg`
  byte-identical to source (via the extended `TestInstall` tuple).
- Manual smoke test (needs a Plasma session): clicking an applet that opens a
  `PlasmaCore.AppletPopup` (clock, calendar, network, battery) shows a square, flat
  `#DDDDDD` popup with a 1px `#000000` outline and a 1px raised bevel, and a
  `PlasmaCore.Dialog` shows the same body; context menus and combo dropdowns keep their
  current background; every other widget is unchanged.

**Known deviation (recorded, not fixed here).** The default theme's
`dialogs/background.svgz` also carries a `shadow-*` element set. This plan defines only the
main frame and makes no claim about a themed drop shadow: `strings
libPlasmaQuick.so.6.3.5` contains no `shadow` element-prefix literal, so the geometry the
compositor would read could not be established here. If a later tick establishes it, that
is a separate plan.

**Follow-up (not planned here).** `widgets/background.svg` for
`PlasmaComponents.Menu`/`Drawer`/`Popup` and planar applet containers — a separate file
with separate consumers; Mac OS 8.6 menus are white, so that plan will use a white face
and treat the rare `PlasmaComponents.Popup`/`Drawer` as the same menu-like surface.

**Docs.** `README.md`'s status block and Installing inventory now name `dialogs/background.svg`.

### Mac OS 8.6 Platinum scroll bar widget for the desktop theme (done 2026-10-08)

**Planned 2026-10-08 by plan.** Independent of the done frame, button, radio-button,
checkmarks, text-field, and list-item plans: it adds one widget file to the existing
`org.macos8.desktop` desktop-theme package, a new scrollbar test module in `tests/`
with the `TestScrollbar` class, and one `TestInstall` tuple entry in
`tests/test_desktoptheme.py`. It does not touch `button.svg`, `frame.svg`,
`radiobutton.svg`, `checkmarks.svg`, `lineedit.svg`, `listitem.svg`, or
`panel-background.svg`.

**Goal.** Ship `widgets/scrollbar.svg` in the `org.macos8.desktop` desktop theme so
`PlasmaComponents.ScrollBar` (the bar used by `PlasmaComponents.ScrollView`, `Menu`,
`ComboBox` and the clipboard applet) draws the Platinum raised grey thumb and flat grey
trough instead of Breeze's thin rounded translucent handle, and the theme stops inheriting
`widgets/scrollbar.svgz` from the default theme.

**Grounding.**
- Consumer verified in the installed Plasma 6.3.6 QML under
  `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/`:
  `components/ScrollBar.qml` is a `T.ScrollBar` whose `background` is a `KSvg.FrameSvgItem`
  with `imagePath: "widgets/scrollbar"` and
  `prefix: controlRoot.horizontal ? "background-horizontal" : "background-vertical"`, and
  whose `contentItem` (the handle) uses
  `prefix: interactive && (pressed || hovered) && enabled ? "mouseover-slider" : "slider"`.
  Its `background` implicit size is
  `max(elementSize("hint-scrollbar-size"), fixedMargins.left + fixedMargins.right)`; its
  `leftPadding`/`rightPadding`/`topPadding`/`bottomPadding` read
  `{handle.usedPrefix}-hint-{side}-inset` and its `leftInset`/`rightInset`/`topInset`/
  `bottomInset` read `{bgFrame.usedPrefix}-hint-{side}-inset`; its `separator` is visible
  only when `private-hint-show-separator` exists.
  `components/ScrollView.qml`, `components/Menu.qml`, `components/ComboBox.qml` and the
  clipboard pages construct `PlasmaComponents3.ScrollBar`.
- `find /usr/share/plasma/desktoptheme -name 'scrollbar.svg*'` returns only
  `default/widgets/scrollbar.svgz` (a 6px Breeze bar whose `hint-tile-center` is 2x2), so
  today the theme inherits Breeze.
- Palette-derived greys, matching the done button/frame bevel convention: a #DDDDDD face
  with a 1px #000000 outline and a 1px bevel (#FFFFFF top/left, #999999 bottom/right) for
  the thumb, and a #EEEEEE trough (`[Colors:View] BackgroundAlternate=238,238,238`) with
  the same 1px #000000 outline. These are not screenshot-anchored: `TestReferenceAnchors`
  records no scroll-bar pixel, and the reference screenshots that show scroll bars are
  JPEGs, which the project's `tools/png.py` cannot decode.
- Plasma 6 limitations the SVG cannot change and the plan does not try to: the `background`
  (trough) is drawn only while the pointer hovers the bar
  (`opacity: hovered && interactive`), and the QML computes but never uses `arrowPresent`
  (`//TODO: support arrows?`), so the Mac OS 8.6 arrow boxes at the trough ends cannot be
  drawn. The plan ships the correct trough and thumb and records both deviations in the
  SVG comment.

**Approach.**
1. New `widgets/scrollbar.svg` in the package: root
   `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">`
   with a comment naming the widget, its consumers, the four prefixes, and the two Plasma
   deviations (hover-only trough, no arrow boxes).
   - Hints (rects, any opaque `style` colour; KSvg reads geometry): `hint-tile-center`
     10x10 at (3,3); `hint-scrollbar-size` 16x16 at (0,0); and for each of the four
     prefixes `background-vertical`, `background-horizontal`, `slider`,
     `mouseover-slider`: `{prefix}-hint-top-margin` 10x3 at (3,0),
     `{prefix}-hint-bottom-margin` 10x3 at (3,13), `{prefix}-hint-left-margin` 3x10 at
     (0,3), `{prefix}-hint-right-margin` 3x10 at (13,3). No `-inset` hints (so the QML
     falls back to zero padding and the handle fills the 16px track) and no
     `private-hint-show-separator`.
   - Trough nine-slice, identical for `background-vertical` and `background-horizontal`:
     each of the nine `<g id="{prefix}-{slice}">` groups holds a #EEEEEE rect of the
     slice size with a 1px #000000 line along each outer edge (top slice: black row 0;
     bottom: black row 2; left: black column 0; right: black column 2; each corner: its
     two outer edges), square corners.
   - Thumb nine-slice, identical for `slider` and `mouseover-slider`: each group holds a
     #DDDDDD rect of the slice size, a 1px #000000 line along each outer edge, and a 1px
     bevel inside it (#FFFFFF top/left, #999999 bottom/right), square corners, the same
     bevel rule as `button.svg`'s `normal` state.
   - Group origins match the other widgets: top translate(3,0), bottom translate(3,13),
     left translate(0,3), right translate(13,3), center translate(3,3), corners at
     (0,0)/(13,0)/(0,13)/(13,13).
2. `tests/desktoptheme_paths.py` (edit): add
   `SCROLLBAR_SVG = os.path.join(PACKAGE, "widgets", "scrollbar.svg")`.
3. `tests/test_desktoptheme.py` (edit): add `("scrollbar.svg", SCROLLBAR_SVG, 16, 16)` to
   `SVG_CANVASES`, update the stale `SVG_CANVASES` comment (it calls the 12x12 nine-slice
   widgets "four"), and add `os.path.join("widgets", "scrollbar.svg")` to
   `TestInstall.INSTALLED_FILES`.
4. New scrollbar test module in `tests/`, named after the existing
   `test_desktoptheme_listitem.py` pattern, with `class TestScrollbar`, importing `SCROLLBAR_SVG` and `assert_slice_ids_present`,
   `assert_tiles_placed_by_margins`, `assert_corner_pixels`, `assert_no_script_elements`,
   `attribute_values`, `rect_geometry`, `render_slices` from `svg_assertions`:
   - `test_scrollbar_slice_ids`: `assert_slice_ids_present(self, tree,
     ["background-vertical", "background-horizontal", "slider", "mouseover-slider"])`.
   - `test_scrollbar_hint_geometry`: `rect_geometry` equals the exact hint dict above.
   - `test_scrollbar_tiles_placed_by_margins`: `assert_tiles_placed_by_margins` for the
     four prefixes.
   - `test_scrollbar_trough_outline`: `render_slices`; every centre pixel of both trough
     prefixes is #EEEEEE, each trough edge slice's outer row/column is #000000, and each
     corner matches `assert_corner_pixels` with its outer edges black and interior #EEEEEE.
   - `test_scrollbar_thumb_bevel`: `slider` and `mouseover-slider` render identically;
     every centre pixel is #DDDDDD; the top slice's three rows are #000000/#FFFFFF/#DDDDDD,
     the bottom's #DDDDDD/#999999/#000000, the left's three columns
     #000000/#FFFFFF/#DDDDDD, the right's #DDDDDD/#999999/#000000, and each corner matches
     `assert_corner_pixels` with its outline, bevel and face pixels.
   - `test_scrollbar_colours`:
     `attribute_values(tree, "fill") == {"#000000", "#FFFFFF", "#999999", "#DDDDDD", "#EEEEEE"}`.
   - `test_no_script_elements`.
5. `README.md` (edit): add "scroll bar" to the `tumwater:status` block's desktop-theme
   widget parenthetical, and `widgets/scrollbar.svg` (the raised grey thumb and flat grey
   trough for `PlasmaComponents.ScrollBar`) to the Installing section's desktop-theme
   sentence.

**Files touched.** New: `scrollbar.svg` in the package's `widgets/` subdirectory and a
scrollbar test module in `tests/` beside the existing `test_desktoptheme_listitem.py`.
Edited:
`tests/desktoptheme_paths.py` (`SCROLLBAR_SVG`), `tests/test_desktoptheme.py`
(`SVG_CANVASES`, `TestInstall` `INSTALLED_FILES`), `README.md`. No change to the color
scheme, the look-and-feel package, the Makefile, or the other widgets.

**Acceptance criteria.**
- `make check` exits 0 with `TestScrollbar` passing and the extended `TestInstall`
  byte-identity assertion.
- The scrollbar SVG parses and contains the 36 `{prefix}-{slice}` ids for the four
  prefixes, the 16 margin hints, `hint-tile-center` and `hint-scrollbar-size`; every trough
  centre is #EEEEEE and every thumb centre #DDDDDD; the only parsed `fill` values are
  #000000, #FFFFFF, #999999, #DDDDDD and #EEEEEE.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/desktoptheme/org.macos8.desktop/widgets/scrollbar.svg` byte-identical
  to source.
- Manual smoke test (needs a Plasma session): a `PlasmaComponents.ScrollView`, `Menu` or
  `ComboBox` shows a 16px-wide raised #DDDDDD thumb with a black outline and bevel; the
  trough appears while hovered as a flat #EEEEEE bar with a black outline; the Mac arrow
  boxes at the ends are absent (Plasma does not render them).

**Follow-up (not planned here).** `widgets/background.svg` for dialog/popup/applet
backgrounds: the same SVG serves `Menu` (white in Mac OS 8.6) and `Dialog`/applet
containers (grey), so it needs a decision before it can be planned.

### Mac OS 8.6 Platinum list item widget for the desktop theme (done 2026-10-08)

**Planned 2026-10-08 by plan.** Independent of the done frame, button, radio-button,
checkmarks, and text-field plans: it adds one widget file to the existing
`org.macos8.desktop` desktop-theme package, a new `test_desktoptheme_listitem.py` module beside the existing
`tests/test_desktoptheme_lineedit.py` with the `TestListItem` class, and one `TestInstall` tuple
entry in `tests/test_desktoptheme.py`. It does not touch
`button.svg`, `frame.svg`, `radiobutton.svg`, `checkmarks.svg`, `lineedit.svg`, or
`panel-background.svg`.

**Goal.** Ship `widgets/listitem.svg` in the `org.macos8.desktop` desktop theme so
`PlasmaComponents.ItemDelegate` (and the applet `PlasmaExtras.ListItem`) draw the Platinum flat
selection row instead of Breeze's rounded gradient, and so the theme stops inheriting
`widgets/listitem.svgz` from the default theme.

**Grounding.**
- Consumers verified in the installed Plasma 6.3.6 QML under
  `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/`:
  - `components/private/DefaultListItemBackground.qml` (the `background` of
    `components/ItemDelegate.qml`) is a `KSvg.FrameSvgItem` with `imagePath: "widgets/listitem"`
    and `prefix: control.highlighted || control.down ? "pressed" : "normal"`, with a nested
    `widgets/listitem` `prefix: "hover"` overlay; the delegate's padding is
    `background.margins`.
  - `extras/ListItem.qml` uses prefixes `pressed`/`normal`/`section` and the `separator`
    element; `components/ToolBar.qml` uses the `separator` element;
    `private/clipboard/ClipboardMenu.qml` uses prefix `normal`.
  - A missing prefix or element renders nothing — the same fallback the done button and
    lineedit plans rely on.
- Palette: `[Colors:Selection] BackgroundNormal=204,204,255` (#CCCCFF) in
  `theme/color-schemes/MacOS8.colors`, with `[Colors:Selection] ForegroundNormal=0,0,0`; the
  selected-delegate text colour is Kirigami's highlighted text, i.e. that black.
  `TestReferenceAnchors.test_selection_background` already decodes
  `macos8.6-screenshots/firstboot_betawiki.png` and pins the selection fill at (200,63). A scan
  of that PNG with `tools/png.py` finds the selected Setup Assistant row as a flat #CCCCFF
  rectangle (x 31..428, y 61..85) flush against the list's sunken frame, with no outline of its
  own.
- `find /usr/share/plasma/desktoptheme -name 'listitem.svg*'` returns only
  `default/widgets/listitem.svgz`, so today the theme inherits Breeze's rounded rows.
- Mac OS 8.6 has no hover highlight, no section headers, and no row separators, so the plan
  omits the `hover` and `section` prefixes and the `separator` element. A hovered or sectioned
  row therefore stays pixel-identical to a normal one, and ToolBar draws no separator line.
- A nine-slice element with no rendered content has no bounding box for KSvg to read margins
  from, so the default theme draws its `normal` slices at `opacity:0.01`. This plan follows
  that proven pattern: the `normal` slices carry `style="fill:#FFFFFF" fill-opacity="0.01"`
  geometry with no `fill` attribute, contributing the 3px margins while painting nothing
  perceptible.

**Approach.**
1. New file `widgets/listitem.svg` in the `org.macos8.desktop` package: root
   `<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12">` with a
   comment naming the widget, its consumers, and the normal/pressed-only contract.
   - Nine-slice hints (rects, any opaque `style` colour; KSvg reads geometry, not colour):
     `hint-tile-center` 6x6 at (3,3); for each of `normal` and `pressed`,
     `{prefix}-hint-top-margin` 6x3 at (3,0), `{prefix}-hint-bottom-margin` 6x3 at (3,9),
     `{prefix}-hint-left-margin` 3x6 at (0,3), `{prefix}-hint-right-margin` 3x6 at (9,3).
   - `normal` nine-slice: one group per slice on the 3px border / 6px centre grid, square
     corners, each holding a single rect of the slice's size with
     `style="fill:#FFFFFF" fill-opacity="0.01"` and no `fill` attribute:
     `normal-top` translate(3,0) 6x3, `normal-bottom` translate(3,9) 6x3, `normal-left`
     translate(0,3) 3x6, `normal-right` translate(9,3) 3x6, `normal-center` translate(3,3)
     6x6, `normal-topleft` 3x3, `normal-topright` translate(9,0) 3x3, `normal-bottomleft`
     translate(0,9) 3x3, `normal-bottomright` translate(9,9) 3x3.
   - `pressed` nine-slice: the same nine groups at the same origins, each holding a single
     rect of the slice's size with `fill="#CCCCFF"` (flat selection fill, no bevel, no
     outline).
   No `hover-*`, `section-*`, `separator`, `focus-*`, `class="ColorScheme-*"`,
   `currentColor`, or `<script>`, and no element outside the 12x12 canvas.
2. `tests/desktoptheme_paths.py` (edit): add
   `LISTITEM_SVG = os.path.join(PACKAGE, "widgets", "listitem.svg")` beside `LINEEDIT_SVG`.
3. `tests/test_desktoptheme.py` (edit): add `("listitem.svg", LISTITEM_SVG, 12, 12)` to
   `SVG_CANVASES`, and add `os.path.join("widgets", "listitem.svg")` to
   `TestInstall.INSTALLED_FILES` (the byte-identity tuple the lifecycle cases iterate).
4. New `test_desktoptheme_listitem.py` beside `tests/test_desktoptheme_lineedit.py` with
   `class TestListItem`, importing
   `LISTITEM_SVG` from `desktoptheme_paths` and `SLICE_IDS`, `attribute_values`,
   `render_slices`, `assert_tiles_placed_by_margins`, and `assert_no_script_elements` from
   `svg_assertions`:
     - `test_listitem_slice_ids`: parse; assert the id set contains every
       `{normal,pressed}-{slice}` id for the nine `SLICE_IDS`, plus `hint-tile-center` and the
       four `{prefix}-hint-{side}-margin` ids for both prefixes.
     - `test_listitem_selection_is_flat_selection_colour`:
       `render_slices(ET.parse(LISTITEM_SVG))` gives every `pressed-*` slice all #CCCCFF, so the
       selection cannot silently gain a bevel or the grey button face.
     - `test_listitem_normal_has_no_fill`: every `normal-*` slice's pixel value is `None` (its
       rects carry no `fill` attribute) and `attribute_values(tree, "fill-opacity") == {"0.01"}`.
     - `test_listitem_colours`: `attribute_values(tree, "fill") == {"#CCCCFF"}` (the hints and
       the normal slices use `style`, so they are excluded).
     - `test_listitem_tiles_placed_by_margins`:
       `assert_tiles_placed_by_margins(self, self.tree, ["normal", "pressed"])`.
     - `test_no_script_elements`.
5. `README.md` (edit): add "list item" to the `tumwater:status` block's desktop-theme widget
   parenthetical, and `widgets/listitem.svg` (the flat #CCCCFF selection row for list and
   applet item delegates) to the Installing section's desktop-theme sentence.

**Files touched.** New: `listitem.svg` in the package's `widgets/` subdirectory and
`test_desktoptheme_listitem.py` beside `tests/test_desktoptheme_lineedit.py`. Edited:
`tests/desktoptheme_paths.py` (`LISTITEM_SVG`),
`tests/test_desktoptheme.py` (`SVG_CANVASES`, `TestInstall` `INSTALLED_FILES`), `README.md`. No
change to the color scheme, the look-and-feel package, the Makefile, or the other widgets.

**Acceptance criteria.**
- `make check` exits 0 with `TestListItem` passing and the extended `TestInstall` byte-identity
  assertion.
- The listitem SVG parses and contains the eighteen `{normal,pressed}-{slice}` ids, the nine
  hint ids, and the `hint-tile-center` id; every `pressed-*` slice renders entirely #CCCCFF;
  every `normal-*` slice has no `fill` attribute and a `fill-opacity` of 0.01; the only parsed
  `fill` attribute value is #CCCCFF.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/desktoptheme/org.macos8.desktop/widgets/listitem.svg` byte-identical to
  source (via the extended `TestInstall` tuple).
- Manual smoke test (needs a Plasma session): a list drawn with `PlasmaComponents.ItemDelegate`
  (Kickoff, System Settings, or a file dialog) shows the selected row as a flat #CCCCFF
  rectangle with black text and no rounded gradient or outline; an unselected row shows the
  view background; hovering a row changes nothing; every other widget is unchanged.

**Follow-up (not planned here).** `widgets/scrollbar.svg` (constrained: the ScrollBar QML
shows its track only while hovered and computes but never uses `arrowPresent`, so the Mac arrow
buttons cannot be drawn) and `widgets/background.svg` for dialog/applet backgrounds.

### Mac OS 8.6 Platinum text field widget for the desktop theme (done 2026-10-08)

**Planned 2026-10-08 by plan.** Independent of the done frame, button, radio-button, and
checkmarks plans: it adds one widget file to the existing `org.macos8.desktop` desktop-theme
package and a `TestLineEdit` class plus one `TestInstall` tuple entry to
`tests/test_desktoptheme.py`. It does not touch `button.svg`, `frame.svg`, `radiobutton.svg`,
`checkmarks.svg`, or `panel-background.svg`.

**Goal.** Ship `widgets/lineedit.svg` in the `org.macos8.desktop` desktop theme so
`PlasmaComponents.TextField`, `TextArea`, `SpinBox` and an editable `ComboBox` draw the Platinum
sunken white text field instead of the Breeze rounded field, and so the theme stops inheriting
`widgets/lineedit.svgz` from the default theme.

**Grounding.**
- Consumers verified in the installed Plasma 6.3.6 QML under
  `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/`:
  - `TextField.qml`'s background is a `KSvg.FrameSvgItem` with `imagePath: "widgets/lineedit"`,
    `prefix: "base"`, overlaid by two more `widgets/lineedit` FrameSvgItems with `prefix:
    "hover"` (`opacity: control.hovered`) and `prefix: control.visualFocus &&
    hasElement("focusframe-center") ? "focusframe" : "focus"` (`opacity: control.visualFocus ||
    control.activeFocus`).
  - `TextArea.qml`'s background is `widgets/lineedit` `prefix: "base"`, with
    `private/TextFieldFocus.qml` drawing `widgets/lineedit` prefixes `"hover"`/`"focus"`/
    `"focusframe"`.
  - `SpinBox.qml` draws `widgets/lineedit` prefixes `"base"`, `"hover"`, and
    `"focus"`/`"focusframe"`; `ComboBox.qml` uses `imagePath: control.editable ?
    "widgets/lineedit" : "widgets/button"` for the editable field.
- The default `lineedit.svgz` (`zcat
  /usr/share/plasma/desktoptheme/default/widgets/lineedit.svgz`) carries a nine-slice for each of
  `base`, `hover`, `focus`, and `focusframe`, plus `hint-tile-center`,
  `{prefix}-hint-{top,bottom,left,right}-margin` (2px for `base`), and `hint-focus-over-base`.
  `KSvg.Svg` resolves a theme file the current theme lacks to the default theme, and
  `find /usr/share/plasma/desktoptheme -name 'lineedit.svg*'` returns only
  `default/widgets/lineedit.svgz`, so today the theme inherits the Breeze field.
- Missing prefixes render nothing — the same fallback behavior the done button plan relies on:
  `hover` is a separate overlay whose opacity gates it, and `focus`/`focusframe` are chosen only
  when visual focus allows. Mac OS 8.6 text fields have no hover highlight and no focus ring (the
  blinking caret is the focus cue), so `hover`, `focus`, and `focusframe` are deliberately omitted
  and a hovered or focused field stays pixel-identical to an idle one.
- Palette: `[Colors:View] BackgroundNormal=255,255,255` (#FFFFFF) in
  `theme/color-schemes/MacOS8.colors`, with the #000000 outline and #999999 shadow the
  frame/button/radio plans pin. A scan of the reference set for the sunken pattern (black top edge,
  #999999 next row, near-#FFFFFF third row) finds it in
  `macos8.6-screenshots/desktop_archiveorg8.6hd.png` at (430,183) (`#00000B`, `#9B9B99`,
  `#FEFEFF`), so Mac OS 8.6 draws recessed surfaces with a grey top/left shadow. The Platinum text
  field is specified here as a white face with that same sunken bevel, reusing the done
  `frame.svg` `sunken` geometry rather than introducing a new one.
- The package is installed with `cp -r` (the `Makefile` `install_package` macro), so the new file
  needs no Makefile change.

**Approach.**
1. New file `widgets/lineedit.svg` in the `org.macos8.desktop` package: root
   `<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12">` with a
   comment naming the widget, its consumers, and the base-only contract.
   - Nine-slice hints: `hint-tile-center` 6x6 at (3,3); `base-hint-top-margin` 6x3 at (3,0),
     `base-hint-bottom-margin` 6x3 at (3,9), `base-hint-left-margin` 3x6 at (0,3),
     `base-hint-right-margin` 3x6 at (9,3). Fill them any opaque colour through `style` (KSvg
     reads their geometry, not their colour).
   - One `base` nine-slice group per slice on the 3px border / 6px centre grid, square corners,
     exactly the done `frame.svg` `sunken` geometry with the face changed from #DDDDDD to
     #FFFFFF: outer 1px #000000, 1px #999999 inside the top/left, 1px #FFFFFF inside the
     bottom/right, #FFFFFF face. Concretely:
     - `base-top` (translate 3,0): 6x3 #FFFFFF, then `y=1` 6x1 #999999, then 6x1 #000000.
     - `base-bottom` (translate 3,9): 6x3 #FFFFFF, then `y=1` 6x1 #FFFFFF, then `y=2` 6x1 #000000.
     - `base-left` (translate 0,3): 3x6 #FFFFFF, then `x=1` 1x6 #999999, then 1x6 #000000.
     - `base-right` (translate 9,3): 3x6 #FFFFFF, then `x=1` 1x6 #FFFFFF, then `x=2` 1x6 #000000.
     - `base-center` (translate 3,3): 6x6 #FFFFFF.
     - `base-topleft`: 3x3 #FFFFFF, `x=1 y=1` 2x1 #999999, `x=1 y=1` 1x2 #999999, 3x1 #000000,
       1x3 #000000.
     - `base-topright` (translate 9,0): 3x3 #FFFFFF, `x=0 y=1` 2x1 #999999, `x=1 y=1` 1x2
       #FFFFFF, 3x1 #000000, `x=2` 1x3 #000000.
     - `base-bottomleft` (translate 0,9): 3x3 #FFFFFF, `x=1 y=0` 1x3 #999999, `x=1 y=1` 2x1
       #FFFFFF, `y=2` 3x1 #000000, 1x3 #000000.
     - `base-bottomright` (translate 9,9): 3x3 #FFFFFF, `x=0 y=1` 2x1 #FFFFFF, `x=1 y=0` 1x3
       #FFFFFF, `y=2` 3x1 #000000, `x=2` 1x3 #000000.
   No `hover-*`, `focus-*`, `focusframe-*`, `hint-focus-over-base`, `class="ColorScheme-*"`,
   `currentColor`, or `<script>`, and no fill outside the 12x12 canvas.
2. `tests/test_desktoptheme.py` (edit):
   - Add `LINEEDIT_SVG = os.path.join(PACKAGE, "widgets", "lineedit.svg")` beside
     `CHECKMARKS_SVG`.
   - Add `class TestLineEdit` beside `TestCheckmarks`:
     - `test_lineedit_slice_ids`: parse; assert every `base-{slice}` id in `SLICE_IDS` and every
       `base-hint-{side}-margin` id are present, plus `hint-tile-center`.
     - `test_lineedit_colours`: assert the parsed `fill` attributes are exactly `{"#FFFFFF",
       "#999999", "#000000"}` (the hints use `style`, so they are excluded).
     - `test_lineedit_face_is_white`: `render_slices(ET.parse(LINEEDIT_SVG))` gives `base-center`
       every pixel #FFFFFF, so the field cannot silently become the grey frame face.
     - `test_no_script_elements`: no element tag ends in `script`.
   - Add `os.path.join("widgets", "lineedit.svg")` to `TestInstall.INSTALLED_FILES` (the
     byte-identity tuple the lifecycle cases iterate).
3. `README.md` (edit): add "text field" to the `tumwater:status` block's desktop-theme widget
   parenthetical, and `widgets/lineedit.svg` (the white sunken field for
   `TextField`/`TextArea`/`SpinBox`) to the Installing section's desktop-theme sentence.

**Files touched.** New: `lineedit.svg` in the package's `widgets/` subdirectory. Edited:
`tests/test_desktoptheme.py` (`TestLineEdit`, `TestInstall` tuple), `README.md`. No change to the
color scheme, the look-and-feel package, the Makefile, or the other widgets.

**Acceptance criteria.**
- `make check` exits 0 with `TestLineEdit` passing and the extended `TestInstall` byte-identity
  assertion.
- The lineedit SVG parses and contains the nine `base-{slice}` ids, the four
  `base-hint-{side}-margin` ids, and `hint-tile-center`; its parsed `fill` values are exactly
  #FFFFFF, #999999, and #000000; `base-center` is entirely #FFFFFF.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/desktoptheme/org.macos8.desktop/widgets/lineedit.svg` byte-identical to
  source (via the extended `TestInstall` tuple).
- Manual smoke test (needs a Plasma session): a `PlasmaComponents.TextField`/`TextArea`/`SpinBox`
  renders a #FFFFFF field with a 1px #000000 outline and a 1px #999999 shadow inside the top/left,
  with no Breeze blue tint, hover highlight, or focus ring; every other widget is unchanged.

**Follow-up (not planned here).** `widgets/actionbutton.svg` for `RoundButton`/`Dial`/`RoundShadow`,
`widgets/scrollbar.svg`, then `listitem` and `background`.

### Mac OS 8.6 Platinum checkmarks widget for the desktop theme (done 2026-10-08)

**Planned 2026-10-08 by plan.** Independent of the done frame, button, and radio-button plans: it
adds one widget file to the existing `org.macos8.desktop` desktop-theme package and a
`TestCheckmarks` class plus one `TestInstall` tuple entry to `tests/test_desktoptheme.py`. It does
not touch `button.svg`, `frame.svg`, `radiobutton.svg`, or `panel-background.svg`.

**Goal.** Ship `widgets/checkmarks.svg` in the `org.macos8.desktop` desktop theme so
`PlasmaComponents.CheckBox` draws the Platinum black checkmark over its face instead of the Breeze
glyph, and so the theme stops inheriting `widgets/checkmarks.svgz` from the default theme. It is
the glyph half of the `CheckBox`/`RadioButton` indicators the button and radio-button plans left on
Breeze glyphs.

**Grounding.**
- `CheckIndicator.qml` (installed at
  `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/CheckIndicator.qml`, 72 lines) is
  the `indicator:` of `CheckBox.qml`. Its root is a `KSvg.FrameSvgItem` with
  `imagePath: "widgets/button"`, `prefix: "normal"`, `implicitWidth`/`implicitHeight`
  `Kirigami.Units.iconSizes.small` (16px), and it overlays a `KSvg.SvgItem` anchored to fill the
  root whose `svg` is `KSvg.Svg { imagePath: "widgets/checkmarks" }` with `elementId: "checkbox"`.
- The overlay's `opacity` is 1 when `control.checkState == Qt.Checked`, 0.5 when
  `Qt.PartiallyChecked`, and 0 when unchecked (and `control.checked ? 1 : 0` for a non-`CheckBox`
  `AbstractButton`). So `checkbox` is a checked-only overlay drawn on top of the button face: the
  file supplies the glyph, not the box.
- The overlay uses `anchors.fill: parent`, so KSvg scales the element by its bounds. A bare glyph
  would be stretched to the 16x16 cell: each element therefore wraps the glyph in a `<g>` with an
  invisible full-cell `<rect fill="none">`, which pins the element bounds to 16x16 so the glyph
  draws 1:1. Qt computes a rect's bounds from its geometry (`QSvgRect::internalBounds` maps
  `m_rect` regardless of fill), so the `fill="none"` rect still sets the bounds.
- `RadioIndicator.qml`'s fallback `compatibilityComponent` draws `widgets/actionbutton` plus a
  `KSvg.SvgItem` on `widgets/checkmarks` with `elementId: "radiobutton"`; the modern
  `radiobuttonComponent` is selected instead now that the theme ships `widgets/radiobutton.svg`.
  `radiobutton` is included so the file is a complete replacement for the inherited Breeze
  `checkmarks.svgz`, which carries exactly `checkbox` and `radiobutton`.
- `KSvg.Svg` resolves a theme file the current theme lacks to the default theme, and
  `find /usr/share/plasma/desktoptheme -name 'checkmarks.svg*'` returns only
  `default/widgets/checkmarks.svgz`, so today the theme inherits the Breeze glyph (a translucent
  `ColorScheme-ButtonFocus` rounded rect plus a dark `ColorScheme-Text` check) over the Platinum
  button face.
- The default `checkmarks.svgz` (parsed from
  `zcat /usr/share/plasma/desktoptheme/default/widgets/checkmarks.svgz`) is a 16x32 canvas:
  `checkbox` occupies the top 16x16 cell and `radiobutton` the bottom 16x16 cell (a circle r=7.5
  plus a dot r=3 at cy=24). Its check path is `M 3.5,8.5 6.5,11.5 l 6,-6` stroked 2px.
- Palette is the `#000000` the button/radio plans pin (`[Colors:Window]`/`[Colors:Button]`
  foreground in `theme/color-schemes/MacOS8.colors`). Mac OS 8.6 has no partial state, so no third
  element is needed.
- **Known limitation (not fixable here).** The checkbox *face* stays `widgets/button` `normal` —
  the `#DDDDDD` rounded face — because `CheckIndicator.qml` hardcodes that `imagePath`; a desktop
  theme cannot override a component's `imagePath`. The checked overlay therefore draws the glyph on
  the Platinum button face, not on a white square. The `radiobutton` fallback face is likewise
  `widgets/actionbutton` (unshipped, so Breeze).

**Approach.**
1. New file `widgets/checkmarks.svg` in the `org.macos8.desktop` package: root
   `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="32" viewBox="0 0 16 32">` with a
   comment naming the widget, its consumers, and the checked-only overlay contract.
   - Each element is a `<g>` holding an invisible full-cell bounding `<rect fill="none">` plus its
     glyph, so KSvg scales the element to the 16x16 cell and draws the glyph 1:1.
   - `<g id="checkbox">` in the top cell: the bounding rect `x="0" y="0" width="16" height="16"
     fill="none"`, then the 2px black check
     `<path d="M 3.5,8.5 L 6.5,11.5 L 12.5,5.5" fill="none" stroke="#000000" stroke-width="2"
     stroke-linecap="square" stroke-linejoin="miter"/>` (the default theme's check shape, with
     `currentColor` resolved to `#000000`).
   - `<g id="radiobutton">` in the bottom cell: the bounding rect `x="0" y="16" width="16"
     height="16" fill="none"`, then the compatibility dot `<circle cx="8" cy="24" r="3"
     fill="#000000"/>`.
   No `hint-size`/`hint-tile-center` (no consumer reads them), no `class="ColorScheme-*"`, no
   `currentColor`, no `<script>`, and no fill outside the 16x32 canvas.
2. `tests/test_desktoptheme.py` (edit):
   - Add `CHECKMARKS_SVG = os.path.join(PACKAGE, "widgets", "checkmarks.svg")` beside
     `RADIOBUTTON_SVG`.
   - Add `class TestCheckmarks` beside `TestRadioButton`:
     - `test_checkmarks_contract`: `ET.parse` the file; assert ids `checkbox` and `radiobutton` are
       present; assert the parsed `stroke` attributes are exactly `{"#000000"}`; assert the parsed
       `fill` attributes are exactly `{"none", "#000000"}`; assert no element tag ends in `script`.
     - `test_checkmarks_geometry`: assert `checkbox` is a `<g>` whose children are one bounding
       `rect` (`x=0`, `y=0`, `width=16`, `height=16`, `fill="none"`) and one `path` with `d` exactly
       `"M 3.5,8.5 L 6.5,11.5 L 12.5,5.5"`, `stroke-width="2"`, and `fill="none"`; assert
       `radiobutton` is a `<g>` whose children are one bounding `rect` (`x=0`, `y=16`, `width=16`,
       `height=16`, `fill="none"`) and one `circle` with `r == 3` and `fill == "#000000"`.
   - Add `os.path.join("widgets", "checkmarks.svg")` to the tuple in
     `TestInstall.test_make_install_copies_package_byte_for_byte`.
3. `README.md` (edit): add `widgets/checkmarks.svg` to the desktop theme's widget inventory and the
   status sentence, naming the 2px black check `CheckBox` overlays when checked and the
   `RadioIndicator` compatibility dot.

**Files touched.** New: `checkmarks.svg` in the package's `widgets/` subdirectory. Edited:
`tests/test_desktoptheme.py` (`TestCheckmarks`, `TestInstall` tuple), `README.md`. No change to the
color scheme, the look-and-feel package, the Makefile, or the other widgets.

**Acceptance criteria.**
- `make check` exits 0 with `TestCheckmarks` passing.
- The checkmarks SVG parses and contains `checkbox` and `radiobutton`, each a `<g>` with a full-cell
  `fill="none"` bounding rect and one glyph child; `checkbox`'s path has the pinned `d`,
  `stroke-width="2"`, and `stroke="#000000"`; `radiobutton`'s circle has `r=3` and
  `fill="#000000"`.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/desktoptheme/org.macos8.desktop/widgets/checkmarks.svg` byte-identical to
  source (via the extended `TestInstall` tuple).
- Manual smoke test (needs a Plasma session): a checked `PlasmaComponents.CheckBox` draws a black
  2px check over the Platinum face with no Breeze blue tint, unchecking hides it, and every other
  widget is unchanged.

**Follow-up (not planned here).** `widgets/actionbutton.svg` for `RoundButton`/`Dial`/`RoundShadow`,
and the checkbox-face mismatch noted above (a Plasma 6.3 `CheckIndicator.qml` constraint, not a
missing SVG), then `scrollbar`, `listitem`, and `background`.


### Mac OS 8.6 Platinum radio button widget for the desktop theme (done 2026-10-07)

**Planned 2026-10-07 by plan.** Independent of the done frame and button plans: it adds one widget
file to the existing `org.macos8.desktop` desktop-theme package and a `TestRadioButton` class plus
one `TestInstall` tuple entry to `tests/test_desktoptheme.py`. It does not touch `button.svg`,
`frame.svg`, or `panel-background.svg`.

**Goal.** Ship `widgets/radiobutton.svg` in the `org.macos8.desktop` desktop theme so
`PlasmaComponents.RadioButton` draws the Platinum radio button — a white circle with a 1px black
outline and, when selected, a black centre dot — instead of the Breeze `actionbutton` face. It is
the radio half of the `CheckBox`/`RadioButton` indicators the button plan left on Breeze
faces/glyphs.

**Grounding.**
- `RadioIndicator.qml` (installed at
  `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/RadioIndicator.qml`) loads
  `KSvg.Svg { imagePath: "widgets/radiobutton" }` and selects its `radiobuttonComponent` only when
  `radioButtonSvg.fromCurrentImageSet` is true; the fallback `compatibilityComponent` draws
  `widgets/actionbutton` plus `widgets/checkmarks` elementId `"radiobutton"`. The default theme is
  the only installed theme with `widgets/radiobutton.svgz` (`find /usr/share/plasma/desktoptheme
  -name 'radiobutton.svg*'` returns just that file; breeze-light/breeze-dark ship no `widgets/`
  directory), so today `fromCurrentImageSet` is false for this theme and radios render the Breeze
  face; shipping our own `widgets/radiobutton.svg` makes it true. The file's own comment states the
  mechanism: "fromCurrentImageSet is false for them. This is because they don't contain any SVGs
  and inherit all of them from the default theme."
- The modern `radiobuttonComponent` draws, each `anchors.centerIn: parent` with
  `implicitWidth: naturalSize.width`: `normal` (always visible), `shadow` (`opacity: enabled &&
  !control.down`), `checked` (opacity when checked), `focus`, `hover`, and `symbol`
  (`scale: control.checked`, so hidden at 0). `hintSize` uses `elementSize("hint-size")` when the
  element is present, else `Kirigami.Units.iconSizes.small` (16px). Missing elements render
  nothing, so the file need not ship the states Mac OS 8.6 does not have.
- The default `radiobutton.svgz` (parsed from
  `zcat /usr/share/plasma/desktoptheme/default/widgets/radiobutton.svgz`) has ids `normal`,
  `checked`, `focus`, `hover`, `shadow`, `symbol`, `hint-size`; its `hint-size` is a circle r=8
  (16x16) and its `symbol` a circle r=3 (6x6).
- Mac OS 8.6 radio buttons have no hover highlight, focus ring, or drop shadow, so those elements
  are deliberately absent. The palette is the `#FFFFFF`/`#000000` the button plan pins
  (`[Colors:Button]`/`[Colors:Window]` in `theme/color-schemes/MacOS8.colors`); the 1px outline is
  a black filled circle under a white filled circle, so the ring stays crisp with no stroke
  antialiasing.
- The package is installed with `cp -r` (the `Makefile` `install_package` macro), so the new file
  needs no Makefile change.

**Approach.**
1. New file `widgets/radiobutton.svg` in the `org.macos8.desktop` package: root
   `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="16" viewBox="0 0 48 16">` with a
   comment naming the widget and its two states.
   - `<g id="normal">` centred at (8,8): `<circle cx="8" cy="8" r="8" fill="#000000"/>` then
     `<circle cx="8" cy="8" r="7" fill="#FFFFFF"/>` — a 16x16 bounding box and a 1px black ring.
   - `<circle id="symbol" cx="40" cy="8" r="3" fill="#000000"/>` — the 6x6 selected dot.
   - `<circle id="hint-size" cx="24" cy="8" r="8" style="fill:#ff00ff"/>` — geometry only, colour
     through `style` so it stays out of the parsed `fill` set (mirrors `button.svg`'s hint rects).
   No `shadow`/`checked`/`focus`/`hover`, no `mask-*`, no `class="ColorScheme-*"`, no `<script>`,
   and no fill outside the 48x16 canvas.
2. `tests/test_desktoptheme.py` (edit):
   - Add `RADIOBUTTON_SVG = os.path.join(PACKAGE, "widgets", "radiobutton.svg")` beside
     `BUTTON_SVG`.
   - Add `class TestRadioButton` beside `TestButton`:
     - `test_radiobutton_contract`: `ET.parse` the file; assert ids `normal`, `symbol`, and
       `hint-size` are present; assert the parsed `fill` attributes are exactly
       `{"#FFFFFF", "#000000"}`; assert no element tag ends in `script`.
     - `test_radiobutton_geometry`: assert the `normal` group holds two `circle` children with radii
       8 and 7, and that the `symbol` circle has radius 3 (so the ring and dot cannot silently
       shrink or vanish).
   - Add `os.path.join("widgets", "radiobutton.svg")` to the tuple in
     `TestInstall.test_make_install_copies_package_byte_for_byte`.
3. `README.md` (edit): extend the `tumwater:status` sentence that enumerates the desktop theme's
   widgets with "and whose `widgets/radiobutton.svg` provides the Platinum radio button (a white
   face with a 1px black outline and a black selection dot)".

**Files touched.** New: `radiobutton.svg` in the package's `widgets/` subdirectory. Edited:
`tests/test_desktoptheme.py` (`TestRadioButton`, `TestInstall` tuple), `README.md`. No change to the
color scheme, the look-and-feel package, the Makefile, or the other widgets.

**Acceptance criteria.**
- `make check` exits 0 with `TestRadioButton` passing.
- The radio SVG parses and contains `normal`, `symbol`, and `hint-size`; its parsed `fill`
  attributes are exactly `#FFFFFF` and `#000000`; the `normal` circles have radii 8 and 7 and the
  `symbol` circle radius 3.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/desktoptheme/org.macos8.desktop/widgets/radiobutton.svg` byte-identical to
  source (via the extended `TestInstall` tuple).
- Manual smoke test (needs a Plasma session): a `PlasmaComponents.RadioButton` renders a white
  circle with a 1px black outline, and when selected shows a black centre dot with no Breeze blue,
  hover highlight, or drop shadow; every other widget is unchanged.

**Follow-up (not planned here).** `widgets/checkmarks.svg` for the checkbox/radio glyph overlays,
`widgets/actionbutton.svg` for `RoundButton`/`Dial`/`RoundShadow`, then `scrollbar`, `listitem`,
and `background`.

### Mac OS 8.6 Platinum frame widget for the desktop theme (done 2026-10-07)

**Planned 2026-10-07 by plan.** Requires the desktop theme package from the panel-background plan
above (its `org.macos8.desktop` directory under `theme/desktop-themes/` and its `test_desktoptheme.py`
under `tests/`); this plan adds
one widget file to that package and does not create it.

**Goal.** Ship `widgets/frame.svg` in the `org.macos8.desktop` desktop theme so the Platinum
raised/plain/sunken border replaces Breeze wherever Plasma draws a frame: `PlasmaComponents.Frame`,
`GroupBox`, the kicker application-menu sidebar, and applet `FrameSvg` consumers. It is the second
widget family after the menu-bar background, and the first multi-state one.

**Grounding.**
- Consumers verified in the installed Plasma 6.3.6 QML: `widgets/frame` with prefix `plain` is set by
  `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/Frame.qml` (`background: KSvg.FrameSvgItem`,
  `prefix: "plain"`), `.../components/GroupBox.qml` (`prefix: "plain"`),
  `/usr/share/plasma/plasmoids/org.kde.plasma.kicker/contents/ui/MenuRepresentation.qml` (the app-menu
  sidebar), and `/usr/share/plasma/plasmoids/org.kde.plasma.calculator/contents/ui/main.qml`. The
  `raised`/`sunken` prefixes are the classic `PlasmaCore.FrameSvg` variants applets pass to
  `imagePath: "widgets/frame"`; the system `default` theme ships all three.
- The default `frame.svgz` (`zcat /usr/share/plasma/desktoptheme/default/widgets/frame.svgz`) id
  contract is `{plain,raised,sunken}-{center,top,bottom,left,right,topleft,topright,bottomleft,bottomright}`,
  `{prefix}-hint-{top,bottom,left,right}-margin`, and one `hint-tile-center`; it has no `mask-*` or
  `shadow-*` elements. Its hint margins are 6px (the value is a hint rect's height for top/bottom and
  its width for left/right); ours can be 3px for a 1px border plus 1px bevel.
- Palette from `theme/color-schemes/MacOS8.colors`: `[Colors:Button]`/`[Colors:Window]`
  `BackgroundNormal=221,221,221` (#DDDDDD) and `ForegroundNormal=0,0,0` (#000000). The panel-background
  plan already established #FFFFFF top/left highlight and #999999 bottom/right shadow for this theme.
- Mac OS 8.6 window/frame corners are square, so the slices need no rounded-corner masks; the SVG's
  own alpha is the shape.
- The panel-background plan's `make install` copies the package with `cp -r`, so a new widget file
  needs no Makefile change.

**Approach.**
1. New file `frame.svg` in that package's `widgets/` subdirectory — a 12x12 canvas, square
   corners, 3px fixed border region, 6px centre tile. Slice geometry: `topleft`/`topright`/
   `bottomleft`/`bottomright` 3x3 at (0,0)/(9,0)/(0,9)/(9,9); `top` 6x3 at (3,0), `bottom` 6x3 at
   (3,9), `left` 3x6 at (0,3), `right` 3x6 at (9,3), `center` 6x6 at (3,3). Hint rects:
   `{prefix}-hint-top-margin` a rect whose bounding-box height is 3, `-bottom-margin` height 3,
   `-left-margin` width 3, `-right-margin` width 3, and `hint-tile-center` 6x6; fill them any opaque
   colour (KSvg reads the geometry, not the colour).
2. Author the three nine-slice groups as `plain`, `raised`, `sunken`. Each slice is a `<rect>` (or a
   `<path>` for the corners) carrying `id="{prefix}-{slice}"`.
   - `plain`: face #DDDDDD with a 1px #000000 border on all four outer edges.
   - `raised`: 1px #000000 outer border, then 1px #FFFFFF along the inside top and left and 1px
     #999999 along the inside bottom and right, face #DDDDDD (the Platinum raised bevel).
   - `sunken`: 1px #000000 outer border, then 1px #999999 along the inside top and left and 1px
     #FFFFFF along the inside bottom and right, face #DDDDDD (the inverted bevel).
   Corners take the two adjacent edges' colours so the bevel turns the corner (e.g. raised `topleft`
   #FFFFFF, raised `bottomright` #999999). No `mask-*`, `shadow-*`, `class="ColorScheme-*"`, or
   `<script>`, and no fill outside the 12x12 canvas.
3. `test_desktoptheme.py` (edit; the file is created by the panel-background plan) — add a
   `TestFrame` class beside `TestPanelBackground`, using the same `xml.etree.ElementTree` approach:
   - `test_frame_svg_contract`: `ET.parse` the frame SVG, collect every `id`; for each prefix in
     `("plain", "raised", "sunken")` assert all nine `{prefix}-{slice}` ids and all four
     `{prefix}-hint-{side}-margin` ids are present; assert `hint-tile-center` is present; assert the
     file text contains `#DDDDDD`, `#FFFFFF`, `#999999`, `#000000`; assert no element tag ends in
     `script`.
   - `test_frame_installed`: run `make install DESTDIR=<tmp> XDG_DATA_HOME=/share`; assert
     `<tmp>/share/plasma/desktoptheme/org.macos8.desktop/widgets/frame.svg` exists and is
     byte-identical to the source file, and that a second run exits 0.
4. `README.md` (edit) — add the frame widget to the `tumwater:status` block and to the Installing
   section's desktop-theme sentence.

**Files touched.** New: `frame.svg` in the package's `widgets/` subdirectory. Edited:
`test_desktoptheme.py` (new `TestFrame`), `README.md`. No change to the color scheme, the
look-and-feel package, or the Makefile.

**Acceptance criteria.**
- `make check` exits 0 with `TestFrame` passing (its SVG-contract and install assertions).
- The frame SVG parses and contains the nine slice ids and four hint-margin ids for each of `plain`,
  `raised`, and `sunken`, plus `hint-tile-center`.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/desktoptheme/org.macos8.desktop/widgets/frame.svg` byte-identical to source,
  and a second `make install` still exits 0.
- Manual smoke test (needs a Plasma session): a `PlasmaComponents.Frame`/`GroupBox` and the kicker
  application-menu sidebar render a #DDDDDD face with a #000000 outline and #FFFFFF top/left +
  #999999 bottom/right bevels; every other widget still renders Breeze.

**Follow-up (not planned here).** `scrollbar`/`tooltip` and the menu widgets (`background`,
`listitem`); the frame establishes the multi-state nine-slice pattern those need. The button widget
is planned separately below.

### Mac OS 8.6 Platinum button widget for the desktop theme (done 2026-10-07)

**Planned 2026-10-07 by plan.** Independent of the frame plan above: it adds a second widget file to
the existing `org.macos8.desktop` desktop-theme package (created by the done panel-background
plan) and a `TestButton` class to the existing `tests/test_desktoptheme.py`; it does not touch the
frame SVG and does not require the frame plan to land first.

**Goal.** Ship `widgets/button.svg` in the `org.macos8.desktop` desktop theme so the Platinum push
button replaces Breeze for the most-used control: `PlasmaComponents.Button`, `ToolButton`,
`CheckBox`/`RadioButton` indicators, `DialogButtonBox`, and every applet button built on them.

**Grounding.**
- Consumers verified in the installed Plasma 6.3.6 QML under
  `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/`:
  `private/RaisedButtonBackground.qml` draws prefixes `"normal"`, `"pressed"`, and
  `["focus-background", "normal"]`; `private/ButtonHover.qml` draws `"hover"`;
  `private/ButtonFocus.qml` draws `flat ? ["toolbutton-focus", "focus"] : "focus"`;
  `private/FlatButtonBackground.qml` draws `["toolbutton-hover", "normal"]` and
  `["toolbutton-pressed", "pressed"]`; `private/ButtonShadow.qml` draws `"shadow"`;
  `CheckIndicator.qml` draws `"normal"` plus the separate `widgets/checkmarks` glyph.
- The default `button.svgz` id contract (parsed from
  `zcat /usr/share/plasma/desktoptheme/default/widgets/button.svgz`) is, per prefix,
  `{prefix}-{center,top,bottom,left,right,topleft,topright,bottomleft,bottomright}` plus
  `{prefix}-hint-{top,bottom,left,right}-margin` (the margin is the hint path's bounding-box height
  for top/bottom and its width for left/right), plus one `hint-tile-center`. Its `normal`, `pressed`,
  and `focus` hint margins are all 2px.
- The prefix fallbacks are QML arrays, so the file need not ship every prefix: a missing `hover`
  makes `ButtonHover` draw nothing, a missing `shadow` makes `ButtonShadow` draw nothing, and missing
  `toolbutton-*`/`focus-background` fall back to `normal`/`pressed`/`focus`. `mask-normal-*` is
  referenced by no PlasmaComponents consumer (`grep -rn mask` over that tree returns nothing).
- Palette from `theme/color-schemes/MacOS8.colors` (`[Colors:Button] BackgroundNormal=221,221,221`
  #DDDDDD, `ForegroundNormal=0,0,0` #000000) and the bevels the panel-background/frame plans use
  (#FFFFFF top/left, #999999 bottom/right). A histogram of the button strip of
  `macos8.6-screenshots/opendialog_macrumors86.jpg` (`convert ... -crop 364x50+0+156 ... histogram`)
  shows those four greys (#FFFFFF, ~#DEDEDE, ~#9D9D9D, #000000).
- This plan specifies the Platinum push button as a rounded rectangle with a 1px #000000 outline, a
  1px #FFFFFF inner top/left bevel, a 1px #999999 inner bottom/right bevel, and a #DDDDDD face; the
  pressed state inverts the bevel. The theme has no hover highlight and no drop shadow, so `hover`
  and `shadow` are intentionally omitted (see the fallback bullet above).

**Approach.**
1. New file `button.svg` in the package's `widgets/` subdirectory — a 12x12 canvas with a 3px border
   and 6px centre tile for `normal`/`pressed`, matching the panel-background and frame grid. Corners
   are quarter-rounds of radius 3 inside the 3x3 corner slices; the SVG's own alpha is the shape.
   - Slice geometry: `topleft`/`topright`/`bottomleft`/`bottomright` 3x3 at (0,0)/(9,0)/(0,9)/(9,9);
     `top`/`bottom` 6x3 at (3,0)/(3,9); `left`/`right` 3x6 at (0,3)/(9,3); `center` 6x6 at (3,3).
     Hint rects: `{prefix}-hint-top-margin` height 3, `-bottom-margin` height 3, `-left-margin`
     width 3, `-right-margin` width 3, and `hint-tile-center` 6x6; give them any opaque colour with
     the `style` attribute (KSvg reads the geometry, not the colour).
   - `normal`: 1px #000000 outer outline, 1px #FFFFFF inside the top and left edges, 1px #999999
     inside the bottom and right edges, #DDDDDD face. Corners carry the two adjacent bevel colours so
     the bevel turns the corner (e.g. `topleft` #FFFFFF, `bottomright` #999999).
   - `pressed`: same outline and face with the bevel inverted — 1px #999999 inside top/left and 1px
     #FFFFFF inside bottom/right.
2. Add a `focus` prefix on the same 12x12 canvas but with a 2px border and 8px centre, matching the
   default theme's 2px focus margins: a 1px #000000 rounded ring in the outer 1px of the border,
   transparent in the inner 1px and the centre. `ButtonFocus` expands its item by its margins, so this
   draws a ring 1-2px outside the button outline (the Platinum default-button ring). Ship its four
   `focus-hint-*-margin` ids and `hint-tile-center`.
   - No `hover-*`, `shadow-*`, `toolbutton-*`, `focus-background-*`, or `mask-*` ids; no `class=`
     attribute, no `<script>`, and no fill outside the 12x12 canvas. Because `hover` is absent, a
     hovered raised button is pixel-identical to an idle one, and a hovered flat/tool button shows the
     `normal` fallback.
3. `tests/test_desktoptheme.py` (edit) — add a `TestButton` class beside `TestPanelBackground`:
   - `BUTTON_PREFIXES = ("normal", "pressed", "focus")` and
     `BUTTON_MARGIN_HINTS = ("hint-top-margin", "hint-bottom-margin",
     "hint-left-margin", "hint-right-margin")`.
   - `test_button_slice_ids`: parse `widgets/button.svg`; for each prefix assert all nine
     `{prefix}-{slice}` ids and all four `{prefix}-hint-{side}-margin` ids are present; assert
     `hint-tile-center` is present.
   - `test_button_colours`: assert the parsed `fill` attribute set equals
     `{"#FFFFFF", "#DDDDDD", "#999999", "#000000"}` (parse attributes, not raw text; the hint
     rects use `style`, so they are excluded).
   - `test_no_script_elements`: no element tag ends in `script`.
   - Extend `TestInstall.test_make_install_copies_package_byte_for_byte`'s tuple with
     `os.path.join("widgets", "button.svg")`, so the install byte-identity check covers the new file.
4. `README.md` (edit) — add the button widget to the `tumwater:status` block's desktop-theme
   sentence.

**Files touched.** New: `widgets/button.svg` in the `org.macos8.desktop` package. Edited:
`tests/test_desktoptheme.py` (new `TestButton`, one tuple line), `README.md`. No Makefile,
color-scheme, or look-and-feel change: the Makefile's `cp -r` already copies new widget files.

**Acceptance criteria.**
- `make check` exits 0 with `TestButton` passing and the extended `TestInstall` byte-identity assertion.
- The button SVG parses and contains the nine slice ids and four hint-margin ids for `normal`,
  `pressed`, and `focus`, plus `hint-tile-center`; its parsed `fill` values are exactly the four
  Platinum greys.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/desktoptheme/org.macos8.desktop/widgets/button.svg` byte-identical to source.
- Manual smoke test (needs a Plasma session): `PlasmaComponents.Button` and `ToolButton` render a
  #DDDDDD rounded face with a #000000 outline and #FFFFFF top/left + #999999 bottom/right bevels;
  pressing inverts the bevel; a focused button shows the black outer ring; hovering changes nothing;
  `CheckBox`/`RadioButton` indicators get the Platinum face (their `widgets/checkmarks` glyph stays
  Breeze and is out of scope here).

**Follow-up (not planned here).** `widgets/checkmarks.svg` for the Platinum checkbox/radio glyphs,
plus `scrollbar`/`listitem`/`background`.

- Mac OS 8.6 desktop theme package with the Platinum panel background (planned 2026-10-07, done 2026-10-07; commit 126538c)
- Mac OS 8.6 look-and-feel global theme package (planned 2026-10-07, done 2026-10-07; commit 0c0cd8b)
- Mac OS 8.6 Platinum color scheme and project check harness (planned 2026-10-07, done 2026-10-07; commit 2e58776)
