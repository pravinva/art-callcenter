"""
Transcript Display Components
"""
from dash import html
import dash_bootstrap_components as dbc
from datetime import datetime
import pandas as pd

ART_TEXT_GRAY = "#666666"

def TranscriptBubble(
    speaker: str,
    text: str,
    timestamp: str,
    sentiment: str = "neutral"
) -> html.Div:
    """Individual transcript bubble component"""
    
    speaker_icon = "👤" if speaker == "customer" else "👔"
    speaker_label = "Member" if speaker == "customer" else "Agent"
    
    sentiment_emoji = {
        'positive': '😊',
        'negative': '😟',
        'neutral': '😐'
    }.get(sentiment, '😐')
    
    bubble_class = "transcript-customer" if speaker == "customer" else "transcript-agent"
    bg_color = "#E6F0FF" if speaker == "customer" else "#F0F0F0"
    align = "flex-start" if speaker == "customer" else "flex-end"
    
    return html.Div([
        html.Div([
            html.Strong(f"{speaker_icon} {speaker_label}"),
            html.Span(f" {sentiment_emoji}", style={"marginLeft": "0.5rem"}),
            html.Small(
                timestamp,
                style={"color": ART_TEXT_GRAY, "marginLeft": "0.5rem"}
            ),
            html.Br(),
            html.Div(text, style={"marginTop": "0.5rem"})
        ], style={
            "background": bg_color,
            "padding": "1rem",
            "borderRadius": "12px",
            "marginBottom": "0.75rem",
            "maxWidth": "80%",
            "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
        })
    ], style={"display": "flex", "justifyContent": align, "width": "100%"})

def TranscriptContainer(transcript_df: pd.DataFrame) -> html.Div:
    """Full transcript container component"""
    if transcript_df is None or transcript_df.empty:
        return dbc.Alert("No transcript data available yet", color="info")
    
    bubbles = []
    for idx, row in transcript_df.iterrows():
        timestamp_str = pd.to_datetime(row['timestamp']).strftime("%H:%M:%S")
        bubble = TranscriptBubble(
            speaker=row['speaker'],
            text=row['transcript_segment'],
            timestamp=timestamp_str,
            sentiment=row.get('sentiment', 'neutral')
        )
        bubbles.append(bubble)
    
    return html.Div(bubbles, style={"padding": "1rem"})

