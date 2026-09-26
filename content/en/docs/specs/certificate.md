---
title: ""
linkTitle: "Certificate format"
description: ""
author: ""
url: ""
date: "2026-06-02T10:58:05.050489242-07:00"
draft: "false"
slug: "certificate"
layout: ""
type: ""
weight: "10"
version: ""
---

{{% pageinfo %}}
The main text preserves the original certificate design and key-delegation proposals.
The [identity signature profile](#identity-signature-profile) defines the v0.0.107 hybrid signature and key encodings.
Current [directory certificate envelopes](/docs/specs/dirauth#27-certificate-envelopes-and-signing) use epoch-based expiration and a map of signatures.
{{% /pageinfo %}}

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="certificate"></span>Certificate format

</div>

<div>

<div class="authorgroup">

<div class="author">

### <span class="firstname">David</span> <span class="surname">Stainton</span>

</div>

</div>

</div>

<div>

<div class="abstract">

**Abstract**

This document proposes a certificate format that Katzenpost mix server, directory
authority server and clients will use.

</div>

</div>

</div>

------------------------------------------------------------------------

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="conventions-used-in-this-document"></span>Conventions used in this document

</div>

</div>

</div>

The key words <span class="quote">“<span class="quote">MUST</span>”</span>, <span class="quote">“<span class="quote">MUST NOT</span>”</span>, <span class="quote">“<span class="quote">REQUIRED</span>”</span>,
<span class="quote">“<span class="quote">SHALL</span>”</span>, <span class="quote">“<span class="quote">SHALL NOT</span>”</span>, <span class="quote">“<span class="quote">SHOULD</span>”</span>, <span class="quote">“<span class="quote">SHOULD
NOT</span>”</span>, <span class="quote">“<span class="quote">RECOMMENDED</span>”</span>, <span class="quote">“<span class="quote">MAY</span>”</span>, and
<span class="quote">“<span class="quote">OPTIONAL</span>”</span> in this document are to be interpreted as described in <a href="#RFC2119" class="link">RFC2119</a>.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="certificate_introduction"></span>Introduction

</div>

</div>

</div>

Mix servers and directory authority servers need to have key agility in the sense
of
operational abilities such as key rotation and key revocation. That is, we wish for
mixes and authorities to periodically utilize a long-term signing key for generating
certificates for new short-term signing keys.

Yet another use-case for these certificate is to replace the use of JOSE <a href="#RFC7515" class="link">RFC7515</a> in the voting directory authority system <a href="#KATZMIXPKI" class="link">KATZMIXPKI</a> for the multi-signature documents exchanged
for voting and consensus.

<div class="section">

<div class="titlepage">

<div>

<div>

#### <span id="document-format"></span>Certificate format

</div>

</div>

</div>

The CBOR <a href="#RFC7049" class="link">RFC7049</a> serialization format is used to
serialize certificates:

Signature is a cryptographic signature which has an associated signer ID.

``` programlisting
type Signature struct {
// Identity is the identity of the signer.
Identity []byte
// Signature is the actual signature value.
Signature []byte
}
```

Certificate structure for serializing certificates.

``` programlisting
type certificate struct {
// Version is the certificate format version.
Version uint32

// Expiration is seconds since Unix epoch.
Expiration int64

// KeyType indicates the type of key
// that is certified by this certificate.
KeyType string

// Certified is the data that is certified by
// this certificate.
Certified []byte

// Signatures are the signature of the certificate.
Signatures []Signature
}
```

That is, one or more signatures sign the certificate. However the
`Certified` field is not the only information that is signed.
The `Certified` field along with the other non-signature fields are
all concatenated together and signed. Before serialization the signatures are sorted
by their identity so that the output is binary deterministic.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

#### <span id="certificate-types"></span>Certificate types

</div>

</div>

</div>

The certificate `type` field indicates the type of certificate.
So far we have only two types:

<div class="itemizedlist">

- identity key certificate

- directory authority certificate

</div>

Both mixes and directory authority servers have a secret, long-term identity key.
This key is ideally stored encrypted and offline, it’s used to sign key certificate
documents. Key certificates contain a medium-term signing key that is used to sign
other documents. In the case of an <span class="quote">“<span class="quote">authority signing key</span>”</span>, it is used
to sign vote and consensus documents whereas the <span class="quote">“<span class="quote">mix singing key</span>”</span> is
used to sign mix descriptors which are uploaded to the directory authority servers.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

#### <span id="certificate-key-types"></span>Certificate key types

</div>

</div>

</div>

It’s more practical to continue using Ed25519 <a href="#ED25519" class="link">ED25519</a> keys but it’s also possible that in the future we could upgrade
to a stateless hash based post quantum cryptographic signature scheme such as
SPHINCS-256 or SPHINCS+. <a href="#SPHINCS256" class="link">SPHINCS256</a>

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="golang-api"></span>Golang API

</div>

</div>

</div>

<div class="itemizedlist">

- https://godoc.org/github.com/katzenpost/katzenpost/core/crypto/cert

</div>

Our golang implementation is agnostic to the specific cryptographic signature scheme
which is used. Cert can handle single and multiple signatures per document and has
a
variety of helper functions that ease use for multi signature use cases.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="acknowledgments"></span>Acknowledgments

</div>

</div>

</div>

This specification was inspired by Tor Project’s certificate format specification
document:

<div class="itemizedlist">

- https://gitweb.torproject.org/torspec.git/tree/cert-spec.txt

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="appendix-a.-references"></span>References

</div>

</div>

</div>

<span id="ED25519"></span><span class="bold">**ED25519**</span>

<a href="https://www.rfc-editor.org/rfc/rfc8032" class="link" target="_top">https://www.rfc-editor.org/rfc/rfc8032</a>.

<span id="KATZMIXPKI"></span><span class="bold">**KATZMIXPKI**</span>

Angel, Y., Piotrowska, A., Stainton, D., <span class="quote">“<span class="quote">Katzenpost Mix Network Public Key Infrastructure Specification</span>”</span>, December 2017, <a href="https://katzenpost.network/docs/specs/pdf/pki.pdf" class="link" target="_top">https://katzenpost.network/docs/specs/pdf/pki.pdf</a>.

<span id="RFC2119"></span><span class="bold">**RFC2119**</span>

Bradner, S., <span class="quote">“<span class="quote">Key words for use in RFCs to Indicate Requirement
Levels</span>”</span>, BCP 14, RFC 2119, DOI 10.17487/RFC2119, March 1997, <a href="http://www.rfc-editor.org/info/rfc2119" class="link" target="_top">http://www.rfc-editor.org/info/rfc2119</a>.

<span id="RFC7049"></span><span class="bold">**RFC7049**</span>

C. Bormann, P. Hoffman, <span class="quote">“<span class="quote">Concise Binary Object Representation (CBOR)</span>”</span>, Internet Engineering Task Force (IETF), October 2013,
<a href="https://www.rfc-editor.org/info/rfc7049" class="link" target="_top">https://www.rfc-editor.org/info/rfc7049</a>.

<span id="RFC7515"></span><span class="bold">**RFC7515**</span>

Jones, M., Bradley, J., Sakimura, N., <span class="quote">“<span class="quote">JSON Web Signature (JWS)</span>”</span>, May 2015,
<a href="https://www.rfc-editor.org/info/rfc7515" class="link" target="_top">https://www.rfc-editor.org/info/rfc7515</a>.

<span id="RFC7693"></span><span class="bold">**RFC7693**</span>

Saarinen, M-J., Ed., and J-P. Aumasson, <span class="quote">“<span class="quote">The BLAKE2 Cryptographic Hash and Message Authentication Code (MAC)</span>”</span>, RFC 7693, DOI 10.17487/RFC7693, November 2015,
<a href="http://www.rfc-editor.org/info/rfc7693" class="link" target="_top">http://www.rfc-editor.org/info/rfc7693</a>.

<span id="SPHINCS256"></span><span class="bold">**SPHINCS256**</span>

Bernstein, D., Hopwood, D., Hulsing, A., Lange, T., Niederhagen, R., Papachristodoulou,
L., Schwabe, P., Wilcox O'Hearn, Z.,
<span class="quote">“<span class="quote">SPHINCS: practical stateless hash-based signatures</span>”</span>,
<a href="http://sphincs.cr.yp.to/sphincs-20141001.pdf" class="link" target="_top">http://sphincs.cr.yp.to/sphincs-20141001.pdf</a>.

</div>

</div>

## Appendix: Identity signature profile {#identity-signature-profile}

This profile defines identity signatures and key encodings for Namenlos with Katzenpost v0.0.107. Its rules apply to the current [directory certificate envelopes](/docs/specs/dirauth#27-certificate-envelopes-and-signing). The main text above preserves the original certificate design.

Here, `||` means byte concatenation. CBOR fields carry raw public keys as byte strings. The key bytes have no ASN.1 wrapper, length prefix, or text encoding.

<div class="key-value-table">

| Key | Value | Explanation |
| --- | --- | --- |
| Signature scheme | `Ed25519 Sphincs+` | Use this exact name in the baseline certificate `KeyType` and document `PKISignatureScheme`. The space is significant. |
| Public key | 96 bytes | Ed25519 public key, 32 bytes, followed by SPHINCS+ public key, 64 bytes. |
| Private key | 192 bytes | Ed25519 seed, 32 bytes, Ed25519 public key, 32 bytes, then SPHINCS+ secret key, 128 bytes. |
| Identity hash | `BLAKE2b-256(identity_public_key)` | Hash the 96 raw public-key bytes. The result is 32 raw bytes. |

</div>

The [signature scheme definition](https://github.com/katzenpost/hpqc/blob/v0.0.93/sign/hybrid/sphincsplus.go#L16-L18) fixes the name and component order. Identity hashes use sequential [BLAKE2b from RFC 7693](https://www.rfc-editor.org/rfc/rfc7693) with a 32-byte output. Do not truncate BLAKE2b-512 to produce BLAKE2b-256.

### Key files

The public PEM label is `ED25519 SPHINCS+ PUBLIC KEY`. The private PEM label is `ED25519 SPHINCS+ PRIVATE KEY`. A PEM payload is the base64 encoding of the corresponding raw key. There are no PEM headers or ASN.1 fields.

The signature private payload is `Ed25519_seed[32] || Ed25519_public[32] || SPHINCS_secret[128]`. This encoding permits import of reference key files. An implementation can use its own internal storage format. The [PEM codec](https://github.com/katzenpost/hpqc/blob/v0.0.93/sign/pem/pem.go#L21-L34) wraps the [raw private bytes](https://github.com/katzenpost/hpqc/blob/v0.0.93/sign/hybrid/hybrid.go#L207-L216).

### Signature algorithm

Use pure [Ed25519 from RFC 8032, Section 5.1](https://www.rfc-editor.org/rfc/rfc8032#section-5.1) and [SPHINCS+ round 3.1](https://sphincs.org/data/sphincs%2B-r3.1-specification.pdf), parameter set `SPHINCS+-SHAKE-256f-robust`. The SPHINCS+ parameters are n=32, h=68, d=17, FORS height=9, FORS trees=35, and Winternitz w=16. Use the `robust` tweakable hashes. The public key is `PUB_SEED[32] || root[32]`. The secret key is `SK_SEED[32] || SK_PRF[32] || PUB_SEED[32] || root[32]`.

Let `M` be the exact byte string to sign. Directory objects use their [specified signing inputs](/docs/specs/dirauth#signed-data-formats). Both component algorithms sign the same `M`:

```text
signature = Ed25519.Sign(ed_sk, M) || SPHINCS+.Sign(spx_sk, M)
```

The first signature is 64 bytes. The second is 49856 bytes. The complete signature is 49920 bytes.

The SPHINCS+ signature contains its 32-byte `R`, FORS signature, and hypertree signature in the order defined by the primitive specification. The signer uses fresh 32-byte `optrand` for SPHINCS+. Do not add an external prehash, context, message prefix, or length field. In particular, this profile uses neither Ed25519ph nor SLH-DSA. Verification MUST reject an incorrect signature length. It MUST accept only when both component signatures verify against `M`.

The implementation composes [the two signatures](https://github.com/katzenpost/hpqc/blob/v0.0.93/sign/hybrid/hybrid.go#L60-L79) and [the two public keys](https://github.com/katzenpost/hpqc/blob/v0.0.93/sign/hybrid/hybrid.go#L267-L276) in this order. Its SPHINCS+ selection fixes [SHAKE-256f and `robust` hashing](https://github.com/katzenpost/sphincsplus/blob/v0.0.2/ref/Makefile#L1-L12), [the parameters](https://github.com/katzenpost/sphincsplus/blob/v0.0.2/ref/params/params-sphincs-shake-256f.h#L6-L16), and [the key and signature encodings](https://github.com/katzenpost/sphincsplus/blob/v0.0.2/ref/sign.c#L48-L155).
