# Bugs

Known bugs, recorded by any loop and fixed by the bugfix loop.
Each bug: symptom, how to reproduce, suspected cause if known. Move fixed bugs to Fixed, with the
required `**Validation gap:** <tag> — <one sentence>` line recording what made the bug hard to
confirm (tag one of: none, no-repro, no-fake, real-run-needed, no-observability, slow-check,
unclear-invariant).

## Open

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

**Directed by the user 2026-10-30 (recorded by the director role):** the interior black rows are
not an intentional part of the look, so fix them by steering the engine/config (the
`[PanelButtonCommand]` frame and `interior.element=button` settings) so the interior paints the
shipped flat `#DDDDDD` face slice — do not mirror the rows into re-derived `button-normal` art.
Keep black rows only if the reference screenshots actually show them on a raised popup button's
interior; sample that surface first and record the provenance if so. Then pin the rendered
button's band runs in the dialog render the way the checkbox cell is pinned.

**Progress (2026-10-30 by bugfix):** reproduced with
`python3 tools/render_surface.py OUTPUT --checkbox-dialog`: the Yes button rows 209 and 228
remain `#000000` across the interior, while row 210 is `#DDDDDD`. Setting Kvantum's
`normal_default_pushbutton=true` did not change those pixels. Kvantum 1.1.4 source shows
`CE_PushButtonBevel` renders a second `button-default` frame/interior pass for a default
`QPushButton`; adding `button-default-*` slices to the theme SVG also left the output unchanged,
so the exact state lookup or other drawing pass still needs to be identified. No workaround has
been retained.

**Needs review 2026-10-30 by bugfix: inspect Kvantum's frame and default-indicator element lookup
for the rendered button; the next pixel probe should identify which pass paints `#000000` at
(195,209) and (195,228), despite `button-normal` containing only `#DDDDDD` in its interior.**

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

**Decided by the user 2026-10-30 (recorded by the director role): the generic frame carries the
field.** Steer `[GenericFrame] frame.element` from `common` to `itemview`; do not change
`[ItemView]`, whose frame slices still paint the per-item selection cells through
`PE_PanelItemViewItem`. Upstream `Kvantum/style/Kvantum.cpp`'s `PE_Frame` resolves a
`QAbstractScrollArea`'s frame with `getFrameSpec("GenericFrame")`, which is why the shipped
`itemview` nine-slice never reaches a list's border, and the installed themes' `GenericFrame` →
`common` mapping is only their own field style, not a binding rule. `common` stays as
`[TabFrame] interior.element=common`, so the raised tab interior is unchanged; `[StatusBar]`,
`[TabBarFrame]`, `[GroupBox]`, `[ToolTip]` and `[DockTitle]` disable or override their frame, so
the remaining `PE_Frame` consumers are the reference's sunken fields (lists, trees, tables, text
areas, scroll areas) plus the Qt color dialog's `QWellArray` swatches, which no reference
screenshot shows — record that swatch change as an adaptation. Then pin the rendered list field's
border runs, not just the `itemview` slices: add a `--menu-dialog` client to
`tools/render_session.py` (the same `dbus-run-session`/KWin session, no new infrastructure) and
assert the reference's `#999999`/`#000000`/`#FFFFFF` left and `#000000`/`#FFFFFF` right/bottom runs
in that capture. Update `SURFACE_CONTROL_CONFIG`'s `GenericFrame` entry, the element test that
reads it, and the `docs/invariants.md` item-view row in the same change.

### The live dialog gates byte-compare one widget cell each, so the other engine-drawn widgets in the two captures stay unpinned (found by the steward role 2026-10-30)

The live render gate compares engine-drawn Kvantum widget pixels in
precisely three regions, each added when its bug was fixed: the checkbox
cell `CHECKBOX_CROP` (156, 187, 14x14) and its 1px face ring in the
`--checkbox-dialog` capture, and the combo-arrow cell `COMBOBOX_CROP`
(316, 178, 12x12) in the `--combobox-dialog` capture
(`tests/test_render_surface.py`); the gate's other byte-compares are the
rendered window chrome strips and boxes. Every other engine-drawn widget
pixel in those two populated 480x360 captures — the push buttons and any
further widget `kdialog` draws there — is never compared, so coverage grows
only when a render pass finds a bug by eye, never from an enumeration of
what the captures draw. Both Open records sit in exactly this unpinned
space: the Yes button's two interior black rows are drawn inside the
`--checkbox-dialog` capture the gate already runs, and the `--menu` field's
GenericFrame frame is an engine-drawn region no gate watches — `make check`
stays green on both. A future regression in any other engine-drawn widget
outside the three regions lands unobserved the same way.

Reproduce: patch the installed theme's `button-normal` interior slice to a
marker colour (the inspection the Open button record's field used on
`common-normal-*`), rebuild the render with
`RENDER_OUTPUT=x.png make render --checkbox-dialog`, and run
`tests/test_render_surface.py`'s dialog-render classes — no assertion
fails, because no compared crop overlaps the button (the check box cell
sits at y=187..200, the button at y=207..230).

**Suspected cause:** infrastructure, not a per-widget fix: the two session
renders already exist in `tools/render_surface.py` and are cheap to rerun,
so the gap is that the gates compare call-chosen single crops instead of
deriving the set of engine-drawn widget regions from the captures and
comparing each region against the shipped art slice its widget maps to.

**Decided by the user 2026-10-30 (recorded by the director role): explicit per-widget regions,
no capture walker.** Extend the two existing dialog gates with one byte-comparison or band-run
assertion per engine-drawn widget region of each capture, in the shape
`test_draws_the_check_box_cell_1_to_1` and `test_draws_the_combo_arrow_cell_1_to_1` already use:
the check box and its face ring plus the Yes and No push buttons in the `--checkbox-dialog`
capture, and the combo arrow, the combo field and the OK button in the `--combobox-dialog`
capture. For composed frames assert the rendered band rows/columns and the flat interior fill
against the shipped slices; do not rebuild a nine-slice composer in the test, because it would
reimplement `renderFrame` and could share its assumptions. A walker that segments regions out of
the capture is rejected: it would reimplement the widget-to-element mapping that this record
exists to pin, and the two captures have fixed 480x360 geometry by construction. The item view
field has no capture yet, so add the `--menu-dialog` client named in the item-view record and pin
its border runs there. Coverage is now exhaustive over the widgets the dialog clients create, not
automatic: a new `--*-dialog` mode must add its regions in the same change, and the region table
must name `tools/render_session.py`'s `checkbox_dialog_client`/`combobox_dialog_client` so that
requirement is visible where the widgets are constructed. `make check` owns the renders, so no new
session infrastructure is proposed.

## Fixed
