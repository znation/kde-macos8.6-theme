# kde-macos8.6-theme

## Initial prompt

<!-- tumwater:prompt:start -->
A KDE Plasma 6 theme to have the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming.
<!-- tumwater:prompt:end -->

## Status

<!-- tumwater:status:start -->
Pre-alpha: five artifacts have landed — the Mac OS 8.6 "Platinum" color scheme, the `org.macos8.desktop` global theme (with its startup splash), the `org.macos8.desktop` desktop theme (Platinum widgets and dialog body), the `org.macos8.desktop` Aurorae window decoration, and the `org.macos8.desktop` wallpaper package.

Open work is tracked in PLANS.md (planned features), BUGS.md (known bugs), and QUESTIONS.md (decisions needed).
<!-- tumwater:status:end -->

## Installing

`make install` copies five artifacts into an absolute `${XDG_DATA_HOME}` (the XDG default
`$HOME/.local/share` when it is unset, empty, or relative; `make install` and `make uninstall`
refuse with a diagnostic when that default cannot be resolved because `HOME` is unset or not an
absolute path): the
color scheme
`theme/color-schemes/MacOS8.colors` into `color-schemes/`, the `org.macos8.desktop` global theme
into `plasma/look-and-feel/`, the `org.macos8.desktop` desktop theme into
`plasma/desktoptheme/`, the `org.macos8.desktop` window decoration into `aurorae/themes/`, and the
`org.macos8.desktop` wallpaper into `wallpapers/`. Applying the global theme selects that wallpaper: the retail 128x128 desktop
pattern, shipped at fixed resolutions so it renders 1:1 when the screen matches one.

Plasma lists the color scheme as `MacOS8` (KDE derives the scheme ID from the filename before the
first dot and resolves an applied ID back to `<ID>.colors`). Select it in System Settings or with
`plasma-apply-colorscheme MacOS8`; because the filename stem is exactly `MacOS8`, the scheme
resolves again on the next start.

