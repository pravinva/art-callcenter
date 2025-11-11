"""
Supervisor Dashboard Page
Dash page for supervisor monitoring and escalations
"""
from dash import html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app_dash.utils.supervisor_data import (
    get_all_active_calls, get_calls_with_escalations_batch, get_escalation_summary
)
from app_dash.components.supervisor import (
    create_active_calls_list, create_escalation_summary, create_escalation_summary_tabs
)
from app_dash.components.common import ErrorAlert

def create_supervisor_layout():
    """Create supervisor dashboard layout"""
    return dbc.Container([
        html.H1("👔 Supervisor Dashboard", className="mb-4"),
        html.P("Real-time call monitoring and escalation management", className="text-muted mb-4"),
        html.Hr(),
        
        # Summary metrics tabs (will be populated with data) - with loading spinner
        dcc.Loading(
            id="supervisor-summary-loading",
            type="default",
            children=html.Div(id="supervisor-summary"),
            style={"minHeight": "200px"}
        ),
        
        # Tab content area - with loading spinner
        dcc.Loading(
            id="supervisor-tab-loading",
            type="default",
            children=html.Div(id="supervisor-tab-content", className="mt-4"),
            style={"minHeight": "300px"}
        ),
        
        # Stores
        dcc.Store(id="store-supervisor-calls"),
        dcc.Store(id="store-supervisor-escalations"),
        dcc.Store(id="store-supervisor-summary-data"),
        
        # Interval for auto-refresh (30 seconds)
        dcc.Interval(id="supervisor-interval", interval=30000, n_intervals=0)
    ], fluid=True, style={"padding": "2rem"})

def register_supervisor_callbacks(app):
    """Register supervisor dashboard callbacks"""
    
    @app.callback(
        Output('supervisor-summary', 'children'),
        Output('store-supervisor-calls', 'data'),
        Output('store-supervisor-escalations', 'data'),
        Output('store-supervisor-summary-data', 'data'),
        Input('supervisor-interval', 'n_intervals'),
        Input('url', 'pathname')  # Also trigger when navigating to supervisor page
    )
    def update_supervisor_dashboard(n_intervals, pathname):
        """Update supervisor dashboard summary tabs"""
        # Only update when on supervisor page
        if pathname != '/supervisor':
            raise PreventUpdate
        
        try:
            # Get active calls
            active_calls_df = get_all_active_calls()
            
            if active_calls_df is None or active_calls_df.empty:
                summary_data = {
                    'total_active_calls': 0,
                    'total_negative_sentiments': 0,
                    'total_compliance_issues': 0,
                    'total_complaints': 0
                }
                summary = create_escalation_summary_tabs(summary_data)
                # Add helpful message about no recent data
                empty_message = dbc.Alert([
                    html.H5("📊 No Active Calls in Last 10 Minutes", className="mb-2"),
                    html.P("The supervisor dashboard shows calls from the last 10 minutes. This could mean:", className="mb-2"),
                    html.Ul([
                        html.Li("No calls are currently active"),
                        html.Li("The enrichment pipeline may not be running"),
                        html.Li("Data may be older than 10 minutes")
                    ]),
                    html.Hr(),
                    html.P([
                        html.Strong("💡 Tip: "),
                        "Check the pipeline status in Databricks UI or extend the time window for demo purposes."
                    ], className="mb-0")
                ], color="info", className="mt-3")
                return html.Div([summary, empty_message]), [], {}, summary_data
            
            # Get escalation data for all calls
            call_ids = active_calls_df['call_id'].tolist()
            escalation_dict = get_calls_with_escalations_batch(call_ids)
            
            # Get summary
            summary_data = get_escalation_summary()
            summary = create_escalation_summary_tabs(summary_data)
            
            # Store data
            calls_data = active_calls_df.to_dict('records') if not active_calls_df.empty else []
            
            return summary, calls_data, escalation_dict, summary_data
        except Exception as e:
            import traceback
            error_msg = f"Error loading supervisor dashboard: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            return ErrorAlert(error_msg), [], {}, {}
    
    @app.callback(
        Output('supervisor-tab-content', 'children'),
        Input('supervisor-tabs', 'active_tab'),
        State('store-supervisor-calls', 'data'),
        State('store-supervisor-escalations', 'data'),
        State('store-supervisor-summary-data', 'data')
    )
    def update_supervisor_tab_content(active_tab, calls_data, escalation_dict, summary_data):
        """Update content based on selected tab"""
        if not calls_data or not escalation_dict:
            return dbc.Alert([
                html.H5("📊 No Data Available", className="mb-2"),
                html.P("No active calls found in the last 10 minutes. The dashboard will update automatically when new calls are detected.", className="mb-0")
            ], color="info")
        
        import pandas as pd
        active_calls_df = pd.DataFrame(calls_data)
        
        if active_tab == 'all-calls':
            # Show all active calls
            return html.Div([
                html.H4("All Active Calls", className="mb-3"),
                create_active_calls_list(active_calls_df, escalation_dict)
            ])
        elif active_tab == 'negative-sentiment':
            # Filter calls with negative sentiment
            filtered_calls = []
            for call_id in escalation_dict:
                if escalation_dict[call_id].get('negative_sentiment_count', 0) > 0:
                    call_row = active_calls_df[active_calls_df['call_id'] == call_id]
                    if not call_row.empty:
                        filtered_calls.append(call_row.iloc[0])
            
            if filtered_calls:
                filtered_df = pd.DataFrame(filtered_calls)
                return html.Div([
                    html.H4(f"Calls with Negative Sentiment ({len(filtered_calls)})", className="mb-3"),
                    create_active_calls_list(filtered_df, escalation_dict)
                ])
            else:
                return dbc.Alert("No calls with negative sentiment", color="info")
        elif active_tab == 'compliance-issues':
            # Filter calls with compliance issues
            filtered_calls = []
            for call_id in escalation_dict:
                if escalation_dict[call_id].get('compliance_violations_count', 0) > 0:
                    call_row = active_calls_df[active_calls_df['call_id'] == call_id]
                    if not call_row.empty:
                        filtered_calls.append(call_row.iloc[0])
            
            if filtered_calls:
                filtered_df = pd.DataFrame(filtered_calls)
                return html.Div([
                    html.H4(f"Calls with Compliance Issues ({len(filtered_calls)})", className="mb-3"),
                    create_active_calls_list(filtered_df, escalation_dict)
                ])
            else:
                return dbc.Alert("No calls with compliance issues", color="info")
        elif active_tab == 'complaints':
            # Filter calls with complaints
            filtered_calls = []
            for call_id in escalation_dict:
                if escalation_dict[call_id].get('complaint_intent_count', 0) > 0:
                    call_row = active_calls_df[active_calls_df['call_id'] == call_id]
                    if not call_row.empty:
                        filtered_calls.append(call_row.iloc[0])
            
            if filtered_calls:
                filtered_df = pd.DataFrame(filtered_calls)
                return html.Div([
                    html.H4(f"Calls with Complaints ({len(filtered_calls)})", className="mb-3"),
                    create_active_calls_list(filtered_df, escalation_dict)
                ])
            else:
                return dbc.Alert("No calls with complaints", color="info")
        
        return html.Div()

