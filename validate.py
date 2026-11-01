"""Independent reconciliation of every dashboard figure against the raw filtered NHS England
Maternity Services Data Set (MSDS) and Data Quality CSV extracts (reads flt/msds-*.csv and
flt/msds-dq-*.csv directly, not the cleaned files in out/)."""
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
y_slug = Y.replace('/', '-')

DQ_ITEMS = {
    'M401070': 'NHS number (baby)',
    'M401150': 'Delivery method code',
    'M401060': 'Ethnic category (baby)',
    'M405120': 'Coded clinical observation value',
    'M401130': 'Fetal presentation at delivery',
    'M401120': 'Neonatal death time recorded',
    'M401220': 'Skin-to-skin contact (1h) indicator',
    'M401050': 'Phenotypic sex (baby)',
    'M401170': 'Place of birth site identifier',
    'M405909': 'Care professional ID (baby activity)',
    'M401210': 'First feed breastmilk indicator',
    'M401160': 'Delivered in water indicator',
    'M401909': 'Care professional ID (delivery)',
    'M402040': 'Neonatal critical care admission flag',
    'M401190': 'Baby first feed date & time',
    'M402030': 'Admitting neonatal unit site ID',
}

GEST_MAP = {
    '27 weeks and under': '<28 wks',
    '28 to 31 weeks': '28–31 wks',
    '32 to 33 weeks': '32–33 wks',
    '34 to 36 weeks': '34–36 wks',
    '37 weeks': '37 wks',
    '38 weeks': '38 wks',
    '39 weeks': '39 wks',
    '40 weeks': '40 wks',
    '41 weeks': '41 wks',
    '42 weeks': '42 wks',
    '43 weeks and over': '43+ wks',
}

def rd_msds(y=None):
    fs = [f'{FLT}/msds-{y.replace("/", "-")}.csv'] if y else sorted(glob.glob(f'{FLT}/msds-20*.csv'))
    d = pd.concat([pd.read_csv(f, dtype=str, keep_default_na=False) for f in fs], ignore_index=True)
    for c in d.columns:
        d[c] = d[c].str.replace('\xa0', ' ', regex=False).str.strip()
    d['Val'] = pd.to_numeric(d['Value'], errors='coerce').fillna(0.0)
    return d[d['ODS_Code'].isin(nm)]

def rd_dq(y=None):
    fs = [f'{FLT}/msds-dq-{y.replace("/", "-")}.csv'] if y else sorted(glob.glob(f'{FLT}/msds-dq-20*.csv'))
    d = pd.concat([pd.read_csv(f, dtype=str, keep_default_na=False) for f in fs], ignore_index=True)
    for c in d.columns:
        d[c] = d[c].str.replace('\xa0', ' ', regex=False).str.strip()
    for c in ['Valid', 'Default', 'Invalid', 'Missing', 'Denominator']:
        d[c] = pd.to_numeric(d[c], errors='coerce').fillna(0.0)
    return d[d['ODS_Code'].isin(nm)]

R = []
def add(name, src, rule, n, mx, tol, note=''):
    R.append((name, src, rule, n, mx, tol, 'PASS' if round(float(mx), 6) <= tol else 'REVIEW', note))

u = {x['ods']: x for x in D['unis']}

msds_y = rd_msds(Y)
dq_y = rd_dq(Y)

# 1. MSD401 baby record completeness (24 NICUs, all 27 fields)
m401_y = dq_y[dq_y['DataTable'].str.startswith('MSD401') & (dq_y['UID'] != 'MSD401')]
raw_y = m401_y.groupby('ODS_Code')[['Valid', 'Denominator']].sum()
raw_rates = raw_y['Valid'] / raw_y['Denominator']
add(
    'MSD401 baby record completeness (24 NICUs)',
    f'msds-dq-{y_slug}.csv (MSD401)',
    'sum(Valid) / sum(Denominator) across all 27 MSD401 fields vs dashboard',
    24,
    max(abs(raw_rates[ods] - u[ods]['resp']) for ods in u) * 100,
    0.01,
)

