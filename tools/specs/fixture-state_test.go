package server

import (
	"bytes"
	"crypto/ecdh"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"sort"
	"testing"

	"github.com/fxamacker/cbor/v2"
	"github.com/katzenpost/hpqc/hash"
	hpqcrand "github.com/katzenpost/hpqc/rand"
	"github.com/katzenpost/hpqc/sign"
	"github.com/katzenpost/hpqc/sign/ed25519"
	"github.com/katzenpost/katzenpost/authority/voting/server/config"
	"github.com/katzenpost/katzenpost/core/cert"
	"github.com/katzenpost/katzenpost/core/epochtime"
	"github.com/katzenpost/katzenpost/core/log"
	"github.com/katzenpost/katzenpost/core/pki"
	"github.com/katzenpost/katzenpost/core/sphinx/geo"
	"github.com/katzenpost/katzenpost/core/wire/commands"
	"github.com/katzenpost/katzenpost/loops"
	"github.com/stretchr/testify/require"
)

type fixtureIdentity struct {
	pub  sign.PublicKey
	priv sign.PrivateKey
	id   [32]byte
	seed []byte
}

type fixturePair struct {
	commit []byte
	reveal []byte
}

func TestDirauthReceiverNormalization(t *testing.T) {
	enc, err := cbor.CanonicalEncOptions().EncMode()
	if err != nil {
		t.Fatal(err)
	}
	cases := []struct {
		input, want string
		destination func() any
	}{
		{"c1f93e00", "01", nil},
		{"c1f9b800", "20", nil},
		{"c1fbbddb7cdfd9d7bdbb", "00", nil},
		{"c074303030312d30312d30315430303a30303a30305a", "f6", nil},
		{"c1f97e00", "f6", nil},
		{"c1f97c00", "f6", nil},
		{"c1f9fc00", "f6", nil},
		{"c11b7fffffffffffffff", "1b7fffffffffffffff", nil},
		{"c11b8000000000000000", "", nil},
		{"c1fb43e0000000000001", "", nil},
		{"c1fbc3e0000000000000", "3b7fffffffffffffff", nil},
		{"c24101", "01", nil},
		{"d903e8f7", "d903e8f6", nil},
		{"a2054161f64162", "a1054162", func() any { return new(map[uint64][]byte) }},
		{"a2054161f74162", "a1054162", func() any { return new(map[uint64][]byte) }},
		{"a26161f93c006162f6", "a26161f93c006162f93c00", func() any { return new(map[string]float64) }},
	}
	for _, tc := range cases {
		t.Run(tc.input, func(t *testing.T) {
			raw, err := hex.DecodeString(tc.input)
			if err != nil {
				t.Fatal(err)
			}
			var value any
			destination := any(&value)
			if tc.destination != nil {
				destination = tc.destination()
			}
			err = cbor.Unmarshal(raw, destination)
			if tc.want == "" {
				if err == nil {
					t.Fatal("expected rejection")
				}
				return
			}
			if err != nil {
				t.Fatal(err)
			}
			encoded, err := enc.Marshal(destination)
			if err != nil {
				t.Fatal(err)
			}
			if got := hex.EncodeToString(encoded); got != tc.want {
				t.Fatalf("canonical encoding %s, want %s", got, tc.want)
			}
		})
	}
}

