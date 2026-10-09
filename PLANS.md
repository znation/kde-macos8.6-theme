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
`splash_macbase.gif`). No shipped or planned artifact covers window decoration or boot/splash,
and there is no icon, cursor, or Qt widget-style theme either. The widget sequence should not be
treated as the whole of the prompt until these surfaces are planned or explicitly ruled out.

### Mac OS 8.6 Platinum startup splash (`contents/splash/`) for the global theme (planned 2026-10-08)

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
- progress track `(221,221,221)` = `#DDDDDD` at `(145,100)`, fill `(173,173,173)` = `#ADADAD` at
  `(120,100)`; wordmark black.
- reference grid rectangles (240x180 pixels): the panel is the bounding box of every pixel that
  is not the field colour, `x=70..169, y=31..108`; the logo is the bounding box of the blue
  pixels, `x=107..132, y=45..65` (26x21); the progress fill is the bounding box of the
  `#ADADAD` pixels, `x=106..138, y=95..102`; the progress track is the `#DDDDDD` band
  `y=89..104`; the wordmark sits in the band `y=71..85`.
The 240x180 frame is a 4:3 thumbnail of the 640x480 Mac OS 8.6 screen; the plan keeps the
reference's own grid and scales it by whole pixels rather than re-deriving 640x480 values.

**Approach.**
- Add a `Splash.qml` under the look-and-feel package's `contents/splash/`. It is a full-screen
  `Rectangle` with `color: "#63639C"` and
  `readonly property int unit: Math.max(1, Math.floor(Math.min(width / 240, height / 180)))`,
  so the reference grid scales by whole pixels and keeps its proportions on any screen. A centred
  `Item` is authored entirely in the 240x180 grid times `unit`:
  - a panel `Rectangle` at the reference's panel bounding box, `#FFFFFF` face, `#DDDDDD` outer
    border and `#BFBFBF` inner rule;
  - an `Image` of `images/macos-logo.svg` at the logo bounding box;
  - a `Text` "Mac OS" in black on the wordmark band;
  - a progress `Rectangle` track across the panel's lower band (`#DDDDDD`) whose `#ADADAD` fill
    width binds to the KDE splash `stage` (0..6): `width: track.width * Math.min(1, stage / 6)`,
    so the reference's roughly three-quarter fill is `stage` 5 of 6.
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
  the `#63639C` literal `Splash.qml` uses; `test_progress_colours_match_reference` does the same
  for the track `#DDDDDD` at `(145,100)` and the fill `#ADADAD` at `(120,100)`.
- `TestSplashQml.test_grid_geometry` parses the panel/logo/progress grid literals out of
  `Splash.qml` and asserts they equal rectangles the test re-derives from
  `macos8.6-screenshots/boot2_betawiki.png` by colour scan (panel = bounding box of non-field
  pixels, logo = bounding box of blue pixels, fill = bounding box of `#ADADAD` pixels);
  `test_uses_the_logo_image` asserts the `Image` source is `images/macos-logo.svg`.
- `TestLogo.test_logo_svg` parses `images/macos-logo.svg`, asserts `viewBox` is 26x21, that
  `assert_no_script_elements` and `assert_unique_ids` pass, and that the fill set is exactly
  `{#4C65CB, #7286D6}`.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/look-and-feel/org.macos8.desktop/contents/splash/Splash.qml` and its logo
  byte-identical to source, and `make uninstall` removes the package.
- Manual smoke test (needs a Plasma session, outside `make check`): applying the global theme
  selects the splash (`[KSplash] Theme=org.macos8.desktop`), and the startup screen shows the
  `#63639C` field, the panel and a progress bar that advances with `stage`.

## Done

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
   - `test_hint_ids_present`: every `HINT_IDS` name is present.
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

### Mac OS 8.6 desktop theme package with the Platinum panel background (done 2026-10-07)

**Planned 2026-10-07 by plan.**

**Goal.** Ship the third installable artifact: a Plasma 6 desktop theme, `org.macos8.desktop`
(`KPackageStructure: "Plasma/Theme"`), whose `widgets/panel-background.svg` renders the Mac OS 8.6
Platinum menu bar, and wire it into the existing global theme so applying
`org.macos8.desktop` also selects it. This is the first widget-theme step toward pixel-perfect UI.

