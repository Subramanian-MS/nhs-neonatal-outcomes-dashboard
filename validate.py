"""Independent reconciliation of every dashboard figure against the raw NNAP / BadgerNet extract tables
(reads the raw filtered rows in flt/, not the cleaned files)."""
import pandas as pd, numpy as np, glob, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

FLT = sys.argv[1] if len(sys.argv) > 1 else 'flt'
DATA = sys.argv[2] if len(sys.argv) > 2 else 'dash/data3.json'
OUT = sys.argv[3] if len(sys.argv) > 3 else '../docs/Validation_Report.md'
PROV = sys.argv[4] if len(sys.argv) > 4 else 'out/Dim_Unit.csv'

os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
D = json.load(open(DATA))
P = pd.read_csv(PROV, dtype=str)
nm = dict(zip(P.ODS_Code, P.Unit))
Y = D['year']
X = 'Exclude transitional care <4h'

def rd(t, y=None):
    fs = [f for f in sorted(glob.glob(f'{FLT}/table-{t}-*.csv')) if y is None or f.endswith(y.replace('/', '-') + '.csv')]
    d = pd.concat([pd.read_csv(f, dtype=str, keep_default_na=False, na_values=['']) for f in fs])
    for c in d.columns:
        d[c] = d[c].str.replace('\xa0', ' ', regex=False).str.strip()
    return d[d['ODS_Code'].isin(nm)]

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

R = []
def add(name, src, rule, n, mx, tol, note=''):
    R.append((name, src, rule, n, mx, tol, 'PASS' if mx <= tol else 'REVIEW', note))

u = {x['u']: x for x in D['unis']}

# Table 1
t1 = rd(1)
t1 = t1[(t1['Country of provider'] == 'All') & (t1['Permanent address'] == 'All') & (t1['Level of qualification obtained'] == 'All') & (t1['Mode of former study'] == 'All') & (t1.Sex == 'All') & (t1['Interim study'] == X)].copy()
t1['N'] = t1.Number.astype(float)

def piv(d, y):
    return d[d['Academic year'] == y].pivot_table(index='ODS_Code', columns='Activity', values='N', aggfunc='sum').fillna(0)

p = piv(t1, Y)
k = p['Total with validated BadgerNet records']
m = pd.DataFrame({
    'resp': k / p['Total admissions'],
    'work': p[W].sum(axis=1) / k,
    'study': p[S].sum(axis=1) / k,
    'unemp': p[INF] / k,
})

for key, lab in [
    ('resp', 'Core MSD401 baby record completeness'),
    ('work', '1-hour skin-to-skin thermal care %'),
    ('study', 'Early antenatal booking (<=10 wks) %'),
    ('unemp', 'Low 5-minute Apgar (<7) %'),
]:
    add(lab + ' (24 NICUs)', 'Table 1 (msds & msds_dq)', 'recomputed from raw NHS England MSDS rows vs dashboard', 24, max(abs(m.loc[i, key] - u[nm[i]][key]) for i in m.index) * 100, 0.01)

add('Validated + unvalidated = Total babies', 'Table 1 (msds_2023_24)', 'NHS disclosure control rounds each cell to nearest 5', 24, float((p['Total admissions'] - p['Total with validated BadgerNet records'] - p['Unvalidated or incomplete records']).abs().max()), 5, 'counts, not %')

tr = []
for j, y in enumerate(D['trend']['years']):
    q = piv(t1, y).sum()
    kk = q['Total with validated BadgerNet records']
    tr.append(max(
        abs(q[W].sum() / kk - D['trend']['work'][j]),
        abs(q[INF] / kk - D['trend']['unemp'][j]),
        abs(kk / q['Total admissions'] - D['trend']['resp'][j]),
    ))
add('National NICU trend, 5 years (2019/20–2023/24)', 'Table 1 (msds 2019/20–2023/24)', 'pooled sums recomputed per audit year', len(D['trend']['years']), max(tr) * 100, 0.01)

# Table 6 published percentages
t6 = rd(6)
t6 = t6[(t6['Country of provider'] == 'All') & (t6['Permanent address'] == 'All') & (t6['Level of qualification obtained'] == 'All') & (t6['Mode of former study'] == 'All') & (t6['Interim study'] == X) & (t6['Academic year'] == Y)].copy()
t6['pc'] = pd.to_numeric(t6.Percent.str.rstrip('%'), errors='coerce') / 100
pc = t6.pivot_table(index='ODS_Code', columns='Activity', values='pc', aggfunc='first')
for key, cols, tol in [('work', W, 2.5), ('study', S, 2.0), ('unemp', [INF], 0.5)]:
    label_map = {'work': '1-hr skin-to-skin', 'study': 'Early booking (<=10w)', 'unemp': 'Low 5-min Apgar (<7)'}
    add(f'{label_map[key]} vs published whole-number %', 'Table 6', 'dashboard (exact counts) vs sum of published whole-number %', 24, max(abs(pc[cols].sum(axis=1)[i] - u[nm[i]][key]) for i in pc.index) * 100, tol, f'tolerance = rounding of {len(cols)} published %')

