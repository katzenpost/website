// Generates and verifies PUBLIC TEST DATA against the exported Katzenpost tag.
// Run with fixture-consensus.sh, never with a host Go toolchain.
package main

import (
	"bytes"
	"crypto/ecdh"
	stded25519 "crypto/ed25519"
	"crypto/sha256"
	"encoding/binary"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"math"
	"os"
	"runtime"
	"time"

	"github.com/fxamacker/cbor/v2"
	"github.com/katzenpost/hpqc/hash"
	"github.com/katzenpost/hpqc/kem/adapter"
	nikeschemes "github.com/katzenpost/hpqc/nike/schemes"
	"github.com/katzenpost/hpqc/nike/x25519"
	hpqcrand "github.com/katzenpost/hpqc/rand"
	"github.com/katzenpost/hpqc/sign"
	"github.com/katzenpost/hpqc/sign/ed25519"
	"github.com/katzenpost/katzenpost/core/cert"
	"github.com/katzenpost/katzenpost/core/epochtime"
	"github.com/katzenpost/katzenpost/core/pki"
	"github.com/katzenpost/katzenpost/core/sphinx/geo"
)

const epoch uint64 = 1000000
const threshold = 2
const sourceCommit = "6f6b13d4524ec2da68ca3ba18fefe4a181af8a04"
const tagObject = "33b06e7e1b7f561c7dffc0cad135760ae3296b46"
const seedPrefix = "Katzenpost dirauth conformance fixture v1/"

func must(err error) {
	if err != nil {
		panic(err)
	}
}

