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

_None yet._

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
