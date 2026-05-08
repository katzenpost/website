---
title:
linkTitle: "Build from source"
description: "Pinned versions of the Katzenpost stack and how to build each component from source"
categories: [""]
tags: [""]
author: ["David Stainton"]
version: 0
draft: false
slug: "/build_from_source/"
---

# Build Katzenpost from source

This page is the canonical reference for the **pinned versions** of the
Katzenpost stack, together with brief instructions for building and
running each component from source. It is intended for anyone who
wishes to run the software ahead of binary packages becoming
available.

## Pinned versions

The following git tags are the current recommended versions for
running the stack. Components in the same row of the same repository
should be built from the same tag.

| Component | Repository | Path | Branch | Tag |
|---|---|---|---|---|
| Server-side components (mix server, dirauth, courier, replica) | [katzenpost](https://github.com/katzenpost/katzenpost) | `cmd/server`, `cmd/dirauth`, `cmd/courier`, `cmd/replica` | main | `v0.0.73` |
| `kpclientd` (client daemon) | [katzenpost](https://github.com/katzenpost/katzenpost) | `cmd/kpclientd` | main | `v0.0.73` |
| Go thin client (reference) | [katzenpost](https://github.com/katzenpost/katzenpost) | `client/thin` | main | `v0.0.73` |
| Rust thin client | [thin_client](https://github.com/katzenpost/thin_client) | `src` | main | `0.0.13` |
| Python thin client | [thin_client](https://github.com/katzenpost/thin_client) | `katzenpost_thinclient` | main | `0.0.13` |
| `katzenqt` (Qt group chat client) | [katzenqt](https://github.com/katzenpost/katzenqt) | (root) | resending_api2026 | `0.0.2-rc5` |


Server-side components are listed for completeness; for full deployment
guidance, see the [Admin Guide](/docs/admin_guide/).

## Prerequisites

- **Go** 1.23 or newer.
- **Rust** stable (with `cargo`).
- **Python** 3.9 or newer (the thin client supports 3.8+, but the venv tooling here assumes 3.9+).
- **Make**, **git**, and a C toolchain (`gcc` or `clang`).

## kpclientd (the client daemon)

The thin client libraries do not, by themselves, speak to the mix
network. They communicate over a local socket with the `kpclientd`
daemon, which performs all cryptographic and network operations.

```shell
git clone https://github.com/katzenpost/katzenpost
cd katzenpost
git checkout v0.0.73
cd cmd/kpclientd
go build
```

The resulting `kpclientd` binary is run with a TOML configuration
file:

```shell
./kpclientd -c /path/to/client.toml
```

A configuration file is required. For testing, the [Docker test
mixnet](/docs/admin_guide/docker.html) generates one automatically; for
joining a public network, you would obtain the configuration from that
network's operators.

## Go thin client

The Go thin client is a library, imported as a Go module:

```go
import "github.com/katzenpost/katzenpost/client/thin"
```

Pin to `v0.0.73` in your application's `go.mod`. There is no
separate build step; the library is compiled with your application.

## Rust thin client

```shell
git clone https://github.com/katzenpost/thin_client
cd thin_client
git checkout 0.0.13
cargo build --release
```

Or, in another Rust project's `Cargo.toml`:

```toml
[dependencies]
katzenpost_thin_client = "0.0.13"
```

## Python thin client

The Python thin client is best installed into a virtualenv, both to
isolate its dependencies and to avoid any disturbance of the system
Python.

```shell
git clone https://github.com/katzenpost/thin_client
cd thin_client
git checkout 0.0.13
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install .
```

## katzenqt (Qt group chat client)

A decentralised group chat client built atop Qt. It depends solely on
the Katzenpost mix network and the Pigeonhole storage services. No
central server is involved. The underlying design is set out in the
[Echomix paper](https://arxiv.org/abs/2501.02933).

A tag has not yet been published; at present, `katzenqt` builds
against a development branch of `katzenpost`. This section will be
updated once a release is cut.

```shell
sudo apt install libxcb-cursor0 libegl1
git clone https://github.com/katzenpost/katzenqt
cd katzenqt
git checkout 0.0.2-rc4
make deps
make run
```

If `make deps run` does not produce a running interface, the
component-by-component sequence in `katzenqt`'s `README.md` is the
recommended fallback.

## Verifying the stack

Once `kpclientd` is running with a valid configuration, a single
test from the Python integration suite is sufficient to exercise the
full Pigeonhole round trip: Alice writes a message to the storage
replicas via the courier, and Bob reads it back.

```shell
source thin_client/.venv/bin/activate
cd thin_client
pytest tests/test_new_pigeonhole_api.py::test_alice_sends_bob_complete_workflow
```

A successful run indicates that `kpclientd` is connected, the PKI
document has been retrieved, the network is producing consensus, and
the courier and replicas are reachable. The remainder of the suite
(`pytest` with no arguments) covers tombstones, copy commands, and
the various error paths.
