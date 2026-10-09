"""
Generate_Dashboard.py
=====================
Master Automated Pipeline for DH Khargone Adverse Outcome Feedback System.

Features:
1. Dynamic input file detection (Data/ or root directory).
2. Auto-indexing and caching of full ANC & HRP registries (16,000+ records).
3. Whitespace-tolerant column mapping and smart empty-row filtering.
4. Triangulation of village/subcentre/block with Location Hierarchy and Frontline Workers (ANM, CHO, ASHA).
5. Clinical categorization and Perinatal/Maternal outcome normalization.
6. Generation of `bmo_dashboard_data.json`.
7. Direct HTML embedding into `BMO_Adverse_Outcome_Dashboard.html` so the dashboard is ALWAYS up-to-date.
8. Auto-execution of `generate_styled_excel.py` for multi-tab styled Excel reports.
"""

import os
import sys
import json
import re
import glob
import pickle
import time
import subprocess
import pandas as pd
import numpy as np

print("=" * 60)
print("  DH KHARGONE - ADVERSE OUTCOME FEEDBACK GENERATOR")
print("=" * 60)

BASE = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────────────────────────────────────
# 0. HELPER UTILITIES
# ─────────────────────────────────────────────────────────────
def clean_val(v):
    if pd.isna(v): return ""
    s = str(v).strip().replace(".0", "")
    if s.lower() in ["nan", "none", "null", "direct entry", "na"]: return ""
    return s

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

def norm_name(s):
    if not s or pd.isna(s): return ""
    s = str(s).lower()
    s = re.sub(r"\b(dr|smt|ku|ms|mr)\b", "", s)
    s = re.sub(r"[^a-z]", "", s)
    return s

def clean_village(v):
    if not v or pd.isna(v): return ""
    s = str(v).strip()
    s = re.sub(r"\s*\([^)]*\)\*?", "", s).strip()
    return s

def find_file(patterns):
    for pat in patterns:
        matches = glob.glob(os.path.join(BASE, pat))
        if matches:
            return matches[0]
    return None

# ─────────────────────────────────────────────────────────────
# 1. LOAD & NORMALIZE ADVERSE OUTCOME LINELIST
# ─────────────────────────────────────────────────────────────
adv_path = find_file(["Data/*Adverse*.xlsx", "*Adverse*.xlsx", "Data/Adverse outcome linelist.xlsx"])
if not adv_path:
    print("ERROR: Could not find Adverse outcome linelist Excel file in Data/ or current folder!")
    sys.exit(1)

print(f"\n[1/5] Loading Adverse Outcome Linelist from: {os.path.basename(adv_path)}")
df_raw = pd.read_excel(adv_path).dropna(how="all")

# Normalize column names for flexible matching
col_map = {}
for c in df_raw.columns:
    clean_c = re.sub(r"\s+", " ", str(c)).strip().lower()
    if "sr" in clean_c and "no" in clean_c:
        col_map[c] = "Sr No"
    elif "mp" in clean_c and "id" in clean_c:
        col_map[c] = "MPID"
    elif "admission" in clean_c and "date" in clean_c:
        col_map[c] = "Admission date"
    elif "patient" in clean_c and "name" in clean_c:
        col_map[c] = "Patient Name"
    elif "address" in clean_c:
        col_map[c] = "Address"
    elif "vill" in clean_c:
        col_map[c] = "village"
    elif "sub" in clean_c and "centre" in clean_c:
        col_map[c] = "Sub centre"
    elif clean_c == "block":
        col_map[c] = "Block"
    elif "diagnos" in clean_c:
        col_map[c] = "Diagnosis"
    elif "mother" in clean_c and "status" in clean_c:
        col_map[c] = "Mother status"
    elif "baby" in clean_c and "status" in clean_c:
        col_map[c] = "Baby status"
    elif "sncu" in clean_c:
        col_map[c] = "Transfer of baby to sncu reason"
    elif "mob" in clean_c or "phone" in clean_c or "contact" in clean_c:
        col_map[c] = "mob num"

df_adv = df_raw.rename(columns=col_map).copy()

# Filter valid rows (must have Patient Name or Diagnosis or Address)
pname_col = "Patient Name" if "Patient Name" in df_adv.columns else df_adv.columns[3]
df_adv = df_adv[df_adv[pname_col].fillna("").astype(str).str.strip().ne("")].copy()
df_adv["Sr No"] = range(1, len(df_adv) + 1)

df_adv["mp_clean"] = df_adv.get("MPID", pd.Series([""] * len(df_adv))).apply(clean_val)
df_adv["mob_clean"] = df_adv.get("mob num", pd.Series([""] * len(df_adv))).apply(clean_phone)

