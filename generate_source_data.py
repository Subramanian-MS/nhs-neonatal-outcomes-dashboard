"""Generates the deterministic raw NNAP / BadgerNet open-data tables (2017/18 to 2023/24)
for the 24 benchmarked English Level 3 Neonatal Intensive Care Units (NICUs) and packages
them into work/raw/NNAP_Extract/table-*.zip and work/flt/table-*.csv."""
import os, zipfile, io, numpy as np, pandas as pd

rng = np.random.default_rng(20240415)

# 24 NHS Level 3 NICUs (ODS Code, Short Name, Full Trust / Hospital Name, ODN Region)
UNITS = [
    ('RR8', "Leeds Children's Hospital", 'Leeds Teaching Hospitals NHS Trust (Leeds Centre for Newborn Care)', 'Yorkshire & Humber'),
    ('RHQ', 'Sheffield Jessop Wing', 'Sheffield Teaching Hospitals NHS Foundation Trust', 'Yorkshire & Humber'),
    ('RAE', 'Bradford Royal Infirmary', 'Bradford Teaching Hospitals NHS Foundation Trust', 'Yorkshire & Humber'),
    ('RWA', 'Hull Royal Infirmary', 'Hull University Teaching Hospitals NHS Trust', 'Yorkshire & Humber'),
    ('RJ1', "Evelina London (St Thomas')", "Guy's and St Thomas' NHS Foundation Trust", 'London South'),
    ('RRV', 'UCLH Elizabeth Garrett Anderson', 'University College London Hospitals NHS Foundation Trust', 'London North Central & East'),
    ('RJZ', "King's College Hospital", "King's College Hospital NHS Foundation Trust", 'London South'),
    ('RYJ', "Queen Charlotte's & Chelsea", 'Imperial College Healthcare NHS Trust', 'London North West'),
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
    ('R99', 'National Transitional Reference Unit', 'NHS Specialist Perinatal Reference Site', 'Reference'),
]

YEARS = ['2017/18', '2018/19', '2019/20', '2020/21', '2021/22', '2022/23', '2023/24']

# 10 mutually exclusive validated episode pathway categories in Table 1
# W (Normothermia within 1h, 36.5-37.5C): first 5 categories
# S (Deferred cord clamping >=1 min): category 0 + categories 5, 6, 7
# INF (Late-onset bloodstream infection >72h): category 9
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

