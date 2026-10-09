import pandas as pd
import re

loc_path = "Resources/Location Hirarchy.xlsx"
df_vill = pd.read_excel(loc_path, sheet_name="Village list", skiprows=1)
df_anm = pd.read_excel(loc_path, sheet_name="ANM", skiprows=2)
df_cho = pd.read_excel(loc_path, sheet_name="CHO", skiprows=2)

def clean_phone(val):
    if pd.isna(val): return ""
    s = str(val).strip().replace(".0", "")
    digits = re.sub(r"\D", "", s)
    if len(digits) >= 10:
        return digits[-10:]
    return digits if digits else ""

def norm_str(s):
    if not s or pd.isna(s): return ""
    s = str(s).lower()
    s = re.sub(r"^(shc|phc|chc)\s+", "", s)
    s = re.sub(r"\s+new\d*$", "", s)
    s = re.sub(r"\s+new$", "", s)
    s = re.sub(r"[^a-z0-9]", "", s)
    return s

df_anm["Contact_clean"] = df_anm["Contact No"].apply(clean_phone)
df_cho["Contact_clean"] = df_cho["Contact No"].apply(clean_phone)

anm_by_sc = {}
for idx, r in df_anm.iterrows():
    k = norm_str(r["Sub-Health Facility"])
    if k and k not in anm_by_sc:
        anm_by_sc[k] = {"name": str(r["ANM Name"]).strip(), "phone": r["Contact_clean"]}

cho_by_sc = {}
for idx, r in df_cho.iterrows():
    k = norm_str(r["Sub Health Facility"])
    if k and k not in cho_by_sc:
        cho_by_sc[k] = {"name": str(r["Name of CHO"]).strip(), "phone": r["Contact_clean"]}

# Test unbooked cases
df_adv = pd.read_excel("Data/Adverse outcome linelist.xlsx").dropna(how="all")
df_adv = df_adv[df_adv["Patient Name "].notna()].copy()

df_anc = pd.read_pickle("anc_matched_cache.pkl")
df_hrp = pd.read_pickle("hrp_matched_cache.pkl")

def clean_val(v):
    if pd.isna(v): return ""
    s = str(v).strip().replace(".0", "")
    if s.lower() in ["nan", "none", "null", "direct entry"]: return ""
    return s

df_adv["mp_clean"] = df_adv["MPID"].apply(clean_val)
df_adv["mob_clean"] = df_adv["mob num"].apply(clean_val)

new_hits = []
for idx, r in df_adv.iterrows():
    sr = int(r["Sr No"])
    mp = r["mp_clean"]
    mob = r["mob_clean"]
    anc_match = (mp != "" and mp in df_anc["MPID_clean"].values) or (mob != "" and mob in df_anc["Mobile_clean"].values)
    hrp_match = (mp != "" and mp in df_hrp["MPID_clean"].values) or (mob != "" and mob in df_hrp["Mobile_clean"].values)
    
    if not anc_match and not hrp_match:
        addr = str(r["Address "]) if pd.notna(r["Address "]) else ""
        sc = str(r["Sub centre "]) if pd.notna(r["Sub centre "]) else ""
        blk = str(r["Block"]) if pd.notna(r["Block"]) else ""
        combined = f"{addr} {sc} {blk}".lower()
        
        # Check special alias
        found_sc = ""
        found_vill = ""
        if "senkheda" in combined or "sinkhedi" in combined:
            found_sc = "SHC Sinkhedi New"
            found_vill = "Sengwi / Sinkhedi"
        elif "heerapur" in combined:
            found_sc = "SHC Ambakheda"
            found_vill = "Heerapur"
        else:
            for w in re.findall(r"[a-z]{4,}", combined):
                if w in ["chc", "phc", "refer", "ward", "teh", "gram", "faliya", "sanawad", "bhikangao", "jhirniya", "bhagwanpura", "khargone", "segaon", "barwah"]:
                    continue
                m = df_vill[df_vill["Village Name"].fillna("").str.lower() == w]
                if len(m) > 0:
                    found_sc = str(m.iloc[0]["Subcentre Name"])
                    found_vill = str(m.iloc[0]["Village Name"])
                    break
        
        if found_sc:
            k = norm_str(found_sc)
            anm = anm_by_sc.get(k, {})
            cho = cho_by_sc.get(k, {})
            new_hits.append({
                "sr": sr, "addr": addr, "sc": found_sc, "vill": found_vill,
                "anm": anm.get("name", ""), "anm_phone": anm.get("phone", ""),
                "cho": cho.get("name", ""), "cho_phone": cho.get("phone", "")
            })

print(f"Total newly enriched unbooked cases: {len(new_hits)}")
for h in new_hits:
    print(f"Case #{h['sr']} ({h['addr']}): SC={h['sc']} -> ANM: {h['anm']} ({h['anm_phone']}) | CHO: {h['cho']} ({h['cho_phone']})")
