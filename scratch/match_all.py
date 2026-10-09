
import pandas as pd
import re
import json

df_adv = pd.read_excel('Adverse outcome linelist.xlsx').dropna(how='all')
df_adv = df_adv[df_adv['Patient Name '].notna()].copy()
df_adv['MPID_clean'] = df_adv['MPID'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
df_adv['mob_clean'] = df_adv['mob num'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

df_anc = pd.read_excel('ANC_Line_list_Report_2026-09-17_09_45_52.xlsx', skiprows=8)
df_anc['MPID_clean'] = df_anc['MP ID'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
df_anc['Mobile_clean'] = df_anc['Mobile Number'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

# Drop duplicates if any in anc
df_anc_by_mp = df_anc[df_anc['MPID_clean'].notna() & ~df_anc['MPID_clean'].isin(['nan', 'Na', ''])].drop_duplicates(subset=['MPID_clean'])
df_anc_by_mob = df_anc[df_anc['Mobile_clean'].notna() & ~df_anc['Mobile_clean'].isin(['nan', 'Na', ''])].drop_duplicates(subset=['Mobile_clean'])

# Load location hierarchy
df_v = pd.read_excel('Location Hirarchy.xlsx', sheet_name='Village list', skiprows=1)

records = []
for idx, r in df_adv.iterrows():
    sr = int(r['Sr No'])
    mp = r['MPID_clean']
    mob = r['mob_clean']
    pname = str(r['Patient Name ']).strip()
    addr = str(r['Address ']).strip() if pd.notna(r['Address ']) else ''
    sc_raw = str(r['Sub centre ']).strip() if pd.notna(r['Sub centre ']) else ''
    blk_raw = str(r['Block']).strip() if pd.notna(r['Block']) else ''
    diag = str(r['Diagnosis ']).strip() if pd.notna(r['Diagnosis ']) else 'Unspecified'
    mother_st = str(r['Mother status']).strip() if pd.notna(r['Mother status']) else 'Not recorded'
    baby_st = str(r['Baby status ']).strip() if pd.notna(r['Baby status ']) else 'Not recorded'
    sncu = str(r['Transfer of baby to sncu reason ']).strip() if pd.notna(r['Transfer of baby to sncu reason ']) else 'No'
    
    # Try match with ANC
    anc_row = None
    match_type = 'None'
    if mp in df_anc_by_mp['MPID_clean'].values:
        anc_row = df_anc_by_mp[df_anc_by_mp['MPID_clean'] == mp].iloc[0]
        match_type = 'MPID'
    elif mob in df_anc_by_mob['Mobile_clean'].values:
        anc_row = df_anc_by_mob[df_anc_by_mob['Mobile_clean'] == mob].iloc[0]
        match_type = 'Mobile'
        
    records.append({
        'sr': sr, 'pname': pname, 'addr': addr, 'sc_raw': sc_raw, 'blk_raw': blk_raw,
        'diag': diag, 'mother_st': mother_st, 'baby_st': baby_st, 'sncu': sncu,
        'has_anc': anc_row is not None, 'match_type': match_type,
        'anc_block': anc_row['Health Block Name'] if anc_row is not None else None,
        'anc_sc': anc_row['Health Sub Centre Name'] if anc_row is not None else None,
        'anc_vill': anc_row['Village Name'] if anc_row is not None else None,
        'anc_anm': anc_row['Name of ANM'] if anc_row is not None else None,
        'anc_asha': anc_row['Name of ASHA'] if anc_row is not None else None,
        'anc_cho': anc_row['CHO Name'] if anc_row is not None else None,
        'anc_hrp': anc_row['HRP Identified(Yes/No)'] if anc_row is not None else None,
        'anc_pw': anc_row['Name of Pregnant Woman'] if anc_row is not None else None,
    })

print(f'Total processed: {len(records)}')
matched_count = sum(1 for x in records if x['has_anc'])
print(f'Total ANC matched: {matched_count}')
with open('scratch/matched_summary.json', 'w', encoding='utf-8') as f:
    json.dump(records, f, indent=2)
print('Saved scratch/matched_summary.json')
