---
title: "Katzenpost"
description: "A post-quantum mix network providing strong metadata privacy against global passive adversaries."
---

{{< blocks/cover image_anchor="top" height="auto" color="black" >}}
<div style="display: flex; align-items: center; gap: 2rem; flex-wrap: wrap;">
<div style="flex: 0 0 auto;">
<img src="/images/lynx-big.png" alt="Katzenpost lynx" style="max-width: 300px; width: 100%; height: auto;">
</div>
<div style="flex: 1 1 auto;">
<h1>Katzenpost</h1>
<p>A post-quantum mix network providing strong metadata privacy against global passive adversaries.</p>
</div>
</div>
{{< /blocks/cover >}}

## What it is

Katzenpost is a free and open-source mix network. It hides who is talking
to whom from network-level observers, including adversaries that record
traffic today for later decryption on a quantum computer. The design is
described in [*Echomix: a Strong Anonymity System with Messaging*](https://arxiv.org/abs/2501.02933).

Beyond messaging, Katzenpost is a substrate for decentralised applications
that tolerate ephemeral storage and modest latency: group chat, voting,
ephemeral collaborative state, and anonymous integration with existing
systems.

## Status

- **katzenqt** — Qt group chat client; buildable from source today, pre-built packages forthcoming.
- **kpclientd** — client daemon; buildable from source, packages forthcoming.
- **Namenlos** — a public Katzenpost mix network anyone may use; coming.
- **Pigeonhole** — anonymous storage protocol; implemented, with thin clients in Go, Rust, and Python.

## Threat model

The published [Threat Model document](/docs/threat_model/) is an evolving
work in progress and does not yet incorporate the new designs introduced in
the paper. To understand the present state of the design, the
[Echomix paper](https://arxiv.org/abs/2501.02933) and the threat model
document must be read together.

## Where to go

- **[Documentation](/docs/)** — start here. Entry points for users, operators, application developers, core developers, and academics.
- **[Blog](/blog/)** — design notes and protocol explainers.
- **[Source](https://github.com/katzenpost)** — the Katzenpost monorepo, the `hpqc` post-quantum cryptography library, thin clients, `katzenqt`, and this website.
- **[Team](/pages/team/)** · **[Funders](/pages/funders/)** · **[Presentations](/pages/presentations/)**.
