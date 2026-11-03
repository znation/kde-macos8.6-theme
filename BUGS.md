# Bugs

Known bugs, recorded by any loop and fixed by the bugfix loop.
Each bug: symptom, how to reproduce, suspected cause if known. Move fixed bugs to Fixed, with the
required `**Validation gap:** <tag> — <one sentence>` line recording what made the bug hard to
confirm (tag one of: none, no-repro, no-fake, real-run-needed, no-observability, slow-check,
unclear-invariant).

Bugs no role can fix under the project's rules are refused with a dated
`**Refused <date> by <role>: <one-line reason>**` note under the entry's heading; they stay in
`## Open` only while the user has not accepted the refusal. Once accepted, move the entry to
`## Won't fix` — positioned after `## Open` so triage reads only fixable entries first — with a
dated `**Won't fix <date> by the <role> role — user accepted the refusal**` line that records the
limitation the theme now carries and what a fix would have required. A refusal whose reason is
"the fix is a redesign, not a repair" does not end there by default: route the redesign to a
PLANS.md plan and let the user decide whether to fund it before moving the bug. (Directed by the
user 2026-11-01; recorded by the director role.)

## Open

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

**Progress (2026-10-30 by bugfix):** rendered the checkbox, combobox and menu
dialog captures successfully at 480x360. The region coordinates and expected
band runs for the unpinned buttons and combo field have not been verified, so
no pixel assertions were added; guessed crops could pin unrelated dialog pixels.

**Review resolved 2026-11-02 at the user's direction: every region below was measured on fresh
`--checkbox-dialog`, `--combobox-dialog` and `--menu-dialog` renders of the current tree, and the
art slice each region maps to was confirmed by recolouring that slice in the theme SVG and
diffing the capture. The assertions are now writable without guessing; no further review is
needed.**

All three captures are 480x360 and each dialog is the session's only centred window, so the
rects are fixed geometry. Region rects are `(x, y, width, height)`; colour runs list the
shipped slice each maps to.

`--checkbox-dialog`, `tools/render_clients.py::checkbox_dialog_client` — the check box cell
`CHECKBOX_CROP` (156, 187, 14, 14) and its face ring `CHECKBOX_FACE_RING_CROP` (155, 186, 16, 16)
are already pinned; add:

- Yes button (156, 207, 82, 24), the `button-normal` frame under the interior ring recorded in
  the entry above. Row 207 `#000000` x=156..237; row 208 `#000000`(156), `#FFFFFF`(157..235),
  `#AAAAAA`(236), `#000000`(237); rows 209..213 `#000000`(156), `#FFFFFF`(157), `#DDDDDD`(158..235),
  `#AAAAAA`(236), `#000000`(237), the same band columns running down the whole interior; row 229
  `#000000`(156), `#FFFFFF`(157), `#AAAAAA`(158..236), `#000000`(237); row 230 `#000000`
  x=156..237. The interior also holds the label, the focus ring and the
  default-indicator wedge described in that entry, so this assertion lands after that steering
  (or excludes the bottom-right 7x7).
- No button (241, 207, 82, 24), the same frame with the interior 243..320 x 209..228 flat
  `#DDDDDD`: row 207 `#000000` x=241..322; row 208 `#000000`(241), `#FFFFFF`(242..320),
  `#AAAAAA`(321), `#000000`(322); row 229 `#000000`(241), `#FFFFFF`(242), `#AAAAAA`(243..321),
  `#000000`(322); row 230 `#000000` x=241..322. It carries no focus or default artifact, so pin it
  first.
- The interiors also carry their labels, and label pixels are not face pixels: the non-face
  extents are (179..235, 214..228) in Yes and (265..299, 213..224) in No. Pair each band-run
  assertion with a face rectangle outside those extents — rows 209..212 run face across both
  buttons — rather than comparing a whole interior.

`--combobox-dialog`, `tools/render_clients.py::combobox_dialog_client` — the combo arrow cell
`COMBOBOX_CROP` (316, 178, 12, 12) is already pinned; add:

- combo field (146, 172, 188, 24). Its bands are the shipped `button-pressed-*` slices, not
  `button-normal-*`: recolouring `button-pressed-top/bottom/left/right` changed exactly its 408
  outline pixels and recolouring `button-normal-*` changed nothing. Kvantum's `CC_ComboBox` frame
  status picks "pressed" for `State_Sunken || State_Selected`, so the field paints the pressed
  bevel rather than the reference's raised one; which of those two states this widget supplies is
  not settled here and does not change the assertion. Row 172 `#000000` x=146..333; row 173 `#000000`(146),
  `#AAAAAA`(147..331), `#FFFFFF`(332), `#000000`(333); rows 174..193 interior `#DDDDDD`
  x=148..331 (the selected text and the pinned arrow cell sit in it); row 194 `#000000`(146),
  `#AAAAAA`(147), `#FFFFFF`(148..332), `#000000`(333); row 195 `#000000` x=146..333; left column
  146 `#000000`, 147 `#AAAAAA`; right column 332 `#FFFFFF`, 333 `#000000`.
- OK button (167, 199, 82, 24): row 199 `#000000` x=167..248; row 200 `#000000`(167),
  `#FFFFFF`(168..246), `#AAAAAA`(247), `#000000`(248); rows 201..220 `#000000`(167),
  `#FFFFFF`(168), `#DDDDDD`(169..246), `#AAAAAA`(247), `#000000`(248) except the default-indicator
  wedge at (240..246, 214..220); row 221 `#000000`(167), `#FFFFFF`(168), `#AAAAAA`(169..247),
  `#000000`(248); row 222 `#000000` x=167..248.
