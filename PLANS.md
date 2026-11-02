# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._

### Fidelity reports: isolate text and JSON rendering from report assembly (planned 2026-11-02 by the plan role)

**Goal and grounding.** Keep output formatting readable as fidelity diagnostics grow. `tools/fidelity_reports.py` now combines report assembly, verdict and coordinate helpers with `render_text` and `render_json`; its text renderer alone spans roughly 125 lines. The finished CLI/report split extracted these responsibilities together, rather than providing a dedicated rendering module. Searches of source and plan headings found no subsequent rendering-module extraction. This maintenance task is independent of the waiting sampler feature.

**Approach and files.** Move `tools/fidelity_reports.py::render_text` and `render_json` into new `tools/fidelity_rendering.py`, carrying their `json` and `escape_controls` imports with them and preserving package/direct-script loading. Keep report construction and diagnostic helpers in `fidelity_reports.py`. Update both import branches and the ownership docstring in `tools/fidelity.py`; update the report module's ownership docstring too. In `tests/test_fidelity_reports.py`, import the renderers from their new owner and retain assembly imports from the existing owner. Add focused characterization cases there before moving code, using explicit result dictionaries and size-only image stubs. These four files bound this extraction; no compatibility wrappers, new abstraction, dependency, or output-schema change is needed. Read the tooling guarantees in `docs/invariants.md`; their output contracts and test paths should continue to hold without a new guarantee.

**Acceptance criteria.** Pin exact text lines and exact JSON serialization for a default report and a report combining optional diagnostics and configured budgets, including diagnostic order, empty arrays versus omitted fields, crop/source coordinates, PASS/FAIL, float formatting and escaped path controls/non-ASCII JSON. Retain the existing RGB/RGBA formatting cases. Renderer calls do not mutate their input dictionaries and require only width/height from the two image stubs. Existing CLI coverage plus direct-script and package invocations of the same small fixture agree on stdout, stderr and exit status for text and JSON. The extraction preserves signatures and output; PNG reads, metric computation and verdict calculation stay in their current owners. Run `make check` after final edits.

## Done
