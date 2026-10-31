# Validation report

Audit year 2023/24; 24 NHS Level 3 Neonatal Intensive Care Units (NICUs); headline basis (validated BadgerNet episodes, excluding transitional care observations <4h).

Tolerances: 0.01 pt (the precision values are stored at) where the dashboard value is a direct recomputation; rounding tolerance where compared with NNAP published whole-number percentages (±0.5 pt per component) or NHS disclosure-controlled rounded counts (±5).

| Check | Source table | Rule | Items | Max difference | Tolerance | Result | Note |
|---|---|---|---|---|---|---|---|
| BadgerNet completeness rate (24 NICUs) | Table 1 | recomputed from raw BadgerNet rows vs dashboard | 24 | 0.0049 | 0.01 | PASS |  |
| On-time normothermia % (24 NICUs) | Table 1 | recomputed from raw BadgerNet rows vs dashboard | 24 | 0.0050 | 0.01 | PASS |  |
| Deferred cord clamping % (24 NICUs) | Table 1 | recomputed from raw BadgerNet rows vs dashboard | 24 | 0.0049 | 0.01 | PASS |  |
| Late-onset infection % (24 NICUs) | Table 1 | recomputed from raw BadgerNet rows vs dashboard | 24 | 0.0048 | 0.01 | PASS |  |
| Validated + unvalidated = Total admissions | Table 1 | NHS disclosure control rounds each cell to nearest 5 | 24 | 0.0000 | 5 | PASS | counts, not % |
| National NICU trend, 7 years | Table 1 | pooled sums recomputed per audit year | 7 | 0.0050 | 0.01 | PASS |  |
| normothermia vs NNAP published % | Table 6 | dashboard (exact counts) vs sum of published whole-number % | 24 | 1.6500 | 2.5 | PASS | tolerance = rounding of 5 published % |
| cord clamping vs NNAP published % | Table 6 | dashboard (exact counts) vs sum of published whole-number % | 24 | 1.6100 | 2.0 | PASS | tolerance = rounding of 4 published % |
| late infection vs NNAP published % | Table 6 | dashboard (exact counts) vs sum of published whole-number % | 24 | 0.4500 | 0.5 | PASS | tolerance = rounding of 1 published % |
| Submission rate vs NNAP raw published | Table 5 | validated / total on raw submission basis (includes transitional care <4h) | 24 | 0.0492 | 0.6 | PASS | 0.1 pt published rounding + count rounding |
| Neonatal population = Table 1 total | Table 5 vs Table 1 | same population, raw submission basis | 24 | 0.0000 | 0 | PASS | counts |
| Maternal breastmilk at discharge % (24 NICUs) | Table 22 | Maternal breastmilk ÷ (Total − Unknown) | 24 | 0.0050 | 0.01 | PASS |  |
| Breastmilk + donor/formula + complex + unknown = Total | Table 22 | NHS count rounding to nearest 5 | 24 | 0.0000 | 5 | PASS | counts |
| 2-year follow-up recorded % (clinic + questionnaire) | Table 8 | sum of clinic and validated questionnaire follow-up % | 24 | 0.0000 | 0.01 | PASS |  |
| Normothermia by clinical cohort (pooled) | Table 28 | sum of normothermia cells / sum of all recorded episode cells, cohorts with >=150 episodes | 16 | 0.0050 | 0.01 | PASS |  |
| Normothermia by clinical cohort, per NICU (cells) | Table 28 | same denominator rule for every NICU and clinical cohort cell | 384 | 0.0046 | 0.01 | PASS |  |
| Cohort validated episodes vs sum of parts (counts) | Table 28 | cells rounded to nearest 5 independently; dashboard uses sum of parts as denominator | 384 | 0.0000 | 15 | PASS | prevents small-cohort percentages from exceeding 100% |
| Gestational age band shares (pooled) | Table 26 | Σ band ÷ Σ total | 14 | 0.0033 | 0.01 | PASS |  |
| Gestational age band shares, per NICU | Table 26 | band / total for each NICU | 24 | 0.0050 | 0.01 | PASS |  |
| Gestational age bands add up to total (counts) | Table 26 | each gestation band rounded to nearest 5 | 24 | 0.0000 | 20 | PASS |  |
| Every displayed rate is between 0% and 100% | All | range check on all rates in the JSON payload | 960 | 0.0000 | 0 | PASS |  |
| NICU populations add up to the National Level 3 totals | Table 1 | sum of 24 NICUs = displayed national totals | 2 | 0.0000 | 0 | PASS | counts |
