## Configuration and Construction

The thin client is configured via a TOML file that specifies only how
to reach the local daemon. We usually name this configuration file
`thinclient.toml`. The Sphinx and Pigeonhole geometries are supplied
by the daemon over the socket during the connection handshake, so the
client never configures them and they cannot drift out of step with
the daemon.

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

The geometries the daemon supplied are available after connecting:
`GetSphinxGeometry()` / `GetPigeonholeGeometry()` on the Go
`ThinClient`, `sphinx_geometry()` / `pigeonhole_geometry()` on the
Rust client, and the `geometry` / `pigeonhole_geometry` attributes of
the Python client.

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
