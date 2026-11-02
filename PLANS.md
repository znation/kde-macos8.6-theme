# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Fidelity input loading: isolate containment and bounded PNG reads (planned 2026-11-02 by the plan role)

**Goal and grounding.** Give fidelity's input policy one focused owner. `tools/fidelity.py::_read_source` currently combines repository containment, alpha-preserving PNG loading, crop-bottom row bounds and a full-image retry for sideways overflow inside the CLI module. The finished parser and report extractions do not extract this input helper; source and archive searches found no dedicated fidelity source-loading module or queued extraction. This is independent of the waiting sampler option-validation plan.

**Approach and files.** Move `_read_source` to `tools/fidelity_sources.py::read_source`, retaining its signature, operation order and exceptions. Import it into `tools/fidelity.py` as `_read_source` in both package and direct-script branches so `main` and its existing pre-read validation spies keep their call boundary. Move `require_within_repo`, `ROOT` and `read_png` ownership into the new module; keep cropping, comparison, error reporting and exit decisions in `main`. Update the containment patches in `tests/test_fidelity_cli.py` and decoder spies in `tests/test_fidelity_cli_crops.py` to patch the owning module. Add `tests/test_fidelity_sources.py` for focused input-policy tests. These five files bound this structural task; use no dependency, injectable loader framework or new CLI option. Preserve the tooling contracts in `docs/invariants.md`; no guarantee changes are intended.

**Acceptance criteria.** Characterize the loader before moving it, then run the same cases against `read_source`: an uncropped read calls the decoder once with `alpha=True`; an in-bounds crop calls it once with `max_rows=y+height` and `alpha=True`; sideways overflow retries without `max_rows`, allowing the existing crop error to report full image dimensions; vertical overflow retains the existing bounded request and decoder clamping. Exercise combined overflow as well. A repository symlink resolving outside the root raises before any decoder call, while an inside-root symlink and an external input remain readable. Keep real-PNG CLI regressions for invalid palette data below the requested crop, alpha preservation and crop diagnostics; pin exact status, stdout and stderr for sideways overflow before and after extraction. Package invocation and a direct-script cropped comparison produce the same report and verdict. Existing threshold-validation tests still intercept `_read_source` before reads. Run `make check` after final edits.

## Done
