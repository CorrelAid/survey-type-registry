"""Validate blessed example DDI snapshots against the official DDI 2.5 XSD
and the CDL custom schematron rules.

Schemas live under ``schemas/`` and are the canonical source for downstream
consumers (qwacback, survey2ddi). Each ``examples/<id>/ddi.xml`` must:

1. Parse as valid XML.
2. Validate against ``schemas/xsd/codebook.xsd``.
3. Pass all schematron assertions in ``schemas/schematron/ddi_custom_rules.sch``.

Drift in any of these = the blessed snapshot violates registry contract.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from .fixtures import (
    REPO_ROOT,
    example_dir,
    load_example_ddi,
    presentation_variants,
)

lxml = pytest.importorskip("lxml")
from lxml import etree  # noqa: E402


XSD_PATH = REPO_ROOT / "schemas" / "xsd" / "codebook.xsd"
SCH_PATH = REPO_ROOT / "schemas" / "schematron" / "ddi_custom_rules.sch"


@pytest.fixture(scope="module")
def xsd_validator() -> etree.XMLSchema:
    if not XSD_PATH.exists():
        pytest.skip(f"DDI 2.5 XSD missing at {XSD_PATH}")
    return etree.XMLSchema(etree.parse(str(XSD_PATH)))


@pytest.mark.parametrize("variant", presentation_variants(), ids=lambda v: v["@id"])
def test_ddi_snapshot_xsd_valid(variant, xsd_validator):
    """Blessed ddi.xml must validate against DDI-Codebook 2.5 XSD."""
    snapshot = load_example_ddi(variant)
    if snapshot is None:
        pytest.skip(f"{variant['@id']}: no committed ddi.xml")

    try:
        doc = etree.fromstring(snapshot.encode())
    except etree.XMLSyntaxError as e:
        pytest.fail(f"{variant['@id']}: ddi.xml is not well-formed: {e}")

    if not xsd_validator.validate(doc):
        errors = "\n  ".join(str(e) for e in xsd_validator.error_log)
        pytest.fail(
            f"{variant['@id']}: XSD validation failed.\n  {errors}\n"
            f"Snapshot: {example_dir(variant) / 'ddi.xml'}"
        )


@pytest.mark.parametrize("variant", presentation_variants(), ids=lambda v: v["@id"])
def test_ddi_snapshot_schematron(variant):
    """Blessed ddi.xml SHOULD pass CDL schematron rules.

    Currently skipped: bundled schematron uses queryBinding='xpath2' + fn:current(),
    which lxml.isoschematron (xpath1 only) and pyschematron (no fn:current) both
    refuse. Enforcement happens in qwacback's Java schematron-worker. To wire it
    here, replace fn:current() uses, drop to xpath1, or invoke saxon CLI.
    """
    pytest.skip("schematron enforcement requires a saxon-based processor — TODO")
