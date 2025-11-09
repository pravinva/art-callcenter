# Zerobus Credentials Setup Summary

## What We Created

✅ **Service Principal**: ART Zerobus Service Principal
- **ID**: 70382044676654
- **Application ID**: f2b42bdc-1515-4b3c-9105-0493a1565bfd

## What You Need to Do

### Step 1: Create OAuth Secret (Account Console)

1. Go to: https://accounts.cloud.databricks.com/
2. Navigate to: **Identity & Access → Service Principals**
3. Find: **ART Zerobus Service Principal**
4. Click: **Manage → OAuth secrets** tab
5. Click: **Add OAuth secret**
6. **Copy immediately**:
   - Client ID
   - Client Secret
   - ⚠️ Secret won't be shown again!

### Step 2: Create Secrets Scope (Workspace)

**Option A: Via Notebook**
```python
dbutils.secrets.createScope('art-zerobus')
```

**Option B: Via UI**
1. Go to: Workspace → Users → Secrets
2. Click: Create Scope
3. Name: `art-zerobus`
4. Click: Create

### Step 3: Store Credentials

**For Local Testing (Environment Variables):**
```bash
export ZEROBUS_CLIENT_ID='<client-id-from-step-1>'
export ZEROBUS_CLIENT_SECRET='<client-secret-from-step-1>'
```

**For Production (Databricks Secrets):**
```python
# Run in Databricks notebook
dbutils.secrets.put('art-zerobus', 'service-principal-id', '<client-id>')
dbutils.secrets.put('art-zerobus', 'service-principal-secret', '<client-secret>')
```

### Step 4: Test

```bash
# Test with Zerobus SDK (requires credentials)
python scripts/03_zerobus_ingestion.py 5

# Or use SQL fallback (no credentials needed)
python scripts/03_zerobus_ingestion_sql.py 5
```

## Mock Testing Without Credentials

For testing without OAuth credentials, use the SQL fallback script which inserts directly into the table:

```bash
python scripts/03_zerobus_ingestion_sql.py 10
```

This works immediately and doesn't require any credentials!