# Parse Admission Date & Month
def parse_adm_dates(row):
    d = row.get("Admission date")
    if pd.notna(d) and str(d).strip() not in ["", "NaT", "nan"]:
        try:
            dt = pd.to_datetime(d)
            return dt.strftime("%Y-%m-%d"), dt.strftime("%B %Y")
        except Exception:
            pass
    return "2026-08-01", "August 2026"

df_adv[["adm_date", "adm_month"]] = df_adv.apply(parse_adm_dates, axis=1, result_type="expand")
print(f"  Processed {len(df_adv)} active adverse outcome records.")

# ─────────────────────────────────────────────────────────────
# 2. LOAD LOCATION HIERARCHY
# ─────────────────────────────────────────────────────────────
loc_path = find_file(["Resources/Location Hirarchy.xlsx", "Resources/Location*.xlsx", "Location Hirarchy.xlsx"])
if not loc_path:
    print("ERROR: Could not find Location Hirarchy.xlsx in Resources/ or current folder!")
    sys.exit(1)

print(f"\n[2/5] Loading Location Hierarchy from: {os.path.basename(loc_path)}")
xl_loc = pd.ExcelFile(loc_path)
df_vill = xl_loc.parse("Village list", skiprows=1)
df_anm = xl_loc.parse("ANM", skiprows=2)
df_cho = xl_loc.parse("CHO", skiprows=2)

df_anm["Contact_clean"] = df_anm["Contact No"].apply(clean_phone)
df_cho["Contact_clean"] = df_cho["Contact No"].apply(clean_phone)

anm_by_sc = {}
for _, r in df_anm.iterrows():
    k = norm_str(r.get("Sub-Health Facility"))
    if k and k not in anm_by_sc:
        anm_by_sc[k] = {"name": str(r.get("ANM Name", "")).strip(), "phone": r["Contact_clean"], "sc": str(r.get("Sub-Health Facility", "")), "blk": str(r.get("Block Name", ""))}

cho_by_sc = {}
for _, r in df_cho.iterrows():
    k = norm_str(r.get("Sub Health Facility"))
    if k and k not in cho_by_sc:
        cho_by_sc[k] = {"name": str(r.get("Name of CHO", "")).strip(), "phone": r["Contact_clean"], "sc": str(r.get("Sub Health Facility", "")), "blk": str(r.get("Block Name", ""))}

anm_by_name = {}
for _, r in df_anm.iterrows():
    k = norm_name(r.get("ANM Name"))
    ph = r["Contact_clean"]
    if k and ph and k not in anm_by_name:
        anm_by_name[k] = {"name": str(r.get("ANM Name", "")).strip(), "phone": ph}

cho_by_name = {}
for _, r in df_cho.iterrows():
    k = norm_name(r.get("Name of CHO"))
    ph = r["Contact_clean"]
    if k and ph and k not in cho_by_name:
        cho_by_name[k] = {"name": str(r.get("Name of CHO", "")).strip(), "phone": ph}

# ─────────────────────────────────────────────────────────────
# 3. LOAD OR BUILD FULL ANC & HRP REGISTRY CACHES
# ─────────────────────────────────────────────────────────────
anc_file = find_file(["Data/ANC_Line_list*.xlsx", "ANC_Line_list*.xlsx"])
hrp_file = find_file(["Data/HRP_Line_List*.xlsx", "HRP_Line_List*.xlsx"])
lookup_cache_path = os.path.join(BASE, "registry_lookups.pkl")

rebuild_cache = False
if not os.path.exists(lookup_cache_path):
    rebuild_cache = True
else:
    cache_mtime = os.path.getmtime(lookup_cache_path)
    if anc_file and os.path.getmtime(anc_file) > cache_mtime: rebuild_cache = True
    if hrp_file and os.path.getmtime(hrp_file) > cache_mtime: rebuild_cache = True

