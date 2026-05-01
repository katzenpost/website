{ "title": "" , "linkTitle": "KEMSphinx" , "description": "" , "url":
"docs/specs/kemsphinx.html" , "date":
"2026-05-01T16:07:40.064824319-07:00", "draft": "false" , "slug": "" ,
"layout": "" , "type": "" , "weight": "20" }

<div class="article">

<div class="titlepage">

<div>

<div>

# <span id="kemsphinx"></span>KEMSphinx

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

Here I present a modification of the Sphinx cryptographic packet format
that uses a KEM instead of a NIKE whilst preserving the properties of
bitwise unlinkability, constant packet size and route length hiding.

</div>

</div>

</div>

------------------------------------------------------------------------

</div>

<div class="toc">

**Table of Contents**

<span class="section">[1. Introduction](#kemsphinx_introduction)</span>

<span class="section">[2. Post Quantum Hybrid
KEM](#post-quantum-hybrid-kem)</span>

<span class="section">[2.1 NIKE to KEM
adapter](#nike-to-kem-adapter)</span>

<span class="section">[2.2 KEM Combiner](#kem-combiner)</span>

<span class="section">[3. KEMSphinx Header
Design](#kemsphinx-header-design)</span>

<span class="section">[4. KEMSphinx Unwrap
Operation](#kemsphinx-unwrap-operation)</span>

<span class="section">[Acknowledgments](#acknowledgments)</span>

<span class="section">[References](#appendix-a.-references)</span>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="kemsphinx_introduction"></span>1. Introduction

</div>

</div>

</div>

We’ll express our KEM Sphinx header in pseudo code. The Sphinx body will
be exactly the same as
<a href="#SPHINXSPEC" class="xref">the section called “References”</a>
Our basic KEM API has three functions:

<div class="itemizedlist">

- `PRIV_KEY, PUB_KEY = GEN_KEYPAIR(RNG)`

- `ct, ss = ENCAP(PUB_KEY)` - Encapsulate generates a shared secret, ss,
  for the public key and encapsulates it into a ciphertext.

- `ss = DECAP(PRIV_KEY, ct)` - Decapsulate computes the shared key, ss,
  encapsulated in the ciphertext, ct, for the private key.

</div>

Additional notation includes:

<div class="itemizedlist">

- `||` = concatenate two binary blobs together

- `PRF` = pseudo random function, a cryptographic hash function,
  e.g. `Blake2b`.

</div>

Therefore we must embed these KEM ciphertexts in the KEMSphinx header,
one KEM ciphertext per mix hop.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="post-quantum-hybrid-kem"></span>2. Post Quantum Hybrid KEM

</div>

</div>

</div>

Special care must be taken in order correctly compose a hybrid post
quantum KEM that is IND-CCA2 robust.

The hybrid post quantum KEMs found in Cloudflare’s circl library are
suitable to be used with Noise or TLS but not with KEM Sphinx because
they are not IND-CCA2 robust. Noise and TLS achieve IND-CCA2 security by
mixing in the public keys and ciphertexts into the hash object and
therefore do not require an IND-CCA2 KEM.

Firstly, our post quantum KEM is IND-CCA2 however we must specifically
take care to make our NIKE to KEM adapter have semantic security.
Secondly, we must make a security preserving KEM combiner.

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="nike-to-kem-adapter"></span>2.1 NIKE to KEM adapter

</div>

</div>

</div>

We easily achieve our IND-CCA2 security by means of hashing together the
DH shared secret along with both of the public keys:

``` programlisting
func ENCAPSULATE(their_pubkey publickey) ([]byte, []byte) {
my_privkey, my_pubkey = GEN_KEYPAIR(RNG)
ss = DH(my_privkey, their_pubkey)
ss2 = PRF(ss || their_pubkey || my_pubkey)
return my_pubkey, ss2
}

func DECAPSULATE(my_privkey, their_pubkey) []byte {
s = DH(my_privkey, their_pubkey)
shared_key = PRF(ss || my_pubkey || their_pubkey)
return shared_key
}
```

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

### <span id="kem-combiner"></span>2.2 KEM Combiner

</div>

</div>

</div>

The KEM Combiners paper <a href="#KEMCOMB" class="link">???</a> makes
the observation that if a KEM combiner is not security preserving then
the resulting hybrid KEM will not have IND-CCA2 security if one of the
composing KEMs does not have IND-CCA2 security. Likewise the paper
points out that when using a security preserving KEM combiner, if only
one of the composing KEMs has IND-CCA2 security then the resulting
hybrid KEM will have IND-CCA2 security.

Our KEM combiner uses the split PRF design from the paper when combining
two KEM shared secrets together we use a hash function to also mix in
the values of both KEM ciphertexts. In this pseudo code example we are
hashing together the two shared secrets from the two underlying KEMs,
ss1 and ss2. Additionally the two ciphertexts from the underlying KEMs,
cct1 and cct2, are also hashed together:

``` programlisting
func SplitPRF(ss1, ss2, cct1, cct2 []byte) []byte {
cct := cct1 || cct2
return PRF(ss1 || cct) XOR PRF(ss2 || cct)
}
```

Which simplifies to:

``` programlisting
SplitPRF := PRF(ss1 || cct2) XOR PRF(ss2 || cct1)
```

The Split PRF can be used to combine an arbitrary number of KEMs. Here’s
what it looks like with three KEMs:

``` programlisting
func SplitPRF(ss1, ss2, ss3, cct1, cct2, cct3 []byte) []byte {
cct := cct1 || cct2 || cct3
return PRF(ss1 || cct) XOR PRF(ss2 || cct) XOR PRF(ss3 || cct)
}
```

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="kemsphinx-header-design"></span>3. KEMSphinx Header Design

</div>

</div>

</div>

NIKE Sphinx header elements:

<div class="orderedlist">

1.  Version number (MACed but not encrypted)

2.  Group element

3.  Encrypted per routing commands

4.  MAC for this hop (authenticates header fields 1 thru 4)

</div>

KEM Sphinx header elements:

<div class="orderedlist">

1.  Version number (MACed but not encrypted)

2.  One KEM ciphertext for use with the next hop

3.  Encrypted per routing commands AND KEM ciphertexts, one for each
    additional hop

4.  MAC for this hop (authenticates header fields 1 thru 4)

</div>

We can say that KEMSphinx differs from NIKE Sphinx by replacing the
header’s group element (e.g. an X25519 public key) field with the KEM
ciphertext. Subsequent KEM ciphertexts for each hop are stored inside
the Sphinx header <span class="quote">“<span class="quote">routing
information</span>”</span> section.

First we must have a data type to express a mix hop, and we can use
lists of these hops to express a route:

``` programlisting
type PathHop struct {
public_key kem.PublicKey
routing_commands Commands
}
```

Here’s how we construct a KEMSphinx packet header where path is a list
of PathHop, and indicates the route through the network:

<div class="orderedlist">

1.  Derive the KEM ciphertexts for each hop.

</div>

``` programlisting
route_keys = []
route_kems = []
for i := 0; i < num_hops; i++ {
kem_ct, ss := ENCAP(path[i].public_key)
route_kems += kem_ct
route_keys += ss
}
```

<div class="orderedlist">

1.  Derive the routing_information keystream and encrypted padding for
    each hop.

</div>

Same as in
<a href="#SPHINXSPEC" class="xref">the section called “References”</a>
except for the fact that each routing info slot is now increased by the
size of the KEM ciphertext.

<div class="orderedlist">

1.  Create the routing_information block.

</div>

Here we modify the Sphinx implementation to pack the next KEM ciphertext
into each routing information block. Each of these blocks is decrypted
for each mix mix hop which will decrypt the KEM ciphertext for the next
hop in the route.

<div class="orderedlist">

1.  Assemble the completed Sphinx Packet Header and Sphinx Packet
    Payload SPRP key vector. Same as in
    <a href="#SPHINXSPEC" class="link">SPHINXSPEC</a> except the
    `kem_element` field is set to the first KEM ciphertext,
    `route_kems[0]`:

</div>

``` programlisting
var sphinx_header SphinxHeader
sphinx_header.additional_data = version
sphinx_header.kem_element = route_kems[0]
sphinx_header.routing_info = routing_info
sphinx_header.mac = mac
```

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="kemsphinx-unwrap-operation"></span>4. KEMSphinx Unwrap Operation

</div>

</div>

</div>

Most of the design here will be exactly the same as in
<a href="#SPHINXSPEC" class="link">SPHINXSPEC</a>. However there are a
few notable differences:

<div class="orderedlist">

1.  The shared secret is derived from the KEM ciphertext instead of a
    DH.

2.  Next hop’s KEM ciphertext stored in the encrypted routing
    information.

</div>

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="acknowledgments"></span>Acknowledgments

</div>

</div>

</div>

I would like to thank Peter Schwabe for the original idea of simply
replacing the Sphinx NIKE with a KEM and for answering all my questions.
I’d also like to thank Bas Westerbaan for answering questions.

</div>

<div class="section">

<div class="titlepage">

<div>

<div>

## <span id="appendix-a.-references"></span>References

</div>

</div>

</div>

<span id="KEMCOMB"></span><span class="bold">**KEMCOMB**</span>

Federico Giacon, Felix Heuer, Bertram Poettering,
<span class="quote">“<span class="quote">KEM Combiners</span>”</span>,
2018,
<a href="https://link.springer.com/chapter/10.1007/978-3-319-76578-5_7"
class="link"
target="_top">https://link.springer.com/chapter/10.1007/978-3-319-76578-5_7</a>

<span id="SPHINX09"></span><span class="bold">**SPHINX09**</span>

Danezis, G., Goldberg, I.,
<span class="quote">“<span class="quote">Sphinx: A Compact and Provably
Secure Mix Format</span>”</span>, DOI 10.1109/SP.2009.15, May 2009,
<a href="https://cypherpunks.ca/~iang/pubs/Sphinx_Oakland09.pdf"
class="link"
target="_top">https://cypherpunks.ca/~iang/pubs/Sphinx_Oakland09.pdf</a>.

<span id="SPHINXSPEC"></span><span class="bold">**SPHINXSPEC**</span>

Angel, Y., Danezis, G., Diaz, C., Piotrowska, A., Stainton, D.,
<span class="quote">“<span class="quote">Sphinx Mix Network
Cryptographic Packet Format Specification</span>”</span>, July 2017,
<a href="https://katzenpost.network/docs/specs/pdf/sphinx.pdf"
class="link"
target="_top">https://katzenpost.network/docs/specs/pdf/sphinx.pdf</a>.

</div>

</div>
