# Santander UK Data Analysis & Data Science Workshop with Devin

## 2-Hour Hands-On Workshop Guide

**Target Audience:** Data Analysis and Data Science Teams at Bank Santander UK  
**Duration:** 2 hours  
**Format:** Hands-on workshop with participants using their own laptops  
**Prerequisites:** Devin access, GitHub account, basic SQL knowledge

---

## Workshop Overview

This workshop demonstrates how Devin can accelerate data analysis workflows, from extracting data from Excel files to generating SQL queries, identifying outliers, and creating interactive dashboards. Throughout the session, we'll showcase how Devin integrates into the Software Development Life Cycle (SDLC).

### Learning Objectives

By the end of this workshop, participants will be able to:

1. Use Devin to extract and transform data from Excel files into SQL-ready formats
2. Leverage Devin for data science tasks including outlier detection and repeat pattern analysis
3. Build interactive dashboards using Devin-generated code
4. Understand how Devin integrates with GitHub, AWS, and other enterprise tools
5. Apply SDLC best practices when working with Devin

---

## Pre-Workshop Setup

### For Workshop Facilitators

**1. Data Files Location**

All dummy data files are available in the S3 bucket:
```
s3://devin-workshop/santander-workshop/
```

Files included:
- `santander_customers.xlsx` - Customer demographics and account information
- `santander_transactions.xlsx` - Transaction history with category summaries
- `customer_complaints.csv` - Complaints data with outliers and repeat complainers
- `product_holdings.csv` - Product metrics for bubble chart analysis
- `database_schema.sql` - SQL schema documentation

**2. S3 Bucket URLs for Participants**

Provide these URLs to participants:
```
https://devin-workshop.s3.eu-north-1.amazonaws.com/santander-workshop/santander_customers.xlsx
https://devin-workshop.s3.eu-north-1.amazonaws.com/santander-workshop/santander_transactions.xlsx
https://devin-workshop.s3.eu-north-1.amazonaws.com/santander-workshop/customer_complaints.csv
https://devin-workshop.s3.eu-north-1.amazonaws.com/santander-workshop/product_holdings.csv
https://devin-workshop.s3.eu-north-1.amazonaws.com/santander-workshop/database_schema.sql
```

**3. GitHub Repository Setup**

Create a workshop repository in your GitHub organization:
```bash
# Repository structure
santander-devin-workshop/
  README.md
  data/
    (participants will download files here)
  scripts/
    (Devin-generated scripts will go here)
  dashboard/
    (Dashboard code will go here)
  docs/
    coding_guidelines.md
    database_schema.sql
```

### For Participants

