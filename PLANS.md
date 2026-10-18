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

### Mac OS 8.6 Platinum applet-popup heading (`widgets/plasmoidheading.svg`) for the desktop theme (planned 2026-10-17 by the plan role; done 2026-10-17)

**Planned 2026-10-17 by plan.** Independent of every other entry: it adds one widget file to the
existing `org.macos8.desktop` desktop-theme package and one new test module, touches no shipped
SVG, and needs no other plan to land first.

**Goal.** Ship `widgets/plasmoidheading.svg` so the header and footer bands of applet popups draw
the Platinum etched rule (the `#888888`-over-`#FFFFFF` pair `widgets/line.svg` already ships)
between the band and the popup body. Today those bands are invisible:
`/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/extras/PlasmoidHeading.qml` draws its
`KSvg.FrameSvgItem` (`imagePath: "widgets/plasmoidheading"`, `prefix: "header"` or `"footer"`)
only while `fromCurrentImageSet === backgroundSvg.fromCurrentImageSet`, and the backgroundSvg is
`dialogs/background`, which our package ships. So Plasma hides the Breeze fallback, and the
heading of kickoff, the system tray, notifications, the digital-clock calendar, network, volume,
bluetooth, clipboard and device-notifier popups runs into the body with no divider.
`grep -rni plasmoidheading` over the repo (outside `.git`) finds nothing, and no PLANS.md entry
covers it.

**Consumer contract (verified in installed Plasma 6 QML and Breeze).** One FrameSvg with two
prefixes, `header` and `footer`, each a full nine-slice (`<prefix>-topleft` … `<prefix>-center`)
plus `<prefix>-hint-{top,bottom,left,right}-margin`. In a popup, `BackgroundMetrics.getMargin`
returns the window's negative padding, so the band's insets pull it out over the
`dialogs/background.svg` 3px border on its top/left/right (header) or bottom/left/right (footer).
`enabledBorders` always includes top and bottom, and left/right only when the band touches the
window edge. Breeze (`/usr/share/plasma/desktoptheme/default/widgets/plasmoidheading.svgz`)
paints a background fill plus a 1px `ColorScheme-Text` line in the last row of `header-bottom`
(and the first row of `footer-top`), with 6px borders.

**Design decisions (settled; do not revisit).**
- Every border is 3px, the same as `dialogs/background.svg`, so where the band overlays the
  dialog border it lines up with it exactly.
- Every slice paints nothing (a transparent placeholder) except the rule rows. So the band shows
  the dialog's `#DDDDDD` face and the dialog's own outline/bevel shows through the band's
  top/left/right (header) or bottom/left/right (footer) edges. The corners are placeholders too,
  so the rule stops at the inside of the dialog's bevel instead of crossing it.
- `header-bottom` (6x3): row 0 placeholder, row 1 `#888888`, row 2 `#FFFFFF`, which puts the rule
  on the band's bottom edge, dark first. `footer-top` (6x3): row 0 `#888888`, row 1 `#FFFFFF`,
  row 2 placeholder, which puts the rule on the band's top edge. The same dark-then-light order
  as `line.svg`'s `horizontal-line`.
- Colours and provenance: `#888888`/`#FFFFFF` are the etched group-box rule sampled from
  `macos8.6-screenshots/systemprofiler_betawiki.png` at `(260,153)`/`(260,154)`, the
  provenance `line.svg` and `tests/test_desktoptheme_line.py::TestLineReference` already pin.
  This file does not re-sample them: its test ties the rule colours to `line.svg`'s
  `horizontal-line` instead. Using the etched rule as a popup header divider is a KDE-required
  surface that the reference set does not show (no 8.6 screenshot has a Plasma-style popup
  heading). Record that in the SVG comment as the nearest Platinum equivalent: the rule that
  divides a Platinum window's body.

**Approach.**
1. New `theme/desktop-themes/org.macos8.desktop/widgets/plasmoidheading.svg`, modelled on
   `widgets/listitem.svg` (a 12x12 canvas where two prefixes share the same tile positions):
   - root `<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12">`
     and a comment naming the consumer (`PlasmaExtras.PlasmoidHeading`), the visibility rule
     above, the design decisions and the provenance;
   - `hint-tile-center` at `(3,3,6,6)` and `header-hint-*-margin` / `footer-hint-*-margin` with
     `listitem.svg`'s geometry (the `nine_slice_margins` layout, border 3, size 6), all
     `style="fill:#…"` like `listitem.svg`;
   - for each prefix, nine `<g id>` slices translated to the standard 3/6/3 tile origins. Each
     holds one full-tile placeholder rect, `style="fill:#FFFFFF" fill-opacity="0.01"` with no
     `fill` attribute. `header-bottom` adds `<rect y="1" width="6" height="1" fill="#888888"/>`
     and `<rect y="2" width="6" height="1" fill="#FFFFFF"/>` after it, and `footer-top` adds the
     same rects at `y="0"` and `y="1"`. The placeholder comes first, so `render_slices` reads its
     rows as `None` and its bounding box gives each tile its full 3px extent. No `class=`,
     `<style>`, `<script>`, rect `transform` or other id.
2. `tests/desktoptheme_paths.py`: add
   `PLASMOIDHEADING_SVG = os.path.join(PACKAGE, "widgets", "plasmoidheading.svg")` beside
   `LINE_SVG`.
3. `tests/test_desktoptheme.py`: import it; add `("plasmoidheading.svg", PLASMOIDHEADING_SVG,
   12, 12)` to `SVG_CANVASES` (and add "plasmoid heading" to the 12x12 group in the comment above
   it); add `os.path.join("widgets", "plasmoidheading.svg")` to `TestInstall.INSTALLED_FILES`.
4. New `tests/test_desktoptheme_plasmoidheading.py`: `TestPlasmoidHeading(NineSliceCase,
   unittest.TestCase)` with `SVG_PATH = PLASMOIDHEADING_SVG` and `PREFIXES = ("header",
   "footer")`, plus module constants `DARK = "#888888"`, `LIGHT = "#FFFFFF"` and
   `SIZES = nine_slice_tile_sizes(12, 12, 3, 3, 3, 3)` (exported by `svg_assertions`; its keys
   are the nine slice names). Tests are listed in the
   acceptance criteria.
5. `README.md`: in the Installing section's desktop-theme inventory, name
   `widgets/plasmoidheading.svg` (the transparent header/footer band of applet popups, divided
   from the body by the same etched `#888888`/`#FFFFFF` rule). `tests/test_readme_theme_files.py`
   fails until README names it.

**Files touched.** New: `widgets/plasmoidheading.svg`,
`tests/test_desktoptheme_plasmoidheading.py`. Edited: `tests/desktoptheme_paths.py`,
`tests/test_desktoptheme.py`, `README.md`, `PLANS.md` (move this entry to Done). The Makefile does
not change: `make install` already copies the whole widgets directory.

**Acceptance criteria.**
- `make check` exits 0, including the new module, `tests/test_desktoptheme.py` (canvas pin,
  registered-SVG check, `TestInstall`) and `tests/test_readme_theme_files.py`.
- The inherited `NineSliceCase` checks pass for both prefixes: slice ids present, tiles placed by
  margins, tiles within margins, no script.
- `test_hint_geometry`: `assert_hint_geometry(self, self.tree, ("header", "footer"), 3, 6)`.
- `test_rule_rows`: `render_slices(tree)["header-bottom"] == pixel_map((None,)*6 + (DARK,)*6 +
  (LIGHT,)*6, 6, 3)` and `render_slices(tree)["footer-top"] == pixel_map((DARK,)*6 +
  (LIGHT,)*6 + (None,)*6, 6, 3)`.
- `test_other_slices_paint_nothing`: every other one of the 18 slices (the eight `header-*` and
  eight `footer-*` names besides those two) equals `pixel_map((None,) * (w*h), w, h)` for its
  `(w, h)` in `SIZES`.
- `test_colours`: `attribute_values(tree, "fill") == {DARK, LIGHT}` and
  `attribute_values(tree, "fill-opacity") == {"0.01"}`.
- `test_rule_matches_line_svg`: parse `LINE_SVG` and require
  `render_slices(line_tree)["horizontal-line"] == {(0, 0): DARK, (0, 1): LIGHT}`. The heading's
  rule then cannot drift from the separator whose colours `TestLineReference` pins to the
  reference pixels.
- `assert_unique_ids`, `assert_no_style_elements` and `assert_no_external_references` pass.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` installs `widgets/plasmoidheading.svg`
  byte-identical to the source (checked by the extended `TestInstall.INSTALLED_FILES`).
- Manual smoke test (needs a Plasma session): the system-tray and kickoff popups show a grey
  line over a white line under their header row, the band otherwise matches the grey popup body,
  and the popup's black outline and bevel stay continuous behind the band.

### Mac OS 8.6 Platinum etched separator (`widgets/line.svg`) for the desktop theme (planned 2026-10-17 by the plan role; done 2026-10-17)

**Planned 2026-10-17 by plan.** Independent of every other entry: it adds one widget file to the
existing `org.macos8.desktop` desktop-theme package and one new test module, touches no shipped
SVG, and needs no other plan to land first.

**Goal.** Ship `widgets/line.svg` so Plasma's separators draw the Platinum etched rule (a dark
grey line with a white line beside it) instead of Breeze's 20%-opacity text-colour hairline.
`widgets/line` is the most-read desktop-theme element the package still lacks: grepping the
installed QML for `imagePath: "widgets/line"` finds it in `PlasmaComponents.SpinBox`,
`PlasmaExtras.ListSectionHeader`, `PlasmaExtras.ExpandableListItem`, and in the kicker, system
tray, notifications, digital-clock calendar, volume, network, bluetooth, margins-separator and
konsole-profiles plasmoids. `ls theme/desktop-themes/org.macos8.desktop/widgets/` shows no
`line.svg`, and no PLANS.md entry covers it.

**Consumer contract (verified in installed Plasma 6 QML and Breeze).** Consumers read exactly two
element ids, `horizontal-line` (10 uses) and `vertical-line` (3 uses), through `KSvg.SvgItem`
(whose implicit size is the element's natural size; `ListSectionHeader.qml` stretches it with
`Layout.fillWidth`, the system tray anchors it left/right) or through
`lineSvg.elementSize("horizontal-line").height` (kicker's `horLineHeight`). Breeze's
`/usr/share/plasma/desktoptheme/default/widgets/line.svgz` draws each as one 1x1 rect inside a
`<g id>`. So the thickness of each element is its natural size across the line, and the element
is stretched along the line.

**Reference and provenance.** `macos8.6-screenshots/systemprofiler_betawiki.png` (1024x768
lossless PNG, `sources.txt` "Mac OS 8.6, Japanese (Apple System Profiler …)") shows the Platinum
etched group-box rules on the `#EEEEEE` window body. `python3 tools/sample.py
macos8.6-screenshots/systemprofiler_betawiki.png X Y` gives:
- horizontal rule: `(136,136,136)` = `#888888` at `(260,153)`, `(255,255,255)` = `#FFFFFF` at
  `(260,154)`, body `#EEEEEE` at `(260,152)` and `(260,155)`;
