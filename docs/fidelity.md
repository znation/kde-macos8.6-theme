# Fidelity checking

Back to [README](../README.md).

## Capturing a candidate

Capture the default Plasma calculator with `make render`, setting its output path with
`RENDER_OUTPUT`:

```sh
make render RENDER_OUTPUT=calculator.png
make render RENDER_MODE=checkbox-dialog RENDER_OUTPUT=checkbox.png
make render RENDER_MODE=desktop RENDER_OUTPUT=desktop.png
make render RENDER_MODE=splash RENDER_OUTPUT=splash.png
```

The Make target uses `RENDER_MODE` (`calculator` by default) to select the calculator, one of
the fourteen dialogs, the desktop menu bar, or the startup splash. The calculator capture defaults to 320x240; dialogs
are fixed at 480x360 and
require `kdialog` for checkbox, combo box, line edit, menu, radio list, calendar, color picker, icon
chooser, progress meter, slider, text box, the two-window inactive pair and the file chooser or
`zenity` for GTK; the desktop capture is fixed at 640x400 and requires `plasmashell`; the splash
capture is fixed at 640x400 and requires `ksplashqml`.
Direct Python commands remain available; each dialog flag must be used alone, and dialog captures
reject `--width`, `--height` and a non-default `--applet`:

| Surface | Command | Image size |
| --- | --- | --- |
| Checkbox dialog | `python3 tools/render_surface.py --checkbox-dialog checkbox.png` | 480x360 |
| Combo box dialog | `python3 tools/render_surface.py --combobox-dialog combobox.png` | 480x360 |
| Line edit dialog | `python3 tools/render_surface.py --lineedit-dialog lineedit.png` | 480x360 |
| Menu dialog | `python3 tools/render_surface.py --menu-dialog menu.png` | 480x360 |
| Radio list dialog | `python3 tools/render_surface.py --radiolist-dialog radiolist.png` | 480x360 |
| Calendar dialog | `python3 tools/render_surface.py --calendar-dialog calendar.png` | 480x360 |
| Color dialog | `python3 tools/render_surface.py --color-dialog color.png` | 480x360 |
| Icon dialog | `python3 tools/render_surface.py --icon-dialog icon.png` | 480x360 |
| Progress bar dialog | `python3 tools/render_surface.py --progressbar-dialog progressbar.png` | 480x360 |
| Slider dialog | `python3 tools/render_surface.py --slider-dialog slider.png` | 480x360 |
| Text box dialog | `python3 tools/render_surface.py --textbox-dialog textbox.png` | 480x360 |
| GTK dialog | `python3 tools/render_surface.py --gtk-dialog gtk.png` | 480x360 |
| Inactive dialog | `python3 tools/render_surface.py --inactive-dialog inactive.png` | 480x360 |
| File dialog | `python3 tools/render_surface.py --file-dialog file.png` | 480x360 |
| Desktop | `python3 tools/render_surface.py --desktop desktop.png` | 640x400 |
| Startup splash | `python3 tools/render_surface.py --splash splash.png` | 640x400 |

