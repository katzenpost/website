# Directory format checks

The published [CDDL](../../static/docs/specs/dirauth/dirauth.cddl) describes
conforming producer objects. The [ABNF](../../static/docs/specs/dirauth/wire.abnf)
describes the directory command subset, not every command on a gateway session.
Both target Katzenpost v0.0.107. The specification supplies semantic acceptance
rules, canonical encoding, and configured key widths that the grammars do not.

Run all parsers inside the container:

```sh
podman build -t katzenpost-dirauth-schema:local -f tools/specs/Containerfile .
podman run --rm --network=none --userns=keep-id \
  -v "$PWD:/site:ro" -w /site katzenpost-dirauth-schema:local
```

Build the existing website render image first with `make image`. The schema
image pins CDDL 0.12.14 and Python abnf 2.9.1. It installs nothing on the host.

The checker exercises 119 CDDL and 31 ABNF examples. Cases include field omission
versus null, nested descriptor bytes versus inline maps, identifier/metadata/hash
boundaries, family-specific status codes, reserved values and header lengths.
It also reproduces the five existing canonical CBOR examples and commit/reveal
hashes. The BODY example is intentionally rejected as a valid document shape.

Synthetic signatures in the original shape fixtures are not cryptographically
valid. The separate [signed-document fixture](fixture-README.md) has valid test
signatures and rejection controls checked against the exact tagged Go source.
The schema checker tests shapes, canonical bytes, hashes, and the signature
input, without rerunning signature verification. Its regeneration wrapper runs
those cryptographic checks inside Podman.

Neither check establishes live epoch-state acceptance or mixed-implementation
conformance.

The [arithmetic vectors](../../static/docs/specs/dirauth/arithmetic-vectors.json) also check exact gateway-rate output.
The checker reproduces the logarithm with binary64 operations and compares it with the Go reference formula.
