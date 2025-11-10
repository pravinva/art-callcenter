# Quick Demo Reference Card

## 🚀 5-Minute Quick Start Demo

### 1. Data Ingestion (30 sec)
```bash
python scripts/03_zerobus_ingestion_sql.py
```
**Show:** Raw transcripts in Bronze layer

### 2. Silver Processing (30 sec)
**Show:** Enriched transcripts with sentiment/intent/compliance
```sql
SELECT call_id, sentiment, intent_category, compliance_flag 
FROM member_analytics.call_center.enriched_transcripts 
ORDER BY enriched_at DESC LIMIT 5;
```

### 3. Live Agent Dashboard (2 min)
- Select active call
- Show real-time transcript
- Click "AI Suggest" → Show suggestions
- Search KB: "contribution limits"

### 4. Supervisor Dashboard (1 min)
- Show 2 escalation alerts
- Explain risk scores
- Filter by escalation

### 5. Analytics Dashboard (1 min)
- Show daily stats
- Show charts
- Show call summaries

---

## 🎯 Key Talking Points

**Real-Time:** "Data flows in seconds, not minutes"  
**AI-Powered:** "Context-aware suggestions help agents"  
**Compliance:** "Automatic detection and escalation"  
**End-to-End:** "Bronze → Silver → Gold → Dashboards"

---

## 🔧 Quick Troubleshooting

**No data?** → Run `python scripts/03_zerobus_ingestion_sql.py`  
**No escalations?** → Run `python scripts/insert_escalation_test_data.py`  
**Slow dashboard?** → Refresh page  
**KB empty?** → Run `python scripts/populate_kb_articles.py`

---

## 📊 Demo URLs

- **Live Agent Dashboard:** http://localhost:8520
- **Supervisor Dashboard:** Navigate via sidebar
- **Analytics Dashboard:** Navigate via sidebar

---

**Total Time:** 5 minutes (quick) or 15-20 minutes (full)

