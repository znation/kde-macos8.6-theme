# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Fidelity diagnostics: page through ranked worst pixels (planned 2026-11-03 by the plan role)

**Goal.** Inspect later severe mismatches without changing the compared crop or tolerance. `tools/fidelity_pixels.py::worst_pixels` currently retains the first N ranked mismatches; source searches and the finished worst-pixel plans cover that first page and source coordinates, but not a ranked offset. This work is independent of the waiting sampler parser extraction.

**Approach and files.** Add `--worst-pixel-offset K` in `tools/fidelity_cli_parser.py::build_parser`, defaulting to None, with a new ASCII-decimal nonnegative validator in `tools/fidelity_arguments.py`. In `tools/fidelity.py::main`, reject explicit use without `--worst-pixels` before source reads. Extend `tools/fidelity_pixels.py::worst_pixels` with keyword-only `offset=0`: retain the first `offset + limit` ranked candidates using the existing generator/heap selection, then construct records for the slice starting at offset. Clamp selection size to the compared pixel area before calling `heapq.nsmallest`. Ranking and tolerance apply before pagination; source-position translation and existing report formats need no changes. Document that selection storage grows with the requested offset plus page size, bounded by image area; this is report pagination, not reduced decoding or comparison work. Extend `tests/test_fidelity_pixels.py` and `tests/test_fidelity_cli_parser.py`, document the flag beside `--worst-pixels` in README.md, and update the worst-pixel guarantee in `docs/invariants.md`. Keep the implementation to these eight files and a few hundred changed lines; no report metadata or additional pagination feature is needed.

**Acceptance criteria.** Given a 3x2 opaque candidate with red values `[9, 5, 9, 0, 7, 9]` over a black reference, tolerance 5, limit 2 and offset 1, records are `(2,0,9)` then `(2,1,9)` in `(x,y,max_delta)` form; offset 3 returns only `(1,1,7)`, and offsets 4 and 100 return an empty list. Offset 0 produces the existing first-page records. Cover an alpha-only mismatch and RGB under zero alpha, plus different nonzero candidate/reference crop origins whose returned source positions identify the selected page's pixels. JSON and text expose the selected records, including an empty page; full-region metrics, verdict and exit status agree with the same comparison without an offset, including an aggregate-budget PASS. Package and direct-script invocations accept the option. Negative, fractional, empty and non-ASCII offsets, and an explicit offset without `--worst-pixels` (including zero), produce status 2 and empty stdout before image reads. Omitting the option preserves existing first-page output and the default no-report behavior. `make check` passes.

## Done

