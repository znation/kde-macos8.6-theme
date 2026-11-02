# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Reference-pixel sampler: separate option compatibility validation from image loading (planned 2026-11-02 by the plan role)

**Goal and grounding.** Keep `tools/sample.py::main` focused on loading a validated region and dispatching its report. It currently checks histogram/search option dependencies, scan-axis compatibility and the alpha/search conflict inline, while `tools/sample_arguments.py` owns parser construction and scalar validators. Source and archive searches found no separate compatibility-validation helper or plan; the completed CLI mode-handler split retained diagnostics and exit decisions in the entry point. This task is independent of the waiting fidelity parser extraction.

**Approach and files.** Add `tools/sample_arguments.py::option_error(args) -> str | None`, moving the pre-containment option-combination checks from `main` into this pure helper in their existing order. Return the first existing diagnostic string, or `None`; do not print, exit, mutate the namespace or access the filesystem. In `tools/sample.py::main`, call it immediately after parsing and pass a returned message to the existing `report_error("sample", message)`. Preserve package and direct-script imports. Keep argparse's scalar/mutually-exclusive-mode validation, containment, image bounds and PNG reads in their current owners. Limit implementation to those two modules and new `tests/test_sample_option_validation.py`; no table-driven rule engine or new dependency is needed.

**Acceptance criteria.** Before extraction, characterize each existing combination rejection through `sample.main` using `support.cli_fixtures.CliTestCase`: exact stderr, status 2 and empty stdout, with `read_png_size` and `read_png` mocked to prove neither is called. Pin first-error precedence with multiple invalid dependent options, including a search dependency together with the alpha/search conflict. After extraction the same cases pass. Direct helper tests verify valid ordinary, histogram, search and explicit-axis rectangular-run namespaces return `None` without namespace mutation; include explicit zero tolerance/alpha and a one-pixel run. Retain successful CLI coverage for those modes and a direct-script invalid-combination case. Existing sampler tests, including containment, bounds and bounded row decoding, pass through `make check` after final edits. This structural change adds no new invariant; preserve the sampler contracts in docs/invariants.md.

## Done
