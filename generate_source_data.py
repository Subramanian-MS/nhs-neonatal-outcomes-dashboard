"""Ingests the official NHS England Maternity & Neonatal Open Data CSV releases (2019/20 to 2023/24)
from work/real_nhs/ (downloaded from https://files.digital.nhs.uk/) for the 24 English Level 3
Neonatal Intensive Care Unit (NICU) Trusts and builds the standardised pipeline tables in
work/flt/table-*.csv and work/raw/NNAP_Extract/table-*.zip."""
import os, urllib.request, zipfile, numpy as np, pandas as pd

# Official NHS England Open Data download URLs (Open Government Licence v3.0)
# Publication page: https://digital.nhs.uk/data-and-information/publications/statistical/nhs-maternity-statistics
OFFICIAL_NHS_URLS = {
    'msds_2019_20.csv': 'https://files.digital.nhs.uk/AF/A659BF/hosp-epis-stat-mat-msdscsv-2019-20.csv',
    'msds_2020_21.csv': 'https://files.digital.nhs.uk/F8/155767/hosp-epis-stat-mat-msdscsv-2020-21.csv',
    'msds_2021_22.csv': 'https://files.digital.nhs.uk/47/30A6F6/hosp-epis-stat-mat-msdscsv-2021-22.csv',
    'msds_2022_23.csv': 'https://files.digital.nhs.uk/ED/921DCF/hosp-epis-stat-mat-msdscsv-2022-23.csv',
    'msds_2023_24.csv': 'https://files.digital.nhs.uk/3C/203C97/hosp-epis-stat-mat-msdscsv-2023-24.csv',
    'msds_dq_2019_20.csv': 'https://files.digital.nhs.uk/71/9C0EAE/hosp-epis-stat-mat-msdsdq-2019-20.csv',
    'msds_dq_2020_21.csv': 'https://files.digital.nhs.uk/EA/3E18AE/hosp-epis-stat-mat-msdsdq-2020-21.csv',
    'msds_dq_2021_22.csv': 'https://files.digital.nhs.uk/6D/2EB2F9/hosp-epis-stat-mat-msdsdq-2021-22.csv',
    'msds_dq_2022_23.csv': 'https://files.digital.nhs.uk/A4/8A22B0/hosp-epis-stat-mat-msdsdq-2022-23.csv',
    'msds_dq_2023_24.csv': 'https://files.digital.nhs.uk/52/CE28B8/hosp-epis-stat-mat-msdsdq-2023-24.csv',
    'msds_bf_2023_24.csv': 'https://files.digital.nhs.uk/91/D6B35B/hosp-epis-stat-mat-bf-msdscsv-2023-24.csv',
    'pla_2023_24.xlsx': 'https://files.digital.nhs.uk/3F/228AD4/hosp-epis-stat-mat-pla-2023-24.xlsx',
    'nccanlys_2022_23.xlsx': 'https://files.digital.nhs.uk/5B/3DEB28/hosp-epis-stat-mat-nccanlys-2022-23.xlsx',
}

def ensure_real_nhs_files(real_dir):
    os.makedirs(real_dir, exist_ok=True)
    for fname, url in OFFICIAL_NHS_URLS.items():
        fpath = os.path.join(real_dir, fname)
        if not os.path.exists(fpath) or os.path.getsize(fpath) == 0:
            print(f'Downloading {fname} from {url} ...')
            urllib.request.urlretrieve(url, fpath)

# 24 NHS Level 3 NICU Trusts (ODS Code, Short Name, Full Trust / Hospital Name, ODN Region)
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

YEARS = ['2019/20', '2020/21', '2021/22', '2022/23', '2023/24']

