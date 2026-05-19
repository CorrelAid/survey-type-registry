"""Transformation: XLSForm → LimeSurvey TSV via xlsform2lstsv (node subprocess).

Asserts emitted TSV `type/scale` column matches registry's `limesurvey.typeCode`
for each LS-supported QuestionType. Also checks selected examples produce
expected row structure.
"""
from __future__ import annotations

import pytest

from .drivers import (
    DriverUnavailable,
    xlsform2lstsv_to_tsv,
)
from .fixtures import (
    load_example,
    ls_supported,
    minimal_form,
    presentation_variants,
    to_survey_rows,
)


def _safe(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except DriverUnavailable as e:
        pytest.skip(str(e))


def _question_rows(tsv_rows: list[dict]) -> list[dict]:
    return [r for r in tsv_rows if r.get("class") == "Q"]


def _answer_rows(tsv_rows: list[dict]) -> list[dict]:
    return [r for r in tsv_rows if r.get("class") == "A"]


# =============================================================================
# minimal forms per LS-supported QuestionType
# =============================================================================

@pytest.mark.parametrize("qt", ls_supported(), ids=lambda e: e["@id"])
def test_minimal_form_type_code(qt):
    """Each LS-supported type emits a Q row with registry's typeCode."""
    survey, choices = minimal_form(qt)
    rows = _safe(xlsform2lstsv_to_tsv, survey, choices)

    qrows = _question_rows(rows)
    assert qrows, f"{qt['@id']}: no Q rows emitted"

    q1 = next((r for r in qrows if r.get("name") == "q1"), None)
    assert q1 is not None, f"{qt['@id']}: no row name=q1"

    expected = qt["limesurvey"]["typeCode"]
    assert q1["type/scale"] == expected, (
        f"{qt['@id']}: registry typeCode={expected!r}, "
        f"emitted {q1['type/scale']!r}"
    )


@pytest.mark.parametrize(
    "qt",
    [e for e in ls_supported() if e.get("limesurvey", {}).get("supportsOther")],
    ids=lambda e: e["@id"],
)
def test_or_other_flag(qt):
    """Types supporting `or_other` emit `other=Y` when input has `... or_other`."""
    survey, choices = minimal_form(qt)
    survey[0]["type"] = survey[0]["type"] + " or_other"
    rows = _safe(xlsform2lstsv_to_tsv, survey, choices)

    q1 = next((r for r in _question_rows(rows) if r.get("name") == "q1"), None)
    assert q1 is not None
    assert q1.get("other") == "Y", (
        f"{qt['@id']}: supportsOther=true + or_other input → expected other=Y, "
        f"got {q1.get('other')!r}"
    )


# =============================================================================
# Presentation variant examples → TSV
# =============================================================================

# Only run examples whose base XLSForm type is LS-supported.
def _ls_supported_variants() -> list[dict]:
    supported_types = {e["xlsform"]["typeString"] for e in ls_supported()}
    out = []
    for v in presentation_variants():
        base = (v.get("skos:broader") or {}).get("@id", "")
        slug = base.split(":", 1)[1] if ":" in base else base
        if slug in supported_types:
            out.append(v)
    return out


@pytest.mark.parametrize("variant", _ls_supported_variants(), ids=lambda v: v["@id"])
def test_example_produces_questions(variant):
    example = load_example(variant)
    survey, choices = to_survey_rows(example)
    rows = _safe(xlsform2lstsv_to_tsv, survey, choices)
    assert _question_rows(rows), f"{variant['@id']}: example produced zero Q rows"


@pytest.mark.parametrize(
    "variant",
    [v for v in _ls_supported_variants()
     if v.get("presentation", {}).get("withOther")],
    ids=lambda v: v["@id"],
)
def test_example_other_flag(variant):
    """withOther presentation variants → at least one Q row has other=Y."""
    example = load_example(variant)
    survey, choices = to_survey_rows(example)
    rows = _safe(xlsform2lstsv_to_tsv, survey, choices)
    qrows = _question_rows(rows)
    assert any(r.get("other") == "Y" for r in qrows), (
        f"{variant['@id']}: withOther=true but no Q row has other=Y"
    )
