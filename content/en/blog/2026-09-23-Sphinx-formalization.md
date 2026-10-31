---
title: "Formalizing Sphinx in Lean"
date: "2026-09-23"
description: "A Lean formalization of the Sphinx packet format, generic over its cryptographic primitives, and what it does and doesn't prove."
author: "David Stainton"
tags: ["sphinx", "lean", "formalization", "formal methods"]
version: ""
draft: false
---

In Lean, a field of a structure type can be a proposition. That one feature changes how a cryptography library can be written.

In a language like Rust a trait is an empty husk that only declares function signatures. It's still a useful contract: all
instances must define the trait's methods. In Lean we describe a primitive generically with a structure whose fields hold
functions and data types, which is how Rust or Go would do it too. Dependent types let us go a step further: a field can
also be a proposition about the other fields. Here is cryptlib's NIKE (non-interactive key exchange) type, abridged:

```lean
structure NIKE where
  PrivateKey   : Type
  PublicKey    : Type
  SharedSecret : Type
  -- ...
  Safe : PublicKey → Prop
  derivePublicKey : PrivateKey → PublicKey
  groupAction : PrivateKey → {pk : PublicKey // Safe pk} → SharedSecret
  -- ...
  derive_safe : ∀ sk, Safe (derivePublicKey sk)
  -- ...
  commutes : ∀ sk₁ sk₂,
    groupAction sk₁ ⟨derivePublicKey sk₂, derive_safe sk₂⟩
      = groupAction sk₂ ⟨derivePublicKey sk₁, derive_safe sk₁⟩
```

Every NIKE instance must supply a proof of `commutes`, so a NIKE whose group operation is not commutative cannot be
constructed. The KEM (key encapsulation mechanism) type likewise carries its round trip correctness as a field.
And these proofs compose: when the hashed ElGamal NIKE-to-KEM adapter builds a KEM from a NIKE, it cannot construct
the KEM without filling in that correctness field, which it does using the NIKE's `commutes`. The theorem "a lawful NIKE
gives a lawful KEM" never has to be stated separately, and nobody can forget to apply it.

This post is about taking that idea up a level, from primitives to a protocol. I recently used Claude Code to formalize
the Sphinx packet format in Lean, generic over its NIKE or KEM, stream cipher, KDF, MAC and wide-block cipher.
Correctness is proved once over any choice of those primitives, and a padding leak that later researchers found in
Sphinx becomes impossible to express in the type. The security proofs are the harder part, and I'll be honest below about
what is and isn't proved yet. Links for background on Sphinx are collected at the end.

* https://cryptlib.io
* https://github.com/katzenpost/cryptlib


## Background: Katzenpost's Sphinx and HPQC

