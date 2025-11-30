
-- ============================================================================
-- SANTANDER UK BANKING DATABASE SCHEMA
-- For Workshop: Data Analysis and Data Science with Devin
-- ============================================================================

-- CUSTOMERS TABLE
CREATE TABLE customers (
    customer_id VARCHAR(10) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    date_of_birth DATE,
    age INTEGER,
    gender VARCHAR(10),
    address VARCHAR(200),
    city VARCHAR(50),
    postcode VARCHAR(10),
    account_type VARCHAR(50),
    account_number VARCHAR(20) UNIQUE,
    sort_code VARCHAR(10),
    account_open_date DATE,
    balance DECIMAL(15, 2),
    income_bracket VARCHAR(20),
    credit_score INTEGER,
    num_products INTEGER,
    customer_segment VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    has_mobile_app BOOLEAN DEFAULT FALSE,
    has_online_banking BOOLEAN DEFAULT FALSE,
    marketing_consent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TRANSACTIONS TABLE
CREATE TABLE transactions (
    transaction_id VARCHAR(15) PRIMARY KEY,
    customer_id VARCHAR(10) REFERENCES customers(customer_id),
    transaction_date DATE NOT NULL,
    transaction_time TIME NOT NULL,
    transaction_type VARCHAR(10) NOT NULL,
    category VARCHAR(50),
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'GBP',
    merchant_name VARCHAR(100),
    merchant_category_code INTEGER,
    channel VARCHAR(20),
    location VARCHAR(50),
    is_international BOOLEAN DEFAULT FALSE,
    is_recurring BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'Completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- COMPLAINTS TABLE
CREATE TABLE complaints (
    complaint_id VARCHAR(15) PRIMARY KEY,
    customer_id VARCHAR(10) REFERENCES customers(customer_id),
    customer_age INTEGER,
    customer_gender VARCHAR(10),
    customer_segment VARCHAR(20),
    customer_city VARCHAR(50),
    complaint_date DATE NOT NULL,
    complaint_time TIME NOT NULL,
    category VARCHAR(50) NOT NULL,
    severity VARCHAR(20),
    description TEXT,
    channel VARCHAR(20),
    status VARCHAR(20) DEFAULT 'Open',
    resolution_date DATE,
    resolution_days INTEGER,
    compensation_amount DECIMAL(10, 2) DEFAULT 0,
    satisfaction_score INTEGER,
    escalated BOOLEAN DEFAULT FALSE,
    product_involved VARCHAR(100),
    branch_code VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PRODUCT_HOLDINGS TABLE
CREATE TABLE product_holdings (
    product_name VARCHAR(100) PRIMARY KEY,
    total_customers INTEGER,
    avg_balance DECIMAL(15, 2),
    avg_customer_age DECIMAL(5, 1),
    revenue_contribution DECIMAL(15, 2),
    customer_satisfaction DECIMAL(3, 2),
    churn_rate DECIMAL(5, 4),
    growth_rate DECIMAL(5, 4),
    avg_tenure_months INTEGER,
    digital_adoption_rate DECIMAL(4, 2)
);

-- INDEXES FOR PERFORMANCE
CREATE INDEX idx_customers_city ON customers(city);
CREATE INDEX idx_customers_segment ON customers(customer_segment);
CREATE INDEX idx_customers_age ON customers(age);
CREATE INDEX idx_transactions_customer ON transactions(customer_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_category ON transactions(category);
CREATE INDEX idx_complaints_customer ON complaints(customer_id);
CREATE INDEX idx_complaints_date ON complaints(complaint_date);
CREATE INDEX idx_complaints_category ON complaints(category);
CREATE INDEX idx_complaints_status ON complaints(status);

-- ============================================================================
-- SAMPLE QUERIES FOR WORKSHOP
-- ============================================================================

-- Query 1: Customer demographics by segment
-- SELECT customer_segment, 
--        AVG(age) as avg_age, 
--        AVG(balance) as avg_balance,
--        COUNT(*) as customer_count
-- FROM customers
-- GROUP BY customer_segment;

-- Query 2: Monthly transaction volume
-- SELECT DATE_TRUNC('month', transaction_date) as month,
--        SUM(amount) as total_amount,
--        COUNT(*) as transaction_count
-- FROM transactions
-- WHERE transaction_type = 'Debit'
-- GROUP BY DATE_TRUNC('month', transaction_date)
-- ORDER BY month;

-- Query 3: Complaint resolution analysis
-- SELECT category,
--        AVG(resolution_days) as avg_resolution_days,
--        COUNT(*) as complaint_count,
--        AVG(satisfaction_score) as avg_satisfaction
-- FROM complaints
-- WHERE status IN ('Resolved', 'Closed')
-- GROUP BY category
-- ORDER BY avg_resolution_days DESC;

-- Query 4: Repeat complainers identification
-- SELECT customer_id, COUNT(*) as complaint_count
-- FROM complaints
-- GROUP BY customer_id
-- HAVING COUNT(*) > 2
-- ORDER BY complaint_count DESC;
