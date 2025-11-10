"""
Compliance Alert Components
"""
from dash import html
import dash_bootstrap_components as dbc

ART_ERROR_RED = "#DC3545"
ART_WARNING_ORANGE = "#FF6B35"
ART_SUCCESS_GREEN = "#00A651"

def create_compliance_alerts_display(alerts: list) -> html.Div:
    """Create compliance alerts display component"""
    if not alerts or len(alerts) == 0:
        return dbc.Alert("✓ No compliance issues detected", color="success")
    
    # Count severity levels
    critical_count = 0
    high_count = 0
    medium_count = 0
    
    alert_cards = []
    
    for alert in alerts:
        if isinstance(alert, (list, tuple)) and len(alert) > 1:
            alert_text = alert[0] if len(alert) > 0 else str(alert)
            severity = str(alert[1]).upper() if len(alert) > 1 else "MEDIUM"
        else:
            alert_text = str(alert)
            severity = "CRITICAL" if "CRITICAL" in alert_text.upper() else "HIGH" if "HIGH" in alert_text.upper() else "MEDIUM"
        
        # Count by severity
        if severity == "CRITICAL":
            critical_count += 1
            color = "danger"
        elif severity == "HIGH":
            high_count += 1
            color = "warning"
        else:
            medium_count += 1
            color = "info"
        
        alert_cards.append(
            dbc.Alert(
                alert_text,
                color=color,
                className="mb-2"
            )
        )
    
    # Summary
    summary = html.Div([
        html.H6("Compliance Summary", className="mb-2"),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4(str(critical_count), style={"color": ART_ERROR_RED, "margin": 0}),
                    html.P("Critical", className="text-muted mb-0", style={"fontSize": "0.85rem"})
                ])
            ], width=4),
            dbc.Col([
                html.Div([
                    html.H4(str(high_count), style={"color": ART_WARNING_ORANGE, "margin": 0}),
                    html.P("High", className="text-muted mb-0", style={"fontSize": "0.85rem"})
                ])
            ], width=4),
            dbc.Col([
                html.Div([
                    html.H4(str(medium_count), style={"color": "#17a2b8", "margin": 0}),
                    html.P("Medium", className="text-muted mb-0", style={"fontSize": "0.85rem"})
                ])
            ], width=4)
        ], className="mb-3")
    ])
    
    return html.Div([
        summary,
        html.Hr(),
        html.Div(alert_cards)
    ])

