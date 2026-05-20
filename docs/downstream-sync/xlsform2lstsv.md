# xlsform2lstsv ← survey-type-registry sync brief

**Goal**: xlsform2lstsv consumes registry as the single source of truth for type mappings, appearances, sanitization rules, the `_other` pattern, the XLSForm→LS TSV column mapping, and presentation-variant examples. Drop all hardcoded equivalents.

## Self-contained brief for the agent

You're working in `/home/jstet/Code/CorrelAid/CDL/xlsform2lstsv/` (independent repo, own remote). Registry is the sibling clone at `../survey-type-registry/`, published at `git@github.com:CorrelAid/survey-type-registry.git` tag `v1.2.0+`.

### Pre-flight reads

1. `xlsform2lstsv/src/processors/TypeMapper.ts` — current inline `TYPE_MAPPINGS` table
2. `xlsform2lstsv/src/xlsformConverter.ts:1-36` — `SKIP_TYPES`, `UNIMPLEMENTED_TYPES`, `UNSUPPORTED_APPEARANCES`
3. `xlsform2lstsv/src/processors/FieldSanitizer.ts` — name/code length constants + strip rules
4. `xlsform2lstsv/src/xlsformConverter.ts:820-957` — appearance dispatch, matrix detection
5. `xlsform2lstsv/src/xlsformConverter.ts:257-304` — `_other` pattern detection
6. Registry generated artifacts to consume: `generated/{TypeMappings.ts, Appearances.ts, conventions.json}`
7. `xlsform2lstsv/.registry-version` (create if missing)

### Phase 1 — pin

```
v1.2.0
```
in `xlsform2lstsv/.registry-version`.

### Phase 2 — sync script

`xlsform2lstsv/scripts/sync-registry.sh`:

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

mkdir -p src/generated
cp "$TMPDIR/registry/generated/TypeMappings.ts" src/generated/
cp "$TMPDIR/registry/generated/Appearances.ts" src/generated/
cp "$TMPDIR/registry/generated/conventions.json" src/generated/

echo "Synced registry $VERSION → xlsform2lstsv/src/generated/"
```

`chmod +x`. Run once.

### Phase 3 — refactor `src/processors/TypeMapper.ts`

- Delete inline `TYPE_MAPPINGS` (lines 8-37).
- Add `import { TYPE_MAPPINGS, type TypeMapping } from '../generated/TypeMappings.js';` (note `.js` for ESM).
- Update `mapType()`:
  - If `mapping.kind === 'metadata'` → return sentinel (consumer drops row).
  - If `mapping.supported === false` → throw `new Error(\`Unimplemented XLSForm type: '${typeInfo.base}'. This type is not currently supported.\`)`.
  - Else use `mapping.limeSurveyType`.
- `parseType()` logic for `select_one|select_multiple|rank` → generalize to check `mapping.requiresListName === true`.

### Phase 4 — refactor `src/xlsformConverter.ts`

Replace constants:

```typescript
import { TYPE_MAPPINGS } from './generated/TypeMappings.js';
import { APPEARANCES } from './generated/Appearances.js';

const SKIP_TYPES: ReadonlySet<string> = new Set(
  Object.entries(TYPE_MAPPINGS)
    .filter(([, v]) => v.kind === 'metadata')
    .map(([k]) => k)
);
const UNIMPLEMENTED_TYPES: ReadonlySet<string> = new Set(
  Object.entries(TYPE_MAPPINGS)
    .filter(([, v]) => v.kind === 'question' && !v.supported)
    .map(([k]) => k)
);
const UNSUPPORTED_APPEARANCES: ReadonlySet<string> = new Set(
  Object.entries(APPEARANCES)
    .filter(([, v]) => v.behavior === 'warn')
    .map(([k]) => k)
);
```

Appearance dispatch (~lines 820-857, 839-846): use `APPEARANCES[name]` to read `lsTypeOverride` (e.g. `minimal` → `!`, `multiline` → `T`). Use `validForTypes` for the "appearance not valid for this question type" warning. Keep the matrix detection state machine (it's stateful, not data-driven).

### Phase 5 — refactor `src/processors/FieldSanitizer.ts`

Read sanitization rules from `conventions.json` (`conventions.sanitization.name` + `conventions.sanitization.choiceCode`). Replace inline `MAX_FIELD_LENGTH = 20`, `maxLength = 5`, regex literals.

ESM JSON import:
```typescript
import conventions from '../generated/conventions.json' with { type: 'json' };
const NAME_RULES = conventions.conventions.sanitization.name;
const CHOICE_RULES = conventions.conventions.sanitization.choiceCode;
```

### Phase 6 — _other pattern

Read `conventions.conventions.other` from `conventions.json`. The companion-suffix, relevance template, choice code, and applicable types all live there now. Replace any hardcoded `"_other"` / `'other'` literals in `xlsformConverter.ts:257-304` with refs to the convention.

### Phase 7 — drop `rank` support

Registry v1.2.0+ archives `type:rank` (documented in wp_eins narrative only,
not operationalized cross-tool). After sync, `rank` no longer appears in
`TYPE_MAPPINGS` (it's in the archived set).

Action:
1. Search `src/` for any literal `'rank'` reference. Remove from any special-case
   branch.
2. The auto-derived `UNIMPLEMENTED_TYPES` set will NOT include `rank` (it's
   absent from `TYPE_MAPPINGS` entirely, neither metadata nor question). Decide:
   - Treat absence-from-TYPE_MAPPINGS as "unimplemented" → throw at conversion
     time (recommended; matches current behavior for unknown types).
   - Or: add `rank` to an `EXPLICITLY_REJECTED` set in code with a clear
     error message pointing at `archived/survey-types.archived.jsonld`.
3. Drop or skip rank-typed test fixtures. Add regression: feeding
   `type=rank …` produces an error citing the registry archival.

### Phase 8 — drift guard

`xlsform2lstsv/scripts/check-registry-drift.sh`:

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

diff -q "$TMPDIR/registry/generated/TypeMappings.ts"  src/generated/TypeMappings.ts
diff -q "$TMPDIR/registry/generated/Appearances.ts"   src/generated/Appearances.ts
diff -q "$TMPDIR/registry/generated/conventions.json" src/generated/conventions.json

echo "OK: synced from registry $VERSION"
```

Wire into existing GitHub Actions workflow as a separate job.

### Phase 9 — verify

- `npm run build` — no type errors
- `npm test` — all vitest pass. Tests in `src/test/unimplementedTypes.test.ts` still pass (same types are now `supported: false` in registry).
- Snapshot tests in `docker_tests/` should not regress.

### Hard rules

- DO NOT modify `../survey-type-registry`. If a registry gap blocks migration, file an issue upstream.
- DO NOT keep inline `TYPE_MAPPINGS` / `UNSUPPORTED_APPEARANCES` after sync lands.
- DO NOT skip the drift guard in CI.
- ESM-only: use `.js` extensions in TS imports (repo is ESM).
- Don't add backwards-compat shims; the old `TYPE_MAPPINGS` export can be deleted outright since consumers are within the package.

### Report back

- Files changed (paths)
- Files added (sync script, drift script, `src/generated/`)
- Test results
- Any registry gap encountered
