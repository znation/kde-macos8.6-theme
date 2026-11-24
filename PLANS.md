# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned
**Steward note 2026-11-24 by the steward role: drift in the queue.** Every
Planned entry on main (`2edd4589a`) is a test-file move or regroup: the
fidelity/kvantum regroup, the invariants checker split (two parts), and the
GTK staging split. None plans product work, and none plans a fix for the
Open flakes. Meanwhile BUGS.md's `## Open` section holds 27 entries on the
same commit, and 24 of them match a test or self-check title pattern
(`test_`, `failed`, `Seven`, `self-check`) — most are quarantined render
flakes parked as "Needs review" or "waiting for a recurrence". The
test-file splits are not wrong, but they are the only work being queued
while the red `make check` and the flake backlog stay unresolved. The plan
role should weigh a plan that addresses the flake backlog (for example, the
capture diagnostics several Open entries ask for) ahead of another split.
This note is a flag, not a new entry, and does not change queue order.

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

### Platinum icon theme: draw videos with an original `video-x-generic` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** A video file without Breeze art of its own type name — Flash
movies, Matroska, RealMedia, SMIL, MXF and their kin in the file manager
or an open or save dialog — is drawn with the theme's own screen art
beside the Platinum documents. Ship one original placeholder icon,
`video-x-generic`, at 16x16, 22x22 and 32x32. The installed shared MIME
database gives exactly 14 MIME types `generic-icon name="video-x-generic"`
(counted on `/usr/share/mime/packages/freedesktop.org.xml`):
`application/smil+xml`, `application/vnd.ms-wpl`, `video/x-flv`,
`video/x-javafx`, `video/vnd.youtube.yt`, `application/x-matroska`,
`application/mxf`, `application/annodex`, `application/ogg`,
`application/x-quicktime-media-link`,
`application/vnd.adobe.flash.movie`, `application/vnd.rn-realmedia`,
`application/x-netshow-channel` and `application/sdp`. KIconLoader's generic
fallback also substitutes `video-x-generic` for video MIME types that
would otherwise draw a per-type icon — `video/mp4`, `video/webm` and
`video/mpeg` are measured cases — so one file covers those names too,
and that wider capture is accepted: the theme's own placeholder art
winning over Breeze's per-type art is the theme's direction everywhere
else in the icon theme.
Planning-time probe with `kiconfinder6` under scratch `XDG_DATA_HOME`,
`XDG_CONFIG_HOME` (with `[Icons] Theme=org.macos8.desktop` in
`kdeglobals`), `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, with `DISPLAY` and
`WAYLAND_DISPLAY` unset and `QT_QPA_PLATFORM=offscreen`: with the theme
installed with no video icon of its own, `video-x-generic`,
`video-mp4`, `video-webm` and `video-mpeg` all resolved to Breeze's
internal `mimetypes/32/` files (the loader's fallback past the missing
names); after a stand-in `video-x-generic.svg` was added to the
installed copy's three `mimetypes` directories, all four names resolved
to the copy's 32x32 `video-x-generic.svg` — the fallback substitutes
`<type>-x-generic` for a missing MIME icon, so one file covers its own
name plus the per-type video names (re-verified 2026-11-24 by the plan
role). Ship no alias files and nothing but `video-x-generic`. Audio,
presentation, font and text names are covered by other plans or stay out
of scope; this plan shares no drawing with them.

**Approach.**

- Add `mimetypes/video-x-generic.svg` under `16x16`, `22x22` and `32x32`
  of `theme/icons/org.macos8.desktop/`. `index.theme` already declares
  the three directories. Give each file the XML declaration, the comment
  `<!-- PLACEHOLDER: original video illustration pending user-approved artwork. -->`,
  a short comment saying it is our own drawing in the Platinum palette,
  not traced from anyone's artwork, and a root with matching `width`,
  `height` and `viewBox`. The art is a display screen with a play
  triangle: a black frame, a white face, a black triangle, and a black
  stand (neck and base). Each file holds these elements in order, written
  `x,y width×height fill` for rects and a path `d` for the triangle:
  - 32x32 (5): rects `3,7 26×20 #000000`; `4,8 24×18 #FFFFFF`; path
    `M13 11 L23 17 L13 23 Z #000000`; rects `12,27 8×2 #000000`;
    `8,29 16×2 #000000`.
  - 22x22 (5): rects `2,5 18×13 #000000`; `3,6 16×11 #FFFFFF`; path
    `M9 8 L15 11 L9 14 Z #000000`; rects `8,19 6×1 #000000`;
    `5,20 12×1 #000000`.
  - 16x16 (5): rects `1,3 14×10 #000000`; `2,4 12×8 #FFFFFF`; path
    `M7 6 L10 8 L7 10 Z #000000`; rects `6,13 4×1 #000000`;
    `4,14 8×1 #000000`.

  These were drawn to read as a screen with a play triangle centred on
  the face and a two-part stand under the frame at every size (painted
  rect by rect at planning time).