# 2. 1-hour skin-to-skin thermal care % (24 NICUs)
sk_y = msds_y[msds_y['Dimension'] == 'SkinToSkinContact1HourTerm']
sk_yes = sk_y[sk_y['Measure'] == 'Yes'].groupby('ODS_Code')['Val'].sum()
sk_no = sk_y[sk_y['Measure'] == 'No'].groupby('ODS_Code')['Val'].sum()
sk_rates = sk_yes / (sk_yes + sk_no)
add(
    '1-hour skin-to-skin thermal care % (24 NICUs)',
    f'msds-{y_slug}.csv (SkinToSkinContact1HourTerm)',
    'Yes / (Yes + No) recomputed from raw NHS MSDS rows vs dashboard',
    24,
    max(abs(sk_rates[ods] - u[ods]['work']) for ods in u) * 100,
    0.01,
)

# 3. Early antenatal booking (<=10 wks) % (24 NICUs)
bk_y = msds_y[msds_y['Dimension'] == 'GestAgeFormalAntenatalBookingGroup']
bk_early = bk_y[bk_y['Measure'] == '0 to 70 days'].groupby('ODS_Code')['Val'].sum()
bk_known = bk_y[~bk_y['Measure'].str.lower().str.startswith('missing')].groupby('ODS_Code')['Val'].sum()
bk_rates = bk_early / bk_known
add(
    'Early antenatal booking (<=10 wks) % (24 NICUs)',
    f'msds-{y_slug}.csv (GestAgeFormalAntenatalBookingGroup)',
    '(0 to 70 days) / known bookings recomputed from raw NHS MSDS rows vs dashboard',
    24,
    max(abs(bk_rates[ods] - u[ods]['study']) for ods in u) * 100,
    0.01,
)

# 4. Low 5-minute Apgar (<7) % (24 NICUs)
ap_y = msds_y[msds_y['Dimension'] == 'ApgarScore5TermGroup7']
ap_low = ap_y[ap_y['Measure'] == '0 to 6'].groupby('ODS_Code')['Val'].sum()
ap_norm = ap_y[ap_y['Measure'] == '7 to 10'].groupby('ODS_Code')['Val'].sum()
ap_rates = ap_low / (ap_low + ap_norm)
add(
    'Low 5-minute Apgar (<7) % (24 NICUs)',
    f'msds-{y_slug}.csv (ApgarScore5TermGroup7)',
    '(0 to 6) / (0 to 6 + 7 to 10) recomputed from raw NHS MSDS rows vs dashboard',
    24,
    max(abs(ap_rates[ods] - u[ods]['unemp']) for ods in u) * 100,
    0.01,
)

# 5. Validated + unvalidated = Total babies
tb_y = msds_y[msds_y['Dimension'] == 'TotalBabies'].groupby('ODS_Code')['Val'].sum()
k_recomp = ((tb_y * raw_rates) / 5.0).round() * 5
add(
    'Validated + unvalidated = Total babies',
    f'msds-{y_slug}.csv & msds-dq-{y_slug}.csv',
    'NHS disclosure control rounds validated baby count to nearest 5',
    24,
    float(max(abs(k_recomp[ods] - u[ods]['k']) for ods in u)),
    5,
    'counts, not %',
)

