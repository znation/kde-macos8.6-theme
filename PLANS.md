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

### Platinum GTK 4 disabled view ink: restate the insensitive view family's grey ink over the toolkit's and the integration library's disabled view arms and co-declare it in the landed disabled-view field group, pinned by declaration tests (planned 2026-11-11 by the plan role; independent of every other entry — it amends only the landed GTK 4 disabled-view field block, adds one dated block directly after it and two tests to `tests/test_gtk4_theme.py`, and appends one end-of-table `docs/invariants.md` row; the waiting GTK 3 disabled-view entry touches only the GTK 3 sheet, `tests/test_gtk_theme.py` and `tests/test_gtk_theme_controls.py`, and the waiting OSD RTL entry only its own OSD groups and module, so no entry shares a sheet region, test name or assertion with this one and either merge order leaves all working — at implementation re-grep every anchor this entry names, since the two spin entries also extended these files)

**Goal.** An insensitive view in a GTK 4 app still paints the toolkit's own foreign ink, because the landed 2026-11-09 disabled-view field group owns only `background-color: #FFFFFF` and its comment records that "disabled ink stays owned by stock and the landed disabled-selected rules". Verified with fresh probes 2026-11-11: `gresource extract /usr/lib/x86_64-linux-gnu/libadwaita-1.so.0 /org/gnome/Adwaita/styles/base.css` (libadwaita 1.7.6, the 2622-line integration resource; one resource serves both deliveries through the theme variables, so there is no dark twin of it) declares exactly six disabled view arms carrying an ink — line 430 `calendar.view:disabled, window.print:not(.ssd-frame) calendar.dialog-action-box:disabled { color: var(--view-fg-color); }`; line 546 `columnview.view:disabled, treeview.view:disabled, window.print:not(.ssd-frame) columnview.dialog-action-box:disabled, window.print:not(.ssd-frame) treeview.dialog-action-box:disabled { color: var(--view-fg-color); }`; line 682 `treeview.view:disabled, window.print:not(.ssd-frame) treeview.dialog-action-box:disabled { color: color-mix(in srgb, var(--view-fg-color) var(--disabled-opacity), transparent); }` (the same members as 546's treeview pair, later in source, so stock's own source order already settles them dimmed); line 1222 `listview.view:disabled, window.print:not(.ssd-frame) listview.dialog-action-box:disabled, list.view:disabled, window.print:not(.ssd-frame) list.dialog-action-box:disabled { color: var(--view-fg-color); }`; line 2505 the generic six-member dimmed arm whose first five members are the landed field group's spellings and whose sixth is `iconview:disabled`; and line 2537 `flowbox.view:disabled, window.print:not(.ssd-frame) flowbox.dialog-action-box:disabled, gridview.view:disabled, window.print:not(.ssd-frame) gridview.dialog-action-box:disabled { color: var(--view-fg-color); }` — with `--disabled-opacity: 50%` fixed at base line 50, so an insensitive view paints full stock black (`--view-fg-color`, grounded `#000000` by the landed `@define-color view_fg_color`) on the calendar, column, list, flow-box and grid families and a 50%-diluted translucent black on the tree and generic arms, never the landed insensitive grey. `gresource extract /usr/lib/x86_64-linux-gnu/libgtk-4.so.1 /org/gtk/libgtk/theme/Default/Default-light.css` (libgtk-4 4.18.6, the 1940-line toolkit resource) declares the same gap for plain GTK 4 apps at line 19 `.view:disabled, iconview:disabled, textview > text:disabled { color: #929595; background-color: #faf9f8; }` and line 672 `columnview.view:disabled, treeview.view:disabled { color: #929595; }` — every member of both declarations is already in the union below minus the exclusions, so one restatement serves libadwaita and plain GTK 4 apps; the dark twin `Default-dark.css` carries the same-shaped family (probe it at implementation and quote it in the invariants row). No collected reference screenshot in `macos8.6-screenshots/` shows a disabled GTK view (the standing GTK-scope adaptation premise), so the value is platform-adapted: the ink reuses the landed insensitive grey `#888888` (`DISABLED_TEXT` in `tests/support/gtk_theme_spec.py`, re-derived from the colour scheme's `[Colors:Button] ForegroundInactive` by `assert_disabled_text`), the same grey the landed disabled-selected ink groups paint. The landed `tests/test_gtk4_theme.py::TestGtk4Theme::test_disabled_view_face` pins `selectors.count(selector) == 1` for the field group's five spellings, so the generic arm's ink cannot join as a second rule naming `.view:disabled` — it must be co-declared inside the landed field group, which the parser (`rules.setdefault` per selector in `tests/support/gtk_css.py`) merges into the same whole-dict read.

**Approach.**

1. `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: two changes (re-grep the landed anchors before writing — the landed field block sits directly before the check/radio comment that follows it). First, in the landed 2026-11-09 disabled-view comment, replace only its closing "disabled ink stays owned by stock and the landed disabled-selected rules" sentence with a dated (2026-11-11) amendment sentence recording that the group now also co-declares the generic arm's ink per-property, and add `color: #888888` as a second declaration of the landed five-spelling field group (`.view:disabled`, `textview > text:disabled`, `window.print:not(.ssd-frame) .dialog-action-box:disabled`, `dialog-host > dialog.view sheet:disabled`, `window.print:not(.ssd-frame) dialog-host > dialog.dialog-action-box sheet:disabled`), so those members answer stock's line-2505 dimmed mix too. Second, directly after that group's closing brace and before the check/radio comment, append one dated (2026-11-11) comment-and-rule: one comma group of the fourteen byte-equal members — `calendar.view:disabled`, `window.print:not(.ssd-frame) calendar.dialog-action-box:disabled`, `columnview.view:disabled`, `treeview.view:disabled`, `window.print:not(.ssd-frame) columnview.dialog-action-box:disabled`, `window.print:not(.ssd-frame) treeview.dialog-action-box:disabled`, `listview.view:disabled`, `window.print:not(.ssd-frame) listview.dialog-action-box:disabled`, `list.view:disabled`, `window.print:not(.ssd-frame) list.dialog-action-box:disabled`, `flowbox.view:disabled`, `window.print:not(.ssd-frame) flowbox.dialog-action-box:disabled`, `gridview.view:disabled`, `window.print:not(.ssd-frame) gridview.dialog-action-box:disabled` — declaring exactly `color: #888888`. The comment records: the six integration arms and the two toolkit arms with their resource lines and the foreign values elided per the palette convention (verbatim values live only in the invariants row), the missing reference surface, the value source named in the Goal, and these exclusions with reasons — the `:disabled:selected` combinations (the landed disabled-selected groups own their ink at higher specificity, and stock's own `columnview.view:disabled:selected` arm at Default-light 674 is likewise outranked); `iconview:disabled` (both generic arms carry it, but the landed field record already routed icon-view nodes to the census-backed class-only `.view:disabled` spelling, so no second spelling is added); the expander's own dimmed arm (base 698, `(0,3,1)` beats the group's treeview spelling and mixes `currentColor`, which the restated grey feeds); the `.navigation-sidebar.view:disabled` arm (base 2108) and `row.combo listview.inline:disabled` (base 1360) — transparent/inherit arms with no foreign ink literal; and the statuspage icon's opacity arm (base 1656) — an opacity-only member. No background, geometry, backdrop or other-state declaration is added: stock claims only `color` on the six per-family arms, stock carries no `:backdrop` twin on any of them, and where fills exist the landed field group and landed per-family face groups own them per-property.

2. `tests/test_gtk4_theme.py`: extend `test_disabled_view_face` — its five whole-dict assertions become `{**DISABLED_TEXT, "background-color": WHITE}` and its comment records the co-declared ink (count-one pins and token sweeps unchanged); add `test_disabled_view_family_ink` beside it: for each of the fourteen members assert `self.rules[selector] == dict(DISABLED_TEXT)` exactly and `self.selectors.count(selector) == 1`; an order pin that each member's index is greater than the landed field group's `.view:disabled` index and than the landed `columnview.view:disabled:selected` key's index; and token sweeps keyed on substrings no other landed selector carries (each view-element `:disabled` spelling and each print-dialog twin, e.g. `calendar.view:disabled`, `flowbox.view:disabled`, `list.view:disabled`, `calendar.dialog-action-box:disabled`, `gridview.dialog-action-box:disabled`), mapping to exactly the expected spelling, so a dropped member, a lost comma member, a stray extra declaration or a changed value fails.

3. `docs/invariants.md`: one appended end-of-table row naming both tests (re-grep the tail first; landed rows are appended at the file's end as the newest entries there) and recording: the missing reference surface (no collected screenshot shows a disabled GTK view); the provenance (both stock sources with the probe commands, resource paths and line numbers quoted in the Goal — integration base 430/546/682/1222/2505/2537, toolkit Default-light 19/672 — their verbatim foreign values, and the dark toolkit twin probed at implementation); the value source (the landed insensitive grey with its `ForegroundInactive` re-derivation); the co-declaration inside the landed field group and the landed count-one pin that forces it; the exclusions with their reasons; and that declaration, count and source-order checks do not establish rendered pixels (the landed child-probe harness is GTK 3 introspection only — there is no GTK 4 rendered-probe path in this repo).

**Files.** `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/test_gtk4_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**

- The GTK 4 sheet's landed disabled-view field group declares exactly `background-color: #FFFFFF` and `color: #888888`, its comment's closing sentence is replaced by the dated ink amendment, and exactly one rule carries each of the fourteen per-family members, each declaring exactly `color: #888888`, placed directly after the landed field group; the landed disabled-selected groups, the `.view, list` field group, the calendar day-number groups and every other sheet rule are unchanged.
- `tests/test_gtk4_theme.py::TestGtk4Theme::test_disabled_view_face` passes with the extended whole-dict pins and fails if the co-declared ink is dropped or spelled with a foreign value; `TestGtk4Theme::test_disabled_view_family_ink` passes and fails on a dropped member, a lost comma member, a stray extra declaration or a changed value.
- `docs/invariants.md` carries the appended row, and `make check` passes.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::_MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
