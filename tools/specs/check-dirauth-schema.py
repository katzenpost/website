"""Check downloadable CDDL/ABNF against examples and deliberate shape errors.

Run in tools/specs/Containerfile. These checks cover formats and selected
deterministic behaviors, not signatures or complete protocol conformance.
"""
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import re
import struct
import subprocess
import tempfile

from abnf import Rule, ParseError
from cbor_examples import decode, encode

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / 'static/docs/specs/dirauth/dirauth.cddl'
WIRE = ROOT / 'static/docs/specs/dirauth/wire.abnf'
SPEC = ROOT / 'content/en/docs/specs/dirauth.md'
EPOCH = 245448


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def shared_random(epoch, reveals, previous):
    ordered = sorted(sorted(reveals.items()), key=lambda pair: pair[1], reverse=True)
    data = b'shared-random' + struct.pack('>Q', epoch)
    data += b''.join(identity + reveal for identity, reveal in ordered) + previous
    return hashlib.blake2b(data, digest_size=32).digest()


def fixture(role):
    desc = dict(Name=role, Epoch=EPOCH, IdentityKey=bytes([1])*32,
                LinkKey=bytes([2])*1216,
                MixKeys={EPOCH+i: bytes([3])*32 for i in range(3)},
                Addresses={'tcp4': ['tcp://127.0.0.1:1']}, Kaetzchen=None,
                KaetzchenAdvertizedData=None, IsGatewayNode=False,
                IsServiceNode=False, LoadWeight=0, AuthenticationType='', Version='')
    if role == 'gateway':
        desc.update(IsGatewayNode=True, AuthenticationType='tofu', IdentityKey=bytes([4])*32)
    if role == 'service':
        desc.update(IsServiceNode=True, Kaetzchen={'echo': {'endpoint': '+echo'}},
                    IdentityKey=bytes([5])*32)
    return desc


