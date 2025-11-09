#!/usr/bin/env python3
"""
Fix DLT Pipeline: Set Access Mode for Unity Catalog
Unity Catalog requires cluster access mode to be "SINGLE_USER" or "SHARED"

Run: python scripts/fix_pipeline_access_mode.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
import requests
import json

def fix_access_mode():
    """Fix pipeline by setting access mode for Unity Catalog"""
    print("🔧 Fixing DLT Pipeline: Setting Access Mode for Unity Catalog")
    print("="*80)
    
    config = Config()
    workspace_url = config.host.rstrip('/')
    token = config.token
    
    pipeline_id = '4bc41e3f-072e-4e5a-80a9-dbb323f2994b'
    
    # Get current pipeline configuration
    api_url = f'{workspace_url}/api/2.0/pipelines/{pipeline_id}'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(api_url, headers=headers)
    pipeline = response.json()
    
    spec = pipeline.get('spec', {})
    
    print(f"\n📊 Current Configuration:")
    print(f"   Target: {spec.get('target')}")
    print(f"   Serverless: {spec.get('serverless', False)}")
    
    # Build cluster config with access mode
    clusters = spec.get('clusters', [])
    if clusters:
        cluster = clusters[0].copy()
    else:
        cluster = {
            "node_type_id": "i3.xlarge",
            "num_workers": 0,
            "spark_conf": {
                "spark.databricks.cluster.profile": "singleNode",
                "spark.master": "local[*]"
            },
            "custom_tags": {
                "ResourceClass": "SingleNode"
            }
        }
    
    # Set access mode and Unity Catalog
    cluster["access_mode"] = "SINGLE_USER"  # Required for Unity Catalog
    cluster["enable_unity_catalog"] = True
    
    update_payload = {
        "name": pipeline.get("name"),
        "target": spec.get("target"),
        "libraries": spec.get("libraries", []),
        "continuous": spec.get("continuous", True),
        "development": spec.get("development", False),
        "photon": True,
        "serverless": False,
        "clusters": [cluster]
    }
    
    print(f"\n📝 Updating Configuration:")
    print(f"   Access Mode: SINGLE_USER (required for Unity Catalog)")
    print(f"   Unity Catalog: Enabled")
    print(f"   Node Type: {cluster.get('node_type_id')}")
    
    # Update pipeline
    update_url = f'{workspace_url}/api/2.0/pipelines/{pipeline_id}'
    response = requests.put(update_url, headers=headers, json=update_payload)
    
    if response.status_code == 200:
        print(f"\n✅ Pipeline updated successfully!")
        updated_pipeline = response.json()
        updated_spec = updated_pipeline.get('spec', {})
        updated_clusters = updated_spec.get('clusters', [])
        
        if updated_clusters:
            updated_cluster = updated_clusters[0]
            print(f"   Access Mode: {updated_cluster.get('access_mode')}")
            print(f"   Unity Catalog: {updated_cluster.get('enable_unity_catalog')}")
        
        print(f"\n📋 Next Steps:")
        print(f"   1. Restart the pipeline")
        print(f"   2. Monitor pipeline status")
        print(f"   3. Verify enriched_transcripts table is created")
        
        return True
    else:
        print(f"\n❌ Error updating pipeline: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

if __name__ == "__main__":
    success = fix_access_mode()
    if success:
        print(f"\n🚀 Ready to restart pipeline!")
        print(f"   Run: python scripts/restart_pipeline.py")
    else:
        print(f"\n⚠️  Could not update pipeline automatically")
        print(f"   Please update manually via UI with access_mode: SINGLE_USER")

