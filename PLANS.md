# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; merged-plan facts re-trimmed 2026-10-23
by the clean role; validation scope clarified 2026-10-25 by the steward role; Firefox artifact
and content-surface status updated 2026-10-26 by the steward role; install-firefox
file list corrected 2026-10-27 by the steward role; shipped-SVG count updated
2026-10-27 by the feature role; Firefox content scope refreshed
2026-10-29 by the steward role; merged-series narration trimmed 2026-11-11 by the
steward role):** The
initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (thirty-one widget SVGs under
`widgets/`, including the `widgets/margins-highlight.svg` panel edit-mode margin highlight and the
`widgets/containment-controls.svg` panel resize and slider handles, plus
`dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
collapse boxes); the desktop wallpaper package; the `org.macos8.desktop` icon theme (our own
32x32 Platinum-style art for the desktop's hard-disk, folder, document,
Trash and full-Trash icons, plus the menu bar's kicker logo `start-here-kde-symbolic` and the
`go-next-symbolic` submenu arrow, our own marks rather than Apple's;
the 2026-10-29 user decision supersedes its final-art status and queues placeholder tracking
below); the `org.macos8.desktop` Kvantum widget
style (Platinum palette and core-control art); the
`org.macos8.desktop` Lato font package (Lato Regular and Bold, the Debian copyright file
carrying the upstream SIL OFL 1.1 body, and the provenance record; installed by `make install`,
and the global theme selects its `Lato` family for general, toolbar and smallest-readable fonts,
`ChicagoFLF` for menus and window titles, and the user-approved `JetBrains Mono Medium` for
KDE's fixed-width font (`[kdeglobals][General] fixed`, part 2/3 of the fixed-width series);
the GTK 3 and GTK 4
Platinum stylesheets under `theme/gtk/` (installed by the opt-in `install-gtk` target and
selected by `apply-gtk`; `make install` copies no GTK files); the standalone Firefox Platinum
sheets under `theme/firefox/` (its `userChrome.css` and `userContent.css` copied, and its
profile preference written, only by the opt-in `install-firefox` target); and the render and
fidelity tooling.
The live reference-comparison gate in `tests/test_render_surface.py` checks Aurorae window-chrome
regions when its render prerequisites are available (README.md, "Fidelity checking").
Firefox's `tests/test_firefox_theme_*.py` and `tests/test_firefox_content_*.py` modules
check stylesheet declarations and selector behavior;
those checks do not establish rendered Firefox pixels. Keep this distinction when assessing
progress toward pixel-perfect application chrome. README.md describes the reference set as the
source of truth for "menu bar, window chrome, widget metrics, icons and colour palette". The
prompt's surfaces and their status are each tracked here (updated 2026-10-21 by the
steward role): a **Qt widget style** for KDE applications (the desktop theme styles only
Plasma shell widgets, so a KDE app's own buttons, menus and scroll bars would keep the Breeze look) is served
by the global theme's selection of our Kvantum theme: the user answered
2026-10-18 that a pixel-matched Platinum style should ship as a Kvantum theme (a new
dependency) — shipped as the four-part "Mac OS 8.6 Kvantum widget style" series (each part
waited on the one before); a **cursor theme** was out of scope on 2026-10-17 because no reference
screenshot shows a cursor, so no pixel ground truth exists to match; on 2026-10-23 the plan role
queued it anyway as the theme's own Platinum-style pointer set (black-face, white-outline arrow,
text I-beam, pointing hand, busy hourglass, move cross, horizontal and vertical resize arrows,
NW-SE and NE-SW diagonal resize arrows, crosshair, circle-slash, drag-and-drop copy plus,
open and closed hands, the help question-mark arrow, the progress arrow with a small hourglass,
a pencil, the `zoom-in`/`zoom-out` magnifiers, and the drag-and-drop/forbidden aliases, not
traced from Apple's artwork), it
has merged inside the icon theme package with its provenance exception recorded in
`docs/invariants.md`, and `make apply-cursor`/`make remove-cursor` link it into the Xcursor path
and select it; Xcursor roles the theme does not name still come from the fallback cursor
theme; **system sounds** are out
of scope (not a visual surface, so the reference set cannot ground them); and a **lock screen** is
out of scope unless a broader login/lock-screen plan is taken up (QUESTIONS.md, answered
2026-10-21). The
shipped work should not be treated as the whole of the prompt.

Two answers on 2026-10-19 widened the scope, and both are recorded below in their merged
state (their merged-series entry narration trimmed 2026-11-11 by the steward role;
the entries themselves are archived in PLANS-DONE.md).
**GTK applications and Firefox** are in scope (QUESTIONS.md, answered 2026-10-19): the GTK 3
and GTK 4/libadwaita Platinum stylesheets under `theme/gtk/` are installed — and selected —
only by the opt-in `install-gtk` and `apply-gtk` targets (`make install` copies no GTK
files), and the opt-in `install-firefox` target copies the Firefox `userChrome.css` and
`userContent.css` sheets into a profile and writes the preference that selects them.
**The UI font** is vendored (QUESTIONS.md, answered 2026-10-19): Lato is installed as the
Charcoal-style body face and selected by the global theme for general, toolbar and
smallest-readable fonts, and ChicagoFLF, a
public-domain Chicago-style face, is selected for menus and window titles (its licence was checked 2026-11-12 by the director role);
JetBrains Mono (the user-approved fixed-width face, QUESTIONS.md answered 2026-11-12)
is selected for KDE's fixed-width font.
GTK and Firefox applications keep their own chrome unless the opt-in GTK targets or the
Firefox install are used. Firefox chrome work since that series merged as single-surface
chrome plans (the downloads-panel and all-tabs rows, the sidebar frame, the menu-bar title
box, the tab faces and the app-menu rows). The `userContent.css` sheet styles surfaces
within six internal pages — about:downloads, about:config, about:preferences,
about:support, about:networking and about:telemetry — including preferences navigation and
controls, support tables and buttons, and telemetry navigation, tables and histograms; this
is surface coverage, not a claim of complete page theming. This content work extends the
2026-10-19 "style Firefox" answer rather than the brief's KDE/Plasma desktop UI, so it is
recorded here to keep the scope deliberate.

**Size drift (2026-11-14, steward; re-measured 2026-11-18 by the steward role):** PRINCIPLES.md
asks each file to stay small enough to read in one sitting, and this plan set's working budget is
roughly 800 lines (the suite-split entries below). Measured with `wc -l` over text files in
`tests/`, `tools/` and `theme/` at this worktree's base, the largest remaining files include
`theme/gtk/.../gtk-3.0/gtk.css` (7111) and `gtk-4.0/gtk.css` (6523), Firefox
`userChrome.css` (1581) and `userContent.css` (941), and test modules
`test_render_file_dialog.py` (1464), `test_gtk_theme.py` (1274),
`test_render_surface.py` (1234), `test_gtk_theme_views.py` (1179),
`test_install_firefox.py` (1173), `test_gtk_css.py` (1170), `test_make_refusals.py`
(1063), `test_gtk_theme_osd.py` (1008), `test_render_failure_paths.py` (999),
`test_apply_theme.py` (970), `test_cursors_theme.py` (964), `test_theme_install.py` (940),
`test_render_surface_units.py` (940), `test_check_parallel.py` (931),
`test_render_dialog_gates.py` (887), `test_local_hook.py` (885),
`tests/support/gtk_rule_cases.py` (881) and `test_firefox_theme_library.py` (864).
`test_gtk4_theme.py` is now 108 lines after its extraction series landed. The render-test files
(`test_render_surface_units.py`, `test_render_dialog_gates.py`, `test_render_file_dialog.py`)
remain above the working budget and have no decomposition plan; the plan role should split them
per family before adding features. The GTK sheets and Firefox `userChrome.css` are single-file
theme artifacts, so splitting them needs a packaging choice (for example GTK `@import`) that is
not settled here. This note queues nothing and changes no behavior.

### Render-session readiness: a KWin settle script reports the mapped client over D-Bus and a session listener writes RENDER_SESSION_READY_FILE (planned 2026-11-16 by the bugfix role, rewritten 2026-11-17 by the plan role)

**Goal.** End the render settle on a real readiness signal instead of the fixed budget, per the
answered QUESTIONS.md entries "How should the ksplashqml client signal that its window is shown?"
(option 2, the KWin side) and "Option 2 needs a file writer KWin scripts do not have" (option 1: the
KWin script reports over D-Bus with `callDBus` to a listener the session shell starts, and the
listener touches the ready file; probe first, and fall back to that question's option 2 if the probe
fails). The session side already waits: `tools/render_session.py::session_script` exports
`RENDER_SESSION_READY_FILE` (`$capture.ready`), polls it, and keeps the settle as the ceiling. Nothing
writes the file yet, so every session waits its full settle. Sibling of the BUGS.md entry
"Render-session tests rely on fixed wall-clock budgets", which stays open until this lands.

**Step 1 — probe on this host, before any code.** In a nested `dbus-run-session -- kwin_wayland
--virtual` session (non-visible, as `session_command` builds it; never the user's desktop), start
`dbus-monitor --session "type='method_call',interface='<iface>',member='ClientReady'"` in the
background, load a one-line KWin script through `qdbus6 org.kde.KWin /Scripting
org.kde.kwin.Scripting.loadScript` + `run` that calls `callDBus("<service>", "/", "<iface>",
"ClientReady")` from a `workspace.windowAdded` handler, start a `kdialog --msgbox` client, and confirm
the monitor prints the call within the session's lifetime, bounded by a `timeout`. Pick `<iface>` /
`<service>` as theme-neutral names (e.g. `org.platinumtheme.RenderSession`); the probe also settles
whether `callDBus` to an unowned name still reaches a monitor (if not, the listener must own the name
— then record that and use the fallback). Record the probe's commands and outcome (KWin version,
date, what printed) in the new script function's docstring, as `focus_settle_text` records its own
probe. **If the probe fails**, do not build the listener: implement the fallback instead — the splash
render keeps its fixed settle (no ready-file wait for `--splash`), and record the failed probe in
QUESTIONS.md as a note on that answered question.

**Step 2 — build it (probe passed).**
- `tools/render_window_rules.py`: add `readiness_settle_text()` returning a KWin script that, for
  each window already in `workspace.windowList()` and each one `workspace.windowAdded` delivers, calls
  `callDBus` with the agreed service/path/interface/`ClientReady` once a window with
  `normalWindow`, `dialog`, `splash` or `desktopWindow` set is present (the dialog, splash and
  plasmashell-desktop renders respectively; panels and notifications do not count); and `write_readiness_settle_script(session)`
  mirroring `write_focus_settle_script`. Keep the names as module constants.
- `tools/render_session.py::session_script`: take a `readiness_script` path (all modes pass one from
  `tools/render_workflow.py`, next to the existing `focus_script`). Before the client starts, launch
  the listener — `dbus-monitor` filtered to the interface/member, piped to a `sh` loop that touches
  `$ready` on the first matching line — load the script with the same `qdbus6`/`qdbus` resolution and
  load-id check the focus block uses, and kill and reap the listener after the settle loop ends. A
  host without `dbus-monitor` or `qdbus` logs one `render-session:` line and keeps the ceiling wait.
- Update the session docstring and the "The client writes RENDER_SESSION_READY_FILE" comment to say
  the listener writes it.

**Files touched.** `tools/render_window_rules.py`, `tools/render_session.py`,
`tools/render_workflow.py`, `tests/test_render_surface_units.py` (or a new focused test module if
that one grows past a sitting), `docs/invariants.md` (a render-session row for the readiness signal).

**Acceptance criteria.**
- `readiness_settle_text()` contains a `callDBus` call naming the agreed service, interface and
  `ClientReady` member, and a `workspace.windowAdded` connection; a unit test pins both.
- A stubbed session (fake `dbus-monitor` that prints one matching line, fake `qdbus6` that returns a
  numeric id) logs `render-session: client ready at` and ends its settle well before a long settle
  ceiling; with a fake `dbus-monitor` that prints nothing, the log shows `settle ceiling reached
  before a client ready file`. Each path has a test, built on the existing stubbed-session harness in
  `TestSessionScript`.
- A session whose host has no `dbus-monitor` on `PATH` logs one `render-session:` line naming the
  missing tool and still captures after the ceiling.
- No listener process outlives the session script in the stubbed tests (the test checks the stub's
  pid is gone after the script exits).
- `make check` passes; the probe's outcome is recorded in the docstring (or, on the fallback path,
  in QUESTIONS.md, and `--splash` sessions no longer wait on a ready file — with its own test).

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
