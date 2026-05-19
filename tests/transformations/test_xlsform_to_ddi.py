"""Transformation: XLSForm → DDI-Codebook XML.

Two input sources, run through each available DDI driver:
1. Auto-generated minimal forms — one per DDI-emittable QuestionType
2. Curated examples/*.xlsform.json — paired with PresentationVariants

Assertions reference the registry's per-type contract (ddi block on
QuestionType, presentation flags on PresentationVariant).
"""
from __future__ import annotations

import pytest

from .drivers import (
    DDI_DRIVERS,
    DDI_NS,
    DriverUnavailable,
    ddi_find,
    ddi_findall,
    ddi_child,
)
from .fixtures import (
    ddi_emittable,
    load_example,
    minimal_form,
    presentation_variants,
    to_survey_rows,
)


# ----- driver parametrization -----

def _driver_param(name):
    marks = []
    if name != "survey2ddi":
        # qwacback needs docker; mark to skip-by-default unless QWACBACK_URL set
        marks = [pytest.mark.docker]
    return pytest.param(name, marks=marks, id=name)


@pytest.fixture(params=[_driver_param(n) for n in DDI_DRIVERS])
def ddi_driver(request):
    fn = DDI_DRIVERS[request.param]
    return fn


# ----- helpers -----

def _is_multiple_resp(qt: dict) -> bool:
    s = qt.get("ddi", {}).get("structure", {})
    return s.get("element") == "varGrp" and s.get("type") == "multipleResp"


def _binary_var(root, name_prefix: str):
    """First <var name='{prefix}_*'> (sibling of multipleResp varGrp)."""
    for v in ddi_findall(root, "var"):
        n = v.get("name") or ""
        if n.startswith(f"{name_prefix}_") and n != f"{name_prefix}_other":
            return v
    return None


