---
title:
linkTitle: "Thin Client API Reference"
description: "Complete API reference for the Katzenpost thin client libraries (Go, Rust, Python)"
categories: [""]
tags: [""]
author: ["David Stainton"]
version: 0
draft: false
slug: "/thin_client_api_reference/"
url: "docs/thin_client_api_reference/"
aliases:
  - "/docs/python_thin_client.html"
---

# Thin Client API Reference

This is the complete API reference for the Katzenpost thin client. The
thin client is an interface to the kpclientd daemon, which handles all
cryptographic and network operations. The thin client communicates
with the daemon over a local socket using CBOR-encoded messages.

**This document is generated.** The canonical source is
`website/tools/thin-client-api-gen/`; edit binding docstrings (in the
source trees) or `groups.yaml` / `overlay/*.md` (in the generator) — do
not edit this file directly, as local changes will be overwritten by
the next generation pass.

There are three implementations: a Go reference (`katzenpost/client/thin`), a
Rust binding (`thin_client/src`), and a Python binding
(`thin_client/katzenpost_thinclient`).

The official API documentation for each binding:

| Language | Official API documentation |
| --- | --- |
| Go | [pkg.go.dev](https://pkg.go.dev/github.com/katzenpost/katzenpost/client/thin) |
| Rust | [docs.rs](https://docs.rs/katzenpost_thin_client/latest/katzenpost_thin_client/) |
| Python | [PyPI: katzenpost_thinclient](https://pypi.org/project/katzenpost_thinclient/) |

This reference describes the following pinned binding versions:

| Binding | Repository | Tag |
| --- | --- | --- |
| Go reference | [katzenpost/client/thin](https://github.com/katzenpost/katzenpost/tree/v0.0.76/client/thin) | [v0.0.76](https://github.com/katzenpost/katzenpost/releases/tag/v0.0.76) |
| Rust | [thin_client/src](https://github.com/katzenpost/thin_client/tree/0.0.15/src) | [0.0.15](https://github.com/katzenpost/thin_client/releases/tag/0.0.15) |
| Python | [thin_client/katzenpost_thinclient](https://github.com/katzenpost/thin_client/tree/0.0.15/katzenpost_thinclient) | [0.0.15](https://github.com/katzenpost/thin_client/releases/tag/0.0.15) |

For pinned versions of the full stack (including `kpclientd`, `katzenqt`, and
the server-side components), see [Build from source](/docs/build_from_source/).

For conceptual background on Pigeonhole, see [Understanding Pigeonhole](/docs/pigeonhole_explained/).
For task-oriented usage guides, see [Thin Client How-to Guide](/docs/thin_client_howto/).

---

## Configuration and Construction

The thin client is configured via a TOML file that specifies only how
to reach the local daemon. We usually name this configuration file
`thinclient.toml`.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
cfg, err := thin.LoadFile("thinclient.toml")
if err != nil {
    log.Fatal(err)
}

logging := &config.Logging{Level: "INFO"}
client := thin.NewThinClient(cfg, logging)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
let config = Config::new("thinclient.toml")?;
let client = ThinClient::new(config).await?;
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
config = Config("thinclient.toml")
client = ThinClient(config)
{{< /tab >}}
{{< /tabpane >}}

### The `thinclient.toml` file

`thinclient.toml` tells the thin client only where to reach the local
daemon. The complete file is simply:

```toml
[Dial]
  [Dial.Tcp]
    Address = "localhost:64331"
    Network = "tcp"
```

**`[Dial]`** selects the daemon transport. Set exactly one of the two
forms:

| Key | Type | Meaning |
|---|---|---|
| `[Dial.Unix]` `Address` | string | Filesystem path of the daemon's Unix socket. |
| `[Dial.Tcp]` `Address` | string | `host:port` of the daemon's TCP listener. |
| `[Dial.Tcp]` `Network` | string | Optional: `"tcp"`, `"tcp4"`, or `"tcp6"` (default `"tcp"`). |

### Concurrency

The Go `ThinClient` is safe for concurrent use by multiple goroutines:
its connection state, current PKI document, and in-flight request
tracking are guarded internally, so the cancel-from-another-goroutine
patterns shown in the [how-to guide](/docs/thin_client_howto/) are
sound. The Rust and Python bindings are `async`: an instance is driven
from its runtime (a Tokio task or an asyncio event loop) and follows
that runtime's ordinary conventions rather than offering an
independent thread-safety guarantee.

## Connection Management

### Dial / new / start

Dial establishes a connection to the client daemon and initializes the client.

This method performs the complete connection handshake with the client daemon:
 1. Establishes network connection (TCP or Unix socket)
 2. Receives initial connection status from daemon
 3. Receives initial PKI document
 4. Starts background workers for event handling

The client supports both online and offline modes. In offline mode (when the
daemon is not connected to the mixnet), channel preparation operations will
work but actual message transmission will fail.

After successful connection, the client will automatically handle:
  - PKI document updates
  - Connection status changes
  - Event distribution to application code

The Rust binding folds the connect step into its constructor:
`ThinClient::new` returns an already-connected handle. Go and
Python construct the client first and connect afterwards via
`Dial()` / `start()`, allowing the application to set up event
sinks (in Go) or callbacks (in Python) before any traffic flows.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) Dial() error
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn new(config: Config) -> Result<Arc<Self>, Box<dyn std::error::Error>>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def start(self, loop: asyncio.AbstractEventLoop) -> None:
{{< /tab >}}
{{< /tabpane >}}

### Close / stop

Close gracefully shuts down the thin client and closes the daemon connection.

This method performs a clean shutdown by:
 1. Sending a close notification to the daemon
 2. Closing the network connection
 3. Stopping all background workers

After calling Close(), the ThinClient instance should not be used further.
Any ongoing operations will be interrupted and may return errors.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) Close() error
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn stop(&self)
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
def stop(self) -> None:
{{< /tab >}}
{{< /tabpane >}}

### IsConnected / is_connected

IsConnected returns true if the client daemon is connected to the mixnet.

This indicates whether the daemon has an active connection to the mixnet
infrastructure. When false, the client is in "offline mode" where channel
operations (prepare operations) will work but actual message transmission
will fail.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) IsConnected() bool
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub fn is_connected(&self) -> bool
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
def is_connected(self) -> bool:
{{< /tab >}}
{{< /tabpane >}}

### Disconnect / disconnect

Disconnect closes the connection without sending ThinClose.
The daemon preserves all state for this client's app ID, allowing
the client to reconnect and resume with the same session token.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) Disconnect() error
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn disconnect(&self)
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
def disconnect(self) -> None:
{{< /tab >}}
{{< /tabpane >}}

## Events

The thin client emits events for connection status changes, PKI
document updates, and message replies. Go uses an event channel; Rust
uses a broadcast receiver; Python uses async callbacks supplied to the
`Config` constructor.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
// Get a channel that receives all events
eventCh := client.EventSink()
defer client.StopEventSink(eventCh)

for ev := range eventCh {
    switch ev.(type) {
    case *thin.ConnectionStatusEvent:
        // ...
    case *thin.NewDocumentEvent:
        // ...
    case *thin.MessageReplyEvent:
        // ...
    }
}
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// Get a receiver that yields all events as CBOR BTreeMaps
let mut event_rx = client.event_sink();

tokio::spawn(async move {
    while let Some(event) = event_rx.recv().await {
        // Inspect event["type"] and dispatch
    }
});
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
# Pass async callback functions to the Config constructor.
# Each callback receives a dict with event-specific keys.
# All callbacks are optional — omitted events are ignored.

async def on_connection_status(event):
    print(f"Connected: {event['is_connected']}")

async def on_message_reply(event):
    print(f"Reply for SURBID {event['surbid']!r}: {event['payload']!r}")

config = Config(
    "thinclient.toml",
    on_connection_status=on_connection_status,
    on_message_reply=on_message_reply,
)
client = ThinClient(config)
{{< /tab >}}
{{< /tabpane >}}

### Event types

- **ConnectionStatusEvent** — emitted when the daemon's connection
  to the mixnet changes. Fields (Go): `IsConnected bool`, `Err error`,
  `InstanceToken [16]byte`. `InstanceToken` uniquely identifies the
  daemon process and lets clients notice daemon restarts.

- **NewDocumentEvent** — emitted when a new PKI consensus document
  is received from the directory authorities. The Go binding exposes
  the parsed document as `Document *cpki.Document`. (The lower-level
  `NewPKIDocumentEvent` carrying a raw CBOR `Payload []byte` is used
  internally between daemon and thin client; applications should
  consume `NewDocumentEvent`.)

- **MessageSentEvent** — emitted when a `SendMessage` request has
  been transmitted by the daemon. Fields (Go):
  `MessageID *[MessageIDLength]byte`, `SURBID *[SURBIDLength]byte`,
  `SentAt time.Time`, `ReplyETA time.Duration`, `Err string`.

- **MessageReplyEvent** — emitted when a reply to a `SendMessage`
  call is received. Fields (Go):
  `MessageID *[MessageIDLength]byte`, `SURBID *[SURBIDLength]byte`,
  `Payload []byte`, `ReplyIndex *uint8`, `ErrorCode uint8`.
  `ReplyIndex` identifies **which of the box's two replicas answered**:
  each box is sharded across K=2 replicas, and the value (0 or 1) is
  the position within that pair of the replica whose response was
  used. It is chiefly of interest for Pigeonhole channel reads and may
  be `nil` when not applicable. The same value is accepted as the
  `reply_index` parameter of `StartResendingEncryptedMessage`, where
  it likewise selects the replica of the pair to address.

- **ShutdownEvent**: emitted when the daemon signals that it is
  shutting down. It carries no fields. It precedes the loss of the
  local socket and is what causes the following
  **DaemonDisconnectedEvent** to report `IsGraceful = true`. Treat it
  as advance notice of the disconnect; no action is required, since
  the thin client reconnects and replays in-flight requests on its
  own.

- **DaemonDisconnectedEvent** — emitted by the thin client (not the
  daemon) when the local socket connection to the daemon is lost.
  Fields (Go): `IsGraceful bool`, `Err error`. `IsGraceful` is true
  precisely when a `ShutdownEvent` preceded the disconnect.

### EventSink / event_sink

EventSink returns a buffered channel that receives all events from the thin client.

This method creates a new event channel that will receive copies of all events
generated by the thin client, including:
  - Connection status changes
  - PKI document updates
  - Message sent confirmations
  - Message replies
  - Channel operation results
  - Error notifications

The returned channel is buffered with capacity 1. Events are never
silently dropped: the fan-out worker blocks until the subscriber
accepts each event, matching the "no loss" contract the Rust and
Python thin clients uphold. Consequently an application that
stops consuming from its sink will stall the entire fan-out
(including events destined for other subscribers); applications
must drain promptly or call StopEventSink() to release their
subscription.

Important: Always call StopEventSink() when done with the channel to prevent
resource leaks and ensure proper cleanup.

Note: The event sink channel is NOT closed when the client shuts down.
Consumers should also select on HaltCh() to detect shutdown, or they
can check for a ShutdownEvent in the event stream.

The Rust binding returns an `mpsc::Receiver` carrying the same
event stream. The Python binding has no equivalent method:
Python applications instead register async callbacks on the
`Config` constructor and receive events through those.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) EventSink() chan Event
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub fn event_sink(&self) -> EventSinkReceiver
{{< /tab >}}
{{< /tabpane >}}

### StopEventSink (Go only)

StopEventSink stops sending events to the specified channel and cleans up resources.

This method removes the channel from the event distribution system and should
be called when the application is done processing events from a channel
returned by EventSink(). Failure to call this method may result in resource
leaks and continued event processing overhead.

Rust subscribers are released by dropping the
`mpsc::Receiver`, so the binding exposes no explicit teardown
method. Python's callback model owns no per-subscriber
resources either, and so likewise needs no equivalent.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) StopEventSink(ch chan Event)
{{< /tab >}}
{{< /tabpane >}}

