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
  `cmd/service-directory`, built on the `pigeonservice/directory` package.
  Operators run it as a plugin on a service node.
- The **voucher router** (capability `voucher_router`) relays a client's
  first message to a pigeonhole service. It is the `voucher-router` program
  in [katzenpost](https://github.com/katzenpost/katzenpost), under
  `cmd/voucher-router`, built on the `pigeonservice/router` package.
  Operators run it as a plugin on a service node.
- The **pigeonhole service library** is for writing pigeonhole services, and
  the clients that reach them, in Go or Rust. A pigeonhole service is the
  responder side of an initiator–responder protocol over Pigeonhole: it
  accepts new connections from clients and then speaks its own protocol over
  each one, such as a bot that joins group chats, or a binary protocol no
  human reads. The Go library is the `pigeonservice` package in
  [katzenpost](https://github.com/katzenpost/katzenpost); the Rust library
  is the `services` module of the `pigeonhole_protocols` crate in
  [pigeonhole_protocols](https://github.com/katzenpost/pigeonhole_protocols),
  which also has ELIZA, a pigeonhole service written with it. The two speak
  the same wire format.

| Part | Where | Status |
|---|---|---|
| This specification | website [#246](https://github.com/katzenpost/website/pull/246) | in review |
| Service directory | katzenpost `cmd/service-directory` [#1247](https://github.com/katzenpost/katzenpost/pull/1247) | in review |
| Voucher router | katzenpost `cmd/voucher-router` [#1247](https://github.com/katzenpost/katzenpost/pull/1247) | in review |
| Go library | katzenpost `pigeonservice` [#1247](https://github.com/katzenpost/katzenpost/pull/1247) | in review |
| Rust library | pigeonhole_protocols `src/services` [#11](https://github.com/katzenpost/pigeonhole_protocols/pull/11) | in review |
| ELIZA | pigeonhole_protocols `src/bin/eliza.rs` [#11](https://github.com/katzenpost/pigeonhole_protocols/pull/11) | in review |
| Rust thin client | thin_client [#100](https://github.com/katzenpost/thin_client/pull/100) | in review |

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
a `RegisterRequest`, with its public key and a MAC. The router uses the
voucher, and the connection that results is the service's *link* with that
router. The router writes every sealed voucher addressed to the service to
the link as a `LinkMessage`, and keeps them for seven days, so a service
that was offline still receives them.

The authorities publish a new PKI document once an epoch, and the client
daemon tells its thin clients about each one. On each new document a service
registers with any router listed in it that it has no link with. A
registration that fails, and a link whose reader fails, are forgotten, so
the next document registers with that router again.

## Advertising and discovery

Once a service holds a link, it advertises its `ServiceDescriptor` in every
directory in the PKI: its public key and the routers it holds links with. An
`AdvertiseRequest` carries a MAC and a sequence number, the time in
nanoseconds; the directory keeps only the descriptor with the highest. A
`WithdrawRequest` removes it, and its sequence number stays, so a replayed
older advertisement cannot bring it back.

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
and *offers* it, for a client to use. ELIZA keeps three on offer in
`data_dir/vouchers/`, as the base64 text a katzenqt user pastes into "Induct
via voucher".

## Connections

Each side writes its messages, one per box, to its own stream, and reads the
peer's stream box by box. A message is at most one box. Replicas keep a box
for one to two replica epochs, so a connection rewrites everything it sent
in the last seven days once a replica epoch, and saves its state after every
send and receive: either side can be offline for days, or restart.

## Request authentication

`RegisterRequest`, `AdvertiseRequest` and `WithdrawRequest` carry a MAC that
proves the request comes from the holder of the service's private key,
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
	Route    *RouteRequest    `cbor:",omitempty"`
	Register *RegisterRequest `cbor:",omitempty"`
}

type RouteRequest struct {
	ServiceID  ServiceID
	Ciphertext []byte // the voucher, sealed to the service
}

type RegisterRequest struct {
	NIKEScheme string
	PublicKey  []byte
	Voucher    []byte
	MAC        []byte
}

type RouterReply struct {
	Status uint8
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
}

pub struct RouteRequest {
    pub service_id: ServiceId,
    pub ciphertext: Vec<u8>, // the voucher, sealed to the service
}

pub struct RegisterRequest {
    pub nike_scheme: String,
    pub public_key: Vec<u8>,
    pub voucher: Vec<u8>,
    pub mac: Option<Vec<u8>>,
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
    pub mac: Option<Vec<u8>>,
}

pub struct WithdrawRequest {
    pub service_id: ServiceId,
    pub seq: u64,
    pub mac: Option<Vec<u8>>,
}

pub struct DirectoryReply {
    pub status: u8,
    pub descriptor: Option<ServiceDescriptor>, // for Lookup
    pub read_cap: Vec<u8>,                     // for List: the snapshot stream
    pub start_index: Vec<u8>,
}

pub struct Snapshot {
    pub seq: u64,
    pub descriptors: Vec<ServiceDescriptor>,
}

// The router reply, the link message and the voucher reply have no type of
// their own; these encode and decode them.
pub fn encode_router_reply(status: Status) -> Vec<u8>;
pub fn decode_status(raw: &[u8]) -> Result<u8, Error>;
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
connection, and ends when its handler returns. Closing the service keeps
its sessions on disk for the next start.

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

type Advertiser interface {
	Advertise(ctx context.Context, d *ServiceDescriptor) error
	Withdraw(ctx context.Context, id ServiceID) error
}

// Package directory: both, over every directory in the PKI.
func NewAll(ph ps.Pigeonhole, key *ps.ServiceKey, pollInterval time.Duration) (*All, error)

// Mints a voucher, routes it to the service and waits for its reply.
func Dial(ctx context.Context, ph Pigeonhole, d *ServiceDescriptor, displayName string, pollInterval time.Duration) (*Conn, error)
// Routes a voucher someone else minted.
func Route(ctx context.Context, ph Pigeonhole, d *ServiceDescriptor, voucher []byte) error
// Uses a voucher a service offered.
func Induct(ctx context.Context, ph Pigeonhole, voucher []byte, displayName string, pollInterval time.Duration) (*Conn, error)
{{< /tab >}}
{{< tab header="Rust" lang="rust" >}}
// One per directory in the PKI.
impl<B: Backend> Directory<B> {
    pub async fn all(ph: Arc<B>, key: Option<Keypair>, poll: Duration) -> Result<Vec<Self>, Error>;
    pub async fn lookup(&self, id: ServiceId) -> Result<ServiceDescriptor, Error>;
    pub async fn list(&self) -> Result<Vec<ServiceDescriptor>, Error>;
    pub async fn advertise(&self, d: &ServiceDescriptor) -> Result<(), Error>;
    pub async fn withdraw(&self, id: ServiceId) -> Result<(), Error>;
}

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
| `pigeonhole-voucher` | katzenpost `cmd/pigeonhole-voucher` | `list` the services; `send` a service a voucher |
| `pigeonhole-echo` | katzenpost `cmd/pigeonhole-echo` | a service that sends back each message |
| `eliza` | pigeonhole_protocols `src/bin/eliza.rs` | ELIZA, in katzenqt's chat framing |

The plugins run on a service node beside the courier. Each has its own data
directory and log directory, and reaches the mixnet through a kpclientd
named by its thin client config:

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
