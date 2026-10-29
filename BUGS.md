# Bugs

Known bugs, recorded by any loop and fixed by the bugfix loop.
Each bug: symptom, how to reproduce, suspected cause if known. Move fixed bugs to Fixed, with the
required `**Validation gap:** <tag> — <one sentence>` line recording what made the bug hard to
confirm (tag one of: none, no-repro, no-fake, real-run-needed, no-observability, slow-check,
unclear-invariant).

## Open

### The CI dependency setup requires passwordless sudo in the local runner (found by the ci role 2026-10-29)

**Symptom:** The workflow's Plasma render-tool installation step cannot run in a worktree environment without passwordless `sudo`, preventing a complete local replay even when the render tools are already installed.

**Reproduce:** Run the `Install the Plasma render tools` step from `.github/workflows/ci.yml` where `sudo` requires a password.

**Observed output:** `sudo: a terminal is required to read the password; either use the -S option to read from standard input or configure an askpass helper` followed by `sudo: a password is required`.

The required tools were already available on `PATH` in this run, and `make check` plus `make check-references` passed. The setup step's result remains unverified in this environment.

## Fixed