func TestDirauthReceiverTaggedNullUpload(t *testing.T) {
	pub, priv := ed25519.Scheme().DeriveKey(fixtureSeed("upload/identity"))
	identity, err := pub.MarshalBinary()
	require.NoError(t, err)
	link, err := ecdh.X25519().NewPrivateKey(fixtureSeed("upload/link"))
	require.NoError(t, err)
	mix, err := ecdh.X25519().NewPrivateKey(fixtureSeed("upload/sphinx"))
	require.NoError(t, err)
	const epoch = 1000000
	descriptor := &pki.MixDescriptor{
		Name: "test-node", Epoch: epoch, IdentityKey: identity,
		LinkKey: link.PublicKey().Bytes(), MixKeys: map[uint64][]byte{epoch: mix.PublicKey().Bytes()},
		Addresses: map[string][]string{"tcp4": {"tcp://192.0.2.1:4242"}},
	}
	require.NoError(t, pki.IsDescriptorWellFormed(descriptor, epoch))
	enc, err := cbor.CanonicalEncOptions().EncMode()
	require.NoError(t, err)
	cases := []struct {
		input      string
		nilPointer bool
	}{
		{"f6", true},
		{"f7", true},
		{"d903e8f6", false},
		{"d9d9f7f6", false},
		{"d903e8f7", false},
		{"d9d9f7f7", false},
	}
	for _, signedNil := range []bool{false, true} {
		upload := &pki.SignedUpload{MixDescriptor: descriptor}
		if !signedNil {
			upload.LoopStats = &loops.LoopStats{}
		}
		require.NoError(t, upload.Sign(priv, pub))
		require.True(t, upload.Verify(pub))
		raw, err := upload.Marshal()
		require.NoError(t, err)
		var fields map[string]cbor.RawMessage
		require.NoError(t, cbor.Unmarshal(raw, &fields))
		for _, tc := range cases {
			t.Run(fmt.Sprintf("signed_nil=%t/%s", signedNil, tc.input), func(t *testing.T) {
				input, err := hex.DecodeString(tc.input)
				require.NoError(t, err)
				fields["LoopStats"] = cbor.RawMessage(input)
				wire, err := enc.Marshal(fields)
				require.NoError(t, err)
				decoded := new(pki.SignedUpload)
				require.NoError(t, decoded.Unmarshal(wire))
				require.NoError(t, pki.IsDescriptorWellFormed(decoded.MixDescriptor, epoch))
				require.Equal(t, tc.nilPointer, decoded.LoopStats == nil)
				canonical, err := enc.Marshal(decoded.LoopStats)
				require.NoError(t, err)
				want := "f6"
				if !tc.nilPointer {
					want = "a36545706f6368006d5365676d656e74526174696f73f66f4d69784964656e7469747948617368f6"
				}
				require.Equal(t, want, hex.EncodeToString(canonical))
				require.Equal(t, signedNil == tc.nilPointer, decoded.Verify(pub))
			})
		}
	}
}

func fixtureSeed(label string) []byte {
	value := sha256.Sum256([]byte("Katzenpost dirauth behavior fixture v1/" + label))
	return value[:]
}

func fixtureIdentities(n int) []fixtureIdentity {
	keys := make([]fixtureIdentity, n)
	for i := range keys {
		seed := fixtureSeed(fmt.Sprintf("authority/%d", i))
		pub, priv := ed25519.Scheme().DeriveKey(seed)
		keys[i] = fixtureIdentity{pub, priv, hash.Sum256From(pub), seed}
	}
	sort.Slice(keys, func(i, j int) bool { return bytes.Compare(keys[i].id[:], keys[j].id[:]) < 0 })
	return keys
}

func fixtureHex(raw []byte) string { return hex.EncodeToString(raw) }

