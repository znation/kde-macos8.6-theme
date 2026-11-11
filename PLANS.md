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

### Platinum GTK 3 progress bar: span the fill across the trough interior and pin it with an offscreen pixel probe (planned 2026-11-11 by the plan role; independent of every other entry — it touches only the GTK 3 sheet's two oriented fill rules, `tests/test_gtk_theme_controls.py` and `docs/invariants.md`'s GTK 3 meter rows; at implementation re-read the landed meter rules and their comment block and re-grep every anchor this entry names)

**Goal.** A GTK 3 progress bar draws its fill as a thin strip centred in the trough, not as the full-height bar the reference meter shows. Measured 2026-11-11 on this host with the shipped `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` (child-interpreter `Gtk.OffscreenWindow`, a 100×10 default-size window holding a horizontal `Gtk.ProgressBar` at fraction 0.5): the trough renders 12px tall (1px `#000000` border rows 0 and 11, `#999999` inset arm at row 1 and column 1, `#EEEEEE` face), but the `#CCCCFF` fill covers only rows 4–7 — 4px of the trough's 10px interior — leaving `#EEEEEE` above and below it. The disabled `#999999` fill shows the same 4px strip. The reference meter fills every interior row: `tests/test_desktoptheme_progressbar.py`'s `FILL_ROWS` samples ten 1px fill rows from `desktop_fandom.png`'s memory meter. The sheet's own comment above `progressbar.horizontal trough` asserts that the fill's "natural allocation already spans the trough", and that is the reason it gives for declaring no fill minimum; the render shows the claim is false. GTK 3 gives the fill its own preferred cross-axis size and centres it in the trough.

**Approach.** In the GTK 3 sheet, add `min-height: 10px` to the existing `progressbar.horizontal progress` rule and `min-width: 10px` to the existing `progressbar.vertical progress` rule. Both rules already hold `margin: 0`, and 10px is the trough's existing interior minimum. Do not add new selectors: `test_meter_geometry`'s family sweep allows only the existing spellings. A scratch render with exactly these two declarations filled the horizontal bar's interior rows 1–10 at the filled columns, and the vertical bar's (12×100) interior columns 1–10 at the filled rows from the top. The fill paints over the trough's inset arm where it covers it, and the unfilled part keeps the `#999999` arm and `#EEEEEE` face. Rewrite the incorrect sentence in the comment block so it records the measured centring and the new minimum instead. `progressbar.osd progress` declares no minimum of its own and its trough is also 10px, so the oriented rules span it the same way. The `entry progress` strip and the `treeview.view.progressbar` cell use different selectors and are unaffected. GTK 4 is out of scope because its probe cannot run on a host without Xvfb. Add `test_progressbar_fill_spans_the_trough` to `TestGtkThemeControls` next to `test_entry_progress_draws_a_two_pixel_strip`. Build it from the same `_GTK3_CHILD_HEAD` / `_GTK3_SHEET_AND_WINDOW` / `_GTK3_PIXEL_HEAD` pieces, run it through `_run_gtk_child`, and strip `url(...)` as that test does. The child should render three bars in turn (a fresh `Gtk.OffscreenWindow` each): horizontal enabled, horizontal insensitive (`set_sensitive(False)`) and vertical enabled, all at fraction 0.5. Sample columns or rows well clear of the fill's end (for example x 25 and x 75 on the 100px bar) so the pin does not transcribe GTK's rounding of the fill length. Update `test_meter_geometry`'s whole-rule dicts for the two fill spellings. Add the minimum to `docs/invariants.md`'s GTK 3 meter-geometry row (the `test_meter_geometry` row), and append a `## gtk` row for the rendered probe that records the measured-render provenance (host, date, GTK 3 offscreen child) and the `FILL_ROWS` reference for the full-height fill, following the landed GTK 3 notebook render row's form.

**Files.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `tests/test_gtk_theme_controls.py`, `docs/invariants.md`.

**Acceptance criteria.**

- When GTK 3 introspection and a display are present, a horizontal 0.5-fraction bar rendered with the shipped sheet reads `#CCCCFF` at every interior row (trough rows 1 through 10) of a column inside the filled half, including row 1 where the inset arm would otherwise show. A column inside the unfilled half reads `#999999` at row 1, `#EEEEEE` at rows 2–10, and `#000000` at rows 0 and 11.
- The insensitive horizontal bar reads `#999999` at every interior row of a filled-half column. Its unfilled half matches the enabled bar's.
- The vertical 0.5-fraction bar reads `#CCCCFF` at every interior column (1 through 10) of a row inside the filled top half. A row inside the unfilled bottom half reads `#999999` at column 1 and `#EEEEEE` at columns 2–10.
- With the sheet's two new declarations removed, the probe fails: the shipped sheet before this change renders `#EEEEEE` at rows 2–3 and 8–10 of a filled column.
- Where GTK 3 introspection or a display is missing, the probe skips with the child's own reason, as the other GTK 3 pixel probes do. The suite process never imports `gi` (`tests/test_no_gtk_introspection.py` still passes).
- `test_meter_geometry` pins `progressbar.horizontal progress` as exactly `{margin: 0, min-height: 10px}` and `progressbar.vertical progress` as exactly `{margin: 0, min-width: 10px}`. Its family sweeps admit no new spelling. The sheet comment no longer claims that the fill's natural allocation spans the trough. `make check` passes.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::_MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
