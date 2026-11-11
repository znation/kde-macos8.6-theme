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
2026-10-29 by the steward role; landed-series narration trimmed 2026-11-11 by the
steward role):** The
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

Two answers on 2026-10-19 widened the scope, and both are recorded below in their landed
state (their landed-series entry narration trimmed 2026-11-11 by the steward role;
the entries themselves are archived in PLANS-DONE.md).
**GTK applications and Firefox** are in scope (QUESTIONS.md, answered 2026-10-19): the GTK 3
and GTK 4/libadwaita Platinum stylesheets under `theme/gtk/` are installed — and selected —
only by the opt-in `install-gtk` and `apply-gtk` targets (`make install` copies no GTK
files), and the opt-in `install-firefox` target copies the Firefox `userChrome.css` and
`userContent.css` sheets into a profile and writes the preference that selects them.
**The UI font** is vendored (QUESTIONS.md, answered 2026-10-19): Lato is installed as the
Charcoal-style body face and selected by the global theme for the general, menu, toolbar,
smallest-readable and window-title fonts, and monospaced text keeps the user's fixed font;
a Chicago-style menu face (part 2/3 of the font series) remains unplanned because its
redistribution licence is unresolved, and Lato is the only family the package installs.
GTK and Firefox applications keep their own chrome unless the opt-in GTK targets or the
Firefox install are used. Firefox chrome work since that series landed as single-surface
chrome plans (the downloads-panel and all-tabs rows, the sidebar frame, the menu-bar title
box, the tab faces and the app-menu rows). The `userContent.css` sheet styles surfaces
within six internal pages — about:downloads, about:config, about:preferences,
about:support, about:networking and about:telemetry — including preferences navigation and
controls, support tables and buttons, and telemetry navigation, tables and histograms; this
is surface coverage, not a claim of complete page theming. This content work extends the
2026-10-19 "style Firefox" answer rather than the brief's KDE/Plasma desktop UI, so it is
recorded here to keep the scope deliberate.

### Platinum cursor set: ship the side-edge and corner resize roles as byte-identical aliases of the landed resize glyphs (planned 2026-11-11 by the plan role; independent of the waiting desktop render part 1/2 — that entry edits the render plumbing (`tools/render_surface.py`, `tools/render_workflow.py`, `tools/render_setup.py`, the `Makefile`, the render test suites and README's render prose), while this entry edits only `tools/cursor_art.py`, the regenerated `theme/icons/org.macos8.desktop/cursors/` files, `tests/test_cursors_theme.py`, README's pointer-set paragraph and the `## icons` cursor row of `docs/invariants.md`, so the two share no file, test or anchor and either merge order leaves both working; at implementation re-grep every anchor this entry names)

**Goal and grounding.** Close the shipped pointer set's visible Xcursor leak: the package carries no file for the eight resize roles an Xcursor client names when a pointer drags or resizes a window edge or corner — `top_side`, `bottom_side`, `left_side`, `right_side`, `top_left_corner`, `top_right_corner`, `bottom_left_corner` and `bottom_right_corner` — so GTK CSD windows and X11 resize handles draw those eight pointers from the fallback theme (Breeze, here and on the hosted CI image; the Breeze set ships each name as its own art file, distinct from its `size_*` glyphs, byte-compare confirmed on this host 2026-11-11). README's pointer-set paragraph already records the limitation ("Xcursor roles the theme does not name still come from the fallback cursor theme"). No new art is needed: the set's alias policy (the `## icons` cursor row's provenance cell records alias grouping as "this theme's own choice") lets each new role ship as a byte-identical copy of the landed resize glyph whose axis it spans. A future set of single-direction arrows for these roles is a separate art candidate and stays out; so does `right_ptr` (no reference screenshot shows a right-pointing arrow and a mirrored glyph is a new-art decision; Breeze supplies it only in RTL locales today).

**Approach.**

