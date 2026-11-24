# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Group the tests/support fidelity and kvantum modules into subpackages (part 3/6 of the tests/support regroup) (planned 2026-11-21 by the plan role)

**Needs review 2026-11-21 by feature: too large for one run**

**Goal.** Land the fidelity- and kvantum-family slices of the
tests/support regroup (see part 1/6 for the split's counts and rules; the
parts are independent).

**Modules to move (importer files counted on main).** `fidelity_cli_case`
(40) and `fidelity_delta_fixtures` (4) → `tests/support/fidelity/` with
`__init__.py`: `cli_case.py`, `delta_fixtures.py`. `kvantum_config_spec`
(4) → `tests/support/kvantum/` with `__init__.py`: `config_spec.py`.

**Approach.** As in part 1/6: move, rewrite importer lines and bare
references, retarget `mock.patch` strings, verify importers before each
move. Known stays, already measured: `kvantum_fixtures` (imported by
kvantum tests and the render dialog-gate tests), `jpeg_sampler_fixture`
(fidelity and sample tests), `png_fixtures` (fidelity, png and sample
tests), `sunken_field_reference` and `firstboot_lineedit` (each spans
desktoptheme, kvantum and render tests).

**Files touched.** The three moved modules, their importer files under
`tests/`, any `mock.patch` target strings, and docs naming the old paths.

**Acceptance criteria.**

- `ls tests/support/fidelity/ tests/support/kvantum/` lists both
  `__init__.py` files and the three moved modules;
  `rg -n 'support\.(fidelity_cli_case|fidelity_delta_fixtures|kvantum_config_spec)'`
  over `tests/`, `tools/`, `Makefile`, `docs/` and `*.md` finds no stale
  reference.
- Every `mock.patch` string naming a moved module resolves, and the tests
  that patch them pass.
- No behavior change: `git diff` shows moves, import lines, patch targets
  and doc paths only.
- `make check` passes after the final edit, apart from main's known-red
  tests.

### Invariants checker extraction, part 2/2: move the cross-check reference-resolution tests into their own module (planned 2026-11-22 by the plan role; "requires part 1/2 landed")

**Goal.** Finish the split planned in part 1/2: move the remaining
`cross_check` tests — how a row's test reference is resolved against the
repository (missing files, classes and methods, test-case bases, unreadable
and oversize modules, the repository boundary) and the control-character
escapes — out of `tests/test_invariants.py`, so the module keeps only the
`parse_rows` tests and the shipped-register drive.

**Approach.**

- `tests/test_invariants_cross_check.py`: append to `TestCrossCheck`, in
  their current order, with their comments:
  `test_cross_check_rejects_a_missing_test_file`,
  `test_cross_check_rejects_a_reference_to_an_unparseable_file`,
  `test_cross_check_rejects_a_reference_to_a_file_it_cannot_read`,
  `test_cross_check_rejects_an_oversize_module_instead_of_loading_it_whole`,
  `test_cross_check_rejects_a_reference_with_a_nul_byte`,
  `test_cross_check_rejects_a_missing_class`,
  `test_cross_check_rejects_an_empty_qualifier`,
  `test_cross_check_rejects_a_reference_with_a_trailing_segment`,
  `test_cross_check_rejects_a_missing_method`,
  `test_cross_check_rejects_a_reference_to_a_non_test_method`,
  `test_cross_check_rejects_a_class_with_no_tests`,
  `test_cross_check_rejects_a_method_on_a_class_with_no_test_case`,
  `test_cross_check_rejects_a_local_base_that_only_looks_like_a_test_case`,
  `test_cross_check_rejects_a_reference_outside_the_repository`,
  `test_cross_check_escapes_control_characters_in_a_section_heading`,
  `test_cross_check_escapes_control_characters_in_a_reference`,
  `test_cross_check_escapes_control_characters_in_a_syntax_error`,
  `test_cross_check_escapes_control_characters_in_a_theme_subsystem`.
  Add the imports they need that part 1 did not bring in
  (`write_file`, `traceback`, `containment_impl`,
  `assert_escapes_escape_character`); keep the module docstring's pointer
  to the shared base.
