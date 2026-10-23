# Fixed bugs

Fixed bugs, newest first, moved here by tumwater from BUGS.md's `## Fixed`. This file
only grows: search it with grep, or read one entry by its line range. Never read it whole.

## Fixed

### A FIFO at either Firefox profile-discovery INI file blocks the install (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`make install-firefox` without `--profile` reads `installs.ini` and `profiles.ini`
under `$HOME/.mozilla/firefox` to find the active profile. `tools/firefox_profile.py`
opened each with `Path.open`, so a FIFO at either path waited forever for a writer and
the install hung with no diagnostic.

**Reproduce:** create a fresh `$HOME`, put a FIFO at
`.mozilla/firefox/installs.ini` (or `profiles.ini`), and run
`python3 tools/install_firefox.py` with `HOME` pointing there. The process blocks
instead of exiting 2.

**Fix:** `_read_ini` now opens the file through the shared
`containment.open_regular_binary`, which opens with `O_NONBLOCK` and checks the
opened descriptor, and wraps a non-regular file, an unreadable file and invalid
UTF-8 as a by-name `ConfigError`. A missing INI still reads as absent and a regular
file still parses the same way. The regression test runs the install in a bounded
child for a FIFO at each INI path.

**Validation gap:** no-fake — Confirming the hang needed a FIFO fixture plus a bounded child process, neither of which the suite had.

### A FIFO at a Firefox profile file blocks the install forever (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`tools/install_firefox.py` read a profile's `chrome/userChrome.css` and `user.js` with
`Path.read_bytes()`. A FIFO or device at either path makes that open wait for a writer (or stream
forever), so `make install-firefox` never returned and printed no diagnostic. Placing a FIFO at
either file reproduces it: the install stops in `_read_text` before writing the other file.

The fix opens both files through the shared containment regular-file reader
(`open_regular_binary`), which opens with `O_NONBLOCK` and inspects the opened descriptor, so a FIFO
or device is refused by name with exit status 2 instead of blocking. A missing file still reads as
absent, and a regular file's bytes are decoded as UTF-8 without newline translation, so its line
endings stay intact. The regression test
`tests/test_firefox_install.py::TestRemove::test_a_fifo_at_either_profile_file_is_refused_without_blocking`
runs the install in a child for a FIFO at each profile file; both cases hit the child-process
timeout before the fix and pass after it.

**Validation gap:** no-fake — confirming it needed a FIFO fixture and a bounded child process the
suite did not have, so the blocked open left no diagnostic; the closest tag is no-fake, and the new
test now supplies that fixture.

### The cursor generator test patches a removed `_write_atomic` symbol (found by the plan role 2026-10-23) — fixed 2026-10-23 by the bugfix role

The entry was filed before an earlier coverage commit repaired the cursor-write test. On this tree,
the cursor-theme module's failed-write test reads and patches the imported shared atomic-write
helper, which the cursor generator imports from the atomic-write module and calls for every cursor
write; the test no longer references the removed private helper name. Running the cursor-theme test
module under the project's check passes that test, so there is nothing left to fix: the entry
describes a failure the earlier commit had already repaired.

**Validation gap:** no-repro — the reported failure could not be reproduced because the test now
patches the existing shared atomic-write helper instead of the removed name.

### Fidelity drops alpha, so a fully transparent candidate passes the byte-exact gate (found by the qa role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`python3 tools/fidelity.py CANDIDATE REFERENCE` compares only each pixel's red, green and blue
bytes. A candidate that matches the reference's RGB but not its alpha therefore reports zero
error and passes the default no-differing-pixel gate. Reproduction (any 8-bit RGBA PNG encoder;
this uses ImageMagick, and the two images differ only in alpha):

```
$ tmp=$(mktemp -d) && cd "$tmp"
$ magick -size 2x2 xc:'rgba(0,0,0,1)' PNG32:opaque.png
$ magick -size 2x2 xc:'rgba(0,0,0,0)' PNG32:clear.png
$ python3 <repo>/tools/fidelity.py clear.png opaque.png
candidate: clear.png  2x2
reference: opaque.png  2x2
pixels compared: 4
mean absolute error: 0.0000
per-channel MAE (R, G, B): 0.0000 0.0000 0.0000
RMSE: 0.0000
max channel delta: 0 at (0, 0)
differing pixels: 0 / 4 (0.000000)
PASS: max-mae=unset max-frac=unset tolerance=0
$ echo $?
0
```

Expected: the default gate fails with exit 1 and a nonzero differing-pixel count, because every
pixel's alpha differs by 255; README's "Fidelity checking" says a run passes only when no pixel
differs from the reference, and docs/invariants.md's tooling row says the gate passes only when no
pixel differs beyond its tolerance. Actual: exit 0 and a byte-exact report for a fully
transparent surface. If RGB-only comparison is intentional, the README and that invariant need to
say alpha is not compared; as written a user cannot tell a transparent surface from the reference.

Suspected cause: `tools/png/read.py`'s `decode_png` drops the alpha byte of a color-type-6 image
(`drop_alpha`) before unfiltering, and `read_png` returns the `Image` type that
`tools/png/image.py` describes as an 8-bit RGB buffer, so `tools/fidelity_metrics.compare` never
sees alpha. The RGBA decoder (`read_rgba`) exists for the cursor PNGs but the fidelity CLI uses
the RGB path.

**Validation gap:** none — the dropped alpha bytes are deterministic and the CLI reproduces
the pass offline.

### The PNG tRNS-order test names an unimported `_PNG_SIGNATURE` (found by the plan role 2026-10-23) — fixed 2026-10-23 by the dedupe role

`tests/test_png_malformed.py::TestTrnsColorTypeValidation.test_truecolor_trns_before_suggested_plte_is_refused`
built its blob by concatenating `_PNG_SIGNATURE`, but the module no longer
imported that name: the change that moved the stream helpers into
`tests/support/png_fixtures.py` removed the import while one use remained, so
the test failed with `NameError: name '_PNG_SIGNATURE' is not defined`. The
entry originally named the sibling `test_palette_trns_before_plte_is_refused`,
which already used `png_stream()` and passed. The repair landed in
the dedupe change `a4e85fc6`, which converted the remaining truecolor stream to
the shared `png_stream()` helper instead of importing the private constant.

**Validation gap:** none — the missing import failed deterministically before `a4e85fc6` converted the truecolor stream to `png_stream()`.

### A truecolor tRNS before a suggested PLTE is accepted (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

The chunk collector treated a tRNS before PLTE as illegal only for a color
type 3 palette image, so a truecolor (color type 2) image whose suggested
palette followed its tRNS still decoded. The PNG spec says a tRNS chunk must
follow the PLTE chunk, if any, not only the palette an indexed image indexes.
Repro from a hand-built 1x1 color type 2 stream with tRNS, then PLTE, then
IDAT: `decode_png` returned `b'\x01\x02\x03'` and `decode_rgba` returned
`(1, 1, b'\x01\x02\x03\x00')`; both now raise "PNG has a tRNS chunk before
its PLTE chunk; tRNS must follow the PLTE chunk, if any". A tRNS with no PLTE
in the stream, and a tRNS after the suggested PLTE, still decode. `check_trns`
now refuses the ordering whenever a palette is present, and a color type 3
image with no PLTE keeps its missing-palette diagnosis. Test:
`tests/test_png_malformed.py::TestTrnsColorTypeValidation::test_truecolor_trns_before_suggested_plte_is_refused`
(fails both subtests without the fix).

**Validation gap:** unclear-invariant — the code and its comments stated the
ordering was legal for a truecolor suggested palette, so the spec rule had to
be reconstructed; the invariant is recorded in docs/invariants.md.

### A palette image with tRNS before PLTE is accepted (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

The PNG specification requires a `tRNS` chunk to follow `PLTE`. `tools/png/stream.py`'s
`collect_chunks` collects the two payloads independently and checks only that both precede
`IDAT`, so a color type 3 image carrying `tRNS` before `PLTE` decodes on both the RGB and RGBA
paths. Reproduce by assembling the chunks by hand:
`_PNG_SIGNATURE + ihdr_chunk(1, 1, 3) + _chunk(b"tRNS", bytes([0, 128])) + _chunk(b"PLTE",
bytes([255, 0, 0, 0, 255, 0])) + _chunk(b"IDAT", zlib.compress(bytes([0, 0]))) +
_chunk(b"IEND", b"")`; both `decode_png` and `decode_rgba` return the image. Suspected cause:
no ordering guard for `tRNS` against an earlier-or-absent `PLTE`; the missing-`PLTE` diagnosis
for color type 3 must keep winning when no palette appears at all.

**Validation gap:** no-fake — no fixture could emit a `tRNS` before `PLTE`, so confirming the
acceptance needed a hand-assembled chunk stream from the lower-level `_chunk` helpers.

### A PLTE chunk on a greyscale color type is silently ignored (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`tools/png/stream.py`'s `collect_chunks` validated a PLTE chunk's length but neither decoder
checked whether the header's color type could carry a palette. The PNG specification makes PLTE
required for color type 3, optional for the truecolor types 2 and 6, and prohibited for the
greyscale types 0 and 4. Reproduce with `make_png(1, 1, [bytes([7])], color_type=0,
palette=bytes([255, 0, 0]))`: both `decode_png` and `decode_rgba` returned the image instead of
refusing the non-conformant chunk.

`tools/png/stream.py` now exports `check_plte(palette, color_type)`, which refuses a palette on
color types 0 and 4 and leaves the optional truecolor suggested palette and the required palette
image accepted. `_decode_image` calls it right after `parse_ihdr`, next to `check_trns`, so both
decode paths refuse the same file.

**Validation gap:** unclear-invariant — the chunk reader's docstrings described framing checks but nowhere stated that PLTE legality depends on the header's color type, so that rule had to be reconstructed from the PNG specification; the invariant is recorded in docs/invariants.md.

