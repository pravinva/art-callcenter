#!/usr/bin/env python3
"""
Phase 1.2: Rich Mock Data Generator
Generate realistic call scenarios with 100+ variations.

Run: python scripts/02_mock_data_generator.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import mock data generator functions
from scripts.mock_data_generator import generate_member_pool, generate_realistic_call, CALL_SCENARIOS

def main():
    print("🚀 Phase 1.2: Rich Mock Data Generator")
    print("="*80)
    
    # Generate member pool
    print("\n📊 Generating member pool...")
    member_pool = generate_member_pool(50)
    print(f"✅ Generated {len(member_pool)} members")
    
    # Generate sample calls
    print("\n📞 Generating sample calls...")
    num_samples = 5
    calls = []
    for i in range(num_samples):
        call = generate_realistic_call(member_pool)
        calls.append(call)
        print(f"\n  Call {i+1}:")
        print(f"    Member: {call['member']['name']} ({call['member']['member_id']})")
        print(f"    Scenario: {call['scenario_type']} ({call['complexity']})")
        print(f"    Balance: ${call['member']['balance']:,.0f}")
        print(f"    Utterances: {len(call['dialogue'])}")
    
    print(f"\n✅ Generated {len(calls)} sample calls")
    print(f"\n📋 Available scenario types: {list(CALL_SCENARIOS.keys())}")
    print(f"\n💡 This generator can create 100+ call variations")
    print(f"   Ready for Phase 1.3: Zerobus Ingestion")
    
    return calls, member_pool

if __name__ == "__main__":
    calls, members = main()