The global theme applies that same scheme as one selection: `lookandfeeltool -a
org.macos8.desktop` (list installed packages with `lookandfeeltool -l`). Applying the global
theme also selects its startup splash (`contents/splash/Splash.qml`), which the KDE splash engine
reads, and its window decoration through `[kwinrc][org.kde.kdecoration2]`, so a new window wears
the `org.macos8.desktop` Platinum title bar with the close box on the left and the zoom box and
collapse box on the right. The theme also ships a desktop layout,
`contents/layouts/org.kde.plasma.desktop-layout.js`: applying the theme with
`lookandfeeltool -a org.macos8.desktop --resetLayout` (or with "Desktop and window layout" ticked
in System Settings → Global Theme) replaces your existing panels with one flush 20px top menu bar
holding the Apple menu (kicker), the application menu, a spacer, the system tray, the clock and
the window list. Plasma replaces your panels only when the layout is
applied; applying the theme without it leaves them alone. The layout also switches each desktop
in the current activity to the image wallpaper plugin. The desktop theme can be selected on its own with
`plasma-apply-desktoptheme org.macos8.desktop`; the global theme applies it through
`[plasmarc][Theme]` in its `contents/defaults`. The desktop theme ships
`widgets/panel-background.svg` (the menu bar), `widgets/frame.svg` (the Platinum
plain/raised/sunken frame used by `PlasmaComponents.Frame`, `GroupBox`, the kicker
application-menu sidebar and applet `FrameSvg` consumers), `widgets/button.svg` (the
normal/pressed push button and focus ring), `widgets/radiobutton.svg` (the white,
black-outlined radio face with a black selection dot), and `widgets/checkmarks.svg` (the 2px
black check `CheckBox` overlays on its face when checked, plus the `RadioIndicator`
compatibility dot), `widgets/lineedit.svg` (the white sunken field for
`TextField`/`TextArea`/`SpinBox`), `widgets/listitem.svg` (the flat #CCCCFF
selection row for list and applet item delegates), `widgets/viewitem.svg` (the flat #CCCCFF
highlight for menu items and icon-grid selection), `widgets/menubaritem.svg` (the
flat #CCCCFF title fill an application-menu title shows while its menu is open, with
no hover highlight), `widgets/tabbar.svg` (the raised Platinum tab highlights for
Plasma TabBar, TabButton, kickoff footer, and panel applets), `widgets/toolbar.svg` (the
raised grey Platinum toolbar background for `PlasmaComponents.ToolBar` and its
consumers in kickoff, the system tray, and the desktop shell), `widgets/arrows.svg` (the solid
black triangles `ComboBox` and menu buttons draw as their dropdown indicator),
`widgets/scrollbar.svg` (the raised grey thumb and flat grey trough for
`PlasmaComponents.ScrollBar`), `widgets/bar_meter_horizontal.svg` (the sunken grey
track with a lavender fill for `PlasmaComponents.ProgressBar`), `widgets/line.svg` (the 2px
Platinum etched separator, `#888888` then `#FFFFFF`, that list section headers, spin boxes and
the kicker, system-tray and notification separators draw), and `widgets/plasmoidheading.svg`
(the transparent header and footer bands of applet popups, divided from the body by the same
etched `#888888`/`#FFFFFF` rule).
`widgets/slider.svg` ships the same flat grey trough (its `groove` nine-slice)
with a raised grey thumb for `PlasmaComponents.Slider` and `RangeSlider`, in
both orientations. The package
also ships `widgets/background.svg` (the flat white Platinum body for
`PlasmaComponents.Menu`, `Drawer`, `Popup` and planar applet containers) and
`dialogs/background.svg` (the raised grey Platinum window body
`PlasmaCore.Dialog` and `PlasmaCore.AppletPopup` draw, replacing Breeze's
translucent rounded rectangle). The window decoration ships
`metadata.json` and `metadata.desktop` (the KPackage and KWin-discovery
metadata), `org.macos8.desktoprc` (the Aurorae layout: a 22px title bar, 6px
side and bottom borders, and 12x12 close/zoom/collapse widgets), `decoration.svg` (the
active and inactive frames) with its gzipped `decoration.svgz` (the form
`kpackagetool6` requires), and `close.svg`, `maximize.svg`, `restore.svg`, `shade.svg` (the
active and inactive widgets); select it in System Settings → Window
Decorations. An unfocused window wears the flat grey inactive frame and
boxes. `make
uninstall` removes the five installed artifacts, leaving the shared `color-schemes/`, `look-and-feel/`, `desktoptheme/`,
`aurorae/themes/` and `wallpapers/`
directories and anything else in them in place. It removes only the artifacts
`install` copied, never the user's configuration: if the removed scheme is still
the selected one (`[General] ColorScheme` in `kdeglobals`), KDE may not be able to resolve
it after the uninstall and falls back to BreezeLight on the next start, so
`make uninstall` prints a warning naming `plasma-apply-colorscheme BreezeLight`
as the reset. `make check` runs the test suite, and `make help`
lists the public targets and the variables that tune them; a run can be narrowed to the test
modules a shell glob matches, e.g. `make check CHECK_PATTERN='test_colorscheme*.py'`, or to
one module, class or method with `make check CHECK_TESTS=test_colorscheme.TestAnchors`. Both
`check` and `check-references` require Python 3.10 or newer (the fidelity tool uses
`int.bit_count()`) and refuse an older `PYTHON` with a diagnostic naming it.
`make render` renders the installed theme in a headless KWin session and writes a screenshot PNG
(a 320x240 Plasma calculator window by default) to `RENDER_OUTPUT` (`render.png`); it needs
`dbus-run-session`, `kwin_wayland`, `plasma-apply-colorscheme`, `plasmawindowed` and
`spectacle` and exits 2 naming the first missing tool. It
installs into a scratch data home and leaves your own Plasma configuration alone.

## Generating the wallpaper

`python3 tools/make_wallpaper.py` rewrites the wallpaper package's images in
theme/wallpapers/org.macos8.desktop/contents/images/ from the reference desktop screenshot
(`macos8.6-screenshots/desktop_betawiki.png`, which needs its Git LFS image materialized). The
output is deterministic, so re-running it rewrites identical bytes.

## Reference screenshots

`macos8.6-screenshots/` is the visual reference set for this theme: 28 images for **Mac OS 8.6**
(released 1999-05-10) — retail screenshots and beta builds, one 8.5 supplement and two
photographs — collected from the internet and used as the source of truth when matching menu bar,
window chrome, widget metrics, icons and colour palette in the Plasma 6 port. They are reference
material only — the theme does not ship them.

