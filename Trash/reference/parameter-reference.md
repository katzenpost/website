---
title: "Admin Guide"
linkTitle: "Admin Guide"
draft: false
slug: "/admin_guide/"
type: "pages"
---

<html xmlns:ng="http://docbook.org/docbook-ng"><head>
      <meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
   <title>Katzenpost administrator's guide</title><meta name="generator" content="DocBook XSL Stylesheets V1.79.2"></head><body bgcolor="white" text="black" link="#0000FF" vlink="#840084" alink="#0000FF"><div class="book"><div class="titlepage"><div><div><h1 class="title"><a name="d6e1"></a>Katzenpost administrator's guide</h1></div></div><hr></div><div class="toc"><p><b>Table of Contents</b></p><dl class="toc"><dt><span class="preface"><a href="#introduction">Introduction</a></span></dt><dt><span class="chapter"><a href="#components">1. Components and configuration of the Katzenpost mixnet</a></span></dt><dd><dl><dt><span class="section"><a href="#overview">Understanding the Katzenpost components</a></span></dt><dd><dl><dt><span class="section"><a href="#intro-dirauth">Directory authorities (dirauths)</a></span></dt><dt><span class="section"><a href="#intro-mix">Mix nodes</a></span></dt><dt><span class="section"><a href="#intro-gateway">Gateway nodes</a></span></dt><dt><span class="section"><a href="#intro-service">Service nodes</a></span></dt><dt><span class="section"><a href="#intro-client">Clients</a></span></dt></dl></dd><dt><span class="section"><a href="#configuration">Configuring Katzenpost</a></span></dt><dd><dl><dt><span class="section"><a href="#auth-config">Configuring directory authorities</a></span></dt><dt><span class="section"><a href="#mix-config">Configuring mix nodes</a></span></dt><dt><span class="section"><a href="#gateway-config">Configuring gateway nodes</a></span></dt><dt><span class="section"><a href="#service-config">Configuring service nodes</a></span></dt></dl></dd></dl></dd><dt><span class="chapter"><a href="#container">2. Using the Katzenpost Docker test network</a></span></dt><dd><dl><dt><span class="section"><a href="#requirements">Requirements</a></span></dt><dt><span class="section"><a href="#install_kp">Preparing to run the container image</a></span></dt><dt><span class="section"><a href="#basic-ops">Operating the test mixnet</a></span></dt><dd><dl><dt><span class="section"><a href="#start-mixnet">Starting and monitoring the mixnet</a></span></dt><dt><span class="section"><a href="#test-mixnet">Testing the mixnet</a></span></dt><dt><span class="section"><a href="#shutdown-mixnet">Shutting down the mixnet</a></span></dt><dt><span class="section"><a href="#uninstall-mixnet">Uninstalling and cleaning up</a></span></dt></dl></dd><dt><span class="section"><a href="#topology">Network topology and components</a></span></dt><dd><dl><dt><span class="section"><a href="#d6e2648">The Docker file tree</a></span></dt></dl></dd><dt><span class="section"><a href="#d6e2654"></a></span></dt></dl></dd><dt><span class="chapter"><a href="#docker-config">3. Appendix: Configuration files from the Docker test mixnet </a></span></dt><dd><dl><dt><span class="section"><a href="#dirauth-config">Directory authority</a></span></dt><dt><span class="section"><a href="#mix-node-config">Mix node</a></span></dt><dt><span class="section"><a href="#gateway-node-config">Gateway node</a></span></dt><dt><span class="section"><a href="#service-node-config">Service node</a></span></dt></dl></dd><dt><span class="chapter"><a href="#gensphinx">4. Appendix: Using <span class="emphasis"><em>gensphinx</em></span></a></span></dt></dl></div><div class="list-of-figures"><p><b>List of Figures</b></p><dl><dt>1.1. <a href="#d6e28">The pictured element types correspond to discrete client and server programs that
                Katzenpost requires to function. </a></dt><dt>2.1. <a href="#d6e2552">Test network topology</a></dt></dl></div><div class="list-of-tables"><p><b>List of Tables</b></p><dl><dt>1.1. <a href="#d6e72">Katzenpost clients</a></dt><dt>1.2. <a href="#d6e143"><span class="bold">Directory authority (dirauth) configuration
                        sections</span></a></dt><dt>1.3. <a href="#d6e657">Mix node configuration sections</a></dt><dt>1.4. <a href="#d6e1133">Gateway node configuration sections</a></dt><dt>1.5. <a href="#d6e1621">Mix node configuration sections</a></dt><dt>2.1. <a href="#d6e2353">Table 1: Makefile targets</a></dt><dt>2.2. <a href="#d6e2574">Table 2: Test mixnet hosts</a></dt></dl></div> 
    
   <div class="preface"><div class="titlepage"><div><div><h1 class="title"><a name="introduction"></a>Introduction</h1></div></div></div>
       
       <p>To Do</p>
   </div>
      
    <div class="chapter"><div class="titlepage"><div><div><h1 class="title"><a name="components"></a>Chapter&nbsp;1.&nbsp;Components and configuration of the Katzenpost mixnet</h1></div></div></div><div class="toc"><p><b>Table of Contents</b></p><dl class="toc"><dt><span class="section"><a href="#overview">Understanding the Katzenpost components</a></span></dt><dd><dl><dt><span class="section"><a href="#intro-dirauth">Directory authorities (dirauths)</a></span></dt><dt><span class="section"><a href="#intro-mix">Mix nodes</a></span></dt><dt><span class="section"><a href="#intro-gateway">Gateway nodes</a></span></dt><dt><span class="section"><a href="#intro-service">Service nodes</a></span></dt><dt><span class="section"><a href="#intro-client">Clients</a></span></dt></dl></dd><dt><span class="section"><a href="#configuration">Configuring Katzenpost</a></span></dt><dd><dl><dt><span class="section"><a href="#auth-config">Configuring directory authorities</a></span></dt><dt><span class="section"><a href="#mix-config">Configuring mix nodes</a></span></dt><dt><span class="section"><a href="#gateway-config">Configuring gateway nodes</a></span></dt><dt><span class="section"><a href="#service-config">Configuring service nodes</a></span></dt></dl></dd></dl></div>
    
    <p>This section of the Katzenpost technical documentation provides an introduction to the
        software components that make up Katzenpost and guidance on how to configure each
        component.  The intended reader is a system administrator who wants to implement a working,
        production Katzenpost network. </p>
    <p>For information about the theory and design of this software, see <a class="xref" href="#introduction" title="Introduction">Introduction</a>. For a quickly deployable,
        non-production test network (primarily for use by developers), see <a class="xref" href="#container" title="Chapter&nbsp;2.&nbsp;Using the Katzenpost Docker test network">Using the Katzenpost Docker test network</a>.</p>    
    <div class="section"><div class="titlepage"><div><div><h2 class="title" style="clear: both"><a name="overview"></a>Understanding the Katzenpost components</h2></div></div></div>
        
        <p>The core of Katzenpost consists of two program executables, <a class="link" href="#">dirauth</a> and <a class="link" href="#">server</a>.
            Running the <span class="command"><strong>dirauth </strong></span>commmand runs a <span class="emphasis"><em>directory
                authority</em></span> node, or <span class="emphasis"><em>dirauth</em></span>, that functions as part
            of the mixnet's public-key infrastructure (PKI). Running the <span class="command"><strong>server</strong></span>
            runs either a <span class="emphasis"><em>mix</em></span> node, a <span class="emphasis"><em>gateway</em></span> node, or a
                <span class="emphasis"><em>service</em></span> node, depending on the configuration. Configuration
            settings are provided in an associated <code class="filename">katzenpost-authority.toml</code> or
                <code class="filename">katzenpost.toml</code> file respectively. </p>
        <p>In addition to the server components, Katzenpost also supports connections to
            client applications hosted externally to the mix network and communicating with it
            through gateway nodes. </p>
        <p>A model mix network is shown in Figure 1.</p>
        <div class="figure"><a name="d6e28"></a><p class="title"><b>Figure&nbsp;1.1.&nbsp;The pictured element types correspond to discrete client and server programs that
                Katzenpost requires to function. </b></p><div class="figure-contents">
            
            <div class="mediaobject"><img src="/admin_guide/pix/components-production.png" width="405" alt="The pictured element types correspond to discrete client and server programs that Katzenpost requires to function."></div>
        </div></div><br class="figure-break">
        <p>The mix network contains an <span class="emphasis"><em>n</em></span>-layer topology of mix-nodes, with
            three nodes per layer in this example. Sphinx packets traverse the network in one
            direction only. The gateway nodes allow clients to interact with the mix network. The
            service nodes provide mix network services that mix network clients can interact with.
            All messages sent by clients are handed to a <span class="emphasis"><em>connector</em></span> daemon
            hosted on the client system, passed across the Internet to a gateway, and then relayed
            to a service node by way of the nine mix nodes. The service node sends its reply back
            across the mix-node layers to a gateway, which transmits it across the Internet to be
            received by the targeted client. The mix, gateway, and service nodes send <span class="emphasis"><em>mix
                descriptors</em></span> to the dirauths and retrieve a <span class="emphasis"><em>consensus
                document</em></span> from them, described below.</p>
        <p>In addition to the server components, Katzenpost supports connections to client
            applications hosted externally to the mix network and communicating with it through
            gateway nodes and, in some cases, a client connector.</p>
        <div class="section"><div class="titlepage"><div><div><h3 class="title"><a name="intro-dirauth"></a>Directory authorities (dirauths)</h3></div></div></div>
            
            <p>Dirauths compose the decentralized public key infrastructure (PKI) that serves as
                the root of security for the entire mix network. Clients, mix nodes, gateways nodes,
                and service nodes rely on the PKI/dirauth system to maintain and sign an up-to-date
                consensus document, providing a view of the network including connection information
                and public cryptographic key materials and signatures.</p>
            <p>Every 20 minutes (the current value for an <span class="emphasis"><em>epoch</em></span>), each mix,
                gateway, and service node signs a mix descriptor and uploads it to the dirauths. The
                dirauths then vote on a new consensus document. If consensus is reached, each
                dirauth signs the document. Clients and nodes download the document as needed and
                verify the signatures. Consensus fails when 1/2 + 1 nodes fail, which yields greater
                fault tolerance than, for example, Byzantine Fault Tolerance, which fails when 1/3 +
                1 of the nodes fail.</p>
            <p>The PKI signature scheme is fully configurable by the dirauths. Our recommendation
                is to use a hybrid signature scheme consisting of classical Ed25519 and the
                post-quantum, stateless, hash-based signature scheme known as Sphincs+ (with the
                parameters: "sphincs-shake-256f"), which is designated in Katzenpost
                configurations as "Ed25519 Sphincs+". Examples are provided below.</p>
        </div>
        <div class="section"><div class="titlepage"><div><div><h3 class="title"><a name="intro-mix"></a>Mix nodes</h3></div></div></div>
            
            <p>The mix node is the fundamental building block of the mix network. </p>
            <p>Katzenpost mix nodes are arranged in a layered topology to achieve the best
                levels of anonymity and ease of analysis while being flexible enough to scale with
                traffic demands. </p>
        </div>
        <div class="section"><div class="titlepage"><div><div><h3 class="title"><a name="intro-gateway"></a>Gateway nodes</h3></div></div></div>
            
            <p>Gateway nodes provide external client access to the mix network. Because gateways
                are uniquely positioned to identify clients, they are designed to have as little
                information about client behavior as possible. Gateways are randomly selected and
                have no persistent relationship with clients and no knowledge of whether a client's
                packets are decoys or not. When client traffic through a gateway is slow, the node
                additionally generates decoy traffic. </p>
        </div>
        <div class="section"><div class="titlepage"><div><div><h3 class="title"><a name="intro-service"></a>Service nodes</h3></div></div></div>
            
            <p>Service
                nodes provide functionality requested by clients. They are
                logically positioned at the deepest point of the mix network, with incoming queries
                and outgoing replies both needing to traverse all <span class="emphasis"><em>n</em></span> layers of
                mix nodes. A service node's functionality may involve storing messages, publishing
                information outside of the mixnet, interfacing with a blockchain node, and so on.
                Service nodes also process decoy packets. </p>
        </div>
        <div class="section"><div class="titlepage"><div><div><h3 class="title"><a name="intro-client"></a>Clients</h3></div></div></div>
            
            <p>Client applications should be designed so that the following conditions are
                met:</p>
            <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                    <p>Separate service requests from a client are unlinkable. Repeating the same
                        request may be lead to linkability. </p>
                </li><li class="listitem">
                    <p>Service nodes and clients have no persistent relationship.</p>
                </li><li class="listitem">
                    <p>Cleints generate a stream of packets addressed to random or pseudorandom
                        services regardless of whether a real service request is being made. Most of
                        these packets will be decoy traffic.</p>
                </li><li class="listitem">
                    <p>Traffic from a client to a service node must be correctly coupled with
                        decoy traffic. This can mean that the service node is chosen independently
                        from traffic history, or that the transmitted packet replaces a decoy packet
                        that was meant to go to the desired service.</p>
                </li></ul></div>
            <p>Katzenpost currently includes several client applications. All applications
                make extensive use of Sphinx single-use reply blocks (SURBs), which enable service
                nodes to send replies without knowing the location of the client. Newer clients
                require a connection through the client <span class="emphasis"><em>connector</em></span>, which
                provides multiplexing and privilege separation with a consequent reduction in
                processing overhead. These clients also implement the Pigeonhole storage and BACAP
                protocols detailed in <span class="bold"><strong>Place-holder for research paper link</strong></span>. </p>
            <p>The following client applications are available.</p><div class="table"><a name="d6e72"></a><p class="title"><b>Table&nbsp;1.1.&nbsp;Katzenpost clients</b></p><div class="table-contents">
                    
                    <table class="table" summary="Katzenpost clients" border="1"><colgroup><col class="c1"><col class="newCol2"><col class="c2"><col class="c3"></colgroup><thead><tr><th>
                                    <p>Name</p>
                                </th><th>
                                    <p>Needs connector</p>
                                </th><th>
                                    <p>Description</p>
                                </th><th>
                                    <p>Code</p>
                                </th></tr></thead><tbody><tr><td>
                                    <p><span class="bold"><strong>Ping</strong></span></p>
                                </td><td>
                                    <p>no</p>
                                </td><td>
                                    <p>The mix network equivalent of an ICMP ping utility, used
                                        for network testing.</p>
                                </td><td>
                                    <p>GitHub: <a class="ulink" href="https://github.com/katzenpost/katzenpost/tree/main/ping" target="_top">ping</a></p>
                                </td></tr><tr><td>
                                    <p><span class="bold"><strong>Katzen</strong></span></p>
                                </td><td>
                                    <p>no</p>
                                </td><td>
                                    <p>A text chat client with file-transfer support.</p>
                                </td><td>
                                    <p>GitHub: <a class="ulink" href="https://github.com/katzenpost/katzen" target="_top">katzen</a></p>
                                </td></tr><tr><td>
                                    <p><span class="bold"><strong>Status</strong></span></p>
                                </td><td>
                                    <p>yes</p>
                                </td><td>
                                    <p>An HTML page containing status information about the mix
                                        network.</p>
                                </td><td>
                                    <p>GitHub: <a class="ulink" href="https://github.com/katzenpost/status" target="_top">status</a></p>
                                </td></tr><tr><td>
                                    <p><span class="bold"><strong>Worldmap</strong></span></p>
                                </td><td>yes</td><td>
                                    <p>An HTML page with a world map showing geographic locations
                                        of mix network nodes. </p>
                                </td><td>
                                    <p>GitHub: <a class="ulink" href="https://github.com/katzenpost/worldmap" target="_top">worldmap</a></p>
                                </td></tr></tbody></table>
                </div></div><p><br class="table-break"></p>
        </div>
    </div>
    <div class="section"><div class="titlepage"><div><div><h2 class="title" style="clear: both"><a name="configuration"></a>Configuring Katzenpost</h2></div></div></div>
        
 
        
        <p>This section documents the configuration parameters for each type of Katzenpost
            server node. Each node has its own configuration file in <a class="ulink" href="https://toml.io/en/v1.0.0" target="_top">TOML</a> format. </p>

        <div class="section"><div class="titlepage"><div><div><h3 class="title"><a name="auth-config"></a>Configuring directory authorities</h3></div></div></div>
            
            <p>The following configuration is drawn from the reference implementation in
                    <code class="filename">katzenpost/docker/dirauth_mixnet/auth1/authority.toml</code>. In a
                real-world mixnet, the component hosts would not be sharing a single IP address. For
                more information about the test mixnet, see <span class="bold"><strong><a class="xref" href="#container" title="Chapter&nbsp;2.&nbsp;Using the Katzenpost Docker test network">Using the Katzenpost Docker test network</a></strong></span>.</p>
            <div class="table"><a name="d6e143"></a><p class="title"><b>Table&nbsp;1.2.&nbsp;<span class="bold">Directory authority (dirauth) configuration
                        sections</span></b></p><div class="table-contents">
                
                <table class="table" summary="Directory authority (dirauth) configuration&#xA;                        sections" border="1"><colgroup><col class="c1"></colgroup><tbody><tr><td>            
                                <p><a class="xref" href="#auth-server-section-config" title="Dirauth: Server section">Dirauth: Server section</a></p>
                            </td></tr><tr><td>
                                <p><a class="xref" href="#auth-authorities-section-config" title="Dirauth: Authorities section">Dirauth: <code class="code">Authorities</code>
                    section</a></p>
                            </td></tr><tr><td>
                                <p><a class="xref" href="#auth-logging" title="Dirauth: Logging section">Dirauth: Logging section</a></p>
                            </td></tr><tr><td>
                                <p><a class="xref" href="#auth-parameters" title="Dirauth: Parameters section">Dirauth: Parameters section</a></p>
                            </td></tr><tr><td>
                                <p><a class="xref" href="#auth-debug" title="Dirauth: Debug section">Dirauth: Debug section</a></p>
                            </td></tr><tr><td>
                                <p><a class="xref" href="#auth-mixes-section-config" title="Dirauth: Mixes sections">Dirauth: Mixes
                    sections</a></p>
                            </td></tr><tr><td>
                                <p><a class="xref" href="#auth-gatewaynodes-section-config" title="Dirauth: GatewayNodes section">Dirauth:
                        GatewayNodes section</a></p>
                            </td></tr><tr><td>
                                <p><a class="xref" href="#auth-servicenodes-section-config" title="Dirauth: ServiceNodes sections">Dirauth:
                        ServiceNodes sections</a></p>
                            </td></tr><tr><td>
                                <p><a class="xref" href="#auth-topology" title="Dirauth: Topology section">Dirauth: Topology section</a></p>
                            </td></tr><tr><td>
                                <p><a class="xref" href="#auth-sphinx-config" title="Dirauth: SphinxGeometry section">Dirauth: SphinxGeometry
                    section</a></p>
                            </td></tr></tbody></table>
            </div></div><br class="table-break">
            

            
            
            

            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="auth-server-section-config"></a>Dirauth: Server section</h4></div></div></div>
                
                <p>The <code class="code">Server</code> section configures mandatory basic parameters for each
                    directory authority.</p>
                <pre class="programlisting">[Server]
    Identifier = "auth1"
    WireKEMScheme = "xwing"
    PKISignatureScheme = "Ed25519 Sphincs+"
    Addresses = ["tcp://127.0.0.1:30001"]
    DataDir = "/dirauth_mixnet/auth1"</pre>
                <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                        <p><span class="bold"><strong>Identifier</strong></span></p>
                        <p>Specifies the human-readable identifier for a node, and must be unique
                            per mixnet. The identifier can be an FQDN but does not have to
                            be.</p>
                        <p>Type: string</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>WireKEMScheme</strong></span></p>
                        <p>Specifies the key encapsulation mechanism (KEM) scheme
                            for the <a class="ulink" href="https://eprint.iacr.org/2022/539" target="_top">PQ
                                Noise</a>-based wire protocol (link layer) that nodes use
                            to communicate with each other. PQ Noise is a post-quantum variation of
                            the <a class="ulink" href="https://noiseprotocol.org/" target="_top">Noise protocol
                                framework</a>, which algebraically transforms ECDH handshake
                            patterns into KEM encapsulate/decapsulate operations.</p>
                            
                            <p>This configuration option supports the optional use of
                            hybrid post-quantum cryptography to strengthen security. The following KEM
                            schemes are supported: </p><div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: circle; "><li class="listitem">
                                    <p><span class="bold"><strong>Classical:</strong></span> "x25519", "x448"</p>
                                    <div class="note" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Note"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Note]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/note.png"></td><th align="left">Note</th></tr><tr><td align="left" valign="top">
                                        <p>X25519 and X448 are actually non-interactive key-exchanges
                                            (NIKEs), not KEMs. Katzenpost uses
                                            a hashed ElGamal cryptographic construction
                                            to convert them from NIKEs to KEMs.</p>
                                    </td></tr></table></div>
                                </li><li class="listitem">
                                    <p><span class="bold"><strong>Hybrid post-quantum:</strong></span>
                                        "mlkem768", "sntrup4591761", "frodo640shake",
                                        "mceliece348864", "mceliece348864f", "mceliece460896",
                                        "mceliece460896f", "mceliece6688128", "mceliece6688128f",
                                        "mceliece6960119", "mceliece6960119f", "mceliece8192128",
                                        "mceliece8192128f", "xwing", "Kyber768-X25519",
                                        "MLKEM768-X25519", "MLKEM768-X448", "CTIDH511", "CTIDH512",
                                        "CTIDH1024", "CTIDH2048", "CTIDH512-X25519",
                                        "CTIDH512-X25519"</p>
                                </li></ul></div>						
                        <p>Type: string</p>
                        <p>Required: Yes</p>                    
                    </li><li class="listitem">
                        <p><span class="bold"><strong>PKISignatureScheme</strong></span></p>
                        <p>Specifies the cryptographic signature scheme which will be used by all
                            components of the mix network when interacting with the PKI system. Mix
                            nodes sign their descriptors using this signature scheme, and dirauth
                            nodes similarly sign PKI documents using the same scheme.</p>
                        <p>The following signature schemes are supported: "ed25519", "ed448",
                            "Ed25519 Sphincs+", "Ed448-Sphincs+", "Ed25519-Dilithium2",
                            "Ed448-Dilithium3" </p>
                        <p>Type: string</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>Addresses</strong></span></p>
                        <p>Specifies a list of one or more address URLs in a format that contains
                            the transport protocol, IP address, and port number that the node will
                            bind to for incoming connections. Katzenpost supports URLs with that
                            start with either "tcp://" or "quic://" such as:
                            ["tcp://192.168.1.1:30001"] and ["quic://192.168.1.1:40001"].</p>
                        <p>Type: []string</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>DataDir</strong></span></p>
                        <p>Specifies the absolute path to a node's state directory. This is
                                where<code class="filename"> persistence.db</code> is written to disk and
                            where a node stores its cryptographic key materials when started with
                            the "-g" command-line option.</p>
                        <p>Type: string</p>
                        <p>Required: Yes</p>
                    </li></ul></div>
                <p></p>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="auth-authorities-section-config"></a>Dirauth: <code class="code">Authorities</code>
                    section</h4></div></div></div>
                
                <p>An <code class="code">Authorities</code> section is configured for each peer authority. We
                    recommend using <a class="ulink" href="https://quickref.me/toml.html" target="_top">TOML's style</a>
                    for multi-line quotations for key materials.</p>
                <pre class="programlisting">[[Authorities]]
    Identifier = "auth1"
    IdentityPublicKey = """
-----BEGIN ED25519 PUBLIC KEY-----
dYpXpbozjFfqhR45ZC2q97SOOsXMANdHaEdXrP42CJk=
-----END ED25519 PUBLIC KEY-----
"""
    PKISignatureScheme = "Ed25519"
    LinkPublicKey = """
-----BEGIN XWING PUBLIC KEY-----
ooQBPYNdmfwnxXmvnljPA2mG5gWgurfHhbY87DMRY2tbMeZpinJ5BlSiIecprnmm
QqxcS9o36IS62SVMlOUkw+XEZGVvc9wJqHpgEgVJRAs1PCR8cUAdM6QIYLWt/lkf
SPKDCtZ3GiSIOzMuaglo2tarIPEv1AY7r9B0xXOgSKMkGyBkCfw1VBZf46MM26NL
...
gHtNyQJnXski52O03JpZRIhR40pFOhAAcMMAZDpMTVoxlcdR6WA4SlBiSceeJBgY
Yp9PlGhCimx9am99TrdLoLCdTHB6oowt8tss3POpIOxaSlguyeym/sBhkUrnXOgN
ldMtDsvvc9KUfE4I0+c+XQ==
-----END XWING PUBLIC KEY-----
    """
    WireKEMScheme = "xwing"
    Addresses = ["tcp://127.0.0.1:30001"]</pre>
                <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                        <p><span class="bold"><strong>Identifier</strong></span></p>
                        <p>Specifies the human-readable identifier for the node which must be
                            unique per mixnet. The identifier can be an FQDN but does not have to
                            be.</p>
                        <p>Type: string</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>IdentityPublicKey</strong></span></p>
                        <p>String containing the node's public identity key in PEM format.
                                <code class="code">IdentityPublicKey</code> is the node's permanent identifier
                            and is used to verify cryptographic signatures produced by its private
                            identity key.</p>
                        <p>Type: string</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>PKISignatureScheme</strong></span></p>
                        <p>Specifies the cryptographic signature scheme used by all directory
                            authority nodes. <code class="code">PKISignatureScheme</code> must match the scheme
                            specified in the <code class="code">Server</code> section of the configuration. </p>
                        <p>Type: string</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>LinkPublicKey</strong></span></p>
                        <p>String containing the peer's public link-layer key in PEM format.
                                <code class="code">LinkPublicKey</code> must match the specified
                                <code class="code">WireKEMScheme</code>.</p>
                        <p>Type: string</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>WireKEMScheme</strong></span></p>
                        <p>Specifies the key encapsulation mechanism (KEM) scheme
                            for the <a class="ulink" href="https://eprint.iacr.org/2022/539" target="_top">PQ
                                Noise</a>-based wire protocol (link layer) that nodes use
                            to communicate with each other. PQ Noise is a post-quantum variation of
                            the <a class="ulink" href="https://noiseprotocol.org/" target="_top">Noise protocol
                                framework</a>, which algebraically transforms ECDH handshake
                            patterns into KEM encapsulate/decapsulate operations.</p>
                            
                            <p>This configuration option supports the optional use of
                            hybrid post-quantum cryptography to strengthen security. The following KEM
                            schemes are supported: </p><div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: circle; "><li class="listitem">
                                    <p><span class="bold"><strong>Classical:</strong></span> "x25519", "x448"</p>
                                    <div class="note" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Note"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Note]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/note.png"></td><th align="left">Note</th></tr><tr><td align="left" valign="top">
                                        <p>X25519 and X448 are actually non-interactive key-exchanges
                                            (NIKEs), not KEMs. Katzenpost uses
                                            a hashed ElGamal cryptographic construction
                                            to convert them from NIKEs to KEMs.</p>
                                    </td></tr></table></div>
                                </li><li class="listitem">
                                    <p><span class="bold"><strong>Hybrid post-quantum:</strong></span>
                                        "mlkem768", "sntrup4591761", "frodo640shake",
                                        "mceliece348864", "mceliece348864f", "mceliece460896",
                                        "mceliece460896f", "mceliece6688128", "mceliece6688128f",
                                        "mceliece6960119", "mceliece6960119f", "mceliece8192128",
                                        "mceliece8192128f", "xwing", "Kyber768-X25519",
                                        "MLKEM768-X25519", "MLKEM768-X448", "CTIDH511", "CTIDH512",
                                        "CTIDH1024", "CTIDH2048", "CTIDH512-X25519",
                                        "CTIDH512-X25519"</p>
                                </li></ul></div>						
                        <p>Type: string</p>
                        <p>Required: Yes</p>                    
                    </li><li class="listitem">
                        <p><span class="bold"><strong>Addresses</strong></span></p>
                        <p>Specifies a list of one or more address URLs in a format that contains
                            the transport protocol, IP address, and port number that the node will
                            bind to for incoming connections. Katzenpost supports URLs with that
                            start with either "tcp://" or "quic://" such as:
                            ["tcp://192.168.1.1:30001"] and ["quic://192.168.1.1:40001"].</p>
                        <p>Type: []string</p>
                        <p>Required: Yes</p>
                    </li></ul></div>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="auth-logging"></a>Dirauth: Logging section</h4></div></div></div>
                
                
                
                <div class="simplesect"><div class="titlepage"><div><div><h5 class="title"><a name="d6e303"></a></h5></div></div></div>
        
        <div class="informalexample"> 
            <p>The <code class="code">Logging</code> configuration section controls logging behavior across Katzenpost.</p>
            <pre class="programlisting">[Logging]
                Disable = false
                File = "katzenpost.log"
                Level = "INFO"</pre>
            <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                    <p><span class="bold"><strong>Disable</strong></span></p>
                    <p>If <span class="bold"><strong>true</strong></span>, logging is disabled.</p>
                    <p>Type: bool</p>
                    <p>Required: No</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>File</strong></span></p>
                    <p>Specifies the log file. If omitted, <code class="code">stdout</code> is used.</p>
                    <p>An absolute or relative file path can be specified. A relative path is 
                    relative to the DataDir specified in the <code class="code">Server</code> section of the 
                    configuration.</p>
                    <p>Type: string</p>
                    <p>Required: No</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>Level</strong></span></p>
                    <p>Supported logging level values are ERROR | WARNING | NOTICE |INFO | DEBUG.</p>
                    <p>Type: string</p>
                    <p>Required: No</p>
                    <div class="warning" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Warning"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Warning]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/warning.png"></td><th align="left">Warning</th></tr><tr><td align="left" valign="top">
                        <p>The DEBUG log level is unsafe for
                            production use.</p>
                    </td></tr></table></div>                               
                </li></ul></div>   
        </div>
    </div>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="auth-parameters"></a>Dirauth: Parameters section</h4></div></div></div>
                
                <p>The <code class="code">Parameters</code> section contains the network parameters.</p>
                <pre class="programlisting">[Parameters]
    SendRatePerMinute = 0
    Mu = 0.005
    MuMaxDelay = 1000
    LambdaP = 0.001
    LambdaPMaxDelay = 1000
    LambdaL = 0.0005
    LambdaLMaxDelay = 1000
    LambdaD = 0.0005
    LambdaDMaxDelay = 3000
    LambdaM = 0.0005
    LambdaG = 0.0
    LambdaMMaxDelay = 100
    LambdaGMaxDelay = 100</pre>
                <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                        <p><span class="bold"><strong>SendRatePerMinute</strong></span></p>
                        <p>Specifies the maximum allowed rate of packets per client per gateway
                            node. Rate limiting is done on the gateway nodes.</p>
                        <p>Type: uint64</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>Mu</strong></span></p>
                        <p>Specifies the inverse of the mean of the exponential distribution from
                            which the Sphinx packet per-hop mixing delay will be sampled.</p>
                        <p>Type: float64</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>MuMaxDelay</strong></span></p>
                        <p>Specifies the maximum Sphinx packet per-hop mixing delay in
                            milliseconds. </p>
                        <p>Type: uint64</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>LambdaP</strong></span></p>
                        <p>Specifies the inverse of the mean of the exponential distribution that
                            clients sample to determine the time interval between sending messages,
                            whether actual messages from the FIFO egress queue or decoy messages if
                            the queue is empty.</p>
                        <p>Type: float64</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>LambdaPMaxDelay</strong></span></p>
                        <p>Specifies the maximum send delay interval for LambdaP in
                            milliseconds.</p>
                        <p>Type: uint64</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>LambdaL</strong></span></p>
                        <p>Specifies the inverse of the mean of the exponential distribution that
                            clients sample to determine the delay interval between loop
                            decoys.</p>
                        <p>Type: float64</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>LambdaLMaxDelay</strong></span></p>
                        <p>Specifies the maximum send delay interval for LambdaL in
                            milliseconds.</p>
                        <p>Type: uint64</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>LambdaD</strong></span></p>
                        <p>LambdaD is the inverse of the mean of the exponential distribution
                            that clients sample to determine the delay interval between decoy drop
                            messages. </p>
                        <p>Type: float64</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>LambdaDMaxDelay</strong></span></p>
                        <p>Specifies the maximum send interval in for LambdaD in milliseconds. </p>
                        <p>Type: uint64</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>LambdaM</strong></span></p>
                        <p>LambdaM is the inverse of the mean of the exponential distribution
                            that mix nodes sample to determine the delay between mix loop
                            decoys.</p>
                        <p>Type: float64</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>LambdaG</strong></span></p>
                        <p>LambdaG is the inverse of the mean of the exponential distribution
                            that gateway nodes to select the delay between gateway node
                            decoys.</p>
                        <div class="warning" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Warning"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Warning]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/warning.png"></td><th align="left">Warning</th></tr><tr><td align="left" valign="top">
                            <p>Do not set this value manually in the TOML configuration file. The
                                field is used internally by the dirauth server state machine.</p>
                        </td></tr></table></div>
                        <p>Type: float64</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>LambdaMMaxDelay</strong></span></p>
                        <p>Specifies the maximum delay for LambdaM in milliseconds.</p>
                        <p>Type: uint64</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>LambdaGMaxDelay</strong></span></p>
                        <p>Specifies the maximum delay for LambdaG in milliseconds.</p>
                        <p>Type: uint64</p>
                        <p>Required: Yes</p>
                    </li></ul></div>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="auth-debug"></a>Dirauth: Debug section</h4></div></div></div>
                
                <pre class="programlisting">[Debug]
    Layers = 3
    MinNodesPerLayer = 1
    GenerateOnly = false</pre>
                <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                        <p><span class="bold"><strong>Layers</strong></span></p>
                        <p>Specifies the number of non-service-provider layers in the network
                            topology.</p>
                        <p>Type: int</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>MinNodesrPerLayer</strong></span></p>
                        <p>Specifies the minimum number of nodes per layer required to form a
                            valid consensus document.</p>
                        <p>Type: int</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>GenerateOnly</strong></span></p>
                        <p>If <span class="bold"><strong>true</strong></span>, the server halts and cleans
                            up the data directory immediately after long-term key generation.</p>
                        <p>Type: bool</p>
                        <p>Required: No</p>
                    </li></ul></div>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="auth-mixes-section-config"></a>Dirauth: Mixes
                    sections</h4></div></div></div>
                
                <p>The <code class="code">Mixes</code> configuration sections list mix nodes that are known to
                    the authority.</p>
                <pre class="programlisting">[[Mixes]]
    Identifier = "mix1"
    IdentityPublicKeyPem = "../mix1/identity.public.pem"

