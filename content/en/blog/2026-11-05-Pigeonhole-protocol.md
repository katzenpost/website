---
title: "Introduction to Pigeonhole Protocol"
date: "2026-11-05"
description: "What we have built on Pigeonhole so far: hushphone, a group chat client with voting that runs over the mixnet or a Reticulum mesh, and Pigeonhole services, which are hidden services on the mixnet."
author: "David Stainton"
tags: ["research", "mixnet", "reticulum", "apps", "pigeonhole", "protocol"]
version: ""
draft: false
---

Pigeonhole is a protocol for asynchronous, unlinkable communication. Without a read
capability, no one can tell which messages belong together, and sender and reader need not
be online at the same time. Our paper,
[Echomix: a Strong Anonymity System with Messaging](https://arxiv.org/abs/2501.02933), and
[Understanding Pigeonhole](/docs/pigeonhole_explained/) have the details. This post is about
the two things we have built on it so far: hushphone, a group chat client, and Pigeonhole
services, which are hidden services on the mixnet.

## Channels

A Pigeonhole channel is a sequence of *boxes*: fixed-size ciphertexts, each signed and named
by a Box ID. Two capabilities govern it. The write capability writes boxes and derives the
read capability; the read capability finds, verifies and decrypts them. A channel has one
writer and any number of readers. Storage replicas keep a box for one to two weeks, then
garbage-collect it.

We always get two-way communication the same way: each party makes a channel of their own,
and the two exchange read capabilities. We make that exchange with the
[contact voucher](/docs/specs/contactvoucher/) protocol, in which a single token crosses out
of band, in one direction only. That keeps the user's part simple, and it has security
properties that a bare exchange of read capabilities lacks.

## hushphone

[hushphone](https://github.com/katzenpost/hushphone) is group chat with push-to-talk voice
messages, for Linux and Android. It speaks katzenqt1, our
[group chat protocol](/docs/specs/groupchat/), in which every member writes a channel of
their own and reads everyone else's. Its groups are therefore the same ones
[katzenqt](https://github.com/katzenpost/katzenqt),
[jam](https://github.com/katzenpost/jam),
[frank_chat](https://github.com/katzenpost/frank_chat) and
[katzenrns](https://github.com/katzenpost/katzenrns) use.

### Voting, and where a CRDT belongs

hushphone has voting built in: a member puts a question and its options to the group, the
others vote and may change their votes, and everyone sees the counts as they change. This is
katzenqt's tally protocol, which rides on top of the group chat. A vote in progress is a
Conflict-free Replicated Data Type (CRDT). Each member publishes events on their own channel, and every client
computes the same thing:

```
state = fold(events)
```

The events may arrive in any order and the state comes out the same. They may not go
missing. An operation-based CRDT converges only if every member receives all of the events;
most of them will not do. A CRDT therefore corrects no errors, and it cannot be the
fundamental message type of a protocol in the hope that it will. It has to be layered on a
protocol that already delivers everything.

That is why we made the group chat reliable before we used a CRDT on it. In katzenqt1,
members acknowledge the boxes they have read, and an author writes again every box that some
member has not acknowledged
([acknowledgements and backfill](/docs/specs/groupchat/#opportunistic_acks)). The tally is
folded over a stream of events that has no gaps.

### Mixnet or mesh

hushphone reaches Pigeonhole over the Katzenpost mixnet, through the client daemon
`kpclientd`, or over a [Reticulum](https://reticulum.network) mesh, through a replica's
address. The groups and the protocol are the same on both. The mixnet hides which node
writes or reads a box from everyone, a global observer of the network included. On an open
mesh the replica a node talks to sees which boxes it writes and fetches, and when.

On the mesh, the storage is
[replica_rns](https://github.com/katzenpost/pigeonhole_rns), a Reticulum node that stores
boxes and replicates them to the other replicas it hears; the
[specification](/docs/specs/pigeonhole-protocols-reticulum/) has the details. A replica can
also be a bridge to a Katzenpost storage replica, so mesh users and mixnet users share
groups. We have tested exactly that: katzenrns users on a mesh chatting with hushphone users
on namenlos through the namenlos bridge.

We timed bare box operations, with no chat client in the way: write three boxes to a fresh
channel one after another, read them back at once (the first read), then read them again.
Figures are cumulative seconds, the median of five runs on 5 November 2026, with the range in
brackets.

| seconds | namenlos mixnet | Reticulum, local replica | Reticulum, namenlos bridge |
|---|---|---|---|
| write 1 box | 25 (24–30) | 0.05 (0.05–0.05) | 0.20 (0.20–0.20) |
| write 2 boxes | 51 (47–61) | 0.10 (0.10–0.10) | 0.35 (0.35–0.40) |
| write 3 boxes | 73 (67–80) | 0.15 (0.15–0.16) | 0.55 (0.50–0.60) |
| first read of 1 box | 24 (15–26) | 0.05 (0.05–0.05) | 0.15 (0.15–0.20) |
| read 1 box | 28 (21–31) | 0.05 (0.05–0.06) | 0.15 (0.15–0.20) |
| read 2 boxes | 46 (40–61) | 0.10 (0.10–0.11) | 0.30 (0.30–0.35) |
| read 3 boxes | 67 (65–90) | 0.15 (0.15–0.16) | 0.45 (0.45–0.50) |

The mixnet client was the Python thin client on its own `kpclientd`, with the default ARQ:
each operation is two round trips over five-hop Sphinx routes
([the Pigeonhole ARQ](/docs/pigeonhole_explained/#the-pigeonhole-arq)), and a read retries
until the box is there. The mesh client was `pigeonhole_rns`, over TCP to a replica on the
same machine and to the namenlos bridge replica, 145 ms away. The mesh figures exclude the 5
to 6 seconds Reticulum took to set up the Link, and are rounded up to the client's 50 ms
polling interval.

## Pigeonhole services

A Pigeonhole service is a hidden service that uses Pigeonhole channels as its transport. It
has no address and no open port: everything it sends or receives is a box on the storage
replicas. A client and a service talk as any two parties do on Pigeonhole, over two
channels, one written by each.

The difficulty is the first contact. Pigeonhole requires prior knowledge: without a
capability there is nothing to read. A client that has never talked to a service shares
nothing with it. Mixnet services have no such requirement. They run as plugins on service
nodes, a mixnet may have many service nodes, and the mixnet's PKI document publishes the
services each one hosts, so that any client can learn of them and use them.

We therefore use two mixnet services to bootstrap a connection to a Pigeonhole service:

- The **service directory** holds a descriptor for each Pigeonhole service, saying how to
  reach it.
- The **voucher router** relays a client's contact voucher, sealed to the service's key, to
  the service. The router cannot open it.

The service uses the voucher, and from then on the two share a two-way connection in which
the directory and the router take no part. The
[Pigeonhole services](/docs/specs/pigeonhole_services/) specification has the details.

The services written so far are in
[pigeonhole_protocols](https://github.com/katzenpost/pigeonhole_protocols):

- [zulip-bridge](https://github.com/katzenpost/pigeonhole_protocols/tree/main/rust/src/services/zulip)
  joins a Pigeonhole group chat to a Zulip stream. It is a member of the group and a bot in
  Zulip, and it relays text both ways.
- [status-bot](https://github.com/katzenpost/pigeonhole_protocols/blob/main/docs/status-bot.md)
  reports each epoch on the mixnet it is on: what changed in the PKI document, and which
  Pigeonhole services the directory lists and whether each answers. Anything else said to it
  gets an ELIZA answer.
- [motd](https://github.com/katzenpost/pigeonhole_protocols/tree/main/go/services/motd) is
  the message of the day, a minimal service to copy from.

A channel also carries a stream.
[kp-fa](https://github.com/katzenpost/pigeonhole_protocols/blob/main/docs/kp-fa.md)
broadcasts Ogg/Opus audio into a new channel and prints its read capability; a listener who
holds it tunes in live or from the start.
