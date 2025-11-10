#!/usr/bin/env python3
"""
ART Live Agent Assist Dashboard
3-column Streamlit interface for call center agents with real-time AI assistance.

Run: streamlit run app/agent_dashboard.py
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
    FUNCTION_SEARCH_KB, FUNCTION_CHECK_COMPLIANCE,
    FUNCTION_GET_MEMBER_HISTORY,
    VECTOR_SEARCH_ENDPOINT, KB_INDEX_NAME, KB_TABLE
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
    
    /* Live Call Header - Prominent with ringing animation */
    .live-call-header {{
        background: linear-gradient(135deg, {ART_PRIMARY_BLUE} 0%, {ART_ACCENT_BLUE} 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 81, 255, 0.25);
        border: 2px solid {ART_ACCENT_BLUE};
    }}
    
    .live-call-title {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        color: {ART_WHITE};
        font-size: 1.75rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }}
    
    .live-call-title span:first-child {{
        font-size: 2rem;
        animation: ring 2s ease-in-out infinite;
    }}
    
    @keyframes ring {{
        0%, 100% {{
            transform: rotate(0deg) scale(1);
        }}
        10%, 30% {{
            transform: rotate(-10deg) scale(1.1);
        }}
        20%, 40% {{
            transform: rotate(10deg) scale(1.1);
        }}
        50% {{
            transform: rotate(0deg) scale(1);
        }}
    }}
    
    .live-indicator {{
        display: inline-block;
        width: 12px;
        height: 12px;
        background-color: {ART_SUCCESS_GREEN};
        border-radius: 50%;
        margin-left: 0.5rem;
        animation: pulse 2s ease-in-out infinite;
        box-shadow: 0 0 0 0 rgba(0, 166, 81, 0.7);
    }}
    
    @keyframes pulse {{
        0% {{
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(0, 166, 81, 0.7);
        }}
        70% {{
            transform: scale(1);
            box-shadow: 0 0 0 10px rgba(0, 166, 81, 0);
        }}
        100% {{
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(0, 166, 81, 0);
        }}
    }}
    
    .live-subtitle {{
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.1rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.5rem;
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
    
    /* AI suggestion card */
    .suggestion-card {{
        background-color: {ART_WHITE};
        border: 1px solid {ART_BORDER};
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        line-height: 1.7;
        color: {ART_TEXT_DARK};
    }}
    
    /* Context Summary styling */
    .suggestion-card .context-summary {{
        font-size: 0.95rem;
        color: {ART_TEXT_DARK};
        margin-bottom: 1.25rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid {ART_BORDER};
    }}
    
    .suggestion-card .context-summary strong {{
        font-size: 0.9rem;
        font-weight: 600;
        color: {ART_PRIMARY_BLUE};
        display: block;
        margin-bottom: 0.5rem;
    }}
    
    /* Compliance Warning styling */
    .suggestion-card .compliance-warning {{
        background-color: #FFF3E0;
        border-left: 4px solid {ART_WARNING_ORANGE};
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-size: 0.9rem;
        line-height: 1.6;
    }}
    
    .suggestion-card .compliance-warning strong {{
        font-size: 0.95rem;
        font-weight: 600;
        color: {ART_WARNING_ORANGE};
        display: block;
        margin-bottom: 0.5rem;
    }}
    
    /* Immediate Action styling */
    .suggestion-card .immediate-action {{
        background-color: #FFEBEE;
        border-left: 4px solid {ART_ERROR_RED};
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-size: 0.9rem;
        line-height: 1.6;
    }}
    
    .suggestion-card .immediate-action strong {{
        font-size: 0.95rem;
        font-weight: 600;
        color: {ART_ERROR_RED};
        display: block;
        margin-bottom: 0.5rem;
    }}
    
    /* Response time styling */
    .suggestion-card .response-time {{
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 2px solid {ART_BORDER};
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: {ART_TEXT_GRAY};
        font-size: 0.9rem;
    }}
    
    .suggestion-card .response-time strong {{
        color: {ART_PRIMARY_BLUE};
        font-weight: 600;
    }}
    
    /* Action section styling */
    .suggestion-card .action-section {{
        background-color: {ART_LIGHT_BLUE};
        border-left: 4px solid {ART_PRIMARY_BLUE};
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-size: 0.9rem;
        line-height: 1.6;
    }}
    
    .suggestion-card .action-section strong {{
        font-size: 0.95rem;
        font-weight: 600;
        color: {ART_PRIMARY_BLUE};
        display: block;
        margin-bottom: 0.5rem;
    }}
    
    /* Suggested Response styling */
    .suggestion-card .suggested-response {{
        background-color: {ART_LIGHT_BLUE};
        border-left: 4px solid {ART_PRIMARY_BLUE};
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-size: 0.95rem;
        line-height: 1.7;
        font-style: italic;
    }}
    
    .suggestion-card .suggested-response strong {{
        font-size: 0.9rem;
        font-weight: 600;
        color: {ART_PRIMARY_BLUE};
        display: block;
        margin-bottom: 0.5rem;
        font-style: normal;
    }}
    
    /* Compliance Info styling (positive compliance status) */
    .suggestion-card .compliance-info {{
        margin: 1rem 0;
        padding: 1rem;
        background-color: #E8F5E9;
        border-left: 4px solid {ART_SUCCESS_GREEN};
        border-radius: 4px;
        font-size: 0.95rem;
        line-height: 1.6;
    }}
    
    .suggestion-card .compliance-info strong {{
        color: {ART_SUCCESS_GREEN};
        font-weight: 600;
        display: block;
        margin-bottom: 0.5rem;
    }}
    
    /* Remove markdown formatting from suggestion card */
    .suggestion-card h1,
    .suggestion-card h2,
    .suggestion-card h3 {{
        font-size: 1rem;
        font-weight: 600;
        margin: 1rem 0 0.5rem 0;
        color: {ART_PRIMARY_BLUE};
    }}
    
    .suggestion-card p {{
        margin: 0.5rem 0;
        font-size: 0.95rem;
    }}
    
    .suggestion-card ul,
    .suggestion-card ol {{
        margin: 0.5rem 0;
        padding-left: 1.5rem;
        font-size: 0.95rem;
    }}
    
    .suggestion-card li {{
        margin: 0.25rem 0;
    }}
    
    .suggestion-card code {{
        background-color: #F5F5F5;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-size: 0.85rem;
        font-family: 'Courier New', monospace;
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
    
    /* Column 1 (Human Call Center Agent) - near sidebar */
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
</style>
""", unsafe_allow_html=True)

def search_kb_vector_search(query: str, num_results: int = 5):
    """
    Search knowledge base using vector search (semantic similarity).
    Falls back to SQL function if vector search is not available.
    """
    try:
        # Try standard import first, then fallback to databricks-vectorsearch package
        try:
            from databricks.vector_search.client import VectorSearchClient
        except ImportError:
            from databricks_vectorsearch.client import VectorSearchClient
        
        # Initialize vector search client
        vsc = VectorSearchClient(disable_notice=True)
        
        # Get the vector search index
        try:
            index = vsc.get_index(
                endpoint_name=VECTOR_SEARCH_ENDPOINT,
                index_name=KB_INDEX_NAME
            )
        except Exception as e:
            # Index doesn't exist yet, fallback to SQL
            # Don't show warning in Streamlit (will show in logs)
            import logging
            logging.debug(f"Vector search index not found, using keyword search: {e}")
            return search_kb_sql_fallback(query)
        
        # Perform vector search
        results = index.similarity_search(
            query_text=query,
            columns=["article_id", "title", "content", "category"],
            num_results=num_results
        )
        
        # Convert results to list of dicts (matching SQL function format)
        articles = []
        if results and 'result' in results and 'data_array' in results['result']:
            for hit in results['result']['data_array']:
                # hit format: [article_id, title, content, category]
                articles.append({
                    'article_id': hit[0] if len(hit) > 0 else 'N/A',
                    'title': hit[1] if len(hit) > 1 else 'N/A',
                    'content': hit[2] if len(hit) > 2 else 'N/A',
                    'category': hit[3] if len(hit) > 3 else 'N/A'
                })
        
        return articles
        
    except Exception as e:
        # Fallback to SQL keyword search if vector search fails
        # Don't show warning in Streamlit (will show in logs)
        import logging
        logging.debug(f"Vector search failed, using keyword search: {e}")
        return search_kb_sql_fallback(query)

def search_kb_sql_fallback(query: str):
    """Fallback to SQL keyword search if vector search is not available"""
    try:
        query_sql = f"SELECT * FROM {FUNCTION_SEARCH_KB}('{query}')"
        articles_df = execute_sql(query_sql, return_dataframe=True)
        
        if not articles_df.empty:
            return articles_df.to_dict('records')
        else:
            return []
    except Exception as e:
        st.error(f"Error in SQL KB search: {e}")
        return []

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

@st.cache_data(ttl=5)  # Cache for 5 seconds - balance freshness vs performance
def get_live_transcript_cached(call_id):
    """Cached version of get_live_transcript"""
    return get_live_transcript(call_id)

