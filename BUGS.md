# Bugs

Known bugs, recorded by any role and fixed by the bugfix role.
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

### The file-dialog gate's header column-layout pins move with the time of day because the seeded files' mtime text drives the Date column's width (found by the feature role 2026-11-11)

**Symptom.** `tests/test_render_surface.py::TestFileDialogRender` passes at some hours and fails 13 of its landed tests at others. At 13:33–13:41 on this host three consecutive full `--file-dialog` runs agreed byte-for-byte outside the caret strip, but every header column-layout pin sat 7px right of the landed constants: the Size/Date divider columns measured at x=350/351 and x=400/401 instead of the landed x=343/344 and x=393/394, the Size caption inked x=356..377 instead of x=349..371, the Date caption x=407..432 instead of x=400..425, the style-drawn sort arrow x=337..347 instead of x=329..339, and the size-text ink rectangles x=375..393 instead of the landed x=368..386. The failing tests are `test_the_column_header_band_pins_its_face_and_dividers`, `test_the_header_inks_its_captions_and_sort_arrow` and `test_the_list_rows_pin_their_band_faces` (the landed part 1/2 pins); a dry-run of the landed class against the fresh capture fails exactly those 13 (13 subtest failures across the three tests). Earlier today the same gate ran green in `make check` and in isolation, so the layout varies within a single day although the seeded directory is fixed.

**Reproduce.** Render twice at times whose mtime display draws at different widths (e.g. hours apart, or across a narrow-digit boundary in the clock) and compare the header band: `python3 tools/render_surface.py <scratch>/a.png --file-dialog` twice, byte-comparing the header rows 99..122 and the size-text columns against the landed pins. The sidebar (x=6..138) showed no such movement across the measured runs.

**Suspected cause.** The seeded files are `touch()`ed at session start (`tools/render_clients.py`), so their mtime display is the session's wall clock, and KIO sizes the details-view columns from their content: the Date column's width follows the mtime text's rendered width (the theme's Lato digits have a narrow `1`), and the stretch Name column absorbs the difference, shifting the Size/Date dividers, both captions, the sort arrow and the size-text x-positions together. `tools/render_clients.py`'s docstring claims "the absence of clock-dependent content keep[s] every capture deterministic" — the mtime display is exactly such content. A fix probably narrows the gate's header pins to clock-stable structure or anchors them per-column-relative rather than absolute; that re-derivation belongs to the landed header-band pins (part 1/2's territory), not to the sidebar pins this entry's neighbour added.

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
