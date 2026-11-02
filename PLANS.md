# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._

### Fidelity diagnostics: locate disjoint horizontal mismatch runs (planned 2026-11-02 by the plan role)

**Goal and grounding.** Distinguish separated errors along a bevel from one continuous bad band. `tools/fidelity_pixels.py::difference_row_bounds` encloses unchanged gaps; `worst_pixels` limits the reported points. Source, test and plan-archive searches found no diagnostic reporting complete contiguous mismatch intervals. This is independent of the queued reference sampler extension.

**Approach and files.** Add opt-in `--difference-runs` to `tools/fidelity.py::main`, with package and direct-script imports of a new `tools/fidelity_pixels.py::difference_runs(candidate, reference, tolerance)`. Reuse `_absolute_deltas` to enumerate maximal horizontal runs of pixels whose maximum raw RGBA delta strictly exceeds tolerance. Emit a flat row-major list of `{"x": start, "y": row, "length": length}` records in crop-relative coordinates; flush at each row boundary, even when the next row starts with a mismatch. Different delta magnitudes belong to the same run when adjacent pixels both exceed tolerance. Missing alpha means 255; RGB beneath transparency participates. Return an empty list for identical surfaces. Wire an optional `runs` keyword through `tools/fidelity_reports.py::report_data` to JSON key `difference_runs`; `render_text` prints the same array as `difference runs: ...` after column bounds and before the verdict. Omission skips the helper and omits the key/line. No new threshold or verdict semantics. Add `tests/test_fidelity_difference_runs.py` using `support.fidelity_cli_case.FidelityCliTestCase`, document crop translation and potentially large output in README.md, and add the dated guarantee to docs/invariants.md. These six files bound one implementation run; no image decoder or theme changes.

**Acceptance criteria.** Nonsquare synthetic fixtures pin separated intervals, adjacent mismatches with different deltas, unchanged rows, first/last columns, final-row flushing, and mismatches straddling a row boundary that must remain separate. Sum of lengths equals `compare(...).differing`; runs exclude deltas equal to tolerance and are empty at tolerance 255. Cover single-pixel, single-row and single-column surfaces, alpha-only differences, absent alpha as opaque, and stored RGB beneath zero alpha. CLI tests pin exact text/JSON records with distinct offset crop origins, exclusion of outside-crop differences, composition with existing row bounds/counts, FAIL and aggregate-budget PASS, opt-in omission with a mock proving no helper call, and direct-script success. Read and size errors retain status 2 and empty stdout. Run `make check` after final edits.

## Done
