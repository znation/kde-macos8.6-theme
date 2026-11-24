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

### Platinum icon theme: draw email with an original `internet-mail` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** KIO resolves a `mailto:` URL item's icon to the
`internet-mail` name, and on this host the name still draws Breeze's
art: ship one original placeholder icon, `internet-mail`, at 16x16,
22x22 and 32x32, in the same mimetype-item series as the landed
`text-html` and `x-office-*` files. Provenance: the installed
`libKF6KIOCore.so.6.13.0` carries the bare `internet-mail` literal
(`strings -e l`), sitting among the KIO protocol icon names (its
neighbours in the binary are `text-html`, `text-x-texinfo`,
`user-trash` and `unknown`), so a KDE consumer requests the name for
mail links; the shared MIME database gives the name no binding (zero
`internet-mail` hits across `/usr/share/mime/packages/*.xml`), so no
alias files and no MIME fallback are in play — one file covers exactly
its own name. Breeze ships the name only under `apps/` at 48 (plus
symbolic renditions this theme stays out of), so at the theme's item
sizes the name currently falls to Breeze's resampled 48px art.
Planning-time probe on 2026-11-24 with `kiconfinder6`, the theme
installed into scratch XDG homes (`QT_QPA_PLATFORM=offscreen`, no
`DISPLAY`): `internet-mail` resolved to Breeze's
`:/icons/breeze/apps/48/internet-mail.svg` while `text-html` resolves
to the theme's own file, so the theme must ship the name to win it.
The theme holds no application-icon series, so the files ship under
`mimetypes/`, the series KDE's item-icon lookup already draws its URL
and document icons from; the probe above confirms a `mimetypes/` file
wins the request (a scratch copy under `32x32/mimetypes/` resolved
with `kiconfinder6`), and the placement is recorded in the
`docs/invariants.md` provenance. No reference screenshot shows an
email icon, so no reference pixels are used and the drawing is this
theme's own choice.

**Approach.**

- Add `mimetypes/internet-mail.svg` under `16x16`, `22x22` and `32x32`
  of `theme/icons/org.macos8.desktop/`. `index.theme` already declares
  the three directories. Give each file the XML declaration, the
  comment `<!-- PLACEHOLDER: original envelope illustration pending user-approved artwork. -->`,
  a short comment saying it is our own drawing in the Platinum palette,
  not traced from anyone's artwork, and a root with matching `width`,
  `height` and `viewBox`. The art is a flat Platinum envelope, written
  `x,y width×height fill` for rects, with the flap as a filled black V
  band over the face:
  - 32x32: rect `2,6 28×20 #000000` (outline); rect `3,7 26×18
    #DDDDDD` (face); path `M3 7 L16 17 L29 7 Z` `#000000` (flap band);
    path `M4 8 L16 16 L28 8 Z` `#DDDDDD` (flap interior).
  - 22x22: rect `1,4 20×14 #000000`; rect `2,5 18×12 #DDDDDD`; path
    `M2 5 L11 12 L20 5 Z` `#000000`; path `M3 6 L11 11 L19 6 Z`
    `#DDDDDD`.
  - 16x16: rect `1,3 14×10 #000000`; rect `2,4 12×8 #DDDDDD`; path
    `M2 4 L8 9 L14 4 Z` `#000000`; path `M3 5 L8 8 L13 5 Z`
    `#DDDDDD`.

  In each list the first rect is the 1px #000000 outline, the second
  the #DDDDDD face, the third the #000000 flap band from the face's
  top corners to its centre, and the last the #DDDDDD interior that
  leaves the band 1px thick. Validate by XML only, never by
  rasterizing: `convert`'s MSVG reader bleeds 1px rects, so the pins
  below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside that size's `text-html`
  row, described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths where
  the other `mimetypes` paths are listed in `SHIPPED_ICONS` (the base
  tuple or one of the `SHIPPED_ICONS += tuple(...)` blocks), and name
  the email icon in the comment above the list beside `text-html`.