- vertical rule: `#888888` at `(241,128)`, `#FFFFFF` at `(242,128)`, body `#EEEEEE` at
  `(240,128)` and `(243,128)`.
The rule is therefore 2px thick: dark first (top / left), white second (bottom / right). The same
`#888888`/`#FFFFFF` pair recurs at `(678,128)`/`(679,128)` (another vertical rule).

**Approach.**
1. New `theme/desktop-themes/org.macos8.desktop/widgets/line.svg`: root
   `<svg xmlns="http://www.w3.org/2000/svg" width="4" height="2" viewBox="0 0 4 2">` with a
   comment naming the widget, its two element ids, the consumers named above and the
   provenance above (file, coordinates, colours).
   - `<g id="vertical-line">` (no transform) holding `<rect width="1" height="1" fill="#888888"/>`
     and `<rect x="1" width="1" height="1" fill="#FFFFFF"/>`: a 2-wide x 1-tall element at (0,0).
   - `<g id="horizontal-line" transform="translate(3,0)">` holding
     `<rect width="1" height="1" fill="#888888"/>` and
     `<rect y="1" width="1" height="1" fill="#FFFFFF"/>`: a 1-wide x 2-tall element at (3,0).
   - Column 2 stays empty so the two elements' bounds do not touch. Rects carry no `id`, no
     `transform`, and literal `fill` attributes. No `class=`, `<style>`, `<script>`, `style=`
     attribute, hint rect or any other id.
2. `tests/desktoptheme_paths.py`: add `LINE_SVG = os.path.join(PACKAGE, "widgets", "line.svg")`
   beside `ARROWS_SVG`.
3. `tests/test_desktoptheme.py`: import `LINE_SVG`; add `("line.svg", LINE_SVG, 4, 2)` to
   `SVG_CANVASES` (and mention the 4x2 canvas in the comment above it); add
   `os.path.join("widgets", "line.svg")` to `TestInstall.INSTALLED_FILES`.
4. New `tests/test_desktoptheme_line.py`, modelled on `tests/test_desktoptheme_arrows.py`
   (`SvgCase` with `SVG_PATH = LINE_SVG`), with module constants `DARK = "#888888"` and
   `LIGHT = "#FFFFFF"` used by both classes:
   - `TestLine` (see acceptance criteria).
   - `TestLineReference(unittest.TestCase)`: `setUpClass` calls
     `reference_image.read_reference(REFERENCE)`, `setUp` calls `skip_unless_materialized`, and a
     `pixel` helper wraps `png.pixel_at` (follow `SplashReferenceCase` in
     `tests/test_lookandfeel_splash.py`).
5. `README.md`: in the Installing section's desktop-theme inventory, name `widgets/line.svg`
   (the 2px Platinum etched separator, `#888888` then `#FFFFFF`, that list section headers,
   spin boxes and the kicker, system-tray and notification separators draw).
   `tests/test_readme_theme_files.py` fails until README names it.

**Files touched.** New: `widgets/line.svg`, `tests/test_desktoptheme_line.py`. Edited:
`tests/desktoptheme_paths.py`, `tests/test_desktoptheme.py`, `README.md`, `PLANS.md` (move this
entry to Done). The Makefile does not change: `make install` already copies the whole widgets
directory.

**Acceptance criteria.**
- `make check` exits 0, including the new module, `tests/test_desktoptheme.py` (canvas pin,
  `TestInstall`) and `tests/test_readme_theme_files.py`.
- `TestLine.test_line_contract`: `assert_ids_present(self, tree, ("horizontal-line",
  "vertical-line"))`; `{g.get("id") for g in groups_with_id(tree)} == {"horizontal-line",
  "vertical-line"}`; `assert_unique_ids`, `assert_no_script_elements`,
  `assert_no_style_elements` and `assert_no_external_references` pass; and
  `attribute_values(tree, "fill") == {DARK, LIGHT}`.
- `TestLine.test_line_pixels`: `render_slices(tree)["horizontal-line"] == pixel_map((DARK,
  LIGHT), 1, 2)` and `render_slices(tree)["vertical-line"] == pixel_map((DARK, LIGHT), 2, 1)`.
- `TestLine.test_line_placement`: the `vertical-line` group has no `transform` and the
  `horizontal-line` group's `transform` is exactly `"translate(3,0)"`, so the elements' canvas
  bounds are 2x1 at (0,0) and 1x2 at (3,0) (the natural sizes consumers read).
- `TestLineReference.test_horizontal_rule_matches_reference` asserts `pixel(260,153) ==
  (0x88,0x88,0x88)`, `pixel(260,154) == (0xFF,0xFF,0xFF)`, and `pixel(260,152) ==
  pixel(260,155) == (0xEE,0xEE,0xEE)`; `test_vertical_rule_matches_reference` asserts the same
  at `(241,128)`, `(242,128)`, `(240,128)` and `(243,128)`. Each also asserts that
  `"#%02X%02X%02X" % pixel(...)` equals `DARK` / `LIGHT`, tying the sample to the SVG literal.
  Both skip (not fail) when the LFS image is not materialized.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` installs `widgets/line.svg` byte-identical to
  the source (checked by the extended `TestInstall.INSTALLED_FILES`).
- Manual smoke test (needs a Plasma session): the system-tray popup's header separator and a
  kicker submenu separator show a grey line over a white line, with no translucent hairline.


### Mac OS 8.6 menu-bar desktop layout for the global theme (`contents/layouts/`) (planned 2026-10-17 by the plan role; done 2026-10-17)

**Goal.** Make applying the global theme with its desktop layout give one Mac OS 8.6 menu bar:
a single 20px panel across the top of the screen, holding the Apple menu at the left, the
application's menus after it, and the clock and Application menu at the right. Today
`theme/look-and-feel/org.macos8.desktop/contents/` ships no `layouts/` directory. So
`lookandfeeltool -a org.macos8.desktop --resetLayout` (or ticking "Desktop and window layout" in
System Settings → Global Theme) keeps Breeze's bottom taskbar, which `widgets/panel-background.svg`
then draws as a menu-bar bevel at the wrong edge and height.

**Grounding (sampled 2026-10-17 with `tools/png.read_png` + `pixel_at`).** In
`macos8.6-screenshots/desktop_betawiki.png` (retail, 1024x768), at both x=300 and x=400:
row 0 is `#FFFFFF`, rows 1–17 are `#DDDDDD`, row 18 is `#999999`, row 19 is `#000000`, and
row 20 is the desktop pattern `#63639C`. So the menu bar is 20px tall, and its bottom rule ends
at row 19. `desktop_betawiki86b9.png` has the same rows, but it is a beta, so it is not
evidence. `desktop_archiveorg8.6hd.png` (800x600) has a shorter, resampled bar, so ignore it.
These rows match the 2px bottom margin (`#999999` over `#000000`) that
`tests/test_desktoptheme_panel.py` `PANEL_EDGE_PIXELS` already pins.

**Approach.**
- New `theme/look-and-feel/org.macos8.desktop/contents/layouts/org.kde.plasma.desktop-layout.js`,
  modelled on `/usr/share/plasma/layout-templates/org.kde.plasma.desktop.appmenubar/contents/layout.js`
  and on Breeze's `org.kde.breeze.desktop/contents/layouts/org.kde.plasma.desktop-layout.js`. It does
  exactly this, with no `loadTemplate` call (Breeze's `defaultPanel` template is the bottom taskbar
  this replaces):
  - `var panel = new Panel;`
  - `panel.location = "top";`
  - `panel.height = 20;` (a literal, not `gridUnit`-derived; comment it with the sampled rows
    above).
  - `panel.floating = false;` (Plasma 6 panels float by default, which would detach the bar
    from the screen edge. `floating` is a Panel scripting property: the string sits next to
    `lengthMode`/`hiding` in `plasmashell`.)
  - `panel.addWidget(...)` in this order:
    1. `org.kde.plasma.kicker` (the Apple menu; this plan does not configure its icon)
    2. `org.kde.plasma.appmenu` (the global menu, as the stock appmenubar template uses)
    3. `org.kde.plasma.panelspacer`
    4. `org.kde.plasma.systemtray` (kept so that notifications and status icons still have a
       home; Mac OS 8.6 has no equivalent)
    5. `org.kde.plasma.digitalclock`
    6. `org.kde.plasma.windowlist` (the 8.6 Application menu at the far right: it shows the
       active window and switches between windows)

    All six plasmoids are installed under `/usr/share/plasma/plasmoids/`.
  - Then Breeze's wallpaper loop over `desktopsForActivity(currentActivity())`, setting
    `wallpaperPlugin = 'org.kde.image'`, so the `[Wallpaper] Image=org.macos8.desktop` default in
    `contents/defaults` has an image wallpaper to select.
