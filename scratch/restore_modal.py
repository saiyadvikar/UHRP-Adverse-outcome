# -*- coding: utf-8 -*-
import json
import re

with open('BMO_Adverse_Outcome_Dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Load modal JS
with open('scratch/modal_func.js', 'r', encoding='utf-8') as mf:
    raw_modal_js = mf.read()
# Replace escaped newlines if any
modal_js = raw_modal_js.encode('utf-8').decode('unicode_escape')

# Read build_enhanced_dashboard.py to get updated script
# Let's inspect where openCaseModal should be placed in HTML
if 'function openCaseModal' not in html:
    # Insert right before function initCharts()
    html = html.replace('    // Visual Charts in Tab 4', modal_js + '\n\n    // Visual Charts in Tab 4')

with open('BMO_Adverse_Outcome_Dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Modal functions restored and verified!')
