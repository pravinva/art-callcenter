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

async def ingest_call_zerobus(call_data, sdk, stream, agent_id=None, realtime_delay=True):
    """Ingest realistic call via Zerobus with Genesys Cloud-like patterns"""
    
    call_id = f"CALL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(10000, 99999)}"
    start_time = datetime.now()
    agent_id = agent_id or f"AGENT-{random.randint(100, 999)}"
    
    # Variable utterance timing (realistic speech patterns)
    # Short utterances: 1-2s, Medium: 2-4s, Long: 4-8s
    utterance_delays = {
        'short': (1.0, 2.0),
        'medium': (2.0, 4.0),
        'long': (4.0, 8.0)
    }
    
    # Determine if this is a short or long call (realistic distribution)
    # 60% short calls (< 2 min), 30% medium (2-5 min), 10% long (> 5 min)
    call_length_type = random.choices(
        ['short', 'medium', 'long'],
        weights=[60, 30, 10]
    )[0]
    
    # Trim dialogue for short calls, extend for long calls
    dialogue = call_data["dialogue"]
    if call_length_type == 'short' and len(dialogue) > 8:
        dialogue = dialogue[:random.randint(4, 8)]
    elif call_length_type == 'long' and len(dialogue) < 20:
        # Repeat some dialogue patterns for longer calls
        dialogue = dialogue * 2 + dialogue[:random.randint(5, 10)]
    
    try:
        batch_records = []
        batch_size = 5  # Batch records for better throughput
        
        for idx, (speaker, utterance) in enumerate(dialogue):
            # Realistic timestamp progression (not fixed intervals)
            if idx == 0:
                timestamp = start_time
            else:
                # Variable delays based on utterance length
                utterance_length = len(utterance.split())
                if utterance_length < 5:
                    delay_range = utterance_delays['short']
                elif utterance_length < 15:
                    delay_range = utterance_delays['medium']
                else:
                    delay_range = utterance_delays['long']
                
                delay = random.uniform(*delay_range)
                timestamp = start_time + timedelta(seconds=sum([
                    random.uniform(*utterance_delays['short']) 
                    for _ in range(idx)
                ]) + delay)
            
            record = {
                "call_id": call_id,
                "member_id": call_data["member"]["member_id"],
                "member_name": call_data["member"]["name"],
                "agent_id": agent_id,
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
            
            import json
            record_json = json.dumps(record)
            batch_records.append(record_json)
            
            # Batch ingest for better throughput
            if len(batch_records) >= batch_size:
                await asyncio.gather(*[stream.ingest_record(r) for r in batch_records])
                batch_records = []
            
            # Real-time delay only if enabled (for realistic streaming)
            if realtime_delay:
                # Faster delays for high throughput (0.05-0.2s instead of 0.5s)
                await asyncio.sleep(random.uniform(0.05, 0.2))
        
        # Ingest remaining records
        if batch_records:
            await asyncio.gather(*[stream.ingest_record(r) for r in batch_records])
        
        await stream.flush()
        
    except Exception as e:
        print(f"❌ Error ingesting call {call_id}: {e}")
        raise
    
    return call_id

async def simulate_call_center(num_calls=10, member_pool=None, throughput=None, continuous=False, max_duration_minutes=None):
    """
    Simulate realistic Genesys Cloud call center volume with high throughput
    
    Args:
        num_calls: Number of calls to generate (ignored if continuous=True)
        member_pool: Pool of members to use
        throughput: Calls per minute (default: variable based on time of day)
        continuous: Run indefinitely (until interrupted)
        max_duration_minutes: Maximum duration for continuous mode
    """
    
    if not ZEROBUS_AVAILABLE:
        print("❌ Zerobus SDK not available. Use SQL fallback:")
        print("   python scripts/03_zerobus_ingestion_sql.py")
        return
    
    print(f"\n🏢 GENESYS CLOUD CALL CENTER SIMULATION")
    if continuous:
        print(f"🔄 Continuous mode: Generating calls until interrupted")
        if max_duration_minutes:
            print(f"⏱️  Max duration: {max_duration_minutes} minutes")
    else:
        print(f"📞 Generating {num_calls} realistic calls...")
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
    
    server_endpoint = f"https://{workspace_hostname}/api/2.0/zerobus/streams"
    unity_catalog_endpoint = f"https://{workspace_hostname}/api/2.0/unity-catalog"
    
    print(f"🔌 Connecting to Zerobus...")
    print(f"   Workspace: {workspace_url}")
    print(f"   Target table: {ZEROBUS_TABLE}")
    
    sdk = ZerobusSdk(server_endpoint, unity_catalog_endpoint)
    table_props = TableProperties(table_name=ZEROBUS_TABLE)
    
    # Create stream using async API
    stream = await sdk.create_stream(
        client_id=client_id,
        client_secret=client_secret,
        table_properties=table_props
    )
    
    print("✅ Stream created\n")
    
    # Generate agent pool (realistic: multiple agents handling calls)
    num_agents = random.randint(5, 15)
    agent_pool = [f"AGENT-{random.randint(100, 999)}" for _ in range(num_agents)]
    print(f"👥 Agent pool: {len(agent_pool)} agents available\n")
    
    call_ids = []
    start_time = datetime.now()
    call_count = 0
    
    def get_throughput():
        """Calculate realistic throughput based on time of day (peak hours)"""
        if throughput:
            return throughput
        
        hour = datetime.now().hour
        # Peak hours: 9-11 AM, 1-3 PM (higher volume)
        if 9 <= hour <= 11 or 13 <= hour <= 15:
            return random.uniform(20, 40)  # 20-40 calls/min during peak
        elif 8 <= hour <= 17:
            return random.uniform(10, 25)  # 10-25 calls/min during business hours
        else:
            return random.uniform(2, 8)    # 2-8 calls/min off-hours
    
    async def start_call(call_num):
        """Start a single call (can run concurrently)"""
        agent_id = random.choice(agent_pool)
        call_data = generate_realistic_call(member_pool)
        
        # High throughput: minimal delay between calls
        call_id = await ingest_call_zerobus(
            call_data, sdk, stream, 
            agent_id=agent_id,
            realtime_delay=True  # Real-time streaming
        )
        return call_id
    
    try:
        if continuous:
            # Continuous mode: generate calls at realistic throughput
            end_time = start_time + timedelta(minutes=max_duration_minutes) if max_duration_minutes else None
            
            while True:
                if end_time and datetime.now() >= end_time:
                    print(f"\n⏱️  Max duration reached. Stopping...")
                    break
                
                # Calculate calls to start based on throughput
                calls_per_min = get_throughput()
                calls_to_start = max(1, int(calls_per_min / 60))  # Calls per second
                
                # Start multiple calls concurrently (realistic: multiple calls at once)
                concurrent_calls = min(calls_to_start, 10)  # Max 10 concurrent
                
                tasks = [start_call(call_count + i) for i in range(concurrent_calls)]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, Exception):
                        print(f"⚠️  Call failed: {result}")
                    else:
                        call_ids.append(result)
                        call_count += 1
                
                # Wait before next batch (simulate continuous incoming calls)
                await asyncio.sleep(random.uniform(0.5, 2.0))
                
        else:
            # Batch mode: generate specified number of calls with high throughput
            # Calculate inter-call delay based on throughput
            calls_per_min = get_throughput()
            inter_call_delay = 60.0 / calls_per_min  # Seconds between calls
            
            # Start calls concurrently in batches
            batch_size = min(5, num_calls)  # Process 5 calls concurrently
            
            for batch_start in range(0, num_calls, batch_size):
                batch_end = min(batch_start + batch_size, num_calls)
                batch_num = batch_start // batch_size + 1
                total_batches = (num_calls + batch_size - 1) // batch_size
                
                print(f"\n📱 Batch {batch_num}/{total_batches}: Starting {batch_end - batch_start} concurrent calls")
                
                # Start batch of calls concurrently
                tasks = [
                    start_call(call_count + i) 
                    for i in range(batch_start, batch_end)
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, Exception):
                        print(f"⚠️  Call failed: {result}")
                    else:
                        call_ids.append(result)
                        call_count += 1
                
                # Short delay between batches (high throughput)
                if batch_end < num_calls:
                    await asyncio.sleep(inter_call_delay / batch_size)
        
        await stream.close()
        duration = (datetime.now() - start_time).total_seconds()
        calls_per_sec = len(call_ids) / duration if duration > 0 else 0
        
        print(f"\n{'='*80}")
        print(f"✅ SIMULATION COMPLETE")
        print(f"{'='*80}")
        print(f"📊 Statistics:")
        print(f"   Total calls: {len(call_ids)}")
        print(f"   Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"   Throughput: {calls_per_sec:.2f} calls/second ({calls_per_sec*60:.1f} calls/minute)")
        print(f"   Agents used: {len(set(agent_pool))}")
        print(f"   Table: {table_props.table_name}")
        print(f"{'='*80}\n")
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Interrupted by user")
        await stream.close()
        print(f"✅ Ingested {len(call_ids)} calls before interruption")
    except Exception as e:
        print(f"\n❌ Error during simulation: {e}")
        await stream.close()
        raise

def main():
    print("🚀 Phase 1.3: Zerobus Ingestion (Genesys Cloud Simulation)")
    print("="*80)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Simulate Genesys Cloud call center with Zerobus')
    parser.add_argument('num_calls', type=int, nargs='?', default=10, 
                       help='Number of calls to generate (default: 10)')
    parser.add_argument('--continuous', action='store_true',
                       help='Run continuously until interrupted')
    parser.add_argument('--throughput', type=float,
                       help='Calls per minute (default: variable based on time of day)')
    parser.add_argument('--duration', type=int,
                       help='Maximum duration in minutes (for continuous mode)')
    parser.add_argument('--members', type=int, default=50,
                       help='Number of members in pool (default: 50)')
    
    args = parser.parse_args()
    
    # Generate member pool
    print(f"\n📊 Generating member pool ({args.members} members)...")
    member_pool = generate_member_pool(args.members)
    print(f"✅ Generated {len(member_pool)} members")
    
    # Run simulation
    try:
        if args.continuous:
            print(f"\n🔄 Continuous mode: Generating calls at realistic throughput")
            if args.throughput:
                print(f"   Target throughput: {args.throughput} calls/minute")
            if args.duration:
                print(f"   Max duration: {args.duration} minutes")
        else:
            print(f"\n🎯 Generating {args.num_calls} calls...")
            if args.throughput:
                print(f"   Target throughput: {args.throughput} calls/minute")
        
        asyncio.run(simulate_call_center(
            num_calls=args.num_calls,
            member_pool=member_pool,
            throughput=args.throughput,
            continuous=args.continuous,
            max_duration_minutes=args.duration
        ))
        
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

