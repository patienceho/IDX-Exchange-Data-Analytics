from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

# This script concatenates all CRMLSSold monthly files from January 2024 through the
# most recently completed month, then filters the combined dataset to PropertyType == 'Residential'.

START_MONTH = "202401"
FILE_PATTERN = r"CRMLSSold(\d{6})\.csv$"
COMBINED_OUTPUT = "CombinedCRMLSSold.csv"
RESIDENTIAL_OUTPUT = "CombinedCRMLSSold_Residential.csv"
FILTER_COLUMN = "PropertyType"
FILTER_VALUE = "Residential"


def find_monthly_files(root: Path) -> list[tuple[str, Path]]:
    matcher = re.compile(FILE_PATTERN)
    results = []

    for path in sorted(root.iterdir()):
        if path.is_file():
            match = matcher.match(path.name)
            if match:
                month = match.group(1)
                if month >= START_MONTH:
                    results.append((month, path))

    return sorted(results, key=lambda item: item[0])


def combine_csv_files(files: list[Path]) -> pd.DataFrame:
    if not files:
        raise ValueError("No monthly sold CSV files found for the requested range.")

    frames = []
    for path in files:
        df = pd.read_csv(path)
        df["source_file"] = path.name
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    return combined


def filter_residential(df: pd.DataFrame) -> pd.DataFrame:
    if FILTER_COLUMN not in df.columns:
        raise KeyError(f"Expected filter column '{FILTER_COLUMN}' not found in the dataframe.")

    residential = df[df[FILTER_COLUMN] == FILTER_VALUE].copy()
    return residential


def main() -> None:
    root = Path(__file__).resolve().parent
    monthly = find_monthly_files(root)

    if not monthly:
        raise FileNotFoundError("No sold monthly files found for January 2024 or later.")

    months = [month for month, _ in monthly]
    paths = [path for _, path in monthly]

    print(f"Found {len(paths)} sold monthly files from {months[0]} through {months[-1]}.")
    print(f"Row count before concatenation: 0 (per-month counts are displayed below)")

    combined = combine_csv_files(paths)
    print(f"Row count after concatenation: {len(combined)}")

    combined.to_csv(root / COMBINED_OUTPUT, index=False)
    print(f"Saved combined sold dataset to: {COMBINED_OUTPUT}")

    residential = filter_residential(combined)
    print(f"Row count after Residential filter: {len(residential)}")

    residential.to_csv(root / RESIDENTIAL_OUTPUT, index=False)
    print(f"Saved Residential-only sold dataset to: {RESIDENTIAL_OUTPUT}")


if __name__ == "__main__":
    main()
