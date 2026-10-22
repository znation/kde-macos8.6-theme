"""Tests for the splash QML's structure, which need no reference image."""

from __future__ import annotations

import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import splash_fixtures
from support import snippet_child
from support.splash_fixtures import object_source, qml_unit_expression, read_qml
from tools import containment as tools_containment


class TestSplashQml(unittest.TestCase):
    """QML structure checks that need no reference image.

    They run in a clone without the LFS thumbnail, where ``SplashReferenceCase``
    skips; the logo source and the ``stage`` binding must still be checked.
    """

    def test_uses_the_logo_image(self):
        self.assertIn('source: "images/macos-logo.svg"', read_qml())

    def test_logo_rasterizes_at_its_displayed_size(self):
        # `test_uses_the_logo_image` pins the source path and
        # `test_grid_geometry` pins the 26x21 grid rect it is drawn into, but
        # nothing pins the size the SVG is rasterized at. The SVG's intrinsic
        # size is that same 26x21, so on any `unit` above 1 (the splash scales
        # its whole grid by whole pixels) an Image without `sourceSize` would
        # load a 26x21 bitmap and scale it up, softening the logo while every
        # geometry and colour test still passed. Bind the raster size to the
        # item's displayed size.
        logo = object_source(read_qml(), "logo")
        self.assertIn("sourceSize.width: width", logo)
        self.assertIn("sourceSize.height: height", logo)

    def test_logo_loads_asynchronously(self):
        # The logo is a rasterized SVG; without `asynchronous: true` Qt decodes
        # it on the UI thread while the splash is already on screen, stalling
        # the first frame. The flag is the only part of the Image left
        # unpinned, and dropping it would pass every geometry and colour test.
        logo = object_source(read_qml(), "logo")
        self.assertIn("asynchronous: true", logo)

    def test_progress_fill_follows_stage(self):
        # The fill width binds to the KDE splash `stage` (0..6). Pin the
        # binding, or a fill that ignores `stage` would look plausible but never advance.
        self.assertIn(
            "width: parent.width * Math.min(1, root.stage / 6)", read_qml()
        )

    def test_progress_fill_stretches_to_the_track_height(self):
        # The fill's width binding is pinned above, but its vertical extent is
        # not. The fill declares no `height` of its own, so it is drawn only
        # because `anchors.top` and `anchors.bottom` stretch it to the track's
        # inside; dropping either collapses it to a 0px line, an empty-looking
        # progress well, while the width test and every colour test still pass.
        # `anchors.left` places its origin on the track's left edge. Pin all
        # three so the fill keeps spanning the well as the stage advances.
        fill = object_source(read_qml(), "fill")
        self.assertIn("anchors.left: parent.left", fill)
        self.assertIn("anchors.top: parent.top", fill)
        self.assertIn("anchors.bottom: parent.bottom", fill)

    def test_unit_scales_the_reference_grid_without_collapsing(self):
        # Every geometry binding is a reference-grid literal times `root.unit`,
        # but no test pinned `unit` itself. A definition that dropped the
        # `Math.max(1, ...)` floor would let `unit` reach 0 on a window smaller
        # than the 240x180 grid and collapse the whole splash, while every
        # geometry binding still read correctly. Pin the exact scale: one whole
        # pixel per reference-grid pixel, floored at 1.
        self.assertEqual(
            qml_unit_expression(),
            "Math.max(1, Math.floor(Math.min(width / 240, height / 180)))",
        )

    def test_stage_two_starts_the_intro_animation(self):
        # The QML follows Breeze's stage protocol: the splash stays hidden
        # until the session reaches stage 2, then fades in. `stage` drives
        # both the progress fill and this reveal, but only the fill was
        # pinned. Dropping the handler, changing the stage it tests, or
        # assigning a different animator would leave the splash permanently
        # invisible while every other test still passed. Tie the stage number
        # to the assignment in one match so they cannot drift apart.
        match = re.search(
            r"onStageChanged:\s*\{\s*if \(stage == (\d+)\)\s*\{\s*"
            r"introAnimation\.running = true\s*\}",
            read_qml(),
        )
        self.assertIsNotNone(
            match, "onStageChanged must start introAnimation"
        )
        self.assertEqual(match.group(1), "2")

    def test_intro_animation_fades_content_in(self):
        # The reveal is only correct as a whole chain: `content` must start
        # transparent, and the animator must target that same item and fade it
        # from 0 to 1. A retargeted animator, or a `content` that starts
        # opaque (a visible flash before the fade), would otherwise pass every
        # other test while looking wrong on screen.
        qml = read_qml()
        self.assertIn("opacity: 0", object_source(qml, "content"))
        animator = object_source(qml, "introAnimation")
        self.assertIn("target: content", animator)
        self.assertIn("from: 0", animator)
        self.assertIn("to: 1", animator)

    def test_intro_animation_uses_the_reference_timing(self):
        # The fade chain above pins where the animation goes, but not how long
        # it takes or how it eases. Dropping `duration` falls back to Qt's
        # 250ms default and dropping `easing.type` to Linear, so the reveal
        # would snap to its midpoint and run at a third of the authored speed
        # while every other test still passed. Pin both literals together.
        animator = object_source(read_qml(), "introAnimation")
        self.assertIn("duration: 800", animator)
        self.assertIn("easing.type: Easing.InOutQuad", animator)

    def test_content_is_the_centred_reference_grid(self):
        # Every child rect is positioned in the 240x180 reference grid, but the
        # `content` item those coordinates are relative to is unpinned: if its
        # size dropped a grid literal, or its `anchors.centerIn` moved the
        # item's origin off centre, the whole composition would shrink or
        # shift while every child-binding and colour test still passed.
        # `anchors.centerIn` centres the item's own rect, so its size and its
        # anchor are one position and must be pinned together.
        content = object_source(read_qml(), "content")
        self.assertIn("width: 240 * root.unit", content)
        self.assertIn("height: 180 * root.unit", content)
        self.assertIn("anchors.centerIn: parent", content)

    def test_wordmark_sits_on_the_panel_at_its_reference_position(self):
        # The "Mac OS 8.6" wordmark is the only element placed relative to the
        # panel rather than the grid: `test_wordmark_colour_matches_reference`
        # pins its colour and `test_reference_colours_are_painted` its colour
        # binding, but nothing pins where it is drawn. A changed `y` literal or
        # a dropped `anchors.horizontalCenter` would slide the wordmark off the
        # panel while every colour and rectangle test still passed.
        wordmark = object_source(read_qml(), "wordmark")
        self.assertIn("y: 71 * root.unit", wordmark)
        self.assertIn(
            "anchors.horizontalCenter: panel.horizontalCenter", wordmark
        )

    def test_wordmark_shows_the_reference_label_at_its_grid_size(self):
        # Where the wordmark sits and what colour it is are pinned, but not the
        # label it draws or the size it draws it at. `test_wordmark_colour_
        # matches_reference` samples one of its glyph pixels and the position
        # test pins that pixel's location, yet a changed `text` or a dropped
        # `font.pixelSize` (Text would then fall back to the application's
        # default font, at a different size) would leave every other test
        # green. Pin the label and the reference-grid size together.
        wordmark = object_source(read_qml(), "wordmark")
        self.assertIn('text: "Mac OS 8.6"', wordmark)
        self.assertIn("font.pixelSize: 12 * root.unit", wordmark)

    def test_reference_colours_are_painted(self):
        """Each anchor colour must be bound to the object at its reference rect.

        A declared colour property proves nothing about the screen: the pixel
        and geometry tests would still pass if no object bound the colour, or
        bound it to the wrong rectangle. This ties every anchor colour property
        to the object whose geometry literals ``test_grid_geometry`` pins to
        the reference rectangle, so the pair can only hold when that object
        paints that colour over that rectangle.
        """
        qml = read_qml()
        self.assertIn("color: root.fieldColor", qml)
        expected = {
            "bevel": (
                "color: root.panelBevelColor",
                "x: root.bevelX * root.unit",
                "y: root.bevelY * root.unit",
                "width: root.bevelWidth * root.unit",
                "height: root.bevelHeight * root.unit",
            ),
            "panel": (
                "color: root.panelColor",
                "border.color: root.panelRuleColor",
                "x: root.panelX * root.unit",
                "y: root.panelY * root.unit",
                "width: root.panelWidth * root.unit",
                "height: root.panelHeight * root.unit",
            ),
            "track": (
                "color: root.trackColor",
                "x: root.trackX * root.unit",
                "y: root.trackY * root.unit",
                "width: root.trackWidth * root.unit",
                "height: root.trackHeight * root.unit",
            ),
            "fill": ("color: root.fillColor",),
            "wordmark": ("color: root.wordmarkColor",),
        }
        for object_id, bindings in expected.items():
            block = object_source(qml, object_id)
            for binding in bindings:
                self.assertIn(binding, block, f"{object_id}: {binding}")


