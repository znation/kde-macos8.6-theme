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
`$XDG_DATA_HOME/fonts/org.macos8.desktop`; it does not select it. Selecting
the installed families in KDE/Plasma/Qt is a later part of the UI-font series.
