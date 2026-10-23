# kde-macos8.6-theme

## Initial prompt

<!-- tumwater:prompt:start -->
A KDE Plasma 6 theme to have the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming.
<!-- tumwater:prompt:end -->

## Status

<!-- tumwater:status:start -->
Pre-alpha: the Mac OS 8.6 "Platinum" look is installable as eight artifacts — color scheme, global theme (with startup splash and desktop layout), desktop theme, Aurorae decoration, wallpaper, icon theme, Kvantum widget style, and Lato font package — plus opt-in GTK 3 and GTK 4 stylesheets, a Firefox userChrome stylesheet, and a cursor theme selection.

Open work is tracked in PLANS.md (planned features), BUGS.md (known bugs), and QUESTIONS.md (decisions needed).
<!-- tumwater:status:end -->

## Installing

`make install` copies eight artifacts into an absolute `${XDG_DATA_HOME}` (the XDG default
`$HOME/.local/share` when it is unset, empty, or relative; `make install` and `make uninstall`
refuse with a diagnostic when that default cannot be resolved because `HOME` is unset or not an
absolute path): the
color scheme
`theme/color-schemes/MacOS8.colors` into `color-schemes/`, the `org.macos8.desktop` global theme
into `plasma/look-and-feel/`, the `org.macos8.desktop` desktop theme into
`plasma/desktoptheme/`, the `org.macos8.desktop` window decoration into `aurorae/themes/`, the
`org.macos8.desktop` wallpaper into `wallpapers/`, the `org.macos8.desktop` icon theme into
`icons/`, the `org.macos8.desktop` Kvantum widget style into
`themes/org.macos8.desktop/Kvantum/`, and the `org.macos8.desktop` Lato font
package into `fonts/org.macos8.desktop/` (Lato Regular and Bold under the SIL
OFL 1.1; the global theme selects it for the general, menu, toolbar, smallest-readable and window-title fonts at KDE default sizes, monospaced text keeps the user's fixed font, and menus and window titles use Lato until a Chicago-style face lands). Applying the global theme selects that wallpaper: the retail 128x128 desktop
pattern, shipped at fixed resolutions so it renders 1:1 when the screen matches one.

The `org.macos8.desktop` Kvantum widget style is selected by the global theme
(`widgetStyle=kvantum`). Kvantum is a separate engine the theme cannot install, so when it is absent
the widgets fall back to another style — choose one in System Settings → Application Style, or
install Kvantum and select our theme with `kvantummanager --set org.macos8.desktop`; `make apply`
runs that selection when `kvantummanager` is on `PATH`. Its Platinum palette and control art
live in
`theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig` and
`theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`; toolbar buttons, toolbar combo boxes
and line edits, split-button dropdowns, tree-view expanders and the status bar map to the same
Platinum button, line-edit and arrow art. Kvantum searches
`$HOME/.local/share/themes/<name>/Kvantum/` with that literal path, so it finds the theme only
when `${XDG_DATA_HOME}` is the default `$HOME/.local/share`.

GTK applications use the separate opt-in install: `make install-gtk` copies the GTK 3 and GTK 4
Platinum stylesheets into `$XDG_DATA_HOME/themes/org.macos8.desktop/`, the same directory that
holds the shared `Kvantum/` widget style, so the two artifacts share one theme directory. The
default `make install` copies no GTK files. `make apply-gtk` installs them the same way and then
selects them: it sets `gtk-theme-name=org.macos8.desktop` in `[Settings]` of
`$XDG_CONFIG_HOME/gtk-3.0/settings.ini` and `gtk-4.0/settings.ini` (the XDG default
`$HOME/.config`), and writes `$XDG_CONFIG_HOME/gtk-4.0/gtk.css` with the
`/* org.macos8.desktop GTK 4 user CSS */` marker and an `@import url(...)` of the installed GTK 4
sheet, so libadwaita applications use it too. Restart running GTK applications to pick up the
selection; KDE users can also choose the theme in System Settings -> Application Style ->
GNOME/GTK Application Style. `make remove-gtk` is what clears the selection: it removes only our
`gtk-theme-name` lines and the marker `gtk.css`, leaving a foreign value or file untouched.
`make uninstall` removes the three GTK files, their `.staging`
leftovers and the emptied `gtk-3.0`/`gtk-4.0` directories but leaves `Kvantum/` and the theme
directory itself.

The standalone Firefox Platinum `userChrome.css` ships at
`theme/firefox/org.macos8.desktop/chrome/userChrome.css` and is installed opt-in into
one profile: `make install-firefox` copies it to that profile's `chrome/userChrome.css`
and adds `toolkit.legacyUserProfileCustomizations.stylesheets=true` as a marker-delimited
block in its `user.js`, and `make remove-firefox` removes only those two changes, leaving
a foreign sheet or preference untouched. Both targets use the profile named by
`FIREFOX_PROFILE=path` (an absolute profile directory) or, when it is unset, the active
profile under `$HOME/.mozilla/firefox` (from `installs.ini`, then `profiles.ini`).
Restart Firefox to pick up the change; setting
`browser.tabs.inTitlebar=0` makes Firefox use the KWin-drawn Aurorae frame.

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
holding the Apple menu (kicker), the application menu, a spacer, the system tray, the clock (12-hour time with AM/PM, no date or
seconds, as the Mac OS 8.6 menu bar shows it) and
the window list. Plasma replaces your panels only when the layout is
applied; applying the theme without it leaves them alone. The layout also switches each desktop
in the current activity to the image wallpaper plugin and lines its icons up in one 32px column
at the right edge with each icon's name on one line under it, as Mac OS 8.6 does. The desktop theme can be selected on its own with
`plasma-apply-desktoptheme org.macos8.desktop`; the global theme applies it through
`[plasmarc][Theme]` in its `contents/defaults`. The global theme also selects the
`org.macos8.desktop` icon theme through `[kdeglobals][Icons]` in the same `contents/defaults`; it
ships our own Platinum-style art for the desktop's hard-disk, folder, document, Trash and
full-Trash icons, drawn at 32x32 with 16x16 and 22x22 renditions,
and for the menu bar's kicker logo (`start-here-kde-symbolic`, our own mark rather than Apple's)
and the `go-next-symbolic` submenu arrow the reference's open Apple menu draws,
drawn for this theme, not traced from Apple's artwork, and inherits Breeze for every other name. The package also ships the `cursors/` Platinum pointer set at nominal sizes 16, 24 and 32: the `left_ptr` arrow, the `xterm` text I-beam, the `hand2` pointing hand, the `watch` busy hourglass, the `fleur` move cross, the `size_hor` and `size_ver` resize arrows, the `size_fdiag` and `size_bdiag` diagonal resize arrows, the `crosshair` precision cross, the `not-allowed` circle-slash, the `dnd-copy` copy plus, the `grab` open hand, the `grabbing` closed fist, the `help` question-mark arrow, the `progress` arrow with a small hourglass, the `pencil` diagonal pencil and the `zoom-in`/`zoom-out` magnifiers, each a black face inside a white outline with byte-identical X-name aliases (`arrow`, `default`, `top_left_arrow`, `dnd-none`; `text`, `ibeam`; `hand1`, `pointer`, `pointing_hand`; `wait`; `move`, `all-scroll`, `size_all`, `dnd-move`; `e-resize`, `ew-resize`, `w-resize`, `h_double_arrow`, `sb_h_double_arrow`; `n-resize`, `ns-resize`, `s-resize`, `sb_v_double_arrow`, `v_double_arrow`, `00008160000006810000408080010102`; `nw-resize`, `se-resize`, `nwse-resize`; `ne-resize`, `sw-resize`, `nesw-resize`; `cross`, `tcross`; `circle`, `crossed_circle`, `03b6e0fcb3499374a867c041f52298f0`, `forbidden`, `no-drop`, `dnd-no-drop`; `left_ptr_help`, `question_arrow`, `whats_this`, `5c6cd98b3f3ebcb1f9c7f1c204630408`, `d9ce0ab605698f320427677b458ad60b`; `half-busy`, `left_ptr_watch`, `00000000000000020006000e7e9ffc3f`, `08e8e1c95fe2fc01f976f1e063a24ccd`, `3ecb610c1bf2410f44200f48c40d3599`). Xcursor roles the theme does not name still come from the fallback cursor theme. `make apply-cursor` selects it: Xcursor searches `$HOME/.icons` rather than `$XDG_DATA_HOME/icons`, so the target installs the icon theme (`INSTALL_PACKAGES=icon-theme`), creates the symlink `$HOME/.icons/org.macos8.desktop` to the installed theme, and runs `plasma-apply-cursortheme org.macos8.desktop`; restart running applications for the new pointer to display correctly. `make remove-cursor` removes only that symlink; it leaves a foreign path and `kcminputrc` untouched, and when `[Mouse] cursorTheme` still names `org.macos8.desktop` it prints `plasma-apply-cursortheme breeze_cursors` as the reset. `make install` and `make apply` select no cursor. The global theme also selects the
`kvantum` widget style (`[kdeglobals][KDE] widgetStyle`), so KDE applications draw the Platinum
bevelled controls instead of Breeze's rounded ones; when Kvantum is not installed they fall back to
another style, which you can choose in System Settings → Application Style. The desktop theme ships
`widgets/panel-background.svg` (the menu bar; a top menu bar draws its white top highlight from a
top-panel `north-` state, and a byte-identical copy ships at `solid/widgets/panel-background.svg`,
where `Panel.qml` looks for an opaque panel's background), `widgets/frame.svg` (the Platinum
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
no hover highlight; its 7px side padding spaces the titles as the reference menu bar does), `widgets/tabbar.svg` (the raised Platinum tab highlights for
Plasma TabBar, TabButton, kickoff footer, and panel applets), `widgets/toolbar.svg` (the
raised grey Platinum toolbar background for `PlasmaComponents.ToolBar` and its
consumers in kickoff, the system tray, and the desktop shell), `widgets/arrows.svg` (the solid
black triangles `ComboBox` and menu buttons draw as their dropdown indicator),
`widgets/scrollbar.svg` (the raised grey thumb and flat grey trough for
`PlasmaComponents.ScrollBar`), `widgets/bar_meter_horizontal.svg` (the sunken grey
track with a lavender-to-white vertical gradient fill for `PlasmaComponents.ProgressBar`), `widgets/line.svg` (the 2px
Platinum etched separator, `#888888` then `#FFFFFF`, that list section headers, spin boxes and
the kicker, system-tray and notification separators draw), and `widgets/plasmoidheading.svg`
(the transparent header and footer bands of applet popups, divided from the body by the same
etched `#888888`/`#FFFFFF` rule), and `widgets/busywidget.svg` (the Platinum ring
`PlasmaComponents.BusyIndicator` spins while a task runs). `widgets/actionbutton.svg`
ships the round Platinum button `PlasmaComponents.RoundButton` and `PlasmaComponents.Dial` draw: a
`#DDDDDD` face with a 1px `#000000` outline and bevel, plus hover and focus rings.
`widgets/action-overlays.svg` ships the desktop containment's folder-icon
add/open/remove action buttons in normal, hover and pressed states.
`widgets/margins-highlight.svg` ships the translucent lavender panel-margin
highlight Plasma draws while a panel is in edit mode, and
`widgets/containment-controls.svg` ships its black-edged Platinum ruler frame,
its twelve offset/minimum/maximum drag sliders as raised Platinum thumbs and
its two lavender centre indicators.
`widgets/slider.svg` ships the same flat grey trough (its `groove` nine-slice)
with a raised grey thumb for `PlasmaComponents.Slider` and `RangeSlider`, in
both orientations. `widgets/switch.svg` ships the Platinum track-and-thumb
toggle `PlasmaComponents.Switch` draws: a flat `#EEEEEE` inactive trough, a
flat white active field, and the same raised grey thumb, with hover, pressed
and focus states. The package
also ships `widgets/background.svg` (the Platinum grey `#DDDDDD` menu body for
`PlasmaComponents.Menu`, `Drawer`, `Popup` and planar applet containers; a
byte-identical copy ships at `widgets/translucentbackground.svg`, where
`BasicAppletContainer.qml` looks for a translucent-hint applet container's
background),
`widgets/tooltip.svg` (the flat `#FFFFCC` Platinum tooltip with a black outline, for panel and
`PlasmaComponents.ToolTip` tooltips; a byte-identical copy ships at `solid/widgets/tooltip.svg`,
where `PlasmaComponents.ToolTip` looks for it) and
`dialogs/background.svg` (the raised grey Platinum window body
`PlasmaCore.Dialog` and `PlasmaCore.AppletPopup` draw, replacing Breeze's
translucent rounded rectangle). The window decoration ships
`metadata.json` and `metadata.desktop` (the KPackage and KWin-discovery
metadata), `org.macos8.desktoprc` (the Aurorae layout: a 22px title bar, 6px
side and bottom borders, and 13x13 close and collapse widgets, each a 12x12 box plus its 1px white highlight, and a 21x13 zoom widget: its box plus the stripe-free gap to its left and the flat spacing to its right), `decoration.svg` (the
active and inactive frames) with its gzipped `decoration.svgz` (the form
`kpackagetool6` requires), and `close.svg`, `maximize.svg`, `restore.svg`, `shade.svg` (the
active and inactive widgets); select it in System Settings → Window
Decorations. An unfocused window wears the flat grey inactive frame and
boxes. `make
uninstall` removes the eight default artifacts and the three opt-in GTK files, leaving the shared
`color-schemes/`, `look-and-feel/`, `desktoptheme/`,
`aurorae/themes/`, `wallpapers/`, `icons/`, `fonts/` and `themes/`
directories and anything else in them in place. It removes only those artifacts, their
hidden `.staging`/`.old` leftovers and the emptied GTK directories, and never edits the
user's configuration: if the removed scheme is still
the selected one (`[General] ColorScheme` in `kdeglobals`), KDE may not be able to resolve
it after the uninstall and falls back to BreezeLight on the next start, so
`make uninstall` prints a warning naming `plasma-apply-colorscheme BreezeLight`
as the reset. `make check` runs the test suite, and `make help`
lists the public targets and the variables that tune them; a run can be narrowed to the test
modules a shell glob matches, e.g. `make check CHECK_PATTERN='test_colorscheme*.py'`, or to
one module, class or method with `make check CHECK_TESTS=test_colorscheme.TestAnchors`. Both
`check` and `check-references` require Python 3.10 or newer (the fidelity tool uses
`int.bit_count()`) and refuse an older `PYTHON` with a diagnostic naming it.
`make apply` installs the eight artifacts exactly as `make install` does and then re-applies them to
the running Plasma session (`make apply` re-applies the global theme, which
selects Lato; a bare `make install` only copies the family), so the just-built theme becomes current without a logout: it re-selects
the `org.macos8.desktop` global theme (without `--resetLayout`, so your panels are left alone), the
`MacOS8` color scheme and the `org.macos8.desktop` desktop theme, tells Kvantum to draw our theme
when `kvantummanager` is on `PATH` (otherwise it notes that and the widgets fall back), then asks
KWin to reconfigure so the window decoration reloads (when neither `qdbus6` nor `qdbus` is installed
it notes that and leaves KWin to reload on its next start). It refuses a non-empty `DESTDIR`, since
applying a staged tree to the running session is wrong, and it needs `lookandfeeltool`,
`plasma-apply-colorscheme` and `plasma-apply-desktoptheme`, exiting 2 naming the first one that is
missing or cannot be started. The startup splash is read at login, so a splash change appears only on the next login.
`make install-local-hook` writes a local-only `post-commit` hook into this clone's git hooks
directory (the common `.git/hooks` shared by the `.tumwater/worktrees/*` worktrees), so every
commit installs and re-applies the theme from the committing worktree; the hook is uncommitted, so
other clones and contributors are unaffected, and `make apply` is the manual equivalent. A
fast-forward merge creates no commit, so it does not trigger the hook. `tools/local_hook.py`
refuses to overwrite or remove a `post-commit` hook it did not write -- this clone's Git LFS hook
is one -- naming the path instead, so `make uninstall-local-hook` removes only its own hook.
`make render` renders the installed theme in a headless KWin session and writes a screenshot PNG
(a 320x240 Plasma calculator window by default) to `RENDER_OUTPUT` (`render.png`); it needs
`dbus-run-session`, `kwin_wayland`, `plasma-apply-colorscheme`, `plasmawindowed` and
`spectacle` and exits 2 naming the first missing tool; a `make` or `dbus-run-session`
that exists but cannot be started is reported the same way. It
installs into a scratch data home and leaves your own Plasma configuration alone.

