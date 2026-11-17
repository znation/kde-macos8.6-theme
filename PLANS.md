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

**Size drift (2026-11-14, steward; re-measured 2026-11-14 by the steward role):** PRINCIPLES.md
asks each file to stay small enough to read in one sitting, and this plan set's working budget is
roughly 800 lines (the suite-split entries below). Measured with `wc -l` over `tests/`, `tools/`
and `theme/` at this worktree's base, 23 files exceed 800 lines: `theme/gtk/.../gtk-3.0/gtk.css`
(7111) and `gtk-4.0/gtk.css` (6523), `theme/firefox/.../chrome/userChrome.css` (1581) and
`userContent.css` (941), and these tests: `test_render_surface_units.py` (1960),
`test_gtk4_theme.py` (1947), `test_render_dialog_gates.py` (1721), `test_render_file_dialog.py`
(1462), `test_gtk_theme.py` (1274), `test_render_surface.py` (1234), `test_gtk_theme_views.py`
(1179), `test_install_firefox.py` (1173), `test_gtk_css.py` (1170), `test_make_refusals.py`
(1063), `test_gtk_theme_osd.py` (1008), `test_render_failure_paths.py` (998),
`test_cursors_theme.py` (964), `test_apply_theme.py` (956), `test_theme_install.py` (940),
`test_check_parallel.py` (931), `tests/support/gtk_rule_cases.py` (881),
`test_firefox_theme_library.py` (864) and `test_local_hook.py` (857).
`test_gtk_theme_controls.py` has left the list (283 lines after GTK 3 split parts 1/11 to 10/11
landed). The only queued splits that touch a listed file are the two GTK 4 extraction entries for
`test_gtk4_theme.py`; together they move the scrolled-window run and the scroll-bar breadth tail,
which leaves it well above 800 lines. The render-test files (`test_render_surface_units.py`,
`test_render_dialog_gates.py`, `test_render_file_dialog.py`) have no plan. The plan role should
decompose those per family, as the GTK 4 extraction series did, before adding features to them.
The two GTK sheets and the Firefox `userChrome.css` are a different problem: the sheets are
single-file theme artifacts, so splitting them needs a packaging choice (for example GTK
`@import`) that is not settled here. This note queues nothing and changes no behavior.

### Render units suite extraction: isolate the scratch session setup checks (planned 2026-11-16 by the plan role)

