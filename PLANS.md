# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._

### Fidelity report assembly: make optional diagnostic fields explicit in one mapping (planned 2026-11-02 by the plan role)

**Goal and grounding.** Shorten the repetitive optional-field assembly in `tools/fidelity_reports.py::report_data` so its argument-to-JSON-key correspondence can be read together. It currently uses a separate `is not None` branch for each diagnostic, including renamed pairs such as `channels`/`channel_counts` and `explanation`/`worst_pixel`. The finished CLI/report and rendering extractions established module boundaries, but did not consolidate this mapping. This maintenance task is independent of the waiting sampler bounds plan.

**Approach and files.** In `report_data`, replace just the diagnostic assignment chain with a local ordered tuple of `(output_key, supplied_value)` pairs and one loop assigning values when `value is not None`. Preserve the current insertion order, signature, base envelope and separate threshold branches. Keep the tuple inside the function; add no registry, callback, wrapper or module. Extend `tests/test_fidelity_reports.py::TestReportData` with table-driven characterization before the refactor. Read the fidelity JSON tooling guarantee in `docs/invariants.md`; this preserves that contract and its test anchor. Limit edits to the report module and its existing test module.

**Acceptance criteria.** Tests explicitly enumerate the existing diagnostic keyword/output-key pairs rather than importing the implementation's mapping. Exercise each keyword alone, asserting its exact key and value and absence of the other optional keys; `None` omits a diagnostic, while empty lists and dictionaries remain present. A combined case pins optional-key insertion order and verifies supplied nested records are not mutated. Existing default serialization, configured threshold, crop/source-bounds and text-rendering tests continue to pass. Do not move scan calls or change output schemas, formatting, verdicts or CLI options. Run `make check` after final edits.

## Done