# Unit-specific baseline profiles for 2023/24:
# (total_admissions, dq_rate, norm_rate, cord_rate, inf_rate, milk_rate, fup_rate)
PROFILES = {
    'RR8': (1085, 0.9631, 0.8571, 0.6590, 0.0369, 0.8841, 0.8800), # Leeds Children's Hospital - flagship strong performer
    'RHQ': (860,  0.9419, 0.8333, 0.6235, 0.0432, 0.8514, 0.8500), # Sheffield Jessop Wing
    'RAE': (740,  0.9257, 0.8102, 0.5985, 0.0511, 0.8125, 0.8200), # Bradford Royal Infirmary
    'RWA': (685,  0.9124, 0.7920, 0.5680, 0.0640, 0.7863, 0.7900), # Hull Royal Infirmary
    'RJ1': (1120, 0.9554, 0.8645, 0.6636, 0.0374, 0.9082, 0.8900), # Evelina London
    'RRV': (950,  0.9474, 0.8500, 0.6444, 0.0389, 0.9130, 0.8700), # UCLH
    'RJZ': (990,  0.9293, 0.8207, 0.6033, 0.0543, 0.8675, 0.8400), # King's College Hospital
    'RYJ': (910,  0.9560, 0.8678, 0.6724, 0.0345, 0.9211, 0.8800), # Queen Charlotte's & Chelsea
    'RJ7': (830,  0.9277, 0.8182, 0.6104, 0.0519, 0.8561, 0.8300), # St George's London
    'RQX': (795,  0.9371, 0.8322, 0.6309, 0.0470, 0.8768, 0.8400), # Homerton
    'R0A': (1240, 0.9355, 0.8276, 0.6164, 0.0517, 0.8286, 0.8400), # St Mary's Manchester
    'REP': (1050, 0.9429, 0.8384, 0.6313, 0.0455, 0.8118, 0.8500), # Liverpool Women's
    'RXN': (710,  0.9085, 0.7984, 0.5736, 0.0620, 0.7848, 0.8000), # Royal Preston
    'RTD': (925,  0.9514, 0.8466, 0.6420, 0.0398, 0.8481, 0.8600), # Royal Victoria Newcastle
    'RTR': (670,  0.9104, 0.7869, 0.5574, 0.0656, 0.7692, 0.7800), # James Cook Middlesbrough
    'RGT': (940,  0.9574, 0.8611, 0.6556, 0.0389, 0.9038, 0.8700), # Rosie Hospital Cambridge
    'RM1': (760,  0.9211, 0.8071, 0.5857, 0.0571, 0.8258, 0.8100), # Norfolk & Norwich
    'RTH': (980,  0.9541, 0.8556, 0.6524, 0.0374, 0.8976, 0.8700), # John Radcliffe Oxford
    'RHM': (890,  0.9382, 0.8323, 0.6228, 0.0479, 0.8590, 0.8500), # Princess Anne Southampton
    'RVJ': (875,  0.9429, 0.8424, 0.6364, 0.0424, 0.8782, 0.8600), # Southmead Bristol
    'RA7': (845,  0.9349, 0.8291, 0.6139, 0.0506, 0.8690, 0.8400), # St Michael's Bristol
    'RQ3': (1150, 0.9304, 0.8178, 0.6028, 0.0561, 0.8254, 0.8300), # Birmingham Women's
    'RKB': (775,  0.9032, 0.7786, 0.5500, 0.0714, 0.7769, 0.7900), # University Hospital Coventry
    'RX1': (965,  0.9275, 0.8212, 0.5978, 0.0559, 0.8313, 0.8300), # Queen's Medical Centre Nottingham
    'R99': (400,  0.9000, 0.8000, 0.5500, 0.0500, 0.8000, 0.8000), # Reference
}

def r5(x):
    return int(5 * round(x / 5.0))

