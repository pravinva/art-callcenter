"""
Databricks Client Utilities for Dash App
Wraps Databricks SDK with caching and error handling
"""
from functools import lru_cache
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
import time
from typing import Optional, List, Dict, Any

# Cache WorkspaceClient (singleton pattern)
@lru_cache(maxsize=1)
def get_workspace_client() -> WorkspaceClient:
    """Get cached WorkspaceClient instance"""
    return WorkspaceClient()

def execute_sql(
    query: str,
    warehouse_id: str,
    return_dataframe: bool = False,
    timeout: int = 10
) -> Optional[Any]:
    """
    Execute SQL query using Databricks SDK
    
    Args:
        query: SQL query string
        warehouse_id: SQL warehouse ID
        return_dataframe: If True, return pandas DataFrame
        timeout: Timeout in seconds
        
    Returns:
        Query results (list of tuples or DataFrame)
    """
    w = get_workspace_client()
    
    try:
        # Execute SQL statement
        response = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=query,
            wait_timeout=f"{timeout}s"
        )
        
        # Wait for completion
        statement_id = response.statement_id
        max_wait = timeout
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
            
            time.sleep(0.5)
            waited += 0.5
        
        if not result_manifest:
            return [] if not return_dataframe else None
        
        # Extract results
        if return_dataframe:
            import pandas as pd
            if result_manifest.result_sets and len(result_manifest.result_sets) > 0:
                result_set = result_manifest.result_sets[0]
                if result_set.rows:
                    # Convert to DataFrame
                    columns = [col.name for col in result_set.schema.columns]
                    data = [[cell.value for cell in row.values] for row in result_set.rows]
                    return pd.DataFrame(data, columns=columns)
            return pd.DataFrame()
        else:
            # Return list of tuples
            if result_manifest.result_sets and len(result_manifest.result_sets) > 0:
                result_set = result_manifest.result_sets[0]
                if result_set.rows:
                    return [[cell.value for cell in row.values] for row in result_set.rows]
            return []
            
    except Exception as e:
        print(f"Error executing SQL: {e}")
        raise

