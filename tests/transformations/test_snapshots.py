"""Snapshot regression: driver output vs committed example artifacts.

Each example dir holds derived artifacts emitted by `codegen.py`:
- `ddi.xml`  — current survey2ddi output (canonical generator)
- `tsv.tsv`  — current xlsform2lstsv output (only when XLSForm types supported)
- `meta.json` — registry-derived metadata

These tests re-run the same drivers at test time and compare against the
committed snapshots. Any diff = either a driver regression or an intentional
upstream change requiring `python codegen.py && git add examples/`.

For per-attribute conformance (intrvl/typeCode/etc.) see test_xlsform_to_ddi.py
and test_xlsform_to_lstsv.py. These tests catch *structural* drift those don't.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from .drivers import (
    DriverUnavailable,
    xlsform2lstsv_to_tsv,
)
from .fixtures import (
    example_dir,
    load_example,
    load_example_ddi,
    load_example_tsv,
    presentation_variants,
    to_survey_rows,
)


def _canon_xml(xml_str: str) -> str:
    """Whitespace + attribute-order-normalized XML for snapshot diffing."""
    return ET.canonicalize(xml_str)


def _safe(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except DriverUnavailable as e:
        pytest.skip(str(e))


# =============================================================================
# DDI snapshot (driver: survey2ddi)
# =============================================================================

@pytest.mark.parametrize("variant", presentation_variants(), ids=lambda v: v["@id"])
def test_ddi_snapshot(variant):
    """survey2ddi driver output matches committed ddi.xml byte-for-byte (canonicalized)."""
    snapshot = load_example_ddi(variant)
    if snapshot is None:
        pytest.skip(f"{variant['@id']}: no committed ddi.xml")

    example = load_example(variant)
    survey, choices = to_survey_rows(example)
    try:
        from survey2ddi_core.ddi_xml import build_ddi_xml
    except ImportError as e:
        pytest.skip(f"survey2ddi not installed: {e}")

    observed = build_ddi_xml(
        asset_name=variant["@id"].split(":", 1)[1],
        survey_rows=survey,
        choices_by_list=choices,
        settings={},
        submissions=[],
    )
    # survey2ddi build_ddi_xml returns string already; the driver re-parses.
    # Canonicalize both sides for stable comparison.
    expected_c = _canon_xml(snapshot)
    observed_c = _canon_xml(observed)
    assert observed_c == expected_c, (
        f"{variant['@id']}: DDI snapshot drift.\n"
        f"Run `uv run python codegen.py && git add examples/`, inspect diff, "
        f"commit if intentional.\n"
        f"Snapshot path: {example_dir(variant) / 'ddi.xml'}"
    )


# =============================================================================
# LS TSV snapshot (driver: xlsform2lstsv)
# =============================================================================

@pytest.mark.parametrize("variant", presentation_variants(), ids=lambda v: v["@id"])
def test_tsv_snapshot(variant):
    """xlsform2lstsv driver output matches committed tsv.tsv byte-for-byte."""
    snapshot = load_example_tsv(variant)
    if snapshot is None:
        pytest.skip(
            f"{variant['@id']}: no committed tsv.tsv "
            "(input uses LS-unsupported XLSForm types — expected)"
        )

    example = load_example(variant)
    survey, choices = to_survey_rows(example)

    try:
        rows = xlsform2lstsv_to_tsv(survey, choices)
    except DriverUnavailable as e:
        pytest.skip(str(e))

    # rows is list[dict]; reconstruct TSV in same shape as committed snapshot
    if not rows:
        observed = ""
    else:
        headers = list(rows[0].keys())
        lines = ["\t".join(headers)]
        for r in rows:
            lines.append("\t".join(r.get(h, "") for h in headers))
        observed = "\n".join(lines) + "\n"

    # Normalize both sides: strip trailing whitespace per line, collapse blank tails
    def norm(s: str) -> list[str]:
        return [ln.rstrip() for ln in s.splitlines() if ln.strip()]

    expected_lines = norm(snapshot)
    observed_lines = norm(observed)

    assert observed_lines == expected_lines, (
        f"{variant['@id']}: TSV snapshot drift.\n"
        f"Run `uv run python codegen.py && git add examples/`, inspect diff, "
        f"commit if intentional.\n"
        f"Snapshot path: {example_dir(variant) / 'tsv.tsv'}"
    )
