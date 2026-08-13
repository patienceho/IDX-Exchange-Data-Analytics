from pathlib import Path

import pandas as pd


# Week 7 - Outlier Detection and Data Quality
folder = Path(__file__).resolve().parent
sold = pd.read_csv(folder / "week6_market_metrics.csv", low_memory=False)

columns = ["ClosePrice", "LivingArea", "DaysOnMarket"]
outlier_flags = []

# Business-rule flag from the internship handbook
sold["invalid_data_flag"] = (
    (sold["ClosePrice"] <= 0)
    | (sold["LivingArea"] <= 0)
    | (sold["DaysOnMarket"] < 0)
)

print("Before filtering:")
print(f"Rows: {len(sold):,}")
print(sold[columns].median())

# Calculate the IQR and create one outlier flag for each required field
for column in columns:
    q1 = sold[column].quantile(0.25)
    q3 = sold[column].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    flag = f"{column}_outlier_flag"
    sold[flag] = (sold[column] < lower) | (sold[column] > upper)
    outlier_flags.append(flag)

    print(
        f"{column}: {sold[flag].sum():,} outliers "
        f"(lower={lower:,.2f}, upper={upper:,.2f})"
    )

# Keep the complete dataset with flags
sold["any_outlier_flag"] = sold[outlier_flags].any(axis=1)
sold.to_csv(folder / "week7_outlier_flagged.csv", index=False)

# Create a separate clean dataset without outliers or invalid values
sold_filtered = sold[
    (~sold["any_outlier_flag"]) & (~sold["invalid_data_flag"])
].copy()
sold_filtered.to_csv(folder / "week7_clean_filtered.csv", index=False)

# Save and print the required before-and-after comparison
comparison = pd.DataFrame(
    {
        "dataset": ["Before filtering", "After filtering"],
        "row_count": [len(sold), len(sold_filtered)],
        "median_close_price": [
            sold["ClosePrice"].median(),
            sold_filtered["ClosePrice"].median(),
        ],
        "median_living_area": [
            sold["LivingArea"].median(),
            sold_filtered["LivingArea"].median(),
        ],
        "median_days_on_market": [
            sold["DaysOnMarket"].median(),
            sold_filtered["DaysOnMarket"].median(),
        ],
    }
)

comparison.to_csv(folder / "week7_before_after_comparison.csv", index=False)

print("\nBefore-and-after comparison:")
print(comparison.to_string(index=False))
print("\nSaved week7_outlier_flagged.csv")
print("Saved week7_clean_filtered.csv")
print("Saved week7_before_after_comparison.csv")
