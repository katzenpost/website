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

There are three implementations:

| Language | Source | API Docs |
|----------|--------|----------|
| Go (reference) | [katzenpost/client/thin](https://github.com/katzenpost/katzenpost/tree/main/client/thin) | [pkg.go.dev](https://pkg.go.dev/github.com/katzenpost/katzenpost/client/thin) |
| Rust | [thin_client/src](https://github.com/katzenpost/thin_client/tree/main/src) | [docs.rs](https://docs.rs/katzenpost_thin_client) |
| Python | [thin_client/katzenpost_thinclient](https://github.com/katzenpost/thin_client/tree/main/katzenpost_thinclient) | [katzenpost.network](https://katzenpost.network/docs/python_thin_client.html) |

**NOTE** that this reference refers to unreleased software. Therefore
the rust crate and the python and golang libraries will not have
API documentation available at the expected locations until it is officially released.
*HOWEVER* you can make use of this software *right now* if you use our
release candidate tags:

| Thinclient Language(s) | Git repo | Release Candidate Git Tag |
|------------------------|----------|---------------------------|
| golang   | [github.com/katzenpost/katzenpost](https://github.com/katzenpost/katzenpost) | **v0.0.73-rc1**  |
| python & rust | [github.com/katzenpost/thinclient](https://github.com/katzenpost/thinclient) | **0.0.12-rc1** |


Also note that our production mix network known as `namenlos` does not currently run this candidate release
of katzenpost. Therefore in order to write new protocols and software against this candidate release you
can simply use a local docker mixnet:

In other words:

```bash
git clone https://github.com/katzenpost/katzenpost.git
cd katzenpost
git checkout v0.0.73-rc1
cd docker
make start wait run-ping
...
```

Note the location of the `thinclient.toml` configuration in the docker mixnet:
`katzenpost/docker/voting_mixnet/client/thinclient.toml`
You will need this to properly configure you thinclient for use with the docker mixnet.

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

---

## Connection Management

### Dial / new / start

Connect to the kpclientd daemon.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) Dial() error
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn new(config: Config) -> Result<Arc<Self>, Box<dyn std::error::Error>>
// Note: Rust connects during construction
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def start(self, loop: asyncio.AbstractEventLoop) -> None
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
def stop(self) -> None
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
def is_connected(self) -> bool
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
def disconnect(self) -> None
{{< /tab >}}
{{< /tabpane >}}

---

## Events

The thin client emits events for connection status changes, PKI
document updates, and message replies. Go uses an event channel; Rust
and Python use callbacks.

### EventSink / event_sink

Go and Rust use an event channel/receiver. Python uses async
callbacks passed to the `Config` constructor.

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
// Get a receiver that yields all events
let mut event_rx = client.event_sink();

tokio::spawn(async move {
    while let Some(event) = event_rx.recv().await {
        // Process event
    }
});
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
# Pass async callback functions to the Config constructor.
# Each callback receives a dict with event-specific keys.
# All callbacks are optional — omitted events are ignored.

async def on_connection_status(event):
    # event keys: 'is_connected' (bool), 'err' (str)
    print(f"Connected: {event['is_connected']}")

async def on_new_pki_document(event):
    # event keys: 'payload' (bytes) — CBOR-encoded PKI document
    pass

async def on_message_sent(event):
    # event keys: 'message_id' (bytes), 'surbid' (bytes|None),
    #   'sent_at' (str), 'reply_eta' (float), 'err' (str)
    pass

async def on_message_reply(event):
    # event keys: 'message_id' (bytes), 'surbid' (bytes|None),
    #   'payload' (bytes), 'reply_index' (int|None), 'error_code' (int)
    pass

async def on_daemon_disconnected(event):
    # Emitted when the connection to kpclientd is lost
    pass

config = Config(
    "thinclient.toml",
    on_connection_status=on_connection_status,
    on_new_pki_document=on_new_pki_document,
    on_message_sent=on_message_sent,
    on_message_reply=on_message_reply,
    on_daemon_disconnected=on_daemon_disconnected,
)
client = ThinClient(config)
{{< /tab >}}
{{< /tabpane >}}

### Event types

- **ConnectionStatusEvent** -- Emitted when the daemon's connection
  to the mixnet changes. Includes an `instance_token` field that
  uniquely identifies the daemon process.

- **NewPKIDocumentEvent** -- Emitted when a new PKI consensus
  document is received from the directory authorities.

- **MessageReplyEvent** -- Emitted when a reply to a `SendMessage`
  call is received. Contains the SURB ID and reply payload.

- **MessageSentEvent** -- Emitted when a `SendMessage` request has
  been transmitted by the daemon.

- **DaemonDisconnectedEvent** -- Emitted by the thin client (not the
  daemon) when the connection to the daemon is lost. Indicates
  whether the disconnect was graceful or unexpected.

---

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
def pki_document(self) -> "Dict[str, Any] | None"
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
pub async fn get_service(&self, service_name: &str) -> Result<ServiceDescriptor, ThinClientError>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
def get_service(self, service_name: str) -> ServiceDescriptor
{{< /tab >}}
{{< /tabpane >}}

### GetServices / get_services

Returns all instances of a service with the given capability name.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) GetServices(capability string) ([]*common.ServiceDescriptor, error)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// Use the standalone function:
pub fn find_services(capability: &str, doc: &BTreeMap<Value, Value>) -> Vec<ServiceDescriptor>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
def get_services(self, capability: str) -> "List[ServiceDescriptor]"
{{< /tab >}}
{{< /tabpane >}}

---

## Direct Messaging

These methods send messages directly to mixnet services (such as the
echo service). They are not used with Pigeonhole -- for Pigeonhole
communication, use the methods in the sections below.

### SendMessage / send_message

Sends a message with a SURB (Single Use Reply Block) that allows the
destination service to reply. This method is asynchronous: it returns
after the daemon accepts the request, not after the message is
delivered. To receive the reply, monitor events for a
`MessageReplyEvent` matching the SURB ID.

Raises `ThinClientOfflineError` (Python) / returns error (Go) /
`ThinClientError::OfflineMode` (Rust) if the daemon is not connected
to the mixnet.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) SendMessage(
    surbID *[SURBIDLength]byte,
    payload []byte,
    destNode *[32]byte,
    destQueue []byte,
) error
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
async def send_message(
    self,
    surb_id: bytes,
    payload: bytes | str,
    dest_node: bytes,
    dest_queue: bytes,
) -> None
{{< /tab >}}
{{< /tabpane >}}

### SendMessageWithoutReply / send_message_without_reply

Sends a fire-and-forget message with no SURB. The destination cannot
reply. Requires mixnet connectivity.

Raises `ThinClientOfflineError` (Python) / returns error (Go) /
`ThinClientError::OfflineMode` (Rust) if the daemon is not connected
to the mixnet.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) SendMessageWithoutReply(
    payload []byte,
    destNode *[32]byte,
    destQueue []byte,
) error
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
async def send_message_without_reply(
    self,
    payload: bytes | str,
    dest_node: bytes,
    dest_queue: bytes,
) -> None
{{< /tab >}}
{{< /tabpane >}}

### BlockingSendMessage / blocking_send_message

Sends a message and blocks until a reply is received or the timeout
expires. This is a convenience wrapper that generates a SURB ID,
sends the message, and waits for the matching reply event.

Raises `ThinClientOfflineError` (Python) / returns error (Go) /
`ThinClientError::OfflineMode` (Rust) if the daemon is not connected.
Raises `asyncio.TimeoutError` (Python) / `context.DeadlineExceeded`
(Go) / `ThinClientError::Timeout` (Rust) if the timeout expires.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) BlockingSendMessage(
    ctx context.Context,
    payload []byte,
    destNode *[32]byte,
    destQueue []byte,
) ([]byte, error)
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
async def blocking_send_message(
    self,
    payload: bytes | str,
    dest_node: bytes,
    dest_queue: bytes,
    timeout_seconds: float = 30.0,
) -> bytes
{{< /tab >}}
{{< /tabpane >}}

