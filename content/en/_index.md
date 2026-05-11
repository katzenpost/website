---
title: "Katzenpost"
description: "A post-quantum mix network providing strong metadata privacy against global passive adversaries."
---

{{< blocks/cover image_anchor="top" height="auto" color="black" >}}
<div style="display: flex; flex-direction: column; align-items: center; text-align: center; gap: 1.25rem;">
<h1 style="margin: 0;">Katzenpost</h1>
<p style="max-width: 640px; margin: 0;">A post-quantum mix network providing strong metadata privacy against global passive adversaries.</p>
<div style="display: flex; flex-wrap: wrap; gap: 0.75rem; justify-content: center; margin-top: 0.5rem;">
<a class="btn btn-lg btn-primary" href="https://arxiv.org/abs/2501.02933">Read the paper</a>
<a class="btn btn-lg btn-outline-light" href="/docs/">Documentation</a>
<a class="btn btn-lg btn-outline-light" href="https://github.com/katzenpost">Source</a>
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

## What we ship

### Available now

- **Pigeonhole**: anonymous storage protocol with thin clients in Go, Rust, and Python.
- **katzenqt**: Qt group chat client. Buildable from source today.
- **kpclientd**: client daemon. Buildable from source today.

### Coming next

- Pre-built packages for **katzenqt** and **kpclientd**.
- **Namenlos**: a public Katzenpost mix network anyone may use.

## Threat model

The published [Threat Model document](/docs/threat_model/) is an evolving
work in progress and does not yet incorporate the new designs introduced in
the paper. To understand the present state of the design, the
[Echomix paper](https://arxiv.org/abs/2501.02933) and the threat model
document must be read together.

## Where to go

- **[Documentation](/docs/)**: start here. Entry points for users, operators, application developers, core developers, and academics.
- **[Blog](/blog/)**: design notes and protocol explainers.
- **[Source](https://github.com/katzenpost)**: the Katzenpost monorepo, the `hpqc` post-quantum cryptography library, thin clients, `katzenqt`, and this website.
- **[Team](/pages/team/)** · **[Funders](/pages/funders/)** · **[Presentations](/pages/presentations/)**.
