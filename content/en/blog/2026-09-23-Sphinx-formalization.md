---
title: "Formalizing Sphinx in Lean"
date: "2026-09-23"
description: "A Lean formalization of the Sphinx packet format, generic over its cryptographic primitives, and what it does and doesn't prove."
author: "David Stainton"
tags: ["sphinx", "lean", "formalization", "formal methods"]
version: ""
draft: false
---

I recently used Claude Code to formalize the Sphinx cryptographic packet format.
First I'll provide some links to provide some more context about the Sphinx packet format.
And then I'll discuss details about the formalization.

* https://github.com/katzenpost/CryptWalker



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


## Katzenpost's Post Quantum Sphinx

In the Katzenpost mixnet project we use a golang implementation of the Sphinx packet format which is generic
over a NIKE interface. This means we can use any NIKE (non-interactive key exchange).
Our implementation can also use any KEM (key encapsulation mechanism) for the KEM Sphinx variant.

* https://github.com/katzenpost/katzenpost/tree/main/core/sphinx

To be clear, both variations of Sphinx can be post quantum or hybrid post quantum combining classical and post quantum
public key primitives together.


## HPQC: Katzenpost's hybrid post quantum cryptography library

* https://github.com/katzenpost/hpqc

HPQC defines our KEM and NIKE golang interfaces which we use to genericize cryptographic protocols like Sphinx.
One interesting contribution of HPQC is that we can use a NIKE combiner and a KEM combiner to make hybrid NIKEs and KEMs
which mix classical and postquantum primitives together. Also HPQC has a NIKE to KEM adapter (hashed ElGamal construction)
which allows us to combine a NIKE such as X25519 as if it were a KEM along with MLKEM. This helps us make hybrid KEMs
by for example combining X25519 with a post quantum KEM such as MLKEM.



## The Crypt Walker Theorems

A couple of years ago I was very excited to be learning Lean. I started the Lean theorem prover meetup
at the Noisebridge hacker space in San Francisco, which ran as a weekly study group.
I was fortunate that some very smart people attended
the study meetings because I was able to learn a lot from the group.

The Lean community on the Lean Zulip was also very enthusiastic to answer my questions and help
me when I got stuck. Several times I ended up chatting with Mario Carneiro on the Lean Zulip
and asked him questions about program verification and modeling cryptography in Lean. At some point
he posted a sort of minimal KEM type definition in Lean whose struct contains
a proposition field with the KEM completeness theorem. It says that everything the KEM
encapsulates can be decapsulated:

https://leanprover.zulipchat.com/#narrow/channel/236449-Program-verification/topic/Lean.20library.20rust.20integration.3F/near/452695059

At the time, I was considering that I didn't really want yet another symbolic modeler for cryptography
because I was already using Proverif which works great and automates finding security flaws.
Obviously if I used Lean's type theory to make a symbolic modeler for cryptography protocols, it wouldn't
have any automated security analysis or any of the features that Proverif or Tamarin have for finding protocol information leaks etc.

I didn't fully understand the implications of what Mario was showing me.
It's so much more than a symbolic model but we'll come back to that shortly.

So I wrote Lean implementations of a few constructions in HPQC including a NIKE to KEM adapter, the NIKE combiner, the KEM combiner.
After about two years passed, I started working on CryptWalker again, at the Utrecht University Summer Lean Theorem Prover class.
It was a 5 day Lean workshop with a couple of days devoted to the student chosen projects.
I was able to write theorems about the HPQC constructs that said:

* A NIKE is lawful if its group operation is commutative.
* A KEM is lawful if it can decapsulate everything it encapsulates.

And then I wrote a theorem that said:

* Given a lawful NIKE, the NIKE to KEM adapter (hashed ElGamal construction) produces a lawful KEM.



##  Towards A Dependent Type Proclivity

Instead of writing a struct type definition and then separate theorems,
I realized that some of the theorems about a given cryptographic primitive can be placed inside the type's struct field
and it can say something about the other fields of the struct type. So the NIKE proposition field called "commutes" contains
a theorem that says the group operation is commutative. That's the whole point of the Diffie Hellman Shared Secret, is that it's
commutative and therefore both parties can compute the same shared secret by different means, e.g. g^x^y = g^y^x

