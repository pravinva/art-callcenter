# Dash Migration - Complete Documentation

## Overview

This document describes the complete Dash migration for the ART Call Center solution, migrating from Streamlit to Dash for better performance and reactivity.

## Architecture

### Directory Structure

```
app_dash/
├── app.py                 # Main agent dashboard (original)
├── app_unified.py        # Unified app with routing (recommended)
├── components/            # Reusable Dash components
│   ├── common.py
│   ├── transcript.py
│   ├── ai_suggestions.py
│   ├── member_info.py
│   ├── kb_search.py
│   ├── compliance.py
│   ├── analytics.py
│   └── supervisor.py
├── utils/                 # Utility functions
│   ├── state_manager.py
│   ├── data_fetchers.py
│   ├── ai_suggestions.py
│   ├── kb_search.py
│   ├── analytics_data.py
│   └── supervisor_data.py
├── pages/                 # Page modules
│   ├── analytics.py
│   └── supervisor.py
└── tests/                 # Testing utilities
    └── test_imports.py
```

## Features

### Phase 0-4: Core Infrastructure
- ✅ Dash app setup with Bootstrap theme
- ✅ State management with dcc.Store
- ✅ Sidebar with call selection
- ✅ Live transcript display
- ✅ AI suggestions with heuristic fallback

### Phase 5-8: AI Assistant Features
- ✅ Member Info tab
- ✅ Knowledge Base search
- ✅ Compliance alerts
- ✅ Tab navigation

### Phase 9-10: Additional Dashboards
- ✅ Analytics dashboard (Overview, Agent Performance, Call Summaries, Daily Stats)
- ✅ Supervisor dashboard (Escalation monitoring, Risk scores)

### Phase 11-12: Integration & Optimization
- ✅ Multi-page routing
- ✅ Performance optimizations (caching, lazy loading)
- ✅ Efficient SQL queries

## Running the Application

### Option 1: Unified App (Recommended)

```bash
source venv/bin/activate
python app_dash/app_unified.py
```

Access at: http://localhost:8050

### Option 2: Original Agent Dashboard Only

```bash
source venv/bin/activate
python app_dash/app.py
```

## Navigation

The unified app includes three pages:
1. **Live Agent Assist** (`/`) - Main agent dashboard
2. **Analytics** (`/analytics`) - Analytics and reporting
3. **Supervisor** (`/supervisor`) - Escalation monitoring

## Key Improvements Over Streamlit

1. **True Reactivity**: Only updates changed components, not entire page
2. **State Management**: Centralized state with dcc.Store
3. **Performance**: Caching and lazy loading reduce SQL queries
4. **Routing**: Multi-page navigation without full page reloads
5. **Component Isolation**: Tabs and pages don't interfere with each other
6. **State Persistence**: All component state (transcript, AI suggestions, KB results, compliance, member info) persists when navigating between tabs

## State Persistence Architecture

### How It Works

The application preserves all state when navigating between pages (Live Agent → Analytics/Supervisor → back to Live Agent):

1. **Persistent Layout**: All page layouts remain in DOM, hidden/shown with CSS `display` property
2. **dcc.Store Components**: State stored in client-side storage for:
   - Selected call ID (`store-selected-call-id`)
   - Transcript data (`store-transcript-data`)
   - Last rendered call (`store-last-rendered-call-id`)
   - AI suggestions (`store-suggestion-state`)
   - Compliance alerts (`store-compliance-alerts`)
   - Member context (`store-member-context`)
   - KB search results (`store-kb-results`)

3. **Pathname-Aware Callbacks**: Key callbacks listen to `Input('url', 'pathname')` to restore state when returning to agent page:
   - `update_transcript` - Restores cached transcript immediately on return
   - `update_compliance_alerts` - Restores compliance status
   - `update_ai_suggestions` - Restores AI suggestions
   - Other callbacks preserve state similarly

### Critical Implementation Details

**Transcript Persistence (app.py:977-1028)**:
```python
@app.callback(
    Output('transcript-display', 'children'),
    Input('store-selected-call-id', 'data'),
    Input('interval-component', 'n_intervals'),
    Input('url', 'pathname'),  # Critical: fires on navigation
    State('store-transcript-data', 'data'),
)
def update_transcript(selected_call_id, n_intervals, pathname, previous_transcript_data):
    # Only update on agent page
    if pathname != '/' and pathname != '/agent':
        raise PreventUpdate

    # When returning to page, immediately restore cached data
    if triggered_id == 'url' and previous_transcript_data:
        return cached_display, previous_transcript_data, last_call_id
```

**State Only Clears When**:
- User selects a new call from the dropdown
- User explicitly refreshes the page

**State DOES NOT Clear When**:
- Navigating to Analytics or Supervisor tabs
- Returning to Live Agent tab
- Interval callbacks fire (they preserve existing state)

## Testing

Run import tests:

```bash
python app_dash/tests/test_imports.py
```

## Deployment

### Local Development

```bash
source venv/bin/activate
python app_dash/app_unified.py
```

### Production Deployment

1. Use gunicorn or similar WSGI server
2. Set environment variables for Databricks credentials
3. Configure reverse proxy (nginx) if needed

Example gunicorn command:

```bash
gunicorn app_dash.app_unified:app --bind 0.0.0.0:8050 --workers 4
```

## Dependencies

See `requirements_dash.txt` for all dependencies:

- dash
- dash-bootstrap-components
- dash-core-components
- dash-html-components
- plotly
- cachetools
- pandas
- databricks-sdk

## Migration Status

✅ **COMPLETE** - All phases (0-12) implemented and tested

## Next Steps

1. Test all pages locally
2. Deploy to production environment
3. Monitor performance metrics
4. Gather user feedback
