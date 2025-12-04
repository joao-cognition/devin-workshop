"""
Interactive Complaints Dashboard with Supabase Connection.

This Streamlit dashboard provides real-time analysis of customer complaints
with filtering, dynamic statistics, and interactive charts.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from supabase import create_client, Client

SUPABASE_URL = "https://nvpgcrcvrouihxsakovx.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im52cGdjcmN2cm91aWh4c2Frb3Z4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ3OTIyNjEsImV4cCI6MjA4MDM2ODI2MX0.JXZUirdsnvxp6UWZznATkFcVVYv-EnmTH6FjsYMD0ZI"

st.set_page_config(
    page_title="Complaints Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #ec0000;
        margin-bottom: 1rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #ec0000 0%, #b30000 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .outlier-card {
        border-left: 4px solid #ec0000;
        padding: 1rem;
        background: #f8f9fa;
        margin-bottom: 0.5rem;
        border-radius: 0 8px 8px 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_supabase_client() -> Client:
    """Initialize and return Supabase client."""
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


@st.cache_data(ttl=300)
def load_complaints_data() -> pd.DataFrame:
    """
    Load complaints data from Supabase with caching.
    
    Returns:
        DataFrame containing all complaints data.
    """
    supabase = get_supabase_client()
    response = supabase.table("santander_customer_complaints").select("*").execute()
    
    if response.data:
        df = pd.DataFrame(response.data)
        if "complaint_date" in df.columns:
            df["complaint_date"] = pd.to_datetime(df["complaint_date"])
        if "compensation_amount" in df.columns:
            df["compensation_amount"] = pd.to_numeric(
                df["compensation_amount"], errors="coerce"
            ).fillna(0)
        return df
    return pd.DataFrame()


def calculate_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate summary statistics from complaints data.
    
    Args:
        df: DataFrame containing complaints data.
        
    Returns:
        Dictionary with calculated statistics.
    """
    if df.empty:
        return {
            "total": 0,
            "avg_resolution": 0,
            "median_resolution": 0,
            "total_compensation": 0,
            "avg_compensation": 0,
            "repeat_complainers": 0
        }
    
    resolution_days = df["resolution_days"].fillna(0)
    compensation = df["compensation_amount"].fillna(0)
    
    customer_counts = df["customer_id"].value_counts()
    repeat_complainers = (customer_counts >= 3).sum()
    
    return {
        "total": len(df),
        "avg_resolution": resolution_days.mean(),
        "median_resolution": resolution_days.median(),
        "total_compensation": compensation.sum(),
        "avg_compensation": compensation.mean(),
        "repeat_complainers": repeat_complainers
    }


def get_time_series_data(
    df: pd.DataFrame, 
    granularity: str
) -> pd.DataFrame:
    """
    Aggregate complaints by time period.
    
    Args:
        df: DataFrame containing complaints data.
        granularity: Time granularity ('Daily', 'Weekly', 'Monthly').
        
    Returns:
        DataFrame with time series aggregation.
    """
    if df.empty or "complaint_date" not in df.columns:
        return pd.DataFrame()
    
    df_copy = df.copy()
    
    if granularity == "Daily":
        df_copy["period"] = df_copy["complaint_date"].dt.date
    elif granularity == "Weekly":
        df_copy["period"] = df_copy["complaint_date"].dt.to_period("W").dt.start_time.dt.date
    else:
        df_copy["period"] = df_copy["complaint_date"].dt.to_period("M").dt.start_time.dt.date
    
    time_series = df_copy.groupby("period").agg(
        count=("complaint_id", "count"),
        avg_compensation=("compensation_amount", "mean")
    ).reset_index()
    
    time_series["period"] = pd.to_datetime(time_series["period"])
    return time_series.sort_values("period")


def get_category_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get complaint counts and average compensation by category.
    
    Args:
        df: DataFrame containing complaints data.
        
    Returns:
        DataFrame with category breakdown.
    """
    if df.empty:
        return pd.DataFrame()
    
    breakdown = df.groupby("category").agg(
        count=("complaint_id", "count"),
        avg_compensation=("compensation_amount", "mean"),
        avg_resolution=("resolution_days", "mean")
    ).reset_index()
    
    return breakdown.sort_values("count", ascending=False)


def get_outliers(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Identify outlier complaints.
    
    Args:
        df: DataFrame containing complaints data.
        
    Returns:
        Dictionary with outlier DataFrames.
    """
    return {
        "long_resolution": df[df["resolution_days"] > 60].nlargest(
            10, "resolution_days"
        ),
        "high_compensation": df[df["compensation_amount"] > 300].nlargest(
            10, "compensation_amount"
        ),
        "zero_day": df[df["resolution_days"] == 0].head(10)
    }


