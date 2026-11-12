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


### Antialiased text and hand cursors: draw the I-beam and pointing hand as vector art (planned 2026-11-12 by the plan role; "requires Antialiased cursors part 3/3 landed")

**Goal.** This is the next cursor family the BUGS.md cursor report routes: the text I-beam (`xterm`, aliases `text` and `ibeam`) and the pointing hand (`hand2`, aliases `hand1`, `pointer` and `pointing_hand`). They are the cursors users see most after the arrow. Redraw both as smooth, original, antialiased vector art, rendered natively at 16, 24 and 32 through the `VectorCursor` path that part 2/3 adds to `tools/make_cursors.py`. This entry adds no generator change.

**Approach.**
- **Art.** In `tools/cursor_art_pointers.py`, replace `XTERM_GRID` and `HAND2_GRID` with `XTERM_ART` and `HAND2_ART`. Both are `VectorCursor(face=…, outline_width=2, design_size=32)`. Set `XTERM_HOTSPOT = (15, 15)` and `HAND2_HOTSPOT = (14, 4)` in design units. Delete the two grids: they are bound only in `tools/cursor_art.py` (checked with grep), and no other grid reuses their cells. Rewrite their comments. These polygons are the design decision, listed in order:
  - I-beam: `(10,4) (20,4) (20,6) (16,6) (16,26) (20,26) (20,28) (10,28) (10,26) (14,26) (14,6) (10,6)`. The stem is 2 units wide, with serifs 10 units wide, and the shape is symmetric about x=15. The stem edges fall on pixel boundaries at 16 and 32, so it stays crisp there.
  - Hand: `(13,3) (15,3) (16,5) (16,12) (17,11) (19,11) (20,12) (21,11.5) (23,12) (24,14) (24,24) (21,28) (12,28) (9,25) (9,21) (6.5,17) (6.5,15.5) (8,14.5) (12,17) (12,5)`. This is a raised index finger 4 units wide, with knuckle bumps along the palm top, a thumb on the left and a rounded heel. The implementer may move a vertex by at most 1 unit, and only to satisfy a criterion below.
- **Binding.** In `tools/cursor_art.py`, import the two `*_ART` constants and bind `xterm` and `hand2` to them with the same aliases. Update the module docstring to say these two are also antialiased vector art.
- **Regenerate** with `python3 tools/make_cursors.py`.
- **Tests.**
  - `tests/test_cursors_theme.py`:
    - Update `HOTSPOTS` for both cursors to the values below.
    - Move `xterm` and `hand2` out of the grid-cell `PINNED_PIXELS` check into the per-size vector pins below. Use the same mechanism part 3/3 uses for `left_ptr`; if part 3/3 kept `left_ptr` in `PINNED_PIXELS` some other way, follow that shape.
    - In every `cursor_art.CURSORS`-wide test, treat both entries the same way part 3/3 treats the `left_ptr` vector entry: the corrupted-glyph variant, the shield-grid check and the differs-from-arrow check.
    - Add one test per cursor for the criteria below.
  - `tests/test_cursor_art_bindings.py`: the two `*_ART` constants pair with their `*_HOTSPOT` constants, under the rule part 3/3 added.
  - `docs/invariants.md`: update the cursor-set row and the hotspot row so they list `xterm` and `hand2` as vector-rendered.

**Files.** `tools/cursor_art_pointers.py`, `tools/cursor_art.py`, `tests/test_cursors_theme.py`, `tests/test_cursor_art_bindings.py`, `docs/invariants.md`, and the seven regenerated files `xterm`, `text`, `ibeam`, `hand2`, `hand1`, `pointer` and `pointing_hand` under `theme/icons/org.macos8.desktop/cursors/`.

**Acceptance criteria.** The values below are measured from the planned polygons with `tools/cursor_vector.py` on main. Tests derive their expectations from the design coordinates, not from the rendered output.
- **xterm.** The committed `xterm` parses to frames at 16, 24 and 32 with hotspots `(7,7)`, `(11,11)` and `(15,15)`. In each frame:
  - The hotspot pixel and the pixel containing design point `(15,15)` are `(0,0,0,255)`.
  - The pixel containing design point `(17,15)` is `(255,255,255,255)`: that is `(8,7)`, `(12,11)` and `(17,15)`.
  - All four corners are `(0,0,0,0)`.
  - At least one pixel has alpha strictly between 0 and 255.
  - The 24-pixel frame also has an opaque pixel with a channel strictly between 0 and 255, where the stem edge falls inside a pixel.
