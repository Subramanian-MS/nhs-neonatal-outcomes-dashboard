# Calculation rules and clinical data definitions

Basis for every figure: Official **NHS England Maternity Services Data Set (MSDS) & Neonatal Critical Care Open Data** releases (`2019/20` to `2023/24` annual cohorts, downloaded directly from `https://files.digital.nhs.uk/` and stored in `work/real_nhs/`), headline basis (validated core `MSD401 Baby's Demographics and Birth Details` records, excluding unmapped optional fields `M401090 Local Fetal Identifier` and `M401180 Maternity Care Setting`), across all **24 English Level 3 Neonatal Intensive Care Unit (NICU) Trusts**. Counts are rounded to the nearest 5 in accordance with NHS England statistical disclosure control.

## Official NHS England Source Files (`work/real_nhs/`)
- **Provider-Level Measures (`msds_2019_20.csv` to `msds_2023_24.csv`)**:
  - `2023/24`: `https://files.digital.nhs.uk/3C/203C97/hosp-epis-stat-mat-msdscsv-2023-24.csv`
  - `2022/23`: `https://files.digital.nhs.uk/ED/921DCF/hosp-epis-stat-mat-msdscsv-2022-23.csv`
  - `2021/22`: `https://files.digital.nhs.uk/47/30A6F6/hosp-epis-stat-mat-msdscsv-2021-22.csv`
  - `2020/21`: `https://files.digital.nhs.uk/F8/155767/hosp-epis-stat-mat-msdscsv-2020-21.csv`
  - `2019/20`: `https://files.digital.nhs.uk/AF/A659BF/hosp-epis-stat-mat-msdscsv-2019-20.csv`
- **Provider-Level Data Quality & Completeness (`msds_dq_2019_20.csv` to `msds_dq_2023_24.csv`)**:
  - `2023/24`: `https://files.digital.nhs.uk/52/CE28B8/hosp-epis-stat-mat-msdsdq-2023-24.csv`
  - `2022/23`: `https://files.digital.nhs.uk/A4/8A22B0/hosp-epis-stat-mat-msdsdq-2022-23.csv`
  - `2021/22`: `https://files.digital.nhs.uk/6D/2EB2F9/hosp-epis-stat-mat-msdsdq-2021-22.csv`
  - `2020/21`: `https://files.digital.nhs.uk/EA/3E18AE/hosp-epis-stat-mat-msdsdq-2020-21.csv`
  - `2019/20`: `https://files.digital.nhs.uk/71/9C0EAE/hosp-epis-stat-mat-msdsdq-2019-20.csv`
- **Supplementary Provider & Neonatal Critical Care Releases**:
  - `msds_bf_2023_24.csv`: `https://files.digital.nhs.uk/91/D6B35B/hosp-epis-stat-mat-bf-msdscsv-2023-24.csv`
  - `pla_2023_24.xlsx`: `https://files.digital.nhs.uk/3F/228AD4/hosp-epis-stat-mat-pla-2023-24.xlsx`
  - `nccanlys_2022_23.xlsx`: `https://files.digital.nhs.uk/5B/3DEB28/hosp-epis-stat-mat-nccanlys-2022-23.xlsx`

## Metric Definitions

