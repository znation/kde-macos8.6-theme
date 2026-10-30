# Bugs

Known bugs, recorded by any loop and fixed by the bugfix loop.
Each bug: symptom, how to reproduce, suspected cause if known. Move fixed bugs to Fixed, with the
required `**Validation gap:** <tag> — <one sentence>` line recording what made the bug hard to
confirm (tag one of: none, no-repro, no-fake, real-run-needed, no-observability, slow-check,
unclear-invariant).

## Open

### The rendered window shows a 5px band of the decoration's centre tile below the title bar (found by the render pass 2026-10-29)

Every window rendered through the theme shows five rows of the Aurorae decoration's centre tile
(`decoration-center`, `#FFFFFF` in the shipped art) between the 22px title bar and the window's
content. The reference shows one `#FFFFFF` row (the frame's inner highlight) and the content from
the next row, so each rendered window's content sits four rows lower than the Mac window's. The
render gate cannot see it: `tests/test_render_surface.py` byte-compares the title-bar strip
(candidate rows 0-21) and the 6px side and bottom border strips, and the band lies at rows 22-26,
inside the client area.

Reproduce with `make render` (or the pass's throwaway Qt-widget session:
`python3 /tmp/wpass/render.py OUT.png --kvantum --command '<app>'`, which installs into a scratch
data home, writes the theme's kwinrc/kdeglobals, runs `kwin_wayland --virtual` under
`dbus-run-session` and captures the active window with `spectacle -a`) and read the capture's
rows 22-26 at any x inside the frame.

**Observed output:** `python3 tools/sample.py render.png 100 24` → `255,255,255  #FFFFFF`, and the
content starts at row 27; `aboutsystem_betawiki.png` at (107, 48) → `221,221,221  #DDDDDD` (its
row 47 is the `#FFFFFF` highlight).

**Suspected cause:** the theme's `org.macos8.desktoprc` sets `[Layout] TitleEdgeTop=0` and
`TitleHeight=22` but omits `TitleEdgeBottom`, so Aurorae's default (5) applies and the client area
starts at `TitleHeight + 5` = 27 while the frame art paints a 22px title bar; the decoration's
centre tile shows through the five rows the client does not cover. Measured in the throwaway
session (client row at which the content starts): `TitleHeight=22` → 27, `TitleHeight=17` → 22,
`TitleHeight=10` → 22 (the SVG's 22px top-margin hint floors it), `TitleEdgeTop=5` → 32, and
`TitleEdgeBottom=0` → 22 with the window exactly 5 rows shorter (104 → 99 rows). `BorderTop=6` or
`27`, `ButtonMarginTop=0`, `BorderSize=None` and a 17px top-margin hint change nothing. Patching
the installed `decoration-center` tile to `#FF00FF` turns exactly rows 22-26, x=6..122 magenta, so
the band is the decoration's tile, not the application's background. `docs/invariants.md`'s
aurorae row and `tests/test_aurorae_rc.py` treat the rc's title height and border widths as the
reference-derived geometry, which the render contradicts.

**Review resolved 2026-10-30 by the director role:** the open half of the review was which
`TitleEdgeBottom` value places the client at the reference position. Re-sampling the reference
settles it: `aboutsystem_betawiki.png` at x=250 and x=60 shows the title band ending in its black
rule at row 46 (`#000000`), then exactly one `#FFFFFF` row at 47, then the `#DDDDDD` content from
row 48 — one white row, matching the white `decoration-center` tile the band shows today. So the
note's original candidate `TitleEdgeBottom=0` is wrong: it puts the client at row 22, one row
above the reference, and erases the highlight row. The reference-derived value is
`TitleEdgeBottom=1`: the client begins at `TitleHeight + 1` (row 23), leaving exactly one row
where the frame's white centre tile shows as the highlight, and the fix removes four rows of band.
The title bar itself does not move (`TitleHeight` and the rows 0-21 strip are untouched; the side
and bottom border strips keep their `Border*` insets); the rendered window is four rows shorter
correspondingly. Fix: add `TitleEdgeBottom=1` to `[Layout]`; pin it in
`tests/test_aurorae_rc.py::TestRc::test_layout_metrics_match_reference` by re-deriving the one-row
white gap from the reference; and extend `tests/test_render_surface.py` to byte-compare the
capture's rows 22-26 against the reference's first client rows so the band cannot return.

### The rendered combo box indicator is a squashed 4px-wide arrow, not the reference's centred double arrow (found by the render pass 2026-10-29)

A `QComboBox`'s indicator renders as two right-aligned triangles four pixels wide (band widths
1/2/3/4 and 4/3/2/1 with the right edge fixed at x=187), while the reference cell and the shipped
`comboarrow-normal` art are 7px-wide centred triangles (1/3/5/7 and 7/5/3/1) in a 12x12
`#DDDDDD` cell. `tests/test_kvantum_combobox_reference.py` passes, so the art is right and only
the rendered pixels differ.

Reproduce with the pass's throwaway session: `kdialog --title "Test" --combobox "Choose a disk:"
"Macintosh HD" "Zip Disk"`, then dump x=174..187, y=56..71.

**Observed output:** row 59 one black pixel (x=187), row 60 two (186-187), row 61 three (185-187),
row 62 four (184-187), two face rows, then 4/3/2/1; the reference's cell
(`systeminfo_betawiki.png` x=233..244, y=106..117) has 1/3/5/7 and 7/5/3/1 centred bands —
`tools/sample.py systeminfo_betawiki.png 236 109 --width 5` is five `#000000` pixels where the
render's matching row has three.

**Suspected cause:** the same resampling as the check box — Kvantum draws the 12x12
`comboarrow` art into a narrower indicator area (about 7px), squashing the triangles; the theme's
`[ComboBox] indicator.size=12` does not reach the rendered indicator.

**Needs review by bugfix:** first try steering the engine to draw the 12x12 `comboarrow` cell
1:1 — an explicit `[ComboBox]` `indicator.size` matching the art's canvas, per the same
direction as the check box's recorded decision — and pin the rendered arrow's centred bands
(1/3/5/7, 7/5/3/1) with a test that re-derives the pixels from a render. Only if the engine
cannot be steered to the art's size, re-derive the `comboarrow` art at the size Kvantum actually
draws and record the smaller cell's deviation from the reference's 12x12 so the same direction
does not silently ship resampled art.

### The item view's frame art never reaches the screen: rendered lists draw the GenericFrame `common` frame instead of the reference's sunken field (found by the render pass 2026-10-29)

A rendered list (kdialog's `--menu` and `--checklist` dialogs, KFind's results) draws its field
frame as a raised 2px frame: the `#000000` outline outside, `#FFFFFF` inside on the top/left and
`#999999` inside on the bottom/right. The reference's item view
(`setup_emaculation.png`, the field the repo's own test derives: x=22 `#999999`, x=23 `#000000`,
x=24+ `#FFFFFF`) is a sunken field with the bevel *outside* the outline, and the shipped
`itemview` frame slices paint exactly that — but they never appear: patching the installed
theme's `itemview-normal-left`/`-top` slices to marker colours leaves the render unchanged, while
patching `common-normal-left`/`-top` (the `[GenericFrame]` element) changes the rendered frame's
pixels.

Reproduce with the pass's throwaway session: `kdialog --title "Test" --menu "Pick an item:"
"Alpha" a "Beta" b`, then profile row 150 (x=12 `#000000`, x=13+ `#FFFFFF`) and row 200
(x=266 `#999999`, x=267 `#000000`).

**Observed output:** the rendered field's left/top border is `#000000` then the `#FFFFFF` face,
and its right/bottom border is `#999999` then `#000000`; the reference's field is `#999999`,
`#000000`, `#FFFFFF` on the left and `#000000`, `#FFFFFF` on the right
(`setup_emaculation.png` (22, 250) = `#999999`, (23, 250) = `#000000`, (24, 250) = `#FFFFFF`).

**Suspected cause:** Qt draws a `QAbstractScrollArea`'s frame through the style's generic frame,
which this theme maps to `common` (`[GenericFrame] frame.element=common`), so `[ItemView]
frame.element=itemview` is never used for a list's border; the theme's reference-grounded sunken
field therefore only exists in the art.

**Needs review by bugfix:** decide whether the generic frame (or the list's own frame) should
carry the reference's sunken field, and pin the rendered list field's border runs, not just the
`itemview` slices.

## Fixed
