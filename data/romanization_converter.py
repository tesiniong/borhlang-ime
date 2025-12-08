#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
莆仙語羅馬字系統轉換器
Puxian Romanization System Converter

支援三種羅馬字系統的雙向轉換：
1. 莆仙話拼音（Pouseng Ping'ing, PSP）- 現代標準拼音
2. 輸入式平話字 - 純 ASCII 版本
3. 興化平話字（Báⁿ-uā-ci̍, BUC）- 19世紀傳教士系統

轉換路徑：
    PSP <-> 輸入式 <-> BUC
"""

import re
from typing import List, Tuple, Optional
from unicodedata import normalize as norm


class RomanizationConverter:
    """莆仙語羅馬字系統轉換器"""

    # ========== 聲母對照表 ==========
    # 格式：{"莆拼": ("輸入式", "平話字")}
    INITIALS = {
        "b": ("b", "b"),
        "p": ("p", "p"),
        "m": ("m", "m"),
        "d": ("d", "d"),
        "t": ("t", "t"),
        "n": ("n", "n"),
        "l": ("l", "l"),
        "g": ("g", "g"),
        "k": ("k", "k"),
        "ng": ("ng", "ng"),
        "h": ("h", "h"),
        "z": ("c", "c"),      # PSP z -> 輸入式/BUC c
        "c": ("ch", "ch"),    # PSP c -> 輸入式/BUC ch
        "s": ("s", "s"),
        "": ("", "")          # 零聲母
    }

    # 反向查找表：輸入式 -> 莆拼
    INITIALS_INPUT_TO_PSP = {
        "b": "b", "p": "p", "m": "m",
        "d": "d", "t": "t", "n": "n", "l": "l",
        "g": "g", "k": "k", "ng": "ng", "h": "h",
        "c": "z",     # 輸入式 c -> PSP z（需檢查是否為 ch）
        "ch": "c",    # 輸入式 ch -> PSP c
        "s": "s",
        "": ""
    }

    # ========== 韻母對照表：莆拼 -> 輸入式 ==========
    # 格式：{"PSP韻母": "輸入式韻母"}
    FINALS_PSP_TO_INPUT = {
        # 單元音
        "a": "a",
        "ae": "e",
        "e": "aa",         # PSP e -> 輸入式 aa (a̤)
        "i": "i",
        "ou": "o",         # PSP ou -> 輸入式 o
        "u": "u",
        "y": "y",          # PSP y -> 輸入式 y (ṳ)
        "ung": "ng",       # PSP ung -> 輸入式 ng (用於非零聲母/h的情況)

        # 複韻母
        "ai": "ai",
        "ao": "au",        # PSP ao -> 輸入式 au
        "uei": "oi",       # PSP uei -> 輸入式 oi
        "ui": "ui",

        # i-介音複韻
        "ia": "ia",
        "ieng": "iang",    # PSP ieng -> 輸入式 iang
        "ieo": "aauh",     # PSP ieo -> 輸入式 aauh (a̤uh)
        "iu": "iu",

        # u-介音複韻
        "ua": "ua",

        # 特殊韻母
        "o": "eo",         # PSP o -> 輸入式 eo
        "oe": "ee",        # PSP oe -> 輸入式 ee (e̤)
        "or": "oo",        # PSP or -> 輸入式 oo (o̤)

        # 鼻音韻尾
        "ang": "ang",
        "eng": "eng",
        "ing": "ing",
        "ong": "eong",     # PSP ong -> 輸入式 eong
        "oeng": "eeng",    # PSP oeng -> 輸入式 eeng (e̤ng)
        "orng": "oong",    # PSP orng -> 輸入式 oong (o̤ng)
        "uang": "uang",

        # 入聲韻尾
        "ah": "ah",
        "aeh": "eh",
        "eh": "aah",       # PSP eh -> 輸入式 aah (a̤h)
        "ih": "ih",
        "oh": "eoh",       # PSP oh -> 輸入式 eoh
        "oeh": "eeh",      # PSP oeh -> 輸入式 eeh (e̤h)
        "orh": "ooh",      # PSP orh -> 輸入式 ooh (o̤h)
        "uah": "uah",
        "uh": "uh",
        "yh": "yh",        # PSP yh -> 輸入式 yh (ṳh)

        # y-介音韻母
        "yor": "ioo",      # PSP yor -> 輸入式 ioo (io̤)
        "yorh": "iooh",    # PSP yorh -> 輸入式 iooh (io̤h)
        "yorng": "ioong",  # PSP yorng -> 輸入式 ioong (io̤ng)

        # 單獨鼻音
        "ng": "ng",

        # 鼻化韻（莆田話已無鼻化，但為完整性保留）
        # 注意：這些會在轉換時丟失鼻化標記
    }

    # 容錯表：錯誤的PSP拼法 -> 正確的PSP拼法
    WRONG_FINALS = {
        "au": "ao",
        "iang": "ieng",
        "ieu": "ieo",
        "iau": "ieo",
        "iao": "ieo",
        "uai": "uei",
        "ue": "uei",
        "yeh": "yoeh",
        "yeng": "yoeng",
        "yo": "yor",
        "yoh": "yorh",
        "yong": "yorng"
    }

    # ========== 韻母對照表：輸入式 -> 莆拼 ==========
    # 格式：{"輸入式韻母": "PSP韻母"}
    FINALS_INPUT_TO_PSP = {
        # 單元音
        "a": "a",
        "e": "ae",
        "aa": "e",         # 輸入式 aa (a̤) -> PSP e
        "i": "i",
        "o": "ou",         # 輸入式 o -> PSP ou
        "u": "u",
        "y": "y",

        # 複韻母
        "ai": "ai",
        "au": "ao",
        "oi": "uei",
        "ui": "ui",

        # i-介音複韻
        "ia": "ia",
        "iang": "ieng",
        "iu": "iu",

        # u-介音複韻
        "ua": "ua",

        # 特殊韻母
        "eo": "o",
        "ee": "oe",
        "oo": "or",

        # 鼻音韻尾
        "ang": "ang",
        "eng": "eng",
        "ing": "ing",
        "eong": "ong",
        "eeng": "oeng",
        "oong": "orng",
        "uang": "uang",

        # 入聲韻尾
        "ah": "ah",
        "eh": "aeh",
        "aah": "eh",
        "ih": "ih",
        "eoh": "oh",
        "eeh": "oeh",
        "ooh": "orh",
        "uah": "uah",
        "uh": "uh",
        "yh": "yh",

        # y-介音韻母
        "ioo": "yor",
        "iooh": "yorh",
        "ioong": "yorng",

        # 單獨鼻音
        "ng": "ng",

        # 鼻化韻 -> 莆拼（丟失鼻化）
        "ann": "a",        # aⁿ -> a
        "aann": "e",       # a̤ⁿ -> e
        "eenn": "oe",      # e̤ⁿ -> oe
        "iann": "ia",      # iaⁿ -> ia
        "oonn": "or",      # o̤ⁿ -> or
        "oinn": "uei",     # oiⁿ -> uei
        "uann": "ua",      # uaⁿ -> ua
        "aaunn": "ieo",    # a̤uⁿ -> ieo
        "ioonn": "yor",    # io̤ⁿ -> yor

        # 複合入聲韻
        "aauh": "ieo",     # a̤uh -> ieo（注意：無h版本）
        "aih": "ai",       # 簡化處理
    }

    # ========== 特殊字符映射：輸入式 <-> 平話字 ==========
    BUC_TO_INPUT_CHARS = {
        "a̤": "aa",
        "e̤": "ee",
        "o̤": "oo",
        "ṳ": "y",
        "ⁿ": "nn"
    }

    INPUT_TO_BUC_CHARS = {
        "aa": "a̤",
        "ee": "e̤",
        "oo": "o̤",
        "y": "ṳ",
        "nn": "ⁿ"
    }

    # ========== 聲調符號映射 ==========
    # 調號 -> Unicode 組合符號
    TONE_MARKS = {
        "1": "",           # 陰平：無標記
        "2": "\u0301",     # 陽平：́ (acute)
        "3": "\u0302",     # 上聲：̂ (circumflex)
        "4": "\u030D",     # 陰去：̍ (vertical line above)
        "5": "\u0304",     # 陽去：̄ (macron)
        "6": "",           # 陰入：無標記（或 macron，視韻尾而定）
        "7": "\u030D",     # 陽入：̍ (vertical line above，視韻尾而定)
    }

    # Unicode 組合符號 -> 調號（基礎映射）
    TONE_MARKS_REVERSE = {
        "": "1",
        "\u0301": "2",     # acute
        "\u0302": "3",     # circumflex
        "\u030D": "4",     # vertical line（需根據韻尾判斷是4還是7）
        "\u0304": "5",     # macron（需根據韻尾判斷是5還是6）
    }

    # ========== 調符位置表 ==========
    # 格式：{"輸入式韻母": 位置索引}
    # 位置索引指應在第幾個字符後插入調符
    TONE_POSITIONS = {
        "a": 1, "ann": 1, "ah": 1, "e": 1,
        "ai": 1, "aih": 1, "ang": 1, "au": 1,
        "aa": 1, "aann": 1, "aah": 1,  # a̤ 系列
        "eh": 1, "eng": 1,
        "i": 1, "ih": 1, "ing": 1,
        "ia": 2, "iann": 2, "iah": 2, "iang": 2,
        "aauh": 3, "aaunn": 3,  # a̤u 系列
        "iu": 2,
        "ng": 1,
        "eo": 2, "eoh": 2, "eong": 2,
        "ee": 1, "eenn": 1, "eeh": 1, "eeng": 1,  # e̤ 系列
        "oo": 1, "oonn": 1, "ooh": 1, "oong": 1,  # o̤ 系列
        "o": 1,
        "u": 1, "uh": 1, "ui": 1,
        "ua": 2, "uann": 2, "uah": 2, "uang": 2,
        "oi": 1, "oinn": 1, "oih": 1, "uai": 2,
        "y": 1, "yh": 1, "yng": 1,  # ṳ 系列
        "ioo": 2, "ioonn": 2, "iooh": 2, "ioong": 2  # io̤ 系列
    }

    # ========== 第6B調和第7B調的特定韻母 ==========
    # 第6B調：所有陰聲韻（以元音結尾的韻母）
    TONE6B_FINALS_INPUT = {
        "a", "aa", "e", "ee", "i", "o", "oo", "u", "y",
        "ai", "au", "eo", "ia", "iu", "oi", "ua", "ui", "ioo"
    }

    # 第7B調：特定韻母（PSP不以h結尾但可能對應BUC的h結尾）
    TONE7B_FINALS_INPUT = {
        "a",    # ah*
        "aa",   # a̤h*
        "i",    # ih*
        "ia",   # iah*
        "eo",   # eoh*
        "oo",   # o̤h*
        "ua",   # uah*
        "oi",   # oih*
        "ioo"   # io̤h*
    }

    # ========== 核心轉換方法 ==========

    @staticmethod
    def psp_to_input(syllable: str) -> str:
        """
        莆拼 -> 輸入式

        Args:
            syllable: 莆拼音節（如 "pou2", "syorng5", "de4"）

        Returns:
            輸入式音節（如 "po2", "sioong5", "daa4"）
        """
        # 處理大小寫（專有名詞會大寫）
        syllable = syllable.lower()

        # 驗證格式
        if not syllable or not syllable[-1].isdigit():
            raise ValueError(f"無效的莆拼格式：{syllable}（必須以數字結尾）")

        # 提取聲調
        tone = syllable[-1]
        syllable_no_tone = syllable[:-1]

        # 提取聲母
        initial_psp = RomanizationConverter._extract_initial_psp(syllable_no_tone)
        final_psp = syllable_no_tone[len(initial_psp):]

        # 容錯處理
        if final_psp in RomanizationConverter.WRONG_FINALS:
            final_psp = RomanizationConverter.WRONG_FINALS[final_psp]

        # 轉換聲母
        if initial_psp not in RomanizationConverter.INITIALS:
            raise ValueError(f"未知的莆拼聲母：{initial_psp}")
        initial_input = RomanizationConverter.INITIALS[initial_psp][0]

        # 轉換韻母
        if final_psp not in RomanizationConverter.FINALS_PSP_TO_INPUT:
            raise ValueError(f"未知的莆拼韻母：{final_psp}")
        final_input = RomanizationConverter.FINALS_PSP_TO_INPUT[final_psp]

        return initial_input + final_input + tone

    @staticmethod
    def input_to_psp(syllable: str) -> str:
        """
        輸入式 -> 莆拼

        Args:
            syllable: 輸入式音節（如 "po2", "sioong5", "daa4"）

        Returns:
            莆拼音節（如 "pou2", "syorng5", "de4"）
        """
        # 處理大小寫
        syllable = syllable.lower()

        # 驗證格式
        if not syllable or not syllable[-1].isdigit():
            raise ValueError(f"無效的輸入式格式：{syllable}（必須以數字結尾）")

        # 提取聲調
        tone = syllable[-1]
        syllable_no_tone = syllable[:-1]

        # 提取聲母
        initial_input = RomanizationConverter._extract_initial_input(syllable_no_tone)
        final_input = syllable_no_tone[len(initial_input):]

        # 轉換聲母
        if initial_input == "ch":
            initial_psp = "c"
        elif initial_input == "c":
            initial_psp = "z"
        elif initial_input in RomanizationConverter.INITIALS_INPUT_TO_PSP:
            initial_psp = RomanizationConverter.INITIALS_INPUT_TO_PSP[initial_input]
        else:
            raise ValueError(f"未知的輸入式聲母：{initial_input}")

        # 特殊處理：ng 韻母的轉換
        # 零聲母或 h 聲母 + ng → ng (保持)
        # 其他聲母 + ng → ung
        if final_input == "ng":
            if initial_input in ["", "h"]:
                final_psp = "ng"
            else:
                final_psp = "ung"
        else:
            # 轉換韻母
            if final_input not in RomanizationConverter.FINALS_INPUT_TO_PSP:
                raise ValueError(f"未知的輸入式韻母：{final_input}")
            final_psp = RomanizationConverter.FINALS_INPUT_TO_PSP[final_input]

        return initial_psp + final_psp + tone

    @staticmethod
    def input_to_buc(syllable: str, output_tone6b: bool = True,
                     output_tone7b: bool = True) -> List[str]:
        """
        輸入式 -> 真平話字

        Args:
            syllable: 輸入式音節（如 "sa5", "sa6", "sa2", "sah7"）
            output_tone6b: 是否同時輸出第6B調的變體（sā 和 sā*）
            output_tone7b: 是否同時輸出第7B調的變體（sá 和 sa̍h*）

        Returns:
            平話字列表（可能包含多個變體）
        """
        # 處理大小寫
        syllable = syllable.lower()

        # 驗證格式
        if not syllable or not syllable[-1].isdigit():
            raise ValueError(f"無效的輸入式格式：{syllable}（必須以數字結尾）")

        # 提取聲調
        tone = syllable[-1]
        syllable_no_tone = syllable[:-1]

        # 提取聲母和韻母
        initial = RomanizationConverter._extract_initial_input(syllable_no_tone)
        final_input = syllable_no_tone[len(initial):]

        # 轉換輸入式韻母為平話字韻母
        final_buc = RomanizationConverter._input_final_to_buc(final_input)

        # 判斷韻母是否為陰聲韻（以元音結尾）
        is_open_final = not (final_input.endswith("ng") or
                             final_input.endswith("h") or
                             final_input.endswith("nn"))

        # 生成候選列表
        candidates = []

        # 處理不同聲調
        if tone == "6":
            # 第6調（陰入）
            if final_input.endswith("h"):
                # 6A：h結尾，無調符
                candidates.append(norm('NFC', initial + final_buc))
            else:
                # 6B：陰聲韻，macron
                final_with_tone = RomanizationConverter._add_tone_mark(
                    final_buc, final_input, RomanizationConverter.TONE_MARKS["5"]
                )
                syllable = norm('NFC', initial + final_with_tone)
                candidates.append(syllable)

                # 如果韻母在特定列表且參數為True，添加帶星號的變體
                if output_tone6b and final_input in RomanizationConverter.TONE6B_FINALS_INPUT:
                    candidates.append(syllable + "*")

        elif tone == "7":
            # 第7調（陽入）
            if final_input.endswith("h"):
                # 7A：h結尾，vertical line
                final_with_tone = RomanizationConverter._add_tone_mark(
                    final_buc, final_input, RomanizationConverter.TONE_MARKS["7"]
                )
                candidates.append(norm('NFC', initial + final_with_tone))
            else:
                # 7B：陰聲韻，acute（讀音同第2調）
                final_with_tone = RomanizationConverter._add_tone_mark(
                    final_buc, final_input, RomanizationConverter.TONE_MARKS["2"]
                )
                syllable = norm('NFC', initial + final_with_tone)
                candidates.append(syllable)

                # 如果韻母在特定列表且參數為True，添加帶星號的變體
                if output_tone7b and final_input in RomanizationConverter.TONE7B_FINALS_INPUT:
                    # 7B變體：加h + vertical line + 星號
                    final_with_h_tone = RomanizationConverter._add_tone_mark(
                        final_buc + "h", final_input + "h",
                        RomanizationConverter.TONE_MARKS["7"]
                    )
                    candidates.append(norm('NFC', initial + final_with_h_tone + "*"))

        elif tone == "2":
            # 第2調（陽平）
            final_with_tone = RomanizationConverter._add_tone_mark(
                final_buc, final_input, RomanizationConverter.TONE_MARKS["2"]
            )
            candidates.append(norm('NFC', initial + final_with_tone))

        elif tone == "5":
            # 第5調（陽去）
            final_with_tone = RomanizationConverter._add_tone_mark(
                final_buc, final_input, RomanizationConverter.TONE_MARKS["5"]
            )
            candidates.append(norm('NFC', initial + final_with_tone))

        else:
            # 第1、3、4調：標準處理
            tone_mark = RomanizationConverter.TONE_MARKS[tone]
            if tone_mark:
                final_with_tone = RomanizationConverter._add_tone_mark(
                    final_buc, final_input, tone_mark
                )
                candidates.append(norm('NFC', initial + final_with_tone))
            else:
                candidates.append(norm('NFC', initial + final_buc))

        return candidates if candidates else [norm('NFC', initial + final_buc)]

    @staticmethod
    def buc_to_input(syllable: str) -> str:
        """
        真平話字 -> 輸入式

        Args:
            syllable: 平話字音節（如 "sā", "sā*", "sá", "sa̍h*"）

        Returns:
            輸入式音節（如 "sa5", "sa6", "sa2", "sa7"）
        """
        # 移除星號標記（記錄是否有星號）
        has_star = syllable.endswith("*")
        syllable_clean = syllable.rstrip("*")

        # NFD分解以識別調符
        syllable_nfd = norm('NFD', syllable_clean)

        # 提取調符
        tone_mark = ""
        for char in syllable_nfd:
            if char in RomanizationConverter.TONE_MARKS_REVERSE:
                tone_mark = char
                break

        # 移除調符
        syllable_no_tone = syllable_nfd.replace(tone_mark, "")
        syllable_no_tone = norm('NFC', syllable_no_tone)

        # 判斷基礎調號
        if tone_mark in RomanizationConverter.TONE_MARKS_REVERSE:
            tone = RomanizationConverter.TONE_MARKS_REVERSE[tone_mark]
        else:
            tone = "1"  # 無標記預設為第1調

        # 檢查韻尾
        ends_with_h = syllable_no_tone.endswith("h")

        # 根據韻尾和星號調整調號
        if tone == "5":  # macron
            if ends_with_h:
                tone = "6"  # macron + h = 第6調
            elif has_star:
                tone = "6"  # macron + * = 第6B調
            # 否則保持第5調

        elif tone == "4":  # vertical line
            if ends_with_h:
                if has_star:
                    tone = "7"  # vertical + h + * = 第7B調
                else:
                    tone = "7"  # vertical + h = 第7調
            # 否則保持第4調

        elif tone == "1":  # 無標記
            if ends_with_h:
                tone = "6"  # 無標記 + h = 第6調（預設）
            # 否則保持第1調

        # 提取聲母和韻母
        initial = RomanizationConverter._extract_initial_input(syllable_no_tone)
        final_buc = syllable_no_tone[len(initial):]

        # 轉換平話字韻母為輸入式韻母
        final_input = RomanizationConverter._buc_final_to_input(final_buc)

        return initial + final_input + tone

    # ========== 輔助方法 ==========

    @staticmethod
    def _extract_initial_psp(syllable: str) -> str:
        """提取莆拼聲母"""
        # 特殊處理：ng 作為單獨韻母時，聲母為空
        if syllable == "ng":
            return ""
        elif syllable.startswith("ng") and len(syllable) > 2:
            return "ng"
        elif syllable.startswith("ch"):
            return "ch"
        elif syllable and syllable[0] in "bpmgkhdtnlcsz":
            return syllable[0]
        else:
            return ""  # 零聲母

    @staticmethod
    def _extract_initial_input(syllable: str) -> str:
        """提取輸入式聲母"""
        # 特殊處理：ng 作為單獨韻母時，聲母為空
        if syllable == "ng":
            return ""
        elif syllable.startswith("ng") and len(syllable) > 2:
            return "ng"
        elif syllable.startswith("ch"):
            return "ch"
        elif syllable and syllable[0] in "bpmgkhdtnlcs":
            return syllable[0]
        else:
            return ""  # 零聲母

    @staticmethod
    def _input_final_to_buc(final_input: str) -> str:
        """將輸入式韻母轉換為平話字韻母"""
        result = final_input
        # 按照長度從長到短替換，避免誤替換
        for input_char, buc_char in sorted(
            RomanizationConverter.INPUT_TO_BUC_CHARS.items(),
            key=lambda x: len(x[0]),
            reverse=True
        ):
            result = result.replace(input_char, buc_char)
        return result

    @staticmethod
    def _buc_final_to_input(final_buc: str) -> str:
        """將平話字韻母轉換為輸入式韻母"""
        result = final_buc
        # NFD分解
        result = norm('NFD', result)
        # 移除所有調符
        for tone_mark in RomanizationConverter.TONE_MARKS_REVERSE.keys():
            if tone_mark:
                result = result.replace(tone_mark, "")
        result = norm('NFC', result)

        # 替換特殊字符
        for buc_char, input_char in sorted(
            RomanizationConverter.BUC_TO_INPUT_CHARS.items(),
            key=lambda x: len(x[0]),
            reverse=True
        ):
            result = result.replace(buc_char, input_char)
        return result

    @staticmethod
    def _add_tone_mark(buc_final: str, final_input: str, tone_mark: str) -> str:
        """
        在平話字韻母的正確位置添加調符

        Args:
            buc_final: 平話字韻母（無調符）
            final_input: 對應的輸入式韻母（用於查找位置）
            tone_mark: 調符（Unicode組合符號）

        Returns:
            添加調符後的平話字韻母（NFD形式）
        """
        if not tone_mark:
            return buc_final

        # 查找調符位置
        if final_input not in RomanizationConverter.TONE_POSITIONS:
            # 如果找不到，預設放在第一個字符後
            position = 1
        else:
            position = RomanizationConverter.TONE_POSITIONS[final_input]

        # NFD分解
        final_nfd = norm('NFD', buc_final)

        # 在指定位置插入調符
        if position <= len(final_nfd):
            result = final_nfd[:position] + tone_mark + final_nfd[position:]
        else:
            result = final_nfd + tone_mark

        return result


# ========== 測試代碼 ==========
if __name__ == "__main__":
    converter = RomanizationConverter()

    print("=== 莆拼 <-> 輸入式 測試 ===")
    test_cases_psp = [
        ("pou2", "莆田"),
        ("syorng5", "上"),
        ("de4", "帝"),
        ("ka5", "教"),
    ]

    for psp, meaning in test_cases_psp:
        try:
            input_form = converter.psp_to_input(psp)
            back_to_psp = converter.input_to_psp(input_form)
            print(f"{psp} ({meaning}) -> {input_form} -> {back_to_psp}")
        except Exception as e:
            print(f"{psp} 轉換失敗: {e}")

    print("\n=== 輸入式 <-> 平話字 測試 ===")
    test_cases_input = [
        ("sa5", "第5調"),
        ("sa6", "第6B調"),
        ("sah6", "第6A調"),
        ("sa2", "第2調"),
        ("sa7", "第7B調"),
        ("sah7", "第7A調"),
    ]

    for input_syl, meaning in test_cases_input:
        try:
            buc_forms = converter.input_to_buc(input_syl, output_tone6b=True, output_tone7b=True)
            print(f"{input_syl} ({meaning}) -> {buc_forms}")

            # 測試反向轉換
            for buc in buc_forms:
                back = converter.buc_to_input(buc)
                print(f"  {buc} -> {back}")
        except Exception as e:
            print(f"{input_syl} 轉換失敗: {e}")
