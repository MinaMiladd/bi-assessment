

import os
import pandas as pd

def run_etl_pipeline():
    print(" Step 1: Ingesting raw unstructured data sources...")
    # Read the raw JSON datasets directly from the root working directory
    try:
        sales_raw = pd.read_json("Sales.json")
        forecast_raw = pd.read_json("forecast.json")
    except Exception as e:
        print(f" Error loading source JSON files: {e}")
        return

    print("\n Step 2: Running Data Exploration Diagnostics...")
    # Diagnostic 1: Identify high-volume row duplication
    total_rows = len(sales_raw)
    duplicate_count = sales_raw.duplicated().sum()
    print(f"   [INFO] Total Raw Records: {total_rows}")
    print(f"   [INFO] Exact Duplicate Rows Identified: {duplicate_count} ({round((duplicate_count/total_rows)*100, 2)}%)")

    # Diagnostic 2: Locate missing data (Nulls)
    null_counts = sales_raw.isnull().sum()
    print("   [INFO] Missing values per field detected:")
    for col, count in null_counts.items():
        if count > 0:
            print(f"          - Column '{col}': {count} null records")

    print("\n Step 3: Executing Data Transformation & Quality Fixes...")
    # 1. Deduplication
    sales_clean = sales_raw.drop_duplicates().copy()
    
    # 2. Attribute Mapping Fix (Dropping redundant Color/Subcategory column)
    if 'Color' in sales_clean.columns:
        sales_clean = sales_clean.drop(columns=['Color'])
        print("   [FIX] Removed 'Color' column due to exact string replication of 'Subcategory'.")

    # 3. Demographic Imputation
    demographic_fields = ['Name', 'Education', 'Occupation']
    for field in demographic_fields:
        sales_clean[field] = sales_clean[field].fillna('Unknown')
    print("   [FIX] Imputed missing customer demographic records with 'Unknown'.")

    # 4. Data Type Normalization
    sales_clean['OrderDate'] = pd.to_datetime(sales_clean['OrderDate'], format='%m/%d/%Y')
    print("   [FIX] Normalized 'OrderDate' into explicit datetime64 object format.")

    print("\n Step 4: Normalizing Flat Schema into Relational Tables...")
    # Extract Dimension Tables with guaranteed Primary Key uniqueness
    dim_product = sales_clean[['ProductKey', 'Product Name', 'Brand', 'Subcategory', 'Category']].drop_duplicates(subset=['ProductKey'])
    dim_customer = sales_clean[['CustomerKey', 'Customer Code', 'Name', 'Education', 'Occupation', 'Continent', 'City', 'State', 'CountryRegion']].drop_duplicates(subset=['CustomerKey'])
    
    # Extract Fact Table matching data warehouse standards
    fact_sales = sales_clean[['ProductKey', 'CustomerKey', 'OrderDate', 'Quantity', 'Net Price']]

    print("\n Step 5: Extracting Shared Granularity Bridge Tables...")
    # Isolate unique attributes to safely bridge the Sales and Forecast granularity gap
    unique_brands = pd.concat([dim_product['Brand'], forecast_raw['Brand']]).unique()
    dim_brand = pd.DataFrame({'Brand': unique_brands})

    unique_countries = pd.concat([dim_customer['CountryRegion'], forecast_raw['CountryRegion']]).unique()
    dim_country = pd.DataFrame({'CountryRegion': unique_countries})

    print("\n Step 6: Writing relational tables to structured storage...")
    os.makedirs('data', exist_ok=True)
    
    dim_product.to_csv('data/Dim_Product.csv', index=False)
    dim_customer.to_csv('data/Dim_Customer.csv', index=False)
    dim_brand.to_csv('data/Dim_Brand.csv', index=False)
    dim_country.to_csv('data/Dim_Country.csv', index=False)
    fact_sales.to_csv('data/Fact_Sales.csv', index=False)
    forecast_raw.to_csv('data/Fact_Forecast.csv', index=False)

    print("\n ETL Pipeline execution completed successfully!")
    print(f"    Final Dim_Product Row Count:  {len(dim_product)}")
    print(f"    Final Dim_Customer Row Count: {len(dim_customer)}")
    print(f"    Final Fact_Sales Row Count:   {len(fact_sales)}")

if __name__ == "__main__":
    run_etl_pipeline()