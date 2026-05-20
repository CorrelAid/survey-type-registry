# qwacback ← survey-type-registry sync brief

**Goal**: qwacback consumes registry as the single source of truth for type mappings, DDI XSDs, CDL schematron rules, and the Java validator worker. Delete local duplicates.

## Self-contained brief for the agent

You're working in `/home/jstet/Code/CorrelAid/CDL/qwacback/`. This repo currently vendors several things that have moved upstream into `survey-type-registry` (sibling clone at `../survey-type-registry/`, published at `git@github.com:CorrelAid/survey-type-registry.git` tag `v1.0.0+`).

### Pre-flight reads

1. `qwacback/internal/converter/type_mappings.go` — generated from registry; should match registry's `generated/type_mappings.go`
2. `qwacback/xml/` — DDI 2.5 XSDs (duplicated upstream at `registry/schemas/xsd/`)
3. `qwacback/schematron/ddi_custom_rules.sch` — CDL custom rules (duplicated upstream at `registry/schemas/schematron/`)
4. `qwacback/schematron-worker/` — Java NATS service (duplicated upstream at `registry/workers/schematron-worker/`)
5. `qwacback/internal/examples/examples.go` — XLSForm example payloads (duplicated upstream at `registry/types/<slug>/examples/<variant>/xlsform.json`)
6. `qwacback/Dockerfile` + `docker-compose.yml` — paths into `xml/` and `schematron/`
7. `qwacback/.registry-version` — create if missing

### Phase 1 — pin

Create `qwacback/.registry-version` containing exactly one tag:
```
v1.0.0
```

### Phase 2 — sync script

`qwacback/scripts/sync-registry.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

VERSION=$(cat .registry-version)
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

git clone --depth 1 --branch "$VERSION" \
  https://github.com/CorrelAid/survey-type-registry.git \
  "$TMPDIR/registry" >/dev/null

# Generated code (Go)
mkdir -p internal/converter/_generated
cp "$TMPDIR/registry/generated/type_mappings.go" internal/converter/_generated/

# DDI schemas
rm -rf xml schematron
mkdir -p xml schematron
cp -r "$TMPDIR/registry/schemas/xsd/." xml/
cp "$TMPDIR/registry/schemas/schematron/ddi_custom_rules.sch" schematron/

# Schematron worker source (replace local vendored copy)
rm -rf schematron-worker
cp -r "$TMPDIR/registry/workers/schematron-worker" .

# Example fixtures (replace examples.go later)
mkdir -p internal/examples/_synced
cp "$TMPDIR/registry/generated/examples_index.json" internal/examples/_synced/

echo "Synced registry $VERSION → qwacback"
```

`chmod +x`. Run it once.

### Phase 3 — refactor Go code

1. `internal/converter/type_mappings.go` becomes a re-export shim:
   ```go
   package converter

   import _generated "qwacback/internal/converter/_generated"

   var TypeRegistry = _generated.TypeRegistry  // re-export
   ```
   Or delete `type_mappings.go` and update imports.

2. `internal/examples/examples.go` reads from `_synced/examples_index.json` at startup instead of hardcoding `defs` array. Parse JSON, run `converter.XLSFormToDDI` per entry to produce DDI XML (existing behavior preserved). Delete the inline `defs` block.

3. Dockerfile + docker-compose:
   - `XSD_PATH` env defaults to `/app/xml/codebook.xsd` — keep
   - `SCHEMATRON_PATH` env defaults to `/app/schematron/ddi_custom_rules.sch` — keep
   - Build sequence: copy synced `xml/` + `schematron/` + `schematron-worker/` into image
   - Schematron-worker Dockerfile builds the jar — unchanged shape, source now lives in this repo via sync

### Phase 4 — CI drift guard

`qwacback/scripts/check-registry-drift.sh`:
```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

VERSION=$(cat .registry-version)
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

git clone --depth 1 --branch "$VERSION" \
  https://github.com/CorrelAid/survey-type-registry.git \
  "$TMPDIR/registry" >/dev/null

diff -q "$TMPDIR/registry/generated/type_mappings.go" internal/converter/_generated/type_mappings.go
diff -rq "$TMPDIR/registry/schemas/xsd/" xml/
diff -q "$TMPDIR/registry/schemas/schematron/ddi_custom_rules.sch" schematron/ddi_custom_rules.sch
diff -rq "$TMPDIR/registry/workers/schematron-worker/" schematron-worker/

echo "OK: synced from registry $VERSION"
```

Wire into existing CI as a separate job.

### Phase 5 — verify

- `go test ./...` — all unit + integration tests pass
- `docker-compose up --build` — schematron-worker boots, validation requests succeed
- `gh pr create` — review the deletions of duplicated files

### Hard rules

- DO NOT modify `../survey-type-registry`. If a registry change is needed, file an issue there or open a PR upstream.
- DO NOT keep dual copies of XSD / schematron / worker after sync lands.
- DO NOT skip the drift guard in CI.
- DO NOT bump `.registry-version` without testing locally first.

### Report back

- Files deleted (paths)
- Files added (sync scripts, `_generated/`, `_synced/`)
- Test results
- Docker-compose smoke test result
- Any registry gap encountered (file upstream issue)
