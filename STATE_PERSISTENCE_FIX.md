# State Persistence Fix - Live Agent Assist Dashboard

## Problem
When navigating between tabs (Live Agent → Analytics/Supervisor → back to Live Agent), all state was lost:
- Dropdown selection cleared
- Call transcript disappeared
- AI suggestions cleared
- KB search results cleared
- Compliance status cleared
- Member info cleared
- Escalation status cleared

## Root Cause
Streamlit multi-page apps don't automatically persist state between pages. Each page rerun starts with a clean slate unless data is explicitly stored in `st.session_state`.

## Solution Applied

### 1. Session State Initialization (Lines 584-596)
Added initialization of all critical session state variables at the start of the page:
```python
if 'selected_call_id' not in st.session_state:
    st.session_state['selected_call_id'] = None
if 'transcript_data' not in st.session_state:
    st.session_state['transcript_data'] = None
if 'member_context' not in st.session_state:
    st.session_state['member_context'] = None
if 'escalation_data' not in st.session_state:
    st.session_state['escalation_data'] = None
if 'compliance_alerts' not in st.session_state:
    st.session_state['compliance_alerts'] = None
if 'call_metrics' not in st.session_state:
    st.session_state['call_metrics'] = None
```

### 2. Persistent Call Selection (Lines 615-643)
- Dropdown now remembers the selected call across page navigations
- Pre-selects the previously chosen call when returning to Live Agent tab
- Clears cached data only when a NEW call is selected
```python
# Get previously selected call if it exists
if st.session_state['selected_call_id'] and st.session_state['selected_call_id'] in call_options.values():
    # Find the display name for the selected call
    selected_display = next((k for k, v in call_options.items() if v == st.session_state['selected_call_id']), list(call_options.keys())[0])
    default_index = list(call_options.keys()).index(selected_display) if selected_display in call_options else 0
```

### 3. Loading Spinners for All Data Sections

#### Transcript (Lines 675-682)
```python
if st.session_state['transcript_data'] is None or st.session_state.get('transcript_call_id') != selected_call_id:
    with st.spinner("🔄 Loading transcript..."):
        transcript_df = get_live_transcript(selected_call_id)
        st.session_state['transcript_data'] = transcript_df
        st.session_state['transcript_call_id'] = selected_call_id
else:
    transcript_df = st.session_state['transcript_data']
```

#### Member Info (Lines 783-790)
```python
if st.session_state['member_context'] is None or st.session_state.get('member_context_call_id') != selected_call_id:
    with st.spinner("🔄 Loading member info..."):
        query = f"SELECT * FROM {FUNCTION_GET_CALL_CONTEXT}('{selected_call_id}')"
        results = execute_sql(query, return_dataframe=False)
        st.session_state['member_context'] = results
        st.session_state['member_context_call_id'] = selected_call_id
```

#### Escalation Status (Lines 861-867)
```python
if st.session_state['escalation_data'] is None or st.session_state.get('escalation_call_id') != selected_call_id:
    with st.spinner("🔄 Loading escalation status..."):
        escalation_data = get_escalation_triggers(selected_call_id)
        st.session_state['escalation_data'] = escalation_data
        st.session_state['escalation_call_id'] = selected_call_id
```

#### Compliance Alerts (Lines 917-923)
```python
if st.session_state['compliance_alerts'] is None or st.session_state.get('compliance_call_id') != selected_call_id:
    with st.spinner("🔄 Loading compliance alerts..."):
        alerts = get_compliance_alerts(selected_call_id)
        st.session_state['compliance_alerts'] = alerts
        st.session_state['compliance_call_id'] = selected_call_id
```

#### Call Metrics (Lines 963-968)
```python
if st.session_state['transcript_data'] is not None:
    transcript_df = st.session_state['transcript_data']
else:
    with st.spinner("🔄 Loading metrics..."):
        transcript_df = get_live_transcript(selected_call_id)
        st.session_state['transcript_data'] = transcript_df
```

## Benefits

1. **State Persistence**: All data persists when switching between tabs
2. **Performance**: Cached data loads instantly when returning to Live Agent tab
3. **User Experience**: Loading spinners provide feedback during data fetches
4. **Efficiency**: Data is only reloaded when:
   - First time accessing the page
   - Selecting a different call
   - Data hasn't been cached yet

## Testing Instructions

1. Start the Streamlit app:
   ```bash
   cd /Users/pravin.varma/Documents/Demo/art-callcenter
   streamlit run app/pages/01_Live_Agent_Assist.py
   ```

2. Select a call from the dropdown
3. Wait for all data to load (transcript, member info, etc.)
4. Click "Get AI Suggestion" and search KB
5. Navigate to Analytics or Supervisor tab
6. Return to Live Agent tab
7. **Verify**: All data should still be present:
   - Same call selected in dropdown
   - Transcript still visible
   - Member info still loaded
   - AI suggestions still displayed
   - KB search results still shown
   - Compliance alerts still present
   - Escalation status still visible

## Files Modified

- `app/pages/01_Live_Agent_Assist.py` - Main live agent assist page

## Additional Notes

- KB results were already being persisted (lines 779-785) so no changes needed
- AI suggestions use a separate caching mechanism with `st.session_state['last_suggestion']` which continues to work
- The fix is backward compatible - existing functionality unchanged
- Loading spinners only show when data needs to be fetched, providing smooth UX

## Future Improvements

Consider adding:
1. Cache expiration (TTL) for auto-refresh of stale data
2. Manual refresh button for each section
3. Visual indicator showing data age
4. Preload data for likely-to-be-selected calls
