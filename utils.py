"""
utils.py
Core data processing functions for AquaWatch Naija
"""

import numpy as np
import pandas as pd
import streamlit as st

# -------------------------------------------------
# WHO SAFETY THRESHOLDS
# -------------------------------------------------

PH_MIN = 6.5
PH_MAX = 8.5

TURBIDITY_MAX = 5.0
BACTERIA_MAX = 1000.0
CONTAMINANT_MAX = 7.0

# -------------------------------------------------
# REGION COORDINATES
# -------------------------------------------------

REGION_COORDS = {
    "Abuja (FCT)": (9.0765, 7.3986),
    "Benue South": (7.1900, 8.1300),
    "Central": (9.5000, 7.6000),
    "North": (11.9964, 8.5920),
    "South": (4.8156, 7.0498),
    "East": (6.4500, 7.5000),
    "West": (7.3775, 3.9470),
}

# -------------------------------------------------
# RISK CLASSIFICATION
# -------------------------------------------------

def classify_risk(row):

    reasons = []

    if pd.notna(row["pH Level"]):
        if not (PH_MIN <= row["pH Level"] <= PH_MAX):
            reasons.append("Unsafe pH")

    if pd.notna(row["Turbidity (NTU)"]):
        if row["Turbidity (NTU)"] > TURBIDITY_MAX:
            reasons.append("High Turbidity")

    if pd.notna(row["Bacteria Count (CFU/mL)"]):
        if row["Bacteria Count (CFU/mL)"] > BACTERIA_MAX:
            reasons.append("High Bacteria")

    if pd.notna(row["Contaminant Level (ppm)"]):
        if row["Contaminant Level (ppm)"] > CONTAMINANT_MAX:
            reasons.append("High Contaminants")

    if len(reasons) >= 2:
        return pd.Series(
            ["High Risk", ", ".join(reasons)]
        )

    elif len(reasons) == 1:
        return pd.Series(
            ["Moderate Risk", reasons[0]]
        )

    else:
        return pd.Series(
            ["Safe", "No threshold exceeded"]
        )

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

@st.cache_data
def load_data(csv_file):

    df = pd.read_csv(csv_file)

    df[["Risk Level", "Risk Reason"]] = df.apply(
        classify_risk,
        axis=1
    )

    rng = np.random.default_rng(42)

    latitudes = []
    longitudes = []

    for region in df["Region"]:

        lat, lon = REGION_COORDS.get(
            region,
            (9.0820, 8.6753)
        )

        lat += rng.uniform(-0.25, 0.25)
        lon += rng.uniform(-0.25, 0.25)

        latitudes.append(lat)
        longitudes.append(lon)

    df["Latitude"] = latitudes
    df["Longitude"] = longitudes

    return df

# -------------------------------------------------
# FILTERING
# -------------------------------------------------

def apply_filters(
    df,
    region,
    source,
    year,
    risk,
    search
):

    filtered = df.copy()

    if region != "All":
        filtered = filtered[
            filtered["Region"] == region
        ]

    if source != "All":
        filtered = filtered[
            filtered["Water Source Type"] == source
        ]

    if year != "All":
        filtered = filtered[
            filtered["Year"] == year
        ]

    if risk != "All":
        filtered = filtered[
            filtered["Risk Level"] == risk
        ]

    if search:

        filtered = filtered[
            filtered["Region"]
            .str.contains(
                search,
                case=False,
                na=False
            )
        ]

    return filtered

# -------------------------------------------------
# DASHBOARD METRICS
# -------------------------------------------------

def calculate_metrics(df):

    safe = len(df[df["Risk Level"] == "Safe"])

    moderate = len(
        df[df["Risk Level"] == "Moderate Risk"]
    )

    high = len(
        df[df["Risk Level"] == "High Risk"]
    )

    return {

        "tests": len(df),

        "safe": safe,

        "moderate": moderate,

        "high": high,

        "ph": round(
            df["pH Level"].mean(),
            2
        ) if len(df) else 0,

        "turbidity": round(
            df["Turbidity (NTU)"].mean(),
            2
        ) if len(df) else 0,

        "contaminant": round(
            df["Contaminant Level (ppm)"].mean(),
            2
        ) if len(df) else 0,

        "bacteria": round(
            df["Bacteria Count (CFU/mL)"].mean(),
            2
        ) if len(df) else 0,
    }

# -------------------------------------------------
# EXTRA STATISTICS
# -------------------------------------------------

def dashboard_statistics(df):

    return {

        "Highest pH":
            df["pH Level"].max(),

        "Lowest pH":
            df["pH Level"].min(),

        "Highest Turbidity":
            df["Turbidity (NTU)"].max(),

        "Highest Bacteria":
            df["Bacteria Count (CFU/mL)"].max(),

        "Highest Contaminant":
            df["Contaminant Level (ppm)"].max(),

        "Most Common Source":
            df["Water Source Type"]
              .mode()[0],

        "Cleanest Region":
            (
                df[df["Risk Level"] == "Safe"]
                ["Region"]
                .mode()[0]
                if not df[df["Risk Level"] == "Safe"].empty
                else "N/A"
            ),

        "Most Polluted Region":
            (
                df[df["Risk Level"] == "High Risk"]
                ["Region"]
                .mode()[0]
                if not df[df["Risk Level"] == "High Risk"].empty
                else "N/A"
            ),
    }