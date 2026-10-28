#!/usr/bin/env bash
# The one gate, run locally before committing and by CI: the same command in
# both places, so a change that passes here passes there.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== tests (includes the docs lint gate)"
bash tests/run_tests.sh
echo "== shellcheck"
shellcheck -S warning bin/dss-lab bin/lib/*.sh tests/run_tests.sh
echo "== markdownlint"
markdownlint .
echo "== all checks passed"