func fixtureState(t *testing.T, epoch uint64, keys []fixtureIdentity, owner int, template *pki.Document, geometry *geo.Geometry) *state {
	t.Helper()
	lb, err := log.New("", "ERROR", true)
	require.NoError(t, err)
	t.Cleanup(func() { _ = lb.Close() })
	params := &config.Parameters{Mu: template.Mu, LambdaP: template.LambdaP, LambdaL: template.LambdaL, LambdaM: template.LambdaM, LambdaR: template.LambdaR}
	cfg := &config.Config{
		Server: &config.Server{PKISignatureScheme: "Ed25519"}, Parameters: params,
		Debug:        &config.Debug{Layers: len(template.Topology), MinNodesPerLayer: 1},
		Topology:     &config.Topology{Layers: make([]config.Layer, len(template.Topology))},
		GatewayNodes: make([]*config.Node, len(template.GatewayNodes)),
		Notice:       config.Notice{MinClientVersion: "0.1", ClientNotice: "Public fixture"},
	}
	st := &state{
		s:   &Server{cfg: cfg, identityPublicKey: keys[owner].pub, identityPrivateKey: keys[owner].priv, logBackend: lb},
		geo: geometry, log: lb.GetLogger("fixture"), votingEpoch: epoch, state: stateAcceptVote,
		documents: make(map[uint64]*pki.Document), myconsensus: make(map[uint64]*pki.Document),
		descriptors:        map[uint64]map[[32]byte]*pki.MixDescriptor{epoch: {}},
		replicaDescriptors: make(map[uint64]map[[32]byte]*pki.ReplicaDescriptor),
		votes:              map[uint64]map[[32]byte]*pki.Document{epoch: {}},
		certificates:       map[uint64]map[[32]byte]*pki.Document{epoch: {}},
		commits:            map[uint64]map[[32]byte][]byte{epoch: {}},
		reveals:            map[uint64]map[[32]byte][]byte{epoch: {}},
		signatures:         make(map[uint64]map[[32]byte]*cert.Signature),
		verifiers:          make(map[[32]byte]sign.PublicKey), reverseHash: make(map[[32]byte]sign.PublicKey),
		authorizedAuthorities: make(map[[32]byte]bool), authorityNames: make(map[[32]byte]string),
		authorizedMixes: make(map[[32]byte]string), authorizedGatewayNodes: make(map[[32]byte]string),
		authorizedServiceNodes: make(map[[32]byte]string), authorizedReplicaNodes: make(map[[32]byte]*authorizedReplicaInfo),
		weeklySRV: make([][]byte, 0), fixedTopology: make([][][32]byte, len(template.Topology)),
	}
	st.s.log = st.log
	st.threshold, st.dissenters = votingThresholds(len(keys))
	for i, key := range keys {
		st.verifiers[key.id], st.reverseHash[key.id] = key.pub, key.pub
		st.authorizedAuthorities[key.id] = true
		st.authorityNames[key.id] = fmt.Sprintf("authority-%d", i)
	}
	nodes := append(append([]*pki.MixDescriptor{}, template.GatewayNodes...), template.ServiceNodes...)
	for layer, descs := range template.Topology {
		cfg.Topology.Layers[layer].Nodes = make([]config.Node, len(descs))
		for _, desc := range descs {
			st.fixedTopology[layer] = append(st.fixedTopology[layer], hash.Sum256(desc.IdentityKey))
			nodes = append(nodes, desc)
		}
	}
	for _, original := range nodes {
		desc := *original
		desc.Epoch = epoch
		desc.MixKeys = map[uint64][]byte{epoch: original.MixKeys[original.Epoch], epoch + 1: original.MixKeys[original.Epoch+1], epoch + 2: original.MixKeys[original.Epoch+2]}
		id := hash.Sum256(desc.IdentityKey)
		st.descriptors[epoch][id] = &desc
		switch {
		case desc.IsGatewayNode:
			st.authorizedGatewayNodes[id] = desc.Name
		case desc.IsServiceNode:
			st.authorizedServiceNodes[id] = desc.Name
		default:
			st.authorizedMixes[id] = desc.Name
		}
	}
	return st
}

func fixtureEnvelope(t *testing.T, doc *pki.Document) string {
	raw, err := doc.MarshalCertificate()
	require.NoError(t, err)
	return fixtureHex(raw)
}

