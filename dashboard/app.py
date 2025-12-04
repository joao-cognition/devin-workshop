"""
Santander UK Complaints Analysis Dashboard

An interactive Streamlit dashboard connected to Supabase for analyzing
customer complaints data with filtering, dynamic statistics, and charts.
"""

import os
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from supabase import create_client, Client


# Page configuration
st.set_page_config(
    page_title="Complaints Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Santander branding
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #ec0000 0%, #b30000 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2rem;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    .stat-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
        border-left: 4px solid #ec0000;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #ec0000;
    }
    .stat-label {
        color: #666;
        font-size: 0.9rem;
        text-transform: uppercase;
    }
    .outlier-card {
        background: #fff5f5;
        border-left: 4px solid #ec0000;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .stSelectbox label, .stMultiSelect label, .stDateInput label {
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


def get_supabase_client() -> Client:
    """Initialize and return Supabase client.
    
    Returns:
        Supabase client instance.
        
    Raises:
        ValueError: If Supabase credentials are not configured.
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        st.error("Supabase credentials not configured. Please set SUPABASE_URL and SUPABASE_KEY.")
        st.stop()
    
    return create_client(url, key)


@st.cache_data(ttl=300)
def load_complaints_data() -> pd.DataFrame:
    """Load complaints data from Supabase with caching.
    
    Data is cached for 5 minutes (300 seconds) to reduce API calls.
    
    Returns:
        DataFrame containing all complaints data.
    """
    try:
        supabase = get_supabase_client()
        response = supabase.table("santander_customer_complaints").select("*").execute()
        df = pd.DataFrame(response.data)
        
        # Convert date columns
        df['complaint_date'] = pd.to_datetime(df['complaint_date'])
        df['resolution_date'] = pd.to_datetime(df['resolution_date'], errors='coerce')
        
        # Convert compensation to numeric
        df['compensation_numeric'] = df['compensation_amount'].str.replace('£', '').astype(float)
        
        return df
    except Exception as e:
        st.error(f"Error loading data from Supabase: {str(e)}")
        st.stop()


def apply_filters(
    df: pd.DataFrame,
    categories: list[str],
    severities: list[str],
    statuses: list[str],
    segments: list[str],
    date_range: tuple[datetime, datetime]
) -> pd.DataFrame:
    """Apply filters to the complaints DataFrame.
    
    Args:
        df: Original DataFrame.
        categories: List of selected categories.
        severities: List of selected severities.
        statuses: List of selected statuses.
        segments: List of selected customer segments.
        date_range: Tuple of (start_date, end_date).
        
    Returns:
        Filtered DataFrame.
    """
    filtered_df = df.copy()
    
    if categories:
        filtered_df = filtered_df[filtered_df['category'].isin(categories)]
    
    if severities:
        filtered_df = filtered_df[filtered_df['severity'].isin(severities)]
    
    if statuses:
        filtered_df = filtered_df[filtered_df['status'].isin(statuses)]
    
    if segments:
        filtered_df = filtered_df[filtered_df['customer_segment'].isin(segments)]
    
    if date_range[0] and date_range[1]:
        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1])
        filtered_df = filtered_df[
            (filtered_df['complaint_date'] >= start_date) & 
            (filtered_df['complaint_date'] <= end_date)
        ]
    
    return filtered_df


def calculate_statistics(df: pd.DataFrame) -> dict:
    """Calculate summary statistics for the filtered data.
    
    Args:
        df: Filtered DataFrame.
        
    Returns:
        Dictionary containing calculated statistics.
    """
    if df.empty:
        return {
            'total_complaints': 0,
            'avg_resolution_days': 0,
            'repeat_complainers': 0,
            'pct_with_compensation': 0,
            'total_compensation': 0,
            'median_resolution_days': 0,
            'max_resolution_days': 0,
            'avg_compensation': 0
        }
    
    repeat_complainers = df.groupby('customer_id').size()
    repeat_count = (repeat_complainers >= 3).sum()
    
    complaints_with_comp = (df['compensation_numeric'] > 0).sum()
    pct_with_comp = (complaints_with_comp / len(df) * 100) if len(df) > 0 else 0
    
    return {
        'total_complaints': len(df),
        'avg_resolution_days': df['resolution_days'].mean(),
        'repeat_complainers': repeat_count,
        'pct_with_compensation': pct_with_comp,
        'total_compensation': df['compensation_numeric'].sum(),
        'median_resolution_days': df['resolution_days'].median(),
        'max_resolution_days': df['resolution_days'].max(),
        'avg_compensation': df['compensation_numeric'].mean()
    }


def create_time_series_chart(df: pd.DataFrame, aggregation: str) -> go.Figure:
    """Create time series chart with configurable aggregation.
    
    Args:
        df: Filtered DataFrame.
        aggregation: One of 'Daily', 'Weekly', or 'Monthly'.
        
    Returns:
        Plotly figure object.
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
        return fig
    
    df_copy = df.copy()
    
    if aggregation == 'Daily':
        df_copy['period'] = df_copy['complaint_date'].dt.date
    elif aggregation == 'Weekly':
        df_copy['period'] = df_copy['complaint_date'].dt.to_period('W').apply(lambda x: x.start_time)
    else:  # Monthly
        df_copy['period'] = df_copy['complaint_date'].dt.to_period('M').apply(lambda x: x.start_time)
    
    time_series = df_copy.groupby('period').size().reset_index(name='count')
    time_series['period'] = pd.to_datetime(time_series['period'])
    
    fig = px.line(
        time_series,
        x='period',
        y='count',
        title=f'Complaints Over Time ({aggregation})',
        labels={'period': 'Date', 'count': 'Number of Complaints'}
    )
    
    fig.update_traces(
        line_color='#ec0000',
        fill='tozeroy',
        fillcolor='rgba(236, 0, 0, 0.1)'
    )
    
    fig.update_layout(
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)')
    )
    
    return fig


