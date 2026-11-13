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
general, menu, toolbar, smallest-readable and window-title fonts at KDE's
default point sizes (10 / 10 / 10 / 8 / 10). Monospaced text keeps the user's
fixed font. Menus and window titles use Lato until a Chicago-style face lands.

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
