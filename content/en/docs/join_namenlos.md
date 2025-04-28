---
title: "How to Use the Namenlos Mixnet"
linkTitle: ""
description: ""
categories: [""]
tags: [""]
author: []
version: 0
draft: false
slug: "/howto_use_namenlos_mixnet/"
---

<i>namenlos</i> is a Katzenpost mixnet ran by the KP team.
It is our canonical example of a Katzenpost-type mixnet instance.

```
# To clone namenlos, you must authenticate
git clone git@github.com:katzenpost/namenlos.git

# To clone the rest, you do not need to authenticate
git clone https://github.com/katzenpost/katzenpost
git clone https://github.com/katzenpost/thin_client

# Build kpclientd
cd katzenpost/client2/
make makeclientdaemon
cd ../../

# Install thin_client for Python
cd thin_client
# Make a Python venv and install the Python thin_client module in the Python venv
python3 -m venv thin_client-venv
source thin_client-venv/bin/activate
pip install jinja2 matplotlib cartopy geoip2
pip install .
cd ../

# Install the config file and the daemon into
sudo cp namenlos/configs/client2.toml /usr/local/etc/namenlos.toml
sudo cp katzenpost/client2/cmd/kpclientd/kpclientd /usr/local/bin/kpclientd

# In a terminal run kpclientd with the namenlos config:
kpclientd -c /usr/local/etc/namenlos.toml

# In another terminal run the programs that interact with kpclientd's
# thin_client interface in the Python venv:
source thin_client/thin_client-venv/bin/activate

# Run ping:
python3 thin_client/examples/echo_ping.py

# Fetch the PKI document for the current consensus:
python3 thin_client/examples/fetch_pki_doc.py

# Generate a network_status.html file for the current network status:
python3 thin_client/examples/mixnet_status.py

# You will need to install GeoLite2-City_20241025/GeoLite2-City.mmdb to make
# the next command work.
#
# Generate a world map of the namenlos network:
python3 thin_client/examples/world_map.py
```