if rebuild_cache and anc_file and hrp_file:
    print("\n[3/5] Building fast registry lookups from full ANC & HRP files (one-time index)...")
    t0 = time.time()
    df_anc_full = pd.read_excel(anc_file, skiprows=8)
    df_anc_full["MPID_clean"] = df_anc_full["MP ID"].apply(clean_val)
    df_anc_full["Mobile_clean"] = df_anc_full["Mobile Number"].apply(clean_phone)
    anc_by_mp = df_anc_full[df_anc_full["MPID_clean"] != ""].drop_duplicates(subset=["MPID_clean"]).set_index("MPID_clean").to_dict(orient="index")
    anc_by_mob = df_anc_full[df_anc_full["Mobile_clean"] != ""].drop_duplicates(subset=["Mobile_clean"]).set_index("Mobile_clean").to_dict(orient="index")

    df_hrp_full = pd.read_excel(hrp_file, skiprows=7)
    df_hrp_full["MPID_clean"] = df_hrp_full["MP ID"].apply(clean_val)
    df_hrp_full["Mobile_clean"] = df_hrp_full["Mobile Number"].apply(clean_phone)
    hrp_by_mp = df_hrp_full[df_hrp_full["MPID_clean"] != ""].drop_duplicates(subset=["MPID_clean"]).set_index("MPID_clean").to_dict(orient="index")
    hrp_by_mob = df_hrp_full[df_hrp_full["Mobile_clean"] != ""].drop_duplicates(subset=["Mobile_clean"]).set_index("Mobile_clean").to_dict(orient="index")

    with open(lookup_cache_path, "wb") as f:
        pickle.dump({
            "anc_by_mp": anc_by_mp, "anc_by_mob": anc_by_mob,
            "hrp_by_mp": hrp_by_mp, "hrp_by_mob": hrp_by_mob
        }, f)
    print(f"  Indexed & cached in {time.time()-t0:.2f}s ({len(anc_by_mp)} ANC, {len(hrp_by_mp)} HRP).")
elif os.path.exists(lookup_cache_path):
    print("\n[3/5] Loading pre-indexed ANC & HRP registry lookups (instant cache)...")
    with open(lookup_cache_path, "rb") as f:
        lookups = pickle.load(f)
    anc_by_mp = lookups["anc_by_mp"]
    anc_by_mob = lookups["anc_by_mob"]
    hrp_by_mp = lookups["hrp_by_mp"]
    hrp_by_mob = lookups["hrp_by_mob"]
    print(f"  Loaded in < 1s ({len(anc_by_mp)} ANC, {len(hrp_by_mp)} HRP records).")
else:
    anc_by_mp, anc_by_mob, hrp_by_mp, hrp_by_mob = {}, {}, {}, {}

# ─────────────────────────────────────────────────────────────
# 4. CLINICAL & LOCATION ENRICHMENT
# ─────────────────────────────────────────────────────────────
def categorize_clinical(diag_raw):
    d = str(diag_raw).lower()
    # In adverse outcome linelist, all SCD or Sickle cell entries represent crisis/complications
    is_scd = any(k in d for k in ["scd", "sickle", "hbss", "hb-ss", "hb ss", "sickle cell"])
    is_convulsion = "convulsion" in d
    has_isolated_eclampsia = bool(re.search(r"(?<!pre\s)(?<!pre)eclampsia", d))
    is_eclamp = is_convulsion or has_isolated_eclampsia
    is_preeclamp = "preeclampsia" in d or "pre eclampsia" in d or "pih" in d
    is_anemia = "anemia" in d or "anaemia" in d

    if is_scd:
        category = "Sickle Cell Disease Crisis"
        sub_type = "SCD Crisis with Complications"
    elif is_eclamp:
        category = "Hypertensive Disorders (Eclampsia)"
        sub_type = "Eclampsia / Convulsions"
    elif is_preeclamp:
        category = "Hypertensive Disorders (Severe Preeclampsia)"
        sub_type = "Severe Preeclampsia / PIH"
    elif is_anemia:
        category = "Severe Anemia"
        sub_type = "Severe Anemia (Hb < 7 g/dL)"
    else:
        category = "Other Adverse Outcome"
        sub_type = "Unclassified"

    return category, sub_type

def check_out_of_district(full_text):
    if any(k in full_text for k in ["sendhwa", "shendhwa", "kamod"]):
        return True, "Barwani", "Out of District", "Sendhwa (Barwani)", "Out of District (Barwani)"
    if "thikri" in full_text:
        return True, "Barwani", "Out of District", "Thikri (Barwani)", "Out of District (Barwani)"
    if "rajpur" in full_text or "nagalwadi" in full_text:
        return True, "Barwani", "Out of District", "Rajpur (Barwani)", "Out of District (Barwani)"
    if any(k in full_text for k in ["nepanagar", "dahinala"]):
        return True, "Burhanpur", "Out of District", "Nepanagar (Burhanpur)", "Out of District (Burhanpur)"
    if "dharampuri" in full_text:
        return True, "Dhar", "Out of District", "Dharampuri (Dhar)", "Out of District (Dhar)"
    if any(k in full_text for k in ["punasa", "punasala", "ichapur"]):
        return True, "Khandwa", "Out of District", "Punasa (Khandwa)", "Out of District (Khandwa)"
    if any(k in full_text for k in ["jalgaon", "maharashtra", "pawal"]):
        return True, "Jalgaon (Maharashtra)", "Out of District", "Pawal Tehsil (Jalgaon, MH)", "Out of District (Maharashtra)"
    return False, "", "", "", ""

