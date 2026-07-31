"""
===========================================================
AquaWatch Naija
Hyperlocal Water Quality Monitor Portal

Grow with Google x Mentor Me Collective
UN SDG 6 - Clean Water and Sanitation
===========================================================
"""

import streamlit as st
import pandas as pd

from utils import (
    load_data,
    apply_filters,
    calculate_metrics
)

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
# PAGE CONFIG
# --------------------------------------------------------

st.set_page_config(
    page_title="AquaWatch Naija",
    page_icon="💧",
    layout="wide",
)

# --------------------------------------------------------
# LOAD DATA
# --------------------------------------------------------

with st.spinner("🔄 Loading AquaWatch Dashboard..."):

    df = load_data("nigeria_combined_water_data.csv")

# --------------------------------------------------------
# HEADER
# --------------------------------------------------------

st.title("💧 AquaWatch Naija")

st.markdown("""
### Hyperlocal Water Quality Monitor Portal

Supporting **United Nations Sustainable Development Goal 6**

Clean Water and Sanitation

This dashboard helps communities visualize municipal water quality,
identify unsafe water sources, monitor trends, and improve public
awareness of water safety.
""")

st.divider()

# --------------------------------------------------------
# SIDEBAR
# --------------------------------------------------------

st.sidebar.header("Dashboard Filters")

regions = ["All"] + sorted(df["Region"].unique())

sources = ["All"] + sorted(df["Water Source Type"].unique())

years = ["All"] + sorted(df["Year"].unique())

risk_levels = ["All"] + sorted(df["Risk Level"].unique())

selected_region = st.sidebar.selectbox(
    "Region",
    regions
)

selected_source = st.sidebar.selectbox(
    "Water Source",
    sources
)

selected_year = st.sidebar.selectbox(
    "Year",
    years
)

selected_risk = st.sidebar.selectbox(
    "Risk Level",
    risk_levels
)

search = st.sidebar.text_input(
    "Search Region"
)

st.sidebar.divider()

with st.sidebar.expander("WHO Drinking Water Standards"):

    st.write("""
**Safe pH**

6.5 - 8.5

**Maximum Turbidity**

5 NTU

**Maximum Contaminants**

7 ppm

**Maximum Bacteria**

1000 CFU/mL
""")

# --------------------------------------------------------
# FILTER DATA
# --------------------------------------------------------

filtered = apply_filters(
    df,
    selected_region,
    selected_source,
    selected_year,
    selected_risk,
    search
)

# --------------------------------------------------------
# ALERTS
# --------------------------------------------------------

high = filtered[filtered["Risk Level"] == "High Risk"]

moderate = filtered[
    filtered["Risk Level"] == "Moderate Risk"
]

if len(high):

    st.error(
        f"🚨 {len(high)} High Risk water source(s) detected."
    )

elif len(moderate):

    st.warning(
        f"⚠ {len(moderate)} Moderate Risk water source(s) detected."
    )

else:

    st.success(
        "✅ No unsafe water sources found in current filters."
    )

st.divider()

# --------------------------------------------------------
# KPI SECTION
# --------------------------------------------------------

metrics = calculate_metrics(filtered)

c1, c2, c3, c4 = st.columns(4)

c5, c6, c7, c8 = st.columns(4)

c1.metric(
    "Total Tests",
    metrics["tests"]
)

c2.metric(
    "Safe",
    metrics["safe"]
)

c3.metric(
    "Moderate",
    metrics["moderate"]
)

c4.metric(
    "High Risk",
    metrics["high"]
)

c5.metric(
    "Average pH",
    metrics["ph"]
)

c6.metric(
    "Avg Turbidity",
    metrics["turbidity"]
)

c7.metric(
    "Avg Contaminants",
    metrics["contaminant"]
)

c8.metric(
    "Avg Bacteria",
    metrics["bacteria"]
)

st.divider()

# --------------------------------------------------------
# MAP
# --------------------------------------------------------

st.header("🗺 Water Quality Map")

map_figure = create_map(filtered)

st.plotly_chart(
    map_figure,
    use_container_width=True
)

st.divider()

# --------------------------------------------------------
# CHARTS
# --------------------------------------------------------

st.header("📊 Water Quality Analytics")

left, right = st.columns(2)

with left:

    st.plotly_chart(
        risk_distribution_chart(filtered),
        use_container_width=True
    )

    st.plotly_chart(
        ph_region_chart(filtered),
        use_container_width=True
    )

    st.plotly_chart(
        contaminant_chart(filtered),
        use_container_width=True
    )

    st.plotly_chart(
        yearly_trend_chart(filtered),
        use_container_width=True
    )

with right:

    st.plotly_chart(
        water_source_chart(filtered),
        use_container_width=True
    )

    st.plotly_chart(
        turbidity_region_chart(filtered),
        use_container_width=True
    )

    st.plotly_chart(
        bacteria_chart(filtered),
        use_container_width=True
    )

    st.plotly_chart(
        regional_risk_chart(filtered),
        use_container_width=True
    )

st.divider()

# --------------------------------------------------------
# DATA TABLE
# --------------------------------------------------------

st.header("📋 Water Testing Records")

st.dataframe(
    filtered,
    use_container_width=True,
    hide_index=True
)

csv = filtered.to_csv(index=False)

st.download_button(
    "⬇ Download Filtered Data",
    csv,
    file_name="filtered_water_data.csv",
    mime="text/csv"
)

high_csv = high.to_csv(index=False)

st.download_button(
    "⬇ Download High Risk Report",
    high_csv,
    file_name="high_risk_sites.csv",
    mime="text/csv"
)

st.divider()

# --------------------------------------------------------
# FOOTER
# --------------------------------------------------------

st.caption(
"""
Built by Team Quantum Engineers

Grow with Google x Mentor Me Collective

UN SDG Goal 6 - Clean Water and Sanitation
"""
)