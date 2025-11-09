#!/usr/bin/env python3
"""
Check Pipeline Update Status
Checks if pipeline update completed successfully and if enriched table exists.

Run: python scripts/check_update_status.py
"""
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks.sdk import WorkspaceClient
from databricks import sql
from config.config import get_workspace_client, get_workspace_url, SQL_WAREHOUSE_ID

def check_update_status():
    """Check pipeline update status"""
    w = get_workspace_client()
    pipeline_id = "4bc41e3f-072e-4e5a-80a9-dbb323f2994b"
    
    print("🔍 Checking Pipeline Update Status")
    print("="*80)
    
    try:
        pipeline = w.pipelines.get(pipeline_id)
        
        if hasattr(pipeline, 'latest_updates') and pipeline.latest_updates:
            latest = pipeline.latest_updates[0]
            print(f"\n📊 Latest Update:")
            print(f"   Update ID: {latest.update_id}")
            print(f"   State: {latest.state}")
            
            # Check update details
            try:
                update_details = w.pipelines.get_update(pipeline_id, latest.update_id)
                print(f"   Status: {getattr(update_details, 'state', 'N/A')}")
                
                # Check for errors
                if hasattr(update_details, 'error'):
                    if update_details.error:
                        print(f"\n❌ Update Error:")
                        print(f"   {update_details.error}")
                
            except Exception as e:
                print(f"   Could not get update details: {e}")
        
        # Check if enriched table exists
        print(f"\n📊 Checking for enriched_transcripts table...")
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
        
        connection = sql.connect(
            server_hostname=workspace_url.replace('https://', ''),
            http_path=http_path,
            access_token=token
        )
        
        cursor = connection.cursor()
        
        # Check if table exists
        try:
            cursor.execute("SELECT COUNT(*) FROM member_analytics.call_center.enriched_transcripts LIMIT 1")
            count = cursor.fetchone()[0]
            print(f"✅ enriched_transcripts table exists!")
            print(f"   Row count: {count}")
            
            # Get sample
            cursor.execute("SELECT call_id, sentiment, intent_category, compliance_flag FROM member_analytics.call_center.enriched_transcripts LIMIT 3")
            samples = cursor.fetchall()
            print(f"\n📋 Sample enriched records:")
            for row in samples:
                print(f"   Call: {row[0]}, Sentiment: {row[1]}, Intent: {row[2]}, Compliance: {row[3]}")
            
        except Exception as e:
            print(f"⚠️  enriched_transcripts table not found: {e}")
            print(f"\n💡 Possible reasons:")
            print(f"   1. Pipeline is still processing (wait longer)")
            print(f"   2. Pipeline encountered an error (check UI)")
            print(f"   3. Table name mismatch")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_update_status()

