#!/usr/bin/env python3
"""
ART Live Agent Assist Dashboard
3-column Streamlit interface for call center agents with real-time AI assistance.

Run: streamlit run app/agent_dashboard.py
"""
import streamlit as st
import sys
from pathlib import Path
import time
from datetime import datetime, timedelta
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks import sql
from databricks.sdk import WorkspaceClient
from config.config import (
    get_workspace_url, SQL_WAREHOUSE_ID,
    ENRICHED_TABLE, FUNCTION_GET_CALL_CONTEXT,
    FUNCTION_SEARCH_KB, FUNCTION_CHECK_COMPLIANCE,
    FUNCTION_GET_MEMBER_HISTORY
)
import os

# Page configuration
st.set_page_config(
    page_title="ART Live Agent Assist",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Australian Retirement Trust Brand Colors
# Based on ART website: Blue (#0051FF), White, Professional tone
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

# Custom CSS for ART Branding
st.markdown(f"""
<style>
    /* Australian Retirement Trust Brand Colors */
    :root {{
        --art-primary-blue: {ART_PRIMARY_BLUE};
        --art-dark-blue: {ART_DARK_BLUE};
        --art-light-blue: {ART_LIGHT_BLUE};
        --art-accent-blue: {ART_ACCENT_BLUE};
        --art-text-dark: {ART_TEXT_DARK};
        --art-text-gray: {ART_TEXT_GRAY};
        --art-bg-light: {ART_BG_LIGHT};
        --art-border: {ART_BORDER};
        --art-white: {ART_WHITE};
        --art-success: {ART_SUCCESS_GREEN};
        --art-warning: {ART_WARNING_ORANGE};
        --art-error: {ART_ERROR_RED};
    }}
    
    /* Import professional font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Main container */
    .main {{
        background-color: var(--art-bg-light);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}
    
    /* Header - ART Branding */
    .header-container {{
        background: linear-gradient(135deg, {ART_PRIMARY_BLUE} 0%, {ART_ACCENT_BLUE} 100%);
        padding: 2rem 2.5rem;
        border-radius: 0;
        margin: -1rem -1rem 2rem -1rem;
        box-shadow: 0 4px 12px rgba(0, 81, 255, 0.15);
        position: relative;
        overflow: hidden;
    }}
    
    .header-container::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: repeating-linear-gradient(
            45deg,
            transparent,
            transparent 10px,
            rgba(255, 255, 255, 0.03) 10px,
            rgba(255, 255, 255, 0.03) 20px
        );
        pointer-events: none;
    }}
    
    .header-title {{
        color: {ART_WHITE};
        font-size: 2.25rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.02em;
        position: relative;
        z-index: 1;
    }}
    
    .header-subtitle {{
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.1rem;
        margin-top: 0.75rem;
        font-weight: 400;
        position: relative;
        z-index: 1;
        line-height: 1.6;
    }}
    
    /* Transcript bubbles */
    .transcript-bubble {{
        padding: 1rem 1.25rem;
        border-radius: 12px;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
        font-size: 0.95rem;
        line-height: 1.6;
    }}
    
    .transcript-customer {{
        background-color: {ART_LIGHT_BLUE};
        border-left: 3px solid {ART_PRIMARY_BLUE};
        margin-left: 15%;
    }}
    
    .transcript-agent {{
        background-color: {ART_WHITE};
        border-left: 3px solid {ART_SUCCESS_GREEN};
        margin-right: 15%;
        border: 1px solid {ART_BORDER};
    }}
    
    /* Compliance alert */
    .compliance-alert {{
        background-color: #FFF3E0;
        border-left: 4px solid {ART_WARNING_ORANGE};
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }}
    
    .compliance-critical {{
        background-color: #FFEBEE;
        border-left: 4px solid {ART_ERROR_RED};
    }}
    
    /* AI suggestion card */
    .suggestion-card {{
        background-color: {ART_WHITE};
        border: 1px solid {ART_BORDER};
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }}
    
    /* Button styling */
    .stButton > button {{
        background-color: {ART_PRIMARY_BLUE};
        color: {ART_WHITE};
        border-radius: 8px;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        width: 100%;
    }}
    
    .stButton > button:hover {{
        background-color: {ART_DARK_BLUE};
        box-shadow: 0 4px 8px rgba(0, 81, 255, 0.3);
    }}
    
    /* Status indicator */
    .status-indicator {{
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }}
    
    .status-online {{
        background-color: {ART_SUCCESS_GREEN};
        box-shadow: 0 0 0 2px rgba(0, 166, 81, 0.2);
    }}
    
    /* Hide Streamlit default elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Column styling */
    .stColumn {{
        padding: 0 0.5rem;
    }}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_sql_connection():
    """Get SQL connection to Databricks"""
    workspace_url = get_workspace_url()
    # Try to get token from environment or use WorkspaceClient
    token = os.environ.get('DATABRICKS_TOKEN')
    if not token:
        try:
            from databricks.sdk import WorkspaceClient
            w = WorkspaceClient()
            token = w.config.token
        except:
            pass
    
    if not token:
        st.error("DATABRICKS_TOKEN not found. Please set it as environment variable.")
        st.stop()
    
    return sql.connect(
        server_hostname=workspace_url.replace('https://', ''),
        http_path=f'/sql/1.0/warehouses/{SQL_WAREHOUSE_ID}',
        access_token=token
    )

@st.cache_resource
def get_agent():
    """Get GenAI agent"""
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from scripts.genai_agent import create_agent
        return create_agent()
    except Exception as e:
        st.error(f"Agent not available: {e}")
        return None

def get_active_calls():
    """Get active calls from last 10 minutes"""
    conn = get_sql_connection()
    cursor = conn.cursor()
    
    query = f"""
    SELECT DISTINCT
        call_id,
        member_name,
        member_id,
        scenario,
        MIN(timestamp) as call_start,
        COUNT(*) as utterances
    FROM {ENRICHED_TABLE}
    WHERE timestamp > CURRENT_TIMESTAMP() - INTERVAL 10 MINUTE
    GROUP BY call_id, member_name, member_id, scenario
    ORDER BY call_start DESC
    LIMIT 20
    """
    
    cursor.execute(query)
    return cursor.fetchall()

def get_live_transcript(call_id):
    """Get live transcript for a call"""
    conn = get_sql_connection()
    
    query = f"""
    SELECT 
        timestamp,
        speaker,
        transcript_segment,
        sentiment,
        intent_category,
        compliance_flag,
        compliance_severity
    FROM {ENRICHED_TABLE}
    WHERE call_id = '{call_id}'
    ORDER BY timestamp ASC
    LIMIT 50
    """
    
    df = pd.read_sql(query, conn)
    return df

def get_ai_suggestion(call_id):
    """Get AI suggestion for call"""
    agent = get_agent()
    if not agent:
        return "Agent not available. Please check configuration."
    
    try:
        result = agent.invoke({
            'messages': [{
                'role': 'user',
                'content': f'Help me with call {call_id}. Provide context and suggest next response.'
            }]
        })
        
        if isinstance(result, dict) and 'messages' in result:
            last_message = result['messages'][-1]
            return last_message.content
        return str(result)
    except Exception as e:
        return f"Error getting suggestion: {e}"

def get_compliance_alerts(call_id):
    """Get compliance alerts for a call"""
    conn = get_sql_connection()
    cursor = conn.cursor()
    
    query = f"SELECT * FROM {FUNCTION_CHECK_COMPLIANCE}('{call_id}')"
    cursor.execute(query)
    return cursor.fetchall()

# Header with logo
logo_path = Path(__file__).parent.parent / "logo.svg"

col1, col2 = st.columns([1, 5])
with col1:
    try:
        if logo_path.exists():
            st.image(str(logo_path), width=140)
        else:
            st.markdown("### 📞")
    except Exception as e:
        st.markdown("### 📞")

with col2:
    st.markdown(f"""
    <div class="header-container">
        <h1 class="header-title">Live Agent Assist</h1>
        <p class="header-subtitle">Real-time AI assistance for Australian Retirement Trust member service representatives</p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar - Active calls
with st.sidebar:
    st.markdown("### 📞 Active Calls")
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("Auto-refresh (5s)", value=True)
    
    # Get active calls
    try:
        active_calls = get_active_calls()
        
        if active_calls:
            call_options = {
                f"{call[1]} ({call[0][-8:]})": call[0] 
                for call in active_calls
            }
            
            selected_call_display = st.selectbox(
                "Select Call to Monitor",
                options=list(call_options.keys()),
                key="call_selector"
            )
            
            selected_call_id = call_options[selected_call_display]
            
            # Show call info
            selected_call_info = next(c for c in active_calls if c[0] == selected_call_id)
            st.markdown("---")
            st.markdown(f"**Member:** {selected_call_info[1]}")
            st.markdown(f"**Scenario:** {selected_call_info[3]}")
            st.markdown(f"**Utterances:** {selected_call_info[4]}")
        else:
            st.warning("No active calls in last 10 minutes")
            selected_call_id = None
    except Exception as e:
        st.error(f"Error loading calls: {e}")
        selected_call_id = None
    
    st.markdown("---")
    st.markdown("""
    <div>
        <span class="status-indicator status-online"></span>
        <strong>System Online</strong>
    </div>
    """, unsafe_allow_html=True)

# Main dashboard - 3 column layout
if selected_call_id:
    col1, col2, col3 = st.columns([2, 2, 1])
    
    # COLUMN 1: Live Transcript
    with col1:
        st.header("📝 Live Transcript")
        
        try:
            transcript_df = get_live_transcript(selected_call_id)
            
            if not transcript_df.empty:
                # Display transcript
                for idx, row in transcript_df.iterrows():
                    speaker_icon = "👤" if row['speaker'] == "customer" else "👔"
                    timestamp_str = pd.to_datetime(row['timestamp']).strftime("%H:%M:%S")
                    
                    # Sentiment emoji
                    sentiment_emoji = {
                        'positive': '😊',
                        'negative': '😟',
                        'neutral': '😐'
                    }.get(row['sentiment'], '😐')
                    
                    # Compliance warning
                    if row['compliance_severity'] in ['HIGH', 'CRITICAL']:
                        alert_class = "compliance-critical" if row['compliance_severity'] == 'CRITICAL' else "compliance-alert"
                        st.markdown(f"""
                        <div class="{alert_class}">
                            <strong>⚠️ COMPLIANCE WARNING [{row['compliance_severity']}]</strong><br>
                            {row['compliance_flag'].replace('_', ' ').title()}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Transcript bubble
                    bubble_class = "transcript-customer" if row['speaker'] == "customer" else "transcript-agent"
                    speaker_label = "Member" if row['speaker'] == "customer" else "Agent"
                    
                    st.markdown(f"""
                    <div class="transcript-bubble {bubble_class}">
                        <strong>{speaker_icon} {speaker_label}</strong> {sentiment_emoji} 
                        <small style="color: {ART_TEXT_GRAY};">{timestamp_str}</small><br>
                        {row['transcript_segment']}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No transcript data available yet")
        except Exception as e:
            st.error(f"Error loading transcript: {e}")
    
    # COLUMN 2: AI Suggestions
    with col2:
        st.header("🤖 AI Assistant")
        
        tab1, tab2, tab3 = st.tabs(["💡 Suggestions", "👤 Member Info", "📚 Knowledge Base"])
        
        with tab1:
            st.subheader("AI-Generated Suggestions")
            
            if st.button("🔄 Get AI Suggestion", key="get_suggestion"):
                with st.spinner("Analyzing call context..."):
                    suggestion = get_ai_suggestion(selected_call_id)
                    st.session_state['last_suggestion'] = suggestion
                    st.session_state['last_call_id'] = selected_call_id
            
            # Show last suggestion if available
            if 'last_suggestion' in st.session_state and st.session_state.get('last_call_id') == selected_call_id:
                st.markdown(f"""
                <div class="suggestion-card">
                    {st.session_state['last_suggestion']}
                </div>
                """, unsafe_allow_html=True)
        
        with tab2:
            st.subheader("Member 360 View")
            
            try:
                conn = get_sql_connection()
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {FUNCTION_GET_CALL_CONTEXT}('{selected_call_id}')")
                context = cursor.fetchone()
                
                if context:
                    st.metric("Member Name", context[0] or "N/A")
                    st.metric("Balance", f"${context[1]:,.2f}" if context[1] else "N/A")
                    st.markdown(f"**Recent Transcript:**")
                    st.info(context[2][:200] + "..." if context[2] and len(context[2]) > 200 else (context[2] or "N/A"))
                    st.markdown(f"**Sentiment:** {context[3] or 'N/A'}")
                    st.markdown(f"**Intents:** {context[4] or 'N/A'}")
                    st.markdown(f"**Compliance Issues:** {context[5] or 'None'}")
            except Exception as e:
                st.error(f"Error loading member info: {e}")
        
        with tab3:
            st.subheader("Knowledge Base")
            
            search_query = st.text_input("Search KB", key="kb_search")
            if st.button("🔍 Search", key="search_kb"):
                try:
                    conn = get_sql_connection()
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT * FROM {FUNCTION_SEARCH_KB}('{search_query}')")
                    articles = cursor.fetchall()
                    
                    for article in articles:
                        st.markdown(f"""
                        <div class="suggestion-card">
                            <strong>[{article[0]}] {article[1]}</strong><br>
                            {article[2]}
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error searching KB: {e}")
    
    # COLUMN 3: Compliance Alerts
    with col3:
        st.header("⚠️ Compliance Alerts")
        
        try:
            alerts = get_compliance_alerts(selected_call_id)
            
            if alerts:
                for alert in alerts:
                    severity = alert[1]
                    alert_class = "compliance-critical" if severity == 'CRITICAL' else "compliance-alert"
                    
                    st.markdown(f"""
                    <div class="{alert_class}">
                        <strong>{severity}</strong><br>
                        {alert[0]}<br>
                        <small>{alert[2][:100]}...</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ No compliance issues")
        except Exception as e:
            st.error(f"Error loading alerts: {e}")
        
        st.markdown("---")
        st.markdown("### 📊 Call Metrics")
        
        try:
            transcript_df = get_live_transcript(selected_call_id)
            if not transcript_df.empty:
                sentiment_counts = transcript_df['sentiment'].value_counts()
                st.metric("Positive", sentiment_counts.get('positive', 0))
                st.metric("Neutral", sentiment_counts.get('neutral', 0))
                st.metric("Negative", sentiment_counts.get('negative', 0))
                
                intent_counts = transcript_df['intent_category'].value_counts()
                st.markdown("**Top Intents:**")
                for intent, count in intent_counts.head(3).items():
                    st.caption(f"{intent}: {count}")
        except:
            pass

else:
    st.info("👈 Select an active call from the sidebar to begin")

# Auto-refresh logic using Streamlit's built-in mechanism
if auto_refresh and selected_call_id:
    # Use st.empty() with a timer to trigger refresh
    refresh_placeholder = st.empty()
    with refresh_placeholder.container():
        # This will cause a rerun after the page loads
        if 'refresh_count' not in st.session_state:
            st.session_state['refresh_count'] = 0
        st.session_state['refresh_count'] += 1
        
        # Use JavaScript to trigger refresh after 5 seconds
        st.markdown("""
        <script>
        setTimeout(function() {
            window.location.reload();
        }, 5000);
        </script>
        """, unsafe_allow_html=True)

