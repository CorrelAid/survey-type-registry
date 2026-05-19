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


import json
import shutil
import subprocess


def _find_worker_jar() -> Path | None:
    """Find the shadowJar built by workers/schematron-worker.

    Build it first with:
      cd workers/schematron-worker && ./gradlew shadowJar
    Or use scripts/build-worker.sh.
    """
    libs = REPO_ROOT / "workers" / "schematron-worker" / "build" / "libs"
    if not libs.exists():
        return None
    for jar in libs.glob("*-all.jar"):
        return jar
    return None


@pytest.fixture(scope="module")
def worker_jar() -> Path:
    jar = _find_worker_jar()
    if jar is None:
        pytest.skip(
            "schematron-worker jar not built. "
            "Run `bash scripts/build-worker.sh` (requires JDK 21)."
        )
    if shutil.which("java") is None:
        pytest.skip("java not on PATH (need JDK 21 for schematron-worker)")
    return jar


@pytest.mark.parametrize("variant", presentation_variants(), ids=lambda v: v["@id"])
def test_ddi_snapshot_schematron(variant, worker_jar):
    """Blessed ddi.xml passes CDL schematron rules via schematron-worker CLI."""
    snapshot = load_example_ddi(variant)
    if snapshot is None:
        pytest.skip(f"{variant['@id']}: no committed ddi.xml")

    result = subprocess.run(
        [
            "java",
            "-cp", str(worker_jar),
            "dev.correlaid.schematron.CliMain",
            "--sch", str(SCH_PATH),
            "--xml", str(example_dir(variant) / "ddi.xml"),
        ],
        capture_output=True,
        timeout=30,
    )
    if result.returncode == 0:
        return  # valid
    if result.returncode == 2:
        pytest.fail(f"worker CLI argument/IO error: {result.stderr.decode()[:500]}")

    # returncode == 1 → validation failures. Parse JSON for readable message.
    try:
        report = json.loads(result.stdout.decode())
        msgs = "\n  ".join(
            f"{e.get('rule', '?')}: {e.get('message', '?')}" for e in report.get("errors", [])
        )
    except Exception:
        msgs = result.stdout.decode()[:500]
    pytest.fail(
        f"{variant['@id']}: schematron failed.\n  {msgs}\n"
        f"Snapshot: {example_dir(variant) / 'ddi.xml'}"
    )
