"""Direct tests for tools/session_bus.py.

The `apply_theme` and `apply_keymap` suites exercise the defaulted address
through their command stubs; these pin the helper's own contract. The branch
no caller test reaches is an absolute `XDG_RUNTIME_DIR` whose `bus` socket
does not exist: the environment must be returned unchanged instead of pointing
a session tool at a socket that is not there.
"""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import tmp_dir
from tools import session_bus


class TestSessionEnv(unittest.TestCase):
    def setUp(self):
        self.directory = tmp_dir.make_tmp_dir(self)

    def test_an_existing_address_is_returned_unchanged(self):
        self.assertEqual(
            {"XDG_RUNTIME_DIR": str(self.directory),
             "DBUS_SESSION_BUS_ADDRESS": "unix:path=/existing"},
            session_bus.session_env(
                {"XDG_RUNTIME_DIR": str(self.directory),
                 "DBUS_SESSION_BUS_ADDRESS": "unix:path=/existing"}
            ),
        )

    def test_an_absolute_runtime_dir_with_a_bus_socket_names_it(self):
        (self.directory / "bus").write_text("", encoding="utf-8")
        self.assertEqual(
            {"XDG_RUNTIME_DIR": str(self.directory),
             "DBUS_SESSION_BUS_ADDRESS": f"unix:path={self.directory}/bus"},
            session_bus.session_env({"XDG_RUNTIME_DIR": str(self.directory)}),
        )

    def test_an_absolute_runtime_dir_without_a_bus_socket_is_left_unchanged(self):
        # The runtime directory names a session only when its bus socket is
        # present; defaulting to a socket that is not there would send the
        # session tools at a path the bus never listens on.
        self.assertEqual(
            {"XDG_RUNTIME_DIR": str(self.directory)},
            session_bus.session_env({"XDG_RUNTIME_DIR": str(self.directory)}),
        )

    def test_a_relative_runtime_dir_is_left_unchanged(self):
        # A relative runtime dir cannot name the session's socket, so no
        # address is defaulted even when a sibling 'bus' path would resolve.
        self.assertEqual(
            {"XDG_RUNTIME_DIR": "relative/rt"},
            session_bus.session_env({"XDG_RUNTIME_DIR": "relative/rt"}),
        )

    def test_an_empty_runtime_dir_is_left_unchanged(self):
        # An empty XDG_RUNTIME_DIR is not an absolute directory, so it cannot
        # name a bus socket; the address stays unset rather than becoming a
        # path relative to the current directory.
        self.assertEqual(
            {"XDG_RUNTIME_DIR": ""},
            session_bus.session_env({"XDG_RUNTIME_DIR": ""}),
        )

    def test_an_absent_runtime_dir_is_left_unchanged(self):
        # Neither variable may be carried, so the lookup must treat the
        # absent XDG_RUNTIME_DIR as "no runtime directory", not as a KeyError.
        self.assertEqual({}, session_bus.session_env({}))


if __name__ == "__main__":
    unittest.main()
