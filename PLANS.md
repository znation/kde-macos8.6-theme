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

**Size drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; merged-plan facts re-trimmed 2026-10-23
by the clean role; validation scope clarified 2026-10-25 by the steward role; Firefox artifact
and content-surface status updated 2026-10-26 by the steward role; install-firefox
file list corrected 2026-10-27 by the steward role; shipped-SVG count updated
2026-10-27 by the feature role; Firefox content scope refreshed
2026-10-29 by the steward role; merged-series narration trimmed 2026-11-11 by the
steward role; measurements refreshed 2026-11-18 by the steward role):** PRINCIPLES.md asks
each file to stay small enough to read in one sitting. Current `wc -l` measurements include
`theme/gtk/.../gtk-3.0/gtk.css` (7111), `gtk-4.0/gtk.css` (6523), Firefox
`userChrome.css` (1581) and `userContent.css` (941). Among the tests,
`test_render_file_dialog.py` is 1336 lines and `test_gtk_theme_views.py` is 1142;
the two queued GTK 3 extractions split declarations out of the views module.
`test_render_surface_units.py` is 527 lines after its dialog-argument and capture-paint
extractions, and `test_gtk_theme.py` is 331 lines. Those two render extractions and the
measured list-row fixture extraction are archived in PLANS-DONE.md; they no longer queue
render-suite work here. The GTK sheets and Firefox stylesheets remain single-file theme
artifacts. The user chose source partials concatenated into one shipped sheet (QUESTIONS.md,
answered 2026-11-14); the "Stylesheet sources" series below queues that split. This note queues nothing and changes no
behavior.

### Stylesheet sources, part 3/3: split the Firefox chrome and content sheets into partials (planned 2026-11-19 by the plan role; "requires part 1/3 landed")

**Goal.** Give `theme/firefox/org.macos8.desktop/chrome/userChrome.css` (1581 lines) and
`userContent.css` (941 lines) per-family source partials, under the user's 2026-11-14 option 1
answer. Concatenation needs no `@import`, so the Firefox relative-import question does not
arise. Both shipped sheets stay byte-identical.

**Header exception (revised 2026-11-19 by the plan role).** `userChrome.css` opens with one
top-level comment spanning 802 lines (its first `*/` at column 0 closes it), so no legal cut
inside it exists. Byte identity outranks the size cap: each Firefox sheet's `000-header.css`
holds exactly that sheet's opening comment (through its closing `*/` line and the blank line
after it) and is exempt from the 500-line cap. No `*/`/`/*` pair is inserted and no shipped
byte changes. Every other Firefox partial keeps the cap.

**Approach and files touched.** Add two pairs to `tools/make_sheets.py::SHEETS`:

- `theme/firefox/src/userChrome` → the shipped `chrome/userChrome.css`
- `theme/firefox/src/userContent` → the shipped `chrome/userContent.css`

Split each sheet by part 1/3's cut, numbering and naming rules, with the header exception
above. For a partial led by an `@-moz-document` or `@media` block, the slug is the block's
first inner selector's leading name. The partials stay outside
`theme/firefox/org.macos8.desktop/`, so `tools/install_firefox.py` and its file lists see no
new file. In `tests/test_make_sheets.py`, add a Firefox counterpart to
`TestShippedSheetIsFresh.test_every_gtk_partial_is_at_most_500_lines_and_starts_at_top_level`
that applies the same start-of-partial check to every Firefox partial and the cap to every one
but `000-header.css`, asserting instead that `000-header.css` starts with `/*`, holds exactly
one comment, and its last non-blank line is `*/`. Add two `## firefox` rows to
`docs/invariants.md` (one per sheet) in the shape of the GTK concatenation rows, stating the
header exception. Extend part 1/3's README section to name the Firefox sheets.

**Acceptance criteria.**

- `python3 tools/make_sheets.py` exits 0 and leaves both Firefox sheets byte-identical
  (`git diff` empty for them), along with every sheet already in the table.
- Each Firefox `000-header.css` is exactly its sheet's opening comment; every other Firefox
  partial is at most 500 lines and starts at a top-level comment, rule or at-rule.
- A Firefox `000-header.css` that also carried a rule after its comment fails the new test.
- If a contributor edits only a shipped Firefox sheet, the freshness test fails and names that
  sheet's source directory.
- `make install-firefox` against a staged profile installs the same file set as before (the
  existing install tests pass unchanged), and `make check` passes after the final edit.

### Firefox installer tests: move the removal cases into their own module (planned 2026-11-19 by the plan role)

