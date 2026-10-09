# kde-macos8.6-theme

## Initial prompt

<!-- tumwater:prompt:start -->
A KDE Plasma 6 theme to have the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming.
<!-- tumwater:prompt:end -->

## Status

<!-- tumwater:status:start -->
Pre-alpha: four artifacts have landed — the Mac OS 8.6 "Platinum" color scheme in `theme/color-schemes/`, the `org.macos8.desktop` global theme in `theme/look-and-feel/` (with its Mac OS 8.6 startup splash under `contents/splash/`), the `org.macos8.desktop` desktop theme in `theme/desktop-themes/` (menu bar, frame, push button, radio button, checkbox, text field, list item, scroll bar, slider, and menu/popup body widgets, plus the dialog / applet-popup window body), and the `org.macos8.desktop` Aurorae window decoration in `theme/aurorae/themes/` (the active and inactive Platinum title bars with their close and zoom widgets).

Open work is tracked in PLANS.md (planned features), BUGS.md (known bugs), and QUESTIONS.md (decisions needed).
<!-- tumwater:status:end -->

## Installing

`make install` copies four artifacts into an absolute `${XDG_DATA_HOME}` (the XDG default
`$HOME/.local/share` when it is unset, empty, or relative; `make install` and `make uninstall`
refuse with a diagnostic when that default cannot be resolved because `HOME` is unset or not an
absolute path): the
color scheme
`theme/color-schemes/MacOS8.colors` into `color-schemes/`, the `org.macos8.desktop` global theme
into `plasma/look-and-feel/`, the `org.macos8.desktop` desktop theme into
`plasma/desktoptheme/`, and the `org.macos8.desktop` window decoration into `aurorae/themes/`.

Plasma lists the color scheme as `MacOS8` (KDE derives the scheme ID from the filename before the
first dot and resolves an applied ID back to `<ID>.colors`). Select it in System Settings or with
`plasma-apply-colorscheme MacOS8`; because the filename stem is exactly `MacOS8`, the scheme
resolves again on the next start.

The global theme applies that same scheme as one selection: `lookandfeeltool -a
org.macos8.desktop` (list installed packages with `lookandfeeltool -l`). Applying the global
theme also selects its startup splash (`contents/splash/Splash.qml`), which the KDE splash engine
reads, and its window decoration through `[kwinrc][org.kde.kdecoration2]`, so a new window wears
the `org.macos8.desktop` Platinum title bar with the close box on the left and the zoom box on
the right. The desktop theme can be selected on its own with
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
selection row for list and applet item delegates), and `widgets/scrollbar.svg` (the
raised grey thumb and flat grey trough for `PlasmaComponents.ScrollBar`).
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
side and bottom borders, and 12x12 close/zoom widgets), `decoration.svg` (the
active and inactive frames) with its gzipped `decoration.svgz` (the form
`kpackagetool6` requires), and `close.svg`, `maximize.svg`, `restore.svg` (the
active and inactive widgets); select it in System Settings → Window
Decorations. An unfocused window wears the flat grey inactive frame and
boxes. `make
uninstall` removes the four installed artifacts, leaving the shared `color-schemes/`, `look-and-feel/`, `desktoptheme/` and
`aurorae/themes/`
directories and anything else in them in place. It removes only the artifacts
`install` copied, never the user's configuration: if the removed scheme is still
the selected one (`[General] ColorScheme` in `kdeglobals`), KDE may not be able to resolve
it after the uninstall and falls back to BreezeLight on the next start, so
`make uninstall` prints a warning naming `plasma-apply-colorscheme BreezeLight`
as the reset. `make check` runs the test suite, and `make help`
lists the public targets and the variables that tune them; a run can be narrowed to the test
modules a shell glob matches, e.g. `make check CHECK_PATTERN='test_colorscheme*.py'`.

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
the default no-differing-pixel gate no longer applies. Producing the candidate render is not yet
automated (see BUGS.md).
