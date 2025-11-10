#!/usr/bin/env python3
"""
Analytics Dashboard for ART Call Center
Streamlit dashboard for Gold layer analytics

Run: streamlit run app/analytics_dashboard.py --server.port 8521
"""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
from config.config import get_workspace_client
import time
from datetime import datetime
import pandas as pd

# Page config
st.set_page_config(
    page_title="ART Call Center Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ART Branding Colors
ART_PRIMARY = "#003366"  # Dark blue
ART_SECONDARY = "#0066CC"  # Medium blue
ART_ACCENT = "#FF6600"  # Orange
ART_BACKGROUND = "#F5F5F5"
ART_TEXT = "#333333"
ART_TEXT_GRAY = "#666666"

# Custom CSS
st.markdown(f"""
    <style>
        .main {{
            background-color: {ART_BACKGROUND};
        }}
        .stApp {{
            background-color: {ART_BACKGROUND};
        }}
        h1 {{
            color: {ART_PRIMARY};
            font-weight: bold;
        }}
        h2 {{
            color: {ART_PRIMARY};
            font-weight: 600;
        }}
        .metric-card {{
            background-color: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }}
        .stat-box {{
            background: linear-gradient(135deg, {ART_PRIMARY} 0%, {ART_SECONDARY} 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
            margin: 0.5rem 0;
        }}
        .stat-value {{
            font-size: 2.5rem;
            font-weight: bold;
            margin: 0.5rem 0;
        }}
        .stat-label {{
            font-size: 1rem;
            opacity: 0.9;
        }}
    </style>
""", unsafe_allow_html=True)

# Initialize workspace client
@st.cache_resource
def get_client():
    return get_workspace_client()

w = get_client()

# Helper function to execute SQL
@st.cache_data(ttl=300)  # Cache for 5 minutes
def execute_sql(query: str, max_rows: int = 1000):
    """Execute SQL query and return results as pandas DataFrame"""
    try:
        response = w.statement_execution.execute_statement(
            warehouse_id='4b9b953939869799',
            statement=query,
            wait_timeout='30s'
        )
        
        statement_id = response.statement_id
        max_attempts = 30
        
        for attempt in range(max_attempts):
            status = w.statement_execution.get_statement(statement_id)
            
            if status.status.state == StatementState.SUCCEEDED:
                if status.result and status.result.data_array:
                    # Get column names
                    columns = []
                    if status.manifest and status.manifest.schema and status.manifest.schema.columns:
                        columns = [col.name for col in status.manifest.schema.columns]
                    else:
                        columns = [f"col_{i}" for i in range(len(status.result.data_array[0]))]
                    
                    # Convert to DataFrame
                    df = pd.DataFrame(status.result.data_array[:max_rows], columns=columns)
                    return df
                else:
                    return pd.DataFrame()
            elif status.status.state == StatementState.FAILED:
                # Try to get error message from status
                error_msg = "Query failed"
                if hasattr(status.status, 'message') and status.status.message:
                    error_msg = status.status.message
                elif hasattr(status.status, 'state_message') and status.status.state_message:
                    error_msg = status.status.state_message
                else:
                    error_msg = f"Query failed: {status.status.state}"
                st.error(f"Query failed: {error_msg}")
                return pd.DataFrame()
            
            time.sleep(1)
        
        st.warning("Query timed out")
        return pd.DataFrame()
    
    except Exception as e:
        st.error(f"Error executing query: {str(e)[:300]}")
        return pd.DataFrame()

# Header
st.title("📊 ART Call Center Analytics Dashboard")
st.markdown("---")

# Sidebar filters
st.sidebar.header("Filters")
date_range = st.sidebar.date_input(
    "Date Range",
    value=(datetime.now().date(), datetime.now().date()),
    help="Select date range for analytics"
)

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Overview",
    "👥 Agent Performance",
    "📞 Call Summaries",
    "📊 Daily Statistics"
])

