# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned
_None yet._

### Fidelity diagnostics: report the centroid of mismatching pixels (planned 2026-11-02 by the plan role) — done 2026-11-02 by the feature role

**Goal and grounding.** Locate the spatial centre of scattered rendering errors without treating their enclosing rectangle's midpoint as their centre. `tools/fidelity_spatial.py` reports row/column counts, bounds and runs; searches found no mismatch-centroid diagnostic.

**Implemented.** Added opt-in `--difference-centroid`, a constant-space row-major scan using the existing raw RGBA predicate, crop-relative mean coordinates, explicit JSON/text null for no mismatches, tests, and documentation. The test fixture covers unequal mismatch magnitudes, tolerance exclusion, hidden RGB and opaque-alpha fallback; CLI coverage checks cropped coordinates, both verdict outcomes, and default omission. (planned 2026-11-02 by the plan role; completed within this run.)
### Reference-pixel sampler: count color matches per column (planned 2026-11-02 by the plan role)

**Goal and grounding.** Measure vertical color bands without listing matching coordinates or intervals. `tools/sample_report_search.py::_search_match` already collects per-row counts, but searches of the sampler, its tests and the plan archive found no `--match-columns` summary. This complements the finished per-row plan with one independently usable diagnostic.

**Approach and files.** Add opt-in `--match-columns` in `tools/sample_arguments.py::build_parser`, requiring `--find-color` through `option_error`. In `tools/sample_report_search.py::_search_match`, allocate a width-sized zero array only when requested and increment `columns[x - args.x]` inside the existing accepted-match branch, sharing its RGB-tolerance and exact-alpha predicate and positioned traversal. Emit the dense array as `match.columns` in JSON; `report_search` prints `matching columns: [..]` with compact JSON after any matching-rows line. Index zero denotes the region's first column; zero-match columns remain present, and `--match-pixels` does not limit these counts. Document this next to `--match-rows` in README.md. Add `tests/test_sample_match_columns.py`, following `tests/test_sample_match_rows.py` and its existing CLI fixture helpers. No new dependency or interval refactor is needed.

**Acceptance criteria.** Tests pin an offset, asymmetric rectangle containing zero-match columns; the array length equals region width and its sum equals `match.count`. Cover empty/full matches, single-row/column/pixel regions, RGB tolerance boundaries, exact alpha including hidden RGB and opaque fallback, and combination with `--match-rows` and `--match-pixels 1`. Assert exact JSON/text arrays, omission without the flag, help and direct-script output, and rejection without `--find-color` before image reads. A mocked positioned iterator proves combined row/column summaries use one traversal; a PNG-read assertion preserves crop-bounded decoding. Run `make check`.

## Done