print(f"\n[4/5] Triangulating {len(df_adv)} adverse cases with registries & frontline staff...")

enriched_records = []
for idx, r in df_adv.iterrows():
    sr = int(r["Sr No"])
    name = str(r.get("Patient Name", "")).strip()
    addr = str(r.get("Address", "")).strip() if pd.notna(r.get("Address")) else ""
    vill_raw = str(r.get("village", "")).strip() if pd.notna(r.get("village")) else ""
    sc_raw = str(r.get("Sub centre", "")).strip() if pd.notna(r.get("Sub centre")) else ""
    blk_raw = str(r.get("Block", "")).strip() if pd.notna(r.get("Block")) else ""
    diag_raw = str(r.get("Diagnosis", "")).strip() if pd.notna(r.get("Diagnosis")) else "Unspecified"
    mother_raw = str(r.get("Mother status", "")).strip() if pd.notna(r.get("Mother status")) else "Not recorded"
    baby_raw = str(r.get("Baby status", "")).strip() if pd.notna(r.get("Baby status")) else "Not recorded"
    sncu_raw = str(r.get("Transfer of baby to sncu reason", "")).strip() if pd.notna(r.get("Transfer of baby to sncu reason")) else "No"
    mob = r["mob_clean"]
    mp = r["mp_clean"]
    adm_date = r["adm_date"]
    adm_month = r["adm_month"]

    cat, sub_type = categorize_clinical(diag_raw)

    m_lower = mother_raw.lower()
    if "died" in m_lower or "death" in m_lower:
        mother_status_norm = "Maternal Death"
    elif "refer" in m_lower or "indore" in m_lower:
        mother_status_norm = "Critical Near-Miss (Tertiary Referral)"
    elif "live" in m_lower:
        mother_status_norm = "Survived / Discharged"
    else:
        mother_status_norm = "Not Recorded"

    b_lower = baby_raw.lower()
    if any(k in b_lower for k in ["iud", "iufd", "stillbirth", "msb"]):
        baby_status_norm = "Stillbirth / IUFD"
    elif any(k in b_lower for k in ["died", "death"]):
        baby_status_norm = "Early Neonatal Death"
    elif "live" in b_lower:
        baby_status_norm = "Live Birth"
    else:
        baby_status_norm = "Not Recorded"

    s_lower = sncu_raw.lower()
    is_sncu = any(k in s_lower for k in ["yes", "shift", "lbw", "gasping", "msl"]) or "death in sncu" in b_lower

    # 1. Match against ANC & HRP
    anc_match = None
    if mp != "" and mp in anc_by_mp:
        anc_match = anc_by_mp[mp]
    elif mob != "" and mob in anc_by_mob:
        anc_match = anc_by_mob[mob]

    hrp_match = None
    if mp != "" and mp in hrp_by_mp:
        hrp_match = hrp_by_mp[mp]
    elif mob != "" and mob in hrp_by_mob:
        hrp_match = hrp_by_mob[mob]

    # Location Triangulation
    assigned_district = "Khargone (West Nimar)"
    assigned_block = ""
    assigned_sc = ""
    assigned_village = ""
    is_khargone = True
    sub_area = ""
    match_status = ""

    # Check Out-of-District first
    full_text = f"{addr} {sc_raw} {blk_raw}".lower()
    is_out, out_dist, out_blk, out_sub, out_status = check_out_of_district(full_text)
    if is_out:
        is_khargone = False
        assigned_district = out_dist
        assigned_block = out_blk
        sub_area = out_sub
        match_status = out_status

    # If registry matched, use verified registry location
    ref_row = hrp_match if hrp_match is not None else anc_match
    if ref_row is not None:
        reg_blk = str(ref_row.get("Health Block Name", "")).strip()
        reg_sc = str(ref_row.get("Health Sub Centre Name", "")).strip()
        reg_vill = str(ref_row.get("Village Name", "")).strip()
        
        if reg_blk and reg_blk.lower() not in ["nan", "none", ""]:
            assigned_block = reg_blk
            assigned_sc = reg_sc
            assigned_village = clean_village(reg_vill)
            is_khargone = True
            assigned_district = "Khargone (West Nimar)"
            sub_area = f"{reg_sc} ({clean_village(reg_vill)})"
            match_status = f"Verified via {'HRP' if hrp_match is not None else 'ANC'} Registry"

    # If not assigned block yet, check stated fields
    if not assigned_block:
        blk_lower = blk_raw.lower()
        if "oon" in blk_lower or "oon" in full_text:
            assigned_block = "Khargone"
            sub_area = "PHC Oon Sector"
            match_status = "Matched (Khargone - Oon Sector)"
        elif "jhirniya" in blk_lower or "jhiranya" in blk_lower:
            assigned_block = "Jhiranya"
            sub_area = "Jhiranya Block"
            match_status = "Matched (Jhiranya)"
        elif "barwah" in blk_lower or "sanawad" in full_text:
            assigned_block = "Barwaha"
            sub_area = "Barwaha / Sanawad Block"
            match_status = "Matched (Barwaha)"
        elif "gogawa" in blk_lower or "gogaon" in blk_lower:
            assigned_block = "Gogaon"
            sub_area = "Gogaon Block"
            match_status = "Matched (Gogaon)"
        elif "kasrawad" in blk_lower:
            assigned_block = "Kasrawad"
            sub_area = "Kasrawad Block"
            match_status = "Matched (Kasrawad)"
        elif "bhagwanpura" in blk_lower or "sirvel" in full_text:
            assigned_block = "Bhagwanpura"
            sub_area = "Bhagwanpura Block"
            match_status = "Matched (Bhagwanpura)"
        elif "bhikangao" in blk_lower or "bhikangaon" in blk_lower:
            assigned_block = "Bhikangaon"
            sub_area = "Bhikangaon Block"
            match_status = "Matched (Bhikangaon)"
        elif "segao" in blk_lower or "segaon" in blk_lower:
            assigned_block = "Segaon"
            sub_area = "Segaon Block"
            match_status = "Matched (Segaon)"
        elif "maheshwar" in blk_lower:
            assigned_block = "Maheshwar"
            sub_area = "Maheshwar Block"
            match_status = "Matched (Maheshwar)"
        elif "khargone" in blk_lower:
            assigned_block = "Khargone"
            sub_area = "Khargone Block"
            match_status = "Matched (Khargone)"

    # If assigned_sc is still empty, search village in Village list
    if not assigned_sc and is_khargone:
        combined_lower = f"{addr} {vill_raw} {sc_raw}".lower()
        if "senkheda" in combined_lower or "sinkhedi" in combined_lower:
            assigned_sc = "SHC Sinkhedi New"
            assigned_village = "Sengwi / Sinkhedi"
            assigned_block = "Segaon"
        elif "heerapur" in combined_lower:
            assigned_sc = "SHC Ambakheda"
            assigned_village = "Heerapur"
            assigned_block = "Bhagwanpura"
        elif "tharadpura" in combined_lower:
            assigned_sc = "SHC Ambakheda"
            assigned_village = "Tharadpura"
            assigned_block = "Bhagwanpura"
        elif "mogawa" in combined_lower:
            assigned_sc = "SHC Mogawa"
            assigned_village = "Mogawa"
            assigned_block = "Barwaha"
        elif "gorakhpur" in combined_lower:
            assigned_sc = "SHC Gorakhpur"
            assigned_village = "Gorakhpur"
            assigned_block = "Jhiranya"
        elif "kanjhar" in combined_lower:
            assigned_sc = "SHC Kanjhar"
            assigned_village = "Kanjhar"
            assigned_block = "Bhikangaon"
        elif "sapatiya" in combined_lower:
            assigned_sc = "SHC Saikheda"
            assigned_village = "Sapatiya"
            assigned_block = "Jhiranya"
        elif "aawaliya" in combined_lower:
            assigned_sc = "SHC Bhagwanpura New1"
            assigned_village = "Aawaliya"
            assigned_block = "Bhikangaon"
        elif "umariya" in combined_lower:
            assigned_sc = "SHC Umariya"
            assigned_village = "Umariya"
            assigned_block = "Barwaha"
        elif "chandawad" in combined_lower:
            assigned_sc = "SHC Banher"
            assigned_village = "Chandawad"
            assigned_block = "Bhagwanpura"
        else:
            for w in re.findall(r"[a-z]{4,}", combined_lower):
                if w in ["chc", "phc", "refer", "ward", "teh", "gram", "faliya", "sanawad", "bhikangao", "jhirniya", "bhagwanpura", "khargone", "segaon", "barwah"]:
                    continue
                m_v = df_vill[(df_vill["Block Name"].fillna("").str.lower() == assigned_block.lower()) & (df_vill["Village Name"].fillna("").str.lower() == w)]
                if len(m_v) == 0:
                    m_v = df_vill[df_vill["Village Name"].fillna("").str.lower() == w]
                if len(m_v) > 0:
                    v_hit = m_v.iloc[0]
                    assigned_sc = str(v_hit["Subcentre Name"])
                    assigned_village = clean_village(v_hit["Village Name"])
                    if not assigned_block:
                        assigned_block = str(v_hit["Block Name"])
                    break

    # Fallback to Out of District if unmapped
    if not assigned_block:
        assigned_block = "Out of District"
        is_khargone = False
        assigned_district = "Out of District"
        sub_area = "Unmapped Location"
        match_status = "Unmapped / Out of District"

    if assigned_block.lower() == "jhirniya": assigned_block = "Jhiranya"
    elif assigned_block.lower() == "gogawa": assigned_block = "Gogaon"
    elif assigned_block.lower() == "barwah": assigned_block = "Barwaha"

    # Frontline Workers
    anm_name, anm_phone, cho_name, cho_phone, asha_name = "", "", "", "", ""

    if ref_row is not None:
        raw_anm = str(ref_row.get("Name of ANM", "")).strip()
        raw_cho = str(ref_row.get("CHO Name", "")).strip()
        raw_asha = str(ref_row.get("Name of ASHA", "")).strip()
        if raw_anm and raw_anm.lower() not in ["nan", "none", "null", ""]: anm_name = raw_anm
        if raw_cho and raw_cho.lower() not in ["nan", "none", "null", ""]: cho_name = raw_cho
        if raw_asha and raw_asha.lower() not in ["nan", "none", "null", ""]: asha_name = raw_asha

    target_sc = assigned_sc if assigned_sc else sc_raw
    sc_k = norm_str(target_sc)
    if sc_k and sc_k in anm_by_sc:
        if not anm_name or anm_name == "Unrecorded (DH Direct Case)": anm_name = anm_by_sc[sc_k]["name"]
        if not anm_phone: anm_phone = anm_by_sc[sc_k]["phone"]
    if sc_k and sc_k in cho_by_sc:
        if not cho_name or cho_name == "Unrecorded (DH Direct Case)": cho_name = cho_by_sc[sc_k]["name"]
        if not cho_phone: cho_phone = cho_by_sc[sc_k]["phone"]

    if anm_name and not anm_phone:
        nk = norm_name(anm_name)
        if nk in anm_by_name: anm_phone = anm_by_name[nk]["phone"]
    if cho_name and not cho_phone:
        nk = norm_name(cho_name)
        if nk in cho_by_name: cho_phone = cho_by_name[nk]["phone"]

    if not anm_name and not cho_name:
        if not is_khargone:
            anm_name, cho_name, asha_name = "Out of District Staff", "Out of District CHO", "Out of District ASHA"
        else:
            anm_name, cho_name, asha_name = "Unrecorded (DH Direct Case)", "Unrecorded (DH Direct Case)", "Unrecorded (DH Direct Case)"

    staff_display_parts = []
    if anm_name and anm_name != "Unrecorded (DH Direct Case)":
        staff_display_parts.append(f"ANM: {anm_name}" + (f" (Ph: {anm_phone})" if anm_phone else ""))
    if cho_name and cho_name != "Unrecorded (DH Direct Case)":
        staff_display_parts.append(f"CHO: {cho_name}" + (f" (Ph: {cho_phone})" if cho_phone else ""))
    if asha_name and asha_name != "Unrecorded (DH Direct Case)":
        staff_display_parts.append(f"ASHA: {asha_name}")
    
    frontline_workers_str = " | ".join(staff_display_parts) if staff_display_parts else "Unrecorded / Direct DH Case"

    # HRP Details
    hrp_flagged_cat = "Not Flagged in HRP"
    pih_mgmt = "None"
    fcm_given = "No"
    bt_units = "0"

    if hrp_match is not None:
        hrp_cats = []
        if str(hrp_match.get("Identified with PIH (Yes/No)", "")).strip().lower() == "yes":
            hrp_cats.append("PIH / Hypertensive Disorder")
            pih_mgmt = str(hrp_match.get("PIH Management Done (If Yes in PIH) (Methyledopa/Labetalol/Inj. MgSO4/ Nifedipine)", "None")).strip()
        if str(hrp_match.get("If severe anemia (Yes/No)", "")).strip().lower() == "yes":
            hrp_cats.append("Severe Anemia")
        elif str(hrp_match.get("If moderate anemia (Yes/No)", "")).strip().lower() == "yes":
            hrp_cats.append("Moderate Anemia")
        
        scd_val = str(hrp_match.get("Result of sickle cell test (1. Trait 2. Disease  3. Thalassemia 4. Sickle beta Thalassemia 5.Negative 6. Not done)", "")).strip()
        if any(k in scd_val.lower() for k in ["trait", "disease", "sickle"]):
            hrp_cats.append(f"Sickle Cell ({scd_val})")
        
        if str(hrp_match.get("GDM Positive", "")).strip().lower() == "yes":
            hrp_cats.append("Gestational Diabetes (GDM)")
        if str(hrp_match.get("Previous LSCS", "")).strip().lower() == "yes":
            hrp_cats.append("Previous LSCS")
        
        fcm_raw = str(hrp_match.get("Inj FCM given (Yes/No)", "")).strip()
        if fcm_raw.lower() == "yes": fcm_given = "Yes"

        bt_raw = str(hrp_match.get("Number of Blood transfusion units (If BT Given Only)", "0")).strip()
        if bt_raw and bt_raw.lower() not in ["nan", "none", "0.0", ""]:
            bt_units = bt_raw.replace(".0", "")

        hrp_flagged_cat = "; ".join(hrp_cats) if hrp_cats else "Flagged High Risk on Portal"

    bmo_actions = [
        "1) Do community audit why condition was not resolved?",
        "2) Ask in review meeting to MO and CHO why women presented with adverse outcome?",
        "3) If found any system gaps try to resolve."
    ]

    record = {
        "sr_no": sr,
        "mpid": mp if mp else "Not Available",
        "patient_name": name,
        "mobile_number": mob if mob else "Not Available",
        "admission_month": adm_month,
        "admission_date": adm_date,
        "stated_address": addr,
        "stated_subcentre": sc_raw if sc_raw else "Not Specified",
        "stated_block": blk_raw if blk_raw else "Missing",
        "diagnosis_raw": diag_raw,
        "clinical_category": cat,
        "clinical_sub_type": sub_type,
        "mother_status": mother_raw,
        "mother_status_norm": mother_status_norm,
        "baby_status": baby_raw,
        "baby_status_norm": baby_status_norm,
        "sncu_reason": sncu_raw,
        "is_sncu_admission": is_sncu,
        "is_khargone_district": is_khargone,
        "assigned_district": assigned_district,
        "assigned_block": assigned_block,
        "sub_location_area": sub_area,
        "assigned_subcentre": assigned_sc if assigned_sc else (sc_raw if sc_raw else "Not Specified"),
        "assigned_village": clean_village(assigned_village if assigned_village else (vill_raw if vill_raw else addr)),
        "hierarchy_match_status": match_status,
        "anc_registry_matched": anc_match is not None,
        "anm_name": anm_name,
        "anm_phone": anm_phone,
        "cho_name": cho_name,
        "cho_phone": cho_phone,
        "asha_name": asha_name,
        "frontline_workers": frontline_workers_str,
        "hrp_matched": hrp_match is not None,
        "hrp_flagged_category": hrp_flagged_cat,
        "pih_management_done": pih_mgmt,
        "inj_fcm_given": fcm_given,
        "blood_transfusion_units": bt_units,
        "bmo_feedback_action": " ".join(bmo_actions)
    }
    enriched_records.append(record)

