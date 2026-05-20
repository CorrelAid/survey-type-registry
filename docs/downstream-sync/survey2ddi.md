# survey2ddi ← survey-type-registry sync brief

**Goal**: survey2ddi v0.5 consumes registry as single source of truth for type mappings and DDI XSDs. Fixes the over-skip bug introduced in v0.4 by using `NON_DDI_EMITTABLE_TYPES` instead of `UNSUPPORTED_TYPES`.

## Self-contained brief for the agent

You're working in `/home/jstet/Code/CorrelAid/CDL/survey2ddi/` (independent repo, has its own remote). Registry is the sibling clone at `../survey-type-registry/`, published at `git@github.com:CorrelAid/survey-type-registry.git` tag `v1.0.0+`.

### Pre-flight reads

1. `survey2ddi/survey2ddi_core/xlsform.py` — current SKIP_TYPES, TYPE_MAP, MEASURE_MAP (probably already imports from a `_generated/` dir if v0.4 migration landed)
2. `survey2ddi/survey2ddi_core/ddi_xml.py` — current DDI_TYPE_MAP, RESPONSE_DOMAIN_MAP
3. `survey2ddi/survey2ddi_core/_generated/type_mappings.py` (if present) — synced from registry
4. `survey2ddi/.registry-version` (create if missing)
5. `survey2ddi/tests/schemas/` — DDI XSDs (duplicated upstream at `registry/schemas/xsd/`)
6. `survey2ddi/tests/test_ddi_xml.py` — XSD validation tests
7. Open issue: https://github.com/CorrelAid/survey2ddi/issues/2 (UNSUPPORTED_TYPES over-skip)

### Phase 1 — bump pin

```
v1.0.0
```
in `survey2ddi/.registry-version`. Run `bash scripts/sync-registry.sh` to pull fresh `type_mappings.py`.

### Phase 2 — fix the over-skip bug (issue #2)

In `survey2ddi/survey2ddi_core/xlsform.py`, replace:

```python
from survey2ddi_core._generated.type_mappings import (
    TYPE_MAP, MEASURE_MAP, METADATA_TYPES, UNSUPPORTED_TYPES, STRUCTURAL_TYPES,
)
SKIP_TYPES = METADATA_TYPES | UNSUPPORTED_TYPES | STRUCTURAL_TYPES   # OLD
```

with:

```python
from survey2ddi_core._generated.type_mappings import (
    TYPE_MAP, MEASURE_MAP, METADATA_TYPES, STRUCTURAL_TYPES, NON_DDI_EMITTABLE_TYPES,
)
# DDI-side skip set: only types that aren't DDI-emittable (no ddi.intrvl declared
# in registry). LS-unsupported types like `range`, `acknowledge`, and
# `select_*_from_file` are still DDI-emittable and must NOT be skipped here.
SKIP_TYPES = METADATA_TYPES | STRUCTURAL_TYPES | NON_DDI_EMITTABLE_TYPES
```

Registry v1.0.0 emits `NON_DDI_EMITTABLE_TYPES` (entries that lack `ddi.intrvl`). Renames `UNSUPPORTED_TYPES` → `LS_UNSUPPORTED_TYPES` (LS perspective only; do not union into a DDI-side SKIP set).

### Phase 3 — sync DDI XSDs from registry

1. Delete `survey2ddi/tests/schemas/` (DDI XSDs duplicated upstream).
2. Update `survey2ddi/scripts/sync-registry.sh` to also copy XSDs:
   ```bash
   mkdir -p tests/_synced/schemas
   cp -r "$TMPDIR/registry/schemas/xsd/." tests/_synced/schemas/
   ```
3. In `survey2ddi/tests/test_ddi_xml.py`, change XSD load path from `tests/schemas/codebook.xsd` → `tests/_synced/schemas/codebook.xsd`.
4. Update drift script to include the schemas dir in its diff.

### Phase 4 — verify

- `uv run pytest` — all existing tests pass
- DDI XML output for `range`, `acknowledge`, `select_one_from_file`, `select_multiple_from_file` should now contain `<var>` elements again (instead of empty `<dataDscr/>` like v0.4)
- Registry's `tests/transformations/test_xlsform_to_ddi.py` xfails on survey2ddi for these types should *turn green* — verify by running the registry test suite with the new survey2ddi version pinned:
  ```bash
  cd ../survey-type-registry
  uv lock --upgrade-package survey2ddi
  JAVA_HOME=… uv run pytest tests/transformations/ -m "not docker"
  ```

### Phase 5 — handle the canonical naming clean-up (defer if v0.4 already landed)

If v0.4 still has any `"string"` literal as canonical type in `ddi_xml.py`:
- Search: `grep -rn '"string"' survey2ddi_core/`
- Replace with `"text"` (registry's canonical slug; `string` is only an XLSForm-side alias).

### Phase 6 — bump survey2ddi version + tag

```
v0.5.0
```
with release notes citing registry v1.0.0 and resolution of registry issue #2.

### Hard rules

- DO NOT modify `../survey-type-registry`. Open issues / PRs upstream if changes needed.
- DO NOT add `"string"` as a compat alias post-rename. Clean break.
- DO NOT pin `survey2ddi` to a branch in registry's pyproject.toml — use the new tag once published.
- DO NOT touch the qwacback schematron rule logic; registry owns it.

### Report back

- Files changed (xlsform.py, ddi_xml.py, test_ddi_xml.py)
- Files deleted (tests/schemas/)
- pytest results
- Output of registry's transformations suite against the new pin
- Tagged version
