"""
Configuration settings for ART Call Center project.
Uses Databricks CLI credentials from ~/.databrickscfg
"""
import os
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config

def get_workspace_client():
    """Initialize WorkspaceClient using Databricks CLI config"""
    return WorkspaceClient()

def get_workspace_url():
    """Get workspace URL from config"""
    config = Config()
    return config.host

def get_zerobus_endpoint():
    """Get Zerobus endpoint URL"""
    workspace_url = get_workspace_url()
    # Remove trailing slash if present
    workspace_url = workspace_url.rstrip('/')
    return f"{workspace_url}/api/2.0/zerobus/streams"

# ============================================================================
# Databricks Configuration
# ============================================================================
WORKSPACE_URL = get_workspace_url()
ZEROBUS_ENDPOINT = get_zerobus_endpoint()

# ============================================================================
# Catalog and Schema Configuration
# ============================================================================
CATALOG_NAME = "member_analytics"
SCHEMA_NAME = "call_center"
TABLE_NAME = "zerobus_transcripts"

# ============================================================================
# Secrets Configuration
# ============================================================================
SECRETS_SCOPE = "art-zerobus"
CLIENT_ID_SECRET = "service-principal-id"
CLIENT_SECRET_KEY = "service-principal-secret"
ZEROBUS_CLIENT_ID_ENV = "ZEROBUS_CLIENT_ID"
ZEROBUS_CLIENT_SECRET_ENV = "ZEROBUS_CLIENT_SECRET"

# ============================================================================
# LLM Configuration
# ============================================================================
# Databricks Claude Sonnet 4-5 endpoint
LLM_ENDPOINT_NAME = "databricks-claude-sonnet-4-5"
LLM_MODEL_NAME = "databricks-claude-sonnet-4-5"

# ============================================================================
# Agent Configuration
# ============================================================================
AGENT_MODEL_NAME = "member_analytics.call_center.live_agent_assist"
AGENT_ENDPOINT_NAME = "live-agent-assist"

# ============================================================================
# Table Names
# ============================================================================
ZEROBUS_TABLE = f"{CATALOG_NAME}.{SCHEMA_NAME}.{TABLE_NAME}"
ENRICHED_TABLE = f"{CATALOG_NAME}.{SCHEMA_NAME}.enriched_transcripts"
ONLINE_TABLE = f"{CATALOG_NAME}.{SCHEMA_NAME}.live_transcripts_online"

# Gold Layer Tables (created by Gold Layer DLT pipeline)
CALL_SUMMARIES_TABLE = f"{CATALOG_NAME}.{SCHEMA_NAME}.call_summaries"
AGENT_PERFORMANCE_TABLE = f"{CATALOG_NAME}.{SCHEMA_NAME}.agent_performance"
MEMBER_HISTORY_TABLE = f"{CATALOG_NAME}.{SCHEMA_NAME}.member_interaction_history"
DAILY_STATS_TABLE = f"{CATALOG_NAME}.{SCHEMA_NAME}.daily_call_statistics"

# ============================================================================
# UC Function Names
# ============================================================================
FUNCTION_GET_CALL_CONTEXT = f"{CATALOG_NAME}.{SCHEMA_NAME}.get_live_call_context"
FUNCTION_SEARCH_KB = f"{CATALOG_NAME}.{SCHEMA_NAME}.search_knowledge_base"
FUNCTION_CHECK_COMPLIANCE = f"{CATALOG_NAME}.{SCHEMA_NAME}.check_compliance_realtime"
FUNCTION_GET_MEMBER_HISTORY = f"{CATALOG_NAME}.{SCHEMA_NAME}.get_member_history"
FUNCTION_DETECT_SENTIMENT = f"{CATALOG_NAME}.{SCHEMA_NAME}.detect_sentiment"
FUNCTION_EXTRACT_INTENT = f"{CATALOG_NAME}.{SCHEMA_NAME}.extract_member_intent"
FUNCTION_IDENTIFY_ESCALATION = f"{CATALOG_NAME}.{SCHEMA_NAME}.identify_escalation_triggers"

# ============================================================================
# SQL Warehouse Configuration
# ============================================================================
SQL_WAREHOUSE_ID = "4b9b953939869799"

def get_zerobus_credentials():
    """Get Zerobus credentials from environment or secrets"""
    import os
    client_id = os.getenv(ZEROBUS_CLIENT_ID_ENV)
    client_secret = os.getenv(ZEROBUS_CLIENT_SECRET_ENV)
    return client_id, client_secret

