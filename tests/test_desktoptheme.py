"""Validate the org.macos8.desktop Plasma desktop theme package."""

import os
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET

from install_failure_cases import FailedInstallPreservesPackage
from kde_config import read as read_kde_config
from package_metadata import PackageMetadata, load_metadata
from theme_install import (
    ROOT,
    assert_files_identical,
    install,
    installed_package,
    installed_plasma_dir,
    old_sibling,
    run,
    shadow_command_env,
    staging_sibling,
    uninstall,
)

DTHEME_ID = "org.macos8.desktop"
PACKAGE = os.path.join(ROOT, "theme", "desktop-themes", DTHEME_ID)
METADATA = os.path.join(PACKAGE, "metadata.json")
PANEL_SVG = os.path.join(PACKAGE, "widgets", "panel-background.svg")
FRAME_SVG = os.path.join(PACKAGE, "widgets", "frame.svg")
FRAME_PREFIXES = ("plain", "raised", "sunken")
BUTTON_SVG = os.path.join(PACKAGE, "widgets", "button.svg")
BUTTON_PREFIXES = ("normal", "pressed", "focus")
BUTTON_MARGIN_HINTS = (
    "hint-top-margin", "hint-bottom-margin",
    "hint-left-margin", "hint-right-margin",
)
RADIOBUTTON_SVG = os.path.join(PACKAGE, "widgets", "radiobutton.svg")
CHECKMARKS_SVG = os.path.join(PACKAGE, "widgets", "checkmarks.svg")

LNF_DEFAULTS = os.path.join(
    ROOT, "theme", "look-and-feel", DTHEME_ID, "contents", "defaults"
)
# configparser reads the KDE `[plasmarc][Theme]` header greedily, so the
# section key includes the inner bracket pair.
PLASMA_SECTION = "plasmarc][Theme"

SLICE_IDS = [
    "center", "top", "bottom", "left", "right",
    "topleft", "topright", "bottomleft", "bottomright",
]
HINT_IDS = [
    "hint-tile-center",
    "hint-top-margin", "hint-bottom-margin",
    "hint-left-margin", "hint-right-margin",
    "hint-top-inset", "hint-bottom-inset",
    "hint-left-inset", "hint-right-inset",
]

# Every pixel of each raised/sunken 3x3 corner slice, row-major in slice-local
# coordinates. The bevel must turn the corner: the edge bevel colours continue
# into the corner and meet there. A corner that stops the bevel one pixel short
# leaves a face-coloured (#DDDDDD) notch where the side tile shows highlight or
# shadow, so pinning the pixels makes that defect fail the suite.
CORNER_PIXELS = {
    "raised": {
        "topleft": (
            "#000000", "#000000", "#000000",
            "#000000", "#FFFFFF", "#FFFFFF",
            "#000000", "#FFFFFF", "#DDDDDD",
        ),
        "topright": (
            "#000000", "#000000", "#000000",
            "#FFFFFF", "#999999", "#000000",
            "#DDDDDD", "#999999", "#000000",
        ),
        "bottomleft": (
            "#000000", "#FFFFFF", "#DDDDDD",
            "#000000", "#999999", "#999999",
            "#000000", "#000000", "#000000",
        ),
        "bottomright": (
            "#DDDDDD", "#999999", "#000000",
            "#999999", "#999999", "#000000",
            "#000000", "#000000", "#000000",
        ),
    },
    "sunken": {
        "topleft": (
            "#000000", "#000000", "#000000",
            "#000000", "#999999", "#999999",
            "#000000", "#999999", "#DDDDDD",
        ),
        "topright": (
            "#000000", "#000000", "#000000",
            "#999999", "#FFFFFF", "#000000",
            "#DDDDDD", "#FFFFFF", "#000000",
        ),
        "bottomleft": (
            "#000000", "#999999", "#DDDDDD",
            "#000000", "#FFFFFF", "#FFFFFF",
            "#000000", "#000000", "#000000",
        ),
        "bottomright": (
            "#DDDDDD", "#FFFFFF", "#000000",
            "#FFFFFF", "#FFFFFF", "#000000",
            "#000000", "#000000", "#000000",
        ),
    },
}

