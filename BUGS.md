# Bugs

Known bugs, recorded by any loop and fixed by the bugfix loop.
Each bug: symptom, how to reproduce, suspected cause if known. Move fixed bugs to Fixed, with the
required `**Validation gap:** <tag> — <one sentence>` line recording what made the bug hard to
confirm (tag one of: none, no-repro, no-fake, real-run-needed, no-observability, slow-check,
unclear-invariant).

## Open

### The PNG tRNS-order test names an unimported `_PNG_SIGNATURE` (found by the plan role 2026-10-23)

`tests/test_png_malformed.py::TestTrnsColorTypeValidation.test_palette_trns_before_plte_is_refused`
builds its blob from `_PNG_SIGNATURE`, but the module no longer imports that name: the change
that moved the stream helpers into `tests/support/png_fixtures.py` removed the import while one
use remained. `make check` stops with `NameError: name '_PNG_SIGNATURE' is not defined`, so the
suite is red on main. Reproduce with
`make check CHECK_TESTS=test_png_malformed.TestTrnsColorTypeValidation.test_palette_trns_before_plte_is_refused`.
Suspected cause: an incomplete rename or removal in the test module; `tests/support/png_fixtures.py`
still defines and exports the helper.

**Validation gap:** none — the missing import fails deterministically whenever that test runs.

## Fixed
