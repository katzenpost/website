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

<span class="section">[kpclientd (the client daemon)](#kpclientd-the-client-daemon)</span>

<span class="section">[katzenqt (Qt group chat client)](#katzenqt-qt-group-chat-client)</span>

</div>

This page is the canonical reference for the
<span class="strong">**pinned versions**</span> of the Katzenpost
stack, together with brief instructions for building and running
each component from source. It is intended for users and mixnet node
operators who wish to run the software ahead of binary packages
becoming available. Application developers looking for the thin
client libraries should consult the
<a href="/docs/thin_client_api_reference/" class="link" target="_top">Thin
Client API Reference</a>, which carries its own pinned-versions
table.

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="pinned-versions"></span>Pinned versions

</div>

</div>

</div>

The following git tags are the current recommended versions for
running the stack. Components in the same row of the same
repository should be built from the same tag.

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
<td style="text-align: left;"><code class="literal">katzenqt</code> (Qt group chat client)</td>
<td style="text-align: left;"><a href="https://github.com/katzenpost/katzenqt" class="link" target="_top">katzenqt</a></td>
<td style="text-align: left;">(root)</td>
<td style="text-align: left;">main</td>
<td style="text-align: left;"><code class="literal">{{< pin "katzenqt" >}}</code></td>
</tr>
</tbody>
</table>

</div>

The katzenpost repository's top-level Makefile provides a build
target for each component (`make server`, `make dirauth`,
`make courier`, `make kpclientd`, and so on), and these build the
binaries deterministically, with the exception of the replica so
far. For full deployment guidance for the server-side components,
see the
<a href="/docs/admin_guide/" class="link" target="_top">Admin Guide</a>.

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

## <span id="kpclientd-the-client-daemon"></span>kpclientd (the client daemon)

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

## <span id="katzenqt-qt-group-chat-client"></span>katzenqt (Qt group chat client)

</div>

</div>

</div>

A decentralised group chat client built atop Qt. It depends solely
on the Katzenpost mix network and the Pigeonhole storage services.
No central server is involved. The underlying design is set out in
the <a href="https://arxiv.org/abs/2501.02933" class="link" target="_top">Echomix
paper</a>.

Build, install, and run instructions live on
<a href="/docs/build_katzenqt/" class="link" target="_top">Build and
run katzenqt from source</a>; the pinned tag is
`{{< pin "katzenqt" >}}` (see the table above).

</div>

</div>