func fixtureRound(t *testing.T, name string, epoch uint64, prior bool, keys []fixtureIdentity, template *pki.Document, geometry *geo.Geometry) map[string]interface{} {
	t.Helper()
	entropy, err := hpqcrand.NewDeterministicRandReader(fixtureSeed(name))
	require.NoError(t, err)
	oldReader := hpqcrand.Reader
	hpqcrand.Reader = entropy
	defer func() { hpqcrand.Reader = oldReader }()
	oldFirst, oldSecond, previous := fixtureSeed("history/first"), fixtureSeed("history/second"), fixtureSeed("previous/srv")
	var priorDocument *pki.Document
	priorEnvelope := ""
	if prior {
		builder := fixtureState(t, epoch-1, keys, 0, template, geometry)
		builder.genesisEpoch = epoch - 100
		builder.weeklySRV = [][]byte{oldFirst, oldSecond}
		descriptors := []*pki.MixDescriptor{}
		for _, descriptor := range builder.descriptors[epoch-1] {
			descriptors = append(descriptors, descriptor)
		}
		sortNodesByPublicKey(descriptors)
		priorDocument = builder.getDocument(descriptors, []*pki.ReplicaDescriptor{}, builder.s.cfg.Parameters, config.Notice{}, previous)
		require.NoError(t, pki.IsDocumentWellFormed(priorDocument, builder.getVerifiers()))
		for i := 0; i < builder.threshold; i++ {
			_, err := pki.SignDocument(keys[i].priv, keys[i].pub, priorDocument)
			require.NoError(t, err)
		}
		priorRaw, err := priorDocument.MarshalCertificate()
		require.NoError(t, err)
		_, _, _, err = cert.VerifyThreshold(builder.getVerifiers(), builder.threshold, priorRaw)
		require.NoError(t, err)
		priorEnvelope = fixtureHex(priorRaw)
	}
	states := make([]*state, len(keys))
	for i := range states {
		states[i] = fixtureState(t, epoch, keys, i, template, geometry)
		if prior {
			states[i].documents[epoch-1] = priorDocument
		}
	}
	votes := make([]string, len(keys))
	for i, st := range states {
		doc, err := st.getVote(epoch)
		require.NoError(t, err)
		votes[i] = fixtureEnvelope(t, doc)
	}
	for i, from := range states {
		raw, err := hex.DecodeString(votes[i])
		require.NoError(t, err)
		for j, to := range states {
			if i == j {
				continue
			}
			response := to.onVoteUpload(&commands.Vote{Epoch: epoch, PublicKey: from.s.identityPublicKey, Payload: raw}, keys[i].id[:]).(*commands.VoteStatus)
			require.Equal(t, uint8(commands.VoteOk), response.ErrorCode)
		}
	}
	for _, st := range states {
		st.state = stateAcceptReveal
	}
	reveals := make([]string, len(keys))
	for i, from := range states {
		raw := from.reveal(epoch)
		reveals[i] = fixtureHex(raw)
		for j, to := range states {
			if i == j {
				continue
			}
			response := to.onRevealUpload(&commands.Reveal{Epoch: epoch, PublicKey: from.s.identityPublicKey, Payload: raw}, keys[i].id[:]).(*commands.RevealStatus)
			require.Equal(t, uint8(commands.RevealOk), response.ErrorCode)
		}
	}
	certificates := make([]string, len(keys))
	for i, st := range states {
		st.Lock()
		doc, err := st.getCertificate(epoch)
		st.Unlock()
		require.NoError(t, err)
		certificates[i] = fixtureEnvelope(t, doc)
		st.state = stateAcceptCert
	}
	for i, from := range states {
		raw, err := hex.DecodeString(certificates[i])
		require.NoError(t, err)
		for j, to := range states {
			if i == j {
				continue
			}
			response := to.onCertUpload(&commands.Cert{Epoch: epoch, PublicKey: from.s.identityPublicKey, Payload: raw}, keys[i].id[:]).(*commands.CertStatus)
			require.Equal(t, uint8(commands.CertOk), response.ErrorCode)
		}
	}
	consensuses := make([]*pki.Document, len(keys))
	var firstBody []byte
	for i, st := range states {
		st.Lock()
		doc, err := st.getMyConsensus(epoch)
		st.Unlock()
		require.NoError(t, err)
		consensuses[i] = doc
		raw, err := doc.MarshalCertificate()
		require.NoError(t, err)
		body, err := cert.GetCertified(raw)
		require.NoError(t, err)
		if i == 0 {
			firstBody = body
		} else {
			require.Equal(t, firstBody, body)
		}
		expectedHistory := [][]byte{oldFirst, oldSecond}
		if !prior {
			expectedHistory = [][]byte{doc.SharedRandomValue, doc.SharedRandomValue}
		} else if epoch%504 == 0 {
			expectedHistory = [][]byte{doc.SharedRandomValue, oldFirst}
		}
		require.Equal(t, expectedHistory, doc.WeeklySharedRandom)
	}
	combined := consensuses[0]
	for i := 1; i < states[0].threshold; i++ {
		require.NoError(t, combined.AddSignature(keys[i].pub, consensuses[i].Signatures[keys[i].id]))
	}
	raw, err := combined.MarshalCertificate()
	require.NoError(t, err)
	_, good, _, err := cert.VerifyThreshold(states[0].getVerifiers(), states[0].threshold, raw)
	require.NoError(t, err)
	require.Len(t, good, states[0].threshold)
	history := []string{}
	if prior {
		history = []string{fixtureHex(oldFirst), fixtureHex(oldSecond)}
	}
	return map[string]interface{}{
		"name": name, "epoch": epoch, "prior_consensus": prior, "prior_history_hex": history,
		"prior_consensus_envelope_hex": priorEnvelope,
		"prior_srv_hex":                fixtureHex(previous), "vote_envelopes_hex": votes, "reveal_envelopes_hex": reveals,
		"voting_certificate_envelopes_hex": certificates, "consensus_envelope_hex": fixtureHex(raw),
		"consensus_body_hex": fixtureHex(firstBody), "threshold": states[0].threshold, "verified_signatures": len(good),
		"srv_hex": fixtureHex(combined.SharedRandomValue), "history_hex": []string{fixtureHex(combined.WeeklySharedRandom[0]), fixtureHex(combined.WeeklySharedRandom[1])},
	}
}

