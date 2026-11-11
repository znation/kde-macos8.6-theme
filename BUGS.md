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

### An environment-supplied HOME value executes GNU make functions during Makefile parsing (found by the security role 2026-11-02)

An environment `HOME` whose value carries make syntax is expanded as make syntax when the
Makefile reads `$(HOME)` at parse time, so make functions in it run before any target, guard or
recipe — including under `make -n`, which is supposed to run nothing. Reproduce with

    env HOME='$(shell touch /tmp/canary)' make -n help

which creates `/tmp/canary` (confirmed by an adversarial reviewer on 2026-11-11 with make exit 0
and the canary file present) before `help` prints anything.

**Suspected cause:** `XDG_DATA_HOME := $(if $(filter /%,$(XDG_DATA_HOME_ENV)),$(XDG_DATA_HOME_ENV),$(HOME)/.local/share)`
expands `$(HOME)` while parsing, and GNU make expands environment-origin variables as recursive
variables, so their values are evaluated as make syntax. The `shell_unsafe_chars` guard closes
the shell-quoting route for values pasted into recipe shells; it does not see the raw value of a
variable make has already expanded — the Makefile's own comment on that guard says a value
carrying make `$( )` is expanded by make while the guard reads it, and calls that documented
behaviour outside the shell route the guard closes. The impact is parse-time command execution
from an untrusted environment value that the guards treat as a path.

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
