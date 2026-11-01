"""Standardises and harmonises the 5 annual NHS England Maternity Services Data Set (MSDS)
and Data Quality CSV extracts (2019/20 to 2023/24) from flt/msds-*.csv and flt/msds-dq-*.csv
into native NHS analytical fact tables in out/."""
import os, glob, numpy as np, pandas as pd

OUT = 'out'
os.makedirs(OUT, exist_ok=True)

# Remove any legacy files in out/
for old_f in glob.glob(f'{OUT}/*.csv'):
    os.remove(old_f)

UNITS = [
    ('RR8', "Leeds Children's Hospital", 'Leeds Teaching Hospitals NHS Trust (Leeds Centre for Newborn Care)', 'Yorkshire & Humber'),
    ('RHQ', 'Sheffield Jessop Wing', 'Sheffield Teaching Hospitals NHS Foundation Trust', 'Yorkshire & Humber'),
    ('RAE', 'Bradford Royal Infirmary', 'Bradford Teaching Hospitals NHS Foundation Trust', 'Yorkshire & Humber'),
    ('RWA', 'Hull Royal Infirmary', 'Hull University Teaching Hospitals NHS Trust', 'Yorkshire & Humber'),
    ('RJ1', "Evelina London (St Thomas')", "Guy's and St Thomas' NHS Foundation Trust", 'London South'),
    ('RRV', 'UCLH Elizabeth Garrett Anderson', 'University College London Hospitals NHS Foundation Trust', 'London North Central & East'),
    ('RJZ', "King's College Hospital", "King's College Hospital NHS Foundation Trust", 'London South'),
    ('RQM', 'Chelsea & Westminster Hospital', 'Chelsea and Westminster Hospital NHS Foundation Trust', 'London North West'),
    ('RJ7', "St George's Hospital London", "St George's University Hospitals NHS Foundation Trust", 'London South'),
    ('RQX', 'Homerton University Hospital', 'Homerton Healthcare NHS Foundation Trust', 'London North Central & East'),
    ('R0A', "St Mary's Hospital Manchester", 'Manchester University NHS Foundation Trust', 'North West'),
    ('REP', "Liverpool Women's Hospital", "Liverpool Women's NHS Foundation Trust", 'North West'),
    ('RXN', 'Royal Preston Hospital', 'Lancashire Teaching Hospitals NHS Foundation Trust', 'North West'),
    ('RTD', 'Royal Victoria Newcastle', 'The Newcastle upon Tyne Hospitals NHS Foundation Trust', 'Northern'),
    ('RTR', 'James Cook Middlesbrough', 'South Tees Hospitals NHS Foundation Trust', 'Northern'),
    ('RGT', 'Rosie Hospital Cambridge', 'Cambridge University Hospitals NHS Foundation Trust', 'East of England'),
    ('RM1', 'Norfolk & Norwich Hospital', 'Norfolk and Norwich University Hospitals NHS Foundation Trust', 'East of England'),
    ('RTH', 'John Radcliffe Oxford', 'Oxford University Hospitals NHS Foundation Trust', 'Thames Valley & Wessex'),
    ('RHM', 'Princess Anne Southampton', 'University Hospital Southampton NHS Foundation Trust', 'Thames Valley & Wessex'),
    ('RVJ', 'Southmead Hospital Bristol', 'North Bristol NHS Trust', 'South West'),
    ('RA7', "St Michael's Hospital Bristol", 'University Hospitals Bristol and Weston NHS Foundation Trust', 'South West'),
    ('RQ3', "Birmingham Women's Hospital", "Birmingham Women's and Children's NHS Foundation Trust", 'West Midlands'),
    ('RKB', 'University Hospital Coventry', 'University Hospitals Coventry and Warwickshire NHS Trust', 'West Midlands'),
    ('RX1', "Queen's Medical Centre Nottingham", 'Nottingham University Hospitals NHS Trust', 'East Midlands'),
]

GEST_BANDS = [
    ('27 weeks and under', 'Less than 28 wks'),
    ('28 to 31 weeks', '28 - 31 wks'),
    ('32 to 33 weeks', '32 - 33 wks'),
    ('34 to 36 weeks', '34 - 36 wks'),
    ('37 weeks', '37 wks'),
    ('38 weeks', '38 wks'),
    ('39 weeks', '39 wks'),
    ('40 weeks', '40 wks'),
    ('41 weeks', '41 wks'),
    ('42 weeks', '42 wks'),
    ('43 weeks and over', '43+ wks'),
]

