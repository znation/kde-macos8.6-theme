"""Tests for the config writer's atomic publication and per-name loop.

Pins ``tools/theme_config_writer.py``: the atomic single-file writer
(``write_config_atomically``) and the per-name publication loop
(``publish_configs``), driven through direct calls and an injected writer.
``write_configs``'s name and config-home validation pins stay in
``tests/test_theme_defaults.py``.
"""

from __future__ import annotations

import os
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.close_tracking import tracking_closes
from support.tmp_dir import make_tmp_dir
from tools import theme_config_writer  # noqa: E402


def _recording_writer(recorded):
    """Patch ``write_config_atomically`` with a stand-in recording calls.

    The publication step :func:`theme_config_writer.publish_configs` uses is
    the module's ``write_config_atomically``; patching that attribute lets a
    recording stand-in pin which names the per-name loop writes and in which
    call order, without touching a real file. Use as a context manager.
    """

    def write(path, content):
        recorded.append((path.name, content))

    return mock.patch.object(theme_config_writer, "write_config_atomically", write)


def _failing_writer(failures):
    """Patch ``write_config_atomically`` to raise before its failing writes.

    A name in *failures* raises instead of writing anything; every other
    write goes through the real publication step captured before the patch,
    so the promoted file is a genuine temp-sibling-and-rename write. Use as
    a context manager.
    """

    real = theme_config_writer.write_config_atomically

    def write(path, content):
        if path.name in failures:
            raise OSError(f"simulated failure writing {path.name}")
        real(path, content)

    return mock.patch.object(theme_config_writer, "write_config_atomically", write)


class TestWriteConfigAtomically(unittest.TestCase):
    def test_failed_write_leaves_previous_config_intact(self):
        directory = make_tmp_dir(self)
        target = directory / "kwinrc"
        target.write_text("ORIGINAL\n", encoding="utf-8")
        original_mode = target.stat().st_mode & 0o777
        real_replace = os.replace
        def boom(src, dst):
            raise OSError("simulated failure")
        os.replace = boom
        try:
            with self.assertRaises(OSError):
                theme_config_writer.write_config_atomically(target, "NEW\n")
        finally:
            os.replace = real_replace
        self.assertEqual("ORIGINAL\n", target.read_text(encoding="utf-8"))
        self.assertEqual(original_mode, target.stat().st_mode & 0o777)
        # no leftover temp files
        self.assertEqual({"kwinrc"}, set(os.listdir(directory)))

    def test_failed_write_before_fdopen_closes_descriptor(self):
        directory = make_tmp_dir(self)
        target = directory / "kwinrc"
        target.write_text("ORIGINAL\n", encoding="utf-8")
        real_chmod = os.fchmod
        def boom(path, mode):
            raise OSError("simulated failure")
        os.fchmod = boom
        try:
            with tracking_closes() as closed:
                with self.assertRaises(OSError):
                    theme_config_writer.write_config_atomically(target, "NEW\n")
        finally:
            os.fchmod = real_chmod
        self.assertEqual("ORIGINAL\n", target.read_text(encoding="utf-8"))
        self.assertEqual({"kwinrc"}, set(os.listdir(directory)))
        self.assertEqual(1, len(closed))

    def test_write_preserves_existing_target_mode(self):
        directory = make_tmp_dir(self)
        target = directory / "kwinrc"
        target.write_text("ORIGINAL\n", encoding="utf-8")
        target.chmod(0o644)
        theme_config_writer.write_config_atomically(target, "NEW\n")
        self.assertEqual(0o644, target.stat().st_mode & 0o777)
        self.assertEqual("NEW\n", target.read_text(encoding="utf-8"))

    def test_write_replaces_output_symlink_without_changing_its_target(self):
        directory = make_tmp_dir(self)
        target = directory / "kwinrc"
        linked_file = directory / "linked-config"
        linked_file.write_text("KEEP\n", encoding="utf-8")
        target.symlink_to(linked_file.name)

        theme_config_writer.write_config_atomically(target, "NEW\n")

        self.assertFalse(target.is_symlink())
        self.assertEqual("NEW\n", target.read_text(encoding="utf-8"))
        self.assertEqual("KEEP\n", linked_file.read_text(encoding="utf-8"))
        self.assertEqual({"kwinrc", "linked-config"}, set(os.listdir(directory)))

    def test_removal_before_the_stat_lookup_writes(self):
        directory = make_tmp_dir(self)
        target = directory / "kwinrc"
        target.write_text("ORIGINAL\n", encoding="utf-8")
        # A partner (a KWin session saving its scratch config at exit) removes
        # the file before the stat lookup. A missing target must fall through
        # to the umask-defaulted write used for a never-present file.
        target.unlink()
        theme_config_writer.write_config_atomically(target, "NEW\n")
        self.assertEqual("NEW\n", target.read_text(encoding="utf-8"))
        self.assertEqual({"kwinrc"}, set(os.listdir(directory)))

    def test_a_stat_permission_error_refuses_without_writing(self):
        # Only an absent target reads as "no mode". A permission error from
        # the lookup must propagate: a None mode would let the writer publish
        # over a file it could not inspect, with a umask-defaulted mode.
        target = mock.Mock()
        target.stat.side_effect = PermissionError(13, "Permission denied")
        with mock.patch.object(theme_config_writer, "write_atomically") as write:
            with self.assertRaises(PermissionError):
                theme_config_writer.write_config_atomically(target, "NEW\n")
        write.assert_not_called()

    def test_a_lookup_through_a_regular_file_refuses_without_writing(self):
        # ENOTDIR is not absence either: the target's parent is a file, so the
        # stat must raise and nothing may be published beside it.
        directory = make_tmp_dir(self)
        blocker = directory / "not-a-dir"
        blocker.write_text("BLOCKER\n", encoding="utf-8")
        with mock.patch.object(theme_config_writer, "write_atomically") as write:
            with self.assertRaises(NotADirectoryError):
                theme_config_writer.write_config_atomically(blocker / "kwinrc", "NEW\n")
        write.assert_not_called()
        self.assertEqual("BLOCKER\n", blocker.read_text(encoding="utf-8"))
        self.assertEqual({"not-a-dir"}, set(os.listdir(directory)))

    def test_new_file_mode_respects_umask(self):
        directory = make_tmp_dir(self)
        target = directory / "kwinrc"
        old = os.umask(0o022)
        try:
            theme_config_writer.write_config_atomically(target, "NEW\n")
        finally:
            os.umask(old)
        self.assertEqual(0o644, target.stat().st_mode & 0o777)


