# Rendering a candidate

Back to [Installing](../README.md#installing).

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
[Prerequisites](../README.md#prerequisites) for the other rendering tools. To compare a candidate PNG with
the references, see [Fidelity checking](../README.md#fidelity-checking).

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
For help diagnosing a failed capture, see [Troubleshooting a render](fidelity.md#troubleshooting-a-render).
With `--checkbox-dialog` the render instead opens a `kdialog` warning box whose
"do not ask again" check box the Kvantum engine draws with the theme's checkbox art
(`kdialog` must be on `PATH` in the kdialog dialog modes) and captures it as a 480x360 PNG
whose crop the checkbox gate (`tests/test_render_dialog_gates.py::TestCheckboxDialogRender`)
byte-compares like the chrome strips. `--combobox-dialog` opens a `kdialog` chooser
whose combo box the engine draws with the theme's `comboarrow` art; the render captures
it the same way, for the combo arrow gate
(`tests/test_render_dialog_gates.py::TestComboboxDialogRender`). `--menu-dialog` opens a
`kdialog` menu list whose item view the engine frames with the theme's `GenericFrame` art,
captured at the same 480x360 size; the item-view gate
(`tests/test_render_dialog_gates.py::TestMenuDialogRender`) byte-compares the item view's
rendered border runs, its white interior and the current-item focus ring there.
`--radiolist-dialog` opens a `kdialog` radio list whose sunken list field, the selected
row's selection band and the checked and unchecked radio indicators the engine draws
with the theme's palette and the shipped `radio` art, captured at the same 480x360 size;
the checked item is a fixed default (`on` in the client's arguments), so the selection
never depends on clock, network or input. The radio-list gate
(`tests/test_render_dialog_gates.py::TestRadioDialogRender`) pins the clear selection-face band,
the checked dot and unchecked ring cores, and the top edge of the sunken list field.
`--calendar-dialog` opens a `kdialog` calendar pinned to January 1970 (`--default
1970-01-07` with the load-bearing `--dateformat`: without it kdialog ignores `--default`
and opens today's month), captured at the same 480x360 size; the calendar gate
(`tests/test_render_dialog_gates.py::TestCalendarDialogRender`) pins the flat window face,
the white day-table face with the weekday-letter inks, the selected day's `#CCCCFF`
fill and digit ink, and the leftmost day column's red day digits there.
`--color-dialog` opens a `kdialog` color picker whose basic-color swatch grid, sunken value
fields and push buttons the engine draws with the theme's palette and the shipped push-button
art, captured at the same 480x360 size; the color gate
(`tests/test_render_dialog_gates.py::TestColorDialogRender`) pins the flat window face, the
swatch grid's first row's `#000000` lead cell and its `#AA0000` neighbour with the
window-face gap between them, the value field's `#999999` shadow over the sunk `#000000`
outline and `#FFFFFF` face, and a push button's raised frame with its `#DDDDDD` face cell
there.
`--icon-dialog` opens a `kdialog` icon chooser whose top-row search field's sunken
line edit and whose sunken icon-grid field the engine draws with the theme's palette
and the shipped field art, captured at the same 480x360 size; the icon gate
(`tests/test_render_dialog_gates.py::TestIconDialogRender`) pins the flat window face,
the icon-grid field's top edge's #999999 shadow row over the sunk `#000000`
outline and `#FFFFFF` face, the search field's `#999999` shadow arm over its sunk
outline and `#FFFFFF` face, and a push button's raised frame with its `#DDDDDD`
face cell there. The grid's icon cells' picture content is the fallback icon
theme's and stays deliberately unpinned, and the search field's blinking caret
column sits outside every band.
`--lineedit-dialog` opens a `kdialog` input box whose empty line edit the engine sinks
with the theme's sunken-field art, captured at the same 480x360 size; the line-edit gate
(`tests/test_render_dialog_gates.py::TestLineInputDialogRender`) pins the field's sunken bevel
right of the caret and the OK button's push-button frame there.
`--progressbar-dialog` opens a `kdialog` progress meter whose at-rest trough the engine
draws as the theme's `progress` element art, captured at the same 480x360 size; the helper
daemon `kdialog_progress_helper` shows it (kdialog execs the helper for a progress dialog
and its launcher exits, where the helper stays for the session script to capture), and the
progressbar gate (`tests/test_render_dialog_gates.py::TestProgressbarDialogRender`) pins the
trough's flat face between its outline rows, its #FFFFFF top/left bevel arms and its
#999999 bottom/right arms there.
`--slider-dialog` opens a `kdialog` slider whose at-rest thumb the engine draws with the
theme's `slidercursor` art at the trough's left end and whose trough the engine paints flat
through the theme's `slider` interior art, captured at the same 480x360 size; the slider gate
(`tests/test_render_dialog_gates.py::TestSliderDialogRender`) byte-compares the thumb cell 1:1 with
the shipped art and pins the trough's flat face between its 1px black boundary rows there.
`--textbox-dialog` opens a `kdialog` text box whose vertical scrollbar the engine draws with
the theme's scrollbar art (the raised `scrollbarslider` handle with its `grip` indicator, the
`slider`-element trough and the `arrow`-element buttons), captured at the same 480x360 size;
the scrollbar gate (`tests/test_render_dialog_gates.py::TestTextboxDialogRender`) pins the handle's
outline-and-bevel bands and grip bars, the disabled #999999 up triangle and the enabled
#000000 down triangle, and the trough's flat #EEEEEE interior below the resting handle there.
`--gtk-dialog` opens a zenity text-entry dialog: zenity is a GTK 4 client, so with no
theme-name CSS switch it wears the theme through the selection the render publishes into the
scratch config home (`gtk-4.0/settings.ini` theme-name keys and the user-css `@import` of the
installed sheet), and the render captures it at the same 480x360 size. In this render mode the
GTK 4 dialog gate (`tests/test_render_dialog_gates.py::TestGtkDialogRender`) pins the rendered entry-field
cell 1:1 against the shipped art, along with the action-button row, Cancel button and CSD shell
edge; it also checks capture-level invariants. The fourteen dialog modes cannot be combined. In each mode the scratch session links its own home's
`themes/` onto the installed theme directory, because Kvantum looks there under the
literal `$HOME/.local/share/themes/` path.
`--inactive-dialog` opens two `kdialog` message boxes with two distinct fixed titles and
captures the pair at the same 480x360 size: the session reads forced-geometry window
rules that place the two windows side by side, and KWin activates the newest one, so the
captured surface shows the unfocused window — the earlier-spawned one, on the left — drawn
with the inactive decoration art; the inactive gate
(`tests/test_render_dialog_gates.py::TestInactiveDialogRender`) pins that window's outline
ring, recoloured client edge, flat bar and title ink there.
`--file-dialog` opens a `kdialog` file chooser (KDE's KIO file dialog) whose places
sidebar, file list view, toolbar and name-filter surfaces the engine draws with the theme's
palette and the shipped field and button art, captured at the same 480x360 size; the chooser
opens on the scratch session's fixed `Documents` directory holding exactly `alpha.txt`,
`bravo.txt` and `delta.rtf`, so the listing it shows is deterministic. The file-dialog gate
(`tests/test_render_file_dialog.py::TestFileDialogRender`) pins the chooser's frame and title-bar
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
