# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Fidelity diagnostics: locate disjoint vertical mismatch runs (planned 2026-11-02 by the plan role)

**Goal and grounding.** Locate separated errors along vertical window borders without including unchanged gaps. `tools/fidelity_pixels.py::difference_column_bounds` encloses those gaps; `difference_runs` reports horizontal intervals only. Searches of fidelity source/tests, PLANS.md and related PLANS-DONE.md entries found no vertical mismatch-run report. The finished horizontal-run and column-bound plans supply the adjacent capabilities. This is independent of the held dialog-render bugs.

**Approach and files.** Add opt-in `--difference-column-runs` in `tools/fidelity.py::main`, importing a new `tools/fidelity_pixels.py::difference_column_runs(candidate, reference, tolerance)` in both import modes. Reuse `_absolute_deltas`; enumerate columns left-to-right and each column top-to-bottom, emitting maximal contiguous vertical runs as crop-relative `{"x": column, "y": start, "length": length}` records. Flush at each column boundary; adjacent mismatches remain together regardless of delta magnitude. A pixel differs when its maximum raw RGBA delta strictly exceeds tolerance; absent alpha is 255 and RGB beneath transparency participates. Add optional `column_runs` to `tools/fidelity_reports.py::report_data`, emitting JSON `difference_column_runs`; `render_text` prints `difference column runs: ...` after horizontal runs and before the verdict. Omission skips the helper and omits the key/line. Both run options may coexist; preserve the existing horizontal option's schema and semantics. Add `tests/test_fidelity_column_runs.py` using `support.fidelity_cli_case.FidelityCliTestCase`, document ordering, crop translation and potentially large output in README.md, and add a dated tooling guarantee to docs/invariants.md. These six files bound the implementation; no theme or decoder changes.

**Acceptance criteria.** Nonsquare synthetic fixtures assert exact column-major records for separated intervals, differing adjacent delta magnitudes, unchanged columns, top/bottom edges, final-column flushing and mismatches across column boundaries that must remain separate. Sum of lengths equals `compare(...).differing`; deltas equal to tolerance are excluded and tolerance 255 yields an empty list. Cover identical, single-pixel, single-row and single-column surfaces, alpha-only differences, missing alpha as opaque and stored RGB beneath alpha zero. CLI tests pin text/JSON with distinct nonzero crop origins, exclude outside-crop differences, compose both run flags with column bounds, and cover FAIL plus aggregate-budget PASS without changing the verdict. Mock omission to prove no helper call and no output field/line; exercise direct-script imports. Read and unequal-size errors retain status 2 and empty stdout. Run `make check` after final edits.

## Done
