# Santander UK Data Analysis & Data Science Workshop with Devin

## 2-Hour Hands-On Workshop Guide

**Target Audience:** Data Analysis and Data Science Teams at Bank Santander UK  
**Duration:** 2 hours  
**Format:** Hands-on workshop with participants using their own laptops  
**Prerequisites:** Devin access, GitHub account

---

## Workshop Overview

This workshop demonstrates how Devin accelerates data analysis workflows through natural language prompts—from extracting data from Excel files to building interactive dashboards. Participants will learn to work with Devin using focused prompts, create reproducible playbooks, and integrate Devin into automated workflows via API and CI/CD.

### Learning Objectives

By the end of this workshop, participants will be able to:

1. Write effective prompts for data extraction, transformation, and SQL generation
2. Use Devin for data science tasks: outlier detection, pattern analysis, and visualization
3. Create reproducible playbooks for daily analysis workflows
4. Build interactive dashboards with live database connections
5. Understand Devin API integration and CI/CD automation patterns
6. Review AI-generated PRs and analyze session insights

---

## Pre-Workshop Setup

### For Workshop Facilitators

**Environment Preparation Checklist:**

**1. S3 Bucket Configuration**
- [ ] Verify access to S3 bucket: `s3://devin-workshop/santander-workshop/`
- [ ] Ensure AWS credentials are configured in Devin secrets
- [ ] Test access to data files and schema files in the bucket

**2. Repository Setup**
- [ ] Repository: `joao-cognition/devin-workshop`
- [ ] Enable repository indexing in Devin
- [ ] Enable DeepWiki for repository documentation

**3. Secrets Configuration**
Add the following secrets to Devin:
- [ ] `AWS_ACCESS_KEY_ID` - For S3 bucket access (eu-north-1 region)
- [ ] `AWS_SECRET_ACCESS_KEY` - For S3 bucket access
- [ ] `DEVIN_API_KEY` - For API integration demos

**4. Knowledge Base Setup**
Add the following knowledge documents:
- [ ] `data-quality-guidelines` - Data quality assessment standards
- [ ] `coding-guidelines` - Santander coding standards (from `docs/coding_guidelines.md`)

**5. Playbooks Setup**
Configure the following playbooks:
- [ ] `elastic` - Elasticsearch integration playbook
- [ ] `s3-data-analysis` - S3 data extraction and analysis playbook

**6. Data Files Location**

All dummy data files are available in the S3 bucket:
```
Region: eu-north-1
Bucket: s3://devin-workshop/santander-workshop/
Console: eu-north-1.console.aws.amazon.com/s3/buckets/devin-workshop
```

Files included:
- `santander_customers.xlsx` - Customer demographics and account information
- `santander_transactions.xlsx` - Transaction history with category summaries
- `customer_complaints.csv` - Complaints data with outliers and repeat complainers
- `product_holdings.csv` - Product metrics for bubble chart analysis
- `schema.sql` - Database schema definition for creating local SQLite database

### For Participants

1. Ensure you have Devin access (app.devin.ai)
2. Have a GitHub account with access to the workshop repository
3. Verify AWS credentials are configured for S3 access

---

## Workshop Agenda

| Time | Duration | Section | Focus |
|------|----------|---------|-------|
| 0:00 | 10 min | Introduction | Workshop overview, Devin capabilities |
| 0:10 | 40 min | Use Case 1 | Data Analysis |
| 0:50 | 10 min | Break | - |
| 1:00 | 15 min | Use Case 2 | Data Science & Dashboard |
| 1:15 | 30 min | SDLC Deep Dive | API & CI/CD Demo (during dashboard build) |
| 1:45 | 15 min | Q&A | - |

---

## Section 1: Introduction (10 minutes)

### 1.1 Welcome and Context Setting (5 minutes)

**Facilitator Script:**

Today, we'll work through two realistic banking scenarios:
1. Extracting customer and transaction data from Excel files and generating SQL queries
2. Analyzing customer complaints data to identify outliers and repeat complainers, then building a dashboard


### 1.2 Devin vs AI IDE (5 minutes)

**Key Differences from AI IDEs (like Windsurf):**

**AI IDEs:** Local, synchronous, 1:1 dev-to-editor relationship  
**Devin:** Remote cloud agent, asynchronous, 1 dev can run multiple sessions in parallel

**Analogy:** Devin works like a Junior Software Engineer—you spend 5 minutes explaining the task, then they return with a PR to review or a follow-up question

### 1.3 Housekeeping (0 minutes)

---

## Section 2: Data Analysis Use Case (40 minutes)

