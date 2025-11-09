# DLT Pipeline Unity Catalog Configuration Guide

## Issue
Unity Catalog requires cluster access mode to be "SINGLE_USER" or "SHARED", but DLT pipelines don't allow setting `access_mode` directly in the cluster configuration via API.

## Solution: Manual UI Configuration

### Step 1: Update Cluster Configuration
1. Go to: **Workflows → Delta Live Tables → `art-callcenter-enrichment`**
2. Click **"Settings"** → **"Compute"**
3. Under **"Cluster Configuration"**, edit the JSON and ensure:
   ```json
   {
     "enable_unity_catalog": true
   }
   ```

### Step 2: Set Access Mode (Critical!)
The access mode must be set at the **pipeline level**, not in cluster config:

1. In the same **"Settings"** page
2. Look for **"Access Mode"** or **"Cluster Access Mode"** setting
3. Set it to **"Single User"** (or "Shared" if using shared compute)
4. This is usually in a separate section from cluster configuration

### Step 3: Alternative - Use Serverless Compute
If manual access mode setting doesn't work, consider using serverless compute:
- Serverless automatically enables Unity Catalog
- Go to **"Compute"** settings
- Select **"Serverless"** instead of **"Standard"**
- Note: Requires catalog to be specified (may need to recreate pipeline)

## JSON Configuration (for reference)

```json
{
  "id": "4bc41e3f-072e-4e5a-80a9-dbb323f2994b",
  "pipeline_type": "WORKSPACE",
  "name": "art-callcenter-enrichment",
  "storage": "dbfs:/pipelines/4bc41e3f-072e-4e5a-80a9-dbb323f2994b",
  "clusters": [
    {
      "spark_conf": {
        "spark.databricks.cluster.profile": "singleNode",
        "spark.master": "local[*]"
      },
      "node_type_id": "i3.xlarge",
      "custom_tags": {
        "ResourceClass": "SingleNode"
      },
      "num_workers": 0,
      "enable_unity_catalog": true
    }
  ],
  "libraries": [
    {
      "notebook": {
        "path": "/Workspace/Users/pravin.varma@databricks.com/art-callcenter/dlt_enrichment_pipeline"
      }
    }
  ],
  "target": "member_analytics.call_center",
  "continuous": true,
  "development": false,
  "photon": true,
  "serverless": false
}
```

**Note:** The `access_mode` cannot be set via API for DLT pipelines - it must be configured via UI.

## Verification

After updating:
1. Save the pipeline settings
2. Restart the pipeline
3. Check logs - Unity Catalog errors should be resolved
4. Verify `enriched_transcripts` table is created

## If Still Failing

If Unity Catalog errors persist:
1. Check workspace Unity Catalog settings
2. Verify metastore assignment
3. Consider recreating pipeline with Unity Catalog enabled from start
4. Or use serverless compute (automatically enables Unity Catalog)

