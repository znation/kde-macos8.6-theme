# Bugs

Known bugs, recorded by any loop and fixed by the bugfix loop.
Each bug: symptom, how to reproduce, suspected cause if known. Move fixed bugs to Fixed, with the
required `**Validation gap:** <tag> — <one sentence>` line recording what made the bug hard to
confirm (tag one of: none, no-repro, no-fake, real-run-needed, no-observability, slow-check,
unclear-invariant).

## Open

### The symlink-containment guard is reimplemented at five sites (found by the steward role 2026-10-19)

**Symptom:** the guarantee "refuse a contributor-supplied repository file whose path resolves
outside the repository" is implemented five times. Four copies use one mechanism and one uses
another: `tests/support/containment.py` (the shared guard), `tests/placeholders.py`'s
`_resolves_within`, `tests/invariants.py`'s inline check, and `tools/theme_defaults.py`'s
`_require_within_repo` compare `os.path.realpath` results with `startswith(base + os.sep)`;
`tools/reference_validation.py`'s `_resolves_within` uses
`Path.resolve().is_relative_to(directory.resolve())`. A refinement applied to one copy does not
reach the other four, so a later reader can adopt a stale copy and reopen the leak class the
guard exists to close.

**Why this is a structural risk:** the same contributor-content leak has been fixed one module at
a time. Seven `no-fake` Fixed entries in `BUGS-FIXED.md` are that class, each a module that read
its repository file bare and needed its own symlink fixture to confirm the leak:
`tests/placeholders.py`'s `cross_check`; `tests/invariants.py`'s `cross_check`;
`tests/support/checker_mutations.py`'s register reads; the color-scheme provenance test; the
desktop-theme copy-identity tests; `tests/support/splash_fixtures.py`; and
`tests/support/package_metadata.py`. The shared `tests/support/containment.py` was extracted along
the way, but four modules still keep a local copy of the check.

**Suspected cause:** `tools/` cannot import `tests/support/`, so `tools/theme_defaults.py` and
`tools/reference_validation.py` grew their own copies; `tests/placeholders.py` and
`tests/invariants.py` kept a local check from before the shared helper existed, even though both
already import `support.containment` for another read.

**Suggested direction:** move the guard to one module both trees can import, route all five sites
through it, and pin the shared behaviour with one test. No fix here: this entry records the risk
so the next reader of a contributor-supplied file does not add a sixth copy.

## Fixed

### `make uninstall`'s color-scheme warning misses an indented `[General]` section header (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** when `$XDG_CONFIG_HOME/kdeglobals` opens its `[General]` section with a line
that has leading whitespace, `make uninstall` does not warn about a still-selected scheme.
KDE trims each line before parsing it, so the indented header still opens `[General]` and its
`ColorScheme` key is the live selection; the diagnostic claims to read kdeglobals "the way
KDE reads it", so the missing warning is a real, if low-severity, gap.

**Reproduction:**
`tests/test_colorscheme_install.py::TestInstall.test_make_uninstall_warns_for_an_indented_general_section`
writes `"  [General]\nColorScheme=MacOS8\n"` as kdeglobals and runs `make uninstall`; before
the fix it emitted no warning.

**Cause:** the uninstall recipe's `awk` recognised a section header only at the start of the
line (`/^\[/`), so an indented `[General]` was never seen as the current section and its
`ColorScheme` key was skipped.

**Fix:** the `awk` now matches and strips leading whitespace before the `[` (`/^[[:space:]]*\[/`),
matching KDE's trim-before-parse behaviour.

**Validation gap:** unclear-invariant — no test or doc stated that KDE's config reader trims a
line before matching a section header, so that invariant had to be established before the
parser could be pinned to it.