def make_breakdown(k, norm_r, cord_r, inf_r):
    """Splits k (multiple of 5) into 10 non-negative categories (each multiple of 5) summing to k."""
    if k <= 5:
        counts = [k, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        return dict(zip(OUTCOME_CATS, counts))
    if k <= 30:
        # Compact valid split for small cohorts (k = 10, 15, 20, 25, 30)
        w_tot = max(5, min(k - 5, r5(k * norm_r)))
        rem = k - w_tot
        s1 = min(rem, 5)
        inf_cnt = rem - s1
        counts = [w_tot, 0, 0, 0, 0, s1, 0, 0, 0, inf_cnt]
        assert sum(counts) == k and min(counts) >= 0
        return dict(zip(OUTCOME_CATS, counts))
    w_tot = r5(k * norm_r)
    s_tot = r5(k * cord_r)
    inf_cnt = max(5, r5(k * inf_r))
    s_only = max(15, r5(k * (1.0 - norm_r) * 0.62))
    if w_tot + s_only + inf_cnt > k - 5:
        s_only = max(10, k - 5 - w_tot - inf_cnt)
    cat0 = max(5, min(s_tot - s_only, w_tot - 20))
    s_only = max(10, min(s_tot - cat0, k - 5 - w_tot - inf_cnt))
    w_rem = max(0, w_tot - cat0)
    w1 = r5(w_rem * 0.48)
    w2 = r5(w_rem * 0.22)
    w3 = r5(w_rem * 0.16)
    w4 = max(0, w_rem - w1 - w2 - w3)
    s1 = r5(s_only * 0.55)
    s2 = r5(s_only * 0.25)
    s3 = max(0, s_only - s1 - s2)
    oth = k - (cat0 + w1 + w2 + w3 + w4 + s1 + s2 + s3 + inf_cnt)
    if oth < 0:
        w1 = max(0, w1 + oth)
        oth = 0
    counts = [cat0, w1, w2, w3, w4, s1, s2, s3, oth, inf_cnt]
    assert sum(counts) == k and min(counts) >= 0, f"Invalid breakdown: {counts} vs {k}"
    return dict(zip(OUTCOME_CATS, counts))

# 16 Clinical Cohorts for Table 28
COHORTS = [
    ('01 Elective caesarean preterm delivery', +0.078, 0.085),
    ('02 In-utero maternal transfer to Level 3 NICU', +0.066, 0.095),
    ('03 Twin and higher-order multiple birth', +0.048, 0.075),
    ('04 Moderate preterm (32-33 weeks gestation)', +0.036, 0.110),
    ('05 Late preterm (34-36 weeks gestation)', +0.025, 0.090),
    ('06 Maternal pre-eclampsia and hypertension', +0.018, 0.065),
    ('07 Very preterm (28-31 weeks gestation)', +0.008, 0.105),
    ('08 Neonatal respiratory distress syndrome', -0.002, 0.085),
    ('09 Intrauterine growth restriction (SGA)', -0.012, 0.060),
    ('10 Term surgical and congenital anomaly', -0.024, 0.055),
    ('11 Hypoxic-ischaemic encephalopathy (cooling)', -0.035, 0.032),
    ('12 Preterm prelabour rupture of membranes', -0.046, 0.048),
    ('13 Spontaneous emergency preterm labour', -0.062, 0.042),
    ('14 Extremely preterm (24-27 weeks gestation)', -0.085, 0.028),
    ('15 Ex-utero postnatal emergency transfer', -0.108, 0.015),
    ('16 Outborn or unplanned delivery (<28 weeks)', -0.125, 0.010),
]

# 14 Gestational Age Bands for Table 26
GEST_BANDS = [
    'Less than 24 wks',
    '24 - 25 wks',
    '26 - 27 wks',
    '28 - 29 wks',
    '30 - 31 wks',
    '32 wks',
    '33 wks',
    '34 wks',
    '35 wks',
    '36 wks',
    '37 wks',
    '38 wks',
    '39 wks',
    '40+ wks',
]
# Base share across the 14 gestation bands (first 10 bands are Preterm <37 wks ~ 62%, last 4 are Term 37+ wks ~ 38%)
BASE_GEST = np.array([0.018, 0.038, 0.056, 0.078, 0.094, 0.072, 0.068, 0.066, 0.064, 0.062, 0.092, 0.108, 0.098, 0.086])
BASE_GEST = BASE_GEST / BASE_GEST.sum()

def generate_all(base_dir='.'):
    flt_dir = os.path.join(base_dir, 'work', 'flt')
    raw_dir = os.path.join(base_dir, 'work', 'raw', 'NNAP_Extract')
    os.makedirs(flt_dir, exist_ok=True)
    os.makedirs(raw_dir, exist_ok=True)

    by_table_year = {t: {} for t in [1, 5, 6, 8, 22, 26, 28]}

    for y_idx, y in enumerate(YEARS):
        # Year progression offsets (2017/18 -> 2023/24)
        # Normothermia improved slightly, deferred cord clamping rose substantially, late infection edged down/fluctuated, BadgerNet dq rose
        yr_delta_dq   = -0.052 + y_idx * 0.0087 + (0.003 if y_idx == 3 else 0)
        yr_delta_norm = -0.034 + y_idx * 0.0057 + (-0.004 if y_idx == 2 else 0)
        yr_delta_cord = -0.145 + y_idx * 0.0242
        yr_delta_inf  = +0.011 - y_idx * 0.0018 + (0.003 if y_idx == 4 else 0)
        yr_delta_milk = -0.028 + y_idx * 0.0047

        t1_rows, t5_rows, t6_rows, t8_rows, t22_rows, t26_rows, t28_rows = [], [], [], [], [], [], []

        for u_idx, (ods, short_name, full_name, odn) in enumerate(UNITS):
            base_n, base_dq, base_norm, base_cord, base_inf, base_milk, base_fup = PROFILES[ods]
            # Small deterministic unit-year ripple
            rip = ((u_idx * 7 + y_idx * 13) % 11 - 5) * 0.0012 if y_idx < 6 else 0.0
            n_tot = r5(base_n * (0.94 + 0.01 * y_idx + (((u_idx + y_idx) % 5 - 2) * 0.005 if y_idx < 6 else 0)))
            dq_r = np.clip(base_dq + yr_delta_dq + rip, 0.82, 0.985)
            k_val = r5(n_tot * dq_r)
            unval = n_tot - k_val

            norm_r = np.clip(base_norm + yr_delta_norm + rip, 0.72, 0.92)
            cord_r = np.clip(base_cord + yr_delta_cord - rip, 0.38, 0.76)
            inf_r  = np.clip(base_inf + yr_delta_inf - rip * 0.5, 0.025, 0.095)

            bk = make_breakdown(k_val, norm_r, cord_r, inf_r)

            # Headline basis rows (Exclude transitional care <4h)
            X_BASIS = 'Exclude transitional care <4h'
            I_BASIS = 'Include transitional care <4h'
            for cat, num in list(bk.items()) + [
                ('Total with validated BadgerNet records', k_val),
                ('Unvalidated or incomplete records', unval),
                ('Total admissions', n_tot),
            ]:
                t1_rows.append([ods, full_name, 'All', y, 'All', 'All', 'All', 'All', X_BASIS, cat, str(num)])
                # Also add regional metadata row for Dim_Unit lookup on latest year
                if y == '2023/24' and cat == 'Total admissions':
                    t1_rows.append([ods, full_name, odn, y, 'All', 'All', 'All', 'All', X_BASIS, cat, str(num)])

            # Include transitional care <4h basis (for Table 5 reconciliation)
            n_inc = n_tot + r5(n_tot * 0.12)
            k_inc = k_val + r5(n_tot * 0.115)
            unv_inc = n_inc - k_inc
            for cat, num in [
                ('Total with validated BadgerNet records', k_inc),
                ('Unvalidated or incomplete records', unv_inc),
                ('Total admissions', n_inc),
            ]:
                t1_rows.append([ods, full_name, 'All', y, 'All', 'All', 'All', 'All', I_BASIS, cat, str(num)])

            # Table 5: Published submission rates (on Include transitional care basis)
            pub_rate_exact = k_inc / n_inc
            pub_rate_pct = round(pub_rate_exact * 100, 1)
            comp_pct = round((pub_rate_exact - 0.018) * 100, 1)
            part_pct = round(pub_rate_pct - comp_pct, 1)
            for cat_name, val_str in [
                ('Complete first-pass BadgerNet submission rate', f'{comp_pct:.1f}%'),
                ('Post-audit query resolved rate', f'{part_pct:.1f}%'),
                ('Overall BadgerNet submission rate (all episodes)', f'{pub_rate_pct:.1f}%'),
                ('Total neonatal population', str(n_inc)),
            ]:
                t5_rows.append([ods, full_name, 'All', 'All', 'All', 'All', y, cat_name, val_str])

            # Table 6: Published whole-number percentages & 95% CI
            for cat in OUTCOME_CATS:
                num = bk[cat]
                p_whole = int(round((num / k_val) * 100))
                lo = max(0, p_whole - 2)
                hi = min(100, p_whole + 2)
                t6_rows.append([ods, full_name, 'All', y, 'All', 'All', 'All', X_BASIS, cat, str(num), f'{p_whole}%', f'({lo}%-{hi}%)'])

            # Table 22: Discharge nutrition classification
            milk_r = np.clip(base_milk + yr_delta_milk + rip, 0.72, 0.95)
            unk_n = r5(k_val * 0.04)
            kn_nut = k_val - unk_n
            high_tot = r5(kn_nut * milk_r)
            h1 = r5(high_tot * 0.56)
            h2 = r5(high_tot * 0.24)
            h3 = high_tot - h1 - h2
            rem_nut = kn_nut - high_tot
            med_tot = r5(rem_nut * 0.65)
            m1 = r5(med_tot * 0.35)
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
                ('Total', k_val),
            ]:
                t22_rows.append([ods, full_name, 'All', y, 'All', 'All', 'All', 'All', soc_cat, str(cnt)])

            # Table 8: 2-year neurodevelopmental follow-up & family care reflections
            fup_r = round(np.clip(base_fup - 0.03 + y_idx * 0.005, 0.72, 0.93), 2)
            ag1 = round(fup_r * 0.62, 2)
            ag2 = round(fup_r - ag1, 2)
            rem_f = round(1.0 - fup_r, 2)
            d1 = round(rem_f * 0.25, 2)
            d2 = round(rem_f * 0.35, 2)
            n1 = round(rem_f - d1 - d2, 2)
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
                    t8_rows.append([ods, full_name, 'All', y, 'All', X_BASIS, 'All', q_text, ans, f'{pct_v*100:.0f}%'])

            # Table 28: Clinical cohorts (16 cohorts)
            if y == '2023/24':
                for c_idx, (c_name, c_delta, c_share) in enumerate(COHORTS):
                    # Give Leeds (RR8) especially strong results across key preterm & surgical cohorts
                    leeds_boost = 0.018 if (ods == 'RR8' and c_idx in (1, 6, 9, 10, 13)) else 0.0
                    c_k = max(5, r5(k_val * c_share * (1.0 + ((u_idx + c_idx) % 5 - 2) * 0.06)))
                    # Create a few genuinely small cells (<8 suppressed -> 5, or <25 low-denominator -> 15) in smaller units for cohorts 14, 15, 16
                    if c_idx >= 13 and base_n < 800:
                        c_k = 5 if (u_idx + c_idx) % 2 == 0 else 15
                    c_norm = np.clip(norm_r + c_delta + leeds_boost + ((u_idx * 3 + c_idx) % 7 - 3) * 0.004, 0.58, 0.96)
                    c_cord = np.clip(cord_r + c_delta * 0.5, 0.35, 0.82)
                    c_inf  = np.clip(inf_r - c_delta * 0.2, 0.02, 0.12)
                    c_bk = make_breakdown(c_k, c_norm, c_cord, c_inf)
                    for cat, num in c_bk.items():
                        t28_rows.append([ods, full_name, y, 'All', 'All', X_BASIS, c_name, cat, str(num)])
                    t28_rows.append([ods, full_name, y, 'All', 'All', X_BASIS, c_name, 'Total with validated BadgerNet records', str(c_k)])
                    t28_rows.append([ods, full_name, y, 'All', 'All', X_BASIS, c_name, 'Unvalidated or incomplete records', '5'])
                    t28_rows.append([ods, full_name, y, 'All', 'All', X_BASIS, c_name, 'Total admissions', str(c_k + 5)])

            # Table 26: Gestational Age Bands (14 bands)
            if y == '2023/24':
                # Unit-specific tilt toward preterm (<37w) vs term surgical
                tilt = np.linspace((u_idx % 7 - 3) * 0.003, -(u_idx % 7 - 3) * 0.003, 14)
                if ods == 'RR8':
                    # Leeds has high tertiary preterm + specialist surgical caseload
                    tilt = np.array([0.004, 0.006, 0.008, 0.009, 0.008, 0.004, 0.002, 0.0, -0.002, -0.003, -0.008, -0.010, -0.009, -0.009])
                weights = np.clip(BASE_GEST + tilt, 0.008, 0.25)
                weights = weights / weights.sum()
                g_tot = r5(k_val * 0.92)
                g_cnts = [r5(g_tot * w) for w in weights]
                diff_g = g_tot - sum(g_cnts)
                g_cnts[6] += diff_g
                for b_name, b_cnt in zip(GEST_BANDS, g_cnts):
                    pct_b = round(b_cnt / g_tot * 100, 1)
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

    # Write filtered CSVs directly to work/flt and package raw zip
    for t, y_dict in by_table_year.items():
        z_path = os.path.join(raw_dir, f'table-{t}.zip')
        with zipfile.ZipFile(z_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for y, df in y_dict.items():
                y_slug = y.replace('/', '-')
                csv_name = f'table-{t}-{y_slug}.csv'
                # Filter out R99 when writing to flt? No, filter_rows.sh keeps the 24 units (or 25 with R99)
                df_flt = df[df['ODS_Code'] != 'R99']
                df_flt.to_csv(os.path.join(flt_dir, csv_name), index=False, encoding='utf-8')
                zf.writestr(csv_name, df.to_csv(index=False))

    print('Generated raw and filtered NNAP/BadgerNet tables in', flt_dir)

if __name__ == '__main__':
    generate_all()
