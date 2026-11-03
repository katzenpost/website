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

katzenqt1 is the group chat protocol of katzenqt, hushphone, jam and katzenrns. On a mesh it
needs only the boxes of [Pigeonhole protocols over Reticulum](/docs/specs/pigeonhole-protocols-reticulum/);
this document is what it writes into them. The member state machine, which decides what to
write and read next, exists in four languages. A new client reuses one or matches it:

| language | repository                                                                       | state machine                                                                                                              |
|----------|----------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| Lean     | [katzenpost/group_chat_client](https://github.com/katzenpost/group_chat_client)  | [GroupChatClient/](https://github.com/katzenpost/group_chat_client/tree/main/GroupChatClient)                               |
| Rust     | [katzenpost/pigeonhole_protocols](https://github.com/katzenpost/pigeonhole_protocols) | [rust/src/protocols/katzenqt1/member/](https://github.com/katzenpost/pigeonhole_protocols/tree/main/rust/src/protocols/katzenqt1/member) |
| Go       | [katzenpost/pigeonhole_protocols](https://github.com/katzenpost/pigeonhole_protocols) | [go/protocols/katzenqt1/member/](https://github.com/katzenpost/pigeonhole_protocols/tree/main/go/protocols/katzenqt1/member) |
| Python   | [katzenpost/pigeonhole_protocols](https://github.com/katzenpost/pigeonhole_protocols) | [py/pigeonhole_protocols/katzenqt1/member/](https://github.com/katzenpost/pigeonhole_protocols/tree/main/py/pigeonhole_protocols/katzenqt1/member) |

Its rules, rosters, acknowledgements, backfill, numbering and rewrite, are the
[Group chat specification](/docs/specs/groupchat/); vouchers are the
[Contact voucher specification](/docs/specs/contactvoucher/).


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
| voucher        | 32 bytes, SHA-256 of the VoucherPayload; shown and carried as standard base64     |
| voucher stream | a write capability generated from SHAKE256(voucher): Ed25519 seed 32 bytes, KDF state 32, counter 16 |
| box 0          | the VoucherPayload, at the stream's first index                                   |
| box 1          | the sealed VoucherReply, at the next index                                        |
| seal           | MKEM over the hybrid NIKE X25519 then CTIDH1024                                   |
| salt           | 32 bytes                                                                          |

The newcomer:

1. Makes a stream S and a seal keypair (sk, pk).
2. Builds PleaseAdd {DisplayName, MessageReadCap = S's read capability}; SignedPleaseAdd
   {PleaseAdd, Signature = Ed25519 by S's root key over the PleaseAdd bytes}; VoucherPayload
   {SignedPleaseAdd, VoucherPubKey = pk}. voucher = SHA-256(VoucherPayload).
3. Writes the VoucherPayload to box 0. Gives the voucher away.
4. Polls box 1. NOT_FOUND: wait. TOMBSTONE: withdrawn, the join failed. A box: open with sk,
   giving VoucherReply {WhoReply, VoucherSalt}.
5. Mutates S's write capability KDF state by the salt and writes the group there from its first
   index. WhoReply is a ReplyWho: reads each member from the position it gives.

A member answering the voucher:

1. Derives the voucher stream and reads box 0. NOT_FOUND: wait. TOMBSTONE: withdrawn.
2. Checks SHA-256(payload) = voucher and the signature under the root key in MessageReadCap.
   Otherwise stops.
3. Draws a 32 byte salt. The newcomer's live read capability is MessageReadCap with its KDF
   state mutated by the salt. Builds the ReplyWho: every member with the position the newcomer
   starts from, its own stream at the index its Introduction will occupy.
4. Writes Introduction {display_name, live read capability} to its own stream at that index,
   ahead of anything queued.
5. Writes VoucherReply {WhoReply, VoucherSalt}, sealed to pk, to box 1, until a replica holds
   it. ALREADY_EXISTS: another member answered; stop.
6. Reads the newcomer at the live read capability from its first index.

A member answers one voucher at a time. Box 0 is left as written; the voucher is spent once box
1 exists.


## ReplyWho

A CBOR map with these fields; absent is `None`.

```rust
struct ReplyWho {
    /// One per place: `None` for a member the sender cannot name.
    please_adds: Vec<Option<PleaseAdd>>,
    /// One per place, the member's roster; `None` while unknown.
    rosters: Option<Vec<Option<Vec<RosterEntry>>>>,
    introductions: Option<Vec<IntroAt>>,
    /// The sender's place.
    introducer: Option<usize>,
    /// The newcomer's place: the number of places.
    newcomer: Option<usize>,
}
struct PleaseAdd { display_name: String, read_cap: [u8; 136] } // key, then the start index
struct RosterEntry(usize, Option<usize>);                      // [roster index, place]
struct IntroAt(usize, [u8; 104], usize);                       // [by, index, member]
```

Without `rosters`, the newcomer takes the places named, the first as introducer, every roster
unknown. With `rosters`, the reply is refused when `newcomer` is not the number of places,
`introducer` is not below it, there are 256 places or more, two places share a key, a roster
names a place that does not exist, or the introducer's place is `None`.

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

GroupChatMessage, a CBOR map with these fields in this order; absent is `None`:

```rust
struct GroupChatMessage {
    version: u64,                        // 3; readers accept 0 to 3
    membership_hash: [u8; 32],
    msg_type: u64,                       // see below
    text: Option<String>,                // type 0
    introduction: Option<Introduction>,  // type 1
    file_upload: Option<FileUpload>,     // type 2
    who: Option<Value>,                  // type 3, kept and rewritten as read
    reply_who: Option<Value>,            // type 4, kept and rewritten as read
    tally: Option<Value>,                // kept and rewritten as read
    acks: Option<Vec<u8>>,               // layout under Encoding
    numbers: Option<Vec<u8>>,            // layout under Encoding
    introduced_at: Option<Vec<u8>>,      // layout under Encoding
}
struct Introduction { display_name: String, read_cap: [u8; 136] } // 1 to 30 characters
struct FileUpload { payload: Vec<u8>, filetype: String, basename: String }
```

| `msg_type` | message      | carries                                   |
|------------|--------------|-------------------------------------------|
| 0          | text         | `text`                                    |
| 1          | introduction | `introduction`                            |
| 2          | file upload  | `file_upload`                             |
| 3          | who          | `who`                                     |
| 4          | reply who    | `reply_who`                               |
| 10         | control      | only `acks`, `numbers`, `introduced_at`   |

A type above 10 is refused. A message without `msg_type` has the type of the field it carries,
text when none. Any message may carry `acks`, `numbers` and `introduced_at`.

membership_hash = SHA-256(`KP:membership:v1` ‖ the members' keys, each once, in byte order,
one's own included). The sentinel for an unknown membership is 32 zero bytes; readers also
accept `TODO` repeated to 32 bytes. Content carries the hash as written; control messages and
Introductions carry the writer's current membership, or the sentinel.


## Geometry

B is the box size of [Pigeonhole protocols over Reticulum](/docs/specs/pigeonhole-protocols-reticulum/).
A member's box holds B − 1 bytes of GroupChatMessage CBOR; box 1 of a voucher stream holds B
bytes of sealed reply. The costs below are exact for the field order above. h is a string's
CBOR header: 1, 2 or 3 bytes below 24, 256 and 65536 bytes.

| field or message                                  | bytes                                  |
|---------------------------------------------------|----------------------------------------|
| GroupChatMessage: `version`, `membership_hash`, `msg_type` | 70                            |
| `text` of n bytes                                 | 5 + h + n                              |
| `introduction`, name of n bytes                   | 174 + h + n                            |
| `file_upload`, payload n, type t, name b          | 39 + (h + n) + (h + t) + (h + b)       |
| `acks` of k members                               | 6 + h + naming + 8k; naming ≤ k        |
| `numbers` of m prefixes                           | 9 + h + 8m                             |
| `introduced_at`                                   | 121                                    |
| ReplyWho without rosters, places with names of n  | 14 + Σ (162 + h + n)                   |
| ReplyWho with rosters and p − 1 introductions, names of 10 | 236, 527, 1436, 3071 for p = 1, 2, 5, 10 |
| VoucherPayload, name of n bytes                   | 451 + h + n                            |
| sealed VoucherReply                               | WhoReply + 359                         |
| seal public key, X25519 ‖ CTIDH1024               | 160                                    |

With B = 1000: a text is at most 921 bytes; a control message acknowledges at most 113
members; a sealed reply holds a WhoReply of 641 bytes, three places without rosters or two
with. A group whose reply does not fit one box cannot admit a newcomer on that mesh, so B is
chosen with the group sizes wanted in mind.


## Reading

* Each member's stream from the position given: a box or a tombstone advances, NOT_FOUND waits
  with the backoff.
* `acks`, `numbers` and `introduced_at` let a reader jump and backfill, as the state machine
  does.
* Replicas keep two epochs; older boxes are recovered only through acknowledgements.


## Vectors

In `katzenpost/pigeonhole_protocols`: `testdata/katzenqt1/groupchat_wire_vectors.json`
(`messages`, `written`, `membership`, `replies`) and `testdata/katzenqt1/acks_vectors.json`.
BACAP and voucher vectors are in `katzenpost/hpqc`. katzenrns is a client of this protocol on
meshes: match the above, not its storage or interface.


## Encoding

CBOR maps have text keys; byte fields are byte strings. The voucher messages are canonical
CBOR.

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

* PleaseAdd: map `DisplayName` text, `MessageReadCap` 136 bytes.
* SignedPleaseAdd: map `PleaseAdd` the PleaseAdd's CBOR, `Signature` 64 bytes.
* VoucherPayload, box 0: map `SignedPleaseAdd` its CBOR, `VoucherPubKey` the seal public key.
* VoucherReply: map `WhoReply` the ReplyWho's CBOR, `VoucherSalt` 32 bytes. Sealed with the
  MKEM to the seal public key; the sealed bytes are the plaintext of box 1.
