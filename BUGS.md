# Bugs

Known bugs, recorded by any loop and fixed by the bugfix loop.
Each bug: symptom, how to reproduce, suspected cause if known. Move fixed bugs to Fixed, with the
required `**Validation gap:** <tag> — <one sentence>` line recording what made the bug hard to
confirm (tag one of: none, no-repro, no-fake, real-run-needed, no-observability, slow-check,
unclear-invariant).

## Open

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

### A rendered kdialog push button paints two black rows the shipped button frame does not contain (found by the bugfix role 2026-10-30)

The dialog render this run (the checkbox gate's `--checkbox-dialog` render, a kdialog warning at
480x360) draws its Yes button, a 24px-tall raised `PanelButtonCommand` frame at x=157..234,
y=207..230, with the shipped frame bands — outline `#000000`, highlight `#FFFFFF`, `#DDDDDD`
face, `#AAAAAA` shadow (rows 208/229, columns 158/233) match the frame slices the Kvantum suites
derive — plus **two interior black rows the shipped art cannot produce**: rows 209 and 228 are
`#000000` across the interior (x=158..234), where the `button-normal` interior slice is a flat
`#DDDDDD` canvas and `button-normal-top`/`-left` are the 2px outline/highlight bands only.

Reproduce with `RENDER_OUTPUT=x.png make render --checkbox-dialog`, then dump x=158..234 at
y=209 and y=228 against the shipped `button-normal` interior and `button-normal-top` slices.

**Observed output:** row 209 and row 228 read `000…000` across the interior; the shipped
interior art is flat face (`tests/test_kvantum_button_reference.py` stays green, so the art is
right and only the rendered pixel rows differ). The reference's raised popup-button bevel adds
no such rows.

**Suspected cause:** the engine stretches or repeats the 2px frame bands (`frame.top=2`,
`frame.bottom=2` in `[PanelButtonCommand]`) into the interior instead of filling it from the
interior slice, or the interior art probe mis-fits by two rows — review upstream
`Kvantum.cpp`'s `CE_PushButton` / frame-drawing against those margins.

**Needs review by bugfix:** decide first whether the black rows are a Kvantum drawing choice the
art should match (re-deriving `button-normal` with the black end rows and recording the missing
reference surface) or a steered config fix (`frame.top`/`frame.bottom`); then pin the rendered
button's band runs in the dialog render the way the checkbox cell is pinned.

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
