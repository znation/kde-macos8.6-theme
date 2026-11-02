# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._

### Fidelity diagnostics: count over-tolerance pixels by row (planned 2026-11-02 by the plan role) — done 2026-11-02 by the feature role

**Goal and grounding.** Locate horizontal mismatch bands without losing their distribution inside a single difference rectangle or a bounded worst-pixel list. This helps inspect artifacts such as the button rows reported in BUGS.md without prescribing their fix. Inspected `tools/fidelity_pixels.py::channel_counts`, `tools/fidelity.py::main` and `tools/fidelity_reports.py::report_data`/`render_text`; searches of fidelity source/tests, the queue and archived fidelity headings found no row-count diagnostic. The finished bounds and channel-count plans cover spatial extent and channel totals, respectively. This plan can merge independently of the queued channel-maxima diagnostic.

**Approach and files.** Added opt-in `--difference-rows` and a `difference_rows(candidate, reference, tolerance)` helper. It returns one count per compared crop-relative row, including zero rows, counting each pixel once if any absolute RGBA delta strictly exceeds tolerance. Missing alpha is treated as 255 and RGB beneath transparency remains uncomposited. JSON and text include the requested dense array immediately before verdict; default output omits it. README documents crop-relative y indexing; `docs/invariants.md` records the behavior. Coverage is in `tests/test_fidelity_difference_rows.py`.

**Acceptance criteria.** Tests cover row distributions, tolerance boundaries, alpha and transparent RGB semantics, crop handling, text/JSON, verdicts, flag composition, default omission, direct-script use and CLI errors.

## Done
