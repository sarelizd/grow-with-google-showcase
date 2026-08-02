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
       pip install -r requirements.txt
3. Put this file (app.py) and "nigeria_combined_water_data.csv"
   in the SAME folder.
4. Open a terminal in that folder and run:
       streamlit run app.py
5. Your browser will open automatically at http://localhost:8501
"""

import textwrap
from pathlib import Path

import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

# -----------------------------------------------------------------------
# PAGE CONFIG  (must be the first Streamlit command in the script)
# -----------------------------------------------------------------------
st.set_page_config(
    page_title="AquaWatch Naija",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------
# CSS — Award-style glassmorphism, with a light "HydraFlow" finish layered
# on top. Two blocks, same as the design draft: the first sets up the
# glass-card/tab/alert system, the second re-tints it toward a lighter,
# more legible palette so text stays readable against the aqua background.
# -----------------------------------------------------------------------
st.markdown(
    """
<style>
:root{
    --bg-blue:#082c57;
    --bg-cobalt:#0f4fbf;
    --bg-turq:#2ec4b6;
    --bg-mint:#9ce8d0;

    --glass:rgba(255,255,255,.72);
    --glass-strong:rgba(255,255,255,.84);
    --glass-border:rgba(255,255,255,.72);

    --mint:#40e0a2;
    --emerald:#17c77b;
    --cobalt:#1f6fff;
    --amber:#ffbf47;
    --danger:#ff4d63;

    --text:#10251b;
    --muted:rgba(16,37,27,.62);
    --dark:#0d2338;
}

/* ---------- Global ---------- */
html, body, [class*="css"]{
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
                 "Segoe UI", sans-serif;
}

