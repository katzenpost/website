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

- **MessageStream** — Bob writes; group reads.
- **ReplyStream** — Alice seals; Bob reads.
- **VoucherStream** — the rendezvous; read+write derivable from `Voucher`.

## Stream Objects

- **MessageStream** — `.WriteCap` (Bob keeps), `.ReadCap` (travels in payload, inside `SignedPleaseAdd`).
- **ReplyStream** — `.rootSK` (Bob keeps), `.rootPK` (travels in payload).
- **VoucherStream** — read and write caps derivable by anyone holding the `Voucher`.

## Messages

- `SignedPleaseAdd` — Bob's signed self-introduction: a serialized `PleaseAdd` (his `DisplayName` and `MessageStream.ReadCap`) plus a signature over it produced by `MessageStream.WriteCap`.

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

- `WhoReply` := the existing members' read caps **each with its nonce** (see below), sealed to Bob.
- `Introduction` := `SignedPleaseAdd + VoucherSalt`, published to the group. The `VoucherSalt` is the nonce for Bob's stream's payloads.

```
VoucherPayload := SignedPleaseAdd || ReplyStream.rootPK
Voucher        := Hash(VoucherPayload)
```

## The VoucherSalt: the box-payload nonce

`VoucherSalt` is the **nonce** under which Bob's MessageStream box payloads are encrypted and decrypted. BACAP itself is used unchanged and on its default context: it supplies only the **box ID** and the **signature** (its `SignBox`/`VerifyBox` half), which address and authenticate the boxes. The payload is sealed under an AEAD whose nonce is the `VoucherSalt`, so opening a box needs that nonce in addition to the cap.

That is why the spec says **derive Bob's read capability from `VoucherPayload + VoucherSalt`**: neither half alone suffices. The published read cap lets you *locate and verify* Bob's boxes; the `VoucherSalt` is the nonce that lets you *open* them. Read = cap **and** nonce.

The nonce is the one secret a voucher snoop never receives. It is sealed to Bob inside the `VoucherReply` and handed to the existing members in the `Introduction`; it never appears in box 0. So an interceptor of the out-of-band `Voucher` can see that the voucher was spent, find Bob's boxes, and check their signatures, but cannot decrypt a single payload. That is exactly the spec's stated goal. (The salt is born at induction, not at mint: Bob does not know it when he writes box 0, so his `PleaseAdd` carries only his read cap, never the nonce.)

The nonce is therefore a **per-member** fact, not a global one: a mature group mixes voucher-joined members (whose payloads open under their own `VoucherSalt`) with seed members (on BACAP's default box nonce). Every shared read cap must travel **with** its nonce. In particular `WhoReply` carries, per member, the read cap **and** the nonce under which to open it, and the `Introduction` carries Bob's read cap together with his `VoucherSalt`.

## Steps

1. **Bob creates two streams.** He generates MessageStream and ReplyStream, keeping `MessageStream.WriteCap` and `ReplyStream.rootSK`.
2. **Bob builds the voucher.** He forms `SignedPleaseAdd = {DisplayName, MessageStream.ReadCap}` signed by `MessageStream.WriteCap`; sets `VoucherPayload := SignedPleaseAdd || ReplyStream.rootPK`; `Voucher := Hash(VoucherPayload)`.
3. **Bob publishes.** The `Voucher` derives VoucherStream; Bob writes `VoucherPayload` to box 0.
4. **Bob → Alice (OOB).** He hands over only the `Voucher`.
5. **Alice reads and verifies.** From `Voucher` she derives VoucherStream, reads box 0, checks `Hash(VoucherPayload) == Voucher`, and verifies the `SignedPleaseAdd` signature against its read cap's rootPK.
6. **Alice replies.** She picks `VoucherSalt`, seals `WhoReply + VoucherSalt` to `ReplyStream.rootPK`, and reads `MessageStream` by opening each box payload with `VoucherSalt` as the nonce.
7. **Alice commits (all-or-nothing COPY).** In one operation: write the sealed `WhoReply` to VoucherStream box 1; publish `Introduction` (`SignedPleaseAdd + VoucherSalt`) to her group; tombstone box 0 against reuse.
8. **Bob finishes.** He polls VoucherStream box 1, opens `WhoReply` with `ReplyStream.rootSK`, and recovers `VoucherSalt` (his own stream's payload nonce) along with the members' read caps and the nonce for each. Both now share the live streams, every stream's payloads opened under its own nonce.