[[Mixes]]
    Identifier = "mix2"
    IdentityPublicKeyPem = "../mix2/identity.public.pem"

[[Mixes]]
    Identifier = "mix3"
    IdentityPublicKeyPem = "../mix3/identity.public.pem"</pre>
                <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                        <p><span class="bold"><strong>Identifier</strong></span></p>
                        <p>Specifies the human-readable identifier for a mix node, and must be
                            unique per mixnet. The identifier can be an FQDN but does not have to
                            be.</p>
                        <p>Type: string</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>IdentityPublicKeyPem</strong></span></p>
                        <p>Path and file name of a mix node's public identity signing key, also
                            known as the identity key, in PEM format.</p>
                        <p>Type: string</p>
                        <p>Required: Yes</p>
                    </li></ul></div>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="auth-gatewaynodes-section-config"></a>Dirauth:
                        GatewayNodes section</h4></div></div></div>
                
                <p>The <code class="code">GatewayNodes</code> sections list gateway nodes that are known to
                    the authority.</p>
                <pre class="programlisting">[[GatewayNodes]]
    Identifier = "gateway1"
    IdentityPublicKeyPem = "../gateway1/identity.public.pem"</pre>
                <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                        <p><span class="bold"><strong>Identifier</strong></span></p>
                        <p>Specifies the human-readable identifier for a gateway node, and must
                            be unique per mixnet. Identifier can be an FQDN but does not have to
                            be.</p>
                        <p>Type: string</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>IdentityPublicKeyPem</strong></span></p>
                        <p>Path and file name of a gateway node's public identity signing key,
                            also known as the identity key, in PEM format.</p>
                        <p>Type: string</p>
                        <p>Required: Yes</p>
                    </li></ul></div>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="auth-servicenodes-section-config"></a>Dirauth:
                        ServiceNodes sections</h4></div></div></div>
                
                <p>The <code class="code">ServiceNodes</code> sections list service nodes that are known to
                    the authority.</p>
                <pre class="programlisting">[[ServiceNodes]]
    Identifier = "servicenode1"
    IdentityPublicKeyPem = "../servicenode1/identity.public.pem"</pre>
                <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                        <p><span class="bold"><strong>Identifier</strong></span></p>
                        <p>Specifies the human-readable identifier for a service node, and must
                            be unique per mixnet. Identifier can be an FQDN but does not have to
                            be.</p>
                        <p>Type: string</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>IdentityPublicKeyPem</strong></span></p>
                        <p>Path and file name of a service node's public identity signing key,
                            also known as the identity key, in PEM format.</p>
                        <p>Type: string</p>
                        <p>Required: Yes</p>
                    </li></ul></div>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="auth-topology"></a>Dirauth: Topology section</h4></div></div></div>
                
                <p>The <code class="code">Topology</code> section defines the layers of the mix network and
                    the mix nodes in each layer.</p>
                <pre class="programlisting">[Topology]
                    
    [[Topology.Layers]]
    
        [[Topology.Layers.Nodes]]
            Identifier = "mix1"
            IdentityPublicKeyPem = "../mix1/identity.public.pem"
    
    [[Topology.Layers]]
    
        [[Topology.Layers.Nodes]]
            Identifier = "mix2"
            IdentityPublicKeyPem = "../mix2/identity.public.pem"
    
    [[Topology.Layers]]
    
        [[Topology.Layers.Nodes]]
            Identifier = "mix3"
            IdentityPublicKeyPem = "../mix3/identity.public.pem"</pre>
                <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                        <p><span class="bold"><strong>Identifier</strong></span></p>
                        <p>Specifies the human-readable identifier for a node, and must be unique
                            per mixnet. The identifier can be an FQDN but does not have to
                            be.</p>
                        <p>Type: string</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>IdentityPublicKeyPem</strong></span></p>
                        <p>Path and file name of a mix node's public identity signing key, also
                            known as the identity key, in PEM format.</p>
                        <p>Type: string</p>
                        <p>Required: Yes</p>
                    </li></ul></div>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="auth-sphinx-config"></a>Dirauth: SphinxGeometry
                    section</h4></div></div></div>
                
                <p>Sphinx is an encrypted nested-packet format designed primarily for mixnets.
                    The <a class="ulink" href="https://www.freehaven.net/anonbib/cache/DBLP:conf/sp/DanezisG09.pdf" target="_top">original Sphinx paper</a> described a non-interactive key exchange
                    (NIKE) employing classical encryption. The Katzenpost implementation
                    strongly emphasizes configurability, supporting key encapsulation mechanisms
                    (KEMs) as well as NIKEs, and enabling the use of either classical or hybrid
                    post-quantum cryptography. Hybrid constructions offset the newness of
                    post-quantum algorithms by offering heavily tested classical algorithms as a
                    fallback.</p>
                <div class="note" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Note"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Note]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/note.png"></td><th align="left">Note</th></tr><tr><td align="left" valign="top">
                    <p>Sphinx, the nested-packet format, should not be confused with <a class="ulink" href="http://sphincs.org/index.html" target="_top">Sphincs or Sphincs+</a>, which
                        are post-quantum signature schemes.</p>
                </td></tr></table></div>
                <p>Katzenpost Sphinx also relies on the following classical cryptographic
                    primitives: </p>
                <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                        <p>CTR-AES256, a stream cipher</p>
                    </li><li class="listitem">
                        <p>HMAC-SHA256, a message authentication code (MAC) function</p>
                    </li><li class="listitem">
                        <p>HKDF-SHA256, a key derivation function (KDF)</p>
                    </li><li class="listitem">
                        <p>AEZv5, a strong pseudorandom permutation (SPRP)</p>
                    </li></ul></div>
                <p>All dirauths must be configured to use the same <code class="code">SphinxGeometry</code>
                    parameters. Any geometry not advertised by the PKI document will fail. Each
                    dirauth publishes the hash of its <code class="code">SphinxGeometry</code> parameters in the
                    PKI document for validation by its peer dirauths. </p>
                
                
                <div class="simplesect"><div class="titlepage"><div><div><h5 class="title"><a name="d6e534"></a></h5></div></div></div>
        
        <div class="informalexample">        
            <p>The <code class="code">SphinxGeometry</code> section defines parameters for the Sphinx
                encrypted nested-packet format used internally by Katzenpost. 
                </p><div class="warning" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Warning"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Warning]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/warning.png"></td><th align="left">Warning</th></tr><tr><td align="left" valign="top"><p>The values in the <code class="code">SphinxGeometry</code> configuration section must
                        be programmatically generated by <span class="command"><strong>gensphinx</strong></span>. Many of the
                        parameters are interdependent and cannot be individually modified. Do not
                        modify the these values by hand.</p></td></tr></table></div>
            <p>The settings in this section are generated by the <span class="command"><strong>gensphinx</strong></span>
                utility, which computes the Sphinx geometry based on the following user-supplied
                directives:</p>
            <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                    <p>The number of  mix node layers (not counting gateway and service
                        nodes)</p>
                </li><li class="listitem">
                    <p>The length of the application-usable packet payload</p>
                </li><li class="listitem">
                    <p>The selected NIKE or KEM scheme</p>
                </li></ul></div>
            <p>The output in TOML should then be pasted unchanged into the node's configuration
                file, as shown below. For more information, see <a class="xref" href="#gensphinx" title="Chapter&nbsp;4.&nbsp;Appendix: Using gensphinx">Chapter&nbsp;4, <i>Appendix: Using <span class="emphasis"><em>gensphinx</em></span></i></a>.</p>
            <pre class="programlisting">[SphinxGeometry]
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
                KEMName = ""</pre>
            <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                    <p><span class="bold"><strong>PacketLength</strong></span></p>
                    <p>The length of a Sphinx packet in bytes.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>NrHops</strong></span></p>
                    <p>The number of hops a Sphinx packet takes through the mixnet. Because
                        packet headers hold destination information for each hop, the size of the
                        header increases linearly with the number of hops.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>HeaderLength</strong></span></p>
                    <p>The total length of the Sphinx packet header in bytes.</p>                   
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>RoutingInfoLength</strong></span></p>
                    <p>The total length of the routing information portion of the Sphinx packet
                        header.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>PerHopRoutingInfoLength</strong></span></p>
                    <p>The length of the per-hop routing information in the Sphinx packet
                        header.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>SURBLength</strong></span></p>
                    <p>The length of a single-use reply block (SURB).</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>SphinxPlaintextHeaderLength</strong></span></p>
                    <p>The length of the plaintext Sphinx packet header.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>PayloadTagLength</strong></span></p>
                    <p>The length of the payload tag.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>ForwardPayloadLength</strong></span></p>
                    <p>The total size of the payload.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>UserForwardPayloadLength</strong></span></p>
                    <p>The size of the usable payload.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>NextNodeHopLength</strong></span></p>
                    <p>The <code class="code">NextNodeHopLength</code> is derived from the largest routing-information 
                        block that we expect to encounter. Other packets have 
                        <code class="code">NextNodeHop</code> + <code class="code">NodeDelay</code> sections, or a <code class="code">Recipient</code> section, both of which
                        are shorter.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>SPRPKeyMaterialLength</strong></span></p>
                    <p>The length of the strong pseudo-random permutation (SPRP) key.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>NIKEName</strong></span></p>
                    <p>The name of the non-interactive key exchange (NIKE) scheme used by Sphinx
                        packets.</p>
                    <p><code class="code">NIKEName</code> and <code class="code">KEMName</code> are mutually
                        exclusive.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>KEMName</strong></span></p>
                    <p>The name of the key encapsulation mechanism (KEM) used by Sphinx
                        packets.</p>
                    <p><code class="code">NIKEName</code> and <code class="code">KEMName</code> are mutually exclusive.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li></ul></div>            
        </div>
    </div>
            </div>
        </div>
        <div class="section"><div class="titlepage"><div><div><h3 class="title"><a name="mix-config"></a>Configuring mix nodes</h3></div></div></div>
            
            <p>The following configuration is drawn from the reference implementation in
                    <code class="filename">katzenpost/docker/dirauth_mixnet/mix1/katzenpost.toml</code>. In a
                real-world mixnet, the component hosts would not be sharing a single IP address. For
                more information about the test mixnet, see <span class="bold"><strong><a class="xref" href="#container" title="Chapter&nbsp;2.&nbsp;Using the Katzenpost Docker test network">Using the Katzenpost Docker test network</a></strong></span>.</p>
            <p>
                </p><div class="table"><a name="d6e657"></a><p class="title"><b>Table&nbsp;1.3.&nbsp;Mix node configuration sections</b></p><div class="table-contents">
                    
                    <table class="table" summary="Mix node configuration sections" border="1"><colgroup><col class="c1"></colgroup><tbody><tr><td>
                                    <p><a class="xref" href="#mix-server-section-config" title="Mix node: Server section">Mix node: Server section</a></p>
                                </td></tr><tr><td>
                                    <p><a class="xref" href="#mix-logging-config" title="Mix node: Logging section">Mix node: Logging section</a></p>
                                </td></tr><tr><td>
                                    <p><a class="xref" href="#mix-pki-config" title="Mix node: PKI section">Mix node: PKI section</a></p>
                                </td></tr><tr><td>
                                    <p><a class="xref" href="#mix-management-config" title="Mix node: Management section">Mix node: Management section</a></p>
                                </td></tr><tr><td>
                                    <p><a class="xref" href="#mix-sphinx-config" title="Mix node: SphinxGeometry section">Mix node: SphinxGeometry section</a></p>
                                </td></tr><tr><td>
                                    <p><a class="xref" href="#mix-debug-config" title="Mix node: Debug section">Mix node: Debug section</a></p>
                                </td></tr></tbody></table>
                </div></div><p><br class="table-break">
            </p>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="mix-server-section-config"></a>Mix node: Server section</h4></div></div></div>
                
                <p>The <code class="code">Server</code> section configures mandatory basic parameters for each
                    server node.</p>
                <p>
                    </p><pre class="programlisting">[Server]
  Identifier = "mix1"
  WireKEM = "xwing"
  PKISignatureScheme = "Ed25519"
  Addresses = ["127.0.0.1:30008"]
  OnlyAdvertiseAltAddresses = false
  MetricsAddress = "127.0.0.1:30009"
  DataDir = "/dirauth_mixnet/mix1"
  IsGatewayNode = false
  IsServiceNode = false
  [Server.AltAddresses]</pre><p>
                </p>
                
                
                <div class="simplesect"><div class="titlepage"><div><div><h5 class="title"><a name="d6e692"></a></h5></div></div></div>
        
               
        <div class="informalexample"> 
            <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                    <p><span class="bold"><strong>Identifier</strong></span></p>
                    <p>Specifies the human-readable identifier for a node, and must be unique per mixnet. 
                        The identifier can be an FQDN but does not have to be.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                        <p><span class="bold"><strong>WireKEM</strong></span></p>
                        <p>WireKEM specifies the key encapsulation mechanism (KEM) scheme
                            for the <a class="ulink" href="https://eprint.iacr.org/2022/539" target="_top">PQ
                                Noise</a>-based wire protocol (link layer) that nodes use
                            to communicate with each other. PQ Noise is a post-quantum variation of
                            the <a class="ulink" href="https://noiseprotocol.org/" target="_top">Noise protocol
                                framework</a>, which algebraically transforms ECDH handshake
                            patterns into KEM encapsulate/decapsulate operations.</p>
                            
                            <p>This configuration option supports the optional use of
                            hybrid post-quantum cryptography to strengthen security. The following KEM
                            schemes are supported: </p><div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: circle; "><li class="listitem">
                                    <p><span class="bold"><strong>Classical:</strong></span> "x25519",
                                        "x448"</p>
                                     <div class="note" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Note"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Note]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/note.png"></td><th align="left">Note</th></tr><tr><td align="left" valign="top"><p>X25519 and X448 are actually non-interactive key-exchanges
                                            (NIKEs), not KEMs. Katzenpost uses
                                            a Hashed ElGamal cryptographic construction
                                            to convert them from NIKEs to KEMs.</p></td></tr></table></div>
                                </li><li class="listitem">
                                    <p><span class="bold"><strong>Hybrid post-quantum:</strong></span>
                                        "mlkem768", "sntrup4591761", "frodo640shake",
                                        "mceliece348864", "mceliece348864f", "mceliece460896",
                                        "mceliece460896f", "mceliece6688128", "mceliece6688128f",
                                        "mceliece6960119", "mceliece6960119f", "mceliece8192128",
                                        "mceliece8192128f", "xwing", "Kyber768-X25519",
                                        "MLKEM768-X25519", "MLKEM768-X448", "CTIDH511", "CTIDH512",
                                        "CTIDH1024", "CTIDH2048", "CTIDH512-X25519",
                                        "CTIDH512-X25519"</p>
                                </li></ul></div>						
                        <p>Type: string</p>
                        <p>Required: Yes</p>                    
                    </li><li class="listitem">
                    <p><span class="bold"><strong>PKISignatureScheme</strong></span></p>
                    <p>Specifies the cryptographic signature scheme that will be used by all
                        components of the mix network when interacting with the PKI system. Mix
                        nodes sign their descriptors using this signature scheme, and dirauth nodes
                        similarly sign PKI documents using the same scheme.</p>
                    <p>The following signature schemes are supported:</p>
                    <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: circle; "><li class="listitem">
                            <p><span class="bold"><strong>Classical:</strong></span>  "ed25519", "ed448"</p>
                        </li><li class="listitem">
                            <p><span class="bold"><strong>Hybrid post-quantum:</strong></span> "Ed25519
                                Sphincs+", "Ed448-Sphincs+", "Ed25519-Dilithium2",
                                "Ed448-Dilithium3" </p>
                        </li></ul></div>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>Addresses</strong></span></p>
                    <p>Specifies a list of one or more address URLs in a format that contains the
                        transport protocol, IP address, and port number that the server will bind to
                        for incoming connections. Katzenpost supports URLs with that start with
                        either "tcp://" or "quic://" such as: ["tcp://192.168.1.1:30001"] and
                        ["quic://192.168.1.1:40001"].</p>
                    <p>Type: []string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>BindAddresses</strong></span></p>
                    <p>If <span class="bold"><strong>true</strong></span>, allows setting of listener
                        addresses that the server will bind to and accept connections on. These
                        addresses are not advertised in the PKI.</p>
                    <p>Type: bool</p>
                    <p>Required: No</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>MetricsAddress</strong></span></p>
                    <p>Specifies the address/port to bind the Prometheus metrics endpoint
                        to.</p>
                    <p>Type: string</p>
                    <p>Required: No</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>DataDir</strong></span></p>
                    <p>Specifies the absolute path to a node's state directory. This is 
                        where persistence.db is written to disk and where a node stores its 
                        cryptographic key materials when started with the "-g" commmand-line 
                        option.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>IsGatewayNode</strong></span></p>
                    <p>If <span class="bold"><strong>true</strong></span>, the server is a gateway
                        node.</p>
                    <p>Type: bool</p>
                    <p>Required: No</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>IsServiceNode</strong></span></p>
                    <p>If <span class="bold"><strong>true</strong></span>, the server is a service
                        node.</p>
                    <p>Type: bool</p>
                    <p>Required: No</p>
                </li></ul></div>
            
        </div>
    </div>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="mix-logging-config"></a>Mix node: Logging section</h4></div></div></div>
                
                
                
                <div class="simplesect"><div class="titlepage"><div><div><h5 class="title"><a name="d6e775"></a></h5></div></div></div>
        
        <div class="informalexample"> 
            <p>The <code class="code">Logging</code> configuration section controls logging behavior across Katzenpost.</p>
            <pre class="programlisting">[Logging]
                Disable = false
                File = "katzenpost.log"
                Level = "INFO"</pre>
            <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                    <p><span class="bold"><strong>Disable</strong></span></p>
                    <p>If <span class="bold"><strong>true</strong></span>, logging is disabled.</p>
                    <p>Type: bool</p>
                    <p>Required: No</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>File</strong></span></p>
                    <p>Specifies the log file. If omitted, <code class="code">stdout</code> is used.</p>
                    <p>An absolute or relative file path can be specified. A relative path is 
                    relative to the DataDir specified in the <code class="code">Server</code> section of the 
                    configuration.</p>
                    <p>Type: string</p>
                    <p>Required: No</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>Level</strong></span></p>
                    <p>Supported logging level values are ERROR | WARNING | NOTICE |INFO | DEBUG.</p>
                    <p>Type: string</p>
                    <p>Required: No</p>
                    <div class="warning" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Warning"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Warning]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/warning.png"></td><th align="left">Warning</th></tr><tr><td align="left" valign="top">
                        <p>The DEBUG log level is unsafe for
                            production use.</p>
                    </td></tr></table></div>                               
                </li></ul></div>   
        </div>
    </div>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="mix-pki-config"></a>Mix node: PKI section</h4></div></div></div>
                
                
                
                <div class="simplesect"><div class="titlepage"><div><div><h5 class="title"><a name="d6e808"></a></h5></div></div></div>
             
        <div class="informalexample"> 
            <p>The <code class="code">PKI</code> section contains the directory authority configuration for a mix, gateway, or service node.</p>
            <pre class="programlisting">[PKI]