- New `tests/test_lookandfeel_layout.py` (stdlib only, regex over the JS text; no JS engine).
  Put a module-level `LAYOUT` path constant next to the test.
  - `test_layout_file_is_shipped`: the file exists under the package's `contents/layouts/`.
  - `test_exactly_one_panel`: `new Panel` occurs once.
  - `test_panel_is_a_flush_top_bar`: matches `panel.location = "top"`, `panel.floating = false`
    and `panel.height = (\d+)`.
  - `test_panel_height_matches_the_reference`: re-derives the height from
    `desktop_betawiki.png` and checks it equals the JS `panel.height`. Wrap the read in
    `reference_image.read_reference` / `skip_unless_materialized`, as the other reference
    tests do. Derive the height as the first row y at column 400 whose pixel is `#000000` and
    whose next row is not panel grey, plus 1; it must be 20. Also assert that row 0 is
    `#FFFFFF` and row y-1 is `#999999`, so that a moved bevel fails the test.
  - `test_widgets_in_menu_bar_order`: the ordered list of `addWidget("…")` ids equals the six
    above, which pins that `org.kde.plasma.taskmanager`/`icontasks`/`kickoff` are absent.
  - `test_desktops_use_the_image_wallpaper`: matches `wallpaperPlugin = 'org.kde.image'`.
- `tests/test_lookandfeel.py` `TestPackageValid` already validates the installed package, and
  `make install` copies the whole package directory through `install_package`. So no Makefile
  change is needed. Confirm that the installed tree contains `contents/layouts/` (extend an
  existing install assertion only if one lists package files).
- README.md: in the paragraph that describes the global theme, add one sentence. It names
  `contents/layouts/org.kde.plasma.desktop-layout.js`, says that applying the theme with
  `lookandfeeltool -a org.macos8.desktop --resetLayout` (or with "Desktop and window layout"
  ticked) replaces the panels with the single 20px top menu bar, and lists the widgets.
  Plasma replaces the user's existing panels only when the layout is applied, so state that
  plainly.

**Files touched.** `theme/look-and-feel/org.macos8.desktop/contents/layouts/org.kde.plasma.desktop-layout.js`
(new), `tests/test_lookandfeel_layout.py` (new), `README.md`.

**Out of scope (later plans).** The Apple-logo icon for kicker (needs an icon theme or a
shipped icon), the Mac OS 8.6 menu-title metrics for `appmenu`, and the clock format.

**Acceptance criteria.**
- `make check` passes, including the new `tests/test_lookandfeel_layout.py`. Its reference-height
  test runs (does not skip) when the LFS image is materialized, and reads `20`.
- Changing `panel.height` to any value other than the re-derived height, adding a second
  `new Panel`, dropping `panel.floating = false`, or reordering or adding an `addWidget` id each
  makes a named test fail.
- `make install XDG_DATA_HOME=<tmp>` installs
  `<tmp>/plasma/look-and-feel/org.macos8.desktop/contents/layouts/org.kde.plasma.desktop-layout.js`,
  and `kpackagetool6 --type Plasma/LookAndFeel --show org.macos8.desktop` still validates (via the
  existing `TestPackageValid`).

### Headless Plasma render-and-capture script that feeds `tools/fidelity.py` (planned 2026-10-17 by the director role, from the BUGS.md entry "No automated Plasma render/capture step feeding the fidelity check"; done 2026-10-17)

**Provenance.** This replaces the BUGS.md entry "No automated Plasma render/capture step feeding
the fidelity check" (found 2026-10-07). That entry was refused on 2026-10-07 because no offline
render path existed. At the user's direction it is now a plan, because a headless path does
exist on this machine. On 2026-10-17 the director probed it with no display server and isolated
`XDG_*` directories, and every step below exited 0:
- `make install XDG_DATA_HOME=<tmp>/data`;
- seeding `<tmp>/cfg/kwinrc` and `<tmp>/cfg/plasmarc` (below);
- `dbus-run-session -- kwin_wayland --virtual --no-lockscreen --width 320 --height 240 --socket
  <name> --exit-with-session "sh -c 'plasmawindowed org.kde.plasma.calculator & sleep 8;
  spectacle -b -n -f -o <out.png>'"`.

The result was a 320x240 PNG showing the Platinum Aurorae title bar and Platinum push buttons. The
window body pixels sampled `#DDDDDD` (`tests/platinum_palette.py` `FACE`). Without the seeded
config the same capture rendered Breeze. Two things did not work, and the approach avoids them:
- `plasma-apply-colorscheme` run *outside* the KWin session dumped core.
- `lookandfeeltool -a` run inside the session wrote `kdeglobals` but not the `kwinrc`
  decoration keys.
`xvfb-run`, `Xvfb` and `qml`/`qmlscene` are still absent; the path above needs none of them.

**Goal.** Add one bounded, non-interactive command that renders a themed Plasma surface at a fixed
size and writes it as the candidate PNG `tools/fidelity.py` consumes. Pin it with a test that
`make check` runs.

**Approach.**
- New `tools/render_surface.py`. Use the standard library only, following the argparse /
  `report_error` style of `tools/fidelity.py` and `tools/cli.py`.
  - CLI: `python3 tools/render_surface.py OUTPUT [--applet ID] [--width W] [--height H]
    [--settle SECONDS] [--timeout SECONDS]`.
  - Defaults: `--applet org.kde.plasma.calculator`, 320x240, `--settle 8`, `--timeout 90`.
  - Exit status: 0 when written, 1 when the render or capture fails, 2 for usage errors or
    missing tools.
  - `main()` creates a `tempfile.mkdtemp()` scratch root holding `rt/` (mode 0700, used as
    `XDG_RUNTIME_DIR`), `cfg/` (`XDG_CONFIG_HOME`) and `data/` (`XDG_DATA_HOME`). It removes the
    root in a `finally`. The user's real config and session are never touched.
  - It runs `make install XDG_DATA_HOME=<data>` from the repo root.
  - It writes `cfg/kwinrc` and `cfg/plasmarc` from the `[kwinrc][org.kde.kdecoration2]` and
    `[plasmarc][Theme]` groups of `theme/look-and-feel/org.macos8.desktop/contents/defaults`,
    parsed by a small helper `_defaults_groups()`. That way the render follows the global theme
    rather than a second copy of its keys.
  - It launches `dbus-run-session -- kwin_wayland --virtual --no-lockscreen --width W --height H
    --socket render-surface --exit-with-session <sh -c script>`. The script runs these steps in
    order:
    1. `plasma-apply-colorscheme MacOS8`;
    2. `plasmawindowed <applet> &`;
    3. `sleep <settle>`;
    4. `spectacle -b -n -f -o <OUTPUT>`.
  - The child environment drops `WAYLAND_DISPLAY` and `DISPLAY` and sets the three `XDG_*` paths.
    The child runs in its own session (`start_new_session=True`). On `--timeout` the script
    kills the whole process group, as `tests/process_runner.py` does, and exits 1.
  - Before launching, the script checks every external binary above with `shutil.which` and
    exits 2 naming the first one missing.
  - After the run it checks that `OUTPUT` exists and decodes with `tools/png.py` `read_png` at
    exactly W x H. Otherwise it exits 1.
- `Makefile`: add a public `render` target, `$(PYTHON) tools/render_surface.py
  $(RENDER_OUTPUT)`, with `RENDER_OUTPUT ?= render.png`. List it and `RENDER_OUTPUT` in `make
  help`. Add `render.png` to `.gitignore`.
- New `tests/test_render_surface.py`:
  - `TestDefaultsGroups` always runs and parses the real `contents/defaults`. It asserts that
    `_defaults_groups()` returns the `kwinrc` decoration theme
    `__aurorae__svg__org.macos8.desktop` and the `plasmarc` theme name.
  - `TestMissingTool` always runs. It puts an empty directory on `PATH` and asserts exit 2
    with the missing binary named on stderr.
  - `TestRender` is decorated `unittest.skipUnless` all of `kwin_wayland`, `dbus-run-session`,
    `plasmawindowed`, `spectacle` and `plasma-apply-colorscheme` are on `PATH`. In
    `setUpClass` it renders once to a temp file, using `process_runner.start` and
    `process_runner.finish(..., timeout=150)`. It asserts:
    - exit 0;
    - a 320x240 PNG;
    - the pixel at (300, 200) in the window body equals `platinum_palette.FACE`.
  - The render test is slow (about 10–15 s; this machine can throttle under load). Run it once
    per class, never per method.
- `README.md`: one sentence in the `make check`/`make help` paragraph naming `make render` and
  what it writes. Also update the `tools/fidelity.py` module docstring sentence "The Plasma
  render step that produces the candidate image is outside this tool" to name
  `tools/render_surface.py`.

**Out of scope.** These belong to a later plan once a render exists to compare:
- choosing a reference crop and `tools/fidelity.py` thresholds for a rendered surface;
- rendering a `plasmashell` panel.

**Acceptance criteria.**
- `make render` on this machine writes a 320x240 `render.png` whose window body pixel is
  `#DDDDDD`. It leaves `$HOME/.config` and `$HOME/.local/share` unmodified, and removes its
  scratch root.
- `make check` passes. `TestRender` runs here and skips cleanly where the tools are absent.
- No process from the render outlives the script. After `make render`, `pgrep -f
  'socket render-surface'` finds nothing.

**As built (2026-10-17, feature role).** `REQUIRED_TOOLS` also lists `make`, which the script runs
for the install. The capture is written inside the scratch root and copied to `OUTPUT` only after
it decodes at exactly W x H, so a failed run never leaves a stale or partial `OUTPUT`. Beyond the
plan, `tests/test_render_surface.py` covers argument validation and the failure and timeout paths
against shell stubs of the external tools, so those run where KDE is absent.


