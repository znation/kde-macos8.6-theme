# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Reference-pixel histogram: report each emitted color's centroid (planned 2026-11-02 by the plan role) — done 2026-11-02 by the feature role

**Goal and grounding.** Measure the spatial centre of several palette colors in one reference region without repeating single-color searches. `tools/sample_report_histogram.py::_histogram_result` already counts colors and optionally traverses coordinates for bounds and first positions; `tools/sample_report_search.py::_search_match` offers a centroid for one search target. Searches of sampler source, tests and planned/finished entries for histogram/color centroids found no equivalent histogram option. This is independent of the waiting fidelity report mapping plan.

**Approach and files.** Add boolean `--color-centroids` in `tools/sample_arguments.py::build_parser`, requiring `--histogram` through `option_error` before image reads. In `_histogram_result`, accumulate integer x/y sums for emitted colors during the existing optional positioned traversal, enabling that traversal for centroids too. Divide by each color's full region count and append `centroid: {x, y}` to its JSON record. In `report_histogram`, append `  centroid=X,Y` after existing text suffixes, using ordinary Python float formatting. Use absolute integer pixel indices without a half-pixel offset; group by RGB normally and exact RGBA with `--alpha`. Retain sums only for emitted colors under `--top-colors`, while including every occurrence of those colors in the requested region. Add no per-color rescans or stored coordinate lists. Touch these two tool files, new `tests/test_sample_histogram_centroids.py`, the histogram documentation in `README.md` outside the brief, and a new sampler guarantee row in `docs/invariants.md`.

## Done
