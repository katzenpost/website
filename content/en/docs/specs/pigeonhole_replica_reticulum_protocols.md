---
title: ""
linkTitle: "Pigeonhole Storage Replica Reticulum Protocols"
description: ""
author: "David Stainton"
url: ""
date: ""
draft: "false"
slug: "reticulum"
layout: ""
type: ""
weight: "999"
version: ""
---

**Abstract**

Here I present a low bandwidth integration between Katzenpost mix networks and Reticulum mesh networks.
It offers:
* Reticulum users a post quantum encrypted group chat.
* Users of a Katzenpost mix network and users of Reticulum mesh networks the ability to chat
in the same groups and to use the other protocols built on Pigeonhole, from our
[Echomix paper](https://arxiv.org/abs/2501.02933).
* Operation with or without a Katzenpost mixnet. Mix networks need not use any of these features.


## Introduction

This document assumes you've read our [paper](https://arxiv.org/abs/2501.02933) and our
[Pigeonhole explained doc](https://katzenpost.network/docs/pigeonhole_explained/).

Pigeonhole has four layers, each resting on the one before:

1. A cryptographic capability protocol, BACAP.
2. A ciphertext storage system with a one week GC schedule, for asynchronous communication rather than permanent storage.
3. A channel abstraction for reading and writing fixed size ciphertext boxes.
4. A messaging API for one on one and group messaging.

A Pigeonhole storage replica can be connected to:

1. a Katzenpost mixnet only,
2. both a Reticulum mesh and a Katzenpost mixnet, or
3. a Reticulum mesh only.

Replicas on a mesh need no Internet connection. Some are multi-homed, connected to both a mesh
and the Internet.

Every storage query either reads or writes a box. A box is a fixed size ciphertext blob, a signature
over that blob, and a Box ID, the database key for the box. The Box ID is also the public key that
verifies the signature. Writing requires the matching private key; reading and decrypting require
the read capability, from which the decryption key is derived. See section 4 of our paper.


## Design Priorities

The Reticulum integration favours reliability over privacy. A mesh network does not provide the
traffic analysis resistance of a mix network and this design does not pretend otherwise. Its purposes
are post quantum security for Reticulum users and a group chat that keeps working under the
intermittent, partitioned connectivity typical of mesh networks.


## Storage Domains

There are two storage domains, each with its own replica set:

1. The mixnet domain: the replicas listed in the Katzenpost PKI document.
2. The mesh domain: the replicas listed in the mesh directory, a list of replica identity keys signed
   by the mesh directory key that clients ship with.

Each domain places a box by rendezvous hashing its Box ID over its own replicas, so the same Box ID
maps to different replicas in each domain. A mesh client must know every replica in the mesh directory
and none on the mixnet. Placement never spans the two domains: mesh links cannot carry the mixnet's
traffic, and a mesh cut off from the Internet must still serve the boxes written on it.

### Bridges

A bridge is a multi-homed replica in both domains: an ordinary replica on the mesh, and a Katzenpost
client sending queries through a courier on the mixnet.

* Mesh to mixnet is push. A mesh replica that stores a write forwards a copy to a reachable bridge,
  which writes it into the mixnet domain. Boxes a bridge brought in from the mixnet are not pushed back.
* Mixnet to mesh is pull, because the mixnet never notifies the mesh. A mesh client gives a bridge a
  watch list of the Box IDs it expects to read next. The bridge polls the mixnet for them and writes
  each one it finds into the mesh domain.
* Tombstones cross in both directions like any other box, so lagging readers on either side can skip them.

A bridge learns the Box IDs it forwards and the watch lists it holds, which the priorities above accept.
Replicas store a duplicate write once, so bridges need no coordination with each other.


## Mesh Placement

Each mesh replica's score for a box is the hash of its identity key concatenated with the Box ID.
Sorting the mesh directory by score gives the box's preference list. The mixnet stores a box on the
first two replicas of its own list. The mesh uses the first N, as a sloppy quorum with hinted handoff
in the manner of Amazon's Dynamo, so a box stays writable and readable while replicas are unreachable.

A client MKEM-encrypts each query to all N replicas, so whichever of them handles it can decrypt it.
Each extra recipient adds one encrypted key to the query, which bounds N on a low bandwidth mesh.

### Writes

A write goes to the first two reachable replicas among the N. A replica standing in for an unreachable
one ahead of it stores the box with a hint naming that replica. The write succeeds once two replicas
have stored the box.

### Hinted Handoff

A stand-in watches for announces from the replicas named in its hints. When one becomes reachable,
the stand-in sends it the box and, once acknowledged, deletes its copy and the hint. Hinted boxes
follow the weekly GC schedule like every other box, so a handoff that cannot complete in time ends
with the box.

### Reads

A read queries the N replicas in preference list order, skipping unreachable ones, until one returns
the box. Walking past the first two finds boxes held by stand-ins.

### Partition Healing

When a partition heals, hinted handoff moves each box to its owners. Placement depends only on the
Box ID, so the two sides never disagree about where a box belongs, only about whether it has arrived.
A tombstone supersedes the box it replaces wherever the two meet.


## Protocol 1: The Authenticated Key Update Protocol

MKEM, from our paper, is a multi-recipient encryption scheme built from a NIKE and an AEAD rather
than a KEM. A query is encrypted once and every recipient replica can decrypt it, which saves
bandwidth. Katzenpost clients use MKEM to reach replicas through a courier; Reticulum clients use it
to reach the N replicas of a box's preference list.

Clients therefore need the MKEM public keys of every replica in the mesh directory. Each replica
signs its current MKEM public key with its identity key and announces itself on Reticulum as a
Pigeonhole replica. Replicas gossip these signed keys, so a client can collect them from announces
or download the whole set from any replica it finds. Keys rotate weekly, so clients download them
once per week. The client verifies the mesh directory with the mesh directory key it ships with, and
each MKEM key with the identity key the directory lists.

The Katzenpost PKI signature scheme is too large for this. We need hybrid post quantum security with
very small signatures, so we propose SQIsign combined with Ed25519.
See the SQIsign paper: https://eprint.iacr.org/2026/1166

None of this requires a Katzenpost mixnet, PKI or dirauth.


## Protocol 2: The Replica Store and Forward Protocol

MKEM is already a hybrid post quantum construction, so the confidentiality of a query does not rely
on Reticulum's cryptography. Replicas forward MKEM ciphertexts to each other over Reticulum Links,
holding each one while its next hop is unreachable, until it reaches a replica able to decrypt it.
