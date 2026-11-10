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

_None yet._ (Only the standing scope-drift note above.)

### Sample JPEG screenshots directly: let `tools/sample.py` convert a JPEG input through ImageMagick instead of refusing it with "convert it to PNG first" (planned 2026-11-10 by the plan role; an independent tooling capability beside the waiting icon-dialog render entry — different CLI, different files, mergeable in any order)

**Goal.** The sampler is PNG-only: `python3 tools/sample.py` pointed at one of the reference set's JPEG screenshots (verified 2026-11-10 against `macos8.6-screenshots/opendialog_macrumors86.jpg`) exits 2 with `error: cannot decode <path>: not a PNG file: the input is a JPEG image, not a PNG; convert it to PNG first` — a refusal whose own text promises a conversion. Measuring a JPEG-distributed reference surface (e.g. the Open dialog's push-button recipes cite `opendialog_macrumors86.jpg`) currently needs a manual `convert` round-trip whose output path, naming and cleanup the operator nurses by hand. Let the sampler do that decoding itself: a JPEG input is sniffed at open, converted once through ImageMagick into a private temporary PNG, and then sampled exactly like a PNG today. The PNG decode pipeline in `tools/png/` stays stdlib-only PNG; this plan adds the conversion bridge beside the disk layer, not inside the package.

**Approach and files.** Add `tools/jpeg_convert.py`, a small module beside the PNG package holding everything the sampler's JPEG branch shares: `JPEG_MAGIC = bytes((0xFF, 0xD8, 0xFF))`; `is_jpeg(head: bytes) -> bool`; and `convert_jpeg(input_bytes: bytes, temp_png: Path) -> str | None` that resolves `convert` with `shutil.which` and, when it is absent, returns a diagnostic naming `convert` (the same message shape the sampler's other refusals print), otherwise runs `convert jpeg:- png:<temp_png>` with the bytes piped on stdin, supervised through `tools/process_group.py::run_logged_split` (returning the failure text through its non-zero-status path), and returns None on success — the output is written into a caller-provided path inside a private `tempfile.TemporaryDirectory()`, never the input's directory, so the user's tree is untouched and no planted path is followed. In `tools/sample.py::main`, after the existing fd open, containment and regular-file checks, `os.pread` the fd's first three bytes — a read on the already-open stable procfs handle, so a concurrent symlink swap cannot change what is sniffed — and route through a JPEG branch when `is_jpeg` holds: (1) a `--alpha` or `--match-alpha` refusal fires before any conversion, naming that flag, exiting 2, because a JPEG carries no alpha channel to sample or match; (2) the fd is read whole with `os.pread`, the private temp directory is created, and a `convert_jpeg` problem returns through `report_error` naming the user-facing path like every other failure while a success continues with `read_png_size` and `read_png` on the temp PNG, the same `region_error` bounds check as today running against the JPEG's own decoded size, and any `PngError` message carrying the temp path rewritten to `args.image` by the landed `/proc/self/fd` rewrite's pattern; (3) the `image:` header line still names `args.image`, now with the decoded JPEG's width x height. The non-JPEG path keeps the entire current code path byte for byte: same `read_png_size`/`read_png` calls, same refusal texts, no subprocess, so the `--alpha` and `--match-alpha` PNG behaviors are unchanged. No change to `tools/fidelity.py`; this plan covers the sampler only. README's `## Sampling reference pixels` opening paragraph gains one sentence: JPEG inputs are converted with ImageMagick before sampling, `--alpha` and `--match-alpha` need a PNG because JPEG carries no alpha, and the reference set's JPEG screenshots are readable directly. docs/invariants.md's `## tooling` table gains one dated (2026-11-10) end-of-table row naming the new tests, the JPEG flag rejection, ImageMagick's input-format decode, and that the PNG decoder itself is unchanged.

**Fixtures.** `tests/support/jpeg_sampler_fixture.py` ships a deterministic tiny JPEG as a base64 constant: the feature run generates it once with `convert` from a deterministic small RGB quilt (e.g. 32x24 colored blocks with distinct RGB values) and, alongside the base64, records the exact post-conversion decoded RGB triples measured once through the completed sampler, written as literal constants (the JPEG artifact, like the reference set's own JPEGs, is measured evidence, not a computed value). The test thus never runs ImageMagick at check time: it base64-decodes the shipped bytes and exercises `is_jpeg` and the sampler end to end against the recorded constants; give the fixture file a one-line provenance comment naming the generation date and command.

**Acceptance criteria.**

- `python3 tools/sample.py <fixture>.jpg <x> <y> --width 3 --height 2` prints the pinned RGB triples and hex literals for that pinned region, identical to the recorded constants; `--histogram` and `--runs` over pinned regions report exactly the recorded counts; `--find-color` with a recorded hex literal yields the recorded match coordinates. The `image:` header line names the user-facing `.jpg` path with the decoded JPEG's own width x height.
- JPEG with `--alpha` or `--match-alpha` exits 2 with a message naming that flag before any conversion runs; the same flags on a PNG still work exactly as today.
- With `convert` absent from PATH (test by monkeypatching `shutil.which` in `tools.jpeg_convert` or by an empty-PATH subprocess environment), a JPEG input exits 2 with a diagnostic naming `convert` and reaches no other read. A truncated JPEG whose bytes decode to no valid image exits 2 with a diagnostic naming the user-facing `.jpg` path, never the temp one.
- Every existing PNG-path sampler test passes unchanged and the fixture test asserts the JPEG branch is not entered for a PNG input (no conversion attempt, no subprocess); non-PNG non-JPEG bytes keep today's exact `not a PNG file` refusal. `make check` passes after the final edit.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::_MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