- `PLACEHOLDERS.md`: one row per file beside that size's
  `image-x-generic` row, described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths to
  `SHIPPED_ICONS` beside the flash-media paths, and name the video icon
  in the comment above it (the comment already records which
  `generic-icon` groups the shipped mimetype names cover — give the 14
  video types there).
- `tests/support/icon/shape_pins.py`: pin the three drawings in
  `ICON_SHAPES` from the lists above (translate each list to `_shape`
  calls: rects keep their attributes, the triangle is
  `_shape("path", d="M13 11 L23 17 L13 23 Z", fill="#000000")` and kin);
  the existing `test_the_geometry_registry_covers_every_shipped_icon`
  and `test_each_icon_draws_its_pinned_artwork` then enforce the pins in
  both directions.
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, record the
  provenance of `video-x-generic` in the last cell: no reference pixels
  were used, the name is the `generic-icon` of 14 MIME types in the
  installed shared MIME database and, through KIconLoader's generic
  fallback, also covers `video/mp4`, `video/webm` and `video/mpeg`
  (measured with `kiconfinder6`: all four resolve to the shipped file),
  the screen-and-triangle drawing is this theme's own choice.
- `docs/installing.md`: add the video icon to the sentence listing the
  icon theme's placeholder illustrations and their sizes.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`, `tests/support/icon/shape_pins.py`,
