"""Build the ignored Agmarknet datasets required by the FastAPI service.

This script is intended for Render's build command. It deliberately delegates
to the project's existing download, ingestion, and cleaning scripts instead
of committing generated CSV files to Git.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "cleaned_dataset.csv"
REQUIRED_COLUMNS = {
    "Reported Date",
    "State Name",
    "District Name",
    "Mandi",
    "Crop",
    "Modal Price (Rs./Quintal)",
    "Arrivals (Tonnes)",
}


def dataset_is_valid(path: Path) -> bool:
    """Return true only for a non-empty CSV that the API can read."""
    if not path.is_file() or path.stat().st_size == 0:
        return False

    try:
        columns = set(pd.read_csv(path, nrows=1).columns)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError):
        return False

    return REQUIRED_COLUMNS.issubset(columns)


def run_pipeline() -> None:
    commands = [
        [sys.executable, "scripts/setup_and_download.py"],
        [sys.executable, "ml/preprocessing/ingest.py"],
        [sys.executable, "ml/preprocessing/cleaner.py"],
    ]

    for command in commands:
        subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def main() -> None:
    if dataset_is_valid(DATASET_PATH):
        print(f"Using existing deployment dataset: {DATASET_PATH}")
        return

    print("Generating deployment dataset from the public Agmarknet source...")
    run_pipeline()

    if not dataset_is_valid(DATASET_PATH):
        raise RuntimeError(
            "Dataset preparation completed without producing a valid "
            f"{DATASET_PATH}. Check the download and preprocessing logs."
        )

    print(f"Deployment dataset is ready: {DATASET_PATH}")


if __name__ == "__main__":
    main()
