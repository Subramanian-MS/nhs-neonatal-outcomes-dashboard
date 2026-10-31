"""Builds native NHS dimension lookup tables (Dim_*.csv) for Power BI and the analytical validation pipeline."""
import os, pandas as pd, numpy as np

OUT = 'out'
os.makedirs(OUT, exist_ok=True)

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

# 1. Dim_Unit.csv
p = pd.DataFrame(UNITS, columns=['ODS_Code', 'Unit', 'Trust_Full_Name', 'ODN_Region'])
p['Network_Group'] = np.where(p.ODN_Region == 'Yorkshire & Humber', 'Yorkshire & Humber ODN (Level 3)', 'England Level 3 NICU')
p['Is_YH_ODN'] = (p.ODN_Region == 'Yorkshire & Humber').astype(int)
p['Unit_Sort'] = range(1, len(p) + 1)
p.to_csv(f'{OUT}/Dim_Unit.csv', index=False)

# 2. Dim_Year.csv
yrs = ['2019/20', '2020/21', '2021/22', '2022/23', '2023/24']
pd.DataFrame({
    'Year': yrs,
    'Year_Sort': range(1, len(yrs) + 1),
    'Audit_End_Year': [int(y[:4]) + 1 for y in yrs],
    'Is_Latest': [int(y == yrs[-1]) for y in yrs],
}).to_csv(f'{OUT}/Dim_Year.csv', index=False)

# 3. Dim_ClinicalIndicator.csv
indicators = [
    ('SkinToSkinContact1HourTerm', '1-hr skin-to-skin', 'Yes', 'Yes + No', 'Higher is better', 1),
    ('GestAgeFormalAntenatalBookingGroup', 'Early booking (<=10w)', '0 to 70 days', 'All known booking gestation groups', 'Higher is better', 2),
    ('ApgarScore5TermGroup7', 'Low 5-min Apgar (<7)', '0 to 6', '0 to 6 + 7 to 10', 'Lower is better', 3),
    ('BabyFirstFeedBreastMilkStatus', 'Breastmilk first feed', 'Maternal or Donor Breast Milk', 'Maternal or Donor Breast Milk + Not Breast Milk', 'Higher is better', 4),
]
pd.DataFrame(indicators, columns=['Indicator', 'Display_Name', 'Numerator_Rule', 'Denominator_Rule', 'Direction', 'Indicator_Sort']).to_csv(f'{OUT}/Dim_ClinicalIndicator.csv', index=False)

# 4. Dim_MSDSDataItem.csv (16 benchmarked MSDS v2 baby & neonatal data items)
dq_items = [
    ('M401070', 'MSD401', 'NHS number (baby)', 1),
    ('M401150', 'MSD401', 'Delivery method code', 2),
    ('M401060', 'MSD401', 'Ethnic category (baby)', 3),
    ('M405120', 'MSD405', 'Coded clinical observation value', 4),
    ('M401130', 'MSD401', 'Fetal presentation at delivery', 5),
    ('M401120', 'MSD401', 'Neonatal death time recorded', 6),
    ('M401220', 'MSD401', 'Skin-to-skin contact (1h) indicator', 7),
    ('M401050', 'MSD401', 'Phenotypic sex (baby)', 8),
    ('M401170', 'MSD401', 'Place of birth site identifier', 9),
    ('M405909', 'MSD405', 'Care professional ID (baby activity)', 10),
    ('M401210', 'MSD401', 'First feed breastmilk indicator', 11),
    ('M401160', 'MSD401', 'Delivered in water indicator', 12),
    ('M401909', 'MSD401', 'Care professional ID (delivery)', 13),
    ('M402040', 'MSD402', 'Neonatal critical care admission flag', 14),
    ('M401190', 'MSD401', 'Baby first feed date & time', 15),
    ('M402030', 'MSD402', 'Admitting neonatal unit site ID', 16),
]
pd.DataFrame(dq_items, columns=['UID', 'DataTable', 'Item_Label', 'Item_Sort']).to_csv(f'{OUT}/Dim_MSDSDataItem.csv', index=False)

# 5. Dim_GestationBand.csv (11 Official NHS England GestationLengthBirth bands)
bands = [
    ('Less than 28 wks', '27 weeks and under', 22, 27, 'Preterm (<37 wks)'),
    ('28 - 31 wks', '28 to 31 weeks', 28, 31, 'Preterm (<37 wks)'),
    ('32 - 33 wks', '32 to 33 weeks', 32, 33, 'Preterm (<37 wks)'),
    ('34 - 36 wks', '34 to 36 weeks', 34, 36, 'Preterm (<37 wks)'),
    ('37 wks', '37 weeks', 37, 37, 'Term (37+ wks)'),
    ('38 wks', '38 weeks', 38, 38, 'Term (37+ wks)'),
    ('39 wks', '39 weeks', 39, 39, 'Term (37+ wks)'),
    ('40 wks', '40 weeks', 40, 40, 'Term (37+ wks)'),
    ('41 wks', '41 weeks', 41, 41, 'Term (37+ wks)'),
    ('42 wks', '42 weeks', 42, 42, 'Term (37+ wks)'),
    ('43+ wks', '43 weeks and over', 43, 44, 'Term (37+ wks)'),
    ('Total', 'Total known gestation at birth', np.nan, np.nan, 'Total'),
]
sb = pd.DataFrame(bands, columns=['Gestation_Band', 'Raw_Measure', 'Week_Lower', 'Week_Upper', 'Maturity_Group'])
sb['Band_Sort'] = range(1, len(sb) + 1)
sb['Row_Type'] = np.where(sb.Gestation_Band == 'Total', 'Total', 'Band')
sb.to_csv(f'{OUT}/Dim_GestationBand.csv', index=False)

# 6. Dim_FeedingCategory.csv
feed_cats = [
    ('Maternal or Donor Breast Milk', 'Breastmilk', 'Outcome', 1),
    ('Not Breast Milk', 'Non-breastmilk', 'Outcome', 2),
    ('Missing Value / Value outside reporting parameters', 'Missing', 'Unknown', 3),
    ('Total Known', 'Subtotal', 'Subtotal', 4),
    ('Total', 'Total', 'Total', 5),
]
pd.DataFrame(feed_cats, columns=['Feeding_Category', 'Feeding_Group', 'Row_Type', 'Feeding_Sort']).to_csv(f'{OUT}/Dim_FeedingCategory.csv', index=False)
print('Built native NHS dimension tables in out/')
