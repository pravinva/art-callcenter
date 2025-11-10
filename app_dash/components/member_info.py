"""
Member Info Components
"""
from dash import html
import dash_bootstrap_components as dbc

ART_TEXT_GRAY = "#666666"

def create_member_info_display(member_context: list) -> html.Div:
    """Create member info display component"""
    if not member_context or len(member_context) == 0:
        return dbc.Alert("No member context available", color="info")
    
    member_name = member_context[0] if len(member_context) > 0 else "N/A"
    balance_value = member_context[1] if len(member_context) > 1 else None
    transcript_text = member_context[2] if len(member_context) > 2 else "N/A"
    member_id = member_context[3] if len(member_context) > 3 else "N/A"
    recent_interactions = member_context[4] if len(member_context) > 4 else "N/A"
    compliance_issues = member_context[5] if len(member_context) > 5 else "None"
    
    # Format balance
    balance_display = "N/A"
    if balance_value is not None:
        try:
            balance_float = float(balance_value) if isinstance(balance_value, str) else balance_value
            balance_display = f"${balance_float:,.2f}"
        except (ValueError, TypeError):
            balance_display = str(balance_value)
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Member Name", className="text-muted"),
                        html.H4(member_name)
                    ])
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Balance", className="text-muted"),
                        html.H4(balance_display)
                    ])
                ])
            ], width=6)
        ], className="mb-3"),
        
        html.Hr(),
        
        html.H6("Recent Transcript Summary", className="mb-2"),
        html.Div(
            transcript_text if transcript_text != "N/A" else "No transcript available",
            style={
                "background": "#F8F9FA",
                "padding": "1rem",
                "borderRadius": "8px",
                "maxHeight": "200px",
                "overflowY": "auto",
                "fontSize": "0.9rem",
                "lineHeight": "1.6"
            }
        ),
        
        html.Hr(),
        
        dbc.Row([
            dbc.Col([
                html.P([
                    html.Strong("Member ID: "),
                    member_id
                ])
            ], width=6),
            dbc.Col([
                html.P([
                    html.Strong("Compliance Issues: "),
                    compliance_issues
                ])
            ], width=6)
        ])
    ])

