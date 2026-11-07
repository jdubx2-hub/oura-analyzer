"""Local storage helpers.

Persistent storage is intended for user-downloaded account exports. API response
persistence will remain disabled until permitted retention is confirmed.
"""

from pathlib import Path


def ensure_data_dir(path: Path) -> Path:
    """Create and return a local data directory."""
    path.mkdir(parents=True, exist_ok=True)
    return path
