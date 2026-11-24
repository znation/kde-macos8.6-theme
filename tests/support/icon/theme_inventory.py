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
# the shared-library `application-x-sharedlib` icon at all three sizes
# (our own drawing of that window holding a two-bar stack; the name is
# the type-spelled `application/x-sharedlib` MIME type in the installed
# shared MIME database), the Python-bytecode `application-x-python-bytecode`
# icon at all three sizes (our own drawing of that window holding a black
# chip; the name is the type-spelled `application/x-python-bytecode` MIME
# type in the installed shared MIME database, where the `*.pyc` and
# `*.pyo` globs both map),
# the backup-file `application-x-trash` icon at
# all three sizes (our own drawing of that window holding a black tilde;
# the name is the canonical `application/x-trash` MIME type in the
# installed shared MIME database, where the `.bak`, `.old`, `.sik`, `~`
# and `%` globs all map),
# the PGP-keys `application-pgp-keys` icon at all three sizes
# (our own drawing of that window holding a skeleton key; the name is
# the type-spelled icon name of the `application/pgp-keys` MIME type in
# the installed shared MIME database),
# the shell-script `application-x-shellscript` icon at all three sizes
# (our own drawing of a document with a terminal prompt), the core-dump
# `application-x-core` icon at all three sizes (our own drawing of that
# document with a crash-core band; the name is the type-spelled icon
# name of the `application/x-core` MIME type in the installed shared
# MIME database), the Android-package
# `application-vnd.android.package-archive` icon at all three sizes
# (our own drawing of that document with a zipper band; the name is
# the type-spelled icon name of the `application/vnd.android.package-archive`
# MIME type in the installed shared MIME database), the package
# `package-x-generic` icon at all three sizes (our own drawing of a sealed
# box; the name is the `generic-icon` of the archive and package MIME types
# in the installed shared MIME database), the ZIP-archive
# `application-zip` icon at all three sizes (our own drawing of that
# sealed box with a zipper slider tab riding its tape stripe; the name
# is the type-spelled `application/zip` MIME type in the installed
# shared MIME database), the tar-archive
# `application-x-tar` icon at all three sizes (our own drawing of that
# sealed box with a black capital letter T standing on its white body;
# the name is the type-spelled `application/x-tar` MIME type in the
# installed shared MIME database), the office-document
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
# `application/x-shellscript`, already draws its own shipped icon and
# another, `application/x-perl`, now ships its own type-spelled icon
# beside these paths), the desktop-launcher
# `application-x-desktop` icon at all three sizes (our own drawing of the
# generic document's page holding a small window; the name is the
# type-spelled `application/x-desktop` MIME type in the installed shared
# MIME database), the
# office-presentation
# `x-office-presentation` icon at all three sizes (our own drawing of the
# generic document's page holding a slide; the name is the `generic-icon`
# of the presentation MIME types in the installed shared MIME database),
# the contact-book
# `x-office-address-book` icon at all three sizes (our own drawing of a
# closed address book; the name is read by KMail's recipient chooser in
# the installed `libkmailprivate.so.6` and by the installed GTK 3, GTK 4
# and appstream-glib libraries),
# the template
# `text-x-generic-template` icon at all three sizes (our own drawing of
# the generic document's page holding a stencil plate; the name is the
# `generic-icon` of the template MIME types in the installed shared MIME
# database),
# the web-document
# `text-html` icon at all three sizes (our own drawing of a window
# holding a globe), the mail
# `internet-mail` icon at all three sizes (our own drawing of an envelope
# with a flap; the name is the item icon of `mailto:` URL items read from
# the installed KIO core), the PDF document
# `application-pdf` icon at all three sizes (the generic document's page
# under text lines and a seal plate; the name is the type-spelled icon
# name of the `application/pdf` MIME type in the installed shared MIME
# database), the 7z-archive
# `application-x-7z-compressed` icon at all three sizes (the sealed
# package box holding a stepped numeral 7; the name is the type-spelled
# icon name of the `application/x-7z-compressed` MIME type in the
# installed shared MIME database), the gzip-archive
# `application-gzip` icon at all three sizes (the sealed
# package box holding a downward arrow; the name is the type-spelled
# icon name of the `application/gzip` MIME type in the
# installed shared MIME database), the deb-package
# `application-vnd.debian.binary-package` icon at all three sizes (the
# sealed package box holding a black capital letter D; the name is the
# type-spelled icon name of the `application/vnd.debian.binary-package`
# MIME type in the installed shared MIME database), the
# gzip-compressed-tar-archive
# `application-x-compressed-tar` icon at all three sizes (the sealed
# package box holding a stepped capital Z; the name is the type-spelled
# icon name of the `application/x-compressed-tar` MIME type in the
# installed shared MIME database), the RAR-archive
# `application-vnd.rar` icon at all three sizes (the sealed
# package box holding a stepped diamond; the name is the type-spelled
# icon name of the `application/vnd.rar` MIME type in the
# installed shared MIME database), the bzip2-compressed-tar-archive
# `application-x-bzip2-compressed-tar` icon at all three sizes (the
# sealed package box holding a lowercase letter b; the name is the
# type-spelled icon name of the `application/x-bzip2-compressed-tar`
# MIME type in the installed shared MIME database), the ISO disc-image
# `application-vnd.efi.iso` icon at all three sizes (the optical disc the
# media-optical icon draws holding a black capital letter I; the name is
# the type-spelled icon name of the `application/vnd.efi.iso` MIME type
# in the installed shared MIME database), the Squashfs filesystem-image
# `application-vnd.squashfs` icon at all three sizes (the optical disc
# the media-optical icon draws holding three white tapering bands; the
# name is the type-spelled icon name of the `application/vnd.squashfs`
# MIME type in the installed shared MIME database), the QCOW disk-image
# `application-x-qemu-disk` icon at all three sizes (the optical disc
# the media-optical icon draws holding a white Q; the name is the
# type-spelled icon name of the `application/x-qemu-disk` MIME type in
# the installed shared MIME database), the flash-media
# `media-flash`
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
# `generic-icon` binding, so one file covers exactly its own name), the headset
# `audio-headset` icon at all three sizes (our own drawing of a headset with
# a headband, two ear cups and a mic boom; the name is a KDE-required value
# read from `libKF6BluezQt.so.6`, the installed
# `libKF6BluezQt.so.6.13.0` carries the bare `audio-headset` literal, and the
# shared MIME database gives the name no `generic-icon` binding, so one file
# covers exactly its own name), the scanner
# `scanner` icon at all three sizes (our own drawing of a flatbed scanner
# seen from above: a landscape body with an outline and bevels, a closed lid
# holding a white glass strip with a scan-lamp bar and a status LED at the
# larger sizes; the name is a KDE-required value read from the installed
# print-manager's `libkcupslib.so.6.3.5`, which carries the bare `scanner`
# literal, and the shared MIME database gives the name no `generic-icon`
# binding, so one file covers exactly its own name), the phone
# `phone` icon at all three sizes (our own drawing of an upright smartphone
# with a screen, a speaker slot above it and a home button below; the name
# is the device name KDE's device views draw for phones and the dash
# fallback of the `phone-apple-iphone` device icon),
# the kicker logo the menu bar's top-left button shows at the two panel sizes,
# the `media-eject` eject glyph the file dialogs' eject control draws (our own
# triangle and bar; no reference screenshot shows an eject glyph),
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
    os.path.join("32x32", "devices", "audio-headset.svg"),
    os.path.join("16x16", "devices", "audio-headset.svg"),
    os.path.join("22x22", "devices", "audio-headset.svg"),
    os.path.join("32x32", "devices", "scanner.svg"),
    os.path.join("16x16", "devices", "scanner.svg"),
    os.path.join("22x22", "devices", "scanner.svg"),
    os.path.join("32x32", "devices", "phone.svg"),
    os.path.join("16x16", "devices", "phone.svg"),
    os.path.join("22x22", "devices", "phone.svg"),
    # The `smartphone` icon at all three sizes shares the `phone` art: the
    # name is the device name KDE Connect and plasma-nm draw phone-type
    # devices with and the shared MIME database gives the name no binding,
    # so one file covers exactly its own name.
    os.path.join("32x32", "devices", "smartphone.svg"),
    os.path.join("16x16", "devices", "smartphone.svg"),
    os.path.join("22x22", "devices", "smartphone.svg"),
    os.path.join("32x32", "devices", "battery.svg"),
    os.path.join("16x16", "devices", "battery.svg"),
    os.path.join("22x22", "devices", "battery.svg"),
    # The digital-camera control module's camera (the name is required by
    # the installed `kcm_kamera.desktop` entry).
    os.path.join("32x32", "devices", "camera-photo.svg"),
    os.path.join("16x16", "devices", "camera-photo.svg"),
    os.path.join("22x22", "devices", "camera-photo.svg"),
    # The screen-capture tool's video camera (the name is required by
    # the installed `spectacle`).
    os.path.join("32x32", "devices", "camera-video.svg"),
    os.path.join("16x16", "devices", "camera-video.svg"),
    os.path.join("22x22", "devices", "camera-video.svg"),
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
    os.path.join("32x32", "mimetypes", "application-x-sharedlib.svg"),
    os.path.join("16x16", "mimetypes", "application-x-sharedlib.svg"),
    os.path.join("22x22", "mimetypes", "application-x-sharedlib.svg"),
    # The WIM disk-image `application-x-ms-wim` icon at all three sizes (our
    # own drawing of the program window with a black split image plate; the
    # name is the type-spelled icon name of the `application/x-ms-wim` MIME
    # type in the installed shared MIME database, which has no `generic-icon`,
    # no aliases and no per-type fallback, and at the exact name Breeze's own
    # file beats the theme's otherwise-missing fallback).
    os.path.join("32x32", "mimetypes", "application-x-ms-wim.svg"),
    os.path.join("16x16", "mimetypes", "application-x-ms-wim.svg"),
    os.path.join("22x22", "mimetypes", "application-x-ms-wim.svg"),
    # The Python-bytecode `application-x-python-bytecode` icon at all three
    # sizes (our own drawing of that window holding a black chip; the name
    # is the type-spelled `application/x-python-bytecode` MIME type in the
    # installed shared MIME database, whose `*.pyc` and `*.pyo` globs map
    # here and which declares no `generic-icon`, no aliases and no per-type
    # fallback; at the exact name Breeze's own file beat the theme's
    # otherwise-missing fallback).
    os.path.join("32x32", "mimetypes", "application-x-python-bytecode.svg"),
    os.path.join("16x16", "mimetypes", "application-x-python-bytecode.svg"),
    os.path.join("22x22", "mimetypes", "application-x-python-bytecode.svg"),
    # The backup-file `application-x-trash` icon at all three sizes (our
    # own drawing of that window holding a black tilde; the name is the
    # canonical `application/x-trash` MIME type in the installed shared
    # MIME database, which has no `generic-icon`, no aliases and no
    # per-type fallback, and at the exact name Breeze's own file beats the
    # theme's otherwise-missing fallback).
    os.path.join("32x32", "mimetypes", "application-x-trash.svg"),
    os.path.join("16x16", "mimetypes", "application-x-trash.svg"),
    os.path.join("22x22", "mimetypes", "application-x-trash.svg"),
    # The PGP-keys `application-pgp-keys` icon at all three sizes (our own
    # drawing of that window holding a skeleton key; the name is the
    # type-spelled icon name of the `application/pgp-keys` MIME type in the
    # installed shared MIME database, which has no `generic-icon`, no
    # aliases and no per-type fallback, and at the exact name Breeze's own
    # file beats the theme's otherwise-missing fallback).
    os.path.join("32x32", "mimetypes", "application-pgp-keys.svg"),
    os.path.join("16x16", "mimetypes", "application-pgp-keys.svg"),
    os.path.join("22x22", "mimetypes", "application-pgp-keys.svg"),
    # The detached-signature `application-pgp-signature` icon at all three
    # sizes (our own drawing of the generic document's page with a black
    # signature stroke and underline; the name is the type-spelled icon
    # name of the `application/pgp-signature` MIME type, whose
    # MIME-database entry has no `generic-icon`, no aliases and no
    # per-type fallback, so one file covers the exact name, where Breeze's
    # own file otherwise beats the theme's missing fallback).
    os.path.join("32x32", "mimetypes", "application-pgp-signature.svg"),
    os.path.join("16x16", "mimetypes", "application-pgp-signature.svg"),
    os.path.join("22x22", "mimetypes", "application-pgp-signature.svg"),
    os.path.join("32x32", "mimetypes", "application-x-shellscript.svg"),
    os.path.join("16x16", "mimetypes", "application-x-shellscript.svg"),
    os.path.join("22x22", "mimetypes", "application-x-shellscript.svg"),
    # The core-dump `application-x-core` icon at all three sizes (our own
    # drawing of the shell-script document's page with a black band
    # holding a white square ring and dot; the name is the type-spelled
    # icon name of the `application/x-core` MIME type in the installed
    # shared MIME database, which has no `generic-icon`, no aliases and
    # no per-type fallback, and at the exact name Breeze's own file beats
    # the theme's otherwise-missing fallback).
    os.path.join("32x32", "mimetypes", "application-x-core.svg"),
    os.path.join("16x16", "mimetypes", "application-x-core.svg"),
    os.path.join("22x22", "mimetypes", "application-x-core.svg"),
    # The Android-package `application-vnd.android.package-archive` icon
    # at all three sizes (our own drawing of the shell-script document's
    # page with a black band holding interlocked zipper teeth; the name
    # is the type-spelled icon name of the `application/vnd.android.package-archive`
    # MIME type in the installed shared MIME database, which has no
    # `generic-icon`, no aliases and no per-type fallback, and at the
    # exact name Breeze's own file beats the theme's otherwise-missing
    # fallback).
    os.path.join("32x32", "mimetypes", "application-vnd.android.package-archive.svg"),
    os.path.join("16x16", "mimetypes", "application-vnd.android.package-archive.svg"),
    os.path.join("22x22", "mimetypes", "application-vnd.android.package-archive.svg"),
    # The X.509-certificate `application-pkix-cert` icon at all three sizes
    # (our own drawing of the shell-script document's page with a black
    # band holding a white award seal; the name is the type-spelled icon
    # name of the `application/pkix-cert` MIME type, whose MIME-database
    # entry has no `generic-icon`, no aliases and no per-type fallback, so
    # one file covers the exact name, where Breeze's own file otherwise
    # beats the theme's missing fallback).
    os.path.join("32x32", "mimetypes", "application-pkix-cert.svg"),
    os.path.join("16x16", "mimetypes", "application-pkix-cert.svg"),
    os.path.join("22x22", "mimetypes", "application-pkix-cert.svg"),
    # The NZB usenet-index `application-x-nzb` icon at all three sizes
    # (our own drawing of the generic document's page with index dot and
    # grey segment-bar groups; the name is the type-spelled icon name of
    # the `application/x-nzb` MIME type, whose MIME-database entry has no
    # `generic-icon`, no aliases and no per-type fallback, so one file
    # covers the exact name, where Breeze's own file otherwise beats the
    # theme's missing fallback).
    os.path.join("32x32", "mimetypes", "application-x-nzb.svg"),
    os.path.join("16x16", "mimetypes", "application-x-nzb.svg"),
    os.path.join("22x22", "mimetypes", "application-x-nzb.svg"),
    # The MHTML web-archive `application-x-mimearchive` icon at all three
    # sizes (our own drawing of the generic document's page with a black
    # paperclip; the name is the type-spelled icon name of the
    # `application/x-mimearchive` MIME type, whose MIME-database entry has
    # no `generic-icon`, no aliases and no per-type fallback, so one file
    # covers the exact name, where Breeze's own file otherwise beats the
    # theme's missing fallback).
    os.path.join("32x32", "mimetypes", "application-x-mimearchive.svg"),
    os.path.join("16x16", "mimetypes", "application-x-mimearchive.svg"),
    os.path.join("22x22", "mimetypes", "application-x-mimearchive.svg"),
    # The desktop-launcher `application-x-desktop` icon at all three sizes
    # (our own drawing of the generic document's page with a small window;
    # the name is the type-spelled icon name of the `application/x-desktop`
    # MIME type in the installed shared MIME database, whose `generic-icon`
    # is the shipped `text-x-generic`, and at the exact name Breeze's own
    # file beats the theme's generic-icon fallback).
    os.path.join("32x32", "mimetypes", "application-x-desktop.svg"),
    os.path.join("16x16", "mimetypes", "application-x-desktop.svg"),
    os.path.join("22x22", "mimetypes", "application-x-desktop.svg"),
    os.path.join("32x32", "mimetypes", "text-x-script.svg"),
    os.path.join("16x16", "mimetypes", "text-x-script.svg"),
    os.path.join("22x22", "mimetypes", "text-x-script.svg"),
    # The JSON-document `application-json` icon at all three sizes (our own
    # drawing of the generic document's page with a pair of black curly
    # braces; the name is the type-spelled icon name of the
    # `application/json` MIME type in the installed shared MIME database,
    # whose `generic-icon` is the shipped `text-x-script`, and at the exact
    # name Breeze's own file beats the theme's generic-icon fallback).
    os.path.join("32x32", "mimetypes", "application-json.svg"),
    os.path.join("16x16", "mimetypes", "application-json.svg"),
    os.path.join("22x22", "mimetypes", "application-json.svg"),
    # The Perl-script `application-x-perl` icon at all three sizes (our own
    # drawing of the generic document's page with a black capital P; the
    # name is the type-spelled icon name of the `application/x-perl` MIME
    # type in the installed shared MIME database, whose `generic-icon` is
    # the shipped `text-x-script`, and at the exact name Breeze's own file
    # beats the theme's generic-icon fallback).
    os.path.join("32x32", "mimetypes", "application-x-perl.svg"),
    os.path.join("16x16", "mimetypes", "application-x-perl.svg"),
    os.path.join("22x22", "mimetypes", "application-x-perl.svg"),
    # The BitTorrent-file `application-x-bittorrent` icon at all three
    # sizes (our own drawing of the generic document's page with a black
    # band holding a white download arrow over a tray; the name is the
    # type-spelled icon name of the `application/x-bittorrent` MIME type
    # in the installed shared MIME database, which has no `generic-icon`
    # and no aliases, and at the exact name Breeze's own file beats the
    # theme's generic-icon fallback).
    os.path.join("32x32", "mimetypes", "application-x-bittorrent.svg"),
    os.path.join("16x16", "mimetypes", "application-x-bittorrent.svg"),
    os.path.join("22x22", "mimetypes", "application-x-bittorrent.svg"),
    # The SQLite-database `application-vnd.sqlite3` icon at all three sizes
    # (our own drawing of the generic document's page with a black band
    # holding a white database canister; the name is the type-spelled icon
    # name of the `application/vnd.sqlite3` MIME type in the installed
    # shared MIME database, which has no `generic-icon` and whose
    # `application/x-sqlite3` alias resolves to the canonical name, and at
    # the exact name Breeze's own file beats the theme's generic-icon
    # fallback).
    os.path.join("32x32", "mimetypes", "application-vnd.sqlite3.svg"),
    os.path.join("16x16", "mimetypes", "application-vnd.sqlite3.svg"),
    os.path.join("22x22", "mimetypes", "application-vnd.sqlite3.svg"),
    os.path.join("32x32", "mimetypes", "package-x-generic.svg"),
    os.path.join("16x16", "mimetypes", "package-x-generic.svg"),
    os.path.join("22x22", "mimetypes", "package-x-generic.svg"),
    # The type-spelled package and archive series: each name is a MIME
    # type in the installed shared MIME database (`application/zip`,
    # `application/x-tar`, `application/x-7z-compressed`,
    # `application/gzip`, `application/vnd.debian.binary-package`,
    # `application/x-compressed-tar`, `application/vnd.rar`,
    # `application/x-xz-compressed-tar`,
    # `application/x-bzip2-compressed-tar`,
    # `application/x-lzma-compressed-tar`, `application/x-cpio` and
    # `application/vnd.efi.iso`), which gives the types the
    # `package-x-generic` generic icon and no icon of their own; at the
    # exact names Breeze's own files beat the theme's generic-icon
    # fallback.
    os.path.join("32x32", "mimetypes", "application-zip.svg"),
    os.path.join("16x16", "mimetypes", "application-zip.svg"),
    os.path.join("22x22", "mimetypes", "application-zip.svg"),
    os.path.join("32x32", "mimetypes", "application-x-tar.svg"),
    os.path.join("16x16", "mimetypes", "application-x-tar.svg"),
    os.path.join("22x22", "mimetypes", "application-x-tar.svg"),
    os.path.join("32x32", "mimetypes", "application-x-7z-compressed.svg"),
    os.path.join("16x16", "mimetypes", "application-x-7z-compressed.svg"),
    os.path.join("22x22", "mimetypes", "application-x-7z-compressed.svg"),
    os.path.join("32x32", "mimetypes", "application-gzip.svg"),
    os.path.join("16x16", "mimetypes", "application-gzip.svg"),
    os.path.join("22x22", "mimetypes", "application-gzip.svg"),
    os.path.join("32x32", "mimetypes", "application-vnd.debian.binary-package.svg"),
    os.path.join("16x16", "mimetypes", "application-vnd.debian.binary-package.svg"),
    os.path.join("22x22", "mimetypes", "application-vnd.debian.binary-package.svg"),
    os.path.join("32x32", "mimetypes", "application-x-compressed-tar.svg"),
    os.path.join("16x16", "mimetypes", "application-x-compressed-tar.svg"),
    os.path.join("22x22", "mimetypes", "application-x-compressed-tar.svg"),
    os.path.join("32x32", "mimetypes", "application-vnd.rar.svg"),
    os.path.join("16x16", "mimetypes", "application-vnd.rar.svg"),
    os.path.join("22x22", "mimetypes", "application-vnd.rar.svg"),
    os.path.join("32x32", "mimetypes", "application-x-xz-compressed-tar.svg"),
    os.path.join("16x16", "mimetypes", "application-x-xz-compressed-tar.svg"),
    os.path.join("22x22", "mimetypes", "application-x-xz-compressed-tar.svg"),
    os.path.join("32x32", "mimetypes", "application-x-bzip2-compressed-tar.svg"),
    os.path.join("16x16", "mimetypes", "application-x-bzip2-compressed-tar.svg"),
    os.path.join("22x22", "mimetypes", "application-x-bzip2-compressed-tar.svg"),
    os.path.join("32x32", "mimetypes", "application-x-lzma-compressed-tar.svg"),
    os.path.join("16x16", "mimetypes", "application-x-lzma-compressed-tar.svg"),
    os.path.join("22x22", "mimetypes", "application-x-lzma-compressed-tar.svg"),
    os.path.join("32x32", "mimetypes", "application-x-cpio.svg"),
    os.path.join("16x16", "mimetypes", "application-x-cpio.svg"),
    os.path.join("22x22", "mimetypes", "application-x-cpio.svg"),
    os.path.join("32x32", "mimetypes", "application-vnd.efi.iso.svg"),
    os.path.join("16x16", "mimetypes", "application-vnd.efi.iso.svg"),
    os.path.join("22x22", "mimetypes", "application-vnd.efi.iso.svg"),
    # The Squashfs filesystem-image `application-vnd.squashfs` icon at
    # all three sizes (the optical disc the media-optical icon draws
    # holding three white tapering bands; the name is the type-spelled
    # icon name of the `application/vnd.squashfs` MIME type in the
    # installed shared MIME database).
    os.path.join("32x32", "mimetypes", "application-vnd.squashfs.svg"),
    os.path.join("16x16", "mimetypes", "application-vnd.squashfs.svg"),
    os.path.join("22x22", "mimetypes", "application-vnd.squashfs.svg"),
    # The QCOW disk-image `application-x-qemu-disk` icon at all three sizes
    # (the optical disc the media-optical icon draws holding a white Q;
    # the name is the type-spelled icon name of the `application/x-qemu-disk`
    # MIME type, whose MIME-database entry has no `generic-icon`, no aliases
    # and no per-type fallback, so one file covers the exact name, where
    # Breeze's own file otherwise beats the theme's missing fallback).
    os.path.join("32x32", "mimetypes", "application-x-qemu-disk.svg"),
    os.path.join("16x16", "mimetypes", "application-x-qemu-disk.svg"),
    os.path.join("22x22", "mimetypes", "application-x-qemu-disk.svg"),
    # The ICC color-profile `application-vnd.iccprofile` icon at all three
    # sizes (the generic document's page holding a black framed two by two
    # grid of color swatches; the name is the type-spelled icon name of
    # the `application/vnd.iccprofile` MIME type in the installed shared
    # MIME database).
    os.path.join("32x32", "mimetypes", "application-vnd.iccprofile.svg"),
    os.path.join("16x16", "mimetypes", "application-vnd.iccprofile.svg"),
    os.path.join("22x22", "mimetypes", "application-vnd.iccprofile.svg"),
    os.path.join("32x32", "mimetypes", "x-office-document.svg"),
    os.path.join("16x16", "mimetypes", "x-office-document.svg"),
    os.path.join("22x22", "mimetypes", "x-office-document.svg"),
    os.path.join("32x32", "mimetypes", "x-office-spreadsheet.svg"),
    os.path.join("16x16", "mimetypes", "x-office-spreadsheet.svg"),
    os.path.join("22x22", "mimetypes", "x-office-spreadsheet.svg"),
    os.path.join("32x32", "mimetypes", "x-office-presentation.svg"),
    os.path.join("16x16", "mimetypes", "x-office-presentation.svg"),
    os.path.join("22x22", "mimetypes", "x-office-presentation.svg"),
    os.path.join("32x32", "mimetypes", "x-office-address-book.svg"),
    os.path.join("16x16", "mimetypes", "x-office-address-book.svg"),
    os.path.join("22x22", "mimetypes", "x-office-address-book.svg"),
    os.path.join("32x32", "mimetypes", "text-html.svg"),
    os.path.join("16x16", "mimetypes", "text-html.svg"),
    os.path.join("22x22", "mimetypes", "text-html.svg"),
    os.path.join("32x32", "mimetypes", "internet-mail.svg"),
    os.path.join("16x16", "mimetypes", "internet-mail.svg"),
    os.path.join("22x22", "mimetypes", "internet-mail.svg"),
    os.path.join("32x32", "mimetypes", "application-pdf.svg"),
    os.path.join("16x16", "mimetypes", "application-pdf.svg"),
    os.path.join("22x22", "mimetypes", "application-pdf.svg"),
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
    os.path.join("16x16", "actions", "media-eject.svg"),
    os.path.join("22x22", "actions", "media-eject.svg"),
    os.path.join("32x32", "actions", "media-eject.svg"),
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
