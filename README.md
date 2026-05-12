# Survey Type Registry

A semantic registry for question types across the CDL survey ecosystem, using JSON-LD for interoperability.

## What is This?

The CDL survey toolchain involves multiple transformations between formats:

```
XLSForm → LimeSurvey TSV → Survey Data → DDI-Codebook XML
         ↑___________________________________________________|
```

Each format has its own type system, constraints, and conventions. This registry provides:

1. **A single source of truth** for how types map across formats
2. **Machine-readable metadata** about constraints, transformations, and data loss
3. **Code generation** to keep type mappings consistent across TypeScript, Python, and Go

## Why Semantic Technologies?

We use **JSON-LD** (Linked Data) for the registry because:

- ✅ **Human-readable** JSON that tooling can parse
- ✅ **Machine-readable** semantics (can be queried with SPARQL)
- ✅ **Extensible** (add new properties without breaking existing tools)
- ✅ **Interoperable** (can link to external vocabularies like SKOS, DDI-RDF)

## Repository Structure

```
survey-type-registry/
├── survey-types.jsonld          # The registry (JSON-LD)
├── codegen.py                   # Code generator
├── generated/                   # Auto-generated code (don't edit!)
│   ├── TypeMappings.ts          # For xlsform2lstsv
│   ├── type_mappings.py         # For survey2ddi
│   ├── type_mappings.go         # For qwacback
│   └── TYPE_EQUIVALENCE.md      # Human-readable docs
└── README.md                    # This file
```

## The Registry Format

`survey-types.jsonld` is a JSON-LD file containing metadata for each question type. Example:

```json
{
  "@id": "type:select_multiple",
  "@type": "QuestionType",
  "skos:prefLabel": "Multiple Choice (Checkboxes)",
  "xlsform": {
    "typeString": "select_multiple",
    "requiresListName": true
  },
  "limesurvey": {
    "typeCode": "M",
    "supportsOther": true,
    "answerClass": "SQ"
  },
  "ddi": {
    "intrvl": "discrete",
    "formatType": "numeric",
    "responseDomainType": "multiple",
    "structure": {
      "element": "varGrp",
      "type": "multipleResp",
      "memberVars": "binary-per-choice"
    }
  },
  "constraints": {
    "maxNameLength": 20,
    "maxChoiceCodeLength": 5,
    "warnings": ["Choice codes > 5 chars will be truncated in LimeSurvey"]
  },
  "transformation": {
    "roundTripSafe": false,
    "lossless": false,
    "dataColumns": "n-choices",
    "dataStructure": "multiple-binary-columns",
    "structureChanges": [
      {
        "from": "XLSForm",
        "to": "DDI",
        "change": "Single question → varGrp with binary child variables"
      }
    ]
  }
}
```

### Key Properties

- **`xlsform`**: How the type appears in XLSForm spreadsheets
- **`limesurvey`**: LimeSurvey type code and metadata
- **`ddi`**: DDI-Codebook XML attributes (`intrvl`, `formatType`, structure)
- **`kobo`**: KoboToolbox-specific notes
- **`constraints`**: Validation rules (name length, patterns, warnings)
- **`transformation`**: What happens during format conversions
  - `roundTripSafe`: Can you go XLS → DDI → XLS without loss?
  - `lossless`: Any information lost in any direction?
  - `dataStructure`: How data is stored (single column, binary columns, etc.)
  - `structureChanges`: Detailed transformations

## Usage

### 1. Add or Update Types

Edit `survey-types.jsonld` to add new types or update metadata. Follow the existing structure and use the `@context` for standard prefixes.

### 2. Generate Code

Run the code generator:

```bash
python codegen.py
```

This creates:
- `generated/TypeMappings.ts` → Copy to `xlsform2lstsv/src/processors/TypeMappings.ts`
- `generated/type_mappings.py` → Copy to `survey2ddi/survey2ddi_core/type_mappings.py`
- `generated/type_mappings.go` → Copy to `qwacback/internal/converter/type_mappings.go`
- `generated/TYPE_EQUIVALENCE.md` → Documentation for users

