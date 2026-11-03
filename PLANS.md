# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned
_None yet._

### Fidelity diagnostics: summarize the longest vertical mismatch run (planned 2026-11-02 by the plan role)

**Goal.** Locate an uninterrupted side-border defect without emitting the complete vertical mismatch list. Code and related archive searches found `--difference-column-runs` and the horizontal `--longest-difference-run`, but no vertical summary. This is independent of the waiting sampler histogram filter.

**Approach and files.** Add `--longest-difference-column-run` in `tools/fidelity_cli_parser.py::build_parser`. Add `longest_difference_column_run` in `tools/fidelity_spatial.py`, consuming `_iter_difference_axis_runs(..., vertical=True)` and retaining one best record: greatest length, then earliest `(x, y)`; return None for no mismatches. Reuse the iterator's strict maximum raw RGBA delta predicate and column boundaries. Wire both import paths and `main` in `tools/fidelity.py`; when the vertical list is also requested, select the summary from that column-major list without another scan. Extend `tools/fidelity_reports.py::report_data` with keyword-only `longest_column_run` and `include_longest_column_run` arguments so requested empty summaries emit top-level `longest_difference_column_run: null`, while omitted summaries have no key. Records contain crop-relative `{x, y, length}`. In `tools/fidelity_rendering.py::render_text`, print `longest difference column run: ` followed by the JSON record or `null`, after the horizontal summary when present and before the verdict. Add `tests/test_fidelity_longest_column_run.py` using `FidelityCliTestCase`, extend parser expectation tables in `tests/test_fidelity_cli_parser.py`, and document the option in README.md and the fidelity rows of docs/invariants.md. Follow the existing horizontal summary pattern; keep this to a few hundred changed lines including tests, without a broader diagnostic refactor.

**Acceptance criteria.** Literal expected records on a nonsquare fixture cover separated vertical segments, different delta magnitudes within a segment, ties within and between columns, empty columns, and bottom-edge flushing without joining columns. Cover identical images, one-pixel/one-row/one-column images, equality at tolerance, tolerance 255, alpha-only differences, implicit opaque alpha and stored RGB beneath zero alpha. CLI checks use distinct nonzero candidate/reference crop origins to prove crop-relative coordinates; assert text/JSON including requested null, direct-script invocation, simultaneous horizontal/vertical summaries and list/summary composition. Compare verdicts with and without the flag on passing and failing comparisons. Mock the helper to prove omission skips it and combined vertical list/summary requests reuse the list; mock the vertical list wrapper to prove summary-only mode avoids list materialization. Retain existing horizontal summary and vertical list expectations, update parser defaults and explicit-flag assertions, and run `make check` after final edits.

## Done
