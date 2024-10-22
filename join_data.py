import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
import re

# Function to convert phone numbers to numeric format
def convert_phone_to_numeric(df):
    # Convert the 'phone' column to string, remove any single quotes, and convert it to numeric 
    df['phone'] = pd.to_numeric(df['phone'].astype(str).str.replace('\'', '', regex=False), errors='coerce')
    return df

# Function to clean rows in a given column, removing unwanted characters and handling 'name' specifically
def clean_column(df, attribute):
    # Remove rows where the specified column contains unwanted characters like '\u' or '\x' (Unicode or hex characters)
    df = df[~df[attribute].str.contains(r'\\u|\\x', na=False)]
    
    # Function to process and clean attribute values, splitting at '|' if more than one exists
    def process_attribute(attribute):
        if attribute.count('|') > 1:
            return attribute.split('|')[0].strip()  # Keep only the part before the first "|"
        return attribute.strip()  # Keep full value if only one "|"

    # Apply the cleaning logic to the specified column
    df.loc[:, attribute] = df[attribute].apply(process_attribute)
    return df


# Load datasets
google = pd.read_csv('google_dataset.csv', on_bad_lines='skip', low_memory=False)
fb = pd.read_csv('facebook_dataset.csv', on_bad_lines='skip', low_memory=False)
website = pd.read_csv('website_dataset.csv', sep=';', on_bad_lines='skip', low_memory=False)
#google.to_excel('google_data_excel_all.xlsx', index=False) 
#print(google.head())
#print(google.info())

# Clean Facebook and website datasets by encoding text to escape Unicode characters
fb = fb.map(lambda x: x.encode('unicode_escape').decode('utf-8') if isinstance(x, str) else x)
#fb.to_excel('facebook_data_excel.xlsx', index=False) 
#print(fb.head())
#print(fb.info())

website = website.map(lambda x: x.encode('unicode_escape').decode('utf-8') if isinstance(x, str) else x)
#website.to_excel('website_data_excel_all.xlsx', index=False) 
# print(website.head())
# print(website.info())

# Convert phone columns to numeric format across all datasets
google = convert_phone_to_numeric(google)
fb = convert_phone_to_numeric(fb)
website = convert_phone_to_numeric(website)

# Standardize column names across datasets and create copies explicitly
google_subset = google[['phone', 'category', 'name', 'city', 'country_name', 'region_name']].copy()
google_subset.columns = ['phone', 'category', 'name', 'city', 'country', 'region']

fb_subset = fb[['phone', 'categories', 'name', 'city', 'country_name']].copy()
fb_subset.columns = ['phone', 'category', 'name', 'city', 'country']

website_subset = website[['phone', 's_category', 'legal_name', 'main_city', 'main_country', 'main_region']].copy()
website_subset.columns = ['phone', 'category', 'name', 'city', 'country', 'region']

# Remove rows where phone numbers are missing 
google_subset = google_subset.dropna(subset=['phone']).copy()
fb_subset = fb_subset.dropna(subset=['phone']).copy()
website_subset = website_subset.dropna(subset=['phone']).copy()

# Standardize the case for city and country columns to lowercase for consistency
google_subset['city'] = google_subset['city'].str.lower()
google_subset['country'] = google_subset['country'].str.lower()
google_subset['region'] = google_subset['region'].str.lower()

fb_subset['city'] = fb_subset['city'].str.lower()
fb_subset['country'] = fb_subset['country'].str.lower()

website_subset['city'] = website_subset['city'].str.lower()
website_subset['country'] = website_subset['country'].str.lower()
website_subset['region'] = website_subset['region'].str.lower()

# Fill empty cells for all other columns (except 'phone') with 'NULL'
columns_to_fill_google = [col for col in google_subset.columns if col != 'phone']
google_subset.loc[:, columns_to_fill_google] = google_subset[columns_to_fill_google].fillna('NULL')

columns_to_fill_fb = [col for col in fb_subset.columns if col != 'phone']
fb_subset.loc[:, columns_to_fill_fb] = fb_subset[columns_to_fill_fb].fillna('NULL')

columns_to_fill_website = [col for col in website_subset.columns if col != 'phone']
website_subset.loc[:, columns_to_fill_website] = website_subset[columns_to_fill_website].fillna('NULL')

# Eliminate duplicates based on the 'phone' column (create a copy)
google_subset = google_subset.drop_duplicates(subset=['phone']).copy()
fb_subset = fb_subset.drop_duplicates(subset=['phone']).copy()
website_subset = website_subset.drop_duplicates(subset=['phone']).copy()

