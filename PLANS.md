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
2026-10-29 by the steward role):** The
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

Two answers on 2026-10-19 widen the scope again, and both are being implemented in series.
**GTK applications and Firefox** are in scope (QUESTIONS.md, answered 2026-10-19) as a
four-part series: parts 1/4 (GTK 3 Platinum theme) and 2/4 (GTK 4/libadwaita stylesheet) have
landed, and part 3/4 has landed as three entries — the opt-in install (parts 1/3 and 2/3) and
the selection (part 3/3) — while part 4/4 is split into two runs: part 1/2 (the
Firefox `userChrome.css` stylesheet) has landed and part 2/2 (the profile install plus the
preference) has landed. **The UI font** is to be vendored
(QUESTIONS.md, answered 2026-10-19) as a three-part series: part 1/3 vendors Lato as the
Charcoal-style body face and has landed (installed and selected by the global theme); part 2/3
(a Chicago-style menu face, whose redistribution licence is still unresolved) is not planned
yet; and part 3/3 (selecting the installed family in KDE/Plasma/Qt) has landed for the Lato
body face only, because Lato is the only family the package installs. KDE, Plasma and Qt
applications now use Lato for the general, menu, toolbar, smallest-readable and window-title
fonts, and monospaced text keeps the user's fixed font; GTK and Firefox
applications keep their own chrome unless the opt-in GTK targets or the Firefox userChrome
install are used (the GTK entries have landed, and Firefox chrome is part 1/2, which has
landed, while its profile install is part 2/2, which has landed). Firefox work since that
series landed as single-surface chrome plans (the downloads-panel and all-tabs rows, the
sidebar frame, the menu-bar title box, the tab faces and the app-menu rows). The
`userContent.css` sheet now styles surfaces within six internal pages:
about:downloads, about:config, about:preferences, about:support, about:networking
and about:telemetry. These include preferences navigation and controls, support
tables and buttons, and telemetry navigation, tables and histograms; this is
surface coverage, not a claim of complete page theming. The opt-in profile install
copies this sheet alongside `userChrome.css`. This content work extends the
2026-10-19 "style Firefox" answer rather than the brief's KDE/Plasma desktop UI, so it is
recorded here to keep the scope deliberate.

### Rendered inactive-window gate, part 1/2: plumb a two-window capture that renders one unfocused client through the render CLI, workflow, session and Makefile (planned 2026-11-11 by the plan role; part 1 of a two-part series — part 2/2 will add the `TestInactiveDialogRender` pixel gate to `tests/test_render_surface.py`, byte-comparing the captured unfocused window's flat buttonless bar, `#777777` title ink and frame rows against the shipped inactive Aurorae art `tests/test_aurorae_frame.py` pins, and will be planned once this part lands, its heading naming this part as its landed prerequisite in the allocator's clause form, so this part lands mergeable on its own; independent of the waiting fidelity JPEG entry — that entry edits `tools/fidelity_sources.py`, `tests/test_fidelity_jpeg.py`, README's `## Fidelity checking` section and one appended `## tooling` row, while this entry edits the render plumbing (`tools/render_clients.py`, `tools/render_dialogs.py`, `tools/render_workflow.py`, `tools/render_surface.py` only through the shared table, `Makefile`), two render test modules and README's render sections plus its own appended `## tooling` row, so the two share no production function, no test module and no assertion and either merge order leaves all working — at implementation re-grep every anchor this entry names)

