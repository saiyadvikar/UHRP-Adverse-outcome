# -*- coding: utf-8 -*-
import re

with open('BMO_Adverse_Outcome_Dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

script_opens = len(re.findall(r'<script\b', html))
script_closes = len(re.findall(r'</script>', html))
print(f'Script tags: {script_opens} open, {script_closes} close')

style_opens = len(re.findall(r'<style\b', html))
style_closes = len(re.findall(r'</style>', html))
print(f'Style tags: {style_opens} open, {style_closes} close')

div_opens = len(re.findall(r'<div\b', html))
div_closes = len(re.findall(r'</div>', html))
print(f'Div tags: {div_opens} open, {div_closes} close')

critical_ids = [
    'global-filter-block', 'global-filter-month', 'global-filter-diag', 'global-filter-search',
    'kpi-total', 'kpi-khargone', 'kpi-out', 'kpi-hdp', 'kpi-anemia', 'kpi-loss',
    'block-scorecard-body', 'cases-table-body', 'linelist-counter',
    'tab-blocks', 'tab-linelist', 'tab-outdistrict', 'tab-overview', 'tab-guidance',
    'outdistrict-filter', 'out-district-table-body', 'out-district-cards-container',
    'chart-blocks', 'chart-diagnoses', 'chart-outcomes',
    'community-audit-table-body', 'mo-review-table-body',
    'case-modal', 'modal-case-no', 'modal-patient-name', 'modal-body-content'
]

missing = [i for i in critical_ids if f'id="{i}"' not in html]
print(f'Missing critical IDs: {missing}')
