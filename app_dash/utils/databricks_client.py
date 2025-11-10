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
                # Also store status for fallback access
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
        
        # Get results using chunked API (like Streamlit version)
        all_rows = []
        chunk_index = 0
        
        try:
            while True:
                result_chunk = w.statement_execution.get_statement_result_chunk_n(statement_id, chunk_index)
                if not result_chunk or not result_chunk.data_array:
                    break
                
                all_rows.extend(result_chunk.data_array)
                
                # Check if there are more chunks
                if not result_chunk.next_chunk_index or result_chunk.next_chunk_index == chunk_index:
                    break
                chunk_index = result_chunk.next_chunk_index
        except Exception as chunk_error:
            # Fallback to manifest-based approach if chunk API fails
            print(f"Chunk API failed, using manifest: {chunk_error}")
            all_rows = []
        
        # Extract results - handle both chunked and manifest-based results
        if return_dataframe:
            import pandas as pd
            if all_rows:
                # Use chunked results
                if result_manifest and result_manifest.schema and result_manifest.schema.columns:
                    columns = [col.name for col in result_manifest.schema.columns]
                    df = pd.DataFrame(all_rows, columns=columns)
                    return df
                elif all_rows and isinstance(all_rows[0], dict):
                    # Dict format
                    df = pd.DataFrame(all_rows)
                    return df
                else:
                    # Array format - infer columns
                    num_cols = len(all_rows[0]) if all_rows else 0
                    columns = [f"col_{i+1}" for i in range(num_cols)]
                    df = pd.DataFrame(all_rows, columns=columns)
                    return df
            # Fallback: try manifest result_sets
            elif result_manifest and hasattr(result_manifest, 'result_sets') and result_manifest.result_sets and len(result_manifest.result_sets) > 0:
                result_set = result_manifest.result_sets[0]
                if result_set.rows:
                    columns = [col.name for col in result_set.schema.columns]
                    data = [[cell.value for cell in row.values] for row in result_set.rows]
                    return pd.DataFrame(data, columns=columns)
            return pd.DataFrame()
        else:
            # Return list of tuples
            if all_rows:
                return all_rows
            # Fallback: try manifest result_sets
            elif result_manifest and hasattr(result_manifest, 'result_sets') and result_manifest.result_sets and len(result_manifest.result_sets) > 0:
                result_set = result_manifest.result_sets[0]
                if result_set.rows:
                    return [[cell.value for cell in row.values] for row in result_set.rows]
            return []
            
    except Exception as e:
        print(f"Error executing SQL: {e}")
        raise

