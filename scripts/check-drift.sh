#!/usr/bin/env bash
# CI drift guard: re-runs codegen and fails if generated/ differs from committed.
set -euo pipefail
cd "$(dirname "$0")/.."

python codegen.py > /dev/null

# *.xlsx excluded — openpyxl writes timestamps into the zip container,
# making binary contents non-deterministic across runs. The .xlsform.json
# source IS drift-guarded; xlsx is just a rendering of it.
TARGETS=(generated types archived)
# examples/ retained only if it exists (legacy flat layout). After full
# migration to types/<slug>/examples/<variant>/, it disappears.
[ -d examples ] && TARGETS+=(examples)

if ! git diff --exit-code --ignore-matching-lines='.' \
      ':(exclude)*.xlsx' \
      "${TARGETS[@]}" ; then
  echo ""
  echo "ERROR: registry artifacts out of sync with codegen.py / survey-types.jsonld"
  echo "Run: python codegen.py && git add ${TARGETS[*]}"
  exit 1
fi

echo "OK: generated artifacts in sync."
