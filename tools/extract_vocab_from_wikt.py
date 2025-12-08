#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從維基詞典數據提取詞彙
Extract vocabulary from Wiktionary data

輸入：docs/puxian_phrases_from_wikt.txt
輸出：data/vocab_from_wikt.yaml (Pouseng Ping'ing 格式)
"""

import re
import sys
from pathlib import Path
from collections import defaultdict
from unicodedata import normalize as norm

# 導入轉換模組
sys.path.append(str(Path(__file__).parent.parent / "data"))
from psp_to_buc import buc_tones


class BucToPspConverter:
    """平話字 → 莆仙話拼音轉換器"""

    # 反向聲調映射
    TONE_MARKS_TO_NUM = {
        '': '1',          # 無標記 = 第1調
        '\u0301': '2',    # acute ́
        '\u0302': '3',    # circumflex ̂
        '\u030D': '4',    # vertical line ̍
        '\u0304': '5',    # macron ̄
    }

    # 韻母反向映射（平話字 → 莆拼）
    FINAL_MAP = {
        'a': 'a',
        'aⁿ': 'a',
        'ah': 'ah',
        'ai': 'ai',
        'ang': 'ang',
        'au': 'ao',
        'a̤': 'e',
        'a̤ⁿ': 'e',
        'a̤h': 'eh',
        'eh': 'eh',
        'eng': 'eng',
        'i': 'i',
        'ih': 'ih',
        'ia': 'ia',
        'iaⁿ': 'ia',
        'iah': 'iah',
        'iang': 'ieng',
        'a̤u': 'ieo',
        'a̤uⁿ': 'ieo',
        'a̤uh': 'ieh',
        'ing': 'ing',
        'iu': 'iu',
        'ng': 'ng',
        'eo': 'o',
        'eoh': 'oh',
        'e̤': 'oe',
        'e̤ⁿ': 'oe',
        'e̤h': 'oeh',
        'e̤ng': 'oeng',
        'eong': 'ong',
        'o̤': 'or',
        'o̤ⁿ': 'or',
        'o̤h': 'orh',
        'o̤ng': 'orng',
        'o': 'ou',
        'u': 'u',
        'ua': 'ua',
        'uaⁿ': 'ua',
        'uah': 'uah',
        'uang': 'uang',
        'oi': 'ue',
        'oiⁿ': 'ue',
        'oih': 'uh',
        'uh': 'uh',
        'ui': 'ui',
        'ṳ': 'y',
        'ṳh': 'yh',
        'ṳng': 'yng',
        'io̤': 'yo',
        'io̤ⁿ': 'yo',
        'io̤h': 'yoh',
        'io̤ng': 'yong',
    }

    # 聲母反向映射（平話字 → 莆拼）
    INITIAL_MAP = {
        'b': 'b', 'p': 'p', 'm': 'm',
        'd': 'd', 't': 't', 'n': 'n', 'l': 'l',
        'g': 'g', 'k': 'k', 'ng': 'ng', 'h': 'h',
        'c': 'z', 'ch': 'c', 's': 's',
        '': ''
    }

    @staticmethod
    def convert_syllable(buc_syl: str) -> str:
        """
        將平話字音節轉為莆仙話拼音
        例如: kā → ka5, sá̤ → se2
        """
        # NFD 分解，方便處理聲調標記
        syl_nfd = norm('NFD', buc_syl)

        # 提取聲調
        tone = '1'  # 預設
        for mark, num in BucToPspConverter.TONE_MARKS_TO_NUM.items():
            if mark and mark in syl_nfd:
                tone = num
                # 移除聲調標記
                syl_nfd = syl_nfd.replace(mark, '')
                break

        # NFC 正規化
        base = norm('NFC', syl_nfd)

        # 解析聲母
        initial_buc = ''
        if base.startswith('ng'):
            initial_buc = 'ng'
            base = base[2:]
        elif base.startswith('ch'):
            initial_buc = 'ch'
            base = base[2:]
        elif base and base[0] in 'bpmgkhdtnlcs':
            initial_buc = base[0]
            base = base[1:]

        # 韻母
        final_buc = base

        # 處理入聲（h結尾）
        ends_with_h = final_buc.endswith('h')
        if ends_with_h and tone in ['6', '7']:
            # 入聲調值可能需要調整
            pass

        # 映射聲母
        initial_psp = BucToPspConverter.INITIAL_MAP.get(initial_buc, initial_buc)

        # 映射韻母
        final_psp = BucToPspConverter.FINAL_MAP.get(final_buc, final_buc)

        # 組合
        return initial_psp + final_psp + tone

    @staticmethod
    def convert_word(buc_word: str) -> str:
        """
        轉換完整詞彙（多音節）
        例如: kā-sí → ka5 si2
        """
        # 分割音節（用連字號或空格）
        syllables = re.split(r'[-\s]+', buc_word)
        psp_syllables = []

        for syl in syllables:
            if syl:
                psp_syl = BucToPspConverter.convert_syllable(syl)
                psp_syllables.append(psp_syl)

        return ' '.join(psp_syllables)


def extract_from_wiktionary(input_file: Path, output_file: Path):
    """從維基詞典數據提取詞彙"""

    print("=" * 60)
    print("從維基詞典數據提取詞彙")
    print("=" * 60)
    print(f"讀取檔案：{input_file}")

    entries = {}  # {漢字: (莆拼, 權重)}
    duplicates = 0
    errors = 0

    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            # 分割欄位
            fields = line.split('\t')
            if len(fields) != 4:
                print(f"警告：第 {line_num} 行格式錯誤（欄位數不是4）：{line[:50]}")
                errors += 1
                continue

            hanzi, buc, psp_original, psp_actual = fields

            # 使用實際讀音（第4欄）
            psp = psp_actual.strip()

            # 如果沒有實際讀音，使用原始讀音
            if not psp:
                psp = psp_original.strip()

            # 如果還是沒有，嘗試從平話字轉換
            if not psp:
                try:
                    psp = BucToPspConverter.convert_word(buc)
                except Exception as e:
                    print(f"警告：第 {line_num} 行無法轉換：{hanzi} {buc} - {e}")
                    errors += 1
                    continue

            # 去重（保留第一次出現）
            if hanzi in entries:
                duplicates += 1
                continue

            # 權重：根據詞長設定
            char_count = len(hanzi)
            if char_count == 1:
                weight = 1000
            elif char_count == 2:
                weight = 800
            elif char_count == 3:
                weight = 600
            elif char_count == 4:
                weight = 500
            else:
                weight = 400

            entries[hanzi] = (psp, weight)

    print(f"\n統計：")
    print(f"  總行數：{line_num}")
    print(f"  有效詞條：{len(entries)}")
    print(f"  重複項：{duplicates}")
    print(f"  錯誤項：{errors}")

    # 寫入 YAML
    print(f"\n寫入輸出檔案：{output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Rime dictionary\n")
        f.write("# encoding: utf-8\n")
        f.write("#\n")
        f.write("# 從維基詞典提取的莆仙話詞彙\n")
        f.write("# Vocabulary extracted from Wiktionary\n")
        f.write("#\n")
        f.write("# 來源：docs/puxian_phrases_from_wikt.txt\n")
        f.write("#\n")
        f.write("---\n")
        f.write("name: vocab_from_wikt\n")
        f.write('version: "0.1.0"\n')
        f.write("use_preset_vocabulary: false\n")
        f.write("sort: by_weight\n")
        f.write("...\n\n")

        # 按權重排序寫入
        sorted_entries = sorted(entries.items(), key=lambda x: x[1][1], reverse=True)
        for hanzi, (psp, weight) in sorted_entries:
            f.write(f"{hanzi}\t{psp}\t{weight}\n")

    print(f"[OK] 完成！共 {len(entries)} 個詞條")


def main():
    """主函數"""
    base_dir = Path(__file__).parent.parent

    input_file = base_dir / "docs" / "puxian_phrases_from_wikt.txt"
    output_file = base_dir / "data" / "vocab_from_wikt.yaml"

    if not input_file.exists():
        print(f"錯誤：找不到輸入檔案 {input_file}")
        return 1

    extract_from_wiktionary(input_file, output_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