[PKI.dirauth]

    [[PKI.dirauth.Authorities]]
        Identifier = "auth1"
        IdentityPublicKey = """-----BEGIN ED25519 PUBLIC KEY-----
tqN6tpOVotHWXKCszVn2kS7vAZjQpvJjQF3Qz/Qwhyg=
-----END ED25519 PUBLIC KEY-----
"""
        PKISignatureScheme = "Ed25519"
        LinkPublicKey = """-----BEGIN XWING PUBLIC KEY-----
JnJ8ztQEIjAkKJcpuZvJAdkWjBim/5G5d8yoosEQHeGJeeBqNPdm2AitUbpiQPcd
tNCo9DxuC9Ieqmsfw0YpV6AtOOsaInA6QnHDYcuBfZcQL5MU4+t2TzpBZQYlrSED
hPCKrAG+8GEUl6akseG371WQzEtPpEWWCJCJOiS/VDFZT7eKrldlumN6gfiB84sR
...
arFh/WKwYJUj+aGBsFYSqGdzC6MdY4x/YyFe2ze0MJEjThQE91y1d/LCQ3Sb7Ri+
u6PBi3JU2qzlPEejDKwK0t5tMNEAkq8iNrpRTdD/hS0gR+ZIN8Z9QKh7Xf94FWG2
H+r8OaqImQhgHabrWRDyLg==
-----END XWING PUBLIC KEY-----
"""
        WireKEMScheme = "xwing"
        Addresses = ["127.0.0.1:30001"]

    [[PKI.dirauth.Authorities]]
        Identifier = "auth2"
        IdentityPublicKey = """-----BEGIN ED25519 PUBLIC KEY-----
O51Ty2WLu4C1ETMa29s03bMXV72gnjJfTfwLV++LVBI=
-----END ED25519 PUBLIC KEY-----	
"""
        PKISignatureScheme = "Ed25519"
        LinkPublicKey = """-----BEGIN XWING PUBLIC KEY-----
TtQkg2XKUnY602FFBaPJ+zpN0Twy20cwyyFxh7FNUjaXA9MAJXs0vUwFbJc6BjYv
f+olKnlIKFSmDvcF74U6w1F0ObugwTNKNxeYKPKhX4FiencUbRwkHoYHdtZdSctz
TKy08qKQyCAccqCRpdo6ZtYXPAU+2rthjYTOL7Zn+7SHUKCuJClcPnvEYjVcJxtZ
...
ubJIe5U4nMJbBkOqr7Kq6niaEkiLODa0tkpB8tKMYTMBdcYyHSXCzpo7U9sb6LAR
HktiTBDtRXviu2vbw7VRXhkMW2kjYZDtReQ5sAse04DvmD49zgTp1YxYW+wWFaL3
37X7/SNuLdHX4PHZXIWHBQ==
-----END XWING PUBLIC KEY-----	
"""
        WireKEMScheme = "xwing"
        Addresses = ["127.0.0.1:30002"]

    [[PKI.dirauth.Authorities]]
        Identifier = "auth3"
        IdentityPublicKey = """-----BEGIN ED25519 PUBLIC KEY-----
zQvydRYJq3npeLcg1NqIf+SswEKE5wFmiwNsI9Z1whQ=
-----END ED25519 PUBLIC KEY-----
"""
        PKISignatureScheme = "Ed25519"
        LinkPublicKey = """
-----BEGIN XWING PUBLIC KEY-----
OYK9FiC53xwZ1VST3jDOO4tR+cUMSVRSekmigZMChSjDCPZbKut8TblxtlUfc/yi
Ugorz4NIvYPMWUt3QPwS2UWq8/HMWXNGPUiAevg12+oV+jOJXaJeCfY24UekJnSw
TNcdGaFZFSR0FocFcPBBnrK1M2B8w8eEUKQIsXRDM3x/8aRIuDif+ve8rSwpgKeh
...
OdVD3yw7OOS8uPZLORGQFyJbHtVmFPVvwja4G/o2gntAoHUZ2LiJJakpVhhlSyrI
yuzvwwFtZVfWtNb5gAKZCyg0aduR3qgd7MPerRF+YopZk3OCRpC02YxfUZrHv398
FZWJFK0R8iU52CEUxVpXTA==
-----END XWING PUBLIC KEY-----	
"""
        WireKEMScheme = "xwing"
        Addresses = ["127.0.0.1:30003"]</pre>
            <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                    <p><span class="bold"><strong>Identifier</strong></span></p>
                    <p>Specifies the human-readable identifier for a node, which must be unique per mixnet. 
                    The identifier can be an FQDN but does not have to be.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>IdentityPublicKey</strong></span></p>
                    <p>String containing the node's public identity key in PEM format.
                            <code class="code">IdentityPublicKey</code> is the node's permanent identifier
                        and is used to verify cryptographic signatures produced by its private
                        identity key.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>PKISignatureScheme</strong></span></p>
                    <p>Specifies the cryptographic signature scheme that will be used by all
                        components of the mix network when interacting with the PKI system. Mix
                        nodes sign their descriptors using this signature scheme, and dirauth nodes
                        similarly sign PKI documents using the same scheme.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>LinkPublicKey</strong></span></p>
                    <p>String containing the peer's public link-layer key in PEM format.
                            <code class="code">LinkPublicKey</code> must match the specified
                            <code class="code">WireKEMScheme</code>.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>WireKEMScheme</strong></span></p>
                    <p>The name of the wire protocol key-encapsulation mechanism (KEM) to use.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>Addresses</strong></span></p>
                    <p>Specifies a list of one or more address URLs in a format that contains the
                        transport protocol, IP address, and port number that the server will bind to
                        for incoming connections. Katzenpost supports URLs that start with
                        either "tcp://" or "quic://" such as: ["tcp://192.168.1.1:30001"] and
                        ["quic://192.168.1.1:40001"].</p>
                    <p>Type: []string</p>
                    <p>Required: Yes</p>
                </li></ul></div>                            
        </div>
    </div>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="mix-management-config"></a>Mix node: Management section</h4></div></div></div>
                
                
                
                <div class="simplesect"><div class="titlepage"><div><div><h5 class="title"><a name="d6e856"></a></h5></div></div></div>
        
           <div class="informalexample"> 
           <p>The <code class="code">Management</code> section specifies 
               connectivity information for the Katzenpost control protocol which can be used to make run-time 
               configuration changes. A configuration resembles the following:</p>
           <pre class="programlisting">[Management]
   Enable = false
   Path = "/dirauth_mixnet/mix1/management_sock"</pre>
           <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                   <p><span class="bold"><strong>Enable</strong></span></p>
                   <p>If <span class="bold"><strong>true</strong></span>, the management interface is
                        enabled.</p>
                   <p>Type: bool</p>
                   <p>Required: No</p>
               </li><li class="listitem">
                   <p><span class="bold"><strong>Path</strong></span></p>
                   <p>Specifies the path to the management interface socket. If left empty, then <code class="code">management_sock</code> 
                       is located in the configuration's defined <code class="code">DataDir</code>&gt;.</p>
                   <p>Type: string</p>
                   <p>Required: No</p>
               </li></ul></div>
       </div>
    </div>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="mix-sphinx-config"></a>Mix node: SphinxGeometry section</h4></div></div></div>
                
                
                
                <div class="simplesect"><div class="titlepage"><div><div><h5 class="title"><a name="d6e880"></a></h5></div></div></div>
        
        <div class="informalexample">        
            <p>The <code class="code">SphinxGeometry</code> section defines parameters for the Sphinx
                encrypted nested-packet format used internally by Katzenpost. 
                </p><div class="warning" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Warning"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Warning]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/warning.png"></td><th align="left">Warning</th></tr><tr><td align="left" valign="top"><p>The values in the <code class="code">SphinxGeometry</code> configuration section must
                        be programmatically generated by <span class="command"><strong>gensphinx</strong></span>. Many of the
                        parameters are interdependent and cannot be individually modified. Do not
                        modify the these values by hand.</p></td></tr></table></div>
            <p>The settings in this section are generated by the <span class="command"><strong>gensphinx</strong></span>
                utility, which computes the Sphinx geometry based on the following user-supplied
                directives:</p>
            <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                    <p>The number of  mix node layers (not counting gateway and service
                        nodes)</p>
                </li><li class="listitem">
                    <p>The length of the application-usable packet payload</p>
                </li><li class="listitem">
                    <p>The selected NIKE or KEM scheme</p>
                </li></ul></div>
            <p>The output in TOML should then be pasted unchanged into the node's configuration
                file, as shown below. For more information, see <a class="xref" href="#gensphinx" title="Chapter&nbsp;4.&nbsp;Appendix: Using gensphinx">Chapter&nbsp;4, <i>Appendix: Using <span class="emphasis"><em>gensphinx</em></span></i></a>.</p>
            <pre class="programlisting">[SphinxGeometry]
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
                KEMName = ""</pre>
            <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                    <p><span class="bold"><strong>PacketLength</strong></span></p>
                    <p>The length of a Sphinx packet in bytes.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>NrHops</strong></span></p>
                    <p>The number of hops a Sphinx packet takes through the mixnet. Because
                        packet headers hold destination information for each hop, the size of the
                        header increases linearly with the number of hops.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>HeaderLength</strong></span></p>
                    <p>The total length of the Sphinx packet header in bytes.</p>                   
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>RoutingInfoLength</strong></span></p>
                    <p>The total length of the routing information portion of the Sphinx packet
                        header.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>PerHopRoutingInfoLength</strong></span></p>
                    <p>The length of the per-hop routing information in the Sphinx packet
                        header.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>SURBLength</strong></span></p>
                    <p>The length of a single-use reply block (SURB).</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>SphinxPlaintextHeaderLength</strong></span></p>
                    <p>The length of the plaintext Sphinx packet header.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>PayloadTagLength</strong></span></p>
                    <p>The length of the payload tag.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>ForwardPayloadLength</strong></span></p>
                    <p>The total size of the payload.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>UserForwardPayloadLength</strong></span></p>
                    <p>The size of the usable payload.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>NextNodeHopLength</strong></span></p>
                    <p>The <code class="code">NextNodeHopLength</code> is derived from the largest routing-information 
                        block that we expect to encounter. Other packets have 
                        <code class="code">NextNodeHop</code> + <code class="code">NodeDelay</code> sections, or a <code class="code">Recipient</code> section, both of which
                        are shorter.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>SPRPKeyMaterialLength</strong></span></p>
                    <p>The length of the strong pseudo-random permutation (SPRP) key.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>NIKEName</strong></span></p>
                    <p>The name of the non-interactive key exchange (NIKE) scheme used by Sphinx
                        packets.</p>
                    <p><code class="code">NIKEName</code> and <code class="code">KEMName</code> are mutually
                        exclusive.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>KEMName</strong></span></p>
                    <p>The name of the key encapsulation mechanism (KEM) used by Sphinx
                        packets.</p>
                    <p><code class="code">NIKEName</code> and <code class="code">KEMName</code> are mutually exclusive.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li></ul></div>            
        </div>
    </div>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="mix-debug-config"></a>Mix node: Debug section</h4></div></div></div>
                
                
                
                <div class="simplesect"><div class="titlepage"><div><div><h5 class="title"><a name="d6e998"></a></h5></div></div></div>
             
        <div class="informalexample">    
            <p>The <code class="code">Debug</code> section is the Katzenpost server debug configuration
                for advanced tuning.</p>   
            <pre class="programlisting">[Debug]
                NumSphinxWorkers = 16
                NumServiceWorkers = 3
                NumGatewayWorkers = 3
                NumKaetzchenWorkers = 3
                SchedulerExternalMemoryQueue = false
                SchedulerQueueSize = 0
                SchedulerMaxBurst = 16
                UnwrapDelay = 250
                GatewayDelay = 500
                ServiceDelay = 500
                KaetzchenDelay = 750
                SchedulerSlack = 150
                SendSlack = 50
                DecoySlack = 15000
                ConnectTimeout = 60000
                HandshakeTimeout = 30000
                ReauthInterval = 30000
                SendDecoyTraffic = false
                DisableRateLimit = false
                GenerateOnly = false</pre>
                <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                        <p><span class="bold"><strong>NumSphinxWorkers</strong></span></p>
                        <p>Specifies the number of worker instances to use for inbound Sphinx
                            packet processing.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>NumProviderWorkers</strong></span></p>
                        <p>Specifies the number of worker instances to use for provider specific
                            packet processing.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>NumKaetzchenWorkers</strong></span></p>
                        <p>Specifies the number of worker instances to use for Kaetzchen-specific
                        packet processing.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>SchedulerExternalMemoryQueue</strong></span></p>
                        <p>If <span class="bold"><strong>true</strong></span>, the experimental disk-backed external memory 
                            queue is enabled.</p>
                        <p>Type: bool</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>SchedulerQueueSize</strong></span></p>
                        <p>Specifies the maximum scheduler queue size before random entries will
                        start getting dropped. A value less than or equal to zero is treated as
                        unlimited.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>SchedulerMaxBurst</strong></span></p>
                        <p>Specifies the maximum number of packets that will be dispatched per
                            scheduler wakeup event.</p>
                        <p>Type: </p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>UnwrapDelay</strong></span></p>
                        <p>Specifies the maximum unwrap delay due to queueing in
                            milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>GatewayDelay</strong></span></p>
                        <p>Specifies the maximum gateway node worker delay due to queueing in milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>ServiceDelay</strong></span></p>
                        <p>Specifies the maximum provider delay due to queueing in
                            milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p> 
                    </li><li class="listitem">
                        <p><span class="bold"><strong>KaetzchenDelay</strong></span></p>
                        <p>Specifies the maximum kaetzchen delay due to queueing in
                            milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>SchedulerSlack</strong></span></p>
                        <p>Specifies the maximum scheduler slack due to queueing and/or
                            processing in milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>SendSlack</strong></span></p>
                        <p>Specifies the maximum send-queue slack due to queueing and/or
                            congestion in milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>DecoySlack</strong></span></p>
                        <p>Specifies the maximum decoy sweep slack due to external
                            delays such as latency before a loop decoy packet will be considered
                            lost.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>ConnectTimeout</strong></span></p>
                        <p>Specifies the maximum time a connection can take to establish a
                            TCP/IP connection in milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>HandshakeTimeout</strong></span></p>
                        <p>Specifies the maximum time a connection can take for a link-protocol
                            handshake in milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>ReauthInterval</strong></span></p>
                        <p>Specifies the interval at which a connection will be reauthenticated
                            in milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>SendDecoyTraffic</strong></span></p>
                        <p>If <span class="bold"><strong>true</strong></span>, decoy traffic is enabled. 
                            This parameter is experimental and untuned, 
                            and is disabled by default.</p>
                        <div class="note" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Note"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Note]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/note.png"></td><th align="left">Note</th></tr><tr><td align="left" valign="top">
                            <p>This option will be removed once decoy traffic is fully implemented.</p>
                        </td></tr></table></div>
                        <p>Type: bool</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>DisableRateLimit</strong></span></p>
                        <p>If <span class="bold"><strong>true</strong></span>, the per-client rate limiter is disabled.</p>
                        <div class="note" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Note"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Note]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/note.png"></td><th align="left">Note</th></tr><tr><td align="left" valign="top">
                            <p>This option should only be used for testing.</p>
                        </td></tr></table></div>
                        <p>Type: bool</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>GenerateOnly</strong></span></p>
                        <p>If <span class="bold"><strong>true</strong></span>, the server immediately halts
                        and cleans up after long-term key generation.</p>
                        <p>Type: bool</p>
                        <p>Required: No</p>
                    </li></ul></div>
        </div> 
    </div>
            </div>
        </div>
        <div class="section"><div class="titlepage"><div><div><h3 class="title"><a name="gateway-config"></a>Configuring gateway nodes</h3></div></div></div>
            
            <p>The following configuration is drawn from the reference implementation in
                    <code class="filename">katzenpost/docker/dirauth_mixnet/gateway1/katzenpost.toml</code>.
                In a real-world mixnet, the component hosts would not be sharing a single IP
                address. For more information about the test mixnet, see <span class="bold"><strong><a class="xref" href="#container" title="Chapter&nbsp;2.&nbsp;Using the Katzenpost Docker test network">Using the Katzenpost Docker test network</a></strong></span>.</p>
            <div class="table"><a name="d6e1133"></a><p class="title"><b>Table&nbsp;1.4.&nbsp;Gateway node configuration sections</b></p><div class="table-contents">
                
                <table class="table" summary="Gateway node configuration sections" border="1"><colgroup><col class="c1"></colgroup><tbody><tr><td>
                                <p><a class="xref" href="#gateway-server-section-config" title="Gateway node: Server section">Gateway node: Server section</a></p>
                            </td></tr><tr><td>
                                <p><a class="xref" href="#gateway-logging-config" title="Gateway node: Logging section">Gateway node: Logging section</a></p>
                            </td></tr><tr><td>
                                <p><a class="xref" href="#gateway-gateway-section-config" title="Gateway node: Gateway section">Gateway node: Gateway
                    section</a></p>
                            </td></tr><tr><td>
                                <p><a class="xref" href="#gateway-pki-config" title="Gateway node: PKI section">Gateway node: PKI section</a></p>
                            </td></tr><tr><td>
                                <p><a class="xref" href="#gateway-management-config" title="Gateway node: Management section">Gateway node: Management section</a></p>
                            </td></tr><tr><td>
                                <p><a class="xref" href="#gateway-sphinx-config" title="Gateway node: SphinxGeometry section">Gateway node: SphinxGeometry section</a></p>
                            </td></tr><tr><td>
                                <p><a class="xref" href="#gateway-debug-config" title="Gateway node: Debug section">Gateway node: Debug section</a></p>
                            </td></tr></tbody></table>
            </div></div><br class="table-break">
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="gateway-server-section-config"></a>Gateway node: Server section</h4></div></div></div>
                
                <p>The <code class="code">Server</code> section configures mandatory basic parameters for each
                    server node.</p>
                <pre class="programlisting">[Server]
    Identifier = "gateway1"
    WireKEM = "xwing"
    PKISignatureScheme = "Ed25519"
    Addresses = ["127.0.0.1:30004"]
    OnlyAdvertiseAltAddresses = false
    MetricsAddress = "127.0.0.1:30005"
    DataDir = "/dirauth_mixnet/gateway1"
    IsGatewayNode = true
    IsServiceNode = false
    [Server.AltAddresses]
        TCP = ["localhost:30004"]</pre>
                
                
                <div class="simplesect"><div class="titlepage"><div><div><h5 class="title"><a name="d6e1171"></a></h5></div></div></div>
        
               
        <div class="informalexample"> 
            <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                    <p><span class="bold"><strong>Identifier</strong></span></p>
                    <p>Specifies the human-readable identifier for a node, and must be unique per mixnet. 
                        The identifier can be an FQDN but does not have to be.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                        <p><span class="bold"><strong>WireKEM</strong></span></p>
                        <p>WireKEM specifies the key encapsulation mechanism (KEM) scheme
                            for the <a class="ulink" href="https://eprint.iacr.org/2022/539" target="_top">PQ
                                Noise</a>-based wire protocol (link layer) that nodes use
                            to communicate with each other. PQ Noise is a post-quantum variation of
                            the <a class="ulink" href="https://noiseprotocol.org/" target="_top">Noise protocol
                                framework</a>, which algebraically transforms ECDH handshake
                            patterns into KEM encapsulate/decapsulate operations.</p>
                            
                            <p>This configuration option supports the optional use of
                            hybrid post-quantum cryptography to strengthen security. The following KEM
                            schemes are supported: </p><div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: circle; "><li class="listitem">
                                    <p><span class="bold"><strong>Classical:</strong></span> "x25519",
                                        "x448"</p>
                                     <div class="note" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Note"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Note]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/note.png"></td><th align="left">Note</th></tr><tr><td align="left" valign="top"><p>X25519 and X448 are actually non-interactive key-exchanges
                                            (NIKEs), not KEMs. Katzenpost uses
                                            a Hashed ElGamal cryptographic construction
                                            to convert them from NIKEs to KEMs.</p></td></tr></table></div>
                                </li><li class="listitem">
                                    <p><span class="bold"><strong>Hybrid post-quantum:</strong></span>
                                        "mlkem768", "sntrup4591761", "frodo640shake",
                                        "mceliece348864", "mceliece348864f", "mceliece460896",
                                        "mceliece460896f", "mceliece6688128", "mceliece6688128f",
                                        "mceliece6960119", "mceliece6960119f", "mceliece8192128",
                                        "mceliece8192128f", "xwing", "Kyber768-X25519",
                                        "MLKEM768-X25519", "MLKEM768-X448", "CTIDH511", "CTIDH512",
                                        "CTIDH1024", "CTIDH2048", "CTIDH512-X25519",
                                        "CTIDH512-X25519"</p>
                                </li></ul></div>						
                        <p>Type: string</p>
                        <p>Required: Yes</p>                    
                    </li><li class="listitem">
                    <p><span class="bold"><strong>PKISignatureScheme</strong></span></p>
                    <p>Specifies the cryptographic signature scheme that will be used by all
                        components of the mix network when interacting with the PKI system. Mix
                        nodes sign their descriptors using this signature scheme, and dirauth nodes
                        similarly sign PKI documents using the same scheme.</p>
                    <p>The following signature schemes are supported:</p>
                    <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: circle; "><li class="listitem">
                            <p><span class="bold"><strong>Classical:</strong></span>  "ed25519", "ed448"</p>
                        </li><li class="listitem">
                            <p><span class="bold"><strong>Hybrid post-quantum:</strong></span> "Ed25519
                                Sphincs+", "Ed448-Sphincs+", "Ed25519-Dilithium2",
                                "Ed448-Dilithium3" </p>
                        </li></ul></div>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>Addresses</strong></span></p>
                    <p>Specifies a list of one or more address URLs in a format that contains the
                        transport protocol, IP address, and port number that the server will bind to
                        for incoming connections. Katzenpost supports URLs with that start with
                        either "tcp://" or "quic://" such as: ["tcp://192.168.1.1:30001"] and
                        ["quic://192.168.1.1:40001"].</p>
                    <p>Type: []string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>BindAddresses</strong></span></p>
                    <p>If <span class="bold"><strong>true</strong></span>, allows setting of listener
                        addresses that the server will bind to and accept connections on. These
                        addresses are not advertised in the PKI.</p>
                    <p>Type: bool</p>
                    <p>Required: No</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>MetricsAddress</strong></span></p>
                    <p>Specifies the address/port to bind the Prometheus metrics endpoint
                        to.</p>
                    <p>Type: string</p>
                    <p>Required: No</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>DataDir</strong></span></p>
                    <p>Specifies the absolute path to a node's state directory. This is 
                        where persistence.db is written to disk and where a node stores its 
                        cryptographic key materials when started with the "-g" commmand-line 
                        option.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>IsGatewayNode</strong></span></p>
                    <p>If <span class="bold"><strong>true</strong></span>, the server is a gateway
                        node.</p>
                    <p>Type: bool</p>
                    <p>Required: No</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>IsServiceNode</strong></span></p>
                    <p>If <span class="bold"><strong>true</strong></span>, the server is a service
                        node.</p>
                    <p>Type: bool</p>
                    <p>Required: No</p>
                </li></ul></div>
            
        </div>
    </div>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="gateway-logging-config"></a>Gateway node: Logging section</h4></div></div></div>
                
                
                
                <div class="simplesect"><div class="titlepage"><div><div><h5 class="title"><a name="d6e1254"></a></h5></div></div></div>
        
        <div class="informalexample"> 
            <p>The <code class="code">Logging</code> configuration section controls logging behavior across Katzenpost.</p>
            <pre class="programlisting">[Logging]
                Disable = false
                File = "katzenpost.log"
                Level = "INFO"</pre>
            <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                    <p><span class="bold"><strong>Disable</strong></span></p>
                    <p>If <span class="bold"><strong>true</strong></span>, logging is disabled.</p>
                    <p>Type: bool</p>
                    <p>Required: No</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>File</strong></span></p>
                    <p>Specifies the log file. If omitted, <code class="code">stdout</code> is used.</p>
                    <p>An absolute or relative file path can be specified. A relative path is 
                    relative to the DataDir specified in the <code class="code">Server</code> section of the 
                    configuration.</p>
                    <p>Type: string</p>
                    <p>Required: No</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>Level</strong></span></p>
                    <p>Supported logging level values are ERROR | WARNING | NOTICE |INFO | DEBUG.</p>
                    <p>Type: string</p>
                    <p>Required: No</p>
                    <div class="warning" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Warning"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Warning]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/warning.png"></td><th align="left">Warning</th></tr><tr><td align="left" valign="top">
                        <p>The DEBUG log level is unsafe for
                            production use.</p>
                    </td></tr></table></div>                               
                </li></ul></div>   
        </div>
    </div>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="gateway-gateway-section-config"></a>Gateway node: Gateway
                    section</h4></div></div></div>
                
                <p></p>
                <p>The <code class="code">Gateway</code> section of the configuration is required for configuring a Gateway
                    node. The section must contain <code class="code">UserDB </code>and <code class="code">SpoolDB</code>
                    definitions. <a class="ulink" href="https://github.com/boltdb/bolt" target="_top">Bolt</a> is an
                    embedded database library for the Go programming language that Katzenpost
                    has used in the past for its user and spool databases. Because Katzenpost
                    currently persists data on Service nodes instead of Gateways, these databases
                    will probably be deprecated in favour of in-memory concurrency structures. In
                    the meantime, it remains necessary to configure a Gateway node as shown below,
                    only changing the file paths as needed: </p>
                <pre class="programlisting">[Gateway]
    [Gateway.UserDB]
        Backend = "bolt"
            [Gateway.UserDB.Bolt]
                UserDB = "/dirauth_mixnet/gateway1/users.db"
    [Gateway.SpoolDB]
        Backend = "bolt"
            [Gateway.SpoolDB.Bolt]
                SpoolDB = "/dirauth_mixnet/gateway1/spool.db"</pre>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="gateway-pki-config"></a>Gateway node: PKI section</h4></div></div></div>
                
                
                
                <div class="simplesect"><div class="titlepage"><div><div><h5 class="title"><a name="d6e1296"></a></h5></div></div></div>
             
        <div class="informalexample"> 
            <p>The <code class="code">PKI</code> section contains the directory authority configuration for a mix, gateway, or service node.</p>
            <pre class="programlisting">[PKI]