# Every pixel of each panel-background edge/corner slice, row-major in
# slice-local coordinates (the centre tile is checked separately). The menu-bar
# bevel must run the right way: #FFFFFF on the outer top/left edge, #999999 on
# the inner bottom edge and the outer right edge, and the #000000 rule on the
# outer bottom edge. `test_platinum_colours_present` sees the same four fills
# whichever way the bevel runs, so only pinning the pixels catches a swapped
# highlight/shadow or the black rule moved to the wrong edge.
PANEL_EDGE_PIXELS = {
    "top": (8, 2, ("#FFFFFF",) * 8 + ("#DDDDDD",) * 8),
    "bottom": (8, 2, ("#999999",) * 8 + ("#000000",) * 8),
    "left": (2, 8, ("#FFFFFF", "#DDDDDD") * 8),
    "right": (2, 8, ("#DDDDDD", "#999999") * 8),
    "topleft": (2, 2, ("#FFFFFF", "#FFFFFF", "#FFFFFF", "#DDDDDD")),
    "topright": (2, 2, ("#FFFFFF", "#999999", "#DDDDDD", "#999999")),
    "bottomleft": (2, 2, ("#999999", "#999999", "#000000", "#000000")),
    "bottomright": (2, 2, ("#999999", "#999999", "#000000", "#000000")),
}


def local_name(element):
    """Return *element*'s tag without its `{namespace}` prefix.

    Each SVG declares the default SVG namespace, so ElementTree reports a tag
    as `{http://www.w3.org/2000/svg}rect`; these tests match on the local name.
    """
    return element.tag.rsplit("}", 1)[-1]


def render_slices(tree):
    """Composite each id-bearing <g> of a nine-slice SVG into a {(x, y): fill} map.

    The frame's corner slices and the button's edge slices are both read this
    way. Coordinates are slice-local: the groups are pure translations, so a
    slice's appearance is its rects painted in document order, with a later
    rect overriding an earlier one as KSvg composites one nine-slice tile.
    """
    slices = {}
    for group in tree.iter():
        if local_name(group) != "g" or not group.get("id"):
            continue
        pixels = {}
        for rect in group:
            if local_name(rect) != "rect":
                continue
            x = int(rect.get("x", 0))
            y = int(rect.get("y", 0))
            for dx in range(int(rect.get("width"))):
                for dy in range(int(rect.get("height"))):
                    pixels[(x + dx, y + dy)] = rect.get("fill")
        slices[group.get("id")] = pixels
    return slices


class TestMetadata(PackageMetadata, unittest.TestCase):
    METADATA_PATH = METADATA
    PACKAGE_STRUCTURE = "Plasma/Theme"
    PACKAGE_ID = DTHEME_ID
    PLASMA_API_KEY = "X-Plasma-API"
    PLASMA_API_VERSION = "5.0"


class TestPanelBackground(unittest.TestCase):
    def setUp(self):
        self.tree = ET.parse(PANEL_SVG)
        self.ids = {el.get("id") for el in self.tree.iter() if el.get("id")}

    def test_nine_slice_ids_present(self):
        for name in SLICE_IDS:
            self.assertIn(name, self.ids, name)

    def test_hint_ids_present(self):
        for name in HINT_IDS:
            self.assertIn(name, self.ids, name)

    def test_platinum_colours_present(self):
        # Read the parsed artwork's fill attributes, not the raw file: the
        # header comment names all four colours, so a text search would pass
        # even if the artwork used none of them.
        fills = {el.get("fill") for el in self.tree.iter() if el.get("fill")}
        self.assertEqual(
            fills, {"#FFFFFF", "#DDDDDD", "#999999", "#000000"}
        )

    def test_panel_background_pixels(self):
        # `test_platinum_colours_present` pins only the set of fills, so a
        # highlight/shadow swap or a rule on the wrong edge passes it. Read
        # each edge/corner slice's pixels in paint order instead.
        slices = render_slices(self.tree)
        for name, (width, height, expected) in PANEL_EDGE_PIXELS.items():
            pixels = slices[name]
            actual = tuple(
                pixels.get((x, y))
                for y in range(height)
                for x in range(width)
            )
            with self.subTest(slice=name):
                self.assertEqual(actual, expected, name)
        # The centre tile is one body rect, so every pixel is the same face.
        center = slices["center"]
        self.assertEqual(set(center.values()), {"#DDDDDD"})
        self.assertEqual(len(center), 8 * 8)

    def test_no_script_elements(self):
        for element in self.tree.iter():
            tag = local_name(element)
            self.assertFalse(tag.endswith("script"), tag)


