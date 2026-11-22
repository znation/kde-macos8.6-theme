"""Pin what the render session inherits from and drops from caller environment."""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401
from support.render.stub_tools import StubTools
from tools.render import session as render_session


class TestRenderEnvironment(StubTools, unittest.TestCase):
    def test_session_receives_the_geometry_and_the_themed_configs(self):
        record = self.root / "args"
        self.stub(
            "dbus-run-session",
            f'echo "$@" > "{record}"; cat "$XDG_CONFIG_HOME/kwinrc" >> "{record}";'
            f' echo "$XDG_DATA_HOME $WAYLAND_DISPLAY $DISPLAY" >> "{record}"',
        )
        with mock.patch.dict(os.environ, {"WAYLAND_DISPLAY": "wl", "DISPLAY": ":9"}):
            self.run_main("--width", "64", "--height", "48", "--applet", "a b")
        text = record.read_text(encoding="utf-8")
        self.assertIn("--width 64 --height 48", text)
        self.assertIn("--socket render-surface", text)
        self.assertIn("theme=org.macos8.desktop", text)
        self.assertIn("--exit-with-session", text)
        last = text.splitlines()[-1].split()
        self.assertTrue(Path(last[0]).parent.name.startswith("render-surface-"))
        self.assertEqual(
            ["render-surface"],
            last[1:],
            "the session did not get its own socket, or DISPLAY leaked",
        )

    def test_session_ignores_a_config_search_path_from_the_environment(self):
        record = self.root / "config-dirs"
        self.stub("dbus-run-session", f'printf "%s" "$XDG_CONFIG_DIRS" > "{record}"')
        with mock.patch.dict(os.environ, {"XDG_CONFIG_DIRS": str(self.root / "ambient")}):
            self.run_main()
        self.assertEqual(
            "",
            record.read_text(encoding="utf-8"),
            "the caller's XDG_CONFIG_DIRS leaked into the render session",
        )

    def test_session_pins_the_nested_bus_to_a_display_free_qt_platform(self):
        record = self.root / "qt-platform"
        self.stub("dbus-run-session", f'printf "%s" "$QT_QPA_PLATFORM" > "{record}"')
        with mock.patch.dict(os.environ, {"QT_QPA_PLATFORM": "wayland"}):
            self.run_main()
        self.assertEqual(
            "offscreen",
            record.read_text(encoding="utf-8"),
            "the caller's QT_QPA_PLATFORM leaked into the render session, or the "
            "activated services were left free to open the nested Wayland socket",
        )

    def test_session_script_keeps_the_clients_on_the_nested_compositor_platform(self):
        script = render_session.session_script()
        self.assertIn(
            "export QT_QPA_PLATFORM=wayland; ",
            script,
            "the session script no longer re-pins the client to the nested "
            "compositor's wayland platform, while the session subtree is pinned "
            "to a display-free one",
        )

    def test_install_ignores_a_destdir_from_the_environment(self):
        record = self.root / "make-env"
        self.stub("make", f'echo "[$DESTDIR] $*" > "{record}"')
        with mock.patch.dict(os.environ, {"DESTDIR": str(self.root / "stage")}):
            self.run_main()
        argv = record.read_text(encoding="utf-8")
        self.assertTrue(argv.startswith("[] install XDG_DATA_HOME="), argv)

    def test_install_ignores_makefiles_from_the_environment(self):
        marker = self.root / "makefiles-executed"
        injected_makefile = self.root / "injected.mk"
        injected_makefile.write_text(f"$(shell touch '{marker}')\n", encoding="utf-8")
        self.stub("make", f'exec "{self.real_make}" "$@"')
        with mock.patch.dict(os.environ, {"MAKEFILES": str(injected_makefile)}):
            self.run_main()
        self.assertFalse(
            marker.exists(), "caller-controlled MAKEFILES ran during the render install"
        )

    def test_install_ignores_a_destdir_from_the_outer_make_command_line(self):
        record = self.root / "make-destdir"
        makefile = self.root / "install.mk"
        makefile.write_text(
            f'install:\n\t@echo "[$(DESTDIR)]" > "{record}"\n', encoding="utf-8"
        )
        self.stub("make", f'exec "{self.real_make}" -f "{makefile}" "$@"')
        with mock.patch.dict(os.environ, {"MAKEFLAGS": f"-- DESTDIR={self.root / 'stage'}"}):
            self.run_main()
        self.assertEqual("[]", record.read_text(encoding="utf-8").strip())


if __name__ == "__main__":
    unittest.main()
