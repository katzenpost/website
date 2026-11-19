---
title: "Download"
linkTitle: "Download"
description: ""
slug: "/download/"
menu: {main: {weight: 60}}
type: "pages"
---

<div class="downloads">
<div class="dl-lead">
<p>Start with hushphone, the client we recommend today: its groups carry chat, voice messages, polls and files.</p>
<ul>
<li>Install and start kpclientd first.</li>
<li>Every app here connects to it over a unix domain socket or TCP.</li>
<li>None of them works without it.</li>
</ul>
</div>
<div class="row g-4">
<div class="col-lg-6">
<div class="dl-card">
<div class="dl-head"><i class="fa-brands fa-android" aria-hidden="true"></i><div><h2>Android</h2><p>Android 13 or later</p></div></div>
<h3>kpclientd-android <span class="dl-ver">v1.2.0</span></h3>
<div class="dl-btns">
<a class="btn btn-lg btn-primary" href="https://github.com/katzenpost/kpclientd-android/releases/download/v1.2.0/kpclientd-android-v1.2.0-arm64-v8a.apk"><i class="fa fa-download" aria-hidden="true"></i>Phone APK</a>
<a class="btn btn-lg btn-outline-primary" href="https://github.com/katzenpost/kpclientd-android/releases/download/v1.2.0/kpclientd-android-v1.2.0-x86_64.apk"><i class="fa fa-download" aria-hidden="true"></i>Emulator APK</a>
</div>
<p class="dl-meta"><a href="https://github.com/katzenpost/kpclientd-android/releases/download/v1.2.0/SHA256SUMS">checksums</a> · <a href="https://github.com/katzenpost/kpclientd-android/tree/v1.2.0">source</a></p>
<h3>hushphone <span class="dl-ver">v0.3.6</span></h3>
<div class="dl-btns">
<a class="btn btn-lg btn-primary" href="https://github.com/katzenpost/hushphone/releases/download/v0.3.6/hushphone-v0.3.6-arm64-v8a.apk"><i class="fa fa-download" aria-hidden="true"></i>Phone APK</a>
<a class="btn btn-lg btn-outline-primary" href="https://github.com/katzenpost/hushphone/releases/download/v0.3.6/hushphone-v0.3.6-x86_64.apk"><i class="fa fa-download" aria-hidden="true"></i>Emulator APK</a>
</div>
<p class="dl-meta"><a href="https://github.com/katzenpost/hushphone/releases/download/v0.3.6/SHA256SUMS">checksums</a> · <a href="https://github.com/katzenpost/hushphone/tree/v0.3.6">source</a></p>
<h3>Start</h3>
<p class="dl-run">Open KP Daemon and start the daemon. Open hushphone and allow it when KP Daemon asks.</p>
</div>
</div>
<div class="col-lg-6">
<div class="dl-card">
<div class="dl-head"><i class="fa-brands fa-linux" aria-hidden="true"></i><div><h2>Linux desktop</h2><p>Debian 13 or Ubuntu 24.04, amd64</p></div></div>
<h3>kpclientd <span class="dl-ver">0.0.111</span></h3>
<div class="dl-btns">
<a class="btn btn-lg btn-primary" href="/downloads/kpclientd_0.0.111_amd64.deb"><i class="fa fa-download" aria-hidden="true"></i>.deb</a>
</div>
<p class="dl-meta">SHA-256 <code>ab3fb57b05cd2fc33f9044779a1f82d8b54757d3d85d14542fbd19df14df684d</code></p>
<p class="dl-meta"><a href="https://github.com/katzenpost/katzenpost/tree/9d877d6c9dc0f8a3c4bfa69bcce311337fb89f6e">source</a></p>
<h3>hushphone <span class="dl-ver">v0.3.6</span></h3>
<div class="dl-btns">
<a class="btn btn-lg btn-primary" href="https://github.com/katzenpost/hushphone/releases/download/v0.3.6/hushphone-v0.3.6-debian-13-amd64.deb"><i class="fa fa-download" aria-hidden="true"></i>Debian 13 .deb</a>
<a class="btn btn-lg btn-primary" href="https://github.com/katzenpost/hushphone/releases/download/v0.3.6/hushphone-v0.3.6-ubuntu-24.04-amd64.deb"><i class="fa fa-download" aria-hidden="true"></i>Ubuntu 24.04 .deb</a>
</div>
<p class="dl-meta"><a href="https://github.com/katzenpost/hushphone/releases/download/v0.3.6/hushphone-v0.3.6-linux-x86_64.tar.gz">tarball</a> · <a href="https://github.com/katzenpost/hushphone/releases/download/v0.3.6/SHA256SUMS">checksums</a> · <a href="https://github.com/katzenpost/hushphone/tree/v0.3.6">source</a></p>
<h3>Install and start</h3>
<pre class="dl-cmd">sudo apt install ./kpclientd_*.deb ./hushphone-*.deb
systemctl --user enable --now kpclientd
hushphone</pre>
</div>
</div>
</div>
<details class="dl-source"><summary>Build kpclientd from source</summary>
<pre class="dl-cmd">git clone --depth 1 https://github.com/katzenpost/katzenpost
cd katzenpost && make kpclientd
cmd/kpclientd/kpclientd -c docker/client-configs/namenlos.toml</pre>
<p class="dl-meta">Needs Go 1.26 or later and a C compiler.</p>
</details>
<h2 class="dl-h">Experimental chat clients</h2>
<div class="row g-3">
<div class="col-6 col-md-3"><div class="dl-mini"><h3>jam</h3><a class="btn btn-sm btn-outline-primary" href="https://github.com/katzenpost/jam/releases/tag/v0.2.0">v0.2.0</a><a class="dl-meta" href="https://github.com/katzenpost/jam/tree/v0.2.0">source</a></div></div>
<div class="col-6 col-md-3"><div class="dl-mini"><h3>frank_chat</h3><a class="btn btn-sm btn-outline-primary" href="https://github.com/katzenpost/frank_chat/releases/tag/v0.4.1">v0.4.1</a><a class="dl-meta" href="https://github.com/katzenpost/frank_chat/tree/v0.4.1">source</a></div></div>
<div class="col-6 col-md-3"><div class="dl-mini"><h3>katzenqt</h3><a class="btn btn-sm btn-outline-primary" href="https://github.com/katzenpost/katzenqt">source</a></div></div>
<div class="col-6 col-md-3"><div class="dl-mini"><h3>katzenrns</h3><a class="btn btn-sm btn-outline-primary" href="https://github.com/katzenpost/katzenrns">source</a></div></div>
</div>
<h2 class="dl-h">Running a mixnet</h2>
<p>Build from <a href="https://github.com/katzenpost/katzenpost">source</a> or install with <a href="https://github.com/katzenpost/kno">kno</a>.</p>
</div>
