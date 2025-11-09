# Testing the Streamlit Dashboard

## 🚀 Dashboard Started

The Streamlit dashboard should now be running at:

**URL:** http://localhost:8520

## 📋 Testing Checklist

### 1. **Access the Dashboard**
- Open your browser and go to: `http://localhost:8520`
- You should see the ART Live Agent Assist dashboard with:
  - ART logo in the header
  - Blue branding colors
  - Sidebar with "Active Calls" section

### 2. **Check Prerequisites**
Make sure you have:
- ✅ `DATABRICKS_TOKEN` environment variable set
- ✅ SQL Warehouse running (ID: 4b9b953939869799)
- ✅ Data in `enriched_transcripts` table

### 3. **Test Features**

**Sidebar:**
- Should show "Active Calls" dropdown
- Should list calls from last 10 minutes
- Auto-refresh toggle should be available

**Column 1 - Live Transcript:**
- Select a call from sidebar
- Should display transcript with:
  - Speaker labels (Member/Agent)
  - Sentiment indicators (😊😐😟)
  - Timestamps
  - Compliance warnings (if any)

**Column 2 - AI Assistant:**
- **Suggestions Tab:** Click "Get AI Suggestion" button
- **Member Info Tab:** Should show member details from UC Function
- **Knowledge Base Tab:** Search for articles

**Column 3 - Compliance Alerts:**
- Should show compliance violations
- Should display call metrics (sentiment counts, intents)

### 4. **Troubleshooting**

**If dashboard doesn't load:**
```bash
# Check if Streamlit is running
lsof -i :8520

# Restart manually
cd /Users/pravin.varma/Documents/Demo/art-callcenter
source venv/bin/activate
streamlit run app/agent_dashboard.py --server.port 8520
```

**If "No active calls" message:**
- Check that DLT pipeline has processed data
- Verify `enriched_transcripts` table has recent rows:
  ```sql
  SELECT COUNT(*) FROM member_analytics.call_center.enriched_transcripts
  WHERE timestamp > CURRENT_TIMESTAMP() - INTERVAL 10 MINUTE
  ```

**If connection errors:**
- Verify `DATABRICKS_TOKEN` is set:
  ```bash
  echo $DATABRICKS_TOKEN
  ```
- Check SQL Warehouse is running in Databricks UI

**If agent suggestions fail:**
- Agent is optional - other features should still work
- Check UC Functions are accessible
- Verify LLM endpoint is available

### 5. **Expected Behavior**

✅ **Working:**
- Dashboard loads with ART branding
- Active calls list populates
- Transcript displays correctly
- Member info shows from UC Functions
- Compliance alerts display

⚠️ **May need Databricks environment:**
- AI suggestions (requires LLM endpoint access)
- Some UC Function calls (may need Unity Catalog permissions)

## 🎯 Quick Test Commands

```bash
# Check dashboard is running
curl http://localhost:8520

# View Streamlit logs
# (Check terminal where you ran streamlit)

# Test UC Functions directly
python scripts/test_uc_functions.py
```

## 📊 Next Steps

Once dashboard is working:
1. Test with live call data
2. Verify all 3 columns display correctly
3. Test AI suggestions functionality
4. Create Databricks App for production deployment

