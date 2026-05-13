include pinned-versions.env
export

OUTPUT := ../../content/en/docs/thin_client_api_reference.md

GO_SRC     := $(KATZENPOST_PATH)/client/thin
RUST_SRC   := $(THINCLIENT_PATH)/src
PYTHON_SRC := $(THINCLIENT_PATH)/katzenpost_thinclient

BUILD_DIR := extract-out

GO_JSON     := $(BUILD_DIR)/go.json
RUST_JSON   := $(BUILD_DIR)/rust.json
PYTHON_JSON := $(BUILD_DIR)/python.json

VENV       := .venv
VENV_STAMP := $(VENV)/.installed
PYTHON     := $(VENV)/bin/python3

.PHONY: build check check-versions clean venv venv-refresh \
        extract-go-json extract-rust-json extract-python-json help

help:
	@echo "Targets:"
	@echo "  build               generate $(OUTPUT)"
	@echo "  check               build with --strict (CI mode)"
	@echo "  check-versions      verify both binding checkouts are at their pinned tags"
	@echo "  venv                create local .venv/ with required Python packages"
	@echo "  venv-refresh        re-install packages into the existing venv"
	@echo "  clean               remove $(BUILD_DIR), .venv/ and extractor artefacts"
	@echo "  extract-<lang>-json run one extractor in isolation (pretty-printed)"

check-versions:
ifndef SKIP_VERSION_CHECK
	@kp_tag=$$(git -C "$(KATZENPOST_PATH)" describe --tags --exact-match 2>/dev/null || echo ""); \
	if [ "$$kp_tag" != "$(KATZENPOST_TAG)" ]; then \
	    echo "ERROR: $(KATZENPOST_PATH) is at '$$kp_tag', expected '$(KATZENPOST_TAG)'." >&2; \
	    echo "       Check out the pinned tag, or set SKIP_VERSION_CHECK=1 to override." >&2; \
	    exit 1; \
	fi
	@tc_tag=$$(git -C "$(THINCLIENT_PATH)" describe --tags --exact-match 2>/dev/null || echo ""); \
	if [ "$$tc_tag" != "$(THINCLIENT_TAG)" ]; then \
	    echo "ERROR: $(THINCLIENT_PATH) is at '$$tc_tag', expected '$(THINCLIENT_TAG)'." >&2; \
	    echo "       Check out the pinned tag, or set SKIP_VERSION_CHECK=1 to override." >&2; \
	    exit 1; \
	fi
	@echo "check-versions: both checkouts match pinned tags."
else
	@echo "check-versions: SKIPPED (SKIP_VERSION_CHECK set)."
endif

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

$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

GO_SOURCES     := extract-go/main.go extract-go/go.mod \
                  $(shell find $(GO_SRC) -name '*.go' 2>/dev/null)
RUST_SOURCES   := extract-rust/src/main.rs extract-rust/Cargo.toml \
                  $(shell find $(RUST_SRC) -name '*.rs' 2>/dev/null)
PYTHON_SOURCES := extract-python.py \
                  $(shell find $(PYTHON_SRC) -name '*.py' 2>/dev/null)

$(GO_JSON): $(GO_SOURCES) | $(BUILD_DIR)
	cd extract-go && go run . "$(GO_SRC)" > ../$@.tmp
	@mv $@.tmp $@

$(RUST_JSON): $(RUST_SOURCES) | $(BUILD_DIR)
	cd extract-rust && cargo run --release --quiet -- "$(RUST_SRC)" > ../$@.tmp
	@mv $@.tmp $@

$(PYTHON_JSON): $(PYTHON_SOURCES) $(VENV_STAMP) | $(BUILD_DIR)
	$(PYTHON) extract-python.py "$(PYTHON_SRC)" > $@.tmp
	@mv $@.tmp $@

build: check-versions $(VENV_STAMP) $(GO_JSON) $(RUST_JSON) $(PYTHON_JSON)
	$(PYTHON) stitch.py \
	    --go-json $(GO_JSON) \
	    --rust-json $(RUST_JSON) \
	    --python-json $(PYTHON_JSON) \
	    --groups groups.yaml \
	    --overlay overlay \
	    --katzenpost-tag $(KATZENPOST_TAG) \
	    --thinclient-tag $(THINCLIENT_TAG) \
	    --output $(OUTPUT)

check: check-versions $(VENV_STAMP) $(GO_JSON) $(RUST_JSON) $(PYTHON_JSON)
	$(PYTHON) stitch.py \
	    --go-json $(GO_JSON) \
	    --rust-json $(RUST_JSON) \
	    --python-json $(PYTHON_JSON) \
	    --groups groups.yaml \
	    --overlay overlay \
	    --katzenpost-tag $(KATZENPOST_TAG) \
	    --thinclient-tag $(THINCLIENT_TAG) \
	    --output $(OUTPUT) \
	    --strict

extract-go-json: $(GO_JSON)
	@jq . $(GO_JSON)

extract-rust-json: $(RUST_JSON)
	@jq . $(RUST_JSON)

extract-python-json: $(PYTHON_JSON)
	@jq . $(PYTHON_JSON)

clean:
	rm -rf $(BUILD_DIR) $(VENV)
	cd extract-rust && cargo clean --quiet 2>/dev/null || true