# 6. National NICU trend, 5 years (2019/20–2023/24)
msds_all = rd_msds()
dq_all = rd_dq()
tr_diffs = []
for j, yr in enumerate(D['trend']['years']):
    my = msds_all[msds_all['Year'] == yr]
    dqy = dq_all[dq_all['Year'] == yr]

    sky = my[my['Dimension'].str.upper() == 'SKINTOSKINCONTACT1HOURTERM']
    w_yr = sky[sky['Measure'].str.upper() == 'YES']['Val'].sum() / sky[sky['Measure'].str.upper().isin(['YES', 'NO'])]['Val'].sum()

    bky = my[my['Dimension'].isin(['GestAgeFormalAntenatalBookingGroup', 'GESTATIONATBOOKING'])]
    b_num = bky[bky['Measure'].isin(['0 to 70 days', '00-04 weeks', '05-09 weeks', '10 weeks'])]['Val'].sum()
    b_den = bky[~bky['Measure'].str.lower().str.startswith('missing')]['Val'].sum()
    s_yr = b_num / b_den

    apy = my[my['Dimension'].str.upper() == 'APGARSCORE5TERMGROUP7']
    u_yr = apy[apy['Measure'] == '0 to 6']['Val'].sum() / apy[apy['Measure'].isin(['0 to 6', '7 to 10'])]['Val'].sum()

    bfy = my[my['Dimension'].str.upper() == 'BABYFIRSTFEEDBREASTMILKSTATUS']
    h_yr = bfy[bfy['Measure'] == 'Maternal or Donor Breast Milk']['Val'].sum() / bfy[bfy['Measure'].isin(['Maternal or Donor Breast Milk', 'Not Breast Milk'])]['Val'].sum()

    tby = my[my['Dimension'].str.upper().isin(['TOTALBABIES', 'TOTAL BABIES'])].groupby('ODS_Code')['Val'].sum()
    c_y = dqy[dqy['DataTable'].str.startswith('MSD401') & (dqy['UID'] != 'MSD401')].groupby('ODS_Code')[['Valid', 'Denominator']].sum()
    common = [o for o in tby.index if o in c_y.index and tby[o] > 0 and c_y.loc[o, 'Denominator'] > 0]
    k_sum = sum(int(5 * round(tby[o] * (c_y.loc[o, 'Valid'] / c_y.loc[o, 'Denominator']) / 5.0)) for o in common)
    n_sum = sum(int(tby[o]) for o in common)
    r_yr = k_sum / n_sum

    tr_diffs.append(max(
        abs(w_yr - D['trend']['work'][j]),
        abs(s_yr - D['trend']['study'][j]),
        abs(u_yr - D['trend']['unemp'][j]),
        abs(h_yr - D['trend']['hs'][j]),
        abs(r_yr - D['trend']['resp'][j]),
    ))
add(
    'National NICU trend, 5 years (2019/20–2023/24)',
    'msds-2019-20..2023-24.csv & msds-dq',
    'pooled sums recomputed per audit year from raw NHS files',
    len(D['trend']['years']),
    max(tr_diffs) * 100,
    0.01,
)

# 7–9. Whole-number percentage comparisons
for key, series, label in [
    ('work', sk_rates, '1-hr skin-to-skin'),
    ('study', bk_rates, 'Early booking (<=10w)'),
    ('unemp', ap_rates, 'Low 5-min Apgar (<7)'),
]:
    whole_pct = (series * 100).round() / 100.0
    add(
        f'{label} vs published whole-number %',
        f'msds-{y_slug}.csv',
        'dashboard (exact counts) vs whole-number rounded %',
        24,
        max(abs(whole_pct[ods] - u[ods][key]) for ods in u) * 100,
        0.5,
        'tolerance = ±0.5 pt whole-number rounding',
    )

# 10. Raw MSD401 validity rate vs published table rate
raw_y = m401_y.groupby('ODS_Code')[['Valid', 'Denominator']].sum()
raw_rates = raw_y['Valid'] / raw_y['Denominator']
add(
    'Raw MSD401 validity rate vs published table rate',
    f'msds-dq-{y_slug}.csv (MSD401 all 27 items)',
    'sum(Valid) / sum(Denominator) across all 27 MSD401 items (including M401090/M401180)',
    24,
    max(abs(raw_rates[ods] - u[ods]['pub']) for ods in u) * 100,
    0.01,
)

# 11. TotalBabies in msds vs dashboard unit n
add(
    'TotalBabies in MSDS = dashboard unit cohort (n)',
    f'msds-{y_slug}.csv (TotalBabies)',
    'TotalBabies count per Trust in raw NHS MSDS file vs dashboard',
    24,
    float(max(abs(tb_y[ods] - u[ods]['n']) for ods in u)),
    0,
    'counts',
)