func fixtureReconciliation(t *testing.T, template *pki.Document, geometry *geo.Geometry) map[string]interface{} {
	const epoch uint64 = 1000440
	keys := fixtureIdentities(5)
	pairs := make(map[string]fixturePair)
	encoded := make(map[string]interface{})
	identities := make([]map[string]string, len(keys))
	for i, key := range keys {
		pub, err := key.pub.MarshalBinary()
		require.NoError(t, err)
		identities[i] = map[string]string{"identity_hash_hex": fixtureHex(key.id[:]), "public_key_hex": fixtureHex(pub), "PUBLIC_TEST_seed_hex": fixtureHex(key.seed)}
		for variant := 0; variant < 2; variant++ {
			label := fmt.Sprintf("%d-%d", i, variant)
			entropy, err := hpqcrand.NewDeterministicRandReader(fixtureSeed("pair/" + label))
			require.NoError(t, err)
			oldReader := hpqcrand.Reader
			hpqcrand.Reader = entropy
			random := new(pki.SharedRandom)
			commit, err := random.Commit(epoch)
			hpqcrand.Reader = oldReader
			require.NoError(t, err)
			signedCommit, err := cert.Sign(key.priv, key.pub, commit, epoch)
			require.NoError(t, err)
			signedReveal, err := cert.Sign(key.priv, key.pub, random.Reveal(), epoch)
			require.NoError(t, err)
			pairs[label] = fixturePair{signedCommit, signedReveal}
			_, err = cert.Verify(key.pub, signedCommit)
			require.NoError(t, err)
			_, err = cert.Verify(key.pub, signedReveal)
			require.NoError(t, err)
			encoded[label] = map[string]interface{}{"commit_envelope_hex": fixtureHex(signedCommit), "reveal_envelope_hex": fixtureHex(signedReveal), "identity_hash_hex": fixtureHex(key.id[:]), "commit_signature_valid": true, "reveal_signature_valid": true}
		}
	}
	for _, i := range []int{1, 2} {
		label := fmt.Sprintf("%d-invalid", i)
		original := pairs[fmt.Sprintf("%d-0", i)]
		malformed := new(cert.Certificate)
		require.NoError(t, cbor.Unmarshal(original.commit, malformed))
		signature := malformed.Signatures[keys[i].id]
		signature.Payload[0] ^= 1
		malformed.Signatures[keys[i].id] = signature
		bad, err := malformed.Marshal()
		require.NoError(t, err)
		pairs[label] = fixturePair{bad, original.reveal}
		_, err = cert.Verify(keys[i].pub, bad)
		require.ErrorIs(t, err, cert.ErrBadSignature)
		encoded[label] = map[string]interface{}{"commit_envelope_hex": fixtureHex(bad), "reveal_envelope_hex": fixtureHex(original.reveal), "identity_hash_hex": fixtureHex(keys[i].id[:]), "commit_signature_valid": false, "reveal_signature_valid": true}
	}
	base := func() map[int]string { return map[int]string{0: "0-0", 1: "1-0", 2: "2-0", 3: "3-0", 4: "4-0"} }
	record := func(name string, inputs map[int]map[int]string, expected []int) map[string]interface{} {
		st := fixtureState(t, epoch, keys, 0, template, geometry)
		st.genesisEpoch = epoch
		descriptors := []*pki.MixDescriptor{}
		for _, desc := range st.descriptors[epoch] {
			descriptors = append(descriptors, desc)
		}
		sortNodesByPublicKey(descriptors)
		docs := st.certificates[epoch]
		records := []map[string]interface{}{}
		authors := []int{}
		for author := range inputs {
			authors = append(authors, author)
		}
		sort.Ints(authors)
		for _, author := range authors {
			doc := st.getDocument(descriptors, []*pki.ReplicaDescriptor{}, st.s.cfg.Parameters, config.Notice{}, make([]byte, 32))
			doc.SharedRandomCommit, doc.SharedRandomReveal = make(map[[32]byte][]byte), make(map[[32]byte][]byte)
			entryNames := make(map[string]string)
			for identity, label := range inputs[author] {
				pair := pairs[label]
				doc.SharedRandomCommit[keys[identity].id], doc.SharedRandomReveal[keys[identity].id] = pair.commit, pair.reveal
				entryNames[fixtureHex(keys[identity].id[:])] = label
			}
			validation := pki.IsDocumentWellFormed(doc, st.getVerifiers())
			records = append(records, map[string]interface{}{"author_hash_hex": fixtureHex(keys[author].id[:]), "entries": entryNames, "passes_document_validation": validation == nil})
			docs[keys[author].id] = doc
		}
		st.Lock()
		commits, reveals := st.verifyCommits(epoch)
		st.Unlock()
		survivors := []string{}
		for _, identity := range sortedHashKeys(commits) {
			survivors = append(survivors, fixtureHex(identity[:]))
		}
		want := []string{}
		for _, i := range expected {
			want = append(want, fixtureHex(keys[i].id[:]))
		}
		require.Equal(t, want, survivors, name)
		result := map[string]interface{}{"name": name, "certificates": records, "surviving_identity_hashes_hex": survivors, "threshold_met": len(commits) >= st.threshold}
		if len(commits) >= st.threshold {
			srv, err := st.computeSharedRandom(epoch, commits, reveals)
			require.NoError(t, err)
			result["srv_hex"] = fixtureHex(srv)
		}
		return result
	}
	second, third := base(), base()
	second[2], third[2], third[3] = "2-1", "2-1", "3-1"
	skipAuthor := record("skip-excluded-certificate-author", map[int]map[int]string{0: base(), 1: second, 2: third}, []int{0, 1, 3, 4})
	badEntry := base()
	badEntry[2] = "2-invalid"
	skipEntry := record("skip-excluded-cited-identity", map[int]map[int]string{0: base(), 1: second, 3: badEntry}, []int{0, 1, 3, 4})
	stopRetain := record("stop-on-invalid-retain-earlier-pairs", map[int]map[int]string{3: {0: "0-0", 1: "1-invalid", 4: "4-0"}}, []int{0})
	return map[string]interface{}{"epoch": epoch, "threshold": 3, "authorities": identities, "pairs": encoded, "cases": []interface{}{skipAuthor, skipEntry, stopRetain},
		"scope": "Actual verifyCommits calls. The first case uses individually well-formed certificates. The other cases test defensive branches with internal inputs that document validation rejects before network storage."}
}

