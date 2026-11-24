# Placeholders

Temporary stand-in assets shipped so the theme's plumbing works end to end. Each
is our own generic art, not a reproduction of Apple's Platinum artwork (see the
2026-10-18 answer in QUESTIONS.md). A placeholder asset carries a `PLACEHOLDER:`
comment marker naming what it stands in for; `tests/support/placeholders.py`
cross-checks this table against those markers, so a new placeholder added
without a row fails `make check`.

**Decision 2026-10-29, recorded by the director role:** The user requires original
placeholder graphics for now. This supersedes the earlier designation of the icon
art as final. The queued Platinum graphics plans in PLANS.md restore per-asset
tracking and replace the reference-cropped wallpaper.

| Placeholder | Stands in for |
| --- | --- |
| `theme/wallpapers/org.macos8.desktop/metadata.json` | original flat desktop-field stand-in pending user-approved artwork. |
| `theme/look-and-feel/org.macos8.desktop/contents/splash/images/macos-logo.svg` | original geometric startup logo pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/places/folder.svg` | original generic folder illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/actions/go-next-symbolic.svg` | original submenu-arrow illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/devices/drive-harddisk.svg` | original hard-disk illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/devices/phone.svg` | original phone illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/devices/computer.svg` | original desktop-computer illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/devices/drive-removable-media.svg` | original removable-drive illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/devices/drive-optical.svg` | original optical-drive illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/devices/media-optical.svg` | original optical-disc illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/devices/media-flash.svg` | original flash-media illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/devices/input-mouse.svg` | original mouse illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/devices/input-keyboard.svg` | original keyboard illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/devices/printer.svg` | original printer illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/devices/battery.svg` | original battery illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/mimetypes/application-octet-stream.svg` | original blank-document illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/mimetypes/application-x-zerosize.svg` | original blank-document illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/mimetypes/application-x-executable.svg` | original program illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/mimetypes/text-html.svg` | original web-document illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/mimetypes/application-x-shellscript.svg` | original shell-script illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/mimetypes/package-x-generic.svg` | original package illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/mimetypes/image-x-generic.svg` | original image illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/mimetypes/audio-x-generic.svg` | original audio illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/mimetypes/text-x-generic.svg` | original document illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/mimetypes/text-x-generic-template.svg` | original template illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/mimetypes/text-x-script.svg` | original script illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/mimetypes/x-office-document.svg` | original office-document illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/mimetypes/font-x-generic.svg` | original font illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/mimetypes/x-office-spreadsheet.svg` | original office-spreadsheet illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/mimetypes/x-office-presentation.svg` | original office-presentation illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/mimetypes/unknown.svg` | original blank-document illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/places/folder-documents.svg` | original Documents place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/places/folder-download.svg` | original Downloads place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/places/folder-downloads.svg` | original Downloads place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/places/folder-music.svg` | original Music place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/places/folder-pictures.svg` | original Pictures place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/places/folder-public.svg` | original Public place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/places/folder-temp.svg` | original Temporary Files place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/places/folder-templates.svg` | original Templates place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/places/folder-videos.svg` | original Videos place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/places/inode-directory.svg` | original directory illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/places/start-here-kde-symbolic.svg` | original menu logo illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/places/user-desktop.svg` | original Desktop place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/places/user-home.svg` | original Home place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/places/user-trash-full.svg` | original full Trash illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/16x16/places/user-trash.svg` | original Trash illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/actions/go-next-symbolic.svg` | original submenu-arrow illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/devices/drive-harddisk.svg` | original hard-disk illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/devices/phone.svg` | original phone illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/devices/computer.svg` | original desktop-computer illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/devices/drive-removable-media.svg` | original removable-drive illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/devices/drive-optical.svg` | original optical-drive illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/devices/media-optical.svg` | original optical-disc illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/devices/media-flash.svg` | original flash-media illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/devices/input-mouse.svg` | original mouse illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/devices/input-keyboard.svg` | original keyboard illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/devices/printer.svg` | original printer illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/devices/battery.svg` | original battery illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/mimetypes/application-octet-stream.svg` | original blank-document illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/mimetypes/application-x-zerosize.svg` | original blank-document illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/mimetypes/application-x-executable.svg` | original program illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/mimetypes/text-html.svg` | original web-document illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/mimetypes/application-x-shellscript.svg` | original shell-script illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/mimetypes/package-x-generic.svg` | original package illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/mimetypes/image-x-generic.svg` | original image illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/mimetypes/audio-x-generic.svg` | original audio illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/mimetypes/text-x-generic.svg` | original document illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/mimetypes/text-x-generic-template.svg` | original template illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/mimetypes/text-x-script.svg` | original script illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/mimetypes/x-office-document.svg` | original office-document illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/mimetypes/font-x-generic.svg` | original font illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/mimetypes/x-office-spreadsheet.svg` | original office-spreadsheet illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/mimetypes/x-office-presentation.svg` | original office-presentation illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/mimetypes/unknown.svg` | original blank-document illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/places/folder-documents.svg` | original Documents place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/places/folder-download.svg` | original Downloads place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/places/folder-downloads.svg` | original Downloads place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/places/folder-music.svg` | original Music place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/places/folder-pictures.svg` | original Pictures place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/places/folder-public.svg` | original Public place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/places/folder-temp.svg` | original Temporary Files place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/places/folder-templates.svg` | original Templates place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/places/folder-videos.svg` | original Videos place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/places/folder.svg` | original generic folder illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/places/inode-directory.svg` | original directory illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/places/start-here-kde-symbolic.svg` | original menu logo illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/places/user-desktop.svg` | original Desktop place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/places/user-home.svg` | original Home place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/places/user-trash-full.svg` | original full Trash illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/22x22/places/user-trash.svg` | original Trash illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/devices/drive-harddisk.svg` | original hard-disk illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/devices/phone.svg` | original phone illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/devices/computer.svg` | original desktop-computer illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/devices/drive-removable-media.svg` | original removable-drive illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/devices/drive-optical.svg` | original optical-drive illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/devices/media-optical.svg` | original optical-disc illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/devices/media-flash.svg` | original flash-media illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/devices/input-mouse.svg` | original mouse illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/devices/input-keyboard.svg` | original keyboard illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/devices/printer.svg` | original printer illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/devices/battery.svg` | original battery illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/mimetypes/application-octet-stream.svg` | original blank-document illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/mimetypes/application-x-zerosize.svg` | original blank-document illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/mimetypes/application-x-executable.svg` | original program illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/mimetypes/text-html.svg` | original web-document illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/mimetypes/application-x-shellscript.svg` | original shell-script illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/mimetypes/package-x-generic.svg` | original package illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/mimetypes/image-x-generic.svg` | original image illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/mimetypes/audio-x-generic.svg` | original audio illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/mimetypes/text-x-generic.svg` | original document illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/mimetypes/text-x-generic-template.svg` | original template illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/mimetypes/text-x-script.svg` | original script illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/mimetypes/x-office-document.svg` | original office-document illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/mimetypes/font-x-generic.svg` | original font illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/mimetypes/x-office-spreadsheet.svg` | original office-spreadsheet illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/mimetypes/x-office-presentation.svg` | original office-presentation illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/mimetypes/unknown.svg` | original blank-document illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/places/folder-documents.svg` | original Documents place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/places/folder-download.svg` | original Downloads place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/places/folder-downloads.svg` | original Downloads place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/places/folder-music.svg` | original Music place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/places/folder-pictures.svg` | original Pictures place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/places/folder-public.svg` | original Public place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/places/folder-temp.svg` | original Temporary Files place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/places/folder-templates.svg` | original Templates place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/places/folder-videos.svg` | original Videos place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/places/folder.svg` | original generic folder illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/places/inode-directory.svg` | original directory illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/places/user-desktop.svg` | original Desktop place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/places/user-home.svg` | original Home place illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/places/user-trash-full.svg` | original full Trash illustration pending user-approved artwork. |
| `theme/icons/org.macos8.desktop/32x32/places/user-trash.svg` | original Trash illustration pending user-approved artwork. |
