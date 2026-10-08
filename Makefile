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
# Stage the scheme as a hidden sibling and rename it in, so a copy that fails
# or is interrupted cannot truncate the working installed scheme. The rename
# replaces atomically, and the EXIT trap removes the staging file on failure.
	@staging='$(INSTALL_DIR)/.$(COLOR_SCHEME_NAME).staging'; \
	trap 'rm -f "$$staging"' EXIT; \
	install -Dm644 $(COLOR_SCHEME) "$$staging" && \
	mv "$$staging" $(INSTALL_DIR)/$(COLOR_SCHEME_NAME)
	install -d $(LNF_INSTALL_DIR)
# Stage the package as a sibling, then swap it in with a rename, so a copy that
# fails or is interrupted cannot leave a partial package installed or delete the
# working one. The old package is moved aside rather than deleted first: the
# swap is then a rename either way, and if the final rename fails the EXIT trap
# moves the old package back. A reinstall still replaces rather than merges, so
# files deleted from $(LNF_PACKAGE) do not stay behind as stale QML.
	@staging='$(LNF_INSTALL_DIR)/.$(LNF_ID).staging'; \
	old='$(LNF_INSTALL_DIR)/.$(LNF_ID).old'; \
	trap 'rm -rf "$$staging"; if [ ! -e $(LNF_INSTALL_DIR)/$(LNF_ID) ] && [ -e "$$old" ]; then mv "$$old" $(LNF_INSTALL_DIR)/$(LNF_ID); fi' EXIT; \
	rm -rf "$$staging" "$$old" && \
	cp -r $(LNF_PACKAGE) "$$staging" && \
	if [ -e $(LNF_INSTALL_DIR)/$(LNF_ID) ]; then mv $(LNF_INSTALL_DIR)/$(LNF_ID) "$$old"; fi && \
	mv "$$staging" $(LNF_INSTALL_DIR)/$(LNF_ID) && \
	rm -rf "$$old"
	install -d $(DTHEME_INSTALL_DIR)
# Same stage-then-swap rule as the look-and-feel package above: a copy that
# fails or is interrupted must not delete the working desktop theme or leave a
# partial one installed, and a failed swap restores the old theme.
	@staging='$(DTHEME_INSTALL_DIR)/.$(DTHEME_ID).staging'; \
	old='$(DTHEME_INSTALL_DIR)/.$(DTHEME_ID).old'; \
	trap 'rm -rf "$$staging"; if [ ! -e $(DTHEME_INSTALL_DIR)/$(DTHEME_ID) ] && [ -e "$$old" ]; then mv "$$old" $(DTHEME_INSTALL_DIR)/$(DTHEME_ID); fi' EXIT; \
	rm -rf "$$staging" "$$old" && \
	cp -r $(DTHEME_PACKAGE) "$$staging" && \
	if [ -e $(DTHEME_INSTALL_DIR)/$(DTHEME_ID) ]; then mv $(DTHEME_INSTALL_DIR)/$(DTHEME_ID) "$$old"; fi && \
	mv "$$staging" $(DTHEME_INSTALL_DIR)/$(DTHEME_ID) && \
	rm -rf "$$old"

# Remove only the artifacts `install` copied: the parent directories are shared
# (other color schemes, other look-and-feel/desktop-theme packages), so leave
# them and everything else in them alone. `rm -f`/`rm -rf` make a repeated run a
# no-op.
uninstall:
	rm -f $(INSTALL_DIR)/$(COLOR_SCHEME_NAME)
	rm -rf $(LNF_INSTALL_DIR)/$(LNF_ID)
	rm -rf $(DTHEME_INSTALL_DIR)/$(DTHEME_ID)
