# Validation report

Audit year 2023/24; 24 NHS Level 3 Neonatal Intensive Care Trusts; headline basis (core MSD401 baby records, excluding unmapped optional fields M401090/M401180).

Tolerances: 0.01 pt (the precision values are stored at) where the dashboard value is a direct recomputation from the official NHS England open-data CSVs (`msds_2019_20.csv`–`msds_2023_24.csv` and `msds_dq_2019_20.csv`–`msds_dq_2023_24.csv`); rounding tolerance where compared with whole-number percentages (±0.5 pt per component) or NHS disclosure-controlled rounded counts (±5).

| Check | Source table | Rule | Items | Max difference | Tolerance | Result | Note |
|---|---|---|---|---|---|---|---|
| Core MSD401 baby record completeness (24 NICUs) | Table 1 (msds & msds_dq) | recomputed from raw NHS England MSDS rows vs dashboard | 24 | 0.0046 | 0.01 | PASS |  |
| 1-hour skin-to-skin thermal care % (24 NICUs) | Table 1 (msds & msds_dq) | recomputed from raw NHS England MSDS rows vs dashboard | 24 | 0.0044 | 0.01 | PASS |  |
| Early antenatal booking (<=10 wks) % (24 NICUs) | Table 1 (msds & msds_dq) | recomputed from raw NHS England MSDS rows vs dashboard | 24 | 0.0049 | 0.01 | PASS |  |
| Low 5-minute Apgar (<7) % (24 NICUs) | Table 1 (msds & msds_dq) | recomputed from raw NHS England MSDS rows vs dashboard | 24 | 0.0049 | 0.01 | PASS |  |
| Validated + unvalidated = Total babies | Table 1 (msds_2023_24) | NHS disclosure control rounds each cell to nearest 5 | 24 | 0.0000 | 5 | PASS | counts, not % |
| National NICU trend, 5 years (2019/20–2023/24) | Table 1 (msds 2019/20–2023/24) | pooled sums recomputed per audit year | 5 | 0.0049 | 0.01 | PASS |  |
| 1-hr skin-to-skin vs published whole-number % | Table 6 | dashboard (exact counts) vs sum of published whole-number % | 24 | 1.1600 | 2.5 | PASS | tolerance = rounding of 5 published % |
| Early booking (<=10w) vs published whole-number % | Table 6 | dashboard (exact counts) vs sum of published whole-number % | 24 | 1.1500 | 2.0 | PASS | tolerance = rounding of 4 published % |
| Low 5-min Apgar (<7) vs published whole-number % | Table 6 | dashboard (exact counts) vs sum of published whole-number % | 24 | 0.4900 | 0.5 | PASS | tolerance = rounding of 1 published % |
| Raw MSD401 validity rate vs published table rate | Table 5 (msds_dq_2023_24) | validated / total on raw MSD401 basis (includes optional M401090/M401180) | 24 | 0.0487 | 0.6 | PASS | 0.1 pt published rounding + count rounding |
| MSD401 baby denominator = Table 1 raw total | Table 5 vs Table 1 | same population, raw MSD401 submission basis | 24 | 0.0000 | 0 | PASS | counts |
| First-feed breastmilk % (24 NICUs) | Table 22 (msds_2023_24) | Breastmilk ÷ (Total − Unknown) | 24 | 0.0047 | 0.01 | PASS |  |
| Breastmilk + non-breastmilk + unknown = Total | Table 22 (msds_2023_24) | NHS count rounding to nearest 5 | 24 | 0.0000 | 5 | PASS | counts |
| First-feed status recorded % (UID M401210) | Table 8 (msds_dq_2023_24) | valid M401210 records ÷ denominator in MSD401 | 24 | 0.0000 | 0.01 | PASS |  |
| MSDS item completeness (16 items, pooled) | Table 28 (msds_dq_2023_24) | sum of valid cells / sum of denominator cells, items with >=150 records | 16 | 0.0047 | 0.01 | PASS |  |
| MSDS item completeness, per NICU (cells) | Table 28 (msds_dq_2023_24) | same denominator rule for every NICU and MSDS data item cell | 374 | 0.0050 | 0.01 | PASS |  |
| MSDS item denominator vs sum of parts (counts) | Table 28 (msds_dq_2023_24) | cells rounded to nearest 5 independently; dashboard uses sum of parts as denominator | 384 | 0.0000 | 15 | PASS | prevents small-cohort percentages from exceeding 100% |
| Gestational age band shares (11 bands, pooled) | Table 26 (msds_2023_24) | Σ band ÷ Σ total (GestationLengthBirth) | 11 | 0.0037 | 0.01 | PASS |  |
| Gestational age band shares, per NICU | Table 26 (msds_2023_24) | band / total for each NICU | 24 | 0.0050 | 0.01 | PASS |  |
| Gestational age bands add up to total (counts) | Table 26 (msds_2023_24) | each gestation band rounded to nearest 5 | 24 | 0.0000 | 20 | PASS |  |
| Every displayed rate is between 0% and 100% | All | range check on all rates in the JSON payload | 865 | 0.0000 | 0 | PASS |  |
| NICU populations add up to the National Level 3 totals | Table 1 (msds_2023_24) | sum of 24 NICUs = displayed national totals | 2 | 0.0000 | 0 | PASS | counts |
