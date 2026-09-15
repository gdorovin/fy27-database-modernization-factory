#!/usr/bin/env bash
# Development environment bootstrap. Idempotent; safe to re-run.
set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> Python"
python --version

echo "==> Installing the package with development tooling"
python -m pip install --upgrade pip >/dev/null
python -m pip install -e ".[dev]"

if command -v pre-commit >/dev/null 2>&1; then
  echo "==> Installing pre-commit hooks"
  pre-commit install --install-hooks
fi

echo "==> Verifying the offline core"
dbmodernize version
dbmodernize validate-repo || true   # first run may report gaps; the gate below is definitive

cat <<'MESSAGE'

Ready.

  make gate        everything CI enforces
  make validate    repository, playbook, skills, agents, scenarios
  make test        test suite

Run one scenario end to end, offline:

  dbmodernize validate-scenario scenarios/01-sql2016-to-managed-instance

This toolkit produces plans and evidence. It does not migrate, deploy, or cut over
anything, and it has no cloud credentials.
MESSAGE
