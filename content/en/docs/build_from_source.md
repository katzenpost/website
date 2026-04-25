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
body_class: "td-style-dashes"
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

| Component | Repository | Path | Tag |
|---|---|---|---|
| `kpclientd` (client daemon) | [katzenpost](https://github.com/katzenpost/katzenpost) | `cmd/kpclientd` | `v0.0.73-rc3` |
| Go thin client (reference) | [katzenpost](https://github.com/katzenpost/katzenpost) | `client/thin` | `v0.0.73-rc3` |
| Rust thin client | [thin_client](https://github.com/katzenpost/thin_client) | `src` | `0.0.12-rc3` |
| Python thin client | [thin_client](https://github.com/katzenpost/thin_client) | `katzenpost_thinclient` | `0.0.12-rc3` |
| `katzenqt` (Qt group chat client) | [katzenqt](https://github.com/katzenpost/katzenqt) | (root) | *tag pending* |
| Server-side components (mix server, dirauth, courier, replica) | [katzenpost](https://github.com/katzenpost/katzenpost) | `server/`, `authority/`, `courier/`, `replica/` | `v0.0.73-rc3` |

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
git checkout v0.0.73-rc3
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

Pin to `v0.0.73-rc3` in your application's `go.mod`. There is no
separate build step; the library is compiled with your application.

## Rust thin client

```shell
git clone https://github.com/katzenpost/thin_client
cd thin_client
git checkout 0.0.12-rc3
cargo build --release
```

Or, in another Rust project's `Cargo.toml`:

```toml
[dependencies]
katzenpost_thin_client = "0.0.12-rc3"
```

## Python thin client

The Python thin client is best installed into a virtualenv, both to
isolate its dependencies and to avoid any disturbance of the system
Python.

```shell
git clone https://github.com/katzenpost/thin_client
cd thin_client
git checkout 0.0.12-rc3
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install .
```

The example programs under `thin_client/examples/` (`echo_ping.py`,
`fetch_pki_doc.py`, `mixnet_status.py`, and others) demonstrate the
API and are useful smoke tests once `kpclientd` is running.

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
make deps
make run
```

If `make deps run` does not produce a running interface, the
component-by-component sequence in `katzenqt`'s `README.md` is the
recommended fallback.

## Verifying the stack

Once `kpclientd` is running with a valid configuration, the Python
example `echo_ping.py` is the simplest end-to-end smoke test. It
sends a packet through the mix network and waits for the SURB reply.

```shell
source thin_client/.venv/bin/activate
python3 thin_client/examples/echo_ping.py
```

A successful run indicates that `kpclientd` is connected, the PKI
document has been retrieved, and the network is producing consensus.
