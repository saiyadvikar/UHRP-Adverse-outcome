import pandas as pd
import re

adv_path = 'Data/Adverse outcome linelist.xlsx'
df_adv = pd.read_excel(adv_path).dropna(how='all')
df_adv = df_adv[df_adv['Patient Name '].notna()].copy()

def clean_val(v):
    if pd.isna(v): return ''
    s = str(v).strip().replace('.0', '')
    if s.lower() in ['nan', 'none', 'null', 'direct entry']: return ''
    return s

adv_mp = set(df_adv['MPID'].apply(clean_val).loc[lambda x: x != ''])
adv_mob = set(df_adv['mob num'].apply(clean_val).loc[lambda x: x != ''])

print(f"Adverse MPIDs count: {len(adv_mp)}")
print(f"Adverse Mobile count: {len(adv_mob)}")

# Check against full ANC file
print("Loading full ANC file...")
df_anc = pd.read_excel('Data/ANC_Line_list_Report_2026-09-17_09_45_52.xlsx', skiprows=8)
df_anc['mp_c'] = df_anc['MP ID'].apply(clean_val)
df_anc['mob_c'] = df_anc['Mobile Number'].apply(clean_val)

anc_mp_matches = set(df_anc['mp_c']).intersection(adv_mp)
anc_mob_matches = set(df_anc['mob_c']).intersection(adv_mob)

print(f"Matched MPIDs in full ANC: {len(anc_mp_matches)}")
print(f"Matched Mobiles in full ANC: {len(anc_mob_matches)}")

# Check against full HRP file
print("Loading full HRP file...")
df_hrp = pd.read_excel('Data/HRP_Line_List_Report_2026-09-17_10_22_24.xlsx')
df_hrp['mp_c'] = df_hrp['MP ID'].apply(clean_val)
df_hrp['mob_c'] = df_hrp['Mobile Number'].apply(clean_val)

hrp_mp_matches = set(df_hrp['mp_c']).intersection(adv_mp)
hrp_mob_matches = set(df_hrp['mob_c']).intersection(adv_mob)

print(f"Matched MPIDs in full HRP: {len(hrp_mp_matches)}")
print(f"Matched Mobiles in full HRP: {len(hrp_mob_matches)}")
