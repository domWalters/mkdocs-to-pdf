at ?= @
makefile_dir := $(patsubst %/,%,$(dir $(firstword $(MAKEFILE_LIST))))

.PHONY: help
help:
	@echo "Usage:"
	@echo "  build      : build a PDF"
	@echo "  clean      : delete the site directory"
	@echo "  distclean  : clean the whole project"
	@echo "  help       : show this message"

.PHONY: clean
clean:
	$(at)rm -rf $(makefile_dir)/site

.PHONY: distclean
distclean: clean
	$(at)rm -rf $(makefile_dir)/.venv

$(makefile_dir)/.venv/bin/activate:
	$(at)python3 -m venv $(makefile_dir)/.venv

$(makefile_dir)/.venv/bin/mkdocs: $(makefile_dir)/.venv/bin/activate $(makefile_dir)/requirements.txt
	$(at). .venv/bin/activate \
        && pip3 install -r $(makefile_dir)/requirements.txt \
        && $(makefile_dir)/../generate-requirements-full.sh

.PHONY: build
build: $(makefile_dir)/.venv/bin/mkdocs
	$(at)cd $(makefile_dir) \
        && $(makefile_dir)/.venv/bin/mkdocs build
