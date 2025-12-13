#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
興化平話字調符位置表
Hinghua Romanization Tone Mark Position Table

此表定義了每個韻母的調符插入位置（從 0 開始計數）
統一供所有轉換工具使用，確保一致性
"""

# 調符位置表
# 格式：{"輸入式韻母": 位置索引}
# 位置索引指應在第幾個字符後插入調符（從 0 開始）
TONE_POSITIONS = {
    # 單字母
    "a": 1,          # a → á
    "aa": 1,         # a̤ (aa) → á̤
    "e": 1,          # e → é
    "ee": 1,         # e̤ (ee) → é̤
    "oo": 1,         # o̤ (oo) → ó̤
    "i": 1,          # i → í
    "o": 1,          # o → ó
    "u": 1,          # u → ú
    "y": 1,          # ṳ (y) → ṳ́
    
    # 多字母
    "ai": 1,         # ai → ái
    "au": 1,         # au → áu
    "aau": 2,        # a̤u (aau) → á̤u
    "eo": 2,         # eo → eó
    "ia": 2,         # ia → iá
    "ioo": 2,        # io̤ (ioo) → ió̤ (ióo)
    "iu": 2,         # iu → iú
    "oi": 1,         # oi → ói
    "ua": 2,         # ua → uá
    "uai": 2,        # uai → uái
    "ui": 1,         # ui → úi

    # 鼻音韻
    "ng": 1,         # ng → ńg
    "ang": 1,        # ang → áng
    "eng": 1,        # eng → éng
    "ing": 1,        # ing → íng
    "eong": 2,       # eong → eóng
    "eeng": 1,       # e̤ng (eeng) → é̤ng
    "oong": 1,       # o̤ng (oong) → ó̤ng
    "iang": 2,       # iang → iáng
    "uang": 2,       # uang → uáng
    "yng": 1,        # ṳng (yng) → ṳ́ng
    "ioong": 2,      # io̤ng (ioong) → ió̤ng

    # 鼻化韻
    "ann": 1,        # aⁿ (ann) → áⁿ
    "aann": 1,       # a̤ⁿ (aann) → á̤ⁿ
    "eenn": 1,       # e̤ⁿ (eenn) → é̤ⁿ
    "oonn": 1,       # o̤ⁿ (oonn) → ó̤ⁿ
    "iann": 2,       # iaⁿ (iann) → iáⁿ
    "oinn": 1,       # oiⁿ (oinn) → óiⁿ
    "uann": 2,       # uaⁿ (uann) → uáⁿ
    "aaann": 2,      # a̤uⁿ (aaann) → á̤uⁿ
    "ioonn": 2,      # io̤ⁿ (ioonn) → ió̤ⁿ

    # 入聲韻
    "ah": 1,         # ah → a̍h
    "aih": 1,        # aih → a̍ih
    "aah": 1,        # a̤h (aah) → a̤̍h
    "aauh": 3,       # a̤uh (aauh) → a̤u̍h
    "eh": 1,         # eh → e̍h
    "eeh": 1,        # e̤h (eeh) → e̤̍h
    "eoh": 2,        # eoh → eo̍h
    "iah": 2,        # iah → ia̍h
    "ih": 1,         # ih → i̍h
    "iooh": 2,       # io̤h (iooh) → ióoh (ió̤h)
    "oih": 1,        # oih → o̍ih
    "ooh": 1,        # o̤h (ooh) → o̤̍h
    "uah": 2,        # uah → ua̍h
    "uh": 1,         # uh → u̍h
    "yh": 1,         # ṳh (yh) → ṳ̍h
}


def get_tone_position(final: str) -> int:
    """
    取得韻母的調符位置

    Args:
        final: 輸入式韻母（如 "ang", "ia", "ng"）

    Returns:
        調符應插入的位置索引（從 0 開始）
        如果韻母不在表中，返回 1（預設在第一個字符後）
    """
    return TONE_POSITIONS.get(final, 1)


def validate_tone_position(final: str, position: int) -> bool:
    """
    驗證調符位置是否正確

    Args:
        final: 輸入式韻母
        position: 位置索引

    Returns:
        True 如果位置正確，False 否則
    """
    expected = get_tone_position(final)
    return position == expected


# 元音優先級（用於找不到韻母時的備用邏輯）
# 按優先級從高到低排列
VOWEL_PRIORITY = ['a', 'o', 'e', 'i', 'u', 'y', 'n']


if __name__ == "__main__":
    # 測試
    print("調符位置表測試：")
    print("=" * 50)

    test_cases = [
        ("a", "á"),
        ("ng", "ńg"),
        ("ang", "áng"),
        ("ia", "iá"),
        ("eo", "eó"),
        ("ui", "uí"),
        ("aau", "á̤u"),
        ("iang", "iáng"),
        ("gui", "gúi"),
    ]

    for final, expected in test_cases:
        pos = get_tone_position(final)
        print(f"{final:10} → 位置 {pos} → {expected}")

    print(f"\n總共 {len(TONE_POSITIONS)} 個韻母定義")