**Goal.** `tests/test_render_surface_units.py` is still well above 800 lines
(1533 at this plan's base), and the size-drift note above asks the plan role
to break up the render-test files by family. This entry moves one whole
family, the `TestSessionSetup` class, into its own module. The class has 12
test methods. They check what `render_session.Session.create` makes: the
scratch directory layout and its cleanup on setup failure, the session
environment, and the Kvantum themes link `render_setup.link_kvantum_themes`
makes. No production code or behavior changes.

This entry depends on no other entry. The waiting "Render dialog gates suite
extraction: isolate the GTK 4 dialog gate" entry touches
`tests/test_render_dialog_gates.py`, a new `tests/test_render_gtk_dialog.py`
and the docs anchors for `TestGtkDialogRender`. This entry touches none of
those files or anchors, though both entries edit `docs/invariants.md` (on
different rows). `TestSessionScript` stays where it is on purpose: the open
BUGS.md entry about render-session wall-clock budgets may change its tests.

**Approach and files.**
- Create `tests/test_render_session_setup.py`. Give it a module docstring
  saying it holds the scratch-session setup checks moved out of
  ``tests/test_render_surface_units.py``: the layout, environment and
  cleanup of ``tools/render_session.py``'s ``Session.create``, and the
  Kvantum themes link in ``tools/render_setup.py``. Add `from __future__
  import annotations`, the `from support import repo_root  # noqa: F401`
  path line the source module uses, the imports the moved body needs, and
  the `if __name__ == "__main__":` guard (copy the source module's guard).
  Move `class TestSessionSetup` whole, every method in source order, with
  bodies and comments unchanged. Keep the class name. Do not import
  `tests/test_render_surface_units.py`.
- At this plan's base the moved class uses these module-level names: `os`,
  `stat`, `unittest`, `mock`, `tmp_dir`, `render_session` and
  `render_setup`. Of these, only `stat` is used nowhere else in the source
  module, so drop `import stat` from the source and keep the rest. Grep the
  moved range again for module-level names before writing the imports. The
  unused-import scanner in `make check` (`tests/test_no_unused_imports.py`)
  decides every import.
- In the source module's docstring, delete ``scratch environment and``
  from the clause ``scratch environment and KWin session command
  construction in ``tools/render_session.py`` `` (the moved family). Add
  one sentence naming ``tests/test_render_session_setup.py`` as the home of
  the scratch-session setup checks, next to the existing sentence that
  names ``tests/test_render_session_command.py``. Leave the rest of the
  docstring alone.
- `docs/invariants.md` names two moved methods, in the `## tooling` table:
  `tests/test_render_surface_units.py::TestSessionSetup::test_environment_forces_spectacles_null_video_platform`
  and
  `tests/test_render_surface_units.py::TestSessionSetup::test_environment_disables_kwin_screenshot_authorization`.
  Rewrite both to the `tests/test_render_session_setup.py::TestSessionSetup::…`
  path and leave the rest of each row alone. At this plan's base,
  `docs/rendering.md`, `docs/fidelity.md`, `tests/test_ci_workflow.py`,
  README.md, BUGS.md and QUESTIONS.md name neither `TestSessionSetup` nor a
  moved method. When implementing, grep `docs/ tests/ tools/ README.md
  BUGS.md QUESTIONS.md` for `TestSessionSetup` again and rewrite any new
  anchor that turns up. Do not rewrite history in PLANS-DONE.md or
  BUGS-FIXED.md. The class needs no skip guard: it starts no session or
  display.

**Acceptance criteria.**
- Unittest discovery lists all 12 `TestSessionSetup` methods exactly once,
  under `test_render_session_setup.TestSessionSetup`, and none under
  `test_render_surface_units`. `TestArguments`, `TestAppletPreflight`,
  `TestSessionScript`, `TestSessionThemeSources` and
  `TestCapturePaintCheck` are still listed under
  `test_render_surface_units` with the same methods as before.
- The moved class's AST matches the original's at this plan's base commit.
  Check this once during the run, for example by comparing `ast.dump` of
  the two `ClassDef` nodes. It is a run-time check, not a new committed
  test.
- `grep -rn "test_render_surface_units.py::TestSessionSetup" docs tests tools README.md`
  prints nothing, and the invariants anchor check in `make check` passes.
- `grep -n "^import stat" tests/test_render_surface_units.py` prints
  nothing, and the unused-import scanner reports nothing for either module.
- `tests/test_render_surface_units.py` shrinks by at least 150 lines, and
  `tests/test_render_session_setup.py` stays under about 200 lines.
- `git diff --stat` touches only `tests/test_render_surface_units.py`,
  `tests/test_render_session_setup.py` and `docs/invariants.md`, plus any
  file the anchor grep above turned up. `make check` passes after the final
  edit.

### Render-session readiness: the client writes RENDER_SESSION_READY_FILE once its window is shown (planned 2026-11-16 by the bugfix role)

**Goal.** Make the render settle end on a real client readiness signal, as the user chose
(option 2, QUESTIONS.md 2026-11-16). The session side is in place: `tools/render_session.py::session_script`
exports `RENDER_SESSION_READY_FILE` (`<capture>.ready`) before the client starts and ends the settle
early once the file exists, with the settle budget as the ceiling. Nothing writes the file yet, so
every session still waits its full settle.

**Remaining work (client side, one launch path per change).** Each client that a render starts must
touch `$RENDER_SESSION_READY_FILE` once its window is shown: the ksplashqml `--test` client (splash
mode), the plasmashell applet/desktop path, and the inactive-dialog wrapper. Each path needs a test
that stubs the readiness write, and a bounded real-session run to confirm the signal fires. Sibling of
the BUGS.md entry "Render-session tests rely on fixed wall-clock budgets" (which stays open until
these land).

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