Likewise I make a completeness proposition field for the KEM type that says the KEM can always decapsulate whatever it encapsulates.
Once the NIKE to KEM adapter is wired to use these new types, the theorem

* Given a lawful NIKE, the NIKE to KEM adapter (hashed ElGamal construction) produces a lawful KEM.

stops being a separate theorem that someone has to remember to state and apply. The adapter can't even construct its KEM
without filling in the KEM's completeness field, so the proof is written exactly once, inside the adapter, using the
NIKE's own "commutes" field. The type system prevents a NIKE implementation from having a group operation
that is not commutative. Likewise, all KEM instances must satisfy the completeness theorem built into the KEM type, in the struct's proposition field.
To be clear, these type proposition fields are in fact proof obligations for all type instances of NIKE and KEM.
The tradeoff is worth it though: we get a type system guarantee that the rules of the type cannot be violated and only
valid type instances can ever be expressed.



## Implicit Proofs are transitive in dependent type composition

My thesis here is simple:

"When we use dependent types in composition we get implicit transitive proofs for free."

With the example of the NIKE to KEM adapter, every user of the adapter's KEM gets the completeness proof for free,
and never has to prove it again.
I asked Claude Code to write me a Sphinx implementation in Lean which can be verified
using test vectors shared with the Katzenpost Sphinx implementation.

However, I found that with the Lean implementation of Sphinx, there are additional benefits
to using dependent types to represent cryptographic primitive functions: The proof obligations
were reduced and greatly simplified!

I developed this Sphinx formalization in Lean in roughly 4 phases:

1. Implement Sphinx as a static cryptographic construction with specific primitives.
2. Try to prove the Sphinx paper's security properties: fail because the proofs involve too much complexity from the individual cryptographic primitive functions.
3. Rewrite our Lean language Sphinx construction to use generic dependent types representing each cryptographic function in the construction: NIKE/KEM, Stream Cipher, KDF, MAC, Wide-block Cipher.
4. Try again: correctness is now proved outright, over any NIKE or KEM and any choice of the other primitives. The other three properties are formalized, with the steps that aren't proved yet isolated as explicit hypotheses.

In other words, when trying to prove the security properties of the static Sphinx construction using for example the AEZ block cipher,
I then also have a proof obligation which involves the complexities of AEZ. However, if I replace AEZ with a generic wide-block cipher
type, a dependent type with an encryption/decryption completeness proposition in one of its struct fields,
the Sphinx proofs only need that one proposition and never look inside AEZ.
This greatly simplifies our existing proof obligations.




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

It turns out this four property framework is not the end of the story. The first followup paper listed above
showed that these properties don't actually imply ideal onion routing, so even complete proofs of all four wouldn't
show that Sphinx is secure. The later papers replace them with layer unlinkability and tail indistinguishability
properties, which do imply it. Integrity and wrap-resistance no longer appear as separate properties, and forward/reply
indistinguishability is built into the new unlinkability games.



## Sphinx type

Let's briefly look over the Sphinx type definitions and then discuss them below.

Crypt Walker git repo:

* https://github.com/katzenpost/CryptWalker


* Below is our Sphinx type definition and here's also a link to Sphinx type definition: https://github.com/katzenpost/CryptWalker/blob/main/CryptWalker/Sphinx/sphinx.lean


