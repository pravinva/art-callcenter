"""
Transcript Display Components
"""
from dash import html
import dash_bootstrap_components as dbc
from datetime import datetime
import pandas as pd

ART_TEXT_GRAY = "#666666"
ART_LIGHT_BLUE = "#E6F0FF"
ART_WHITE = "#FFFFFF"
ART_PRIMARY_BLUE = "#0051FF"
ART_SUCCESS_GREEN = "#00A651"
ART_BORDER = "#E0E0E0"

def TranscriptBubble(
    speaker: str,
    text: str,
    timestamp: str,
    sentiment: str = "neutral"
) -> html.Div:
    """Individual transcript bubble component - matches Streamlit style"""
    
    # Use same emojis as Streamlit
    speaker_icon = "👤" if speaker == "customer" else "👔"
    speaker_label = "Member" if speaker == "customer" else "Agent"
    
    sentiment_emoji = {
        'positive': '😊',
        'negative': '😟',
        'neutral': '😐'
    }.get(sentiment.lower() if sentiment else 'neutral', '😐')
    
    # Styling to match Streamlit version
    if speaker == "customer":
        bg_color = ART_LIGHT_BLUE
        border_color = ART_PRIMARY_BLUE
        align_style = {"marginLeft": "15%", "marginRight": "0"}
    else:
        bg_color = ART_WHITE
        border_color = ART_SUCCESS_GREEN
        align_style = {"marginRight": "15%", "marginLeft": "0"}
    
    return html.Div([
        html.Div([
            html.Strong(f"{speaker_icon} {speaker_label}"),
            html.Span(f" {sentiment_emoji}", style={"marginLeft": "0.5rem"}),
            html.Small(
                timestamp,
                style={"color": ART_TEXT_GRAY, "marginLeft": "0.5rem"}
            ),
            html.Br(),
            html.Div(text, style={"marginTop": "0.5rem", "lineHeight": "1.6"})
        ], style={
            "background": bg_color,
            "padding": "1rem 1.25rem",
            "borderRadius": "12px",
            "marginBottom": "0.75rem",
            "borderLeft": f"3px solid {border_color}",
            "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.08)",
            "fontSize": "0.95rem",
            "lineHeight": "1.6"
        })
    ], style=align_style)

def TranscriptContainer(transcript_df: pd.DataFrame) -> html.Div:
    """Full transcript container component - matches Streamlit style"""
    if transcript_df is None or transcript_df.empty:
        return dbc.Alert("No transcript data available yet", color="info")
    
    bubbles = []
    for idx, row in transcript_df.iterrows():
        # Format timestamp
        try:
            timestamp_str = pd.to_datetime(row['timestamp']).strftime("%H:%M:%S")
        except:
            timestamp_str = str(row.get('timestamp', ''))
        
        bubble = TranscriptBubble(
            speaker=row.get('speaker', 'customer'),
            text=row.get('transcript_segment', ''),
            timestamp=timestamp_str,
            sentiment=row.get('sentiment', 'neutral')
        )
        bubbles.append(bubble)
    
    return html.Div([
        # Header matching Streamlit style
        html.Div([
            html.Div([
                html.Span("🔴", style={"fontSize": "1.2rem", "marginRight": "0.5rem"}),
                html.Span("Live Call", style={"fontSize": "1.25rem", "fontWeight": "600", "marginRight": "0.5rem"}),
                html.Span("●", style={"color": "#00A651", "fontSize": "0.8rem", "marginRight": "0.5rem"}),
                html.Small("Live", style={"color": "#00A651", "fontWeight": "500"})
            ], style={"display": "flex", "alignItems": "center", "marginBottom": "0.5rem"}),
            html.Div([
                html.Span("👨‍💼 Human Agent Conversation • Active Now", style={"color": ART_TEXT_GRAY, "fontSize": "0.9rem"})
            ])
        ], style={
            "marginBottom": "1.5rem",
            "paddingBottom": "1rem",
            "borderBottom": f"2px solid {ART_BORDER}"
        }),
        html.Div(bubbles, style={"padding": "0.5rem 0"})
    ], style={"padding": "1rem"})

