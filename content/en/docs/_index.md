---
title: "Katzenpost Documentation"
linkTitle: "Documentation"
draft: false
menu: {main: {weight: 70}}
type: "base"
no_list: true
body_class: "td-no-sidebar"
---

<p class="lead">Choose your audience.</p>

## For users

You wish to use a Katzenpost client application to communicate.

<div class="row row-cols-1 g-3 mb-5">
  <div class="col">
    <div class="card h-100 doc-card doc-card--coming">
      <div class="card-body">
        <h5 class="card-title"><span class="doc-card-icon">🐈</span> Namenlos public mixnet <span class="badge text-bg-dark ms-2">coming soon</span></h5>
        <p class="card-text">A public Katzenpost mix network that anyone may use, without the burden of operating their own. Documentation will appear here once the network is open to the public.</p>
      </div>
    </div>
  </div>
</div>

## For operators

You wish to run your own Katzenpost mix network with friends and collaborators.

<div class="row row-cols-1 row-cols-md-2 g-3 mb-5">
  <div class="col">
    <a class="card h-100 doc-card" href="/docs/admin_guide/">
      <div class="card-body">
        <h5 class="card-title"><span class="doc-card-icon">📖</span> Admin Guide</h5>
        <p class="card-text">Deploying and operating Katzenpost servers — installation, configuration, the Docker test mixnet, NAT considerations, and a full configuration appendix.</p>
      </div>
    </a>
  </div>
  <div class="col">
    <a class="card h-100 doc-card" href="/docs/run_katzenpost_mixnode_docker/">
      <div class="card-body">
        <h5 class="card-title"><span class="doc-card-icon">🐳</span> Run a Mix Server in Docker</h5>
        <p class="card-text">A focused recipe for running a single Katzenpost mix server inside a Docker container, intended for operators who simply want to participate in an existing mix network.</p>
      </div>
    </a>
  </div>
  <div class="col">
    <a class="card h-100 doc-card" href="/docs/build_from_source/">
      <div class="card-body">
        <h5 class="card-title"><span class="doc-card-icon">🔧</span> Build from source</h5>
        <p class="card-text">Pinned versions of the Katzenpost stack and brief instructions for building each component (kpclientd, thin clients, katzenqt, server-side) from source.</p>
      </div>
    </a>
  </div>
</div>

## For application developers

You wish to build software that integrates with Katzenpost — custom clients, services, or higher-level protocols layered atop the mixnet.

<div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-3 mb-5">
  <div class="col">
    <a class="card h-100 doc-card" href="/docs/thin_client_api_reference/">
      <div class="card-body">
        <h5 class="card-title"><span class="doc-card-icon">📘</span> Thin Client API Reference</h5>
        <p class="card-text">Complete API reference for the Go, Rust, and Python thin client libraries.</p>
      </div>
    </a>
  </div>
  <div class="col">
    <a class="card h-100 doc-card" href="/docs/thin_client_howto/">
      <div class="card-body">
        <h5 class="card-title"><span class="doc-card-icon">📗</span> Thin Client How-to Guide</h5>
        <p class="card-text">Task-oriented guides for accomplishing common operations with the thin client API.</p>
      </div>
    </a>
  </div>
  <div class="col">
    <a class="card h-100 doc-card" href="/docs/pigeonhole_explained/">
      <div class="card-body">
        <h5 class="card-title"><span class="doc-card-icon">🕊️</span> Understanding Pigeonhole</h5>
        <p class="card-text">A high-level introduction to the Pigeonhole anonymous storage protocol for application developers.</p>
      </div>
    </a>
  </div>
  <div class="col">
    <a class="card h-100 doc-card" href="/docs/build_from_source/">
      <div class="card-body">
        <h5 class="card-title"><span class="doc-card-icon">🔧</span> Build from source</h5>
        <p class="card-text">Pinned versions of the Katzenpost stack and brief instructions for building each component (kpclientd, thin clients, katzenqt) from source.</p>
      </div>
    </a>
  </div>
</div>

## For core developers

You wish to contribute code to Katzenpost itself.

<div class="row row-cols-1 row-cols-md-2 g-3 mb-5">
  <div class="col">
    <a class="card h-100 doc-card" href="/docs/specs/">
      <div class="card-body">
        <h5 class="card-title"><span class="doc-card-icon">🛠️</span> Design Specifications</h5>
        <p class="card-text">The protocol specifications that the implementation must honour: Sphinx, KEMSphinx, the wire protocol, the directory authority, replay detection, and more.</p>
      </div>
    </a>
  </div>
  <div class="col">
    <a class="card h-100 doc-card" href="https://github.com/katzenpost/katzenpost">
      <div class="card-body">
        <h5 class="card-title"><span class="doc-card-icon">🐙</span> Source Repository</h5>
        <p class="card-text">The Katzenpost monorepo on GitHub: server, dirauth, client, courier, replica, and core. Issues, pull requests, and discussions live here.</p>
      </div>
    </a>
  </div>
</div>

## For academics

You are a mathematician, computer scientist, security researcher, or hacker investigating the design.

<div class="row row-cols-1 row-cols-md-2 g-3 mb-5">
  <div class="col">
    <a class="card h-100 doc-card" href="https://arxiv.org/abs/2501.02933">
      <div class="card-body">
        <h5 class="card-title"><span class="doc-card-icon">📄</span> Echomix paper</h5>
        <p class="card-text"><em>Echomix: a Strong Anonymity System with Messaging.</em> The principal academic treatment of the Katzenpost design (arXiv).</p>
      </div>
    </a>
  </div>
  <div class="col">
    <a class="card h-100 doc-card" href="/docs/threat_model/">
      <div class="card-body">
        <h5 class="card-title"><span class="doc-card-icon">🔒</span> Threat Model</h5>
        <p class="card-text">An evolving treatment of Katzenpost's security assumptions, attack scenarios, and mitigation strategies. <a href="/research/Threat_Model_Doc.pdf">PDF</a>.</p>
      </div>
    </a>
  </div>
  <div class="col">
    <a class="card h-100 doc-card" href="/research/Literature_overview__website_version.pdf">
      <div class="card-body">
        <h5 class="card-title"><span class="doc-card-icon">📚</span> Literature Review</h5>
        <p class="card-text">A curated review of the academic literature underpinning Katzenpost's design decisions.</p>
      </div>
    </a>
  </div>
  <div class="col">
    <a class="card h-100 doc-card" href="/docs/audio_eng/">
      <div class="card-body">
        <h5 class="card-title"><span class="doc-card-icon">🎧</span> Audio Engineering Considerations</h5>
        <p class="card-text">A technical report on the challenges of carrying voice traffic through a modern mix network, with attention to usability and scalability. <a href="/research/Audio_Engineering_Considerations_for_a_Modern_Mixnet.pdf">PDF</a>.</p>
      </div>
    </a>
  </div>
  <div class="col">
    <a class="card h-100 doc-card" href="/docs/specs/">
      <div class="card-body">
        <h5 class="card-title"><span class="doc-card-icon">🛠️</span> Design Specifications</h5>
        <p class="card-text">The full set of protocol specifications. Useful reading for anyone investigating the design in depth.</p>
      </div>
    </a>
  </div>
</div>
