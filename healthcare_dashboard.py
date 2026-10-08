"""Healthcare Metrics dashboard. Run: python -m streamlit run healthcare_dashboard.py

Put this file, the assets folder, and CMS CSV files in the same project folder.

"""

from pathlib import Path

import base64

import pandas as pd

import plotly.express as px

import streamlit as st



st.set_page_config(page_title="Healthcare Metrics | DE Academy", layout="wide", initial_sidebar_state="expanded")

ROOT = Path(__file__).resolve().parent

ASSETS = ROOT / "assets"

BURGUNDY = "#68152c"



def picture(filename):

    """Convert a local picture into text that can be displayed in HTML."""

    path = ASSETS / filename

    if not path.exists():

        return ""

    return base64.b64encode(path.read_bytes()).decode("ascii")



# STEP 1: Dashboard colors and banner

st.markdown("""

<style>

.stApp {background: #f8eeee; color: #481325;}

[data-testid="stSidebar"] {background: #f2dfe2;}

h1,h2,h3,h4,p,label,div[data-testid="stMetricLabel"] {color:#481325;}

[data-testid="stMetric"] {background:#fff9f8; border:1px solid #e4c8cd; padding:18px; border-radius:13px;}

[data-testid="stMetricValue"] {color:#68152c;}

[data-testid="stPlotlyChart"], [data-testid="stDataFrame"] {background:#fff9f8; border-radius:12px;}

.stButton button[kind="primary"] {background:#68152c; border-color:#68152c; color:white;}

.banner {background:linear-gradient(105deg,#f6dfe2,#e9c3ca);border-radius:14px;

 padding:15px 22px;display:flex;align-items:center;justify-content:space-between;

 gap:20px;flex-wrap:wrap;border:1px solid #dfb8bf;margin-bottom:22px;}

.banner-logo {max-width:330px;width:100%;height:auto;mix-blend-mode:multiply;}

.person {display:flex;align-items:center;gap:11px;color:#4b1222;}

.person img {width:82px;height:82px;object-fit:cover;border-radius:50%;border:3px solid white;}

.person strong {display:block;font-size:17px;}

.person small {font-size:13px;}

</style>

""", unsafe_allow_html=True)

logo = picture("de_academy_banner_logo.png")

chris = picture("chris_founder.png")

miguel = picture("miguel_owner.png")

st.markdown(f'''<div class="banner">

  <div><img class="banner-logo" src="data:image/png;base64,{logo}" alt="DE Academy"><div style="font-size:12px;letter-spacing:2px">DATA · SKILLS · OPPORTUNITY</div></div>

  <div class="person"><img src="data:image/png;base64,{chris}" alt="Founder photo"><div><strong>Chris Garzon</strong><small>Founder · DE Academy</small></div></div>

  <div class="person"><img src="data:image/png;base64,{miguel}" alt="Project owner photo"><div><strong>Miguel Zapata</strong><small>Healthcare Metrics Project Creator</small></div></div>

</div>''', unsafe_allow_html=True)

st.title("Healthcare Metrics: Nursing Home Staffing")

st.caption("CMS payroll-based staffing data · April–June 2024 · Historical data")



# STEP 2: Find and load the CSV from the same folder as this script.

@st.cache_data(show_spinner="Loading CMS staffing data...")

def load_data(path):

    fields = ["PROVNUM", "PROVNAME", "STATE", "WorkDate", "MDScensus",

              "Hrs_RN", "Hrs_LPN", "Hrs_CNA", "Hrs_RN_ctr", "Hrs_LPN_ctr", "Hrs_CNA_ctr"]

    data = pd.read_csv(path, usecols=fields, encoding="cp1252",

                       dtype={"PROVNUM":"string", "WorkDate":"string", "STATE":"string"})

    before = len(data)

    data = data.drop_duplicates()

    data["WorkDate"] = pd.to_datetime(data["WorkDate"], format="%Y%m%d", errors="coerce")

    for col in fields[4:]:

        data[col] = pd.to_numeric(data[col], errors="coerce")

    hours = ["Hrs_RN", "Hrs_LPN", "Hrs_CNA"]

    valid = (data["MDScensus"] > 0) & data["WorkDate"].notna()

    valid &= data[hours].notna().all(axis=1) & data[hours].ge(0).all(axis=1)

    removed = len(data) - int(valid.sum())

    data = data.loc[valid].copy()

    data["NurseHours"] = data[hours].sum(axis=1)

    contracts = ["Hrs_RN_ctr", "Hrs_LPN_ctr", "Hrs_CNA_ctr"]

    data["ContractHours"] = data[contracts].sum(axis=1, min_count=3)

    data.loc[data[contracts].lt(0).any(axis=1), "ContractHours"] = float("nan")

    data["DayType"] = data["WorkDate"].dt.dayofweek.map(lambda n: "Weekend" if n >= 5 else "Weekday")

    data["FacilityLabel"] = (data["PROVNAME"].fillna("Unknown facility") +

                              " · " + data["STATE"].fillna("??") + " · " + data["PROVNUM"].fillna("Unknown"))

    return data, before, removed



