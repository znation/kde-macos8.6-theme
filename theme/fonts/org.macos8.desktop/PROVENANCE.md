# Lato font provenance

This package ships the Lato Regular and Bold faces as the theme's
Charcoal-style body font. Lato is an approximation, not a reference anchor:
no Mac OS 8.6 screenshot in `macos8.6-screenshots/` supplies a font pixel, and
the theme does not trace or redistribute Apple's Charcoal or Chicago. The
reference crops that informed the later font parts are the menu bar in
`desktop_betawiki.png` and the `System` dialog body in
`aboutsystem_betawiki.png`.

## Source

The three files are byte-for-byte copies of the locally installed Debian
packages:

| Shipped file | Local source | SHA-256 |
| --- | --- | --- |
| `Lato-Regular.ttf` | `/usr/share/fonts/truetype/lato/Lato-Regular.ttf` | `6f6940be0835c3ddec9199e5fc42be4cbc61ebcfd58c623fdf719366253f1780` |
| `Lato-Bold.ttf` | `/usr/share/fonts/truetype/lato/Lato-Bold.ttf` | `bf1b8130069b44b9148eeece35e5423bedac49777ba746615b826b8276574a7b` |
| `LICENSE-Lato.txt` | `/usr/share/doc/fonts-lato/copyright` (Debian package `fonts-lato`) | `1e6ccc54aa0b0aa4188cda121174f17cf1c28bac9734749bbe1128bb6dd89a97` |

Upstream: `http://www.latofonts.com`, by Łukasz Dziedzic, distributed by
Debian as `fonts-lato`. The internal font family name is `Lato`.

## Licence

`LICENSE-Lato.txt` is the Debian `copyright` file copied with `cp`, including
its missing final newline: 5,157 bytes, not a 5,158-byte version with a
newline appended. The `Files: *` stanza carries the upstream copyright line
and the complete SIL Open Font License 1.1 body (`License: OFL-1.1`, with the
`PERMISSION & CONDITIONS` clause). The trailing `Files: debian/*` stanza is
Debian packaging GPL-2+ text and does not cover the fonts.

## Selection

This package installs the family under
`$XDG_DATA_HOME/fonts/org.macos8.desktop`. The global theme selects it for the
general, toolbar and smallest-readable fonts at KDE's default point sizes
(10 / 10 / 8). Monospaced text keeps the user's fixed font. ChicagoFLF supplies
the menu and window-title fonts.

# ChicagoFLF font provenance

ChicagoFLF is a Chicago-style approximation by third-party designer Robin
Casady. It is not Apple's font and is not traced from a reference screenshot;
the reference set supplies no font pixel. The unmodified family name
`ChicagoFLF` is the upstream internal font identifier, not a theme-owned UI
label.

## Source

The following files are byte-for-byte copies from the ChicagoFLF 2.1 archive
at `https://fontlibrary.org/assets/downloads/chicagoflf/a2e4a3d14e40fa7076a0a1bc06f3de43/chicagoflf.zip`,
SHA-256 `a5c1ff8aeb06505c77e6286fb63b6350494a9b030b688c212322d331d9d2278f`:

| Shipped file | Archive member | SHA-256 |
| --- | --- | --- |
| `ChicagoFLF.ttf` | `chicago/ChicagoFLF.ttf` | `b442111f37639e27572d9df0c5190e7480e6a7b01ec768aea47a154efab8d50d` |
| `README.ChicagoFLF` | `chicago/README.ChicagoFLF` | `60ca3e47853943cba1792103a1efbbb5b38797e6f249104b0e27b7fdc4943044` |

## Public domain

`README.ChicagoFLF` states “PUBLIC DOMAIN (statement from original designer
via email 2014/01/30).” The font's name records identify ID 13 as `Public
Domain` and ID 0 quotes Casady's dedication: “You are free to use them as you
wish. I consider those two in the public domain.” The archive contains a
single Regular face and no Bold face.

# JetBrains Mono font provenance

JetBrains Mono is the user-approved fixed-width face (QUESTIONS.md,
“Which monospaced font should the theme ship for fixed-width text?”, answered
2026-11-12: “option 1 … package it with the theme, like Lato”). It is an
approximation, not a reference anchor: no Mac OS 8.6 screenshot in
`macos8.6-screenshots/` supplies a terminal font surface or a font pixel, so
the face is recorded as a user-selected approximation rather than sampled
from a reference. This part installs the family only; no theme selection
names it (the global theme's defaults are unchanged, and monospaced text
still keeps the user's fixed font).

## Source

The four files are byte-for-byte copies of the Debian source package
`fonts-jetbrains-mono` version `2.304+ds-5` (trixie/main, all), downloaded
from
`http://deb.debian.org/debian/pool/main/f/fonts-jetbrains-mono/fonts-jetbrains-mono_2.304+ds-5_all.deb`,
SHA-256 `a3b42e1de29a93d8e78ae14ea6898a4534af5838ce946234ec3d8c7ab8ac271d`:

| Shipped file | Archive member | SHA-256 |
| --- | --- | --- |
| `JetBrainsMono-Regular.ttf` | `usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf` | `9fd21a629ec73a93d1665b6d8bbb73928040a290b49d2f6772505b8129e68cdc` |
| `JetBrainsMono-Medium.ttf` | `usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Medium.ttf` | `a3735d53e905b3898a23dedb2f118757be11858979e254865dc1b30ea63c0de6` |
| `JetBrainsMono-Bold.ttf` | `usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf` | `10389fb114512e1df7ca54f791b9f83572e2785e9ff1946c8197d5e5faaafd7a` |
| `LICENSE-JetBrainsMono.txt` | `usr/share/doc/fonts-jetbrains-mono/copyright` | `af1f9fe50b20580bbe159f3e7f88b0a5a201c2f7f71a0eb61ba6b39b867d1c72` |

Upstream: JetBrains s.r.o.; Debian's copyright file names the author as
Phillip Nurullin <philipp.nurullin@jetbrains.com> with source
`https://github.com/JetBrains/JetBrainsMono`, packaged as
`fonts-jetbrains-mono`. The shipped files carry the internal names the fonts'
own name tables read: `JetBrains Mono` Regular, `JetBrains Mono Medium`
Regular (Medium is exposed as its own family name, per the OFL naming
convention for non-RIBBI weights), and `JetBrains Mono` Bold. Every face's
`post` table records `isFixedPitch = 1`.

## Licence

JetBrains Mono is dual-licensed upstream: SIL Open Font License 1.1 and
Apache 2.0. This theme redistributes it under OFL-1.1, which the shipped
fonts themselves declare in their `name` table licence records (name IDs 13
and 14 name the SIL OFL licence text and `https://scripts.sil.org/OFL`);
unmodified redistribution is also permitted under the copyright file's
Apache-2 grant. `LICENSE-JetBrainsMono.txt` is the Debian package's
`copyright` file copied byte for byte (1,822 bytes). Debian records
Apache-2 as the package licence for `Files: *`; the file does not restate
the OFL grant, so the fonts' own licence records are the shipped evidence of
the OFL-1.1 basis. The trailing `Files: debian/*` stanza is Debian
packaging GPL-3+ text and does not cover the fonts.