`tests/test_icon_theme_geometry.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding exactly
  the elements listed for that size, carries a placeholder marker and
  comment and has a `PLACEHOLDERS.md` row; the existing inventory, palette,
  geometry and placeholder-register tests cover all three.
- Changing a rectangle's position, size or fill, the triangle's `d`, or
  the element order in one file makes the geometry pin fail.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme` puts
  the three files in the installed theme, and uninstalling removes them
  (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme into a
  scratch `XDG_DATA_HOME` (create the destination `icons` directory before
  copying the theme into it, so the copy does not flatten), use a scratch
  `HOME`, `XDG_CONFIG_HOME` (with `[Icons] Theme=org.macos8.desktop` in
  `kdeglobals`), `XDG_CACHE_HOME` and `XDG_RUNTIME_DIR`, unset `DISPLAY`
  and `WAYLAND_DISPLAY`, and set `QT_QPA_PLATFORM=offscreen`.
  `video-x-generic`, `video-mp4`, `video-webm` and `video-mpeg` all
  resolve to the theme's file. Report the output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full `make check`
  after the final edit, apart from main's known-red tests.


### Render sessions log a capture-time KWin window report (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** When a render gate's pixel pin fails, the session log names every
window KWin had at capture time — one line per `workspace.windowList()`
entry with its caption, whether it is active and its kind — so a recurrence
of the quarantined `'#CCCCCC' != '#000000'` pixel flakes (BUGS.md, the
`TestInactiveDialogRender` and `TestDesktopRender` entries parked pending a
recurrence) shows whether the client's window had actually mapped before the
settle ceiling ended the wait, instead of leaving only the settle path and
stage timestamps. The bugfix reviews of those entries name exactly this
capture-time mapping report as the missing evidence.

**Approach.** Reuse the session script's existing script-loading shapes; no
new process, D-Bus service or capture command.

1. `tools/render/settle_scripts.py`: add `WINDOW_REPORT_SCRIPT =
   "render-window-report.js"` and `window_report_text()` beside
   `readiness_settle_text()`: a one-shot KWin script with no signal handlers
   and no `callDBus`, whose `run` prints one
   `render-session: window at capture:` line per listed window carrying
   `window.caption`, `window.active` and the kind tag the existing scripts
   already filter on (`normalWindow`, `dialog`, `splash`, `desktopWindow`).
   KWin script `print` output already reaches the session log, as the
   focus-settle script's settled-activation line does. Add
   `write_window_report_script(session)` beside
   `write_readiness_settle_script`, writing through
   `_write_session_script`.
2. `tools/render/session_script.py`: a new stage between `_settle_wait()`
   and the capture stage loads the report script with the session's
   `qdbus6`/`qdbus` fallback and runs it once — the same loadScript/run
   shape `_focus_settle` uses, after the settle so the snapshot is the
   capture-time state. A missing `qdbus` or a failed load logs the omission
   ("no qdbus for the window report" / "the window report script did not
   load") and the capture proceeds unchanged. Thread the path as a third
   script argument beside focus/readiness in `session_script`'s signature
   and `_prologue`, inert like the other two guards when it is empty, so a
   caller that passes no report script gets byte-identical script text.
3. `tools/render/session.py::session_command`: accept
   `window_report_script: str | None = None` and pass it to
   `session_script`.
4. `tools/render/workflow.py::render`: write the report script for every
   mode — including splash and `--desktop`, which keep no readiness script —
   and pass its path to `session_command`.
5. Docs, same change: docs/fidelity.md's "Troubleshooting a render" black-
   capture row gains the window report as evidence a recurrence carries, and
   docs/invariants.md's tooling section gains a row pinning the capture-time
   report to its tests (the readiness row's provenance cell already covers
   KWin script `print` reaching the session log).

**Files touched.** `tools/render/settle_scripts.py`,
`tools/render/session_script.py`, `tools/render/session.py`,
`tools/render/workflow.py`, their pinning tests, docs/fidelity.md and
docs/invariants.md.

**Acceptance criteria.**

- `tests/test_render_settle_scripts.py` pins the new text: the report
  script names every `workspace.windowList()` entry's caption, active state
  and the four kind tags, and `write_window_report_script` writes the script
  into the session scratch root under `render-window-report.js`.
- `session_script` with a report path runs the load/run stage after the
  settle ends and before the capture starts, and a missing `qdbus` starts no
  load and still captures — pinned in `tests/test_render_session_focus_settle.py`
  in the shape of its existing focus-settle pins. Because the stage is inert
  when the path is empty, the four existing fixture digests in
  `test_session_script_matches_the_four_pre_split_script_fixtures` keep
  their lengths and digests; that test gains a fifth combination for the
  focus/readiness/report script set the CLI now builds.
- `tests/test_render_session_modes.py` pins that a mode render's session
  command argv names the report script (extend the existing inactive-dialog
  and desktop mode pins rather than adding a session).
- A gate failure's appended render output can show the report: on a painted
  capture, `report_render_log`'s tail includes the `window at capture:`
  lines, so `render_output_note` carries them into the next pixel mismatch
  without any gate change (pinned only as the existing
  `render_output_note` behaviour allows — no new gate test).
- The existing splash, desktop and single-dialog session shapes keep their
  settle ceilings and readiness behaviour unchanged: no test that pins a
  settle path, stage order or fixture digest changes its expectation except
  where the criteria above name it.
- `make check CHECK_TESTS='test_render_settle_scripts
  test_render_session_focus_settle test_render_session_modes
  test_render_session_command test_render_readiness'` passes, and so does
  full `make check` after the final edit, apart from main's known-red tests.

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
