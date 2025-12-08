#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""分析vocab_from_bible.yaml中的引號字符"""

with open('data/vocab_from_bible.yaml', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 檢查537和558行
problem_lines = [537, 558]

for line_num in problem_lines:
    if line_num <= len(lines):
        line = lines[line_num - 1]
        print(f"Line {line_num}: {line.rstrip()}")

        # 分析每個字符
        for i, char in enumerate(line):
            if ord(char) > 127:  # 非ASCII
                print(f"  Position {i}: '{char}' (U+{ord(char):04X})")

print("\n" + "="*60)
print("檢查原始聖經文本中的引號...")

with open('docs/hinghua_bible.txt', 'r', encoding='utf-8') as f:
    bible_lines = f.readlines()

# 找出所有包含引號的行
quote_chars = set()
for i, line in enumerate(bible_lines):
    for char in line:
        if char in '""\'"\'""':
            quote_chars.add((char, f'U+{ord(char):04X}'))

print("\n聖經文本中發現的引號字符：")
for char, code in sorted(quote_chars):
    print(f"  '{char}' {code}")
