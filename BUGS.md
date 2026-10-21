# Bugs

Known bugs, recorded by any loop and fixed by the bugfix loop.
Each bug: symptom, how to reproduce, suspected cause if known. Move fixed bugs to Fixed, with the
required `**Validation gap:** <tag> — <one sentence>` line recording what made the bug hard to
confirm (tag one of: none, no-repro, no-fake, real-run-needed, no-observability, slow-check,
unclear-invariant).

## Open

### KDE's config-reading rules are re-derived in three readers, so a quirk fixed in one is not checked in the others (found by the steward role 2026-10-19)

**Symptom:** three independent readers implement KDE's INI dialect:
`tests/support/kde_config.py`'s `read` (the reader the theme tests use), the inline `awk` in the
`_uninstall` recipe (`Makefile`, the "Read ... the way KDE reads it" block), and
`tools/theme_defaults.py`'s `defaults_groups`. Each defines the same rules itself: strip a leading
UTF-8 BOM, trim each line before it can open a section or key, keep key names case-sensitive, and
let the last duplicate key win. A rule learned by one reader is not exercised on the other two.
They already disagree: `kde_config.read` returns `MacOS8` for a `ColorScheme:MacOS8` line
(`configparser` accepts `:` as a delimiter), while the Makefile's awk reads no value for it, and
no test or doc says which reading matches KDE.

**Why this is a structural risk:** the same quirk has already been fixed once per reader. On
2026-10-19 the missing-BOM case was fixed twice: in `make uninstall`'s awk (`BUGS-FIXED.md`:
"`make uninstall`'s color-scheme warning misses a `kdeglobals` that opens with a UTF-8 BOM") and
in `kde_config.read` (`BUGS-FIXED.md`: "`tests/support/kde_config.py` cannot read a KDE INI that
opens with a UTF-8 BOM"); the commit that made the second fix (`23978a0`) drops the same change
from `theme_defaults` as a duplicate. The awk then separately learned the indented-header rule
(`BUGS.md ## Fixed`) and last-key-wins (`BUGS-FIXED.md`: "`make uninstall`'s color-scheme warning
reads the first duplicate `ColorScheme` key, not the last"), and `defaults_groups`'
indented-heading case was pinned only later (`1b71ead`). The gap tags record this as recurring
(the BOM pair as `no-observability`, the header and duplicate-key cases as `unclear-invariant`),
but neither promoted remedy covers it: the mutation harness targets the shipped registers and
checkers, and `docs/invariants.md` has no row for KDE INI semantics. No test feeds one fixture
text through more than one reader, so a divergence is invisible:
`tests/test_colorscheme_install.py` drives the Makefile reader through `make uninstall` with
hand-written fixtures, `tests/test_kde_config.py` pins `kde_config.read` with its own, and
`tests/test_theme_defaults.py` pins `defaults_groups` with a third set.

**Reproduction:** no failing behaviour is needed; each reader passes its own cases. Confirm the
drift with a scratch `kdeglobals` holding `[General]` then `ColorScheme:MacOS8`:
`kde_config.read` returns `MacOS8`, and the `_uninstall` recipe's awk prints nothing.

**Suggested direction:** keep one fixture corpus of small KDE INI texts (BOM, indented header,
indented key, duplicate key, case mismatch, colon-delimited key, comment, blank line, `%` in a
value) and one test that runs the corpus through `kde_config.read`, `defaults_groups` and the
Makefile's reader (through `make uninstall`, as the install tests already do), asserting the same
interpretation and recording the chosen KDE semantics in `docs/invariants.md`'s `tooling`
section; a new quirk then lands in one place and fails in every reader that misses it.

## Fixed
