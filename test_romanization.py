#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""測試羅馬字轉換模組"""

import sys
from pathlib import Path

# 添加 data 目錄到路徑
sys.path.append(str(Path(__file__).parent / "data"))
from romanization_converter import RomanizationConverter

def test_psp_input_conversion():
    """測試莆拼 <-> 輸入式轉換"""
    print("=== 莆拼 <-> 輸入式 測試 ===\n")

    test_cases = [
        ("pou2", "莆田"),
        ("leng2", "田"),
        ("syorng5", "上"),
        ("de4", "帝"),
        ("ka5", "教"),
        ("sieo6", "少"),
        ("ng2", "黃"),
    ]

    results = []
    for psp, meaning in test_cases:
        try:
            input_form = RomanizationConverter.psp_to_input(psp)
            back_to_psp = RomanizationConverter.input_to_psp(input_form)
            status = "✓" if back_to_psp == psp else "✗"
            results.append(f"{status} {psp} ({meaning}) -> {input_form} -> {back_to_psp}")
        except Exception as e:
            results.append(f"✗ {psp} ({meaning}) 轉換失敗: {e}")

    return "\n".join(results)

def test_input_buc_conversion():
    """測試輸入式 <-> 平話字轉換"""
    print("=== 輸入式 <-> 平話字 測試 ===\n")

    test_cases = [
        ("sa1", "第1調（陰平）"),
        ("sa2", "第2調（陽平）"),
        ("sa3", "第3調（上聲）"),
        ("sa4", "第4調（陰去）"),
        ("sa5", "第5調（陽去）"),
        ("sa6", "第6B調（陰入-陰聲韻）"),
        ("sah6", "第6A調（陰入-入聲韻）"),
        ("sa7", "第7B調（陽入-陰聲韻）"),
        ("sah7", "第7A調（陽入-入聲韻）"),
    ]

    results = []

    # 測試 1: 帶變體參數
    results.append("【測試組1：輸出所有變體】")
    for input_syl, meaning in test_cases:
        try:
            buc_forms = RomanizationConverter.input_to_buc(
                input_syl, output_tone6b=True, output_tone7b=True
            )
            results.append(f"\n{input_syl} ({meaning}):")
            for buc in buc_forms:
                back = RomanizationConverter.buc_to_input(buc)
                status = "✓" if back == input_syl else "✗"
                results.append(f"  {status} {repr(buc)} -> {back}")
        except Exception as e:
            results.append(f"  ✗ 轉換失敗: {e}")

    # 測試 2: 不輸出變體
    results.append("\n\n【測試組2：不輸出變體】")
    for input_syl, meaning in test_cases:
        try:
            buc_forms = RomanizationConverter.input_to_buc(
                input_syl, output_tone6b=False, output_tone7b=False
            )
            results.append(f"\n{input_syl} ({meaning}): {repr(buc_forms)}")
        except Exception as e:
            results.append(f"  ✗ 轉換失敗: {e}")

    return "\n".join(results)

def test_special_cases():
    """測試特殊案例"""
    print("=== 特殊案例測試 ===\n")

    test_cases = [
        # 鼻化韻丟失
        ("aann2", "a̤ⁿ丟失鼻化"),
        ("iann5", "iaⁿ丟失鼻化"),

        # 複韻母
        ("aauh4", "a̤uh 複韻母"),
        ("ioong5", "io̤ng 複韻母"),

        # 容錯測試（通過莆拼）
    ]

    results = []
    for input_syl, description in test_cases:
        try:
            # 輸入式 -> 莆拼
            psp = RomanizationConverter.input_to_psp(input_syl)
            # 莆拼 -> 輸入式（應該回得去）
            back = RomanizationConverter.psp_to_input(psp)
            status = "✓" if back == input_syl else "✗"
            results.append(f"{status} {input_syl} ({description}) -> {psp} -> {back}")
        except Exception as e:
            results.append(f"✗ {input_syl} ({description}) 轉換失敗: {e}")

    return "\n".join(results)

def main():
    output = []

    output.append(test_psp_input_conversion())
    output.append("\n" + "="*60 + "\n")
    output.append(test_input_buc_conversion())
    output.append("\n" + "="*60 + "\n")
    output.append(test_special_cases())

    # 寫入文件
    result_text = "\n".join(output)
    with open("D:/borhlang-ime/test_results.txt", "w", encoding="utf-8") as f:
        f.write(result_text)

    print("測試完成！結果已寫入 test_results.txt")
    print("\n摘要：")
    print(result_text[:500] + "...\n（完整結果請查看 test_results.txt）")

if __name__ == "__main__":
    main()