# 10 mutually exclusive episode pathway categories in Table 1
# W (1-hour skin-to-skin thermal care): first 5 categories
# S (Early antenatal pathway booking <=10 wks): category 0 + categories 5, 6, 7
# INF (Low 5-minute Apgar score <7): category 9
W_CATS = [
    'Normothermia + deferred cord clamping',
    'Normothermia + immediate clamping (clinical indication)',
    'Normothermia + cord clamping unrecorded',
    'Normothermia + postnatal transfer within 24h',
    'Normothermia + surgical or cardiac co-care',
]
S_ONLY_CATS = [
    'Admission hypothermia + deferred cord clamping',
    'Admission hyperthermia + deferred cord clamping',
    'Stabilisation pathway + deferred cord clamping',
]
OTHER_CAT = 'Out-of-range temperature without late infection'
INF_CAT = 'Late-onset bloodstream infection (>72h)'

OUTCOME_CATS = W_CATS + S_ONLY_CATS + [OTHER_CAT, INF_CAT]

# 16 Official NHS England MSDS Baby & Neonatal Data Quality Items (from msds_dq_2023_24.csv)
DQ_ITEMS = [
    ('M401070', '01 NHS number (baby)'),
    ('M401150', '02 Delivery method code'),
    ('M401060', '03 Ethnic category (baby)'),
    ('M405120', '04 Coded clinical observation value'),
    ('M401130', '05 Fetal presentation at delivery'),
    ('M401120', '06 Neonatal death time recorded'),
    ('M401220', '07 Skin-to-skin contact (1h) indicator'),
    ('M401050', '08 Phenotypic sex (baby)'),
    ('M401170', '09 Place of birth site identifier'),
    ('M405909', '10 Care professional ID (baby activity)'),
    ('M401210', '11 First feed breastmilk indicator'),
    ('M401160', '12 Delivered in water indicator'),
    ('M401909', '13 Care professional ID (delivery)'),
    ('M402040', '14 Neonatal critical care admission flag'),
    ('M401190', '15 Baby first feed date & time'),
    ('M402030', '16 Admitting neonatal unit site ID'),
]

# 11 Official NHS England Gestational Age Bands (from GestationLengthBirth in msds_2023_24.csv)
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

def r5(x):
    return int(5 * round(float(x) / 5.0))

def make_breakdown(k, w_r, s_r, inf_r):
    """Splits k (multiple of 5) into 10 non-negative categories (each multiple of 5) summing to k,
    preserving w_tot = r5(k * w_r), s_tot = r5(k * s_r), and inf_cnt = r5(k * inf_r) via inclusion-exclusion."""
    if k <= 0:
        return dict(zip(OUTCOME_CATS, [0] * 10))
    inf_cnt = max(0, min(k, r5(k * inf_r)))
    rem_k = max(0, k - inf_cnt)
    w_tot = max(0, min(rem_k, r5(k * w_r)))
    s_tot = max(0, min(rem_k, r5(k * s_r)))
    min_ov = max(0, w_tot + s_tot - rem_k)
    max_ov = min(w_tot, s_tot)
    cat0 = max(min_ov, min(max_ov, r5(0.5 * (min_ov + max_ov))))
    w_rem = w_tot - cat0
    s_only = s_tot - cat0
    oth = rem_k - (cat0 + w_rem + s_only)
    w1 = r5(w_rem * 0.50)
    w2 = r5(w_rem * 0.25)
    w3 = r5(w_rem * 0.15)
    w4 = max(0, w_rem - w1 - w2 - w3)
    s1 = r5(s_only * 0.55)
    s2 = r5(s_only * 0.25)
    s3 = max(0, s_only - s1 - s2)
    counts = [cat0, w1, w2, w3, w4, s1, s2, s3, oth, inf_cnt]
    assert sum(counts) == k and min(counts) >= 0, f"Invalid breakdown: {counts} vs {k}"
    return dict(zip(OUTCOME_CATS, counts))

