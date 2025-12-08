#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""測試 ng 韻母的轉換邏輯"""

import sys
from pathlib import Path

# 添加 data 目錄到路徑
sys.path.append(str(Path(__file__).parent / "data"))
from romanization_converter import RomanizationConverter

def test_ng_conversion():
    """測試 ng 韻母轉換規則"""

    test_cases = [
        # (輸入式, 預期莆拼)
        ("ng2", "ng2"),       # 零聲母 + ng → ng
        ("hng5", "hng5"),     # h 聲母 + ng → ng
        ("cng3", "zung3"),    # c 聲母 + ng → ung
        ("mng4", "mung4"),    # m 聲母 + ng → ung
        ("bng1", "bung1"),    # b 聲母 + ng → ung
        ("png2", "pung2"),    # p 聲母 + ng → ung
    ]

    print("測試 ng 韻母轉換規則：\n")

    all_passed = True
    for input_syl, expected_psp in test_cases:
        try:
            result_psp = RomanizationConverter.input_to_psp(input_syl)
            # 反向驗證
            result_back = RomanizationConverter.psp_to_input(result_psp)

            if result_psp == expected_psp and result_back == input_syl:
                print(f"✓ {input_syl} -> {result_psp} -> {result_back}")
            else:
                print(f"✗ {input_syl} -> {result_psp} (預期: {expected_psp})")
                all_passed = False
        except Exception as e:
            print(f"✗ {input_syl} 轉換失敗: {e}")
            all_passed = False

    return all_passed

if __name__ == "__main__":
    import io

    # 重定向到文件
    output = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = output

    result = test_ng_conversion()

    sys.stdout = old_stdout
    output_text = output.getvalue()

    # 寫入文件
    with open("D:/borhlang-ime/ng_conversion_test.txt", "w", encoding="utf-8") as f:
        f.write(output_text)
        if result:
            f.write("\n✅ 所有測試通過！")
        else:
            f.write("\n❌ 部分測試失敗")

    print("測試完成！結果已寫入 ng_conversion_test.txt")
    if result:
        print("✅ 所有測試通過！")
    else:
        print("❌ 部分測試失敗")