class TestButton(unittest.TestCase):
    def test_button_slice_ids(self):
        tree = ET.parse(BUTTON_SVG)
        ids = {el.get("id") for el in tree.iter() if el.get("id")}
        for prefix in BUTTON_PREFIXES:
            for name in SLICE_IDS:
                self.assertIn(f"{prefix}-{name}", ids, name)
            for hint in BUTTON_MARGIN_HINTS:
                self.assertIn(f"{prefix}-{hint}", ids, hint)
        self.assertIn("hint-tile-center", ids)

    def test_button_colours(self):
        # Read the parsed artwork's fill attributes, not the raw file: the
        # header comment and the hint rects (which set colour through `style`)
        # would otherwise make a text search pass without any Platinum grey.
        tree = ET.parse(BUTTON_SVG)
        fills = {el.get("fill") for el in tree.iter() if el.get("fill")}
        self.assertEqual(
            fills, {"#FFFFFF", "#DDDDDD", "#999999", "#000000"}
        )

    def test_no_script_elements(self):
        tree = ET.parse(BUTTON_SVG)
        for element in tree.iter():
            tag = local_name(element)
            self.assertFalse(tag.endswith("script"), tag)

    def test_button_bevel_direction(self):
        # `test_button_colours` sees the same four fills whichever way the
        # normal/pressed bevels run, so only the per-slice paint order pins
        # the direction: normal is #FFFFFF inside top/left and #999999 inside
        # bottom/right, and pressed is the exact inverse. Composite the edge
        # slices (their rects) and read the corner paths' document order.
        slices = render_slices(ET.parse(BUTTON_SVG))
        # (outer outline, bevel, inner face), from the slice's outer edge in.
        outward = {
            "normal-top": ("#000000", "#FFFFFF", "#DDDDDD"),
            "normal-bottom": ("#000000", "#999999", "#DDDDDD"),
            "normal-left": ("#000000", "#FFFFFF", "#DDDDDD"),
            "normal-right": ("#000000", "#999999", "#DDDDDD"),
            "pressed-top": ("#000000", "#999999", "#DDDDDD"),
            "pressed-bottom": ("#000000", "#FFFFFF", "#DDDDDD"),
            "pressed-left": ("#000000", "#999999", "#DDDDDD"),
            "pressed-right": ("#000000", "#FFFFFF", "#DDDDDD"),
        }
        for name, colours in outward.items():
            pixels = slices[name]
            horizontal = name.endswith(("top", "bottom"))
            reversed_axis = name.endswith(("bottom", "right"))
            for depth, colour in enumerate(colours):
                local = 2 - depth if reversed_axis else depth
                point = (0, local) if horizontal else (local, 0)
                with self.subTest(slice=name, depth=depth):
                    self.assertEqual(pixels.get(point), colour, name)

        # The corner paths carry no rects, so `render_slices` cannot composite
        # them; pin the order they are painted in instead: the black outline,
        # the corner's bevel colour, then the face.
        tree = ET.parse(BUTTON_SVG)
        groups = {
            el.get("id"): el for el in tree.iter()
            if local_name(el) == "g" and el.get("id")
        }
        corners = {
            "normal-topleft": ("#000000", "#FFFFFF", "#DDDDDD"),
            "normal-topright": ("#000000", "#FFFFFF", "#999999", "#DDDDDD"),
            "normal-bottomleft": ("#000000", "#FFFFFF", "#999999", "#DDDDDD"),
            "normal-bottomright": ("#000000", "#999999", "#DDDDDD"),
            "pressed-topleft": ("#000000", "#999999", "#DDDDDD"),
            "pressed-topright": ("#000000", "#999999", "#FFFFFF", "#DDDDDD"),
            "pressed-bottomleft": ("#000000", "#999999", "#FFFFFF", "#DDDDDD"),
            "pressed-bottomright": ("#000000", "#FFFFFF", "#DDDDDD"),
        }
        for name, colours in corners.items():
            fills = tuple(
                child.get("fill")
                for child in groups[name]
                if local_name(child) == "path"
            )
            with self.subTest(corner=name):
                self.assertEqual(fills, colours, name)

    def test_button_focus_ring_pixels(self):
        # The focus state is a 1px #000000 ring on the outer pixel of its 2px
        # border, transparent inside and in the centre, so ButtonFocus draws
        # it 1-2px outside the button outline. `test_button_colours` sees the
        # same four fills whichever pixel of the border is painted, so only
        # pinning the pixels keeps the ring from sliding to the inner pixel,
        # being recoloured to another Platinum grey, or the centre from being
        # filled in.
        slices = render_slices(ET.parse(BUTTON_SVG))
        expected = {
            "focus-top": {(x, 0): "#000000" for x in range(8)},
            "focus-bottom": {(x, 1): "#000000" for x in range(8)},
            "focus-left": {(0, y): "#000000" for y in range(8)},
            "focus-right": {(1, y): "#000000" for y in range(8)},
            "focus-center": {},
        }
        for name, pixels in expected.items():
            with self.subTest(slice=name):
                self.assertEqual(slices[name], pixels, name)

        # The rounded corners are paths, so `render_slices` cannot composite
        # them; pin that each carries exactly the one black ring path.
        tree = ET.parse(BUTTON_SVG)
        groups = {
            el.get("id"): el for el in tree.iter()
            if local_name(el) == "g" and el.get("id")
        }
        for name in (
            "focus-topleft", "focus-topright",
            "focus-bottomleft", "focus-bottomright",
        ):
            with self.subTest(corner=name):
                self.assertEqual(
                    [
                        child.get("fill") for child in groups[name]
                        if local_name(child) == "path"
                    ],
                    ["#000000"],
                    name,
                )


