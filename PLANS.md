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
ChicagoFLF, a public-domain Chicago-style face, is planned for menus and window titles (the two
"Chicago-style face" plans under `## Planned`; its licence was checked 2026-11-12 by the director role).
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

### Chicago-style face, part 2/2: select ChicagoFLF for menus and window titles (planned 2026-11-12 by the director role; "requires part 1/2 landed")

**Goal.** Part 1/2 installs ChicagoFLF. This part selects it in the two KDE font roles that earlier font parts set aside for a Chicago-style face (PLANS-DONE.md, the font-selection part: "the part that vendors a Chicago-style face will update `menuFont`/`activeFont`"). Those roles are menus and active window titles. Body, toolbar and smallest-readable text stay Lato, the Charcoal-style face. Monospace keeps the user's fixed font.

**Approach and files.**
- `theme/look-and-feel/org.macos8.desktop/contents/defaults`: set `[kdeglobals][General] menuFont=ChicagoFLF,10` and `[kdeglobals][WM] activeFont=ChicagoFLF,10`. 10 is the KDE default size the Lato keys already use. Change no other key.
- `tests/test_lookandfeel.py`: split `test_fonts_name_the_installed_lato_family` into two tests:
  - One asserts that `font`, `toolBarFont` and `smallestReadableFont` name `Lato`.
  - `test_menu_and_title_fonts_name_the_installed_chicago_face` asserts that `menuFont` and `activeFont` name `ChicagoFLF` at a positive size equal to `font`'s size.
  - Keep the smallest ≤ general size check.
- Text that says menus and window titles use Lato must now name ChicagoFLF for those two roles:
  - `theme/fonts/org.macos8.desktop/PROVENANCE.md`: the Selection section and the "until a Chicago-style face lands" sentence.
  - `README.md`: the install paragraph describing the font package. It must not touch the brief block between the tumwater:prompt markers.
  - `docs/invariants.md`: the two rows naming `tests/test_lookandfeel.py::TestDefaults` and the font selection.
  - `PLANS.md`: the `## Planned` preamble's font sentence.
  - Find every such line with `grep -n "Lato" README.md docs/invariants.md theme/fonts/org.macos8.desktop/PROVENANCE.md PLANS.md`, excluding the archives.

**Acceptance criteria.**
- `grep -c "ChicagoFLF" theme/look-and-feel/org.macos8.desktop/contents/defaults` prints `2`.
- The new test fails if either key is reverted to Lato. The Lato test fails if `font` is set to ChicagoFLF.
- No remaining line outside the archives says menus or window titles use Lato.
- `make check` passes after the final edit.


### GTK 4 suite extraction: isolate OSD overlay declarations (planned 2026-11-12 by the plan role)

**Goal.** `tests/test_gtk4_theme.py` is still about 5,700 lines in one `TestGtk4Theme` class. That breaks the principle that a file is small enough to read in one sitting. Move the six `test_osd_*` declaration checks (about 380 lines) into their own module, the same way part 9/9 moved the calendar checks. This is independent of the cursor entries and of "GTK 4 suite extraction: isolate scale declarations": that entry moves only `test_scale*` methods, and the two method sets do not overlap. No stylesheet or production behavior changes.

