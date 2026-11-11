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

### Platinum GTK 3 vertical spin button: draw each field/stepper join as one 1px black line and pin it with an offscreen pixel probe (planned 2026-11-11 by the plan role; independent of every other entry — it extends the two landed `spinbutton.vertical button.up`/`button.down` rules in the GTK 3 sheet, extends one test in `tests/test_gtk_theme_views.py` and adds one probe to `tests/test_gtk_theme_controls.py` and one `## gtk` row to `docs/invariants.md`, sharing no sheet region, test or invariants row with the waiting flat-`Gtk.Frame` entry; at implementation re-read the landed radius record and its comment, `test_vertical_stepper_and_content_view_check_corners`, `test_horizontal_spinbutton_steppers_render_one_pixel_seams` and the horizontal-seam invariants row, and re-grep every anchor this entry names)

**Goal.** A vertical GTK 3 spin button stacks its up stepper on top, the field in the middle and the down stepper below, and each member paints its own full 1px black border, so both field/stepper joins draw adjacent 2px black lines. Measured 2026-11-11 on this host with the shipped `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` (`url(...)` stripped) in a child-interpreter `Gtk.OffscreenWindow`: a `Gtk.SpinButton.new_with_range(0, 100, 1)` with `set_orientation(Gtk.Orientation.VERTICAL)` and `set_can_focus(False)`, packed in a `Gtk.Box` with a 5px border width, allocation L,T,R,B = 5,5,36,88. The column at L+3 read `#000000` at both rows T+27 and T+28 (the up stepper's bottom border beside the field's top border) and at both rows T+55 and T+56 (the field's bottom border beside the down stepper's top border); the top and bottom edges were single. Rendered with the stock resource extracted the same day, the same widget draws exactly one 1px separator line at each join and no adjacent doubles.

The stock resource GTK 3 ships avoids the doubling by splitting the steppers' border-style: re-extracted with `gresource` on 2026-11-11, `gtk-contained.css` inside `/usr/lib/x86_64-linux-gnu/libgtk-3.so.0` declares `spinbutton.vertical button.up { … border-style: solid solid none solid; }` (resource line 532) and `spinbutton.vertical button.down { … border-style: none solid solid solid; }` (resource line 534). Selecting this theme replaces that resource, so neither half reaches the steppers — the landed radius record's comment claims these halves "stay inherited per-property", which the doubling measurement disproves on the selecting path. The landed record already restates both rules' `border-radius: 0`, and this plan extends those same two rules rather than adding new ones, because `test_vertical_stepper_and_content_view_check_corners` pins that exactly one rule in the sheet carries each of the two spellings. No collected reference screenshot shows a GTK spin button.

**Approach.** In the GTK 3 sheet, change the two landed radius rules to:
- `spinbutton.vertical button.up { border-radius: 0; border-style: solid solid none solid; }`
- `spinbutton.vertical button.down { border-radius: 0; border-style: none solid solid solid; }`

