---
title: ""
linkTitle: "Pigeonhole protocols over Reticulum"
description: ""
author: "David Stainton"
url: ""
date: ""
draft: "false"
slug: "pigeonhole-protocols-reticulum"
layout: ""
type: ""
weight: "999"
version: ""
---

## Pigeonhole protocols over Reticulum

A client on a Reticulum mesh reads and writes Pigeonhole boxes through one replica. This is
what it sends and receives. Replicas, placement and bridges are in
[Pigeonhole replicas over Reticulum](/docs/specs/reticulum/); BACAP is in the
[Echomix paper](https://arxiv.org/abs/2501.02933); a protocol on top, such as
[katzenqt1 chat](/docs/specs/katzenqt1-reticulum/), adds only what it writes into boxes.


## Replicas

|                           |                                                                        |
|---------------------------|------------------------------------------------------------------------|
| destination               | application name `pigeonhole`, aspect `replica`, single                |
| announce application data | 1 byte: 0, or 1 for a bridge to a mixnet                               |
| identity                  | the first heard for a destination; a later one for it is ignored       |
| entry replica             | any announced replica with a path, the fewest hops by preference       |

A client uses one replica at a time. The replica stores, forwards and finds boxes, and fetches
from the mixnet through a bridge; the client does none of that.


## Requests

A query is a Link request to the replica's destination. One Link per replica, one request at a
time on it, reopened when it closes; a request above the MTU travels as a Resource.

| path    | query       | reply                              |
|---------|-------------|------------------------------------|
| `write` | write query | result code                        |
| `read`  | read query  | result code, and the box when found |

A query whose first byte disagrees with its path is answered INVALID_PAYLOAD. `peek` is replica
to replica. Reference timeouts: 20 s to establish a Link, 60 s per request; an unanswered
request is asked again later, not repeated at once.


## Boxes

BACAP under the context string `pigeonhole context`.

|                                                                              | bytes         |
|------------------------------------------------------------------------------|---------------|
| Box ID: a blinded Ed25519 public key                                         | 32            |
| signature: Ed25519 over the ciphertext, verifying under the Box ID           | 64            |
| MessageBoxIndex: counter 8, blinding factor 32, encryption key 32, KDF state 32 | 104        |
| read capability: root public key, MessageBoxIndex                            | 136           |
| write capability: root private key as seed then public key, MessageBoxIndex  | 168           |
| ciphertext                                                                   | box size + 20 |

For the context string, the index's blinding factor and encryption key each go through
HKDF-BLAKE2b-512 with the string as salt. Box ID = root public key blinded by the derived
factor. Ciphertext = AES-GCM-SIV under the derived key, nonce the first 12 bytes of the Box ID,
the Box ID as associated data. Signature = root private key blinded by the derived factor, over
the ciphertext. A capability's index is its first box; each next index derives from the one
before it.

The box size is one number per mesh, equal to the mixnet's plaintext payload length where a
bridge exists. A client is told it with the mesh.


## Geometry

Every size on the mesh follows from the box size B, the plaintext a box carries.

| quantity                               | bytes   |
|----------------------------------------|---------|
| plaintext a protocol may put in a box  | B       |
| padded plaintext                       | B + 4   |
| ciphertext                             | B + 20  |
| read query                             | 33      |
| write query                            | B + 117 |
| reply to a write, or a miss            | 1       |
| reply with a box                       | B + 85  |
| tombstone write                        | 97      |

The reference meshes use B = 1000, which gives a 1020 byte ciphertext and a 1117 byte write
query. The seal scheme the protocols on top use is the hybrid NIKE `CTIDH1024-X25519` and the
signature scheme is Ed25519, as on the mixnet.

## Writing, reading, deleting

| action | send                            | outcome                                                                                                                       |
|--------|---------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| write  | write query                     | SUCCESS or ALREADY_EXISTS: the replica holds a box under that ID. Same bytes: SUCCESS. Different bytes: ALREADY_EXISTS, nothing changes; use the next index. |
| read   | read query                      | SUCCESS with the box: verify, open. NOT_FOUND: not written yet; poll with backoff, reference 2 s doubling to 60 s. TOMBSTONE: deleted. |
| delete | write query, empty ciphertext   | replaces the box; a box never replaces a tombstone                                                                            |

A client that has seen a tombstone treats that Box ID as deleted from then on; other replicas
may hold the box until the tombstone reaches them.


## Epochs

The mesh carries no epoch. Replica epoch = ⌊(now − 1496275200) / 604800⌋, Unix seconds.
Replicas keep the current and the previous epoch.


## Closed meshes

The same queries and replies, inside the Noise session of Pigeonhole replicas over Reticulum,
to a replica on the key list the client was given.


## Encoding

All integers are big endian.

### Queries

A read is 33 bytes:

* one byte, 0,
* the 32 byte Box ID.

A read with anything after the Box ID is refused.

A write is 97 bytes and the ciphertext:

* one byte, 1,
* the 32 byte Box ID,
* the 64 byte signature,
* the ciphertext, to the end of the message. There is no length field.

A tombstone is a write with an empty ciphertext: 97 bytes.

### Replies

* one byte, the result code,
* for SUCCESS to a read that found a box, the 64 byte signature and the ciphertext.

A reply to a write is the one byte. A reply to a read of an unwritten box, or of a tombstone, is
the one byte.

The codes are the Pigeonhole replica's: 0 SUCCESS, 1 NOT_FOUND, 2 INVALID_BOX_ID,
3 INVALID_SIGNATURE, 4 DATABASE_FAILURE, 5 INVALID_PAYLOAD, 6 STORAGE_FULL, 7 INTERNAL_ERROR,
8 INVALID_EPOCH, 9 REPLICATION_FAILED, 10 ALREADY_EXISTS, 11 TOMBSTONE.

### Padding

The plaintext of a box is:

* a 4 byte length,
* the data,
* zeros, to the box size plus 4 bytes.

The ciphertext is that plaintext encrypted, with a 16 byte tag: the box size plus 20 bytes.

### Announce

The application data of a replica's announce is one byte: 0, or 1 for a bridge. On a closed
mesh the replica's hybrid key follows it, as Pigeonhole replicas over Reticulum specifies.

### Vectors

`testdata/bridge_socket_vectors.json` in `pigeonhole_rns` holds query and reply bytes (`queries`,
`replies`), queries a replica refuses (`malformed`) and boxes with what a replica answers each
(`boxes`). The frames in it, a 4 byte length before each message, are the socket between a
bridge's two halves and are not sent by a client.