---

## Pigeonhole: Key Management

### NewKeypair / new_keypair

Generates a new BACAP keypair from a 32-byte seed. Returns the write
capability, read capability, and first message index for a new
Pigeonhole stream.

Does not cause network traffic. Does not store state in the daemon.

Raises `ValueError` (Python) / returns error (Go/Rust) if the seed
is not exactly 32 bytes.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) NewKeypair(
    seed []byte,
) (writeCap *bacap.WriteCap,
   readCap *bacap.ReadCap,
   firstMessageIndex *bacap.MessageBoxIndex,
   err error)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn new_keypair(
    &self,
    seed: &[u8; 32],
) -> Result<KeypairResult, ThinClientError>
// KeypairResult { write_cap: Vec<u8>, read_cap: Vec<u8>, first_index: Vec<u8> }
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def new_keypair(
    self,
    seed: bytes,
) -> KeypairResult
# KeypairResult contains: write_cap, read_cap, first_index
{{< /tab >}}
{{< /tabpane >}}

---

## Pigeonhole: Index Management

### NextMessageBoxIndex / next_message_box_index

Returns the next message box index in the sequence. This is a local
KDF computation -- it does not cause network traffic or store state.

If you have a BACAP implementation in your language, you can compute
this locally instead of making a round trip to the daemon.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) NextMessageBoxIndex(
    messageBoxIndex *bacap.MessageBoxIndex,
) (nextMessageBoxIndex *bacap.MessageBoxIndex, err error)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn next_message_box_index(
    &self,
    message_box_index: &[u8],
) -> Result<Vec<u8>, ThinClientError>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def next_message_box_index(
    self,
    message_box_index: bytes,
) -> bytes
{{< /tab >}}
{{< /tabpane >}}

