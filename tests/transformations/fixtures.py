"""Test inputs for transformation tests.

Two fixture sources:
1. examples/*.xlsform.json — curated, registry-owned, paired with PresentationVariant
2. auto-generated minimal one-question XLSForms — one per QuestionType
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
REGISTRY_PATH = REPO_ROOT / "survey-types.jsonld"
EXAMPLES_DIR = REPO_ROOT / "examples"


def load_registry() -> list[dict]:
    return json.loads(REGISTRY_PATH.read_text())["@graph"]


def index_by_id(graph: list[dict]) -> dict[str, dict]:
    return {e["@id"]: e for e in graph}


def question_types() -> list[dict]:
    return [e for e in load_registry() if e.get("@type") == "QuestionType"]


def ddi_emittable() -> list[dict]:
    return [e for e in question_types() if e.get("ddi", {}).get("intrvl")]


def ls_supported() -> list[dict]:
    return [
        e for e in question_types()
        if e.get("limesurvey", {}).get("typeCode")
        and e.get("limesurvey", {}).get("supported", True) is not False
    ]


def presentation_variants() -> list[dict]:
    return [e for e in load_registry() if e.get("@type") == "PresentationVariant"]


def load_example(variant: dict) -> dict:
    """Load the source xlsform.json from a PresentationVariant's example dir."""
    path = REPO_ROOT / variant["examplePath"]
    return json.loads(path.read_text())


def example_dir(variant: dict) -> Path:
    """examples/<id>/ for a PresentationVariant."""
    return REPO_ROOT / variant["exampleDir"]


def load_example_meta(variant: dict) -> dict:
    """Load the registry-derived meta.json from the example dir."""
    return json.loads((example_dir(variant) / "meta.json").read_text())


def load_example_ddi(variant: dict) -> str | None:
    """Return committed ddi.xml string or None if not generated for this variant."""
    p = example_dir(variant) / "ddi.xml"
    return p.read_text() if p.exists() else None


def load_example_tsv(variant: dict) -> str | None:
    """Return committed tsv.tsv string or None if xlsform2lstsv doesn't support
    this variant's input types."""
    p = example_dir(variant) / "tsv.tsv"
    return p.read_text() if p.exists() else None


def to_survey_rows(example: dict) -> tuple[list[dict], dict[str, list[dict]]]:
    """Normalize example payload into (survey_rows, choices_by_list) shape
    consumed by survey2ddi.build_ddi_xml."""
    survey = list(example.get("survey", []))
    choices_raw = example.get("choices", [])
    by_list: dict[str, list[dict]] = {}
    for c in choices_raw:
        ln = c.get("list_name")
        if not ln:
            continue
        by_list.setdefault(ln, []).append({
            "name": c.get("name", ""),
            "label": c.get("label", ""),
        })
    return survey, by_list


def minimal_form(qt: dict) -> tuple[list[dict], dict[str, list[dict]]]:
    """Build a 1-question XLSForm for a QuestionType."""
    xls_type = qt["xlsform"]["typeString"]
    needs_list = qt["xlsform"].get("requiresListName", False)

    if needs_list:
        type_str = f"{xls_type} mylist"
        choices = {
            "mylist": [
                {"name": "a", "label": "Option A"},
                {"name": "b", "label": "Option B"},
            ]
        }
    else:
        type_str = xls_type
        choices = {}

    survey = [{"type": type_str, "name": "q1", "label": "Question 1"}]
    return survey, choices
