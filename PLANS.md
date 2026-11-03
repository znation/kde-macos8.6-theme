# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned
_None yet._

### Reference-pixel sampler: report enclosing color-match spans per column (planned 2026-11-02 by the plan role)

**Goal and grounding.** Measure the vertical extent of a sampled border or bevel color in each column without enumerating disconnected runs. `tools/sample_report_search.py::_search_match` currently offers column counts, contiguous column runs and whole-region bounds, but no dense enclosing column spans. Source/test and archive searches found no sampler column-bounds capability; the finished fidelity column-bounds feature compares two images. This is independently mergeable alongside the queued row-span plan, with no dependency on it.

**Approach and files.** Add opt-in `--match-column-bounds` in `tools/sample_arguments.py::build_parser`; `option_error` requires `--find-color` before image reads. In `_search_match`, allocate a width-sized span list only when requested and update it for accepted matches in the existing positioned traversal, using the existing RGB-tolerance/exact-alpha predicate. JSON adds `match.column_bounds`: one entry per requested column, `null` when empty, otherwise `{"y": TOP, "height": BOTTOM-TOP+1}` using absolute image y coordinates. Index zero denotes the region's first column; disconnected matches enclose gaps. `report_search` prints compact JSON on `matching column bounds: [...]` after the existing count summaries and after row bounds if that diagnostic is present when implemented. `--match-pixels` limits only the coordinate list. Touch these two modules, new `tests/test_sample_match_column_bounds.py`, README.md's sampling section and the sampler section of docs/invariants.md. Leave `_MatchRuns` interval bookkeeping intact; no shared abstraction or row-span implementation is required.

**Acceptance criteria.** Model tests on `tests/test_sample_match_rows.py::TestSampleMatchRows`: use an asymmetric offset crop with disconnected vertical matches, an empty column and a singleton column to pin absolute y, inclusive height and dense left-to-right ordering in text and JSON. Cover empty/full matches, single-row/column/pixel crops, RGB tolerance boundaries, exact-alpha filtering with hidden RGB and opaque fallback. Combine column bounds with row/column counts, both run flags and `--match-pixels 1` to prove spans include matches beyond retained coordinates. Assert omission without the flag, help/direct-script behavior and rejection without `--find-color` before image reads. Wrap `_positioned_region_pixels` to verify combined diagnostics use one traversal; assert the PNG read remains bounded to the requested bottom row. If row bounds have merged, include them in the combination test. Run `make check`.

## Done
