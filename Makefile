SETUP=python setup.py
.PHONY: clean tests
all:
	$(SETUP) build
install:
	$(SETUP) install
test:
	nosetests
clean:
	rm -rf build/
	$(SETUP) clean