DIM_MAP = {
    'TOTAL BABIES': 'TotalBabies',
    'TOTALBABIES': 'TotalBabies',
    'TOTAL DELIVERIES': 'TotalDeliveries',
    'TOTALDELIVERIES': 'TotalDeliveries',
    'SKINTOSKINCONTACT1HOURTERM': 'SkinToSkinContact1HourTerm',
    'APGARSCORE5TERMGROUP7': 'ApgarScore5TermGroup7',
    'BABYFIRSTFEEDBREASTMILKSTATUS': 'BabyFirstFeedBreastMilkStatus',
    'GESTATIONATBOOKING': 'GestAgeFormalAntenatalBookingGroup',
    'GESTAGEFORMALANTENATALBOOKINGGROUP': 'GestAgeFormalAntenatalBookingGroup',
    'GESTATIONLENGTHBIRTH': 'GestationLengthBirth',
    'GESTATIONLENGTHBIRTHGROUP37': 'GestationLengthBirthGroup37',
}

def r5(x):
    return int(5 * round(float(x) / 5.0))

def wilson_ci(num, den):
    if den <= 0:
        return 0.0, 0.0
    p = num / den
    z = 1.95996
    denom = 1.0 + z * z / den
    centre = (p + z * z / (2.0 * den)) / denom
    half = (z * np.sqrt((p * (1.0 - p) + z * z / (4.0 * den)) / den)) / denom
    return round(max(0.0, centre - half), 4), round(min(1.0, centre + half), 4)

# 1. Load and harmonise all 5 years of msds-*.csv
msds_frames = []
for f in sorted(glob.glob('flt/msds-20*.csv')):
    d = pd.read_csv(f, dtype=str, keep_default_na=False)
    for c in d.columns:
        d[c] = d[c].str.replace('\xa0', ' ', regex=False).str.strip()
    d['Dim_Upper'] = d['Dimension'].str.upper()
    d['Dimension_Std'] = d['Dim_Upper'].map(lambda x: DIM_MAP.get(x, x))
    d['Value_Num'] = pd.to_numeric(d['Value'], errors='coerce').fillna(0).astype(int)
    msds_frames.append(d)

msds_all = pd.concat(msds_frames, ignore_index=True)
msds_out = msds_all[['ODS_Code', 'Trust_Name', 'ODN_Region', 'Year', 'Dimension_Std', 'Measure', 'Count_Of', 'Value_Num']].rename(
    columns={'Dimension_Std': 'Dimension', 'Value_Num': 'Value'}
)
msds_out.to_csv(f'{OUT}/Fact_MSDS_Measures.csv', index=False, encoding='utf-8')

# 2. Load and harmonise all 5 years of msds-dq-*.csv
dq_frames = []
for f in sorted(glob.glob('flt/msds-dq-20*.csv')):
    d = pd.read_csv(f, dtype=str, keep_default_na=False)
    for c in d.columns:
        d[c] = d[c].str.replace('\xa0', ' ', regex=False).str.strip()
    for c in ['Valid', 'Default', 'Invalid', 'Missing', 'Denominator']:
        d[c] = pd.to_numeric(d[c], errors='coerce').fillna(0).astype(int)
    d['Is_MSD401_Field'] = (d['DataTable'].str.startswith('MSD401') & (d['UID'] != 'MSD401')).astype(int)
    d['Is_Core_MSD401'] = ((d['Is_MSD401_Field'] == 1) & (~d['UID'].isin(['M401090', 'M401180']))).astype(int)
    dq_frames.append(d)

dq_all = pd.concat(dq_frames, ignore_index=True)
dq_all.to_csv(f'{OUT}/Fact_MSDS_DataQuality.csv', index=False, encoding='utf-8')

years = sorted(msds_out['Year'].unique())

# 3. Build Fact_CompletenessSummary.csv and Fact_ClinicalIndicators.csv and Fact_FirstFeedNutrition.csv
comp_rows = []
ind_rows = []
nut_rows = []
gest_rows = []

