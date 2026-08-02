"""
AquaWatch Naija — Hyperlocal Water Quality Monitor Portal
=============================================================
UN SDG Goal 6 — Clean Water and Sanitation


A public dashboard that lets community members view municipal water
testing results and safety warnings in one place.


Data source: nigeria_combined_water_data.csv


HOW TO RUN THIS APP
--------------------
1. Make sure you have Python installed.
2. Install the required libraries (only needs to be done once):
       pip install streamlit pandas numpy
3. Put this file (app.py) and "nigeria_combined_water_data.csv"
   in the SAME folder.
4. Open a terminal in that folder and run:
       streamlit run app.py
5. Your browser will open automatically at http://localhost:8501
"""


import numpy as np
import pandas as pd
import streamlit as st


# -----------------------------------------------------------------------
# PAGE CONFIG  (must be the first Streamlit command in the script)
# -----------------------------------------------------------------------
st.set_page_config(
    page_title="AquaWatch Naija",
    page_icon="💧",
    layout="wide",
)


# -----------------------------------------------------------------------
# SAFETY THRESHOLDS
# -----------------------------------------------------------------------
PH_MIN, PH_MAX = 6.5, 8.5          # Safe drinking water pH range
TURBIDITY_MAX = 5.0                # NTU  (WHO acceptable limit)
BACTERIA_MAX = 1000.0              # CFU/mL (simplified "high risk" cutoff)
CONTAMINANT_MAX = 7.0              # ppm (on this dataset's 0-10 scale)


# -----------------------------------------------------------------------
# LOAD & PREPARE THE DATA
# -----------------------------------------------------------------------
# NOTE: This is the Playground-only version. The Streamlit Playground runs
# in a sandboxed browser environment that blocks outbound network requests,
# and it has no access to files on your computer or in your GitHub repo.
# This version uses a file uploader instead, which reads the file locally
# via the browser's file picker — confirmed to work in the Playground.
#
# For the REAL deployed app (Streamlit Cloud / your GitHub repo), use the
# version of this file with CSV_FILE = "nigeria_combined_water_data.csv"
# instead — that one reads the CSV automatically, no manual upload needed.
uploaded_file = st.sidebar.file_uploader(
    "📁 Upload nigeria_combined_water_data.csv to preview the dashboard",
    type="csv",
)

if uploaded_file is None:
    st.info("👆 Upload **nigeria_combined_water_data.csv** in the sidebar to load the dashboard.")
    st.stop()




@st.cache_data
def load_data(file) -> pd.DataFrame:
    """Read the uploaded CSV and add a few helper columns used across the app."""
    df = pd.read_csv(file)


    # --- Build a single, easy-to-read Risk Level column -----------------
    # A site is flagged "High Risk" if ANY of its readings breach a
    # safety threshold. This lets us evaluate every row, even the ones
    # that don't already have a written "Disease Indicator / Risk" note.
    def classify_risk(row):
        reasons = []
        if pd.notna(row["pH Level"]) and not (PH_MIN <= row["pH Level"] <= PH_MAX):
            reasons.append("pH out of safe range")
        if pd.notna(row["Turbidity (NTU)"]) and row["Turbidity (NTU)"] > TURBIDITY_MAX:
            reasons.append("High turbidity")
        if pd.notna(row["Bacteria Count (CFU/mL)"]) and row["Bacteria Count (CFU/mL)"] > BACTERIA_MAX:
            reasons.append("High bacteria count")
        if pd.notna(row["Contaminant Level (ppm)"]) and row["Contaminant Level (ppm)"] > CONTAMINANT_MAX:
            reasons.append("High contaminant level")


        if len(reasons) >= 2:
            return "High Risk", "; ".join(reasons)
        elif len(reasons) == 1:
            return "Moderate Risk", reasons[0]
        else:
            return "Safe", "No thresholds breached"


    risk_results = df.apply(classify_risk, axis=1, result_type="expand")
    df["Risk Level"] = risk_results[0]
    df["Risk Reason"] = risk_results[1]


    # --- Give every region an approximate map location -------------------
    # NOTE: The dataset doesn't include exact GPS coordinates, so we use
    # approximate central points for each region (for visualization
    # purposes only) and add a small random "jitter" so multiple test
    # sites in the same region don't sit on top of each other.
    region_coords = {
        "Abuja (FCT)": (9.0765, 7.3986),
        "Benue South": (7.1900, 8.1300),
        "Central": (9.5000, 7.6000),
        "North": (11.9964, 8.5920),
        "South": (4.8156, 7.0498),
        "East": (6.4500, 7.5000),
        "West": (7.3775, 3.9470),
    }
    rng = np.random.default_rng(42)  # fixed seed = same map every run
    lat_list, lon_list = [], []
    for region in df["Region"]:
        base_lat, base_lon = region_coords.get(region, (9.0820, 8.6753))  # Nigeria center fallback
        lat_list.append(base_lat + rng.uniform(-0.35, 0.35))
        lon_list.append(base_lon + rng.uniform(-0.35, 0.35))
    df["lat"] = lat_list
    df["lon"] = lon_list


    return df




try:
    data = load_data(uploaded_file)
except Exception as e:
    st.error(f" Could not read that file as a CSV. Details: {e}")
    st.stop()


# -----------------------------------------------------------------------
# SIDEBAR — FILTERS
# -----------------------------------------------------------------------
st.sidebar.title("Filter Results")
st.sidebar.write("Narrow down the testing results shown on the dashboard.")


region_options = ["All Regions"] + sorted(data["Region"].dropna().unique().tolist())
selected_region = st.sidebar.selectbox("Region", region_options)


