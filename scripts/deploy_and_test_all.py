#!/usr/bin/env python3
"""
Deploy and Test All Components
Sequentially deploys and tests each component before proceeding.

Run: python scripts/deploy_and_test_all.py
"""
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.run_sql import execute_sql_file
from scripts.deploy_all import create_dlt_pipeline_via_rest
from scripts.04_verify_dlt import verify_tables, check_enrichment
from databricks.sdk import WorkspaceClient
from config.config import get_workspace_client

def deploy_and_test_all():
    """Deploy and test all components sequentially"""
    print("🚀 Complete Deployment and Testing")
    print("="*80)
    
    w = get_workspace_client()
    all_passed = True
    
    # Step 1: DLT Pipeline
    print("\n" + "="*80)
    print("STEP 1: Deploy DLT Pipeline")
    print("="*80)
    
    pipeline_id = create_dlt_pipeline_via_rest()
    
    if pipeline_id:
        print(f"✅ Pipeline created: {pipeline_id}")
        print(f"🚀 Starting pipeline...")
        try:
            w.pipelines.start_update(pipeline_id)
            print(f"✅ Pipeline started!")
            print(f"⏳ Waiting 60 seconds for initial processing...")
            time.sleep(60)
        except Exception as e:
            print(f"⚠️  Could not start automatically: {e}")
            all_passed = False
    else:
        print(f"❌ Pipeline creation failed")
        print(f"   Create manually: Workflows → Delta Live Tables")
        all_passed = False
    
    # Step 2: Online Table
    print("\n" + "="*80)
    print("STEP 2: Create Online Table")
    print("="*80)
    
    try:
        sql_file = Path(__file__).parent.parent / "sql" / "02_online_table.sql"
        execute_sql_file(str(sql_file))
        print(f"✅ Online Table created")
    except Exception as e:
        print(f"⚠️  Online Table creation: {e}")
        all_passed = False
    
    # Step 3: UC Functions
    print("\n" + "="*80)
    print("STEP 3: Create UC Functions")
    print("="*80)
    
    try:
        sql_file = Path(__file__).parent.parent / "sql" / "03_uc_functions.sql"
        execute_sql_file(str(sql_file))
        print(f"✅ UC Functions created")
    except Exception as e:
        print(f"⚠️  UC Functions creation: {e}")
        all_passed = False
    
    # Step 4: Verify Everything
    print("\n" + "="*80)
    print("STEP 4: Verify Deployment")
    print("="*80)
    
    try:
        results = verify_tables()
        if results.get("Enriched Table", {}).get("exists"):
            check_enrichment()
        print(f"✅ Verification complete")
    except Exception as e:
        print(f"⚠️  Verification error: {e}")
        all_passed = False
    
    # Summary
    print("\n" + "="*80)
    print("DEPLOYMENT SUMMARY")
    print("="*80)
    
    if all_passed:
        print(f"\n✅ All components deployed and tested successfully!")
        print(f"\n📋 Ready for Phase 3: GenAI Agent")
    else:
        print(f"\n⚠️  Some components need attention")
        print(f"   Review errors above and retry")
    
    return all_passed

if __name__ == "__main__":
    success = deploy_and_test_all()
    sys.exit(0 if success else 1)

