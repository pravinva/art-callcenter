#!/usr/bin/env python3
"""
ART Supervisor Dashboard
Real-time monitoring dashboard for call center supervisors to monitor calls,
track escalations, and oversee agent performance.

Run: streamlit run app/supervisor_dashboard.py --server.port 8522
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import time as time_module
import re
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
from config.config import (
    get_workspace_url, SQL_WAREHOUSE_ID,
    ENRICHED_TABLE, FUNCTION_GET_CALL_CONTEXT,
    FUNCTION_IDENTIFY_ESCALATION
)

# Page configuration
st.set_page_config(
    page_title="ART Supervisor Dashboard",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Australian Retirement Trust Brand Colors
ART_PRIMARY_BLUE = "#0051FF"
ART_DARK_BLUE = "#0033CC"
ART_LIGHT_BLUE = "#E6F0FF"
ART_ACCENT_BLUE = "#3385FF"
ART_TEXT_DARK = "#1A1A1A"
ART_TEXT_GRAY = "#666666"
ART_BG_LIGHT = "#F8F9FA"
ART_BORDER = "#E0E0E0"
ART_WHITE = "#FFFFFF"
ART_SUCCESS_GREEN = "#00A651"
ART_WARNING_ORANGE = "#FF6B35"
ART_ERROR_RED = "#DC3545"

# Custom CSS for Supervisor Dashboard
st.markdown(f"""
<style>
    /* Import professional font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Main container */
    .main {{
        background-color: {ART_BG_LIGHT};
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        max-width: 100% !important;
        padding: 0 2rem;
    }}
    
    .block-container {{
        max-width: 100% !important;
        padding-left: 2rem;
        padding-right: 2rem;
    }}
    
    /* Header */
    .header-container {{
        background: linear-gradient(135deg, {ART_PRIMARY_BLUE} 0%, {ART_ACCENT_BLUE} 100%);
        padding: 2rem 2.5rem;
        border-radius: 0;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 4px 12px rgba(0, 81, 255, 0.15);
    }}
    
    .header-title {{
        color: {ART_WHITE};
        font-size: 2.25rem;
        font-weight: 700;
        margin: 0;
    }}
    
    .header-subtitle {{
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.1rem;
        margin-top: 0.75rem;
    }}
    
    /* Escalation card */
    .escalation-card {{
        background-color: {ART_WHITE};
        border: 1px solid {ART_BORDER};
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }}
    
    .escalation-critical {{
        background-color: #FFEBEE;
        border-left: 4px solid {ART_ERROR_RED};
        padding: 1.25rem;
        border-radius: 8px;
        margin: 1rem 0;
        line-height: 1.6;
    }}
    
    .escalation-warning {{
        background-color: #FFF3E0;
        border-left: 4px solid {ART_WARNING_ORANGE};
        padding: 1.25rem;
        border-radius: 8px;
        margin: 1rem 0;
        line-height: 1.6;
    }}
    
    .escalation-safe {{
        background-color: #E8F5E9;
        border-left: 4px solid {ART_SUCCESS_GREEN};
        padding: 1.25rem;
        border-radius: 8px;
        margin: 1rem 0;
        line-height: 1.6;
    }}
    
    /* Call card */
    .call-card {{
        background-color: {ART_WHITE};
        border: 1px solid {ART_BORDER};
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }}
    
    /* Metric card */
    .metric-card {{
        background-color: {ART_WHITE};
        border: 1px solid {ART_BORDER};
        border-radius: 8px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }}
    
    /* Hide Streamlit default elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_workspace_client():
    """Get WorkspaceClient - cached to avoid multiple connections"""
    return WorkspaceClient()

def execute_sql(query, return_dataframe=False):
    """Execute SQL using Databricks SDK"""
    w = get_workspace_client()
    
    try:
        response = w.statement_execution.execute_statement(
            warehouse_id=SQL_WAREHOUSE_ID,
            statement=query,
            wait_timeout="10s"
        )
        
        statement_id = response.statement_id
        max_wait = 10
        waited = 0
        result_manifest = None
        
        while waited < max_wait:
            status = w.statement_execution.get_statement(statement_id)
            if status.status.state == StatementState.SUCCEEDED:
                if status.manifest:
                    result_manifest = status.manifest
                break
            elif status.status.state in [StatementState.FAILED, StatementState.CANCELED]:
                error_msg = f"SQL execution failed: {status.status.state}"
                if hasattr(status.status, 'message') and status.status.message:
                    error_msg = status.status.message
                raise Exception(error_msg)
            time_module.sleep(0.2)
            waited += 0.2
        
        if waited >= max_wait:
            raise Exception("SQL execution timed out")
        
        if not result_manifest:
            raise Exception("Could not retrieve result manifest")
        
        all_rows = []
        chunk_index = 0
        
        while True:
            result_chunk = w.statement_execution.get_statement_result_chunk_n(statement_id, chunk_index)
            if not result_chunk or not result_chunk.data_array:
                break
            all_rows.extend(result_chunk.data_array)
            if not result_chunk.next_chunk_index or result_chunk.next_chunk_index == chunk_index:
                break
            chunk_index = result_chunk.next_chunk_index
        
        if return_dataframe:
            if all_rows and result_manifest and result_manifest.schema and result_manifest.schema.columns:
                columns = [col.name for col in result_manifest.schema.columns]
                df = pd.DataFrame(all_rows, columns=columns)
                return df
            return pd.DataFrame()
        return all_rows
    except Exception as e:
        st.error(f"SQL execution error: {e}")
        return pd.DataFrame() if return_dataframe else []

def get_all_active_calls():
    """Get all active calls with basic info"""
    query = f"""
    SELECT DISTINCT
        call_id,
        member_name,
        member_id,
        agent_id,
        scenario,
        COUNT(*) as utterance_count,
        MAX(timestamp) as last_utterance_time
    FROM {ENRICHED_TABLE}
    WHERE timestamp >= current_timestamp() - INTERVAL 10 MINUTES
    GROUP BY call_id, member_name, member_id, agent_id, scenario
    ORDER BY last_utterance_time DESC
    """
    df = execute_sql(query, return_dataframe=True)
    
    # Convert numeric columns to proper types
    if not df.empty:
        if 'utterance_count' in df.columns:
            df['utterance_count'] = pd.to_numeric(df['utterance_count'], errors='coerce')
    
    return df

@st.cache_data(ttl=30)  # Cache for 30 seconds
def get_escalation_data(call_id):
    """Get escalation triggers for a call - cached to avoid repeated queries"""
    try:
        query = f"SELECT * FROM {FUNCTION_IDENTIFY_ESCALATION}('{call_id}')"
        results = execute_sql(query, return_dataframe=False)
        if results and len(results) > 0:
            return results[0]
        return None
    except Exception as e:
        print(f"Error getting escalation data: {e}")
        return None

def get_calls_with_escalations_batch(call_ids):
    """Get escalation data for multiple calls in ONE efficient SQL query - filters to only calls with escalations"""
    if not call_ids:
        return {}
    
    try:
        # Build efficient batch query that replicates escalation logic
        call_ids_str = "', '".join(call_ids)
        query = f"""
        SELECT 
            call_id,
            CASE 
                WHEN (
                    SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) > 0 AND
                    SUM(CASE WHEN compliance_flag != 'ok' THEN 1 ELSE 0 END) > 0 AND
                    SUM(CASE WHEN intent_category = 'complaint' THEN 1 ELSE 0 END) > 0
                ) THEN TRUE
                WHEN (
                    SUM(CASE WHEN compliance_severity = 'CRITICAL' THEN 1 ELSE 0 END) > 0
                ) THEN TRUE
                WHEN (
                    SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) >= 3 AND
                    SUM(CASE WHEN compliance_flag != 'ok' THEN 1 ELSE 0 END) > 0
                ) THEN TRUE
                ELSE FALSE
            END as escalation_recommended,
            (
                SUM(CASE WHEN sentiment = 'negative' THEN 2 ELSE 0 END) +
                SUM(CASE WHEN compliance_flag != 'ok' THEN 3 ELSE 0 END) +
                SUM(CASE WHEN intent_category = 'complaint' THEN 2 ELSE 0 END) +
                SUM(CASE WHEN compliance_severity = 'CRITICAL' THEN 5 ELSE 0 END) +
                SUM(CASE WHEN compliance_severity = 'HIGH' THEN 3 ELSE 0 END)
            ) as risk_score,
            ARRAY_JOIN(ARRAY_AGG(DISTINCT 
                CASE 
                    WHEN sentiment = 'negative' THEN 'negative_sentiment'
                    WHEN compliance_flag != 'ok' THEN CONCAT('compliance_', compliance_flag)
                    WHEN intent_category = 'complaint' THEN 'complaint_intent'
                    ELSE NULL
                END
            ), ', ') as risk_factors,
            SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) as negative_sentiment_count,
            SUM(CASE WHEN compliance_flag != 'ok' THEN 1 ELSE 0 END) as compliance_violations_count,
            SUM(CASE WHEN intent_category = 'complaint' THEN 1 ELSE 0 END) as complaint_intent_count,
            CASE 
                WHEN (
                    SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) > 0 AND
                    SUM(CASE WHEN compliance_flag != 'ok' THEN 1 ELSE 0 END) > 0 AND
                    SUM(CASE WHEN intent_category = 'complaint' THEN 1 ELSE 0 END) > 0
                ) THEN 'IMMEDIATE ESCALATION: Multiple risk factors detected (negative sentiment + compliance violation + complaint)'
                WHEN (
                    SUM(CASE WHEN compliance_severity = 'CRITICAL' THEN 1 ELSE 0 END) > 0
                ) THEN 'IMMEDIATE ESCALATION: Critical compliance violation detected'
                WHEN (
                    SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) >= 3 AND
                    SUM(CASE WHEN compliance_flag != 'ok' THEN 1 ELSE 0 END) > 0
                ) THEN 'ESCALATION RECOMMENDED: Multiple negative sentiments with compliance issues'
                WHEN (
                    SUM(CASE WHEN compliance_flag != 'ok' THEN 1 ELSE 0 END) >= 2
                ) THEN 'ESCALATION RECOMMENDED: Multiple compliance violations detected'
                WHEN (
                    SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) >= 5
                ) THEN 'MONITOR CLOSELY: High number of negative sentiment indicators'
                WHEN (
                    (
                        SUM(CASE WHEN sentiment = 'negative' THEN 2 ELSE 0 END) +
                        SUM(CASE WHEN compliance_flag != 'ok' THEN 3 ELSE 0 END) +
                        SUM(CASE WHEN intent_category = 'complaint' THEN 2 ELSE 0 END) +
                        SUM(CASE WHEN compliance_severity = 'CRITICAL' THEN 5 ELSE 0 END) +
                        SUM(CASE WHEN compliance_severity = 'HIGH' THEN 3 ELSE 0 END)
                    ) >= 8
                ) THEN 'MONITOR CLOSELY: Elevated risk score detected'
                ELSE 'NO ESCALATION: Call proceeding normally'
            END as recommendation
        FROM {ENRICHED_TABLE}
        WHERE call_id IN ('{call_ids_str}')
        GROUP BY call_id
        HAVING 
            -- Only return calls that ACTUALLY need escalation (escalation_recommended = TRUE)
            -- Don't include calls that just have high risk_score but no escalation triggers
            (
                -- Escalation required conditions (must match escalation_recommended logic)
                (
                    SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) > 0 AND
                    SUM(CASE WHEN compliance_flag != 'ok' THEN 1 ELSE 0 END) > 0 AND
                    SUM(CASE WHEN intent_category = 'complaint' THEN 1 ELSE 0 END) > 0
                ) OR
                (
                    SUM(CASE WHEN compliance_severity = 'CRITICAL' THEN 1 ELSE 0 END) > 0
                ) OR
                (
                    SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) >= 3 AND
                    SUM(CASE WHEN compliance_flag != 'ok' THEN 1 ELSE 0 END) > 0
                )
            )
        """
        
        results = execute_sql(query, return_dataframe=True)
        
        # Convert to dictionary mapping call_id to escalation data
        escalation_map = {}
        if not results.empty:
            for _, row in results.iterrows():
                call_id = row['call_id']
                escalation_recommended = bool(row['escalation_recommended'])
                risk_score = int(row['risk_score']) if pd.notna(row['risk_score']) else 0
                
                # Only include if escalation_recommended is TRUE (not just high risk_score)
                if escalation_recommended:
                    # Fix recommendation if it says "NO ESCALATION" but escalation_recommended is TRUE
                    recommendation_text = str(row['recommendation']) if pd.notna(row['recommendation']) else "NO ESCALATION"
                    if "NO ESCALATION" in recommendation_text:
                        # Override recommendation based on escalation_recommended status and risk_score
                        if risk_score >= 12:
                            recommendation_text = "IMMEDIATE ESCALATION: High risk score and escalation triggers detected"
                        elif risk_score >= 8:
                            recommendation_text = "ESCALATION RECOMMENDED: Risk factors detected"
                        else:
                            recommendation_text = "ESCALATION RECOMMENDED: Escalation triggers detected"
                    
                    escalation_map[call_id] = (
                        escalation_recommended,
                        risk_score,
                        str(row['risk_factors']) if pd.notna(row['risk_factors']) else "None",
                        int(row['negative_sentiment_count']) if pd.notna(row['negative_sentiment_count']) else 0,
                        int(row['compliance_violations_count']) if pd.notna(row['compliance_violations_count']) else 0,
                        int(row['complaint_intent_count']) if pd.notna(row['complaint_intent_count']) else 0,
                        recommendation_text
                    )
        
        return escalation_map
    except Exception as e:
        print(f"Error getting batch escalation data: {e}")
        return {}

# Header
st.markdown(f"""
<div class="header-container">
    <h1 class="header-title">Supervisor Dashboard</h1>
    <p class="header-subtitle">Real-time call monitoring and escalation management for Australian Retirement Trust</p>
</div>
""", unsafe_allow_html=True)

# Sidebar - Filters
with st.sidebar:
    st.markdown("### 🔍 Filters")
    
    # Get all active calls - cache key includes timestamp to refresh periodically
    cache_key = st.session_state.get('calls_cache_key', 0)
    if 'active_calls_df' not in st.session_state or cache_key < time_module.time() - 30:
        st.session_state['active_calls_df'] = get_all_active_calls()
        st.session_state['calls_cache_key'] = time_module.time()
    
    active_calls_df = st.session_state['active_calls_df']
    
    if not active_calls_df.empty:
        # Filter by agent - use key to prevent unnecessary reruns
        agents = ['All'] + sorted(active_calls_df['agent_id'].unique().tolist())
        selected_agent = st.selectbox("Filter by Agent", agents, key="agent_filter")
        
        # Filter by escalation status - use key to prevent unnecessary reruns
        escalation_filter = st.selectbox("Escalation Status", 
                                         ["All", "Escalation Needed", "Monitor Closely", "Normal"],
                                         key="escalation_filter")
        
        # Filter calls based on selections
        filtered_calls = active_calls_df.copy()
        if selected_agent != 'All':
            filtered_calls = filtered_calls[filtered_calls['agent_id'] == selected_agent]
        
        st.markdown("---")
        st.markdown(f"**Active Calls:** {len(filtered_calls)}")
        st.markdown(f"**Total Agents:** {len(active_calls_df['agent_id'].unique())}")
    else:
        st.warning("No active calls")
        filtered_calls = pd.DataFrame()
        escalation_filter = "All"

# Main dashboard
if not filtered_calls.empty:
    # Overview metrics
    st.markdown("## 📊 Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0; color: {ART_PRIMARY_BLUE};">{len(filtered_calls)}</h3>
            <p style="margin: 0.5rem 0 0 0; color: {ART_TEXT_GRAY};">Active Calls</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        unique_agents = len(filtered_calls['agent_id'].unique())
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0; color: {ART_PRIMARY_BLUE};">{unique_agents}</h3>
            <p style="margin: 0.5rem 0 0 0; color: {ART_TEXT_GRAY};">Active Agents</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Count calls needing escalation - use efficient batch query
        escalation_count = 0
        call_ids_list = filtered_calls['call_id'].tolist()
        
        # Use efficient batch query that only returns calls with escalations
        cache_key = f"escalation_data_{hash(tuple(sorted(call_ids_list)))}"
        if cache_key not in st.session_state:
            escalation_map = get_calls_with_escalations_batch(call_ids_list)
            st.session_state[cache_key] = escalation_map
        else:
            escalation_map = st.session_state[cache_key]
        
        # Count escalation_recommended = True
        escalation_count = sum(1 for data in escalation_map.values() if data and len(data) >= 7 and data[0])
        
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0; color: {ART_ERROR_RED};">{escalation_count}</h3>
            <p style="margin: 0.5rem 0 0 0; color: {ART_TEXT_GRAY};">Need Escalation</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Calculate average utterances - ensure numeric type
        utterance_col = pd.to_numeric(filtered_calls['utterance_count'], errors='coerce')
        avg_utterances = utterance_col.mean()
        if pd.isna(avg_utterances):
            avg_display = "N/A"
        else:
            avg_display = f"{avg_utterances:.1f}"
        
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0; color: {ART_PRIMARY_BLUE};">{avg_display}</h3>
            <p style="margin: 0.5rem 0 0 0; color: {ART_TEXT_GRAY};">Avg Utterances</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Escalation alerts section
    st.markdown("## 🚨 Escalation Alerts")
    
    # Get escalation data for calls that need it - ONLY show calls with escalations
    escalation_calls = []
    
    # Use cached escalation map (only contains calls with escalations)
    call_ids_list = filtered_calls['call_id'].tolist()
    cache_key = f"escalation_data_{hash(tuple(sorted(call_ids_list)))}"
    escalation_map = st.session_state.get(cache_key, {})
    
    # Only process calls that are in escalation_map (they need escalation)
    for _, row in filtered_calls.iterrows():
        escalation_data = escalation_map.get(row['call_id'])
        if escalation_data and len(escalation_data) >= 7:
            escalation_recommended = escalation_data[0]
            # Ensure risk_score is numeric
            try:
                risk_score = int(escalation_data[1]) if escalation_data[1] is not None else 0
            except (ValueError, TypeError):
                risk_score = 0
            risk_factors = escalation_data[2] if escalation_data[2] else "None"
            negative_count = escalation_data[3]
            compliance_count = escalation_data[4]
            complaint_count = escalation_data[5]
            recommendation = escalation_data[6]
            
            # Only add if escalation_recommended is TRUE (not just high risk_score)
            if escalation_recommended:
                call_info = {
                    'call_id': row['call_id'],
                    'member_name': row['member_name'],
                    'agent_id': row['agent_id'],
                    'scenario': row['scenario'],
                    'utterance_count': row['utterance_count'],
                    'escalation_recommended': escalation_recommended,
                    'risk_score': risk_score,
                    'risk_factors': risk_factors,
                    'negative_count': negative_count,
                    'compliance_count': compliance_count,
                    'complaint_count': complaint_count,
                    'recommendation': recommendation
                }
                escalation_calls.append(call_info)
    
    # Filter based on escalation filter
    if escalation_filter == "Escalation Needed":
        display_calls = [c for c in escalation_calls if c['escalation_recommended']]
    elif escalation_filter == "Monitor Closely":
        display_calls = []  # Only show escalation_recommended calls, not just high risk_score
    elif escalation_filter == "Normal":
        display_calls = []  # Don't show normal calls in escalation alerts section
    else:
        display_calls = escalation_calls  # Show all escalation calls (all have escalation_recommended = TRUE)
    
    # Sort by risk score (highest first)
    display_calls.sort(key=lambda x: x['risk_score'], reverse=True)
    
    # Only show escalation alerts if there are any
    if display_calls:
        for call_info in display_calls:
            # All calls in display_calls have escalation_recommended = TRUE
            if call_info['escalation_recommended']:
                if call_info['risk_score'] >= 12:
                    alert_class = "escalation-critical"
                    alert_title = "🚨 ESCALATION REQUIRED"
                else:
                    alert_class = "escalation-critical"
                    alert_title = "🚨 ESCALATION REQUIRED"
            else:
                continue  # Skip calls that don't need escalation (shouldn't happen, but safety check)
            
            st.markdown(f"""
            <div class="{alert_class}">
                <strong>{alert_title}</strong><br>
                <strong>Call ID:</strong> {call_info['call_id'][-8:]}<br>
                <strong>Member:</strong> {call_info['member_name']}<br>
                <strong>Agent:</strong> {call_info['agent_id']}<br>
                <strong>Scenario:</strong> {call_info['scenario']}<br>
                <strong>Risk Score:</strong> {call_info['risk_score']}<br>
                <strong>Risk Factors:</strong> {call_info['risk_factors']}<br>
                <strong>Negative Sentiments:</strong> {call_info['negative_count']}<br>
                <strong>Compliance Violations:</strong> {call_info['compliance_count']}<br>
                <strong>Complaint Intents:</strong> {call_info['complaint_count']}<br>
                <br>
                <strong>Recommendation:</strong><br>
                {call_info['recommendation']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No escalations needed - all calls proceeding normally")
    
    st.markdown("---")
    
    # All active calls table
    st.markdown("## 📞 All Active Calls")
    
    # Add escalation status to dataframe - use cached escalation map
    display_df = filtered_calls.copy()
    escalation_statuses = []
    risk_scores = []
    
    # Use cached escalation map (only contains calls with escalations)
    call_ids_list = filtered_calls['call_id'].tolist()
    cache_key = f"escalation_data_{hash(tuple(sorted(call_ids_list)))}"
    escalation_map = st.session_state.get(cache_key, {})
    
    for _, row in filtered_calls.iterrows():
        escalation_data = escalation_map.get(row['call_id'])
        if escalation_data and len(escalation_data) >= 7:
            escalation_statuses.append("🚨 Escalation" if escalation_data[0] else "✅ Normal")
            # Ensure risk_score is numeric
            try:
                risk_score = int(escalation_data[1]) if escalation_data[1] is not None else 0
            except (ValueError, TypeError):
                risk_score = 0
            risk_scores.append(risk_score)
        else:
            # Not in escalation_map = no escalation needed
            escalation_statuses.append("✅ Normal")
            risk_scores.append(0)
    
    display_df['Escalation Status'] = escalation_statuses
    display_df['Risk Score'] = risk_scores
    
    # Format for display
    display_df['Call ID'] = display_df['call_id'].str[-8:]
    display_df['Last Activity'] = pd.to_datetime(display_df['last_utterance_time']).dt.strftime('%H:%M:%S')
    
    st.dataframe(
        display_df[['Call ID', 'member_name', 'agent_id', 'scenario', 'utterance_count', 'Risk Score', 'Escalation Status']].rename(columns={
            'member_name': 'Member',
            'agent_id': 'Agent',
            'scenario': 'Scenario',
            'utterance_count': 'Utterances'
        }),
        use_container_width=True,
        hide_index=True
    )
    
else:
    st.info("No active calls to display")

