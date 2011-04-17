SETUP=python setup.py
ICONDIR=/usr/share/icons
SCHEMADIR=/usr/share/gconf/schemas
DARKTHEME=ubuntu-mono-dark
LIGHTTHEME=ubuntu-mono-light
INSTALL=/usr/bin/install
.PHONY: clean tests
all:
	$(SETUP) build
install: install_egg install_shared

install_egg:
	$(SETUP) install

install_shared:
	$(INSTALL) share/curator.svg /usr/share/icons/ubuntu-mono-dark/apps/48/curator.svg
	gtk-update-icon-cache -q -t -f /usr/share/icons/ubuntu-mono-dark/
	$(INSTALL) share/curator.schemas /usr/share/gconf/schemas/curator.schemas
	$(INSTALL) share/curator.desktop /usr/share/applications/curator.desktop
test:
	nosetests
clean:
	rm -rf build/ curator/*.pyc tests/*.pyc
	$(SETUP) clean
