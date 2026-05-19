# Thin Client API Reference Generator

Generates `content/en/docs/thin_client_api_reference.generated.md` from the
three thin-client bindings (Go, Rust, Python) by extracting signatures and
docstrings, stitching them with a hand-curated `groups.yaml` and markdown
fragments under `overlay/`, and emitting Hugo markdown with Docsy
`{{< tabpane >}}` shortcodes.

## Prerequisites

* Go 1.18+ (`go/ast`).
* Rust stable with `cargo` (the `syn`-based extractor compiles locally).
* Python 3.9+ with the `venv` module (for `ast.unparse` and local deps).
* `jq` (only for the `extract-*-json` debug targets).
* Local checkouts of the two binding repositories at the tags pinned in
  `pinned-versions.env`.

Python dependencies (currently just `PyYAML`) are installed into a
local `.venv/` by the `Makefile`; the system Python is not touched.

## Usage

```sh
# First-time setup (also run automatically by make build):
make venv

# Verify both checkouts are at their pinned tags, then generate:
make build

# Same but fails loudly on any unresolved symbol in groups.yaml:
make check

# Inspect the extractor JSON directly:
make extract-go-json
make extract-rust-json
make extract-python-json

# Skip the pinned-tag check (development only):
make build SKIP_VERSION_CHECK=1

# Rebuild the venv after updating requirements.txt:
make venv-refresh

# Remove .venv/, extract-out/, and cargo target/:
make clean
```

## Directory layout

```
.
├── Makefile
├── pinned-versions.env           # pinned tags + binding checkout paths
├── groups.yaml                   # logical-op → per-binding symbols + prose
├── overlay/                      # cross-cutting prose fragments
├── extract-go/                   # Go extractor (go/ast)
├── extract-rust/                 # Rust extractor (syn)
├── extract-python.py             # Python extractor (stdlib ast)
└── stitch.py                     # composes the final markdown
```

## Adding a new API method

1. Add the method to the appropriate binding source(s), with a proper
   docstring (Go: `Parameters:` / `Returns:` sections; Rust: `# Arguments`
   / `# Returns` / `# Errors`; Python: Google-style `Args:` / `Returns:` /
   `Raises:`).
2. Add a group entry in `groups.yaml` naming the per-binding symbols.
3. Run `make check` to confirm there are no unresolved references.
4. Run `make build` and diff the output to confirm the section renders as
   expected.

## Editorial principle

**Per-method prose lives in binding docstrings, not in the overlay.**
If the generated section for a method reads thinly, the correct fix is to
expand the docstring in the binding source, not to add prose to the
overlay. The overlay is reserved for truly cross-cutting content:
transport-layer errors, the replica error-code catalogue, expected-outcome
conventions, the introduction and version-pin table.
