# Healthcare Metrics Project — Technical Documentation

**Application:** `healthcare_dashboard.py`  
**Language:** Python  
**Tools:** Pandas, Streamlit, Plotly Express

## 1. Source and file discovery

The dashboard searches for the PBJ staffing CSV in the same folder as the script:

```python
from pathlib import Path
ROOT = Path(__file__).resolve().parent
matches = sorted(ROOT.glob("PBJ_Daily_Nurse_Staffing_Q2_2024*.csv"))
```

The wildcard accepts a filename such as `PBJ_Daily_Nurse_Staffing_Q2_2024(1).csv`. `Path.glob()` receives a **relative filename pattern**, not an absolute Windows path.

## 2. Load only the required columns

```python
fields = [
    "PROVNUM", "PROVNAME", "STATE", "WorkDate", "MDScensus",
    "Hrs_RN", "Hrs_LPN", "Hrs_CNA",
    "Hrs_RN_ctr", "Hrs_LPN_ctr", "Hrs_CNA_ctr"
]
data = pd.read_csv(path, usecols=fields, encoding="cp1252",
                   dtype={"PROVNUM": "string", "WorkDate": "string", "STATE": "string"})
```

Reading only needed columns reduces memory use. Keeping `PROVNUM` as text protects leading zeros in CMS provider identifiers.

## 3. Cleaning workflow

1. Remove exact duplicate rows with `drop_duplicates()`.
2. Convert `WorkDate` from `YYYYMMDD` text to a date using `pd.to_datetime(..., format="%Y%m%d", errors="coerce")`.
3. Convert census and staffing hours to numeric values.
4. Retain records with valid dates, positive census, and complete, nonnegative RN/LPN/CNA hours.
5. Add calculated columns without overwriting the source CSV.
6. Preserve unusual nonnegative observations for review rather than silently deleting them.

The original dataset is not edited in place. `@st.cache_data` caches the loaded and transformed DataFrame to avoid repeating expensive reads unnecessarily.

## 4. Calculated fields

```python
data["NurseHours"] = data["Hrs_RN"] + data["Hrs_LPN"] + data["Hrs_CNA"]

data["ContractHours"] = data[
    ["Hrs_RN_ctr", "Hrs_LPN_ctr", "Hrs_CNA_ctr"]
].sum(axis=1, min_count=3)
```

The application also excludes negative contract components from the contract-share calculation. `DayType` is created from `WorkDate` (Monday–Friday vs. Saturday–Sunday).

**Hours per resident-day (HPRD):**

```python
hprd = selected_rows["NurseHours"].sum() / selected_rows["MDScensus"].sum()
```

**Contract share:**

```python
complete = selected_rows.dropna(subset=["ContractHours"])
contract_share = complete["ContractHours"].sum() / complete["NurseHours"].sum()
```

Both formulas use the same records in numerator and denominator as appropriate. In production, protect against a zero denominator and display missing values instead of implying a measured zero.

## 5. Filtering

The sidebar allows selection of:

- One, several, or all states (an empty state selection means all).
- Facilities available within the selected states.
- A date range inside the available quarter.

Facility options include **facility name, state, and provider number** to distinguish duplicate names. When states change, invalid facility selections are removed from session state. All KPI and chart calculations use the resulting filtered DataFrame.

## 6. Aggregation and visualizations

Pandas `groupby()` and `agg()` calculate summaries:

```python
by_state = filtered.groupby("STATE", as_index=False).agg(
    Hours=("NurseHours", "sum"),
    Census=("MDScensus", "sum"),
    Facilities=("PROVNUM", "nunique")
)
by_state["Coverage"] = by_state["Hours"] / by_state["Census"]
```

Plotly Express creates line and bar charts. Streamlit displays them with `st.plotly_chart()`, shows KPI cards with `st.metric()`, and displays tables with `st.dataframe()`. A CSV download button exports the currently filtered facility summary.

## 7. Styling and images

The dashboard uses custom CSS injected through `st.markdown(..., unsafe_allow_html=True)` to style a light burgundy background, dark burgundy text, cards, and sidebar. The `assets/` folder contains the DE Academy logo/banner graphic and the supplied photographs of Chris Garzon and Miguel Zapata. Image bytes are embedded in the banner as base64 data URLs. Only trusted, local assets should be used with this HTML approach.

## 8. Application sections

