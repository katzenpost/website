---
title: "Katzenpost Documentation"
linkTitle: "Documentation"
draft: false
menu: {main: {weight: 70}}
type: "base"
no_list: true
body_class: "td-no-sidebar"
---

<img src="/images/ZII-WIZ3.png" alt="ANSI wizard casting a spell, by Zeus" class="img-fluid mb-4" style="max-width: 640px;">

## For users

Client applications, packages, and a public mixnet.

|     | Title | Description |
|-----|-------|-------------|
| 🐈  | **Namenlos public mixnet** | A public Katzenpost mix network that anyone may use, without the burden of operating their own. `katzenqt` connects to it out of the box; live network health is on the [status page](https://status.namenlos.network/). |
| 💬  | **katzenqt group chat** | A decentralised group chat application running over the Katzenpost mix network and the Pigeonhole storage services. Pre-built packages forthcoming. [Build and run from source](/docs/build_katzenqt/) in the meantime. |

## For operators

You wish to run your own Katzenpost mix network with friends and collaborators.

|     | Title | Description |
|-----|-------|-------------|
| 📖  | **[Admin Guide](/docs/admin_guide/)** | Deploying and operating Katzenpost servers: installation, configuration, the Docker test mixnet, NAT considerations, and a full configuration appendix. |
| 🐳  | **[Run a Mix Server in Docker](/docs/run_katzenpost_mixnode_docker/)** | A focused recipe for running a single Katzenpost mix server inside a Docker container, intended for operators who wish to participate in an existing mix network. |
| 🔧  | **[Build from source](/docs/build_from_source/)** | Pinned versions of the Katzenpost stack and brief instructions for building the components users and operators run (kpclientd, katzenqt, server-side) from source. |

## For application developers

You wish to build software that integrates with Katzenpost.

|     | Title | Description |
|-----|-------|-------------|
| 📘  | **[Thin Client API Reference](/docs/thin_client_api_reference/)** | Complete API reference for the Go, Rust, and Python thin client libraries. |
| 📗  | **[Thin Client How-to Guide](/docs/thin_client_howto/)** | Task-oriented guides for accomplishing common operations with the thin client API. |
| 🕊️  | **[Understanding Pigeonhole](/docs/pigeonhole_explained/)** | A high-level introduction to the Pigeonhole anonymous storage protocol for application developers. |

## For core developers

You wish to contribute code to Katzenpost itself.

|     | Title | Description |
|-----|-------|-------------|
| 🛠️  | **[Design Specifications](/docs/specs/)** | The protocol specifications that the implementation must honour: Sphinx, KEMSphinx, the wire protocol, the directory authority, replay detection, and more. |
| <i class="fab fa-github"></i>  | **[Source Repository](https://github.com/katzenpost/katzenpost)** | The Katzenpost monorepo on GitHub: server, dirauth, client, courier, replica, and core. Issues, pull requests, and discussions live here. |

## For academics

You are a mathematician, computer scientist, security researcher, or hacker investigating the design.

Read in the order below. Seasoned mixnet researchers may skip ahead to the Echomix paper.

|     | Title | Description |
|-----|-------|-------------|
| 📚  | **1. [Literature Review](/research/Literature_overview__website_version.pdf)** *(last updated April 2024)* | Start here if you are new to mixnet research. Field context, attack taxonomy, and the conceptual positions the Echomix paper builds on. |
| <img src="/iconx/arxiv.svg" alt="arXiv" height="14">  | **2. [Echomix paper](https://arxiv.org/abs/2501.02933)** | *Echomix: a Strong Anonymity System with Messaging.* Katzenpost's design, presented as research (arXiv). |
| 🔒  | **3. [Threat Model](/docs/threat_model/)** ([PDF](/research/Threat_Model_Doc.pdf)) | Detailed security assumptions and mitigations specific to the deployed system. |

Supplementary reading:

|     | Title | Description |
|-----|-------|-------------|
| 🎧  | **Audio Engineering Considerations** ([PDF](/research/Audio_Engineering_Considerations_for_a_Modern_Mixnet.pdf)) | A technical report on the challenges of carrying voice traffic through a modern mix network, with attention to usability and scalability. |