func TestDirauthBehaviorFixture(t *testing.T) {
	if os.Getenv("DIRAUTH_DOCUMENT_FIXTURE") == "" {
		t.Skip("Run the fixture-consensus.sh wrapper to generate these vectors")
	}
	var input struct {
		Certificate string `json:"certificate_cbor_hex"`
		Geometry    string `json:"geometry_cbor_hex"`
	}
	raw, err := os.ReadFile(os.Getenv("DIRAUTH_DOCUMENT_FIXTURE"))
	require.NoError(t, err)
	require.NoError(t, json.Unmarshal(raw, &input))
	certificate, err := hex.DecodeString(input.Certificate)
	require.NoError(t, err)
	template, err := pki.ParseDocument(certificate)
	require.NoError(t, err)
	geometryBytes, err := hex.DecodeString(input.Geometry)
	require.NoError(t, err)
	geometry := new(geo.Geometry)
	require.NoError(t, cbor.Unmarshal(geometryBytes, geometry))
	now, _, _ := epochtime.Now()
	require.Less(t, now, uint64(1000439), "behavior fixtures expired under the real clock")
	keys := fixtureIdentities(3)
	identities := make([]map[string]string, len(keys))
	for i, key := range keys {
		pub, err := key.pub.MarshalBinary()
		require.NoError(t, err)
		identities[i] = map[string]string{"identity_hash_hex": fixtureHex(key.id[:]), "public_key_hex": fixtureHex(pub), "PUBLIC_TEST_seed_hex": fixtureHex(key.seed)}
	}
	result := map[string]interface{}{
		"fixture_version": 1, "source_commit": "6f6b13d4524ec2da68ca3ba18fefe4a181af8a04",
		"warning":     "PUBLIC DETERMINISTIC TEST KEYS. Never deploy these keys.",
		"scope":       "Deterministic calls to the tagged vote, reveal, certificate, reconciliation and consensus methods. This is not a network run, transport test or mixed-implementation conformance test.",
		"authorities": identities, "rounds": []interface{}{
			fixtureRound(t, "genesis-ordinary", 1000439, false, keys, template, geometry),
			fixtureRound(t, "carried-ordinary", 1000439, true, keys, template, geometry),
			fixtureRound(t, "carried-504-boundary", 1000440, true, keys, template, geometry),
			fixtureRound(t, "genesis-504-boundary", 1000440, false, keys, template, geometry),
		},
		"reconciliation": fixtureReconciliation(t, template, geometry),
	}
	output, err := json.MarshalIndent(result, "", "  ")
	require.NoError(t, err)
	require.NoError(t, os.WriteFile(os.Getenv("DIRAUTH_BEHAVIOR_FIXTURE"), append(output, '\n'), 0600))
}
