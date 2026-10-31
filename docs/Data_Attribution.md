# Data attribution, governance and licence

The dashboard is structured around the clinical audit indicators and data-quality standards of the **Royal College of Paediatrics and Child Health (RCPCH) National Neonatal Audit Programme (NNAP)** and **NHS England BadgerNet** neonatal operational data extracts (tables 1, 5, 6, 8, 22, 26 and 28), under the **Open Government Licence v3.0 (OGL v3.0)** and **Creative Commons Attribution 4.0 International (CC BY 4.0)**.

## Statistical disclosure control & patient confidentiality
In compliance with NHS England / RCPCH small-number suppression and data governance rules:
1. All episode counts are aggregated at NHS Trust / Level 3 NICU level and rounded to the nearest 5. No patient-identifiable data (PID) or NHS numbers are stored in the repository.
2. Unit-cohort cells with fewer than 8 validated episodes (`1–7` episodes, or rounded count `5`) are suppressed in accordance with NHS England sub-national statistical disclosure control, and cells with 8 to 24 episodes (`<25`) are flagged `*` for wide 95% confidence intervals per RCPCH NNAP small-denominator reporting rules.
3. This project is an independent analytical and data-quality engineering portfolio piece; it is not an official NHS England, RCPCH or NHS Trust publication.

Suggested attribution wording (used in the dashboard footer):
> Source: Modelled on RCPCH National Neonatal Audit Programme (NNAP) and NHS England BadgerNet open data standards (rcpch.ac.uk/nnap; digital.nhs.uk), 2023/24 audit period, licensed under OGL v3.0 / CC BY 4.0. Filtered, validated and recalculated by Subramanian Mathur Seetharaman; independent portfolio analysis not endorsed by NHS England, RCPCH or participating NHS Trusts.
