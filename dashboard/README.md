# Complaints Analysis Dashboard

An interactive Streamlit dashboard for analyzing Santander UK customer complaints data, connected to Supabase.

## Features

- **Live Data Connection**: Connects directly to Supabase with 5-minute caching
- **Interactive Filters**: Filter by category, severity, status, date range, and customer segment
- **Dynamic Statistics**: KPI cards that update based on applied filters
- **Interactive Charts**:
  - Time series with daily/weekly/monthly toggle
  - Complaints by category bar chart
  - Severity distribution donut chart
  - Resolution time distribution
- **Outlier Highlights**: Identifies extended resolution times, high compensation, and same-day resolutions
- **Repeat Complainers Analysis**: Customers with 3+ complaints and their patterns

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

3. Run the dashboard:
   ```bash
   streamlit run app.py
   ```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Your Supabase anon/public key |

## Data Requirements

The dashboard expects a `santander_customer_complaints` table in Supabase with the following columns:

- `complaint_id` - Unique complaint identifier
- `customer_id` - Customer identifier
- `category` - Complaint category
- `severity` - Low, Medium, High, or Critical
- `status` - Complaint status
- `complaint_date` - Date of complaint
- `resolution_date` - Date of resolution
- `resolution_days` - Days to resolve
- `compensation_amount` - Compensation paid (e.g., "£100.00")
- `customer_segment` - Customer segment classification