.stApp{
    background:
        radial-gradient(circle at 8% 12%, rgba(185,235,190,.55), transparent 28%),
        radial-gradient(circle at 88% 8%, rgba(124,207,235,.48), transparent 32%),
        linear-gradient(135deg, #c9e8d0 0%, #b9e3dc 42%, #9fd8ea 100%);
    color:#10251b;
}

.block-container{
    max-width:1500px;
    padding-top:1.25rem;
    padding-bottom:2.2rem;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"]{
    background:linear-gradient(
        180deg,
        rgba(255,255,255,.76),
        rgba(242,250,244,.64)
    );
    border-right:1px solid var(--glass-border);
    backdrop-filter:blur(14px);
}

section[data-testid="stSidebar"] *{
    color:#173321;
}

.sidebar-brand{
    display:flex;
    align-items:center;
    gap:12px;
    margin:0 0 22px;
}

.sidebar-logo{
    width:46px;height:46px;
    display:grid;place-items:center;
    border-radius:15px;
    background:linear-gradient(145deg,var(--cobalt),var(--mint));
    box-shadow:0 12px 28px rgba(0,0,0,.18);
    font-size:23px;
}

.sidebar-title{
    font-size:1.18rem;
    font-weight:800;
    letter-spacing:-.03em;
}

.sidebar-sub{
    font-size:.75rem;
    color:rgba(255,255,255,.68);
    margin-top:-2px;
}

/* ---------- Hero ---------- */
.hero-wrap{
    display:flex;
    align-items:flex-end;
    justify-content:space-between;
    gap:24px;
    margin-bottom:20px;
}

.hero-kicker{
    display:inline-flex;
    align-items:center;
    gap:8px;
    padding:6px 10px;
    border-radius:999px;
    background:rgba(64,224,162,.12);
    border:1px solid rgba(64,224,162,.24);
    color:#b8ffe4;
    font-size:.74rem;
    font-weight:750;
    letter-spacing:.02em;
}

.hero-title{
    margin-top:11px;
    font-size:2.45rem;
    line-height:1.02;
    font-weight:850;
    letter-spacing:-.055em;
    color:#ffffff;
}

.hero-sub{
    margin-top:9px;
    max-width:760px;
    font-size:.98rem;
    color:var(--muted);
    line-height:1.55;
}

/* ---------- Glass card ---------- */
.glass-card{
    background:var(--glass);
    border:1px solid var(--glass-border);
    border-radius:16px;
    backdrop-filter:blur(10px);
    -webkit-backdrop-filter:blur(10px);
    box-shadow:
        0 14px 32px rgba(4,25,48,.18),
        inset 0 1px 0 rgba(255,255,255,.08);
}

/* ---------- KPI ---------- */
.kpi-card{
    min-height:155px;
    padding:20px 22px;
    position:relative;
    overflow:hidden;
}

.kpi-card:after{
    content:"";
    position:absolute;
    width:120px;height:120px;
    right:-35px;bottom:-50px;
    border-radius:50%;
    background:linear-gradient(145deg,rgba(64,224,162,.28),rgba(31,111,255,.22));
}

.kpi-label{
    color:rgba(255,255,255,.74);
    font-size:.79rem;
    font-weight:700;
    text-transform:uppercase;
    letter-spacing:.08em;
}

.kpi-value{
    margin-top:12px;
    font-size:2.45rem;
    line-height:1;
    font-weight:860;
    letter-spacing:-.05em;
    color:#ffffff;
}

.kpi-meta{
    margin-top:9px;
    font-size:.76rem;
    color:#c7f8e6;
    font-weight:700;
}

/* ---------- Safety banners ---------- */
.alert-safe,
.alert-caution,
.alert-danger{
    border-radius:16px;
    padding:16px 18px;
    border:1px solid rgba(255,255,255,.2);
    backdrop-filter:blur(10px);
    display:flex;
    gap:13px;
    align-items:flex-start;
    box-shadow:0 10px 24px rgba(0,0,0,.12);
}

.alert-safe{
    background:linear-gradient(135deg,rgba(17,199,123,.26),rgba(21,153,101,.17));
}

.alert-caution{
    background:linear-gradient(135deg,rgba(255,152,0,.29),rgba(230,126,0,.16));
}

.alert-danger{
    background:linear-gradient(135deg,rgba(255,77,99,.34),rgba(179,21,50,.22));
    animation:dangerPulse 1.65s infinite;
}

@keyframes dangerPulse{
    0%,100%{
        box-shadow:0 0 0 0 rgba(255,77,99,.12),0 10px 24px rgba(0,0,0,.12);
    }
    50%{
        box-shadow:0 0 0 10px rgba(255,77,99,.03),0 10px 24px rgba(0,0,0,.16);
    }
}

.alert-icon{
    width:34px;height:34px;
    border-radius:12px;
    display:grid;place-items:center;
    background:rgba(255,255,255,.14);
    flex:0 0 auto;
}

.alert-title{
    font-size:.92rem;
    font-weight:850;
    color:white;
}

.alert-copy{
    margin-top:3px;
    color:rgba(255,255,255,.78);
    font-size:.77rem;
    line-height:1.45;
}

/* ---------- Section headers ---------- */
.section-title{
    font-size:1.06rem;
    font-weight:820;
    letter-spacing:-.02em;
    color:#fff;
    margin:10px 0 12px;
}

/* ---------- Custom tabs ---------- */
div[data-baseweb="tab-list"]{
    gap:10px;
    background:rgba(255,255,255,.08);
    border:1px solid rgba(255,255,255,.14);
    border-radius:16px;
    padding:7px;
    backdrop-filter:blur(10px);
}

button[data-baseweb="tab"]{
    height:44px;
    border-radius:12px !important;
    color:rgba(255,255,255,.72) !important;
    font-weight:750 !important;
    background:transparent !important;
}

button[data-baseweb="tab"][aria-selected="true"]{
    color:#fff !important;
    background:linear-gradient(135deg,rgba(31,111,255,.92),rgba(49,155,229,.82)) !important;
    box-shadow:0 8px 20px rgba(17,76,159,.25);
}

div[data-baseweb="tab-highlight"]{
    display:none;
}

/* ---------- Native widgets ---------- */
div[data-baseweb="select"] > div,
.stMultiSelect [data-baseweb="select"] > div,
.stTextInput input{
    border-radius:12px !important;
    border:1px solid rgba(255,255,255,.18) !important;
    background:rgba(255,255,255,.12) !important;
    color:white !important;
    backdrop-filter:blur(10px);
}

div[data-baseweb="select"] span{
    color:white !important;
}

.stMetric{
    background:rgba(255,255,255,.11);
    border:1px solid rgba(255,255,255,.16);
    border-radius:14px;
    padding:14px 16px;
}

[data-testid="stMetricLabel"]{
    color:rgba(255,255,255,.7);
}

[data-testid="stMetricValue"]{
    color:white;
}

/* ---------- Dataframe ---------- */
[data-testid="stDataFrame"]{
    background:rgba(255,255,255,.10);
    border:1px solid rgba(255,255,255,.16);
    border-radius:16px;
    overflow:hidden;
    backdrop-filter:blur(10px);
}

/* ---------- Action cards ---------- */
.action-card{
    min-height:175px;
    padding:18px;
}

.action-step{
    width:34px;height:34px;
    border-radius:11px;
    display:grid;place-items:center;
    font-weight:850;
    color:white;
    background:linear-gradient(145deg,var(--cobalt),var(--mint));
    box-shadow:0 8px 18px rgba(0,0,0,.14);
}

.action-title{
    margin-top:13px;
    font-size:.94rem;
    font-weight:820;
    color:white;
}

.action-copy{
    margin-top:6px;
    font-size:.77rem;
    color:rgba(255,255,255,.72);
    line-height:1.5;
}

/* ---------- Breakdown cards ---------- */
.metric-mini{
    padding:18px;
    min-height:125px;
}

.metric-mini-label{
    color:rgba(255,255,255,.68);
    font-size:.76rem;
}

.metric-mini-value{
    margin-top:13px;
    font-size:1.75rem;
    font-weight:840;
    color:white;
}

.metric-mini-note{
    margin-top:4px;
    font-size:.7rem;
    color:#bcf7dc;
}

/* ---------- Misc ---------- */
hr{
    border-color:rgba(255,255,255,.12) !important;
}

#MainMenu{visibility:hidden;}
footer{visibility:hidden;}
header{background:transparent;}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>
/* HydraFlow-inspired light glass finish */
.hero-title,.section-title{color:#173321!important}
.hero-sub{color:#52685a!important}
.hero-kicker{color:#0b754b!important;background:rgba(255,255,255,.52)!important;border-color:rgba(16,120,75,.18)!important}
.kpi-card,.metric-mini,.action-card{
    background:rgba(255,255,255,.76)!important;
    border:1px solid rgba(255,255,255,.88)!important;
    box-shadow:0 18px 42px rgba(31,88,74,.10)!important;
}
.kpi-label,.metric-mini-label{color:#52685a!important}
.kpi-value,.metric-mini-value,.action-title{color:#14261a!important}
.kpi-meta,.metric-mini-note{color:#168b54!important}
.action-copy{color:#607064!important}
.alert-title,.alert-copy,.alert-icon{color:white!important}
.alert-safe{background:linear-gradient(135deg,#179b5b,#28bd78)!important}
.alert-caution{background:linear-gradient(135deg,#cc7a00,#ff9800)!important}
.alert-danger{background:linear-gradient(135deg,#d94752,#f0646e)!important}
button[data-baseweb="tab"]{color:#4e6657!important}
button[data-baseweb="tab"][aria-selected="true"]{
    color:white!important;
    background:linear-gradient(135deg,#15975a,#28c781)!important;
}
div[data-baseweb="tab-list"]{
    background:rgba(255,255,255,.62)!important;
    border-color:rgba(255,255,255,.78)!important;
}
div[data-baseweb="select"] > div,.stTextInput input{
    background:rgba(255,255,255,.78)!important;
    color:#173321!important;
    border-color:rgba(255,255,255,.90)!important;
}
div[data-baseweb="select"] span{color:#173321!important}
[data-testid="stMetricLabel"],[data-testid="stMetricValue"]{color:#173321!important}
.stMetric{background:rgba(255,255,255,.68)!important;border-color:rgba(255,255,255,.82)!important}
section[data-testid="stSidebar"] .sidebar-sub,
section[data-testid="stSidebar"] .stCaption{color:#607064!important}
</style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------
# SAFETY THRESHOLDS
# -----------------------------------------------------------------------
PH_MIN, PH_MAX = 6.5, 8.5          # Safe drinking water pH range
TURBIDITY_MAX = 5.0                # NTU  (WHO acceptable limit)
BACTERIA_MAX = 1000.0              # CFU/mL (simplified "high risk" cutoff)
CONTAMINANT_MAX = 7.0              # ppm (on this dataset's 0-10 scale)

# -----------------------------------------------------------------------
# RISK LEVEL COLORS (discrete: Green = Safe, Orange = Moderate, Red = High)
# -----------------------------------------------------------------------
# Colors are tied directly to the 3 Risk Level buckets — not a continuous
# score — so the legend, map dots, and table row shading always agree on
# exactly which of the 3 categories a given site falls into.
RISK_COLORS = {
    "Safe": (52, 168, 83),          # green
    "Moderate Risk": (255, 152, 0), # orange
    "High Risk": (234, 67, 53),     # red
}


def risk_level_color(level: str) -> list:
    """Return the RGB color for a Risk Level bucket, used for the map dots."""
    return list(RISK_COLORS.get(level, (150, 150, 150)))


def highlight_risk(row):
    # Same discrete Green/Orange/Red colors as the map, applied as a light
    # background tint so a table row's shade always matches its risk bucket.
    r, g, b = RISK_COLORS.get(row["Risk Level"], (150, 150, 150))
    return [f"background-color: rgba({r}, {g}, {b}, 0.25)"] * len(row)


# -----------------------------------------------------------------------
# LOAD & PREPARE THE DATA
# -----------------------------------------------------------------------
# Resolved relative to THIS FILE's location (not the working directory).
# Streamlit Cloud's working directory is always the repo root, regardless
# of where app.py lives — so a bare filename breaks once app.py moves into
# a subfolder like src/. This works from the repo root or from inside src/.
CSV_FILE = Path(__file__).parent / "nigeria_combined_water_data.csv"


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """Read the CSV and add a few helper columns used across the app."""
    df = pd.read_csv(path)

    # --- Build a single, easy-to-read Risk Level column -----------------
    # A site is flagged "High Risk" if 2+ readings breach a safety
    # threshold, "Moderate Risk" if exactly 1 breaches, else "Safe".
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

    # --- Fill blank Disease Indicator / Risk cells with a derived note ---
    # Only ~9 of 324 rows have a hand-written field note in this column
    # (from Abuja/Benue South site surveys) — those are left untouched.
    # For the remaining rows, this builds a note from the dataset's own
    # Cholera / Typhoid / Diarrheal columns, using published WHO-referenced
    # incidence bands, rather than leaving the field blank or inventing
    # narrative detail that was never actually observed. Only the single
    # highest-incidence disease (by raw cases/100k) is kept per row.
    def disease_indicator_note(row):
        original = row.get("Disease Indicator / Risk")
        if pd.notna(original) and str(original).strip():
            return original  # keep the real, field-observed note as-is

        # Only the single highest-incidence disease (by raw cases/100k) is
        # reported per row, rather than listing every disease column that
        # has a value — this keeps each row to one disease note instead of
        # up to three.
        candidates = []  # (incidence_value, note_text)

        cholera = row.get("Cholera Cases per 100,000 people")
        if pd.notna(cholera):
            if cholera >= 10:
                note = (
                    f"Cholera incidence high ({cholera:.0f}/100k; WHO-referenced "
                    "'high incidence' band is ≥10 cases/100k/yr)"
                )
            elif cholera >= 1:
                note = f"Cholera incidence moderate ({cholera:.0f}/100k)"
            else:
                note = None
            if note:
                candidates.append((cholera, note))

        typhoid = row.get("Typhoid Cases per 100,000 people")
        if pd.notna(typhoid):
            if typhoid >= 100:
                note = (
                    f"Typhoid incidence high ({typhoid:.0f}/100k; published "
                    "classification is ≥100 cases/100k person-years)"
                )
            elif typhoid >= 10:
                note = (
                    f"Typhoid incidence medium ({typhoid:.0f}/100k; published "
                    "range is 10-100 cases/100k person-years)"
                )
            else:
                note = None
            if note:
                candidates.append((typhoid, note))

        diarrheal = row.get("Diarrheal Cases per 100,000 people")
        if pd.notna(diarrheal):
            candidates.append(
                (
                    diarrheal,
                    f"Diarrheal disease rate {diarrheal:.0f}/100k (WASH-related; no "
                    "single absolute WHO alert threshold exists for this indicator — "
                    "outbreaks are typically judged against a local baseline)",
                )
            )

        if candidates:
            # Highest raw incidence value wins; only that one is kept.
            _, top_note = max(candidates, key=lambda c: c[0])
            return top_note

        return "No elevated disease indicators recorded"

    df["Disease Indicator / Risk"] = df.apply(disease_indicator_note, axis=1)

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
    data = load_data(CSV_FILE)
except FileNotFoundError:
    st.error(
        f" Could not find **{CSV_FILE}**. "
        "Please make sure it is in the same folder as app.py, then refresh this page."
    )
    st.stop()

# -----------------------------------------------------------------------
# SIDEBAR — BRAND + FILTERS
# -----------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-logo">💧</div>
            <div>
                <div class="sidebar-title">AquaWatch Naija</div>
                <div class="sidebar-sub">Hyperlocal Water Quality Monitor</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Location Filters")

    # NOTE: the dataset's finest geographic grain is "Region" (there is no
    # LGA-level breakdown in this CSV), so filters are Region + Water
    # Source Type — the same two dimensions the underlying data supports.
    region_options = ["All Regions"] + sorted(data["Region"].dropna().unique().tolist())
    selected_region = st.selectbox("Region", region_options)

    source_options = ["All Water Source Types"] + sorted(data["Water Source Type"].dropna().unique().tolist())
    selected_source = st.selectbox("Water Source Type", source_options)

    st.markdown("---")
    st.caption(
        "**Safety classification methodology:** pH (6.5–8.5) and Turbidity "
        f"(≤ {TURBIDITY_MAX} NTU) thresholds follow WHO drinking-water guidelines. "
        f"Bacteria (≤ {int(BACTERIA_MAX)} CFU/mL) and Contaminant Level "
        f"(≤ {CONTAMINANT_MAX} ppm) use simplified, dataset-calibrated cutoffs, "
        "since the source data doesn't specify which pathogen or contaminant was "
        "measured, so no single WHO limit maps directly to those two fields. "
        "A site is High Risk if 2+ readings breach a threshold, Moderate Risk if "
        "exactly 1 does, and Safe otherwise."
    )

# Apply the filters
filtered = data.copy()
if selected_region != "All Regions":
    filtered = filtered[filtered["Region"] == selected_region]
if selected_source != "All Water Source Types":
    filtered = filtered[filtered["Water Source Type"] == selected_source]

total_samples = len(filtered)
safe_count = int((filtered["Risk Level"] == "Safe").sum())
moderate_count = int((filtered["Risk Level"] == "Moderate Risk").sum())
high_count = int((filtered["Risk Level"] == "High Risk").sum())

safe_pct = 0 if total_samples == 0 else round(100 * safe_count / total_samples)
active_alerts = moderate_count + high_count

avg_ph = filtered["pH Level"].mean()
avg_turbidity = filtered["Turbidity (NTU)"].mean()
avg_bacteria = filtered["Bacteria Count (CFU/mL)"].mean()
avg_contaminant = filtered["Contaminant Level (ppm)"].mean()

# -----------------------------------------------------------------------
# HERO
# -----------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-wrap">
        <div>
            <div class="hero-kicker">● LIVE MUNICIPAL WATER INTELLIGENCE</div>
            <div class="hero-title">AquaWatch Naija: Hyperlocal Water Quality Monitor</div>
            <div class="hero-sub">
                Know your water safety before you drink. A community portal for checking
                local drinking water quality and safety alerts across Nigerian towns,
                backing <b>UN SDG 6: Clean Water and Sanitation</b>.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    f"Showing **{total_samples}** of **{len(data)}** total test records "
    f"— Region: *{selected_region}*, Source: *{selected_source}*"
)

# -----------------------------------------------------------------------
# KPI CARDS
# -----------------------------------------------------------------------
c1, c2, c3 = st.columns(3, gap="medium")

with c1:
    st.markdown(
        f"""
        <div class="glass-card kpi-card">
            <div class="kpi-label">Total Samples</div>
            <div class="kpi-value">{total_samples}</div>
            <div class="kpi-meta">Current filtered municipal records</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f"""
        <div class="glass-card kpi-card">
            <div class="kpi-label">Safe Sources</div>
            <div class="kpi-value">{safe_pct}%</div>
            <div class="kpi-meta">Meets pH, turbidity, bacteria & contaminant screening range</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        f"""
        <div class="glass-card kpi-card">
            <div class="kpi-label">Active Alerts</div>
            <div class="kpi-value">{active_alerts}</div>
            <div class="kpi-meta">{high_count} high risk • {moderate_count} moderate risk</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# -----------------------------------------------------------------------
# SAFETY ALERT BANNERS
# -----------------------------------------------------------------------
st.markdown('<div class="section-title">Safety Status</div>', unsafe_allow_html=True)

if total_samples == 0:
    st.info("No test records match the selected filters. Try a different Region or Water Source Type.")
else:
    a1, a2, a3 = st.columns(3, gap="medium")

    with a1:
        st.markdown(
            f"""
            <div class="alert-safe">
                <div class="alert-icon">✓</div>
                <div>
                    <div class="alert-title">Safe — Meets Screening Range</div>
                    <div class="alert-copy">{safe_count} sample(s) currently pass all safety checks.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with a2:
        st.markdown(
            f"""
            <div class="alert-caution">
                <div class="alert-icon">!</div>
                <div>
                    <div class="alert-title">Moderate Risk — Monitor Closely</div>
                    <div class="alert-copy">{moderate_count} sample(s) breach one threshold and should be monitored or retested.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with a3:
        st.markdown(
            f"""
            <div class="alert-danger">
                <div class="alert-icon">⚠</div>
                <div>
                    <div class="alert-title">High Risk — Unsafe Without Treatment</div>
                    <div class="alert-copy">{high_count} sample(s) breach multiple thresholds and require urgent action.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")

# -----------------------------------------------------------------------
# TABS
# -----------------------------------------------------------------------
tab_map, tab_quality, tab_action = st.tabs(
    ["Water Safety Map", "Water Quality Breakdown", "Community Action Steps"]
)

# -----------------------------------------------------------------------
# TAB 1 — MAP  (pydeck, discrete Green/Orange/Red risk coloring)
# -----------------------------------------------------------------------
with tab_map:
    st.markdown('<div class="section-title">Water Safety Map</div>', unsafe_allow_html=True)
    st.caption("Note: Points are placed at approximate regional locations for illustration.")

    if total_samples == 0:
        st.info("No samples match the current filters.")
    else:
        map_df = filtered.copy()
        map_df["color"] = map_df["Risk Level"].apply(risk_level_color)

        # Scale circle size and zoom to how narrow the current selection is.
        num_regions_shown = map_df["Region"].nunique()
        if selected_region != "All Regions":
            point_radius_m = 1200
            map_zoom = 8.3
        elif num_regions_shown <= 2:
            point_radius_m = 2500
            map_zoom = 7.0
        else:
            point_radius_m = 6000
            map_zoom = 5.2

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position="[lon, lat]",
            get_fill_color="color",
            get_radius=point_radius_m,
            radius_min_pixels=3,
            radius_max_pixels=35,
            pickable=True,
            opacity=0.8,
            stroked=True,
            get_line_color=[255, 255, 255],
            line_width_min_pixels=1,
        )

        view_state = pdk.ViewState(
            latitude=map_df["lat"].mean(),
            longitude=map_df["lon"].mean(),
            zoom=map_zoom,
        )

        tooltip = {
            "html": (
                "<b>Region:</b> {Region}<br/>"
                "<b>Water Source:</b> {Water Source Type}<br/>"
                "<b>Risk Level:</b> {Risk Level}<br/>"
                "<b>Reason:</b> {Risk Reason}"
            ),
            "style": {"backgroundColor": "black", "color": "white"},
        }

        st.pydeck_chart(
            pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip=tooltip,
                map_provider="carto",
                map_style="road",  # closest free basemap to Google Maps' classic road-map look
            )
        )

        st.caption("🟢 Safe   🟠 Moderate Risk   🔴 High Risk — Hover over a point for more details")

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Safe", safe_count)
        with k2:
            st.metric("Moderate Risk", moderate_count)
        with k3:
            st.metric("High Risk", high_count)
        with k4:
            st.metric("Mapped Sources", len(map_df))

        map_table_cols = ["Region", "Water Source Type", "Risk Level", "pH Level", "Turbidity (NTU)"]
        map_table = filtered[map_table_cols].sort_values(
            by="Risk Level", key=lambda s: s.map({"High Risk": 0, "Moderate Risk": 1, "Safe": 2})
        )
        st.dataframe(
            map_table.style.apply(highlight_risk, axis=1),
            width="stretch",
            hide_index=True,
            height=340,
        )

# -----------------------------------------------------------------------
# TAB 2 — WATER QUALITY BREAKDOWN
# -----------------------------------------------------------------------
with tab_quality:
    st.markdown('<div class="section-title">Water Quality Breakdown</div>', unsafe_allow_html=True)

    q1, q2, q3, q4 = st.columns(4, gap="medium")

    with q1:
        st.markdown(
            f"""
            <div class="glass-card metric-mini">
                <div class="metric-mini-label">Average pH</div>
                <div class="metric-mini-value">{"N/A" if pd.isna(avg_ph) else f"{avg_ph:.2f}"}</div>
                <div class="metric-mini-note">Target {PH_MIN}–{PH_MAX}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with q2:
        turbidity_display = "N/A" if pd.isna(avg_turbidity) else f"{avg_turbidity:.2f}"
        st.markdown(
            f"""
            <div class="glass-card metric-mini">
                <div class="metric-mini-label">Average Turbidity</div>
                <div class="metric-mini-value">{turbidity_display} NTU</div>
                <div class="metric-mini-note">Threshold ≤ {TURBIDITY_MAX} NTU</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with q3:
        bacteria_display = "N/A" if pd.isna(avg_bacteria) else f"{avg_bacteria:.0f}"
        st.markdown(
            f"""
            <div class="glass-card metric-mini">
                <div class="metric-mini-label">Average Bacteria</div>
                <div class="metric-mini-value">{bacteria_display}</div>
                <div class="metric-mini-note">CFU/mL, threshold ≤ {int(BACTERIA_MAX)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with q4:
        contaminant_display = "N/A" if pd.isna(avg_contaminant) else f"{avg_contaminant:.2f}"
        st.markdown(
            f"""
            <div class="glass-card metric-mini">
                <div class="metric-mini-label">Average Contaminant Level</div>
                <div class="metric-mini-value">{contaminant_display} ppm</div>
                <div class="metric-mini-note">Threshold ≤ {CONTAMINANT_MAX} ppm</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    st.markdown('<div class="section-title">Municipal Water Testing Results</div>', unsafe_allow_html=True)

    quality_cols = [
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
    quality_table = filtered[quality_cols].sort_values(
        by="Risk Level", key=lambda s: s.map({"High Risk": 0, "Moderate Risk": 1, "Safe": 2})
    )
    st.dataframe(
        quality_table.style.apply(highlight_risk, axis=1),
        width="stretch",
        hide_index=True,
        height=520,
    )
    st.caption(
        "🟢 Safe   🟠 Moderate Risk   🔴 High Risk — matching the colors on the map above. "
        "Displays field notes for Benue South and Abuja. For all other locations, the table shows "
        "the top disease risk (Cholera, Typhoid, Diarrheal) based on WHO safety levels."
    )

# -----------------------------------------------------------------------
# TAB 3 — COMMUNITY ACTION STEPS
# -----------------------------------------------------------------------
with tab_action:
    st.markdown('<div class="section-title">Community Action Steps</div>', unsafe_allow_html=True)

    s1, s2, s3 = st.columns(3, gap="medium")

    with s1:
        st.markdown(
            textwrap.dedent("""
            <div class="glass-card action-card">
                <div class="action-step">1</div>
                <div class="action-title">Check the local result</div>
                <div class="action-copy">
                    Confirm the Region, water source type, and latest Risk Level before taking action.
                </div>
            </div>
            """).strip(),
            unsafe_allow_html=True,
        )

    with s2:
        st.markdown(
            textwrap.dedent("""
            <div class="glass-card action-card">
                <div class="action-step">2</div>
                <div class="action-title">Treat or avoid unsafe water</div>
                <div class="action-copy">
                    For Moderate or High Risk readings, use an approved treatment method or an alternative safe source.
                </div>
            </div>
            """).strip(),
            unsafe_allow_html=True,
        )

    with s3:
        st.markdown(
            textwrap.dedent("""
            <div class="glass-card action-card">
                <div class="action-step">3</div>
                <div class="action-title">Report and request retesting</div>
                <div class="action-copy">
                    Escalate repeated unsafe readings to the appropriate local water authority and request verification.
                </div>
            </div>
            """).strip(),
            unsafe_allow_html=True,
        )

    st.write("")

    if high_count > 0:
        st.error(f"Urgent: {high_count} High Risk reading(s) are visible under the current filters.")
    elif moderate_count > 0:
        st.warning(f"{moderate_count} Moderate Risk reading(s) are visible. Treatment or retesting is recommended.")
    else:
        st.success("No Moderate or High Risk readings are visible under the current filters.")

# -----------------------------------------------------------------------
# FOOTER
# -----------------------------------------------------------------------
st.markdown("---")
st.caption(
    "Built for Grow with Google | Mentor Me Collective BUILD Project — "
    "UN SDG 6: Clean Water and Sanitation."
)
