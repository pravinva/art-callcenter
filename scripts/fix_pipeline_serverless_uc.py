#!/usr/bin/env python3
"""
Fix DLT Pipeline: Switch to Serverless Mode with Unity Catalog
Serverless mode automatically enables Unity Catalog when catalog is specified.

Run: python scripts/fix_pipeline_serverless_uc.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
import requests
import json

def fix_to_serverless():
    """Update pipeline to serverless mode with Unity Catalog"""
    print("🔧 Fixing DLT Pipeline: Serverless Mode with Unity Catalog")
    print("="*80)
    
    config = Config()
    workspace_url = config.host.rstrip('/')
    token = config.token
    
    pipeline_id = '4bc41e3f-072e-4e5a-80a9-dbb323f2994b'
    notebook_path = '/Workspace/Users/pravin.varma@databricks.com/art-callcenter/dlt_enrichment_pipeline'
    
    # Get current pipeline configuration
    api_url = f'{workspace_url}/api/2.0/pipelines/{pipeline_id}'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(api_url, headers=headers)
    pipeline = response.json()
    
    spec = pipeline.get('spec', {})
    
    print(f"\n📊 Current Configuration:")
    print(f"   Target: {spec.get('target')}")
    print(f"   Serverless: {spec.get('serverless', False)}")
    
    # Build update payload for serverless with Unity Catalog
    # Key: catalog and target (schema only) must be specified separately
    update_payload = {
        "name": pipeline.get("name"),
        "catalog": "member_analytics",  # Catalog name (required for serverless + UC)
        "target": "call_center",  # Schema only (not full three-part name)
        "libraries": [
            {
                "notebook": {
                    "path": notebook_path
                }
            }
        ],
        "continuous": spec.get("continuous", True),
        "development": spec.get("development", False),
        "photon": True,
        "serverless": True  # Enable serverless - Unity Catalog auto-enabled
        # No clusters config needed for serverless
    }
    
    print(f"\n📝 Updating to Serverless Mode:")
    print(f"   Serverless: True (Unity Catalog auto-enabled)")
    print(f"   Catalog: member_analytics")
    print(f"   Target: call_center (schema only)")
    print(f"   Photon: True")
    
    # Update pipeline
    update_url = f'{workspace_url}/api/2.0/pipelines/{pipeline_id}'
    response = requests.put(update_url, headers=headers, json=update_payload)
    
    if response.status_code == 200:
        print(f"\n✅ Pipeline updated successfully!")
        updated_pipeline = response.json()
        updated_spec = updated_pipeline.get('spec', {})
        
        print(f"   Serverless: {updated_spec.get('serverless')}")
        print(f"   Catalog: {updated_spec.get('catalog')}")
        print(f"   Target: {updated_spec.get('target')}")
        print(f"   Unity Catalog: Automatically enabled in serverless mode")
        
        print(f"\n📋 Next Steps:")
        print(f"   1. Restart the pipeline")
        print(f"   2. Monitor pipeline status")
        print(f"   3. Verify enriched_transcripts table is created")
        
        return True
    else:
        print(f"\n❌ Error updating pipeline: {response.status_code}")
        print(f"   Response: {response.text}")
        
        # Check if it's the storage location issue
        if "storage location" in response.text.lower():
            print(f"\n⚠️  Note: Pipeline has existing storage location")
            print(f"   You may need to recreate the pipeline with serverless from the start")
            print(f"   Or try updating via UI with the JSON configuration")
        
        return False

if __name__ == "__main__":
    success = fix_to_serverless()
    if success:
        print(f"\n🚀 Ready to restart pipeline!")
        print(f"   Run: python scripts/restart_pipeline.py")
    else:
        print(f"\n⚠️  Could not update pipeline automatically")
        print(f"\n💡 Manual Update via UI:")
        print(f"   1. Go to: Workflows → Delta Live Tables → art-callcenter-enrichment")
        print(f"   2. Click 'Settings' → 'Compute'")
        print(f"   3. Update configuration with:")
        print(f"      - serverless: true")
        print(f"      - catalog: member_analytics")
        print(f"      - target: call_center")
        print(f"   4. Save and restart")

