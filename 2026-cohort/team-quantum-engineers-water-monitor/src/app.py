"""
===========================================================
AquaWatch Naija (Dash version)
Hyperlocal Water Quality Monitor Portal

Grow with Google x Mentor Me Collective
UN SDG 6 - Clean Water and Sanitation
===========================================================
"""

import pandas as pd
from dash import Dash, dcc, html, dash_table, Input, Output, State

from utils import load_data, apply_filters, calculate_metrics
from charts import (
    risk_distribution_chart,
    water_source_chart,
    ph_region_chart,
    turbidity_region_chart,
    contaminant_chart,
    bacteria_chart,
    yearly_trend_chart,
    regional_risk_chart,
)
from map_utils import create_map

# --------------------------------------------------------
# LOAD DATA (once, at startup)
# --------------------------------------------------------

df = load_data("nigeria_combined_water_data.csv")

regions = ["All"] + sorted(df["Region"].unique())
sources = ["All"] + sorted(df["Water Source Type"].unique())
years = ["All"] + sorted(df["Year"].unique())
risk_levels = ["All"] + sorted(df["Risk Level"].unique())

# --------------------------------------------------------
# APP INIT
# --------------------------------------------------------

app = Dash(__name__)
app.title = "AquaWatch Naija"
server = app.server  # needed by most hosts (Render, Plotly Cloud, etc.)

# --------------------------------------------------------
# REUSABLE STYLES
# --------------------------------------------------------

SIDEBAR_STYLE = {
    "width": "260px",
    "padding": "20px",
    "backgroundColor": "#f7f9fa",
    "borderRight": "1px solid #ddd",
    "minHeight": "100vh",
}

CONTENT_STYLE = {
    "flex": "1",
    "padding": "30px",
}

KPI_CARD_STYLE = {
    "flex": "1",
    "backgroundColor": "#ffffff",
    "border": "1px solid #eee",
    "borderRadius": "8px",
    "padding": "16px",
    "textAlign": "center",
    "boxShadow": "0 1px 3px rgba(0,0,0,0.06)",
}

CHART_STYLE = {"width": "49%", "display": "inline-block", "verticalAlign": "top"}

# --------------------------------------------------------
# LAYOUT
# --------------------------------------------------------

