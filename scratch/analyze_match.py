
import pandas as pd
import re
import sys

df_adv = pd.read_excel('Adverse outcome linelist.xlsx').dropna(how='all')
df_adv = df_adv[df_adv['Patient Name '].notna()].copy()
df_v = pd.read_excel('Location Hirarchy.xlsx', sheet_name='Village list', skiprows=1)

df_v['Village_clean'] = df_v['Village Name'].astype(str).str.lower().str.strip()
df_v['SC_clean'] = df_v['Subcentre Name'].astype(str).str.lower().str.strip()
df_v['Fac_clean'] = df_v['Facility Name'].astype(str).str.lower().str.strip()
df_v['Block_clean'] = df_v['Block Name'].astype(str).str.lower().str.strip()

print(f'Total adverse rows: {len(df_adv)}')
for idx, r in df_adv.iterrows():
    sr = int(r['Sr No'])
    name = str(r['Patient Name '])
    addr = str(r['Address ']).strip() if pd.notna(r['Address ']) else ''
    sc = str(r['Sub centre ']).strip() if pd.notna(r['Sub centre ']) else ''
    blk = str(r['Block']).strip() if pd.notna(r['Block']) else ''
    diag = str(r['Diagnosis ']).strip() if pd.notna(r['Diagnosis ']) else ''
    
    # Check for external districts
    ext = None
    lower_all = (addr + ' ' + sc + ' ' + blk).lower()
    if 'sendhwa' in lower_all or 'shendhwa' in lower_all:
        ext = 'Sendhwa (Barwani District)'
    elif 'thikri' in lower_all:
        ext = 'Thikri (Barwani District)'
    elif 'rajpur' in lower_all:
        ext = 'Rajpur (Barwani District)'
    elif 'nepanagar' in lower_all or 'dahinala' in lower_all:
        ext = 'Nepanagar (Burhanpur District)'
    elif 'punasala' in lower_all or 'punasa' in lower_all or 'ichapur' in lower_all:
        ext = 'Punasa (Khandwa District)'
    elif 'dharampuri' in lower_all:
        ext = 'Dharampuri (Dhar District)'
    elif 'jalgaon' in lower_all or 'maharashtra' in lower_all:
        ext = 'Jalgaon (Maharashtra)'
        
    print(f'Case #{sr:02d} | {name:20s} | Stated Blk: {blk:12s} | Ext?: {str(ext):28s} | Addr: {addr:25s} | SC: {sc}')
