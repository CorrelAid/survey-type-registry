#!/usr/bin/env bash
# CI drift guard: re-runs codegen and fails if generated/ differs from committed.
set -euo pipefail
cd "$(dirname "$0")/.."

python codegen.py > /dev/null

if ! git diff --exit-code generated/ examples/ ; then
  echo ""
  echo "ERROR: generated/ or examples/ out of sync with codegen.py / survey-types.jsonld"
  echo "Run: python codegen.py && git add generated/ examples/"
  exit 1
fi

echo "OK: generated artifacts in sync."