- Cancel button (252, 199, 82, 24): the same bands with the interior 254..331 x 201..220 flat
  `#DDDDDD` and no wedge — row 199 `#000000` x=252..333, row 200 `#000000`(252), `#FFFFFF`(253..331),
  `#AAAAAA`(332), `#000000`(333), row 221 `#000000`(252), `#FFFFFF`(253), `#AAAAAA`(254..332),
  `#000000`(333), row 222 `#000000`.
- These two interiors carry their labels too: non-face extents are (190..246, 206..220) in OK
  (which includes the wedge) and (265..321, 205..216) in Cancel, so rows 201..204 run face across
  both buttons and rows 217..220 across Cancel.

`--menu-dialog`, `tools/render_clients.py::menu_dialog_client` — the render CLI and client already
exist but no gate runs the mode: add a fourth kind to `_Renders.KINDS` and a
`TestMenuDialogRender` class under the same `_dialog_gate_guard()`. Its engine-drawn region is:

- item-view field (112, 93, 256, 182), a 2px `itemview` frame drawn in the focused state (its art
  is identical to the normal state). Row 93 `#999999` x=112..366 with (367, 93) the window face
  `#DDDDDD`; row 94 `#999999`(112), `#000000`(113..366), `#FFFFFF`(367); left column 112
  `#999999` y=93..273 and 113 `#000000` y=94..273; right column 366 `#000000` y=94..273 and 367
  `#FFFFFF` y=94..274; row 273 `#999999`(112), `#000000`(113..366), `#FFFFFF`(367); row 274
  `#FFFFFF` x=113..367 with (112, 274) the window face `#DDDDDD`; interior `#FFFFFF` x=114..365,
  y=95..272. The two unpainted corners are the shipped art's own unpainted corner pixels, not the
  face slice, so state them explicitly rather than deriving them from a composer.
- the current item's `[Focus]` ring, black 1px at (115..364, 96..113), sits inside that field and
  is engine focus art, not field art: recolouring `focus-*` changed exactly its 528 pixels. Exclude
  it from the field comparison or assert it separately as `[Focus]`.

Look deviation found while verifying the combo field, recorded for its own triage: the reference's
pop-up buttons are raised — `opendialog_macrumors86.jpg` rows 15..33 (black outline, `#FFFFFF` top
highlight, `#DDDDDD` face, `#AAAAAA` bottom shadow), and `systeminfo_betawiki.png` rows 102..121
for the "Show:" popup the `comboarrow` cell is grounded in — while the capture's combo box renders the
pressed bevel (dark top-left, white bottom-right). The field assertion therefore pins the
`button-pressed-*` mapping the engine actually uses; the raised look needs a state steering or a
bug entry of its own.

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
must name `tools/render_clients.py`'s `checkbox_dialog_client`/`combobox_dialog_client` so that
requirement is visible where the widgets are constructed. That module owns the dialog argv
recipes. `make check` owns the renders, so no new
session infrastructure is proposed.

### The reference sampler reopens an image path after its symlink containment check (found by the security role 2026-11-03)

`tools/sample.py::main` checks `resolves_within(ROOT, image_path)` for a path lexically
inside the checkout, then calls `read_png_size(args.image)` and later
`read_png(args.image)`. Both calls in `tools/png/loader.py` open the pathname
again. A local process able to modify a checkout entry can replace a checked
in-repository image or parent symlink with one pointing outside the checkout
after the containment check and before either open. The sampler then reads the
outside PNG and prints its selected pixels, bypassing the guard intended to
prevent disclosure of private image data.

Reproduce deterministically by invoking `sample.main` with an in-repository
symlink to a valid PNG outside the checkout, and wrapping `resolves_within` so
it first performs the real containment check, then replaces that symlink with
one to the outside PNG before returning `True`. The existing guard passes on
the original target, while the subsequent size and image reads follow the
replacement and the report contains pixels from the outside image. Fix by
validating and decoding through the same opened file descriptor (including
the size read), so a pathname replacement cannot change the file after the
containment decision.

## Won't fix

### A killed GTK selection commit can leave settings files at different transaction versions (found by the robustness role 2026-11-01)

**Won't fix 2026-11-02 by the director role — user accepted the refusal**

Covered by the project-wide SIGKILL decision in PRINCIPLES.md (directed by the user
2026-11-02). Partial publication and leftover backups after SIGKILL are accepted limitations;
roles should use that standing decision when triaging equivalent reports.

`tools/gtk_staging.py::commit` publishes the GTK 3 settings, GTK 4 settings and GTK 4 user CSS
with separate replacements. Its rollback runs only when Python catches an exception; if the
process receives `SIGKILL` after one replacement, later files retain their old contents while
the first file contains the new selection, and its hidden hard-link backup remains. The GTK
selection is then partly applied despite the caller never completing.

Reproduce by staging different contents for two existing settings files, running `commit`, and
delivering `SIGKILL` after the first `os.replace` returns but before the second begins. The first
target contains new bytes, the second retains old bytes, and a `.backup` sibling remains. Recovery
would require a durable transaction record or another crash-consistent publication design;
in-process exception rollback cannot run after `SIGKILL`, and automatic recovery could overwrite
user edits made after the interrupted commit.

## Fixed
