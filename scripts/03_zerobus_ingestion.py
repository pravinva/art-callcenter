#!/usr/bin/env python3
"""
Phase 1.3: Zerobus Ingestion
Stream call transcripts to Delta table via Zerobus SDK.

Run: python scripts/03_zerobus_ingestion.py
"""
import sys
import asyncio
import random
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from zerobus.sdk.aio import ZerobusSdk
    from zerobus.sdk import TableProperties
    ZEROBUS_AVAILABLE = True
except ImportError:
    try:
        from zerobus.sdk import ZerobusSdk, TableProperties
        ZEROBUS_AVAILABLE = True
    except ImportError:
        print("⚠️  Zerobus SDK not found. Install with: pip install git+https://github.com/databricks/zerobus-sdk-py.git")
        print("   Use SQL fallback: python scripts/03_zerobus_ingestion_sql.py")
        ZEROBUS_AVAILABLE = False
        ZerobusSdk = None
        TableProperties = None
from databricks.sdk import WorkspaceClient
from config.config import (
    get_workspace_client, get_zerobus_endpoint, get_workspace_url,
    CATALOG_NAME, SCHEMA_NAME, TABLE_NAME, ZEROBUS_TABLE,
    get_zerobus_credentials
)

# Import mock data generator
from scripts.mock_data_generator import generate_member_pool, generate_realistic_call

async def get_secrets(w: WorkspaceClient):
    """Get secrets from environment variables"""
    client_id, client_secret = get_zerobus_credentials()
    
    if not client_id or not client_secret:
        from config.config import SECRETS_SCOPE, CLIENT_ID_SECRET, CLIENT_SECRET_KEY, ZEROBUS_CLIENT_ID_ENV, ZEROBUS_CLIENT_SECRET_ENV
        print("⚠️  Zerobus credentials not found in environment variables")
        print(f"   Set {ZEROBUS_CLIENT_ID_ENV} and {ZEROBUS_CLIENT_SECRET_ENV}")
        print(f"   Or retrieve from secrets scope: {SECRETS_SCOPE}")
        print(f"\n   To get secrets, run in Databricks notebook:")
        print(f"   client_id = dbutils.secrets.get('{SECRETS_SCOPE}', '{CLIENT_ID_SECRET}')")
        print(f"   client_secret = dbutils.secrets.get('{SECRETS_SCOPE}', '{CLIENT_SECRET_KEY}')")
        return None, None
    
    return client_id, client_secret

async def ingest_call_zerobus(call_data, sdk, stream):
    """Ingest realistic call via Zerobus"""
    
    call_id = f"CALL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(10000, 99999)}"
    start_time = datetime.now()
    
    print(f"\n{'='*80}")
    print(f"📞 Call #{call_id}")
    print(f"Member: {call_data['member']['name']} ({call_data['member']['member_id']})")
    print(f"Scenario: {call_data['scenario_type']} ({call_data['complexity']})")
    print(f"Balance: ${call_data['member']['balance']:,.0f}")
    print(f"{'='*80}\n")
    
    try:
        for idx, (speaker, utterance) in enumerate(call_data["dialogue"]):
            timestamp = start_time + timedelta(seconds=idx * 5)
            
            record = {
                "call_id": call_id,
                "member_id": call_data["member"]["member_id"],
                "member_name": call_data["member"]["name"],
                "agent_id": f"AGENT-{random.randint(100, 999)}",
                "timestamp": timestamp.isoformat(),
                "transcript_segment": utterance,
                "speaker": speaker,
                "confidence": round(random.uniform(0.90, 0.99), 3),
                "queue": "member_services",
                "scenario": call_data["scenario_type"],
                "complexity": call_data["complexity"],
                "channel": "voice",
                "member_balance": float(call_data["member"]["balance"]),
                "member_life_stage": call_data["member"]["life_stage"]
            }
            
            # Convert record to JSON string for JSON mode
            import json
            record_json = json.dumps(record)
            
            # Ingest record (async API - returns awaitable)
            await stream.ingest_record(record_json)
            
            print(f"⚡ [{speaker:8s}] {utterance[:70]}")
            await asyncio.sleep(0.5)  # Faster for demo
        
        await stream.flush()
        
    except Exception as e:
        print(f"❌ Error ingesting call: {e}")
        raise
    
    print(f"\n{'='*80}")
    print(f"✅ Call Complete")
    print(f"{'='*80}\n")
    
    return call_id

