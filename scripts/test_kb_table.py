#!/usr/bin/env python3
"""
Test KB table and SQL function directly
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import KB_TABLE, FUNCTION_SEARCH_KB, SQL_WAREHOUSE_ID
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
import pandas as pd
import time

def get_workspace_client():
    """Get WorkspaceClient"""
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
            
            time.sleep(0.2)
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
            
            if not result_chunk.next_chunk_index or result_chunk.next_chunk_index == chunk_index:
                break
            chunk_index = result_chunk.next_chunk_index
        
        if return_dataframe:
            if all_rows and result_manifest and result_manifest.schema and result_manifest.schema.columns:
                columns = [col.name for col in result_manifest.schema.columns]
                df = pd.DataFrame(all_rows, columns=columns)
                return df
            elif all_rows:
                num_cols = len(all_rows[0]) if all_rows else 0
                columns = [f"col_{i+1}" for i in range(num_cols)]
                df = pd.DataFrame(all_rows, columns=columns)
                return df
            return pd.DataFrame()
        else:
            return all_rows
    except Exception as e:
        raise Exception(f"SQL execution error: {e}")

def test_kb_table():
    """Test KB table and SQL function"""
    print("🧪 Testing KB Table and SQL Function")
    print("="*80)
    
    # Test 1: Check if KB table exists and has data
    print("\n📝 Test 1: Check KB Table")
    print("-" * 80)
    try:
        query = f"SELECT COUNT(*) as count FROM {KB_TABLE}"
        df = execute_sql(query, return_dataframe=True)
        count = df.iloc[0]['count'] if not df.empty else 0
        print(f"  ✅ KB Table exists: {KB_TABLE}")
        print(f"  📊 Total articles: {count}")
        
        if count > 0:
            # Get sample articles
            query = f"SELECT article_id, title, category FROM {KB_TABLE} LIMIT 5"
            df = execute_sql(query, return_dataframe=True)
            print(f"\n  Sample articles:")
            for _, row in df.iterrows():
                print(f"    - [{row['article_id']}] {row['title']} ({row['category']})")
        else:
            print(f"  ⚠️  KB table is empty!")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test 2: Test SQL function directly
    print("\n📝 Test 2: Test SQL Function")
    print("-" * 80)
    test_queries = [
        "complaint",
        "contribution",
        "withdrawal"
    ]
    
    for query in test_queries:
        print(f"\n  Query: '{query}'")
        try:
            sql_query = f"SELECT * FROM {FUNCTION_SEARCH_KB}('{query}')"
            df = execute_sql(sql_query, return_dataframe=True)
            if not df.empty:
                print(f"    ✅ Found {len(df)} results")
                for i, row in df.iterrows():
                    print(f"      {i+1}. [{row.get('article_id', 'N/A')}] {row.get('title', 'N/A')[:50]}...")
            else:
                print(f"    ⚠️  No results")
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    test_kb_table()

