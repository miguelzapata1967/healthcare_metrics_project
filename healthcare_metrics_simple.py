"""Healthcare Metrics — beginner-friendly Streamlit dashboard.

Keep this script alongside PBJ_Daily_Nurse_Staffing_Q2_2024*.csv.
Run with: python -m streamlit run healthcare_metrics_final.py
You can also use VS Code's Run Python File button.
"""
from pathlib import Path
import subprocess
import sys

# STEP 0: If launched as ordinary Python, start Streamlit automatically.
if __name__ == "__main__" and not any("streamlit" in arg.lower() for arg in sys.argv[:1]):
    # Streamlit sets this environment variable when it runs a script.
    import os
    if not os.environ.get("STREAMLIT_SERVER_PORT") and not os.environ.get("STREAMLIT_RUNTIME_EXISTS"):
        # Detect Streamlit's active script context rather than relying on environment variables.
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        if get_script_run_ctx(suppress_warning=True) is None:
            subprocess.run([sys.executable, "-m", "streamlit", "run", str(Path(__file__).resolve())])
            sys.exit()

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Healthcare Metrics", layout="wide")
st.title("Healthcare Metrics: Nursing Home Staffing")
st.write("CMS payroll-based staffing data | April–June 2024")

# STEP 1: Find the CSV beside this script (including names ending in (1).csv).
folder = Path(__file__).resolve().parent
files = sorted(folder.glob("PBJ_Daily_Nurse_Staffing_Q2_2024*.csv"))
if not files:
    st.error("Staffing CSV file not found in this folder:")
    st.code(str(folder))
    st.stop()
st.caption(f"Source file: {files[0].name}")

# STEP 2: Read and clean the data.
@st.cache_data(show_spinner="Loading staffing data...")
def load_data(file_path):
    columns = ["PROVNUM", "PROVNAME", "STATE", "WorkDate", "MDScensus",
               "Hrs_RN", "Hrs_LPN", "Hrs_CNA",
               "Hrs_RN_ctr", "Hrs_LPN_ctr", "Hrs_CNA_ctr"]
    data = pd.read_csv(file_path, usecols=columns, encoding="cp1252",
                       dtype={"PROVNUM": "string", "WorkDate": "string"}, low_memory=False)
    original_rows = len(data)
    data = data.drop_duplicates()
    duplicate_rows = original_rows - len(data)
    # A date such as 20240401 means April 1, 2024.
    data["WorkDate"] = pd.to_datetime(data["WorkDate"], format="%Y%m%d", errors="coerce")
    hours_columns = ["Hrs_RN", "Hrs_LPN", "Hrs_CNA",
                     "Hrs_RN_ctr", "Hrs_LPN_ctr", "Hrs_CNA_ctr"]
    for column in ["MDScensus"] + hours_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    valid = data["MDScensus"].gt(0) & data["WorkDate"].notna()
    valid &= data[["Hrs_RN", "Hrs_LPN", "Hrs_CNA"]].notna().all(axis=1)
    valid &= data[["Hrs_RN", "Hrs_LPN", "Hrs_CNA"]].ge(0).all(axis=1)
    excluded_rows = int((~valid).sum())
    data = data.loc[valid].copy()

    # One row represents one facility on one day.
    data["NurseHours"] = data["Hrs_RN"] + data["Hrs_LPN"] + data["Hrs_CNA"]
    contract_cols = ["Hrs_RN_ctr", "Hrs_LPN_ctr", "Hrs_CNA_ctr"]
    # Do not count a missing contract value as zero.
    data["ContractHours"] = data[contract_cols].sum(axis=1, min_count=3)
    # Invalid contract-hour records should not enter the contract percentage.
    contract_valid = data[contract_cols].ge(0).all(axis=1)
    contract_valid &= data["ContractHours"].le(data["NurseHours"] + 0.01)
    data.loc[~contract_valid, "ContractHours"] = float("nan")
    data["DayType"] = data["WorkDate"].dt.dayofweek.map(
        lambda day: "Weekend" if day >= 5 else "Weekday")
    return data, duplicate_rows, excluded_rows

df, duplicate_rows, excluded_rows = load_data(str(files[0]))

# STEP 3: Filters (every graph below uses the selected records).
st.sidebar.header("Filters")
states = sorted(df["STATE"].dropna().unique().tolist())
chosen_states = st.sidebar.multiselect("States", states, default=states)
view = df[df["STATE"].isin(chosen_states)].copy()
# Use provider IDs, not names, because two facilities may have the same name.
options = view[["PROVNUM", "PROVNAME", "STATE"]].drop_duplicates("PROVNUM")
options["Label"] = options["PROVNAME"].fillna("Unknown") + " (" + options["STATE"].fillna("?") + ", " + options["PROVNUM"].astype(str) + ")"
labels = dict(zip(options["PROVNUM"].astype(str), options["Label"]))
chosen_ids = st.sidebar.multiselect("Facilities (optional)", sorted(labels),
                                     format_func=lambda key: labels[key])
if chosen_ids:
    view = view[view["PROVNUM"].isin(chosen_ids)]
