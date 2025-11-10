# Demo Flow Guide: ART Call Center Solution
## Complete End-to-End Demonstration

This guide walks through demonstrating the entire call center solution from data ingestion to analytics dashboards.

---

## 🎯 Demo Overview

**Duration:** 15-20 minutes  
**Audience:** Technical stakeholders, business users, executives  
**Goal:** Show real-time AI-powered call center assistance with end-to-end data flow

---

## 📋 Pre-Demo Checklist

### Prerequisites
- [ ] DLT pipeline is running (Silver layer enrichment)
- [ ] Gold layer pipeline has run at least once
- [ ] UC Functions are deployed
- [ ] Streamlit dashboards are running
- [ ] Knowledge Base is populated with ART articles
- [ ] Test escalation data is inserted (2 escalation calls)

### Dashboards Running
- [ ] Live Agent Dashboard: `http://localhost:8520` (or deployed URL)
- [ ] Supervisor Dashboard: Available via navigation
- [ ] Analytics Dashboard: Available via navigation

---

## 🚀 Demo Flow

### **Phase 1: Data Ingestion (2 minutes)**

#### 1.1 Show Bronze Layer Ingestion

**What to Show:**
- Zerobus SDK ingestion OR SQL fallback method
- Raw call transcripts being ingested

**Scripts to Run:**
```bash
# Option 1: Zerobus SDK (if configured)
python scripts/03_zerobus_ingestion.py

# Option 2: SQL fallback (always works)
python scripts/03_zerobus_ingestion_sql.py
```

**What to Explain:**
- "We're ingesting call transcripts from Genesys Cloud via Zerobus"
- "Data flows into our Bronze layer: `member_analytics.call_center.zerobus_transcripts`"
- "Each utterance is captured in real-time with speaker identification"

**SQL to Show:**
```sql
-- Show recent raw transcripts
SELECT 
    call_id,
    member_name,
    agent_id,
    timestamp,
    speaker,
    transcript_segment,
    scenario
FROM member_analytics.call_center.zerobus_transcripts
ORDER BY timestamp DESC
LIMIT 10;
```

**Key Points:**
- ✅ Real-time ingestion (every few seconds)
- ✅ Raw transcripts with metadata
- ✅ Speaker identification (agent vs customer)
- ✅ Call scenarios and member information

---

### **Phase 2: Silver Layer Processing (2 minutes)**

#### 2.1 Show DLT Pipeline Processing

**What to Show:**
- DLT pipeline running status
- Enriched transcripts being created

**What to Explain:**
- "Our DLT pipeline automatically processes raw transcripts"
- "Adds sentiment analysis, intent detection, and compliance checking"
- "Creates Silver layer: `member_analytics.call_center.enriched_transcripts`"

**SQL to Show:**
```sql
-- Show enriched transcripts with sentiment/intent/compliance
SELECT 
    call_id,
    member_name,
    agent_id,
    timestamp,
    speaker,
    transcript_segment,
    sentiment,
    intent_category,
    compliance_flag,
    compliance_severity,
    enriched_at
FROM member_analytics.call_center.enriched_transcripts
ORDER BY enriched_at DESC
LIMIT 10;
```

**Key Points:**
- ✅ Automatic enrichment (no manual intervention)
- ✅ Sentiment analysis (positive/negative/neutral)
- ✅ Intent detection (contribution_inquiry, complaint, etc.)
- ✅ Compliance flagging (privacy_breach, personal_advice, etc.)
- ✅ Real-time processing (streaming)

**Visual:**
- Show DLT pipeline status in Databricks UI
- Show enriched data appearing within seconds of ingestion

---

### **Phase 3: Live Agent Dashboard (5 minutes)**

#### 3.1 Navigate to Live Agent Dashboard

**URL:** `http://localhost:8520` (or deployed URL)

**What to Show:**

1. **Sidebar - Active Calls**
   - List of active calls
   - Call selection dropdown
   - Real-time call count

