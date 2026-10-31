"""Builds dimension lookup tables (Dim_*.csv) for Power BI and the analytical validation pipeline."""
import os, pandas as pd, numpy as np, re

OUT = 'out'

def uniq(f, col):
    s = set()
    for ch in pd.read_csv(f'{OUT}/{f}.csv', usecols=[col], dtype=str, chunksize=500000, keep_default_na=False):
        s |= set(ch[col].unique())
    return s

# 24 Level 3 NICU providers
short = {
    'RR8': "Leeds Children's Hospital",
    'RHQ': 'Sheffield Jessop Wing',
    'RAE': 'Bradford Royal Infirmary',
    'RWA': 'Hull Royal Infirmary',
    'RJ1': "Evelina London (St Thomas')",
    'RRV': 'UCLH Elizabeth Garrett Anderson',
    'RJZ': "King's College Hospital",
    'RQM': 'Chelsea & Westminster Hospital',
    'RJ7': "St George's Hospital London",
    'RQX': 'Homerton University Hospital',
    'R0A': "St Mary's Hospital Manchester",
    'REP': "Liverpool Women's Hospital",
    'RXN': 'Royal Preston Hospital',
    'RTD': 'Royal Victoria Newcastle',
    'RTR': 'James Cook Middlesbrough',
    'RGT': 'Rosie Hospital Cambridge',
    'RM1': 'Norfolk & Norwich Hospital',
    'RTH': 'John Radcliffe Oxford',
    'RHM': 'Princess Anne Southampton',
    'RVJ': 'Southmead Hospital Bristol',
    'RA7': "St Michael's Hospital Bristol",
    'RQ3': "Birmingham Women's Hospital",
    'RKB': 'University Hospital Coventry',
    'RX1': "Queen's Medical Centre Nottingham",
}

raw = pd.read_csv('flt/table-1-' + os.environ.get('LATEST_YEAR', '2023/24').replace('/', '-') + '.csv', dtype=str, usecols=['ODS_Code', 'Provider name', 'Country of provider'])
odn = raw[raw['Country of provider'] != 'All'].drop_duplicates('ODS_Code').set_index('ODS_Code')['Country of provider']
full = raw.drop_duplicates('ODS_Code').set_index('ODS_Code')['Provider name']

p = pd.DataFrame({'ODS_Code': list(short)})
p['Unit'] = p.ODS_Code.map(short)
p['Trust_Full_Name'] = p.ODS_Code.map(full)
p['ODN_Region'] = p.ODS_Code.map(odn)
p['Network_Group'] = np.where(p.ODN_Region == 'Yorkshire & Humber', 'Yorkshire & Humber ODN (Level 3)', 'England Level 3 NICU')
p['Is_YH_ODN'] = (p.ODN_Region == 'Yorkshire & Humber').astype(int)
p['Unit_Sort'] = range(1, len(p) + 1)
p.to_csv(f'{OUT}/Dim_Unit.csv', index=False)

# Year
yrs = sorted(uniq('Fact_Episodes_CI', 'Year'))
pd.DataFrame({
    'Year': yrs,
    'Year_Sort': range(1, len(yrs) + 1),
    'Audit_End_Year': [int(y[:4]) + 1 for y in yrs],
    'Is_Latest': [int(y == yrs[-1]) for y in yrs],
}).to_csv(f'{OUT}/Dim_Year.csv', index=False)

# Episode Category
act = [
    ('Normothermia + deferred cord clamping', 'Normothermia and deferred cord clamping', 'Outcome'),
    ('Normothermia + immediate clamping (clinical indication)', 'Normothermia within 1h', 'Outcome'),
    ('Normothermia + cord clamping unrecorded', 'Normothermia within 1h', 'Outcome'),
    ('Normothermia + postnatal transfer within 24h', 'Normothermia within 1h', 'Outcome'),
    ('Normothermia + surgical or cardiac co-care', 'Normothermia within 1h', 'Outcome'),
    ('Admission hypothermia + deferred cord clamping', 'Deferred cord clamping', 'Outcome'),
    ('Admission hyperthermia + deferred cord clamping', 'Deferred cord clamping', 'Outcome'),
    ('Stabilisation pathway + deferred cord clamping', 'Deferred cord clamping', 'Outcome'),
    ('Out-of-range temperature without late infection', 'Other pathway', 'Outcome'),
    ('Late-onset bloodstream infection (>72h)', 'Late-onset infection', 'Outcome'),
    ('Total with validated BadgerNet records', 'Total', 'Total with validated BadgerNet records (denominator)'),
    ('Unvalidated or incomplete records', 'Total', 'Unvalidated or incomplete records'),
    ('Total admissions', 'Total', 'Total neonatal admissions surveyed'),
]
a = pd.DataFrame(act, columns=['Episode_Category', 'Pathway_Group', 'Row_Type'])
a['Category_Sort'] = range(1, len(a) + 1)
a['Is_Outcome_Category'] = (a.Row_Type == 'Outcome').astype(int)
a.to_csv(f'{OUT}/Dim_EpisodeCategory.csv', index=False)

