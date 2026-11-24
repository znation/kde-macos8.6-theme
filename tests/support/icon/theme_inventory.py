"""The icon theme package's identity and shipped-icon inventory.

``test_icon_theme`` and ``test_icon_theme_geometry`` share these constants:
the package's id and directory, the icons it ships at each size, the standard
XDG folder places and the folder aliases that draw the folder art.
"""

import os

from support.repo_root import ROOT

ICON_ID = "org.macos8.desktop"
PACKAGE = os.path.join(ROOT, "theme", "icons", ICON_ID)

# The icons the package ships: the desktop's hard disk, folder, document,
# Trash and full Trash (32x32), the `inode-directory` alias KDE resolves a
# directory to plus the `user-home` and `user-desktop` places, all drawing
# the folder art, 16x16 and 22x22 renditions of the folder, aliases, Trash
# and full Trash, 16x16 and 22x22 renditions of the hard disk and document,
# the removable-drive `drive-removable-media` icon at all three sizes (our own
# drawing of a drive with a media slot and eject button, sharing the hard
# disk's body and bevel), the optical-drive `drive-optical` icon at all three
# sizes (our own drawing of the drive family's body and bevel holding a
# centred disc, sharing the hard disk's body and bevel at 22x22 and 32x32;
# at 16x16 the body is two pixels taller so the disc fits inside the bevel),
# the program `application-x-executable` icon at
# all three sizes (our own drawing of a window holding a play triangle),
# the shell-script `application-x-shellscript` icon at all three sizes
# (our own drawing of a document with a terminal prompt), the package
# `package-x-generic` icon at all three sizes (our own drawing of a sealed
# box; the name is the `generic-icon` of the archive and package MIME types
# in the installed shared MIME database), the office-document
# `x-office-document` icon at all three sizes (our own drawing of the
# generic document's page with a heading band, body lines and a signature
# line; the name is the `generic-icon` of the document MIME types in the
# installed shared MIME database), the office-spreadsheet
# `x-office-spreadsheet` icon at all three sizes (our own drawing of the
# generic document's page holding a table; the name is the `generic-icon`
# of the spreadsheet and office-table MIME types in the installed shared
# MIME database), the script `text-x-script` icon at all three sizes
# (our own drawing of the generic document's page with angle brackets and
# code lines; the name is the `generic-icon` of 30 script MIME types in
# the installed shared MIME database, one of which,
# `application/x-shellscript`, already draws its own shipped icon), the
# office-presentation
# `x-office-presentation` icon at all three sizes (our own drawing of the
# generic document's page holding a slide; the name is the `generic-icon`
# of the presentation MIME types in the installed shared MIME database),
# the template
# `text-x-generic-template` icon at all three sizes (our own drawing of
# the generic document's page holding a stencil plate; the name is the
# `generic-icon` of the template MIME types in the installed shared MIME
# database),
# the web-document
# `text-html` icon at all three sizes (our own drawing of a window
# holding a globe), the flash-media `media-flash`
# icon at all three sizes (our own drawing of an upright card standing on
# its contact pins; the name is a KDE-required value read from
# `libKF6Solid.so.6`, which also loads it with the reduced subnames
# `media-flash-sd-mmc`, `media-flash-memory-stick` and
# `media-flash-smart-media` that one file covers), the floppy-disk
# `media-floppy` icon at all three sizes (our own drawing of a square disk
# with a shutter and a label plate; the name is a KDE-required value read
# from `libKF6Solid.so.6` and is the `generic-icon` of the
# `application/x-raw-floppy-disk-image` MIME type in the installed shared
# MIME database), the modem
# `modem` icon at all three sizes (our own drawing of an external modem
# with indicator LEDs and a telephone jack; the name is a KDE-required
# value read from `libKF6BluezQt.so.6`, the installed
# `libKF6BluezQt.so.6.13.0` carries the bare `modem` literal and no
# reduced `modem-*` subnames), the printer
# `printer` icon at all three sizes (our own drawing of a body with
# paper sheets feeding through it; the name is required by the
# installed KDE print desktop entries `org.kde.PrintQueue.desktop`,
# `org.kde.ConfigurePrinter.desktop` and `org.kde.kde-add-printer.desktop`), the
# `battery` battery icon at all three sizes (our own drawing of an upright cell
# with a terminal cap, a bevelled body, a glint at 22x22 and 32x32 and a
# charge bar; the name is a KDE-required value read from `libKF6Solid.so.6`),
# the image
# `image-x-generic` icon at all three sizes (our own drawing of a framed
# photograph; the name captures the raster image icon names by
# type-spelling fallback and is the `generic-icon` of the graphics and
# 3D-model MIME types in the installed shared MIME database), the audio
# `audio-x-generic` icon at all three sizes (our own drawing of a beamed
# pair of eighth notes; the name captures the audio MIME types by
# type-spelling fallback and is the `generic-icon` of the playlist,
# lossless-audio and SMAF audio types in the installed shared MIME
# database), the video
# `video-x-generic` icon at all three sizes (our own drawing of a display
# screen with a play triangle and a stand; the name is the `generic-icon`
# of 14 video MIME types in the installed shared MIME database —
# `application/smil+xml`, `application/vnd.ms-wpl`, `video/x-flv`,
# `video/x-javafx`, `video/vnd.youtube.yt`, `application/x-matroska`,
# `application/mxf`, `application/annodex`, `application/ogg`,
# `application/x-quicktime-media-link`,
# `application/vnd.adobe.flash.movie`, `application/vnd.rn-realmedia`,
# `application/x-netshow-channel` and `application/sdp` — and, through
# KIconLoader's generic fallback, also covers `video/mp4`, `video/webm`
# and `video/mpeg`), the font
# `font-x-generic` icon at all three sizes (our own drawing of the
# generic document's page under a capital letter A; the name is the
# `generic-icon` of the 23 font MIME types in the installed shared MIME
# database), the desktop-computer `computer` icon at all three sizes
# (our own drawing of a monitor over a desktop case; the name is a
# KDE-required value read from `libKF6Solid.so.6`), the
# `input-keyboard` keyboard at all three sizes (our own drawing of a raised
# face holding rows of keys and a space bar; the name is the input-device
# icon name KDE builds as `input-` + the device name, so the library
# carries no `input-keyboard` literal), the
# `media-optical` optical disc at all three sizes (our own drawing of a
# CD or DVD: a disc with white glints and a hub), the mouse
# `input-mouse` icon at all three sizes (our own drawing of a rounded
# mouse body with a two-button band and a scroll wheel; the name is the
# input-device icon name KDE builds from the udev subsystem), the tablet
# `input-tablet` icon at all three sizes (our own drawing of a graphics tablet
# with a white drawing surface on the left and an upright pen on the right;
# the name is a KDE-required value read from `libkwin.so.6`, which carries the
# bare `input-tablet` literal, and the shared MIME database gives the name no
# `generic-icon` binding, so one file covers exactly its own name), the phone
# `phone` icon at all three sizes (our own drawing of an upright smartphone
# with a screen, a speaker slot above it and a home button below; the name
# is the device name KDE's device views draw for phones and the dash
# fallback of the `phone-apple-iphone` device icon),
# the kicker logo the menu bar's top-left button shows at the two panel sizes,
# and the `go-next-symbolic` submenu arrow the reference's open Apple menu
# draws.
SHIPPED_ICONS = (
    os.path.join("32x32", "devices", "drive-harddisk.svg"),
    os.path.join("16x16", "devices", "drive-harddisk.svg"),
    os.path.join("22x22", "devices", "drive-harddisk.svg"),
    os.path.join("32x32", "devices", "drive-removable-media.svg"),
    os.path.join("16x16", "devices", "drive-removable-media.svg"),
    os.path.join("22x22", "devices", "drive-removable-media.svg"),
    os.path.join("32x32", "devices", "drive-optical.svg"),
    os.path.join("32x32", "devices", "media-optical.svg"),
    os.path.join("16x16", "devices", "drive-optical.svg"),
    os.path.join("16x16", "devices", "media-optical.svg"),
    os.path.join("22x22", "devices", "drive-optical.svg"),
    os.path.join("22x22", "devices", "media-optical.svg"),
    os.path.join("32x32", "devices", "media-flash.svg"),
    os.path.join("16x16", "devices", "media-flash.svg"),
    os.path.join("22x22", "devices", "media-flash.svg"),
    os.path.join("32x32", "devices", "media-floppy.svg"),
    os.path.join("16x16", "devices", "media-floppy.svg"),
    os.path.join("22x22", "devices", "media-floppy.svg"),
    os.path.join("32x32", "devices", "modem.svg"),
    os.path.join("16x16", "devices", "modem.svg"),
    os.path.join("22x22", "devices", "modem.svg"),
    os.path.join("32x32", "mimetypes", "video-x-generic.svg"),
    os.path.join("16x16", "mimetypes", "video-x-generic.svg"),
    os.path.join("22x22", "mimetypes", "video-x-generic.svg"),
    os.path.join("32x32", "devices", "printer.svg"),
    os.path.join("16x16", "devices", "printer.svg"),
    os.path.join("22x22", "devices", "printer.svg"),
    os.path.join("32x32", "devices", "computer.svg"),
    os.path.join("16x16", "devices", "computer.svg"),
    os.path.join("22x22", "devices", "computer.svg"),
    os.path.join("32x32", "devices", "input-keyboard.svg"),
    os.path.join("16x16", "devices", "input-keyboard.svg"),
    os.path.join("22x22", "devices", "input-keyboard.svg"),
    os.path.join("32x32", "devices", "input-mouse.svg"),
    os.path.join("16x16", "devices", "input-mouse.svg"),
    os.path.join("22x22", "devices", "input-mouse.svg"),
    os.path.join("32x32", "devices", "input-tablet.svg"),
    os.path.join("16x16", "devices", "input-tablet.svg"),
    os.path.join("22x22", "devices", "input-tablet.svg"),
    os.path.join("32x32", "devices", "phone.svg"),
    os.path.join("16x16", "devices", "phone.svg"),
    os.path.join("22x22", "devices", "phone.svg"),
    os.path.join("32x32", "devices", "battery.svg"),
    os.path.join("16x16", "devices", "battery.svg"),
    os.path.join("22x22", "devices", "battery.svg"),
    # The digital-camera control module's camera (the name is required by
    # the installed `kcm_kamera.desktop` entry).
    os.path.join("32x32", "devices", "camera-photo.svg"),
    os.path.join("16x16", "devices", "camera-photo.svg"),
    os.path.join("22x22", "devices", "camera-photo.svg"),
    # The VPN import tool's VPN (the name is required by the installed
    # `org.kde.vpnimport.desktop` entry).
    os.path.join("32x32", "devices", "network-vpn.svg"),
    os.path.join("16x16", "devices", "network-vpn.svg"),
    os.path.join("22x22", "devices", "network-vpn.svg"),
    os.path.join("32x32", "mimetypes", "text-x-generic.svg"),
    os.path.join("16x16", "mimetypes", "text-x-generic.svg"),
    os.path.join("22x22", "mimetypes", "text-x-generic.svg"),
    os.path.join("32x32", "mimetypes", "text-x-generic-template.svg"),
    os.path.join("16x16", "mimetypes", "text-x-generic-template.svg"),
    os.path.join("22x22", "mimetypes", "text-x-generic-template.svg"),
    os.path.join("32x32", "mimetypes", "application-x-executable.svg"),
    os.path.join("16x16", "mimetypes", "application-x-executable.svg"),
    os.path.join("22x22", "mimetypes", "application-x-executable.svg"),
    os.path.join("32x32", "mimetypes", "application-x-shellscript.svg"),
    os.path.join("16x16", "mimetypes", "application-x-shellscript.svg"),
    os.path.join("22x22", "mimetypes", "application-x-shellscript.svg"),
    os.path.join("32x32", "mimetypes", "text-x-script.svg"),
    os.path.join("16x16", "mimetypes", "text-x-script.svg"),
    os.path.join("22x22", "mimetypes", "text-x-script.svg"),
    os.path.join("32x32", "mimetypes", "package-x-generic.svg"),
    os.path.join("16x16", "mimetypes", "package-x-generic.svg"),
    os.path.join("22x22", "mimetypes", "package-x-generic.svg"),
    os.path.join("32x32", "mimetypes", "x-office-document.svg"),
    os.path.join("16x16", "mimetypes", "x-office-document.svg"),
    os.path.join("22x22", "mimetypes", "x-office-document.svg"),
    os.path.join("32x32", "mimetypes", "x-office-spreadsheet.svg"),
    os.path.join("16x16", "mimetypes", "x-office-spreadsheet.svg"),
    os.path.join("22x22", "mimetypes", "x-office-spreadsheet.svg"),
    os.path.join("32x32", "mimetypes", "x-office-presentation.svg"),
    os.path.join("16x16", "mimetypes", "x-office-presentation.svg"),
    os.path.join("22x22", "mimetypes", "x-office-presentation.svg"),
    os.path.join("32x32", "mimetypes", "text-html.svg"),
    os.path.join("16x16", "mimetypes", "text-html.svg"),
    os.path.join("22x22", "mimetypes", "text-html.svg"),
    os.path.join("32x32", "mimetypes", "image-x-generic.svg"),
    os.path.join("16x16", "mimetypes", "image-x-generic.svg"),
    os.path.join("22x22", "mimetypes", "image-x-generic.svg"),
    os.path.join("32x32", "mimetypes", "audio-x-generic.svg"),
    os.path.join("16x16", "mimetypes", "audio-x-generic.svg"),
    os.path.join("22x22", "mimetypes", "audio-x-generic.svg"),
    os.path.join("32x32", "mimetypes", "font-x-generic.svg"),
    os.path.join("16x16", "mimetypes", "font-x-generic.svg"),
    os.path.join("22x22", "mimetypes", "font-x-generic.svg"),
    # The network-server place (a freedesktop icon-naming-spec places
    # value, carried by the installed `org.kde.akonadi_kolab_resource.desktop`
    # desktop entry).
    os.path.join("32x32", "places", "network-server.svg"),
    os.path.join("16x16", "places", "network-server.svg"),
    os.path.join("22x22", "places", "network-server.svg"),
    # The display icon (the name is the plugin icon of the five installed
    # KInfoCenter information modules: EDID, GLX, EGL, OpenCL and Vulkan).
    os.path.join("32x32", "devices", "video-display.svg"),
    os.path.join("16x16", "devices", "video-display.svg"),
    os.path.join("22x22", "devices", "video-display.svg"),
    os.path.join("32x32", "places", "folder.svg"),
    os.path.join("32x32", "places", "inode-directory.svg"),
    os.path.join("32x32", "places", "user-home.svg"),
    os.path.join("32x32", "places", "user-desktop.svg"),
    os.path.join("32x32", "places", "user-trash.svg"),
    os.path.join("32x32", "places", "user-trash-full.svg"),
    os.path.join("16x16", "places", "folder.svg"),
    os.path.join("16x16", "places", "inode-directory.svg"),
    os.path.join("16x16", "places", "user-home.svg"),
    os.path.join("16x16", "places", "user-desktop.svg"),
    os.path.join("16x16", "places", "user-trash.svg"),
    os.path.join("16x16", "places", "user-trash-full.svg"),
    os.path.join("22x22", "places", "folder.svg"),
    os.path.join("22x22", "places", "inode-directory.svg"),
    os.path.join("22x22", "places", "user-home.svg"),
    os.path.join("22x22", "places", "user-desktop.svg"),
    os.path.join("22x22", "places", "user-trash.svg"),
    os.path.join("22x22", "places", "user-trash-full.svg"),
    os.path.join("16x16", "places", "start-here-kde-symbolic.svg"),
    os.path.join("22x22", "places", "start-here-kde-symbolic.svg"),
    os.path.join("16x16", "actions", "go-next-symbolic.svg"),
    os.path.join("22x22", "actions", "go-next-symbolic.svg"),
)