df_enriched = pd.DataFrame(enriched_records)

# ─────────────────────────────────────────────────────────────
# 5. BLOCK SCORECARD & SUMMARY PAYLOAD
# ─────────────────────────────────────────────────────────────
df_khargone = df_enriched[df_enriched["is_khargone_district"]].copy()

blk_summary = df_khargone.groupby("assigned_block").agg(
    Total_Adverse_Cases=("sr_no", "count"),
    Severe_Preeclampsia=("clinical_category", lambda x: (x == "Hypertensive Disorders (Severe Preeclampsia)").sum()),
    Eclampsia=("clinical_category", lambda x: (x == "Hypertensive Disorders (Eclampsia)").sum()),
    Severe_Anemia=("clinical_category", lambda x: (x == "Severe Anemia").sum()),
    Sickle_Cell_Crisis=("clinical_category", lambda x: (x == "Sickle Cell Disease Crisis").sum()),
    Stillbirths_IUFD=("baby_status_norm", lambda x: (x == "Stillbirth / IUFD").sum()),
    SNCU_Transfers=("is_sncu_admission", "sum"),
    Neonatal_Deaths=("baby_status_norm", lambda x: (x == "Early Neonatal Death").sum())
).reset_index()

blk_summary = blk_summary.sort_values("assigned_block")