---

## Pigeonhole: Encryption

### EncryptRead / encrypt_read

Creates an encrypted read request for a single Pigeonhole box. The
returned ciphertext and envelope data must be sent via
`StartResendingEncryptedMessage` to actually perform the read.

Does not cause network traffic. Does not store state in the daemon.

Returns the message ciphertext, envelope descriptor, envelope hash,
and the next message box index.

Raises `ValueError` (Python) / returns error (Go/Rust) if `readCap`
or `messageBoxIndex` is nil/None.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) EncryptRead(
    readCap *bacap.ReadCap,
    messageBoxIndex *bacap.MessageBoxIndex,
) (messageCiphertext []byte,
   envelopeDescriptor []byte,
   envelopeHash *[32]byte,
   nextMessageBoxIndex *bacap.MessageBoxIndex,
   err error)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn encrypt_read(
    &self,
    read_cap: &[u8],
    message_box_index: &[u8],
) -> Result<EncryptReadResult, ThinClientError>
// EncryptReadResult { message_ciphertext, envelope_descriptor, envelope_hash, next_message_box_index }
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def encrypt_read(
    self,
    read_cap: bytes,
    message_box_index: bytes,
) -> EncryptReadResult
# EncryptReadResult contains: message_ciphertext, envelope_descriptor,
#     envelope_hash, next_message_box_index
{{< /tab >}}
{{< /tabpane >}}

### EncryptWrite / encrypt_write

Creates an encrypted write request for a single Pigeonhole box. The
returned ciphertext and envelope data must be sent via
`StartResendingEncryptedMessage` to actually perform the write.

Does not cause network traffic. Does not store state in the daemon.

To create a tombstone (deletion marker), pass an empty byte slice as
the plaintext.

Returns the message ciphertext, envelope descriptor, envelope hash,
and the next message box index.