## PKI and Service Discovery

### PKIDocument / pki_document

PKIDocument returns the thin client's current PKI document.

The PKI document contains the current network topology, service information,
and cryptographic parameters for the current epoch. This document is
automatically updated when the client daemon receives new PKI information.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) PKIDocument() *cpki.Document
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn pki_document(&self) -> Result<BTreeMap<Value, Value>, ThinClientError>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
def pki_document(self) -> 'Dict[str,Any] | None':
{{< /tab >}}
{{< /tabpane >}}

### GetPKIDocumentRaw / get_pki_document_raw

GetPKIDocumentRaw returns the cert.Certificate-wrapped signed PKI
document for the requested epoch, with every directory authority
signature intact. Pass epoch == 0 to request the document the daemon
believes is current.

The thin client receives the stripped PKI document by default (as
pushed in NewPKIDocumentEvent); use this method when the caller
needs to verify the directory authority signatures itself. The
payload can be deserialized and verified with core/pki.FromPayload.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) GetPKIDocumentRaw(epoch uint64) ([]byte, uint64, error)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn get_pki_document_raw(
    &self,
    epoch: u64,
) -> Result<(Vec<u8>, u64), ThinClientError>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def get_pki_document_raw(self, epoch: int = 0) -> 'Tuple[bytes,int]':
{{< /tab >}}
{{< /tabpane >}}

### GetService / get_service

GetService returns a randomly selected service matching the specified capability.

This method is a convenience wrapper around GetServices() that randomly
selects one service from all available services with the given capability.
This provides automatic load balancing across available service instances.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) GetService(serviceName string) (*common.ServiceDescriptor, error)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn get_service(
    &self,
    service_name: &str,
) -> Result<ServiceDescriptor, ThinClientError>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
def get_service(self, service_name: str) -> ServiceDescriptor:
{{< /tab >}}
{{< /tabpane >}}

### GetServices / get_services

GetServices returns all services matching the specified capability name.

This method searches the current PKI document for services that provide
the specified capability. Services in Katzenpost are identified by their
capability names (e.g., "echo", "courier", "keyserver").