**Goal.** No render gate has ever rendered an unfocused window: every landed gate captures exactly one client, and KWin activates a session's only window, so the shipped inactive Aurorae art — the flat buttonless `#DDDDDD` bar whose centered title paints `org.macos8.desktoprc`'s `InactiveTextColor` `#777777` (`tests/test_aurorae_frame.py::TestDecorationSvg`'s static pins, the 2026-11-04 inactive-art direction) — has never been seen drawn by a running KWin. The landed kwin-decoration session proofs (docs/invariants.md `## kwin-decoration`) exercised only the active path. A two-window capture — the focused client beside an earlier one KWin leaves unfocused — closes that gap and gives part 2/2 its candidate. Grep of PLANS.md `## Planned`, PLANS-DONE.md, BUGS.md, BUGS-FIXED.md and the tree found no window-rule or two-window render coverage.

**Grounding (verified fresh 2026-11-11).** `tools/render_dialogs.py::DIALOG_MODES` declares one `DialogMode(attr, flag, help, client, client_tool)` per dialog surface; `tools/render_surface.py` builds one `--*-dialog` flag per entry from that table and refuses more than one, `tools/render_workflow.py::_client_command` maps the flag to the client factory and `_select_dialog_theme` writes the Kvantum selection (the GTK selection only for `zenity` modes), and `_dialog_config_files` adds `kdeglobals` for every dialog render. `tools/render_session.py::session_script` backgrounds one client argv (`"$@" & client=$!`), liveness-checks it after the settle and reaps it after the capture, and `session_command` wraps `dbus-run-session -- kwin_wayland --virtual --width/--height`; `tools/render_setup.py::write_session_configs` writes exactly the config files named by the `files` tuple from the look-and-feel `contents/defaults` via `tools/theme_defaults.py::defaults_groups`. The `Makefile` spells the mode list once in `RENDER_MODE_VALUES`, pinned against `DIALOG_MODES` by `tests/test_render_make.py`'s mode-table test.

**Approach.**

1. `tools/render_clients.py`: add `inactive_dialog_client(session)`, returning a `sh -c` wrapper command that backgrounds two `kdialog --title <TITLE> --msgbox <TEXT>` windows with two distinct fixed titles — the to-be-inactive window first, the focused one last, so KWin activates the newest and the earlier one draws the inactive frame — then `wait`s, so the wrapper is the single client PID the session script liveness-checks and reaps exactly as today. The factory's comment records that the wrapper's death leaves the two kdialogs to the private bus's teardown, the session lifecycle every client already relies on.
2. `tools/render_dialogs.py`: append the entry `DialogMode("inactive_dialog", "--inactive-dialog", <help in the landed help style naming the two kdialog windows and the 480x360 capture>, inactive_dialog_client, "kdialog")` at the table's end. The existing wiring (`render_surface`'s parser and one-flag refusal, `_client_command`, `_select_dialog_theme`) picks it up unchanged.
3. Geometry: a new small `tools/render_window_rules.py` writes a `kwinrulesrc` into the scratch config home holding exactly two rules matched on the exact titles and forcing both position and size — the inactive window at the capture's left, the focused one at its right, both fully inside the 480x360 dialog capture. Probe the installed KWin 6.3.6's rule parser (the rule grammar and the rule-value integer meaning "force") the way the kwin-decoration records verified engine behavior, record the probed keys in the rules writer's test comments and the invariants row, and pin both windows' forced sizes in the writer's tests; sizes are chosen from a first measured render, never assumed. `tools/render_workflow.py`: extend `DialogMode` with an optional trailing `extra_config_files: tuple[str, ...] = ()` field (empty for every landed mode) and have `render()` pass `files=_dialog_config_files() + mode.extra_config_files` for the selected mode, so only this mode's session writes `kwinrulesrc`.
4. `Makefile`: append `inactive-dialog` to `RENDER_MODE_VALUES` in `tools/render_surface.py`'s flag order, keeping `tests/test_render_make.py`'s DIALOG_MODES pin passing unchanged in shape.
5. Unit tests beside the landed dialog-mode unit tests in `tests/test_render_surface.py`: the parser accepts `--inactive-dialog` alone and refuses it beside any other `--*-dialog` flag with the landed "open one dialog client each" wording; `_client_command` maps the flag to the two-window wrapper; the mode's session configs include `kwinrulesrc` beside `kwinrc`, `plasmarc` and `kdeglobals`; the Kvantum selection is written and no GTK selection installs; a new `tests/test_render_window_rules.py` pins the written `kwinrulesrc` bytes (both exact titles, both forced geometries, nothing else in the file). Confirm `tests/test_ci_workflow.py` needs no new tool (`kdialog` is already required for the kdialog modes) and extend only a mode list it enumerates.