class TestSplashQmlContainment(unittest.TestCase):
    """`read_qml` must refuse an unusable contributor file, not hang or crash."""

    def test_refuses_an_oversize_file_instead_of_loading_it_whole(self):
        # Splash.qml is contributor-supplied, so a stray multi-gigabyte file
        # must not be loaded whole: a plain read would allocate it and raise a
        # MemoryError naming neither the file nor the guard. The shared reader
        # refuses one past its cap by name instead.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = tmp / "repo"
            root.mkdir()
            splash = root / "Splash.qml"
            splash.write_bytes(b"x" * (tools_containment._MAX_READ_BYTES + 1))
            with mock.patch.object(splash_fixtures, "ROOT", root), \
                    mock.patch.object(splash_fixtures, "SPLASH", splash):
                with self.assertRaises(ValueError) as caught:
                    splash_fixtures.read_qml()
        self.assertIn(str(splash), str(caught.exception))
        self.assertIn("larger than", str(caught.exception))

    def test_refuses_a_fifo_instead_of_blocking(self):
        # A FIFO at the Splash.qml path blocks open() until a writer appears,
        # and read_qml has no timeout, so one stray pipe would stall the whole
        # suite with no diagnostic. Run it in a child so the pre-fix hang is a
        # bounded timeout rather than a stalled run.
        if not hasattr(os, "mkfifo"):
            self.skipTest("os.mkfifo is not available on this platform")
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = tmp / "repo"
            root.mkdir()
            fifo = root / "Splash.qml"
            os.mkfifo(fifo)
            child = snippet_child.run(
                [
                    "import sys; import support.splash_fixtures as f; "
                    "f.ROOT, f.SPLASH = sys.argv[1], sys.argv[2]; "
                    "f.read_qml()",
                    str(root),
                    str(fifo),
                ],
                cwd=os.path.dirname(__file__),
                timeout=10,
            )
        self.assertNotEqual(0, child.returncode, child.stdout + child.stderr)
        self.assertIn("not a regular file", child.stderr)
        self.assertIn(str(fifo), child.stderr)

    def test_rejects_a_symlink_that_escapes_the_repository(self):
        # Splash.qml is contributor-supplied, and a checked-in symlink can
        # point at a private file; the QML probes and `assertIn` checks echo
        # its lines into a failing test's diagnostic, so following the symlink
        # would leak that file's content. A path that resolves outside the
        # repository must be refused before it is opened.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = tmp / "repo"
            root.mkdir()
            secret = tmp / "secret.qml"
            secret.write_text("PRIVATE-SECRET\n", encoding="utf-8")
            link = root / "Splash.qml"
            link.symlink_to(secret)
            with mock.patch.object(splash_fixtures, "ROOT", root), \
                    mock.patch.object(splash_fixtures, "SPLASH", link):
                with self.assertRaises(ValueError) as caught:
                    splash_fixtures.read_qml()
        self.assertIn(str(link), str(caught.exception))

    def test_allows_a_symlink_that_stays_within_the_repository(self):
        # The guard must refuse only escapes, not a legitimate repository path
        # that happens to be reached through a symlink inside the repository.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = tmp / "repo"
            (root / "theme").mkdir(parents=True)
            target = root / "theme" / "Splash.qml"
            target.write_text("// inside\n", encoding="utf-8")
            link = root / "link.qml"
            link.symlink_to(target)
            with mock.patch.object(splash_fixtures, "ROOT", root), \
                    mock.patch.object(splash_fixtures, "SPLASH", link):
                self.assertEqual(
                    splash_fixtures.read_qml(), "// inside\n"
                )


if __name__ == "__main__":
    unittest.main()
