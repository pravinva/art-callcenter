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

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
from config.config import (
    get_workspace_url, SQL_WAREHOUSE_ID,
    ENRICHED_TABLE, FUNCTION_GET_CALL_CONTEXT,
    FUNCTION_SEARCH_KB, FUNCTION_CHECK_COMPLIANCE,
    FUNCTION_GET_MEMBER_HISTORY, FUNCTION_IDENTIFY_ESCALATION
)
import os
import time

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
        max-width: 100% !important;
        padding: 0 2rem;
    }}
    
    /* Make page wider */
    .block-container {{
        max-width: 100% !important;
        padding-left: 2rem;
        padding-right: 2rem;
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
    
    /* Column styling */
    .stColumn {{
        padding: 0 0.5rem;
    }}
    
    /* Section spacing */
    .section-container {{
        margin-bottom: 2rem;
        padding: 1.5rem;
        background-color: {ART_WHITE};
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }}
    
    .section-header {{
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid {ART_LIGHT_BLUE};
    }}
    
    /* Add spacing between sections */
    .section-spacer {{
        margin-top: 2rem;
        margin-bottom: 2rem;
        height: 1px;
        background: linear-gradient(to right, transparent, {ART_BORDER}, transparent);
    }}
    
    /* Column 1 (Live Transcript) - near sidebar */
    div[data-testid="column"]:nth-of-type(1) {{
        padding-left: 0.5rem;
        padding-right: 1rem;
    }}
    
    /* Column 2 (AI Assistant) - middle */
    div[data-testid="column"]:nth-of-type(2) {{
        padding-left: 1rem;
        padding-right: 1rem;
    }}
    
    /* Column 3 (Escalation/Compliance) - right side */
    div[data-testid="column"]:nth-of-type(3) {{
        padding-left: 1rem;
        padding-right: 0.5rem;
    }}
    
    div[data-testid="column"]:nth-of-type(3) .section-container {{
        margin-bottom: 2.5rem;
    }}
    
    div[data-testid="column"]:nth-of-type(3) h3 {{
        margin-top: 0;
        margin-bottom: 1rem;
    }}
    
    /* Header spacing */
    h3 {{
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }}
    
    /* Compliance alert */
    .compliance-alert {{
        background-color: #FFF3E0;
        border-left: 4px solid {ART_WARNING_ORANGE};
        padding: 1.25rem;
        border-radius: 8px;
        margin: 1rem 0;
        line-height: 1.6;
    }}
    
    .compliance-critical {{
        background-color: #FFEBEE;
        border-left: 4px solid {ART_ERROR_RED};
        padding: 1.25rem;
        margin: 1rem 0;
        line-height: 1.6;
    }}
    
    /* Escalation alert */
    .escalation-alert {{
        background-color: #FFF3E0;
        border-left: 4px solid {ART_WARNING_ORANGE};
        padding: 1.25rem;
        border-radius: 8px;
        margin: 1rem 0;
        line-height: 1.6;
    }}
    
    .escalation-critical {{
        background-color: #FFF3E0;
        border-left: 4px solid {ART_WARNING_ORANGE};
        font-weight: 500;
        padding: 1.25rem;
        margin: 1rem 0;
        line-height: 1.6;
        color: {ART_TEXT_DARK};
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
def get_workspace_client():
    """Get WorkspaceClient - cached to avoid multiple connections"""
    return WorkspaceClient()

def execute_sql(query, return_dataframe=False):
    """Execute SQL using Databricks SDK - optimized for speed"""
    w = get_workspace_client()
    
    try:
        # Execute SQL statement with shorter timeout
        response = w.statement_execution.execute_statement(
            warehouse_id=SQL_WAREHOUSE_ID,
            statement=query,
            wait_timeout="10s"  # Reduced from 30s
        )
        
        # Wait for completion and get manifest - faster polling
        statement_id = response.statement_id
        max_wait = 10  # Reduced from 30s
        waited = 0
        result_manifest = None
        
        while waited < max_wait:
            status = w.statement_execution.get_statement(statement_id)
            if status.status.state == StatementState.SUCCEEDED:
                # Get manifest from statement response
                if status.manifest:
                    result_manifest = status.manifest
                break
            elif status.status.state in [StatementState.FAILED, StatementState.CANCELED]:
                # Try to get error message from various sources
                error_msg = f"SQL execution failed: {status.status.state}"
                
                # Check status object for error details
                if hasattr(status.status, 'message') and status.status.message:
                    error_msg = status.status.message
                elif hasattr(status.status, 'state_message') and status.status.state_message:
                    error_msg = status.status.state_message
                
                # Check if there's error information in the result
                if hasattr(status, 'result') and status.result:
                    if hasattr(status.result, 'error') and status.result.error:
                        if hasattr(status.result.error, 'message'):
                            error_msg = status.result.error.message
                        elif isinstance(status.result.error, dict):
                            error_msg = str(status.result.error)
                        else:
                            error_msg = str(status.result.error)
                
                # Try to get error from status attributes
                status_dict = {}
                if hasattr(status.status, '__dict__'):
                    status_dict = status.status.__dict__
                    if 'error' in status_dict and status_dict['error']:
                        error_msg = str(status_dict['error'])
                    elif 'message' in status_dict and status_dict['message']:
                        error_msg = status_dict['message']
                
                raise Exception(error_msg)
            time.sleep(0.2)  # Faster polling - 0.2s instead of 0.5s
            waited += 0.2
        
        if waited >= max_wait:
            raise Exception("SQL execution timed out")
        
        if not result_manifest:
            raise Exception("Could not retrieve result manifest")
        
        # Get results - may need to get multiple chunks
        all_rows = []
        chunk_index = 0
        
        while True:
            result_chunk = w.statement_execution.get_statement_result_chunk_n(statement_id, chunk_index)
            if not result_chunk or not result_chunk.data_array:
                break
            
            all_rows.extend(result_chunk.data_array)
            
            # Check if there are more chunks
            if not result_chunk.next_chunk_index or result_chunk.next_chunk_index == chunk_index:
                break
            chunk_index = result_chunk.next_chunk_index
        
        if return_dataframe:
            # Convert to DataFrame
            if all_rows and result_manifest and result_manifest.schema and result_manifest.schema.columns:
                columns = [col.name for col in result_manifest.schema.columns]
                df = pd.DataFrame(all_rows, columns=columns)
                return df
            elif all_rows:
                # Fallback: infer column names from data if schema not available
                # Try to get column names from first row structure
                if all_rows and isinstance(all_rows[0], dict):
                    columns = list(all_rows[0].keys())
                    df = pd.DataFrame(all_rows)
                    return df
                # If data is array/list, use generic column names
                num_cols = len(all_rows[0]) if all_rows else 0
                columns = [f"col_{i+1}" for i in range(num_cols)]
                df = pd.DataFrame(all_rows, columns=columns)
                return df
            return pd.DataFrame()
        else:
            # Return raw results as list of tuples/lists
            return all_rows
            
    except Exception as e:
        st.error(f"SQL execution error: {e}")
        import traceback
        st.code(traceback.format_exc())
        raise

@st.cache_resource
def get_agent():
    """Get GenAI agent"""
    try:
        # Import agent creation function directly
        import importlib.util
        agent_script_path = Path(__file__).parent.parent / "scripts" / "07_genai_agent.py"
        
        if not agent_script_path.exists():
            st.error(f"Agent script not found: {agent_script_path}")
            return None
        
        spec = importlib.util.spec_from_file_location("genai_agent", agent_script_path)
        genai_agent_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(genai_agent_module)
        
        # Get the create_agent function
        if hasattr(genai_agent_module, 'create_agent'):
            agent = genai_agent_module.create_agent()
            return agent
        else:
            st.error("create_agent function not found in agent script")
            return None
            
    except Exception as e:
        st.error(f"Agent not available: {e}")
        import traceback
        st.code(traceback.format_exc())
        return None

def get_active_calls():
    """Get active calls from last 10 minutes"""
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
    
    results = execute_sql(query, return_dataframe=False)
    return results

def get_live_transcript(call_id):
    """Get live transcript for a call"""
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
    
    df = execute_sql(query, return_dataframe=True)
    return df

def get_ai_suggestion(call_id):
    """Get AI suggestion for call - optimized for speed with caching and timing"""
    import time as time_module
    start_time = time_module.time()
    
    # Check cache first (30 second cache)
    cache_key = f'ai_suggestion_{call_id}'
    if cache_key in st.session_state:
        cached_result, cached_time = st.session_state[cache_key]
        if time_module.time() - cached_time < 30:
            elapsed = time_module.time() - start_time
            return cached_result, elapsed
    
    agent = get_agent()
    if not agent:
        return "Agent not available. Please check configuration.", 0
    
    try:
        # Optimized prompt - more direct, less verbose
        prompt = f"""Call ID: {call_id}
        
Analyze this call and provide:
1. Brief context summary (2-3 sentences)
2. Suggested agent response (1-2 sentences)
3. Any compliance concerns

Be concise and actionable."""
        
        result = agent.invoke({
            'messages': [{
                'role': 'user',
                'content': prompt
            }]
        })
        
        elapsed_time = time_module.time() - start_time
        
        if isinstance(result, dict) and 'messages' in result:
            last_message = result['messages'][-1]
            response = last_message.content
            
            # Cache the result
            st.session_state[cache_key] = (response, time_module.time())
            return response, elapsed_time
        return str(result), elapsed_time
    except Exception as e:
        elapsed_time = time_module.time() - start_time
        return f"Error getting suggestion: {e}", elapsed_time

def get_compliance_alerts(call_id):
    """Get compliance alerts for a call"""
    query = f"SELECT * FROM {FUNCTION_CHECK_COMPLIANCE}('{call_id}')"
    results = execute_sql(query, return_dataframe=False)
    return results

def get_escalation_triggers(call_id):
    """Get escalation triggers for a call"""
    try:
        query = f"SELECT * FROM {FUNCTION_IDENTIFY_ESCALATION}('{call_id}')"
        results = execute_sql(query, return_dataframe=False)
        return results
    except Exception as e:
        # Return empty list on error instead of raising
        print(f"Error getting escalation triggers: {e}")
        return []

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

# Initialize session state for persistent data
if 'selected_call_id' not in st.session_state:
    st.session_state['selected_call_id'] = None
if 'transcript_data' not in st.session_state:
    st.session_state['transcript_data'] = None
if 'member_context' not in st.session_state:
    st.session_state['member_context'] = None
if 'escalation_data' not in st.session_state:
    st.session_state['escalation_data'] = None
if 'compliance_alerts' not in st.session_state:
    st.session_state['compliance_alerts'] = None
if 'call_metrics' not in st.session_state:
    st.session_state['call_metrics'] = None

# Sidebar - Active calls
with st.sidebar:
    st.markdown("### 📞 Active Calls")

    # Auto-refresh toggle (disabled - was causing new tabs to open)
    auto_refresh = st.checkbox("Auto-refresh (disabled)", value=False, disabled=True, help="Auto-refresh disabled to prevent new tabs. Refresh page manually.")

    # Get active calls
    try:
        active_calls = get_active_calls()

        if active_calls:
            call_options = {
                f"{call[1]} ({call[0][-8:]})": call[0]
                for call in active_calls
            }

            # Get previously selected call if it exists
            if st.session_state['selected_call_id'] and st.session_state['selected_call_id'] in call_options.values():
                # Find the display name for the selected call
                selected_display = next((k for k, v in call_options.items() if v == st.session_state['selected_call_id']), list(call_options.keys())[0])
                default_index = list(call_options.keys()).index(selected_display) if selected_display in call_options else 0
            else:
                default_index = 0

            selected_call_display = st.selectbox(
                "Select Call to Monitor",
                options=list(call_options.keys()),
                index=default_index,
                key="call_selector"
            )

            selected_call_id = call_options[selected_call_display]

            # If call changed, clear cached data
            if st.session_state['selected_call_id'] != selected_call_id:
                st.session_state['selected_call_id'] = selected_call_id
                st.session_state['transcript_data'] = None
                st.session_state['member_context'] = None
                st.session_state['escalation_data'] = None
                st.session_state['compliance_alerts'] = None
                st.session_state['call_metrics'] = None
                # Clear suggestion cache for new call
                if 'last_call_id' in st.session_state:
                    st.session_state['last_call_id'] = None
                    st.session_state['last_suggestion'] = None

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

# Main dashboard - 3 column layout (wider, transcript near sidebar)
if selected_call_id:
    col1, col2, col3 = st.columns([2.5, 3, 2])
    
    # COLUMN 1: Live Transcript
    with col1:
        st.header("📝 Live Transcript")

        try:
            # Load transcript with spinner if not cached
            if st.session_state['transcript_data'] is None or st.session_state.get('transcript_call_id') != selected_call_id:
                with st.spinner("🔄 Loading transcript..."):
                    transcript_df = get_live_transcript(selected_call_id)
                    st.session_state['transcript_data'] = transcript_df
                    st.session_state['transcript_call_id'] = selected_call_id
            else:
                transcript_df = st.session_state['transcript_data']

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
            
            # Initialize session state for async-like behavior
            if 'suggestion_loading' not in st.session_state:
                st.session_state['suggestion_loading'] = False
            if 'suggestion_error' not in st.session_state:
                st.session_state['suggestion_error'] = None
            if 'suggestion_response_time' not in st.session_state:
                st.session_state['suggestion_response_time'] = None
            
            # Create empty containers for dynamic updates (prevents freezing)
            suggestion_placeholder = st.empty()
            loading_placeholder = st.empty()
            error_placeholder = st.empty()
            
            # Button to get suggestion - sets flag instead of blocking
            if st.button("🔄 Get AI Suggestion", key="get_suggestion", use_container_width=True):
                st.session_state['suggestion_loading'] = True
                st.session_state['suggestion_error'] = None
                st.session_state['suggestion_call_id'] = selected_call_id
                st.session_state['suggestion_trigger'] = True
                st.rerun()  # Trigger rerun to process in next cycle
            
            # Show loading indicator in placeholder (renders immediately)
            if st.session_state.get('suggestion_loading') and st.session_state.get('suggestion_call_id') == selected_call_id:
                loading_placeholder.info("🔄 Analyzing call context... (You can switch tabs - processing continues)")
            else:
                loading_placeholder.empty()
            
            # Show error if any
            if st.session_state.get('suggestion_error'):
                error_placeholder.error(f"Error: {st.session_state['suggestion_error']}")
            else:
                error_placeholder.empty()
            
            # Show last suggestion if available
            if not st.session_state.get('suggestion_loading') and 'last_suggestion' in st.session_state and st.session_state.get('last_call_id') == selected_call_id:
                response_time = st.session_state.get('suggestion_response_time', 0)
                time_display = f"<small style='color: {ART_TEXT_GRAY}; font-size: 0.85em; display: block; margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.1);'>⏱️ Response time: {response_time:.2f}s</small>" if response_time > 0 else ""
                suggestion_placeholder.markdown(f"""
                <div class="suggestion-card">
                    {st.session_state['last_suggestion']}
                    {time_display}
                </div>
                """, unsafe_allow_html=True)
            else:
                suggestion_placeholder.empty()
        
        with tab2:
            st.subheader("Member 360 View")

            try:
                # Load member context with spinner if not cached
                if st.session_state['member_context'] is None or st.session_state.get('member_context_call_id') != selected_call_id:
                    with st.spinner("🔄 Loading member info..."):
                        query = f"SELECT * FROM {FUNCTION_GET_CALL_CONTEXT}('{selected_call_id}')"
                        results = execute_sql(query, return_dataframe=False)
                        st.session_state['member_context'] = results
                        st.session_state['member_context_call_id'] = selected_call_id
                else:
                    results = st.session_state['member_context']

                if results and len(results) > 0:
                    context = results[0]  # First row
                    st.metric("Member Name", context[0] if len(context) > 0 else "N/A")
                    # Convert balance to float if it's a string, then format
                    balance_value = context[1] if len(context) > 1 and context[1] else None
                    if balance_value is not None:
                        try:
                            balance_float = float(balance_value) if isinstance(balance_value, str) else balance_value
                            st.metric("Balance", f"${balance_float:,.2f}")
                        except (ValueError, TypeError):
                            st.metric("Balance", str(balance_value))
                    else:
                        st.metric("Balance", "N/A")
                    st.markdown(f"**Recent Transcript:**")
                    transcript_text = context[2] if len(context) > 2 else "N/A"
                    st.info(transcript_text[:200] + "..." if transcript_text and len(str(transcript_text)) > 200 else (transcript_text or "N/A"))
                    st.markdown(f"**Sentiment:** {context[3] if len(context) > 3 else 'N/A'}")
                    st.markdown(f"**Intents:** {context[4] if len(context) > 4 else 'N/A'}")
                    st.markdown(f"**Compliance Issues:** {context[5] if len(context) > 5 else 'None'}")
                else:
                    st.info("No member context available")
            except Exception as e:
                st.error(f"Error loading member info: {e}")
        
        with tab3:
            st.subheader("Knowledge Base")
            
            search_query = st.text_input("Search KB", key="kb_search")
            kb_results_container = st.container()
            
            if st.button("🔍 Search", key="search_kb", use_container_width=True):
                with kb_results_container:
                    try:
                        query = f"SELECT * FROM {FUNCTION_SEARCH_KB}('{search_query}')"
                        articles = execute_sql(query, return_dataframe=False)
                        
                        if articles:
                            st.session_state['kb_results'] = articles
                            st.session_state['kb_query'] = search_query
                        else:
                            st.session_state['kb_results'] = []
                            st.info("No articles found")
                    except Exception as e:
                        st.error(f"Error searching KB: {e}")
            
            # Display KB results
            with kb_results_container:
                if 'kb_results' in st.session_state and st.session_state.get('kb_query') == search_query:
                    for article in st.session_state['kb_results']:
                        article_id = article[0] if len(article) > 0 else 'N/A'
                        title = article[1] if len(article) > 1 else 'N/A'
                        content = article[2] if len(article) > 2 else 'N/A'
                        st.markdown(f"""
                        <div class="suggestion-card">
                            <strong>[{article_id}] {title}</strong><br>
                            {content}
                        </div>
                        """, unsafe_allow_html=True)
    
    # COLUMN 3: Compliance Alerts & Escalation
    with col3:
        # Escalation Alerts (shown first if escalation needed)
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.header("🚨 Escalation Status")
        st.markdown('</div>', unsafe_allow_html=True)

        try:
            # Load escalation data with spinner if not cached
            if st.session_state['escalation_data'] is None or st.session_state.get('escalation_call_id') != selected_call_id:
                with st.spinner("🔄 Loading escalation status..."):
                    escalation_data = get_escalation_triggers(selected_call_id)
                    st.session_state['escalation_data'] = escalation_data
                    st.session_state['escalation_call_id'] = selected_call_id
            else:
                escalation_data = st.session_state['escalation_data']

            if escalation_data and len(escalation_data) > 0:
                escalation = escalation_data[0]
                if isinstance(escalation, (list, tuple)) and len(escalation) >= 7:
                    escalation_recommended = escalation[0]
                    risk_score = escalation[1]
                    risk_factors = escalation[2] if escalation[2] else "None"
                    negative_count = escalation[3]
                    compliance_count = escalation[4]
                    complaint_count = escalation[5]
                    recommendation = escalation[6]
                    
                    if escalation_recommended:
                        alert_class = "escalation-critical"
                        st.markdown(f"""
                        <div class="{alert_class}">
                            <strong>🚨 ESCALATION RECOMMENDED</strong><br>
                            <strong>Risk Score:</strong> {risk_score}<br>
                            <strong>Risk Factors:</strong> {risk_factors}<br>
                            <strong>Negative Sentiments:</strong> {negative_count}<br>
                            <strong>Compliance Violations:</strong> {compliance_count}<br>
                            <strong>Complaint Intents:</strong> {complaint_count}<br>
                            <br>
                            <strong>Recommendation:</strong><br>
                            {recommendation}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.success(f"✅ No escalation needed\n\n**Risk Score:** {risk_score}\n\n**Status:** {recommendation}")
                else:
                    st.info("Escalation data unavailable")
            else:
                st.info("Escalation data unavailable")
        except Exception as e:
            st.error(f"Error loading escalation: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Spacer between sections
        st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
        
        # Compliance Alerts
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.header("⚠️ Compliance Alerts")
        st.markdown('</div>', unsafe_allow_html=True)

        try:
            # Load compliance alerts with spinner if not cached
            if st.session_state['compliance_alerts'] is None or st.session_state.get('compliance_call_id') != selected_call_id:
                with st.spinner("🔄 Loading compliance alerts..."):
                    alerts = get_compliance_alerts(selected_call_id)
                    st.session_state['compliance_alerts'] = alerts
                    st.session_state['compliance_call_id'] = selected_call_id
            else:
                alerts = st.session_state['compliance_alerts']

            if alerts:
                for alert in alerts:
                    if isinstance(alert, (list, tuple)) and len(alert) >= 3:
                        violation_type = alert[0]
                        severity = alert[1]
                        segment = alert[2]
                    else:
                        violation_type = str(alert[0]) if len(alert) > 0 else "Unknown"
                        severity = str(alert[1]) if len(alert) > 1 else "LOW"
                        segment = str(alert[2]) if len(alert) > 2 else ""
                    
                    alert_class = "compliance-critical" if severity == 'CRITICAL' else "compliance-alert"
                    
                    st.markdown(f"""
                    <div class="{alert_class}">
                        <strong>{severity}</strong><br>
                        {violation_type}<br>
                        <small>{segment[:100]}...</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ No compliance issues")
        except Exception as e:
            st.error(f"Error loading alerts: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Spacer between sections
        st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
        
        # Call Metrics
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">', unsafe_allow_html=True)
        st.markdown("### 📊 Call Metrics")
        st.markdown('</div>', unsafe_allow_html=True)

        try:
            # Use cached transcript data for metrics
            if st.session_state['transcript_data'] is not None:
                transcript_df = st.session_state['transcript_data']
            else:
                with st.spinner("🔄 Loading metrics..."):
                    transcript_df = get_live_transcript(selected_call_id)
                    st.session_state['transcript_data'] = transcript_df

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
        
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("👈 Select an active call from the sidebar to begin")

# Process AI suggestion AFTER all UI is rendered (prevents tab freezing)
# This runs at the end, so tabs render first, then processing happens
if st.session_state.get('suggestion_trigger') and st.session_state.get('suggestion_call_id'):
    try:
        # This will block, but all tabs have already rendered
        suggestion, elapsed_time = get_ai_suggestion(st.session_state['suggestion_call_id'])
        st.session_state['last_suggestion'] = suggestion
        st.session_state['last_call_id'] = st.session_state['suggestion_call_id']
        st.session_state['suggestion_response_time'] = elapsed_time
        st.session_state['suggestion_loading'] = False
        st.session_state['suggestion_error'] = None
        st.session_state['suggestion_trigger'] = False
        st.rerun()  # Update UI with result
    except Exception as e:
        st.session_state['suggestion_error'] = str(e)
        st.session_state['suggestion_loading'] = False
        st.session_state['suggestion_trigger'] = False
        st.session_state['suggestion_response_time'] = None
        st.rerun()

# Auto-refresh disabled - was causing new tabs to open
# Users can manually refresh the page if needed
# Future: Implement proper Streamlit rerun mechanism if auto-refresh is needed

