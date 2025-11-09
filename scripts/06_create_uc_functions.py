#!/usr/bin/env python3
"""
Phase 3: UC Functions Creation
Create UC Functions that will be used as agent tools.

Run: python scripts/06_create_uc_functions.py
Or use SQL: databricks-sql-cli -f sql/03_uc_functions.sql
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks.sdk import WorkspaceClient
from config.config import (
    get_workspace_client,
    CATALOG_NAME, SCHEMA_NAME,
    FUNCTION_GET_CALL_CONTEXT, FUNCTION_SEARCH_KB,
    FUNCTION_CHECK_COMPLIANCE, FUNCTION_GET_MEMBER_HISTORY
)

def create_uc_functions():
    """Create UC Functions via SQL"""
    print("🚀 Phase 3: Creating UC Functions")
    print("="*80)
    
    w = get_workspace_client()
    
    print("\n📝 Note: UC Functions must be created via SQL")
    print("   Run: databricks-sql-cli -f sql/03_uc_functions.sql")
    print("\n   Or execute the SQL commands in sql/03_uc_functions.sql manually")
    
    print("\n✅ UC Functions will be created:")
    print(f"   - {FUNCTION_GET_CALL_CONTEXT}")
    print(f"   - {FUNCTION_SEARCH_KB}")
    print(f"   - {FUNCTION_CHECK_COMPLIANCE}")
    print(f"   - {FUNCTION_GET_MEMBER_HISTORY}")

if __name__ == "__main__":
    create_uc_functions()