Raises `ValueError` (Python) / returns error (Go/Rust) if `writeCap`
or `messageBoxIndex` is nil/None.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) EncryptWrite(
    plaintext []byte,
    writeCap *bacap.WriteCap,
    messageBoxIndex *bacap.MessageBoxIndex,
) (messageCiphertext []byte,
   envelopeDescriptor []byte,
   envelopeHash *[32]byte,
   nextMessageBoxIndex *bacap.MessageBoxIndex,
   err error)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn encrypt_write(
    &self,
    plaintext: &[u8],
    write_cap: &[u8],
    message_box_index: &[u8],
) -> Result<EncryptWriteResult, ThinClientError>
// EncryptWriteResult { message_ciphertext, envelope_descriptor, envelope_hash, next_message_box_index }
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def encrypt_write(
    self,
    plaintext: bytes,
    write_cap: bytes,
    message_box_index: bytes,
) -> EncryptWriteResult
# EncryptWriteResult contains: message_ciphertext, envelope_descriptor,
#     envelope_hash, next_message_box_index
{{< /tab >}}
{{< /tabpane >}}

---

## Pigeonhole: ARQ Transport

### StartResendingEncryptedMessage / start_resending_encrypted_message

Sends an encrypted read or write request to a courier via the ARQ
(Automatic Repeat reQuest) mechanism. **Blocks** until the operation
completes or is cancelled.

**This method causes network traffic and stores ARQ state in the
daemon.** The daemon retransmits the request until it receives an
acknowledgment from the courier.

For writes, set `writeCap` and leave `readCap` as nil/None. For
reads, set `readCap` and leave `writeCap` as nil/None.

By default, writes treat `BoxAlreadyExists` as idempotent success,
and reads retry indefinitely on `BoxIDNotFound` (to handle
replication lag). Use the variant methods below for different
behavior.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) StartResendingEncryptedMessage(
    readCap *bacap.ReadCap,
    writeCap *bacap.WriteCap,
    messageBoxIndex []byte,
    replyIndex *uint8,
    envelopeDescriptor []byte,
    messageCiphertext []byte,
    envelopeHash *[32]byte,
) (*StartResendingResult, error)
// StartResendingResult { Plaintext []byte }
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
// StartResendingResult { plaintext: Vec<u8> }
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def start_resending_encrypted_message(
    self,
    read_cap: bytes | None,
    write_cap: bytes | None,
    next_message_index: bytes | None,
    reply_index: int | None,
    envelope_descriptor: bytes,
    message_ciphertext: bytes,
    envelope_hash: bytes,
) -> bytes  # plaintext
{{< /tab >}}
{{< /tabpane >}}

**Errors (reads -- `readCap` is set):**

| Error | Go | Rust | Python |
|-------|-----|------|--------|
| Box not found (retries exhausted) | `ErrBoxIDNotFound` | `ThinClientError::BoxNotFound` | `BoxIDNotFoundError` |
| MKEM decryption failed | `ErrMKEMDecryptionFailed` | `ThinClientError::MkemDecryptionFailed` | `MKEMDecryptionFailedError` |
| BACAP decryption failed | `ErrBACAPDecryptionFailed` | `ThinClientError::BacapDecryptionFailed` | `BACAPDecryptionFailedError` |
| Tombstone (box was deleted) | `ErrTombstone` | `ThinClientError::Tombstone` | `TombstoneError` |

**Errors (writes -- `writeCap` is set):**

| Error | Go | Rust | Python |
|-------|-----|------|--------|
| Storage full | `ErrStorageFull` | `ThinClientError::StorageFull` | `StorageFullError` |

**Errors (both reads and writes):**

