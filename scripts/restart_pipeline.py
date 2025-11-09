#!/usr/bin/env python3
"""
Restart DLT Pipeline Update
Restarts the pipeline to process data.

Run: python scripts/restart_pipeline.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks.sdk import WorkspaceClient
from config.config import get_workspace_client

def restart_pipeline():
    """Restart DLT pipeline"""
    w = get_workspace_client()
    pipeline_id = "4bc41e3f-072e-4e5a-80a9-dbb323f2994b"
    
    print("🔄 Restarting DLT Pipeline")
    print("="*80)
    
    try:
        # Stop any running updates
        print(f"⏹️  Checking for active updates...")
        try:
            pipeline = w.pipelines.get(pipeline_id)
            if hasattr(pipeline, 'latest_updates') and pipeline.latest_updates:
                latest = pipeline.latest_updates[0]
                if latest.state.value not in ['COMPLETED', 'CANCELED', 'FAILED']:
                    print(f"   Stopping active update: {latest.update_id}")
                    w.pipelines.stop(pipeline_id)
                    import time
                    time.sleep(5)
                    print(f"✅ Update stopped")
        except Exception as e:
            print(f"   (No active update to stop)")
        
        # Start new update
        print(f"\n🚀 Starting new pipeline update...")
        update = w.pipelines.start_update(pipeline_id)
        print(f"✅ Pipeline update started!")
        print(f"   Update ID: {update.update_id}")
        print(f"\n⏳ Pipeline will process data and create enriched_transcripts table")
        print(f"   Monitor: Workflows → Delta Live Tables → art-callcenter-enrichment")
        print(f"\n💡 Waiting 2 minutes for initial processing...")
        import time
        time.sleep(120)
        
        return update.update_id
        
    except Exception as e:
        print(f"❌ Error restarting pipeline: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    restart_pipeline()

