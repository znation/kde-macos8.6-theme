# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned
### Reference-pixel sampler: report enclosing color-match spans per row (planned 2026-11-02 by the plan role)

**Goal and grounding.** Measure the horizontal extent of a sampled bevel color on each row without listing every matching run. `tools/sample_report_search.py::_search_match` reports whole-region bounds, row counts and contiguous runs, but no dense row-span summary; searches of sampler code/tests and planned/finished entries found no matching capability. The finished fidelity row-bounds diagnostic compares two images; this addition locates a color in one reference image and is independently usable.

**Approach and files.** Add opt-in `--match-row-bounds` to `tools/sample_arguments.py::build_parser`, with `option_error` requiring `--find-color` before image reads. In `_search_match`, allocate a height-sized list only when requested and update each accepted match's row inside the existing positioned traversal and RGB-tolerance/exact-alpha predicate. JSON adds `match.row_bounds`: one entry per requested row, `null` for no match, otherwise `{"x": LEFT, "width": RIGHT-LEFT+1}` with absolute image x coordinates. Index zero denotes the region's first row. Disconnected matches enclose intervening gaps; this is not a contiguous-run report. `report_search` prints compact JSON on `matching row bounds: [...]` after existing row/column summaries. `--match-pixels` limits only the coordinate list. Touch these two modules, new `tests/test_sample_match_row_bounds.py`, README.md's sampling section and the sampler section of docs/invariants.md; leave interval collection in `_MatchRuns` intact.

**Acceptance criteria.** Following `tests/test_sample_match_rows.py::TestSampleMatchRows`, use an asymmetric offset crop with disconnected matches, an empty row and a singleton row to pin absolute x, inclusive width and dense row ordering in text and JSON. Cover no matches, full matches, single-row/column/pixel crops, RGB tolerance boundaries, exact alpha with hidden RGB and opaque fallback. Combine with row/column counts, both run flags and `--match-pixels 1` to prove spans cover matches beyond the retained coordinate. Assert output omission without the flag, help/direct-script behavior and rejection without `--find-color` before image reads. A wrapped positioned iterator must show one traversal for combined diagnostics, and the PNG read must retain its requested-bottom-row bound. Run `make check`.

## Done
