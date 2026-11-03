# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned
_None yet._

### Reference-pixel sampler: summarize the longest vertical color-match run (planned 2026-11-02 by the plan role)

**Goal.** Locate an uninterrupted reference side-border band without printing the full vertical interval list. Searches of tools, tests and plan headings found the horizontal `--longest-match-run` summary and vertical `--match-column-runs` list, but no vertical longest-run summary. This is independent of the queued fidelity bounds extraction.

**Approach and files.** Add `--longest-match-column-run` in `tools/sample_arguments.py::build_parser` and require `--find-color` through `option_error` before image reads. Extend `tools/sample_match_runs.py::_MatchRuns` with independently controlled vertical summary and list collection, preserving existing constructor calls. Use the existing per-column starts in the row-major traversal; send both mismatch closures and bottom-edge flushes through `_end_column`. Track the best vertical segment by descending length then ascending `(x, y)`, explicitly comparing ties because closure order is not column-major. Summary-only mode retains the active column starts and one best segment, without building or sorting `column_runs`. In `tools/sample_report_search.py::_search_match` and `report_search`, enable vertical tracking when either vertical option is requested; emit `match.longest_column_run` as absolute `{x, y, length}` or `null`, and text `longest matching column run: X,Y,LENGTH` or `longest matching column run: none`, after any horizontal summary. Reuse the existing RGB-tolerance/exact-alpha predicate and full-region traversal. Add `tests/test_sample_longest_match_column_run.py`, document the option in README.md and add its test-backed tooling row to docs/invariants.md. Keep this to these six files and a few hundred lines including tests; no theme values change.

**Acceptance criteria.** Explicit JSON/text expectations cover offset nonsquare crops, disconnected vertical intervals, empty/full regions, single pixel/row/column and bottom-edge flushes. A tie fixture must close a higher-x segment first but select the lower-x segment, and another must select the earlier y within one column. Cover RGB tolerance boundaries, exact-alpha rejection, missing alpha as 255 and preserved RGB beneath transparency. Coordinate limits must not truncate the summary. Exercise coexistence with horizontal summary and both full lists, omission without the new flag, help, direct-script invocation and rejection without `--find-color` before PNG reads. A direct collector test must prove summary-only mode leaves `column_runs` empty while finding the expected best segment; retain existing horizontal-summary and vertical-list tests. Run `make check` after final edits.

## Done
