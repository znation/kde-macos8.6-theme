# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Split reference sampler report handlers by mode, part 2/4: histogram handler (planned 2026-11-02 by the plan role; requires part 1/4 landed)

**Goal and grounding.** Isolate the Counter/selection/bounds/output branch in `tools/sample_reports.py::report`. Sibling part 1/4 supplies shared primitives; parts 3/4 and 4/4 extract independent search and runs branches and are not prerequisites.

**Approach and files.** Move the histogram branch into `tools/sample_report_histogram.py::report_histogram(args, image, width, height, header)`, assembling its region metadata locally. Move `Counter` and `nsmallest` imports with it and import traversal/formatting primitives directly from `sample_report_pixels`, using explicit package/direct-script paths. Replace only the histogram branch with delegation in `sample_reports.report`; remove imports there only when no remaining branch uses them. Update `tests/test_sample_histogram_bounds.py` to patch the new handler module's `_positioned_region_pixels` binding, preserving the optional-traversal assertion. Use existing histogram tests for output regressions, adding a direct-script case only if missing. Do not redesign counting or bounds.

**Acceptance criteria.** Histogram text/JSON fields and order, RGB/RGBA tuple tie sorting, top-color omitted totals, full-region fractions and absolute disconnected-color bounds retain their existing fixtures. `TestSampleHistogramBounds.test_bounds_traversal_is_optional_and_uses_single_decode` still proves plain histograms skip positioned traversal and each CLI call decodes once. Package and direct-script histogram invocations succeed. Search source/tests/markdown for stale ownership references; update docs only where a reference changes. Run `make check` after final edits. This part merges without parts 3/4 or 4/4.

### Split reference sampler report handlers by mode, part 3/4: color-search handler (planned 2026-11-02 by the plan role; requires part 1/4 landed)

**Goal and grounding.** Isolate color matching and its report from `tools/sample_reports.py::report`. Sibling part 1/4 provides traversal/formatting primitives; histogram part 2/4 and runs part 4/4 are independent.

**Approach and files.** Extract the find-color branch into `tools/sample_report_search.py::report_search(args, image, width, height, header)`, including local region metadata assembly. Import helpers directly from `sample_report_pixels` with explicit package/direct-script paths and delegate only this branch in `sample_reports.report`. Preserve full-region scanning and the bounded retained-coordinate prefix; avoid algorithm or parser changes. Use `tests/test_sample_find_color.py` and the existing match-alpha/pixels/fraction suites; add a missing exact-output or direct-script case in the relevant suite only if needed. Remove dispatcher imports only when unused by its remaining branches.

**Acceptance criteria.** Existing text and JSON search fixtures preserve default exact matching, explicit tolerance zero versus omission, exact alpha filtering with opaque fallback, stored RGB beneath transparency, absent-match null bounds, absolute disconnected-match bounds, bounded row-major coordinate prefixes and full-region fractions. Package and direct-script search invocations succeed; validation-before-read and bounded decode tests pass. Search source/tests/markdown for stale references and update actual ownership references only. Run `make check` after final edits. This part merges without parts 2/4 or 4/4.

### Split reference sampler report handlers by mode, part 4/4: scanline-runs handler (planned 2026-11-02 by the plan role; requires part 1/4 landed)

**Goal and grounding.** Isolate `_color_runs` and the runs-output branch of `tools/sample_reports.py::report`. Part 1/4 supplies shared primitives; parts 2/4 and 3/4 are independent extractions. Once the siblings merge, the dispatcher delegates four modes.

**Approach and files.** Move `_color_runs` and its branch into `tools/sample_report_runs.py`, exposing `report_runs(args, image, width, height, header)` and assembling region metadata there. Import helpers directly from `sample_report_pixels` with explicit package/direct-script paths. Delegate only the runs branch in `sample_reports.report`; remove its imports and local region metadata only when unused by remaining branches. Use `tests/test_sample_runs.py` for exact-output regressions and add a missing direct-script case there only if needed. Do not change run grouping or argument validation.

**Acceptance criteria.** Existing horizontal, vertical, single-pixel and separated-equal-color fixtures preserve run origins, lengths, order, hex formatting and text/JSON layout. RGBA equality distinguishes alpha transitions, missing alpha uses 255 and transparent RGB stays uncomposited. Package and direct-script runs invocations succeed; two-dimensional run requests still fail before reads. Search source/tests/markdown for stale symbol references and update actual ownership references only. Run `make check` after final edits. This part merges without parts 2/4 or 3/4.

## Done
