# Sampling reference pixels

Back to [README](../README.md).

## Choosing a sampling mode

Choose a command based on the measurement you need. These commands use a beta reference
screenshot to demonstrate the sampler; it is not retail palette evidence. Choose coordinates
and region sizes for the surface you are measuring. Coordinates are absolute image pixels;
`--width` and `--height` set the sampled region starting at that coordinate, and both default
to 1. The reference PNGs are stored with Git LFS; materialize them as described in
[Validating the reference set](../README.md#validating-the-reference-set). Run `python3 tools/sample.py --help`
for the complete option list. JPEG reference screenshots are readable directly: the sampler
decodes a JPEG input once with ImageMagick's `convert` into a private temporary PNG and
samples it like any PNG, while `--alpha` and `--match-alpha` need a PNG input because JPEG
carries no alpha channel. For common refusals, see [Troubleshooting a sample](#troubleshooting-a-sample).

| Task | Command | Result |
| --- | --- | --- |
| Read one pixel | `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5` | RGB and hex values |
| Rank a small region's palette | `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --width 4 --height 4 --histogram --top-colors 3` | Up to three colors, ranked by count |
| [Page through a ranked palette](#sampling-palette-pages) | `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --width 4 --height 4 --histogram --top-colors 3 --color-offset 0 --json` | First three eligible colors and full-region totals |
| [Locate dominant palette colors](#sampling-palette-locations) | `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --width 4 --height 4 --histogram --top-colors 3 --color-bounds --color-positions --color-centroids --json` | Up to three ranked colors with absolute enclosing bounds, first row-major positions and mean pixel coordinates |
| Measure vertical color runs | `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --height 4 --runs` | Run colors, start coordinates, and lengths |
| [Page through border color runs](#sampling-run-pages) | `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --height 40 --runs --max-runs 5 --run-offset 0 --run-count --json` | First five vertical runs and the full-region run count |
| [Locate the longest border color run](#sampling-longest-run) | `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --height 40 --runs --longest-run --max-runs 5 --json` | Longest vertical run's absolute start, length and color, alongside up to five listed runs |
| Locate an exact color | `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --width 4 --height 4 --find-color '#63639C'` | Match count and enclosing bounds |
| [List matching color pixels](#sampling-match-coordinates) | `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --width 4 --height 4 --find-color '#63639C' --match-pixels 5 --json` | Up to five matching coordinates, count and enclosing bounds |
| [Locate the longest horizontal color match](#sampling-longest-horizontal-match) | `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --width 4 --height 4 --find-color '#63639C' --longest-match-run --json` | Longest horizontal matching segment's absolute start and length, or null |
| [Locate the longest vertical color match](#sampling-longest-vertical-match) | `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --width 4 --height 4 --find-color '#63639C' --longest-match-column-run --json` | Longest vertical matching segment's absolute start and length, or null |
| [Locate a near color within an RGB tolerance](#sampling-color-tolerance) | `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --width 4 --height 4 --find-color '#63639C' --color-tolerance 8 --json` | Match count and enclosing bounds for pixels whose red, green and blue each differ from the target by at most the tolerance, with the tolerance echoed in the report |
| [Measure a color's coverage and center](#sampling-match-coverage) | `python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --width 4 --height 4 --find-color '#63639C' --match-fraction --match-centroid --json` | Match count, enclosing bounds, the fraction of the requested region's pixels that match, and the mean absolute coordinate of the matching pixels (`null` when none match) |

For the next palette page, change `--color-offset 0` to `--color-offset 3`.
Offsets count eligible ranked colors, not pixel coordinates, and a later page
can be empty. Omitted pixels include skipped and trailing colors; paging limits
the displayed palette while counting still covers the full region.

The longest-run summary covers the complete scan before list caps, paging or run filters;
the longest segment need not appear in the displayed list. Ties retain the first run in scan order.

The coordinate list may be empty. Bounds can enclose nonmatching pixels, and a centroid is an
arithmetic mean that need not be a pixel of that color. The match-pixel cap limits displayed
coordinates, not the searched area.

The longest horizontal color match searches the complete rectangle, even when pixel or interval
lists are capped or filtered. Ties select the earliest row, then column. The summary omits the
full interval list unless `--match-runs` is requested separately. This target-color search is
distinct from the scanline color-run commands above, which summarize equal-color runs without
searching for a chosen color.

The longest vertical color match is the column-wise counterpart of the horizontal search
above. It searches the complete rectangle for the chosen color, reports one segment with
absolute start and length, and ties keep the lowest column, then the lowest row. It omits the
full vertical interval list unless `--match-column-runs` is requested separately. It is not the
scanline color-run command, which summarizes equal-color runs without searching for a chosen color.

Use the exact-color row for lossless PNG measurement. For a near color, the tolerance row
treats the tolerance as a per-channel maximum, not a combined distance: a pixel matches when
each of its red, green and blue values differs from the target by at most N. Alpha is ignored
unless `--match-alpha` is also given. The tolerance applies to every match report the search
produces, including coordinates, intervals and longest-match summaries. Beta reference evidence
is still not retail palette evidence, so treat the count as a demonstration rather than a claim.

The coverage and centroid reports use the same match predicate as the count. The fraction divides
by the full requested region area, including nonmatching pixels. The centroid uses pixel indices
with no half-pixel offset and need not land on a matching pixel. Both honor `--color-tolerance`
and `--match-alpha`, and `--match-pixels` truncates neither.

## Sampling options

Jump to an option family:

- [Pixel and rectangle samples](#pixel-and-rectangle-samples)
- [Histogram options](#histogram-options)
- [Color search options](#color-search-options)
- [Scanline run options](#scanline-run-options)

### Pixel and rectangle samples

`python3 tools/sample.py IMAGE X Y` prints the RGB value of one pixel of a reference
screenshot, in both forms the theme files use:

```
$ python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5
image: macos8.6-screenshots/boot2_betawiki.png  240x180
pixel (5, 5): 99,99,156  #63639C
```

The `99,99,156` triple is copied into a `.colors` file; the `#63639C` literal is copied
into an SVG or QML file. Pass `--width W` and/or `--height H` (default 1) to sample a
rectangle anchored at `(X, Y)`, printed row by row, so a whole title-bar column is one
command:

```
$ python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --height 2
image: macos8.6-screenshots/boot2_betawiki.png  240x180
region (5, 5) 1x2:
(5, 5): 99,99,156  #63639C
(5, 6): 99,99,156  #63639C
```

Pass `--json` to emit one structured JSON object instead. `image` retains the original image
argument, `image_width` and `image_height` describe the full image, `region` records the requested
rectangle, and `pixels` lists absolute coordinates in row-major order; a single pixel has the
same schema:

```sh
$ python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --json
{"image": "macos8.6-screenshots/boot2_betawiki.png", "image_width": 240, "image_height": 180, "region": {"x": 5, "y": 5, "width": 1, "height": 1}, "pixels": [{"x": 5, "y": 5, "rgb": [99, 99, 156], "hex": "#63639C"}]}
```

Pass `--alpha` for ordinary pixel and rectangle samples to include each pixel's
alpha byte (255 when the PNG has no transparency). RGB remains unchanged even
when alpha is zero. The flag adds `alpha` to JSON pixel records and `alpha=N`
to text pixel lines. With `--runs`, alpha is included in run equality, so
adjacent pixels merge only when both RGB and alpha match; JSON run records add
`alpha`, and text appends `alpha=N` after the run length. RGB under transparent
pixels is preserved without compositing. With `--histogram`, `--alpha` counts
RGBA colors, sorts ties by RGBA tuple, and adds `alpha` to JSON colors or
`alpha=N` after text counts; opaque images use alpha 255. The flag cannot be
combined with `--find-color`.

Coordinates are plain ASCII integers and `--width`/`--height` must be at least 1; a
coordinate or region outside the image, a missing file, or an unreadable PNG exits 2
with a diagnostic naming the coordinate, region, image size or path. A repository image
path that resolves outside the repository (a checked-in symlink) is refused by name
before it is read, so a private image's pixels cannot be sampled; a path outside the
repository is read as before.

### Histogram options

Pass `--histogram` to count the RGB colors in the requested rectangle instead
of listing its pixels. Counts sort from largest to smallest, with RGB tuple
order breaking ties; with `--alpha`, distinct RGBA tuples sort by RGBA order.
Combine it with `--json` for a `colors` array containing
`rgb`, `hex` and `count` fields:

```sh
$ python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --width 3 --height 2 --histogram --json
{"image":"macos8.6-screenshots/boot2_betawiki.png","image_width":240,"image_height":180,"region":{"x":5,"y":5,"width":3,"height":2},"colors":[{"rgb":[99,99,156],"hex":"#63639C","count":6}]}
```

Add `--top-colors N` with `--histogram` to limit the displayed palette while
still counting the complete region. It adds `total_colors` (the distinct-color
count before truncation) and `omitted_pixels` (region pixels not represented
in emitted colors) to JSON; text appends the same totals. Both fields appear
even when the limit includes every color.

Counts retain their full-region values, and ties keep ascending RGB ordering.
This limits report size; decoding and counting still cover the complete
region. Without the option, the complete histogram is printed.

<a id="sampling-palette-pages"></a>

Add `--color-offset K` with `--top-colors N` to page through the ranked
histogram after named-color exclusions and count/fraction filters. Ranking is
descending count, then ascending RGB or RGBA tuple; explicit zero selects the
first page. Named-color inclusion and exclusion, plus count and fraction
filters, run before paging. JSON adds `color_offset` and text prints
`color offset: K`. Totals and fractions retain their full-region meanings, and
omitted pixels include filtered colors, skipped colors and trailing colors.
Selection stores at most `min(K + N, distinct color count)` entries.

```sh
python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 0 0 --histogram --top-colors 2 --color-offset 1 --json
```

Add `--min-color-count N` with `--histogram` to omit colors whose count is
below N. The cutoff is inclusive and runs before `--top-colors`. JSON and text
include `total_colors` and `omitted_pixels` whenever either option is used;
the distinct-color total is measured before filtering, and omitted pixels
include filtered and truncated colors. Fractions retain the full-region
denominator, while spatial diagnostics describe only emitted colors. A cutoff
larger than the region area returns an empty palette and marks the full region
omitted.

Add `--max-color-count N` with `--histogram` to omit colors occurring more
than N times. The inclusive cutoff combines with minimum count, minimum
fraction and named-color exclusions before `--top-colors`; contradictory
minimum and maximum counts are refused when the minimum exceeds the maximum. Explicit use reports the
original `total_colors` and `omitted_pixels`, even when every color remains.
Fractions still use the full region area, and spatial diagnostics describe
only emitted colors.

Add `--min-color-fraction F` with `--histogram` to omit colors whose share of
the requested region is below F (0 through 1 inclusive). Filtering runs before
`--top-colors` and combines with `--min-color-count`; both predicates must pass.
The share uses the full region area, and explicit filtering reports the original
`total_colors` and `omitted_pixels`. At F=0 the palette is unchanged.

Add `--max-color-fraction F` with `--histogram` to omit colors whose share of
the requested region is above F (0 through 1 inclusive). This inclusive cutoff
combines with minimum fraction, count filters and named-color exclusions before
`--top-colors`. A minimum above the maximum is refused before image reading. The
share uses the full region area, including pixels later omitted by other
filters. Explicit use reports the original `total_colors` and `omitted_pixels`,
and spatial diagnostics describe only emitted colors.

For color count, color fraction, scanline run length, horizontal match-run
length and vertical match-run length, a supplied minimum above its paired
maximum exits 2 before image reading with an error naming both flags and
values. Equal bounds are valid and inclusive; valid windows with no qualifying
values still produce an empty result.

```sh
python3 tools/sample.py missing.png 0 0 --runs --min-run-length 3 --max-run-length 2
python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --width 4 --runs --min-run-length 4 --max-run-length 4
```

Add repeatable `--exclude-color RRGGBB` with `--histogram` to omit named RGB
colors before minimum-count, minimum-fraction and top-color selection. Values
accept six hexadecimal digits with optional `#` and are case-insensitive.
With `--alpha`, every opacity variant is excluded, including stored RGB under
zero alpha. The original distinct-color total and full-region denominator are
preserved; explicit exclusions report totals even when a named color is absent.
Omitted pixels include exclusions and other filters without double counting.
Spatial diagnostics apply only to emitted colors.

Add repeatable `--include-color RRGGBB` with `--histogram` to retain only named
RGB colors. Values accept six hexadecimal digits with optional `#` and are
case-insensitive. Inclusion is applied before exclusions, count/fraction
filters and top-color pagination; exclusions win when a color appears in both
lists. With `--alpha`, each opacity variant of an included RGB value is
retained independently, including stored RGB beneath zero alpha. The original
distinct-color total and full-region denominator are preserved, and explicit
inclusion reports totals even when it matches no colors or the full palette.
Omitted pixels include every filtered color, and spatial diagnostics apply
only to emitted colors.

Add `--color-fractions` with `--histogram` to add each emitted color's share
of the complete requested region (`count / width / height`). JSON color
records gain a numeric `fraction`; text appends `fraction=VALUE`. Fractions
use ordinary Python float formatting and are not rounded. With `--top-colors`,
the denominator still includes pixels omitted from the displayed palette.

Add `--color-cumulative-fractions` with `--histogram` to report how much of
the complete requested region the displayed palette explains as colors
accumulate. Each emitted color gains its running pixel count divided by the
full region area, accumulated in report order with integer counts so the last
color on a complete page reaches exactly `1.0`. Coverage is page-local:
excluded, filtered, skipped and trailing colors never enter the numerator.
JSON color records gain a numeric `cumulative_fraction`; text appends
`cumulative_fraction=VALUE` after the optional `fraction` and before
position and centroid fields. The option works independently of
`--color-fractions`; with `--top-colors`, the denominator still includes
pixels omitted from the displayed page.

<a id="sampling-palette-locations"></a>

Add `--color-bounds` with `--histogram` to report each emitted color's
smallest enclosing rectangle, using absolute image coordinates. The bounds
include disconnected occurrences and do not imply a solid rectangle. With
`--top-colors`, bounds are calculated only for colors shown; counts and the
top-color summary still cover the full region. `--alpha` keeps different
opacity values separate. JSON color records gain a `bounds` object, and text
appends `bounds=X,Y,W,H` after each color's existing fields.

Add `--color-positions` with `--histogram` to report the first row-major
occurrence of each emitted color, using absolute image coordinates. JSON color
records gain a `position` object with `x` and `y`; text appends
`position=X,Y`. Cropping limits the search to the requested region, and
`--alpha` keeps opacity variants separate. When combined with `--color-bounds`,
both diagnostics share one positioned traversal.

Add `--color-centroids` with `--histogram` to report each emitted color's
arithmetic mean pixel coordinate in absolute image coordinates. JSON color
records gain a `centroid` object with `x` and `y`; text appends
`centroid=X,Y`. Coordinates use integer pixel indices without a half-pixel
offset. Cropping and `--alpha` determine the sampled group, and `--top-colors`
limits reported colors while retaining all occurrences of each emitted color
in its centroid. Centroids share one positioned traversal with bounds and
positions.

Add `--row-color-counts` with `--histogram` to report how many distinct colors
each region row holds. The array lists one count per crop row in top-to-bottom
order, grouped like the emitted colors (RGB alone, or RGBA with `--alpha`, which
keeps opacity variants apart while a transparent pixel still contributes its
stored RGB). Counts cover the complete region, so displayed-palette filters and
`--top-colors` paging never change them. JSON adds `row_color_counts`, and text
adds a `row color counts:` line after the color list and before the totals.

Add `--column-color-counts` with `--histogram` to do the same for region
columns, one count per crop column in left-to-right order. JSON adds
`column_color_counts`, and text adds a `column color counts:` line after the
optional `row color counts:` line. Omitting both options adds neither count,
neither line and no traversal.

### Color search options

Pass `--find-color '#63639C'` to count exact RGB matches and report their
smallest enclosing bounds. Bounds use absolute image coordinates, include
disconnected matches, and do not imply that every pixel inside the rectangle
matches. Add `--json` for a `match` object with `rgb`, uppercase `hex`, `count`
and `bounds` (`null` when absent):

```sh
python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 0 0 --width 240 --height 180 --find-color '#63639C' --json
```

<a id="sampling-color-tolerance"></a>

Add `--color-tolerance N` to include pixels whose red, green and blue channel
differences are each at most N (0–255). This helps locate colors affected by
rendering or capture variation; alpha is ignored. The option requires
`--find-color`. When supplied, including as `--color-tolerance 0`, its value
appears in the text and JSON match report; omitting it preserves exact-match output.
Add `--match-alpha N` (0–255) to require an exact PNG alpha value as well as the RGB
predicate. It requires `--find-color`, preserves RGB bytes beneath transparency, and
uses alpha 255 for images without transparency. JSON adds `alpha` to `match`; text
prints `alpha: N` after the optional tolerance. RGB tolerance never relaxes this alpha
match. This option filters matches and can be combined with `--color-tolerance`, but
not with `--alpha`.

<a id="sampling-match-coordinates"></a>

Add `--match-pixels N` (1–1000) with `--find-color` to list the first N
matching coordinates in row-major order. Coordinates are absolute image
positions within the requested region. Matching count and bounds still cover
the full region; JSON adds `pixels` and `omitted_pixels` to `match`, while
text prints the retained coordinates and omitted count. The option uses the
same RGB tolerance and exact-alpha filters as the match count.

Add `--match-pixel-offset N` with `--match-pixels` to list a later page of the
same row-major match sequence. The offset counts matching pixels, not scanned
pixels; `--match-pixel-offset 0` selects the original first page. JSON adds
`pixel_offset` when explicitly requested, and text prints `pixel offset:` before
the coordinate list. `omitted_pixels` includes both skipped matches and matches
after the current page. Count, bounds and optional match diagnostics still cover
the full region, and an offset at or beyond the match count returns an empty
coordinate list.

<a id="sampling-match-coverage"></a>

Add `--match-fraction` with `--find-color` to report the match count divided
by the full requested region area. JSON adds numeric `fraction` to `match`;
text prints `fraction:` after `count:`. It uses the same RGB tolerance and
exact-alpha filters, and `--match-pixels` does not truncate its numerator.

Add `--match-centroid` with `--find-color` to report the arithmetic mean of
matching pixel coordinates. JSON adds `match.centroid` with absolute `x` and
`y` values, or `null` when no pixels match; text prints `centroid: X,Y` or
`centroid: none` after bounds. Pixel indices are used without a half-pixel
offset. Tolerance and exact-alpha filters apply, and `--match-pixels` does not
truncate the centroid calculation.

Add `--match-runs` with `--find-color` to report maximal contiguous horizontal
segments matching the same RGB tolerance and exact-alpha predicate. JSON adds
`match.runs` records with absolute `x`, `y` and `length`; text prints the same
records on a `matching runs:` line. Segments are ordered by row then column,
stop at each row boundary, and merge adjacent matches even when their RGB
values differ within tolerance. The report covers the full region independently
of `--match-pixels`; potentially large output is opt-in.

Add `--match-run-count` with `--find-color` to report the number of maximal
horizontal matching segments as `match.run_count` in JSON or a
`matching run count:` text line. It counts the full region using the same RGB
tolerance and exact-alpha predicate, independent of coordinate paging and run
length filters. The run list remains omitted unless `--match-runs` is requested.

Add `--min-match-run-length N` with `--match-runs` to omit horizontal match
segments shorter than `N` pixels. The inclusive cutoff filters only the
reported list; match counts and other full-region diagnostics, including the
longest-run summary, still use every matching pixel. A cutoff above the longest
segment reports an empty `match.runs` array (or `matching runs: []` in text).

Add `--max-match-run-length N` with `--match-runs` to omit horizontal match
segments longer than `N` pixels. The inclusive cutoff filters completed
segments; match counts and summaries still use the full search. Minimum and
maximum cutoffs combine inclusively. A minimum above the maximum is refused
before image reading.

Add `--max-match-runs N` with `--match-runs` to report only the first `N`
eligible horizontal intervals in row-major order after both length filters.
Pass `--match-run-offset K` with `--max-match-runs` to skip K eligible intervals
after both length filters and report the next page. JSON adds `match.run_offset`
and text prints `matching run offset: K` immediately before the list. The omitted
count in `match.omitted_runs` includes skipped and trailing eligible intervals;
text prints `omitted matching runs: N` immediately after the interval list,
including zero. Match counts and longest-run summaries still use the full search.
When a cap is supplied, completed intervals are filtered and paged as they are
collected, so retained horizontal interval storage is bounded by the cap.
Without a cap, matching intervals are retained as before.
Omitting the offset adds no `match.run_offset` field or text line.

Add `--match-column-runs` with `--find-color` to report maximal contiguous
vertical segments using the same match predicate. JSON adds `match.column_runs`
with absolute `x`, `y` and `length`; text prints the records on a
`matching column runs:` line after any horizontal runs. Segments are ordered
by column then row, stop at each column boundary, and merge adjacent tolerance
matches even when their RGB values differ. They cover the full region
independently of `--match-pixels`; potentially large output is opt-in.

Add `--match-column-run-count` with `--find-color` to report the number of
maximal vertical matching segments as `match.column_run_count` in JSON or a
`matching column run count:` text line. It counts the full region with the same
RGB tolerance and exact-alpha predicate, independent of coordinate paging and
column-run length filters. The interval list remains omitted unless
`--match-column-runs` is requested; when both options are used, the count
appears immediately before the list.

Add `--min-match-column-run-length N` with `--match-column-runs` to omit
vertical match segments shorter than `N` pixels. The inclusive cutoff filters
only the reported list; match counts and diagnostics, including the longest
vertical-run summary, still use every matching pixel. A cutoff above the
longest segment reports an empty `match.column_runs` array (or
`matching column runs: []` in text).

Add `--max-match-column-run-length N` with `--match-column-runs` to omit
vertical match segments longer than `N` pixels. The inclusive maximum filters
only the reported list and combines with the minimum cutoff. A minimum above
the maximum is refused before image reading; match counts and longest-run
diagnostics still cover the full search for valid windows.

Add `--max-match-column-runs N` with `--match-column-runs` to report only the
first `N` eligible vertical intervals in column-major order, after both
inclusive length filters. JSON adds `match.omitted_column_runs`; text prints
`omitted matching column runs: N` immediately after the list, including zero.
Counts, longest-run summaries and other search measurements still cover the
full region. When a cap is supplied, the search runs one extra column-major
predicate scan over the already-decoded region, and completed vertical
intervals are filtered and paged as that scan collects them, so retained
vertical interval storage is bounded by the cap.

Pass `--match-column-run-offset K` with `--match-column-runs` and
`--max-match-column-runs` to skip K eligible vertical intervals in column-major
order after both length filters. JSON adds `match.column_run_offset`; text prints
`matching column run offset: K` before the list. The omitted count includes
skipped and trailing eligible intervals. Paging requires the cap and rides the
same bounded capped collection, so skipped eligible intervals are not
retained.

Add `--match-rows` with `--find-color` to count matching pixels in each row of
the requested region. JSON adds a dense `match.rows` array and text prints the
same array on a `matching rows:` line after interval reports. Index zero is the
region's first row; rows with no matches are included. Counts use the same RGB
tolerance and exact-alpha predicate and cover the full region regardless of
`--match-pixels`. The diagnostic is omitted unless requested.

Add `--match-columns` with `--find-color` to count matching pixels in each
column of the requested region. JSON adds a dense `match.columns` array and
text prints the same array on a `matching columns:` line after any matching
rows line. Index zero is the region's first column; columns with no matches
are included. Counts use the same RGB tolerance and exact-alpha predicate and
cover the full region regardless of `--match-pixels`. The diagnostic is
omitted unless requested.

Add `--match-row-bounds` with `--find-color` to report the smallest horizontal
interval enclosing matches on each row. JSON adds dense `match.row_bounds`
entries: `null` for an empty row, otherwise absolute `x` and inclusive `width`;
text prints the same array on a `matching row bounds:` line. Disconnected
matches enclose intervening pixels. The report covers the full region regardless
of `--match-pixels`, uses the same tolerance and exact-alpha predicate, and is
omitted unless requested.

Add `--match-column-bounds` with `--find-color` to report the smallest vertical
interval enclosing matches in each column. JSON adds dense `match.column_bounds`
entries: `null` for an empty column, otherwise absolute `y` and inclusive
`height`; text prints the same array on a `matching column bounds:` line.
Disconnected matches enclose intervening pixels. The report covers the full
region regardless of `--match-pixels`, uses the same tolerance and exact-alpha
predicate, and is omitted unless requested.

<a id="sampling-longest-horizontal-match"></a>

Add `--longest-match-run` with `--find-color` to report the longest contiguous
horizontal matching segment. JSON adds `match.longest_run` with absolute `x`,
`y` and `length`, or `null` when there are no matches; text prints
`longest matching run: X,Y,LENGTH` or `longest matching run: none`. Ties keep
the earliest row-major segment. The summary uses the same tolerance and exact
alpha filters, covers the full region regardless of `--match-pixels`, and does
not emit the full run list unless `--match-runs` is also requested.

<a id="sampling-longest-vertical-match"></a>

Add `--longest-match-column-run` with `--find-color` to report the longest
contiguous vertical matching segment. JSON adds `match.longest_column_run`
with absolute `x`, `y` and `length`, or `null` when there are no matches; text
prints `longest matching column run: X,Y,LENGTH` or
`longest matching column run: none`. Ties prefer greater length, then the
lowest x and y. The summary uses the same tolerance and exact-alpha filters,
covers the full region regardless of `--match-pixels`, and does not emit the
full column-run list unless `--match-column-runs` is also requested.

### Scanline run options

Pass `--runs` to group adjacent equal RGB values along one row or column.
Add `--alpha` to group by RGBA instead, distinguishing transparency boundaries
even when neighboring pixels have the same RGB values; an image without alpha
uses 255 for every run. RGB values remain uncomposited, including beneath
fully transparent pixels.
With `--height 1` (the default), traversal is horizontal; otherwise use
`--width 1` for a vertical scan. A two-dimensional region is rejected unless
`--run-axis horizontal` or `--run-axis vertical` selects parallel scanlines.
Horizontal scans visit rows top-to-bottom and pixels left-to-right; vertical
scans visit columns left-to-right and pixels top-to-bottom. Runs never cross
scanline boundaries, even when adjacent scanlines end and begin with equal colors.
For example, `--width 4 --height 3 --runs --run-axis vertical` reports four
independent top-to-bottom column scans. Add
`--json` to return the `axis` and traversal-ordered `runs`, each with its
absolute starting coordinate, `length`, `rgb` and `hex`:

```sh
$ python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --width 4 --runs --json
{"image":"macos8.6-screenshots/boot2_betawiki.png","image_width":240,"image_height":180,"region":{"x":5,"y":5,"width":4,"height":1},"axis":"horizontal","runs":[{"x":5,"y":5,"length":4,"rgb":[99,99,156],"hex":"#63639C"}]}
```

Use `--height` for a vertical scan:

```sh
python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5 --height 4 --runs
```

Pass `--min-run-length N` with `--runs` to omit completed color runs shorter than `N` pixels.
The inclusive cutoff is applied independently within each scanline; omitted runs do not join
separated runs of the same color. A minimum cutoff of 1 keeps the unfiltered result.
Pass `--max-run-length N` to omit completed runs longer than `N`; it combines
inclusively with the minimum cutoff after segmentation and does not join separated runs.
A maximum at least as large as the scanline keeps the unfiltered result.
If both bounds are supplied and the minimum exceeds the maximum, the sampler
exits 2 with an error naming both flags and values before reading the image.
Pass repeatable `--run-color RRGGBB` to retain runs whose RGB value is named;
values accept an optional `#` and are case-insensitive. Color selection follows
segmentation, so distinct adjacent selected colors and separated runs stay
separate; it combines with the inclusive length filters. With `--alpha`, runs
are still segmented by RGBA while selection matches RGB regardless of opacity.
Pass repeatable `--exclude-run-color RRGGBB` to omit runs with a named RGB
value after segmentation; values accept an optional `#` and are case-insensitive.
Exclusion ignores opacity and wins when the same value is also selected with
`--run-color`. It combines with the inclusive length filters and requires
`--runs`.

Pass `--run-count` with `--runs` to add a scalar run total alongside the list:
JSON gains a top-level `run_count` and text prints `run count: N` immediately
after the `axis:` line (after the `longest run:` line when `--longest-run` is
also given). The count is the complete unfiltered number of scanline
runs each scan produces — counted before `--run-color` selection,
`--exclude-run-color` and the inclusive length filters, including zero when a
scan yields none — with runs of different scanlines counted separately and the
count covering all scanlines of the region. What `runs` lists does not change;
omitting the flag omits the JSON key, the text line and the counting. The flag
requires `--runs`.

Pass `--scanline-run-counts` with `--runs` to add one run count per scanline
alongside the list: JSON gains a top-level `scanline_run_counts` and text
prints `scanline run counts: N, N, ...` immediately after the optional
`run count` line, before the run list. Each count is the same unfiltered
per-scanline total `--run-count` sums — taken before `--run-color` selection,
`--exclude-run-color` and the inclusive length filters — listed in scanning
order, top-to-bottom rows for the horizontal axis and left-to-right columns
for the vertical; every scanline yields at least one run, so the list is never
empty for a nonempty region. Filters change what `runs` lists but never the
counts; omitting the flag omits the JSON key, the text line and the counting.
The flag requires `--runs`.

<a id="sampling-longest-run"></a>

Pass `--longest-run` with `--runs` to add the dominant scanline run as a
scalar: JSON gains a top-level `longest_run` mirroring one `runs` entry (`x`,
`y`, `length`, `rgb`, `hex`, plus `alpha` under `--alpha`) and text prints
`longest run: X,Y,LENGTH` immediately after the `axis:` line. The summary
covers every scan run of the region before `--run-color` selection,
`--exclude-run-color` and the inclusive length filters, resolving ties in
scanning order — top-to-bottom rows for the horizontal axis, left-to-right
columns for the vertical, and the earliest run within a scanline. Every
scanline yields at least one run, so the summary is never null. What `runs`
lists does not change; omitting the flag omits the JSON key, the text line and
the comparison. The flag requires `--runs`.

<a id="sampling-run-pages"></a>

For a longer vertical border scan, start with `--max-runs 5 --run-offset 0 --run-count --json`
as in the chooser above. Change the offset to 5 for the
next page. Offsets count eligible run slots, not pixels; a later page can be
empty. The cap limits displayed records, while the scan and requested
unfiltered run count cover the full region.

Pass `--max-runs N` with `--runs` to display only the first N eligible runs
across the complete scan in its existing row or column order. Named color
selection and exclusion plus inclusive run-length filters apply before this
prefix limit. JSON adds `omitted_runs`, and text prints `omitted runs: N`
after the displayed runs, including zero when the limit covers every eligible
run. This caps the retained report list; the scan continues so
`--run-count`, `--scanline-run-counts` and `--longest-run` retain their
unfiltered full-region meanings. Without the option, output is unchanged.
The option requires `--runs` and is distinct from `--max-run-length`, which
filters runs by their individual pixel lengths.

Pass `--run-offset K` with `--runs` and `--max-runs N` to page through eligible
runs without printing earlier pages. Color selection, exclusion and inclusive
length filters apply before the offset. The offset counts skipped eligible runs;
`omitted_runs` counts both skipped runs and eligible runs after the displayed
page. JSON adds `run_offset`, and text prints `run offset: K` before the run
list. An offset beyond the end returns an empty page. The option requires
`--max-runs` and is nonnegative.

## Troubleshooting a sample

| Symptom | What to do |
| --- | --- |
| The file is an unmaterialized Git LFS pointer | Follow [Validating the reference set](../README.md#validating-the-reference-set), including `git lfs install` and `git lfs pull`, to fetch the image bytes. |
| The path is missing or unreadable | Check the path named in the diagnostic and confirm you can read the file. |
| The pixel or region is outside the image | Correct `X`, `Y`, `--width` or `--height` to fit the image dimensions in the report. |
| JPEG decoding says `convert` is missing | Install ImageMagick and ensure its `convert` command is on `PATH`; PNG inputs need no converter. |
| An alpha option was requested for JPEG | Omit `--alpha` or `--match-alpha`, or use a PNG that actually has alpha. JPEG conversion cannot recover transparency that JPEG does not store. |
| An option dependency or min/max window is refused | Add the required mode or cap described in the [option families](#sampling-options), or correct the bounds so the minimum does not exceed the maximum. |

Reports and `--help` return status 0. A valid sample with no matching or retained values is still a successful empty report; an out-of-image pixel or region is refused instead. Handled usage, read and decode refusals return status 2. These are sampler statuses; fidelity comparison failures have their own status.
