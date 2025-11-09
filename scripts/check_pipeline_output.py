#!/usr/bin/env python3
"""
Check DLT Pipeline Details and Output
Checks pipeline status and verifies if enriched table exists.

Run: python scripts/check_pipeline_output.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks.sdk import WorkspaceClient
from databricks import sql
from config.config import get_workspace_client, get_workspace_url, SQL_WAREHOUSE_ID

def check_pipeline_details():
    """Check DLT pipeline details"""
    w = get_workspace_client()
    pipeline_id = "4bc41e3f-072e-4e5a-80a9-dbb323f2994b"
    
    print("🔍 Checking DLT Pipeline Details")
    print("="*80)
    
    try:
        pipeline = w.pipelines.get(pipeline_id)
        
        print(f"\n📋 Pipeline Information:")
        print(f"   ID: {pipeline_id}")
        print(f"   Name: {pipeline.name}")
        print(f"   State: {pipeline.state}")
        print(f"   Target: {getattr(pipeline, 'target', 'N/A')}")
        print(f"   Continuous: {getattr(pipeline, 'continuous', 'N/A')}")
        
        # Check latest updates
        if hasattr(pipeline, 'latest_updates') and pipeline.latest_updates:
            latest = pipeline.latest_updates[0]
            print(f"\n📊 Latest Update:")
            print(f"   Update ID: {latest.update_id}")
            print(f"   State: {latest.state}")
            print(f"   Creation Time: {getattr(latest, 'creation_time', 'N/A')}")
            
            # Check for errors
            if hasattr(latest, 'state') and 'FAILED' in str(latest.state):
                print(f"\n⚠️  Pipeline update failed!")
                if hasattr(latest, 'error'):
                    print(f"   Error: {latest.error}")
        
        # List all tables in the target schema
        print(f"\n📊 Checking tables in target schema...")
        try:
            tables_query = "SHOW TABLES IN member_analytics.call_center"
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
            cursor.execute(tables_query)
            tables = cursor.fetchall()
            
            print(f"   Found {len(tables)} tables:")
            for table in tables:
                print(f"   - {table[1]}.{table[0]}")
            
            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"   Could not list tables: {e}")
        
    except Exception as e:
        print(f"❌ Error checking pipeline: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_pipeline_details()