- `tests/support/icon/shape_pins/mimetypes.py`: pin the three drawings
  in its `PINS` table from the lists above (the table feeds
  `ICON_SHAPES` in `tests/support/icon/shape_pins/__init__.py`), with
  a comment recording that the name is the mailto item icon.
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, append the
  provenance of `internet-mail` to the row's last cell: no reference
  pixels were used; the name is read by the installed
  `libKF6KIOCore.so.6` for mailto URL items (the bare literal sits
  among the KIO protocol icon names, `strings -e l` verified); the
  shared MIME database gives the name no binding; the files ship
  under `mimetypes/` because the theme holds no application series and
  the item-icon lookup draws from the mimetype series; Breeze's own
  art was beaten by shipping the name at the theme's sizes (before the
  change, `kiconfinder6 internet-mail` with the theme installed into
  scratch XDG homes resolved to Breeze's `:/icons/breeze/apps/48`
  file), and the envelope drawing is this theme's own choice.
- `docs/installing.md`: add the email icon to the sentence listing the
  icon theme's placeholder illustrations and their sizes, beside the
  web-document sentence.

**Files touched.** Three new SVGs, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/mimetypes.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the elements listed for that size, carries a placeholder
  marker and has a `PLACEHOLDERS.md` row; the existing inventory,
  palette, geometry and placeholder-register tests cover all three.
- Changing an element's position, size, fill or order, or the flap
  band's vertices, in one file makes
  `test_each_icon_draws_its_pinned_artwork` fail; dropping a file
  while leaving it shipped makes
  `test_the_geometry_registry_covers_every_shipped_icon` fail.
- The new fills stay inside `PLATINUM_FILLS`, so
  `test_each_icon_uses_only_the_platinum_palette` passes unchanged.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme` puts
  the three files in the installed theme, and uninstalling removes them
  (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme into a
  scratch `XDG_DATA_HOME`, use a scratch `HOME`, `XDG_CONFIG_HOME` (with
  `[Icons] Theme=org.macos8.desktop` in `kdeglobals`), `XDG_CACHE_HOME` and
  `XDG_RUNTIME_DIR`, unset `DISPLAY` and `WAYLAND_DISPLAY`, and set
  `QT_QPA_PLATFORM=offscreen`. `internet-mail` resolves to the theme's
  32x32 file (at planning time, before this change, it resolved to
  Breeze's `:/icons/breeze/apps/48/internet-mail.svg`), and `text-html`
  stays on the theme's 32x32 file. Report the output in VERIFIED.
- The existing icon files, `index.theme` and the cursors are unchanged.
- `make check CHECK_TESTS='test_icon_theme test_icon_theme_geometry
  test_placeholders test_invariants'` passes, and so does full `make check`
  after the final edit, apart from main's known-red tests.

### Desktop render: recapture in-session until the wallpaper field is painted (planned 2026-11-24 by the plan role; independent of the waiting camera-video, internet-mail, media-eject and tests/support plans)

**Goal.** A `tools/render_surface.py <out> --desktop` capture must show the
painted wallpaper field every run, without a manual retry. The `--desktop`
mode keeps its measured 30 s settle ceiling (readiness stays off — landed
2026-11-21 as PLANS-DONE.md's "Desktop wallpaper, part 1/2", because the
shell's desktop window maps before the wallpaper paints), so plasmashell
that paints late still yields a capture with black rows below the bar
(measured by the feature role 2026-11-21: four consecutive runs, two black
and two painted), and the open `TestDesktopRender` quarantine family also
records sessions that exited 0 without writing `surface.png` at all. Today
the only repair is the post-hoc failure "capture is entirely black: …
retry with a longer `--settle`" — a manual knob. This plan moves the check
into the session, in the spirit of the answered budgets question
(QUESTIONS.md 2026-11-15, option 3: wait on evidence, keep the budget as a
ceiling): each capture is verified against the desktop gate's own pinned
field value, and an unpainted capture is recaptured inside the same
session instead of failing the check. Every attempt is logged, so a
recurrence still shows each verdict; this does not mask evidence, and the
post-hoc diagnosis stays as the backstop.

**Approach.**

1. `tools/render/field_probe.py` (new): `main(argv)` pinned callable per
   the CLI convention; contract
   `python3 tools/render/field_probe.py <png> <RRGGBB> <x> <y>`. Read the
   capture with the project's own PNG reader (`tools.png`'s `read_png`, the
   same decode `tools/render/workflow.py` uses — no new dependency) and read
   the RGB plane at the offset `(y * width + x) * 3`. Exit 0 when the pixel
   equals `<RRGGBB>`, exit 1 when it is another colour, exit 2 when the
   capture is missing, unreadable, not a PNG, or `(x, y)` is outside it,
   naming the capture and the reason on stderr and writing nothing to
   stdout. No colour tolerance: the field is a flat fill the gate already
   pins exact.
