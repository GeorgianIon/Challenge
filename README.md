# Challenge3
Script Workflow
1. Load Datasets
The datasets are loaded using pandas:
•	Google: google_dataset.csv
•	Facebook: facebook_dataset.csv
•	Website: website_dataset.csv (semicolon-separated)
The files are processed with on_bad_lines='skip' to handle any erroneous lines in the data.

3. Clean Phone Numbers
Phone numbers in each dataset are converted to numeric format:
df['phone'] = pd.to_numeric(df['phone'].astype(str).str.replace("'", '', regex=False), errors='coerce')

5. Text Field Cleaning
The script removes any special characters like \u or \x in the name, category, city, country, and region fields.
It also processes attributes that contain multiple values separated by | and keeps only the first part when multiple values exist.

7. Standardize Column Names
The script standardizes the column names across the three datasets to ensure consistency:
•	Google: ['phone', 'category', 'name', 'city', 'country', 'region']
•	Facebook: ['phone', 'category', 'name', 'city', 'country']
•	Website: ['phone', 'category', 'name', 'city', 'country', 'region']

9. Data Cleaning and Deduplication
•	Rows with missing phone numbers are removed.
•	Text fields (city, country, region) are converted to lowercase for uniformity.
•	Empty cells in other columns are filled with NULL.
•	Duplicate rows based on the phone column are eliminated.

11. Merging Datasets
The datasets are merged using an outer join on the phone column. Missing values in common columns are filled with a prioritization order: website -> google -> facebook.
merged_df['name'] = merged_df['name_website'].fillna(merged_df['name_google']).fillna(merged_df['name'])

13. Final Data Cleaning
•	Unnecessary columns after the merge are dropped.
•	Rows with missing or invalid name values are filtered out.

15. Save Output
The cleaned and merged dataset is saved into an Excel file:
merged_df.to_excel('merged_cleaned_data_single_columns.xlsx', index=False)

