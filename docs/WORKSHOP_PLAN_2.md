# Santander UK Workshop with Devin
## 2-Hour Hands-On Session

---

## 📦 Data Location

**S3 Bucket:**
- Region: `eu-north-1`
- Bucket: `s3://devin-workshop/santander-workshop/`
- Console: `eu-north-1.console.aws.amazon.com/s3/buckets/devin-workshop`

---

## 1️⃣ Introduction (10 min)

### Devin vs AI IDE
- **AI IDEs:** Local, synchronous, 1:1 relationship
- **Devin:** Remote cloud agent, asynchronous, parallel sessions

### Housekeeping
- Access check
- Questions format

---

## 2️⃣ Data Analysis Use Case (40 min)

### 🎯 Demo 1: Fetch Data & Build Database

**Show flow DeepWiki->AskDevin->Devin Sessions**

**Show S3 bucket contents**

**Prompt:**
```
Fetch all data files from the S3 bucket s3://devin-workshop/santander-workshop/ (region: eu-north-1):
- santander_customers.xlsx
- santander_transactions.xlsx
- customer_complaints.csv
- product_holdings.csv
- schema.sql

1. Create a local SQLite database using the schema.sql file
2. Load all the data files into the appropriate tables
3. List for each table:
   - The schema
   - The table name
   - A brief description of what the table contains
   - Some relevant data samples to highlight the table structure
```

**While running, explain:**
- Show Devin improve prompt feature
- Explain Devin's Machine concept
- Go through setup in `santander-group-uk-gln/suk-digird1-devinjava`
- Explain MCP not enabled yet → fetch files directly
- Start DB running locally within Devin's Machine
- Go through the secrets configuration



---

### 🎯 Demo 2: Parallel Analytical Queries (15 min)

**Demonstrate Devin's parallel execution**

**Launch 4 separate sessions:**

**Explain Knowledge feature:**
- Show `!fetching-santander-data` knowledge


**Session 1 - Written Summary:**
```
Using !fetching-santander-data analyze customer demographics by segment 
(count, avg age, avg balance). Show me a written summary.
```

**Session 2 - Table Output:**
```
Using !fetching-santander-data, analyze monthly transaction volume by category. 
Show me a table.
```

**Session 3 - Graph Output:**
```
Using !fetching-santander-data, find top 10 customers by transaction count. 
Show me a graph.
```

**Session 4 - JSON Output:**
```
Using !fetching-santander-data, analyze average transaction amount by channel. 
Show me a json.
```



**Key Point:** All 4 sessions run simultaneously → dramatically reduced wait time


---

### 🎯 Demo 3: Data Quality Assessment (15 min)

**Show knowledge feature in detail:**
- Show `!data-quality-guidelines` knowledge
- Run data quality check on first query

**When ready, prompt:**
```
Using the data !data-quality-guidelines analyse the tables in the 
local SQLite database you just created.
```

**Explain Playbooks:**
- These 4 sessions could run sequentially instead
- Execute analysis repetitively (daily, on new data)
- Create playbook from these 4 sessions
- Concrete and repeatable workflows

**Show Flow Schematic:**
- Final architecture once MCPs are enabled
- How SQL queries get created and returned

---

### ☕ Break Time

---

## 3️⃣ Break (10 min)

---

## 4️⃣ Data Science Use Case (15 min)

### 🎯 Demo 4: Complaints Analysis

**⚠️ Show pre-run session (ran during break)**

**Prompt used:**
```
Fetch customer_complaints.csv using !fetching-santander-data and show me:
- Outliers: complaints with resolution times > 60 days, compensation > £300, or 0-day resolution
- Repeat complainers: customers with 3+ complaints and their patterns
- Statistical summary: resolution time distribution, compensation stats, and category breakdown
```

**Explain Playbook Expert:**
- Demonstrate: "Improve my playbook to run this analysis too"
- Playbooks enable reproducible data science workflows
- Devin documents approach for future automation
- Show pre-run version (takes too long live)

---

### 🎯 Demo 5: Static HTML Dashboard

**Run on top of previous session:**
```
Using the complaints data create a static HTML dashboard showing the analysis results. Include:
- Summary statistics table
- Time series chart of complaints over time
- Bar chart of complaints by category
- Outlier highlights section
```

