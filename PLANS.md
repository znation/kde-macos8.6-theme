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

### Platinum GTK 3 disabled view: restate the insensitive view family's white field and grey ink over the toolkit's stock disabled arms and pin both with an offscreen pixel probe (planned 2026-11-11 by the plan role; independent of every other entry — it adds one dated block directly after the GTK 3 sheet's landed disabled-selected groups, two tests to `tests/test_gtk_theme.py`, one render probe to `tests/test_gtk_theme_controls.py` and one appended end-of-table `## gtk` row of `docs/invariants.md`; the waiting OSD RTL entry touches only that sheet's four OSD entry-field state groups and the landed RTL-mirror comment, its own OSD test module and one probe method of its own in the same controls file, so the entries share no sheet region, test name or assertion and either merge order leaves both working — at implementation re-grep every anchor this entry names, since the two spin entries also extended these files)

**Goal.** An insensitive list, icon view, text view or tree view in a GTK 3 app still paints the toolkit's own foreign disabled faces. Measured 2026-11-11 with `gresource extract` of `/org/gtk/libgtk/theme/Adwaita/gtk-contained.css` in `/usr/lib/x86_64-linux-gnu/libgtk-3.so.0` (libgtk-3 3.24.49, the 2055-line resource; paths recorded in `docs/invariants.md`): the resource declares exactly three disabled view arms — line 28 `.view:disabled, iconview:disabled, .view text:disabled, iconview text:disabled, textview text:disabled { color: #929595; background-color: #faf9f8; }`, line 699 `treeview.view:disabled { color: #929595; }` and line 705 `treeview.view:disabled:backdrop { color: #d4cfca; }` — and the toolkit's dark twin `gtk-contained-dark.css` carries the same-shaped family (probe it at implementation and quote it in the invariants row). Every member of the first arm out-specifies the landed base view group `.view, textview text, list` (which declares `background-color: #FFFFFF` and `color: #000000`), and the landed disabled-selected groups own only the `:disabled:selected` combinations, so today an insensitive view paints the warm near-white stock field `#faf9f8` under stock grey `#929595` ink, and in an unfocused window the tree ink pales to stock's `#d4cfca`, instead of the landed white field, the landed insensitive grey and the landed disabled-selected backdrop policy. No collected reference screenshot in `macos8.6-screenshots/` shows a disabled GTK view (the standing GTK-scope adaptation premise), so the values are platform-adapted: the fill reuses the landed white view field the base group states, the ink reuses the landed insensitive grey `#888888` (the same grey the landed disabled label, entry and disabled-selected arms paint, re-derived from the colour scheme's `[Colors:Button] ForegroundInactive`), and the backdrop twin keeps that grey in unfocused windows exactly as the landed `row:backdrop:disabled:selected` and `treeview.view:disabled:selected:backdrop` restatements do.

**Approach.**

1. `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: one dated (2026-11-11) comment block plus three rules appended directly after the landed `label:backdrop selection:disabled, …` disabled-selected group and before the tab-close comment block that follows it (re-grep the anchor before writing): a comma group spelling stock's line-28 members byte-equal — `.view:disabled, iconview:disabled, .view text:disabled, iconview text:disabled, textview text:disabled` — restating exactly `color: #888888` and `background-color: #FFFFFF`, so the byte-equal spelling wins both per-property ties by later user-sheet source order; and the two byte-equal tree arms `treeview.view:disabled { color: #888888; }` and `treeview.view:disabled:backdrop { color: #888888; }`, restated separately because their spellings out-specify the comma group and would otherwise keep the stock values. The comment records: the three stock arms with their resource lines and the foreign literals elided per the palette convention (the verbatim values live in the invariants row), the missing reference surface, the value sources named in the Goal, and the exclusions — the `:disabled:selected` combinations (the landed disabled-selected groups own their ink, including `treeview.view:disabled:selected` and its backdrop twin), the toolkit's remaining insensitive arms outside the view family (label, entry and button fields are the landed disabled-text records' own), and the GTK 4 sibling: the integration library's per-family disabled view ink arms and the landed 2026-11-09 GTK 4 disabled-view group's deliberately excluded `color` co-declaration are a separate candidate entry, not this one. No geometry, margin, transition or other-state declaration is added.

