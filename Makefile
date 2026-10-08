PYTHON ?= python3
XDG_DATA_HOME ?= $(HOME)/.local/share

COLOR_SCHEME := theme/color-schemes/MacOS8.colors
# KDE derives the scheme id from the installed filename, so install under the
# source's own basename: renaming the scheme then moves the id with it instead
# of leaving a stale hardcoded name behind.
COLOR_SCHEME_NAME := $(notdir $(COLOR_SCHEME))
INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/color-schemes

LNF_ID := org.macos8.desktop
LNF_PACKAGE := theme/look-and-feel/$(LNF_ID)
LNF_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/plasma/look-and-feel

DTHEME_ID := org.macos8.desktop
DTHEME_PACKAGE := theme/desktop-themes/$(DTHEME_ID)
DTHEME_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/plasma/desktoptheme

.PHONY: check check-references install uninstall

check:
	$(PYTHON) -m unittest discover -s tests -v

# Opt-in: the repository check needs materialized Git LFS images, so it stays
# out of `check`. The deterministic self-test runs first and fails fast.
check-references:
	$(PYTHON) tools/check_references.py --self-test
	$(PYTHON) tools/check_references.py

install:
	install -Dm644 $(COLOR_SCHEME) $(INSTALL_DIR)/$(COLOR_SCHEME_NAME)
	install -d $(LNF_INSTALL_DIR)
# Stage the package as a sibling, then swap it in with a rename, so a copy that
# fails or is interrupted cannot leave a partial package installed or delete the
# working one. The rename also replaces rather than merges, so a reinstall drops
# files deleted from $(LNF_PACKAGE) instead of keeping stale QML. The EXIT trap
# removes the staging directory on the failure path.
	@staging='$(LNF_INSTALL_DIR)/.$(LNF_ID).staging'; \
	trap 'rm -rf "$$staging"' EXIT; \
	rm -rf "$$staging" && \
	cp -r $(LNF_PACKAGE) "$$staging" && \
	rm -rf $(LNF_INSTALL_DIR)/$(LNF_ID) && \
	mv "$$staging" $(LNF_INSTALL_DIR)/$(LNF_ID)
	install -d $(DTHEME_INSTALL_DIR)
# Same stage-then-rename rule as the look-and-feel package above: a copy that
# fails or is interrupted must not delete the working desktop theme or leave a
# partial one installed.
	@staging='$(DTHEME_INSTALL_DIR)/.$(DTHEME_ID).staging'; \
	trap 'rm -rf "$$staging"' EXIT; \
	rm -rf "$$staging" && \
	cp -r $(DTHEME_PACKAGE) "$$staging" && \
	rm -rf $(DTHEME_INSTALL_DIR)/$(DTHEME_ID) && \
	mv "$$staging" $(DTHEME_INSTALL_DIR)/$(DTHEME_ID)

# Remove only the artifacts `install` copied: the parent directories are shared
# (other color schemes, other look-and-feel/desktop-theme packages), so leave
# them and everything else in them alone. `rm -f`/`rm -rf` make a repeated run a
# no-op.
uninstall:
	rm -f $(INSTALL_DIR)/$(COLOR_SCHEME_NAME)
	rm -rf $(LNF_INSTALL_DIR)/$(LNF_ID)
	rm -rf $(DTHEME_INSTALL_DIR)/$(DTHEME_ID)
