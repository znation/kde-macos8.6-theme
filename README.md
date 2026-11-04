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

## Contents

- [Prerequisites](#prerequisites)
- [Installing](#installing)
- [Generating the wallpaper](#generating-the-wallpaper)
- [Reference screenshots](#reference-screenshots)
- [Validating the reference set](#validating-the-reference-set)
- [Sampling reference pixels](#sampling-reference-pixels)
- [Common sampling tasks](#common-sampling-tasks)
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
| Render headlessly | Python 3.10 or newer; `dbus-run-session`, `kwin_wayland`, `plasma-apply-colorscheme`, `plasmawindowed` and `spectacle`. Dialog render modes also require `kdialog`; the GTK dialog render mode requires `zenity` instead. |
| Materialize reference images | Git LFS; run `git lfs install` and `git lfs pull`. See [Validating the reference set](#validating-the-reference-set). |

## Navigation

- [Installing](#installing)
- [Generating the wallpaper](#generating-the-wallpaper)
- [Reference screenshots](#reference-screenshots)
- [Validating the reference set](#validating-the-reference-set)
- [Sampling reference pixels](#sampling-reference-pixels)
- [Common sampling tasks](#common-sampling-tasks)
- [Fidelity checking](#fidelity-checking)
- [Running checks](#running-checks)
- [Invariants](#invariants)
- [Development team](#development-team)

## Installing

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
`plasma/desktoptheme/`, the `org.macos8.desktop` window decoration into `aurorae/themes/`, the
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
when `${XDG_DATA_HOME}` is the default `$HOME/.local/share`.

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
drawn for this theme, not traced from Apple's artwork, and inherits Breeze for every other name. The package also ships the `cursors/` Platinum pointer set at nominal sizes 16, 24 and 32: the `left_ptr` arrow, the `xterm` text I-beam, the `hand2` pointing hand, the `watch` busy wristwatch, the `fleur` move cross, the `size_hor` and `size_ver` resize arrows, the `size_fdiag` and `size_bdiag` diagonal resize arrows, the `crosshair` precision cross, the `not-allowed` circle-slash, the `dnd-copy` copy plus, the `grab` open hand, the `grabbing` closed fist, the `help` question-mark arrow, the `progress` arrow with a miniature watch face, the `pencil` diagonal pencil, the `zoom-in`/`zoom-out` magnifiers and the `context-menu` arrow beside a small menu panel, each a black face inside a white outline with byte-identical X-name aliases (`arrow`, `default`, `top_left_arrow`, `dnd-none`; `text`, `ibeam`; `hand1`, `pointer`, `pointing_hand`; `wait`; `move`, `all-scroll`, `size_all`, `dnd-move`; `e-resize`, `ew-resize`, `w-resize`, `h_double_arrow`, `sb_h_double_arrow`, `col-resize`, `split_h`; `n-resize`, `ns-resize`, `s-resize`, `sb_v_double_arrow`, `v_double_arrow`, `00008160000006810000408080010102`, `row-resize`, `split_v`; `nw-resize`, `se-resize`, `nwse-resize`; `ne-resize`, `sw-resize`, `nesw-resize`; `cross`, `tcross`; `circle`, `crossed_circle`, `03b6e0fcb3499374a867c041f52298f0`, `forbidden`, `no-drop`, `dnd-no-drop`; `left_ptr_help`, `question_arrow`, `whats_this`, `5c6cd98b3f3ebcb1f9c7f1c204630408`, `d9ce0ab605698f320427677b458ad60b`; `half-busy`, `left_ptr_watch`, `00000000000000020006000e7e9ffc3f`, `08e8e1c95fe2fc01f976f1e063a24ccd`, `3ecb610c1bf2410f44200f48c40d3599`; `cell`, `plus`; `openhand`; `closedhand`). Xcursor roles the theme does not name still come from the fallback cursor theme. `make apply-cursor` selects it: Xcursor searches `$HOME/.icons` rather than `$XDG_DATA_HOME/icons`, so the target installs the icon theme (`INSTALL_PACKAGES=icon-theme`), creates the symlink `$HOME/.icons/org.macos8.desktop` to the installed theme, and runs `plasma-apply-cursortheme org.macos8.desktop`; restart running applications for the new pointer to display correctly. `make remove-cursor` removes only that symlink; it leaves a foreign path and `kcminputrc` untouched, and when `[Mouse] cursorTheme` still names `org.macos8.desktop` it prints `plasma-apply-cursortheme breeze_cursors` as the reset. `make install` copies the cursor artifacts without selecting them, while aggregate `make apply` exposes the installed pointer set and selects it when `plasma-apply-cursortheme` is available; when that tool is absent, apply leaves the set installed and linked and prints a note. The global theme also selects the
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
translucent rounded rectangle). The window decoration ships
`metadata.json` and `metadata.desktop` (the KPackage and KWin-discovery
metadata), `org.macos8.desktoprc` (the Aurorae layout: a 22px title bar, 6px
side and bottom borders, and 13x13 close and collapse widgets, each a 12x12 box plus its 1px white highlight, and a 21x13 zoom widget: its box plus the stripe-free gap to its left and the flat spacing to its right), `decoration.svg` (the
active and inactive frames) with its gzipped `decoration.svgz` (the form
`kpackagetool6` requires), and `close.svg`, `maximize.svg`, `restore.svg`, `shade.svg` (the
active and inactive widgets); select it in System Settings → Window
Decorations. An unfocused window wears the flat grey inactive frame and
boxes. `make
uninstall` removes every installed artifact, including the thirteen GTK files, leaving the shared
`color-schemes/`, `look-and-feel/`, `desktoptheme/`,
`aurorae/themes/`, `wallpapers/`, `icons/`, `fonts/` and `themes/`
directories and anything else in them in place. It removes only those artifacts, their
hidden `.staging`/`.old` leftovers and the emptied GTK directories; it refuses to run if a fixed
install destination parent is a symlink. It never edits the user's configuration: if the removed
scheme is still
the selected one (`[General] ColorScheme` in `kdeglobals`), KDE may not be able to resolve
it after the uninstall and falls back to BreezeLight on the next start, so
`make uninstall` prints a warning naming `plasma-apply-colorscheme BreezeLight`
as the reset; if the GTK selection `make apply` published still names
`org.macos8.desktop` after the uninstall, it likewise prints a warning naming
`make remove-gtk` as the reset. Neither warning edits the user's configuration.
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
is refused by the same shared guard, before any recipe runs and unechoed; a value carrying a
control byte (0x01-0x1f or 0x7f, tab and newline excepted) is refused the same way, since the
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
KWin to reconfigure so the window decoration reloads (when neither `qdbus6` nor `qdbus` is installed
it notes that and leaves KWin to reload on its next start). It then opts the current user into the
reference's modifier layout: `tools/apply_keymap.py` appends `ctrl:swap_lalt_lctl` to
`[Layout] Options` in `kxkbrc` (keeping every other XKB option), sets `ResetOldOptions` so KWin
applies those options on Wayland, and emits `org.kde.keyboard /Layouts reloadConfig` so the swap
takes effect without a logout. After the swap the physical left Alt produces Control and the
physical left Control produces Alt for every application in this user's session, putting Cut, Copy,
Paste and the rest of the reference's shortcut modifier at the Command-key position, provided
the keyboard reports PC keycodes. A keyboard switched to its Mac (Apple) mode already swaps those
positions in firmware: its Command-position key sends Super, so the option then lands on the
left Ctrl and Super keys instead — the Command-position key opens the launcher and the Windows
key produces Control. Switch such a keyboard back to its PC/Windows mode; the keymap is already
right and needs no second apply. Right Alt
(AltGr) and other users' sessions are unchanged, and a repeat apply keeps one copy. The reload is
best effort: when neither `dbus-send` nor `busctl` is on `PATH`, or the emitted signal fails, it
notes that the swap takes effect at the next login. The setting persists after `make uninstall`;
run `make remove-keymap` to remove `ctrl:swap_lalt_lctl` while preserving other XKB options; this does not
restore earlier keyboard settings.
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
After `make install`, run `make apply-plasma` to reselect the installed global theme, color scheme and desktop theme, write the window-button placement, and request Kvantum selection and a KWin reload without applying other surfaces. It requires Python 3.10+ and `lookandfeeltool`, `plasma-apply-colorscheme`, `plasma-apply-desktoptheme` and `kwriteconfig6`. The global-theme application preserves panels; Kvantum selection works with its existing default-data-home limitation, and the splash change appears at the next login.
`make install-local-hook` writes a local-only `post-commit` hook into this clone's git hooks
directory (the common `.git/hooks` shared by the `.tumwater/worktrees/*` worktrees), so every
commit installs and re-applies the theme from the committing worktree; the hook is uncommitted, so
other clones and contributors are unaffected, and `make apply` is the manual equivalent. A
fast-forward merge creates no commit, so it does not trigger the hook. `tools/local_hook.py`
refuses to overwrite or remove a `post-commit` hook it did not write -- this clone's Git LFS hook
is one -- naming the path instead, so `make uninstall-local-hook` removes only its own hook.
### Rendering a candidate

Capture the default calculator or one of the four widget dialogs:

```sh
make render RENDER_OUTPUT=calculator.png
python3 tools/render_surface.py checkbox.png --checkbox-dialog
python3 tools/render_surface.py combobox.png --combobox-dialog
python3 tools/render_surface.py menu.png --menu-dialog
python3 tools/render_surface.py gtk.png --gtk-dialog
```

The Make target captures the default calculator and takes its output path from `RENDER_OUTPUT`;
the direct Python commands select dialog modes. The calculator capture defaults to 320x240;
each dialog capture is fixed at 480x360. Dialog modes cannot be combined with each other, a
different applet, or width/height overrides. Dialog captures require `kdialog` in the kdialog
modes and `zenity` in the GTK mode; see
[Prerequisites](#prerequisites) for the other rendering tools. To compare a candidate PNG with
the references, see [Fidelity checking](#fidelity-checking).

`make render` renders the installed theme in a headless KWin session and writes a screenshot PNG
(a 320x240 Plasma calculator window by default) to `RENDER_OUTPUT` (`render.png`); it needs
`dbus-run-session`, `kwin_wayland`, `plasma-apply-colorscheme`, `plasmawindowed` and
`spectacle` and exits 2 naming the first missing tool; a `make` or `dbus-run-session`
that exists but cannot be started is reported the same way, as is a scratch session
directory that cannot be created. It
installs into a scratch data home and leaves your own Plasma configuration alone. A wholly
black capture — the screen before the window has painted — is refused with a diagnostic
naming the settle wait rather than published as a render. A failed install, render or
capture exits 1; a SIGTERM or SIGHUP ends the run with 128 plus the signal number.
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
`--gtk-dialog` opens a zenity text-entry dialog: zenity is a GTK 4 client, so with no
theme-name CSS switch it wears the theme through the selection the render publishes into the
scratch config home (`gtk-4.0/settings.ini` theme-name keys and the user-css `@import` of the
installed sheet), and the render captures it at the same 480x360 size. In this render mode the
GTK 4 dialog gate (`tests/test_render_surface.py::TestGtkDialogRender`) pins the rendered entry-field
cell 1:1 against the shipped art, along with the action-button row, Cancel button and CSD shell
edge; it also checks capture-level invariants. The four dialog modes cannot be combined. In each mode the scratch session links its own home's
`themes/` onto the installed theme directory, because Kvantum looks there under the
literal `$HOME/.local/share/themes/` path.

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
| `make remove-keymap` | Removes `ctrl:swap_lalt_lctl` from the current user's XKB options, preserving other options. It cannot restore earlier keyboard settings. |
| `make uninstall` | Deletes installed theme packages and leaves user configuration in place. Run after clearing selections; it does not remove the cursor link or keyboard settings. |

The left Alt/Control swap also persists after theme removal; `make remove-keymap` removes only
that XKB option. As when applying, the swap assumes the keyboard is in its PC/Windows mode.

To apply the keyboard option without installing packages or applying the other theme surfaces,
run `make apply-keymap`. It requires Python 3.10+, `kreadconfig6` and `kwriteconfig6`; it preserves
other XKB options and uses the same best-effort reload behavior as `make apply`. The keyboard
must be in PC/Windows mode for the Command-position key to become Control.

To reselect the installed Plasma settings without installing packages or applying the other
theme surfaces, run `make apply-plasma`. Install first with `make install`; it requires Python
3.10+, `lookandfeeltool`, `plasma-apply-colorscheme`, `plasma-apply-desktoptheme` and
`kwriteconfig6`. It preserves panels, attempts Kvantum selection when available (with the
existing default-data-home limitation), and the splash change appears at the next login.

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
`plasma-apply-colorscheme`), the `kdialog` client the gate's checkbox and
combobox dialog renders open, and the `zenity` client its GTK dialog render opens, so
`make check` runs the rendered-pixel gate,
both dialog renders included, there too. Run those same commands locally for
parity with the workflow's check steps.

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

### Choosing a sampling mode

Choose a command based on the measurement you need. These commands use a beta reference
screenshot to demonstrate the sampler; it is not retail palette evidence. Choose coordinates
and region sizes for the surface you are measuring. Coordinates are absolute image pixels;
`--width` and `--height` set the sampled region starting at that coordinate, and both default
to 1. The reference PNGs are stored with Git LFS; materialize them as described in
[Validating the reference set](#validating-the-reference-set). Run `python3 tools/sample.py --help`
for the complete option list.

| Task | Command | Result |
| --- | --- | --- |
| Read one pixel | `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5` | RGB and hex values |
| Rank a small region's palette | `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --width 4 --height 4 --histogram --top-colors 3` | Up to three colors, ranked by count |
| Measure vertical color runs | `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --height 4 --runs` | Run colors, start coordinates, and lengths |
| Locate an exact color | `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --width 4 --height 4 --find-color '#63639C'` | Match count and enclosing bounds |

### Sampling options

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
minimum and maximum counts produce an empty palette. Explicit use reports the
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
`--top-colors`; contradictory fraction cutoffs return an empty palette. The
share uses the full region area, including pixels later omitted by other
filters. Explicit use reports the original `total_colors` and `omitted_pixels`,
and spatial diagnostics describe only emitted colors.

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
maximum cutoffs combine, and contradictory cutoffs report an empty run list.

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
only the reported list and combines with the minimum cutoff; contradictory
cutoffs produce an empty list while match counts and longest-run diagnostics
still cover the full search.

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
after the `axis:` line. The count is the complete unfiltered number of scanline
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



## Fidelity checking

`python3 tools/fidelity.py CANDIDATE REFERENCE` compares a rendered PNG surface against a
reference screenshot and reports mean absolute error, per-channel mean absolute error
(R, G, B, A), RMSE, worst per-channel delta and where it occurs, and the fraction of
differing pixels.
Pass `--candidate-crop X,Y,W,H` to crop the candidate and `--crop X,Y,W,H` to select a
surface region of the reference.

### Capturing a candidate

Capture the default Plasma calculator with `make render`, setting its output path with
`RENDER_OUTPUT`:

```sh
make render RENDER_OUTPUT=calculator.png
```

The Make target passes only the output path. Use the Python CLI directly for dialog captures;
each dialog flag must be used alone, and dialog captures reject `--width`, `--height` and a
non-default `--applet`:

| Surface | Command | Image size |
| --- | --- | --- |
| Checkbox dialog | `python3 tools/render_surface.py --checkbox-dialog checkbox.png` | 480x360 |
| Combo box dialog | `python3 tools/render_surface.py --combobox-dialog combobox.png` | 480x360 |
| Menu dialog | `python3 tools/render_surface.py --menu-dialog menu.png` | 480x360 |
| GTK dialog | `python3 tools/render_surface.py --gtk-dialog gtk.png` | 480x360 |

The calculator capture defaults to 320x240. Dialog captures need `kdialog` on `PATH` in the
kdialog modes and `zenity` in the GTK mode;
see [Prerequisites](#prerequisites) for the render tools. To allow a slower calculator paint,
increase the settle wait and set a longer timeout (which must exceed settle):

```sh
python3 tools/render_surface.py --settle 12 --timeout 120 calculator.png
```

A longer wait does not guarantee a successful capture. Compare the candidate with the relevant
reference surface using the [fidelity checker](#fidelity-checking); use its crop options to
compare a region rather than assuming a full capture matches a reference screenshot.

### Comparing a region

The documented calculator title-strip gate compares these corresponding 80x22 rectangles:

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

Add mismatch locations and RGBA values in JSON with:

```sh
python3 tools/fidelity.py calculator.png macos8.6-screenshots/aboutsystem_betawiki.png --candidate-crop 30,0,80,22 --crop 30,25,80,22 --worst-pixels 5 --explain-worst --json
```

The exit status is 0 when the comparison passes, 1 when it fails, and 2 for a usage or read error.

Reported `x`/`y` positions are relative to the compared crops. `candidate_position` and
`reference_position` locate each result in the original images; `--explain-worst` gives both
pixels' RGBA values and their channel differences. A mismatch is a useful report with exit status
1; status 2 means usage or image reading failed. See the diagnostic reference below for other
reports.

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
The aggregate metrics use comparison raw bytes and are independent of `--tolerance`; RMSE is not a
perceptual error measure. Add `--worst-pixels N` (1–1000) to list
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
Add `--channel-counts` to report, per channel, how many compared pixels exceed `--tolerance`
on that channel alone. `--json` adds the counts as a top-level `channel_counts` object
and text prints one `channel differing pixels (R, G, B, A)` line immediately before the
verdict, on passing and failing runs alike. A pixel can contribute to several counts (a
tint change moves three channels at once), so the counts overlap and must not be summed
into a union; `metrics.differing` already holds that union count.
Add `--delta-histogram` to report every compared pixel once, grouped by its
maximum absolute RGBA channel delta from 0 through 255. The complete distribution
includes zero and deltas at or below tolerance, and is independent of the gate:
JSON adds `delta_histogram` records (`delta` and `count`), while text prints the
same array as one `delta histogram:` line immediately before the verdict. The
option reports on passing and failing comparisons; omitting it skips the scan
and leaves the default output unchanged.
Add `--delta-percentiles` to summarize that same maximum-RGBA-delta distribution
with nearest-rank p50, p95 and p99. Each rank is `ceil(p * pixel_count / 100)`;
the reported delta is the smallest bin whose cumulative count reaches that
rank. The complete compared crop, including zero and sub-tolerance deltas,
contributes. Percentiles are diagnostic and do not affect the gate. JSON adds a
`delta_percentiles` object and text prints the same object as one `delta percentiles:`
line immediately before the verdict. Percentiles alone omit histogram output;
both options share one histogram scan.
Add `--channel-bias` to report the signed mean candidate-minus-reference byte delta for each
RGBA channel. Positive values mean the candidate trends higher; negative values mean it trends
lower. Opposite errors can cancel to zero even when pixels differ. This is a raw-byte diagnostic,
including RGB beneath transparent pixels, with missing alpha treated as opaque; it does not
composite or describe perceptual color error. JSON adds a `channel_bias` object and text prints
the same object immediately before the verdict. It is independent of tolerance and verdict.
Add `--channel-maxima` to report the largest absolute byte delta seen in each RGBA channel.
JSON adds a `channel_maxima` object and text prints a labelled RGBA maximum-delta line before
the verdict. It includes RGB bytes beneath transparent pixels, treats missing alpha as opaque,
and is independent of tolerance and verdict.
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
records. The diagnostic is omitted unless requested.
Pass `--min-difference-run-length N` with `--difference-runs` to omit completed runs shorter than
`N`. The inclusive cutoff filters the reported list after segmentation, so separated runs stay
separate and comparison metrics and longest-run summaries still use the complete mismatch data.
An empty requested list is reported as `[]`.
Pass `--max-difference-run-length N` with `--difference-runs` to omit completed runs longer
than `N`. The inclusive maximum combines with the minimum cutoff; if the cutoffs conflict,
the requested list is empty. Segmentation, comparison metrics and longest-run summaries still
use the complete mismatch data.
Add `--difference-column-runs` for maximal vertical runs, ordered left-to-right and then
top-to-bottom. JSON adds crop-relative `difference_column_runs` records with `x`, `y` and
`length`; text prints them after horizontal runs. Runs end at each column boundary and adjacent
pixels remain together across differing delta magnitudes. Crop origins translate their positions
to either source image. Output can grow with disjoint runs, so this scan is opt-in. Pass
`--min-difference-column-run-length N` with `--difference-column-runs` to omit completed runs
shorter than `N`. The inclusive cutoff filters after segmentation, preserving separated intervals,
comparison metrics and longest-column summaries. An empty requested list is reported as `[]`.
Pass `--max-difference-column-run-length N` with `--difference-column-runs` to omit completed runs
longer than `N`. The inclusive maximum combines with the minimum cutoff; conflicting cutoffs yield
an empty list. Segmentation, metrics and longest-column summaries use the complete mismatch data.
Add `--difference-column-run-count` to report the number of maximal vertical mismatch runs as
`difference_column_run_count` in JSON or `difference column run count: N` in text. It counts
unfiltered segments, so length cutoffs affect the optional run list but not the scalar. Combined
with `--difference-column-runs`, it reuses that scan; by itself it streams the count without
retaining intervals. The diagnostic is omitted unless requested.
Add `--difference-centroid` to report the equal-weight mean `(x, y)` of pixels whose maximum raw
RGBA channel delta exceeds tolerance. Coordinates are crop-relative integer pixel indices; delta
magnitude does not affect weight. JSON includes `difference_centroid` and text prints it immediately
before the verdict, with `null` when no pixel differs. The scan is opt-in.
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
region with the same `crop`/`compare` the fidelity tool uses. The dialog renders the same
suite runs (`tests/test_render_surface.py::TestCheckboxDialogRender`,
`::TestComboboxDialogRender`, `::TestMenuDialogRender` and `::TestGtkDialogRender`) open a
`kdialog` warning box, chooser and menu list and a `zenity` GTK 4 entry dialog and
byte-compare the engine-drawn check box cell with the shipped `checkbox-*` canvas, the
engine-drawn combo arrow with the shipped `comboarrow-normal` slice and the engine-drawn item
view frame with the shipped `GenericFrame` art. The GTK 4 dialog gate byte-compares the rendered
entry-field cell with its shipped art and pins the rendered action-button row, Cancel button and
CSD shell edge; it also checks capture-level invariants.

## Running checks

Run the full project check before submitting changes. Focused runs help with iteration, but do not
replace the full check.

| Scope | Command |
| --- | --- |
| Full project check | `make check` |
| Matching test modules | `make check CHECK_PATTERN='test_colorscheme*.py'` |
| One test class | `make check CHECK_TESTS=test_colorscheme.TestAnchors` |
| Serial discovery | `make check CHECK_PARALLEL=0` |

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
