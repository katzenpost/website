---
title: "Contact Voucher Protocol Narration"
linkTitle: "Contact Voucher Protocol Narration"
description: ""
author: "David Stainton"
url: ""
date: "2026-06-02T00:00:00Z"
draft: "false"
slug: "contact_voucher_narration"
layout: ""
type: ""
weight: "1"
version: "0"
---

## Introduction

The [voucher spec](../contact_voucher/) was very difficult for me to read and it overloads variable names and doesn't make certain facts explicit enough. I wrote this spec for my own understanding of the design as an implementation guide for myself.

## Streams

There is no separate reply stream. Alice replies on the very same stream Bob used to mint the voucher.

- **MessageStream**: Bob writes; the group reads. This is the stream whose live messages the protocol must protect.
- **VoucherStream**: the rendezvous, derived entirely from the `Voucher`. Box 0 holds Bob's `VoucherPayload`; box 1 holds Alice's `VoucherReply`.
- **the group's other streams**: each existing member has their own MessageStream, just like Bob's.

## Stream Objects

- **MessageStream**: `.WriteCap` (Bob keeps), `.ReadCap` (travels in `VoucherPayload`, inside `SignedPleaseAdd`).
- **VoucherStream**: read and write caps derivable by anyone holding the `Voucher`.
- **VoucherKeypair**: `VoucherSecretKey` (Bob keeps), `VoucherPublicKey` (travels in `VoucherPayload`). This is the MKEM keypair under which Alice seals the reply to Bob.

## Messages

- `SignedPleaseAdd` is Bob's signed self-introduction: a serialized `PleaseAdd` (his `DisplayName` and `MessageStream.ReadCap`) plus a signature over it produced by `MessageStream.WriteCap`.

```go
// PleaseAdd is a member's request to join, carrying their display name
// and the read cap that lets others read their messages.
type PleaseAdd struct {
    // DisplayName is the party's name to be displayed in chat clients.
    DisplayName string

    // UniversalReadCap is the BACAP read cap for this member's
    // MessageStream, letting others read all messages posted by them.
    UniversalReadCap *bacap.UniversalReadCap
}

// SignedPleaseAdd binds a PleaseAdd to a signature made by the member's
// write cap, so any party can verify the name-and-cap binding.
type SignedPleaseAdd struct {
    // PleaseAdd contains the CBOR serialized PleaseAdd struct.
    PleaseAdd []byte

    // Signature contains the cryptographic signature over the PleaseAdd field.
    Signature []byte
}
```

- `WhoReply` := the existing members' MessageStream read caps (one or more), so Bob can read everyone already in the group.
- `VoucherReply` := `WhoReply || VoucherSalt`, MKEM-sealed to `VoucherPublicKey` and written to VoucherStream box 1. Box 1 is an ordinary BACAP box, so the payload is BACAP-encrypted as a stream box and then additionally MKEM-encrypted to Bob's `VoucherPublicKey`; only Bob, holding `VoucherSecretKey`, can open it.
- `Introduction` := Bob's display name together with his salt-mutated MessageStream read cap, published to the existing group so the members can read Bob. The group receives the mutated cap directly and never the salt.

```
VoucherPayload := SignedPleaseAdd || VoucherPublicKey
Voucher        := Hash(VoucherPayload)
```

## The VoucherSalt: re-seeding the MessageStream

`VoucherSalt` is the heart of the protocol. It is **not** a nonce and it does **not** modify BACAP. It is a value that **replaces the KDF state** inside a MessageStream's `MessageBoxIndex`, which re-seeds the index chain and so moves the stream to a fresh, unpredictable sequence of box IDs. Only two parties ever touch it. Bob mutates his `MessageStream.WriteCap` by the salt and writes his real messages at the mutated position. Alice mutates Bob's matching `MessageStream.ReadCap` by the same salt **once**, before she shares it, so writer and readers meet at the mutated position. The group never learns the salt; it only ever receives the already-mutated read cap.

That is why the spec says **derive Bob's read capability from `VoucherPayload + VoucherSalt`**: the read cap published in box 0 is only half of it. That derivation is Alice's alone. The read cap in box 0 names Bob's *original* stream; the salt re-seeds it to where Bob's real messages actually go. She performs the derivation once and hands the result to the group.

The salt is the one secret a voucher snoop never receives. It is born at induction, not at mint: Alice mints it and seals it inside the MKEM-encrypted `VoucherReply`. It is never written to box 0, so Bob's `PleaseAdd` carries only his original read cap, never the salt. An interceptor of the out-of-band `Voucher` can derive the VoucherStream, read box 0, and check that the voucher was spent, but he holds only the un-mutated read cap. He cannot compute the salt-mutated box IDs, so he cannot read a single one of Bob's actual messages. That is exactly the spec's stated confidentiality goal.

Because the salt re-seeds rather than decorates the stream, it is a **per-member** fact known only to that member and to whoever inducted them. A mature group mixes voucher-joined members (each on their own salt-mutated index) with seed members (on the unmutated index), and no member needs to carry any salt: every read cap that circulates is already at its live, mutated position. `WhoReply` hands Bob the existing members' live read caps directly, and the `Introduction` hands the group Bob's read cap after Alice has applied his salt.

## Steps

1. **Bob mints.** He generates his MessageStream (keeping `MessageStream.WriteCap`) and a `VoucherKeypair` (keeping `VoucherSecretKey`). He forms `SignedPleaseAdd = {DisplayName, MessageStream.ReadCap}` signed by `MessageStream.WriteCap`; sets `VoucherPayload := SignedPleaseAdd || VoucherPublicKey`; `Voucher := Hash(VoucherPayload)`.
2. **Bob publishes.** The `Voucher` derives the VoucherStream; Bob writes `VoucherPayload` to box 0.
3. **Bob → Alice (OOB).** He hands over only the `Voucher`.
4. **Alice reads and verifies.** From `Voucher` she derives the VoucherStream, reads box 0, checks `Hash(VoucherPayload) == Voucher`, and verifies the `SignedPleaseAdd` signature against its read cap's rootPK.
5. **Alice replies.** She mints `VoucherSalt`, assembles `WhoReply` from the existing members' live read caps, forms `VoucherReply := WhoReply || VoucherSalt`, and MKEM-seals it to `VoucherPublicKey`.
6. **Alice commits (all-or-nothing COPY).** She first mutates Bob's published read cap by the `VoucherSalt`. Then, in one operation: write the sealed `VoucherReply` to VoucherStream box 1; publish the `Introduction` (Bob's display name and his salt-mutated read cap) to her group, which never sees the salt itself; tombstone box 0 against reuse.
7. **Bob finishes.** He polls VoucherStream box 1, MKEM-opens the `VoucherReply` with `VoucherSecretKey`, and recovers `WhoReply` and `VoucherSalt`. He mutates his `MessageStream.WriteCap` by the salt and begins writing real messages there. The group already holds his mutated read cap, so they read him without ever learning the salt. Both sides now share the live streams.