def main():
    text = SPEC.read_text()
    schema = SCHEMA.read_text()
    version = subprocess.run(['cddl'], capture_output=True, text=True)
    require('0.12.14' in version.stderr + version.stdout, 'unexpected CDDL version')
    count = 0
    with tempfile.TemporaryDirectory(prefix='dirauth-schema-') as directory:
        directory = Path(directory)
        def check(name, root, value, expected=True):
            nonlocal count
            grammar = directory / 'root.cddl'
            grammar.write_text('root = ' + root + '\n' + schema)
            data = directory / 'instance.cbor'
            data.write_bytes(encode(value))
            result = subprocess.run(['cddl', str(grammar), 'validate', str(data)],
                                    capture_output=True, text=True, timeout=30)
            require((result.returncode == 0) == expected,
                    f'{name}: unexpected verdict\n{result.stdout}\n{result.stderr}')
            count += 1

        mix, gateway, service = [fixture(role) for role in ['mix', 'gateway', 'service']]
        replica = dict(Name='replica', Epoch=EPOCH, IdentityKey=bytes([6])*32,
                       LinkKey=bytes([7])*1216, EnvelopeKeys={487: bytes([8])*160},
                       Addresses={'tcp': ['tcp://127.0.0.1:2']}, ReplicaID=1)
        sig = dict(PublicKeySum256=bytes(32), Payload=bytes(64))
        upload = dict(Signature=sig, MixDescriptor=encode(mix), LoopStats=None)
        replica_upload = dict(Signature=sig, ReplicaDescriptor=replica)
        rates = dict(Mu=.001, LambdaP=.001, LambdaL=.0005, LambdaM=.0005, LambdaR=.02)
        doc = dict(Epoch=EPOCH, GenesisEpoch=EPOCH, **rates, LambdaG=.002,
                   Topology=[[encode(mix)]], GatewayNodes=[encode(gateway)],
                   ServiceNodes=[encode(service)], StorageReplicas=[replica],
                   ConfiguredReplicaIDs=bytes([1]), ConfiguredReplicaIdentityKeys=[replica['IdentityKey']],
                   SharedRandomCommit=None, SharedRandomReveal=None,
                   SharedRandomValue=bytes(32), PriorSharedRandom=[bytes(32), bytes(32)],
                   SphinxGeometryHash=bytes(32), Version='v1', PKISignatureScheme='Ed25519')
        cert = dict(Version=0, Expiration=EPOCH+5, KeyType='Ed25519',
                    Certified=encode(doc), Signatures={bytes(32): sig})
        for name, root, value in [('mix', 'mix-descriptor', mix), ('gateway', 'mix-descriptor', gateway),
                                 ('service', 'mix-descriptor', service), ('replica', 'replica-descriptor', replica),
                                 ('upload', 'signed-upload', upload), ('replica-upload', 'signed-replica-upload', replica_upload),
                                 ('document', 'document', doc), ('certificate', 'certificate', cert),
                                 ('parameters', 'parameters', rates)]:
            check(name, root, value)
        # Signed input has an explicit null signature, never an omitted key.
        unsigned = deepcopy(upload)
        unsigned['Signature'] = None
        check('unsigned upload', 'signed-upload', unsigned)
        bad = deepcopy(upload)
        del bad['Signature']
        check('omitted signature', 'signed-upload', bad, False)
        bad = deepcopy(upload)
        bad['MixDescriptor'] = mix
        check('inline mix', 'signed-upload', bad, False)
        bad = deepcopy(replica_upload)
        bad['ReplicaDescriptor'] = encode(replica)
        check('wrapped replica', 'signed-replica-upload', bad, False)
        for key, value in [('Version', 'v2'), ('SphinxGeometryHash', bytes(31)),
                           ('GatewayNodes', None), ('Epoch', -1), ('Mu', 1)]:
            bad = deepcopy(doc)
            bad[key] = value
            check('bad document ' + key, 'document', bad, False)
        bad = deepcopy(doc)
        bad['UnknownField'] = 1
        check('unknown producer field', 'document', bad, False)
        for size in [0, 32, 33]:
            bad = deepcopy(mix)
            bad['Name'] = 'a' * size
            check('name boundary ' + str(size), 'mix-descriptor', bad, size == 32)
        for field, limit in [('SoftwareVersion', 128), ('ContactInfo', 256)]:
            for size in [0, limit, limit+1]:
                bad = deepcopy(mix)
                bad[field] = 'a' * size
                check(field + str(size), 'mix-descriptor', bad, size == limit)
        for size in [0, 31, 32, 64, 96, 97]:
            bad = deepcopy(mix)
            bad['QUICKeyHash'] = bytes(size)
            check('QUIC hash boundary ' + str(size), 'mix-descriptor', bad, size in [32, 64, 96])
        bad = deepcopy(cert)
        bad['Version'] = 1
        check('bad envelope version', 'certificate', bad, False)
        bad = deepcopy(cert)
        bad['Signatures'] = {bytes(31): sig}
        check('short signer hash', 'certificate', bad, False)
        for name, root, expected in [('GEOMETRY_CBOR', 'geometry', True), ('PARAMKEY', 'parameters', True),
                                      ('CERT_CBOR', 'certificate', True), ('SIGNEDUPLOAD_CBOR', 'signed-upload', True),
                                      ('BODY', 'document', False)]:
            match = re.search(rf'^{name}(?: \([^\n]*\))?\n([0-9a-f]+(?:\n[0-9a-f]+)*)', text, re.M)
            require(match is not None, 'missing conformance vector ' + name)
            raw = bytes.fromhex(match[1])
            value = decode(raw)
            require(encode(value) == raw, 'non-canonical vector ' + name)
            check('conformance ' + name, root, value, expected)
        signed = json.loads((SCHEMA.parent / 'conformance.json').read_text())
        require(signed['provenance']['source_commit'] == '6f6b13d4524ec2da68ca3ba18fefe4a181af8a04',
                'unexpected signed-fixture source')
        decoded = {}
        for field, root in [('certificate_cbor_hex', 'certificate'),
                            ('document_body_cbor_hex', 'document'), ('geometry_cbor_hex', 'geometry')]:
            raw = bytes.fromhex(signed[field])
            value = decode(raw)
            require(encode(value) == raw, 'non-canonical signed-fixture ' + field)
            check('signed-fixture ' + root, root, value)
            decoded[root] = value
        require(decoded['certificate']['Certified'] == bytes.fromhex(signed['document_body_cbor_hex']),
                'signed-fixture body differs from Certified')
        for field, digest in [('certificate_cbor_hex', 'certificate_blake2b256_hex'),
                              ('document_body_cbor_hex', 'document_body_blake2b256_hex'),
                              ('geometry_cbor_hex', 'geometry_blake2b256_hex')]:
            require(hashlib.blake2b(bytes.fromhex(signed[field]), digest_size=32).hexdigest() == signed[digest],
                    'signed-fixture hash differs: ' + field)
        envelope = decoded['certificate']
        signature_input = (struct.pack('<IQ', envelope['Version'], envelope['Expiration'])
                           + envelope['KeyType'].encode() + envelope['Certified'])
        require(signature_input.hex() == signed['signature_input']['hex'], 'signed-fixture signature input differs')
        for node in signed['nodes']:
            check('signed-fixture node ' + node['name'], 'mix-descriptor',
                  decode(bytes.fromhex(node['descriptor_cbor_hex'])))
            require(decode(bytes.fromhex(node['descriptor_cbor_hex']))['Version'] == '',
                    'fixture node must use the reference producer Version')
        for control in signed['negative_controls']:
            # Invalid signatures still have a valid envelope shape.
            check('signed-fixture control ' + control['name'], 'certificate',
                  decode(bytes.fromhex(control['certificate_cbor_hex'])))
        replica_record = signed['replica_upload']
        replica = decode(bytes.fromhex(replica_record['descriptor_cbor_hex']))
        upload = decode(bytes.fromhex(replica_record['signed_upload_cbor_hex']))
        check('signed replica descriptor', 'replica-descriptor', replica)
        check('signed replica upload', 'signed-replica-upload', upload)
        require(upload['ReplicaDescriptor'] == replica and 'Version' not in replica,
                'replica descriptor nesting or Version differs')
        upload['Signature'] = None
        require(encode(upload).hex() == replica_record['signature_input_hex'],
                'replica signature input differs')
        version_control = replica_record['version_control']
        changed = decode(bytes.fromhex(version_control['signed_upload_cbor_hex']))
        check('replica Version control', 'signed-replica-upload', changed, False)
        require(changed['ReplicaDescriptor']['Version'] == '' and
                version_control['original_signature_valid'] and
                not version_control['reference_decoded_signature_valid'],
                'replica Version control lost its meaning')
        changed['Signature'] = None
        require(encode(changed).hex() == version_control['signature_input_hex'],
                'replica Version control signature input differs')

        behavior = json.loads((SCHEMA.parent / 'behavior-vectors.json').read_text())
        require(behavior['source_commit'] == signed['provenance']['source_commit'],
                'behavior fixture source differs')
        require(len(behavior['rounds']) == 4, 'expected four round cases')
        for run in behavior['rounds']:
            epoch = run['epoch']
            history = [bytes.fromhex(value) for value in run['prior_history_hex']]
            if run['prior_consensus']:
                prior_envelope = decode(bytes.fromhex(run['prior_consensus_envelope_hex']))
                prior = decode(prior_envelope['Certified'])
                check(run['name'] + ' prior envelope', 'certificate', prior_envelope)
                check(run['name'] + ' prior body', 'document', prior)
                require(prior['Epoch'] == epoch-1 and prior['GenesisEpoch'] == epoch-100 and
                        prior['PriorSharedRandom'] == history and
                        prior['SharedRandomValue'].hex() == run['prior_srv_hex'] and
                        len(prior_envelope['Signatures']) == run['threshold'],
                        'prior consensus inputs differ')
            else:
                require(run['prior_consensus_envelope_hex'] == '' and history == [],
                        'genesis case has prior consensus input')
            documents = {}
            for stage, field in [('vote', 'vote_envelopes_hex'),
                                 ('certificate', 'voting_certificate_envelopes_hex'),
                                 ('consensus', 'consensus_envelope_hex')]:
                encoded_envelopes = run[field] if stage != 'consensus' else [run[field]]
                documents[stage] = []
                for encoded_envelope in encoded_envelopes:
                    envelope = decode(bytes.fromhex(encoded_envelope))
                    document = decode(envelope['Certified'])
                    require(encode(envelope).hex() == encoded_envelope and
                            encode(document) == envelope['Certified'], 'non-canonical round document')
                    check(run['name'] + ' ' + stage + ' envelope', 'certificate', envelope)
                    check(run['name'] + ' ' + stage + ' body', 'document', document)
                    require(document['Epoch'] == epoch and envelope['Expiration'] == epoch+5,
                            'round epoch differs')
                    require(document['GenesisEpoch'] == (epoch-100 if run['prior_consensus'] else epoch),
                            'round genesis differs')
                    documents[stage].append(document)
            for vote in documents['vote']:
                require(vote['SharedRandomValue'] == bytes(32) and
                        len(vote['SharedRandomCommit']) == 1 and vote['SharedRandomReveal'] is None and
                        vote['PriorSharedRandom'] == history, 'vote stage fields differ')
            for certificate in documents['certificate']:
                require(certificate['SharedRandomValue'] == bytes(32) and
                        len(certificate['SharedRandomCommit']) == 3 and
                        len(certificate['SharedRandomReveal']) == 3 and
                        certificate['PriorSharedRandom'] == history, 'certificate stage fields differ')
            certificate = documents['certificate'][0]
            reveals = {}
            for identity, raw in certificate['SharedRandomReveal'].items():
                reveal = decode(raw)['Certified']
                commit = decode(certificate['SharedRandomCommit'][identity])['Certified']
                require(reveal[:8] == struct.pack('>Q', epoch) and
                        commit == reveal[:8] + hashlib.blake2b(reveal, digest_size=32).digest(),
                        'round commit does not open')
                reveals[identity] = reveal
            previous = bytes.fromhex(run['prior_srv_hex']) if run['prior_consensus'] else bytes(32)
            srv = shared_random(epoch, reveals, previous)
            consensus = documents['consensus'][0]
            expected_history = ([srv, srv] if not run['prior_consensus'] else
                                [srv, history[0]] if epoch % 504 == 0 else history)
            require(consensus['SharedRandomCommit'] is None and consensus['SharedRandomReveal'] is None,
                    'consensus retained commit or reveal maps')
            require(consensus['SharedRandomValue'] == srv and srv.hex() == run['srv_hex'] and
                    consensus['PriorSharedRandom'] == expected_history and
                    encode(consensus).hex() == run['consensus_body_hex'], 'consensus or history bytes differ')

        reconciliation = behavior['reconciliation']
        require(len(reconciliation['cases']) == 3, 'expected three reconciliation cases')
        pairs = reconciliation['pairs']
        for case in reconciliation['cases']:
            validation = [item['passes_document_validation'] for item in case['certificates']]
            require(validation == ([True, True, True] if case['name'] == 'skip-excluded-certificate-author'
                                   else [True, True, False] if case['name'] == 'skip-excluded-cited-identity'
                                   else [False]), 'reconciliation admission scope differs')
            bad, commits, reveals = set(), {}, {}
            for certificate in sorted(case['certificates'], key=lambda item: item['author_hash_hex']):
                author = certificate['author_hash_hex']
                if author in bad:
                    continue
                for identity, label in sorted(certificate['entries'].items()):
                    if identity in bad:
                        continue
                    pair = pairs[label]
                    if not pair['commit_signature_valid'] or not pair['reveal_signature_valid']:
                        bad.add(author)
                        break
                    commit, reveal = pair['commit_envelope_hex'], pair['reveal_envelope_hex']
                    if identity in commits and commits[identity] != commit:
                        bad.add(identity)
                    commits.setdefault(identity, commit)
                    if identity in reveals and reveals[identity] != reveal:
                        bad.add(identity)
                    reveals.setdefault(identity, reveal)
            for identity in bad:
                commits.pop(identity, None)
                reveals.pop(identity, None)
            require(sorted(commits) == case['surviving_identity_hashes_hex'],
                    'reconciliation survivors differ: ' + case['name'])
            require(case['threshold_met'] == (len(commits) >= reconciliation['threshold']),
                    'reconciliation threshold differs')
            if case['threshold_met']:
                raw_reveals = {bytes.fromhex(identity): decode(bytes.fromhex(raw))['Certified']
                               for identity, raw in reveals.items()}
                require(shared_random(reconciliation['epoch'], raw_reveals, bytes(32)).hex() == case['srv_hex'],
                        'reconciliation SRV differs: ' + case['name'])
        print(f'CDDL: {count} positive/negative examples match; canonical vectors and signed-fixture hashes match')
        print('Tagged behavior vectors: four round/history cases and three reconciliation cases match')

    class WireRule(Rule):
        pass
    WireRule.load_grammar(WIRE.read_text())
    wire_count = 0
    def wire_check(root, raw, expected=True):
        nonlocal wire_count
        try:
            WireRule(root).parse_all(raw.decode('latin-1'))
            accepted = True
        except ParseError:
            accepted = False
        require(accepted == expected, root + ': unexpected ABNF verdict')
        wire_count += 1
    epoch = struct.pack('>Q', EPOCH)
    frame = lambda number, body: bytes([number, 0]) + struct.pack('>I', len(body)) + body
    wire_check('authority-command', frame(0, b''))
    wire_check('authority-command', frame(18, epoch))
    wire_check('authority-command', frame(18, epoch)[:-1], False)
    wire_check('authority-command', bytes([18, 1]) + frame(18, epoch)[2:], False)
    for number, low, high in [(21, 0, 4), (10, 0, 4), (23, 0, 7), (26, 8, 13), (30, 14, 19), (28, 20, 26)]:
        wire_check('authority-command', frame(number, bytes([low])))
        wire_check('authority-command', frame(number, bytes([high])))
        wire_check('authority-command', frame(number, bytes([high+1])), False)
    for number in [22, 25, 29, 27]:
        wire_check('authority-command', frame(number, epoch + bytes([42])*32 + b'payload'))
    wire_check('authority-command', frame(24, b''), False)  # reserved GetVote
    wire_check('gateway-command', frame(32, epoch) + bytes(10))
    wire_check('gateway-command', frame(31, bytes([0]) + struct.pack('>II', 0, 1) + b'gzip') + bytes(10))
    wire_check('transport-record', bytes(42))
    wire_check('transport-record', bytes(41), False)
    # Recompute hash/epoch values independently of the schema validator.
    def hexline(name):
        return bytes.fromhex(re.search(rf'^{name}\s+([0-9a-f]+)$', text, re.M)[1])
    reveal = epoch + hashlib.blake2b(hexline('RN'), digest_size=32).digest()
    require(reveal == hexline('REVEAL'), 'reveal vector mismatch')
    require(epoch + hashlib.blake2b(reveal, digest_size=32).digest() == hexline('COMMIT'), 'commit vector mismatch')
    print(f'ABNF: {wire_count} positive/negative wire examples match; commit/reveal hashes match')
    print('Scope: schemas and examples, not complete semantic or cryptographic conformance')


if __name__ == '__main__':
    main()
    subprocess.run(["python3", str(ROOT / "tools/specs/check-dirauth-arithmetic.py")], check=True)