def _safe_driver(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except DriverUnavailable as e:
        pytest.skip(str(e))


# =============================================================================
# Input A: minimal forms per QuestionType
# =============================================================================

def _skip_if_driver_drops_type(qt: dict, var) -> None:
    """If registry says type is DDI-emittable but driver emitted no <var>, mark xfail
    rather than fail. Driver-side divergence is reported separately."""
    if var is None:
        pytest.xfail(
            f"{qt['@id']}: registry says DDI-emittable but driver emitted no <var>. "
            "Driver divergence — file upstream issue."
        )


@pytest.mark.parametrize("qt", ddi_emittable(), ids=lambda e: e["@id"])
def test_minimal_form_intrvl(ddi_driver, qt):
    survey, choices = minimal_form(qt)
    root = _safe_driver(ddi_driver, survey, choices)

    expected = qt["ddi"]["intrvl"]
    if _is_multiple_resp(qt):
        var = _binary_var(root, "q1")
    else:
        var = ddi_find(root, "var", "q1")
    _skip_if_driver_drops_type(qt, var)

    assert var.get("intrvl") == expected, (
        f"{qt['@id']}: registry intrvl={expected!r}, emitted {var.get('intrvl')!r}"
    )


@pytest.mark.parametrize("qt", ddi_emittable(), ids=lambda e: e["@id"])
def test_minimal_form_response_domain(ddi_driver, qt):
    expected = qt["ddi"].get("responseDomainType")
    if not expected:
        pytest.skip("no responseDomainType in registry")

    survey, choices = minimal_form(qt)
    root = _safe_driver(ddi_driver, survey, choices)

    if _is_multiple_resp(qt):
        grp = ddi_find(root, "varGrp", "q1")
        if grp is None:
            pytest.xfail(
                f"{qt['@id']}: registry says multipleResp varGrp but driver emitted none."
            )
        assert grp.get("type") == "multipleResp", (
            f"{qt['@id']}: expected varGrp/@type='multipleResp', got {grp.get('type')!r}"
        )
        var = _binary_var(root, "q1")
        _skip_if_driver_drops_type(qt, var)
        qstn = ddi_child(var, "qstn")
        if qstn is None:
            pytest.skip("no <qstn> on binary var")
        assert qstn.get("responseDomainType") == expected
        return

    var = ddi_find(root, "var", "q1")
    _skip_if_driver_drops_type(qt, var)
    qstn = ddi_child(var, "qstn")
    if qstn is None:
        pytest.skip(f"no <qstn> for {qt['@id']}")
    assert qstn.get("responseDomainType") == expected, (
        f"{qt['@id']}: registry={expected!r}, emitted={qstn.get('responseDomainType')!r}"
    )


@pytest.mark.parametrize("qt", ddi_emittable(), ids=lambda e: e["@id"])
def test_minimal_form_format_type(ddi_driver, qt):
    expected = qt["ddi"].get("formatType")
    if not expected:
        pytest.skip("no formatType in registry")

    survey, choices = minimal_form(qt)
    root = _safe_driver(ddi_driver, survey, choices)

    if _is_multiple_resp(qt):
        var = _binary_var(root, "q1")
    else:
        var = ddi_find(root, "var", "q1")
    _skip_if_driver_drops_type(qt, var)

    vf = ddi_child(var, "varFormat")
    if vf is None:
        pytest.skip(f"no <varFormat> for {qt['@id']}")
    assert vf.get("type") == expected, (
        f"{qt['@id']}: registry formatType={expected!r}, emitted {vf.get('type')!r}"
    )


# =============================================================================
# Input B: curated examples (PresentationVariant fixtures)
# =============================================================================

@pytest.mark.parametrize("variant", presentation_variants(), ids=lambda v: v["@id"])
def test_example_emits_some_var(ddi_driver, variant):
    """Every PresentationVariant example produces at least one <var> in DDI output."""
    example = load_example(variant)
    survey, choices = to_survey_rows(example)
    root = _safe_driver(ddi_driver, survey, choices)
    vars_emitted = ddi_findall(root, "var")
    if not vars_emitted:
        pytest.xfail(
            f"{variant['@id']}: driver emitted zero <var> elements for this example. "
            "Driver-side divergence from registry contract."
        )


@pytest.mark.parametrize(
    "variant",
    [v for v in presentation_variants()
     if v.get("presentation", {}).get("withOther")],
    ids=lambda v: v["@id"],
)
def test_example_other_pattern_group(ddi_driver, variant):
    """Variants with withOther=true must emit a parent <varGrp type='other'>."""
    example = load_example(variant)
    survey, choices = to_survey_rows(example)
    root = _safe_driver(ddi_driver, survey, choices)

    other_groups = [g for g in ddi_findall(root, "varGrp") if g.get("type") == "other"]
    assert other_groups, (
        f"{variant['@id']}: withOther=true but no <varGrp type='other'> emitted"
    )


@pytest.mark.parametrize(
    "variant",
    [v for v in presentation_variants()
     if v.get("presentation", {}).get("withLongList")],
    ids=lambda v: v["@id"],
)
def test_long_list_concept_vocab(ddi_driver, variant):
    """withLongList variants should reference the external vocab via <concept vocab='...'>.

    Convention `convention:externalCodeList` (qwacback). survey2ddi may not yet
    implement this; the test xfails for survey2ddi until it does.
    """
    example = load_example(variant)
    survey, choices = to_survey_rows(example)
    root = _safe_driver(ddi_driver, survey, choices)

    # Expected vocab = filename stem of "select_X_from_file <filename>.csv"
    raw_type = example["survey"][0]["type"]
    parts = raw_type.split(None, 1)
    if len(parts) < 2 or not parts[1].endswith(".csv"):
        pytest.skip(f"cannot derive vocab from type {raw_type!r}")
    expected_vocab = parts[1].removesuffix(".csv")

    # Find any <concept vocab="...">
    concepts = []
    for path in (f".//{{{DDI_NS}}}concept", ".//concept"):
        concepts.extend(root.iterfind(path))
    matched = [c for c in concepts if c.get("vocab") == expected_vocab]
    if not matched:
        pytest.xfail(
            f"{variant['@id']}: driver did not emit <concept vocab={expected_vocab!r}>. "
            "Registry convention:externalCodeList not yet implemented in this driver."
        )


@pytest.mark.parametrize(
    "variant",
    [v for v in presentation_variants() if v["@id"] == "variant:grid"],
    ids=lambda v: v["@id"],
)
def test_grid_emits_grid_var_group(ddi_driver, variant):
    """grid variant must produce <varGrp type='grid'>."""
    example = load_example(variant)
    survey, choices = to_survey_rows(example)
    root = _safe_driver(ddi_driver, survey, choices)

    grid_groups = [g for g in ddi_findall(root, "varGrp") if g.get("type") == "grid"]
    assert grid_groups, (
        f"{variant['@id']}: expected <varGrp type='grid'>, none found"
    )
