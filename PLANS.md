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
Charcoal-style body face and selected by the global theme for general, toolbar and
smallest-readable fonts, and ChicagoFLF, a
public-domain Chicago-style face, is selected for menus and window titles (its licence was checked 2026-11-12 by the director role);
JetBrains Mono (the user-approved fixed-width face, QUESTIONS.md answered 2026-11-12)
is selected for KDE's fixed-width font.
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


### GTK 4 suite extraction: isolate progressbar declarations (planned 2026-11-12 by the plan role)

**Goal.** `tests/test_gtk4_theme.py` is still one large `TestGtk4Theme`
class. Move the seven `test_progressbar_*`-named declaration checks (about 81
lines at this plan's base commit) into their own module, the same way the
landed OSD (`tests/test_gtk4_osd.py`), scale (`tests/test_gtk4_scale.py`),
spinbutton, disabled, emoji, entry, notebook and scrollbar parts moved theirs.
This is independent of the waiting "GTK 4 suite extraction: isolate switch
declarations" entry (that entry moves only `test_switch*` methods; the two
method sets do not overlap and neither entry edits the other's invariants
members, though both edit `tests/test_gtk4_theme.py` and — on the shared OSD
container row of `docs/invariants.md` — the same table row, rewriting
different members of it, so whichever merges later re-reads that row before
writing). The landed rendered probe `tests/test_gtk4_progressbar_probe.py`
and its invariants row stay untouched. At implementation re-grep every anchor
this entry names. No stylesheet or production behavior changes.

**Approach and files.**
- Create `tests/test_gtk4_progressbar.py` with
  `class TestGtk4Progressbar(Gtk4SheetRuleCases, unittest.TestCase)` and a
  one-line module docstring on the landed extraction modules' pattern. Move
  every `TestGtk4Theme` method whose name starts with `test_progressbar_`
  plus the bare `test_progressbar`, keeping each method's body and docstring
  unchanged: `test_progressbar`, `test_progressbar_label_ink`,
  `test_progressbar_osd_trough_paint`, `test_progressbar_osd_trough_thickness`,
  `test_progressbar_oriented_trough_thickness`,
  `test_progressbar_directional_corners` and `test_progressbar_disabled_filter`.
  `test_progressbar` and `test_progressbar_label_ink` are contiguous in the
  file between `test_scrolled_corner_junction_shares_the_scrollbar_band` and
  `test_treeview_progress_cell_faces`, which stay;
  `test_progressbar_osd_trough_paint` sits between
  `test_treeview_progress_cell_faces` and `test_headerbar_meter_faces`, which
  stay; the remaining four are contiguous between `test_headerbar_meter_faces`
  and `test_selected_row_meter_rims`, which stay. Methods that only contain
  `progress` mid-name (`test_treeview_progress_cell_faces`,
  `test_headerbar_meter_faces`) stay where they are. The landed GTK 3 checks
  live elsewhere and stay there. Never import
  `tests/test_gtk4_theme.py` or inherit `TestGtk4Theme`.
- The new module imports exactly the names the moved bodies use: `TROUGH`,
  `BLACK` and `GREY` from `support.platinum_palette` and `PROGRESSBAR_TROUGH`
  from `support.gtk_theme_spec` (the source module
  `tests/test_gtk4_theme.py`'s import blocks draw them from the same two
  modules; grep-counted at this plan's base commit, the moved bodies use each
  constant and the source module still references it after the move, so the
  source import block needs no pruning). Every assertion helper the bodies
  call comes with `Gtk4SheetRuleCases` and its base classes: `assert_rule`,
  `assert_rule_group`, `assert_rule_after` and `assert_progressbar` on
  `support/gtk_rule_cases.py`'s `GtkSheetRuleCases`, and the `self.rules` and
  `self.selectors` attributes come the same way; the moved bodies call no
  other support name (no `gtk_css`, `parse_css`, `HEX`, mock, tempfile,
  symlink helper or `re` use).
- In `docs/invariants.md`, rewrite each
  `tests/test_gtk4_theme.py::TestGtk4Theme::test_progressbar…` anchor to
  `tests/test_gtk4_progressbar.py::TestGtk4Progressbar::test_progressbar…`,
  wherever it appears — in the anchor column and in provenance prose (the
  GTK 3 OSD thin-bar row names `test_progressbar_osd_trough_paint` inside its
  prose). `grep -o 'TestGtk4Theme::test_progressbar[a-z_]*' docs/invariants.md`
  finds fifteen member mentions on eight rows at this plan's base commit
  (`test_progressbar` bare 4, `test_progressbar_osd_trough_paint` 3,
  `test_progressbar_disabled_filter` 2, `test_progressbar_label_ink` 2,
  `test_progressbar_osd_trough_thickness` 2, and one each of
  `test_progressbar_directional_corners` and
  `test_progressbar_oriented_trough_thickness`). On the rows that also name
  members staying in `TestGtk4Theme` (the shared OSD container row names
  `test_video_osd_image_corners` and `test_infobar`; the rendered-probe row
  names `test_progressbar_faces_render`) rewrite only the
  `test_progressbar_*` members and leave the others and the row prose alone —
  except where the prose names a moved member, as the thin-bar row does, which
  moves with it. Do not rewrite history in PLANS-DONE.md or BUGS-FIXED.md.

**Acceptance criteria.**
- Unittest discovery lists each of the seven moved methods exactly once, under
  `test_gtk4_progressbar.TestGtk4Progressbar`, and none of them under
  `test_gtk4_theme.TestGtk4Theme`. Every other `TestGtk4Theme` method is still
  listed there.
- For each moved method, the AST of its function definition is identical to
  the original's at this plan's base commit, checked once during the run (for
  example by comparing `ast.dump` output). This is a run-time check, not a new
  committed test.
- `grep -n 'TestGtk4Theme::test_progressbar' docs/invariants.md` prints
  nothing, every staying member on the shared rows still reads its original
  module, and the invariants checker inside `make check` resolves every new
  anchor.
- `tests/test_gtk4_theme.py` shrinks by at least 75 lines, and
  `tests/test_gtk4_progressbar.py` stays under about 250 lines.
- `git diff --stat` touches only `tests/test_gtk4_theme.py`,
  `tests/test_gtk4_progressbar.py` and `docs/invariants.md`. `make check`
  passes after the final edit.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