source_options = ["All Water Source Types"] + sorted(data["Water Source Type"].dropna().unique().tolist())
selected_source = st.sidebar.selectbox("Water Source Type", source_options)


# Apply the filters
filtered = data.copy()
if selected_region != "All Regions":
    filtered = filtered[filtered["Region"] == selected_region]
if selected_source != "All Water Source Types":
    filtered = filtered[filtered["Water Source Type"] == selected_source]


st.sidebar.markdown("---")
st.sidebar.caption(
    "Thresholds used to flag risk: "
    f"pH outside {PH_MIN}-{PH_MAX}, Turbidity > {TURBIDITY_MAX} NTU, "
    f"Bacteria > {int(BACTERIA_MAX)} CFU/mL, Contaminant > {CONTAMINANT_MAX} ppm."
)


# -----------------------------------------------------------------------
# HEADER
# -----------------------------------------------------------------------
st.title("AquaWatch Naija")
st.markdown(
    "##### A public dashboard for municipal water testing results & safety warnings — "
    "supporting **UN SDG 6: Clean Water and Sanitation**"
)
st.markdown(
    f"Showing **{len(filtered)}** of **{len(data)}** total test records "
    f"— Region: *{selected_region}*, Source: *{selected_source}*"
)
st.divider()


# -----------------------------------------------------------------------
# SAFETY WARNINGS & ALERT BANNERS
# -----------------------------------------------------------------------
high_risk_df = filtered[filtered["Risk Level"] == "High Risk"]
moderate_risk_df = filtered[filtered["Risk Level"] == "Moderate Risk"]


if len(filtered) == 0:
    st.info("No test records match the selected filters. Try a different Region or Water Source Type.")
else:
    if len(high_risk_df) > 0:
        st.error(
            f" **HIGH RISK ALERT:** {len(high_risk_df)} water source(s) in this view "
            "have failed multiple safety checks and may be unsafe to use without treatment. "
            "See the flagged rows in the table below."
        )
    if len(moderate_risk_df) > 0:
        st.warning(
            f" **Moderate Risk Notice:** {len(moderate_risk_df)} water source(s) breach "
            "one safety threshold and should be monitored closely."
        )
    if len(high_risk_df) == 0 and len(moderate_risk_df) == 0:
        st.success("No high or moderate risk sites found in the current selection.")


st.divider()


# -----------------------------------------------------------------------
# KEY SUMMARY METRICS
# -----------------------------------------------------------------------
st.subheader("Summary Metrics")


col1, col2, col3, col4 = st.columns(4)


total_tests = len(filtered)
high_risk_sites = len(high_risk_df)
avg_ph = filtered["pH Level"].mean()
avg_turbidity = filtered["Turbidity (NTU)"].mean()


col1.metric("Total Tests", f"{total_tests}")
col2.metric("High Risk Sites", f"{high_risk_sites}",
            delta=None if high_risk_sites == 0 else "Needs attention",
            delta_color="inverse")
col3.metric("Average pH", f"{avg_ph:.2f}" if pd.notna(avg_ph) else "N/A")
col4.metric("Average Turbidity (NTU)", f"{avg_turbidity:.2f}" if pd.notna(avg_turbidity) else "N/A")


st.divider()


# -----------------------------------------------------------------------
# INTERACTIVE MAP
# -----------------------------------------------------------------------
st.subheader("Testing Site Locations (Nigeria)")
st.caption(
    "Note: Exact GPS coordinates were not available in the dataset, so points are placed "
    "at approximate regional locations for illustration."
)


if len(filtered) > 0:
    # Color the map points red for High Risk, orange for Moderate, green for Safe
    def risk_color(level):
        if level == "High Risk":
            return [220, 20, 60]      # red
        elif level == "Moderate Risk":
            return [255, 165, 0]      # orange
        else:
            return [34, 139, 34]      # green


    map_df = filtered.copy()
    map_df["color"] = map_df["Risk Level"].apply(risk_color)


    st.map(map_df, latitude="lat", longitude="lon", color="color", size=8000)


    st.caption("🔴 High Risk   🟠 Moderate Risk   🟢 Safe")
else:
    st.info("No locations to display for the current filters.")


st.divider()


# -----------------------------------------------------------------------
# DATA TABLE
# -----------------------------------------------------------------------
st.subheader("Municipal Water Testing Results")


display_columns = [
    "Region",
    "Water Source Type",
    "Year",
    "pH Level",
    "Turbidity (NTU)",
    "Bacteria Count (CFU/mL)",
    "Contaminant Level (ppm)",
    "Dissolved Oxygen (mg/L)",
    "Water Treatment Method",
    "Risk Level",
    "Risk Reason",
    "Disease Indicator / Risk",
]
table_df = filtered[display_columns].sort_values(
    by="Risk Level", key=lambda s: s.map({"High Risk": 0, "Moderate Risk": 1, "Safe": 2})
)




def highlight_risk(row):
    if row["Risk Level"] == "High Risk":
        return ["background-color: #ffcccc"] * len(row)
    elif row["Risk Level"] == "Moderate Risk":
        return ["background-color: #fff3cd"] * len(row)
    else:
        return [""] * len(row)




st.dataframe(
    table_df.style.apply(highlight_risk, axis=1),
    width="stretch",
    hide_index=True,
)




st.caption(
    "Rows highlighted in red are High Risk; rows highlighted in yellow are Moderate Risk. "
    "'Disease Indicator / Risk' shows any recorded public health notes for that specific test."
)


# -----------------------------------------------------------------------
# FOOTER
# -----------------------------------------------------------------------
st.divider()
st.caption(
    "Built for the Grow with Google | Mentor Me Collective BUILD Project — "
    "UN SDG 6: Clean Water and Sanitation."
)
