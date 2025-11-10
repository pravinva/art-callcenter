"""
Supervisor Dashboard Page
Dash page for supervisor monitoring and escalations
"""
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from app_dash.utils.supervisor_data import (
    get_all_active_calls, get_calls_with_escalations_batch, get_escalation_summary
)
from app_dash.components.supervisor import (
    create_active_calls_list, create_escalation_summary
)
from app_dash.components.common import ErrorAlert

def create_supervisor_layout():
    """Create supervisor dashboard layout"""
    return html.Div([
        html.H1("👔 Supervisor Dashboard", className="mb-4"),
        html.P("Real-time call monitoring and escalation management", className="text-muted mb-4"),
        html.Hr(),
        
        # Summary metrics
        html.Div(id="supervisor-summary"),
        
        # Active calls list
        html.H3("Active Calls", className="mt-4 mb-3"),
        html.Div(id="supervisor-active-calls"),
        
        # Stores
        dcc.Store(id="store-supervisor-calls"),
        dcc.Store(id="store-supervisor-escalations"),
        
        # Interval for auto-refresh (30 seconds)
        dcc.Interval(id="supervisor-interval", interval=30000, n_intervals=0)
    ])

def register_supervisor_callbacks(app):
    """Register supervisor dashboard callbacks"""
    
    @app.callback(
        Output('supervisor-summary', 'children'),
        Output('supervisor-active-calls', 'children'),
        Output('store-supervisor-calls', 'data'),
        Output('store-supervisor-escalations', 'data'),
        Input('supervisor-interval', 'n_intervals'),
        prevent_initial_call=True
    )
    def update_supervisor_dashboard(n_intervals):
        """Update supervisor dashboard"""
        try:
            # Get active calls
            active_calls_df = get_all_active_calls()
            
            if active_calls_df is None or active_calls_df.empty:
                summary = create_escalation_summary({
                    'total_active_calls': 0,
                    'total_negative_sentiments': 0,
                    'total_compliance_issues': 0,
                    'total_complaints': 0
                })
                calls_display = dbc.Alert("No active calls", color="info")
                return summary, calls_display, [], {}
            
            # Get escalation data for all calls
            call_ids = active_calls_df['call_id'].tolist()
            escalation_dict = get_calls_with_escalations_batch(call_ids)
            
            # Get summary
            summary_data = get_escalation_summary()
            summary = create_escalation_summary(summary_data)
            
            # Create calls list
            calls_display = create_active_calls_list(active_calls_df, escalation_dict)
            
            # Store data
            calls_data = active_calls_df.to_dict('records') if not active_calls_df.empty else []
            
            return summary, calls_display, calls_data, escalation_dict
        except Exception as e:
            return ErrorAlert(f"Error loading supervisor dashboard: {e}"), html.Div(), [], {}

