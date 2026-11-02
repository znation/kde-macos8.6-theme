# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._

### Fidelity diagnostics: count over-tolerance pixels by row (planned 2026-11-02 by the plan role)

**Goal and grounding.** Locate horizontal mismatch bands without losing their distribution inside a single difference rectangle or a bounded worst-pixel list. This helps inspect artifacts such as the button rows reported in BUGS.md without prescribing their fix. Inspected `tools/fidelity_pixels.py::channel_counts`, `tools/fidelity.py::main` and `tools/fidelity_reports.py::report_data`/`render_text`; searches of fidelity source/tests, the queue and archived fidelity headings found no row-count diagnostic. The finished bounds and channel-count plans cover spatial extent and channel totals, respectively. This plan can merge independently of the queued channel-maxima diagnostic.

**Approach and files.** Add opt-in `--difference-rows` in `tools/fidelity.py::main` and a `difference_rows(candidate, reference, tolerance)` helper in `tools/fidelity_pixels.py`, called after `compare` validates the cropped images. Return one integer count per compared row, including zero rows, in increasing crop-relative y order. Count a pixel once when any absolute RGBA delta strictly exceeds tolerance; treat missing alpha as 255 and compare RGB beneath transparency without compositing. Scan the already loaded crops; leave `Metrics` and verdict rules intact. Extend `tools/fidelity_reports.py::report_data` with defaulted keyword-only `rows=None`; when requested add top-level JSON `difference_rows` with the dense count array, and have `render_text` emit `difference rows: ` followed by that array as JSON immediately before the verdict. Array index is crop-relative y; source y is that index plus the corresponding crop origin already reported. The output intentionally scales with crop height and is omitted, with no helper call, without the flag. Add `tests/test_fidelity_difference_rows.py` using `support.fidelity_cli_case.FidelityCliTestCase`, document the option and coordinate semantics in README.md, and append a dated tooling invariant in docs/invariants.md. These six files bound one run; no new dependency or theme-art changes are needed.

**Acceptance criteria.** Independently specified fixtures assert exact row arrays for separated horizontal bands, blank intervening rows, a single-row image, and pixels differing on several channels that count once. Cover delta equal to tolerance, delta just above it, tolerance 255, identical images, alpha-only errors with missing alpha in either argument order, and RGB differences under zero alpha. Assert array length equals compared height, each count is between zero and compared width, and its sum equals `metrics.differing`. Distinct nonzero candidate/reference crop origins must exclude mismatches outside the crops and preserve the documented index-to-source-y mapping. CLI text and JSON agree; ordinary mismatch FAIL and aggregate-budget PASS both retain the requested array. Verify composition with `--channel-counts`, default omission and no helper call, a direct-script invocation, and read/size errors returning 2 with empty stdout. Run `make check` after final implementation and documentation edits.

## Done