## Generating the wallpaper

`python3 tools/make_wallpaper.py` rewrites the wallpaper package's images in
theme/wallpapers/org.macos8.desktop/contents/images/ from the reference desktop screenshot
(`macos8.6-screenshots/desktop_betawiki.png`, which needs its Git LFS image materialized). The
output is deterministic, so re-running it rewrites identical bytes. It refuses a reference
screenshot that resolves outside the repository — a checked-in symlink — with a diagnostic
naming the path, so a private file's pixels cannot be copied into the package. It refuses an
images directory that resolves outside the repository the same way, so the generated images
stay inside the wallpaper package.

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
  from retail and must not be used as retail reference. One exception is
  recorded: `aboutsystem_betawiki.png` is a beta build, but its title bar, side
  borders and close/collapse boxes are pixel-identical to the retail
  `systemprofiler_betawiki.png`, so it is used as an evidence-backed
  window-chrome proxy where the set has no other lossless window-chrome
  screenshot. That equality is pinned by
  `tests/test_aurorae_reference_equivalence.py`, and the render gate's
  bottom-border crop stays on the beta because the System Profiler window's
  bottom differs (its sunken content field and bottom scrollbar).
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
well-formed absolute URL (a bad scheme, raw whitespace or control characters, an authority
naming no host, or a malformed path, query or fragment, except for a `file://` URL).
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
reference screenshot and reports mean absolute error, per-channel mean absolute error
(R, G, B, A), RMSE, worst per-channel delta and where it occurs, and the fraction of
differing pixels.
Pass `--candidate-crop X,Y,W,H` to crop the candidate and `--crop X,Y,W,H` to select a
surface region of the reference.

