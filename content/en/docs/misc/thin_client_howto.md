---
title:
linkTitle: "Thin Client How-to Guide"
description: "Task-oriented guides for using the Katzenpost thin client API"
categories: [""]
tags: [""]
author: ["David Stainton"]
version: 0
draft: false
slug: "/thin_client_howto/"
url: "docs/thin_client_howto/"
---

# Thin Client How-to Guide

This guide shows how to accomplish specific tasks with the Katzenpost
thin client. Each section is self-contained: find the task you need
and follow the steps.

If you are new to Pigeonhole, read
[Understanding Pigeonhole](/docs/pigeonhole_explained/) first for the
concepts, then return here for the recipes, and consult the
[Thin Client API Reference](/docs/thin_client_api_reference/) for the
precise signatures.

Throughout this guide and the API the words **channel** and **stream**
are used interchangeably: they denote one and the same thing.

## Authoritative working examples

A word of caution before you proceed. The code fragments in this guide
are illustrative: they are written to teach one task at a time, and to
keep the reader's eye on the matter at hand they omit imports, error
handling, and surrounding context. They are **not** compiled or run by
our continuous integration, and so, as the API evolves, an individual
snippet may fall out of step with it.

The integration tests below carry no such caveat. They are exercised on
every change by CI, so they are guaranteed to compile and to pass
against the code they accompany. When a fragment in this guide and a
test disagree, **the test is correct.** Treat these files as the
canonical, runnable companion to the prose:

