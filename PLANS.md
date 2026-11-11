# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned
_None yet._


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

### Platinum GTK 4 spin field in RTL: mirror the etch's inset arm to the field's exposed edge in the plain and .osd state groups, pinned by declaration tests and the landed child-interpreter probe shape (planned 2026-11-11 by the plan role; independent of the waiting GTK 4 disabled-view ink entry — that entry amends only the landed disabled-view field block at the sheet tail, extends `test_disabled_view_face` and adds `test_disabled_view_family_ink` in `tests/test_gtk4_theme.py`, and appends its own end-of-table `docs/invariants.md` row, while this entry adds rules directly after the landed `entry, spinbutton:not(.vertical), spinbutton.vertical > text` field rule and the three landed `.osd` field groups, adds two new tests beside `test_osd_entry_fields` in `tests/test_gtk4_theme.py` and appends its own row, so no entry shares a sheet region, test name or assertion and either merge order leaves all working — at implementation re-grep every anchor this entry names, since the waiting entry also edits the same two files)

**Goal.** The landed 2026-10-29 entry recipe paints every GTK 4 field with `box-shadow: inset 1px 1px #999999` — the `entry, spinbutton:not(.vertical), spinbutton.vertical > text` rule and, inside an OSD overlay, the landed 2026-11-03 `.osd` restate's three state groups (`.osd spinbutton.vertical > text, .osd spinbutton:not(.vertical), .osd entry` and its `:focus-within` and `:disabled` twins). GTK 4, like GTK 3, does not mirror `box-shadow` for text direction, so in a right-to-left horizontal spin button the steppers sit at the field's left edge — the landed sheet's own `:dir(rtl)` stepper arms (`spinbutton:not(.vertical) > button.image-button.up:not(.flat):dir(rtl)` and its `:dir(rtl):first-child` corner twins, plus the `row.spin` twins) move both buttons there — covering the etch's vertical arm at that edge, so the exposed right edge keeps only the horizontal top arm: a half-etched field where the LTR field shows the full L. The landed GTK 3 sheet already carries the fix for its own sheet (the `spinbutton:dir(rtl):not(.vertical)` mirror and the four `.osd spinbutton:dir(rtl)` state twins, measured 2026-11-11 in a GTK 3 offscreen child and recorded beside the plain field rule); a fresh grep this run finds no `spinbutton:dir(rtl)` `box-shadow` arm anywhere in `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, so the GTK 4 field keeps the half-etched defect. No collected reference screenshot shows a GTK spin field in either direction (the standing GTK-scope adaptation premise), so the fix restates the landed recipe's own grey, introducing no palette value.

**Approach.**

1. `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: before writing, re-read the landed field rule and the three `.osd` groups and measure first — run the probe below's child program before the edit and record in the dated comment that the shipped sheet's RTL field exposed right edge lacks the etch arm on this host and date. Then, directly after the landed `entry, spinbutton:not(.vertical), spinbutton.vertical > text` rule, add one dated (2026-11-11) comment-and-rule `spinbutton:dir(rtl):not(.vertical) { box-shadow: inset -1px 1px #999999; }`, and directly after each of the three landed `.osd` state groups its twin — `.osd spinbutton:dir(rtl):not(.vertical)`, `.osd spinbutton:dir(rtl):focus-within:not(.vertical)` and `.osd spinbutton:dir(rtl):disabled:not(.vertical)` — each declaring exactly `box-shadow: inset -1px 1px #999999`. Each mirror out-ranks its base group by one class (`:dir(rtl)`), so the win does not depend on source position. The dated comment records the mechanism (GTK does not mirror box-shadow for direction; the steppers cover the etch's vertical arm at the RTL field's left edge, measured before the edit), the landed GTK 3 mirror it follows, and the exclusions with their reasons: vertical `spinbutton.vertical > text` fields (no horizontal stepper covers the arm — the landed GTK 3 exclusion's reason stands), plain `entry` fields (no steppers, the landed GTK 3 plain-entry exclusion), and the treeview-embedded entry group (an `entry`, not a spin field). No background, border, radius, colour or other declaration is added, and the `.osd` record declares no `:backdrop` field twin, so none is mirrored.

2. `tests/test_gtk4_theme.py`: first re-grep `test_flat_entry_fields` and `test_osd_entry_fields` for any count or token-sweep pin the four new selectors would break, then add `test_spin_field_mirrors_the_etch_in_rtl` beside `test_osd_entry_fields`: for each of the four mirror selectors assert `self.rules[selector] == {"box-shadow": "inset -1px 1px #999999"}` exactly and `self.selectors.count(selector) == 1`; an order pin that each mirror's index is greater than its base group's index (`spinbutton:dir(rtl):not(.vertical)` after the landed `spinbutton:not(.vertical),`-carrying plain field key, each `.osd spinbutton:dir(rtl)` after its `.osd` state group); and token sweeps keyed on substrings no other landed selector carries (`spinbutton:dir(rtl):not(.vertical)`, `.osd spinbutton:dir(rtl):focus-within:not(.vertical)`, `.osd spinbutton:dir(rtl):disabled:not(.vertical)`), mapping to exactly the expected spelling, so a dropped mirror, a lost twin, a stray extra declaration or a changed value fails.

3. `tests/test_gtk4_theme.py`, probe: add `test_spin_field_renders_the_mirrored_etch_in_rtl` beside the landed probes, the same shape as `test_mixed_indicators_draw_black_dashes`: `require_gui_opt_in()` first, then a child interpreter subprocess with `GDK_BACKEND=x11` and `GSK_RENDERER=cairo`, exit 77 mapped to a skip naming what is missing; the child loads the shipped sheet bytes with the same `../assets/` URL rewrite at provider priority 801, builds a `Gtk.SpinButton` with an adjustment in a `Gtk.Window` (wide enough that no digit glyph reaches the pinned pixels), calls `set_direction(Gtk.TextDirection.RTL)` on the spin button, presents, finds the spin field node (guarded by `get_css_name() == "spinbutton"`), settles by frame and snapshots it with `Gtk.WidgetPaintable.new(...)` through `renderer.render_texture` into a pixbuf with the landed deadline loop, then asserts each pinned pixel as a literal tuple. A second window in the same child wraps an identical RTL spin button in an ancestor box carrying the `osd` class so the landed `.osd spinbutton …` descendant groups match, and captures it the same way. The pinned positions are measured at implementation on this host from a fresh child render, the plan states no coordinates, and every position is clear of glyph rows, the field border's edge ratio and the stepper buttons' interior: on the plain capture, one interior pixel at the field's exposed right edge expecting the mirrored `#999999` vertical arm (dropping the mirror turns it field-white), one pixel on the top border row expecting `#000000`, and one interior pixel at the covered left edge under a stepper expecting the stepper button's `#FFFFFF` bevel arm rather than the etch grey; on the `.osd` capture, the same exposed-edge pixel expecting `#999999` — so any of a dropped mirror, a foreign value, a mirror that loses its specificity race or an unmirrored `.osd` state changes at least one pinned pixel.

4. `docs/invariants.md`: append one dated (2026-11-11) end-of-table `## gtk` row naming both tests, re-grepping the tail first since landed rows are appended there, and recording: the missing reference surface (no collected screenshot shows a GTK spin field in either direction); the value source (the landed entry recipe's own etch grey, mirrored from the landed GTK 3 `spinbutton:dir(rtl)` record); the specificity shape (each mirror out-ranks its base group by one class); the exclusions and reasons; and that the probe establishes rendered pixels only under the opt-in guard where GTK 4 introspection and an X display are present, as declaration checks never have.

**Files.** `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/test_gtk4_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**

- The GTK 4 sheet declares exactly the four mirror rules, each with exactly `box-shadow: inset -1px 1px #999999`, each placed directly after its base group with its dated comment; the landed field rule, the three `.osd` groups, the stepper arms and every other sheet rule are unchanged.
- `tests/test_gtk4_theme.py::TestGtk4Theme::test_spin_field_mirrors_the_etch_in_rtl` passes and fails on a dropped mirror, a foreign value, a lost placement or a stray extra declaration; `test_flat_entry_fields` and `test_osd_entry_fields` pass unchanged.
- Without `PLATINUM_RUN_GUI_TESTS=1` the probe raises the landed opt-in skip, and where GTK 4 introspection or a display is missing despite the opt-in it skips with its own reason; where both are present the child completes and its pinned pixels read the literal tuples, so deleting any one of the four mirrors — or spelling one with the LTR arm `inset 1px 1px #999999` — changes at least one pinned pixel and fails.
- `docs/invariants.md` carries the appended row, and `make check` passes after the final edit.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::_MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
