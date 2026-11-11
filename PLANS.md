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

_None yet._

### GTK 3 child-probe harness: move the shared child-interpreter program heads and runner into tests/support/gtk_child_probe.py (planned 2026-11-11 by the plan role; independent of every other entry — it touches only `tests/test_gtk_theme_controls.py`'s harness block, the three `_GTK3_*` program-string constants and the `_run_gtk_child` method, and adds `tests/support/gtk_child_probe.py` plus one contract test, sharing no sheet rule, widget, probe assertion or invariants row with the waiting RTL spin-field entry or the in-flight vertical-spin-button branch, whose probes keep working unchanged whichever lands first because the imported names and the `_run_gtk_child` call surface stay; at implementation re-grep every anchor this entry names, since the two spin entries also extend this test file)

**Goal.** `tests/test_gtk_theme_controls.py` (2,503 lines) carries, besides its probes and shipped-glyph tests, the GTK 3 child-probe harness: the three program-string constants `_GTK3_CHILD_HEAD`, `_GTK3_SHEET_AND_WINDOW` and `_GTK3_PIXEL_HEAD` and the `TestGtkThemeControls._run_gtk_child` runner that seven probes call through. The project's one-responsibility principle puts shared helpers in `tests/support` beside `snippet_child.py`, `gtk_css.py` and the rest; the waiting RTL spin-field entry and the in-flight vertical-spin-button branch each add more probes to this same file, and every landed GTK 3 probe plan (progress-bar fill, notebook faces, seam and frame probes) already describes its probe as built from these in-file pieces. Moving the harness gives the growing probe family a stable import surface and trims the test file without touching a single probe.

**Approach.**

1. New `tests/support/gtk_child_probe.py`: the module docstring carries the harness comment above the constants (the child interpreter's gi imports with their exit-77 skip guards, the sheet provider the `Gtk.OffscreenWindow` paints with, the pixel reader the assertions sample through, and why the GTK work runs in a child — an in-process `import gi` leaves GLib's C worker threads in the suite process, which `tests/test_no_gtk_introspection.py` pins) and the `_run_gtk_child` docstring's rationale. The three constants move byte-for-byte. Add `def run_gtk_child(test, program, *paths)` with the moved method body: `subprocess.run([sys.executable, "-c", program, *paths], capture_output=True, text=True, timeout=120)`, `returncode == 77` calls `test.skipTest(result.stdout.strip() or "GTK 3 is not available")`, otherwise `test.assertEqual(result.returncode, 0, result.stdout + result.stderr)`. The module imports only `subprocess` and `sys`; `gi` appears only inside string constants, which the AST scanner never sees as imports.

2. `tests/test_gtk_theme_controls.py`: delete the constants block and the `_run_gtk_child` body. Import the three constants from `support.gtk_child_probe` and shrink the method to a one-line delegate — `return run_gtk_child(self, program, *paths)` — keeping its name, signature and a short docstring pointing at the support module. Every one of the seven call sites, every probe program and every prose mention of `_run_gtk_child` stays untouched.

3. New `tests/test_gtk_child_probe_support.py` (no GTK in the suite process, no introspection needed):
   - Pin `_GTK3_CHILD_HEAD`'s contract strings as substrings: `gi.require_version("Gtk", "3.0")` and `gi.require_version("Gdk", "3.0")`, the two skip reasons "GTK 3 introspection is not installed" and "no display for GTK 3" (the parent judges the child's printed reason, so the wording is the contract), and both `sys.exit(77)` guards.
   - Pin `_GTK3_PIXEL_HEAD`'s pixel reader: it defines `def at(x, y)` over the offscreen pixbuf's pixels, stride and channel count.
   - Pin `run_gtk_child` against a recorder object (methods `skipTest(reason)` and `assertEqual(a, b, msg=None)` that record instead of skipping): a child printing a reason and exiting 77 records a skip with that reason; a child exiting 1 with output records the failure assertion with the child's output attached; a child printing "ok" and exiting 0 records neither. This fails on the plausible swapped-branch bug — treating 77 as a failure or 0 as a skip.

No sheet, artwork or invariants change: the no-gi invariant row in `docs/invariants.md` pins `tests/test_no_gtk_introspection.py`, which scans `tests/` tree-wide and keeps passing over the new module unchanged; the GTK 4 counterpart head in `tests/test_gtk_view_census.py` stays where it is (its probes use the `GDK_BACKEND`/`GSK_RENDERER` pattern and are out of scope).

**Files.** `tests/support/gtk_child_probe.py` (new), `tests/test_gtk_theme_controls.py`, `tests/test_gtk_child_probe_support.py` (new).

**Acceptance criteria.**

- `tests/support/gtk_child_probe.py` holds the three program-string constants byte-equal to the deleted block and defines `run_gtk_child`; `tests/test_gtk_theme_controls.py` defines none of the four harness members itself beyond the one-line `_run_gtk_child` delegate and imports the three constants from `support.gtk_child_probe`; all seven call sites still read `self._run_gtk_child(...)` unchanged.
- A GTK 3 pixel probe renders the same pixels after the move as before it: the child programs are byte-identical concatenations, so every probe that passed before the move passes after it where GTK 3 introspection and a display are present, and skips with the child's own reason where they are missing — the probe set's behavior is unchanged.
- `tests/test_no_gtk_introspection.py` passes unchanged over the new support module, and `tests/test_no_unused_imports.py` reports no finding in the touched files.
- The new contract test pins the head's guard strings, the pixel reader's presence and `run_gtk_child`'s three exit-status behaviors (77 → skip with the child's reason, nonzero → failure with the child's output attached, 0 → pass), and fails when the 77 and 0 branches are swapped.
- `make check` passes.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::_MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