| Surface | Count | Files |
| --- | --- | --- |
| Desktop | 5 | `desktop_betawiki.png`, `desktop_betawiki86b9.png`, `desktop_fandom.png`, `desktop_archiveorg.jpg`, `desktop_archiveorg8.6hd.png` |
| Boot / splash | 5 | `boot_betawiki.png`, `boot2_betawiki.png`, `boot_archiveorg.jpg`, `bootwhite_archiveorg.jpg`, `splash_macbase.gif` |
| Welcome / first boot / installer | 5 | `welcome_betawiki.png`, `welcome_tomo197707.png`, `firstboot_betawiki.png`, `setup_betawiki.png`, `setup_emaculation.png` |
| About / System Profiler | 7 | `about_betawiki*.png` (3), `aboutsystem_betawiki*.png` (2), `systeminfo_betawiki.png`, `systemprofiler_betawiki.png` |
| Finder / dialogs / apps | 3 | `finder_archiveorg.jpg`, `opendialog_macrumors86.jpg`, `apps_macrumors8.6.jpg` |
| Photos of real hardware | 2 | `boot_powerbookphoto_macrumors.jpg`, `welcome_crtphoto_macrumors.jpg` |
| Non-8.6 supplement | 1 | `sherlock_fandom.jpg` (Mac OS 8.5) |

`sources.txt` records the origin URL and a version label for every file.

- **Labels are evidence-based.** A file is labelled 8.6 only when the version string is legible in
  the image itself (or the source states it). Beta/alpha builds (`8.6a3c2`, `8.6b3`, `8.6b9`,
  `8.6b2c4L8`) and the 8.5 Sherlock supplement are marked as such — they show chrome that differs
  from retail and must not be used as retail reference.
- **Two entries are photographs**, not screenshots: real Macs running 8.6, useful for CRT
  colour/gamma and physical bezel context only.
- **Binary assets are stored with Git LFS** (see `.gitattributes`); run `git lfs install` after
  cloning.
- Images are third-party material kept for reference and attribution; copyright remains with the
  original authors.

## Validating the reference set

`sources.txt` is the provenance record for the images. After adding or renaming a screenshot, run
`python3 tools/check_references.py`: it fails if the record and the files on disk disagree (a
missing file, an unmaterialized Git LFS pointer, a file whose bytes are not a PNG/JPEG/GIF/WebP
image, an image with no entry, a malformed or duplicate entry) or if a source URL is not a
well-formed absolute URL (a bad scheme, raw whitespace or control characters, or an authority
naming no host, except for a `file://` URL).
`python3 tools/check_references.py --self-test` exercises the checker itself.
`make check-references` runs the self-test and then the repository check; it needs the Git LFS
images materialized, so it stays separate from `make check`.

## Sampling reference pixels

`python3 tools/sample.py IMAGE X Y` prints the RGB value of one pixel of a reference
screenshot, in both forms the theme files use:

```
$ python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5
image: macos8.6-screenshots/boot2_betawiki.png  240x180
pixel (5, 5): 99,99,156  #63639C
```

The `99,99,156` triple is copied into a `.colors` file; the `#63639C` literal is copied
into an SVG or QML file. Pass `--width W` and/or `--height H` (default 1) to sample a
rectangle anchored at `(X, Y)`, printed row by row, so a whole title-bar column is one
command:

```
$ python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --height 2
image: macos8.6-screenshots/boot2_betawiki.png  240x180
region (5, 5) 1x2:
(5, 5): 99,99,156  #63639C
(5, 6): 99,99,156  #63639C
```

Coordinates are plain ASCII integers and `--width`/`--height` must be at least 1; a
coordinate or region outside the image, a missing file, or an unreadable PNG exits 2
with a diagnostic naming the coordinate, region, image size or path.

## Fidelity checking

`python3 tools/fidelity.py CANDIDATE REFERENCE` compares a rendered PNG surface against a
reference screenshot and reports mean absolute error, per-channel mean absolute error (R, G, B),
RMSE, worst per-channel delta and where it occurs, and the fraction of differing pixels.
Pass `--crop X,Y,W,H` to select a surface region of the reference.

The exit status is 0 when the comparison passes, 1 when it fails, and 2 for a usage or read error.
By default a run passes only when no pixel differs from the reference by more than `--tolerance`
(a per-channel delta; 0, i.e. byte-exact, unless given). `--max-mae F` and `--max-frac F` set
aggregate budgets instead: when either is given, a run passes when each given budget is met —
`--max-mae` bounds the mean absolute error, `--max-frac` bounds the differing-pixel fraction — and
the default no-differing-pixel gate no longer applies. `make render` (`tools/render_surface.py`)
produces a candidate render; no reference crop or threshold for a rendered surface is chosen yet.
