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

**Abstract**

katzenqt1 is the group chat protocol that katzenqt, hushphone and katzenrns speak. This document
is how a group chat app on a Reticulum mesh speaks it: what it writes, what it reads and what it
does with each, so that it shares groups with those clients, and with the mixnet through a
bridge. It assumes [Pigeonhole protocols over Reticulum](/docs/specs/pigeonhole-protocols-reticulum/)
for boxes, the [Group chat specification](/docs/specs/groupchat/) for the protocol's design,
rosters, acknowledgements, backfill, numbering, rewrite and disappearing messages, and the
[Contact voucher specification](/docs/specs/contactvoucher/). It restates a rule of those only
where the mesh changes it.


## A group

A group is a set of members, and each member is a BACAP stream that it alone writes. The group
has no stream of its own and no server: reading the group is reading every member's stream, and
saying something is writing the next box of one's own. A member's identity in the group is its
stream's key, the first 32 bytes of its read capability, and a member knows the others by their
read capabilities and the position in each from which it reads. Membership changes travel as
introductions written in members' streams, and the membership hash in every box says which set
of members its writer believed in.

A newcomer gets in through a voucher. The newcomer mints it and hands its code to someone, and a
member who holds the code answers it with the group. How the code travels is not the protocol's:
it is pasted into another member's client, read aloud, or routed to a pigeonhole service that
invites into its group.

On the mixnet a member writes some boxes through a temporary stream and a copy command, so that a
courier sees one action. The mesh has no courier and no copy command, and a mesh client writes
every box directly to its entry replica, in the order given below. Readers on both networks see
the same streams.


## Vouchers

A voucher is 32 bytes, shown and carried as standard base64. It is the hash of what the newcomer
publishes, so whoever holds it can find that and check it; and it seeds the voucher stream, the
rendezvous both sides derive from it alone: the 32 byte voucher seeds SHAKE256, which supplies in
turn the stream's Ed25519 seed, 32 bytes, its KDF state, 32 bytes, and its first counter, 16
bytes, as a fresh stream is made. Box 0 of that stream is the capability's first position, box 1
the next.

The newcomer:

1. Makes a stream of its own: the stream it will write the group in.
2. Makes a seal keypair, a hybrid NIKE of X25519 and CTIDH1024 in that order, used as an MKEM.
3. Writes a PleaseAdd with its display name and its stream's read capability, signs it with the
   stream's root key, a plain Ed25519 signature over the PleaseAdd bytes, and puts the
   SignedPleaseAdd and the seal public key in a VoucherPayload. The voucher is the SHA-256 of the
   VoucherPayload.
4. Derives the voucher stream and writes the VoucherPayload to box 0. The group now shows as
   joining, with the voucher's code to give away.
5. Polls box 1. NOT_FOUND is not yet. TOMBSTONE means the voucher was withdrawn and the join
   failed. A box is the sealed reply: the newcomer opens it with its seal secret key, which gives
   a VoucherReply, a WhoReply and a 32 byte salt. It mutates its own stream's write capability by
   the salt, by the BACAP KDF state mutation, and writes the group in that mutated stream from
   its first position. The WhoReply is the ReplyWho below, and from it the newcomer knows every
   member and where to start reading each.

A member answering the code:

1. Derives the voucher stream and reads box 0. NOT_FOUND is not yet. TOMBSTONE means withdrawn.
2. Checks that the VoucherPayload hashes to the voucher and that the signature verifies under
   the root key in the read capability it carries. If either fails the voucher is not answered.
3. Composes the ReplyWho: every member, each with the position the newcomer starts reading from,
   its own stream at the position its Introduction of the newcomer will occupy. It chooses a 32
   byte salt, mutates the newcomer's read capability by it, which is the capability the group
   will read the newcomer at, and seals the VoucherReply, WhoReply and salt, to the seal public
   key from box 0.
4. Writes the Introduction of the newcomer, its display name and mutated read capability, to its
   own stream at the position the reply names, ahead of anything else it has queued.
5. Writes the sealed reply to box 1, trying again until a replica holds it. ALREADY_EXISTS
   means another member answered first; this one stops.
6. Reads the newcomer at the mutated read capability from its first position.

Box 0 stays as written: the voucher is spent once box 1 exists. A member answers one voucher at
a time, and refuses a second code until the first is done.


## ReplyWho

A ReplyWho is a CBOR map. `please_adds` lists the group's places in order: each is a map of
`display_name` and `read_cap`, the member's key followed by the position the newcomer reads it
from, or null for a place whose member the sender does not know. `rosters` gives, per place, that
member's roster as pairs of roster index and place, or null where unknown; `introductions` lists
who introduced whom and at which position, as `[by, index, member]`; `introducer` is the sender's
place and `newcomer` the newcomer's, which is the number of places. The Group chat specification
says how rosters and introductions are used.

A reply without `rosters` is valid: the newcomer takes the members named, the first as
introducer, with every roster unknown, and learns the rosters as it reads. A reply with rosters
is refused, and the join fails, when `newcomer` is not the number of places, when `introducer`
is not below it, when there are 256 places or more, when two places name one key, when a roster
names a place that does not exist, or when the introducer's place is null.

A pigeonhole service that admits a client answers with a ReplyWho of one place and no rosters:
to the newcomer it is a group of one member.


## What a member writes

A member's box holds one byte, `F`, and the CBOR of a GroupChatMessage. An empty plaintext is a
tombstone: the message was deleted, and readers step past it. A message that does not fit the
box size, less its one framing byte, is written to a stream of its own: its chunks as `C` boxes,
the last as an `F` box, and the member's own stream gets an `I` box, the number of chunks as 4
big endian bytes followed by the chunk stream's 136 byte read capability, or that read
capability alone. A reader that does not fetch the chunks steps past the `I` box.

