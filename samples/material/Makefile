at ?= @
makefile_dir := $(realpath $(patsubst %/,%,$(dir $(firstword $(MAKEFILE_LIST)))))

.PHONY: help
help:
	@echo "Usage:"
	@echo "  build      : build a PDF"
	@echo "  clean      : delete the site directory"
	@echo "  distclean  : clean the whole project"
	@echo "  help       : show this message"

.PHONY: clean
clean:
	$(at)find $(makefile_dir) -type d -name "site" -exec rm -rf {} +

.PHONY: distclean
distclean: clean
	$(at)rm -rf $(makefile_dir)/.venv

activate_python_source ?= $(abspath $(makefile_dir)/../../.venv/bin/activate)

ifneq "exists" "$(shell if [ -e $(activate_python_source) ]; then echo exists; fi)"
    $(error File $(activate_python_source) does not exist.)
endif

$(makefile_dir)/.venv/bin/activate:
	$(at). $(activate_python_source) \
		&& python3 -m venv $(makefile_dir)/.venv

$(makefile_dir)/.venv/bin/mkdocs: $(makefile_dir)/.venv/bin/activate $(makefile_dir)/requirements.txt
	$(at). .venv/bin/activate \
		&& pip3 install -r $(makefile_dir)/requirements.txt \
		&& $(makefile_dir)/generate-requirements-full.sh

samples ?= $(notdir $(shell find $(makefile_dir) -mindepth 1 -maxdepth 1 -type d ! -path "*/\.*"))

.PHONY: build
build: $(makefile_dir)/.venv/bin/mkdocs
	$(at)find "$(makefile_dir)" -mindepth 1 -maxdepth 1 -type d ! -path "*/\.*" -print0 | xargs -0 -I {} sh -c " \
		cd {} && $(makefile_dir)/.venv/bin/mkdocs build; \
	"
