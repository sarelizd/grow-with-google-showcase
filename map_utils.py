"""
map_utils.py

Interactive Plotly map for AquaWatch Naija
"""

import plotly.express as px


# ----------------------------------------------------------
# Risk Colors
# ----------------------------------------------------------

RISK_COLORS = {
    "Safe": "#2E8B57",           # Green
    "Moderate Risk": "#F4A300",  # Orange
    "High Risk": "#D7263D"       # Red
}


# ----------------------------------------------------------
# Create Interactive Map
# ----------------------------------------------------------

def create_map(df):

    if df.empty:

        fig = px.scatter_map(
            lat=[],
            lon=[]
        )

        fig.update_layout(
            map_style="open-street-map",
            height=650,
            margin=dict(l=0, r=0, t=0, b=0)
        )

        return fig

    fig = px.scatter_map(
        df,
        lat="Latitude",
        lon="Longitude",

        color="Risk Level",

        color_discrete_map=RISK_COLORS,

        hover_name="Region",

        hover_data={
            "Water Source Type": True,
            "Year": True,
            "pH Level": ":.2f",
            "Turbidity (NTU)": ":.2f",
            "Bacteria Count (CFU/mL)": ":,.0f",
            "Contaminant Level (ppm)": ":.2f",
            "Risk Level": True,
            "Risk Reason": True,
            "Latitude": False,
            "Longitude": False,
        },

        zoom=5,
        height=650,
    )

    fig.update_traces(
        marker=dict(
            size=14,
            opacity=0.85,
        )
    )

    fig.update_layout(

        map_style="open-street-map",

        legend_title="Risk Level",

        margin=dict(
            l=0,
            r=0,
            t=40,
            b=0
        ),

        title="Water Testing Locations",

        template="plotly_white"
    )

    return fig