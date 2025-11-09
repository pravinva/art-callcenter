#!/usr/bin/env python3
"""
Fix DLT Pipeline: Use Serverless Mode with Catalog Specification
Serverless mode automatically enables Unity Catalog, but requires catalog specification.

Run: python scripts/fix_pipeline_serverless.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
import requests
import json

def fix_with_serverless():
    """Fix pipeline by using serverless mode with catalog specification"""
    print("🔧 Fixing DLT Pipeline: Serverless Mode with Catalog")
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
    target = spec.get('target', 'member_analytics.call_center')
    catalog_name = target.split('.')[0]  # Extract catalog name
    
    print(f"\n📊 Current Configuration:")
    print(f"   Target: {target}")
    print(f"   Catalog: {catalog_name}")
    print(f"   Serverless: {spec.get('serverless', False)}")
    
    # Build update payload for serverless mode
    # Serverless requires catalog to be specified separately
    update_payload = {
        "name": pipeline.get("name"),
        "target": target,
        "catalog": catalog_name,  # Explicitly specify catalog for serverless
        "libraries": spec.get("libraries", []),
        "continuous": spec.get("continuous", True),
        "development": spec.get("development", False),
        "photon": True,
        "serverless": True,  # Enable serverless - Unity Catalog auto-enabled
        # Remove clusters config when using serverless
    }
    
    print(f"\n📝 Updating to Serverless Mode:")
    print(f"   Serverless: True (Unity Catalog auto-enabled)")
    print(f"   Catalog: {catalog_name}")
    print(f"   Photon: True")
    print(f"   Target: {target}")
    
    # Update pipeline
    update_url = f'{workspace_url}/api/2.0/pipelines/{pipeline_id}'
    response = requests.put(update_url, headers=headers, json=update_payload)
    
    if response.status_code == 200:
        print(f"\n✅ Pipeline updated successfully!")
        updated_pipeline = response.json()
        updated_spec = updated_pipeline.get('spec', {})
        
        print(f"   Serverless: {updated_spec.get('serverless')}")
        print(f"   Catalog: {updated_spec.get('catalog')}")
        print(f"   Unity Catalog: Automatically enabled in serverless mode")
        
        print(f"\n📋 Next Steps:")
        print(f"   1. Restart the pipeline")
        print(f"   2. Monitor pipeline status")
        print(f"   3. Verify enriched_transcripts table is created")
        
        return True
    else:
        print(f"\n❌ Error updating pipeline: {response.status_code}")
        print(f"   Response: {response.text}")
        
        # Try alternative: Keep standard cluster but ensure UC is enabled
        print(f"\n🔄 Trying alternative: Standard cluster with explicit UC enablement...")
        return fix_with_standard_cluster(workspace_url, headers, pipeline_id, pipeline, spec)

def fix_with_standard_cluster(workspace_url, headers, pipeline_id, pipeline, spec):
    """Alternative: Fix with standard cluster and explicit UC enablement"""
    print("\n" + "="*80)
    print("Alternative: Standard Cluster with Unity Catalog")
    print("="*80)
    
    # Build cluster config with Unity Catalog explicitly enabled
    clusters = [{
        "node_type_id": "i3.xlarge",
        "num_workers": 0,
        "spark_conf": {
            "spark.databricks.cluster.profile": "singleNode",
            "spark.master": "local[*]"
        },
        "custom_tags": {
            "ResourceClass": "SingleNode"
        },
        "enable_unity_catalog": True
    }]
    
    update_payload = {
        "name": pipeline.get("name"),
        "target": spec.get("target"),
        "libraries": spec.get("libraries", []),
        "continuous": spec.get("continuous", True),
        "development": spec.get("development", False),
        "photon": True,
        "serverless": False,
        "clusters": clusters
    }
    
    print(f"\n📝 Updating with Standard Cluster:")
    print(f"   Serverless: False")
    print(f"   Unity Catalog: Explicitly enabled in cluster config")
    print(f"   Node Type: {clusters[0]['node_type_id']}")
    
    update_url = f'{workspace_url}/api/2.0/pipelines/{pipeline_id}'
    response = requests.put(update_url, headers=headers, json=update_payload)
    
    if response.status_code == 200:
        print(f"\n✅ Pipeline updated successfully!")
        return True
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

if __name__ == "__main__":
    success = fix_with_serverless()
    if success:
        print(f"\n🚀 Ready to restart pipeline!")
        print(f"   Run: python scripts/restart_pipeline.py")
    else:
        print(f"\n⚠️  Could not update pipeline automatically")
        print(f"   Please check the error messages above")
        print(f"   Or try updating via Databricks UI:")

