import pandas as pd
import re

loc_file = 'Resources/Location Hirarchy.xlsx'
df_anm = pd.read_excel(loc_file, sheet_name='ANM', skiprows=2)
df_cho = pd.read_excel(loc_file, sheet_name='CHO', skiprows=2)
df_hr = pd.read_excel(loc_file, sheet_name='HR_Directory_15-Mar-2023_11-49-')

def clean_phone(val):
    if pd.isna(val): return ''
    s = str(val).strip().replace('.0', '')
    digits = re.sub(r'\D', '', s)
    if len(digits) >= 10:
        return digits[-10:]
    return digits if digits else ''

def norm_name(val):
    if not val or pd.isna(val): return ''
    s = str(val).lower()
    s = re.sub(r'\b(dr|smt|ku|ms|mr)\b', '', s)
    s = re.sub(r'[^a-z]', '', s)
    return s

anm_by_name = {}
for idx, r in df_anm.iterrows():
    n = norm_name(r['ANM Name'])
    ph = clean_phone(r['Contact No'])
    if n and ph and n not in anm_by_name:
        anm_by_name[n] = {'name': str(r['ANM Name']).strip(), 'phone': ph, 'sc': str(r['Sub-Health Facility']), 'block': str(r['Block Name'])}

cho_by_name = {}
for idx, r in df_cho.iterrows():
    n = norm_name(r['Name of CHO'])
    ph = clean_phone(r['Contact No'])
    if n and ph and n not in cho_by_name:
        cho_by_name[n] = {'name': str(r['Name of CHO']).strip(), 'phone': ph, 'sc': str(r['Sub Health Facility']), 'block': str(r['Block Name'])}

print("ANM by name count:", len(anm_by_name))
print("CHO by name count:", len(cho_by_name))