@st.cache_data(ttl=10)  # Cache for 10 seconds
def get_compliance_alerts_cached(call_id):
    """Cached version of get_compliance_alerts"""
    return get_compliance_alerts(call_id)

@st.cache_data(ttl=10)  # Cache for 10 seconds
def get_call_context_cached(call_id):
    """Cached version of get_call_context"""
    query = f"SELECT * FROM {FUNCTION_GET_CALL_CONTEXT}('{call_id}')"
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

def get_heuristic_suggestion(call_id):
    """Get instant heuristic suggestion based on call context (no LLM call)"""
    try:
        transcript_df = get_live_transcript(call_id)
        if not transcript_df.empty and len(transcript_df) > 0:
            latest_intent = transcript_df['intent_category'].iloc[-1] if 'intent_category' in transcript_df.columns else None
            latest_sentiment = transcript_df['sentiment'].iloc[-1] if 'sentiment' in transcript_df.columns else None
            
            # Simple instant suggestions for common intents (no LLM call needed)
            if latest_intent == 'contribution_inquiry':
                return "Member asking about contributions. Suggested: 'The concessional cap is $30,000 for 2024-25. Would you like details on catch-up contributions?'"
            elif latest_intent == 'withdrawal_inquiry':
                return "Member asking about withdrawals. Suggested: 'I can help with withdrawal options. Are you looking for early access or regular withdrawal?'"
            elif latest_sentiment == 'negative':
                return "Member showing negative sentiment. Suggested: 'I understand your concern. Let me help resolve this for you. What specific issue can I address?'"
    except:
        pass
    return None

def get_ai_suggestion(call_id, use_heuristic=True):
    """Get AI suggestion for call - optimized for speed with caching and detailed timing"""
    import time as time_module
    start_time = time_module.time()
    timing_breakdown = {}
    
    # Check cache first (30 second cache)
    cache_key = f'ai_suggestion_{call_id}'
    cache_start = time_module.time()
    if cache_key in st.session_state:
        cached_result, cached_time = st.session_state[cache_key]
        if time_module.time() - cached_time < 30:
            elapsed = time_module.time() - start_time
            timing_breakdown['cache_lookup'] = time_module.time() - cache_start
            timing_breakdown['total'] = elapsed
            return cached_result, elapsed, timing_breakdown
    timing_breakdown['cache_lookup'] = time_module.time() - cache_start
    
    # Get heuristic suggestion first (instant)
    if use_heuristic:
        heuristic_start = time_module.time()
        heuristic = get_heuristic_suggestion(call_id)
        timing_breakdown['heuristic'] = time_module.time() - heuristic_start
        if heuristic:
            elapsed = time_module.time() - start_time
            timing_breakdown['total'] = elapsed
            st.session_state[cache_key] = (heuristic, time_module.time())
            return heuristic, elapsed, timing_breakdown
    
    # Fall through to LLM-based suggestion
    agent_start = time_module.time()
    agent = get_agent()
    timing_breakdown['agent_init'] = time_module.time() - agent_start
    if not agent:
        return "Agent not available. Please check configuration.", 0, timing_breakdown
    
    try:
        # Optimized prompt - supportive and helpful tone, very concise, directs agent to use minimum tools
        prompt = f"""Help me assist with call {call_id}. 

IMPORTANT: Call get_live_call_context FIRST - it has all the info you need (member info, transcript, sentiment, intent).
Only use other tools if absolutely necessary.

Provide:
- Brief context (1 sentence from get_live_call_context)
- Suggested response (1-2 sentences)
- Compliance warnings if any

Be helpful and supportive. Be FAST - use minimum tools."""
        
        # Measure LLM synthesis time separately
        llm_start = time_module.time()
        result = agent.invoke({
            'messages': [{
                'role': 'user',
                'content': prompt
            }]
        })
        timing_breakdown['llm_synthesis'] = time_module.time() - llm_start
        
        # Measure response extraction time
        extract_start = time_module.time()
        if isinstance(result, dict) and 'messages' in result:
            last_message = result['messages'][-1]
            response = last_message.content
        else:
            response = str(result)
        timing_breakdown['response_extraction'] = time_module.time() - extract_start
        
        elapsed_time = time_module.time() - start_time
        timing_breakdown['total'] = elapsed_time
        
        # Cache the result
        st.session_state[cache_key] = (response, time_module.time())
        return response, elapsed_time, timing_breakdown
    except Exception as e:
        elapsed_time = time_module.time() - start_time
        timing_breakdown['total'] = elapsed_time
        timing_breakdown['error'] = str(e)
        return f"Error getting suggestion: {e}", elapsed_time, timing_breakdown

def get_suggested_kb_questions(call_id):
    """Get suggested KB questions based on call context (scenario, intent)"""
    try:
        # Get call context to understand scenario and intent
        query = f"""
        SELECT DISTINCT 
            scenario,
            intent_category,
            COUNT(*) as count
        FROM {ENRICHED_TABLE}
        WHERE call_id = '{call_id}'
        GROUP BY scenario, intent_category
        ORDER BY count DESC
        LIMIT 5
        """
        results = execute_sql(query, return_dataframe=True)
        
        if results.empty:
            return []
        
        # Map scenarios/intents to KB questions
        suggestions = []
        
        for _, row in results.iterrows():
            scenario = str(row.get('scenario', '')).lower()
            intent = str(row.get('intent_category', '')).lower()
            
            # Scenario-based suggestions
            if 'withdrawal' in scenario or 'withdrawal' in intent:
                suggestions.extend([
                    "compassionate grounds withdrawal",
                    "financial hardship withdrawal",
                    "early access super"
                ])
            elif 'contribution' in scenario or 'contribution' in intent:
                suggestions.extend([
                    "contribution caps",
                    "employer contributions",
                    "non-concessional contributions"
                ])
            elif 'insurance' in scenario or 'insurance' in intent:
                suggestions.extend([
                    "insurance coverage",
                    "insurance claim",
                    "TPD insurance"
                ])
            elif 'investment' in scenario or 'investment' in intent:
                suggestions.extend([
                    "investment options",
                    "investment performance",
                    "switch investment"
                ])
            elif 'retirement' in scenario or 'retirement' in intent:
                suggestions.extend([
                    "retirement options",
                    "transition to retirement",
                    "preservation age"
                ])
            elif 'fee' in scenario or 'fee' in intent:
                suggestions.extend([
                    "fee structure",
                    "administration fees",
                    "investment fees"
                ])
            elif 'balance' in scenario or 'balance' in intent:
                suggestions.extend([
                    "account balance",
                    "check balance",
                    "balance enquiry"
                ])
            elif 'consolidat' in scenario or 'consolidat' in intent:
                suggestions.extend([
                    "consolidating super accounts",
                    "transfer super",
                    "combine accounts"
                ])
            elif 'tax' in scenario or 'tax' in intent:
                suggestions.extend([
                    "tax on contributions",
                    "tax on withdrawals",
                    "super tax"
                ])
            elif 'complaint' in scenario or 'complaint' in intent:
                suggestions.extend([
                    "complaint process",
                    "dispute resolution",
                    "AFCA"
                ])
        
        # Remove duplicates and return top 6
        unique_suggestions = list(dict.fromkeys(suggestions))[:6]
        
        # If no specific matches, add general suggestions
        if not unique_suggestions:
            unique_suggestions = [
                "contribution caps",
                "insurance coverage",
                "withdrawal options",
                "investment options",
                "fee structure",
                "account balance"
            ]
        
        return unique_suggestions
    except Exception as e:
        print(f"Error getting suggested questions: {e}")
        return [
            "contribution caps",
            "insurance coverage",
            "withdrawal options",
            "investment options",
            "fee structure",
            "account balance"
        ]