### Wallpaper, part 2/2: Install the Mac OS 8.6 wallpaper package and select it from the global theme (planned 2026-10-17 by the plan role; done 2026-10-17)

**Goal.** Make part 1's `theme/wallpapers/org.macos8.desktop` package (see "Mac OS 8.6 default
desktop pattern as a Plasma wallpaper package") reach the user. `make install` copies it into
`${XDG_DATA_HOME}/wallpapers/`, the user-local directory Plasma's image wallpaper and
`kpackagetool6 -t Wallpaper/Images` search. `make uninstall` removes it. Applying the global
theme selects it.

**Approach.**
- `Makefile`:
  - Add `WALLPAPER_ID := org.macos8.desktop`,
    `WALLPAPER_PACKAGE := theme/wallpapers/$(WALLPAPER_ID)` and
    `WALLPAPER_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/wallpapers` next to the `AURORAE_*`
    variables.
  - In `_install`, add `install -d "$(WALLPAPER_INSTALL_DIR)"` plus
    `$(call install_package,$(WALLPAPER_ID),$(WALLPAPER_PACKAGE),$(WALLPAPER_INSTALL_DIR))`.
  - In `_uninstall`, add the matching `rm -rf` of the package and its `.staging`/`.old`
    siblings, the same way as the Aurorae line.
  - Update the `_uninstall` comment's list of shared parents.
- `tests/theme_install.py`: add `installed_wallpaper_dir(destdir)`
  (`<destdir>/<XDG_DATA_HOME>/wallpapers`) and `installed_wallpaper(destdir, package_id)`,
  modelled on `installed_aurorae_dir` / `installed_aurorae_theme`.
- `tests/test_wallpaper.py`: add
  `TestInstall(FailedInstallPreservesPackage, InstallLifecycleCases, unittest.TestCase)`,
  shaped like `tests/test_aurorae_decoration.py::TestInstall`:
  - `KIND = "wallpapers"`
  - `PACKAGE_ID`
  - `PACKAGE_DIR`
  - `INSTALLED_FILES`: `metadata.json` and `contents/images/1024x768.png` (add more only if
    the cases accept nested paths; check `tests/install_lifecycle_cases.py`)
  - `COPY_FAILURE_GLOB = "*/wallpapers/*"`
  - overrides of `installed_parent` / `installed_package_dir`
- `tests/test_theme_install.py`: the spaced-root lifecycle test that asserts the scheme, the
  look-and-feel, the desktop theme and the Aurorae theme are installed and then removed also
  asserts the wallpaper package.
- `theme/look-and-feel/org.macos8.desktop/contents/defaults`: append `[Wallpaper]` with
  `Image=org.macos8.desktop`, the same form as Breeze's `Image=Next`.
- `tests/test_lookandfeel.py`:
  - Add the `"Wallpaper"` section and its `["Image"]` option to
    `TestDefaults.test_the_expected_sections_and_keys_are_set`.
  - Add `test_wallpaper_names_the_shipped_package`: `Image` equals the `KPlugin.Id` of
    `theme/wallpapers/org.macos8.desktop/metadata.json`.
- `README.md` "Installing" (outside the tumwater markers): the artifact count goes from four to
  five; name `wallpapers/` among the destinations and the shared directories `make uninstall`
  leaves in place. Add one sentence: the wallpaper is the retail 128x128 desktop pattern,
  shipped at fixed resolutions so it renders 1:1 when the screen matches one. Keep
  `tests/test_readme_theme_files.py` and `tests/test_readme_commands.py` green.

**Files touched.** `Makefile`, `theme/look-and-feel/org.macos8.desktop/contents/defaults`,
`tests/theme_install.py`, `tests/test_wallpaper.py`, `tests/test_theme_install.py`,
`tests/test_lookandfeel.py`, `README.md`.

**Acceptance criteria.**
- `make install DESTDIR=<tmp>` creates
  `<tmp><XDG_DATA_HOME>/wallpapers/org.macos8.desktop/metadata.json`, and
  `make uninstall` removes that package and its `.staging`/`.old` siblings while leaving
  `wallpapers/` and any other package in it.
- The `TestInstall` lifecycle and failed-copy cases pass for the wallpaper.
- `TestDefaults` pins `[Wallpaper] Image=org.macos8.desktop` and ties it to the package
  metadata `Id`.
- `make check` passes.


### Wallpaper, part 1/2: Mac OS 8.6 default desktop pattern as a Plasma wallpaper package (planned 2026-10-17 by the plan role; done 2026-10-17)

