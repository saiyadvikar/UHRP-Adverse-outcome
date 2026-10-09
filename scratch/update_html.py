import json
import re

with open("bmo_dashboard_data.json", encoding="utf-8") as f:
    json_obj = json.load(f)

json_str = json.dumps(json_obj, indent=2)

with open("BMO_Adverse_Outcome_Dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update Header Button to point to styled excel
html = re.sub(
    r'<a href="[^"]*"\s+download\s+class="[^"]*bg-indigo-600[^"]*">\s*<i class="fa-solid fa-file-excel"></i>\s*Export Excel\s*</a>',
    '<a href="Adverse_Outcome_Patient_Linelist_Styled.xlsx" download class="px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-sm flex items-center gap-1.5 transition"><i class="fa-solid fa-file-excel"></i> Download Styled Excel Linelist</a>',
    html
)

# 2. Update Linelist header to include download button
old_linelist_hdr = '<span id="linelist-counter" class="text-xs font-semibold text-indigo-900 bg-indigo-50 border border-indigo-200 px-3 py-1 rounded-md">\n            56 Patients\n          </span>'
new_linelist_hdr = '''<div class="flex items-center gap-2">
            <span id="linelist-counter" class="text-xs font-semibold text-indigo-900 bg-indigo-50 border border-indigo-200 px-3 py-1.5 rounded-md">
              56 Patients
            </span>
            <a href="Adverse_Outcome_Patient_Linelist_Styled.xlsx" download class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-md shadow-xs flex items-center gap-1.5 transition">
              <i class="fa-solid fa-file-excel"></i> Download Styled Linelist (.xlsx)
            </a>
          </div>'''

if old_linelist_hdr in html:
    html = html.replace(old_linelist_hdr, new_linelist_hdr)
else:
    html = re.sub(
        r'<span id="linelist-counter"[^>]*>.*?</span>',
        new_linelist_hdr,
        html,
        flags=re.DOTALL
    )

# 3. Replace const DATA = { ... };
pattern_data = r'(<!-- Raw Data Injection -->\s*<script>\s*const DATA = )\{.*?\};(\s*</script>)'
repl_data = r'\g<1>' + json_str + r';\g<2>'

html = re.sub(pattern_data, repl_data, html, flags=re.DOTALL)

# 4. Enhance Frontline Workers and Assigned Block in renderCasesTable
old_row_frag = r'''          <!-- 1. Assigned Block & Subcentre -->
          <td class="px-4 py-3">
            <div class="font-bold ${c.is_khargone_district ? 'text-indigo-950' : 'text-amber-800'}">
              ${c.assigned_block}
            </div>
            <div class="text-[11px] text-slate-500">${c.stated_address || c.sub_location_area}</div>
            <div class="text-[10px] text-slate-400">SC: ${c.stated_subcentre}</div>
          </td>'''

new_row_frag = '''          <!-- 1. Assigned Block & Subcentre -->
          <td class="px-4 py-3">
            <div class="font-bold ${c.is_khargone_district ? 'text-indigo-950' : 'text-amber-800'}">
              ${c.assigned_block}
            </div>
            <div class="text-[11px] font-medium text-slate-700">SC: ${c.assigned_subcentre || c.stated_subcentre}</div>
            <div class="text-[10px] text-slate-500">${c.assigned_village || c.stated_address || c.sub_location_area}</div>
          </td>'''

html = html.replace(old_row_frag, new_row_frag)

old_staff_frag = r'''          <!-- 7. Frontline Workers -->
          <td class="px-4 py-3">
            <div class="text-[11px] text-slate-800">ANM: <span class="font-semibold text-indigo-700">${c.anm_name}</span></div>
            <div class="text-[10px] text-slate-500">ASHA: ${c.asha_name}</div>
            <div class="text-[10px] text-slate-500">CHO: ${c.cho_name}</div>
          </td>'''

new_staff_frag = '''          <!-- 7. Frontline Workers -->
          <td class="px-4 py-3">
            <div class="text-[11px] text-slate-800">
              <span class="font-semibold text-slate-600">ANM:</span> 
              <span class="font-bold text-indigo-700">${c.anm_name}</span>
              ${c.anm_phone ? `<a href="tel:${c.anm_phone}" class="ml-1 text-[10px] text-emerald-700 font-semibold bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200 inline-flex items-center gap-0.5 hover:bg-emerald-100" title="Call ANM"><i class="fa-solid fa-phone text-[8px]"></i>${c.anm_phone}</a>` : ''}
            </div>
            <div class="text-[10px] text-slate-600 mt-0.5">
              <span class="font-semibold text-slate-500">CHO:</span> 
              <span class="font-medium text-slate-800">${c.cho_name}</span>
              ${c.cho_phone ? `<a href="tel:${c.cho_phone}" class="ml-1 text-[10px] text-indigo-700 font-semibold bg-indigo-50 px-1.5 py-0.5 rounded border border-indigo-200 inline-flex items-center gap-0.5 hover:bg-indigo-100" title="Call CHO"><i class="fa-solid fa-phone text-[8px]"></i>${c.cho_phone}</a>` : ''}
            </div>
            <div class="text-[10px] text-slate-500 mt-0.5">
              <span class="font-semibold text-slate-400">ASHA:</span> <span class="font-medium text-slate-700">${c.asha_name}</span>
            </div>
          </td>'''

html = html.replace(old_staff_frag, new_staff_frag)

# 5. Enhance modal staff section
old_modal_staff = r'''        <div class="bg-slate-50 p-3.5 rounded-xl border border-slate-200">
          <div class="font-bold text-slate-900 mb-1.5">Assigned Frontline Staff</div>
          <div class="grid grid-cols-3 gap-2 text-slate-700">
            <div>ANM: <div class="font-semibold text-indigo-900">${c.anm_name}</div></div>
            <div>ASHA: <div class="font-semibold text-indigo-900">${c.asha_name}</div></div>
            <div>CHO: <div class="font-semibold text-indigo-900">${c.cho_name}</div></div>
          </div>
        </div>'''

new_modal_staff = '''        <div class="bg-slate-50 p-3.5 rounded-xl border border-slate-200">
          <div class="font-bold text-slate-900 mb-2 flex items-center justify-between">
            <span>Assigned Frontline Staff (Location Hierarchy)</span>
            <span class="text-[10px] text-slate-500 font-normal">Contact info for BMO audit</span>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5 text-slate-700">
            <div class="bg-white p-2.5 rounded-lg border border-slate-200 shadow-xs">
              <div class="text-[10px] uppercase font-bold text-slate-500">ANM</div>
              <div class="font-bold text-indigo-950 mt-0.5">${c.anm_name}</div>
              ${c.anm_phone ? `<a href="tel:${c.anm_phone}" class="text-xs text-emerald-700 font-bold mt-1 inline-flex items-center gap-1 hover:underline"><i class="fa-solid fa-phone text-[10px]"></i> ${c.anm_phone}</a>` : '<div class="text-[10px] text-slate-400 mt-1">No phone recorded</div>'}
            </div>
            <div class="bg-white p-2.5 rounded-lg border border-slate-200 shadow-xs">
              <div class="text-[10px] uppercase font-bold text-slate-500">CHO</div>
              <div class="font-bold text-indigo-950 mt-0.5">${c.cho_name}</div>
              ${c.cho_phone ? `<a href="tel:${c.cho_phone}" class="text-xs text-indigo-700 font-bold mt-1 inline-flex items-center gap-1 hover:underline"><i class="fa-solid fa-phone text-[10px]"></i> ${c.cho_phone}</a>` : '<div class="text-[10px] text-slate-400 mt-1">No phone recorded</div>'}
            </div>
            <div class="bg-white p-2.5 rounded-lg border border-slate-200 shadow-xs">
              <div class="text-[10px] uppercase font-bold text-slate-500">ASHA</div>
              <div class="font-bold text-indigo-950 mt-0.5">${c.asha_name}</div>
              <div class="text-[10px] text-slate-400 mt-1">Village Health Worker</div>
            </div>
          </div>
        </div>'''

html = html.replace(old_modal_staff, new_modal_staff)

# 6. Update search string in applyGlobalFilters to search anm_phone and cho_phone
html = html.replace(
    "${c.anm_name} ${c.asha_name} ${c.cho_name}",
    "${c.anm_name} ${c.anm_phone} ${c.cho_name} ${c.cho_phone} ${c.asha_name} ${c.assigned_subcentre} ${c.assigned_village}"
)

# 7. Update staff sorting
html = html.replace(
    "vA = ((a.anm_name || '') + ' ' + (a.asha_name || '')).toLowerCase();",
    "vA = ((a.anm_name || '') + ' ' + (a.cho_name || '') + ' ' + (a.asha_name || '')).toLowerCase();"
)
html = html.replace(
    "vB = ((b.anm_name || '') + ' ' + (b.asha_name || '')).toLowerCase();",
    "vB = ((b.anm_name || '') + ' ' + (b.cho_name || '') + ' ' + (b.asha_name || '')).toLowerCase();"
)

with open("BMO_Adverse_Outcome_Dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Updated BMO_Adverse_Outcome_Dashboard.html successfully!")