# Apply the clean_column function to the subset dataframes
attributes =['name','category','city','country', 'region']
for atr in attributes:
    google_subset = clean_column(google_subset, atr)
    if atr != 'region':
        fb_subset = clean_column(fb_subset, atr)
    website_subset = clean_column(website_subset, atr)
    
# Save the subsets to Excel
google_subset.to_excel('google_data_excel.xlsx', index=False)
fb_subset = fb_subset.apply(lambda x: x.encode('unicode_escape').decode('utf-8') if isinstance(x, str) else x)
fb_subset.to_excel('facebook_data_excel.xlsx', index=False)
website_subset = website_subset.apply(lambda x: x.encode('unicode_escape').decode('utf-8') if isinstance(x, str) else x)
website_subset.to_excel('website_data_excel.xlsx', index=False)

# Merge the datasets on 'phone' column using outer join
merged_df = pd.merge(website_subset, google_subset, on='phone', how='outer', suffixes=('_website', '_google'))
merged_df = pd.merge(merged_df, fb_subset, on='phone', how='outer', suffixes=('', '_fb'))

# Fill missing values for common columns, prioritize website -> google -> fb
merged_df['name'] = merged_df['name_website'].fillna(merged_df['name_google']).fillna(merged_df['name'])
merged_df['category'] = merged_df['category_website'].fillna(merged_df['category_google']).fillna(merged_df['category'])
merged_df['city'] = merged_df['city_website'].fillna(merged_df['city_google']).fillna(merged_df['city'])
merged_df['country'] = merged_df['country_website'].fillna(merged_df['country_google']).fillna(merged_df['country'])
merged_df['region'] = merged_df['region_website'].fillna(merged_df['region_google']).fillna('NULL')


# Drop unnecessary columns after merging
merged_df.drop(columns=['name_website', 'name_google', 'name_fb', 'category_website', 'category_google', 'category_fb',
                        'city_website', 'city_google', 'city_fb', 'country_website', 'country_google', 'country_fb', 'region_google', 'region_website'],
               inplace=True, errors='ignore')

# Filter out rows where the 'name' is NULL or contains the string "NULL"
merged_df = merged_df[merged_df['name'].notna() & (merged_df['name'] != 'NULL')]


# Save the final merged and cleaned dataset to an Excel file
merged_df.to_excel('dataset_4.xlsx', index=False)

# Load the cleaned dataset from Excel
df = pd.read_excel('dataset_4.xlsx')

# Descriptive statistics: Get an overview of the data
print(df.describe())
print(df.info())

# Frequency Analysis: Top categories
category_counts = df['category'].value_counts()
print("Top Categories:")
print(category_counts.head(10))  # Show top 10 categories

# Visualize the top categories
plt.figure(figsize=(12, 6))  # Increase figure size
category_counts.head(10).plot(kind='bar', color='skyblue')
plt.title('Top 10 Business Categories')
plt.xlabel('Category')
plt.ylabel('Count')
plt.xticks(rotation=45, ha='right')  # Rotate labels
plt.subplots_adjust(top=0.85, bottom=0.2, left=0.1, right=0.9)
plt.tight_layout()  
plt.show()

# Category Distribution by Country
category_by_country = df.groupby(['country', 'category']).size().unstack(fill_value=0)
print(category_by_country.head(10))  #

# Visualize Category Distribution by Country (Top 5 countries)
top_countries = df['country'].value_counts().head(5).index
plt.figure(figsize=(12, 8))  # Increase figure size
category_by_country.loc[top_countries].plot(kind='bar', stacked=True)
plt.title('Category Distribution by Top 5 Countries')
plt.xlabel('Country')
plt.ylabel('Count')
plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation=0)  # Rotate labels if needed
plt.subplots_adjust(top=0.85, bottom=0.2, left=0.1, right=0.9)
#plt.tight_layout()  
plt.show()

# Missing data analysis
missing_values = df.isnull().sum()
print("Missing values in each column:")
print(missing_values)

# Filter rows with missing 'category'
missing_category_df = df[df['category'].isnull()]
print(f"Rows with missing categories: {len(missing_category_df)}")

# Filter rows with missing 'phone' or 'name'
missing_phone_name = df[df['phone'].isnull() | df['name'].isnull()]
print(f"Rows with missing phone or name: {len(missing_phone_name)}")
