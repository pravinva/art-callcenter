#!/usr/bin/env python3
"""
Wait and Restart Pipeline
Waits for current update to finish, then restarts with updated notebook.

Run: python scripts/wait_and_restart_pipeline.py
"""
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks.sdk import WorkspaceClient
from config.config import get_workspace_client

def wait_and_restart():
    """Wait for pipeline update to finish, then restart"""
    w = get_workspace_client()
    pipeline_id = "4bc41e3f-072e-4e5a-80a9-dbb323f2994b"
    
    print("⏳ Waiting for current pipeline update to finish...")
    print("="*80)
    
    # Wait for current update to complete
    max_wait = 5 * 60  # 5 minutes
    for i in range(max_wait // 10):
        try:
            pipeline = w.pipelines.get(pipeline_id)
            if hasattr(pipeline, 'latest_updates') and pipeline.latest_updates:
                latest = pipeline.latest_updates[0]
                state = str(latest.state)
                
                if 'COMPLETED' in state or 'FAILED' in state or 'CANCELED' in state:
                    print(f"✅ Current update finished: {state}")
                    break
                elif i % 6 == 0:  # Print every minute
                    print(f"   Still running... ({i*10}s elapsed)")
            
            time.sleep(10)
        except Exception as e:
            print(f"   Error checking: {e}")
            time.sleep(10)
    
    # Now restart
    print(f"\n🚀 Starting new pipeline update with fixed notebook...")
    try:
        update = w.pipelines.start_update(pipeline_id)
        print(f"✅ Pipeline update started!")
        print(f"   Update ID: {update.update_id}")
        print(f"\n📊 Monitor: Workflows → Delta Live Tables → art-callcenter-enrichment")
        print(f"\n💡 The pipeline will now:")
        print(f"   1. Read from member_analytics.call_center.zerobus_transcripts")
        print(f"   2. Enrich with sentiment, intent, compliance")
        print(f"   3. Create enriched_transcripts table")
        
    except Exception as e:
        print(f"❌ Error starting update: {e}")
        print(f"\n💡 You may need to manually restart the pipeline:")
        print(f"   Workflows → Delta Live Tables → art-callcenter-enrichment → Start")

if __name__ == "__main__":
    wait_and_restart()

