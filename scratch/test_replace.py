# -*- coding: utf-8 -*-
import json
import re

with open('BMO_Adverse_Outcome_Dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Let's inspect where sections start and end
print('File length:', len(html))
