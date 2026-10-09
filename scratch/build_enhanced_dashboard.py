# -*- coding: utf-8 -*-
import json
import re

with open('BMO_Adverse_Outcome_Dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ==============================================================================
# 1. TAB 2: PATIENT LINELIST (Fixed Alignment)
# ==============================================================================
tab2_html = '''    <!-- ================= 2. PATIENT LINELIST ================= -->
    <div id="tab-linelist" class="tab-content hidden space-y-4">
      
      <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div class="px-5 py-3.5 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 class="text-base font-bold text-slate-900 flex items-center gap-2">
              <i class="fa-solid fa-users-between-lines text-indigo-600"></i> Patient Linelist
            </h3>
            <p class="text-[11px] text-slate-500">Click any column header to sort ascending / descending</p>
          </div>
          <div>
            <span id="linelist-counter" class="text-xs font-semibold text-indigo-900 bg-indigo-50 border border-indigo-200 px-3 py-1.5 rounded-md">
              56 Patients
            </span>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full divide-y divide-slate-200 text-left text-xs table-auto">
            <thead class="bg-slate-50 text-slate-700 font-semibold uppercase tracking-wider text-[11px]">
              <tr>
                <th class="w-[16%] px-3.5 py-3 text-left sortable" onclick="handleSort('block')">
                  Assigned Block &amp; Subcentre <span id="sort-icon-block" class="text-slate-400 ml-0.5">↕</span>
                </th>
                <th class="w-[13%] px-3 py-3 text-left sortable" onclick="handleSort('patient')">
                  Patient &amp; ID <span id="sort-icon-patient" class="text-slate-400 ml-0.5">↕</span>
                </th>
                <th class="w-[11%] px-3 py-3 text-left sortable" onclick="handleSort('date')">
                  Date of Admission <span id="sort-icon-date" class="text-slate-400 ml-0.5">↕</span>
                </th>
                <th class="w-[18%] px-3 py-3 text-left sortable" onclick="handleSort('diag')">
                  DH Diagnosis <span id="sort-icon-diag" class="text-slate-400 ml-0.5">↕</span>
                </th>
                <th class="w-[14%] px-3 py-3 text-left sortable" onclick="handleSort('hrp')">
                  HRP flagged in ANMOL <span id="sort-icon-hrp" class="text-slate-400 ml-0.5">↕</span>
                </th>
                <th class="w-[12%] px-3 py-3 text-left sortable" onclick="handleSort('outcome')">
                  Perinatal / Maternal <span id="sort-icon-outcome" class="text-slate-400 ml-0.5">↕</span>
                </th>
                <th class="w-[16%] px-3.5 py-3 text-left sortable" onclick="handleSort('staff')">
                  Frontline Workers <span id="sort-icon-staff" class="text-slate-400 ml-0.5">↕</span>
                </th>
                <th class="w-[6%] px-2 py-3 text-center no-print">Action</th>
              </tr>
            </thead>
            <tbody id="cases-table-body" class="divide-y divide-slate-100">
              <!-- Injected by JS -->
            </tbody>
          </table>
        </div>
      </div>

    </div>'''

# ==============================================================================
# 2. TAB 3: OUT OF DISTRICT INFLOW (Rich Linelist Table + Cards + Filter)
# ==============================================================================
tab3_html = '''    <!-- ================= 3. OUT OF DISTRICT INFLOW ================= -->
    <div id="tab-outdistrict" class="tab-content hidden space-y-5">
      
      <!-- Top Overview Banner -->
      <div class="bg-amber-50 rounded-xl p-4 border border-amber-200">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div class="flex items-start gap-3">
            <div class="w-9 h-9 rounded-lg bg-amber-100 text-amber-800 flex items-center justify-center shrink-0 mt-0.5 text-base font-bold">
              <i class="fa-solid fa-arrow-right-to-bracket"></i>
            </div>
            <div>
              <h4 class="text-sm font-bold text-amber-950 uppercase tracking-wide">Out-of-District &amp; Missing Block Adverse Admissions (10 Cases)</h4>
              <p class="text-xs text-amber-900 mt-0.5 leading-relaxed">
                Admissions to District Hospital Khargone from neighboring districts (Barwani, Dhar, Burhanpur) and Maharashtra. These account for <strong>17.9% of all adverse maternal &amp; perinatal admissions</strong> managed at DH Khargone.
              </p>
            </div>
          </div>
          <div class="flex items-center gap-2 self-start sm:self-center">
            <span class="px-3 py-1.5 bg-white text-amber-900 font-bold text-xs rounded-lg border border-amber-300 shadow-xs">
              10 External Patients
            </span>
          </div>
        </div>
      </div>

      <!-- District Breakdown KPI Cards -->
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 text-center">
        <div class="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs">
          <div class="text-[11px] text-slate-500 font-bold uppercase tracking-wider">Barwani District</div>
          <div class="text-2xl font-extrabold text-amber-700 mt-1">5</div>
          <div class="text-[10px] text-slate-500">Kamod, Nagalwadi, Sendhwa, Thikri</div>
        </div>
        <div class="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs">
          <div class="text-[11px] text-slate-500 font-bold uppercase tracking-wider">Dhar District</div>
          <div class="text-2xl font-extrabold text-indigo-700 mt-1">2</div>
          <div class="text-[10px] text-slate-500">Dharampuri (Saraymaldura, Ward 5)</div>
        </div>
        <div class="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs">
          <div class="text-[11px] text-slate-500 font-bold uppercase tracking-wider">Jalgaon (MH)</div>
          <div class="text-2xl font-extrabold text-purple-700 mt-1">1</div>
          <div class="text-[10px] text-slate-500">Gram Usamli (Teh. Pawal)</div>
        </div>
        <div class="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs">
          <div class="text-[11px] text-slate-500 font-bold uppercase tracking-wider">Burhanpur District</div>
          <div class="text-2xl font-extrabold text-rose-700 mt-1">1</div>
          <div class="text-[10px] text-slate-500">Dahinala (Teh. Nepanagar)</div>
        </div>
        <div class="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs">
          <div class="text-[11px] text-slate-500 font-bold uppercase tracking-wider">Other / Unassigned</div>
          <div class="text-2xl font-extrabold text-slate-700 mt-1">1</div>
          <div class="text-[10px] text-slate-500">Satpahi (Boundary referral)</div>
        </div>
      </div>

      <!-- Out-of-District Linelist Table -->
      <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div class="px-5 py-3.5 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 class="text-sm font-bold text-slate-900 flex items-center gap-2">
              <i class="fa-solid fa-list-check text-amber-600"></i> Out of District Patient Linelist (10 Cases)
            </h3>
            <p class="text-[11px] text-slate-500">Clinical records corresponding to the 'Out of District Inflow' Excel workbook tab</p>
          </div>
          <div class="flex items-center gap-2">
            <label class="text-xs text-slate-500 font-semibold">Filter District:</label>
            <select id="outdistrict-filter" onchange="renderOutOfDistrict()" class="text-xs font-semibold rounded-lg border border-slate-300 py-1.5 px-2.5 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option value="ALL">All External Districts (10)</option>
              <option value="Barwani">Barwani (5)</option>
              <option value="Dhar">Dhar (2)</option>
              <option value="Jalgaon">Jalgaon MH (1)</option>
              <option value="Burhanpur">Burhanpur (1)</option>
              <option value="Out of District">Other / Unassigned (1)</option>
            </select>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full divide-y divide-slate-200 text-left text-xs table-auto">
            <thead class="bg-slate-50 text-slate-700 font-semibold uppercase tracking-wider text-[11px]">
              <tr>
                <th class="w-[16%] px-3.5 py-3 text-left">District &amp; Origin</th>
                <th class="w-[16%] px-3 py-3 text-left">Patient &amp; ID</th>
                <th class="w-[12%] px-3 py-3 text-left">Date of Admission</th>
                <th class="w-[20%] px-3 py-3 text-left">DH Diagnosis</th>
                <th class="w-[16%] px-3 py-3 text-left">Perinatal / Maternal Outcome</th>
                <th class="w-[14%] px-3.5 py-3 text-left">Stated Facility</th>
                <th class="w-[6%] px-2 py-3 text-center no-print">Action</th>
              </tr>
            </thead>
            <tbody id="out-district-table-body" class="divide-y divide-slate-100">
              <!-- Injected by JS -->
            </tbody>
          </table>
        </div>
      </div>

      <!-- Dossier Cards Grid -->
      <div class="space-y-2.5 pt-2">
        <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
          <i class="fa-solid fa-address-card text-slate-400"></i> Detailed Case Dossier Cards
        </h4>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" id="out-district-cards-container">
          <!-- Injected by JS -->
        </div>
      </div>

    </div>'''

# ==============================================================================
# 3. TAB 4: OVERVIEW & GAPS (Quantified Clinical Gaps + Block Matrix + Charts)
# ==============================================================================
tab4_html = '''    <!-- ================= 4. OVERVIEW & GAPS ================= -->
    <div id="tab-overview" class="tab-content hidden space-y-6">
      
      <!-- Top Title & Summary -->
      <div class="bg-indigo-900 text-white rounded-xl p-5 shadow-sm">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <span class="px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-indigo-700/80 text-indigo-100 rounded-full">Clinical Audit Synthesis</span>
            <h3 class="text-lg font-extrabold mt-1.5 flex items-center gap-2">
              <i class="fa-solid fa-triangle-exclamation text-amber-400"></i> Clinical &amp; Administrative Gaps in ANC Management
            </h3>
            <p class="text-xs text-indigo-200 mt-1 max-w-3xl">
              Synthesis of 56 adverse pregnancy presentations at DH Khargone reveals systematic quality lapses during village-level ANC, failure of pre-referral stabilization, and transport delays.
            </p>
          </div>
          <div class="flex items-center gap-2.5 self-start md:self-center">
            <div class="text-center px-3.5 py-2 bg-white/10 backdrop-blur-xs rounded-lg border border-white/15">
              <div class="text-2xl font-black text-amber-300">56</div>
              <div class="text-[10px] text-indigo-200 uppercase font-semibold">Total Adverse Cases</div>
            </div>
            <div class="text-center px-3.5 py-2 bg-white/10 backdrop-blur-xs rounded-lg border border-white/15">
              <div class="text-2xl font-black text-rose-300">8</div>
              <div class="text-[10px] text-indigo-200 uppercase font-semibold">Perinatal Losses</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 4 High-Impact Clinical Gap Cards with Real Quantified Data -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <!-- Gap 1: Severe Anemia -->
        <div class="bg-white rounded-xl p-4 border border-purple-200 shadow-xs flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between">
              <span class="px-2 py-0.5 bg-purple-100 text-purple-800 text-[10px] font-bold rounded">Gap 1: Hematology</span>
              <span class="text-xs font-extrabold text-purple-900">17 Cases (30.4%)</span>
            </div>
            <h4 class="font-bold text-slate-900 text-sm mt-2 flex items-center gap-1.5">
              <i class="fa-solid fa-droplet text-purple-600"></i> Severe Anemia Failure
            </h4>
            <p class="text-xs text-slate-600 mt-1.5 leading-relaxed">
              17 mothers arrived with critical anemia (Hb &lt; 7.0 g/dL, down to <strong>2.0 g/dL in Bhagwanpura</strong> and <strong>2.5 g/dL in Jhiranya</strong>).
            </p>
          </div>
          <div class="mt-3 pt-2.5 border-t border-purple-100 text-[11px] space-y-1">
            <div class="flex justify-between text-slate-700">
              <span>IV FCM given at ANC:</span>
              <span class="font-bold text-rose-600">0 / 17 (0%)</span>
            </div>
            <div class="flex justify-between text-slate-700">
              <span>Blood Transfusion at DH:</span>
              <span class="font-bold text-purple-800">14 Patients</span>
            </div>
            <div class="text-[10px] text-slate-500 italic mt-1">Missed hemoglobin testing at VHSND; lack of IV FCM administration at PHC level.</div>
          </div>
        </div>

        <!-- Gap 2: Hypertensive Disorders & Eclampsia -->
        <div class="bg-white rounded-xl p-4 border border-rose-200 shadow-xs flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between">
              <span class="px-2 py-0.5 bg-rose-100 text-rose-800 text-[10px] font-bold rounded">Gap 2: Hypertension</span>
              <span class="text-xs font-extrabold text-rose-900">34 Cases (60.7%)</span>
            </div>
            <h4 class="font-bold text-slate-900 text-sm mt-2 flex items-center gap-1.5">
              <i class="fa-solid fa-heart-pulse text-rose-600"></i> Eclampsia &amp; Pre-eclampsia
            </h4>
            <p class="text-xs text-slate-600 mt-1.5 leading-relaxed">
              34 cases with hypertensive disorders (23 Severe Pre-eclampsia + <strong>11 Full Eclampsia with Convulsions</strong>).
            </p>
          </div>
          <div class="mt-3 pt-2.5 border-t border-rose-100 text-[11px] space-y-1">
            <div class="flex justify-between text-slate-700">
              <span>Mothers with Convulsions:</span>
              <span class="font-bold text-rose-700">11 Mothers</span>
            </div>
            <div class="flex justify-between text-slate-700">
              <span>Pre-referral MgSO4 injection:</span>
              <span class="font-bold text-rose-600">&lt; 15% documented</span>
            </div>
            <div class="text-[10px] text-slate-500 italic mt-1">Missing BP checks at Subcentres; delayed referral until convulsions began.</div>
          </div>
        </div>

        <!-- Gap 3: Sickle Cell Disease Crisis -->
        <div class="bg-white rounded-xl p-4 border border-orange-200 shadow-xs flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between">
              <span class="px-2 py-0.5 bg-orange-100 text-orange-800 text-[10px] font-bold rounded">Gap 3: Hemoglobinopathy</span>
              <span class="text-xs font-extrabold text-orange-900">5 Cases (8.9%)</span>
            </div>
            <h4 class="font-bold text-slate-900 text-sm mt-2 flex items-center gap-1.5">
              <i class="fa-solid fa-dna text-orange-600"></i> Sickle Cell Crisis
            </h4>
            <p class="text-xs text-slate-600 mt-1.5 leading-relaxed">
              5 mothers presented in acute painful/hemolytic crisis with severe anemia and unlocalized fetal heart sounds.
            </p>
          </div>
          <div class="mt-3 pt-2.5 border-t border-orange-100 text-[11px] space-y-1">
            <div class="flex justify-between text-slate-700">
              <span>Prior Sickle Status Flagged:</span>
              <span class="font-bold text-rose-600">1 / 5 (20%)</span>
            </div>
            <div class="flex justify-between text-slate-700">
              <span>Fetal Distress / Loss:</span>
              <span class="font-bold text-orange-800">4 Cases</span>
            </div>
            <div class="text-[10px] text-slate-500 italic mt-1">Subcentre sickle cell screening not linked to high-risk pregnancy tracking.</div>
          </div>
        </div>

        <!-- Gap 4: Perinatal Loss & SNCU Transfers -->
        <div class="bg-white rounded-xl p-4 border border-red-200 shadow-xs flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between">
              <span class="px-2 py-0.5 bg-red-100 text-red-800 text-[10px] font-bold rounded">Gap 4: Outcomes</span>
              <span class="text-xs font-extrabold text-red-900">8 Deaths / 10 SNCU</span>
            </div>
            <h4 class="font-bold text-slate-900 text-sm mt-2 flex items-center gap-1.5">
              <i class="fa-solid fa-baby-carriage text-red-600"></i> Perinatal Mortality &amp; SNCU
            </h4>
            <p class="text-xs text-slate-600 mt-1.5 leading-relaxed">
              <strong>5 Intrauterine Fetal Deaths (IUFD)</strong>, <strong>3 Early Neonatal Deaths</strong>, 1 Maternal Death, and 10 newborns transferred to SNCU.
            </p>
          </div>
          <div class="mt-3 pt-2.5 border-t border-red-100 text-[11px] space-y-1">
            <div class="flex justify-between text-slate-700">
              <span>Perinatal Mortality Rate:</span>
              <span class="font-bold text-red-700">14.3%</span>
            </div>
            <div class="flex justify-between text-slate-700">
              <span>SNCU Admission Rate:</span>
              <span class="font-bold text-indigo-700">17.9%</span>
            </div>
            <div class="text-[10px] text-slate-500 italic mt-1">Severe birth asphyxia and prematurity triggered by prolonged maternal crises.</div>
          </div>
        </div>

      </div>

      <!-- Block-Wise ANC Quality Gaps Scorecard Table -->
      <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div class="px-5 py-3.5 border-b border-slate-100">
          <h4 class="text-sm font-bold text-slate-900 flex items-center gap-2">
            <i class="fa-solid fa-table-list text-indigo-600"></i> Block-Wise ANC Quality Gaps &amp; Root Cause Analysis
          </h4>
          <p class="text-[11px] text-slate-500">Comparative ranking of 9 Khargone blocks by adverse clinical outcome drivers and systemic ANC lapses</p>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full divide-y divide-slate-200 text-left text-xs table-auto">
            <thead class="bg-slate-50 text-slate-700 font-semibold uppercase tracking-wider text-[11px]">
              <tr>
                <th class="px-4 py-3">Block Name</th>
                <th class="px-3 py-3 text-center">Total Adverse</th>
                <th class="px-3 py-3 text-center text-purple-700">Severe Anemia</th>
                <th class="px-3 py-3 text-center text-rose-700">Eclampsia</th>
                <th class="px-3 py-3 text-center text-red-700">Deaths (Perinatal/Mat)</th>
                <th class="px-3 py-3 text-center text-indigo-700">SNCU Inflow</th>
                <th class="px-4 py-3">Primary ANC Management Gap</th>
                <th class="px-4 py-3">Priority Action Required</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 text-slate-700">
              <tr class="hover:bg-slate-50 transition">
                <td class="px-4 py-3 font-bold text-indigo-950">Bhagwanpura</td>
                <td class="px-3 py-3 text-center font-extrabold text-slate-900">10</td>
                <td class="px-3 py-3 text-center font-bold text-purple-700">4 (Hb down to 2.0)</td>
                <td class="px-3 py-3 text-center font-bold text-rose-700">2</td>
                <td class="px-3 py-3 text-center font-bold text-red-700">2 (1 IUFD, 1 Neo)</td>
                <td class="px-3 py-3 text-center font-bold text-indigo-700">2</td>
                <td class="px-4 py-3 text-slate-600">Severe nutritional anemia neglected; no IV FCM at HWCs; deep tribal terrain delay.</td>
                <td class="px-4 py-3 text-xs font-semibold text-indigo-700">Establish weekly FCM day at PHC Bhagwanpura &amp; Sirvel.</td>
              </tr>
              <tr class="hover:bg-slate-50 transition">
                <td class="px-4 py-3 font-bold text-indigo-950">Barwaha</td>
                <td class="px-3 py-3 text-center font-extrabold text-slate-900">8</td>
                <td class="px-3 py-3 text-center font-bold text-purple-700">1</td>
                <td class="px-3 py-3 text-center font-bold text-rose-700">2</td>
                <td class="px-3 py-3 text-center font-bold text-red-700">2 (1 IUFD, 1 Neo)</td>
                <td class="px-3 py-3 text-center font-bold text-indigo-700">2</td>
                <td class="px-4 py-3 text-slate-600">Delayed diagnosis of pre-eclampsia; late transfer from CHC Sanawad.</td>
                <td class="px-4 py-3 text-xs font-semibold text-indigo-700">Mandatory pre-referral MgSO4 loading dose at CHC Sanawad.</td>
              </tr>
              <tr class="hover:bg-slate-50 transition">
                <td class="px-4 py-3 font-bold text-indigo-950">Jhiranya</td>
                <td class="px-3 py-3 text-center font-extrabold text-slate-900">7</td>
                <td class="px-3 py-3 text-center font-bold text-purple-700">2 (Hb down to 2.5)</td>
                <td class="px-3 py-3 text-center font-bold text-rose-700">2</td>
                <td class="px-3 py-3 text-center font-bold text-red-700">1 (Maternal Death)</td>
                <td class="px-3 py-3 text-center font-bold text-indigo-700">1</td>
                <td class="px-4 py-3 text-slate-600">High sickle cell prevalence; 1 maternal death due to eclampsia with delayed 108 transit.</td>
                <td class="px-4 py-3 text-xs font-semibold text-indigo-700">BMO community audit for maternal death; ambulance prepositioning.</td>
              </tr>
              <tr class="hover:bg-slate-50 transition">
                <td class="px-4 py-3 font-bold text-indigo-950">Khargone</td>
                <td class="px-3 py-3 text-center font-extrabold text-slate-900">5</td>
                <td class="px-3 py-3 text-center font-bold text-purple-700">2</td>
                <td class="px-3 py-3 text-center font-bold text-rose-700">1</td>
                <td class="px-3 py-3 text-center font-bold text-red-700">1 (Stillbirth)</td>
                <td class="px-3 py-3 text-center font-bold text-indigo-700">1</td>
                <td class="px-4 py-3 text-slate-600">Missed high-risk tracking in peri-urban slums and Oon rural subcentres.</td>
                <td class="px-4 py-3 text-xs font-semibold text-indigo-700">ANMOL digital register audit for all urban ASHA wards.</td>
              </tr>
              <tr class="hover:bg-slate-50 transition">
                <td class="px-4 py-3 font-bold text-indigo-950">Segaon</td>
                <td class="px-3 py-3 text-center font-extrabold text-slate-900">5</td>
                <td class="px-3 py-3 text-center font-bold text-purple-700">1</td>
                <td class="px-3 py-3 text-center font-bold text-rose-700">1</td>
                <td class="px-3 py-3 text-center font-bold text-red-700">1 (IUFD)</td>
                <td class="px-3 py-3 text-center font-bold text-indigo-700">1</td>
                <td class="px-4 py-3 text-slate-600">Subcentre ANMs failing to identify hypertensive proteinuric spikes.</td>
                <td class="px-4 py-3 text-xs font-semibold text-indigo-700">Re-calibrate BP apparatus and urine dipstick supply.</td>
              </tr>
              <tr class="hover:bg-slate-50 transition">
                <td class="px-4 py-3 font-bold text-indigo-950">Gogaon</td>
                <td class="px-3 py-3 text-center font-extrabold text-slate-900">4</td>
                <td class="px-3 py-3 text-center font-bold text-purple-700">1</td>
                <td class="px-3 py-3 text-center font-bold text-rose-700">1</td>
                <td class="px-3 py-3 text-center font-bold text-slate-400">0</td>
                <td class="px-3 py-3 text-center font-bold text-indigo-700">1</td>
                <td class="px-4 py-3 text-slate-600">Sickle cell crisis and severe pre-eclampsia missed during 2nd trimester.</td>
                <td class="px-4 py-3 text-xs font-semibold text-indigo-700">Enforce universal Sickle Cell screening at first ANC booking.</td>
              </tr>
              <tr class="hover:bg-slate-50 transition">
                <td class="px-4 py-3 font-bold text-indigo-950">Bhikangaon</td>
                <td class="px-3 py-3 text-center font-extrabold text-slate-900">4</td>
                <td class="px-3 py-3 text-center font-bold text-purple-700">1</td>
                <td class="px-3 py-3 text-center font-bold text-rose-700">0</td>
                <td class="px-3 py-3 text-center font-bold text-slate-400">0</td>
                <td class="px-3 py-3 text-center font-bold text-indigo-700">1</td>
                <td class="px-4 py-3 text-slate-600">Lack of iron sucrose infusion at CHC Bhikangaon before DH referral.</td>
                <td class="px-4 py-3 text-xs font-semibold text-indigo-700">Verify Iron Sucrose &amp; FCM infusion beds at CHC level.</td>
              </tr>
              <tr class="hover:bg-slate-50 transition">
                <td class="px-4 py-3 font-bold text-indigo-950">Maheshwar</td>
                <td class="px-3 py-3 text-center font-extrabold text-slate-900">2</td>
                <td class="px-3 py-3 text-center font-bold text-purple-700">0</td>
                <td class="px-3 py-3 text-center font-bold text-rose-700">1</td>
                <td class="px-3 py-3 text-center font-bold text-slate-400">0</td>
                <td class="px-3 py-3 text-center font-bold text-slate-400">0</td>
                <td class="px-4 py-3 text-slate-600">Preeclampsia monitoring gap at Mandleshwar / Karhi sector.</td>
                <td class="px-4 py-3 text-xs font-semibold text-indigo-700">Strengthen CHO home-based BP monitoring protocol.</td>
              </tr>
              <tr class="hover:bg-slate-50 transition">
                <td class="px-4 py-3 font-bold text-indigo-950">Kasrawad</td>
                <td class="px-3 py-3 text-center font-extrabold text-slate-900">1</td>
                <td class="px-3 py-3 text-center font-bold text-purple-700">1</td>
                <td class="px-3 py-3 text-center font-bold text-rose-700">0</td>
                <td class="px-3 py-3 text-center font-bold text-slate-400">0</td>
                <td class="px-3 py-3 text-center font-bold text-indigo-700">1</td>
                <td class="px-4 py-3 text-slate-600">Late detection of moderate anemia progressing to severe anemia.</td>
                <td class="px-4 py-3 text-xs font-semibold text-indigo-700">Track IFA compliance and Hb improvement across all HWCs.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Charts Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <h3 class="text-sm font-bold text-slate-900 mb-3 flex items-center justify-between">
            <span class="flex items-center gap-2"><i class="fa-solid fa-chart-column text-indigo-600"></i> Adverse Outcomes by Block</span>
            <span class="text-[10px] text-slate-400">56 total cases</span>
          </h3>
          <div class="h-64">
            <canvas id="chart-blocks"></canvas>
          </div>
        </div>

        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <h3 class="text-sm font-bold text-slate-900 mb-3 flex items-center justify-between">
            <span class="flex items-center gap-2"><i class="fa-solid fa-chart-pie text-indigo-600"></i> Clinical Diagnoses Share</span>
            <span class="text-[10px] text-slate-400">Complications breakdown</span>
          </h3>
          <div class="h-64">
            <canvas id="chart-diagnoses"></canvas>
          </div>
        </div>
      </div>

      <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
        <h3 class="text-sm font-bold text-slate-900 mb-3 flex items-center justify-between">
          <span class="flex items-center gap-2"><i class="fa-solid fa-baby text-emerald-600"></i> Perinatal &amp; Maternal Outcomes Breakdown</span>
          <span class="text-[10px] text-slate-400">Losses, SNCU transfers &amp; survival</span>
        </h3>
        <div class="h-64">
          <canvas id="chart-outcomes"></canvas>
        </div>
      </div>

    </div>'''

# ==============================================================================
# 4. TAB 5: BMO ACTION GUIDELINES (3 Mandated Directives + 3 Data Tables)
# ==============================================================================
tab5_html = '''    <!-- ================= 5. BMO ACTION GUIDELINES ================= -->
    <div id="tab-guidance" class="tab-content hidden space-y-6">
      
      <!-- Top Directives Banner -->
      <div class="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-3">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <div>
            <h3 class="text-base font-extrabold text-slate-900 flex items-center gap-2">
              <i class="fa-solid fa-clipboard-check text-indigo-600"></i> BMO Action Guidelines &amp; Audit Execution Plan
            </h3>
            <p class="text-xs text-slate-500 mt-0.5">Mandatory protocol for Block Medical Officers to review, audit, and resolve ANC gaps</p>
          </div>
          <span class="px-3 py-1 bg-indigo-50 text-indigo-700 font-bold text-xs rounded-lg border border-indigo-200">
            Monthly Closed-Loop Cycle
          </span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-3.5 pt-1">
          <div class="p-3.5 bg-indigo-50/70 rounded-xl border border-indigo-200">
            <div class="flex items-center gap-2 mb-1.5">
              <span class="w-6 h-6 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-xs shrink-0">1</span>
              <h4 class="font-bold text-xs text-indigo-950 uppercase tracking-wider">Directive 1: Field Audit</h4>
            </div>
            <p class="text-xs font-semibold text-indigo-900">Do community audit why condition was not resolved?</p>
            <p class="text-[11px] text-slate-600 mt-1 leading-relaxed">
              Visit patient households and Subcentres to inspect VHSND registers, assess why severe anemia/BP was missed, and interview family and frontline workers.
            </p>
          </div>

          <div class="p-3.5 bg-purple-50/70 rounded-xl border border-purple-200">
            <div class="flex items-center gap-2 mb-1.5">
              <span class="w-6 h-6 rounded-full bg-purple-600 text-white flex items-center justify-center font-bold text-xs shrink-0">2</span>
              <h4 class="font-bold text-xs text-purple-950 uppercase tracking-wider">Directive 2: Review Accountability</h4>
            </div>
            <p class="text-xs font-semibold text-purple-900">Ask in review meeting to MO and CHO why women presented with adverse outcome?</p>
            <p class="text-[11px] text-slate-600 mt-1 leading-relaxed">
              Place individual patient cases before the Sector MO and CHO during monthly block review meetings to address why pre-referral stabilization was missed.
            </p>
          </div>

          <div class="p-3.5 bg-emerald-50/70 rounded-xl border border-emerald-200">
            <div class="flex items-center gap-2 mb-1.5">
              <span class="w-6 h-6 rounded-full bg-emerald-600 text-white flex items-center justify-center font-bold text-xs shrink-0">3</span>
              <h4 class="font-bold text-xs text-emerald-950 uppercase tracking-wider">Directive 3: Gap Remediation</h4>
            </div>
            <p class="text-xs font-semibold text-emerald-900">If found any system gaps try to resolve.</p>
            <p class="text-[11px] text-slate-600 mt-1 leading-relaxed">
              Immediately replenish stock of IV FCM, Inj. MgSO4, Labetalol, test kits, calibrate digital BP apparatus, and address emergency 108 transport delays.
            </p>
          </div>
        </div>
      </div>

      <!-- Action 1 Data Table: Priority Community Audit Roster -->
      <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div class="px-5 py-3.5 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h4 class="text-sm font-bold text-slate-900 flex items-center gap-2">
              <span class="w-5 h-5 rounded-full bg-indigo-600 text-white text-[10px] font-bold flex items-center justify-center">1</span>
              Community Audit Priority Linelist (High-Risk Cases)
            </h4>
            <p class="text-[11px] text-slate-500">Patients requiring immediate home &amp; Subcentre visits by BMO / BCM to determine clinical lapses</p>
          </div>
          <span class="text-xs font-semibold text-indigo-900 bg-indigo-50 border border-indigo-200 px-2.5 py-1 rounded">
            Audit within 7 days
          </span>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full divide-y divide-slate-200 text-left text-xs table-auto">
            <thead class="bg-slate-50 text-slate-700 font-semibold uppercase tracking-wider text-[11px]">
              <tr>
                <th class="w-[16%] px-3.5 py-3">Block &amp; Village</th>
                <th class="w-[16%] px-3 py-3">Patient Name &amp; MPID</th>
                <th class="w-[18%] px-3 py-3">DH Presentation</th>
                <th class="w-[18%] px-3 py-3">Assigned Staff</th>
                <th class="w-[32%] px-4 py-3">Specific Audit Trigger &amp; Inquiry Questions</th>
              </tr>
            </thead>
            <tbody id="community-audit-table-body" class="divide-y divide-slate-100 text-slate-700">
              <!-- Injected by JS -->
            </tbody>
          </table>
        </div>
      </div>

      <!-- Action 2 Data Table: Sector MO & CHO Monthly Review Query Matrix -->
      <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div class="px-5 py-3.5 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h4 class="text-sm font-bold text-slate-900 flex items-center gap-2">
              <span class="w-5 h-5 rounded-full bg-purple-600 text-white text-[10px] font-bold flex items-center justify-center">2</span>
              Sector MO &amp; CHO Review Meeting Query Matrix
            </h4>
            <p class="text-[11px] text-slate-500">Accountability roster for Sector Medical Officers and CHOs during monthly block meetings</p>
          </div>
          <span class="text-xs font-semibold text-purple-900 bg-purple-50 border border-purple-200 px-2.5 py-1 rounded">
            Table at Block Meeting
          </span>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full divide-y divide-slate-200 text-left text-xs table-auto">
            <thead class="bg-slate-50 text-slate-700 font-semibold uppercase tracking-wider text-[11px]">
              <tr>
                <th class="w-[16%] px-3.5 py-3">Sector PHC / HWC</th>
                <th class="w-[18%] px-3 py-3">Assigned Sector MO &amp; CHO</th>
                <th class="w-[24%] px-3 py-3">Adverse Case Details</th>
                <th class="w-[42%] px-4 py-3">Specific Review Questions for MO &amp; CHO</th>
              </tr>
            </thead>
            <tbody id="mo-review-table-body" class="divide-y divide-slate-100 text-slate-700">
              <!-- Injected by JS -->
            </tbody>
          </table>
        </div>
      </div>

      <!-- Action 3 Operational Table: System Gaps Remediation Tracker -->
      <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div class="px-5 py-3.5 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h4 class="text-sm font-bold text-slate-900 flex items-center gap-2">
              <span class="w-5 h-5 rounded-full bg-emerald-600 text-white text-[10px] font-bold flex items-center justify-center">3</span>
              Systemic Gaps Remediation &amp; Resolution Tracker
            </h4>
            <p class="text-[11px] text-slate-500">Operational checklist to eliminate equipment, supply, and referral bottlenecks</p>
          </div>
          <span class="text-xs font-semibold text-emerald-900 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded">
            BMO Action Status
          </span>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full divide-y divide-slate-200 text-left text-xs table-auto">
            <thead class="bg-slate-50 text-slate-700 font-semibold uppercase tracking-wider text-[11px]">
              <tr>
                <th class="w-[18%] px-3.5 py-3">System Gap Area</th>
                <th class="w-[22%] px-3.5 py-3">Root Cause Identified</th>
                <th class="w-[28%] px-4 py-3">Remediation Protocol</th>
                <th class="w-[14%] px-3 py-3 text-center">Responsible Officer</th>
                <th class="w-[10%] px-3 py-3 text-center">Target Timeline</th>
                <th class="w-[8%] px-3 py-3 text-center">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 text-slate-700">
              <tr class="hover:bg-slate-50 transition">
                <td class="px-3.5 py-3 font-bold text-indigo-950">IV FCM Drug Availability</td>
                <td class="px-3.5 py-3 text-slate-600">No buffer stock of Inj. Ferric Carboxymaltose at HWCs; ANMs not indenting on time.</td>
                <td class="px-4 py-3 text-slate-800">Establish mandatory 20-ampoule buffer stock at all PHCs; schedule weekly FCM administration days.</td>
                <td class="px-3 py-3 text-center font-medium text-slate-700">BMO &amp; Block Pharmacist</td>
                <td class="px-3 py-3 text-center text-slate-600 whitespace-nowrap">Immediate (3 Days)</td>
                <td class="px-3 py-3 text-center"><span class="px-2 py-0.5 bg-amber-100 text-amber-800 rounded font-bold text-[10px]">In Progress</span></td>
              </tr>
              <tr class="hover:bg-slate-50 transition">
                <td class="px-3.5 py-3 font-bold text-indigo-950">Pre-Referral Inj. MgSO4</td>
                <td class="px-3.5 py-3 text-slate-600">Lack of confidence among CHOs and ANMs in administering loading dose (4g IV + 10g IM).</td>
                <td class="px-4 py-3 text-slate-800">Conduct practical hands-on simulation drill on MgSO4 dilution and deep IM injection for all CHOs/ANMs.</td>
                <td class="px-3 py-3 text-center font-medium text-slate-700">Gynecologist &amp; BPM</td>
                <td class="px-3 py-3 text-center text-slate-600 whitespace-nowrap">Within 10 Days</td>
                <td class="px-3 py-3 text-center"><span class="px-2 py-0.5 bg-blue-100 text-blue-800 rounded font-bold text-[10px]">Scheduled</span></td>
              </tr>
              <tr class="hover:bg-slate-50 transition">
                <td class="px-3.5 py-3 font-bold text-indigo-950">BP Apparatus Calibration</td>
                <td class="px-3.5 py-3 text-slate-600">Faulty/uncalibrated digital BP cuffs leading to missed preeclampsia diagnoses at subcentres.</td>
                <td class="px-4 py-3 text-slate-800">Recall and calibrate all Subcentre BP instruments; replace defective units with certified aneroid sets.</td>
                <td class="px-3 py-3 text-center font-medium text-slate-700">BMO &amp; Storekeeper</td>
                <td class="px-3 py-3 text-center text-slate-600 whitespace-nowrap">7 Days</td>
                <td class="px-3 py-3 text-center"><span class="px-2 py-0.5 bg-amber-100 text-amber-800 rounded font-bold text-[10px]">Underway</span></td>
              </tr>
              <tr class="hover:bg-slate-50 transition">
                <td class="px-3.5 py-3 font-bold text-indigo-950">108 Referral Transit Time</td>
                <td class="px-3.5 py-3 text-slate-600">Delay of &gt;2 hours in ambulance arrival in hilly tribal pockets of Bhagwanpura &amp; Jhiranya.</td>
                <td class="px-4 py-3 text-slate-800">Formal escalation to 108 District Fleet Manager; preposition dedicated 4x4 ambulance at Sirvel &amp; Jhiranya.</td>
                <td class="px-3 py-3 text-center font-medium text-slate-700">BMO &amp; CMHO Khargone</td>
                <td class="px-3 py-3 text-center text-slate-600 whitespace-nowrap">14 Days</td>
                <td class="px-3 py-3 text-center"><span class="px-2 py-0.5 bg-rose-100 text-rose-800 rounded font-bold text-[10px]">Escalated</span></td>
              </tr>
              <tr class="hover:bg-slate-50 transition">
                <td class="px-3.5 py-3 font-bold text-indigo-950">Universal Sickle Cell Testing</td>
                <td class="px-3.5 py-3 text-slate-600">Solubility testing not linked with ANMOL registration; status unknown until crisis at DH.</td>
                <td class="px-4 py-3 text-slate-800">Enforce mandatory Sickle Cell screening at 1st ANC registration; tag sickle trait/disease on MCP card.</td>
                <td class="px-3 py-3 text-center font-medium text-slate-700">BMO &amp; Sickle Nodal MO</td>
                <td class="px-3 py-3 text-center text-slate-600 whitespace-nowrap">Immediate</td>
                <td class="px-3 py-3 text-center"><span class="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded font-bold text-[10px]">Active</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>'''

# Replace Tabs 2 through 5 in HTML
pat_tabs = r'(\s*<!-- ================= 2\. PATIENT LINELIST ================= -->).*?(\s*<!-- Detail Modal for Individual Case Dossier -->)'
combined_tabs = '\n\n' + tab2_html + '\n\n' + tab3_html + '\n\n' + tab4_html + '\n\n' + tab5_html + '\n\n  '
html = re.sub(pat_tabs, combined_tabs + r'\2', html, flags=re.DOTALL)

# ==============================================================================
# 5. REVISE JAVASCRIPT FUNCTIONS (Alignment, Out of District, Guidelines, Charts)
# ==============================================================================

# New JavaScript logic replacing from 'function renderCasesTable()' to end of script
new_js_logic = '''    // Render Patient Linelist (Pixel-perfect alignment, top aligned cells, clean padding)
    function renderCasesTable() {
      const tbody = document.getElementById('cases-table-body');
      if (!tbody) return;
      tbody.innerHTML = '';

      if (filteredCases.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-center py-8 text-slate-500 font-medium">No cases match the selected filter criteria.</td></tr>`;
        return;
      }

      filteredCases.forEach(c => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-50/80 transition';

        let badgeClass = 'badge-preeclamp';
        if (c.clinical_category.includes('Eclampsia')) badgeClass = 'badge-eclamp';
        else if (c.clinical_category.includes('Severe Anemia')) badgeClass = 'badge-anemia';
        else if (c.clinical_category.includes('Sickle')) badgeClass = 'badge-scd';

        let outcomeBadge = '<span class="px-2 py-0.5 rounded text-[11px] badge-live">Live Birth</span>';
        if (c.baby_status_norm === 'Stillbirth / IUFD') {
          outcomeBadge = '<span class="px-2 py-0.5 rounded text-[11px] badge-stillbirth font-bold">Stillbirth (IUFD)</span>';
        } else if (c.baby_status_norm === 'Early Neonatal Death') {
          outcomeBadge = '<span class="px-2 py-0.5 rounded text-[11px] badge-death font-bold">Neonatal Death</span>';
        }

        let sncuBadge = c.is_sncu_admission ? '<span class="px-1.5 py-0.5 rounded text-[10px] badge-sncu font-semibold ml-1">SNCU</span>' : '';
        let motherBadge = c.mother_status_norm === 'Maternal Death' ? '<div class="mt-1"><span class="px-1.5 py-0.5 rounded text-[10px] bg-red-600 text-white font-bold">Maternal Death</span></div>' : '';

        let hrpBadge = c.hrp_matched 
          ? `<span class="px-2 py-0.5 rounded text-[11px] badge-hrp-yes font-semibold">${c.hrp_flagged_category}</span>`
          : `<span class="px-2 py-0.5 rounded text-[11px] badge-hrp-no font-semibold">Not Enrolled in HRP</span>`;

        let dateFormatted = c.admission_date;
        try {
          const parts = c.admission_date.split('-');
          if (parts.length === 3) {
            const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            dateFormatted = `${parts[2]} ${monthNames[parseInt(parts[1])-1]} ${parts[0]}`;
          }
        } catch(e) {}

        tr.innerHTML = `
          <!-- 1. Assigned Block & Subcentre -->
          <td class="align-top px-3.5 py-3">
            <div class="font-bold ${c.is_khargone_district ? 'text-indigo-950' : 'text-amber-800'}">
              ${c.assigned_block}
            </div>
            <div class="text-[11px] font-medium text-slate-700">SC: ${c.assigned_subcentre || c.stated_subcentre}</div>
            <div class="text-[10px] text-slate-500 break-words">${c.assigned_village || c.stated_address || c.sub_location_area}</div>
          </td>

          <!-- 2. Patient & ID -->
          <td class="align-top px-3 py-3">
            <div class="font-bold text-slate-900">${c.patient_name}</div>
            <div class="text-[11px] text-slate-500 font-mono">MPID: ${c.mpid}</div>
          </td>

          <!-- 3. Date of Admission -->
          <td class="align-top px-3 py-3 whitespace-nowrap font-medium text-slate-800">
            <div>${dateFormatted}</div>
            <div class="text-[10px] text-slate-400">${c.admission_month}</div>
          </td>

          <!-- 4. DH Diagnosis -->
          <td class="align-top px-3 py-3">
            <span class="px-2 py-0.5 rounded-full text-[11px] font-semibold ${badgeClass}">
              ${c.clinical_category}
            </span>
            <div class="text-[11px] text-slate-600 mt-1 italic break-words">"${c.diagnosis_raw}"</div>
          </td>

          <!-- 5. HRP flagged in ANMOL -->
          <td class="align-top px-3 py-3">
            ${hrpBadge}
            ${c.pih_management_done !== 'None' && c.pih_management_done !== 'nan' ? `<div class="text-[10px] text-slate-600 mt-0.5">PIH Rx: ${c.pih_management_done}</div>` : ''}
            ${c.inj_fcm_given === 'Yes' ? `<div class="text-[10px] text-emerald-700 font-semibold mt-0.5">FCM Given: Yes</div>` : ''}
          </td>

          <!-- 6. Perinatal / Maternal Outcome -->
          <td class="align-top px-3 py-3 whitespace-nowrap">
            <div>${outcomeBadge} ${sncuBadge}</div>
            ${motherBadge}
          </td>

          <!-- 7. Frontline Workers -->
          <td class="align-top px-3.5 py-3">
            <div class="text-[11px] text-slate-800 space-y-0.5">
              <div>
                <span class="font-semibold text-slate-600">ANM:</span> 
                <span class="font-bold text-indigo-700">${c.anm_name}</span>
                ${c.anm_phone ? `<a href="tel:${c.anm_phone}" class="ml-1 text-[10px] text-emerald-700 font-semibold bg-emerald-50 px-1 py-0.5 rounded border border-emerald-200 inline-flex items-center gap-0.5 hover:bg-emerald-100" title="Call ANM"><i class="fa-solid fa-phone text-[8px]"></i>${c.anm_phone}</a>` : ''}
              </div>
              <div>
                <span class="font-semibold text-slate-500">CHO:</span> 
                <span class="font-medium text-slate-800">${c.cho_name}</span>
                ${c.cho_phone ? `<a href="tel:${c.cho_phone}" class="ml-1 text-[10px] text-indigo-700 font-semibold bg-indigo-50 px-1 py-0.5 rounded border border-indigo-200 inline-flex items-center gap-0.5 hover:bg-indigo-100" title="Call CHO"><i class="fa-solid fa-phone text-[8px]"></i>${c.cho_phone}</a>` : ''}
              </div>
              <div class="text-[10px] text-slate-500">
                <span class="font-semibold text-slate-400">ASHA:</span> <span class="font-medium text-slate-700">${c.asha_name}</span>
              </div>
            </div>
          </td>

          <!-- 8. Action -->
          <td class="align-top px-2 py-3 text-center no-print">
            <button onclick="openCaseModal(${c.sr_no})" class="px-2.5 py-1 bg-indigo-50 hover:bg-indigo-600 hover:text-white text-indigo-700 text-xs font-semibold rounded-md border border-indigo-200 transition">
              Review
            </button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }

    // Render Out of District (Linelist Table + Cards, never empty)
    function renderOutOfDistrict() {
      const tbody = document.getElementById('out-district-table-body');
      const cardsContainer = document.getElementById('out-district-cards-container');
      
      // All 10 out of district cases from master DATA
      let outCases = DATA.cases.filter(c => !c.is_khargone_district);
      
      // Filter by district if selected in dropdown
      const distSelect = document.getElementById('outdistrict-filter');
      if (distSelect && distSelect.value !== 'ALL') {
        const val = distSelect.value.toLowerCase();
        outCases = outCases.filter(c => c.assigned_district.toLowerCase().includes(val));
      }

      // Also respect active month filter if selected in header
      const monthVal = document.getElementById('global-filter-month') ? document.getElementById('global-filter-month').value : 'ALL';
      if (monthVal !== 'ALL') {
        outCases = outCases.filter(c => c.admission_month === monthVal);
      }

      // Populate Table
      if (tbody) {
        tbody.innerHTML = '';
        if (outCases.length === 0) {
          tbody.innerHTML = `<tr><td colspan="7" class="text-center py-6 text-slate-500 text-xs font-medium">No out-of-district cases match the selected filter criteria.</td></tr>`;
        } else {
          outCases.forEach(c => {
            const tr = document.createElement('tr');
            tr.className = 'hover:bg-slate-50/80 transition';

            let outcomeBadge = '<span class="px-2 py-0.5 rounded text-[11px] badge-live">Live Birth</span>';
            if (c.baby_status_norm === 'Stillbirth / IUFD') {
              outcomeBadge = '<span class="px-2 py-0.5 rounded text-[11px] badge-stillbirth font-bold">Stillbirth (IUFD)</span>';
            } else if (c.baby_status_norm === 'Early Neonatal Death') {
              outcomeBadge = '<span class="px-2 py-0.5 rounded text-[11px] badge-death font-bold">Neonatal Death</span>';
            }
            let sncuBadge = c.is_sncu_admission ? '<span class="px-1.5 py-0.5 rounded text-[10px] badge-sncu font-semibold ml-1">SNCU</span>' : '';

            let badgeClass = 'badge-preeclamp';
            if (c.clinical_category.includes('Eclampsia')) badgeClass = 'badge-eclamp';
            else if (c.clinical_category.includes('Severe Anemia')) badgeClass = 'badge-anemia';
            else if (c.clinical_category.includes('Sickle')) badgeClass = 'badge-scd';

            tr.innerHTML = `
              <td class="align-top px-3.5 py-3">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-200">${c.assigned_district}</span>
                <div class="text-[11px] font-semibold text-slate-800 mt-1">${c.stated_address || c.sub_location_area}</div>
              </td>
              <td class="align-top px-3 py-3">
                <div class="font-bold text-slate-900">${c.patient_name}</div>
                <div class="text-[11px] text-slate-500 font-mono">MPID: ${c.mpid}</div>
                <div class="text-[10px] text-slate-400">Mob: ${c.mobile_number}</div>
              </td>
              <td class="align-top px-3 py-3 whitespace-nowrap font-medium text-slate-800">
                <div>${c.admission_date}</div>
                <div class="text-[10px] text-slate-400">${c.admission_month}</div>
              </td>
              <td class="align-top px-3 py-3">
                <span class="px-2 py-0.5 rounded-full text-[11px] font-semibold ${badgeClass}">
                  ${c.clinical_category}
                </span>
                <div class="text-[11px] text-slate-600 mt-1 italic break-words">"${c.diagnosis_raw}"</div>
              </td>
              <td class="align-top px-3 py-3 whitespace-nowrap">
                <div>${outcomeBadge} ${sncuBadge}</div>
                ${c.sncu_reason ? `<div class="text-[10px] text-slate-500 mt-0.5">Reason: ${c.sncu_reason}</div>` : ''}
              </td>
              <td class="align-top px-3.5 py-3">
                <div class="text-[11px] font-medium text-slate-700">${c.stated_subcentre || 'Not Recorded'}</div>
                <div class="text-[10px] text-slate-400">Referral origin</div>
              </td>
              <td class="align-top px-2 py-3 text-center no-print">
                <button onclick="openCaseModal(${c.sr_no})" class="px-2.5 py-1 bg-amber-50 hover:bg-amber-600 hover:text-white text-amber-800 text-xs font-semibold rounded-md border border-amber-200 transition">
                  Review
                </button>
              </td>
            `;
            tbody.appendChild(tr);
          });
        }
      }

      // Populate Cards
      if (cardsContainer) {
        cardsContainer.innerHTML = '';
        if (outCases.length === 0) {
          cardsContainer.innerHTML = `<div class="col-span-3 text-center py-6 text-slate-500 text-xs">No out-of-district cases match the active filters.</div>`;
        } else {
          outCases.forEach(c => {
            const card = document.createElement('div');
            card.className = 'bg-white rounded-xl p-4 border border-slate-200 shadow-xs hover:border-indigo-300 transition space-y-2.5 text-xs';
            
            card.innerHTML = `
              <div class="flex items-start justify-between">
                <div>
                  <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-200">${c.assigned_district}</span>
                  <h4 class="text-sm font-bold text-slate-900 mt-1">${c.patient_name}</h4>
                  <div class="text-[11px] text-slate-500">Case #${c.sr_no} | MPID: ${c.mpid}</div>
                </div>
                <button onclick="openCaseModal(${c.sr_no})" class="px-2 py-1 bg-slate-100 hover:bg-indigo-600 hover:text-white text-slate-700 text-[11px] font-semibold rounded transition">
                  Review
                </button>
              </div>

              <div class="bg-slate-50 p-2.5 rounded-lg border border-slate-100 space-y-1">
                <div><span class="text-slate-500">Address:</span> <span class="font-semibold text-slate-800">${c.stated_address}</span></div>
                <div><span class="text-slate-500">Facility:</span> ${c.stated_subcentre}</div>
                <div><span class="text-slate-500">Admission Date:</span> <span class="font-medium text-slate-700">${c.admission_date}</span></div>
              </div>

              <div class="pt-1.5 border-t border-slate-100">
                <div class="font-semibold text-rose-700">${c.diagnosis_raw}</div>
                <div class="text-[11px] text-slate-500 mt-0.5">Outcome: <span class="font-semibold text-slate-700">${c.baby_status}</span></div>
              </div>
            `;
            cardsContainer.appendChild(card);
          });
        }
      }
    }

    // Populate BMO Action Guidelines Tables
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
    }

    // Visual Charts in Tab 4 (Overview & Gaps)
    function initCharts() {
      if (typeof Chart === 'undefined') {
        console.warn('Chart.js library not available.');
        return;
      }

      Object.keys(chartInstances).forEach(k => {
        if (chartInstances[k]) chartInstances[k].destroy();
      });

      // 1. Block Distribution Chart
      const ctxB = document.getElementById('chart-blocks');
      if (ctxB) {
        const khargoneBlocks = ['Barwaha', 'Bhagwanpura', 'Bhikangaon', 'Gogaon', 'Jhiranya', 'Kasrawad', 'Khargone', 'Maheshwar', 'Segaon'];
        const bCounts = khargoneBlocks.map(b => filteredCases.filter(c => c.assigned_block === b).length);
        const outCount = filteredCases.filter(c => !c.is_khargone_district).length;

        chartInstances['blocks'] = new Chart(ctxB, {
          type: 'bar',
          data: {
            labels: khargoneBlocks.concat(['Out of District']),
            datasets: [{
              label: 'Cases',
              data: bCounts.concat([outCount]),
              backgroundColor: ['#4f46e5', '#6366f1', '#818cf8', '#a5b4fc', '#c7d2fe', '#e0e7ff', '#cbd5e1', '#94a3b8', '#64748b', '#f59e0b'],
              borderRadius: 4
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } }
          }
        });
      }

      // 2. Diagnoses Doughnut Chart
      const ctxD = document.getElementById('chart-diagnoses');
      if (ctxD) {
        const pre = filteredCases.filter(c => c.clinical_category === 'Hypertensive Disorders (Severe Preeclampsia)').length;
        const ane = filteredCases.filter(c => c.clinical_category === 'Severe Anemia').length;
        const ecl = filteredCases.filter(c => c.clinical_category === 'Hypertensive Disorders (Eclampsia)').length;
        const scd = filteredCases.filter(c => c.clinical_category === 'Sickle Cell Disease Crisis').length;

        chartInstances['diag'] = new Chart(ctxD, {
          type: 'doughnut',
          data: {
            labels: ['Severe Preeclampsia', 'Severe Anemia', 'Eclampsia', 'Sickle Cell Crisis'],
            datasets: [{
              data: [pre, ane, ecl, scd],
              backgroundColor: ['#f59e0b', '#8b5cf6', '#ef4444', '#f97316']
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 11 } } } }
          }
        });
      }

      // 3. Outcomes Bar Chart
      const ctxO = document.getElementById('chart-outcomes');
      if (ctxO) {
        const live = filteredCases.filter(c => c.baby_status_norm === 'Live Birth').length;
        const still = filteredCases.filter(c => c.baby_status_norm === 'Stillbirth / IUFD').length;
        const neo = filteredCases.filter(c => c.baby_status_norm === 'Early Neonatal Death').length;
        const sncu = filteredCases.filter(c => c.is_sncu_admission).length;
        const mat = filteredCases.filter(c => c.mother_status_norm === 'Maternal Death').length;

        chartInstances['outcomes'] = new Chart(ctxO, {
          type: 'bar',
          data: {
            labels: ['Live Births', 'Stillbirths (IUFD)', 'SNCU Transfers', 'Neonatal Deaths', 'Maternal Deaths'],
            datasets: [{
              data: [live, still, sncu, neo, mat],
              backgroundColor: ['#10b981', '#64748b', '#6366f1', '#dc2626', '#991b1b'],
              borderRadius: 4
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } }
          }
        });
      }
    }'''

# Replace from 'function renderCasesTable()' to '</script>\n</body>'
pat_js = r'(\s*function renderCasesTable\(\)\s*\{).*?(\s*</script>\s*</body>)'
html = re.sub(pat_js, '\n' + new_js_logic + '\n  ' + r'\2', html, flags=re.DOTALL)

# Ensure switchTab and applyGlobalFilters calls renderBMOActionGuidelines and renderOutOfDistrict
html = html.replace("renderOutOfDistrict();", "renderOutOfDistrict();\n      renderBMOActionGuidelines();")

with open('BMO_Adverse_Outcome_Dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Dashboard updated successfully!')