### Scenario Overview

**Business Context:** The Data Analysis team needs to extract data from S3, build a local database, assess data quality using organizational standards, and run multiple analytical queries efficiently to support business decisions.

**Data Source:** S3 bucket (eu-north-1) containing:
- Customer demographics and account information (Excel)
- Transaction history with merchant and category data (Excel)
- Customer complaints data (CSV)
- Product holdings and performance metrics (CSV)
- Database schema definition (SQL)

**Tasks:**
1. Fetch data files and schema from S3 bucket
2. Build a local SQLite database from the schema and data
3. Assess data quality using standardized guidelines
4. Run analytical queries for different business questions
5. Consolidate insights into actionable reports

### Exercise 2.1: Fetch Data from S3 and Build Database (10 minutes)

**Instructor Demo (3 minutes):**

**Participant Instructions:**

1. Open Devin at app.devin.ai
2. Start a new session with this prompt:

```
Fetch all data files from the S3 bucket s3://devin-workshop/santander-workshop/ (region: eu-north-1):
- santander_customers.xlsx
- santander_transactions.xlsx
- customer_complaints.csv
- product_holdings.csv
- schema.sql
```

```
1. Create a local SQLite database using the schema.sql file
2. Load all the data files into the appropriate tables
3. List for each table:
   - The schema
   - The table name
   - A brief description of what the table contains
   - Some relevant data samples to highlight the table structure
```

**Show what is happening:**
- Secure data access: Fetch data from S3 using AWS credentials stored in Devin secrets
- Database creation: Build a local SQLite database for fast querying
- Data loading: Parse Excel and CSV files and populate the database
- Schema exploration: Understand table structures, relationships, and data types
- Query execution: Run SQL against the local database
- Results formatting: Display query outputs in various formats (tables, charts, JSON)

### Exercise 2.2: Parallel Analytical Queries (15 minutes)

**Participant Instructions:**

Now we'll demonstrate Devin's ability to work on multiple tasks simultaneously. 
Start **4 separate Devin sessions** with these prompts:

**Session 1:**
```
Using !fetching-santander-data analyze customer demographics by segment (count, avg age, avg balance). Show me a written summary.
```

**Session 2:**
```
Using !fetching-santander-data, analyze monthly transaction volume by category. Show me a table.
```

**Session 3:**
```
Using !fetching-santander-data, find top 10 customers by transaction count. Show me a graph.
```

**Session 4:**
```
Using !fetching-santander-data, analyze average transaction amount by channel. Show me a json.
```

**Parallelization:**
All 4 sessions run simultaneously, dramatically reducing wait time

### Exercise 2.3: Data Quality Assessment with System Knowledge (15 minutes)

**Participant Instructions:**

Now use this prompt with Devin - in the original session

```
Using the data !data-quality-guidelines analyse the tables in the local SQLite database you just created.
```

**Knowledge:**
- Use system knowledge to provide guidelines to analyse data quality
- Devin can apply your team's specific quality standards
- The report format can be customized (terminal, markdown, HTML, etc.)
- Data quality report showing:
  - Completeness metrics per table
  - Duplicate analysis
  - Format validation results
  - Statistical outlier detection

**Check if Data Quality is over:**
- If yes review, if not start parallel sessions

**Playbooks:**
How you can leverage this to execute tasks in a concrete and repeatable way—every time there is new data, once a day to keep reports up to date. Create a playbook from these 4 sessions.

**Show Flow Schematic:**
Demonstrate how the SQL queries get created and returned to the user


**Break:**
Do a small break


## Section 3: Break (10 minutes)

---

## Section 4: Data Science Use Case (15 minutes)

### Scenario Overview

**Business Context:** The Data Science team needs to analyze customer complaints data to identify patterns, outliers, and repeat complainers. They also need to create a dashboard for ongoing monitoring.

**Data:**
- Customer complaints data from S3 bucket (will be fetched and loaded into local database)


**Tasks:**
1. Fetch complaints data from S3 and build local database
2. Analyze complaints data for outliers and patterns
3. Identify repeat complainers
4. Create an interactive dashboard with multiple views
   - Descriptive statistics table
   - Time series graph
   - Bar chart
   - Filter dropdowns

### Exercise 4.1: Complaints Data Analysis (5 minutes)

**Prompt for Participants:**

```
Fetch customer_complaints.csv using !fetching-santander-data and show me:
- Outliers: complaints with resolution times > 60 days, compensation > £300, or 0-day resolution
- Repeat complainers: customers with 3+ complaints and their patterns
- Statistical summary: resolution time distribution, compensation stats, and category breakdown
```

