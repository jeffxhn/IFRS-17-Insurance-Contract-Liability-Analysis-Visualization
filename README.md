# IFRS 17 Insurance Contract Liability Analysis & Visualization

## Project Overview

This project simulates a realistic actuarial reporting workflow under IFRS 17. It models a life insurance portfolio consisting of 100 contracts across three product lines (Term Life, Whole Life, and Annuity), tracks their contractual service margin (CSM) over 8 quarterly reporting periods (2024 Q1 – 2025 Q4), and presents the results through an interactive Power BI dashboard.

The goal is to demonstrate hands-on proficiency in:
- IFRS 17 core concepts (CSM, LRC, insurance service result, loss components)
- Data generation using Python (pandas, numpy)
- Data storage and querying with MySQL
- Data modeling and visualization with Power BI (DAX, drill-through, waterfall chart)
- Building a professional three-page actuarial report dashboard

## Data Summary

| Item | Detail |
|------|--------|
| Total Records | 800 rows (100 contracts × 8 quarters) |
| Contract IDs | CON00001 – CON00100 |
| Product Types | Term Life (50%), Whole Life (30%), Annuity (20%) |
| Reporting Period | 2024 Q1 – 2025 Q4 |
| Loss-making Contracts | 6 out of 100 |

## Key IFRS 17 Metrics

| Metric | Value | Definition |
|--------|-------|------------|
| Total CSM | 15.03M | Contractual Service Margin (closing balance) |
| Total LRC | 42.51M | Liability for Remaining Coverage (CSM + FCF + RA) |
| Insurance Service Result | 340K | Insurance Revenue – Insurance Service Expense |
| Insurance Net Result | 119.98K | Insurance Service Result – Insurance Finance Expense |
| CSM Release Rate | 2.01% / quarter | CSM amortization rate (≈8% annualized) |
| Loss Contracts | 6 | Contracts with loss_component > 0 |

## Data Dictionary

| Field Name | Description |
|------------|-------------|
| `contract_id` | Unique contract identifier |
| `report_date` | Reporting quarter end date |
| `product_type` | Product line (Term Life / Whole Life / Annuity) |
| `issue_year` | Year the contract was issued |
| `cohort` | Issue year and quarter |
| `fulfilment_cashflows` | Fulfilment cash flows (FCF) |
| `risk_adjustment` | Risk adjustment (RA) |
| `csm_opening` | CSM at start of period |
| `csm_release` | CSM released to profit in current period |
| `csm_unlocking` | Experience unlocking adjustments |
| `csm_interest_accretion` | Interest accretion on CSM |
| `csm_new_business` | CSM added from new business |
| `csm_closing` | CSM at end of period |
| `loss_component` | Loss component (if any) |
| `discount_rate` | Discount rate used for calculations |
| `insurance_revenue` | Insurance service revenue |
| `insurance_service_expense` | Insurance service expense |
| `insurance_finance_expense` | Insurance finance expense |

## Dashboard Pages

### Page 1 – Executive Summary
- KPI cards: Total CSM, Total LRC, Insurance Service Result, Insurance Net Result, Loss Contracts
- Slicers: Product Type, Issue Year
- Line chart: CSM trend by quarter
- Donut chart: CSM distribution by product type

### Page 2 – Profit & Loss Analysis
- KPI cards: Total Revenue, Total Service Expense, Insurance Net Result
- Column chart: Insurance Service Result by quarter
- Bar chart: Insurance Net Result by product type
- Table: Loss contract details (contract_id, report_date, product_type, loss_component)

### Page 3 – CSM Roll-forward Analysis
- KPI cards: Opening CSM, Closing CSM, CSM Release Rate
- Waterfall chart: CSM roll-forward (Opening → Release → Unlocking → Interest → New Business → Closing)
- Line chart: CSM Release Rate by quarter
- Bar chart: CSM Release Rate by product type

### Drill-through
- From Page 1 donut chart → Page 2 (filtered by product type)

## Technology Stack

| Component | Tool |
|-----------|------|
| Data Generation | Python 3.x (pandas, numpy) |
| Data Storage | MySQL 8.0 |
| Data Connection | ODBC |
| Data Visualization | Power BI Desktop |
| Version Control | GitHub |

## Key DAX Measures & SQL Queries

