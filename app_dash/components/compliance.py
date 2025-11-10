"""
Compliance Alert Components - Compact with categorized summaries
"""
from dash import html
import dash_bootstrap_components as dbc
from collections import defaultdict

ART_ERROR_RED = "#DC3545"
ART_WARNING_ORANGE = "#FF6B35"
ART_SUCCESS_GREEN = "#00A651"

def categorize_alert(alert_text: str) -> str:
    """Categorize alert by type"""
    alert_lower = alert_text.lower()
    
    if 'privacy' in alert_lower or 'personal information' in alert_lower or 'pii' in alert_lower:
        return 'Privacy'
    elif 'financial' in alert_lower or 'payment' in alert_lower or 'money' in alert_lower:
        return 'Financial'
    elif 'disclosure' in alert_lower or 'disclose' in alert_lower:
        return 'Disclosure'
    elif 'consent' in alert_lower or 'authorization' in alert_lower:
        return 'Consent'
    elif 'record' in alert_lower or 'documentation' in alert_lower:
        return 'Documentation'
    elif 'escalation' in alert_lower or 'supervisor' in alert_lower:
        return 'Escalation'
    else:
        return 'General'

def create_compliance_alerts_display(alerts: list) -> html.Div:
    """Create compact compliance alerts display with categorized summaries"""
    if not alerts or len(alerts) == 0:
        return dbc.Alert(
            "✓ No compliance issues detected",
            color="success",
            className="mb-0",
            style={"fontSize": "0.9rem", "padding": "0.75rem"}
        )
    
    # Group alerts by category and severity
    categorized = defaultdict(lambda: {'critical': [], 'high': [], 'medium': [], 'low': []})
    severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    
    for alert in alerts:
        if isinstance(alert, (list, tuple)) and len(alert) > 1:
            alert_text = alert[0] if len(alert) > 0 else str(alert)
            severity = str(alert[1]).upper() if len(alert) > 1 else "MEDIUM"
        else:
            alert_text = str(alert)
            severity = "CRITICAL" if "CRITICAL" in alert_text.upper() else "HIGH" if "HIGH" in alert_text.upper() else "MEDIUM"
        
        category = categorize_alert(alert_text)
        severity_lower = severity.lower()
        
        # Normalize severity levels - map 'low' to 'medium' for display
        if severity_lower == 'low':
            severity_lower = 'medium'
        
        # Ensure severity is valid
        if severity_lower not in ['critical', 'high', 'medium']:
            severity_lower = 'medium'  # Default to medium if unknown
        
        categorized[category][severity_lower].append(alert_text)
        severity_counts[severity_lower] += 1
    
    # Create compact summary cards
    summary_cards = []
    
    if severity_counts['critical'] > 0:
        summary_cards.append(
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.H5(str(severity_counts['critical']), style={
                            "color": ART_ERROR_RED,
                            "margin": 0,
                            "fontSize": "1.5rem",
                            "fontWeight": "700"
                        }),
                        html.P("Critical", style={
                            "margin": 0,
                            "fontSize": "0.75rem",
                            "color": "#666",
                            "textTransform": "uppercase",
                            "letterSpacing": "0.5px"
                        })
                    ], style={"textAlign": "center"})
                ], style={"padding": "0.75rem"})
            ], color="danger", outline=True, className="mb-2")
        )
    
    if severity_counts['high'] > 0:
        summary_cards.append(
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.H5(str(severity_counts['high']), style={
                            "color": ART_WARNING_ORANGE,
                            "margin": 0,
                            "fontSize": "1.5rem",
                            "fontWeight": "700"
                        }),
                        html.P("High", style={
                            "margin": 0,
                            "fontSize": "0.75rem",
                            "color": "#666",
                            "textTransform": "uppercase",
                            "letterSpacing": "0.5px"
                        })
                    ], style={"textAlign": "center"})
                ], style={"padding": "0.75rem"})
            ], color="warning", outline=True, className="mb-2")
        )
    
    if severity_counts['medium'] > 0:
        summary_cards.append(
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.H5(str(severity_counts['medium']), style={
                            "color": "#17a2b8",
                            "margin": 0,
                            "fontSize": "1.5rem",
                            "fontWeight": "700"
                        }),
                        html.P("Medium", style={
                            "margin": 0,
                            "fontSize": "0.75rem",
                            "color": "#666",
                            "textTransform": "uppercase",
                            "letterSpacing": "0.5px"
                        })
                    ], style={"textAlign": "center"})
                ], style={"padding": "0.75rem"})
            ], color="info", outline=True, className="mb-2")
        )
    
    # Create categorized details (compact)
    category_sections = []
    
    for category in sorted(categorized.keys()):
        category_alerts = categorized[category]
        total_in_category = sum(len(category_alerts[s]) for s in ['critical', 'high', 'medium'])
        
        if total_in_category == 0:
            continue
        
        # Count by severity for this category
        cat_critical = len(category_alerts['critical'])
        cat_high = len(category_alerts['high'])
        cat_medium = len(category_alerts['medium'])
        
        # Determine color based on highest severity
        if cat_critical > 0:
            badge_color = "danger"
        elif cat_high > 0:
            badge_color = "warning"
        else:
            badge_color = "info"
        
        # Create compact category summary
        severity_badges = []
        if cat_critical > 0:
            severity_badges.append(
                dbc.Badge(f"{cat_critical} Critical", color="danger", className="me-1", style={"fontSize": "0.7rem"})
            )
        if cat_high > 0:
            severity_badges.append(
                dbc.Badge(f"{cat_high} High", color="warning", className="me-1", style={"fontSize": "0.7rem"})
            )
        if cat_medium > 0:
            severity_badges.append(
                dbc.Badge(f"{cat_medium} Medium", color="info", className="me-1", style={"fontSize": "0.7rem"})
            )
        
        # Get first alert text as summary
        first_alert = None
        if category_alerts['critical']:
            first_alert = category_alerts['critical'][0]
        elif category_alerts['high']:
            first_alert = category_alerts['high'][0]
        elif category_alerts['medium']:
            first_alert = category_alerts['medium'][0]
        
        category_sections.append(
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Div([
                            html.Strong(category, style={"fontSize": "0.85rem", "color": "#333"}),
                            html.Div(severity_badges, style={"marginTop": "0.25rem"})
                        ], style={"flex": 1}),
                        html.Div([
                            html.P(
                                first_alert[:80] + "..." if first_alert and len(first_alert) > 80 else (first_alert or ""),
                                style={
                                    "margin": 0,
                                    "fontSize": "0.75rem",
                                    "color": "#666",
                                    "marginTop": "0.5rem"
                                }
                            )
                        ])
                    ])
                ], style={"padding": "0.75rem"})
            ], outline=True, className="mb-2", style={"borderLeft": f"3px solid {ART_ERROR_RED if cat_critical > 0 else ART_WARNING_ORANGE if cat_high > 0 else '#17a2b8'}"})
        )
    
    return html.Div([
        # Summary row
        dbc.Row([
            dbc.Col(card, width=4 if len(summary_cards) == 3 else (6 if len(summary_cards) == 2 else 12))
            for card in summary_cards
        ], className="mb-3 g-2"),
        
        # Categorized details (compact)
        html.Div(category_sections, style={"maxHeight": "300px", "overflowY": "auto"})
    ], style={"fontSize": "0.9rem"})