json_payload = {
    "summary": {
        "total_cases": len(df_enriched),
        "khargone_cases": int(df_enriched["is_khargone_district"].sum()),
        "out_of_district_cases": int((~df_enriched["is_khargone_district"]).sum()),
        "severe_anemia_count": int((df_enriched["clinical_category"] == "Severe Anemia").sum()),
        "severe_preeclampsia_count": int((df_enriched["clinical_category"] == "Hypertensive Disorders (Severe Preeclampsia)").sum()),
        "eclampsia_count": int((df_enriched["clinical_category"] == "Hypertensive Disorders (Eclampsia)").sum()),
        "scd_crisis_count": int((df_enriched["clinical_category"] == "Sickle Cell Disease Crisis").sum()),
        "maternal_deaths": int((df_enriched["mother_status_norm"] == "Maternal Death").sum()),
        "stillbirths_iufd": int((df_enriched["baby_status_norm"] == "Stillbirth / IUFD").sum()),
        "neonatal_deaths": int((df_enriched["baby_status_norm"] == "Early Neonatal Death").sum()),
        "sncu_transfers": int(df_enriched["is_sncu_admission"].sum()),
        "hrp_matched_count": int(df_enriched["hrp_matched"].sum()),
        "months": sorted(list(df_enriched["admission_month"].unique()))
    },
    "block_summary": blk_summary.to_dict(orient="records"),
    "cases": df_enriched.to_dict(orient="records")
}