```dax
-- ===== DATE TABLE =====
Dim_Date = 
ADDCOLUMNS(
    CALENDAR(DATE(2024,1,1), DATE(2025,12,31)),
    "Year", YEAR([Date]),
    "Quarter", "Q" & QUARTER([Date]),
    "Quarter_Year", "Q" & QUARTER([Date]) & "-" & YEAR([Date]),
    "Month", FORMAT([Date], "MMM"),
    "Month_Num", MONTH([Date]),
    "YearMonth", FORMAT([Date], "YYYY-MM")
)

-- ===== CORE MEASURES =====
Total CSM = SUM(fact_contract_liability[csm_closing])

Total Revenue = SUM(fact_contract_liability[insurance_revenue])

Total Service Expense = SUM(fact_contract_liability[insurance_service_expense])

Insurance Service Result = [Total Revenue] - [Total Service Expense]

Total Finance Expense = SUM(fact_contract_liability[insurance_finance_expense])

Insurance Net Result = [Insurance Service Result] - [Total Finance Expense]

Total FCF = SUM(fact_contract_liability[fulfilment_cashflows])

Total LRC = [Total CSM] + [Total FCF] + SUM(fact_contract_liability[risk_adjustment])

CSM Release Rate = 
DIVIDE(
    SUM(fact_contract_liability[csm_release]),
    SUM(fact_contract_liability[csm_opening]),
    0
)

Loss Contracts = 
CALCULATE(
    DISTINCTCOUNT(fact_contract_liability[contract_id]),
    fact_contract_liability[loss_component] > 0
)

Opening CSM = SUM(fact_contract_liability[csm_opening])
CSM Release = SUM(fact_contract_liability[csm_release])
Experience Unlocking = SUM(fact_contract_liability[csm_unlocking])
Interest Accretion = SUM(fact_contract_liability[csm_interest_accretion])
New Business CSM = SUM(fact_contract_liability[csm_new_business])
Closing CSM = SUM(fact_contract_liability[csm_closing])

-- ===== CSM WATERFALL TABLE =====
CSM_Waterfall = 
UNION(
    ROW("Step", "Opening CSM", "Value", [Opening CSM]),
    ROW("Step", "- CSM Release", "Value", -[CSM Release]),
    ROW("Step", "+ Experience Unlocking", "Value", [Experience Unlocking]),
    ROW("Step", "+ Interest Accretion", "Value", [Interest Accretion]),
    ROW("Step", "+ New Business", "Value", [New Business CSM]),
    ROW("Step", "Closing CSM", "Value", [Closing CSM])
)

-- ===== KEY SQL QUERIES =====
-- Create database and table
CREATE DATABASE IF NOT EXISTS ifrs17_project;
USE ifrs17_project;

CREATE TABLE fact_contract_liability (
    id INT AUTO_INCREMENT PRIMARY KEY,
    contract_id VARCHAR(20),
    report_date DATE,
    product_type VARCHAR(30),
    issue_year INT,
    cohort VARCHAR(10),
    fulfilment_cashflows DECIMAL(15,2),
    risk_adjustment DECIMAL(15,2),
    csm_opening DECIMAL(15,2),
    csm_release DECIMAL(15,2),
    csm_unlocking DECIMAL(15,2),
    csm_interest_accretion DECIMAL(15,2),
    csm_new_business DECIMAL(15,2),
    csm_closing DECIMAL(15,2),
    loss_component DECIMAL(15,2),
    discount_rate DECIMAL(5,4),
    insurance_revenue DECIMAL(15,2),
    insurance_service_expense DECIMAL(15,2),
    insurance_finance_expense DECIMAL(15,2)
);

-- Verify data
SELECT COUNT(*) FROM fact_contract_liability;  -- Expected: 800
SELECT COUNT(DISTINCT contract_id) FROM fact_contract_liability;  -- Expected: 100

Business Insights
CSM Release Rate of ~2% per quarter (≈8% annualized) is consistent with typical life insurance long-term profit patterns.

6 loss-making contracts were identified. They are concentrated in the Term Life product, suggesting potential pricing assumption gaps worth reviewing.

Term Life is the dominant product, contributing approximately 51% of total CSM, making it the company's primary profit driver.

Insurance Service Result is positive (340K), indicating the insurance business itself is profitable before finance costs.

How to Reproduce This Project
1. MySQL Setup
CREATE DATABASE ifrs17_project;

Import the CSV file using MySQL Workbench Import Wizard or the LOAD DATA LOCAL INFILE command.

2. Power BI Setup
Open IFRS17_Report.pbix in Power BI Desktop

The data source is configured via ODBC to localhost:3306 database ifrs17_project

You may need to update ODBC connection settings if your MySQL credentials differ

3. Python Data Generation (Optional)
pip install pandas numpy
python scripts/generate_data.py

File Structure
ifrs17_project/
├── README.md
├── IFRS17_Report.pbix
├── IFRS17_Report.pdf
├── data/
│   └── ifrs17_data.csv
├── scripts/
│   └── generate_data.py
└── sql/
    └── mysql_queries.sql

Acknowledgments
This project was independently completed as part of a self-directed actuarial data visualization portfolio. It demonstrates practical application of IFRS 17 concepts, data engineering, and business intelligence skills relevant to entry-level actuarial roles.

Author
Jeff Haonan Xie
jeffxhn@gmail.com
Linkedin: https://www.linkedin.com/in/jeff-haonan-xie-05530b164/ 
