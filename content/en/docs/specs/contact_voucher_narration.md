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

- `WhoReply` := the existing members' read caps, sealed to Bob.
- `Introduction` := `SignedPleaseAdd + VoucherSalt`, published to the group.

```
VoucherPayload := SignedPleaseAdd || ReplyStream.rootPK
Voucher        := Hash(VoucherPayload)
```

## Steps

1. **Bob creates two streams.** He generates MessageStream and ReplyStream, keeping `MessageStream.WriteCap` and `ReplyStream.rootSK`.
2. **Bob builds the voucher.** He forms `SignedPleaseAdd = {DisplayName, MessageStream.ReadCap}` signed by `MessageStream.WriteCap`; sets `VoucherPayload := SignedPleaseAdd || ReplyStream.rootPK`; `Voucher := Hash(VoucherPayload)`.
3. **Bob publishes.** The `Voucher` derives VoucherStream; Bob writes `VoucherPayload` to box 0.
4. **Bob → Alice (OOB).** He hands over only the `Voucher`.
5. **Alice reads and verifies.** From `Voucher` she derives VoucherStream, reads box 0, checks `Hash(VoucherPayload) == Voucher`, and verifies the `SignedPleaseAdd` signature against its read cap's rootPK.
6. **Alice replies.** She picks `VoucherSalt`, seals `WhoReply + VoucherSalt` to `ReplyStream.rootPK`, and begins reading `MessageStream` under `ctx = VoucherSalt`.
7. **Alice commits (all-or-nothing COPY).** In one operation: write the sealed `WhoReply` to VoucherStream box 1; publish `Introduction` (`SignedPleaseAdd + VoucherSalt`) to her group; tombstone box 0 against reuse.
8. **Bob finishes.** He polls VoucherStream box 1, opens `WhoReply` with `ReplyStream.rootSK`, and recovers `VoucherSalt` (the `ctx`) and the members' read caps. Both now share the live, salted streams.
