#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""測試聖經詞彙轉換"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "tools"))
sys.path.append(str(Path(__file__).parent / "data"))

from convert_dict_v3 import DictConverter, LuaDictParser

# 載入維基詞典數據
cpx_file = Path("data/cpx-pron-data.lua")
cpx_data = LuaDictParser.parse_lua_dict(cpx_file)
print(f"載入了 {len(cpx_data)} 個漢字的讀音數據\n")

# 創建轉換器
converter = DictConverter(cpx_data)

# 測試聖經詞條
test_entries = [
    ('該隱', 'Gai1 yng3 gorng3', '300'),  # 3音節版本
    ('該隱', 'gai1 yng3', '300'),         # 2音節版本
    ('以諾', 'i3 dorh4', '300'),
    ('塞特', 'seh1 deh4', '300'),
    ('雅列', 'nga3 leh4', '300'),
]

print("=" * 60)
print("測試聖經詞彙轉換")
print("=" * 60)

for hanzi, pinyin, weight in test_entries:
    print(f"\n處理：{hanzi} {pinyin}")

    # 解析詞條
    chars, syllables = converter.parse_entry(hanzi, pinyin)
    print(f"  漢字：{chars}  ({len(chars)}個)")
    print(f"  音節：{syllables}  ({len(syllables)}個)")

    if len(chars) != len(syllables):
        print(f"  [X] 數量不匹配！跳過")
        continue

    # 轉換詞條
    result = converter.convert_entry(hanzi, pinyin, weight)

    if result:
        print(f"  [OK] 成功：{result[0]} {result[1]} {result[2]}")
    else:
        print(f"  [X] 轉換失敗")
        if converter.warnings:
            print(f"     警告：{converter.warnings[-1]}")

print("\n" + "=" * 60)
print("轉換統計：")
for key, value in converter.stats.items():
    print(f"  {key}: {value}")
