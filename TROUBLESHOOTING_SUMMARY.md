# Step-by-Step Troubleshooting Summary

## Problem
```
[UC_NOT_ENABLED] Unity Catalog is not enabled on this cluster. SQLSTATE: 56038
```

## Troubleshooting Steps Completed

### ✅ Step 1: Diagnostic
```bash
python scripts/troubleshoot_pipeline_uc.py
```
**Findings:**
- ❌ Unity Catalog NOT enabled in cluster config
- ✅ Catalog exists: `member_analytics`
- ✅ Source table exists: `member_analytics.call_center.zerobus_transcripts` (101 rows)
- ✅ Target is valid: `member_analytics.call_center`

### ✅ Step 2: Attempted Fixes

**Fix Attempt 1: Add `enable_unity_catalog: True` to cluster config**
- Status: API update succeeded but field doesn't persist
- Issue: Field may not be returned by GET API even when set

**Fix Attempt 2: Switch to Serverless Mode**
- Status: Failed - Cannot add catalog to existing pipeline with storage location
- Error: `Cannot add catalog to an existing pipeline with defined storage location`

**Fix Attempt 3: Use `dlt.external()` Decorator**
- Status: ✅ Applied - Updated notebook to use `dlt.external()` pattern
- Rationale: This pattern may work better with Unity Catalog tables

### ✅ Step 3: Notebook Update

Changed from:
```python
spark.readStream.table("member_analytics.call_center.zerobus_transcripts")
```

To:
```python
@dlt.external(name="zerobus_transcripts_source")
def zerobus_transcripts_source():
    return spark.readStream.table("member_analytics.call_center.zerobus_transcripts")

# Then use:
dlt.read_stream("zerobus_transcripts_source")
```

## Next Steps

1. **Restart Pipeline**
   ```bash
   python scripts/restart_pipeline.py
   ```

2. **Monitor Status**
   ```bash
   python scripts/check_update_status.py
   ```

3. **If Still Failing:**
   - Check if Unity Catalog is enabled at workspace level
   - Consider recreating pipeline with Unity Catalog from start
   - Or use manual UI update to ensure Unity Catalog is enabled

## Alternative Solutions

### Option A: Manual UI Update
1. Go to: Workflows → Delta Live Tables → `art-callcenter-enrichment`
2. Click "Settings" → "Compute"
3. Under "Cluster Configuration", manually add:
   ```json
   {
     "enable_unity_catalog": true
   }
   ```
4. Save and restart

### Option B: Recreate Pipeline
If fixes don't work, recreate pipeline:
1. Create new DLT pipeline via UI
2. Set target: `member_analytics.call_center`
3. Enable Unity Catalog during creation
4. Upload notebook

### Option C: Check Workspace Settings
- Verify workspace has Unity Catalog enabled
- Check metastore assignment
- Verify user has UC permissions

## Files Created

- `scripts/troubleshoot_pipeline_uc.py` - Diagnostic script
- `scripts/fix_pipeline_serverless.py` - Fix attempts
- `TROUBLESHOOTING_GUIDE.md` - This guide

## Current Status

- ✅ Notebook updated with `dlt.external()` pattern
- ⏳ Waiting for pipeline restart to test fix
- ⏳ May need manual UI update if API approach doesn't work

