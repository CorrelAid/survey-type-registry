#!/usr/bin/env bash
# Regenerate snapshot fixtures (examples/<id>/ddi.xml + tsv.tsv) using
# current driver versions (survey2ddi + xlsform2lstsv). Manual gate —
# default codegen does NOT touch these files so snapshot tests stay
# non-tautological.
#
# Run after bumping a driver version pin (e.g. survey2ddi in pyproject.toml,
# or rebuilding xlsform2lstsv). Inspect git diff, commit if intentional.
set -euo pipefail
cd "$(dirname "$0")/.."

uv run python codegen.py --bless-snapshots

echo ""
echo "Snapshots regenerated. Review with:"
echo "  git diff examples/"
echo "  git add examples/ && git commit -m 'bless: regen snapshots for driver X.Y.Z'"