2. **Live Transcript Panel (Left)**
   - Real-time transcript updates
   - Speaker identification (Member/Agent)
   - Sentiment indicators (😊/😐/😞)
   - Compliance warnings (if any)

3. **AI Assistant Panel (Center)**
   - Context Summary (auto-updates)
   - AI-Generated Suggestions
   - Response time display
   - "AI Suggest" button

4. **Member Info Panel (Right)**
   - Member details
   - Account balance
   - Recent interactions
   - Life stage

5. **Knowledge Base Tab**
   - Search functionality
   - Auto-suggested questions
   - Relevant KB articles
   - Article content display

**Demo Actions:**

1. **Select an Active Call**
   - Show call appears in transcript
   - Show context summary updates
   - Show member info loads

2. **Show Real-Time Updates**
   - New utterances appear automatically
   - Sentiment updates in real-time
   - Compliance warnings appear if triggered

3. **Test AI Suggestions**
   - Click "AI Suggest"
   - Show response time (< 2 seconds)
   - Show relevant suggestions appear
   - Explain how AI analyzes context

4. **Search Knowledge Base**
   - Type: "contribution limits"
   - Show relevant articles appear
   - Click article to show content
   - Show auto-suggested questions

5. **Show Compliance Alerts**
   - If compliance violation detected
   - Show warning appears
   - Explain severity levels

**Key Points:**
- ✅ Real-time transcript updates
- ✅ AI-powered suggestions
- ✅ Context-aware assistance
- ✅ Knowledge base integration
- ✅ Compliance monitoring

---

### **Phase 4: Supervisor Dashboard (4 minutes)**

#### 4.1 Navigate to Supervisor Dashboard

**What to Show:**

1. **Dashboard Overview**
   - Total active calls
   - Escalation alerts count
   - Average call metrics
   - Real-time statistics

2. **Escalation Alerts Section**
   - Show 2 escalation calls (from test data)
   - Risk scores and factors
   - Escalation recommendations
   - Call details

3. **Active Calls Table**
   - All active calls
   - Risk scores
   - Escalation status
   - Filtering options

**Demo Actions:**

1. **Show Escalation Alerts**
   - Point out 2 escalation calls
   - Explain escalation criteria:
     - CRITICAL compliance violations
     - Multiple negative sentiments + compliance issues
   - Show risk scores (15, 12+)
   - Show recommendations

2. **Filter Calls**
   - Filter by "Escalation Needed"
   - Show only escalation calls
   - Filter by agent
   - Filter by scenario

3. **Click on Escalation Call**
   - Show call details
   - Show transcript
   - Show risk factors
   - Show compliance violations

4. **Show Real-Time Monitoring**
   - Calls update automatically
   - New escalations appear
   - Risk scores update

**Key Points:**
- ✅ Real-time escalation detection
- ✅ Risk scoring (0-20+ scale)
- ✅ Compliance violation tracking
- ✅ Supervisor alerts
- ✅ Call filtering and search

---

### **Phase 5: Analytics Dashboard (3 minutes)**

#### 5.1 Navigate to Analytics Dashboard

**What to Show:**

1. **Key Metrics**
   - Total calls today
   - Average call duration
   - Escalation rate
   - Compliance violation rate

2. **Charts and Visualizations**
   - Calls by scenario (pie chart)
   - Sentiment distribution (bar chart)
   - Compliance violations over time (line chart)
   - Agent performance metrics

3. **Call Summaries**
   - Recent call summaries
   - Member interaction history
   - Daily statistics

**Demo Actions:**

1. **Show Daily Statistics**
   - Total calls processed
   - Average metrics
   - Trends over time

2. **Show Charts**
   - Explain sentiment distribution
   - Show compliance trends
   - Show scenario breakdown

3. **Show Call Summaries**
   - Click on a call summary
   - Show full transcript summary
   - Show key insights

4. **Show Agent Performance**
   - Agent metrics
   - Average call duration
   - Escalation rates per agent

