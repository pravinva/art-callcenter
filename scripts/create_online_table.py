#!/usr/bin/env python3
"""
Create Online Table programmatically using Databricks CLI
Online Tables provide low-latency, real-time access to Delta tables.

Run: python scripts/create_online_table.py
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import ENRICHED_TABLE

def create_online_table():
    """Create Online Table using Databricks CLI"""
    print("🚀 Creating Online Table")
    print("="*80)
    
    # Parse table name
    # Format: catalog.schema.table
    table_name = ENRICHED_TABLE  # member_analytics.call_center.enriched_transcripts
    
    print(f"\n📋 Table: {table_name}")
    print(f"   This will create an Online Table for low-latency access")
    
    # Use Databricks CLI to create Online Table
    # Command: databricks online-tables create --name <catalog>.<schema>.<table>
    cmd = ["databricks", "online-tables", "create", "--name", table_name]
    
    print(f"\n🔧 Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        print("\n✅ Online Table created successfully!")
        print(result.stdout)
        
        print("\n📋 Next Steps:")
        print("   1. Online Table is now available for real-time queries")
        print("   2. Use it in UC Functions and agent tools")
        print("   3. Configure refresh settings via UI if needed")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error creating Online Table:")
        print(f"   {e.stderr}")
        
        if "already exists" in e.stderr.lower():
            print("\n✅ Online Table already exists!")
            return True
        elif "not found" in e.stderr.lower() or "does not exist" in e.stderr.lower():
            print("\n⚠️  Source table might not exist or CLI version is outdated")
            print("   Try updating Databricks CLI:")
            print("   pip install --upgrade databricks-cli")
            print("\n   Or create manually via UI:")
            print("   1. Go to Catalog Explorer")
            print(f"   2. Select: {table_name}")
            print("   3. Click 'Create Online Table'")
        else:
            print("\n💡 Alternative: Create via UI")
            print("   1. Go to Catalog Explorer")
            print(f"   2. Select: {table_name}")
            print("   3. Click 'Create Online Table'")
        
        return False
        
    except FileNotFoundError:
        print("\n❌ Databricks CLI not found")
        print("   Install with: pip install databricks-cli")
        print("   Or create manually via UI:")
        print("   1. Go to Catalog Explorer")
        print(f"   2. Select: {table_name}")
        print("   3. Click 'Create Online Table'")
        return False

if __name__ == "__main__":
    success = create_online_table()
    sys.exit(0 if success else 1)

