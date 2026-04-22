---
title:
linkTitle: "Thin Client API Reference"
description: "Complete API reference for the Katzenpost thin client libraries (Go, Rust, Python)"
categories: [""]
tags: [""]
author: []
version: 0
draft: false
slug: "/thin_client_api_reference/"
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

There are three implementations:

| Language | Source | Release candidate |
|----------|--------|-------------------|
| Go (reference) | [katzenpost/client/thin](https://github.com/katzenpost/katzenpost/tree/main/client/thin) | `v0.0.73-rc2` |
| Rust | [thin_client/src](https://github.com/katzenpost/thin_client/tree/main/src) | `0.0.12-rc2` |
| Python | [thin_client/katzenpost_thinclient](https://github.com/katzenpost/thin_client/tree/main/katzenpost_thinclient) | `0.0.12-rc2` |

For conceptual background on Pigeonhole, see [Understanding Pigeonhole](/docs/pigeonhole_explained/).
For task-oriented usage guides, see [Thin Client How-to Guide](/docs/thin_client_howto/).

---

## Configuration and Construction

The thin client is configured via a TOML file that specifies the
daemon socket path and network geometry. We usually name this
configuration file `thinclient.toml`.

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

## Connection Management

### Dial / new / start

Connect to the kpclientd daemon. The Rust binding connects during
construction (`ThinClient::new`), whereas Go and Python construct the
client first and then connect via `Dial()` / `start()`.

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

Disconnect from the daemon and shut down the thin client. All blocked
callers receive an error.

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

Returns whether the daemon is currently connected to the mixnet.

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

Disconnect from the daemon without shutting down. The thin client will
automatically reconnect with exponential backoff.

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

- **DaemonDisconnectedEvent** — emitted by the thin client (not the
  daemon) when the local socket connection to the daemon is lost.
  Fields (Go): `IsGraceful bool`, `Err error`.

### EventSink / event_sink

Returns a channel (Go) or receiver (Rust) that yields events from the
daemon. Python uses async callbacks supplied via the `Config`
constructor, so has no equivalent method.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) EventSink() chan Event
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub fn event_sink(&self) -> EventSinkReceiver
{{< /tab >}}
{{< /tabpane >}}

### StopEventSink (Go only)

Stops delivering events on the given channel. Rust receivers are
dropped via their own lifetime; Python's callback model requires no
teardown.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) StopEventSink(ch chan Event)
{{< /tab >}}
{{< /tabpane >}}

## PKI and Service Discovery

### PKIDocument / pki_document

Returns the current PKI consensus document, which contains the
network topology and available services.

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

### GetService / get_service

Returns a random instance of the named service from the PKI document.
The result contains the destination node hash and queue ID needed for
sending messages to that service.

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

Returns all instances of a service with the given capability name.
The Rust binding exposes this as a standalone helper in `helpers.rs`,
not a method on `ThinClient`.

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

Sends a message with a SURB (Single Use Reply Block) that allows the
destination service to reply. This method is asynchronous: it returns
after the daemon accepts the request, not after the message is
delivered. To receive the reply, monitor events for a
`MessageReplyEvent` matching the SURB ID. See "Transport and
Lifecycle Errors" below for the error raised when offline.

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

Sends a fire-and-forget message with no SURB. The destination cannot
reply.

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

Sends a message and blocks until a reply is received or the timeout
expires. This is a convenience wrapper that generates a SURB ID,
sends the message, and waits for the matching reply event.

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

Generates a new BACAP keypair from a 32-byte seed. Returns the write
capability, read capability, and first message index for a new
Pigeonhole stream. Does not cause network traffic.

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

Returns the next message box index in the sequence. This is a local
KDF computation — it does not cause network traffic or store state.
If you have a BACAP implementation in your language, you can compute
this locally instead of making a round trip to the daemon.

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

Creates an encrypted read request for a single Pigeonhole box. The
returned ciphertext and envelope data must be sent via
`StartResendingEncryptedMessage` to actually perform the read.
Does not cause network traffic.

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

Creates an encrypted write request for a single Pigeonhole box. The
returned ciphertext and envelope data must be sent via
`StartResendingEncryptedMessage` to actually perform the write.
To create a tombstone (deletion marker), pass an empty byte slice as
the plaintext.

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

Sends an encrypted read or write request to a courier via the ARQ
(Automatic Repeat reQuest) mechanism. **Blocks** until the operation
completes or is cancelled. The daemon retransmits the request until
it receives an acknowledgment from the courier. By default writes
treat `BoxAlreadyExists` as idempotent success, and reads retry
indefinitely on `BoxIDNotFound`.

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

Same as the default variant, but returns `BoxAlreadyExists` as an
error instead of treating it as success. Use this when you need to
distinguish a new write from a repeated one.

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

Same as the default variant, but returns `BoxIDNotFound` immediately
instead of retrying indefinitely. Use this when polling for a message
that may not exist yet.

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

Cancels an in-flight `StartResendingEncryptedMessage` operation.
The blocked caller receives a `StartResendingCancelled` error.
Removes the operation from in-flight tracking so it will not be
replayed on reconnect.

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

Creates encrypted tombstone envelopes for a range of consecutive
boxes. Tombstones are writes with an empty payload that delete the
box contents. Does not cause network traffic; the caller must send
each envelope individually via `StartResendingEncryptedMessage`.

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

Packs a single payload for one destination into copy stream elements.
The payload can be up to ~10 MB. Returns properly sized chunks ready
to be written to boxes via `EncryptWrite`.

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

Packs multiple payloads for different destinations into copy stream
elements. More space-efficient than calling the single-payload
variant multiple times because envelopes are packed together without
wasted padding.

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

Packs tombstone envelopes for a range of consecutive destination
boxes into copy stream elements. Use this to atomically tombstone
boxes as part of a copy command.

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

Sends a copy command to a courier via ARQ and **blocks** until the
courier acknowledges completion. The courier reads the temporary
copy stream, executes each envelope, tombstones the temporary
stream, and sends an ACK. The Rust and Python bindings take
optional courier-identity parameters to pin the command to a
specific courier; the Go binding exposes this as a separate
method (see below).

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

Like `StartResendingCopyCommand` but sends to a specific courier
instead of a random one. Used for nested copy commands. In Rust
and Python this is achieved by supplying the optional
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

Cancels an in-flight copy command. The parameter is the blake2b-256
hash of the serialized write capability.

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

Returns every courier service advertised in the current PKI
document. Not yet exposed in the Rust binding.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) GetAllCouriers() (couriers []CourierDescriptor, err error)
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
def get_all_couriers(self) -> 'List[Tuple[bytes, bytes]]':
{{< /tab >}}
{{< /tabpane >}}

