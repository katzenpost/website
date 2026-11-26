---
title: "Formalizing Sphinx in Lean, Part II: Tail Indistinguishability and Layer Unlinkability"
date: "2026-11-22"
description: "Lean proofs of tail indistinguishability and of layer unlinkability at a mix with a replay cache, for KEM Sphinx, and what payload tagging leaves of the second."
author: "David Stainton"
tags: ["sphinx", "lean", "cryptlib", "formalization", "formal methods"]
version: ""
draft: false
---

[Part I](/blog/2026/10/31/formalizing-sphinx-in-lean/) ended with a plan. The four security
properties of the 2009 Sphinx paper do not imply secure onion routing, so cryptlib's security
statements should move to the two properties that do, layer unlinkability and tail
indistinguishability, and they should be about each instance's own `wrap` and `unwrap`, as the
correctness field already is.

This post reports that work for KEM Sphinx. Tail indistinguishability is proved in the game of
the paper. Layer unlinkability is proved in a narrower game than the paper's, and one part of the
paper's game is false for Sphinx as we build it; I say below which part and why. Everything is
proved about the code that builds and unwraps real packets, the same code that is checked
against the test vectors shared with the Katzenpost Go implementation. The last section before
the caveats is about replies, which that paper does not have.

The definitions are from
[Breaking and (Partially) Fixing Provably Secure Onion Routing](https://arxiv.org/pdf/1910.13772)
by Kuhn, Beck and Strufe. In both games the adversary controls every node but one honest relay.


## The forwarded packet is a fresh packet

A proof of tail indistinguishability has to show that what the honest hop forwards carries no
trace of the hops before it. For KEM Sphinx this is an exact statement, with no probability in
it: the packet the first hop forwards *is* the packet that the sender's own function builds on
the rest of the path. Here it is, abridged; the full statement is in
[KEMSphinxTail.lean](https://github.com/katzenpost/cryptlib/blob/main/Cryptlib/Protocols/Sphinx/KEMSphinxTail.lean).

```lean
theorem newKEMPacket_unwrapKEM
    -- ... the primitives, the geometry, and well-formedness hypotheses ...
    (hnk : newKEMPacket kem cipher macS kdfS streamS geom seeds filler path payload
      = Except.ok pkt) :
    (2 ≤ path.size →
      ∃ (replayTag mac : Vector UInt8 32) (fwd : Vector UInt8 pkt.size),
        unwrapKEM kem cipher macS kdfS streamS geom privKey pkt
          = Except.ok (none, replayTag,
              (path[0]!).commands ++ [RoutingCommand.nextNodeHop (path[1]!).id mac], some fwd) ∧
        newKEMPacket kem cipher macS kdfS streamS geom (seeds.extract 1 seeds.size)
            (tailFiller kem kdfS streamS geom path seeds filler) (path.extract 1 path.size) payload
          = Except.ok (ofVector fwd)) ∧
    (path.size = 1 → ...)
```

`newKEMPacket` builds a packet from one seed per hop, the random filler for the unused
routing-info slots, the path and the payload. When the first hop unwraps that packet, the packet
it forwards is `newKEMPacket` again, on the path without its first hop, from the seeds without
the first seed, and with a different filler. The second half of the statement is for the only
hop of a one-hop path, which gets its commands and the payload.

That filler is the whole of the difference. It is the old filler followed by one more block,
since a path one hop shorter leaves one more slot unused. The new block is the XOR of one block
of header keystream from every hop of the path. The first hop's contribution is the last block
of its keystream, which is one block longer than the routing info. That block masks nothing in
the packet the first hop receives. Its only use is to hide, in the forwarded packet, everything
the earlier keystreams left behind.

`chainForward_eq` extends this to any number of hops: after `j` hops the forwarded packet is
`newKEMPacket` on the remaining path, with `j` extra filler blocks.

`KEMSphinxScheme` carries the one-hop fact as a field, `unwrap_tail`, stated about the scheme's
own `wrap` and `unwrap`. Unlike the `integrity` and `indistinguishable` fields that Part I was
candid about, a `KEMSphinxScheme` cannot be constructed without proving it.


## Tail indistinguishability

In the paper's game (Definition 6) the adversary is given the honest relay's public key and may
have the relay process packets of its choice, before and after the challenge. It chooses a
message and a path through the honest relay. It is then given either the onion layer that the
honest relay forwards, or the same layer of a second onion that shares the rest of the path and
carries the same message. It must say which.

`ti6Advantage_le` bounds the adversary's advantage in that game, with the honest relay at any
position but the last. The terms of the bound are:

- the KEM, in a game with a decapsulation oracle where the adversary is given a key and never
  the ciphertext;
- the KDF, as a generator on a uniform shared secret;
- the stream cipher, as a generator of the header keystream;
- the probability of the draws the exact theorems do not cover: a seed for which the KEM may
  fail to decapsulate, or a packet that cannot be built.

Nothing is assumed of the KEM beyond its own type, which has a predicate for the states from
which a round trip is guaranteed. The same proof covers a KEM that never fails and ML-KEM, which
fails with small probability. No MAC assumption appears, because in this game the adversary
never sees the packet entering the honest relay.


## Payload tagging

Layer unlinkability is about the packet entering the honest relay and the packet leaving it. In
the paper's game (Definition 7) the adversary sees both, and may have the relay process any
packet but the challenge itself.

Sphinx checks a MAC over the header at every hop. The payload is checked once, at the final hop:
the hop decrypts it and looks for a tag of zero bytes at the front of the plaintext. So an
adversary can take the challenge packet, change its payload, and ask the relay to process the
copy. The header MAC still verifies and the relay forwards it. `procWith_payload_congr` states
this about our code:

```lean
theorem procWith_payload_congr (dec : ByteArray → Except String ByteArray) (pkt pkt' : ByteArray)
    (hsz : pkt'.size = pkt.size)
    (hhdr : pkt'.extract 0 (payloadOffset kem geom) = pkt.extract 0 (payloadOffset kem geom))
    (h : procWith kem cipher macS kdfS streamS geom dec pkt = some (none, tag, cmds, some fwd)) :
    ∃ fwd', procWith kem cipher macS kdfS streamS geom dec pkt' = some (none, tag, cmds, some fwd')
      ∧ fwd'.extract 0 (payloadOffset kem geom) = fwd.extract 0 (payloadOffset kem geom)
```

The copy comes out with the same forwarded header as the original, and that links the packet
entering to the packet leaving. The paper says as much: Sphinx with integrity on the header only
does not meet its definition, and its own proof is for a variant that authenticates the payload
at every hop.

Two things limit what this attack gives.

The first is the replay cache. The replay tag is a hash of the KEM ciphertext in the header, so
the original and the copy have the same tag, and a mix that has processed one refuses the other.
The cache is not part of the packet format. `unwrapKEM` returns the tag and keeps no state. In
the games below it is a rule of the oracle.

The second is the tag at the final hop. An adversary who changes the one packet in flight, with
no copy, is not stopped by any mix. `procWith_payload_changed` says the change survives each
hop: the forwarded packets have the same header and different payloads. `tagGame_le` then bounds
the chance that the honest final hop accepts such a packet. The terms are the KEM, the KDF, and
a game about the payload cipher alone, in which the adversary must produce a second ciphertext
that decrypts to a zero tag.

Together these say what payload tagging is in Sphinx: a channel of one bit per packet. The
final hop learns that a payload was altered or that it was not. The wide-block cipher is what
keeps it to one bit, since any change to the ciphertext scrambles the whole plaintext, and the
adversary cannot plant a mark that survives. To read the bit the adversary needs the final hop's
key. In Katzenpost the final hop is a service node.


## Layer unlinkability with a replay cache

`luAdvantage_le` is the positive result. The adversary is given the packet entering the honest
mix and the packet the mix forwards. After the challenge, the mix's oracle refuses any packet
that carries the challenge's KEM ciphertext, as a replay cache would. The theorem bounds the
adversary's advantage in telling that pair from a pair with nothing in common: a packet to the
mix whose routing info and payload are uniform, and a fresh packet on the rest of the path,
built from its own seeds and filler.

The terms of the bound are:

- the KEM, in the game with a decapsulation oracle that refuses the challenge ciphertext;
- the KDF, as a generator of the hop's four keys;
- the payload cipher, on one encryption under a uniform key;
- the stream cipher, as a generator of the header keystream;
- the probability of the bad draws, as before.

Again no MAC assumption appears. The oracle refuses the only KEM ciphertext the hop's MAC key
belongs to.

The proof rests on a second exact theorem, `newKEMPacket_layer`: the packet entering a mix is
one layer around the packet it forwards. The layer uses the mix's KEM ciphertext, its payload
key and IV, its MAC key, and the part of its header keystream that masks the routing info.
Everything else in it is read off the forwarded packet. With uniform keys the keystream is a
one-time pad on the routing info, and its last block does for the forwarded packet what it did
in the tail proof.


## Replies

The 2020 paper has no replies. A later paper from the same group,
[Provable Security for the Onion Routing and Mix Network Packet Format Sphinx](https://arxiv.org/abs/2312.08028)
by Scherer, Weis and Strufe, defines a scheme that has them, and in which the last relay
delivers to a receiver outside the network, as a Katzenpost service node does. It gives three
properties for that scheme: layer unlinkability on the forward path that allows for the tagging
above, layer unlinkability on the backward path, and tail indistinguishability over both.

cryptlib now has that scheme and its three games, in
[RSOR.lean](https://github.com/katzenpost/cryptlib/blob/main/Cryptlib/Protocols/RSOR.lean). The
paper's correctness conditions are fields of the scheme's type, so an instance cannot be given
without proving them.

KEM Sphinx is an instance, `scheme` in
[KEMSphinxRSOR.lean](https://github.com/katzenpost/cryptlib/blob/main/Cryptlib/Protocols/Sphinx/KEMSphinxRSOR.lean).
Its algorithms are `newKEMPacket` and `unwrapKEM` on the forward path, and `newKEMSURB`,
`newPacketFromSURB` and `decryptSURBPayload` for the reply. The four laws say:

- a relay on the forward path gets the next relay's name and the next layer, and the exit relay
  gets the message and the receiver;
- the exit relay's reply, built from the SURB it finds in the payload, is the first layer of the
  reply;
- a relay on the backward path gets the next layer of the reply;
- the last relay of the backward path gets a payload that the sender opens to the reply.

A reply's header is the header of a forward packet on the backward path. Its payload starts as
the message under the SURB's key, and each relay decrypts it once more under its own key. The
sender undoes this by encrypting under the relays' keys in reverse order. That needs encryption
to invert decryption, and the cipher's type states only that decryption inverts encryption. The
other direction follows from it: on blocks of one size, encryption is an injection of a finite
set into itself.

The laws hold for the sender's draws from which every layer can be built and no KEM round trip
fails.


## What is not proved

- **The three properties of the 2024 paper are stated and not proved.** For KEM Sphinx only
  correctness is proved. The tail and layer results above are in the games of the 2020 paper.
  The 2024 games as stated here differ from the paper's in three ways, listed at the top of
  `RSOR.lean`.

- **Layer unlinkability is narrower than Definition 7.** The honest mix is the first hop of the
  packet the adversary sees, and the rest of the path and the message are fixed, not chosen by
  the adversary. The statement compares the real pair with an ideal pair. The paper compares it
  with the pair from a replacement onion; that form would follow from this one and the tail
  theorem, and I have not written it.
- **The replay cache is an assumption about the mix.** The theorem is about the format together
  with an oracle that refuses a repeated KEM ciphertext. Without that rule the property is false,
  as above.
- **The KEM games are ours.** One gives the adversary the challenge ciphertext and an oracle that
  refuses it, which is the standard shape. The other, in the tail proof, withholds the
  ciphertext and refuses nothing. Neither is yet reduced to VCVio's `IND_CCA_Game`.
- **The symmetric primitives are named assumptions.** The KDF and the stream cipher are assumed
  to be generators. The payload cipher is assumed to hide one encryption, and to make a second
  ciphertext with a zero tag hard to find. Both follow from a strong pseudorandom permutation,
  and those reductions are not written.
- **The tag game is about the last layer**, and about forward packets. The last relay of a
  reply's path does not check the payload. The sender does, and no game here covers that.
- **The bad-draw terms are loose.** They count every seed as a possible KEM failure, and they
  count a packet that cannot be built.
- **NIKE Sphinx** is not started. Its header carries a blinded group element in place of a
  ciphertext per hop, so the forwarded packet need not be the output of `wrap` from any state,
  and the statements may have to change.
- The `integrity` and `indistinguishable` fields of the 2009 framework are still in the `Sphinx`
  type, as Part I left them.

As in Part I, a model is only as good as its statement. The exact theorems are about the code,
so there is little room for them to mean something other than they say. The games are mine, and
they are where a reader should look hardest.


## What's next

The bounds for the three games of the 2024 paper, for KEM Sphinx. They take the place of the
narrower layer unlinkability result here. Then NIKE Sphinx, and the reductions to VCVio's own
KEM game. Review is welcome, as before.