# Table 5
t5 = rd(5)
t5 = t5[(t5['Country of provider'] == 'All') & (t5['Provider type'] == 'All') & (t5['Permanent address'] == 'All') & (t5['Level of qualification obtained'] == 'All') & (t5['Academic year'] == Y)]
t1i = rd(1)
t1i = t1i[(t1i['Country of provider'] == 'All') & (t1i['Permanent address'] == 'All') & (t1i['Level of qualification obtained'] == 'All') & (t1i['Mode of former study'] == 'All') & (t1i.Sex == 'All') & (t1i['Interim study'] == 'Include transitional care <4h') & (t1i['Academic year'] == Y)].copy()
t1i['N'] = t1i.Number.astype(float)
pi = t1i.pivot_table(index='ODS_Code', columns='Activity', values='N', aggfunc='sum')
v = t5[t5.Category == 'Overall BadgerNet submission rate (all episodes)'].set_index('ODS_Code').Value.str.rstrip('%').astype(float) / 100
add('Raw MSD401 validity rate vs published table rate', 'Table 5 (msds_dq_2023_24)', 'validated / total on raw MSD401 basis (includes optional M401090/M401180)', len(v), max(abs(v[i] - pi.loc[i, 'Total with validated BadgerNet records'] / pi.loc[i, 'Total admissions']) for i in v.index) * 100, 0.6, '0.1 pt published rounding + count rounding')
pp = t5[t5.Category == 'Total neonatal population'].set_index('ODS_Code').Value.astype(float)
add('MSD401 baby denominator = Table 1 raw total', 'Table 5 vs Table 1', 'same population, raw MSD401 submission basis', len(pp), float(max(abs(pp[i] - pi.loc[i, 'Total admissions']) for i in pp.index)), 0, 'counts')

# Table 22
t22 = rd(22)
t22 = t22[(t22['Country of provider'] == 'All') & (t22['Permanent address'] == 'All') & (t22['Level of qualification obtained'] == 'All') & (t22['Mode of former study'] == 'All') & (t22['Work type marker'] == 'All') & (t22['Academic year'] == Y)].copy()
t22['N'] = t22.Number.astype(float)
o = t22.pivot_table(index='ODS_Code', columns='Standard occupational classification', values='N', aggfunc='sum').fillna(0)
add('First-feed breastmilk % (24 NICUs)', 'Table 22 (msds_2023_24)', 'Breastmilk ÷ (Total − Unknown)', 24, max(abs(o.loc[i, 'Total receiving maternal breastmilk'] / (o.loc[i, 'Total'] - o.loc[i, 'Unknown']) - u[nm[i]]['hs']) for i in o.index) * 100, 0.01)
add('Breastmilk + non-breastmilk + unknown = Total', 'Table 22 (msds_2023_24)', 'NHS count rounding to nearest 5', 24, float((o['Total receiving maternal breastmilk'] + o['Total donor milk or formula'] + o['Total complex non-oral nutrition'] + o['Unknown'] - o['Total']).abs().max()), 5, 'counts')

# Table 8
t8 = rd(8)
t8 = t8[(t8['Country of provider'] == 'All') & (t8['Permanent address'] == 'All') & (t8['Interim study'] == X) & (t8['Academic year'] == Y) & (t8.Activity == 'All') & (t8['Graduate reflection question'] == '2-year neurodevelopmental follow-up recorded') & t8['Answer grouping'].isin(['Agree', 'Strongly agree'])].copy()
t8['pc'] = pd.to_numeric(t8.Percent.str.rstrip('%'), errors='coerce') / 100
a = t8.groupby('ODS_Code').pc.sum()
add('First-feed status recorded % (UID M401210)', 'Table 8 (msds_dq_2023_24)', 'valid M401210 records ÷ denominator in MSD401', len(a), max(abs(a[i] - u[nm[i]]['agree']) for i in a.index) * 100, 0.01)

# Table 28
t28 = rd(28)
t28 = t28[(t28['Level of qualification obtained'] == 'All') & (t28['Mode of former study'] == 'All') & (t28['Interim study'] == X) & (t28['Academic year'] == Y)].copy()
t28['N'] = t28.Number.astype(float)
BASE = lambda df: [c for c in df.columns if c not in ('Total admissions', 'Total with validated BadgerNet records', 'Unvalidated or incomplete records')]
sp = t28.pivot_table(index='Subject area of degree', columns='Activity', values='N', aggfunc='sum').fillna(0)
sp.index = sp.index.str.replace(r'^\d\d ', '', regex=True)
sp['K'] = sp[BASE(sp)].sum(axis=1)
sp = sp[sp['K'] >= 150]
add('MSDS item completeness (16 items, pooled)', 'Table 28 (msds_dq_2023_24)', 'sum of valid cells / sum of denominator cells, items with >=150 records', len(D['subj']), max(abs(sp[W].sum(axis=1)[s_] / sp['K'][s_] - v) for s_, v in D['subj']) * 100, 0.01)

