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

# 導入轉換模組
sys.path.append(str(Path(__file__).parent.parent / "data"))
from psp_to_buc import buc_initials, buc_finals, buc_tones


class RomanizationConverter:
    """輸入式 → 平話字轉換器"""

    @staticmethod
    def convert_syllable(input_syl: str) -> str:
        """
        將輸入式音節轉為平話字
        例如: gaa2 → gá̤
        """
        # 解析聲調
        if not input_syl or not input_syl[-1].isdigit():
            return input_syl

        tone = input_syl[-1]
        base = input_syl[:-1]  # 移除聲調數字

        # 替換特殊字元
        base = base.replace('aa', 'a\u0324')  # a̤
        base = base.replace('ee', 'e\u0324')  # e̤
        base = base.replace('oo', 'o\u0324')  # o̤
        base = base.replace('y', '\u1E73')     # ṳ
        base = base.replace('nn', '\u207F')    # ⁿ

        # 檢查是否以 h 結尾（入聲韻）
        ends_with_h = base.endswith('h')

        # 聲調標記
        tone_marks = {
            '1': '',
            '2': '\u0301',  # ́ acute
            '3': '\u0302',  # ̂ circumflex
            '4': '\u030D',  # ̍ vertical line above
            '5': '\u0304',  # ̄ macron
            '6': '\u0304' if not ends_with_h else '',  # 非h結尾用macron
            '7': '\u030D',  # ̍ vertical line above
        }

        tone_mark = tone_marks.get(tone, '')

        # 如果沒有聲調標記，直接返回
        if not tone_mark:
            return norm('NFC', base)

        # 找主元音並加聲調
        # 元音優先級：a > o > e > i/u/ṳ
        result = base
        for vowel in ['a', 'o', 'e', 'i', 'u', '\u1E73']:
            if vowel in base:
                # 在第一個出現的該元音後加聲調
                parts = base.split(vowel, 1)
                result = parts[0] + vowel + tone_mark + (parts[1] if len(parts) > 1 else '')
                break

        return norm('NFC', result)

    @staticmethod
    def convert_text(input_text: str) -> str:
        """
        轉換完整文本（多個音節）
        例如: po2 cheng2 → pó-chéng
        """
        syllables = input_text.split()
        converted = [RomanizationConverter.convert_syllable(syl) for syl in syllables]
        return '-'.join(converted)


