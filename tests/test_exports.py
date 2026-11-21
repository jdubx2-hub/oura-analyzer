from datetime import date, datetime, timezone
from pathlib import Path
import json

import pytest

from oura_analyzer.exports import (
    EXPORT_SCHEMA_VERSION,
    build_export_package,
    inspect_export,
    write_export_package,
)


def test_inspect_export_lists_files(tmp_path: Path) -> None:
    (tmp_path / "sample.csv").write_text("a,b\n1,2\n")
    assert [p.name for p in inspect_export(tmp_path)] == ["sample.csv"]


def test_inspect_export_requires_directory(tmp_path: Path) -> None:
    file_path = tmp_path / "file.txt"
    file_path.write_text("hello")
    with pytest.raises(NotADirectoryError):
        inspect_export(file_path)


def test_build_export_package_adds_manifest_without_mutating_records() -> None:
    workout = {"id": "workout-1", "distance": 1200}
    collection = {
        "date_range": {
            "start_date": "2026-10-01",
            "end_date": "2026-10-31",
            "timezone": "America/Los_Angeles",
        },
        "datasets": {"workouts": [workout], "daily_sleep": []},
        "errors": {"daily_spo2": "403: unavailable"},
    }

    package = build_export_package(
        collection,
        generated_at=datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc),
    )

    assert package["manifest"]["schema"] == "jmt-oura-export"
    assert package["manifest"]["schema_version"] == EXPORT_SCHEMA_VERSION
    assert package["manifest"]["source"] == "oura_api_v2"
    assert package["manifest"]["date_range"] == {
        "start_date": "2026-10-01",
        "end_date": "2026-10-31",
    }
    assert package["manifest"]["datasets_included"] == ["daily_sleep", "workouts"]
    assert package["manifest"]["datasets_with_errors"] == ["daily_spo2"]
    assert package["datasets"]["workouts"][0] is workout


def test_build_export_package_requires_timezone_aware_generation_time() -> None:
    collection = {
        "date_range": {"start_date": "2026-10-01", "end_date": "2026-10-31"},
        "datasets": {},
    }
    with pytest.raises(ValueError, match="timezone-aware"):
        build_export_package(collection, generated_at=datetime(2026, 11, 21))


def test_write_export_package_creates_parent_and_valid_json(tmp_path: Path) -> None:
    package = {"manifest": {"schema_version": EXPORT_SCHEMA_VERSION}, "datasets": {}}
    output = tmp_path / "nested" / "oura-export.json"

    result = write_export_package(package, output)

    assert result == output
    assert json.loads(output.read_text(encoding="utf-8")) == package
    assert not output.with_suffix(".json.tmp").exists()
