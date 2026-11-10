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

_None yet._ (Only the standing scope-drift note above; the entries below wait in the queue.)


### Reference validation: reject a truncated image body (planned 2026-11-09 by the plan role)

**Goal.** A reference download cut short can end in valid image bytes: today `tools/reference_validation.py::_check_entries` sniffs only the leading bytes through `tools/image_format.py::is_image`, so a truncated PNG (signature and IHDR present, IEND missing) passes `make check-references` and is found later only when a sampler decode of that image fails. The checker should report an incomplete stream at validation time, complementing the unrelated README diagnostics guide under `## Planned`. New diagnostic text is the contract, so it is pinned in tests.

**Approach and files.** In `tools/image_format.py` add `TERMINAL_PNG = bytes((0, 0, 0, 0)) + b"IEND" + b"\xae\x42\x60\x82"` (the zero-length IEND chunk with its constant CRC) and `TERMINAL_JPEG = b"\xff\xd9"`, `TERMINAL_GIF = b";"`, plus a pure function `is_complete(head: bytes, tail: bytes, size: int) -> bool` that identifies the format from `head` alone (PNG, JPEG, GIF 87a/89a, or RIFF+WEBP per the existing constants: never the extension, so `sherlock_fandom.jpg` routes by its WebP container) and returns True only when: PNG's last bytes equal `TERMINAL_PNG`; JPEG's last two bytes equal `TERMINAL_JPEG`; GIF's last byte is `TERMINAL_GIF`; or WebP's declared RIFF size (`int.from_bytes(head[4:8], "little") + 8`) equals `size`. Return False when the format is not an image. In `tools/reference_validation.py`, have the declared-entry reader take head and last 12 bytes in the single existing `open_regular_binary` call (padding `tail` with the head's own bytes when the file is shorter keeps both reads atomic in one open), and after the signature check passes append a problem naming the format's missing terminator: a PNG "ends without the PNG IEND trailer", a JPEG "ends without the JPEG EOI marker", a GIF "ends without the GIF trailer byte", a WebP "declares N RIFF bytes but holds M" (N from `head[4:8]`, M from `size`), each with the existing `"{sources}:{lineno}: {filename!r} ...; it may be a truncated download"` suffix and prefix shape. `_check_undeclared` still sniffs heads only. An unrecognized-payload diagnostic (HTML error page under an image name) always outranks the truncation diagnostic. Update `tools/check_references_selftest.py`'s clean-set fixtures from their current `PNG_MAGIC`-only contents to complete minimal images (a helper prefix plus `TERMINAL_PNG` suffices, as for JPEG `JPEG_MAGIC + TERMINAL_JPEG`, GIF `b"GIF89a" + TERMINAL_GIF`, WebP `b"RIFF" + (4).to_bytes(4, "little") + b"WEBP"`) and add four truncated cases, each one expecting the new diagnostic text. In `tests/test_check_references_validation.py` unit-test `is_complete` direction by direction (each complete form passing, each cut form failing, a RIFF/WAVE payload failing the image test before any terminator check) and pin the CLI diagnostics with `reference_set`/`assert_problem`; the existing `test_declared_image_prefix_is_read_with_one_open` must pass unchanged. README's `## Validating the reference set` failure list gains one clause naming the missing-stream-terminator diagnostic and stating it is a bounded structural check, not a full decode; add and date a `## tooling` row in docs/invariants.md pinning the ending rules with this entry's measurement below as provenance.

**Acceptance criteria.**

- For each of the four formats, a declared file missing its terminator exits 1 from `python3 tools/check_references.py` on a fixture set, prints the `sources.txt:<line>` problem naming the file and the format's terminator (WebP naming its declared and held sizes), and no sampler is ever reached; a complete `JPEG_MAGIC + TERMINAL_JPEG` fixture and the set's intact files still pass. A RIFF/WAVE payload keeps the existing "not a PNG, JPEG, GIF or WebP" diagnostic, never a truncation one.
- Against the materialized repository set, `make check-references` passes with today's output unchanged; `python3 tools/check_references.py --self-test` exits 0 with the rewritten fixtures and the `test_declared_image_prefix_is_read_with_one_open` open count stays exactly one per declared file.
- README's new clause and the dated invariant row name these tests; the row records that every currently materialized reference file satisfies the ending rules (verified 2026-11-09 for all 28 image files in `macos8.6-screenshots/`) so no shipped reference regresses the gate. No runtime path other than `check-references` changes behavior; `make check` passes after the final edit.

### Kvantum line-edit dialog render gate: pin a captured kdialog input box's sunken field on the landed art recipe (planned 2026-11-09 by the plan role; independent of the waiting truncated-image entry ahead of it in the queue — that entry edits `tools/image_format.py`, `tools/reference_validation.py` and the check-references suites with their README "Validating the reference set" and invariants rows, while this entry edits the render plumbing and its suites with README's render sections, so they share no file region and can merge in either order)

**Goal.** The live render gates already measure the kdialog checkbox cell, the combobox indicator and combo field, the GTK entry and button bands, and the window-chrome strips, but no gate captures the theme's sunken white line edit from a rendered pixel: a Kvantum `[LineEdit]` regression ships green. A kdialog input-box dialog opens a real themed line edit in the isolated headless session, giving the missing surface. No collected reference screenshot shows a dialog with an input field, so the comparison surfaces are the shipped art recipe — the sunken-field arrangement `tests/test_kvantum_lineedit_reference.py` re-derives from `firstboot_betawiki.png` and `tests/support/firstboot_lineedit.py` pins — and the landed push-button recipe; the references they name stay out of the gate code, exactly as the landed GTK entry/button gate does.

**Approach and files.** In `tools/render_surface.py` add a mutually exclusive `--lineedit-dialog` flag in the existing dialog flag group, included in the same dialog-size argument checks (rejects `--width`, `--height` and a non-default `--applet`) and fixed at 480x360; counts as one of the kdialog dialog modes for the tool check (the `kdialog_flags` line) and shares the dialog session setup (`tools/render_workflow.py` dispatches a new `tools/render_clients.py::lineedit_dialog_client` returning `kdialog --title Test --inputbox Choose a name:` with an empty initial value; the empty field keeps the caret at the field's left padding). Add `lineedit-dialog) set -- --lineedit-dialog ;;` beside the `checkbox-dialog` branch of the `Makefile` `RENDER_MODE` case and extend the RENDER_MODE error strings that enumerate the modes. In `tests/test_render_surface.py`, add unit cases beside the landed dialog-mode cases (mutually exclusive with each other dialog mode and the calculator surface, missing-tool naming names kdialog, usage exit 2, help text names the mode; the landed `test_only_dialog_renders_add_kdeglobals_to_the_session_configs` must pass unchanged). Model the new gate class `TestLineInputDialogRender` on `TestCheckboxDialogRender` (same prerequisite and software-renderer-guard skips): measure the window origin and crops from two consecutive full `--lineedit-dialog` captures on the implementation host that agree byte for byte under `cmp`, then pin (a) the field band's crop and expected pixels against the sunken-field arrangement `ShippedSunkenFieldMixin` pins for the shipped tiles — the same shadow/outline/face arrangement the reference's Setup Assistant field shows — choosing the crop so no caret or glyph byte falls inside it (the landed GTK `ENTRY_FIELD_CROP` trick, right of the caret with the field empty), and (b) the OK push-button band's crop against the landed push-button arrangement the checkbox gate pins (1px black border rows and border column, white bevel top arm, flat #DDDDDD face, #AAAAAA `BUTTON_SHADOW` bottom arm) with the band's own position measured on the host. Record both measured-crop dates in the class comment the way the landed crops' comments name their capture dates. README's dialog-capture table gains one row naming the command and image size beside the dialog rows, and docs/invariants.md's `## tooling` table gains one dated (2026-11-09) end-of-table row naming the gate's tests, the missing reference surface (no dialog input field in the set), and the shipped-art/landed-recipe value sources.

**Acceptance criteria.**

- `python3 tools/render_surface.py --lineedit-dialog out.png` and `make render RENDER_MODE=lineedit-dialog out.png` reach the same argv; using the new flag with any other dialog flag or the calculator surface, or with `--width`/`--height`/a non-default `--applet`, exits 2 before installing; a missing kdialog is named as the first missing tool; `--help` and the Makefile's RENDER_MODE enumeration name the new mode.
- When the documented render prerequisites are present and the software-renderer guard is quiet, two consecutive full `--lineedit-dialog` captures agree byte for byte under `cmp`, and the gate's two pinned crops match the expected pixels: the field band paints the shipped sunken-field arrangement with no caret byte inside the crop, and the OK band paints the landed push-button arrangement. The gate skips cleanly when its tools are missing or the software-renderer guard triggers, so `make check` passes with today's skip behavior on the hosted job.
- The gate code reads no reference screenshot and mentions no brand or library name (the landed sheet-level conventions); the invariants row records the measured-capture provenance and the value sources. `make check` passes after the final edit.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::_MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.
