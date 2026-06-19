#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Python executable not found at '$PYTHON_BIN'. Create venv first or export PYTHON_BIN."
  exit 1
fi

echo "Using interpreter: $PYTHON_BIN"
"$PYTHON_BIN" --version

echo "Upgrading pip..."
"$PYTHON_BIN" -m pip install --upgrade pip

echo "Installing project dependencies..."
"$PYTHON_BIN" -m pip install -r requirements.txt

echo "Running smoke test..."
"$PYTHON_BIN" -m pytest -q tests/test_health.py

echo "Bootstrap completed."
