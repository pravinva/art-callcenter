#!/usr/bin/env python3
"""
Create New DLT Pipeline: Serverless Mode with Unity Catalog
Since existing pipeline has storage location, we need to create a new one.

Run: python scripts/create_serverless_pipeline.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
import requests
import json

def create_serverless_pipeline():
    """Create new DLT pipeline in serverless mode with Unity Catalog"""
    print("🚀 Creating New DLT Pipeline: Serverless Mode with Unity Catalog")
    print("="*80)
    
    config = Config()
    workspace_url = config.host.rstrip('/')
    token = config.token
    
    pipeline_name = "art-callcenter-enrichment-serverless"
    notebook_path = '/Workspace/Users/pravin.varma@databricks.com/art-callcenter/dlt_enrichment_pipeline'
    
    # Create new pipeline payload for serverless with Unity Catalog
    create_payload = {
        "name": pipeline_name,
        "catalog": "member_analytics",  # Catalog name (required for serverless + UC)
        "target": "call_center",  # Schema only (not full three-part name)
        "libraries": [
            {
                "notebook": {
                    "path": notebook_path
                }
            }
        ],
        "continuous": True,
        "development": False,
        "photon": True,
        "serverless": True  # Enable serverless - Unity Catalog auto-enabled
    }
    
    print(f"\n📝 Creating Pipeline:")
    print(f"   Name: {pipeline_name}")
    print(f"   Serverless: True (Unity Catalog auto-enabled)")
    print(f"   Catalog: member_analytics")
    print(f"   Target: call_center (schema only)")
    print(f"   Notebook: {notebook_path}")
    
    # Create pipeline
    api_url = f'{workspace_url}/api/2.0/pipelines'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(api_url, headers=headers, json=create_payload)
    
    if response.status_code == 200:
        new_pipeline = response.json()
        pipeline_id = new_pipeline.get('pipeline_id')
        
        print(f"\n✅ Pipeline created successfully!")
        print(f"   Pipeline ID: {pipeline_id}")
        print(f"   Pipeline Name: {pipeline_name}")
        
        print(f"\n📋 Next Steps:")
        print(f"   1. Start the pipeline")
        print(f"   2. Monitor pipeline status")
        print(f"   3. Verify enriched_transcripts table is created")
        print(f"\n   To start: python scripts/start_pipeline.py {pipeline_id}")
        
        return pipeline_id
    else:
        print(f"\n❌ Error creating pipeline: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 400 and "already exists" in response.text.lower():
            print(f"\n⚠️  Pipeline with this name may already exist")
            print(f"   Use a different name or delete the existing one")
        
        return None

if __name__ == "__main__":
    pipeline_id = create_serverless_pipeline()
    if pipeline_id:
        print(f"\n✅ New serverless pipeline created: {pipeline_id}")
        print(f"\n💡 Note: You can delete the old pipeline if needed:")
        print(f"   Old pipeline ID: 4bc41e3f-072e-4e5a-80a9-dbb323f2994b")
    else:
        print(f"\n⚠️  Could not create pipeline automatically")
        print(f"\n💡 Alternative: Update existing pipeline via UI with this JSON:")
        print(json.dumps({
            "catalog": "member_analytics",
            "target": "call_center",
            "serverless": True,
            "photon": True,
            "continuous": True
        }, indent=2))