2. `tools/render/session_script.py`: extend
   `session_script(..., content_probe: str | None = None)`. When it is
   None the script text is byte-identical to today's, the same inert-stage
   pattern the window-report stage already uses. When set, the capture
   stage becomes a bounded loop: after `spectacle` returns, run the probe
   command; on exit 0 continue to the existing alive-check, resume and
   termination unchanged; on any other exit log
   `render-session: capture attempt N unpainted (probe exit S)` with the
   millisecond stamp, resume the client (`kill -CONT`) for 5 s so a late
   paint can land, re-freeze it (`kill -STOP`), and recapture, at most four
   attempts in total (1 + 3 retries; the added waits bound near 15 s plus
   probe time against the mode's 180 s timeout). The session exits with the
   last capture's status, and a resumed client that dies mid-capture still
   trips the existing `CLIENT_EXITED_DURING_CAPTURE` marker.
3. `tools/render/session.py::session_command`: thread `content_probe`
   through to `session_script` beside the focus, readiness and
   window-report script paths.
4. `tools/render/workflow.py::render`: for `args.desktop`, build the probe
   command `python3 <ROOT>/tools/render/field_probe.py "$capture" 63639C
   2 398` — the interpreter and path `shlex.quote`d at generation time, the
   command constructed only by the generator, so the session script may
   embed it verbatim — and pass it to `session_command`; every other mode
   passes None. Provenance of the probe pixel and value: `(2, 398)` sits in
   the desktop gate's pinned flat field rows 20..399 (`#63639C`, re-derived
   2026-11-21 from a consecutive pair; clear of the bar's rows 0..19 and of
   the excluded right half x=351..639), and `63639C` is the shipped
   wallpaper's own flat field, itself re-derived from the reference
   `macos8.6-screenshots/desktop_betawiki.png` — the plan introduces no new
   visual value. Name the constant beside the desktop mode's existing
   settle constants in `tools/render/surface_options.py` or the workflow,
   so one place owns the coordinate and colour.
5. `session_script`'s docstring: name the new stage beside the focus,
   readiness and window-report stages.
