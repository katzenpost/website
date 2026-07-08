---
title: "Build Katzenpost from source"
linkTitle: "Build from source"
description: "Pinned versions of the Katzenpost stack and how to build each component from source."
author: "David Stainton"
url: "docs/build_from_source"
date: "2026-05-11T21:31:32.650814427-07:00"
draft: "false"
slug: ""
layout: ""
type: ""
weight: ""
version: "0"
aliases:
  - "/docs/build_katzenqt/"
---

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

<span class="section">[For users](#for-users)</span>

<span class="section">[For operators](#for-operators)</span>

</div>

This page is the canonical reference for the
<span class="strong">**pinned versions**</span> of the Katzenpost
stack, together with brief instructions for building and running
each component from source. It is intended for users and mixnet node
operators who wish to run the software ahead of binary packages
becoming available. The pinned-versions table below is the full
compatibility set across repositories and serves application
developers as well; for the thin client library APIs themselves,
consult the
<a href="/docs/thin_client_api_reference/" class="link" target="_top">Thin
Client API Reference</a>.

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="pinned-versions"></span>Pinned versions

</div>

</div>

</div>

The following git tags are the current recommended versions for
running the stack, and they are one mutually compatible set: this
katzenpost with this thin_client with this katzenqt. Components in
the same row of the same repository should be built from the same
tag.

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
<td style="text-align: left;">Server-side components (mix server, dirauth, courier,
replica)</td>
<td style="text-align: left;"><a href="https://github.com/katzenpost/katzenpost" class="link" target="_top">katzenpost</a></td>
<td style="text-align: left;"><code class="literal">cmd/server</code>,
<code class="literal">cmd/dirauth</code>,
<code class="literal">cmd/courier</code>,
<code class="literal">cmd/replica</code></td>
<td style="text-align: left;">main</td>
<td style="text-align: left;"><code class="literal">{{< pin "katzenpost" >}}</code></td>
</tr>
<tr class="even">
<td style="text-align: left;"><code class="literal">kpclientd</code> (client daemon)</td>
<td style="text-align: left;"><a href="https://github.com/katzenpost/katzenpost" class="link" target="_top">katzenpost</a></td>
<td style="text-align: left;"><code class="literal">cmd/kpclientd</code></td>
<td style="text-align: left;">main</td>
<td style="text-align: left;"><code class="literal">{{< pin "katzenpost" >}}</code></td>
</tr>
<tr class="odd">
<td style="text-align: left;">Thin client libraries (Rust, Python; the Go thin client lives in
the katzenpost repository at the katzenpost tag)</td>
<td style="text-align: left;"><a href="https://github.com/katzenpost/thin_client" class="link" target="_top">thin_client</a></td>
<td style="text-align: left;"><code class="literal">src</code>,
<code class="literal">katzenpost_thinclient</code></td>
<td style="text-align: left;">main</td>
<td style="text-align: left;"><code class="literal">{{< pin "thin_client" >}}</code></td>
</tr>
<tr class="even">
<td style="text-align: left;"><code class="literal">katzenqt</code> (Qt group chat client)</td>
<td style="text-align: left;"><a href="https://github.com/katzenpost/katzenqt" class="link" target="_top">katzenqt</a></td>
<td style="text-align: left;">(root)</td>
<td style="text-align: left;">main</td>
<td style="text-align: left;"><code class="literal">{{< pin "katzenqt" >}}</code></td>
</tr>
</tbody>
</table>

</div>

The <a href="https://github.com/katzenpost/hpqc" class="link" target="_top">hpqc</a>
cryptography library needs no row here: it is pinned by the
katzenpost repository's `go.mod` and
`go.sum`.

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

- <span class="strong">**Make**</span>,
  <span class="strong">**git**</span>, and a C toolchain
  (`gcc` or `clang`).

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="for-users"></span>For users

</div>

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="kpclientd-the-client-daemon"></span>kpclientd (the client daemon)

</div>

</div>

</div>

Client applications such as `katzenqt` do not, by
themselves, speak to the mix network. They communicate over a local
socket with the `kpclientd` daemon, which performs
all cryptographic and network operations.

``` programlisting
git clone https://github.com/katzenpost/katzenpost
cd katzenpost
git checkout {{< pin "katzenpost" >}}
make kpclientd
```

The resulting `cmd/kpclientd/kpclientd` binary is run with a
TOML configuration file:

``` programlisting
./kpclientd -c /path/to/client.toml
```

A configuration file is required. For testing, the
<a href="/docs/admin_guide/docker.html" class="link" target="_top">Docker test
mixnet</a> generates one automatically; for joining a public
network, you would obtain the configuration from that network’s
operators.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="katzenqt-qt-group-chat-client"></span>katzenqt (Qt group chat client)

</div>

</div>

</div>

A decentralised group chat client built atop Qt. It depends solely
on the Katzenpost mix network and the Pigeonhole storage services;
no central server is involved. The
<a href="/docs/specs/groupchat/" class="link" target="_top">Group Chat
Design</a> spec describes some of `katzenqt`'s
design; for the storage concept, see
<a href="/docs/pigeonhole_explained/" class="link" target="_top">Understanding
Pigeonhole</a>.

<span class="strong">**Warning.**</span> `katzenqt` is in active
development; it is not appropriate to rely on it for anonymity,
security, or privacy at this stage.

``` programlisting
sudo apt install -y git make libxcb-cursor0 libegl1
git clone https://github.com/katzenpost/katzenqt
cd katzenqt
git checkout {{< pin "katzenqt" >}}
make deps
make run
```

Out of the box, `make run` builds `kpclientd`,
installs it as a systemd user service, and connects to the
<span class="strong">**namenlos public mixnet**</span>: the Makefile
installs a `kpclientd` configuration that dials
namenlos and a thin client configuration that reaches the daemon
over a local socket. No configuration editing is required. If the
application cannot connect or messages fail to move, first check
the network's health on the
<a href="https://status.namenlos.network/" class="link" target="_top">namenlos
status page</a>.

For step-by-step setup, troubleshooting, and details on persistent
state, see the repository's
<a href="https://github.com/katzenpost/katzenqt/blob/{{< pin "katzenqt" >}}/README.md" class="link" target="_top">README
at the pinned tag</a>.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="for-operators"></span>For operators

</div>

</div>

</div>

The backend components (mix server, dirauth, courier, replica) are
built from the katzenpost repository's top-level Makefile, which
provides a target per component. Several of the targets, among them
`make server` and `make dirauth`, produce
deterministic, reproducible binaries; work is underway to make every
component build reproducibly, the replica being the furthest out.

``` programlisting
git clone https://github.com/katzenpost/katzenpost
cd katzenpost
git checkout {{< pin "katzenpost" >}}
make server
make dirauth
make courier
make replica
```

The replica requires RocksDB; its Makefile target installs that
dependency first. For deployment guidance, configuration, and
operating practice, see the
<a href="/docs/admin_guide/" class="link" target="_top">Admin Guide</a>.

</div>

</div>