The Rust binding exposes the same lookup as the free function
`find_services` in `helpers.rs`, rather than as a method on
`ThinClient`.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) GetServices(capability string) ([]*common.ServiceDescriptor, error)
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
def get_services(self, capability: str) -> 'List[ServiceDescriptor]':
{{< /tab >}}
{{< /tabpane >}}

## Direct Messaging

### SendMessage / send_message

SendMessage sends a message with reply capability using the legacy API.

This method sends a message with a Single Use Reply Block (SURB) that allows
the destination to send a reply. The method is asynchronous - it only blocks
until the daemon receives the send request, not until the message is actually
transmitted or a reply is received.

To receive replies, applications must monitor events from EventSink() and
look for MessageReplyEvent instances with matching SURB IDs.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) SendMessage(surbID *[sConstants.SURBIDLength]byte, payload []byte, destNode *[32]byte, destQueue []byte) error
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn send_message(
    &self,
    surb_id: Vec<u8>,
    payload: &[u8],
    dest_node: Vec<u8>,
    dest_queue: Vec<u8>,
) -> Result<(), ThinClientError>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def send_message(self, surb_id: bytes, payload: bytes | str, dest_node: bytes, dest_queue: bytes) -> None:
{{< /tab >}}
{{< /tabpane >}}

### SendMessageWithoutReply / send_message_without_reply

SendMessageWithoutReply sends a fire-and-forget message using the legacy API.

This method sends a message without any reply capability. The message is
encapsulated in a Sphinx packet and sent through the mixnet, but no response
can be received. This is suitable for notifications or one-way communication.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) SendMessageWithoutReply(payload []byte, destNode *[32]byte, destQueue []byte) error
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn send_message_without_reply(
    &self,
    payload: &[u8],
    dest_node: Vec<u8>,
    dest_queue: Vec<u8>,
) -> Result<(), ThinClientError>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def send_message_without_reply(self, payload: bytes | str, dest_node: bytes, dest_queue: bytes) -> None:
{{< /tab >}}
{{< /tabpane >}}

### BlockingSendMessage / blocking_send_message

BlockingSendMessage sends a message and blocks until a reply is received.

This method provides a synchronous request-response pattern by automatically
generating a SURB ID, sending the message, and waiting for the reply. It
blocks until either a reply is received or the context times out.

This is convenient for simple request-response interactions but lacks the
advanced features of the Pigeonhole Channel API such as message ordering,
channel persistence, and offline operation support.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) BlockingSendMessage(ctx context.Context, payload []byte, destNode *[32]byte, destQueue []byte) ([]byte, error)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn blocking_send_message(
    &self,
    payload: &[u8],
    dest_node: Vec<u8>,
    dest_queue: Vec<u8>,
    timeout: std::time::Duration,
) -> Result<Vec<u8>, ThinClientError>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def blocking_send_message(self, payload: bytes | str, dest_node: bytes, dest_queue: bytes, timeout_seconds: float = 30.0) -> bytes:
{{< /tab >}}
{{< /tabpane >}}

## Pigeonhole: Key Management

### NewKeypair / new_keypair

NewKeypair creates a new keypair for use with the Pigeonhole protocol.

This method generates a WriteCap and ReadCap from the provided seed using
the BACAP (Blinding-and-Capability) protocol. The WriteCap should be stored
securely for writing messages, while the ReadCap can be shared with others
to allow them to read messages.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) NewKeypair(seed []byte) (writeCap *bacap.WriteCap, readCap *bacap.ReadCap, firstMessageIndex *bacap.MessageBoxIndex, err error)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn new_keypair(
    &self,
    seed: &[u8; 32],
) -> Result<KeypairResult, ThinClientError>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def new_keypair(self, seed: bytes) -> KeypairResult:
{{< /tab >}}
{{< /tabpane >}}

## Pigeonhole: Index Management

### NextMessageBoxIndex / next_message_box_index

NextMessageBoxIndex increments a MessageBoxIndex using the BACAP NextIndex method.

This method is used when sending multiple messages to different mailboxes using
the same WriteCap or ReadCap. It properly advances the cryptographic state by:
  - Incrementing the Idx64 counter
  - Deriving new encryption and blinding keys using HKDF
  - Updating the HKDF state for the next iteration

The client daemon handles the cryptographic operations using our BACAP library
documented here: https://pkg.go.dev/github.com/katzenpost/hpqc/bacap

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) NextMessageBoxIndex(messageBoxIndex *bacap.MessageBoxIndex) (nextMessageBoxIndex *bacap.MessageBoxIndex, err error)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn next_message_box_index(
    &self,
    message_box_index: &[u8],
) -> Result<Vec<u8>, ThinClientError>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def next_message_box_index(self, message_box_index: bytes) -> bytes:
{{< /tab >}}
{{< /tabpane >}}

## Pigeonhole: Encryption

### EncryptRead / encrypt_read

EncryptRead encrypts a read operation for a given read capability.

This method prepares an encrypted read request that can be sent to the
courier service to retrieve a message from a pigeonhole box. The returned
ciphertext should be sent via StartResendingEncryptedMessage.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) EncryptRead(readCap *bacap.ReadCap, messageBoxIndex *bacap.MessageBoxIndex) (messageCiphertext []byte, envelopeDescriptor []byte, envelopeHash *[32]byte, nextMessageBoxIndex *bacap.MessageBoxIndex, err error)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn encrypt_read(
    &self,
    read_cap: &[u8],
    message_box_index: &[u8],
) -> Result<EncryptReadResult, ThinClientError>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def encrypt_read(self, read_cap: bytes, message_box_index: bytes) -> EncryptReadResult:
{{< /tab >}}
{{< /tabpane >}}

### EncryptWrite / encrypt_write

EncryptWrite encrypts a write operation for a given write capability.

This method prepares an encrypted write request that can be sent to the
courier service to store a message in a pigeonhole box. The returned
ciphertext should be sent via StartResendingEncryptedMessage.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) EncryptWrite(plaintext []byte, writeCap *bacap.WriteCap, messageBoxIndex *bacap.MessageBoxIndex) (messageCiphertext []byte, envelopeDescriptor []byte, envelopeHash *[32]byte, nextMessageBoxIndex *bacap.MessageBoxIndex, err error)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn encrypt_write(
    &self,
    plaintext: &[u8],
    write_cap: &[u8],
    message_box_index: &[u8],
) -> Result<EncryptWriteResult, ThinClientError>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def encrypt_write(self, plaintext: bytes, write_cap: bytes, message_box_index: bytes) -> EncryptWriteResult:
{{< /tab >}}
{{< /tabpane >}}

## Pigeonhole: ARQ Transport

### StartResendingEncryptedMessage / start_resending_encrypted_message

StartResendingEncryptedMessage sends an encrypted message via ARQ and blocks until completion.

This method BLOCKS until a reply is received. CancelResendingEncryptedMessage is only
useful when called from another goroutine to interrupt this blocking call.

