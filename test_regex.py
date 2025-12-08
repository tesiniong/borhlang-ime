#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""測試正則表達式"""
import re

# 當前的正則表達式
pattern = r'[,，;；:.。:：!！?？、()（）"""\'\'\""]'

test_strings = [
    ('"', 'U+0022 ASCII quote'),
    ('"', 'U+201C Left double quote'),
    ('"', 'U+201D Right double quote'),
    (''', 'U+2018 Left single quote'),
    (''', 'U+2019 Right single quote'),
]

print('測試當前正則表達式移除效果：')
print(f'Pattern: {pattern}\n')

for char, desc in test_strings:
    result = re.sub(pattern, '', char)
    removed = len(result) == 0
    status = "REMOVED" if removed else "NOT removed"
    print(f'{char} {desc}: {status}')

# 建議的完整正則表達式
print('\n' + '='*60)
suggested_pattern = r'[,，;；:.。:：!！?？、()（）"""\'\'\""\u201C\u201D\u2018\u2019]'
print(f'建議使用 Unicode escape:\n{suggested_pattern}\n')

for char, desc in test_strings:
    result = re.sub(suggested_pattern, '', char)
    removed = len(result) == 0
    status = "REMOVED" if removed else "NOT removed"
    print(f'{char} {desc}: {status}')
