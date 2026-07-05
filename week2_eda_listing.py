from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np

# week2_eda_listing.py
# EDA on week1 combined listing dataset.
# - documents unique PropertyType values
# - filters to Residential
# - produces null-count summary and >90% missing flag
# - numeric distribution summary for ClosePrice, LivingArea, DaysOnMarket
# - saves filtered dataset and reports

INPUT_CSV = "week1_CombinedCRMLSListing.csv"
FILTERED_CSV = "week2_FilteredCRMLSListing_Residential.csv"
NULL_SUMMARY_CSV = "week2_null_summary_listing.csv"
NUMERIC_SUMMARY_CSV = "week2_numeric_summary_listing.csv"
MISSING_FLAGS_CSV = "week2_missing_flags_listing.csv"
KEY_NUMERIC = ["ClosePrice", "LivingArea", "DaysOnMarket"]
FILTER_COLUMN = "PropertyType"
FILTER_VALUE = "Residential"


def read_data(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False)


def null_summary(df: pd.DataFrame) -> pd.DataFrame:
    total = len(df)
    nulls = df.isnull().sum()
    pct = (nulls / total) * 100
    summary = pd.DataFrame({"null_count": nulls, "null_pct": pct})
    return summary.sort_values("null_pct", ascending=False)


def numeric_distribution(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    rows = []
    for c in cols:
        if c not in df.columns:
            rows.append({"field": c, "note": "missing"})
            continue
        ser = pd.to_numeric(df[c], errors="coerce")
        desc = ser.describe(percentiles=[0.01,0.05,0.1,0.25,0.5,0.75,0.9,0.95,0.99])
        iqr = desc['75%'] - desc['25%'] if '75%' in desc and '25%' in desc else np.nan
        lower = desc['25%'] - 3 * iqr if not np.isnan(iqr) else np.nan
        upper = desc['75%'] + 3 * iqr if not np.isnan(iqr) else np.nan
        outlier_count = ((ser < lower) | (ser > upper)).sum() if not np.isnan(lower) else 0
        rows.append({
            "field": c,
            "count": int(desc['count']) if 'count' in desc else 0,
            "min": desc.get('min', np.nan),
            "1%": desc.get('1%', np.nan),
            "5%": desc.get('5%', np.nan),
            "10%": desc.get('10%', np.nan),
            "25%": desc.get('25%', np.nan),
            "50%": desc.get('50%', np.nan),
            "75%": desc.get('75%', np.nan),
            "90%": desc.get('90%', np.nan),
            "95%": desc.get('95%', np.nan),
            "99%": desc.get('99%', np.nan),
            "max": desc.get('max', np.nan),
            "mean": desc.get('mean', np.nan),
            "std": desc.get('std', np.nan),
            "iqr": iqr,
            "extreme_outliers": int(outlier_count),
        })
    return pd.DataFrame(rows)


def main() -> None:
    root = Path(__file__).resolve().parent
    input_path = root / INPUT_CSV
    if not input_path.exists():
        raise FileNotFoundError(f"Expected input CSV not found: {input_path}")

    df = read_data(input_path)

    # Dataset structure
    print(f"Dataset shape (rows, cols): {df.shape}")
    print("Column dtypes:")
    print(df.dtypes)
    print("\nFirst 5 rows:")
    print(df.head())

    # Unique property types
    if FILTER_COLUMN in df.columns:
        uniques = df[FILTER_COLUMN].dropna().unique()
        print(f"Unique values in {FILTER_COLUMN}: {uniques}")
        pd.Series(uniques).to_csv(root / "week2_unique_propertytypes_listing.csv", index=False)
    else:
        print(f"Warning: {FILTER_COLUMN} not in dataframe columns.")

    # Null summary
    nulls = null_summary(df)
    nulls.to_csv(root / NULL_SUMMARY_CSV)
    print(f"Null summary saved to {NULL_SUMMARY_CSV}")

    # Missing flags (>90%)
    flags = nulls[nulls['null_pct'] > 90].copy()
    flags['flag'] = 'drop_candidate'
    flags.to_csv(root / MISSING_FLAGS_CSV)
    print(f"Missing flags (>90% null) saved to {MISSING_FLAGS_CSV}")

    # Filter Residential
    if FILTER_COLUMN in df.columns:
        before_count = len(df)
        df_filtered = df[df[FILTER_COLUMN] == FILTER_VALUE].copy()
        after_count = len(df_filtered)
        print(f"Rows before Residential filter: {before_count}")
        print(f"Rows after Residential filter: {after_count}")

        # Save filtered dataset
        df_filtered.to_csv(root / FILTERED_CSV, index=False)
        print(f"Filtered dataset saved to {FILTERED_CSV}")
    else:
        print("Skipping Residential filter because column missing.")
        df_filtered = df

    # Numeric distribution summary
    numeric_summary = numeric_distribution(df_filtered, KEY_NUMERIC)
    numeric_summary.to_csv(root / NUMERIC_SUMMARY_CSV, index=False)
    print(f"Numeric distribution summary saved to {NUMERIC_SUMMARY_CSV}")

    # Print answers to suggested intern questions (basic)
    print("\nSuggested questions answers (basic):")
    if FILTER_COLUMN in df.columns:
        prop_counts = df[FILTER_COLUMN].value_counts(dropna=False)
        print(prop_counts)
    if 'ClosePrice' in df_filtered.columns:
        print(f"Median ClosePrice: {df_filtered['ClosePrice'].median(skipna=True)}")
        print(f"Mean ClosePrice: {df_filtered['ClosePrice'].mean(skipna=True)}")
    if 'DaysOnMarket' in df_filtered.columns:
        print(f"DaysOnMarket distribution (describe):\n{df_filtered['DaysOnMarket'].describe()}" )


if __name__ == '__main__':
    main()
