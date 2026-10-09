import pandas as pd
import re
import json

df_adv = pd.read_excel('Data/Adverse outcome linelist.xlsx').dropna(how='all')
df_adv = df_adv[df_adv['Patient Name '].notna()].copy()

def clean_val(v):
    if pd.isna(v): return ''
    s = str(v).strip().replace('.0', '')
    if s.lower() in ['nan', 'none', 'null', 'direct entry']: return ''
    return s

df_adv['mp_clean'] = df_adv['MPID'].apply(clean_val)
df_adv['mob_clean'] = df_adv['mob num'].apply(clean_val)

df_anc_cache = pd.read_pickle('anc_matched_cache.pkl')
df_hrp_cache = pd.read_pickle('hrp_matched_cache.pkl')

print('--- CHECKING MATCHES FOR ALL 56 CASES ---')
matched_anc_count = 0
matched_hrp_count = 0

for idx, r in df_adv.iterrows():
    sr = r['Sr No']
    pname = r['Patient Name ']
    mp = r['mp_clean']
    mob = r['mob_clean']
    blk = r['Block']
    sc = r['Sub centre ']
    vill = r['village ']
    addr = r['Address ']
    
    anc_m = None
    anc_how = ''
    if mp and mp in df_anc_cache['MPID_clean'].values:
        anc_m = df_anc_cache[df_anc_cache['MPID_clean'] == mp].iloc[0]
        anc_how = 'MPID'
    elif mob and mob in df_anc_cache['Mobile_clean'].values:
        anc_m = df_anc_cache[df_anc_cache['Mobile_clean'] == mob].iloc[0]
        anc_how = 'Mobile'
        
    hrp_m = None
    hrp_how = ''
    if mp and mp in df_hrp_cache['MPID_clean'].values:
        hrp_m = df_hrp_cache[df_hrp_cache['MPID_clean'] == mp].iloc[0]
        hrp_how = 'MPID'
    elif mob and mob in df_hrp_cache['Mobile_clean'].values:
        hrp_m = df_hrp_cache[df_hrp_cache['Mobile_clean'] == mob].iloc[0]
        hrp_how = 'Mobile'
        
    info = f"Case #{sr}: {pname} | MPID:{mp} | Mob:{mob} | Stated: Blk={blk}, SC={sc}, Vill={vill}"
    if anc_m is not None:
        matched_anc_count += 1
        b = anc_m['Health Block Name']
        s = anc_m['Health Sub Centre Name']
        v = anc_m['Village Name']
        anm = anc_m['Name of ANM']
        cho = anc_m['CHO Name']
        asha = anc_m['Name of ASHA']
        info += f"\n   -> Matched ANC ({anc_how}): Blk={b}, SC={s}, Vill={v}, ANM={anm}, CHO={cho}, ASHA={asha}"
    if hrp_m is not None:
        matched_hrp_count += 1
        b = hrp_m['Health Block Name']
        s = hrp_m['Health Sub Centre Name']
        v = hrp_m['Village Name']
        anm = hrp_m['Name of ANM']
        cho = hrp_m['CHO Name']
        asha = hrp_m['Name of ASHA']
        info += f"\n   -> Matched HRP ({hrp_how}): Blk={b}, SC={s}, Vill={v}, ANM={anm}, CHO={cho}, ASHA={asha}"
    if anc_m is None and hrp_m is None:
        info += f"\n   -> NOT matched in ANC/HRP cache. Stated Addr: {addr}"
    print(info)

print(f"\nTotal Matched ANC: {matched_anc_count}, Total Matched HRP: {matched_hrp_count}")
