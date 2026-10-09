# -*- coding: utf-8 -*-
import json
import re

with open('BMO_Adverse_Outcome_Dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Verify content has markers
assert '<!-- ================= 2. PATIENT LINELIST' in content
assert '<!-- ================= 3. OUT OF DISTRICT' in content
assert '<!-- ================= 4. OVERVIEW & GAPS' in content
assert '<!-- ================= 5. BMO ACTION GUIDELINES' in content
assert 'function renderCasesTable()' in content
assert 'function renderOutOfDistrict()' in content
print('All markers verified successfully.')