# Tab 1: Overview
with tab1:
    st.header("Call Center Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Total calls today
    today_stats = execute_sql("""
        SELECT 
            SUM(total_calls) as total_calls,
            COUNT(DISTINCT active_agents) as active_agents,
            SUM(unique_members) as unique_members,
            AVG(positive_sentiment_rate) as avg_positive_rate
        FROM member_analytics.call_center.daily_call_statistics
        WHERE call_date >= CURRENT_DATE() - INTERVAL 7 DAYS
    """)
    
    if not today_stats.empty:
        total_calls = int(today_stats.iloc[0]['total_calls']) if 'total_calls' in today_stats.columns else 0
        active_agents = int(today_stats.iloc[0]['active_agents']) if 'active_agents' in today_stats.columns else 0
        unique_members = int(today_stats.iloc[0]['unique_members']) if 'unique_members' in today_stats.columns else 0
        avg_positive = float(today_stats.iloc[0]['avg_positive_rate']) if 'avg_positive_rate' in today_stats.columns else 0
        
        with col1:
            st.metric("Total Calls (7 days)", f"{total_calls:,}")
        with col2:
            st.metric("Active Agents", f"{active_agents:,}")
        with col3:
            st.metric("Unique Members", f"{unique_members:,}")
        with col4:
            st.metric("Avg Positive Sentiment", f"{avg_positive:.1f}%")
    
    st.markdown("---")
    
    # Recent call summaries
    st.subheader("Recent Call Summaries")
    recent_calls = execute_sql("""
        SELECT 
            call_id,
            member_name,
            agent_id,
            call_duration_minutes,
            overall_sentiment,
            primary_intent,
            has_compliance_issues,
            compliance_severity_level,
            summary_created_at
        FROM member_analytics.call_center.call_summaries
        ORDER BY summary_created_at DESC
        LIMIT 20
    """)
    
    if not recent_calls.empty:
        st.dataframe(recent_calls, use_container_width=True, hide_index=True)
    else:
        st.info("No call summaries available")

# Tab 2: Agent Performance
with tab2:
    st.header("Agent Performance Metrics")
    
    # Top performers
    st.subheader("Top Performing Agents")
    top_agents = execute_sql("""
        SELECT 
            agent_id,
            call_date,
            total_calls,
            avg_call_duration_minutes,
            positive_sentiment_rate,
            compliance_rate,
            performance_score,
            metrics_calculated_at
        FROM member_analytics.call_center.agent_performance
        ORDER BY performance_score DESC
        LIMIT 20
    """)
    
    if not top_agents.empty:
        st.dataframe(top_agents, use_container_width=True, hide_index=True)
        
        # Performance metrics visualization
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Performance Score Distribution")
            if 'performance_score' in top_agents.columns and not top_agents.empty:
                # Use DataFrame display instead of bar_chart to avoid altair compatibility issues
                perf_data = top_agents[['agent_id', 'performance_score']].head(10)
                st.dataframe(perf_data.set_index('agent_id'), use_container_width=True)
        
        with col2:
            st.subheader("Compliance Rate")
            if 'compliance_rate' in top_agents.columns and not top_agents.empty:
                # Use DataFrame display instead of bar_chart
                compliance_data = top_agents[['agent_id', 'compliance_rate']].head(10)
                st.dataframe(compliance_data.set_index('agent_id'), use_container_width=True)
    else:
        st.info("No agent performance data available")
    
    st.markdown("---")
    
    # Agent search
    st.subheader("Search Agent Performance")
    agent_id = st.text_input("Enter Agent ID", placeholder="e.g., AGENT-001")
    
    if agent_id:
        agent_data = execute_sql(f"""
            SELECT 
                agent_id,
                call_date,
                total_calls,
                avg_call_duration_minutes,
                positive_sentiment_rate,
                compliance_rate,
                performance_score
            FROM member_analytics.call_center.agent_performance
            WHERE agent_id = '{agent_id}'
            ORDER BY call_date DESC
        """)
        
        if not agent_data.empty:
            st.dataframe(agent_data, use_container_width=True, hide_index=True)
        else:
            st.warning(f"No data found for agent {agent_id}")

# Tab 3: Call Summaries
with tab3:
    st.header("Call Summaries")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        sentiment_filter = st.selectbox(
            "Sentiment Filter",
            ["All", "positive", "negative", "neutral"]
        )
    with col2:
        compliance_filter = st.selectbox(
            "Compliance Filter",
            ["All", "Has Issues", "No Issues"]
        )
    with col3:
        intent_filter = st.selectbox(
            "Intent Filter",
            ["All", "general_inquiry", "complaint", "contribution_inquiry", "insurance_inquiry", "withdrawal_request"]
        )
    
    # Build query
    where_clauses = []
    if sentiment_filter != "All":
        where_clauses.append(f"overall_sentiment = '{sentiment_filter}'")
    if compliance_filter == "Has Issues":
        where_clauses.append("has_compliance_issues = true")
    elif compliance_filter == "No Issues":
        where_clauses.append("has_compliance_issues = false")
    if intent_filter != "All":
        where_clauses.append(f"primary_intent = '{intent_filter}'")
    
    where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    call_summaries = execute_sql(f"""
        SELECT 
            call_id,
            member_name,
            agent_id,
            call_duration_minutes,
            overall_sentiment,
            primary_intent,
            has_compliance_issues,
            compliance_severity_level,
            summary_created_at
        FROM member_analytics.call_center.call_summaries
        WHERE {where_clause}
        ORDER BY summary_created_at DESC
        LIMIT 100
    """)
    
    if not call_summaries.empty:
        st.dataframe(call_summaries, use_container_width=True, hide_index=True)
        
        # Summary statistics
        st.markdown("---")
        st.subheader("Summary Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Calls", len(call_summaries))
        with col2:
            if 'overall_sentiment' in call_summaries.columns:
                positive_count = len(call_summaries[call_summaries['overall_sentiment'] == 'positive'])
                st.metric("Positive Sentiment", f"{positive_count} ({positive_count/len(call_summaries)*100:.1f}%)")
        with col3:
            if 'has_compliance_issues' in call_summaries.columns:
                compliance_count = len(call_summaries[call_summaries['has_compliance_issues'] == True])
                st.metric("Compliance Issues", f"{compliance_count} ({compliance_count/len(call_summaries)*100:.1f}%)")
        with col4:
            if 'call_duration_minutes' in call_summaries.columns:
                avg_duration = call_summaries['call_duration_minutes'].mean()
                st.metric("Avg Duration (min)", f"{avg_duration:.2f}")
    else:
        st.info("No call summaries match the selected filters")

# Tab 4: Daily Statistics
with tab4:
    st.header("Daily Call Statistics")
    
    daily_stats = execute_sql("""
        SELECT 
            call_date,
            total_calls,
            active_agents,
            unique_members,
            avg_call_duration_minutes,
            positive_sentiment_rate,
            compliance_rate,
            stats_calculated_at
        FROM member_analytics.call_center.daily_call_statistics
        ORDER BY call_date DESC
        LIMIT 30
    """)
    
    if not daily_stats.empty:
        st.dataframe(daily_stats, use_container_width=True, hide_index=True)
        
        # Visualizations
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Daily Call Volume")
            if 'call_date' in daily_stats.columns and 'total_calls' in daily_stats.columns and not daily_stats.empty:
                # Use DataFrame display instead of line_chart
                volume_data = daily_stats[['call_date', 'total_calls']].head(10)
                st.dataframe(volume_data.set_index('call_date'), use_container_width=True)
        
        with col2:
            st.subheader("Positive Sentiment Rate")
            if 'call_date' in daily_stats.columns and 'positive_sentiment_rate' in daily_stats.columns and not daily_stats.empty:
                # Use DataFrame display instead of line_chart
                sentiment_data = daily_stats[['call_date', 'positive_sentiment_rate']].head(10)
                st.dataframe(sentiment_data.set_index('call_date'), use_container_width=True)
        
        # Summary metrics
        st.markdown("---")
        st.subheader("7-Day Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        if 'total_calls' in daily_stats.columns:
            total_calls_7d = daily_stats['total_calls'].sum()
            with col1:
                st.metric("Total Calls (7d)", f"{int(total_calls_7d):,}")
        
        if 'active_agents' in daily_stats.columns:
            avg_agents = daily_stats['active_agents'].mean()
            with col2:
                st.metric("Avg Active Agents", f"{int(avg_agents):,}")
        
        if 'positive_sentiment_rate' in daily_stats.columns:
            avg_positive = daily_stats['positive_sentiment_rate'].mean()
            with col3:
                st.metric("Avg Positive Rate", f"{avg_positive:.1f}%")
        
        if 'compliance_rate' in daily_stats.columns:
            avg_compliance = daily_stats['compliance_rate'].mean()
            with col4:
                st.metric("Avg Compliance Rate", f"{avg_compliance:.1f}%")
    else:
        st.info("No daily statistics available")

# Footer
st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: {ART_TEXT_GRAY}; padding: 1rem;'>"
    "Australian Retirement Trust Call Center Analytics Dashboard | "
    f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    "</div>",
    unsafe_allow_html=True
)

