"""Adds 7-year per-unit clinical trends, episode pathway breakdowns, and discharge nutrition tiers to dash/data2.json."""
import pandas as pd, json, os

d = json.load(open('dash/data.json'))
P = pd.read_csv('out/Dim_Unit.csv', dtype=str)
nm = dict(zip(P.ODS_Code, P.Unit))
a = pd.read_csv('dash/Dash_Episodes.csv', dtype={'ODS_Code': str})
o = pd.read_csv('dash/Dash_Nutrition.csv', dtype={'ODS_Code': str})

W = [
    'Normothermia + deferred cord clamping',
    'Normothermia + immediate clamping (clinical indication)',
    'Normothermia + cord clamping unrecorded',
    'Normothermia + postnatal transfer within 24h',
    'Normothermia + surgical or cardiac co-care',
]
S = [
    'Normothermia + deferred cord clamping',
    'Admission hypothermia + deferred cord clamping',
    'Admission hyperthermia + deferred cord clamping',
    'Stabilisation pathway + deferred cord clamping',
]
INF = 'Late-onset bloodstream infection (>72h)'

p = a.pivot_table(index=['ODS_Code', 'Year'], columns='Episode_Category', values='Number', aggfunc='sum').fillna(0)
k = p['Total with validated BadgerNet records']
p['work'] = p[W].sum(axis=1) / k
p['study'] = p[S].sum(axis=1) / k
p['unemp'] = p[INF] / k

yrs = d['trend']['years']
Y = d['year']
mixc = W + [c for c in S if c not in W] + ['Out-of-range temperature without late infection', INF]
q = o.pivot_table(index=['ODS_Code', 'Year'], columns='Nutrition_Group', values='Number', aggfunc='sum').fillna(0)

def sk(r):
    t = r['Total'] - r['Unknown']
    return [
        round(r['Total receiving maternal breastmilk'] / t, 4),
        round(r['Total donor milk or formula'] / t, 4),
        round(r['Total complex non-oral nutrition'] / t, 4),
    ]

for u in d['unis']:
    uk = [i for i, n in nm.items() if n == u['u']][0]
    u['n'] = int(p.loc[(uk, Y), 'Total admissions'])
    u['tr'] = [[round(p.loc[(uk, y), m], 4) for y in yrs] for m in ['work', 'study', 'unemp']]
    u['mix'] = [int(p.loc[(uk, Y), c]) for c in mixc]
    u['sk'] = sk(q.loc[(uk, Y)])

tot = q.xs(Y, level='Year').sum()
d['sk'] = sk(tot)
d['mixk'] = mixc
json.dump(d, open('dash/data2.json', 'w'), separators=(',', ':'))

# Cross-check vs published whole-number percentages (Table 6)
c = pd.read_csv('out/Fact_Episodes_CI.csv', dtype={'ODS_Code': str})
c = c[(c.Year == Y) & (c.Care_Setting == 'All') & (c.Gestation_Filter == 'All') & (c.Admission_Source == 'All') & (c.Basis == 'Exclude transitional care <4h')]
pc = c.pivot_table(index='ODS_Code', columns='Episode_Category', values='Percent', aggfunc='first')
pw = pc[W].sum(axis=1)
pu = pc[INF]
mine = p.xs(Y, level='Year')
print('max |norm diff| pp:', round(((mine.work - pw).abs().max()) * 100, 2), ' max |inf diff| pp:', round(((mine.unemp - pu).abs().max()) * 100, 2))
print(os.path.getsize('dash/data2.json'))