class TestRadioButton(unittest.TestCase):
    def test_radiobutton_contract(self):
        tree = ET.parse(RADIOBUTTON_SVG)
        ids = {el.get("id") for el in tree.iter() if el.get("id")}
        for name in ("normal", "symbol", "hint-size"):
            self.assertIn(name, ids, name)
        fills = {el.get("fill") for el in tree.iter() if el.get("fill")}
        self.assertEqual(fills, {"#FFFFFF", "#000000"})
        for element in tree.iter():
            tag = local_name(element)
            self.assertFalse(tag.endswith("script"), tag)

    def test_radiobutton_geometry(self):
        # The black ring is a filled circle under the white face, so the two
        # normal circles must stay r=8 over r=7 (a 1px outline), and the
        # selected dot must stay r=3 (a 6x6 symbol). Pin each circle's fill
        # with its radius: the contract test only checks the fill set, so a
        # swap of the two faces (black face, white ring) would otherwise pass.
        tree = ET.parse(RADIOBUTTON_SVG)
        by_id = {el.get("id"): el for el in tree.iter() if el.get("id")}
        circles = [
            el for el in by_id["normal"]
            if local_name(el) == "circle"
        ]
        self.assertEqual(
            [(float(el.get("r")), el.get("fill")) for el in circles],
            [(8, "#000000"), (7, "#FFFFFF")],
        )
        symbol = by_id["symbol"]
        self.assertEqual(float(symbol.get("r")), 3)
        self.assertEqual(symbol.get("fill"), "#000000")


