# Bugs

Known bugs, recorded by any loop and fixed by the bugfix loop.
Each bug: symptom, how to reproduce, suspected cause if known. Move fixed bugs to Fixed, with the
required `**Validation gap:** <tag> — <one sentence>` line recording what made the bug hard to
confirm (tag one of: none, no-repro, no-fake, real-run-needed, no-observability, slow-check,
unclear-invariant).

## Open

### An oversize GTK settings or user-CSS file crashes the GTK selection with a MemoryError (found by the bugfix role 2026-10-23)

`tools/apply_gtk.py::_read_config_text` reads the whole of
`$XDG_CONFIG_HOME/gtk-3.0/settings.ini`, `gtk-4.0/settings.ini` or
`gtk-4.0/gtk.css` into memory in chunks with no size cap. A GTK config file
of hundreds of megabytes raises `MemoryError`, which is not an `OSError`, so
the tool's `except ConfigError` path never runs and `make apply-gtk` or
`make remove-gtk` ends in a traceback instead of its documented exit-2
diagnostic naming the file.

**Reproduce:** truncate a `gtk-4.0/gtk.css` to 300 MB and run
`HOME=... XDG_CONFIG_HOME=... python3 tools/apply_gtk.py --remove` under
`ulimit -v 120000`; the process exits 1 after a `MemoryError` instead of
exiting 2 with a named diagnostic.

**Suspected cause:** neither the read nor the accumulated bytes are bounded.
The same 1 MiB cap `tools/install_firefox.py::_read_text` now applies to the
Firefox profile files would bound it; settings.ini and gtk.css are small
user files.

## Fixed