for y in years:
    m_y = msds_out[msds_out['Year'] == y]
    dq_y = dq_all[dq_all['Year'] == y]
    for ods, short_name, full_name, odn in UNITS:
        mt = m_y[m_y['ODS_Code'] == ods]
        dqt = dq_y[dq_y['ODS_Code'] == ods]

        # Total babies
        tb = int(mt[mt['Dimension'] == 'TotalBabies']['Value'].sum())
        m401_fields = dqt[dqt['Is_MSD401_Field'] == 1]
        core_fields = dqt[dqt['Is_Core_MSD401'] == 1]

        raw_v = int(m401_fields['Valid'].sum())
        raw_d = int(m401_fields['Denominator'].sum())
        core_v = int(core_fields['Valid'].sum())
        core_d = int(core_fields['Denominator'].sum())

        m210 = m401_fields[m401_fields['UID'] == 'M401210']
        ff_v = int(m210['Valid'].sum())
        ff_d = int(m210['Denominator'].sum())

        is_rep = 1 if (tb > 0 and raw_d > 0) else 0
        core_rate = (core_v / core_d) if core_d > 0 else np.nan
        raw_rate = (raw_v / raw_d) if raw_d > 0 else np.nan
        ff_rate = (ff_v / ff_d) if ff_d > 0 else np.nan
        k_babies = r5(tb * raw_rate) if (tb > 0 and raw_d > 0) else 0

        comp_rows.append({
            'ODS_Code': ods,
            'Year': y,
            'Total_Babies': tb,
            'Validated_Babies': k_babies,
            'Unvalidated_Babies': max(0, tb - k_babies),
            'Core_Valid_Fields': core_v,
            'Core_Denom_Fields': core_d,
            'Core_Completeness_Rate': round(core_rate, 6) if not np.isnan(core_rate) else np.nan,
            'Raw_Valid_Fields': raw_v,
            'Raw_Denom_Fields': raw_d,
            'Raw_Table_Rate': round(raw_rate, 6) if not np.isnan(raw_rate) else np.nan,
            'FirstFeed_Valid': ff_v,
            'FirstFeed_Denom': ff_d,
            'FirstFeed_Recorded_Rate': round(ff_rate, 6) if not np.isnan(ff_rate) else np.nan,
            'Is_Reported': is_rep,
        })

        # 4 Clinical Indicators from msds
        # (a) SkinToSkinContact1HourTerm
        sk = mt[mt['Dimension'] == 'SkinToSkinContact1HourTerm']
        sk_yes = int(sk[sk['Measure'].str.upper() == 'YES']['Value'].sum())
        sk_no = int(sk[sk['Measure'].str.upper() == 'NO']['Value'].sum())
        sk_mis = int(sk[sk['Measure'].str.upper().str.startswith('MISSING')]['Value'].sum())
        sk_den = sk_yes + sk_no

        # (b) GestAgeFormalAntenatalBookingGroup
        bk = mt[mt['Dimension'] == 'GestAgeFormalAntenatalBookingGroup']
        bk_early = int(bk[bk['Measure'].isin(['0 to 70 days', '00-04 weeks', '05-09 weeks', '10 weeks'])]['Value'].sum())
        bk_known = int(bk[~bk['Measure'].str.lower().str.startswith('missing')]['Value'].sum())
        bk_mis = int(bk[bk['Measure'].str.lower().str.startswith('missing')]['Value'].sum())

        # (c) ApgarScore5TermGroup7
        ap = mt[mt['Dimension'] == 'ApgarScore5TermGroup7']
        ap_low = int(ap[ap['Measure'] == '0 to 6']['Value'].sum())
        ap_norm = int(ap[ap['Measure'] == '7 to 10']['Value'].sum())
        ap_mis = int(ap[ap['Measure'].str.lower().str.startswith('missing')]['Value'].sum())
        ap_den = ap_low + ap_norm

        # (d) BabyFirstFeedBreastMilkStatus
        bf = mt[mt['Dimension'] == 'BabyFirstFeedBreastMilkStatus']
        bf_yes = int(bf[bf['Measure'] == 'Maternal or Donor Breast Milk']['Value'].sum())
        bf_no = int(bf[bf['Measure'] == 'Not Breast Milk']['Value'].sum())
        bf_mis = int(bf[bf['Measure'].str.lower().str.startswith('missing')]['Value'].sum())
        bf_den = bf_yes + bf_no

        for ind_name, num_label, num_v, den_v, mis_v in [
            ('SkinToSkinContact1HourTerm', 'Yes (within 1 hour of birth)', sk_yes, sk_den, sk_mis),
            ('GestAgeFormalAntenatalBookingGroup', '0 to 70 days (<=10 completed weeks)', bk_early, bk_known, bk_mis),
            ('ApgarScore5TermGroup7', '0 to 6 (low 5-minute Apgar)', ap_low, ap_den, ap_mis),
            ('BabyFirstFeedBreastMilkStatus', 'Maternal or Donor Breast Milk', bf_yes, bf_den, bf_mis),
        ]:
            rate_v = (num_v / den_v) if den_v > 0 else np.nan
            ci_lo, ci_hi = wilson_ci(num_v, den_v)
            ind_rows.append({
                'ODS_Code': ods,
                'Year': y,
                'Indicator': ind_name,
                'Numerator_Label': num_label,
                'Numerator': num_v,
                'Denominator': den_v,
                'Missing_Count': mis_v,
                'Total_Count': den_v + mis_v,
                'Rate': round(rate_v, 6) if not np.isnan(rate_v) else np.nan,
                'Whole_Pct': int(round(rate_v * 100)) if not np.isnan(rate_v) else 0,
                'CI_Low': ci_lo,
                'CI_High': ci_hi,
                'Is_Reported': 1 if den_v > 0 else 0,
            })

        for f_cat, f_cnt in [
            ('Maternal or Donor Breast Milk', bf_yes),
            ('Not Breast Milk', bf_no),
            ('Missing Value / Value outside reporting parameters', bf_mis),
            ('Total Known', bf_den),
            ('Total', bf_den + bf_mis),
        ]:
            nut_rows.append({
                'ODS_Code': ods,
                'Year': y,
                'Feeding_Category': f_cat,
                'Babies': f_cnt,
            })

        # GestationLengthBirth bands (reported natively in 2020/21-2023/24)
        gb = mt[mt['Dimension'] == 'GestationLengthBirth']
        if len(gb) > 0:
            tot_g = 0
            band_vals = []
            for raw_m, clean_b in GEST_BANDS:
                cnt = int(gb[gb['Measure'] == raw_m]['Value'].sum())
                band_vals.append((clean_b, raw_m, cnt))
                tot_g += cnt
            for clean_b, raw_m, cnt in band_vals:
                gest_rows.append({
                    'ODS_Code': ods,
                    'Year': y,
                    'Gestation_Band': clean_b,
                    'Raw_Measure': raw_m,
                    'Babies': cnt,
                    'Share': round(cnt / tot_g, 6) if tot_g > 0 else 0.0,
                })
            gest_rows.append({
                'ODS_Code': ods,
                'Year': y,
                'Gestation_Band': 'Total',
                'Raw_Measure': 'Total known gestation at birth',
                'Babies': tot_g,
                'Share': 1.0 if tot_g > 0 else 0.0,
            })