### tRNS validation ran only on the RGBA decode path (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`tools/png/read.py`'s `decode_rgba` validated a tRNS chunk's length while it
applied alpha, but `decode_png` discarded the chunk without looking at it and
neither path checked whether the header's color type could carry one. A
truecolor PNG with a 5-byte tRNS decoded as RGB but raised on the RGBA path;
an overlong palette tRNS did the same; and a tRNS chunk on an alpha color type
(4 or 6), which the PNG specification forbids outright, was accepted by both.
Reproduce with `make_png(1, 1, [bytes([1, 2, 3, 4])], color_type=6,
trns=b"\x00\x01\x00\x02\x00\x03")`: `decode_rgba` returned the image instead
of raising.

`tools/png/stream.py` now exports `check_trns`, which refuses a tRNS chunk on
color types 4 and 6, a greyscale or truecolor tRNS whose length is not exactly
2 or 6 bytes, and a palette tRNS outside 1 to the palette's entry count.
`_decode_image` calls it right after `parse_ihdr`, so both decoders reject the
same malformed transparency (a palette image with no PLTE still gets the
missing-palette diagnosis).

**Validation gap:** unclear-invariant — the rule that tRNS is valid only for color types 0, 2 and 3 with color-type-specific lengths was stated nowhere and pinned only indirectly by the RGBA path, so it had to be reconstructed from the PNG specification; the invariant is recorded in docs/invariants.md.

### A non-empty IEND payload is silently accepted (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`tools/png/chunks.py`'s `iter_chunks` checked an IEND chunk's length and CRC
but not its payload, so `png.decode_png`, `png.decode_rgba` and the file
readers accepted an IEND carrying data. The PNG specification gives IEND an
empty data field, so a conformant reader refuses that file; ours decoded it as
if the extra bytes did not exist. Reproduce by replacing a valid PNG's final
`IEND` chunk with `_chunk(b"IEND", b"x")`: the decoder returned the image
instead of raising.