**Show browser visualization:**
- What Devin uses to build
- Live preview capability

---

### 🎯 Demo 6: Interactive Dashboard

**Final upgrade prompt:**
```
Upgrade the dashboard to an interactive app that can:
- Filter dropdowns: category, severity, status, date range, customer segment
- Dynamic statistics that update with filters
- Interactive charts: time series (daily/weekly/monthly toggle) and category breakdown

When complete, create a PR in a completely separate folder in 
@santander-group-uk-gln/suk-digird1-devinfrontend and deploy to a link I can access.
```

**⏱️ Note:** This builds in background (~15-20 min) → Move to Section 5

---

## 5️⃣ SDLC Deep Dive - API & CI/CD (30 min)

**⏱️ Timing:** Runs while interactive dashboard builds in background

**Context:** Automate code quality checks using Devin API

---

### 🎯 Demo 7: Devin API Generation

**API Key Types:**
- **Personal:** Individual developer access
- **Company:** Team-wide access, org-managed

**Create API Key steps:**
1. Devin Settings → API Keys
2. Click "Create New Key"
3. Choose scope: Personal or Company
4. Copy and store securely

**Best Practice:**
```bash
export DEVIN_API_KEY="your-api-key-here"
```
Never commit to git!

---

### 🎯 Demo 8: Launch API Locally

**Show API Documentation:**
- Navigate to `https://api.devin.ai/docs`
- Endpoint: `https://api.devin.ai/v1/sessions`
- Authentication headers
- Request/response format

**Show Elastic Logs File:**
- Display `data/elastic_logs_security.json`
- Contains: security threats, performance issues, errors

**Launch 3 Parallel Sessions:**
- **Prompt 1:** Security Analysis
- **Prompt 2:** Performance Analysis
- **Prompt 3:** Error Analysis

**Show Results:**
- Display one analysis result
- Highlight parallel execution

**💡 Key Takeaway:** 3 analyses complete in time of 1

---

### 🎯 Demo 9: CI/CD for New Files

**Add API Secret to GitHub:**
1. Repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `DEVIN_API_KEY`
4. Value: [paste API key]
5. Save

**Alternative:** GitHub App integration (org-wide)

**Create GitHub Actions Workflow:**
- Prompt Devin to create workflow

**Test the Pipeline:**
1. Commit new test file to `data/`
2. Push to GitHub
3. Watch Actions tab
4. Show parallel job execution
5. Review PR comments

**💡 Key Takeaway:** Automated checks on every commit, zero manual work

---

### 🎯 Demo 10: CI/CD with Playbook

**Problem:** Hard-coded rules = difficult to maintain

**Solution: Playbooks**
- **GitHub Actions:** API calls + CI/CD orchestration
- **Playbooks:** Analysis logic, rules, prompts
- **Benefits:** Update rules without touching CI/CD

**Steps:**
1. Create Playbook
2. Update GitHub Actions to reference playbook
3. Show Full CI/CD Pipeline

**💡 Key Takeaway:** Maintainable and scalable SDLC automation

---

## 🎬 Wrap-Up

### What We Covered:
- ✅ Devin API authentication (personal vs company)
- ✅ Local API testing with parallel sessions
- ✅ GitHub Actions CI/CD integration
- ✅ Playbook-driven workflows

### Real-World Impact:
- 🚀 Automated code quality checks on every commit
- ⚡ 3x faster analysis with parallel execution
- 🔧 Easy rule updates without touching CI/CD
- 🔄 Consistent, repeatable analysis across teams

---

## 📚 Post-Workshop Resources

### Documentation
- **Devin Docs:** `https://docs.devin.ai`
- **API Reference:** `https://api.devin.ai/docs`
- **GitHub Actions:** `https://docs.github.com/en/actions`

### Next Steps
1. 🧪 Practice with your own datasets
2. 📝 Create custom playbooks for your workflows
3. 🔗 Integrate Devin into CI/CD pipelines
4. 🚀 Explore advanced features (MCP servers, batch processing)

### Support
- 💬 **Devin Support:** support@cognition.ai
- 📂 **Workshop Materials:** [GitHub Repository URL]
- 📋 **Feedback Form:** [Survey Link]

---

**Workshop by Cognition AI** | Version 1.0 | November 2025