**Approach and files.**
- Create `tests/test_gtk4_osd.py` with `class TestGtk4Osd(Gtk4SheetRuleCases, unittest.TestCase)` and a one-line module docstring. Move every `TestGtk4Theme` method whose name starts with `test_osd_` into it, keeping each method's body and docstring unchanged: `test_osd_entry_fields`, `test_osd_container_bands`, `test_osd_check_radio`, `test_osd_spinbutton_steppers`, `test_osd_progress_scale` and `test_osd_scale_thumbs`. Methods that only contain `osd` mid-name (`test_video_osd_image_corners`, `test_progressbar_osd_trough_paint`, `test_progressbar_osd_trough_thickness`, `test_switch_osd_checked_track_color`) stay where they are.
- Import the names the moved bodies use straight from the modules the original imports them from: `chain` from `itertools`; spec names such as `BUTTON_BEVEL`, `INVERTED_BUTTON_BEVEL`, `CHECK`, `RADIO`, `ENTRY_FIELD`, `INFOBAR`, `PROGRESSBAR_TROUGH`, `PROGRESSBAR_PROGRESS`, `SCALE_TROUGH`, `SCALE_THUMB` and `SCALE_EMPTY_FILL` from `support/gtk_theme_spec.py`; palette names such as `BLACK`, `WHITE`, `FACE` and `GREY` from `support/platinum_palette.py`. Where a name like `ETCH_DARK` exists in both modules, import it from the module `tests/test_gtk4_theme.py` imports it from. Never import `tests/test_gtk4_theme.py` or inherit `TestGtk4Theme`. `self.rules`, `self.selectors`, `assert_rule` and `assert_rule_group` come with `Gtk4SheetRuleCases`.
- Prune any import in `tests/test_gtk4_theme.py` that the remaining code no longer uses, and only those.
- In `docs/invariants.md`, rewrite each `tests/test_gtk4_theme.py::TestGtk4Theme::test_osd_…` anchor to `tests/test_gtk4_osd.py::TestGtk4Osd::test_osd_…`. Leave the rows' prose alone. Do not rewrite history in PLANS-DONE.md or BUGS-FIXED.md.

**Acceptance criteria.**
- Unittest discovery lists each of the six moved methods exactly once, under `test_gtk4_osd.TestGtk4Osd`, and none of them under `test_gtk4_theme.TestGtk4Theme`. Every other `TestGtk4Theme` method is still listed there.
- For each moved method, the AST of its function definition is identical to the original's at this plan's base commit, checked once during the run (for example by comparing `ast.dump` output). This is a run-time check, not a new committed test.
- `grep -n 'TestGtk4Theme::test_osd_' docs/invariants.md` prints nothing, and the invariants checker inside `make check` resolves every new anchor.
- `tests/test_gtk4_theme.py` shrinks by at least the moved methods' line count, and `tests/test_gtk4_osd.py` stays under about 450 lines.
- `git diff --stat` touches only `tests/test_gtk4_theme.py`, `tests/test_gtk4_osd.py` and `docs/invariants.md`. `make check` passes after the final edit.

### KDE fixed-width font, part 1/3: package JetBrains Mono (planned 2026-11-12 by the director role)

**Goal.** Ship the user's approved JetBrains Mono family with the theme, like Lato
(QUESTIONS.md, "Which monospaced font should the theme ship for fixed-width text?").
The user's 2026-11-12 follow-up requires its use in Konsole and KDE fixed-width roles;
parts 2/3 and 3/3 select it. This part installs assets without selecting them.

**Approach and files.** Obtain the static Regular, Medium and Bold TTFs and the copyright
file from Debian's `fonts-jetbrains-mono` package, using a downloaded package extracted
in scratch space rather than installing system packages. Vendor unmodified copies as
`theme/fonts/org.macos8.desktop/JetBrainsMono-{Regular,Medium,Bold}.ttf` and
`LICENSE-JetBrainsMono.txt`. Extend that directory's `PROVENANCE.md` with the package
version, download URL, archive and shipped-file SHA-256 digests, upstream author/source,
OFL-1.1 redistribution basis, and internal family/subfamily names read from the files.
Record this as a user-selected approximation: the references supply no terminal font
surface or font pixel. Keep Lato and ChicagoFLF assets intact. The existing Makefile
font-package directory install is the intended install path.

**Acceptance criteria.** Extend `tests/test_fonts.py`, reusing `_name_table`, to verify
the three faces' family/subfamily identities, pinned digests and provenance/licence
records; include a fixed-pitch check of the TTF `post` table's `isFixedPitch` field using
the standard library. Extend its install lifecycle expectations to cover byte-preserving
staged installation and removal of the new files while preserving a foreign font sibling.
Update the fonts section of `docs/invariants.md` and the font inventory in the installation
guide (README.md or its extracted `docs/installing.md`). `make check` passes. No selection
changes belong to this part.

### KDE fixed-width font, part 2/3: select the KDE fixed role (planned 2026-11-12 by the director role; "requires part 1/3 landed")