**Grounding.**
- Plasma desktop themes live at `$XDG_DATA_DIRS/plasma/desktoptheme/<KPlugin.Id>/`: a
  `metadata.json` plus `widgets/*.svg[z]`, optional `colors`, `plasmarc`, `opaque/`, `dialogs/`.
  The system references are `/usr/share/plasma/desktoptheme/default/` (43 `widgets/*.svgz`) and
  `/usr/share/plasma/desktoptheme/breeze-light/`, which ships **no `widgets/` at all** yet is an
  enabled, selectable theme — so Plasma renders missing widgets from the `default` theme and a
  partial theme is supported. `libPlasma.so.6` contains both the `.svgz` and `.svg` lookup
  strings, so an uncompressed, diffable `.svg` works. This plan therefore ships only
  `widgets/panel-background.svg`; every other widget keeps the Breeze default.
- The global theme selects a desktop theme through `contents/defaults`
  `[plasmarc][Theme] name=<id>` (Breeze uses `name=default`). Verified headless with a temp
  `XDG_DATA_HOME`: `plasma-apply-desktoptheme --list-themes` lists the package and
  `plasma-apply-desktoptheme org.macos8.desktop` exits 0 and writes `$XDG_CONFIG_HOME/plasmarc`
  `[Theme] name=org.macos8.desktop`; no session is needed.
- Palette sampled from `macos8.6-screenshots/desktop_betawiki.png` (top 20 rows at x=500) and
  `desktop_archiveorg8.6hd.png`: body `#DDDDDD`, top/left highlight `#FFFFFF`, bottom/right shadow
  `#999999`, bottom rule `#000000`. The body matches `theme/color-schemes/MacOS8.colors`
  (`[Colors:Button] BackgroundNormal=221,221,221`).
- Plasma's nine-slice contract: the SVG carries one element each with `id` `center`, `top`,
  `bottom`, `left`, `right`, `topleft`, `topright`, `bottomleft`, `bottomright`, plus magic-coloured
  hint rects `hint-tile-center`, `hint-{top,bottom,left,right}-margin` and
  `hint-{top,bottom,left,right}-inset`. A hint's value is the rect's height for top/bottom and its
  width for left/right (`zcat`
  `/usr/share/plasma/desktoptheme/default/widgets/panel-background.svgz` to see the encoding).
  `mask-*`/`shadow-*` only serve rounded corners and drop shadows; a square opaque bar omits them.

**Approach.**
1. A new package directory named `org.macos8.desktop` under `theme/desktop-themes/` (a new
   sibling of `look-and-feel`). Inside it, `metadata.json` (new) — `KPackageStructure`
   `"Plasma/Theme"`, `X-Plasma-API` `"5.0"` (the value `default` uses), and `KPlugin` with `Id`
   `org.macos8.desktop`, `Name` `Mac OS 8.6`, `Description`, `Version` `0.1.0`, `License`
   `GPL-2.0-or-later`, empty `Category`, one `Authors` entry.
2. In that package's `widgets/` subdirectory, `panel-background.svg` (new) — a tight 12x12
   canvas (no shadow space), 2px border, 8px centre tile: corners 2x2 at (0,0)/(10,0)/(0,10)/(10,10);
   `top` 8x2 at (2,0), `bottom` 8x2 at (2,10), `left` 2x8 at (0,2), `right` 2x8 at (10,2), `center`
   8x8 at (2,2). Fills: body `#DDDDDD`; outer 1px top/left `#FFFFFF`; outer 1px bottom/right
   `#999999`; an extra 1px `#000000` rule along the bottom outer edge; corners take the adjacent
   edge colour. Hint rects: `hint-tile-center` 8x8, each `hint-*-margin` 2x2, each `hint-*-inset`
   zero-height/width at its edge. Author the Platinum shapes; use the decompressed default SVG only
   as the element-ID/transform layout reference, not as artwork. No `class="ColorScheme-*"` hooks
   (the palette is fixed), no `mask-*`, `shadow-*`, `thick-*`, or `<script>`.
3. The look-and-feel package's `contents/defaults` (edit) — add a
   `[plasmarc][Theme]` section with `name=org.macos8.desktop` after the existing
   `[kdeglobals][General] ColorScheme=MacOS8`.
