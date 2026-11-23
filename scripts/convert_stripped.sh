#!/usr/bin/env bash
# Produce the python 2.7 / 3.6 compatible sources (stripped type
# annotations, downgraded syntax) that get installed on XCP-ng 8.3.
#
# The conversion runs strip-python3 (from the "build" uv group, which
# needs python 3.9+; uv selects 3.12 itself) and lays the result out
# as a source tree ready for the RPM:
#
#   <outdir>/<target>/xcp-ng-xapi-plugins-<version>/
#       LICENSE
#       README.md
#       SOURCES/etc/xapi.d/plugins/*.py
#       SOURCES/etc/xapi.d/plugins/xcpngutils/*.py
#
# With --tar a .tar.gz + .sha256 are produced on top, named
# xcp-ng-xapi-plugins-<version>-stripped-<target>.tar.gz, so the
# tarball can be uploaded as a GitHub release asset and consumed by
# the xcp-ng-xapi-plugins RPM (its Source0).
#
# Usage: scripts/convert_stripped.sh 2.7 | 3.6 | all --version VER [--outdir DIR] [--tar]
#
# This is also the single code path used by check_stripped_compat.sh,
# so the CI compatibility check exercises the very same conversion.

set -eu

usage() {
    echo "Usage: $0 2.7 | 3.6 | all --version VER [--outdir DIR] [--tar]" >&2
    exit 2
}

TAR=0
VERSION=""
OUTDIR=""
POSITIONAL=()

while [ $# -gt 0 ]; do
    case "$1" in
        --version)  [ $# -ge 2 ] || usage; VERSION="$2"; shift 2 ;;
        --outdir)   [ $# -ge 2 ] || usage; OUTDIR="$2"; shift 2 ;;
        --tar)      TAR=1; shift ;;
        -h|--help)  usage ;;
        -*)         usage ;;
        *)          POSITIONAL+=("$1"); shift ;;
    esac
done

[ ${#POSITIONAL[@]} -eq 1 ] || usage
TARGETS="${POSITIONAL[0]}"

case "$TARGETS" in
    2.7|3.6|all) ;;
    *)    usage ;;
esac
[ -n "$VERSION" ] || { echo "error: --version is required" >&2; usage; }
[ -n "$OUTDIR" ] || OUTDIR="build/stripped"

cd "$(dirname "$0")/.."
topdir="xcp-ng-xapi-plugins-${VERSION}"
srcdir="SOURCES/etc/xapi.d/plugins"
relsrc="SOURCES/etc/xapi.d/plugins"

# Resolve the repository root; refuse to run from a checkout that does
# not have the sources, so a wrong --outdir never hides a wrong CWD.
[ -d "$srcdir" ] || { echo "error: $srcdir not found; run from the repository root" >&2; exit 1; }

convert_one() {
    local target="$1"
    local outroot="$OUTDIR/$target"
    local outsrc="$outroot/$topdir/$relsrc"

    echo ">>> Converting for python $target into $outroot"
    rm -rf -- "$outroot"
    mkdir -p "$outsrc/xcpngutils"

    # The RPM carries them as %doc; the stripped tarball must contain
    # them or the package cannot be built from it.
    cp -- "LICENSE" "README.md" "$outroot/$topdir/"

    for f in "$srcdir"/*.py "$srcdir"/xcpngutils/*.py; do
        local rel="${f#$srcdir/}"
        uv run --python 3.12 --group build strip-python3 -P "$target" -n -o "$outsrc/$rel" "$f"
    done

    if [ "$TAR" = 1 ]; then
        local tarball="xcp-ng-xapi-plugins-${VERSION}-stripped-${target}.tar.gz"
        tar -czf "$OUTDIR/$tarball" -C "$outroot" "$topdir"
        (cd "$OUTDIR" && sha256sum "$tarball" > "$tarball.sha256")
        echo "    $OUTDIR/$tarball"
    fi
}

if [ "$TARGETS" = "all" ]; then
    convert_one 2.7
    convert_one 3.6
else
    convert_one "$TARGETS"
fi