**Goal.** Select packaged JetBrains Mono Medium at 10 pt for KDE's fixed-width role.
This replaces the earlier statement that monospaced text keeps the user's fixed font.
Konsole profile overrides are handled separately in part 3/3.

**Approach and files.** Add `[kdeglobals][General] fixed` to
`theme/look-and-feel/org.macos8.desktop/contents/defaults`. Use Qt's serialized QFont
form specifying family JetBrains Mono, point size 10 and Medium weight (Qt 6 weight 500),
with the style name Medium, grounded against the installed Qt 6 serialization contract;
record that contract and the exact chosen string in the font package's `PROVENANCE.md`.
Use a scratch-home `lookandfeeltool` application to verify the key is actually published;
if it is not, add an explicit `kwriteconfig6` step to `tools/apply_theme.py::STEPS` after
the global-theme step, and test that path in `tests/test_apply_theme.py`. No visible GUI
probe is permitted. Extend `tools/uninstall_live_diagnostics.py::_font_diagnostics` and
`kdeglobals_messages` to read `fixed` and warn for the published value, naming the correct
family and the `--group General --key fixed --delete` reset. Preserve other font warnings.

**Acceptance criteria.** In `tests/test_lookandfeel.py::TestDefaults`, pin family, point
size, Medium style/weight and presence of `fixed`; dropping the key or selecting Lato
must fail. Extend `tests/test_kdeglobals_fonts_uninstall_diagnostic.py` for a matching
fixed selection, a foreign value, later duplicate override and another group; diagnostics
leave config bytes intact. Update the fonts/look-and-feel rows in `docs/invariants.md`,
the installation guide, font provenance and this file's current-state preamble, replacing
the superseded fixed-font statements. Preserve Chicago menu/title selection work. Document
that KDE clients using the system fixed font inherit this choice; application-specific
overrides may supersede it. `make install` remains selection-free; `make check` passes.

### KDE fixed-width font, part 3/3: apply it to the default Konsole profile (planned 2026-11-12 by the director role; "requires part 2/3 landed")

**Goal.** Ensure new Konsole sessions use the packaged face even when the default
profile has an explicit font override, while preserving shell, colors, shortcuts and
other profile settings. This completes the user's 2026-11-12 request alongside part 2/3.

**Approach and files.** Add a focused `tools/apply_konsole_font.py` helper and call it
from `tools/apply_theme.py::_apply` after required Plasma selections, under the existing
data-home lock. Resolve homes through `tools/xdg_homes.py`. Read Konsole's
`konsolerc [Desktop Entry] DefaultProfile` and resolve that profile through XDG data
search directories; ground these platform keys against upstream Konsole source and
record the source/version in the installation guide. Write only `[Appearance] Font`,
using part 2/3's exact QFont value and the existing bounded `run_required`/`kwriteconfig6`
command pattern. For a profile in a system data directory, first copy it to the user's
`konsole/` directory with the same basename, then modify that copy. For an absent default
or the built-in fallback, create `konsole/Platinum.profile` with `[General] Name=Platinum`,
`Parent=FALLBACK/` and the font, then select that filename in `konsolerc`. Refuse unsafe
profile names (absolute paths, separators or traversal), symlink destinations and an
unresolvable explicitly named profile, with an actionable diagnostic rather than guessing.
Do not edit non-default profiles. Do not start Konsole or require its binary; the helper
prepares its config even on systems where it is not installed. Fail apply on a config
write error using the existing required-step error conventions.

**Acceptance criteria.** Add `tests/test_apply_konsole_font.py` with scratch XDG homes
and stubbed commands, covering a user default with a foreign font, a system default copied
locally, fallback creation, repeated apply, unsafe names, symlink refusal and command
failure. Assert unrelated profile keys, shell and keyboard mappings are preserved, and
system source files and non-default profiles stay byte-identical. Extend
`tests/test_apply_theme.py` to prove helper invocation, ordering and failure propagation.
Document new-session/restart requirements and the exact manual reset for the selected
profile's font; uninstall continues to preserve user configuration. Update
`docs/invariants.md` with the helper's guarantees and tests. `make check` passes without
opening a window in the user's session. Keep this run to the helper, wiring, tests and
their documentation; extra terminal/editor integrations are outside this part.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