class TestPublishConfigs(unittest.TestCase):
    # The writer's parameterization is only direct-call code: in the tree it
    # runs exclusively through theme_defaults.write_configs, whose tests alone
    # can only pin the DEFAULTS-pinned success shape and wrapper-level
    # rejection shapes. The tests below pin the injected-write shapes against
    # the module's own doc comments: the writer receives one call per wanted
    # name, each carrying \n-joined [group]/key=value/trailing-blank lines;
    # every name and the config home are validated before the first write
    # fires; a mid-loop failure leaves the earlier configs written and no
    # temp, staging or backup sibling behind for any name.

    def test_rejects_a_non_pathlib_config_home_through_the_injected_writer(self):
        # The direct entry's config-home guard must refuse a plain string
        # name before any write, not after the loop has started with a
        # config home whose write only a MagicMock standing in for the
        # config home (where a mkdir call would be a no-op and the paths
        # would be recorded on a fake object) observes.
        recorded = []
        with self.assertRaises(ValueError) as caught, _recording_writer(recorded):
            theme_config_writer.publish_configs(
                "somewhere/config",
                ("kwinrc",),
                defaults_path=make_tmp_dir(self) / "defaults",
                read_groups=lambda _path: {},
            )
        self.assertIn("config_home must be a pathlib.Path", str(caught.exception))
        self.assertEqual([], recorded)

    def test_rejects_a_single_string_as_names_through_the_injected_writer(self):
        # A string as *names* iterates its characters; without this guard the
        # loop would write one config per letter, and with a recording writer
        # the surprise letters would survive only inside the records.
        recorded = []
        for names in ("kwinrc", b"kwinrc"):
            with self.subTest(names=names):
                with (
                    self.assertRaises(ValueError) as caught,
                    _recording_writer(recorded),
                ):
                    theme_config_writer.publish_configs(
                        make_tmp_dir(self),
                        names,
                        defaults_path=make_tmp_dir(self) / "defaults",
                        read_groups=lambda _path: {},
                    )
                self.assertIn("not a single", str(caught.exception))
                self.assertEqual([], recorded)

    def test_rejects_names_that_are_not_iterable_through_the_injected_writer(self):
        # A non-iterable names value must surface as the iterable-expected
        # ValueError, naming its type, before the writer fires.
        recorded = []
        with self.assertRaises(ValueError) as caught, _recording_writer(recorded):
            theme_config_writer.publish_configs(
                make_tmp_dir(self),
                37,
                defaults_path=make_tmp_dir(self) / "defaults",
                read_groups=lambda _path: {},
            )
        self.assertIn("must be an iterable", str(caught.exception))
        self.assertIn("int", str(caught.exception))
        self.assertEqual([], recorded)

    def test_rejects_a_name_that_is_not_a_string_through_the_injected_writer(self):
        # Each element of *names* must be a str config filename: an int or a
        # bytes object is refused with the module's own ValueError naming the
        # type, before any write fires. Without this guard a bytes name would
        # slip past the plain-filename check (Path accepts bytes on POSIX) and
        # be published as a config file with a bytes name, and an int would
        # escape as a raw TypeError from the pathlib join instead.
        recorded = []
        for name, type_name in ((37, "int"), (b"kwinrc", "bytes")):
            with self.subTest(name=name):
                with (
                    self.assertRaises(ValueError) as caught,
                    _recording_writer(recorded),
                ):
                    theme_config_writer.publish_configs(
                        make_tmp_dir(self),
                        (name,),
                        defaults_path=make_tmp_dir(self) / "defaults",
                        read_groups=lambda _path: {},
                    )
                self.assertIn("names must be str config filenames", str(caught.exception))
                self.assertIn(type_name, str(caught.exception))
                self.assertEqual([], recorded)

    def test_rejects_a_name_that_is_not_a_plain_config_filename(self):
        # config_home / name must stay a join onto the config home, so the
        # guard must refuse a name that is empty, one of the reserved dot
        # names, or carries a directory part; and a NUL byte must be refused
        # by name outright rather than failing midway through a write.
        recorded = []
        for name in (".", "..", "sub/kwinrc", "kwinrc\0", ""):
            with self.subTest(name=name):
                with (
                    self.assertRaises(ValueError) as caught,
                    _recording_writer(recorded),
                ):
                    theme_config_writer.publish_configs(
                        make_tmp_dir(self),
                        (name,),
                        defaults_path=make_tmp_dir(self) / "defaults",
                        read_groups=lambda _path: {},
                    )
                self.assertIn("plain config filenames", str(caught.exception))
                self.assertEqual([], recorded)

    def test_refuses_a_name_the_defaults_do_not_define_before_the_first_write(self):
        # The module's contract: every name is checked against the defaults
        # sections before the first file is written, so a defaults file
        # truncated mid-run cannot leave a config partially published —
        # visible here as a zero-element record even though the first name
        # is fully defined.
        recorded = []
        defaults = make_tmp_dir(self) / "defaults"
        with self.assertRaises(ValueError) as caught, _recording_writer(recorded):
            theme_config_writer.publish_configs(
                make_tmp_dir(self),
                ("kwinrc", "plasmarc"),
                defaults_path=defaults,
                read_groups=lambda _path: {
                    ("kwinrc", "Theme"): {"name": "demo"},
                },
            )
        self.assertIn("plasmarc", str(caught.exception))
        self.assertIn(str(defaults), str(caught.exception))
        self.assertEqual([], recorded)

    def test_writes_one_recorded_config_per_wanted_name(self):
        # The writer parameterization the wrapper hides: with the write stub
        # installed, exactly one call fires per wanted name, in wanted order,
        # each carrying its groups' whole joined content — the same
        # [group]/key=value/trailing-blank byte shape the wrapper's own
        # written-config pin asserts, under an injected read_groups that
        # names no shipped defaults file.
        recorded = []
        with _recording_writer(recorded):
            theme_config_writer.publish_configs(
                make_tmp_dir(self),
                ("kwinrc", "plasmarc"),
                defaults_path=make_tmp_dir(self) / "defaults",
                read_groups=lambda _path: {
                    ("plasmarc", "Theme"): {"name": "example"},
                    ("kwinrc", "General"): {"key": "value"},
                },
            )
        self.assertEqual(
            [
                ("kwinrc", "[General]\nkey=value\n"),
                ("plasmarc", "[Theme]\nname=example\n"),
            ],
            recorded,
        )

    def test_writes_every_group_for_a_config_in_defaults_order(self):
        # Several defaults sections can target one config file. Omitting a
        # later group would silently drop part of the theme configuration.
        recorded = []
        with _recording_writer(recorded):
            theme_config_writer.publish_configs(
                make_tmp_dir(self),
                ("kwinrc",),
                defaults_path=make_tmp_dir(self) / "defaults",
                read_groups=lambda _path: {
                    ("kwinrc", "org.kde.kdecoration2"): {
                        "theme": "org.macos8.desktop",
                    },
                    ("kwinrc", "Compositing"): {"Enabled": "true"},
                },
            )
        self.assertEqual(
            [
                (
                    "kwinrc",
                    "[org.kde.kdecoration2]\ntheme=org.macos8.desktop\n\n"
                    "[Compositing]\nEnabled=true\n",
                ),
            ],
            recorded,
        )

    def test_a_failing_second_write_keeps_the_first_config_and_leaves_no_scratch(self):
        # Only the failing write is prevented: the first config was already
        # written through the real temp-sibling-and-rename path, and the
        # config home holds both names and nothing else — no .tmp temp
        # sibling, no staging or backup copy for either name. The wrapper's
        # own tests cannot reach this: their failure hooks are
        # write_config_atomically-level (patched os.replace/os.fchmod), so no
        # test fires a failure between the loop's first and second write.
        directory = make_tmp_dir(self)
        plasmarc = directory / "plasmarc"
        plasmarc.write_text("ORIGINAL\n", encoding="utf-8")
        with self.assertRaises(OSError) as caught, _failing_writer(("plasmarc",)):
            theme_config_writer.publish_configs(
                directory,
                ("kwinrc", "plasmarc"),
                defaults_path=directory / "defaults",
                read_groups=lambda _path: {
                    ("kwinrc", "Theme"): {"name": "one"},
                    ("plasmarc", "Theme"): {"name": "two"},
                },
            )
        self.assertIn("plasmarc", str(caught.exception))
        self.assertEqual(
            "[Theme]\nname=one\n",
            (directory / "kwinrc").read_text(encoding="utf-8"),
        )
        self.assertEqual("ORIGINAL\n", plasmarc.read_text(encoding="utf-8"))
        self.assertEqual({"kwinrc", "plasmarc"}, set(os.listdir(directory)))


if __name__ == "__main__":
    unittest.main()