| Error | Go | Rust | Python |
|-------|-----|------|--------|
| Operation cancelled | `ErrStartResendingCancelled` | `ThinClientError::StartResendingCancelled` | `StartResendingCancelledError` |
| Invalid box ID | `ErrInvalidBoxID` | `ThinClientError::InvalidBoxId` | `InvalidBoxIDError` |
| Invalid signature | `ErrInvalidSignature` | `ThinClientError::InvalidSignature` | `InvalidSignatureError` |
| Database failure | `ErrDatabaseFailure` | `ThinClientError::DatabaseFailure` | `DatabaseFailureError` |
| Invalid payload | `ErrInvalidPayload` | `ThinClientError::InvalidPayload` | `InvalidPayloadError` |
| Invalid epoch | `ErrInvalidEpoch` | `ThinClientError::InvalidEpoch` | `InvalidEpochError` |
| Replication failed | `ErrReplicationFailed` | `ThinClientError::ReplicationFailed` | `ReplicationFailedError` |
| Replica internal error | `ErrReplicaInternalError` | `ThinClientError::ReplicaInternalError` | `ReplicaInternalError` |

Note: `BoxAlreadyExists` is treated as success by default (idempotent write). Use `StartResendingEncryptedMessageReturnBoxExists` to get it as an error.
Note: `BoxIDNotFound` retries indefinitely by default. Use `StartResendingEncryptedMessageNoRetry` for immediate failure.

### StartResendingEncryptedMessageReturnBoxExists

Same as `StartResendingEncryptedMessage`, but returns
`BoxAlreadyExists` as an error instead of treating it as success. Use
this when you need to distinguish a new write from a repeated one.

Same errors as `StartResendingEncryptedMessage`, plus:

| Error | Go | Rust | Python |
|-------|-----|------|--------|
| Box already written | `ErrBoxAlreadyExists` | `ThinClientError::BoxAlreadyExists` | `BoxAlreadyExistsError` |

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) StartResendingEncryptedMessageReturnBoxExists(
    readCap *bacap.ReadCap, writeCap *bacap.WriteCap,
    messageBoxIndex []byte, replyIndex *uint8,
    envelopeDescriptor []byte, messageCiphertext []byte,
    envelopeHash *[32]byte,
) (*StartResendingResult, error)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn start_resending_encrypted_message_return_box_exists(
    &self,
    read_cap: Option<&[u8]>, write_cap: Option<&[u8]>,
    message_box_index: Option<&[u8]>, reply_index: Option<u8>,
    envelope_descriptor: &[u8], message_ciphertext: &[u8],
    envelope_hash: &[u8; 32],
) -> Result<StartResendingResult, ThinClientError>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def start_resending_encrypted_message_return_box_exists(
    self,
    read_cap: bytes | None, write_cap: bytes | None,
    next_message_index: bytes | None, reply_index: int | None,
    envelope_descriptor: bytes, message_ciphertext: bytes,
    envelope_hash: bytes,
) -> bytes
{{< /tab >}}
{{< /tabpane >}}

### StartResendingEncryptedMessageNoRetry

Same as `StartResendingEncryptedMessage`, but returns
`BoxIDNotFound` immediately instead of retrying indefinitely. Use
this when polling for a message that may not exist yet.

Same errors as `StartResendingEncryptedMessage`, but `BoxIDNotFound`
is returned on the first occurrence instead of being retried.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) StartResendingEncryptedMessageNoRetry(
    readCap *bacap.ReadCap, writeCap *bacap.WriteCap,
    messageBoxIndex []byte, replyIndex *uint8,
    envelopeDescriptor []byte, messageCiphertext []byte,
    envelopeHash *[32]byte,
) (*StartResendingResult, error)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn start_resending_encrypted_message_no_retry(
    &self,
    read_cap: Option<&[u8]>, write_cap: Option<&[u8]>,
    message_box_index: Option<&[u8]>, reply_index: Option<u8>,
    envelope_descriptor: &[u8], message_ciphertext: &[u8],
    envelope_hash: &[u8; 32],
) -> Result<StartResendingResult, ThinClientError>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def start_resending_encrypted_message_no_retry(
    self,
    read_cap: bytes | None, write_cap: bytes | None,
    next_message_index: bytes | None, reply_index: int | None,
    envelope_descriptor: bytes, message_ciphertext: bytes,
    envelope_hash: bytes,
) -> bytes
{{< /tab >}}
{{< /tabpane >}}

