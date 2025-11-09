#!/usr/bin/env python3
"""
Check DLT Pipeline Status
Check if pipeline is running and if enriched table exists.

Run: python scripts/check_pipeline_status.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks.sdk import WorkspaceClient
from config.config import get_workspace_client

def check_pipeline_status():
    """Check DLT pipeline status"""
    print("🔍 Checking DLT Pipeline Status")
    print("="*80)
    
    w = get_workspace_client()
    pipeline_name = "art-callcenter-enrichment"
    
    try:
        pipelines = list(w.pipelines.list_pipelines())
        matching = [p for p in pipelines if p.name == pipeline_name]
        
        if matching:
            pipeline = matching[0]
            print(f"✅ Pipeline found: {pipeline.pipeline_id}")
            print(f"   Name: {pipeline.name}")
            print(f"   State: {getattr(pipeline, 'state', 'Unknown')}")
            
            # Get pipeline details
            try:
                details = w.pipelines.get(pipeline.pipeline_id)
                print(f"   Target: {details.target}")
                print(f"   Continuous: {details.continuous}")
                
                # Check latest update
                if hasattr(details, 'latest_updates') and details.latest_updates:
                    latest = details.latest_updates[0]
                    print(f"   Latest Update State: {latest.state}")
                    print(f"   Latest Update ID: {latest.update_id}")
                
            except Exception as e:
                print(f"   Could not get details: {e}")
            
            return pipeline.pipeline_id
        else:
            print(f"❌ Pipeline '{pipeline_name}' not found")
            return None
            
    except Exception as e:
        print(f"❌ Error checking pipeline: {e}")
        return None

if __name__ == "__main__":
    check_pipeline_status()

