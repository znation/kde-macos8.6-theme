# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Mac OS 8.6 Platinum checkmarks widget for the desktop theme

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
   - `<path id="checkbox" d="M 3.5,8.5 L 6.5,11.5 L 12.5,5.5" fill="none" stroke="#000000"
     stroke-width="2" stroke-linecap="square" stroke-linejoin="miter"/>` — the 2px black check
     in the top cell (the default theme's check shape, with `currentColor` resolved to `#000000`).
   - `<circle id="radiobutton" cx="8" cy="24" r="3" fill="#000000"/>` — the compatibility dot
     in the bottom cell.
   No `hint-size`/`hint-tile-center` (no consumer reads them), no `class="ColorScheme-*"`, no
   `currentColor`, no `<script>`, and no fill outside the 16x32 canvas.
2. `tests/test_desktoptheme.py` (edit):
   - Add `CHECKMARKS_SVG = os.path.join(PACKAGE, "widgets", "checkmarks.svg")` beside
     `RADIOBUTTON_SVG`.
   - Add `class TestCheckmarks` beside `TestRadioButton`:
     - `test_checkmarks_contract`: `ET.parse` the file; assert ids `checkbox` and `radiobutton` are
       present; assert the parsed `stroke` attributes are exactly `{"#000000"}`; assert the parsed
       `fill` attributes are exactly `{"none", "#000000"}`; assert no element tag ends in `script`.
     - `test_checkmarks_geometry`: assert the `checkbox` element's tag is `path`, its `d` is exactly
       `"M 3.5,8.5 L 6.5,11.5 L 12.5,5.5"`, and its `stroke-width` is `"2"`; assert the
       `radiobutton` element's tag is `circle` with `r == 3` and `fill == "#000000"`.
   - Add `os.path.join("widgets", "checkmarks.svg")` to the tuple in
     `TestInstall.test_make_install_copies_package_byte_for_byte`.
3. `README.md` (edit): extend the `tumwater:status` sentence that enumerates the desktop theme's
   widgets with "and whose `widgets/checkmarks.svg` provides the Platinum checkbox checkmark (a 2px
   black check drawn over the face when checked)".

**Files touched.** New: `checkmarks.svg` in the package's `widgets/` subdirectory. Edited:
`tests/test_desktoptheme.py` (`TestCheckmarks`, `TestInstall` tuple), `README.md`. No change to the
color scheme, the look-and-feel package, the Makefile, or the other widgets.

**Acceptance criteria.**
- `make check` exits 0 with `TestCheckmarks` passing.
- The checkmarks SVG parses and contains `checkbox` and `radiobutton`; `checkbox` is a `path` with
  the pinned `d`, `stroke-width="2"`, and `stroke="#000000"`; `radiobutton` is a `circle` with
  `r=3` and `fill="#000000"`.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/desktoptheme/org.macos8.desktop/widgets/checkmarks.svg` byte-identical to
  source (via the extended `TestInstall` tuple).
- Manual smoke test (needs a Plasma session): a checked `PlasmaComponents.CheckBox` draws a black
  2px check over the Platinum face with no Breeze blue tint, unchecking hides it, and every other
  widget is unchanged.

**Follow-up (not planned here).** `widgets/actionbutton.svg` for `RoundButton`/`Dial`/`RoundShadow`,
and the checkbox-face mismatch noted above (a Plasma 6.3 `CheckIndicator.qml` constraint, not a
missing SVG), then `scrollbar`, `listitem`, and `background`.

## Done

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
   255,255,204`, `Window ForegroundNormal == 0,0,0`). A `TestInstall` case runs
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
(see the Fixed BUGS.md entry). The tooltip token (`255,255,204`) still has no reference screenshot
and remains pinned only by the test.

**Follow-ups (not planned here).** Wrap the scheme in a `look-and-feel` global-theme package,
then build the Plasma desktop-theme widget SVGs and the Platinum window decoration.