**Goal.** `tests/test_install_firefox.py` is 1191 lines, and PRINCIPLES.md asks for files small
enough to read in one sitting. Its last class, `TestRemove`, pins `install_firefox.py --remove`
and is about 515 lines on its own. This plan moves that class unchanged into a new
`tests/test_remove_firefox.py`, leaving `TestInstall` and `TestProfileLock` behind. No tool
behavior or test body changes. It is independent of the "Stylesheet sources" series and of the
`@define-color` test move; neither touches these files.

**Approach and files touched.**

- `tests/support/firefox_profile_case.py`: add a module-level `read_utf8(path)` that returns
  `path.read_bytes().decode("utf-8")`, the body of `_read` in `tests/test_install_firefox.py`.
  Both suites call `_read` (per L4, the helper moves into support rather than one test module
  importing the other). Each suite imports it as `_read`
  (`from support.firefox_profile_case import FirefoxProfileTestCase, read_utf8 as _read`), so
  the moved bodies stay verbatim. Also update the following docstrings in this file:
  - The module docstring: name `tests/test_remove_firefox.py` beside
    `tests/test_install_firefox.py` as a user of the case.
  - `assert_profile_absent`: say its call sites are in both installer suites, not only
    `tests/test_install_firefox.py`.
  - `run_with_failed_write`: the "Seven callers" sentence becomes six callers in
    `tests/test_install_firefox.py` and one in `tests/test_remove_firefox.py`.
  - `interrupt_unlink_to`: both of its callers move, so "Two callers in
    `tests/test_install_firefox.py`" becomes "Two callers in `tests/test_remove_firefox.py`".
  - `interrupt_write_to`: all five callers stay, so leave it unchanged.
  - Recount each changed docstring with grep after the move.
- New `tests/test_remove_firefox.py`:
  - Module docstring: it pins the removal half of the Firefox profile workflow. The install and
    profile-lock cases stay in `tests/test_install_firefox.py`.
  - Move `class TestRemove(FirefoxProfileTestCase)` there verbatim, with its `install` helper
    and every method in its current order, and keep the class name.
  - Give it the `if __name__ == "__main__": unittest.main()` footer.
  - Import only what the moved bodies use. As of this plan that is `errno`, `os`, `unittest`,
    `Path`, `mock`, `snippet_child`, `repo_root` (the sys.path side-effect import),
    `assert_fifo_refused`, `make_fifo`, `write_file as _write`, `FirefoxProfileTestCase`,
    `read_utf8 as _read`, and `firefox_user_files`, `firefox_user_js` and `install_firefox`
    from `tools`. Confirm each with grep.
- `tests/test_install_firefox.py`:
  - Delete `TestRemove` and the local `_read` function, and import `_read` from support as
    above.
  - Drop the imports no remaining code uses. As of this plan those are `os`, `snippet_child`,
    `assert_fifo_refused` and `make_fifo`. Confirm with grep and keep anything still referenced.
  - Its module docstring says it covers install and removal: point the removal part at
    `tests/test_remove_firefox.py`.
