# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned
_None yet._

### Reference-pixel sampler: filter short horizontal color-match runs (planned 2026-11-02 by the plan role)

**Goal.** Isolate long border spans for a chosen reference color while suppressing short matching glyph fragments. Source and related archive searches found horizontal match lists and longest-match summaries, plus the separate equal-color `--runs` filter, but no length filter for `--match-runs`. This is independent of the waiting fidelity selector extraction.

**Approach and files.** Add `--min-match-run-length N` using `positive_int` with an absent default in `tools/sample_arguments.py::build_parser`; `option_error` requires `--match-runs`, whose existing validation requires `--find-color`. In `tools/sample_report_search.py::_search_match`, filter the completed horizontal `matched_runs` returned by `_MatchRuns.finish()` by inclusive length before result assembly. Keep `_MatchRuns` and its full-region statistics and summaries intact: the option filters only the emitted horizontal list, without merging intervals or changing counts, bounds, fractions, coordinate limits, centroids, row/column diagnostics or either longest-run summary. In particular, a cutoff above the longest run yields an empty list while the longest summary still reports the original run. Preserve the report schema: JSON has `match.runs: []` when empty and text prints `matching runs: []`, with no additional metadata. Add `tests/test_sample_match_runs_min_length.py` using `CliTestCase`, extend `tests/test_sample_option_validation.py`, document the option beside `--match-runs` in README.md and amend its tooling guarantee in docs/invariants.md. These six files bound one run; this is an output filter with no decoding optimization or vertical filter.

**Acceptance criteria.** Literal text/JSON expectations cover offset multi-row crops with intervals shorter than, equal to and longer than the cutoff, row-edge flushing, separated matches and adjacent matching row boundaries that must remain separate. Cover cutoff 1 matching omitted-option output, no matches, and a cutoff above region width. Include adjacent unequal RGB values accepted by tolerance, the tolerance boundary, exact-alpha rejection, stored RGB beneath alpha zero and opaque alpha fallback. Combine the filter with `--match-pixels 1`, both longest summaries and the vertical list; compare the remaining match fields with unfiltered output, including a non-null longest horizontal summary when its list is emptied. Reject zero, negative, non-ASCII, malformed and missing values with status 2 and empty stdout; valid numeric use with `--find-color` but without `--match-runs` must emit `--min-match-run-length requires --match-runs` before either PNG reader runs. Check help, package/direct-script parity and the existing single bounded decode (`max_rows=y+height`). Run `make check` after final edits.

## Done