4. A `test_desktoptheme.py` (new) under `tests/` — stdlib `unittest`, `json`, `configparser`,
   `xml.etree.ElementTree`, `shutil`, `subprocess`, `tempfile`:
   - `TestMetadata`: `KPackageStructure == "Plasma/Theme"`, `KPlugin.Id == "org.macos8.desktop"`,
     `Name`, non-empty `Version`, `X-Plasma-API == "5.0"`.
   - `TestPanelBackground`: `ET.parse` the SVG, collect every `id`, assert the nine slice ids and
     all nine hint ids are present, assert the text contains `#FFFFFF`, `#DDDDDD`, `#999999`,
     `#000000`, and assert no element tag ends in `script`.
   - `TestDefaultsWiring`: parse the LNF `contents/defaults` (same `configparser` trick as
     `tests/test_lookandfeel.py`) and assert `[plasmarc][Theme] name` equals the desktop theme's
     `KPlugin.Id`.
   - `TestInstall`: run `make install DESTDIR=<tmp> XDG_DATA_HOME=/share`; assert
     `<tmp>/share/plasma/desktoptheme/org.macos8.desktop/{metadata.json,widgets/panel-background.svg}`
     are byte-identical to source and a second run exits 0.
   - `TestApplyDesktopTheme` (`@unittest.skipUnless(shutil.which("plasma-apply-desktoptheme"), ...)`):
     install into a temp prefix, run `plasma-apply-desktoptheme --list-themes` with
     `XDG_DATA_HOME=<tmp>/share` and a fresh `XDG_CONFIG_HOME`, assert the output names
     `org.macos8.desktop`; run `plasma-apply-desktoptheme org.macos8.desktop`, assert exit 0 and
     `<tmp>/config/plasmarc` contains `[Theme] name=org.macos8.desktop`.
   - `TestPackageValid` (`@unittest.skipUnless(shutil.which("kpackagetool6"), ...)`):
     `kpackagetool6 -t Plasma/Theme -p <fresh tmp> -i` on the new package directory
     exits 0 and leaves `<fresh tmp>/org.macos8.desktop/metadata.json`.
5. `tests/test_lookandfeel.py` (edit) — `TestDefaults.test_only_the_color_scheme_key_is_set` now
   fails because the defaults carry a second section; rewrite it to assert both sections
   (`kdeglobals][General` with `ColorScheme`, `plasmarc][Theme` with `name`) and leave
   `test_color_scheme_matches_the_scheme_file` unchanged.
6. `Makefile` (edit) — add `DTHEME_ID := org.macos8.desktop`,
   `DTHEME_PACKAGE := theme/desktop-themes/$(DTHEME_ID)`,
   `DTHEME_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/plasma/desktoptheme`; extend `install` with
   `install -d`, `rm -rf $(DTHEME_INSTALL_DIR)/$(DTHEME_ID)`, `cp -r` (the same replace-not-merge
   rule as the look-and-feel package).
7. `README.md` (edit) — extend the `tumwater:status` block and the Installing section: the panel
   background now ships, `plasma-apply-desktoptheme org.macos8.desktop` selects it, and the global
   theme applies it via `[plasmarc][Theme]`.

