"""Import helpers for files downloaded from Oura account data export."""

from pathlib import Path


def inspect_export(path: Path) -> list[Path]:
    """List files in an extracted export directory.

    This intentionally does not assume a particular export schema yet.
    """
    if not path.exists():
        raise FileNotFoundError(path)
    if not path.is_dir():
        raise NotADirectoryError(path)
    return sorted(p for p in path.rglob("*") if p.is_file())
