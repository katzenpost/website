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