### CancelResendingEncryptedMessage / cancel_resending_encrypted_message

Cancels an in-flight `StartResendingEncryptedMessage` operation.
The blocked caller receives a `StartResendingCancelled` error.
Removes the operation from in-flight tracking so it will not be
replayed on reconnect.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) CancelResendingEncryptedMessage(
    envelopeHash *[32]byte,
) error
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn cancel_resending_encrypted_message(
    &self,
    envelope_hash: &[u8; 32],
) -> Result<(), ThinClientError>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def cancel_resending_encrypted_message(
    self,
    envelope_hash: bytes,
) -> None
{{< /tab >}}
{{< /tabpane >}}

---

## Pigeonhole: Tombstones

### TombstoneRange / tombstone_range

Creates encrypted tombstone envelopes for a range of consecutive
boxes. Tombstones are writes with an empty payload that delete the
box contents.

Does not cause network traffic. The caller must send each envelope
individually via `StartResendingEncryptedMessage`.

To tombstone a single box, use `maxCount=1`.

Returns a result containing the list of tombstone envelopes and the
next index after the last tombstoned box.

Raises `ValueError` (Python) / returns error (Go) if `writeCap` or
`start` is nil/None. If an error occurs mid-range, returns a partial
result with the envelopes created so far.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) TombstoneRange(
    writeCap *bacap.WriteCap,
    start *bacap.MessageBoxIndex,
    maxCount uint32,
) (*TombstoneRangeResult, error)
// TombstoneRangeResult { Envelopes []*TombstoneEnvelope, Next *bacap.MessageBoxIndex }
// TombstoneEnvelope { MessageCiphertext, EnvelopeDescriptor, EnvelopeHash, BoxIndex }
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn tombstone_range(
    &self,
    write_cap: &[u8],
    start: &[u8],
    max_count: u32,
) -> TombstoneRangeResult
// TombstoneRangeResult { envelopes: Vec<TombstoneEnvelope>, next: Vec<u8> }
// TombstoneEnvelope { message_ciphertext, envelope_descriptor, envelope_hash, box_index }
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def tombstone_range(
    self,
    write_cap: bytes,
    start: bytes,
    max_count: int,
) -> TombstoneRangeResult
# TombstoneRangeResult contains: envelopes (list of TombstoneEnvelope), next
# TombstoneEnvelope contains: message_ciphertext, envelope_descriptor,
#     envelope_hash, box_index
{{< /tab >}}
{{< /tabpane >}}

---

## Pigeonhole: Copy Stream Construction

These methods construct courier envelopes encoded as copy stream
elements, ready to be written to a temporary copy stream channel.
After writing all elements, send a copy command
(`StartResendingCopyCommand`) to instruct a courier to process them.

All three methods are stateless -- they do not cause network traffic
or store state in the daemon.

### CreateCourierEnvelopesFromPayload / create_courier_envelopes_from_payload

Packs a single payload for one destination into copy stream elements.
The payload can be up to 10 MB. Returns properly sized chunks ready
to be written to boxes via `EncryptWrite`.

Use `isStart=true` on the first call and `isLast=true` on the final
call. For a single-call copy stream, set both to `true`.

Raises `ValueError` (Python) / returns error (Go/Rust) if
`destWriteCap` or `destStartIndex` is nil/None.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) CreateCourierEnvelopesFromPayload(
    payload []byte,
    destWriteCap *bacap.WriteCap,
    destStartIndex *bacap.MessageBoxIndex,
    isStart bool,
    isLast bool,
) (envelopes [][]byte, nextDestIndex *bacap.MessageBoxIndex, err error)
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
// CreateEnvelopesResult { envelopes: Vec<Vec<u8>>, next_dest_index: Vec<u8> }
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def create_courier_envelopes_from_payload(
    self,
    payload: bytes,
    dest_write_cap: bytes,
    dest_start_index: bytes,
    is_start: bool,
    is_last: bool,
) -> CreateEnvelopesResult
# CreateEnvelopesResult contains: envelopes, next_dest_index
{{< /tab >}}
{{< /tabpane >}}