1. Ensure you have Devin access (app.devin.ai)
2. Have a GitHub account with access to the workshop repository
3. Install Python 3.9+ on your laptop
4. Install VS Code or preferred IDE
5. Have SQLite installed (or use Python's built-in sqlite3)

---

## Workshop Agenda

| Time | Duration | Section | Focus |
|------|----------|---------|-------|
| 0:00 | 10 min | Introduction | Workshop overview, Devin capabilities |
| 0:10 | 35 min | Use Case 1 | Data Analysis - Excel to SQL |
| 0:45 | 10 min | Break | - |
| 0:55 | 50 min | Use Case 2 | Data Science - Complaints Analysis & Dashboard |
| 1:45 | 15 min | SDLC Deep Dive | Advanced Devin features |

---

## Section 1: Introduction (10 minutes)

### 1.1 Welcome and Context Setting (5 minutes)

**Facilitator Script:**

"Welcome to today's workshop on using Devin for data analysis and data science tasks. Devin is an AI software engineer that can help you write code, analyze data, and integrate with your existing tools and workflows.

Today, we'll work through two realistic banking scenarios:
1. Extracting customer and transaction data from Excel files and generating SQL queries
2. Analyzing customer complaints data to identify outliers and repeat complainers, then building a dashboard

Throughout the workshop, we'll also explore how Devin fits into your Software Development Life Cycle."

### 1.2 Devin Capabilities Overview (5 minutes)

**Key Points to Cover:**

- Devin can read and understand various file formats (Excel, CSV, JSON, etc.)
- Devin writes production-quality code in multiple languages
- Devin integrates with GitHub for version control and CI/CD
- Devin can interact with databases, APIs, and cloud services
- Devin follows coding guidelines and best practices you provide

**Demo:** Show the Devin interface briefly, highlighting:
- Chat interface for natural language instructions
- File browser and code editor
- Terminal access
- Browser for documentation lookup

---

## Section 2: Data Analysis Use Case (35 minutes)

### Scenario Overview

**Business Context:** The Data Analysis team needs to extract customer and transaction data from Excel reports and format it for loading into the bank's SQL database. They also need to generate queries for common analytical tasks.

**Input Files:**
- `santander_customers.xlsx` - Contains customer demographics, account details, and segment information
- `santander_transactions.xlsx` - Contains transaction history with merchant and category data

**Tasks:**
1. Extract and validate data from Excel files
2. Generate SQL INSERT statements for database loading
3. Create analytical queries based on the database schema

### Exercise 2.1: Setting Up the Repository (5 minutes)

**Participant Instructions:**

1. Open Devin at app.devin.ai
2. Start a new session with this prompt:

```
I need to set up a new Python project for data analysis. Please:

1. Clone the repository: https://github.com/[ORG]/santander-devin-workshop
2. Create a virtual environment
3. Install pandas, openpyxl, and sqlalchemy
4. Download the Excel files from S3:
   - https://devin-workshop.s3.eu-north-1.amazonaws.com/santander-workshop/santander_customers.xlsx
   - https://devin-workshop.s3.eu-north-1.amazonaws.com/santander-workshop/santander_transactions.xlsx
5. Place them in the data/ directory
```

**Expected Devin Actions:**
- Clone repository
- Set up Python environment
- Install dependencies
- Download files using curl or requests
- Organize project structure

**SDLC Integration Point:** Discuss how Devin automatically sets up proper project structure and dependency management.

### Exercise 2.2: Data Extraction and Validation (10 minutes)

**Participant Instructions:**

Use this prompt with Devin:

```
Please analyze the Excel files in the data/ directory:

1. Read santander_customers.xlsx and santander_transactions.xlsx
2. Show me the structure of each file (columns, data types, row counts)
3. Identify any data quality issues (missing values, duplicates, invalid formats)
4. Create a data validation report

Follow our coding guidelines in docs/coding_guidelines.md for code style.
```

**Expected Devin Output:**
- Python script that reads Excel files
- Data profiling report showing:
  - 500 customers with columns: customer_id, first_name, last_name, email, etc.
  - 5000 transactions with columns: transaction_id, customer_id, amount, etc.
  - Data quality metrics

**Discussion Points:**
- How Devin uses pandas for data manipulation
- How Devin follows provided coding guidelines
- The importance of data validation before database loading

### Exercise 2.3: SQL Generation (15 minutes)

**Participant Instructions:**

Use this prompt with Devin:

```
Based on the database schema in docs/database_schema.sql, please:

1. Generate SQL INSERT statements for loading the customer data
2. Generate SQL INSERT statements for loading the transaction data
3. Create the following analytical queries:
   a. Customer demographics by segment (count, avg age, avg balance)
   b. Monthly transaction volume by category
   c. Top 10 customers by transaction count
   d. Average transaction amount by channel

Save all SQL to scripts/data_load.sql and scripts/analytics_queries.sql
```

**Expected Devin Output:**

```sql
-- Example INSERT statement
INSERT INTO customers (customer_id, first_name, last_name, email, phone, 
                       date_of_birth, age, gender, address, city, postcode,
                       account_type, account_number, sort_code, account_open_date,
                       balance, income_bracket, credit_score, num_products,
                       customer_segment, is_active, has_mobile_app, 
                       has_online_banking, marketing_consent)
VALUES ('SAN100000', 'John', 'Smith', 'john.smith@email.com', '+44 7700 900123',
        '1980-05-15', 44, 'Male', '123 High Street', 'London', 'SW1A 1AA',
        'Current Account', '12345678', '09-01-28', '2020-03-15',
        15234.50, '50k-75k', 720, 3, 'Premium', TRUE, TRUE, TRUE, TRUE);

-- Example analytical query
SELECT customer_segment,
       COUNT(*) as customer_count,
       ROUND(AVG(age), 1) as avg_age,
       ROUND(AVG(balance), 2) as avg_balance
FROM customers
GROUP BY customer_segment
ORDER BY customer_count DESC;
```

**SDLC Integration Point:** 
- Demonstrate how Devin creates a PR with the generated SQL scripts
- Show how to use Devin for code review of the generated SQL
- Discuss unit testing SQL queries

### Exercise 2.4: Commit and Push (5 minutes)

**Participant Instructions:**

```
Please commit all the work we've done so far:

1. Add all new files to git
2. Create a meaningful commit message
3. Push to a new branch called 'feature/data-analysis-scripts'
4. Create a pull request with a description of the changes
```

**Expected Devin Actions:**
- Stage files
- Create descriptive commit message
- Push to feature branch
- Create PR with summary

---

## Section 3: Break (10 minutes)

---

## Section 4: Data Science Use Case (50 minutes)

### Scenario Overview

**Business Context:** The Data Science team needs to analyze customer complaints data to identify patterns, outliers, and repeat complainers. They also need to create a dashboard for ongoing monitoring.

**Input Files:**
- `customer_complaints.csv` - Contains 1000 complaint records with outliers and repeat complainers

**Tasks:**
1. Load complaints data into SQLite database
2. Identify outliers and repeat complainers
3. Create an interactive dashboard with:
   - Descriptive statistics table
   - Time series graph
   - Bar chart
   - Filter dropdowns

### Exercise 4.1: SQLite Database Setup (10 minutes)

**Participant Instructions:**

```
I have a customer complaints CSV file at data/customer_complaints.csv. Please:

1. Create a Python script that:
   - Reads the CSV file
   - Creates a SQLite database called 'complaints.db'
   - Creates a table with appropriate data types
   - Loads all records into the database
   - Adds appropriate indexes for performance

2. Write unit tests for the data loading script

3. Verify the data was loaded correctly by running some test queries

Save the script to scripts/load_complaints_to_sqlite.py
```

**Expected Devin Output:**

```python
import sqlite3
import pandas as pd
from pathlib import Path

def create_database(db_path: str = 'complaints.db') -> sqlite3.Connection:
    """Create SQLite database and return connection."""
    conn = sqlite3.connect(db_path)
    return conn

def create_complaints_table(conn: sqlite3.Connection) -> None:
    """Create complaints table with appropriate schema."""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            complaint_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            customer_age INTEGER,
            customer_gender TEXT,
            customer_segment TEXT,
            customer_city TEXT,
            complaint_date DATE NOT NULL,
            complaint_time TIME,
            category TEXT NOT NULL,
            severity TEXT,
            description TEXT,
            channel TEXT,
            status TEXT,
            resolution_date DATE,
            resolution_days INTEGER,
            compensation_amount REAL DEFAULT 0,
            satisfaction_score INTEGER,
            escalated BOOLEAN,
            product_involved TEXT,
            branch_code TEXT
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_customer_id ON complaints(customer_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_complaint_date ON complaints(complaint_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON complaints(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON complaints(status)')
    
    conn.commit()

def load_csv_to_database(csv_path: str, conn: sqlite3.Connection) -> int:
    """Load CSV data into SQLite database."""
    df = pd.read_csv(csv_path)
    df.to_sql('complaints', conn, if_exists='replace', index=False)
    return len(df)

if __name__ == '__main__':
    conn = create_database()
    create_complaints_table(conn)
    records = load_csv_to_database('data/customer_complaints.csv', conn)
    print(f"Loaded {records} records into complaints.db")
    conn.close()
```

**SDLC Integration Point:** Discuss unit testing with Devin - show how to ask Devin to write pytest tests.

### Exercise 4.2: Outlier and Repeat Complainer Analysis (15 minutes)

**Participant Instructions:**

```
Using the complaints.db database, please:

1. Identify outliers in the data:
   - Complaints with unusually long resolution times (> 60 days)
   - Complaints with unusually high compensation amounts (> GBP 300)
   - Complaints with instant resolution (0 days) - potentially suspicious

2. Identify repeat complainers:
   - Customers with more than 2 complaints
   - Show their complaint history and patterns

3. Generate a statistical summary including:
   - Distribution of resolution times
   - Compensation amount statistics
   - Category-wise complaint counts

4. Create visualizations for the outlier analysis

Save the analysis script to scripts/outlier_analysis.py
```

**Expected Devin Output:**

```python
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

def identify_resolution_time_outliers(conn: sqlite3.Connection) -> pd.DataFrame:
    """Identify complaints with unusual resolution times."""
    query = '''
        SELECT complaint_id, customer_id, category, resolution_days, 
               compensation_amount, status
        FROM complaints
        WHERE resolution_days > 60 OR resolution_days = 0
        ORDER BY resolution_days DESC
    '''
    return pd.read_sql_query(query, conn)

def identify_high_compensation_outliers(conn: sqlite3.Connection) -> pd.DataFrame:
    """Identify complaints with unusually high compensation."""
    query = '''
        SELECT complaint_id, customer_id, category, severity,
               compensation_amount, resolution_days
        FROM complaints
        WHERE compensation_amount > 300
        ORDER BY compensation_amount DESC
    '''
    return pd.read_sql_query(query, conn)

def identify_repeat_complainers(conn: sqlite3.Connection) -> pd.DataFrame:
    """Identify customers with multiple complaints."""
    query = '''
        SELECT customer_id, 
               COUNT(*) as complaint_count,
               GROUP_CONCAT(category) as categories,
               AVG(resolution_days) as avg_resolution_days,
               SUM(compensation_amount) as total_compensation
        FROM complaints
        GROUP BY customer_id
        HAVING COUNT(*) > 2
        ORDER BY complaint_count DESC
    '''
    return pd.read_sql_query(query, conn)

# ... additional analysis functions
```

**Discussion Points:**
- Statistical methods for outlier detection
- Business implications of repeat complainers
- How Devin can help with exploratory data analysis

### Exercise 4.3: Dashboard Creation (20 minutes)

**Participant Instructions:**

```
Please create an interactive dashboard for the complaints data using Streamlit. The dashboard should include:

1. A descriptive statistics table showing:
   - Total complaints count
   - Available columns and their data types
   - Missing value counts
   - Unique value counts for categorical columns

2. A time series graph showing:
   - Complaints over time (daily/weekly/monthly aggregation)
   - Option to filter by category

3. A bar chart showing:
   - Complaints by category
   - Option to show by severity or status

4. Filter dropdowns for:
   - Category
   - Severity
   - Status
   - Date range
   - Customer segment

5. On-demand statistics that update based on filters

Save the dashboard to dashboard/app.py and include a requirements.txt
```

**Expected Devin Output:**

```python
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Santander Complaints Dashboard",
    page_icon="📊",
    layout="wide"
)

# Database connection
@st.cache_resource
def get_connection():
    return sqlite3.connect('complaints.db', check_same_thread=False)

@st.cache_data
def load_data():
    conn = get_connection()
    return pd.read_sql_query("SELECT * FROM complaints", conn)

def main():
    st.title("📊 Santander UK Customer Complaints Dashboard")
    
    # Load data
    df = load_data()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Category filter
    categories = ['All'] + sorted(df['category'].unique().tolist())
    selected_category = st.sidebar.selectbox("Category", categories)
    
    # Severity filter
    severities = ['All'] + sorted(df['severity'].dropna().unique().tolist())
    selected_severity = st.sidebar.selectbox("Severity", severities)
    
    # Status filter
    statuses = ['All'] + sorted(df['status'].unique().tolist())
    selected_status = st.sidebar.selectbox("Status", statuses)
    
    # Date range filter
    df['complaint_date'] = pd.to_datetime(df['complaint_date'])
    min_date = df['complaint_date'].min()
    max_date = df['complaint_date'].max()
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Apply filters
    filtered_df = df.copy()
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    if selected_severity != 'All':
        filtered_df = filtered_df[filtered_df['severity'] == selected_severity]
    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['complaint_date'] >= pd.Timestamp(date_range[0])) &
            (filtered_df['complaint_date'] <= pd.Timestamp(date_range[1]))
        ]
    
    # Main content
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Complaints", len(filtered_df))
    with col2:
        st.metric("Open Complaints", len(filtered_df[filtered_df['status'] == 'Open']))
    with col3:
        avg_resolution = filtered_df['resolution_days'].mean()
        st.metric("Avg Resolution (days)", f"{avg_resolution:.1f}" if pd.notna(avg_resolution) else "N/A")
    with col4:
        total_compensation = filtered_df['compensation_amount'].sum()
        st.metric("Total Compensation", f"£{total_compensation:,.2f}")
    
    # Descriptive Statistics Table
    st.header("📋 Data Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Column Information")
        column_info = pd.DataFrame({
            'Column': filtered_df.columns,
            'Data Type': filtered_df.dtypes.astype(str),
            'Non-Null Count': filtered_df.count(),
            'Null Count': filtered_df.isnull().sum(),
            'Unique Values': filtered_df.nunique()
        })
        st.dataframe(column_info, use_container_width=True)
    
    with col2:
        st.subheader("Numeric Statistics")
        st.dataframe(filtered_df.describe(), use_container_width=True)
    
    # Time Series Graph
    st.header("📈 Complaints Over Time")
    
    time_agg = st.radio("Aggregation", ["Daily", "Weekly", "Monthly"], horizontal=True)
    
    time_df = filtered_df.copy()
    if time_agg == "Daily":
        time_df['period'] = time_df['complaint_date'].dt.date
    elif time_agg == "Weekly":
        time_df['period'] = time_df['complaint_date'].dt.to_period('W').dt.start_time
    else:
        time_df['period'] = time_df['complaint_date'].dt.to_period('M').dt.start_time
    
    time_series = time_df.groupby('period').size().reset_index(name='count')
    
    fig_time = px.line(time_series, x='period', y='count',
                       title=f'{time_agg} Complaint Volume',
                       labels={'period': 'Date', 'count': 'Number of Complaints'})
    st.plotly_chart(fig_time, use_container_width=True)
    
    # Bar Charts
    st.header("📊 Complaint Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("By Category")
        category_counts = filtered_df['category'].value_counts()
        fig_cat = px.bar(x=category_counts.index, y=category_counts.values,
                        labels={'x': 'Category', 'y': 'Count'},
                        color=category_counts.values,
                        color_continuous_scale='Reds')
        fig_cat.update_layout(showlegend=False)
        st.plotly_chart(fig_cat, use_container_width=True)
    
    with col2:
        st.subheader("By Severity")
        severity_counts = filtered_df['severity'].value_counts()
        fig_sev = px.bar(x=severity_counts.index, y=severity_counts.values,
                        labels={'x': 'Severity', 'y': 'Count'},
                        color=severity_counts.values,
                        color_continuous_scale='Blues')
        fig_sev.update_layout(showlegend=False)
        st.plotly_chart(fig_sev, use_container_width=True)
    
    # Detailed Data Table
    st.header("📝 Detailed Complaints Data")
    st.dataframe(filtered_df, use_container_width=True)

if __name__ == '__main__':
    main()
```

**SDLC Integration Point:** 
- Discuss how to deploy the dashboard
- Show GitHub Actions integration for CI/CD
- Demonstrate Devin API for batch processing

### Exercise 4.4: Commit and Create PR (5 minutes)

**Participant Instructions:**

```
Please commit all the data science work:

1. Add all new files (scripts, dashboard, tests)
2. Create a commit with a descriptive message
3. Push to branch 'feature/complaints-analysis-dashboard'
4. Create a pull request
5. Run any linting or tests before the PR
```

---

## Section 5: SDLC Deep Dive (15 minutes)

### 5.1 Using Internal Documentation as Context (3 minutes)

**Demonstration:**

Show how to provide Devin with coding guidelines:

```
Please read our coding guidelines at docs/coding_guidelines.md and follow them for all code you write. Key points include:
- Use type hints for all functions
- Include docstrings in Google format
- Maximum line length of 100 characters
- Use meaningful variable names
```

**Sample Coding Guidelines File:**

```markdown
# Santander UK Coding Guidelines

## Python Standards

1. **Type Hints**: All functions must include type hints
2. **Docstrings**: Use Google-style docstrings
3. **Line Length**: Maximum 100 characters
4. **Imports**: Group imports (standard library, third-party, local)
5. **Testing**: Minimum 80% code coverage

## SQL Standards

1. **Naming**: Use snake_case for tables and columns
2. **Indexes**: Always index foreign keys
3. **Comments**: Document complex queries

## Git Workflow

1. **Branches**: feature/, bugfix/, hotfix/ prefixes
2. **Commits**: Use conventional commit messages
3. **PRs**: Require at least one review
```

### 5.2 Unit Testing with Devin (3 minutes)

**Demonstration:**

```
Please write unit tests for the load_complaints_to_sqlite.py script using pytest. Include:
- Test for successful database creation
- Test for data loading with valid CSV
- Test for handling missing columns
- Test for handling empty CSV
```

**Expected Output:**

```python
import pytest
import sqlite3
import pandas as pd
from pathlib import Path
import tempfile
from scripts.load_complaints_to_sqlite import (
    create_database,
    create_complaints_table,
    load_csv_to_database
)

@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        yield f.name
    Path(f.name).unlink(missing_ok=True)

def test_create_database(temp_db):
    """Test database creation."""
    conn = create_database(temp_db)
    assert conn is not None
    assert Path(temp_db).exists()
    conn.close()

def test_create_complaints_table(temp_db):
    """Test table creation with correct schema."""
    conn = create_database(temp_db)
    create_complaints_table(conn)
    
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='complaints'")
    assert cursor.fetchone() is not None
    conn.close()

# ... more tests
```

### 5.3 Devin API for Multiple Sessions (3 minutes)

**Demonstration:**

Show how to use the Devin API to launch multiple analysis sessions:

```python
import requests
import os

DEVIN_API_KEY = os.environ.get('DEVIN_API_KEY')
API_URL = 'https://api.devin.ai/v1/sessions'

def launch_analysis_session(data_file: str, analysis_type: str) -> str:
    """Launch a Devin session for data analysis."""
    
    prompt = f"""
    Analyze the file {data_file} and perform {analysis_type} analysis.
    Generate a report with visualizations and save to reports/{analysis_type}_report.html
    """
    
    response = requests.post(
        API_URL,
        headers={'Authorization': f'Bearer {DEVIN_API_KEY}'},
        json={
            'prompt': prompt,
            'repo_url': 'https://github.com/org/santander-devin-workshop',
            'branch': 'main'
        }
    )
    
    return response.json()['session_id']

# Launch multiple sessions in parallel
sessions = [
    launch_analysis_session('customer_complaints.csv', 'outlier'),
    launch_analysis_session('customer_complaints.csv', 'trend'),
    launch_analysis_session('product_holdings.csv', 'performance')
]
```

### 5.4 Batch Playbooks (3 minutes)

**Demonstration:**

Show how to create reusable playbooks:

```yaml
# playbooks/data_analysis_playbook.yaml
name: Standard Data Analysis Pipeline
description: Automated data analysis workflow for banking data

steps:
  - name: Data Validation
    prompt: |
      Read the input file and validate:
      - Check for missing values
      - Verify data types
      - Identify duplicates
      - Generate validation report

  - name: Statistical Analysis
    prompt: |
      Perform statistical analysis:
      - Descriptive statistics
      - Distribution analysis
      - Correlation analysis
      - Outlier detection

  - name: Visualization
    prompt: |
      Create visualizations:
      - Distribution plots
      - Time series (if applicable)
      - Category breakdowns
      - Save to reports/

  - name: Report Generation
    prompt: |
      Generate HTML report combining:
      - Validation results
      - Statistical findings
      - Visualizations
      - Recommendations
```

### 5.5 GitHub Actions Integration (3 minutes)

**Demonstration:**

Show a GitHub Actions workflow that triggers Devin:

```yaml
# .github/workflows/devin-analysis.yml
name: Automated Data Analysis with Devin

on:
  push:
    paths:
      - 'data/*.csv'
      - 'data/*.xlsx'

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Trigger Devin Analysis
        env:
          DEVIN_API_KEY: ${{ secrets.DEVIN_API_KEY }}
        run: |
          curl -X POST https://api.devin.ai/v1/sessions \
            -H "Authorization: Bearer $DEVIN_API_KEY" \
            -H "Content-Type: application/json" \
            -d '{
              "prompt": "New data files detected. Run standard analysis playbook and create PR with results.",
              "repo_url": "${{ github.repository }}",
              "branch": "${{ github.ref_name }}"
            }'
      
      - name: Wait for Analysis
        run: sleep 300  # Wait for Devin to complete
      
      - name: Check Results
        run: |
          # Check if analysis report was generated
          if [ -f "reports/analysis_report.html" ]; then
            echo "Analysis complete!"
          fi
```

---

## Appendix A: Sample Prompts Reference

### Data Analysis Prompts

```
# Excel Data Extraction
"Read the Excel file at [path] and show me the structure of each sheet including column names, data types, and sample values."

# SQL Generation
"Based on this data structure, generate SQL CREATE TABLE statements and INSERT statements for loading into a PostgreSQL database."

# Data Validation
"Validate this dataset for: missing values, duplicate records, invalid formats, and outliers. Generate a data quality report."

# Query Generation
"Write SQL queries to answer these business questions: [list questions]"
```

### Data Science Prompts

```
# Outlier Detection
"Identify outliers in the [column] using IQR method and Z-score. Visualize the results and explain the findings."

# Pattern Analysis
"Find patterns in customer complaints: repeat complainers, seasonal trends, category correlations."

# Dashboard Creation
"Create a Streamlit dashboard with: KPI metrics, time series chart, category breakdown, and interactive filters."

# Statistical Analysis
"Perform statistical analysis on [dataset]: descriptive stats, distribution analysis, hypothesis testing for [specific question]."
```

### SDLC Prompts

```
# Code Review
"Review this code for: best practices, potential bugs, performance issues, and security concerns."

# Test Generation
"Write comprehensive unit tests for [module] using pytest. Include edge cases and error handling tests."

# Documentation
"Generate API documentation for this module in OpenAPI format."

# CI/CD Setup
"Create a GitHub Actions workflow for: linting, testing, and deploying this Python application."
```

---

## Appendix B: Troubleshooting Guide

### Common Issues and Solutions

**Issue: Devin can't access the S3 bucket**
- Solution: Ensure the bucket has public read access or provide AWS credentials

**Issue: SQLite database locked**
- Solution: Close any other connections to the database

**Issue: Dashboard not loading**
- Solution: Check that all dependencies are installed and the database path is correct

**Issue: Git push fails**
- Solution: Ensure you have write access to the repository

---

## Appendix C: Data Dictionary

### Customers Table

| Column | Type | Description |
|--------|------|-------------|
| customer_id | VARCHAR(10) | Unique customer identifier (SAN######) |
| first_name | VARCHAR(50) | Customer's first name |
| last_name | VARCHAR(50) | Customer's last name |
| email | VARCHAR(100) | Email address |
| phone | VARCHAR(20) | UK phone number |
| date_of_birth | DATE | Date of birth |
| age | INTEGER | Current age (18-85) |
| gender | VARCHAR(10) | Male/Female/Other |
| address | VARCHAR(200) | Street address |
| city | VARCHAR(50) | UK city |
| postcode | VARCHAR(10) | UK postcode |
| account_type | VARCHAR(50) | Account type |
| account_number | VARCHAR(20) | 8-digit account number |
| sort_code | VARCHAR(10) | Sort code (##-##-##) |
| account_open_date | DATE | Account opening date |
| balance | DECIMAL(15,2) | Current balance (GBP) |
| income_bracket | VARCHAR(20) | Income range |
| credit_score | INTEGER | Credit score (300-850) |
| num_products | INTEGER | Number of products held |
| customer_segment | VARCHAR(20) | Premium/Standard Plus/Standard |
| is_active | BOOLEAN | Account active status |
| has_mobile_app | BOOLEAN | Mobile app user |
| has_online_banking | BOOLEAN | Online banking user |
| marketing_consent | BOOLEAN | Marketing consent given |

### Transactions Table

| Column | Type | Description |
|--------|------|-------------|
| transaction_id | VARCHAR(15) | Unique transaction ID (TXN#######) |
| customer_id | VARCHAR(10) | Customer reference |
| transaction_date | DATE | Transaction date |
| transaction_time | TIME | Transaction time |
| transaction_type | VARCHAR(10) | Credit/Debit |
| category | VARCHAR(50) | Transaction category |
| amount | DECIMAL(15,2) | Transaction amount (GBP) |
| currency | VARCHAR(3) | Currency code |
| merchant_name | VARCHAR(100) | Merchant name |
| merchant_category_code | INTEGER | MCC code |
| channel | VARCHAR(20) | Transaction channel |
| location | VARCHAR(50) | Transaction location |
| is_international | BOOLEAN | International transaction |
| is_recurring | BOOLEAN | Recurring transaction |
| status | VARCHAR(20) | Completed/Pending/Failed |

### Complaints Table

| Column | Type | Description |
|--------|------|-------------|
| complaint_id | VARCHAR(15) | Unique complaint ID (CMP######) |
| customer_id | VARCHAR(10) | Customer reference |
| customer_age | INTEGER | Customer age at complaint time |
| customer_gender | VARCHAR(10) | Customer gender |
| customer_segment | VARCHAR(20) | Customer segment |
| customer_city | VARCHAR(50) | Customer city |
| complaint_date | DATE | Complaint date |
| complaint_time | TIME | Complaint time |
| category | VARCHAR(50) | Complaint category |
| severity | VARCHAR(20) | Low/Medium/High/Critical |
| description | TEXT | Complaint description |
| channel | VARCHAR(20) | Complaint channel |
| status | VARCHAR(20) | Open/In Progress/Resolved/Escalated/Closed |
| resolution_date | DATE | Resolution date |
| resolution_days | INTEGER | Days to resolve |
| compensation_amount | DECIMAL(10,2) | Compensation paid (GBP) |
| satisfaction_score | INTEGER | Customer satisfaction (1-5) |
| escalated | BOOLEAN | Was complaint escalated |
| product_involved | VARCHAR(100) | Related product |
| branch_code | VARCHAR(10) | Branch code if applicable |

---

## Appendix D: Persona-Specific Exercises

### Data Analyst Persona

Focus on:
- Excel data extraction and transformation
- SQL query generation and optimization
- Data validation and quality checks
- Report generation

**Additional Exercise:**
```
Create a monthly executive summary report that includes:
- Customer acquisition metrics
- Transaction volume trends
- Top performing products
- Key risk indicators
```

### Data Scientist Persona

Focus on:
- Statistical analysis and hypothesis testing
- Outlier detection and anomaly identification
- Predictive modeling preparation
- Feature engineering

**Additional Exercise:**
```
Prepare features for a customer churn prediction model:
- Calculate recency, frequency, monetary (RFM) scores
- Create behavioral features from transaction data
- Identify risk indicators from complaints data
```

### ML Engineer Persona

Focus on:
- Feature abstraction and pipeline creation
- Model deployment preparation
- API development for model serving
- Monitoring and logging setup

**Additional Exercise:**
```
Create a feature store for the banking data:
- Define feature schemas
- Implement feature computation pipelines
- Set up feature versioning
- Create serving endpoints
```

---

## Post-Workshop Resources

### Documentation Links
- Devin Documentation: https://docs.devin.ai
- Devin API Reference: https://api.devin.ai/docs
- GitHub Actions: https://docs.github.com/en/actions

### Next Steps
1. Practice with your own datasets
2. Create custom playbooks for your team's workflows
3. Integrate Devin into your CI/CD pipelines
4. Explore advanced features (MCP servers, batch processing)

### Support
- Devin Support: support@cognition.ai
- Workshop Materials: [GitHub Repository URL]
- Feedback Form: [Survey Link]

---

**Workshop Created By:** Cognition AI  
**Version:** 1.0  
**Last Updated:** November 2025
