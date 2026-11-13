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

[docs/sampling.md](docs/sampling.md) holds the sampler's user guide: the sampling modes, the option families and
troubleshooting. The most common command samples one pixel:
`python3 tools/sample.py macos8.6-screenshots/boot2_betawiki.png 5 5` prints its RGB and hex values. See
[Sampling reference pixels](docs/sampling.md).

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