The calculator capture defaults to 320x240. Dialog captures need `kdialog` on `PATH` in the
kdialog modes and `zenity` in the GTK mode; the desktop capture needs `plasmashell` on `PATH`;
the splash capture needs `ksplashqml` on `PATH`;
see [Prerequisites](../README.md#prerequisites) for the render tools. To allow a slower calculator paint,
increase the settle wait and set a longer timeout (which must exceed settle):

```sh
python3 tools/render_surface.py --settle 12 --timeout 120 calculator.png
```

A longer wait does not guarantee a successful capture. Compare the candidate with the relevant
reference surface using the [fidelity checker](../README.md#fidelity-checking); use its crop options to
compare a region rather than assuming a full capture matches a reference screenshot.

## Troubleshooting a render

| Symptom | Check and next action |
| --- | --- |
| The diagnostic names a missing or unstartable executable. | Repair that executable or its `PATH` entry, then rerun the same command. The first missing required tool is named; a present but unstartable `make` or `dbus-run-session` is also diagnosed. |
| The capture is entirely black. | The window did not paint before capture. Check whether the paint needs more time and increase `--settle`; use the [slower-paint example](#capturing-a-candidate), with `--timeout` longer than `--settle`. A longer wait does not guarantee a capture. |
| The render timed out. | Check [Prerequisites](../README.md#prerequisites) and increase `--timeout` only as needed, keeping it longer than `--settle`. A missing `org.kde.plasma.calculator` applet is no longer an undiagnosed timeout cause: its own preflight refusal exits 2 before any session and names the applet id. |
| The render session exits nonzero. | Inspect the diagnostic's printed session log tail for the failing command. The log is in a temporary scratch directory and is removed with the session, so it is not a persistent report. |

Direct `python3 tools/render_surface.py` invocations return 2 for usage or preflight errors
(including missing tools and invalid timeout settings), and 1 for workflow failures. GNU Make
reports its own recipe-failure status for `make render`. Failure diagnostics include a bounded
log tail when a log is available. The software-renderer skip described in
[Running checks](../README.md#running-checks) applies to the automated pixel gates; it is separate from a
direct render failure.

## Comparing a region

When render tools are available and the software-renderer guard does not trigger, the
calculator title-strip gate compares these corresponding 80x22 rectangles:

```sh
python3 tools/fidelity.py calculator.png macos8.6-screenshots/aboutsystem_betawiki.png --candidate-crop 30,0,80,22 --crop 30,25,80,22
```

Use [Rendering a candidate](rendering.md) to produce `calculator.png`; see
[Capturing a candidate](#capturing-a-candidate) for capture options, and
[Validating the reference set](../README.md#validating-the-reference-set) to materialize the images.
These coordinates belong to the documented calculator/title-strip gate, not arbitrary windows.
For another surface, choose corresponding rectangles independently in the two images; they must
have equal dimensions. `aboutsystem_betawiki.png` is the documented beta window-chrome proxy:
its relevant chrome is pixel-identical to the retail reference, as pinned by the
retail-equivalence test. It is not general evidence for retail palette values.

## Troubleshooting a comparison

| Symptom | Check and next action |
| --- | --- |
| The reference is an unmaterialized Git LFS pointer. | Follow [Validating the reference set](../README.md#validating-the-reference-set) to install Git LFS and materialize the image. |
| An input is missing or unreadable. | Check the path named in the diagnostic and confirm the file is readable. |
| A JPEG input is refused because `convert` is unavailable. | Install ImageMagick and verify `convert` is on `PATH`. |
| A PNG is refused during decoding. | Inspect the named image and provide a valid supported PNG input. |
| A crop extends beyond its image. | Correct that source's crop coordinates; see [Comparing a region](#comparing-a-region) for the two crop options. |
| The cropped images have different sizes. | Choose corresponding equal-size regions using [Comparing a region](#comparing-a-region). |

A completed comparison returns 0 when it passes and 1 when it reports a mismatch; use
[Choosing a diagnostic](#choosing-a-diagnostic) to inspect a mismatch. Usage and input
refusals return 2. `--quiet` suppresses comparison reports, so omit it when you need to see
the mismatch details. Direct CLI statuses differ from Make's recipe-failure status.

Add mismatch locations and RGBA values in JSON with:

```sh
python3 tools/fidelity.py calculator.png macos8.6-screenshots/aboutsystem_betawiki.png --candidate-crop 30,0,80,22 --crop 30,25,80,22 --worst-pixels 5 --explain-worst --json
```

The exit status is 0 when the comparison passes, 1 when it fails, and 2 for a usage or read error.

## Choosing a diagnostic

Append one of these options to the aligned-crop command above to choose the report that best
answers your question:

| Need | Additional options | Result |
| --- | --- | --- |
| [Find the enclosing mismatch rectangle](#fidelity-report-bounds) | None; this is the default report | Smallest bounds containing pixels beyond tolerance; unchanged gaps may lie inside. |
| [Inspect the most severe individual mismatches](#fidelity-report-worst-pixels) | `--worst-pixels 5 --explain-worst --json` | Ranked pixels with positions, RGBA values and channel differences. |
| [See horizontal mismatch segments](#fidelity-report-horizontal-runs) | `--difference-runs --max-difference-runs 20 --json` | Capped list of horizontal intervals. |
| [Locate the longest horizontal defect](#fidelity-report-longest-horizontal-run) | `--longest-difference-run --json` | One longest horizontal mismatch segment with crop-relative start and pixel length, or null when no pixel exceeds tolerance. |
| [See vertical mismatch segments](#fidelity-report-vertical-runs) | `--difference-column-runs --max-difference-column-runs 20 --json` | Capped list of vertical intervals. |
| [Locate the longest vertical defect](#fidelity-report-longest-vertical-run) | `--longest-difference-column-run --json` | One longest vertical mismatch segment with crop-relative start and pixel length, or null when no pixel exceeds tolerance. |
| [Find row and column concentration](#fidelity-report-scanline-counts) | `--difference-rows --difference-columns --json` | Per-row and per-column mismatch counts. |
| [Attribute mismatches to channels](#fidelity-report-channel-counts) | `--channel-counts --json` | Per-channel counts; a pixel may count in multiple channels, so do not sum them. |
| [See the error-magnitude distribution](#fidelity-report-delta-histogram) | `--delta-histogram --json` | Counts grouped by each pixel's maximum absolute RGBA delta. |
| [See typical and tail error](#fidelity-report-delta-percentiles) | `--delta-percentiles --json` | Nearest-rank p50, p95 and p99 maximum RGBA deltas. |
| [Check the direction of channel drift](#fidelity-report-channel-bias) | `--channel-bias --json` | Signed mean candidate-minus-reference RGBA deltas. |
| [Find the worst error per channel](#fidelity-report-channel-maxima) | `--channel-maxima --json` | Maximum absolute delta for each RGBA channel. |

Interval coordinates are relative to the compared crops. See [Diagnostic reference](#diagnostic-reference)
for details about these reports and their fields.

The longest horizontal segment covers the complete compared crop; ties select the earliest row,
then column. This summary alone does not emit the full interval list.

The longest vertical segment also covers the complete compared crop; ties select the earliest
column, then row. This summary alone does not emit the full interval list.

These are raw-byte diagnostics: where applicable they include zero and sub-tolerance errors,
and none changes the comparison verdict. Opposite signed errors can cancel in channel bias.

Reported `x`/`y` positions are relative to the compared crops. `candidate_position` and
`reference_position` locate each result in the original images; `--explain-worst` gives both
pixels' RGBA values and their channel differences. A mismatch is a useful report with exit status
1; status 2 means usage or image reading failed. See the diagnostic reference below for other
reports.

## Diagnostic reference

<a id="fidelity-report-bounds"></a>

Add `--json` to emit the paths, crop rectangles, thresholds, full precision metrics and verdict
as one JSON object (for example, `python3 tools/fidelity.py render.png reference.png --json`).
The `metrics` object uses the field names from `tools/fidelity_metrics.py::Metrics`; crop-relative
dimensions, worst-delta coordinates, and `difference_bounds` describe the compared surfaces.
The bounds are `(x, y, width, height)` for the smallest rectangle containing pixels whose
maximum channel delta exceeds tolerance, or `null`/`none` when no pixel exceeds it.
The top-level `candidate_difference_bounds` and `reference_difference_bounds` translate that
rectangle into each source image's coordinates, using the corresponding crop origin (or zero).
Text output prints the same two source rectangles after the local bounds line.

A candidate or reference path inside the repository that resolves outside it (a checked-in
symlink) is refused by name before it is read, so a comparison cannot probe a private image;
a path outside the repository is read as before. Guarded PNG reads and crop-bounded row decoding
are handled by `tools/fidelity_sources.py`, called by the CLI in `tools/fidelity.py`.
Add `--quiet` to suppress the report and use only the exit status (0 pass, 1 comparison failure,
2 usage or read error) in a scripted gate. It can be combined with comparison diagnostics, which
are still calculated but not printed; `--quiet` and `--json` are mutually exclusive.

By default a run passes only when no pixel differs from the reference by more than `--tolerance`
(a per-channel delta; 0, i.e. byte-exact, unless given). Each pixel's alpha byte is compared
along with its red, green and blue bytes, so a transparent candidate cannot pass as an opaque
reference. `--max-mae F`, `--max-frac F` and `--max-differing N` set
aggregate budgets instead: when one is given, a run passes when each given budget is met —
`--max-mae` bounds the mean absolute error, `--max-frac` bounds the differing-pixel fraction, and
`--max-rmse` bounds root mean square error, and `--max-delta` caps the largest absolute RGBA
channel difference; `--max-differing` caps the absolute number of pixels whose maximum RGBA
channel delta exceeds `--tolerance` — and the default no-differing-pixel gate no longer applies.
<a id="fidelity-report-longest-horizontal-run"></a>

`--longest-difference-run` reports the longest horizontal contiguous interval whose maximum raw
RGBA channel delta exceeds tolerance, with crop-relative `x`, `y` and `length`; ties use the
earliest row and then column. The JSON field is `longest_difference_run`, and an empty comparison
reports `null`. When combined with `--difference-runs`, it reuses those intervals.
<a id="fidelity-report-longest-vertical-run"></a>

`--longest-difference-column-run` reports the longest vertical contiguous interval under the same
comparison rule, with crop-relative coordinates; ties use the earliest column and then row. Its
JSON field is `longest_difference_column_run`, and an empty comparison reports `null`. When
combined with `--difference-column-runs`, it reuses those intervals.
<a id="fidelity-report-worst-pixels"></a>

The mean, RMSE and maximum-delta metrics use comparison raw bytes and are independent of
`--tolerance`; the differing-pixel fraction and the `--max-differing` count are measured beyond
`--tolerance`. RMSE is not a perceptual error measure. Add `--worst-pixels N` (1–1000) to list
the most severe mismatches, ranked by maximum RGBA channel delta with row-major tie ordering.
The listed `x`/`y` coordinates are relative to the compared, cropped surfaces. Each record also
includes `candidate_position` and `reference_position`, which add the corresponding crop origin
and point into the original images (an omitted crop has origin 0,0). Text lines show both source
positions too. With `--json`, the records appear in a `worst_pixels` array; the default output and
work remain unchanged.
Use `--worst-pixel-offset K` with `--worst-pixels N` to page through the same ranked list;
the offset is a nonnegative ASCII decimal integer. Ranking, tolerance and comparison metrics
are unchanged by pagination. Selection storage grows with `K + N`, capped at the compared image
area; decoding and comparison still process the requested images as before. An offset beyond the
available mismatches emits an empty `worst_pixels` array (or no records in text output).
Add `--explain-worst` to report the candidate and reference RGBA values at the comparator's
maximum-delta pixel, along with the absolute per-channel differences. Its `position` is relative
to the compared surfaces; `candidate_position` and `reference_position` add each crop's origin
and point into the original images. The diagnostic appears as `worst_pixel` in JSON or as a
JSON-formatted `worst pixel:` line immediately before the verdict. It is reported on passing
comparisons too, including identical images, where the selected position is `(0, 0)`.
<a id="fidelity-report-channel-counts"></a>

Add `--channel-counts` to report, per channel, how many compared pixels exceed `--tolerance`
on that channel alone. `--json` adds the counts as a top-level `channel_counts` object
and text prints one `channel differing pixels (R, G, B, A)` line immediately before the
verdict, on passing and failing runs alike. A pixel can contribute to several counts (a
tint change moves three channels at once), so the counts overlap and must not be summed
into a union; `metrics.differing` already holds that union count.
<a id="fidelity-report-delta-histogram"></a>

Add `--delta-histogram` to report every compared pixel once, grouped by its
maximum absolute RGBA channel delta from 0 through 255. The complete distribution
includes zero and deltas at or below tolerance, and is independent of the gate:
JSON adds `delta_histogram` records (`delta` and `count`), while text prints the
same array as one `delta histogram:` line immediately before the verdict. The
option reports on passing and failing comparisons; omitting it skips the scan
and leaves the default output unchanged.
<a id="fidelity-report-delta-percentiles"></a>

Add `--delta-percentiles` to summarize that same maximum-RGBA-delta distribution
with nearest-rank p50, p95 and p99. Each rank is `ceil(p * pixel_count / 100)`;
the reported delta is the smallest bin whose cumulative count reaches that
rank. The complete compared crop, including zero and sub-tolerance deltas,
contributes. Percentiles are diagnostic and do not affect the gate. JSON adds a
`delta_percentiles` object and text prints the same object as one `delta percentiles:`
line immediately before the verdict. Percentiles alone omit histogram output;
both options share one histogram scan.
<a id="fidelity-report-channel-bias"></a>

Add `--channel-bias` to report the signed mean candidate-minus-reference byte delta for each
RGBA channel. Positive values mean the candidate trends higher; negative values mean it trends
lower. Opposite errors can cancel to zero even when pixels differ. This is a raw-byte diagnostic,
including RGB beneath transparent pixels, with missing alpha treated as opaque; it does not
composite or describe perceptual color error. JSON adds a `channel_bias` object and text prints
the same object immediately before the verdict. It is independent of tolerance and verdict.
<a id="fidelity-report-channel-maxima"></a>

Add `--channel-maxima` to report the largest absolute byte delta seen in each RGBA channel.
JSON adds a `channel_maxima` object and text prints a labelled RGBA maximum-delta line before
the verdict. It includes RGB bytes beneath transparent pixels, treats missing alpha as opaque,
and is independent of tolerance and verdict.
<a id="fidelity-report-horizontal-runs"></a>

Add `--difference-runs` to report maximal contiguous horizontal runs of pixels whose maximum
raw RGBA channel delta exceeds `--tolerance`. JSON adds row-major `difference_runs` records
with crop-relative `x`, `y` and `length`; text prints the same array after column bounds.
Runs end at every row boundary, and adjacent pixels stay in one run even when their delta
magnitudes differ. Crop origins translate these coordinates to source images. Output can grow
with the number of disjoint runs, so the option is opt-in; omitted runs skip the scan.
Add `--difference-run-count` to report the number of maximal horizontal mismatch runs as
`difference_run_count` in JSON or a `difference run count:` text line. It counts unfiltered
segments whose pixels' maximum raw RGBA channel delta exceeds `--tolerance`; alpha and RGB beneath
transparent pixels participate, and missing alpha is treated as 255. This is an interval count,
not a mismatching-pixel count: runs end at row boundaries, and adjacent mismatching pixels in one
row form one segment. Length cutoffs affect the optional run list but not the scalar. Combined
with `--difference-runs`, it reuses that scan; by itself it streams the count without retaining run
records. Requesting the run list also reports the count; with neither option the diagnostic is
omitted.
Pass `--min-difference-run-length N` with `--difference-runs` to omit completed runs shorter than
`N`. The inclusive cutoff filters the reported list after segmentation, so separated runs stay
separate and comparison metrics and longest-run summaries still use the complete mismatch data.
An empty requested list is reported as `[]`.
Pass `--max-difference-run-length N` with `--difference-runs` to omit completed runs longer
than `N`. The inclusive maximum combines with the minimum cutoff; a minimum above its paired
maximum is refused before any image read with a diagnostic naming both flags and both values.
Segmentation, comparison metrics and longest-run summaries still use the complete mismatch data.
Pass `--max-difference-runs N` with `--difference-runs` to report only the first N eligible
horizontal intervals in row-major order. This positive count cap is applied after the minimum
and maximum run-length filters; JSON adds `omitted_difference_runs`, and text prints
`omitted difference runs: N` immediately after the list, including zero. Run counts, longest-run
summaries, metrics and the verdict still use the full mismatch data. With a cap, intervals are
collected as they are scanned, retaining the requested page and the first longest interval;
count and longest summaries share that full-stream scan. Without a cap, the full run list is
retained. This bounds horizontal interval records only, not image buffers or vertical intervals.
Omitting the option adds no report field or line.
Pass `--difference-run-offset K` with that cap to skip K eligible intervals after both length
filters, in global row-major order. The offset must be a nonnegative ASCII integer; even zero
requires the cap. JSON adds `difference_run_offset`, and text prints `difference run offset: K`
immediately before the interval list. The omitted count includes skipped intervals and eligible
intervals beyond the page.
<a id="fidelity-report-vertical-runs"></a>

Add `--difference-column-runs` for maximal vertical runs, ordered left-to-right and then
top-to-bottom. JSON adds crop-relative `difference_column_runs` records with `x`, `y` and
`length`; text prints them after horizontal runs. Runs end at each column boundary and adjacent
pixels remain together across differing delta magnitudes. Crop origins translate their positions
to either source image. Output can grow with disjoint runs, so this scan is opt-in. Pass
`--min-difference-column-run-length N` with `--difference-column-runs` to omit completed runs
shorter than `N`. The inclusive cutoff filters after segmentation, preserving separated intervals,
comparison metrics and longest-column summaries. An empty requested list is reported as `[]`.
Pass `--max-difference-column-run-length N` with `--difference-column-runs` to omit completed runs
longer than `N`. The inclusive maximum combines with the minimum cutoff; a minimum above its
paired maximum is refused before any image read with a diagnostic naming both flags and both
values. Segmentation, metrics and longest-column summaries use the complete mismatch data.
Pass `--max-difference-column-runs N` to report only the first N eligible vertical intervals in
column-major order after both length filters. JSON adds `omitted_difference_column_runs`, and text
prints `omitted difference column runs: N` immediately after the vertical list, including zero.
Run counts, longest-column summaries, metrics and verdict still use the full mismatch data. With
a cap, the scan retains the requested page and first longest interval; count and longest summaries
share that scan. This bounds vertical interval records, not image buffers. Without a cap, the full
run list is retained. Omitting the option adds no report field or line.
Pass `--difference-column-run-offset K` with that cap to skip K eligible vertical intervals after
both length filters, in global column-major order. JSON adds `difference_column_run_offset`, and
text prints `difference column run offset: K` immediately before the vertical list. The omitted
count includes skipped intervals and eligible intervals beyond the page. Capped paging retains
the requested page and first longest interval rather than the full vertical run list.
Add `--difference-column-run-count` to report the number of maximal vertical mismatch runs as
`difference_column_run_count` in JSON or `difference column run count: N` in text. It counts
unfiltered segments, so length cutoffs affect the optional run list but not the scalar. Combined
with `--difference-column-runs`, it reuses that scan; by itself it streams the count without
retaining intervals. The diagnostic is omitted unless requested.
Add `--difference-centroid` to report the equal-weight mean `(x, y)` of pixels whose maximum raw
RGBA channel delta exceeds tolerance. Coordinates are crop-relative integer pixel indices; delta
magnitude does not affect weight. JSON includes `difference_centroid` and text prints it immediately
before the verdict, with `null` when no pixel differs. The scan is opt-in.
<a id="fidelity-report-scanline-counts"></a>

Add `--difference-rows` to count compared pixels beyond tolerance in each row. A pixel counts
once when any RGBA channel exceeds tolerance; missing alpha is opaque and RGB beneath
transparency is compared as stored. JSON adds a dense `difference_rows` array, and text prints
the same array immediately before the verdict. Its indices are crop-relative y coordinates, so
add the corresponding crop's y origin to locate a row in either source image. Zero rows are
included, and the diagnostic is omitted unless requested.
Add `--difference-columns` to count the same over-tolerance pixel union in each column. JSON
adds a dense `difference_columns` array, and text prints it immediately after the row diagnostic
when both are requested. Indices are crop-relative x coordinates; add the crop's x origin to
locate a column in either source image. Zero columns are included, and the diagnostic is omitted
unless requested.
Add `--difference-row-bounds` to report each compared row's smallest crop-relative horizontal
interval containing a pixel beyond tolerance. Rows without a mismatch are `null`; a nonempty
entry has `x` and `width`, and unchanged gaps inside the interval may be included. JSON adds a
dense `difference_row_bounds` array and text prints the same array immediately before the verdict.
Add the corresponding crop's x origin to locate an interval in either source image. The report
uses raw RGBA deltas, including RGB beneath transparency, and is omitted unless requested.
Add `--difference-column-bounds` to report each compared column's smallest crop-relative vertical
interval containing a pixel beyond tolerance. Columns without a mismatch are `null`; nonempty
entries have `y` and `height`, and unchanged gaps inside the interval may be included. JSON adds a
dense `difference_column_bounds` array and text prints it after row bounds and before the verdict.
Add the corresponding crop's y origin to locate an interval in either source image. The report
uses raw RGBA deltas, including RGB beneath transparency, and is omitted unless requested.
`make render` invokes the CLI
(`tools/render_surface.py`), which dispatches the lifecycle in `tools/render_workflow.py` to
produce a candidate render. Where the Plasma render tools are on `PATH`, `make check` renders the
window and byte-compares the title-bar strip (candidate `30,0,80,22` against reference
`30,25,80,22`), the close, zoom and collapse box regions, and the side and bottom border strips of
`aboutsystem_betawiki.png` (the zoom box against `systemprofiler_betawiki.png`), cropping each
region with the same `crop`/`compare` the fidelity tool uses. The applet face gate
(`tests/test_render_surface.py::TestRender`) pins the same capture's client face beside
those strips: the display field's black outline and flat interior and the keypad's
eighteen raised cells with their blended corner arcs, plus the flat gap rows and
columns between the cells, while the font-dependent label and digit ink is pinned
only by live-ink checks. The dialog renders the same
suite runs (`tests/test_render_surface.py::TestCheckboxDialogRender`,
`::TestComboboxDialogRender`, `::TestLineInputDialogRender`, `::TestMenuDialogRender`,
`::TestCalendarDialogRender`, `::TestColorDialogRender`, `::TestSliderDialogRender`,
`::TestTextboxDialogRender`, `::TestProgressbarDialogRender`, `::TestGtkDialogRender` and
`::TestInactiveDialogRender`)
open a `kdialog` warning box, chooser, input box, menu list, calendar, color picker, slider,
progress meter and text box and a `zenity` GTK 4 entry dialog, and byte-compare the
engine-drawn widgets with the shipped art described under
[Rendering a candidate](rendering.md), except that the menu gate pins the
engine-drawn `GenericFrame` item-view border runs, white interior and current-item
focus ring against measured pixel values. The inactive gate pins the two-window
capture's unfocused window: its decoration pixels — the `#555555` outline ring, the
recoloured client edge, the flat buttonless `#DDDDDD` bar and the `#777777` title ink —
against the shipped inactive art, beside the focused neighbour that proves the capture
holds two states. The GTK 4 dialog gate also pins the
rendered action-button row, Cancel button and CSD shell edge; the gates also check capture-level
invariants.

