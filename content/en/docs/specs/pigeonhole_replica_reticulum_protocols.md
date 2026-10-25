---
title: ""
linkTitle: "Pigeohole Storage Replica Reticulum Protocols"
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

Here I present to you a low bandwidth protocol integration between Katzenpost mix networks and the Reticulum mesh networks.
The value proposition here is as follows:
* It provides Reticulum users access to a post quantum encrypted group chat
* It will allow users of both a Katzenpost mix network and of Reticulum mesh networks
to interact with each other in group chats and with other protocols based on
the Pigeonhole protocol from our [Echomix paper](https://arxiv.org/abs/2501.02933).
* This design can function with or without a Katzenpost mixnet. Likewise Katzenpost
mix networks don't have to use any of these Reticulum integration features if they don't want to.


## Introduction

Although this document assumes you've read our [paper](https://arxiv.org/abs/2501.02933) and our [Pigeonhole explaioned doc](https://katzenpost.network/docs/pigeonhole_explained/)
I will nevertheless elaborate some of the same design here in order to be clear what changes I propose making.

Pigeonhole protocol has a few layers to it:

1. Cryptographic capability protocol
2. A ciphertext storage system which a 1 week GC schedule to facilitate asynchronous communications but not permanent storage.
3. A channel abstraction for reading and writing fixed sized ciphertext boxes
4. A message system API

It's an enchilada. It has layers and each layer rests on the previous layer.
Number 4 is the highest layer. A messaging API for one on one or group messaging.

Regardless of the messaging protocols, if there exists Reticulum mesh networks that
share some of the same storage servers as a Katzenpost mix network then we should be
able to enable clients across both networks to chat with one another. Or to interact with
other pigeonhole based protocols.

I envision three ways to configure a Pigeonhole storage replica node:

1. katzenpost connected only
2. reticulum mesh and katzenpost connected
3. reticulum mesh connected only


We want to make a meaningful integration with Reticulum such that pigeonhole storage replica
nodes can be operated on a Reticulum mesh network WITHOUT being connected to the Internet.
The ideas is that some of the nodes will be multi-homed, connected to a mesh and to the Internet.
These replica nodes form a store and forward network which endeavors to
proxy opaque ciphertext queries to the correct hash shard so they can be decrypted and processed.

Separately, we want to design another protocol used by these storage replica nodes to update each other's
knowledge of each other's current public keys used for decrypting and processing queries.

All the storage node queries are either to read a box or to write a
box. A box is just a fixed size ciphertext blog, a signature over that
blob, and a Box ID which is the database key that points to the
box. The Box ID is also interestingly enough the public key one uses
to check the signature. The private key is needed for decryption
however. See section 4 of our paper.


## Design Priorities

The Reticulum integration favours reliability over privacy. A mesh network does
not provide the traffic analysis resistance of a mix network and this design does
not pretend otherwise. Its purposes are post quantum security for Reticulum users
and a group chat that keeps working under the intermittent, partitioned connectivity
typical of mesh networks. Interoperation with a Katzenpost mix network is a bonus.


## Storage Domains

There are two storage domains, each with its own replica set and its own placement:

1. The mixnet domain: the storage replicas listed in the Katzenpost PKI document,
   placed by the existing hash sharding scheme.
2. The mesh domain: the storage replicas listed in the mesh roster, a list of replica
   identity keys signed by the roster root key that clients ship with.

Each domain places a box by rendezvous hashing its Box ID over its own replica set.
The same Box ID therefore maps to different replicas in each domain. A mesh client
needs knowledge of every replica in the mesh roster and of no replica on the mixnet.
Placement never spans the two domains: mesh links cannot carry the mixnet's traffic
volume, and a mesh partitioned from the Internet must still serve the boxes written
on it.

### Bridges

A bridge is a multi-homed replica present in both domains. On the mesh side it is
an ordinary mesh replica; on the mixnet side it is a Katzenpost client sending
queries through a courier. Bridges carry boxes between the domains:

* Mesh to mixnet is push. A mesh replica that stores a write forwards a copy to a
  reachable bridge, which writes it into the mixnet domain.
* Mixnet to mesh is pull. The mixnet never notifies the mesh, so a mesh client
  registers a watch list with a bridge: the Box IDs it expects to read next on the
  streams it follows. The bridge polls the mixnet for those boxes and writes each
  one it finds into the mesh domain.
* Tombstones cross in both directions like any other box, so a reader that has
  fallen behind on either side can skip past them.

A bridge learns the Box IDs it forwards and the watch lists it holds, which is
accepted under the priorities above. Writes are idempotent, so a box forwarded by
several bridges or several replicas is stored once and bridges need no coordination
with each other.


## Mesh Placement

On the mesh, each replica's score for a box is the hash of its identity key
concatenated with the Box ID, as in the mixnet scheme. Sorting the roster by score
gives the box's preference list. The mixnet domain uses only the first two entries
of that list. The mesh domain uses the whole list, as a sloppy quorum with hinted
handoff in the manner of Amazon's Dynamo, so that a box remains writable and readable
while replicas are unreachable.

### Writes

A write goes to the first two reachable replicas in the preference list. When a
replica among the first two is unreachable, the next reachable replica in the list
stores the box in its place together with a hint naming the replica it stands in for.
The write succeeds once two replicas have stored the box.

### Hinted Handoff

A replica holding hinted boxes watches for announces from the replicas named in its
hints. When a named replica becomes reachable, the stand-in sends it the box and,
once the box is acknowledged, deletes its copy and the hint. Hinted boxes are
garbage collected on the same weekly schedule as every other box, so a handoff that
cannot complete within the box's lifetime ends with the box.

### Reads

A read queries replicas in preference list order, skipping unreachable ones, until
a replica returns the box or a configured number of replicas have answered that they
do not hold it. Walking past the first two finds boxes held by stand-ins during a
partition or before handoff completes.

### Partition Healing

When a partition heals, boxes written on either side reach their owners through
hinted handoff. Because placement is determined by the Box ID alone, the two sides
never disagree about where a box belongs, only about whether it has arrived there.
A tombstone supersedes the box it replaces wherever the two meet.


## Protocol 1: The Authenticated Key Update Protocol

As a reminder, our hash based sharding scheme puts two replicas in each shard.
In theory we could make the number of replicas per shard configurable. But in practice
our current implementations are designed for this to be hardcoded to be 2 only.
Related to this I wanted to mention that to save bandwidth we use a multi-recipient "KEM scheme"
which we call MKEM in our paper. It's actually not at all a KEM and is based on a NIKE and an AEAD.
The idea behind MKEM is that we only want to encrypt our replica query once but we want to send it to
two different replicas and let them all decrypt it.

Clients, for example group chat clients on a Katzenpost mix network use MKEM to talk to replica through a courier.
Reticulum mesh network clients will use MKEM to encrypt their read or write query to the two replicas for the shard
they are sending to. The Reticulum based store and forward network of replica nodes will eventually forward their opaque ciphertext query
to the two correct replicas for that query's destination shard.

In order for this to work clients need to be able to learn the MKEM keys of all the replicas in the mesh roster.
All replicas connected to Reticulum form a gossip network to propagate MKEM public keys.
These replicas that are on a Reticulum mesh network also announce themseleves as a pigeonhole replica.
Reticulum clients merely have to here an announce packet of a pigeonhole replica? Or maybe they can query
a reticulum router for a cache announces list.

The client simply downloads all keys from the gossip network; actually there will be a signature scheme
or some kind of certificate. The client must already have all replica node's master signing public key.
The signature scheme that we will use for this will be different than the existing Katzenpost signature scheme
used by the PKI system (dirauth nodes and PKI clients). Why different? Because we need our protocol to be
as compact and low bandwidth as possible but we also want hybrid post quantum security.

**We need a post quantum signature scheme with very small signatures.**

How about we use SQISign combined with Ed25519?
Here's the SQISign paper https://eprint.iacr.org/2026/1166

The replicas gossip about each other's MKEM pub keys so that later on clients can ask any replica
they find for all the keys. Client's only need to download all the keys once per week due to key rotation.
No Katzenpost mixnet is required. No Katzenpost PKI or Dirauth is required. This works without Katzenpost.
But it is better with Katzenpost because a mixnet and a mesh net interacting with each other through
these cryptographic storage of ciphertexts has interesting security and privacy properties, and it
gives the Reticulum community a group chat with post quantum cryptographic protections.


## Protocol 2: The Replica Store and Forward Protocol

Since MKEM ciphertext is already a hybrid post quantum cryptographic construction,
we are not relying on the Reticulum cryptography for confidentiality of our client's replica query.
This protocol uses reticulum session transport to proxy the MKEM ciphertext message from replica to replica.
It's a gossip network as well of course. But it's also a store and forward network.

The details of this protocol need to be fleshed out but I am not a Reticulum expert so I'm not sure what we should do.




