#!/usr/bin/env bash
# The sources must remain installable on XCP-ng 8.3, where the plugins run
# with python 2.7 (3.6 is also available). At install time, strip-python3
# removes the type annotations and downgrades the syntax. This check runs
# that transformation and verifies the result compiles with python 2.7
# and/or 3.6.

set -eu

usage() {
    echo "Usage: $0 [2.7 | 3.6 | all]" >&2
    exit 2
}

[ $# -eq 1 ] || usage
VERSION="$1"
shift

case "$VERSION" in
    2.7|3.6|all) ;;
    *)    usage ;;
esac

srcdir="SOURCES/etc/xapi.d/plugins"

tmpdirs=()
cleanup() {
    for d in "${tmpdirs[@]}"; do
        rm -rf -- "$d"
    done
}
trap cleanup EXIT

run_one() {
    local version="$1"
    local envname
    local pyname
    local python
    local tmpdir

    if [ "$version" = "2.7" ]; then
        envname=PYTHON27
        pyname=python2.7
    elif [ "$version" = "3.6" ]; then
        envname=PYTHON36
        pyname=python3.6
    fi

    if [ -n "${!envname:-}" ]; then
        python="${!envname}"
    elif command -v "$pyname" > /dev/null; then
        python="$pyname"
    else
        echo "error: no python $version interpreter found (set $envname or put $pyname on the path)" >&2
        exit 1
    fi

    tmpdir="$(mktemp -d)"
    tmpdirs+=("$tmpdir")

    mkdir -p "$tmpdir/xcpngutils"
    for f in "$srcdir"/*.py; do
        uv run strip-python3 -P $version -n -o "$tmpdir/$(basename "$f")" "$f" || return 1
    done
    for f in "$srcdir"/xcpngutils/*.py; do
        uv run strip-python3 -P $version -n -o "$tmpdir/xcpngutils/$(basename "$f")" "$f" || return 1
    done

    "$python" -m compileall -q "$tmpdir"
    echo "OK: stripped sources compile with python $version"
}

rc=0
if [ "$VERSION" = "all" ]; then
    run_one 2.7 "$@" || rc=1
    run_one 3.6 "$@" || rc=1
else
    run_one "$VERSION" "$@" || rc=1
fi
exit $rc