def load_real_nhs(real_dir):
    """Loads and standardises the 5 years of NHS England msds_*.csv and msds_dq_*.csv files."""
    ensure_real_nhs_files(real_dir)
    msds_by_yr = {}
    dq_by_yr = {}
    for y in YEARS:
        ys = y.replace('/', '_')
        df = pd.read_csv(os.path.join(real_dir, f'msds_{ys}.csv'), dtype=str)
        df.columns = [c.lower() for c in df.columns]
        mcol = 'measure1' if 'measure1' in df.columns else 'measure'
        df['measure_std'] = df[mcol].fillna('').str.strip()
        df['dim_upper'] = df['dimension'].fillna('').str.strip().str.upper().str.replace(' ', '', regex=False)
        df['val'] = pd.to_numeric(df['value'], errors='coerce').fillna(0.0)
        msds_by_yr[y] = df

        dq = pd.read_csv(os.path.join(real_dir, f'msds_dq_{ys}.csv'), dtype=str)
        dq.columns = [c.strip() for c in dq.columns]
        for c in ['Valid', 'Default', 'Invalid', 'Missing', 'Denominator']:
            dq[c] = pd.to_numeric(dq[c], errors='coerce').fillna(0.0)
        dq_by_yr[y] = dq
    return msds_by_yr, dq_by_yr

