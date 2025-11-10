"""
Analytics Dashboard Utilities
Data fetching functions for analytics dashboard
"""
from typing import List, Dict, Optional
import pandas as pd
from app_dash.utils.databricks_client import execute_sql
from config.config import SQL_WAREHOUSE_ID

# Gold layer tables
GOLD_CALL_SUMMARIES = "member_analytics.call_center.call_summaries"
GOLD_AGENT_PERFORMANCE = "member_analytics.call_center.agent_performance"
GOLD_MEMBER_INTERACTIONS = "member_analytics.call_center.member_interaction_history"
GOLD_DAILY_STATS = "member_analytics.call_center.daily_call_statistics"

def get_overview_metrics(days: int = 7) -> Dict:
    """Get overview metrics for the last N days"""
    query = f"""
    SELECT 
        SUM(total_calls) as total_calls,
        COUNT(DISTINCT active_agents) as active_agents,
        SUM(unique_members) as unique_members,
        AVG(positive_sentiment_rate) as avg_positive_rate
    FROM {GOLD_DAILY_STATS}
    WHERE call_date >= CURRENT_DATE() - INTERVAL {days} DAYS
    """
    results = execute_sql(query, SQL_WAREHOUSE_ID, return_dataframe=True)
    
    if results is None or results.empty:
        return {
            'total_calls': 0,
            'active_agents': 0,
            'unique_members': 0,
            'avg_positive_rate': 0.0
        }
    
    row = results.iloc[0]
    return {
        'total_calls': int(row.get('total_calls', 0) or 0),
        'active_agents': int(row.get('active_agents', 0) or 0),
        'unique_members': int(row.get('unique_members', 0) or 0),
        'avg_positive_rate': float(row.get('avg_positive_rate', 0.0) or 0.0)
    }

def get_recent_call_summaries(limit: int = 20) -> pd.DataFrame:
    """Get recent call summaries"""
    query = f"""
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
    FROM {GOLD_CALL_SUMMARIES}
    ORDER BY summary_created_at DESC
    LIMIT {limit}
    """
    return execute_sql(query, SQL_WAREHOUSE_ID, return_dataframe=True) or pd.DataFrame()

def get_agent_performance(limit: int = 20) -> pd.DataFrame:
    """Get agent performance metrics"""
    query = f"""
    SELECT 
        agent_id,
        call_date,
        total_calls,
        avg_call_duration_minutes,
        positive_sentiment_rate,
        compliance_rate,
        performance_score,
        metrics_calculated_at
    FROM {GOLD_AGENT_PERFORMANCE}
    ORDER BY performance_score DESC
    LIMIT {limit}
    """
    return execute_sql(query, SQL_WAREHOUSE_ID, return_dataframe=True) or pd.DataFrame()

def get_agent_by_id(agent_id: str) -> pd.DataFrame:
    """Get performance data for a specific agent"""
    query = f"""
    SELECT 
        agent_id,
        call_date,
        total_calls,
        avg_call_duration_minutes,
        positive_sentiment_rate,
        compliance_rate,
        performance_score
    FROM {GOLD_AGENT_PERFORMANCE}
    WHERE agent_id = '{agent_id}'
    ORDER BY call_date DESC
    """
    return execute_sql(query, SQL_WAREHOUSE_ID, return_dataframe=True) or pd.DataFrame()

def get_call_summaries_filtered(
    sentiment_filter: str = "All",
    compliance_filter: str = "All",
    limit: int = 50
) -> pd.DataFrame:
    """Get call summaries with filters"""
    where_clauses = []
    
    if sentiment_filter != "All":
        where_clauses.append(f"overall_sentiment = '{sentiment_filter.lower()}'")
    
    if compliance_filter == "Has Issues":
        where_clauses.append("has_compliance_issues = TRUE")
    elif compliance_filter == "No Issues":
        where_clauses.append("has_compliance_issues = FALSE")
    
    where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    query = f"""
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
    FROM {GOLD_CALL_SUMMARIES}
    WHERE {where_clause}
    ORDER BY summary_created_at DESC
    LIMIT {limit}
    """
    return execute_sql(query, SQL_WAREHOUSE_ID, return_dataframe=True) or pd.DataFrame()

def get_daily_statistics(days: int = 30) -> pd.DataFrame:
    """Get daily call statistics"""
    query = f"""
    SELECT 
        call_date,
        total_calls,
        active_agents,
        unique_members,
        avg_call_duration_minutes,
        positive_sentiment_rate,
        compliance_rate
    FROM {GOLD_DAILY_STATS}
    WHERE call_date >= CURRENT_DATE() - INTERVAL {days} DAYS
    ORDER BY call_date DESC
    """
    return execute_sql(query, SQL_WAREHOUSE_ID, return_dataframe=True) or pd.DataFrame()

