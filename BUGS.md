# Bugs

Known bugs, recorded by any loop and fixed by the bugfix loop.
Each bug: symptom, how to reproduce, suspected cause if known. Move fixed bugs to Fixed, with the
required `**Validation gap:** <tag> — <one sentence>` line recording what made the bug hard to
confirm (tag one of: none, no-repro, no-fake, real-run-needed, no-observability, slow-check,
unclear-invariant).

## Open

### CI parity cannot run its Python matrix in the local worktree (found by the ci role 2026-10-29)

The CI workflow runs `make check` and `make check-references` with Python 3.10 and 3.12. This
worktree has only Python 3.13.5 available (`ls /usr/bin/python3.*` showed
`/usr/bin/python3.13`), and no `uv`, `pyenv`, Docker, Podman, Nix, Conda, mise or asdf command
was available to provision the workflow interpreters. Consequently local parity could run only
on Python 3.13.5; the matrix job remains unverified here. Reproduce by running the workflow's
two `make` steps with its matrix versions in this environment; interpreter discovery fails
before either command can run under those versions. The available interpreter's checks passed.

**Observed output:** `ls /usr/bin/python3.*` → `/usr/bin/python3.13`; `command -v python3.10`
and `command -v python3.12` produced no paths.

**Progress:** Confirmed this is an interpreter availability gap in the local environment: CI
provisions both matrix versions with `actions/setup-python`, while this worktree has only
Python 3.13.5. The repository's workflow already runs both public checks under the matrix.

**Needs review 2026-10-29 by bugfix: `make` will report that Python 3.10 or newer is required if the requested matrix interpreter cannot be launched; otherwise these checks run under that interpreter.**

## Fixed
