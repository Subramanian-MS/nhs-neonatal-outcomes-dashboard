"""Extracts native NHS headline-slice CSV tables for Power BI (Dash_*.csv) and computes
the initial pooled and per-unit summary JSON (dash/data.json) directly from official NHS England counts."""
import pandas as pd, json, shutil, os, glob

O = 'out/'
D = 'dash/'
os.makedirs(D, exist_ok=True)

for old_f in glob.glob(f'{D}*.csv'):
    os.remove(old_f)

P = pd.read_csv(O + 'Dim_Unit.csv', dtype=str)
nm = dict(zip(P.ODS_Code, P.Unit))
odn_map = dict(zip(P.ODS_Code, P.ODN_Region))

comp = pd.read_csv(O + 'Fact_CompletenessSummary.csv', dtype={'ODS_Code': str})
ind = pd.read_csv(O + 'Fact_ClinicalIndicators.csv', dtype={'ODS_Code': str})
nut = pd.read_csv(O + 'Fact_FirstFeedNutrition.csv', dtype={'ODS_Code': str})
gest = pd.read_csv(O + 'Fact_GestationBand.csv', dtype={'ODS_Code': str})
dq = pd.read_csv(O + 'Fact_MSDS_DataQuality.csv', dtype={'ODS_Code': str})
dq_items = pd.read_csv(O + 'Dim_MSDSDataItem.csv', dtype=str)

# Export Power BI headline tables (Dash_*.csv) and dimensions (Dim_*.csv)
comp.to_csv(D + 'Dash_CompletenessSummary.csv', index=False)
ind.to_csv(D + 'Dash_ClinicalIndicators.csv', index=False)
nut.to_csv(D + 'Dash_FirstFeedNutrition.csv', index=False)
gest.to_csv(D + 'Dash_GestationBand.csv', index=False)

dq_16 = dq.merge(dq_items[['UID', 'Item_Label']], on='UID', how='inner')[
    ['ODS_Code', 'Year', 'DataTable', 'UID', 'Item_Label', 'Valid', 'Default', 'Invalid', 'Missing', 'Denominator']
]
dq_16.to_csv(D + 'Dash_MSDSDataItems.csv', index=False)

for f in ['Dim_Unit', 'Dim_Year', 'Dim_ClinicalIndicator', 'Dim_MSDSDataItem', 'Dim_GestationBand', 'Dim_FeedingCategory']:
    shutil.copy(O + f + '.csv', D + f + '.csv')

Y = os.environ.get('LATEST_YEAR', '2023/24')
years = sorted(comp['Year'].unique())
R = lambda x, d=4: round(float(x), d)

# 5-year national pooled trends from reported numerators and denominators
def pooled_ind_trend(ind_name):
    sub = ind[(ind['Indicator'] == ind_name) & (ind['Is_Reported'] == 1)]
    g = sub.groupby('Year')[['Numerator', 'Denominator']].sum()
    return [R(g.loc[y, 'Numerator'] / g.loc[y, 'Denominator']) for y in years]

comp_rep = comp[comp['Is_Reported'] == 1].groupby('Year')[['Validated_Babies', 'Total_Babies', 'Core_Valid_Fields', 'Core_Denom_Fields']].sum()
resp_trend = [R(comp_rep.loc[y, 'Validated_Babies'] / comp_rep.loc[y, 'Total_Babies']) for y in years]

work_trend = pooled_ind_trend('SkinToSkinContact1HourTerm')
study_trend = pooled_ind_trend('GestAgeFormalAntenatalBookingGroup')
unemp_trend = pooled_ind_trend('ApgarScore5TermGroup7')
hs_trend = pooled_ind_trend('BabyFirstFeedBreastMilkStatus')

comp_y = comp[comp['Year'] == Y].set_index('ODS_Code').sort_index()
ind_y = ind[ind['Year'] == Y].set_index(['ODS_Code', 'Indicator'])

# 16 benchmarked MSDS items in latest year
dq_y = dq_16[dq_16['Year'] == Y].groupby('Item_Label')[['Valid', 'Denominator']].sum()
dq_y = dq_y[dq_y['Denominator'] >= 150].copy()
dq_y['Rate'] = dq_y['Valid'] / dq_y['Denominator']
dq_y = dq_y.sort_values('Rate', ascending=False)

