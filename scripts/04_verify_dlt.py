#!/usr/bin/env python3
"""
Phase 2: Verify DLT Pipeline and Online Tables
Check that enrichment pipeline is working and Online Tables are accessible.

Run: python scripts/04_verify_dlt.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks import sql
from databricks.sdk import WorkspaceClient
from config.config import (
    get_workspace_url, SQL_WAREHOUSE_ID,
    ZEROBUS_TABLE, ENRICHED_TABLE, ONLINE_TABLE
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

def verify_tables():
    """Verify tables exist and have data"""
    print("🔍 Verifying Tables")
    print("="*80)
    
    connection = get_sql_connection()
    cursor = connection.cursor()
    
    tables_to_check = [
        ("Raw Zerobus Table", ZEROBUS_TABLE),
        ("Enriched Table", ENRICHED_TABLE),
        ("Online Table", ONLINE_TABLE)
    ]
    
    results = {}
    
    for table_name, table_path in tables_to_check:
        try:
            # Check if table exists and get row count
            query = f"SELECT COUNT(*) as cnt FROM {table_path}"
            cursor.execute(query)
            count = cursor.fetchone()[0]
            
            results[table_name] = {
                "exists": True,
                "count": count
            }
            
            print(f"\n✅ {table_name}: {table_path}")
            print(f"   Row count: {count:,}")
            
            # Get sample data if available
            if count > 0:
                sample_query = f"SELECT * FROM {table_path} LIMIT 3"
                cursor.execute(sample_query)
                samples = cursor.fetchall()
                print(f"   Sample records: {len(samples)}")
                
        except Exception as e:
            results[table_name] = {
                "exists": False,
                "error": str(e)
            }
            print(f"\n⚠️  {table_name}: {table_path}")
            print(f"   Error: {e}")
    
    cursor.close()
    connection.close()
    
    return results

def check_enrichment():
    """Check if enrichment is working"""
    print("\n" + "="*80)
    print("Enrichment Check")
    print("="*80)
    
    connection = get_sql_connection()
    cursor = connection.cursor()
    
    try:
        # Check if enriched table has sentiment, intent, compliance fields
        query = f"""
        SELECT 
            COUNT(*) as total,
            COUNT(DISTINCT sentiment) as sentiment_types,
            COUNT(DISTINCT intent_category) as intent_types,
            COUNT(DISTINCT CASE WHEN compliance_flag != 'ok' THEN compliance_flag END) as compliance_issues
        FROM {ENRICHED_TABLE}
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        print(f"\n📊 Enrichment Statistics:")
        print(f"   Total records: {result[0]:,}")
        print(f"   Sentiment types: {result[1]}")
        print(f"   Intent categories: {result[2]}")
        print(f"   Compliance issues found: {result[3]}")
        
        # Sample enriched records
        sample_query = f"""
        SELECT 
            call_id,
            speaker,
            sentiment,
            intent_category,
            compliance_flag,
            compliance_severity,
            SUBSTRING(transcript_segment, 1, 50) as sample_text
        FROM {ENRICHED_TABLE}
        WHERE compliance_flag != 'ok'
        LIMIT 5
        """
        
        cursor.execute(sample_query)
        compliance_samples = cursor.fetchall()
        
        if compliance_samples:
            print(f"\n⚠️  Compliance Issues Detected:")
            for row in compliance_samples:
                print(f"   - {row[4]} ({row[5]}): {row[6]}...")
        else:
            print(f"\n✅ No compliance issues found in sample")
        
    except Exception as e:
        print(f"\n⚠️  Could not check enrichment: {e}")
    
    cursor.close()
    connection.close()

def main():
    print("🚀 Phase 2: Verify DLT Pipeline and Online Tables")
    print("="*80)
    
    # Verify tables
    results = verify_tables()
    
    # Check enrichment
    if results.get("Enriched Table", {}).get("exists"):
        check_enrichment()
    
    # Summary
    print("\n" + "="*80)
    print("Summary")
    print("="*80)
    
    all_good = all(r.get("exists", False) for r in results.values())
    
    if all_good:
        print("\n✅ All tables exist and are accessible")
        print("\n📋 Next Steps:")
        print("   1. Verify data is flowing through DLT pipeline")
        print("   2. Check Online Table refresh")
        print("   3. Proceed to Phase 3: UC Functions and GenAI Agent")
    else:
        print("\n⚠️  Some tables may need to be created")
        print("   Run SQL scripts:")
        print("   - sql/02_dlt_enrichment.sql")
        print("   - sql/02_online_table.sql")

if __name__ == "__main__":
    main()

