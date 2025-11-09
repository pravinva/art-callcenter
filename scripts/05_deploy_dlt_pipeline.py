#!/usr/bin/env python3
"""
Deploy DLT Pipeline Job
Creates and deploys the DLT pipeline as a continuous job.

Run: python scripts/05_deploy_dlt_pipeline.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks.sdk import WorkspaceClient
from config.config import get_workspace_client

def deploy_dlt_pipeline():
    """Deploy DLT pipeline as a continuous job"""
    print("🚀 Deploying DLT Pipeline Job")
    print("="*80)
    
    w = get_workspace_client()
    
    # Pipeline configuration
    pipeline_name = "art-callcenter-enrichment"
    notebook_path = "/Workspace/Users/pravin.varma@databricks.com/art-callcenter/dlt_enrichment_pipeline"
    
    print(f"\n📋 Pipeline Configuration:")
    print(f"   Name: {pipeline_name}")
    print(f"   Notebook: {notebook_path}")
    
    try:
        # Check if pipeline already exists
        print(f"\n🔍 Checking for existing pipeline...")
        pipelines = list(w.pipelines.list_pipelines())
        existing = [p for p in pipelines if p.name == pipeline_name]
        
        if existing:
            pipeline_id = existing[0].pipeline_id
            print(f"✅ Pipeline exists: {pipeline_id}")
            print(f"\n📝 To update pipeline:")
            print(f"   1. Update notebook: {notebook_path}")
            print(f"   2. Pipeline will auto-refresh or restart manually")
            return pipeline_id
        else:
            print(f"   No existing pipeline found")
            print(f"\n📝 Creating DLT pipeline...")
            print(f"\n⚠️  Note: DLT pipelines must be created via Databricks UI or REST API")
            print(f"\n💡 To create the pipeline:")
            print(f"\n   Option 1: Via Databricks UI")
            print(f"   1. Go to: Workflows → Delta Live Tables → Create Pipeline")
            print(f"   2. Pipeline name: {pipeline_name}")
            print(f"   3. Notebook path: {notebook_path}")
            print(f"   4. Target: member_analytics.call_center")
            print(f"   5. Storage location: (auto-generated)")
            print(f"   6. Cluster mode: Standard or Serverless")
            print(f"   7. Enable: 'Continuous' for real-time processing")
            print(f"   8. Click 'Create'")
            
            print(f"\n   Option 2: Via REST API (programmatic)")
            print(f"   Use Databricks SDK to create pipeline:")
            print(f"   w.pipelines.create(...)")
            
            print(f"\n   Option 3: Via Terraform/Databricks Asset Bundles")
            print(f"   Define pipeline in databricks_pipeline resource")
            
            return None
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_pipeline_via_api():
    """Create DLT pipeline via REST API"""
    w = get_workspace_client()
    
    notebook_path = "/Workspace/Users/pravin.varma@databricks.com/art-callcenter/dlt_enrichment_pipeline"
    pipeline_name = "art-callcenter-enrichment"
    
    try:
        print(f"\n📝 Creating DLT pipeline via API...")
        print(f"   Name: {pipeline_name}")
        print(f"   Notebook: {notebook_path}")
        
        # Create pipeline - use correct API structure
        from databricks.sdk.service.pipelines import CreatePipeline
        
        pipeline = w.pipelines.create(
            CreatePipeline(
                name=pipeline_name,
                target="member_analytics.call_center",
                libraries=[],  # DLT runtime is included automatically
                continuous=True,  # Continuous mode for real-time
                development=False,  # Production mode
                photon=True,  # Use Photon for better performance
                serverless=False,  # Use standard clusters
            ).with_notebooks([notebook_path])
        )
        
        print(f"✅ Pipeline created successfully!")
        print(f"   Pipeline ID: {pipeline.pipeline_id}")
        print(f"   Pipeline URL: {pipeline.catalog_name}")
        
        return pipeline.pipeline_id
        
    except Exception as e:
        print(f"⚠️  API creation error: {e}")
        print(f"\n   This might require additional permissions")
        print(f"   Fallback: Use UI method (see instructions)")
        return None

def main():
    print("\n" + "="*80)
    print("DLT PIPELINE DEPLOYMENT")
    print("="*80)
    
    w = get_workspace_client()
    pipeline_name = "art-callcenter-enrichment"
    
    # Try to deploy
    pipeline_id = deploy_dlt_pipeline()
    
    # Try API creation if UI method needed
    if not pipeline_id:
        print(f"\n🔄 Attempting API creation...")
        pipeline_id = create_pipeline_via_api()
    
    if pipeline_id:
        print(f"\n✅ Pipeline ID: {pipeline_id}")
        print(f"\n📊 Monitor pipeline:")
        print(f"   Workflows → Delta Live Tables → {pipeline_name}")
        print(f"\n🔄 Pipeline will run continuously and process:")
        print(f"   - New transcripts from Zerobus")
        print(f"   - Enrichment with sentiment, intent, compliance")
        print(f"   - Updates to enriched_transcripts table")
        
        # Start the pipeline
        print(f"\n🚀 Starting pipeline...")
        try:
            w.pipelines.start_update(pipeline_id)
            print(f"✅ Pipeline started!")
        except Exception as e:
            print(f"⚠️  Could not start pipeline automatically: {e}")
            print(f"   Start manually via UI: Workflows → Delta Live Tables")
    else:
        print(f"\n📝 Follow the instructions above to create the pipeline")
        print(f"\n💡 After creation, the pipeline will:")
        print(f"   1. Run continuously")
        print(f"   2. Process streaming data from Zerobus")
        print(f"   3. Enrich transcripts automatically")
        print(f"   4. Update enriched_transcripts table in real-time")

if __name__ == "__main__":
    main()