A GroupChatMessage carries `version`, 3; `membership_hash`; `msg_type`; and the fields of its
type. The types are 0 text, with `text`; 1 introduction, with `introduction`, a map of
`display_name` and `read_cap`; 2 file upload, with `file_upload`; 3 who, with `who`; 4 reply who,
with `reply_who`; and 10 control, which carries only the acknowledgement fields. A reader accepts
any version up to 3 and refuses a type above 10. Any message may also carry `acks`, `numbers` and
`introduced_at`, byte strings whose layouts are below and whose rules are the Group chat
specification's acknowledgements, numbering and introductions. A message without `msg_type` is
typed by the field it carries, text when none.

The membership hash is SHA-256 over the string `KP:membership:v1` followed by the members' keys,
each once, in byte order; a member's own key counts. The all zero hash is the sentinel for a
membership not yet known; readers also accept the older sentinel, 32 bytes of `TODO` repeated.
Content messages carry the hash as their writer's claim; control messages and introductions
carry it as the writer's current membership, and the sentinel when it has none.

A display name, in an Introduction as in a PleaseAdd, is 1 to 30 characters. What of it a client
shows, and how it tells two members with one name apart, is the client's own.


## Reading members

A member reads every other member's stream from the position it was given, one box at a time: a
box or a tombstone advances to the next position, NOT_FOUND waits with a backoff. The
acknowledgements, numbers and introduced_at a message carries let a reader that was away jump
ahead and backfill, as the Group chat specification describes, and its retention and backfill
are timed by the replica epoch of Pigeonhole protocols over Reticulum. Boxes older than two
epochs are gone from the replicas, so a member that was away longer reads what the
acknowledgements let it recover.


## Interoperating with katzenrns

katzenrns is the group chat client on Reticulum meshes today, and its behaviour on the wire is
this document. A second client must match everything above and nothing of katzenrns's own: its
state directory, its names for members, its text filtering and its interface are not the
protocol. The vectors to check against are `testdata/katzenqt1/groupchat_wire_vectors.json`
(messages, written boxes, membership hashes, replies) and `testdata/katzenqt1/acks_vectors.json`
in `pigeonhole_protocols`, and the BACAP and voucher vectors in `hpqc`. The live check is a
group with one member on each client, joined through a voucher in each direction, with text
read on both sides.


## Encoding

CBOR maps are written with text keys. Byte fields are CBOR byte strings. The voucher messages
are written in canonical CBOR.

### GroupChatMessage

| key               | value                                                  |
|-------------------|--------------------------------------------------------|
| `version`         | integer, 3                                             |
| `membership_hash` | 32 bytes                                               |
| `msg_type`        | integer: 0, 1, 2, 3, 4 or 10                           |
| `text`            | text; type 0                                           |
| `introduction`    | map `display_name` text, `read_cap` 136 bytes; type 1  |
| `file_upload`     | map `payload` bytes, `filetype` text, `basename` text; type 2 |
| `who`             | type 3                                                 |
| `reply_who`       | type 4                                                 |
| `tally`           | kept and rewritten as read                             |
| `acks`            | bytes, layout below; optional                          |
| `numbers`         | bytes, layout below; optional                          |
| `introduced_at`   | bytes, layout below; optional                          |

### Framing

The first byte of a box's plaintext: `F` a whole message or the last chunk of one, `C` a chunk,
`I` an indirection. An `I` box is `I`, a 4 byte big endian chunk count and a 136 byte read
capability, or `I` and the read capability. An empty plaintext is a tombstone.

### Acks

Empty when nothing is acknowledged. Otherwise:

* one byte, the number of members acknowledged, less one,
* the members, by roster index in the sender's roster, in ascending order: as a list of one
  byte each when that is no longer than a bitmap, else as a bitmap, most significant bit first,
  as many bytes as the highest index needs,
* one 8 byte little endian counter per member, in the same order: the counter of the
  acknowledged box.

A reader takes the naming as a list when it is as long as the count, as a bitmap when shorter,
and refuses a list out of order, a bitmap ending in a zero byte or one naming a different
number of members than the count.

### Numbers

* one byte, the first roster index assigned,
* an 8 byte key prefix per member numbered, one per consecutive index.

A single byte is the roster index of the member an Introduction in the same message introduces.
A reader refuses the field when the indexes would pass 255 or a prefix repeats.

### IntroducedAt

* one byte, the introducer's roster index in the sender's roster,
* the 104 byte position of the Introduction in the introducer's stream.

### ReplyWho

| key             | value                                                                 |
|-----------------|-----------------------------------------------------------------------|
| `please_adds`   | array of map `display_name` text, `read_cap` 136 bytes; or null       |
| `rosters`       | array, one per place, of arrays of `[index, place or null]`; or null; absent when unknown |
| `introductions` | array of `[by, index 104 bytes, member]`                              |
| `introducer`    | integer                                                               |
| `newcomer`      | integer                                                               |

### Voucher stream

Box 0 is the first position of the capability derived from the voucher, box 1 the next.

* PleaseAdd: map `DisplayName` text, `MessageReadCap` 136 bytes.
* SignedPleaseAdd: map `PleaseAdd` the PleaseAdd's CBOR, `Signature` 64 bytes.
* VoucherPayload, box 0: map `SignedPleaseAdd` its CBOR, `VoucherPubKey` the seal public key.
* Voucher: SHA-256 of the VoucherPayload's bytes.
* VoucherReply: map `WhoReply` the ReplyWho's CBOR, `VoucherSalt` 32 bytes; sealed with the MKEM
  to the seal public key, and the sealed bytes are the plaintext of box 1.
