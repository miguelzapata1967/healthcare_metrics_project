# Healthcare Metrics Project

**Project creator:** Miguel Zapata  
**Educational affiliation:** DE Academy  
**DE Academy founder:** Chris Garzon  
**Primary source:** Centers for Medicare & Medicaid Services (CMS), Payroll-Based Journal (PBJ), April–June 2024

## Project overview

This project studies daily nursing staffing and resident census information from U.S. nursing homes and skilled nursing facilities. The goal is to turn a large CSV into understandable measures, interactive charts, and questions that healthcare administrators can investigate.

This is an **educational, historical, descriptive analysis**. It does not establish whether a facility provided safe or adequate care.

## Questions

- How many RN, LPN, and CNA hours were reported?
- How many nursing hours were available per resident-day?
- How does recorded coverage differ by state, facility, and weekday/weekend?
- What share of nursing hours came from contracted staff?
- Which facilities warrant closer review because of unusual staffing records?

## Technology

Python, Pandas, Streamlit, Plotly Express, and local CMS CSV files. The dashboard has a light burgundy background, dark burgundy text, DE Academy branding, and project attribution.

## Dashboard pages

- **Home:** overview and key charts
- **Staffing Metrics:** daily coverage, nursing roles, weekday/weekend comparison
- **State Analysis:** staffing coverage and state table
- **Facility Analysis:** highest recorded hours and lowest coverage (with minimum observed-day requirement)
- **Comparisons:** state-level contract staffing
- **Data Tables:** filtered records and downloadable facility summary
- **About the Project:** source, credits, and interpretation cautions

State, facility, and date selections filter the displayed results. Facilities are identified by CMS provider number (`PROVNUM`) rather than name alone.

## Folder layout

```text
HealthCare_Metrics_Project/
├── healthcare_dashboard.py
├── requirements.txt
├── README.md
├── readme_analysis.md
├── readme_tech.md
├── PBJ_Daily_Nurse_Staffing_Q2_2024(1).csv
├── assets/
│   ├── de_academy_banner_logo.png
│   ├── chris_founder.png
│   └── miguel_owner.png
└── other CMS CSV files (reserved for future analysis)
```

## How to run

Open a VS Code terminal in the project folder and execute:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run healthcare_dashboard.py
```

The dashboard automatically searches its own folder for a file beginning with `PBJ_Daily_Nurse_Staffing_Q2_2024` and ending in `.csv`.

## Results and methodology

See [readme_analysis.md](readme_analysis.md) for findings and [readme_tech.md](readme_tech.md) for code, cleaning rules, and formulas.

## Scope and limitations

The current dashboard **analyzes the PBJ staffing CSV only**. Other uploaded CMS datasets (citations, penalties, ownership, vaccination, and value-based purchasing) are available for future modules, but are **not yet incorporated into the displayed metrics**. Comparisons across different CMS reporting periods would require careful matching and qualification.

## AI assistance disclosure

AI tools assisted with Python code drafting, debugging, Streamlit styling, and documentation. The project owner is responsible for reviewing calculations, verifying results against source data, and explaining the work. Findings should not be treated as independently audited.
