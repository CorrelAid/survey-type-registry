#!/usr/bin/env bash
# CI drift guard: re-runs codegen and fails if generated/ differs from committed.
set -euo pipefail
cd "$(dirname "$0")/.."

python codegen.py > /dev/null

# *.xlsx excluded — openpyxl writes timestamps into the zip container,
# making binary contents non-deterministic across runs. The .xlsform.json
# source IS drift-guarded; xlsx is just a rendering of it.
if ! git diff --exit-code --ignore-matching-lines='.' \
      ':(exclude)*.xlsx' \
      generated/ examples/ types/ archived/ ; then
  echo ""
  echo "ERROR: generated/, examples/, types/, or archived/ out of sync with codegen.py / survey-types.jsonld"
  echo "Run: python codegen.py && git add generated/ examples/ types/ archived/"
  exit 1
fi

echo "OK: generated artifacts in sync."
