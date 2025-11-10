#!/usr/bin/env python3
"""
Upload Gold Layer DLT Pipeline Notebook to Databricks
Uploads the Gold layer DLT pipeline notebook to workspace for deployment.

Run: python scripts/upload_gold_layer_notebook.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.workspace import ImportFormat, Language
from config.config import get_workspace_client

def upload_gold_layer_notebook():
    """Upload Gold Layer DLT pipeline notebook to Databricks workspace"""
    print("📤 Uploading Gold Layer DLT Pipeline Notebook")
    print("="*80)
    
    w = get_workspace_client()
    
    # Notebook paths
    local_notebook = Path(__file__).parent.parent / "notebooks" / "dlt_gold_layer_pipeline.py"
    workspace_path = "/Workspace/Users/pravin.varma@databricks.com/art-callcenter/dlt_gold_layer_pipeline"
    
    if not local_notebook.exists():
        print(f"❌ Notebook not found: {local_notebook}")
        return False
    
    print(f"\n📄 Local file: {local_notebook}")
    print(f"📁 Workspace path: {workspace_path}")
    
    try:
        # Create directory if it doesn't exist
        workspace_dir = "/Workspace/Users/pravin.varma@databricks.com/art-callcenter"
        try:
            w.workspace.mkdirs(workspace_dir)
            print(f"✅ Created directory: {workspace_dir}")
        except Exception as e:
            # Directory might already exist, that's okay
            print(f"   Directory check: {workspace_dir}")
        
        # Read notebook content
        with open(local_notebook, 'r') as f:
            notebook_content = f.read()
        
        # Upload to workspace
        print(f"\n📤 Uploading notebook...")
        w.workspace.upload(
            path=workspace_path,
            content=notebook_content.encode('utf-8'),
            format=ImportFormat.SOURCE,  # Python notebook
            language=Language.PYTHON,
            overwrite=True
        )
        
        print(f"✅ Notebook uploaded successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error uploading notebook: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = upload_gold_layer_notebook()
    
    if success:
        print(f"\n✅ Gold layer notebook ready for DLT pipeline deployment")
    else:
        print(f"\n⚠️  Upload failed. Check error messages above")

