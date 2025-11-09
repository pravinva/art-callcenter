#!/usr/bin/env python3
"""
Phase 5: Deploy Streamlit Dashboard as Databricks App
Creates the app structure and provides deployment instructions.

Run: python scripts/08_deploy_streamlit_app.py
"""
import sys
import os
from pathlib import Path
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.workspace import ImportFormat, Language
from config.config import get_workspace_client

def create_app_structure():
    """Create Databricks App structure"""
    print("🚀 Phase 5: Deploy Streamlit Dashboard as Databricks App")
    print("="*80)
    
    # App configuration
    app_name = "art-live-agent-assist"
    workspace_path = "/Workspace/Users/pravin.varma@databricks.com/art-callcenter-app"
    
    print(f"\n📋 App Configuration:")
    print(f"   Name: {app_name}")
    print(f"   Workspace Path: {workspace_path}")
    
    # Create local app directory structure
    local_app_dir = Path(__file__).parent.parent / "databricks_app"
    local_app_dir.mkdir(exist_ok=True)
    
    print(f"\n📁 Creating app structure...")
    
    # Copy Streamlit app
    app_file = Path(__file__).parent.parent / "app" / "agent_dashboard.py"
    if app_file.exists():
        shutil.copy(app_file, local_app_dir / "app.py")
        print(f"   ✅ Copied: app/agent_dashboard.py → app.py")
    else:
        print(f"   ❌ Source file not found: {app_file}")
        return False
    
    # Create requirements.txt for the app
    requirements_content = """streamlit>=1.28.0
databricks-sql-connector>=3.0.0
databricks-sdk>=0.40.0
pandas>=2.0.0
"""
    
    (local_app_dir / "requirements.txt").write_text(requirements_content)
    print(f"   ✅ Created: requirements.txt")
    
    # Create README for the app
    readme_content = """# ART Live Agent Assist Dashboard

Real-time AI assistance for Australian Retirement Trust call center agents.

## Features
- Live call transcript monitoring
- AI-powered suggestions
- Compliance alerts
- Member 360 view

## Usage
The app will automatically start when deployed as a Databricks App.
"""
    
    (local_app_dir / "README.md").write_text(readme_content)
    print(f"   ✅ Created: README.md")
    
    print(f"\n✅ Local app structure created at: {local_app_dir}")
    
    # Upload to Databricks workspace
    print(f"\n📤 Uploading to Databricks workspace...")
    w = get_workspace_client()
    
    try:
        # Create directory in workspace (must create full path)
        workspace_dir = workspace_path
        try:
            w.workspace.mkdirs(workspace_dir)
            print(f"   ✅ Created directory: {workspace_dir}")
        except Exception as e:
            if "RESOURCE_ALREADY_EXISTS" not in str(e):
                print(f"   ⚠️  Directory might already exist: {e}")
        
        # Upload app.py
        app_workspace_path = f"{workspace_path}/app.py"
        with open(local_app_dir / "app.py", "rb") as f:
            w.workspace.upload(
                app_workspace_path,
                f.read(),
                format=ImportFormat.SOURCE,
                language=Language.PYTHON,
                overwrite=True
            )
        print(f"   ✅ Uploaded: {app_workspace_path}")
        
        # Upload requirements.txt
        req_workspace_path = f"{workspace_path}/requirements.txt"
        with open(local_app_dir / "requirements.txt", "rb") as f:
            w.workspace.upload(
                req_workspace_path,
                f.read(),
                format=ImportFormat.AUTO,
                overwrite=True
            )
        print(f"   ✅ Uploaded: {req_workspace_path}")
        
        print(f"\n✅ App files uploaded successfully!")
        
        print(f"\n📋 Next Steps:")
        print(f"   1. Go to Databricks Workspace → Apps")
        print(f"   2. Click 'Create App'")
        print(f"   3. Select source: {workspace_path}")
        print(f"   4. App name: {app_name}")
        print(f"   5. Click 'Create'")
        print(f"\n   The app will be available at: /apps/{app_name}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error uploading app: {e}")
        import traceback
        traceback.print_exc()
        
        print(f"\n💡 Manual Upload Alternative:")
        print(f"   1. Create directory: {workspace_path}")
        print(f"   2. Upload files from: {local_app_dir}")
        print(f"   3. Create app via UI")
        
        return False

if __name__ == "__main__":
    success = create_app_structure()
    sys.exit(0 if success else 1)