class SyllableGenerator:
    """合法音節生成器"""

    # 聲母（15個）
    INITIALS = ['b', 'p', 'm', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'ng', 'c', 'ch', 's', '']

    # 韻母分類
    FINALS_NASAL_NN = ['ann', 'aann', 'eenn', 'oonn', 'iann', 'aaunn', 'oinn', 'ioonn', 'uann']
    FINALS_NASAL_NG = ['ng', 'ang', 'ioong', 'eeng', 'uang', 'eong', 'oong', 'eng', 'iang', 'ing', 'yng']
    FINALS_CHECKED = ['ah', 'aah', 'ooh', 'eoh', 'ih', 'iah', 'aauh', 'oih', 'iooh', 'eh', 'eeh', 'yh', 'uah']
    FINALS_OPEN = ['a', 'aa', 'ee', 'oo', 'eo', 'i', 'y', 'u', 'ia', 'aau', 'iu', 'ai', 'au', 'o', 'ua', 'uai', 'ui', 'ioo']

    # 聲調
    TONES_OPEN = ['1', '2', '3', '4', '5']  # 非h結尾韻母（不包含6，因為和5相同）
    TONES_CHECKED = ['6', '7']  # h結尾韻母

    @classmethod
    def is_valid_syllable(cls, initial: str, final: str, tone: str) -> bool:
        """檢查音節是否合法"""
        # 規則1: m, n, ng 不能搭配 nn 結尾韻母
        if initial in ['m', 'n', 'ng'] and final in cls.FINALS_NASAL_NN:
            return False

        # 規則2: ng 不能搭配韻母 ng
        if initial == 'ng' and final == 'ng':
            return False

        # 規則3: h結尾韻母只能 6、7 調
        if final in cls.FINALS_CHECKED and tone not in cls.TONES_CHECKED:
            return False

        # 規則4: 非h結尾韻母只能 1-5 調
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
    """詞庫合併器"""

    def __init__(self):
        self.syllable_groups = defaultdict(list)  # {syllable: [(hanzi, weight), ...]}
        self.multi_syllable_entries = []  # [(hanzi, syllables, weight), ...]

    def parse_dict(self, dict_file: Path):
        """解析詞庫檔案"""
        print(f"讀取詞庫：{dict_file}")

        with open(dict_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        in_header = True
        for line in lines:
            line = line.rstrip('\n')

            # 跳過標頭
            if in_header:
                if line == '...':
                    in_header = False
                continue

            # 跳過空行和註釋
            if not line.strip() or line.strip().startswith('#'):
                continue

            # 解析詞條：漢字\t拼音\t權重（可選）
            parts = line.split('\t')
            if len(parts) < 2:
                continue

            hanzi = parts[0].strip()
            syllables_str = parts[1].strip()
            weight = parts[2].strip() if len(parts) > 2 else None

            syllables = syllables_str.split()

            # 單音節詞
            if len(syllables) == 1:
                self.syllable_groups[syllables[0]].append((hanzi, weight))
            # 多音節詞
            else:
                self.multi_syllable_entries.append((hanzi, syllables, weight))

        print(f"解析完成：{len(self.syllable_groups)} 個不同音節，{len(self.multi_syllable_entries)} 個多音節詞")

    def merge_same_pronunciation(self):
        """合併相同讀音的多音節詞"""
        merged_multi = defaultdict(list)  # {tuple(syllables): [(hanzi, weight), ...]}

        for hanzi, syllables, weight in self.multi_syllable_entries:
            key = tuple(syllables)
            merged_multi[key].append((hanzi, weight))

        # 轉換回列表格式
        self.merged_multi_entries = []
        for syllables_tuple, hanzi_list in merged_multi.items():
            # 合併漢字，用斜線分隔
            merged_hanzi = '/'.join([h for h, w in hanzi_list])
            # 使用第一個詞的權重（或可以取平均、最大值等）
            weight = hanzi_list[0][1] if hanzi_list[0][1] else None
            self.merged_multi_entries.append((merged_hanzi, list(syllables_tuple), weight))

        print(f"合併後：{len(self.merged_multi_entries)} 個不同讀音的多音節詞")

    def calculate_weights(self):
        """計算權重（按聲調排序）"""
        tone_weights = {
            '1': 60,  # 陰平
            '2': 50,  # 陽平
            '3': 40,  # 上聲
            '4': 30,  # 陰去
            '5': 20,  # 陽去
            '6': 10,  # 陰入
            '7': 0,   # 陽入
        }

        # 為單音節詞設定權重
        for syllable, hanzi_list in self.syllable_groups.items():
            # 取得聲調
            tone = syllable[-1] if syllable and syllable[-1].isdigit() else '1'

            # 基礎權重：有漢字的詞
            base_weight = 1000 + tone_weights.get(tone, 0)

            # 更新權重（如果原本沒有權重）
            updated_list = []
            for hanzi, weight in hanzi_list:
                if weight is None:
                    weight = str(base_weight)
                updated_list.append((hanzi, weight))

            self.syllable_groups[syllable] = updated_list

    def add_placeholder_syllables(self):
        """加入有音無字的音節（佔位符）"""
        print("\n生成所有合法音節...")
        all_valid_syllables = SyllableGenerator.generate_all_syllables()
        existing_syllables = set(self.syllable_groups.keys())

        missing_syllables = all_valid_syllables - existing_syllables
        print(f"發現 {len(missing_syllables)} 個無漢字的合法音節")

        # 計算佔位符權重
        tone_weights = {
            '1': 60, '2': 50, '3': 40, '4': 30, '5': 20, '6': 10, '7': 0,
        }

        for syllable in missing_syllables:
            tone = syllable[-1] if syllable and syllable[-1].isdigit() else '1'
            # 佔位符使用較低的基礎權重
            weight = 100 + tone_weights.get(tone, 0)
            self.syllable_groups[syllable] = [('▣', str(weight))]

    def generate_output(self, output_file: Path):
        """生成輸出詞庫"""
        print(f"\n生成輸出詞庫：{output_file}")

        entries = []
        converter = RomanizationConverter()

        # 處理單音節詞
        for syllable in sorted(self.syllable_groups.keys()):
            hanzi_list = self.syllable_groups[syllable]

            # 合併同音字，用斜線分隔
            merged_hanzi = '/'.join([h for h, w in hanzi_list])

            # 使用第一個字的權重（已按聲調排序）
            weight = hanzi_list[0][1] if hanzi_list else None

            # 轉換為平話字
            buc_form = converter.convert_text(syllable)

            # 格式：text<TAB>code<TAB>weight
            # text: 平話字@輸入式@漢字|
            # code: 輸入式
            text = f"{buc_form}@{syllable}@{merged_hanzi}|"
            code = syllable

            entries.append((text, code, weight))

        # 處理多音節詞
        for merged_hanzi, syllables, weight in self.merged_multi_entries:
            input_text = ' '.join(syllables)  # 空格分隔的輸入式
            buc_form = converter.convert_text(input_text)  # 轉為平話字

            # 格式：text<TAB>code<TAB>weight
            # text: 平話字@輸入式@漢字|
            # code: 輸入式
            text = f"{buc_form}@{input_text}@{merged_hanzi}|"
            code = input_text

            # 多音節詞使用原始權重或預設值
            if weight is None:
                weight = '500'

            entries.append((text, code, weight))

        # 寫入檔案
        with open(output_file, 'w', encoding='utf-8') as f:
            # 寫入標頭
            f.write("# Rime dictionary\n")
            f.write("# encoding: utf-8\n")
            f.write("#\n")
            f.write("# 興化平話字詞庫（純平話字版本）\n")
            f.write("# Báⁿ-uā-ci̍ Dictionary (Pure Romanization Version)\n")
            f.write("#\n")
            f.write("# 本詞庫用於純平話字輸入方案\n")
            f.write("# 詞庫格式：平話字@輸入式@漢字|<TAB>輸入式<TAB>權重\n")
            f.write("# 由 Lua filter 解析並轉換顯示\n")
            f.write("#\n")
            f.write("---\n")
            f.write("name: borhlang_bannuaci\n")
            f.write('version: "0.2.0"\n')
            f.write("use_preset_vocabulary: false\n")
            f.write("sort: by_weight\n")
            f.write("...\n\n")

            # 寫入詞條
            for text, code, weight in entries:
                if weight:
                    f.write(f"{text}\t{code}\t{weight}\n")
                else:
                    f.write(f"{text}\t{code}\n")

        print(f"完成！共 {len(entries)} 個詞條")
        print(f"  - 單音節：{len(self.syllable_groups)}")
        print(f"  - 多音節：{len(self.merged_multi_entries)}")


def main():
    """主函數"""
    base_dir = Path(__file__).parent.parent

    input_file = base_dir / "bannuaci" / "borhlang_bannuaci_han.dict.yaml"
    output_file = base_dir / "bannuaci" / "borhlang_bannuaci.dict.yaml"

    # 創建合併器
    merger = DictMerger()

    # 解析詞庫
    merger.parse_dict(input_file)

    # 合併多音節詞
    merger.merge_same_pronunciation()

    # 計算權重
    merger.calculate_weights()

    # 加入佔位符音節
    merger.add_placeholder_syllables()

    # 生成輸出
    merger.generate_output(output_file)


if __name__ == '__main__':
    main()
