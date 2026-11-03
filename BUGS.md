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

### A stray `check.log` full-check output is tracked at the repository root (found by the plan role 2026-11-03)

**Symptom.** `git ls-files` names `check.log` at the repository root; its content is one run's complete `make check` capture (it opens with the check harness invocation `python3 tools/check_parallel.py` and the per-worker `===== <module>: exit 0 =====` progress lines), no repository file, recipe or test reads it, and every subsequent check run would make the tracked copy stale. It is a run artifact of the 2026-11-03 plan run that wrote its check output to a fixed path in the worktree root instead of `$TMPDIR`, and the run's commit swept the file into the tree.

**Reproduce.** `git ls-files | grep -x check.log` prints `check.log`; `grep -rn "check.log" Makefile tools tests README.md docs` finds no consumer. `make check` stays green because `tests/test_scratch_hygiene.py`'s offender scan only rejects top-level tracked files whose first line names a run scratch directory (`/tmp/tumwater-run-*/tmp.*`), which a plain check capture does not.

**Suspected cause.** The run tooling records check output at a worktree-local scratch path out of habit (`check.log` in the root), and nothing in the scratch-hygiene test recognizes a check-output file, so the commit bandwagoning every worktree file shipped it.

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