- `tests/test_invariants.py`: delete the moved tests; `TestHelpers` keeps
  only the seven `test_parse_rows_*` tests and `TestRepositoryRegister`
  stays as it is. Drop every import left unused.
- `tests/support/validation_gaps/no_fake.py`: retarget the
  `invariants-nul-row` reproduction, whose named test moves in this part,
  to `tests/test_invariants_cross_check.py::TestCrossCheck::<same method>`.
  `invariants-unreadable-test-file` names a `test_checker_mutations.py`
  test and stays as it is.
- `docs/invariants.md`: retarget the tooling row that anchors
  `tests/test_invariants.py::TestHelpers::test_cross_check_rejects_an_oversize_module_instead_of_loading_it_whole`
  to `tests/test_invariants_cross_check.py::TestCrossCheck::<same method>`;
  keep the guarantee text. The register cross-check validates that anchor,
  so the retarget must land in the same change.
- Before editing, grep `tests docs README.md .github` for the moved test
  names, to find any other anchor or prose pointer.

**Files touched.** `tests/test_invariants_cross_check.py`,
`tests/test_invariants.py`, `tests/support/validation_gaps/no_fake.py`,
`docs/invariants.md` (one anchor cell).

**Acceptance criteria.**

- `rg -n 'def test_cross_check|def test_parsed_module' tests/test_invariants.py`
  finds nothing, and each of the 18 moved test names is defined only in
  `tests/test_invariants_cross_check.py`.
- `rg -n 'TestHelpers::test_cross_check' tests docs` finds nothing.
- `rg -n 'invariants-nul-row' tests/support/validation_gaps/no_fake.py`
  names `tests/test_invariants_cross_check.py::TestCrossCheck`.
- `make check CHECK_TESTS='test_invariants test_invariants_cross_check
  test_validation_gaps test_no_unused_imports'` passes, with all
  `test_cross_check_*` names running under `TestCrossCheck`.
- `tests/test_invariants.py` is under 250 lines.
- No behaviour change: `git diff` shows only moved code, import lines,
  docstrings, and the anchor and no_fake retargets.
- `make check` passes after the final edit, apart from main's known-red
  tests.

### Inactive-dialog render: end the settle when both windows are mapped and the pair's focus has settled (planned 2026-11-24 by the plan role; independent of the waiting test-extraction entries)

**Goal.** Every render mode but three ends its settle on a KWin readiness
signal. The two-window `--inactive-dialog` render is one of the three: it
sleeps its whole settle (20 s in the gate) and captures whatever is there,
because the shared script reports the first mapped window only. The
director notes of 2026-11-23 in BUGS.md (`test_right_window_keeps_its_active_frame`,
`test_title_ink_is_the_inactive_text_colour`) call this readiness gap
real and its fix separate work. Give the mode its own readiness script,
which reports only once the pair is in the state the gate pins. The
settle then becomes a ceiling, so the gate can afford a longer one.

**Probe (2026-11-24, scratch copy, KWin virtual session, this host).** A
script with the condition below, with `workflow.py` no longer excluding
the mode, ran `tools/render_surface.py --inactive-dialog --settle 40`
three times: 8.2 s, 11.2 s and 18.9 s wall time, so none waited out the
ceiling. All three captures matched an unmodified `--settle 20` capture
pixel for pixel. `make check CHECK_TESTS='test_render_dialog_gates'`
passed in that copy at the gate's 20 s. This shows the mechanism works;
it does not reproduce or explain the quarantined failures.

**Approach.**

- `tools/render/window_rules.py`: add `pair_readiness_text()` beside
  `readiness_settle_text()`. Its KWin script holds one `check()` that
  reports at most once, when `workspace.windowList()` has a window
  captioned `INACTIVE_TITLE` that is not `active` and one captioned
  `FOCUSED_TITLE` that is. The report is the same `callDBus` the shared
  script makes. Run `check()` for the windows already listed and on
  `workspace.windowAdded`, `workspace.windowActivated` and each window's
  `captionChanged`. The last is needed if a caption is set after the window
  is added; connect it for listed and added windows alike.
- Give `write_readiness_settle_script` a keyword `pair: bool = False`
  selecting the text, written to the same `READINESS_SETTLE_SCRIPT` file.