[PKI.dirauth]

    [[PKI.dirauth.Authorities]]
        Identifier = "auth1"
        IdentityPublicKey = """-----BEGIN ED25519 PUBLIC KEY-----
tqN6tpOVotHWXKCszVn2kS7vAZjQpvJjQF3Qz/Qwhyg=
-----END ED25519 PUBLIC KEY-----
"""
        PKISignatureScheme = "Ed25519"
        LinkPublicKey = """-----BEGIN XWING PUBLIC KEY-----
JnJ8ztQEIjAkKJcpuZvJAdkWjBim/5G5d8yoosEQHeGJeeBqNPdm2AitUbpiQPcd
tNCo9DxuC9Ieqmsfw0YpV6AtOOsaInA6QnHDYcuBfZcQL5MU4+t2TzpBZQYlrSED
hPCKrAG+8GEUl6akseG371WQzEtPpEWWCJCJOiS/VDFZT7eKrldlumN6gfiB84sR
...
arFh/WKwYJUj+aGBsFYSqGdzC6MdY4x/YyFe2ze0MJEjThQE91y1d/LCQ3Sb7Ri+
u6PBi3JU2qzlPEejDKwK0t5tMNEAkq8iNrpRTdD/hS0gR+ZIN8Z9QKh7Xf94FWG2
H+r8OaqImQhgHabrWRDyLg==
-----END XWING PUBLIC KEY-----
"""
        WireKEMScheme = "xwing"
        Addresses = ["127.0.0.1:30001"]

    [[PKI.dirauth.Authorities]]
        Identifier = "auth2"
        IdentityPublicKey = """-----BEGIN ED25519 PUBLIC KEY-----
O51Ty2WLu4C1ETMa29s03bMXV72gnjJfTfwLV++LVBI=
-----END ED25519 PUBLIC KEY-----	
"""
        PKISignatureScheme = "Ed25519"
        LinkPublicKey = """-----BEGIN XWING PUBLIC KEY-----
TtQkg2XKUnY602FFBaPJ+zpN0Twy20cwyyFxh7FNUjaXA9MAJXs0vUwFbJc6BjYv
f+olKnlIKFSmDvcF74U6w1F0ObugwTNKNxeYKPKhX4FiencUbRwkHoYHdtZdSctz
TKy08qKQyCAccqCRpdo6ZtYXPAU+2rthjYTOL7Zn+7SHUKCuJClcPnvEYjVcJxtZ
...
ubJIe5U4nMJbBkOqr7Kq6niaEkiLODa0tkpB8tKMYTMBdcYyHSXCzpo7U9sb6LAR
HktiTBDtRXviu2vbw7VRXhkMW2kjYZDtReQ5sAse04DvmD49zgTp1YxYW+wWFaL3
37X7/SNuLdHX4PHZXIWHBQ==
-----END XWING PUBLIC KEY-----	
"""
        WireKEMScheme = "xwing"
        Addresses = ["127.0.0.1:30002"]

    [[PKI.dirauth.Authorities]]
        Identifier = "auth3"
        IdentityPublicKey = """-----BEGIN ED25519 PUBLIC KEY-----
zQvydRYJq3npeLcg1NqIf+SswEKE5wFmiwNsI9Z1whQ=
-----END ED25519 PUBLIC KEY-----
"""
        PKISignatureScheme = "Ed25519"
        LinkPublicKey = """
-----BEGIN XWING PUBLIC KEY-----
OYK9FiC53xwZ1VST3jDOO4tR+cUMSVRSekmigZMChSjDCPZbKut8TblxtlUfc/yi
Ugorz4NIvYPMWUt3QPwS2UWq8/HMWXNGPUiAevg12+oV+jOJXaJeCfY24UekJnSw
TNcdGaFZFSR0FocFcPBBnrK1M2B8w8eEUKQIsXRDM3x/8aRIuDif+ve8rSwpgKeh
...
OdVD3yw7OOS8uPZLORGQFyJbHtVmFPVvwja4G/o2gntAoHUZ2LiJJakpVhhlSyrI
yuzvwwFtZVfWtNb5gAKZCyg0aduR3qgd7MPerRF+YopZk3OCRpC02YxfUZrHv398
FZWJFK0R8iU52CEUxVpXTA==
-----END XWING PUBLIC KEY-----	
"""
        WireKEMScheme = "xwing"
        Addresses = ["127.0.0.1:30003"]</pre>
            <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                    <p><span class="bold"><strong>Identifier</strong></span></p>
                    <p>Specifies the human-readable identifier for a node, which must be unique per mixnet. 
                    The identifier can be an FQDN but does not have to be.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>IdentityPublicKey</strong></span></p>
                    <p>String containing the node's public identity key in PEM format.
                            <code class="code">IdentityPublicKey</code> is the node's permanent identifier
                        and is used to verify cryptographic signatures produced by its private
                        identity key.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>PKISignatureScheme</strong></span></p>
                    <p>Specifies the cryptographic signature scheme that will be used by all
                        components of the mix network when interacting with the PKI system. Mix
                        nodes sign their descriptors using this signature scheme, and dirauth nodes
                        similarly sign PKI documents using the same scheme.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>LinkPublicKey</strong></span></p>
                    <p>String containing the peer's public link-layer key in PEM format.
                            <code class="code">LinkPublicKey</code> must match the specified
                            <code class="code">WireKEMScheme</code>.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>WireKEMScheme</strong></span></p>
                    <p>The name of the wire protocol key-encapsulation mechanism (KEM) to use.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>Addresses</strong></span></p>
                    <p>Specifies a list of one or more address URLs in a format that contains the
                        transport protocol, IP address, and port number that the server will bind to
                        for incoming connections. Katzenpost supports URLs that start with
                        either "tcp://" or "quic://" such as: ["tcp://192.168.1.1:30001"] and
                        ["quic://192.168.1.1:40001"].</p>
                    <p>Type: []string</p>
                    <p>Required: Yes</p>
                </li></ul></div>                            
        </div>
    </div>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="gateway-management-config"></a>Gateway node: Management section</h4></div></div></div>
                
                
                
                <div class="simplesect"><div class="titlepage"><div><div><h5 class="title"><a name="d6e1344"></a></h5></div></div></div>
        
           <div class="informalexample"> 
           <p>The <code class="code">Management</code> section specifies 
               connectivity information for the Katzenpost control protocol which can be used to make run-time 
               configuration changes. A configuration resembles the following:</p>
           <pre class="programlisting">[Management]
   Enable = false
   Path = "/dirauth_mixnet/mix1/management_sock"</pre>
           <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                   <p><span class="bold"><strong>Enable</strong></span></p>
                   <p>If <span class="bold"><strong>true</strong></span>, the management interface is
                        enabled.</p>
                   <p>Type: bool</p>
                   <p>Required: No</p>
               </li><li class="listitem">
                   <p><span class="bold"><strong>Path</strong></span></p>
                   <p>Specifies the path to the management interface socket. If left empty, then <code class="code">management_sock</code> 
                       is located in the configuration's defined <code class="code">DataDir</code>&gt;.</p>
                   <p>Type: string</p>
                   <p>Required: No</p>
               </li></ul></div>
       </div>
    </div>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="gateway-sphinx-config"></a>Gateway node: SphinxGeometry section</h4></div></div></div>
                
                
                
                <div class="simplesect"><div class="titlepage"><div><div><h5 class="title"><a name="d6e1368"></a></h5></div></div></div>
        
        <div class="informalexample">        
            <p>The <code class="code">SphinxGeometry</code> section defines parameters for the Sphinx
                encrypted nested-packet format used internally by Katzenpost. 
                </p><div class="warning" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Warning"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Warning]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/warning.png"></td><th align="left">Warning</th></tr><tr><td align="left" valign="top"><p>The values in the <code class="code">SphinxGeometry</code> configuration section must
                        be programmatically generated by <span class="command"><strong>gensphinx</strong></span>. Many of the
                        parameters are interdependent and cannot be individually modified. Do not
                        modify the these values by hand.</p></td></tr></table></div>
            <p>The settings in this section are generated by the <span class="command"><strong>gensphinx</strong></span>
                utility, which computes the Sphinx geometry based on the following user-supplied
                directives:</p>
            <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                    <p>The number of  mix node layers (not counting gateway and service
                        nodes)</p>
                </li><li class="listitem">
                    <p>The length of the application-usable packet payload</p>
                </li><li class="listitem">
                    <p>The selected NIKE or KEM scheme</p>
                </li></ul></div>
            <p>The output in TOML should then be pasted unchanged into the node's configuration
                file, as shown below. For more information, see <a class="xref" href="#gensphinx" title="Chapter&nbsp;4.&nbsp;Appendix: Using gensphinx">Chapter&nbsp;4, <i>Appendix: Using <span class="emphasis"><em>gensphinx</em></span></i></a>.</p>
            <pre class="programlisting">[SphinxGeometry]
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
                KEMName = ""</pre>
            <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                    <p><span class="bold"><strong>PacketLength</strong></span></p>
                    <p>The length of a Sphinx packet in bytes.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>NrHops</strong></span></p>
                    <p>The number of hops a Sphinx packet takes through the mixnet. Because
                        packet headers hold destination information for each hop, the size of the
                        header increases linearly with the number of hops.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>HeaderLength</strong></span></p>
                    <p>The total length of the Sphinx packet header in bytes.</p>                   
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>RoutingInfoLength</strong></span></p>
                    <p>The total length of the routing information portion of the Sphinx packet
                        header.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>PerHopRoutingInfoLength</strong></span></p>
                    <p>The length of the per-hop routing information in the Sphinx packet
                        header.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>SURBLength</strong></span></p>
                    <p>The length of a single-use reply block (SURB).</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>SphinxPlaintextHeaderLength</strong></span></p>
                    <p>The length of the plaintext Sphinx packet header.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>PayloadTagLength</strong></span></p>
                    <p>The length of the payload tag.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>ForwardPayloadLength</strong></span></p>
                    <p>The total size of the payload.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>UserForwardPayloadLength</strong></span></p>
                    <p>The size of the usable payload.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>NextNodeHopLength</strong></span></p>
                    <p>The <code class="code">NextNodeHopLength</code> is derived from the largest routing-information 
                        block that we expect to encounter. Other packets have 
                        <code class="code">NextNodeHop</code> + <code class="code">NodeDelay</code> sections, or a <code class="code">Recipient</code> section, both of which
                        are shorter.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>SPRPKeyMaterialLength</strong></span></p>
                    <p>The length of the strong pseudo-random permutation (SPRP) key.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>NIKEName</strong></span></p>
                    <p>The name of the non-interactive key exchange (NIKE) scheme used by Sphinx
                        packets.</p>
                    <p><code class="code">NIKEName</code> and <code class="code">KEMName</code> are mutually
                        exclusive.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>KEMName</strong></span></p>
                    <p>The name of the key encapsulation mechanism (KEM) used by Sphinx
                        packets.</p>
                    <p><code class="code">NIKEName</code> and <code class="code">KEMName</code> are mutually exclusive.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li></ul></div>            
        </div>
    </div>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="gateway-debug-config"></a>Gateway node: Debug section</h4></div></div></div>
                
                
                
                <div class="simplesect"><div class="titlepage"><div><div><h5 class="title"><a name="d6e1486"></a></h5></div></div></div>
             
        <div class="informalexample">    
            <p>The <code class="code">Debug</code> section is the Katzenpost server debug configuration
                for advanced tuning.</p>   
            <pre class="programlisting">[Debug]
                NumSphinxWorkers = 16
                NumServiceWorkers = 3
                NumGatewayWorkers = 3
                NumKaetzchenWorkers = 3
                SchedulerExternalMemoryQueue = false
                SchedulerQueueSize = 0
                SchedulerMaxBurst = 16
                UnwrapDelay = 250
                GatewayDelay = 500
                ServiceDelay = 500
                KaetzchenDelay = 750
                SchedulerSlack = 150
                SendSlack = 50
                DecoySlack = 15000
                ConnectTimeout = 60000
                HandshakeTimeout = 30000
                ReauthInterval = 30000
                SendDecoyTraffic = false
                DisableRateLimit = false
                GenerateOnly = false</pre>
                <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                        <p><span class="bold"><strong>NumSphinxWorkers</strong></span></p>
                        <p>Specifies the number of worker instances to use for inbound Sphinx
                            packet processing.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>NumProviderWorkers</strong></span></p>
                        <p>Specifies the number of worker instances to use for provider specific
                            packet processing.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>NumKaetzchenWorkers</strong></span></p>
                        <p>Specifies the number of worker instances to use for Kaetzchen-specific
                        packet processing.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>SchedulerExternalMemoryQueue</strong></span></p>
                        <p>If <span class="bold"><strong>true</strong></span>, the experimental disk-backed external memory 
                            queue is enabled.</p>
                        <p>Type: bool</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>SchedulerQueueSize</strong></span></p>
                        <p>Specifies the maximum scheduler queue size before random entries will
                        start getting dropped. A value less than or equal to zero is treated as
                        unlimited.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>SchedulerMaxBurst</strong></span></p>
                        <p>Specifies the maximum number of packets that will be dispatched per
                            scheduler wakeup event.</p>
                        <p>Type: </p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>UnwrapDelay</strong></span></p>
                        <p>Specifies the maximum unwrap delay due to queueing in
                            milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>GatewayDelay</strong></span></p>
                        <p>Specifies the maximum gateway node worker delay due to queueing in milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>ServiceDelay</strong></span></p>
                        <p>Specifies the maximum provider delay due to queueing in
                            milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p> 
                    </li><li class="listitem">
                        <p><span class="bold"><strong>KaetzchenDelay</strong></span></p>
                        <p>Specifies the maximum kaetzchen delay due to queueing in
                            milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>SchedulerSlack</strong></span></p>
                        <p>Specifies the maximum scheduler slack due to queueing and/or
                            processing in milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>SendSlack</strong></span></p>
                        <p>Specifies the maximum send-queue slack due to queueing and/or
                            congestion in milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>DecoySlack</strong></span></p>
                        <p>Specifies the maximum decoy sweep slack due to external
                            delays such as latency before a loop decoy packet will be considered
                            lost.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>ConnectTimeout</strong></span></p>
                        <p>Specifies the maximum time a connection can take to establish a
                            TCP/IP connection in milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>HandshakeTimeout</strong></span></p>
                        <p>Specifies the maximum time a connection can take for a link-protocol
                            handshake in milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>ReauthInterval</strong></span></p>
                        <p>Specifies the interval at which a connection will be reauthenticated
                            in milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>SendDecoyTraffic</strong></span></p>
                        <p>If <span class="bold"><strong>true</strong></span>, decoy traffic is enabled. 
                            This parameter is experimental and untuned, 
                            and is disabled by default.</p>
                        <div class="note" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Note"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Note]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/note.png"></td><th align="left">Note</th></tr><tr><td align="left" valign="top">
                            <p>This option will be removed once decoy traffic is fully implemented.</p>
                        </td></tr></table></div>
                        <p>Type: bool</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>DisableRateLimit</strong></span></p>
                        <p>If <span class="bold"><strong>true</strong></span>, the per-client rate limiter is disabled.</p>
                        <div class="note" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Note"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Note]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/note.png"></td><th align="left">Note</th></tr><tr><td align="left" valign="top">
                            <p>This option should only be used for testing.</p>
                        </td></tr></table></div>
                        <p>Type: bool</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>GenerateOnly</strong></span></p>
                        <p>If <span class="bold"><strong>true</strong></span>, the server immediately halts
                        and cleans up after long-term key generation.</p>
                        <p>Type: bool</p>
                        <p>Required: No</p>
                    </li></ul></div>
        </div> 
    </div>
            </div>
        </div>
        <div class="section"><div class="titlepage"><div><div><h3 class="title"><a name="service-config"></a>Configuring service nodes</h3></div></div></div>
            
            <p>The following configuration is drawn from the reference implementation in
                    <code class="filename">katzenpost/docker/dirauth_mixnet/servicenode1/authority.toml</code>.
                In a real-world mixnet, the component hosts would not be sharing a single IP
                address. For more information about the test mixnet, see <span class="bold"><strong><a class="xref" href="#container" title="Chapter&nbsp;2.&nbsp;Using the Katzenpost Docker test network">Using the Katzenpost Docker test network</a></strong></span>.</p>
            <div class="table"><a name="d6e1621"></a><p class="title"><b>Table&nbsp;1.5.&nbsp;Mix node configuration sections</b></p><div class="table-contents">
                
                <table class="table" summary="Mix node configuration sections" border="1"><colgroup><col class="c1"></colgroup><tbody><tr><td>
                                <p><a class="xref" href="#service-server-section-config" title="Service node: Server section">Service node: Server section</a></p>
                            </td></tr><tr><td>
                                <p><a class="xref" href="#service-logging-config" title="Service node: Logging section">Service node: Logging section</a></p>
                            </td></tr><tr><td>
                                <p><a class="xref" href="#service-servicenode-section-config" title="Service node: ServiceNode section">Service node: ServiceNode
                    section</a></p>
                            </td></tr><tr><td>
                                <p><a class="xref" href="#service-pki-config" title="Service node: PKI section">Service node: PKI section</a></p>
                            </td></tr><tr><td>
                                <p><a class="xref" href="#service-management-config" title="Service node: Management section">Service node: Management section</a></p>
                            </td></tr><tr><td>
                                <p><a class="xref" href="#service-sphinx-config" title="Service node: SphinxGeometry section">Service node: SphinxGeometry section</a></p>
                            </td></tr><tr><td>
                                <p><a class="xref" href="#service-debug-config" title="Service node: Debug section">Service node: Debug section</a></p>
                            </td></tr></tbody></table>
            </div></div><br class="table-break">
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="service-server-section-config"></a>Service node: Server section</h4></div></div></div>
                
                <p>The <code class="code">Server</code> section configures mandatory basic parameters for each
                    server node.</p>
                <pre class="programlisting">[Server]
    Identifier = "servicenode1"
    WireKEM = "xwing"
    PKISignatureScheme = "Ed25519"
    Addresses = ["127.0.0.1:30006"]
    OnlyAdvertiseAltAddresses = false
    MetricsAddress = "127.0.0.1:30007"
    DataDir = "/dirauth_mixnet/servicenode1"
    IsGatewayNode = false
    IsServiceNode = true
    [Server.AltAddresses]</pre>
                
                
                <div class="simplesect"><div class="titlepage"><div><div><h5 class="title"><a name="d6e1659"></a></h5></div></div></div>
        
               
        <div class="informalexample"> 
            <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                    <p><span class="bold"><strong>Identifier</strong></span></p>
                    <p>Specifies the human-readable identifier for a node, and must be unique per mixnet. 
                        The identifier can be an FQDN but does not have to be.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                        <p><span class="bold"><strong>WireKEM</strong></span></p>
                        <p>WireKEM specifies the key encapsulation mechanism (KEM) scheme
                            for the <a class="ulink" href="https://eprint.iacr.org/2022/539" target="_top">PQ
                                Noise</a>-based wire protocol (link layer) that nodes use
                            to communicate with each other. PQ Noise is a post-quantum variation of
                            the <a class="ulink" href="https://noiseprotocol.org/" target="_top">Noise protocol
                                framework</a>, which algebraically transforms ECDH handshake
                            patterns into KEM encapsulate/decapsulate operations.</p>
                            
                            <p>This configuration option supports the optional use of
                            hybrid post-quantum cryptography to strengthen security. The following KEM
                            schemes are supported: </p><div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: circle; "><li class="listitem">
                                    <p><span class="bold"><strong>Classical:</strong></span> "x25519",
                                        "x448"</p>
                                     <div class="note" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Note"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Note]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/note.png"></td><th align="left">Note</th></tr><tr><td align="left" valign="top"><p>X25519 and X448 are actually non-interactive key-exchanges
                                            (NIKEs), not KEMs. Katzenpost uses
                                            a Hashed ElGamal cryptographic construction
                                            to convert them from NIKEs to KEMs.</p></td></tr></table></div>
                                </li><li class="listitem">
                                    <p><span class="bold"><strong>Hybrid post-quantum:</strong></span>
                                        "mlkem768", "sntrup4591761", "frodo640shake",
                                        "mceliece348864", "mceliece348864f", "mceliece460896",
                                        "mceliece460896f", "mceliece6688128", "mceliece6688128f",
                                        "mceliece6960119", "mceliece6960119f", "mceliece8192128",
                                        "mceliece8192128f", "xwing", "Kyber768-X25519",
                                        "MLKEM768-X25519", "MLKEM768-X448", "CTIDH511", "CTIDH512",
                                        "CTIDH1024", "CTIDH2048", "CTIDH512-X25519",
                                        "CTIDH512-X25519"</p>
                                </li></ul></div>						
                        <p>Type: string</p>
                        <p>Required: Yes</p>                    
                    </li><li class="listitem">
                    <p><span class="bold"><strong>PKISignatureScheme</strong></span></p>
                    <p>Specifies the cryptographic signature scheme that will be used by all
                        components of the mix network when interacting with the PKI system. Mix
                        nodes sign their descriptors using this signature scheme, and dirauth nodes
                        similarly sign PKI documents using the same scheme.</p>
                    <p>The following signature schemes are supported:</p>
                    <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: circle; "><li class="listitem">
                            <p><span class="bold"><strong>Classical:</strong></span>  "ed25519", "ed448"</p>
                        </li><li class="listitem">
                            <p><span class="bold"><strong>Hybrid post-quantum:</strong></span> "Ed25519
                                Sphincs+", "Ed448-Sphincs+", "Ed25519-Dilithium2",
                                "Ed448-Dilithium3" </p>
                        </li></ul></div>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>Addresses</strong></span></p>
                    <p>Specifies a list of one or more address URLs in a format that contains the
                        transport protocol, IP address, and port number that the server will bind to
                        for incoming connections. Katzenpost supports URLs with that start with
                        either "tcp://" or "quic://" such as: ["tcp://192.168.1.1:30001"] and
                        ["quic://192.168.1.1:40001"].</p>
                    <p>Type: []string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>BindAddresses</strong></span></p>
                    <p>If <span class="bold"><strong>true</strong></span>, allows setting of listener
                        addresses that the server will bind to and accept connections on. These
                        addresses are not advertised in the PKI.</p>
                    <p>Type: bool</p>
                    <p>Required: No</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>MetricsAddress</strong></span></p>
                    <p>Specifies the address/port to bind the Prometheus metrics endpoint
                        to.</p>
                    <p>Type: string</p>
                    <p>Required: No</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>DataDir</strong></span></p>
                    <p>Specifies the absolute path to a node's state directory. This is 
                        where persistence.db is written to disk and where a node stores its 
                        cryptographic key materials when started with the "-g" commmand-line 
                        option.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>IsGatewayNode</strong></span></p>
                    <p>If <span class="bold"><strong>true</strong></span>, the server is a gateway
                        node.</p>
                    <p>Type: bool</p>
                    <p>Required: No</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>IsServiceNode</strong></span></p>
                    <p>If <span class="bold"><strong>true</strong></span>, the server is a service
                        node.</p>
                    <p>Type: bool</p>
                    <p>Required: No</p>
                </li></ul></div>
            
        </div>
    </div>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="service-logging-config"></a>Service node: Logging section</h4></div></div></div>
                
                
                
                <div class="simplesect"><div class="titlepage"><div><div><h5 class="title"><a name="d6e1742"></a></h5></div></div></div>
        
        <div class="informalexample"> 
            <p>The <code class="code">Logging</code> configuration section controls logging behavior across Katzenpost.</p>
            <pre class="programlisting">[Logging]
                Disable = false
                File = "katzenpost.log"
                Level = "INFO"</pre>
            <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                    <p><span class="bold"><strong>Disable</strong></span></p>
                    <p>If <span class="bold"><strong>true</strong></span>, logging is disabled.</p>
                    <p>Type: bool</p>
                    <p>Required: No</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>File</strong></span></p>
                    <p>Specifies the log file. If omitted, <code class="code">stdout</code> is used.</p>
                    <p>An absolute or relative file path can be specified. A relative path is 
                    relative to the DataDir specified in the <code class="code">Server</code> section of the 
                    configuration.</p>
                    <p>Type: string</p>
                    <p>Required: No</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>Level</strong></span></p>
                    <p>Supported logging level values are ERROR | WARNING | NOTICE |INFO | DEBUG.</p>
                    <p>Type: string</p>
                    <p>Required: No</p>
                    <div class="warning" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Warning"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Warning]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/warning.png"></td><th align="left">Warning</th></tr><tr><td align="left" valign="top">
                        <p>The DEBUG log level is unsafe for
                            production use.</p>
                    </td></tr></table></div>                               
                </li></ul></div>   
        </div>
    </div>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="service-servicenode-section-config"></a>Service node: ServiceNode
                    section</h4></div></div></div>
                
                <p>The <code class="code">ServiceNode</code> section contains configurations for each network
                    service that Katzenpost supports. </p>
                <p>Services, termed <a class="ulink" href="https://github.com/katzenpost/katzenpost/blob/main/docs/Specificatons/pdf/kaetzchen.pdf" target="_top">Kaetzchen</a>, can be divided into built-in and external services.
                    External services are provided through the <a class="ulink" href="https://pkg.go.dev/github.com/katzenpost/katzenpost@v0.0.35/server/cborplugin#ResponseFactory" target="_top">CBORPlugin</a>, a Go programming language implementation of the <a class="ulink" href="https://datatracker.ietf.org/doc/html/rfc8949" target="_top">Concise Binary Object
                        Representation (CBOR)</a>, a binary data serialization format. While
                    native services need simply to be activated, external services are invoked by a
                    separate command and connected to the mixnet over a Unix socket. The plugin
                    allows mixnet services to be added in any programming language.</p>
                <pre class="programlisting">[ServiceNode]
                    
    [[ServiceNode.Kaetzchen]]
        Capability = "echo"
        Endpoint = "+echo"
        Disable = false
    
    [[ServiceNode.CBORPluginKaetzchen]]
        Capability = "spool"
        Endpoint = "+spool"
        Command = "/dirauth_mixnet/memspool.alpine"
        MaxConcurrency = 1
        Disable = false
        [ServiceNode.CBORPluginKaetzchen.Config]
            data_store = "/dirauth_mixnet/servicenode1/memspool.storage"
            log_dir = "/dirauth_mixnet/servicenode1"
    
    [[ServiceNode.CBORPluginKaetzchen]]
        Capability = "pigeonhole"
        Endpoint = "+pigeonhole"
        Command = "/dirauth_mixnet/pigeonhole.alpine"
        MaxConcurrency = 1
        Disable = false
        [ServiceNode.CBORPluginKaetzchen.Config]
            db = "/dirauth_mixnet/servicenode1/map.storage"
            log_dir = "/dirauth_mixnet/servicenode1"
    
    [[ServiceNode.CBORPluginKaetzchen]]
        Capability = "panda"
        Endpoint = "+panda"
        Command = "/dirauth_mixnet/panda_server.alpine"
        MaxConcurrency = 1
        Disable = false
        [ServiceNode.CBORPluginKaetzchen.Config]
            fileStore = "/dirauth_mixnet/servicenode1/panda.storage"
            log_dir = "/dirauth_mixnet/servicenode1"
            log_level = "INFO"
    
    [[ServiceNode.CBORPluginKaetzchen]]
        Capability = "http"
        Endpoint = "+http"
        Command = "/dirauth_mixnet/proxy_server.alpine"
        MaxConcurrency = 1
        Disable = false
        [ServiceNode.CBORPluginKaetzchen.Config]
            host = "localhost:4242"
            log_dir = "/dirauth_mixnet/servicenode1"
            log_level = "DEBUG"</pre>
                <p><span class="bold"><strong>Common parameters:</strong></span></p>
                <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                        <p><span class="bold"><strong>Capability</strong></span></p>
                        <p>Specifies the protocol capability exposed by the agent.</p>
                        <p>Type: string</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>Endpoint</strong></span></p>
                        <p>Specifies the provider-side Endpoint where the agent will accept
                            requests. While not required by the specification, this server only
                            supports Endpoints that are
                            lower-case
                            local parts of an email address.</p>
                        <p>Type: string</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>Command</strong></span></p>
                        <p>Specifies the full path to the external plugin program that implements
                            this <code class="code">Kaetzchen</code> service.</p>
                        <p>Type: string</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>MaxConcurrency</strong></span></p>
                        <p>Specifies the number of worker goroutines to start for this
                            service.</p>
                        <p>Type: int</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>Config</strong></span></p>
                        <p>Specifies extra per-agent arguments to be passed to the agent's
                            initialization routine.</p>
                        <p>Type: map[string]interface{}</p>
                        <p>Required: Yes</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>Disable</strong></span></p>
                        <p>If <span class="bold"><strong>true</strong></span>, disables a configured
                            agent.</p>
                        <p>Type: bool</p>
                        <p>Required: No</p>
                    </li></ul></div>
                <p><span class="bold"><strong>Per-service parameters:</strong></span></p>
                <p>
                    </p><div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                            <p><span class="bold"><strong>echo</strong></span></p>
                            <p>The internal <code class="code">echo</code> service must be enabled on every
                                service node of a production mixnet for decoy traffic to work
                                properly. </p>
                        </li><li class="listitem">
                            <p><span class="bold"><strong>spool</strong></span></p>
                            <p>The <code class="code">spool</code> service supports the <code class="code">catshadow</code>
                                storage protocol,
                                which
                                is required by the Katzen chat client. The
                                example configuration above shows spool enabled with the setting:</p><pre class="programlisting">Disable = false</pre><div class="note" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Note"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Note]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/note.png"></td><th align="left">Note</th></tr><tr><td align="left" valign="top">
                                    <p><code class="code">Spool</code>, properly <code class="code">memspool</code>, should
                                        not be confused with the spool database on gateway
                                        nodes.</p>
                                </td></tr></table></div>
                            <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: circle; "><li class="listitem">
                                    <p><span class="bold"><strong>data_store</strong></span></p>
                                    <p>Specifies the full path to the service database
                                        file.</p>
                                    <p>Type: string</p>
                                    <p>Required: Yes</p>
                                </li><li class="listitem">
                                    <p><span class="bold"><strong>log_dir</strong></span></p>
                                    <p>Specifies the path to the node's log directory.</p>
                                    <p>Type: string</p>
                                    <p>Required: Yes</p>
                                </li></ul></div>
                        </li><li class="listitem">
                            <p><span class="bold"><strong>pigeonhole</strong></span></p>
                            <p>The <code class="code">pigeonhole</code> courier service supports the
                                Blinding-and-Capability scheme (BACAP)-based unlinkable messaging
                                protocols detailed in <span class="bold"><strong>Place-holder for research paper link</strong></span>. Most of our future protocols
                                will use the <code class="code">pigeonhole</code> courier service.</p>
                            <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: circle; "><li class="listitem">
                                    <p><span class="bold"><strong>db</strong></span></p>
                                    <p>Specifies the full path to the service database
                                        file.</p>
                                    <p>Type: string</p>
                                    <p>Required: Yes</p>
                                </li><li class="listitem">
                                    <p><span class="bold"><strong>log_dir</strong></span></p>
                                    <p>Specifies the path to the node's log directory.</p>
                                    <p>Type: string</p>
                                    <p>Required: Yes</p>
                                </li></ul></div>
                        </li><li class="listitem">
                            <p><span class="bold"><strong>panda</strong></span></p>
                            <p>The <code class="code">panda</code> storage and authentication service
                                currently does not work properly.</p>
                            <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: circle; "><li class="listitem">
                                    <p><span class="bold"><strong>fileStore</strong></span></p>
                                    <p>Specifies the full path to the service database
                                        file.</p>
                                    <p>Type: string</p>
                                    <p>Required: Yes</p>
                                </li><li class="listitem">
                                    <p><span class="bold"><strong>log_dir</strong></span></p>
                                    <p>Specifies the path to the node's log directory.</p>
                                    <p>Type: string</p>
                                    <p>Required: Yes</p>
                                </li><li class="listitem">
                                    <p><span class="bold"><strong>log_level</strong></span></p>
                                    <p>Supported values are ERROR | WARNING | NOTICE |INFO |
                                        DEBUG.</p>
                                    <div class="warning" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Warning"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Warning]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/warning.png"></td><th align="left">Warning</th></tr><tr><td align="left" valign="top">
                                        <p>The DEBUG log level is unsafe for production
                                            use.</p>
                                    </td></tr></table></div>
                                    <p>Type: string</p>
                                    <p>Required: Yes</p>
                                    <p>Required: Yes</p>
                                </li></ul></div>
                        </li><li class="listitem">
                            <p><span class="bold"><strong>http</strong></span></p>
                            <p>The <code class="code">http</code> service is completely optional, but allows
                                the mixnet to be used as an HTTP proxy. This may be useful for
                                integrating with existing software systems.</p>
                            <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: circle; "><li class="listitem">
                                    <p><span class="bold"><strong>host</strong></span></p>
                                    <p>The host name and TCP port of the service.</p>
                                    <p>Type: string</p>
                                    <p>Required: Yes</p>
                                </li><li class="listitem">
                                    <p><span class="bold"><strong>log_dir</strong></span></p>
                                    <p>Specifies the path to the node's log directory.</p>
                                    <p>Type: string</p>
                                    <p>Required: Yes</p>
                                </li><li class="listitem">
                                    <p><span class="bold"><strong>log_level</strong></span></p>
                                    <p>Supported values are ERROR | WARNING | NOTICE |INFO |
                                        DEBUG.</p>
                                    <p>Type: string</p>
                                    <p>Required: Yes</p>
                                    <p>Required: Yes</p>
                                    <div class="warning" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Warning"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Warning]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/warning.png"></td><th align="left">Warning</th></tr><tr><td align="left" valign="top">
                                        <p>The DEBUG log level is unsafe for production
                                            use.</p>
                                    </td></tr></table></div>
                                    <p>Type: string</p>
                                    <p>Required: Yes</p>
                                </li></ul></div>
                        </li></ul></div><p>
                </p>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="service-pki-config"></a>Service node: PKI section</h4></div></div></div>
                
                
                
                <div class="simplesect"><div class="titlepage"><div><div><h5 class="title"><a name="d6e1934"></a></h5></div></div></div>
             
        <div class="informalexample"> 
            <p>The <code class="code">PKI</code> section contains the directory authority configuration for a mix, gateway, or service node.</p>
            <pre class="programlisting">[PKI]