# 11 GestationLengthBirth bands in latest year
gest_y = gest[gest['Year'] == Y].groupby('Gestation_Band')['Babies'].sum()
tot_gest = gest_y['Total']
bands = pd.read_csv(O + 'Dim_GestationBand.csv')
order = [b for b in bands.Gestation_Band if b != 'Total']

unis = []
for ods in sorted(nm.keys()):
    c_row = comp_y.loc[ods]
    w_row = ind_y.loc[(ods, 'SkinToSkinContact1HourTerm')]
    s_row = ind_y.loc[(ods, 'GestAgeFormalAntenatalBookingGroup')]
    u_row = ind_y.loc[(ods, 'ApgarScore5TermGroup7')]
    h_row = ind_y.loc[(ods, 'BabyFirstFeedBreastMilkStatus')]
    unis.append({
        'u': nm[ods],
        'ods': ods,
        'odn': odn_map[ods],
        'resp': R(c_row['Raw_Table_Rate']),
        'work': R(w_row['Rate']),
        'study': R(s_row['Rate']),
        'unemp': R(u_row['Rate']),
        'hs': R(h_row['Rate']),
        'agree': R(c_row['FirstFeed_Recorded_Rate']),
        'k': int(c_row['Validated_Babies']),
        'den': {
            'resp': int(c_row['Raw_Denom_Fields']),
            'pub': int(c_row['Raw_Denom_Fields']),
            'work': int(w_row['Denominator']),
            'study': int(s_row['Denominator']),
            'unemp': int(u_row['Denominator']),
            'hs': int(h_row['Denominator']),
            'agree': int(c_row['FirstFeed_Denom']),
        },
    })

# Clinical indicator summary counts for mix
ind_y_sum = ind[ind['Year'] == Y].groupby('Indicator')[['Numerator', 'Denominator', 'Missing_Count']].sum()
mix = {
    'SkinToSkin_Yes': int(ind_y_sum.loc['SkinToSkinContact1HourTerm', 'Numerator']),
    'SkinToSkin_No': int(ind_y_sum.loc['SkinToSkinContact1HourTerm', 'Denominator'] - ind_y_sum.loc['SkinToSkinContact1HourTerm', 'Numerator']),
    'Booking_Early_0_70d': int(ind_y_sum.loc['GestAgeFormalAntenatalBookingGroup', 'Numerator']),
    'Booking_Later_71d_plus': int(ind_y_sum.loc['GestAgeFormalAntenatalBookingGroup', 'Denominator'] - ind_y_sum.loc['GestAgeFormalAntenatalBookingGroup', 'Numerator']),
    'Apgar5_Low_0_6': int(ind_y_sum.loc['ApgarScore5TermGroup7', 'Numerator']),
    'Apgar5_Normal_7_10': int(ind_y_sum.loc['ApgarScore5TermGroup7', 'Denominator'] - ind_y_sum.loc['ApgarScore5TermGroup7', 'Numerator']),
}

data = {
    'year': Y,
    'n': int(comp_y['Total_Babies'].sum()),
    'k': int(comp_y['Validated_Babies'].sum()),
    'trend': {
        'years': years,
        'work': work_trend,
        'study': study_trend,
        'unemp': unemp_trend,
        'resp': resp_trend,
        'hs': hs_trend,
    },
    'rg': {
        'resp': resp_trend[-1],
        'work': work_trend[-1],
        'study': study_trend[-1],
        'unemp': unemp_trend[-1],
        'hs': hs_trend[-1],
        'agree': R(comp_y['FirstFeed_Valid'].sum() / comp_y['FirstFeed_Denom'].sum()),
    },
    'unis': unis,
    'mix': mix,
    'subj': [[lbl, R(row['Rate'])] for lbl, row in dq_y.iterrows()],
    'sal': [[b.replace('Less than ', '<').replace(' - ', '–'), R(gest_y[b] / tot_gest)] for b in order],
    'subjk': {lbl: int(row['Denominator']) for lbl, row in dq_y.iterrows()},
}

json.dump(data, open('dash/data.json', 'w'), separators=(',', ':'))
print(os.path.getsize('dash/data.json'), len(data['subj']), data['rg'], data['sal'][:3])
