# Data attribution, governance and licence

The dashboard is built directly from official **NHS England Maternity Services Data Set (MSDS) & Neonatal Critical Care Open Data** releases (`2019/20` to `2023/24`), published by NHS England (`https://digital.nhs.uk/data-and-information/publications/statistical/nhs-maternity-statistics`) and licensed under the **Open Government Licence v3.0 (OGL v3.0)**.

## Official Downloaded Datasets (`work/real_nhs/`)
1. **MSDS Provider-Level Measures CSVs (`2019/20` to `2023/24`)**:
   - `https://files.digital.nhs.uk/3C/203C97/hosp-epis-stat-mat-msdscsv-2023-24.csv`
   - `https://files.digital.nhs.uk/ED/921DCF/hosp-epis-stat-mat-msdscsv-2022-23.csv`
   - `https://files.digital.nhs.uk/47/30A6F6/hosp-epis-stat-mat-msdscsv-2021-22.csv`
   - `https://files.digital.nhs.uk/F8/155767/hosp-epis-stat-mat-msdscsv-2020-21.csv`
   - `https://files.digital.nhs.uk/AF/A659BF/hosp-epis-stat-mat-msdscsv-2019-20.csv`
2. **MSDS Provider-Level Data Quality CSVs (`2019/20` to `2023/24`)**:
   - `https://files.digital.nhs.uk/52/CE28B8/hosp-epis-stat-mat-msdsdq-2023-24.csv`
   - `https://files.digital.nhs.uk/A4/8A22B0/hosp-epis-stat-mat-msdsdq-2022-23.csv`
   - `https://files.digital.nhs.uk/6D/2EB2F9/hosp-epis-stat-mat-msdsdq-2021-22.csv`
   - `https://files.digital.nhs.uk/EA/3E18AE/hosp-epis-stat-mat-msdsdq-2020-21.csv`
   - `https://files.digital.nhs.uk/71/9C0EAE/hosp-epis-stat-mat-msdsdq-2019-20.csv`
3. **Supplementary Provider Level Analysis & Neonatal Critical Care Data Quality Review**:
   - `https://files.digital.nhs.uk/91/D6B35B/hosp-epis-stat-mat-bf-msdscsv-2023-24.csv`
   - `https://files.digital.nhs.uk/3F/228AD4/hosp-epis-stat-mat-pla-2023-24.xlsx`
   - `https://files.digital.nhs.uk/5B/3DEB28/hosp-epis-stat-mat-nccanlys-2022-23.xlsx`

## Statistical disclosure control & patient confidentiality
In compliance with NHS England sub-national small-number suppression and data governance rules:
1. All counts are aggregated at NHS Trust level and rounded to the nearest 5. No patient-identifiable data (PID) or NHS numbers are stored in the repository.
2. Cells with fewer than 8 records (`1–7` records, or rounded count `5`) are suppressed in accordance with NHS England statistical disclosure control, and cells with 8 to 24 records (`<25`) are flagged `*` for wide 95% confidence intervals.
3. This project is an independent analytical and data-quality engineering portfolio piece; it is not endorsed by NHS England or participating NHS Trusts.

Suggested attribution wording (used in the dashboard footer):
> Source: Official NHS England Maternity Services Data Set (MSDS) & Neonatal Critical Care Open Data (digital.nhs.uk/nhs-maternity-statistics; files.digital.nhs.uk), 2019/20 to 2023/24 annual releases, licensed under Open Government Licence v3.0. Filtered, validated and recalculated by Subramanian Mathur Seetharaman; independent portfolio analysis not endorsed by NHS England or participating NHS Trusts.
