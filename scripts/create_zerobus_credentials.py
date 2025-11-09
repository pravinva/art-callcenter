#!/usr/bin/env python3
"""
Create Service Principal for Zerobus Testing
Creates a service principal and stores credentials for Zerobus ingestion.

Run: python scripts/create_zerobus_credentials.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.iam import ServicePrincipal
from config.config import get_workspace_client, SECRETS_SCOPE, CLIENT_ID_SECRET, CLIENT_SECRET_KEY

def create_service_principal():
    """Create a service principal for Zerobus"""
    print("🚀 Creating Service Principal for Zerobus")
    print("="*80)
    
    w = get_workspace_client()
    
    # Service principal details
    sp_name = "art-zerobus-service-principal"
    sp_display_name = "ART Zerobus Service Principal"
    
    print(f"\n📋 Service Principal Details:")
    print(f"   Name: {sp_name}")
    print(f"   Display Name: {sp_display_name}")
    
    try:
        # Check if service principal already exists
        print("\n🔍 Checking for existing service principal...")
        existing_sps = list(w.service_principals.list(filter=f"displayName eq '{sp_display_name}'"))
        
        if existing_sps:
            sp = existing_sps[0]
            print(f"✅ Service principal already exists: {sp.id}")
            print(f"   Application ID: {sp.application_id}")
            print(f"\n⚠️  To get credentials, you need to:")
            print(f"   1. Go to Databricks Account Console")
            print(f"   2. Navigate to Service Principals")
            print(f"   3. Find '{sp_display_name}'")
            print(f"   4. Create OAuth secret for this service principal")
            return sp
        else:
            print("   No existing service principal found")
            
            # Create new service principal
            print(f"\n📝 Creating new service principal...")
            sp = w.service_principals.create(
                display_name=sp_display_name,
                active=True
            )
            
            print(f"✅ Service principal created!")
            print(f"   ID: {sp.id}")
            print(f"   Application ID: {sp.application_id}")
            print(f"\n📋 Next Steps:")
            print(f"   1. Go to Databricks Account Console (not workspace)")
            print(f"   2. Navigate to: Identity & Access → Service Principals")
            print(f"   3. Find '{sp_display_name}'")
            print(f"   4. Click 'Manage' → 'OAuth secrets'")
            print(f"   5. Create a new OAuth secret")
            print(f"   6. Copy the Client ID and Client Secret")
            print(f"\n   Then store them:")
            print(f"   export ZEROBUS_CLIENT_ID='<client-id>'")
            print(f"   export ZEROBUS_CLIENT_SECRET='<client-secret>'")
            print(f"\n   Or add to Databricks secrets scope '{SECRETS_SCOPE}':")
            print(f"   dbutils.secrets.put('{SECRETS_SCOPE}', '{CLIENT_ID_SECRET}', '<client-id>')")
            print(f"   dbutils.secrets.put('{SECRETS_SCOPE}', '{CLIENT_SECRET_KEY}', '<client-secret>')")
            
            return sp
            
    except Exception as e:
        print(f"\n❌ Error creating service principal: {e}")
        print(f"\n💡 Alternative: Create manually via Account Console")
        print(f"   1. Go to: https://accounts.cloud.databricks.com/")
        print(f"   2. Navigate to: Identity & Access → Service Principals")
        print(f"   3. Click 'Add Service Principal'")
        print(f"   4. Name: {sp_display_name}")
        print(f"   5. Create OAuth secret")
        print(f"   6. Copy Client ID and Client Secret")
        raise

def check_secrets_scope():
    """Check if secrets scope exists"""
    from config.config import SECRETS_SCOPE, CLIENT_ID_SECRET, CLIENT_SECRET_KEY
    
    w = get_workspace_client()
    
    print(f"\n🔍 Checking secrets scope '{SECRETS_SCOPE}'...")
    
    try:
        scopes = list(w.secrets.list_scopes())
        scope_names = [s.name for s in scopes]
        
        if SECRETS_SCOPE in scope_names:
            print(f"✅ Secrets scope exists")
            return True
        else:
            print(f"⚠️  Secrets scope '{SECRETS_SCOPE}' not found")
            print(f"\n   Create it in a Databricks notebook:")
            print(f"   dbutils.secrets.createScope('{SECRETS_SCOPE}')")
            print(f"\n   Or via UI: Workspace → Users → Secrets → Create Scope")
            return False
            
    except Exception as e:
        print(f"❌ Error checking secrets: {e}")
        return False

def main():
    print("\n" + "="*80)
    print("ZEROBUS CREDENTIALS SETUP")
    print("="*80)
    
    try:
        # Check secrets scope
        secrets_ok = check_secrets_scope()
        
        # Create service principal
        sp = create_service_principal()
        
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"\n✅ Service Principal: {sp.display_name}")
        print(f"   Application ID: {sp.application_id}")
        
        if secrets_ok:
            print(f"\n✅ Secrets scope '{SECRETS_SCOPE}' exists")
            print(f"   You can store credentials there after creating OAuth secret")
        else:
            print(f"\n⚠️  Create secrets scope '{SECRETS_SCOPE}' first")
        
        print(f"\n📝 To complete setup:")
        print(f"   1. Create OAuth secret in Account Console")
        print(f"   2. Store credentials (environment variables or secrets scope)")
        print(f"   3. Test with: python scripts/03_zerobus_ingestion.py 5")
        
    except Exception as e:
        print(f"\n❌ Setup incomplete: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

