# kde-macos8.6-theme

## Initial prompt

<!-- tumwater:prompt:start -->
A KDE Plasma 6 theme to have the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming.
<!-- tumwater:prompt:end -->

## Status

<!-- tumwater:status:start -->
Pre-alpha: the Platinum theme covers KDE/Qt, GTK 3 and GTK 4, Firefox chrome and content, and cursor surfaces.

Open work is tracked in PLANS.md (planned features), BUGS.md (known bugs), and QUESTIONS.md (decisions needed).
<!-- tumwater:status:end -->

<a id="navigation"></a>

## Contents

- [Prerequisites](#prerequisites)
- [Installing](#installing)
- [Generating the wallpaper](#generating-the-wallpaper)
- [Reference screenshots](#reference-screenshots)
- [Validating the reference set](#validating-the-reference-set)
- [Sampling reference pixels](#sampling-reference-pixels)
- [Fidelity checking](#fidelity-checking)
- [Running checks](#running-checks)
- [Invariants](#invariants)
- [Development team](#development-team)

## Prerequisites

| Task | Requirements |
| --- | --- |
| Use the KDE theme | A KDE Plasma 6 session. Kvantum is a separately installed widget engine; when it is absent, widgets use another style. `kvantummanager` selects the theme in Kvantum. |
| Install packages | GNU Make and standard Linux utilities, including `install` and `flock`. `make install` copies theme files into the data home; it does not change the running user's settings. See [Installing](#installing). |
| Apply the theme | Python 3.10 or newer; `lookandfeeltool`, `plasma-apply-colorscheme`, `plasma-apply-desktoptheme`, `kwriteconfig6` and `kreadconfig6`. `make apply` installs the files and changes the running user's settings. |
| Select the GTK theme alone | Python 3.10 or newer, the package-install utilities above, and writable data and config homes. Run `make apply-gtk`; restart GTK applications. See [Installing](#installing) for selection and backup details. |
| Select the cursor theme alone | Python 3.10 or newer, the package-install utilities above, and `plasma-apply-cursortheme` on `PATH`. Run `make apply-cursor`; aggregate `make apply` skips cursor selection with a note when that tool is missing. See [Installing](#installing) for details. |
| Install Firefox sheets alone | Python 3.10 or newer and an existing writable Firefox profile, found automatically or specified as `FIREFOX_PROFILE=/absolute/profile`. Run `make install-firefox`; aggregate `make apply` skips this step with a note when it finds no profile. See [Installing](#installing) for profile selection and restart details. |
| Render headlessly | Python 3.10 or newer; `dbus-run-session`, `kwin_wayland`, `plasma-apply-colorscheme`, `plasmawindowed` and `spectacle`. Dialog render modes also require `kdialog`; the GTK dialog render mode requires `zenity` instead; the desktop render mode requires `plasmashell`; the splash render mode requires `ksplashqml`. The default applet render also needs the `org.kde.plasma.calculator` applet (Debian packages it in `plasma-widgets-addons`); missing, the render refuses with exit 2 before any session, naming the applet id and the searched locations. See [Rendering a candidate](#rendering-a-candidate). |
| Run optional GTK 4 probes | Xvfb, `xvfb-run`, `xauth`, and Python GTK 4 introspection bindings. See [Running checks](#running-checks) for isolated commands. |
| Materialize reference images | Git LFS; run `git lfs install` and `git lfs pull`. See [Validating the reference set](#validating-the-reference-set). |
| Sample JPEG screenshots | ImageMagick's `convert` on `PATH`; PNG inputs need no extra tool. The sampler refuses a JPEG input without it. See [Sampling reference pixels](#sampling-reference-pixels). |

## Installing

### Quick start

See [Prerequisites](#prerequisites) for requirements. Choose one route:

```sh
make install
```

This copies the theme files without selecting them. To install and select Platinum for the
running user, use the alternative below. It changes user settings and may replace personal GTK 4
CSS after backing it up; [restoring personal GTK 4 CSS](#restoring-personal-gtk-4-css) explains
how. Existing panels are preserved; applying the optional desktop layout is a separate choice.

```sh
make apply
```

Restart GTK applications and Firefox to pick up their styles; the splash changes at the next
login. For GTK alone, use `make apply-gtk`. See [Removing the theme](#removing-the-theme) to
undo the installation.

### Installation details

`make install` copies every data-home artifact into an absolute `${XDG_DATA_HOME}` (the XDG default
`$HOME/.local/share` when it is unset, empty, or relative; `make install` and `make uninstall`
refuse with a diagnostic when that default cannot be resolved because `HOME` is unset or not an
absolute path, and refuse a `DESTDIR`, `XDG_DATA_HOME`, `HOME`, `FLOCK_TIMEOUT` or `RENDER_OUTPUT` carrying a character that is
shell syntax inside the double-quoted recipe words such a value is expanded into -- a double
quote, `$`, a backtick or a backslash -- before running any recipe (a value carrying any other
control byte -- 0x01-0x1f or 0x7f, tab and newline excepted -- such as 0x1b, the terminal
escape, is refused instead of echoed back, since those diagnostics print the raw value on its
way to a terminal), while a space or an apostrophe stays legal; and refuse a `PYTHON` carrying
a character that is shell syntax at the unquoted position its value is expanded into -- those
four plus an apostrophe, a semicolon, a pipe, an ampersand, a parenthesis, a redirection
character or a newline, while a space stays legal because a value may carry interpreter
arguments), and refuse a `PYTHON` carrying a control byte before the unquoted
shell-syntax diagnostic can echo it): the
color scheme
`theme/color-schemes/MacOS8.colors` into `color-schemes/`, the `org.macos8.desktop` global theme
into `plasma/look-and-feel/`, the `org.macos8.desktop` desktop theme into
`plasma/desktoptheme/`, the `org.macos8.desktop` window decoration into `aurorae/themes/`, the `org.macos8.desktop`
window decoration's QML package into `kwin/decorations/` (the look-and-feel defaults select it: their `library=org.kde.kwin.aurorae` / `theme=org.macos8.desktop` pair pins the package here, where KWin 6.3.6 matches this plugin's packages under `kwin/decorations/` by `KPlugin.Id`), the
`org.macos8.desktop` wallpaper into `wallpapers/`, the `org.macos8.desktop` icon theme into
`icons/`, the `org.macos8.desktop` Kvantum widget style into
`themes/org.macos8.desktop/Kvantum/`, and the `org.macos8.desktop` Lato font
package into `fonts/org.macos8.desktop/` (Lato Regular and Bold under the SIL
OFL 1.1; the global theme selects it for the general, menu, toolbar, smallest-readable and window-title fonts at KDE default sizes, monospaced text keeps the user's fixed font, and menus and window titles use Lato until a Chicago-style face lands), and the GTK 3 and GTK 4 Platinum stylesheets, their `index.theme` descriptor and ten shared assets into `themes/org.macos8.desktop/`. Applying the global theme selects the original neutral `#CCCCCC` wallpaper placeholder, shipped at fixed resolutions.

The `org.macos8.desktop` Kvantum widget style is selected by the global theme
(`widgetStyle=kvantum`). Kvantum is a separate engine the theme cannot install, so when it is absent
the widgets fall back to another style — choose one in System Settings → Application Style, or
install Kvantum and select our theme with `kvantummanager --set org.macos8.desktop`; `make apply`
runs that selection when `kvantummanager` is on `PATH`. Its Platinum palette and control art
live in
`theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig` and
`theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`; toolbar buttons, toolbar combo boxes
and line edits, split-button dropdowns, tree-view expanders, toolbox tabs, the status bar, the
dock header band, the MDI subwindow title band and its window buttons map to the same
Platinum button, line-edit and arrow art; a window's bottom-right size grip draws the reference
grow box's white and `#777777` checker diamond. Kvantum searches
`$HOME/.local/share/themes/<name>/Kvantum/` with that literal path, so it finds the theme only
when `${XDG_DATA_HOME}` is the default `$HOME/.local/share`. Running `make apply` with a
non-default `${XDG_DATA_HOME}` prints a note naming both paths, because the selection would
succeed yet the engine would keep drawing Kvantum's built-in default theme until the theme
directory also exists under the literal default data home.

`make remove-kvantum` clears that selection: it removes only our
`[General] theme=org.macos8.desktop` line from
`$XDG_CONFIG_HOME/Kvantum/kvantum.kvconfig`, leaving a foreign theme name and the rest of the
file byte-identical, and creates nothing when the directory, the file or the selection is
absent. Restart running Qt applications afterwards so they reload the widgets. `make uninstall`
leaves the selection in place — a theme chosen through System Settings survives an uninstall —
and names this reset when the kept selection still points at the removed theme.

GTK applications use the same install: `make install` (and therefore `make apply`) copies the GTK 3 and GTK 4
Platinum stylesheets, their `index.theme` theme descriptor and the ten shared check, radio, mixed-state dash,
combo box, menu arrow, disclosure arrow, submenu arrow and title-button box assets into
`$XDG_DATA_HOME/themes/org.macos8.desktop/`, the same directory that
holds the shared `Kvantum/` widget style, so the two artifacts share one theme directory. `make install-gtk` installs only those files, for repairing that surface without touching the other packages. `make apply` then
selects them: it sets `gtk-theme-name=org.macos8.desktop` in `[Settings]` of
`$XDG_CONFIG_HOME/gtk-3.0/settings.ini` and `gtk-4.0/settings.ini` (the XDG default
`$HOME/.config`), and writes `$XDG_CONFIG_HOME/gtk-4.0/gtk.css` with the
`/* org.macos8.desktop GTK 4 user CSS */` marker and an `@import url(...)` of the installed GTK 4
sheet, so libadwaita applications use it too. A `gtk.css` that is not ours is copied byte-for-byte
to an unused `gtk.css.bak` sibling first (`.bak.1`, `.bak.2` and up when that name is taken, so an
earlier backup is never overwritten) and then replaced. `make apply-gtk` installs and selects only this surface. Restart running GTK applications to pick up the
selection; KDE users can also choose the theme in System Settings -> Application Style ->
GNOME/GTK Application Style. `make remove-gtk` is what clears the selection: it removes only our
`gtk-theme-name` lines and the marker `gtk.css`, leaving a foreign value or file and any backup
untouched. The two targets serialize on a lock over the config home's parent directory, so a concurrent apply
and removal cannot publish a stale selection; a run that cannot take that lock within its bounded
wait exits 2 with a diagnostic. An apply also holds the data-home lock that `make install` and
`make uninstall` hold for their whole run, re-checks the installed sheets under it and keeps it
through the selection, so a concurrent uninstall cannot remove the sheets between the apply's
check and the selection that names them. `make uninstall` removes the thirteen GTK files, their `.staging`
leftovers and the emptied `assets`/`gtk-3.0`/`gtk-4.0` directories but leaves `Kvantum/` and the
theme directory itself.

The standalone Firefox Platinum `userChrome.css` and `userContent.css` ship at
`theme/firefox/org.macos8.desktop/chrome/userChrome.css` and
`theme/firefox/org.macos8.desktop/chrome/userContent.css`. `make apply` installs them into the active profile when one exists (a machine without a Firefox profile gets a note and the other surfaces still apply); `make install-firefox` installs them into
one named profile: it copies them to that profile's
`chrome/userChrome.css` and `chrome/userContent.css` and adds
`toolkit.legacyUserProfileCustomizations.stylesheets=true` and
`browser.tabs.inTitlebar=0` as a marker-delimited block in its `user.js`, and
`make remove-firefox` removes only those three changes,
leaving a foreign sheet or preference untouched. The title-bar preference hands
Firefox's tab-in-title-bar chrome to the window manager, so the window takes the
Platinum Aurorae frame (pinstriped title bar, close and zoom boxes) instead of
Firefox's own borderless title strip. All of these use the profile named by
`FIREFOX_PROFILE=path` (an absolute profile directory) or, when it is unset, the active
profile under `$HOME/.mozilla/firefox` (from `installs.ini`, then `profiles.ini`). The
profile path reaches the recipe shells pasted into a double-quoted word, so the
Makefile refuses a `FIREFOX_PROFILE` carrying a character that is shell syntax
inside it -- a double quote, `$`, a backtick or a backslash -- before running
any recipe (a control-byte value is refused without its bytes echoing into the
diagnostic), while a space or an apostrophe stays legal.
The two targets serialize on a lock over the profile directory, so a concurrent
install and removal cannot leave a preference block without its sheets (or the
sheets without the block); a run that cannot take that lock within its bounded
wait exits 2 with a diagnostic. Restart Firefox to pick up the change; the
installed `browser.tabs.inTitlebar=0` is what makes Firefox use the KWin-drawn
Aurorae frame.

System Settings displays the color scheme as `Platinum`; its legacy CLI ID remains `MacOS8` (KDE derives the scheme ID from the filename before the
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
ships original placeholder illustrations for the desktop's hard-disk, folder, document, Trash and
full-Trash icons, drawn at 32x32 with 16x16 and 22x22 renditions, for the Home and
Desktop places and the standard Documents, Downloads, Music, Pictures, Videos,
Templates, Public and Temporary Files places (the same Platinum folder at every size),
and for the menu bar's kicker logo (`start-here-kde-symbolic`, our own mark rather than Apple's)
and the `go-next-symbolic` submenu arrow. `PLACEHOLDERS.md` records each temporary graphic
pending user-approved replacement. The illustrations are
drawn for this theme, not traced from Apple's artwork, and inherits Breeze for every other name. The package also ships the `cursors/` Platinum pointer set at nominal sizes 16, 24 and 32: the `left_ptr` arrow, the `xterm` text I-beam, the `hand2` pointing hand, the `watch` busy wristwatch, the `fleur` move cross, the `size_hor` and `size_ver` resize arrows, the `size_fdiag` and `size_bdiag` diagonal resize arrows, the `crosshair` precision cross, the `not-allowed` circle-slash, the `dnd-copy` copy plus, the `grab` open hand, the `grabbing` closed fist, the `help` question-mark arrow, the `progress` arrow with a miniature watch face, the `pencil` diagonal pencil, the `zoom-in`/`zoom-out` magnifiers and the `context-menu` arrow beside a small menu panel, each a black face inside a white outline with byte-identical X-name aliases (`arrow`, `default`, `top_left_arrow`, `dnd-none`; `text`, `ibeam`; `hand1`, `pointer`, `pointing_hand`; `wait`; `move`, `all-scroll`, `size_all`, `dnd-move`; `e-resize`, `ew-resize`, `w-resize`, `h_double_arrow`, `sb_h_double_arrow`, `col-resize`, `split_h`, `left_side`, `right_side`; `n-resize`, `ns-resize`, `s-resize`, `sb_v_double_arrow`, `v_double_arrow`, `00008160000006810000408080010102`, `row-resize`, `split_v`, `top_side`, `bottom_side`; `nw-resize`, `se-resize`, `nwse-resize`, `top_left_corner`, `bottom_right_corner`; `ne-resize`, `sw-resize`, `nesw-resize`, `top_right_corner`, `bottom_left_corner`; `cross`, `tcross`; `circle`, `crossed_circle`, `03b6e0fcb3499374a867c041f52298f0`, `forbidden`, `no-drop`, `dnd-no-drop`; `left_ptr_help`, `question_arrow`, `whats_this`, `5c6cd98b3f3ebcb1f9c7f1c204630408`, `d9ce0ab605698f320427677b458ad60b`; `half-busy`, `left_ptr_watch`, `00000000000000020006000e7e9ffc3f`, `08e8e1c95fe2fc01f976f1e063a24ccd`, `3ecb610c1bf2410f44200f48c40d3599`; `cell`, `plus`; `openhand`; `closedhand`). Xcursor roles the theme does not name still come from the fallback cursor theme. `make apply-cursor` selects it: Xcursor searches `$HOME/.icons` rather than `$XDG_DATA_HOME/icons`, so the target installs the icon theme (`INSTALL_PACKAGES=icon-theme`), creates the symlink `$HOME/.icons/org.macos8.desktop` to the installed theme, and runs `plasma-apply-cursortheme org.macos8.desktop`; restart running applications for the new pointer to display correctly. `make remove-cursor` removes only that symlink; it leaves a foreign path and `kcminputrc` untouched, and when `[Mouse] cursorTheme` still names `org.macos8.desktop` it prints `plasma-apply-cursortheme breeze_cursors` as the reset. `make install` copies the cursor artifacts without selecting them, while aggregate `make apply` exposes the installed pointer set and selects it when `plasma-apply-cursortheme` is available; when that tool is absent, apply leaves the set installed and linked and prints a note. The global theme also selects the
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
no hover highlight; its 7px side padding spaces the titles as the reference menu bar does), `widgets/pager.svg` (the optional Pager's virtual-desktop cells: an idle #999999 outline, a translucent #EEEEEE hover wash and the current desktop's translucent #CCCCFF selection, as one 1px-border nine-slice shared by such a panel applet), `widgets/notes.svg` (the
optional Notes plasmoid's ten sticky-note papers — one flat fill inside a 1px black outline
per 32x32 cell, one cell per config colour), `widgets/timer.svg` (the optional Timer
plasmoid's 22 LCD edit digits — ten black seven-segment numerals and their red-alert `_1`
variants plus the two colon separators, each a stroke-only glyph in a 16x32 cell), `widgets/clock.svg` (the
optional analog clock plasmoid's flat white ringed face with twelve 2px black hour ticks, the black centre screw,
the point-down black hour and minute shafts and red second shaft, and the invisible shadow and glass overlays, as
nine side-by-side element columns on one 528x96 canvas),
`widgets/tasks.svg` (the optional Task Manager's task faces — idle (transparent), hover/focus (#CCCCFF), attention (#FFFFCC), minimized (#999999 rule) and progress (#CCCCFF rule) — as one 7px/3px nine-slice shared by every panel edge, plus the four group-expander arrows), `widgets/tabbar.svg` (the raised Platinum tab highlights for
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
translucent rounded rectangle). The package carries no art for the twelve legacy default-theme widget names (`analog_meter`, `bar_meter_vertical`, `branding`, `calendar`, `configuration-icons`, `dragger`, `glowbar`, `media-delegate`, `monitor`, `picker`, `plot-background` and `scrollwidget`), so those elements keep the stock default theme's art: no installed Plasma 6 shell, plasmoid or desktop QML requests one of these names as a widgets/<stem>.svg path (probed 2026-11-09), and the guarded list is pinned by `tests/test_desktoptheme_legacy.py` and the `## desktoptheme` row in `docs/invariants.md`. The window decoration ships
`metadata.json` and `metadata.desktop` (the KPackage and KWin-discovery
metadata), `org.macos8.desktoprc` (the Aurorae layout: a 22px title bar, 6px
side and bottom borders, and 13x13 close and collapse widgets, each a 12x12 box plus its 1px white highlight, and a 21x13 zoom widget: its box plus the stripe-free gap to its left and the flat spacing to its right), `decoration.svg` (the
active and inactive frames) with its gzipped `decoration.svgz` (the form
`kpackagetool6` requires), and `close.svg`, `maximize.svg`, `restore.svg`, `shade.svg` (the
active and inactive widgets); select it in System Settings → Window
Decorations. An unfocused window wears the flat grey inactive frame around
a buttonless bar: no close, zoom or collapse boxes draw on it, and the grey
title text is the reference's centred `#777777`, and clicking where one of those boxes would sit
presses nothing: the installed `kwin/decorations/` package copies — the selection the look-and-feel
defaults make — gate their title-bar buttons' hit areas on window activity, so the click meant to
refocus the window cannot act a close, zoom or collapse box. `make uninstall` removes every installed artifact, including the thirteen GTK files, leaving the shared
`color-schemes/`, `look-and-feel/`, `desktoptheme/`,
`aurorae/themes/`, `kwin/decorations/`, `wallpapers/`, `icons/`, `fonts/` and `themes/`
directories and anything else in them in place. It removes only those artifacts, their
hidden `.staging`/`.old` leftovers and the emptied GTK directories; it refuses to run if a fixed
install destination parent is a symlink. It never edits the user's configuration: if the removed
scheme is still
the selected one (`[General] ColorScheme` in `kdeglobals`), KDE may not be able to resolve
it after the uninstall and falls back to BreezeLight on the next start, so
`make uninstall` prints a warning naming `plasma-apply-colorscheme BreezeLight`
as the reset; if the GTK selection `make apply` published still names
`org.macos8.desktop` after the uninstall, it likewise prints a warning naming
`make remove-gtk` as the reset; if the Kvantum selection `kvantummanager` wrote
(`[General] theme=` in `kvantum.kvconfig`) still names `org.macos8.desktop`, it
prints a warning naming `make remove-kvantum` as the reset that clears only that
selection; if the widget-style selection the look-and-feel apply wrote
(`[kdeglobals][KDE] widgetStyle=kvantum`, which selects the Kvantum style
plugin as Qt's widget style) still names `kvantum` after the uninstall, it
prints a warning naming the reset
`kwriteconfig6 --file kdeglobals --group KDE --key widgetStyle --delete`,
which deletes exactly the key the apply wrote and reverts it to its absence
(as prose grounded against the upstream KDE/Kvantum sources the project
reads for its Kvantum adaptations, never test-asserted: every Qt start
keeps selecting the style that key names whether or not it still resolves,
drawing the Kvantum engine's built-in default theme while the plugin -- a
system package outside this theme's artifacts -- exists, or the platform
default style when it does not); and if the icon-theme selection the
look-and-feel apply wrote (`[kdeglobals][Icons] Theme=org.macos8.desktop`)
still names the removed icon theme after the uninstall, it prints a warning
naming the reset `kwriteconfig6 --file kdeglobals --group Icons --key Theme
--delete`, which deletes exactly the key the apply wrote and reverts it to
its absence (likewise never-test-asserted prose ground: KDE and Qt
applications cannot load the removed icon theme and keep the default
icons; the reference screenshots show no uninstall warning to sample either
of these warnings from); and if the global theme the look-and-feel
apply step selected (`[kdeglobals][KDE]
LookAndFeelPackage=org.macos8.desktop`, the published selection of the
apply's `lookandfeeltool -a` step) still names the removed global theme
after the uninstall, it prints a warning naming the reset
`kwriteconfig6 --file kdeglobals --group KDE --key LookAndFeelPackage
--delete`, which deletes exactly the key the apply wrote and reverts it
to its absence (as prose grounded against the upstream `lookandfeeltool`
sources the project reads for its apply adaptations, never
test-asserted: a Plasma shell start whose global-theme id no longer
resolves keeps the stock look-and-feel on the next start; the reference
screenshots show no uninstall warning to sample it from); and if the
pointer selection
`plasma-apply-cursortheme` wrote
(`[Mouse] cursorTheme=` in `kcminputrc`) still names `org.macos8.desktop`, it
prints a warning naming `plasma-apply-cursortheme breeze_cursors` as the reset
— that command must be run by hand, because `make remove-cursor` owns only the
`$HOME/.icons` link and never touches `kcminputrc`; and if the font
selections the look-and-feel apply wrote (`[kdeglobals][General]
font=Lato,10`, `menuFont=Lato,10`, `toolBarFont=Lato,10` and
`smallestReadableFont=Lato,8`, and `[kdeglobals][WM] activeFont=Lato,10` —
the Lato family `make uninstall` deletes with the fonts) still name their
published values after the uninstall, it prints one warning per
still-selected key, each naming that key's reset
`kwriteconfig6 --file kdeglobals --group General --key font --delete` (and
the analogous `menuFont`, `toolBarFont`, `smallestReadableFont` and
`--group WM --key activeFont` resets), which deletes exactly the one key the
apply wrote and reverts it to its absence (as prose grounded against the
fontconfig font matching KDE and Qt applications use for text rendering,
never test-asserted: when the requested family name stops resolving inside
the installation, the match falls back to the best-scoring installed
family, so applications keep drawing text with a default face wherever no
other copy of the family remains installed; the reference screenshots show
no uninstall warning to sample it from); if the desktop theme
selection `plasma-apply-desktoptheme` wrote (`[Theme] name=` in `plasmarc`)
still names `org.macos8.desktop` after the uninstall, it prints a warning
naming `plasma-apply-desktoptheme breeze` as the reset (`breeze` is Plasma's
stock default desktop theme, a platform-required value grounded against the
tool the apply itself runs — like the pointer's `breeze_cursors`, the
reference screenshots show no uninstall warning to sample it from); and if the
window-button layout the apply's `kwriteconfig6` runs wrote
(`[org.kde.kdecoration2] ButtonsOnLeft=X` and `ButtonsOnRight=AL` in
`kwinrc`) is still there after the uninstall, it prints a warning naming the
reset `kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key
ButtonsOnLeft --delete && kwriteconfig6 --file kwinrc --group
org.kde.kdecoration2 --key ButtonsOnRight --delete`, which deletes exactly
the two keys the apply wrote and reverts the layout to the keys' absence,
where KWin draws its built-in default decoration (`kwriteconfig6`'s
documented `--delete` option is the grounded platform-required value; the
reference screenshots show no uninstall warning to sample it from); and if
the window-decoration selection the look-and-feel apply wrote
(`[kwinrc][org.kde.kdecoration2] library=org.kde.kwin.aurorae` and
`theme=org.macos8.desktop`, the `KWin/Decoration` package id KWin resolves
the window decoration through under that plugin library -- its packages live
under `kwin/decorations/` and match the id by `KPlugin.Id`) is still
there after the uninstall, it prints a warning naming the reset
`kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key library
--delete && kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key
theme --delete`, which deletes exactly the two keys the apply wrote and
reverts KWin to the keys' absence, where it draws its built-in default
window decoration (the `--delete` reset is the same grounded
`kwriteconfig6` platform-required value as the button layout's, and the
fallback claim -- what KWin draws when the package id cannot resolve
inside the Aurorae engine -- is grounded against the
upstream KWin window-decoration sources the project reads for its aurorae
engine; the reference screenshots show no uninstall warning to sample it
from); and if the window-decoration theme key alone -- the
`theme=org.macos8.desktop` value in
`[kwinrc][org.kde.kdecoration2]`, even when `library` is missing or foreign,
a shape the pair diagnostic above stays silent on -- still names the removed
decoration package after the uninstall, it prints a warning naming the
reset `kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme
--delete && kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key
library --delete`, which deletes exactly the two keys the look-and-feel
apply wrote and reverts KWin to the keys' absence, where it draws its
built-in default window decoration (the `--delete` reset is the same
grounded `kwriteconfig6` platform-required value as the pair's, and the
fallback claims -- that a start whose group holds neither key draws the
built-in default window decoration and that a start with `library` set but
no resolvable `theme` falls back the same way -- are recorded as prose,
never test-asserted, grounded against the upstream KWin window-decoration
sources the project reads for its aurorae engine; the reference screenshots
show no uninstall warning to sample it from); and if the defaults layer of
the KDE config search path that the look-and-feel apply wrote still names
the removed ids -- a `kdedefaults/ksplashrc` file whose `[KSplash]` group's
last `Theme` value is `org.macos8.desktop`, the splash selection that
appears nowhere else in any read config, and a flat `kdedefaults/package`
file whose whole trimmed content is `org.macos8.desktop` -- it prints the
two warnings naming the resets `kwriteconfig6 --file <path> --group
KSplash --key Theme --delete` for the splash selection and `rm "<path>"`
for the package default (`kwriteconfig6`'s accepting a literal
`kdedefaults/` path for `--delete` is a platform-required value verified in
a scratch-home apply on this host, and the flat file's writer/removal story
is a prose ground against the upstream Plasma sources the project reads for
its Plasma-tool adaptations; the reference screenshots show no uninstall
warning to sample them from); and if the defaults layer also mirrors the
live selections the landed diagnostics cover -- a `kdedefaults/kdeglobals`
file whose `[KDE]` group's last `widgetStyle` value is `kvantum` and whose
`[Icons]` group's last `Theme` value is `org.macos8.desktop` (the two
conditions independent), a `kdedefaults/kwinrc` file whose
`[org.kde.kdecoration2]` group holds the `library=org.kde.kwin.aurorae` and
`theme=org.macos8.desktop` pair (the `NoPlugin=false` key
the apply also wrote is not a match condition), and a
`kdedefaults/plasmarc` file whose `[Theme]` group's last `name` value is
`org.macos8.desktop` -- it prints four warnings naming the resets
`kwriteconfig6 --file <path> --group KDE --key widgetStyle --delete`,
`kwriteconfig6 --file <path> --group Icons --key Theme --delete`, the
`kwriteconfig6 --file <path> --group org.kde.kdecoration2` two-key
`library`/`theme` `--delete` pair and `kwriteconfig6 --file <path>
--group Theme --key name --delete` (the same scratch-home apply recorded
above left all three mirrors on this host, and the fallback claim -- that a
start whose live key is absent or reset away re-resolves the selection
from the defaults layer -- is recorded as prose grounded against the KDE
config-cascade sources the landed live-config diagnostics already ground;
the reference screenshots show no uninstall warning to sample it from).
No such warning edits the
user's configuration.
Because these diagnostics name the settings under `$XDG_CONFIG_HOME`, that
variable when it carries a control byte (0x01-0x1f or 0x7f, tab and newline
excepted) is refused at parse time, before any recipe runs and unechoed;
shell metacharacters stay legal, since the value is not expanded by recipes
into unquoted words -- the recipes read it through the shell, inside double
quotes. `make check` runs the test suite, and `make help`
lists the public targets and the variables that tune them; a run can be narrowed to the test
modules a shell glob matches, e.g. `make check CHECK_PATTERN='test_colorscheme*.py'`, or to
one module, class or method with `make check CHECK_TESTS=test_colorscheme.TestAnchors`.
Both overriding variables are validated before the run: a `CHECK_PATTERN` carrying a recipe-shell
metacharacter — a double quote, `$`, a backtick or a backslash, and also an apostrophe, which the
single-quoted `-p` word the value is expanded into cannot escape — or an `INSTALL_PACKAGES`
carrying one of those four plus a semicolon, pipe, ampersand, parenthesis, newline or redirection
character (its value list is expanded unquoted) is refused outright, before any recipe runs, with a
diagnostic naming the variable and the value, while a space stays legal in either; the
validators of `CHECK_TESTS` and `CHECK_PARALLEL` paste the value into their own double-quoted
guard words first, so a value of either carrying a double quote, `$`, a backtick or a backslash
is refused by the same shared guard before any recipe runs, with a diagnostic naming the
variable and value; a value carrying a control byte (0x01-0x1f or 0x7f, tab and newline
excepted) is refused without echoing the value, since the
validators echo a refused value's bounds from the shell-copied argument and a byte like 0x1b
would otherwise reach the terminal raw. The wider shell punctuation — a semicolon, an apostrophe,
a pipe and the like — stays inert inside the guards' double quotes and is still refused at run
time by the guards' own alphabet tests, which name the value back. By
default the discovered modules run in parallel through `tools/check_parallel.py`, which runs
each module as one worker process and prints the modules' outputs in module order;
`make check CHECK_PARALLEL=0` restores the serial `unittest discover` run, and
`make check CHECK_PARALLEL=n` bounds the worker count (default: one per core). Every
target that runs a Python tool requires Python 3.10 or newer (the fidelity tool uses
`int.bit_count()`) and refuses an older `PYTHON` with a diagnostic naming the target; `make help`
lists the same `PYTHON` floor.
`make apply` installs every artifact exactly as `make install` does and then applies all of them: it re-applies the theme to
the running Plasma session (`make apply` re-applies the global theme, which
selects Lato; a bare `make install` only copies the family), so the just-built theme becomes current without a logout: it re-selects
the `org.macos8.desktop` global theme (without `--resetLayout`, so your panels are left alone), the
`MacOS8` color scheme and the `org.macos8.desktop` desktop theme, writes the theme's
window-button layout into `kwinrc` (close box at the leading edge, zoom and collapse at the
trailing edge — Plasma's look-and-feel apply drops those two keys), tells Kvantum to draw our theme
when `kvantummanager` is on `PATH` (otherwise it notes that and the widgets fall back), then asks
KWin to reconfigure so the window decoration reloads. That reload request needs a D-Bus
command-line tool: it prefers `qdbus6` and falls back to `qdbus` when `qdbus6` is not installed.
When neither tool is installed, when the chosen command cannot be started or times out, or when it
exits nonzero, the apply prints a note naming the failure and the consequence, and the optional
reload step does not fail the apply; in every such case KWin reloads the window decoration on its
next start. Applying or removing Platinum preserves the user's keyboard mappings and does not
change `kxkbrc`.

**Existing installations (2026-11-04):** Earlier versions added `ctrl:swap_lalt_lctl` to the
keyboard's XKB options. To undo that change, open KDE System Settings → Keyboard → Advanced,
disable the left Control/Alt swap, and retain any other selected options. Apply the change and
log out and back in if needed.
The apply process then selects the installed GTK 3 and GTK 4 schemes, exposes and selects the Xcursor pointer set, and installs the Firefox sheets into the active profile when one exists. The cursor selection is skipped with a note when `plasma-apply-cursortheme` is absent, and the Firefox step is skipped with a note when no profile is found, so an apply still completes on a machine that has neither. It refuses a non-empty `DESTDIR`, since
applying a staged tree to the running session is wrong, and it needs `lookandfeeltool`,
`plasma-apply-colorscheme`, `plasma-apply-desktoptheme`, `kwriteconfig6` and `kreadconfig6`,
exiting 2 naming the first one that is
missing or cannot be started, or reporting the scratch directory it cannot create. The three
Plasma re-selections and the button-layout write run under the data-home flock that `make install` and `make uninstall` hold: a run
that cannot take that lock within its bounded wait exits 2 naming the data home, so a concurrent
uninstall cannot remove the packages between the apply's selections, and a `HOME` no install could
have resolved is refused the same way. The startup
splash is read at login, so a splash change appears only on the next login; restart GTK applications and Firefox for their selections. `make apply-gtk` and `make apply-cursor` remain available to repair one surface alone.
After `make install`, run `make apply-plasma` to reselect the installed global theme, color scheme and desktop theme, write the window-button placement, and request Kvantum selection and a KWin reload without applying other surfaces. It requires Python 3.10+ and `lookandfeeltool`, `plasma-apply-colorscheme`, `plasma-apply-desktoptheme` and `kwriteconfig6`. The global-theme application preserves panels; Kvantum selection names its off-default data home in a note when it runs under one, and the splash change appears at the next login.
`make install-local-hook` writes a local-only `post-commit` hook into this clone's git hooks
directory (the common `.git/hooks` shared by the `.tumwater/worktrees/*` worktrees), so every
commit installs and re-applies the theme from the committing worktree; the hook is uncommitted, so
other clones and contributors are unaffected, and `make apply` is the manual equivalent. A
fast-forward merge creates no commit, so it does not trigger the hook. `tools/local_hook.py`
refuses to overwrite or remove a `post-commit` hook it did not write -- this clone's Git LFS hook
is one -- naming the path instead, so `make uninstall-local-hook` removes only its own hook.
### Rendering a candidate

Capture the default calculator, one of the fourteen widget dialogs, the desktop menu bar, or the startup splash:

```sh
make render RENDER_OUTPUT=calculator.png
make render RENDER_MODE=gtk-dialog RENDER_OUTPUT=gtk.png
python3 tools/render_surface.py checkbox.png --checkbox-dialog
python3 tools/render_surface.py combobox.png --combobox-dialog
python3 tools/render_surface.py lineedit.png --lineedit-dialog
python3 tools/render_surface.py menu.png --menu-dialog
python3 tools/render_surface.py radiolist.png --radiolist-dialog
python3 tools/render_surface.py calendar.png --calendar-dialog
python3 tools/render_surface.py color.png --color-dialog
python3 tools/render_surface.py icon.png --icon-dialog
python3 tools/render_surface.py progressbar.png --progressbar-dialog
python3 tools/render_surface.py slider.png --slider-dialog
python3 tools/render_surface.py textbox.png --textbox-dialog
python3 tools/render_surface.py gtk.png --gtk-dialog
python3 tools/render_surface.py inactive.png --inactive-dialog
python3 tools/render_surface.py file.png --file-dialog
python3 tools/render_surface.py desktop.png --desktop
python3 tools/render_surface.py splash.png --splash
```

The Make target captures the default calculator and takes its output path from `RENDER_OUTPUT`;
set `RENDER_MODE` to `calculator`, `checkbox-dialog`, `combobox-dialog`, `lineedit-dialog`,
`menu-dialog`, `radiolist-dialog`, `calendar-dialog`, `color-dialog`, `icon-dialog`, `progressbar-dialog`, `slider-dialog`,
`textbox-dialog`, `gtk-dialog`, `inactive-dialog`, `file-dialog`, `desktop` or `splash` to select a surface. Direct Python commands remain available. The calculator
capture defaults to 320x240; each dialog capture is fixed at 480x360; the desktop capture is fixed at 640x400; the splash capture is fixed at 640x400. Dialog modes cannot be combined with each other, a
different applet, or width/height overrides; the desktop capture cannot be combined with a dialog mode, an applet override, or width/height overrides; the splash capture cannot be combined with a dialog
mode, the desktop mode, an applet override, or width/height overrides. Dialog captures require `kdialog` in the kdialog
modes and `zenity` in the GTK mode, the desktop capture requires `plasmashell`, and the splash capture requires `ksplashqml`; see
[Prerequisites](#prerequisites) for the other rendering tools. To compare a candidate PNG with
the references, see [Fidelity checking](#fidelity-checking).

`make render` renders the installed theme in a headless KWin session and writes a screenshot PNG
(a 320x240 Plasma calculator window by default) to `RENDER_OUTPUT` (`render.png`); it needs
`dbus-run-session`, `kwin_wayland`, `plasma-apply-colorscheme`, `plasmawindowed` and
`spectacle` and exits 2 naming the first missing tool; the calculator captures also need the
`org.kde.plasma.calculator` applet installed (Debian packages it in `plasma-widgets-addons`),
which no tool check sees because a package is not a command — a render whose applet is absent
refuses with exit 2 before any session, naming the applet id and the searched
`plasma/plasmoids` locations. A `make` or `dbus-run-session`
that exists but cannot be started is reported the same way, as is a scratch session
directory that cannot be created. It
installs into a scratch data home and leaves your own Plasma configuration alone. The
scratch config home takes its `[kwinrc][org.kde.kdecoration2]` selection from the look-and-feel
`defaults` (`library=org.kde.kwin.aurorae`, `theme=org.macos8.desktop`), the `KWin/Decoration`
package id KWin matches under `kwin/decorations/`; re-running the same capture in the same
session setup with the earlier SVG-aurorae value (`__aurorae__svg__org.macos8.desktop`) pasted in
produces a byte-identical PNG, the A/B selection-equality check recorded in docs/invariants.md's
`## kwin-decoration` row, and sabotaging an installed package file the QML copies need makes the
two captures differ instead of silently passing. A wholly
black capture — the screen before the window has painted — is refused with a diagnostic
naming the settle wait rather than published as a render. A failed install, render or
capture exits 1; a SIGTERM or SIGHUP ends the run with 128 plus the signal number.
For help diagnosing a failed capture, see [Troubleshooting a render](#troubleshooting-a-render).
With `--checkbox-dialog` the render instead opens a `kdialog` warning box whose
"do not ask again" check box the Kvantum engine draws with the theme's checkbox art
(`kdialog` must be on `PATH` in the kdialog dialog modes) and captures it as a 480x360 PNG
whose crop the checkbox gate (`tests/test_render_surface.py::TestCheckboxDialogRender`)
byte-compares like the chrome strips. `--combobox-dialog` opens a `kdialog` chooser
whose combo box the engine draws with the theme's `comboarrow` art; the render captures
it the same way, for the combo arrow gate
(`tests/test_render_surface.py::TestComboboxDialogRender`). `--menu-dialog` opens a
`kdialog` menu list whose item view the engine frames with the theme's `GenericFrame` art,
captured at the same 480x360 size; the item-view gate
(`tests/test_render_surface.py::TestMenuDialogRender`) byte-compares the item view's
rendered border runs, its white interior and the current-item focus ring there.
`--radiolist-dialog` opens a `kdialog` radio list whose sunken list field, the selected
row's selection band and the checked and unchecked radio indicators the engine draws
with the theme's palette and the shipped `radio` art, captured at the same 480x360 size;
the checked item is a fixed default (`on` in the client's arguments), so the selection
never depends on clock, network or input. The radio-list gate
(`tests/test_render_surface.py::TestRadioDialogRender`) pins the clear selection-face band,
the checked dot and unchecked ring cores, and the top edge of the sunken list field.
`--calendar-dialog` opens a `kdialog` calendar pinned to January 1970 (`--default
1970-01-07` with the load-bearing `--dateformat`: without it kdialog ignores `--default`
and opens today's month), captured at the same 480x360 size; the calendar gate
(`tests/test_render_surface.py::TestCalendarDialogRender`) pins the flat window face,
the white day-table face with the weekday-letter inks, the selected day's `#CCCCFF`
fill and digit ink, and the leftmost day column's red day digits there.
`--color-dialog` opens a `kdialog` color picker whose basic-color swatch grid, sunken value
fields and push buttons the engine draws with the theme's palette and the shipped push-button
art, captured at the same 480x360 size; the color gate
(`tests/test_render_surface.py::TestColorDialogRender`) pins the flat window face, the
swatch grid's first row's `#000000` lead cell and its `#AA0000` neighbour with the
window-face gap between them, the value field's `#999999` shadow over the sunk `#000000`
outline and `#FFFFFF` face, and a push button's raised frame with its `#DDDDDD` face cell
there.
`--icon-dialog` opens a `kdialog` icon chooser whose top-row search field's sunken
line edit and whose sunken icon-grid field the engine draws with the theme's palette
and the shipped field art, captured at the same 480x360 size; the icon gate
(`tests/test_render_surface.py::TestIconDialogRender`) pins the flat window face,
the icon-grid field's top edge's #999999 shadow row over the sunk `#000000`
outline and `#FFFFFF` face, the search field's `#999999` shadow arm over its sunk
outline and `#FFFFFF` face, and a push button's raised frame with its `#DDDDDD`
face cell there. The grid's icon cells' picture content is the fallback icon
theme's and stays deliberately unpinned, and the search field's blinking caret
column sits outside every band.
`--lineedit-dialog` opens a `kdialog` input box whose empty line edit the engine sinks
with the theme's sunken-field art, captured at the same 480x360 size; the line-edit gate
(`tests/test_render_surface.py::TestLineInputDialogRender`) pins the field's sunken bevel
right of the caret and the OK button's push-button frame there.
`--progressbar-dialog` opens a `kdialog` progress meter whose at-rest trough the engine
draws as the theme's `progress` element art, captured at the same 480x360 size; the helper
daemon `kdialog_progress_helper` shows it (kdialog execs the helper for a progress dialog
and its launcher exits, where the helper stays for the session script to capture), and the
progressbar gate (`tests/test_render_surface.py::TestProgressbarDialogRender`) pins the
trough's flat face between its outline rows, its #FFFFFF top/left bevel arms and its
#999999 bottom/right arms there.
`--slider-dialog` opens a `kdialog` slider whose at-rest thumb the engine draws with the
theme's `slidercursor` art at the trough's left end and whose trough the engine paints flat
through the theme's `slider` interior art, captured at the same 480x360 size; the slider gate
(`tests/test_render_surface.py::TestSliderDialogRender`) byte-compares the thumb cell 1:1 with
the shipped art and pins the trough's flat face between its 1px black boundary rows there.
`--textbox-dialog` opens a `kdialog` text box whose vertical scrollbar the engine draws with
the theme's scrollbar art (the raised `scrollbarslider` handle with its `grip` indicator, the
`slider`-element trough and the `arrow`-element buttons), captured at the same 480x360 size;
the scrollbar gate (`tests/test_render_surface.py::TestTextboxDialogRender`) pins the handle's
outline-and-bevel bands and grip bars, the disabled #999999 up triangle and the enabled
#000000 down triangle, and the trough's flat #EEEEEE interior below the resting handle there.
`--gtk-dialog` opens a zenity text-entry dialog: zenity is a GTK 4 client, so with no
theme-name CSS switch it wears the theme through the selection the render publishes into the
scratch config home (`gtk-4.0/settings.ini` theme-name keys and the user-css `@import` of the
installed sheet), and the render captures it at the same 480x360 size. In this render mode the
GTK 4 dialog gate (`tests/test_render_surface.py::TestGtkDialogRender`) pins the rendered entry-field
cell 1:1 against the shipped art, along with the action-button row, Cancel button and CSD shell
edge; it also checks capture-level invariants. The fourteen dialog modes cannot be combined. In each mode the scratch session links its own home's
`themes/` onto the installed theme directory, because Kvantum looks there under the
literal `$HOME/.local/share/themes/` path.
`--inactive-dialog` opens two `kdialog` message boxes with two distinct fixed titles and
captures the pair at the same 480x360 size: the session reads forced-geometry window
rules that place the two windows side by side, and KWin activates the newest one, so the
captured surface shows the unfocused window — the earlier-spawned one, on the left — drawn
with the inactive decoration art; the inactive gate
(`tests/test_render_surface.py::TestInactiveDialogRender`) pins that window's outline
ring, recoloured client edge, flat bar and title ink there.
`--file-dialog` opens a `kdialog` file chooser (KDE's KIO file dialog) whose places
sidebar, file list view, toolbar and name-filter surfaces the engine draws with the theme's
palette and the shipped field and button art, captured at the same 480x360 size; the chooser
opens on the scratch session's fixed `Documents` directory holding exactly `alpha.txt`,
`bravo.txt` and `delta.rtf`, so the listing it shows is deterministic. The file-dialog gate
(`tests/test_render_surface.py::TestFileDialogRender`) pins the chooser's frame and title-bar
bands, the title-bar boxes and pinstripes, the panels' sunken borders, the selected places row,
the Name and Filter fields, the toolbar and bottom buttons, the list panel's column-header band
with its dividers and style-drawn sort arrow, the file rows' `#FFFFFF` and `#EEEEEE` band faces
with each per-file type-icon cell, the empty rows' flat face, the places sidebar's two group
headers, the Home entry's folder icon cell and the two device entries' drive icon cells, the
entries' live label bands, and both capacity-bar troughs with their caps, edge column and
left-anchored fills; the caption glyphs, the file names, the group-header and entry-label glyphs
and the clock-dependent date column stay live ink, each capacity bar's fill extent stays
unpinned because it is the host filesystem's live used-space total (session writes can move the
fill/free boundary between runs), and the icon art remains the fallback icon theme's.
`--desktop` opens the themed Plasma shell itself (`plasmashell`, the 640x400 virtual
session's only client) so the flush 20px top panel the look-and-feel layout builds — the
menu bar with its clock and window list — paints into the capture; the scratch session
selects the look-and-feel (`[KDE] LookAndFeelPackage` in the scratch `plasmarc` and
`kdeglobals`) and defaults to a 30 s settle and a 180 s timeout because plasmashell's
first start imports the layout. The desktop gate
(`tests/test_render_surface.py::TestDesktopRender`) pins the bar's Platinum structure — the
white top row, the `#DDDDDD` face rows, the 14x10 raised leftmost mark, the empty corridor
before the bar's right half and the two bottom rules — while the bar's right half (tray
icons, clock digits, shell label) and the desktop area below the bar stay deliberately
unpinned. `--splash` opens the look-and-feel's own startup splash fullscreen at 640x400, and
the splash gate (`tests/test_render_surface.py::TestSplashRender`) pins the flat field, the
bevel and panel boxes, the logo cell as measured, the wordmark ink and the track's
left-anchored fill, while the fill's extent — the splash engine's stage clock — stays
deliberately unpinned.

### Staging packages

To inspect installed package paths without selecting the theme in your session, stage an install
into a scratch root:

```sh
stage_dir=$(mktemp -d)
make install DESTDIR="$stage_dir" XDG_DATA_HOME=/usr/share INSTALL_PACKAGES='color-scheme gtk'
```

The scheme lands at `$stage_dir/usr/share/color-schemes/MacOS8.colors` and the GTK 3 and GTK 4
sheets and assets land under `$stage_dir/usr/share/themes/org.macos8.desktop/` (`index.theme`,
`gtk-3.0/gtk.css`, `gtk-4.0/gtk.css` and `assets/`). `/usr/share` here is the data-home suffix
inside the scratch root — `DATA_HOME` is `DESTDIR` followed by `XDG_DATA_HOME` — not a request to
install into the live system.

`INSTALL_PACKAGES` takes a space-separated list of the package families the Makefile knows:
`color-scheme`, `look-and-feel`, `desktop-theme`, `aurorae`, `wallpaper`, `icon-theme`,
`kvantum`, `fonts` and `gtk`. Omit the selector and the install copies every family; name a
subset and the install copies only that subset into the scratch root. A subset install is
additive: staging another family into the same scratch root later copies its files beside what
is already there and deletes nothing from earlier installs.

`make install` copies files into the destination and changes no selection or setting anywhere;
applying a selection is `make apply`'s job, which refuses to run with a non-empty `DESTDIR`
because a staged tree is for inspection, not for pointing the running session at. When you are
done inspecting, remove the scratch root yourself (`rm -rf -- "$stage_dir"`); nothing else
tracks it.

### Removing the theme

Choose another global theme in System Settings, then clear the individual selections before
deleting the installed packages. These commands remove this theme's selections or files; they do
not restore earlier settings or backups.

| Command | Effect and remaining action |
| --- | --- |
| `make remove-gtk` | Clears this theme's GTK selection and marker CSS. Existing GTK backups remain; restart GTK applications. |
| `make remove-firefox` | Removes this theme's sheets and preference block from the active profile. To target another profile, use `FIREFOX_PROFILE=/absolute/profile make remove-firefox`. Restart Firefox. |
| `make remove-cursor` | Removes this theme's cursor link but leaves the cursor selection. If it still names `org.macos8.desktop`, reset it with `plasma-apply-cursortheme breeze_cursors`. |
| `make remove-kvantum` | Clears only this theme's Kvantum engine selection (`[General] theme` in `kvantum.kvconfig`). A foreign theme name and the rest of the file remain; restart Qt applications. |
| `make uninstall` | Deletes installed theme packages and leaves user configuration in place. It also removes the theme-id directories it emptied under `themes/` (the shared directory and its `Kvantum/` parent); a directory still holding a file the theme did not install survives. This removes directories the install created, not user configuration. Run after clearing selections; it does not remove the cursor link or change keyboard mappings. |

To reselect the installed Plasma settings without installing packages or applying the other
theme surfaces, run `make apply-plasma`. Install first with `make install`; it requires Python
3.10+, `lookandfeeltool`, `plasma-apply-colorscheme`, `plasma-apply-desktoptheme` and
`kwriteconfig6`. It preserves panels, attempts Kvantum selection when available (a non-default
`${XDG_DATA_HOME}` prints a note naming the limitation, as the Installing section describes),
and the splash change appears at the next login.

#### Restoring personal GTK 4 CSS

When `make apply` replaced a nonempty foreign `gtk-4.0/gtk.css`, it first copied that stylesheet
beside itself and printed a note naming both paths:

```
apply_gtk: note: backed up <your gtk-4.0/gtk.css> to <the new backup> before replacing it
```

`make remove-gtk` keeps them: it deletes only the marker-led sheet this theme wrote and leaves
a foreign `gtk.css` alone, so finish that removal successfully before restoring anything.

Backup candidates are `gtk-4.0/gtk.css.bak` and, when several replacements happened, the
unused-name siblings `gtk.css.bak.1` and up, all under your config home (`$XDG_CONFIG_HOME` when
it is an absolute path, otherwise `$HOME/.config`). A numbered suffix only means the plain name
was already taken when another apply made a backup — it is the next unused filename, not a
chronology, and the largest number is not the newest edition. Read the candidates and choose by
contents.

Copy the chosen backup back at the console; `cp -i --` preserves the backup and prompts before
replacing an existing destination. Quote every path so spaces survive:

```sh
cp -i -- "/absolute/path/to/gtk-4.0/gtk.css.bak" "/absolute/path/to/gtk-4.0/gtk.css"
```

If a foreign `gtk.css` survived the removal, it may hold edits newer than any backup, so read it
before replacing it. Restart running GTK applications afterward so they reload the restored
stylesheet.

This restores the user CSS alone: it does not restore the theme name your `gtk-3.0/settings.ini`
or `gtk-4.0/settings.ini` carried before applying (`make remove-gtk` clears its selection and
leaves the rest of the file alone), so choose a preferred GTK theme separately when you want
one.

## Generating the wallpaper

`python3 tools/make_wallpaper.py` rewrites the wallpaper package's images in
theme/wallpapers/org.macos8.desktop/contents/images/ as a solid `#CCCCCC` tile, an original
neutral placeholder rather than a crop of the reference desktop. The output is deterministic,
so re-running it rewrites identical bytes. It refuses an images directory that resolves outside
the repository — a checked-in symlink — so the generated images stay inside the wallpaper
package. `PLACEHOLDERS.md` tracks this temporary artwork.

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

`.github/workflows/ci.yml` runs `make check` and `make check-references` on
pushes and pull requests, on Python 3.13 with a checkout with Git LFS images
materialized; the Makefile's targets still require Python 3.10 or newer at run
time. Its check job also installs the render gate's five Plasma tools
(`dbus-run-session`, `kwin_wayland`, `plasmawindowed`, `spectacle`,
`plasma-apply-colorscheme`), the `kdialog` client the gate's checkbox, combobox, line-edit, menu,
calendar, color, progressbar, slider and textbox dialog renders open, and the `zenity` client its
GTK
dialog render opens, so `make check` reaches the rendered-pixel gates, including the kdialog and
GTK dialog renders. Their
software-renderer guard still skips captures in the workflow environment; installed tools
are prerequisites, not proof that rendered pixels were compared. See [Running checks](#running-checks)
for the guard conditions and GPU-host guidance. Run those same commands locally for parity
with the workflow's check steps.

`sources.txt` is the provenance record for the images. After adding or renaming a screenshot, run
`python3 tools/check_references.py`: it fails if the record and the files on disk disagree (a
missing file, an unmaterialized Git LFS pointer, a file whose bytes are not a PNG/JPEG/GIF/WebP
image, an image with no entry, a malformed or duplicate entry) or if a source URL is not a
well-formed absolute URL (a bad scheme, raw whitespace or control characters, an authority
naming no host, or a malformed path, query or fragment, except for a `file://` URL).
`python3 tools/check_references.py --self-test` exercises the checker itself.
`make check-references` runs the self-test and then the repository check; it needs the Git LFS
images materialized, so it stays separate from `make check`.

### Troubleshooting the reference set

Each problem is printed on its own line. A record problem names its line as
`macos8.6-screenshots/sources.txt:<line>`; a file problem names the image instead.
Map a diagnostic to its next action:

| Diagnostic | Cause and next action |
| --- | --- |
| `... is an unmaterialized Git LFS pointer ...` | The file holds an LFS pointer, not the image bytes. Run `git lfs install` and `git lfs pull`, then `make check-references` again. |
| `... does not exist in .../macos8.6-screenshots/` | A declared file is absent — an incomplete checkout or a wrong filename in the record. Check the checkout, and compare the declared filename against the file on disk; fix the record only if the filename is genuinely wrong. Do not delete the provenance record to silence this: the record is the attribution trail for the set. |
| `image has no entry in sources.txt` | A file in the reference directory has no provenance record. Add one line for it: `filename \| source URL \| version label`. The filename is a bare name inside `macos8.6-screenshots/` (no path), the URL cites where the image came from, and the label is the evidence-based version string — see [Reference screenshots](#reference-screenshots) for the retail/beta labelling policy rather than restating it here. |
| `expected 3 fields ...`, `empty field in entry`, `duplicate entry for ...`, `source URL ...` | The record line is malformed, duplicate, or cites a URL that is not a well-formed absolute URL. Fix the record line the diagnostic names; it prints `sources.txt:<line>`, and a duplicate names the line of the first entry too. |
| `... is not a PNG, JPEG, GIF or WebP image; it may be an HTML error page or a truncated download` | The file's leading bytes match no known image signature. Inspect the download for an HTML error response or truncation and obtain the intended reference again; changing the file's extension does not change its bytes. |
| `... ends without the PNG IEND trailer`, `... ends without the JPEG EOI marker`, `... ends without the GIF trailer byte`, `... declares N RIFF bytes but holds M`; it may be a truncated download | The file's leading bytes match a known image format, but the stream stops before that format's end marker, so the download was cut short yet still looks like an image to the signature check. This diagnostic is a bounded structural check — the file's last bytes and, for WebP, its declared RIFF size — not a full decode. Obtain the intended reference again with a complete download and re-run the check. |
| `... points outside .../ (a symlink escape)` | A symlink in the reference set leads outside the reference directory, or the reference directory itself resolves outside the repository. Replace the symlink with the real file or directory it should name. |

A file that cannot be read at all — a read error, a non-UTF-8 `sources.txt`, a `sources.txt`
over the 1 MiB record limit, or a missing `sources.txt` — is reported directly; restore the
file it names.

The checker inspects signatures, not pixels: a pass means the bytes match a known image
format and every record line parses. It does not establish that an image decodes completely,
that a retail-labelled image is authentic, or that any pixel matches — those are the
[sampling](#sampling-reference-pixels) and [fidelity](#fidelity-checking) gates' work, on the
evidence each image actually carries. `--self-test` exercises the checker against its built-in
fixtures; it validates the checker, not the repository images. Run it alone or through
`make check-references`, which follows it with the repository check.

Exit statuses differ between callers. Direct `python3 tools/check_references.py` returns 0 when
the check or self-test passes (and for `--help`), 1 when the reference set has problems or a
self-test case misbehaves, and 2 for an unrecognized argument. GNU Make reports its own
recipe-failure status for `make check-references`; the checker's problem lines above appear in
the recipe's output either way.

## Sampling reference pixels

### Choosing a sampling mode

Choose a command based on the measurement you need. These commands use a beta reference
screenshot to demonstrate the sampler; it is not retail palette evidence. Choose coordinates
and region sizes for the surface you are measuring. Coordinates are absolute image pixels;
`--width` and `--height` set the sampled region starting at that coordinate, and both default
to 1. The reference PNGs are stored with Git LFS; materialize them as described in
[Validating the reference set](#validating-the-reference-set). Run `python3 tools/sample.py --help`
for the complete option list. JPEG reference screenshots are readable directly: the sampler
decodes a JPEG input once with ImageMagick's `convert` into a private temporary PNG and
samples it like any PNG, while `--alpha` and `--match-alpha` need a PNG input because JPEG
carries no alpha channel. For common refusals, see [Troubleshooting a sample](#troubleshooting-a-sample).

| Task | Command | Result |
| --- | --- | --- |
| Read one pixel | `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5` | RGB and hex values |
| Rank a small region's palette | `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --width 4 --height 4 --histogram --top-colors 3` | Up to three colors, ranked by count |
| [Locate dominant palette colors](#sampling-palette-locations) | `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --width 4 --height 4 --histogram --top-colors 3 --color-bounds --color-positions --color-centroids --json` | Up to three ranked colors with absolute enclosing bounds, first row-major positions and mean pixel coordinates |
| Measure vertical color runs | `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --height 4 --runs` | Run colors, start coordinates, and lengths |
| [Page through border color runs](#sampling-run-pages) | `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --height 40 --runs --max-runs 5 --run-offset 0 --run-count --json` | First five vertical runs and the full-region run count |
| Locate an exact color | `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --width 4 --height 4 --find-color '#63639C'` | Match count and enclosing bounds |

Bounds can enclose disconnected occurrences, and a centroid is an arithmetic mean that need not
be a pixel of that color.

### Sampling options

Jump to an option family:

- [Pixel and rectangle samples](#pixel-and-rectangle-samples)
- [Histogram options](#histogram-options)
- [Color search options](#color-search-options)
- [Scanline run options](#scanline-run-options)

#### Pixel and rectangle samples

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

Pass `--json` to emit one structured JSON object instead. `image` retains the original image
argument, `image_width` and `image_height` describe the full image, `region` records the requested
rectangle, and `pixels` lists absolute coordinates in row-major order; a single pixel has the
same schema:

```sh
$ python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --json
{"image": "macos8.6-screenshots/boot2_betawiki.png", "image_width": 240, "image_height": 180, "region": {"x": 5, "y": 5, "width": 1, "height": 1}, "pixels": [{"x": 5, "y": 5, "rgb": [99, 99, 156], "hex": "#63639C"}]}
```

Pass `--alpha` for ordinary pixel and rectangle samples to include each pixel's
alpha byte (255 when the PNG has no transparency). RGB remains unchanged even
when alpha is zero. The flag adds `alpha` to JSON pixel records and `alpha=N`
to text pixel lines. With `--runs`, alpha is included in run equality, so
adjacent pixels merge only when both RGB and alpha match; JSON run records add
`alpha`, and text appends `alpha=N` after the run length. RGB under transparent
pixels is preserved without compositing. With `--histogram`, `--alpha` counts
RGBA colors, sorts ties by RGBA tuple, and adds `alpha` to JSON colors or
`alpha=N` after text counts; opaque images use alpha 255. The flag cannot be
combined with `--find-color`.

Coordinates are plain ASCII integers and `--width`/`--height` must be at least 1; a
coordinate or region outside the image, a missing file, or an unreadable PNG exits 2
with a diagnostic naming the coordinate, region, image size or path. A repository image
path that resolves outside the repository (a checked-in symlink) is refused by name
before it is read, so a private image's pixels cannot be sampled; a path outside the
repository is read as before.

#### Histogram options

Pass `--histogram` to count the RGB colors in the requested rectangle instead
of listing its pixels. Counts sort from largest to smallest, with RGB tuple
order breaking ties; with `--alpha`, distinct RGBA tuples sort by RGBA order.
Combine it with `--json` for a `colors` array containing
`rgb`, `hex` and `count` fields:

```sh
$ python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --width 3 --height 2 --histogram --json
{"image":"macos8.6-screenshots/boot2_betawiki.png","image_width":240,"image_height":180,"region":{"x":5,"y":5,"width":3,"height":2},"colors":[{"rgb":[99,99,156],"hex":"#63639C","count":6}]}
```

Add `--top-colors N` with `--histogram` to limit the displayed palette while
still counting the complete region. It adds `total_colors` (the distinct-color
count before truncation) and `omitted_pixels` (region pixels not represented
in emitted colors) to JSON; text appends the same totals. Both fields appear
even when the limit includes every color.

Counts retain their full-region values, and ties keep ascending RGB ordering.
This limits report size; decoding and counting still cover the complete
region. Without the option, the complete histogram is printed.

Add `--color-offset K` with `--top-colors N` to page through the ranked
histogram after named-color exclusions and count/fraction filters. Ranking is
descending count, then ascending RGB or RGBA tuple; explicit zero selects the
first page. Named-color inclusion and exclusion, plus count and fraction
filters, run before paging. JSON adds `color_offset` and text prints
`color offset: K`. Totals and fractions retain their full-region meanings, and
omitted pixels include filtered colors, skipped colors and trailing colors.
Selection stores at most `min(K + N, distinct color count)` entries.

```sh
python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 0 0 --histogram --top-colors 2 --color-offset 1 --json
```

Add `--min-color-count N` with `--histogram` to omit colors whose count is
below N. The cutoff is inclusive and runs before `--top-colors`. JSON and text
include `total_colors` and `omitted_pixels` whenever either option is used;
the distinct-color total is measured before filtering, and omitted pixels
include filtered and truncated colors. Fractions retain the full-region
denominator, while spatial diagnostics describe only emitted colors. A cutoff
larger than the region area returns an empty palette and marks the full region
omitted.

Add `--max-color-count N` with `--histogram` to omit colors occurring more
than N times. The inclusive cutoff combines with minimum count, minimum
fraction and named-color exclusions before `--top-colors`; contradictory
minimum and maximum counts are refused when the minimum exceeds the maximum. Explicit use reports the
original `total_colors` and `omitted_pixels`, even when every color remains.
Fractions still use the full region area, and spatial diagnostics describe
only emitted colors.

Add `--min-color-fraction F` with `--histogram` to omit colors whose share of
the requested region is below F (0 through 1 inclusive). Filtering runs before
`--top-colors` and combines with `--min-color-count`; both predicates must pass.
The share uses the full region area, and explicit filtering reports the original
`total_colors` and `omitted_pixels`. At F=0 the palette is unchanged.

Add `--max-color-fraction F` with `--histogram` to omit colors whose share of
the requested region is above F (0 through 1 inclusive). This inclusive cutoff
combines with minimum fraction, count filters and named-color exclusions before
`--top-colors`. A minimum above the maximum is refused before image reading. The
share uses the full region area, including pixels later omitted by other
filters. Explicit use reports the original `total_colors` and `omitted_pixels`,
and spatial diagnostics describe only emitted colors.

For color count, color fraction, scanline run length, horizontal match-run
length and vertical match-run length, a supplied minimum above its paired
maximum exits 2 before image reading with an error naming both flags and
values. Equal bounds are valid and inclusive; valid windows with no qualifying
values still produce an empty result.

```sh
python3 tools/sample.py missing.png 0 0 --runs --min-run-length 3 --max-run-length 2
python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --width 4 --runs --min-run-length 4 --max-run-length 4
```

Add repeatable `--exclude-color RRGGBB` with `--histogram` to omit named RGB
colors before minimum-count, minimum-fraction and top-color selection. Values
accept six hexadecimal digits with optional `#` and are case-insensitive.
With `--alpha`, every opacity variant is excluded, including stored RGB under
zero alpha. The original distinct-color total and full-region denominator are
preserved; explicit exclusions report totals even when a named color is absent.
Omitted pixels include exclusions and other filters without double counting.
Spatial diagnostics apply only to emitted colors.

Add repeatable `--include-color RRGGBB` with `--histogram` to retain only named
RGB colors. Values accept six hexadecimal digits with optional `#` and are
case-insensitive. Inclusion is applied before exclusions, count/fraction
filters and top-color pagination; exclusions win when a color appears in both
lists. With `--alpha`, each opacity variant of an included RGB value is
retained independently, including stored RGB beneath zero alpha. The original
distinct-color total and full-region denominator are preserved, and explicit
inclusion reports totals even when it matches no colors or the full palette.
Omitted pixels include every filtered color, and spatial diagnostics apply
only to emitted colors.

Add `--color-fractions` with `--histogram` to add each emitted color's share
of the complete requested region (`count / width / height`). JSON color
records gain a numeric `fraction`; text appends `fraction=VALUE`. Fractions
use ordinary Python float formatting and are not rounded. With `--top-colors`,
the denominator still includes pixels omitted from the displayed palette.

Add `--color-cumulative-fractions` with `--histogram` to report how much of
the complete requested region the displayed palette explains as colors
accumulate. Each emitted color gains its running pixel count divided by the
full region area, accumulated in report order with integer counts so the last
color on a complete page reaches exactly `1.0`. Coverage is page-local:
excluded, filtered, skipped and trailing colors never enter the numerator.
JSON color records gain a numeric `cumulative_fraction`; text appends
`cumulative_fraction=VALUE` after the optional `fraction` and before
position and centroid fields. The option works independently of
`--color-fractions`; with `--top-colors`, the denominator still includes
pixels omitted from the displayed page.

<a id="sampling-palette-locations"></a>

Add `--color-bounds` with `--histogram` to report each emitted color's
smallest enclosing rectangle, using absolute image coordinates. The bounds
include disconnected occurrences and do not imply a solid rectangle. With
`--top-colors`, bounds are calculated only for colors shown; counts and the
top-color summary still cover the full region. `--alpha` keeps different
opacity values separate. JSON color records gain a `bounds` object, and text
appends `bounds=X,Y,W,H` after each color's existing fields.

Add `--color-positions` with `--histogram` to report the first row-major
occurrence of each emitted color, using absolute image coordinates. JSON color
records gain a `position` object with `x` and `y`; text appends
`position=X,Y`. Cropping limits the search to the requested region, and
`--alpha` keeps opacity variants separate. When combined with `--color-bounds`,
both diagnostics share one positioned traversal.

Add `--color-centroids` with `--histogram` to report each emitted color's
arithmetic mean pixel coordinate in absolute image coordinates. JSON color
records gain a `centroid` object with `x` and `y`; text appends
`centroid=X,Y`. Coordinates use integer pixel indices without a half-pixel
offset. Cropping and `--alpha` determine the sampled group, and `--top-colors`
limits reported colors while retaining all occurrences of each emitted color
in its centroid. Centroids share one positioned traversal with bounds and
positions.

Add `--row-color-counts` with `--histogram` to report how many distinct colors
each region row holds. The array lists one count per crop row in top-to-bottom
order, grouped like the emitted colors (RGB alone, or RGBA with `--alpha`, which
keeps opacity variants apart while a transparent pixel still contributes its
stored RGB). Counts cover the complete region, so displayed-palette filters and
`--top-colors` paging never change them. JSON adds `row_color_counts`, and text
adds a `row color counts:` line after the color list and before the totals.

Add `--column-color-counts` with `--histogram` to do the same for region
columns, one count per crop column in left-to-right order. JSON adds
`column_color_counts`, and text adds a `column color counts:` line after the
optional `row color counts:` line. Omitting both options adds neither count,
neither line and no traversal.

#### Color search options

Pass `--find-color '#63639C'` to count exact RGB matches and report their
smallest enclosing bounds. Bounds use absolute image coordinates, include
disconnected matches, and do not imply that every pixel inside the rectangle
matches. Add `--json` for a `match` object with `rgb`, uppercase `hex`, `count`
and `bounds` (`null` when absent):

```sh
python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 0 0 --width 240 --height 180 --find-color '#63639C' --json
```

Add `--color-tolerance N` to include pixels whose red, green and blue channel
differences are each at most N (0–255). This helps locate colors affected by
rendering or capture variation; alpha is ignored. The option requires
`--find-color`. When supplied, including as `--color-tolerance 0`, its value
appears in the text and JSON match report; omitting it preserves exact-match output.
Add `--match-alpha N` (0–255) to require an exact PNG alpha value as well as the RGB
predicate. It requires `--find-color`, preserves RGB bytes beneath transparency, and
uses alpha 255 for images without transparency. JSON adds `alpha` to `match`; text
prints `alpha: N` after the optional tolerance. RGB tolerance never relaxes this alpha
match. This option filters matches and can be combined with `--color-tolerance`, but
not with `--alpha`.

Add `--match-pixels N` (1–1000) with `--find-color` to list the first N
matching coordinates in row-major order. Coordinates are absolute image
positions within the requested region. Matching count and bounds still cover
the full region; JSON adds `pixels` and `omitted_pixels` to `match`, while
text prints the retained coordinates and omitted count. The option uses the
same RGB tolerance and exact-alpha filters as the match count.

Add `--match-pixel-offset N` with `--match-pixels` to list a later page of the
same row-major match sequence. The offset counts matching pixels, not scanned
pixels; `--match-pixel-offset 0` selects the original first page. JSON adds
`pixel_offset` when explicitly requested, and text prints `pixel offset:` before
the coordinate list. `omitted_pixels` includes both skipped matches and matches
after the current page. Count, bounds and optional match diagnostics still cover
the full region, and an offset at or beyond the match count returns an empty
coordinate list.

Add `--match-fraction` with `--find-color` to report the match count divided
by the full requested region area. JSON adds numeric `fraction` to `match`;
text prints `fraction:` after `count:`. It uses the same RGB tolerance and
exact-alpha filters, and `--match-pixels` does not truncate its numerator.

Add `--match-centroid` with `--find-color` to report the arithmetic mean of
matching pixel coordinates. JSON adds `match.centroid` with absolute `x` and
`y` values, or `null` when no pixels match; text prints `centroid: X,Y` or
`centroid: none` after bounds. Pixel indices are used without a half-pixel
offset. Tolerance and exact-alpha filters apply, and `--match-pixels` does not
truncate the centroid calculation.

Add `--match-runs` with `--find-color` to report maximal contiguous horizontal
segments matching the same RGB tolerance and exact-alpha predicate. JSON adds
`match.runs` records with absolute `x`, `y` and `length`; text prints the same
records on a `matching runs:` line. Segments are ordered by row then column,
stop at each row boundary, and merge adjacent matches even when their RGB
values differ within tolerance. The report covers the full region independently
of `--match-pixels`; potentially large output is opt-in.

Add `--match-run-count` with `--find-color` to report the number of maximal
horizontal matching segments as `match.run_count` in JSON or a
`matching run count:` text line. It counts the full region using the same RGB
tolerance and exact-alpha predicate, independent of coordinate paging and run
length filters. The run list remains omitted unless `--match-runs` is requested.

Add `--min-match-run-length N` with `--match-runs` to omit horizontal match
segments shorter than `N` pixels. The inclusive cutoff filters only the
reported list; match counts and other full-region diagnostics, including the
longest-run summary, still use every matching pixel. A cutoff above the longest
segment reports an empty `match.runs` array (or `matching runs: []` in text).

Add `--max-match-run-length N` with `--match-runs` to omit horizontal match
segments longer than `N` pixels. The inclusive cutoff filters completed
segments; match counts and summaries still use the full search. Minimum and
maximum cutoffs combine inclusively. A minimum above the maximum is refused
before image reading.

Add `--max-match-runs N` with `--match-runs` to report only the first `N`
eligible horizontal intervals in row-major order after both length filters.
Pass `--match-run-offset K` with `--max-match-runs` to skip K eligible intervals
after both length filters and report the next page. JSON adds `match.run_offset`
and text prints `matching run offset: K` immediately before the list. The omitted
count in `match.omitted_runs` includes skipped and trailing eligible intervals;
text prints `omitted matching runs: N` immediately after the interval list,
including zero. Match counts and longest-run summaries still use the full search.
When a cap is supplied, completed intervals are filtered and paged as they are
collected, so retained horizontal interval storage is bounded by the cap.
Without a cap, matching intervals are retained as before.
Omitting the offset adds no `match.run_offset` field or text line.

Add `--match-column-runs` with `--find-color` to report maximal contiguous
vertical segments using the same match predicate. JSON adds `match.column_runs`
with absolute `x`, `y` and `length`; text prints the records on a
`matching column runs:` line after any horizontal runs. Segments are ordered
by column then row, stop at each column boundary, and merge adjacent tolerance
matches even when their RGB values differ. They cover the full region
independently of `--match-pixels`; potentially large output is opt-in.

Add `--match-column-run-count` with `--find-color` to report the number of
maximal vertical matching segments as `match.column_run_count` in JSON or a
`matching column run count:` text line. It counts the full region with the same
RGB tolerance and exact-alpha predicate, independent of coordinate paging and
column-run length filters. The interval list remains omitted unless
`--match-column-runs` is requested; when both options are used, the count
appears immediately before the list.

Add `--min-match-column-run-length N` with `--match-column-runs` to omit
vertical match segments shorter than `N` pixels. The inclusive cutoff filters
only the reported list; match counts and diagnostics, including the longest
vertical-run summary, still use every matching pixel. A cutoff above the
longest segment reports an empty `match.column_runs` array (or
`matching column runs: []` in text).

Add `--max-match-column-run-length N` with `--match-column-runs` to omit
vertical match segments longer than `N` pixels. The inclusive maximum filters
only the reported list and combines with the minimum cutoff. A minimum above
the maximum is refused before image reading; match counts and longest-run
diagnostics still cover the full search for valid windows.

Add `--max-match-column-runs N` with `--match-column-runs` to report only the
first `N` eligible vertical intervals in column-major order, after both
inclusive length filters. JSON adds `match.omitted_column_runs`; text prints
`omitted matching column runs: N` immediately after the list, including zero.
Counts, longest-run summaries and other search measurements still cover the
full region. When a cap is supplied, the search runs one extra column-major
predicate scan over the already-decoded region, and completed vertical
intervals are filtered and paged as that scan collects them, so retained
vertical interval storage is bounded by the cap.

Pass `--match-column-run-offset K` with `--match-column-runs` and
`--max-match-column-runs` to skip K eligible vertical intervals in column-major
order after both length filters. JSON adds `match.column_run_offset`; text prints
`matching column run offset: K` before the list. The omitted count includes
skipped and trailing eligible intervals. Paging requires the cap and rides the
same bounded capped collection, so skipped eligible intervals are not
retained.

Add `--match-rows` with `--find-color` to count matching pixels in each row of
the requested region. JSON adds a dense `match.rows` array and text prints the
same array on a `matching rows:` line after interval reports. Index zero is the
region's first row; rows with no matches are included. Counts use the same RGB
tolerance and exact-alpha predicate and cover the full region regardless of
`--match-pixels`. The diagnostic is omitted unless requested.

Add `--match-columns` with `--find-color` to count matching pixels in each
column of the requested region. JSON adds a dense `match.columns` array and
text prints the same array on a `matching columns:` line after any matching
rows line. Index zero is the region's first column; columns with no matches
are included. Counts use the same RGB tolerance and exact-alpha predicate and
cover the full region regardless of `--match-pixels`. The diagnostic is
omitted unless requested.

Add `--match-row-bounds` with `--find-color` to report the smallest horizontal
interval enclosing matches on each row. JSON adds dense `match.row_bounds`
entries: `null` for an empty row, otherwise absolute `x` and inclusive `width`;
text prints the same array on a `matching row bounds:` line. Disconnected
matches enclose intervening pixels. The report covers the full region regardless
of `--match-pixels`, uses the same tolerance and exact-alpha predicate, and is
omitted unless requested.

Add `--match-column-bounds` with `--find-color` to report the smallest vertical
interval enclosing matches in each column. JSON adds dense `match.column_bounds`
entries: `null` for an empty column, otherwise absolute `y` and inclusive
`height`; text prints the same array on a `matching column bounds:` line.
Disconnected matches enclose intervening pixels. The report covers the full
region regardless of `--match-pixels`, uses the same tolerance and exact-alpha
predicate, and is omitted unless requested.

Add `--longest-match-run` with `--find-color` to report the longest contiguous
horizontal matching segment. JSON adds `match.longest_run` with absolute `x`,
`y` and `length`, or `null` when there are no matches; text prints
`longest matching run: X,Y,LENGTH` or `longest matching run: none`. Ties keep
the earliest row-major segment. The summary uses the same tolerance and exact
alpha filters, covers the full region regardless of `--match-pixels`, and does
not emit the full run list unless `--match-runs` is also requested.

Add `--longest-match-column-run` with `--find-color` to report the longest
contiguous vertical matching segment. JSON adds `match.longest_column_run`
with absolute `x`, `y` and `length`, or `null` when there are no matches; text
prints `longest matching column run: X,Y,LENGTH` or
`longest matching column run: none`. Ties prefer greater length, then the
lowest x and y. The summary uses the same tolerance and exact-alpha filters,
covers the full region regardless of `--match-pixels`, and does not emit the
full column-run list unless `--match-column-runs` is also requested.

#### Scanline run options

Pass `--runs` to group adjacent equal RGB values along one row or column.
Add `--alpha` to group by RGBA instead, distinguishing transparency boundaries
even when neighboring pixels have the same RGB values; an image without alpha
uses 255 for every run. RGB values remain uncomposited, including beneath
fully transparent pixels.
With `--height 1` (the default), traversal is horizontal; otherwise use
`--width 1` for a vertical scan. A two-dimensional region is rejected unless
`--run-axis horizontal` or `--run-axis vertical` selects parallel scanlines.
Horizontal scans visit rows top-to-bottom and pixels left-to-right; vertical
scans visit columns left-to-right and pixels top-to-bottom. Runs never cross
scanline boundaries, even when adjacent scanlines end and begin with equal colors.
For example, `--width 4 --height 3 --runs --run-axis vertical` reports four
independent top-to-bottom column scans. Add
`--json` to return the `axis` and traversal-ordered `runs`, each with its
absolute starting coordinate, `length`, `rgb` and `hex`:

```sh
$ python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --width 4 --runs --json
{"image":"macos8.6-screenshots/boot2_betawiki.png","image_width":240,"image_height":180,"region":{"x":5,"y":5,"width":4,"height":1},"axis":"horizontal","runs":[{"x":5,"y":5,"length":4,"rgb":[99,99,156],"hex":"#63639C"}]}
```

Use `--height` for a vertical scan:

```sh
python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --height 4 --runs
```

Pass `--min-run-length N` with `--runs` to omit completed color runs shorter than `N` pixels.
The inclusive cutoff is applied independently within each scanline; omitted runs do not join
separated runs of the same color. A minimum cutoff of 1 keeps the unfiltered result.
Pass `--max-run-length N` to omit completed runs longer than `N`; it combines
inclusively with the minimum cutoff after segmentation and does not join separated runs.
A maximum at least as large as the scanline keeps the unfiltered result.
If both bounds are supplied and the minimum exceeds the maximum, the sampler
exits 2 with an error naming both flags and values before reading the image.
Pass repeatable `--run-color RRGGBB` to retain runs whose RGB value is named;
values accept an optional `#` and are case-insensitive. Color selection follows
segmentation, so distinct adjacent selected colors and separated runs stay
separate; it combines with the inclusive length filters. With `--alpha`, runs
are still segmented by RGBA while selection matches RGB regardless of opacity.
Pass repeatable `--exclude-run-color RRGGBB` to omit runs with a named RGB
value after segmentation; values accept an optional `#` and are case-insensitive.
Exclusion ignores opacity and wins when the same value is also selected with
`--run-color`. It combines with the inclusive length filters and requires
`--runs`.

Pass `--run-count` with `--runs` to add a scalar run total alongside the list:
JSON gains a top-level `run_count` and text prints `run count: N` immediately
after the `axis:` line (after the `longest run:` line when `--longest-run` is
also given). The count is the complete unfiltered number of scanline
runs each scan produces — counted before `--run-color` selection,
`--exclude-run-color` and the inclusive length filters, including zero when a
scan yields none — with runs of different scanlines counted separately and the
count covering all scanlines of the region. What `runs` lists does not change;
omitting the flag omits the JSON key, the text line and the counting. The flag
requires `--runs`.

Pass `--scanline-run-counts` with `--runs` to add one run count per scanline
alongside the list: JSON gains a top-level `scanline_run_counts` and text
prints `scanline run counts: N, N, ...` immediately after the optional
`run count` line, before the run list. Each count is the same unfiltered
per-scanline total `--run-count` sums — taken before `--run-color` selection,
`--exclude-run-color` and the inclusive length filters — listed in scanning
order, top-to-bottom rows for the horizontal axis and left-to-right columns
for the vertical; every scanline yields at least one run, so the list is never
empty for a nonempty region. Filters change what `runs` lists but never the
counts; omitting the flag omits the JSON key, the text line and the counting.
The flag requires `--runs`.

Pass `--longest-run` with `--runs` to add the dominant scanline run as a
scalar: JSON gains a top-level `longest_run` mirroring one `runs` entry (`x`,
`y`, `length`, `rgb`, `hex`, plus `alpha` under `--alpha`) and text prints
`longest run: X,Y,LENGTH` immediately after the `axis:` line. The summary
covers every scan run of the region before `--run-color` selection,
`--exclude-run-color` and the inclusive length filters, resolving ties in
scanning order — top-to-bottom rows for the horizontal axis, left-to-right
columns for the vertical, and the earliest run within a scanline. Every
scanline yields at least one run, so the summary is never null. What `runs`
lists does not change; omitting the flag omits the JSON key, the text line and
the comparison. The flag requires `--runs`.

<a id="sampling-run-pages"></a>

For a longer vertical border scan, start with `--max-runs 5 --run-offset 0 --run-count --json`
as in the chooser above. Change the offset to 5 for the
next page. Offsets count eligible run slots, not pixels; a later page can be
empty. The cap limits displayed records, while the scan and requested
unfiltered run count cover the full region.

Pass `--max-runs N` with `--runs` to display only the first N eligible runs
across the complete scan in its existing row or column order. Named color
selection and exclusion plus inclusive run-length filters apply before this
prefix limit. JSON adds `omitted_runs`, and text prints `omitted runs: N`
after the displayed runs, including zero when the limit covers every eligible
run. This caps the retained report list; the scan continues so
`--run-count`, `--scanline-run-counts` and `--longest-run` retain their
unfiltered full-region meanings. Without the option, output is unchanged.
The option requires `--runs` and is distinct from `--max-run-length`, which
filters runs by their individual pixel lengths.

Pass `--run-offset K` with `--runs` and `--max-runs N` to page through eligible
runs without printing earlier pages. Color selection, exclusion and inclusive
length filters apply before the offset. The offset counts skipped eligible runs;
`omitted_runs` counts both skipped runs and eligible runs after the displayed
page. JSON adds `run_offset`, and text prints `run offset: K` before the run
list. An offset beyond the end returns an empty page. The option requires
`--max-runs` and is nonnegative.

### Troubleshooting a sample

| Symptom | What to do |
| --- | --- |
| The file is an unmaterialized Git LFS pointer | Follow [Validating the reference set](#validating-the-reference-set), including `git lfs install` and `git lfs pull`, to fetch the image bytes. |
| The path is missing or unreadable | Check the path named in the diagnostic and confirm you can read the file. |
| The pixel or region is outside the image | Correct `X`, `Y`, `--width` or `--height` to fit the image dimensions in the report. |
| JPEG decoding says `convert` is missing | Install ImageMagick and ensure its `convert` command is on `PATH`; PNG inputs need no converter. |
| An alpha option was requested for JPEG | Omit `--alpha` or `--match-alpha`, or use a PNG that actually has alpha. JPEG conversion cannot recover transparency that JPEG does not store. |
| An option dependency or min/max window is refused | Add the required mode or cap described in the [option families](#sampling-options), or correct the bounds so the minimum does not exceed the maximum. |

Reports and `--help` return status 0. A valid sample with no matching or retained values is still a successful empty report; an out-of-image pixel or region is refused instead. Handled usage, read and decode refusals return status 2. These are sampler statuses; fidelity comparison failures have their own status.

## Fidelity checking

`python3 tools/fidelity.py CANDIDATE REFERENCE` compares a rendered PNG surface against a
reference screenshot and reports mean absolute error, per-channel mean absolute error
(R, G, B, A), RMSE, worst per-channel delta and where it occurs, and the fraction of
differing pixels.
Pass `--candidate-crop X,Y,W,H` to crop the candidate and `--crop X,Y,W,H` to select a
surface region of the reference.
If a comparison refuses to run, see [Troubleshooting a comparison](#troubleshooting-a-comparison).
A JPEG candidate or reference is decoded once through ImageMagick's `convert` into a
private temporary PNG before the comparison, so the reference set's JPEG screenshots are
comparable directly; other non-PNG formats keep the decode refusal.

### Capturing a candidate

Capture the default Plasma calculator with `make render`, setting its output path with
`RENDER_OUTPUT`:

```sh
make render RENDER_OUTPUT=calculator.png
make render RENDER_MODE=checkbox-dialog RENDER_OUTPUT=checkbox.png
make render RENDER_MODE=desktop RENDER_OUTPUT=desktop.png
make render RENDER_MODE=splash RENDER_OUTPUT=splash.png
```

The Make target uses `RENDER_MODE` (`calculator` by default) to select the calculator, one of
the fourteen dialogs, the desktop menu bar, or the startup splash. The calculator capture defaults to 320x240; dialogs
are fixed at 480x360 and
require `kdialog` for checkbox, combo box, line edit, menu, radio list, calendar, color picker, icon
chooser, progress meter, slider, text box, the two-window inactive pair and the file chooser or
`zenity` for GTK; the desktop capture is fixed at 640x400 and requires `plasmashell`; the splash
capture is fixed at 640x400 and requires `ksplashqml`.
Direct Python commands remain available; each dialog flag must be used alone, and dialog captures
reject `--width`, `--height` and a non-default `--applet`:

| Surface | Command | Image size |
| --- | --- | --- |
| Checkbox dialog | `python3 tools/render_surface.py --checkbox-dialog checkbox.png` | 480x360 |
| Combo box dialog | `python3 tools/render_surface.py --combobox-dialog combobox.png` | 480x360 |
| Line edit dialog | `python3 tools/render_surface.py --lineedit-dialog lineedit.png` | 480x360 |
| Menu dialog | `python3 tools/render_surface.py --menu-dialog menu.png` | 480x360 |
| Radio list dialog | `python3 tools/render_surface.py --radiolist-dialog radiolist.png` | 480x360 |
| Calendar dialog | `python3 tools/render_surface.py --calendar-dialog calendar.png` | 480x360 |
| Color dialog | `python3 tools/render_surface.py --color-dialog color.png` | 480x360 |
| Icon dialog | `python3 tools/render_surface.py --icon-dialog icon.png` | 480x360 |
| Progress bar dialog | `python3 tools/render_surface.py --progressbar-dialog progressbar.png` | 480x360 |
| Slider dialog | `python3 tools/render_surface.py --slider-dialog slider.png` | 480x360 |
| Text box dialog | `python3 tools/render_surface.py --textbox-dialog textbox.png` | 480x360 |
| GTK dialog | `python3 tools/render_surface.py --gtk-dialog gtk.png` | 480x360 |
| Inactive dialog | `python3 tools/render_surface.py --inactive-dialog inactive.png` | 480x360 |
| File dialog | `python3 tools/render_surface.py --file-dialog file.png` | 480x360 |
| Desktop | `python3 tools/render_surface.py --desktop desktop.png` | 640x400 |
| Startup splash | `python3 tools/render_surface.py --splash splash.png` | 640x400 |

The calculator capture defaults to 320x240. Dialog captures need `kdialog` on `PATH` in the
kdialog modes and `zenity` in the GTK mode; the desktop capture needs `plasmashell` on `PATH`;
the splash capture needs `ksplashqml` on `PATH`;
see [Prerequisites](#prerequisites) for the render tools. To allow a slower calculator paint,
increase the settle wait and set a longer timeout (which must exceed settle):

```sh
python3 tools/render_surface.py --settle 12 --timeout 120 calculator.png
```

A longer wait does not guarantee a successful capture. Compare the candidate with the relevant
reference surface using the [fidelity checker](#fidelity-checking); use its crop options to
compare a region rather than assuming a full capture matches a reference screenshot.

### Troubleshooting a render

| Symptom | Check and next action |
| --- | --- |
| The diagnostic names a missing or unstartable executable. | Repair that executable or its `PATH` entry, then rerun the same command. The first missing required tool is named; a present but unstartable `make` or `dbus-run-session` is also diagnosed. |
| The capture is entirely black. | The window did not paint before capture. Check whether the paint needs more time and increase `--settle`; use the [slower-paint example](#capturing-a-candidate), with `--timeout` longer than `--settle`. A longer wait does not guarantee a capture. |
| The render timed out. | Check [Prerequisites](#prerequisites) and increase `--timeout` only as needed, keeping it longer than `--settle`. A missing `org.kde.plasma.calculator` applet is no longer an undiagnosed timeout cause: its own preflight refusal exits 2 before any session and names the applet id. |
| The render session exits nonzero. | Inspect the diagnostic's printed session log tail for the failing command. The log is in a temporary scratch directory and is removed with the session, so it is not a persistent report. |

Direct `python3 tools/render_surface.py` invocations return 2 for usage or preflight errors
(including missing tools and invalid timeout settings), and 1 for workflow failures. GNU Make
reports its own recipe-failure status for `make render`. Failure diagnostics include a bounded
log tail when a log is available. The software-renderer skip described in
[Running checks](#running-checks) applies to the automated pixel gates; it is separate from a
direct render failure.

### Comparing a region

When render tools are available and the software-renderer guard does not trigger, the
calculator title-strip gate compares these corresponding 80x22 rectangles:

```sh
python3 tools/fidelity.py calculator.png macos8.6-screenshots/aboutsystem_betawiki.png --candidate-crop 30,0,80,22 --crop 30,25,80,22
```

Use [Rendering a candidate](#rendering-a-candidate) to produce `calculator.png`; see
[Capturing a candidate](#capturing-a-candidate) for capture options, and
[Validating the reference set](#validating-the-reference-set) to materialize the images.
These coordinates belong to the documented calculator/title-strip gate, not arbitrary windows.
For another surface, choose corresponding rectangles independently in the two images; they must
have equal dimensions. `aboutsystem_betawiki.png` is the documented beta window-chrome proxy:
its relevant chrome is pixel-identical to the retail reference, as pinned by the
retail-equivalence test. It is not general evidence for retail palette values.

### Troubleshooting a comparison

| Symptom | Check and next action |
| --- | --- |
| The reference is an unmaterialized Git LFS pointer. | Follow [Validating the reference set](#validating-the-reference-set) to install Git LFS and materialize the image. |
| An input is missing or unreadable. | Check the path named in the diagnostic and confirm the file is readable. |
| A JPEG input is refused because `convert` is unavailable. | Install ImageMagick and verify `convert` is on `PATH`. |
| A PNG is refused during decoding. | Inspect the named image and provide a valid supported PNG input. |
| A crop extends beyond its image. | Correct that source's crop coordinates; see [Comparing a region](#comparing-a-region) for the two crop options. |
| The cropped images have different sizes. | Choose corresponding equal-size regions using [Comparing a region](#comparing-a-region). |

A completed comparison returns 0 when it passes and 1 when it reports a mismatch; use
[Choosing a diagnostic](#choosing-a-diagnostic) to inspect a mismatch. Usage and input
refusals return 2. `--quiet` suppresses comparison reports, so omit it when you need to see
the mismatch details. Direct CLI statuses differ from Make's recipe-failure status.

Add mismatch locations and RGBA values in JSON with:

```sh
python3 tools/fidelity.py calculator.png macos8.6-screenshots/aboutsystem_betawiki.png --candidate-crop 30,0,80,22 --crop 30,25,80,22 --worst-pixels 5 --explain-worst --json
```

The exit status is 0 when the comparison passes, 1 when it fails, and 2 for a usage or read error.

### Choosing a diagnostic

Append one of these options to the aligned-crop command above to choose the report that best
answers your question:

| Need | Additional options | Result |
| --- | --- | --- |
| [Find the enclosing mismatch rectangle](#fidelity-report-bounds) | None; this is the default report | Smallest bounds containing pixels beyond tolerance; unchanged gaps may lie inside. |
| [Inspect the most severe individual mismatches](#fidelity-report-worst-pixels) | `--worst-pixels 5 --explain-worst --json` | Ranked pixels with positions, RGBA values and channel differences. |
| [See horizontal mismatch segments](#fidelity-report-horizontal-runs) | `--difference-runs --max-difference-runs 20 --json` | Capped list of horizontal intervals. |
| [See vertical mismatch segments](#fidelity-report-vertical-runs) | `--difference-column-runs --max-difference-column-runs 20 --json` | Capped list of vertical intervals. |
| [Find row and column concentration](#fidelity-report-scanline-counts) | `--difference-rows --difference-columns --json` | Per-row and per-column mismatch counts. |
| [Attribute mismatches to channels](#fidelity-report-channel-counts) | `--channel-counts --json` | Per-channel counts; a pixel may count in multiple channels, so do not sum them. |
| [See the error-magnitude distribution](#fidelity-report-delta-histogram) | `--delta-histogram --json` | Counts grouped by each pixel's maximum absolute RGBA delta. |
| [See typical and tail error](#fidelity-report-delta-percentiles) | `--delta-percentiles --json` | Nearest-rank p50, p95 and p99 maximum RGBA deltas. |
| [Check the direction of channel drift](#fidelity-report-channel-bias) | `--channel-bias --json` | Signed mean candidate-minus-reference RGBA deltas. |
| [Find the worst error per channel](#fidelity-report-channel-maxima) | `--channel-maxima --json` | Maximum absolute delta for each RGBA channel. |

Interval coordinates are relative to the compared crops. See [Diagnostic reference](#diagnostic-reference)
for details about these reports and their fields.

These are raw-byte diagnostics: where applicable they include zero and sub-tolerance errors,
and none changes the comparison verdict. Opposite signed errors can cancel in channel bias.

Reported `x`/`y` positions are relative to the compared crops. `candidate_position` and
`reference_position` locate each result in the original images; `--explain-worst` gives both
pixels' RGBA values and their channel differences. A mismatch is a useful report with exit status
1; status 2 means usage or image reading failed. See the diagnostic reference below for other
reports.

### Diagnostic reference

<a id="fidelity-report-bounds"></a>

Add `--json` to emit the paths, crop rectangles, thresholds, full precision metrics and verdict
as one JSON object (for example, `python3 tools/fidelity.py render.png reference.png --json`).
The `metrics` object uses the field names from `tools/fidelity_metrics.py::Metrics`; crop-relative
dimensions, worst-delta coordinates, and `difference_bounds` describe the compared surfaces.
The bounds are `(x, y, width, height)` for the smallest rectangle containing pixels whose
maximum channel delta exceeds tolerance, or `null`/`none` when no pixel exceeds it.
The top-level `candidate_difference_bounds` and `reference_difference_bounds` translate that
rectangle into each source image's coordinates, using the corresponding crop origin (or zero).
Text output prints the same two source rectangles after the local bounds line.

A candidate or reference path inside the repository that resolves outside it (a checked-in
symlink) is refused by name before it is read, so a comparison cannot probe a private image;
a path outside the repository is read as before. Guarded PNG reads and crop-bounded row decoding
are handled by `tools/fidelity_sources.py`, called by the CLI in `tools/fidelity.py`.
Add `--quiet` to suppress the report and use only the exit status (0 pass, 1 comparison failure,
2 usage or read error) in a scripted gate. It can be combined with comparison diagnostics, which
are still calculated but not printed; `--quiet` and `--json` are mutually exclusive.

By default a run passes only when no pixel differs from the reference by more than `--tolerance`
(a per-channel delta; 0, i.e. byte-exact, unless given). Each pixel's alpha byte is compared
along with its red, green and blue bytes, so a transparent candidate cannot pass as an opaque
reference. `--max-mae F`, `--max-frac F` and `--max-differing N` set
aggregate budgets instead: when one is given, a run passes when each given budget is met —
`--max-mae` bounds the mean absolute error, `--max-frac` bounds the differing-pixel fraction, and
`--max-rmse` bounds root mean square error, and `--max-delta` caps the largest absolute RGBA
channel difference; `--max-differing` caps the absolute number of pixels whose maximum RGBA
channel delta exceeds `--tolerance` — and the default no-differing-pixel gate no longer applies.
`--longest-difference-run` reports the longest horizontal contiguous interval whose maximum raw
RGBA channel delta exceeds tolerance, with crop-relative `x`, `y` and `length`; ties use the
earliest row and then column. The JSON field is `longest_difference_run`, and an empty comparison
reports `null`. When combined with `--difference-runs`, it reuses those intervals.
`--longest-difference-column-run` reports the longest vertical contiguous interval under the same
comparison rule, with crop-relative coordinates; ties use the earliest column and then row. Its
JSON field is `longest_difference_column_run`, and an empty comparison reports `null`. When
combined with `--difference-column-runs`, it reuses those intervals.
<a id="fidelity-report-worst-pixels"></a>

The mean, RMSE and maximum-delta metrics use comparison raw bytes and are independent of
`--tolerance`; the differing-pixel fraction and the `--max-differing` count are measured beyond
`--tolerance`. RMSE is not a perceptual error measure. Add `--worst-pixels N` (1–1000) to list
the most severe mismatches, ranked by maximum RGBA channel delta with row-major tie ordering.
The listed `x`/`y` coordinates are relative to the compared, cropped surfaces. Each record also
includes `candidate_position` and `reference_position`, which add the corresponding crop origin
and point into the original images (an omitted crop has origin 0,0). Text lines show both source
positions too. With `--json`, the records appear in a `worst_pixels` array; the default output and
work remain unchanged.
Use `--worst-pixel-offset K` with `--worst-pixels N` to page through the same ranked list;
the offset is a nonnegative ASCII decimal integer. Ranking, tolerance and comparison metrics
are unchanged by pagination. Selection storage grows with `K + N`, capped at the compared image
area; decoding and comparison still process the requested images as before. An offset beyond the
available mismatches emits an empty `worst_pixels` array (or no records in text output).
Add `--explain-worst` to report the candidate and reference RGBA values at the comparator's
maximum-delta pixel, along with the absolute per-channel differences. Its `position` is relative
to the compared surfaces; `candidate_position` and `reference_position` add each crop's origin
and point into the original images. The diagnostic appears as `worst_pixel` in JSON or as a
JSON-formatted `worst pixel:` line immediately before the verdict. It is reported on passing
comparisons too, including identical images, where the selected position is `(0, 0)`.
<a id="fidelity-report-channel-counts"></a>

Add `--channel-counts` to report, per channel, how many compared pixels exceed `--tolerance`
on that channel alone. `--json` adds the counts as a top-level `channel_counts` object
and text prints one `channel differing pixels (R, G, B, A)` line immediately before the
verdict, on passing and failing runs alike. A pixel can contribute to several counts (a
tint change moves three channels at once), so the counts overlap and must not be summed
into a union; `metrics.differing` already holds that union count.
<a id="fidelity-report-delta-histogram"></a>

Add `--delta-histogram` to report every compared pixel once, grouped by its
maximum absolute RGBA channel delta from 0 through 255. The complete distribution
includes zero and deltas at or below tolerance, and is independent of the gate:
JSON adds `delta_histogram` records (`delta` and `count`), while text prints the
same array as one `delta histogram:` line immediately before the verdict. The
option reports on passing and failing comparisons; omitting it skips the scan
and leaves the default output unchanged.
<a id="fidelity-report-delta-percentiles"></a>

Add `--delta-percentiles` to summarize that same maximum-RGBA-delta distribution
with nearest-rank p50, p95 and p99. Each rank is `ceil(p * pixel_count / 100)`;
the reported delta is the smallest bin whose cumulative count reaches that
rank. The complete compared crop, including zero and sub-tolerance deltas,
contributes. Percentiles are diagnostic and do not affect the gate. JSON adds a
`delta_percentiles` object and text prints the same object as one `delta percentiles:`
line immediately before the verdict. Percentiles alone omit histogram output;
both options share one histogram scan.
<a id="fidelity-report-channel-bias"></a>

Add `--channel-bias` to report the signed mean candidate-minus-reference byte delta for each
RGBA channel. Positive values mean the candidate trends higher; negative values mean it trends
lower. Opposite errors can cancel to zero even when pixels differ. This is a raw-byte diagnostic,
including RGB beneath transparent pixels, with missing alpha treated as opaque; it does not
composite or describe perceptual color error. JSON adds a `channel_bias` object and text prints
the same object immediately before the verdict. It is independent of tolerance and verdict.
<a id="fidelity-report-channel-maxima"></a>

Add `--channel-maxima` to report the largest absolute byte delta seen in each RGBA channel.
JSON adds a `channel_maxima` object and text prints a labelled RGBA maximum-delta line before
the verdict. It includes RGB bytes beneath transparent pixels, treats missing alpha as opaque,
and is independent of tolerance and verdict.
<a id="fidelity-report-horizontal-runs"></a>

Add `--difference-runs` to report maximal contiguous horizontal runs of pixels whose maximum
raw RGBA channel delta exceeds `--tolerance`. JSON adds row-major `difference_runs` records
with crop-relative `x`, `y` and `length`; text prints the same array after column bounds.
Runs end at every row boundary, and adjacent pixels stay in one run even when their delta
magnitudes differ. Crop origins translate these coordinates to source images. Output can grow
with the number of disjoint runs, so the option is opt-in; omitted runs skip the scan.
Add `--difference-run-count` to report the number of maximal horizontal mismatch runs as
`difference_run_count` in JSON or a `difference run count:` text line. It counts unfiltered
segments whose pixels' maximum raw RGBA channel delta exceeds `--tolerance`; alpha and RGB beneath
transparent pixels participate, and missing alpha is treated as 255. This is an interval count,
not a mismatching-pixel count: runs end at row boundaries, and adjacent mismatching pixels in one
row form one segment. Length cutoffs affect the optional run list but not the scalar. Combined
with `--difference-runs`, it reuses that scan; by itself it streams the count without retaining run
records. Requesting the run list also reports the count; with neither option the diagnostic is
omitted.
Pass `--min-difference-run-length N` with `--difference-runs` to omit completed runs shorter than
`N`. The inclusive cutoff filters the reported list after segmentation, so separated runs stay
separate and comparison metrics and longest-run summaries still use the complete mismatch data.
An empty requested list is reported as `[]`.
Pass `--max-difference-run-length N` with `--difference-runs` to omit completed runs longer
than `N`. The inclusive maximum combines with the minimum cutoff; a minimum above its paired
maximum is refused before any image read with a diagnostic naming both flags and both values.
Segmentation, comparison metrics and longest-run summaries still use the complete mismatch data.
Pass `--max-difference-runs N` with `--difference-runs` to report only the first N eligible
horizontal intervals in row-major order. This positive count cap is applied after the minimum
and maximum run-length filters; JSON adds `omitted_difference_runs`, and text prints
`omitted difference runs: N` immediately after the list, including zero. Run counts, longest-run
summaries, metrics and the verdict still use the full mismatch data. With a cap, intervals are
collected as they are scanned, retaining the requested page and the first longest interval;
count and longest summaries share that full-stream scan. Without a cap, the full run list is
retained. This bounds horizontal interval records only, not image buffers or vertical intervals.
Omitting the option adds no report field or line.
Pass `--difference-run-offset K` with that cap to skip K eligible intervals after both length
filters, in global row-major order. The offset must be a nonnegative ASCII integer; even zero
requires the cap. JSON adds `difference_run_offset`, and text prints `difference run offset: K`
immediately before the interval list. The omitted count includes skipped intervals and eligible
intervals beyond the page.
<a id="fidelity-report-vertical-runs"></a>

Add `--difference-column-runs` for maximal vertical runs, ordered left-to-right and then
top-to-bottom. JSON adds crop-relative `difference_column_runs` records with `x`, `y` and
`length`; text prints them after horizontal runs. Runs end at each column boundary and adjacent
pixels remain together across differing delta magnitudes. Crop origins translate their positions
to either source image. Output can grow with disjoint runs, so this scan is opt-in. Pass
`--min-difference-column-run-length N` with `--difference-column-runs` to omit completed runs
shorter than `N`. The inclusive cutoff filters after segmentation, preserving separated intervals,
comparison metrics and longest-column summaries. An empty requested list is reported as `[]`.
Pass `--max-difference-column-run-length N` with `--difference-column-runs` to omit completed runs
longer than `N`. The inclusive maximum combines with the minimum cutoff; a minimum above its
paired maximum is refused before any image read with a diagnostic naming both flags and both
values. Segmentation, metrics and longest-column summaries use the complete mismatch data.
Pass `--max-difference-column-runs N` to report only the first N eligible vertical intervals in
column-major order after both length filters. JSON adds `omitted_difference_column_runs`, and text
prints `omitted difference column runs: N` immediately after the vertical list, including zero.
Run counts, longest-column summaries, metrics and verdict still use the full mismatch data. With
a cap, the scan retains the requested page and first longest interval; count and longest summaries
share that scan. This bounds vertical interval records, not image buffers. Without a cap, the full
run list is retained. Omitting the option adds no report field or line.
Pass `--difference-column-run-offset K` with that cap to skip K eligible vertical intervals after
both length filters, in global column-major order. JSON adds `difference_column_run_offset`, and
text prints `difference column run offset: K` immediately before the vertical list. The omitted
count includes skipped intervals and eligible intervals beyond the page. Capped paging retains
the requested page and first longest interval rather than the full vertical run list.
Add `--difference-column-run-count` to report the number of maximal vertical mismatch runs as
`difference_column_run_count` in JSON or `difference column run count: N` in text. It counts
unfiltered segments, so length cutoffs affect the optional run list but not the scalar. Combined
with `--difference-column-runs`, it reuses that scan; by itself it streams the count without
retaining intervals. The diagnostic is omitted unless requested.
Add `--difference-centroid` to report the equal-weight mean `(x, y)` of pixels whose maximum raw
RGBA channel delta exceeds tolerance. Coordinates are crop-relative integer pixel indices; delta
magnitude does not affect weight. JSON includes `difference_centroid` and text prints it immediately
before the verdict, with `null` when no pixel differs. The scan is opt-in.
<a id="fidelity-report-scanline-counts"></a>

Add `--difference-rows` to count compared pixels beyond tolerance in each row. A pixel counts
once when any RGBA channel exceeds tolerance; missing alpha is opaque and RGB beneath
transparency is compared as stored. JSON adds a dense `difference_rows` array, and text prints
the same array immediately before the verdict. Its indices are crop-relative y coordinates, so
add the corresponding crop's y origin to locate a row in either source image. Zero rows are
included, and the diagnostic is omitted unless requested.
Add `--difference-columns` to count the same over-tolerance pixel union in each column. JSON
adds a dense `difference_columns` array, and text prints it immediately after the row diagnostic
when both are requested. Indices are crop-relative x coordinates; add the crop's x origin to
locate a column in either source image. Zero columns are included, and the diagnostic is omitted
unless requested.
Add `--difference-row-bounds` to report each compared row's smallest crop-relative horizontal
interval containing a pixel beyond tolerance. Rows without a mismatch are `null`; a nonempty
entry has `x` and `width`, and unchanged gaps inside the interval may be included. JSON adds a
dense `difference_row_bounds` array and text prints the same array immediately before the verdict.
Add the corresponding crop's x origin to locate an interval in either source image. The report
uses raw RGBA deltas, including RGB beneath transparency, and is omitted unless requested.
Add `--difference-column-bounds` to report each compared column's smallest crop-relative vertical
interval containing a pixel beyond tolerance. Columns without a mismatch are `null`; nonempty
entries have `y` and `height`, and unchanged gaps inside the interval may be included. JSON adds a
dense `difference_column_bounds` array and text prints it after row bounds and before the verdict.
Add the corresponding crop's y origin to locate an interval in either source image. The report
uses raw RGBA deltas, including RGB beneath transparency, and is omitted unless requested.
`make render` invokes the CLI
(`tools/render_surface.py`), which dispatches the lifecycle in `tools/render_workflow.py` to
produce a candidate render. Where the Plasma render tools are on `PATH`, `make check` renders the
window and byte-compares the title-bar strip (candidate `30,0,80,22` against reference
`30,25,80,22`), the close, zoom and collapse box regions, and the side and bottom border strips of
`aboutsystem_betawiki.png` (the zoom box against `systemprofiler_betawiki.png`), cropping each
region with the same `crop`/`compare` the fidelity tool uses. The applet face gate
(`tests/test_render_surface.py::TestRender`) pins the same capture's client face beside
those strips: the display field's black outline and flat interior and the keypad's
eighteen raised cells with their blended corner arcs, plus the flat gap rows and
columns between the cells, while the font-dependent label and digit ink is pinned
only by live-ink checks. The dialog renders the same
suite runs (`tests/test_render_surface.py::TestCheckboxDialogRender`,
`::TestComboboxDialogRender`, `::TestLineInputDialogRender`, `::TestMenuDialogRender`,
`::TestCalendarDialogRender`, `::TestColorDialogRender`, `::TestSliderDialogRender`,
`::TestTextboxDialogRender`, `::TestProgressbarDialogRender`, `::TestGtkDialogRender` and
`::TestInactiveDialogRender`)
open a `kdialog` warning box, chooser, input box, menu list, calendar, color picker, slider,
progress meter and text box and a `zenity` GTK 4 entry dialog, and byte-compare the
engine-drawn widgets with the shipped art described under
[Rendering a candidate](#rendering-a-candidate), except that the menu gate pins the
engine-drawn `GenericFrame` item-view border runs, white interior and current-item
focus ring against measured pixel values. The inactive gate pins the two-window
capture's unfocused window: its decoration pixels — the `#555555` outline ring, the
recoloured client edge, the flat buttonless `#DDDDDD` bar and the `#777777` title ink —
against the shipped inactive art, beside the focused neighbour that proves the capture
holds two states. The GTK 4 dialog gate also pins the
rendered action-button row, Cancel button and CSD shell edge; the gates also check capture-level
invariants.

## Running checks

Run the full project check before submitting changes. Focused runs help with iteration, but do not
replace the full check.

| Scope | Command |
| --- | --- |
| Full project check | `make check` |
| Matching test modules | `make check CHECK_PATTERN='test_colorscheme*.py'` |
| One test class | `make check CHECK_TESTS=test_colorscheme.TestAnchors` |
| Serial discovery | `make check CHECK_PARALLEL=0` |

The hosted check job sets `LIBGL_ALWAYS_SOFTWARE=1`, so its render capture gates skip even
when their tools are installed. A green check with those skips does not establish rendered-pixel
equality. The guard is environment-based, not a KWin-version probe: it triggers when
`LIBGL_ALWAYS_SOFTWARE=1`, or when `MESA_LOADER_DRIVER_OVERRIDE` or `GALLIUM_DRIVER` contains
`llvmpipe`, `softpipe`, `swrast` or `zink` (case-insensitive). The skip reason cites a fix in
KWin 6.8, but upgrading KWin alone does not bypass this guard. To exercise the capture gates,
use a GPU-backed host with the documented render tools and without software-forcing variables.
The isolated headless rendering commands remain available under [Rendering a candidate](#rendering-a-candidate).

The GTK 4 button, notebook, progressbar, scale, indicator, spin-field and view-census probes skip during routine checks. To opt in
without using your desktop display, run each probe under Xvfb:

```sh
env -u DISPLAY -u WAYLAND_DISPLAY xvfb-run -a -- env PLATINUM_RUN_GUI_TESTS=1 make check CHECK_TESTS=test_gtk4_button_probe.TestGtk4ButtonProbe.test_button_faces_render
env -u DISPLAY -u WAYLAND_DISPLAY xvfb-run -a -- env PLATINUM_RUN_GUI_TESTS=1 make check CHECK_TESTS=test_gtk4_notebook_probe.TestGtk4NotebookProbe.test_notebook_tab_faces_render
env -u DISPLAY -u WAYLAND_DISPLAY xvfb-run -a -- env PLATINUM_RUN_GUI_TESTS=1 make check CHECK_TESTS=test_gtk4_progressbar_probe.TestGtk4ProgressbarProbe.test_progressbar_faces_render
env -u DISPLAY -u WAYLAND_DISPLAY xvfb-run -a -- env PLATINUM_RUN_GUI_TESTS=1 make check CHECK_TESTS=test_gtk4_scale_probe.TestGtk4ScaleProbe.test_scale_faces_render
env -u DISPLAY -u WAYLAND_DISPLAY xvfb-run -a -- env PLATINUM_RUN_GUI_TESTS=1 make check CHECK_TESTS=test_gtk4_scrollbar_probe.TestGtk4ScrollbarProbe.test_scrollbar_faces_render
env -u DISPLAY -u WAYLAND_DISPLAY xvfb-run -a -- env PLATINUM_RUN_GUI_TESTS=1 make check CHECK_TESTS=test_gtk4_indicators_probe.TestGtk4IndicatorsProbe.test_mixed_indicators_draw_black_dashes
env -u DISPLAY -u WAYLAND_DISPLAY xvfb-run -a -- env PLATINUM_RUN_GUI_TESTS=1 make check CHECK_TESTS=test_gtk4_spin_probe.TestGtk4SpinProbe.test_spin_field_renders_the_mirrored_etch_in_rtl
env -u DISPLAY -u WAYLAND_DISPLAY xvfb-run -a -- env PLATINUM_RUN_GUI_TESTS=1 make check CHECK_TESTS=test_gtk_view_census
```

`xvfb-run -a` allocates and cleans up a separate virtual X server. Unsetting inherited
`DISPLAY` and `WAYLAND_DISPLAY` before starting it prevents these commands from selecting the
desktop display. Missing GTK 4 introspection bindings can still cause a probe to skip for lack of
capability; setting the opt-in variable alone does not mean the probe ran.

Reference image validation is separate: see [Validating the reference set](#validating-the-reference-set)
for `make check-references` and its Git LFS materialization requirement.

## Invariants

`docs/invariants.md` states, per `theme/` subsystem and for the fidelity gate, the guarantee a
surface must keep and the test that pins it. Read the matching row before changing a surface, and
update it in the same change when a guarantee moves. `tests/support/invariants.py` keeps the register
and the repository in step.

## Development team

This theme is developed by a tumwater team of AI roles. How many roles run at once is a tumwater
setting, not a file in this repository: `maxConcurrent` in the primary checkout's `tumwater.json`
(alongside any `maxConcurrentPerProvider` cap) is the most model runs in flight across all roles
at once, merges included, with the director's own runs sitting outside it; it defaults to 6. A
role cannot change that concurrency setting, so the operator sets it from the primary checkout, for example
`tumwater config set maxConcurrent 6` (requested 2026-10-18: run six roles at once).

The project check is `make check`, without `CHECK_PATTERN` or `CHECK_TESTS` overrides.
From the primary checkout, operators can inspect the configured check with
`tumwater doctor check --json` (the `check` row should read `ok`) and
`tumwater status --json` (the output should have no `noDeclaredCheck`). If a clone has no
declared check, configure it from the primary checkout with
`tumwater config set check.command 'make check'`.
The separate reference-image validation remains `make check-references`.