The message will be resent periodically until either:
  - A reply is received from the courier (this method returns)
  - The message is cancelled via CancelResendingEncryptedMessage (from another goroutine)
  - The client is shut down

This is used for both read and write operations in the new Pigeonhole API.

The daemon implements a finite state machine (FSM) for handling the stop-and-wait ARQ protocol:
  - For default write operations (writeCap != nil, readCap == nil,
    noIdempotentBoxAlreadyExists == false):
    The method waits for an ACK from the courier and returns immediately.
    The ACK confirms the courier received the envelope and will dispatch it
    to both shard replicas. This requires only a single round-trip through
    the mixnet.
  - For BoxAlreadyExists-aware writes (noIdempotentBoxAlreadyExists == true):
    The method waits for an ACK, then sends a second SURB to retrieve the
    replica's error code. This requires two round-trips through the mixnet.
  - For read operations (readCap != nil, writeCap == nil):
    The method waits for an ACK from the courier, then the daemon automatically
    sends a new SURB to request the payload, and this method waits for the payload.
    The daemon performs all decryption (MKEM envelope + BACAP payload) and returns
    the fully decrypted plaintext.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) StartResendingEncryptedMessage(readCap *bacap.ReadCap, writeCap *bacap.WriteCap, messageBoxIndex []byte, replyIndex *uint8, envelopeDescriptor []byte, messageCiphertext []byte, envelopeHash *[32]byte) (*StartResendingResult, error)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn start_resending_encrypted_message(
    &self,
    read_cap: Option<&[u8]>,
    write_cap: Option<&[u8]>,
    message_box_index: Option<&[u8]>,
    reply_index: Option<u8>,
    envelope_descriptor: &[u8],
    message_ciphertext: &[u8],
    envelope_hash: &[u8; 32],
) -> Result<StartResendingResult, ThinClientError>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def start_resending_encrypted_message(self, read_cap: 'bytes|None', write_cap: 'bytes|None', message_box_index: 'bytes|None', reply_index: 'int|None', envelope_descriptor: bytes, message_ciphertext: bytes, envelope_hash: bytes, no_retry_on_box_id_not_found: bool = False, no_idempotent_box_already_exists: bool = False) -> StartResendingResult:
{{< /tab >}}
{{< /tabpane >}}

### StartResendingEncryptedMessageReturnBoxExists

StartResendingEncryptedMessageReturnBoxExists behaves exactly like
StartResendingEncryptedMessage save that it returns
ErrBoxAlreadyExists when the replica reports that the destination
box has already been written, rather than swallowing the condition
as idempotent success. Use it when one needs to distinguish a
fresh write from a repeat: for instance, when implementing
optimistic concurrency on top of the channel, or when establishing
whether a particular call actually caused a state change at the
replica.

Note that this variant costs an additional mixnet round trip: the
BoxAlreadyExists code is carried by the replica's reply rather than
the courier's ACK, so the daemon must dispatch a second SURB before
it can return the answer.

As with StartResendingEncryptedMessage, an in-flight call may be
cancelled from another goroutine via CancelResendingEncryptedMessage.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) StartResendingEncryptedMessageReturnBoxExists(readCap *bacap.ReadCap, writeCap *bacap.WriteCap, messageBoxIndex []byte, replyIndex *uint8, envelopeDescriptor []byte, messageCiphertext []byte, envelopeHash *[32]byte) (*StartResendingResult, error)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn start_resending_encrypted_message_return_box_exists(
    &self,
    read_cap: Option<&[u8]>,
    write_cap: Option<&[u8]>,
    message_box_index: Option<&[u8]>,
    reply_index: Option<u8>,
    envelope_descriptor: &[u8],
    message_ciphertext: &[u8],
    envelope_hash: &[u8; 32],
) -> Result<StartResendingResult, ThinClientError>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def start_resending_encrypted_message_return_box_exists(self, read_cap: 'bytes|None', write_cap: 'bytes|None', message_box_index: 'bytes|None', reply_index: 'int|None', envelope_descriptor: bytes, message_ciphertext: bytes, envelope_hash: bytes) -> StartResendingResult:
{{< /tab >}}
{{< /tabpane >}}

### StartResendingEncryptedMessageNoRetry

StartResendingEncryptedMessageNoRetry behaves exactly like
StartResendingEncryptedMessage save that it disables the daemon's
automatic retry of ErrBoxIDNotFound. The caller learns at once that
the box is absent rather than waiting for replication to settle.

Use it when polling a box that may not yet have been written, for
instance when a reader peeks ahead at a peer's next message before
that peer has produced it; the regular variant would block until
the box appeared, which can be many round trips.

As with StartResendingEncryptedMessage, an in-flight call may be
cancelled from another goroutine via CancelResendingEncryptedMessage.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) StartResendingEncryptedMessageNoRetry(readCap *bacap.ReadCap, writeCap *bacap.WriteCap, messageBoxIndex []byte, replyIndex *uint8, envelopeDescriptor []byte, messageCiphertext []byte, envelopeHash *[32]byte) (*StartResendingResult, error)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn start_resending_encrypted_message_no_retry(
    &self,
    read_cap: Option<&[u8]>,
    write_cap: Option<&[u8]>,
    message_box_index: Option<&[u8]>,
    reply_index: Option<u8>,
    envelope_descriptor: &[u8],
    message_ciphertext: &[u8],
    envelope_hash: &[u8; 32],
) -> Result<StartResendingResult, ThinClientError>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def start_resending_encrypted_message_no_retry(self, read_cap: 'bytes|None', write_cap: 'bytes|None', message_box_index: 'bytes|None', reply_index: 'int|None', envelope_descriptor: bytes, message_ciphertext: bytes, envelope_hash: bytes) -> StartResendingResult:
{{< /tab >}}
{{< /tabpane >}}

### CancelResendingEncryptedMessage / cancel_resending_encrypted_message

CancelResendingEncryptedMessage cancels ARQ resending for an encrypted message.

This method stops the automatic repeat request (ARQ) for a previously started
encrypted message transmission. This is useful when:
  - A reply has been received through another channel
  - The operation should be aborted
  - The message is no longer needed

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) CancelResendingEncryptedMessage(envelopeHash *[32]byte) error
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn cancel_resending_encrypted_message(
    &self,
    envelope_hash: &[u8; 32],
) -> Result<(), ThinClientError>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def cancel_resending_encrypted_message(self, envelope_hash: bytes) -> None:
{{< /tab >}}
{{< /tabpane >}}

## Pigeonhole: Tombstones

### TombstoneRange / tombstone_range

TombstoneRange prepares the encrypted envelopes needed to
tombstone a consecutive range of pigeonhole boxes beginning at the
supplied MessageBoxIndex. A tombstone is a signed empty payload
that the replica recognises as a deletion marker; the daemon
constructs one by signing rather than encrypting whenever
EncryptWrite is invoked with an empty plaintext.

