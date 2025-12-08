#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""檢查 vocab_from_bible.yaml 中的引號和括號問題"""

with open('data/vocab_from_bible.yaml', 'r', encoding='utf-8') as f:
    content = f.read()

# 搜尋各種引號和括號
problematic_chars = {
    '"': 'ASCII quote',
    "'": 'ASCII single quote',
    '"': 'Left double quote',
    '"': 'Right double quote',
    ''': 'Left single quote',
    ''': 'Right single quote',
    '(': 'Left paren',
    ')': 'Right paren',
    '（': 'Fullwidth left paren',
    '）': 'Fullwidth right paren',
}

found_issues = {}
lines = content.split('\n')
for i, line in enumerate(lines):
    if line.strip().startswith('#') or not line.strip():
        continue
    for char, name in problematic_chars.items():
        if char in line:
            if name not in found_issues:
                found_issues[name] = []
            found_issues[name].append((i+1, line.strip()[:100]))

if found_issues:
    print('發現問題字元：')
    for name, occurrences in found_issues.items():
        print(f'\n{name}: {len(occurrences)} 次')
        for line_num, text in occurrences[:10]:
            print(f'  Line {line_num}: {text}')
else:
    print('未發現引號或括號問題')
