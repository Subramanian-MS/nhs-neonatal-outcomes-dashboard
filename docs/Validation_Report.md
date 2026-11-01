# Validation report

Audit year 2023/24; 24 NHS Level 3 Neonatal Intensive Care Trusts; headline basis (core MSD401 baby records, excluding unmapped optional fields M401090/M401180).

Tolerances: 0.01 pt (the precision values are stored at) where the dashboard value is a direct recomputation from the official NHS England open-data CSVs (`msds_2019_20.csv`–`msds_2023_24.csv` and `msds_dq_2019_20.csv`–`msds_dq_2023_24.csv`); rounding tolerance where compared with whole-number percentages (±0.5 pt) or NHS disclosure-controlled rounded counts (±5).

| Check | Source table | Rule | Items | Max difference | Tolerance | Result | Note |
|---|---|---|---|---|---|---|---|
| MSD401 baby record completeness (24 NICUs) | msds-dq-2023-24.csv (MSD401) | sum(Valid) / sum(Denominator) across all 27 MSD401 fields vs dashboard | 24 | 0.0050 | 0.01 | PASS |  |
| 1-hour skin-to-skin thermal care % (24 NICUs) | msds-2023-24.csv (SkinToSkinContact1HourTerm) | Yes / (Yes + No) recomputed from raw NHS MSDS rows vs dashboard | 24 | 0.0043 | 0.01 | PASS |  |
| Early antenatal booking (<=10 wks) % (24 NICUs) | msds-2023-24.csv (GestAgeFormalAntenatalBookingGroup) | (0 to 70 days) / known bookings recomputed from raw NHS MSDS rows vs dashboard | 24 | 0.0050 | 0.01 | PASS |  |
| Low 5-minute Apgar (<7) % (24 NICUs) | msds-2023-24.csv (ApgarScore5TermGroup7) | (0 to 6) / (0 to 6 + 7 to 10) recomputed from raw NHS MSDS rows vs dashboard | 24 | 0.0042 | 0.01 | PASS |  |
| Validated + unvalidated = Total babies | msds-2023-24.csv & msds-dq-2023-24.csv | NHS disclosure control rounds validated baby count to nearest 5 | 24 | 0.0000 | 5 | PASS | counts, not % |
| National NICU trend, 5 years (2019/20–2023/24) | msds-2019-20..2023-24.csv & msds-dq | pooled sums recomputed per audit year from raw NHS files | 5 | 0.0049 | 0.01 | PASS |  |
| 1-hr skin-to-skin vs published whole-number % | msds-2023-24.csv | dashboard (exact counts) vs whole-number rounded % | 24 | 0.4800 | 0.5 | PASS | tolerance = ±0.5 pt whole-number rounding |
| Early booking (<=10w) vs published whole-number % | msds-2023-24.csv | dashboard (exact counts) vs whole-number rounded % | 24 | 0.5000 | 0.5 | PASS | tolerance = ±0.5 pt whole-number rounding |
| Low 5-min Apgar (<7) vs published whole-number % | msds-2023-24.csv | dashboard (exact counts) vs whole-number rounded % | 24 | 0.5000 | 0.5 | PASS | tolerance = ±0.5 pt whole-number rounding |
| Raw MSD401 validity rate vs published table rate | msds-dq-2023-24.csv (MSD401 all 27 items) | sum(Valid) / sum(Denominator) across all 27 MSD401 items (including M401090/M401180) | 24 | 0.0050 | 0.01 | PASS |  |
| TotalBabies in MSDS = dashboard unit cohort (n) | msds-2023-24.csv (TotalBabies) | TotalBabies count per Trust in raw NHS MSDS file vs dashboard | 24 | 0.0000 | 0 | PASS | counts |
| First-feed breastmilk % (24 NICUs) | msds-2023-24.csv (BabyFirstFeedBreastMilkStatus) | Breastmilk ÷ (Breastmilk + Not Breast Milk) | 24 | 0.0047 | 0.01 | PASS |  |
| Breastmilk + non-breastmilk + unknown = Total | msds-2023-24.csv (BabyFirstFeedBreastMilkStatus) | sum of feeding outcomes equals total baby feeding records per Trust | 24 | 0.0000 | 5 | PASS | counts |
| First-feed status recorded % (UID M401210) | msds-dq-2023-24.csv (UID M401210) | Valid M401210 records ÷ Denominator in MSD401 | 24 | 0.0050 | 0.01 | PASS |  |
| MSDS item completeness (16 items, pooled) | msds-dq-2023-24.csv (MSD401/402/405) | sum(Valid) / sum(Denominator) across 24 NICUs, items with >=150 records | 16 | 0.0047 | 0.01 | PASS |  |
| MSDS item completeness, per NICU (cells) | msds-dq-2023-24.csv (MSD401/402/405) | Valid / Denominator for every NICU and MSDS data item cell | 374 | 0.0050 | 0.01 | PASS |  |
| MSDS item denominator vs sum of parts (counts) | msds-dq-2023-24.csv (MSD401/402/405) | Valid + Default + Invalid + Missing vs Denominator (cells rounded to nearest 5) | 384 | 5.0000 | 15 | PASS | NHS disclosure control rounds each DQ status column to nearest 5 |
| Gestational age band shares (11 bands, pooled) | msds-2023-24.csv (GestationLengthBirth) | Σ band ÷ Σ total known gestation at birth | 11 | 0.0037 | 0.01 | PASS |  |
| Gestational age band shares, per NICU | msds-2023-24.csv (GestationLengthBirth) | band / total known gestation for each NICU | 24 | 0.0050 | 0.01 | PASS |  |
| Gestational age bands add up to total (counts) | msds-2023-24.csv (GestationLengthBirth) | sum of 11 gestation bands equals unit gestation denominator (sn) | 24 | 0.0000 | 20 | PASS |  |
| Every displayed rate is between 0% and 100% | All | range check on all rates in the JSON payload | 875 | 0.0000 | 0 | PASS |  |
| NICU populations add up to the National Level 3 totals | msds-2023-24.csv (TotalBabies) | sum of 24 NICUs = displayed national totals | 2 | 0.0000 | 0 | PASS | counts |
