# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._

### Fidelity diagnostics: count over-tolerance pixels by column (planned 2026-11-02 by the plan role)

**Goal and grounding.** Locate vertical mismatch bands when inspecting side borders and widget edges. `tools/fidelity_pixels.py::difference_rows` reports horizontal distributions, while bounds and bounded worst-pixel reports do not give a column distribution. Searches of tools, tests, PLANS.md and PLANS-DONE.md found no `difference_columns`/`--difference-columns` capability; inspected archived fidelity headings and the finished channel-maxima entry distinguish the existing diagnostics. This is a small counterpart to the row diagnostic already recorded above, independently mergeable without changing its output.

**Approach and files.** Add opt-in `--difference-columns` in `tools/fidelity.py::main` and a `tools/fidelity_pixels.py::difference_columns(candidate, reference, tolerance)` helper using `_absolute_deltas`. For equally sized validated cropped images, return a dense list of length width, counting each pixel once in its column when any raw RGBA delta strictly exceeds tolerance. Include zero columns, treat missing alpha as 255, and preserve RGB beneath transparency. Scan only when requested, after the existing comparison validates dimensions; do not change `Metrics` or verdict calculation. Extend `tools/fidelity_reports.py::report_data` with defaulted keyword-only `columns=None`; emit top-level JSON `difference_columns` and text `difference columns: [N, ...]` immediately before the verdict (after the row line when both are requested). Omit the key and line without the flag. Add `tests/test_fidelity_difference_columns.py` using `support.fidelity_cli_case.FidelityCliTestCase`; document crop-relative x indexing in README.md and add a dated tooling invariant in docs/invariants.md. These six files bound one run; no dependency or theme asset changes are needed.

**Acceptance criteria.** Use an independently specified asymmetric multi-row fixture with zero and nonzero columns and multiple channel errors at one pixel to pin exact counts without double counting. Test identical images, tolerance equality and 255, alpha-only errors with a missing alpha plane in either argument order, and raw RGB differences beneath zero alpha. CLI fixtures with distinct candidate/reference crop origins exclude outside mismatches and assert exact text/JSON column order, width, and sum equal to `metrics.differing`. Verify simultaneous row/column output and equal totals, a budget-based PASS retaining nonzero counts, unchanged verdicts with the flag, default key/line omission and skipped helper, direct-script invocation, and read/size errors returning 2 with empty stdout. Run `make check` after the final implementation and documentation edits.

## Done
