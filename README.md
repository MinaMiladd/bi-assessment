# Data Analytics Engineering Assessment: Sales & Forecast Optimization

## 📋 Project Summary
An end-to-end data analytics solutions architecture engineered to transform raw, unoptimized transactional data into an enterprise-grade Relational Star Schema. The final deliverable features an automated Python ETL pipeline paired with a high-performance, single-page Power BI executive dashboard addressing core sales performance and target variances.

---

## ⚙️ Task 1: Python ETL Pipeline & Data Quality Remediation
A programmatic data cleaning pipeline was built via `pandas` to isolate and rectify extensive data anomalies present within the initial raw inputs.

### 🔍 Data Exploration Diagnostics & Discoveries:
* **Severe Record Duplication:** Identified **218,008 duplicate rows** out of 298,246 total entries (an extreme **73% duplication rate**).
* **Structural Column Anomaly:** The field `Color` was structurally redundant, completely replicating the contents of the `Subcategory` text string.
* **Critical Demographic Gaps:** Discovered a **90% null rate** across customer profiling metrics: `Name`, `Education`, and `Occupation`.
* **Data Type Corruption:** The transactional transaction metric `OrderDate` was stored natively as a raw text string.

### 🛠️ Data Transformation Actions:
* **Systematic Deduplication:** Eliminated all 218,008 duplicate entries, compressing the dataset to a baseline of **80,238 unique sales rows**.
* **Normalization & Redundancy Removal:** Completely stripped the unmapped `Color` column to respect relational constraints.
* **Demographic Imputation:** Imputed missing values across customer profiling attributes with the standard string label `"Unknown"`.
* **Temporal Casting:** Explicitly parsed and cast the text-based order data into a synchronized `datetime64` object.

---

## 📐 Task 2: Data Modeling & Granularity Architecture
The defining engineering constraint of this project involves resolving a stark mismatch in data granularity between the historical sales data and the business forecast targets:
* **Highly Granular:** `Fact_Sales` records metrics on a **Daily / Line-Item / Product / Customer** level.
* **Coarsely Granular:** `Fact_Forecast` provides metrics strictly on an **Annual / Brand / Country** level.

### 🏗️ The Shared Bridge Dimension Solution
To bypass performance-degrading many-to-many relationships and prevent unpredictable filtering errors inside Power BI, a **Shared Bridge Dimension** architecture was deployed.
* **Dimensional Separation:** Extracted dedicated lookup bridge tables for **`Dim_Brand`** and **`Dim_Country`** using Python.
* **1-to-Many Relationships ($1 \rightarrow *$):** These bridge tables sit cleanly between the high-level `Fact_Forecast` target table and the highly detailed dimension tables (`Dim_Product` and `Dim_Customer`).
* **Date Dimension Integration:** Generated a custom DAX calendar table (**`Dim_Date`**). A controlled 1-to-Many relationship connects `Dim_Date[Date]` $\rightarrow$ `Fact_Sales[OrderDate]`, while a calendar link connects `Dim_Date[Year]` $\rightarrow$ `Fact_Forecast[Year]` with a Single Cross-Filter direction setting (*Dim_Date filters Fact_Forecast*).

---

## 📊 Task 3: Optimized Analytical Calculations (DAX)
To maintain quick processing speeds, all analytical business requirements are executed using dynamic DAX measures:
* **Total Sales:** `Total Sales = SUMX(Fact_Sales, Fact_Sales[Quantity] * Fact_Sales[Net Price])`
* **Sales 2008:** `Sales 2008 = CALCULATE([Total Sales], Dim_Date[Year] = 2008)`
* **Sales 2009:** `Sales 2009 = CALCULATE([Total Sales], Dim_Date[Year] = 2009)`
* **YoY Change %:** `Sales YoY Change % = DIVIDE([Sales 2009] - [Sales 2008], [Sales 2008], 0)`
* **Total Forecast:** `Total Forecast = SUM(Fact_Forecast[Forecast])`
* **Forecast Variance:** `Forecast Variance = [Sales 2009] - [Total Forecast]`
* **Product Share %:** `Product Share % = DIVIDE([Total Sales], CALCULATE([Total Sales], ALL(Dim_Product)), 0)`
* **Customer Sales Rank:** `Customer Sales Rank = RANKX(ALL(Dim_Customer), [Total Sales], , DESC)`

---

## 🎨 Task 4: Interactive Executive Dashboard
The visual presentation layout delivers maximum insights on a single screen using a professional corporate aesthetic:
* **Top-Down KPI Panel:** Provides immediate visual access to total sales scale, year-over-year percentage trends, and overall forecast variations.
* **Temporal Tracking with Drill-Down Integration:** The main sales trend line chart utilizes a clean visual hierarchy (`Year` $\rightarrow$ `Quarter` $\rightarrow$ `Month`).
* **Side-by-Side Target Comparison:** A clustered vertical bar visual plots 2009 actual revenues directly next to forecast targets by individual brand.
* **Dynamic Top Consumer Evaluation:** Incorporates a specialized table combined with an operational Top-1 ranking filter to isolate the highest-spending client.
* **Global Operational Filters:** Includes dedicated dropdown slicers for Country and State across the header banner.