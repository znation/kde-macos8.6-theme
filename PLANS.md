# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; landed-plan facts re-trimmed 2026-10-23
by the clean role; validation scope clarified 2026-10-25 by the steward role; Firefox artifact
and content-surface status updated 2026-10-26 by the steward role; install-firefox
file list corrected 2026-10-27 by the steward role; shipped-SVG count updated
2026-10-27 by the feature role; Firefox content scope refreshed
2026-10-29 by the steward role; landed-series narration trimmed 2026-11-11 by the
steward role):** The
initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (thirty-one widget SVGs under
`widgets/`, including the `widgets/margins-highlight.svg` panel edit-mode margin highlight and the
`widgets/containment-controls.svg` panel resize and slider handles, plus
`dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
collapse boxes); the desktop wallpaper package; the `org.macos8.desktop` icon theme (our own
32x32 Platinum-style art for the desktop's hard-disk, folder, document,
Trash and full-Trash icons, plus the menu bar's kicker logo `start-here-kde-symbolic` and the
`go-next-symbolic` submenu arrow, our own marks rather than Apple's;
the 2026-10-29 user decision supersedes its final-art status and queues placeholder tracking
below); the `org.macos8.desktop` Kvantum widget
style (Platinum palette and core-control art); the
`org.macos8.desktop` Lato font package (Lato Regular and Bold, the Debian copyright file
carrying the upstream SIL OFL 1.1 body, and the provenance record; installed by `make install`,
and the global theme selects its `Lato` family for the general, menu, toolbar, smallest-readable
and window-title fonts, while monospaced text keeps the user's fixed font); the GTK 3 and GTK 4
Platinum stylesheets under `theme/gtk/` (installed by the opt-in `install-gtk` target and
selected by `apply-gtk`; `make install` copies no GTK files); the standalone Firefox Platinum
sheets under `theme/firefox/` (its `userChrome.css` and `userContent.css` copied, and its
profile preference written, only by the opt-in `install-firefox` target); and the render and
fidelity tooling.
The live reference-comparison gate in `tests/test_render_surface.py` checks Aurorae window-chrome
regions when its render prerequisites are available (README.md, "Fidelity checking").
Firefox's `tests/test_firefox_theme_*.py` and `tests/test_firefox_content_*.py` modules
check stylesheet declarations and selector behavior;
those checks do not establish rendered Firefox pixels. Keep this distinction when assessing
progress toward pixel-perfect application chrome. README.md describes the reference set as the
source of truth for "menu bar, window chrome, widget metrics, icons and colour palette". The
prompt's surfaces and their status are each tracked here (updated 2026-10-21 by the
steward role): a **Qt widget style** for KDE applications (the desktop theme styles only
Plasma shell widgets, so a KDE app's own buttons, menus and scroll bars would keep the Breeze look) is served
by the global theme's selection of our Kvantum theme: the user answered
2026-10-18 that a pixel-matched Platinum style should ship as a Kvantum theme (a new
dependency) — shipped as the four-part "Mac OS 8.6 Kvantum widget style" series (each part
waited on the one before); a **cursor theme** was out of scope on 2026-10-17 because no reference
screenshot shows a cursor, so no pixel ground truth exists to match; on 2026-10-23 the plan role
queued it anyway as the theme's own Platinum-style pointer set (black-face, white-outline arrow,
text I-beam, pointing hand, busy hourglass, move cross, horizontal and vertical resize arrows,
NW-SE and NE-SW diagonal resize arrows, crosshair, circle-slash, drag-and-drop copy plus,
open and closed hands, the help question-mark arrow, the progress arrow with a small hourglass,
a pencil, the `zoom-in`/`zoom-out` magnifiers, and the drag-and-drop/forbidden aliases, not
traced from Apple's artwork), it
has landed inside the icon theme package with its provenance exception recorded in
`docs/invariants.md`, and `make apply-cursor`/`make remove-cursor` link it into the Xcursor path
and select it; Xcursor roles the theme does not name still come from the fallback cursor
theme; **system sounds** are out
of scope (not a visual surface, so the reference set cannot ground them); and a **lock screen** is
out of scope unless a broader login/lock-screen plan is taken up (QUESTIONS.md, answered
2026-10-21). The
shipped work should not be treated as the whole of the prompt.

Two answers on 2026-10-19 widened the scope, and both are recorded below in their landed
state (their landed-series entry narration trimmed 2026-11-11 by the steward role;
the entries themselves are archived in PLANS-DONE.md).
**GTK applications and Firefox** are in scope (QUESTIONS.md, answered 2026-10-19): the GTK 3
and GTK 4/libadwaita Platinum stylesheets under `theme/gtk/` are installed — and selected —
only by the opt-in `install-gtk` and `apply-gtk` targets (`make install` copies no GTK
files), and the opt-in `install-firefox` target copies the Firefox `userChrome.css` and
`userContent.css` sheets into a profile and writes the preference that selects them.
**The UI font** is vendored (QUESTIONS.md, answered 2026-10-19): Lato is installed as the
Charcoal-style body face and selected by the global theme for the general, menu, toolbar,
smallest-readable and window-title fonts, and monospaced text keeps the user's fixed font;
a Chicago-style menu face (part 2/3 of the font series) remains unplanned because its
redistribution licence is unresolved, and Lato is the only family the package installs.
GTK and Firefox applications keep their own chrome unless the opt-in GTK targets or the
Firefox install are used. Firefox chrome work since that series landed as single-surface
chrome plans (the downloads-panel and all-tabs rows, the sidebar frame, the menu-bar title
box, the tab faces and the app-menu rows). The `userContent.css` sheet styles surfaces
within six internal pages — about:downloads, about:config, about:preferences,
about:support, about:networking and about:telemetry — including preferences navigation and
controls, support tables and buttons, and telemetry navigation, tables and histograms; this
is surface coverage, not a claim of complete page theming. This content work extends the
2026-10-19 "style Firefox" answer rather than the brief's KDE/Plasma desktop UI, so it is
recorded here to keep the scope deliberate.

### Antialiased cursors, part 2/3: render VectorCursor art in the cursor generator and define the arrow design (planned 2026-11-12 by the plan role; split from part 2/2 2026-11-12 by the plan role)

**Goal.** Teach `tools/make_cursors.py` to render a `VectorCursor` (from part 1, `tools/cursor_vector.py`, already landed) in the art slot, and add the theme's own antialiased arrow design beside the arrow grid. Nothing is bound or regenerated here: every committed cursor file keeps its bytes. Part 3/3 binds the arrow and regenerates `left_ptr`. This split answers the feature role's 2026-11-12 "too large for one run" note on the former part 2/2.

**Approach.**
- **Arrow art.** In `tools/cursor_art_pointers.py`, add `ARROW_ART = VectorCursor(face=…, outline_width=2, design_size=32)` and `ARROW_HOTSPOT = (3, 3)` (design units), with a comment that this is this theme's own original outline. The face is this polygon, in order: tip `(3,3)`, down the vertical left edge to `(3,24)`, notch `(8,19.5)`, tail `(12,28)`, `(15,26.6)`, inner notch `(11.2,18.5)`, wing `(18,18.5)`, then back to the tip. This polygon is the design decision; the implementer may nudge a tail vertex by at most 1 unit only to keep the tail at least 2 units wide. Leave `ARROW_GRID`, `HOTSPOT` and `tools/cursor_art.py` unchanged.
- **Generator.** In `tools/make_cursors.py`, `_build_cursor_bytes` and `cursor_bytes` accept either a grid (tuple of row strings) or a `VectorCursor` in the `rows` slot:
  - A `VectorCursor` is rendered per size with `render_vector_rgba` and its hotspot is mapped with `vector_hotspot`. Its hotspot must lie in `[0, design_size)`. It is not passed through `_checked_rows` or `_checked_hotspot`.
  - A grid keeps today's `render_rgba` and `_scaled_hotspot` path and its existing refusals.
  - Any other value in the slot is refused with `ValueError`, as a malformed grid is today.
  - Keep the `lru_cache` (`VectorCursor` is hashable), and check the vector hotspot before the cache lookup so a bad one is refused on every call, as for grids.
  - `cursor_bytes()` defaults stay `ARROW_GRID` and `HOTSPOT`, so the committed `left_ptr` stays fresh.
  - Update the module docstring, which today says the module scales grids nearest-neighbour.
- **Tests.** In `tests/test_make_cursors.py`, add a test class for the vector path. Parse output with the `support.xcursor` reader the file already imports. Expected values come from the design coordinates scaled by `size/32`, not from rendered output.

**Files.** `tools/cursor_art_pointers.py`, `tools/make_cursors.py`, `tests/test_make_cursors.py`.

**Acceptance criteria.**
- **Arrow frames.** `make_cursors.cursor_bytes(rows=ARROW_ART, hotspot=ARROW_HOTSPOT)` parses to three frames at nominal sizes 16, 24 and 32, with hotspots `(1,1)`, `(2,2)` and `(3,3)`. In each frame:
  - The hotspot pixel has alpha 255.
  - The pixel containing design point `(6,14)` is `(0,0,0,255)`: `(3,7)`, `(4,10)` and `(6,14)` respectively.
  - The top-right `(size-1,0)` and bottom-right `(size-1,size-1)` pixels are `(0,0,0,0)`.
  - At least one pixel has alpha strictly between 0 and 255, and at least one opaque pixel has a channel strictly between 0 and 255. This is the antialiasing evidence.
- **Variants.** With the vector art, a moved face vertex, a dropped size or a moved hotspot each change the bytes.
- **Refusals.** A vector hotspot of `(32, 3)` or `(-1, 3)` raises `ValueError`, also after a cached build of the same art. A `rows` value that is neither a grid nor a `VectorCursor` (for example an integer) raises `ValueError`.
- **Scope.** `python3 tools/make_cursors.py` leaves every committed file under `theme/icons/org.macos8.desktop/cursors/` unchanged (`git status` shows none modified), and `cursor_bytes()` with no arguments still equals the committed `left_ptr`.
- `make check` passes after the final edit.

### Antialiased cursors, part 3/3: bind the arrow pointer to its vector art and regenerate it (planned 2026-11-12 by the plan role; split from part 2/2 2026-11-12 by the plan role; "requires part 2/3 landed")

**Goal.** Replace the arrow (`left_ptr` and its aliases `arrow`, `default`, `top_left_arrow` and `dnd-none`), the pointer users see most, with part 2/3's `ARROW_ART`, rendered natively at each nominal size. The other cursor families keep their grids until their own plans; they are routed per family as the BUGS.md cursor report asks.

**Approach.**
- **Binding.** In `tools/cursor_art.py`, import `ARROW_ART` and `ARROW_HOTSPOT` and bind `left_ptr` to them with the same aliases. Keep `ARROW_GRID` and `HOTSPOT` exported: the help, progress and context-menu tests in `tests/test_cursors_theme.py` still compare against those cells, though `CURSORS` no longer binds them. Update the module docstring: the arrow is now antialiased vector art.
- **Generator defaults.** In `tools/make_cursors.py`, the `cursor_bytes()` defaults become `ARROW_ART` and `ARROW_HOTSPOT`, so the default call still equals the committed `left_ptr`. Tests in `tests/test_make_cursors.py` that relied on the default being a grid pass `rows=cursor_art.ARROW_GRID, hotspot=cursor_art.HOTSPOT` explicitly.
- **Regenerate** with `python3 tools/make_cursors.py`. Only `left_ptr` and its four alias files change.
- **Tests.**
  - `tests/test_cursor_art_bindings.py`: admit exported `*_ART` constants beside `*_GRID`; `ARROW_ART` pairs with `ARROW_HOTSPOT`. Exempt `ARROW_GRID` from the bound-exactly-once rule through an explicit, commented set of reference grids that must be bound zero times. The hotspot-inside check uses design units for vector entries.
  - `tests/test_cursors_theme.py`:
    - Rewrite `test_each_frame_pins_the_hotspot_outline_tip_and_transparency` and `test_left_ptr_draws_the_classic_silhouette` to the frame criteria below, read from the committed file. Rewrite `test_a_corrupted_grid_dropped_size_or_moved_hotspot_changes_the_artifact` so a moved face vertex replaces the corrupted grid.
    - Update the `HOTSPOTS["left_ptr"]` row.
    - In the `cursor_art.CURSORS`-wide tests (`test_every_frame_pins_its_hotspot_face_and_outline`, `test_a_corrupted_grid_dropped_size_or_moved_hotspot_changes_each_glyph`, `test_every_cursor_grid_shields_its_black_from_transparent`), give vector entries an explicit branch: grid-cell pins and the shield check apply to grid entries only; the variant check moves a face vertex for vector entries. The "Antialiased text and hand cursors" entry reuses this shape.
  - `docs/invariants.md`: update the cursor-set row (the icon theme's `cursors/` row) and the nearest-neighbour hotspot row so they say which entries are vector-rendered.

**Files.** `tools/cursor_art.py`, `tools/make_cursors.py`, `tests/test_make_cursors.py` (only for default-argument tests), `tests/test_cursors_theme.py`, `tests/test_cursor_art_bindings.py`, `docs/invariants.md`, and the five regenerated files under `theme/icons/org.macos8.desktop/cursors/`.

**Acceptance criteria.**
- **Frames.** The committed `left_ptr` parses to three frames at nominal sizes 16, 24 and 32 with hotspots `(1,1)`, `(2,2)` and `(3,3)`, and meets part 2/3's per-frame arrow criteria: opaque hotspot pixel, `(0,0,0,255)` at the pixel containing design point `(6,14)`, transparent top-right and bottom-right corners, and antialiasing evidence.
- **Freshness and aliases.** The committed `left_ptr` equals `make_cursors.cursor_bytes()`, and each of its four aliases is byte-identical to it. A moved face vertex, a dropped size or a moved hotspot each change the bytes.
- **Bindings.** Removing `ARROW_ART` from `CURSORS`, or binding `ARROW_GRID` again, fails `tests/test_cursor_art_bindings.py`.
- **Scope.** `git diff --stat` touches no other cursor file: the grid-drawn cursors, including help, progress and context-menu, keep their committed bytes.
- `make check` passes after the final edit. This change does not close the BUGS.md cursor report: the user's visual verdict on the arrow, plus the remaining families, decide that.

### Antialiased text and hand cursors: draw the I-beam and pointing hand as vector art (planned 2026-11-12 by the plan role; "requires Antialiased cursors part 3/3 landed")

**Goal.** This is the next cursor family the BUGS.md cursor report routes: the text I-beam (`xterm`, aliases `text` and `ibeam`) and the pointing hand (`hand2`, aliases `hand1`, `pointer` and `pointing_hand`). They are the cursors users see most after the arrow. Redraw both as smooth, original, antialiased vector art, rendered natively at 16, 24 and 32 through the `VectorCursor` path that part 2/3 adds to `tools/make_cursors.py`. This entry adds no generator change.

**Approach.**
- **Art.** In `tools/cursor_art_pointers.py`, replace `XTERM_GRID` and `HAND2_GRID` with `XTERM_ART` and `HAND2_ART`. Both are `VectorCursor(face=…, outline_width=2, design_size=32)`. Set `XTERM_HOTSPOT = (15, 15)` and `HAND2_HOTSPOT = (14, 4)` in design units. Delete the two grids: they are bound only in `tools/cursor_art.py` (checked with grep), and no other grid reuses their cells. Rewrite their comments. These polygons are the design decision, listed in order:
  - I-beam: `(10,4) (20,4) (20,6) (16,6) (16,26) (20,26) (20,28) (10,28) (10,26) (14,26) (14,6) (10,6)`. The stem is 2 units wide, with serifs 10 units wide, and the shape is symmetric about x=15. The stem edges fall on pixel boundaries at 16 and 32, so it stays crisp there.
  - Hand: `(13,3) (15,3) (16,5) (16,12) (17,11) (19,11) (20,12) (21,11.5) (23,12) (24,14) (24,24) (21,28) (12,28) (9,25) (9,21) (6.5,17) (6.5,15.5) (8,14.5) (12,17) (12,5)`. This is a raised index finger 4 units wide, with knuckle bumps along the palm top, a thumb on the left and a rounded heel. The implementer may move a vertex by at most 1 unit, and only to satisfy a criterion below.
- **Binding.** In `tools/cursor_art.py`, import the two `*_ART` constants and bind `xterm` and `hand2` to them with the same aliases. Update the module docstring to say these two are also antialiased vector art.
- **Regenerate** with `python3 tools/make_cursors.py`.
- **Tests.**
  - `tests/test_cursors_theme.py`:
    - Update `HOTSPOTS` for both cursors to the values below.
    - Move `xterm` and `hand2` out of the grid-cell `PINNED_PIXELS` check into the per-size vector pins below. Use the same mechanism part 3/3 uses for `left_ptr`; if part 3/3 kept `left_ptr` in `PINNED_PIXELS` some other way, follow that shape.
    - In every `cursor_art.CURSORS`-wide test, treat both entries the same way part 3/3 treats the `left_ptr` vector entry: the corrupted-glyph variant, the shield-grid check and the differs-from-arrow check.
    - Add one test per cursor for the criteria below.
  - `tests/test_cursor_art_bindings.py`: the two `*_ART` constants pair with their `*_HOTSPOT` constants, under the rule part 3/3 added.
  - `docs/invariants.md`: update the cursor-set row and the hotspot row so they list `xterm` and `hand2` as vector-rendered.

**Files.** `tools/cursor_art_pointers.py`, `tools/cursor_art.py`, `tests/test_cursors_theme.py`, `tests/test_cursor_art_bindings.py`, `docs/invariants.md`, and the seven regenerated files `xterm`, `text`, `ibeam`, `hand2`, `hand1`, `pointer` and `pointing_hand` under `theme/icons/org.macos8.desktop/cursors/`.

**Acceptance criteria.** The values below are measured from the planned polygons with `tools/cursor_vector.py` on main. Tests derive their expectations from the design coordinates, not from the rendered output.
- **xterm.** The committed `xterm` parses to frames at 16, 24 and 32 with hotspots `(7,7)`, `(11,11)` and `(15,15)`. In each frame:
  - The hotspot pixel and the pixel containing design point `(15,15)` are `(0,0,0,255)`.
  - The pixel containing design point `(17,15)` is `(255,255,255,255)`: that is `(8,7)`, `(12,11)` and `(17,15)`.
  - All four corners are `(0,0,0,0)`.
  - At least one pixel has alpha strictly between 0 and 255.
  - The 24-pixel frame also has an opaque pixel with a channel strictly between 0 and 255, where the stem edge falls inside a pixel.
- **hand2.** The committed `hand2` parses to frames at 16, 24 and 32 with hotspots `(7,2)`, `(10,3)` and `(14,4)`. In each frame:
  - The hotspot pixel has alpha 255.
  - The pixel containing design point `(14,8)` (the finger) is `(0,0,0,255)`.
  - The pixel containing design point `(17,7)` (the outline beside the finger) is `(255,255,255,255)`.
  - All four corners are `(0,0,0,0)`.
  - At least one pixel has alpha strictly between 0 and 255, and at least one opaque pixel has a channel strictly between 0 and 255.
- **Freshness and aliases.** Each committed canonical file equals `make_cursors.cursor_bytes` for its entry, and each alias is byte-identical to its canonical file. A moved face vertex, a dropped size or a moved hotspot each change the bytes.
- **Scope.** `git diff --stat` touches no cursor file outside the seven listed above.
- `make check` passes after the final edit. This change does not close the BUGS.md cursor report. The remaining families are watch; help, progress and context-menu; resize, fleur and crosshair; and drag, grab and not-allowed. Each will get its own entry.

### GTK 4 suite extraction: isolate scale declarations (planned 2026-11-12 by the plan role)

**Goal.** `tests/test_gtk4_theme.py` is still about 5,700 lines after the nine-part extraction series. That breaks the principle that a file is small enough to read in one sitting. Move the scale declaration checks out the same way part 9/9 moved the calendar ones. This does not depend on the cursor entries above. No stylesheet or production behavior changes.

**Approach and files.**
- Create `tests/test_gtk4_scale.py` with `class TestGtk4Scale(Gtk4SheetRuleCases, unittest.TestCase)` and a one-line module docstring. Move every `TestGtk4Theme` method in `tests/test_gtk4_theme.py` whose name starts with `test_scale` into it, keeping each method's body and docstring unchanged. That is `test_scale_focus_outline_color`, `test_scale_focus_transition`, `test_scale_popup_buttons`, `test_scale` and the contiguous `test_scale_marks_value_ink` … `test_scale_parent_interaction_highlight_image` block. Methods that only mention scales but are named otherwise (for example `test_osd_progress_scale` and `test_osd_scale_thumbs`) stay where they are.
- Import the names the moved bodies use straight from the support modules the original imports them from: `SCALE_FOCUS` and `SCALE_SLIDER` from `support/gtk4_sheet.py`, palette names such as `BLACK`, `FACE`, `TROUGH` and `RAISED_BEVEL` from `support/platinum_palette.py`, and spec names such as `BUTTON_BEVEL` from `support/gtk_theme_spec.py`. Never import `tests/test_gtk4_theme.py` or inherit `TestGtk4Theme`. The helpers `assert_rule`, `assert_rule_group`, `assert_rule_after` and `assert_scale` come with `Gtk4SheetRuleCases`.
- Prune any import in `tests/test_gtk4_theme.py` that the remaining code no longer uses, and only those.
- In `docs/invariants.md`, rewrite each `tests/test_gtk4_theme.py::TestGtk4Theme::test_scale…` anchor to `tests/test_gtk4_scale.py::TestGtk4Scale::test_scale…`. Leave the rows' prose alone. Do not rewrite history in PLANS-DONE.md or BUGS-FIXED.md.

**Acceptance criteria.**
- Unittest discovery lists each moved method exactly once, under `test_gtk4_scale.TestGtk4Scale`. None of them is still listed under `test_gtk4_theme.TestGtk4Theme`. Every other `TestGtk4Theme` method is still listed there.
- For each moved method, the AST of its function definition is identical to the original's at this plan's base commit, checked once during the run (for example by comparing `ast.dump` output). This is a run-time check, not a new committed test.
- `grep -n 'test_gtk4_theme.py::TestGtk4Theme::test_scale' docs/invariants.md` prints nothing, and the invariants checker inside `make check` resolves every new anchor.
- `tests/test_gtk4_theme.py` shrinks by at least the moved methods' line count, and `tests/test_gtk4_scale.py` stays under about 450 lines.
- `git diff --stat` touches only `tests/test_gtk4_theme.py`, `tests/test_gtk4_scale.py` and `docs/invariants.md`. `make check` passes after the final edit.

## Done

### GTK 4 suite extraction, part 5/9: isolate the progressbar probe (planned 2026-11-11 by the plan role; "requires part 1/9 landed") — done 2026-11-11 by the review role

**Goal.** Give the progressbar rendered check its own small suite; sibling parts 2–8 move different probes and do not depend on each other.

**Approach and files.** Move only `TestGtk4Theme.test_progressbar_faces_render` from `tests/test_gtk4_theme.py` into new `tests/test_gtk4_progressbar_probe.py::TestGtk4ProgressbarProbe(unittest.TestCase)`. Import required constants from `support/gtk4_sheet.py` and palette/spec modules directly; do not import the original test module or inherit its test class. Preserve the complete method, including child-source string, opt-in guard, exit-77 handling, environment and timeout. Repoint the corresponding test anchors in `docs/invariants.md` in the same change; retain historical completed-plan records. Prune imports from the old module only when unused. The recursive guard in `tests/test_no_gtk_introspection.py` already covers new Python modules; no scanner extension is needed.

**Acceptance.** Discovery finds `test_progressbar_faces_render` once at the new dotted ID and no longer at the old one; its AST body and embedded child program match the original. Without GUI opt-in the moved probe skips, with no desktop window. The documented isolated Xvfb invocation, adapted to this new ID, either exercises the same assertions or reports the existing capability skip. The invariants checker resolves its moved anchors and `make check` passes. No probe-prelude extraction or pixel changes are part of this move.

**Completion and verification.** The probe moved intact to its standalone unittest class; the invariant anchor and isolated README invocation use the new ID. Focused unittest discovery without GUI opt-in found the new test and skipped before launching a child; the old module no longer defines it. The child source, environment, timeout and pixel assertions are unchanged. Xvfb is unavailable here, so the isolated render invocation was not executed; no new rendered-pixel verification is claimed. Tumwater owns the full project check.

### Reference-pixel sampler: select named colors in scanline runs (planned 2026-11-03 by the plan role) — done 2026-11-03 by the feature role

**Goal.** Isolate known border and stripe shades in a reference crop while retaining their separate equal-color runs. The current run report filters lengths, while named inclusion is limited to histograms; source and related finished-plan searches found no named run selection. This feature is independent of the waiting histogram plan.

**Approach and files.** Add repeatable `--run-color RRGGBB` in `tools/sample_arguments.py::build_parser`, destination `run_colors`, default None, using `tools/sample_validators.py::rgb_argument`. In `option_error`, immediately after the maximum-run-length dependency check, require `--runs` with diagnostic `--run-color requires --runs`. In `tools/sample_report_runs.py::_runs_result`, build a set of requested RGB tuples once and intersect membership with the existing length predicates on completed `_color_runs` records. Selection ignores opacity, but segmentation still uses RGB or RGBA according to `--alpha`; retain separate adjacent runs of different selected colors. Preserve the report schema, traversal order and absolute coordinates. Add `tests/test_sample_runs_colors.py` using `CliTestCase` and fixture patterns from `tests/test_sample_runs_max_length.py::TestSampleRunsMaximumLength`; extend `tests/test_sample_option_validation.py::TestSampleOptionValidation`. Document the flag beside the run length filters in README.md and amend the scanline-run row in docs/invariants.md. These six files form one bounded change of a few hundred lines including tests; decoding and search-mode diagnostics remain outside scope.

**Acceptance criteria.**
- For a crop at (2,1) containing successive pixels A,A,B,B,B,A,C,C, where A=`010203`, B=`090807`, C=`040506`, selecting A emits starts (2,1) and (7,1) with lengths 2 and 1. Selecting A and C also emits (8,1) with length 2, in scan order. Adding minimum length 2 removes the singleton A; maximum length 1 retains only that singleton. Omitted B never joins the A runs. Selecting adjacent distinct colors retains their individual run records.
- Repetition, lowercase and optional `#` give the same selection. An absent color yields JSON `runs: []` and text with image, region and axis lines but no run lines or added metadata. Selecting the complete crop palette matches the unfiltered report. Literal expected records cover an offset nonsquare rectangle in both axes, inferred single-column traversal, an explicit vertical singleton, crop-edge runs and equal colors on adjacent scanlines that remain separate. Text and JSON agree; direct-script and package invocations agree; omitting the flag retains existing fixtures.
- For adjacent RGBA pixels (1,2,3,0), (1,2,3,128), (4,5,6,255), selecting `010203` yields one length-2 run in RGB mode and two length-1 runs with their original alpha bytes in alpha mode. Minimum length 2 in alpha mode yields an empty list, proving segmentation precedes selection and length filtering. An RGB-only fixture reports alpha 255 when requested.
- Missing and malformed values exit 2 with empty stdout. Valid use outside runs mode, including ordinary samples, histogram and find-color modes, exits 2 with `--run-color requires --runs` before image access; guard `os.open`, `read_png_size` and `read_png` in validation tests. Earlier incompatible-option diagnostics retain precedence. Help lists the repeatable option and the absent parser default is None. Run `make check` after final edits.

### Fidelity CLI: extract parser construction from comparison orchestration (planned 2026-11-02 by the plan role) — done 2026-11-11 by the feature role

**Goal and grounding.** Make the fidelity entry point readable as a comparison workflow. `tools/fidelity.py::main` currently starts with parser construction and a nested `worst_pixel_limit` validator before it reads images. `tools/fidelity_arguments.py` already owns the other argument validators. The finished report-extraction plan deliberately retained parser setup in the entry point; heading searches found no separate parser-extraction plan. This maintenance task is independent of the queued sampler work.

**Approach and files.** Create `tools/fidelity_cli_parser.py::build_parser`, moving the existing `EscapingArgumentParser` construction and option declarations there without changing their order, help strings, defaults, destinations or types. Move `worst_pixel_limit` to `tools/fidelity_arguments.py` and import the validators into the new parser module. In `tools/fidelity.py::main`, replace the construction block with `build_parser().parse_args(argv)` and remove imports made unused by the move. Support package imports and direct-script execution using the existing conditional import pattern. Keep image reads, crop application, optional diagnostic scans and reporting in their current owners. Inspect repository references to validators imported through `tools.fidelity` before removing those imports; preserve an existing consumer's import path if needed. Bound the change to those three production files and a new `tests/test_fidelity_cli_parser.py`; adjust ownership docstrings in the touched files. No CLI behavior change or new dependency is intended.

**Acceptance criteria.** Before moving declarations, capture characterization fixtures in the new test module for normalized help text and parsed default/explicit namespaces, including both crops, diagnostic switches and combined budgets. The same fixtures pass after extraction. Use the existing unittest framework to verify two independently constructed parsers work, malformed crop/budget/worst-pixel arguments retain status 2 and escaped diagnostics, and help and invalid arguments do not call `tools/fidelity.py::_read_source`. Existing fidelity CLI, JSON, crop and direct-script tests continue to pass. Run `make check` after final edits. This structural change adds no guarantee to docs/invariants.md; its existing tooling contracts remain the acceptance boundary.

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