if view.empty:
    st.warning("No matching records. Change the filters.")
    st.stop()

# STEP 4: Main metrics.
total_hours = view["NurseHours"].sum()
resident_days = view["MDScensus"].sum()
coverage = total_hours / resident_days if resident_days else float("nan")
# Use the SAME complete rows for numerator and denominator.
contract_data = view.dropna(subset=["ContractHours"])
contract_hours = contract_data["ContractHours"].sum()
eligible_hours = contract_data["NurseHours"].sum()
contract_share = contract_hours / eligible_hours if eligible_hours else float("nan")

one, two, three, four = st.columns(4)
one.metric("Total nursing hours", f"{total_hours:,.0f}")
two.metric("Hours per resident-day", f"{coverage:.2f}")
three.metric("Contract staffing share", f"{contract_share:.1%}")
four.metric("Facilities", f"{view['PROVNUM'].nunique():,}")
st.caption("Hours per resident-day is NOT a count of nurses per patient. These are historical records.")

# STEP 5: Charts.
st.header("1. How does staffing change each day?")
daily = view.groupby("WorkDate", as_index=False).agg(
    Hours=("NurseHours", "sum"), ResidentDays=("MDScensus", "sum"))
daily["HoursPerResidentDay"] = daily["Hours"] / daily["ResidentDays"]
st.plotly_chart(px.line(daily, x="WorkDate", y="HoursPerResidentDay",
                        title="Daily nursing hours per resident-day"), use_container_width=True)
st.write("A lower point means fewer recorded nursing hours per resident that day.")

st.header("2. Which nursing role provides the most hours?")
roles = view[["Hrs_RN", "Hrs_LPN", "Hrs_CNA"]].sum().reset_index()
roles.columns = ["Role", "Hours"]
roles["Role"] = roles["Role"].replace({"Hrs_RN": "RN", "Hrs_LPN": "LPN", "Hrs_CNA": "CNA"})
st.plotly_chart(px.bar(roles, x="Role", y="Hours", title="Nursing hours by role"), use_container_width=True)

st.header("3. Which states have higher staffing coverage?")
by_state = view.groupby("STATE", as_index=False).agg(
    Hours=("NurseHours", "sum"), ResidentDays=("MDScensus", "sum"))
by_state["HoursPerResidentDay"] = by_state["Hours"] / by_state["ResidentDays"]
st.plotly_chart(px.bar(by_state.sort_values("HoursPerResidentDay"), x="STATE",
                       y="HoursPerResidentDay", title="Staffing coverage by state"), use_container_width=True)

st.header("4. Are weekends staffed differently?")
by_day = view.groupby("DayType", as_index=False).agg(
    Hours=("NurseHours", "sum"), ResidentDays=("MDScensus", "sum"))
by_day["HoursPerResidentDay"] = by_day["Hours"] / by_day["ResidentDays"]
st.plotly_chart(px.bar(by_day, x="DayType", y="HoursPerResidentDay",
                       title="Weekday versus weekend coverage"), use_container_width=True)

st.header("5. Which facilities have the most hours or lowest coverage?")
by_facility = view.groupby(["PROVNUM", "PROVNAME", "STATE"], as_index=False).agg(
    Hours=("NurseHours", "sum"), ResidentDays=("MDScensus", "sum"),
    Days=("WorkDate", "nunique"))
by_facility["HoursPerResidentDay"] = by_facility["Hours"] / by_facility["ResidentDays"]
st.subheader("Top 10 facilities by total hours")
st.dataframe(by_facility.nlargest(10, "Hours"), hide_index=True, use_container_width=True)
st.subheader("Lowest coverage (at least 30 observed days)")
st.dataframe(by_facility[by_facility["Days"] >= 30].nsmallest(10, "HoursPerResidentDay"),
             hide_index=True, use_container_width=True)
st.warning("Low coverage alone does not prove understaffing. Investigate reporting and facility needs.")

st.header("6. Where is contract staffing more common?")
contract_state = contract_data.groupby("STATE", as_index=False).agg(
    ContractHours=("ContractHours", "sum"), Hours=("NurseHours", "sum"))
contract_state = contract_state[contract_state["Hours"] > 0].copy()
contract_state["ContractShare"] = contract_state["ContractHours"] / contract_state["Hours"]
st.plotly_chart(px.bar(contract_state.sort_values("ContractShare"), x="STATE",
                       y="ContractShare", title="Contract staffing share by state"), use_container_width=True)
st.caption("Only records with complete, valid contract hours are included in this percentage.")

# STEP 6: Data quality and download.
with st.expander("Data quality notes"):
    st.write(f"Exact duplicate rows removed: {duplicate_rows:,}")
    st.write(f"Rows excluded for invalid census, dates, or total nursing hours: {excluded_rows:,}")
    st.write(f"Rows with incomplete or invalid contract staffing hours: {view['ContractHours'].isna().sum():,}")
    st.write("The app does not use other CMS CSV files yet; those analyses can be added later.")
st.download_button("Download facility summary CSV", by_facility.to_csv(index=False),
                   "healthcare_facility_summary.csv", "text/csv")