6. `docs/invariants.md`: in the `## tooling` `--desktop` row (the one whose
   guarantee begins "The `--desktop` render captures the theme's Plasma
   shell menu bar"), append a sentence that the desktop session verifies
   the capture's field pixel in-session and recaptures bounded, with the
   probe pixel, value and provenance, and add the new tests to its test
   column. `docs/rendering.md`: in the desktop-mode paragraph that records
   the 30 s settle and 180 s timeout, name the in-session paint
   verification.

**Files touched.** New `tools/render/field_probe.py`; `tools/render/session_script.py`,
`tools/render/session.py`, `tools/render/workflow.py`; new
`tests/test_render_field_probe.py`; `tests/test_render_surface_units.py`,
`tests/test_render_live_capture.py`, `tests/test_render_session_modes.py`;
`docs/invariants.md`, `docs/rendering.md`.

**Acceptance criteria.**

- `python3 tools/render/field_probe.py <png> 63639C 2 398` exits 0 on a
  capture whose pixel `(2, 398)` is `#63639C`, 1 on one that differs, and 2
  on a missing file, a non-PNG file, or a capture too small for the probe
  pixel, with the reason on stderr and empty stdout; direct-script and
  package invocation agree.
- `session_script(content_probe=...)` embeds the probe after the capture,
  the attempt log line, the 5 s resume window and the re-freeze before each
  recapture, and exits with the last capture's status; without it the
  script text is byte-identical to today's, so the existing
  `TestSessionScript` fixtures pass unchanged.
- The `--desktop` session command carries the probe command; the applet,
  splash and dialog session commands carry none (pinned in
  `TestSessionModes` beside `test_desktop_render_launches_the_plasmashell_client`).
- Live-stub run through the `tests/test_render_live_capture.py` `StubTools`
  harness with `--desktop` (a `plasmashell` stubbed like the applet
  launcher): a stub `spectacle` that writes a flat-black capture on its
  first call and a `#63639C`-field capture on its second publishes the
  painted one, exits 0, and the session log shows exactly two capture
  attempts with the unpainted line between them; a stub that always writes
  black fails the render with the existing entirely-black diagnosis and
  shows four attempts in the log.
- `make check` passes after the final edit, apart from main's known-red
  tests.

### Platinum icon theme: draw eject with an original `media-eject` icon (planned 2026-11-24 by the plan role; independent of the waiting plans)

**Goal.** The file dialogs' eject control draws the `media-eject`
action name, and on this host the name still draws Breeze's art: ship
one original placeholder icon, `media-eject`, at 16x16, 22x22 and
32x32, in the same actions series as the landed `go-next-symbolic`
arrow. Provenance: the installed `libKF6KIOFileWidgets.so.6.13.0`
carries the bare `media-eject` literal (`strings -e l`), so a KDE
consumer requests the name; the shared MIME database gives the name no
binding (zero `media-eject` hits across
`/usr/share/mime/packages/*.xml`), so no alias files and no MIME
fallback are in play — one file covers exactly its own name. Breeze
ships the name under `actions/` at 16, 22 and 32 (plus symbolic
renditions this theme stays out of). Planning-time probe on
2026-11-24 with `kiconfinder6`, the theme installed into scratch XDG
homes (`QT_QPA_PLATFORM=offscreen`, no `DISPLAY`): `media-eject`
resolved to Breeze's `:/icons/breeze/actions/32/media-eject.svg`, so
the theme must ship the name to win it. The theme declares an actions
directory at 16x16 and 22x22 only, so `index.theme` gains a
`32x32/actions` directory; the 16x16 and 22x22 renditions join the
existing ones. No reference screenshot shows an eject glyph, so no
reference pixels are used and the drawing is this theme's own choice.

**Approach.**

- `theme/icons/org.macos8.desktop/index.theme`: add `32x32/actions` to
  the `[Icon Theme]` `Directories` list and a `[32x32/actions]`
  section with `Size=32`, `Context=Actions`, `Type=Fixed`, matching
  the other declared sections.
- Add `actions/media-eject.svg` under `16x16`, `22x22` and `32x32`.
  Give each file the XML declaration, the comment
  `<!-- PLACEHOLDER: original eject-glyph illustration pending user-approved artwork. -->`,
  a short comment saying it is our own drawing in the Platinum
  palette, not traced from anyone's artwork, and a root with matching
  `width`, `height` and `viewBox`. The art is a bare Platinum eject
  glyph — a filled #000000 triangle above a filled #000000 bar, no
  face or bevel — written as one path and one rect per file
  (`x,y width×height fill` for the rect):
  - 32x32: path `M10 19 L22 19 L16 8 Z` `#000000` (triangle, apex up);
    rect `10,22 12×3 #000000` (bar).
  - 22x22: path `M7 13 L15 13 L11 6 Z` `#000000`; rect `7,15 8×2
    #000000`.
  - 16x16: path `M4 9 L12 9 L8 4 Z` `#000000`; rect `4,11 8×2
    #000000`.

  In each file the triangle's and the bar's bounding boxes share the
  same horizontal extent and centre, so the glyph reads as one mark;
  a -symbolic eject name stays out of scope, as the symbolic renditions
  always do. Validate by XML only, never by rasterizing: the pins
  below are the drawing contract.
- `PLACEHOLDERS.md`: one row per file beside that size's
  `go-next-symbolic` row, described as the marker describes it.
- `tests/support/icon/theme_inventory.py`: add the three paths where
  the other `actions` paths are listed in `SHIPPED_ICONS` (the base
  tuple or one of the `SHIPPED_ICONS += tuple(...)` blocks), and name
  the eject icon in the comment above the list beside
  `go-next-symbolic`.
- `tests/support/icon/shape_pins/actions.py`: pin the three drawings
  in its `PINS` table from the paths above (the table feeds
  `ICON_SHAPES` in `tests/support/icon/shape_pins/__init__.py`).
- `docs/invariants.md`: in the row anchored to
  `tests/test_icon_theme_geometry.py::TestIconGeometry`, append the
  provenance of `media-eject` to the row's last cell: no reference
  pixels were used; the name is read by the installed
  `libKF6KIOFileWidgets.so.6` for the file dialogs' eject control (the
  installed `.so.6.13.0` carries the bare literal, `strings -e l`
  verified); the shared MIME database gives the name no binding; the
  change adds the theme's `32x32/actions` directory to `index.theme`;
  Breeze's own art was beaten by shipping the name at the theme's
  sizes (before the change, `kiconfinder6 media-eject` with the theme
  installed into scratch XDG homes resolved to Breeze's
  `:/icons/breeze/actions/32` file), and the triangle-and-bar drawing
  is this theme's own choice.
