"""Download E-CUP train.parquet from Google Drive into data/.

Google Drive file id: ``1IiqGvrIooBLTMs1P759IQklKXteUfn84``
Destination: ``<repo>/data/train.parquet`` (~172–180 MB).

If ``gdown`` is not installed, the script installs it via pip.
Existing files ≥ ``MIN_BYTES`` are skipped unless ``--force`` is set.

Example:
    python scripts/download_dataset.py
    python scripts/download_dataset.py --force
"""

from __future__ import annotations

import argparse
import importlib
import subprocess
import sys
from pathlib import Path

FILE_ID = "1IiqGvrIooBLTMs1P759IQklKXteUfn84"
MIN_BYTES = 100 * 1024 * 1024
REPO_ROOT = Path(__file__).resolve().parent.parent
DEST = REPO_ROOT / "data" / "train.parquet"


def _ensure_gdown() -> None:
    """Install ``gdown`` with pip if the package is not importable."""
    try:
        importlib.import_module("gdown")
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gdown"])


def _is_complete(path: Path) -> bool:
    """Return True if ``path`` exists and is at least ``MIN_BYTES`` (not an HTML stub)."""
    return path.is_file() and path.stat().st_size >= MIN_BYTES


def download_dataset(*, force: bool = False) -> Path:
    """Download ``train.parquet`` to ``DEST``.

    Args:
        force: Re-download even if a complete file already exists.

    Returns:
        Path to ``data/train.parquet``.

    Raises:
        RuntimeError: Download finished but the file is smaller than ``MIN_BYTES``.
    """
    DEST.parent.mkdir(parents=True, exist_ok=True)
    if not force and _is_complete(DEST):
        print(f"Skip: {DEST} already exists ({DEST.stat().st_size} bytes)")
        return DEST

    _ensure_gdown()
    gdown = importlib.import_module("gdown")
    gdown.download(id=FILE_ID, output=str(DEST), quiet=False, fuzzy=True)
    if not _is_complete(DEST):
        size = DEST.stat().st_size if DEST.exists() else 0
        raise RuntimeError(
            f"Download looks incomplete ({size} bytes < {MIN_BYTES}). "
            "Check that the Drive file is shared as Anyone with the link."
        )
    print(f"Saved {DEST} ({DEST.stat().st_size} bytes)")
    return DEST


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if data/train.parquet already looks complete.",
    )
    args = parser.parse_args()
    download_dataset(force=args.force)


if __name__ == "__main__":
    main()
