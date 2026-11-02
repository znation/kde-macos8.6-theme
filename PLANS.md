# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Split reference sampler report handlers by mode, part 1/4: pixel reports and shared traversal (planned 2026-11-02 by the plan role)

**Goal and grounding.** Make the ordinary pixel report independently readable and establish shared primitives for sibling parts 2/4 (histogram), 3/4 (search), and 4/4 (runs). Inspected `tools/sample_reports.py::report`: its final branches format JSON pixels, single-pixel text and rectangle text; `_hex`, `_region_pixels`, `_positioned_region_pixels` and `_region_alpha` serve several modes. The finished 2026-11-01 CLI split moved reporting into this module, not into separate mode handlers. This replaces the held whole-dispatcher refactor with one bounded extraction.

**Approach and files.** Add `tools/sample_report_pixels.py` containing those four primitives and `report_pixels(args, image, width, height, header)` for the three ordinary-output branches. Keep region metadata assembly inside the handler. In `tools/sample_reports.py`, import the primitives for remaining modes and delegate the final fallback to `report_pixels`; preserve runs/histogram/find-color precedence. Use explicit package/direct-script imports as in `tools/sample.py`; the new module must not import the dispatcher. Keep `_positioned_region_pixels` imported in the dispatcher while its histogram branch and patch seam still live there. Touch these two source files and `tests/test_sample_cli.py` / `tests/test_sample_alpha.py` only as needed for focused coverage. Leave parser, validation, loading and diagnostics in `sample.main`. No new framework or compatibility wrapper.

**Acceptance criteria.** Existing exact text and JSON pixel/rectangle fixtures pass through `sample.main`, including absolute row-major coordinates, control-bearing paths, alpha 255 fallback and stored RGB beneath zero alpha. Add a missing direct-script ordinary-output case if needed. Histogram, search and runs tests still pass with the moved helpers; `TestSampleHistogramBounds.test_bounds_traversal_is_optional_and_uses_single_decode` retains its patch target until part 2/4. Search source/tests/markdown for moved symbols and correct stale references. README.md and tooling invariants need edits only if an actual reference or test owner changes; the CLI contract stays intact. Run `make check` after final edits.

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
