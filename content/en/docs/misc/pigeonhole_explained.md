---
title:
linkTitle: "Understanding Pigeonhole"
description: "A high-level introduction to the Pigeonhole protocol for application developers"
categories: [""]
tags: [""]
author: ["David Stainton"]
version: 0
draft: false
slug: ""
url: "docs/pigeonhole_explained"
---

# Understanding Pigeonhole

Pigeonhole is the storage layer of the Katzenpost mix network. It
lets applications communicate anonymously using encrypted,
append-only streams. From a passive network observer's perspective
there is no consistent stream access and instead everything looks like
randomly scattered queries across storage servers.

```text
   client      ┌───── via mix network ─────┐    courier        replicas
                                                                   ┌────┐
   kpclientd ──▶  Sphinx round-trip (×3 mix layers)  ──▶  service  │  1 │
                                                         node      ├────┤
                                                         (courier) │  2 │
                                                            │      ├────┤
                                                            └─────▶│ ...│
                                                                   └────┘
                                              fixed-throughput     K = 2
                                              connections;          replicas
                                              cannot read box IDs   per box
                                                                   (consistent
                                                                    hashing)
```

This is the document to read first. Having understood the concepts
here, proceed to the [how-to guide](/docs/thin_client_howto/) for
task-oriented recipes, and consult the
[API reference](/docs/thin_client_api_reference/) for the precise
signatures.

