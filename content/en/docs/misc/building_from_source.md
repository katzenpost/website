{ "title":"Build Katzenpost from source" , "linkTitle":"Build from source" , "description":"Pinned versions of the Katzenpost stack and how to build each component from source." , "author":"David Stainton" , "url":"" , "date":"2026-05-10T15:44:07.365863523-07:00" , "draft":"false" , "slug":"build_from_source" , "layout":"" , "type":"" , "weight":"" , "version":"0" }

<div class="article">

<div class="titlepage">

<div>

<div>

# <span id="building"></span>Build Katzenpost from source

</div>

</div>

------------------------------------------------------------------------

</div>

<div class="toc">

**Table of Contents**

<span class="section">[Pinned versions](#pinned-versions)</span>

<span class="section">[Prerequisites](#prerequisites)</span>

<span class="section">[kpclientd (the client daemon)](#kpclientd-the-client-daemon)</span>

<span class="section">[Go thin client](#go-thin-client)</span>

<span class="section">[Rust thin client](#rust-thin-client)</span>

<span class="section">[Python thin client](#python-thin-client)</span>

<span class="section">[katzenqt (Qt group chat client)](#katzenqt-qt-group-chat-client)</span>

<span class="section">[Verifying the stack](#verifying-the-stack)</span>

</div>

This page is the canonical reference for the <span class="strong">**pinned versions**</span> of the Katzenpost stack, together with brief instructions for building and running each component from source. It is intended for anyone who wishes to run the software ahead of binary packages becoming available.

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="pinned-versions"></span>Pinned versions

</div>

</div>

</div>

The following git tags are the current recommended versions for running the stack. Components in the same row of the same repository should be built from the same tag.

<div class="informaltable">

<table class="informaltable" data-border="1">
<thead>
<tr class="header">
<th style="text-align: left;">Component</th>
<th style="text-align: left;">Repository</th>
<th style="text-align: left;">Path</th>
<th style="text-align: left;">Branch</th>
<th style="text-align: left;">Tag</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;">Server-side components (mix server, dirauth, courier, replica)</td>
<td style="text-align: left;"><a href="https://github.com/katzenpost/katzenpost" class="link" target="_top">katzenpost</a></td>
<td style="text-align: left;"><code class="literal">cmd/server</code>, <code class="literal">cmd/dirauth</code>, <code class="literal">cmd/courier</code>, <code class="literal">cmd/replica</code></td>
<td style="text-align: left;">main</td>
<td style="text-align: left;"><code class="literal">v0.0.73</code></td>
</tr>
<tr class="even">
<td style="text-align: left;"><code class="literal">kpclientd</code> (client daemon)</td>
<td style="text-align: left;"><a href="https://github.com/katzenpost/katzenpost" class="link" target="_top">katzenpost</a></td>
<td style="text-align: left;"><code class="literal">cmd/kpclientd</code></td>
<td style="text-align: left;">main</td>
<td style="text-align: left;"><code class="literal">v0.0.73</code></td>
</tr>
<tr class="odd">
<td style="text-align: left;">Go thin client (reference)</td>
<td style="text-align: left;"><a href="https://github.com/katzenpost/katzenpost" class="link" target="_top">katzenpost</a></td>
<td style="text-align: left;"><code class="literal">client/thin</code></td>
<td style="text-align: left;">main</td>
<td style="text-align: left;"><code class="literal">v0.0.73</code></td>
</tr>
<tr class="even">
<td style="text-align: left;">Rust thin client</td>
<td style="text-align: left;"><a href="https://github.com/katzenpost/thin_client" class="link" target="_top">thin_client</a></td>
<td style="text-align: left;"><code class="literal">src</code></td>
<td style="text-align: left;">main</td>
<td style="text-align: left;"><code class="literal">0.0.13</code></td>
</tr>
<tr class="odd">
<td style="text-align: left;">Python thin client</td>
<td style="text-align: left;"><a href="https://github.com/katzenpost/thin_client" class="link" target="_top">thin_client</a></td>
<td style="text-align: left;"><code class="literal">katzenpost_thinclient</code></td>
<td style="text-align: left;">main</td>
<td style="text-align: left;"><code class="literal">0.0.13</code></td>
</tr>
<tr class="even">
<td style="text-align: left;"><code class="literal">katzenqt</code> (Qt group chat client)</td>
<td style="text-align: left;"><a href="https://github.com/katzenpost/katzenqt" class="link" target="_top">katzenqt</a></td>
<td style="text-align: left;">(root)</td>
<td style="text-align: left;">resending_api2026</td>
<td style="text-align: left;"><code class="literal">0.0.2-rc5</code></td>
</tr>
</tbody>
</table>

</div>

Server-side components are listed for completeness; for full deployment guidance, see the <a href="/docs/admin_guide/" class="link" target="_top">Admin Guide</a>.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="prerequisites"></span>Prerequisites

</div>

</div>

</div>

<div class="itemizedlist">

- <span class="strong">**Go**</span> 1.23 or newer.

- <span class="strong">**Rust**</span> stable (with `cargo`).

- <span class="strong">**Python**</span> 3.9 or newer (the thin client supports 3.8+, but the venv tooling here assumes 3.9+).

- <span class="strong">**Make**</span>, <span class="strong">**git**</span>, and a C toolchain (`gcc` or `clang`).

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="kpclientd-the-client-daemon"></span>kpclientd (the client daemon)

</div>

</div>

</div>

The thin client libraries do not, by themselves, speak to the mix network. They communicate over a local socket with the `kpclientd` daemon, which performs all cryptographic and network operations.

``` programlisting
git clone https://github.com/katzenpost/katzenpost
cd katzenpost
git checkout v0.0.73
cd cmd/kpclientd
go build
```

The resulting `kpclientd` binary is run with a TOML configuration file:

``` programlisting
./kpclientd -c /path/to/client.toml
```

A configuration file is required. For testing, the <a href="/docs/admin_guide/docker.html" class="link" target="_top">Docker test mixnet</a> generates one automatically; for joining a public network, you would obtain the configuration from that network’s operators.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="go-thin-client"></span>Go thin client

</div>

</div>

</div>

The Go thin client is a library, imported as a Go module:

``` programlisting
import "github.com/katzenpost/katzenpost/client/thin"
```

Pin to `v0.0.73` in your application’s `go.mod`. There is no separate build step; the library is compiled with your application.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="rust-thin-client"></span>Rust thin client

</div>

</div>

</div>

``` programlisting
git clone https://github.com/katzenpost/thin_client
cd thin_client
git checkout 0.0.13
cargo build --release
```

Or, in another Rust project’s `Cargo.toml`:

``` programlisting
[dependencies]
katzenpost_thin_client = "0.0.13"
```

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="python-thin-client"></span>Python thin client

</div>

</div>

</div>

The Python thin client is best installed into a virtualenv, both to isolate its dependencies and to avoid any disturbance of the system Python.

``` programlisting
git clone https://github.com/katzenpost/thin_client
cd thin_client
git checkout 0.0.13
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install .
```

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="katzenqt-qt-group-chat-client"></span>katzenqt (Qt group chat client)

</div>

</div>

</div>

A decentralised group chat client built atop Qt. It depends solely on the Katzenpost mix network and the Pigeonhole storage services. No central server is involved. The underlying design is set out in the <a href="https://arxiv.org/abs/2501.02933" class="link" target="_top">Echomix paper</a>.

A tag has not yet been published; at present, `katzenqt` builds against a development branch of `katzenpost`. This section will be updated once a release is cut.

``` programlisting
sudo apt install libxcb-cursor0 libegl1
git clone https://github.com/katzenpost/katzenqt
cd katzenqt
git checkout 0.0.2-rc4
make deps
make run
```

If `make deps run` does not produce a running interface, the component-by-component sequence in `katzenqt`’s `README.md` is the recommended fallback.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="verifying-the-stack"></span>Verifying the stack

</div>

</div>

</div>

Once `kpclientd` is running with a valid configuration, a single test from the Python integration suite is sufficient to exercise the full Pigeonhole round trip: Alice writes a message to the storage replicas via the courier, and Bob reads it back.

``` programlisting
source thin_client/.venv/bin/activate
cd thin_client
pytest tests/test_new_pigeonhole_api.py::test_alice_sends_bob_complete_workflow
```

A successful run indicates that `kpclientd` is connected, the PKI document has been retrieved, the network is producing consensus, and the courier and replicas are reachable. The remainder of the suite (`pytest` with no arguments) covers tombstones, copy commands, and the various error paths.

</div>

</div>