### CreateCourierEnvelopesFromMultiPayload / create_courier_envelopes_from_multi_payload

Packs multiple payloads for different destinations into copy stream
elements. More space-efficient than calling
`CreateCourierEnvelopesFromPayload` multiple times because envelopes
are packed together without wasted padding.

This method supports multi-call usage via the `buffer` parameter.
Pass `nil`/`None` on the first call, then pass the returned buffer
to subsequent calls. The application is responsible for persisting
the buffer for crash recovery.

Raises `ValueError` (Python) / returns error (Go/Rust) if
`destinations` is empty.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) CreateCourierEnvelopesFromMultiPayload(
    destinations []DestinationPayload,
    isStart bool,
    isLast bool,
    buffer []byte,
) (*CreateEnvelopesResult, error)
// DestinationPayload { Payload []byte, WriteCap *bacap.WriteCap, StartIndex *bacap.MessageBoxIndex }
// CreateEnvelopesResult { Envelopes [][]byte, Buffer []byte }
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn create_courier_envelopes_from_multi_payload(
    &self,
    destinations: Vec<(&[u8], &[u8], &[u8])>,  // (payload, write_cap, start_index)
    is_start: bool,
    is_last: bool,
    buffer: Option<Vec<u8>>,
) -> Result<CreateEnvelopesResult, ThinClientError>
// CreateEnvelopesResult { envelopes: Vec<Vec<u8>>, buffer: Option<Vec<u8>> }
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def create_courier_envelopes_from_multi_payload(
    self,
    destinations: List[Dict[str, Any]],
    # Each dict: {"payload": bytes, "write_cap": bytes, "start_index": bytes}
    is_start: bool,
    is_last: bool,
    buffer: bytes | None = None,
) -> CreateEnvelopesResult
# CreateEnvelopesResult contains: envelopes, buffer
{{< /tab >}}
{{< /tabpane >}}

### CreateCourierEnvelopesFromTombstoneRange / create_courier_envelopes_from_tombstone_range

Packs tombstone envelopes for a range of consecutive destination
boxes into copy stream elements. Use this to atomically tombstone
boxes as part of a copy command (the courier performs the tombstoning).

Like `CreateCourierEnvelopesFromMultiPayload`, this method supports
multi-call usage via the `buffer` parameter.

Raises `ValueError` (Python) / returns error (Go/Rust) if
`destWriteCap` or `destStartIndex` is nil/None.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) CreateCourierEnvelopesFromTombstoneRange(
    destWriteCap *bacap.WriteCap,
    destStartIndex *bacap.MessageBoxIndex,
    maxCount uint32,
    isStart bool,
    isLast bool,
    buffer []byte,
) (envelopes [][]byte, nextBuffer []byte,
   nextDestIndex *bacap.MessageBoxIndex, err error)
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
// CreateEnvelopesResult { envelopes: Vec<Vec<u8>>, buffer: Option<Vec<u8>>, next_dest_index: Vec<u8> }
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def create_courier_envelopes_from_tombstone_range(
    self,
    dest_write_cap: bytes,
    dest_start_index: bytes,
    max_count: int,
    is_start: bool,
    is_last: bool,
    buffer: bytes | None = None,
) -> CreateEnvelopesResult
# CreateEnvelopesResult contains: envelopes, buffer, next_dest_index
{{< /tab >}}
{{< /tabpane >}}

---

## Pigeonhole: Copy Command Transport

### StartResendingCopyCommand / start_resending_copy_command

Sends a copy command to a courier via ARQ and **blocks** until the
courier acknowledges completion. The courier reads the temporary copy
stream, executes each envelope, tombstones the temporary stream, and
sends an ACK.

**This method causes network traffic and stores ARQ state in the
daemon.**