**Goal.** The theme still shows Plasma's default wallpaper, but the desktop is the largest
surface in every reference. In the retail desktop `macos8.6-screenshots/desktop_betawiki.png`
(1024x768, lossless), the desktop picture is a **128x128 tile anchored at screen (0,0)**. The
tile at `x=0..127, y=128..255` is byte-identical to 32 other 128-aligned tiles. Each tile in
row `y=0` differs in 2560 pixels (128 x 20, the menu bar's height); tiles under icons and
windows differ too. The tile has 42 colours; the most common is `#63639C`, followed by
`#65659E`, `#64649D`, `#6767A0`, `#66669F` and `#62629B`. Part 1 ships that tile as a Plasma
wallpaper package (`Wallpaper/Images`) of full-screen PNGs. Part 2 ("Install the Mac OS 8.6
wallpaper package and select it from the global theme", which requires this part) installs the
package and has the global theme select it.

**Why full-screen PNGs and not an SVG or a single tile.** The Plasma look-and-feel `[Wallpaper]`
defaults group takes only `Image=<package id>`. Breeze's
`/usr/share/plasma/look-and-feel/org.kde.breeze.desktop/contents/defaults` uses `Image=Next`.
`lookandfeeltool` and `kcm_lookandfeel.so` contain no `FillMode` string, so a theme cannot ask
for tiling. Plasma therefore scales the package image whose size is nearest the screen
("Scaled and Cropped"). An exact-size PNG renders the tile 1:1; a scaled SVG pattern or tile
would blur the 1-px dither. This follows Breeze's `Next` package, which ships
`contents/images/<W>x<H>.png` per resolution.

**Approach.**
- `tools/png_write.py` (new, standard library only: `zlib`, `struct`): add
  `encode_png(width, height, rgb) -> bytes`. It writes 8-bit RGB (colour type 2),
  non-interlaced, filter type 0 on every row, one IDAT compressed at `zlib` level 9, and
  `IHDR`/`IDAT`/`IEND` with CRCs. It raises `ValueError` when `rgb` is not bytes/bytearray of
  exactly `width*height*3`, or when either dimension is not a positive int. This is a separate
  module because `tools/png.py` is the reader and is already over 500 lines.
- `tools/make_wallpaper.py` (new): define these constants:
  - `REFERENCE = "macos8.6-screenshots/desktop_betawiki.png"`
  - `TILE_ORIGIN = (0, 128)`
  - `TILE_SIZE = 128`
  - `RESOLUTIONS`: `(1024,768)`, `(1280,800)`, `(1280,1024)`, `(1366,768)`, `(1440,900)`,
    `(1600,900)`, `(1680,1050)`, `(1920,1080)`, `(1920,1200)`, `(2560,1440)`, `(2560,1600)`,
    `(3840,2160)`
  - `PACKAGE_DIR = "theme/wallpapers/org.macos8.desktop"`

  Also add these functions:
  - `tile_from_reference(image) -> bytes`: the 128x128 RGB block at `TILE_ORIGIN`, read from a
    `tools.png.Image`.
  - `tiled_rgb(tile, width, height) -> bytes`: pixel `(x, y)` is `tile[y % 128][x % 128]`. Build
    each row by repeating the tile row and slicing; do not loop per pixel.
  - `main()`: reads the reference with `tools.png.read_png` and writes
    `PACKAGE_DIR/contents/images/<W>x<H>.png` for each resolution with `encode_png`. Each image
    starts at the tile origin, matching the reference's screen-anchored pattern. The output is
    deterministic, so re-running produces identical bytes.

  The files total about 670 KB at level 9 (measured: 1024x768 ≈ 28 KB, 3840x2160 ≈ 146 KB).
  They are committed like the other PNGs, so they go through Git LFS per `.gitattributes`.
- `theme/wallpapers/org.macos8.desktop/metadata.json` (new): `KPlugin` with
  `"Id": "org.macos8.desktop"` and `"Name": "Mac OS 8.6"`. Copy
  `"Authors": [{"Name": "kde-macos8.6-theme"}]`, `"License": "GPL-2.0-or-later"` and
  `"Version": "0.1.0"` from `theme/look-and-feel/org.macos8.desktop/metadata.json`. Add a
  `Description` ("Mac OS 8.6 default desktop pattern") and
  `"KPackageStructure": "Wallpaper/Images"`.
- Generate the images by running `python3 tools/make_wallpaper.py` once, and commit them.

**Files touched.** `tools/png_write.py`, `tools/make_wallpaper.py`,
`theme/wallpapers/org.macos8.desktop/metadata.json`,
`theme/wallpapers/org.macos8.desktop/contents/images/*.png` (generated),
`tests/test_png_write.py`, `tests/test_wallpaper.py`.

**Acceptance criteria.**
- `tests/test_png_write.py`:
  - `encode_png` output decodes with `tools.png.decode_png` back to the same width, height and
    `rgb`, for a 1x1 image and for a multi-row image of distinct pixels.
  - A wrong-length `rgb`, a zero dimension and a `bool` dimension each raise `ValueError`.
- `tests/test_wallpaper.py`, `TestMetadata`: reuse `tests/package_metadata.PackageMetadata` the
  way `tests/test_lookandfeel.py::TestMetadata` does. Pin `KPackageStructure == "Wallpaper/Images"`
  and `Id == "org.macos8.desktop"`.
- `tests/test_wallpaper.py`, `TestImages` (each read goes through
  `tests/reference_image.skip_unless_materialized`, since the shipped PNGs are LFS objects):
  - `contents/images/` holds exactly `<W>x<H>.png` for each of `make_wallpaper.RESOLUTIONS`.
  - Each image decodes to its named size.
  - Each image's `rgb` equals `make_wallpaper.tiled_rgb(tile, W, H)`, where `tile` is the
    top-left 128x128 block of the shipped `1024x768.png`. This proves every image is the same
    tile, anchored at (0,0).
- `tests/test_wallpaper.py`, `TestReferenceTile` (skip unless `desktop_betawiki.png` is
  materialized):
  - `tile_from_reference(read_png(REFERENCE))` equals the shipped tile.
  - The block at `TILE_ORIGIN` equals the reference block at `(384, 384)` and at `(768, 512)`,
    two other 128-aligned positions, which re-derives the 128 px period.
  - The reference pixel at `(300, 500)` is `#63639C` and equals tile pixel
    `(300 % 128, 500 % 128)`.
- `tests/test_wallpaper.py`, `TestPackageValid(KPackageInstallCase)` with
  `KPACKAGETOOL_TYPE = "Wallpaper/Images"`: `kpackagetool6 -i` accepts the package.
- `make check` passes.

### Mac OS 8.6 Platinum progress bar widget (`widgets/bar_meter_horizontal.svg`) for the desktop theme (planned 2026-10-17 by the plan role; done 2026-10-17)

**Planned 2026-10-17 by plan.** Independent of every other entry: it adds one widget file to the
existing `org.macos8.desktop` desktop-theme package and one new test module, touches no existing
SVG, and needs no other plan to land first. It does not depend on the BUGS.md entry "Splash
progress bar pins the panel face and the empty track as its track and fill colours (found by the
plan role 2026-10-17)". That bug and this plan read the same reference pixels, and neither
change needs the other.

**Goal.** Ship `widgets/bar_meter_horizontal.svg` so `PlasmaComponents.ProgressBar` draws the
Platinum progress bar (a sunken grey track with a lavender fill) instead of Breeze's. Today the
package has no `bar_meter_horizontal` file (`grep -rln "bar_meter" theme tests` finds nothing), so
the notification job progress (`org.kde.plasma.notifications/contents/ui/components/JobItem.qml`),
the task-manager progress overlay (`org.kde.plasma.taskmanager/contents/ui/TaskProgressOverlay.qml`)
and the media controller's `ExpandedRepresentation.qml` fall back to Breeze.

**Consumer (verified in installed Plasma 6 QML).**
`/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/ProgressBar.qml` declares a
`KSvg.Svg` with `imagePath: "widgets/bar_meter_horizontal"` and two `KSvg.FrameSvgItem`s on the
same `imagePath`: the `background` uses `prefix: "bar-inactive"` across the full width, and the
`contentItem` uses `prefix: "bar-active"`, which is `position * availableWidth` wide (for an
indeterminate bar, a quarter-width chunk that slides back and forth) and is hidden when narrower
than `fixedMargins.left + fixedMargins.right`. Both items are
`barSvg.elementSize("hint-bar-size").height` tall when the SVG has a `hint-bar-size` element,
and otherwise top margin plus bottom margin. `widgets/bar_meter_vertical` is out of scope:
`ProgressBar.qml` never reads it.

**Reference and provenance.** `macos8.6-screenshots/boot2_betawiki.png` (240x180 lossless PNG,
`sources.txt` "Mac OS 8.6 (boot screen)") shows the "Starting Up" bar just after it starts. It is
a 0.375x thumbnail of the 640x480 screen. In the thumbnail, the bar occupies rows y=99..102 and
columns x=101..138: x=101..105 hold the lavender filled portion, and x=106..138 the grey unfilled
track. `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png X Y` gives these exact
values, which this plan pins:
- track shadow (top row) `(154,154,154)` = `#9A9A9A` at `(120,99)`;
- track face `(173,173,173)` = `#ADADAD` at `(120,100)`;
- track light edge (bottom row) `(184,184,184)` = `#B8B8B8` at `(120,102)`;
- fill face `(155,155,234)` = `#9B9BEA` at `(102,100)`;
- fill dark edge (lower row) `(120,120,209)` = `#7878D1` at `(102,101)`.
The thumbnail cannot resolve the bar's pixel geometry, so its shape is provenance, recorded here.
The bar is a classic 1px sunken bevel: shadow on the top and left, light on the bottom and right.
The fill draws the same shadow on its top/left and `#7878D1` on its bottom/right. The bar is 10px
tall (the thumbnail's 4 rows / 0.375 ≈ 10.7), with 3px nine-slice borders.

**Approach.**
1. New `theme/desktop-themes/org.macos8.desktop/widgets/bar_meter_horizontal.svg`: root
   `<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 10 10">` with a
   comment naming the widget, its consumer and both prefixes, and the provenance above.
   - Hints (id-bearing rects; KSvg reads only their geometry): `hint-tile-center` 4x4 at (3,3).
     For each of `bar-inactive` and `bar-active`: `{prefix}-hint-top-margin` 4x3 at (3,0),
     `-hint-bottom-margin` 4x3 at (3,7), `-hint-left-margin` 3x4 at (0,3), `-hint-right-margin`
     3x4 at (7,3). Also `hint-bar-size` 10x10 at (0,0). These are exactly
     `nine_slice_hint_geometry(["bar-inactive", "bar-active"], 3, 4)` plus that one extra rect.
   - Both prefixes have nine `<g id="{prefix}-{slice}">` groups (`topleft`, `top`, `topright`,
     `left`, `center`, `right`, `bottomleft`, `bottom`, `bottomright`). The groups sit at the
     canvas origins the margin hints give them: corners at (0,0)/(7,0)/(0,7)/(7,7), top (3,0),
     bottom (3,7), left (0,3), right (7,3), centre (3,3). Draw both prefixes over the same region,
     as frame.svg does for its states. Inside the groups, plain rects with no id and literal
     `fill` attributes paint each prefix's 10x10 bar as follows. The outer top row and outer left
     column are the shadow (`#9A9A9A` for both prefixes). The outer bottom row and outer right
     column are the light edge (`#B8B8B8` inactive, `#7878D1` active). Every other pixel is the
     face (`#ADADAD` inactive, `#9B9BEA` active). At the two mixed corners the shadow takes the
     top-right pixel (0-based (9,0)) and the bottom-left pixel ((0,9)), and the light edge takes
     the bottom-right pixel ((9,9)).
   - Leave out `class=`, `<style>`, `<script>`, any `-inset` hint and any other prefix.
2. `tests/desktoptheme_paths.py`: add `BAR_METER_HORIZONTAL_SVG = os.path.join(PACKAGE, "widgets",
   "bar_meter_horizontal.svg")` beside `SLIDER_SVG`.
3. `tests/test_desktoptheme.py`: import it, add `("bar_meter_horizontal.svg",
   BAR_METER_HORIZONTAL_SVG, 10, 10)` to `SVG_CANVASES`, and add `os.path.join("widgets",
   "bar_meter_horizontal.svg")` to `TestInstall.INSTALLED_FILES`.
4. New `tests/test_desktoptheme_progressbar.py` with `class TestProgressBar(NineSliceCase, …)`
   (follow `tests/test_desktoptheme_slider.py`), with `SVG_PATH = BAR_METER_HORIZONTAL_SVG` and
   `PREFIXES = ("bar-inactive", "bar-active")`, plus a `TestProgressBarReference` class that reads
   the reference through `tools.png` and calls `reference_image.skip_unless_materialized`
   (follow the `pixel` helper in `tests/test_lookandfeel_splash.py`).
5. `README.md`: in the Installing section's desktop-theme inventory, name
   `widgets/bar_meter_horizontal.svg` (the sunken grey Platinum track with a lavender fill for
   `PlasmaComponents.ProgressBar`).

**Files touched.** New: `widgets/bar_meter_horizontal.svg`, `tests/test_desktoptheme_progressbar.py`.
Edited: `tests/desktoptheme_paths.py`, `tests/test_desktoptheme.py`, `README.md`, `PLANS.md` (move
this entry to Done). Nothing in the Makefile changes, because `cp -r` already installs new widget
files. No shared assertion helper changes: the tests below use only existing `svg_assertions` exports.

**Acceptance criteria.**
- `make check` exits 0. The new module passes, and so do the package, install and other widget suites.
- The inherited `NineSliceCase` tests pass for both prefixes: `test_slice_ids_present`,
  `test_tiles_placed_by_margins`, `test_tiles_stay_within_their_margins` and
  `test_no_script_elements`. `test_progressbar_ids_are_unique` runs `assert_unique_ids`.
- `test_progressbar_hint_geometry` runs `assert_hint_geometry(self, tree, ["bar-inactive",
  "bar-active"], 3, 4, extra={"hint-bar-size": ("0", "0", "10", "10")})`.
- `test_track_pixels` and `test_fill_pixels` use `render_slices` and pin every pixel of each
  prefix's nine slices, using `assert_edge_band_pixels` (size 4) for the four edges,
  `assert_corner_pixels` for the four corners and `assert_center_tile_is(…, size=4)` for the centre.
  The values are the shadow, light and face colours above, including the corner rule (for
  example `bar-inactive-topright` is `("#9A9A9A",)*3 + ("#ADADAD", "#ADADAD", "#B8B8B8")*2`).
- `test_progressbar_colours` asserts `attribute_values(tree, "fill") ==
  {"#9A9A9A", "#ADADAD", "#B8B8B8", "#9B9BEA", "#7878D1"}`, plus whatever fill the hint rects carry.
  Either give the hints one of these five colours, or state the hint colour in the test.
- `TestProgressBarReference.test_colours_match_reference` re-derives all five pixels from
  `boot2_betawiki.png` at the coordinates listed above. It also asserts that each sampled value
  equals the SVG literal the slice tests pin, defined once as a module constant used by both.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` installs
  `widgets/bar_meter_horizontal.svg` byte-identical to the source (checked by the extended
  `TestInstall` tuple).
- Manual smoke test (needs a Plasma session): a notification file-copy job shows a 10px sunken grey
  track filling from the left with lavender, with no Breeze blue.


### Mac OS 8.6 Platinum popup / dropdown arrow widget for the desktop theme (done 2026-10-17)

**Planned 2026-10-16 by plan.** Independent of every done widget plan and of the planned
`tabbar`/`toolbar` plans: it adds one artwork file to the existing `org.macos8.desktop`
desktop-theme package under `widgets/`, one path constant in `tests/desktoptheme_paths.py`, a new
test module under `tests/` (`test_desktoptheme_arrows.py`) with the `TestArrows` class, one
`SVG_CANVASES` entry and one `TestInstall.INSTALLED_FILES` tuple entry in
`tests/test_desktoptheme.py`, and the README inventory lines. It touches no other `widgets/*.svg`,
`dialogs/background.svg`, `metadata.json`, or the color scheme.

**Goal.** Ship `widgets/arrows.svg` so `PlasmaComponents.ComboBox`'s dropdown indicator and
`ButtonContent`'s menu-button indicator draw a solid black Platinum triangle instead of inheriting
Breeze's `arrows.svgz`. Today the theme ships no `widgets/arrows`, so `KSvg` resolves the name to
the default theme's Breeze file.

**Consumers (verified in the installed Plasma 6.3.6 tree; a grep for `widgets/arrows`).**
- `org.kde.plasma.components/ComboBox.qml`: the `indicator: KSvg.SvgItem` names
  `imagePath: "widgets/arrows"`, `elementId: "down-arrow"`, `colorSet: KSvg.Svg.Button`, sized
  `Kirigami.Units.iconSizes.small` square and anchored to the right edge.
- `org.kde.plasma.components/private/ButtonContent.qml`: an `KSvg.SvgItem` names
  `imagePath: "widgets/arrows"` and `elementId: "down-arrow"`, sized
  `Kirigami.Units.iconSizes.small` square, `visible` only when
  `Accessible.role === Accessible.ButtonMenu`.

Both render the element by its own bounds scaled into the item's `Kirigami.Units.iconSizes.small`
square, so the element's bounding rect must be square and the triangle drawn inside it (the
default's 14x14 bounding rect is the same trick).

**Default contract.** `zcat /usr/share/plasma/desktoptheme/default/widgets/arrows.svgz` is a 44x44
canvas holding four element ids -- `up-arrow`, `down-arrow`, `left-arrow`, `right-arrow` -- each a
group with a 14x14 invisible bounding rect plus one `class="ColorScheme-Text"` / `fill="currentColor"`
chevron path; the four groups are the same chevron under a rotation transform. The package test's
`assert_no_style_elements` forbids `<style>`, so the artwork's colours must sit on literal `fill`
attributes the pixel and palette tests can read; the Platinum file paints the fill literally.

**Grounding.**
- No reference screenshot in `macos8.6-screenshots/` shows a combo box or menu button (the set is
  desktop, boot/splash, installer, About/System Profiler, Finder/dialogs, photographs and the 8.5
  supplement), so the arrows have no per-pixel reference. Their fill reuses the grounded
  Platinum black (`#000000`) that `tests/test_desktoptheme_checkmarks.py` already pins, and the SVG
  comment records that provenance, as `dialogs/background.svg` records its palette.
- Mac OS 8.6 popup buttons and combo boxes show a solid down triangle, unlike Breeze's open
  chevron, so the artwork is a filled path (no stroke), not a stroked one.

**Approach.**
1. Add `widgets/arrows.svg` to the package: a 16x16 canvas
   (`width="16" height="16" viewBox="0 0 16 16"`) holding four groups at the origin, each with an
   invisible 16x16 bounding `<rect>` (`fill="none"`, no `id`) and one solid `fill="#000000"`
   triangle path:
   - `down-arrow`: `M 4,5 L 12,5 L 8,11 Z`
   - `up-arrow`: `M 4,11 L 12,11 L 8,5 Z`
   - `left-arrow`: `M 11,4 L 11,12 L 5,8 Z`
   - `right-arrow`: `M 5,4 L 5,12 L 11,8 Z`

   The bounding rect pins each element's KSvg bounds to a full 16x16 square so the consumer scales
   the triangle into its square `iconSizes.small` item without stretching (the
   `widgets/checkmarks.svg` groups use the same trick). Give
   the file a header comment naming `widgets/arrows`, the two consumers and the provenance above.
   Use no `class`, `currentColor`, `<style>`, `<script>` or external reference.
2. Add `ARROWS_SVG = os.path.join(PACKAGE, "widgets", "arrows.svg")` to
   `tests/desktoptheme_paths.py`.
3. Add the new module `tests/test_desktoptheme_arrows.py` with
   `TestArrows(SvgCase, unittest.TestCase)`, `SVG_PATH = ARROWS_SVG`, modelled on
   `tests/test_desktoptheme_checkmarks.py`:
   - `test_arrows_contract`: `assert_ids_present(self, self.tree, ("down-arrow", "up-arrow",
     "left-arrow", "right-arrow"))`; `attribute_values(self.tree, "fill") == {"none", "#000000"}`;
     `assert_no_script_elements`.
   - `test_arrows_geometry`: `elements_by_id(self.tree)`; for each of the four ids assert the group
     holds exactly one `rect` and one `path`, that the rect's `(x, y, width, height, fill)` is
     `("0", "0", "16", "16", "none")`, and that the path's `d` is the exact string above with
     `fill == "#000000"`.
4. Add `("arrows.svg", ARROWS_SVG, 16, 16)` to `SVG_CANVASES` and
   `os.path.join("widgets", "arrows.svg")` to `TestInstall.INSTALLED_FILES` in
   `tests/test_desktoptheme.py`, so `TestSvgRootCanvas`, the id/uniqueness and self-containment
   checks, the registry-coverage check and `TestInstall` cover the new file.
5. Name `widgets/arrows.svg` in README.md's status-block widget list and its Installing inventory
   paragraph.

**Acceptance criteria.**
- `make check` exits 0 with `TestArrows` passing and `TestSvgRootCanvas` / `TestInstall` covering
  the new file.
- The SVG parses and contains the four element ids; each element holds one invisible 16x16 bounding
  rect and one solid `#000000` triangle path with the exact `d` above; the parsed `fill` attribute
  values are exactly `none` and `#000000`.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/desktoptheme/org.macos8.desktop/widgets/arrows.svg` byte-identical to source
  (via the extended `TestInstall` tuple).
- Manual smoke test (needs a Plasma session): a `ComboBox` dropdown and a button whose
  `Accessible.role` is `ButtonMenu` draw a solid black Platinum triangle; every other widget is
  unchanged.

**Known deviations (recorded, not fixed here).**
- The reference set has no combo-box / menu-button screenshot, so the arrows have no per-pixel
  reference and reuse the grounded Platinum black by semantic role; the triangle geometry is a
  KDE-required shape the reference set does not show, pinned exactly by the test.
- The file ships one fill for all states; the default also ships no disabled variant, so a disabled
  `ComboBox` arrow stays black rather than Mac OS 8.6's grey (Plasma applies no separate disabled
  colour to a literal fill).

### Mac OS 8.6 Platinum toolbar background widget for the desktop theme (done 2026-10-17)

**Planned 2026-10-15 by plan; implemented 2026-10-17 by the feature role.** The follow-up the done menubaritem plan named alongside
`tabbar`/`tooltip`/`actionbutton`/`busy`/`switch`. Independent of every done widget plan and of the
planned `tabbar` plan: it adds one artwork file to the existing `org.macos8.desktop` desktop-theme
package under `widgets/`, one path constant in `tests/desktoptheme_paths.py`, a new test module
under `tests/` (`test_desktoptheme_toolbar.py`) with the `TestToolBar` class, one `SVG_CANVASES` entry and one
`TestInstall.INSTALLED_FILES` tuple entry in `tests/test_desktoptheme.py`, and the README inventory
lines. It touches no other `widgets/*.svg`, `dialogs/background.svg`, `metadata.json`, or the color
scheme.

**Goal.** Ship `widgets/toolbar.svg` so the `PlasmaComponents.ToolBar` background draws the raised
grey Platinum surface instead of inheriting Breeze's `toolbar.svgz`. Today the theme ships no
`widgets/toolbar`, so `KSvg` resolves the name to the default theme's Breeze file.

**Consumers (verified in the installed Plasma 6.3.6 tree; a grep for `widgets/toolbar`).**
- `org.kde.plasma.components/ToolBar.qml` sets `imagePath: "widgets/toolbar"` on its background
  `KSvg.FrameSvgItem` (`implicitHeight: 40`) and reads that frame's margins for its padding. Its
  child separator `KSvg.SvgItem` reads `widgets/listitem` element `separator`; the theme's
  `widgets/listitem.svg` deliberately ships no `separator`, so no separator draws and this plan
  leaves that file unchanged.
- Installed QML that instantiates a `ToolBar`: kickoff `contents/ui/Footer.qml` (the
  Applications/Places strip), `private/systemtray` `contents/ui/ExpandedRepresentation.qml` (the
  expanded-tray bottom bar), the desktop shell's `WidgetExplorer.qml` and
  `configuration/ShellContainmentConfiguration.qml`.

**Default contract.** `zcat /usr/share/plasma/desktoptheme/default/widgets/toolbar.svgz` is an
unprefixed nine-slice on a 40x40 canvas: `hint-tile-center` plus `top`/`bottom`/`left`/`right`/
`center`/`topleft`/`topright`/`bottomleft`/`bottomright` and the four margin hints, painted a flat
`ColorScheme-Background` with no bevel and no outline.

**Grounding.**
- No reference screenshot in `macos8.6-screenshots/` shows a Plasma toolbar (it is a Plasma-only
  surface with no Mac OS 8.6 counterpart), so the toolbar has no per-pixel reference. Its fills
  reuse the grounded raised Platinum window-body palette (`#000000` outline, `#FFFFFF` highlight,
  `#999999` shadow, `#DDDDDD` face) that `tests/test_desktoptheme_dialog.py` already pins, and the
  SVG comment records that provenance, as `dialogs/background.svg` records it.
- The raised grey surface is exactly `dialogs/background.svg`'s body: the same
  `[Colors:Window] BackgroundNormal=221,221,221` face and the same bevel rule. A Plasma desktop
  theme cannot alias one SVG to another `imagePath`, so the toolbar needs its own file even though
  the two share geometry.

**Approach.**
1. Add `widgets/toolbar.svg` to the package: one unprefixed nine-slice on the same 16x16 canvas as
   `dialogs/background.svg` -- 3px border, 10px centre tile, square corners -- a raised #DDDDDD
   face with the 1px #000000 outline and the 1px bevel inside it (`#FFFFFF` on top/left, `#999999`
   on bottom/right). Copy `dialogs/background.svg`'s slice geometry and give the file its own
   header comment naming `widgets/toolbar` and the provenance above.
2. Add `TOOLBAR_SVG = os.path.join(PACKAGE, "widgets", "toolbar.svg")` to
   `tests/desktoptheme_paths.py`.
3. Add the new module under `tests/` (`test_desktoptheme_toolbar.py`) with `TestToolBar(NineSliceCase, unittest.TestCase)`,
   `SVG_PATH = TOOLBAR_SVG`, `PREFIXES = ("",)`, modelled on `tests/test_desktoptheme_dialog.py`:
   - `test_toolbar_hint_geometry`: `assert_hint_geometry(self, self.tree, [""], 3, 10)`.
   - `test_toolbar_frame_bevel`: `assert_face_bevel(self, render_slices(self.tree), "", FACE,
     "raised", size=10)`.
   - `test_toolbar_colours`: `assert_fill_palette(self, self.tree)`.
4. Add `("toolbar.svg", TOOLBAR_SVG, 16, 16)` to `SVG_CANVASES` and
   `os.path.join("widgets", "toolbar.svg")` to `TestInstall.INSTALLED_FILES` in
   `tests/test_desktoptheme.py`.
5. Name `widgets/toolbar.svg` in README.md's status block widget list and Installing inventory.

**Acceptance criteria.**
- `make check` exits 0 with `TestToolBar` passing and `TestSvgRootCanvas` / `TestInstall` covering
  the new file.
- The SVG parses and contains the nine unprefixed slice ids and the five hint ids; the centre tile
  is a solid #DDDDDD 10x10; the four edge bands and four corners paint the raised bevel; the parsed
  `fill` attribute values are exactly #000000, #FFFFFF, #999999 and #DDDDDD.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/desktoptheme/org.macos8.desktop/widgets/toolbar.svg` byte-identical to source
  (via the extended `TestInstall` tuple).
- Manual smoke test (needs a Plasma session): the Widget Explorer's toolbar strip and the expanded
  system tray's bottom bar draw a raised grey Platinum surface with no Breeze translucent/rounded
  background; every other widget is unchanged.

**Known deviations (recorded, not fixed here).**
- The reference set has no toolbar screenshot, so the surface has no per-pixel reference and reuses
  the grounded raised Platinum grey window-body palette by semantic role.
- The file ships no `separator` element and `widgets/listitem.svg` gains none, so `ToolBar`'s child
  separator stays undrawn (Mac OS 8.6 has no row separators).

### Mac OS 8.6 Platinum tab-bar highlight widget for the desktop theme (done 2026-10-17)

**Planned 2026-10-15 by plan.** The next follow-up the done menubaritem plan named ("then
`tabbar`, `tooltip`, and the `actionbutton`/`busy`/`switch` surfaces"). Independent of every
done widget plan: it adds one artwork file to the existing `org.macos8.desktop` desktop-theme
package under `widgets/`, one path constant in `tests/desktoptheme_paths.py`, a new
test module under `tests/` (`test_desktoptheme_tabbar.py`) with the `TestTabBar` class, one `SVG_CANVASES`
entry and one `TestInstall.INSTALLED_FILES` tuple entry in `tests/test_desktoptheme.py`, and the
README inventory lines. It touches no other `widgets/*.svg`, `dialogs/background.svg`,
`metadata.json`, or the color scheme.

**Goal.** Ship `widgets/tabbar.svg` so the Plasma active-tab / expanded-applet highlights draw a
Platinum raised tab instead of inheriting Breeze's `tabbar.svgz`. Today the theme ships no
`tabbar.svg`, so `KSvg` resolves the name to the default theme's Breeze file.

**Consumers (verified in the installed Plasma 6.3.6 tree; a grep for `widgets/tabbar`).**
- `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/TabBar.qml` and `TabButton.qml`:
  prefix `"north-active-tab"` for `TabBar.position === Header`, else `"south-active-tab"`.
  `TabButton` also sets `enabledBorders` (left/right plus top and/or bottom).
- `/usr/share/plasma/plasmoids/org.kde.plasma.kickoff/contents/ui/Footer.qml`: the
  Applications/Places tab highlight, north/south by `tabBar.position`.
- `CurrentItemHighLight.qml` (systemtray), `showdesktop/contents/ui/main.qml`,
  `shells/org.kde.plasma.desktop/contents/applet/CompactApplet.qml` and `.../views/Panel.qml`:
  a directional prefix by `Plasmoid.location` / `containment.plasmoid.location`
  (`west`/`north`/`east`/`south`), each followed by `if (!hasElementPrefix(prefix)) prefix =
  "active-tab"`.
- A missing prefix or slice renders nothing, and once this file exists there is no cross-theme
  fallback, so all four directional prefixes ship. Shipping all four keeps the `active-tab`
  fallback dead, exactly as the default theme does (it ships the same four and no `active-tab`).

**Default contract.** `zcat /usr/share/plasma/desktoptheme/default/widgets/tabbar.svgz` carries
the nine-slice ids
`{north,south,east,west}-active-tab-{center,top,bottom,left,right,topleft,topright,bottomleft,bottomright}`
with per-state margin hints; each state's **inner** edge -- the one facing the panel content
(bottom for north, top for south, right for west, left for east) -- is its distinctive edge
(Breeze paints it with `ColorScheme-ButtonFocus`), so the four directions are not
interchangeable.

**Grounding.**
- No reference screenshot in `macos8.6-screenshots/` shows a tab control, so the tab has no
  per-pixel reference. Its fills reuse the grounded Platinum raised-face palette (`#000000`
  outline, `#FFFFFF` highlight, `#999999` shadow, `#DDDDDD` face) that
  `tests/test_desktoptheme_frame.py` already pins, and the SVG comment records that provenance,
  as the tooltip token records its KDE-required-role provenance.
- The raised bevel is the same 1px-outline-plus-bevel `widgets/frame.svg`'s `raised` state
  paints, so the active tab is the Platinum raised surface; the inner edge is left open (face
  only, no outline) so the tab merges with the content the way a Platinum tab does.

**Approach.**
1. Add the tab-bar artwork to the package's `widgets/` directory as `tabbar.svg`: four directional nine-slices
   on the tight 12x12 canvas, 3px border, 6x6 centre tile (the `widgets/frame.svg` /
   `widgets/menubaritem.svg` grid), one shared `hint-tile-center` and four margin hints per
   prefix.
   - Each prefix is a raised Platinum tab: `#DDDDDD` face, a 1px `#000000` outline on the three
     outer edges, a 1px `#FFFFFF` highlight inside the top/left outline and a 1px `#999999`
     shadow inside the bottom/right outline, square corners.
   - The inner edge is open (face only): `north-active-tab` bottom, `south-active-tab` top,
     `west-active-tab` right, `east-active-tab` left.
   - The closed edges use the `face_edge_bands("#DDDDDD", "raised")` bands -- top/left
     `("#000000", "#FFFFFF", "#DDDDDD")`, bottom/right `("#DDDDDD", "#999999", "#000000")`;
     the two fully-raised corners use `face_corners("#DDDDDD", "raised")`; each mixed corner
     where the open edge meets a raised edge extends that raised edge's band across its 3x3 tile
     (so a north `bottomleft` is three `#000000 #FFFFFF #DDDDDD` rows, a north `bottomright`
     three `#DDDDDD #999999 #000000` rows, and east/west transpose the same rule).
2. Add `TABBAR_SVG = os.path.join(PACKAGE, "widgets", "tabbar.svg")` to
   `tests/desktoptheme_paths.py`.
3. Add the new test module `test_desktoptheme_tabbar.py` under `tests/` with `TestTabBar(NineSliceCase, unittest.TestCase)`,
   `SVG_PATH = TABBAR_SVG`, `PREFIXES = ("north-active-tab", "south-active-tab",
   "east-active-tab", "west-active-tab")`, modelled on `tests/test_desktoptheme_frame.py`:
   - `test_tabbar_hint_geometry`: `assert_hint_geometry(self, self.tree, self.PREFIXES, 3, 6)`.
   - `test_tabbar_centres_are_the_face`: `assert_center_tile_is` on each `-center` slice,
     `"#DDDDDD"`, 6.
   - `test_tabbar_closed_edges_are_raised` / `test_tabbar_inner_edges_are_open`:
     `assert_edge_band_pixels` for each edge with the raised band or the flat `("#DDDDDD",) * 3`.
   - `test_tabbar_corners`: `assert_corner_pixels` for each corner with the raised table or the
     band-extended table above.
   - `test_tabbar_colours`: `assert_fill_palette(self, self.tree)` from `platinum_palette`.
4. Add `("tabbar.svg", TABBAR_SVG, 12, 12)` to `SVG_CANVASES` and
   `os.path.join("widgets", "tabbar.svg")` to `TestInstall.INSTALLED_FILES` in
   `tests/test_desktoptheme.py`.
5. Name `widgets/tabbar.svg` in README.md's status block widget list and Installing inventory.

**Acceptance criteria.**
- `make check` exits 0 with `TestTabBar` passing and `TestSvgRootCanvas` / `TestInstall` covering
  the new file.
- The SVG parses and contains the 36 `{north,south,east,west}-active-tab-{slice}` ids, the 16
  per-prefix margin-hint ids and `hint-tile-center`; each prefix's centre tile is a solid #DDDDDD
  6x6; the three closed edges and their corners paint the raised bevel; each inner edge is solid
  #DDDDDD; the parsed `fill` attribute values are exactly #000000, #FFFFFF, #999999 and #DDDDDD.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/desktoptheme/org.macos8.desktop/widgets/tabbar.svg` byte-identical to
  source (via the extended `TestInstall` tuple).
- Manual smoke test (needs a Plasma session): Kickoff's Applications/Places tab highlight and the
  `PC3.TabBar` highlight draw a square Platinum raised tab with no Breeze blue line or rounded
  corner; a top/bottom panel's expanded applet and the system-tray current-item highlight draw
  the same; every other widget is unchanged.

**Known deviations (recorded, not fixed here).**
- The reference set has no tab-control screenshot, so the four directions have no per-pixel
  reference and reuse the grounded Platinum raised palette by semantic role.
- `Panel.qml` may pass an empty prefix (`""`) when there is no containment; the file ships no
  unprefixed slices, exactly as the default theme does, so that case draws nothing.

### Mac OS 8.6 Platinum menu-bar item widget for the desktop theme (done 2026-10-09)

**Planned 2026-10-09 by plan.** The follow-up the done viewitem plan left unplanned.
Independent of every done widget plan: it adds one artwork file to the existing
`org.macos8.desktop` desktop-theme package under `widgets/`, one path constant in
`tests/desktoptheme_paths.py`, a new `tests/test_desktoptheme_menubaritem.py` module with
the `TestMenuBarItem` class, one `SVG_CANVASES` entry and one
`TestInstall.INSTALLED_FILES` tuple entry in `tests/test_desktoptheme.py`, and the README
inventory lines. It touches no other `widgets/*.svg`, `dialogs/background.svg`,
`metadata.json`, or the color scheme.

**Goal.** Ship `widgets/menubaritem.svg` so the Plasma menu-bar titles -- the
`org.kde.plasma.appmenu` applet's application-menu titles and the
`org.kde.plasma.windowlist` task-menu button -- draw the Platinum menu-bar behaviour (no
hover highlight; a flat #CCCCFF fill only while the title's menu is open) instead of
inheriting Breeze's `menubaritem.svgz`. Today the theme ships no `menubaritem.svg`, so
`KSvg` resolves the name to the default theme's Breeze file.

**Consumers (verified in the installed Plasma 6.3.6 tree).**
- `/usr/share/plasma/plasmoids/org.kde.plasma.appmenu/contents/ui/MenuDelegate.qml`:
  `background` is a `KSvg.FrameSvgItem` with `imagePath: "widgets/menubaritem"` and
  `prefix` `"pressed"` when `down`, `"hover"` when `hovered && !menuIsOpen`, else
  `"normal"`; `topPadding`/`leftPadding`/`rightPadding`/`bottomPadding` all come from
  that item's `rest.margins`. `main.qml` sets `down: pressed || Plasmoid.currentIndex ===
  index`, so a title takes `pressed` while its menu is open and `hover` only while merely
  hovered.
- `/usr/share/plasma/plasmoids/org.kde.plasma.windowlist/contents/ui/MenuButton.qml`:
  three stacked `KSvg.FrameSvgItem`s read `widgets/menubaritem` with `prefix` `"normal"`,
  `"hover"` and `"pressed"`.
- No other consumer names `widgets/menubaritem` (a grep over `/usr/share/plasma` and
  `/usr/lib/x86_64-linux-gnu/qt6/qml`).
- A missing prefix or slice renders nothing and there is no cross-theme fallback once the
  file exists, so all three prefixes ship.

**Default contract.** `zcat /usr/share/plasma/desktoptheme/default/widgets/menubaritem.svgz`
carries the nine-slice ids
`{normal,hover,pressed}-{center,top,bottom,left,right,topleft,topright,bottomleft,bottomright}`,
one shared `hint-tile-center`, and four margin hints per state, on a 112x34 canvas with a
uniform 6px border and a 22x22 centre tile.

**Grounding.**
- The Mac OS 8.6 menu bar is a flat light-grey strip (`desktop_betawiki.png` samples
  `#DDDDDD` at (5,5)); the landed `widgets/panel-background.svg` already paints it, so
  `normal` paints nothing perceptible and the panel shows through.
- Mac OS 8.6 highlights a menu-bar title only while its menu is open, not on hover, so
  `hover` also paints nothing perceptible; the appmenu label still switches to
  `Kirigami.Theme.highlightedTextColor` (= `[Colors:Selection] ForegroundNormal=0,0,0`,
  black) on hover, the same black it already uses, so the hovered title does not change.
- `pressed` is the flat `[Colors:Selection] BackgroundNormal=204,204,255` (#CCCCFF) fill,
  square corners, no bevel and no outline. `[Colors:Selection] ForegroundNormal=0,0,0` is
  the label colour while `pressed`, so black text stays readable on #CCCCFF.
- The reference set has no screenshot with a menu pulled down (scanning the light
  menu-bar rows of `desktop_betawiki.png`, `desktop_archiveorg8.6hd.png` and the rest for a
  dark full-width run finds none), so the pressed fill reuses the project's sampled
  selection token by semantic role -- as `widgets/viewitem.svg` and `widgets/listitem.svg`
  already do -- rather than a per-pixel menu sample. The SVG comment records that
  provenance.

**Approach.**
1. Add `theme/desktop-themes/org.macos8.desktop/widgets/menubaritem.svg`: one `normal`,
   one `hover` and one `pressed` nine-slice on a tight 12x12 canvas, 3px border, 6x6 centre
   tile (the `widgets/listitem.svg` / `widgets/viewitem.svg` grid).
   - `pressed-*`: every slice a `#CCCCFF` rect filling its tile.
   - `normal-*` and `hover-*`: every slice a `style="fill:#FFFFFF" fill-opacity="0.01"`
     rect with no `fill` attribute (so `render_slices` reads it as `None`) filling its tile.
   - hints: `hint-tile-center` at (3,3,6,6) and
     `{normal,hover,pressed}-hint-{top,bottom,left,right}-margin` at the 3px edges,
     identical for all three states.
2. Add `MENUBARITEM_SVG = os.path.join(PACKAGE, "widgets", "menubaritem.svg")` to
   `tests/desktoptheme_paths.py`.
3. Add `tests/test_desktoptheme_menubaritem.py` with
   `TestMenuBarItem(NineSliceCase, unittest.TestCase)`, `SVG_PATH = MENUBARITEM_SVG`,
   `PREFIXES = ("normal", "hover", "pressed")`, modelled on
   `tests/test_desktoptheme_viewitem.py`:
   - `test_menubaritem_hint_geometry`: `assert_hint_geometry(self, self.tree, self.PREFIXES, 3, 6)`.
   - `test_menubaritem_normal_and_hover_have_no_fill`: `assert_slices_uniform` with `None`
     for both prefixes, and `attribute_values(self.tree, "fill-opacity") == {"0.01"}`.
   - `test_menubaritem_pressed_is_flat_selection_colour`:
     `assert_slices_uniform(..., "pressed", "#CCCCFF")`.
   - `test_menubaritem_slices_fill_their_tiles`:
     `assert_slices_fill_their_tiles(..., (("normal", None), ("hover", None), ("pressed", "#CCCCFF")), 3, 6)`.
   - `test_menubaritem_colours`: `attribute_values(self.tree, "fill") == {"#CCCCFF"}`.
4. Add `("menubaritem.svg", MENUBARITEM_SVG, 12, 12)` to `SVG_CANVASES` and
   `os.path.join("widgets", "menubaritem.svg")` to `TestInstall.INSTALLED_FILES` in
   `tests/test_desktoptheme.py`.
5. Name `widgets/menubaritem.svg` in README.md's status block and Installing inventory.

**Acceptance criteria.**
- `make check` exits 0 with `TestMenuBarItem` passing and `TestSvgRootCanvas`/`TestInstall`
  covering the new file.
- The SVG parses and contains the 27 `{normal,hover,pressed}-{slice}` ids, the 12 per-state
  margin-hint ids and `hint-tile-center`; every `pressed` slice renders entirely #CCCCFF;
  every `normal`/`hover` slice has no `fill` attribute and a `fill-opacity` of 0.01; the
  only parsed `fill` attribute value is #CCCCFF.
- `make install DESTDIR=<tmp> XDG_DATA_HOME=/share` leaves
  `<tmp>/share/plasma/desktoptheme/org.macos8.desktop/widgets/menubaritem.svg`
  byte-identical to source (via the extended `TestInstall` tuple).
- Manual smoke test (needs a Plasma session): the appmenu application-menu titles show no
  highlight while merely hovered and a flat #CCCCFF rectangle with black text while a
  title's menu is open, with square corners and no Breeze bevel; the windowlist task-menu
  button draws the same; every other widget is unchanged.

**Known deviations (recorded, not fixed here).**
- The `windowlist` MenuButton takes its `hover` background from this file, so a hovered
  task-menu button shows no highlight. Mac OS 8.6 has no analogous window-list button, so
  there is no reference for a hovered state and the transparent `hover` is the faithful
  choice for the appmenu titles.
- The uniform 3px margins are the project's tight 12x12 grid; the reference set has no
  menu-open screenshot to measure a per-side menu-title padding from.

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
