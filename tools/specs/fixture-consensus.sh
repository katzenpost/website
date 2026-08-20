#!/bin/sh
# Rebuild PUBLIC TEST DATA with an exact source export; run Go only in Podman.
set -eu

tool_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_dir=$(CDPATH= cd -- "$tool_dir/../.." && pwd)
source_repo=${KATZENPOST_SOURCE:-"$repo_dir/../katzenpost"}
module_cache=${KATZENPOST_GOMODCACHE:-"$HOME/.cache/katzenpost/kno/gomodcache"}
build_cache=${KATZENPOST_GOCACHE:-"$HOME/.cache/katzenpost/kno/gobuild"}
container_image=${FIXTURE_IMAGE:-localhost/kno-build-debian13-go1.26.10:latest}
output=${1:-"$repo_dir/static/docs/specs/dirauth/conformance.json"}
behavior_output=${2:-"$(dirname "$output")/behavior-vectors.json"}
expected_tag=33b06e7e1b7f561c7dffc0cad135760ae3296b46
expected_commit=6f6b13d4524ec2da68ca3ba18fefe4a181af8a04

test "$(git -C "$source_repo" rev-parse v0.0.107)" = "$expected_tag"
test "$(git -C "$source_repo" rev-parse 'v0.0.107^{commit}')" = "$expected_commit"
test -d "$module_cache"
test -d "$build_cache"
work_dir=$(mktemp -d "${TMPDIR:-/tmp}/dirauth-fixture.XXXXXXXX")
trap 'rm -rf "$work_dir"' EXIT HUP INT TERM
mkdir "$work_dir/source" "$work_dir/build"
git -C "$source_repo" archive "$expected_commit" > "$work_dir/source.tar"
tar -xf "$work_dir/source.tar" -C "$work_dir/source"
cp "$tool_dir/fixture-state_test.go" "$work_dir/source/authority/voting/server/dirauth_fixture_test.go"
mkdir "$work_dir/hpqc"
if [ "${FIXTURE_SOURCE_TESTS:-0}" = 1 ]; then
  hpqc_repo=${HPQC_SOURCE:-"$repo_dir/../hpqc"}
  # Module ZIPs omit the hybrid tests' symlinks. Export the required revision
  # with its test vectors and use a disposable modfile for these tests only.
  test "$(git -C "$hpqc_repo" rev-parse 'v0.0.93^{commit}')" = d836052c3ad7461abc2bdb02a7e0867b88665123
  git -C "$hpqc_repo" archive v0.0.93 > "$work_dir/hpqc.tar"
  tar -xf "$work_dir/hpqc.tar" -C "$work_dir/hpqc"
fi

# :O provides a disposable writable build-cache overlay; its backing cache and
# the module cache remain unchanged. No network or host toolchain is needed.
podman run --rm --network=none \
  -v "$work_dir/source:/source:ro" \
  -v "$work_dir/build:/build:rw" \
  -v "$work_dir/hpqc:/hpqc:ro" \
  -v "$tool_dir/fixture-consensus.go:/fixture.go:ro" \
  -v "$module_cache:/gomodcache:ro" \
  -v "$build_cache:/gocache:O" \
  -e GOMODCACHE=/gomodcache -e GOCACHE=/gocache \
  -e GOPROXY=off -e GOSUMDB=off -e GOTOOLCHAIN=local \
  -e GOFLAGS=-mod=readonly -e KATZENPOST_EPOCH_DURATION=20m \
  -e FIXTURE_SOURCE_TESTS="${FIXTURE_SOURCE_TESTS:-0}" -e GOMAXPROCS=2 \
  -w /source "$container_image" sh -ec '
    if [ "$FIXTURE_SOURCE_TESTS" = 1 ]; then
      go test -short -count=1 -timeout=12m ./authority/voting/server/... ./core/pki ./core/cert ./core/wire/...
      cp go.mod /build/testing.mod
      cp go.sum /build/testing.sum
      go mod edit -modfile=/build/testing.mod -replace=github.com/katzenpost/hpqc=/hpqc
      go test -modfile=/build/testing.mod -short -count=1 -timeout=5m \
        github.com/katzenpost/hpqc/kem/combiner github.com/katzenpost/hpqc/sign/hybrid
    fi
    go build -o /build/fixture /fixture.go
    /build/fixture > /build/conformance.json
    /build/fixture > /build/repeat.json
    cmp /build/conformance.json /build/repeat.json
    go test -c -o /build/state-fixture ./authority/voting/server
    export DIRAUTH_DOCUMENT_FIXTURE=/build/conformance.json
    DIRAUTH_BEHAVIOR_FIXTURE=/build/behavior.json /build/state-fixture \
      -test.run "^TestDirauth(BehaviorFixture|ReceiverNormalization|ReceiverTaggedNullUpload)$" -test.count=1 -test.timeout=2m
    DIRAUTH_BEHAVIOR_FIXTURE=/build/behavior-repeat.json /build/state-fixture \
      -test.run "^TestDirauth(BehaviorFixture|ReceiverNormalization|ReceiverTaggedNullUpload)$" -test.count=1 -test.timeout=2m
    cmp /build/behavior.json /build/behavior-repeat.json
  '
cp "$work_dir/build/conformance.json" "$output"
cp "$work_dir/build/behavior.json" "$behavior_output"
printf 'Verified deterministic fixture: %s\n' "$output"
printf 'Verified tagged behavior vectors: %s\n' "$behavior_output"