comp_df = pd.DataFrame(comp_rows)
# Fill any missing early-year rates per unit via backfill so per-unit 5-year sparklines have no gaps
comp_df = comp_df.sort_values(['ODS_Code', 'Year'])
for col in ['Core_Completeness_Rate', 'Raw_Table_Rate', 'FirstFeed_Recorded_Rate']:
    comp_df[col] = comp_df.groupby('ODS_Code')[col].transform(lambda s: s.bfill().ffill())
comp_df.to_csv(f'{OUT}/Fact_CompletenessSummary.csv', index=False, encoding='utf-8')

ind_df = pd.DataFrame(ind_rows).sort_values(['ODS_Code', 'Indicator', 'Year'])
ind_df['Rate_Sparkline'] = ind_df.groupby(['ODS_Code', 'Indicator'])['Rate'].transform(lambda s: s.bfill().ffill())
ind_df.to_csv(f'{OUT}/Fact_ClinicalIndicators.csv', index=False, encoding='utf-8')

pd.DataFrame(nut_rows).to_csv(f'{OUT}/Fact_FirstFeedNutrition.csv', index=False, encoding='utf-8')
pd.DataFrame(gest_rows).to_csv(f'{OUT}/Fact_GestationBand.csv', index=False, encoding='utf-8')

print('Cleaned native NHS England MSDS & Data Quality tables into out/')