```lean

structure Sphinx where
  State : Type
  PrivateKey : Type
  Command : Type
  [stateI : Inhabited State]
  [privI : Inhabited PrivateKey]

  geometry : Geometry.Geometry

  /-- The four cryptographic primitives every Sphinx instance needs besides its NIKE-or-KEM
  (added by `NIKESphinxScheme`/`KEMSphinxScheme`): a wide-block cipher for the payload, a MAC for
  header integrity, a KDF for per-hop keys, a stream cipher for routing-info encryption. Kept
  abstract so swapping e.g. AEZ for another wide-block cipher needs no change below. -/
  cipher : CryptWalker.WideBlockCipher.WideBlockCipher
  mac    : CryptWalker.MAC.MAC
  kdf    : CryptWalker.KDF.KDF
  stream : CryptWalker.StreamCipher.StreamCipher

  /-- Raw bytes — width depends on which NIKE/KEM this scheme wraps, not fixed here. -/
  derivePublicKey : PrivateKey → ByteArray

  /-- Unused routing-info slots are filled with `drawBytes` from `State`, not supplied by the
  caller (see `fillerLength`). -/
  wrap : List Types.PathHop → Vector UInt8 geometry.forwardPayloadLength →
    EStateM String State (Vector UInt8 geometry.packetLength)

  /-- `(payload, replayTag, cmds, forwardPkt)`. -/
  unwrap : PrivateKey → (pkt : ByteArray) →
    Except String (Option ByteArray × Vector UInt8 32 × List Command × Option (Vector UInt8 pkt.size))

  newSURB : List Types.PathHop →
    EStateM String State (Vector UInt8 geometry.surbLength × ByteArray)

  newPacketFromSURB : Vector UInt8 geometry.surbLength → ByteArray →
    Except String (ByteArray × Vector UInt8 32)

  /-- Which starting states are guaranteed not to run into the backing scheme's rare correctness
  failure over an unbounded run. `True` for every perfect-correctness backing — every NIKE, and
  any Diffie-Hellman-based KEM (`KEM.KEM.Reliable`'s own default, unchanged) — since neither has a
  decoding step with a failure mode to name. A KEM-Sphinx instance backed by a lattice-based KEM
  (e.g. ML-KEM) overrides this with the real per-draw guarantee its own `KEM.Reliable` needs. -/
  unwrapReliable : State → Prop := fun _ => True

  /-- **Completeness**: any packet `wrap` builds, `unwrap` can undo, given `path` is well-formed —
  no hop's `commands` already contains `null` or `nextNodeHop` (both wire-level sentinels this
  port only ever constructs itself, never something a caller supplies), and the last hop carries
  no `surbReply` (a real command, just one that changes `unwrap`'s terminal-hop behavior — its own
  completeness is tracked separately). -/
  unwrap_complete : ∀ (path : List Types.PathHop) (privKeys : List PrivateKey)
      (payload : Vector UInt8 geometry.forwardPayloadLength) (st : State)
      (pkt : Vector UInt8 geometry.packetLength) (st' : State),
    path ≠ [] →
    unwrapReliable st →
    path.map (·.publicKey) = privKeys.map derivePublicKey →
    (∀ hop ∈ path, ∀ c ∈ hop.commands, c ≠ .null ∧ (∀ id m, c ≠ .nextNodeHop id m)) →
    (∀ c ∈ (path[path.length - 1]!).commands, ∀ id, c ≠ .surbReply id) →
    wrap path payload st = .ok pkt st' →
    unwrapChainAux unwrap privKeys (ofVector pkt) = .ok (some (ofVector payload))

  /-- **Indistinguishability** (§4.4): `Indistinguishability.advantage_le`, closed over every
  scheme it's about. Free for every instance — see that theorem's own module doc for the games
  and hardness assumptions it reduces to. -/
  indistinguishable : ∀ {F G Seed KeyMu KeyPi Beta Gamma Delta : Type}
      [Field F] [AddCommGroup G] [Module F G] [AddCommGroup Beta]
      [SampleableType F] [SampleableType Seed] [SampleableType KeyMu] [SampleableType KeyPi]
      [SampleableType Beta] [SampleableType Gamma] [SampleableType Delta]
      [SampleableType (Seed × KeyMu × KeyPi)] [Finite F]
      (S : Indistinguishability.Sys F G Seed KeyMu KeyPi Beta Gamma Delta),
      Indistinguishability.AdvantageLeType S :=
    fun S => Indistinguishability.advantage_le S

  /-- **Integrity** (§4.2): `Integrity.integrity_bound`, closed over every scheme it's about.
  Free for every instance — see that theorem's own module doc for `ProblemP`, its named hardness
  hypothesis. -/
  integrity : ∀ {F G Seed Idx Yy Kappa : Type} [Field F] [AddCommGroup G] [Module F G]
      [Nonempty Yy] (S : Integrity.Sys F G) (hρ : G → Seed) (ρhat0 : Seed → Kappa)
      (ρ0 : Seed → Idx) (f : Idx → Yy → Kappa),
      Integrity.IntegrityBoundType S hρ ρhat0 ρ0 f :=
    fun S hρ ρhat0 ρ0 f => Integrity.integrity_bound S hρ ρhat0 ρ0 f

```