| Figure | Numerator | Denominator | NHS England Source |
|---|---|---|---|
| Total babies (`n`) | `TotalBabies` (`TOTAL BABIES` in 2019/20) | n/a | `msds_*.csv` (Table 1) |
| Validated baby records (`k`) | `TotalBabies × Core MSD401 Completeness` (rounded to nearest 5) | n/a | `msds_*.csv` & `msds_dq_*.csv` (Table 1) |
| Core record completeness (`resp`) | Sum of `Valid` records across core `MSD401` baby fields (excluding optional `M401090` & `M401180`) | Sum of `Denominator` records across core `MSD401` baby fields | `msds_dq_*.csv` (Table 1); raw `MSD401` table rate (Table 5) is shown separately on the KPI card |
| 1-hr skin-to-skin (`work`) | `SkinToSkinContact1HourTerm` where `Measure = 'Yes'` | Known `SkinToSkinContact1HourTerm` (`Yes + No`, excluding `Missing value`) | `msds_*.csv` (Table 1) |
| Early booking ≤10w (`study`) | `GestAgeFormalAntenatalBookingGroup` where `Measure = '0 to 70 days'` (`00-04` to `10 weeks` in 2019/20) | Known booking gestation (`0 to 70`, `71 to 90`, `91 to 140`, `141+ days`) | `msds_*.csv` (Table 1) |
| Low 5-min Apgar <7 (`unemp`) | `ApgarScore5TermGroup7` where `Measure = '0 to 6'` | Known 5-minute Apgar score (`0 to 6` + `7 to 10`) | `msds_*.csv` (Table 1) |
| Breastmilk first feed (`hs`) | `BabyFirstFeedBreastMilkStatus` where `Measure = 'Maternal or Donor Breast Milk'` | Known first-feed status (`Maternal or Donor Breast Milk` + `Not Breast Milk`) | `msds_*.csv` (Table 22) |
| Feed status recorded (`agree`) | `Valid` records for `UID = M401210` (`BABY FIRST FEED BREAST MILK INDICATION CODE`) | `Denominator` records for `UID = M401210` in `MSD401` | `msds_dq_*.csv` (Table 8) |
| MSDS item completeness (16 items) | `Valid` records for each `UID` (`M401050`..`M405909`) | `Denominator` records for that `UID` | `msds_dq_2023_24.csv` (Table 28) |
| Gestational age band share (11 bands) | Babies in `GestationLengthBirth` band (`27 weeks and under` to `43 weeks and over`) | All babies with known `GestationLengthBirth` | `msds_2023_24.csv` & `pla_2023_24.xlsx` Table B (Table 26) |

## Data Engineering & Reconciliation Rules
1. **National Level 3 NICU benchmark figures pool counts first** (sum of numerators ÷ sum of denominators across all 24 Trusts).
2. **Schema harmonisation across 2019/20–2023/24:** In `2019/20`, NHS England published lowercase column headers (`period, dimension, org_level, org_code, org_name, measure1, count_of, value`) and uppercase dimension names (`TOTAL BABIES`, `APGARSCORE5TERMGROUP7`, `SKINTOSKINCONTACT1HOURTERM`), then switched to Title Case headers (`Period, Dimension, Org_Level, Org_Code, Org_Name, Measure, Count_Of, Value`) and CamelCase dimensions in `2020/21`–`2023/24`. The ingestion script normalises headers, dimension names, and missing-value strings across all 5 annual releases.
3. **Core `MSD401` completeness vs raw `MSD401` table rate:** In `msds_dq_2023_24.csv`, `MSD401 Baby's Demographics and Birth Details` includes two optional fields (`M401090 LOCAL FETAL IDENTIFIER` and `M401180 MATERNITY CARE SETTING (ACTUAL PLACE OF BIRTH)`) that many Trusts do not populate (`Valid = 0` or `<2%` at Leeds `RR8`, despite `100%` completeness on NHS Number, Birth Date/Time, Sex, Ethnicity, Birth Order, Delivery Method, and Skin-to-Skin Indicator). Excluding those two optional fields gives the headline **Core record completeness** (`97.4%` at Leeds `RR8`, ranked 1st of 24), while the raw `MSD401` table rate across all 27 fields (`89.6%` at Leeds `RR8`) is displayed on the key-figure card and reconciled against Table 5.
4. **NHS small-number suppression (`<8` records) and low-denominator flag (`<25` records):** In accordance with NHS England sub-national statistical disclosure control rules, any Trust-item cell with fewer than 8 records in the denominator is suppressed (`grey`) in the MSDS item completeness chart, and cells with 8 to 24 records (`<25`) are marked `*` (wide 95% confidence interval, indicative only).
5. **Tolerance band and polarity:** Table cells within 0.5 percentage points of the National NICU average are left uncoloured. For **Low 5-min Apgar (`<7`)**, lower is better.
