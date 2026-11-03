# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Reference-pixel sampler: name run-collector mode switches (planned 2026-11-02 by the plan role)

**Goal.** Make run-collection mode selection reviewable without counting positional booleans. `tools/sample_report_search.py::_search_match` passes six boolean arguments to `tools/sample_match_runs.py::_MatchRuns.__init__`; direct collector tests also use positional switches. Source and archive-heading searches found the run-list and longest-run features, but no keyword-only mode cleanup. This is independent of the waiting fidelity count extraction.

**Approach and files.** Add a keyword-only separator after `height` in `_MatchRuns.__init__`, preserving the six existing parameter names and defaults. Spell out `horizontal`, `vertical`, `summarize`, `collect_runs`, `summarize_columns` and `collect_column_runs` at the `_search_match` call. Convert direct collector construction in `tests/test_sample_longest_match_run.py::TestSampleLongestMatchRun` and `tests/test_sample_longest_match_column_run.py::TestSampleLongestMatchColumnRun` to named switches. Keep this to those four files; preserve the CLI contracts and collection guarantees in the sampler rows of `docs/invariants.md`.

**Acceptance criteria.** Repository search finds no positional mode arguments at `_MatchRuns` call sites. Existing horizontal and vertical summary-only tests still prove that the corresponding full lists stay empty, and existing combined-list CLI tests retain their expected results. Add one nonsquare CLI fixture exercising horizontal summary with vertical list collection and the converse: assert literal longest-run coordinates and lengths, literal opposite-axis lists, and omission of the unrequested summary/list keys. This catches switches being cross-wired at the production call. Retain text/JSON, tie ordering, crop offsets, tolerance/alpha and direct-script coverage. No CLI flags, report fields or theme values change. Run `make check` after final edits; this is a small call-interface refactor, not a new mode abstraction.

## Done