`Home`, `Staffing Metrics`, `State Analysis`, `Facility Analysis`, `Comparisons`, `Data Tables`, and `About the Project` are chosen through a Streamlit sidebar radio control. These are views within one application, not separate Python modules.

## 9. Run and troubleshoot

```powershell
cd "C:\Users\mexar\OneDrive\DE_Academy\HealthCare_Metrics_Project"
python -m pip install -r requirements.txt
python -m streamlit run healthcare_dashboard.py
```

- **`missing ScriptRunContext`**: The script was launched as ordinary Python; use `python -m streamlit run ...`.
- **`IndexError: list index out of range`**: The CSV search returned no files; confirm the filename and directory.
- **`Non-relative patterns are unsupported`**: An absolute path was incorrectly passed to `Path.glob()`; use a relative filename pattern.
- **Missing images**: Check that the `assets/` directory sits next to the script.
- **Wrong facility results**: Verify the selected state, provider number, facility selection, and date range.

## 10. Data-quality validation checklist

- Confirm source row count and exact duplicate count.
- Count invalid/missing dates, census values, and staffing hours.
- Check that retained RN/LPN/CNA values are nonnegative.
- Verify unique provider IDs and state codes.
- Recalculate selected HPRD and contract share by hand from a small sample.
- Investigate facilities with zero or near-zero reported staffing.
- Confirm all filter selections update KPIs, charts, and downloads.
- Verify that figures are labeled with their reporting period.

## 11. Current boundaries

The present code reads **only the PBJ staffing CSV**. The other CMS files are not automatically merged or analyzed. Future integration should validate join keys, granularity (facility/day vs. citation vs. ownership), data collection dates, and one-to-many relationships to avoid multiplying staffing totals.

## AI assistance disclosure

AI assistance was used in code drafting, troubleshooting, visual styling, and documentation. The project creator should test the application in the local environment and verify calculations and interpretations before submitting or publishing.
# AWS S3 and Streamlit Cloud Deployment

**Implementation date:** October 8, 2026

### Deployment Configuration

| Component | Configuration |
|---|---|
| GitHub repository | `miguelzapata1967/healthcare_metrics_project` |
| Branch | `main` |
| Entry point | `healthcare_dashboard.py` |
| Hosting | Streamlit Community Cloud |
| Data storage | Amazon S3 |
| Bucket | `mzapata-healthcare-metrics-2026` |
| Region | `us-west-1` |
| S3 object | `PBJ_Daily_Nurse_Staffing_Q2_2024.csv` |

### Data Pipeline

1. CMS PBJ CSV is stored in a private Amazon S3 bucket.
2. Streamlit obtains AWS credentials through its Secrets configuration.
3. Boto3 retrieves the dataset from S3.
4. Pandas reads and processes the CSV.
5. Data cleaning validates dates, census, staffing hours, and duplicate records.
6. Calculated metrics feed the interactive Streamlit dashboard.
7. Plotly renders charts for filtered results.

### Troubleshooting History

**Issue 1 — GitHub upload restriction**

The dataset exceeded GitHub's 25 MB browser upload limit.

Resolution: Store the approximately 209.5 MB dataset in AWS S3 rather than the public GitHub repository.

**Issue 2 — Dataset unavailable**

The cloud application initially could not find a local CSV or usable AWS configuration.

Resolution: Configure the S3 bucket and object key in the Python application.

**Issue 3 — Streamlit Secrets mismatch**

The AWS access key variable was initially entered as `AWS_ACCESS_KEY` instead of `AWS_ACCESS_KEY_ID`.

Resolution: Correct the Secrets variable names to match the Python code.

Required credential names include:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION
```

The bucket is also configured in the application code. Credentials must never be committed to GitHub.

**Issue 4 — Application runtime error**

Following deployment, Streamlit displayed an "Error running app" page.

Status: Root cause not yet established. The next diagnostic step is to inspect Streamlit application logs for Python exceptions, memory errors, dependency failures, or AWS access errors.

### Security

- Keep S3 Block Public Access enabled.
- Use a dedicated IAM identity with minimum required permissions.
- Store credentials only in Streamlit Secrets.
- Never publish access keys in source code or documentation.
- Verify that public visitors cannot access administrative functions.

### Published Application

[Healthcare Metrics Streamlit Dashboard](https://miguelzapata1967-healthcare-metrics-healthcare-dashboard-euzqg2.streamlit.app/)

**Technical deployment status:** URL established; runtime troubleshooting and final functional testing pending.
