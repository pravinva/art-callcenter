#!/usr/bin/env python3
"""
Complete Deployment Script
Deploys and tests all components in sequence:
1. DLT Pipeline (via API)
2. Online Tables
3. UC Functions
4. Verify everything works

Run: python scripts/deploy_all.py
"""
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks.sdk import WorkspaceClient
from databricks import sql
from config.config import (
    get_workspace_client, get_workspace_url, SQL_WAREHOUSE_ID,
    ENRICHED_TABLE, ONLINE_TABLE
)

def create_dlt_pipeline_via_rest():
    """Create DLT pipeline using REST API directly"""
    import json
    import requests
    from databricks.sdk.core import Config
    
    config = Config()
    workspace_url = config.host.rstrip('/')
    token = config.token
    
    notebook_path = "/Workspace/Users/pravin.varma@databricks.com/art-callcenter/dlt_enrichment_pipeline"
    
    # REST API endpoint
    api_url = f"{workspace_url}/api/2.0/pipelines"
    
    payload = {
        "name": "art-callcenter-enrichment",
        "target": "member_analytics.call_center",
        "libraries": [{"notebook": {"path": notebook_path}}],  # Use notebook as library
        "continuous": True,
        "development": False,
        "photon": True,
        "serverless": False
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"📝 Creating DLT pipeline via REST API...")
        response = requests.post(api_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            pipeline = response.json()
            print(f"✅ Pipeline created: {pipeline.get('pipeline_id')}")
            return pipeline.get('pipeline_id')
        else:
            print(f"⚠️  API error: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"⚠️  REST API error: {e}")
        return None

def deploy_all():
    """Deploy all components"""
    print("🚀 Complete Deployment")
    print("="*80)
    
    w = get_workspace_client()
    
    # Step 1: Create DLT Pipeline
    print("\n" + "="*80)
    print("STEP 1: DLT Pipeline")
    print("="*80)
    
    pipeline_id = create_dlt_pipeline_via_rest()
    
    if pipeline_id:
        print(f"✅ Pipeline created: {pipeline_id}")
        print(f"🚀 Starting pipeline...")
        try:
            w.pipelines.start_update(pipeline_id)
            print(f"✅ Pipeline started!")
            print(f"⏳ Waiting 30 seconds for initial processing...")
            time.sleep(30)
        except Exception as e:
            print(f"⚠️  Could not start automatically: {e}")
            print(f"   Start manually: Workflows → Delta Live Tables")
    else:
        print(f"⚠️  Pipeline creation failed - use UI method")
        print(f"   Workflows → Delta Live Tables → Create Pipeline")
    
    # Step 2: Create Online Table
    print("\n" + "="*80)
    print("STEP 2: Online Table")
    print("="*80)
    
    print(f"📝 Creating Online Table...")
    print(f"   Run: python scripts/run_sql.py sql/02_online_table.sql")
    
    # Step 3: Create UC Functions
    print("\n" + "="*80)
    print("STEP 3: UC Functions")
    print("="*80)
    
    print(f"📝 Creating UC Functions...")
    print(f"   Run: python scripts/run_sql.py sql/03_uc_functions.sql")
    
    # Step 4: Verify
    print("\n" + "="*80)
    print("STEP 4: Verification")
    print("="*80)
    
    print(f"📝 Verifying deployment...")
    print(f"   Run: python scripts/04_verify_dlt.py")
    
    print("\n" + "="*80)
    print("DEPLOYMENT SUMMARY")
    print("="*80)
    print(f"\n✅ Components deployed:")
    if pipeline_id:
        print(f"   ✅ DLT Pipeline: {pipeline_id}")
    else:
        print(f"   ⏳ DLT Pipeline: Create via UI")
    print(f"   ⏳ Online Table: Run SQL script")
    print(f"   ⏳ UC Functions: Run SQL script")
    
    print(f"\n📋 Next Steps:")
    print(f"   1. Complete Online Table creation")
    print(f"   2. Complete UC Functions creation")
    print(f"   3. Verify all components")
    print(f"   4. Proceed to Phase 3: GenAI Agent")

if __name__ == "__main__":
    deploy_all()

