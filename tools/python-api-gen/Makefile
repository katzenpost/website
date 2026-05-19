include pinned-versions.env
export

OUTPUT := ../../content/en/docs/misc/python_thin_client_api.md

VENV       := .venv
VENV_STAMP := $(VENV)/.installed
PYTHON     := $(VENV)/bin/python3

.PHONY: build check-tag venv venv-refresh clean help

help:
	@echo "Targets:"
	@echo "  build          generate $(OUTPUT) from the pinned thin_client tag"
	@echo "  check-tag      verify the pinned tag resolves in the checkout"
	@echo "  venv           create local .venv/ with pydoc-markdown"
	@echo "  venv-refresh   re-install packages into the existing venv"
	@echo "  clean          remove build/ and .venv/"

$(VENV_STAMP): requirements.txt
	@echo "Bootstrapping Python venv at $(VENV)..."
	@python3 -m venv $(VENV)
	@$(VENV)/bin/pip install --quiet --upgrade pip
	@$(VENV)/bin/pip install --quiet -r requirements.txt
	@touch $(VENV_STAMP)

venv: $(VENV_STAMP)

venv-refresh:
	@rm -f $(VENV_STAMP)
	@$(MAKE) venv

check-tag:
	@if ! git -C "$(THINCLIENT_PATH)" rev-parse --verify --quiet \
	    "$(THINCLIENT_TAG)^{commit}" >/dev/null; then \
	    echo "ERROR: tag '$(THINCLIENT_TAG)' does not resolve in $(THINCLIENT_PATH)." >&2; \
	    exit 1; \
	fi
	@echo "check-tag: '$(THINCLIENT_TAG)' resolves in $(THINCLIENT_PATH)."

build: check-tag $(VENV_STAMP)
	$(PYTHON) generate.py

clean:
	rm -rf build $(VENV)
