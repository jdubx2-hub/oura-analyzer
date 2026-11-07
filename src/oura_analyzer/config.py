"""Project paths and configuration.

Keep secrets out of this module and out of version control. Authentication
credentials should eventually be stored in the operating-system keychain.
"""

from pathlib import Path

PROJECT_DIR = Path.cwd()
DEFAULT_DATA_DIR = PROJECT_DIR / "data"


def data_dir(path: Path | None = None) -> Path:
    """Return the configured local data directory."""
    return path or DEFAULT_DATA_DIR
