# Bugs

Known bugs, recorded by any loop and fixed by the bugfix loop.
Each bug: symptom, how to reproduce, suspected cause if known. Move fixed bugs to Fixed, with the
required `**Validation gap:** <tag> — <one sentence>` line recording what made the bug hard to
confirm (tag one of: none, no-repro, no-fake, real-run-needed, no-observability, slow-check,
unclear-invariant).

## Open

### CI parity cannot run because the specified workflow is absent (found by the ci role 2026-10-25)

At main tip `e3a2d88817bdaeb89f595d114d0d18f8fa268a82`, the CI role cannot
read `.github/workflows/ci.yml` to execute its jobs' `run:` steps. Reproduce
from the repository with `wc -l .github/workflows/ci.yml`; the output is:

```text
wc: .github/workflows/ci.yml: No such file or directory
```

`git ls-tree -r --name-only HEAD .github package.json package-lock.json`
prints no paths. The README instead documents `make check` for this
Python/Make project. No CI parity block was supplied with this run either.
The ci role is prohibited from editing `.github/workflows/*`, so it cannot
supply the missing workflow. Restore or identify the intended workflow and
align the role's instructions with it before claiming workflow parity.

**Validation gap:** none — The missing workflow is directly reproducible with the commands above.

## Fixed
