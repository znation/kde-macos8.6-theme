# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._

### Reference-pixel sampler: filter short vertical color-match runs (planned 2026-11-02 by the plan role)

**Goal.** Isolate sustained reference side-border spans while suppressing short matching glyph fragments. Source and related archive searches found vertical match lists and longest summaries, and a horizontal minimum-length filter, but no vertical match-list cutoff. This is independent of the waiting fidelity CLI plan.

**Approach and files.** Add optional `--min-match-column-run-length N` with the existing `positive_int` factory and absent default in `tools/sample_arguments.py::build_parser`. In `option_error`, immediately after the existing column-run dependency check, require `--match-column-runs` with diagnostic `--min-match-column-run-length requires --match-column-runs`; the existing check continues to require `--find-color`. In `tools/sample_report_search.py::_search_match`, filter completed `matched_column_runs` by inclusive length after `_MatchRuns.finish()` and before result assembly. Keep collector segmentation and full-region statistics and longest summaries intact; filter only the emitted vertical list, without joining separated intervals or adding metadata. Preserve column-major ordering and requested empty output (`match.column_runs: []` in JSON and `matching column runs: []` in text). Add `tests/test_sample_match_column_runs_min_length.py` using `support.cli_fixtures.CliTestCase`, extend `tests/test_sample_option_validation.py`, document the option beside `--match-column-runs` in README.md and amend the vertical-list tooling guarantee in docs/invariants.md. These six files bound one run; no collector refactor or decoding optimization is needed.

**Acceptance criteria.** Literal text/JSON expectations cover offset nonsquare crops with intervals shorter than, equal to and longer than the cutoff, separated intervals, bottom-edge flushing and adjacent matching columns that remain separate. Cover cutoff 1 matching omitted-option output, no matches, and a cutoff above crop height. Exercise adjacent unequal RGB values accepted by tolerance, the tolerance boundary, exact-alpha rejection, stored RGB beneath alpha zero and opaque alpha fallback. Combine the filter with the horizontal list and its own cutoff, both longest summaries, `--match-pixels 1`, fractions and row/column diagnostics; compare remaining match fields with unfiltered output, including a non-null longest vertical summary when the vertical list is emptied. Reject zero, negative, fractional, non-ASCII, malformed and missing values with status 2 and empty stdout. Valid numeric use with `--find-color` but without `--match-column-runs` must emit the dependency diagnostic before PNG header or decode reads. Check help, absent parser default, direct-script/package parity and a single bounded decode with `max_rows=y+height`. Run `make check` after final edits.

## Done