async def simulate_call_center(num_calls=10, member_pool=None):
    """Simulate realistic call center volume"""
    
    if not ZEROBUS_AVAILABLE:
        print("❌ Zerobus SDK not available. Use SQL fallback:")
        print("   python scripts/03_zerobus_ingestion_sql.py")
        return
    
    print(f"\n🏢 CALL CENTER SIMULATION")
    print(f"Generating {num_calls} realistic calls...")
    print(f"{'='*80}\n")
    
    # Get Zerobus credentials
    w = get_workspace_client()
    client_id, client_secret = await get_secrets(w)
    
    if not client_id or not client_secret:
        print("❌ Cannot proceed without Zerobus credentials")
        print("   Set environment variables:")
        print("   export ZEROBUS_CLIENT_ID='your-client-id'")
        print("   export ZEROBUS_CLIENT_SECRET='your-client-secret'")
        return
    
    # Initialize Zerobus SDK
    workspace_url = get_workspace_url().rstrip('/')
    workspace_hostname = workspace_url.replace('https://', '').replace('http://', '')
    
    # Based on SDK docs: ZerobusSdk(server_endpoint, unity_catalog_endpoint)
    server_endpoint = f"https://{workspace_hostname}/api/2.0/zerobus/streams"
    unity_catalog_endpoint = f"https://{workspace_hostname}/api/2.0/unity-catalog"
    
    print(f"🔌 Connecting to Zerobus...")
    print(f"   Workspace: {workspace_url}")
    print(f"   Server Endpoint: {server_endpoint}")
    print(f"   UC Endpoint: {unity_catalog_endpoint}")
    
    sdk = ZerobusSdk(server_endpoint, unity_catalog_endpoint)
    
    table_props = TableProperties(table_name=ZEROBUS_TABLE)
    
    print(f"📊 Target table: {table_props.table_name}")
    
    # Create stream using async API
    stream = await sdk.create_stream(
        client_id=client_id,
        client_secret=client_secret,
        table_properties=table_props
    )
    
    print("✅ Stream created\n")
    
    call_ids = []
    
    try:
        for i in range(num_calls):
            print(f"\n📱 Incoming Call {i+1}/{num_calls} - {datetime.now().strftime('%H:%M:%S')}")
            
            call_data = generate_realistic_call(member_pool)
            call_id = await ingest_call_zerobus(call_data, sdk, stream)
            call_ids.append(call_id)
            
            if i < num_calls - 1:
                wait = random.randint(2, 5)  # Faster for demo
                print(f"\n⏳ Next call in {wait} seconds...\n")
                await asyncio.sleep(wait)
        
        await stream.close()
        print(f"\n✅ Successfully ingested {len(call_ids)} calls")
        print(f"   Check table: {table_props.table_name}")
        
    except Exception as e:
        print(f"\n❌ Error during simulation: {e}")
        await stream.close()
        raise

def main():
    print("🚀 Phase 1.3: Zerobus Ingestion")
    print("="*80)
    
    # Generate member pool
    print("\n📊 Generating member pool...")
    member_pool = generate_member_pool(50)
    print(f"✅ Generated {len(member_pool)} members")
    
    # Run simulation
    try:
        num_calls = int(sys.argv[1]) if len(sys.argv) > 1 else 10
        print(f"\n🎯 Ingesting {num_calls} calls...")
        
        asyncio.run(simulate_call_center(num_calls, member_pool))
        
        print("\n✅ Phase 1 Complete!")
        print("   Next: Phase 2 - DLT Pipeline for enrichment")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

