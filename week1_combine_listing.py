from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

# week1_combine_listing.py
# This script concatenates all CRMLSListing monthly files from January 2024
# through the most recently completed month, then filters to PropertyType == 'Residential'.
#
# Comments confirming row counts:
# - Row count before concatenation: prints per-month counts and their sum (confirmed at runtime).
# - Row count after concatenation: prints length of the combined dataframe (should equal the summed per-month counts).
# - Row count before Residential filter: same as after concatenation (the combined dataset).
# - Row count after Residential filter: prints length of the filtered dataframe.
#
# Expected total rows (approx): ~930000 rows across all months (combined dataset).

START_MONTH = "202401"
FILE_PATTERN = r"CRMLSListing(\d{6})\.csv$"
COMBINED_OUTPUT = "week1_CombinedCRMLSListing.csv"
RESIDENTIAL_OUTPUT = "week1_CombinedCRMLSListing_Residential.csv"
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
        raise ValueError("No monthly listing CSV files found for the requested range.")

    frames = []
    per_file_counts = []
    for path in files:
        df = pd.read_csv(path)
        per_file_counts.append((path.name, len(df)))
        df["source_file"] = path.name
        frames.append(df)

    # Row count before concatenation: show per-file counts and their sum
    total_before = sum(cnt for _, cnt in per_file_counts)
    print("Row counts per file (before concatenation):")
    for name, cnt in per_file_counts:
        print(f"  {name}: {cnt}")
    print(f"Row count before concatenation (sum of months): {total_before}")

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
        raise FileNotFoundError("No listing monthly files found for January 2024 or later.")

    months = [month for month, _ in monthly]
    paths = [path for _, path in monthly]

    print(f"Found {len(paths)} listing monthly files from {months[0]} through {months[-1]}.")

    combined = combine_csv_files(paths)

    # Row count after concatenation: length of combined dataframe
    combined_count = len(combined)
    print(f"Row count after concatenation: {combined_count}")

    # Sanity check / comment confirming expected overall size
    if 900000 <= combined_count <= 960000:
        print(f"CONFIRMATION: Combined listing rows ~{combined_count} (within expected ~930000 range).")
    else:
        print(f"WARNING: Combined listing rows = {combined_count} (outside expected range).")

    # Save full combined file
    combined.to_csv(root / COMBINED_OUTPUT, index=False)
    print(f"Saved combined listing dataset to: {COMBINED_OUTPUT}")

    # Row count before Residential filter: same as combined_count (explicit print)
    print(f"Row count before Residential filter: {combined_count}")

    residential = filter_residential(combined)
    residential_count = len(residential)
    print(f"Row count after Residential filter: {residential_count}")

    residential.to_csv(root / RESIDENTIAL_OUTPUT, index=False)
    print(f"Saved Residential-only listing dataset to: {RESIDENTIAL_OUTPUT}")


if __name__ == "__main__":
    main()