Notice that `wrap` and `newSURB` take no filler argument. Earlier versions took the filler for unused hops
from the caller, and nothing in the type stopped a caller from passing zeros. That is exactly the path length leak
found in the "Breaking and (Partially) Fixing" paper above: a recognizable padding pattern tells the last mix how
long the path was. The Katzenpost golang implementation already fills these bytes with randomness. In
[CryptWalker PR #19](https://github.com/katzenpost/CryptWalker/pull/19) the Lean `wrap` draws the filler from its
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
  game doesn't let the adversary query the honest node. The second followup paper above shows that once the adversary
  can query it, DDH isn't enough and the Gap Diffie-Hellman assumption is needed.

However I had to make sub-types of the Sphinx type in order to accurately represent the third security property,
wrap resistance, for only NIKE Sphinx and not for KEM Sphinx. Next I will show you the NIKESphinxScheme and KEMSphinxScheme types:

```lean
structure NIKESphinxScheme extends CryptWalker.Sphinx.Interface.Sphinx where
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
structure KEMSphinxScheme extends CryptWalker.Sphinx.Interface.Sphinx where
  kem : KEM
  /-- **Not wrap-resistant** — the inverse of `NIKESphinxScheme.wrap_resistant`: a known-key
  adversary hits any target routing-info block with certainty, not merely `1/N`. See
  `unwrapKEM_routingInfoBlock_not_wrap_resistant` (in `kem_sphinx_theorems.lean`) for why. Holds
  for any `stream : StreamCipher`, not just a hardcoded one. -/
  not_wrap_resistant : ∀ (key iv target : ByteArray),
      ∃ raw : ByteArray, xorBytes raw (stream.keystream key iv target.size) = target :=
    fun key iv target => xorBytes_achieves_any_target (stream.keystream key iv target.size) target
```

The same caveat applies to `wrap_resistant`: it holds for any `blind` whenever blinding is a bijection, which is
assumed rather than proved, and nothing yet ties `blind` to what this instance's `unwrap` actually does.



## Sphinx Considerations

The reason we have the two sub types NIKESphinxScheme and KEMSphinxScheme is because we wanted
to embed all the security properties into struct proposition fields, and since the Sphinx wrap-resistance property
only applies to NIKE Sphinx we therefore needed two Sphinx types to work with.

I can't think of a reason why Sphinx wrap-resistance would be useful.
The newer security frameworks seem to agree, in that they no longer state it as a separate property at all.

But I'm biased because I usually only think about Sphinx as it is used with the Katzenpost mixnet.
KEM Sphinx doesn't get the wrap-resistance properties and that's fine.
But KEM Sphinx does have a huge downside. It has a large bandwidth overhead with one KEM ciphertext per hop.



## What's next

The plan is to move CryptWalker's security fields from the 2009 four property framework to the properties the
followup papers showed actually imply secure onion routing, and to tie them to each instance's own `wrap` and `unwrap`
the way `unwrap_complete` already is:

* For NIKE Sphinx, the layer unlinkability and tail indistinguishability properties from the Gap Diffie-Hellman proof.
* For KEM Sphinx, the EROR style properties, whose proofs only need an IND-CCA secure KEM, a MAC and a PRF.
  That fits CryptWalker's generic KEM type well, and it's a path to a post quantum security proof, which the
  Diffie-Hellman based proofs can't give.



## Conclusion: dependent types for the win

It turns out that dependent types are great for writing cryptography libraries!
Correctness proofs compose for free, and design flaws like the zero padding leak can be ruled out by the type itself.
The security proofs are the harder part, and that's where the work continues.