### 3. Update Dependent Projects

After generating code, update the imports in each project:

**xlsform2lstsv** (`src/processors/TypeMapper.ts`):
```typescript
// Replace TYPE_MAPPINGS with:
import { TYPE_MAPPINGS } from './TypeMappings';
```

**survey2ddi** (`survey2ddi_core/xlsform.py`):
```python
# Replace TYPE_MAP, DDI_TYPE_MAP with:
from survey2ddi_core.type_mappings import TYPE_MAP, DDI_TYPE_MAP, MEASURE_MAP
```

**qwacback** (`internal/converter/ddi_to_xlsform.go`):
```go
// Replace hardcoded mappings with:
import "github.com/correlaid/qwacback/internal/converter"

mapping := converter.TypeRegistry[xlsformType]
```

## Benefits

### Before (Scattered Type Logic)

- xlsform2lstsv has its own `TYPE_MAPPINGS` (TypeScript)
- survey2ddi has its own `TYPE_MAP`, `DDI_TYPE_MAP` (Python)
- qwacback has its own converter logic (Go)
- Documentation is out of sync
- **Problem**: Update one, forget the others → bugs

### After (Centralized Registry)

- ✅ One source of truth in `survey-types.jsonld`
- ✅ Code generation ensures consistency
- ✅ Documentation auto-generated from registry
- ✅ Semantic queries possible (e.g., "Which types lose data in round trips?")

## Example Semantic Queries

With the registry as RDF, you can query it:

```sparql
PREFIX survey: <https://civic-data.de/survey/>

# Find all types that aren't round-trip safe
SELECT ?type ?label ?warning
WHERE {
  ?typeId a survey:QuestionType ;
          survey:xlsform/survey:typeString ?type ;
          skos:prefLabel ?label ;
          survey:transformation/survey:roundTripSafe false ;
          survey:transformation/survey:warnings ?warning .
}
```

Results:
- `select_multiple` - "Data structure fundamentally changes during transformation"
- `begin_group` - "Plain groups lost in XLSForm → DDI → XLSForm round trip"

```sparql
# Find types that need choice lists
SELECT ?type
WHERE {
  ?typeId a survey:QuestionType ;
          survey:xlsform/survey:requiresListName true ;
          survey:xlsform/survey:typeString ?type .
}
```

Results: `select_one`, `select_multiple`, `rank`

## Future Extensions

The semantic approach allows future enhancements:

1. **Link to DDI-RDF vocabulary**: Map our types to official DDI ontology
2. **Platform-specific extensions**: Add `survey123`, `commcare` properties
3. **Versioning**: Track when type behavior changes (e.g., `limesurvey@6.x` vs `@7.x`)
4. **Machine learning**: Train models to suggest types based on question text
5. **Interactive tools**: Build web UIs that query the registry via SPARQL

## Related Tools

- **[xlsform2lstsv](../xlsform2lstsv/)**: XLSForm → LimeSurvey TSV converter
- **[survey2ddi](../survey2ddi/)**: Survey data → DDI-Codebook XML
- **[qwacback](../qwacback/)**: DDI question bank (import/export/convert)
- **[FormulAid](https://github.com/CorrelAid/formulaid)**: AI-assisted XLSForm generator

## References

- **JSON-LD**: https://json-ld.org/
- **SKOS**: https://www.w3.org/2004/02/skos/ (vocabulary standard)
- **DDI-Codebook 2.5**: https://ddialliance.org/Specification/DDI-Codebook/2.5/
- **XLSForm Spec**: https://xlsform.org/en/

## Contributing

To add a new type or update metadata:

1. Edit `survey-types.jsonld` (add entry to `@graph`)
2. Run `python codegen.py`
3. Commit both the registry and generated files
4. Update dependent projects to use new generated code

## License

Same as parent project (CDL survey toolchain).
