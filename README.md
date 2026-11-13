# kde-macos8.6-theme

## Initial prompt

<!-- tumwater:prompt:start -->
A KDE Plasma 6 theme to have the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming.
<!-- tumwater:prompt:end -->

## Status

<!-- tumwater:status:start -->
Pre-alpha: the Platinum theme covers KDE/Qt, GTK 3 and GTK 4, Firefox chrome and content, and cursor surfaces.

Open work is tracked in PLANS.md (planned features), BUGS.md (known bugs), and QUESTIONS.md (decisions needed).
<!-- tumwater:status:end -->

<a id="navigation"></a>

## Contents

- [Prerequisites](#prerequisites)
- [Installing](#installing)
- [Generating the wallpaper](#generating-the-wallpaper)
- [Reference screenshots](#reference-screenshots)
- [Validating the reference set](#validating-the-reference-set)
- [Sampling reference pixels](#sampling-reference-pixels)
- [Fidelity checking](#fidelity-checking)
- [Running checks](#running-checks)
- [Invariants](#invariants)
- [Development team](#development-team)

## Prerequisites

| Task | Requirements |
| --- | --- |
| Use the KDE theme | A KDE Plasma 6 session. Kvantum is a separately installed widget engine; when it is absent, widgets use another style. `kvantummanager` selects the theme in Kvantum. |
| Install packages | GNU Make and standard Linux utilities, including `install` and `flock`. `make install` copies theme files into the data home; it does not change the running user's settings. See [Installing](#installing). |
| Apply the theme | Python 3.10 or newer; `lookandfeeltool`, `plasma-apply-colorscheme`, `plasma-apply-desktoptheme`, `kwriteconfig6` and `kreadconfig6`. `make apply` installs the files and changes the running user's settings. |
| Select the GTK theme alone | Python 3.10 or newer, the package-install utilities above, and writable data and config homes. Run `make apply-gtk`; restart GTK applications. See [Installing](#installing) for selection and backup details. |
| Select the cursor theme alone | Python 3.10 or newer, the package-install utilities above, and `plasma-apply-cursortheme` on `PATH`. Run `make apply-cursor`; aggregate `make apply` skips cursor selection with a note when that tool is missing. See [Installing](#installing) for details. |
| Install Firefox sheets alone | Python 3.10 or newer and an existing writable Firefox profile, found automatically or specified as `FIREFOX_PROFILE=/absolute/profile`. Run `make install-firefox`; aggregate `make apply` skips this step with a note when it finds no profile. See [Installing](#installing) for profile selection and restart details. |
| Render headlessly | Python 3.10 or newer; `dbus-run-session`, `kwin_wayland`, `plasma-apply-colorscheme`, `plasmawindowed` and `spectacle`. Dialog render modes also require `kdialog`; the GTK dialog render mode requires `zenity` instead; the desktop render mode requires `plasmashell`; the splash render mode requires `ksplashqml`. The default applet render also needs the `org.kde.plasma.calculator` applet (Debian packages it in `plasma-widgets-addons`); missing, the render refuses with exit 2 before any session, naming the applet id and the searched locations. See [Rendering a candidate](docs/rendering.md). |
| Run optional GTK 4 probes | Xvfb, `xvfb-run`, `xauth`, and Python GTK 4 introspection bindings. See [Running checks](#running-checks) for isolated commands. |
| Materialize reference images | Git LFS; run `git lfs install` and `git lfs pull`. See [Validating the reference set](#validating-the-reference-set). |
| Sample JPEG screenshots | ImageMagick's `convert` on `PATH`; PNG inputs need no extra tool. The sampler refuses a JPEG input without it. See [Sampling reference pixels](#sampling-reference-pixels). |

## Installing

### Quick start

See [Prerequisites](#prerequisites) for requirements. Choose one route:

```sh
make install
```

This copies the theme files without selecting them. To install and select Platinum for the
running user, use the alternative below. It changes user settings and may replace personal GTK 4
CSS after backing it up; [restoring personal GTK 4 CSS](#restoring-personal-gtk-4-css) explains
how. Existing panels are preserved; applying the optional desktop layout is a separate choice.

```sh
make apply
```

Restart GTK applications and Firefox to pick up their styles; the splash changes at the next
login. For GTK alone, use `make apply-gtk`. See [Removing the theme](#removing-the-theme) to
undo the installation.

### Installation details

[docs/installing.md](docs/installing.md) holds the details: which files each package installs into the data home, what `make apply` changes and selects in the running session, and how the GTK, Firefox and cursor selections, their backups and their removals work. See [Installation details](docs/installing.md).

### Rendering a candidate

[docs/rendering.md](docs/rendering.md) holds the render modes: what `make render` captures and refuses in each of the calculator, dialog, desktop and splash modes, which tools and applet each mode requires, and what every dialog, desktop and splash render gate pins there. See [Rendering a candidate](docs/rendering.md).

### Staging packages

To inspect installed package paths without selecting the theme in your session, stage an install
into a scratch root:

```sh
stage_dir=$(mktemp -d)
make install DESTDIR="$stage_dir" XDG_DATA_HOME=/usr/share INSTALL_PACKAGES='color-scheme gtk'
```

The scheme lands at `$stage_dir/usr/share/color-schemes/MacOS8.colors` and the GTK 3 and GTK 4
sheets and assets land under `$stage_dir/usr/share/themes/org.macos8.desktop/` (`index.theme`,
`gtk-3.0/gtk.css`, `gtk-4.0/gtk.css` and `assets/`). `/usr/share` here is the data-home suffix
inside the scratch root — `DATA_HOME` is `DESTDIR` followed by `XDG_DATA_HOME` — not a request to
install into the live system.

`INSTALL_PACKAGES` takes a space-separated list of the package families the Makefile knows:
`color-scheme`, `look-and-feel`, `desktop-theme`, `aurorae`, `wallpaper`, `icon-theme`,
`kvantum`, `fonts` and `gtk`. Omit the selector and the install copies every family; name a
subset and the install copies only that subset into the scratch root. A subset install is
additive: staging another family into the same scratch root later copies its files beside what
is already there and deletes nothing from earlier installs.

`make install` copies files into the destination and changes no selection or setting anywhere;
applying a selection is `make apply`'s job, which refuses to run with a non-empty `DESTDIR`
because a staged tree is for inspection, not for pointing the running session at. When you are
done inspecting, remove the scratch root yourself (`rm -rf -- "$stage_dir"`); nothing else
tracks it.

### Removing the theme

Choose another global theme in System Settings, then clear the individual selections before
deleting the installed packages. These commands remove this theme's selections or files; they do
not restore earlier settings or backups.

| Command | Effect and remaining action |
| --- | --- |
| `make remove-gtk` | Clears this theme's GTK selection and marker CSS. Existing GTK backups remain; restart GTK applications. |
| `make remove-firefox` | Removes this theme's sheets and preference block from the active profile. To target another profile, use `FIREFOX_PROFILE=/absolute/profile make remove-firefox`. Restart Firefox. |
| `make remove-cursor` | Removes this theme's cursor link but leaves the cursor selection. If it still names `org.macos8.desktop`, reset it with `plasma-apply-cursortheme breeze_cursors`. |
| `make remove-kvantum` | Clears only this theme's Kvantum engine selection (`[General] theme` in `kvantum.kvconfig`). A foreign theme name and the rest of the file remain; restart Qt applications. |
| `make uninstall` | Deletes installed theme packages and leaves user configuration in place. It also removes the theme-id directories it emptied under `themes/` (the shared directory and its `Kvantum/` parent); a directory still holding a file the theme did not install survives. This removes directories the install created, not user configuration. Run after clearing selections; it does not remove the cursor link or change keyboard mappings. |

To reselect the installed Plasma settings without installing packages or applying the other
theme surfaces, run `make apply-plasma`. Install first with `make install`; it requires Python
3.10+, `lookandfeeltool`, `plasma-apply-colorscheme`, `plasma-apply-desktoptheme` and
`kwriteconfig6`. It preserves panels, attempts Kvantum selection when available (a non-default
`${XDG_DATA_HOME}` prints a note naming the limitation, as the Installing section describes),
and the splash change appears at the next login.

#### Restoring personal GTK 4 CSS

When `make apply` replaced a nonempty foreign `gtk-4.0/gtk.css`, it first copied that stylesheet
beside itself and printed a note naming both paths:

```
apply_gtk: note: backed up <your gtk-4.0/gtk.css> to <the new backup> before replacing it
```

`make remove-gtk` keeps them: it deletes only the marker-led sheet this theme wrote and leaves
a foreign `gtk.css` alone, so finish that removal successfully before restoring anything.

Backup candidates are `gtk-4.0/gtk.css.bak` and, when several replacements happened, the
unused-name siblings `gtk.css.bak.1` and up, all under your config home (`$XDG_CONFIG_HOME` when
it is an absolute path, otherwise `$HOME/.config`). A numbered suffix only means the plain name
was already taken when another apply made a backup — it is the next unused filename, not a
chronology, and the largest number is not the newest edition. Read the candidates and choose by
contents.

Copy the chosen backup back at the console; `cp -i --` preserves the backup and prompts before
replacing an existing destination. Quote every path so spaces survive:

```sh
cp -i -- "/absolute/path/to/gtk-4.0/gtk.css.bak" "/absolute/path/to/gtk-4.0/gtk.css"
```

If a foreign `gtk.css` survived the removal, it may hold edits newer than any backup, so read it
before replacing it. Restart running GTK applications afterward so they reload the restored
stylesheet.

This restores the user CSS alone: it does not restore the theme name your `gtk-3.0/settings.ini`
or `gtk-4.0/settings.ini` carried before applying (`make remove-gtk` clears its selection and
leaves the rest of the file alone), so choose a preferred GTK theme separately when you want
one.

## Generating the wallpaper

`python3 tools/make_wallpaper.py` rewrites the wallpaper package's images in
theme/wallpapers/org.macos8.desktop/contents/images/ as a solid `#CCCCCC` tile, an original
neutral placeholder rather than a crop of the reference desktop. The output is deterministic,
so re-running it rewrites identical bytes. It refuses an images directory that resolves outside
the repository — a checked-in symlink — so the generated images stay inside the wallpaper
package. `PLACEHOLDERS.md` tracks this temporary artwork.

## Reference screenshots

`macos8.6-screenshots/` is the visual reference set for this theme: 30 images for **Mac OS 8.6**
(released 1999-05-10) — retail screenshots and beta builds, two 8.1 supplements, one 8.5 supplement and two
photographs — collected from the internet and used as the source of truth when matching menu bar,
window chrome, widget metrics, icons and colour palette in the Plasma 6 port. They are reference
material only — the theme does not ship them.

| Surface | Count | Files |
| --- | --- | --- |
| Desktop | 5 | `desktop_betawiki.png`, `desktop_betawiki86b9.png`, `desktop_fandom.png`, `desktop_archiveorg.jpg`, `desktop_archiveorg8.6hd.png` |
| Boot / splash | 5 | `boot_betawiki.png`, `boot2_betawiki.png`, `boot_archiveorg.jpg`, `bootwhite_archiveorg.jpg`, `splash_macbase.gif` |
| Welcome / first boot / installer | 5 | `welcome_betawiki.png`, `welcome_tomo197707.png`, `firstboot_betawiki.png`, `setup_betawiki.png`, `setup_emaculation.png` |
| About / System Profiler | 7 | `about_betawiki*.png` (3), `aboutsystem_betawiki*.png` (2), `systeminfo_betawiki.png`, `systemprofiler_betawiki.png` |
| Finder / dialogs / apps | 3 | `finder_archiveorg.jpg`, `opendialog_macrumors86.jpg`, `apps_macrumors8.6.jpg` |
| Zoomed window chrome supplement | 2 | `browsers_zoomed_toastytech81.png`, `infocenter_zoomed_toastytech81.png` (Mac OS 8.1) |
| Photos of real hardware | 2 | `boot_powerbookphoto_macrumors.jpg`, `welcome_crtphoto_macrumors.jpg` |
| Non-8.6 supplement | 1 | `sherlock_fandom.jpg` (Mac OS 8.5) |

`sources.txt` records the origin URL and a version label for every file.

- **Labels are evidence-based.** A file is labelled 8.6 only when the version string is legible in
  the image itself (or the source states it). Beta/alpha builds (`8.6a3c2`, `8.6b3`, `8.6b9`,
  `8.6b2c4L8`) and the 8.5 Sherlock supplement are marked as such — they show chrome that differs
  from retail and must not be used as retail reference. One exception is
  recorded: `aboutsystem_betawiki.png` is a beta build, but its title bar, side
  borders and close/collapse boxes are pixel-identical to the retail
  `systemprofiler_betawiki.png`, so it is used as an evidence-backed
  window-chrome proxy where the set has no other lossless window-chrome
  screenshot. That equality is pinned by
  `tests/test_aurorae_reference_equivalence.py`, and the render gate's
  bottom-border crop stays on the beta because the System Profiler window's
  bottom differs (its sunken content field and bottom scrollbar).
- **Two entries are photographs**, not screenshots: real Macs running 8.6, useful for CRT
  colour/gamma and physical bezel context only.
- **Binary assets are stored with Git LFS** (see `.gitattributes`); run `git lfs install` after
  cloning.
- Images are third-party material kept for reference and attribution; copyright remains with the
  original authors.

## Validating the reference set

`.github/workflows/ci.yml` runs `make check` and `make check-references` on
pushes and pull requests, on Python 3.13 with a checkout with Git LFS images
materialized; the Makefile's targets still require Python 3.10 or newer at run
time. Its check job also installs the render gate's five Plasma tools
(`dbus-run-session`, `kwin_wayland`, `plasmawindowed`, `spectacle`,
`plasma-apply-colorscheme`), the `kdialog` client the gate's checkbox, combobox, line-edit, menu,
calendar, color, progressbar, slider and textbox dialog renders open, and the `zenity` client its
GTK
dialog render opens, so `make check` reaches the rendered-pixel gates, including the kdialog and
GTK dialog renders. Their
software-renderer guard still skips captures in the workflow environment; installed tools
are prerequisites, not proof that rendered pixels were compared. See [Running checks](#running-checks)
for the guard conditions and GPU-host guidance. Run those same commands locally for parity
with the workflow's check steps.

`sources.txt` is the provenance record for the images. After adding or renaming a screenshot, run
`python3 tools/check_references.py`: it fails if the record and the files on disk disagree (a
missing file, an unmaterialized Git LFS pointer, a file whose bytes are not a PNG/JPEG/GIF/WebP
image, an image with no entry, a malformed or duplicate entry) or if a source URL is not a
well-formed absolute URL (a bad scheme, raw whitespace or control characters, an authority
naming no host, or a malformed path, query or fragment, except for a `file://` URL).
`python3 tools/check_references.py --self-test` exercises the checker itself.
`make check-references` runs the self-test and then the repository check; it needs the Git LFS
images materialized, so it stays separate from `make check`.

### Troubleshooting the reference set

Each problem is printed on its own line. A record problem names its line as
`macos8.6-screenshots/sources.txt:<line>`; a file problem names the image instead.
Map a diagnostic to its next action:

| Diagnostic | Cause and next action |
| --- | --- |
| `... is an unmaterialized Git LFS pointer ...` | The file holds an LFS pointer, not the image bytes. Run `git lfs install` and `git lfs pull`, then `make check-references` again. |
| `... does not exist in .../macos8.6-screenshots/` | A declared file is absent — an incomplete checkout or a wrong filename in the record. Check the checkout, and compare the declared filename against the file on disk; fix the record only if the filename is genuinely wrong. Do not delete the provenance record to silence this: the record is the attribution trail for the set. |
| `image has no entry in sources.txt` | A file in the reference directory has no provenance record. Add one line for it: `filename \| source URL \| version label`. The filename is a bare name inside `macos8.6-screenshots/` (no path), the URL cites where the image came from, and the label is the evidence-based version string — see [Reference screenshots](#reference-screenshots) for the retail/beta labelling policy rather than restating it here. |
| `expected 3 fields ...`, `empty field in entry`, `duplicate entry for ...`, `source URL ...` | The record line is malformed, duplicate, or cites a URL that is not a well-formed absolute URL. Fix the record line the diagnostic names; it prints `sources.txt:<line>`, and a duplicate names the line of the first entry too. |
| `... is not a PNG, JPEG, GIF or WebP image; it may be an HTML error page or a truncated download` | The file's leading bytes match no known image signature. Inspect the download for an HTML error response or truncation and obtain the intended reference again; changing the file's extension does not change its bytes. |
| `... ends without the PNG IEND trailer`, `... ends without the JPEG EOI marker`, `... ends without the GIF trailer byte`, `... declares N RIFF bytes but holds M`; it may be a truncated download | The file's leading bytes match a known image format, but the stream stops before that format's end marker, so the download was cut short yet still looks like an image to the signature check. This diagnostic is a bounded structural check — the file's last bytes and, for WebP, its declared RIFF size — not a full decode. Obtain the intended reference again with a complete download and re-run the check. |
| `... points outside .../ (a symlink escape)` | A symlink in the reference set leads outside the reference directory, or the reference directory itself resolves outside the repository. Replace the symlink with the real file or directory it should name. |

A file that cannot be read at all — a read error, a non-UTF-8 `sources.txt`, a `sources.txt`
over the 1 MiB record limit, or a missing `sources.txt` — is reported directly; restore the
file it names.

The checker inspects signatures, not pixels: a pass means the bytes match a known image
format and every record line parses. It does not establish that an image decodes completely,
that a retail-labelled image is authentic, or that any pixel matches — those are the
[sampling](#sampling-reference-pixels) and [fidelity](#fidelity-checking) gates' work, on the
evidence each image actually carries. `--self-test` exercises the checker against its built-in
fixtures; it validates the checker, not the repository images. Run it alone or through
`make check-references`, which follows it with the repository check.

Exit statuses differ between callers. Direct `python3 tools/check_references.py` returns 0 when
the check or self-test passes (and for `--help`), 1 when the reference set has problems or a
self-test case misbehaves, and 2 for an unrecognized argument. GNU Make reports its own
recipe-failure status for `make check-references`; the checker's problem lines above appear in
the recipe's output either way.

## Sampling reference pixels

### Choosing a sampling mode

Choose a command based on the measurement you need. These commands use a beta reference
screenshot to demonstrate the sampler; it is not retail palette evidence. Choose coordinates
and region sizes for the surface you are measuring. Coordinates are absolute image pixels;
`--width` and `--height` set the sampled region starting at that coordinate, and both default
to 1. The reference PNGs are stored with Git LFS; materialize them as described in
[Validating the reference set](#validating-the-reference-set). Run `python3 tools/sample.py --help`
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

### Sampling options

Jump to an option family:

- [Pixel and rectangle samples](#pixel-and-rectangle-samples)
- [Histogram options](#histogram-options)
- [Color search options](#color-search-options)
- [Scanline run options](#scanline-run-options)

#### Pixel and rectangle samples

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

#### Histogram options

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

#### Color search options

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

#### Scanline run options

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

### Troubleshooting a sample

| Symptom | What to do |
| --- | --- |
| The file is an unmaterialized Git LFS pointer | Follow [Validating the reference set](#validating-the-reference-set), including `git lfs install` and `git lfs pull`, to fetch the image bytes. |
| The path is missing or unreadable | Check the path named in the diagnostic and confirm you can read the file. |
| The pixel or region is outside the image | Correct `X`, `Y`, `--width` or `--height` to fit the image dimensions in the report. |
| JPEG decoding says `convert` is missing | Install ImageMagick and ensure its `convert` command is on `PATH`; PNG inputs need no converter. |
| An alpha option was requested for JPEG | Omit `--alpha` or `--match-alpha`, or use a PNG that actually has alpha. JPEG conversion cannot recover transparency that JPEG does not store. |
| An option dependency or min/max window is refused | Add the required mode or cap described in the [option families](#sampling-options), or correct the bounds so the minimum does not exceed the maximum. |

Reports and `--help` return status 0. A valid sample with no matching or retained values is still a successful empty report; an out-of-image pixel or region is refused instead. Handled usage, read and decode refusals return status 2. These are sampler statuses; fidelity comparison failures have their own status.

## Fidelity checking

`python3 tools/fidelity.py CANDIDATE REFERENCE` compares a rendered PNG surface against a
reference screenshot and reports mean absolute error, per-channel mean absolute error
(R, G, B, A), RMSE, worst per-channel delta and where it occurs, and the fraction of
differing pixels.
Pass `--candidate-crop X,Y,W,H` to crop the candidate and `--crop X,Y,W,H` to select a
surface region of the reference.
If a comparison refuses to run, see [Troubleshooting a comparison](#troubleshooting-a-comparison).
A JPEG candidate or reference is decoded once through ImageMagick's `convert` into a
private temporary PNG before the comparison, so the reference set's JPEG screenshots are
comparable directly; other non-PNG formats keep the decode refusal.

### Capturing a candidate

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
see [Prerequisites](#prerequisites) for the render tools. To allow a slower calculator paint,
increase the settle wait and set a longer timeout (which must exceed settle):

```sh
python3 tools/render_surface.py --settle 12 --timeout 120 calculator.png
```

A longer wait does not guarantee a successful capture. Compare the candidate with the relevant
reference surface using the [fidelity checker](#fidelity-checking); use its crop options to
compare a region rather than assuming a full capture matches a reference screenshot.

### Troubleshooting a render

| Symptom | Check and next action |
| --- | --- |
| The diagnostic names a missing or unstartable executable. | Repair that executable or its `PATH` entry, then rerun the same command. The first missing required tool is named; a present but unstartable `make` or `dbus-run-session` is also diagnosed. |
| The capture is entirely black. | The window did not paint before capture. Check whether the paint needs more time and increase `--settle`; use the [slower-paint example](#capturing-a-candidate), with `--timeout` longer than `--settle`. A longer wait does not guarantee a capture. |
| The render timed out. | Check [Prerequisites](#prerequisites) and increase `--timeout` only as needed, keeping it longer than `--settle`. A missing `org.kde.plasma.calculator` applet is no longer an undiagnosed timeout cause: its own preflight refusal exits 2 before any session and names the applet id. |
| The render session exits nonzero. | Inspect the diagnostic's printed session log tail for the failing command. The log is in a temporary scratch directory and is removed with the session, so it is not a persistent report. |

Direct `python3 tools/render_surface.py` invocations return 2 for usage or preflight errors
(including missing tools and invalid timeout settings), and 1 for workflow failures. GNU Make
reports its own recipe-failure status for `make render`. Failure diagnostics include a bounded
log tail when a log is available. The software-renderer skip described in
[Running checks](#running-checks) applies to the automated pixel gates; it is separate from a
direct render failure.

### Comparing a region

When render tools are available and the software-renderer guard does not trigger, the
calculator title-strip gate compares these corresponding 80x22 rectangles:

```sh
python3 tools/fidelity.py calculator.png macos8.6-screenshots/aboutsystem_betawiki.png --candidate-crop 30,0,80,22 --crop 30,25,80,22
```

Use [Rendering a candidate](docs/rendering.md) to produce `calculator.png`; see
[Capturing a candidate](#capturing-a-candidate) for capture options, and
[Validating the reference set](#validating-the-reference-set) to materialize the images.
These coordinates belong to the documented calculator/title-strip gate, not arbitrary windows.
For another surface, choose corresponding rectangles independently in the two images; they must
have equal dimensions. `aboutsystem_betawiki.png` is the documented beta window-chrome proxy:
its relevant chrome is pixel-identical to the retail reference, as pinned by the
retail-equivalence test. It is not general evidence for retail palette values.

### Troubleshooting a comparison

| Symptom | Check and next action |
| --- | --- |
| The reference is an unmaterialized Git LFS pointer. | Follow [Validating the reference set](#validating-the-reference-set) to install Git LFS and materialize the image. |
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

### Choosing a diagnostic

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

### Diagnostic reference

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
[Rendering a candidate](docs/rendering.md), except that the menu gate pins the
engine-drawn `GenericFrame` item-view border runs, white interior and current-item
focus ring against measured pixel values. The inactive gate pins the two-window
capture's unfocused window: its decoration pixels — the `#555555` outline ring, the
recoloured client edge, the flat buttonless `#DDDDDD` bar and the `#777777` title ink —
against the shipped inactive art, beside the focused neighbour that proves the capture
holds two states. The GTK 4 dialog gate also pins the
rendered action-button row, Cancel button and CSD shell edge; the gates also check capture-level
invariants.

## Running checks

Run the full project check before submitting changes. Focused runs help with iteration, but do not
replace the full check.

| Scope | Command |
| --- | --- |
| Full project check | `make check` |
| Matching test modules | `make check CHECK_PATTERN='test_colorscheme*.py'` |
| One test class | `make check CHECK_TESTS=test_colorscheme.TestAnchors` |
| Serial discovery | `make check CHECK_PARALLEL=0` |

The hosted check job sets `LIBGL_ALWAYS_SOFTWARE=1`, so its render capture gates skip even
when their tools are installed. A green check with those skips does not establish rendered-pixel
equality. The guard is environment-based, not a KWin-version probe: it triggers when
`LIBGL_ALWAYS_SOFTWARE=1`, or when `MESA_LOADER_DRIVER_OVERRIDE` or `GALLIUM_DRIVER` contains
`llvmpipe`, `softpipe`, `swrast` or `zink` (case-insensitive). The skip reason cites a fix in
KWin 6.8, but upgrading KWin alone does not bypass this guard. To exercise the capture gates,
use a GPU-backed host with the documented render tools and without software-forcing variables.
The isolated headless rendering commands remain available under [Rendering a candidate](docs/rendering.md).

The GTK 4 button, notebook, progressbar, scale, indicator, spin-field and view-census probes skip during routine checks. To opt in
without using your desktop display, run each probe under Xvfb:

```sh
env -u DISPLAY -u WAYLAND_DISPLAY xvfb-run -a -- env PLATINUM_RUN_GUI_TESTS=1 make check CHECK_TESTS=test_gtk4_button_probe.TestGtk4ButtonProbe.test_button_faces_render
env -u DISPLAY -u WAYLAND_DISPLAY xvfb-run -a -- env PLATINUM_RUN_GUI_TESTS=1 make check CHECK_TESTS=test_gtk4_notebook_probe.TestGtk4NotebookProbe.test_notebook_tab_faces_render
env -u DISPLAY -u WAYLAND_DISPLAY xvfb-run -a -- env PLATINUM_RUN_GUI_TESTS=1 make check CHECK_TESTS=test_gtk4_progressbar_probe.TestGtk4ProgressbarProbe.test_progressbar_faces_render
env -u DISPLAY -u WAYLAND_DISPLAY xvfb-run -a -- env PLATINUM_RUN_GUI_TESTS=1 make check CHECK_TESTS=test_gtk4_scale_probe.TestGtk4ScaleProbe.test_scale_faces_render
env -u DISPLAY -u WAYLAND_DISPLAY xvfb-run -a -- env PLATINUM_RUN_GUI_TESTS=1 make check CHECK_TESTS=test_gtk4_scrollbar_probe.TestGtk4ScrollbarProbe.test_scrollbar_faces_render
env -u DISPLAY -u WAYLAND_DISPLAY xvfb-run -a -- env PLATINUM_RUN_GUI_TESTS=1 make check CHECK_TESTS=test_gtk4_indicators_probe.TestGtk4IndicatorsProbe.test_mixed_indicators_draw_black_dashes
env -u DISPLAY -u WAYLAND_DISPLAY xvfb-run -a -- env PLATINUM_RUN_GUI_TESTS=1 make check CHECK_TESTS=test_gtk4_spin_probe.TestGtk4SpinProbe.test_spin_field_renders_the_mirrored_etch_in_rtl
env -u DISPLAY -u WAYLAND_DISPLAY xvfb-run -a -- env PLATINUM_RUN_GUI_TESTS=1 make check CHECK_TESTS=test_gtk_view_census
```

`xvfb-run -a` allocates and cleans up a separate virtual X server. Unsetting inherited
`DISPLAY` and `WAYLAND_DISPLAY` before starting it prevents these commands from selecting the
desktop display. Missing GTK 4 introspection bindings can still cause a probe to skip for lack of
capability; setting the opt-in variable alone does not mean the probe ran.

Reference image validation is separate: see [Validating the reference set](#validating-the-reference-set)
for `make check-references` and its Git LFS materialization requirement.

## Invariants

`docs/invariants.md` states, per `theme/` subsystem and for the fidelity gate, the guarantee a
surface must keep and the test that pins it. Read the matching row before changing a surface, and
update it in the same change when a guarantee moves. `tests/support/invariants.py` keeps the register
and the repository in step.

## Development team

This theme is developed by a tumwater team of AI roles. How many roles run at once is a tumwater
setting, not a file in this repository: `maxConcurrent` in the primary checkout's `tumwater.json`
(alongside any `maxConcurrentPerProvider` cap) is the most model runs in flight across all roles
at once, merges included, with the director's own runs sitting outside it; it defaults to 6. A
role cannot change that concurrency setting, so the operator sets it from the primary checkout, for example
`tumwater config set maxConcurrent 6` (requested 2026-10-18: run six roles at once).

The project check is `make check`, without `CHECK_PATTERN` or `CHECK_TESTS` overrides.
From the primary checkout, operators can inspect the configured check with
`tumwater doctor check --json` (the `check` row should read `ok`) and
`tumwater status --json` (the output should have no `noDeclaredCheck`). If a clone has no
declared check, configure it from the primary checkout with
`tumwater config set check.command 'make check'`.
The separate reference-image validation remains `make check-references`.
