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
