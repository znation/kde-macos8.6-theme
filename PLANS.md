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

### Platinum GTK 3 scrolled window: stop a wrapped viewport from drawing a second frame inside the scrolled window's own (planned 2026-11-11 by the plan role; independent of every other entry. It adds one rule to the GTK 3 sheet, two tests to `tests/test_gtk_theme_controls.py` and one `## gtk` row to `docs/invariants.md`. When implementing, re-read the sheet's `frame > border, .frame` rule and its `placessidebar > viewport.frame` rule, and re-grep every anchor this entry names)

**Goal.** A GTK 3 scrolled window whose child cannot scroll itself (a `Gtk.Box`, a grid, a preferences page) wraps that child in a `Gtk.Viewport`. That viewport carries the `frame` style class, so the sheet's `frame > border, .frame` rule (`border: 1px solid #000000; box-shadow: inset 1px 1px #999999`) gives it a sunken frame of its own. The viewport draws that frame inside whatever the scrolled window draws. Measured 2026-11-11 on this host with the shipped `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: a child-interpreter `Gtk.OffscreenWindow` held a `Gtk.ScrolledWindow` (size request 30×30, both scrollbar policies `NEVER`, `add(Gtk.Box())`) packed in a `Gtk.Box` with a 5px border width. The viewport's class list was `['frame']`.
- **`set_shadow_type(Gtk.ShadowType.IN)`:** the column through the middle read `#000000`, `#000000`, `#999999` at T, T+1, T+2 and `#000000`, `#000000` at B−1, B. The row through the middle read the same at L…L+2 and R−1, R. That is a 2px black frame, where an ordinary sunken scrolled window (one holding a `Gtk.TextView`) draws 1px.
- **`set_shadow_type(Gtk.ShadowType.NONE)`:** the window asks for no frame, yet the viewport still drew a 1px black frame with a `#999999` inset (`#000000`, `#999999`, `#DDDDDD` at T…T+2; `#000000` at B).

The stock resource GTK 3 ships avoids the doubled frame: `gtk-contained.css` inside `/usr/lib/x86_64-linux-gnu/libgtk-3.so.0`, re-extracted with `gresource` 2026-11-11, declares `scrolledwindow viewport.frame { border-style: none; }`. Selecting this theme replaces that resource. The sheet restates the reset only for `placessidebar > viewport.frame`. The stock reset is not enough by itself, because the sheet adds an inset `box-shadow` that stock frames do not have. A scratch copy with only `border-style: none` fixed the IN case, but the NONE case still read `#999999` at T and L. No collected reference screenshot shows a GTK scrolled window.

**Approach.** Directly after the `frame > border, .frame` rule in the GTK 3 sheet, add this rule with a short provenance comment. The comment names the stock spelling, its extraction date, why `box-shadow` is reset as well, and the doubled-frame measurement:
- `scrolledwindow viewport.frame { border-style: none; box-shadow: none; }`

Change nothing else. The scrolled window keeps drawing its own frame. The existing `placessidebar > viewport.frame` rule stays: the new rule also clears that viewport's inset shadow, which is the intended result. A scratch copy of the sheet with exactly this rule, rendered as above, gave the following, in LTR and with `set_direction(Gtk.TextDirection.RTL)` alike:
- **IN:** the middle column read `#000000`, `#999999`, `#DDDDDD` at T…T+2 and `#DDDDDD`, `#DDDDDD`, `#000000` at B−2…B. The middle row read the same at L…L+2 and R−2…R.
- **NONE:** all six of those pixels read `#DDDDDD` in both the column and the row.