**Key Points:**
- ✅ Historical analytics
- ✅ Trend analysis
- ✅ Agent performance tracking
- ✅ Compliance reporting
- ✅ Call summaries (Gold layer)

---

## 🎬 Complete Demo Script

### **Opening (30 seconds)**
"Today I'll demonstrate our AI-powered call center solution for Australian Retirement Trust. We'll see the complete data flow from raw call transcripts through real-time AI assistance to analytics dashboards."

### **Data Ingestion (2 minutes)**
"First, let's see how call transcripts are ingested from Genesys Cloud via Zerobus into our Bronze layer..."

[Run ingestion script, show SQL query]

### **Silver Layer Processing (2 minutes)**
"Our DLT pipeline automatically enriches transcripts with sentiment analysis, intent detection, and compliance checking..."

[Show DLT pipeline, show enriched data]

### **Live Agent Dashboard (5 minutes)**
"Now let's see how agents use the system in real-time. This dashboard provides AI-powered assistance during live calls..."

[Walk through dashboard features]

### **Supervisor Dashboard (4 minutes)**
"Supervisors can monitor all calls and get alerted to escalations in real-time..."

[Show escalations, filtering, monitoring]

### **Analytics Dashboard (3 minutes)**
"Finally, our analytics dashboard provides insights into call patterns, agent performance, and compliance trends..."

[Show analytics, charts, summaries]

### **Closing (30 seconds)**
"This solution provides end-to-end visibility and AI assistance for call center operations, from real-time agent support to compliance monitoring and analytics."

---

## 🔍 Key Demo Points to Emphasize

### **Real-Time Processing**
- ✅ Data flows in real-time (seconds, not minutes)
- ✅ AI suggestions appear instantly
- ✅ Escalations detected immediately

### **AI-Powered Assistance**
- ✅ Context-aware suggestions
- ✅ Knowledge base integration
- ✅ Sentiment and intent analysis

### **Compliance & Risk**
- ✅ Automatic compliance detection
- ✅ Escalation alerts
- ✅ Risk scoring

### **End-to-End Visibility**
- ✅ Bronze → Silver → Gold layers
- ✅ Real-time dashboards
- ✅ Historical analytics

---

## 🛠️ Troubleshooting During Demo

### If Ingestion Fails
- Use SQL fallback: `python scripts/03_zerobus_ingestion_sql.py`
- Show existing data: "We have sample data already ingested"

### If DLT Pipeline Not Running
- Show existing enriched data
- Explain: "Pipeline runs continuously, here's the enriched data"

### If Dashboards Slow
- Refresh page
- Check SQL warehouse is running
- Use cached data if available

### If Escalations Not Showing
- Run: `python scripts/insert_escalation_test_data.py`
- Refresh supervisor dashboard

---

## 📊 Demo Metrics to Highlight

- **Ingestion Speed:** Real-time (every few seconds)
- **Enrichment Speed:** < 5 seconds latency
- **AI Response Time:** < 2 seconds
- **Escalation Detection:** Real-time
- **Dashboard Refresh:** Auto-refresh every 30 seconds

---

## 🎯 Success Criteria

Demo is successful if you can show:
1. ✅ Data flowing from ingestion → Bronze → Silver → Gold
2. ✅ Real-time AI assistance working
3. ✅ Escalations being detected
4. ✅ All 3 dashboards functional
5. ✅ Knowledge base search working
6. ✅ Analytics showing meaningful data

---

## 📝 Post-Demo Follow-Up

### Questions to Prepare For:
- "How does it scale?" → DLT pipelines auto-scale
- "What about data privacy?" → Unity Catalog governance
- "Can we customize?" → All configurable via SQL/Python
- "What's the cost?" → Serverless DLT, pay-per-use

### Next Steps:
- Schedule technical deep-dive
- Provide access credentials
- Share documentation
- Set up production deployment

---

**Demo Duration:** 15-20 minutes  
**Questions:** 5-10 minutes  
**Total:** ~25-30 minutes

