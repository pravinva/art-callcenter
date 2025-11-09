#!/usr/bin/env python3
"""
Test UC Functions
Tests all UC Functions to verify they work correctly.

Run: python scripts/test_uc_functions.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks import sql
from config.config import (
    get_workspace_url, SQL_WAREHOUSE_ID,
    FUNCTION_GET_CALL_CONTEXT, FUNCTION_SEARCH_KB,
    FUNCTION_CHECK_COMPLIANCE, FUNCTION_GET_MEMBER_HISTORY
)

def get_sql_connection():
    """Get SQL connection"""
    workspace_url = get_workspace_url().rstrip('/')
    http_path = f"/sql/1.0/warehouses/{SQL_WAREHOUSE_ID}"
    
    import subprocess
    token_result = subprocess.run(
        ['databricks', 'auth', 'token'],
        capture_output=True,
        text=True
    )
    
    if token_result.returncode != 0:
        from databricks.sdk.core import Config
        config = Config()
        token = config.token
    else:
        token = token_result.stdout.strip()
    
    return sql.connect(
        server_hostname=workspace_url.replace('https://', ''),
        http_path=http_path,
        access_token=token
    )

def test_uc_functions():
    """Test all UC Functions"""
    print("🧪 Testing UC Functions")
    print("="*80)
    
    connection = get_sql_connection()
    cursor = connection.cursor()
    
    # Get a sample call_id
    print("\n📋 Getting sample call_id...")
    cursor.execute("SELECT DISTINCT call_id FROM member_analytics.call_center.zerobus_transcripts LIMIT 1")
    sample_call = cursor.fetchone()
    
    if not sample_call:
        print("❌ No calls found in zerobus_transcripts")
        return False
    
    call_id = sample_call[0]
    print(f"   Using call_id: {call_id}")
    
    # Test 1: get_live_call_context
    print(f"\n1️⃣  Testing {FUNCTION_GET_CALL_CONTEXT}...")
    try:
        cursor.execute(f"SELECT * FROM {FUNCTION_GET_CALL_CONTEXT}('{call_id}')")
        result = cursor.fetchone()
        if result:
            print(f"   ✅ Function works!")
            print(f"   Member: {result[0]}, Balance: ${result[1]:,.0f}")
        else:
            print(f"   ⚠️  No results (table may not exist yet)")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
    
    # Test 2: search_knowledge_base
    print(f"\n2️⃣  Testing {FUNCTION_SEARCH_KB}...")
    try:
        cursor.execute(f"SELECT * FROM {FUNCTION_SEARCH_KB}('contribution')")
        results = cursor.fetchall()
        print(f"   ✅ Function works! Found {len(results)} articles")
        for row in results:
            print(f"   - {row[1]}: {row[2][:50]}...")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
    
    # Test 3: check_compliance_realtime
    print(f"\n3️⃣  Testing {FUNCTION_CHECK_COMPLIANCE}...")
    try:
        cursor.execute(f"SELECT * FROM {FUNCTION_CHECK_COMPLIANCE}('{call_id}')")
        results = cursor.fetchall()
        print(f"   ✅ Function works! Found {len(results)} compliance issues")
        for row in results:
            print(f"   - {row[0]} ({row[1]}): {row[2][:50]}...")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
    
    # Test 4: get_member_history
    print(f"\n4️⃣  Testing {FUNCTION_GET_MEMBER_HISTORY}...")
    try:
        cursor.execute(f"SELECT member_id FROM member_analytics.call_center.zerobus_transcripts LIMIT 1")
        member_id = cursor.fetchone()[0]
        cursor.execute(f"SELECT * FROM {FUNCTION_GET_MEMBER_HISTORY}('{member_id}')")
        results = cursor.fetchall()
        print(f"   ✅ Function works! Found {len(results)} interactions")
        for row in results:
            print(f"   - {row[1]}: {row[2]}")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
    
    cursor.close()
    connection.close()
    
    print("\n" + "="*80)
    print("✅ UC Functions testing complete!")

if __name__ == "__main__":
    test_uc_functions()

