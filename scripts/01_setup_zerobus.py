#!/usr/bin/env python3
"""
Phase 1.1: Zerobus Setup
Configure workspace, secrets, and Zerobus SDK credentials.

Run: python scripts/01_setup_zerobus.py
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.workspace import SecretScope
from config.config import get_workspace_client, get_workspace_url, SECRETS_SCOPE, CLIENT_ID_SECRET, CLIENT_SECRET_KEY

def check_secrets_scope(w: WorkspaceClient):
    """Check if secrets scope exists, create if not"""
    print("🔍 Checking secrets scope...")
    
    try:
        scopes = list(w.secrets.list_scopes())
        scope_names = [s.name for s in scopes]
        
        if SECRETS_SCOPE in scope_names:
            print(f"✅ Secrets scope '{SECRETS_SCOPE}' already exists")
            return True
        else:
            print(f"⚠️  Secrets scope '{SECRETS_SCOPE}' not found")
            print(f"\nTo create it, run in Databricks workspace:")
            print(f"  dbutils.secrets.createScope('{SECRETS_SCOPE}')")
            print(f"\nOr via UI: Workspace → Users → Secrets → Create Scope")
            print(f"\nThen add these secrets:")
            print(f"  - {SECRETS_SCOPE}/{CLIENT_ID_SECRET}")
            print(f"  - {SECRETS_SCOPE}/{CLIENT_SECRET_KEY}")
            return False
    except Exception as e:
        print(f"❌ Error checking secrets: {e}")
        return False

def check_catalog_schema(w: WorkspaceClient):
    """Check if catalog and schema exist"""
    from config.config import CATALOG_NAME, SCHEMA_NAME
    
    print(f"\n🔍 Checking catalog '{CATALOG_NAME}' and schema '{SCHEMA_NAME}'...")
    
    try:
        # Check catalog
        catalogs = list(w.catalogs.list())
        catalog_names = [c.name for c in catalogs]
        
        if CATALOG_NAME not in catalog_names:
            print(f"⚠️  Catalog '{CATALOG_NAME}' not found")
            print(f"\n   Run SQL script to create:")
            print(f"   databricks-sql-cli -f sql/01_setup.sql")
            print(f"\n   Or manually:")
            print(f"   CREATE CATALOG IF NOT EXISTS {CATALOG_NAME};")
            return False
        
        # Check schema
        schemas = list(w.schemas.list(catalog_name=CATALOG_NAME))
        schema_names = [s.name for s in schemas]
        
        if SCHEMA_NAME not in schema_names:
            print(f"⚠️  Schema '{CATALOG_NAME}.{SCHEMA_NAME}' not found")
            print(f"\n   Run SQL script to create:")
            print(f"   databricks-sql-cli -f sql/01_setup.sql")
            return False
        
        print(f"✅ Catalog and schema exist")
        return True
        
    except Exception as e:
        print(f"❌ Error checking catalog/schema: {e}")
        return False

def print_setup_instructions():
    """Print setup instructions"""
    
    print("\n" + "="*80)
    print("📋 ZEROBUS SETUP INSTRUCTIONS")
    print("="*80)
    
    workspace_url = get_workspace_url()
    print(f"\nWorkspace URL: {workspace_url}")
    
    print("\n1. Create Secrets Scope (if not exists):")
    print(f"   Run in Databricks notebook:")
    print(f"   dbutils.secrets.createScope('{SECRETS_SCOPE}')")
    
    print("\n2. Add Service Principal Credentials:")
    print(f"   Add secrets to scope '{SECRETS_SCOPE}':")
    print(f"   - {CLIENT_ID_SECRET}: Your service principal client ID")
    print(f"   - {CLIENT_SECRET_KEY}: Your service principal secret")
    
    print("\n3. Create Catalog and Schema:")
    print("   Run SQL script:")
    print("   databricks-sql-cli -f sql/01_setup.sql")
    print("\n   Or manually run the SQL commands in sql/01_setup.sql")
    
    print("\n4. Install Zerobus SDK:")
    print("   pip install databricks-zerobus-sdk")
    
    print("\n" + "="*80)

def main():
    print("🚀 Phase 1.1: Zerobus Setup")
    print("="*80)
    
    try:
        w = get_workspace_client()
        workspace_url = get_workspace_url()
        print(f"✅ Connected to workspace: {workspace_url}")
        
        # Check secrets
        secrets_ok = check_secrets_scope(w)
        
        # Check catalog/schema
        catalog_ok = check_catalog_schema(w)
        
        if secrets_ok and catalog_ok:
            print("\n✅ All prerequisites met!")
            print("   You can proceed to Phase 1.2: Mock Data Generator")
        else:
            print_setup_instructions()
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("  1. Databricks CLI is configured (~/.databrickscfg)")
        print("  2. You have workspace access")
        print("  3. You have permissions to read secrets and catalogs")
        sys.exit(1)

if __name__ == "__main__":
    main()

