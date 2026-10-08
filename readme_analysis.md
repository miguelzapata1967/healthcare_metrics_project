# Healthcare Metrics Project — Analysis and Findings

**Author/project creator:** Miguel Zapata  
**Source:** CMS Payroll-Based Journal (PBJ), Q2 2024 (April 1–June 30, 2024)

## 1. Purpose

The analysis asks how recorded nursing staffing compares with resident population across nursing homes and skilled nursing facilities. It measures **hours per resident-day (HPRD)**, not a literal headcount of nurses per patient.

## 2. Data reviewed and cleaning

The source contains **1,325,324 daily records**. The initial profiling found **0 exact duplicate rows**. **320 records** were excluded for invalid or missing essential date, census, or RN/LPN/CNA hour values, leaving **1,325,004 valid records**, **14,564 distinct provider IDs**, and **52 state/territory codes**. These figures are from the initial full-file profiling of the uploaded Q2 2024 PBJ dataset; a filtered dashboard will naturally show different totals.

Cleaning rules: parse `WorkDate`; require a positive `MDScensus`; require complete, nonnegative RN, LPN, and CNA hour values; preserve provider IDs as text; and calculate daily staffing totals. Contract-hour comparisons require complete contract fields. Unusual but nonnegative records are not automatically removed, so they can be investigated.

## 3. Five main metrics

| Metric | Calculation | Overall result |
|---|---|---:|
| Total nursing hours | RN + LPN + CNA hours | 364,144,704 hours |
| Hours per resident-day | Sum of nursing hours / sum of daily census | 3.294 |
| Contract staffing share | Complete contract hours / matching total nursing hours | 7.69% |
| Average daily census | Census summed across facilities and days / number of valid facility-day records | See live filtered dashboard; do not confuse this with a facility's average |
| Facilities represented | Distinct CMS provider IDs | 14,564 |

The dataset contains **110,554,155 resident-days** across valid records. The nursing-hour total consists of approximately **46.12 million RN**, **87.70 million LPN**, and **230.32 million CNA** hours.

### What these metrics mean

- **Total hours** describes volume of staffing work. Larger facilities may naturally report more hours.
- **HPRD** adjusts hours for the resident census and is more comparable than raw hours, but does not by itself measure quality of care.
- **Contract share** indicates reliance on contracted nursing hours, not whether contract staffing is good or bad.
- **Census** helps describe resident load; facility averages should be computed within each facility before comparison.
- **Facility count** measures unique providers in the filtered data, not the number of hospitals.

## 4. Finding: weekdays vs. weekends

- **Weekdays:** approximately **3.384 HPRD**.
- **Weekends:** approximately **3.068 HPRD**.

**Storytelling interpretation:** The pooled dataset shows lower recorded nursing coverage on weekends. This pattern is worth examining at the facility level and by nursing role. It does **not** prove that patients received inadequate care.

**How to present it:** “I divided nursing hours by resident-days for weekdays and weekends. Weekend coverage was lower in the combined data. My next question is whether that pattern appears consistently across facilities.”

## 5. Finding: variation across states and territories

The highest pooled HPRD values in the initial profiling included **AK 5.412**, **OR 4.191**, **PR 4.122**, **ND 4.078**, and **HI 3.991**. Lower values included **MO 2.402**, **TX 2.672**, **OK 2.776**, **IN 2.821**, and **NM 2.835**.

**Storytelling interpretation:** Coverage varies geographically. These are descriptive pooled figures, not a ranking of healthcare quality. Differences may reflect facility mix, patient needs, reporting, and other factors not controlled for here. The dashboard's state filter lets users inspect one or several jurisdictions.

## 6. Finding: facilities with the most recorded nursing hours

The initial profiling's highest-hour facilities included:

| Facility | State | Recorded nursing hours |
|---|---|---:|
| ISABELLA GERIATRIC CENTER INC | NY | 199,144.72 |
| COLER REHABILITATION AND NURSING CARE CENTER | NY | 189,810.35 |
| KINGS HARBOR MULTICARE CENTER | NY | 188,650.15 |
| THE PLAZA REHAB AND NURSING CENTER | NY | 184,704.83 |
| RUTLAND NURSING HOME, INC | NY | 183,568.98 |

**Interpretation:** High total hours can be associated with larger resident populations. Do not interpret these facilities as having the best coverage without considering census.

## 7. Finding: unusually low coverage requires investigation

The initial facility ranking (requiring at least 30 observed days) contained near-zero HPRD values, including **WHITE RIVER HEALTHCARE (AR)** and **ST CATHERINE OF SIENA (NJ)** at 0.000. These are **data-quality or reporting review flags**, not evidence of understaffing. Before drawing a conclusion, examine the daily rows, other staff categories, provider identity, reporting completeness, and relevant CMS documentation.

## 8. What each dashboard graph answers

1. **Daily HPRD line:** Does recorded coverage change during the quarter?
2. **RN/LPN/CNA bar chart:** Which nursing role contributes the most reported hours?
3. **State HPRD bar chart:** How does pooled coverage compare geographically?
4. **Weekday/weekend bar chart:** Is there a weekly coverage pattern?
5. **Facility tables:** Which facilities have the highest total hours, and which have unusually low coverage?
6. **Contract share chart:** Where are contracted nursing hours more common relative to total nursing hours?

## 9. Important limitations

- The data cover **April–June 2024**, not current staffing.
- PBJ data are about **nursing homes and skilled nursing facilities**, not general hospitals.
- HPRD is **hours divided by resident-days**, not nurses divided by patients.
- Pooled ratios can conceal differences between individual facilities.
- Facility-level comparisons do not adjust for resident acuity or case mix.
- Near-zero staffing records may reflect missing or unusual reporting.
- No causal relationship between staffing and resident outcomes can be established from this analysis alone.
- The other uploaded CMS files have different scopes and periods and are not included in these results.

## 10. Presentation summary (study script)

> “For my Healthcare Metrics Project, I analyzed CMS daily nursing-home staffing data for April through June 2024. I cleaned the dataset by checking duplicates, dates, census values, and nursing hours. I then created metrics for total nursing hours, hours per resident-day, contract staffing, and facility comparisons. Across the cleaned data, the pooled staffing measure was approximately 3.29 hours per resident-day. I also observed lower pooled coverage on weekends than weekdays and meaningful variation across states. I built a Streamlit dashboard so a user can filter the results by state, facility, and date. My conclusions are descriptive: unusual values require further investigation, and the data alone cannot establish care quality or causation.”

## 11. Next phase

A future version may connect staffing to CMS citations, penalties, ownership, vaccination, and SNF value-based purchasing results using validated provider identifiers and carefully aligned reporting periods. **No such joined findings are claimed here.**

## AI assistance disclosure

AI tools assisted with profiling workflows, code drafting, and writing explanations. Findings and code should be reviewed and independently verified by the project owner before publication or presentation.
