# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._

### Fidelity diagnostics: count over-tolerance pixels by row (planned 2026-11-02 by the plan role) — done 2026-11-02 by the feature role

**Goal and grounding.** Locate horizontal mismatch bands without losing their distribution inside a single difference rectangle or a bounded worst-pixel list. This helps inspect artifacts such as the button rows reported in BUGS.md without prescribing their fix. Inspected `tools/fidelity_pixels.py::channel_counts`, `tools/fidelity.py::main` and `tools/fidelity_reports.py::report_data`/`render_text`; searches of fidelity source/tests, the queue and archived fidelity headings found no row-count diagnostic. The finished bounds and channel-count plans cover spatial extent and channel totals, respectively. This plan can merge independently of the queued channel-maxima diagnostic.

**Approach and files.** Added opt-in `--difference-rows` and a `difference_rows(candidate, reference, tolerance)` helper. It returns one count per compared crop-relative row, including zero rows, counting each pixel once if any absolute RGBA delta strictly exceeds tolerance. Missing alpha is treated as 255 and RGB beneath transparency remains uncomposited. JSON and text include the requested dense array immediately before verdict; default output omits it. README documents crop-relative y indexing; `docs/invariants.md` records the behavior. Coverage is in `tests/test_fidelity_difference_rows.py`.

**Acceptance criteria.** Tests cover row distributions, tolerance boundaries, alpha and transparent RGB semantics, crop handling, text/JSON, verdicts, flag composition, default omission, direct-script use and CLI errors.

### Reference-pixel sampler: report histogram color fractions (planned 2026-11-02 by the plan role)

**Goal and grounding.** Compare palette coverage between differently sized reference crops without manually dividing counts. Inspected `tools/sample_arguments.py::build_parser`, `tools/sample.py::main`, `tools/sample_reports.py::report` and `tests/test_sample_histogram.py::TestSampleHistogram`; histogram records expose counts but no fractions. Source/test searches and related archived histogram entries cover counting, top-color limits, alpha grouping and color bounds, rather than normalized coverage. This plan is independent of the waiting fidelity-row diagnostic.

**Approach and files.** Add boolean `--color-fractions` to `build_parser`; `main` rejects its use without `--histogram` before image reads, returning 2 with empty stdout. In `report`'s histogram branch, derive each emitted color's fraction as `count / (args.width * args.height)` from existing counts, with no extra pixel traversal or decoding. JSON color records gain numeric `fraction`; text appends `  fraction=VALUE` after existing color fields, using Python's ordinary float string representation without explicit rounding. The denominator remains the complete requested region with `--top-colors`, never the emitted-color total. Do not add omitted-fraction metadata: existing `omitted_pixels` and region dimensions suffice. Preserve RGB/RGBA grouping, transparent RGB, count ordering, bounds and top-color summaries. Add `tests/test_sample_histogram_fractions.py` using `support.cli_fixtures.CliTestCase` and `support.png_fixtures`; document the option and denominator in README.md and append a dated tooling invariant to docs/invariants.md. These six files bound one implementation run; no dependency or theme-art change is needed.

**Acceptance criteria.** Independently specified offset-region fixtures pin unequal fractions, a repeating fraction such as 1/3, tied counts, and a uniform/single-pixel fraction of 1.0; outside pixels cannot affect the denominator. Assert text/JSON numeric agreement, approximately unit sum for complete output, and fractions summing below one with a truncated top-color list. Cover top limits at/above distinct count, combination with `--color-bounds`, RGB grouping across alpha variants and RGBA separation with `--alpha` including alpha zero and opaque fallback. Existing omitted-option schema/text regressions remain green. Misuse with ordinary sampling, runs or find-color returns 2 with empty stdout before header or row reads. Assert bounded decoding and a successful direct-script invocation. Run `make check` after the final implementation and documentation edit.

## Done
