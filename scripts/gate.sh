#!/usr/bin/env bash
# The Sanchaya quality gate. Same command Claude runs in /review, same command git runs before
# every commit once installed as a pre-commit hook:
#
#   ln -sf ../../scripts/gate.sh .git/hooks/pre-commit
#
# A red gate blocks the commit. There is no --no-verify culture in this repo.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

echo "== ruff =="
ruff check .
echo "== mypy =="
mypy src/
echo "== pytest =="
pytest -q
echo "== gate green =="