matches = sorted(ROOT.glob("PBJ_Daily_Nurse_Staffing_Q2_2024*.csv"))

if not matches:

    st.error("Staffing CSV not found. Put PBJ_Daily_Nurse_Staffing_Q2_2024(1).csv beside this script.")

    st.write("Folder searched:", str(ROOT))

    st.stop()

try:

    df, original_rows, removed_rows = load_data(str(matches[0]))

except Exception as exc:

    st.error(f"Could not read staffing CSV: {exc}")

    st.stop()

if df.empty:

    st.warning("No valid records were found in the staffing CSV.")

    st.stop()



# STEP 3: State, facility and date filters. Facility choices update with states.

st.sidebar.header("Dashboard navigation")

section = st.sidebar.radio("View", ["Home", "Staffing Metrics", "State Analysis",

                                    "Facility Analysis", "Comparisons", "Data Tables", "About the Project"])

st.sidebar.divider()

st.sidebar.subheader("Filters")

states = sorted(df["STATE"].dropna().unique().tolist())

selected_states = st.sidebar.multiselect("State(s) — empty means all", states, default=[])

state_df = df[df["STATE"].isin(selected_states)] if selected_states else df



# Use unique CMS provider numbers rather than facility names alone.

facility_options = (state_df[["PROVNUM", "FacilityLabel"]].drop_duplicates()

                    .dropna(subset=["PROVNUM"]).sort_values("FacilityLabel"))

labels = dict(zip(facility_options["PROVNUM"], facility_options["FacilityLabel"]))

valid_ids = set(labels)

# Remove old selections if a state change makes them invalid.

if "facility_ids" not in st.session_state:

    st.session_state.facility_ids = []

st.session_state.facility_ids = [x for x in st.session_state.facility_ids if x in valid_ids]

selected_ids = st.sidebar.multiselect("Facility (optional)", list(labels),

                                      format_func=lambda code: labels.get(code, code), key="facility_ids")

filtered = state_df[state_df["PROVNUM"].isin(selected_ids)] if selected_ids else state_df

minimum, maximum = df["WorkDate"].min().date(), df["WorkDate"].max().date()

range_value = st.sidebar.date_input("Date range", value=(minimum, maximum), min_value=minimum, max_value=maximum)

if isinstance(range_value, tuple) and len(range_value) == 2:

    filtered = filtered[filtered["WorkDate"].between(pd.Timestamp(range_value[0]), pd.Timestamp(range_value[1]))]

# STEP 3B: ReadMe files in the sidebar (reading only).
st.sidebar.divider()
st.sidebar.subheader("ReadMe Files")
readme_choices = {
    "README.md — Project Introduction": "README.md",
    "readme_analysis.md — Findings and Insights": "readme_analysis.md",
    "readme_tech.md — Technical Process": "readme_tech.md",
}
selected_readme = st.sidebar.selectbox(
    "Select a document to read",
    options=["Return to Dashboard"] + list(readme_choices),
    index=0,
)

if selected_readme != "Return to Dashboard":
    document_path = ROOT / readme_choices[selected_readme]
    st.header(selected_readme.split(" — ")[0])
    if document_path.is_file():
        st.markdown(document_path.read_text(encoding="utf-8-sig"))
    else:
        st.warning(f"Document not found: {document_path.name}")
        st.info("Save this Markdown file in the same folder as healthcare_dashboard.py.")
    st.stop()

if filtered.empty:

    st.warning("No matching records. Change the state, facility, or date filters.")

    st.stop()



# STEP 4: Metrics. Hours per resident-day is NOT the number of nurses per patient.

total_hours = filtered["NurseHours"].sum()

resident_days = filtered["MDScensus"].sum()

coverage = total_hours / resident_days if resident_days else float("nan")

complete_contract = filtered.dropna(subset=["ContractHours"])

contract_total = complete_contract["ContractHours"].sum()

contract_denominator = complete_contract["NurseHours"].sum()

contract_share = contract_total / contract_denominator if contract_denominator else float("nan")

a,b,c,d = st.columns(4)

a.metric("Total Nursing Hours", f"{total_hours:,.0f}")

b.metric("Hours per Resident-Day", f"{coverage:.2f}")

c.metric("Contract Staffing Share", f"{contract_share:.1%}")

d.metric("Facilities", f"{filtered['PROVNUM'].nunique():,}")

st.caption("All results update with the filters. Contract share uses only records with complete contract-hour data.")