app.layout = html.Div(
    style={"display": "flex", "fontFamily": "Arial, sans-serif"},
    children=[

        # ---------------- SIDEBAR ----------------
        html.Div(
            style=SIDEBAR_STYLE,
            children=[
                html.H3("Dashboard Filters"),

                html.Label("Region"),
                dcc.Dropdown(
                    id="filter-region",
                    options=[{"label": r, "value": r} for r in regions],
                    value="All",
                    clearable=False,
                ),

                html.Br(),
                html.Label("Water Source"),
                dcc.Dropdown(
                    id="filter-source",
                    options=[{"label": s, "value": s} for s in sources],
                    value="All",
                    clearable=False,
                ),

                html.Br(),
                html.Label("Year"),
                dcc.Dropdown(
                    id="filter-year",
                    options=[{"label": str(y), "value": y} for y in years],
                    value="All",
                    clearable=False,
                ),

                html.Br(),
                html.Label("Risk Level"),
                dcc.Dropdown(
                    id="filter-risk",
                    options=[{"label": r, "value": r} for r in risk_levels],
                    value="All",
                    clearable=False,
                ),

                html.Br(),
                html.Label("Search Region"),
                dcc.Input(
                    id="filter-search",
                    type="text",
                    placeholder="Type to search...",
                    style={"width": "100%"},
                ),

                html.Hr(),
                html.Details([
                    html.Summary("WHO Drinking Water Standards"),
                    html.P("Safe pH: 6.5 - 8.5"),
                    html.P("Maximum Turbidity: 5 NTU"),
                    html.P("Maximum Contaminants: 7 ppm"),
                    html.P("Maximum Bacteria: 1000 CFU/mL"),
                ]),
            ],
        ),

        # ---------------- MAIN CONTENT ----------------
        html.Div(
            style=CONTENT_STYLE,
            children=[

                html.H1("💧 AquaWatch Naija"),
                dcc.Markdown("""
### Hyperlocal Water Quality Monitor Portal

Supporting **United Nations Sustainable Development Goal 6** — Clean Water and Sanitation.

This dashboard helps communities visualize municipal water quality, identify unsafe
water sources, monitor trends, and improve public awareness of water safety.
"""),
                html.Hr(),

                # Alert banner
                html.Div(id="alert-banner", style={"padding": "12px", "borderRadius": "6px", "marginBottom": "20px"}),

                # KPI row 1
                html.Div(
                    style={"display": "flex", "gap": "12px", "marginBottom": "12px"},
                    children=[
                        html.Div([html.H4(id="kpi-tests"), html.P("Total Tests")], style=KPI_CARD_STYLE),
                        html.Div([html.H4(id="kpi-safe"), html.P("Safe")], style=KPI_CARD_STYLE),
                        html.Div([html.H4(id="kpi-moderate"), html.P("Moderate")], style=KPI_CARD_STYLE),
                        html.Div([html.H4(id="kpi-high"), html.P("High Risk")], style=KPI_CARD_STYLE),
                    ],
                ),

                # KPI row 2
                html.Div(
                    style={"display": "flex", "gap": "12px", "marginBottom": "20px"},
                    children=[
                        html.Div([html.H4(id="kpi-ph"), html.P("Average pH")], style=KPI_CARD_STYLE),
                        html.Div([html.H4(id="kpi-turbidity"), html.P("Avg Turbidity")], style=KPI_CARD_STYLE),
                        html.Div([html.H4(id="kpi-contaminant"), html.P("Avg Contaminants")], style=KPI_CARD_STYLE),
                        html.Div([html.H4(id="kpi-bacteria"), html.P("Avg Bacteria")], style=KPI_CARD_STYLE),
                    ],
                ),

                html.Hr(),

                # Map
                html.H2("🗺 Water Quality Map"),
                dcc.Graph(id="map-graph"),

                html.Hr(),

                # Charts
                html.H2("📊 Water Quality Analytics"),
                html.Div([
                    dcc.Graph(id="chart-risk-dist", style=CHART_STYLE),
                    dcc.Graph(id="chart-water-source", style=CHART_STYLE),
                    dcc.Graph(id="chart-ph-region", style=CHART_STYLE),
                    dcc.Graph(id="chart-turbidity", style=CHART_STYLE),
                    dcc.Graph(id="chart-contaminant", style=CHART_STYLE),
                    dcc.Graph(id="chart-bacteria", style=CHART_STYLE),
                    dcc.Graph(id="chart-yearly-trend", style=CHART_STYLE),
                    dcc.Graph(id="chart-regional-risk", style=CHART_STYLE),
                ]),

                html.Hr(),

                # Data table
                html.H2("📋 Water Testing Records"),
                dash_table.DataTable(
                    id="data-table",
                    page_size=10,
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "left", "padding": "6px", "fontSize": "13px"},
                    style_header={"fontWeight": "bold", "backgroundColor": "#f0f2f4"},
                ),

                html.Div(
                    style={"marginTop": "16px", "display": "flex", "gap": "12px"},
                    children=[
                        html.Button("⬇ Download Filtered Data", id="btn-download-filtered"),
                        html.Button("⬇ Download High Risk Report", id="btn-download-highrisk"),
                        dcc.Download(id="download-filtered"),
                        dcc.Download(id="download-highrisk"),
                    ],
                ),

                html.Hr(),
                html.P(
                    "Built by Team Quantum Engineers — Grow with Google x Mentor Me Collective — "
                    "UN SDG Goal 6, Clean Water and Sanitation",
                    style={"color": "#888", "fontSize": "12px"},
                ),
            ],
        ),
    ],
)

# --------------------------------------------------------
# HELPER: get the currently-filtered dataframe
# --------------------------------------------------------

def get_filtered(region, source, year, risk, search):
    return apply_filters(df, region, source, year, risk, search)


# --------------------------------------------------------
# MAIN CALLBACK: updates everything when a filter changes
# --------------------------------------------------------

