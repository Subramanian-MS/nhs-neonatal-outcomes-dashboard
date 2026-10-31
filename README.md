<div align="center">

# 🏥 NHS Neonatal Intensive Care Outcomes & Data Quality Dashboard

**Interactive clinical audit & BadgerNet data-quality benchmark across 24 NHS Level 3 Neonatal Intensive Care Units (NICUs)**

[![Live Dashboard](https://img.shields.io/badge/🔗_Live_Dashboard-View_Now-16285a?style=for-the-badge)](https://subramanian-ms.github.io/nhs-neonatal-outcomes-dashboard/)
[![Audit Framework](https://img.shields.io/badge/Audit_Framework-RCPCH_NNAP_%26_BadgerNet-0072ce?style=for-the-badge)](https://www.rcpch.ac.uk/work-we-do/quality-improvement-patient-safety/national-neonatal-audit-programme)
[![Validation Checks](https://img.shields.io/badge/Automated_Reconciliation-22_%2F_22_PASS-2f6b4a?style=for-the-badge)](docs/Validation_Report.md)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

*How do England's 24 Level 3 Neonatal Intensive Care Units compare on BadgerNet episode completeness, admission normothermia, deferred cord clamping, late-onset infection, maternal breastmilk at discharge, and 2-year neurodevelopmental follow-up?*

</div>

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📊 **Interactive 24-NICU Benchmark Table** | Sort by any clinical or data-quality measure — click column headers to rank units |
| 🔍 **NICU & ODN Network Focus** | Click any unit (e.g. *Leeds Children's Hospital*, *Evelina London*, *Sheffield Jessop Wing*) or filter by **NHS Operational Delivery Network (ODN)** |
| ✅ **BadgerNet Data Quality Tracking** | Compares headline validated BadgerNet completeness (excluding `<4h` transitional care observations) against raw submission rates |
| 📈 **Seven-Year Clinical Trends** | Multi-year trajectories (`2017/18` → `2023/24`) for on-time normothermia, deferred cord clamping, and late-onset infection |
| 📋 **16 Clinical Cohort Breakdown** | Diverging gap chart across 16 neonatal clinical & diagnostic cohorts with NHS statistical disclosure controls (`<8` suppressed, `<25` flagged `*`) |
| 👶 **Gestational Age Acuity Profile** | 14-band gestational age distribution (`<24 wks` to `40+ wks`) comparing preterm (`<37 wks`) caseloads |
| 🛡️ **Expandable Reconciliation Report** | Built-in methodology panel displaying all 22 automated data-quality checks against raw source tables |
| 🌙 **Dark Mode & Print Ready** | Instant light/dark theme toggle and A4 landscape print stylesheet |
| ⚡ **Zero External Dependencies** | Pure HTML/CSS/JS with responsive inline SVG charts — runs offline and loads instantaneously |

## 🏥 Dashboard Overview

The dashboard benchmarks **24 NHS Level 3 Neonatal Intensive Care Units (NICUs)** across England (including all four Yorkshire & Humber ODN Level 3 units — *Leeds Children's Hospital*, *Sheffield Jessop Wing*, *Bradford Royal Infirmary*, and *Hull Royal Infirmary* — alongside London, North West, Northern, East of England, Thames Valley & Wessex, South West, West Midlands, and East Midlands tertiary centres):

- **Headline metrics**:
  - **Validated episodes (`k`) & BadgerNet completeness (`%`)**: Share of neonatal admissions passing mandatory BadgerNet validation checks prior to audit lock
  - **On-time normothermia (`%`)**: Admission temperature taken within 1 hour of birth inside $36.5^\circ\text{C}\text{–}37.5^\circ\text{C}$
  - **Deferred cord clamping (`%`)**: Umbilical cord clamped at $\ge 1$ minute
  - **Late-onset bloodstream infection (`%`)**: Bloodstream or CSF infection after 72 hours of age (*lower is better*)
  - **Breastmilk at discharge (`%`)**: Infants receiving maternal breastmilk (exclusive, fortified, or mixed) at discharge home
  - **2-year follow-up recorded (`%`)**: Eligible `<30` week preterm infants with a completed 2-year neurodevelopmental follow-up assessment entered in BadgerNet
- **Colour coding**: 🟩 Green = better than National NICU benchmark · 🟧 Orange = behind benchmark · ⬜ White = within `±0.5 pt`

## 🚀 Quick Start

### View the Live Dashboard
Visit the **[live interactive dashboard](https://subramanian-ms.github.io/nhs-neonatal-outcomes-dashboard/)** — no installation required.

### Run Locally
```bash
# Clone the repository
git clone https://github.com/Subramanian-MS/nhs-neonatal-outcomes-dashboard.git
cd nhs-neonatal-outcomes-dashboard

# Open the dashboard in your browser
open index.html          # macOS
start index.html         # Windows
xdg-open index.html      # Linux
```

## 🔧 Reproducible Data Quality & Build Pipeline

The dashboard and Power BI star-schema tables are built from raw NNAP / BadgerNet extract tables via a repeatable Python & shell pipeline:

```
NNAP / BadgerNet Extract (table-1..28)
  │
  ├─► filter_rows.sh     → Filter raw tables to the 24 Level 3 NICUs (by NHS ODS Trust code)
  ├─► clean.py            → Standardise headers, convert % to decimals, parse 95% CIs, deduplicate
  ├─► dims.py             → Build star-schema lookup tables (Dim_Unit, Dim_Year, Dim_ClinicalCohort, ...)
  ├─► dropzeros.py        → Strip zero-count rows from large fact tables
  ├─► dash.py / ext.py    → Extract headline slices (Dash_*.csv) & 7-year unit trajectories
  ├─► extend.py           → Compute 16 clinical cohort rates, gestation profiles & raw submission rates
  ├─► validate.py         → Run 22 independent reconciliation & disclosure checks → Validation_Report.md
  └─► build_html.py       → Compile template + JSON + validation table → NHS_Neonatal_Dashboard.html & index.html
```

### Rebuild from Source
```bash
# Generate raw tables and run the full pipeline
python3 generate_source_data.py
./run_all.sh work/raw/NNAP_Extract.zip
```

### Outputs
| File | Description |
|------|-------------|
| `index.html` / `NHS_Neonatal_Dashboard.html` | Self-contained interactive HTML dashboard |
| `work/dash/*.csv` | Clean star-schema Fact (`Dash_*`) and Dimension (`Dim_*`) CSV tables for Power BI |
| `docs/Validation_Report.md` | 22 automated reconciliation checks comparing dashboard JSON against raw tables |

## 📁 Project Structure

```
nhs-neonatal-outcomes-dashboard/
├── index.html                          # Dashboard (GitHub Pages entry point)
├── NHS_Neonatal_Dashboard.html         # Dashboard (named build output)
├── template/
│   └── dashboard_template.html         # HTML/CSS/SVG template with __DATA__ & __CHECKS__ placeholders
├── docs/
│   ├── Calculation_Rules.md            # Numerators, denominators, disclosure rounding & small-cohort rules
│   ├── Validation_Report.md            # 22 automated reconciliation checks (22/22 PASS)
│   ├── Accessibility_Check.md          # WCAG AA contrast verification & keyboard navigation notes
│   ├── Browser_Test_Notes.md           # Cross-browser & responsive viewport test log
│   └── Data_Attribution.md             # OGL v3.0 / CC BY 4.0 licence & NHS statistical disclosure governance
├── generate_source_data.py             # Generates deterministic multi-year NNAP/BadgerNet extract tables
├── build_html.py                       # Injects JSON payload and validation table into HTML template
├── clean.py                            # Data standardisation and CI parsing
├── dash.py                             # Headline Power BI slice & pooled benchmark extraction
├── dims.py                             # Dimension/lookup table builder (ODS codes, ODN networks, cohorts)
├── dropzeros.py                        # Zero-count row removal
├── ext.py                              # 7-year longitudinal trends & nutrition tier breakdown
├── extend.py                           # Per-NICU clinical cohort & gestational age profile builder
├── filter_rows.sh                      # NHS ODS code row filter
├── run_all.sh                          # Master reproducible build script
├── validate.py                         # Independent 22-check reconciliation engine
├── LICENSE                             # MIT License
└── README.md                           # Project documentation
```

## 📖 Documentation

| Document | Contents |
|----------|----------|
| [Calculation Rules](docs/Calculation_Rules.md) | Clinical numerators, denominators, rounding to nearest 5, and NHS small-number suppression (`<8` / `<25`) |
| [Validation Report](docs/Validation_Report.md) | 22 automated checks reconciling dashboard figures against raw extract tables |
| [Accessibility Check](docs/Accessibility_Check.md) | WCAG AA contrast ratios and non-colour visual encoding (`▲`/`▼`) |
| [Browser Test Notes](docs/Browser_Test_Notes.md) | Responsive desktop/mobile and dark-mode verification |
| [Data Attribution](docs/Data_Attribution.md) | Open data governance, statistical disclosure control, and attribution |

## 📜 Data Governance & Attribution

> **Source:** Modelled on RCPCH National Neonatal Audit Programme (NNAP) and NHS England BadgerNet open data standards ([rcpch.ac.uk/nnap](https://www.rcpch.ac.uk/work-we-do/quality-improvement-patient-safety/national-neonatal-audit-programme); [digital.nhs.uk](https://digital.nhs.uk/)), 2023/24 audit period, licensed under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/) / [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
>
> All counts are aggregated at unit level and rounded to the nearest 5 for statistical disclosure control; no patient-identifiable data is used. Filtered, validated and recalculated by the author; **independent portfolio project not endorsed by NHS England, RCPCH or participating NHS Trusts**.

## 📝 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

**Built by [Subramanian Mathur Seetharaman](https://github.com/Subramanian-MS)**

</div>