2. `tests/test_gtk_theme.py`: add `test_disabled_view_face_and_ink` beside the landed disabled-selected block in `TestGtkTheme`, shaped like `tests/test_gtk4_theme.py::TestGtk4Theme::test_disabled_view_face`: count-one pins (each of the three rules appears exactly once) and exact-declaration pins (the comma group to exactly `color: #888888` and `background-color: #FFFFFF` via `tests/support/gtk_theme_spec.py`'s `DISABLED_TEXT` recipe plus the white field, the two tree arms to exactly `color: #888888`), plus token sweeps keyed on substrings no other landed selector carries (e.g. `treeview.view:disabled:backdrop`), so a dropped rule, a stray extra declaration or a changed value fails.

3. `tests/test_gtk_theme_controls.py`: add `test_disabled_view_renders_the_white_field_and_grey_ink` to `TestGtkThemeControls`, built from `support.gtk_child_probe`'s `_GTK3_CHILD_HEAD` and `_run_gtk_child` like the landed render probes: strip `url(...)` from the shipped sheet, install the provider, and render, in a fresh `Gtk.OffscreenWindow`, a `Gtk.TextView` with `set_sensitive(False)` and `set_can_focus(False)` whose buffer holds one long line of underscore characters (a solid ink stroke), packed in a 5px-border `Gtk.Box`. Read the text view's allocation and assert: the four allocation-interior corner pixels each read exactly `#FFFFFF` (the restated field fill); no pixel anywhere in the allocation equals the stock literal `#929595` or `#faf9f8` (both are non-grey, and the restated sheet paints only pure white and pure grey there, so antialiasing can never synthesize them); and at least one allocation row carries eight or more consecutive pixels equal to exactly `#888888` (the underscore stroke's full-coverage core under the restated ink). With the ink twin removed the cores read `#929595` and the test fails; with the fill twin removed the field reads `#faf9f8` and the test fails. It skips with the child's own reason where GTK 3 introspection or a display is missing.

4. `docs/invariants.md`: one appended end-of-table `## gtk` row naming both new tests and recording: the missing reference surface (no collected screenshot shows a disabled GTK view), the provenance (the three stock arms probed 2026-11-11 with `gresource extract` as in the Goal, lines 28, 699 and 705, their verbatim foreign values quoted in the row — `#929595`, `#faf9f8`, `#d4cfca` — plus the dark twin's same-shaped family probed at implementation), the value sources (the landed white field and the landed insensitive grey, with the backdrop policy and its landed disabled-selected backdrop precedents), the `:disabled:selected` exclusion, and the GTK 4 sibling left to its own candidate.

**Files.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `tests/test_gtk_theme.py`, `tests/test_gtk_theme_controls.py`, `docs/invariants.md`.

**Acceptance criteria.**

- The GTK 3 sheet contains exactly one rule for the five-member disabled view comma group (declaring exactly `color: #888888` and `background-color: #FFFFFF`), exactly one `treeview.view:disabled` and exactly one `treeview.view:disabled:backdrop` (each declaring exactly `color: #888888`), each placed directly after the landed disabled-selected groups; the landed disabled-selected groups, the base `.view, textview text, list` group and every other sheet rule are unchanged.
- `tests/test_gtk_theme.py::TestGtkTheme::test_disabled_view_face_and_ink` passes and fails on a dropped rule, a comma member lost, a stray extra declaration, or a changed value.
- When GTK 3 introspection and a display are present, `test_disabled_view_renders_the_white_field_and_grey_ink` renders the insensitive text view reading `#FFFFFF` at its four interior corners, no allocation pixel equal to `#929595` or `#faf9f8`, and an eight-pixel `#888888` underscore run; it fails with either restated rule removed or spelled with a stock value, and it skips with the child's own reason where GTK 3 or a display is missing.
- `docs/invariants.md` carries the appended row, and `make check` passes.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::_MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