def format_suggestion_text(text):
    """Format AI suggestion text - clean HTML and add proper styling"""
    if not text:
        return text
    
    import html
    
    # First, decode any HTML entities
    text = html.unescape(text)
    
    # Check if text is already properly formatted HTML (idempotency check)
    # If it already has proper div wrappers and no raw markdown, skip markdown conversion
    # This prevents double-processing when switching tabs
    has_proper_html = (
        '<div class="context-summary">' in text or
        '<div class="suggested-response">' in text or
        '<div class="compliance-warning">' in text or
        '<div class="compliance-info">' in text or
        '<div class="immediate-action">' in text
    )
    has_raw_markdown = '**' in text
    
    # Check if text looks like it's already been processed (has HTML tags but no markdown)
    # Also check for malformed structures that indicate it was already processed incorrectly
    has_html_tags = '<div' in text or '<strong>' in text or '<br>' in text
    has_malformed_structure = (
        '<strong><div' in text or 
        '</div></strong>' in text or
        re.search(r'<div class="[^"]*">[^<]*<div', text) or  # Nested divs without closing
        re.search(r'</div>[^<]+<div class="(?!action-section|immediate-action|compliance)', text)  # Text between divs (leakage)
    )
    
    # If already properly formatted HTML and no markdown, skip markdown conversion
    # Just do minimal cleanup and return (idempotent operation)
    if (has_proper_html or (has_html_tags and not has_raw_markdown)) and not has_malformed_structure:
        # Only fix obvious malformations, don't reprocess
        # Fix: <strong><div...> -> <div...> (common malformation)
        text = re.sub(r'<strong>\s*<div', r'<div', text)
        # Fix: </div></strong> -> </div>
        text = re.sub(r'</div>\s*</strong>', r'</div>', text)
        # Fix nested strong tags
        text = re.sub(r'<strong>\s*<strong>(.+?)</strong>\s*</strong>', r'<strong>\1</strong>', text)
        # Fix: <div class="</div>..."> (broken attribute - restore it)
        text = re.sub(r'<div class="</div>([^"]+)">', r'<div class="\1">', text)
        return text
    
    # If we have malformed structure, it means it was already processed incorrectly
    # Fix the malformations first before processing
    if has_malformed_structure:
        # Fix: <strong><div...> -> <div...>
        text = re.sub(r'<strong>\s*<div', r'<div', text)
        # Fix: </div></strong> -> </div>
        text = re.sub(r'</div>\s*</strong>', r'</div>', text)
        # Fix: <div class="</div>..."> -> <div class="...">
        text = re.sub(r'<div class="</div>([^"]+)">', r'<div class="\1">', text)
    
    # Convert markdown to HTML FIRST (before processing HTML tags)
    # This handles cases where markdown and HTML are mixed
    # Strategy: Use a more careful approach to avoid breaking HTML structures
    
    # Step 1: Handle markdown wrapping partial HTML structures FIRST (most specific)
    # Pattern: **<div...><strong>...</strong> ** → <div...><strong>...</strong>
    # This handles cases where markdown wraps opening div + strong but not closing div
    # Must come FIRST to avoid being broken by more general patterns
    text = re.sub(r'\*\*<div([^>]*)><strong>([^<]*?)</strong>\s*\*\*', r'<div\1><strong>\2</strong>', text)
    
    # Step 2: Handle markdown wrapping complete HTML structures
    # Pattern: **<div...>...content...</div>** → <div...>...content...</div>
    # This handles cases like **<div class="..."><strong>Text</strong> **
    # Use non-greedy matching to avoid over-matching
    text = re.sub(r'\*\*<div([^>]*)>(.*?)</div>\s*\*\*', r'<div\1>\2</div>', text, flags=re.DOTALL)
    
    # Step 3: Handle markdown wrapping opening tags (but skip div, handled above)
    # Pattern: **<tag...> → <tag...> (for non-div tags only)
    # Process non-div tags first
    text = re.sub(r'\*\*<([a-zA-Z][a-zA-Z0-9]*)([^>]*)>', r'<\1\2>', text)
    # Then handle standalone div tags that weren't caught above
    text = re.sub(r'\*\*<div([^>]*)>', r'<div\1>', text)
    
    # Step 3: Remove markdown bold that wraps HTML closing tags
    # Pattern: </tag>** → </tag>
    text = re.sub(r'</([a-zA-Z][a-zA-Z0-9]*)>\s*\*\*', r'</\1>', text)
    
    # Step 4: Convert remaining markdown bold (**text**) to HTML <strong> tags
    # But skip if it contains HTML tags (already handled above)
    text = re.sub(r'\*\*([^*<]+)\*\*', r'<strong>\1</strong>', text)
    
    # Step 5: Remove any orphaned markdown markers (safety net)
    text = re.sub(r'\*\*', '', text)
    
    # Convert markdown line breaks to HTML
    text = text.replace('\n\n', '<br><br>').replace('\n', '<br>')
    
    # Fix malformed HTML structures more aggressively
    # Pattern 1: <strong><div...> -> <div...>
    text = re.sub(r'<strong>\s*<div', r'<div', text)
    # Pattern 2: </div></strong> -> </div> (fix closing tags)
    text = re.sub(r'</div>\s*</strong>', r'</div>', text)
    # Pattern 3: <strong></div> -> </div>
    text = re.sub(r'<strong>\s*</div>', r'</div>', text)
    # Pattern 4: </strong><div -> <div
    text = re.sub(r'</strong>\s*<div', r'<div', text)
    
    # Fix: <strong></div>Text -> </div><strong>Text
    text = re.sub(r'<strong>\s*</div>([^<]+)</strong>', r'</div><strong>\1</strong>', text)
    
    # Fix: </strong></div>Text -> </div>Text
    text = re.sub(r'</strong>\s*</div>([^<]+)', r'</div>\1', text)
    
    # Fix nested strong tags
    text = re.sub(r'<strong>\s*<strong>(.+?)</strong>\s*</strong>', r'<strong>\1</strong>', text)
    
    # Fix: <strong><div class="compliance-warning"> -> <div class="compliance-warning">
    # This handles cases where <strong> incorrectly wraps <div>
    text = re.sub(
        r'<strong>\s*<div class="compliance-warning">',
        r'<div class="compliance-warning">',
        text
    )
    
    # Fix: <strong><div class="context-summary"> -> <div class="context-summary">
    text = re.sub(
        r'<strong>\s*<div class="context-summary">',
        r'<div class="context-summary">',
        text
    )
    
    # Fix: <strong><div class="suggested-response"> -> <div class="suggested-response">
    text = re.sub(
        r'<strong>\s*<div class="suggested-response">',
        r'<div class="suggested-response">',
        text
    )
    
    # Fix: <strong><div class="immediate-action"> -> <div class="immediate-action">
    text = re.sub(
        r'<strong>\s*<div class="immediate-action">',
        r'<div class="immediate-action">',
        text
    )
    
    # Fix: Remove any </strong> that comes after </div> (closing tag mismatch)
    text = re.sub(r'</div>\s*</strong>', r'</div>', text)
    
    # Fix specific compliance warning malformation
    # <strong><div class="compliance-warning"><strong>[COMPLIANCE WARNING]</strong></strong>
    text = re.sub(
        r'<strong>\s*<div class="compliance-warning">\s*<strong>\[COMPLIANCE WARNING\]</strong>\s*</strong>',
        r'<div class="compliance-warning"><strong>[COMPLIANCE WARNING]</strong>',
        text
    )
    
    # Fix: <div class="compliance-warning">...content...</div></strong> -> </div>
    text = re.sub(r'<div class="compliance-warning">(.+?)</div>\s*</strong>', r'<div class="compliance-warning">\1</div>', text, flags=re.DOTALL)
    
    # Fix: <strong></div>Immediate Action: -> </div><strong>Immediate Action:
    text = re.sub(r'<strong>\s*</div>([A-Z][^<]*?):\s*</strong>', r'</div><strong>\1:</strong>', text)
    
    # Fix: </strong></div>Immediate Action: -> </div><strong>Immediate Action:
    text = re.sub(r'</strong>\s*</div>([A-Z][^<]*?):\s*', r'</div><strong>\1:</strong> ', text)
    
    # Fix: <strong></div>Text -> </div><strong>Text (more general pattern)
    text = re.sub(r'<strong>\s*</div>([A-Z][^<]+)</strong>', r'</div><strong>\1</strong>', text)
    
    # Additional cleanup for any remaining markdown artifacts
    # (most should be handled above, but this catches edge cases)
    
    # If text already contains HTML tags, clean them up
    if '<div' in text or '<strong>' in text or '<br>' in text:
        # Process HTML-wrapped sections
        # Ensure Action section is properly wrapped (different from Immediate Action)
        if 'Action:' in text and '<div class="action-section">' not in text and '<div class="immediate-action">' not in text:
            # Make sure it's not part of "Immediate Action:"
            action_pos = text.find('Action:')
            if action_pos >= 0 and 'Immediate Action:' not in text[max(0, action_pos-20):action_pos+20]:
                match = re.search(r'(?:<strong>\s*)?Action:\s*(.+?)(?=<strong>Compliance|<strong>Context|<strong>Suggested|⏱️|Response time|$)', text, re.DOTALL | re.IGNORECASE)
                if match:
                    action_content = match.group(1).strip()
                    # Remove HTML tags from content if present
                    action_content = re.sub(r'</?div[^>]*>', '', action_content)
                    action_content = re.sub(r'</?strong>', '', action_content)
                    action_content = re.sub(r'<br\s*/?>', ' ', action_content)
                    action_content = ' '.join(action_content.split())
                    # Remove any existing <strong> tags around Action
                    text = re.sub(r'<strong>\s*Action:\s*</strong>', '', text, flags=re.IGNORECASE)
                    text = re.sub(
                        r'(?:<strong>\s*)?Action:\s*.+?(?=<strong>Compliance|<strong>Context|<strong>Suggested|⏱️|Response time|$)',
                        f'<div class="action-section"><strong>Action:</strong> {action_content}</div>',
                        text,
                        flags=re.DOTALL | re.IGNORECASE,
                        count=1
                    )
        
        # Ensure immediate action sections are properly wrapped
        # Handle both "Immediate Action:" label and numbered lists that are actions
        if 'Immediate Action:' in text or 'Immediate Action Required:' in text:
            if '<div class="immediate-action">' not in text:
                # Match from "Immediate Action:" to end or next major section
                match = re.search(r'(?:<strong>\s*)?(?:Immediate Action|Immediate Action Required):\s*(.+?)(?=<strong>Compliance|<strong>Context|<strong>Suggested|Compliance Issues|Do NOT|$)', text, re.DOTALL | re.IGNORECASE)
                if match:
                    action_content = match.group(1).strip()
                    # Remove HTML tags from content if present (but keep <br> and <strong> for formatting)
                    action_content = re.sub(r'</?div[^>]*>', '', action_content)
                    # Remove any existing <strong> tags around Immediate Action
                    text = re.sub(r'<strong>\s*Immediate Action(?: Required)?:\s*</strong>', '', text, flags=re.IGNORECASE)
                    text = re.sub(
                        r'(?:<strong>\s*)?(?:Immediate Action|Immediate Action Required):\s*.+?(?=<strong>Compliance|<strong>Context|<strong>Suggested|Compliance Issues|Do NOT|$)',
                        f'<div class="immediate-action"><strong>Immediate Action:</strong> {action_content}</div>',
                        text,
                        flags=re.DOTALL | re.IGNORECASE,
                        count=1
                    )
        # Also handle numbered lists that are immediate actions (e.g., "1. Stop... 2. Transfer...")
        elif re.search(r'^\d+\.\s*(?:Stop|Transfer|Escalate|Do NOT)', text, re.MULTILINE | re.IGNORECASE):
            # Check if it's not already wrapped
            if '<div class="immediate-action">' not in text:
                # Match numbered list until "Compliance Issues" or "Do NOT" or end
                match = re.search(r'(\d+\.\s*.+?)(?=Compliance Issues|Do NOT|$)', text, re.DOTALL | re.IGNORECASE)
                if match:
                    action_content = match.group(1).strip()
                    # Wrap it
                    text = re.sub(
                        r'(\d+\.\s*.+?)(?=Compliance Issues|Do NOT|$)',
                        r'<div class="immediate-action"><strong>Immediate Action:</strong> \1</div>',
                        text,
                        flags=re.DOTALL | re.IGNORECASE,
                        count=1
                    )
        
        # Ensure "Compliance Issues Detected:" section is wrapped
        if 'Compliance Issues Detected:' in text or 'Compliance Issues:' in text:
            if '<div class="compliance-warning">' not in text.split('Compliance Issues')[1][:200]:
                # Match from "Compliance Issues" to "Do NOT" or end
                match = re.search(r'(?:<strong>\s*)?Compliance Issues(?: Detected)?:\s*(.+?)(?=Do NOT|$)', text, re.DOTALL | re.IGNORECASE)
                if match:
                    issues_content = match.group(1).strip()
                    # Clean up HTML tags
                    issues_content = re.sub(r'</?div[^>]*>', '', issues_content)
                    # Wrap it in compliance-warning div
                    text = re.sub(
                        r'(?:<strong>\s*)?Compliance Issues(?: Detected)?:\s*.+?(?=Do NOT|$)',
                        f'<div class="compliance-warning"><strong>Compliance Issues Detected:</strong> {issues_content}</div>',
                        text,
                        flags=re.DOTALL | re.IGNORECASE,
                        count=1
                    )
        
        # Ensure "Do NOT attempt" warnings are wrapped
        if 'Do NOT attempt' in text or 'Do NOT' in text:
            # Check if it's not already in a div
            if '<div class="immediate-action">' not in text.split('Do NOT')[0][-100:]:
                match = re.search(r'(Do NOT[^<]+?)(?=<div|$)', text, re.DOTALL | re.IGNORECASE)
                if match:
                    warning_text = match.group(1).strip()
                    # Wrap it
                    text = re.sub(
                        r'(Do NOT[^<]+?)(?=<div|$)',
                        r'<div class="immediate-action"><strong>\1</strong></div>',
                        text,
                        flags=re.DOTALL | re.IGNORECASE,
                        count=1
                    )
        
        # Ensure compliance warnings are properly wrapped
        if '[COMPLIANCE WARNING]' in text:
            # Check if it's already wrapped but malformed
            if '<div class="compliance-warning">' in text:
                # Fix malformed closing tags - ensure proper structure
                # Fix: <div class="compliance-warning">...content...</div></strong> -> </div>
                text = re.sub(r'<div class="compliance-warning">(.+?)</div>\s*</strong>', r'<div class="compliance-warning">\1</div>', text, flags=re.DOTALL)
                # Fix: <div class="compliance-warning"><strong>[COMPLIANCE WARNING]</strong></strong> -> </div>
                text = re.sub(r'<div class="compliance-warning"><strong>\[COMPLIANCE WARNING\]</strong>\s*</strong>', r'<div class="compliance-warning"><strong>[COMPLIANCE WARNING]</strong>', text)
                # Fix: <div class="compliance-warning"><strong>[COMPLIANCE WARNING]</div></strong> -> </div>
                text = re.sub(r'<div class="compliance-warning"><strong>\[COMPLIANCE WARNING\]</div>\s*</strong>', r'<div class="compliance-warning"><strong>[COMPLIANCE WARNING]</strong>', text)
            # Check if it's already wrapped properly
            if '<div class="compliance-warning">' not in text or '</div>' not in text.split('[COMPLIANCE WARNING]')[1].split('Suggested')[0].split('Immediate')[0]:
                # Extract compliance warning content
                match = re.search(r'\[COMPLIANCE WARNING\](.+?)(?=Suggested|Context|Immediate|$)', text, re.DOTALL | re.IGNORECASE)
                if match:
                    warning_content = match.group(1).strip()
                    # Clean up any HTML tags from content
                    warning_content = re.sub(r'</?div[^>]*>', '', warning_content)
                    warning_content = re.sub(r'</?strong>', '', warning_content)
                    warning_content = re.sub(r'\*\*', '', warning_content)  # Remove markdown bold
                    warning_content = ' '.join(warning_content.split())
                    # Replace with properly formatted version
                    text = re.sub(
                        r'\[COMPLIANCE WARNING\].+?(?=Suggested|Context|Immediate|$)',
                        f'<div class="compliance-warning"><strong>[COMPLIANCE WARNING]</strong> {warning_content}</div>',
                        text,
                        flags=re.DOTALL | re.IGNORECASE,
                        count=1
                    )
        
        # Ensure context summary is properly wrapped (check for both patterns)
        # Handle both plain text and HTML-wrapped versions
        if ('Context Summary:' in text or 'Context:' in text) and '<div class="context-summary">' not in text:
            # Try Context Summary: first (with or without HTML tags)
            # Stop at numbered lists, "Compliance Issues", "Do NOT", or other major sections
            match = re.search(r'(?:<strong>\s*)?Context Summary:\s*(.+?)(?=<strong>Suggested|<strong>Compliance|<strong>Immediate|Compliance Issues|Do NOT|\d+\.\s*Stop|\d+\.\s*Transfer|$)', text, re.DOTALL | re.IGNORECASE)
            if not match:
                # Try Context: as fallback
                match = re.search(r'(?:<strong>\s*)?Context:\s*(.+?)(?=<strong>Suggested|<strong>Compliance|<strong>Immediate|Compliance Issues|Do NOT|\d+\.\s*Stop|\d+\.\s*Transfer|$)', text, re.DOTALL | re.IGNORECASE)
            if match:
                context_content = match.group(1).strip()
                # Remove HTML tags from content if present
                context_content = re.sub(r'</?strong>', '', context_content)
                context_content = re.sub(r'<br\s*/?>', ' ', context_content)
                # Stop at numbered lists or other indicators
                context_content = re.sub(r'(\d+\.\s*.+?$|Compliance Issues.*?$|Do NOT.*?$)', '', context_content, flags=re.DOTALL | re.IGNORECASE).strip()
                context_content = ' '.join(context_content.split())
                # Remove any existing <strong> tags around Context Summary/Context
                text = re.sub(r'<strong>\s*Context (?:Summary:)?\s*</strong>', '', text, flags=re.IGNORECASE)
                text = re.sub(
                    r'(?:<strong>\s*)?(?:Context Summary|Context):\s*.+?(?=<strong>Suggested|<strong>Compliance|<strong>Immediate|Compliance Issues|Do NOT|\d+\.\s*Stop|\d+\.\s*Transfer|$)',
                    f'<div class="context-summary"><strong>Context Summary:</strong> {context_content}</div>',
                    text,
                    flags=re.DOTALL | re.IGNORECASE,
                    count=1
                )
        # Also handle plain text context (no label, just description)
        # This handles cases where text starts with plain description before any HTML divs
        elif not '<div class="context-summary">' in text and not 'Context Summary:' in text and not 'Context:' in text:
            # Look for pattern: "Name is asking about..." followed by <br> and then div or quoted text
            # Match text from start until we hit <br> followed by <div or "
            # Also handle case where text starts with plain text before any HTML tags
            match = re.search(r'^([A-Z][^<]+?)\s*<br>', text, re.DOTALL)
            if match:
                context_content = match.group(1).strip()
                # Clean up - remove any trailing <br> tags and extra whitespace
                context_content = re.sub(r'<br\s*/?>', ' ', context_content)
                context_content = re.sub(r'\s+', ' ', context_content).strip()
                # Stop at common endings like "no compliance issues" or "positive sentiment"
                context_content = re.sub(r'\s*(?:-|,)\s*(?:positive|negative|no compliance).*$', '', context_content, flags=re.IGNORECASE)
                context_content = context_content.strip()
                if context_content and len(context_content) > 10:  # Make sure we have meaningful content
                    # Replace the text before <br> with wrapped version
                    text = re.sub(
                        r'^([A-Z][^<]+?)\s*<br>',
                        r'<div class="context-summary"><strong>Context Summary:</strong> \1</div><br>',
                        text,
                        flags=re.DOTALL,
                        count=1
                    )
            # Also handle case where text starts directly with description (no <br> before div)
            elif re.search(r'^[A-Z][a-z]+ is asking', text, re.IGNORECASE):
                # Match from start until we hit <div or <br>
                match = re.search(r'^([A-Z][^<]+?)(?=<div|<br>|$)', text, re.DOTALL)
                if match:
                    context_content = match.group(1).strip()
                    # Clean up
                    context_content = re.sub(r'\s+', ' ', context_content).strip()
                    # Stop at common endings
                    context_content = re.sub(r'\s*(?:-|,)\s*(?:positive|negative|no compliance).*$', '', context_content, flags=re.IGNORECASE)
                    context_content = context_content.strip()
                    if context_content and len(context_content) > 10:
                        # Wrap it - insert div before the existing content
                        text = re.sub(
                            r'^([A-Z][^<]+?)(?=<div|<br>|$)',
                            r'<div class="context-summary"><strong>Context Summary:</strong> \1</div>',
                            text,
                            flags=re.DOTALL,
                            count=1
                        )
        
        # Ensure suggested response is properly wrapped
        # Check for quoted text that looks like a suggested response
        if ('Suggested Response:' in text or 'Suggested Agent Response:' in text) and '<div class="suggested-response">' not in text:
            # Extract suggested response content (handle HTML tags)
            match = re.search(r'(?:<strong>\s*)?(?:Suggested Response|Suggested Agent Response):\s*(.+?)(?=<strong>Compliance|<strong>Context|<strong>Immediate|<strong>Action:|$)', text, re.DOTALL | re.IGNORECASE)
            if match:
                response_content = match.group(1).strip()
                # Remove HTML tags from content if present (but keep <br> for line breaks)
                response_content = re.sub(r'</?strong>', '', response_content)
                # Remove any existing <strong> tags around Suggested Response
                text = re.sub(r'<strong>\s*Suggested (?:Agent )?Response:\s*</strong>', '', text, flags=re.IGNORECASE)
                # Replace with properly formatted version
                text = re.sub(
                    r'(?:<strong>\s*)?(?:Suggested Response|Suggested Agent Response):\s*.+?(?=<strong>Compliance|<strong>Context|<strong>Immediate|<strong>Action:|$)',
                    f'<div class="suggested-response"><strong>Suggested Response:</strong> {response_content}</div>',
                    text,
                    flags=re.DOTALL | re.IGNORECASE,
                    count=1
                )
        else:
            # Check for quoted text that might be a suggested response (without explicit label)
            # Pattern: text after context summary that's quoted or looks like a response
            if '<div class="context-summary">' in text and '<div class="suggested-response">' not in text:
                # Look for quoted text or text that appears after context summary
                # Pattern: </div> <br>"text" or </div> <br>text that looks like dialogue
                match = re.search(r'</div>\s*<br>\s*"([^"]+)"', text, re.DOTALL)
                if match:
                    response_content = match.group(1).strip()
                    # Wrap it in suggested-response div
                    text = re.sub(
                        r'</div>\s*<br>\s*"([^"]+)"',
                        f'</div><div class="suggested-response"><strong>Suggested Response:</strong> "\1"</div>',
                        text,
                        flags=re.DOTALL,
                        count=1
                    )
        
        # Also check for quoted text anywhere if no suggested-response div exists
        if '<div class="suggested-response">' not in text:
            # Look for quoted text that appears to be a response (after context or compliance)
            # Pattern: </div> <br>"long quoted text" or <br>"long quoted text" or just "long quoted text"
            # Also handle: context summary text <br>"quoted text"
            match = re.search(r'(?:</div>|<br>|^)\s*"([^"]{20,})"', text, re.DOTALL)
            if match:
                # Check if there's context summary or compliance warning before it
                quote_pos = match.start()
                text_before = text[:quote_pos]
                if ('context-summary' in text_before or 'compliance-warning' in text_before or 
                    'Context Summary' in text_before or 'Context:' in text_before or
                    re.search(r'[A-Z][a-z]+ is asking', text_before)):
                    quoted_text = match.group(0)  # Get the full match including quotes and preceding tags
                    response_content = match.group(1).strip()
                    # Replace the quoted text with wrapped version
                    text = text.replace(
                        quoted_text,
                        f'<div class="suggested-response"><strong>Suggested Response:</strong> "{response_content}"</div>',
                        1  # Only replace first occurrence
                    )
        
        # Ensure compliance section is properly wrapped (if not a warning)
        if 'Compliance:' in text and '<div class="compliance-warning">' not in text and '<div class="compliance-info">' not in text:
            match = re.search(r'(?:<strong>\s*)?Compliance:\s*(.+?)(?=<strong>Suggested|<strong>Context|$)', text, re.DOTALL | re.IGNORECASE)
            if match:
                compliance_content = match.group(1).strip()
                # Remove HTML tags from content if present
                compliance_content = re.sub(r'</?strong>', '', compliance_content)
                compliance_content = re.sub(r'<br\s*/?>', ' ', compliance_content)
                compliance_content = ' '.join(compliance_content.split())
                # Remove any existing <strong> tags around Compliance
                text = re.sub(r'<strong>\s*Compliance:\s*</strong>', '', text, flags=re.IGNORECASE)
                text = re.sub(
                    r'(?:<strong>\s*)?Compliance:\s*.+?(?=<strong>Suggested|<strong>Context|$)',
                    f'<div class="compliance-info"><strong>Compliance:</strong> {compliance_content}</div>',
                    text,
                    flags=re.DOTALL | re.IGNORECASE,
                    count=1
                )
        
    # Final pass: Fix any remaining <strong><div patterns (most aggressive)
    # This catches any cases that weren't caught by the specific patterns above
    text = re.sub(r'<strong>\s*<div', r'<div', text)
    text = re.sub(r'</div>\s*</strong>', r'</div>', text)
    
    # Fix: <strong><div class="action-section"> -> <div class="action-section">
    text = re.sub(
        r'<strong>\s*<div class="action-section">',
        r'<div class="action-section">',
        text
    )
    
    # Convert remaining markdown to HTML if needed (after all HTML fixes)
    # Remove any remaining markdown bold that wasn't converted
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    
    # Clean up any remaining markdown artifacts
    text = re.sub(r'\*\*', '', text)  # Remove any orphaned **
    
    # Convert line breaks
    text = text.replace('\n\n', '<br><br>').replace('\n', '<br>')
    
    # Clean up multiple <br> tags
    text = re.sub(r'(<br>\s*){3,}', '<br><br>', text)
    
    # Handle status messages like "✓ No issues detected" or "All clear ✓" - wrap in info div
    if '✓ No issues detected' in text or 'No issues detected' in text or 'All clear' in text:
        # Find and wrap status message - handle both patterns
        if 'All clear' in text:
            # Handle "All clear ✓" pattern
            match = re.search(r'All clear\s*✓', text, re.IGNORECASE)
            if match and '<div class="compliance-info">' not in text[max(0, match.start()-50):match.end()+50]:
                text = re.sub(
                    r'All clear\s*✓',
                    r'<div class="compliance-info" style="background-color: #E8F5E9; border-left: 4px solid #4CAF50; padding: 0.75rem 1rem; border-radius: 8px; margin-top: 1rem;"><strong>All clear ✓</strong></div>',
                    text,
                    flags=re.IGNORECASE,
                    count=1
                )
        else:
            # Handle "✓ No issues detected" pattern
            match = re.search(r'(✓\s*)?No issues detected', text, re.IGNORECASE)
            if match and '<div class="compliance-info">' not in text[max(0, match.start()-50):match.end()+50]:
                text = re.sub(
                    r'(✓\s*)?No issues detected',
                    r'<div class="compliance-info" style="background-color: #E8F5E9; border-left: 4px solid #4CAF50; padding: 0.75rem 1rem; border-radius: 8px; margin-top: 1rem;"><strong>✓ No issues detected</strong></div>',
                    text,
                    flags=re.IGNORECASE,
                    count=1
                )
    
    return text
    
    # Plain text processing - wrap sections in proper divs
    # Ensure context summary is properly wrapped
    if ('Context Summary:' in text or 'Context:' in text) and '<div class="context-summary">' not in text:
        match = re.search(r'(?:Context Summary|Context):\s*(.+?)(?=Suggested|Compliance|Immediate|$)', text, re.DOTALL | re.IGNORECASE)
        if match:
            context_content = match.group(1).strip()
            context_content = ' '.join(context_content.split())
            text = re.sub(
                r'(?:Context Summary|Context):\s*.+?(?=Suggested|Compliance|Immediate|$)',
                f'<div class="context-summary"><strong>Context Summary:</strong> {context_content}</div>',
                text,
                flags=re.DOTALL | re.IGNORECASE,
                count=1
            )
    
    # Ensure suggested response is properly wrapped
    if ('Suggested Response:' in text or 'Suggested Agent Response:' in text) and '<div class="suggested-response">' not in text:
        match = re.search(r'(?:Suggested Response|Suggested Agent Response):\s*(.+?)(?=Compliance|Context|Immediate|$)', text, re.DOTALL | re.IGNORECASE)
        if match:
            response_content = match.group(1).strip()
            response_content = ' '.join(response_content.split())
            text = re.sub(
                r'(?:Suggested Response|Suggested Agent Response):\s*.+?(?=Compliance|Context|Immediate|$)',
                f'<div class="suggested-response"><strong>Suggested Response:</strong> {response_content}</div>',
                text,
                flags=re.DOTALL | re.IGNORECASE,
                count=1
            )
    
    # Ensure compliance section is properly wrapped (if not a warning)
    if 'Compliance:' in text and '[COMPLIANCE WARNING]' not in text and '<div class="compliance-info">' not in text:
        match = re.search(r'Compliance:\s*(.+?)(?=Suggested|Context|Immediate|$)', text, re.DOTALL | re.IGNORECASE)
        if match:
            compliance_content = match.group(1).strip()
            compliance_content = ' '.join(compliance_content.split())
            text = re.sub(
                r'Compliance:\s*.+?(?=Suggested|Context|Immediate|$)',
                f'<div class="compliance-info"><strong>Compliance:</strong> {compliance_content}</div>',
                text,
                flags=re.DOTALL | re.IGNORECASE,
                count=1
            )
    
    # Convert line breaks to <br>
    text = text.replace('\n\n', '<br><br>').replace('\n', '<br>')
    
    # Clean up multiple <br> tags
    text = re.sub(r'(<br>\s*){3,}', '<br><br>', text)
    
    # Handle status messages like "✓ No issues detected" or "All clear ✓" - wrap in info div
    if '✓ No issues detected' in text or 'No issues detected' in text or 'All clear' in text:
        # Find and wrap status message - handle both patterns
        if 'All clear' in text:
            # Handle "All clear ✓" pattern
            match = re.search(r'All clear\s*✓', text, re.IGNORECASE)
            if match and '<div class="compliance-info">' not in text[max(0, match.start()-50):match.end()+50]:
                text = re.sub(
                    r'All clear\s*✓',
                    r'<div class="compliance-info" style="background-color: #E8F5E9; border-left: 4px solid #4CAF50; padding: 0.75rem 1rem; border-radius: 8px; margin-top: 1rem;"><strong>All clear ✓</strong></div>',
                    text,
                    flags=re.IGNORECASE,
                    count=1
                )
        else:
            # Handle "✓ No issues detected" pattern
            match = re.search(r'(✓\s*)?No issues detected', text, re.IGNORECASE)
            if match and '<div class="compliance-info">' not in text[max(0, match.start()-50):match.end()+50]:
                text = re.sub(
                    r'(✓\s*)?No issues detected',
                    r'<div class="compliance-info" style="background-color: #E8F5E9; border-left: 4px solid #4CAF50; padding: 0.75rem 1rem; border-radius: 8px; margin-top: 1rem;"><strong>✓ No issues detected</strong></div>',
                    text,
                    flags=re.IGNORECASE,
                    count=1
                )
    
    return text

