# -*- coding: utf-8 -*-
import re

with open('BMO_Adverse_Outcome_Dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ==============================================================================
# 1. FIX BLOCK FILTER OPTIONS (True Verified Counts)
# ==============================================================================
old_block_select = '''            <select id="global-filter-block" onchange="applyGlobalFilters()" class="w-full text-xs font-semibold rounded-lg border border-slate-300 py-2 px-3 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option value="ALL">All Blocks &amp; Locations (56)</option>
              <option value="KHARGONE_ONLY">Khargone District Only (46)</option>
              <option value="Jhiranya">Jhiranya (10)</option>
              <option value="Bhagwanpura">Bhagwanpura (9)</option>
              <option value="Khargone">Khargone / Oon (6)</option>
              <option value="Barwaha">Barwaha / Sanawad (5)</option>
              <option value="Gogaon">Gogaon (5)</option>
              <option value="Segaon">Segaon (4)</option>
              <option value="Kasrawad">Kasrawad (3)</option>
              <option value="Maheshwar">Maheshwar (2)</option>
              <option value="Bhikangaon">Bhikangaon (2)</option>
              <option value="Out of District">Out of District (10)</option>
            </select>'''

new_block_select = '''            <select id="global-filter-block" onchange="applyGlobalFilters()" class="w-full text-xs font-semibold rounded-lg border border-slate-300 py-2 px-3 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option value="ALL">All Blocks &amp; Locations (56)</option>
              <option value="KHARGONE_ONLY">Khargone District Only (46)</option>
              <option value="Bhagwanpura">Bhagwanpura (10)</option>
              <option value="Barwaha">Barwaha / Sanawad (8)</option>
              <option value="Jhiranya">Jhiranya (7)</option>
              <option value="Khargone">Khargone / Oon (5)</option>
              <option value="Segaon">Segaon (5)</option>
              <option value="Gogaon">Gogaon (4)</option>
              <option value="Bhikangaon">Bhikangaon (4)</option>
              <option value="Maheshwar">Maheshwar (2)</option>
              <option value="Kasrawad">Kasrawad (1)</option>
              <option value="Out of District">Out of District (10)</option>
            </select>'''

assert old_block_select in html, "Block select markup not matched!"
html = html.replace(old_block_select, new_block_select)

# ==============================================================================
# 2. TAB 3: REMOVE DETAILED CASE DOSSIER CARDS FROM OUT OF DISTRICT INFLOW
# ==============================================================================
dossier_cards_markup = '''      <!-- Dossier Cards Grid -->
      <div class="space-y-2.5 pt-2">
        <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
          <i class="fa-solid fa-address-card text-slate-400"></i> Detailed Case Dossier Cards
        </h4>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" id="out-district-cards-container">
          <!-- Injected by JS -->
        </div>
      </div>'''

assert dossier_cards_markup in html, "Dossier cards markup not matched!"
html = html.replace(dossier_cards_markup, '')

# ==============================================================================
# 3. TAB 4: KEEP ONLY CHARTS & MAKE SMALL TO FIT SIDE-BY-SIDE
# ==============================================================================
pat_tab4 = r'<!-- ================= 4\. OVERVIEW & GAPS ================= -->.*?<!-- ================= 5\. BMO ACTION GUIDELINES ================= -->'

new_tab4 = '''<!-- ================= 4. OVERVIEW & GAPS ================= -->
    <div id="tab-overview" class="tab-content hidden space-y-4">
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Chart 1: Adverse Outcomes by Block -->
        <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-xs font-bold text-slate-900 flex items-center gap-1.5">
              <i class="fa-solid fa-chart-column text-indigo-600"></i> Adverse Outcomes by Block
            </h3>
            <span class="text-[10px] font-semibold text-slate-400">56 cases</span>
          </div>
          <div class="h-56 w-full">
            <canvas id="chart-blocks"></canvas>
          </div>
        </div>

        <!-- Chart 2: Clinical Diagnoses Share -->
        <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-xs font-bold text-slate-900 flex items-center gap-1.5">
              <i class="fa-solid fa-chart-pie text-indigo-600"></i> Clinical Diagnoses Share
            </h3>
            <span class="text-[10px] font-semibold text-slate-400">Complications</span>
          </div>
          <div class="h-56 w-full">
            <canvas id="chart-diagnoses"></canvas>
          </div>
        </div>

        <!-- Chart 3: Perinatal Outcomes Breakdown -->
        <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-xs font-bold text-slate-900 flex items-center gap-1.5">
              <i class="fa-solid fa-baby text-emerald-600"></i> Perinatal Outcomes Breakdown
            </h3>
            <span class="text-[10px] font-semibold text-slate-400">Loss &amp; SNCU</span>
          </div>
          <div class="h-56 w-full">
            <canvas id="chart-outcomes"></canvas>
          </div>
        </div>
      </div>

    </div>

    <!-- ================= 5. BMO ACTION GUIDELINES ================= -->'''

html = re.sub(pat_tab4, new_tab4, html, flags=re.DOTALL)

# ==============================================================================
# 4. TAB 5: REMOVE THE THREE TABLES FROM BMO ACTION GUIDELINES
# ==============================================================================
pat_tab5 = r'(<!-- ================= 5\. BMO ACTION GUIDELINES ================= -->.*?)(<!-- Action 1 Data Table: Priority Community Audit Roster -->.*?)(</div>\s*</main>)'

new_tab5_clean = r'''\1</div>
  </main>'''

html = re.sub(pat_tab5, new_tab5_clean, html, flags=re.DOTALL)

# Clean up JS renderBMOActionGuidelines (so it does not error when tables are gone)
old_bmo_func = '''    // Populate BMO Action Guidelines Tables
    function renderBMOActionGuidelines() {
      // 1. Community Audit Table Body
      const auditTbody = document.getElementById('community-audit-table-body');
      if (auditTbody) {
        auditTbody.innerHTML = '';
        // Select severe cases requiring community audits (Anemia < 7, Eclampsia, Deaths, Sickle)
        const priorityAuditCases = DATA.cases.filter(c => 
          c.clinical_category.includes('Severe Anemia') || 
          c.clinical_category.includes('Eclampsia') || 
          c.baby_status_norm !== 'Live Birth' || 
          c.mother_status_norm === 'Maternal Death'
        ).slice(0, 10);

        priorityAuditCases.forEach(c => {
          let triggerText = '';
          if (c.clinical_category.includes('Severe Anemia')) {
            triggerText = `<strong>Severe Anemia (${c.diagnosis_raw}):</strong> Inspect VHSND register. Was Hb tested in 1st/2nd trimester? Why was IV FCM not administered at HWC? Did ASHA provide home-delivered IFA?`;
          } else if (c.clinical_category.includes('Eclampsia')) {
            triggerText = `<strong>Eclampsia / Convulsions:</strong> Review ANC BP chart. Was protein in urine checked? Why was pre-referral loading dose Inj. MgSO4 (4g IV + 10g IM) not administered before transfer?`;
          } else if (c.baby_status_norm !== 'Live Birth') {
            triggerText = `<strong>Perinatal Death (${c.baby_status}):</strong> Investigate 1st and 2nd delay. When did labor begin? Was 108 ambulance called immediately or was private vehicle delay involved?`;
          } else {
            triggerText = `<strong>High-Risk Complication (${c.diagnosis_raw}):</strong> Check whether patient was flagged in ANMOL and followed up by CHO on e-Sanjeevani.`;
          }

          const tr = document.createElement('tr');
          tr.className = 'hover:bg-slate-50 transition';
          tr.innerHTML = `
            <td class="align-top px-3.5 py-3 font-semibold text-slate-900">
              <div class="text-indigo-950 font-bold">${c.assigned_block}</div>
              <div class="text-[11px] text-slate-600">SC: ${c.assigned_subcentre || c.stated_subcentre}</div>
              <div class="text-[10px] text-slate-400">${c.assigned_village || c.stated_address}</div>
            </td>
            <td class="align-top px-3 py-3">
              <div class="font-bold text-slate-900">${c.patient_name}</div>
              <div class="text-[11px] text-slate-500 font-mono">MPID: ${c.mpid}</div>
              <div class="text-[10px] text-slate-400">Adm: ${c.admission_date}</div>
            </td>
            <td class="align-top px-3 py-3">
              <span class="px-2 py-0.5 rounded text-[11px] font-bold ${c.clinical_category.includes('Eclampsia') ? 'badge-eclamp' : 'badge-anemia'}">
                ${c.clinical_category}
              </span>
              <div class="text-[11px] text-slate-600 mt-1 italic">"${c.diagnosis_raw}"</div>
              <div class="text-[10px] text-slate-500 mt-0.5">Outcome: <span class="font-semibold">${c.baby_status}</span></div>
            </td>
            <td class="align-top px-3 py-3 text-slate-700">
              <div class="text-[11px]"><span class="font-semibold text-slate-500">ANM:</span> <span class="font-bold text-indigo-700">${c.anm_name}</span></div>
              <div class="text-[11px] mt-0.5"><span class="font-semibold text-slate-500">CHO:</span> <span class="font-medium text-slate-800">${c.cho_name}</span></div>
              <div class="text-[10px] text-slate-500 mt-0.5"><span class="font-semibold text-slate-400">ASHA:</span> ${c.asha_name}</div>
            </td>
            <td class="align-top px-4 py-3 text-xs text-slate-700 leading-relaxed bg-amber-50/40 border-l border-amber-200">
              ${triggerText}
            </td>
          `;
          auditTbody.appendChild(tr);
        });
      }

      // 2. Sector MO & CHO Review Table Body
      const moTbody = document.getElementById('mo-review-table-body');
      if (moTbody) {
        moTbody.innerHTML = '';
        const sectorRows = [
          {
            sector: 'PHC Sirvel (Bhagwanpura)',
            staff: 'Sector MO: Dr. Solanki | CHO: Jyoti Badole',
            cases: '4 Patients (Severe Anemia down to Hb 2.0, Eclampsia, 1 Stillbirth)',
            questions: '1) Why was Hb 2.0 not picked up during 2nd trimester VHSND?<br/>2) Why was IV FCM not indented or infused at PHC Sirvel?<br/>3) Review ASHA home visit log for nutritional counseling.'
          },
          {
            sector: 'CHC Sanawad (Barwaha)',
            staff: 'Sector MO: Dr. Rathore | CHO: Sandeep Verma',
            cases: '3 Patients (Severe Preeclampsia, Eclampsia with Convulsions)',
            questions: '1) Verify if loading dose Inj. MgSO4 was given before referral to DH.<br/>2) Review calibration of digital BP apparatus in all attached subcentres.<br/>3) Ask why patient was kept at CHC for 6 hours prior to DH transfer.'
          },
          {
            sector: 'PHC Jhiranya (Jhiranya)',
            staff: 'Sector MO: Dr. Sen | CHO: Kavita Dawar',
            cases: '3 Patients (1 Maternal Death, Severe Anemia Hb 2.5, Sickle Crisis)',
            questions: '1) Full clinical review of maternal death: assess transport timeline and emergency pre-referral medication.<br/>2) Why was Sickle Cell status unrecorded on MCP card?<br/>3) Examine 108 ambulance call records from Jhiranya.'
          },
          {
            sector: 'PHC Segaon (Segaon)',
            staff: 'Sector MO: Dr. Patel | CHO: Anita Chouhan',
            cases: '2 Patients (Severe Preeclampsia, 1 Intrauterine Fetal Death)',
            questions: '1) Why was urine albumin not tested when BP exceeded 140/90 mmHg?<br/>2) Did CHO initiate Tab Labetalol prior to referral?<br/>3) Audit subcentre ANC registers for high-risk tracking.'
          },
          {
            sector: 'PHC Gogaon (Gogaon)',
            staff: 'Sector MO: Dr. Yadav | CHO: Pooja Mandloi',
            cases: '2 Patients (Sickle Cell Crisis with severe anemia, SNCU transfer)',
            questions: '1) Confirm universal Sickle Cell screening at booking ANC.<br/>2) Check hydration and pain management protocols followed at PHC.<br/>3) Audit counseling provided on high-risk maternal signs.'
          }
        ];

        sectorRows.forEach(r => {
          const tr = document.createElement('tr');
          tr.className = 'hover:bg-slate-50 transition';
          tr.innerHTML = `
            <td class="align-top px-3.5 py-3 font-bold text-indigo-950">${r.sector}</td>
            <td class="align-top px-3 py-3 text-slate-800 text-xs">${r.staff}</td>
            <td class="align-top px-3 py-3 font-semibold text-rose-800 text-xs">${r.cases}</td>
            <td class="align-top px-4 py-3 text-xs text-slate-700 leading-relaxed bg-indigo-50/30 border-l border-indigo-200">${r.questions}</td>
          `;
          moTbody.appendChild(tr);
        });
      }
    }'''

new_bmo_func = '''    // BMO Action Guidelines handler
    function renderBMOActionGuidelines() {
      // Guidelines are static action points as requested
    }'''

if old_bmo_func in html:
    html = html.replace(old_bmo_func, new_bmo_func)

with open('BMO_Adverse_Outcome_Dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('All user modifications applied successfully!')
