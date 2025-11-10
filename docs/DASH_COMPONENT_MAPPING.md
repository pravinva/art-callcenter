# Streamlit to Dash Component Mapping Reference

## Layout Components

| Streamlit | Dash Equivalent | Notes |
|-----------|----------------|-------|
| `st.columns([3, 2.5])` | `dbc.Row([dbc.Col(..., width=6), dbc.Col(..., width=5)])` | Use Bootstrap grid |
| `st.sidebar` | `dbc.Offcanvas()` or separate `dbc.Col()` | Offcanvas for mobile |
| `st.tabs(["Tab1", "Tab2"])` | `dbc.Tabs([dbc.Tab(...), dbc.Tab(...)])` | Native tabs |
| `st.container()` | `html.Div()` | Simple container |

## Input Components

| Streamlit | Dash Equivalent | Notes |
|-----------|----------------|-------|
| `st.button("Click")` | `dbc.Button("Click", id="btn", n_clicks=0)` | Use `n_clicks` in callback |
| `st.text_input("Label")` | `dcc.Input(id="input", type="text", value="")` | Use `value` prop |
| `st.selectbox("Label", options)` | `dcc.Dropdown(id="dropdown", options=options)` | Use `value` prop |
| `st.radio("Label", options)` | `dbc.RadioItems(id="radio", options=options)` | Use `value` prop |
| `st.checkbox("Label")` | `dbc.Checkbox(id="checkbox", value=False)` | Use `value` prop |

## Display Components

| Streamlit | Dash Equivalent | Notes |
|-----------|----------------|-------|
| `st.markdown("text")` | `html.Div("text", dangerously_allow_html=True)` | For HTML |
| `st.markdown("text")` | `dcc.Markdown("text")` | For markdown |
| `st.empty()` | `html.Div(id="placeholder")` | Update via callback |
| `st.metric("Label", value)` | `dbc.Card([dbc.CardBody([html.H4(value), html.P("Label")])])` | Custom card |
| `st.info("message")` | `dbc.Alert("message", color="info")` | Alert component |
| `st.error("message")` | `dbc.Alert("message", color="danger")` | Alert component |
| `st.success("message")` | `dbc.Alert("message", color="success")` | Alert component |
| `st.warning("message")` | `dbc.Alert("message", color="warning")` | Alert component |
| `st.spinner("Loading...")` | `dbc.Spinner(html.Div(id="content"), fullscreen=True)` | Loading spinner |

## Data Display

| Streamlit | Dash Equivalent | Notes |
|-----------|----------------|-------|
| `st.dataframe(df)` | `dash_table.DataTable(data=df.to_dict('records'))` | Data table |
| `st.plotly_chart(fig)` | `dcc.Graph(figure=fig)` | Plotly charts |

## State Management

| Streamlit | Dash Equivalent | Notes |
|-----------|----------------|-------|
| `st.session_state['key']` | `dcc.Store(id='store-key', data={})` | Client-side storage |
| `st.cache_data` | `@lru_cache` or manual caching | Server-side caching |
| `st.cache_resource` | `@lru_cache` or singleton | Resource caching |

## Callbacks

| Streamlit | Dash Equivalent | Notes |
|-----------|----------------|-------|
| `on_change=callback` | `@app.callback(Output(...), Input(...))` | True reactive callbacks |
| `st.rerun()` | Not needed - automatic | Dash handles updates |

## Special Patterns

### Conditional Rendering
```python
# Streamlit
if condition:
    st.write("Content")

# Dash
html.Div([
    html.Div("Content", id="content", style={"display": "none" if not condition else "block"})
])
```

### Dynamic Updates
```python
# Streamlit
placeholder = st.empty()
placeholder.write("Updated")

# Dash
@app.callback(
    Output('placeholder', 'children'),
    Input('trigger', 'n_clicks')
)
def update_content(n_clicks):
    return "Updated"
```

### Interval Updates
```python
# Streamlit
if st.checkbox("Auto-refresh"):
    time.sleep(5)
    st.rerun()

# Dash
dcc.Interval(id='interval', interval=5000, n_intervals=0)

@app.callback(
    Output('content', 'children'),
    Input('interval', 'n_intervals')
)
def update_on_interval(n):
    return fetch_data()
```

