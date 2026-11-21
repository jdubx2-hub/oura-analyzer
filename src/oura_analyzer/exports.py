"""Export packaging helpers for Oura API responses."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXPORT_SCHEMA_VERSION = "1.0.0"


def inspect_export(path: Path) -> list[Path]:
    """List files in an extracted export directory.

    This intentionally does not assume a particular schema yet.
    """
    if not path.exists():
        raise FileNotFoundError(path)
    if not path.is_dir():
        raise NotADirectoryError(path)
    return sorted(p for p in path.rglob("*") if p.is_file())


def build_export_package(
    collection: dict[str, Any],
    *,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    """Wrap collected Oura datasets in a versioned, downstream-friendly envelope.

    Dataset records remain unchanged from the Oura API. This preserves source
    fidelity while giving downstream applications a stable package contract.
    """
    timestamp = generated_at or datetime.now(timezone.utc)
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("generated_at must be timezone-aware.")

    date_range = collection["date_range"]
    return {
        "manifest": {
            "schema": "jmt-oura-export",
            "schema_version": EXPORT_SCHEMA_VERSION,
            "source": "oura_api_v2",
            "generated_at": timestamp.astimezone(timezone.utc).isoformat(),
            "date_range": {
                "start_date": date_range["start_date"],
                "end_date": date_range["end_date"],
                **(
                    {"timezone": date_range["timezone"]}
                    if date_range.get("timezone")
                    else {}
                ),
            },
            "datasets_included": sorted(collection["datasets"]),
            "datasets_with_errors": sorted(collection.get("errors", {})),
        },
        "datasets": collection["datasets"],
        "errors": collection.get("errors", {}),
    }


def write_export_package(package: dict[str, Any], path: Path) -> Path:
    """Write a package as UTF-8 JSON, creating its parent directory if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        temporary_path.write_text(
            json.dumps(package, indent=2, ensure_ascii=False, default=str) + "\n",
            encoding="utf-8",
        )
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)
    return path
