import pandas as pd
import re

loc_file = 'Resources/Location Hirarchy.xlsx'
df_vill = pd.read_excel(loc_file, sheet_name='Village list', skiprows=1)
df_anm = pd.read_excel(loc_file, sheet_name='ANM', skiprows=2)
df_cho = pd.read_excel(loc_file, sheet_name='CHO', skiprows=2)
df_hr = pd.read_excel(loc_file, sheet_name='HR_Directory_15-Mar-2023_11-49-')

df_adv = pd.read_excel('Data/Adverse outcome linelist.xlsx').dropna(how='all')
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

print("=== CHECKING UNMATCHED CASES IN LOCATION HIERARCHY ===")
for idx, r in df_adv.iterrows():
    sr = r['Sr No']
    mp = r['mp_clean']
    mob = r['mob_clean']
    
    anc_match = (mp != '' and mp in df_anc['MPID_clean'].values) or (mob != '' and mob in df_anc['Mobile_clean'].values)
    hrp_match = (mp != '' and mp in df_hrp['MPID_clean'].values) or (mob != '' and mob in df_hrp['Mobile_clean'].values)
    
    if not anc_match and not hrp_match:
        addr = str(r['Address ']) if pd.notna(r['Address ']) else ''
        sc = str(r['Sub centre ']) if pd.notna(r['Sub centre ']) else ''
        blk = str(r['Block']) if pd.notna(r['Block']) else ''
        pname = r['Patient Name ']
        
        # Search in df_vill
        matched_vills = []
        for word in re.findall(r'[A-Za-z]{4,}', f"{addr} {sc} {blk}"):
            w_lower = word.lower()
            m = df_vill[df_vill['Village Name'].fillna('').str.lower().str.contains(w_lower)]
            if len(m) > 0 and len(m) < 10:
                for _, vrow in m.head(2).iterrows():
                    matched_vills.append(f"{vrow['Village Name']} ({vrow['Block Name']} - {vrow['Subcentre Name']})")
        print(f"Case #{sr} ({pname}): Addr='{addr}', SC='{sc}', Blk='{blk}' -> Village matches: {set(matched_vills)}")
