# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._

### Fidelity diagnostics: report maximum absolute error per channel (planned 2026-11-02 by the plan role)

**Goal and grounding.** Expose a sparse channel outlier even when another channel dominates the global maximum. `tools/fidelity_metrics.py::compare` computes channel maxima internally but `Metrics` retains just the global maximum; channel counts and bias describe extent and direction rather than each channel's peak. Searches of fidelity source/tests and planned/archived headings found no per-channel peak report. Related finished entries cover channel counts, bias and the global maximum-delta gate. This plan is independent of the waiting sampler coordinate-list plan.

**Approach and files.** Add opt-in `--channel-maxima` in `tools/fidelity.py::main`, calling a new `tools/fidelity_pixels.py::channel_maxima(candidate, reference)` only after comparison validates and crops the images. Return integer `r`, `g`, `b`, `a` maximum absolute byte deltas over the compared pixels, treating missing alpha as 255 and preserving RGB beneath transparency. Use the existing equal-size validated-image precondition; no additional image reads. Keep this diagnostic independent of tolerance and gate budgets, without changing `Metrics` or verdict calculation. Add a defaulted keyword-only `maxima=None` to `tools/fidelity_reports.py::report_data`; when requested emit top-level JSON `channel_maxima` and text `channel maximum delta (R, G, B, A): R G B A` immediately before the verdict. Omit both without the flag and skip the helper. Add `tests/test_fidelity_channel_maxima.py` using `support.fidelity_cli_case.FidelityCliTestCase`, document the flag in README.md and add its dated tooling invariant in docs/invariants.md. These six files and a small helper bound one implementation run; no new dependency or theme artwork is needed.

**Acceptance criteria.** Independently specified fixtures put different channel peaks at different pixels, including a small isolated peak alongside a larger error in another channel; assert exact maxima in text and JSON. Cover identical images, delta 255, RGB-only peers, alpha-only errors with one missing alpha plane in either argument order, and RGB changes beneath zero alpha. Distinct candidate/reference crop origins exclude larger errors outside the selected regions. Tolerance 0 versus 255 returns identical maxima, while PASS/FAIL still follows the existing gate; an aggregate-budget PASS retains nonzero maxima. Verify composition with `--channel-counts` and `--channel-bias`, omission of the new key/line and no helper call without the flag, a direct-script invocation, and read/size errors returning 2 with empty stdout. Run `make check` after the final implementation and documentation edits.

## Done