This method does not itself touch the network: it returns the
envelopes for the caller to dispatch one by one, typically via
StartResendingEncryptedMessage. To tombstone a single box, pass
maxCount=1.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (c *ThinClient) TombstoneRange(
	writeCap *bacap.WriteCap,
	start *bacap.MessageBoxIndex,
	maxCount uint32,
) (result *TombstoneRangeResult, err error)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn tombstone_range(
    &self,
    write_cap: &[u8],
    start: &[u8],
    max_count: u32,
) -> TombstoneRangeResult
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def tombstone_range(self, write_cap: bytes, start: bytes, max_count: int) -> TombstoneRangeResult:
{{< /tab >}}
{{< /tabpane >}}

## Pigeonhole: Copy Stream Construction

### CreateCourierEnvelopesFromPayload

CreateCourierEnvelopesFromPayload packs a payload of arbitrary
size (up to 10 MB) into properly sized CopyStreamElement chunks
for one destination channel. Each chunk is a serialised
CopyStreamElement, ready to be written to a box via EncryptWrite
followed by StartResendingEncryptedMessage; the caller marks the
boundaries of the stream with the isStart and isLast flags.

This method is stateless: no daemon state is kept between calls,
each invocation runs a fresh encoder and flushes before returning.
The 10 MB cap guards against accidental memory exhaustion.

Once the chunks have been written to a temporary copy stream, a
copy command (StartResendingCopyCommand) is despatched to a
courier with the WriteCap for that temporary stream; the courier
reads the chunks back and dispatches each envelope to its
destination box.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) CreateCourierEnvelopesFromPayload(payload []byte, destWriteCap *bacap.WriteCap, destStartIndex *bacap.MessageBoxIndex, isStart bool, isLast bool) (envelopes [][]byte, nextDestIndex *bacap.MessageBoxIndex, err error)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn create_courier_envelopes_from_payload(
    &self,
    payload: &[u8],
    dest_write_cap: &[u8],
    dest_start_index: &[u8],
    is_start: bool,
    is_last: bool,
) -> Result<CreateEnvelopesResult, ThinClientError>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def create_courier_envelopes_from_payload(self, payload: bytes, dest_write_cap: bytes, dest_start_index: bytes, is_start: bool, is_last: bool) -> 'CreateEnvelopesResult':
{{< /tab >}}
{{< /tabpane >}}

### CreateCourierEnvelopesFromMultiPayload

CreateCourierEnvelopesFromMultiPayload packs payloads bound for
several destination channels into a single stream of
CopyStreamElement chunks. This is more space-efficient than
calling CreateCourierEnvelopesFromPayload once per destination,
because the shared encoder runs all envelopes together rather than
padding the final box of each destination independently.

This method is stateless: the buffer argument carries any residual
encoder state across calls in place of daemon-side bookkeeping.
Pass nil for buffer on the first call and the Buffer returned by
the previous call thereafter; set isLast on the final call so that
the encoder flushes its tail.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) CreateCourierEnvelopesFromMultiPayload(destinations []DestinationPayload, isStart bool, isLast bool, buffer []byte) (*CreateEnvelopesResult, error)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn create_courier_envelopes_from_multi_payload(
    &self,
    destinations: Vec<(&[u8], &[u8], &[u8])>,
    is_start: bool,
    is_last: bool,
    buffer: Option<Vec<u8>>,
) -> Result<CreateEnvelopesResult, ThinClientError>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def create_courier_envelopes_from_multi_payload(self, destinations: 'List[Dict[str, Any]]', is_start: bool, is_last: bool, buffer: 'bytes | None' = None) -> 'CreateEnvelopesResult':
{{< /tab >}}
{{< /tabpane >}}

### CreateCourierEnvelopesFromTombstoneRange

CreateCourierEnvelopesFromTombstoneRange creates tombstone CourierEnvelopes for a range
of destination indices, encoded as copy stream elements ready to be written to a
temporary copy stream channel.

This combines the tombstone creation logic (SignBox with empty payload) with the
courier envelope wrapping and copy stream encoding of CreateCourierEnvelopesFromPayload.

The buffer parameter enables stateless continuation across multiple calls without
wasting space in the last box. Pass nil on the first call, then pass the returned
nextBuffer to the next call.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) CreateCourierEnvelopesFromTombstoneRange(
	destWriteCap *bacap.WriteCap,
	destStartIndex *bacap.MessageBoxIndex,
	maxCount uint32,
	isStart bool,
	isLast bool,
	buffer []byte,
) (envelopes [][]byte, nextBuffer []byte, nextDestIndex *bacap.MessageBoxIndex, err error)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn create_courier_envelopes_from_tombstone_range(
    &self,
    dest_write_cap: &[u8],
    dest_start_index: &[u8],
    max_count: u32,
    is_start: bool,
    is_last: bool,
    buffer: Option<Vec<u8>>,
) -> Result<CreateEnvelopesResult, ThinClientError>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def create_courier_envelopes_from_tombstone_range(self, dest_write_cap: bytes, dest_start_index: bytes, max_count: int, is_start: bool, is_last: bool, buffer: 'bytes | None' = None) -> 'CreateEnvelopesResult':
{{< /tab >}}
{{< /tabpane >}}

## Pigeonhole: Copy Command Transport

### StartResendingCopyCommand / start_resending_copy_command

StartResendingCopyCommand sends a copy command via ARQ and blocks until completion.

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

The Rust and Python bindings accept optional `courier_identity_hash`
and `courier_queue_id` arguments to pin the command to a particular
courier; the Go binding exposes that same behaviour through a
distinct method, `StartResendingCopyCommandWithCourier`.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) StartResendingCopyCommand(writeCap *bacap.WriteCap) error
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn start_resending_copy_command(
    &self,
    write_cap: &[u8],
    courier_identity_hash: Option<&[u8]>,
    courier_queue_id: Option<&[u8]>,
) -> Result<(), ThinClientError>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def start_resending_copy_command(self, write_cap: bytes, courier_identity_hash: 'bytes|None' = None, courier_queue_id: 'bytes|None' = None) -> None:
{{< /tab >}}
{{< /tabpane >}}

### StartResendingCopyCommandWithCourier (Go only)

StartResendingCopyCommandWithCourier behaves exactly like
StartResendingCopyCommand save that it dispatches the copy command
to a courier the caller has chosen, rather than to one selected at
random from the current PKI document. The courier is identified by
the (identity-hash, queue-id) pair returned by GetAllCouriers or
GetDistinctCouriers.

This is the building block for nested copy commands, in which the
outer command is sent to one courier and the inner commands carried
inside it reference a different courier. Staggering the two layers
across distinct couriers reduces the chance that any single
compromised courier observes both halves of the copy transaction
and can therefore link them.

In Rust and Python the same behaviour is reached not through a
separate method but by supplying the optional
`courier_identity_hash` and `courier_queue_id` arguments to
`start_resending_copy_command`.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) StartResendingCopyCommandWithCourier(
	writeCap *bacap.WriteCap,
	courierIdentityHash *[32]byte,
	courierQueueID []byte,
) error
{{< /tab >}}
{{< /tabpane >}}

### CancelResendingCopyCommand / cancel_resending_copy_command

CancelResendingCopyCommand cancels ARQ resending for a copy command.