# The standard XDG folder places KDE resolves; the package draws each one
# with the matching size's Platinum folder, as Mac OS 8.6 draws one folder
# shape for a directory. KIO's places model names these eight names
# (read from `libKF6KIOCore.so.6`), while the standard `user-places.xbel`
# entries spell Downloads with the plural `folder-downloads` (the installed
# file's Downloads bookmark, line 58), so ship both download names.
STANDARD_PLACES = (
    "folder-documents",
    "folder-download",
    "folder-downloads",
    "folder-music",
    "folder-pictures",
    "folder-videos",
    "folder-templates",
    "folder-public",
    "folder-temp",
)
SHIPPED_ICONS += tuple(
    os.path.join(size, "places", place + ".svg")
    for size in ("16x16", "22x22", "32x32")
    for place in STANDARD_PLACES
)

# The blank-document names: files whose type KDE does not recognise, and empty
# files. `application-octet-stream` and `application-x-zerosize` are the
# `application/octet-stream` and `application/x-zerosize` MIME types spelled as
# icon names (both declared in the installed shared MIME database), and
# `unknown` is a string in the installed `libKF6KIOGui.so.6`. Each needs its
# own file: a probe showed that adding one name's file changes only that name.
BLANK_DOCUMENTS = (
    "application-octet-stream",
    "application-x-zerosize",
    "unknown",
)
SHIPPED_ICONS += tuple(
    os.path.join(size, "mimetypes", name + ".svg")
    for size in ("16x16", "22x22", "32x32")
    for name in BLANK_DOCUMENTS
)

# The standard places data's folder names that this package draws. KDE
# writes these into a user's Places list, and its Downloads entry is the
# plural `folder-downloads` rather than the `folder-download` the KIO places
# model also names; pin them separately so the inventory cannot pass by
# dropping a name KDE actually resolves.
USER_PLACES_ICONS = (
    "folder-documents",
    "folder-downloads",
    "folder-music",
    "folder-pictures",
    "folder-videos",
)

# The names that share the folder art: the KDE directory alias, the Home and
# Desktop places, and every standard XDG place.
FOLDER_ALIASES = ("inode-directory", "user-home", "user-desktop", *STANDARD_PLACES)