| Language | Test file | Repository |
|----------|-----------|------------|
| Go | [`client/pigeonhole_docker_test.go`](https://github.com/katzenpost/katzenpost/blob/main/client/pigeonhole_docker_test.go) | katzenpost |
| Python | [`tests/test_new_pigeonhole_api.py`](https://github.com/katzenpost/thin_client/blob/main/tests/test_new_pigeonhole_api.py), [`tests/test_new_methods.py`](https://github.com/katzenpost/thin_client/blob/main/tests/test_new_methods.py) | thin_client |
| Rust | [`tests/channel_api_test.rs`](https://github.com/katzenpost/thin_client/blob/main/tests/channel_api_test.rs), [`tests/high_level_api_test.rs`](https://github.com/katzenpost/thin_client/blob/main/tests/high_level_api_test.rs) | thin_client |

These links track the `main` branch of each repository; should you be
working against a pinned release, consult the corresponding files at
that tag instead.

### Table of Contents

| Section | Description |
|---------|-------------|
| [Connect to the daemon and handle events](#how-to-connect-to-the-daemon-and-handle-events) | Establish a connection and process events |
| [Discover network services](#how-to-discover-network-services-via-the-pki-document) | Find services in the PKI document |
| [Verify the PKI document yourself](#how-to-verify-the-pki-document-yourself) | Check directory authority signatures against your own trust store |
| [Send a message to a mixnet service](#how-to-send-a-message-to-a-mixnet-service) | Echo ping and other non-Pigeonhole services |
| [Create a Pigeonhole channel](#how-to-create-a-pigeonhole-channel) | Generate a stream with write/read capabilities |
| [Write a message](#how-to-write-a-message-to-a-pigeonhole-channel) | Encrypt and send a write to a stream |
| [Read a message](#how-to-read-a-message-from-a-pigeonhole-channel) | Retrieve and decrypt a message from a stream |
| [Wait for a message not yet written](#how-to-wait-for-a-message-that-has-not-been-written-yet) | Poll with bounded retry around BoxIDNotFound |
| [Persist and restore channel state](#how-to-persist-and-restore-channel-state) | Survive a process restart without losing your place |
| [Hold a two-way conversation](#how-to-hold-a-two-way-conversation) | Wire two streams into a bidirectional channel |
| [Prepare operations offline](#how-to-prepare-operations-offline) | Do the local crypto now, transmit when connected |
| [A complete end-to-end example](#a-complete-end-to-end-example) | One runnable Alice-writes, Bob-reads program |
| [Delete messages with tombstones](#how-to-delete-messages-with-tombstones) | Tombstone one or more boxes |
| [Send to one channel atomically](#how-to-send-to-one-channel-atomically-via-copy-command) | Single-destination copy command |
| [Send to multiple channels atomically](#how-to-send-to-multiple-channels-atomically) | Multi-destination copy command |
| [Multi-call buffer passing](#how-to-handle-multi-call-buffer-passing-for-large-copy-streams) | Incremental copy streams with crash recovery |
| [Tombstone a range via copy stream](#how-to-tombstone-a-range-via-copy-stream) | Atomic tombstoning through a courier |
| [Cancel in-flight operations](#how-to-cancel-in-flight-operations) | Cancel individual operations or stop all at once |
| [Handle daemon disconnects](#how-to-handle-daemon-disconnects-and-restarts) | Automatic reconnection and request replay |

---

## How to connect to the daemon and handle events

Connect to the kpclientd daemon and set up event handling:

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
cfg, err := thin.LoadFile("thinclient.toml")
if err != nil {
    log.Fatal(err)
}

logging := &config.Logging{Level: "INFO"}
client := thin.NewThinClient(cfg, logging)

err = client.Dial()
if err != nil {
    log.Fatal(err)
}
defer client.Close()

// Listen for events
eventCh := client.EventSink()
defer client.StopEventSink(eventCh)

for ev := range eventCh {
    switch v := ev.(type) {
    case *thin.ConnectionStatusEvent:
        fmt.Printf("Connected: %v\n", v.IsConnected)
    case *thin.NewDocumentEvent:
        fmt.Println("New PKI document received")
    case *thin.MessageReplyEvent:
        fmt.Printf("Reply received for SURB %x\n", v.SURBID)
    }
}
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
let config = Config::new("thinclient.toml")?;
let client = ThinClient::new(config).await?;

// Listen for events
let mut event_rx = client.event_sink();
tokio::spawn(async move {
    while let Some(event) = event_rx.recv().await {
        // Process events
        println!("Event: {:?}", event);
    }
});

// ... do work ...

client.stop().await;
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def on_connection_status(event):
    print(f"Connected: {event.get('is_connected')}")

async def on_new_document(event):
    print("New PKI document received")

async def on_message_reply(event):
    print(f"Reply received")

config = Config("thinclient.toml")
config.on_connection_status = on_connection_status
config.on_new_pki_document = on_new_document
config.on_message_reply = on_message_reply

client = ThinClient(config)
loop = asyncio.get_running_loop()
await client.start(loop)

# ... do work ...

client.stop()
{{< /tab >}}
{{< /tabpane >}}

---

## How to discover network services via the PKI document

**NOTE** that this isn't necessary for using the Pigeonhole protocol
because `kpclientd` does `courier` service discovery automatically.

The PKI document lists all available mixnet services. Use
`GetService` to get a random instance of a named service:

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
doc := client.PKIDocument()
if doc == nil {
    log.Fatal("No PKI document available")
}

// Get a random echo service
desc, err := client.GetService("echo")
if err != nil {
    log.Fatal(err)
}

// Use desc.MixDescriptor.IdentityKey and desc.RecipientQueueID
// as the destination for SendMessage
destNode, destQueue := desc.ToDestination()
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
let doc = client.pki_document().await?;

// Get a random echo service
let desc = client.get_service("echo").await?;

// Use the destination for send_message
let (dest_node, dest_queue) = desc.to_destination();
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
doc = client.pki_document()
if doc is None:
    raise Exception("No PKI document available")

# Get a random echo service
desc = client.get_service("echo")

# Use the destination for send_message
dest_node, dest_queue = desc.to_destination()
{{< /tab >}}
{{< /tabpane >}}

---

## How to verify the PKI document yourself

In ordinary use you do not need this section. `kpclientd` already
verifies every PKI document against the directory authorities listed
in `client.toml`, and only after a sufficient threshold of authority
signatures has passed does it push the document on to the thin
client. The `pki_document()` method described above hands you the
post-verification document, and you inherit the daemon's guarantee
without further work. The signature map is stripped before that
handoff precisely because the verification has already happened;
carrying the signatures through would only invite confusion about
whose trust root is in force.

`get_pki_document_raw` is the trapdoor for special applications and
integrations that want the *signed* document. The cases that come up
in practice include:

- An application that wishes to anchor its own root of trust,
  independently of `kpclientd`'s configuration, for instance when
  shipping a hardened build with the authority keys compiled in.
- A relay that forwards the signed document to a separate consumer
  (for archival, audit, or out-of-band verification) which does not
  itself speak the thin-client protocol.
- A diagnostic or monitoring tool that wishes to display which
  authorities signed which consensus, across time.

The method returns the `cert.Certificate`-wrapped signed document
together with the epoch the daemon resolved to. Pass `0` for the
requested epoch to mean "whatever the daemon currently believes is
the latest".

The examples below verify the document against the post-quantum
hybrid signature scheme `Falcon-padded-512-Ed25519`, the recommended
production scheme published by
[hpqc](https://github.com/katzenpost/hpqc) in both its Python and Go
forms. The authority public keys must come from the application's
own trust store, never from the daemon: if the daemon supplied them,
the verification would establish only that the daemon was internally
consistent, not that the document was signed by the real
authorities.

{{< tabpane >}}
{{< tab header="Python" lang="python" >}}
import struct
from hashlib import blake2b

import cbor2
from hpqc.sign.hybrid import FalconPadded512Ed25519


# The directory authority public keys in the wire format expected by
# hpqc's hybrid scheme: the byte concatenation
# ``falcon_padded_512_pub || ed25519_pub`` (929 bytes per authority).
# These must be obtained out of band, typically baked into the
# application or carried in a separately signed bundle. The hex
# strings below are placeholders.
AUTHORITY_PUBLIC_KEYS = [
    bytes.fromhex("ab" * 929),  # auth1
    bytes.fromhex("cd" * 929),  # auth2
    bytes.fromhex("ef" * 929),  # auth3
]
THRESHOLD = len(AUTHORITY_PUBLIC_KEYS) // 2 + 1
SCHEME_NAME = "Falcon-padded-512-Ed25519"


def _signed_message(cert: dict) -> bytes:
    """Reconstruct the byte string the authorities signed.

    A deterministic little-endian concatenation of the Certificate
    fields preceding Signatures; see katzenpost/core/cert/cert.go for
    the canonical encoding.
    """
    return b"".join([
        struct.pack("<I", cert["Version"]),
        struct.pack("<Q", cert["Expiration"]),
        cert["KeyType"].encode("utf-8"),
        cert["Certified"],
    ])


async def fetch_and_verify_pki(client, epoch: int = 0) -> bytes:
    """Fetch the signed PKI document and verify it against the trust root.

    Returns the inner Certified payload (the CBOR-encoded Document)
    once a sufficient threshold of authority signatures has verified;
    raises ValueError otherwise.
    """
    payload, returned_epoch = await client.get_pki_document_raw(epoch)
    cert = cbor2.loads(payload)

    if cert["Version"] != 0:
        raise ValueError(f"unknown certificate version: {cert['Version']}")
    if cert["KeyType"] != SCHEME_NAME:
        raise ValueError(
            f"unexpected key type {cert['KeyType']!r}, "
            f"expected {SCHEME_NAME!r}"
        )

    msg = _signed_message(cert)
    signatures = cert.get("Signatures") or {}

    verified = 0
    for pubkey in AUTHORITY_PUBLIC_KEYS:
        key_hash = blake2b(pubkey, digest_size=32).digest()
        sig = signatures.get(key_hash)
        if sig is None:
            continue
        if FalconPadded512Ed25519.verify(pubkey, msg, sig["Payload"]):
            verified += 1

    if verified < THRESHOLD:
        raise ValueError(
            f"only {verified} of {len(AUTHORITY_PUBLIC_KEYS)} authority "
            f"signatures verified for epoch {returned_epoch}; threshold "
            f"is {THRESHOLD}"
        )

    # cert["Certified"] is the CBOR-encoded Document. Decode it with
    # cbor2.loads(cert["Certified"]) if the application needs the
    # contents themselves.
    return cert["Certified"]
{{< /tab >}}
{{< tab header="Go" lang="go" >}}
package main

import (
    "encoding/hex"
    "fmt"
    "log"

    "github.com/katzenpost/hpqc/sign"
    "github.com/katzenpost/hpqc/sign/hybrid"

    "github.com/katzenpost/katzenpost/client/thin"
    "github.com/katzenpost/katzenpost/core/cert"
)

// AuthorityPublicKeysHex is the application's root of trust for the
// network's directory: the wire-format hybrid public keys of each
// authority, hex-encoded. They must be obtained out of band and
// never from the daemon. Replace these placeholders with your own.
var AuthorityPublicKeysHex = []string{
    "abab...", // auth1
    "cdcd...", // auth2
    "efef...", // auth3
}

// FetchAndVerifyPKI fetches the signed PKI document for the given
// epoch (pass 0 for "current") and verifies it against the
// authority public keys above using core/cert.VerifyThreshold.
func FetchAndVerifyPKI(client *thin.ThinClient, epoch uint64) ([]byte, error) {
    scheme := hybrid.FalconPadded512Ed25519
    verifiers := make([]sign.PublicKey, 0, len(AuthorityPublicKeysHex))
    for _, hexKey := range AuthorityPublicKeysHex {
        raw, err := hex.DecodeString(hexKey)
        if err != nil {
            return nil, fmt.Errorf("decoding authority key: %w", err)
        }
        pub, err := scheme.UnmarshalBinaryPublicKey(raw)
        if err != nil {
            return nil, fmt.Errorf("parsing authority key: %w", err)
        }
        verifiers = append(verifiers, pub)
    }

    payload, returnedEpoch, err := client.GetPKIDocumentRaw(epoch)
    if err != nil {
        return nil, fmt.Errorf("fetching signed PKI doc: %w", err)
    }

    threshold := len(verifiers)/2 + 1
    certified, good, _, err := cert.VerifyThreshold(verifiers, threshold, payload)
    if err != nil {
        return nil, fmt.Errorf(
            "threshold verification failed for epoch %d: %w",
            returnedEpoch, err,
        )
    }
    log.Printf("verified %d of %d authority signatures for epoch %d",
        len(good), len(verifiers), returnedEpoch)
    return certified, nil
}
{{< /tab >}}
{{< /tabpane >}}

Considerations:

- The authority public keys must come from a trust root external to
  the daemon. If the daemon supplied them, verification would prove
  only that the daemon was internally consistent.
- The threshold above (a simple majority) matches the policy that the
  authorities themselves enforce when they admit a consensus. An
  application may apply a stricter policy, but should not relax it.
- Should the network ever be reconfigured to use a different
  signature scheme, swap the hybrid for the corresponding hpqc
  verifier and adjust the expected `KeyType` (Python) or the
  `hybrid.*` selector (Go) accordingly. The `KeyType` field of the
  certificate is what the authorities signed under, and is the
  authoritative indicator of the scheme in force.
- A Rust binding is not shown because `hpqc` does not yet publish a
  Rust port; a Rust application can compose the verification with
  the `ed25519-dalek` and `falcon` crates by the same wire layout
  (the public key and signature are simple concatenations of the
  two component halves).

---

## How to send a message to a mixnet service

**NOTE** that this API call is NOT used with the Pigeonhole protocol.
However it is still useful for writing other protocols and proving the
`echo` service.


Use `BlockingSendMessage` for simple request-response interactions
with non-Pigeonhole services (like the echo service):

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
desc, err := client.GetService("echo")
if err != nil {
    log.Fatal(err)
}

destNode, destQueue := desc.ToDestination()

ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()

reply, err := client.BlockingSendMessage(ctx, []byte("hello mixnet"), destNode, destQueue)
if err != nil {
    log.Fatal(err)
}
fmt.Printf("Reply: %s\n", reply)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
let desc = client.get_service("echo").await?;
let (dest_node, dest_queue) = desc.to_destination();

let reply = client.blocking_send_message(
    b"hello mixnet",
    dest_node,
    dest_queue,
    std::time::Duration::from_secs(30),
).await?;
println!("Reply: {:?}", reply);
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
desc = client.get_service("echo")
dest_node, dest_queue = desc.to_destination()

reply = await client.blocking_send_message(
    b"hello mixnet", dest_node, dest_queue, timeout_seconds=30.0
)
print(f"Reply: {reply}")
{{< /tab >}}
{{< /tabpane >}}

---

## How to create a Pigeonhole channel

*NOTE* that this does NOT produce any network traffic.
It's a local cryptographic operation only.

A Pigeonhole channel (stream) is created from a 32-byte random seed.
The writer keeps the write cap; the reader receives the read cap and
first index out-of-band.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
seed := make([]byte, 32)
_, err := rand.Reader.Read(seed)
if err != nil {
    log.Fatal(err)
}

writeCap, readCap, firstIndex, err := client.NewKeypair(seed)
if err != nil {
    log.Fatal(err)
}

// Writer keeps: writeCap, firstIndex
// Share with reader out-of-band: readCap, firstIndex
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
let seed: [u8; 32] = rand::random();
let result = client.new_keypair(&seed).await?;

// Writer keeps: result.write_cap, result.first_index
// Share with reader out-of-band: result.read_cap, result.first_index
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
import os
seed = os.urandom(32)
result = await client.new_keypair(seed)

# Writer keeps: result.write_cap, result.first_index
# Share with reader out-of-band: result.read_cap, result.first_index
{{< /tab >}}
{{< /tabpane >}}

---

## How to write a message to a Pigeonhole channel

Writing is a two-step process: encrypt the message, then send it via
ARQ.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// Encrypt the message
ciphertext, envDesc, envHash, nextIndex, err := client.EncryptWrite(
    []byte("hello"), writeCap, currentIndex,
)
if err != nil {
    log.Fatal(err)
}

// Send via ARQ (blocks until acknowledged)
_, err = client.StartResendingEncryptedMessage(
    nil,       // readCap (nil for writes)
    writeCap,
    nil,       // messageBoxIndex (nil for writes)
    nil,       // replyIndex
    envDesc,
    ciphertext,
    envHash,
)
if err != nil {
    log.Fatal(err)
}

// Advance the index for the next write
currentIndex = nextIndex
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// Encrypt the message
let result = client.encrypt_write(
    b"hello", &write_cap, &current_index,
).await?;

// Send via ARQ (blocks until acknowledged)
client.start_resending_encrypted_message(
    None,                           // read_cap (None for writes)
    Some(&write_cap),
    None,                           // message_box_index
    None,                           // reply_index
    &result.envelope_descriptor,
    &result.message_ciphertext,
    &result.envelope_hash,
).await?;

// Advance the index for the next write
current_index = result.next_message_box_index;
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
# Encrypt the message
result = await client.encrypt_write(b"hello", write_cap, current_index)

# Send via ARQ (blocks until acknowledged)
await client.start_resending_encrypted_message(
    read_cap=None,
    write_cap=write_cap,
    next_message_index=None,
    reply_index=None,
    envelope_descriptor=result.envelope_descriptor,
    message_ciphertext=result.message_ciphertext,
    envelope_hash=result.envelope_hash,
)

# Advance the index for the next write
current_index = result.next_message_box_index
{{< /tab >}}
{{< /tabpane >}}

---

## How to read a message from a Pigeonhole channel

Reading is also two steps: encrypt a read request, then send it via
ARQ. The reply contains the plaintext.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// Encrypt a read request
ciphertext, envDesc, envHash, nextIndex, err := client.EncryptRead(
    readCap, currentIndex,
)
if err != nil {
    log.Fatal(err)
}

// Send via ARQ (blocks until the message is retrieved)
result, err := client.StartResendingEncryptedMessage(
    readCap,
    nil,       // writeCap (nil for reads)
    nil,       // messageBoxIndex
    nil,       // replyIndex
    envDesc,
    ciphertext,
    envHash,
)
if err != nil {
    log.Fatal(err)
}

plaintext := result.Plaintext
// Advance the index for the next read
currentIndex = nextIndex
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// Encrypt a read request
let read_result = client.encrypt_read(&read_cap, &current_index).await?;

// Send via ARQ (blocks until the message is retrieved)
let result = client.start_resending_encrypted_message(
    Some(&read_cap),
    None,                                    // write_cap (None for reads)
    None,                                    // message_box_index
    None,                                    // reply_index
    &read_result.envelope_descriptor,
    &read_result.message_ciphertext,
    &read_result.envelope_hash,
).await?;

let plaintext = result.plaintext;
// Advance the index for the next read
current_index = read_result.next_message_box_index;
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
# Encrypt a read request
read_result = await client.encrypt_read(read_cap, current_index)

# Send via ARQ (blocks until the message is retrieved)
plaintext = await client.start_resending_encrypted_message(
    read_cap=read_cap,
    write_cap=None,
    next_message_index=None,
    reply_index=None,
    envelope_descriptor=read_result.envelope_descriptor,
    message_ciphertext=read_result.message_ciphertext,
    envelope_hash=read_result.envelope_hash,
)

# Advance the index for the next read
current_index = read_result.next_message_box_index
{{< /tab >}}
{{< /tabpane >}}

---

## How to wait for a message that has not been written yet

Reads and writes are not coordinated: a reader routinely asks for an
index before the writer has filled it, and replication lag can briefly
hide a box that was in fact written. In both cases the daemon reports
`BoxIDNotFound`. This is the expected answer to "anything here yet?",
not a failure. The correct pattern is a bounded poll: retry on the
expected outcome, with a short delay between attempts, until the data
appears or an application deadline elapses. Use `IsExpectedOutcome` to
tell a benign "not yet" apart from a real error, so that genuine
failures are not silently retried forever.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
deadline := time.Now().Add(2 * time.Minute)
var plaintext []byte
for {
    ciphertext, envDesc, envHash, nextIndex, err := client.EncryptRead(
        readCap, currentIndex,
    )
    if err != nil {
        log.Fatal(err)
    }

    result, err := client.StartResendingEncryptedMessage(
        readCap, nil, nil, nil, envDesc, ciphertext, envHash,
    )
    if err == nil {
        plaintext = result.Plaintext
        currentIndex = nextIndex
        break
    }

    // BoxIDNotFound here just means "not written yet". Anything that
    // is not an expected outcome is a real failure worth surfacing.
    if !thin.IsExpectedOutcome(err) {
        log.Fatal(err)
    }
    if time.Now().After(deadline) {
        log.Fatal("gave up waiting for the message")
    }
    time.Sleep(3 * time.Second)
}
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
let deadline = std::time::Instant::now()
    + std::time::Duration::from_secs(120);
let plaintext = loop {
    let read = client.encrypt_read(&read_cap, &current_index).await?;
    match client.start_resending_encrypted_message(
        Some(&read_cap), None, None, None,
        &read.envelope_descriptor,
        &read.message_ciphertext,
        &read.envelope_hash,
    ).await {
        Ok(result) => {
            current_index = read.next_message_box_index;
            break result.plaintext;
        }
        Err(e) if e.is_expected_outcome() => {
            if std::time::Instant::now() > deadline {
                return Err(e);
            }
            tokio::time::sleep(
                std::time::Duration::from_secs(3)).await;
        }
        Err(e) => return Err(e),
    }
};
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
import asyncio, time
from katzenpost_thinclient import is_expected_outcome

deadline = time.monotonic() + 120
while True:
    read = await client.encrypt_read(read_cap, current_index)
    try:
        plaintext = await client.start_resending_encrypted_message(
            read_cap=read_cap, write_cap=None,
            next_message_index=None, reply_index=None,
            envelope_descriptor=read.envelope_descriptor,
            message_ciphertext=read.message_ciphertext,
            envelope_hash=read.envelope_hash,
        )
        current_index = read.next_message_box_index
        break
    except Exception as exc:
        # "not written yet" is expected; anything else is a real error.
        if not is_expected_outcome(exc):
            raise
        if time.monotonic() > deadline:
            raise
        await asyncio.sleep(3)
{{< /tab >}}
{{< /tabpane >}}

---

## How to persist and restore channel state

The daemon keeps no per-application channel state. The write cap, the
read cap, and above all the **current index** belong to your
application, and if you lose the index across a restart you no longer
know where to append next (re-using a filled index earns
`BoxAlreadyExists`). Persist the index every time you advance it,
durably, before you treat the write as done.

In Go the capabilities and the index are typed; serialise them with
`MarshalBinary` and restore them with the `bacap` constructors. In
Rust and Python `new_keypair` already hands you the caps and index as
byte strings, so persistence is simply storing and reloading those
bytes.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
import "github.com/katzenpost/hpqc/bacap"

// Save: marshal each artefact to bytes and write atomically to disk.
wcBytes, _ := writeCap.MarshalBinary()
rcBytes, _ := readCap.MarshalBinary()
idxBytes, _ := currentIndex.MarshalBinary()
saveState(wcBytes, rcBytes, idxBytes) // your durable, atomic write

// Restore after a restart:
writeCap, err := bacap.NewWriteCapFromBytes(wcBytes)
if err != nil {
    log.Fatal(err)
}
readCap, err := bacap.ReadCapFromBytes(rcBytes)
if err != nil {
    log.Fatal(err)
}
currentIndex, err := bacap.NewEmptyMessageBoxIndexFromBytes(idxBytes)
if err != nil {
    log.Fatal(err)
}
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// new_keypair already returns Vec<u8> for each artefact.
let kp = client.new_keypair(&seed).await?;
save_state(&kp.write_cap, &kp.read_cap, &kp.first_index);
let mut current_index = kp.first_index.clone();

// ... each time you advance, persist the new index bytes ...
save_index(&current_index);

// After a restart, the stored bytes are passed straight back into
// the API; no deserialisation step is required.
let (write_cap, read_cap, current_index) = load_state();
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
# new_keypair already returns bytes for each artefact.
kp = await client.new_keypair(seed)
save_state(kp.write_cap, kp.read_cap, kp.first_index)
current_index = kp.first_index

# ... each time you advance, persist the new index bytes ...
save_index(current_index)

# After a restart, the stored bytes are passed straight back into
# the API; no deserialisation step is required.
write_cap, read_cap, current_index = load_state()
{{< /tab >}}
{{< /tabpane >}}

The writer must persist `currentIndex` after every successful write,
the reader after every successful read. Persist the index *before*
acknowledging the message to the rest of your application, so that a
crash cannot leave you having processed a message whose index you
never recorded.

---

## How to hold a two-way conversation

A stream has exactly one writer, so a conversation between two parties
is two streams: each party writes to its own and reads from the
other's. The setup is symmetric: each creates a stream and shares its
read cap (and first index) with the other out-of-band. Thereafter each
party writes with its own write cap and polls the peer's stream with
the peer's read cap, advancing two independent indices.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// Alice's side. (Bob's is the mirror image.)
aliceWrite, aliceRead, aliceIdx, err := client.NewKeypair(aliceSeed)
if err != nil {
    log.Fatal(err)
}

// Exchange read caps out-of-band: Alice sends aliceRead+aliceIdx to
// Bob and receives bobRead+bobIdx from Bob.
sendOutOfBand(aliceRead, aliceIdx)
bobRead, bobIdx := receiveOutOfBand()

// Send on Alice's own stream.
ct, ed, eh, nextOut, _ := client.EncryptWrite(
    []byte("hello Bob"), aliceWrite, aliceIdx)
_, err = client.StartResendingEncryptedMessage(
    nil, aliceWrite, nil, nil, ed, ct, eh)
if err != nil {
    log.Fatal(err)
}
aliceIdx = nextOut // persist this

// Receive on Bob's stream, using the polling pattern shown above,
// reading with bobRead and advancing bobIdx.
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// Alice's side. (Bob's is the mirror image.)
let alice = client.new_keypair(&alice_seed).await?;

// Exchange read caps out-of-band.
send_out_of_band(&alice.read_cap, &alice.first_index);
let (bob_read, mut bob_idx) = receive_out_of_band();
let mut alice_idx = alice.first_index.clone();

// Send on Alice's own stream.
let w = client.encrypt_write(b"hello Bob",
    &alice.write_cap, &alice_idx).await?;
client.start_resending_encrypted_message(
    None, Some(&alice.write_cap), None, None,
    &w.envelope_descriptor, &w.message_ciphertext,
    &w.envelope_hash).await?;
alice_idx = w.next_message_box_index; // persist this

// Receive on Bob's stream with the polling pattern, reading with
// bob_read and advancing bob_idx.
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
# Alice's side. (Bob's is the mirror image.)
alice = await client.new_keypair(alice_seed)

# Exchange read caps out-of-band.
send_out_of_band(alice.read_cap, alice.first_index)
bob_read, bob_idx = receive_out_of_band()
alice_idx = alice.first_index

# Send on Alice's own stream.
w = await client.encrypt_write(b"hello Bob",
    alice.write_cap, alice_idx)
await client.start_resending_encrypted_message(
    read_cap=None, write_cap=alice.write_cap,
    next_message_index=None, reply_index=None,
    envelope_descriptor=w.envelope_descriptor,
    message_ciphertext=w.message_ciphertext,
    envelope_hash=w.envelope_hash)
alice_idx = w.next_message_box_index  # persist this

# Receive on Bob's stream with the polling pattern, reading with
# bob_read and advancing bob_idx.
{{< /tab >}}
{{< /tabpane >}}

---

## How to prepare operations offline

The daemon distinguishes two kinds of work. Key generation and
envelope encryption (`NewKeypair`, `EncryptWrite`, `EncryptRead`,
`TombstoneRange`, and the copy-stream constructors) are local
cryptography and succeed even when the daemon is not connected to the
mixnet. Only `StartResendingEncryptedMessage` and
`StartResendingCopyCommand` require connectivity; called offline they
fail rather than block.

You can therefore prepare envelopes while offline, persist them, and
transmit once connectivity returns. Test `IsConnected` before
transmitting, or watch the connection event and flush a queue when it
turns true.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// Offline: this is pure local crypto and works regardless.
ciphertext, envDesc, envHash, nextIndex, err := client.EncryptWrite(
    []byte("written while offline"), writeCap, currentIndex,
)
if err != nil {
    log.Fatal(err)
}
enqueue(envDesc, ciphertext, envHash) // persist for later

// Later, only transmit once the daemon is connected.
if client.IsConnected() {
    for _, e := range drainQueue() {
        _, err = client.StartResendingEncryptedMessage(
            nil, writeCap, nil, nil, e.desc, e.ct, e.hash)
        if err != nil {
            log.Fatal(err)
        }
    }
}
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// Offline: pure local crypto, works regardless.
let w = client.encrypt_write(
    b"written while offline", &write_cap, &current_index).await?;
enqueue(&w); // persist for later

// Later, only transmit once connected.
if client.is_connected() {
    for e in drain_queue() {
        client.start_resending_encrypted_message(
            None, Some(&write_cap), None, None,
            &e.envelope_descriptor, &e.message_ciphertext,
            &e.envelope_hash).await?;
    }
}
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
# Offline: pure local crypto, works regardless.
w = await client.encrypt_write(
    b"written while offline", write_cap, current_index)
enqueue(w)  # persist for later

# Later, only transmit once connected.
if client.is_connected():
    for e in drain_queue():
        await client.start_resending_encrypted_message(
            read_cap=None, write_cap=write_cap,
            next_message_index=None, reply_index=None,
            envelope_descriptor=e.envelope_descriptor,
            message_ciphertext=e.message_ciphertext,
            envelope_hash=e.envelope_hash)
{{< /tab >}}
{{< /tabpane >}}

---

## A complete end-to-end example

The fragments above each show one task. Here they are assembled into a
single runnable program: Alice creates a stream, writes one message,
and Bob reads it back. This is the smallest complete program that
exercises the Pigeonhole path. As with every example in this guide it
omits production concerns (durable persistence, structured logging),
but it compiles into the shape of a real application; the
[CI-verified tests](#authoritative-working-examples) are the
authority on exact, current usage.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
package main

import (
    "log"

    "github.com/katzenpost/hpqc/rand"

    "github.com/katzenpost/katzenpost/client/thin"
    "github.com/katzenpost/katzenpost/core/config"
)

func main() {
    cfg, err := thin.LoadFile("thinclient.toml")
    if err != nil {
        log.Fatal(err)
    }
    client := thin.NewThinClient(cfg, &config.Logging{Level: "INFO"})
    if err := client.Dial(); err != nil {
        log.Fatal(err)
    }
    defer client.Close()

    // Alice creates a stream.
    seed := make([]byte, 32)
    if _, err := rand.Reader.Read(seed); err != nil {
        log.Fatal(err)
    }
    writeCap, readCap, idx, err := client.NewKeypair(seed)
    if err != nil {
        log.Fatal(err)
    }

    // Alice writes one message.
    ct, ed, eh, _, err := client.EncryptWrite(
        []byte("hello from Alice"), writeCap, idx)
    if err != nil {
        log.Fatal(err)
    }
    if _, err := client.StartResendingEncryptedMessage(
        nil, writeCap, nil, nil, ed, ct, eh); err != nil {
        log.Fatal(err)
    }

    // Bob reads it back (readCap would normally be shared out-of-band).
    rct, red, reh, _, err := client.EncryptRead(readCap, idx)
    if err != nil {
        log.Fatal(err)
    }
    result, err := client.StartResendingEncryptedMessage(
        readCap, nil, nil, nil, red, rct, reh)
    if err != nil {
        log.Fatal(err)
    }
    log.Printf("Bob read: %s", result.Plaintext)
}
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
use katzenpost_thin_client::{Config, ThinClient};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let config = Config::new("thinclient.toml")?;
    let client = ThinClient::new(config).await?;

    // Alice creates a stream.
    let seed: [u8; 32] = rand::random();
    let kp = client.new_keypair(&seed).await?;

    // Alice writes one message.
    let w = client.encrypt_write(
        b"hello from Alice", &kp.write_cap, &kp.first_index).await?;
    client.start_resending_encrypted_message(
        None, Some(&kp.write_cap), None, None,
        &w.envelope_descriptor, &w.message_ciphertext,
        &w.envelope_hash).await?;

    // Bob reads it back (read_cap would normally be shared out-of-band).
    let r = client.encrypt_read(&kp.read_cap, &kp.first_index).await?;
    let result = client.start_resending_encrypted_message(
        Some(&kp.read_cap), None, None, None,
        &r.envelope_descriptor, &r.message_ciphertext,
        &r.envelope_hash).await?;
    println!("Bob read: {:?}", result.plaintext);

    client.stop().await;
    Ok(())
}
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
import asyncio, os
from katzenpost_thinclient import ThinClient, Config

async def main():
    config = Config("thinclient.toml")
    client = ThinClient(config)
    await client.start(asyncio.get_running_loop())

    # Alice creates a stream.
    seed = os.urandom(32)
    kp = await client.new_keypair(seed)

    # Alice writes one message.
    w = await client.encrypt_write(
        b"hello from Alice", kp.write_cap, kp.first_index)
    await client.start_resending_encrypted_message(
        read_cap=None, write_cap=kp.write_cap,
        next_message_index=None, reply_index=None,
        envelope_descriptor=w.envelope_descriptor,
        message_ciphertext=w.message_ciphertext,
        envelope_hash=w.envelope_hash)

    # Bob reads it back (read_cap would normally be shared out-of-band).
    r = await client.encrypt_read(kp.read_cap, kp.first_index)
    plaintext = await client.start_resending_encrypted_message(
        read_cap=kp.read_cap, write_cap=None,
        next_message_index=None, reply_index=None,
        envelope_descriptor=r.envelope_descriptor,
        message_ciphertext=r.message_ciphertext,
        envelope_hash=r.envelope_hash)
    print("Bob read:", plaintext)

    client.stop()

asyncio.run(main())
{{< /tab >}}
{{< /tabpane >}}

---

## How to delete messages with tombstones

Use `TombstoneRange` to create tombstone envelopes, then send each
one via `StartResendingEncryptedMessage`. To tombstone a single box,
use `maxCount=1`.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// Create tombstone envelopes for 5 boxes
result, err := client.TombstoneRange(writeCap, startIndex, 5)
if err != nil {
    log.Fatal(err)
}

// Send each tombstone
for _, envelope := range result.Envelopes {
    _, err = client.StartResendingEncryptedMessage(
        nil, writeCap, nil, nil,
        envelope.EnvelopeDescriptor,
        envelope.MessageCiphertext,
        envelope.EnvelopeHash,
    )
    if err != nil {
        log.Fatal(err)
    }
}
// result.Next is the index after the last tombstoned box
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// Create tombstone envelopes for 5 boxes
let result = client.tombstone_range(&write_cap, &start_index, 5).await;

// Send each tombstone
for envelope in &result.envelopes {
    client.start_resending_encrypted_message(
        None,
        Some(&write_cap),
        None,
        None,
        &envelope.envelope_descriptor,
        &envelope.message_ciphertext,
        &envelope.envelope_hash,
    ).await?;
}
// result.next is the index after the last tombstoned box
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
# Create tombstone envelopes for 5 boxes
result = await client.tombstone_range(write_cap, start_index, 5)

# Send each tombstone
for envelope in result.envelopes:
    await client.start_resending_encrypted_message(
        read_cap=None,
        write_cap=write_cap,
        next_message_index=None,
        reply_index=None,
        envelope_descriptor=envelope.envelope_descriptor,
        message_ciphertext=envelope.message_ciphertext,
        envelope_hash=envelope.envelope_hash,
    )
# result.next is the index after the last tombstoned box
{{< /tab >}}
{{< /tabpane >}}

---

## How to send to one channel atomically via copy command

A copy command writes data to a destination channel atomically via a
courier. The steps are:

1. Create a temporary channel and a destination channel.
2. Pack the payload into copy stream elements.
3. Write each element to the temporary channel.
4. Send a copy command referencing the temporary channel.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// Create destination channel
destSeed := make([]byte, 32)
rand.Reader.Read(destSeed)
destWriteCap, destReadCap, destFirstIndex, err := client.NewKeypair(destSeed)
if err != nil {
    log.Fatal(err)
}

// Create temporary channel
tempSeed := make([]byte, 32)
rand.Reader.Read(tempSeed)
tempWriteCap, _, tempFirstIndex, err := client.NewKeypair(tempSeed)
if err != nil {
    log.Fatal(err)
}

// Pack payload into copy stream elements
envelopes, _, err := client.CreateCourierEnvelopesFromPayload(
    payload, destWriteCap, destFirstIndex,
    true,  // isStart
    true,  // isLast
)
if err != nil {
    log.Fatal(err)
}

// Write each element to the temporary channel
tempIndex := tempFirstIndex
for _, chunk := range envelopes {
    ciphertext, envDesc, envHash, nextIdx, err := client.EncryptWrite(
        chunk, tempWriteCap, tempIndex,
    )
    if err != nil {
        log.Fatal(err)
    }
    _, err = client.StartResendingEncryptedMessage(
        nil, tempWriteCap, nil, nil, envDesc, ciphertext, envHash,
    )
    if err != nil {
        log.Fatal(err)
    }
    tempIndex = nextIdx
}

// Send the copy command (blocks until courier acknowledges)
err = client.StartResendingCopyCommand(tempWriteCap)
if err != nil {
    log.Fatal(err)
}

// Share destReadCap and destFirstIndex with the reader
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// Create destination channel
let dest_seed: [u8; 32] = rand::random();
let dest = client.new_keypair(&dest_seed).await?;

// Create temporary channel
let temp_seed: [u8; 32] = rand::random();
let temp = client.new_keypair(&temp_seed).await?;

// Pack payload into copy stream elements
let envelopes_result = client.create_courier_envelopes_from_payload(
    &payload, &dest.write_cap, &dest.first_index,
    true,  // is_start
    true,  // is_last
).await?;

// Write each element to the temporary channel
let mut temp_index = temp.first_index.clone();
for chunk in &envelopes_result.envelopes {
    let write_result = client.encrypt_write(
        chunk, &temp.write_cap, &temp_index,
    ).await?;
    client.start_resending_encrypted_message(
        None, Some(&temp.write_cap), None, None,
        &write_result.envelope_descriptor,
        &write_result.message_ciphertext,
        &write_result.envelope_hash,
    ).await?;
    temp_index = write_result.next_message_box_index;
}

// Send the copy command (blocks until courier acknowledges)
client.start_resending_copy_command(&temp.write_cap, None, None).await?;

// Share dest.read_cap and dest.first_index with the reader
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
import os

# Create destination channel
dest_seed = os.urandom(32)
dest = await client.new_keypair(dest_seed)

# Create temporary channel
temp_seed = os.urandom(32)
temp = await client.new_keypair(temp_seed)

# Pack payload into copy stream elements
envelopes_result = await client.create_courier_envelopes_from_payload(
    payload, dest.write_cap, dest.first_index,
    is_start=True,
    is_last=True,
)

# Write each element to the temporary channel
temp_index = temp.first_index
for chunk in envelopes_result.envelopes:
    write_result = await client.encrypt_write(chunk, temp.write_cap, temp_index)
    await client.start_resending_encrypted_message(
        read_cap=None, write_cap=temp.write_cap,
        next_message_index=None, reply_index=None,
        envelope_descriptor=write_result.envelope_descriptor,
        message_ciphertext=write_result.message_ciphertext,
        envelope_hash=write_result.envelope_hash,
    )
    temp_index = write_result.next_message_box_index

# Send the copy command (blocks until courier acknowledges)
await client.start_resending_copy_command(temp.write_cap)

# Share dest.read_cap and dest.first_index with the reader
{{< /tab >}}
{{< /tabpane >}}

---

## How to send to multiple channels atomically

Use `CreateCourierEnvelopesFromMultiPayload` to pack payloads for
different destinations into a single copy stream efficiently:

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// Create destination channels
dest1WriteCap, dest1ReadCap, dest1Index, _ := client.NewKeypair(seed1)
dest2WriteCap, dest2ReadCap, dest2Index, _ := client.NewKeypair(seed2)

// Create temporary channel
tempWriteCap, _, tempFirstIndex, _ := client.NewKeypair(tempSeed)

// Pack multiple payloads
destinations := []thin.DestinationPayload{
    {Payload: payload1, WriteCap: dest1WriteCap, StartIndex: dest1Index},
    {Payload: payload2, WriteCap: dest2WriteCap, StartIndex: dest2Index},
}

result, err := client.CreateCourierEnvelopesFromMultiPayload(
    destinations,
    true,  // isStart
    true,  // isLast
    nil,   // buffer (nil for first call)
)
if err != nil {
    log.Fatal(err)
}

// Write envelopes to temporary channel
tempIndex := tempFirstIndex
for _, chunk := range result.Envelopes {
    ciphertext, envDesc, envHash, nextIdx, err := client.EncryptWrite(
        chunk, tempWriteCap, tempIndex,
    )
    if err != nil {
        log.Fatal(err)
    }
    _, err = client.StartResendingEncryptedMessage(
        nil, tempWriteCap, nil, nil, envDesc, ciphertext, envHash,
    )
    if err != nil {
        log.Fatal(err)
    }
    tempIndex = nextIdx
}

// Send copy command
err = client.StartResendingCopyCommand(tempWriteCap)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// Create destination channels
let dest1 = client.new_keypair(&seed1).await?;
let dest2 = client.new_keypair(&seed2).await?;

// Create temporary channel
let temp = client.new_keypair(&temp_seed).await?;

// Pack multiple payloads
let destinations = vec![
    (&payload1[..], &dest1.write_cap[..], &dest1.first_index[..]),
    (&payload2[..], &dest2.write_cap[..], &dest2.first_index[..]),
];

let result = client.create_courier_envelopes_from_multi_payload(
    destinations,
    true,  // is_start
    true,  // is_last
    None,  // buffer (None for first call)
).await?;

// Write envelopes to temporary channel
let mut temp_index = temp.first_index.clone();
for chunk in &result.envelopes {
    let write_result = client.encrypt_write(
        chunk, &temp.write_cap, &temp_index,
    ).await?;
    client.start_resending_encrypted_message(
        None, Some(&temp.write_cap), None, None,
        &write_result.envelope_descriptor,
        &write_result.message_ciphertext,
        &write_result.envelope_hash,
    ).await?;
    temp_index = write_result.next_message_box_index;
}

// Send copy command
client.start_resending_copy_command(&temp.write_cap, None, None).await?;
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
# Create destination channels
dest1 = await client.new_keypair(seed1)
dest2 = await client.new_keypair(seed2)

# Create temporary channel
temp = await client.new_keypair(temp_seed)

# Pack multiple payloads
destinations = [
    {"payload": payload1, "write_cap": dest1.write_cap, "start_index": dest1.first_index},
    {"payload": payload2, "write_cap": dest2.write_cap, "start_index": dest2.first_index},
]

result = await client.create_courier_envelopes_from_multi_payload(
    destinations,
    is_start=True,
    is_last=True,
    buffer=None,
)

# Write envelopes to temporary channel
temp_index = temp.first_index
for chunk in result.envelopes:
    write_result = await client.encrypt_write(chunk, temp.write_cap, temp_index)
    await client.start_resending_encrypted_message(
        read_cap=None, write_cap=temp.write_cap,
        next_message_index=None, reply_index=None,
        envelope_descriptor=write_result.envelope_descriptor,
        message_ciphertext=write_result.message_ciphertext,
        envelope_hash=write_result.envelope_hash,
    )
    temp_index = write_result.next_message_box_index

# Send copy command
await client.start_resending_copy_command(temp.write_cap)
{{< /tab >}}
{{< /tabpane >}}

---

## How to handle multi-call buffer passing for large copy streams

When building a copy stream across multiple calls (because you have
more data than fits in a single call, or data arrives incrementally),
pass the buffer from each result to the next call:

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
var buffer []byte // nil on first call

// First batch of destinations
result1, err := client.CreateCourierEnvelopesFromMultiPayload(
    batch1Destinations,
    true,   // isStart (first call)
    false,  // isLast (more calls coming)
    buffer,
)
if err != nil {
    log.Fatal(err)
}
// Write result1.Envelopes to temp channel...
buffer = result1.Buffer // save for next call

// Persist buffer to disk for crash recovery
saveState(buffer)

// Second batch (final)
result2, err := client.CreateCourierEnvelopesFromMultiPayload(
    batch2Destinations,
    false,  // isStart (not the first call)
    true,   // isLast (final call)
    buffer,
)
if err != nil {
    log.Fatal(err)
}
// Write result2.Envelopes to temp channel...

// On crash recovery, reload buffer from disk and continue
// with isStart=false
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
let mut buffer: Option<Vec<u8>> = None; // None on first call

// First batch
let result1 = client.create_courier_envelopes_from_multi_payload(
    batch1_destinations,
    true,   // is_start
    false,  // is_last
    buffer,
).await?;
// Write result1.envelopes to temp channel...
buffer = result1.buffer; // save for next call

// Persist buffer to disk for crash recovery
save_state(&buffer);

// Second batch (final)
let result2 = client.create_courier_envelopes_from_multi_payload(
    batch2_destinations,
    false,  // is_start
    true,   // is_last
    buffer,
).await?;
// Write result2.envelopes to temp channel...
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
buffer = None  # None on first call

# First batch
result1 = await client.create_courier_envelopes_from_multi_payload(
    batch1_destinations,
    is_start=True,   # first call
    is_last=False,   # more calls coming
    buffer=buffer,
)
# Write result1.envelopes to temp channel...
buffer = result1.buffer  # save for next call

# Persist buffer to disk for crash recovery
save_state(buffer)

# Second batch (final)
result2 = await client.create_courier_envelopes_from_multi_payload(
    batch2_destinations,
    is_start=False,  # not the first call
    is_last=True,    # final call
    buffer=buffer,
)
# Write result2.envelopes to temp channel...
{{< /tab >}}
{{< /tabpane >}}

---

## How to tombstone a range via copy stream

Use `CreateCourierEnvelopesFromTombstoneRange` to atomically
tombstone boxes as part of a copy command. The courier performs the
tombstoning, so it either all succeeds or none of it is visible.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
tempWriteCap, _, tempFirstIndex, _ := client.NewKeypair(tempSeed)

// Create tombstone copy stream elements
envelopes, nextBuffer, nextDestIndex, err := client.CreateCourierEnvelopesFromTombstoneRange(
    destWriteCap,
    destStartIndex,
    10,     // tombstone 10 boxes
    true,   // isStart
    true,   // isLast
    nil,    // buffer
)
if err != nil {
    log.Fatal(err)
}

// Write to temporary channel
tempIndex := tempFirstIndex
for _, chunk := range envelopes {
    ciphertext, envDesc, envHash, nextIdx, err := client.EncryptWrite(
        chunk, tempWriteCap, tempIndex,
    )
    if err != nil {
        log.Fatal(err)
    }
    _, err = client.StartResendingEncryptedMessage(
        nil, tempWriteCap, nil, nil, envDesc, ciphertext, envHash,
    )
    if err != nil {
        log.Fatal(err)
    }
    tempIndex = nextIdx
}

// Send copy command
err = client.StartResendingCopyCommand(tempWriteCap)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
let temp = client.new_keypair(&temp_seed).await?;

// Create tombstone copy stream elements
let result = client.create_courier_envelopes_from_tombstone_range(
    &dest_write_cap,
    &dest_start_index,
    10,     // tombstone 10 boxes
    true,   // is_start
    true,   // is_last
    None,   // buffer
).await?;

// Write to temporary channel
let mut temp_index = temp.first_index.clone();
for chunk in &result.envelopes {
    let write_result = client.encrypt_write(
        chunk, &temp.write_cap, &temp_index,
    ).await?;
    client.start_resending_encrypted_message(
        None, Some(&temp.write_cap), None, None,
        &write_result.envelope_descriptor,
        &write_result.message_ciphertext,
        &write_result.envelope_hash,
    ).await?;
    temp_index = write_result.next_message_box_index;
}

// Send copy command
client.start_resending_copy_command(&temp.write_cap, None, None).await?;
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
temp = await client.new_keypair(temp_seed)

# Create tombstone copy stream elements
result = await client.create_courier_envelopes_from_tombstone_range(
    dest_write_cap,
    dest_start_index,
    10,              # tombstone 10 boxes
    is_start=True,
    is_last=True,
    buffer=None,
)

# Write to temporary channel
temp_index = temp.first_index
for chunk in result.envelopes:
    write_result = await client.encrypt_write(chunk, temp.write_cap, temp_index)
    await client.start_resending_encrypted_message(
        read_cap=None, write_cap=temp.write_cap,
        next_message_index=None, reply_index=None,
        envelope_descriptor=write_result.envelope_descriptor,
        message_ciphertext=write_result.message_ciphertext,
        envelope_hash=write_result.envelope_hash,
    )
    temp_index = write_result.next_message_box_index

# Send copy command
await client.start_resending_copy_command(temp.write_cap)
{{< /tab >}}
{{< /tabpane >}}

---

## How to cancel in-flight operations

Both `StartResendingEncryptedMessage` and `StartResendingCopyCommand`
block until completion. You can cancel them individually, or stop
everything at once by closing the thin client.

**To cancel a specific operation**, call the corresponding cancel
method from another thread/task:

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// Cancel an encrypted message operation
err := client.CancelResendingEncryptedMessage(envelopeHash)

// Cancel a copy command (needs blake2b-256 hash of the write cap)
writeCapBytes, _ := tempWriteCap.MarshalBinary()
writeCapHash := blake2b.Sum256(writeCapBytes)
err = client.CancelResendingCopyCommand(&writeCapHash)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// Cancel an encrypted message operation
client.cancel_resending_encrypted_message(&envelope_hash).await?;

// Cancel a copy command
use blake2::{Blake2b, Digest};
use digest::consts::U32;
let write_cap_hash: [u8; 32] = Blake2b::<U32>::digest(&temp_write_cap).into();
client.cancel_resending_copy_command(&write_cap_hash).await?;
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
# Cancel an encrypted message operation
await client.cancel_resending_encrypted_message(envelope_hash)

# Cancel a copy command
from hashlib import blake2b
write_cap_hash = blake2b(temp_write_cap, digest_size=32).digest()
await client.cancel_resending_copy_command(write_cap_hash)
{{< /tab >}}
{{< /tabpane >}}

**To stop all in-flight operations at once**, call `Close()` (Go),
`stop()` (Rust), or `stop()` (Python). This shuts down the thin
client entirely -- all blocked callers receive an error, and the
daemon stops all ARQ retransmission loops for this client. This is
useful when your application is shutting down or when you want to
abandon all pending work without cancelling each operation
individually.

---

## How to handle daemon disconnects and restarts

The thin client automatically reconnects when the daemon connection
is lost. It uses an instance token to detect whether it reconnected
to the same daemon or a new one:

- **Same instance token**: The daemon still has its state. No action
  needed.

- **Different instance token**: The daemon is a new process. The thin
  client automatically replays all in-flight
  `StartResendingEncryptedMessage` and `StartResendingCopyCommand`
  operations. Callers blocked on these methods are unaware of the
  disconnect.

Applications do not need to manage reconnection or replay. You can
observe disconnect events to log or update UI state:

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
eventCh := client.EventSink()
defer client.StopEventSink(eventCh)

for ev := range eventCh {
    switch v := ev.(type) {
    case *thin.DaemonDisconnectedEvent:
        if v.IsGraceful {
            fmt.Println("Daemon shut down gracefully")
        } else {
            fmt.Printf("Daemon connection lost: %v\n", v.Err)
        }
        // No action needed -- thin client reconnects automatically
        // and replays in-flight requests if the daemon instance changed.
    case *thin.ConnectionStatusEvent:
        fmt.Printf("Connected: %v\n", v.IsConnected)
        // v.InstanceToken identifies the daemon process.
        // The thin client compares this internally on reconnect.
    }
}
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
let config = Config::new("thinclient.toml")?;
// Set disconnect callback during config
config.on_daemon_disconnected = Some(Box::new(|graceful, err_msg| {
    if graceful {
        println!("Daemon shut down gracefully");
    } else {
        println!("Daemon connection lost: {:?}", err_msg);
    }
    // No action needed -- thin client reconnects automatically
    // and replays in-flight requests if the daemon instance changed.
}));
let client = ThinClient::new(config).await?;
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def on_daemon_disconnected(event):
    if event.get("is_graceful"):
        print("Daemon shut down gracefully")
    else:
        print(f"Daemon connection lost: {event.get('error')}")
    # No action needed -- thin client reconnects automatically
    # and replays in-flight requests if the daemon instance changed.

async def on_connection_status(event):
    print(f"Connected: {event['is_connected']}")
    # event contains 'instance_token' identifying the daemon process.
    # The thin client compares this internally on reconnect.

config = Config(
    "thinclient.toml",
    on_daemon_disconnected=on_daemon_disconnected,
    on_connection_status=on_connection_status,
)
client = ThinClient(config)
{{< /tab >}}
{{< /tabpane >}}

If the thin client is disconnected when you cancel an operation, the
cancel just removes it from in-flight tracking -- it will not be
replayed on reconnect:

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// Safe to call while disconnected -- removes from tracking,
// no message sent to daemon since there is no connection.
err := client.CancelResendingEncryptedMessage(envelopeHash)
err = client.CancelResendingCopyCommand(&writeCapHash)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// Safe to call while disconnected -- removes from tracking,
// no message sent to daemon since there is no connection.
client.cancel_resending_encrypted_message(&envelope_hash).await?;
client.cancel_resending_copy_command(&write_cap_hash).await?;
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
# Safe to call while disconnected -- removes from tracking,
# no message sent to daemon since there is no connection.
await client.cancel_resending_encrypted_message(envelope_hash)
await client.cancel_resending_copy_command(write_cap_hash)
{{< /tab >}}
{{< /tabpane >}}

To terminate the thin client entirely (all blocked callers receive an
error, daemon disconnects never kill the thin client):

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
err := client.Close()
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
client.stop().await;
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
client.stop()
{{< /tab >}}
{{< /tabpane >}}