[PKI.dirauth]

    [[PKI.dirauth.Authorities]]
        Identifier = "auth1"
        IdentityPublicKey = """-----BEGIN ED25519 PUBLIC KEY-----
tqN6tpOVotHWXKCszVn2kS7vAZjQpvJjQF3Qz/Qwhyg=
-----END ED25519 PUBLIC KEY-----
"""
        PKISignatureScheme = "Ed25519"
        LinkPublicKey = """-----BEGIN XWING PUBLIC KEY-----
JnJ8ztQEIjAkKJcpuZvJAdkWjBim/5G5d8yoosEQHeGJeeBqNPdm2AitUbpiQPcd
tNCo9DxuC9Ieqmsfw0YpV6AtOOsaInA6QnHDYcuBfZcQL5MU4+t2TzpBZQYlrSED
hPCKrAG+8GEUl6akseG371WQzEtPpEWWCJCJOiS/VDFZT7eKrldlumN6gfiB84sR
...
arFh/WKwYJUj+aGBsFYSqGdzC6MdY4x/YyFe2ze0MJEjThQE91y1d/LCQ3Sb7Ri+
u6PBi3JU2qzlPEejDKwK0t5tMNEAkq8iNrpRTdD/hS0gR+ZIN8Z9QKh7Xf94FWG2
H+r8OaqImQhgHabrWRDyLg==
-----END XWING PUBLIC KEY-----
"""
        WireKEMScheme = "xwing"
        Addresses = ["127.0.0.1:30001"]

    [[PKI.dirauth.Authorities]]
        Identifier = "auth2"
        IdentityPublicKey = """-----BEGIN ED25519 PUBLIC KEY-----
O51Ty2WLu4C1ETMa29s03bMXV72gnjJfTfwLV++LVBI=
-----END ED25519 PUBLIC KEY-----	
"""
        PKISignatureScheme = "Ed25519"
        LinkPublicKey = """-----BEGIN XWING PUBLIC KEY-----
TtQkg2XKUnY602FFBaPJ+zpN0Twy20cwyyFxh7FNUjaXA9MAJXs0vUwFbJc6BjYv
f+olKnlIKFSmDvcF74U6w1F0ObugwTNKNxeYKPKhX4FiencUbRwkHoYHdtZdSctz
TKy08qKQyCAccqCRpdo6ZtYXPAU+2rthjYTOL7Zn+7SHUKCuJClcPnvEYjVcJxtZ
...
ubJIe5U4nMJbBkOqr7Kq6niaEkiLODa0tkpB8tKMYTMBdcYyHSXCzpo7U9sb6LAR
HktiTBDtRXviu2vbw7VRXhkMW2kjYZDtReQ5sAse04DvmD49zgTp1YxYW+wWFaL3
37X7/SNuLdHX4PHZXIWHBQ==
-----END XWING PUBLIC KEY-----	
"""
        WireKEMScheme = "xwing"
        Addresses = ["127.0.0.1:30002"]

    [[PKI.dirauth.Authorities]]
        Identifier = "auth3"
        IdentityPublicKey = """-----BEGIN ED25519 PUBLIC KEY-----
zQvydRYJq3npeLcg1NqIf+SswEKE5wFmiwNsI9Z1whQ=
-----END ED25519 PUBLIC KEY-----
"""
        PKISignatureScheme = "Ed25519"
        LinkPublicKey = """
-----BEGIN XWING PUBLIC KEY-----
OYK9FiC53xwZ1VST3jDOO4tR+cUMSVRSekmigZMChSjDCPZbKut8TblxtlUfc/yi
Ugorz4NIvYPMWUt3QPwS2UWq8/HMWXNGPUiAevg12+oV+jOJXaJeCfY24UekJnSw
TNcdGaFZFSR0FocFcPBBnrK1M2B8w8eEUKQIsXRDM3x/8aRIuDif+ve8rSwpgKeh
...
OdVD3yw7OOS8uPZLORGQFyJbHtVmFPVvwja4G/o2gntAoHUZ2LiJJakpVhhlSyrI
yuzvwwFtZVfWtNb5gAKZCyg0aduR3qgd7MPerRF+YopZk3OCRpC02YxfUZrHv398
FZWJFK0R8iU52CEUxVpXTA==
-----END XWING PUBLIC KEY-----	
"""
        WireKEMScheme = "xwing"
        Addresses = ["127.0.0.1:30003"]</pre>
            <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                    <p><span class="bold"><strong>Identifier</strong></span></p>
                    <p>Specifies the human-readable identifier for a node, which must be unique per mixnet. 
                    The identifier can be an FQDN but does not have to be.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>IdentityPublicKey</strong></span></p>
                    <p>String containing the node's public identity key in PEM format.
                            <code class="code">IdentityPublicKey</code> is the node's permanent identifier
                        and is used to verify cryptographic signatures produced by its private
                        identity key.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>PKISignatureScheme</strong></span></p>
                    <p>Specifies the cryptographic signature scheme that will be used by all
                        components of the mix network when interacting with the PKI system. Mix
                        nodes sign their descriptors using this signature scheme, and dirauth nodes
                        similarly sign PKI documents using the same scheme.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>LinkPublicKey</strong></span></p>
                    <p>String containing the peer's public link-layer key in PEM format.
                            <code class="code">LinkPublicKey</code> must match the specified
                            <code class="code">WireKEMScheme</code>.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>WireKEMScheme</strong></span></p>
                    <p>The name of the wire protocol key-encapsulation mechanism (KEM) to use.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>Addresses</strong></span></p>
                    <p>Specifies a list of one or more address URLs in a format that contains the
                        transport protocol, IP address, and port number that the server will bind to
                        for incoming connections. Katzenpost supports URLs that start with
                        either "tcp://" or "quic://" such as: ["tcp://192.168.1.1:30001"] and
                        ["quic://192.168.1.1:40001"].</p>
                    <p>Type: []string</p>
                    <p>Required: Yes</p>
                </li></ul></div>                            
        </div>
    </div>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="service-management-config"></a>Service node: Management section</h4></div></div></div>
                
                
                
                <div class="simplesect"><div class="titlepage"><div><div><h5 class="title"><a name="d6e1982"></a></h5></div></div></div>
        
           <div class="informalexample"> 
           <p>The <code class="code">Management</code> section specifies 
               connectivity information for the Katzenpost control protocol which can be used to make run-time 
               configuration changes. A configuration resembles the following:</p>
           <pre class="programlisting">[Management]
   Enable = false
   Path = "/dirauth_mixnet/mix1/management_sock"</pre>
           <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                   <p><span class="bold"><strong>Enable</strong></span></p>
                   <p>If <span class="bold"><strong>true</strong></span>, the management interface is
                        enabled.</p>
                   <p>Type: bool</p>
                   <p>Required: No</p>
               </li><li class="listitem">
                   <p><span class="bold"><strong>Path</strong></span></p>
                   <p>Specifies the path to the management interface socket. If left empty, then <code class="code">management_sock</code> 
                       is located in the configuration's defined <code class="code">DataDir</code>&gt;.</p>
                   <p>Type: string</p>
                   <p>Required: No</p>
               </li></ul></div>
       </div>
    </div>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="service-sphinx-config"></a>Service node: SphinxGeometry section</h4></div></div></div>
                
                
                
                <div class="simplesect"><div class="titlepage"><div><div><h5 class="title"><a name="d6e2006"></a></h5></div></div></div>
        
        <div class="informalexample">        
            <p>The <code class="code">SphinxGeometry</code> section defines parameters for the Sphinx
                encrypted nested-packet format used internally by Katzenpost. 
                </p><div class="warning" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Warning"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Warning]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/warning.png"></td><th align="left">Warning</th></tr><tr><td align="left" valign="top"><p>The values in the <code class="code">SphinxGeometry</code> configuration section must
                        be programmatically generated by <span class="command"><strong>gensphinx</strong></span>. Many of the
                        parameters are interdependent and cannot be individually modified. Do not
                        modify the these values by hand.</p></td></tr></table></div>
            <p>The settings in this section are generated by the <span class="command"><strong>gensphinx</strong></span>
                utility, which computes the Sphinx geometry based on the following user-supplied
                directives:</p>
            <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                    <p>The number of  mix node layers (not counting gateway and service
                        nodes)</p>
                </li><li class="listitem">
                    <p>The length of the application-usable packet payload</p>
                </li><li class="listitem">
                    <p>The selected NIKE or KEM scheme</p>
                </li></ul></div>
            <p>The output in TOML should then be pasted unchanged into the node's configuration
                file, as shown below. For more information, see <a class="xref" href="#gensphinx" title="Chapter&nbsp;4.&nbsp;Appendix: Using gensphinx">Chapter&nbsp;4, <i>Appendix: Using <span class="emphasis"><em>gensphinx</em></span></i></a>.</p>
            <pre class="programlisting">[SphinxGeometry]
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
                KEMName = ""</pre>
            <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                    <p><span class="bold"><strong>PacketLength</strong></span></p>
                    <p>The length of a Sphinx packet in bytes.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>NrHops</strong></span></p>
                    <p>The number of hops a Sphinx packet takes through the mixnet. Because
                        packet headers hold destination information for each hop, the size of the
                        header increases linearly with the number of hops.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>HeaderLength</strong></span></p>
                    <p>The total length of the Sphinx packet header in bytes.</p>                   
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>RoutingInfoLength</strong></span></p>
                    <p>The total length of the routing information portion of the Sphinx packet
                        header.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>PerHopRoutingInfoLength</strong></span></p>
                    <p>The length of the per-hop routing information in the Sphinx packet
                        header.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>SURBLength</strong></span></p>
                    <p>The length of a single-use reply block (SURB).</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>SphinxPlaintextHeaderLength</strong></span></p>
                    <p>The length of the plaintext Sphinx packet header.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>PayloadTagLength</strong></span></p>
                    <p>The length of the payload tag.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>ForwardPayloadLength</strong></span></p>
                    <p>The total size of the payload.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>UserForwardPayloadLength</strong></span></p>
                    <p>The size of the usable payload.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>NextNodeHopLength</strong></span></p>
                    <p>The <code class="code">NextNodeHopLength</code> is derived from the largest routing-information 
                        block that we expect to encounter. Other packets have 
                        <code class="code">NextNodeHop</code> + <code class="code">NodeDelay</code> sections, or a <code class="code">Recipient</code> section, both of which
                        are shorter.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>SPRPKeyMaterialLength</strong></span></p>
                    <p>The length of the strong pseudo-random permutation (SPRP) key.</p>
                    <p>Type: int</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>NIKEName</strong></span></p>
                    <p>The name of the non-interactive key exchange (NIKE) scheme used by Sphinx
                        packets.</p>
                    <p><code class="code">NIKEName</code> and <code class="code">KEMName</code> are mutually
                        exclusive.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li><li class="listitem">
                    <p><span class="bold"><strong>KEMName</strong></span></p>
                    <p>The name of the key encapsulation mechanism (KEM) used by Sphinx
                        packets.</p>
                    <p><code class="code">NIKEName</code> and <code class="code">KEMName</code> are mutually exclusive.</p>
                    <p>Type: string</p>
                    <p>Required: Yes</p>
                </li></ul></div>            
        </div>
    </div>
            </div>
            <div class="section"><div class="titlepage"><div><div><h4 class="title"><a name="service-debug-config"></a>Service node: Debug section</h4></div></div></div>
                
                
                
                <div class="simplesect"><div class="titlepage"><div><div><h5 class="title"><a name="d6e2124"></a></h5></div></div></div>
             
        <div class="informalexample">    
            <p>The <code class="code">Debug</code> section is the Katzenpost server debug configuration
                for advanced tuning.</p>   
            <pre class="programlisting">[Debug]
                NumSphinxWorkers = 16
                NumServiceWorkers = 3
                NumGatewayWorkers = 3
                NumKaetzchenWorkers = 3
                SchedulerExternalMemoryQueue = false
                SchedulerQueueSize = 0
                SchedulerMaxBurst = 16
                UnwrapDelay = 250
                GatewayDelay = 500
                ServiceDelay = 500
                KaetzchenDelay = 750
                SchedulerSlack = 150
                SendSlack = 50
                DecoySlack = 15000
                ConnectTimeout = 60000
                HandshakeTimeout = 30000
                ReauthInterval = 30000
                SendDecoyTraffic = false
                DisableRateLimit = false
                GenerateOnly = false</pre>
                <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                        <p><span class="bold"><strong>NumSphinxWorkers</strong></span></p>
                        <p>Specifies the number of worker instances to use for inbound Sphinx
                            packet processing.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>NumProviderWorkers</strong></span></p>
                        <p>Specifies the number of worker instances to use for provider specific
                            packet processing.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>NumKaetzchenWorkers</strong></span></p>
                        <p>Specifies the number of worker instances to use for Kaetzchen-specific
                        packet processing.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>SchedulerExternalMemoryQueue</strong></span></p>
                        <p>If <span class="bold"><strong>true</strong></span>, the experimental disk-backed external memory 
                            queue is enabled.</p>
                        <p>Type: bool</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>SchedulerQueueSize</strong></span></p>
                        <p>Specifies the maximum scheduler queue size before random entries will
                        start getting dropped. A value less than or equal to zero is treated as
                        unlimited.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>SchedulerMaxBurst</strong></span></p>
                        <p>Specifies the maximum number of packets that will be dispatched per
                            scheduler wakeup event.</p>
                        <p>Type: </p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>UnwrapDelay</strong></span></p>
                        <p>Specifies the maximum unwrap delay due to queueing in
                            milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>GatewayDelay</strong></span></p>
                        <p>Specifies the maximum gateway node worker delay due to queueing in milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>ServiceDelay</strong></span></p>
                        <p>Specifies the maximum provider delay due to queueing in
                            milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p> 
                    </li><li class="listitem">
                        <p><span class="bold"><strong>KaetzchenDelay</strong></span></p>
                        <p>Specifies the maximum kaetzchen delay due to queueing in
                            milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>SchedulerSlack</strong></span></p>
                        <p>Specifies the maximum scheduler slack due to queueing and/or
                            processing in milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>SendSlack</strong></span></p>
                        <p>Specifies the maximum send-queue slack due to queueing and/or
                            congestion in milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>DecoySlack</strong></span></p>
                        <p>Specifies the maximum decoy sweep slack due to external
                            delays such as latency before a loop decoy packet will be considered
                            lost.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>ConnectTimeout</strong></span></p>
                        <p>Specifies the maximum time a connection can take to establish a
                            TCP/IP connection in milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>HandshakeTimeout</strong></span></p>
                        <p>Specifies the maximum time a connection can take for a link-protocol
                            handshake in milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>ReauthInterval</strong></span></p>
                        <p>Specifies the interval at which a connection will be reauthenticated
                            in milliseconds.</p>
                        <p>Type: int</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>SendDecoyTraffic</strong></span></p>
                        <p>If <span class="bold"><strong>true</strong></span>, decoy traffic is enabled. 
                            This parameter is experimental and untuned, 
                            and is disabled by default.</p>
                        <div class="note" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Note"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Note]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/note.png"></td><th align="left">Note</th></tr><tr><td align="left" valign="top">
                            <p>This option will be removed once decoy traffic is fully implemented.</p>
                        </td></tr></table></div>
                        <p>Type: bool</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>DisableRateLimit</strong></span></p>
                        <p>If <span class="bold"><strong>true</strong></span>, the per-client rate limiter is disabled.</p>
                        <div class="note" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Note"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Note]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/note.png"></td><th align="left">Note</th></tr><tr><td align="left" valign="top">
                            <p>This option should only be used for testing.</p>
                        </td></tr></table></div>
                        <p>Type: bool</p>
                        <p>Required: No</p>
                    </li><li class="listitem">
                        <p><span class="bold"><strong>GenerateOnly</strong></span></p>
                        <p>If <span class="bold"><strong>true</strong></span>, the server immediately halts
                        and cleans up after long-term key generation.</p>
                        <p>Type: bool</p>
                        <p>Required: No</p>
                    </li></ul></div>
        </div> 
    </div>
            </div>


        </div>
    </div>
