from pathlib import Path

import pytest

from oura_analyzer.exports import inspect_export


def test_inspect_export_lists_files(tmp_path: Path) -> None:
    (tmp_path / "sample.csv").write_text("a,b\n1,2\n")
    assert [p.name for p in inspect_export(tmp_path)] == ["sample.csv"]


def test_inspect_export_requires_directory(tmp_path: Path) -> None:
    file_path = tmp_path / "file.txt"
    file_path.write_text("hello")
    with pytest.raises(NotADirectoryError):
        inspect_export(file_path)
