"""
Member Info Components
"""
from dash import html
import dash_bootstrap_components as dbc

ART_TEXT_GRAY = "#666666"
ART_PRIMARY_BLUE = "#0051FF"
ART_LIGHT_BLUE = "#E6F0FF"

def create_member_info_display(member_context: list) -> html.Div:
    """Create member info display component - matches Streamlit structure"""
    if not member_context or len(member_context) == 0:
        return dbc.Alert("No member context available", color="info")
    
    # Data structure from get_call_context function:
    # [0] = member_name
    # [1] = balance
    # [2] = transcript_text
    # [3] = sentiment
    # [4] = intents (comma-separated)
    # [5] = compliance_issues (comma-separated)
    
    member_name = member_context[0] if len(member_context) > 0 else "N/A"
    balance_value = member_context[1] if len(member_context) > 1 else None
    transcript_text = member_context[2] if len(member_context) > 2 else "N/A"
    sentiment = member_context[3] if len(member_context) > 3 else "N/A"
    intents = member_context[4] if len(member_context) > 4 else "N/A"
    compliance_issues = member_context[5] if len(member_context) > 5 else "None"
    
    # Format balance
    balance_display = "N/A"
    if balance_value is not None:
        try:
            balance_float = float(balance_value) if isinstance(balance_value, str) else balance_value
            balance_display = f"${balance_float:,.2f}"
        except (ValueError, TypeError):
            balance_display = str(balance_value)
    
    # Format sentiment with color
    sentiment_color = {
        "positive": "#00A651",
        "negative": "#DC3545",
        "neutral": "#666666"
    }.get(sentiment.lower(), "#666666")
    
    # Format intents (comma-separated string)
    intents_display = intents if intents != "N/A" else "None"
    if isinstance(intents_display, str) and intents_display != "None":
        # Split by comma and create badges
        intent_list = [i.strip() for i in intents_display.split(",") if i.strip()]
        intent_badges = [
            dbc.Badge(intent, color="primary", className="me-1 mb-1", style={"fontSize": "0.75rem"})
            for intent in intent_list
        ]
    else:
        intent_badges = [html.Span("None", className="text-muted")]
    
    # Format compliance issues (comma-separated string)
    compliance_display = compliance_issues if compliance_issues != "None" else "None"
    if isinstance(compliance_display, str) and compliance_display != "None":
        # Split by comma and create badges
        compliance_list = [c.strip() for c in compliance_display.split(",") if c.strip()]
        compliance_badges = [
            dbc.Badge(issue, color="danger", className="me-1 mb-1", style={"fontSize": "0.75rem"})
            for issue in compliance_list
        ]
    else:
        compliance_badges = [html.Span("None", className="text-success")]
    
    return html.Div([
        # Member Name and Balance Cards
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Member Name", className="text-muted mb-2"),
                        html.H4(member_name, style={"margin": 0})
                    ])
                ])
            ], width=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Balance", className="text-muted mb-2"),
                        html.H4(balance_display, style={"margin": 0})
                    ])
                ])
            ], width=6)
        ], className="mb-3"),
        
        html.Hr(),
        
        # Recent Transcript Summary
        html.H6("Recent Transcript Summary", className="mb-2"),
        html.Div(
            transcript_text if transcript_text != "N/A" else "No transcript available",
            style={
                "background": ART_LIGHT_BLUE,
                "padding": "1rem",
                "borderRadius": "8px",
                "borderLeft": f"3px solid {ART_PRIMARY_BLUE}",
                "maxHeight": "200px",
                "overflowY": "auto",
                "fontSize": "0.9rem",
                "lineHeight": "1.6"
            }
        ),
        
        html.Hr(),
        
        # Sentiment, Intents, and Compliance
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Strong("Sentiment: ", style={"fontSize": "0.9rem"}),
                    html.Span(
                        sentiment,
                        style={
                            "color": sentiment_color,
                            "fontWeight": "600",
                            "fontSize": "0.9rem"
                        }
                    )
                ])
            ], width=12, className="mb-2"),
            dbc.Col([
                html.Div([
                    html.Strong("Intents: ", style={"fontSize": "0.9rem", "display": "block", "marginBottom": "0.5rem"}),
                    html.Div(intent_badges, style={"display": "flex", "flexWrap": "wrap"})
                ])
            ], width=12, className="mb-2"),
            dbc.Col([
                html.Div([
                    html.Strong("Compliance Issues: ", style={"fontSize": "0.9rem", "display": "block", "marginBottom": "0.5rem"}),
                    html.Div(compliance_badges, style={"display": "flex", "flexWrap": "wrap"})
                ])
            ], width=12)
        ])
    ])

