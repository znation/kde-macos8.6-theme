# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; landed-plan facts re-trimmed 2026-10-23
by the clean role; validation scope clarified 2026-10-25 by the steward role; Firefox artifact
and content-surface status updated 2026-10-26 by the steward role; install-firefox
file list corrected 2026-10-27 by the steward role; shipped-SVG count updated
2026-10-27 by the feature role; Firefox content scope refreshed
2026-10-29 by the steward role; landed-series narration trimmed 2026-11-11 by the
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
and the global theme selects its `Lato` family for the general, menu, toolbar, smallest-readable
and window-title fonts, while monospaced text keeps the user's fixed font); the GTK 3 and GTK 4
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
has landed inside the icon theme package with its provenance exception recorded in
`docs/invariants.md`, and `make apply-cursor`/`make remove-cursor` link it into the Xcursor path
and select it; Xcursor roles the theme does not name still come from the fallback cursor
theme; **system sounds** are out
of scope (not a visual surface, so the reference set cannot ground them); and a **lock screen** is
out of scope unless a broader login/lock-screen plan is taken up (QUESTIONS.md, answered
2026-10-21). The
shipped work should not be treated as the whole of the prompt.

Two answers on 2026-10-19 widened the scope, and both are recorded below in their landed
state (their landed-series entry narration trimmed 2026-11-11 by the steward role;
the entries themselves are archived in PLANS-DONE.md).
**GTK applications and Firefox** are in scope (QUESTIONS.md, answered 2026-10-19): the GTK 3
and GTK 4/libadwaita Platinum stylesheets under `theme/gtk/` are installed — and selected —
only by the opt-in `install-gtk` and `apply-gtk` targets (`make install` copies no GTK
files), and the opt-in `install-firefox` target copies the Firefox `userChrome.css` and
`userContent.css` sheets into a profile and writes the preference that selects them.
**The UI font** is vendored (QUESTIONS.md, answered 2026-10-19): Lato is installed as the
Charcoal-style body face and selected by the global theme for the general, menu, toolbar,
smallest-readable and window-title fonts, and monospaced text keeps the user's fixed font;
a Chicago-style menu face (part 2/3 of the font series) remains unplanned because its
redistribution licence is unresolved, and Lato is the only family the package installs.
GTK and Firefox applications keep their own chrome unless the opt-in GTK targets or the
Firefox install are used. Firefox chrome work since that series landed as single-surface
chrome plans (the downloads-panel and all-tabs rows, the sidebar frame, the menu-bar title
box, the tab faces and the app-menu rows). The `userContent.css` sheet styles surfaces
within six internal pages — about:downloads, about:config, about:preferences,
about:support, about:networking and about:telemetry — including preferences navigation and
controls, support tables and buttons, and telemetry navigation, tables and histograms; this
is surface coverage, not a claim of complete page theming. This content work extends the
2026-10-19 "style Firefox" answer rather than the brief's KDE/Plasma desktop UI, so it is
recorded here to keep the scope deliberate.

### Splash render mode, part 1/2: plumb a `--splash` ksplashqml capture through the render CLI, workflow and Makefile (planned 2026-11-11 by the plan role; independent of both waiting render-gate entries — the file-dialog part 2/2 gate appends a `_DialogGate` subclass and its gate-count words in `tests/test_render_surface.py`'s dialog tail, `README.md`'s `--file-dialog` paragraph and `docs/invariants.md`'s skip-guard row, while the applet face gate extends `TestRender` beside its landed strips, adds one sentence to `README.md`'s fidelity-checking gates paragraph and appends its `## tooling` row at the table's end; this entry edits `tools/render_surface.py`'s parser blocks directly beside `--desktop` and its preflight branch, `tools/render_clients.py`'s new client, `tools/render_workflow.py`'s `_client_command` and `render()` mode branches, the `Makefile`'s `RENDER_MODE_VALUES`/case/help narration, `README.md`'s prerequisites row, capture-enumeration prose and one command-table row, `tests/test_render_surface_units.py` beside its desktop cases, `tests/test_render_make.py`'s mode pin, `tests/test_render_surface.py`'s `TestFailurePaths`, `tests/test_ci_workflow.py`'s render-tool loop and one appended `## tooling` row — so no test method, production function or README paragraph is shared, though this entry and the applet face gate both append a row at the `## tooling` table's end, so whichever merges later re-reads the table before appending; at implementation re-grep every anchor this entry names; the splash's pixel gate is a later part a later plan writes)

