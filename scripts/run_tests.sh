#!/usr/bin/env bash
# Run the test suite with the python versions used by XCP-ng hosts:
#   3.6  (XCP-ng 8.3)
#   3.12 (XCP-ng 9.0)
#
# Usage: scripts/run_tests.sh [3.6 | 3.12 | all] [pytest args...]
#
# uv manages the virtual environment and the dependencies (single
# uv.lock); the interpreter itself must be available on the system,
# since uv cannot install CPython 3.6. A missing interpreter makes
# the test to fail.

set -u

usage() {
    echo "Usage: $0 [3.6 | 3.12 | all] [pytest args...]" >&2
    exit 2
}

[ $# -ge 1 ] || usage
VERSION="$1"
shift

case "$VERSION" in
    3.6|3.12|all) ;;
    *)    usage ;;
esac

run_one() {
    local version="$1"
    local env_dir
    shift
    env_dir=".venv-${version}"

    if ! command -v "python$version" >/dev/null 2>&1; then
        echo "error: no python$version interpreter found, skipping it" >&2
        return 1
    fi

    echo ">>> Running tests with python $version"
    UV_PROJECT_ENVIRONMENT="$env_dir" uv sync --python "python$version" --group test \
        || return 1
    "$env_dir/bin/pytest" "$@"
}

rc=0
if [ "$VERSION" = "all" ]; then
    run_one 3.6 "$@" || rc=1
    run_one 3.12 "$@" || rc=1
else
    run_one "$VERSION" "$@" || rc=1
fi
exit $rc
