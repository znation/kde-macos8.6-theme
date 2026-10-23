# Bugs

Known bugs, recorded by any loop and fixed by the bugfix loop.
Each bug: symptom, how to reproduce, suspected cause if known. Move fixed bugs to Fixed, with the
required `**Validation gap:** <tag> — <one sentence>` line recording what made the bug hard to
confirm (tag one of: none, no-repro, no-fake, real-run-needed, no-observability, slow-check,
unclear-invariant).

## Open

### The cursor generator test patches a removed `_write_atomic` symbol (found by the plan role 2026-10-23)

`tests/test_cursors_theme.py::TestMainErrors.test_reports_a_failed_write_and_stops_at_that_cursor`
reads and patches `make_cursors._write_atomic`, but `tools/make_cursors.py` no longer defines that
name: the dedupe change `15a43bb2` replaced the generator's private wrapper with the shared
`tools.atomic_write.write_bytes_atomically`. Running
`make check CHECK_TESTS=test_cursors_theme` errors with `AttributeError: module
'tools.make_cursors' has no attribute '_write_atomic'`. The test's intent is still valid --
simulate a failed write on the `arrow` alias and assert the generator stops after writing
`left_ptr` -- so patch the imported `make_cursors.write_bytes_atomically` name the generator
actually calls and keep the attempted/stop expectations.

**Validation gap:** none — the stale symbol fails deterministically when the module runs.

## Fixed
