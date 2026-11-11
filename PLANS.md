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

### Platinum GTK 3 horizontal spin button: draw each stepper seam as one 1px black line and pin it with an offscreen pixel probe (planned 2026-11-11 by the plan role; independent of every other entry — it adds two rules to the GTK 3 sheet, two tests to `tests/test_gtk_theme_controls.py` and one `## gtk` row to `docs/invariants.md`; at implementation re-read the sheet's `button` rule and the linked-group seam rules, and re-grep every anchor this entry names)

**Goal.** In a horizontal GTK 3 spin button, the − and + stepper buttons paint the sheet's full `button` border (`1px solid #000000`) inside the spin button's own 1px black field border. Every place where a stepper meets the frame or another stepper therefore draws a 2px black line, but Platinum draws all of these edges 1px wide. Measured 2026-11-11 on this host with the shipped `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` (child-interpreter `Gtk.OffscreenWindow`, a `Gtk.SpinButton.new_with_range(0, 100, 1)` with focus disabled, packed in a `Gtk.Box` with a 5px border width so the frame is not clipped):
- Every stepper column is `#000000` at both the spin button's top row and the row below it, and at both its bottom row and the row above it.
- The trailing edge is two black columns.
- The seam between the two steppers is two black columns.
- An RTL spin button mirrors all of this; its black columns at the row 4px below the top were x 5, 6, 35, 36, 65 and 112.

The sheet has no `spinbutton … button` rule outside `.osd` and the vertical radius pair (`grep -n 'spinbutton[^{]*button'`). The stock resource GTK 3 ships, `gtk-contained.css` inside `/usr/lib/x86_64-linux-gnu/libgtk-3.so.0`, avoids the problem by restyling these buttons: re-extracted with `gresource` 2026-11-11, it declares `spinbutton:not(.vertical) button { … border-style: none none none solid; … }` and `spinbutton:not(.vertical) button:dir(rtl) { border-style: none solid none none; }`. Selecting this theme replaces that resource, so neither rule reaches the steppers. No collected reference screenshot shows a GTK spin button. The one-seam result follows the landed linked-group scheme (`.linked:not(.vertical) > …` strips each member's trailing border so a group paints one 1px seam).

**Approach.** Add these two rules to the GTK 3 sheet directly after the vertical-stepper radius pair (`spinbutton.vertical button.up` / `spinbutton.vertical button.down`), with a short provenance comment naming the stock spelling, its extraction date and the doubled-seam measurement:
- `spinbutton:not(.vertical) button { border-style: none none none solid; }`
- `spinbutton:not(.vertical) button:dir(rtl) { border-style: none solid none none; }`

Change nothing else. The width and colour stay `1px #000000` from `button`, and the steppers keep the plain push-button face and bevel. A scratch render with exactly these two rules gave the following (spin-button allocation L,T,R,B = 5,5,110,36):
- In LTR, the row at T+4 had black columns at exactly x 5, 52, 81 and 110, and no two were adjacent.
- In RTL, the black columns were at x 5, 34, 63 and 110.
- Three columns inside each stepper, away from its seam, each stepper read `#000000` at T, `#FFFFFF` at T+1, `#DDDDDD` at T+2, `#AAAAAA` at B−1 and `#000000` at B.
- A field column still read `#000000` / `#999999` / `#FFFFFF` at T, T+1, T+2.

These rules do not reach the `.osd` stepper groups. Those groups use a full border on purpose, and their higher-specificity rules keep it. The vertical spin button is out of scope; it doubles at its field/stepper joins too, but that is a separate fix. So is GTK 4, whose probe cannot run on a host without Xvfb.

Tests go in `tests/test_gtk_theme_controls.py`, after `test_vertical_spinbutton_focus_outline`:
1. A declaration test, `test_horizontal_spinbutton_steppers_share_one_seam`, uses `assert_rule` to pin the two rules.
2. A pixel probe, `test_horizontal_spinbutton_steppers_render_one_pixel_seams`, is built from `_GTK3_CHILD_HEAD`, `_GTK3_SHEET_AND_WINDOW` and `_GTK3_PIXEL_HEAD`, runs through `_run_gtk_child`, and strips `url(...)` as `test_entry_progress_draws_a_two_pixel_strip` does. It renders the spin button above once LTR and once with `set_direction(Gtk.TextDirection.RTL)`, each in a fresh `Gtk.OffscreenWindow`. It reads the edges from `spin.get_allocation()` and finds the seams by scanning row T+4, so it does not hard-code the stepper widths.

Add a `## gtk` row to `docs/invariants.md` beside the linked-group seam row. It names both tests and records the provenance: no reference screenshot shows a GTK spin button, the stock resource path and extraction date the selector spelling comes from, and the measured render (host, date, GTK 3 offscreen child).

**Files.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `tests/test_gtk_theme_controls.py`, `docs/invariants.md`.

**Acceptance criteria.**

- The GTK 3 sheet contains `spinbutton:not(.vertical) button` declaring exactly `border-style: none none none solid`, and `spinbutton:not(.vertical) button:dir(rtl)` declaring exactly `border-style: none solid none none`. No `.osd spinbutton` rule changes.
- When GTK 3 introspection and a display are present, an LTR horizontal spin button rendered with the shipped sheet has exactly four `#000000` columns across its row T+4: its left edge L, two seams, and its right edge R. No two of them are adjacent, and the two seams lie in the trailing part of the widget, right of the field.
- Three columns into each stepper, the pixels from top to bottom read `#000000`, `#FFFFFF`, `#DDDDDD` at T, T+1, T+2 and `#AAAAAA`, `#000000` at B−1, B.
- A field column of the same LTR render still reads `#000000`, `#999999`, `#FFFFFF` at T, T+1, T+2 and `#000000` at B.
- An RTL render shows the mirror image: four non-adjacent black columns at T+4, with the two seams left of the field, and each stepper column reads the same five colours.
- With the two new rules removed, the probe fails. The shipped sheet before this change has adjacent black columns at row T+4 and reads `#000000` at T+1 of a stepper column.
- Where GTK 3 introspection or a display is missing, the probe skips with the child's own reason, as the other GTK 3 pixel probes do. The suite process never imports `gi` (`tests/test_no_gtk_introspection.py` still passes). `make check` passes.

_None yet._

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::_MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
