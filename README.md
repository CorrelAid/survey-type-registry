# Survey Type Registry

Single source of truth for question type metadata across the CDL survey toolchain.

```
XLSForm → LimeSurvey TSV → Survey Data → DDI-Codebook XML
         ↑___________________________________________________|
```

JSON-LD registry + Python codegen producing typed mapping tables for downstream tools (TypeScript, Python, Go).

## Layout

```
survey-types.jsonld     # source of truth
codegen.py              # generator (stdlib only)
generated/              # committed artifacts — do NOT edit
  TypeMappings.ts       # xlsform2lstsv
  type_mappings.py      # survey2ddi
  type_mappings.go      # qwacback
  Appearances.ts        # xlsform2lstsv (appearance dispatch)
  conventions.json      # xlsform2lstsv (sanitization, _other pattern, column map)
  examples_index.json   # wp_eins / qwacback presentation examples
  TYPE_EQUIVALENCE.md   # human-readable matrix
examples/               # XLSForm payloads per presentation variant
scripts/check-drift.sh  # CI guard: fail if generated/ stale
.github/workflows/ci.yml
```

## Entry types in `@graph`

| `@type` | Purpose |
|---------|---------|
| `QuestionType` | XLSForm question type (e.g. `select_one`, `integer`). Carries `xlsform`, `limesurvey`, `ddi`, `concept`, `qwacback` blocks |
| `MetadataType` | Silent-skip XLSForm types (`start`, `end`, `today`, `audit`, …) |
| `StructuralType` | `begin_group`, `end_group`, `begin_repeat`, `end_repeat` |
| `PresentationVariant` | Pedagogical variant of a QuestionType (e.g. `single_choice_other`). Points at `examples/*.xlsform.json` |
| `Appearance` | XLSForm `appearance` column values (e.g. `minimal`, `multiline`, `table-list`) and their LS effect |
| `GlobalConvention` | `_other` pattern, sanitization rules |
| `XLSFormColumnMap` | XLSForm column → LS TSV column mapping |

## Workflow

```bash
# 1. Edit
$EDITOR survey-types.jsonld

# 2. Regenerate
python codegen.py

# 3. Sanity-check drift
bash scripts/check-drift.sh

# 4. Commit + tag
git add survey-types.jsonld generated/ examples/
git commit -m "..."
git tag -a v0.X.Y -m "..."
git push --tags
```

CI runs `scripts/check-drift.sh` on every PR.

## Versioning

Downstream consumers pin a git tag or commit SHA. See each consumer's `.registry-version` file.

- **Major** — renamed/removed type, changed `@type`, changed `limesurvey.supported`, intrvl/responseDomainType change
- **Minor** — additions, new entry types
- **Patch** — docs, comments

## Consumers

- **[xlsform2lstsv](https://github.com/CorrelAid/xlsform2lstsv)** — XLSForm → LimeSurvey TSV
- **[survey2ddi](https://github.com/CorrelAid/survey2ddi)** — Survey data → DDI-Codebook XML
- **[qwacback](https://github.com/CorrelAid/qwacback)** — DDI question bank
- **[wp_eins](https://github.com/CorrelAid/wp_eins)** — didactic site (uses `examples_index.json`)

## References

- JSON-LD: https://json-ld.org/
- SKOS: https://www.w3.org/2004/02/skos/
- DDI-Codebook 2.5: https://ddialliance.org/Specification/DDI-Codebook/2.5/
- XLSForm spec: https://xlsform.org/en/

## License

Same as parent CDL survey toolchain.
