# Bugs

Known bugs, recorded by any role and fixed by the bugfix role.
Each bug: symptom, how to reproduce, suspected cause if known. Move fixed bugs to Fixed, with the
required `**Validation gap:** <tag> — <one sentence>` line recording what made the bug hard to
confirm (tag one of: none, no-repro, no-fake, real-run-needed, no-observability, slow-check,
unclear-invariant).

Bugs no role can fix under the project's rules are refused with a dated
`**Refused <date> by <role>: <one-line reason>**` note under the entry's heading; they stay in
`## Open` only while the user has not accepted the refusal. Once accepted, move the entry to
`## Won't fix` — positioned after `## Open` so triage reads only fixable entries first — with a
dated `**Won't fix <date> by the <role> role — user accepted the refusal**` line that records the
limitation the theme now carries and what a fix would have required. A refusal whose reason is
"the fix is a redesign, not a repair" does not end there by default: route the redesign to a
PLANS.md plan and let the user decide whether to fund it before moving the bug. (Directed by the
user 2026-11-01; recorded by the director role.)

## Open

_None yet._

## Won't fix

### A killed GTK selection commit can leave settings files at different transaction versions (found by the robustness role 2026-11-01)

**Won't fix 2026-11-02 by the director role — user accepted the refusal**

Covered by the project-wide SIGKILL decision in PRINCIPLES.md (directed by the user
2026-11-02). Partial publication and leftover backups after SIGKILL are accepted limitations;
roles should use that standing decision when triaging equivalent reports.

`tools/gtk_staging.py::commit` publishes the GTK 3 settings, GTK 4 settings and GTK 4 user CSS
with separate replacements. Its rollback runs only when Python catches an exception; if the
process receives `SIGKILL` after one replacement, later files retain their old contents while
the first file contains the new selection, and its hidden hard-link backup remains. The GTK
selection is then partly applied despite the caller never completing.

Reproduce by staging different contents for two existing settings files, running `commit`, and
delivering `SIGKILL` after the first `os.replace` returns but before the second begins. The first
target contains new bytes, the second retains old bytes, and a `.backup` sibling remains. Recovery
would require a durable transaction record or another crash-consistent publication design;
in-process exception rollback cannot run after `SIGKILL`, and automatic recovery could overwrite
user edits made after the interrupted commit.

## Fixed

### the render tests' KWin session cannot allocate its capture buffers under the workflow's llvmpipe env (found by the ci role 2026-11-09) — fixed 2026-11-09 by the feature role

`make check` at main's tip `3a380abe20b939b96004b32fd07ddc3e5d9bf49f` fails `tests/test_render_surface.py` with 32 errors and 5 failures: every KWin virtual render session (`tools/render_session.py`: plain `kwin_wayland --virtual`) fails with `KMS: DRM_IOCTL_MODE_CREATE_DUMB failed: Permission denied`, so the session produces no capture and the tests that read the rendered PNG get `cannot read ... dialog.png: [Errno 2] No such file or directory`.

Reproduce with the workflow job env on this host:

    QT_QPA_PLATFORM=offscreen LIBGL_ALWAYS_SOFTWARE=1 MESA_LOADER_DRIVER_OVERRIDE=llvmpipe \
      make check CHECK_TESTS=test_render_surface

Suspected cause: commit `a005ece42` added `MESA_LOADER_DRIVER_OVERRIDE: llvmpipe` (and `LIBGL_ALWAYS_SOFTWARE: '1'`) to `.github/workflows/ci.yml`'s job env for the GPU-less hosted runner. On this host (kernel `6.12.115+deb13.1-amd64`, a real GPU is present): with `LIBGL_ALWAYS_SOFTWARE=1` alone the virtual session is clean, but adding `MESA_LOADER_DRIVER_OVERRIDE=llvmpipe` drives Mesa's KMS/GBM dumb-buffer path, and the kernel refuses dumb-buffer creation on the render node while permitting it on the primary node — verified with a direct `drmModeCreateDumb`-equivalent ioctl probe: `/dev/dri/card0` succeeds, `/dev/dri/renderD128` returns `Permission denied`. KWin then logs `kmsro: driver missing`, `Failed to open drm node: ""`, and the dumb-buffer denial, and spectacle's `CaptureScreen` on `Virtual-0` gets no reply.

A local-only fix inside project code (unsetting the override in the session or the check target) would silence the env for the runner-run `make check` too, defeating the env the runner still needs and whose runner-side value was never observed: the hosted run at `18ded7fe` failed at the install step before tests, so the forced-llvmpipe KWin path has never executed on the runner. The workflow files are out of the ci role's scope by this team's charter, so this filing routes to the bugfix or plan role: either drop the override from the workflow's env or read why it is needed on the runner and give the session an env it can steer there only.

Worked output from the reproduce run:

    AssertionError: 0 != 1 : render_surface: error: capture is not a readable PNG: cannot read /tmp/tumwater-run-Q0oLZO/render-surface-d99iuox1/surface.png: [Errno 2] No such file or directory: '/tmp/tumwater-run-Q0oLZO/render-surface-d99iuox1/surface.png'
      An error occurred while taking a screenshot.
      KWin screenshot request failed:
      Did not receive a reply. Possible causes include: the remote application did not send a reply, the message bus security policy blocked the reply, the reply timeout expired, or the network connection was broken.
      Potentially relevant information:
      - Method: CaptureScreen
      - Method specific arguments: "Virtual-0"
      
      render-session: capture status 0
      KMS: DRM_IOCTL_MODE_CREATE_DUMB failed: Permission denied
      render-session: client reaped

Fix: the settled change removes the `MESA_LOADER_DRIVER_OVERRIDE: llvmpipe` line from `.github/workflows/ci.yml`'s check job env and keeps only `LIBGL_ALWAYS_SOFTWARE: '1'`, which alone forces a software EGL driver for the nested KWin virtual session; the reproduce contrast above was re-run with the override stripped (`QT_QPA_PLATFORM=offscreen LIBGL_ALWAYS_SOFTWARE=1 make check CHECK_TESTS=test_render_surface`) and the module completes with no KMS dumb-buffer error, the capture gates skipping with the software-renderer reason. The absence is pinned by `tests/test_ci_workflow.py::TestCiWorkflow::test_workflow_runs_the_suite_on_the_headless_qt_platform`'s new `assertNotRegex` assertions on both `MESA_LOADER_DRIVER_OVERRIDE:` and `GALLIUM_DRIVER:` assignments, and `docs/invariants.md`'s two `## tooling` rows reword the forced-llvmpipe wording and record the local contrast's provenance. The fix is filed as the plan entry "CI workflow: drop the forced llvmpipe driver override the KWin render sessions cannot survive on a GPU host", done 2026-11-09 by the feature role (archived under PLANS-DONE.md).

**Validation gap:** real-run-needed — the local reproduce contrast is settled, but the hosted runner's virtual session under the remaining env (`LIBGL_ALWAYS_SOFTWARE=1` alone) was never observed (the hosted run `18ded7fe` failed at the install step before any test); it stays unobserved until the next hosted run that reaches the suite, as recorded in the workflow comment and the invariants row's provenance cell. (Originally tagged the bespoke `runner-side`, a tag in no ledger; re-tagged to the closest header tag — no offline path observed the hosted session — in the change that pinned the archive's tag vocabulary.)
