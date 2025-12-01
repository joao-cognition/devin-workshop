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
Secrets to be provided to participants:
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
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
https://devin-workshop.s3.eu-north-1.amazonaws.com/santander_customers.xlsx
https://devin-workshop.s3.eu-north-1.amazonaws.com/santander_transactions.xlsx
https://devin-workshop.s3.eu-north-1.amazonaws.com/customer_complaints.csv
https://devin-workshop.s3.eu-north-1.amazonaws.com/product_holdings.csv
https://devin-workshop.s3.eu-north-1.amazonaws.com/database_schema.sql
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
```

### For Participants

1. Ensure you have Devin access (app.devin.ai)
2. Have a GitHub account with access to the workshop repository
3. The repository is available within Devin's machine

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
- `customer_complaints.csv` - Contains customer complaints data with outliers and repeat complainers

**Tasks:**
1. Extract and validate data from Excel files
2. Generate SQL INSERT statements for database loading
3. Create analytical queries based on the database schema

### Exercise 2.1: Setting Up the Repository (10 minutes)

**Participant Instructions:**

1. Open Devin at app.devin.ai
2. Start two new sessions with these prompts:

Prompt 1:
```
I need to set up a new Python project for data analysis. Please:

1. Download the Excel file from S3:
   - https://devin-workshop.s3.eu-north-1.amazonaws.com/santander_customers.xlsx
2. Show me the data with pandas
3. Give me a high level summary of the data
```

Prompt 2:
```
I need to set up a new Python project for data analysis. Please:

1. Download the Excel file from S3:
   - https://devin-workshop.s3.eu-north-1.amazonaws.com/santander_transactions.xlsx
2. Show me the data with pandas
3. Give me a high level summary of the data
```

Prompt 3:
```
I need to set up a new Python project for data analysis. Please:

1. Download the Excel file from S3:
   - https://devin-workshop.s3.eu-north-1.amazonaws.com/customer_complaints.csv
2. Show me the data with pandas
3. Give me a high level summary of the data
```

**Expected Devin Actions:**
- Set up Python environment
- Install dependencies
- Download files using aws s3 cp
- Organize project structure

**Discussion Point:** 
- Discuss how Devin automatically sets up proper project structure and dependency management. 
- Discuss parallelisation
- Discuss how Devin doesnt have excel so it finds the best way to open this file with an appropriate python library
- Should be specific, can go multiple paths, html build, show in terminal, find app


### Exercise 2.2: Data Extraction and Validation (10 minutes)

**Participant Instructions:**

Use this prompt with Devin:

```
Please analyze the files in the aws s3 bucket:

1. Read the files in https://devin-workshop.s3.eu-north-1.amazonaws.com/ 
2. Show me the structure of each file (columns, data types, row counts)
3. Identify any data quality issues (missing values, duplicates, invalid formats)
4. Output a data validation report

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

### Exercise 2.3: Creating DB 

Please load the data into a SQLite database:

**Participant Instructions:**

Use this prompt with Devin:

```
1. Create a new SQLite database called santander_bank.db
2. Create tables based on the structure you see in the Excel files
3. Create a script load_data.py to:
3.1. load santander_customers.xlsx into a customers table
3.2. load santander_transactions.xlsx into a transactions table
3.3. load customer_complaints.csv into a customer_complaints table
4. Show me a sample query to verify the data loaded correctly
```     

### Exercise 2.4: SQL Generation (15 minutes)

**Participant Instructions:**

Use this prompt with Devin:

```
Now that we have data in the database, please create analytical queries:

1. Customer demographics by segment (count, avg age, avg balance)
2. Monthly transaction volume by category
3. Top 10 customers by transaction count
4. Average transaction amount by channel

Save these queries to scripts/query_x.sql (individual files) and test them against the database.
```

**Expected Devin Output:**
- SQL scripts in scripts/query_x.sql
- Unit tests for the SQL scripts

**SDLC Integration Point:** 
- Demonstrate how Devin creates a PR with the generated SQL scripts
- Show how to use Devin for code review of the generated SQL
- Discuss unit testing SQL queries

### Exercise 2.5: Commit and Push (5 minutes)

**Participant Instructions:**

```
Please commit the following to GitHub:
- The SQLite database (santander_bank.db)
- The individual analytical queries (scripts/query_x.sql)
- The data loading script (scripts/load_data.py)

Create a PR with a summary of what was created.
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

**Data:**
- `complaints` table in `santander_bank.db` (already loaded)


**Tasks:**
1. Analyze complaints data for outliers and patterns
2. Identify repeat complainers
3. Create an interactive dashboard with multiple views
   - Descriptive statistics table
   - Time series graph
   - Bar chart
   - Filter dropdowns

### Exercise 4.1: SQLite Database Setup (10 minutes)

**Participant Instructions:**

```
Using the santander_bank.db database we created earlier, please:

1. Verify the complaints table exists and show me its structure
2. Show me summary statistics for the complaints table
3. Run a few sample queries to understand the data
```

**SDLC Integration Point:** Discuss unit testing with Devin - show how to ask Devin to write pytest tests.

### Exercise 4.2: Outlier and Repeat Complainer Analysis (15 minutes)

**Participant Instructions:**

```
Using the complaints table, please:

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

## Section 5: Advanced Devin Capabilities (15 minutes)

### 5.1 Knowledge (3 minutes)

**Demonstration:**

Show how to provide Devin with coding guidelines:

**Pre-prompt:**

```
Please follow these coding guidelines for all code you write.
```

**Knowledge:**

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

### 5.2 Unit Testing

**Demonstration:**

```
Please write unit tests for the load_data.py script using pytest. Include:
- Test for successful database creation
- Test for data loading with valid CSV
- Test for handling missing columns
- Test for handling empty CSV
```


### 5.3 Devin API (3 mins)

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

### 5.4 Playbooks

**Demonstration:**

Show how to create reusable playbooks:

```
!standard_analysis_playbook

# **Data Analysis Pipeline — Detailed Sequence of Events**

## **1. Load & Validate Input Data**

1. Read the input file (CSV, XLSX, or Parquet).
2. Confirm the file is readable and not empty.
3. Validate column names against the expected schema.
4. Check each column for:

   * Missing values (count + percentage)
   * Incorrect data types (e.g., string instead of int)
   * Unexpected categorical values
5. Identify duplicate rows and duplicated primary keys.
6. Generate a **data validation report** containing:

   * Schema mismatches
   * Missing-value summary
   * Duplicate summary
   * Data type inconsistencies

---

## **2. Perform Statistical Analysis**

1. Calculate descriptive statistics (mean, median, mode, std, min, max).
2. Compute distribution metrics (skewness, kurtosis).
3. Generate correlation matrix for all numeric variables.
4. Detect outliers using:

   * Z-score
   * IQR (Interquartile Range)
5. Document statistically significant relationships or anomalies.

---

## **3. Create Visualizations**

1. Plot distribution charts for:

   * Numeric columns (histograms, KDE plots)
   * Categorical columns (bar charts)
2. If dataset includes timestamps:

   * Create time-series plots with trend lines
3. Produce scatterplots for high-correlation variable pairs.
4. Highlight outliers visually.
5. Save all charts to `reports/visuals/` as PNG or SVG.

---

## **4. Generate Consolidated Report**

1. Compile all validation results (tables + summaries).
2. Insert statistical analysis findings with interpretations.
3. Embed visualizations with captions.
4. Add actionable insights and data quality recommendations.
5. Export a final **HTML report** to `reports/analysis_report.html`.
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
              "prompt": "New data files detected. Run !standard_analysis_playbook and create PR with results.",
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