def get_repeat_complainers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify customers with 3+ complaints.
    
    Args:
        df: DataFrame containing complaints data.
        
    Returns:
        DataFrame with repeat complainer details.
    """
    if df.empty:
        return pd.DataFrame()
    
    customer_stats = df.groupby("customer_id").agg(
        complaint_count=("complaint_id", "count"),
        categories=("category", lambda x: list(set(x))),
        total_compensation=("compensation_amount", "sum"),
        avg_resolution=("resolution_days", "mean")
    ).reset_index()
    
    repeat = customer_stats[customer_stats["complaint_count"] >= 3]
    return repeat.sort_values("complaint_count", ascending=False).head(10)


def main():
    """Main dashboard application."""
    st.markdown('<p class="main-header">Santander Complaints Dashboard</p>', unsafe_allow_html=True)
    
    with st.spinner("Loading data from Supabase..."):
        df = load_complaints_data()
    
    if df.empty:
        st.error("No data available. Please check the Supabase connection.")
        return
    
    st.sidebar.header("Filters")
    
    if st.sidebar.button("Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    categories = ["All"] + sorted(df["category"].dropna().unique().tolist())
    selected_category = st.sidebar.selectbox("Category", categories)
    
    severities = ["All"] + sorted(df["severity"].dropna().unique().tolist())
    selected_severity = st.sidebar.selectbox("Severity", severities)
    
    statuses = ["All"] + sorted(df["status"].dropna().unique().tolist())
    selected_status = st.sidebar.selectbox("Status", statuses)
    
    segments = ["All"] + sorted(df["customer_segment"].dropna().unique().tolist())
    selected_segment = st.sidebar.selectbox("Customer Segment", segments)
    
    st.sidebar.subheader("Date Range")
    min_date = df["complaint_date"].min().date()
    max_date = df["complaint_date"].max().date()
    
    date_from = st.sidebar.date_input("From", min_date, min_value=min_date, max_value=max_date)
    date_to = st.sidebar.date_input("To", max_date, min_value=min_date, max_value=max_date)
    
    filtered_df = df.copy()
    
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df["category"] == selected_category]
    if selected_severity != "All":
        filtered_df = filtered_df[filtered_df["severity"] == selected_severity]
    if selected_status != "All":
        filtered_df = filtered_df[filtered_df["status"] == selected_status]
    if selected_segment != "All":
        filtered_df = filtered_df[filtered_df["customer_segment"] == selected_segment]
    
    filtered_df = filtered_df[
        (filtered_df["complaint_date"].dt.date >= date_from) &
        (filtered_df["complaint_date"].dt.date <= date_to)
    ]
    
    stats = calculate_stats(filtered_df)
    
    st.subheader("Key Metrics")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("Total Complaints", f"{stats['total']:,}")
    with col2:
        st.metric("Avg Resolution", f"{stats['avg_resolution']:.1f} days")
    with col3:
        st.metric("Median Resolution", f"{stats['median_resolution']:.1f} days")
    with col4:
        st.metric("Total Compensation", f"£{stats['total_compensation']:,.2f}")
    with col5:
        st.metric("Avg Compensation", f"£{stats['avg_compensation']:.2f}")
    with col6:
        st.metric("Repeat Complainers", f"{stats['repeat_complainers']}")
    
    st.markdown("---")
    
    st.subheader("Complaints Over Time")
    granularity = st.radio(
        "Time Granularity",
        ["Daily", "Weekly", "Monthly"],
        horizontal=True,
        index=1
    )
    
    time_series = get_time_series_data(filtered_df, granularity)
    
    if not time_series.empty:
        fig_time = px.line(
            time_series,
            x="period",
            y="count",
            title=f"Complaints ({granularity})",
            labels={"period": "Date", "count": "Number of Complaints"}
        )
        fig_time.update_traces(line_color="#ec0000", line_width=2)
        fig_time.update_layout(
            hovermode="x unified",
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.info("No time series data available for the selected filters.")
    
    st.markdown("---")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Complaints by Category")
        category_data = get_category_breakdown(filtered_df)
        
        if not category_data.empty:
            fig_cat = px.bar(
                category_data,
                x="count",
                y="category",
                orientation="h",
                title="Category Distribution",
                labels={"count": "Number of Complaints", "category": "Category"},
                color="avg_compensation",
                color_continuous_scale=["#ffcccc", "#ec0000", "#8b0000"]
            )
            fig_cat.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                yaxis={"categoryorder": "total ascending"}
            )
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("No category data available.")
    
    with col_right:
        st.subheader("Severity Distribution")
        if not filtered_df.empty:
            severity_counts = filtered_df["severity"].value_counts().reset_index()
            severity_counts.columns = ["severity", "count"]
            
            fig_sev = px.pie(
                severity_counts,
                values="count",
                names="severity",
                title="Complaints by Severity",
                color_discrete_sequence=["#ec0000", "#ff6666", "#ffcccc", "#8b0000"]
            )
            fig_sev.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_sev, use_container_width=True)
        else:
            st.info("No severity data available.")
    
    st.markdown("---")
    
    st.subheader("Resolution Time Distribution")
    if not filtered_df.empty:
        bins = [0, 1, 7, 14, 30, 60, float("inf")]
        labels = ["0 days", "1-7 days", "8-14 days", "15-30 days", "31-60 days", "60+ days"]
        filtered_df["resolution_bucket"] = pd.cut(
            filtered_df["resolution_days"],
            bins=bins,
            labels=labels,
            include_lowest=True
        )
        
        resolution_dist = filtered_df["resolution_bucket"].value_counts().reset_index()
        resolution_dist.columns = ["bucket", "count"]
        resolution_dist = resolution_dist.sort_values(
            "bucket",
            key=lambda x: pd.Categorical(x, categories=labels, ordered=True)
        )
        
        fig_res = px.bar(
            resolution_dist,
            x="bucket",
            y="count",
            title="Resolution Time Distribution",
            labels={"bucket": "Resolution Time", "count": "Number of Complaints"},
            color="count",
            color_continuous_scale=["#ffcccc", "#ec0000"]
        )
        fig_res.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            showlegend=False
        )
        st.plotly_chart(fig_res, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("Outlier Analysis")
    outliers = get_outliers(filtered_df)
    
    tab1, tab2, tab3 = st.tabs([
        "Long Resolution (>60 days)",
        "High Compensation (>£300)",
        "Zero-Day Resolution"
    ])
    
    with tab1:
        if not outliers["long_resolution"].empty:
            st.dataframe(
                outliers["long_resolution"][[
                    "complaint_id", "customer_id", "category",
                    "severity", "resolution_days", "compensation_amount"
                ]].head(10),
                use_container_width=True
            )
        else:
            st.info("No long resolution outliers found.")
    
    with tab2:
        if not outliers["high_compensation"].empty:
            st.dataframe(
                outliers["high_compensation"][[
                    "complaint_id", "customer_id", "category",
                    "severity", "resolution_days", "compensation_amount"
                ]].head(10),
                use_container_width=True
            )
        else:
            st.info("No high compensation outliers found.")
    
    with tab3:
        if not outliers["zero_day"].empty:
            st.dataframe(
                outliers["zero_day"][[
                    "complaint_id", "customer_id", "category",
                    "severity", "resolution_days", "compensation_amount"
                ]].head(10),
                use_container_width=True
            )
        else:
            st.info("No zero-day resolution cases found.")
    
    st.markdown("---")
    
    st.subheader("Repeat Complainers (3+ complaints)")
    repeat_complainers = get_repeat_complainers(filtered_df)
    
    if not repeat_complainers.empty:
        for _, row in repeat_complainers.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="outlier-card">
                    <strong>{row['customer_id']}</strong> - {row['complaint_count']} complaints<br>
                    Categories: {', '.join(row['categories'][:3])}{'...' if len(row['categories']) > 3 else ''}<br>
                    Total Compensation: £{row['total_compensation']:.2f} | 
                    Avg Resolution: {row['avg_resolution']:.1f} days
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No repeat complainers found in the filtered data.")
    
    st.markdown("---")
    st.caption(
        f"Data source: Supabase | "
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"Showing {len(filtered_df):,} of {len(df):,} complaints"
    )


if __name__ == "__main__":
    main()
