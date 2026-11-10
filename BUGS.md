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

### The render harness's nested sessions crash-loop xdg-desktop-portal-kde with SIGABRT while the nested Wayland socket is not serving (found by the director role 2026-11-10)

**Symptom.** On this host (Plasma Wayland login of uid 1000), `coredumpctl -q list --since "2 hours ago"` showed ~640 SIGABRT (Signal 6) coredumps of `/usr/lib/x86_64-linux-gnu/libexec/xdg-desktop-portal-kde` in the window ending 2026-11-10 02:58:14 PST — still firing at 02:58:14 as the user reported, quiet by 03:03. Bursts run roughly one to three dumps per second, and `drkonqi-coredump-launcher` chases every dump in the journal (extra churn; its pid metadata lookups also fail, flooding the log). Every dump's stack is identical: `QGuiApplicationPrivate::createEventDispatcher` → `QMessageLogger::fatal` → `abort` in `QApplicationPrivate::init` at the portal's `_main`, the classic qFatal when the platform plugin cannot connect to a display. Crucially the sampled dumps sit in a `tmux-spawn-…` cgroup scope of `user@1000.service` — descendants of a tmux pane running a role run — not the login portal (that one, a ~4.9-day-old process on the host bus, is stable). The journal carries tens of thousands of portal-kde lines per busy day since October 17, matching the cadence of role render runs, and tens of thousands of coredump payloads this boot.

**Reproduce.** On this host, with the coredump journal readable (`journalctl --user` works for uid 1000), run one dialog render gate (`python3 tools/render_surface.py --color-dialog <out>.png`, documented prerequisites present) and count fresh xdg-desktop-portal-kde SIGABRT entries in `coredumpctl` during the run. The suspected window is the span where `dbus-run-session`'s private bus is up but the nested `kwin_wayland` socket `render-surface` (tools/render_session.py's `SOCKET`) is not yet listening — or has died — while something on that bus (KWin's startup settings-portal call, or a later activation retry) asks for the portal: each activation starts the portal inside the caller's process tree, Qt tries Wayland, QGuiApplication aborts, and D-Bus re-activates, dumping a core per attempt until the socket serves or the run's supervision ends the loop.

**Suspected cause.** The nested session's environment (tools/render_session.py::Session, which drops the host's `DISPLAY`/`WAYLAND_DISPLAY` and exports `WAYLAND_DISPLAY=SOCKET`) is applied at the `dbus-run-session` level and is passed whole to its private bus daemon (tools/render_workflow.py::render calls `process_group.run_logged(command.argv, session.environment, …)`), so every D-Bus-activated service — including xdg-desktop-portal-kde — inherits `WAYLAND_DISPLAY=render-surface` and no `QT_QPA_PLATFORM`. The session script's own `export QT_QPA_PLATFORM=wayland` pins only the client inside the `sh` body, not the activated portal. When the nested KWin socket is not yet listening (before `bind`) or gone (after KWin exits while the bus still lives), the portal's QGuiApplication cannot connect and aborts; nothing pins the portal to a display-free platform, and the re-activation loop turns every attempt into a SIGABRT coredump. Because the crashes are D-Bus-activated descendants of `dbus-run-session`, the end-of-run group kill in tools/process_group.py::run_logged already bounds them per run — the load may be zooming only through repeated runs — but if any private bus outlives its socket without supervision, those kills can never break the loop.

**Fix direction for the bugfix role.** Candidate: in tools/render_session.py::Session's `environment`, set `QT_QPA_PLATFORM=offscreen` for the whole nested bus subtree (the session script still overrides it to `wayland` for the client), so the activated portal never attempts Wayland and serves KWin's settings query from a display-free context; verify empirically that a render run afterwards produces no new xdg-desktop-portal-kde SIGABRT entries in `coredumpctl`, and pin the environment change in the render-surface suite's existing session-environment tests. Do not add any pkill-style name/pattern cleanup (project rule); any teardown must reach only process trees this harness started.


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