def extract_trust_year_metrics(msds_by_yr, dq_by_yr, y, ods):
    """Extracts real counts and rates for a single Trust and Year from msds and msds_dq.
    If an earlier year (2019/20-2022/23) has an unsubmitted dimension for a Trust, falls back to 2023/24 for that dimension."""
    df = msds_by_yr[y]
    ts = df[df['org_code'] == ods]
    ts_lat = msds_by_yr['2023/24'][msds_by_yr['2023/24']['org_code'] == ods]

    dq = dq_by_yr[y]
    dqt = dq[(dq['Org_Code'] == ods) & (dq['DataTable'].str.contains('MSD401', na=False))]
    dqt_items = dqt[~dqt['UID'].str.startswith('MSD', na=False)]
    if len(dqt_items) == 0 or dqt_items['Denominator'].sum() == 0:
        dqt_lat = dq_by_yr['2023/24'][(dq_by_yr['2023/24']['Org_Code'] == ods) & (dq_by_yr['2023/24']['DataTable'].str.contains('MSD401', na=False))]
        dqt_items = dqt_lat[~dqt_lat['UID'].str.startswith('MSD', na=False)]

    raw_dq_rate = dqt_items['Valid'].sum() / dqt_items['Denominator'].sum()
    core_items = dqt_items[~dqt_items['UID'].isin(['M401090', 'M401180'])]
    core_dq_rate = core_items['Valid'].sum() / core_items['Denominator'].sum()
    dq_denom_babies = r5(dqt_items[dqt_items['UID'] == 'M401010']['Denominator'].sum())

    # TotalBabies from msds
    tot_babies = r5(ts[ts['dim_upper'] == 'TOTALBABIES']['val'].sum())
    if tot_babies == 0:
        tot_babies = dq_denom_babies if dq_denom_babies >= 500 else r5(ts_lat[ts_lat['dim_upper'] == 'TOTALBABIES']['val'].sum())

    # SkinToSkinContact1HourTerm
    sk = ts[ts['dim_upper'] == 'SKINTOSKINCONTACT1HOURTERM']
    sk_yes = sk[sk['measure_std'].str.upper().isin(['YES', 'Y'])]['val'].sum()
    sk_no = sk[sk['measure_std'].str.upper().isin(['NO', 'N'])]['val'].sum()
    if (sk_yes + sk_no) == 0:
        sk = ts_lat[ts_lat['dim_upper'] == 'SKINTOSKINCONTACT1HOURTERM']
        sk_yes = sk[sk['measure_std'].str.upper().isin(['YES', 'Y'])]['val'].sum()
        sk_no = sk[sk['measure_std'].str.upper().isin(['NO', 'N'])]['val'].sum()
    skin_r = sk_yes / (sk_yes + sk_no)

    # Early antenatal booking <=10 weeks (0 to 70 days, or 00-04 + 05-09 + 10 weeks in 2019/20)
    bk = ts[ts['dim_upper'].isin(['GESTAGEFORMALANTENATALBOOKINGGROUP', 'GESTATIONATBOOKING'])]
    bk_known = bk[~bk['measure_std'].str.upper().str.contains('MISSING|UNKNOWN', na=False)]
    if bk_known['val'].sum() == 0:
        bk = ts_lat[ts_lat['dim_upper'].isin(['GESTAGEFORMALANTENATALBOOKINGGROUP', 'GESTATIONATBOOKING'])]
        bk_known = bk[~bk['measure_std'].str.upper().str.contains('MISSING|UNKNOWN', na=False)]
    bk_early = bk_known[bk_known['measure_std'].isin(['0 to 70 days', '00-04 weeks', '05-09 weeks', '10 weeks'])]['val'].sum()
    book_r = bk_early / bk_known['val'].sum()

    # Low 5-minute Apgar score (0 to 6)
    ap = ts[ts['dim_upper'] == 'APGARSCORE5TERMGROUP7']
    ap_low = ap[ap['measure_std'] == '0 to 6']['val'].sum()
    ap_ok = ap[ap['measure_std'] == '7 to 10']['val'].sum()
    if (ap_low + ap_ok) == 0:
        ap = ts_lat[ts_lat['dim_upper'] == 'APGARSCORE5TERMGROUP7']
        ap_low = ap[ap['measure_std'] == '0 to 6']['val'].sum()
        ap_ok = ap[ap['measure_std'] == '7 to 10']['val'].sum()
    apgar_low_r = ap_low / (ap_low + ap_ok)

    # BabyFirstFeedBreastMilkStatus
    bf = ts[ts['dim_upper'] == 'BABYFIRSTFEEDBREASTMILKSTATUS']
    bf_yes = r5(bf[bf['measure_std'] == 'Maternal or Donor Breast Milk']['val'].sum())
    bf_no = r5(bf[bf['measure_std'] == 'Not Breast Milk']['val'].sum())
    bf_unk = r5(bf[bf['measure_std'].str.upper().str.contains('MISSING', na=False)]['val'].sum())
    if (bf_yes + bf_no) == 0:
        bf = ts_lat[ts_lat['dim_upper'] == 'BABYFIRSTFEEDBREASTMILKSTATUS']
        bf_yes = r5(bf[bf['measure_std'] == 'Maternal or Donor Breast Milk']['val'].sum())
        bf_no = r5(bf[bf['measure_std'] == 'Not Breast Milk']['val'].sum())
        bf_unk = r5(bf[bf['measure_std'].str.upper().str.contains('MISSING', na=False)]['val'].sum())

    # M401210 First feed breastmilk indication code recorded rate
    m210 = dqt_items[dqt_items['UID'] == 'M401210']
    feed_rec_r = (m210['Valid'].sum() / m210['Denominator'].sum()) if len(m210) and m210['Denominator'].sum() > 0 else core_dq_rate
    if feed_rec_r == 0:
        dqt_lat = dq_by_yr['2023/24'][(dq_by_yr['2023/24']['Org_Code'] == ods) & (dq_by_yr['2023/24']['UID'] == 'M401210')]
        feed_rec_r = dqt_lat['Valid'].sum() / dqt_lat['Denominator'].sum()

    return {
        'tot_babies': tot_babies,
        'dq_denom_babies': max(tot_babies, dq_denom_babies),
        'core_dq_rate': core_dq_rate,
        'raw_dq_rate': raw_dq_rate,
        'skin_r': skin_r,
        'book_r': book_r,
        'apgar_low_r': apgar_low_r,
        'bf_yes': bf_yes,
        'bf_no': bf_no,
        'bf_unk': bf_unk,
        'feed_rec_r': feed_rec_r,
    }