**Files.** `tools/render_clients.py`, `tools/render_dialogs.py`, `tools/render_workflow.py`, `tools/render_window_rules.py` (new), `Makefile`, `tests/test_render_surface.py`, `tests/test_render_window_rules.py` (new), `tests/test_render_make.py` (pin note only if its shape requires it), `README.md` (the render-mode enumeration plus one sentence naming the two kdialog windows and that the captured surface shows the unfocused one), `docs/invariants.md` (one appended `## tooling` row recording the rule-grammar probe and that no pixel is pinned until part 2/2).

**Acceptance criteria.**

- `make render RENDER_MODE=inactive-dialog` exits 0 and publishes a 480x360 PNG in which two KWin-decorated windows stand side by side, non-overlapping and fully inside the capture, the left one drawn inactive; the first measurement run on this host records the capture and the regions part 2/2 will compare in the new gate's comments, and the rules writer's pinned sizes are re-derived from that render, not assumed.
- The render CLI accepts `--inactive-dialog` alone at the 480x360 dialog defaults, refuses it beside any other dialog flag with the landed wording, and treats it as a dialog mode for `kdeglobals`, the Kvantum selection and the missing-`kdialog` refusal exactly as the landed kdialog modes are treated.
- The inactive mode's scratch session holds a `kwinrulesrc` with exactly the two forced-geometry rules; no other mode's session writes `kwinrulesrc`; `RENDER_MODE_VALUES`, the CLI parser, the help text and README's enumeration all name the new mode.
- Every landed `_DialogGate` class and the applet render render and compare unchanged (their unit tests and, where the GUI opt-in is granted, their gates), `tests/test_render_make.py`'s DIALOG_MODES pin passes in its landed shape, and `make check` passes after the final edit.

### Render CLI: refuse a missing applet package before the session starts (planned 2026-11-11 by the plan role; independent of the waiting fidelity JPEG entry and the waiting inactive-window part 1/2 entry — the JPEG entry edits `tools/fidelity_sources.py::read_source`, `tests/test_fidelity_jpeg.py`, README's `## Fidelity checking` section and one `## tooling` row, while part 1/2 edits `tools/render_clients.py`, `tools/render_dialogs.py`, `tools/render_workflow.py`, the `Makefile` and README's render-mode enumeration; this entry edits only `tools/render_surface.py`'s preflight in `main` and the `_applet` validator beside it, a new standalone module with no render plumbing import, its own test module and `tests/test_render_surface_units.py`, and README's prerequisites row plus one troubleshooting-table row — so the three entries share no file region, no test module and no assertion and any merge order leaves all working; at implementation re-grep every anchor this entry names)

**Goal.** The calculator render's client is `plasmawindowed <applet>` (`tools/render_workflow.py::_client_command`'s non-dialog branch), but the CLI's preflight (`tools/render_surface.py::main`) checks only command names through `tools/diagnostics.py::report_missing_tool`; an applet package is not a command, so a host without `org.kde.plasma.calculator` wastes a full scratch KWin session and reports only an indirect failure — README.md's prerequisites row and `### Rendering a candidate` paragraph both say "without it the window never paints and the capture times out instead of failing at a tool check". README's `### Troubleshooting a render` table then has to tell the reader a timeout does not diagnose the absence. A pre-flight existence check closes the wart the same way the landed missing-tool refusal closes the missing-command one: exit 2 before `Session.create()`, naming the applet id. Grep of PLANS.md `## Planned`, PLANS-DONE.md, BUGS.md and BUGS-FIXED.md found no entry carrying a missing-applet preflight (the archived render-triage plan explicitly left it as an unverified cause; the CI workflow's `has_calculator_applet` shell check provisions the runner image and stays untouched).