# 1. Save bmo_dashboard_data.json
json_path = os.path.join(BASE, "bmo_dashboard_data.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(json_payload, f, indent=2)
print(f"\n[5/5] Saved bmo_dashboard_data.json ({len(df_enriched)} cases).")

# 2. Update index.html directly with fresh data
html_path = os.path.join(BASE, "index.html")
if not os.path.exists(html_path):
    html_path = os.path.join(BASE, "BMO_Adverse_Outcome_Dashboard.html")

if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    idx1 = html_content.find("const DATA =")
    if idx1 != -1:
        idx2 = html_content.find("</script>", idx1)
        if idx2 != -1:
            json_str = json.dumps(json_payload, indent=2)
            html_content = html_content[:idx1] + "const DATA = " + json_str + ";\n  " + html_content[idx2:]
            
            # Update 'Last update on DD-MM-YYYY' badge with current date
            today_str = time.strftime("%d-%m-%Y")
            html_content = re.sub(r"Last update on \d{2}-\d{2}-\d{4}", f"Last update on {today_str}", html_content)
            
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"  Updated {os.path.basename(html_path)} with live data and date ({today_str}) embedded!")
        else:
            print(f"  WARNING: Could not find closing </script> tag after const DATA in {os.path.basename(html_path)}.")
    else:
        print(f"  WARNING: Could not find 'const DATA =' in {os.path.basename(html_path)}.")
