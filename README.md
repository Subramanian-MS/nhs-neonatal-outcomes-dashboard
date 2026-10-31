<div align="center">

# 🏥 NHS Neonatal Intensive Care Outcomes & Data Quality Dashboard

**Interactive clinical & data-quality benchmark across 24 NHS Level 3 Neonatal Intensive Care Trusts built from official NHS England Open Data (`2019/20`–`2023/24`)**

[![Live Dashboard](https://img.shields.io/badge/🔗_Live_Dashboard-View_Now-16285a?style=for-the-badge)](https://subramanian-ms.github.io/nhs-neonatal-outcomes-dashboard/)
[![Open Data Source](https://img.shields.io/badge/Data_Source-NHS_England_MSDS_%26_NICU_Open_Data-005eb8?style=for-the-badge)](https://digital.nhs.uk/data-and-information/publications/statistical/nhs-maternity-statistics)
[![Validation Checks](https://img.shields.io/badge/Automated_Reconciliation-22_%2F_22_PASS-2f6b4a?style=for-the-badge)](docs/Validation_Report.md)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

*How do England's 24 Level 3 Neonatal Intensive Care Trusts compare on baby record completeness (`MSD401`), 1-hour skin-to-skin thermal care, early antenatal pathway booking (`≤10 wks`), low 5-minute Apgar (`<7`), first-feed breastmilk nutrition, and feeding documentation?*

</div>

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📊 **Interactive 24-NICU Benchmark Table** | Sort by any clinical or data-quality measure — click column headers to rank trusts |
| 🔍 **NICU & ODN Network Focus** | Click any unit (e.g. *Leeds Children's Hospital*, *Evelina London*, *Sheffield Jessop Wing*) or filter by **NHS Operational Delivery Network (ODN)** |
| ✅ **MSDS Baby Record Data Quality (`MSD401`)** | Compares core baby demographic & birth record completeness (excluding unmapped optional `M401090`/`M401180` fields) against raw `MSD401` table validity rates |
| 📈 **Five-Year Clinical Trends (`2019/20`–`2023/24`)** | Multi-year trajectories across 5 official NHS England annual releases for 1-hour skin-to-skin care, early pathway booking (`≤10 wks`), and low 5-minute Apgar (`<7`) |
| 📋 **16 MSDS Data Item Breakdown** | Diverging gap chart across 16 baby & neonatal data items (`M401050`..`M405909`) from `msds_dq_2023_24.csv` with NHS statistical disclosure controls (`<8` suppressed, `<25` flagged `*`) |
| 👶 **Gestational Age Acuity Profile** | 11 official NHS England `GestationLengthBirth` bands (`<28 wks` to `43+ wks`) comparing preterm (`<37 wks`) vs term (`37+ wks`) caseloads |
| 🛡️ **Automated 22-Check Reconciliation** | Independent validation script (`validate.py`) reconciling every dashboard figure against raw NHS England source tables (`docs/Validation_Report.md`) |
| 🌙 **Dark Mode & Print Ready** | Instant light/dark theme toggle and A4 landscape print stylesheet |
| ⚡ **Zero External Dependencies** | Pure HTML/CSS/JS with responsive inline SVG charts — runs offline and loads instantaneously |

## 📥 Official NHS England Open Data Files (`work/real_nhs/`)

All figures in this repository are extracted and reconciled directly from official **NHS England Maternity Services Data Set (MSDS) & Neonatal Critical Care Open Data** files downloaded from `https://files.digital.nhs.uk/`:

| File in `work/real_nhs/` | Official NHS England Download Link | Contents |
|---|---|---|
| `msds_2023_24.csv` | [`hosp-epis-stat-mat-msdscsv-2023-24.csv`](https://files.digital.nhs.uk/3C/203C97/hosp-epis-stat-mat-msdscsv-2023-24.csv) | 2023/24 Provider-level baby & birth measures (`TotalBabies`, `SkinToSkinContact1HourTerm`, `ApgarScore5TermGroup7`, `BabyFirstFeedBreastMilkStatus`, `GestationLengthBirth`, `GestAgeFormalAntenatalBookingGroup`) |
| `msds_2022_23.csv` | [`hosp-epis-stat-mat-msdscsv-2022-23.csv`](https://files.digital.nhs.uk/ED/921DCF/hosp-epis-stat-mat-msdscsv-2022-23.csv) | 2022/23 Provider-level baby & birth measures |
| `msds_2021_22.csv` | [`hosp-epis-stat-mat-msdscsv-2021-22.csv`](https://files.digital.nhs.uk/47/30A6F6/hosp-epis-stat-mat-msdscsv-2021-22.csv) | 2021/22 Provider-level baby & birth measures |
| `msds_2020_21.csv` | [`hosp-epis-stat-mat-msdscsv-2020-21.csv`](https://files.digital.nhs.uk/F8/155767/hosp-epis-stat-mat-msdscsv-2020-21.csv) | 2020/21 Provider-level baby & birth measures |
| `msds_2019_20.csv` | [`hosp-epis-stat-mat-msdscsv-2019-20.csv`](https://files.digital.nhs.uk/AF/A659BF/hosp-epis-stat-mat-msdscsv-2019-20.csv) | 2019/20 Provider-level baby & birth measures |
| `msds_dq_2023_24.csv` | [`hosp-epis-stat-mat-msdsdq-2023-24.csv`](https://files.digital.nhs.uk/52/CE28B8/hosp-epis-stat-mat-msdsdq-2023-24.csv) | 2023/24 Provider-level Data Quality (`MSD401 Baby's Demographics and Birth Details`, `MSD402 Neonatal Admission`, `MSD405 Care Activity (Baby)`) |
| `msds_dq_2022_23.csv` | [`hosp-epis-stat-mat-msdsdq-2022-23.csv`](https://files.digital.nhs.uk/A4/8A22B0/hosp-epis-stat-mat-msdsdq-2022-23.csv) | 2022/23 Provider-level Data Quality |
| `msds_dq_2021_22.csv` | [`hosp-epis-stat-mat-msdsdq-2021-22.csv`](https://files.digital.nhs.uk/6D/2EB2F9/hosp-epis-stat-mat-msdsdq-2021-22.csv) | 2021/22 Provider-level Data Quality |
| `msds_dq_2020_21.csv` | [`hosp-epis-stat-mat-msdsdq-2020-21.csv`](https://files.digital.nhs.uk/EA/3E18AE/hosp-epis-stat-mat-msdsdq-2020-21.csv) | 2020/21 Provider-level Data Quality |
| `msds_dq_2019_20.csv` | [`hosp-epis-stat-mat-msdsdq-2019-20.csv`](https://files.digital.nhs.uk/71/9C0EAE/hosp-epis-stat-mat-msdsdq-2019-20.csv) | 2019/20 Provider-level Data Quality |
| `msds_bf_2023_24.csv` | [`hosp-epis-stat-mat-bf-msdscsv-2023-24.csv`](https://files.digital.nhs.uk/91/D6B35B/hosp-epis-stat-mat-bf-msdscsv-2023-24.csv) | 2023/24 Provider-level breastfeeding & infant feeding |
| `pla_2023_24.xlsx` | [`hosp-epis-stat-mat-pla-2023-24.xlsx`](https://files.digital.nhs.uk/3F/228AD4/hosp-epis-stat-mat-pla-2023-24.xlsx) | 2023/24 Provider Level Analysis (`Table A` & `Table B` Gestational Age Bands) |
| `nccanlys_2022_23.xlsx` | [`hosp-epis-stat-mat-nccanlys-2022-23.xlsx`](https://files.digital.nhs.uk/5B/3DEB28/hosp-epis-stat-mat-nccanlys-2022-23.xlsx) | Neonatal Critical Care Minimum Data Set (`NCCMDS`) & `MSDS` Data Quality Review |

## 🏥 Dashboard Overview

The dashboard benchmarks **24 NHS Level 3 Neonatal Intensive Care Trusts** across England (`149,105` total babies, `130,410` validated core `MSD401` records in `2023/24`), including all four **Yorkshire & Humber ODN Level 3 units** (*Leeds Children's Hospital (`RR8`)*, *Sheffield Jessop Wing (`RHQ`)*, *Bradford Royal Infirmary (`RAE`)*, and *Hull Royal Infirmary (`RWA`)*):

- **Headline metrics (`2023/24`)**:
  - **Validated baby records (`k`) & Core record completeness (`%`)**: Share of baby records valid across core `MSD401 Baby's Demographics and Birth Details` items (excluding unmapped optional `M401090`/`M401180` fields) — led nationally by **Leeds Children's Hospital (`RR8`) at `97.4%` (`8,220` of `8,440` babies)** vs **`87.5%`** across all 24 Level 3 trusts
  - **1-hour skin-to-skin thermal care (`%`)**: Term babies receiving skin-to-skin contact within 1 hour of birth (`SkinToSkinContact1HourTerm`, `76.8%` pooled; `99,455 / 129,565`)
  - **Early pathway booking `≤10 wks` (`%`)**: Mothers booked within 10 completed weeks / 0–70 days (`GestAgeFormalAntenatalBookingGroup`, `57.8%` pooled; **`70.4%` at Leeds (`RR8`), ranked 4th of 24**)
  - **Low 5-minute Apgar `<7` (`%`)**: Term babies born with a 5-minute Apgar score of `0 to 6` requiring clinical stabilisation (`ApgarScore5TermGroup7`, *lower is better*; `1.4%` pooled; **`1.0%` at Leeds (`RR8`), ranked 6th of 24**)
  - **Breastmilk first feed (`%`)**: Babies receiving maternal or donor breastmilk for their first feed (`BabyFirstFeedBreastMilkStatus`, `76.4%` pooled; **`75.6%` at Leeds (`RR8`), highest in Yorkshire & Humber ODN**)
  - **Feeding status recorded (`%`)**: Completeness of first-feed breastmilk indication code (`UID M401210` in `MSD401`, `87.2%` pooled; **`91.0%` at Leeds (`RR8`)**)
- **Colour coding**: 🟩 Green = better than National NICU benchmark · 🟧 Orange = behind benchmark · ⬜ White = within `±0.5 pt`

## 🔧 Reproducible Data Quality & Build Pipeline

```
Official NHS England CSVs (work/real_nhs/msds_*.csv & msds_dq_*.csv)
  │
  ├─► generate_source_data.py → Filter 5 years of NHS England CSVs to 24 NICU Trusts → work/flt/msds-*.csv & msds-dq-*.csv
  ├─► clean.py                → Harmonise 2019/20–2023/24 schemas, compute Wilson 95% CIs → work/out/Fact_*.csv
  ├─► dims.py                 → Build native NHS lookup tables (Dim_Unit, Dim_Year, Dim_ClinicalIndicator, Dim_MSDSDataItem, Dim_GestationBand)
  ├─► dropzeros.py            → Strip zero-denominator rows from large fact tables
  ├─► dash.py / ext.py        → Extract Power BI slices (Dash_*.csv) & 5-year unit trajectories
  ├─► extend.py               → Compute 16 MSDS item completeness rates, 11 gestation bands & raw MSD401 table rates
  ├─► validate.py             → Run 22 independent reconciliation & disclosure checks → docs/Validation_Report.md
  └─► build_html.py           → Compile template + JSON → NHS_Neonatal_Dashboard.html & index.html
```

## 📖 Documentation

| Document | Contents |
|----------|----------|
| [Calculation Rules](docs/Calculation_Rules.md) | Official NHS England download links, numerators, denominators, schema harmonisation, and NHS small-number suppression (`<8` / `<25`) |
| [Validation Report](docs/Validation_Report.md) | 22 automated checks reconciling dashboard figures against raw NHS England extract tables (`22/22 PASS`) |
| [Accessibility Check](docs/Accessibility_Check.md) | WCAG AA contrast ratios and non-colour visual encoding (`▲`/`▼`) |
| [Browser Test Notes](docs/Browser_Test_Notes.md) | Responsive desktop/mobile and dark-mode verification |
| [Data Attribution](docs/Data_Attribution.md) | Open Government Licence v3.0 governance, statistical disclosure control, and attribution |

## 📝 License

This project is licensed under the [MIT License](LICENSE). Source data is published by NHS England under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

---

<div align="center">

**Built by [Subramanian Mathur Seetharaman](https://github.com/Subramanian-MS)**

</div>
