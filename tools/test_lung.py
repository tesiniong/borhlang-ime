#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "data"))

from convert_dict_v3 import BucRomanizer

rom = BucRomanizer()

# 測試 lung2 的轉換
print("測試 lung2 轉換：")
candidates = rom.psp_to_buc_candidates('lung2')
print(f"  候選數量: {len(candidates)}")
for cand in candidates:
    cand_rom = rom.buc_to_romanization(cand)
    print(f"  - {repr(cand)} → {cand_rom}")

# 測試 dung2 的轉換
print("\n測試 dung2 轉換：")
candidates = rom.psp_to_buc_candidates('dung2')
print(f"  候選數量: {len(candidates)}")
for cand in candidates:
    cand_rom = rom.buc_to_romanization(cand)
    print(f"  - {repr(cand)} → {cand_rom}")