**Files touched.** New: `metadata.json` and `panel-background.svg` (in the package's `widgets/`) in
the new `org.macos8.desktop` package under `theme/desktop-themes/`, plus `test_desktoptheme.py`
under `tests/`. Edited: the look-and-feel package's `contents/defaults`,
`tests/test_lookandfeel.py`, `Makefile`, `README.md`. No change to the color scheme.

**Acceptance criteria.**
- `make check` exits 0 with the new metadata, SVG-contract, defaults-wiring, install,
  `plasma-apply-desktoptheme`, and `kpackagetool6` tests passing (the last two skipped only when
  the tool is absent).
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/desktoptheme/org.macos8.desktop/metadata.json` and
  `widgets/panel-background.svg` byte-identical to source, and a second `make install` still exits
  0.
- `plasma-apply-desktoptheme --list-themes` with `XDG_DATA_HOME` pointed at the installed tree
  lists `org.macos8.desktop`; applying it exits 0 and writes
  `plasmarc [Theme] name=org.macos8.desktop`.
- Manual smoke test (needs a Plasma session): a top panel renders `#DDDDDD` with a white top/left
  highlight and a `#999999`+black bottom edge, and every other widget still renders Breeze.

**Follow-ups (not planned here).** Further widget families (button, scrollbar, tooltip), the
Platinum window decoration, an 8.6 splash, and the automated render/capture step (BUGS.md
`## Open`) — the panel background gives the render harness its first real surface.
### Mac OS 8.6 look-and-feel global theme package (done 2026-10-07)

**Planned 2026-10-07 by plan.**

**Goal.** Ship the second installable artifact: a Plasma 6 `Plasma/LookAndFeel` global theme,
`org.macos8.desktop`, that applies the existing Platinum color scheme as one selectable global
theme and gives the later desktop-theme, window-decoration, and splash plans a package to plug
into.

**Grounding.**
- A `Plasma/LookAndFeel` package is `metadata.json` (`KPackageStructure`, `KPlugin.Id`) plus
  `contents/defaults`; the reference is `/usr/share/plasma/look-and-feel/org.kde.breeze.desktop/`.
  Packages live under `$XDG_DATA_DIRS/plasma/look-and-feel/<KPlugin.Id>/`, and `lookandfeeltool -l`
  lists them (verified with a temp `XDG_DATA_HOME`).
- `contents/defaults` is ini merged into the user's config. Breeze sets every surface
  (`widgetStyle`, `ColorScheme`, `Theme`, cursor, decoration, splash); this project only has a
  color scheme, so the defaults set only `[kdeglobals][General] ColorScheme` and leave the rest at
  the user's current values instead of silently resetting them to Breeze.
- The value must be `MacOS8`, the CLI-visible id: KDE's scheme resolver turns the config value
  into `<value>.colors`, and the file is `theme/color-schemes/MacOS8.colors` (renamed from the
  dotted `MacOS8.6.colors`; see the Fixed BUGS.md entry). Verified by running
  `plasma-apply-colorscheme` with no argument against a temp `XDG_CONFIG_HOME`:
  `ColorScheme=MacOS8` resolves, `ColorScheme=MacOS8.6` prints `Could not find color scheme
  "MacOS8.6" falling back to BreezeLight`.

**Approach.**
1. The package metadata manifest, `metadata.json` (new) — `KPackageStructure`
   `"Plasma/LookAndFeel"`; `KPlugin` with `Id` `org.macos8.desktop`, `Name` `Mac OS 8.6`,
   `Description`, `Version` `0.1.0`, `License` `GPL-2.0-or-later`, empty `Category`, and one
   `Authors` entry; `X-Plasma-APIVersion` `"2"`; `Keywords`
   `"Desktop;Workspace;Appearance;Look and Feel;"`.
2. `theme/look-and-feel/org.macos8.desktop/contents/defaults` (new) — exactly two lines,
   `[kdeglobals][General]` and `ColorScheme=MacOS8`. No other sections or keys.
3. A new `test_lookandfeel.py` module under `tests/` — stdlib `unittest`, `json`, `configparser`, `shutil`,
   `subprocess`, `tempfile`:
   - `TestMetadata`: `json.load` the metadata and assert `KPackageStructure`,
     `KPlugin.Id == "org.macos8.desktop"`, `KPlugin.Name == "Mac OS 8.6"`, `KPlugin.Version`,
     `X-Plasma-APIVersion == "2"`, and a non-empty `Keywords`.
   - `TestDefaults`: parse `contents/defaults` with
     `configparser.ConfigParser(interpolation=None)` and `optionxform = str` (the section key is
     `kdeglobals][General`); assert that is the only section and `ColorScheme` its only option;
     assert the value equals `theme/color-schemes/MacOS8.colors`'s `[General] ColorScheme` and
     that `theme/color-schemes/<value>.colors` exists (the cross-artifact invariant, which stays
     true if the scheme is later renamed).
   - `TestInstall`: run `make install DESTDIR=<tmp> XDG_DATA_HOME=/share`; assert
     `<tmp>/share/plasma/look-and-feel/org.macos8.desktop/metadata.json` and `contents/defaults`
     exist and are byte-identical to source, and that a second run exits 0.
   - `TestPackageValid` (`@unittest.skipUnless(shutil.which("kpackagetool6"), ...)`): run
     `kpackagetool6 -t Plasma/LookAndFeel -p <fresh tmp> -i theme/look-and-feel/$LNF_ID`
     and assert exit 0 with `<fresh tmp>/org.macos8.desktop/metadata.json` present.
4. `Makefile` — add `LNF_ID := org.macos8.desktop` and
   `LNF_PACKAGE := theme/look-and-feel/$LNF_ID`, and
   `LNF_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/plasma/look-and-feel`; extend `install` to
   `install -d $(LNF_INSTALL_DIR)` then `cp -r $(LNF_PACKAGE) $(LNF_INSTALL_DIR)/`. Plain copy, not
   `kpackagetool6 -i`, because `-i` exits 4 when the target already exists and `-u` does not honour
   `--packageroot` (both verified); the copy is idempotent.
5. `README.md` — update the `tumwater:status` block and the Installing section to describe the
   global theme and `lookandfeeltool -a org.macos8.desktop`.

**Files touched.** New files under `theme/look-and-feel`: `metadata.json` and `contents/defaults`;
a new `test_lookandfeel.py` under `tests/`; `Makefile` and `README.md` edited. No change to the
color scheme itself.

**Acceptance criteria.**
- `make check` exits 0; the metadata, defaults/cross-artifact, install, and (on this host)
  kpackagetool6-validity tests pass.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/look-and-feel/org.macos8.desktop/metadata.json` and `contents/defaults`
  byte-identical to source, and a second `make install` still exits 0.
- Manual smoke test (needs a Plasma session, so outside `make check`): with the package under
  `~/.local/share/plasma/look-and-feel/`, `lookandfeeltool -l` lists `org.macos8.desktop`, and
  `lookandfeeltool -a org.macos8.desktop` exits 0 and leaves `kdeglobals [General]
  ColorScheme=MacOS8`, which `plasma-apply-colorscheme` resolves without the "Could not find"
  warning.

**Follow-ups (not planned here).** Desktop-theme widget SVGs, the Platinum window decoration, and
an 8.6 splash (`contents/splash/`) — each adds its own key to this package's `contents/defaults`.

**Implementation note (2026-10-07).** Landed as planned: `metadata.json` (top-level
`KPackageStructure`, `Keywords`, `X-Plasma-APIVersion`; `KPlugin` with `Id`, `Name`,
`Description`, `Version`, `License`, empty `Category`, one author), the two-line
`contents/defaults`, `tests/test_lookandfeel.py`, and the `Makefile` install step. Verified beyond
`make check`: `kpackagetool6 -t Plasma/LookAndFeel -p <tmp> -i` exits 0; with the package
installed under a temp `XDG_DATA_HOME`, `lookandfeeltool -l` lists `org.macos8.desktop` and
`lookandfeeltool -a org.macos8.desktop` exits 0. Headless, the apply wrote the scheme's colour
sections into `kdeglobals` and `[General] ColorScheme=MacOS8` into `kdedefaults/kdeglobals` (KDE's
defaults layer), not the main `kdeglobals`; the in-session restart check still needs a Plasma
session.

### Mac OS 8.6 Platinum color scheme and project check harness (done 2026-10-07)
**Planned 2026-10-07 by plan.**

**Goal.** Ship the project's first artifact — a Plasma 6 color scheme encoding the Mac OS 8.6
"Platinum" palette sampled from the reference screenshots — together with the project's first
`make check` harness that validates the scheme and exercises its install path.

**Evidence.** Palette anchors were sampled with ImageMagick from the retail reference set and are
recorded as assertions in the test: `desktop_archiveorg8.6hd.png` (menu bar and window face
`221,221,221`; view `255,255,255`; chrome `0,0,0`; desktop `100,98,160`), `desktop_fandom.png`
(`192,192,192`, `136,136,136`, `85,85,85`), `opendialog_macrumors86.jpg` (list selection
`206,206,255`).

**Palette tokens (RGB).** `platinum`=221,221,221 · `white`=255,255,255 · `black`=0,0,0 ·
`alternate`=238,238,238 · `shadow`=136,136,136 · `silver`=192,192,192 · `selection`=206,206,255 ·
`tooltip`=255,255,204. KDE requires semantic roles with no Mac OS 8.6 counterpart; use
`link`=0,0,238 · `negative`=204,0,0 · `positive`=0,128,0 · `neutral`=204,102,0 ·
`visited`=85,26,139.

**Approach.**

1. `theme/color-schemes/MacOS8.colors` (new) — an ini color scheme using the same key set as
   `/usr/share/color-schemes/BreezeLight.colors`, with sections `[ColorEffects:Disabled]`,
   `[ColorEffects:Inactive]`, `[Colors:Button]`, `[Colors:Complementary]`, `[Colors:Header]`,
   `[Colors:Header][Inactive]`, `[Colors:Selection]`, `[Colors:Tooltip]`, `[Colors:View]`,
   `[Colors:Window]`, `[General]`, `[KDE]`, `[WM]`. Every `[Colors:*]` section carries
   `BackgroundAlternate`, `BackgroundNormal`, `DecorationFocus`, `DecorationHover`,
   `ForegroundActive`, `ForegroundInactive`, `ForegroundLink`, `ForegroundNegative`,
   `ForegroundNeutral`, `ForegroundNormal`, `ForegroundPositive`, `ForegroundVisited`.
   Mapping: Window/Button/Header/Header][Inactive/Complementary get
   `BackgroundNormal=BackgroundAlternate=platinum`, `ForegroundNormal=ForegroundActive=black`,
   `ForegroundInactive=shadow`, `DecorationFocus=DecorationHover=black`; View gets
   `BackgroundNormal=white`, `BackgroundAlternate=alternate`, the rest as Window; Selection gets
   `BackgroundNormal=BackgroundAlternate=selection` and the Window foregrounds; Tooltip gets
   `BackgroundNormal=tooltip`, `ForegroundNormal=black`, the rest as Window; semantic roles map to
   the tokens above. `[WM]` gets `activeBackground=activeBlend=platinum`,
   `activeForeground=black`, `inactiveBackground=inactiveBlend=platinum`,
   `inactiveForeground=shadow`. `[General]` gets `ColorScheme=MacOS8`, `Name=Mac OS 8.6`,
   `shadeSortColumn=true`; `[KDE]` gets `contrast=4`; the `ColorEffects` sections copy
   BreezeLight with `Color=136,136,136` (Disabled) and `Color=136,136,136` (Inactive).
2. `tests/test_colorscheme.py` (new) — stdlib `unittest` + `configparser` (`interpolation=None`).
   Asserts the file parses; every section and key above exists; every `[Colors:*]` value matches
   `^\d{1,3},\d{1,3},\d{1,3}$` with components 0–255; and the sampled anchors hold
   (`Window`/`Button`/`Header` `BackgroundNormal == 221,221,221`, `View BackgroundNormal ==
   255,255,255`, `Selection BackgroundNormal == 206,206,255`, `Tooltip BackgroundNormal ==
   255,255,204`, `Window ForegroundNormal == 0,0,0`). A `tests/test_colorscheme_install.py`
   `TestInstall` case runs
   `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` in a subprocess and asserts
   `<tmp>/share/color-schemes/MacOS8.colors` is byte-identical to the source.
3. `Makefile` (new) — `check` runs `$(PYTHON) -m unittest discover -s tests -v`; `install` runs
   `install -Dm644 theme/color-schemes/MacOS8.colors
   $(DESTDIR)$(XDG_DATA_HOME)/color-schemes/MacOS8.colors`, with
   `XDG_DATA_HOME ?= $(HOME)/.local/share`.

**Files touched.** `theme/color-schemes/MacOS8.colors`, `tests/test_colorscheme.py`, `Makefile`
— all new; no existing file changes.

**Acceptance criteria.**
- `make check` exits 0 and the run reports the color-scheme structure, anchor, and install tests
  passing.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/color-schemes/MacOS8.colors` byte-identical to the source file.
- Manual smoke test (needs a Plasma session, so outside `make check`): with the file copied to
  `~/.local/share/color-schemes/`, `plasma-apply-colorscheme --list-schemes` lists `MacOS8`, and
  `plasma-apply-colorscheme MacOS8` exits 0 with window/button faces `#DDDDDD` and view
  backgrounds `#FFFFFF`.

**Implementation note (2026-10-07).** `plasma-apply-colorscheme` derives a scheme's ID from the
part of its filename before the first dot, so the originally planned `MacOS8.6.colors` was listed
and selectable as `MacOS8`, not `MacOS8.6` (verified by running the tool against a temp
`XDG_DATA_HOME` holding copies named `MacOS8.6.colors`, `MacOS86.colors`, and `Platinum.colors`:
it printed `MacOS8`, `MacOS86`, and `Platinum`). That mismatch made the applied id fail to
resolve on restart, so the scheme was later renamed to `MacOS8.colors` with `ColorScheme=MacOS8`
(see the Fixed BUGS.md entry); `Name` still reads "Mac OS 8.6".

**Implementation note (2026-10-08).** The selection token was planned as `206,206,255`, sampled
from the lossy `opendialog_macrumors86.jpg`; grounding the anchor in the lossless retail
`firstboot_betawiki.png` showed the selection fill is `204,204,255`, so the scheme was corrected
(see the Fixed BUGS.md entry). `[Colors:Tooltip] BackgroundNormal` is the one palette token with
no Mac OS 8.6 reference in the set: it is a KDE-required semantic role whose value (`255,255,204`)
comes from the classic Platinum palette, not a sampled anchor, and
`theme/color-schemes/MacOS8.colors` and `tests/test_colorscheme.py` say so explicitly (decision
2026-10-08, QUESTIONS.md).

**Follow-ups (not planned here).** Wrap the scheme in a `look-and-feel` global-theme package,
then build the Plasma desktop-theme widget SVGs and the Platinum window decoration.

