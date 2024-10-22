# Challenge3
Script Workflow
1. Load Datasets
The datasets are loaded using pandas:
-	Google: google_dataset.csv
-	Facebook: facebook_dataset.csv
-	Website: website_dataset.csv (semicolon-separated)
The files are processed with on_bad_lines='skip' to handle any erroneous lines in the data.

3. Clean Phone Numbers
Phone numbers in each dataset are converted to numeric format:
df['phone'] = pd.to_numeric(df['phone'].astype(str).str.replace("'", '', regex=False), errors='coerce')

5. Text Field Cleaning
The script removes any special characters like \u or \x in the name, category, city, country, and region fields.
It also processes attributes that contain multiple values separated by | and keeps only the first part when multiple values exist.

7. Standardize Column Names
The script standardizes the column names across the three datasets to ensure consistency:
-	Google: ['phone', 'category', 'name', 'city', 'country', 'region']
-	Facebook: ['phone', 'category', 'name', 'city', 'country']
-	Website: ['phone', 'category', 'name', 'city', 'country', 'region']

9. Data Cleaning and Deduplication
-	Rows with missing phone numbers are removed.
-	Text fields (city, country, region) are converted to lowercase for uniformity.
-	Empty cells in other columns are filled with NULL.
-	Duplicate rows based on the phone column are eliminated.

11. Merging Datasets
The datasets are merged using an outer join on the phone column. Missing values in common columns are filled with a prioritization order: website -> google -> facebook.
merged_df['name'] = merged_df['name_website'].fillna(merged_df['name_google']).fillna(merged_df['name'])

13. Final Data Cleaning
-	Unnecessary columns after the merge are dropped.
-	Rows with missing or invalid name values are filtered out.

15. Save Output
The cleaned and merged dataset is saved into an Excel file:
merged_df.to_excel('merged_cleaned_data_single_columns.xlsx', index=False)

16. Data Analysis and Visualization
- Dataset Overview: Descriptive statistics and data type information are generated.
- The top 10 business categories are identified using frequency analysis, followed by a bar chart visualization.
- The distribution of business categories by country is explored through grouping and visualized as a stacked bar chart for the top 5 countries. 
- Missing data is analyzed, highlighting rows with null values in key columns like category, phone, and name.  

Observations:
- The phone column is used as the common key across the datasets to join them. It is a reliable, unique identifier that ensures consistency between the records from the Google, Facebook, and website datasets.
- In cases of data conflicts, the priority order is as follows: Website data takes precedence over Google data.
Google data takes precedence over Facebook data. This prioritization assumes that the website dataset contains more authoritative and up-to-date information, followed by Google, and then Facebook.Facebook data is considered the least reliable, as social profiles may be less formal or up-to-date.
- When very similar data is encountered, the strategy is to fill missing values in the order of website -> google -> facebook. This ensures that the most complete and reliable information is preserved. For instance, if name, category, city, or country are missing in one dataset but available in another, the value from the prioritized dataset is retained.
- The final dataset retains information that is essential for further analysis, including: phone, name, category, city, country, region. These fields are important for understanding the geographical distribution, categorization, and identification of entities.
- The decision not to include the address field in the final dataset was based on the high level of inconsistency in the data. During the data exploration phase, it became clear that the address field often contained variations in formatting, abbreviations or incomplete information.