- `docs/installing.md`: add the eject icon to the sentence listing the
  icon theme's placeholder illustrations and their sizes, beside the
  submenu-arrow sentence.

**Files touched.** Three new SVGs, `index.theme`, `PLACEHOLDERS.md`,
`tests/support/icon/theme_inventory.py`,
`tests/support/icon/shape_pins/actions.py`, `docs/invariants.md`,
`docs/installing.md`.

**Acceptance criteria.**

- Each new SVG is a square drawing of its directory's size holding
  exactly the path and rect listed for that size, carries a
  placeholder marker and has a `PLACEHOLDERS.md` row; the existing
  inventory, palette, geometry and placeholder-register tests cover
  all three, including the new `32x32/actions` directory
  (`test_every_shipped_icon_lives_in_a_declared_size_directory`).
- Changing the path's vertices, the rect's position, size, fill or
  order, or the glyph's centre alignment in one file makes
  `test_each_icon_draws_its_pinned_artwork` fail; dropping a file
  while leaving it shipped, or shipping a file in an undeclared
  directory, makes
  `test_the_geometry_registry_covers_every_shipped_icon` or
  `test_every_shipped_icon_lives_in_a_declared_size_directory` fail.
- The new fills stay inside `PLATINUM_FILLS`, so
  `test_each_icon_uses_only_the_platinum_palette` passes unchanged.
- Installing into a scratch root with `INSTALL_PACKAGES=icon-theme` puts
  the three files in the installed theme, and uninstalling removes them
  (the existing `TestInstall` cases).
- Manual check, when `kiconfinder6` is present: install the theme into a
  scratch `XDG_DATA_HOME`, use a scratch `HOME`, `XDG_CONFIG_HOME` (with
  `[Icons] Theme=org.macos8.desktop` in `kdeglobals`), `XDG_CACHE_HOME` and
  `XDG_RUNTIME_DIR`, unset `DISPLAY` and `WAYLAND_DISPLAY`, and set
  `QT_QPA_PLATFORM=offscreen`. `media-eject` resolves to the theme's
  32x32 file (at planning time, before this change, it resolved to
  Breeze's `:/icons/breeze/actions/32/media-eject.svg`), and
  `go-next-symbolic` stays on the theme's file. Report the output in
  VERIFIED.
- The existing icon files and the cursors are unchanged apart from the
  one `index.theme` directory addition.
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