else:
    print("  WARNING: index.html not found.")

# 3. Auto-Generate All Excel Reports
print("\n" + "-" * 60)
print("  TRIGGERING EXCEL REPORT GENERATOR (generate_styled_excel.py)")
print("-" * 60)
excel_script = os.path.join(BASE, "generate_styled_excel.py")
if os.path.exists(excel_script):
    res = subprocess.run([sys.executable, excel_script], capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print("WARNING: Excel report generation failed:", res.stderr)
    else:
        print("All Excel reports successfully regenerated in Excel Reports/ folder.")
else:
    print("WARNING: generate_styled_excel.py not found.")

# 4. Auto-Push to GitHub
print("\n" + "-" * 60)
print("  PUSHING UPDATED PROJECT FILES TO GITHUB")
print("-" * 60)
try:
    today_str = time.strftime("%d-%m-%Y")
    # Stage modified files
    subprocess.run(["git", "add", "."], cwd=BASE, check=True)
    
    # Check if there are changes to commit
    status_proc = subprocess.run(["git", "status", "--porcelain"], cwd=BASE, capture_output=True, text=True, check=True)
    if status_proc.stdout.strip():
        commit_msg = f"Auto-update adverse outcome dashboard data: {today_str} ({len(df_enriched)} cases)"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=BASE, check=True)
        print(f"  Committed changes: '{commit_msg}'")
        
        push_proc = subprocess.run(["git", "push", "origin", "main"], cwd=BASE, capture_output=True, text=True)
        if push_proc.returncode == 0:
            print("  Successfully pushed updated project files to GitHub (origin/main)!")
        else:
            # Try plain git push if upstream is set
            push_proc2 = subprocess.run(["git", "push"], cwd=BASE, capture_output=True, text=True)
            if push_proc2.returncode == 0:
                print("  Successfully pushed updated project files to GitHub!")
            else:
                print(f"  WARNING: Git push failed:\n{push_proc.stderr or push_proc.stdout or push_proc2.stderr}")
    else:
        print("  Git working tree clean. No changes to commit/push.")
except Exception as e:
    print(f"  WARNING: Auto git push encountered an error: {e}")

print("=" * 60)
print(f"  DASHBOARD GENERATION COMPLETE! Total Cases: {len(df_enriched)}")
print("=" * 60)
