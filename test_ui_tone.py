#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "data"))

from romanization_converter import RomanizationConverter
from unicodedata import normalize as norm

# 測試 ui 韻母的聲調位置
test_cases = ["ui1", "ui2", "ui3", "ui4", "ui5"]

output = []
output.append("測試 ui 韻母聲調位置：\n")
for input_syl in test_cases:
    result = RomanizationConverter.input_to_buc(input_syl, output_tone6b=False, output_tone7b=False)
    # NFD 分解以查看調符位置
    result_nfd = norm('NFD', result[0])
    output.append(f"{input_syl} -> {result[0]}")
    output.append(f"  NFD: {repr(result_nfd)}")
    output.append("")

# 寫入文件
with open("test_ui_tone_result.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output))

print("測試完成，結果已寫入 test_ui_tone_result.txt")