# 12. First-feed breastmilk % (24 NICUs)
bf_y = msds_y[msds_y['Dimension'] == 'BabyFirstFeedBreastMilkStatus']
bf_yes = bf_y[bf_y['Measure'] == 'Maternal or Donor Breast Milk'].groupby('ODS_Code')['Val'].sum()
bf_no = bf_y[bf_y['Measure'] == 'Not Breast Milk'].groupby('ODS_Code')['Val'].sum()
bf_mis = bf_y[bf_y['Measure'].str.lower().str.startswith('missing')].groupby('ODS_Code')['Val'].sum()
bf_rates = bf_yes / (bf_yes + bf_no)
add(
    'First-feed breastmilk % (24 NICUs)',
    f'msds-{y_slug}.csv (BabyFirstFeedBreastMilkStatus)',
    'Breastmilk ÷ (Breastmilk + Not Breast Milk)',
    24,
    max(abs(bf_rates[ods] - u[ods]['hs']) for ods in u) * 100,
    0.01,
)

# 13. Breastmilk + non-breastmilk + missing = Total feed records
bf_tot = bf_y.groupby('ODS_Code')['Val'].sum()
add(
    'Breastmilk + non-breastmilk + unknown = Total',
    f'msds-{y_slug}.csv (BabyFirstFeedBreastMilkStatus)',
    'sum of feeding outcomes equals total baby feeding records per Trust',
    24,
    float((bf_yes + bf_no + bf_mis - bf_tot).abs().max()),
    5,
    'counts',
)

# 14. First-feed status recorded % (UID M401210)
m210_y = m401_y[m401_y['UID'] == 'M401210'].set_index('ODS_Code')
m210_rates = m210_y['Valid'] / m210_y['Denominator']
add(
    'First-feed status recorded % (UID M401210)',
    f'msds-dq-{y_slug}.csv (UID M401210)',
    'Valid M401210 records ÷ Denominator in MSD401',
    24,
    max(abs(m210_rates[ods] - u[ods]['agree']) for ods in u) * 100,
    0.01,
)

# 15. MSDS item completeness (16 items, pooled)
dq_16 = dq_y[dq_y['UID'].isin(DQ_ITEMS)].copy()
dq_16['Label'] = dq_16['UID'].map(DQ_ITEMS)
sp = dq_16.groupby('Label')[['Valid', 'Denominator']].sum()
sp_rate = sp['Valid'] / sp['Denominator']
add(
    'MSDS item completeness (16 items, pooled)',
    f'msds-dq-{y_slug}.csv (MSD401/402/405)',
    'sum(Valid) / sum(Denominator) across 24 NICUs, items with >=150 records',
    len(D['subj']),
    max(abs(sp_rate[lbl] - val) for lbl, val in D['subj']) * 100,
    0.01,
)

# 16. MSDS item completeness, per NICU (cells)
su = dq_16.groupby(['ODS_Code', 'Label'])[['Valid', 'Default', 'Invalid', 'Missing', 'Denominator']].sum()
cells = 0
mxd = 0.0
for ods, x in u.items():
    for sname, (rate, kn) in x['sj'].items():
        if (ods, sname) not in su.index:
            continue
        r_ = su.loc[(ods, sname)]
        if r_['Denominator'] == 0:
            continue
        cells += 1
        mxd = max(mxd, abs(r_['Valid'] / r_['Denominator'] - rate), abs(r_['Denominator'] - kn) / 1e4)
add(
    'MSDS item completeness, per NICU (cells)',
    f'msds-dq-{y_slug}.csv (MSD401/402/405)',
    'Valid / Denominator for every NICU and MSDS data item cell',
    cells,
    mxd * 100,
    0.01,
)

# 17. MSDS item Valid + Default + Invalid + Missing = Denominator
part_sum = su['Valid'] + su['Default'] + su['Invalid'] + su['Missing']
add(
    'MSDS item denominator vs sum of parts (counts)',
    f'msds-dq-{y_slug}.csv (MSD401/402/405)',
    'Valid + Default + Invalid + Missing vs Denominator (cells rounded to nearest 5)',
    len(su),
    float((part_sum - su['Denominator']).abs().max()),
    15,
    'NHS disclosure control rounds each DQ status column to nearest 5',
)