def create_category_chart(df: pd.DataFrame) -> go.Figure:
    """Create bar chart showing complaints by category.
    
    Args:
        df: Filtered DataFrame.
        
    Returns:
        Plotly figure object.
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
        return fig
    
    category_counts = df['category'].value_counts().reset_index()
    category_counts.columns = ['category', 'count']
    
    fig = px.bar(
        category_counts,
        x='category',
        y='count',
        title='Complaints by Category',
        labels={'category': 'Category', 'count': 'Number of Complaints'},
        color='count',
        color_continuous_scale=['#ffcccc', '#ec0000']
    )
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(showgrid=False, tickangle=45),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
        showlegend=False,
        coloraxis_showscale=False
    )
    
    return fig


def create_severity_chart(df: pd.DataFrame) -> go.Figure:
    """Create donut chart showing complaints by severity.
    
    Args:
        df: Filtered DataFrame.
        
    Returns:
        Plotly figure object.
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
        return fig
    
    severity_counts = df['severity'].value_counts().reset_index()
    severity_counts.columns = ['severity', 'count']
    
    colors = {'Low': '#059669', 'Medium': '#2563eb', 'High': '#d97706', 'Critical': '#dc2626'}
    severity_counts['color'] = severity_counts['severity'].map(colors)
    
    fig = go.Figure(data=[go.Pie(
        labels=severity_counts['severity'],
        values=severity_counts['count'],
        hole=0.5,
        marker_colors=severity_counts['color']
    )])
    
    fig.update_layout(
        title='Complaints by Severity',
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig


def create_resolution_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """Create bar chart showing resolution time distribution.
    
    Args:
        df: Filtered DataFrame.
        
    Returns:
        Plotly figure object.
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False)
        return fig
    
    def categorize_resolution(days: int) -> str:
        if days == 0:
            return 'Same day'
        elif days <= 7:
            return '1-7 days'
        elif days <= 14:
            return '8-14 days'
        elif days <= 30:
            return '15-30 days'
        elif days <= 60:
            return '31-60 days'
        else:
            return '60+ days'
    
    df_copy = df.copy()
    df_copy['resolution_bucket'] = df_copy['resolution_days'].apply(categorize_resolution)
    
    bucket_order = ['Same day', '1-7 days', '8-14 days', '15-30 days', '31-60 days', '60+ days']
    bucket_counts = df_copy['resolution_bucket'].value_counts().reindex(bucket_order, fill_value=0)
    
    colors = ['#059669', '#10b981', '#34d399', '#fbbf24', '#f97316', '#dc2626']
    
    fig = go.Figure(data=[go.Bar(
        x=bucket_counts.index,
        y=bucket_counts.values,
        marker_color=colors
    )])
    
    fig.update_layout(
        title='Resolution Time Distribution',
        xaxis_title='Resolution Time',
        yaxis_title='Number of Complaints',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)')
    )
    
    return fig


def display_outliers(df: pd.DataFrame) -> None:
    """Display outlier highlights section.
    
    Args:
        df: Filtered DataFrame.
    """
    st.subheader("Outlier Highlights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        extended_resolution = df[df['resolution_days'] > 60]
        st.markdown(f"""
        <div class="outlier-card">
            <h4>Extended Resolution (>60 days)</h4>
            <p style="font-size: 2rem; color: #ec0000; font-weight: bold;">{len(extended_resolution)} cases</p>
            <p style="color: #666;">Complaints taking longer than 60 days to resolve</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not extended_resolution.empty:
            with st.expander("View Details"):
                st.dataframe(
                    extended_resolution[['complaint_id', 'customer_id', 'category', 'resolution_days']]
                    .sort_values('resolution_days', ascending=False)
                    .head(10),
                    use_container_width=True
                )
    
    with col2:
        high_compensation = df[df['compensation_numeric'] > 300]
        st.markdown(f"""
        <div class="outlier-card">
            <h4>High Compensation (>£300)</h4>
            <p style="font-size: 2rem; color: #ec0000; font-weight: bold;">{len(high_compensation)} cases</p>
            <p style="color: #666;">Complaints with compensation exceeding £300</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not high_compensation.empty:
            with st.expander("View Details"):
                st.dataframe(
                    high_compensation[['complaint_id', 'customer_id', 'category', 'compensation_amount']]
                    .sort_values('compensation_numeric', ascending=False)
                    .head(10),
                    use_container_width=True
                )
    
    with col3:
        same_day = df[df['resolution_days'] == 0]
        st.markdown(f"""
        <div class="outlier-card">
            <h4>Same-Day Resolution (0 days)</h4>
            <p style="font-size: 2rem; color: #ec0000; font-weight: bold;">{len(same_day)} cases</p>
            <p style="color: #666;">May indicate quick fixes or data quality issues</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not same_day.empty:
            with st.expander("View Details"):
                st.dataframe(
                    same_day[['complaint_id', 'customer_id', 'category', 'status']]
                    .head(10),
                    use_container_width=True
                )


def display_repeat_complainers(df: pd.DataFrame) -> None:
    """Display repeat complainers analysis.
    
    Args:
        df: Filtered DataFrame.
    """
    st.subheader("Repeat Complainers (3+ Complaints)")
    
    repeat_analysis = df.groupby('customer_id').agg({
        'complaint_id': 'count',
        'resolution_days': 'mean',
        'compensation_numeric': 'sum',
        'category': lambda x: ', '.join(x.unique()[:3])
    }).reset_index()
    
    repeat_analysis.columns = ['Customer ID', 'Complaints', 'Avg Resolution (Days)', 
                               'Total Compensation', 'Categories']
    
    repeat_analysis = repeat_analysis[repeat_analysis['Complaints'] >= 3]
    repeat_analysis = repeat_analysis.sort_values('Complaints', ascending=False)
    
    if not repeat_analysis.empty:
        st.info(f"**{len(repeat_analysis)} customers** have filed 3 or more complaints")
        
        repeat_analysis['Avg Resolution (Days)'] = repeat_analysis['Avg Resolution (Days)'].round(1)
        repeat_analysis['Total Compensation'] = repeat_analysis['Total Compensation'].apply(
            lambda x: f"£{x:,.2f}"
        )
        
        st.dataframe(repeat_analysis.head(20), use_container_width=True)
    else:
        st.info("No repeat complainers found with current filters")


def main() -> None:
    """Main application entry point."""
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>Complaints Analysis Dashboard</h1>
        <p>Santander UK Customer Complaints - Live Data Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading data from Supabase..."):
        df = load_complaints_data()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Category filter
    categories = st.sidebar.multiselect(
        "Category",
        options=sorted(df['category'].unique()),
        default=[]
    )
    
    # Severity filter
    severities = st.sidebar.multiselect(
        "Severity",
        options=['Low', 'Medium', 'High', 'Critical'],
        default=[]
    )
    
    # Status filter
    statuses = st.sidebar.multiselect(
        "Status",
        options=sorted(df['status'].unique()),
        default=[]
    )
    
    # Customer segment filter
    segments = st.sidebar.multiselect(
        "Customer Segment",
        options=sorted(df['customer_segment'].unique()),
        default=[]
    )
    
    # Date range filter
    st.sidebar.subheader("Date Range")
    min_date = df['complaint_date'].min().date()
    max_date = df['complaint_date'].max().date()
    
    date_start = st.sidebar.date_input(
        "Start Date",
        value=min_date,
        min_value=min_date,
        max_value=max_date
    )
    
    date_end = st.sidebar.date_input(
        "End Date",
        value=max_date,
        min_value=min_date,
        max_value=max_date
    )
    
    # Clear filters button
    if st.sidebar.button("Clear All Filters"):
        st.rerun()
    
    # Refresh data button
    if st.sidebar.button("Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Apply filters
    filtered_df = apply_filters(
        df,
        categories,
        severities,
        statuses,
        segments,
        (date_start, date_end)
    )
    
    # Calculate statistics
    stats = calculate_statistics(filtered_df)
    
    # Display KPI cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{stats['total_complaints']:,}</div>
            <div class="stat-label">Total Complaints</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{stats['avg_resolution_days']:.1f}</div>
            <div class="stat-label">Avg Resolution (Days)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{stats['repeat_complainers']}</div>
            <div class="stat-label">Repeat Complainers</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{stats['pct_with_compensation']:.1f}%</div>
            <div class="stat-label">Received Compensation</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">£{stats['total_compensation']:,.0f}</div>
            <div class="stat-label">Total Compensation</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts section
    st.subheader("Charts")
    
    # Time series with aggregation toggle
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        aggregation = st.radio(
            "Time Aggregation",
            options=['Daily', 'Weekly', 'Monthly'],
            horizontal=True,
            index=2
        )
        fig_time = create_time_series_chart(filtered_df, aggregation)
        st.plotly_chart(fig_time, use_container_width=True)
    
    with col_chart2:
        fig_category = create_category_chart(filtered_df)
        st.plotly_chart(fig_category, use_container_width=True)
    
    # Second row of charts
    col_chart3, col_chart4 = st.columns(2)
    
    with col_chart3:
        fig_severity = create_severity_chart(filtered_df)
        st.plotly_chart(fig_severity, use_container_width=True)
    
    with col_chart4:
        fig_resolution = create_resolution_distribution_chart(filtered_df)
        st.plotly_chart(fig_resolution, use_container_width=True)
    
    st.markdown("---")
    
    # Outliers section
    display_outliers(filtered_df)
    
    st.markdown("---")
    
    # Repeat complainers section
    display_repeat_complainers(filtered_df)
    
    st.markdown("---")
    
    # Data table section
    st.subheader("Raw Data")
    
    with st.expander("View Filtered Data Table"):
        st.dataframe(
            filtered_df[[
                'complaint_id', 'customer_id', 'category', 'severity', 
                'status', 'complaint_date', 'resolution_days', 'compensation_amount'
            ]].sort_values('complaint_date', ascending=False),
            use_container_width=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"<p style='text-align: center; color: #666;'>"
        f"Generated on {datetime.now().strftime('%B %d, %Y')} | "
        f"Data Source: Supabase - santander_customer_complaints | "
        f"Last refresh: {datetime.now().strftime('%H:%M:%S')}"
        f"</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
