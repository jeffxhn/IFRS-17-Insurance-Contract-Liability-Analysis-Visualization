"""
IFRS 17 Data Generator
Generates simulated contract liability data for Power BI analysis
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(2026)

print("=" * 60)
print("IFRS 17 Data Generator - Starting...")
print("=" * 60)

# ---------- MySQL Connection ----------
# Update the password below to your MySQL root password
engine = create_engine('mysql+mysqlconnector://root:Jy731225@localhost/ifrs17_project')

# ---------- Parameters ----------
num_contracts = 100
product_types = ['Term Life', 'Whole Life', 'Annuity']
product_weights = [0.5, 0.3, 0.2]  # 50% Term Life, 30% Whole Life, 20% Annuity

# 8 quarterly reporting periods: 2024-Q1 to 2025-Q4
report_dates = pd.date_range('2024-01-01', '2025-12-31', freq='Q')

print(f"Generating data for {num_contracts} contracts across {len(report_dates)} quarters")
print(f"Expected total records: {num_contracts * len(report_dates)}")

# ---------- Generate Data ----------
data = []
contract_ids = ['CON' + str(i).zfill(5) for i in range(1, num_contracts + 1)]

print("\nGenerating contract data...")

for idx, contract in enumerate(contract_ids):
    # Contract-level attributes (fixed across all quarters)
    product = np.random.choice(product_types, p=product_weights)
    issue_year = np.random.randint(2018, 2025)
    cohort = f"{issue_year}-Q{np.random.randint(1, 5)}"
    
    # Base financial parameters
    base_fcf = np.random.uniform(10000, 50000)          # Fulfilment cash flows
    base_ra = base_fcf * np.random.uniform(0.05, 0.15)   # Risk adjustment
    base_csm = np.random.uniform(5000, 30000)            # Initial CSM
    
    # Flag some contracts as loss-making (about 5%)
    is_loss_contract = np.random.random() < 0.05
    if is_loss_contract:
        base_csm = -np.random.uniform(1000, 5000)
    
    # Initialize rolling CSM balance (cannot be negative)
    csm_balance = max(base_csm, 0)
    loss_component = max(-base_csm, 0)
    
    # Generate data for each reporting quarter
    for i, rpt_date in enumerate(report_dates):
        # ----- CSM Roll-forward (Core IFRS 17 Logic) -----
        csm_open = csm_balance
        
        # CSM release: ~2% per quarter (8% annualized)
        release_rate = 0.02 + np.random.uniform(-0.005, 0.005)
        csm_release = csm_open * release_rate if csm_open > 0 else 0
        
        # Experience adjustments (unlocking): occurs in ~20% of quarters
        if np.random.random() < 0.2 and csm_open > 0:
            csm_unlocking = np.random.uniform(-csm_open * 0.1, csm_open * 0.1)
        else:
            csm_unlocking = 0
        
        # Interest accretion: based on discount rate (2%-5% annual)
        discount_rate = np.random.uniform(0.02, 0.05)
        csm_interest = (csm_open - csm_release) * (discount_rate / 4) if csm_open > 0 else 0
        
        # New business CSM: only in the first quarter
        csm_new = base_csm * 0.1 if i == 0 else 0
        
        # Closing CSM
        csm_close = csm_open - csm_release + csm_unlocking + csm_interest + csm_new
        
        # Handle loss component
        if csm_close < 0:
            loss_component = -csm_close
            csm_close = 0
        elif loss_component > 0 and csm_close > 0:
            # Recover from loss component gradually (max 10% per quarter)
            recovery = min(loss_component, csm_close * 0.1)
            loss_component -= recovery
            csm_close -= recovery
        
        # Update for next quarter
        csm_balance = csm_close
        
        # ----- Income Statement Items -----
        # Insurance revenue = released CSM + expected claims (~1% of FCF)
        insurance_revenue = csm_release + base_fcf * 0.01 + np.random.uniform(-100, 100)
        insurance_revenue = max(insurance_revenue, 0)
        
        # Insurance service expense = actual claims (~0.8% of FCF) + other costs
        insurance_expense = base_fcf * 0.008 + np.random.uniform(-300, 300)
        insurance_expense = max(insurance_expense, 0)
        
        # Insurance finance expense = discount rate × fulfilment cash flows
        finance_expense = (discount_rate / 4) * base_fcf
        
        # Add random variation to FCF and RA each quarter
        fcf = base_fcf + np.random.uniform(-1000, 1000)
        ra = base_ra * (1 + 0.02 * i)  # RA grows slightly over time
        
        # Append record
        data.append({
            'contract_id': contract,
            'report_date': rpt_date,
            'product_type': product,
            'issue_year': issue_year,
            'cohort': cohort,
            'fulfilment_cashflows': round(fcf, 2),
            'risk_adjustment': round(ra, 2),
            'csm_opening': round(csm_open, 2),
            'csm_release': round(csm_release, 2),
            'csm_unlocking': round(csm_unlocking, 2),
            'csm_interest_accretion': round(csm_interest, 2),
            'csm_new_business': round(csm_new, 2),
            'csm_closing': round(csm_close, 2),
            'loss_component': round(loss_component, 2),
            'discount_rate': round(discount_rate, 4),
            'insurance_revenue': round(insurance_revenue, 2),
            'insurance_service_expense': round(insurance_expense, 2),
            'insurance_finance_expense': round(finance_expense, 2)
        })
    
    # Progress indicator
    if (idx + 1) % 10 == 0:
        print(f"  Completed {idx + 1}/{num_contracts} contracts")

# ---------- Convert to DataFrame ----------
df = pd.DataFrame(data)
print(f"\n[OK] Data generation complete! {len(df)} records created.")

# ---------- Data Quality Checks ----------
print("\n--- Data Preview (first 5 rows) ---")
print(df.head())

print("\n--- Product Distribution ---")
print(df['product_type'].value_counts())

print(f"\nReport date range: {df['report_date'].min()} to {df['report_date'].max()}")
print(f"Unique contracts: {df['contract_id'].nunique()}")

# ---------- Export to CSV ----------
csv_path = 'C:/Users/user/OneDrive/Desktop/project/ifrs17_project/data/ifrs17_data.csv'
df.to_csv(csv_path, index=False)
print(f"\n[OK] Data exported to CSV: {csv_path}")
print(f"Total records: {len(df)}")

print("\n" + "=" * 60)
print("[SUCCESS] CSV export complete! Now import to MySQL using Workbench.")
print("=" * 60)
