# Tests

Conformance tests that drive the actual downstream tools and assert their output matches the registry's contract.

## Layout

```
tests/
  transformations/
    fixtures.py                    # input builders (minimal forms + curated examples)
    drivers.py                     # one driver per (input → output) edge
    _xlsform2lstsv_driver.mjs      # node bridge: stdin JSON → stdout TSV
    test_xlsform_to_ddi.py         # XLSForm → DDI (drivers: survey2ddi, qwacback)
    test_xlsform_to_lstsv.py       # XLSForm → LS TSV (driver: xlsform2lstsv)
```

## Philosophy

Tests are organized by **pipeline edge** (transformation), not by tool. A single test file may run against multiple drivers and parametrize on input fixture. The assertion always references the registry's contract for the *input* type — the driver is the subject under test.

## Inputs

Two fixture sources (`tests/transformations/fixtures.py`):

| Source | Coverage | Purpose |
|--------|----------|---------|
| `minimal_form(qt)` | one auto-generated 1-question XLSForm per `QuestionType` | exhaustive per-type assertions |
| `load_example(variant)` + `to_survey_rows(...)` | curated `examples/*.xlsform.json` per `PresentationVariant` | structural assertions (e.g. `withOther`, grid) |

Both produce the same dict shape: `(survey_rows: list[dict], choices_by_list: dict[str, list[dict]])`. This shape is consumed directly by survey2ddi's `build_ddi_xml`, posted as JSON to qwacback, or piped to xlsform2lstsv via the node bridge.

## Drivers

Each driver in `tests/transformations/drivers.py` is a callable taking `(survey_rows, choices_by_list, settings)` and returning canonical output (parsed `xml.etree.ElementTree.Element` for DDI, `list[dict]` for TSV). Drivers raise `DriverUnavailable` when their environment is missing — tests skip cleanly via the `_safe()` wrapper.

| Driver | Edge | Mechanism | Availability |
|--------|------|-----------|--------------|
| `survey2ddi_xlsform_to_ddi` | XLSForm → DDI XML | direct Python import of `survey2ddi_core.ddi_xml.build_ddi_xml` | dev dep `survey2ddi @ git+...@main` |
| `qwacback_xlsform_to_ddi` | XLSForm → DDI XML | HTTP POST `${QWACBACK_URL}/api/convert/xlsform2ddi` | env var `QWACBACK_URL` (e.g. via `docker-compose up`) |
| `xlsform2lstsv_to_tsv` | XLSForm → LS TSV | `node tests/transformations/_xlsform2lstsv_driver.mjs` subprocess | env var `XLSFORM2LSTSV_PATH` (default: sibling `../xlsform2lstsv`), `dist/index.js` must exist (`npm run build`) |

The node bridge (`_xlsform2lstsv_driver.mjs`) imports the package's compiled ESM entry, monkey-patches `console.warn/log` to stderr so only TSV reaches stdout, and runs `XLSFormToTSVConverter.convert()`.

## What gets asserted

### XLSForm → DDI (`test_xlsform_to_ddi.py`)

Parametrized over each DDI-emittable QuestionType (= has `ddi.intrvl` block) **and** each available DDI driver:

| Test | Asserts |
|------|---------|
| `test_minimal_form_intrvl` | emitted `<var intrvl="…">` matches `registry["ddi"]["intrvl"]` |
| `test_minimal_form_response_domain` | emitted `<qstn responseDomainType="…">` matches registry (or `<varGrp type="multipleResp">` for select_multiple) |
| `test_minimal_form_format_type` | emitted `<varFormat type="…">` matches `registry["ddi"]["formatType"]` |
| `test_example_emits_some_var` | every PresentationVariant example produces at least one `<var>` |
| `test_example_other_pattern_group` | variants with `presentation.withOther=true` emit `<varGrp type="other">` |
| `test_grid_emits_grid_var_group` | grid variant emits `<varGrp type="grid">` |

### XLSForm → LimeSurvey TSV (`test_xlsform_to_lstsv.py`)

Parametrized over each LS-supported QuestionType (= `limesurvey.typeCode` present and `supported != false`):

| Test | Asserts |
|------|---------|
| `test_minimal_form_type_code` | emitted Q-row `type/scale` cell matches `registry["limesurvey"]["typeCode"]` |
| `test_or_other_flag` | types with `supportsOther=true` + `or_other` suffix in input → emitted Q-row has `other="Y"` |
| `test_example_produces_questions` | every LS-supported example produces at least one Q-row |
| `test_example_other_flag` | examples with `presentation.withOther=true` produce at least one Q-row with `other="Y"` |

## Running

```bash
# All transformations, skip docker-gated drivers
uv run pytest tests/transformations/ -m "not docker"

# Single test file
uv run pytest tests/transformations/test_xlsform_to_ddi.py -v

# Include qwacback (requires docker-compose up + QWACBACK_URL=http://localhost:8080)
uv run pytest tests/transformations/

# Point at a custom xlsform2lstsv build (e.g. for testing a migration branch)
XLSFORM2LSTSV_PATH=/path/to/xlsform2lstsv uv run pytest tests/transformations/test_xlsform_to_lstsv.py
```

## Markers

- `docker` — driver requires a running container (e.g. qwacback HTTP service). Skip by default; opt in with no `-m` filter or `-m docker`.

## Known limitations

1. **survey2ddi is tautological until divergence.** Registry's `ddi.intrvl` / `ddi.formatType` / `ddi.responseDomainType` values were initially hand-derived from survey2ddi's inline maps. Tests catch *future* drift but won't catch a registry-side error that already exists in both places. Strong signal requires either an independent driver (qwacback) or external validation (DDI 2.5 XSD).

2. **No qwacback driver wired yet.** All `qwacback-*` test variants skip until `QWACBACK_URL` is set and the `/api/convert/xlsform2ddi` endpoint exists.

3. **No DDI XSD validation.** Output XML is asserted attribute-by-attribute, not validated against the official DDI 2.5 schema. A typo like `intrvl="interval"` (which slipped in earlier) wouldn't be caught at the XSD layer without explicit schema validation.

4. **xlsform2lstsv driver swallows unsupported types.** When a fixture uses `select_one_from_file` (which xlsform2lstsv currently rejects with `Unimplemented XLSForm type`), the test skips rather than fails. Add an explicit "registry says supported but tool rejects" assertion if you want to catch this divergence as a failure instead.

## Adding a new test

1. Add a new transformation test file under `tests/transformations/`.
2. Reuse `fixtures.minimal_form()` or `fixtures.load_example()` for inputs.
3. Reuse an existing driver from `drivers.py`, or add a new one (returning canonical parsed output, raising `DriverUnavailable` when the env is missing).
4. Parametrize over `fixtures.question_types()` / `ddi_emittable()` / `ls_supported()` / `presentation_variants()` as appropriate.
5. Assertions should always reference the **registry contract** (`qt["ddi"]["intrvl"]`, `qt["limesurvey"]["typeCode"]`, `variant["presentation"]["withOther"]`, …), never literal expected values.
