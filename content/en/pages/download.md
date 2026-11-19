---
title: "Download"
linkTitle: "Download"
description: ""
slug: "/download/"
menu: {main: {weight: 60}}
type: "pages"
---

## kpclientd

Every app on this page connects to kpclientd running on the same computer
or phone, over a unix domain socket or TCP. Without kpclientd running, they
do not work.

- Android 13 or later, phones:
  [kpclientd-android v1.2.0 arm64-v8a APK](https://github.com/katzenpost/kpclientd-android/releases/download/v1.2.0/kpclientd-android-v1.2.0-arm64-v8a.apk)
  ([source](https://github.com/katzenpost/kpclientd-android/tree/v1.2.0))
- Android 13 or later, emulators:
  [kpclientd-android v1.2.0 x86_64 APK](https://github.com/katzenpost/kpclientd-android/releases/download/v1.2.0/kpclientd-android-v1.2.0-x86_64.apk)
  ([source](https://github.com/katzenpost/kpclientd-android/tree/v1.2.0))
- Debian 13 and Ubuntu 24.04, amd64:
  [kpclientd 0.0.111 .deb](/downloads/kpclientd_0.0.111_amd64.deb)
  ([source](https://github.com/katzenpost/katzenpost/tree/9d877d6c9dc0f8a3c4bfa69bcce311337fb89f6e))

Checksums:
[Android SHA256SUMS](https://github.com/katzenpost/kpclientd-android/releases/download/v1.2.0/SHA256SUMS).
SHA-256 of the .deb:

```
ab3fb57b05cd2fc33f9044779a1f82d8b54757d3d85d14542fbd19df14df684d
```

From source, with Go and a C compiler:

```
git clone https://github.com/katzenpost/katzenpost
cd katzenpost
make kpclientd
cmd/kpclientd/kpclientd -c client.toml
```

`client.toml` is the
[namenlos client config](https://github.com/katzenpost/kno/blob/main/data/networks/namenlos/.generated/configs/client.toml).

## Android

Android 13 or later. Most phones need arm64-v8a.

1. Download both:
   - [hushphone v0.3.6 arm64-v8a APK](https://github.com/katzenpost/hushphone/releases/download/v0.3.6/hushphone-v0.3.6-arm64-v8a.apk)
     ([source](https://github.com/katzenpost/hushphone/tree/v0.3.6))
   - [kpclientd-android v1.2.0 arm64-v8a APK](https://github.com/katzenpost/kpclientd-android/releases/download/v1.2.0/kpclientd-android-v1.2.0-arm64-v8a.apk)
     ([source](https://github.com/katzenpost/kpclientd-android/tree/v1.2.0))
2. Open each file to install it. Android may ask you to allow installs from
   your browser.
3. Open **KP Daemon** and start it.
4. Open **hushphone**. When KP Daemon asks, allow it.

Emulators:
[hushphone x86_64 APK](https://github.com/katzenpost/hushphone/releases/download/v0.3.6/hushphone-v0.3.6-x86_64.apk)
([source](https://github.com/katzenpost/hushphone/tree/v0.3.6)),
[kpclientd-android x86_64 APK](https://github.com/katzenpost/kpclientd-android/releases/download/v1.2.0/kpclientd-android-v1.2.0-x86_64.apk)
([source](https://github.com/katzenpost/kpclientd-android/tree/v1.2.0)).

## Linux desktop

Debian 13 or Ubuntu 24.04, amd64.

1. Download hushphone for your system, and kpclientd:
   - Debian 13: [hushphone v0.3.6 .deb](https://github.com/katzenpost/hushphone/releases/download/v0.3.6/hushphone-v0.3.6-debian-13-amd64.deb)
     ([source](https://github.com/katzenpost/hushphone/tree/v0.3.6))
   - Ubuntu 24.04: [hushphone v0.3.6 .deb](https://github.com/katzenpost/hushphone/releases/download/v0.3.6/hushphone-v0.3.6-ubuntu-24.04-amd64.deb)
     ([source](https://github.com/katzenpost/hushphone/tree/v0.3.6))
   - Both: [kpclientd 0.0.111 .deb](/downloads/kpclientd_0.0.111_amd64.deb)
     ([source](https://github.com/katzenpost/katzenpost/tree/9d877d6c9dc0f8a3c4bfa69bcce311337fb89f6e))
2. Install them, in a terminal in the folder with the files:

   ```
   sudo apt install ./hushphone-v0.3.6-*-amd64.deb ./kpclientd_0.0.111_amd64.deb
   ```

3. Start kpclientd:

   ```
   systemctl --user enable --now kpclientd
   ```

4. Start hushphone from your applications menu, or run `hushphone`.

Other Linux, x86_64:
[hushphone v0.3.6 tarball](https://github.com/katzenpost/hushphone/releases/download/v0.3.6/hushphone-v0.3.6-linux-x86_64.tar.gz)
([source](https://github.com/katzenpost/hushphone/tree/v0.3.6)), with
kpclientd built from source as above.

Checksums:
[hushphone SHA256SUMS](https://github.com/katzenpost/hushphone/releases/download/v0.3.6/SHA256SUMS).

## Experimental chat clients

- katzenqt: no release yet ([source](https://github.com/katzenpost/katzenqt))
- katzenrns: no release yet ([source](https://github.com/katzenpost/katzenrns))
- jam: [v0.2.0 release](https://github.com/katzenpost/jam/releases/tag/v0.2.0)
  ([source](https://github.com/katzenpost/jam/tree/v0.2.0))
- frank_chat: [v0.4.1 release](https://github.com/katzenpost/frank_chat/releases/tag/v0.4.1)
  ([source](https://github.com/katzenpost/frank_chat/tree/v0.4.1))

## Servers

The server-side components can be built from
[source](https://github.com/katzenpost/katzenpost) or installed using
[kno](https://github.com/katzenpost/kno).
