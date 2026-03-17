---
title:
linkTitle: Katzenpost Client Integration Guide
description: ""
categories: [""]
tags: [""]
author: []
version: 0
draft: false
slug: "/client_integration/"
---


## Overview

This guide is intended to help developers connect their applications
and projects to a Katzenpost mixnet client.

The Katzenpost client daemon - <b>kpclientd</b> - connects to the
Katzenpost mixnet. It has <i>thin client</i> libraries in Go, Python
and Rust, which you can integrate into your app that you want to work
over Katzenpost. The client can multiplex connections to the mixnet
from multiple applications on the same device.

A <i>thin client</i> is an API interface for the client. It's a simple
protocol where clients send and receive CBOR encoded length prefixed
blobs. All of the cryptographic and network complexities are handled
by the daemon so that applications don't need to do it. However, you
should think of the client as part of the application, and remember
that it's the outgoing connection from the client that has the
mixnet's privacy properties.

Our thin client protocol is described here:
https://katzenpost.network/docs/specs/thin_client.html

It can be extended to be used by any language that has a CBOR
serialization library and can talk over TCP or UNIX domain
socket. Currently there are three thin client libraries and
the reference implementation is written in golang:

{{< tabpane text=true >}}
{{% tab header="**Go**" %}}
**Source code:** https://github.com/katzenpost/katzenpost/tree/main/client2

**API docs:** https://pkg.go.dev/github.com/katzenpost/katzenpost/client2/thin

The Go thin client provides a comprehensive API for interacting with the Katzenpost mixnet.
{{% /tab %}}

{{% tab header="**Rust**" %}}
**Source code:** https://github.com/katzenpost/thin_client/blob/main/src/lib.rs

**API docs:** https://docs.rs/katzenpost_thin_client/0.0.4/katzenpost_thin_client/

**Example:** https://github.com/katzenpost/thin_client/blob/main/examples/echo_ping.rs

The Rust thin client provides async/await support for modern Rust applications.
{{% /tab %}}

{{% tab header="**Python**" %}}
**Source code:** https://github.com/katzenpost/thin_client/blob/main/thinclient/__init__.py

**API docs:** https://katzenpost.network/docs/python_thin_client.html

**Examples:**
- https://github.com/katzenpost/thin_client/blob/main/examples/echo_ping.rs
- https://github.com/katzenpost/status
- https://github.com/katzenpost/worldmap

The Python thin client is ideal for rapid prototyping and integration with existing Python applications.
{{% /tab %}}
{{< /tabpane >}}

### Table Of Contents

*Complete guide sections:*