The exit status is 0 when the comparison passes, 1 when it fails, and 2 for a usage or read error.
By default a run passes only when no pixel differs from the reference by more than `--tolerance`
(a per-channel delta; 0, i.e. byte-exact, unless given). Each pixel's alpha byte is compared
along with its red, green and blue bytes, so a transparent candidate cannot pass as an opaque
reference. `--max-mae F` and `--max-frac F` set
aggregate budgets instead: when either is given, a run passes when each given budget is met —
`--max-mae` bounds the mean absolute error, `--max-frac` bounds the differing-pixel fraction — and
the default no-differing-pixel gate no longer applies. `make render` (`tools/render_surface.py`)
produces a candidate render. Where the Plasma render tools are on `PATH`, `make check` renders the
window and byte-compares the title-bar strip (candidate `30,0,80,22` against reference
`30,25,80,22`), the close, zoom and collapse box regions, and the side and bottom border strips of
`aboutsystem_betawiki.png` (the zoom box against `systemprofiler_betawiki.png`), cropping each
region with the same `crop`/`compare` the fidelity tool uses.

## Invariants

`docs/invariants.md` states, per `theme/` subsystem and for the fidelity gate, the guarantee a
surface must keep and the test that pins it. Read the matching row before changing a surface, and
update it in the same change when a guarantee moves. `tests/invariants.py` keeps the register
and the repository in step.

## Development team

This theme is developed by a tumwater team of AI roles. How many roles run at once is a tumwater
setting, not a file in this repository: `maxConcurrent` in the primary checkout's `tumwater.json`
(alongside any `maxConcurrentPerProvider` cap) is the most model runs in flight across all roles
at once, merges included, with the director's own runs sitting outside it; it defaults to 6. A
role cannot change it — the director's `.tumwater-config-request.json` applies only its
`customRoles` array — so the operator sets it from the primary checkout, for example
`tumwater config set maxConcurrent 6` (requested 2026-10-18: run six roles at once).