GTK 4 is out of scope: its viewports carry no `frame` class, and its probe cannot run on a host without Xvfb. The flat `Gtk.Frame` (`set_shadow_type(NONE)`, which the sheet also still draws as a full sunken frame because stock's `frame > border.flat, .frame.flat { border-style: none; }` is not restated) is a separate fix.

Tests go in `tests/test_gtk_theme_controls.py`, after `test_progressbar_fill_spans_the_trough`:
1. **Declaration test.** `test_scrolled_viewport_draws_no_frame` uses `assert_rule` to pin the rule's two declarations exactly.
2. **Pixel probe.** `test_scrolled_viewport_renders_one_frame` is built from `_GTK3_CHILD_HEAD` and runs through `_run_gtk_child`. Like `test_progressbar_fill_spans_the_trough`, it strips `url(...)`, installs the provider once and renders each case in a fresh `Gtk.OffscreenWindow`. The cases are the scrolled window above with shadow IN and with shadow NONE, each in LTR and RTL. The probe reads L, T, R and B from `scrolled.get_allocation()` and samples the middle column and middle row.

Add a `## gtk` row to `docs/invariants.md` near the entry-progress row. It names both tests and records the provenance:
- no reference screenshot shows a GTK scrolled window;
- the stock resource path and extraction date the selector spelling comes from;
- why `box-shadow` is reset too;
- the measured render: this host, the date, a GTK 3 offscreen child.

**Files.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `tests/test_gtk_theme_controls.py`, `docs/invariants.md`.

**Acceptance criteria.**

- The GTK 3 sheet contains `scrolledwindow viewport.frame`, which declares exactly `border-style: none` and `box-shadow: none`. The `frame > border, .frame` and `placessidebar > viewport.frame` rules keep their declarations.
- When GTK 3 introspection and a display are present, consider a shadow-IN scrolled window that wraps a `Gtk.Box` and is rendered with the shipped sheet. Its middle column reads `#000000`, `#999999`, `#DDDDDD` at T, T+1, T+2 and `#DDDDDD`, `#000000` at B−1, B. Its middle row reads the same at L…L+2 and R−1, R. This holds in LTR and in RTL.
- The same window with shadow NONE reads `#DDDDDD` at T, T+1, B−1, B of its middle column and at L, L+1, R−1, R of its middle row, in LTR and in RTL.
- The probe fails with the new rule removed: the shipped sheet before this change reads `#000000` at T+1 and B−1 for shadow IN. The probe also fails with only `border-style: none` kept: shadow NONE then reads `#999999` at T.
- Where GTK 3 introspection or a display is missing, the probe skips with the child's own reason, as the other GTK 3 pixel probes do. The suite process never imports `gi`, so `tests/test_no_gtk_introspection.py` still passes. `make check` passes.

### Platinum GTK 3 flat frame: draw no border or inset shadow on a `Gtk.Frame` whose shadow type is NONE (planned 2026-11-11 by the plan role; independent of every other entry. It adds one rule to the GTK 3 sheet, two tests to `tests/test_gtk_theme_controls.py` and one `## gtk` row to `docs/invariants.md`. When implementing, re-read the sheet's `frame > border, .frame` rule and any `scrolledwindow viewport.frame` rule that has landed beside it, and re-grep every anchor this entry names)

**Goal.** A GTK 3 `Gtk.Frame` set to `Gtk.ShadowType.NONE` asks for no frame: GTK gives its `border` node the `flat` style class. The sheet's `frame > border, .frame` rule (`border: 1px solid #000000; box-shadow: inset 1px 1px #999999`) still matches that node, so a flat frame draws exactly the same sunken frame as a shadow-IN one. Measured 2026-11-11 on this host with the shipped `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` (`url(...)` stripped), in a child-interpreter `Gtk.OffscreenWindow`: a label-less `Gtk.Frame()` with `set_size_request(40, 30)`, packed in a `Gtk.Box` with a 5px border width, allocation L,T,R,B = 5,5,44,34. With shadow NONE, the middle column read `#000000`, `#999999`, `#DDDDDD` at T, T+1, T+2 and `#DDDDDD`, `#DDDDDD`, `#000000` at B−2, B−1, B, and the middle row read the same at L…L+2 and R−2…R — identical to shadow IN — in LTR and with `set_direction(Gtk.TextDirection.RTL)`.

The stock resource GTK 3 ships avoids this: `gtk-contained.css` inside `/usr/lib/x86_64-linux-gnu/libgtk-3.so.0`, re-extracted with `gresource` 2026-11-11, declares `frame > border.flat, .frame.flat { border-style: none; }`. Selecting this theme replaces that resource, and the sheet does not restate the reset (`grep -n 'border\.flat\|frame\.flat'` over `theme/` finds nothing). The stock reset alone is not enough, because the sheet adds an inset `box-shadow` stock frames lack: a scratch copy with only `border-style: none` still read `#999999` at T and at L for shadow NONE. No collected reference screenshot shows a GTK frame.

**Approach.** Directly after the `frame > border, .frame` rule in the GTK 3 sheet (after the `scrolledwindow viewport.frame` rule if that waiting entry has landed there), add this rule with a short provenance comment naming the stock spelling, its extraction date, why `box-shadow` is reset too, and the measurement above:
- `frame > border.flat, .frame.flat { border-style: none; box-shadow: none; }`

Change nothing else. A scratch copy of the sheet with exactly this rule, rendered as above, gave:
- **IN:** unchanged — the middle column read `#000000`, `#999999`, `#DDDDDD` at T…T+2 and `#DDDDDD`, `#DDDDDD`, `#000000` at B−2…B; the middle row the same at L…L+2 and R−2…R; in LTR and RTL.
- **NONE:** all twelve of those pixels read `#DDDDDD`, in LTR and RTL.

GTK 4 is out of scope: `Gtk.Frame` there has no shadow type, and its probe cannot run on a host without Xvfb. The labelled frame's label gap is a separate question.

Tests go in `tests/test_gtk_theme_controls.py`, after `test_progressbar_fill_spans_the_trough` (after the scrolled-viewport tests if those have landed):
1. **Declaration test.** `test_flat_frame_draws_no_border` uses `assert_rule` to pin the rule's two declarations exactly.
2. **Pixel probe.** `test_flat_frame_renders_no_frame` is built from `_GTK3_CHILD_HEAD` and runs through `_run_gtk_child`. Like `test_progressbar_fill_spans_the_trough`, it strips `url(...)`, installs the provider once and renders each case in a fresh `Gtk.OffscreenWindow`: the frame above with shadow IN and with shadow NONE, each in LTR and RTL. It reads L, T, R and B from `frame.get_allocation()` and samples the middle column and middle row.

Add a `## gtk` row to `docs/invariants.md` beside the other GTK 3 pixel-probe rows. It names both tests and records the provenance: no reference screenshot shows a GTK frame; the stock resource path and extraction date the selector spelling comes from; why `box-shadow` is reset too; the measured render (this host, the date, a GTK 3 offscreen child).

**Files.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `tests/test_gtk_theme_controls.py`, `docs/invariants.md`.

**Acceptance criteria.**

- The GTK 3 sheet contains a rule for `frame > border.flat, .frame.flat` declaring exactly `border-style: none` and `box-shadow: none`. The `frame > border, .frame` rule keeps its declarations.
- When GTK 3 introspection and a display are present, a shadow-IN `Gtk.Frame` rendered with the shipped sheet reads `#000000`, `#999999`, `#DDDDDD` at T, T+1, T+2 and `#DDDDDD`, `#000000` at B−1, B of its middle column, and the same at L…L+2 and R−1, R of its middle row, in LTR and in RTL.
- The same frame with shadow NONE reads `#DDDDDD` at T, T+1, B−1, B of its middle column and at L, L+1, R−1, R of its middle row, in LTR and in RTL.
- The probe fails with the new rule removed (shadow NONE then reads `#000000` at T), and fails with only `border-style: none` kept (shadow NONE then reads `#999999` at T).
- Where GTK 3 introspection or a display is missing, the probe skips with the child's own reason, as the other GTK 3 pixel probes do. The suite process never imports `gi`, so `tests/test_no_gtk_introspection.py` still passes. `make check` passes.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::_MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