- `docs/invariants.md`: in the Firefox install row (the one that begins "The Firefox install
  copies both sheets") and the symlinked-`chrome/` row ("Firefox installation and removal refuse
  a symlinked `chrome/` directory"), rewrite every `tests/test_install_firefox.py::TestRemove`
  anchor, both the bare class and the `::method` forms, to `tests/test_remove_firefox.py::TestRemove`.
  Leave `TestInstall` and `TestProfileLock` anchors alone.
- `tests/support/validation_gaps/no_fake.py`: the `firefox-profile-file-fifo` reproduction
  anchors `tests/test_install_firefox.py::TestRemove::test_a_fifo_at_either_profile_file_is_refused_without_blocking`.
  Rewrite it to the new module.
- Docstrings that say removal is pinned in `tests/test_install_firefox.py`: name the new
  module for removal in `tests/support/firefox_chrome_cases.py` ("pins its install and
  removal"). `tests/test_firefox_user_js.py` and `tests/support/firefox_content_cases.py`
  name the file only for the install, so they stay. In `tests/support/theme_install.py`'s
  `write_file` docstring, add `test_remove_firefox.py` to the modules that bind `_write` as an
  import alias.
- Per L1/L3, also grep `docs/rendering.md`, `docs/fidelity.md`, `tests/test_ci_workflow.py`
  and `tests/support/validation_gaps/*.py` for `test_install_firefox.py::TestRemove` and the
  moved method names. As of this plan, the only hits outside the test file are the two
  invariants rows and the `no_fake.py` entry above. These are not render gates, so the
  `_GATE_FILES` lists do not apply. Archives (PLANS-DONE.md, BUGS-FIXED.md) keep their
  historical anchors.

**Acceptance criteria.**

- `tests/test_remove_firefox.py` defines `TestRemove` with the same test methods, names and
  bodies the class had in `tests/test_install_firefox.py`. `grep -n '^class TestRemove'
  tests/test_install_firefox.py` prints nothing.
- Together, the `test_*` method names collected from the two modules equal the set the
  original `tests/test_install_firefox.py` defined, with nothing lost or duplicated.
  `tests/test_install_firefox.py` is under 700 lines (`wc -l`).
- `grep -rn 'test_install_firefox.py::TestRemove' docs tests` prints nothing, and the
  invariants-anchor and validation-gap tests pass with the rewritten anchors.
- Each "N callers" count in `tests/support/firefox_profile_case.py` matches what grep finds
  across the two suites.
- No file under `theme/` or `tools/`, and not the `Makefile`, changes.
- `make check` passes after the final edit, and its run includes the new module's tests.

## Done

### GTK 3 suite extraction: isolate rubberband declarations (planned 2026-11-18 by the plan role) — done 2026-11-18 by the feature role

**Goal.** Give the GTK 3 selection-marquee declaration check a focused
module outside the oversized views suite. This is independent of the queued
accelerator-editor relocation and pending header drag-and-drop extraction.

**Approach and files touched.** Move
`TestGtkThemeViews.test_rubberband` from `tests/test_gtk_theme_views.py`
to new `tests/test_gtk_theme_rubberband.py::TestGtkThemeRubberband`,
preserving its body. Inherit `support.gtk_rule_cases.GtkSheetRuleCases`
and `unittest.TestCase`; import `ROOT` from `support.repo_root` and set
`CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"`.
The base already supplies `assert_rubberband`, parsed rules and the order
assertion; no shared-helper change is needed. Update the views routing
docstring and both GTK 3 rubberband rows in `docs/invariants.md` to the new
anchor, retaining their guarantees and provenance. Search
`docs/rendering.md`, `docs/fidelity.md`, `tests/test_ci_workflow.py` and
`tests/support/` for other moved anchors. Keep GTK 4 coverage and theme
sheets outside this relocation.

**Acceptance criteria.**

- Discovery exposes `test_rubberband` in the destination without a duplicate
  in views or inherited shared-control tests in the destination. Source and
  destination pass independently through project check selectors.
- The moved check retains the exact bare and view-specific rubberband
  selector inventory and existing recipe assertions. Altering the
  `flowbox rubberband` border or adding a rubberband selector fails it.
- Moving the rubberband group before the white `.view` group fails the
  moved order assertion.
- Both invariant anchors resolve and full `make check` passes. This is a
  declaration-test relocation with no new rendered-pixel claim.

### GTK 3 suite extraction: isolate accelerator-editor declarations (planned 2026-11-18 by the plan role) — done 2026-11-18 by the feature role

**Goal.** Give the on-screen accelerator-editor declaration check a focused
suite outside the oversized views module. This relocation is independent
of the queued drag-and-drop extraction and the paned extraction being handled.

**Approach and files touched.** Move
`TestGtkThemeViews.test_view_accelerator_editor` from
`tests/test_gtk_theme_views.py` to new
`tests/test_gtk_theme_accelerator_editor.py::TestGtkThemeAcceleratorEditor`,
preserving its assertions and stock-provenance comment. Replace the comment's
stale invariant line number with the accelerator-editor row's descriptive name.
Inherit `support.gtk_rule_cases.GtkSheetRuleCases` and `unittest.TestCase`;
set `CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"`,
importing `ROOT` from `support.repo_root` and `SELECTION` from
`support.platinum_palette`. The method uses the base's parsed sheet data
without a shared local helper. Update the source routing docstring and the
moved anchor in the accelerator-editor row of `docs/invariants.md`, retaining
the GTK 4 anchor and existing provenance. Search `docs/rendering.md`,
`docs/fidelity.md`, `tests/test_ci_workflow.py` and `tests/support/` for
other moved anchors. Theme sheets and GTK 4 tests need no changes.

**Acceptance criteria.**

- Discovery exposes the named method in the destination without a duplicate
  in views or inherited shared-control tests in the destination. Source and
  destination pass independently through project check selectors.
- The GTK 3 sheet retains exactly one `treeview.view acceleditor > label`
  spelling with only the selection-fill declaration, and no other
  `acceleditor` spelling. Changing that fill or adding an accelerator-editor
  state selector fails the moved check.
- Moving that rule before the selected header-drop group or after the
  list-row focus group fails the moved order check.
- Invariant anchors resolve and full `make check` passes. This relocation
  adds no rendered-pixel claim or keyboard-mapping change.

### GTK 3 suite extraction: isolate drag-and-drop declarations (planned 2026-11-18 by the plan role) — done 2026-11-18 by the feature role

**Goal.** Give GTK 3 header drag-feedback declaration checks a focused
suite outside the oversized views module. This relocation is independent
of the waiting paned-handle and pending message-dialog extractions.

**Approach and files touched.** Move
`TestGtkThemeViews.test_header_drop_indicator`,
`test_header_drop_arm_carries_no_padding` and
`test_no_dndtarget_node_declared` from `tests/test_gtk_theme_views.py` to
new `tests/test_gtk_theme_drag_drop.py::TestGtkThemeDragDrop`, preserving
their bodies. Inherit `support.gtk_rule_cases.GtkSheetRuleCases` and
`unittest.TestCase`; set
`CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"`, importing
`ROOT` from `support.repo_root` and `BLACK` and `SELECTION` from
`support.platinum_palette`. The base supplies sheet parsing and assertions;
no shared helper change is needed. Update the source routing docstring and
repoint the moved anchors in the GTK 3 drag-and-drop row of
`docs/invariants.md`, retaining its guarantee and stock-resource provenance.
Search `docs/rendering.md`, `docs/fidelity.md`, `tests/test_ci_workflow.py`
and `tests/support/` for other moved anchors. Keep GTK 4 coverage and GTK 3
rubberband checks in their existing suites; theme sheets need no changes.

**Acceptance criteria.**

- Discovery exposes the named methods in the destination without duplicate
  methods in views or inherited shared-control tests in the destination.
  Source and destination pass independently through project check selectors.
- The plain, legacy dotted-header and spaced-header selector spellings,
  each with plain, hover, active and selected states, retain selection fill,
  black ink, cleared background image and shadows, no border and zero
  radius checks. Changing just the legacy hovered header arm's fill fails
  a moved check.
- Adding padding to `treeview.view button.dnd` or declaring a `dndtarget`
  node in the GTK 3 sheet fails a moved check.
- Invariant anchors resolve and full `make check` passes. This relocation
  adds no rendered-pixel claim.

### GTK 3 suite extraction: isolate application notification declarations (planned 2026-11-18 by the plan role) — done 2026-11-18 by the feature role

**Goal.** Give the application notification band and frame checks a focused
suite outside `tests/test_gtk_theme.py`. This extraction is independent of
the notebook and infobar entries; notification button-state checks stay
with the existing OSD coverage.

**Approach and files touched.** Move `TestGtkTheme.test_app_notification_band`
and `test_app_notification_frame_border`, preserving bodies and comments,
to new `tests/test_gtk_theme_notification.py::TestGtkThemeNotification`.
Inherit `support.gtk_rule_cases.GtkSheetRuleCases` and `unittest.TestCase`,
setting `CSS_PATH` to
`ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"`.
Import `ROOT` from `support.repo_root`, `gtk_css` from `support`,
`BLACK`, `FACE` and `WHITE` from `support.platinum_palette`, and
`ETCH_DARK` from `support.gtk_theme_spec`, plus `re` and `unittest`.
Do not inherit `GtkSharedControlCases` or import another test module.
Update the source routing docstring and prune imports only when unused.
Repoint the moved anchors in `docs/invariants.md`, preserving their
provenance. Search `docs/rendering.md`, `docs/fidelity.md`,
`tests/test_ci_workflow.py` and `tests/support/` for other moved anchors.
Leave shared helpers, stylesheets and production tools unchanged.

**Acceptance criteria.**

- Discovery exposes the named methods in the new class without duplicates
  in `TestGtkTheme` or inherited shared-control tests in the new module.
  Source and destination run independently through check selectors.
- Notification base, frame and backdrop declarations still require the
  existing face, ink, square corners and etched edge. Reversing the border
  reset and bottom-border declarations fails the extracted checks.
- The exact notification selector census remains checked; an added
  notification selector fails. Direct border children still require
  precisely the border-style and box-shadow resets, so a restored frame
  shadow fails.
- Invariant anchors resolve, focused source and destination checks pass,
  and full `make check` passes. No rendered-pixel claim is added.

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
