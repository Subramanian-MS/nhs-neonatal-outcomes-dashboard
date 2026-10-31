"""Adds 5-year per-unit clinical trends, indicator counts, and first-feed nutrition shares to dash/data2.json."""
import pandas as pd, json, os

d = json.load(open('dash/data.json'))
comp = pd.read_csv('dash/Dash_CompletenessSummary.csv', dtype={'ODS_Code': str})
ind = pd.read_csv('dash/Dash_ClinicalIndicators.csv', dtype={'ODS_Code': str})
nut = pd.read_csv('dash/Dash_FirstFeedNutrition.csv', dtype={'ODS_Code': str})

yrs = d['trend']['years']
Y = d['year']

comp_y = comp[comp['Year'] == Y].set_index('ODS_Code')
ind_piv = ind.pivot_table(index=['ODS_Code', 'Year'], columns='Indicator', values='Rate_Sparkline', aggfunc='first')
ind_num = ind[ind['Year'] == Y].pivot_table(index='ODS_Code', columns='Indicator', values='Numerator', aggfunc='first')
ind_den = ind[ind['Year'] == Y].pivot_table(index='ODS_Code', columns='Indicator', values='Denominator', aggfunc='first')
nut_y = nut[nut['Year'] == Y].pivot_table(index='ODS_Code', columns='Feeding_Category', values='Babies', aggfunc='sum').fillna(0)

def feed_shares(r):
    k = r['Total Known']
    if k <= 0:
        return [0.0, 0.0]
    return [
        round(float(r['Maternal or Donor Breast Milk'] / k), 4),
        round(float(r['Not Breast Milk'] / k), 4),
    ]

for u in d['unis']:
    ods = u['ods']
    u['n'] = int(comp_y.loc[ods, 'Total_Babies'])
    u['tr'] = [
        [round(float(ind_piv.loc[(ods, y), ind_key]), 4) for y in yrs]
        for ind_key in ['SkinToSkinContact1HourTerm', 'GestAgeFormalAntenatalBookingGroup', 'ApgarScore5TermGroup7']
    ]
    u['mix'] = [
        int(ind_num.loc[ods, 'SkinToSkinContact1HourTerm']),
        int(ind_den.loc[ods, 'SkinToSkinContact1HourTerm'] - ind_num.loc[ods, 'SkinToSkinContact1HourTerm']),
        int(ind_num.loc[ods, 'GestAgeFormalAntenatalBookingGroup']),
        int(ind_den.loc[ods, 'GestAgeFormalAntenatalBookingGroup'] - ind_num.loc[ods, 'GestAgeFormalAntenatalBookingGroup']),
        int(ind_num.loc[ods, 'ApgarScore5TermGroup7']),
        int(ind_den.loc[ods, 'ApgarScore5TermGroup7'] - ind_num.loc[ods, 'ApgarScore5TermGroup7']),
    ]
    u['sk'] = feed_shares(nut_y.loc[ods])

tot_nut = nut_y.sum()
d['sk'] = feed_shares(tot_nut)
d['mixk'] = [
    'SkinToSkin_Yes',
    'SkinToSkin_No',
    'Booking_Early_0_70d',
    'Booking_Later_71d_plus',
    'Apgar5_Low_0_6',
    'Apgar5_Normal_7_10',
]
json.dump(d, open('dash/data2.json', 'w'), separators=(',', ':'))

# Cross-check exact rates vs whole-number percentages
ind_lat = ind[ind['Year'] == Y]
for ind_key, label in [
    ('SkinToSkinContact1HourTerm', '1-hr skin-to-skin'),
    ('ApgarScore5TermGroup7', 'Low 5-min Apgar'),
]:
    sub = ind_lat[ind_lat['Indicator'] == ind_key]
    diff = (sub['Rate'] - sub['Whole_Pct'] / 100.0).abs().max() * 100
    print(f'max |{label} exact vs whole-number %| pp:', round(float(diff), 2))
print(os.path.getsize('dash/data2.json'))
