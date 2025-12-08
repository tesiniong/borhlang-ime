#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從興化平話字聖經提取詞彙
Extract vocabulary from Hinghwa Bible text

輸入：docs/hinghua_bible.txt
輸出：data/vocab_from_bible.yaml (輸入式平話字格式)
"""

import re
import sys
from pathlib import Path
from collections import defaultdict, Counter
from unicodedata import normalize as norm

# 導入轉換模組
sys.path.append(str(Path(__file__).parent.parent / "data"))
from romanization_converter import RomanizationConverter


class BibleVocabExtractor:
    """聖經詞彙提取器"""

    def __init__(self):
        self.vocab = defaultdict(Counter)  # {漢字: Counter({輸入式: 次數})}
        self.stats = {
            'total_lines': 0,
            'buc_lines': 0,
            'hanzi_lines': 0,
            'title_lines': 0,
            'aligned_pairs': 0,
            '合音字_count': 0,
            'errors': 0
        }

    def is_title_line(self, line: str) -> bool:
        """判斷是否為標題行"""
        # 章節標題通常只有兩個詞，且第一個詞首字母大寫
        if not line:
            return False

        # 去除小節標記（如 "1:1"）
        line_clean = re.sub(r'^\d+:\d+\s+', '', line)

        # 標題特徵：
        # 1. 很短（少於20字符）
        # 2. 包含大寫字母開頭
        # 3. 沒有太多標點符號
        if len(line_clean) < 30 and line_clean[0].isupper():
            return True

        # "Dā̤ 1 Ca̤uⁿ" 這種格式
        if re.match(r'^[A-Z][^\s]+\s+\d+\s+', line):
            return True

        return False

    def extract_verse_number(self, line: str) -> tuple:
        """提取小節編號，返回 (編號, 剩餘文本)"""
        match = re.match(r'^(\d+:\d+)\s+(.+)$', line)
        if match:
            return match.group(1), match.group(2)
        return None, line

    def parse_合音字(self, hanzi_text: str) -> dict:
        """
        解析合音字標記
        返回 {位置: (合音字, 對應漢字)}
        """
        合音字_map = {}
        # 尋找「」標記
        pattern = r'「([^」]+)」'
        for match in re.finditer(pattern, hanzi_text):
            合音字 = match.group(1)
            start = match.start()
            合音字_map[start] = 合音字
        return 合音字_map

    def align_buc_hanzi(self, buc_line: str, hanzi_line: str) -> list:
        """
        對齊平話字和漢字
        空格 = 詞邊界，連字號 = 音節邊界
        返回 [(平話字詞, 漢字詞), ...]
        """
        # 移除小節標記
        _, buc_text = self.extract_verse_number(buc_line)
        _, hanzi_text = self.extract_verse_number(hanzi_line)

        # 處理合音字標記「」
        合音字_list = []
        for match in re.finditer(r'「([^」]+)」', hanzi_text):
            合音字_list.append(match.group(1))

        # 清理標記
        hanzi_clean = re.sub(r'「|」', '', hanzi_text)

        # 處理重複符號「々」
        def expand_repetition(text):
            result = []
            for i, char in enumerate(text):
                if char == '々' and i > 0:
                    result.append(result[-1])  # 重複前一個字
                else:
                    result.append(char)
            return ''.join(result)

        hanzi_clean = expand_repetition(hanzi_clean)

        # 移除標點符號（包括括號、引號等）
        # 包含：逗號、分號、句號、冒號、驚嘆號、問號、頓號、括號、各種引號
        # 使用 Unicode escape 確保所有引號類型都被移除
        punct_pattern = r'[,，;；:.。:：!！?？、()（）\u0022\u0027\u2018\u2019\u201C\u201D]'
        buc_no_punct = re.sub(punct_pattern, '', buc_text)
        hanzi_no_punct = re.sub(punct_pattern, '', hanzi_clean)

        # 平話字按空格分詞
        buc_words = buc_no_punct.split()

        # 漢字是連續的（沒有空格），轉為字符列表
        hanzi_chars = list(hanzi_no_punct)

        # 對齊：根據平話字詞的音節數，從漢字中提取對應的字
        pairs = []
        hanzi_idx = 0

        for buc_word in buc_words:
            if hanzi_idx >= len(hanzi_chars):
                break

            # 計算音節數
            buc_syllables = buc_word.split('-')
            syllable_count = len(buc_syllables)

            # 檢查接下來的漢字是否包含非漢字字符
            # 先 peek 看看接下來的字符
            end_idx = min(hanzi_idx + syllable_count, len(hanzi_chars))
            potential_hanzi = ''.join(hanzi_chars[hanzi_idx:end_idx])

            # 如果包含羅馬字，嘗試找到對應的羅馬字詞並跳過
            if re.search(r'[a-zA-Z]', potential_hanzi):
                # 找到完整的羅馬字詞（連續的字母+連字號）
                while hanzi_idx < len(hanzi_chars):
                    char = hanzi_chars[hanzi_idx]
                    if not re.match(r'[a-zA-Ź̤̂̄̍̀ⁿ-]', char):
                        break
                    hanzi_idx += 1
                continue

            # 檢查是否為合音字
            is_合音字 = False
            for 合音字 in 合音字_list:
                if hanzi_idx + len(合音字) <= len(hanzi_chars):
                    potential = ''.join(hanzi_chars[hanzi_idx:hanzi_idx + len(合音字)])
                    if potential == 合音字:
                        pairs.append((buc_word, 合音字))
                        hanzi_idx += len(合音字)
                        self.stats['合音字_count'] += 1
                        is_合音字 = True
                        break

            if is_合音字:
                continue

            # 普通對齊
            if hanzi_idx + syllable_count <= len(hanzi_chars):
                hanzi_word = ''.join(hanzi_chars[hanzi_idx:hanzi_idx + syllable_count])
                pairs.append((buc_word, hanzi_word))
                hanzi_idx += syllable_count

        return pairs

    def extract_words(self, pairs: list):
        """從對齊的詞對中提取詞彙"""
        for buc_word, hanzi_word in pairs:
            # 轉換為輸入式
            try:
                # 分割音節（用連字號或空格）
                syllables = re.split(r'[-\s]+', buc_word)
                input_syllables = []

                for buc_syl in syllables:
                    if buc_syl:
                        # 轉小寫（處理專有名詞）
                        buc_syl_lower = buc_syl[0].lower() + buc_syl[1:] if buc_syl and buc_syl[0].isupper() else buc_syl

                        # 平話字 -> 輸入式
                        input_syl = RomanizationConverter.buc_to_input(buc_syl_lower)
                        input_syllables.append(input_syl)

                input_word = ' '.join(input_syllables)
                self.vocab[hanzi_word][input_word] += 1
            except Exception as e:
                # 忽略轉換失敗的詞
                pass

    def process_file(self, input_file: Path):
        """處理聖經檔案"""
        print("=" * 60)
        print("從興化平話字聖經提取詞彙")
        print("=" * 60)
        print(f"讀取檔案：{input_file}")

        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            self.stats['total_lines'] += 1
            line = lines[i].strip()

            # 跳過空行
            if not line:
                i += 1
                continue

            # 跳過標題行
            if self.is_title_line(line):
                self.stats['title_lines'] += 1
                i += 1
                continue

            # 檢查是否為平話字行（含小節標記或首字母大寫）
            verse_num, text = self.extract_verse_number(line)
            is_buc_line = verse_num is not None or (text and text[0].isupper())

            if is_buc_line:
                # 這是平話字行，下一行應該是漢字
                buc_line = line
                self.stats['buc_lines'] += 1

                if i + 1 < len(lines):
                    hanzi_line = lines[i + 1].strip()
                    self.stats['hanzi_lines'] += 1

                    # 對齊並提取
                    try:
                        pairs = self.align_buc_hanzi(buc_line, hanzi_line)
                        self.stats['aligned_pairs'] += len(pairs)

                        # 提取詞彙（直接使用連字號分隔的詞）
                        self.extract_words(pairs)

                    except Exception as e:
                        self.stats['errors'] += 1
                        print(f"警告：第 {i+1} 行處理失敗：{str(e)[:50]}")

                    i += 2  # 跳過兩行
                else:
                    i += 1
            else:
                i += 1

        # 打印統計
        print(f"\n統計：")
        for key, value in self.stats.items():
            print(f"  {key}: {value}")
        print(f"  唯一詞彙數：{len(self.vocab)}")

    def write_output(self, output_file: Path, min_freq=1):
        """寫入輸出檔案"""
        print(f"\n寫入輸出檔案：{output_file}")

        # 過濾：保留出現次數 >= min_freq 的詞
        filtered_vocab = {}
        for hanzi, input_counter in self.vocab.items():
            # 選擇出現次數最多的拼音
            if input_counter:
                most_common_input, freq = input_counter.most_common(1)[0]
                if freq >= min_freq:
                    filtered_vocab[hanzi] = (most_common_input, freq)

        print(f"  過濾後（頻次 >= {min_freq}）：{len(filtered_vocab)} 個詞條")

        # 寫入 YAML
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Rime dictionary\n")
            f.write("# encoding: utf-8\n")
            f.write("#\n")
            f.write("# 從興化平話字聖經提取的詞彙\n")
            f.write("# Vocabulary extracted from Hinghwa Bible\n")
            f.write("#\n")
            f.write("# 來源：docs/hinghua_bible.txt\n")
            f.write(f"# 最小頻次：{min_freq}\n")
            f.write("#\n")
            f.write("---\n")
            f.write("name: vocab_from_bible\n")
            f.write('version: "0.1.0"\n')
            f.write("use_preset_vocabulary: false\n")
            f.write("sort: by_weight\n")
            f.write("...\n\n")

            # 按頻次排序
            sorted_vocab = sorted(filtered_vocab.items(), key=lambda x: x[1][1], reverse=True)

            for hanzi, (input_form, freq) in sorted_vocab:
                # 權重 = 頻次 * 100（讓常用詞排在前面）
                weight = min(freq * 100, 5000)  # 上限5000
                f.write(f"{hanzi}\t{input_form}\t{weight}\n")

        print(f"[OK] 完成！共 {len(filtered_vocab)} 個詞條")


def main():
    """主函數"""
    base_dir = Path(__file__).parent.parent

    input_file = base_dir / "docs" / "hinghua_bible.txt"
    output_file = base_dir / "data" / "vocab_from_bible.yaml"

    if not input_file.exists():
        print(f"錯誤：找不到輸入檔案 {input_file}")
        return 1

    extractor = BibleVocabExtractor()
    extractor.process_file(input_file)
    extractor.write_output(output_file, min_freq=1)  # 降低閾值，保留所有詞彙

    return 0


if __name__ == "__main__":
    sys.exit(main())
