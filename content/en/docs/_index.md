---
title: "Katzenpost Documentation"
linkTitle: "Documentation"
draft: false
menu: {main: {weight: 70}}
type: "base"
no_list: true
body_class: "td-no-sidebar"
---

<p class="lead">Choose your audience.</p>

```text
            forward (Sphinx)                         return (SURB reply)
    ──────────────────────────▶               ──────────────────────────▶

    gateway ─▶ mix¹ ─▶ mix² ─▶ mix³ ─▶ service ─▶ mix¹ ─▶ mix² ─▶ mix³ ─▶ gateway
```

Every client interaction is a round-trip through the stratified mix topology — the forward half carries a Sphinx packet to a service node; the return half carries a Single-Use Reply Block back through the same three mix layers to the originating gateway. This symmetry is what blunts traffic analysis.

## For users

You wish to use a Katzenpost client application to communicate.

> 🐈 **Namenlos public mixnet** *(coming soon)* — A public Katzenpost mix network that anyone may use, without the burden of operating their own. Documentation will appear here once the network is open to the public.

## For operators

You wish to run your own Katzenpost mix network with friends and collaborators.

|     | Title | Description |
|-----|-------|-------------|
| 📖  | **[Admin Guide](/docs/admin_guide/)** | Deploying and operating Katzenpost servers — installation, configuration, the Docker test mixnet, NAT considerations, and a full configuration appendix. |
| 🐳  | **[Run a Mix Server in Docker](/docs/run_katzenpost_mixnode_docker/)** | A focused recipe for running a single Katzenpost mix server inside a Docker container, intended for operators who wish to participate in an existing mix network. |
| 🔧  | **[Build from source](/docs/build_from_source/)** | Pinned versions of the Katzenpost stack and brief instructions for building each component (kpclientd, thin clients, katzenqt, server-side) from source. |

## For application developers

You wish to build software that integrates with Katzenpost — custom clients, services, or higher-level protocols layered atop the mixnet. Pigeonhole is the storage primitive on which those higher protocols are built. Alice mints a channel, writes a message, and Bob reads it with the capability she gives him out of band:

```python
import asyncio, os
from katzenpost_thinclient import ThinClient, Config

async def alice_writes_to_bob():
    alice = ThinClient(Config("/etc/namenlos/thinclient.toml"))
    await alice.start(asyncio.get_event_loop())

    # Mint a Pigeonhole channel: WriteCap for Alice, ReadCap to share with Bob.
    chan = await alice.new_keypair(os.urandom(32))

    # Encrypt and publish a message into the channel's first box.
    enc = await alice.encrypt_write(b"the eagle has landed",
                                    chan.write_cap, chan.first_message_index)
    await alice.start_resending_encrypted_message(
        write_cap=chan.write_cap, read_cap=None, message_box_index=None,
        reply_index=0, envelope_descriptor=enc.envelope_descriptor,
        message_ciphertext=enc.message_ciphertext, envelope_hash=enc.envelope_hash,
    )
    # Bob, given chan.read_cap out of band, calls encrypt_read +
    # start_resending_encrypted_message and receives "the eagle has landed".
```

|     | Title | Description |
|-----|-------|-------------|
| 📘  | **[Thin Client API Reference](/docs/thin_client_api_reference/)** | Complete API reference for the Go, Rust, and Python thin client libraries. |
| 📗  | **[Thin Client How-to Guide](/docs/thin_client_howto/)** | Task-oriented guides for accomplishing common operations with the thin client API. |
| 🕊️  | **[Understanding Pigeonhole](/docs/pigeonhole_explained/)** | A high-level introduction to the Pigeonhole anonymous storage protocol for application developers. |
| 🔧  | **[Build from source](/docs/build_from_source/)** | Pinned versions of the Katzenpost stack and brief instructions for building each component from source. |

## For core developers

You wish to contribute code to Katzenpost itself.

|     | Title | Description |
|-----|-------|-------------|
| 🛠️  | **[Design Specifications](/docs/specs/)** | The protocol specifications that the implementation must honour: Sphinx, KEMSphinx, the wire protocol, the directory authority, replay detection, and more. |
| 🐙  | **[Source Repository](https://github.com/katzenpost/katzenpost)** | The Katzenpost monorepo on GitHub: server, dirauth, client, courier, replica, and core. Issues, pull requests, and discussions live here. |

## For academics

You are a mathematician, computer scientist, security researcher, or hacker investigating the design.

|     | Title | Description |
|-----|-------|-------------|
| 📄  | **[Echomix paper](https://arxiv.org/abs/2501.02933)** | *Echomix: a Strong Anonymity System with Messaging.* The principal academic treatment of the Katzenpost design (arXiv). |
| 🔒  | **[Threat Model](/docs/threat_model/)** ([PDF](/research/Threat_Model_Doc.pdf)) | An evolving treatment of Katzenpost's security assumptions, attack scenarios, and mitigation strategies. |
| 📚  | **[Literature Review](/research/Literature_overview__website_version.pdf)** | A curated review of the academic literature underpinning Katzenpost's design decisions. |
| 🎧  | **[Audio Engineering Considerations](/docs/audio_eng/)** ([PDF](/research/Audio_Engineering_Considerations_for_a_Modern_Mixnet.pdf)) | A technical report on the challenges of carrying voice traffic through a modern mix network, with attention to usability and scalability. |
| 🛠️  | **[Design Specifications](/docs/specs/)** | The full set of protocol specifications. Useful reading for anyone investigating the design in depth. |