# STEP 5: Build tables used by the charts.

daily = filtered.groupby("WorkDate", as_index=False).agg(Hours=("NurseHours", "sum"), Census=("MDScensus", "sum"))

daily["Coverage"] = daily["Hours"] / daily["Census"]

roles = filtered[["Hrs_RN", "Hrs_LPN", "Hrs_CNA"]].sum().rename({"Hrs_RN":"RN", "Hrs_LPN":"LPN", "Hrs_CNA":"CNA"}).reset_index()

roles.columns = ["Role", "Hours"]

by_state = filtered.groupby("STATE", as_index=False).agg(Hours=("NurseHours", "sum"), Census=("MDScensus", "sum"), Facilities=("PROVNUM", "nunique"))

by_state["Coverage"] = by_state["Hours"] / by_state["Census"]

by_day = filtered.groupby("DayType", as_index=False).agg(Hours=("NurseHours", "sum"), Census=("MDScensus", "sum"))

by_day["Coverage"] = by_day["Hours"] / by_day["Census"]

by_facility = filtered.groupby(["PROVNUM", "PROVNAME", "STATE"], as_index=False).agg(Hours=("NurseHours", "sum"), Census=("MDScensus", "sum"), Days=("WorkDate", "nunique"))

by_facility["Coverage"] = by_facility["Hours"] / by_facility["Census"]

contract_state = complete_contract.groupby("STATE", as_index=False).agg(Contract=("ContractHours", "sum"), Hours=("NurseHours", "sum"))

contract_state = contract_state[contract_state["Hours"] > 0].copy()

contract_state["ContractShare"] = contract_state["Contract"] / contract_state["Hours"]



def chart(fig):

    fig.update_layout(paper_bgcolor="#fff9f8", plot_bgcolor="#fff9f8",

                      font_color="#481325", colorway=[BURGUNDY, "#bf8290", "#dbacb5"],

                      margin=dict(l=15, r=15, t=55, b=15))

    st.plotly_chart(fig, use_container_width=True)



if section in ("Home", "Staffing Metrics"):

    st.subheader("Staffing overview")

    left, right = st.columns(2)

    with left:

        chart(px.line(daily, x="WorkDate", y="Coverage", title="Daily Nursing Hours per Resident-Day"))

    with right:

        chart(px.bar(roles, x="Role", y="Hours", title="Hours by Nursing Role"))

    left, right = st.columns(2)

    with left:

        chart(px.bar(by_day, x="DayType", y="Coverage", title="Weekday vs. Weekend Coverage"))

    with right:

        chart(px.bar(contract_state.sort_values("ContractShare"), x="STATE", y="ContractShare", title="Contract Staffing Share by State"))



if section in ("Home", "State Analysis", "Comparisons"):

    st.subheader("State analysis")

    chart(px.bar(by_state.sort_values("Coverage"), x="STATE", y="Coverage", title="Nursing Hours per Resident-Day by State"))

    st.dataframe(by_state.sort_values("Coverage", ascending=False), hide_index=True, use_container_width=True)



if section in ("Home", "Facility Analysis", "Comparisons"):

    st.subheader("Facility analysis")

    left, right = st.columns(2)

    with left:

        st.markdown("**Top 10 facilities by nursing hours**")

        st.dataframe(by_facility.nlargest(10, "Hours"), hide_index=True, use_container_width=True)

    with right:

        st.markdown("**Lowest coverage (at least 30 recorded days)**")

        st.dataframe(by_facility[by_facility["Days"] >= 30].nsmallest(10, "Coverage"), hide_index=True, use_container_width=True)

    st.info("Low recorded coverage is a signal for investigation, not proof of inadequate care.")



if section == "Data Tables":

    st.subheader("Data and downloads")

    st.write(f"Original rows: {original_rows:,} · Rows excluded after removing duplicates and invalid essential values: {removed_rows:,}")

    st.dataframe(filtered.head(1000), hide_index=True, use_container_width=True)

    st.download_button("Download filtered facility summary", by_facility.to_csv(index=False).encode("utf-8"),

                       file_name="healthcare_facility_summary.csv", mime="text/csv")



if section == "About the Project":

    st.subheader("About the project")

    st.write("Project creator: Miguel Zapata | DE Academy founder: Chris Garzon")

    st.write("Source: CMS Payroll-Based Journal daily nurse staffing, April–June 2024.")

    st.write("The analysis uses RN, LPN and CNA staffing hours, resident census, and contract nursing hours.")

    st.write("Coverage = total RN + LPN + CNA hours divided by resident-days. This is not a headcount ratio.")

    st.write("Historical, observational data cannot establish that staffing differences caused care outcomes.")



st.divider()

st.caption("Healthcare Metrics Project · DE Academy · Miguel Zapata · CMS historical data")
