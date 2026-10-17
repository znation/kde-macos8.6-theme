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

### Mac OS 8.6 Platinum etched separator (`widgets/line.svg`) for the desktop theme (planned 2026-10-17 by the plan role)

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

## Done

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
`tests/svg_assertions/checks.py` (the `extra_groups` argument on `assert_tiles_placed_by_margins`),
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
- `tests/svg_assertions/`, `tests/nine_slice_case.py`, `tests/test_svg_assertions_checks.py`
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