The Katzenpost mixnet uses a [Go implementation of Sphinx](https://github.com/katzenpost/katzenpost/tree/main/core/sphinx)
that is generic over a NIKE, plus a KEM Sphinx variant that is generic over a KEM. Both can be hybrid post quantum.
The NIKE and KEM interfaces come from [HPQC](https://github.com/katzenpost/hpqc), our hybrid post quantum cryptography
library, which also provides a NIKE combiner, a KEM combiner, and a NIKE to KEM adapter (hashed ElGamal construction),
so that for example X25519 can be combined with ML-KEM into a hybrid KEM. cryptlib started as a Lean model of HPQC.


## How cryptlib got here

A couple of years ago I started the Lean theorem prover meetup at the Noisebridge hacker space in San Francisco, a weekly
study group with some very smart attendees. On the Lean Zulip I ended up chatting with Mario Carneiro about program
verification and modeling cryptography in Lean, and at some point he posted
[a minimal KEM type](https://leanprover.zulipchat.com/#narrow/channel/236449-Program-verification/topic/Lean.20library.20rust.20integration.3F/near/452695059)
whose struct contains a proposition field with the KEM completeness theorem: everything the KEM encapsulates can be
decapsulated.

At the time I didn't want yet another symbolic modeler for cryptography. I was already using Proverif, which works great
and automates finding security flaws, and a Lean model would have none of that automation. I didn't yet understand that
what Mario was showing me is much more than a symbolic model.

So I wrote Lean implementations of a few HPQC constructions: the NIKE to KEM adapter, the NIKE combiner, the KEM combiner.
About two years later, at the Utrecht University Summer Lean Theorem Prover class, I came back to them and wrote theorems
the conventional way, as separate statements:

* A NIKE is lawful if its group operation is commutative.
* A KEM is lawful if it can decapsulate everything it encapsulates.
* Given a lawful NIKE, the NIKE to KEM adapter produces a lawful KEM.

Then I realized that the first two belong inside the types, as the `commutes` and completeness fields shown in the
introduction, and that the third then disappears: the adapter cannot construct its KEM without proving completeness
from the NIKE's `commutes`. Those proposition fields are proof obligations for every instance, which is the point.
Only valid instances can be expressed at all.


## From primitives to Sphinx

I asked Claude Code to write a Sphinx implementation in Lean, verified against test vectors shared with the Katzenpost
Sphinx implementation. The formalization went through roughly four phases:

1. Implement Sphinx as a static construction with specific primitives.
2. Try to prove the Sphinx paper's security properties, and fail: the proofs drown in the complexity of the individual
   primitives.
3. Rewrite Sphinx over generic dependent types for each primitive in the construction: NIKE/KEM, stream cipher, KDF,
   MAC, wide-block cipher.
4. Try again: correctness is now proved outright, over any NIKE or KEM and any choice of the other primitives. The
   other three properties are formalized, with the steps that aren't proved yet isolated as explicit hypotheses.

The composition benefit from the introduction showed up at protocol scale as a reduction in proof obligations. Proving
anything about the static construction with, say, the AEZ wide-block cipher meant also reasoning about AEZ. With a
generic wide-block cipher type whose struct carries an encryption/decryption completeness proposition, the Sphinx
proofs only need that one proposition and never look inside AEZ.


## Sphinx Security Properties

Section 4 of the Sphinx paper frames Sphinx's security in terms of four properties. The first three come from
Camenisch and Lysyanskaya's formal treatment of onion routing, and in section 4.4 the paper proves their fourth
property, "security", together with Sphinx's own requirement that forward and reply messages be indistinguishable:

1. correctness
2. integrity
3. wrap-resistance
4. security, and indistinguishability of forward and reply messages


Firstly, a correctness theorem for Sphinx is very similar to the KEM correctness theorem we discussed above.
It says that we can fully unwrap Sphinx packets that we create such that the final payload is equal to the original
encapsulated payload.

Secondly, integrity. The Sphinx paper (Danezis & Goldberg, 2009) talks
about Sphinx integrity and says that even an adversary who knows every
mix node's private key can't forge a header that a whole chain of
honest nodes will accept, except with negligible probability. In
practice: each hop checks a MAC_i, and the claim is that nobody can
build a public_key_i, encrypted_header_i, mac_i that passes the MAC check at every one of N =
r + 1 hops unless it was built honestly.

Third, wrap resistance. This means the adversary cannot be given a specific target Sphinx packet and produce
a new Sphinx packet which unwraps to the target Sphinx packet, even if the adversary gets to choose the mix node's private key.

Fourth, security and indistinguishability. An adversary who controls every mix node except one, and chooses the
messages, destinations and paths, cannot tell which of two packets entered the honest node, and in particular
cannot tell whether a packet is a forward message or a reply.

It turns out this four property framework is not the end of the story.
[Breaking and (Partially) Fixing Provably Secure Onion Routing](https://arxiv.org/pdf/1910.13772)
showed that these properties don't actually imply ideal onion routing, so even complete proofs of all four wouldn't
show that Sphinx is secure. The later papers replace them with layer unlinkability and tail indistinguishability
properties, which do imply it. Integrity and wrap-resistance no longer appear as separate properties, and forward/reply
indistinguishability is built into the new unlinkability games.



## Sphinx type

Let's briefly look over the Sphinx type definitions and then discuss them below.

Below is our Sphinx type, abridged to its primitives and the two functions the discussion needs. The full definition
is in [Interface.lean](https://github.com/katzenpost/cryptlib/blob/main/Cryptlib/Protocols/Sphinx/Interface.lean).


```lean
structure Sphinx where
  State : Type
  PrivateKey : Type
  Command : Type
  -- ...
  geometry : Geometry.Geometry

  /-- The four cryptographic primitives every Sphinx instance needs besides its NIKE-or-KEM
  (added by `NIKESphinxScheme`/`KEMSphinxScheme`). Kept abstract so swapping e.g. AEZ for
  another wide-block cipher needs no change below. -/
  cipher : Cryptlib.Primitives.WideBlockCipher.WideBlockCipher
  mac    : Cryptlib.Primitives.MAC.MAC
  kdf    : Cryptlib.Primitives.KDF.KDF
  stream : Cryptlib.Primitives.StreamCipher.StreamCipher

  /-- Unused routing-info slots are filled with `drawBytes` from `State`, not supplied by the
  caller. -/
  wrap : List Types.PathHop → Vector UInt8 geometry.forwardPayloadLength →
    EStateM String State (Vector UInt8 geometry.packetLength)

  unwrap : PrivateKey → (pkt : ByteArray) →
    Except String (Option ByteArray × Vector UInt8 32 × List Command × Option (Vector UInt8 pkt.size))
  -- ...

  /-- **Completeness**: any packet `wrap` builds, `unwrap` can undo, given a well-formed path. -/
  unwrap_complete : ∀ (path : List Types.PathHop) (privKeys : List PrivateKey)
      (payload : Vector UInt8 geometry.forwardPayloadLength) (st : State)
      (pkt : Vector UInt8 geometry.packetLength) (st' : State),
    -- ... well-formedness hypotheses ...
    wrap path payload st = .ok pkt st' →
    unwrapChainAux unwrap privKeys (ofVector pkt) = .ok (some (ofVector payload))

  -- `indistinguishable` and `integrity`: the paper's §4.4 and §4.2 arguments, discussed below.
```

Notice that `wrap` and `newSURB` take no filler argument. Earlier versions took the filler for unused hops
from the caller, and nothing in the type stopped a caller from passing zeros. That is exactly the path length leak
found in the "Breaking and (Partially) Fixing" paper: a recognizable padding pattern tells the last mix how
long the path was. The Katzenpost golang implementation already fills these bytes with randomness. The Lean
`wrap` draws the filler from its
own random `State` instead, so a zero filler can no longer be expressed. That's the dependent type thesis again:
fix it in the type, and every instance gets the fix.

Now an honest caveat about the security fields. `unwrap_complete` really is a proof obligation on each instance:
it talks about that instance's own `wrap` and `unwrap`, so an instance with a broken `wrap` cannot be constructed.
`integrity` and `indistinguishable` are different. They have default values, proved once, about an abstract model of
the paper's games (`Integrity.Sys`, `Indistinguishability.Sys`) that never mentions this instance's `wrap` or `unwrap`.
So today they record the paper's arguments inside the type, but they don't yet constrain the instance the way
`unwrap_complete` does. They also still rest on explicit hypotheses:

* **Integrity** assumes the step the paper itself only calls "a careful, but straightforward, calculation", and
  assumes the hardness of the paper's "Problem P".
* **Indistinguishability** reduces the first hybrid step to DDH, but takes the other two steps as hypotheses, and its
  game doesn't let the adversary query the honest node. The
  [Gap Diffie-Hellman proof](https://arxiv.org/pdf/2312.08028) shows that once the adversary
  can query it, DDH isn't enough and the Gap Diffie-Hellman assumption is needed.

However I had to make sub-types of the Sphinx type in order to accurately represent the third security property,
wrap resistance, for only NIKE Sphinx and not for KEM Sphinx. Next I will show you the NIKESphinxScheme and KEMSphinxScheme types:

```lean
structure NIKESphinxScheme extends Cryptlib.Protocols.Sphinx.Interface.Sphinx where
  nike : NIKE
  Envelope : Type
  [envelopeDecEq : DecidableEq Envelope]
  /-- The header's public-key element, read out of a packet. -/
  parseEnvelope : Vector UInt8 geometry.packetLength → Envelope
  /-- The space a fresh blinding factor is drawn from. -/
  Factor : Type
  [factorFintype : Fintype Factor]
  [factorSampleable : SampleableType Factor]
  /-- Re-blind an envelope element by a factor. -/
  blind : Factor → Envelope → Envelope
  /-- **Wrap-resistance**: whenever blinding by `e` is a bijection (the case for any `e` that
  generates the (sub)group a well-formed header's element lives in), a freshly drawn factor hits
  a chosen `target` with probability exactly `1/|Factor|`. -/
  wrap_resistant : ∀ (e target : Envelope), Function.Bijective (blind · e) →
      Pr[= true | ($ᵗ Factor) >>= fun b => pure (decide (blind b e = target))] =
        (Fintype.card Factor : ℝ≥0∞)⁻¹ :=
    fun _ target hbij => uniformHit_eq hbij target
  /-- **Envelope independence** (§4.4, exact rather than up to some advantage): the envelope
  depends only on `wrap`'s seed-stream draw, never on path/payload, so two calls sharing a
  starting `State` produce byte-for-byte identical envelopes — no adversary can learn anything
  about the session's content from it alone. See `wrapNIKE_envelope_indep` (in
  `nike_sphinx_theorems.lean`) for why: the envelope is the client's own public key. -/
  envelope_indep : ∀ (hop0 hop1 : Types.PathHop) (rest0 rest1 : List Types.PathHop)
      (payload0 payload1 : Vector UInt8 geometry.forwardPayloadLength) (st : State)
      (pkt0 pkt1 : Vector UInt8 geometry.packetLength) (st0' st1' : State),
    wrap (hop0 :: rest0) payload0 st = .ok pkt0 st0' →
    wrap (hop1 :: rest1) payload1 st = .ok pkt1 st1' →
    parseEnvelope pkt0 = parseEnvelope pkt1
```

and

```lean
structure KEMSphinxScheme extends Cryptlib.Protocols.Sphinx.Interface.Sphinx where
  kem : KEM
```

KEM Sphinx has no blinding step, so it is not wrap-resistant: a holder of the node's private key can decapsulate any
ciphertext, compute the header keystream, and craft routing info that unwraps to any target. That is a theorem in the
repository (`unwrapKEM_routingInfoBlock_not_wrap_resistant`), not a field. An earlier version stored it in the type as
a `not_wrap_resistant` proposition, but a proposition field is a guarantee every instance must prove, and "an attack
exists" guarantees nothing and constrains no instance. It was documentation in a struct, so it came out.

The caveat about `integrity` and `indistinguishable` also applies to `wrap_resistant`: it holds for any `blind`
whenever blinding is a bijection, which is assumed rather than proved, and nothing yet ties `blind` to what this
instance's `unwrap` actually does.



## Sphinx Considerations

The reason we have the two sub types NIKESphinxScheme and KEMSphinxScheme is because we wanted
to embed all the security properties into struct proposition fields, and since wrap-resistance and envelope
independence only hold for NIKE Sphinx, only NIKESphinxScheme carries them.

I can't think of a reason why Sphinx wrap-resistance would be useful.
The newer security frameworks seem to agree, in that they no longer state it as a separate property at all.

But I'm biased because I usually only think about Sphinx as it is used with the Katzenpost mixnet.
KEM Sphinx doesn't get the wrap-resistance properties and that's fine.
But KEM Sphinx does have a huge downside. It has a large bandwidth overhead with one KEM ciphertext per hop.



## What's next

The plan is to move cryptlib's security fields from the 2009 four property framework to the properties the
followup papers showed actually imply secure onion routing, and to tie them to each instance's own `wrap` and `unwrap`
the way `unwrap_complete` already is:

* For NIKE Sphinx, the layer unlinkability and tail indistinguishability properties from the Gap Diffie-Hellman proof.
* For KEM Sphinx, the EROR style properties, whose proofs only need an IND-CCA secure KEM, a MAC and a PRF.
  That fits cryptlib's generic KEM type well, and it's a path to a post quantum security proof, which the
  Diffie-Hellman based proofs can't give.



## Conclusion: dependent types for the win

It turns out that dependent types are great for writing cryptography libraries!
Correctness proofs compose for free, and design flaws like the zero padding leak can be ruled out by the type itself.
The security proofs are the harder part, and that's where the work continues.

## Sphinx Links

* The original Sphinx paper: [Sphinx: A Compact and Provably Secure Mix Format](https://cypherpunks.ca/~iang/pubs/Sphinx_Oakland09.pdf)

Followup work by other researchers to improve Sphinx and specify stronger security properties:

* [Breaking and (Partially) Fixing Provably Secure Onion Routing](https://arxiv.org/pdf/1910.13772):
  shows that the security properties the Sphinx proof relies on don't actually imply ideal onion routing,
  and finds a path length leak in Sphinx's zero padding.

* [Provable Security for the Onion Routing and Mix Network Packet Format Sphinx](https://arxiv.org/pdf/2312.08028):
  the first security proof for Sphinx that holds, for a slightly adapted Sphinx, under the Gap Diffie-Hellman assumption
  rather than DDH.

* [EROR: Efficient Repliable Onion Routing with Strong Provable Privacy](https://eprint.iacr.org/2024/020):
  a packet format that also prevents the payload tagging attack Sphinx allows, at the cost of doubling the payload.

* [Onion Routing with Replies](https://eprint.iacr.org/2021/1178):
  the formal model for onion routing with replies that EROR builds on.

* [Outfox: a Postquantum Packet Format for Layered Mixnets](https://arxiv.org/abs/2412.19937):
  a post quantum Sphinx variant for fixed length routes. It cites my
  [Post Quantum Sphinx](https://eprint.iacr.org/2023/1960) paper as lacking formal security guarantees,
  which is part of what this work is trying to address.

* [OmniSphinx: Active Mix Networks](https://arxiv.org/abs/2608.13008):
  packets carry code that determines how mixes process them, so one network can emulate many mix formats.

* [Improving the Sphinx Mix Network](https://www.bartmennink.nl/pubs/16cans.pdf):
  proposes replacing Sphinx's separate MAC and payload cipher with one authenticated encryption call per hop.


Some of my contributions to Sphinx:

* The Katzenpost Specification of the Sphinx packet format: https://katzenpost.network/docs/specs/sphinx/

* The Katzenpost Specification of the KEM Sphinx variant: https://katzenpost.network/docs/specs/kemsphinx/

* The Katzenpost Proverif model of KEM Sphinx: https://github.com/katzenpost/formal_specifications/blob/main/sphinx/kem_sphinx.passive.pv

* The Katzenpost implementation of the Sphinx, originally written by Yawning Angel: https://github.com/katzenpost/katzenpost/tree/main/core/sphinx
  I later added the KEM Sphinx variant and test vectors which are shared with the Lean implementation.