@app.callback(
    Output("alert-banner", "children"),
    Output("alert-banner", "style"),
    Output("kpi-tests", "children"),
    Output("kpi-safe", "children"),
    Output("kpi-moderate", "children"),
    Output("kpi-high", "children"),
    Output("kpi-ph", "children"),
    Output("kpi-turbidity", "children"),
    Output("kpi-contaminant", "children"),
    Output("kpi-bacteria", "children"),
    Output("map-graph", "figure"),
    Output("chart-risk-dist", "figure"),
    Output("chart-water-source", "figure"),
    Output("chart-ph-region", "figure"),
    Output("chart-turbidity", "figure"),
    Output("chart-contaminant", "figure"),
    Output("chart-bacteria", "figure"),
    Output("chart-yearly-trend", "figure"),
    Output("chart-regional-risk", "figure"),
    Output("data-table", "data"),
    Output("data-table", "columns"),
    Input("filter-region", "value"),
    Input("filter-source", "value"),
    Input("filter-year", "value"),
    Input("filter-risk", "value"),
    Input("filter-search", "value"),
)
def update_dashboard(region, source, year, risk, search):

    filtered = get_filtered(region, source, year, risk, search)

    high = filtered[filtered["Risk Level"] == "High Risk"]
    moderate = filtered[filtered["Risk Level"] == "Moderate Risk"]

    if len(high):
        alert_text = f"🚨 {len(high)} High Risk water source(s) detected."
        alert_style = {**{"padding": "12px", "borderRadius": "6px", "marginBottom": "20px"},
                        "backgroundColor": "#fdecea", "color": "#611a15"}
    elif len(moderate):
        alert_text = f"⚠ {len(moderate)} Moderate Risk water source(s) detected."
        alert_style = {**{"padding": "12px", "borderRadius": "6px", "marginBottom": "20px"},
                        "backgroundColor": "#fff4e5", "color": "#663c00"}
    else:
        alert_text = "✅ No unsafe water sources found in current filters."
        alert_style = {**{"padding": "12px", "borderRadius": "6px", "marginBottom": "20px"},
                        "backgroundColor": "#eaf6ea", "color": "#1e4620"}

    metrics = calculate_metrics(filtered)

    # Handle the empty-filtered-data case gracefully so charts never crash
    if filtered.empty:
        empty_fig = create_map(filtered)
        table_data = []
        table_columns = [{"name": c, "id": c} for c in df.columns]
        return (
            alert_text, alert_style,
            metrics["tests"], metrics["safe"], metrics["moderate"], metrics["high"],
            metrics["ph"], metrics["turbidity"], metrics["contaminant"], metrics["bacteria"],
            empty_fig, empty_fig, empty_fig, empty_fig, empty_fig,
            empty_fig, empty_fig, empty_fig, empty_fig,
            table_data, table_columns,
        )

    map_fig = create_map(filtered)
    fig_risk = risk_distribution_chart(filtered)
    fig_source = water_source_chart(filtered)
    fig_ph = ph_region_chart(filtered)
    fig_turbidity = turbidity_region_chart(filtered)
    fig_contaminant = contaminant_chart(filtered)
    fig_bacteria = bacteria_chart(filtered)
    fig_trend = yearly_trend_chart(filtered)
    fig_regional = regional_risk_chart(filtered)

    table_data = filtered.to_dict("records")
    table_columns = [{"name": c, "id": c} for c in filtered.columns]

    return (
        alert_text, alert_style,
        metrics["tests"], metrics["safe"], metrics["moderate"], metrics["high"],
        metrics["ph"], metrics["turbidity"], metrics["contaminant"], metrics["bacteria"],
        map_fig,
        fig_risk, fig_source, fig_ph, fig_turbidity,
        fig_contaminant, fig_bacteria, fig_trend, fig_regional,
        table_data, table_columns,
    )


# --------------------------------------------------------
# DOWNLOAD CALLBACKS
# --------------------------------------------------------

@app.callback(
    Output("download-filtered", "data"),
    Input("btn-download-filtered", "n_clicks"),
    State("filter-region", "value"),
    State("filter-source", "value"),
    State("filter-year", "value"),
    State("filter-risk", "value"),
    State("filter-search", "value"),
    prevent_initial_call=True,
)
def download_filtered(n_clicks, region, source, year, risk, search):
    filtered = get_filtered(region, source, year, risk, search)
    return dcc.send_data_frame(filtered.to_csv, "filtered_water_data.csv", index=False)


@app.callback(
    Output("download-highrisk", "data"),
    Input("btn-download-highrisk", "n_clicks"),
    State("filter-region", "value"),
    State("filter-source", "value"),
    State("filter-year", "value"),
    State("filter-risk", "value"),
    State("filter-search", "value"),
    prevent_initial_call=True,
)
def download_highrisk(n_clicks, region, source, year, risk, search):
    filtered = get_filtered(region, source, year, risk, search)
    high = filtered[filtered["Risk Level"] == "High Risk"]
    return dcc.send_data_frame(high.to_csv, "high_risk_sites.csv", index=False)


# --------------------------------------------------------
# RUN
# --------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