| Section | Description |
|---------|-------------|
| **🔹 [Overview](#overview)** | **Introduction to Katzenpost client integration and thin client libraries** |
| **🔸 [Core functionality API](#core-functionality)** | **Basic client operations: connection management, PKI documents, mixnet service discovery, events/replies** |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Connecting and Disconnecting](#connecting-and-disconnecting) | How to establish and terminate connections to the kpclientd daemon |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Get a view of the network via the PKI Document](#get-a-view-of-the-network-via-the-pki-document) | Obtaining network topology and service information |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Get a random instance of a specific service](#get-a-random-instance-of-a-specific-service) | Finding and selecting mixnet services |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Receiving Thin Client Events and Service Reply Messages](#receiving-thin-client-events-and-service-reply-messages) | Event handling patterns and message processing |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Thin client events](#thin-client-events) | Core events: shutdown, connection status, and PKI document updates |
| **🔸 [Legacy API](#legacy-api)** | **Message oriented communication with mixnet services, with optional ARQ error correction scheme** |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Legacy Events](#legacy-events) | Events specific to the legacy message API |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Sending a message](#sending-a-message) | How to send messages using the legacy API |
| **🔸 [Pigeonhole Channel API](#pigeonhole-channel-api)** | **Reliable, ordered, persistent, replicated communication channels** |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Example Usage](#example-usage) | End-to-end example of sending and receiving with Pigeonhole |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [New Key Pair](#new-key-pair) | Generating a BACAP keypair (writecap, readcap, first index) |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Next Message Box Index](#next-message-box-index) | Deriving the next index in a channel sequence |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Encrypt Read](#encrypt-read) | Preparing an encrypted read request for a box |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Encrypt Write](#encrypt-write) | Preparing an encrypted write request for a box |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Start Resending Encrypted Message](#start-resending-encrypted-message) | Sending a read or write via ARQ until acknowledged |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Cancel Resending Encrypted Message](#cancel-resending-encrypted-message) | Cancelling an in-flight ARQ operation |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Tombstone Box](#tombstone-box) | Creating a tombstone to delete a single box |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Tombstone Range](#tombstone-range) | Creating tombstones for a range of consecutive boxes |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Copy Command Section](#copy-command-section) | Atomically writing to one or more channels via a courier |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ [Start Resending Copy Command](#start-resending-copy-command) | Sending a copy command via ARQ until acknowledged |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ [Cancel Resending Copy Command](#cancel-resending-copy-command) | Cancelling an in-flight copy command |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ [New Stream ID](#new-stream-id) | Generating a stream ID for a copy stream |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ [Create Courier Envelopes From Payload](#create-courier-envelopes-frompayload) | Building copy stream envelopes from a single payload |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ [Create Courier Envelopes From Multi Payload](#create-courier-envelopes-from-multi-payload) | Building copy stream envelopes from multiple payloads |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↳ [Set Stream Buffer](#set-stream-buffer-crash-recovery) | Restoring copy stream encoder state after a crash |
| &nbsp;&nbsp;&nbsp;&nbsp;↳ [Experimental Nested Copy API](#experimental-nested-copy-api) | Recursive copy commands routed through multiple couriers |


## Core functionality

### Connecting and Disconnecting

The thin client connects and disconnects from the kpclientd daemon
like so:

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// Load thin client configuration
cfg, err := thin.LoadFile("thinclient.toml")
if err != nil {
    log.Fatal(err)
}

logging := &config.Logging{Level: "INFO"}
// create thin client
client := thin.NewThinClient(cfg, logging)

// Connect to kpclientd daemon
err = client.Dial()
if err != nil {
    log.Fatal(err)
}

// ... do stuff ...

// Disconnect from kpclientd daemon
client.Close()
{{< /tab >}}

{{< tab header="Rust" lang="rust" >}}
// connect to kpclientd daemon
let client = ThinClient::new(cfg).await?;

// ... do stuff ...

// disconnect from kpclientd daemon
client.stop().await?;

{{< /tab >}}

{{< tab header="Python" lang="python" >}}
thin_client = ThinClient(config)

# connect to kpclientd daemon
await thin_client.start()

# ... do stuff ...

# disconnect from kpclientd daemon
thin_client.stop()
{{< /tab >}}
{{< /tabpane >}}

### Get a view of the network via the PKI Document

`kpclient` needs the PKI document for internal use for Sphinx packet routing.
However applications will also need the PKI document to learn about the
mixnet services that are available and to choose which ones to use.

You can obtain a PKI document using the thin client API, like so:

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}

// Usage example:
doc := thin.PKIDocument()
if doc == nil {
    panic("No Document")
}
{{< /tab >}}

{{< tab header="Rust" lang="rust" >}}
// Get the PKI document asynchronously
let doc = thin_client.pki_document().await;
{{< /tab >}}

{{< tab header="Python" lang="python" >}}
# Get the PKI document
doc = thin_client.pki_document()
{{< /tab >}}
{{< /tabpane >}}

### Get a random instance of a specific service

When creating an app that works over a mixnet, you will need to
interact with <i>mixnet services</i> that are listed in the PKI
document. For example, our mixnet ping CLI tool gets a random echo
service from the PKI document and handles its business using
that information:

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
desc, err := thin.GetService("echo")
if err != nil {
    panic(err)
}
{{< /tab >}}

{{< tab header="Rust" lang="rust" >}}
let service_desc = thin_client.get_service(service_name).await?;
{{< /tab >}}

{{< tab header="Python" lang="python" >}}
service_descriptor = thin_client.get_service(doc, service_name)
{{< /tab >}}
{{< /tabpane >}}

The `GetService` or `get_service` is a convenient helper method which searches the PKI
document for the the service name we give it and then selects a random
entry from that set. I don't care which XYZ service I talk to just so
long as I can talk to one of them. The result is that you procure a
`service descriptor object` which contains a destination mix descriptor
and a destination queue ID.

## Receiving Thin Client Events and Service Reply Messages

It's worth noting that our Go thin client implementation gives you
an events channel for receiving events from the client daemon, whereas
the Python and Rust thin clients allow you to specify callbacks for
each event type. Both approaches are equivalent to each other. HOWEVER,
the events channel approach is more flexible and allows you to
easily write higher level abstractions that do automatic retries.
So we might consider updating our Rust and Python thin clients to use
the events channel approach.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
thin := thin.NewThinClient(cfg)
err = thin.Dial()
if err != nil {
    panic(err)
}

// Use EventSink() to get a channel of events
eventCh := thin.EventSink()
for ev := range eventCh {
    switch ev.(type) {
        case *thin.NewDocumentEvent:
            // handle new PKI document event
        case *thin.MessageReplyEvent:
            // handle message reply event
        case *thin.ConnectionStatusEvent:
            // handle connection status change
        default:
            // handle other events
    }
}
{{< /tab >}}

{{< tab header="Rust" lang="rust" >}}
// Set up event callbacks when creating the client
let mut thin_client = ThinClient::new(config)
    .on_new_document(|doc| {
        // handle new PKI document
    })
    .on_message_reply(|reply| {
        // handle message reply
    })
    .on_connection_status(|status| {
        // handle connection status change
    });

thin_client.start().await?;
{{< /tab >}}

{{< tab header="Python" lang="python" >}}
# Define callback functions
def on_new_document(doc):
    # handle new PKI document
    pass

def on_message_reply(reply):
    # handle message reply
    pass

def on_connection_status(status):
    # handle connection status change
    pass

# Create client with callbacks
thin_client = ThinClient(
    config,
    on_new_document=on_new_document,
    on_message_reply=on_message_reply,
    on_connection_status=on_connection_status
)

thin_client.start()
{{< /tab >}}
{{< /tabpane >}}

### Thin client events

Here I'll tell you a bit about each of the events that thin clients
receive. Firstly, these are the core events that all thin clients
receive:

* `shutdown_event`: This event tells your application that the Katzenpost
  client daemon is shutting down.

* `connection_status_event`: This event notifies your app of a network
  connectvity status change, which is either connected or not
  connected.

* `new_pki_document_event`: This event tells encapsulates the new PKI
  document, a view of the network, including a list of network
  services.



## Pigeonhole Channel API

This API is designed to allow applications to use the Pigeonhole
protocol to send and receive messages to and from storage channels.
These channels can be thought of as storing a stream of bytes however
they are in fact composed as a sequence of encrypted BACAP Boxes.

* BACAP, the Blinded and Capability protocol is described in our paper
in section 4: https://arxiv.org/abs/2501.02933

* Pigeonhole, the storage protocol is described in our paper
in section 5: https://arxiv.org/abs/2501.02933

* The Golang reference implementation of BACAP can be found here:<BR>
https://github.com/katzenpost/hpqc/blob/main/bacap/bacap.go

* The BACAP golang API documentation here:<BR>
https://pkg.go.dev/github.com/katzenpost/hpqc/bacap

Each of these Pigeonhole channels has a read capability often
referred to as just "readcap" and a write capability often
referred to as just "writecap" and a message index. A KDF is used
to derive a sequence of message indexes from the first message index.

This API endeavors to avoid storing state in the client daemon whenever possible. We instead prefer to return enough information to the app so that it can
keep track of the state itself.

**NOTE that each of the API messages are implemented using a query message type and
a reply message type. Therefore each message in this API contains a query ID field so
that the reply can be correlated with the request. If a client
ever repeats one of these (for something we have in memory) and
we are posed with the question of whether we should overwrite
something or not, we send an event saying "protocol violation"
and disconnects the thinclient.**

Our new Pigeonhole API consists of these methods:

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}

func (t *ThinClient) NewKeypair(
	ctx context.Context,
	seed []byte,
) (writeCap *bacap.WriteCap,
	readCap *bacap.ReadCap,
	firstMessageIndex *bacap.MessageBoxIndex,
	err error)

func (t *ThinClient) EncryptRead(
	ctx context.Context,
	readCap *bacap.ReadCap,
	messageBoxIndex *bacap.MessageBoxIndex,
) (messageCiphertext []byte,
	nextMessageIndex []byte,
	envelopeDescriptor []byte,
	envelopeHash *[32]byte,
	err error)

func (t *ThinClient) EncryptWrite(
	ctx context.Context,
	plaintext []byte,
	writeCap *bacap.WriteCap,
	messageBoxIndex *bacap.MessageBoxIndex,
) (messageCiphertext []byte,
	envelopeDescriptor []byte,
	envelopeHash *[32]byte,
	err error)

func (t *ThinClient) StartResendingEncryptedMessage(
	ctx context.Context,
	readCap *bacap.ReadCap,
	writeCap *bacap.WriteCap,
	nextMessageIndex []byte,
	replyIndex *uint8,
	envelopeDescriptor []byte,
	messageCiphertext []byte,
	envelopeHash *[32]byte,
) (plaintext []byte, err error)

func (t *ThinClient) CancelResendingEncryptedMessage(
	ctx context.Context,
	envelopeHash *[32]byte,
) error

func (t *ThinClient) StartResendingCopyCommandWithCourier(
	ctx context.Context,
	writeCap *bacap.WriteCap,
	courierIdentityHash *[32]byte,
	courierQueueID []byte,
) error

func (t *ThinClient) CancelResendingCopyCommand(
	ctx context.Context,
	writeCapHash *[32]byte,
) error

func (t *ThinClient) NextMessageBoxIndex(
	ctx context.Context,
	messageBoxIndex *bacap.MessageBoxIndex,
) (nextMessageBoxIndex *bacap.MessageBoxIndex, err error)

func (t *ThinClient) NewStreamID() *[StreamIDLength]byte

func (t *ThinClient) CreateCourierEnvelopesFromPayload(
	ctx context.Context,
	streamID *[StreamIDLength]byte,
	payload []byte,
	destWriteCap *bacap.WriteCap,
	destStartIndex *bacap.MessageBoxIndex,
	isLast bool,
) (envelopes [][]byte, err error)

func (t *ThinClient) CreateCourierEnvelopesFromMultiPayload(
	ctx context.Context,
	streamID *[StreamIDLength]byte,
	destinations []DestinationPayload,
	isLast bool,
) (*CreateEnvelopesResult, error)
// CreateEnvelopesResult contains Envelopes [][]byte and Buffer []byte

func (t *ThinClient) SetStreamBuffer(
	ctx context.Context,
	streamID *[StreamIDLength]byte,
	buffer []byte,
) error

func (c *ThinClient) TombstoneBox(
	ctx context.Context,
	writeCap *bacap.WriteCap,
	boxIndex *bacap.MessageBoxIndex,
) (messageCiphertext []byte, envelopeDescriptor []byte, envelopeHash *[32]byte, err error)

func (c *ThinClient) TombstoneRange(
	ctx context.Context,
	writeCap *bacap.WriteCap,
	start *bacap.MessageBoxIndex,
	maxCount uint32,
) (*TombstoneRangeResult, error)
// TombstoneRangeResult contains Envelopes []*TombstoneEnvelope and Next *bacap.MessageBoxIndex
// TombstoneEnvelope contains MessageCiphertext, EnvelopeDescriptor, EnvelopeHash, and BoxIndex
{{< /tab >}}

{{< tab header="Python" lang="python" >}}
async def new_keypair(self, seed: bytes) -> "Tuple[bytes, bytes, bytes]"

async def encrypt_read(
    self,
    read_cap: bytes,
    message_box_index: bytes
) -> EncryptReadResult
# EncryptReadResult contains: message_ciphertext, next_message_index,
#     envelope_descriptor, envelope_hash

async def encrypt_write(
    self,
    plaintext: bytes,
    write_cap: bytes,
    message_box_index: bytes
) -> EncryptWriteResult
# EncryptWriteResult contains: message_ciphertext, envelope_descriptor,
#     envelope_hash

async def start_resending_encrypted_message(
    self,
    read_cap: "bytes|None",
    write_cap: "bytes|None",
    next_message_index: "bytes|None",
    reply_index: "int|None",
    envelope_descriptor: bytes,
    message_ciphertext: bytes,
    envelope_hash: bytes
) -> bytes

async def cancel_resending_encrypted_message(self, envelope_hash: bytes) -> None

async def next_message_box_index(self, message_box_index: bytes) -> bytes

async def start_resending_copy_command(
    self,
    write_cap: bytes,
    courier_identity_hash: "bytes|None" = None,
    courier_queue_id: "bytes|None" = None
) -> None:

async def cancel_resending_copy_command(self, write_cap_hash: bytes) -> None:

async def create_courier_envelopes_from_payload(
    self,
    query_id: bytes,
    stream_id: bytes,
    payload: bytes,
    dest_write_cap: bytes,
    dest_start_index: bytes,
    is_last: bool
) -> "CreateEnvelopesResult":
# Returns CreateEnvelopesResult with envelopes and buffer for crash recovery

async def create_courier_envelopes_from_multi_payload(
    self,
    stream_id: bytes,
    destinations: "List[Dict[str, Any]]",
    is_last: bool
) -> "CreateEnvelopesResult":
# Returns CreateEnvelopesResult with envelopes and buffer for crash recovery

async def set_stream_buffer(
    self,
    stream_id: bytes,
    buffer: bytes
) -> None:
# Restore stream buffer state after crash recovery

async def tombstone_box(
    self,
    write_cap: bytes,
    box_index: bytes
) -> "Tuple[bytes, bytes, bytes]":
# Returns (message_ciphertext, envelope_descriptor, envelope_hash)

async def tombstone_range(
    self,
    write_cap: bytes,
    start: bytes,
    max_count: int
) -> "Dict[str, Any]":
# Returns {"envelopes": [...], "next": next_index}
# Each envelope contains: message_ciphertext, envelope_descriptor, envelope_hash, box_index
{{< /tab >}}

{{< tab header="Rust" lang="rust" >}}
    pub async fn new_keypair(
        &self,
        seed: &[u8; 32]
    ) -> Result<(Vec<u8>, Vec<u8>, Vec<u8>), ThinClientError>

    pub async fn encrypt_read(
        &self,
        read_cap: &[u8],
        message_box_index: &[u8]
    ) -> Result<(Vec<u8>, Vec<u8>, Vec<u8>, [u8; 32]), ThinClientError>

    pub async fn encrypt_write(
        &self,
        plaintext: &[u8],
        write_cap: &[u8],
        message_box_index: &[u8]
    ) -> Result<(Vec<u8>, Vec<u8>, [u8; 32]), ThinClientError>

    pub async fn start_resending_encrypted_message(
        &self,
        read_cap: Option<&[u8]>,
        write_cap: Option<&[u8]>,
        next_message_index: Option<&[u8]>,
        reply_index: Option<u8>,
        envelope_descriptor: &[u8],
        message_ciphertext: &[u8],
        envelope_hash: &[u8; 32]
    ) -> Result<Vec<u8>, ThinClientError>

    pub async fn cancel_resending_encrypted_message(
        &self,
        envelope_hash: &[u8; 32]
    ) -> Result<(), ThinClientError>

    pub async fn next_message_box_index(
        &self,
        message_box_index: &[u8]
    ) -> Result<Vec<u8>, ThinClientError>

    pub async fn start_resending_copy_command(
        &self,
        write_cap: &[u8],
        courier_identity_hash: Option<&[u8]>,
        courier_queue_id: Option<&[u8]>
    ) -> Result<(), ThinClientError>

    pub async fn cancel_resending_copy_command(
        &self,
        write_cap_hash: &[u8; 32]
    ) -> Result<(), ThinClientError>

    pub async fn create_courier_envelopes_from_payload(
        &self,
        stream_id: &[u8; 16],
        payload: &[u8],
        dest_write_cap: &[u8],
        dest_start_index: &[u8],
        is_last: bool
    ) -> Result<CreateEnvelopesResult, ThinClientError>
    // CreateEnvelopesResult contains: envelopes: Vec<Vec<u8>>, buffer: Vec<u8>

    pub async fn create_courier_envelopes_from_multi_payload(
        &self,
        stream_id: &[u8; 16],
        destinations: Vec<(&[u8], &[u8], &[u8])>,
        is_last: bool
    ) -> Result<CreateEnvelopesResult, ThinClientError>

    pub async fn set_stream_buffer(
        &self,
        stream_id: &[u8; 16],
        buffer: Vec<u8>
    ) -> Result<(), ThinClientError>

   pub fn new_stream_id() -> [u8; 16]

   pub async fn tombstone_box(
        &self,
        write_cap: &[u8],
        box_index: &[u8]
    ) -> Result<(Vec<u8>, Vec<u8>, Vec<u8>), ThinClientError>
    // Returns (ciphertext, envelope_descriptor, envelope_hash)

    pub async fn tombstone_range(
        &self,
        write_cap: &[u8],
        start: &[u8],
        max_count: u32
    ) -> TombstoneRangeResult
    // TombstoneRangeResult contains: envelopes: Vec<TombstoneEnvelope>, next: Vec<u8>
    // TombstoneEnvelope contains: message_ciphertext, envelope_descriptor, envelope_hash, box_index
{{< /tab >}}
{{< /tabpane >}}

<HR>
<BR>

Most of the methods in the new Pigeonhole API do NOT cause any network traffic.
The only methods that cause network traffic and cause the client daemon to keep state are these two:

* Start Resending Encrypted Message
* Start Resending Copy Command

Also note that this method is the only one that can cause the client daemon to keep state between calls:

* Create Courier Envelopes From Payloads

Therefore most of the API methods are very fast and do not require any network traffic
or for the client daemon to keep state. They are cryptographic operations that are performed
locally by the client daemon:

* New Keypair
* Encrypt Read
* Encrypt Write
* Next Message Box Index
* Tombstone Box
* Tombstone Range

<HR>
<BR>

## Example Usage

The following example shows how Alice can send a message to Bob using Pigeonhole channels.
Alice shares the `read_cap` and `index` with Bob out-of-band via a secure channel.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// ==================== ALICE'S SIDE (Sender) ====================

// SendMessage encrypts and sends a message to a Pigeonhole channel.
// The writeCap and index should be created beforehand via NewKeypair.
func SendMessage(ctx context.Context, client *ThinClient,
    message []byte, writeCap *bacap.WriteCap, index *bacap.MessageBoxIndex) error {

    // Encrypt the message for writing
    ciphertext, envDesc, envHash, err := client.EncryptWrite(ctx, message, writeCap, index)
    if err != nil {
        return err
    }

    // Send the encrypted message via ARQ (automatic retransmission)
    _, err = client.StartResendingEncryptedMessage(
        ctx, nil, writeCap, nil, 0, envDesc, ciphertext, envHash)
    return err
}

// ==================== BOB'S SIDE (Receiver) ====================

// ReceiveMessage retrieves and decrypts a message from a Pigeonhole channel.
// The readCap and index should be shared by Alice out-of-band.
func ReceiveMessage(ctx context.Context, client *ThinClient,
    readCap *bacap.ReadCap, index *bacap.MessageBoxIndex) ([]byte, error) {

    // Encrypt a read request for the given index
    ciphertext, nextIndex, envDesc, envHash, err := client.EncryptRead(ctx, readCap, index)
    if err != nil {
        return nil, err
    }

    // Retrieve the message via ARQ
    plaintext, err := client.StartResendingEncryptedMessage(
        ctx, readCap, nil, nextIndex, 0, envDesc, ciphertext, envHash)
    if err != nil {
        return nil, err
    }

    return plaintext, nil
}
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
# ==================== ALICE'S SIDE (Sender) ====================

async def send_message(
    client: ThinClient,
    message: bytes,
    write_cap: bytes,
    index: bytes,
) -> None:
    """
    Encrypts and sends a message to a Pigeonhole channel.
    The write_cap and index should be created beforehand via new_keypair.
    """
    # Encrypt the message for writing
    ciphertext, env_desc, env_hash = await client.encrypt_write(
        message, write_cap, index
    )

    # Send the encrypted message via ARQ (automatic retransmission)
    await client.start_resending_encrypted_message(
        read_cap=None,
        write_cap=write_cap,
        next_message_index=None,
        reply_index=0,
        envelope_descriptor=env_desc,
        message_ciphertext=ciphertext,
        envelope_hash=env_hash
    )


# ==================== BOB'S SIDE (Receiver) ====================

async def receive_message(
    client: ThinClient,
    read_cap: bytes,
    index: bytes,
) -> bytes:
    """
    Retrieves and decrypts a message from a Pigeonhole channel.
    The read_cap and index should be shared by Alice out-of-band.
    """
    # Encrypt a read request for the given index
    ciphertext, next_index, env_desc, env_hash = await client.encrypt_read(
        read_cap, index
    )

    # Retrieve the message via ARQ
    plaintext = await client.start_resending_encrypted_message(
        read_cap=read_cap,
        write_cap=None,
        next_message_index=next_index,
        reply_index=0,
        envelope_descriptor=env_desc,
        message_ciphertext=ciphertext,
        envelope_hash=env_hash
    )

    return plaintext
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// ==================== ALICE'S SIDE (Sender) ====================

/// Encrypts and sends a message to a Pigeonhole channel.
/// The write_cap and index should be created beforehand via new_keypair.
async fn send_message(
    client: &ThinClient,
    message: &[u8],
    write_cap: &[u8],
    index: &[u8],
) -> Result<(), ThinClientError> {
    // Encrypt the message for writing
    let (ciphertext, env_desc, env_hash) = client
        .encrypt_write(message, write_cap, index).await?;

    // Send the encrypted message via ARQ (automatic retransmission)
    client.start_resending_encrypted_message(
        None,
        Some(write_cap),
        None,
        0,
        &env_desc,
        &ciphertext,
        &env_hash
    ).await?;

    Ok(())
}

// ==================== BOB'S SIDE (Receiver) ====================

/// Retrieves and decrypts a message from a Pigeonhole channel.
/// The read_cap and index should be shared by Alice out-of-band.
async fn receive_message(
    client: &ThinClient,
    read_cap: &[u8],
    index: &[u8],
) -> Result<Vec<u8>, ThinClientError> {
    // Encrypt a read request for the given index
    let (ciphertext, next_index, env_desc, env_hash) = client
        .encrypt_read(read_cap, index).await?;

    // Retrieve the message via ARQ
    let plaintext = client.start_resending_encrypted_message(
        Some(read_cap),
        None,
        Some(&next_index),
        0,
        &env_desc,
        &ciphertext,
        &env_hash
    ).await?;

    Ok(plaintext)
}
{{< /tab >}}
{{< /tabpane >}}

## New Key Pair

The `NewKeypair` method generates a new BACAP keypair which are referred to as the writecap and readcap,
it also returns a first message index which is used to derive a sequence of message indexes using the `Next Message Box Index` method.

These Pigeonhole channels store a stream of data in
a sequence of BACAP boxes. The `NewKeypair` method returns the write
capability for the channel, the read capability for the channel, and the
index of the first box in the channel. These can be used by the application
at any time to read or write to the channel.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
seed := make([]byte, 32)
_, err := rand.Reader.Read(seed)
if err != nil {
    return err
}
writeCap, readCap, firstIndex, err := thinClient.NewKeypair(ctx, seed)
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
seed = os.urandom(32)
write_cap, read_cap, first_index = await thin_client.new_keypair(seed)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
let seed: [u8; 32] = rand::random();
let (write_cap, read_cap, first_index) = thin_client.new_keypair(&seed).await?;
{{< /tab >}}
{{< /tabpane >}}

## Next Message Box Index

This method does NOT cause any network traffic or state changes. It simply tells you the next message box index
that will be used for the next message. This is useful for planning ahead and for saving state.

If you have a binary compatible BACAP implementation in your target language then of course you can use that instead of this method and avoid the round trip on the local socket to the client daemon.


{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
nextIndex, err = thinClient.NextMessageBoxIndex(ctx, firstIndex)
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
next_index = await thin_client.next_message_box_index(first_index)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
let next_index = thin_client.next_message_box_index(&first_index).await?;
{{< /tab >}}
{{< /tabpane >}}


## Encrypt Read

This method returns an encrypted read request for a single Pigeonhole/BACAP Box. This method does not cause any network traffic nor does it cause the client daemon to store any state. The encrypted read transaction blob returned must be sent to a courier using the `StartResendingEncryptedMessage` method.

**Note:** The `next_message_index` (or `nextMessageIndex`) field returned by this method is misnamed — it is actually the *current* index, not the next one. This field will be removed from the API in a future release. To advance to the next index after a read, call `NextMessageBoxIndex` explicitly.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
messageCiphertext, nextMessageIndex, envelopeDescriptor, envelopeHash, err := thinClient.EncryptRead(ctx, readCap, messageBoxIndex)
reply, err := thinClient.StartResendingEncryptedMessage(ctx, readCap, nil, nextMessageIndex, 0, envelopeDescriptor, messageCiphertext, envelopeHash)
// Save the state so we can resume if needed
clientState.Save(writeCap, readCap, nextMessageIndex, envelopeHash)
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
ciphertext, next_index, env_desc, env_hash = await thin_client.encrypt_read(
    read_cap, message_box_index
)
plaintext = await thin_client.start_resending_encrypted_message(
    read_cap=read_cap,
    write_cap=None,
    next_message_index=next_index,
    reply_index=0,  
    envelope_descriptor=env_desc,
    message_ciphertext=ciphertext,
    envelope_hash=env_hash
)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
let (ciphertext, next_index, env_desc, env_hash) = thin_client
    .encrypt_read(&read_cap, &message_box_index).await?;
let plaintext = thin_client.start_resending_encrypted_message(
    Some(&read_cap),
    None,
    Some(&next_index),
    0,
    &env_desc,
    &ciphertext,
    &env_hash
).await?;
{{< /tab >}}
{{< /tabpane >}}

## Encrypt Write

This method returns an encrypted write request for a single Pigeonhole/BACAP Box. This method does not cause any network traffic nor does it cause the client daemon to store any state. The encrypted write transaction blob returned must be sent to a courier using the `StartResendingEncryptedMessage` method.

**Note:** After a successful write, call `NextMessageBoxIndex` to advance the index before writing the next message.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
messageCiphertext, envelopeDescriptor, envelopeHash, err := thinClient.EncryptWrite(ctx, plaintext, writeCap, messageBoxIndex)
err := thinClient.StartResendingEncryptedMessage(ctx, nil, writeCap, nil, 0, envelopeDescriptor, messageCiphertext, envelopeHash)
// Save the state so we can resume if needed
clientState.Save(writeCap, readCap, nextMessageIndex, envelopeHash)
{{< /tab >}}

{{< tab header="Python" lang="python" >}}
ciphertext, env_desc, env_hash = await thin_client.encrypt_write(
    plaintext, write_cap, message_box_index
)
await thin_client.start_resending_encrypted_message(
    read_cap=None,
    write_cap=write_cap,
    next_message_index=None,
    reply_index=0,
    envelope_descriptor=env_desc,
    message_ciphertext=ciphertext,
    envelope_hash=env_hash
)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
let (ciphertext, env_desc, env_hash) = thin_client
    .encrypt_write(&plaintext, &write_cap, &message_box_index).await?;
thin_client.start_resending_encrypted_message(
    None,
    Some(&write_cap),
    None,
    0,
    &env_desc,
    &ciphertext,
    &env_hash
).await?;
{{< /tab >}}

{{< /tabpane >}}

<BR>


## Start Resending Encrypted Message

This method takes your message ciphertext and sends it off
to a courier for delivery to the storage replicas. It does
so using a basic ARQ - automatic repeat request - protocol
which sends retransmissions if it doesn't get an ACK from
the courier.

This method is designed to block until an ACK is received
from the courier or until `CancelResendingEncryptedMessage` is called.

**Errors returned by this method:**

*Read-only errors (when `read_cap` is set):*

* `ErrMKEMDecryptionFailed` — MKEM envelope decryption failed with all replica keys. Indicates corruption or key mismatch.
* `ErrBACAPDecryptionFailed` — BACAP payload decryption or signature verification failed. Indicates invalid credentials or corrupted data.
* `ErrBoxIDNotFound` — The requested box does not exist on the replica. By default, the operation retries up to 10 times to handle replication lag before returning this error. Use `StartResendingEncryptedMessageNoRetry` to get an immediate error without retries.

*Write-only errors (when `write_cap` is set):*

* `ErrBoxAlreadyExists` — The box already contains data. By default this is treated as idempotent success. Use `StartResendingEncryptedMessageReturnBoxExists` if you need to distinguish a new write from a repeated one.
* `ErrStorageFull` — The replica's storage capacity has been exceeded.

*Errors that apply to both reads and writes:*

* `ErrStartResendingCancelled` — The operation was cancelled via `CancelResendingEncryptedMessage`.
* `ErrInvalidBoxID` — The box ID format is invalid or malformed.
* `ErrInvalidSignature` — Signature verification failed during envelope processing.
* `ErrDatabaseFailure` — The replica encountered a database error.
* `ErrInvalidPayload` — The payload data is invalid.
* `ErrReplicaInternalError` — An internal error occurred on the replica.
* `ErrInvalidEpoch` — The epoch is invalid or has expired.
* `ErrReplicationFailed` — Replication to other replicas failed.
* `ErrInvalidEnvelope` — The courier envelope format is invalid.
* `ErrPropagationError` — The request could not be propagated to replicas.
* `ErrInternalError` — An internal client daemon error occurred.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
messageCiphertext, envelopeDescriptor, envelopeHash, err := thinClient.EncryptWrite(ctx, plaintext, writeCap, messageBoxIndex)
reply, err := thinClient.StartResendingEncryptedMessage(ctx, readCap, writeCap, nextMessageIndex, replyIndex, envelopeDescriptor, messageCiphertext, envelopeHash)
{{< /tab >}}

{{< tab header="Python" lang="python" >}}
# For writes (read_cap=None), for reads (write_cap=None)
plaintext = await thin_client.start_resending_encrypted_message(
    read_cap=read_cap,
    write_cap=write_cap,
    next_message_index=next_index,
    reply_index=0,
    envelope_descriptor=env_desc,
    message_ciphertext=ciphertext,
    envelope_hash=env_hash
)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// For writes use None for read_cap, for reads use None for write_cap
let plaintext = thin_client.start_resending_encrypted_message(
    Some(&read_cap),  // None for writes
    Some(&write_cap), // None for reads
    Some(&next_index),
    0,
    &env_desc,
    &ciphertext,
    &env_hash
).await?;
{{< /tab >}}

{{< /tabpane >}}

**Some notes on implementation:**
* kpclientd picks DestNode + DestQueue (courier)
* kpclientd puts each SendEncryptedMessage in an in-memory queue and takes responsibility for resending, so the thin client only needs to send SendEncryptedMessage once per session.
* In-memory queue: one per app
* kpclientd samples from the collection of all the app queues and puts the "resending" into the egress queue
* when an app disconnects we delete their queue
* when does it stop resending?
* we want to stop resending writes once the courier acks
* kpclientd should stop resending the corresponding write.
* kpclientd should emit an event to tell the app their write was successful
* we want to keep a cache of EnvelopeHash->event so that if an app restarts it can get replies to stuff it just sent (that was answered successfully)
* maybe rotate couriers every now and then
* we want to stop resending reads once there is a successful read
* we should emit an event on successful read
* with our current bug we need to stop resending as soon as we get an error from a 
* we should emit an event on "box not found"

## Cancel Resending Encrypted Message

This method is meant to be called from a different thread in order to cancel
a previously called `StartResendingEncryptedMessage` call.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
reply, err := thinClient.StartResendingEncryptedMessage(ctx, readCap, writeCap, nextMessageIndex, replyIndex, envelopeDescriptor, messageCiphertext, envelopeHash)

go func() {
    thinClient.CancelResendingEncryptedMessage(ctx, envelopeHash)
}()
{{< /tab >}}

{{< tab header="Python" lang="python" >}}
# Cancel from another coroutine
await thin_client.cancel_resending_encrypted_message(env_hash)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// Cancel from another task
thin_client.cancel_resending_encrypted_message(&env_hash).await?;
{{< /tab >}}

{{< /tabpane >}}


## Tombstone Box

Create an encrypted tombstone for a single box. A tombstone is a BACAP message with a payload composed of all zeros, used to delete messages.

This method returns the encrypted envelope data without sending it. The caller must send the tombstone via `StartResendingEncryptedMessage`, which allows for cancellation using the returned envelope hash.

**Note:** After tombstoning a box, call `NextMessageBoxIndex` to advance the index before tombstoning the next box. If you need to tombstone a consecutive range of boxes, use `TombstoneRange` instead, which handles index advancement internally.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// Create the encrypted tombstone
ciphertext, envDesc, envHash, err := alice.TombstoneBox(ctx, geo, writeCap, firstIndex)
if err != nil {
    return err
}

// Send the tombstone (can be cancelled with CancelResendingEncryptedMessage(envHash))
_, err = alice.StartResendingEncryptedMessage(
    ctx, nil, writeCap, nil, nil,
    envDesc, ciphertext, envHash,
)
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
# Create the encrypted tombstone
ciphertext, env_desc, env_hash = await thin_client.tombstone_box(geometry, write_cap, first_index)

# Send the tombstone (can be cancelled with cancel_resending_encrypted_message(env_hash))
await thin_client.start_resending_encrypted_message(
    read_cap=None,
    write_cap=write_cap,
    next_message_index=None,
    reply_index=None,
    envelope_descriptor=env_desc,
    message_ciphertext=ciphertext,
    envelope_hash=env_hash
)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// Create the encrypted tombstone
let (ciphertext, env_desc, env_hash) = thin_client
    .tombstone_box(&geometry, &write_cap, &first_index).await?;

// Send the tombstone (can be cancelled with cancel_resending_encrypted_message(&env_hash))
thin_client.start_resending_encrypted_message(
    None,
    Some(&write_cap),
    None,
    0,
    &env_desc,
    &ciphertext,
    &env_hash
).await?;
{{< /tab >}}
{{< /tabpane >}}

## Tombstone Range

Create encrypted tombstones for a range of consecutive boxes. Returns a list of envelope data that the caller must send individually via `StartResendingEncryptedMessage`.

This design allows the caller to control when tombstones are sent, send them in parallel, or cancel any in-flight tombstone using its envelope hash.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// Create tombstone envelopes for 10 boxes
result, err := thinClient.TombstoneRange(ctx, geo, writeCap, firstIndex, 10)
if err != nil {
    return err
}

// Send each tombstone envelope
for _, envelope := range result.Envelopes {
    _, err = thinClient.StartResendingEncryptedMessage(
        ctx, nil, writeCap, nil, nil,
        envelope.EnvelopeDescriptor, envelope.MessageCiphertext, envelope.EnvelopeHash,
    )
    if err != nil {
        return err
    }
}
// result.Next contains the next index after the last tombstoned box
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
# Create tombstone envelopes for 10 boxes
result = await thin_client.tombstone_range(geometry, write_cap, first_index, 10)

# Send each tombstone envelope
for envelope in result["envelopes"]:
    await thin_client.start_resending_encrypted_message(
        read_cap=None,
        write_cap=write_cap,
        next_message_index=None,
        reply_index=None,
        envelope_descriptor=envelope["envelope_descriptor"],
        message_ciphertext=envelope["message_ciphertext"],
        envelope_hash=envelope["envelope_hash"]
    )
# result["next"] contains the next index after the last tombstoned box
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// Create tombstone envelopes for 10 boxes
let result = thin_client.tombstone_range(&geometry, &write_cap, &first_index, 10).await;

// Send each tombstone envelope
for envelope in &result.envelopes {
    thin_client.start_resending_encrypted_message(
        None,
        Some(&write_cap),
        None,
        0,
        &envelope.envelope_descriptor,
        &envelope.message_ciphertext,
        &envelope.envelope_hash
    ).await?;
}
// result.next contains the next index after the last tombstoned box
{{< /tab >}}
{{< /tabpane >}}


<HR>
<BR>

## **COPY COMMAND SECTION**

Here we discuss the "All Or Nothing" protocol from our papper:
https://arxiv.org/abs/2501.02933

The whole point of this section of the Pigeonhole API is to provide a way to make multiple transactions to one or more channels atomically.

Below we present several methods that are of use when sending copy commands:

* StartResendingCopyCommand
* CancelResendingCopyCommand
* NewStreamID
* CreateCourierEnvelopesFromPayload
* CreateCourierEnvelopesFromMultiPayload
* SetStreamBuffer

The idea here is that you have some data that you want
to send to one or more channels. You create a temporary
channel and a series of Courier Envelopes that describe
how to write that data. Each of these envelopes could be
writing to a new channel or the same channel.

```
  A BACAP Box payload is N bytes max.
  A Courier Envelope (contains a full box payload + metadata).
  Total envelope size > N bytes, so a single envelope cannot fit in one box.
  Therefore, envelopes are serialized and split across multiple boxes
  in the temporary copy stream:

  TEMPORARY COPY STREAM BOXES (each holds N bytes):
  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
  │    Box 0    │ │    Box 1    │ │    Box 2    │ │    Box 3    │ │    Box 4    │
  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘

  SERIALIZED ENVELOPE DATA (envelope boundaries don't align with box boundaries):
  ┌─────────────────────────┐┌────────────────────┐┌──────────────────────────┐
  │       Envelope 1        ││     Envelope 2     ││       Envelope 3         │
  └─────────────────────────┘└────────────────────┘└──────────────────────────┘
  |         |         |         |         |         |
       Box 0     Box 1     Box 2     Box 3     Box 4
```

When we are done writing these envelopes to our
temporary channel, we send a copy command to a courier
which takes the given write cap and derives the read cap
and then uses that read cap to read the envelopes from the temporary channel; the courier processes each envelope and writes the described data to the described channel.

We make the API explicitly say when we are terminating
our temporary copy stream by using the `isFinal` boolean
flag in the `Create Courier Envelopes From Payload` and `Create Courier Envelopes From Payloads` methods.
This results in the last box in the stream having the `isFinal` flag set to true. This is how the courier knows that it has reached the end of the stream and that there are no more boxes to read.

We use `Create Courier Envelopes From Payload` and `Create Courier Envelopes From Multi Payload` to create these envelopes.
The returned values are properly sized chunks that fit perfectly into a BACAP box. This means that our next step is to encrypt each of them with `Encrypt Write`
and then send the resulting ciphertext to a courier using `Start Resending Encrypted Message`.

After we've sent all the data to the temporary stream
we compose a Copy Command with the write cap for the
temporary channel and send it to a courier using
`Start Resending Copy Command`.

When the courier receives the copy command it
derives the read cap from the write cap and then
reads the envelopes from the temporary channel and
executes them. After that it overwrites the temporary
channel with tombstones using the write cap it
received in the copy command. Next it sends an ACK back to the client.

`Start Resending Copy Command` is a blocking method that
uses a simple ARQ to do retransmissions when it doesn't receive a reply from the courier. It will retry forever
until it either receives a reply from the courier or
`Cancel Resending Copy Command` is called.
The reply from the courier indicates if the copy was successful or not. 

If successful, the next step is for the client to send the destination stream read cap to someone who is interested in the data that was just copied there by the courier processing the copy command.


{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
destSeed := make([]byte, 32)
_, err := rand.Reader.Read(destSeed)
if err != nil {
    panic(err)
}

destWriteCap, bobReadCap, destFirstIndex, err := thinClient.NewKeypair(ctx, destSeed)
if err != nil {
    panic(err)
}

streamID := thinClient.NewStreamID()
envelopes, err := thinClient.CreateCourierEnvelopesFromPayload(ctx, streamID, payload, destWriteCap, destFirstIndex, true)

for _, chunk := range envelopes {
    ciphertext, envDesc, envHash, err := thinClient.EncryptWrite(ctx, chunk, tempWriteCap, tempIndex)
    err := thinClient.StartResendingEncryptedMessage(ctx, nil, tempWriteCap, nil, 0, envDesc, ciphertext, envHash)
    if err != nil {
        panic(err)
    }
    tempIndex, err = thinClient.NextMessageBoxIndex(ctx, tempIndex)
    if err != nil {
        panic(err)
    }
}

err := thinClient.StartResendingCopyCommand(ctx, tempWriteCap)
if err != nil {
    panic(err)
}

// share dest read cap with Bob here...
// called `bobReadCap`
{{< /tab >}}

{{< tab header="Python" lang="python" >}}
# Create destination channel
dest_seed = os.urandom(32)
dest_write_cap, bob_read_cap, dest_first_index = await thin_client.new_keypair(dest_seed)

# Create temporary copy stream channel
temp_seed = os.urandom(32)
temp_write_cap, _, temp_first_index = await thin_client.new_keypair(temp_seed)

# Create courier envelopes from payload
stream_id = thin_client.new_stream_id()
query_id = thin_client.new_query_id()
chunks = await thin_client.create_courier_envelopes_from_payload(
    query_id, stream_id, payload, dest_write_cap, dest_first_index, True  # is_last
)

# Write chunks to temporary channel
temp_index = temp_first_index
for chunk in chunks:
    ciphertext, env_desc, env_hash = await thin_client.encrypt_write(
        chunk, temp_write_cap, temp_index
    )
    await thin_client.start_resending_encrypted_message(
        read_cap=None, write_cap=temp_write_cap, next_message_index=None,
        reply_index=0, envelope_descriptor=env_desc,
        message_ciphertext=ciphertext, envelope_hash=env_hash
    )
    temp_index = await thin_client.next_message_box_index(temp_index)

# Send copy command
await thin_client.start_resending_copy_command(temp_write_cap)
# Share bob_read_cap with Bob
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// Create destination channel
let dest_seed: [u8; 32] = rand::random();
let (dest_write_cap, bob_read_cap, dest_first_index) = thin_client.new_keypair(&dest_seed).await?;

// Create temporary copy stream channel
let temp_seed: [u8; 32] = rand::random();
let (temp_write_cap, _, temp_first_index) = thin_client.new_keypair(&temp_seed).await?;

// Create courier envelopes from payload
let stream_id = ThinClient::new_stream_id();
let chunks = thin_client.create_courier_envelopes_from_payload(
    &stream_id, &payload, &dest_write_cap, &dest_first_index, true
).await?;

// Write chunks to temporary channel
let mut temp_index = temp_first_index;
for chunk in chunks {
    let (ciphertext, env_desc, env_hash) = thin_client
        .encrypt_write(&chunk, &temp_write_cap, &temp_index).await?;
    thin_client.start_resending_encrypted_message(
        None, Some(&temp_write_cap), None, 0, &env_desc, &ciphertext, &env_hash
    ).await?;
    temp_index = thin_client.next_message_box_index(&temp_index).await?;
}

// Send copy command
thin_client.start_resending_copy_command(&temp_write_cap, None, None).await?;
// Share bob_read_cap with Bob
{{< /tab >}}

{{< /tabpane >}}


<BR>
<HR>

## Start Resending Copy Command

Sends a copy command via ARQ and blocks until completion.

This method BLOCKS until a reply is received. It uses the ARQ (Automatic Repeat reQuest)
mechanism to reliably send copy commands to the courier, automatically retrying if
the reply is not received in time.

The copy command instructs the courier to read from a temporary copy stream channel
and write the parsed envelopes to their destination channels. The courier:
  1. Derives a ReadCap from the WriteCap
  2. Reads boxes from the temporary channel
  3. Parses boxes into CourierEnvelopes
  4. Sends each envelope to intermediate replicas for replication
  5. Writes tombstones to clean up the temporary channel
  6. Sends an ACK to the client

Parameters:
   - ctx: Context for cancellation and timeout control
   - writeCap: Write capability for the temporary copy stream channel

Returns:
   - error: Any error encountered during the operation


{{< tabpane >}}
{{< tab header="Go" lang="go" >}}

// Create temporary copy stream channel
tempSeed := make([]byte, 32)
_, err := rand.Reader.Read(tempSeed)
if err != nil {
    panic(err)
}
tempWriteCap, _, tempFirstIndex, err := thinClient.NewKeypair(ctx, tempSeed)
err := thinClient.StartResendingCopyCommand(ctx, writeCap)

// Create final destination stream channel
destSeed := make([]byte, 32)
_, err := rand.Reader.Read(destSeed)
if err != nil {
    panic=(err)
}
destWriteCap, _, destFirstIndex, err := thinClient.NewKeypair(ctx, destSeed)

// Send Copy command to courier
reply, err := thinClient.StartResendingCopyCommand(ctx, tempWriteCap)
{{< /tab >}}

{{< tab header="Python" lang="python" >}}
# Send copy command - blocks until ACK or cancel
await thin_client.start_resending_copy_command(temp_write_cap)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// Send copy command - blocks until ACK or cancel
// Optional courier_identity_hash and courier_queue_id for specific routing
thin_client.start_resending_copy_command(&temp_write_cap, None, None).await?;
{{< /tab >}}

{{< /tabpane >}}


## Cancel Resending Copy Command

This method is meant to be called from a different thread in order to cancel a previous call to `Start Resending Copy Command`.
It's field is mandatory and is the write cap hash of the temporary copy stream channel.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
err := thinclient.CancelResendingCopyCommand(ctx, tempWriteCapHash)
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
from hashlib import blake2b
write_cap_hash = blake2b(temp_write_cap, digest_size=32).digest()
await thin_client.cancel_resending_copy_command(write_cap_hash)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
use blake2::{Blake2b, Digest};
let mut hasher = Blake2b::<U32>::new();
hasher.update(&temp_write_cap);
let write_cap_hash: [u8; 32] = hasher.finalize().into();
thin_client.cancel_resending_copy_command(&write_cap_hash).await?;
{{< /tab >}}
{{< /tabpane >}}

## Create Courier Envelopes FromPayload

**WARNING:** This method if used repeatedly will cause data to be store inefficiently in the
temporary copy stream channel due to the BACAP Box payload padding. Use `CreateCourierEnvelopesFromPayloads`
instead for larger data transfers. Note that unlike `Create Courier Envelopes From Payloads`,
this method does not cause the client daemon to keep state between calls.

This method is used to create courier envelopes from a payload of any size smaller than 10 megabytes.
The payload is automatically chunked and each chunk is wrapped in a CourierEnvelope. Each returned chunk
is a serialized CopyStreamElement ready to be written to a box.

## New Stream ID

Returns a new random stream ID. This is used to correlate multiple calls to `CreateCourierEnvelopesFromMultiPayload`
that belong to the same copy stream.

## Create Courier Envelopes From Multi Payload

**NOTE:** This method keeps state in the daemon between calls. Each reply includes the current buffer state (`buffer` and `is_first_chunk`) which the application can persist for crash recovery. Use `SetStreamBuffer` to restore state after a crash or restart.

This method is used to create courier envelopes from multiple payloads going to different destination channels.
This is more space-efficient than calling `CreateCourierEnvelopesFromPayload` multiple times because envelopes
from different destinations are packed together in the copy stream without wasting space. The maximum size of a
payload in a single call is 10 megabytes.

This method is meant to be called multiple times with the same stream ID and the very last call must set isLast to true.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
allChunks, err := thinClient.CreateCourierEnvelopesFromMultiPayload(
    ctx, streamID, destinations, true, // isLast
)
if err != nil {
    panic(err)
}

tempIndex := tempFirstIndex
for _, chunk := range allChunks {
    ciphertext, envDesc, envHash, err := thinClient.EncryptWrite(
        ctx, chunk, tempWriteCap, tempIndex,
    )
    if err != nil {
        panic(err)
    }

    _, err = thinClient.StartResendingEncryptedMessage(
        ctx, nil, tempWriteCap, nil, 0, envDesc, ciphertext, envHash,
    )
    if err != nil {
        panic(err)
    }

    tempIndex, err = thinClient.NextMessageBoxIndex(ctx, tempIndex)
    if err != nil {
        panic(err)
    }
}
{{< /tab >}}

{{< tab header="Python" lang="python" >}}
result = await thin_client.create_courier_envelopes_from_payloads(
    stream_id, destinations, is_last=True
)
# Persist result.buffer_state for crash recovery if needed

temp_index = temp_first_index
for chunk in result.envelopes:
    ciphertext, env_desc, env_hash = await thin_client.encrypt_write(
        chunk, temp_write_cap, temp_index
    )

    await thin_client.start_resending_encrypted_message(
        read_cap=None,
        write_cap=temp_write_cap,
        next_message_index=None,
        reply_index=0,
        envelope_descriptor=env_desc,
        message_ciphertext=ciphertext,
        envelope_hash=env_hash
    )

    temp_index = await thin_client.next_message_box_index(temp_index)
{{< /tab >}}

{{< tab header="Rust" lang="rust" >}}
let result = thin_client.create_courier_envelopes_from_multi_payload(
    &stream_id,
    destinations,
    true // is_last
).await.expect("Failed to create courier envelopes from multi payload");
// Persist result.buffer_state for crash recovery if needed

let mut temp_index = temp_first_index.clone();

for chunk in &result.envelopes {
    let (ciphertext, env_desc, env_hash) = thin_client
        .encrypt_write(chunk, &temp_write_cap, &temp_index).await
        .expect("Failed to encrypt chunk");

    let _ = thin_client.start_resending_encrypted_message(
        None,
        Some(&temp_write_cap),
        None,
        Some(0),
        &env_desc,
        &ciphertext,
        &env_hash
    ).await.expect("Failed to send chunk via ARQ");

    temp_index = thin_client.next_message_box_index(&temp_index).await
        .expect("Failed to get next index");
}
{{< /tab >}}
{{< /tabpane >}}


## Set Stream Buffer (Crash Recovery)

The `SetStreamBuffer` method allows applications to restore a copy stream's encoder state after a crash or restart. Only `CreateCourierEnvelopesFromMultiPayload` keeps state in the daemon between calls, and each reply includes the current buffer state that can be persisted and later restored using `SetStreamBuffer`.

**Crash Recovery Workflow:**
1. Call `create_courier_envelopes_from_multi_payload` with `is_last=false`
2. Persist the returned `buffer` and `is_first_chunk` to disk along with the `stream_id`
3. On crash/restart, call `set_stream_buffer` with the saved state
4. Continue streaming from where you left off

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// After creating envelopes, the daemon internally tracks buffer state
// Use SetStreamBuffer to restore after a crash:
err := thinClient.SetStreamBuffer(ctx, streamID, savedBuffer, savedIsFirstChunk)
if err != nil {
    panic(err)
}
// Now continue streaming from where we left off
{{< /tab >}}

{{< tab header="Python" lang="python" >}}
# Save state after each call to create_courier_envelopes_from_payloads
result = await thin_client.create_courier_envelopes_from_payloads(
    stream_id, destinations, is_last=False
)
# Persist buffer_state to disk
save_to_disk(stream_id, result.buffer_state.buffer, result.buffer_state.is_first_chunk)

# On restart, restore state:
buffer, is_first_chunk = load_from_disk(stream_id)
await thin_client.set_stream_buffer(stream_id, buffer, is_first_chunk)
# Continue streaming...
{{< /tab >}}

{{< tab header="Rust" lang="rust" >}}
// Save state after each call to create_courier_envelopes_from_multi_payload
let result = thin_client.create_courier_envelopes_from_multi_payload(
    &stream_id, destinations, false
).await?;
// Persist buffer_state to disk
save_to_disk(&stream_id, &result.buffer_state.buffer, result.buffer_state.is_first_chunk);

// On restart, restore state:
let (buffer, is_first_chunk) = load_from_disk(&stream_id)?;
thin_client.set_stream_buffer(&stream_id, buffer, is_first_chunk).await?;
// Continue streaming...
{{< /tab >}}
{{< /tabpane >}}

<HR>
<BR>

## Experimental Nested Copy API

The golang thin client has these additional experimental Pigeonhole API methods that are used to construct a "nested copy" command which is a kind of recursive copy that constructs a kind
of route among a set of couriers.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) GetAllCouriers() ([]CourierDescriptor, error)

func (t *ThinClient) GetDistinctCouriers(n int) ([]CourierDescriptor, error)

func (t *ThinClient) StartResendingCopyCommandWithCourier(
	ctx context.Context,
	writeCap *bacap.WriteCap,
	courierIdentityHash *[32]byte,
	courierQueueID []byte,
) error

func (t *ThinClient) SendNestedCopy(
	ctx context.Context,
	payload []byte,
	destWriteCap *bacap.WriteCap,
	destFirstIndex *bacap.MessageBoxIndex,
	courierPath []CourierDescriptor,
) error
{{< /tab >}}
{{< /tabpane >}}


### Courier Descriptor

A courier descriptor is a struct that contains the identity hash and queue ID of a courier. It is used to identify a specific courier for sending copy commands to.

```golang
// CourierDescriptor identifies a specific courier service for routing copy commands.
type CourierDescriptor struct {
	IdentityHash *[32]byte
	QueueID      []byte
}
```

### Get All Couriers

This method returns a list of all available courier services from the current PKI document. Use this to select specific couriers for nested copy commands.

### Get Distinct Couriers

This method returns N distinct random couriers. Returns an error if fewer than N couriers are available.

### Send Nested Copy

Send nested copy can be used to send a recursive copy command to a list of couriers. It keeps state and calls `StartResedingCopyCommandWithCourier` under the hood. 

### Events:
    - There is a reply to your read: QueryID, EnvelopeHash
      - The reply to your read was successful: Plaintext (message)
      - The reply to your read was unsuccessful (box not found)
    - "Your message has been sent": QueryID, EnvelopeHash
    - "Protocol violation, I'm going to disconnect this app"
    - The replicas your message was encrypted to are (not / no longer) in the PKI: QueryID, EnvelopeHash

### kpclientd queues
- global egress queue going to first mix layer (with decoys interleaved)
- per-app egress queue (unbounded), killed when app disconnects
- success queue: EnvelopeHash -> successful reply, entries are cleaned up after ... 5 minutes?

### we need to solve the "box not found" Negative ACK cache
- replicas need to tell the couriers when the boxes are filled
- so the kpclientd can keep resending the read and eventually get a successful reply
- we need to spec out the on-disk structures on replica+courier to support this