class TestCheckmarks(unittest.TestCase):
    def test_checkmarks_contract(self):
        tree = ET.parse(CHECKMARKS_SVG)
        ids = {el.get("id") for el in tree.iter() if el.get("id")}
        for name in ("checkbox", "radiobutton"):
            self.assertIn(name, ids, name)
        strokes = {el.get("stroke") for el in tree.iter() if el.get("stroke")}
        self.assertEqual(strokes, {"#000000"})
        fills = {el.get("fill") for el in tree.iter() if el.get("fill")}
        self.assertEqual(fills, {"none", "#000000"})
        for element in tree.iter():
            tag = local_name(element)
            self.assertFalse(tag.endswith("script"), tag)

    def test_checkmarks_geometry(self):
        # The consumers anchor the SvgItem with `anchors.fill`, so KSvg scales
        # each element by its bounds. Without the invisible full-cell bounding
        # rect the checkbox path's natural ~12x9 bounds (and the 6x6 dot)
        # would stretch to the 16x16 cell; pin the group, the rect, and the
        # glyph so that scaling cannot creep back in.
        tree = ET.parse(CHECKMARKS_SVG)
        by_id = {el.get("id"): el for el in tree.iter() if el.get("id")}

        checkbox = by_id["checkbox"]
        self.assertEqual(local_name(checkbox), "g")
        check_rects = [el for el in checkbox if local_name(el) == "rect"]
        check_paths = [el for el in checkbox if local_name(el) == "path"]
        self.assertEqual(len(check_rects), 1)
        self.assertEqual(len(check_paths), 1)
        self.assertEqual(
            [check_rects[0].get(k) for k in ("x", "y", "width", "height", "fill")],
            ["0", "0", "16", "16", "none"],
        )
        self.assertEqual(
            check_paths[0].get("d"),
            "M 3.5,8.5 L 6.5,11.5 L 12.5,5.5",
        )
        self.assertEqual(check_paths[0].get("stroke-width"), "2")
        self.assertEqual(check_paths[0].get("fill"), "none")

        radiobutton = by_id["radiobutton"]
        self.assertEqual(local_name(radiobutton), "g")
        radio_rects = [el for el in radiobutton if local_name(el) == "rect"]
        radio_circles = [el for el in radiobutton if local_name(el) == "circle"]
        self.assertEqual(len(radio_rects), 1)
        self.assertEqual(len(radio_circles), 1)
        self.assertEqual(
            [radio_rects[0].get(k) for k in ("x", "y", "width", "height", "fill")],
            ["0", "16", "16", "16", "none"],
        )
        self.assertEqual(float(radio_circles[0].get("r")), 3)
        self.assertEqual(radio_circles[0].get("fill"), "#000000")