For the privacy properties and the adversary they are designed to
withstand, see the [threat model](/docs/threat_model/) and the
[Echomix paper](https://arxiv.org/abs/2501.02933); a passive network
observer learns only that scattered, unlinkable queries traverse the
storage servers, never which messages belong to one stream nor who
reads them. For protocol details, see the
[Pigeonhole specification](/docs/specs/pigeonhole/) and sections
4-5 of the paper. Note that the published threat model is an evolving
work in progress and does not yet incorporate the newer designs the
paper introduces.


## Terminology

A short glossary of the terms used throughout this document. Each is
elaborated in its own section below.

- **Box.** The unit of storage. A box is a fixed-size, encrypted, signed
  ciphertext addressed by a pseudorandom identifier. Once written, a
  box's contents are immutable except by tombstoning.
- **Stream.** An ordered, append-only sequence of boxes addressed by a
  pair of capabilities; the analogue of a single-writer log. The terms
  **stream** and **channel** are used interchangeably throughout these
  documents and the API: they denote one and the same thing.
- **Write cap.** The capability that grants the right to sign and write
  messages to a stream and to derive the read cap from itself.
- **Read cap.** The capability that grants the right to read and verify
  a stream's contents. It cannot write or tombstone.
- **Tombstone.** A signed empty payload that overwrites a box's
  contents; the write cap holder uses it to retire prior messages.
- **BACAP.** Blinding-And-Capability scheme. The Ed25519 key-blinding
  construction that ties write caps, read caps, and indices to
  unlinkable pseudorandom box identifiers.
- **MKEM.** Multi-recipient KEM. The envelope encryption scheme that
  delivers each request to all of a box's replicas without revealing
  the box ID to the courier.
- **Sphinx.** The mixnet packet format used to route every request
  through three layers of mix nodes before it reaches the courier.
- **SURB.** Single-Use Reply Block. A pre-built Sphinx return path that
  allows the courier to reply to a request without learning the
  client's location.
- **Courier.** A service running on a Katzenpost service node. The
  courier mediates between clients and replicas, maintaining a
  fixed-throughput stream of envelopes so that traffic patterns cannot
  be inferred from the wire.
- **Replica.** A storage server. Each box is sharded across K=2 replicas
  via consistent hashing; replicas mirror writes to their shard peer to
  maintain redundancy.
- **Katzenpost epoch.** The network's wire-protocol epoch, lasting
  **20 minutes by default** (the duration is a deployment parameter and a
  given network operator may configure it otherwise). It governs the
  directory authority consensus, mix key rotation, and Sphinx routing. It
  does **not** govern how long a box's contents survive, and a reader need
  not concern themselves with it.
- **Replica epoch.** A separate, much longer epoch lasting **one week**,
  used solely by the storage replicas. Replicas rotate and garbage-collect
  their storage keys on this weekly schedule; it is this epoch, not the
  20-minute network epoch, that determines the lifetime of stored data.


## Pigeonhole Streams

All communication happens through Pigeonhole streams (also called
channels). A stream is an ordered, append-only sequence of encrypted
messages, known as boxes. These boxes are stored in the storage servers
using a hash based sharding scheme. Boxes have a fixed-size maximum
payload and are padded; the exact size is set by the pigeonhole
geometry, described below.

- **Append-only and immutable.** Once a message is written to a
  box, it cannot be overwritten by another write -- the replica
  rejects the second write with `BoxAlreadyExists`. New messages
  are appended at the next index. The only exception is tombstones:
  a tombstone unconditionally replaces the box contents with an
  empty signed payload, regardless of whether the box previously
  held data.
- **Single-writer, multi-reader.** One writer, any number of readers.
  Nothing in the protocol inherently forbids multiple writers; the
  constraint arises because each index addresses a box that may be
  written only once (tombstones aside). Two writers therefore have no
  agreed answer to the question of which index each should write to: were
  they both to target the same index it would be a race, and whoever
  writes first wins while the other's write is rejected with
  `BoxAlreadyExists`. Avoiding that requires out-of-band coordination, so
  in practice a stream has a single writer. Two-way communication is
  arranged as two streams, one in each direction.
- **Durable.** Each message is replicated across multiple storage
  nodes. Currently, set to 2 storage nodes per shard.
- **Ephemeral.** Storage is keyed to the **replica epoch**, which lasts
  **one week** (not to be confused with the 20-minute Katzenpost network
  epoch). Replicas retain the current and the preceding replica epoch and
  garbage-collect anything older, so a box's contents survive for roughly
  one to two weeks; nothing written to a box outlives that window.
- **Per-replica-epoch storage.** Capabilities are cryptographic
  credentials independent of any epoch schedule and continue to work
  indefinitely, but the data at any given box location does not carry
  across a **replica epoch** transition (the weekly schedule, not the
  20-minute network epoch): at the start of a new replica epoch the box
  reads as empty, even though the capability that addresses it is
  unchanged. Workflows that need data to outlive the replica epoch in
  which it was written must arrange to re-emit it (the copy command,
  described below, is the usual instrument for doing so atomically).
- **Unlinkable.** Storage servers cannot tell which messages belong
  to the same stream.


## Box size and the pigeonhole geometry

Every box carries a fixed-size payload, and a message is padded up to
that size before storage so that all boxes on the wire are
indistinguishable by length. A message larger than one box's payload
must be split across several boxes; one smaller is padded.

The exact size is not a hard-coded constant but a property of the
**pigeonhole geometry**, a deployment parameter rather than something
the application chooses. It is the operators of the mix network who
set the geometries: they choose the network's Sphinx geometry, and the
pigeonhole geometry is derived from, and must be consistent with, it.
A Pigeonhole request travels inside a Sphinx packet, so the usable box
payload is whatever the deployed Sphinx geometry allows once the
envelope and protocol overheads are subtracted. A network running a
larger Sphinx packet has a correspondingly larger box payload; one
running a smaller Sphinx geometry has a smaller one.

The `kpclientd` daemon's configuration file must carry these same
correct Sphinx and pigeonhole geometries, matching the network it is
to connect to; a daemon configured with the wrong geometries cannot
speak to that network. The thin client itself holds no such
configuration. When a thin client connects to `kpclientd`, the daemon
sends it the geometries over the local socket during the connection
handshake. An application should therefore treat the box payload size
as a value obtained at runtime from the daemon, not a fixed number to
hard-code. See the [API reference](/docs/thin_client_api_reference/)
for how each binding exposes it.


## Cryptographic Capabilities

Pigeonhole is a cryptographic capability system. Access to a stream
is controlled by two capabilities:

- The **write cap** can write messages, create tombstones, and derive
  the read cap. Only the write cap holder can sign and encrypt messages, and
  storage servers verify these signatures and store the signature and ciphertext.
- The **read cap** can read, verify signatures and decrypt messages. It cannot
  write or tombstone.

Creating a stream produces a write cap, a read cap, and a starting
index. The writer keeps the write cap. To grant someone read access,
share the read cap and index with them out-of-band. That is the
fundamental operation: **create a stream, share the read cap.**

Multiple readers can hold the same read cap independently.

A capability, once shared, cannot be revoked. There is no mechanism to
withdraw a read cap from someone who holds it: anyone in possession of
it can read every box the stream has produced and will produce, for as
long as that data survives. If a reader must lose access, the only
remedy is to abandon the stream entirely, create a fresh one, and
redistribute the new read cap to the readers who remain. Plan key
distribution with this permanence in mind.


## A first interaction: Alice writes, Bob reads

To anchor the abstractions above, here is the smallest useful
interaction: one writer (Alice) and one reader (Bob).

1. **Alice creates a stream.** She generates a 32-byte random seed and
   calls `new_keypair` (Go: `NewKeypair`). The thin client returns a
   write cap, a read cap, and the first message index.
2. **Alice shares the read cap with Bob.** She hands him the read cap
   and the first message index by any means independent of the mixnet,
   for instance a QR code in a face-to-face meeting, or a separate
   signal channel. Anyone with the read cap can decrypt the stream;
   anyone without it sees only pseudorandom traffic.
3. **Alice writes a message.** She calls `encrypt_write` with her write
   cap, the current index, and the plaintext, then sends the resulting
   envelope via `start_resending_encrypted_message`. The daemon
   dispatches the envelope through three mix layers, the courier
   receives it, and the courier writes the box to both of its replicas.
   Once the call returns Alice advances her local index.
4. **Bob reads the message.** He calls `encrypt_read` with his copy of
   the read cap and his current index, dispatches the envelope, and
   waits for the daemon to return the decrypted plaintext.
5. **Alice writes again.** She repeats step 3 with the next index. Bob
   reads in step 4 at his own pace, advancing his own index. The two
   indices are independent: Alice never blocks on Bob, and Bob can fall
   behind without losing messages until the replica-epoch garbage
   collection window (roughly one to two weeks) expires.

A two-way conversation is therefore two streams, one in each direction,
because every stream has exactly one writer. The
[how-to guide](/docs/thin_client_howto/) shows the equivalent code in
Go, Rust, and Python.


## What the client daemon does

Your application talks to a local daemon (kpclientd) through a thin
client library. The daemon handles all cryptography (BACAP
encryption and decryption, MKEM envelope encryption and decryption,
signature creation and verification, payload padding and unpadding),
Sphinx packet construction, courier selection, and automatic
retransmission (ARQ). Your application creates streams, tracks
indexes, and persists state for crash recovery.

Most API calls are local crypto operations with no network traffic.
Only `StartResendingEncryptedMessage` and `StartResendingCopyCommand`
touch the network.


## Consistency and timing

Pigeonhole offers no read-after-write ordering guarantee across
participants, and an application that assumes one will misbehave.

- **Reading ahead of the writer.** A reader who reads an index the
  writer has not yet written to receives `BoxIDNotFound`. This is not
  an error but the expected answer to "has anything been written here
  yet?": it simply means "not yet." The reader should wait and ask
  again rather than abandon the stream. The thin client exposes
  `IsExpectedOutcome` precisely so that an application can tell this
  benign outcome apart from a genuine failure; the
  [how-to guide](/docs/thin_client_howto/) gives the polling pattern.

- **Replication lag.** Each box is written to both of its K=2
  replicas, but the two are not updated in the same instant. A read
  dispatched in the brief interval after a write reaches one replica
  but before its peer has caught up may transiently return
  `BoxIDNotFound` even though the write has in fact succeeded. The
  remedy is the same: retry. A handful of retries spaced over a few
  seconds is normally ample.

- **Read-delay randomisation.** The courier maintains a
  fixed-throughput connection to the replicas, decoupled from the
  rate at which clients submit requests. A read therefore returns
  after a delay that bears no exploitable relation to when the data
  was written or requested. This randomised latency is a deliberate
  privacy property, not a defect: do not design protocols that depend
  on a read completing within a tight deadline.

The practical consequence is that every read should be written as a
poll with bounded retry, treating `BoxIDNotFound` as "try again
shortly" until either the data appears or an application-level timeout
elapses.


## Copy commands

Copy commands exist for when you need to atomically write more than
one box to one or more streams that already exist and are already
known to other entities. The writer creates a temporary stream,
packs all the destination writes into it, then sends a single copy
command to a courier. The courier reads the temporary stream,
executes all the writes to their destination streams, then
overwrites the temporary stream with tombstones. Either all the
destination writes succeed or none of them are visible to readers.

Use cases: sending to a group, backfilling messages for an offline
reader, atomically tombstoning old messages while writing new ones.


## Tombstones

A tombstone is a Pigeonhole box which is signed with an empty
ciphertext. Unlike normal writes, which are rejected if the box
already exists, a tombstone unconditionally replaces the box
contents. Only the write cap holder can create tombstones. Tombstones
can be sent directly or bundled into a copy command for atomic
deletion.


## Protocol Composition

Many different protocols can be composed using these Pigeonhole streams.
For example, in our [Group Chat Design](/docs/specs/group_chat) each
group participant creates their own channel to write to. Each of the participants
shares their own channel's ReadCap with the other group members. Therefore
each group member monitors and reads from all the other channels in the group.
Each of them can simply write to their own channel in order to write a message
to the group.

Fundamentally, protocols are composed by creating channels and sharing the read caps
to those channels. When writing to a channel the entity doing the writing must keep
track of the current index into the channel. This is the reason why channels are single
writer, multi reader; because without coordination, multiple writers would be racing to
write first before any of the others write to a specific index.

