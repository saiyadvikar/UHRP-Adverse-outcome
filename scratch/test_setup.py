import pandas as pd
import numpy as np
import re
import json

loc_file = 'Resources/Location Hirarchy.xlsx'
df_vill = pd.read_excel(loc_file, sheet_name='Village list', skiprows=1)
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

def norm_str(s):
    if not s or pd.isna(s): return ''
    s = str(s).lower()
    s = re.sub(r'^(shc|phc|chc)\s+', '', s)
    s = re.sub(r'\s+new\d*$', '', s)
    s = re.sub(r'\s+new$', '', s)
    s = re.sub(r'[^a-z0-9]', '', s)
    return s

def norm_name(s):
    if not s or pd.isna(s): return ''
    s = str(s).lower()
    s = re.sub(r'\b(dr|smt|ku|ms|mr)\b', '', s)
    s = re.sub(r'[^a-z]', '', s)
    return s

df_anm['Contact_clean'] = df_anm['Contact No'].apply(clean_phone)
df_cho['Contact_clean'] = df_cho['Contact No'].apply(clean_phone)
df_hr['Contact_clean'] = df_hr['Mobile Number'].apply(clean_phone)

anm_by_sc = {}
for idx, r in df_anm.iterrows():
    k = norm_str(r['Sub-Health Facility'])
    if k and k not in anm_by_sc:
        anm_by_sc[k] = {'name': str(r['ANM Name']).strip(), 'phone': r['Contact_clean'], 'sc': str(r['Sub-Health Facility']), 'blk': str(r['Block Name'])}

cho_by_sc = {}
for idx, r in df_cho.iterrows():
    k = norm_str(r['Sub Health Facility'])
    if k and k not in cho_by_sc:
        cho_by_sc[k] = {'name': str(r['Name of CHO']).strip(), 'phone': r['Contact_clean'], 'sc': str(r['Sub Health Facility']), 'blk': str(r['Block Name'])}

anm_by_name = {}
for idx, r in df_anm.iterrows():
    k = norm_name(r['ANM Name'])
    ph = r['Contact_clean']
    if k and ph and k not in anm_by_name:
        anm_by_name[k] = {'name': str(r['ANM Name']).strip(), 'phone': ph}

cho_by_name = {}
for idx, r in df_cho.iterrows():
    k = norm_name(r['Name of CHO'])
    ph = r['Contact_clean']
    if k and ph and k not in cho_by_name:
        cho_by_name[k] = {'name': str(r['Name of CHO']).strip(), 'phone': ph}

# Load Adverse Linelist
adv_path = 'Data/Adverse outcome linelist.xlsx'
df_adv = pd.read_excel(adv_path).dropna(how='all')
df_adv = df_adv[df_adv['Patient Name '].notna()].copy()
df_anc = pd.read_pickle('anc_matched_cache.pkl')
df_hrp = pd.read_pickle('hrp_matched_cache.pkl')

def clean_val(v):
    if pd.isna(v): return ''
    s = str(v).strip().replace('.0', '')
    if s.lower() in ['nan', 'none', 'null', 'direct entry']: return ''
    return s

df_adv['mp_clean'] = df_adv['MPID'].apply(clean_val)
df_adv['mob_clean'] = df_adv['mob num'].apply(clean_val)

print("Setup completed successfully.")
