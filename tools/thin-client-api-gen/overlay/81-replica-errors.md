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
