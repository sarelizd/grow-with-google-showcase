"""
AquaWatch Naija: Hyperlocal Water Quality Monitor Portal
=============================================================
UN SDG Goal 6: Clean Water and Sanitation

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
# CSS: Award-style glassmorphism, with a light "HydraFlow" finish layered
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

.sidebar-brand-stack{
    display:flex;
    flex-direction:column;
    align-items:flex-start;
    gap:8px;
    margin:0 0 22px;
}

.sidebar-logo-img{
    width:170px;
    height:auto;
    display:block;
}

.sidebar-sub{
    font-size:.85rem;
    font-weight:700;
    color:rgba(255,255,255,.68);
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
/* alert-grid: same equal-height technique as action-grid below - CSS
   Grid stretches all 3 banners to match the tallest one's content,
   regardless of how much text each status has (Safe's copy is much
   shorter than Moderate/High Risk's, so without this the Safe banner
   renders visibly shorter than the other two). */
.alert-grid{
    display:grid;
    grid-template-columns:repeat(3, 1fr);
    gap:20px;
}

@media (max-width: 700px){
    .alert-grid{grid-template-columns:1fr;}
}

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
/* action-grid: CSS Grid (not st.columns) so all 4 cards are forced to the
   SAME height regardless of how much text each one holds. Grid rows size
   to their tallest cell and stretch every cell to fill it by default, so
   card 4 (the longest) sets the height and cards 1-3 match it exactly. */
.action-grid{
    display:grid;
    grid-template-columns:repeat(2, 1fr);
    gap:20px;
    max-width:1000px;
    margin:0 auto;
}

@media (max-width: 650px){
    .action-grid{grid-template-columns:1fr;}
}

.action-card{
    min-height:210px;
    padding:18px;
    display:flex;
    flex-direction:column;
}

.action-step{
    width:34px;height:34px;
    border-radius:11px;
    display:grid;place-items:center;
    font-weight:850;
    color:white;
    background:linear-gradient(145deg,var(--cobalt),var(--mint));
    box-shadow:0 8px 18px rgba(0,0,0,.14);
    flex-shrink:0;
}

.action-title{
    margin-top:13px;
    font-size:.94rem;
    font-weight:820;
    color:white;
    flex-shrink:0;
    line-height:1.25;
    white-space:nowrap;
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
# Colors are tied directly to the 3 Risk Level buckets, not a continuous
# score, so the legend, map dots, and table row shading always agree on
# exactly which of the 3 categories a given site falls into.
RISK_COLORS = {
    "Safe": (52, 168, 83),          # green
    "Moderate Risk": (255, 152, 0), # orange
    "High Risk": (234, 67, 53),     # red
}

# -----------------------------------------------------------------------
# NIGERIA COUNTRY OUTLINE (for the map's border layer)
# -----------------------------------------------------------------------
# Simplified single-polygon boundary (58 vertices), sourced from the
# public "johan/world.geo.json" country-boundaries dataset on GitHub.
# The "road" basemap draws every country's border/label at equal weight,
# which makes Nigeria hard to pick out from neighbors like Niger. This
# highlighted stroke is drawn on top so Nigeria reads as the one country
# that matters here, and the jittered region dots visibly sit inside it.
NIGERIA_BORDER_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "id": "NGA",
            "properties": {"name": "Nigeria"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [8.500288, 4.771983], [7.462108, 4.412108], [7.082596, 4.464689],
                    [6.698072, 4.240594], [5.898173, 4.262453], [5.362805, 4.887971],
                    [5.033574, 5.611802], [4.325607, 6.270651], [3.57418, 6.2583],
                    [2.691702, 6.258817], [2.749063, 7.870734], [2.723793, 8.506845],
                    [2.912308, 9.137608], [3.220352, 9.444153], [3.705438, 10.06321],
                    [3.60007, 10.332186], [3.797112, 10.734746], [3.572216, 11.327939],
                    [3.61118, 11.660167], [3.680634, 12.552903], [3.967283, 12.956109],
                    [4.107946, 13.531216], [4.368344, 13.747482], [5.443058, 13.865924],
                    [6.445426, 13.492768], [6.820442, 13.115091], [7.330747, 13.098038],
                    [7.804671, 13.343527], [9.014933, 12.826659], [9.524928, 12.851102],
                    [10.114814, 13.277252], [10.701032, 13.246918], [10.989593, 13.387323],
                    [11.527803, 13.32898], [12.302071, 13.037189], [13.083987, 13.596147],
                    [13.318702, 13.556356], [13.995353, 12.461565], [14.181336, 12.483657],
                    [14.577178, 12.085361], [14.468192, 11.904752], [14.415379, 11.572369],
                    [13.57295, 10.798566], [13.308676, 10.160362], [13.1676, 9.640626],
                    [12.955468, 9.417772], [12.753672, 8.717763], [12.218872, 8.305824],
                    [12.063946, 7.799808], [11.839309, 7.397042], [11.745774, 6.981383],
                    [11.058788, 6.644427], [10.497375, 7.055358], [10.118277, 7.03877],
                    [9.522706, 6.453482], [9.233163, 6.444491], [8.757533, 5.479666],
                    [8.500288, 4.771983],
                ]],
            },
        }
    ],
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
# of where app.py lives, so a bare filename breaks once app.py moves into
# a subfolder like src/. This works from the repo root or from inside src/.
CSV_FILE = Path(__file__).parent / "nigeria_combined_water_data.csv"


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """Read the CSV and add a few helper columns used across the app."""
    df = pd.read_csv(path)

    # --- Build a single, easy-to-read Risk Level column -----------------
    # A site is flagged "High Risk" if 2+ readings breach a safety
    # threshold, "Moderate Risk" if exactly 1 breaches, else "Safe".
    #
    # Risk Level is graded ONLY on this specific water sample: pH,
    # Turbidity, Bacteria Count, and Contaminant Level (ppm). For the 9
    # Abuja / Benue South rows that have no numeric "Bacteria Count
    # (CFU/mL)" or "Contaminant Level (ppm)" reading, there's a single
    # supplementary signal that stands in for those two missing numeric
    # checks; it does NOT add extra checks for rows that already have
    # full numeric data:
    #
    # FIELD-REPORTED CONTAMINATION (9 Abuja / Benue South rows): these
    # rows have a qualitative field note in the separate "Contaminant
    # Level" TEXT column instead (e.g. "High (Coliforms up to 862
    # MPN/100mL)"). That severity word is mapped onto the same
    # breach-counting scheme used for the numeric thresholds, so those 9
    # sites are still screened on contamination severity rather than
    # being judged on pH/Turbidity alone.
    #
    # Disease Indicator / Risk (below) is a DELIBERATELY separate signal:
    # regional Cholera/Typhoid/Diarrheal case rates, not a water test
    # result, and is never folded into this breach count. The two are
    # allowed to disagree; see the caption on the dashboard for why.
    #
    # (Confirmed the field-note rows and the disease-case-rate rows never
    # overlap: the field-note rows are exactly the 9 rows missing disease
    # case-rate data, and vice versa.)
    FIELD_SEVERITY_BREACH_WEIGHT = {
        "extreme": 2,        # alone, enough to reach High Risk
        "very high": 2,      # alone, enough to reach High Risk
        "high": 1,
        "moderate-high": 1,
    }

    def field_reported_reasons(row):
        if pd.notna(row["Bacteria Count (CFU/mL)"]) and pd.notna(row["Contaminant Level (ppm)"]):
            return []  # real numeric readings exist for this row - nothing to fall back to
        note = row.get("Contaminant Level")
        if pd.isna(note) or not str(note).strip():
            return []
        severity_word = str(note).split("(")[0].strip().lower()
        weight = FIELD_SEVERITY_BREACH_WEIGHT.get(severity_word, 0)
        if weight == 0:
            return []
        # Just the severity tier (e.g. "Extreme", "Very High"), no raw
        # instrument readings, matching the plain style of every other
        # Risk Reason string ("High turbidity", "High bacteria count").
        # The full field note is still shown as-is in Disease Indicator /
        # Risk, so no detail is lost, just not duplicated here.
        label = f"Field-reported contamination: {severity_word.title()}"
        return [label] * weight

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
        reasons.extend(field_reported_reasons(row))

        # dict.fromkeys(...) de-dupes while keeping order, so a weight-2
        # reason reads once in the displayed Risk Reason text even though
        # it counts twice toward the High Risk threshold.
        display_reasons = list(dict.fromkeys(reasons))

        if len(reasons) >= 2:
            return "High Risk", "; ".join(display_reasons)
        elif len(reasons) == 1:
            return "Moderate Risk", reasons[0]
        else:
            return "Safe", "No thresholds breached"

    risk_results = df.apply(classify_risk, axis=1, result_type="expand")
    df["Risk Level"] = risk_results[0]
    df["Risk Reason"] = risk_results[1]

    # --- Fill blank Disease Indicator / Risk cells with a derived note ---
    # Only ~9 of 324 rows have a hand-written field note in this column
    # (from Abuja/Benue South site surveys); those are left untouched.
    #
    # IMPORTANT: Risk Level (above) and Disease Indicator / Risk (below)
    # are DELIBERATELY two separate signals, not one score:
    #   - Risk Level = whether THIS water sample breaches a chemistry/
    #     microbiology threshold (pH, Turbidity, Bacteria, Contaminant).
    #   - Disease Indicator / Risk = whether the surrounding REGION has
    #     elevated Cholera/Typhoid/Diarrheal case rates in the population.
    # A site's water can test clean today while its region still carries a
    # high disease burden from other causes (storage, distribution,
    # sanitation, a past outbreak), so these are allowed to disagree, and
    # the app.py caption below says so explicitly rather than implying a
    # single unified score. (We tried folding disease case-rates into Risk
    # Level directly and it back-fired: the dataset's Cholera/Typhoid
    # values don't sit on an absolute WHO alert scale the way the
    # thresholds assumed. For example, Typhoid tops out at 99 in this dataset, so
    # the ">= 100 = High" band could never fire, while Cholera's median of
    # 24 meant "% >= 10 = High" fired for 254 of 315 rows. Folding that
    # straight into Risk Level pushed 320 of 324 rows to High Risk,
    # destroying the dashboard's ability to distinguish sites at all.)
    #
    # For the text below, Cholera/Typhoid now use the SAME dataset-relative
    # approach already used for Diarrheal (90th/75th percentile of this
    # dataset) instead of a borrowed absolute epidemiological scale, so all
    # three diseases are judged consistently and the label actually varies
    # from region to region instead of saying "High Cholera" almost everywhere.
    cholera_p90 = df["Cholera Cases per 100,000 people"].quantile(0.90)
    cholera_p75 = df["Cholera Cases per 100,000 people"].quantile(0.75)
    typhoid_p90 = df["Typhoid Cases per 100,000 people"].quantile(0.90)
    typhoid_p75 = df["Typhoid Cases per 100,000 people"].quantile(0.75)
    diarrheal_p90 = df["Diarrheal Cases per 100,000 people"].quantile(0.90)
    diarrheal_p75 = df["Diarrheal Cases per 100,000 people"].quantile(0.75)

    def disease_indicator_note(row):
        original = row.get("Disease Indicator / Risk")
        if pd.notna(original) and str(original).strip():
            return original  # keep the real, field-observed note as-is

        candidates = []  # (severity_rank, label) - higher rank displayed first

        cholera = row.get("Cholera Cases per 100,000 people")
        if pd.notna(cholera):
            if cholera >= cholera_p90:
                candidates.append((2, "High incidence risk for Cholera"))
            elif cholera >= cholera_p75:
                candidates.append((1, "Moderate incidence risk for Cholera"))

        typhoid = row.get("Typhoid Cases per 100,000 people")
        if pd.notna(typhoid):
            if typhoid >= typhoid_p90:
                candidates.append((2, "High incidence risk for Typhoid"))
            elif typhoid >= typhoid_p75:
                candidates.append((1, "Moderate incidence risk for Typhoid"))

        diarrheal = row.get("Diarrheal Cases per 100,000 people")
        if pd.notna(diarrheal):
            if diarrheal >= diarrheal_p90:
                candidates.append((2, "High incidence risk for Diarrheal disease"))
            elif diarrheal >= diarrheal_p75:
                candidates.append((1, "Moderate incidence risk for Diarrheal disease"))

        if candidates:
            # Highest-severity reason wins; only that one is kept for display.
            _, top_label = max(candidates, key=lambda c: c[0])
            return top_label

        return "No elevated disease indicators recorded"

    df["Disease Indicator / Risk"] = df.apply(disease_indicator_note, axis=1)

    # --- Water Treatment Method: replace missing values with a clear label
    # (~98 of 324 rows have no treatment method recorded in the source data)
    df["Water Treatment Method"] = df["Water Treatment Method"].fillna("Data not provided")

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
# SIDEBAR: BRAND + FILTERS
# -----------------------------------------------------------------------

# Resolve path relative to this file's location
APP_DIR = Path(__file__).parent
LOGO_PATH = APP_DIR.parent / "docs" / "aquawatch-naija-logo.png"

with st.sidebar:
    st.markdown('<div class="sidebar-brand-stack">', unsafe_allow_html=True)
    st.image(str(LOGO_PATH), width=150)
    st.markdown(
        '<div class="sidebar-sub">Hyperlocal Water Quality Monitor</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown("### Location Filters")

    # NOTE: the dataset's finest geographic grain is "Region" (there is no
    # LGA-level breakdown in this CSV), so filters are Region + Water
    # Source Type: the same two dimensions the underlying data supports.
    region_options = ["All Regions"] + sorted(data["Region"].dropna().unique().tolist())
    selected_region = st.selectbox("Region", region_options)

    source_options = ["All Water Source Types"] + sorted(data["Water Source Type"].dropna().unique().tolist())
    selected_source = st.selectbox("Water Source Type", source_options)

    st.markdown("---")
    st.caption(
        f"**Safety thresholds:** pH ({PH_MIN}–{PH_MAX}) and Turbidity (≤ {TURBIDITY_MAX} NTU) "
        "reflect WHO drinking water guidance on operational/acceptability parameters, not "
        "formal numeric guideline values the way WHO sets for specific health-based "
        f"contaminants. Bacteria (≤ {int(BACTERIA_MAX)} CFU/mL) and Contaminant Level "
        f"(≤ {CONTAMINANT_MAX} ppm) are dataset-calibrated cutoffs with no WHO basis at all "
        "since the source data doesn't identify which pathogen or contaminant was tested. "
        "For context, WHO's actual standard for E. coli is zero detectable presence in any "
        "100 mL sample. High Risk = 2+ thresholds breached, Moderate = 1, Safe = 0. For the "
        "9 Abuja/Benue South rows missing numeric Bacteria/Contaminant readings, a "
        "qualitative field note (e.g., \"Extreme\", \"High\") stands in, so those sites are "
        "still screened on contamination, not judged on pH/Turbidity alone."
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
            <div class="hero-kicker">CLOSING NIGERIA'S WATER DATA GAP</div>
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
    f"(Region: *{selected_region}*, Source: *{selected_source}*)"
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
    # All 3 banners render inside ONE shared "alert-grid" CSS Grid
    # container (instead of 3 separate st.columns) for the same reason
    # as the action-grid in Tab 3: st.columns sizes each column to its
    # own content, and "Safe" has noticeably less copy than "Moderate
    # Risk" or "High Risk", so it would render as a visibly shorter box.
    st.markdown(
        f"""
        <div class="alert-grid">
            <div class="alert-safe">
                <div class="alert-icon">✓</div>
                <div>
                    <div class="alert-title">Safe: Meets Screening Range</div>
                    <div class="alert-copy">{safe_count} sample(s) currently pass all safety checks.</div>
                </div>
            </div>
            <div class="alert-caution">
                <div class="alert-icon">!</div>
                <div>
                    <div class="alert-title">Moderate Risk: Monitor Closely</div>
                    <div class="alert-copy">{moderate_count} sample(s) breach one threshold and should be monitored or retested.</div>
                </div>
            </div>
            <div class="alert-danger">
                <div class="alert-icon">⚠</div>
                <div>
                    <div class="alert-title">High Risk: Unsafe Without Treatment</div>
                    <div class="alert-copy">{high_count} sample(s) breach multiple thresholds and require urgent action.</div>
                </div>
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
# TAB 1: MAP  (pydeck, discrete Green/Orange/Red risk coloring)
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
                "<b>Year:</b> {Year}<br/>"
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
                map_style="road",  # road basemap for context; border layer above highlights Nigeria specifically
            )
        )

        st.caption("🟢 Safe   →   🟠 Moderate Risk   →   🔴 High Risk. Hover over a point for more details.")

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Safe", safe_count)
        with k2:
            st.metric("Moderate Risk", moderate_count)
        with k3:
            st.metric("High Risk", high_count)
        with k4:
            st.metric("Mapped Sources", len(map_df))

        st.markdown('<div class="section-title">Water Safety Status by Region</div>', unsafe_allow_html=True)

        map_table_cols = ["Year", "Region", "Water Source Type", "Risk Level", "pH Level", "Turbidity (NTU)"]
        map_table = filtered[map_table_cols].sort_values(
            by="Risk Level", key=lambda s: s.map({"High Risk": 0, "Moderate Risk": 1, "Safe": 2})
        )
        st.dataframe(
            map_table.style.apply(highlight_risk, axis=1),
            width="stretch",
            hide_index=True,
            height=340,
            # Same approach as the Municipal Water Testing Results table
            # below: every width is an explicit pixel value sized from
            # this data's real header/value lengths, not the vague
            # "small"/"medium"/"large" presets. Water Source Type in
            # particular can hold values up to 30 characters (e.g.
            # "Awulema Borehole (Ohimini LGA)"), which "medium" was not
            # reliably wide enough for.
            column_config={
                "Year": st.column_config.NumberColumn(width=80, format="%d"),
                "Region": st.column_config.TextColumn(width=125),
                "Water Source Type": st.column_config.TextColumn(width=240),
                "Risk Level": st.column_config.TextColumn(width=135),
                "pH Level": st.column_config.NumberColumn(width=100, format="%.2f"),
                "Turbidity (NTU)": st.column_config.NumberColumn(width=145, format="%.2f"),
            },
        )

