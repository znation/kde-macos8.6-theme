# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Reference-pixel sampler centroid, part 2/2: report the centroid of matching pixels (planned 2026-11-02 by the plan role; requires part 1/2 landed)

**Goal and grounding.** Measure the placement of irregular or disconnected color features without treating their enclosing rectangle's center as their center of mass. `tools/sample_report_search.py::report_search` already counts matching pixels and reports bounds, optional coordinate prefixes and runs, but does not accumulate coordinate sums. Searches for centroid/center-of-mass support in tools, tests and planned/finished plan headings found no existing capability. This is independent of the fidelity-rendering extraction above.

**Approach and files.** Build on sibling part 1/2's `_search_match` result boundary. Add opt-in `--match-centroid` in `tools/sample_arguments.py::build_parser`, requiring `--find-color` through `option_error`. In `_search_match`, accumulate integer absolute x/y coordinate sums for matching pixels during its existing traversal when requested; divide each by the full match count when assembling the returned dictionary. Use the existing RGB-tolerance and exact-alpha predicate, with equal weight per matching pixel, no alpha weighting and no additional scan or coordinate list. JSON adds `match.centroid` as `{"x": sum_x / count, "y": sum_y / count}` or `null` for no matches. `report_search` prints `centroid: X,Y` using Python's ordinary float formatting, or `centroid: none`, immediately after the bounds line. Integer pixel indices are the coordinate convention: no half-pixel offset. Add `tests/test_sample_match_centroid.py` using the fixture and CLI patterns in `tests/test_sample_match_fraction.py`, extend `tests/test_sample_option_validation.py`, and document the option in README.md's sampling section and the sampler guarantees in `docs/invariants.md`. No theme art or visual constants change.

**Acceptance criteria.** A cropped asymmetric fixture with disconnected matches proves absolute fractional means and distinguishes the centroid from the bounds midpoint; an out-of-crop match is excluded. Pin text and JSON for zero matches, a singleton and multiple matches. Tolerance, exact-alpha filtering (including RGB under zero alpha) and opaque alpha fallback select the same pixels as count/bounds; `--match-pixels 1` does not truncate the centroid. Exercise the option alongside fraction and both run diagnostics. Without the flag the field and text line are absent and existing reports retain their format. Invalid use without `--find-color` returns 2 with empty stdout before containment or PNG reads; extend the compatibility tests accordingly. Confirm direct-script output and package CLI output agree for a fixture and decoding retains `max_rows=y+height`. Run `make check` after final edits. Keep this to the two tool modules, focused tests and the two documentation files.

## Done
