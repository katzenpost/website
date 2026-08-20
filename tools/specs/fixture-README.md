# Directory fixtures

[conformance.json](../../static/docs/specs/dirauth/conformance.json) contains a
signed consensus and a separate signed replica upload. All private seeds are
**public test data**. Never deploy these keys or the synthetic network.

The consensus has two Ed25519 signatures from three test authorities. It has
three layers of two mixes, one gateway, one echo service, and no replicas.
Node identity keys use Ed25519. Link and Sphinx keys use actual X25519 points.
MixDescriptor Version is empty, as the reference producer emits it.
Addresses use the documentation address 192.0.2.1.

The separate replica upload omits Version. Its envelope keys use actual
CTIDH1024-X25519 points for the current and next replica epochs. The generator
checks the descriptor, signature, key parsers, and canonical round-trip.
An Ed25519 verifier from the Go standard library also checks the signature.

A negative replica control adds Version and signs the resulting bytes correctly.
The reference decoder removes that unknown field. The signature then fails when
the reference verifier reconstructs the upload. Both signature inputs and
complete uploads appear in the JSON.

Hex strings encode bytes. Letter case has no protocol significance.

The receiver tests check 16 normalization cases against the pinned CBOR library.
They cover time tags, bignums, unknown tags, scalar map reuse, and time bounds.
Twelve upload cases also check bare and tagged null and undefined.
They check pointer allocation, canonical bytes, and signature acceptance.

## Reproduce

Run the wrapper from the website repository:

```sh
tools/specs/fixture-consensus.sh /tmp/conformance.json /tmp/behavior-vectors.json
cmp /tmp/conformance.json static/docs/specs/dirauth/conformance.json
cmp /tmp/behavior-vectors.json static/docs/specs/dirauth/behavior-vectors.json
```

The wrapper verifies the local v0.0.107 tag object
`33b06e7e1b7f561c7dffc0cad135760ae3296b46` and its source commit
`6f6b13d4524ec2da68ca3ba18fefe4a181af8a04`. It exports that commit into a
temporary directory. It never builds the sibling working tree.

Go runs only inside Podman. The container has no network access. It mounts the
module cache read-only and gives the build cache a disposable overlay. The default
image is `localhost/kno-build-debian13-go1.26.10:latest`. It supplies Go 1.26.10
and the C compiler required by the tagged dependencies.

The module cache must contain the dependencies from the tag, including hpqc
v0.0.93. The wrapper downloads and installs nothing. Default cache paths are
`$HOME/.cache/katzenpost/kno/{gomodcache,gobuild}`. The default source checkout is
the sibling `katzenpost` repository. Overrides are `KATZENPOST_SOURCE`,
`KATZENPOST_GOMODCACHE`, `KATZENPOST_GOCACHE`, and `FIXTURE_IMAGE`.
A different Go version changes the JSON provenance field.

Without output arguments, the wrapper replaces both published files after
all checks pass. It runs each generator twice and requires identical output.

## Document checks

The generator calls the tagged `pki.SignDocument`, `cert.VerifyThreshold`,
`pki.ParseDocument`, and `pki.IsDocumentWellFormed`. It checks the requested
epoch, geometry, node key parsers, and exact canonical round-trip.
The standard-library Ed25519 verifier checks the reconstructed signature input:

```text
LE_uint32(Version) || LE_uint64(Expiration) || UTF8(KeyType) || Certified
```

Four complete consensus controls must fail threshold verification:

- A changed signature produces `cert.ErrBadSignature` for its signer.
- A removed signature produces `cert.ErrIdentitySignatureNotFound`.
- A changed body invalidates both signatures.
- A changed expiration invalidates both signatures.

The first two controls retain one valid signer. The other two retain none.
The JSON records all individual and threshold results.

## Tagged behavior checks

[behavior-vectors.json](../../static/docs/specs/dirauth/behavior-vectors.json)
contains outputs from the tagged authority methods. The wrapper copies
`fixture-state_test.go` into its temporary source export to call those methods.
It does not change an implementation function.

Four cases cover vote, voting-certificate, and consensus construction:

- Genesis at ordinary epoch 1000439.
- Existing history at ordinary epoch 1000439.
- Existing history at epoch 1000440, which is divisible by 504.
- Genesis at epoch 1000440, where initialization takes precedence over rotation.

Each case uses three authorities and a fixed topology. Actual upload handlers
accept the votes, reveals, and voting certificates. Each authority constructs
the same consensus body. The helper attaches two signatures and verifies the
threshold. Prior documents, when present, are well formed and threshold-signed.
The JSON includes complete envelopes, history inputs, SRV, and resulting bytes.

Three additional cases call `verifyCommits` directly. They distinguish an
excluded certificate author, an excluded cited identity, and retention of
previous pairs when processing stops at an invalid entry. The first case uses
individually well-formed certificates. The other two exercise defensive branches
with internal inputs that upload validation rejects. They do not claim that
those inputs enter storage through the network.

The schema checker independently decodes the vectors and checks stage fields,
commit openings, SRV bytes, history rules, and reconciliation results.
Signature checks run in the tagged Go generator.

## Time and scope

The document fixture uses epoch 1000000 and expires at epoch 1000005, on
2055-06-10 at 23:00 UTC. Epoch duration is 1200 seconds. The generators use the
real clock and fail after fixture expiration. They do not change the epoch or
freeze time. A live authority applies additional epoch and phase gates.

These checks use direct method calls. They do not run timers, a transport
session, disk publication, or a mixed-implementation network. They do not prove
complete protocol conformance. The consensus signatures use Ed25519, so these
checks do not exercise the hybrid signature scheme.

The conformance consensus uses a synthetic SRV. The behavior fixtures derive
each SRV through the tagged round methods.

Set `FIXTURE_SOURCE_TESTS=1` to run the tagged authority, PKI, certificate, and
wire tests before generation. This also checks the hpqc combiner and hybrid
signature packages. Their test vectors require a separate hpqc v0.0.93 export.
`HPQC_SOURCE` selects that checkout, which defaults to the sibling `hpqc`
repository. All tests remain inside the offline container.