and extend the comment above them with a dated note naming the stock border-style halves being restated, their resource lines and extraction date, the doubling measurement that corrects the comment's per-property-inheritance claim, and the result: the up stepper keeps its solid head and the down keeps its solid tail, so the field's own 1px borders supply each join's single line. Change nothing else. Under the lower-sheet reading the extended declarations stay per-property ties with stock that later source order wins; under the replacing reading they now carry the halves. A scratch copy of the sheet with exactly these two extended rules rendered as above gave, in LTR and RTL alike, allocation height 82 (was 84) and:
- exactly four fully-black rows — T, T+27, T+54 and B — each a single 1px line, no adjacent pair;
- the column at L+3 read `#000000` at T, `#FFFFFF` at T+1, `#DDDDDD` at T+2, `#AAAAAA` at the row before the first join, `#000000` at the first join, `#999999` at the row after it, `#FFFFFF` at the row after that (the field's etched face), `#000000` at the second join, `#FFFFFF` at the row after it, `#DDDDDD` from the next row to two rows above B, `#AAAAAA` at B−1 and `#000000` at B.

The `.osd spinbutton.vertical button:first-child` groups declare no border-style, so the restated halves shape the OSD's stacked steppers the same way stock's own halves shape them; no OSD test pins border-style there. The landed horizontal-seam rules and the `.osd` groups are untouched. GTK 4 is out of scope: its vertical steppers use a different node tree (`spinbutton.vertical > button`) with its own landed geometry arms, and its probe cannot run on a host without Xvfb.

Tests:
1. `tests/test_gtk_theme_views.py::test_vertical_stepper_and_content_view_check_corners` — extend the two stepper dictionaries in its `assert_rule_group` call with the border-style declarations and update its docstring, which today says the two groups rest stock's end halves at zero radius only.
2. A pixel probe in `tests/test_gtk_theme_controls.py`, directly after `test_horizontal_spinbutton_steppers_render_one_pixel_seams`: `test_vertical_spinbutton_renders_one_pixel_joins`, built like that test from `_GTK3_CHILD_HEAD`, the url-stripped sheet and `_run_gtk_child`, rendering the vertical spin button above once LTR and once with `set_direction(Gtk.TextDirection.RTL)`, each in a fresh `Gtk.OffscreenWindow`. It finds the fully-black rows from the allocation and asserts the two measured results above.

Add one `## gtk` row to `docs/invariants.md` directly after the landed horizontal-spin-button seam row, naming both tests and recording: no reference screenshot shows a GTK spin button; the stock resource path, the two resource lines and the 2026-11-11 extraction date the selector spelling comes from; the doubled-join measurement that corrects the radius record's inheritance claim; and the measured render (this host, the date, a GTK 3 offscreen child). In the same change, reword the horizontal-seam row's trailing clause "the vertical spin button is unchanged" to point at the new row instead.

**Files.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `tests/test_gtk_theme_views.py`, `tests/test_gtk_theme_controls.py`, `docs/invariants.md`.

**Acceptance criteria.**

- The GTK 3 sheet's `spinbutton.vertical button.up` rule declares exactly `border-radius: 0` and `border-style: solid solid none solid`, and its `spinbutton.vertical button.down` rule declares exactly `border-radius: 0` and `border-style: none solid solid solid`. Each spelling still names exactly one rule in the sheet, and no `.osd spinbutton` rule changes.
- When GTK 3 introspection and a display are present, a vertical spin button rendered with the shipped sheet paints exactly four fully-black single-row lines across its allocation — its top edge, the field/stepper join, the two-steppers' join and its bottom edge — with no adjacent black pair, in LTR and in RTL.
- The up stepper's column keeps the raised button pattern `#000000`, `#FFFFFF`, `#DDDDDD` at its head rows and `#AAAAAA` above its removed bottom border; the field column keeps `#000000`, `#999999`, `#FFFFFF` after its top border; the down stepper keeps `#FFFFFF`, `#DDDDDD` at its head rows after its removed top border and `#AAAAAA`, `#000000` at its bottom edge. All hold in LTR and RTL.
- The probe fails with the extended declarations removed: the shipped sheet before this change paints two adjacent fully-black rows at each join, and the render is two rows taller.
- Where GTK 3 introspection or a display is missing, the probe skips with the child's own reason, as the other GTK 3 pixel probes do. The suite process never imports `gi`, so `tests/test_no_gtk_introspection.py` still passes. `make check` passes.

### Platinum GTK 3 spin field in RTL: mirror the etch's inset arm to the field's exposed edge and pin it in the seam probe (planned 2026-11-11 by the plan role; independent of every other entry — it adds one rule to the GTK 3 sheet directly after the landed `entry, spinbutton:not(.vertical)` rule, one declaration test to `tests/test_gtk_theme.py`, extends the landed probe `test_horizontal_spinbutton_steppers_render_one_pixel_seams` in `tests/test_gtk_theme_controls.py` and adds one `## gtk` row to `docs/invariants.md`, sharing no sheet region, test or invariants row with the waiting flat-`Gtk.Frame` entry or the queued vertical-spin-button entry; at implementation re-read the landed field rule and the horizontal-seam record and its probe, and re-grep every anchor this entry names)

**Goal.** The landed field rule `entry, spinbutton:not(.vertical)` etches the spin field with `box-shadow: inset 1px 1px #999999`, and GTK 3 does not mirror `box-shadow` for right-to-left text direction. In a horizontal RTL spin button the steppers therefore overlay the entry node's left edge and cover the etch's vertical arm, so the exposed field draws only the horizontal top arm — a half-etched field, where the LTR field shows the full L. Measured 2026-11-11 on this host with the shipped `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` (`url(...)` stripped) in a child-interpreter `Gtk.OffscreenWindow`: a `Gtk.SpinButton.new_with_range(0, 100, 1)` with focus disabled, packed in a `Gtk.Box` with a 5px border width, allocation L,T,R,B = 5,5,110,36, its four black columns at L, 52, 81, R in LTR and at L, 34, 63, R in RTL (the steppers sit left of the field in RTL). The column at L+1 read `#999999` at T+1, T+2, T+3 and B−1 in LTR; in RTL the same column read `#FFFFFF` at T+1…T+3 and `#AAAAAA` at B−1 (the steppers' face over the arm), and the exposed field's other edge read `#999999` at T+1 only, then `#FFFFFF` — no vertical arm at either exposed edge. That GTK 3 keeps the arm at the covered left column rather than mirroring it is itself measured: if the toolkit mirrored `box-shadow`, the RTL column at R−1 would read `#999999` below T+1 and it reads `#FFFFFF` in the shipped sheet. No collected reference screenshot shows a GTK spin button in any direction (the standing GTK-scope adaptation premise); the etch is the theme's own landed recipe, and mirroring it keeps the RTL field's sunken L at its exposed outer edge, the same corner the LTR field's L sits at.

**Approach.** In the GTK 3 sheet, directly after the `entry, spinbutton:not(.vertical)` rule, add this rule with a short dated comment naming the landed etch it mirrors, the measured covered-arm defect above, GTK 3's non-mirrored `box-shadow`, and the mirrored result:
- `spinbutton:dir(rtl):not(.vertical) { box-shadow: inset -1px 1px #999999; }`

The mirror out-specifies the base rule per-property (two pseudo-classes against one), so it wins the plain RTL field's `box-shadow` at any source position; placing it beside the base rule keeps the record together. Change nothing else. A scratch copy of the sheet with exactly this rule at exactly that position, rendered as above, gave:
- **LTR:** unchanged — the column at L+1 read `#999999` at T+1, T+2, T+3, B−1 and the column at R−1 `#AAAAAA` at those rows; the four black columns stayed at L, 52, 81, R.
- **RTL:** the column at R−1 read `#999999` at T+1, T+2, T+3 and B−1 (was `#999999` at T+1 only); the column at L+1 kept the steppers' `#FFFFFF`, `#FFFFFF`, `#FFFFFF`, `#AAAAAA`; the four black columns stayed at L, 34, 63, R.

Exclusions with reasons, recorded in the comment and the invariants row: the four `.osd spinbutton:not(.vertical)` state groups restate the etch at equal-or-higher specificity, so their RTL fields keep the covered arm; giving them `:dir(rtl)` twins would multiply the overlay-scoped OSD record across its four states, so the OSD family is this entry's own future candidate, not part of it. Plain `entry` fields are untouched — the plan measures only the spin field, whose overlay is the defect. The rule carries `:not(.vertical)`, so vertical spin fields cannot match it. GTK 4 is out of scope: its spin button uses a different node tree and its probe cannot run on a host without Xvfb.

**Tests.**
1. `tests/test_gtk_theme.py::TestGtkTheme::test_rtl_spin_field_mirrors_the_etch`, shaped like `test_rtl_collapsed_expander_arrows`: `assert_rule` pins the mirror's single declaration exactly, and `self.selectors.count("spinbutton:dir(rtl):not(.vertical)")` equals exactly 1.
2. Extend `test_horizontal_spinbutton_steppers_render_one_pixel_seams` in `tests/test_gtk_theme_controls.py`: inside its LTR/RTL loop, after the seam assertions, read the columns at L+1 and R−1 at rows T+1, T+2, T+3 and B−1 and assert the two measured column results above — this fails on the shipped sheet (RTL R−1 reads `#FFFFFF` at T+2 and B−1) and on a mirror added to the wrong side (RTL L+1 would then read `#999999`).

Add one `## gtk` row to `docs/invariants.md` beside the horizontal-spin-button seam row, naming both tests and recording: no reference screenshot shows a GTK spin button; the etch is the landed field recipe and the mirror is this theme's adaptation because GTK 3 does not mirror `box-shadow` for RTL; the covered-arm measurement and the mirrored render (this host, the date, a GTK 3 offscreen child); and the OSD exclusion with its reason.

**Files.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `tests/test_gtk_theme.py`, `tests/test_gtk_theme_controls.py`, `docs/invariants.md`.

**Acceptance criteria.**

- The GTK 3 sheet contains exactly one `spinbutton:dir(rtl):not(.vertical)` rule, placed directly after the `entry, spinbutton:not(.vertical)` rule, declaring exactly `box-shadow: inset -1px 1px #999999`; the base rule's declarations are unchanged and no `.osd spinbutton` rule changes.
- When GTK 3 introspection and a display are present, a horizontal spin button rendered with the shipped sheet reads, at rows T+1, T+2, T+3 and B−1: column L+1 `#999999` at all four rows and column R−1 `#AAAAAA` at all four rows in LTR; column R−1 `#999999` at all four rows and column L+1 `#FFFFFF`, `#FFFFFF`, `#FFFFFF`, `#AAAAAA` in RTL. The four fully-black columns stay one per edge with two non-adjacent seams in both directions, and the allocation is unchanged.
- The probe fails with the new rule removed (RTL R−1 then reads `#FFFFFF` at T+2 and B−1) and with the mirror spelled `inset 1px 1px #999999` (RTL R−1 then reads `#FFFFFF` at T+2).
- Where GTK 3 introspection or a display is missing, the probe skips with the child's own reason, as the other GTK 3 pixel probes do. The suite process never imports `gi`, so `tests/test_no_gtk_introspection.py` still passes. `make check` passes.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::_MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