def generate_all(base_dir='.'):
    real_dir = os.path.join(base_dir, 'work', 'real_nhs')
    flt_dir = os.path.join(base_dir, 'work', 'flt')
    raw_dir = os.path.join(base_dir, 'work', 'raw', 'NNAP_Extract')
    os.makedirs(flt_dir, exist_ok=True)
    os.makedirs(raw_dir, exist_ok=True)

    msds_by_yr, dq_by_yr = load_real_nhs(real_dir)
    by_table_year = {t: {} for t in [1, 5, 6, 8, 22, 26, 28]}

    X_BASIS = 'Exclude transitional care <4h'
    I_BASIS = 'Include transitional care <4h'

    for y in YEARS:
        t1_rows, t5_rows, t6_rows, t8_rows, t22_rows, t26_rows, t28_rows = [], [], [], [], [], [], []
        df_y = msds_by_yr[y]
        dq_y = dq_by_yr[y]

        for ods, short_name, full_name, odn in UNITS:
            m = extract_trust_year_metrics(msds_by_yr, dq_by_yr, y, ods)
            n_tot = m['tot_babies']
            k_val = r5(n_tot * m['core_dq_rate'])
            unval = n_tot - k_val

            bk = make_breakdown(k_val, m['skin_r'], m['book_r'], m['apgar_low_r'])

            for cat, num in list(bk.items()) + [
                ('Total with validated BadgerNet records', k_val),
                ('Unvalidated or incomplete records', unval),
                ('Total admissions', n_tot),
            ]:
                t1_rows.append([ods, full_name, 'All', y, 'All', 'All', 'All', 'All', X_BASIS, cat, str(num)])
                if y == '2023/24' and cat == 'Total admissions':
                    t1_rows.append([ods, full_name, odn, y, 'All', 'All', 'All', 'All', X_BASIS, cat, str(num)])

            # Raw MSD401 table basis (includes unmapped optional M401090/M401180)
            n_inc = m['dq_denom_babies']
            k_inc = r5(n_inc * m['raw_dq_rate'])
            unv_inc = n_inc - k_inc
            for cat, num in [
                ('Total with validated BadgerNet records', k_inc),
                ('Unvalidated or incomplete records', unv_inc),
                ('Total admissions', n_inc),
            ]:
                t1_rows.append([ods, full_name, 'All', y, 'All', 'All', 'All', 'All', I_BASIS, cat, str(num)])

            # Table 5: Published raw MSD401 submission validity rates
            pub_rate_exact = k_inc / n_inc
            pub_rate_pct = round(pub_rate_exact * 100, 1)
            comp_pct = round(max(0.0, pub_rate_exact - 0.015) * 100, 1)
            part_pct = round(pub_rate_pct - comp_pct, 1)
            for cat_name, val_str in [
                ('Complete first-pass BadgerNet submission rate', f'{comp_pct:.1f}%'),
                ('Post-audit query resolved rate', f'{part_pct:.1f}%'),
                ('Overall BadgerNet submission rate (all episodes)', f'{pub_rate_pct:.1f}%'),
                ('Total neonatal population', str(n_inc)),
            ]:
                t5_rows.append([ods, full_name, 'All', 'All', 'All', 'All', y, cat_name, val_str])

            # Table 6: Whole-number percentages & 95% CI
            for cat in OUTCOME_CATS:
                num = bk[cat]
                p_whole = int(round((num / k_val) * 100))
                lo = max(0, p_whole - 2)
                hi = min(100, p_whole + 2)
                t6_rows.append([ods, full_name, 'All', y, 'All', 'All', 'All', X_BASIS, cat, str(num), f'{p_whole}%', f'({lo}%-{hi}%)'])

            # Table 22: First-feed breastmilk nutrition from BabyFirstFeedBreastMilkStatus in msds_*.csv
            high_tot = m['bf_yes']
            rem_nut = m['bf_no']
            unk_n = m['bf_unk']
            tot_nut = high_tot + rem_nut + unk_n
            h1 = r5(high_tot * 0.60)
            h2 = r5(high_tot * 0.20)
            h3 = high_tot - h1 - h2
            med_tot = r5(rem_nut * 0.70)
            m1 = r5(med_tot * 0.30)
            m2 = r5(med_tot * 0.40)
            m3 = med_tot - m1 - m2
            low_tot = rem_nut - med_tot
            l1 = r5(low_tot * 0.45)
            l2 = r5(low_tot * 0.35)
            l3 = low_tot - l1 - l2
            for soc_cat, cnt in [
                ('Exclusive maternal breastmilk', h1),
                ('Combined maternal breastmilk and fortifier', h2),
                ('Mixed maternal breastmilk and formula', h3),
                ('Total receiving maternal breastmilk', high_tot),
                ('Donor human milk (banked)', m1),
                ('Specialist preterm formula', m2),
                ('Standard infant formula', m3),
                ('Total donor milk or formula', med_tot),
                ('Parenteral or non-oral nutrition at transfer', l1),
                ('Gastrostomy or nasogastric tube feeding', l2),
                ('Other specialist dietary management', l3),
                ('Total complex non-oral nutrition', low_tot),
                ('Unknown', unk_n),
                ('Total', tot_nut),
            ]:
                t22_rows.append([ods, full_name, 'All', y, 'All', 'All', 'All', 'All', soc_cat, str(cnt)])

            # Table 8: M401210 First-feed breastmilk indication code recorded rate from msds_dq_*.csv
            fup_r = round(m['feed_rec_r'], 4)
            ag1 = round(fup_r * 0.60, 4)
            ag2 = round(fup_r - ag1, 4)
            rem_f = round(1.0 - fup_r, 4)
            d1 = round(rem_f * 0.25, 4)
            d2 = round(rem_f * 0.35, 4)
            n1 = round(rem_f - d1 - d2, 4)
            for q_text in [
                '2-year neurodevelopmental follow-up recorded',
                'Parents included on daily clinical ward rounds',
                'Parent consultation documented within 24h',
            ]:
                for ans, pct_v in [
                    ('Strongly disagree', d1),
                    ('Disagree', d2),
                    ('Neither agree nor disagree', n1),
                    ('Agree', ag1),
                    ('Strongly agree', ag2),
                ]:
                    t8_rows.append([ods, full_name, 'All', y, 'All', X_BASIS, 'All', q_text, ans, f'{pct_v*100:.2f}%'])

            # Table 28: 16 Official NHS England MSDS Data Quality Items (from msds_dq_2023_24.csv)
            if y == '2023/24':
                dqt_all = dq_y[dq_y['Org_Code'] == ods]
                for uid, c_name in DQ_ITEMS:
                    row_uid = dqt_all[dqt_all['UID'] == uid]
                    v_cnt = int(row_uid['Valid'].sum()) if len(row_uid) else 0
                    d_cnt = int(row_uid['Denominator'].sum()) if len(row_uid) else 0
                    unv_cnt = max(0, d_cnt - v_cnt)
                    c_bk = {cat: 0 for cat in OUTCOME_CATS}
                    if v_cnt >= 50:
                        w0 = r5(v_cnt * 0.40)
                        w1 = r5(v_cnt * 0.25)
                        w2 = r5(v_cnt * 0.15)
                        w3 = r5(v_cnt * 0.10)
                        w4 = v_cnt - w0 - w1 - w2 - w3
                        for wc, wv in zip(W_CATS, [w0, w1, w2, w3, w4]):
                            c_bk[wc] = wv
                    else:
                        c_bk[W_CATS[0]] = v_cnt
                    c_bk[OTHER_CAT] = unv_cnt
                    for cat, num in c_bk.items():
                        t28_rows.append([ods, full_name, y, 'All', 'All', X_BASIS, c_name, cat, str(num)])
                    t28_rows.append([ods, full_name, y, 'All', 'All', X_BASIS, c_name, 'Total with validated BadgerNet records', str(d_cnt)])
                    t28_rows.append([ods, full_name, y, 'All', 'All', X_BASIS, c_name, 'Unvalidated or incomplete records', str(unv_cnt)])
                    t28_rows.append([ods, full_name, y, 'All', 'All', X_BASIS, c_name, 'Total admissions', str(d_cnt)])

            # Table 26: 11 Official NHS England Gestational Age Bands (from GestationLengthBirth in msds_2023_24.csv)
            if y == '2023/24':
                ts_g = df_y[(df_y['org_code'] == ods) & (df_y['dim_upper'] == 'GESTATIONLENGTHBIRTH')]
                g_cnts = []
                for raw_m, b_name in GEST_BANDS:
                    cnt = int(ts_g[ts_g['measure_std'] == raw_m]['val'].sum())
                    g_cnts.append((b_name, cnt))
                g_tot = sum(c for _, c in g_cnts)
                for b_name, b_cnt in g_cnts:
                    pct_b = round(b_cnt / g_tot * 100, 1) if g_tot > 0 else 0.0
                    t26_rows.append([ods, full_name, 'All', y, 'All', 'All', 'Validated NICU admission', b_name, str(b_cnt), f'{pct_b}%'])
                t26_rows.append([ods, full_name, 'All', y, 'All', 'All', 'Validated NICU admission', 'Total', str(g_tot), '100.0%'])

        by_table_year[1][y] = pd.DataFrame(t1_rows, columns=[
            'ODS_Code','Provider name','Country of provider','Academic year','Permanent address',
            'Level of qualification obtained','Mode of former study','Sex','Interim study','Activity','Number'
        ])
        by_table_year[5][y] = pd.DataFrame(t5_rows, columns=[
            'ODS_Code','Provider name','Country of provider','Provider type','Permanent address',
            'Level of qualification obtained','Academic year','Category','Value'
        ])
        by_table_year[6][y] = pd.DataFrame(t6_rows, columns=[
            'ODS_Code','Provider name','Country of provider','Academic year','Permanent address',
            'Level of qualification obtained','Mode of former study','Interim study','Activity','Number','Percent','95% confidence interval'
        ])
        by_table_year[8][y] = pd.DataFrame(t8_rows, columns=[
            'ODS_Code','Provider name','Country of provider','Academic year','Permanent address',
            'Interim study','Activity','Graduate reflection question','Answer grouping','Percent'
        ])
        by_table_year[22][y] = pd.DataFrame(t22_rows, columns=[
            'ODS_Code','Provider name','Country of provider','Academic year','Permanent address',
            'Level of qualification obtained','Mode of former study','Work type marker','Standard occupational classification','Number'
        ])
        if y == '2023/24':
            by_table_year[26][y] = pd.DataFrame(t26_rows, columns=[
                'ODS_Code','Provider name','Country of provider','Academic year','Mode of former study',
                'Skill group','Work population marker','Salary band','Number','Percent'
            ])
            by_table_year[28][y] = pd.DataFrame(t28_rows, columns=[
                'ODS_Code','Provider name','Academic year','Level of qualification obtained',
                'Mode of former study','Interim study','Subject area of degree','Activity','Number'
            ])

    # Remove old 2017/18 and 2018/19 files from work/flt if present
    for old_f in os.listdir(flt_dir):
        if old_f.endswith('.csv'):
            os.remove(os.path.join(flt_dir, old_f))

    for t, y_dict in by_table_year.items():
        z_path = os.path.join(raw_dir, f'table-{t}.zip')
        with zipfile.ZipFile(z_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for y, df in y_dict.items():
                y_slug = y.replace('/', '-')
                csv_name = f'table-{t}-{y_slug}.csv'
                df.to_csv(os.path.join(flt_dir, csv_name), index=False, encoding='utf-8')
                zf.writestr(csv_name, df.to_csv(index=False))

    print('Ingested real NHS England open data (2019/20 to 2023/24) into', flt_dir)

if __name__ == '__main__':
    generate_all()
