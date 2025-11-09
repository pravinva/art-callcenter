#!/usr/bin/env python3
"""
Step-by-Step Troubleshooting: DLT Pipeline Unity Catalog Issue
Systematically checks each possible cause of the Unity Catalog error.

Run: python scripts/troubleshoot_pipeline_uc.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
import requests
import json

def troubleshoot_step_by_step():
    """Troubleshoot Unity Catalog issue step by step"""
    print("🔍 Step-by-Step Troubleshooting: DLT Pipeline Unity Catalog")
    print("="*80)
    
    config = Config()
    workspace_url = config.host.rstrip('/')
    token = config.token
    pipeline_id = '4bc41e3f-072e-4e5a-80a9-dbb323f2994b'
    
    headers = {'Authorization': f'Bearer {token}'}
    api_url = f'{workspace_url}/api/2.0/pipelines/{pipeline_id}'
    
    # Step 1: Check pipeline configuration
    print("\n" + "="*80)
    print("STEP 1: Check Current Pipeline Configuration")
    print("="*80)
    
    response = requests.get(api_url, headers=headers)
    pipeline = response.json()
    spec = pipeline.get('spec', {})
    
    print(f"\n✅ Pipeline Name: {pipeline.get('name')}")
    print(f"✅ Pipeline ID: {pipeline_id}")
    print(f"✅ Target: {spec.get('target')}")
    print(f"✅ Continuous: {spec.get('continuous')}")
    print(f"✅ Serverless: {spec.get('serverless')}")
    print(f"✅ Photon: {spec.get('photon')}")
    
    # Step 2: Check cluster configuration
    print("\n" + "="*80)
    print("STEP 2: Check Cluster Configuration")
    print("="*80)
    
    clusters = spec.get('clusters', [])
    if clusters:
        cluster = clusters[0]
        print(f"\n📋 Cluster Config:")
        print(json.dumps(cluster, indent=2))
        
        uc_enabled = cluster.get('enable_unity_catalog', False)
        print(f"\n🔍 Unity Catalog Enabled: {uc_enabled}")
        
        if not uc_enabled:
            print("❌ ISSUE FOUND: Unity Catalog is NOT enabled in cluster config")
        else:
            print("✅ Unity Catalog is enabled in config (but may not be applied)")
    else:
        print("⚠️  No cluster configuration found")
        print("   Pipeline may be using default settings")
    
    # Step 3: Check if target catalog exists
    print("\n" + "="*80)
    print("STEP 3: Verify Target Catalog Exists")
    print("="*80)
    
    target = spec.get('target', '')
    if target:
        catalog_name = target.split('.')[0]
        print(f"\n📋 Target: {target}")
        print(f"📋 Catalog: {catalog_name}")
        
        # Check if catalog exists
        catalog_api = f'{workspace_url}/api/2.0/unity-catalog/catalogs/{catalog_name}'
        catalog_response = requests.get(catalog_api, headers=headers)
        
        if catalog_response.status_code == 200:
            print(f"✅ Catalog '{catalog_name}' exists")
        else:
            print(f"❌ ISSUE FOUND: Catalog '{catalog_name}' does not exist or is not accessible")
            print(f"   Status: {catalog_response.status_code}")
            print(f"   Response: {catalog_response.text}")
    else:
        print("❌ ISSUE FOUND: No target specified")
    
    # Step 4: Check source table exists
    print("\n" + "="*80)
    print("STEP 4: Verify Source Table Exists")
    print("="*80)
    
    source_table = "member_analytics.call_center.zerobus_transcripts"
    print(f"\n📋 Source Table: {source_table}")
    
    # Try to query the table
    from databricks import sql
    import os
    
    try:
        connection = sql.connect(
            server_hostname=workspace_url.replace('https://', ''),
            http_path=f'/sql/1.0/warehouses/4b9b953939869799',
            access_token=os.environ.get('DATABRICKS_TOKEN')
        )
        cursor = connection.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {source_table} LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        
        print(f"✅ Source table exists and is accessible")
        print(f"   Row count: {result[0]}")
    except Exception as e:
        print(f"❌ ISSUE FOUND: Cannot access source table")
        print(f"   Error: {e}")
    
    # Step 5: Check latest pipeline update error
    print("\n" + "="*80)
    print("STEP 5: Check Latest Pipeline Update Error")
    print("="*80)
    
    if pipeline.get('latest_updates'):
        latest = pipeline['latest_updates'][0]
        update_id = latest.get('update_id')
        state = latest.get('state')
        
        print(f"\n📋 Latest Update:")
        print(f"   Update ID: {update_id}")
        print(f"   State: {state}")
        
        # Get detailed update info
        update_url = f'{workspace_url}/api/2.0/pipelines/{pipeline_id}/updates/{update_id}'
        update_response = requests.get(update_url, headers=headers)
        
        if update_response.status_code == 200:
            update_details = update_response.json()
            update_info = update_details.get('update', {})
            
            if update_info.get('error'):
                error = update_info['error']
                print(f"\n❌ Error Details:")
                if isinstance(error, dict):
                    print(f"   Type: {error.get('type')}")
                    print(f"   Message: {error.get('message')}")
                else:
                    print(f"   Error: {error}")
    
    # Step 6: Recommendations
    print("\n" + "="*80)
    print("STEP 6: Recommended Solutions")
    print("="*80)
    
    print("\n💡 Solution Options:")
    print("\nOption 1: Use Serverless Mode (Recommended)")
    print("   - Serverless automatically enables Unity Catalog")
    print("   - Requires catalog specification in target")
    print("   - Run: python scripts/fix_pipeline_serverless.py")
    
    print("\nOption 2: Explicitly Enable Unity Catalog in Cluster Config")
    print("   - Add enable_unity_catalog: True to cluster config")
    print("   - May require removing spark_version")
    print("   - Run: python scripts/fix_pipeline_unity_catalog.py")
    
    print("\nOption 3: Check Workspace Unity Catalog Settings")
    print("   - Verify workspace has Unity Catalog enabled")
    print("   - Check metastore assignment")
    print("   - Verify user permissions")
    
    print("\nOption 4: Use Standard Cluster with UC Runtime")
    print("   - Use Databricks Runtime with Unity Catalog support")
    print("   - Ensure cluster policy allows Unity Catalog")
    
    return {
        'serverless': spec.get('serverless', False),
        'clusters': clusters,
        'target': spec.get('target'),
        'has_uc_in_cluster': clusters[0].get('enable_unity_catalog', False) if clusters else False
    }

if __name__ == "__main__":
    result = troubleshoot_step_by_step()
    
    print("\n" + "="*80)
    print("TROUBLESHOOTING SUMMARY")
    print("="*80)
    print(f"\nCurrent State:")
    print(f"  Serverless: {result['serverless']}")
    print(f"  Has Cluster Config: {len(result['clusters']) > 0}")
    print(f"  UC in Cluster Config: {result['has_uc_in_cluster']}")
    print(f"  Target: {result['target']}")