class TestFrame(unittest.TestCase):
    def test_frame_svg_contract(self):
        tree = ET.parse(FRAME_SVG)
        ids = {el.get("id") for el in tree.iter() if el.get("id")}
        for prefix in FRAME_PREFIXES:
            for name in SLICE_IDS:
                self.assertIn(f"{prefix}-{name}", ids, name)
            for side in ("top", "bottom", "left", "right"):
                self.assertIn(f"{prefix}-hint-{side}-margin", ids, side)
        self.assertIn("hint-tile-center", ids)
        # Read the raw file for the palette: the frame's hints deliberately
        # avoid the Platinum colours, so every hit here comes from the artwork.
        with open(FRAME_SVG, encoding="utf-8") as handle:
            text = handle.read()
        for colour in ("#DDDDDD", "#FFFFFF", "#999999", "#000000"):
            self.assertIn(colour, text)
        for element in tree.iter():
            tag = local_name(element)
            self.assertFalse(tag.endswith("script"), tag)

    def test_frame_corner_bevels_turn_the_corner(self):
        slices = render_slices(ET.parse(FRAME_SVG))
        for prefix, corners in CORNER_PIXELS.items():
            for name, expected in corners.items():
                pixels = slices[f"{prefix}-{name}"]
                actual = tuple(
                    pixels.get((x, y))
                    for y in range(3)
                    for x in range(3)
                )
                self.assertEqual(actual, expected, f"{prefix}-{name}")

    def test_frame_plain_corners_are_flat(self):
        # `test_frame_corner_bevels_turn_the_corner` pins only the raised and
        # sunken corners, and `test_frame_edge_bevels` does not reach the
        # corners, so a plain corner that copy-pasted a bevel from a
        # neighbouring state leaves a #FFFFFF or #999999 pixel where the face
        # should be and passes every existing test. Pin every plain-corner
        # pixel: the face plus the 1px black outline on the two outer edges,
        # with no bevel.
        slices = render_slices(ET.parse(FRAME_SVG))
        expected = {
            "plain-topleft": (
                "#000000", "#000000", "#000000",
                "#000000", "#DDDDDD", "#DDDDDD",
                "#000000", "#DDDDDD", "#DDDDDD",
            ),
            "plain-topright": (
                "#000000", "#000000", "#000000",
                "#DDDDDD", "#DDDDDD", "#000000",
                "#DDDDDD", "#DDDDDD", "#000000",
            ),
            "plain-bottomleft": (
                "#000000", "#DDDDDD", "#DDDDDD",
                "#000000", "#DDDDDD", "#DDDDDD",
                "#000000", "#000000", "#000000",
            ),
            "plain-bottomright": (
                "#DDDDDD", "#DDDDDD", "#000000",
                "#DDDDDD", "#DDDDDD", "#000000",
                "#000000", "#000000", "#000000",
            ),
        }
        for name, colours in expected.items():
            pixels = slices[name]
            actual = tuple(
                pixels.get((x, y))
                for y in range(3)
                for x in range(3)
            )
            with self.subTest(corner=name):
                self.assertEqual(actual, colours, name)

    def test_frame_edge_bevels(self):
        # `test_frame_corner_bevels_turn_the_corner` pins only the raised and
        # sunken corners; the edge slices carry the same bevel along the frame
        # and are otherwise checked by id alone, so a raised top painted with
        # the shadow colour (or a plain edge that grew a bevel) passes every
        # existing test. Pin each edge's pixels from its outer edge in, and
        # each state's centre tile to the face.
        slices = render_slices(ET.parse(FRAME_SVG))
        # (outer outline, bevel, inner face) read from the slice's outer edge
        # inward; plain has no bevel, so its middle band is the face.
        outward = {
            "plain": ("#000000", "#DDDDDD", "#DDDDDD"),
            "raised": ("#000000", "#FFFFFF", "#DDDDDD"),
            "sunken": ("#000000", "#999999", "#DDDDDD"),
        }
        # The bottom/right edges mirror the top/left: the outline stays on the
        # outer edge while the bevel colour swaps sides.
        mirrored = {
            "plain": ("#DDDDDD", "#DDDDDD", "#000000"),
            "raised": ("#DDDDDD", "#999999", "#000000"),
            "sunken": ("#DDDDDD", "#FFFFFF", "#000000"),
        }
        for prefix in FRAME_PREFIXES:
            for side in ("top", "bottom", "left", "right"):
                band = (
                    outward if side in ("top", "left") else mirrored
                )[prefix]
                horizontal = side in ("top", "bottom")
                if horizontal:
                    # Three 6px rows, one per band colour.
                    expected = (band[0],) * 6 + (band[1],) * 6 + (band[2],) * 6
                    points = ((x, y) for y in range(3) for x in range(6))
                else:
                    # Six 3px rows, each running outer to inner.
                    expected = band * 6
                    points = ((x, y) for y in range(6) for x in range(3))
                pixels = slices[f"{prefix}-{side}"]
                actual = tuple(pixels.get(point) for point in points)
                with self.subTest(slice=f"{prefix}-{side}"):
                    self.assertEqual(actual, expected, f"{prefix}-{side}")
            # The centre tile is one body rect, so every pixel is the face.
            with self.subTest(slice=f"{prefix}-center"):
                self.assertEqual(
                    slices[f"{prefix}-center"],
                    {(x, y): "#DDDDDD" for y in range(6) for x in range(6)},
                )

    def test_frame_installed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = install(tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            target = os.path.join(
                installed_package(tmp, "desktoptheme", DTHEME_ID),
                "widgets", "frame.svg",
            )
            assert_files_identical(self, FRAME_SVG, target)
            again = install(tmp)
            self.assertEqual(again.returncode, 0, again.stderr)


class TestDefaultsWiring(unittest.TestCase):
    def test_defaults_select_the_desktop_theme(self):
        parser = read_kde_config(LNF_DEFAULTS)
        self.assertEqual(
            parser.get(PLASMA_SECTION, "name"),
            load_metadata(METADATA)["KPlugin"]["Id"],
        )


class TestInstall(FailedInstallPreservesPackage, unittest.TestCase):
    KIND = "desktoptheme"
    PACKAGE_ID = DTHEME_ID

    def reinstall_failure_env(self, tmp):
        # Shadow `cp` with a fake that fails only when copying the desktop
        # theme (the look-and-feel copy must still succeed), writing part of
        # the tree then dying like a killed or out-of-space `cp` would.
        real_cp = shutil.which("cp")
        return shadow_command_env(
            tmp,
            "cp",
            "#!/bin/sh\n"
            'case "$2" in\n'
            "  */desktop-themes/*)\n"
            '    dest="$3/$(basename "$2")"\n'
            '    mkdir -p "$dest"\n'
            '    printf partial > "$dest/metadata.json"\n'
            "    exit 1;;\n"
            "esac\n"
            f'exec "{real_cp}" "$@"\n',
        )

    def test_make_install_copies_package_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = install(tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            installed = installed_package(tmp, "desktoptheme", DTHEME_ID)
            for name in (
                "metadata.json",
                os.path.join("widgets", "panel-background.svg"),
                os.path.join("widgets", "button.svg"),
                os.path.join("widgets", "radiobutton.svg"),
                os.path.join("widgets", "checkmarks.svg"),
            ):
                source = os.path.join(PACKAGE, name)
                target = os.path.join(installed, name)
                assert_files_identical(self, source, target, name)

    def test_make_install_is_repeatable(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = install(tmp)
            self.assertEqual(first.returncode, 0, first.stderr)
            second = install(tmp)
            self.assertEqual(second.returncode, 0, second.stderr)

    def test_make_uninstall_removes_the_installed_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            installed = install(tmp)
            self.assertEqual(installed.returncode, 0, installed.stderr)
            parent = installed_plasma_dir(tmp, "desktoptheme")
            package = os.path.join(parent, DTHEME_ID)
            self.assertTrue(os.path.isdir(package), package)

            # SIGKILL cannot be trapped, so an install killed in the swap
            # window leaves a hidden staging directory and the moved-aside old
            # package behind. `uninstall` must remove those leftovers too.
            leaked = [
                staging_sibling(parent, DTHEME_ID),
                old_sibling(parent, DTHEME_ID),
            ]
            for path in leaked:
                os.makedirs(path)
                with open(
                    os.path.join(path, "metadata.json"), "w", encoding="utf-8"
                ) as handle:
                    handle.write("{}")

            removed = uninstall(tmp)
            self.assertEqual(removed.returncode, 0, removed.stderr)
            self.assertFalse(os.path.exists(package), package)
            for path in leaked:
                self.assertFalse(
                    os.path.exists(path),
                    f"{path} leaked after uninstall",
                )

            again = uninstall(tmp)
            self.assertEqual(again.returncode, 0, again.stderr)


@unittest.skipUnless(
    shutil.which("plasma-apply-desktoptheme"),
    "needs plasma-apply-desktoptheme",
)
class TestApplyDesktopTheme(unittest.TestCase):
    def test_apply_lists_and_selects_the_theme(self):
        with tempfile.TemporaryDirectory() as tmp:
            installed = install(tmp)
            self.assertEqual(installed.returncode, 0, installed.stderr)
            env = dict(
                os.environ,
                XDG_DATA_HOME=os.path.join(tmp, "share"),
                XDG_CONFIG_HOME=os.path.join(tmp, "config"),
            )
            listed = run(
                ["plasma-apply-desktoptheme", "--list-themes"],
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(listed.returncode, 0, listed.stderr)
            self.assertIn(DTHEME_ID, listed.stdout)
            applied = run(
                ["plasma-apply-desktoptheme", DTHEME_ID],
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(applied.returncode, 0, applied.stderr)
            parser = read_kde_config(os.path.join(tmp, "config", "plasmarc"))
            self.assertEqual(parser.get("Theme", "name"), DTHEME_ID)


@unittest.skipUnless(shutil.which("kpackagetool6"), "needs kpackagetool6")
class TestPackageValid(unittest.TestCase):
    def test_kpackagetool6_installs_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run(
                [
                    "kpackagetool6", "-t", "Plasma/Theme",
                    "-p", tmp, "-i", PACKAGE,
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(
                os.path.isfile(os.path.join(tmp, DTHEME_ID, "metadata.json"))
            )


if __name__ == "__main__":
    unittest.main()
