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





### Platinum GTK 4 notebook: pin the rendered tab faces and header band through the opt-in snapshot probe (planned 2026-11-10 by the plan role; independent of the waiting radio-list gate parts — those touch the render-CLI plumbing (`tools/render_clients.py`, `tools/render_surface.py`, `tools/render_workflow.py`, the `Makefile`, README), `tests/test_render_surface.py`, the CLI unit suite and `docs/invariants.md`'s `## tooling` table, while this entry touches only `tests/test_gtk4_theme.py` and one appended end-of-table `## gtk` row of `docs/invariants.md`, so the entries share no file region and may merge in any order; at implementation re-read the landed notebook rules, the landed probe classes and the `## gtk` table tail and re-grep every anchor this entry names)

Needs review 2026-11-11 by feature: plan defect — the rendered notebook probe already exists on main at 9d343cc44 as `TestGtk4Theme.test_notebook_tab_faces_render` in `tests/test_gtk4_theme.py`.

**Goal.** The GTK 4 sheet carries the landed notebook recipe in `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: `notebook > header` paints the flat #DDDDDD band with a 1px #000000 border, panel tabs carry the raised bevel (1px #000000 border, `border-radius: 0`, `box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #999999`), and checked tabs are flattened (`box-shadow: none`, `border-bottom-color: #DDDDDD`), every state spelled in both the plain and `.reorderable-page` forms. That recipe is verified only through declaration checks: `tests/support/gtk_rule_cases.py::assert_tab_faces` drives `TAB_STATES` from `tests/test_gtk4_theme.py`, which cannot see a rule that never matches the rendered node tree or a GTK-side paint that ignores a declaration. No rendered-pixel probe of a `Gtk.Notebook` exists in the GTK 4 suite (a grep over `tests/test_gtk4_theme.py` finds no `Notebook` construction; the file's one snapshot probe pins a check/radio indicator, and the landed GTK 4 invariants rows state for their cases that declaration coverage does not establish rendered pixels), so a GTK regression — a tab node losing the equal-specificity tie to a toolkit rule, a bevel arm never painting, the checked state keeping stock's geometry — would ship green. The route to fix it is landed: `tests/test_gtk4_theme.py::TestGtk4Theme::test_mixed_indicators_draw_black_dashes` shows the shape (call `require_gui_opt_in`, run a child interpreter that imports `gi` with `Gtk` 4.0 loads the shipped sheet's bytes into a `Gtk.CssProvider` at priority 801 with the `'../assets/'` URL rewrite, paints with `Gtk.WidgetPaintable` + `renderer.render_texture` + `Gdk.pixbuf_get_from_texture`, settles by frame rather than a wall-clock deadline, and exits 77 when introspection or a display is missing). No collected reference screenshot shows a GTK notebook, so the comparison values are the sheet's own landed recipe and the palette constants (`FACE`, `BLACK`, `WHITE`, `GREY` from `tests/support/platinum_palette.py`, already imported in `tests/test_gtk4_theme.py`), recorded in the invariants row with that provenance.