def get_compliance_alerts(call_id):
    query = f"SELECT * FROM {FUNCTION_CHECK_COMPLIANCE}('{call_id}')"
    results = execute_sql(query, return_dataframe=False)
    return results

@st.cache_data(ttl=5)  # Cache for 5 seconds - balance freshness vs performance
def get_live_transcript_cached(call_id):
    """Cached version of get_live_transcript"""
    return get_live_transcript(call_id)

@st.cache_data(ttl=10)  # Cache for 10 seconds
def get_compliance_alerts_cached(call_id):
    """Cached version of get_compliance_alerts"""
    return get_compliance_alerts(call_id)

@st.cache_data(ttl=10)  # Cache for 10 seconds
def get_call_context_cached(call_id):
    """Cached version of get_call_context"""
    query = f"SELECT * FROM {FUNCTION_GET_CALL_CONTEXT}('{call_id}')"
    results = execute_sql(query, return_dataframe=False)
    return results

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

# Main dashboard - 2 column layout (cleaner, less cluttered)
if selected_call_id:
    # Track call_id changes - only refresh call card when call_id actually changes
    last_rendered_call_id = st.session_state.get('last_rendered_call_id')
    call_id_changed = (last_rendered_call_id != selected_call_id)
    
    # Track KB interactions - use cached data when KB is active
    kb_interaction = st.session_state.get('kb_interaction', False)
    
    # Update last rendered call_id
    if call_id_changed:
        st.session_state['last_rendered_call_id'] = selected_call_id
        st.session_state['kb_interaction'] = False  # Reset KB interaction flag
    
    col1, col2 = st.columns([3, 2.5])
    
    # COLUMN 1: Live Call Transcript (larger)
    # ALWAYS render - use cached data if KB interaction is active
    with col1:
        # Prominent Live Call Header with ringing phone and live indicator
        st.markdown("""
        <div class="live-call-header">
            <div style="flex: 1;">
                <div class="live-call-title">
                    <span>📞</span>
                    <span>Live Call</span>
                    <span class="live-indicator"></span>
                </div>
                <div class="live-subtitle">
                    👨‍💼 Human Agent Conversation • Active Now
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            # Use cached version if KB interaction is active (prevents unnecessary refreshes)
            # Otherwise fetch fresh data
            if kb_interaction and not call_id_changed:
                # Use cached transcript if available
                cache_key = f'transcript_cache_{selected_call_id}'
                if cache_key in st.session_state:
                    transcript_df = st.session_state[cache_key]
                else:
                    # Fallback to fetching if no cache
                    transcript_df = get_live_transcript_cached(selected_call_id)
                    st.session_state[cache_key] = transcript_df
            else:
                # Fetch fresh data and cache it
                transcript_df = get_live_transcript_cached(selected_call_id)
                cache_key = f'transcript_cache_{selected_call_id}'
                st.session_state[cache_key] = transcript_df
            
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
                    
                    # Transcript bubble (compliance warnings removed - shown in summary card instead)
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
            
            # Button to get suggestion - show heuristic immediately, then LLM async
            if st.button("🔄 Get AI Suggestion", key="get_suggestion", use_container_width=True):
                # Show heuristic suggestion immediately (no LLM call)
                heuristic_suggestion = get_heuristic_suggestion(selected_call_id)
                if heuristic_suggestion:
                    # Show heuristic immediately
                    formatted_heuristic = format_suggestion_text(heuristic_suggestion)
                    suggestion_placeholder.markdown(f"""
                    <div class="suggestion-card">
                        <div style="color: {ART_PRIMARY_BLUE}; font-weight: bold; margin-bottom: 0.5rem;">⚡ Instant Suggestion (Heuristic):</div>
                        {formatted_heuristic}
                        <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid rgba(0,0,0,0.1); font-size: 0.85em; color: {ART_TEXT_GRAY};">
                            🔄 Getting enhanced AI suggestion...
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.session_state['heuristic_shown'] = True
                    st.session_state['heuristic_suggestion'] = heuristic_suggestion
                
                # Set flag for async LLM processing
                st.session_state['suggestion_loading'] = True
                st.session_state['suggestion_error'] = None
                st.session_state['suggestion_call_id'] = selected_call_id
                st.session_state['suggestion_trigger'] = True
            
            # Show loading indicator if processing LLM (but heuristic already shown)
            if st.session_state.get('suggestion_loading') and st.session_state.get('suggestion_call_id') == selected_call_id:
                if not st.session_state.get('heuristic_shown'):
                    loading_placeholder.info("🔄 Analyzing call context...")
                else:
                    loading_placeholder.empty()  # Heuristic already shown, just wait for LLM
            else:
                loading_placeholder.empty()
            
            # Show error if any
            if st.session_state.get('suggestion_error'):
                error_placeholder.error(f"Error: {st.session_state['suggestion_error']}")
            else:
                error_placeholder.empty()
            
            # Show final LLM suggestion when ready (replaces heuristic if available)
            if not st.session_state.get('suggestion_loading') and 'last_suggestion' in st.session_state and st.session_state.get('last_call_id') == selected_call_id:
                response_time = st.session_state.get('suggestion_response_time', 0)
                timing_breakdown = st.session_state.get('suggestion_timing_breakdown', {})
                
                # Measure formatting time separately (should be fast)
                format_start = time_module.time()
                # Always format fresh from raw text - don't trust cached formatting
                # IMPORTANT: Store formatted version separately to prevent corruption from tab switches
                raw_suggestion = st.session_state['last_suggestion']
                
                # Check if we have a cached formatted version that's still valid
                cache_key = f'formatted_suggestion_{selected_call_id}'
                cached_formatted = None
                has_malformed = False
                
                # Only use cache if we're NOT in a KB interaction (prevents corruption)
                kb_interaction = st.session_state.get('kb_interaction', False)
                use_cache = not kb_interaction
                
                if use_cache and cache_key in st.session_state and st.session_state.get('last_call_id') == selected_call_id:
                    cached_formatted = st.session_state[cache_key]
                    # Validate cached version - check if it's malformed
                    # If it has malformed structures, reformat it
                    has_malformed = (
                        '<strong><div' in cached_formatted or 
                        '</div></strong>' in cached_formatted or
                        re.search(r'<div class="[^"]*">[^<]*<div', cached_formatted) or  # Nested divs without closing
                        re.search(r'</div>[^<]+<div class="(?!action-section|immediate-action|compliance)', cached_formatted)  # Text between divs
                    )
                    if has_malformed:
                        # Cached version is corrupted, reformat from raw
                        cached_formatted = None
                
                if cached_formatted and not has_malformed:
                    # Use cached formatted version if available and valid
                    formatted_suggestion = cached_formatted
                else:
                    # Format fresh and cache it
                    formatted_suggestion = format_suggestion_text(raw_suggestion)
                    st.session_state[cache_key] = formatted_suggestion
                
                format_time = time_module.time() - format_start
                timing_breakdown['formatting'] = format_time
                
                # Measure rendering time
                render_start = time_module.time()
                
                # Build detailed timing display
                timing_details = []
                if timing_breakdown:
                    if 'llm_synthesis' in timing_breakdown:
                        timing_details.append(f"LLM: {timing_breakdown['llm_synthesis']:.2f}s")
                    if 'formatting' in timing_breakdown:
                        timing_details.append(f"Format: {timing_breakdown['formatting']:.3f}s")
                    if 'response_extraction' in timing_breakdown:
                        timing_details.append(f"Extract: {timing_breakdown['response_extraction']:.3f}s")
                    if 'agent_init' in timing_breakdown:
                        timing_details.append(f"Init: {timing_breakdown['agent_init']:.3f}s")
                
                time_display = f"""
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 2px solid {ART_BORDER}; display: flex; flex-direction: column; gap: 0.25rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1rem;">⏱️</span>
                        <span style="color: {ART_TEXT_GRAY}; font-size: 0.9rem; font-weight: 500;">Total: <strong style="color: {ART_PRIMARY_BLUE};">{response_time:.2f}s</strong></span>
                    </div>
                    {f'<div style="font-size: 0.75rem; color: {ART_TEXT_GRAY}; margin-left: 1.5rem;">{" | ".join(timing_details)}</div>' if timing_details else ''}
                </div>
                """ if response_time > 0 else ""
                
                # Check if this is enhanced version of heuristic
                heuristic_shown = st.session_state.get('heuristic_shown', False)
                enhanced_label = "<div style='color: #28a745; font-weight: bold; margin-bottom: 0.5rem;'>✨ Enhanced AI Suggestion:</div>" if heuristic_shown else ""
                
                suggestion_placeholder.markdown(f"""
                <div class="suggestion-card">
                    {enhanced_label}
                    {formatted_suggestion}
                    {time_display}
                </div>
                """, unsafe_allow_html=True)
                
                render_time = time_module.time() - render_start
                timing_breakdown['rendering'] = render_time
                
                # Clear heuristic flag
                st.session_state['heuristic_shown'] = False
                
                # Clear KB interaction flag after rendering (allows cache use next time)
                if st.session_state.get('kb_interaction'):
                    st.session_state['kb_interaction'] = False
            elif st.session_state.get('heuristic_shown') and st.session_state.get('heuristic_suggestion'):
                # Show heuristic while waiting for LLM - always format fresh
                raw_heuristic = st.session_state['heuristic_suggestion']
                formatted_heuristic = format_suggestion_text(raw_heuristic)
                suggestion_placeholder.markdown(f"""
                <div class="suggestion-card">
                    <div style="color: {ART_PRIMARY_BLUE}; font-weight: bold; margin-bottom: 0.5rem;">⚡ Instant Suggestion (Heuristic):</div>
                    {formatted_heuristic}
                    <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid rgba(0,0,0,0.1); font-size: 0.85em; color: {ART_TEXT_GRAY};">
                        🔄 Getting enhanced AI suggestion...
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                suggestion_placeholder.empty()
        
        with tab2:
            st.subheader("Member 360 View")
            
            try:
                # Use cached version - only fetch if call_id changed
                results = get_call_context_cached(selected_call_id)
                
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
                    
                    st.markdown("---")
                    st.markdown("**Recent Transcript:**")
                    transcript_text = context[2] if len(context) > 2 else "N/A"
                    
                    # Display transcript text properly (not character by character)
                    if transcript_text and transcript_text != "N/A":
                        # Ensure it's a string and not being iterated
                        transcript_str = str(transcript_text)
                        # Truncate if too long
                        display_text = transcript_str[:500] + "..." if len(transcript_str) > 500 else transcript_str
                        # Use text area or markdown for proper display
                        st.markdown(f"""
                        <div style="background-color: {ART_LIGHT_BLUE}; padding: 1rem; border-radius: 8px; border-left: 3px solid {ART_PRIMARY_BLUE}; font-size: 0.9rem; line-height: 1.6;">
                            {display_text.replace(chr(10), '<br>').replace(chr(13), '')}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("No transcript available")
                    
                    st.markdown("---")
                    st.markdown(f"**Sentiment:** {context[3] if len(context) > 3 else 'N/A'}")
                    st.markdown(f"**Intents:** {context[4] if len(context) > 4 else 'N/A'}")
                    st.markdown(f"**Compliance Issues:** {context[5] if len(context) > 5 else 'None'}")
                else:
                    st.info("No member context available")
            except Exception as e:
                st.error(f"Error loading member info: {e}")
        
        with tab3:
            st.subheader("Knowledge Base")
            
            # Initialize KB session state
            if 'kb_search_query' not in st.session_state:
                st.session_state['kb_search_query'] = ''
            if 'kb_results' not in st.session_state:
                st.session_state['kb_results'] = []
            if 'kb_query' not in st.session_state:
                st.session_state['kb_query'] = ''
            if 'kb_selected_question' not in st.session_state:
                st.session_state['kb_selected_question'] = None
            if 'kb_last_known_query' not in st.session_state:
                st.session_state['kb_last_known_query'] = ''
            
            # Show suggested questions as radio buttons (less rerun triggers than buttons)
            if selected_call_id:
                suggested_questions = get_suggested_kb_questions(selected_call_id)
                
                if suggested_questions:
                    st.markdown("**💡 Suggested Questions:**")
                    # Use radio buttons - only triggers rerun on selection change
                    # Get current selection index
                    current_selection = st.session_state.get('kb_selected_question')
                    current_index = None
                    if current_selection and current_selection in suggested_questions:
                        current_index = suggested_questions.index(current_selection)
                    
                    selected_question = st.radio(
                        "Select a question to search:",
                        options=suggested_questions,
                        key="kb_question_radio",
                        label_visibility="collapsed",
                        index=current_index
                    )
                    
                    # Only search if selection changed
                    if selected_question and selected_question != st.session_state.get('kb_selected_question'):
                        st.session_state['kb_selected_question'] = selected_question
                        st.session_state['kb_search_query'] = selected_question
                        st.session_state['kb_interaction'] = True  # Mark KB interaction
                        
                        # Execute search
                        try:
                            articles = search_kb_vector_search(selected_question, num_results=5)
                            if articles:
                                st.session_state['kb_results'] = articles
                                st.session_state['kb_query'] = selected_question
                            else:
                                st.session_state['kb_results'] = []
                                st.session_state['kb_query'] = selected_question
                        except Exception as e:
                            st.session_state['kb_results'] = []
                            st.session_state['kb_query'] = selected_question
                            st.session_state['kb_error'] = str(e)
                else:
                    st.caption("No suggestions available")
                
                st.markdown("---")
            
            # Simple text search (optional - less used, no form to reduce reruns)
            # Use on_change to prevent reruns while typing
            def on_search_change():
                # This callback only runs when user presses Enter or loses focus
                pass
            
            search_query = st.text_input(
                "Or search manually:",
                value=st.session_state.get('kb_search_query', ''),
                key="kb_manual_search",
                placeholder="Type your question here...",
                on_change=on_search_change
            )
            
            # Only search when user presses Enter (not on every keystroke)
            # Check if search_query changed from last known value
            last_known_query = st.session_state.get('kb_last_known_query', '')
            if search_query != last_known_query and search_query:
                st.session_state['kb_last_known_query'] = search_query
                # Only search if query changed and not from radio selection
                if search_query != st.session_state.get('kb_query') and search_query != st.session_state.get('kb_selected_question'):
                    st.session_state['kb_search_query'] = search_query
                    st.session_state['kb_selected_question'] = None  # Clear radio selection
                    st.session_state['kb_interaction'] = True
                    try:
                        articles = search_kb_vector_search(search_query, num_results=5)
                        if articles:
                            st.session_state['kb_results'] = articles
                            st.session_state['kb_query'] = search_query
                        else:
                            st.session_state['kb_results'] = []
                            st.session_state['kb_query'] = search_query
                    except Exception as e:
                        st.session_state['kb_results'] = []
                        st.session_state['kb_query'] = search_query
                        st.session_state['kb_error'] = str(e)
            
            # Display KB results using empty container (prevents rerenders)
            kb_results_placeholder = st.empty()
            with kb_results_placeholder.container():
                if st.session_state.get('kb_error'):
                    st.error(f"Error: {st.session_state['kb_error']}")
                    st.session_state['kb_error'] = None  # Clear after showing
                
                if st.session_state.get('kb_results') and st.session_state.get('kb_query'):
                    st.markdown(f"**📚 Results for: '{st.session_state.get('kb_query', '')}'**")
                    for idx, article in enumerate(st.session_state['kb_results']):
                        article_id = article.get('article_id', 'N/A')
                        title = article.get('title', 'N/A')
                        content = article.get('content', 'N/A')
                        category = article.get('category', 'N/A')
                        
                        # Truncate content for display
                        content_display = content[:500] + "..." if len(str(content)) > 500 else content
                        
                        st.markdown(f"""
                        <div class="suggestion-card" style="margin-bottom: 1rem;">
                            <strong>[{article_id}] {title}</strong><br>
                            <small style="color: {ART_TEXT_GRAY};">Category: {category}</small><br>
                            <div style="margin-top: 0.5rem; font-size: 0.9rem; line-height: 1.5;">
                                {content_display}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                elif not st.session_state.get('kb_search_query') and not st.session_state.get('kb_selected_question'):
                    st.info("👆 Select a suggested question above or enter a search term")
        
        # Compliance Summary Card (clean, single card instead of multiple alerts)
        st.markdown("---")
        st.markdown("### ⚖️ Compliance Status")
        
        try:
            # Use cached version - only fetch if call_id changed
            alerts = get_compliance_alerts_cached(selected_call_id)
            
            if alerts and len(alerts) > 0:
                # Count severity levels
                critical_count = sum(1 for alert in alerts if (isinstance(alert, (list, tuple)) and len(alert) > 1 and str(alert[1]).upper() == 'CRITICAL') or (isinstance(alert, str) and 'CRITICAL' in str(alert).upper()))
                high_count = sum(1 for alert in alerts if (isinstance(alert, (list, tuple)) and len(alert) > 1 and str(alert[1]).upper() == 'HIGH') or (isinstance(alert, str) and 'HIGH' in str(alert).upper() and 'CRITICAL' not in str(alert).upper()))
                total_count = len(alerts)
                
                # Get unique violation types
                violation_types = set()
                for alert in alerts:
                    if isinstance(alert, (list, tuple)) and len(alert) > 0:
                        violation_type = str(alert[0])
                        # Format violation type: replace underscores with spaces and title case
                        violation_type = violation_type.replace('_', ' ').title()
                        violation_types.add(violation_type)
                    elif isinstance(alert, str):
                        violation_type = alert.split('|')[0] if '|' in alert else alert
                        violation_type = violation_type.replace('_', ' ').title()
                        violation_types.add(violation_type)
                
                # Determine overall status
                if critical_count > 0:
                    status_color = ART_ERROR_RED
                    status_icon = "🔴"
                    status_text = "Critical Issues Detected"
                elif high_count > 0:
                    status_color = "#FF9800"
                    status_icon = "🟠"
                    status_text = "High Priority Issues"
                else:
                    status_color = ART_SUCCESS_GREEN
                    status_icon = "✅"
                    status_text = "All Clear"
                
                # Build violation types string safely
                violation_types_list = list(violation_types)[:4]
                violation_types_str = ', '.join(violation_types_list) if violation_types_list else 'None'
                if len(violation_types) > 4:
                    violation_types_str += '...'
                
                st.markdown(f"""
                <div class="suggestion-card" style="border-left: 4px solid {status_color}; padding: 0.75rem 1rem;">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.2rem; margin-right: 0.5rem;">{status_icon}</span>
                        <strong style="color: {status_color}; font-size: 0.95rem;">{status_text}</strong>
                    </div>
                    <div style="font-size: 0.85rem; margin-bottom: 0.4rem;">
                        <div style="display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center; padding: 0.75rem; background-color: rgba(255, 107, 53, 0.08); border-radius: 8px;">
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <strong style="color: {ART_TEXT_DARK}; font-weight: 600;">Total:</strong>
                                <span style="background-color: {ART_WARNING_ORANGE}; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-weight: 600; font-size: 0.85rem;">{total_count}</span>
                            </div>
                            {f'<div style="display: flex; align-items: center; gap: 0.5rem;"><strong style="color: {ART_TEXT_DARK}; font-weight: 600;">Critical:</strong><span style="background-color: {ART_ERROR_RED}; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-weight: 600; font-size: 0.85rem;">{critical_count}</span></div>' if critical_count > 0 else ''}
                            {f'<div style="display: flex; align-items: center; gap: 0.5rem;"><strong style="color: {ART_TEXT_DARK}; font-weight: 600;">High:</strong><span style="background-color: {ART_ERROR_RED}; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-weight: 600; font-size: 0.85rem;">{high_count}</span></div>' if high_count > 0 else ''}
                        </div>
                    </div>
                    <div style="margin-top: 0.75rem; padding: 0.75rem; background-color: {ART_LIGHT_BLUE}; border-radius: 8px; border-left: 3px solid {ART_PRIMARY_BLUE};">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <strong style="color: {ART_PRIMARY_BLUE}; font-size: 0.9rem; font-weight: 600;">Violation Types:</strong>
                        </div>
                        <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                            {''.join([f'<span style="background-color: {ART_WHITE}; color: {ART_TEXT_DARK}; padding: 0.35rem 0.75rem; border-radius: 6px; border: 1px solid {ART_BORDER}; font-size: 0.85rem; font-weight: 500;">{vt}</span>' for vt in violation_types_list])}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="suggestion-card" style="border-left: 4px solid {ART_SUCCESS_GREEN}; padding: 0.75rem 1rem;">
                    <div style="display: flex; align-items: center;">
                        <span style="font-size: 1.2rem; margin-right: 0.5rem;">✅</span>
                        <strong style="color: {ART_SUCCESS_GREEN}; font-size: 0.95rem;">No Compliance Issues</strong>
                    </div>
                    <div style="margin-top: 0.4rem; color: {ART_TEXT_GRAY}; font-size: 0.8rem;">
                        All interactions compliant.
                    </div>
                </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error loading compliance status: {e}")
    
    # COLUMN 3 removed - cleaner layout with compliance summary in column 2

else:
    st.info("👈 Select an active call from the sidebar to begin")

# Process AI suggestion AFTER all UI is rendered (prevents tab freezing)
# This runs at the end, so tabs render first, then processing happens
if st.session_state.get('suggestion_trigger') and st.session_state.get('suggestion_call_id'):
    try:
        # Process LLM suggestion (heuristic already shown)
        suggestion, elapsed_time, timing_breakdown = get_ai_suggestion(st.session_state['suggestion_call_id'], use_heuristic=False)
        # Store raw suggestion text (not formatted) - formatting happens on display
        st.session_state['last_suggestion'] = suggestion
        st.session_state['last_call_id'] = st.session_state['suggestion_call_id']
        st.session_state['suggestion_response_time'] = elapsed_time
        st.session_state['suggestion_timing_breakdown'] = timing_breakdown
        # Clear cached formatted version when new suggestion arrives
        cache_key = f'formatted_suggestion_{st.session_state["suggestion_call_id"]}'
        if cache_key in st.session_state:
            del st.session_state[cache_key]
        st.session_state['suggestion_loading'] = False
        st.session_state['suggestion_error'] = None
        st.session_state['suggestion_trigger'] = False
        # Use rerun to update UI with LLM result (but heuristic already shown)
        st.rerun()
    except Exception as e:
        st.session_state['suggestion_error'] = str(e)
        st.session_state['suggestion_loading'] = False
        st.session_state['suggestion_trigger'] = False
        st.session_state['suggestion_response_time'] = None
        st.session_state['suggestion_timing_breakdown'] = {}
        st.rerun()

# Auto-refresh disabled - was causing new tabs to open
# Users can manually refresh the page if needed
# Future: Implement proper Streamlit rerun mechanism if auto-refresh is needed

