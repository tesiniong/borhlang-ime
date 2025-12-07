#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "data"))

from convert_dict_v3 import BucRomanizer, LuaDictParser
from unicodedata import normalize as norm

rom = BucRomanizer()
cpx_data = LuaDictParser.parse_lua_dict(Path(r'D:\borhlang-ime\data\cpx-pron-data.lua'))

# 測試 nao2 的直接轉換
candidates = rom.psp_to_buc_candidates('nao2')
print(f"nao2 candidates: {len(candidates)}")
for cand in candidates:
    cand_rom = rom.buc_to_romanization(cand)
    print(f"  {cand_rom}")

# 字典中頭的讀音
dict_prons = cpx_data.get('頭', [])
print(f"\nDict prons for 頭: {len(dict_prons)}")
for pron in dict_prons:
    pron_rom = rom.buc_to_romanization(pron)
    print(f"  {pron_rom}")

# 檢查是否匹配
print("\nDirect match check:")
for cand in candidates:
    cand_norm = norm('NFC', cand)
    for dict_pron in dict_prons:
        dict_pron_norm = norm('NFC', dict_pron)
        if cand_norm == dict_pron_norm:
            print(f"  MATCHED!")

# 測試反推候選
print("\nReverse case 1 (nasal_ng final + n initial):")
for init in ['d', 't', 'n', 'l', 'z', 'c', 's']:
    psp = init + 'ao2'
    candidates_rev = rom.psp_to_buc_candidates(psp)
    for cand in candidates_rev:
        cand_norm = norm('NFC', cand)
        cand_rom = rom.buc_to_romanization(cand)
        for dict_pron in dict_prons:
            dict_pron_norm = norm('NFC', dict_pron)
            if cand_norm == dict_pron_norm:
                print(f"  {psp} -> {cand_rom} MATCHED!")