1. `tools/cursor_art.py`: extend four `CURSORS` alias tuples with no change to any canonical name, grid or hotspot — `size_ver` gains `"top_side"` and `"bottom_side"`, `size_hor` gains `"left_side"` and `"right_side"`, `size_fdiag` gains `"top_left_corner"` and `"bottom_right_corner"`, and `size_bdiag` gains `"top_right_corner"` and `"bottom_left_corner"`. Add one dated (2026-11-11) comment above the tuple recording the grounding: no reference screenshot shows a cursor, X draws single-direction arrows for the side and corner roles, and reusing the landed double-arrow resize art for each role keeps the set's one-face-set policy with the alias grouping again the theme's own choice.
2. Regenerate the committed artifacts with `python3 tools/make_cursors.py` from the repository root (its output is deterministic; re-running rewrites identical bytes), which writes the eight new alias files as byte-identical copies of their canonical glyph at all three nominal sizes and rewrites nothing else.
3. `tests/test_cursors_theme.py`: extend the module-level `ALIASES` map (the four resize canonicals' tuples each gain their two new names) and the `CURSOR_FILES` tuple (eight new names) beside the existing entries — the whole-set tests (`test_every_alias_is_byte_identical_to_its_canonical`, `test_every_committed_cursor_is_a_fresh_generator_result`, `test_generator_writes_every_file_deterministically_in_a_temp_directory`) then cover the new roles without weakening any existing pin. Add nothing to `PINNED_PIXELS`, `HOTSPOTS`, `CANONICAL` or `TRANSPARENT_CORNER_CURSORS`: no new canonical art exists.
4. README's pointer-set paragraph (the `## Installing` section's `make apply-cursor` prose): append the eight new alias names into their four alias groups and keep the trailing fallback-theme limitation sentence — it stays true for the roles the set still does not name (`right_ptr`, `sizing`, `center_ptr`, the single-direction future candidate).
5. `docs/invariants.md`: extend the `## icons` cursor row's alias enumeration with the eight new names and add one provenance sentence recording the grouping choice and the checked Breeze distinctness (each new role is its own art file in the installed Breeze set, byte-compare 2026-11-11, so the alias reuse is the theme's own adaptation, not a Breeze byte-group follow).

**Files.** `tools/cursor_art.py`, `theme/icons/org.macos8.desktop/cursors/` (eight new files, regenerated), `tests/test_cursors_theme.py`, `README.md` (one paragraph), `docs/invariants.md` (one row extended). No generator change (`tools/make_cursors.py` derives from `CURSORS`), no install/apply change (`make apply-cursor` links the whole `cursors/` directory), no `index.theme` change, and no file touched by the waiting desktop render part 1/2.

**Acceptance criteria.**

- After `python3 tools/make_cursors.py`, `theme/icons/org.macos8.desktop/cursors/` holds exactly eight additional files, and each is byte-identical (`cmp`) to its canonical: `top_side` and `bottom_side` to `size_ver`, `left_side` and `right_side` to `size_hor`, `top_left_corner` and `bottom_right_corner` to `size_fdiag`, `top_right_corner` and `bottom_left_corner` to `size_bdiag`; the directory holds no other new name and every pre-existing file keeps its bytes.
- A user who selects the pointer set (`make apply-cursor`) sees the Platinum resize arrows, not the fallback theme's, at every window edge and corner a GTK CSD or X11 resize handle draws — the eight Xcursor names now resolve inside `$HOME/.icons/org.macos8.desktop/cursors/`.
- `tests/test_cursors_theme.py`'s alias sweep names exactly the eight new spellings and fails on a missing alias file, an alias diverging from its canonical, or a regenerated canonical that changed; `make check` passes after the final edit.

## Done

### Fidelity CLI: extract parser construction from comparison orchestration (planned 2026-11-02 by the plan role) — done 2026-11-11 by the feature role

**Goal and grounding.** Make the fidelity entry point readable as a comparison workflow. `tools/fidelity.py::main` currently starts with parser construction and a nested `worst_pixel_limit` validator before it reads images. `tools/fidelity_arguments.py` already owns the other argument validators. The finished report-extraction plan deliberately retained parser setup in the entry point; heading searches found no separate parser-extraction plan. This maintenance task is independent of the queued sampler work.

**Approach and files.** Create `tools/fidelity_cli_parser.py::build_parser`, moving the existing `EscapingArgumentParser` construction and option declarations there without changing their order, help strings, defaults, destinations or types. Move `worst_pixel_limit` to `tools/fidelity_arguments.py` and import the validators into the new parser module. In `tools/fidelity.py::main`, replace the construction block with `build_parser().parse_args(argv)` and remove imports made unused by the move. Support package imports and direct-script execution using the existing conditional import pattern. Keep image reads, crop application, optional diagnostic scans and reporting in their current owners. Inspect repository references to validators imported through `tools.fidelity` before removing those imports; preserve an existing consumer's import path if needed. Bound the change to those three production files and a new `tests/test_fidelity_cli_parser.py`; adjust ownership docstrings in the touched files. No CLI behavior change or new dependency is intended.

**Acceptance criteria.** Before moving declarations, capture characterization fixtures in the new test module for normalized help text and parsed default/explicit namespaces, including both crops, diagnostic switches and combined budgets. The same fixtures pass after extraction. Use the existing unittest framework to verify two independently constructed parsers work, malformed crop/budget/worst-pixel arguments retain status 2 and escaped diagnostics, and help and invalid arguments do not call `tools/fidelity.py::_read_source`. Existing fidelity CLI, JSON, crop and direct-script tests continue to pass. Run `make check` after final edits. This structural change adds no guarantee to docs/invariants.md; its existing tooling contracts remain the acceptance boundary.

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::_MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
