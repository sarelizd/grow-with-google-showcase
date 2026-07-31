"""
charts.py
Interactive Plotly charts for AquaWatch Naija
"""

import plotly.express as px
import pandas as pd

# ----------------------------------------------------------
# Dashboard Color Palette
# ----------------------------------------------------------

COLORS = {
    "Safe": "#2E8B57",
    "Moderate Risk": "#F4A300",
    "High Risk": "#D7263D"
}


# ----------------------------------------------------------
# Risk Distribution
# ----------------------------------------------------------

def risk_distribution_chart(df):

    counts = (
        df["Risk Level"]
        .value_counts()
        .rename_axis("Risk Level")
        .reset_index(name="Count")
    )

    fig = px.bar(
        counts,
        x="Risk Level",
        y="Count",
        color="Risk Level",
        color_discrete_map=COLORS,
        title="Risk Distribution",
        text="Count",
    )

    fig.update_layout(
        template="plotly_white",
        showlegend=False,
        height=420
    )

    return fig


# ----------------------------------------------------------
# Water Source Distribution
# ----------------------------------------------------------

def water_source_chart(df):

    counts = (
        df["Water Source Type"]
        .value_counts()
        .reset_index()
    )

    counts.columns = ["Water Source", "Count"]

    fig = px.pie(
        counts,
        names="Water Source",
        values="Count",
        hole=0.45,
        title="Water Source Distribution"
    )

    fig.update_layout(
        template="plotly_white",
        height=420
    )

    return fig


# ----------------------------------------------------------
# Average pH by Region
# ----------------------------------------------------------

def ph_region_chart(df):

    ph = (
        df.groupby("Region")["pH Level"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        ph,
        x="Region",
        y="pH Level",
        color="pH Level",
        title="Average pH by Region"
    )

    fig.update_layout(
        template="plotly_white",
        height=420
    )

    return fig


# ----------------------------------------------------------
# Average Turbidity
# ----------------------------------------------------------

def turbidity_region_chart(df):

    turbidity = (
        df.groupby("Region")["Turbidity (NTU)"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        turbidity,
        x="Region",
        y="Turbidity (NTU)",
        color="Turbidity (NTU)",
        title="Average Turbidity by Region"
    )

    fig.update_layout(
        template="plotly_white",
        height=420
    )

    return fig


# ----------------------------------------------------------
# Average Contaminants
# ----------------------------------------------------------

def contaminant_chart(df):

    contam = (
        df.groupby("Region")["Contaminant Level (ppm)"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        contam,
        x="Region",
        y="Contaminant Level (ppm)",
        color="Contaminant Level (ppm)",
        title="Average Contaminant Level"
    )

    fig.update_layout(
        template="plotly_white",
        height=420
    )

    return fig


# ----------------------------------------------------------
# Average Bacteria
# ----------------------------------------------------------

def bacteria_chart(df):

    bacteria = (
        df.groupby("Region")["Bacteria Count (CFU/mL)"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        bacteria,
        x="Region",
        y="Bacteria Count (CFU/mL)",
        color="Bacteria Count (CFU/mL)",
        title="Average Bacteria Count"
    )

    fig.update_layout(
        template="plotly_white",
        height=420
    )

    return fig


# ----------------------------------------------------------
# Yearly Trend
# ----------------------------------------------------------

def yearly_trend_chart(df):

    yearly = (
        df.groupby("Year")[
            [
                "pH Level",
                "Turbidity (NTU)",
                "Contaminant Level (ppm)"
            ]
        ]
        .mean()
        .reset_index()
    )

    fig = px.line(
        yearly,
        x="Year",
        y=[
            "pH Level",
            "Turbidity (NTU)",
            "Contaminant Level (ppm)"
        ],
        markers=True,
        title="Water Quality Trends by Year"
    )

    fig.update_layout(
        template="plotly_white",
        height=450
    )

    return fig


# ----------------------------------------------------------
# Risk by Region
# ----------------------------------------------------------

def regional_risk_chart(df):

    region = (
        df.groupby(
            ["Region", "Risk Level"]
        )
        .size()
        .reset_index(name="Count")
    )

    fig = px.bar(
        region,
        x="Region",
        y="Count",
        color="Risk Level",
        color_discrete_map=COLORS,
        barmode="stack",
        title="Risk Levels by Region"
    )

    fig.update_layout(
        template="plotly_white",
        height=450
    )

    return fig


# ----------------------------------------------------------
# Top 10 Highest Risk Records
# ----------------------------------------------------------

def top10_high_risk(df):

    risk_order = {
        "High Risk": 0,
        "Moderate Risk": 1,
        "Safe": 2
    }

    temp = df.copy()

    temp["Sort"] = temp["Risk Level"].map(risk_order)

    temp = temp.sort_values(
        ["Sort", "Contaminant Level (ppm)"],
        ascending=[True, False]
    )

    return temp.head(10)