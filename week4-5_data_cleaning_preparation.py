import pandas as pd
import os

# File paths
base_dir = r'c:\Users\patie\OneDrive - Indiana University\Desktop\IDX Exchange\File Data'

# Load week3 merged datasets
sold = pd.read_csv(os.path.join(base_dir, 'week3_CombinedCRMLSSold_with_rates.csv'))
listings = pd.read_csv(os.path.join(base_dir, 'week3_CombinedCRMLSListing_with_rates.csv'))

# Convert date fields to datetime format
print('---|DATETIME FORMAT|---')
listing_columns = [
    'CloseDate',
    'PurchaseContractDate',
    'ListingContractDate',
    'ContractStatusChangeDate'
]

for col in listing_columns:
    if col in sold.columns:
        sold[col] = pd.to_datetime(sold[col], errors='coerce')
    if col in listings.columns:
        listings[col] = pd.to_datetime(listings[col], errors='coerce')

print('---|REMOVE UNNECESSARY COLUMNS|---')
# Remove clearly redundant or unnecessary columns
columns_to_drop = [
    'BuyerAgentEmail',
    'ListAgentEmail',
    'BuyerAgentAOR',
    'ListAgentAOR',
    'OriginatingSystemName',
    'OriginatingSystemSubName',
    'BuyerAgencyCompensationType'
]

for col in columns_to_drop:
    if col in sold.columns:
        sold = sold.drop(columns=[col])
    if col in listings.columns:
        listings = listings.drop(columns=[col])

print('---|HANDLE MISSING VALUES|---')
# Handle missing values appropriately
for df in [sold, listings]:
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(0)
        else:
            df[col] = df[col].fillna('')

print('---|ENSURE NUMERIC FIELDS ARE PROPERLY TYPED|---')
# Coerce obvious numeric columns to numeric dtype
for df in [sold, listings]:
    for col in df.columns:
        if col.lower().endswith(('price', 'amount', 'rate', 'size', 'area', 'count', 'number', 'year')):
            df[col] = pd.to_numeric(df[col], errors='coerce')

print('---|REMOVE OR FLAG INVALID NUMERIC VALUES|---')
# Flag or remove invalid numeric values based on domain rules
for df in [sold, listings]:
    if 'ClosePrice' in df.columns:
        df['invalid_close_price'] = df['ClosePrice'] <= 0
        df.loc[df['invalid_close_price'], 'ClosePrice'] = pd.NA
    if 'LivingArea' in df.columns:
        df['invalid_living_area'] = df['LivingArea'] <= 0
        df.loc[df['invalid_living_area'], 'LivingArea'] = pd.NA
    if 'DaysOnMarket' in df.columns:
        df['invalid_days_on_market'] = df['DaysOnMarket'] < 0
        df.loc[df['invalid_days_on_market'], 'DaysOnMarket'] = pd.NA
    if 'Bedrooms' in df.columns:
        df['invalid_bedrooms'] = df['Bedrooms'] < 0
        df.loc[df['invalid_bedrooms'], 'Bedrooms'] = pd.NA
    if 'Bathrooms' in df.columns:
        df['invalid_bathrooms'] = df['Bathrooms'] < 0
        df.loc[df['invalid_bathrooms'], 'Bathrooms'] = pd.NA

print('---|VALIDATE DATE FIELD ORDER|---')
# Create boolean flags for invalid date ordering logic
for df in [sold, listings]:
    if 'ListingContractDate' in df.columns and 'CloseDate' in df.columns:
        df['listing_after_close_flag'] = (
            df['ListingContractDate'].notna() & df['CloseDate'].notna() &
            (df['ListingContractDate'] > df['CloseDate'])
        )
    if 'PurchaseContractDate' in df.columns and 'CloseDate' in df.columns:
        df['purchase_after_close_flag'] = (
            df['PurchaseContractDate'].notna() & df['CloseDate'].notna() &
            (df['PurchaseContractDate'] > df['CloseDate'])
        )
    if 'ListingContractDate' in df.columns and 'PurchaseContractDate' in df.columns and 'CloseDate' in df.columns:
        df['negative_timeline_flag'] = (
            (df['ListingContractDate'].notna() & df['PurchaseContractDate'].notna() & df['CloseDate'].notna()) &
            ((df['ListingContractDate'] > df['PurchaseContractDate']) | (df['PurchaseContractDate'] > df['CloseDate']))
        )

# Example: preview columns and row counts
print('Sold rows:', len(sold))
print('Listings rows:', len(listings))
print('Sold columns:', list(sold.columns)[:10])
print('Listings columns:', list(listings.columns)[:10])