- `tools/render/workflow.py`: drop the `mode.focus_settle` arm from the
  `readiness_script is None` condition and pass `pair=True` for that mode.
  Splash and `--desktop` keep no readiness script. Correct the comment.
  `session_script.py` needs no change: its focus and readiness stages
  already compose, its digests are pinned by
  `test_session_script_matches_the_four_pre_split_script_fixtures`, and the
  1 s paint grace applies. The focus-settle loop still starts and still
  runs until the capture returns.
- Update the `session_script` docstring where it says the listener ends
  the settle "when an eligible window maps", to allow for the pair.
- `tests/support/render/gates.py`: raise the `inactive` kind's `--settle`
  from 20 to 45. The tool's 90 s default timeout stays above it. Rename
  `TestRenderBudgets.test_the_inactive_gate_settles_for_twenty_seconds`
  in `tests/test_render_surface.py` to
  `test_the_inactive_gate_settles_for_at_most_forty_five_seconds`, and
  rewrite its comment: 45 s is now the ceiling for a pair that never
  reports. BUGS.md cites the old name; update that citation. Correct the
  neighbouring budget comments that call the inactive gate a 20 s one.
- `docs/invariants.md`, `## tooling`: the readiness row (starting
  "Single-window render sessions start a KWin readiness script") drops
  the inactive pair from the ceiling-only modes and states its condition;
  add the new tests there. Extend `docs/rendering.md`'s
  `--inactive-dialog` paragraph by one sentence.

**Not in scope.** Do not close or lift any quarantine in BUGS.md: their
holds wait for a recurrence. No change to the splash or desktop settle,
the focus-settle script, the single-window readiness text or any pinned
pixel.

**Files touched.** `tools/render/window_rules.py`,
`tools/render/workflow.py`, `tools/render/session_script.py` (docstring
only), `tests/support/render/gates.py`, `tests/test_render_window_rules.py`,
`tests/test_render_session_modes.py`, `tests/test_render_surface.py`,
`docs/invariants.md`, `docs/rendering.md`, `BUGS.md` (the renamed test only).

**Acceptance criteria.**

- A `--inactive-dialog` session script carries both a non-empty focus
  path and a non-empty readiness path: the `readiness=""` assertion in
  `TestSessionModes::test_inactive_dialog_launches_its_two_window_wrapper`
  becomes one that names `READINESS_SETTLE_SCRIPT`. The splash and desktop
  tests keep their `readiness=""` assertions unchanged.
- Through the workflow, the inactive mode's written script is the pair
  text and a single-dialog mode's is the existing text. A test fails if
  the two are swapped or if the inactive mode gets the first-window text.
- Unit tests in `tests/test_render_window_rules.py` pin that the pair
  script names both titles, requires the first inactive and the second
  active, connects `windowAdded`, `windowActivated` and `captionChanged`,
  calls the agreed service, interface and `ClientReady`, and does not
  contain the any-window eligibility test (`window.normalWindow || …`).
- `make render RENDER_MODE=inactive-dialog` with the settle raised to 45 s
  finishes before that ceiling, with a capture pixel-identical to one from
  main at `--settle 20`. Record both durations in the run's VERIFIED line.
- `TestInactiveDialogRender`'s tests pass with their pixel pins unchanged.
- `grep -rn test_the_inactive_gate_settles_for_twenty_seconds` over
  `tests`, `docs` and `BUGS.md` finds nothing.
- `make check` passes after the final edit, apart from main's known-red
  tests.

### Platinum icon theme: draw removable drives with an original `drive-removable-media` icon (planned 2026-11-24 by the plan role; independent of the waiting regroup, invariants, staging and inactive-dialog plans)

**Goal.** The icon theme's only device icon is `drive-harddisk`, so a USB
stick on the desktop or in the file manager's Places list is drawn with
Breeze's art beside the Platinum hard disk. Ship one original placeholder
icon, `drive-removable-media`, at 16x16, 22x22 and 32x32. The installed
`libKF6Solid.so.6` (6.13.0) contains the names `drive-removable-media`,
`drive-removable-media-usb` and `drive-removable-media-usb-pendrive`. One
name covers all three: planning-time probe with `kiconfinder6`, with a copy
of the theme selected through scratch XDG homes, resolved the first two to
Breeze; after a file named `drive-removable-media.svg` was added to the
copy's `32x32/devices`, all three resolved to that file (the icon loader
drops dash suffixes within a theme before trying the inherited one). Do not
ship alias files for the two longer names.

