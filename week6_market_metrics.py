from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

INPUT_CSV = "week2_FilteredCRMLSSold_Residential.csv"
OUTPUT_CSV = "week6_market_metrics.csv"
KEY_METRICS_CSV = "week6_key_metrics.csv"
SAMPLE_OUTPUT_CSV = "week6_sample_output.csv"


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)

    for col in ["OriginalListPrice", "ClosePrice", "LivingArea", "DaysOnMarket"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["CloseDate", "PurchaseContractDate", "ListingContractDate"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    for col in ["OriginalListPrice", "ClosePrice", "LivingArea", "DaysOnMarket"]:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors="coerce")

    for col in ["CloseDate", "PurchaseContractDate", "ListingContractDate"]:
        if col in result.columns:
            result[col] = pd.to_datetime(result[col], errors="coerce")

    metric_columns = []

    if "OriginalListPrice" in result.columns and "ClosePrice" in result.columns:
        result["Price Ratio"] = result["ClosePrice"] / result["OriginalListPrice"]
        result["Close to Original List Ratio"] = result["ClosePrice"] / result["OriginalListPrice"]
        metric_columns.extend(["Price Ratio", "Close to Original List Ratio"])

    if "ClosePrice" in result.columns and "LivingArea" in result.columns:
        result["Price Per Sq Ft"] = result["ClosePrice"] / result["LivingArea"]
        metric_columns.append("Price Per Sq Ft")

    if "DaysOnMarket" in result.columns:
        result["Days on Market"] = result["DaysOnMarket"]
        metric_columns.append("Days on Market")

    if "CloseDate" in result.columns:
        result["Year"] = result["CloseDate"].dt.year
        result["Month"] = result["CloseDate"].dt.month
        result["YrMo"] = result["CloseDate"].dt.to_period("M").astype(str)
        metric_columns.extend(["Year", "Month", "YrMo"])

    if "PurchaseContractDate" in result.columns and "ListingContractDate" in result.columns:
        result["Listing to Contract Days"] = (
            result["PurchaseContractDate"] - result["ListingContractDate"]
        ).dt.days
        metric_columns.append("Listing to Contract Days")

    if "CloseDate" in result.columns and "PurchaseContractDate" in result.columns:
        result["Contract to Close Days"] = (
            result["CloseDate"] - result["PurchaseContractDate"]
        ).dt.days
        metric_columns.append("Contract to Close Days")

    base_columns = [
        col for col in [
            "PropertyType",
            "PropertySubType",
            "CountyOrParish",
            "MLSAreaMajor",
            "ListOfficeName",
            "BuyerOfficeName",
        ] if col in result.columns
    ]
    core_columns = [col for col in ["ClosePrice", "OriginalListPrice", "LivingArea", "DaysOnMarket", "CloseDate"] if col in result.columns]
    metric_cols = [col for col in metric_columns if col in result.columns]

    key_metrics = result[base_columns + core_columns + metric_cols].copy()
    return key_metrics


def build_segment_summary(metrics_df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    available_cols = [col for col in group_cols if col in metrics_df.columns]
    if not available_cols:
        return pd.DataFrame()

    summary_cols = [col for col in ["ClosePrice", "Price Ratio", "Price Per Sq Ft", "Days on Market", "Listing to Contract Days", "Contract to Close Days"] if col in metrics_df.columns]
    if not summary_cols:
        return pd.DataFrame()

    work = metrics_df[available_cols + summary_cols].copy()
    for col in available_cols:
        work[col] = work[col].fillna("Unknown")

    summary = (
        work.groupby(available_cols, dropna=False)
        .agg(
            records=("ClosePrice", "size"),
            median_close_price=("ClosePrice", "median"),
            mean_close_price=("ClosePrice", "mean"),
            median_price_ratio=("Price Ratio", "median"),
            mean_price_ratio=("Price Ratio", "mean"),
            median_price_per_sqft=("Price Per Sq Ft", "median"),
            mean_price_per_sqft=("Price Per Sq Ft", "mean"),
            median_days_on_market=("Days on Market", "median"),
            mean_days_on_market=("Days on Market", "mean"),
            median_listing_to_contract_days=("Listing to Contract Days", "median"),
            mean_listing_to_contract_days=("Listing to Contract Days", "mean"),
            median_contract_to_close_days=("Contract to Close Days", "median"),
            mean_contract_to_close_days=("Contract to Close Days", "mean"),
        )
        .reset_index()
    )

    return summary.sort_values(["records", "median_close_price"], ascending=[False, False]).reset_index(drop=True)


def main() -> None:
    root = Path(__file__).resolve().parent
    input_path = root / INPUT_CSV

    if not input_path.exists():
        raise FileNotFoundError(f"Expected input CSV not found: {input_path}")

    df = load_data(input_path)
    metrics_df = calculate_metrics(df)

    output_path = root / OUTPUT_CSV
    key_metrics_path = root / KEY_METRICS_CSV
    sample_output_path = root / SAMPLE_OUTPUT_CSV

    metrics_df.to_csv(output_path, index=False)
    metrics_df.to_csv(key_metrics_path, index=False)

    sample_output_cols = [
        "ClosePrice",
        "OriginalListPrice",
        "Price Ratio",
        "Price Per Sq Ft",
        "Days on Market",
        "Year",
        "Month",
        "YrMo",
        "Close to Original List Ratio",
        "Listing to Contract Days",
        "Contract to Close Days",
    ]
    sample_output = metrics_df[[col for col in sample_output_cols if col in metrics_df.columns]].head(10).copy()
    sample_output.to_csv(sample_output_path, index=False)

    summary_specs = [
        ("PropertyType and PropertySubType", ["PropertyType", "PropertySubType"], "week6_property_segment_summary.csv"),
        ("CountyOrParish and MLSAreaMajor", ["CountyOrParish", "MLSAreaMajor"], "week6_geography_segment_summary.csv"),
        ("ListOfficeName and BuyerOfficeName", ["ListOfficeName", "BuyerOfficeName"], "week6_office_segment_summary.csv"),
    ]

    for label, group_cols, filename in summary_specs:
        summary_df = build_segment_summary(metrics_df, group_cols)
        if summary_df.empty:
            print(f"Skipping {label} summary because required columns were not available.")
            continue
        summary_path = root / filename
        summary_df.to_csv(summary_path, index=False)
        print(f"Saved {label} summary to {summary_path.name}")

    print(f"Loaded {len(metrics_df)} rows from {input_path.name}")
    print(f"Saved full metrics frame to {output_path.name}")
    print(f"Saved key metrics frame to {key_metrics_path.name}")
    print(f"Saved sample output table to {sample_output_path.name}")
    print("\nMetric columns created:")
    for col in [
        "Price Ratio",
        "Price Per Sq Ft",
        "Days on Market",
        "Year",
        "Month",
        "YrMo",
        "Close to Original List Ratio",
        "Listing to Contract Days",
        "Contract to Close Days",
    ]:
        if col in metrics_df.columns:
            print(f"- {col}")

    print("\nSample output table (first 10 rows):")
    print(sample_output.to_string(index=False))


if __name__ == "__main__":
    main()
