"""Removes zero-count rows from the large MSDS count tables (a missing row means zero)."""
import pandas as pd, os

f_m = 'out/Fact_MSDS_Measures.csv'
df_m = pd.read_csv(f_m, dtype=str, keep_default_na=False)
df_m[df_m['Value'] != '0'].to_csv(f_m, index=False)

f_dq = 'out/Fact_MSDS_DataQuality.csv'
df_dq = pd.read_csv(f_dq, dtype=str, keep_default_na=False)
df_dq[df_dq['Denominator'] != '0'].to_csv(f_dq, index=False)
