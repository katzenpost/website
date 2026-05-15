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

### The `thinclient.toml` file

The file has three tables. `[SphinxGeometry]` and
`[PigeonholeGeometry]` describe the network the daemon is part of and
**must match the values the operator's network was configured with**;
they are not free parameters a client invents. `[Dial]` tells the thin
client where the local daemon socket is and is the only table most
applications set by hand. The geometry values are normally obtained
from the operator (or copied from the daemon's own configuration).

A representative file:

```toml
[SphinxGeometry]
  PacketLength = 3082
  NrHops = 5
  HeaderLength = 476
  RoutingInfoLength = 410
  PerHopRoutingInfoLength = 82
  SURBLength = 572
  SphinxPlaintextHeaderLength = 2
  PayloadTagLength = 32
  ForwardPayloadLength = 2574
  UserForwardPayloadLength = 2000
  NextNodeHopLength = 65
  SPRPKeyMaterialLength = 64
  NIKEName = "x25519"
  KEMName = ""

[PigeonholeGeometry]
  MaxPlaintextPayloadLength = 1553
  CourierQueryReadLength = 359
  CourierQueryWriteLength = 2000
  CourierQueryReplyReadLength = 1698
  CourierQueryReplyWriteLength = 50
  NIKEName = "CTIDH1024-X25519"
  SignatureSchemeName = "Ed25519"

[Dial]
  [Dial.Tcp]
    Address = "localhost:64331"
    Network = "tcp"
```

**`[SphinxGeometry]`** describes the Sphinx packet format:

| Key | Type | Meaning |
|---|---|---|
| `PacketLength` | int | Total Sphinx packet size in bytes. |
| `NrHops` | int | Number of mix hops a packet traverses. |
| `HeaderLength` | int | Sphinx header size. |
| `RoutingInfoLength` | int | Total routing-information size. |
| `PerHopRoutingInfoLength` | int | Routing information per hop. |
| `SURBLength` | int | Single-Use Reply Block size. |
| `SphinxPlaintextHeaderLength` | int | Plaintext header size. |
| `PayloadTagLength` | int | SPRP authentication tag size. |
| `ForwardPayloadLength` | int | Total payload carrier size. |
| `UserForwardPayloadLength` | int | Usable payload size before Pigeonhole overhead. |
| `NextNodeHopLength` | int | Size of the largest routing block. |
| `SPRPKeyMaterialLength` | int | SPRP key material size. |
| `NIKEName` | string | NIKE scheme name (e.g. `"x25519"`); empty if a KEM is used. |
| `KEMName` | string | KEM scheme name; empty if a NIKE is used. |

**`[PigeonholeGeometry]`** sizes the Pigeonhole protocol, and is
derived from, and consistent with, the Sphinx geometry above:

| Key | Type | Meaning |
|---|---|---|
| `MaxPlaintextPayloadLength` | int | Largest application payload that fits in one box; larger messages must be split. |
| `CourierQueryReadLength` | int | Size of a read query to the courier. |
| `CourierQueryWriteLength` | int | Size of a write query to the courier. |
| `CourierQueryReplyReadLength` | int | Size of a courier reply to a read. |
| `CourierQueryReplyWriteLength` | int | Size of a courier reply to a write. |
| `NIKEName` | string | NIKE scheme used for MKEM envelope encryption. |
| `SignatureSchemeName` | string | Signature scheme used for box signing. |

**`[Dial]`** selects the daemon transport. Set exactly one of the two
sub-tables:

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
