#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成純平話字輸入方案詞庫
從 borhlang_bannuaci.dict.yaml 生成合併同音字的詞庫
"""

import re
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Set
from unicodedata import normalize as norm

# 導入轉換模組 (保留原有的導入，雖然下面主要使用 SyllableGenerator 的定義)
sys.path.append(str(Path(__file__).parent.parent / "data"))
try:
    from psp_to_buc import buc_initials, buc_finals, buc_tones
except ImportError:
    pass

class RomanizationConverter:
    """輸入式 → 平話字轉換器"""

    # 興化平話字調符位置表
    TONE_POSITIONS = {
        # 單字母
        "a": 1, "aa": 1, "e": 1, "ee": 1, "oo": 1, 
        "i": 1, "o": 1, "u": 1, "y": 1,
        
        # 多字母
        "ai": 1, "au": 1, "aau": 2, "eo": 2, 
        "ia": 2, "ioo": 2, "iu": 2, "oi": 1, 
        "ua": 2, "uai": 2, "ui": 1, "io": 2,

        # 鼻音韻
        "ng": 1, "ang": 1, "eng": 1, "ing": 1, "eong": 2, 
        "eeng": 1, "oong": 1, "iang": 2, "uang": 2, "yng": 1, 
        "ioong": 2,

        # 鼻化韻
        "ann": 1, "aann": 1, "eenn": 1, "oonn": 1, 
        "iann": 2, "oinn": 1, "uann": 2, "aaann": 2, 
        "ioonn": 2,

        # 入聲韻
        "ah": 1, "aih": 1, "aah": 1, "aauh": 3, 
        "eh": 1, "eeh": 1, "eoh": 2, "iah": 2, 
        "ih": 1, "iooh": 2, "oih": 1, "ooh": 1, 
        "uah": 2, "uh": 1, "yh": 1,
    }

    @classmethod
    def convert_syllable(cls, input_syl: str) -> str:
        """
        將輸入式音節轉為平話字
        """
        # 1. 基礎檢查
        if not input_syl or not input_syl[-1].isdigit():
            return cls._apply_replacements(input_syl)

        tone = input_syl[-1]
        base_full = input_syl[:-1]

        # 2. 分離聲母與韻母
        sorted_initials = sorted([i for i in SyllableGenerator.INITIALS if i], key=len, reverse=True)
        
        initial = ''
        final = base_full

        for init in sorted_initials:
            if base_full.startswith(init):
                remainder = base_full[len(init):]
                
                # --- 修正開始 ---
                # 特殊判斷：韻化輔音 (Syllabic Consonants)
                # 如果扣除聲母後為空，且該聲母本身是 m 或 ng
                # 則視為「零聲母」+「m/ng 韻母」
                if remainder == '' and init in ['m', 'ng']:
                    initial = ''
                    final = base_full  # 整個音節作為韻母
                    break  # 直接結束，不要讓它繼續匹配 'n'
                # --- 修正結束 ---

                initial = init
                final = remainder
                break

        # 3. 處理韻母替換
        processed_final = cls._apply_replacements(final)

        # 4. 決定聲調符號
        ends_with_h = final.endswith('h')
        tone_marks = {
            '1': '',
            '2': '\u0301',  # ́ acute
            '3': '\u0302',  # ̂ circumflex
            '4': '\u030D',  # ̍ vertical line above
            '5': '\u0304',  # ̄ macron
            '6': '\u0304' if not ends_with_h else '',
            '7': '\u030D',  # ̍ vertical line above
        }
        tone_mark = tone_marks.get(tone, '')

        if not tone_mark:
            return norm('NFC', initial + processed_final)

        # 5. 插入聲調符號
        # 使用原始 final 查表
        position = cls.TONE_POSITIONS.get(final, 1)

        # 防呆
        if position > len(processed_final):
            position = len(processed_final)

        final_with_tone = processed_final[:position] + tone_mark + processed_final[position:]

        return norm('NFC', initial + final_with_tone)

    @staticmethod
    def _apply_replacements(text: str) -> str:
        text = text.replace('aa', 'a\u0324')
        text = text.replace('ee', 'e\u0324')
        text = text.replace('oo', 'o\u0324')
        text = text.replace('y', '\u1E73')
        text = text.replace('nn', '\u207F')
        return text

    @staticmethod
    def convert_text(input_text: str) -> str:
        syllables = input_text.split()
        converted = [RomanizationConverter.convert_syllable(syl) for syl in syllables]
        return '-'.join(converted)

class SyllableGenerator:
    """合法音節生成器"""

    # 聲母（15個）
    INITIALS = ['b', 'p', 'm', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'ng', 'c', 'ch', 's', '']

    # 韻母分類 (保持原樣)
    FINALS_NASAL_NN = ['ann', 'aann', 'eenn', 'oonn', 'iann', 'aaunn', 'oinn', 'ioonn', 'uann']
    FINALS_NASAL_NG = ['ng', 'ang', 'ioong', 'eeng', 'uang', 'eong', 'oong', 'eng', 'iang', 'ing', 'yng']
    FINALS_CHECKED = ['ah', 'aah', 'aih', 'aauh', 'eh', 'eeh', 'eoh', 'ih', 'iah', 'iooh', 'oih', 'ooh', 'uah', 'uh', 'yh']
    FINALS_OPEN = ['a', 'aa', 'e', 'ee', 'oo', 'eo', 'i', 'y', 'u', 'ia', 'aau', 'iu', 'ai', 'au', 'o', 'ua', 'uai', 'ui', 'ioo']

    # 聲調
    TONES_OPEN = ['1', '2', '3', '4', '5']  
    TONES_CHECKED = ['6', '7']

    @classmethod
    def is_valid_syllable(cls, initial: str, final: str, tone: str) -> bool:
        """檢查音節是否合法"""
        if initial in ['m', 'n', 'ng'] and final in cls.FINALS_NASAL_NN:
            return False
        if initial == 'ng' and final == 'ng':
            return False
        if final in cls.FINALS_CHECKED and tone not in cls.TONES_CHECKED:
            return False
        all_open_finals = cls.FINALS_NASAL_NN + cls.FINALS_NASAL_NG + cls.FINALS_OPEN
        if final in all_open_finals and tone not in cls.TONES_OPEN:
            return False
        return True

    @classmethod
    def generate_all_syllables(cls) -> Set[str]:
        """生成所有合法音節"""
        syllables = set()
        all_finals = (cls.FINALS_NASAL_NN + cls.FINALS_NASAL_NG +
                     cls.FINALS_CHECKED + cls.FINALS_OPEN)
        all_tones = cls.TONES_OPEN + cls.TONES_CHECKED

        for initial in cls.INITIALS:
            for final in all_finals:
                for tone in all_tones:
                    if cls.is_valid_syllable(initial, final, tone):
                        syllable = f"{initial}{final}{tone}"
                        syllables.add(syllable)
        return syllables


class DictMerger:
    # ... (DictMerger 類別保持不變，與原腳本相同) ...
    def __init__(self):
        self.syllable_groups = defaultdict(list)
        self.multi_syllable_entries = []
        self.rom_only_candidates = []  # 儲存只有羅馬字的候選詞

    def parse_dict(self, dict_file: Path, is_rom_only: bool = False):
        """
        解析詞典文件

        Args:
            dict_file: 詞典文件路徑
            is_rom_only: 是否為只有羅馬字的詞典（來自聖經但無漢字的詞）
        """
        print(f"讀取詞庫：{dict_file}")
        with open(dict_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        in_header = True
        for line in lines:
            line = line.rstrip('\n')
            if in_header:
                if line == '...':
                    in_header = False
                continue
            if not line.strip() or line.strip().startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) < 2:
                continue
            hanzi = parts[0].strip()
            syllables_str = parts[1].strip()
            weight = parts[2].strip() if len(parts) > 2 else None
            syllables = syllables_str.split()

            # 如果是只有羅馬字的詞（帶 ▣ 佔位符），單獨處理
            if is_rom_only and '▣' in hanzi:
                if len(syllables) > 1:  # 只處理多音節詞
                    self.rom_only_candidates.append((hanzi, syllables, weight))
            else:
                # 正常處理有漢字的詞
                if len(syllables) == 1:
                    self.syllable_groups[syllables[0]].append((hanzi, weight))
                else:
                    self.multi_syllable_entries.append((hanzi, syllables, weight))

        if is_rom_only:
            print(f"解析完成：{len(self.rom_only_candidates)} 個只有羅馬字的候選詞")
        else:
            print(f"解析完成：{len(self.syllable_groups)} 個不同音節，{len(self.multi_syllable_entries)} 個多音節詞")

    def add_rom_only_if_missing(self):
        """
        添加只有羅馬字的候選詞（如果該讀音尚未存在）
        """
        print(f"\n處理只有羅馬字的候選詞...")

        # 建立現有多音節詞的讀音集合
        existing_pronunciations = set()
        for hanzi, syllables, weight in self.multi_syllable_entries:
            key = tuple(syllables)
            existing_pronunciations.add(key)

        # 檢查候選詞
        added_count = 0
        for hanzi, syllables, weight in self.rom_only_candidates:
            key = tuple(syllables)

            # 如果這個讀音還不存在，則添加
            if key not in existing_pronunciations:
                self.multi_syllable_entries.append((hanzi, syllables, weight))
                existing_pronunciations.add(key)
                added_count += 1

        print(f"從只有羅馬字的候選詞中添加了 {added_count} 個新讀音")

    def merge_same_pronunciation(self):
        merged_multi = defaultdict(list)
        for hanzi, syllables, weight in self.multi_syllable_entries:
            key = tuple(syllables)
            merged_multi[key].append((hanzi, weight))
        self.merged_multi_entries = []
        for syllables_tuple, hanzi_list in merged_multi.items():
            # 去除重複的漢字（保持順序）
            unique_hanzi = list(dict.fromkeys([h for h, w in hanzi_list]))
            merged_hanzi = '/'.join(unique_hanzi)
            weight = hanzi_list[0][1] if hanzi_list[0][1] else None
            self.merged_multi_entries.append((merged_hanzi, list(syllables_tuple), weight))
        print(f"合併後：{len(self.merged_multi_entries)} 個不同讀音的多音節詞")

    def calculate_weights(self):
        tone_weights = {'1': 60, '2': 50, '3': 40, '4': 30, '5': 20, '6': 10, '7': 0}
        for syllable, hanzi_list in self.syllable_groups.items():
            tone = syllable[-1] if syllable and syllable[-1].isdigit() else '1'
            base_weight = 1000 + tone_weights.get(tone, 0)
            updated_list = []
            for hanzi, weight in hanzi_list:
                if weight is None:
                    weight = str(base_weight)
                updated_list.append((hanzi, weight))
            self.syllable_groups[syllable] = updated_list

    def add_placeholder_syllables(self):
        print("\n生成所有合法音節...")
        all_valid_syllables = SyllableGenerator.generate_all_syllables()
        existing_syllables = set(self.syllable_groups.keys())
        missing_syllables = all_valid_syllables - existing_syllables
        print(f"發現 {len(missing_syllables)} 個無漢字的合法音節")
        tone_weights = {'1': 60, '2': 50, '3': 40, '4': 30, '5': 20, '6': 10, '7': 0}
        for syllable in missing_syllables:
            tone = syllable[-1] if syllable and syllable[-1].isdigit() else '1'
            weight = 100 + tone_weights.get(tone, 0)
            self.syllable_groups[syllable] = [('▣', str(weight))]

    def generate_output(self, output_file: Path):
        print(f"\n生成輸出詞庫：{output_file}")
        entries = []
        converter = RomanizationConverter()

        for syllable in sorted(self.syllable_groups.keys()):
            hanzi_list = self.syllable_groups[syllable]
            # 去除重複的漢字（保持順序）
            unique_hanzi = list(dict.fromkeys([h for h, w in hanzi_list]))
            merged_hanzi = '/'.join(unique_hanzi)
            weight = hanzi_list[0][1] if hanzi_list else None
            buc_form = converter.convert_text(syllable)
            text = f"{buc_form}@{syllable}@{merged_hanzi}|"
            code = syllable
            entries.append((text, code, weight))

        for merged_hanzi, syllables, weight in self.merged_multi_entries:
            input_text = ' '.join(syllables)
            buc_form = converter.convert_text(input_text)
            text = f"{buc_form}@{input_text}@{merged_hanzi}|"
            code = input_text
            if weight is None:
                weight = '500'
            entries.append((text, code, weight))

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Rime dictionary\n# encoding: utf-8\n#\n# 興化平話字詞庫（純平話字版本）\n")
            f.write("# Báⁿ-uā-ci̍ Dictionary (Pure Romanization Version)\n#\n")
            f.write("---\nname: borhlang_bannuaci\nversion: \"0.2.0\"\n")
            f.write("sort: by_weight\n...\n\n")
            for text, code, weight in entries:
                if weight:
                    f.write(f"{text}\t{code}\t{weight}\n")
                else:
                    f.write(f"{text}\t{code}\n")
        print(f"完成！共 {len(entries)} 個詞條")


def main():
    """主函數"""
    base_dir = Path(__file__).parent.parent
    input_file = base_dir / "bannuaci" / "borhlang_bannuaci_han.dict.yaml"
    rom_only_file = base_dir / "data" / "vocab_from_bible.yaml"
    output_file = base_dir / "bannuaci" / "borhlang_bannuaci.dict.yaml"

    merger = DictMerger()

    # 讀取有漢字的詞庫
    merger.parse_dict(input_file, is_rom_only=False)

    # 讀取只有羅馬字的候選詞（來自聖經）
    if rom_only_file.exists():
        merger.parse_dict(rom_only_file, is_rom_only=True)
        # 添加那些讀音尚未存在的詞
        merger.add_rom_only_if_missing()
    else:
        print(f"\n警告：找不到只有羅馬字的詞庫 {rom_only_file}，跳過處理")

    merger.merge_same_pronunciation()
    merger.calculate_weights()
    merger.add_placeholder_syllables()
    merger.generate_output(output_file)

if __name__ == '__main__':
    main()