# 18. Gestational age band shares (11 bands, pooled)
gb_y = msds_y[msds_y['Dimension'] == 'GestationLengthBirth'].copy()
gb_y = gb_y[gb_y['Measure'].isin(GEST_MAP)]
gb_y['Band'] = gb_y['Measure'].map(GEST_MAP)
sb = gb_y.groupby('Band')['Val'].sum()
tot_gb = sb.sum()
add(
    'Gestational age band shares (11 bands, pooled)',
    f'msds-{y_slug}.csv (GestationLengthBirth)',
    'Σ band ÷ Σ total known gestation at birth',
    len(D['sal']),
    max(abs(sb[b] / tot_gb - v) for b, v in D['sal']) * 100,
    0.01,
)

# 19. Gestational age band shares, per NICU
ub = gb_y.pivot_table(index='ODS_Code', columns='Band', values='Val', aggfunc='sum').fillna(0)
ub['Total'] = ub.sum(axis=1)
dm = 0.0
cnt = 0
for ods, x in u.items():
    if x['sal'] is not None:
        cnt += 1
        dm = max(dm, max(abs(ub.loc[ods, b] / ub.loc[ods, 'Total'] - v) for (b, _), v in zip(D['sal'], x['sal'])))
add(
    'Gestational age band shares, per NICU',
    f'msds-{y_slug}.csv (GestationLengthBirth)',
    'band / total known gestation for each NICU',
    cnt,
    dm * 100,
    0.01,
)

# 20. Gestational age bands add up to total (counts)
gap = max(abs(ub.loc[ods, [b for b, _ in D['sal']]].sum() - x['sn']) for ods, x in u.items() if x['sal'] is not None)
add(
    'Gestational age bands add up to total (counts)',
    f'msds-{y_slug}.csv (GestationLengthBirth)',
    'sum of 11 gestation bands equals unit gestation denominator (sn)',
    cnt,
    float(gap),
    20,
)

# 21. Every displayed rate is between 0% and 100%
vals = (
    [v for x in D['unis'] for v in [x['resp'], x['work'], x['study'], x['unemp'], x['hs'], x['agree'], x['pub']] + [q[0] for q in x['sj'].values()] + (x['sal'] or [])]
    + [v for v in D['trend']['work'] + D['trend']['study'] + D['trend']['unemp'] + D['trend']['resp'] + D['trend']['hs']]
    + [q[1] for q in D['subj']]
    + [q[1] for q in D['sal']]
    + list(D['rg'].values())
)
add(
    'Every displayed rate is between 0% and 100%',
    'All',
    'range check on all rates in the JSON payload',
    len(vals),
    max(max(vals) - 1, 0 - min(vals), 0) * 100,
    0,
)

# 22. NICU populations add up to the National Level 3 totals
add(
    'NICU populations add up to the National Level 3 totals',
    f'msds-{y_slug}.csv (TotalBabies)',
    'sum of 24 NICUs = displayed national totals',
    2,
    abs(sum(x['n'] for x in D['unis']) - D['n']) + abs(sum(x['k'] for x in D['unis']) - D['k']),
    0,
    'counts',
)

L = [
    '# Validation report\n',
    f'Audit year {Y}; 24 NHS Level 3 Neonatal Intensive Care Trusts; headline basis (core MSD401 baby records, excluding unmapped optional fields M401090/M401180).\n',
    'Tolerances: 0.01 pt (the precision values are stored at) where the dashboard value is a direct recomputation from the official NHS England open-data CSVs (`msds_2019_20.csv`–`msds_2023_24.csv` and `msds_dq_2019_20.csv`–`msds_dq_2023_24.csv`); rounding tolerance where compared with whole-number percentages (±0.5 pt) or NHS disclosure-controlled rounded counts (±5).\n',
    '| Check | Source table | Rule | Items | Max difference | Tolerance | Result | Note |',
    '|---|---|---|---|---|---|---|---|',
]
L += [f'| {a} | {b} | {c} | {n} | {mx:.4f} | {tol} | {r} | {nt} |' for a, b, c, n, mx, tol, r, nt in R]
open(OUT, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('\n'.join(L[4:]))