`iter_chunks` now refuses a non-empty IEND by name and offset before yielding
it ("PNG IEND chunk at offset N has M payload bytes; IEND's data field must be
empty"), so every consumer of the chunk stream sees the same diagnosis.

**Validation gap:** unclear-invariant — the IEND-empty-data-field guarantee was not stated in the module docstring or pinned by a test, so it had to be reconstructed from the PNG specification; the invariant is recorded in docs/invariants.md.

### PNG chunks after IEND are silently ignored (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`tools/png/stream.py`'s `collect_chunks` stopped at the first IEND, so a
complete chunk after it — an ancillary `tEXt`, a second `IDAT`, even a second
`IHDR` — was dropped and `png.decode_png` returned the image. The same held
for 1-7 trailing bytes too short to be a chunk header. Reproduce by appending
`_chunk(b"tEXt", b"x")`, a second IDAT, or a few bytes of a chunk to a valid
PNG's bytes: the decoder returned the image instead of raising.

The reader now keeps walking after IEND and refuses any later complete chunk
by name ("… after IEND; IEND must be the last chunk"), while the framing
iterator still yields those chunks to callers that want them. A trailing
fragment after IEND, which the iterator's framing loop cannot see as a chunk,
is refused there by name ("… trailing bytes after IEND that do not form a
chunk; IEND must be the last chunk").

**Validation gap:** unclear-invariant — the IEND-last guarantee was not stated in the module or pinned by a test, so it had to be reconstructed from the PNG specification; the reconstructed invariant is recorded in docs/invariants.md.

### Non-consecutive IDAT chunks and PLTE/tRNS after IDAT are accepted (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`tools/png/stream.py`'s `collect_chunks` concatenated every IDAT payload and
kept a PLTE or tRNS payload wherever it appeared, so a malformed stream whose
IDAT chunks are separated by another chunk, or whose PLTE/tRNS follows the
image data, decoded as if its chunk order were valid. Reproduce by building a
1x1 RGB PNG whose IDAT is split around a tEXt chunk, or a palette PNG whose
PLTE chunk is moved after IDAT: `png.decode_png` returned the image instead of
raising.

The guard now closes the IDAT run at the first non-IDAT chunk and refuses a
later IDAT, and refuses a PLTE or tRNS once image data has started, matching
the PNG chunk-order rules while still allowing ancillary chunks after the last
IDAT.

**Validation gap:** unclear-invariant — the chunk-order guarantee was neither stated in the module nor pinned by a test, so it had to be reconstructed from the PNG specification; the reconstructed invariant is recorded in docs/invariants.md.

### GTK settings edits rewrite a foreign file's line endings (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`gtk_settings.set_theme_name` and `remove_theme_name` split a settings file on every boundary `str.splitlines` recognises and rejoined the lines with `"\n"`, so editing the `gtk-theme-name` key in a CRLF, lone-CR or mixed-ending `settings.ini` rewrote every foreign line's terminator, contradicting the module's promise and `docs/invariants.md` that every foreign line is preserved.

**Reproduction.** `set_theme_name("[Settings]\r\ngtk-font-name=Lato 10\r\n", "org.macos8.desktop")` returned `'[Settings]\ngtk-font-name=Lato 10\n...'`; `tests/test_gtk_settings.py::TestLineEndings` now pins every foreign line's ending through replacement, insertion, appending and removal.

**Validation gap:** none — a scratch call to `set_theme_name` showed the rewritten endings immediately; no shim or real run was needed, though no existing test covered a CRLF file.

### The PNG decoder accepts trailing bytes after the IDAT zlib stream (found by the bugfix role 2026-10-23) — fixed 2026-10-23 by the bugfix role

`decode_png` and `decode_rgba` inflate the IDAT stream and check its output length, end marker and adler32, but never inspect `zlib.decompressobj.unused_data`. A PNG whose IDAT payload is a valid zlib stream followed by arbitrary bytes therefore decodes successfully, silently dropping the trailing bytes instead of refusing the malformed image.

**Reproduction.** `png_with_idat(zlib.compress(raw) + b"trailing")`, where `raw` is a valid 1x1 RGB scanline, decoded to the pixel instead of raising `PngError`; `tests/test_png_malformed.py::TestMalformedImageData::test_rejects_trailing_bytes_after_the_zlib_stream` now pins the refusal.

**Validation gap:** unclear-invariant — the decoder's docstring promised the whole compressed stream was validated but never stated that the IDAT stream must end exactly at the zlib trailer, so the reconstructed invariant is recorded in `docs/invariants.md`.

### `apply_gtk --remove` refuses to clear the GTK selection when no data home resolves (found by the bugfix role 2026-10-23; fixed 2026-10-23 by the bugfix role)

**Symptom:** `python3 tools/apply_gtk.py --remove` (and so `make remove-gtk`)
exits 2 with an `XDG_DATA_HOME` diagnostic and leaves the selection in place
when `$XDG_DATA_HOME` and `$HOME` are unusable, even though
`$XDG_CONFIG_HOME` is absolute and removal reads and writes only the config
home.

**Reproduction:** a scratch run with our `gtk-theme-name` lines in a temporary
`$XDG_CONFIG_HOME`, `env -i PATH=... XDG_CONFIG_HOME=<tmp>` and no `HOME` or
`XDG_DATA_HOME`, printed `apply_gtk: error: XDG_DATA_HOME is unset or not
absolute ...` and exited 2 with the key still present. The new
`tests/test_gtk_apply.py::TestRemove::test_remove_clears_the_selection_without_a_resolvable_data_home`
failed the same way before the fix and passes after it.

**Cause:** `main` resolved both the data and config homes before dispatching,
although `_remove` takes only the config home; the apply path is the only one
that reads the installed sheet below the data home.

**Fix:** `main` resolves the data home only on the apply path and checks only
the config home for removal. Applying still refuses an unresolvable data home.

**Validation gap:** no-observability — every existing removal test supplied a
data home, so the removal's needless data-home dependency left no failing
trace; the closest tag is no-observability.

### The Aurorae decoration reader blocks forever on a FIFO at `decoration.svg` or `decoration.svgz` (found by the bugfix role 2026-10-21; fixed 2026-10-21 by the bugfix role)

**Symptom:** the Aurorae decoration suite reads contributor-supplied artwork
without a regular-file guard. `SvgCase.setUp` parses `decoration.svg` with
`ET.parse(path)`, and `tests/test_aurorae_frame.py`'s `_read_capped` opens
`decoration.svgz` with `gzip.open()`. A FIFO at either path has no writer, so
the open or parse blocks and `make check` stalls with no diagnostic.

**Reproduction:** a scratch child called `_read_capped(fifo)` on a temporary
FIFO and was still blocked when the 3-second subprocess timeout fired. The new
`tests/test_aurorae_frame.py::TestReadCappedContainment::test_refuses_a_fifo_instead_of_blocking`
hit the test's 10-second timeout before the fix and passes after it; it runs the
real `parse_svg` path for `decoration.svg` as well as the capped gzip read.

**Cause:** the reader's earlier hardening refused symlink escapes and oversize
decompression, but `parse_svg` and `_read_capped` still opened the path itself
rather than the shared regular-file guard. `ET.parse` and `open()` on a FIFO
wait for a writer before any read-side check can run.

**Fix:** both readers now open through `containment.open_regular_binary`, which
opens non-blocking and refuses a descriptor that is not a regular file by name.
`parse_svg` hands the guarded handle to `ET.parse`; `_read_capped`'s optional
opener wraps its guarded handle, so the gzip path still decompresses through
the size cap, and `tests/support/containment.py` re-exports the shared helper.

**Validation gap:** no-observability — the aurorae reader tests covered symlink
escapes, outside paths and oversize decompression but never a non-regular path,
so the FIFO hang left no failing trace until a scratch child call surfaced it.

### The containment guard fails open for a root spelled with a POSIX double leading slash (found by the bugfix role 2026-10-21; fixed 2026-10-21 by the bugfix role)

**Symptom:** `tools.containment.is_within("//tmp/repo", "/tmp/repo/link")` returns
False even though both spellings name the same directory on POSIX. Because
`require_within_repo` resolves a path only when `is_within` says it is eligible, a
root spelled `//tmp/repo` makes `read_bytes` return a symlink target outside the
repository instead of refusing the escape (fail open).

**Reproduction:** a scratch read of a temporary root's escaping symlink, passing
`"//" + root.lstrip("/")` as the root, returned the secret's bytes. The new
`tests/test_containment.py::TestReadBytes::test_rejects_a_symlink_escape_when_the_root_has_a_double_slash_prefix`
and
`tests/test_containment.py::TestIsWithin::test_treats_a_posix_double_slash_spelling_as_the_same_root`
failed before the fix and pass after.

**Cause:** `os.path.abspath` preserves a path's exactly-two leading slashes, so
the lexical comparison saw `//tmp/repo` and `/tmp/repo` as different, and the
root's child was judged outside the root before the resolver ran.

**Fix:** `is_within` normalizes a POSIX path's double-leading-slash spelling to
one slash before comparing, and builds the boundary by trimming trailing
separators and appending exactly one, so `/`, `//`, and ordinary roots all keep
a correct component boundary.

**Validation gap:** no-observability — no caller in the suite or tools passes a
root with a double-slash spelling, so the fail-open left no trace until a direct
scratch call with a temporary root surfaced it.

### The lexical containment guard rejects every child of a filesystem root (found by the bugfix role 2026-10-21; fixed 2026-10-21 by the bugfix role)

**Symptom:** `tools.containment.is_within("/", "/etc")` returns False, though every
absolute path is inside `/`. Because `require_within_repo` resolves a path only when
`is_within` says it is eligible, a root of `/` makes the guard skip the symlink-escape
check for every path (fail open) instead of refusing an escaping one.

**Reproduction:** a scratch call printed `False` for `is_within("/", "/etc")`;
`tests/test_containment.py::TestIsWithin::test_accepts_a_path_under_the_filesystem_root`
failed on it before the fix and passes after.

**Cause:** the guard compared `absolute.startswith(base + os.sep)`. A base of `/`
already ends with the separator, so the boundary became `//` and no real child matched it.

**Fix:** `is_within` appends `os.sep` only when the base does not already end with one,
so both a filesystem root and an ordinary directory keep a correct boundary.

**Validation gap:** no-observability — no caller in the suite or tools passes a filesystem
root, so the guard's contract violation left no trace until a direct scratch call and the
new test surfaced it.

### A malformed KDE group header makes the test-side reader raise where KDE ignores it (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** a KDE INI text whose group header has no closing `]` (for example `[General`) makes
`tests/support/kde_config.py`'s `read` raise `configparser.MissingSectionHeaderError` (when it is
the first line) or `configparser.ParsingError` (after a valid section), aborting the caller.
KConfig 6.13 logs `Invalid group header` and ignores the line: a following key with no new header
stays in the previous section, and a key before any valid header is filed in KDE's `<default>`
root group. The other two
readers already disagree on the same text, so this is the same recurring divergence the parity
corpus was meant to catch: `defaults_groups` deliberately raises `ValueError` naming the heading,
while the `uninstall` awk treats `[General` as the `General` section.

**Reproduction:** confirmed with `kreadconfig6` 6.13.0 and a scratch `kdeglobals`. For
`[General\nColorScheme=MacOS8\n`, KDE warns about the header and files the key in `<default>`, so
it resolves no `[General]` value; the test-side reader raises `MissingSectionHeaderError` and the
awk prints `MacOS8`. For
`[General]\nColorScheme=BreezeLight\n[Broken\nColorScheme=MacOS8\n`, KDE resolves `MacOS8`
(continuing `[General]`), the test-side reader raises `ParsingError` and the awk prints
`BreezeLight`.

**Suggested direction:** add both shapes to `tests/support/kde_ini_corpus.py` and decide the
shared rule before changing a reader: KDE's skip-and-continue for the test-side reader and awk
(the reader can drop a line that starts with `[` and has no closing `]`), while
`defaults_groups` may keep its stricter refusal because its headings name output files and a
silently skipped heading would drop a whole config section. Record whichever contract is chosen
in the parity corpus docstring and `docs/invariants.md`.

**Fix:** `tests/support/kde_config.py`'s `_parseable_lines` now drops a line that opens a heading
but never closes it, keeping the open section for the keys after it, and keeps a key line seen
before the first valid heading in KDE's `<default>` root group rather than discarding it. An empty
`[]` heading opens a group of its own, so the keys after it are not left in the previous section
(configparser has no empty section name, so those keys are dropped). `read` thus resolves what
KConfig resolves instead of raising. The `uninstall` recipe's `awk` skips a `[`-opened line with
no `]` for the same reason, and `[]` already reset its section to none, so no following key joined
the previous section. `defaults_groups` keeps its stricter `ValueError` because its headings name
output files; the corpus marks that split with a `defaults_raises` field, and
`tests/test_kde_ini_parity.py` feeds both malformed shapes, the empty header and the root-group key
through all three readers. `docs/invariants.md`'s tooling row records the contract.

**Validation gap:** none — `kreadconfig6` 6.13.0 and the scratch `kdeglobals` reproduced both
shapes deterministically, and the new corpus cases failed before the fix (`MissingSectionHeaderError`
and `ParsingError` from the reader; the awk returned `BreezeLight` where KDE resolves `MacOS8`) and
passed after it.

### KDE's config-reading rules are re-derived in three readers, so a quirk fixed in one is not checked in the others (found by the steward role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** three independent readers implement KDE's INI dialect:
`tests/support/kde_config.py`'s `read` (the reader the theme tests use), the inline `awk` in the
`_uninstall` recipe (`Makefile`, the "Read ... the way KDE reads it" block), and
`tools/theme_defaults.py`'s `defaults_groups`. Each defines the same rules itself: strip a leading
UTF-8 BOM, trim each line before it can open a section or key, keep key names case-sensitive, and
let the last duplicate key win. A rule learned by one reader is not exercised on the other two.
They already disagree: `kde_config.read` returns `MacOS8` for a `ColorScheme:MacOS8` line
(`configparser` accepts `:` as a delimiter), while the Makefile's awk reads no value for it, and
no test or doc says which reading matches KDE.

**Why this is a structural risk:** the same quirk has already been fixed once per reader. On
2026-10-19 the missing-BOM case was fixed twice: in `make uninstall`'s awk (`BUGS-FIXED.md`:
"`make uninstall`'s color-scheme warning misses a `kdeglobals` that opens with a UTF-8 BOM") and
in `kde_config.read` (`BUGS-FIXED.md`: "`tests/support/kde_config.py` cannot read a KDE INI that
opens with a UTF-8 BOM"); the commit that made the second fix (`23978a0`) drops the same change
from `theme_defaults` as a duplicate. The awk then separately learned the indented-header rule
(`BUGS.md ## Fixed`) and last-key-wins (`BUGS-FIXED.md`: "`make uninstall`'s color-scheme warning
reads the first duplicate `ColorScheme` key, not the last"), and `defaults_groups`'
indented-heading case was pinned only later (`1b71ead`). The gap tags record this as recurring
(the BOM pair as `no-observability`, the header and duplicate-key cases as `unclear-invariant`),
but neither promoted remedy covers it: the mutation harness targets the shipped registers and
checkers, and `docs/invariants.md` has no row for KDE INI semantics. No test feeds one fixture
text through more than one reader, so a divergence is invisible:
`tests/test_colorscheme_install.py` drives the Makefile reader through `make uninstall` with
hand-written fixtures, `tests/test_kde_config.py` pins `kde_config.read` with its own, and
`tests/test_theme_defaults.py` pins `defaults_groups` with a third set.

**Reproduction:** no failing behaviour is needed; each reader passes its own cases. Confirm the
drift with a scratch `kdeglobals` holding `[General]` then `ColorScheme:MacOS8`:
`kde_config.read` returns `MacOS8`, and the `_uninstall` recipe's awk prints nothing.

**Suggested direction:** keep one fixture corpus of small KDE INI texts (BOM, indented header,
indented key, duplicate key, case mismatch, colon-delimited key, comment, blank line, `%` in a
value) and one test that runs the corpus through `kde_config.read`, `defaults_groups` and the
Makefile's reader (through `make uninstall`, as the install tests already do), asserting the same
interpretation and recording the chosen KDE semantics in `docs/invariants.md`'s `tooling`
section; a new quirk then lands in one place and fails in every reader that misses it.

**Fix:** `tests/support/kde_ini_corpus.py` holds one small text per rule, and
`tests/test_kde_ini_parity.py` feeds every case through `kde_config.read`, `defaults_groups` and
`make uninstall`. The corpus pins KDE's observed semantics: `=` is the only key/value delimiter
(a colon-delimited line is an invalid entry, ignored), each line is trimmed, section and key names
are case-sensitive, the last duplicate key wins, and only a leading `#` starts a comment. The
readers already agreed except `kde_config.read`, which now parses with `=` alone, skips the
no-`=` lines KDE skips instead of rejecting the file, treats only `#` as a comment, and lets the
last duplicate key win. `docs/invariants.md`'s `tooling` section now records the shared
semantics. The BOM case stays: all three readers strip one as a deliberate leniency (KConfig
6.13 logs a BOM-prefixed first line as invalid) so an editor-saved file still loads.

**Validation gap:** none — the entry's scratch `kdeglobals` reproduced the colon divergence
deterministically, and the new parity test failed on the colon and duplicate fixtures before the
fix and passed after it.

### `make uninstall`'s color-scheme warning misses an indented `[General]` section header (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** when `$XDG_CONFIG_HOME/kdeglobals` opens its `[General]` section with a line
that has leading whitespace, `make uninstall` does not warn about a still-selected scheme.
KDE trims each line before parsing it, so the indented header still opens `[General]` and its
`ColorScheme` key is the live selection; the diagnostic claims to read kdeglobals "the way
KDE reads it", so the missing warning is a real, if low-severity, gap.

**Reproduction:**
`tests/test_colorscheme_install.py::TestInstall.test_make_uninstall_warns_for_an_indented_general_section`
writes `"  [General]\nColorScheme=MacOS8\n"` as kdeglobals and runs `make uninstall`; before
the fix it emitted no warning.

**Cause:** the uninstall recipe's `awk` recognised a section header only at the start of the
line (`/^\[/`), so an indented `[General]` was never seen as the current section and its
`ColorScheme` key was skipped.

**Fix:** the `awk` now matches and strips leading whitespace before the `[` (`/^[[:space:]]*\[/`),
matching KDE's trim-before-parse behaviour.

**Validation gap:** unclear-invariant — no test or doc stated that KDE's config reader trims a
line before matching a section header, so that invariant had to be established before the
parser could be pinned to it.

### `make uninstall`'s color-scheme warning misses a `kdeglobals` that opens with a UTF-8 BOM (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** when `$XDG_CONFIG_HOME/kdeglobals` opens with a UTF-8 BOM before its
`[General]` header, `make uninstall` does not warn about a still-selected scheme.
Qt (and the project's `tests/support/kde_config.py`) strips a leading BOM before
parsing, so the BOM-prefixed file still opens `[General]` and its `ColorScheme`
key is the live selection; the diagnostic claims to read kdeglobals "the way KDE
reads it", so the missing warning is a real, if low-severity, gap.

**Reproduction:**
`tests/test_colorscheme_install.py::TestInstall.test_make_uninstall_warns_for_a_kdeglobals_with_a_utf8_bom`
writes `"\ufeff[General]\nColorScheme=MacOS8\n"` (encoding `utf-8`, so the BOM
bytes `EF BB BF`) as kdeglobals and runs `make uninstall`; before the fix it
emitted no warning.

**Cause:** the uninstall recipe's `awk` recognised a section header only with
`/^[[:space:]]*\[/`, so the BOM bytes before the `[` kept the first line from
being seen as a section and its `ColorScheme` key was skipped.

**Fix:** the `awk` now strips a leading UTF-8 BOM on its first record
(`NR==1 { sub(/^\357\273\277/, "") }`) before matching, matching Qt's
strip-before-parse behaviour.

**Validation gap:** no-observability — the suite never wrote a BOM-prefixed
kdeglobals, so the omitted warning left no trace and only a new BOM case could
confirm it.

### A NUL byte in a guarded path escapes the containment guard's fail-closed contract (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** `tools/containment.resolves_within` documents that a path whose resolution
fails is refused, not assumed contained, but an embedded NUL byte makes POSIX
`Path.resolve()` raise `ValueError`, which the guard did not catch. The error escaped as a bare
`lstat: embedded null character in path` instead of the guard's own refusal, so a caller that
expected a boolean or the named `ValueError` saw an unrelated exception.

**Reproduction:** `containment.resolves_within(root, root / "a\x00b")` raised `ValueError`, and
`containment.require_within_repo(root / "a\x00b", root)` raised the bare `lstat` error. Pinned by
`tests/test_containment.py::TestResolutionFailureFailsClosed`.

**Cause:** `resolves_within` caught only `OSError` and `RuntimeError` from `Path.resolve()`;
POSIX `Path.resolve()` raises `ValueError` for an embedded NUL.

**Fix:** `resolves_within` now also catches `ValueError`, so every resolution failure fails
closed; `require_within_repo` then raises its own named refusal.

**Validation gap:** no-observability — no reader passes a NUL-bearing path, so the guard's
contract violation left no trace in the suite and surfaced only from a direct scratch call.

### The symlink-containment guard is reimplemented at five sites (found by the steward role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** the guarantee "refuse a contributor-supplied repository file whose path resolves
outside the repository" was implemented five times. Four copies used one mechanism and one used
another: `tests/support/containment.py` (the shared guard), `tests/placeholders.py`'s
`_resolves_within`, `tests/invariants.py`'s inline check, and `tools/theme_defaults.py`'s
`_require_within_repo` compared `os.path.realpath` results with `startswith(base + os.sep)`;
`tools/reference_validation.py`'s `_resolves_within` used
`Path.resolve().is_relative_to(directory.resolve())`. A refinement applied to one copy did not
reach the other four, so a later reader could adopt a stale copy and reopen the leak class the
guard exists to close.

**Why this is a structural risk:** the same contributor-content leak has been fixed one module at
a time. Seven `no-fake` Fixed entries in `BUGS-FIXED.md` are that class, each a module that read
its repository file bare and needed its own symlink fixture to confirm the leak:
`tests/placeholders.py`'s `cross_check`; `tests/invariants.py`'s `cross_check`;
`tests/support/checker_mutations.py`'s register reads; the color-scheme provenance test; the
desktop-theme copy-identity tests; `tests/support/splash_fixtures.py`; and
`tests/support/package_metadata.py`. The shared `tests/support/containment.py` was extracted along
the way, but four modules still kept a local copy of the check.

**Suspected cause:** `tools/` cannot import `tests/support/`, so `tools/theme_defaults.py` and
`tools/reference_validation.py` grew their own copies; `tests/placeholders.py` and
`tests/invariants.py` kept a local check from before the shared helper existed, even though both
already import `support.containment` for another read.

**Fix:** the guard now lives once in `tools/containment.py`, the one module both trees can import
(tests reach it as `tools.containment` with the repository root on `sys.path`).
`tests/support/containment.py` re-exports the shared functions under the name the test helpers
already use, and `tests/placeholders.py`, `tests/invariants.py`, `tools/theme_defaults.py` and
`tools/reference_validation.py` call the shared `resolves_within`/`require_within_repo` instead of
their local copies. `tests/test_containment.py::TestGuardIsShared` pins the single
implementation, and the `tooling` section of `docs/invariants.md` records the guarantee.

**Validation gap:** no-observability — the five copies had no failing behavior to reproduce, so
only a source-level check can observe the drift risk; the regression test parses the four readers'
ASTs and rejects a local resolver definition or an inline `realpath`/`is_relative_to` call.

### `make install INSTALL_PACKAGES=<unknown>` silently installs nothing (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** `make install INSTALL_PACKAGES=colour-scheme` (a typo, or any name
that is not one of the seven families) filtered every family out, created the
data home, copied nothing and exited 0 — a green install that installed nothing,
the same failure the empty-value guard refuses.

**Reproduction:**
`tests/test_theme_install.py::TestInstallPackagesGuard.test_unknown_family_is_refused_before_creating_the_data_home`
runs `make install INSTALL_PACKAGES=colour-scheme`; before the fix it exited 0
with an empty data home.

**Cause:** `require_install_packages` only rejected an empty or whitespace-only
value; it never checked that each named word was a known artifact family, and
`_install`'s `$(filter ...)` guards turn an unknown word into a no-op.

**Fix:** the guard now word-splits `INSTALL_PACKAGES` (with `set -f` so a glob
cannot expand), refuses an empty list as before, and refuses any word not in the
new `INSTALL_FAMILIES` list with a diagnostic naming the unknown families and
the known ones.

**Validation gap:** unclear-invariant — no test or doc stated that the guard's
promise was "no green install that installs nothing" rather than "reject the
empty value", so that invariant had to be reconstructed and is now recorded in
`docs/invariants.md` (tooling).

### `tests/support/kde_config.py` cannot read a KDE INI that opens with a UTF-8 BOM (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** `kde_config.read` opened the file with `encoding="utf-8"`, so a leading
BOM stayed in the first line. `configparser` then found no section header and raised
`MissingSectionHeaderError` ("File contains no section headers") instead of reading
the file the way Plasma's `QSettings`/`QTextStream` does (Qt strips a UTF-8 BOM). A
contributor-supplied `MacOS8.colors`, `org.macos8.desktoprc`,
`org.macos8.desktop.kvconfig` or `contents/defaults` saved with a BOM therefore
aborted the test that read it.

**Reproduction:** a scratch run wrote `b"\xef\xbb\xbf[General]\nColorScheme=MacOS8\n"`
to a temp file and called `kde_config.read(path)`; it raised
`MissingSectionHeaderError` at line 1.
`tests/test_kde_config.py::TestReadKdeConfig.test_strips_a_leading_utf8_bom` now pins
the fixed behavior.

**Cause:** `read` opened with `encoding="utf-8"`, so the BOM was not stripped before
`configparser.read_file`.

**Fix:** read with `encoding="utf-8-sig"`, which strips a leading BOM and behaves
identically to `utf-8` for BOM-less files, matching Qt's reader and the project's
other contributor-file readers (`tools/theme_defaults.py`,
`tools/reference_validation.py`).

**Validation gap:** no-observability — no test read a BOM-prefixed INI, so the
reader's mishandling was never triggered in the suite and only a new BOM case could
confirm it.

### `tests/placeholders.py`'s `cross_check` reads a symlinked `PLACEHOLDERS.md` bare (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** when `PLACEHOLDERS.md` is a checked-in symlink resolving outside the repository,
`cross_check(ROOT, REGISTER)` opened it bare and parsed its table rows. A row matching the
register's `| \`path\` | stands in for |` shape then reached an `AssertionError` that echoes the
asset path (`"... lists <asset>, which does not exist"`), leaking a line of a private file into
the failing test's diagnostic.

**Reproduction:**
`tests/test_placeholders.py::TestHelpers.test_cross_check_refuses_a_symlinked_register_that_escapes`
symlinks a temp root's `PLACEHOLDERS.md` to a private file containing
``| `secret-token` | classified |``; before the fix the `AssertionError` contained
`secret-token`.

**Cause:** `cross_check` passed its `register` straight to `register_entries`, which opened it
with a bare `open(path, encoding="utf-8")`; nothing checked that a repository register still
resolved inside the repository.

**Fix:** `cross_check` now calls `support.containment.require_within_repo(register, root)` before
reading the register, so a path lexically inside `root` that resolves outside it raises
`ValueError` before any row is parsed. A register outside `root` (a test's temporary file) is
unaffected.

**Validation gap:** no-fake — the leak needed a manufactured private file plus a symlinked
register that the suite did not previously build.

### `tests/invariants.py`'s `cross_check` reads a symlinked register bare (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** when the register path handed to `cross_check` is a checked-in symlink that
resolves outside the repository (the shipped call passes `docs/invariants.md`), the register is
read and parsed anyway. `parse_rows` echoes a malformed table row's line in its
`AssertionError`, so a private file's line reaches the failing test's diagnostic. This is the
same contributor-content leak class the seed reads in `tests/support/checker_mutations.py` were
guarded against, left open on the checker's own production read.

**Reproduction:**
`tests/test_invariants.py::TestHelpers.test_cross_check_refuses_a_symlinked_register_that_escapes`
symlinks `docs/invariants.md` under a fake root to a private file holding a malformed row and
calls `cross_check`; before the fix it raised `AssertionError: malformed table row ... |
secret-token | short`, echoing the private line, instead of refusing the escape.

**Cause:** `cross_check` opened the register with a bare `open(register, encoding="utf-8")`
and caught only `UnicodeDecodeError`/`OSError`; a symlink resolving outside `root` was followed
like any other file.

**Fix:** the read now routes through `support.containment.read_text(register, root)`, which
resolves the path and raises `ValueError` naming the escape before opening it. A register that
is a test's temporary file outside `root` is unaffected, as are the missing-file and non-UTF-8
paths, which still surface as the checker's own `AssertionError`.

**Validation gap:** no-fake — the suite had no `cross_check` fixture with a symlinked register,
so confirming the leak needed a scratch fake root plus a symlink, which was then added as the
regression test.

### `tests/support/checker_mutations.py`'s register reads follow a symlinked register outside the repository (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** `Scratch.build` read `docs/invariants.md` and `PLACEHOLDERS.md` with a bare
`Path.read_text`, so a checked-in symlink at either path that resolves outside the repository
was followed. That text seeds the scratch copy the checker runs against, and
`tests/invariants.py` echoes a malformed row's line in its `AssertionError`, so a private
file's line could reach a failing test's diagnostic.

**Reproduction:** with `checker_mutations.ROOT` pointed at a scratch root whose
`docs/invariants.md` symlinks a private file outside that root, `Scratch.build` returned a
scratch holding the private line and `invariants.cross_check` raised
`malformed table row in section secret (expected 3 cells): | a | b`, echoing it;
`tests/test_checker_mutations.py::TestCheckerMutations.test_register_reads_refuse_a_symlink_escape`
now pins the refusal.

**Cause:** the two seed reads bypassed `support/containment.py`, the guard every other reader
of a contributor-supplied repository file goes through.

**Fix:** both reads go through a new `_read_register` helper that calls
`containment.read_text(ROOT / relative_path, ROOT)`, which refuses a path that resolves
outside the repository.

**Validation gap:** no-fake — no fixture created a symlinked register, so confirming the leak
needed a fake repository root with the register symlinked outside it.

### The color-scheme provenance test reads `MacOS8.colors` unguarded (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** `tests/test_colorscheme.py::TestProvenanceNote.test_tooltip_is_named_as_not_reference_sampled`
opened `SCHEME` with a bare `open()`, joined its `#` comment lines into `text`, and passed `text`
to `assertIn`/`assertRegex`. A checked-in symlink at
`theme/color-schemes/MacOS8.colors` to a private file is read, and a failing assertion echoes
that file's comment lines into the diagnostic. Unlike `load_scheme`/`kde_config.read`, this read
never called `containment.require_within_repo`.

**Reproduction:** point `SCHEME` at a symlink to a private file whose comment lines lack
`[Colors:Tooltip]`; the `assertIn` diagnostic contained the private comment lines. A scratch
script with the symlink at a repository path showed the bare read echoing
`private secret line [Colors:Other]`; after the fix the guarded read raises
`ValueError: ... resolves outside ... (a symlink escape)` and echoes nothing. The new
`tests/test_containment.py::TestReadText.test_rejects_a_symlink_that_escapes_the_root` fails
without `containment.read_text`.

**Cause:** the direct `open(SCHEME)` predated the containment guards; the test read the scheme
directly instead of through a guarded reader.

**Fix:** `tests/support/containment.py` gained `read_text(path, root)`, the text sibling of
`read_bytes`, which calls `require_within_repo` before opening; the provenance test now reads
through it.

**Validation gap:** no-fake — confirming the leak needed a symlink fixture the existing suite did
not have, so one had to be manufactured before the diagnostic echo could be observed.

### The desktop-theme copy-identity tests read the secondary SVG copy unguarded (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** `tests/test_desktoptheme_background.py::TestBackground.test_translucent_copy_is_identical`,
`tests/test_desktoptheme_panel.py::TestPanelBackground.test_solid_copy_is_identical` and
`tests/test_desktoptheme_tooltip.py::TestTooltip.test_solid_copy_is_identical` each open their
secondary SVG copy (`TRANSLUCENT_BACKGROUND_SVG`, `SOLID_PANEL_SVG`, `SOLID_TOOLTIP_SVG`) with a
bare `open()`. A checked-in symlink at that path to a private file is read, and `assertEqual` on
the mismatched byte strings echoes that file's bytes into the failing test's diagnostic.

**Reproduction:** a scratch script (a symlink at the secondary path plus the bare
`open`/`assertEqual` pair) printed the secret's bytes in the `AssertionError`; the new
`tests/test_containment.py::TestReadBytes.test_rejects_a_symlink_that_escapes_the_root` fails
without the guard.

**Cause:** only the primary `SVG_PATH` went through `SvgCase.setUp`'s containment guard; the
copy-identity checks read the duplicate file directly, so the guard the primary path gets was
never applied to the second path.

**Fix:** `tests/support/containment.py` gained `read_bytes(path, root)`, which calls
`require_within_repo` before opening; the three copy-identity tests read both copies through it.

**Validation gap:** no-fake — confirming the leak needed a symlink fixture the existing suite did
not have, so one had to be manufactured before the diagnostic echo could be observed.

### `tests/support/splash_fixtures.py`'s `read_qml` follows a symlinked `Splash.qml` outside the repository (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** a checked-in `Splash.qml` that is a symlink to a private file outside the
repository is opened and its text returned. The splash tests feed that text to `assertIn` and to
`object_source`'s brace-balanced slice, and a failing `assertIn` echoes the container, so the
private file's content can appear in a test diagnostic. The security sweep guarded
`support/kde_config.read`, `header_comment` and `SvgCase.setUp` against exactly this symlink
escape, and the bugfix role guarded `load_metadata`, but left this reader unguarded.

**Reproduction:**
`tests/test_splash_qml.py::TestSplashQmlContainment::test_rejects_a_symlink_that_escapes_the_repository`
makes a `Splash.qml` symlink inside a repository root that points at a private sibling and calls
`read_qml`; before the fix the private text came back and no `ValueError` was raised.

**Cause:** `read_qml` called `open(SPLASH)` with no containment check, so it read the symlink's
target.

**Fix:** `read_qml` now calls `containment.require_within_repo(SPLASH, ROOT)` before opening,
so a `Splash.qml` that resolves outside the repository is refused with the path named, matching
the other contributor-supplied readers.

**Validation gap:** no-fake — the suite never created a symlinked `Splash.qml`, so confirming
the escape needed a symlink fixture and a patched repository root that did not exist.

### `tests/support/package_metadata.py`'s `load_metadata` follows a symlinked `metadata.json` outside the repository (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** a checked-in `metadata.json` that is a symlink to a private JSON file outside the
repository is opened and parsed. The `PackageMetadata` mixin then asserts the parsed object's
fields, and a failing `assertEqual` echoes the actual value, so the private file's content can
appear in a test diagnostic. The security sweep guarded `support/kde_config.read`,
`header_comment` and `SvgCase.setUp` against exactly this symlink escape but left this reader
unguarded.

**Reproduction:**
`tests/test_package_metadata.py::TestLoadMetadataContainment::test_rejects_a_symlink_that_escapes_the_repository`
makes a `metadata.json` symlink inside a repository root that points at a private sibling and
calls `load_metadata`; before the fix the private object came back and no `ValueError` was raised.

**Cause:** `load_metadata` called `open(path)` with no containment check, so `json.load` read the
symlink's target.

**Fix:** `load_metadata` now calls `containment.require_within_repo(path, ROOT)` before opening,
so a `metadata.json` that resolves outside the repository is refused with the path named, matching
the other contributor-supplied readers.

**Validation gap:** no-fake — the suite never created a symlinked `metadata.json`, so confirming
the escape needed a symlink fixture and a patched repository root that did not exist.

### `tests/invariants.py`'s `cross_check` lets an unreadable register escape as a bare `OSError` (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** when `docs/invariants.md` is missing, is a directory or is otherwise unreadable,
`cross_check` aborts with a bare `FileNotFoundError`/`OSError` naming neither the checker nor
the register's role; a register whose bytes are not UTF-8 aborts with a bare
`UnicodeDecodeError`. The helper's docstring promises `AssertionError` diagnostics for a bad
register, so a caller cannot catch and report the failure as the register's own problem.

**Reproduction:**
`tests/test_invariants.py::TestHelpers.test_cross_check_rejects_an_unreadable_register` calls
`cross_check` with a missing register path; before the fix it raised `FileNotFoundError`.
`...test_cross_check_rejects_a_non_utf8_register` writes a non-UTF-8 `docs/invariants.md`;
before the fix it raised `UnicodeDecodeError`.

**Cause:** `cross_check` read the register with a bare `open()` outside any handler, unlike
`tests/placeholders.py::register_entries`, which reports the same failure as its own
`AssertionError`.

**Fix:** `cross_check` now reads the register inside a `try` and raises
`AssertionError(f"{register} cannot be read: {exc}")` on `OSError` and
`AssertionError(f"{register} is not valid UTF-8 text: {exc}")` on `UnicodeDecodeError`,
matching the placeholder checker; `parse_rows` still runs on the decoded text.

**Validation gap:** no-fake — the shipped suite had no fixture for an unreadable or non-UTF-8
register, so one had to be written before the failure could be confirmed.

### `tests/support/package_metadata.py` lets an unreadable `metadata.json` escape as a bare `OSError` (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** `load_metadata` opens the file with `open()` outside its `try`, so a
`metadata.json` that cannot be read at all -- a missing file, a dangling symlink, a directory, a
permission error -- escapes as a bare `OSError` (e.g. `FileNotFoundError`) instead of the
helper's own `ValueError`. The three suites that share the mixin (`test_lookandfeel`,
`test_desktoptheme`, `test_wallpaper`) then abort with a read error that names neither the guard
nor the file's role, and a caller guarding on `ValueError` does not catch it.

**Reproduction:**
`tests/test_package_metadata.py::TestLoadMetadata::test_unreadable_file_names_the_path` calls
`load_metadata` on a path whose parent directory does not exist; before the fix it raised
`FileNotFoundError`.

**Cause:** `load_metadata`'s `try` wrapped only `json.load`, with arms for `JSONDecodeError` and
`UnicodeDecodeError`; the `open()` call sat outside it, so an `OSError` from opening (or reading)
the file had no arm.

**Fix:** `load_metadata` now wraps the `open()`/`json.load()` pair in one `try` with an
`OSError` arm that raises `ValueError(f"{path}: cannot be read: {exc}")`, matching the helper's
contract of naming the file for every bad input.

**Validation gap:** no-fake — no fixture supplied an unreadable `metadata.json`, so the `OSError`
path was unobserved; the regression test creates a missing path the suite did not have.

### `tests/placeholders.py` lets an unreadable register escape as a bare `OSError` (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** `register_entries` (and so `cross_check`) reads `PLACEHOLDERS.md` with `open()`
but caught only `UnicodeDecodeError`, so a register that cannot be read -- a missing file, a
directory, a permission error -- escaped as a bare `OSError` naming neither the checker nor the
register's role, aborting the placeholder check instead of the checker's own `AssertionError`.

**Reproduction:**
`tests/test_placeholders.py::TestHelpers::test_register_entries_rejects_an_unreadable_register`
passes a path that does not exist; before the fix it raised `FileNotFoundError`.

**Cause:** `register_entries`' `try` had only a `UnicodeDecodeError` arm; the same `OSError`
arm added to `_marker_text` the previous run was not applied here.

**Fix:** `register_entries` now catches `OSError` alongside `UnicodeDecodeError` and raises
`AssertionError(f"{path} cannot be read: {exc}")`, matching `_marker_text`.

**Validation gap:** no-fake — no fixture supplied an unreadable register, so the `OSError` path
was unobserved; the regression test creates a missing register path the suite did not have.

### `tests/placeholders.py` lets a dangling symlink inside `theme/` escape as a bare `FileNotFoundError` (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** a text asset under `theme/` that is a symlink to a nonexistent
target *inside* `theme/` passes the symlink-escape guard (the resolved path is
contained), but `_marker_text` then opens it and raises a bare
`FileNotFoundError`. The module documents that an unreadable asset fails as
the checker's own `AssertionError` naming the path; instead the run aborts
with an unrelated traceback that does not name the checker.

**Reproduction:**
`tests/test_placeholders.py::TestHelpers::test_markers_rejects_a_dangling_symlink_within_the_theme_root`
builds a synthetic theme root whose `theme/link.svg` points at
`theme/missing.svg` and calls `markers`; before the fix it errored with
`FileNotFoundError` instead of the expected `AssertionError`.

**Cause:** `_marker_text` caught only `UnicodeDecodeError`, so an `OSError`
from `open` (the dangling symlink, or any unreadable asset) escaped the
checker.

**Fix:** `_marker_text` now catches `OSError` alongside `UnicodeDecodeError`
and raises `AssertionError` naming the path (`cannot be read`), matching its
documented contract and the symlink-escape guard's handling.

**Validation gap:** no-fake — confirming it needed a synthetic theme root
carrying a dangling symlink that resolves inside `theme/`, a fixture the suite
did not have.

### `make check`'s `CHECK_PATTERN` guard accepts a pattern with surrounding whitespace that then matches no test module (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** `make check CHECK_PATTERN=' test_byteops.py '` passed the `require_check_pattern`
guard, which trims leading whitespace only to test for an empty value, but the recipe handed the
untrimmed glob to `unittest discover -p ' test_byteops.py '`. The glob matches no file, so the run
executes nothing: interpreters before 3.12 exit 0 — the silent green suite the guard was added to
prevent — and 3.12 and newer exit 5 with only "NO TESTS RAN".

**Reproduction:** `make -n check` with `CHECK_PATTERN=' test_byteops.py '` printed
`-p ' test_byteops.py '` before the fix.
`tests/test_make_check.py::TestCheckPattern.test_surrounding_whitespace_pattern_is_stripped`
fails on the old recipe and passes on the new one.

**Cause:** the guard trimmed a copy of the value for its emptiness check, but the recipe expanded
`$(CHECK_PATTERN)` itself, so the value validated and the value run could differ by surrounding
whitespace.

**Fix:** the discovery recipe now hands `$(strip $(CHECK_PATTERN))` to `unittest discover`, so the
guard's trimmed value is the value the run uses.

**Validation gap:** no-repro — the untrimmed glob was visible in a `make -n` dry run, but the
silent-green symptom needs an interpreter before 3.12; on the installed 3.13 the same glob fails
loudly with NO TESTS RAN, so the guard's gap was confirmed from the dry run and the version guard
rather than from the failure itself.

### `make uninstall`'s color-scheme warning reads the first duplicate `ColorScheme` key, not the last (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** when `[General]` in `$XDG_CONFIG_HOME/kdeglobals` repeats the `ColorScheme` key,
`make uninstall`'s warning about a still-selected scheme is decided by the **first** line. KDE
(like `configparser`) lets the **last** key win, so a file holding `ColorScheme=BreezeLight`
then `ColorScheme=MacOS8` leaves KDE on `MacOS8` while uninstall stays silent; the reverse
order leaves KDE on `BreezeLight` while uninstall warns wrongly. The diagnostic claims to read
kdeglobals "the way KDE reads it", so a wrong or missing warning is a real, if low-severity,
gap.

**Reproduction:**
`tests/test_colorscheme_install.py::TestInstall.test_make_uninstall_warns_for_the_last_duplicate_selection`
and `::test_make_uninstall_does_not_warn_for_an_overridden_selection` write a two-line
`ColorScheme` kdeglobals and run `make uninstall`; before the fix the first missed its warning
and the second emitted a false one.

**Cause:** the uninstall recipe's `awk` matched the first `ColorScheme=` in `[General]` and
called `exit` immediately, so it never saw a later override.

**Fix:** the `awk` now records every match and prints the last non-empty one from its `END`
block, matching KDE's last-key-wins semantics.

**Validation gap:** unclear-invariant — no test or doc stated which duplicate key KDE's config
reader honours, so that last-key-wins invariant had to be established before the parser could
be pinned to it.

### `tools/render_surface.py` leaks the caller's `XDG_CONFIG_DIRS` into the throwaway render session (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** the render session built by `tools/render_surface.py` still resolves config
through the caller's `XDG_CONFIG_DIRS`, so a host session's `kdeglobals`/`kwinrc` (or a scheme
already applied there) can change the rendered surface even though the run installs into a
scratch `XDG_DATA_HOME` and writes `kwinrc`/`plasmarc` into a scratch `XDG_CONFIG_HOME`. This
is the same non-hermeticity that made `plasma-apply-desktoptheme` a no-op in the sibling
`TestApplyDesktopTheme` bug.

**Reproduction:** `tests/test_render_surface.py::TestFailurePaths.test_session_ignores_a_config_search_path_from_the_environment`
sets `XDG_CONFIG_DIRS` to an ambient directory and has the `dbus-run-session` stub echo the
variable it was given; before the fix it recorded the ambient path.

**Cause:** `_render` copied `os.environ` into the child env and dropped only
`WAYLAND_DISPLAY`, `DISPLAY`, `DESTDIR` and `MAKEFLAGS`, so `XDG_CONFIG_DIRS` passed through
to `plasma-apply-colorscheme` and the session.

**Fix:** drop `XDG_CONFIG_DIRS` from the child env too, so the session uses the system default
search path and never the caller's config directories.

**Validation gap:** unclear-invariant — the module promised the user's configuration is never
touched but never said the XDG config search path was part of that, so the isolation guarantee
had to be established before it could be pinned.

### `tests/test_desktoptheme.py::TestApplyDesktopTheme` fails when `XDG_CONFIG_DIRS` already names a session theme (found by the feature role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** `make check` errors in `test_apply_lists_and_selects_the_theme` with
`FileNotFoundError: [Errno 2] No such file or directory: '<tmp>/config/plasmarc'`.
`plasma-apply-desktoptheme org.macos8.desktop` exits 0 but prints `The requested theme
"org.macos8.desktop" is already set as the theme for the current Plasma session.` and writes no
`plasmarc`, so the test's `read_kde_config` call raises.

**Reproduction:** With `XDG_CONFIG_DIRS` naming a directory whose `plasmarc` already sets
`[Theme] name=org.macos8.desktop` (this session exports
`XDG_CONFIG_DIRS=/home/zach/.config/kdedefaults:/etc/xdg:...`, and
`~/.config/kdedefaults/plasmarc` holds that value), run `make check
CHECK_TESTS='test_desktoptheme.TestApplyDesktopTheme'`. Seeding the test's isolated
`$XDG_CONFIG_HOME/plasmarc` with a different theme (`[Theme] name=breeze-dark`) makes the apply
write the file and the test pass; so does clearing `XDG_CONFIG_DIRS`.

**Cause:** `plasma-apply-desktoptheme` reads the current session theme from the config search
path, which includes `XDG_CONFIG_DIRS`. The test overrides `XDG_DATA_HOME` and `XDG_CONFIG_HOME`
but not `XDG_CONFIG_DIRS`, so the real user's `kdedefaults/plasmarc` still reports the theme as
already selected and the apply is a no-op. Overriding `HOME` and `XDG_CONFIG_HOME` alone does not
isolate it.

**Fix:** `TestApplyDesktopTheme` now runs the apply through `_apply_isolated`, which points
`XDG_CONFIG_DIRS` at an empty directory inside the test's `tmp`, and
`test_apply_ignores_a_session_theme_in_the_config_search_path` plants a session-theme `plasmarc`
in the ambient `XDG_CONFIG_DIRS` to pin that isolation.

**Validation gap:** no-repro — the failure depended on the developer's ambient `XDG_CONFIG_DIRS`
naming the theme, so confirming it needed a planted session-theme config dir to make the leak
deterministic.

### `widgets/lineedit.svg` corner tiles miss the reference field's outline and top-right notch (found by the bugfix role 2026-10-19; fixed 2026-10-19 by the bugfix role)

**Symptom:** The `base` corner tiles of `theme/desktop-themes/org.macos8.desktop/widgets/lineedit.svg` did not reproduce the Mac OS 8.6 text field's corners in `macos8.6-screenshots/firstboot_betawiki.png`. Three pixels differed from the reference: the bottom-left and bottom-right corner tiles painted the #000000 outline's bottom pixel (canvas `(1,2)`) as #FFFFFF, so the outline stopped one row short of the field's bottom edge (reference `(29,351)` and `(430,351)` are #000000); and the top-right tile painted its outer pixel (canvas `(2,0)`) as #999999 where the reference `(431,58)` is the window face #CCCCCC, because the top shadow stops one pixel short of the outer highlight.

**Reproduction:** `python3 tools/sample.py macos8.6-screenshots/firstboot_betawiki.png 29 351`, `... 430 351` (both #000000) and `... 431 58` (#CCCCCC); the pre-fix artwork rendered #FFFFFF and #999999 there. `tests/test_desktoptheme_lineedit.py::TestLineEditReference::test_corners_match_the_reference` now re-derives all six corner pixels, and `TestLineEdit::test_lineedit_corner_bevels_turn_the_corner` fails against the old artwork.

**Cause:** `sunken_outside_face_corners` and the SVG corner groups were drawn from the edge bands alone, which is self-consistent but puts the bottom outline one row short and fills the top-right outer corner with the shadow. The existing corner test pinned that wrong table, and the reference test only sampled three border runs, so the whole suite passed.

**Validation gap:** unclear-invariant — the in-repo corner table was self-consistent with the artwork, so confirming the bug meant reconstructing the field's intended corner geometry from the reference screenshot's corner pixels before the test could assert it.

### `tools/url_check.py` accepts a malformed path, query or fragment as a provenance citation (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role)

**Symptom:** `url_problem` returned `None` for
`https://example.test/%`, `https://example.test/a%2`,
`https://example.test/a<b>` and `https://example.test/a?q=%`, so
`tools/check_references.py` would accept a `sources.txt` row citing any of
them as a well-formed absolute URL. RFC 3986 requires a `%` to introduce
exactly two hex digits and limits a path to `pchar` (plus `/`), a query and a
fragment to `pchar` (plus `/` and `?`), so each is malformed while the
provenance check reported it clean.

**How to reproduce:**
`python3 -c "from tools.url_check import is_absolute_url; print(is_absolute_url('https://example.test/%'))"`
printed `True` before the fix and prints `False` after.

**Cause:** `url_problem` validated the scheme, whitespace and authority but
never the path, query or fragment after them, even though its docstring
claims to return why a URL is not a well-formed absolute URL.

**Fix:** After the authority checks, `url_problem` splits the remainder into
path, query and fragment and holds each to its RFC 3986 character set
(`_is_path`, `_is_query_or_fragment`), so a bare percent or a raw character
no `pchar` allows is rejected.

**Test:** `tests/test_url_check.py::TestPathQueryFragmentCharacters` gained
`test_path_query_fragment_characters_are_accepted` and
`test_malformed_path_query_fragment_characters_are_rejected`; the class
failed on the malformed cases before the fix and passes after.

**Validation gap:** unclear-invariant -- the docstring claimed well-formedness
but named only the scheme and authority rules, so I had to reconstruct that
the path, query and fragment were meant to be covered before I could confirm
the acceptance was a bug and not intended scope.

### `tools/url_check.py` rejects an uppercase IPvFuture host as a provenance citation (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role)

**Symptom:** `url_problem` returned `"must bracket an IPv6 or IPvFuture
address"` for `https://[V1.a]/x`, so the checker reported a well-formed RFC 3986
IPvFuture as a malformed citation. RFC 3986's ABNF imports RFC 5234's
case-insensitive literals, so the leading `v` of `IPvFuture = "v" 1*HEXDIG "."
1*( unreserved / sub-delims / ":" )` may be either case.

**How to reproduce:**
`python3 -c "from tools.url_check import is_absolute_url; print(is_absolute_url('https://[V1.a]/x'))"`
printed `False` before the fix; `https://[v1.a]/x` printed `True`.

**Cause:** `_IPV_FUTURE` was compiled as
`re.compile(r"v[0-9A-Fa-f]+\....")`, whose literal `v` matched only lowercase
while `ipaddress.IPv6Address` then rejected `V1.a`, so the whole bracketed host
failed.

**Fix:** `_IPV_FUTURE` is now `re.compile(r"[vV][0-9A-Fa-f]+\....")`, so the
leading `v` matches either case as the ABNF requires.

**Test:** `tests/test_url_check.py::TestBracketedHosts` gained
`https://[V1.a]/x` in `test_valid_ip_literals_are_accepted`; the class failed on
it before the fix and passes after.

**Validation gap:** unclear-invariant -- the docstring and the suite stated the
IPvFuture rule but not that ABNF literals are case-insensitive, so I had to
reconstruct that the uppercase form is well formed before I could confirm the
rejection was a bug and not intended.

### `tools/url_check.py` accepts an IPv6 zone identifier as a provenance citation (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role)

**Symptom:** `url_problem` returned `None` for
`https://[fe80::1%eth0]/x`, `https://[fe80::1%25eth0]/x` and
`https://[::1%eth0]/x`, so `tools/check_references.py` would accept a
`sources.txt` row citing any of them as a well-formed absolute URL. RFC 3986's
`IPv6address` has no zone identifier, so a `%` in a bracketed host is
malformed while the provenance check reported it clean.

**Cause:** `_is_ip_literal` fell through to `ipaddress.IPv6Address`, which
accepts a `%scope` suffix (a zone identifier) that RFC 3986 does not include;
the `_IPV_FUTURE` branch never sees one because its character class has no
`%`.

**Fix:** `_is_ip_literal` rejects a bracketed host holding `%` before it
reaches `ipaddress.IPv6Address`, so neither a raw scope (`fe80::1%eth0`) nor
its percent-encoded form (`fe80::1%25eth0`) passes.

**Test:** `tests/test_url_check.py::TestBracketedHosts` gained the three
zone-identifier forms in `test_malformed_bracketed_hosts_are_rejected`; the
class failed on `https://[fe80::1%eth0]/x` before the fix and passes after.

**Validation gap:** unclear-invariant -- the docstring named RFC 3986 but
neither it nor the suite said that the standard library's IPv6 parser accepts
zone identifiers the RFC omits, so I had to reconstruct that boundary before I
could confirm the acceptance was a bug and not intended.

### `tools/url_check.py` accepts a malformed userinfo as a provenance citation (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role)

**Symptom:** `url_problem` returned `None` for
`https://a<b>@example.test/x`, `https://a{b}c@example.test/x`,
`https://host\name@example.test/x`, `https://user@@example.test/x`,
`https://exa%2@example.test/x` and a raw non-ASCII byte before the `@`, so
`tools/check_references.py` would accept a `sources.txt` row citing any of
them as a well-formed absolute URL. RFC 3986 makes userinfo a run of
unreserved characters, pct-encoded octets, sub-delims and colons, so each is
malformed while the provenance check reported it clean.

**Cause:** `_authority_host` took the host as `authority.rsplit("@", 1)[-1]`,
discarding everything before the last `@` without validating it; only the host
after it was checked against the reg-name rule.

**Fix:** `_authority_host` now splits the authority with `rpartition("@")` and
validates the userinfo with `_is_userinfo`, which shares the new
`_is_uri_component` scanner with `_is_reg_name` and adds the colon to its
allowed set. A malformed userinfo is rejected with "must use only userinfo
characters before '@'" before the host is parsed.

**Test:** `tests/test_url_check.py::TestUserinfoCharacters` covers both the
accepted userinfo forms (empty, `user`, `user:pass`, sub-delims, pct-encoded)
and the rejected ones; the class failed on `https://a<b>@example.test/x`
before the fix and passes after.

**Validation gap:** unclear-invariant -- the parser's guarantee for userinfo
was neither documented nor tested, so I had to reconstruct the RFC 3986
userinfo shape from the host rule before I could confirm the acceptance was a
bug and not intended.

### `tools/url_check.py` accepts an empty bracketed host (`file://[]`) as a provenance citation (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role)

**Symptom:** `url_problem` returned `None` for `file://[]/x`, `file://[]` and
`file://[]:80/x`, so `tools/check_references.py` would accept a `sources.txt`
row citing any of them as a well-formed absolute URL. RFC 3986 makes a
bracketed host an IP-literal, and an empty one (`[]`) is not an IP-literal, so
each is malformed while the provenance check reported it clean.

**Cause:** `_authority_host` treated an empty bracketed host (`host` empty
inside `[...]`) as "no host" and returned no problem; `url_problem` then let it
through because `file` is the one scheme allowed an empty host. The empty-host
allowance, meant for `file:///path`, swallowed the malformed bracketed form.

**Fix:** `_authority_host` now runs the IP-literal check on the bracketed host
unconditionally, so an empty bracketed host is rejected with "must bracket an
IPv6 or IPvFuture address" before the scheme's empty-host rule is consulted.

**Test:** `tests/test_url_check.py::TestBracketedHosts` gained the `file://[]`
forms (the class failed on `file://[]/x` before the fix and passes after).

**Validation gap:** unclear-invariant -- the module docstring said `[]` is not a
host, but I had to reconstruct how the `file`-only empty-host allowance bypasses
the bracketed-host check to confirm the acceptance was a bug and not intended.

### `tools/url_check.py` accepts an unbracketed host with non-reg-name characters (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role)

**Symptom:** `url_problem` returned `None` for `https://a<b>c.example/x`,
`https://a{b}c.example/x`, `https://host\name.example/x`,
`https://host"name.example/x`, `https://host|name.example/x`,
`https://exa%2.example/x` and a host holding a raw non-ASCII byte, so
`tools/check_references.py` would accept a `sources.txt` row citing any of them
as a well-formed absolute URL. RFC 3986 defines the unbracketed host as a
reg-name -- `*( unreserved / pct-encoded / sub-delims )` -- so each is
malformed while the provenance check reported it clean.

**Cause:** `_authority_host` only required an unbracketed host to be non-empty;
it never examined the host's characters, unlike the port and the bracketed
IP-literal checks beside it.

**Fix:** a new `_is_reg_name` helper accepts RFC 3986 unreserved characters,
sub-delims and `%HH` pct-encoded octets (rejecting a bare or short percent), and
`_authority_host` applies it to the unbracketed host. The empty host
(`file:///path`, `https://:80/p`) stays valid and is still caught by the
existing empty-host check.

**Test:** `tests/test_url_check.py::TestUnbracketedHostCharacters` (a scratch run
of `url_problem` returned `None` for the malformed hosts before the fix; the new
class fails on `https://a<b>c.example/x` before the fix and passes after).

**Validation gap:** unclear-invariant -- the module's docstring stated the
bracketed-host and port rules but never the unbracketed host's character set, so
I had to reconstruct RFC 3986's reg-name form before calling the acceptance a
bug.

### `tools/url_check.py` accepts a non-numeric or doubled port as a provenance citation (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role)

**Symptom:** `url_problem` returned `None` for `https://host:80:90/x`,
`https://host:abc/x`, `https://[::1]:80:90/x` and `https://[::1]:abc/x`, so
`tools/check_references.py` would accept a `sources.txt` row citing any of them
as a well-formed absolute URL. RFC 3986 defines a port as `*DIGIT`, so each is
malformed while the provenance check reports it clean.

**Cause:** `_authority_host` took the unbracketed host as
`hostport.split(":", 1)[0]` and ignored everything after the first colon, and
for a bracketed host it only checked that the character after `]` was a colon;
neither path examined the port's contents.

**Fix:** a new `_is_port` helper accepts only ASCII digits (an empty port, the
`host:` form, stays valid because `*DIGIT` allows zero digits), and
`_authority_host` applies it to the port after both an unbracketed host and a
bracketed one. The host and empty-host messages are unchanged.

**Test:** `tests/test_url_check.py::TestAuthorityPorts` (a scratch run of
`url_problem` returned `None` for the four malformed URLs before the fix; the
class passes after).

**Validation gap:** unclear-invariant — the module never stated the port rule,
so I had to reconstruct RFC 3986's `*DIGIT` form before I could call the
acceptance a bug.

### `test_url_check.py` fails to import when run as the only `CHECK_TESTS` module (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role)

**Symptom:** `make check CHECK_TESTS='test_url_check'` exited 2 with
`ModuleNotFoundError: No module named 'tools'` before running any test, so a
contributor could not run this module's tests on its own. The Makefile
documents `CHECK_TESTS` as a supported way to run one module, class or method.

**Cause:** `test_url_check.py` was the only `tests/test_*.py` module whose
first import was `tools.*` rather than `support`; it only ever passed because
unittest discovery imports other modules (which import `support.repo_root`,
the import that puts the repository root on `sys.path`) before it.

**Fix:** `test_url_check.py` now imports `support.repo_root` first, matching
every other test module.

**Test:** `make check CHECK_TESTS='test_url_check'` (the focused run exited 2
with the `ModuleNotFoundError` before the fix and exits 0 after).

**Validation gap:** none — the documented focused-run command reproduced the
failure and confirmed the fix.

### `tools/url_check.py` accepts a malformed bracketed host as a provenance citation (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role)

**Symptom:** `url_problem` returned `None` for `https://[]/x`,
`https://[::1/x`, `https://[not-an-ip]/x` and `https://exa[mple].test/x`, so
`tools/check_references.py` would accept a `sources.txt` row citing any of them
as a well-formed absolute URL. Each names no usable host, so the citation
points nowhere while the provenance check reports it clean.

**Cause:** the host was taken as
`authority.rsplit("@", 1)[-1].split(":", 1)[0]`, which for a bracketed
authority is the literal `[` — truthy, so the empty-host guard never fired and
the bracket contents were never examined.

**Fix:** `_authority_host` parses an RFC 3986 authority: a bracketed host must
be closed and hold an IPv6 or IPvFuture address (`_is_ip_literal`, using the
stdlib `ipaddress`), and an unbracketed host must not carry a bracket. The
empty-host message and the `file://` exemption are unchanged.

**Test:** `tests/test_url_check.py::TestBracketedHosts` (a scratch run of
`url_problem` returned `None` for the four malformed URLs before the fix; the
class passes after).

**Validation gap:** unclear-invariant — the code never stated the bracketed
host rule, so I had to reconstruct RFC 3986's IP-literal form before I could
call the acceptance a bug.

### `tests/invariants.py` lets a register reference with a NUL byte escape as an unrelated exception (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role)

**Symptom:** a register row whose test reference contained a NUL byte (the
cell regex `` `([^`]+)` `` matches NUL) made `check_reference` raise
`ValueError: lstat: embedded null character in path` from
`os.path.realpath`, an exception naming neither the register section nor the
reference, so a failing run did not say which row broke the register.
`check_reference` is documented to raise `AssertionError` naming the section
and the first missing piece.

**Cause:** `check_reference` resolved the joined path with
`os.path.realpath(file_path)` before any guard; `realpath` raises `ValueError`
(not `OSError`) for a path with an embedded NUL byte, so the repository-escape
and isfile checks never ran.

**Fix:** `check_reference` now rejects a NUL byte in the reference's path with
`AssertionError` naming the section and the reference, before it reaches
`os.path.realpath`.

**Test:**
`tests/test_invariants.py::TestHelpers::test_cross_check_rejects_a_reference_with_a_nul_byte`
(a scratch run showed the `ValueError` escaping before the fix; the test
errored before the fix and passes after).

**Validation gap:** no-fake -- confirming it needed a synthetic register row
carrying a NUL byte, a fixture the suite did not have.

- `tests/invariants.py` lets a reference to an unreadable test file escape as an unrelated exception (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 4cb013f; gap: no-fake)
- `tests/invariants.py` accepts a class whose locally defined base only looks like a test case (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit c769e5f; gap: no-observability)
- `tests/invariants.py` accepts a register reference that escapes the repository (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 24eb3a3; gap: no-observability)
- `tests/invariants.py` accepts a method reference into a class that is not a test case (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 4888e9d; gap: no-observability)
- `tests/invariants.py` accepts a register reference to a class with no tests (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 117647d; gap: no-observability)
- `tests/invariants.py` accepts a register reference to a non-test method (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 304545a; gap: no-observability)
- `tests/invariants.py` accepts a register reference with a segment after the method (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 90e6564; gap: no-observability)
- `tests/invariants.py` drops a register row that does not split into three cells (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 91c8968; gap: no-observability)
- `tests/invariants.py` drops a register row whose Test cell has no backticked reference (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit d90e79d; gap: no-observability)
- `tests/invariants.py` drops a register row whose cell contains an escaped pipe (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit ee90205; gap: no-observability)
- `tests/invariants.py` accepts a register reference ending in `::`, pinning a guarantee to no test (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit c87ada1; gap: no-observability)
- `tests/placeholders.py` ignores `PLACEHOLDER:` markers in the theme's `.kvconfig` file (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 16010b3; gap: no-observability)
- `_log_tail_lines` splits a log line on a vertical tab or other exotic break byte (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 7110891)
- `_log_tail_lines` keeps a blank first line when the tail window opens on a `\r\n` newline (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 384a7ac)
- `tests/placeholders.py` ignores `PLACEHOLDER:` markers in the theme's `.js` and `.desktoprc` files (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 21267c2; gap: no-observability)
- `org.macos8.desktop` icon theme still calls its final art "placeholder icons" (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 7cf57e0; gap: unclear-invariant)
- `make render` installs the theme outside its scratch data home when `DESTDIR` is on the outer make command line (found by the bugfix role 2026-10-18; fixed 2026-10-18 by the bugfix role; commit 28132d5)
- README lists three tools `make render` needs, but `REQUIRED_TOOLS` has six (found by the qa role 2026-10-17) — fixed 2026-10-17 by the bugfix role; commit 1ff84a5
- `make install` fails with a shell syntax error when `XDG_DATA_HOME` or `DESTDIR` contains an apostrophe (found by the bugfix role 2026-10-17; fixed 2026-10-17 by the bugfix role; commit c69c398)
- `make render` runs the whole render before reporting an unwritable output, and cannot write an output path starting with `-` (found by the bugfix role 2026-10-17; fixed 2026-10-17 by the bugfix role; commit 54ff603)
- `make render` installs the theme outside its scratch data home when `DESTDIR` is set in the environment (found by the bugfix role 2026-10-17; fixed 2026-10-17 by the bugfix role; commit 6ba6b00)
- Splash progress bar pins the panel face and the empty track as its track and fill colours (found by the plan role 2026-10-17; fixed 2026-10-17 by the bugfix role; commit fb34ec7)
- Test suite fails with 43 failures and 3 errors (found 2026-10-16; fixed 2026-10-17 by the bugfix role; commit 090a345)
- Uninstalling the scheme while it is selected leaves KDE warning `Could not find color scheme "MacOS8"` (found 2026-10-09; fixed 2026-10-09; commit c2b0481; gap: real-run-needed)
- Palette anchors are not re-derivable from the reference screenshots (structural risk, found 2026-10-07; fixed 2026-10-08; commit e723886; gap: no-observability)
- Selection palette anchor is not re-derivable (found 2026-10-07; fixed 2026-10-08; commit df1bedd; gap: unclear-invariant)
- `--tolerance` does not gate the fidelity exit status; README documents no pass threshold (found 2026-10-07; fixed 2026-10-07; commit 14c6530)
- `plasma-apply-colorscheme` writes a scheme ID that does not survive a restart (found 2026-10-07; fixed 2026-10-07; commit aac7aa7; gap: real-run-needed)
- No objective fidelity check for "pixel-perfect" (structural risk, found 2026-10-07; fixed 2026-10-07; commit 2b0b3d5; gap: unclear-invariant)
