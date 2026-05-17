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

<!-- DATA_TYPES_TABLE -->
