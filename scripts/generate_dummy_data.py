#!/usr/bin/env python3
"""
Generate realistic dummy banking data for Santander UK Workshop
This script creates:
1. Two Excel sheets with customer and transaction data (for Data Analysis use case)
2. Customer complaints CSV (for Data Science use case)
3. SQL schema documentation
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os

# Initialize Faker with UK locale
fake = Faker('en_GB')
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# Output directory
OUTPUT_DIR = '/home/ubuntu/santander-workshop/data'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================================
# CONFIGURATION
# ============================================================================

NUM_CUSTOMERS = 500
NUM_TRANSACTIONS = 5000
NUM_COMPLAINTS = 1000

# UK Cities for Santander branches
UK_CITIES = [
    'London', 'Manchester', 'Birmingham', 'Leeds', 'Glasgow', 'Liverpool',
    'Newcastle', 'Sheffield', 'Bristol', 'Edinburgh', 'Cardiff', 'Belfast',
    'Nottingham', 'Southampton', 'Leicester', 'Coventry', 'Bradford', 'Stoke-on-Trent'
]

# Account types
ACCOUNT_TYPES = ['Current Account', 'Savings Account', 'ISA', 'Business Account', 'Student Account']

# Product categories
PRODUCTS = ['1|2|3 Current Account', 'Everyday Current Account', 'Select Current Account',
            'eSaver', 'Everyday Saver', 'Help to Buy ISA', 'Cash ISA', 'Stocks & Shares ISA',
            'Personal Loan', 'Mortgage', 'Credit Card', 'Business Current Account']

# Transaction categories
TRANSACTION_CATEGORIES = [
    'Groceries', 'Utilities', 'Entertainment', 'Transport', 'Dining',
    'Shopping', 'Healthcare', 'Education', 'Travel', 'Subscriptions',
    'Salary', 'Transfer In', 'Transfer Out', 'ATM Withdrawal', 'Direct Debit'
]

# Complaint categories
COMPLAINT_CATEGORIES = [
    'Account Access Issues', 'Transaction Disputes', 'Fee Complaints',
    'Customer Service', 'Mobile App Issues', 'Card Problems',
    'Loan/Mortgage Issues', 'Fraud/Security', 'Branch Service',
    'Online Banking', 'Payment Delays', 'Interest Rate Disputes'
]

COMPLAINT_SEVERITY = ['Low', 'Medium', 'High', 'Critical']
COMPLAINT_STATUS = ['Open', 'In Progress', 'Resolved', 'Escalated', 'Closed']
COMPLAINT_CHANNELS = ['Phone', 'Email', 'Branch', 'Mobile App', 'Online Chat', 'Social Media']

# ============================================================================
# DATA GENERATION FUNCTIONS
# ============================================================================

def generate_customer_data():
    """Generate customer demographic and account data"""
    customers = []
    
    for i in range(NUM_CUSTOMERS):
        # Generate age with realistic distribution (18-85)
        age = int(np.random.normal(45, 15))
        age = max(18, min(85, age))
        
        # Gender distribution
        gender = random.choice(['Male', 'Female', 'Other'])
        
        # Generate name based on gender
        if gender == 'Male':
            first_name = fake.first_name_male()
        elif gender == 'Female':
            first_name = fake.first_name_female()
        else:
            first_name = fake.first_name()
        
        last_name = fake.last_name()
        
        # Account opening date (within last 10 years)
        account_open_date = fake.date_between(start_date='-10y', end_date='today')
        
        # Income bracket based on age
        if age < 25:
            income_bracket = random.choice(['0-20k', '20k-35k', '35k-50k'])
        elif age < 35:
            income_bracket = random.choice(['20k-35k', '35k-50k', '50k-75k', '75k-100k'])
        elif age < 55:
            income_bracket = random.choice(['35k-50k', '50k-75k', '75k-100k', '100k+'])
        else:
            income_bracket = random.choice(['20k-35k', '35k-50k', '50k-75k'])
        
        # Credit score (300-850)
        credit_score = int(np.random.normal(680, 80))
        credit_score = max(300, min(850, credit_score))
        
        # Account balance
        balance = round(random.uniform(100, 50000), 2)
        
        # Number of products
        num_products = random.choices([1, 2, 3, 4, 5], weights=[30, 35, 20, 10, 5])[0]
        
        # Customer segment
        if balance > 25000 or income_bracket in ['75k-100k', '100k+']:
            segment = 'Premium'
        elif balance > 10000:
            segment = 'Standard Plus'
        else:
            segment = 'Standard'
        
        customer = {
            'customer_id': f'SAN{100000 + i}',
            'first_name': first_name,
            'last_name': last_name,
            'email': f'{first_name.lower()}.{last_name.lower()}@{fake.free_email_domain()}',
            'phone': fake.phone_number(),
            'date_of_birth': (datetime.now() - timedelta(days=age*365)).strftime('%Y-%m-%d'),
            'age': age,
            'gender': gender,
            'address': fake.street_address(),
            'city': random.choice(UK_CITIES),
            'postcode': fake.postcode(),
            'account_type': random.choice(ACCOUNT_TYPES),
            'account_number': f'{random.randint(10000000, 99999999)}',
            'sort_code': f'{random.randint(10, 99)}-{random.randint(10, 99)}-{random.randint(10, 99)}',
            'account_open_date': account_open_date.strftime('%Y-%m-%d'),
            'balance': balance,
            'income_bracket': income_bracket,
            'credit_score': credit_score,
            'num_products': num_products,
            'customer_segment': segment,
            'is_active': random.choices([True, False], weights=[95, 5])[0],
            'has_mobile_app': random.choices([True, False], weights=[70, 30])[0],
            'has_online_banking': random.choices([True, False], weights=[85, 15])[0],
            'marketing_consent': random.choices([True, False], weights=[60, 40])[0]
        }
        customers.append(customer)
    
    return pd.DataFrame(customers)

def generate_transaction_data(customers_df):
    """Generate transaction data linked to customers"""
    transactions = []
    
    customer_ids = customers_df['customer_id'].tolist()
    
    for i in range(NUM_TRANSACTIONS):
        customer_id = random.choice(customer_ids)
        
        # Transaction date (within last 12 months)
        trans_date = fake.date_time_between(start_date='-12M', end_date='now')
        
        # Transaction type and amount
        category = random.choice(TRANSACTION_CATEGORIES)
        
        if category in ['Salary', 'Transfer In']:
            trans_type = 'Credit'
            amount = round(random.uniform(500, 5000), 2)
        elif category in ['Transfer Out', 'ATM Withdrawal']:
            trans_type = 'Debit'
            amount = round(random.uniform(20, 500), 2)
        else:
            trans_type = 'Debit'
            amount = round(random.uniform(5, 200), 2)
        
        # Merchant info
        if category == 'Groceries':
            merchant = random.choice(['Tesco', 'Sainsbury\'s', 'ASDA', 'Morrisons', 'Waitrose', 'Aldi', 'Lidl'])
        elif category == 'Utilities':
            merchant = random.choice(['British Gas', 'EDF Energy', 'Thames Water', 'BT', 'Sky', 'Virgin Media'])
        elif category == 'Transport':
            merchant = random.choice(['TfL', 'National Rail', 'Uber', 'Shell', 'BP', 'Esso'])
        elif category == 'Dining':
            merchant = random.choice(['Nando\'s', 'Pizza Express', 'Wagamama', 'Costa', 'Starbucks', 'Pret'])
        elif category == 'Entertainment':
            merchant = random.choice(['Netflix', 'Spotify', 'Amazon Prime', 'Disney+', 'Vue Cinema', 'Odeon'])
        else:
            merchant = fake.company()
        
        transaction = {
            'transaction_id': f'TXN{1000000 + i}',
            'customer_id': customer_id,
            'transaction_date': trans_date.strftime('%Y-%m-%d'),
            'transaction_time': trans_date.strftime('%H:%M:%S'),
            'transaction_type': trans_type,
            'category': category,
            'amount': amount,
            'currency': 'GBP',
            'merchant_name': merchant,
            'merchant_category_code': random.randint(1000, 9999),
            'channel': random.choice(['Online', 'In-Store', 'ATM', 'Mobile App', 'Direct Debit']),
            'location': random.choice(UK_CITIES),
            'is_international': random.choices([True, False], weights=[5, 95])[0],
            'is_recurring': random.choices([True, False], weights=[20, 80])[0],
            'status': random.choices(['Completed', 'Pending', 'Failed'], weights=[95, 3, 2])[0]
        }
        transactions.append(transaction)
    
    return pd.DataFrame(transactions)

def generate_complaints_data(customers_df):
    """Generate customer complaints data with outliers and repeat complainers"""
    complaints = []
    
    customer_ids = customers_df['customer_id'].tolist()
    
    # Create some repeat complainers (10% of customers will have multiple complaints)
    repeat_complainers = random.sample(customer_ids, int(len(customer_ids) * 0.1))
    
    complaint_id = 0
    
    # Generate complaints for repeat complainers (3-8 complaints each)
    for customer_id in repeat_complainers:
        num_complaints = random.randint(3, 8)
        for _ in range(num_complaints):
            complaint = generate_single_complaint(complaint_id, customer_id, customers_df)
            complaints.append(complaint)
            complaint_id += 1
    
    # Fill remaining complaints with random customers
    remaining_complaints = NUM_COMPLAINTS - len(complaints)
    for _ in range(remaining_complaints):
        customer_id = random.choice(customer_ids)
        complaint = generate_single_complaint(complaint_id, customer_id, customers_df)
        complaints.append(complaint)
        complaint_id += 1
    
    # Add some outliers (unusual resolution times, extreme amounts)
    df = pd.DataFrame(complaints)
    
    # Add outlier resolution times (some very long, some very short)
    outlier_indices = random.sample(range(len(df)), int(len(df) * 0.05))
    for idx in outlier_indices:
        if random.random() > 0.5:
            df.loc[idx, 'resolution_days'] = random.randint(90, 180)  # Very long resolution
        else:
            df.loc[idx, 'resolution_days'] = 0  # Instant resolution (suspicious)
    
    # Add outlier compensation amounts
    outlier_indices = random.sample(range(len(df)), int(len(df) * 0.03))
    for idx in outlier_indices:
        df.loc[idx, 'compensation_amount'] = round(random.uniform(500, 2000), 2)  # High compensation
    
    return df

def generate_single_complaint(complaint_id, customer_id, customers_df):
    """Generate a single complaint record"""
    customer = customers_df[customers_df['customer_id'] == customer_id].iloc[0]
    
    # Complaint date (within last 18 months)
    complaint_date = fake.date_time_between(start_date='-18M', end_date='now')
    
    # Resolution time (1-60 days typically)
    resolution_days = int(np.random.exponential(14))
    resolution_days = max(1, min(60, resolution_days))
    
    resolution_date = complaint_date + timedelta(days=resolution_days)
    if resolution_date > datetime.now():
        resolution_date = None
        status = random.choice(['Open', 'In Progress', 'Escalated'])
    else:
        status = random.choice(['Resolved', 'Closed'])
    
    # Compensation (only for resolved complaints)
    if status in ['Resolved', 'Closed'] and random.random() > 0.7:
        compensation = round(random.uniform(10, 200), 2)
    else:
        compensation = 0.0
    
    category = random.choice(COMPLAINT_CATEGORIES)
    severity = random.choices(COMPLAINT_SEVERITY, weights=[40, 35, 20, 5])[0]
    
    # Generate complaint description based on category
    descriptions = {
        'Account Access Issues': [
            'Unable to log into online banking for 3 days',
            'Password reset not working',
            'Account locked without explanation',
            'Two-factor authentication issues'
        ],
        'Transaction Disputes': [
            'Unauthorized transaction on my account',
            'Double charged for a purchase',
            'Refund not received after 30 days',
            'Incorrect amount debited'
        ],
        'Fee Complaints': [
            'Unexpected overdraft fee charged',
            'Monthly fee increased without notice',
            'Foreign transaction fee too high',
            'ATM withdrawal fee dispute'
        ],
        'Customer Service': [
            'Long wait times on phone support',
            'Unhelpful staff at branch',
            'Promised callback never received',
            'Incorrect information provided'
        ],
        'Mobile App Issues': [
            'App crashes when checking balance',
            'Cannot make payments through app',
            'Fingerprint login not working',
            'App shows incorrect balance'
        ],
        'Card Problems': [
            'Card declined despite sufficient funds',
            'New card not received after 2 weeks',
            'Contactless payment not working',
            'Card blocked while travelling'
        ],
        'Loan/Mortgage Issues': [
            'Incorrect interest rate applied',
            'Payment not reflected on account',
            'Early repayment fee dispute',
            'Mortgage application delayed'
        ],
        'Fraud/Security': [
            'Suspicious activity not flagged',
            'Fraud alert triggered incorrectly',
            'Security breach concern',
            'Phishing email received'
        ],
        'Branch Service': [
            'Branch closed without notice',
            'Long queues at branch',
            'Appointment not honored',
            'Documents lost by branch'
        ],
        'Online Banking': [
            'Website down during payment',
            'Cannot download statements',
            'Transfer limit too restrictive',
            'Session timeout too short'
        ],
        'Payment Delays': [
            'Salary not credited on time',
            'Standing order failed',
            'International transfer delayed',
            'Direct debit not processed'
        ],
        'Interest Rate Disputes': [
            'Savings rate lower than advertised',
            'Variable rate increased unexpectedly',
            'Promotional rate not applied',
            'Interest calculation incorrect'
        ]
    }
    
    description = random.choice(descriptions.get(category, ['General complaint']))
    
    return {
        'complaint_id': f'CMP{100000 + complaint_id}',
        'customer_id': customer_id,
        'customer_age': customer['age'],
        'customer_gender': customer['gender'],
        'customer_segment': customer['customer_segment'],
        'customer_city': customer['city'],
        'complaint_date': complaint_date.strftime('%Y-%m-%d'),
        'complaint_time': complaint_date.strftime('%H:%M:%S'),
        'category': category,
        'severity': severity,
        'description': description,
        'channel': random.choice(COMPLAINT_CHANNELS),
        'status': status,
        'resolution_date': resolution_date.strftime('%Y-%m-%d') if resolution_date else None,
        'resolution_days': resolution_days if status in ['Resolved', 'Closed'] else None,
        'compensation_amount': compensation,
        'satisfaction_score': random.randint(1, 5) if status in ['Resolved', 'Closed'] else None,
        'escalated': severity in ['High', 'Critical'] and random.random() > 0.5,
        'product_involved': random.choice(PRODUCTS),
        'branch_code': f'BR{random.randint(100, 999)}' if random.random() > 0.5 else None
    }

def generate_product_holdings():
    """Generate product holdings data for bubble chart analysis"""
    products = []
    
    for product in PRODUCTS:
        # Generate metrics for each product
        product_data = {
            'product_name': product,
            'total_customers': random.randint(5000, 100000),
            'avg_balance': round(random.uniform(1000, 50000), 2),
            'avg_customer_age': round(random.uniform(25, 55), 1),
            'revenue_contribution': round(random.uniform(100000, 5000000), 2),
            'customer_satisfaction': round(random.uniform(3.0, 4.8), 2),
            'churn_rate': round(random.uniform(0.02, 0.15), 4),
            'growth_rate': round(random.uniform(-0.05, 0.20), 4),
            'avg_tenure_months': random.randint(12, 120),
            'digital_adoption_rate': round(random.uniform(0.3, 0.95), 2)
        }
        products.append(product_data)
    
    return pd.DataFrame(products)

def generate_sql_schema():
    """Generate SQL schema documentation"""
    schema = """
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
"""
    return schema

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    print("Generating Santander UK Workshop Dummy Data...")
    print("=" * 60)
    
    # Generate customer data
    print("1. Generating customer data...")
    customers_df = generate_customer_data()
    print(f"   Generated {len(customers_df)} customer records")
    
    # Generate transaction data
    print("2. Generating transaction data...")
    transactions_df = generate_transaction_data(customers_df)
    print(f"   Generated {len(transactions_df)} transaction records")
    
    # Generate complaints data
    print("3. Generating complaints data...")
    complaints_df = generate_complaints_data(customers_df)
    print(f"   Generated {len(complaints_df)} complaint records")
    
    # Generate product holdings
    print("4. Generating product holdings data...")
    products_df = generate_product_holdings()
    print(f"   Generated {len(products_df)} product records")
    
    # Save Excel files for Data Analysis use case
    print("\n5. Saving Excel files...")
    
    # Excel Sheet 1: Customer Information
    with pd.ExcelWriter(f'{OUTPUT_DIR}/santander_customers.xlsx', engine='xlsxwriter') as writer:
        customers_df.to_excel(writer, sheet_name='Customer_Data', index=False)
        
        # Add summary sheet
        summary_data = {
            'Metric': ['Total Customers', 'Active Customers', 'Premium Segment', 
                      'Standard Plus Segment', 'Standard Segment', 'Avg Balance',
                      'Avg Credit Score', 'Mobile App Users', 'Online Banking Users'],
            'Value': [
                len(customers_df),
                customers_df['is_active'].sum(),
                len(customers_df[customers_df['customer_segment'] == 'Premium']),
                len(customers_df[customers_df['customer_segment'] == 'Standard Plus']),
                len(customers_df[customers_df['customer_segment'] == 'Standard']),
                round(customers_df['balance'].mean(), 2),
                round(customers_df['credit_score'].mean(), 0),
                customers_df['has_mobile_app'].sum(),
                customers_df['has_online_banking'].sum()
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
    print(f"   Saved: {OUTPUT_DIR}/santander_customers.xlsx")
    
    # Excel Sheet 2: Transaction Information
    with pd.ExcelWriter(f'{OUTPUT_DIR}/santander_transactions.xlsx', engine='xlsxwriter') as writer:
        transactions_df.to_excel(writer, sheet_name='Transaction_Data', index=False)
        
        # Add category summary
        category_summary = transactions_df.groupby('category').agg({
            'amount': ['sum', 'mean', 'count']
        }).round(2)
        category_summary.columns = ['Total_Amount', 'Avg_Amount', 'Count']
        category_summary.reset_index().to_excel(writer, sheet_name='Category_Summary', index=False)
    print(f"   Saved: {OUTPUT_DIR}/santander_transactions.xlsx")
    
    # Save CSV for Data Science use case
    print("\n6. Saving CSV files...")
    complaints_df.to_csv(f'{OUTPUT_DIR}/customer_complaints.csv', index=False)
    print(f"   Saved: {OUTPUT_DIR}/customer_complaints.csv")
    
    products_df.to_csv(f'{OUTPUT_DIR}/product_holdings.csv', index=False)
    print(f"   Saved: {OUTPUT_DIR}/product_holdings.csv")
    
    # Save SQL schema
    print("\n7. Saving SQL schema...")
    with open(f'{OUTPUT_DIR}/database_schema.sql', 'w') as f:
        f.write(generate_sql_schema())
    print(f"   Saved: {OUTPUT_DIR}/database_schema.sql")
    
    # Print data summary
    print("\n" + "=" * 60)
    print("DATA GENERATION COMPLETE")
    print("=" * 60)
    print(f"\nFiles created in {OUTPUT_DIR}:")
    print("  - santander_customers.xlsx (Customer demographics & accounts)")
    print("  - santander_transactions.xlsx (Transaction history)")
    print("  - customer_complaints.csv (Complaints data for analysis)")
    print("  - product_holdings.csv (Product metrics for bubble charts)")
    print("  - database_schema.sql (SQL schema documentation)")
    
    print("\n--- Data Statistics ---")
    print(f"Customers: {len(customers_df)}")
    print(f"  - Age range: {customers_df['age'].min()} - {customers_df['age'].max()}")
    print(f"  - Gender distribution: {customers_df['gender'].value_counts().to_dict()}")
    print(f"  - Segment distribution: {customers_df['customer_segment'].value_counts().to_dict()}")
    
    print(f"\nTransactions: {len(transactions_df)}")
    print(f"  - Total value: GBP {transactions_df['amount'].sum():,.2f}")
    print(f"  - Date range: {transactions_df['transaction_date'].min()} to {transactions_df['transaction_date'].max()}")
    
    print(f"\nComplaints: {len(complaints_df)}")
    print(f"  - Categories: {complaints_df['category'].nunique()}")
    print(f"  - Repeat complainers: {len(complaints_df.groupby('customer_id').filter(lambda x: len(x) > 2)['customer_id'].unique())}")
    
    # Identify outliers for workshop reference
    print("\n--- Outliers for Workshop ---")
    long_resolution = complaints_df[complaints_df['resolution_days'] > 60]
    print(f"  - Complaints with resolution > 60 days: {len(long_resolution)}")
    high_compensation = complaints_df[complaints_df['compensation_amount'] > 300]
    print(f"  - Complaints with compensation > GBP 300: {len(high_compensation)}")
