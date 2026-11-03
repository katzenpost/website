---
title: ""
linkTitle: "katzenqt1 chat over Reticulum"
description: ""
author: "David Stainton"
url: ""
date: ""
draft: "false"
slug: "katzenqt1-reticulum"
layout: ""
type: ""
weight: "999"
version: ""
---

## katzenqt1 chat over Reticulum

katzenqt1 is the group chat protocol of katzenqt, hushphone, jam, frank_chat and katzenrns. It is
CBOR messages of a few types, each written as one BACAP box in the writer's own stream. A client
keeps a read capability and an index for every member and reads each member's next box;
acknowledgements inside the messages tell it where others have got to. All of that logic is in
a sans-IO state machine, written once per language, and the same machine runs on the Katzenpost
mixnet and on a Reticulum mesh. What differs is the transport beneath it: on the mixnet the
client daemon does BACAP and carries the boxes; on a mesh the transport does BACAP itself and
sends the boxes of [Pigeonhole protocols over Reticulum](/docs/specs/pigeonhole-protocols-reticulum/).
So a new mesh client is a transport, or a transport and a state machine that matches these:

| language | repository                                                                       | state machine                                                                                                              |
|----------|----------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| Lean     | [katzenpost/cryptlib](https://github.com/katzenpost/cryptlib)                    | [Cryptlib/Protocols/GroupComm/GroupChatKatzenqt1/Member/](https://github.com/katzenpost/cryptlib/tree/main/Cryptlib/Protocols/GroupComm/GroupChatKatzenqt1/Member) |
| Rust     | [katzenpost/pigeonhole_protocols](https://github.com/katzenpost/pigeonhole_protocols) | [rust/src/protocols/katzenqt1/member/](https://github.com/katzenpost/pigeonhole_protocols/tree/main/rust/src/protocols/katzenqt1/member) |
| Go       | [katzenpost/pigeonhole_protocols](https://github.com/katzenpost/pigeonhole_protocols) | [go/protocols/katzenqt1/member/](https://github.com/katzenpost/pigeonhole_protocols/tree/main/go/protocols/katzenqt1/member) |
| Python   | [katzenpost/pigeonhole_protocols](https://github.com/katzenpost/pigeonhole_protocols) | [py/pigeonhole_protocols/katzenqt1/member/](https://github.com/katzenpost/pigeonhole_protocols/tree/main/py/pigeonhole_protocols/katzenqt1/member) |

The transports written so far, one interface per language, which the state machine's engine
drives:

| transport                               | who does BACAP      | implementations                                                                                                                                                                                                                                                                              |
|-----------------------------------------|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Katzenpost mixnet, through kpclientd    | the client daemon   | Rust [rust/src/transport/thinclient/](https://github.com/katzenpost/pigeonhole_protocols/tree/main/rust/src/transport/thinclient), Go [go/transport/thinclient/](https://github.com/katzenpost/pigeonhole_protocols/tree/main/go/transport/thinclient), Lean [GroupChatKatzenqt1/Daemon.lean](https://github.com/katzenpost/group_chat_client/blob/main/GroupChatClient/GroupChatKatzenqt1/Daemon.lean) in [katzenpost/group_chat_client](https://github.com/katzenpost/group_chat_client) |
| Reticulum mesh                          | the transport, with hpqc | Python [katzenrns/transport.py](https://github.com/katzenpost/katzenrns/blob/main/katzenrns/transport.py) over [pigeonhole_rns](https://github.com/katzenpost/pigeonhole_rns)                                                                                                      |
| in memory, for tests                    | the transport       | Rust [sim.rs](https://github.com/katzenpost/pigeonhole_protocols/blob/main/rust/src/transport/sim.rs), Go [go/transport/sim/](https://github.com/katzenpost/pigeonhole_protocols/tree/main/go/transport/sim), Python [transport/sim.py](https://github.com/katzenpost/pigeonhole_protocols/blob/main/py/pigeonhole_protocols/transport/sim.py), Lean [GroupChatKatzenqt1/Sim.lean](https://github.com/katzenpost/group_chat_client/blob/main/GroupChatClient/GroupChatKatzenqt1/Sim.lean) |

The interface itself: Rust [transport/mod.rs](https://github.com/katzenpost/pigeonhole_protocols/blob/main/rust/src/transport/mod.rs),
Go [transport/transport.go](https://github.com/katzenpost/pigeonhole_protocols/blob/main/go/transport/transport.go),
Python [transport/base.py](https://github.com/katzenpost/pigeonhole_protocols/blob/main/py/pigeonhole_protocols/transport/base.py),
Lean [GroupChatKatzenqt1/Backend.lean](https://github.com/katzenpost/group_chat_client/blob/main/GroupChatClient/GroupChatKatzenqt1/Backend.lean).

The protocol's rules, rosters, acknowledgements, backfill, numbering and rewrite, are the
[Group chat specification](/docs/specs/groupchat/); vouchers are the
[Contact voucher specification](/docs/specs/contactvoucher/).

This document gives version 4 of the wire format. Readers accept version 3 as well, whose
encodings are at the end; a writer emits version 4.


## Model

* A member is a BACAP stream that it alone writes. Its key is the first 32 bytes of its read
  capability.
* A group is a set of members. Reading the group is reading every member's stream from the
  position given for it.
* Membership changes are Introductions written in members' streams. Every box carries its
  writer's membership hash.
* A newcomer joins through a voucher that a member answers.
* The mesh has no copy command: every box is written directly, in the order given here.


## What the state machine asks of the transport

| operation                                   | on the mesh                                                       |
|---------------------------------------------|-------------------------------------------------------------------|
| new stream                                  | a fresh write capability                                          |
| write box (write capability, index, plaintext) | pad, encrypt, sign, write query; ALREADY_EXISTS is a refusal   |
| read box (read capability, index)           | read query: NOT_FOUND, TOMBSTONE, or the plaintext                |
| next index                                  | the BACAP derivation                                              |
| epoch                                       | ⌊(now − 1496275200) / 604800⌋                                     |
| box size                                    | the mesh's                                                        |
| voucher mint, derive stream, induct, open   | below                                                             |


## Vouchers

|                |                                                                                   |
|----------------|-----------------------------------------------------------------------------------|
| voucher        | 32 bytes, BLAKE2b-256 of the VoucherPayload; shown and carried as standard base64 |
| voucher stream | a write capability generated from SHAKE256(voucher): Ed25519 seed 32 bytes, KDF state 32, counter 16 |
| box 0          | the VoucherPayload, at the stream's first index                                   |
| boxes 1 on     | the sealed VoucherReply, framed, from the next index                              |
| seal           | sealed box over the hybrid NIKE X25519 then CTIDH1024, `CTIDH1024-X25519`         |
| salt           | 32 bytes                                                                          |

The newcomer:

1. Makes a stream S and a seal keypair (sk, pk).
2. Signs [S's read capability, pk, display name], as CBOR, with S's root key (Ed25519), and
   builds VoucherPayload [S's read capability, pk, display name, signature]. voucher =
   BLAKE2b-256 of its bytes.
3. Writes the VoucherPayload to box 0. Gives the voucher away.
4. Reads box 1, then each next box while the one before began with `C`. NOT_FOUND: wait.
   TOMBSTONE: withdrawn, the join failed. The boxes' bytes after their first byte, joined, are
   the sealed reply: open with sk, giving VoucherReply [WhoReply, salt].
5. Mutates S's write capability KDF state by the salt and writes the group there from its first
   index. WhoReply is a ReplyWho: reads each member from the position it gives.

A member answering the voucher:

1. Derives the voucher stream and reads box 0. NOT_FOUND: wait. TOMBSTONE: withdrawn.
2. Checks BLAKE2b-256(payload) = voucher, and the signature under the root key in the
   payload's read capability. Otherwise stops.
3. Draws a 32 byte salt. The newcomer's live read capability is the payload's read capability
   with its KDF state mutated by the salt. Builds the ReplyWho: every member with the position
   the newcomer starts from, its own stream at the index its Introduction will occupy.
4. Writes Introduction [display name, live read capability] to its own stream at that index,
   ahead of anything queued.
5. Seals VoucherReply [WhoReply, salt] to pk, cuts the sealed bytes into pieces of the box size
   less one, and writes them from box 1 on, each behind `C`, the last behind `F`, each until a
   replica holds it. ALREADY_EXISTS on box 1: another member answered; stop.
6. Reads the newcomer at the live read capability from its first index.

A member answers one voucher at a time. Box 0 is left as written; the voucher is spent once box
1 exists. A payload in the version 3 form, a CBOR map, is answered wholly in version 3: the
map form of the ReplyWho, sealed with the MKEM, unframed, in box 1 alone.


## ReplyWho

A CBOR array of one to five elements; trailing `None`s are left out.

```rust
struct ReplyWho(
    /// One per place: `None` for a member the sender cannot name.
    Vec<Option<PleaseAdd>>,
    /// One per place, the member's roster; `None` while unknown.
    Option<Vec<Option<Vec<RosterEntry>>>>,
    Option<Vec<IntroAt>>,
    /// The sender's place.
    Option<usize>,
    /// The newcomer's place: the number of places.
    Option<usize>,
);
struct PleaseAdd(String, [u8; 136]);        // [display_name of 1 to 30 characters, read_cap]: key, then the start index
struct RosterEntry(usize, Option<usize>);   // [roster index, place]
struct IntroAt(usize, [u8; 104], usize);    // [by, index, member]
```

A reply is refused when a place's name is empty or longer than 30 characters or its read
capability is not 136 bytes. Without rosters, the newcomer takes the places named, the first
as introducer, every roster unknown. With rosters, the reply is refused when the newcomer's
place is not the number of places, the introducer's is not below it, there are 256 places or
more, two places share a key, a roster names a place that does not exist, or the introducer's
place is `None`.

A pigeonhole service that admits a client answers with one place and no rosters.


## Boxes

| plaintext                                       | meaning                                      |
|-------------------------------------------------|----------------------------------------------|
| `F`, GroupChatMessage CBOR                      | a message                                    |
| empty                                           | tombstone: the message was deleted, step past |
| `C`, bytes                                      | a chunk of a long message, in its own stream |
| `I`, 4 byte big endian chunk count, 136 byte read capability of the chunk stream; or `I` and the read capability | a long message: its chunks are `C` boxes ending in an `F` box |

A message fits the box size less one byte. A reader that does not fetch chunks steps past an `I`
box.

GroupChatMessage, a CBOR array of four to seven elements; trailing `None`s are left out:

```rust
struct GroupChatMessage(
    u64,                 // version: 4
    [u8; 32],            // membership_hash
    u64,                 // msg_type, below
    Body,                // the type's payload; None for control
    Option<Vec<u8>>,     // acks, layout under Encoding
    Option<Vec<u8>>,     // numbers, layout under Encoding
    Option<Vec<u8>>,     // introduced_at, layout under Encoding
);
enum Body {
    Text(String),                                   // type 0
    Introduction(String, [u8; 136]),                // type 1: [display_name, read_cap]
    FileUpload(Vec<u8>, String, String),            // type 2: [payload, filetype, basename]
    Who(Value), ReplyWho(Value), Tally(Value),      // types 3, 4, 5 to 9: as the app defines
    None,                                           // type 10
}
```

| `msg_type` | message      | body                                      |
|------------|--------------|-------------------------------------------|
| 0          | text         | the text                                  |
| 1          | introduction | [display_name of 1 to 30 characters, read_cap] |
| 2          | file upload  | [payload, filetype, basename]             |
| 3          | who          | the app's value                           |
| 4          | reply who    | the app's value                           |
| 5 to 9     | tally        | the app's value                           |
| 10         | control      | `None`; only acks, numbers, introduced_at |

A type above 10 is refused. Any message may carry acks, numbers and introduced_at.

membership_hash = SHA-256(`KP:membership:v1` ‖ the members' keys, each once, in byte order,
one's own included). The sentinel for an unknown membership is 32 zero bytes; readers also
accept `TODO` repeated to 32 bytes. Content carries the hash as written; control messages and
Introductions carry the writer's current membership, or the sentinel.


## Geometry

B is the box size of [Pigeonhole protocols over Reticulum](/docs/specs/pigeonhole-protocols-reticulum/).
A member's box holds B − 1 bytes of GroupChatMessage CBOR; each box of a sealed reply holds
B − 1 bytes of it. The costs below are measured on the encoders. h is a string's CBOR header:
1, 2 or 3 bytes below 24, 256 and 65536 bytes.

| field or message                                  | bytes                                  |
|---------------------------------------------------|----------------------------------------|
| GroupChatMessage: array, version, membership_hash, msg_type | 37                           |
| text of n bytes                                   | h + n                                  |
| introduction, name of n bytes                     | 139 + h + n                            |
| file upload, payload n, type t, name b            | 1 + (h + n) + (h + t) + (h + b)        |
| control body                                      | 1                                      |
| acks of k members                                 | h + 1 + naming + 8k; naming ≤ k        |
| numbers of m prefixes                             | h + 1 + 8m                             |
| introduced_at                                     | 107                                    |
| each absent field before a present one            | 1                                      |
| ReplyWho without rosters, places with names of n  | 2 + Σ (139 + h + n)                    |
| ReplyWho with rosters and p − 1 introductions, names of 10 | 160, 429, 1272, 2797 for p = 1, 2, 5, 10 |
| VoucherPayload, name of n bytes                   | 367 + h + n                            |
| sealed VoucherReply                               | WhoReply + 211 + h                     |
| seal public key, X25519 ‖ CTIDH1024               | 160                                    |

Version 3 cost 70 for the fixed fields, 5 + h + n for a text, 174 + h + n for an introduction,
451 + h + n for a VoucherPayload and 359 for the seal, so version 4 saves 33 bytes on every
box, 35 on an introduction, 84 on a voucher and 146 on its reply. With B = 1000: a text is at
most 959 bytes; a control message acknowledges up to 117 members; a sealed reply that fits
box 1 alone holds a WhoReply of 786 bytes, five places without rosters or three with; a larger
reply continues in box 2 and on.


## Reading

* Each member's stream from the position given: a box or a tombstone advances, NOT_FOUND waits
  with the backoff.
* acks, numbers and introduced_at let a reader jump and backfill, as the state machine does.
* Replicas keep two epochs; older boxes are recovered only through acknowledgements.


## Vectors

In `katzenpost/pigeonhole_protocols`: `testdata/katzenqt1/groupchat_wire_vectors_v4.json`
(messages, written boxes, membership hashes, replies, refused arrays) for version 4,
`testdata/katzenqt1/groupchat_wire_vectors.json` for version 3, and
`testdata/katzenqt1/acks_vectors.json`. Voucher vectors are `voucher/testdata/voucher_vectors_v2.json`
in `katzenpost/hpqc`, beside the version 3 file; BACAP vectors are in the same repository.
katzenrns is a client of this protocol on meshes: match the above, not its storage or interface.
Until version 4 is merged, the code that writes it is on the branch `katzenqt1-v4` of
`hpqc`, `pigeonhole_protocols`, `cryptlib`, `group_chat_client`, `katzenqt` and `katzenrns`;
the deployed version 3 is the branch `katzenqt1-v3` of each.


## Encoding

Byte fields are CBOR byte strings; names are text strings; integers are unsigned.

### Acks

Empty when nothing is acknowledged. Otherwise:

* one byte, the number of members acknowledged, less one,
* the members by roster index, ascending: a list of one byte each when no longer than the
  bitmap, else a bitmap, most significant bit first, as many bytes as the highest index needs,
* one 8 byte little endian counter per member, same order: the counter of the acknowledged box.

A naming as long as the count is a list, shorter is a bitmap. Refused: a list out of order, a
bitmap ending in a zero byte, a bitmap naming other than the count.

### Numbers

* one byte, the first roster index assigned,
* one 8 byte key prefix per member numbered, consecutive indexes.

A single byte is the roster index of the member the same message's Introduction introduces.
Refused when the indexes would pass 255 or a prefix repeats.

### IntroducedAt

* one byte, the introducer's roster index in the sender's roster,
* the 104 byte index of the Introduction in the introducer's stream.

### Voucher stream

* VoucherPayload, box 0: array [read_cap 136 bytes, seal public key 160 bytes, display_name,
  signature 64 bytes]; the signature is Ed25519 by the read cap's root key over the CBOR array
  of the first three.
* Voucher: BLAKE2b-256 of the VoucherPayload's bytes.
* VoucherReply: array [WhoReply, the ReplyWho's CBOR; salt 32 bytes]. Sealed as a sealed box
  to the seal public key: the sender's ephemeral hybrid public key, 160 bytes, then
  XSalsa20-Poly1305 of the plaintext under a key and nonce derived from the shared secret, as
  hpqc's `sealedbox` defines, with the NIKE named `CTIDH1024-X25519`.
* Boxes 1 on: the sealed bytes in pieces of B − 1, each behind one byte, `C` for a piece that
  continues, `F` for the last.

### Version 3

Readers accept these as well; a version 3 message is a CBOR map, a version 4 one an array,
which the first byte tells apart.

GroupChatMessage: map `version` 3, `membership_hash`, `msg_type`, then the type's field under
its name, `text`, `introduction` (map `display_name`, `read_cap`), `file_upload` (map `payload`,
`filetype`, `basename`), `who`, `reply_who`, `tally`, and optional `acks`, `numbers`,
`introduced_at`. A map without `msg_type` has the type of the field it carries, text when none.

ReplyWho: map `please_adds` (array of map `display_name`, `read_cap`, or null), `rosters`,
`introductions`, `introducer`, `newcomer`, the last four absent when unknown.

Vouchers: PleaseAdd is map `DisplayName`, `MessageReadCap`; SignedPleaseAdd map `PleaseAdd`
(its CBOR), `Signature` (64 bytes, Ed25519 by the stream's root key over the PleaseAdd bytes);
VoucherPayload map `SignedPleaseAdd` (its CBOR), `VoucherPubKey`; all canonical CBOR.
VoucherReply is map `WhoReply`, `VoucherSalt`, sealed with hpqc's MKEM to the seal public key
and written unframed to box 1 alone. A member answers a version 3 payload in this form, with
the map form of the ReplyWho inside.
