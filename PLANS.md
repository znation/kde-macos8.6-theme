# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned
_None yet._

### Reference-pixel sampler: count color matches per row (planned 2026-11-02 by the plan role)

**Goal and grounding.** Locate horizontal bands of a sampled color without dumping matching coordinates or intervals. `tools/sample_report_search.py::_search_match` already evaluates the RGB tolerance and exact-alpha predicate in one positioned traversal, but reports a whole-region count and optional coordinates, centroid and intervals rather than dense row counts. Searches of sampler code, tests and planned/finished plan text found no `--match-rows` capability; the finished horizontal and vertical matching-segment plans cover intervals instead. This work is independent of the waiting fidelity-axis extraction.

**Approach and files.** Add boolean `--match-rows` in `tools/sample_arguments.py::build_parser` and reject it without `--find-color` in `option_error`, before image reads. In `_search_match`, allocate a height-sized zero list only when requested and increment index `y - args.y` inside the existing accepted-match branch. Add `match.rows` to JSON only with the option. In `report_search`, append `matching rows: ` followed by the compact JSON integer array after existing optional interval lines. Array index zero denotes the requested region's first row; include zero-match rows. Reuse the predicate and traversal, without an image mask or another decode. Add `tests/test_sample_match_rows.py` using `support.cli_fixtures.CliTestCase`, document the flag beside color-search options in README.md, and add its guarantee to the sampler section of docs/invariants.md. These five files bound the implementation; no new dependency or theme asset is needed.

**Acceptance criteria.** An offset nonsquare fixture with outside-region matches, separated matching pixels and an empty interior row pins literal expected arrays in text/JSON; sum of row counts equals the full match count. Cover absent matches, full coverage, single row, single column and single pixel. Pin tolerance-boundary inclusion, exact-alpha exclusion, stored RGB under zero alpha and opaque fallback. Combine with `--match-pixels 1`, `--match-runs` and `--match-column-runs` to verify row counts still cover the complete region and existing fields retain their expected values. Assert default key/line omission, missing `--find-color` returns 2 with empty stdout before header/decode reads, help mentions the flag, and direct-script/package invocations agree. Spy on the positioned iterator to verify a single traversal and retain the existing `max_rows=y+height` decode bound. Run `make check` after final implementation and documentation edits; keep changes within a few hundred lines including tests.

### Fidelity diagnostics: report the centroid of mismatching pixels (planned 2026-11-02 by the plan role) — done 2026-11-02 by the feature role

**Goal and grounding.** Locate the spatial centre of scattered rendering errors without treating their enclosing rectangle's midpoint as their centre. `tools/fidelity_spatial.py` reports row/column counts, bounds and runs; searches found no mismatch-centroid diagnostic.

**Implemented.** Added opt-in `--difference-centroid`, a constant-space row-major scan using the existing raw RGBA predicate, crop-relative mean coordinates, explicit JSON/text null for no mismatches, tests, and documentation. The test fixture covers unequal mismatch magnitudes, tolerance exclusion, hidden RGB and opaque-alpha fallback; CLI coverage checks cropped coordinates, both verdict outcomes, and default omission. (planned 2026-11-02 by the plan role; completed within this run.)
## Done
