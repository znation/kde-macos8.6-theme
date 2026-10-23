# Bugs

Known bugs, recorded by any loop and fixed by the bugfix loop.
Each bug: symptom, how to reproduce, suspected cause if known. Move fixed bugs to Fixed, with the
required `**Validation gap:** <tag> — <one sentence>` line recording what made the bug hard to
confirm (tag one of: none, no-repro, no-fake, real-run-needed, no-observability, slow-check,
unclear-invariant).

## Open

### An exported empty `FIREFOX_PROFILE` makes the Firefox targets fail instead of discovering the profile (found by the qa role 2026-10-23)

`make install-firefox` and `make remove-firefox` with an empty `FIREFOX_PROFILE` exit 2
with `install_firefox: error: Firefox profile must be an absolute path: .` instead of
using the active profile under `$HOME/.mozilla/firefox`, which the same targets use when
the variable is unset.

**Reproduce:** in a scratch directory, create `home/.mozilla/firefox/zz.default` and an
`installs.ini` naming it, then run `HOME=$PWD/home FIREFOX_PROFILE= make install-firefox`
(an empty value given as a make argument, `make install-firefox FIREFOX_PROFILE=`, does
the same). It exits 2 without touching the profile. In the same tree,
`HOME=$PWD/home env -u FIREFOX_PROFILE make install-firefox` installs the sheet and
`user.js` block into `zz.default`; `FIREFOX_PROFILE= make remove-firefox` fails the
same way.

**Expected:** the Makefile's `$(if $(FIREFOX_PROFILE),--profile ...)` already treats an
empty value as "no profile named" and omits `--profile`, so the tool should fall back to
`installs.ini`/`profiles.ini`; `make help` lists the active profile under
`$HOME/.mozilla/firefox` as the default.

**Actual:** `tools/firefox_profile.py::resolve_profile` reads
`env.get("FIREFOX_PROFILE")` and treats `""` as a named path. `Path("")` is `.`, which is
relative, so it raises `ConfigError("Firefox profile must be an absolute path: .")`.
GNU make exports an empty command-line variable to the recipe, so both spellings above
reach the tool with the empty value set.

## Fixed
