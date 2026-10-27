# Bugs

Known bugs, recorded by any loop and fixed by the bugfix loop.
Each bug: symptom, how to reproduce, suspected cause if known. Move fixed bugs to Fixed, with the
required `**Validation gap:** <tag> — <one sentence>` line recording what made the bug hard to
confirm (tag one of: none, no-repro, no-fake, real-run-needed, no-observability, slow-check,
unclear-invariant).

## Open

### CI's `make check` runs no rendered-pixel comparison: the whole `TestRender` class skips because the workflow installs none of the five Plasma render tools (found by the steward role 2026-10-27)

**Symptom.** `.github/workflows/ci.yml` runs exactly `make check` and
`make check-references` (pinned to that two-run list by
`tests/test_ci_workflow.py::TestCiWorkflow::test_workflow_runs_public_checks_with_materialized_assets`),
and its other steps are only checkout with LFS and setup-python: no step installs
`kwin_wayland`, `dbus-run-session`, `plasmawindowed`, `spectacle` or
`plasma-apply-colorscheme`, and `make check-references` only validates the reference
set. The suite's one live rendered-pixel check,
`tests/test_render_surface.py::TestRender`, is wrapped in
`@unittest.skipUnless(all(shutil.which(tool) for tool in REAL_TOOLS), ...)` over exactly
those five tools, so wherever any of the five is absent the entire class reports
skipped and the job still goes green. The standard `ubuntu-latest` runner image ships
none of the Plasma tools, so the render gate that byte-compares the title-bar strip,
the close, zoom and collapse boxes and the side and bottom border strips against
`aboutsystem_betawiki.png` (README, "Fidelity checking") never exercises in CI: a
regression in the rendered chrome merges with CI green and is caught only on a host
where the gate runs (this project's merge host has all five on PATH). The skip line
is visible in the verbose unittest log, so the gap is discoverable but not surfaced
by the job's status.

**Reproduce.** On any host with none of the five tools on PATH — or by reading the
two files, which is the CI situation:

```
PYTHONPATH=tests python3 -m unittest tests.test_render_surface.TestRender -v
```

prints `skipped 'needs kwin_wayland, dbus-run-session, plasmawindowed, spectacle and
plasma-apply-colorscheme on PATH'` instead of running the pixel tests; every step of
`.github/workflows/ci.yml` can be grepped for the five tool names with no hit.

**Suspected cause.** Not a code defect but a workflow-versus-gate drift: the class
skips deliberately so `make check` stays runnable without a Plasma session, but no
CI step compensates for the skip, so a green CI run is compatible with zero
rendered-pixel coverage. Remediation belongs to a plan (for example a CI job with
the KDE runtime running the render gate, or a CI guard that fails when
`TestRender` skipped, or a recorded carve-out in README's "Fidelity checking"), not
to a one-line fix.

## Fixed
