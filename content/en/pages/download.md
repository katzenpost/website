---
title: "Download and install a client"
linkTitle: "Download"
description: ""
slug: "/download/"
menu: {main: {weight: 60}}
type: "pages"
---

<div class="downloads">
<p class="dl-lead">Before you can use a client you need the daemon, kpclientd. Every app here connects to it over a unix domain socket or TCP, and none of them works without it, so install and start kpclientd first. The client we recommend today is hushphone: its groups carry chat, voice messages, polls and files.</p>
<div class="row g-4">
<div class="col-lg-6">
<div class="dl-card">
<div class="dl-head"><i class="fa-brands fa-android" aria-hidden="true"></i><div><h2>Android</h2><p>Android 13 or later</p></div></div>
<h3>1. Download</h3>
<p class="dl-run">On your phone, download both apps.</p>
<h4>kpclientd-android <span class="dl-ver">{{< release kpclientd-android >}}</span></h3>
<div class="dl-btns">
<a class="btn btn-lg btn-primary" href="{{< release kpclientd-android "kpclientd-android-TAG-arm64-v8a.apk" >}}"><i class="fa fa-download" aria-hidden="true"></i>Phone APK</a>
<a class="btn btn-lg btn-outline-primary" href="{{< release kpclientd-android "kpclientd-android-TAG-x86_64.apk" >}}"><i class="fa fa-download" aria-hidden="true"></i>Emulator APK</a>
</div>
<p class="dl-meta"><a href="{{< release kpclientd-android "SHA256SUMS" >}}">checksums</a> · <a href="https://github.com/katzenpost/kpclientd-android/tree/{{< release kpclientd-android >}}">source</a></p>
<h4>hushphone <span class="dl-ver">{{< release hushphone >}}</span></h4>
<div class="dl-btns">
<a class="btn btn-lg btn-primary" href="{{< release hushphone "hushphone-TAG-arm64-v8a.apk" >}}"><i class="fa fa-download" aria-hidden="true"></i>Phone APK</a>
<a class="btn btn-lg btn-outline-primary" href="{{< release hushphone "hushphone-TAG-x86_64.apk" >}}"><i class="fa fa-download" aria-hidden="true"></i>Emulator APK</a>
</div>
<p class="dl-meta"><a href="{{< release hushphone "SHA256SUMS" >}}">checksums</a> · <a href="https://github.com/katzenpost/hushphone/tree/{{< release hushphone >}}">source</a></p>
<h3>2. Install</h3>
<p class="dl-run">Open each downloaded file and tap Install. If Android asks, allow your browser to install apps.</p>
<h3>3. Start</h3>
<p class="dl-run">Open KP Daemon and start the daemon. Then open hushphone and allow it when KP Daemon asks.</p>
</div>
</div>
<div class="col-lg-6">
<div class="dl-card">
<div class="dl-head"><i class="fa-brands fa-linux" aria-hidden="true"></i><div><h2>Linux desktop</h2><p>Debian 13 or Ubuntu 24.04, amd64</p></div></div>
<h3>1. Download</h3>
<p class="dl-run">Download kpclientd and hushphone for your system.</p>
{{< released katzenpost "kpclientd_VERSION_amd64.deb" >}}
<h4>kpclientd <span class="dl-ver">TAG</span></h4>
<div class="dl-btns">
<a class="btn btn-lg btn-primary" href="https://github.com/katzenpost/katzenpost/releases/download/TAG/kpclientd_VERSION_amd64.deb"><i class="fa fa-download" aria-hidden="true"></i>amd64 .deb</a>
{{< release katzenpost "kpclientd_VERSION_arm64.deb" "arm64 .deb" >}}
{{< release katzenpost "kpclientd-VERSION-1-x86_64.pkg.tar.zst" "Arch package" >}}
</div>
<p class="dl-meta"><a href="https://github.com/katzenpost/katzenpost/releases/download/TAG/SHA256SUMS">checksums</a> · <a href="https://github.com/katzenpost/katzenpost/tree/TAG">source</a></p>
{{< /released >}}
{{< released katzenpost "kpclientd_VERSION_amd64.deb" "not" >}}
<h4>kpclientd <span class="dl-ver">0.0.111</span></h4>
<div class="dl-btns">
<a class="btn btn-lg btn-primary" href="/downloads/kpclientd_0.0.111_amd64.deb"><i class="fa fa-download" aria-hidden="true"></i>.deb</a>
{{< release katzenpost "kpclientd-VERSION-1-x86_64.pkg.tar.zst" "Arch package" >}}
</div>
<p class="dl-meta">SHA-256 <code>067c47a3bcd118cc5734c042b0dda32e07f182a0d31ae7ea0a939961cf5130c0</code></p>
<p class="dl-meta"><a href="https://github.com/katzenpost/katzenpost/tree/a51103f99bdb293bf9571394863985476b770419">source</a></p>
{{< /released >}}
<h4>hushphone <span class="dl-ver">{{< release hushphone >}}</span></h4>
<div class="dl-btns">
<a class="btn btn-lg btn-primary" href="{{< release hushphone "hushphone-TAG-debian-13-amd64.deb" >}}"><i class="fa fa-download" aria-hidden="true"></i>Debian 13 .deb</a>
<a class="btn btn-lg btn-primary" href="{{< release hushphone "hushphone-TAG-ubuntu-24.04-amd64.deb" >}}"><i class="fa fa-download" aria-hidden="true"></i>Ubuntu 24.04 .deb</a>
{{< release hushphone "hushphone-TAG-arch-x86_64.pkg.tar.zst" "Arch package" >}}
</div>
<p class="dl-meta"><a href="{{< release hushphone "hushphone-TAG-linux-x86_64.tar.gz" >}}">tarball</a> · <a href="{{< release hushphone "SHA256SUMS" >}}">checksums</a> · <a href="https://github.com/katzenpost/hushphone/tree/{{< release hushphone >}}">source</a></p>
<h3>2. Install</h3>
<p class="dl-run">Open a terminal in the folder with the downloads and run the line for your system.</p>
<p class="dl-meta">Debian or Ubuntu</p>
<pre class="dl-cmd">sudo apt install ./kpclientd_*.deb ./hushphone-*.deb</pre>
{{< released hushphone "hushphone-TAG-arch-x86_64.pkg.tar.zst" >}}
<p class="dl-meta">Arch</p>
<pre class="dl-cmd">sudo pacman -U {{< released katzenpost "kpclientd-VERSION-1-x86_64.pkg.tar.zst" >}}./kpclientd-*.pkg.tar.zst {{< /released >}}./hushphone-*.pkg.tar.zst</pre>
{{< /released >}}
<p class="dl-meta">Nix package manager or NixOS, no download needed</p>
<pre class="dl-cmd">{{< nix katzenpost "#kpclientd" >}}
{{< nix hushphone >}}</pre>
<h3>3. Start</h3>
<p class="dl-run">Start the daemon, then hushphone.</p>
<pre class="dl-cmd">systemctl --user enable --now kpclientd
hushphone</pre>
</div>
</div>
</div>
<p class="dl-status">Not connecting? See the <a href="https://status.namenlos.network/">network status</a>.</p>
<details class="dl-source"><summary>Build kpclientd from source</summary>
<pre class="dl-cmd">git clone --depth 1 https://github.com/katzenpost/katzenpost
cd katzenpost && make kpclientd
curl -LO https://raw.githubusercontent.com/katzenpost/kno/main/data/networks/namenlos/.generated/configs/client.toml
cmd/kpclientd/kpclientd -c client.toml</pre>
<p class="dl-meta">Needs Go 1.26 or later and a C compiler.</p>
</details>
<h2 class="dl-h">Experimental chat clients</h2>
<div class="row g-3">
<div class="col-6 col-md-3"><div class="dl-mini"><h3>jam</h3><a class="btn btn-sm btn-outline-primary" href="https://github.com/katzenpost/jam/releases/tag/{{< release jam >}}">{{< release jam >}}</a><a class="dl-meta" href="https://github.com/katzenpost/jam/tree/{{< release jam >}}">source</a></div></div>
<div class="col-6 col-md-3"><div class="dl-mini"><h3>frank_chat</h3><a class="btn btn-sm btn-outline-primary" href="https://github.com/katzenpost/frank_chat/releases/tag/{{< release frank_chat >}}">{{< release frank_chat >}}</a><a class="dl-meta" href="https://github.com/katzenpost/frank_chat/tree/{{< release frank_chat >}}">source</a></div></div>
<div class="col-6 col-md-3"><div class="dl-mini"><h3>katzenqt</h3><a class="btn btn-sm btn-outline-primary" href="https://github.com/katzenpost/katzenqt">source</a></div></div>
<div class="col-6 col-md-3"><div class="dl-mini"><h3>katzenrns</h3><a class="btn btn-sm btn-outline-primary" href="https://github.com/katzenpost/katzenrns">source</a></div></div>
</div>
<h2 class="dl-h">Running a mixnet</h2>
<p>Build from <a href="https://github.com/katzenpost/katzenpost">source</a> or install with <a href="https://github.com/katzenpost/kno">kno</a>.</p>
</div>