Optical, floppy and flash media icons are out of scope; so are the other
names the theme inherits from Breeze.

**Approach.**

- Add `devices/drive-removable-media.svg` under `16x16`, `22x22` and `32x32`
  of `theme/icons/org.macos8.desktop/`. `index.theme` already declares the
  three directories. Give each file the XML declaration, the comment
  `<!-- PLACEHOLDER: original removable-drive illustration pending user-approved artwork. -->`,
  a short comment saying it is our own drawing in the Platinum palette, not
  traced from anyone's artwork, and a root with matching `width`, `height`
  and `viewBox`. The art is the matching size's hard-disk body and bevel
  with a media slot (black, white lower lip) and a black eject button in
  place of the label plate and light. Each file holds these nine `rect`
  elements in order, written `x,y width×height fill`:
  - 32x32: `3,8 26×17 #000000`; `4,9 24×15 #DDDDDD`; `4,9 24×2 #FFFFFF`;
    `4,9 1×15 #FFFFFF`; `4,22 24×2 #999999`; `27,9 1×15 #999999`;
    `7,13 18×2 #000000`; `7,15 18×1 #FFFFFF`; `21,18 4×2 #000000`.
  - 22x22: `2,4 18×15 #000000`; `3,5 16×13 #DDDDDD`; `3,5 16×2 #FFFFFF`;
    `3,5 1×13 #FFFFFF`; `3,17 16×1 #999999`; `18,5 1×13 #999999`;
    `5,9 12×2 #000000`; `5,11 12×1 #FFFFFF`; `13,14 4×1 #000000`.
  - 16x16: `1,3 14×10 #000000`; `2,4 12×8 #DDDDDD`; `2,4 12×1 #FFFFFF`;
    `2,4 1×8 #FFFFFF`; `2,11 12×1 #999999`; `13,4 1×8 #999999`;
    `4,7 8×1 #000000`; `4,8 8×1 #FFFFFF`; `9,10 3×1 #000000`.
- `PLACEHOLDERS.md`: one row per file beside that size's `drive-harddisk`
  row, described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths to
  `SHIPPED_ICONS` after the hard-disk paths, and name the removable drive in
  the comment above it.
- `tests/test_icon_theme_geometry.py`: add the three `ICON_SHAPES` entries
  from the lists above. Add one test that each size's removable drive starts
  with the same six drawing elements (body and bevel) as that size's
  `drive-harddisk.svg`, comparing the shipped files.
- `docs/invariants.md`: in the icon-theme row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, say the
  `drive-removable-media` icon shares the hard disk's body and bevel, and
  record its provenance in the row's last cell: no reference pixels were
  used, the name is a KDE-required value read from `libKF6Solid.so.6`, and
  the drawing is this theme's own choice.
- `docs/installing.md`: add the removable-drive icon to the sentence listing
  the shipped placeholder illustrations.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`, `tests/test_icon_theme_geometry.py`,
`docs/invariants.md`, `docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding exactly
  the nine rectangles listed for that size, carries a placeholder marker and
  has a `PLACEHOLDERS.md` row; the existing inventory, palette, geometry and
  placeholder-register tests cover all three.
- Changing any of the first six rectangles in one removable-drive file makes
  the body-sharing test fail.
- Installing into a scratch root with
  `INSTALL_PACKAGES=icon-theme` puts the three files in the installed theme,
  and uninstalling removes them (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme into a
  scratch `XDG_DATA_HOME`, use a scratch `HOME`, `XDG_CONFIG_HOME` (with
  `[Icons] Theme=org.macos8.desktop` in `kdeglobals`), `XDG_CACHE_HOME` and
  `XDG_RUNTIME_DIR`, unset `DISPLAY` and `WAYLAND_DISPLAY`, and set
  `QT_QPA_PLATFORM=offscreen`. The three Solid names all resolve to the
  theme's `drive-removable-media.svg`. Report the output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full `make check`
  after the final edit, apart from main's known-red tests.

## Done

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

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
