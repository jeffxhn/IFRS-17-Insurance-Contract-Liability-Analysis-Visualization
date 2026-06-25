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
SELECT COUNT(*) FROM fact_contract_liability;      -- 800 rows
SELECT COUNT(DISTINCT contract_id) FROM fact_contract_liability;   -- 100 contracts
