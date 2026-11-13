# Installation details

Back to [Installing](../README.md#installing).

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
OFL 1.1, ChicagoFLF for menus and window titles, and the JetBrains Mono static
Regular, Medium and Bold faces for fixed-width text; the global theme
selects Lato for general, toolbar and smallest-readable fonts, ChicagoFLF
for menus and window titles, and JetBrains Mono Medium at 10 pt for the
fixed-width font, so KDE clients that follow the system fixed font inherit
that face while application-specific overrides may supersede it; the apply
writes that selection into `kdeglobals` itself because the look-and-feel
apply publishes no defaults' font key),
and the GTK 3 and GTK 4 Platinum stylesheets, their `index.theme` descriptor
and ten shared assets into `themes/org.macos8.desktop/`. Applying the global
theme selects the original neutral `#CCCCCC` wallpaper placeholder, shipped at
fixed resolutions.

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
font=Lato,10`, `menuFont=ChicagoFLF,10`, `toolBarFont=Lato,10` and
`smallestReadableFont=Lato,8`, `[kdeglobals][WM] activeFont=ChicagoFLF,10`,
and `[kdeglobals][General]
fixed=JetBrains Mono,10,-1,5,500,0,0,0,0,0,0,0,0,0,0,1,Medium`, the
fixed-width selection the apply run writes itself) still name their
published values after the uninstall, it prints one warning per
still-selected key, each naming that key's reset
`kwriteconfig6 --file kdeglobals --group General --key font --delete` (and
the analogous `menuFont`, `toolBarFont`, `smallestReadableFont`, `fixed`
and `--group WM --key activeFont` resets), which deletes exactly the one key the
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
live selections the existing diagnostics cover -- a `kdedefaults/kdeglobals`
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
config-cascade sources the existing live-config diagnostics already ground;
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
selects Lato for general, toolbar and smallest-readable text and ChicagoFLF for menus and window titles; a bare `make install` only copies the families), so the just-built theme becomes current without a logout: it re-selects
the `org.macos8.desktop` global theme (without `--resetLayout`, so your panels are left alone), the
`MacOS8` color scheme and the `org.macos8.desktop` desktop theme, writes the theme's
window-button layout into `kwinrc` (close box at the leading edge, zoom and collapse at the
trailing edge — Plasma's look-and-feel apply drops those two keys), points Konsole's default
profile at the packaged fixed-width face (a profile font overrides the `kdeglobals` selection in
every new Konsole session; see the Konsole paragraph below), tells Kvantum to draw our theme
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
Plasma re-selections, the button-layout write and the Konsole profile write run under the data-home flock that `make install` and `make uninstall` hold: a run
that cannot take that lock within its bounded wait exits 2 naming the data home, so a concurrent
uninstall cannot remove the packages between the apply's selections, and a `HOME` no install could
have resolved is refused the same way. The startup
splash is read at login, so a splash change appears only on the next login; restart GTK applications and Firefox for their selections. `make apply-gtk` and `make apply-cursor` remain available to repair one surface alone.
After the Plasma selections, the apply points Konsole's default profile at the packaged fixed-width face, so a new Konsole session draws JetBrains Mono Medium at 10 pt even when its profile names a face of its own: a profile's `[Appearance] Font` overrides the `[kdeglobals][General] fixed` selection the apply writes first. The profile keys are Konsole's own, grounded against upstream Konsole source (KDE Gear 25.04; the installed Konsole is 25.04.2) — no reference screenshot shows a terminal, so nothing here is sampled from one. The apply reads `[Desktop Entry] DefaultProfile` from `konsolerc`; an unset selection gets a new `~/.local/share/konsole/Platinum.profile` (`[General] Name=Platinum`, inheriting `Parent=FALLBACK/`, Konsole's built-in fallback profile, plus the font) that `konsolerc` then selects. A profile named explicitly is resolved through `konsole/` under the data home and then under each `XDG_DATA_DIRS` entry: edited in place when it lives in the data home, and first copied there under the same basename when it lives in a system data directory — Konsole reads the data home first, so the copy is what new sessions load, and the system file is never modified. Only the profile's `[Appearance] Font` entry is written, and `konsolerc` is written only to select a default that is not set, so every other profile key — name, shell, colors, shortcuts, keyboard mapping — is left untouched, non-default profiles are never read or written, and `make uninstall` leaves `konsolerc` and the profiles alone. An already-open Konsole keeps the font its sessions loaded; new sessions draw the written profile from their next start, so restart Konsole to see the change. To undo it by hand, delete the key the apply wrote — `kwriteconfig6 --file ~/.local/share/konsole/Platinum.profile --group Appearance --key Font --delete`, and, if the apply selected the profile, `kwriteconfig6 --file ~/.config/konsolerc --group "Desktop Entry" --key DefaultProfile --delete`. A profile name that is not a plain file name, a symlinked profile file and an unresolvable profile name are refused with a diagnostic naming the correction, and the apply exits 2.
After `make install`, run `make apply-plasma` to reselect the installed global theme, color scheme and desktop theme, write the fixed-width font selection, point Konsole's default profile at that font, and write the window-button placement, then request Kvantum selection and a KWin reload without applying other surfaces. It requires Python 3.10+ and `lookandfeeltool`, `plasma-apply-colorscheme`, `plasma-apply-desktoptheme`, `kwriteconfig6` and `kreadconfig6`. The global-theme application preserves panels; Kvantum selection names its off-default data home in a note when it runs under one, and the splash change appears at the next login.
`make install-local-hook` writes a local-only `post-commit` hook into this clone's git hooks
directory (the common `.git/hooks` shared by the `.tumwater/worktrees/*` worktrees), so every
commit installs and re-applies the theme from the committing worktree; the hook is uncommitted, so
other clones and contributors are unaffected, and `make apply` is the manual equivalent. A
fast-forward merge creates no commit, so it does not trigger the hook. `tools/local_hook.py`
refuses to overwrite or remove a `post-commit` hook it did not write -- this clone's Git LFS hook
is one -- naming the path instead, so `make uninstall-local-hook` removes only its own hook.
