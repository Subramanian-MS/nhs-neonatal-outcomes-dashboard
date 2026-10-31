"""Adds per-unit MSDS data item completeness rates, gestational age distributions, and raw MSD401 table rates (dash/data3.json)."""
import pandas as pd, json, sys

DATA = sys.argv[1] if len(sys.argv) > 1 else 'dash/data2.json'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'dash/data3.json'
DASH = sys.argv[3] if len(sys.argv) > 3 else 'dash'

d = json.load(open(DATA))
Y = d['year']

dq = pd.read_csv(f'{DASH}/Dash_MSDSDataItems.csv', dtype={'ODS_Code': str})
dq_y = dq[dq['Year'] == Y].groupby(['ODS_Code', 'Item_Label'])[['Valid', 'Denominator']].sum()

gest = pd.read_csv(f'{DASH}/Dash_GestationBand.csv', dtype={'ODS_Code': str})
gest_y = gest[gest['Year'] == Y].pivot_table(index='ODS_Code', columns='Gestation_Band', values='Babies', aggfunc='sum').fillna(0)
raw_band = lambda b: b.replace('<', 'Less than ').replace('–', ' - ')

comp = pd.read_csv(f'{DASH}/Dash_CompletenessSummary.csv', dtype={'ODS_Code': str})
comp_y = comp[comp['Year'] == Y].set_index('ODS_Code')

for u in d['unis']:
    ods = u['ods']
    u['sj'] = {}
    for name, _ in d['subj']:
        if (ods, name) in dq_y.index:
            r = dq_y.loc[(ods, name)]
            den = int(r['Denominator'])
            val = int(r['Valid'])
            u['sj'][name] = [round(val / den, 4) if den > 0 else 0.0, den]
        else:
            u['sj'][name] = [0.0, 0]

    if ods in gest_y.index and gest_y.loc[ods, 'Total'] > 0:
        t = gest_y.loc[ods, 'Total']
        u['sal'] = [round(float(gest_y.loc[ods, raw_band(b)] / t), 4) for b, _ in d['sal']]
        u['sn'] = int(t)
    else:
        u['sal'] = None
        u['sn'] = 0

    u['pub'] = round(float(comp_y.loc[ods, 'Raw_Table_Rate']), 4)

d['rg']['pub'] = round(float(comp_y['Raw_Valid_Fields'].sum() / comp_y['Raw_Denom_Fields'].sum()), 4)

json.dump(d, open(OUT, 'w'), separators=(',', ':'))
print(
    len(open(OUT).read()),
    'bytes;',
    sum(1 for u in d['unis'] if u['sn'] >= 8),
    'units with >=8 gestation-band records;',
    sum(1 for u in d['unis'] for v in u['sj'].values() if v[1] < 8),
    'MSDS item cells under 8 (NHS SDC suppressed)',
)
