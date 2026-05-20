# CDL Survey Schema Registry

Single source of truth for **how question types behave** across the CDL survey toolchain — from XLSForm authoring through LimeSurvey collection to DDI-Codebook archival.

```
XLSForm → LimeSurvey TSV → Survey Data → DDI-Codebook XML
         ↑___________________________________________________|
```

## What's in here

The repo owns three sibling responsibilities:

| Layer | Owns | Consumers |
|-------|------|-----------|
| **Type metadata** | XLSForm ↔ LS ↔ DDI ↔ qwacback mappings, sanitization rules, `_other` pattern, vocabularies, presentation variants | xlsform2lstsv, survey2ddi, qwacback, wp_eins (via `generated/`) |
| **DDI spec & validation** | DDI-Codebook 2.5 XSDs + CDL custom Schematron rules | qwacback (prod NATS service), registry tests |
| **Reference validator** | Java schematron-worker (Saxon-HE + schxslt2) | qwacback (NATS deployment), registry tests (CLI mode) |

## Layout

```
types/                                # v1-blessed QuestionTypes (self-contained)
  <slug>/
    definition.jsonld                 # the single QuestionType entry
    docs.md                           # auto-generated workflow narrative + mermaid
    examples/<variant>/               # PresentationVariants whose broader is this type
      xlsform.json                    # source
      xlsform.xlsx                    # derived
      ddi.xml                         # blessed snapshot
      tsv.tsv                         # blessed snapshot (when LS-supported)
      meta.json                       # registry-derived metadata

archived/
  survey-types.archived.jsonld        # QuestionTypes recognized in XLSForm spec
                                      #  but rejected from CDL ecosystem. Not
                                      #  loaded by codegen.

survey-types.jsonld                   # conventions, vocabs, structural,
                                      #  metadata, non-blessed QuestionTypes,
                                      #  PresentationVariants, Appearances,
                                      #  XLSFormColumnMap

schemas/
  xsd/                                # DDI-Codebook 2.5 XSDs (W3C/DDI Alliance)
  schematron/ddi_custom_rules.sch     # CDL convention rules

workers/
  schematron-worker/                  # Java validator: NATS service + CLI mode

generated/                            # codegen output — DO NOT EDIT
  TypeMappings.ts                     # xlsform2lstsv
  Appearances.ts                      # xlsform2lstsv
  conventions.json                    # xlsform2lstsv
  type_mappings.py                    # survey2ddi
  type_mappings.go                    # qwacback
  examples_index.json                 # wp_eins
  TYPE_EQUIVALENCE.md                 # human-readable cross-format matrix

codegen.py                            # generator (stdlib only)
scripts/
  check-drift.sh                      # CI guard
  bless-snapshots.sh                  # regenerate ddi.xml + tsv.tsv per example
  build-worker.sh                     # build schematron-worker shadow jar
tests/                                # transformation + snapshot + validation suite
.github/workflows/ci.yml              # drift-guard + transformations + schematron jobs
```

## Tiers

| Tier | Set | Layout | Codegen | Tests |
|------|-----|--------|---------|-------|
| **v1-blessed** | `integer`, `text`, `date`, `select_one`, `select_multiple`, `begin_group` | `types/<slug>/` self-contained | yes | per-type folder + cross-cutting |
| **v1-conditional** | `decimal`, `note`, `time`, `datetime`, `rank`, `calculate`, `select_one_from_file`, `select_multiple_from_file` | flat in `survey-types.jsonld` | yes | cross-cutting only |
| **archived** | `geopoint, geotrace, geoshape, start-geopoint, image, audio, video, file, background-audio, barcode, phonenumber, email, csv-external, range, acknowledge` | `archived/` | no | none |

## Entry types in `@graph`

| `@type` | Purpose |
|---------|---------|
| `QuestionType` | XLSForm question type. Carries `xlsform`, `limesurvey`, `ddi`, `concept`, `qwacback` blocks |
| `MetadataType` | Silent-skip XLSForm types (`start`, `end`, `today`, `audit`, …) |
| `StructuralType` | `begin_group`, `end_group`, `begin_repeat`, `end_repeat` |
| `PresentationVariant` | Pedagogical/UI variant of a QuestionType (e.g. `single_choice_other`, `grid`). References a base via `skos:broader`, points at `examples/<id>/` |
| `Appearance` | XLSForm `appearance` column values (e.g. `minimal`, `multiline`, `table-list`) and their LS effect |
| `Vocabulary` | External code list reference (e.g. `vocab:iso_3166_1`, `xlsformFilename: iso_3166_1.csv`) |
| `GlobalConvention` | `_other` pattern, sanitization rules, external code list pattern |
| `XLSFormColumnMap` | XLSForm column → LS TSV column mapping |

## Workflow

```bash
# 1. Edit
$EDITOR types/<slug>/definition.jsonld    # for v1-blessed
$EDITOR survey-types.jsonld               # for everything else

# 2. Regenerate
python codegen.py
# Optionally regenerate driver-derived snapshots:
bash scripts/bless-snapshots.sh           # requires built xlsform2lstsv + survey2ddi installed

# 3. Sanity-check
bash scripts/check-drift.sh
JAVA_HOME=$(/path/to/jdk21) uv run pytest tests/transformations/ -m "not docker"

# 4. Commit + tag
git commit -am "..."
git tag -a v0.X.Y -m "..."
git push --tags
```

CI (`.github/workflows/ci.yml`) runs three jobs:
- `drift-guard` — codegen output in sync with source (excludes `*.xlsx` due to openpyxl wall-clock timestamps)
- `transformations` — clones `xlsform2lstsv`, builds it, runs pytest
- `schematron-validation` — builds the Java schematron-worker, validates every blessed `ddi.xml` against XSD + CDL schematron rules

## Versioning

Downstream consumers pin a git tag or commit SHA. Each consumer has a `.registry-version` file recording the pin.

- **Major** — renamed/removed type, changed `@type`, changed `limesurvey.supported`, intrvl/responseDomainType change, changed export name in `generated/`
- **Minor** — additions, new entry types, new conventions
- **Patch** — docs, comments

## Consumers

- **[xlsform2lstsv](https://github.com/CorrelAid/xlsform2lstsv)** — XLSForm → LimeSurvey TSV. Imports `generated/{TypeMappings,Appearances}.ts` + `generated/conventions.json`.
- **[survey2ddi](https://github.com/CorrelAid/survey2ddi)** — Survey data + XLSForm → DDI-Codebook XML. Imports `generated/type_mappings.py`. Should also sync `schemas/xsd/` (currently vendors locally).
- **[qwacback](https://github.com/CorrelAid/qwacback)** — DDI question bank. Imports `generated/type_mappings.go`. Should sync `schemas/`, `workers/schematron-worker/` (currently vendors locally).
- **[wp_eins](https://github.com/CorrelAid/wp_eins)** — didactic site. Imports `generated/examples_index.json` + `types/<slug>/examples/<variant>/`.

## References

- JSON-LD: https://json-ld.org/
- SKOS: https://www.w3.org/2004/02/skos/
- DDI-Codebook 2.5: https://ddialliance.org/Specification/DDI-Codebook/2.5/
- XLSForm spec: https://xlsform.org/en/
- ISO Schematron: https://schematron.com/

## License

Same as parent CDL survey toolchain.