This method stops the automatic repeat request (ARQ) for a previously started
copy command. This is useful when:
  - A reply has been received through another channel
  - The operation should be aborted
  - The copy command is no longer needed

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) CancelResendingCopyCommand(writeCapHash *[32]byte) error
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn cancel_resending_copy_command(
    &self,
    write_cap_hash: &[u8; 32],
) -> Result<(), ThinClientError>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def cancel_resending_copy_command(self, write_cap_hash: bytes) -> None:
{{< /tab >}}
{{< /tabpane >}}

## Pigeonhole: Courier Discovery

### GetAllCouriers / get_all_couriers

GetAllCouriers returns every courier service advertised in the
current PKI document, each described by an (identity-hash,
queue-id) pair. The list reflects only the couriers that the
current consensus regards as serving.

The principal caller is the nested-copy-command machinery, which
needs to choose particular couriers rather than accept the random
draw made on the caller's behalf by StartResendingCopyCommand; for
simple cases where any courier will do, the default routing path
is usually preferable.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) GetAllCouriers() (couriers []CourierDescriptor, err error)
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
def get_all_couriers(self) -> 'List[Tuple[bytes, bytes]]':
{{< /tab >}}
{{< /tabpane >}}

### GetDistinctCouriers / get_distinct_couriers

GetDistinctCouriers draws n couriers uniformly at random from the
list returned by GetAllCouriers, without replacement, so that no
two entries in the returned slice refer to the same courier. This
is the usual building block for a nested copy command, every layer
of which must be carried by a different courier.

Returns an error if the current PKI document advertises fewer than
n couriers.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) GetDistinctCouriers(n int) (couriers []CourierDescriptor, err error)
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
def get_distinct_couriers(self, n: int) -> 'List[Tuple[bytes, bytes]]':
{{< /tab >}}
{{< /tabpane >}}

### get_courier_destination (Rust only)

Returns one courier destination, drawn uniformly at random from
the couriers advertised in the current PKI document, as the
`(identity_hash, queue_id)` pair the rest of the API expects. This
spares the caller from handling a list when one courier will do.

The principal use is the routine "pick a courier, send a copy
command to it" pattern; for the nested-copy-command case where two
distinct couriers are required, draw them with a single call to
the underlying service helpers in `helpers.rs` rather than calling
this method twice and risking the same draw.

Go and Python callers reach the same result by calling
`GetDistinctCouriers(1)` / `get_distinct_couriers(1)` and taking
the first element of the returned slice.

{{< tabpane >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn get_courier_destination(
    &self,
) -> Result<(Vec<u8>, Vec<u8>), ThinClientError>
{{< /tab >}}
{{< /tabpane >}}

### pigeonhole_geometry (Rust only)

Returns the pigeonhole geometry the daemon supplied during the
connection handshake. This geometry defines the payload sizes and
envelope formats for the pigeonhole protocol.

Panics if called before the daemon's first ConnectionStatusEvent
has been processed, or if the daemon did not supply the geometry
(an incompatible daemon).

Go callers retrieve the same value through
`GetConfig().PigeonholeGeometry`. The Python binding stores the
geometry internally but does not at present expose a public
accessor.

{{< tabpane >}}
{{< tab header="Rust" lang="rust" >}}
pub fn pigeonhole_geometry(&self) -> PigeonholeGeometry
{{< /tab >}}
{{< /tabpane >}}

## Utility

### NewMessageID / new_message_id

NewMessageID generates a new cryptographically random message identifier.

Message IDs are used to correlate requests with responses in both legacy
and channel APIs. Each message should have a unique ID to prevent
confusion and enable proper event correlation.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) NewMessageID() *[MessageIDLength]byte
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub fn new_message_id() -> Vec<u8>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
def new_message_id() -> bytes:
{{< /tab >}}
{{< /tabpane >}}

### NewSURBID / new_surb_id

NewSURBID generates a new Single Use Reply Block identifier.

SURB IDs are used in the legacy API to correlate reply messages with
their original requests. Each SURB should have a unique ID.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) NewSURBID() *[sConstants.SURBIDLength]byte
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub fn new_surb_id() -> Vec<u8>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
def new_surb_id(self) -> bytes:
{{< /tab >}}
{{< /tabpane >}}

### NewQueryID / new_query_id

NewQueryID generates a new cryptographically random query identifier.

Query IDs are used in the channel API to correlate channel operation
requests with their responses. Each query should have a unique ID.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) NewQueryID() *[QueryIDLength]byte
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub fn new_query_id() -> Vec<u8>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
def new_query_id(self) -> bytes:
{{< /tab >}}
{{< /tabpane >}}

## Data Types

The Pigeonhole methods return structured results whose fields are
enumerated below. These are the **Go reference structs** from
`katzenpost/client/thin`; they are authoritative. The Rust and Python
bindings return the equivalent data through their own result types,
with the same fields rendered in `snake_case` (for example `WriteCap`
becomes `write_cap`, `NextMessageBoxIndex` becomes
`next_message_box_index`).

Two fields recur throughout and are protocol plumbing rather than
application data:

- `QueryID` correlates a reply with the request that produced it; the
  bindings manage it for you.