func require(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func seed(label string) []byte {
	s := sha256.Sum256([]byte(seedPrefix + label))
	return s[:]
}

func hx(value []byte) string { return hex.EncodeToString(value) }

func marshal(value interface{ MarshalBinary() ([]byte, error) }) []byte {
	raw, err := value.MarshalBinary()
	must(err)
	return raw
}

// Generate actual public points, not arbitrary parser-sized byte strings.
func publicX25519(label string) []byte {
	key, err := ecdh.X25519().NewPrivateKey(seed(label))
	must(err)
	return key.PublicKey().Bytes()
}

func node(name, role string) *pki.MixDescriptor {
	identity, _ := ed25519.Scheme().DeriveKey(seed("node/" + name + "/identity"))
	d := &pki.MixDescriptor{
		Name: name, Epoch: epoch, IdentityKey: marshal(identity),
		LinkKey:   publicX25519("node/" + name + "/link"),
		MixKeys:   make(map[uint64][]byte),
		Addresses: map[string][]string{"tcp4": {"tcp://192.0.2.1:4242"}},
	}
	for e := epoch; e < epoch+3; e++ {
		d.MixKeys[e] = publicX25519(fmt.Sprintf("node/%s/sphinx/%d", name, e))
	}
	if role == "gateway" {
		d.IsGatewayNode = true
		d.AuthenticationType = pki.TrustOnFirstUseAuth
	}
	if role == "service" {
		d.IsServiceNode = true
		d.Kaetzchen = map[string]map[string]interface{}{"echo": {"endpoint": "+echo"}}
	}
	return d
}

func cloneEnvelope(raw []byte) *cert.Certificate {
	c := new(cert.Certificate)
	must(cbor.Unmarshal(raw, c))
	return c
}

func signatureInput(c *cert.Certificate) []byte {
	var input bytes.Buffer
	must(binary.Write(&input, binary.LittleEndian, c.Version))
	must(binary.Write(&input, binary.LittleEndian, c.Expiration))
	input.WriteString(c.KeyType)
	input.Write(c.Certified)
	return input.Bytes()
}

func replicaUpload(enc cbor.EncMode) map[string]interface{} {
	pub, priv := ed25519.Scheme().DeriveKey(seed("replica/identity"))
	envelopeScheme := nikeschemes.ByName("CTIDH1024-X25519")
	replicaEpoch := epoch * 1200 / 604800
	desc := &pki.ReplicaDescriptor{
		Name: "replica-1", Epoch: epoch, ReplicaID: 1,
		IdentityKey: marshal(pub), LinkKey: publicX25519("replica/link"),
		EnvelopeKeys: make(map[uint64][]byte),
		Addresses:    map[string][]string{"tcp": {"tcp://192.0.2.1:4243"}},
	}
	for e := replicaEpoch; e <= replicaEpoch+1; e++ {
		entropy, err := hpqcrand.NewDeterministicRandReader(seed(fmt.Sprintf("replica/envelope/%d", e)))
		must(err)
		key, private, err := envelopeScheme.GenerateKeyPairFromEntropy(entropy)
		must(err)
		desc.EnvelopeKeys[e] = marshal(key)
		private.Reset()
		_, err = envelopeScheme.UnmarshalBinaryPublicKey(desc.EnvelopeKeys[e])
		must(err)
	}
	must(pki.IsReplicaDescriptorWellFormed(desc, epoch))
	upload := &pki.SignedReplicaUpload{ReplicaDescriptor: desc}
	unsigned, err := upload.Marshal()
	must(err)
	must(upload.Sign(priv, pub))
	raw, err := upload.Marshal()
	must(err)
	parsed := new(pki.SignedReplicaUpload)
	must(parsed.Unmarshal(raw))
	require(parsed.Verify(pub), "signed replica upload failed verification")
	roundtrip, err := parsed.Marshal()
	must(err)
	require(bytes.Equal(raw, roundtrip), "replica upload round-trip differs")
	require(stded25519.Verify(stded25519.PublicKey(marshal(pub)), unsigned, upload.Signature.Payload),
		"independent replica signature verification failed")
	descriptor, err := desc.Marshal()
	must(err)
	var fields map[string]interface{}
	must(cbor.Unmarshal(descriptor, &fields))
	_, hasVersion := fields["Version"]
	require(!hasVersion, "replica descriptor unexpectedly contains Version")
	fields["Version"] = ""
	changed := map[string]interface{}{"Signature": nil, "ReplicaDescriptor": fields}
	changedInput, err := enc.Marshal(changed)
	must(err)
	signature := priv.Scheme().Sign(priv, changedInput, nil)
	require(stded25519.Verify(stded25519.PublicKey(marshal(pub)), changedInput, signature),
		"Version control is not correctly signed over its original bytes")
	changed["Signature"] = &cert.Signature{PublicKeySum256: hash.Sum256From(pub), Payload: signature}
	changedRaw, err := enc.Marshal(changed)
	must(err)
	changedParsed := new(pki.SignedReplicaUpload)
	must(changedParsed.Unmarshal(changedRaw))
	require(!changedParsed.Verify(pub), "replica Version control unexpectedly verified after typed decoding")
	return map[string]interface{}{
		"identity_public_key_hex": hx(marshal(pub)), "envelope_scheme": envelopeScheme.Name(),
		"replica_epochs":      []uint64{replicaEpoch, replicaEpoch + 1},
		"descriptor_cbor_hex": hx(descriptor), "signed_upload_cbor_hex": hx(raw),
		"signature_input_hex": hx(unsigned), "signature_hex": hx(upload.Signature.Payload),
		"version_control": map[string]interface{}{
			"signed_upload_cbor_hex": hx(changedRaw), "signature_input_hex": hx(changedInput),
			"original_signature_valid": true, "reference_decoded_signature_valid": false,
		},
		"verified": []string{"IsReplicaDescriptorWellFormed", "SignedReplicaUpload.Verify", "canonical round-trip", "CTIDH1024-X25519 public-key parsing", "standard-library Ed25519 verification"},
	}
}

func main() {
	period := 20 * time.Minute
	must(epochtime.Configure(&period, os.Stderr))
	now, _, _ := epochtime.Now()
	require(now < epoch+5, "fixture expired under the real clock; do not silently change its epoch")
	enc, err := cbor.CanonicalEncOptions().EncMode()
	must(err)
	verifiers := make([]sign.PublicKey, 3)
	private := make([]sign.PrivateKey, 3)
	authorities := make([]map[string]interface{}, 3)
	for i := range verifiers {
		label := fmt.Sprintf("authority/%d", i+1)
		verifiers[i], private[i] = ed25519.Scheme().DeriveKey(seed(label))
		keyHash := hash.Sum256From(verifiers[i])
		authorities[i] = map[string]interface{}{
			"label": label, "PUBLIC_TEST_seed_hex": hx(seed(label)),
			"public_key_hex": hx(marshal(verifiers[i])), "identity_blake2b256_hex": hx(keyHash[:]),
			"signs_fixture": i < threshold,
		}
	}

	nike := x25519.Scheme(nil)
	link := adapter.FromNIKE(nike)
	geometry := geo.GeometryFromUserForwardPayloadLength(nike, 1024, true, 5)
	must(geometry.Validate())
	geometryCBOR, err := enc.Marshal(geometry)
	must(err)
	geometryHash := geometry.Hash()
	computedGeometryHash := hash.Sum256(geometryCBOR)
	require(bytes.Equal(geometryHash, computedGeometryHash[:]), "geometry hash mismatch")
	srv := hash.Sum256([]byte(seedPrefix + "synthetic shared random value"))
	doc := &pki.Document{
		Epoch: epoch, GenesisEpoch: epoch,
		Mu: .001, LambdaP: .001, LambdaL: .0005, LambdaM: .0005, LambdaR: .02,
		LambdaG: 4 * math.Log(2) * .001,
		Topology: [][]*pki.MixDescriptor{
			{node("mix-1", "mix"), node("mix-2", "mix")},
			{node("mix-3", "mix"), node("mix-4", "mix")},
			{node("mix-5", "mix"), node("mix-6", "mix")},
		},
		GatewayNodes:      []*pki.MixDescriptor{node("gateway-1", "gateway")},
		ServiceNodes:      []*pki.MixDescriptor{node("service-1", "service")},
		StorageReplicas:   []*pki.ReplicaDescriptor{},
		SharedRandomValue: srv[:], WeeklySharedRandom: [][]byte{srv[:], srv[:]},
		SphinxGeometryHash: geometryHash, PKISignatureScheme: ed25519.Scheme().Name(),
		Version: pki.DocumentVersion,
	}
	must(pki.IsDocumentWellFormed(doc, verifiers))
	nodes := append(append([]*pki.MixDescriptor{}, doc.GatewayNodes...), doc.ServiceNodes...)
	for _, layer := range doc.Topology {
		nodes = append(nodes, layer...)
	}
	nodeRecords := make([]map[string]interface{}, 0, len(nodes))
	for _, d := range nodes {
		_, err = ed25519.Scheme().UnmarshalBinaryPublicKey(d.IdentityKey)
		must(err)
		_, err = link.UnmarshalBinaryPublicKey(d.LinkKey)
		must(err)
		for e := range d.MixKeys {
			_, err = d.UnmarshalMixKeyAsNike(e, geometry)
			must(err)
		}
		raw := marshal(d)
		keyHash := hash.Sum256(d.IdentityKey)
		nodeRecords = append(nodeRecords, map[string]interface{}{
			"name": d.Name, "identity_public_key_hex": hx(d.IdentityKey),
			"identity_blake2b256_hex": hx(keyHash[:]), "descriptor_cbor_hex": hx(raw),
		})
	}

	var envelope []byte
	for i := 0; i < threshold; i++ {
		envelope, err = pki.SignDocument(private[i], verifiers[i], doc)
		must(err)
	}
	body, good, bad, err := cert.VerifyThreshold(verifiers, threshold, envelope)
	must(err)
	require(len(good) == 2 && len(bad) == 1, "unexpected positive threshold counts")
	parsed, err := pki.ParseDocument(envelope)
	must(err)
	must(pki.IsDocumentWellFormed(parsed, verifiers))
	require(parsed.Epoch == epoch, "requested epoch mismatch")
	require(bytes.Equal(parsed.SphinxGeometryHash, geometryHash), "requested geometry mismatch")
	roundtrip, err := parsed.MarshalCertificate()
	must(err)
	require(bytes.Equal(roundtrip, envelope), "canonical envelope/body round-trip differs")
	c := cloneEnvelope(envelope)
	require(bytes.Equal(c.Certified, body), "verified body differs from envelope Certified")
	input := signatureInput(c)
	for i := 0; i < threshold; i++ {
		keyHash := hash.Sum256From(verifiers[i])
		signature := c.Signatures[keyHash]
		_, err = cert.Verify(verifiers[i], envelope)
		must(err)
		require(stded25519.Verify(stded25519.PublicKey(marshal(verifiers[i])), input, signature.Payload),
			"independent standard-library verification of signature input failed")
		authorities[i]["signature_hex"] = hx(signature.Payload)
	}

	controls := make([]map[string]interface{}, 0, 4)
	for _, kind := range []string{"invalid-signature", "insufficient-signatures", "changed-body", "changed-expiration"} {
		mutated := cloneEnvelope(envelope)
		keyHash := hash.Sum256From(verifiers[0])
		if kind == "invalid-signature" {
			signature := mutated.Signatures[keyHash]
			signature.Payload[0] ^= 1
			mutated.Signatures[keyHash] = signature
		} else if kind == "insufficient-signatures" {
			delete(mutated.Signatures, keyHash)
		} else if kind == "changed-body" {
			mutated.Certified[len(mutated.Certified)-1] ^= 1
		} else {
			mutated.Expiration++
		}
		raw, err := mutated.Marshal()
		must(err)
		_, individual := cert.Verify(verifiers[0], raw)
		if kind != "insufficient-signatures" {
			require(errors.Is(individual, cert.ErrBadSignature), "bad signature was not rejected")
		} else {
			require(errors.Is(individual, cert.ErrIdentitySignatureNotFound), "missing signature was not detected")
		}
		_, good, bad, err := cert.VerifyThreshold(verifiers, threshold, raw)
		require(errors.Is(err, cert.ErrThresholdNotMet), "negative control met threshold")
		expectedGood := 1
		if kind == "changed-body" || kind == "changed-expiration" {
			expectedGood = 0
		}
		require(len(good) == expectedGood && len(bad) == 3-expectedGood, "unexpected negative threshold counts")
		controls = append(controls, map[string]interface{}{
			"name": kind, "certificate_cbor_hex": hx(raw),
			"individual_verification_error": individual.Error(), "threshold_error": err.Error(),
			"valid_signers": len(good), "failed_or_absent_signers": len(bad),
		})
	}
	inputHash := hash.Sum256(input)
	bodyHash := hash.Sum256(body)
	envelopeHash := hash.Sum256(envelope)
	record := map[string]interface{}{
		"fixture_version": 3,
		"warning":         "PUBLIC DETERMINISTIC TEST KEYS. Never use these keys or this synthetic network in production.",
		"scope":           "Valid 2-of-3 Ed25519 certificate and well-formed consensus document, not a completed voting round, live network, PQ test, or full protocol conformance test.",
		"provenance": map[string]interface{}{
			"katzenpost_tag": "v0.0.107", "tag_object": tagObject, "source_commit": sourceCommit,
			"hpqc_version": "v0.0.93", "go_version": runtime.Version(),
			"seed_derivation": "SHA-256(UTF-8(\"" + seedPrefix + "\" + label)); all seeds are public test data",
		},
		"time": map[string]interface{}{
			"requested_epoch": epoch, "genesis_epoch": epoch, "expiration_epoch": epoch + 5,
			"epoch_period_seconds": 1200, "epoch_zero_utc": epochtime.Epoch.Format(time.RFC3339),
			"expires_utc": epochtime.Epoch.Add(time.Duration(epoch+5) * period).Format(time.RFC3339),
			"assumption":  "Uses the real clock; verification requires current epoch < expiration_epoch. The future requested epoch is checked against the document, not against a live authority state machine.",
		},
		"configuration": map[string]interface{}{
			"signature_scheme": ed25519.Scheme().Name(), "link_kem_scheme": link.Name(),
			"sphinx_nike_scheme": nike.Name(), "threshold": threshold,
			"fixed_layer_names": [][]string{{"mix-1", "mix-2"}, {"mix-3", "mix-4"}, {"mix-5", "mix-6"}},
			"note":              "Three layers of two mixes; one gateway; one echo service; no storage replicas. Documentation-only 192.0.2.1 addresses. SRV is synthetic, with genesis history [srv,srv]; no commit/reveal round was executed.",
		},
		"authorities": authorities, "nodes": nodeRecords, "geometry": geometry,
		"replica_upload":    replicaUpload(enc),
		"geometry_cbor_hex": hx(geometryCBOR), "geometry_blake2b256_hex": hx(geometryHash),
		"document_body_cbor_hex": hx(body), "document_body_blake2b256_hex": hx(bodyHash[:]),
		"certificate_cbor_hex": hx(envelope), "certificate_blake2b256_hex": hx(envelopeHash[:]),
		"signature_input": map[string]interface{}{
			"construction": "LE_uint32(Version) || LE_uint64(Expiration) || UTF8(KeyType) || Certified",
			"hex":          hx(input), "blake2b256_hex": hx(inputHash[:]),
		},
		"verified":          []string{"cert.VerifyThreshold: 2 valid of 3 configured authorities", "pki.ParseDocument", "pki.IsDocumentWellFormed", "requested epoch and local geometry equality", "canonical MarshalCertificate round-trip", "all descriptor identity/link/Sphinx public keys parse", "standard-library Ed25519 verification of reconstructed signature input"},
		"negative_controls": controls,
	}
	writer := json.NewEncoder(os.Stdout)
	writer.SetIndent("", "  ")
	must(writer.Encode(record))
	fmt.Fprintln(os.Stderr, "PASS: 2-of-3 consensus threshold, replica upload, key parsing, canonical round-trip, independent Ed25519 verification; four consensus controls and replica Version control rejected")
}
