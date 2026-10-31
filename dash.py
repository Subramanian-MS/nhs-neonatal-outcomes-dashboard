"""Extracts headline-slice CSV tables for Power BI (Dash_*.csv) and computes the initial pooled and per-unit summary JSON (dash/data.json)."""
import pandas as pd, json, shutil, os, re

O = 'out/'
D = 'dash/'
os.makedirs(D, exist_ok=True)

P = pd.read_csv(O + 'Dim_Unit.csv', dtype=str)
nm = dict(zip(P.ODS_Code, P.Unit))
odn_map = dict(zip(P.ODS_Code, P.ODN_Region))
rd = lambda f: pd.read_csv(O + f, dtype={'ODS_Code': str})
X = 'Exclude transitional care <4h'

a = rd('Fact_Episodes_Sex.csv')
a = a[(a.Care_Setting == 'All') & (a.Gestation_Filter == 'All') & (a.Admission_Source == 'All') & (a.Sex == 'All') & (a.Basis == X)][['ODS_Code', 'Year', 'Episode_Category', 'Number']]

o = rd('Fact_DischargeNutrition.csv')
o = o[(o.Care_Setting == 'All') & (o.Gestation_Filter == 'All') & (o.Admission_Source == 'All') & (o.Care_Type == 'All')][['ODS_Code', 'Year', 'Nutrition_Group', 'Number']]

s = rd('Fact_ClinicalCohort.csv')
s = s[(s.Gestation_Filter == 'All') & (s.Admission_Source == 'All') & (s.Basis == X)][['ODS_Code', 'Year', 'Clinical_Cohort', 'Episode_Category', 'Number']]

sl = rd('Fact_GestationBand.csv')
sl = sl[(sl.Admission_Source == 'All') & (sl.Acuity_Group == 'All') & (sl.Population_Marker == 'Validated NICU admission')][['ODS_Code', 'Year', 'Gestation_Band', 'Number']]

r = rd('Fact_FollowUp.csv')
r = r[(r.Episode_Category == 'All') & (r.Care_Setting == 'All') & (r.Basis == X)][['ODS_Code', 'Year', 'Audit_Question', 'Response_Group', 'Percent']]

for n, d in [('Dash_Episodes', a), ('Dash_Nutrition', o), ('Dash_ClinicalCohort', s), ('Dash_GestationBand', sl), ('Dash_FollowUp', r)]:
    d.to_csv(D + n + '.csv', index=False)

for f in ['Dim_Unit', 'Dim_Year', 'Dim_EpisodeCategory', 'Dim_Nutrition', 'Dim_ClinicalCohort', 'Dim_GestationBand', 'Dim_AuditQuestion', 'Dim_ResponseGroup']:
    shutil.copy(O + f + '.csv', D + f + '.csv')

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

def kp(df, by):
    p = df.pivot_table(index=by, columns='Episode_Category', values='Number', aggfunc='sum').fillna(0)
    k = p['Total with validated BadgerNet records']
    return pd.DataFrame({
        'n': p['Total admissions'],
        'k': k,
        'resp': k / p['Total admissions'],
        'work': p[W].sum(axis=1) / k,
        'study': p[S].sum(axis=1) / k,
        'unemp': p[INF] / k,
    })

Y = os.environ.get('LATEST_YEAR', '2023/24')
tr = kp(a, 'Year')
ho = o.pivot_table(index=['ODS_Code', 'Year'], columns='Nutrition_Group', values='Number', aggfunc='sum').fillna(0)
hsY = ho.groupby('Year').sum()
hsY = hsY['Total receiving maternal breastmilk'] / (hsY['Total'] - hsY['Unknown'])

u = kp(a[a.Year == Y], 'ODS_Code')
hu = ho.xs(Y, level='Year')
u['hs'] = hu['Total receiving maternal breastmilk'] / (hu['Total'] - hu['Unknown'])

rf = r[(r.Year == Y) & (r.Audit_Question == '2-year neurodevelopmental follow-up recorded') & r.Response_Group.isin(['Agree', 'Strongly agree'])].groupby('ODS_Code').Percent.sum()
u['agree'] = rf

am = a[(a.Year == Y)].groupby('Episode_Category').Number.sum()
mix = {k: int(am[k]) for k in am.index if k not in ('Total admissions', 'Total with validated BadgerNet records', 'Unvalidated or incomplete records')}

sj = s[s.Year == Y]
sp = sj.pivot_table(index='Clinical_Cohort', columns='Episode_Category', values='Number', aggfunc='sum').fillna(0)
sp = sp[sp.index.str.match(r'^\d\d ')]
sp['K'] = sp[[c for c in sp.columns if c not in ('Total admissions', 'Total with validated BadgerNet records', 'Unvalidated or incomplete records')]].sum(axis=1)
sp = sp[sp['K'] >= 150]
sw = (sp[W].sum(axis=1) / sp['K']).sort_values(ascending=False)

sal = sl[(sl.Year == Y)].groupby('Gestation_Band').Number.sum()
tot = sal.pop('Total')
bands = pd.read_csv(O + 'Dim_GestationBand.csv')
order = [b for b in bands.Gestation_Band if b != 'Total']

R = lambda x, d=4: round(float(x), d)
data = {
    'year': Y,
    'n': int(tr.loc[Y, 'n']),
    'k': int(tr.loc[Y, 'k']),
    'trend': {
        'years': list(tr.index),
        'work': [R(x) for x in tr.work],
        'study': [R(x) for x in tr.study],
        'unemp': [R(x) for x in tr.unemp],
        'resp': [R(x) for x in tr.resp],
        'hs': [R(x) for x in hsY],
    },
    'rg': {
        'resp': R(tr.loc[Y, 'resp']),
        'work': R(tr.loc[Y, 'work']),
        'study': R(tr.loc[Y, 'study']),
        'unemp': R(tr.loc[Y, 'unemp']),
        'hs': R(hsY[Y]),
        'agree': R((u.agree * u.k).sum() / u.k[u.agree.notna()].sum()),
    },
    'unis': [
        {
            'u': nm[i],
            'ods': i,
            'odn': odn_map[i],
            'resp': R(r_.resp),
            'work': R(r_.work),
            'study': R(r_.study),
            'unemp': R(r_.unemp),
            'hs': R(r_.hs),
            'agree': R(r_.agree),
            'k': int(r_.k),
        }
        for i, r_ in u.iterrows()
    ],
    'mix': mix,
    'subj': [[re.sub(r'^\d\d ', '', k), R(v)] for k, v in sw.items()],
    'sal': [[b.replace('Less than ', '<').replace(' - ', '–'), R(sal[b] / tot)] for b in order],
    'subjk': {re.sub(r'^\d\d ', '', k): int(v) for k, v in sp['K'].items()},
}

json.dump(data, open('dash/data.json', 'w'), separators=(',', ':'))
print(os.path.getsize('dash/data.json'), len(data['subj']), data['rg'], data['sal'][:3])
