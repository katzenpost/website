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
