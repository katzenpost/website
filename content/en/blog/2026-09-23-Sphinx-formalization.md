---
title: "Formalization Sphinx in Lean"
date: "2026-09-23"
description: ""
author: "David Stainton"
tags: ["sphinx", "lean", "formalization", "formal methods"]
version: ""
draft: false
---

I recently used Claude Code to formalize the Sphinx cryptographic packet format.
First I'll provide some links to provide some more context about the Sphinx packet format.
And then I'll discuss details about about the formalization.

* https://github.com/katzenpost/CryptWalker



## Sphinx Links

* The original Sphinx cryptographic packet format paper: [Sphinx: A Compact and Provably Secure Mix Format](https://cypherpunks.ca/~iang/pubs/Sphinx_Oakland09.pdf)

* The Katzenpost Specification of the Sphinx packet format: https://katzenpost.network/docs/specs/sphinx/

* The Katzenpost Specification of the KEM Sphinx variant: https://katzenpost.network/docs/specs/kemsphinx/

* The Katzenpost Proverif model of KEM Sphinx: https://github.com/katzenpost/formal_specifications/blob/main/sphinx/kem_sphinx.passive.pv



## Katzenpost's Post Quantum Sphinx

In the Katzenpost mixnet project we use a golang implementation of the Sphinx packet format which is generic
over a NIKE interface. This means we can use any NIKE (non-interactive key exchange) such as X25519 or X448.
Our implementation can also use any KEM for the KEM Sphinx variant.

* https://github.com/katzenpost/katzenpost/tree/main/core/sphinx



## HPQC: Katzenposts's hybrid post quantum cryptography library

* https://github.com/katzenpost/hpqc

HPQC defines our KEM and NIKE golang interfaces which we use to genericize cryptographic protocols like Sphinx.
One interesting contribution of HPQC is that we can use a NIKE combiner and a KEM combiner to make hybrid NIKEs and KEMs
which mix classical and postquantum primitives together. Also HPQC has a NIKE to KEM adapter (hashed ElGamal construction)
which allows us to combine a NIKE such as X25519 as if it were a KEM along with MLKEM.



## The Crypt Walker Theorems

A couple of years ago I chatted with Mario Carneiro on the Lean Zulip
and asked him questions about modeling cryptography in Lean. At some point
he posted a sort of minimal KEM type definition in Lean whose struct contains
a proposition field with the KEM completeness theorem. It says that everything the KEM
encapsulates can be decapsulated:

https://leanprover.zulipchat.com/#narrow/channel/236449-Program-verification/topic/Lean.20library.20rust.20integration.3F/near/452695059

At the time, I was considering that I didn't really want yet another symbolic modeler for cryptography
because I was already using Proverif which works great and automates finding security flaws.
So I wrote Lean implementations of a few constructions in HPQC including a NIKE to KEM adapter, the NIKE combiner, the KEM combiner.
I was able to get help both in person at a Lean study meetup and on the Lean zulip when I had Lean programming questions.
The Lean community is very friendly and very smart.

After about two years passed, I started working on CryptWalker again, at the Utrecht University Summer Lean Theorem Prover class.
It was a 5 day Lean workshop with a couple of days devoted to the student chosen projects.
I was able to write theorems about the HPQC constructs that said:

* A NIKE is lawful if it's group operation is commutative.
* A KEM is lawful if it can decapsulate everything it encapsulates.

And then I wrote a theorem that said:

* Given a lawful NIKE, the NIKE to KEM adapter (hashed ElGamal construction) produces a lawful KEM.



## Proclivity Towards Dependent Types

Instead of writing a struct type definition and then separate thereoms,
I realized that some of the theorems about a given cryptographic primitive can be placed inside the type's struct field
and it can say something about the other fields of the struct type. So the NIKE proposition field called "commutes" contains
a thereom that says the group operation is commutative. That's the whole point of the Diffie Hellman Shared Secret, is that it's
commutative and therefore both parties can computate the same shared secret by different means, e.g. g^x^y = g^y^x

Likewise I make a completeness proposition field for the KEM type that says the KEM can always depcapsulate whatever it encapsulates.
Once the NIKE to KEm adapter is wired to use these new types there is no longer any need to write the following theorem:

* Given a lawful NIKE, the NIKE to KEM adapter (hashed ElGamal construction) produces a lawful KEM.

It's no longer needed because the type system prevents a NIKE implementation from having a group operation that is not commutative.
Likewise, all KEM instances must satisfy the completeness theorem built into the KEM type, in the struct's proposition field.
To be clear, these type proposition fields are in fact proof obligations for all type instances of NIKE and KEM.
HOWEVER, the tradeoff is that now we get a type system gaurantee that the rules of the type cannot be violated and only
valid type instances can ever be expressed in Lean.



## Implicit Proofs are transitive in depedent type composition

My thesis here is simple:

"When we use dependent types in composition we get implicit transitive proofs for free."

With the example of the NIKE to KEM adapter, we got the transitive proof for free.
I asked Claude Code to write me a Sphinx implementation in Lean which can be verified
using test vectors shared with the Katzenpost Sphinx implementation.

However, I found that with the Lean implementation of Sphinx, there are additional benefits
to using dependent types to represent cryptographic primitive functions: The proof obligations
were reduced and greatly simplified!

I proceeded to development this Sphinx formalization in Lean in roughly 4 phases:

1. Implement Sphinx is a static cryptographic construction with specific primitives.
2. Try to prove the 4 security properties from the Sphinx paper: fail because the proofs involve too much complexity from the individual cryptographic primitive funtions.
3. Rewrite our Lean language Sphinx construction to use generic depedent types representing each cryptographic function in the construction: NIKE/KEM, Stream Cipher, KDF, MAC, Wide-block Cipher.
4. Try to prove the 4 security properties from the Sphinx paper: Success!

In other words, when trying to prove the security properties of the static Sphinx construction using for example the AEZ block cipher
I then also have a proof obligation which involves the complexities of AEZ. However If I replace AEZ with a generic wide-block cipher
type, a dependent type with an encryption/decryption completeness proposition in one of it's struct fields.
This greatly simplifies our existing proof obligations.




## Sphinx Security Properties

Section 4 of the Sphinx paper discusses 4 security properties:

1. correctness
2. integrity
3. wrap-resistance
4. indistinguishability of forward and reply messages


Firstly, a correctness theorem for Sphinx is very similar to the KEM correctness theorem we discussed above.
It says that we can fully unwrap Sphinx packets that we create such that the final payload is equal to the original
encapsulated payload.

Secondly, integrity. The Sphinx paper (Danezis & Goldberg, 2009) talks
about Sphinx integrity and say that even an adversary who knows every
mix node's private key can't forge a header that a whole chain of
honest nodes will accept, except with negligible probability. In
practice: each hop checks a MAC_i, and the claim is that nobody can
build an public_key_i, encrypted_header_i, mac_i that passes the MAC check at every one of N =
r + 1 hops unless it was built honestly.

Third, wrap resistance. This means the adversary cannot be given a specific target Sphinx packet and produce
a new Sphinx packet which unwraps to the target Sphinx packet.

Forth, indistinguishability. The property of forward and reply messages are indistinguishable.



## Sphinx type

Let's briefly look over the Sphinx type defintions and then discuss them below.

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

  wrap : List Types.PathHop → (filler : ByteArray) → Vector UInt8 geometry.forwardPayloadLength →
    EStateM String State (Vector UInt8 geometry.packetLength)

  /-- `(payload, replayTag, cmds, forwardPkt)`. -/
  unwrap : PrivateKey → (pkt : ByteArray) →
    Except String (Option ByteArray × Vector UInt8 32 × List Command × Option (Vector UInt8 pkt.size))

  newSURB : List Types.PathHop → (filler : ByteArray) →
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
      (filler : ByteArray) (payload : Vector UInt8 geometry.forwardPayloadLength) (st : State)
      (pkt : Vector UInt8 geometry.packetLength) (st' : State),
    path ≠ [] →
    unwrapReliable st →
    path.map (·.publicKey) = privKeys.map derivePublicKey →
    (∀ hop ∈ path, ∀ c ∈ hop.commands, c ≠ .null ∧ (∀ id m, c ≠ .nextNodeHop id m)) →
    (∀ c ∈ (path[path.length - 1]!).commands, ∀ id, c ≠ .surbReply id) →
    wrap path filler payload st = .ok pkt st' →
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

However I had to make sub-types of the Sphinx type in order to accurately represent the 4th security property,
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
  depends only on `wrap`'s seed-stream draw, never on path/filler/payload, so two calls sharing a
  starting `State` produce byte-for-byte identical envelopes — no adversary can learn anything
  about the session's content from it alone. See `wrapNIKE_envelope_indep` (in
  `nike_sphinx_theorems.lean`) for why: the envelope is the client's own public key. -/
  envelope_indep : ∀ (hop0 hop1 : Types.PathHop) (rest0 rest1 : List Types.PathHop)
      (filler0 filler1 : ByteArray)
      (payload0 payload1 : Vector UInt8 geometry.forwardPayloadLength) (st : State)
      (pkt0 pkt1 : Vector UInt8 geometry.packetLength) (st0' st1' : State),
    wrap (hop0 :: rest0) filler0 payload0 st = .ok pkt0 st0' →
    wrap (hop1 :: rest1) filler1 payload1 st = .ok pkt1 st1' →
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

## Sphinx Considerations

I honestly can't think of a reason why Sphinx wrap-resistance would be useful.
But I'm biased because I usually only think about Sphinx as it is used with the Katzenpost mixnet.
KEM Sphinx doesn't get the wrap-resistance properties and that's fine.
But KEM Sphinx does have a huge downside. It has a large bandwidth overhead with one KEM ciphertext per hop.










