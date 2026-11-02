# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._

### Fidelity reports: isolate text and JSON rendering from report assembly (planned 2026-11-02 by the plan role)

**Goal and grounding.** Keep output formatting readable as fidelity diagnostics grow. `tools/fidelity_reports.py` now combines report assembly, verdict and coordinate helpers with `render_text` and `render_json`; its text renderer alone spans roughly 125 lines. The finished CLI/report split extracted these responsibilities together, rather than providing a dedicated rendering module. Searches of source and plan headings found no subsequent rendering-module extraction. This maintenance task is independent of the waiting sampler feature.

**Approach and files.** Move `tools/fidelity_reports.py::render_text` and `render_json` into new `tools/fidelity_rendering.py`, carrying their `json` and `escape_controls` imports with them and preserving package/direct-script loading. Keep report construction and diagnostic helpers in `fidelity_reports.py`. Update both import branches and the ownership docstring in `tools/fidelity.py`; update the report module's ownership docstring too. In `tests/test_fidelity_reports.py`, import the renderers from their new owner and retain assembly imports from the existing owner. Add focused characterization cases there before moving code, using explicit result dictionaries and size-only image stubs. These four files bound this extraction; no compatibility wrappers, new abstraction, dependency, or output-schema change is needed. Read the tooling guarantees in `docs/invariants.md`; their output contracts and test paths should continue to hold without a new guarantee.

**Acceptance criteria.** Pin exact text lines and exact JSON serialization for a default report and a report combining optional diagnostics and configured budgets, including diagnostic order, empty arrays versus omitted fields, crop/source coordinates, PASS/FAIL, float formatting and escaped path controls/non-ASCII JSON. Retain the existing RGB/RGBA formatting cases. Renderer calls do not mutate their input dictionaries and require only width/height from the two image stubs. Existing CLI coverage plus direct-script and package invocations of the same small fixture agree on stdout, stderr and exit status for text and JSON. The extraction preserves signatures and output; PNG reads, metric computation and verdict calculation stay in their current owners. Run `make check` after final edits.

### Reference-pixel sampler: report the centroid of matching pixels (planned 2026-11-02 by the plan role)

**Goal and grounding.** Measure the placement of irregular or disconnected color features without treating their enclosing rectangle's center as their center of mass. `tools/sample_report_search.py::report_search` already counts matching pixels and reports bounds, optional coordinate prefixes and runs, but does not accumulate coordinate sums. Searches for centroid/center-of-mass support in tools, tests and planned/finished plan headings found no existing capability. This is independent of the fidelity-rendering extraction above.

**Approach and files.** Add opt-in `--match-centroid` in `tools/sample_arguments.py::build_parser`, requiring `--find-color` through `option_error`. In `report_search`, accumulate integer absolute x/y coordinate sums for matching pixels during its existing traversal when requested; divide each by the full match count at output. Use the existing RGB-tolerance and exact-alpha predicate, with equal weight per matching pixel, no alpha weighting and no additional scan or coordinate list. JSON adds `match.centroid` as `{"x": sum_x / count, "y": sum_y / count}` or `null` for no matches. Text prints `centroid: X,Y` using Python's ordinary float formatting, or `centroid: none`, immediately after the bounds line. Integer pixel indices are the coordinate convention: no half-pixel offset. Add `tests/test_sample_match_centroid.py` using the fixture and CLI patterns in `tests/test_sample_match_fraction.py`, extend `tests/test_sample_option_validation.py`, and document the option in README.md's sampling section and the sampler guarantees in `docs/invariants.md`. No theme art or visual constants change.

**Acceptance criteria.** A cropped asymmetric fixture with disconnected matches proves absolute fractional means and distinguishes the centroid from the bounds midpoint; an out-of-crop match is excluded. Pin text and JSON for zero matches, a singleton and multiple matches. Tolerance, exact-alpha filtering (including RGB under zero alpha) and opaque alpha fallback select the same pixels as count/bounds; `--match-pixels 1` does not truncate the centroid. Exercise the option alongside fraction and both run diagnostics. Without the flag the field and text line are absent and existing reports retain their format. Invalid use without `--find-color` returns 2 with empty stdout before containment or PNG reads; extend the compatibility tests accordingly. Confirm direct-script output and package CLI output agree for a fixture and decoding retains `max_rows=y+height`. Run `make check` after final edits. Keep this to the two tool modules, focused tests and the two documentation files.

Needs review 2026-11-02 by feature: too large for one run


## Done
