#!/usr/bin/env python3
"""
Enable Change Data Feed (CDF) on KB Articles Table
Required for delta-sync vector search indexes.

Run: python scripts/enable_cdf_kb_table.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import KB_TABLE, SQL_WAREHOUSE_ID
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
import time

def enable_cdf():
    """Enable Change Data Feed on KB articles table"""
    print("🔄 Enabling Change Data Feed (CDF) on KB Articles Table")
    print("="*80)
    
    print(f"\n📊 Table: {KB_TABLE}")
    
    w = WorkspaceClient()
    
    # SQL to enable CDF
    enable_cdf_sql = f"""
    ALTER TABLE {KB_TABLE} 
    SET TBLPROPERTIES (
        'delta.enableChangeDataFeed' = 'true'
    )
    """
    
    print(f"\n🔧 Executing SQL to enable CDF...")
    print(f"SQL: {enable_cdf_sql.strip()}")
    
    try:
        response = w.statement_execution.execute_statement(
            warehouse_id=SQL_WAREHOUSE_ID,
            statement=enable_cdf_sql,
            wait_timeout="30s"
        )
        
        statement_id = response.statement_id
        max_wait = 30
        waited = 0
        
        while waited < max_wait:
            status = w.statement_execution.get_statement(statement_id)
            if status.status.state == StatementState.SUCCEEDED:
                print(f"\n✅ CDF enabled successfully on {KB_TABLE}")
                return True
            elif status.status.state in [StatementState.FAILED, StatementState.CANCELED]:
                error_msg = f"SQL execution failed: {status.status.state}"
                if hasattr(status.status, 'message') and status.status.message:
                    error_msg = status.status.message
                
                # Check if CDF is already enabled
                if "already enabled" in error_msg.lower() or "already set" in error_msg.lower():
                    print(f"\n✅ CDF is already enabled on {KB_TABLE}")
                    return True
                
                raise Exception(error_msg)
            
            time.sleep(0.5)
            waited += 0.5
        
        raise Exception("SQL execution timed out")
        
    except Exception as e:
        error_str = str(e).lower()
        if "already enabled" in error_str or "already set" in error_str:
            print(f"\n✅ CDF is already enabled on {KB_TABLE}")
            return True
        else:
            print(f"\n❌ Error enabling CDF: {e}")
            return False

if __name__ == "__main__":
    success = enable_cdf()
    if success:
        print("\n" + "="*80)
        print("✅ CDF Enabled - Ready to create vector index!")
        print("="*80)
        print("\n💡 Next step: Run python scripts/create_kb_vector_index.py")
    sys.exit(0 if success else 1)

