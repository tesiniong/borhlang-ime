#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""驗證調符位置是否正確"""

import sys
from pathlib import Path
from unicodedata import normalize as norm

# 添加 data 目錄到路徑
sys.path.append(str(Path(__file__).parent / "data"))
from romanization_converter import RomanizationConverter

def verify_tone_positions():
    """驗證各種音節的調符位置"""

    test_cases = [
        # (輸入式, 預期的調符應該在哪個元音上)
        ("sa2", "a"),      # 單元音
        ("saa2", "a̤"),    # 特殊元音
        ("sia2", "i"),     # i-介音：調符應在 i 上
        ("sioong5", "o̤"), # io̤ng：調符應在第一個 o（即 o̤）上
        ("cheng2", "e"),   # 單元音
        ("aauh4", "a̤"),   # a̤uh：調符應在第三個位置（a̤ 之後）
    ]

    print("驗證調符位置：\n")

    for input_syl, expected_vowel in test_cases:
        buc_forms = RomanizationConverter.input_to_buc(input_syl,
                                                         output_tone6b=False,
                                                         output_tone7b=False)
        buc = buc_forms[0]

        # NFD 分解以檢查調符位置
        buc_nfd = norm('NFD', buc)

        # 檢查調符是否在預期元音後
        found = False
        for i, char in enumerate(buc_nfd):
            if char in ['\u0301', '\u0302', '\u030D', '\u0304']:  # 調符
                if i > 0:
                    prev_char = buc_nfd[i-1]
                    # 檢查是否為複合字符（如 a̤）
                    if i >= 2 and buc_nfd[i-2:i] == norm('NFD', expected_vowel):
                        found = True
                        print(f"✓ {input_syl} -> {buc} (調符在 {expected_vowel} 上)")
                        break
                    elif prev_char == expected_vowel[0]:
                        found = True
                        print(f"✓ {input_syl} -> {buc} (調符在 {expected_vowel} 上)")
                        break

        if not found and input_syl[-1] not in ['1', '6']:  # 第1、6調可能無調符
            print(f"✗ {input_syl} -> {buc} (預期調符在 {expected_vowel} 上)")

    print("\n檢查多音節詞：\n")

    multi_syllable_tests = [
        ("po2 cheng2", "莆田"),
        ("sioong5 daa4", "上帝"),
    ]

    for input_word, hanzi in multi_syllable_tests:
        syllables = input_word.split()
        buc_syllables = []

        for syl in syllables:
            buc_forms = RomanizationConverter.input_to_buc(syl,
                                                             output_tone6b=False,
                                                             output_tone7b=False)
            buc_syllables.append(buc_forms[0])

        buc_word = '-'.join(buc_syllables)
        print(f"{hanzi}: {input_word} -> {buc_word}")

if __name__ == "__main__":
    import io
    import sys

    # 重定向輸出到文件
    output = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = output

    verify_tone_positions()

    sys.stdout = old_stdout
    result = output.getvalue()

    # 寫入文件
    with open("D:/borhlang-ime/tone_position_verification.txt", "w", encoding="utf-8") as f:
        f.write(result)

    print("驗證完成！結果已寫入 tone_position_verification.txt")
