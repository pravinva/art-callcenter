#!/usr/bin/env python3
"""
Deploy Gold Layer DLT Pipeline (Serverless)
Creates a serverless DLT pipeline for batch post-call processing (call summaries, agent performance, etc.)

Run: python scripts/09_deploy_gold_layer_pipeline.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
import requests
import json
from config.config import get_workspace_client

def deploy_gold_layer_pipeline():
    """Deploy Gold Layer DLT Pipeline for batch post-call processing (serverless)"""
    print("🚀 Deploying Gold Layer DLT Pipeline (Serverless)")
    print("="*80)
    
    config = Config()
    workspace_url = config.host.rstrip('/')
    token = config.token
    
    # Pipeline configuration
    pipeline_name = "art-callcenter-gold-layer"
    notebook_path = "/Workspace/Users/pravin.varma@databricks.com/art-callcenter/dlt_gold_layer_pipeline"
    
    print(f"\n📋 Pipeline Configuration:")
    print(f"   Name: {pipeline_name}")
    print(f"   Notebook: {notebook_path}")
    print(f"   Catalog: member_analytics")
    print(f"   Target: call_center")
    print(f"   Mode: Serverless (batch)")
    
    # Check if pipeline already exists
    w = get_workspace_client()
    existing_pipelines = list(w.pipelines.list_pipelines())
    existing_pipeline = next((p for p in existing_pipelines if p.name == pipeline_name), None)
    
    if existing_pipeline:
        print(f"\n⚠️  Pipeline '{pipeline_name}' already exists (ID: {existing_pipeline.pipeline_id})")
        print(f"   Pipeline URL: {workspace_url}/#joblist/pipelines/{existing_pipeline.pipeline_id}")
        print("   Updating pipeline configuration...")
        pipeline_id = existing_pipeline.pipeline_id
        
        # Update existing pipeline via REST API
        update_payload = {
            "name": pipeline_name,
            "catalog": "member_analytics",
            "target": "call_center",
            "libraries": [
                {
                    "notebook": {
                        "path": notebook_path
                    }
                }
            ],
            "continuous": False,  # Batch mode
            "development": False,
            "photon": True,
            "serverless": True,
            "configuration": {
                "pipelines.enableTrackHistory": "true"
            }
        }
        
        update_url = f'{workspace_url}/api/2.0/pipelines/{pipeline_id}'
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.put(update_url, headers=headers, json=update_payload)
        
        if response.status_code == 200:
            print("✅ Pipeline updated successfully!")
        else:
            print(f"⚠️  Could not update pipeline: {response.status_code}")
            print(f"   Response: {response.text}")
        
        return pipeline_id
    
    # Create pipeline configuration (serverless, like Silver layer)
    create_payload = {
        "name": pipeline_name,
        "catalog": "member_analytics",
        "target": "call_center",
        "libraries": [
            {
                "notebook": {
                    "path": notebook_path
                }
            }
        ],
        "continuous": False,  # Batch mode (not continuous streaming)
        "development": False,
        "photon": True,
        "serverless": True,  # Use serverless compute (like Silver layer)
        "configuration": {
            "pipelines.enableTrackHistory": "true"
        }
    }
    
    try:
        print("\n📦 Creating pipeline...")
        api_url = f'{workspace_url}/api/2.0/pipelines'
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.post(api_url, headers=headers, json=create_payload)
        
        if response.status_code == 200:
            pipeline = response.json()
            pipeline_id = pipeline.get('pipeline_id')
            print(f"\n✅ Pipeline created successfully!")
            print(f"   Pipeline ID: {pipeline_id}")
            print(f"   Pipeline URL: {workspace_url}/#joblist/pipelines/{pipeline_id}")
            
            print("\n📝 Pipeline Details:")
            print("   - Mode: Serverless (batch)")
            print("   - Catalog: member_analytics")
            print("   - Target: call_center")
            print("   - Creates 4 Gold layer tables:")
            print("     • call_summaries")
            print("     • agent_performance")
            print("     • member_interaction_history")
            print("     • daily_call_statistics")
            
            return pipeline_id
        else:
            print(f"\n❌ Error creating pipeline: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
        
    except Exception as e:
        print(f"\n❌ Error creating pipeline: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    deploy_gold_layer_pipeline()

