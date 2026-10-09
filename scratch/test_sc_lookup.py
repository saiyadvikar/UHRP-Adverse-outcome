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

def norm_sc(name):
    if not name or pd.isna(name): return ''
    s = str(name).lower()
    s = re.sub(r'^(shc|phc|chc)\s+', '', s)
    s = re.sub(r'\s+new\d*$', '', s)
    s = re.sub(r'\s+new$', '', s)
    s = re.sub(r'[^a-z0-9]', '', s)
    return s

# Clean contact numbers
df_anm['Contact_clean'] = df_anm['Contact No'].apply(clean_phone)
df_cho['Contact_clean'] = df_cho['Contact No'].apply(clean_phone)
df_hr['Contact_clean'] = df_hr['Mobile Number'].apply(clean_phone)

# Create lookup dicts
# Try key by normalized subcentre name
anm_by_sc = {}
for idx, r in df_anm.iterrows():
    sc = str(r['Sub-Health Facility'])
    k = norm_sc(sc)
    if k and k not in anm_by_sc:
        anm_by_sc[k] = {'name': str(r['ANM Name']).strip(), 'phone': r['Contact_clean'], 'orig_sc': sc, 'block': str(r['Block Name'])}

cho_by_sc = {}
for idx, r in df_cho.iterrows():
    sc = str(r['Sub Health Facility'])
    k = norm_sc(sc)
    if k and k not in cho_by_sc:
        cho_by_sc[k] = {'name': str(r['Name of CHO']).strip(), 'phone': r['Contact_clean'], 'orig_sc': sc, 'block': str(r['Block Name'])}

hr_by_sc = {}
for idx, r in df_hr.iterrows():
    fn = str(r['Facility Name'])
    k = norm_sc(fn)
    if k and k not in hr_by_sc:
        hr_by_sc[k] = {'name': str(r['HR Name']).strip(), 'designation': str(r['Designation']).strip(), 'phone': r['Contact_clean'], 'orig_fac': fn}

print(f"Total ANM mapped subcentres: {len(anm_by_sc)}")
print(f"Total CHO mapped subcentres: {len(cho_by_sc)}")
print(f"Total HR directory mapped facilities: {len(hr_by_sc)}")

# Test looking up sample subcentres from ANC/HRP
test_scs = ['SHC Satajana', 'SHC Balgaon', 'SHC Abhapuri', 'SHC Sirlay', 'SHC Panali', 'SHC Mundiya', 'SHC Achhalwadi', 'SHC Atarsumba New', 'SHC Neelkanth New']
for t in test_scs:
    k = norm_sc(t)
    anm = anm_by_sc.get(k, None)
    cho = cho_by_sc.get(k, None)
    hr = hr_by_sc.get(k, None)
    print(f"\nTarget: {t} (key: {k}):")
    print(f"  ANM: {anm}")
    print(f"  CHO: {cho}")
    print(f"  HR:  {hr}")
