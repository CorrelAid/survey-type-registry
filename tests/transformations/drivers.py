"""Transformation drivers — one per (input → output) edge in the pipeline.

Each driver is a callable that takes (survey_rows, choices_by_list, settings)
and returns the transformed artifact in canonical form (parsed XML for DDI,
list-of-dicts for TSV).

Drivers may be unavailable (missing dep, docker not up) — they raise
DriverUnavailable so tests skip cleanly.
"""
from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from typing import Callable


class DriverUnavailable(Exception):
    """Raised when a transformation driver is not callable in this environment."""


# ---------- XLSForm → DDI ----------

def survey2ddi_xlsform_to_ddi(
    survey_rows: list[dict],
    choices_by_list: dict,
    settings: dict | None = None,
) -> ET.Element:
    try:
        from survey2ddi_core.ddi_xml import build_ddi_xml
    except ImportError as e:
        raise DriverUnavailable(f"survey2ddi not installed: {e}") from e

    xml = build_ddi_xml(
        asset_name="conformance-test",
        survey_rows=survey_rows,
        choices_by_list=choices_by_list,
        settings=settings or {},
        submissions=[],
    )
    return ET.fromstring(xml)


def qwacback_xlsform_to_ddi(
    survey_rows: list[dict],
    choices_by_list: dict,
    settings: dict | None = None,
) -> ET.Element:
    url = os.getenv("QWACBACK_URL")
    if not url:
        raise DriverUnavailable("QWACBACK_URL not set (start docker-compose first)")
    try:
        import httpx
    except ImportError as e:
        raise DriverUnavailable(f"httpx not installed: {e}") from e

    payload = {
        "survey": survey_rows,
        "choices": [
            {"list_name": ln, **c}
            for ln, items in choices_by_list.items()
            for c in items
        ],
    }
    r = httpx.post(f"{url}/api/convert/xlsform2ddi", json=payload, timeout=10.0)
    r.raise_for_status()
    return ET.fromstring(r.text)


DDI_DRIVERS: dict[str, Callable] = {
    "survey2ddi": survey2ddi_xlsform_to_ddi,
    "qwacback": qwacback_xlsform_to_ddi,
}


# ---------- XLSForm → LS TSV ----------

_DRIVER_DIR = os.path.dirname(os.path.abspath(__file__))
_NODE_DRIVER = os.path.join(_DRIVER_DIR, "_xlsform2lstsv_driver.mjs")


def xlsform2lstsv_to_tsv(
    survey_rows: list[dict],
    choices_by_list: dict,
    settings: dict | None = None,
) -> list[dict]:
    """Run XLSFormToTSVConverter.convert via node subprocess.

    Returns list of row dicts (header-keyed). Requires:
    - `node` on PATH
    - xlsform2lstsv built with `npm run build` (dist/index.js present)
    - XLSFORM2LSTSV_PATH env var, or sibling layout repo-root/../xlsform2lstsv
    """
    import json
    import shutil
    import subprocess

    if shutil.which("node") is None:
        raise DriverUnavailable("node not on PATH")

    pkg_path = os.environ.get(
        "XLSFORM2LSTSV_PATH",
        os.path.normpath(os.path.join(_DRIVER_DIR, "..", "..", "..", "xlsform2lstsv")),
    )
    dist = os.path.join(pkg_path, "dist", "index.js")
    if not os.path.exists(dist):
        raise DriverUnavailable(
            f"xlsform2lstsv dist missing at {dist}. "
            "Run `npm run build` in xlsform2lstsv, or set XLSFORM2LSTSV_PATH."
        )

    payload = {
        "survey": survey_rows,
        "choices": [
            {"list_name": ln, **c}
            for ln, items in choices_by_list.items()
            for c in items
        ],
        "settings": settings or [],
    }
    try:
        proc = subprocess.run(
            ["node", _NODE_DRIVER],
            input=json.dumps(payload).encode(),
            capture_output=True,
            check=True,
            timeout=20,
        )
    except subprocess.CalledProcessError as e:
        raise DriverUnavailable(
            f"xlsform2lstsv driver failed: {e.stderr.decode()[:500]}"
        ) from e

    return parse_tsv(proc.stdout.decode())


def parse_tsv(tsv: str) -> list[dict]:
    lines = [ln for ln in tsv.splitlines() if ln.strip()]
    if not lines:
        return []
    headers = lines[0].split("\t")
    rows = []
    for ln in lines[1:]:
        cells = ln.split("\t")
        # Pad short rows
        cells += [""] * (len(headers) - len(cells))
        rows.append(dict(zip(headers, cells, strict=False)))
    return rows


# ---------- DDI XML helpers ----------

DDI_NS = "ddi:codebook:2_5"


def ddi_find(root: ET.Element, tag: str, name: str | None = None) -> ET.Element | None:
    """Find first <tag> element by name, namespace-tolerant."""
    selectors = [f".//{{{DDI_NS}}}{tag}", f".//{tag}"]
    for sel in selectors:
        for el in root.iterfind(sel):
            if name is None or el.get("name") == name:
                return el
    return None


def ddi_findall(root: ET.Element, tag: str) -> list[ET.Element]:
    out: list[ET.Element] = []
    for sel in (f".//{{{DDI_NS}}}{tag}", f".//{tag}"):
        out.extend(root.iterfind(sel))
        if out:
            break
    return out


def ddi_child(parent: ET.Element, tag: str) -> ET.Element | None:
    for path in (f"{{{DDI_NS}}}{tag}", tag):
        el = parent.find(path)
        if el is not None:
            return el
    return None