- **hand2.** The committed `hand2` parses to frames at 16, 24 and 32 with hotspots `(7,2)`, `(10,3)` and `(14,4)`. In each frame:
  - The hotspot pixel has alpha 255.
  - The pixel containing design point `(14,8)` (the finger) is `(0,0,0,255)`.
  - The pixel containing design point `(17,7)` (the outline beside the finger) is `(255,255,255,255)`.
  - All four corners are `(0,0,0,0)`.
  - At least one pixel has alpha strictly between 0 and 255, and at least one opaque pixel has a channel strictly between 0 and 255.
- **Freshness and aliases.** Each committed canonical file equals `make_cursors.cursor_bytes` for its entry, and each alias is byte-identical to its canonical file. A moved face vertex, a dropped size or a moved hotspot each change the bytes.
- **Scope.** `git diff --stat` touches no cursor file outside the seven listed above.
- `make check` passes after the final edit. This change does not close the BUGS.md cursor report. The remaining families are watch; help, progress and context-menu; resize, fleur and crosshair; and drag, grab and not-allowed. Each will get its own entry.

### README split, part 1/5: let the README tests follow links into docs/ guides (planned 2026-11-12 by the director role)

**Goal.** On 2026-11-12 the user asked to shorten README.md (1,934 lines) by moving its longest sections into separate markdown files and linking to them. Parts 2/5–5/5 each move one section into a `docs/<topic>.md` guide. About a dozen tests read README.md text and would fail or quietly lose coverage once that text moves. This part adds the shared reader those parts retarget to, and it extends the link checker across files. It moves no prose.

**Approach.**
- New `tests/support/user_docs.py`:
  - `linked_guides(readme_text) -> list[str]` returns the repo-relative `docs/*.md` paths that README's inline links point at (`](docs/<name>.md)` or `](docs/<name>.md#frag)`, outside fenced code), deduplicated, in first-seen order.
  - `read_user_docs() -> str` returns README.md's text followed by each linked guide's text, joined with `"\n\n"`. Every read goes through `containment.read_text(path, ROOT, encoding="utf-8")`, the same guard the README readers use.
  - The corpus is whatever README links to, so a guide joins it when README links it. A guide that README does not link is not user documentation. README links neither `docs/invariants.md` nor `docs/principles-rationale.md` today, so they stay out.
- `tests/test_readme_links.py`:
  - Keep `local_link_errors` for same-document `(#frag)` links. Run it on README and on each linked guide.
  - Add `cross_file_link_errors(source_path, text)`. It resolves `](<relpath>.md#frag)` and `](<relpath>.md)` targets relative to the source file and returns a target in either of two cases: the file does not exist, or the fragment matches no heading slug or explicit anchor in that file. Reuse the existing `_slug`/heading/anchor logic: refactor its destination collection into a helper that both functions call, without changing current results. Ignore links with a URL scheme.
  - Apply it to README → guide links and to guide → `../README.md#frag` links.
- `docs/invariants.md`: update the `tests/test_readme_links.py::TestReadmeLinks` row. It now says "no network or cross-file validation"; make it describe the cross-file check over README and its linked guides.

**Files.** `tests/support/user_docs.py` (new), `tests/test_readme_links.py`, a new `tests/test_user_docs.py` (or new cases in `tests/test_readme_links.py`), `docs/invariants.md`.

**Acceptance criteria.**
- In unit tests on temporary files, `linked_guides` returns `docs/a.md` once for text that links `docs/a.md` twice and `docs/a.md#x` once. It ignores a link inside a fenced code block and a link to `https://example.com/docs/b.md`.
- `cross_file_link_errors` reports a link to a missing file, and a link whose fragment matches no heading in an existing file. It reports nothing for a link whose fragment matches a heading slug.
- `read_user_docs()` on the current tree equals README.md's text, because README links no guide yet. A symlinked guide that escapes the repository is refused, like the existing README containment tests.
- README.md is unchanged. `make check` passes after the final edit.

### README split, part 2/5: move "Installation details" into docs/installing.md (planned 2026-11-12 by the director role; "requires part 1/5 landed")

**Goal.** Move README's `### Installation details` subsection, the longest in the file (about 430 lines, with paragraphs that are a single very long line), into a new `docs/installing.md`. README keeps `### Quick start`, `### Staging packages`, `### Removing the theme` and `#### Restoring personal GTK 4 CSS`.

