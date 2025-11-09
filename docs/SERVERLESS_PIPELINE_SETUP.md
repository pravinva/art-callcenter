# Serverless Pipeline Configuration for Unity Catalog

## Issue
The existing pipeline has a storage location (`dbfs:/pipelines/...`), so we cannot add a catalog via API. We need to either:
1. Update via UI manually
2. Create a new pipeline with serverless from the start

## JSON Configuration (Copy-Paste Ready)

```json
{
  "id": "4bc41e3f-072e-4e5a-80a9-dbb323f2994b",
  "pipeline_type": "WORKSPACE",
  "name": "art-callcenter-enrichment",
  "storage": "dbfs:/pipelines/4bc41e3f-072e-4e5a-80a9-dbb323f2994b",
  "catalog": "member_analytics",
  "target": "call_center",
  "libraries": [
    {
      "notebook": {
        "path": "/Workspace/Users/pravin.varma@databricks.com/art-callcenter/dlt_enrichment_pipeline"
      }
    }
  ],
  "continuous": true,
  "development": false,
  "photon": true,
  "serverless": true
}
```

## Key Changes for Serverless + Unity Catalog

1. **`catalog: "member_analytics"`** - Catalog name (required for serverless + UC)
2. **`target: "call_center"`** - Schema only (NOT `member_analytics.call_center`)
3. **`serverless: true`** - Enables serverless compute (Unity Catalog auto-enabled)
4. **No `clusters` config** - Serverless doesn't use cluster configuration

## Manual Update via UI

Since the API doesn't allow adding catalog to existing pipeline:

1. Go to: **Workflows → Delta Live Tables → `art-callcenter-enrichment`**
2. Click **"Settings"** → **"Compute"**
3. Update the configuration:
   - Set **`serverless: true`**
   - Add **`catalog: "member_analytics"`**
   - Change **`target`** from `"member_analytics.call_center"` to `"call_center"` (schema only)
   - Remove **`clusters`** array (not needed for serverless)
4. Save and restart

## Alternative: Create New Pipeline

If UI update doesn't work, create a new pipeline:

```bash
python scripts/create_serverless_pipeline.py
```

This will create `art-callcenter-enrichment-serverless` with the correct configuration.

## Benefits of Serverless

- ✅ Unity Catalog automatically enabled
- ✅ No cluster management needed
- ✅ Automatic scaling
- ✅ Cost-effective (pay per use)

## After Update

Once updated:
1. Restart the pipeline
2. Monitor status: `python scripts/check_update_status.py`
3. Verify `enriched_transcripts` table is created