**Grounding (verified fresh 2026-11-11).** `plasmawindowed` opens a KPackage applet package from the XDG data directories' `plasma/plasmoids/<id>/` directory: on this host `/usr/share/plasma/plasmoids/org.kde.plasma.calculator/metadata.json` exists and `plasmawindowed --help` takes `applet` as its first positional. `tools/render_surface.py::main` runs `report_missing_tool(TOOL, requirements)` and then `output_problem`, all before `with exit_on_termination(): return render(args)` — the insertion point for the new refusal. `_applet` (same file) already refuses empty, option-like and NUL-carrying ids but accepts path separators (`"a/b"` parses), which a path-joining existence check must not accept. The dialog modes never open the applet (`main` computes `dialog_flags` before the preflight), so the check must be skipped when a dialog flag is set — a `--menu-dialog`-only host without the calculator applet must still render its dialogs.

**Approach.**

1. New `tools/render_applet.py`, no imports from the render plumbing: `applet_problem(applet_id, data_roots=None) -> str | None`. When `data_roots` is None, derive them as `XDG_DATA_HOME` (default `~/.local/share` when unset or empty) followed by the `XDG_DATA_DIRS` entries (default `/usr/local/share:/usr/share`), mirroring the XDG data locations KPackage searches. An id that is empty or contains `/`, `\` or NUL is itself a problem string. When every root misses `<root>/plasma/plasmoids/<id>/metadata.json` (a plain file, not a directory), return a problem string naming the applet id and the searched `plasma/plasmoids` locations; any root holding that file ends the search with None. The module docstring records the probed location rule and its 2026-11-11 host evidence.
2. `tools/render_surface.py`: extend `_applet` to also refuse path separators with the same diagnostic shape (a plasmoid id is a dotted KPlugin id; `"a/b"` must exit 2 at parse time). In `main`, directly after the `report_missing_tool` block, when `dialog_flags` is empty call `applet_problem(args.applet)` and on a problem `return report_error(TOOL, problem)` (exit 2, the same missing-external-dependency status the epilog already documents), before `output_problem` and the session.
3. `tests/test_render_applet.py` (new): the finder unit tests pass explicit `data_roots` lists — found via an `XDG_DATA_HOME`-style root, found via an `XDG_DATA_DIRS`-style root, directory without `metadata.json` still missing, first matching root wins, problem string names the id and both attempted shapes, path-separator and empty ids refused — plus one derivation test patching `XDG_DATA_HOME`/`XDG_DATA_DIRS` in `os.environ` (including the empty-string-falls-back-to-default cases).
4. `tests/test_render_surface_units.py`: beside the landed applet cases, pin that `"a/b"` as `--applet` exits 2 at parse time; and that `main(["out.png"])` with `XDG_DATA_HOME`/`XDG_DATA_DIRS` patched to empty scratch dirs exits 2 with a diagnostic naming `org.kde.plasma.calculator` and reaches no session (patch the render call seam to fail loudly on invocation), while the same patched environment with a scratch root holding `plasma/plasmoids/org.kde.plasma.calculator/metadata.json` passes the preflight and reaches the render seam; and that a `--menu-dialog` run under the empty patched environment refuses through the landed missing-client-tool path and never consults the applet check (assert the check seam was not called alongside the tool-report seam), all without starting a KWin session.
5. README.md: in the prerequisites row and the `### Rendering a candidate` paragraph, replace the "never paints and the capture times out" wart wording with the new behavior — a calculator capture needs the `org.kde.plasma.calculator` applet installed (Debian packages it in `plasma-widgets-addons`), and a render of a missing applet refuses with exit 2 before any session, naming the applet id and the searched locations. In the `### Troubleshooting a render` table, reword the timeout row's applet clause: the absence is now diagnosed by its own preflight refusal, so a bare timeout no longer lists it as an undiagnosed cause.
6. `docs/invariants.md` `## tooling` table: append one dated (2026-11-11) end-of-table row naming `tests/test_render_applet.py` and the new `tests/test_render_surface_units.py` cases, recording the probed KPackage applet location (XDG data dirs' `plasma/plasmoids/<id>/metadata.json`, verified against the installed `plasmawindowed` on 2026-11-11), that the refusal is a preflight diagnostic with no pixel pinned, and that dialog modes skip the check.

**Files.** `tools/render_applet.py` (new), `tools/render_surface.py`, `tests/test_render_applet.py` (new), `tests/test_render_surface_units.py`, `README.md`, `docs/invariants.md`.

**Acceptance criteria.**

- `python3 tools/render_surface.py out.png` on a host whose XDG data locations hold no `org.kde.plasma.calculator` package (reproducible with the patched-environment unit cases) exits 2 with a diagnostic naming `org.kde.plasma.calculator` and the searched `plasma/plasmoids` locations, creating no scratch session directory; with the package present (this host) the render proceeds unchanged and the landed calculator gates and their unit tests pass unchanged.
- `--applet a/b` (and `a\\b`, and an empty id) exits 2 at parse time with the landed applet-validator diagnostic shape; a dialog flag with a non-installed default applet still refuses only through the landed dialog preflight, never on the applet check.
- Every `plasma/plasmoids/<id>/metadata.json` root match ends the search and produces no diagnostic; a directory without `metadata.json` does not match; the searched-location list appears in the missing-applet diagnostic.
- README's prerequisites row, `### Rendering a candidate` paragraph and `### Troubleshooting a render` timeout row state the preflight refusal instead of the timeout wart; `docs/invariants.md`'s `## tooling` table ends with the new row; `make check` passes after the final edit.

## Done

### Fidelity CLI: extract parser construction from comparison orchestration (planned 2026-11-02 by the plan role) — done 2026-11-11 by the feature role

**Goal and grounding.** Make the fidelity entry point readable as a comparison workflow. `tools/fidelity.py::main` currently starts with parser construction and a nested `worst_pixel_limit` validator before it reads images. `tools/fidelity_arguments.py` already owns the other argument validators. The finished report-extraction plan deliberately retained parser setup in the entry point; heading searches found no separate parser-extraction plan. This maintenance task is independent of the queued sampler work.

**Approach and files.** Create `tools/fidelity_cli_parser.py::build_parser`, moving the existing `EscapingArgumentParser` construction and option declarations there without changing their order, help strings, defaults, destinations or types. Move `worst_pixel_limit` to `tools/fidelity_arguments.py` and import the validators into the new parser module. In `tools/fidelity.py::main`, replace the construction block with `build_parser().parse_args(argv)` and remove imports made unused by the move. Support package imports and direct-script execution using the existing conditional import pattern. Keep image reads, crop application, optional diagnostic scans and reporting in their current owners. Inspect repository references to validators imported through `tools.fidelity` before removing those imports; preserve an existing consumer's import path if needed. Bound the change to those three production files and a new `tests/test_fidelity_cli_parser.py`; adjust ownership docstrings in the touched files. No CLI behavior change or new dependency is intended.

**Acceptance criteria.** Before moving declarations, capture characterization fixtures in the new test module for normalized help text and parsed default/explicit namespaces, including both crops, diagnostic switches and combined budgets. The same fixtures pass after extraction. Use the existing unittest framework to verify two independently constructed parsers work, malformed crop/budget/worst-pixel arguments retain status 2 and escaped diagnostics, and help and invalid arguments do not call `tools/fidelity.py::_read_source`. Existing fidelity CLI, JSON, crop and direct-script tests continue to pass. Run `make check` after final edits. This structural change adds no guarantee to docs/invariants.md; its existing tooling contracts remain the acceptance boundary.

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::_MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
