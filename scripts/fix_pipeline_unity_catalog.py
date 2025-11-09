#!/usr/bin/env python3
"""
Fix DLT Pipeline: Enable Unity Catalog
Updates the DLT pipeline configuration to enable Unity Catalog on the cluster.

Run: python scripts/fix_pipeline_unity_catalog.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
import requests
import json

def fix_pipeline_unity_catalog():
    """Update pipeline to enable Unity Catalog"""
    print("🔧 Fixing DLT Pipeline: Enabling Unity Catalog")
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
    
    print(f"\n📊 Current Configuration:")
    spec = pipeline.get('spec', {})
    print(f"   Name: {pipeline.get("name")}")
    print(f"   Target: {spec.get("target")}")
    print(f"   Continuous: {spec.get("continuous")}")
    
    # Build update payload with Unity Catalog enabled
    update_payload = {
        "name": pipeline.get("name"),
        "target": spec.get("target"),
        "libraries": spec.get("libraries", []),
        "continuous": spec.get("continuous", True),
        "development": spec.get("development", False),
        "photon": spec.get("photon", True),
        "serverless": spec.get("serverless", False),
        "clusters": [
            {
                # Note: spark_version is managed by DLT automatically
                "node_type_id": "i3.xlarge",
                "num_workers": 0,
                "spark_conf": {
                    "spark.databricks.cluster.profile": "singleNode",
                    "spark.master": "local[*]"
                },
                "custom_tags": {
                    "ResourceClass": "SingleNode"
                },
                "enable_unity_catalog": True  # CRITICAL: Enable Unity Catalog
            }
        ]
    }
    
    print(f"\n📝 Updating pipeline with Unity Catalog enabled...")
    print(f"   Cluster Configuration:")
    print(f"     - Unity Catalog: ENABLED")
    print(f"     - Spark Version: (managed by DLT)")
    print(f"     - Node Type: {update_payload['clusters'][0]['node_type_id']}")
    print(f"     - Workers: {update_payload['clusters'][0]['num_workers']}")
    
    # Update pipeline
    update_url = f'{workspace_url}/api/2.0/pipelines/{pipeline_id}'
    response = requests.put(update_url, headers=headers, json=update_payload)
    
    if response.status_code == 200:
        print(f"\n✅ Pipeline updated successfully!")
        updated_pipeline = response.json()
        print(f"   Pipeline ID: {pipeline_id}")
        
        # Verify Unity Catalog is enabled
        updated_spec = updated_pipeline.get('spec', {})
        clusters = updated_spec.get('clusters', [])
        if clusters:
            uc_enabled = clusters[0].get('enable_unity_catalog', False)
            if uc_enabled:
                print(f"   ✅ Unity Catalog: ENABLED")
            else:
                print(f"   ⚠️  Unity Catalog: NOT ENABLED (check manually)")
        
        print(f"\n📋 Next Steps:")
        print(f"   1. Restart the pipeline to apply changes")
        print(f"   2. Monitor pipeline status")
        print(f"   3. Verify enriched_transcripts table is created")
        
        return True
    else:
        print(f"\n❌ Error updating pipeline: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

if __name__ == "__main__":
    success = fix_pipeline_unity_catalog()
    if success:
        print(f"\n🚀 Ready to restart pipeline!")
        print(f"   Run: python scripts/restart_pipeline.py")