# Discharge Nutrition
nut_map = {
    'Exclusive maternal breastmilk': ('Maternal breastmilk', 'Major group', 1),
    'Combined maternal breastmilk and fortifier': ('Maternal breastmilk', 'Major group', 2),
    'Mixed maternal breastmilk and formula': ('Maternal breastmilk', 'Major group', 3),
    'Total receiving maternal breastmilk': ('Maternal breastmilk', 'Subtotal', 4),
    'Donor human milk (banked)': ('Donor or formula', 'Major group', 5),
    'Specialist preterm formula': ('Donor or formula', 'Major group', 6),
    'Standard infant formula': ('Donor or formula', 'Major group', 7),
    'Total donor milk or formula': ('Donor or formula', 'Subtotal', 8),
    'Parenteral or non-oral nutrition at transfer': ('Complex non-oral', 'Major group', 9),
    'Gastrostomy or nasogastric tube feeding': ('Complex non-oral', 'Major group', 10),
    'Other specialist dietary management': ('Complex non-oral', 'Major group', 11),
    'Total complex non-oral nutrition': ('Complex non-oral', 'Subtotal', 12),
    'Unknown': ('Unknown', 'Unknown', 13),
    'Total': ('Total', 'Total', 14),
}
pd.DataFrame([(k,) + v for k, v in nut_map.items()], columns=['Nutrition_Group', 'Feeding_Tier', 'Row_Type', 'Nutrition_Sort']).to_csv(f'{OUT}/Dim_Nutrition.csv', index=False)

# Clinical Cohort
sub = sorted(uniq('Fact_ClinicalCohort', 'Clinical_Cohort'))
rows = []
for s in sub:
    m = re.match(r'^(\d{2}) (.*)$', s)
    if m:
        rows.append((s, m.group(1), m.group(2), 'Cohort'))
    else:
        rows.append((s, '', s, 'Total'))
d = pd.DataFrame(rows, columns=['Clinical_Cohort', 'Cohort_Code', 'Cohort_Name', 'Row_Type'])
d['Cohort_Sort'] = range(1, len(d) + 1)
d.to_csv(f'{OUT}/Dim_ClinicalCohort.csv', index=False)

# Gestation Band (11 Official NHS England GestationLengthBirth bands)
bands = [
    ('Less than 28 wks', 22, 27, 'Preterm (<37 wks)'),
    ('28 - 31 wks', 28, 31, 'Preterm (<37 wks)'),
    ('32 - 33 wks', 32, 33, 'Preterm (<37 wks)'),
    ('34 - 36 wks', 34, 36, 'Preterm (<37 wks)'),
    ('37 wks', 37, 37, 'Term (37+ wks)'),
    ('38 wks', 38, 38, 'Term (37+ wks)'),
    ('39 wks', 39, 39, 'Term (37+ wks)'),
    ('40 wks', 40, 40, 'Term (37+ wks)'),
    ('41 wks', 41, 41, 'Term (37+ wks)'),
    ('42 wks', 42, 42, 'Term (37+ wks)'),
    ('43+ wks', 43, 44, 'Term (37+ wks)'),
    ('Total', np.nan, np.nan, 'Total'),
]
sb = pd.DataFrame(bands, columns=['Gestation_Band', 'Week_Lower', 'Week_Upper', 'Maturity_Group'])
sb['Band_Sort'] = range(1, len(sb) + 1)
sb['Row_Type'] = np.where(sb.Gestation_Band == 'Total', 'Total', 'Band')
sb.to_csv(f'{OUT}/Dim_GestationBand.csv', index=False)

# Follow-up & Parent Audit Questions
q = sorted(uniq('Fact_FollowUp', 'Audit_Question'))
a_ = ['Strongly disagree', 'Disagree', 'Neither agree nor disagree', 'Agree', 'Strongly agree']
pd.DataFrame({'Audit_Question': q, 'Question_Sort': range(1, len(q) + 1)}).to_csv(f'{OUT}/Dim_AuditQuestion.csv', index=False)
pd.DataFrame({'Response_Group': a_, 'Response_Sort': range(1, 6), 'Is_Positive': [0, 0, 0, 1, 1]}).to_csv(f'{OUT}/Dim_ResponseGroup.csv', index=False)
print(p.to_string())
