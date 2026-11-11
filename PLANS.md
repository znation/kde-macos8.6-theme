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

### Platinum GTK 3 OSD spin field in RTL: mirror the etch's inset arm to the field's exposed edge in the four OSD state twins (planned 2026-11-11 by the plan role; independent of every other entry — it touches only the GTK 3 sheet's four OSD entry-field state groups and the landed RTL-mirror comment beside the plain spin rules, `tests/test_gtk_theme_osd.py`, one new probe in `tests/test_gtk_theme_controls.py` and one new `docs/invariants.md` row; the waiting child-probe harness entry touches only that probe file's harness block, the `_GTK3_*` constants and `_run_gtk_child`, whose call surface this entry's new probe keeps, so either merge order leaves both working)

**Goal.** The landed RTL mirror `spinbutton:dir(rtl):not(.vertical) { box-shadow: inset -1px 1px #999999; }` in `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` deliberately excluded the four `.osd spinbutton:not(.vertical)` state groups, whose record that entry named "a future candidate". Those groups restate `box-shadow: inset 1px 1px #999999` at equal-or-higher specificity — `.osd spinbutton:not(.vertical)` ties the (0,2,1) mirror and wins by later source position, and the `:focus`/`:backdrop`/`:disabled` arms out-rank it — so an RTL OSD spin field still draws the half-etched field the mirror fixed everywhere else. Measured 2026-11-11 on this host with a GTK 3 offscreen child rendering a `Gtk.SpinButton` under an `.osd`-classed `Gtk.Box` (columns L+1 and R−1 of the spin button's allocation, rows T+1, T+2, T+3 and B−1): LTR reads `#999999` at all four rows at L+1 and `#000000` at all four at R−1; RTL reads `#000000` at all four at L+1 and `#999999`, `#FFFFFF`, `#FFFFFF`, `#FFFFFF` at R−1 — the top arm only, no vertical arm, with the plain mirror rule already active. A scratch copy of the sheet with `.osd spinbutton:dir(rtl):not(.vertical) { box-shadow: inset -1px 1px #999999; }` appended rendered RTL R−1 as `#999999` at all four rows and left LTR unchanged.

**Approach.**

1. `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: directly after each of the four groups at the `/* No collected reference screenshot shows a field inside a GTK OSD overlay … */` record — `.osd spinbutton:not(.vertical), .osd entry`, `.osd spinbutton:focus:not(.vertical), .osd entry:focus`, `.osd spinbutton:backdrop:not(.vertical), .osd entry:backdrop`, `.osd spinbutton:disabled:not(.vertical), .osd entry:disabled` (re-grep each selector for count-one before writing) — append one twin rule carrying exactly one declaration, `box-shadow: inset -1px 1px #999999`, spelled `.osd spinbutton:dir(rtl):not(.vertical)`, `.osd spinbutton:dir(rtl):focus:not(.vertical)`, `.osd spinbutton:dir(rtl):backdrop:not(.vertical)` and `.osd spinbutton:dir(rtl):disabled:not(.vertical)`. Each twin out-ranks its base group by one class, so the win does not depend on source position; placing each beside its group keeps the record together. Change nothing in the four base groups, in the grouped `.osd entry` arms, or in the landed plain mirror rule. Replace the mirror comment's last sentence ("The four .osd spinbutton state groups … the OSD family stays a future candidate.") with a pointer naming the landed twins. Above the twins, one dated (2026-11-11) adaptation comment recording: no collected reference screenshot shows a field inside a GTK OSD overlay (the standing premise the base groups' comment already records), so the etch is the landed field recipe and the mirror is this theme's adaptation because GTK 3 does not mirror `box-shadow` for direction; the four groups restate the etch at equal-or-higher specificity, so the landed plain mirror never reached an OSD RTL field (measured as in the Goal, this host, the date, a GTK 3 offscreen child); plain `entry` fields stay untouched because they have no steppers to cover the arm — the landed exclusion's reason stands for them.

2. `tests/test_gtk_theme_osd.py`: extend `test_osd_entry_fields` — its `expected` dict gains the four twin selectors each mapping to exactly `{"box-shadow": "inset -1px 1px #999999"}` and its family sweep over `self.rules` (every selector containing `.osd entry` or `.osd spinbutton` and no `" button"`) grows to include them, keeping the sweep's dropped-or-stray kill. Docstring gains one sentence naming the twins' reason. Add `test_osd_spin_field_mirrors_the_etch_in_rtl`, shaped like `tests/test_gtk_theme.py::TestGtkTheme::test_rtl_spin_field_mirrors_the_etch`: count-one and exact-declaration pins for the four twins (the `expected` extension already pins the declarations; this test pins each twin's source position directly after its base group's selector in the comment-stripped sheet, killing a misplaced twin).

3. `tests/test_gtk_theme_controls.py`: add `test_osd_spin_field_renders_the_mirrored_etch_in_rtl` directly after `test_horizontal_spinbutton_steppers_render_one_pixel_seams`, built from `_GTK3_CHILD_HEAD` and `_run_gtk_child` like that test: strip `url(...)` from the shipped sheet, install the provider, and render, in fresh `Gtk.OffscreenWindow`s, a `Gtk.SpinButton.new_with_range(0, 100, 1)` with `set_can_focus(False)` packed into a `Gtk.Box` with 5px border width whose style context carries `.osd`, once LTR and once with `set_direction(Gtk.TextDirection.RTL)`. Read the spin button's allocation and assert the Goal's measured edge columns — LTR `L+1` `#999999` ×4 and `R−1` `#000000` ×4; RTL `L+1` `#000000` ×4 and `R−1` `#999999` ×4.

4. `docs/invariants.md`: one new `## gtk` row beside the landed RTL-spin-field row (the row naming `test_rtl_spin_field_mirrors_the_etch`), naming both new tests and recording: the missing reference surface (no collected screenshot shows a GTK OSD overlay field), the provenance (the etch is the landed field recipe, the mirror is the theme's adaptation because GTK 3 does not mirror `box-shadow` for direction, and the four OSD groups restated it at higher specificity so the plain mirror never reached an OSD RTL field — measured, this host, 2026-11-11, a GTK 3 offscreen child, the shipped sheet reading `#999999`, `#FFFFFF`, `#FFFFFF`, `#FFFFFF` at RTL R−1), the entry-field exclusion with its reason, and that this resolves the landed entry's recorded OSD-family exclusion.

**Files.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `tests/test_gtk_theme_osd.py`, `tests/test_gtk_theme_controls.py`, `docs/invariants.md`.

**Acceptance criteria.**

- The GTK 3 sheet contains exactly one rule for each of the four twin selectors, each declaring exactly `box-shadow: inset -1px 1px #999999`, each placed directly after its base state group; the four base groups' declarations are unchanged, as are the landed plain mirror rule and every other `.osd` rule.
- `tests/test_gtk_theme_osd.py::test_osd_entry_fields` pins the four twins in its `expected` dict and family sweep and passes; `test_osd_spin_field_mirrors_the_etch_in_rtl` fails on a dropped twin, a stray extra spelling in the family, or a twin moved away from its base group.
- When GTK 3 introspection and a display are present, `test_osd_spin_field_renders_the_mirrored_etch_in_rtl` renders the OSD spin button reading LTR `L+1` `#999999` ×4 and `R−1` `#000000` ×4, and RTL `L+1` `#000000` ×4 and `R−1` `#999999` ×4; it fails with any twin removed or spelled `inset 1px 1px #999999` (RTL `R−1` then reads `#FFFFFF` below the top arm) and it skips with the child's own reason where GTK 3 or a display is missing.
- `docs/invariants.md` carries the new row, and `make check` passes.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::_MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
