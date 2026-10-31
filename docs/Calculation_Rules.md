# Calculation rules and clinical data definitions

Basis for every figure: NNAP / BadgerNet neonatal intensive care extract tables (2023/24 audit period, with trends from 2017/18), headline basis (validated BadgerNet episodes, excluding short `<4h` transitional care observations), 24 NHS Level 3 Neonatal Intensive Care Units (NICUs). Counts are rounded to the nearest 5 in accordance with NHS statistical disclosure control.

| Figure | Numerator | Denominator | Source table |
|---|---|---|---|
| Admissions recorded | "Total admissions" | n/a | 1 |
| Validated episodes | "Total with validated BadgerNet records" | n/a | 1 |
| BadgerNet completeness rate (headline basis) | Validated episodes | Admissions recorded | 1; raw submission rate (table 5, including `<4h` transitional care) is shown separately |
| On-time normothermia (`36.5°C–37.5°C`) | Normothermia + deferred cord clamping + immediate clamping + cord unrecorded + postnatal transfer `<24h` + surgical/cardiac co-care | Validated episodes | 1 |
| Deferred cord clamping (`>=1 min`) | Normothermia + deferred cord clamping + hypothermia/hyperthermia/stabilisation with deferred cord clamping | Validated episodes | 1 |
| Late-onset bloodstream infection (`>72h`) | "Late-onset bloodstream infection (>72h)" | Validated episodes | 1 |
| Breastmilk at discharge | Maternal breastmilk groups ("Total receiving maternal breastmilk": exclusive, fortified, or mixed) | "Total" minus "Unknown" feeding status at discharge | 22 |
| 2-year follow-up recorded | Published % with completed clinic assessment (Bayley-III / PARCA-R) + validated parent/health-visitor questionnaire | Eligible `<30` week cohort | 8 |
| Normothermia by clinical cohort | On-time normothermia (as above) within the clinical cohort | Sum of all recorded episode pathway cells within the cohort (not the independently rounded "validated records" total) | 28 |
| Gestational age band share | Validated admissions in the gestational age band | All validated NICU admissions in the gestation table (`<24 wks` to `40+ wks`) | 26 |

## Rules
1. **National Level 3 NICU benchmark figures pool counts first** (sum of numerators ÷ sum of denominators across all 24 NICUs). The exception is "2-year follow-up recorded", which is a published percentage in Table 8, so units are weighted by their validated episode count.
2. **"On-time normothermia" and "Deferred cord clamping" overlap** (babies achieving both admission normothermia and deferred cord clamping count in both), so the two percentages do not sum to 100%.
3. **NHS small-number suppression (`<8` episodes):** In accordance with NHS England sub-national statistical disclosure control rules, a unit-cohort result based on fewer than 8 validated episodes (`1–7` episodes, or rounded count `5`) is suppressed in the clinical cohort chart.
4. **Tolerance band and polarity:** Table cells within 0.5 percentage points of the National NICU average are left uncoloured. For late-onset bloodstream infection (`>72h`), lower is better.
5. **Headline BadgerNet completeness vs raw submission rate:** The dashboard's headline BadgerNet completeness rate is calculated on the validated audit basis (excluding short `<4h` transitional care observations and unverified episodes). The raw submission rate (Table 5) includes transitional care observations; both appear on the key-figure card. Recomputing the raw submission rate on its own basis agrees with the published Table 5 figure within 0.6 percentage points.
6. **Sum-of-parts denominator rule:** Because NHS statistical disclosure control rounds every cell to the nearest 5 independently, a published cohort total can differ slightly from the sum of its pathway parts. Clinical cohort normothermia shares therefore use the sum of the recorded pathway cells as the denominator so that small-cohort percentages can never exceed 100%.
7. **Low-denominator statistical reliability flag (`<25` episodes):** Unit-cohort results based on 8 to 24 validated episodes are marked `*` (wide 95% confidence interval, indicative only) in accordance with RCPCH NNAP small-denominator reporting guidance.
