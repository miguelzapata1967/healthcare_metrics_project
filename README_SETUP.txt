HEALTHCARE METRICS DASHBOARD - SIMPLE SETUP

1. Unzip this package into:
   C:\Users\mexar\OneDrive\DE_Academy\HealthCare_Metrics_Project

2. Keep healthcare_dashboard.py and the assets folder together.

3. Make sure PBJ_Daily_Nurse_Staffing_Q2_2024(1).csv is in that same project folder.
   The CSV is not included in this ZIP because it is your existing data file.

4. In VS Code terminal:
   cd "C:\Users\mexar\OneDrive\DE_Academy\HealthCare_Metrics_Project"
   python -m pip install -r requirements.txt
   python -m streamlit run healthcare_dashboard.py

5. Sidebar: select state(s), then select facility. Facility names include CMS provider IDs.

6. The images in assets are the two uploaded photos, plus a cropped DE Academy logo
   from the supplied reference screenshot. You may replace the logo asset with
   an approved official logo file later.

Note: The reference screenshot contains sample chart values and names. The app
calculates real values from the CMS staffing CSV instead of copying those samples.