</div> 

    <div class="chapter"><div class="titlepage"><div><div><h1 class="title"><a name="container"></a>Chapter&nbsp;2.&nbsp;Using the Katzenpost Docker test network</h1></div></div></div><div class="toc"><p><b>Table of Contents</b></p><dl class="toc"><dt><span class="section"><a href="#requirements">Requirements</a></span></dt><dt><span class="section"><a href="#install_kp">Preparing to run the container image</a></span></dt><dt><span class="section"><a href="#basic-ops">Operating the test mixnet</a></span></dt><dd><dl><dt><span class="section"><a href="#start-mixnet">Starting and monitoring the mixnet</a></span></dt><dt><span class="section"><a href="#test-mixnet">Testing the mixnet</a></span></dt><dt><span class="section"><a href="#shutdown-mixnet">Shutting down the mixnet</a></span></dt><dt><span class="section"><a href="#uninstall-mixnet">Uninstalling and cleaning up</a></span></dt></dl></dd><dt><span class="section"><a href="#topology">Network topology and components</a></span></dt><dd><dl><dt><span class="section"><a href="#d6e2648">The Docker file tree</a></span></dt></dl></dd><dt><span class="section"><a href="#d6e2654"></a></span></dt></dl></div>
        
    
    <p>Katzenpost provides a ready-to-deploy Docker
            image for developers who need a non-production test environment for developing
        and testing client applications and server side plugins. By running this image on a single computer, you avoid the
        need to build and manage a complex multi-node mix net. The image can also be run using <a class="ulink" href="https://podman.io/" target="_top">Podman</a></p>
    <p>The test mix network includes the following components:</p>
    <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
            <p>Three directory authority (<a class="ulink" href="https://katzenpost.network/docs/specs/pki/" target="_top">PKI</a>) nodes</p>
        </li><li class="listitem">
            <p>Six <a class="ulink" href="https://katzenpost.network/docs/specs/mixnet/" target="_top">mix</a> nodes,
                including one node serving also as both gateway and service provider</p>
        </li><li class="listitem">
            <p>A ping utility, <span class="command"><strong>run-ping</strong></span></p>
        </li></ul></div>
    
    <div class="section"><div class="titlepage"><div><div><h2 class="title" style="clear: both"><a name="requirements"></a>Requirements</h2></div></div></div>         
        
        <p>Before running the Katzenpost docker image, make sure that the
            following
            software is installed. </p>
        <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                <p>A <a class="ulink" href="https://debian.org" target="_top">Debian GNU Linux</a> or <a class="ulink" href="https://ubuntu.com" target="_top">Ubuntu</a> system</p>
            </li><li class="listitem">
                <p><a class="ulink" href="https://git-scm.com/" target="_top">Git</a></p>
            </li><li class="listitem">
                <p><a class="ulink" href="https://go.dev/" target="_top">Go</a></p>
            </li><li class="listitem">
                <p><a class="ulink" href="https://www.gnu.org/software/make/" target="_top">GNU Make</a></p>
            </li><li class="listitem">
                <p><a class="ulink" href="https://prometheus.io/docs/introduction/overview/" target="_top">Prometheus</a></p>
            </li><li class="listitem">
                <p><a class="ulink" href="https://www.docker.com" target="_top">Docker</a>, <a class="ulink" href="https://docs.docker.com/compose/" target="_top">Docker Compose</a>, and
                    (optionally) <a class="ulink" href="https://podman.io" target="_top">Podman</a></p>
                <div class="note" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Note"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Note]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/note.png"></td><th align="left">Note</th></tr><tr><td align="left" valign="top">
                    <p>If both Docker and Podman are present on your system, Katzenpost uses
                        Podman. Podman is a drop-in daemonless equivalent to Docker that does not
                        require superuser privileges to run.</p>
                </td></tr></table></div>
            </li></ul></div>
        <p>On Debian, these software requirements can be installed with the following commands
            (running as superuser). <span class="command"><strong>Apt</strong></span> will pull in the needed
            dependencies.</p>
        <pre class="programlisting"><code class="prompt"># </code><span class="command"><strong>apt update</strong></span>
<code class="prompt"># </code><span class="command"><strong>apt install git golang make docker docker-compose podman</strong></span></pre>       
    </div>   
    <div class="section"><div class="titlepage"><div><div><h2 class="title" style="clear: both"><a name="install_kp"></a>Preparing to run the container image</h2></div></div></div>
        
        <p>Complete the following procedure to obtain, build, and deploy the Katzenpost test
            network. </p>
        <div class="procedure"><ol class="procedure" type="1"><li class="step">
                <p>Install the Katzenpost code repository, hosted at <a class="ulink" href="https://github.com/katzenpost" target="_top">https://github.com/katzenpost</a>. The main Katzenpost
                    repository contains code for the server components as well as the docker image.
                    Clone the repository with the following command (your directory location may
                    vary):</p>
                <pre class="programlisting"><code class="prompt">~$ </code><span class="command"><strong>git clone https://github.com/katzenpost/katzenpost.git</strong></span></pre>
            </li><li class="step">
                <p>Navigate to the new <code class="filename">katzenpost</code> subdirectory and ensure
                    that the code is up to date.
                    </p><pre class="programlisting"><code class="prompt">~$ </code><span class="command"><strong>cd katzenpost</strong></span>
<code class="prompt">~/katzenpost$ </code><span class="command"><strong>git checkout main</strong></span>
<code class="prompt">~/katzenpost$ </code><span class="command"><strong>git pull</strong></span></pre>
            </li><li class="step">
                <p>(Optional) Create a development branch and check it
                    out.</p><pre class="programlisting"><code class="prompt">~/katzenpost$ </code><span class="command"><strong>git checkout -b devel</strong></span></pre>
            </li><li class="step">
                <p>(Optional) If you are using Podman, complete the following steps:</p>
                <div class="procedure"><ol class="procedure" type="1"><li class="step">
                        <p>Point the DOCKER_HOST environment variable at the Podman
                            process.</p>
                        <pre class="programlisting"><code class="prompt">$ </code><span class="command"><strong>export DOCKER_HOST=unix:///var/run/user/$(id -u)/podman/podman.sock</strong></span></pre>
                    </li><li class="step">
                        <p> Set up and start the Podman server (as superuser).</p>
                        <pre class="programlisting"><code class="prompt">$ </code><span class="command"><strong>podman system service -t 0 $DOCKER_HOST &amp;</strong></span>