### GetDistinctCouriers / get_distinct_couriers

Returns `n` distinct couriers drawn at random from the current PKI
document. Not yet exposed in the Rust binding.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) GetDistinctCouriers(n int) (couriers []CourierDescriptor, err error)
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
def get_distinct_couriers(self, n: int) -> 'List[Tuple[bytes, bytes]]':
{{< /tab >}}
{{< /tabpane >}}

### get_courier_destination (Rust only)

Returns a single courier destination as a
`(identity_hash, queue_id)` tuple, sparing the caller from
handling a list. Go and Python callers achieve the same by
calling `GetDistinctCouriers(1)` / `get_distinct_couriers(1)`
and taking the first element.

{{< tabpane >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn get_courier_destination(
    &self,
) -> Result<(Vec<u8>, Vec<u8>), ThinClientError>
{{< /tab >}}
{{< /tabpane >}}

### pigeonhole_geometry (Rust only)

Returns a reference to the negotiated Pigeonhole geometry, so that
callers can size payloads to its `max_plaintext_payload_length`.
Go callers obtain this via `GetConfig().PigeonholeGeometry`; the
Python binding stores it internally but does not currently expose
an accessor.

{{< tabpane >}}
{{< tab header="Rust" lang="rust" >}}
pub fn pigeonhole_geometry(&self) -> &PigeonholeGeometry
{{< /tab >}}
{{< /tabpane >}}

## Utility

### NewMessageID / new_message_id

Returns a new random message ID (16 bytes).

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

Returns a new random SURB ID for correlating message replies.

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

Returns a new random query ID for correlating requests and replies
within the thin client protocol.

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