**Devin Playbook Expert:**
- Demonstrate creating a playbook: "Create a playbook document in docs/ that captures this analysis workflow so we can rerun it daily"
- Discuss how playbooks enable reproducible data science workflows
- Show how Devin documents its approach for future automation


---

### Exercise 4.2: Static HTML Dashboard (5 minutes)

**Prompt for Participants:**

```
Using the complaints data from the local SQLite database, create a static HTML dashboard showing the analysis results. Include:
- Summary statistics table
- Time series chart of complaints over time
- Bar chart of complaints by category
- Outlier highlights section
```

---

### Exercise 4.3: Interactive Dashboard (5 minutes)

**Prompt for Participants:**

```
Upgrade the dashboard to an interactive app that can fetch fresh data from S3 on demand. Add:
- Data refresh capability: fetch latest data from S3 bucket s3://devin-workshop/santander-workshop/ (region: eu-north-1)
- Filter dropdowns: category, severity, status, date range, customer segment
- Dynamic statistics that update with filters
- Interactive charts: time series (daily/weekly/monthly toggle) and category breakdown

When complete, create a PR in a completely separate folder in @santander-group-uk-gln/suk-digird1-devinfrontend and deploy to a link I can access.
```

**Note:** While this dashboard builds (~15-20 minutes), move to Section 5 for the SDLC Deep Dive demo.

---

## Section 5: SDLC Deep Dive - API & CI/CD Integration (30 minutes: 1:15-1:45)

**Timing Note:** This section begins while the interactive dashboard builds in the background (Exercise 4.3).

**Business Context:** Your team wants to automate code quality checks using Devin API. You'll integrate Devin into your SDLC to automatically analyze security threats, performance issues, and errors in new code files.

---

### Devin API Generation

**Understanding API Key Types:**
- **Personal API Keys:** Individual developer access, tied to your account
- **Company API Keys:** Team-wide access, managed by organization admins

**Create API Key:**
1. Go to Devin Settings → API Keys
2. Click "Create New Key"
3. Choose scope: Personal or Company
4. Copy and securely store the key

**Best Practice:** Store in environment variables, never commit to git

```bash
export DEVIN_API_KEY="your-api-key-here"
```

---

### Launching API from Locally

**Show Devin API Documentation:**
- Navigate to https://api.devin.ai/docs
- API endpoint: `https://api.devin.ai/v1/sessions`
- Authentication headers
- Request/response format

**Show Elastic Logs File:**
- Display `data/elastic_logs_security.json` with security threats, performance issues, and errors

**Run Three Parallel Sessions:**

Launch 3 Devin sessions in parallel with these prompts:

**Prompt 1 - Security Analysis:**
**Prompt 2 - Performance Analysis:**
**Prompt 3 - Error Analysis:**

**Show Results Sessions Running:**

Display one of the analysis results showing the parallel execution

**Key Takeaway:** Parallel execution saves time—3 analyses complete in the time of 1

---

### Launching CI/CD for New Files

**Add API Secret to GitHub:**
1. Repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `DEVIN_API_KEY`
4. Value: [paste API key]
5. Save

**Alternative:** GitHub App integration for organization-wide access

**Create GitHub Actions Workflow:**

Prompt Devin to create the workflow:


**Test the CI/CD Pipeline:**

1. Commit a new test file to `data/`
2. Push to GitHub
3. Watch Actions tab for workflow execution
4. Show parallel job execution
5. Review results in PR comments

**Key Takeaway:** Automated code quality checks on every commit, no manual intervention

---

### Launching CI/CD for New Files with Playbook

**Problem:** Hard-coded analysis rules in GitHub Actions are difficult to maintain and update

**Solution:** Separate concerns using Playbooks
- **GitHub Actions:** Manages API calls and CI/CD orchestration
- **Playbooks:** Contains analysis logic, rules, and prompts
- **Benefits:** Update analysis rules without touching CI/CD code

**Create Playbook:**


**Update GitHub Actions to Use Playbook:**

Modify workflow to reference the playbook:


**Show Full CI/CD Pipeline:**



**Key Takeaway:** Playbooks make your SDLC automation maintainable and scalable

---

### Section 5 Wrap-Up

**What We Covered:**
- Devin API authentication (personal vs company keys)
- Local API testing with parallel sessions
- GitHub Actions CI/CD integration
- Playbook-driven workflows for maintainability

**Real-World Impact:**
- Automated code quality checks on every commit
- 3x faster analysis with parallel execution
- Easy rule updates without touching CI/CD code
- Consistent, repeatable analysis across your team

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
