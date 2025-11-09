#!/usr/bin/env python3
"""
Create Secrets Scope for Zerobus
Creates the secrets scope and provides instructions for storing credentials.

Run: python scripts/setup_secrets_scope.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks.sdk import WorkspaceClient
from config.config import SECRETS_SCOPE, CLIENT_ID_SECRET, CLIENT_SECRET_KEY

def create_secrets_scope():
    """Create secrets scope for Zerobus credentials"""
    print("🔐 Creating Secrets Scope for Zerobus")
    print("="*80)
    
    w = WorkspaceClient()
    
    print(f"\n📋 Scope Name: {SECRETS_SCOPE}")
    
    try:
        # Check if scope exists
        scopes = list(w.secrets.list_scopes())
        scope_names = [s.name for s in scopes]
        
        if SECRETS_SCOPE in scope_names:
            print(f"✅ Secrets scope '{SECRETS_SCOPE}' already exists")
            return True
        else:
            print(f"\n📝 Creating secrets scope...")
            print(f"\n⚠️  Note: Secrets scopes must be created via Databricks UI or notebook")
            print(f"   The SDK doesn't support creating scopes directly")
            print(f"\n💡 To create the scope:")
            print(f"\n   Option 1: Via Databricks Notebook")
            print(f"   Run this in a Databricks notebook:")
            print(f"   dbutils.secrets.createScope('{SECRETS_SCOPE}')")
            print(f"\n   Option 2: Via Databricks UI")
            print(f"   1. Go to: Workspace → Users → Secrets")
            print(f"   2. Click 'Create Scope'")
            print(f"   3. Name: {SECRETS_SCOPE}")
            print(f"   4. Click 'Create'")
            print(f"\n   After creating, store credentials:")
            print(f"   dbutils.secrets.put('{SECRETS_SCOPE}', '{CLIENT_ID_SECRET}', '<client-id>')")
            print(f"   dbutils.secrets.put('{SECRETS_SCOPE}', '{CLIENT_SECRET_KEY}', '<client-secret>')")
            
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def print_oauth_instructions():
    """Print instructions for creating OAuth secrets"""
    print("\n" + "="*80)
    print("OAUTH CREDENTIALS SETUP")
    print("="*80)
    
    print("\n📋 Service Principal Details:")
    print("   Name: ART Zerobus Service Principal")
    print("   Application ID: f2b42bdc-1515-4b3c-9105-0493a1565bfd")
    
    print("\n🔑 Steps to Create OAuth Secret:")
    print("\n   1. Go to Databricks Account Console:")
    print("      https://accounts.cloud.databricks.com/")
    print("\n   2. Navigate to:")
    print("      Identity & Access → Service Principals")
    print("\n   3. Find 'ART Zerobus Service Principal'")
    print("\n   4. Click 'Manage' → 'OAuth secrets' tab")
    print("\n   5. Click 'Add OAuth secret'")
    print("\n   6. Copy the generated:")
    print("      - Client ID (this is your ZEROBUS_CLIENT_ID)")
    print("      - Client Secret (this is your ZEROBUS_CLIENT_SECRET)")
    print("\n   ⚠️  IMPORTANT: Copy the secret immediately - it won't be shown again!")
    
    print("\n💾 Store Credentials:")
    print("\n   Option 1: Environment Variables (for local testing)")
    print("   export ZEROBUS_CLIENT_ID='<client-id-from-account-console>'")
    print("   export ZEROBUS_CLIENT_SECRET='<client-secret-from-account-console>'")
    
    print("\n   Option 2: Databricks Secrets Scope (for production)")
    print("   After creating the secrets scope, run in a Databricks notebook:")
    print(f"   dbutils.secrets.put('{SECRETS_SCOPE}', '{CLIENT_ID_SECRET}', '<client-id>')")
    print(f"   dbutils.secrets.put('{SECRETS_SCOPE}', '{CLIENT_SECRET_KEY}', '<client-secret>')")
    
    print("\n🧪 Test After Setup:")
    print("   python scripts/03_zerobus_ingestion.py 5")

def main():
    print("\n" + "="*80)
    print("ZEROBUS CREDENTIALS COMPLETE SETUP GUIDE")
    print("="*80)
    
    # Check/create secrets scope
    scope_exists = create_secrets_scope()
    
    # Print OAuth instructions
    print_oauth_instructions()
    
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("\n1. ✅ Service Principal created")
    if not scope_exists:
        print("2. ⏳ Create secrets scope (see instructions above)")
    else:
        print("2. ✅ Secrets scope exists")
    print("3. ⏳ Create OAuth secret in Account Console (see instructions above)")
    print("4. ⏳ Store credentials (environment variables or secrets scope)")
    print("5. ⏳ Test ingestion: python scripts/03_zerobus_ingestion.py 5")
    
    print("\n💡 For mock testing without real credentials, use SQL fallback:")
    print("   python scripts/03_zerobus_ingestion_sql.py 5")

if __name__ == "__main__":
    main()

