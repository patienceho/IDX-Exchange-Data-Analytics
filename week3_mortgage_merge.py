import pandas as pd

# Step 1 – Fetch the mortgage rate data from FRED
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url, parse_dates=['observation_date'])
mortgage.columns = ['date', 'rate_30yr_fixed']

# Step 2 – Resample weekly rates to monthly averages
mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = (
 mortgage.groupby('year_month')['rate_30yr_fixed']
 .mean()
 .reset_index()
)

# Step 3 – Create a matching year_month key on the MLS datasets
sold = pd.read_csv('week1_CombinedCRMLSSold.csv')
listings = pd.read_csv('week1_CombinedCRMLSListing.csv')
sold['year_month'] = pd.to_datetime(sold['CloseDate']).dt.to_period('M')
listings['year_month'] = pd.to_datetime(
 listings['ListingContractDate']
).dt.to_period('M')

# Step 4 – Merge
sold_with_rates = sold.merge(mortgage_monthly, on='year_month', how='left')
listings_with_rates = listings.merge(mortgage_monthly, on='year_month', how='left')

# Step 5 – Validate the merge
# Check for any unmatched rows (rate should not be null)
print(sold_with_rates['rate_30yr_fixed'].isnull().sum())
print(listings_with_rates['rate_30yr_fixed'].isnull().sum())

if sold_with_rates['rate_30yr_fixed'].isnull().sum() > 0 or listings_with_rates['rate_30yr_fixed'].isnull().sum() > 0:
    raise ValueError('Merge validation failed: null rate values found after merge')
else:
    print('Validation passed: no null rate values found after merge')