# -----------------------------------------------------------------------
# TAB 2: WATER QUALITY BREAKDOWN
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

    st.info(
        "ℹ️ **Two different signals here.**\n\n"
        "- **Risk Level:** Does *this water sample* pass its safety checks? "
        "(pH, turbidity, bacteria, contaminants)\n"
        "- **Disease Indicator / Risk:** Is *this region* seeing higher rates of "
        "Cholera, Typhoid, or Diarrheal disease? (For the 9 Abuja/Benue South sites "
        "with no regional disease data, this instead shows the original contamination "
        "note recorded in the field for that sample.)\n\n"
        "These can disagree: a sample can show **Safe** while its region still shows "
        "a **High** disease indicator, because regional illness rates can come from "
        "other causes (storage, distribution, sanitation, a past outbreak), not just "
        "this one sample. **That's expected, not an error.**"
    )

    quality_cols = [
        "Year",
        "Region",
        "Water Source Type",
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

    # --- Show missing readings as "Data not provided" instead of "None" -
    # Bacteria Count and Contaminant Level are genuinely blank for some
    # rows (e.g. both Abuja readings). Streamlit's NumberColumn renders a
    # missing numeric value as the literal text "None", which reads like
    # a bug. This formats those two columns to text *only in this display
    # copy* of the table. quality_table is a local copy used solely for
    # rendering, so the real numeric columns in `filtered`/`df` (used for
    # the Average Bacteria Count / Average Contaminant Level metric cards
    # above and for Risk Level classification) are completely untouched.
    for numeric_col, decimals in [
        ("Bacteria Count (CFU/mL)", 0),
        ("Contaminant Level (ppm)", 2),
    ]:
        quality_table[numeric_col] = quality_table[numeric_col].apply(
            lambda v, d=decimals: "Data not provided" if pd.isna(v) else f"{v:.{d}f}"
        )

    # --- Shorten the 9 verbatim Abuja/Benue South field notes for display
    # These originally run up to 113 characters (e.g. "High Turbidity &
    # Microbial Hazard (Turbidity: 52.04 NTU far exceeds safe clarity
    # limits; Coliforms up to 237 MPN)") because they embed raw instrument
    # readings that duplicate what the pH/Turbidity/Bacteria columns
    # already show elsewhere in this same row. Keeping just the phrase
    # before the first "(" preserves the actual field-recorded severity
    # description (e.g. "High Turbidity & Microbial Hazard") without the
    # redundant numbers, cutting the column's max width by more than half.
    #
    # EXCEPTION: one of the 9 notes explicitly names diseases inside the
    # parenthetical ("Severe Pathogen Alert (Cholera / Typhoid / Dysentery
    # risk; Extremely high coliforms >1600 MPN)"). Blindly cutting at "("
    # would silently delete the only disease name in a column called
    # "Disease Indicator / Risk", so any disease keyword found in the
    # dropped portion is re-appended in short form instead of discarded.
    # Display-only: quality_table is a local copy, so the untouched
    # verbatim note is still what's stored in filtered/df.
    _DISEASE_KEYWORDS = ["Cholera", "Typhoid", "Dysentery", "Diarrheal", "Diarrhea"]

    def _shorten_field_note(v):
        if not isinstance(v, str):
            return v
        head = v.split(" (")[0].strip()
        head_lower = head.lower()
        mentioned = [
            kw for kw in _DISEASE_KEYWORDS
            if kw.lower() in v.lower() and kw.lower() not in head_lower
        ]
        if mentioned:
            return f"{head} ({'/'.join(dict.fromkeys(mentioned))} risk)"
        return head

    quality_table["Disease Indicator / Risk"] = quality_table["Disease Indicator / Risk"].apply(
        _shorten_field_note
    )

    st.dataframe(
        quality_table.style.apply(highlight_risk, axis=1),
        width="stretch",
        hide_index=True,
        height=520,
        # Every width below is an explicit pixel value sized from this
        # table's *actual* data (both the header text and the longest
        # real cell value in each column), not the "small"/"medium"/
        # "large" presets. Those presets were the root problem: several
        # headers here are much longer than they look:
        # "Bacteria Count (CFU/mL)", "Contaminant Level (ppm)", and
        # "Dissolved Oxygen (mg/L)" are all 23-24 characters, so
        # "small" was clipping the header text itself even though the
        # values underneath are short. "Risk Reason" (now max 65 chars,
        # after removing a duplicated-text bug in the field-reported
        # label) and "Disease Indicator / Risk" (now max 54 chars in this
        # display copy, after trimming the 9 verbatim field notes down to
        # their core phrase) both fit comfortably at the widths below.
        column_config={
            "Year": st.column_config.NumberColumn(width=80),
            "Region": st.column_config.TextColumn(width=125),
            "Water Source Type": st.column_config.TextColumn(width=240),
            "pH Level": st.column_config.NumberColumn(width=100, format="%.2f"),
            "Turbidity (NTU)": st.column_config.NumberColumn(width=145, format="%.2f"),
            # TextColumn (not NumberColumn) because quality_table now
            # holds these as pre-formatted text; see the "Data not
            # provided" formatting step above.
            "Bacteria Count (CFU/mL)": st.column_config.TextColumn(width=210),
            "Contaminant Level (ppm)": st.column_config.TextColumn(width=210),
            "Dissolved Oxygen (mg/L)": st.column_config.NumberColumn(width=200, format="%.2f"),
            "Water Treatment Method": st.column_config.TextColumn(width=200),
            "Risk Level": st.column_config.TextColumn(width=135),
            "Risk Reason": st.column_config.TextColumn(width=460),
            # 360 comfortably fits this column's new longest entry (54
            # chars, "Severe Pathogen Alert (Cholera/Typhoid/Dysentery
            # risk)") now that the 9 verbatim field notes are trimmed to
            # their core phrase (with any disease name preserved) in the
            # display step above.
            "Disease Indicator / Risk": st.column_config.TextColumn(width=360),
        },
    )
    st.caption("🟢 Safe   →   🟠 Moderate Risk   →   🔴 High Risk, matching the colors in the table above.")
    st.caption(
        "For the 9 Abuja/Benue South rows, this shows the original field note recorded for that "
        "sample. For every other row, it names the disease (Cholera, Typhoid, or Diarrheal) with the "
        "highest incidence relative to this dataset."
    )

# -----------------------------------------------------------------------
# TAB 3: COMMUNITY ACTION STEPS
# -----------------------------------------------------------------------
with tab_action:
    st.markdown('<div class="section-title">Community Action Steps</div>', unsafe_allow_html=True)

    # All 4 cards render inside ONE shared "action-grid" CSS Grid container
    # (instead of 4 separate st.columns) specifically so they come out as
    # equal-size squares. st.columns can't do this on its own: each column
    # sizes itself to its own content, so card 4 (much more text than 1-3)
    # would render taller than the rest and break the grid look. CSS Grid's
    # row items stretch to match the tallest cell by default, so all 4
    # cards always match card 4's height, however long its text is.
    st.markdown(
        textwrap.dedent("""
        <div class="action-grid">
            <div class="glass-card action-card">
                <div class="action-step">1</div>
                <div class="action-title">Check the local result</div>
                <div class="action-copy">
                    Confirm the <b>Year</b>, <b>Region</b>, <b>Water Source Type</b>, and latest <b>Risk Level</b> before taking action.
                    Refer to the <i>Water Safety Status by Region</i> table.
                </div>
            </div>
            <div class="glass-card action-card">
                <div class="action-step">2</div>
                <div class="action-title">Check the Disease Indicator / Risk</div>
                <div class="action-copy">
                    A water sample that's <b>Safe</b> doesn't rule out a regional disease signal. Check the
                    <b>Disease Indicator / Risk</b> column in the <i>Municipal Water Testing Results</i> table.
                    If it names any concern, such as elevated illness incidence or a
                    pathogen alert, use safe storage and handling (covered containers, clean
                    hands and utensils). Stay alert to symptoms locally. Only "No elevated
                    disease indicators recorded" means no extra precaution is needed here.
                </div>
            </div>
            <div class="glass-card action-card">
                <div class="action-step">3</div>
                <div class="action-title">Treat or avoid unsafe water</div>
                <div class="action-copy">
                    For <b>Moderate</b> or <b>High Risk</b> readings, use an approved treatment method or an alternative safe source.
                    Refer to the <i>Municipal Water Testing Results</i> table.
                </div>
            </div>
            <div class="glass-card action-card">
                <div class="action-step">4</div>
                <div class="action-title">Report and request retesting</div>
                <div class="action-copy">
                    Escalate repeated unsafe readings to the appropriate local water authority and request verification.
                </div>
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
