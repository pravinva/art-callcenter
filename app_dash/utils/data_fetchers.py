"""
Data Fetching Utilities for Dash App
Wraps SQL queries with caching
"""
from functools import lru_cache
from datetime import datetime, timedelta
import pandas as pd
import time
from typing import List, Dict, Any, Optional

from app_dash.utils.databricks_client import execute_sql
from config.config import (
    ENRICHED_TABLE, SQL_WAREHOUSE_ID,
    FUNCTION_GET_CALL_CONTEXT,
    FUNCTION_CHECK_COMPLIANCE,
    FUNCTION_GET_MEMBER_HISTORY
)

# Cache with TTL simulation (using timestamp)
_cache_timestamps = {}
_cache_data = {}

def _is_cache_valid(cache_key: str, ttl_seconds: int) -> bool:
    """Check if cache entry is still valid"""
    if cache_key not in _cache_timestamps:
        return False
    elapsed = time.time() - _cache_timestamps[cache_key]
    return elapsed < ttl_seconds

def get_active_calls() -> List[tuple]:
    """Get active calls from last 30 minutes (increased from 10)"""
    cache_key = "active_calls"
    ttl = 10  # 10 seconds
    
    if _is_cache_valid(cache_key, ttl):
        return _cache_data[cache_key]
    
    query = f"""
    SELECT DISTINCT
        call_id,
        member_name,
        member_id,
        scenario,
        MIN(timestamp) as call_start,
        COUNT(*) as utterances
    FROM {ENRICHED_TABLE}
    WHERE timestamp > CURRENT_TIMESTAMP() - INTERVAL 30 MINUTE
    GROUP BY call_id, member_name, member_id, scenario
    ORDER BY call_start DESC
    LIMIT 50
    """
    
    results = execute_sql(query, SQL_WAREHOUSE_ID, return_dataframe=False)
    
    _cache_data[cache_key] = results
    _cache_timestamps[cache_key] = time.time()
    
    return results

def get_live_transcript(call_id: str) -> pd.DataFrame:
    """Get live transcript for a call"""
    cache_key = f"transcript_{call_id}"
    ttl = 5  # 5 seconds
    
    if _is_cache_valid(cache_key, ttl):
        return _cache_data[cache_key]
    
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
    
    df = execute_sql(query, SQL_WAREHOUSE_ID, return_dataframe=True)
    
    _cache_data[cache_key] = df
    _cache_timestamps[cache_key] = time.time()
    
    return df

def get_call_context(call_id: str) -> Optional[List]:
    """Get call context (member info)"""
    cache_key = f"context_{call_id}"
    ttl = 10  # 10 seconds
    
    if _is_cache_valid(cache_key, ttl):
        return _cache_data[cache_key]
    
    query = f"SELECT * FROM {FUNCTION_GET_CALL_CONTEXT}('{call_id}')"
    results = execute_sql(query, SQL_WAREHOUSE_ID, return_dataframe=False)
    
    context = results[0] if results and len(results) > 0 else None
    
    _cache_data[cache_key] = context
    _cache_timestamps[cache_key] = time.time()
    
    return context

def get_compliance_alerts(call_id: str) -> List:
    """Get compliance alerts for a call"""
    cache_key = f"compliance_{call_id}"
    ttl = 10  # 10 seconds
    
    if _is_cache_valid(cache_key, ttl):
        return _cache_data[cache_key]
    
    query = f"SELECT * FROM {FUNCTION_CHECK_COMPLIANCE}('{call_id}')"
    results = execute_sql(query, SQL_WAREHOUSE_ID, return_dataframe=False)
    
    _cache_data[cache_key] = results
    _cache_timestamps[cache_key] = time.time()
    
    return results

def get_member_history(member_id: str) -> List:
    """Get member interaction history"""
    cache_key = f"history_{member_id}"
    ttl = 30  # 30 seconds
    
    if _is_cache_valid(cache_key, ttl):
        return _cache_data[cache_key]
    
    query = f"SELECT * FROM {FUNCTION_GET_MEMBER_HISTORY}('{member_id}')"
    results = execute_sql(query, SQL_WAREHOUSE_ID, return_dataframe=False)
    
    _cache_data[cache_key] = results
    _cache_timestamps[cache_key] = time.time()
    
    return results

