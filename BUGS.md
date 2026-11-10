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

### The GTK 3 selected-row colorswatch ring test pins a selector the landed sheet no longer ships (found by the dedupe role 2026-11-10)

**Symptom:** on a pristine checkout of main, `make check` fails in
`tests/test_gtk_theme_colorchooser.py::TestGtkThemeColorChooser::test_selected_row_color_swatch_ring`:
`self.selectors.count("row:selected colorswatch")` is 0, and
`GtkSheetRuleCases.assert_color_swatch_corners` also fails for the same selector.

**Repro:** `make check`; also `cd tests && python3 test_gtk_theme_colorchooser.py` (both fail with 2
failures in that module, verified 2026-11-10 with no local edits).

**Suspected cause:** the sheet
(`theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`) contains no `row:selected colorswatch` arm at all,
so the test's pin (`{"box-shadow": "0 0 0 2px #000000"}` at line 54) matches nothing. Reviewer commit
6aedc94d3 (2026-11-10, "tumwater(reviewer): Fix 5b0cb131") removed the sheet's copy as an alleged
"duplicate CSS rule", believing an identical rule existed further down the swatch block — but the
shipped sheet has no other copy (checked by grep, 2026-11-10), so the removal deleted the only
declaration the test and the corner inventory look for.

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
