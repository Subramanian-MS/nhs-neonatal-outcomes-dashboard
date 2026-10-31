"""Adds per-unit clinical cohort normothermia rates, gestational age distributions, and raw BadgerNet submission rates (dash/data3.json)."""
import pandas as pd, json, re, sys

DATA = sys.argv[1] if len(sys.argv) > 1 else 'dash/data2.json'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'dash/data3.json'
DASH = sys.argv[3] if len(sys.argv) > 3 else 'dash'
PROV = sys.argv[4] if len(sys.argv) > 4 else 'out/Dim_Unit.csv'

d = json.load(open(DATA))
Y = d['year']
P = pd.read_csv(PROV, dtype=str)
uk = {v: k for k, v in zip(P.ODS_Code, P.Unit)}

W = [
    'Normothermia + deferred cord clamping',
    'Normothermia + immediate clamping (clinical indication)',
    'Normothermia + cord clamping unrecorded',
    'Normothermia + postnatal transfer within 24h',
    'Normothermia + surgical or cardiac co-care',
]

s = pd.read_csv(f'{DASH}/Dash_ClinicalCohort.csv', dtype={'ODS_Code': str})
s = s[s.Year == Y]
s['Clinical_Cohort'] = s.Clinical_Cohort.str.replace(r'^\d\d ', '', regex=True)
sp = s.pivot_table(index=['ODS_Code', 'Clinical_Cohort'], columns='Episode_Category', values='Number', aggfunc='sum').fillna(0)

sl = pd.read_csv(f'{DASH}/Dash_GestationBand.csv', dtype={'ODS_Code': str})
sl = sl[sl.Year == Y]
sb = sl.pivot_table(index='ODS_Code', columns='Gestation_Band', values='Number', aggfunc='sum').fillna(0)
raw = lambda b: b.replace('<', 'Less than ').replace('–', ' - ')

for u in d['unis']:
    k = uk[u['u']]
    u['sj'] = {}
    for name, _ in d['subj']:
        if (k, name) in sp.index:
            r = sp.loc[(k, name)]
            kn = sum(r[c] for c in r.index if c not in ('Total admissions', 'Total with validated BadgerNet records', 'Unvalidated or incomplete records'))
            u['sj'][name] = [round(r[W].sum() / kn, 4) if kn else 0, int(kn)]
    if k in sb.index and sb.loc[k, 'Total'] > 0:
        t = sb.loc[k, 'Total']
        u['sal'] = [round(sb.loc[k, raw(b)] / t, 4) for b, _ in d['sal']]
        u['sn'] = int(t)
    else:
        u['sal'] = None
        u['sn'] = 0

rr = pd.read_csv('out/Fact_SubmissionRate.csv', dtype={'ODS_Code': str})
rr = rr[(rr.Year == Y) & (rr.Setting_Detail == 'All') & (rr.Cohort_Detail == 'All')].set_index('ODS_Code').Submission_Rate

fa = pd.read_csv('out/Fact_Episodes_Sex.csv', dtype={'ODS_Code': str})
fa = fa[(fa.Year == Y) & (fa.Care_Setting == 'All') & (fa.Gestation_Filter == 'All') & (fa.Admission_Source == 'All') & (fa.Sex == 'All') & (fa.Basis == 'Include transitional care <4h')]
pv = fa.pivot_table(index='ODS_Code', columns='Episode_Category', values='Number', aggfunc='sum')

for u in d['unis']:
    u['pub'] = round(float(rr[uk[u['u']]]), 4)
d['rg']['pub'] = round(float(pv['Total with validated BadgerNet records'].sum() / pv['Total admissions'].sum()), 4)

json.dump(d, open(OUT, 'w'), separators=(',', ':'))
print(len(open(OUT).read()), 'bytes;', sum(1 for u in d['unis'] if u['sn'] >= 23), 'units with >=23 gestation-band admissions;', sum(1 for u in d['unis'] for v in u['sj'].values() if v[1] < 23), 'cohort cells under 23')
