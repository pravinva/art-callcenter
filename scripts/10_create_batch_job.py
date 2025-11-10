#!/usr/bin/env python3
"""
Create Scheduled Job for Gold Layer Batch Processing
Creates a Databricks job that runs the Gold layer DLT pipeline on a schedule

Run: python scripts/10_create_batch_job.py
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

def create_batch_job():
    """Create scheduled job for Gold layer batch processing"""
    print("🚀 Creating Scheduled Batch Job for Gold Layer")
    print("="*80)
    
    config = Config()
    workspace_url = config.host.rstrip('/')
    token = config.token
    
    # Job configuration
    job_name = "art-callcenter-gold-layer-batch"
    pipeline_name = "art-callcenter-gold-layer"
    
    print(f"\n📋 Job Configuration:")
    print(f"   Name: {job_name}")
    print(f"   Pipeline: {pipeline_name}")
    print(f"   Schedule: Hourly (can be changed)")
    
    # Find the pipeline ID
    w = get_workspace_client()
    pipelines = list(w.pipelines.list_pipelines())
    pipeline = next((p for p in pipelines if p.name == pipeline_name), None)
    
    if not pipeline:
        print(f"\n❌ Pipeline '{pipeline_name}' not found!")
        print("   Please run: python scripts/09_deploy_gold_layer_pipeline.py first")
        return None
    
    print(f"   Found pipeline ID: {pipeline.pipeline_id}")
    
    # Check if job already exists
    jobs = list(w.jobs.list())
    existing_job = next((j for j in jobs if j.settings.name == job_name), None)
    
    if existing_job:
        print(f"\n⚠️  Job '{job_name}' already exists (ID: {existing_job.job_id})")
        print(f"   Job URL: {workspace_url}/#job/{existing_job.job_id}")
        print("   Updating job configuration...")
        
        # Update existing job
        update_payload = {
            "job_id": existing_job.job_id,
            "new_settings": {
                "name": job_name,
                "tasks": [
                    {
                        "task_key": "run_gold_layer_pipeline",
                        "description": "Run Gold layer DLT pipeline to process completed calls",
                        "pipeline_task": {
                            "pipeline_id": pipeline.pipeline_id
                        }
                    }
                ],
                "schedule": {
                    "quartz_cron_expression": "0 0 * * * ?",  # Every hour at minute 0 (Quartz syntax)
                    "timezone_id": "Australia/Sydney",
                    "pause_status": "UNPAUSED"
                },
                "timeout_seconds": 3600,  # 1 hour timeout
                "max_concurrent_runs": 1
            }
        }
        
        update_url = f'{workspace_url}/api/2.1/jobs/update'
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.post(update_url, headers=headers, json=update_payload)
        
        if response.status_code == 200:
            print("✅ Job updated successfully!")
        else:
            print(f"⚠️  Could not update job: {response.status_code}")
            print(f"   Response: {response.text}")
        
        return existing_job.job_id
    
    # Create job with schedule via REST API
    create_payload = {
        "name": job_name,
        "tasks": [
            {
                "task_key": "run_gold_layer_pipeline",
                "description": "Run Gold layer DLT pipeline to process completed calls",
                "pipeline_task": {
                    "pipeline_id": pipeline.pipeline_id
                }
            }
        ],
        "schedule": {
            "quartz_cron_expression": "0 0 * * * ?",  # Every hour at minute 0 (Quartz syntax)
            "timezone_id": "Australia/Sydney",
            "pause_status": "UNPAUSED"
        },
        "timeout_seconds": 3600,  # 1 hour timeout
        "max_concurrent_runs": 1
    }
    
    try:
        print("\n📦 Creating job...")
        api_url = f'{workspace_url}/api/2.1/jobs/create'
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.post(api_url, headers=headers, json=create_payload)
        
        if response.status_code == 200:
            job = response.json()
            job_id = job.get('job_id')
            print(f"\n✅ Job created successfully!")
            print(f"   Job ID: {job_id}")
            print(f"   Job URL: {workspace_url}/#job/{job_id}")
            
            print("\n📝 Schedule Details:")
            print("   - Runs every hour")
            print("   - Timezone: Australia/Sydney")
            print("   - Processes completed calls from the last hour")
            print("   - Creates call summaries, agent performance metrics, and member history")
            
            print("\n💡 To change schedule:")
            print("   1. Go to Jobs UI")
            print("   2. Edit the job")
            print("   3. Update the cron expression")
            print("   Examples:")
            print("     - Daily at 2 AM: '0 2 * * ?'")
            print("     - Every 6 hours: '0 */6 * * ?'")
            print("     - Every 30 minutes: '0 */30 * * ?'")
            
            return job_id
        else:
            print(f"\n❌ Error creating job: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
        
    except Exception as e:
        print(f"\n❌ Error creating job: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    create_batch_job()

