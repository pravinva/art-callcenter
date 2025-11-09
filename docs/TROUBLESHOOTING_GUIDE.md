# Step-by-Step Troubleshooting Guide: DLT Pipeline Unity Catalog

## Problem
```
[UC_NOT_ENABLED] Unity Catalog is not enabled on this cluster. SQLSTATE: 56038
```

## Troubleshooting Steps

### Step 1: Run Diagnostic Script
```bash
python scripts/troubleshoot_pipeline_uc.py
```

This checks:
- ✅ Pipeline configuration
- ✅ Cluster configuration  
- ✅ Target catalog existence
- ✅ Source table accessibility
- ✅ Latest pipeline errors

### Step 2: Identify Root Cause

Based on diagnostic output:

**Issue Found:** Unity Catalog is NOT enabled in cluster config

**Other Checks:**
- ✅ Catalog exists: `member_analytics`
- ✅ Source table exists: `member_analytics.call_center.zerobus_transcripts` (101 rows)
- ✅ Target is valid: `member_analytics.call_center`

### Step 3: Apply Fix

**Option A: Standard Cluster with Explicit UC (Recommended for existing pipelines)**
```bash
python scripts/fix_pipeline_serverless.py
```
- Automatically tries serverless first
- Falls back to standard cluster with `enable_unity_catalog: True`
- Works for pipelines with existing storage location

**Option B: Manual Fix via UI**
1. Go to: Workflows → Delta Live Tables → `art-callcenter-enrichment`
2. Click "Settings" → "Compute"
3. Under "Cluster Configuration", ensure:
   - `enable_unity_catalog: True` is set
   - Or use "Serverless" compute (if creating new pipeline)

### Step 4: Verify Fix

```bash
# Check configuration
python scripts/troubleshoot_pipeline_uc.py

# Restart pipeline
python scripts/restart_pipeline.py

# Monitor status
python scripts/check_update_status.py
```

### Step 5: Monitor Pipeline

Expected progression:
1. `WAITING_FOR_RESOURCES` → Cluster provisioning
2. `RUNNING` → Processing data
3. `COMPLETED` → Table created

## Common Issues & Solutions

### Issue 1: `enable_unity_catalog` not persisting
**Solution:** Pipeline may need to be recreated, or use serverless mode

### Issue 2: Serverless requires catalog specification
**Solution:** Cannot add catalog to existing pipeline with storage location. Use standard cluster with explicit UC enablement instead.

### Issue 3: Cluster config not applied
**Solution:** 
- Stop all active pipeline updates
- Update configuration
- Restart pipeline

## Files Created

- `scripts/troubleshoot_pipeline_uc.py` - Comprehensive diagnostic script
- `scripts/fix_pipeline_serverless.py` - Automated fix script (tries serverless, falls back to standard)

## Next Steps After Fix

Once pipeline completes successfully:
1. ✅ Verify `enriched_transcripts` table exists
2. ✅ Run: `python scripts/create_uc_functions_with_enriched_table.py`
3. ✅ Proceed with Phase 4: GenAI Agent Development