<code class="prompt">$ </code><span class="command"><strong>systemctl --user enable --now podman.socket</strong></span>
                        </pre>
                    </li></ol></div>
            </li></ol></div>        
    </div>           
    <div class="section"><div class="titlepage"><div><div><h2 class="title" style="clear: both"><a name="basic-ops"></a>Operating the test mixnet</h2></div></div></div>
        
        <p>Navigate to <code class="filename">katzenpost/docker</code>. The <code class="filename">Makefile</code>
            contains target operations to create, manage, and test the self-contained Katzenpost
            container network. To invoke a target, run a command with the using the following
            pattern:</p>
        <pre class="programlisting"> <code class="prompt">~/katzenpost/docker$ </code><span class="command"><strong>make<em class="replaceable"><code> target</code></em></strong></span></pre>
        <p>Running <span class="command"><strong>make</strong></span> with no target specified returns a list of available
            targets.</p>
        <div class="table"><a name="d6e2353"></a><p class="title"><b>Table&nbsp;2.1.&nbsp;Table 1: Makefile targets</b></p><div class="table-contents">
            
            <table class="table" summary="Table 1: Makefile targets" border="1"><colgroup><col><col></colgroup><tbody><tr><td>
                            <p>[none]</p>
                        </td><td>
                            <p>Display this list of targets.</p>
                        </td></tr><tr><td>
                            <p><span class="bold"><strong>start</strong></span></p>
                        </td><td>
                            <p>Run the test network in the background.</p>
                        </td></tr><tr><td>
                            <p><span class="bold"><strong>stop</strong></span></p>
                        </td><td>
                            <p>Stop the test network.</p>
                        </td></tr><tr><td>
                            <p><span class="bold"><strong>wait</strong></span></p>
                        </td><td>
                            <p>Wait for the test network to have consensus.</p>
                        </td></tr><tr><td><span class="bold"><strong>watch</strong></span></td><td>
                            <p>Display live log entries until <span class="command"><strong>Ctrl-C</strong></span>.</p>
                        </td></tr><tr><td>
                            <p><span class="bold"><strong>status</strong></span></p>
                        </td><td>
                            <p>Show test network consensus status.</p>
                        </td></tr><tr><td>
                            <p><span class="bold"><strong>show-latest-vote</strong></span></p>
                        </td><td>
                            <p>Show latest consensus vote.</p>
                        </td></tr><tr><td>
                            <p><span class="bold"><strong>run-ping</strong></span></p>
                        </td><td>Send a ping over the test network.</td></tr><tr><td>
                            <p><span class="bold"><strong>clean-bin</strong></span></p>
                        </td><td>
                            <p>Stop all components and delete binaries.</p>
                        </td></tr><tr><td>
                            <p><span class="bold"><strong>clean-local</strong></span></p>
                        </td><td>
                            <p>Stop all components, delete binaries, and delete data.</p>
                        </td></tr><tr><td>
                            <p><span class="bold"><strong>clean-local-dryrun</strong></span></p>
                        </td><td>
                            <p>Show what clean-local would delete.</p>
                        </td></tr><tr><td>
                            <p><span class="bold"><strong>clean</strong></span></p>
                        </td><td>
                            <p>Same as <span class="bold"><strong>clean-local</strong></span>, but also
                                deletes <code class="code">go_deps</code> image.</p>
                        </td></tr></tbody></table>
        </div></div><br class="table-break">
        <div class="section"><div class="titlepage"><div><div><h3 class="title"><a name="start-mixnet"></a>Starting and monitoring the mixnet</h3></div></div></div>
            
            <p>The first time that you run <span class="command"><strong>make start</strong></span>, the Docker image is
                downloaded, built, installed, and started. This takes several minutes. When the
                build is complete, the command exits while the network remains running in the
                background.</p>
            <pre class="programlisting"><code class="prompt">~/katzenpost/docker$ </code><span class="command"><strong>make start</strong></span></pre>
            <p>Subsequent runs of <span class="command"><strong>make start</strong></span> either start or restart the
                network without building the components from scratch. The exception to this is when
                you delete any of the Katzenpost binaries (dirauth.alpine, server.alpine, etc.).
                In that case, <span class="command"><strong>make start</strong></span> rebuilds just the parts of the network
                dependent on the deleted binary. For more information about the files created during
                the Docker build, see <a class="xref" href="#topology" title="Network topology and components">the section called &#8220;Network topology and components&#8221;</a>.</p>
            <p></p>
            <div class="note" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Note"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Note]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/note.png"></td><th align="left">Note</th></tr><tr><td align="left" valign="top">
                <p>When running <span class="command"><strong>make start</strong></span> , be aware of the following
                    considerations:</p>
                <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                        <p>If you intend to use Docker, you need to run <span class="command"><strong>make</strong></span>
                            as superuser. If you are using <span class="command"><strong>sudo</strong></span> to elevate your
                            privileges, you need to edit
                                <code class="filename">katzenpost/docker/Makefile</code> to prepend
                                <span class="command"><strong>sudo</strong></span> to each command contained in it.</p>
                    </li><li class="listitem">
                        <p>If you have Podman installed on your system and you nonetheless want
                            to run Docker, you can override the default behavior by adding the
                            argument <span class="command"><strong>docker=docker</strong></span> to the command as in the
                            following:</p><pre class="programlisting"><code class="prompt">~/katzenpost/docker$ </code><span class="command"><strong>make run docker=docker</strong></span> </pre>
                    </li></ul></div>
            </td></tr></table></div>
            <p>After the <span class="command"><strong>make start</strong></span> command exits, the mixnet runs in the
                background, and you can run <span class="command"><strong>make watch</strong></span> to display a live log of
                the network activity.</p>
            <p>
                </p><pre class="programlisting"><code class="prompt">~/katzenpost/docker$ </code><span class="command"><strong>make watch</strong></span>
    ...
    &lt;output&gt;
    ...</pre><p>
            </p>
            <p>When installation is complete, the mix servers vote and reach a consensus. You can
                use the <span class="command"><strong>wait</strong></span> target to wait for the mixnet to get consensus and
                be ready to use. This can also take several minutes:</p>
            <p>
                </p><pre class="programlisting"><code class="prompt">~/katzenpost/docker$ </code><span class="command"><strong>make wait</strong></span>
    ...
    &lt;output&gt;
    ...</pre><p>
            </p>
            <p>You can confirm that installation and configuration are complete by issuing the
                    <span class="command"><strong>status</strong></span> command from the same or another terminal. When the
                network is ready for use, <span class="command"><strong>status</strong></span> begins returning consensus
                information similar to the following:</p>
            <p>
                </p><pre class="programlisting"><code class="prompt">~/katzenpost/docker$ </code><span class="command"><strong>make status</strong></span>
    ...
    00:15:15.003 NOTI state: Consensus made for epoch 1851128 with 3/3 signatures: &amp;{Epoch: 1851128 GenesisEpoch: 1851118
    ...</pre><p>
            </p>
        </div>
        <div class="section"><div class="titlepage"><div><div><h3 class="title"><a name="test-mixnet"></a>Testing the mixnet</h3></div></div></div>
            
            <p>At this point, you should have a locally running mix network. You can test whether
                it is working correctly by using <span class="command"><strong>run-ping</strong></span>, which launches a
                packet into the network and watches for a successful reply. Run the following
                command:</p><pre class="programlisting"><code class="prompt">~/katzenpost/docker$ </code><span class="command"><strong>make run-ping</strong></span></pre>
            <p>If the network is functioning properly, the resulting output contains lines
                similar to the following:</p>
            <pre class="programlisting">19:29:53.541 INFO gateway1_client: sending loop decoy
    !19:29:54.108 INFO gateway1_client: sending loop decoy
    19:29:54.632 INFO gateway1_client: sending loop decoy
    19:29:55.160 INFO gateway1_client: sending loop decoy
    !19:29:56.071 INFO gateway1_client: sending loop decoy
    !19:29:59.173 INFO gateway1_client: sending loop decoy
    !Success rate is 100.000000 percent 10/10)</pre>
            <p>lf <span class="command"><strong>run-ping</strong></span> fails to receive a reply, it eventually times out
                with an error message. If this happens, try the command again. </p>
            <div class="note" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Note"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Note]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/note.png"></td><th align="left">Note</th></tr><tr><td align="left" valign="top">
                <p>If you attempt use <span class="bold"><strong>run-ping</strong></span> too quickly after
                    starting the mixnet, and consensus has not been reached, the utility may crash
                    with an error message or hang indefinitely. If this happens, issue (if
                    necessary) a <span class="command"><strong>Ctrl-C</strong></span> key sequence to abort, check the
                    consensus status with the <span class="command"><strong>status</strong></span> command, and then retry
                        <span class="command"><strong>run-ping</strong></span>.</p>
            </td></tr></table></div>
        </div>
        <div class="section"><div class="titlepage"><div><div><h3 class="title"><a name="shutdown-mixnet"></a>Shutting down the mixnet</h3></div></div></div>
            
            <p>The mix network continues to run in the terminal where you started it until you
                issue a <span class="command"><strong>Ctrl-C</strong></span> key sequence, or until you issue the following
                command in another terminal:</p>
            <pre class="programlisting"><code class="prompt">~/katzenpost/docker$ </code><span class="command"><strong>make stop</strong></span></pre>
            <p>When you stop the network, the binaries and data are left in place. This allows
                for a quick restart.</p>
        </div>
        <div class="section"><div class="titlepage"><div><div><h3 class="title"><a name="uninstall-mixnet"></a>Uninstalling and cleaning up</h3></div></div></div>
            
            <p>Several command targets can be used to uninstall the Docker image and restore your
                system to a clean state. The following examples demonstrate the commands and their
                output.</p>
            <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                    <p><span class="command"><strong>clean-bin</strong></span></p>
                    <p>To stop the network and delete the compiled binaries, run the following
                        command:</p>
                    <pre class="programlisting"><code class="prompt">~/katzenpost/docker$ </code><span class="command"><strong>make clean-bin</strong></span>
    
    [ -e voting_mixnet ] &amp;&amp; cd voting_mixnet &amp;&amp; DOCKER_HOST=unix:///run/user/1000/podman/podman.sock docker-compose down --remove-orphans; rm -fv running.stamp
    Stopping voting_mixnet_auth3_1        ... done
    Stopping voting_mixnet_servicenode1_1 ... done
    Stopping voting_mixnet_metrics_1      ... done
    Stopping voting_mixnet_mix3_1         ... done
    Stopping voting_mixnet_auth2_1        ... done
    Stopping voting_mixnet_mix2_1         ... done
    Stopping voting_mixnet_gateway1_1     ... done
    Stopping voting_mixnet_auth1_1        ... done
    Stopping voting_mixnet_mix1_1         ... done
    Removing voting_mixnet_auth3_1        ... done
    Removing voting_mixnet_servicenode1_1 ... done
    Removing voting_mixnet_metrics_1      ... done
    Removing voting_mixnet_mix3_1         ... done
    Removing voting_mixnet_auth2_1        ... done
    Removing voting_mixnet_mix2_1         ... done
    Removing voting_mixnet_gateway1_1     ... done
    Removing voting_mixnet_auth1_1        ... done
    Removing voting_mixnet_mix1_1         ... done
    removed 'running.stamp'
    rm -vf ./voting_mixnet/*.alpine
    removed './voting_mixnet/echo_server.alpine'
    removed './voting_mixnet/fetch.alpine'
    removed './voting_mixnet/memspool.alpine'
    removed './voting_mixnet/panda_server.alpine'
    removed './voting_mixnet/pigeonhole.alpine'
    removed './voting_mixnet/ping.alpine'
    removed './voting_mixnet/reunion_katzenpost_server.alpine'
    removed './voting_mixnet/server.alpine'
    removed './voting_mixnet/voting.alpine'</pre>
                    <p>This command leaves in place the cryptographic keys, the state data, and
                        the logs.</p>
                </li><li class="listitem">
                    <p><span class="command"><strong>clean-local-dryrun</strong></span></p>
                    <p>To diplay a preview of what <span class="command"><strong>clean-local</strong></span> would remove,
                        without actually deleting anything, run the following command:</p>
                    <pre class="programlisting"><code class="prompt">~/katzenpost/docker$ </code><span class="command"><strong>make clean-local-dryrun</strong></span></pre>
                </li><li class="listitem">
                    <p><span class="command"><strong>clean-local</strong></span></p>
                    <p>To delete both compiled binaries and data, run the following
                        command:</p>
                    <pre class="programlisting"><code class="prompt">~/katzenpost/docker$ </code><span class="command"><strong>make clean-local</strong></span>
                        
    [ -e voting_mixnet ] &amp;&amp; cd voting_mixnet &amp;&amp; DOCKER_HOST=unix:///run/user/1000/podman/podman.sock docker-compose down --remove-orphans; rm -fv running.stamp
    Removing voting_mixnet_mix2_1         ... done
    Removing voting_mixnet_auth1_1        ... done
    Removing voting_mixnet_auth2_1        ... done
    Removing voting_mixnet_gateway1_1     ... done
    Removing voting_mixnet_mix1_1         ... done
    Removing voting_mixnet_auth3_1        ... done
    Removing voting_mixnet_mix3_1         ... done
    Removing voting_mixnet_servicenode1_1 ... done
    Removing voting_mixnet_metrics_1      ... done
    removed 'running.stamp'
    rm -vf ./voting_mixnet/*.alpine
    removed './voting_mixnet/echo_server.alpine'
    removed './voting_mixnet/fetch.alpine'
    removed './voting_mixnet/memspool.alpine'
    removed './voting_mixnet/panda_server.alpine'
    removed './voting_mixnet/pigeonhole.alpine'
    removed './voting_mixnet/reunion_katzenpost_server.alpine'
    removed './voting_mixnet/server.alpine'
    removed './voting_mixnet/voting.alpine'
    git clean -f -x voting_mixnet
    Removing voting_mixnet/
    git status .
    On branch main
    Your branch is up to date with 'origin/main'.</pre>
                </li><li class="listitem">
                    <p><span class="command"><strong>clean</strong></span></p>
                    <p>To stop the the network and delete the binaries, the data, and the go_deps
                        image, run the following command as superuser: </p>
                    <pre class="programlisting"><code class="prompt">~/katzenpost/docker$ </code><span class="command"><strong>sudo make clean</strong></span></pre>
                </li></ul></div>
        </div>
    </div>
    <div class="section"><div class="titlepage"><div><div><h2 class="title" style="clear: both"><a name="topology"></a>Network topology and components</h2></div></div></div>
        
        <p>The Docker image deploys a working mixnet with all components and component groups
            needed to perform essential mixnet functions: </p>
        <div class="itemizedlist"><ul class="itemizedlist" style="list-style-type: disc; "><li class="listitem">
                <p>message mixing (including packet reordering, timing randomization, injection
                    of decoy traffic, obfuscation of senders and receivers, and so on)</p>
            </li><li class="listitem">
                <p>service provisioning</p>
            </li><li class="listitem">
                <p>internal authentication and integrity monitoring</p>
            </li><li class="listitem">
                <p>interfacing with external clients</p>
            </li></ul></div>
        <div class="warning" style="margin-left: 0.5in; margin-right: 0.5in;"><table border="0" summary="Warning"><tr><td rowspan="2" align="center" valign="top" width="25"><img alt="[Warning]" src="file:/home/usr/local/Oxygen%20XML%20Editor%2026/frameworks/docbook/css/img/warning.png"></td><th align="left">Warning</th></tr><tr><td align="left" valign="top">
            <p>While suited for client development and testing, the test mixnet omits performance
                and security redundancies. <span class="emphasis"><em>Do not use it in production.</em></span></p>
        </td></tr></table></div>
        <p>The following diagram illustrates the components and their network interactions. The
            gray blocks represent nodes, and the arrows represent information transfer. </p>
        <div class="figure"><a name="d6e2552"></a><p class="title"><b>Figure&nbsp;2.1.&nbsp;Test network topology</b></p><div class="figure-contents">
            
            <div class="mediaobject"><img src="/admin_guide/pix/katzenpost-docker.png" width="405" alt="Test network topology"></div>
        </div></div><br class="figure-break">
        <p>On the left, the <span class="bold"><strong>Client</strong></span> transmits a message (shown by
            purple arrows) through the <span class="bold"><strong>Gateway node</strong></span>, across three
                <span class="bold"><strong>mix node</strong></span> layers, to the <span class="bold"><strong>Service node</strong></span>. The <span class="bold"><strong>Service node</strong></span>
            processes the request and responds with a reply (shown by the green arrows) that
            traverses the <span class="bold"><strong>mix node</strong></span> layers before exiting the mixnet
            via the <span class="bold"><strong>Gateway node</strong></span> and arriving at the <span class="bold"><strong>Client</strong></span>.</p>
        <p>On the right, directory authorities <span class="bold"><strong>Dirauth 1</strong></span>,
                <span class="bold"><strong>Dirauth 2</strong></span>, and <span class="bold"><strong>Dirauth
                3</strong></span> provide PKI services. The directory authorities receive <span class="bold"><strong>mix descriptors</strong></span> from the other nodes, collate these into a
                <span class="bold"><strong>consensus document</strong></span> containing validated network
            status and authentication materials , and make that available to the other nodes. </p>
        <p>The elements in the topology diagram map to the mixnet's component nodes as shown in
            the following table. Note that all nodes share the same IP address (127.0.0.1, i.e.,
            localhost), but are accessed through different ports. Each node type links to additional
            information in <a class="xref" href="#components" title="Chapter&nbsp;1.&nbsp;Components and configuration of the Katzenpost mixnet">Components and configuration of the Katzenpost mixnet</a>.</p>
        <div class="table"><a name="d6e2574"></a><p class="title"><b>Table&nbsp;2.2.&nbsp;Table 2: Test mixnet hosts</b></p><div class="table-contents">
            
            <table class="table" summary="Table 2: Test mixnet hosts" border="1"><colgroup><col class="c1"><col class="c2"><col class="newCol3"><col class="c3"><col class="c4"></colgroup><thead><tr><th>Node type</th><th>Docker ID</th><th>Diagram label</th><th>IP address</th><th>TCP port</th></tr></thead><tbody><tr><td rowspan="3">
                            <p><a class="link" href="#intro-dirauth" title="Directory authorities (dirauths)">Directory authority</a></p>
                        </td><td>auth1</td><td>Dirauth1</td><td rowspan="8">
                            <p>127.0.0.1 (localhost)</p>
                        </td><td>
                            <p>30001</p>
                        </td></tr><tr><td>
                            <p>auth2</p>
                        </td><td>Dirauth 2</td><td>
                            <p>30002</p>
                        </td></tr><tr><td>
                            <p>auth3</p>
                        </td><td>Dirauth 3</td><td>
                            <p>30003</p>
                        </td></tr><tr><td><a class="link" href="#intro-gateway" title="Gateway nodes">Gateway node</a></td><td>gateway1</td><td>Gateway node</td><td>30004</td></tr><tr><td>
                            <p><a class="link" href="#intro-service" title="Service nodes">Service node</a></p>
                        </td><td>
                            <p>servicenode1</p>
                        </td><td>Service node</td><td>
                            <p>30006 </p>
                        </td></tr><tr><td rowspan="3">
                            <p><a class="link" href="#intro-mix" title="Mix nodes">Mix node</a></p>
                        </td><td>
                            <p>mix1</p>
                        </td><td>Layer 1 mix node</td><td>
                            <p>30008</p>
                        </td></tr><tr><td>
                            <p>mix2</p>
                        </td><td>Layer 2 mix node</td><td>
                            <p>30010</p>
                        </td></tr><tr><td>
                            <p>mix3</p>
                        </td><td>Layer 3 mix node</td><td>
                            <p>30012</p>
                        </td></tr></tbody></table>
        </div></div><br class="table-break">
        <div class="section"><div class="titlepage"><div><div><h3 class="title"><a name="d6e2648"></a>The Docker file tree</h3></div></div></div>
            
            <p>The following <a class="ulink" href="https://manpages.debian.org/bookworm/tree/tree.1.en.html" target="_top">tree</a>
                output shows the location, relative to the <code class="filename">katzenpost</code>
                repository root, of the files created by the Docker build. During testing and use,
                you would normally touch only the TOML configuration file associated with each node,
                as highlighted in the listing. For help in understanding these files and a complete
                list of configuration options, follow the links in <span class="guilabel">Table 2: Test mixnet
                    hosts</span>.</p>
        </div>
    </div>
    <div class="section"><div class="titlepage"></div>
        <pre class="programlisting">katzenpost/docker/voting_mixnet/
|---<span class="bold"><strong>auth1</strong></span>
|&nbsp;&nbsp; |---<span class="bold"><strong>authority.toml</strong></span>
|&nbsp;&nbsp; |---identity.private.pem
|&nbsp;&nbsp; |---identity.public.pem
|&nbsp;&nbsp; |---katzenpost.log
|&nbsp;&nbsp; |---link.private.pem
|&nbsp;&nbsp; |---link.public.pem
|&nbsp;&nbsp; |---persistence.db
|---<span class="bold"><strong>auth2</strong></span>
|&nbsp;&nbsp; |---<span class="bold"><strong>authority.toml</strong></span>
|&nbsp;&nbsp; |---identity.private.pem
|&nbsp;&nbsp; |---identity.public.pem
|&nbsp;&nbsp; |---katzenpost.log
|&nbsp;&nbsp; |---link.private.pem
|&nbsp;&nbsp; |---link.public.pem
|&nbsp;&nbsp; |---persistence.db
|---<span class="bold"><strong>auth3</strong></span>
|&nbsp;&nbsp; |---<span class="bold"><strong>authority.toml</strong></span>
|&nbsp;&nbsp; |---identity.private.pem
|&nbsp;&nbsp; |---identity.public.pem
|&nbsp;&nbsp; |---katzenpost.log
|&nbsp;&nbsp; |---link.private.pem
|&nbsp;&nbsp; |---link.public.pem
|&nbsp;&nbsp; |---persistence.db
|---client
|&nbsp;&nbsp; |---client.toml
|---client2
|&nbsp;&nbsp; |---client.toml
|---dirauth.alpine
|---docker-compose.yml
|---echo_server.alpine
|---fetch.alpine
|---<span class="bold"><strong>gateway1</strong></span>
|&nbsp;&nbsp; |---identity.private.pem
|&nbsp;&nbsp; |---identity.public.pem
|&nbsp;&nbsp; |---katzenpost.log
|&nbsp;&nbsp; |---<span class="bold"><strong>katzenpost.toml</strong></span>
|&nbsp;&nbsp; |---link.private.pem
|&nbsp;&nbsp; |---link.public.pem
|&nbsp;&nbsp; |---management_sock
|&nbsp;&nbsp; |---spool.db
|&nbsp;&nbsp; |---users.db
|---memspool.alpine
|---<span class="bold"><strong>mix1</strong></span>
|&nbsp;&nbsp; |---identity.private.pem
|&nbsp;&nbsp; |---identity.public.pem
|&nbsp;&nbsp; |---katzenpost.log
|&nbsp;&nbsp; |---<span class="bold"><strong>katzenpost.toml</strong></span>
|&nbsp;&nbsp; |---link.private.pem
|&nbsp;&nbsp; |---link.public.pem
|---<span class="bold"><strong>mix2</strong></span>
|&nbsp;&nbsp; |---identity.private.pem
|&nbsp;&nbsp; |---identity.public.pem
|&nbsp;&nbsp; |---katzenpost.log
|&nbsp;&nbsp; |---<span class="bold"><strong>katzenpost.toml</strong></span>
|&nbsp;&nbsp; |---link.private.pem
|&nbsp;&nbsp; |---link.public.pem
|---<span class="bold"><strong>mix3</strong></span>
|&nbsp;&nbsp; |---identity.private.pem
|&nbsp;&nbsp; |---identity.public.pem
|&nbsp;&nbsp; |---katzenpost.log
|&nbsp;&nbsp; |---<span class="bold"><strong>katzenpost.toml</strong></span>
|&nbsp;&nbsp; |---link.private.pem
|&nbsp;&nbsp; |---link.public.pem
|---panda_server.alpine
|---pigeonhole.alpine
|---ping.alpine
|---prometheus.yml
|---proxy_client.alpine
|---proxy_server.alpine
|---running.stamp
|---server.alpine
|---<span class="bold"><strong>servicenode1</strong></span>
|&nbsp;&nbsp; |---identity.private.pem
|&nbsp;&nbsp; |---identity.public.pem
|&nbsp;&nbsp; |---katzenpost.log
|&nbsp;&nbsp; |---<span class="bold"><strong>katzenpost.toml</strong></span>
|&nbsp;&nbsp; |---link.private.pem
|&nbsp;&nbsp; |---link.public.pem
|&nbsp;&nbsp; |---management_sock
|&nbsp;&nbsp; |---map.storage
|&nbsp;&nbsp; |---memspool.13.log
|&nbsp;&nbsp; |---memspool.storage
|&nbsp;&nbsp; |---panda.25.log
|&nbsp;&nbsp; |---panda.storage
|&nbsp;&nbsp; |---pigeonHole.19.log
|&nbsp;&nbsp; |---proxy.31.log
|---voting_mixnet</pre>
        <p>Examples of complete TOML configuration files are provided in <a class="xref" href="#docker-config" title="Chapter&nbsp;3.&nbsp;Appendix: Configuration files from the Docker test mixnet">Appendix: Configuration files from the Docker test mixnet </a>.</p>
    </div>
    
    
</div>
    <div class="chapter"><div class="titlepage"><div><div><h1 class="title"><a name="docker-config"></a>Chapter&nbsp;3.&nbsp;Appendix: Configuration files from the Docker test mixnet </h1></div></div></div><div class="toc"><p><b>Table of Contents</b></p><dl class="toc"><dt><span class="section"><a href="#dirauth-config">Directory authority</a></span></dt><dt><span class="section"><a href="#mix-node-config">Mix node</a></span></dt><dt><span class="section"><a href="#gateway-node-config">Gateway node</a></span></dt><dt><span class="section"><a href="#service-node-config">Service node</a></span></dt></dl></div>
    
    <p>As an aid to adminstrators implementing a Katzenpost mixnet, this appendix provides
        lightly edited examples of configuration files for each Katzenpost node type. These
        files are drawn from a built instance of the <a class="link" href="#container" title="Chapter&nbsp;2.&nbsp;Using the Katzenpost Docker test network">Docker test
            mixnet</a>. These code listings are meant to be used as a reference alongside the
        detailed configuration documentation in <a class="xref" href="#components" title="Chapter&nbsp;1.&nbsp;Components and configuration of the Katzenpost mixnet">Chapter&nbsp;1, <i>Components and configuration of the Katzenpost mixnet</i></a>. You cannot use these
        listings as a drop-in solution in your own mixnets for reasons explained in the <a class="xref" href="#topology" title="Network topology and components">the section called &#8220;Network topology and components&#8221;</a> section of the Docker test mixnet documentation.</p>
    <div class="section"><div class="titlepage"><div><div><h2 class="title" style="clear: both"><a name="dirauth-config"></a>Directory authority</h2></div></div></div>
        
        <p>Source:
            <code class="filename">../katzenpost/docker/voting_mixnet/auth1/authority.toml</code></p>
        <pre class="programlisting">[Server]
  Identifier = "auth1"
  WireKEMScheme = "xwing"
  PKISignatureScheme = "Ed448-Dilithium3"
  Addresses = ["tcp://127.0.0.1:30001"]
  DataDir = "/voting_mixnet/auth1"

[[Authorities]]
  Identifier = "auth1"
  IdentityPublicKey = "-----BEGIN ED448-DILITHIUM3 PUBLIC KEY-----\nfvcvAfUpeu7lMHjQBw [...] Gpi8ovBXl9ENIHLwA=\n-----END ED448-DILITHIUM3 PUBLIC KEY-----\n"
  PKISignatureScheme = "Ed448-Dilithium3"
  LinkPublicKey = "-----BEGIN XWING PUBLIC KEY-----\nsxxS04mftoEmwjxE/w [...] expP2fbERpGQwVNg==\n-----END XWING PUBLIC KEY-----\n"
  WireKEMScheme = "xwing"
  Addresses = ["tcp://127.0.0.1:30001"]

[[Authorities]]
  Identifier = "auth2"
  IdentityPublicKey = "-----BEGIN ED448-DILITHIUM3 PUBLIC KEY-----\n5nsy6uFQ1782fZ+iYn [...] Sdr2xoinylYJr/3AA=\n-----END ED448-DILITHIUM3 PUBLIC KEY-----\n"
  PKISignatureScheme = "Ed448-Dilithium3"
  LinkPublicKey = "-----BEGIN XWING PUBLIC KEY-----\nkQzCJvaS6jg06szLea [...] PG1Bzx1JwHGFxRBQ==\n-----END XWING PUBLIC KEY-----\n"
  WireKEMScheme = "xwing"
  Addresses = ["tcp://127.0.0.1:30002"]

[[Authorities]]
  Identifier = "auth3"
  IdentityPublicKey = "-----BEGIN ED448-DILITHIUM3 PUBLIC KEY-----\nJzkFpS035de1PmA2MM [...] jo6Z7is9GLs0YxVQA=\n-----END ED448-DILITHIUM3 PUBLIC KEY-----\n"
  PKISignatureScheme = "Ed448-Dilithium3"
  LinkPublicKey = "-----BEGIN XWING PUBLIC KEY-----\n+pIUsgEGwHa8k4GZcb [...] 1mxoc+4kcgZWuOAg==\n-----END XWING PUBLIC KEY-----\n"
  WireKEMScheme = "xwing"
  Addresses = ["tcp://127.0.0.1:30003"]

[Logging]
  Disable = false
  File = "katzenpost.log"
  Level = "INFO"

[Parameters]
  SendRatePerMinute = 0
  Mu = 0.005
  MuMaxDelay = 1000
  LambdaP = 0.001
  LambdaPMaxDelay = 1000
  LambdaL = 0.0005
  LambdaLMaxDelay = 1000
  LambdaD = 0.0005
  LambdaDMaxDelay = 3000
  LambdaM = 0.0005
  LambdaG = 0.0
  LambdaMMaxDelay = 100
  LambdaGMaxDelay = 100

[Debug]
  Layers = 3
  MinNodesPerLayer = 1
  GenerateOnly = false

[[Mixes]]
  Identifier = "mix1"
  IdentityPublicKeyPem = "../mix1/identity.public.pem"

[[Mixes]]
  Identifier = "mix2"
  IdentityPublicKeyPem = "../mix2/identity.public.pem"

[[Mixes]]
  Identifier = "mix3"
  IdentityPublicKeyPem = "../mix3/identity.public.pem"

[[GatewayNodes]]
  Identifier = "gateway1"
  IdentityPublicKeyPem = "../gateway1/identity.public.pem"

[[ServiceNodes]]
  Identifier = "servicenode1"
  IdentityPublicKeyPem = "../servicenode1/identity.public.pem"

[Topology]

  [[Topology.Layers]]

    [[Topology.Layers.Nodes]]
      Identifier = "mix1"
      IdentityPublicKeyPem = "../mix1/identity.public.pem"

  [[Topology.Layers]]

    [[Topology.Layers.Nodes]]
      Identifier = "mix2"
      IdentityPublicKeyPem = "../mix2/identity.public.pem"

  [[Topology.Layers]]

    [[Topology.Layers.Nodes]]
      Identifier = "mix3"
      IdentityPublicKeyPem = "../mix3/identity.public.pem"

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
  KEMName = ""</pre>
    </div>
    <div class="section"><div class="titlepage"><div><div><h2 class="title" style="clear: both"><a name="mix-node-config"></a>Mix node</h2></div></div></div>
        
        <p>Source:<code class="filename">
            ../katzenpost/docker/voting_mixnet/mix1/katzenpost.toml</code></p>
        <pre class="programlisting">[Server]
  Identifier = "mix1"
  WireKEM = "xwing"
  PKISignatureScheme = "Ed448-Dilithium3"
  Addresses = ["tcp://127.0.0.1:30010", "quic://[::1]:30011"]
  MetricsAddress = "127.0.0.1:30012"
  DataDir = "/voting_mixnet/mix1"
  IsGatewayNode = false
  IsServiceNode = false

[Logging]
  Disable = false
  File = "katzenpost.log"
  Level = "INFO"

[PKI]
  [PKI.Voting]

    [[PKI.Voting.Authorities]]
      Identifier = "auth1"
      IdentityPublicKey = "-----BEGIN ED448-DILITHIUM3 PUBLIC KEY-----\nfvcvAfUpeu7lMHjQBw [...] Gpi8ovBXl9ENIHLwA=\n-----END ED448-DILITHIUM3 PUBLIC KEY-----\n"
      PKISignatureScheme = "Ed448-Dilithium3"
      LinkPublicKey = "-----BEGIN XWING PUBLIC KEY-----\nsxxS04mftoEmwjxE/w [...] expP2fbERpGQwVNg==\n-----END XWING PUBLIC KEY-----\n"
      WireKEMScheme = "xwing"
      Addresses = ["tcp://127.0.0.1:30001"]

    [[PKI.Voting.Authorities]]
      Identifier = "auth2"
      IdentityPublicKey = "-----BEGIN ED448-DILITHIUM3 PUBLIC KEY-----\n5nsy6uFQ1782fZ+iYn [...] Sdr2xoinylYJr/3AA=\n-----END ED448-DILITHIUM3 PUBLIC KEY-----\n"
      PKISignatureScheme = "Ed448-Dilithium3"
      LinkPublicKey = "-----BEGIN XWING PUBLIC KEY-----\nkQzCJvaS6jg06szLea [...] PG1Bzx1JwHGFxRBQ==\n-----END XWING PUBLIC KEY-----\n"
      WireKEMScheme = "xwing"
      Addresses = ["tcp://127.0.0.1:30002"]

    [[PKI.Voting.Authorities]]
      Identifier = "auth3"
      IdentityPublicKey = "-----BEGIN ED448-DILITHIUM3 PUBLIC KEY-----\nJzkFpS035de1PmA2M [...] jo6Z7is9GLs0YxVQA=\n-----END ED448-DILITHIUM3 PUBLIC KEY-----\n"
      PKISignatureScheme = "Ed448-Dilithium3"
      LinkPublicKey = "-----BEGIN XWING PUBLIC KEY-----\n+pIUsgEGwHa8k4GZcb [...] 1mxoc+4kcgZWuOAg==\n-----END XWING PUBLIC KEY-----\n"
      WireKEMScheme = "xwing"
      Addresses = ["tcp://127.0.0.1:30003"]

[Management]
  Enable = false
  Path = "/voting_mixnet/mix1/management_sock"

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

[Debug]
  NumSphinxWorkers = 16
  NumServiceWorkers = 3
  NumGatewayWorkers = 3
  NumKaetzchenWorkers = 3
  SchedulerExternalMemoryQueue = false
  SchedulerQueueSize = 0
  SchedulerMaxBurst = 16
  UnwrapDelay = 250
  GatewayDelay = 500
  ServiceDelay = 500
  KaetzchenDelay = 750
  SchedulerSlack = 150
  SendSlack = 50
  DecoySlack = 15000
  ConnectTimeout = 60000
  HandshakeTimeout = 30000
  ReauthInterval = 30000
  SendDecoyTraffic = false
  DisableRateLimit = false
  GenerateOnly = false</pre>
    </div>
    <div class="section"><div class="titlepage"><div><div><h2 class="title" style="clear: both"><a name="gateway-node-config"></a>Gateway node</h2></div></div></div>
        
        <p>Source:
                <code class="filename">../katzenpost/docker/voting_mixnet/gateway1/katzenpost.toml</code></p>
        <pre class="programlisting">[Server]
  Identifier = "gateway1"
  WireKEM = "xwing"
  PKISignatureScheme = "Ed448-Dilithium3"
  Addresses = ["tcp://127.0.0.1:30004", "quic://[::1]:30005", "onion://thisisjustatestoniontoverifythatconfigandpkiworkproperly.onion:4242"]
  BindAddresses = ["tcp://127.0.0.1:30004", "quic://[::1]:30005"]
  MetricsAddress = "127.0.0.1:30006"
  DataDir = "/voting_mixnet/gateway1"
  IsGatewayNode = true
  IsServiceNode = false

[Logging]
  Disable = false
  File = "katzenpost.log"
  Level = "INFO"

[Gateway]
  [Gateway.UserDB]
    Backend = "bolt"
    [Gateway.UserDB.Bolt]
      UserDB = "/voting_mixnet/gateway1/users.db"
  [Gateway.SpoolDB]
    Backend = "bolt"
    [Gateway.SpoolDB.Bolt]
      SpoolDB = "/voting_mixnet/gateway1/spool.db"

[PKI]
  [PKI.Voting]

    [[PKI.Voting.Authorities]]
      Identifier = "auth1"
      IdentityPublicKey = "-----BEGIN ED448-DILITHIUM3 PUBLIC KEY-----\nfvcvAfUpeu7lMHjQBw [...] Gpi8ovBXl9ENIHLwA=\n-----END ED448-DILITHIUM3 PUBLIC KEY-----\n"
      PKISignatureScheme = "Ed448-Dilithium3"
      LinkPublicKey = "-----BEGIN XWING PUBLIC KEY-----\nsxxS04mftoEmwjxE/w [...] expP2fbERpGQwVNg==\n-----END XWING PUBLIC KEY-----\n"
      WireKEMScheme = "xwing"
      Addresses = ["tcp://127.0.0.1:30001"]

    [[PKI.Voting.Authorities]]
      Identifier = "auth2"
      IdentityPublicKey = "-----BEGIN ED448-DILITHIUM3 PUBLIC KEY-----\n5nsy6uFQ1782fZ+iYn [...] Sdr2xoinylYJr/3AA=\n-----END ED448-DILITHIUM3 PUBLIC KEY-----\n"
      PKISignatureScheme = "Ed448-Dilithium3"
      LinkPublicKey = "-----BEGIN XWING PUBLIC KEY-----\nkQzCJvaS6jg06szLea [...] PG1Bzx1JwHGFxRBQ==\n-----END XWING PUBLIC KEY-----\n"
      WireKEMScheme = "xwing"
      Addresses = ["tcp://127.0.0.1:30002"]

    [[PKI.Voting.Authorities]]
      Identifier = "auth3"
      IdentityPublicKey = "-----BEGIN ED448-DILITHIUM3 PUBLIC KEY-----\nJzkFpS035de1PmA2MM [...] jo6Z7is9GLs0YxVQA=\n-----END ED448-DILITHIUM3 PUBLIC KEY-----\n"
      PKISignatureScheme = "Ed448-Dilithium3"
      LinkPublicKey = "-----BEGIN XWING PUBLIC KEY-----\n+pIUsgEGwHa8k4GZcb [...] 1mxoc+4kcgZWuOAg==\n-----END XWING PUBLIC KEY-----\n"
      WireKEMScheme = "xwing"
      Addresses = ["tcp://127.0.0.1:30003"]

[Management]
  Enable = true
  Path = "/voting_mixnet/gateway1/management_sock"

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

[Debug]
  NumSphinxWorkers = 16
  NumServiceWorkers = 3
  NumGatewayWorkers = 3
  NumKaetzchenWorkers = 3
  SchedulerExternalMemoryQueue = false
  SchedulerQueueSize = 0
  SchedulerMaxBurst = 16
  UnwrapDelay = 250
  GatewayDelay = 500
  ServiceDelay = 500
  KaetzchenDelay = 750
  SchedulerSlack = 150
  SendSlack = 50
  DecoySlack = 15000
  ConnectTimeout = 60000
  HandshakeTimeout = 30000
  ReauthInterval = 30000
  SendDecoyTraffic = false
  DisableRateLimit = false
  GenerateOnly = false</pre>
    </div>
    <div class="section"><div class="titlepage"><div><div><h2 class="title" style="clear: both"><a name="service-node-config"></a>Service node</h2></div></div></div>
        
        <p>Source:
                <code class="filename">../katzenpost/docker/voting_mixnet/servicenode1/katzenpost.toml</code></p>
        <pre class="programlisting">[Server]
  Identifier = "servicenode1"
  WireKEM = "xwing"
  PKISignatureScheme = "Ed448-Dilithium3"
  Addresses = ["tcp://127.0.0.1:30007", "quic://[::1]:30008"]
  MetricsAddress = "127.0.0.1:30009"
  DataDir = "/voting_mixnet/servicenode1"
  IsGatewayNode = false
  IsServiceNode = true

[Logging]
  Disable = false
  File = "katzenpost.log"
  Level = "INFO"

[ServiceNode]

  [[ServiceNode.Kaetzchen]]
    Capability = "echo"
    Endpoint = "+echo"
    Disable = false

  [[ServiceNode.Kaetzchen]]
    Capability = "testdest"
    Endpoint = "+testdest"
    Disable = false

  [[ServiceNode.CBORPluginKaetzchen]]
    Capability = "spool"
    Endpoint = "+spool"
    Command = "/voting_mixnet/memspool.alpine"
    MaxConcurrency = 1
    Disable = false
    [ServiceNode.CBORPluginKaetzchen.Config]
      data_store = "/voting_mixnet/servicenode1/memspool.storage"
      log_dir = "/voting_mixnet/servicenode1"

  [[ServiceNode.CBORPluginKaetzchen]]
    Capability = "pigeonhole"
    Endpoint = "+pigeonhole"
    Command = "/voting_mixnet/pigeonhole.alpine"
    MaxConcurrency = 1
    Disable = false
    [ServiceNode.CBORPluginKaetzchen.Config]
      db = "/voting_mixnet/servicenode1/map.storage"
      log_dir = "/voting_mixnet/servicenode1"

  [[ServiceNode.CBORPluginKaetzchen]]
    Capability = "panda"
    Endpoint = "+panda"
    Command = "/voting_mixnet/panda_server.alpine"
    MaxConcurrency = 1
    Disable = false
    [ServiceNode.CBORPluginKaetzchen.Config]
      fileStore = "/voting_mixnet/servicenode1/panda.storage"
      log_dir = "/voting_mixnet/servicenode1"
      log_level = "INFO"

  [[ServiceNode.CBORPluginKaetzchen]]
    Capability = "http"
    Endpoint = "+http"
    Command = "/voting_mixnet/proxy_server.alpine"
    MaxConcurrency = 1
    Disable = false
    [ServiceNode.CBORPluginKaetzchen.Config]
      host = "localhost:4242"
      log_dir = "/voting_mixnet/servicenode1"
      log_level = "DEBUG"

[PKI]
  [PKI.Voting]

    [[PKI.Voting.Authorities]]
      Identifier = "auth1"
      IdentityPublicKey = "-----BEGIN ED448-DILITHIUM3 PUBLIC KEY-----\nfvcvAfUpeu7lMHjQBw [...] Gpi8ovBXl9ENIHLwA=\n-----END ED448-DILITHIUM3 PUBLIC KEY-----\n"
      PKISignatureScheme = "Ed448-Dilithium3"
      LinkPublicKey = "-----BEGIN XWING PUBLIC KEY-----\nsxxS04mftoEmwjxE/w [...] expP2fbERpGQwVNg==\n-----END XWING PUBLIC KEY-----\n"
      WireKEMScheme = "xwing"
      Addresses = ["tcp://127.0.0.1:30001"]

    [[PKI.Voting.Authorities]]
      Identifier = "auth2"
      IdentityPublicKey = "-----BEGIN ED448-DILITHIUM3 PUBLIC KEY-----\n5nsy6uFQ1782fZ+iYn [...] Sdr2xoinylYJr/3AA=\n-----END ED448-DILITHIUM3 PUBLIC KEY-----\n"
      PKISignatureScheme = "Ed448-Dilithium3"
      LinkPublicKey = "-----BEGIN XWING PUBLIC KEY-----\nkQzCJvaS6jg06szLea [...] PG1Bzx1JwHGFxRBQ==\n-----END XWING PUBLIC KEY-----\n"
      WireKEMScheme = "xwing"
      Addresses = ["tcp://127.0.0.1:30002"]

    [[PKI.Voting.Authorities]]
      Identifier = "auth3"
      IdentityPublicKey = "-----BEGIN ED448-DILITHIUM3 PUBLIC KEY-----\nJzkFpS035de1PmA2MM [...] jo6Z7is9GLs0YxVQA=\n-----END ED448-DILITHIUM3 PUBLIC KEY-----\n"
      PKISignatureScheme = "Ed448-Dilithium3"
      LinkPublicKey = "-----BEGIN XWING PUBLIC KEY-----\n+pIUsgEGwHa8k4GZcb [...] 1mxoc+4kcgZWuOAg==\n-----END XWING PUBLIC KEY-----\n"
      WireKEMScheme = "xwing"
      Addresses = ["tcp://127.0.0.1:30003"]

[Management]
  Enable = true
  Path = "/voting_mixnet/servicenode1/management_sock"

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

[Debug]
  NumSphinxWorkers = 16
  NumServiceWorkers = 3
  NumGatewayWorkers = 3
  NumKaetzchenWorkers = 4
  SchedulerExternalMemoryQueue = false
  SchedulerQueueSize = 0
  SchedulerMaxBurst = 16
  UnwrapDelay = 250
  GatewayDelay = 500
  ServiceDelay = 500
  KaetzchenDelay = 750
  SchedulerSlack = 150
  SendSlack = 50
  DecoySlack = 15000
  ConnectTimeout = 60000
  HandshakeTimeout = 30000
  ReauthInterval = 30000
  SendDecoyTraffic = false
  DisableRateLimit = false
  GenerateOnly = false</pre>
    </div>

    
</div>
    <div class="chapter"><div class="titlepage"><div><div><h1 class="title"><a name="gensphinx"></a>Chapter&nbsp;4.&nbsp;Appendix: Using <span class="emphasis"><em>gensphinx</em></span></h1></div></div></div>
    
    <p>To Do</p>

</div>
</div></body></html>
