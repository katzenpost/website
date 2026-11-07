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
what it sends and receives. Replicas, replication and bridges are in
[Pigeonhole replicas over Reticulum](/docs/specs/reticulum/); BACAP is in the
[Echomix paper](https://arxiv.org/abs/2501.02933); a protocol on top, such as
[katzenqt1 chat](/docs/specs/katzenqt1-reticulum/), adds only what it writes into boxes.


## Replicas

|                           |                                                                        |
|---------------------------|------------------------------------------------------------------------|
| destination               | application name `pigeonhole`, aspect `replica`, single                |
| announce application data | 1 byte of flags, under Encoding; a bridge's 16 byte mixnet id after it |
| identity                  | the first heard for a destination; a later one for it is ignored       |
| entry replica             | any announced replica with a path, the fewest hops by preference       |

A client uses one replica at a time. The mesh runs in open mode: every replica holds every box,
and the replica forwards, syncs and finds boxes, and fetches from the mixnet through a bridge;
the client does none of that. Replicas are authenticated only by Reticulum's classical link
encryption.


## Requests

A query reaches a replica over a Link to its destination, in one of two modes. One Link per
replica, reopened when it closes. Both modes carry the same query and reply bytes.

**Request mode**, every replica not announcing bit 3: the query is a Link request; a request
above the MTU travels as a Resource. Up to 8 queries in flight per Link.

| path    | query       | reply                              |
|---------|-------------|------------------------------------|
| `write` | write query | result code                        |
| `read`  | read query  | result code, and the box when found |

A query whose first byte disagrees with its path is answered INVALID_PAYLOAD. `subscribe` and
`unsubscribe` are under Push; the other paths are replica to replica. Reference timeouts: 20 s
to establish a Link, 60 s per request; an unanswered request is asked again later, not repeated
at once.

**Channel mode**, replicas announcing bit 1: the query goes as Channel messages on the Link,
for Reticulum stacks with Links and Channel but no requests or Resources. A client uses it
only with replicas that announce bit 1, and only it with those announcing bit 3. The
query's first byte picks read, write, subscribe or unsubscribe. A query or reply larger than
one Channel message is cut into pieces, each a frame carrying the query's request id; the reply
comes back with the same request id. A replica drops a request whose pieces do not all arrive
within 60 s. Bytes on the air for one box of 1000 bytes, client sent / received:

| link MTU | query | request mode | channel mode |
|----------|-------|--------------|--------------|
| 500      | write | 1484 / 297   | 1468 / 428   |
| 500      | read  | 329 / 1436   | 480 / 1456   |

Channel mode costs about 100 to 150 bytes more per query, mostly the proof every Channel packet
gets. With the `mesh` box size a write is one packet in either mode.

**Choosing a mode.** The reference clients have a mode setting: request, Channel, or auto, the
default. Auto asks a replica with a Link request first and, when a replica announcing bit 1
does not answer, asks again in Channel mode, and keeps per replica the mode that answered. The
Rust client on Reticulum-rs speaks Channel mode alone. Replicas asking each other go Channel
first, as Pigeonhole replicas over Reticulum describes.


## Push

A client on a replica announcing bit 4 need not poll. After a read answers NOT_FOUND, the
client subscribes to that Box ID on the same Link, in Channel mode, since pushes come only
over Channel. When the replica holds the box it pushes it down the Link, and the client takes
the box from the push with no further query. The client then subscribes to the stream's next
Box ID.

Pushes are best effort, so a stream waiting for a push still reads again every 5 minutes,
which also renews the subscription. A subscription lasts at most an hour, and a Link waits for
at most 256 Box IDs. Against a replica that does not announce push, and on the mixnet, the
client polls with backoff.


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

The box size B is the plaintext a box carries. Two sizes are fixed: `mesh`, 256 bytes, the
largest multiple of 16 whose write fits one Link packet at the 500 byte MTU with 16 bytes to
spare in either mode, and `mixnet`, 1549 bytes, the Katzenpost box. A client on Reticulum writes
at `mesh`. A box too long for that size is written at the smallest allowed size that holds it;
only a voucher's box 0 ever is, since it is never split. A reader takes a box of any allowed size: the
two above, the size its transport was given (1549 by default) and any configured extra, each
from 141 to 16384 bytes. It refuses any other size, and a replica answers a box of a size it
does not take with INVALID_PAYLOAD.


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

With B = 256 that is a 276 byte ciphertext and a 373 byte write query; with B = 1549, 1569 and
1666. The seal scheme the protocols on top use is the hybrid NIKE `CTIDH1024-X25519` and the
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
A replica keeps a box for the replica epoch it arrived in and the next, one to two weeks, and
may evict the oldest boxes earlier when its disk is full.


## Overhead

This section gives the bytes every operation puts on a Reticulum link at the 500 byte MTU, for
the two box sizes a mesh carries, B = 256 and B = 1549.

The Pigeonhole bytes are measured: queries and replies come from the encoders of
`pigeonhole_rns` with BACAP from `hpqc`, and agree with `testdata/box_sizes.json` in
`pigeonhole_protocols`. The voucher sizes are measured from `voucher_vectors_v2.json` in `hpqc`.
Reticulum's encryption overhead is measured by encrypting with RNS 1.5.7's own Token.

The packets are computed from RNS 1.5.7's framing: the header and proof sizes are its constants,
and its own `ResourceAdvertisement` packs the advertisements. The same computation reproduces,
byte for byte, the eight figures `tests/e2e_two_replicas.py` measured for a 1000 byte box in the
table under Requests, once a 20 byte keepalive in each direction is counted in the Channel read.
Airtime is computed from these sizes with the LoRa formula below; it has not been measured on
radios.

### Layers

| layer | bytes |
|-------|-------|
| read query | 33 |
| write query | B + 117: 373 for B = 256, 1666 for B = 1549 |
| tombstone write | 97 |
| reply: written, not found, tombstone | 1 |
| reply with a box | B + 85: 341, 1634 |
| subscribe to n Box IDs, and its answer | 3 + 32n, and 5 |
| push | 32 + the reply with the box: 373, 1666 |
| Link request: msgpack of [time, path hash, query] | the query plus 30, or 31 from 256 bytes |
| Link response: msgpack of [request id, reply] | the reply plus 21, or 22 from 256 bytes |
| Channel: envelope and frame header, per piece of at most 421 bytes | 10 |
| Link encryption of n bytes: IV, padding to 16 bytes, HMAC | 48 + 16 × (⌊n / 16⌋ + 1) |
| packet header: flags, hops, link id, context | 19 |
| proof of a Channel packet: header, packet hash, signature | 115 |

A Link request or response larger than the Link MDU, 431 bytes, travels as a Resource: the
sender encrypts it once with 4 random bytes before it and sends an advertisement (211 bytes
here) and parts of up to 464 bytes, each behind a header; the receiver sends a request for the
parts (131 bytes for four) and an 83 byte proof. Requests and responses that fit one packet are
not proven; every Channel packet is.

The mesh write in request mode, layer by layer: the 373 byte query becomes 404 bytes of msgpack,
464 of ciphertext and a 483 byte packet; the one byte reply becomes 22, 64 and 83. In Channel
mode the query becomes 383 bytes framed, 432 encrypted and a 451 byte packet; the reply becomes
11, 64 and 83, and each side proves the other's packet with 115 bytes.

Opening a Link costs 86 bytes from the client, 118 from the replica and 83 from the client
again, once per Link. An open Link sends a 20 byte keepalive each way at most every 360 seconds.

### Per operation

Each cell lists the packets one side sends, in bytes. `bytes` is the sum of both sides. The
LoRa frames column is for an RNode, which sends a packet of up to 254 bytes in one frame and a
larger one in two, each frame carrying one byte of its own header, so the LoRa payload on the
air is the bytes plus one per frame.

#### B = 256

| operation | mode | client sends | replica sends | bytes | packets | LoRa frames |
|---|---|---|---|---|---|---|
| write | Link request | 483 | 99 | 582 | 1 + 1 | 2 + 1 |
| write | Channel | 451 + 115 | 83 + 115 | 764 | 2 + 2 | 3 + 2 |
| tombstone | Link request | 195 | 99 | 294 | 1 + 1 | 1 + 1 |
| tombstone | Channel | 179 + 115 | 83 + 115 | 492 | 2 + 2 | 2 + 2 |
| read, found | Link request | 131 | 435 | 566 | 1 + 1 | 1 + 2 |
| read, found | Channel | 115 + 115 | 419 + 115 | 764 | 2 + 2 | 2 + 3 |
| read, not found | Link request | 131 | 99 | 230 | 1 + 1 | 1 + 1 |
| read, not found | Channel | 115 + 115 | 83 + 115 | 428 | 2 + 2 | 2 + 2 |
| read, tombstone | Link request | 131 | 99 | 230 | 1 + 1 | 1 + 1 |
| read, tombstone | Channel | 115 + 115 | 83 + 115 | 428 | 2 + 2 | 2 + 2 |
| subscribe | Channel | 115 + 115 | 83 + 115 | 428 | 2 + 2 | 2 + 2 |
| push | Channel | 115 | 451 | 566 | 1 + 1 | 1 + 2 |

#### B = 1549

| operation | mode | client sends | replica sends | bytes | packets | LoRa frames |
|---|---|---|---|---|---|---|
| write | Link request | 211 + 483 + 483 + 483 + 387 | 131 + 83 + 99 | 2360 | 5 + 3 | 9 + 3 |
| write | Channel | 499 + 499 + 499 + 483 + 115 | 83 + 115 + 115 + 115 + 115 | 2638 | 5 + 5 | 9 + 5 |
| tombstone | Link request | 195 | 99 | 294 | 1 + 1 | 1 + 1 |
| tombstone | Channel | 179 + 115 | 83 + 115 | 492 | 2 + 2 | 2 + 2 |
| read, found | Link request | 131 + 131 + 83 | 211 + 483 + 483 + 483 + 339 | 2344 | 3 + 5 | 3 + 9 |
| read, found | Channel | 115 + 115 + 115 + 115 + 115 | 499 + 499 + 499 + 451 + 115 | 2638 | 5 + 5 | 5 + 9 |
| read, not found | Link request | 131 | 99 | 230 | 1 + 1 | 1 + 1 |
| read, not found | Channel | 115 + 115 | 83 + 115 | 428 | 2 + 2 | 2 + 2 |
| read, tombstone | Link request | 131 | 99 | 230 | 1 + 1 | 1 + 1 |
| read, tombstone | Channel | 115 + 115 | 83 + 115 | 428 | 2 + 2 | 2 + 2 |
| subscribe | Channel | 115 + 115 | 83 + 115 | 428 | 2 + 2 | 2 + 2 |
| push | Channel | 115 + 115 + 115 + 115 | 499 + 499 + 499 + 483 | 2440 | 4 + 4 | 4 + 8 |

A read that finds nothing costs the same at either size. Only a found box, a write and a push
grow with B. At B = 256 every query and reply fits one packet, but a packet over 254 bytes, such
as a mesh write, takes two LoRa frames. A write fits one LoRa frame only for B ≤ 48 in Channel
mode and B ≤ 27 in request mode.

### Joining through a voucher

The voucher protocol is reads and writes of boxes, so its cost is the sum of the rows above.
The newcomer writes the VoucherPayload to box 0 and reads the sealed reply from box 1 on. The
inductor reads box 0, writes its Introduction to its own stream, and writes the sealed reply in
pieces of B − 1 bytes, one box each. The compact VoucherPayload is 373 bytes for a five letter
display name, 368 bytes plus a name shorter than 24 bytes, so it does not fit a 256 byte box.
It is written at the smallest allowed size that holds it, 1549 by default, and read at that
size. An Introduction with a name of 10 bytes is 188 bytes and takes one mesh box.

The sealed reply is the ReplyWho plus 213 bytes for a ReplyWho of 24 to 255 bytes, plus 214
from 256: the vectors' 37 byte ReplyWho seals to 250. The ReplyWho grows with the group; with
rosters and names of 10 bytes it is 160 bytes for a group of one member, 429 for two and 1272
for five. The table gives each side's bytes, with the reply boxes written at B = 256; in the
last three columns the newcomer's exchange comes first, then the inductor's.

| members | sealed reply | boxes | mode | newcomer sends | inductor sends | replicas send | packets | LoRa frames |
|---|---|---|---|---|---|---|---|---|
| 1 | 373 | 2 | Link request | 2309 | 1794 | 1183 + 2296 | 12 + 14 | 18 + 21 |
| 1 | 373 | 2 | Channel | 2555 | 2273 | 1611 + 2657 | 18 + 22 | 24 + 29 |
| 2 | 643 | 3 | Link request | 2440 | 2277 | 1618 + 2395 | 14 + 16 | 21 + 24 |
| 2 | 643 | 3 | Channel | 2785 | 2839 | 2145 + 2855 | 22 + 26 | 29 + 34 |
| 5 | 1486 | 6 | Link request | 2833 | 3726 | 2923 + 2692 | 20 + 22 | 30 + 33 |
| 5 | 1486 | 6 | Channel | 3475 | 4537 | 3747 + 3449 | 34 + 38 | 44 + 49 |

These assume every box is there when read. Each read that finds a box not yet written adds a
miss, and a subscription adds the subscribe and the push in place of the second read. The
inductor then reads the newcomer's stream like any other member's.

## LoRa airtime

A LoRa frame of PL bytes takes, by Semtech's formula,

```text
T_sym      = 2^SF / BW
n_payload  = 8 + max(⌈(8 PL − 4 SF + 28 + 16 CRC − 20 IH) / (4 (SF − 2 DE))⌉ × (CR + 4), 0)
T_frame    = (n_preamble + 4.25) × T_sym + n_payload × T_sym
```

with RNode's settings: CRC on (CRC = 1), explicit header (IH = 0), low data rate optimization
(DE = 1) when a symbol lasts more than 16 ms, and n_preamble = max(18, ⌈24 ms / T_sym⌉). CR = 1
is coding rate 4/5. The firmware programs four symbols fewer into SX127x radios, so their frames
are four symbols shorter than given here. Channel access waits are not counted.

| setting | symbol | preamble | low data rate optimization | 21 B frame | 116 B frame | 255 B frame |
|---|---|---|---|---|---|---|
| SF7, 125 kHz, 4/5 | 1.024 ms | 24 symbols | off | 73 ms | 211 ms | 416 ms |
| SF9, 125 kHz, 4/5 | 4.096 ms | 18 symbols | off | 226 ms | 656 ms | 1291 ms |
| SF12, 125 kHz, 4/5 | 32.768 ms | 18 symbols | on | 1810 ms | 4923 ms | 9347 ms |

The 21, 116 and 255 byte frames are a keepalive, a proof and a full frame, each with RNode's
header byte.

Under the EU 868 MHz duty cycle of 1 %, each transmitter may be on the air 36 seconds an hour. The
table gives, per operation, the client's and then the replica's airtime, and how many such
operations each could send an hour on that budget alone, one hop apart. A replica answering
several clients shares one budget among them, and every transport node on a longer path spends
its own.

| operation | B | mode | SF7 | SF9 | SF12 |
|---|---|---|---|---|---|
| write | 256 | Link request | 0.80 / 0.19 s; 45 / 188 | 2.48 / 0.59 s; 14 / 60 | 17.87 / 4.27 s; 2 / 8 |
| write | 256 | Channel | 0.96 / 0.38 s; 37 / 95 | 2.99 / 1.17 s; 12 / 30 | 21.82 / 8.70 s; 1 / 4 |
| read, found | 256 | Link request | 0.24 / 0.72 s; 152 / 49 | 0.74 / 2.25 s; 48 / 15 | 5.41 / 16.40 s; 6 / 2 |
| read, found | 256 | Channel | 0.42 / 0.91 s; 85 / 39 | 1.31 / 2.85 s; 27 / 12 | 9.85 / 20.83 s; 3 / 1 |
| read, not found | 256 | Link request | 0.24 / 0.19 s; 152 / 188 | 0.74 / 0.59 s; 48 / 60 | 5.41 / 4.27 s; 6 / 8 |
| read, not found | 256 | Channel | 0.42 / 0.38 s; 85 / 95 | 1.31 / 1.17 s; 27 / 30 | 9.85 / 8.70 s; 3 / 4 |
| subscribe | 256 | Channel | 0.42 / 0.38 s; 85 / 95 | 1.31 / 1.17 s; 27 / 30 | 9.85 / 8.70 s; 3 / 4 |
| push | 256 | Channel | 0.21 / 0.75 s; 170 / 47 | 0.66 / 2.34 s; 54 / 15 | 4.92 / 16.89 s; 7 / 2 |
| write | 1549 | Link request | 3.40 / 0.59 s; 10 / 60 | 10.58 / 1.85 s; 3 / 19 | 76.42 / 13.46 s; < 1 / 2 |
| write | 1549 | Channel | 3.46 / 1.01 s; 10 / 35 | 10.76 / 3.14 s; 3 / 11 | 78.39 / 23.47 s; < 1 / 1 |
| read, found | 1549 | Link request | 0.64 / 3.33 s; 56 / 10 | 1.99 / 10.37 s; 18 / 3 | 14.61 / 74.95 s; 2 / < 1 |
| read, found | 1549 | Channel | 1.06 / 3.41 s; 34 / 10 | 3.28 / 10.62 s; 10 / 3 | 24.62 / 77.41 s; 1 / < 1 |
| join, newcomer | | Link request | 3.87 / 2.04 s; 9 / 17 | 12.05 / 6.36 s; 2 / 5 | 87.25 / 46.26 s; < 1 / < 1 |
| join, inductor | | Link request | 3.03 / 3.90 s; 11 / 9 | 9.43 / 12.16 s; 3 / 2 | 68.23 / 87.75 s; < 1 / < 1 |
| join, newcomer | | Channel | 4.30 / 2.83 s; 8 / 12 | 13.39 / 8.84 s; 2 / 4 | 98.08 / 65.13 s; < 1 / < 1 |
| join, inductor | | Channel | 3.94 / 4.54 s; 9 / 7 | 12.26 / 14.13 s; 2 / 2 | 90.06 / 103.51 s; < 1 / < 1 |

The join rows are for a group of one member, request mode on a Python replica and Channel mode
on a Rust one. At SF7 a client can write a mesh box about 40 times an hour; at SF9, about 13; at
SF12, once or twice. A 1549 byte box costs three to four times a mesh box to write. At SF12 that
write takes over 76 seconds, more than two hours of a 1 % budget, and every join makes one.


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

### Channel frames

Each Channel message has MSGTYPE `0x5048` and carries one frame:

* a 2 byte request id,
* a 1 byte piece index, from 0,
* a 1 byte piece count, 1 to 255,
* the piece: the next slice of the query or reply.

A frame whose count is 0 or differs from earlier pieces of its request, or whose index is not
below its count, is dropped with its request. Duplicate pieces are ignored.

Piece size is computed from the Link: link MDU = ⌊(MTU − 68) / 16⌋ × 16 − 1, Channel MDU = link
MDU − 6, piece = Channel MDU − 4. At MTU 500 that is 431, 425 and 421 bytes, so a write of one
1000 byte box takes three frames.

### Channel messages

A stack that is not RNS must match RNS's Channel on the wire:

* each message is one Link packet with context `CHANNEL` (0x0E), its payload a 6 byte envelope,
  MSGTYPE, sequence number and length, each 2 bytes, then the message;
* sequence numbers wrap at 65536; messages are delivered in order, and out-of-order ones
  buffered up to 48 ahead; duplicates and ones behind are dropped;
* every Channel packet is acknowledged by the Link's packet proof, and a receiver must prove
  each one, or the sender retries and then closes the Link;
* the sender keeps at most its window of unproven packets in flight: 2 at first, one more per
  delivery, one less per timeout;
* a packet is resent with the same sequence number up to 5 tries, after
  1.5^(tries − 1) × max(2.5 × RTT, 0.025 s) × (packets in flight + 1.5).

### Subscribe and push

Subscribe is the Channel query `6 | ttl u16 seconds | box id 32 | ...`, or the Link request
`subscribe` with the bytes after the 6. The answer is `0 | taken u16 | ttl u16`: the first
`taken` IDs are subscribed, for the granted `ttl`, the asked one capped at 3600, 0 asking for
3600. A malformed subscribe is answered with the one byte 5. Unsubscribe is `7 | box id 32 | ...`,
or the request `unsubscribe`, dropping those IDs, or all when none is named; the answer is the
one byte 0.

A push is a run of Channel messages of MSGTYPE `0x5049`, framed as Channel frames are under
request ids the replica counts, carrying `box id 32 | reply`, the reply as for a read: 0 with the
signature and ciphertext, or 11 for a tombstone.

### Announce

The application data of a replica's announce is one byte of flags: bit 0 a bridge, bit 1 serves
Channel mode, bit 2 serves the replica paths in Channel mode, bit 3 serves no Link requests,
bit 4 serves push. A bridge follows it with its 16 byte mixnet id.

### Vectors

`testdata/bridge_socket_vectors.json` in `pigeonhole_rns` holds query and reply bytes (`queries`,
`replies`), queries a replica refuses (`malformed`) and boxes with what a replica answers each
(`boxes`). The frames in it, a 4 byte length before each message, are the socket between a
bridge's two halves and are not sent by a client.