Raises `ValueError` (Python) / returns error (Go/Rust) if `writeCap`
is nil/None. Returns `StartResendingCancelledError` (Python) /
`ErrStartResendingCancelled` (Go) /
`ThinClientError::StartResendingCancelled` (Rust) if cancelled via
`CancelResendingCopyCommand`.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) StartResendingCopyCommand(
    writeCap *bacap.WriteCap,
) error
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
async def start_resending_copy_command(
    self,
    write_cap: bytes,
    courier_identity_hash: bytes | None = None,
    courier_queue_id: bytes | None = None,
) -> None
{{< /tab >}}
{{< /tabpane >}}

### StartResendingCopyCommandWithCourier (Go only)

Like `StartResendingCopyCommand` but sends to a specific courier
instead of a random one. Used for nested copy commands.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) StartResendingCopyCommandWithCourier(
    writeCap *bacap.WriteCap,
    courierIdentityHash *[32]byte,
    courierQueueID []byte,
) error
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// Use start_resending_copy_command with courier_identity_hash
// and courier_queue_id parameters set
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
# Use start_resending_copy_command with courier_identity_hash
# and courier_queue_id parameters set
{{< /tab >}}
{{< /tabpane >}}

### CancelResendingCopyCommand / cancel_resending_copy_command

Cancels an in-flight copy command. The parameter is the blake2b-256
hash of the serialized write capability.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) CancelResendingCopyCommand(
    writeCapHash *[32]byte,
) error
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub async fn cancel_resending_copy_command(
    &self,
    write_cap_hash: &[u8; 32],
) -> Result<(), ThinClientError>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
async def cancel_resending_copy_command(
    self,
    write_cap_hash: bytes,
) -> None
{{< /tab >}}
{{< /tabpane >}}

---

## Pigeonhole: Courier Discovery (Go only)

### GetAllCouriers

Returns all courier services from the current PKI document.

```go
func (t *ThinClient) GetAllCouriers() ([]CourierDescriptor, error)
```

### GetDistinctCouriers

Returns N distinct random couriers. Returns an error if fewer than N
are available.

```go
func (t *ThinClient) GetDistinctCouriers(n int) ([]CourierDescriptor, error)
```

### CourierDescriptor

```go
type CourierDescriptor struct {
    IdentityHash *[32]byte
    QueueID      []byte
}
```

---

## Pigeonhole: Nested Copy (Go only, experimental)

### SendNestedCopy

Sends a recursive copy command routed through a path of couriers.
This constructs nested copy streams so that the payload traverses
multiple couriers before reaching its final destination.

```go
func (t *ThinClient) SendNestedCopy(
    payload []byte,
    destWriteCap *bacap.WriteCap,
    destFirstIndex *bacap.MessageBoxIndex,
    courierPath []CourierDescriptor,
) error
```

---

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
@staticmethod
def new_message_id() -> bytes
{{< /tab >}}
{{< /tabpane >}}

### NewSURBID / new_surb_id

Returns a new random SURB ID for correlating message replies.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func (t *ThinClient) NewSURBID() *[SURBIDLength]byte
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub fn new_surb_id() -> Vec<u8>
{{< /tab >}}
{{< tab header="Python" lang="python" >}}
def new_surb_id(self) -> bytes
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
def new_query_id(self) -> bytes
{{< /tab >}}
{{< /tabpane >}}

---

## Expected Outcomes vs Real Failures

Some errors from `StartResendingEncryptedMessage` represent completed
operations, not failures. Use `IsExpectedOutcome` (Go) /
`is_expected_outcome()` (Rust/Python) to distinguish them:

| Error | Why it may be expected |
|-------|----------------------|
| `BoxIDNotFound` / `BoxNotFound` | Polling for a message that hasn't been written yet |
| `BoxAlreadyExists` | Retrying an idempotent write that already succeeded |
| `Tombstone` | Reading a box that was intentionally deleted |

These should generally not trigger retries in your application.
