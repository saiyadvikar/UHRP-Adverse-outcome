import pandas as pd
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

# Indexes for Location Hierarchy
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

# Load Adverse, ANC, HRP
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

results = []
for idx, r in df_adv.iterrows():
    sr = int(r['Sr No'])
    pname = r['Patient Name ']
    mp = r['mp_clean']
    mob = r['mob_clean']
    
    anc_m = None
    if mp and mp in df_anc['MPID_clean'].values:
        anc_m = df_anc[df_anc['MPID_clean'] == mp].iloc[0]
    elif mob and mob in df_anc['Mobile_clean'].values:
        anc_m = df_anc[df_anc['Mobile_clean'] == mob].iloc[0]
        
    hrp_m = None
    if mp and mp in df_hrp['MPID_clean'].values:
        hrp_m = df_hrp[df_hrp['MPID_clean'] == mp].iloc[0]
    elif mob and mob in df_hrp['Mobile_clean'].values:
        hrp_m = df_hrp[df_hrp['Mobile_clean'] == mob].iloc[0]

    # Triangulate workers
    anm_name = ''
    anm_phone = ''
    cho_name = ''
    cho_phone = ''
    asha_name = ''
    matched_sc = ''
    matched_blk = ''
    matched_vill = ''
    
    # 1. From ANC / HRP
    ref_row = hrp_m if hrp_m is not None else anc_m
    if ref_row is not None:
        matched_blk = str(ref_row.get('Health Block Name', ''))
        matched_sc = str(ref_row.get('Health Sub Centre Name', ''))
        matched_vill = str(ref_row.get('Village Name', ''))
        raw_anm = str(ref_row.get('Name of ANM', '')).strip()
        raw_cho = str(ref_row.get('CHO Name', '')).strip()
        raw_asha = str(ref_row.get('Name of ASHA', '')).strip()
        
        if raw_anm and raw_anm.lower() not in ['nan', 'none', 'null', '']:
            anm_name = raw_anm
        if raw_cho and raw_cho.lower() not in ['nan', 'none', 'null', '']:
            cho_name = raw_cho
        if raw_asha and raw_asha.lower() not in ['nan', 'none', 'null', '']:
            asha_name = raw_asha

    # 2. Enrich from Location Hierarchy by Subcentre
    sc_key = norm_str(matched_sc)
    if sc_key:
        if sc_key in anm_by_sc:
            if not anm_name: anm_name = anm_by_sc[sc_key]['name']
            if not anm_phone: anm_phone = anm_by_sc[sc_key]['phone']
        if sc_key in cho_by_sc:
            if not cho_name: cho_name = cho_by_sc[sc_key]['name']
            if not cho_phone: cho_phone = cho_by_sc[sc_key]['phone']

    # 3. Enrich contact numbers by Name if still missing
    if anm_name and not anm_phone:
        nk = norm_name(anm_name)
        if nk in anm_by_name:
            anm_phone = anm_by_name[nk]['phone']
    if cho_name and not cho_phone:
        nk = norm_name(cho_name)
        if nk in cho_by_name:
            cho_phone = cho_by_name[nk]['phone']

    # If unbooked, try matching stated village in Location Hierarchy
    if not matched_sc:
        addr = str(r['Address ']) if pd.notna(r['Address ']) else ''
        sc_stated = str(r['Sub centre ']) if pd.notna(r['Sub centre ']) else ''
        blk_stated = str(r['Block']) if pd.notna(r['Block']) else ''
        combined = f"{addr} {sc_stated} {blk_stated}"
        
        # Check Village list
        for word in re.findall(r'[A-Za-z]{4,}', combined):
            w_lower = word.lower()
            m = df_vill[df_vill['Village Name'].fillna('').str.lower() == w_lower]
            if len(m) > 0:
                vrow = m.iloc[0]
                matched_vill = str(vrow['Village Name'])
                matched_sc = str(vrow['Subcentre Name'])
                matched_blk = str(vrow['Block Name'])
                
                # Check workers for this subcentre
                sck = norm_str(matched_sc)
                if sck in anm_by_sc:
                    anm_name = anm_by_sc[sck]['name']
                    anm_phone = anm_by_sc[sck]['phone']
                if sck in cho_by_sc:
                    cho_name = cho_by_sc[sck]['name']
                    cho_phone = cho_by_sc[sck]['phone']
                break

    # Build formatted frontline workers string
    parts = []
    if anm_name:
        parts.append(f"ANM: {anm_name}" + (f" ({anm_phone})" if anm_phone else ""))
    if cho_name:
        parts.append(f"CHO: {cho_name}" + (f" ({cho_phone})" if cho_phone else ""))
    if asha_name:
        parts.append(f"ASHA: {asha_name}")
        
    worker_str = " | ".join(parts) if parts else "Unrecorded / Direct DH Case"
    
    results.append({
        'sr': sr, 'pname': pname, 'matched_blk': matched_blk, 'matched_sc': matched_sc,
        'matched_vill': matched_vill, 'anm_name': anm_name, 'anm_phone': anm_phone,
        'cho_name': cho_name, 'cho_phone': cho_phone, 'asha_name': asha_name,
        'worker_str': worker_str
    })

print(f"Enriched {len(results)} cases.")
for item in results[:15]:
    print(f"#{item['sr']}: Blk='{item['matched_blk']}', SC='{item['matched_sc']}' -> {item['worker_str']}")
