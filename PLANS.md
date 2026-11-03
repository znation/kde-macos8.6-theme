# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Fidelity diagnostics: summarize the longest horizontal mismatch run (planned 2026-11-02 by the plan role)

**Goal.** Locate a long horizontal border defect without printing the full mismatch-run list. `tools/fidelity_spatial.py::_difference_axis_runs` currently accumulates intervals; code and archive searches found run-list diagnostics but no longest-mismatch summary. This is independent of the waiting sampler call-interface cleanup.

**Approach and files.** Add `--longest-difference-run` to `tools/fidelity_cli_parser.py::build_parser`. In `tools/fidelity_spatial.py`, extract the existing segmentation loop into `_iter_difference_axis_runs`, yielding records in its existing axis order; retain `_difference_axis_runs` as a list wrapper for the existing public functions. Add `longest_difference_run`, consuming horizontal intervals and retaining one best record: greatest length, then earliest `(y, x)`; return `None` for no mismatches. Use the existing strict maximum-raw-RGBA-delta predicate, row boundaries and edge flushing. In both import paths and `main` of `tools/fidelity.py`, wire the opt-in helper. When horizontal lists and summary are both requested, derive the summary from the collected list instead of scanning twice. Extend `tools/fidelity_reports.py::report_data` with keyword-only summary and explicit inclusion arguments, following the centroid pattern so requested empty results serialize as null. `tools/fidelity_rendering.py::render_text` prints `longest difference run: ` followed by the JSON record or `null`, after run-list diagnostics. JSON uses top-level `longest_difference_run` with crop-relative `{x, y, length}`. Update README.md and the fidelity rows of docs/invariants.md; add `tests/test_fidelity_longest_run.py` and adjust parser-schema expectations in `tests/test_fidelity_cli_parser.py`. Keep the implementation and tests to a few hundred changed lines; no vertical summary in this task.

**Acceptance criteria.** Literal expected records on a nonsquare fixture cover separated runs, differing delta magnitudes within a run, equal-length ties, empty rows, and right-edge flushing without joining adjacent rows. Cover identical images, one-pixel/one-row/one-column images, equality at tolerance, tolerance 255, alpha-only differences, missing alpha as 255 and stored RGB beneath zero alpha. CLI tests assert crop-relative coordinates with distinct candidate/reference origins, text/JSON including requested null, direct-script imports, composed list/summary output and the same verdict with and without the option. Mock the summary helper to prove an omitted option skips it; mock the list wrapper to prove summary-only mode does not materialize the full list. Exercise the iterator directly to prove records are yielded lazily, and retain existing horizontal/vertical list expectations. Update parser default/flag expectation tables. Run `make check` after final edits.

## Done
