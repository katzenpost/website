---
title:
linkTitle: Run a Katzenpost Mix server in a Docker container
description: ""
categories: [""]
tags: [""]
author: []
version: 0
draft: false
slug: "/run_katzenpost_mixnode_docker/"
---

# Run a Katzenpost Mix server in a Docker container

## Prerequisites

* Access to the `namenlos` git repo

## Preparing the host filesystem

```bash
mkdir katzenpost-mix
cd katzenpost-mix
mkdir {conf,data}
chmod 700 data
```

All further actions are performed from the `katzenpost-mix` directory.

## Building the Docker image

* Create `Dockerfile`:

    ```docker
    FROM golang:bookworm AS builder

    LABEL authors="<ops@cryptonymity.net>"

    RUN \
        cd /go && \
        git clone https://github.com/katzenpost/katzenpost  && \
        cd katzenpost && \
        go mod tidy && \
        cd cmd/server && go build

    FROM debian:bookworm AS deploy

    COPY --from=builder /go/katzenpost/cmd/server/server /usr/bin/server

    EXPOSE 8181

    ARG uid=1000
    ARG gid=1000

    RUN \
        mkdir -p /home/user && \
        echo "user:x:${uid}:${gid}:User,,,:/home/user:/bin/bash" >> /etc/passwd && \
        echo "user:x:${uid}:" >> /etc/group

    USER user
    ENV HOME=/home/user

    ENTRYPOINT ["/usr/bin/server","-f","/conf/katzenpost.toml"]
    ```

* Build Docker image:

```bash
docker build -t katzenpost/mix --build-arg uid=$(id -u) --build-arg gid=$(id -g) .
```

* Create `service.sh` (modify to match your port) to manage the server:

    ```bash
    #!/bin/bash

    CMD=${1:-start}
    case ${CMD} in
        genkeys)
            MODE="-ti --rm"
            EXEC="/usr/bin/server -g"
            ;;
        start)
            MODE="-d --restart=unless-stopped"
            EXEC=""
            ;;
        stop)
            docker stop katzenpost-mix
            docker rm katzenpost-mix
            exit
            ;;
        *)
            echo "unknown command"
            exit 1
            ;;
    esac

    docker run ${MODE} \
        --name katzenpost-mix -h katzenpost-mix \
        -p 0.0.0.0:<port>:8181 \
        -v $(pwd)/conf:/conf \
        -v $(pwd)/data:/var/lib/katzenpost \
        katzenpost/mix ${EXEC}
    ```

    Always run this script while in the `katzenpost-mix` directory.

## Creating a configuration file

* Create a new file named `<yourname>-pq-mixserver.toml` in `<namenlos.repo>/configs/SSOT/mixes` and adjust `Identifier` and  IP/port setting in `Addresses`:

    ```toml
    [Server]
    Identifier = "<yourname>"
    PKISignatureScheme = "Ed25519 Sphincs+"
    WireKEM = "KYBER768-X25519"
    Addresses = [ "tcp://<public-ipv4>:<port>" ]
    BindAddresses = [ "tcp://0.0.0.0:8181" ]
    DataDir = "/var/lib/katzenpost"
    IsGatewayNode = false
    IsServiceNode = false

    [Logging]
    Disable = false
    File = ""
    Level = "NOTICE"

    ```

* Build the configuration file `conf/katzenpost.toml`:

    1. In the `namenlos` repo, change into the `configs` directory and run `make`.

    2. Copy the generated configuration file:

    ```
    cp <namelos.repo>/configs/<yourname>-pq-mixserver.toml conf/katzenpost.toml
    ```

## Generating and extracting keys

* Run the server to generate the keys:

```
./service.sh genkeys
```

* Check that keys (`*.pem`) have been created in the `data/` directory and copy the public identity key to the `namenlos` repo:

```bash
cp data/identity.public.pem <namelos.repo>/keys/mixserver-keys/<yourname>_mix_id_pub_key.pem
```

* Update the repo:

```bash
cd <namenlos.repo>/configs
make
git commit -a
git push
```

## Starting/stopping the server
```bash
cd katzenpost-mix
./service.sh [start|stop]
```
