#!/usr/bin/env bash
# The sources must remain installable on XCP-ng 8.3, where the plugins run
# with python 2.7 (3.6 is also available). This check runs the same
# conversion the release process uses (scripts/convert_stripped.sh, i.e.
# strip-python3 removing the type annotations and downgrading the syntax)
# and verifies the result compiles with python 2.7 and/or 3.6.

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

    # Same conversion as the release artefacts (see
    # scripts/convert_stripped.sh); the version is irrelevant here, it
    # only names the top directory of the tree.
    "$(dirname "$0")/convert_stripped.sh" "$version" --version check --outdir "$tmpdir" || return 1

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