**Goal.** The global theme ships a startup splash — `theme/look-and-feel/org.macos8.desktop/contents/splash/Splash.qml` with its placeholder `macos-logo.svg`, authored on the 240x180 grid of `macos8.6-screenshots/boot2_betawiki.png` and pinned by `tests/test_splash_qml.py`, `tests/test_splash_logo.py` and `tests/test_splash_reference.py` — but the fidelity workflow cannot capture it: `tools/render_surface.py` renders the calculator applet, the fourteen dialogs and the desktop menu bar, and no QML-structure check establishes rendered splash pixels (a runtime-only break — a missing image reference, a `unit` computation that collapses, a LayerShellQt surface the compositor never maps — passes every landed splash test). This part plumbs a `--splash` render mode that starts the themed splash in the headless KWin session and publishes a 640x400 fullscreen capture; its pixel gate is the later part. The splash's own placeholder asset keeps its `PLACEHOLDER:` marker and `PLACEHOLDERS.md` row — a render is measurement evidence, not a shipped-artifact change.

**Grounding (verified fresh 2026-11-11 by the plan role).** `ksplashqml` is installed on this host (`/usr/bin/ksplashqml`, `--help`: `Usage: ksplashqml [options] theme`, options `--test` (test mode), `--window` (windowed), `--nofork` (don't fork), `--pid`, positional `theme` — "Path to the theme to test"); an offscreen `QT_QPA_PLATFORM=offscreen ksplashqml --test --nofork <look-and-feel package dir>` run exits 0 quickly, so the binary starts and returns, but offscreen cannot confirm paint. The session plumbing already supports a shell-only client: `tools/render_workflow.py::_client_command`'s `args.desktop` branch returns `["plasmashell"]`, `render()` writes `write_desktop_selection(session)` for it, and `tools/render_session.py::session_script` applies the color scheme, waits the settle, fails the session when the backgrounded client is dead at the settle (`"$1 exited before the capture"`), captures fullscreen with `spectacle -b -n -f -o` and reaps the client afterwards — so the splash client must stay alive at the settle, which is why `--nofork` (no forking parent exit) is required and why the probe below measures which argument shape survives. `make install` copies the look-and-feel package to `{XDG_DATA_HOME}/look-and-feel/org.macos8.desktop` (`INSTALL_FAMILIES` includes `look-and-feel`; the render session runs `make install` with `XDG_DATA_HOME={session.data}`, `tools/render_setup.py::install_theme`), so the client argument is a session-local path, deterministic and outside the caller's data home. The splash paints fullscreen on the nested compositor's layer shell, and the probe's virtual framebuffer is the 640x400 the desktop capture already fixes (`_DESKTOP_CAPTURE = (640, 400)`, `tools/render_surface.py`), so the splash capture is the same fixed size. `Splash.qml`'s field colour is the literal `"#63639C"` (`root.fieldColor`), so a painted capture is recognizably non-black and the probe can demand it.

**Approach.**

1. First probe the client on this host, inside a nested session shaped like the render CLI's own (`dbus-run-session` with a scratch `XDG_DATA_HOME` holding a `make install`-ed tree, `WAYLAND_DISPLAY`/`QT_QPA_PLATFORM=wayland`, KWin running, capture with `spectacle -b -n -f` after a settle): try `ksplashqml --nofork <scratch-data>/look-and-feel/org.macos8.desktop` (the primary shape), then, only if it exits before the settle or paints nothing, `--test --nofork` and `--window --nofork` with the same path. Require the chosen shape to (a) still be running at an 8 s settle and (b) produce a capture containing the `#63639C` splash field in a measurable region; record the chosen shape, the measured first-paint settle and the argument form that worked (the package directory path, versus a package id resolved through the data dirs) in the test comments added below. If no shape paints the splash in a bare nested session, stop — record the finding as a plan-defect note on this entry for the plan role instead of plumbing a mode that cannot paint. If the first paint misses the 8 s default, raise the splash settle default to the measured minimum plus margin (the `--desktop` precedent: `_DESKTOP_SETTLE = 30.0`) and record the re-derivation beside the constant.
2. `tools/render_surface.py`: add `_SPLASH_CAPTURE = (640, 400)` beside `_DESKTOP_CAPTURE`, and a `--splash` `store_true` argument directly after the `--desktop` one with help text naming the themed startup-splash capture and the fixed 640x400 size. Extend the validation with the desktop-shaped checks: `--splash` refuses every `--*-dialog` flag and `--desktop` with the landed one-conflict wording shape (`--splash renders the look-and-feel's own splash: do not combine it with <flag>`), refuses a non-default `--applet` and refuses `--width`/`--height` (`--splash captures at 640x400, the probe framebuffer size the later splash gate crops: do not combine it with --width/--height`); a splash run fixes `args.width, args.height = _SPLASH_CAPTURE`. Defaults: the applet's 8 s settle and 90 s timeout (`args.settle`/`args.timeout`'s mode ternaries gain the splash arm) unless step 1's probe raised the settle; the `--timeout must be longer than --settle` guard runs unchanged. Preflight: when `args.splash`, `requirements = REQUIRED_TOOLS + ("ksplashqml",)` so the missing-tool diagnostic names `ksplashqml`; no applet-package preflight (the splash opens no applet).
3. `tools/render_clients.py`: add `splash_client(session: Session) -> tuple[str, ...]` returning `("ksplashqml", "--nofork", str(session.data / "look-and-feel" / "org.macos8.desktop"))` (the shape step 1 chose; adjust the arguments there and record the choice) with a docstring naming what the gate renders — the look-and-feel package's own `Splash.qml` painted from the session's installed tree, never the caller's data home. Keep the id alongside `tools/render_setup.py`'s package ids the way the file's existing style does (import or comment, decided when writing).
4. `tools/render_workflow.py`: `_client_command` gains the splash branch beside the desktop one (`if args.splash: return list(splash_client(session))`, checked before the applet fallback); `render()` gains `splash = args.splash` beside `desktop = args.desktop` — session configs stay `CONFIG_FILES` for a splash run (the splash reads no selection), no Kvantum or GTK selection, no desktop selection, and no window-rules write.
5. `Makefile`: append `splash` to `RENDER_MODE_VALUES` and a `splash) set -- --splash ;;` arm to the case beside `desktop`; the `RENDER_MODE=name` help line's list derives from `RENDER_MODE_LIST`, so it moves unchanged.
6. Tests: `tests/test_render_make.py`'s `RENDER_MODE_VALUES` pin set and the flag-pairing table gain the splash entry. `tests/test_render_surface_units.py` gains cases beside the landed desktop ones: `--splash` delegates at the fixed 640x400 capture, refuses each conflicting option (`--desktop`, one dialog flag each, a non-default `--applet`, `--width`/`--height`) with the landed diagnostics' shape, carries the settle/timeout defaults overridable by explicit flags, names `ksplashqml` in the missing-tool diagnostic, and `--help` names the mode. `tests/test_render_surface.py`'s `TestFailurePaths` gains, modeled on the landed desktop ones: the splash render launches the `ksplashqml` client with the scratch-data package path, writes only the `CONFIG_FILES` session configs, runs no applet preflight and installs no Kvantum or GTK selection; the landed unpainted-capture and size-mismatch refusals cover the splash unchanged. `tests/test_ci_workflow.py`'s by-name tool loop gains `ksplashqml`, with its comment's tool count moved (seven→eight tools; the "five Plasma tools" wording moves likewise) — the CI image installs `plasma-workspace`, so no workflow install line changes; verify that reading the workflow before editing.
7. `README.md`: the prerequisites' "Render headlessly" row gains the splash clause (the splash render also needs `ksplashqml`); the `### Capturing a candidate` enumeration sentence gains "or the startup splash" after "or the desktop menu bar", the fixed-size/tool sentence gains the splash clause (`the splash capture is fixed at 640x400 and requires ksplashqml`), and the command table gains one row (`python3 tools/render_surface.py --splash splash.png`, 640x400). No `--file-dialog`/`--desktop` paragraph and no fidelity-checking paragraph edit.
8. `docs/invariants.md`: append one `## tooling` row recording the new mode: the client shape and argument the probe chose, the measured first-paint settle, the fixed 640x400 fullscreen capture basis (the probe framebuffer, the desktop capture's own basis), that the splash reads no selection (the client argument is the session-local installed package path), and that this plumbing pins no pixel (the splash gate is a later part).

**Files.** `tools/render_surface.py`, `tools/render_clients.py`, `tools/render_workflow.py`, `Makefile`, `README.md`, `docs/invariants.md`, `tests/test_render_surface_units.py`, `tests/test_render_surface.py`, `tests/test_render_make.py`, `tests/test_ci_workflow.py`. `tools/render_session.py`, `tools/render_setup.py` and `tools/render_dialogs.py` stay untouched: the session script, the install and the dialog table need no change for a shell-only client.

**Acceptance criteria.**

- On this host `python3 tools/render_surface.py --splash <scratch>/splash.png` exits 0 and publishes a 640x400 PNG of the themed startup splash (the probe's shape and settle), and the fresh probe's findings (client shape, argument form, first-paint settle) are recorded in the new tests' comments and the appended `## tooling` row.
- `--splash` refuses each conflicting option with the landed wording shape, keeps the `--timeout must be longer than --settle` guard, and a host missing `ksplashqml` refuses with exit 2 naming `ksplashqml` before any session; the unit and failure-path tests pin each behavior, and the landed desktop and dialog tests read back unchanged.
- `tests/test_render_make.py`'s pin covers the splash entry, `make render RENDER_MODE=splash RENDER_OUTPUT=<scratch>/splash.png` renders it, and `make check` passes after the final edit.

## Done

### Fidelity CLI: extract parser construction from comparison orchestration (planned 2026-11-02 by the plan role) — done 2026-11-11 by the feature role

**Goal and grounding.** Make the fidelity entry point readable as a comparison workflow. `tools/fidelity.py::main` currently starts with parser construction and a nested `worst_pixel_limit` validator before it reads images. `tools/fidelity_arguments.py` already owns the other argument validators. The finished report-extraction plan deliberately retained parser setup in the entry point; heading searches found no separate parser-extraction plan. This maintenance task is independent of the queued sampler work.

**Approach and files.** Create `tools/fidelity_cli_parser.py::build_parser`, moving the existing `EscapingArgumentParser` construction and option declarations there without changing their order, help strings, defaults, destinations or types. Move `worst_pixel_limit` to `tools/fidelity_arguments.py` and import the validators into the new parser module. In `tools/fidelity.py::main`, replace the construction block with `build_parser().parse_args(argv)` and remove imports made unused by the move. Support package imports and direct-script execution using the existing conditional import pattern. Keep image reads, crop application, optional diagnostic scans and reporting in their current owners. Inspect repository references to validators imported through `tools.fidelity` before removing those imports; preserve an existing consumer's import path if needed. Bound the change to those three production files and a new `tests/test_fidelity_cli_parser.py`; adjust ownership docstrings in the touched files. No CLI behavior change or new dependency is intended.

**Acceptance criteria.** Before moving declarations, capture characterization fixtures in the new test module for normalized help text and parsed default/explicit namespaces, including both crops, diagnostic switches and combined budgets. The same fixtures pass after extraction. Use the existing unittest framework to verify two independently constructed parsers work, malformed crop/budget/worst-pixel arguments retain status 2 and escaped diagnostics, and help and invalid arguments do not call `tools/fidelity.py::_read_source`. Existing fidelity CLI, JSON, crop and direct-script tests continue to pass. Run `make check` after final edits. This structural change adds no guarantee to docs/invariants.md; its existing tooling contracts remain the acceptance boundary.

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