**Approach and files.** Edit only `tests/test_gtk4_theme.py` and `docs/invariants.md`. In `TestGtk4Theme` add `test_notebook_tab_faces_render` beside `test_mixed_indicators_draw_black_dashes`, the same shape: `require_gui_opt_in()` first, then a child interpreter subprocess with `GDK_BACKEND=x11` and `GSK_RENDERER=cairo`, mapping exit 77 to a skip naming what is missing. The child loads the sheet bytes with the same asset-URL rewrite, builds a `Gtk.Window` holding a two-page `Gtk.Notebook` whose tab labels are single spaces (keeping every glyph row out of the pinned ink, the landed probes' no-glyph discipline), guards the header lookup with `assert header.get_css_name() == "header"` on `notebook.get_first_child()` the way the landed probe guards its indicator node, pumps the main context until allocated, snapshots the header with `Gtk.WidgetPaintable.new(header)` at the header's measured size, renders it through `renderer.render_texture(node, viewport)` into a pixbuf with the same deadline loop and failure reporting as the landed probe, then asserts each pinned pixel as a literal tuple. The pinned positions come from the render geometry measured at implementation on this host — the plan states no coordinates, and the probe re-derives every position from a fresh child render as the landed probes record their measurement dates. Pin four discriminating bands, each clear of glyph rows and of every tab's edge-ratio antialiasing: (a) one pixel inside the `notebook > header` band's interior, beyond the tabs' widths and clear of the band's border rows, expecting the flat #DDDDDD face — so a recolored or lost header face fails; (b) one pixel on the band's top border row, expecting #000000 — so a lost header border fails; (c) one pixel inside an unselected page's tab interior just below its top border row, expecting the bevel's #FFFFFF arm, and the relative pixel above its bottom border row, expecting the bevel's #999999 arm — so a dropped bevel arm, or an arm inverted to the other grey, fails; (d) the same relative pixels inside the checked page's tab, expecting #DDDDDD on both (the bevel dropped), plus one pixel on the checked tab's bottom border row expecting #DDDDDD where the unselected tab's bottom border row reads #000000 — so a never-flattened or never-matched checked state fails either side. Alternatively stated as falsifiability: any of a weakened header face, lost header border, dropped bevel arm, or a checked tab that keeps stock geometry changes at least one pinned pixel. In `docs/invariants.md` append one dated (2026-11-10) end-of-table `## gtk` row naming the probe's test, the missing reference surface (no collected screenshot in `macos8.6-screenshots/` shows a GTK notebook — the GTK scope's standing adaptation premise), the value sources (the sheet's landed notebook recipe and the platinum palette constants) and that the probe runs under the opt-in guard through the child interpreter, so it establishes rendered pixels only where GTK 4 introspection and an X display (Xvfb or equivalent) are present, as declaration checks never have.

**Acceptance criteria.**

- `make check` stays green where GTK 4 probes are not runnable: without `PLATINUM_RUN_GUI_TESTS=1`, the new probe raises the same skip as the landed mixed-indicator probe; where GTK 4 introspection or a display is missing despite the opt-in, the child exits 77 and the test skips with its own reason — so the hosted job keeps today's behavior, and this host runs the suite without the Xvfb it lacks.
- Where GTK 4 introspection and an X display are present with `PLATINUM_RUN_GUI_TESTS=1`, the child completes and its pinned pixels read the literal tuples for (a)–(d) exactly: the band interior and the checked tab's interior and bottom border are #DDDDDD, the header border row and the unselected tab's bottom border row are #000000, and the unselected tab's two bevel arms are #FFFFFF and #999999; deleting or weakening any landed notebook rule — a bevel arm dropped on the unselected tabs, the flat face lost on the header or the checked tab, or the checked tab's flattened bottom border lost — changes at least one pinned pixel and fails the probe.
- The probe imports no GTK in the suite process (the guard `tests/test_no_gtk_introspection.py` pins) and mentions no brand or toolkit name; the invariants row records the measured-render provenance and the missing reference surface. `make check` passes after the final edit.

### Reusable deterministic fixtures for recurring no-fake validation gaps (planned 2026-11-10 by the steward role; promote the recurring `no-fake` tag and scope the first deliverable to process-start races and bounded filesystem reads)

Needs review 2026-11-11 by feature: plan defect — the planned shared fixtures already exist on main at 236483302: `tests/support/popen_signal.py` is used by `tests/test_process_group.py`, and `tests/support/fifo_fixtures.py` plus the bounded `snippet_child.run` helper are used by the cited Firefox FIFO case.

**Goal.** The archive records repeated missing-fake gaps for the same validation patterns: SIGINT and SIGTERM arriving as `Popen` returns (BUGS-FIXED.md, “A SIGINT while a child starts can leave the caller without cleanup” and “A SIGTERM that arrives while a child starts leaves the command running”), and FIFO paths requiring bounded child checks (BUGS-FIXED.md, “A FIFO at either Firefox profile-discovery INI file blocks the install” and “A FIFO at a Firefox profile file blocks the install forever”). Each fix added its own fixture after the absence of one made confirmation harder. Reduce that repeated setup cost without introducing a dependency or obscuring each test's behavior.

**Approach and files.** Inspect the cited tests and `tests/support/` first. Identify the smallest reusable standard-library helpers for (1) injecting a signal at a controlled `Popen` return boundary and (2) running a child with a bounded timeout against a FIFO fixture. Add a helper only if it removes duplicated setup across the cited cases while keeping assertions and cleanup visible at the call site; otherwise document why the existing tests are already the appropriate reusable pattern and close the plan with that finding. Update the relevant test modules and any focused helper documentation, then run `make check`. Keep this effort limited to these two recurring fixture patterns; do not generalize every historical `no-fake` case into a fixture framework.

**Acceptance criteria.**

- The cited signal-race and FIFO tests use shared, narrowly named helpers where setup is genuinely duplicated, and retain explicit assertions for signal outcome, child termination, timeout, and cleanup.
- Helpers use only the standard library, have focused tests if they introduce behavior, and do not leave child processes or temporary files behind on failure.
- If inspection finds no meaningful shared setup, record the evidence in the plan's Done epitaph instead of adding abstraction. `make check` passes after the final edit.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::_MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
