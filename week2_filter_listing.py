from __future__ import annotations

from pathlib import Path

import pandas as pd

# week2_filter_listing.py
# Reads the week1 combined listing dataset, documents PropertyType values,
# filters to Residential, and saves the filtered output.

INPUT_CSV = "week1_CombinedCRMLSListing.csv"
OUTPUT_CSV = "week2_FilteredCRMLSListing_Residential.csv"
FILTER_COLUMN = "PropertyType"
FILTER_VALUE = "Residential"


def main() -> None:
    root = Path(__file__).resolve().parent
    input_path = root / INPUT_CSV
    if not input_path.exists():
        raise FileNotFoundError(f"Missing input file: {input_path}")

    df = pd.read_csv(input_path, low_memory=False)

    print(f"Loaded listing dataset: {df.shape[0]} rows, {df.shape[1]} columns")

    if FILTER_COLUMN not in df.columns:
        raise KeyError(f"Expected filter column '{FILTER_COLUMN}' not found")

    unique_types = sorted(df[FILTER_COLUMN].dropna().unique())
    print(f"Unique values in {FILTER_COLUMN}: {unique_types}")

    before_count = len(df)
    df_filtered = df[df[FILTER_COLUMN] == FILTER_VALUE].copy()
    after_count = len(df_filtered)

    print(f"Rows before Residential filter: {before_count}")
    print(f"Rows after Residential filter: {after_count}")

    df_filtered.to_csv(root / OUTPUT_CSV, index=False)
    print(f"Saved Residential-only listing dataset to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
