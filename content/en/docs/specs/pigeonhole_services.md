---
title: "Pigeonhole services"
linkTitle: "Pigeonhole services"
description: "How clients discover and connect to pigeonhole services through the service directory and the voucher router"
author: "David Stainton"
url: ""
date: "2026-10-29T00:00:00Z"
draft: "false"
slug: "pigeonhole_services"
layout: ""
type: ""
weight: "16"
version: "0"
---

This document explains how three components work together to let a client
reach a pigeonhole service it has never talked to. Two are programs that
mixnet operators run; the third is a library for writing pigeonhole services.

- The **service directory** (capability `service_directory`) holds a
  descriptor for each pigeonhole service, saying how to reach it. It is the
  `service-directory` program in
  [katzenpost](https://github.com/katzenpost/katzenpost), under
  `cmd/service-directory`, built on the `pigeonservice/discovery` package.
  Operators run it as a plugin on a service node.
- The **voucher router** (capability `voucher_router`) relays a client's
  first message to a pigeonhole service. It is the `voucher-router` program
  in [katzenpost](https://github.com/katzenpost/katzenpost), under
  `cmd/voucher-router`, built on the `pigeonservice/voucher_router` package.
  Operators run it as a plugin on a service node.
- The **pigeonhole service library** is for writing pigeonhole services, and
  the clients that reach them, in Go or Rust. A pigeonhole service is the
  responder side of an initiator–responder protocol over Pigeonhole: it
  accepts new connections from clients and then speaks its own protocol over
  each one, such as a bot that joins group chats, or a binary protocol no
  human reads. The Go library is the `pigeonservice` package of
  [pigeonhole_protocols](https://github.com/katzenpost/pigeonhole_protocols),
  under `go/pigeonservice`, over the `pigeonservice/common`,
  `pigeonservice/voucher_router` and `pigeonservice/discovery` packages of
  katzenpost, which hold what the plugins and the services share; the Rust
  library is the `pigeonservice` module of the `pigeonhole_protocols` crate,
  under `rust/src/pigeonservice`. The same repository has services written
  with them: ELIZA and a Zulip bridge in Rust, the message of the day in Go.
  The two libraries speak the same wire format.

| Part | Where | Revision |
|---|---|---|
| Service directory and voucher router | katzenpost `cmd/service-directory`, `cmd/voucher-router`, `pigeonservice/{common,voucher_router,discovery}` | main [`fc420a396b0d`](https://github.com/katzenpost/katzenpost/commit/fc420a396b0d8e65d418c6736d824c71fb751c49) holds the first version, as `pigeonservice/{directory,router}`; the split ([#1256](https://github.com/katzenpost/katzenpost/pull/1256)) and the leases ([#1259](https://github.com/katzenpost/katzenpost/pull/1259)) are in review |
| Go and Rust libraries | pigeonhole_protocols `go/pigeonservice`, `rust/src/pigeonservice` | main [`ad9d3e270f4e`](https://github.com/katzenpost/pigeonhole_protocols/commit/ad9d3e270f4e); the leases and the Rust module ([#22](https://github.com/katzenpost/pigeonhole_protocols/pull/22)) are in review |
| ELIZA, zulip-bridge, motd | pigeonhole_protocols `rust/src/bin`, `go/cmd` | main [`ad9d3e270f4e`](https://github.com/katzenpost/pigeonhole_protocols/commit/ad9d3e270f4e) |
| Rust thin client | thin_client [#100](https://github.com/katzenpost/thin_client/pull/100) | in review |

The revisions change as that stack merges; this table names the commit on
`main` that holds what the text describes.

A pigeonhole service has no address and no open port; everything it sends
or receives is a box on the storage replicas. The directory and the router
bootstrap the first contact.

Many operators should run the directory and the router. If one operator ran
the only instance of each, that operator would be a single point of failure
for every pigeonhole service. With two or more there is none: a pigeonhole
service registers with every router and advertises in every directory the
PKI document lists, and a client can look it up in any directory and route through
any of a service's routers. A pigeonhole service notices when a new PKI
document lists more routers or directories, and starts using them.

![The bootstrap of a connection](/docs/specs/pix/pigeonhole_services.svg)

Afterwards the client and the service share a connection of two Pigeonhole
streams, one written by each, and each holds the other's read cap. The
router and the directory take no further part. Every party reaches the
mixnet through a client daemon, kpclientd, which does all the cryptography
that involves keys.

## Contact vouchers

Every connection starts from a contact voucher: one side mints it, the other
uses it, and both end up holding each other's read cap. A voucher can be
used once. The protocol is specified in [Contact
voucher](/docs/specs/contactvoucher/) and narrated
in [Contact voucher protocol
narration](/docs/specs/contact_voucher_narration/).
Here it matters only who mints the voucher and how it travels.

A client could instead send a service a read cap and a write cap directly.
Vouchers are used because:

- **Forward secrecy.** Routers keep forwarded messages for days, sealed to
  the service's long-term key. Caps in them would stay valid for anyone who
  later gets that key; a used voucher is worthless, since its payload is
  tombstoned and its reply is sealed to a key only the client holds.
- **Each side makes its own stream.** No one holds a write cap to the other's
  stream.
- **The client knows it was accepted.** The voucher reply confirms the
  connection; with bare caps the client cannot tell an idle service from one
  that never got them.
- **One token for every path.** The same short, single-use token is routed,
  offered, or pasted into a chat app.

The cost is a few extra round trips before the first message.

## Identity

A service is known by its NIKE keypair, `x25519-ctidh1024`, kept in its data
directory so it survives restarts. Its `ServiceID` is the BLAKE2b-256 hash of
the public key, written as 64 hex digits.

The router and the directory publish their NIKE public keys in the PKI
document, as the parameters `nikeScheme` and `publicKey` of their service
node entry. A client trusts a router or a directory because the PKI lists
it, and trusts nothing a directory says without checking it against the PKI.

## Registering with routers

A service mints a voucher and sends it to each voucher router in the PKI in
a `RegisterRequest`, with its public key, a sequence number, the expiry it
asks for and a MAC. The router uses the voucher, and the connection that
results is the service's *link* with that router. The router writes every
sealed voucher addressed to the service to the link as a `LinkMessage`, and
keeps them rewritten for seven days, so a service that was offline still
receives them.

A link is a lease (see [Lifetimes](#lifetimes)): the service renews it with
a `RenewRequest` once half of it has passed, closes it with an
`UnregisterRequest`, and the router forgets a link whose lease has run out.

Every ten minutes a service rescans the PKI, which the authorities publish
anew once an epoch, and registers with any router listed in it that it has
no link with. A registration that fails, a link whose reader fails, and a
link whose router answers a renewal with `StatusUnknownService` or
`StatusStale` are forgotten, so the next rescan registers with that router
again.

## Advertising and discovery

Once a service holds a link, it advertises its `ServiceDescriptor` in every
directory in the PKI: its public key and the routers it holds links with,
with the expiry it asks for. An `AdvertiseRequest` carries a MAC and a
sequence number, the time in nanoseconds; the directory keeps only the
descriptor with the highest, and only until its lease runs out. A service
advertises again once half of its lease has passed and whenever its links
change, and a `WithdrawRequest` removes the descriptor when the service
stops. The sequence number of a withdrawn or expired descriptor is kept for
a while, so a replayed older advertisement cannot bring it back.

A client finds one service with a `LookupRequest`, asking each directory in
turn and checking that the descriptor it gets is the service's. A
`ListRequest` instead returns the read cap of a *snapshot stream*, where the
directory writes all its descriptors whenever one changes; a client merges
the lists of every directory, so no single directory can hide a service's
routers.

## Dialing a service

A client mints a voucher, seals it to the service's public key, and sends it
to one of the service's routers in a `RouteRequest`. It tries only routers
the PKI lists, five minutes each. The router forwards the sealed voucher
over its link without being able to open it; the service opens it, uses it,
and answers in the voucher reply. The router learns which service is being
contacted and when, but not by whom, since the request travels over Sphinx
with a reply SURB.

A chat app that cannot route vouchers itself can mint one and hand it to
`pigeonhole-voucher send SERVICE_IDENTITY VOUCHER_TOKEN`.

The other direction needs no router or directory: a service mints a voucher
and *offers* it, for a client to use.

## Connections

Each side writes its messages, one per box, to its own stream, and reads the
peer's stream box by box. A message is at most one box. Replicas keep a box
for one to two replica epochs, so a connection rewrites everything it sent
in the last seven days once a replica epoch, and saves its state after every
send and receive: either side can be offline for days, or restart.

## Lifetimes

Nothing a service registers or advertises outlives it by more than a lease,
so a router's table of links and a directory's list of services hold only
services that are around to renew them.

A `RegisterRequest`, a `RenewRequest` and an `AdvertiseRequest` name an
expiry, in Unix seconds. The plugin refuses one at or before its own clock,
or further ahead than the longest lease it grants plus ten minutes of clock
skew, with `StatusInvalidRequest`; it answers with the expiry it granted. So
a request is only ever valid within its own window.

| | Link with a router | Descriptor in a directory |
|---|---|---|
| Longest lease | 7 days | 24 hours |
| A service renews after | half the lease: 3.5 days | half the lease: 12 hours |
| Renewed by | `RenewRequest` | advertising again |
| Ended by | `UnregisterRequest`, or expiry | `WithdrawRequest`, or expiry |
| On expiry | the router stops routing to the link at once and closes it within an hour | lookups answer `StatusUnknownService` and the next snapshot leaves it out |
| Most held | 4096 (`max_links`) | 4096 (`max_entries`) |

A service asks for the longest lease unless configured otherwise, and renews
on its ten-minute rescan. A service that keeps hours asks for less, and
withdraws when it stops: closing a service withdraws it from every
directory, while its links stay for the next start, since a client may be
waiting on a voucher routed meanwhile. A new service beyond a plugin's limit
is refused with `StatusBusy` until a lease runs out.

Every request from a service carries a sequence number that must exceed the
last one the plugin applied, else `StatusStale`; an exact retransmission is
answered `StatusOK` again. After a lease ends or the service withdraws, the
plugin keeps the sequence number until no request made before then could
still be in date: the longest lease plus the clock skew after the last
request it applied. Then it forgets the service entirely, and a replay of
any earlier request is refused for its expiry having passed. So a replay
can never bring a service back, and a plugin holds nothing for a service
that has gone for more than a lease and a week.

## Request authentication

`RegisterRequest`, `RenewRequest`, `UnregisterRequest`, `AdvertiseRequest`
and `WithdrawRequest` carry a MAC that proves the request comes from the holder of the service's private key,
without a challenge round:

```text
ss  = DH(servicePriv, pluginPub) = DH(pluginPriv, servicePub)
key = HKDF-BLAKE2b-256(ss, salt = none, info = "katzenpost-pigeonservice-mac-v1" || pluginPub || servicePub)
mac = BLAKE2b-256(key = key, msg = canonical CBOR of the request with MAC null)
```

`pluginPub` is the router's or the directory's public key from the PKI. An
all-zero shared secret is rejected, and MACs are compared in constant time.

## Messages

Requests are the payloads of Sphinx queries to the plugin's endpoint, and
replies come back in the reply SURB. Every message is canonical CBOR, a map
keyed by the Go field names. A decoder accepts the zero padding Sphinx adds
after the item. The daemon retransmits a request until a reply arrives, so
the router and the directory treat a repeated request as one.

A reply's status says what became of the request:

| Status | Value | Meaning |
|---|---|---|
| `StatusOK` | 0 | applied, or a retransmission of a request already applied |
| `StatusInvalidRequest` | 1 | not exactly one request, a malformed field, or an expiry outside the plugin's window |
| `StatusBadMAC` | 2 | the MAC does not verify for the service's key; for a withdrawal, also a key that is not the descriptor's |
| `StatusUnknownService` | 3 | the plugin holds no live link or descriptor for the service |
| `StatusStale` | 4 | the sequence number does not exceed the last one applied |
| `StatusBusy` | 5 | a limit is reached: registrations being inducted, vouchers waiting on a link, links or descriptors held; or a `ListRequest` before the first snapshot |
| `StatusInternalError` | 6 | the plugin's database failed |

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
const (
	RouterCapability    = "voucher_router"
	DirectoryCapability = "service_directory"
	ParamNIKEScheme     = "nikeScheme"
	ParamPublicKey      = "publicKey"
)

const (
	StatusOK uint8 = iota
	StatusInvalidRequest
	StatusBadMAC
	StatusUnknownService
	StatusStale
	StatusBusy
	StatusInternalError
)

type ServiceID [32]byte

type RouterRef struct {
	NodeIDHash [32]byte
	Endpoint   string
}

type ServiceDescriptor struct {
	NIKEScheme string
	PublicKey  []byte
	Routers    []RouterRef
}

// To a voucher router; exactly one field is set.
type RouterRequest struct {
	Route      *RouteRequest      `cbor:",omitempty"`
	Register   *RegisterRequest   `cbor:",omitempty"`
	Renew      *RenewRequest      `cbor:",omitempty"`
	Unregister *UnregisterRequest `cbor:",omitempty"`
}

type RouteRequest struct {
	ServiceID  ServiceID
	Ciphertext []byte // the voucher, sealed to the service
}

type RegisterRequest struct {
	NIKEScheme string
	PublicKey  []byte
	Voucher    []byte
	Seq        uint64
	Expiry     uint64 // Unix seconds
	MAC        []byte
}

type RenewRequest struct {
	NIKEScheme string
	PublicKey  []byte
	Seq        uint64
	Expiry     uint64
	MAC        []byte
}

type UnregisterRequest struct {
	NIKEScheme string
	PublicKey  []byte
	Seq        uint64
	MAC        []byte
}

type RouterReply struct {
	Status uint8
	Expiry uint64 `cbor:",omitempty"` // the lease granted to a Register or a Renew
}

// One box on the router's stream of a link.
type LinkMessage struct {
	Forward []byte `cbor:",omitempty"` // a client's sealed voucher
}

// To a service directory; exactly one field is set.
type DirectoryRequest struct {
	Advertise *AdvertiseRequest `cbor:",omitempty"`
	Withdraw  *WithdrawRequest  `cbor:",omitempty"`
	Lookup    *LookupRequest    `cbor:",omitempty"`
	List      *ListRequest      `cbor:",omitempty"`
}

type AdvertiseRequest struct {
	Descriptor ServiceDescriptor
	Seq        uint64
	Expiry     uint64 // Unix seconds
	MAC        []byte
}

type WithdrawRequest struct {
	ServiceID ServiceID
	Seq       uint64
	MAC       []byte
}

type LookupRequest struct {
	ServiceID ServiceID
}

type ListRequest struct{}

type DirectoryReply struct {
	Status     uint8
	Expiry     uint64             `cbor:",omitempty"` // the lease granted to an Advertise
	Descriptor *ServiceDescriptor `cbor:",omitempty"` // for Lookup
	ReadCap    []byte             `cbor:",omitempty"` // for List: the snapshot stream
	StartIndex []byte             `cbor:",omitempty"`
}

// A snapshot stream holds a 4-byte big-endian length, then this.
type Snapshot struct {
	Seq         uint64
	Descriptors []ServiceDescriptor
}

// The voucher reply, in the shape of katzenqt's ReplyWho with one member.
type whoReply struct {
	PleaseAdds []pleaseAdd `cbor:"please_adds"`
}

type pleaseAdd struct {
	DisplayName string `cbor:"display_name"`
	ReadCap     []byte `cbor:"read_cap"`
}
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub const ROUTER_CAPABILITY: &str = "voucher_router";
pub const DIRECTORY_CAPABILITY: &str = "service_directory";
pub const PARAM_NIKE_SCHEME: &str = "nikeScheme";
pub const PARAM_PUBLIC_KEY: &str = "publicKey";

#[repr(u8)]
pub enum Status { Ok = 0, InvalidRequest, BadMac, UnknownService, Stale, Busy, InternalError }

pub struct ServiceId(pub [u8; 32]);

pub struct RouterRef {
    pub node_id_hash: [u8; 32],
    pub endpoint: String,
}

pub struct ServiceDescriptor {
    pub nike_scheme: String,
    pub public_key: Vec<u8>,
    pub routers: Vec<RouterRef>,
}

pub enum RouterRequest {
    Route(RouteRequest),
    Register(RegisterRequest),
    Renew(RenewRequest),
    Unregister(UnregisterRequest),
}

pub struct RouteRequest {
    pub service_id: ServiceId,
    pub ciphertext: Vec<u8>, // the voucher, sealed to the service
}

pub struct RegisterRequest {
    pub nike_scheme: String,
    pub public_key: Vec<u8>,
    pub voucher: Vec<u8>,
    pub seq: u64,
    pub expiry: u64, // Unix seconds
    pub mac: Option<Vec<u8>>,
}

pub struct RenewRequest {
    pub nike_scheme: String,
    pub public_key: Vec<u8>,
    pub seq: u64,
    pub expiry: u64,
    pub mac: Option<Vec<u8>>,
}

pub struct UnregisterRequest {
    pub nike_scheme: String,
    pub public_key: Vec<u8>,
    pub seq: u64,
    pub mac: Option<Vec<u8>>,
}

pub struct RouterReply {
    pub status: u8,
    pub expiry: u64, // the lease granted to a Register or a Renew; 0 otherwise
}

pub enum DirectoryRequest {
    Advertise(AdvertiseRequest),
    Withdraw(WithdrawRequest),
    Lookup(ServiceId),
    List,
}

pub struct AdvertiseRequest {
    pub descriptor: ServiceDescriptor,
    pub seq: u64,
    pub expiry: u64, // Unix seconds
    pub mac: Option<Vec<u8>>,
}

pub struct WithdrawRequest {
    pub service_id: ServiceId,
    pub seq: u64,
    pub mac: Option<Vec<u8>>,
}

pub struct DirectoryReply {
    pub status: u8,
    pub expiry: u64,                           // the lease granted to an Advertise
    pub descriptor: Option<ServiceDescriptor>, // for Lookup
    pub read_cap: Vec<u8>,                     // for List: the snapshot stream
    pub start_index: Vec<u8>,
}

pub struct Snapshot {
    pub seq: u64,
    pub descriptors: Vec<ServiceDescriptor>,
}

// The link message and the voucher reply have no type of their own; these
// encode and decode them.
pub fn encode_link_message(forward: &[u8]) -> Vec<u8>;
pub fn decode_link_message(raw: &[u8]) -> Result<Vec<u8>, Error>;
pub(crate) fn encode_who_reply(display_name: &str, read_cap: &[u8]) -> Vec<u8>;
{{< /tab >}}
{{< /tabpane >}}

## Interfaces

### The mixnet

A service reaches the mixnet through one interface, which the thin client
implements and tests replace with an in-memory network.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
type Pigeonhole interface {
	NewStream() (*bacap.WriteCap, *bacap.ReadCap, *bacap.MessageBoxIndex, error)
	Write(ctx context.Context, writeCap *bacap.WriteCap, idx *bacap.MessageBoxIndex, plaintext []byte) (*bacap.MessageBoxIndex, error)
	Read(ctx context.Context, readCap *bacap.ReadCap, idx *bacap.MessageBoxIndex) ([]byte, *bacap.MessageBoxIndex, error)
	Tombstone(ctx context.Context, writeCap *bacap.WriteCap, idx *bacap.MessageBoxIndex) error
	WritePayload(ctx context.Context, writeCap *bacap.WriteCap, idx *bacap.MessageBoxIndex, payload []byte) (*bacap.MessageBoxIndex, error)
	MaxPlaintext() int

	VoucherMint(messageWriteCap []byte, displayName string) (*MintResult, error)
	VoucherInduct(voucher, payload, whoReply []byte) (*InductResult, error)
	VoucherOpen(secretKey, sealedReply, messageWriteCap []byte) (*OpenResult, error)
	VoucherDeriveStream(voucher []byte) (writeCap, readCap []byte, err error)

	BoxSeal(nikeScheme string, publicKey, plaintext []byte) ([]byte, error)

	Request(ctx context.Context, node *[32]byte, endpoint []byte, payload []byte) ([]byte, error)
	Services(capability string) ([]ServiceNode, error)
}

func NewThinPigeonhole(c *thin.ThinClient) Pigeonhole
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
pub trait Backend: Send + Sync + 'static {
    fn new_keypair(&self) -> impl Future<Output = Result<Keypair>> + Send;
    fn write_box(&self, write_cap: &[u8], index: &[u8], plaintext: &[u8]) -> impl Future<Output = Result<()>> + Send;
    fn read_box(&self, read_cap: &[u8], index: &[u8]) -> impl Future<Output = Result<Read>> + Send;
    fn replica_epoch(&self) -> impl Future<Output = Result<u64>> + Send;
    fn max_plaintext(&self) -> impl Future<Output = Result<usize>> + Send;

    fn voucher_mint(&self, write_cap: &[u8], name: &str) -> impl Future<Output = Result<Minted>> + Send;
    fn voucher_derive_stream(&self, voucher: &[u8]) -> impl Future<Output = Result<(Secret, Secret)>> + Send;
    fn voucher_induct(&self, voucher: &[u8], payload: &[u8], who_reply: &[u8]) -> impl Future<Output = Result<Inducted>> + Send;
    fn voucher_open(&self, secret_key: &[u8], sealed_reply: &[u8], write_cap: &[u8]) -> impl Future<Output = Result<Opened>> + Send;

    fn request(&self, node: &[u8; 32], endpoint: &[u8], payload: &[u8]) -> impl Future<Output = Result<Vec<u8>>> + Send;
    fn services(&self, capability: &str) -> impl Future<Output = Result<Vec<ServiceNode>>> + Send;

    fn nike_generate_key_pair(&self, scheme: &str) -> impl Future<Output = Result<(Vec<u8>, Secret)>> + Send;
    fn nike_derive_secret(&self, scheme: &str, private: &[u8], public: &[u8]) -> impl Future<Output = Result<Secret>> + Send;
    fn box_seal(&self, scheme: &str, public: &[u8], plaintext: &[u8]) -> impl Future<Output = Result<Vec<u8>>> + Send;
    fn box_open(&self, scheme: &str, private: &[u8], ciphertext: &[u8]) -> impl Future<Output = Result<Vec<u8>>> + Send;
}

// `daemon` is `@name` for an abstract unix socket, a socket path, or `host:port`.
impl ThinClientBackend {
    pub async fn dial(daemon: &str) -> Result<ThinClientBackend, Box<dyn std::error::Error>>;
}
{{< /tab >}}
{{< /tabpane >}}

### Writing a service

A service runs a handler for each client's session. A session is a
connection, and ends when its handler returns. Closing the service withdraws
it from the directories and keeps its links and sessions on disk for the
next start. The leases it asks for are `Config.LinkTTL` and
`Config.AdvertiseTTL` in Go, `link_ttl` and `advertise_ttl` in Rust, the
longest a plugin grants unless set shorter.

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
func LoadServiceKey(dataDir string) (*ServiceKey, error)
func NewService(cfg Config, ph Pigeonhole) (*Service, error)

func (s *Service) ID() ServiceID
func (s *Service) Descriptor() *ServiceDescriptor
func (s *Service) Run(ctx context.Context, h Handler) error
func (s *Service) Close() error

type Handler interface {
	OnSession(ctx context.Context, s *Session)
}

type Session struct {
	*Conn
	// ...
}

func (c *Conn) Send(ctx context.Context, msg []byte) error
func (c *Conn) Recv(ctx context.Context) ([]byte, error)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
impl<B: Backend> Service<B> {
    pub fn new(cfg: Config, ph: Arc<B>) -> Result<Self, Error>;
    pub fn id(&self) -> ServiceId;
    pub fn descriptor(&self) -> ServiceDescriptor;
    pub async fn run<F, Fut>(&self, handler: F) -> Result<(), Error>
    where
        F: Fn(Session<B>) -> Fut + Send + Sync + 'static,
        Fut: Future<Output = ()> + Send + 'static;
    pub async fn offer(&self) -> Result<Vec<u8>, Error>;
    pub async fn close(&self);
}

// A Session derefs to its Conn.
impl<B: Backend> Conn<B> {
    pub async fn send(&self, msg: &[u8]) -> Result<(), Error>;
    pub async fn recv(&self) -> Result<Vec<u8>, Error>;
}
{{< /tab >}}
{{< /tabpane >}}

### Reaching a service

{{< tabpane >}}
{{< tab header="Go" lang="go" >}}
type Discoverer interface {
	Lookup(ctx context.Context, id ServiceID) (*ServiceDescriptor, error)
	List(ctx context.Context) ([]ServiceDescriptor, error)
}

// Advertise asks for a lease until expiry and returns the one granted.
type Advertiser interface {
	Advertise(ctx context.Context, d *ServiceDescriptor, expiry uint64) (uint64, error)
	Withdraw(ctx context.Context, id ServiceID) error
}

// Package discovery: both, over every directory in the PKI.
func NewAll(ph common.Pigeonhole, key *common.ServiceKey, pollInterval time.Duration) (*All, error)

// Package voucher_router: a service's side of a link.
func Register(ctx context.Context, ph common.Pigeonhole, key *common.ServiceKey, node *common.ServiceNode, pollInterval time.Duration, expiry uint64) (*Conn, error)
func Renew(ctx context.Context, ph common.Pigeonhole, key *common.ServiceKey, node *common.ServiceNode, expiry uint64) error
func Unregister(ctx context.Context, ph common.Pigeonhole, key *common.ServiceKey, node *common.ServiceNode) error

// Package pigeonservice: mints a voucher, routes it to the service and waits for its reply.
func Dial(ctx context.Context, ph common.Pigeonhole, d *common.ServiceDescriptor, displayName string, pollInterval time.Duration) (*voucher_router.Conn, error)
// Package voucher_router: routes a voucher someone else minted.
func Route(ctx context.Context, ph common.Pigeonhole, d *common.ServiceDescriptor, voucher []byte) error
// Uses a voucher a service offered.
func Induct(ctx context.Context, ph common.Pigeonhole, voucher []byte, displayName string, pollInterval time.Duration) (*Conn, error)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// One per directory in the PKI.
impl<B: Backend> Directory<B> {
    pub async fn all(ph: Arc<B>, key: Option<Keypair>, poll: Duration) -> Result<Vec<Self>, Error>;
    pub async fn lookup(&self, id: ServiceId) -> Result<ServiceDescriptor, Error>;
    pub async fn list(&self) -> Result<Vec<ServiceDescriptor>, Error>;
    /// Asks for a lease until `expiry` and returns the one granted.
    pub async fn advertise(&self, d: &ServiceDescriptor, expiry: u64) -> Result<u64, Error>;
    pub async fn withdraw(&self, id: ServiceId) -> Result<(), Error>;
}

/// A service's side of a link with the router at `node`.
pub async fn register<B: Backend>(ph: &B, key: &Keypair, node: &ServiceNode, expiry: u64) -> Result<Pending, Error>;
pub async fn renew<B: Backend>(ph: &B, key: &Keypair, node: &ServiceNode, expiry: u64) -> Result<(), Error>;
pub async fn unregister<B: Backend>(ph: &B, key: &Keypair, node: &ServiceNode) -> Result<(), Error>;

/// Mints a voucher, routes it to the service and waits for its reply.
pub async fn dial<B: Backend>(ph: Arc<B>, d: &ServiceDescriptor, display_name: &str, poll: Duration) -> Result<Conn<B>, Error>;
/// Routes a voucher someone else minted.
pub async fn route<B: Backend>(ph: &B, d: &ServiceDescriptor, voucher: &[u8]) -> Result<(), Error>;
/// Uses a voucher a service offered.
pub async fn induct<B: Backend>(ph: Arc<B>, voucher: &[u8], display_name: &str, poll: Duration) -> Result<Conn<B>, Error>;
{{< /tab >}}
{{< /tabpane >}}

## Programs

| Program | Where | What it does |
|---|---|---|
| `voucher-router` | katzenpost `cmd/voucher-router` | the voucher router plugin |
| `service-directory` | katzenpost `cmd/service-directory` | the service directory plugin |
| `pigeonhole-voucher` | pigeonhole_protocols `go/cmd/pigeonhole-voucher` | `list` the services; `send` a service a voucher |
| `pigeonhole-echo` | pigeonhole_protocols `go/cmd/pigeonhole-echo` | a service that sends back each message |
| `eliza` | pigeonhole_protocols `rust/src/bin/eliza.rs` | ELIZA, in katzenqt's chat framing |
| `zulip-bridge` | pigeonhole_protocols `rust/src/bin/zulip_bridge.rs` | bridges a group chat with a Zulip stream; invites whoever sends it a voucher code |
| `motd-service` | pigeonhole_protocols `go/cmd/motd-service` | a Go service that answers each request with the message of the day, read from a file |
| `motd` | pigeonhole_protocols `go/cmd/motd` | fetches the message of the day from a `motd-service` |

### Talking to ELIZA

ELIZA can be dialed from any of our chat clients:
[katzenqt](https://github.com/katzenpost/katzenqt),
[jam](https://github.com/katzenpost/jam),
[frank_chat](https://github.com/katzenpost/frank_chat) or
[hushphone](https://github.com/katzenpost/hushphone). Generate a voucher in
the client, find ELIZA's service identity among the services
`pigeonhole-voucher list` shows, and send ELIZA the voucher token:

```sh
pigeonhole-voucher --thin_config thinclient.toml list
pigeonhole-voucher --thin_config thinclient.toml send SERVICE_IDENTITY VOUCHER_TOKEN
```

ELIZA inducts you into a new chat, opens it with a greeting, and answers
each message you send.

### Running the router and the directory

The voucher router and the service directory run on a service node: a
special kind of mix node in a Katzenpost mix network that delivers Sphinx
packet payloads to services and sends their answers back in SURB replies.
The node runs each service as a plugin, beside others such as the courier.
An operator adds the two plugins to the `[ServiceNode]` section of the
node's configuration:

```toml
[[ServiceNode.CBORPluginKaetzchen]]
  Capability = "voucher_router"
  Endpoint = "voucher_router"
  Command = "/usr/local/bin/voucher-router"
  MaxConcurrency = 1
  [ServiceNode.CBORPluginKaetzchen.Config]
    data_dir = "/var/lib/katzenpost-servicenode/voucher_router"
    log_dir = "/var/log/katzenpost/voucher_router"
    thin_config = "/etc/katzenpost-servicenode/pigeonservice-thinclient.toml"

[[ServiceNode.CBORPluginKaetzchen]]
  Capability = "service_directory"
  Endpoint = "service_directory"
  Command = "/usr/local/bin/service-directory"
  MaxConcurrency = 1
  [ServiceNode.CBORPluginKaetzchen.Config]
    data_dir = "/var/lib/katzenpost-servicenode/service_directory"
    log_dir = "/var/log/katzenpost/service_directory"
    thin_config = "/etc/katzenpost-servicenode/pigeonservice-thinclient.toml"
```

`Capability` is the name the plugin is listed under in the PKI document, and
`Endpoint` the name a client addresses its requests to. Each plugin has its
own data directory, for its key and database, and its own log directory.
Because the router and the directory also read and write Pigeonhole streams,
each reaches the mixnet through a client daemon, kpclientd, named by its
thin client configuration. On first start a plugin generates its NIKE
keypair, and the node publishes the public key in the PKI document.
`max_links` and `max_entries` bound the services a router and a directory
hold, 4096 each by default.
