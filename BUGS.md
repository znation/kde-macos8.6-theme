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

### The live render gate byte-compares only Aurorae window chrome, so `make check` stays green on widgets the engine draws wrongly (found by the steward role 2026-10-30)

The declared check's only rendered-pixel comparisons live in
`tests/test_render_surface.py::TestRender`, and they cover the Aurorae frame only: the title-bar
strip, the close, collapse and zoom boxes and the three border strips byte-compared against the
references, plus one body-face pixel at (300, 200). Nothing in the suite compares an engine-drawn
Kvantum widget's pixels with a reference — the Kvantum suites (`tests/test_kvantum_combobox_reference.py`
and its siblings) compare the *shipped art* against the reference cells, not the *rendered* widget —
so whatever the engine does to that art on screen is invisible to the check. This is one structural
risk behind a run of same-shaped bugs, each found only by a manual render pass and never by a test:
the fixed resampled check box indicator (BUGS-FIXED, found by the render pass 2026-10-29), and the
two needs-review Kvantum bugs above (the squashed combo indicator, the unmapped item-view frame).
The append-per-bug pattern confirms the shape: when each render bug is fixed, its armor is a handful
of newly byte-compared strips (the title-band entry above plans exactly rows 22-26 next), so the
gate grows strip by strip and the next resampled, squashed or unmapped widget stays as invisible to
`make check` as this run's bugs were.

**Reproduce:** run `make check` on a tree with the two needs-review Kvantum bugs unfixed — it passes
while the rendered dialog window draws the squashed arrow and the raised list frame; the two
entries' throwaway-session commands above produce the contradicting pixels.

**Observed output:** the two entries' dumps above (combo indicator bands 1/2/3/4 against the
reference's 1/3/5/7; list frame `#000000` then `#FFFFFF` against the reference's `#999999`,
`#000000`, `#FFFFFF`) alongside a green `make check`.

**Suspected cause:** the reference surface the gate byte-compares (one 320x240 window captured by
`TestRender`) contains no populated Kvantum widgets, only the Aurorae-decorated empty window body,
so the widget interiors fall outside every strip; whether the fix is a wider populated capture (for
example a second session with a combobox, a checkbox and a list, whose widget cells are byte-compared
the way the title bar is) or a cheaper substitute, and how a session keeps it cheap, is the review
question — the render session already exists (`tools/render.py`), so this plans as infrastructure,
not as a per-widget fix.

## Fixed
