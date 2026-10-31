"""Downloads (if not already cached) and filters the official NHS England Maternity Services Data Set
(MSDS) and Data Quality CSV releases (2019/20 to 2023/24) from work/real_nhs/ to the 24 English
Level 3 Neonatal Intensive Care Unit (NICU) Trusts, writing native NHS filtered tables to work/flt/."""
import os, urllib.request, pandas as pd

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

def ensure_real_nhs_files(real_dir):
    os.makedirs(real_dir, exist_ok=True)
    for fname, url in OFFICIAL_NHS_URLS.items():
        fpath = os.path.join(real_dir, fname)
        if not os.path.exists(fpath) or os.path.getsize(fpath) == 0:
            print(f'Downloading {fname} from {url} ...')
            urllib.request.urlretrieve(url, fpath)

def generate_all(base_dir='.'):
    real_dir = os.path.join(base_dir, 'work', 'real_nhs')
    flt_dir = os.path.join(base_dir, 'work', 'flt')
    os.makedirs(flt_dir, exist_ok=True)
    ensure_real_nhs_files(real_dir)

    # Clear old files in work/flt
    for old_f in os.listdir(flt_dir):
        if old_f.endswith('.csv'):
            os.remove(os.path.join(flt_dir, old_f))

    ods_set = {u[0] for u in UNITS}
    trust_map = {u[0]: u[2] for u in UNITS}
    odn_map = {u[0]: u[3] for u in UNITS}

    for y in YEARS:
        ys = y.replace('/', '_')
        y_slug = y.replace('/', '-')

        # 1. Filter msds_{ys}.csv to the 24 Level 3 NICU Trusts
        df = pd.read_csv(os.path.join(real_dir, f'msds_{ys}.csv'), dtype=str, keep_default_na=False)
        col_map = {c.lower(): c for c in df.columns}
        ocol = col_map['org_code']
        dcol = col_map['dimension']
        mcol = col_map.get('measure1') or col_map.get('measure')
        ccol = col_map['count_of']
        vcol = col_map['value']

        sub = df[df[ocol].str.strip().isin(ods_set)].copy()
        out_msds = pd.DataFrame({
            'ODS_Code': sub[ocol].str.strip(),
            'Trust_Name': sub[ocol].str.strip().map(trust_map),
            'ODN_Region': sub[ocol].str.strip().map(odn_map),
            'Year': y,
            'Dimension': sub[dcol].str.strip(),
            'Measure': sub[mcol].str.strip(),
            'Count_Of': sub[ccol].str.strip(),
            'Value': sub[vcol].str.strip(),
        })
        out_msds.to_csv(os.path.join(flt_dir, f'msds-{y_slug}.csv'), index=False, encoding='utf-8')

        # 2. Filter msds_dq_{ys}.csv to the 24 Level 3 NICU Trusts
        dq = pd.read_csv(os.path.join(real_dir, f'msds_dq_{ys}.csv'), dtype=str, keep_default_na=False)
        dq.columns = [c.strip() for c in dq.columns]
        dq_sub = dq[dq['Org_Code'].str.strip().isin(ods_set)].copy()
        out_dq = pd.DataFrame({
            'ODS_Code': dq_sub['Org_Code'].str.strip(),
            'Trust_Name': dq_sub['Org_Code'].str.strip().map(trust_map),
            'ODN_Region': dq_sub['Org_Code'].str.strip().map(odn_map),
            'Year': y,
            'DataTable': dq_sub['DataTable'].str.strip(),
            'UID': dq_sub['UID'].str.strip(),
            'DataItem': dq_sub['DataItem'].str.strip(),
            'Valid': dq_sub['Valid'].str.strip(),
            'Default': dq_sub['Default'].str.strip(),
            'Invalid': dq_sub['Invalid'].str.strip(),
            'Missing': dq_sub['Missing'].str.strip(),
            'Denominator': dq_sub['Denominator'].str.strip(),
        })
        out_dq.to_csv(os.path.join(flt_dir, f'msds-dq-{y_slug}.csv'), index=False, encoding='utf-8')

    print('Filtered official NHS England MSDS & Data Quality CSVs (2019/20 to 2023/24) to 24 NICU Trusts in', flt_dir)

if __name__ == '__main__':
    import sys
    base = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    generate_all(base)
