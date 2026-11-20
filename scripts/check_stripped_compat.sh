#!/usr/bin/env bash
# The sources must remain installable on XCP-ng 8.3, where the plugins run
# with python 2.7 (3.6 is also available). At install time, strip-python3
# removes the type annotations and downgrades the syntax. This check runs
# that transformation and verifies the result compiles with python 3.6.

set -eu

srcdir="SOURCES/etc/xapi.d/plugins"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

mkdir -p "$tmpdir/xcpngutils"
for f in "$srcdir"/*.py; do
    uv run strip-python3 -P 2.7 -n -o "$tmpdir/$(basename "$f")" "$f"
done
for f in "$srcdir"/xcpngutils/*.py; do
    uv run strip-python3 -P 2.7 -n -o "$tmpdir/xcpngutils/$(basename "$f")" "$f"
done

# Interpreter used to check the stripped sources: the $PYTHON36
# environment variable, else python3.6 on the path.
if [ -n "${PYTHON36:-}" ]; then
    python36="$PYTHON36"
elif command -v python3.6 > /dev/null; then
    python36="python3.6"
else
    echo "error: no python 3.6 interpreter found (set PYTHON36 or put python3.6 on the path)" >&2
    exit 1
fi

"$python36" -m compileall -q "$tmpdir"
echo "OK: stripped sources compile with python 3.6"
