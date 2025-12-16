#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
莆仙話拼音詞庫轉換為興化平話字詞庫（拼式版本）v3
Convert Puxian Pinyin dictionary to Báⁿ-uā-ci̍ dictionary (romanization version)

本版本實作完整的聲母類化反推邏輯
"""

import re
import sys
from pathlib import Path
from unicodedata import normalize as norm
from typing import List, Dict, Tuple, Optional, Set

# 導入轉換模組
sys.path.append(str(Path(__file__).parent.parent / "data"))
from romanization_converter import RomanizationConverter
from psp_to_buc import buc_finals, buc_tones  # 仍需要用於候選生成


class BucRomanizer:
    """平話字拼式轉換器（包裝 RomanizationConverter）"""

    @staticmethod
    def psp_to_buc_candidates(psp_syllable: str) -> List[str]:
        """
        將莆仙話拼音音節轉換為平話字候選列表（可能有多個）

        Args:
            psp_syllable: 莆仙話拼音音節（如 ka5, yor3）

        Returns:
            平話字列表（如 ['kā', 'kāⁿ']）
        """
        # 驗證輸入格式
        if not psp_syllable or not psp_syllable[-1].isdigit():
            return []

        # 解析聲母和韻母+聲調
        if psp_syllable.startswith("ng") and len(psp_syllable) == 3:
            initial_psp = ""
            finaltone = psp_syllable
        elif psp_syllable.startswith("ng") or psp_syllable.startswith("ch"):
            initial_psp = psp_syllable[:2]
            finaltone = psp_syllable[2:]
        elif psp_syllable[0] in 'bpmgkhdtnlcsz':
            initial_psp = psp_syllable[0]
            finaltone = psp_syllable[1:]
        else:
            initial_psp = ""
            finaltone = psp_syllable

        # 分離韻母和聲調
        final_psp = finaltone[:-1]
        tone_psp = finaltone[-1]

        # 驗證聲調
        if tone_psp not in buc_tones:
            return []

        # 轉換聲母：莆拼 → 平話字
        initial_map = {
            'b': 'b', 'p': 'p', 'm': 'm',
            'd': 'd', 't': 't', 'n': 'n', 'l': 'l',
            'g': 'g', 'k': 'k', 'ng': 'ng', 'h': 'h',
            'z': 'c', 'c': 'ch', 's': 's',
            '': ''  # 零聲母
        }

        if initial_psp not in initial_map:
            return []

        buc_initial = initial_map[initial_psp]

        # 處理常見的韻母變體
        final_map = {
            "au": "ao",
            "iang": "ieng",
            "ieu": "ieo",
            "iau": "ieo",
            "iao": "ieo",
            "uai": "ue",
            "uei": "ue",
            "yoeh": "yeh",
            "yoeng": "yeng",
            "yor": "yo",
            "yorh": "yoh",
            "yorng": "yong"
        }

        if final_psp in final_map:
            final_psp = final_map[final_psp]

        # 獲取韻母候選
        if final_psp not in buc_finals:
            return []

        buc_final_candidates = buc_finals[final_psp]

        # 獲取聲調標記
        tone_mark = buc_tones[tone_psp]

        # 生成所有候選
        candidates = []
        for final_info in buc_final_candidates:
            buc_final = final_info[0]

            # 構建平話字：聲母 + 韻母 + 聲調
            buc_syllable = buc_initial + buc_final

            # 添加聲調標記（NFD 形式）
            if tone_mark:
                # 找到主元音添加聲調標記
                buc_syllable = BucRomanizer.add_tone_mark(buc_syllable, tone_mark)

            candidates.append(norm('NFC', buc_syllable))

        return candidates

    @staticmethod
    def add_tone_mark(syllable: str, tone_mark: str) -> str:
        """在音節的主元音上添加聲調標記"""
        # NFD 分解
        syllable = norm('NFD', syllable)

        # 元音優先級規則：
        # 1. 如果有 a/o/e，按 a > o > e 優先級標記
        # 2. 否則，標在第一個元音上（i, u, ṳ）
        # 3. 如果沒有元音（如 ng, m），標在鼻音輔音上

        high_priority_vowels = ['a', 'o', 'e']
        all_vowels = ['a', 'o', 'e', 'i', 'u', 'ṳ']
        nasal_consonants = ['n', 'm', 'ng']

        # 先檢查高優先級元音
        for vowel in high_priority_vowels:
            if vowel in syllable:
                parts = syllable.split(vowel, 1)
                if len(parts) == 2:
                    return parts[0] + vowel + tone_mark + parts[1]

        # 沒有高優先級元音，找第一個出現的元音
        for i, char in enumerate(syllable):
            if char in all_vowels:
                return syllable[:i] + char + tone_mark + syllable[i+1:]

        # 沒有元音，標在鼻音輔音上（如 ng, m）
        # 優先標在 n 上（ng 的情況）
        if 'ng' in syllable:
            # ng 的情況，標在 n 上
            parts = syllable.split('ng', 1)
            if len(parts) == 2:
                return parts[0] + 'n' + tone_mark + 'g' + parts[1]
        elif 'n' in syllable:
            parts = syllable.split('n', 1)
            if len(parts) == 2:
                return parts[0] + 'n' + tone_mark + parts[1]
        elif 'm' in syllable:
            parts = syllable.split('m', 1)
            if len(parts) == 2:
                return parts[0] + 'm' + tone_mark + parts[1]

        return syllable

    @staticmethod
    def buc_final_to_romanization(buc_final: str) -> str:
        """
        將平話字韻母轉換為拼式

        a̤ → aa, e̤ → ee, o̤ → oo, ṳ → y, ⁿ → nn
        """
        result = buc_final
        result = result.replace('a̤', 'aa')
        result = result.replace('e̤', 'ee')
        result = result.replace('o̤', 'oo')
        result = result.replace('ṳ', 'y')
        result = result.replace('ⁿ', 'nn')
        return result

    @staticmethod
    def buc_to_romanization(buc_syllable: str) -> str:
        """
        將平話字音節轉換為輸入式

        例如：kā → ka5, sâ̤ → saa3, guáⁿ → guann2, do̤̍h → dooh7

        使用新的 RomanizationConverter
        """
        return RomanizationConverter.buc_to_input(buc_syllable)


class LuaDictParser:
    """Lua 字典解析器"""

    @staticmethod
    def parse_lua_dict(lua_file: Path) -> Dict[str, List[str]]:
        """解析 cpx-pron-data.lua 文件"""
        char_dict = {}

        with open(lua_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取 export.buc = { ... } 部分
        match = re.search(r'export\.buc\s*=\s*\{(.+)\}', content, re.DOTALL)
        if not match:
            print("錯誤：無法解析 Lua 文件")
            return {}

        dict_content = match.group(1)

        # 解析每個條目：["字"] = {"pron1", "pron2", ...}
        pattern = r'\["(.+?)"\]\s*=\s*\{([^}]*)\}'

        for match in re.finditer(pattern, dict_content):
            char = match.group(1)
            prons_str = match.group(2)

            # 解析讀音列表
            prons = re.findall(r'"([^"]+)"', prons_str)
            # 移除星號
            prons = [p.replace('*', '') for p in prons]
            char_dict[char] = prons

        return char_dict


class AssimilationReverser:
    """聲母類化反推器"""

    @staticmethod
    def get_final_type(romanization: str) -> str:
        """
        判斷拼式的韻尾類型

        Returns:
            'nasal_nn': 鼻化韻 (nn)
            'nasal_ng': 鼻音韻 (ng)
            'stop': 入聲韻 (h)
            'open': 陰聲韻 (a/i/e/o/u/y)
        """
        # 先去掉聲調數字（1-8）
        rom_no_tone = re.sub(r'[1-8]$', '', romanization)

        if rom_no_tone.endswith('nn'):
            return 'nasal_nn'
        elif rom_no_tone.endswith('ng'):
            return 'nasal_ng'
        elif rom_no_tone.endswith('h'):
            return 'stop'
        else:
            # a, i, e, o, u, y 結尾
            return 'open'

    @staticmethod
    def reverse_case_1(current_initial_psp: str) -> List[str]:
        """
        情況1：前字拼式為鼻音韻 (ng)

        Returns:
            可能的原始聲母（莆拼形式）
        """
        reverse_map = {
            'm': ['b', 'p', 'm'],
            'n': ['d', 't', 'n', 'l', 'z', 'c', 's'],
            'ng': ['g', 'k', 'h', 'ng', ''],  # 零聲母
        }
        return reverse_map.get(current_initial_psp, [current_initial_psp])

    @staticmethod
    def reverse_case_2(current_initial_psp: str) -> List[str]:
        """
        情況2：前字拼式為入聲韻 (h)

        任何聲母保持不變
        """
        return [current_initial_psp]

    @staticmethod
    def reverse_case_3(current_initial_psp: str) -> List[str]:
        """
        情況3：前字拼式為陰聲韻或鼻化韻 (a/i/e/o/u/y/nn)

        Returns:
            可能的原始聲母（莆拼形式）
        """
        reverse_map = {
            '': ['b', 'p', 'g', 'k', 'h', ''],  # 零聲母
            'l': ['d', 't', 'z', 'c', 's', 'l'],
            'm': ['m'],
            'n': ['n'],
            'ng': ['ng'],
        }
        return reverse_map.get(current_initial_psp, [current_initial_psp])

    @staticmethod
    def reverse_case_4(current_initial_psp: str) -> List[str]:
        """
        情況4：前字鼻化韻、後字非鼻化韻

        只在情況1-3找不到且後字聲母是 m/n 時使用
        """
        reverse_map = {
            'm': ['b', 'p'],
            'n': ['d', 't', 'l', 'z', 'c', 's'],
        }
        return reverse_map.get(current_initial_psp, [])

    @staticmethod
    def reverse_case_5(current_initial_psp: str) -> List[str]:
        """
        情況5：前字非鼻化韻、後字鼻化韻

        只在情況1-3找不到且後字聲母是 m/n 時使用
        """
        reverse_map = {
            'm': ['b', 'p'],
            'n': ['d', 't'],
        }
        return reverse_map.get(current_initial_psp, [])


class DictConverter:
    """詞庫轉換器（帶完整類化反推）"""

    def __init__(self, cpx_data: Dict[str, List[str]]):
        self.cpx_data = cpx_data
        self.romanizer = BucRomanizer()
        self.reverser = AssimilationReverser()
        self.warnings = []
        self.stats = {
            'total': 0,
            'success': 0,
            'from_dict_direct': 0,
            'from_dict_case_123': 0,
            'from_dict_case_45': 0,
            'from_conversion': 0,
            'failed': 0,
            'bracketed': 0
        }
        self.seen_entries: Set[Tuple[str, str]] = set()

    def convert_entry(self, hanzi: str, pinyin: str, weight: Optional[str] = None) -> Optional[Tuple[str, str, Optional[str]]]:
        """
        轉換一個詞條

        Returns:
            (漢字, 拼式, 詞頻) 或 None
        """
        self.stats['total'] += 1

        # 解析漢字和拼音
        chars, syllables = self.parse_entry(hanzi, pinyin)

        if len(chars) != len(syllables):
            self.warnings.append(f"警告：{hanzi} {pinyin} - 漢字與音節數量不匹配")
            return None

        # 逐字轉換，每次使用前一個字的確定拼式
        romanized_syllables = []
        prev_romanization = None

        for i, (char, psp_syl) in enumerate(zip(chars, syllables)):
            is_bracketed = char.startswith('[')
            char_clean = char.strip('[]')
            is_first = (i == 0)

            # 轉換音節為拼式
            rom_syl = self.convert_syllable(
                char_clean, psp_syl, is_bracketed, is_first, prev_romanization
            )

            if rom_syl is None:
                self.warnings.append(f"警告：{hanzi} {pinyin} - 無法轉換音節 {char}={psp_syl}")
                self.stats['failed'] += 1
                return None

            romanized_syllables.append(rom_syl)
            prev_romanization = rom_syl  # 更新前一個字的拼式

        # 組合拼式（用空格連接）
        romanization = ' '.join(romanized_syllables)

        # 去重檢查
        entry_key = (hanzi, romanization)
        if entry_key in self.seen_entries:
            return None
        self.seen_entries.add(entry_key)

        self.stats['success'] += 1
        return (hanzi, romanization, weight)

    def parse_entry(self, hanzi: str, pinyin: str) -> Tuple[List[str], List[str]]:
        """解析詞條的漢字和拼音"""
        chars = []
        i = 0
        while i < len(hanzi):
            if hanzi[i] == '[':
                j = hanzi.find(']', i)
                if j != -1:
                    chars.append(hanzi[i:j+1])
                    i = j + 1
                else:
                    chars.append(hanzi[i])
                    i += 1
            else:
                chars.append(hanzi[i])
                i += 1

        syllables = []
        for syl in pinyin.split():
            syl = syl.strip('{}')
            syllables.append(syl)

        return chars, syllables

    def convert_syllable(
        self,
        char: str,
        psp_syllable: str,
        is_bracketed: bool,
        is_first: bool,
        prev_romanization: Optional[str]
    ) -> Optional[str]:
        """
        轉換單個音節為拼式（帶類化反推）

        Args:
            char: 漢字
            psp_syllable: 莆拼音節
            is_bracketed: 是否為括號內的合音字
            is_first: 是否為詞首
            prev_romanization: 前一個字的確定拼式

        Returns:
            拼式或 None
        """
        # 括號內的合音字，直接轉換
        if is_bracketed:
            self.stats['bracketed'] += 1
            candidates = self.romanizer.psp_to_buc_candidates(psp_syllable)
            if candidates:
                rom = self.romanizer.buc_to_romanization(candidates[0])
                self.stats['from_conversion'] += 1
                return rom
            return None

        # 詞首字，直接轉換並查字典
        if is_first:
            return self.convert_first_syllable(char, psp_syllable)

        # 非詞首字，需要考慮類化
        return self.convert_non_first_syllable(char, psp_syllable, prev_romanization)

    def convert_first_syllable(self, char: str, psp_syllable: str) -> Optional[str]:
        """轉換詞首音節（不需要類化反推）"""
        # 1. 直接轉換
        buc_candidates = self.romanizer.psp_to_buc_candidates(psp_syllable)
        if not buc_candidates:
            return None

        # 2. 查字典匹配
        matched = self.match_dict(char, buc_candidates)
        if matched:
            self.stats['from_dict_direct'] += 1
            return matched

        # 3. 未找到，使用第一個候選
        rom = self.romanizer.buc_to_romanization(buc_candidates[0])
        self.stats['from_conversion'] += 1
        self.warnings.append(f"註：{char}={psp_syllable} 使用直接轉換 {rom}")
        return rom

    def convert_non_first_syllable(
        self,
        char: str,
        psp_syllable: str,
        prev_romanization: str
    ) -> Optional[str]:
        """轉換非詞首音節（需要類化反推）"""
        # Step 1: 直接轉換並查字典
        buc_candidates = self.romanizer.psp_to_buc_candidates(psp_syllable)
        if not buc_candidates:
            return None

        matched = self.match_dict(char, buc_candidates)
        if matched:
            self.stats['from_dict_direct'] += 1
            return matched

        # Step 2: 情況1-3反推
        final_type = self.reverser.get_final_type(prev_romanization)
        matched = self.try_reverse_case_123(
            char, psp_syllable, final_type
        )
        if matched:
            self.stats['from_dict_case_123'] += 1
            self.warnings.append(f"註：{char}={psp_syllable} 使用情況1-3反推 {matched}")
            return matched

        # Step 3: 情況4-5反推（僅當後字聲母是 m/n）
        current_initial = self.extract_initial_psp(psp_syllable)
        if current_initial in ['m', 'n']:
            matched = self.try_reverse_case_45(
                char, psp_syllable, prev_romanization, final_type
            )
            if matched:
                self.stats['from_dict_case_45'] += 1
                self.warnings.append(f"註：{char}={psp_syllable} 使用情況4-5反推 {matched}")
                return matched

        # Step 4: 全部失敗，使用直接轉換的第一個候選
        rom = self.romanizer.buc_to_romanization(buc_candidates[0])
        self.stats['from_conversion'] += 1
        self.warnings.append(f"註：{char}={psp_syllable} 使用直接轉換 {rom}")
        return rom

    def try_reverse_case_123(
        self,
        char: str,
        psp_syllable: str,
        final_type: str
    ) -> Optional[str]:
        """嘗試情況1-3的反推"""
        current_initial = self.extract_initial_psp(psp_syllable)
        finaltone = psp_syllable[len(current_initial):] if current_initial else psp_syllable

        # 根據前字韻尾類型選擇反推規則
        if final_type == 'nasal_ng':
            possible_initials = self.reverser.reverse_case_1(current_initial)
        elif final_type == 'stop':
            possible_initials = self.reverser.reverse_case_2(current_initial)
        else:  # open or nasal_nn
            possible_initials = self.reverser.reverse_case_3(current_initial)

        # 先生成所有可能的候選
        all_buc_candidates = []
        for init in possible_initials:
            psp_candidate = init + finaltone
            buc_candidates = self.romanizer.psp_to_buc_candidates(psp_candidate)
            all_buc_candidates.extend(buc_candidates)

        # 一次性查字典，返回字典中排序最前的
        matched = self.match_dict(char, all_buc_candidates)
        if matched:
            return matched

        return None

    def try_reverse_case_45(
        self,
        char: str,
        psp_syllable: str,
        prev_romanization: str,
        final_type: str
    ) -> Optional[str]:
        """嘗試情況4-5的反推"""
        current_initial = self.extract_initial_psp(psp_syllable)
        finaltone = psp_syllable[len(current_initial):] if current_initial else psp_syllable

        # 情況4：前字鼻化韻、後字非鼻化韻
        if final_type == 'nasal_nn':
            possible_initials = self.reverser.reverse_case_4(current_initial)
            all_buc_candidates = []
            for init in possible_initials:
                psp_candidate = init + finaltone
                buc_candidates = self.romanizer.psp_to_buc_candidates(psp_candidate)
                # 只選無 ⁿ 的版本
                buc_candidates = [c for c in buc_candidates if 'ⁿ' not in c]
                all_buc_candidates.extend(buc_candidates)

            matched = self.match_dict(char, all_buc_candidates)
            if matched:
                return matched

        # 情況5：前字非鼻化韻、後字鼻化韻
        else:
            possible_initials = self.reverser.reverse_case_5(current_initial)
            all_buc_candidates = []
            for init in possible_initials:
                psp_candidate = init + finaltone
                buc_candidates = self.romanizer.psp_to_buc_candidates(psp_candidate)
                # 只選有 ⁿ 的版本
                buc_candidates = [c for c in buc_candidates if 'ⁿ' in c]
                all_buc_candidates.extend(buc_candidates)

            matched = self.match_dict(char, all_buc_candidates)
            if matched:
                return matched

        return None

    def extract_initial_psp(self, psp_syllable: str) -> str:
        """提取莆拼聲母"""
        if psp_syllable.startswith("ng"):
            return "ng"
        elif psp_syllable.startswith("ch"):
            return "ch"
        elif psp_syllable[0] in 'bpmgkhdtnlcsz':
            return psp_syllable[0]
        else:
            return ""  # 零聲母

    def match_dict(self, char: str, buc_candidates: List[str]) -> Optional[str]:
        """
        從候選中找字典匹配，優先返回字典中排序最前的讀音

        Returns:
            匹配的拼式或 None
        """
        if char not in self.cpx_data:
            return None

        char_prons = self.cpx_data[char]

        # 優先遍歷字典（按順序），這樣會返回字典中排序最前的讀音
        for dict_pron in char_prons:
            dict_pron_norm = norm('NFC', dict_pron)
            for buc_cand in buc_candidates:
                buc_cand_norm = norm('NFC', buc_cand)
                if buc_cand_norm == dict_pron_norm:
                    # 找到匹配！返回字典中的這個讀音
                    return self.romanizer.buc_to_romanization(dict_pron)

        return None

    def add_cpx_dict_entries(self) -> List[Tuple[str, str, Optional[str]]]:
        """從 cpx 字典添加單字詞條"""
        entries = []
        for char, prons in self.cpx_data.items():
            if '[' in char or ']' in char:
                continue

            for pron in prons:
                rom = self.romanizer.buc_to_romanization(pron)
                entry_key = (char, rom)
                if entry_key not in self.seen_entries:
                    self.seen_entries.add(entry_key)
                    entries.append((char, rom, None))

        return entries


def convert_pouleng_dict(pouleng_file: Path, cpx_file: Path, output_file: Path):
    """轉換詞庫（拼式版本）"""

    print(f"讀取字典資料：{cpx_file}")
    cpx_data = LuaDictParser.parse_lua_dict(cpx_file)
    print(f"已載入 {len(cpx_data)} 個漢字的讀音資料\n")

    print(f"讀取詞庫：{pouleng_file}\n")
    converter = DictConverter(cpx_data)

    # 讀取原始詞庫
    with open(pouleng_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 解析詞條
    entries = []
    in_header = True

    for line in lines:
        line = line.rstrip('\n')

        if in_header:
            if line == '...':
                in_header = False
            continue
        else:
            if not line.strip() or line.strip().startswith('#'):
                continue

            parts = line.split('\t')
            if len(parts) >= 2:
                hanzi = parts[0]
                pinyin = parts[1]
                weight = parts[2] if len(parts) > 2 else None

                result = converter.convert_entry(hanzi, pinyin, weight)
                if result:
                    entries.append(result)

    # 添加 cpx 字典的單字條目
    print("\n添加 cpx 字典的單字條目...")
    cpx_entries = converter.add_cpx_dict_entries()
    print(f"從 cpx 字典添加了 {len(cpx_entries)} 個單字條目\n")

    entries.extend(cpx_entries)

    # 寫入輸出文件
    print(f"寫入輸出檔案：{output_file}\n")
    with open(output_file, 'w', encoding='utf-8') as f:
        # 寫入標頭
        f.write("# Rime dictionary\n")
        f.write("# encoding: utf-8\n")
        f.write("#\n")
        f.write("# 興化平話字詞庫（漢字輸出版本）Báⁿ-uā-ci̍ Dictionary (Chinese Character Output)\n")
        f.write("# 基於莆田城區口音 Based on Putian downtown accent\n")
        f.write("#\n")
        f.write("# 本詞庫用於漢字輸出模式\n")
        f.write("# 格式：漢字 + 輸入式平話字 + 權重\n")
        f.write("# 候選詞顯示漢字，註釋顯示平話字\n")
        f.write("#\n")
        f.write("---\n")
        f.write("name: borhlang_bannuaci_han\n")
        f.write("version: \"0.3.0\"\n")
        f.write("use_preset_vocabulary: false\n")
        f.write("sort: by_weight\n")
        f.write("...\n\n")

        # 寫入詞條
        for hanzi, romanization, weight in entries:
            if weight:
                f.write(f"{hanzi}\t{romanization}\t{weight}\n")
            else:
                f.write(f"{hanzi}\t{romanization}\n")

    # 輸出統計
    print("轉換完成！")
    print(f"總詞條數：{converter.stats['total']}")
    print(f"成功轉換：{converter.stats['success']}")
    print(f"  - 從字典直接匹配：{converter.stats['from_dict_direct']}")
    print(f"  - 從字典情況1-3反推：{converter.stats['from_dict_case_123']}")
    print(f"  - 從字典情況4-5反推：{converter.stats['from_dict_case_45']}")
    print(f"  - 從自動轉換：{converter.stats['from_conversion']}")
    print(f"重複略過的條目數：{converter.stats['total'] - converter.stats['success'] - len([w for w in converter.warnings if '警告' in w])}")
    print(f"轉換失敗：{len([w for w in converter.warnings if '警告' in w])}")
    print(f"多字總條數：{len(entries)}\n")

    # 寫入日誌
    log_file = output_file.parent / "conversion_log_v3.txt"
    with open(log_file, 'w', encoding='utf-8') as f:
        for warning in converter.warnings:
            f.write(warning + '\n')

    print(f"轉換日誌已寫入：{log_file}")
    print(f"共 {len(converter.warnings)} 筆\n")


if __name__ == '__main__':
    base_dir = Path(__file__).parent.parent

    # 使用合併後的莆仙話拼音詞庫（包含維基詞典和聖經詞彙）
    pouleng_file = base_dir / "pouseng_pinging" / "borhlang_pouleng.dict.yaml"
    cpx_file = base_dir / "data" / "cpx-pron-data.lua"
    # 輸出為漢字+拼式版本（供 generate_pure_bannuaci_dict.py 使用）
    output_file = base_dir / "bannuaci" / "borhlang_bannuaci_han.dict.yaml"

    convert_pouleng_dict(pouleng_file, cpx_file, output_file)
