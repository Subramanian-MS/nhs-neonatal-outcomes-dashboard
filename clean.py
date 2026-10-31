"""Standardises headers, converts percentage strings to decimals, extracts 95% confidence intervals,
and removes duplicate regional total rows from the filtered NNAP / BadgerNet extract tables."""
import pandas as pd, numpy as np, glob, sys, os, re

OUT = 'out'
os.makedirs(OUT, exist_ok=True)

def rd(t):
    for f in sorted(glob.glob(f'flt/table-{t}-*.csv')):
        d = pd.read_csv(f, dtype=str, keep_default_na=False, na_values=[''])
        for c in d.columns:
            d[c] = d[c].str.replace('\xa0', ' ', regex=False).str.strip()
        yield d

def pct(s):
    return pd.to_numeric(s.str.rstrip('%'), errors='coerce') / 100

def write(df, name, first):
    df.to_csv(f'{OUT}/{name}.csv', mode='w' if first else 'a', header=first, index=False, encoding='utf-8')

REN = {
    'Academic year': 'Year',
    'Permanent address': 'Care_Setting',
    'Level of qualification obtained': 'Gestation_Filter',
    'Mode of former study': 'Admission_Source',
    'Interim study': 'Basis',
    'Activity': 'Episode_Category',
}

def base(d):
    if 'Country of provider' in d.columns:
        d = d[d['Country of provider'] == 'All'].drop(columns=['Country of provider'])
    d = d.drop(columns=['Provider name'])
    return d.rename(columns=REN)

t = sys.argv[1]
spec = {
    '1': ('Fact_Episodes_Sex', ['ODS_Code', 'Year', 'Care_Setting', 'Gestation_Filter', 'Admission_Source', 'Basis', 'Sex', 'Episode_Category']),
    '22': ('Fact_DischargeNutrition', ['ODS_Code', 'Year', 'Care_Setting', 'Care_Type', 'Gestation_Filter', 'Admission_Source', 'Nutrition_Group']),
    '28': ('Fact_ClinicalCohort', ['ODS_Code', 'Year', 'Gestation_Filter', 'Admission_Source', 'Basis', 'Clinical_Cohort', 'Episode_Category']),
}

first = True
if t in spec:
    name, cols = spec[t]
    for d in rd(t):
        d = base(d)
        d['Number'] = pd.to_numeric(d['Number']).astype('int32')
        d = d.rename(columns={
            'Work type marker': 'Care_Type',
            'Standard occupational classification': 'Nutrition_Group',
            'Subject area of degree': 'Clinical_Cohort',
        })
        write(d, name, first)
        first = False
elif t == '6':
    for d in rd('6'):
        d = base(d)
        d['Number'] = pd.to_numeric(d['Number']).astype('int32')
        d['Percent'] = pct(d['Percent'])
        ci = d['95% confidence interval'].str.extract(r'\((\d+)%-(\d+)%\)').astype(float) / 100
        d['CI_Low'] = ci[0]
        d['CI_High'] = ci[1]
        d = d.drop(columns=['95% confidence interval'])
        write(d, 'Fact_Episodes_CI', first)
        first = False
elif t == '5':
    for d in rd('5'):
        d = d[(d['Country of provider'] == 'All') & (d['Provider type'] == 'All')].drop(columns=['Country of provider', 'Provider name', 'Provider type'])
        d = d.rename(columns={
            'Academic year': 'Year',
            'Permanent address': 'Setting_Detail',
            'Level of qualification obtained': 'Cohort_Detail',
        })
        d['Value'] = np.where(d.Category == 'Total neonatal population', pd.to_numeric(d.Value, errors='coerce'), pct(d.Value))
        w = d.pivot_table(index=['ODS_Code', 'Year', 'Setting_Detail', 'Cohort_Detail'], columns='Category', values='Value', aggfunc='first').reset_index()
        w = w.rename(columns={
            'Complete first-pass BadgerNet submission rate': 'FirstPass_Rate',
            'Post-audit query resolved rate': 'QueryResolved_Rate',
            'Overall BadgerNet submission rate (all episodes)': 'Submission_Rate',
            'Total neonatal population': 'Neonatal_Population',
        })
        w.columns.name = None
        write(w, 'Fact_SubmissionRate', first)
        first = False
elif t == '8':
    for d in rd('8'):
        d = base(d)
        d['Percent'] = pct(d['Percent'])
        d = d.rename(columns={
            'Graduate reflection question': 'Audit_Question',
            'Answer grouping': 'Response_Group',
        })
        write(d, 'Fact_FollowUp', first)
        first = False
elif t == '26':
    for d in rd('26'):
        d = d[d['Country of provider'] == 'All'].drop(columns=['Country of provider', 'Provider name'])
        d = d.rename(columns={
            'Academic year': 'Year',
            'Mode of former study': 'Admission_Source',
            'Skill group': 'Acuity_Group',
            'Work population marker': 'Population_Marker',
            'Salary band': 'Gestation_Band',
        })
        d['Number'] = pd.to_numeric(d['Number']).astype('int32')
        d['Percent'] = pct(d['Percent'])
        write(d, 'Fact_GestationBand', first)
        first = False

print('done', t)
