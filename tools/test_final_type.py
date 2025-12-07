#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "data"))

from convert_dict_v3 import AssimilationReverser

reverser = AssimilationReverser()

# 測試 geeng2 和 geong2 的韻尾類型
test_cases = ['geeng2', 'geong2', 'saaunn1', 'ci5', 'su5']

for rom in test_cases:
    final_type = reverser.get_final_type(rom)
    print(f"{rom:12s} -> {final_type}")
