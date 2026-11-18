"""Build a minimal installed applet package for render preflight tests."""

from pathlib import Path


def make_applet_package(data_root: Path, applet_id: str) -> Path:
    """Create an applet package with plain metadata.json under *data_root*."""
    package = data_root / "plasma" / "plasmoids" / applet_id
    package.mkdir(parents=True)
    (package / "metadata.json").write_text("{}", encoding="utf-8")
    return package