- `ErrorCode` is zero on success and otherwise names the failure. The
  bindings translate a non-zero code into the language-native error
  documented under [Replica and Courier
  Errors](#replica-and-courier-errors); application code inspects the
  raised error or returned sentinel rather than this byte directly.

### NewKeypair result (Rust/Python: KeypairResult)

NewKeypairReply is the reply to a NewKeypair request.

| Field | Type | Description |
|---|---|---|
| `QueryID` | `*[QueryIDLength]byte` | QueryID is used for correlating this reply with the NewKeypair request |
| `WriteCap` | `*bacap.WriteCap` | WriteCap is the write capability that should be stored for channel |
| `ReadCap` | `*bacap.ReadCap` | ReadCap is the read capability that can be shared with others to allow them to read messages from this channel. |
| `FirstMessageIndex` | `*bacap.MessageBoxIndex` | FirstMessageIndex is the first message index that should be used when writing messages to the channel. |
| `ErrorCode` | `uint8` | ErrorCode indicates the reason for a failure to create a new keypair if any. Otherwise it is set to zero for success. |

### EncryptWrite result (Rust/Python: EncryptWriteResult)

EncryptWriteReply is the reply to an EncryptWrite request.

| Field | Type | Description |
|---|---|---|
| `QueryID` | `*[QueryIDLength]byte` | QueryID is used for correlating this reply with the EncryptWrite request |
| `MessageCiphertext` | `[]byte` | MessageCiphertext is the encrypted message ciphertext that should be sent to the Courier service. |
| `EnvelopeDescriptor` | `[]byte` | EnvelopeDescriptor contains the serialized EnvelopeDescriptor that contains the private key material needed to decrypt the envelope reply. |
| `EnvelopeHash` | `*[32]byte` | EnvelopeHash is the hash of the CourierEnvelope that was sent to the mixnet and is used to resume the write operation. |
| `NextMessageBoxIndex` | `*bacap.MessageBoxIndex` | NextMessageBoxIndex is the next message box index to use for subsequent write operations. This is computed by the daemon using BACAP's NextIndex. |
| `ErrorCode` | `uint8` | ErrorCode indicates the reason for a failure to encrypt the write if any. Otherwise it is set to zero for success. |

### EncryptRead result (Rust/Python: EncryptReadResult)

EncryptReadReply is the reply to an EncryptRead request.

| Field | Type | Description |
|---|---|---|
| `QueryID` | `*[QueryIDLength]byte` | QueryID is used for correlating this reply with the EncryptRead request |
| `MessageCiphertext` | `[]byte` | MessageCiphertext is the encrypted message ciphertext that should be sent to the Courier service. |
| `EnvelopeDescriptor` | `[]byte` | EnvelopeDescriptor contains the serialized EnvelopeDescriptor that contains the private key material needed to decrypt the envelope reply. |
| `EnvelopeHash` | `*[32]byte` | EnvelopeHash is the hash of the CourierEnvelope that was sent to the mixnet and is used to resume the read operation. |
| `NextMessageBoxIndex` | `*bacap.MessageBoxIndex` | NextMessageBoxIndex is the next message box index to use for subsequent read operations. This is computed by the daemon using BACAP's NextIndex. |
| `ErrorCode` | `uint8` | ErrorCode indicates the reason for a failure to encrypt the read if any. Otherwise it is set to zero for success. |

### StartResendingEncryptedMessage result (Rust/Python: StartResendingResult)

StartResendingEncryptedMessageReply is the reply to a StartResendingEncryptedMessage request.

| Field | Type | Description |
|---|---|---|
| `QueryID` | `*[QueryIDLength]byte` | QueryID is used for correlating this reply with the StartResendingEncryptedMessage request |
| `Plaintext` | `[]byte` | Plaintext is the plaintext message that was read from the channel. |
| `ErrorCode` | `uint8` | ErrorCode indicates the reason for a failure to start resending the encrypted message if any. Otherwise it is set to zero for success. |
| `CourierIdentityHash` | `*[32]byte` | CourierIdentityHash is the 32-byte hash of the identity key of the courier that was selected to handle this message. Callers can watch PKI document updates for this courier disappearing from consensus and cancel+re-encrypt if it does. |
| `CourierQueueID` | `[]byte` | CourierQueueID is the queue ID of the courier that was selected. |

### StartResendingCopyCommand result

StartResendingCopyCommandReply is the reply to a StartResendingCopyCommand request.

| Field | Type | Description |
|---|---|---|
| `QueryID` | `*[QueryIDLength]byte` | QueryID is used for correlating this reply with the StartResendingCopyCommand request |
| `ErrorCode` | `uint8` | ErrorCode indicates the reason for a failure to execute the copy command if any. Otherwise it is set to zero for success. |
| `ReplicaErrorCode` | `uint8` | ReplicaErrorCode is the pigeonhole replica ErrorCode that caused the Copy command to abort on the courier. Meaningful only when ErrorCode indicates a Copy failure and the courier identified a specific replica-side reason (e.g. ReplicaErrorBoxAlreadyExists). |
| `FailedEnvelopeIndex` | `uint64` | FailedEnvelopeIndex is the 1-based sequential position in the copy stream of the envelope whose write triggered the abort. 0 if not applicable. Not a BACAP message index. |

### NextMessageBoxIndex result

NextMessageBoxIndexReply is the reply to a NextMessageBoxIndex request.

| Field | Type | Description |
|---|---|---|
| `QueryID` | `*[QueryIDLength]byte` | QueryID is used for correlating this reply with the NextMessageBoxIndex request |
| `NextMessageBoxIndex` | `*bacap.MessageBoxIndex` | NextMessageBoxIndex is the incremented message box index. |
| `ErrorCode` | `uint8` | ErrorCode indicates the reason for a failure to increment the index if any. Otherwise it is set to zero for success. |

### GetMessageBoxIndexCounter result

GetMessageBoxIndexCounterReply is the reply to a GetMessageBoxIndexCounter request.

| Field | Type | Description |
|---|---|---|
| `QueryID` | `*[QueryIDLength]byte` | QueryID is used for correlating this reply with the GetMessageBoxIndexCounter request. |
| `Counter` | `uint64` | Counter is the BACAP Idx64 value read out of the requested MessageBoxIndex. |
| `ErrorCode` | `uint8` | ErrorCode indicates the reason for a failure to read the counter if any. Otherwise it is set to zero for success. |

### GetPKIDocumentRaw result

GetPKIDocumentReply is the reply to a GetPKIDocument request. The
Payload field carries the cert.Certificate-wrapped signed PKI document
exactly as the daemon received it from the gateway, retaining every
directory authority signature so that callers may verify it
themselves.

| Field | Type | Description |
|---|---|---|
| `QueryID` | `*[QueryIDLength]byte` | QueryID is used for correlating this reply with the GetPKIDocument request. |
| `Payload` | `[]byte` | Payload is the cert.Certificate-wrapped signed PKI document, or nil on failure. Use core/pki.FromPayload to deserialize and verify it against the directory authorities' public keys. |
| `Epoch` | `uint64` | Epoch is the epoch of the returned document. When the request asked for the current epoch this echoes the epoch the daemon believes is current. |
| `ErrorCode` | `uint8` | ErrorCode indicates the reason for a failure to return a signed PKI document if any. Otherwise it is set to zero for success. |

### CreateCourierEnvelopesFromPayload result

CreateCourierEnvelopesFromPayloadReply is sent in response to a CreateCourierEnvelopesFromPayload request.
It provides multiple serialized CopyStreamElements, one for each chunk of the payload.

| Field | Type | Description |
|---|---|---|
| `QueryID` | `*[QueryIDLength]byte` | QueryID is used for correlating this reply with the CreateCourierEnvelopesFromPayload request that created it. |
| `Envelopes` | `[][]byte` | Envelopes is a slice of serialized CopyStreamElements, one per chunk. |
| `NextDestIndex` | `*bacap.MessageBoxIndex` | NextDestIndex is the next destination message box index after all boxes consumed by this call. Use this as DestStartIndex in subsequent calls to continue writing to the same destination stream. |
| `ErrorCode` | `uint8` | ErrorCode indicates the success or failure of the envelope creation. A value of ThinClientSuccess indicates successful creation. |

### CreateCourierEnvelopesFromMultiPayload result

CreateCourierEnvelopesFromPayloadsReply is sent in response to a CreateCourierEnvelopesFromPayloads request.
It provides multiple serialized CopyStreamElements packed efficiently from multiple destination payloads.

| Field | Type | Description |
|---|---|---|
| `QueryID` | `*[QueryIDLength]byte` | QueryID is used for correlating this reply with the CreateCourierEnvelopesFromPayloads request that created it. |
| `Envelopes` | `[][]byte` | Envelopes is a slice of serialized CopyStreamElements containing all the courier envelopes from all destinations packed efficiently together. |
| `Buffer` | `[]byte` | Buffer contains any data buffered by the encoder that hasn't been output yet. This can be persisted for crash recovery and restored via SetStreamBuffer. |
| `NextDestIndices` | `[]*bacap.MessageBoxIndex` | NextDestIndices contains the next destination message box index for each destination, in the same order as the destinations in the request. Use these as StartIndex in subsequent calls to continue writing to the same destination streams. |
| `ErrorCode` | `uint8` | ErrorCode indicates the success or failure of the envelope creation. A value of ThinClientSuccess indicates successful creation. |

### CreateCourierEnvelopesFromTombstoneRange result

CreateCourierEnvelopesFromTombstoneRangeReply is sent in response to a
CreateCourierEnvelopesFromTombstoneRange request. It provides serialized
CopyStreamElements containing tombstone courier envelopes.

| Field | Type | Description |
|---|---|---|
| `QueryID` | `*[QueryIDLength]byte` | QueryID is used for correlating this reply with the request. |
| `Envelopes` | `[][]byte` | Envelopes is a slice of serialized CopyStreamElements. |
| `Buffer` | `[]byte` | Buffer is the residual encoder buffer to pass to the next call. Nil when IsLast was true in the request. |
| `NextDestIndex` | `*bacap.MessageBoxIndex` | NextDestIndex is the next destination message box index after all tombstones created by this call. |
| `ErrorCode` | `uint8` | ErrorCode indicates the success or failure of the operation. |

### DestinationPayload (parameter)

DestinationPayload specifies a payload and its destination channel for multi-channel writes.

Passed *into* CreateCourierEnvelopesFromMultiPayload, one per destination channel.

| Field | Type | Description |
|---|---|---|
| `Payload` | `[]byte` | Payload is the data to be written to this destination. |
| `WriteCap` | `*bacap.WriteCap` | WriteCap is the write capability for the destination channel. |
| `StartIndex` | `*bacap.MessageBoxIndex` | StartIndex is the starting index in the destination channel. |

## Transport and Lifecycle Errors

These errors can in principle be raised by *any* method that performs
I/O against the daemon or the mixnet.

| Condition | Go | Rust | Python |
|---|---|---|---|
| Daemon not connected to mixnet | ad-hoc error with message "cannot send message in offline mode - daemon not connected to mixnet" (no sentinel — check `IsConnected()` first) | `ThinClientError::OfflineMode(String)` | `ThinClientOfflineError` |
| Operation timed out | `context.DeadlineExceeded` (from `ctx.Err()`) | `ThinClientError::Timeout(String)` | `asyncio.TimeoutError` |
| Operation cancelled by caller | `context.Canceled` (from `ctx.Err()`) | (no distinct variant — uses higher-level cancellation) | `asyncio.CancelledError` |
| Local socket to kpclientd lost | returned on the next I/O; thin client attempts reconnect with exponential backoff | ditto (receive `DaemonDisconnectedEvent` on the event sink) | ditto |
| CBOR (de)serialisation failure | wrapped error | `ThinClientError::CborError(serde_cbor::Error)` | `serde`-layer exception bubbles up |

The Go binding does not provide a named sentinel for offline mode.
Applications that must distinguish "daemon offline" from other errors
should test `IsConnected()` *before* sending, not compare error values
after the fact. The Rust and Python bindings provide proper sentinels
testable with `matches!` / `isinstance`.

## Replica and Courier Errors

The errors below can be returned by `StartResendingEncryptedMessage`
and its variants. They are defined in
[`pigeonhole/errors.go`](https://github.com/katzenpost/katzenpost/blob/main/pigeonhole/errors.go).

### Errors specific to reads (when `readCap` is set)

| Error | Go | Rust | Python |
|-------|-----|------|--------|
| Box not found (retries exhausted) | `ErrBoxIDNotFound` | `ThinClientError::BoxNotFound` | `BoxIDNotFoundError` |
| MKEM decryption failed | `ErrMKEMDecryptionFailed` | `ThinClientError::MkemDecryptionFailed` | `MKEMDecryptionFailedError` |
| BACAP decryption failed | `ErrBACAPDecryptionFailed` | `ThinClientError::BacapDecryptionFailed` | `BACAPDecryptionFailedError` |
| Tombstone (box was deleted) | `ErrTombstone` | `ThinClientError::Tombstone` | `TombstoneError` |

### Errors specific to writes (when `writeCap` is set)

| Error | Go | Rust | Python |
|-------|-----|------|--------|
| Storage full | `ErrStorageFull` | `ThinClientError::StorageFull` | `StorageFullError` |

### Errors on both reads and writes

| Error | Go | Rust | Python |
|-------|-----|------|--------|
| Operation cancelled | `ErrStartResendingCancelled` | `ThinClientError::StartResendingCancelled` | `StartResendingCancelledError` |
| Invalid box ID | `ErrInvalidBoxID` | `ThinClientError::InvalidBoxId` | `InvalidBoxIDError` |
| Invalid signature | `ErrInvalidSignature` | `ThinClientError::InvalidSignature` | `InvalidSignatureError` |
| Invalid tombstone signature | `ErrInvalidTombstoneSignature` | `ThinClientError::InvalidTombstoneSignature` | `InvalidTombstoneSignatureError` |
| Database failure | `ErrDatabaseFailure` | `ThinClientError::DatabaseFailure` | `DatabaseFailureError` |
| Invalid payload | `ErrInvalidPayload` | `ThinClientError::InvalidPayload` | `InvalidPayloadError` |
| Invalid epoch | `ErrInvalidEpoch` | `ThinClientError::InvalidEpoch` | `InvalidEpochError` |
| Replication failed | `ErrReplicationFailed` | `ThinClientError::ReplicationFailed` | `ReplicationFailedError` |
| Replica internal error | `ErrReplicaInternalError` | `ThinClientError::ReplicaInternalError` | `ReplicaInternalError` |
| Box already exists (writes only, when non-idempotent variant used) | `ErrBoxAlreadyExists` | `ThinClientError::BoxAlreadyExists` | `BoxAlreadyExistsError` |

### Copy-command failure

`StartResendingCopyCommand` can return a diagnostic error carrying the
underlying replica error code and the 1-based sequential envelope
index at which processing stopped:

| Binding | Error |
|---|---|
| Go | `ErrCopyCommandFailed` (see `CopyCommandFailedError` struct for fields) |
| Rust | `ThinClientError::CopyCommandFailed { replica_error_code, failed_envelope_index }` |
| Python | `CopyCommandFailedError(replica_error_code, failed_envelope_index)` |

## Expected Outcomes vs Real Failures

Some errors from `StartResendingEncryptedMessage` represent completed
operations, not failures. Use `IsExpectedOutcome(err)` (Go),
`err.is_expected_outcome()` (Rust), or `is_expected_outcome(exc)`
(Python) to distinguish them:

| Error | Why it may be expected |
|-------|------------------------|
| `BoxIDNotFound` / `BoxNotFound` | Polling for a message that hasn't been written yet |
| `BoxAlreadyExists` | Retrying an idempotent write that already succeeded |
| `Tombstone` | Reading a box that was intentionally deleted |

These should generally not trigger retries in your application.

