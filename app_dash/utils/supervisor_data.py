"""
Supervisor Dashboard Utilities
Data fetching functions for supervisor dashboard
"""
from typing import List, Dict, Optional
import pandas as pd
from app_dash.utils.databricks_client import execute_sql
from config.config import SQL_WAREHOUSE_ID, ENRICHED_TABLE

def get_all_active_calls() -> pd.DataFrame:
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
    df = execute_sql(query, SQL_WAREHOUSE_ID, return_dataframe=True)
    
    if df is None or df.empty:
        return pd.DataFrame()
    
    # Convert numeric columns
    if 'utterance_count' in df.columns:
        df['utterance_count'] = pd.to_numeric(df['utterance_count'], errors='coerce')
    
    return df

def get_escalation_data(call_id: str) -> Optional[Dict]:
    """Get escalation triggers for a call"""
    query = f"""
    SELECT * FROM {ENRICHED_TABLE}
    WHERE call_id = '{call_id}'
    ORDER BY timestamp DESC
    LIMIT 1
    """
    results = execute_sql(query, SQL_WAREHOUSE_ID, return_dataframe=False)
    
    if results and len(results) > 0:
        return results[0]
    return None

def get_calls_with_escalations_batch(call_ids: List[str]) -> Dict[str, Dict]:
    """Get escalation data for multiple calls efficiently"""
    if not call_ids:
        return {}
    
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
        SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) as negative_sentiment_count,
        SUM(CASE WHEN compliance_flag != 'ok' THEN 1 ELSE 0 END) as compliance_violations_count,
        SUM(CASE WHEN intent_category = 'complaint' THEN 1 ELSE 0 END) as complaint_intent_count
    FROM {ENRICHED_TABLE}
    WHERE call_id IN ('{call_ids_str}')
    GROUP BY call_id
    """
    
    results = execute_sql(query, SQL_WAREHOUSE_ID, return_dataframe=True)
    
    escalation_dict = {}
    if results is not None and not results.empty:
        for _, row in results.iterrows():
            call_id = row.get('call_id')
            if call_id:
                escalation_dict[call_id] = {
                    'escalation_recommended': bool(row.get('escalation_recommended', False)),
                    'risk_score': int(row.get('risk_score', 0) or 0),
                    'negative_sentiment_count': int(row.get('negative_sentiment_count', 0) or 0),
                    'compliance_violations_count': int(row.get('compliance_violations_count', 0) or 0),
                    'complaint_intent_count': int(row.get('complaint_intent_count', 0) or 0)
                }
    
    return escalation_dict

def get_escalation_summary() -> Dict:
    """Get overall escalation summary"""
    query = f"""
    SELECT 
        COUNT(DISTINCT call_id) as total_active_calls,
        SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) as total_negative_sentiments,
        SUM(CASE WHEN compliance_flag != 'ok' THEN 1 ELSE 0 END) as total_compliance_issues,
        SUM(CASE WHEN intent_category = 'complaint' THEN 1 ELSE 0 END) as total_complaints
    FROM {ENRICHED_TABLE}
    WHERE timestamp >= current_timestamp() - INTERVAL 10 MINUTES
    """
    results = execute_sql(query, SQL_WAREHOUSE_ID, return_dataframe=True)
    
    if results is None or results.empty:
        return {
            'total_active_calls': 0,
            'total_negative_sentiments': 0,
            'total_compliance_issues': 0,
            'total_complaints': 0
        }
    
    row = results.iloc[0]
    return {
        'total_active_calls': int(row.get('total_active_calls', 0) or 0),
        'total_negative_sentiments': int(row.get('total_negative_sentiments', 0) or 0),
        'total_compliance_issues': int(row.get('total_compliance_issues', 0) or 0),
        'total_complaints': int(row.get('total_complaints', 0) or 0)
    }