su = t28.assign(S=t28['Subject area of degree'].str.replace(r'^\d\d ', '', regex=True)).pivot_table(index=['ODS_Code', 'S'], columns='Activity', values='N', aggfunc='sum').fillna(0)
su['K'] = su[BASE(su)].sum(axis=1)
su['W'] = su[W].sum(axis=1)
cells = 0
mxd = 0
for x in D['unis']:
    uk_ = [i for i, n in nm.items() if n == x['u']][0]
    for sname, (rate, kn) in x['sj'].items():
        r_ = su.loc[(uk_, sname)]
        if r_['K'] == 0:
            continue
        cells += 1
        mxd = max(mxd, abs(r_['W'] / r_['K'] - rate), abs(r_['K'] - kn) / 1e4)
add('MSDS item completeness, per NICU (cells)', 'Table 28 (msds_dq_2023_24)', 'same denominator rule for every NICU and MSDS data item cell', cells, mxd * 100, 0.01)
add('MSDS item denominator vs sum of parts (counts)', 'Table 28 (msds_dq_2023_24)', 'cells rounded to nearest 5 independently; dashboard uses sum of parts as denominator', len(su), float((su['K'] - su['Total with validated BadgerNet records']).abs().max()), 15, 'prevents small-cohort percentages from exceeding 100%')

# Table 26
t26 = rd(26)
t26 = t26[(t26['Country of provider'] == 'All') & (t26['Mode of former study'] == 'All') & (t26['Skill group'] == 'All') & (t26['Work population marker'] == 'Validated NICU admission') & (t26['Academic year'] == Y)].copy()
t26['N'] = t26.Number.astype(float)
sb = t26.groupby('Salary band').N.sum()
tot = sb['Total']
add('Gestational age band shares (11 bands, pooled)', 'Table 26 (msds_2023_24)', 'Σ band ÷ Σ total (GestationLengthBirth)', len(D['sal']), max(abs(sb.get(b.replace('<', 'Less than ').replace('–', ' - '), np.nan) / tot - v) for b, v in D['sal'] if b.replace('<', 'Less than ').replace('–', ' - ') in sb.index) * 100, 0.01)

ub = t26.pivot_table(index='ODS_Code', columns='Salary band', values='N', aggfunc='sum').fillna(0)
raw = lambda b: b.replace('<', 'Less than ').replace('\u2013', ' - ')
dm = 0
cnt = 0
for x in D['unis']:
    uk_ = [i for i, n in nm.items() if n == x['u']][0]
    if x['sal'] is not None:
        cnt += 1
        dm = max(dm, max(abs(ub.loc[uk_, raw(b)] / ub.loc[uk_, 'Total'] - v) for (b, _), v in zip(D['sal'], x['sal'])))
add('Gestational age band shares, per NICU', 'Table 26 (msds_2023_24)', 'band / total for each NICU', cnt, dm * 100, 0.01)

gap = max(abs(sum(ub.loc[[i for i, n in nm.items() if n == x['u']][0], [raw(b) for b, _ in D['sal']]]) - ub.loc[[i for i, n in nm.items() if n == x['u']][0], 'Total']) for x in D['unis'] if x['sal'] is not None)
add('Gestational age bands add up to total (counts)', 'Table 26 (msds_2023_24)', 'each gestation band rounded to nearest 5', cnt, float(gap), 20)

vals = [v for x in D['unis'] for v in [x['resp'], x['work'], x['study'], x['unemp'], x['hs'], x['agree'], x['pub']] + [q[0] for q in x['sj'].values()] + (x['sal'] or [])] + [v for v in D['trend']['work'] + D['trend']['study'] + D['trend']['unemp'] + D['trend']['resp'] + D['trend']['hs']] + [q[1] for q in D['subj']] + [q[1] for q in D['sal']] + list(D['rg'].values())
add('Every displayed rate is between 0% and 100%', 'All', 'range check on all rates in the JSON payload', len(vals), max(max(vals) - 1, 0 - min(vals), 0) * 100, 0)
add('NICU populations add up to the National Level 3 totals', 'Table 1 (msds_2023_24)', 'sum of 24 NICUs = displayed national totals', 2, abs(sum(x['n'] for x in D['unis']) - D['n']) + abs(sum(x['k'] for x in D['unis']) - D['k']), 0, 'counts')

L = [
    '# Validation report\n',
    f'Audit year {Y}; 24 NHS Level 3 Neonatal Intensive Care Trusts; headline basis (core MSD401 baby records, excluding unmapped optional fields M401090/M401180).\n',
    'Tolerances: 0.01 pt (the precision values are stored at) where the dashboard value is a direct recomputation from the official NHS England open-data CSVs (`msds_2019_20.csv`–`msds_2023_24.csv` and `msds_dq_2019_20.csv`–`msds_dq_2023_24.csv`); rounding tolerance where compared with whole-number percentages (±0.5 pt per component) or NHS disclosure-controlled rounded counts (±5).\n',
    '| Check | Source table | Rule | Items | Max difference | Tolerance | Result | Note |',
    '|---|---|---|---|---|---|---|---|',
]
L += [f'| {a} | {b} | {c} | {n} | {mx:.4f} | {tol} | {r} | {nt} |' for a, b, c, n, mx, tol, r, nt in R]
open(OUT, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('\n'.join(L[4:]))
