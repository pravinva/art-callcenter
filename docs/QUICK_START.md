# Quick Start Guide - Streamlit Dashboard

## 🚀 Starting the Dashboard

The dashboard is starting on **port 8520**.

**Access URL:** http://localhost:8520

## ⚙️ Prerequisites

### 1. Set Databricks Token
```bash
export DATABRICKS_TOKEN='your-databricks-token'
```

To get your token:
- Go to Databricks Workspace → User Settings → Access Tokens
- Generate a new token
- Copy and set it as environment variable

### 2. Verify Dependencies
```bash
cd /Users/pravin.varma/Documents/Demo/art-callcenter
source venv/bin/activate
pip install tornado pydeck  # If not already installed
```

## 🎯 Testing the Dashboard

### Step 1: Open Browser
Navigate to: **http://localhost:8520**

### Step 2: Check Sidebar
- Should show "Active Calls" dropdown
- If empty, check that:
  - DLT pipeline has processed data
  - `enriched_transcripts` table has recent rows

### Step 3: Select a Call
- Choose a call from the dropdown
- Dashboard should populate with:
  - **Column 1:** Live transcript
  - **Column 2:** AI Assistant (3 tabs)
  - **Column 3:** Compliance alerts

### Step 4: Test Features
- ✅ View transcript with sentiment indicators
- ✅ Click "Get AI Suggestion" button
- ✅ View member info in Member Info tab
- ✅ Search knowledge base
- ✅ View compliance alerts

## 🔧 Troubleshooting

### Dashboard won't start
```bash
# Check if port 8520 is in use
lsof -i :8520

# Kill existing process if needed
kill -9 <PID>

# Start fresh
cd /Users/pravin.varma/Documents/Demo/art-callcenter
source venv/bin/activate
streamlit run app/agent_dashboard.py --server.port 8520
```

### "No active calls" message
- Check DLT pipeline status
- Verify data exists:
  ```sql
  SELECT COUNT(*) 
  FROM member_analytics.call_center.enriched_transcripts
  WHERE timestamp > CURRENT_TIMESTAMP() - INTERVAL 10 MINUTE
  ```

### Connection errors
- Verify `DATABRICKS_TOKEN` is set:
  ```bash
  echo $DATABRICKS_TOKEN
  ```
- Check SQL Warehouse is running
- Verify Unity Catalog permissions

### Agent suggestions not working
- Agent is optional - other features should work
- Check LLM endpoint availability
- Verify UC Functions are accessible

## 📊 Expected Dashboard Features

✅ **Working:**
- ART branding and logo
- 3-column layout
- Active calls list
- Transcript display
- Member info from UC Functions
- Compliance alerts
- Call metrics

⚠️ **May need Databricks environment:**
- AI suggestions (requires LLM endpoint)
- Some UC Function calls

## 🎉 Success Indicators

When everything is working, you should see:
1. Dashboard loads with blue ART branding
2. Sidebar shows active calls
3. Selecting a call populates all 3 columns
4. Transcript displays with proper formatting
5. Member info shows from UC Functions
6. Compliance alerts display (if any violations)

## 📝 Next Steps

Once dashboard is working:
1. Test with different call scenarios
2. Verify AI suggestions functionality
3. Test compliance alert detection
4. Deploy as Databricks App for production

