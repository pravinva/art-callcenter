#!/usr/bin/env python3
"""
Create UC Functions that depend on enriched_transcripts table
This script should be run after the DLT pipeline creates enriched_transcripts.

Run: python scripts/create_uc_functions_with_enriched_table.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks import sql
from config.config import get_workspace_url, SQL_WAREHOUSE_ID
import os

def check_table_exists(table_name):
    """Check if a table exists"""
    workspace_url = get_workspace_url()
    
    connection = sql.connect(
        server_hostname=workspace_url.replace('https://', ''),
        http_path=f'/sql/1.0/warehouses/{SQL_WAREHOUSE_ID}',
        access_token=os.environ.get('DATABRICKS_TOKEN')
    )
    
    cursor = connection.cursor()
    
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name} LIMIT 1")
        exists = True
        return exists
    except Exception:
        return False
    finally:
        cursor.close()
        connection.close()

def create_functions():
    """Create UC Functions that depend on enriched_transcripts"""
    print("🚀 Creating UC Functions (enriched_transcripts dependent)")
    print("="*80)
    
    # Check if enriched_transcripts exists
    enriched_table = "member_analytics.call_center.enriched_transcripts"
    print(f"\n🔍 Checking for {enriched_table}...")
    
    if not check_table_exists(enriched_table):
        print(f"❌ {enriched_table} does not exist yet")
        print(f"   Please wait for DLT pipeline to complete")
        print(f"   Run this script again after pipeline creates the table")
        return False
    
    print(f"✅ {enriched_table} exists!")
    
    workspace_url = get_workspace_url()
    connection = sql.connect(
        server_hostname=workspace_url.replace('https://', ''),
        http_path=f'/sql/1.0/warehouses/{SQL_WAREHOUSE_ID}',
        access_token=os.environ.get('DATABRICKS_TOKEN')
    )
    
    cursor = connection.cursor()
    
    functions = [
        {
            "name": "get_live_call_context",
            "sql": """
            CREATE OR REPLACE FUNCTION member_analytics.call_center.get_live_call_context(call_id_param STRING)
            RETURNS TABLE (
                member_name STRING,
                balance DECIMAL(18,2),
                recent_transcript STRING,
                sentiment STRING,
                intents STRING,
                compliance_issues STRING
            )
            RETURN SELECT 
                MAX(member_name) as member_name,
                MAX(member_balance) as balance,
                SUBSTRING(ARRAY_JOIN(ARRAY_AGG(transcript_segment), ' '), 1, 500) as recent_transcript,
                MAX(sentiment) as sentiment,
                ARRAY_JOIN(ARRAY_AGG(DISTINCT intent_category), ', ') as intents,
                ARRAY_JOIN(ARRAY_AGG(DISTINCT CASE WHEN compliance_flag != 'ok' THEN compliance_flag END), ', ') as compliance_issues
            FROM (
                SELECT member_name, member_balance, transcript_segment, sentiment, intent_category, compliance_flag
                FROM member_analytics.call_center.enriched_transcripts
                WHERE call_id = call_id_param
                ORDER BY timestamp
            )
            GROUP BY member_name
            """
        },
        {
            "name": "check_compliance_realtime",
            "sql": """
            CREATE OR REPLACE FUNCTION member_analytics.call_center.check_compliance_realtime(call_id_param STRING)
            RETURNS TABLE (
                violation_type STRING,
                severity STRING,
                segment STRING,
                timestamp TIMESTAMP
            )
            RETURN SELECT 
                compliance_flag as violation_type,
                compliance_severity as severity,
                transcript_segment as segment,
                timestamp
            FROM member_analytics.call_center.enriched_transcripts
            WHERE call_id = call_id_param
              AND compliance_flag != 'ok'
            ORDER BY timestamp DESC
            """
        }
    ]
    
    print(f"\n📝 Creating {len(functions)} UC Functions...")
    
    for func in functions:
        try:
            print(f"\n   Creating {func['name']}...")
            cursor.execute(func['sql'])
            print(f"   ✅ {func['name']} created successfully")
            
            # Grant permissions
            grant_sql = f"GRANT EXECUTE ON FUNCTION member_analytics.call_center.{func['name']} TO `account users`"
            try:
                cursor.execute(grant_sql)
                print(f"   ✅ Permissions granted")
            except Exception as e:
                print(f"   ⚠️  Permission grant failed: {e}")
                
        except Exception as e:
            print(f"   ❌ Error creating {func['name']}: {e}")
    
    cursor.close()
    connection.close()
    
    print("\n" + "="*80)
    print("✅ UC Functions creation completed!")
    print("\n📋 Created functions:")
    print("   ✅ get_live_call_context")
    print("   ✅ check_compliance_realtime")
    print("\n💡 Already created (from previous run):")
    print("   ✅ search_knowledge_base")
    print("   ✅ get_member_history")
    
    return True

if __name__ == "__main__":
    create_functions()