**Approach.**
- Cut the whole `### Installation details` subsection, from its heading up to `### Rendering a candidate`, and paste it verbatim into `docs/installing.md`. The new file starts with a `# Installation details` H1 and a one-line back link to `../README.md#installing`, then promotes the moved headings one level. Copy the prose and code exactly; shortening it is not this part's job.
- In README, put a short `### Installation details` stub in the subsection's place. It has two to four lines saying what the guide covers (which files each package installs, what `make apply` changes, GTK/Firefox/cursor selection details) and a link to `docs/installing.md`.
- Repoint every link into the moved text: README `(#frag)` links (including the Prerequisites table's "See [Installing](#installing)" links, wherever the detail now lives) become `docs/installing.md#frag`, and links in the moved text back to sections still in README become `../README.md#frag`. Part 1/5's link test checks both directions.
- Retarget the tests whose README text moved so they read `user_docs.read_user_docs()` instead of README alone. Expected: `tests/test_readme_theme_files.py` (shipped SVG names), `tests/test_desktoptheme_legacy.py` (`README_ANCHOR`; that test reads README directly with `open`), `tests/support/firefox_chrome_cases.py` (`cls.readme`), `tests/test_make_help.py::test_readme_names_every_public_target`, and the `make`-target/tool/package-path scans in `tests/test_readme_commands.py`. Run `make check` before retargeting to find any others. Each retargeted test keeps its containment-refusal case. Update any `docs/invariants.md` row that names README as where the moved text lives.

**Files.** `README.md`, `docs/installing.md` (new), the tests listed above, `docs/invariants.md` (only the rows that name the moved text).

**Acceptance criteria.**
- After the move, the moved subsection's content appears in `docs/installing.md` byte-for-byte, apart from heading levels and repointed link targets. Show that with a diff against the removed README lines that ignores those changes, and record how in VERIFIED.
- README no longer contains the sentence beginning "The package carries no art for the twelve legacy". `tests/test_desktoptheme_legacy.py` still finds it, through the corpus.
- README.md is at least 350 lines shorter. `make check` passes after the final edit, with no test deleted or skipped to get there.

### README split, part 3/5: move "Rendering a candidate" into docs/rendering.md (planned 2026-11-12 by the director role; "requires part 1/5 landed")

**Goal.** Move README's `### Rendering a candidate` subsection (about 170 lines: the `make render` modes and their dialog gates) into a new `docs/rendering.md`.

**Approach.** Same mechanics as part 2/5:
- Move the subsection verbatim into `docs/rendering.md`, from its heading up to `### Staging packages`. Give the file an H1, a back link to `../README.md`, and promote the headings one level.
- Leave a two-to-four-line README stub that links to it.
- Repoint links in both directions, including the Prerequisites table's `#rendering-a-candidate` link and any links from `## Fidelity checking`.
- Retarget `tests/test_readme_render_gates.py` and `tests/test_readme_commands.py::test_readme_names_every_tool_make_render_requires` (it searches for "`make render` renders") to `user_docs.read_user_docs()`, plus any other README reader that `make check` shows failing.
- Update the `docs/invariants.md` rows that say README's render section holds the evidence (for example the KPackage-route row) so they name `docs/rendering.md`.

**Files.** `README.md`, `docs/rendering.md` (new), `tests/test_readme_render_gates.py`, `tests/test_readme_commands.py`, `docs/invariants.md`.

**Acceptance criteria.** The verbatim-move check from part 2/5 applies. README no longer contains "`make render` renders", and the render-gate test still finds each gate name through the corpus. `make check` passes after the final edit, with no test deleted or skipped.

### README split, part 4/5: move "Sampling reference pixels" into docs/sampling.md (planned 2026-11-12 by the director role; "requires part 1/5 landed")

**Goal.** Move README's `## Sampling reference pixels` section (about 600 lines: sampling modes, the option references and troubleshooting) into a new `docs/sampling.md`, the sampler's user guide.

**Approach.** Same mechanics as part 2/5:
- Move every subsection verbatim into `docs/sampling.md`, from the section heading up to `## Fidelity checking`, with an H1, a back link and promoted headings.
- In README, the `## Sampling reference pixels` heading stays, so the Contents entry and the Prerequisites "Sample JPEG screenshots" link still resolve. Under it goes a short stub: one sentence on what the sampler is for, the single most common command, and a link to the guide.
- Repoint links in both directions. Retarget any README-reading test that `make check` shows failing to `user_docs.read_user_docs()` (`grep -rn README tests/` lists the readers).

**Files.** `README.md`, `docs/sampling.md` (new), plus only the tests and `docs/invariants.md` rows that name the moved text.

**Acceptance criteria.** The verbatim-move check from part 2/5 applies. README is at least 500 lines shorter. `make check` passes after the final edit, with no test deleted or skipped.

### README split, part 5/5: move the fidelity diagnostics into docs/fidelity.md (planned 2026-11-12 by the director role; "requires part 1/5 landed")

**Goal.** Move the bulk of README's `## Fidelity checking` section (about 400 lines) into a new `docs/fidelity.md`. That is `### Capturing a candidate`, `### Troubleshooting a render`, `### Comparing a region`, `### Troubleshooting a comparison`, `### Choosing a diagnostic` and `### Diagnostic reference`.

**Approach.** Same mechanics as part 2/5:
- README keeps the `## Fidelity checking` heading and its introductory paragraphs, up to the first `###`, followed by a link to the guide.
- Move the six subsections verbatim, up to `## Running checks`, with an H1, a back link and promoted headings.
- Repoint links in both directions, including links that part 3/5's `docs/rendering.md` may hold. Whichever part merges second fixes them, and part 1/5's link test catches a stale one.
- Retarget any README-reading test that `make check` shows failing to `user_docs.read_user_docs()`.

**Files.** `README.md`, `docs/fidelity.md` (new), plus only the tests and `docs/invariants.md` rows that name the moved text.

**Acceptance criteria.** The verbatim-move check from part 2/5 applies. README is at least 300 lines shorter. `make check` passes after the final edit, with no test deleted or skipped.


## Done

### GTK 4 suite extraction, part 5/9: isolate the progressbar probe (planned 2026-11-11 by the plan role; "requires part 1/9 landed") — done 2026-11-11 by the review role

**Goal.** Give the progressbar rendered check its own small suite; sibling parts 2–8 move different probes and do not depend on each other.

**Approach and files.** Move only `TestGtk4Theme.test_progressbar_faces_render` from `tests/test_gtk4_theme.py` into new `tests/test_gtk4_progressbar_probe.py::TestGtk4ProgressbarProbe(unittest.TestCase)`. Import required constants from `support/gtk4_sheet.py` and palette/spec modules directly; do not import the original test module or inherit its test class. Preserve the complete method, including child-source string, opt-in guard, exit-77 handling, environment and timeout. Repoint the corresponding test anchors in `docs/invariants.md` in the same change; retain historical completed-plan records. Prune imports from the old module only when unused. The recursive guard in `tests/test_no_gtk_introspection.py` already covers new Python modules; no scanner extension is needed.

**Acceptance.** Discovery finds `test_progressbar_faces_render` once at the new dotted ID and no longer at the old one; its AST body and embedded child program match the original. Without GUI opt-in the moved probe skips, with no desktop window. The documented isolated Xvfb invocation, adapted to this new ID, either exercises the same assertions or reports the existing capability skip. The invariants checker resolves its moved anchors and `make check` passes. No probe-prelude extraction or pixel changes are part of this move.

**Completion and verification.** The probe moved intact to its standalone unittest class; the invariant anchor and isolated README invocation use the new ID. Focused unittest discovery without GUI opt-in found the new test and skipped before launching a child; the old module no longer defines it. The child source, environment, timeout and pixel assertions are unchanged. Xvfb is unavailable here, so the isolated render invocation was not executed; no new rendered-pixel verification is claimed. Tumwater owns the full project check.

### Reference-pixel sampler: select named colors in scanline runs (planned 2026-11-03 by the plan role) — done 2026-11-03 by the feature role

**Goal.** Isolate known border and stripe shades in a reference crop while retaining their separate equal-color runs. The current run report filters lengths, while named inclusion is limited to histograms; source and related finished-plan searches found no named run selection. This feature is independent of the waiting histogram plan.

**Approach and files.** Add repeatable `--run-color RRGGBB` in `tools/sample_arguments.py::build_parser`, destination `run_colors`, default None, using `tools/sample_validators.py::rgb_argument`. In `option_error`, immediately after the maximum-run-length dependency check, require `--runs` with diagnostic `--run-color requires --runs`. In `tools/sample_report_runs.py::_runs_result`, build a set of requested RGB tuples once and intersect membership with the existing length predicates on completed `_color_runs` records. Selection ignores opacity, but segmentation still uses RGB or RGBA according to `--alpha`; retain separate adjacent runs of different selected colors. Preserve the report schema, traversal order and absolute coordinates. Add `tests/test_sample_runs_colors.py` using `CliTestCase` and fixture patterns from `tests/test_sample_runs_max_length.py::TestSampleRunsMaximumLength`; extend `tests/test_sample_option_validation.py::TestSampleOptionValidation`. Document the flag beside the run length filters in README.md and amend the scanline-run row in docs/invariants.md. These six files form one bounded change of a few hundred lines including tests; decoding and search-mode diagnostics remain outside scope.

**Acceptance criteria.**
- For a crop at (2,1) containing successive pixels A,A,B,B,B,A,C,C, where A=`010203`, B=`090807`, C=`040506`, selecting A emits starts (2,1) and (7,1) with lengths 2 and 1. Selecting A and C also emits (8,1) with length 2, in scan order. Adding minimum length 2 removes the singleton A; maximum length 1 retains only that singleton. Omitted B never joins the A runs. Selecting adjacent distinct colors retains their individual run records.
- Repetition, lowercase and optional `#` give the same selection. An absent color yields JSON `runs: []` and text with image, region and axis lines but no run lines or added metadata. Selecting the complete crop palette matches the unfiltered report. Literal expected records cover an offset nonsquare rectangle in both axes, inferred single-column traversal, an explicit vertical singleton, crop-edge runs and equal colors on adjacent scanlines that remain separate. Text and JSON agree; direct-script and package invocations agree; omitting the flag retains existing fixtures.
- For adjacent RGBA pixels (1,2,3,0), (1,2,3,128), (4,5,6,255), selecting `010203` yields one length-2 run in RGB mode and two length-1 runs with their original alpha bytes in alpha mode. Minimum length 2 in alpha mode yields an empty list, proving segmentation precedes selection and length filtering. An RGB-only fixture reports alpha 255 when requested.
- Missing and malformed values exit 2 with empty stdout. Valid use outside runs mode, including ordinary samples, histogram and find-color modes, exits 2 with `--run-color requires --runs` before image access; guard `os.open`, `read_png_size` and `read_png` in validation tests. Earlier incompatible-option diagnostics retain precedence. Help lists the repeatable option and the absent parser default is None. Run `make check` after final edits.

### Fidelity CLI: extract parser construction from comparison orchestration (planned 2026-11-02 by the plan role) — done 2026-11-11 by the feature role

**Goal and grounding.** Make the fidelity entry point readable as a comparison workflow. `tools/fidelity.py::main` currently starts with parser construction and a nested `worst_pixel_limit` validator before it reads images. `tools/fidelity_arguments.py` already owns the other argument validators. The finished report-extraction plan deliberately retained parser setup in the entry point; heading searches found no separate parser-extraction plan. This maintenance task is independent of the queued sampler work.

**Approach and files.** Create `tools/fidelity_cli_parser.py::build_parser`, moving the existing `EscapingArgumentParser` construction and option declarations there without changing their order, help strings, defaults, destinations or types. Move `worst_pixel_limit` to `tools/fidelity_arguments.py` and import the validators into the new parser module. In `tools/fidelity.py::main`, replace the construction block with `build_parser().parse_args(argv)` and remove imports made unused by the move. Support package imports and direct-script execution using the existing conditional import pattern. Keep image reads, crop application, optional diagnostic scans and reporting in their current owners. Inspect repository references to validators imported through `tools.fidelity` before removing those imports; preserve an existing consumer's import path if needed. Bound the change to those three production files and a new `tests/test_fidelity_cli_parser.py`; adjust ownership docstrings in the touched files. No CLI behavior change or new dependency is intended.

**Acceptance criteria.** Before moving declarations, capture characterization fixtures in the new test module for normalized help text and parsed default/explicit namespaces, including both crops, diagnostic switches and combined budgets. The same fixtures pass after extraction. Use the existing unittest framework to verify two independently constructed parsers work, malformed crop/budget/worst-pixel arguments retain status 2 and escaped diagnostics, and help and invalid arguments do not call `tools/fidelity.py::_read_source`. Existing fidelity CLI, JSON, crop and direct-script tests continue to pass. Run `make check` after final edits. This structural change adds no guarantee to docs/invariants.md; its existing tooling contracts remain the acceptance boundary.

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
