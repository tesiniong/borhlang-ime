#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
莆仙話拼音詞庫轉換為興化平話字詞庫
Convert Puxian Pinyin dictionary to Báⁿ-uā-ci̍ dictionary
"""

import re
import sys
from pathlib import Path
from unicodedata import normalize as norm
from typing import List, Dict, Tuple, Optional

# 導入 psp_to_buc 轉換邏輯
sys.path.append(str(Path(__file__).parent.parent / "data"))
from psp_to_buc import buc_initials, buc_finals, buc_tones, psp_syllable_to_buc

class AssimilationReverser:
    """聲母類化反推器"""

    @staticmethod
    def reverse_assimilation(syllable: str, prev_final: str, dialect: str = "莆田") -> List[str]:
        """
        根據前一個音節的韻尾，反推可能的原始聲母

        Args:
            syllable: 當前音節（可能已類化）
            prev_final: 前一個音節的韻尾類型 ("ng", "h", "open", "nasal", "none")
            dialect: 方言點

        Returns:
            可能的原始音節列表
        """
        # 解析當前音節的聲母
        if syllable.startswith("ng"):
            initial = "ng"
            rest = syllable[2:]
        elif len(syllable) > 1 and syllable[0] in "bpmgkhdtnlcsz":
            initial = syllable[0]
            rest = syllable[1:]
        else:
            # 零聲母
            initial = ""
            rest = syllable

        candidates = [syllable]  # 包含原始形式

        # 根據類化規則反推
        if prev_final == "ng":
            # 當前一音節以 -ng 結尾時
            if initial == "m":
                # m 可能來自 b, p, m
                candidates.extend([f"b{rest}", f"p{rest}", f"m{rest}"])
            elif initial == "n":
                # n 可能來自 d, t, n, l, z, c, s
                candidates.extend([f"d{rest}", f"t{rest}", f"n{rest}", f"l{rest}",
                                 f"z{rest}", f"c{rest}", f"s{rest}"])
            elif initial == "ng":
                # ng 可能來自 g, k, h, ng, (zero)
                candidates.extend([f"g{rest}", f"k{rest}", f"h{rest}", f"ng{rest}", rest])

        elif prev_final == "h":
            # 當前一音節以 -h 結尾時，聲母不變
            pass

        elif prev_final == "open":
            # 當前一音節是開音節時
            if initial == "" or initial == "w":
                # 零聲母或 w 可能來自 b, p
                candidates.extend([f"b{rest}", f"p{rest}"])
            elif initial == "l":
                # l 可能來自 d, t, z, c, s, l
                candidates.extend([f"d{rest}", f"t{rest}", f"z{rest}", f"c{rest}", f"s{rest}", f"l{rest}"])
            elif initial == "" :
                # 零聲母可能來自 g, k, h, (zero)
                candidates.extend([f"g{rest}", f"k{rest}", f"h{rest}", rest])
            # m, n, ng 保持不變

        elif prev_final == "nasal":
            # 當前一音節以鼻化韻結尾時（僅某些方言）
            if initial == "m":
                candidates.extend([f"b{rest}", f"p{rest}", f"m{rest}"])
            elif initial == "n":
                if dialect in ["東海"]:
                    # 東海某些音節：n 可能來自 d, t, n, z, c, s
                    candidates.extend([f"d{rest}", f"t{rest}", f"n{rest}",
                                     f"z{rest}", f"c{rest}", f"s{rest}"])
                else:
                    candidates.extend([f"d{rest}", f"t{rest}", f"n{rest}", f"l{rest}",
                                     f"z{rest}", f"c{rest}", f"s{rest}"])
            elif initial == "l" and dialect == "東海":
                # 東海某些音節
                candidates.extend([f"d{rest}", f"t{rest}", f"l{rest}",
                                 f"z{rest}", f"c{rest}", f"s{rest}"])
            elif initial == "":
                candidates.extend([f"g{rest}", f"k{rest}", f"h{rest}", rest])

        # 去重並返回
        return list(set(candidates))

    @staticmethod
    def get_final_type(syllable: str) -> str:
        """判斷音節的韻尾類型"""
        if syllable.endswith("ng") or syllable.endswith("ung") or syllable.endswith("ang") or \
           syllable.endswith("eng") or syllable.endswith("ing") or syllable.endswith("yng") or \
           syllable.endswith("ong") or syllable.endswith("orng") or syllable.endswith("ieng") or \
           syllable.endswith("yorng") or syllable.endswith("oeng") or syllable.endswith("uang") or \
           syllable.endswith("iang"):
            return "ng"
        elif syllable.endswith("h") or syllable.endswith("ah") or syllable.endswith("eh") or \
             syllable.endswith("ih") or syllable.endswith("oh") or syllable.endswith("uh") or \
             syllable.endswith("yh") or syllable.endswith("orh") or syllable.endswith("oeh") or \
             syllable.endswith("ieh") or syllable.endswith("uah") or syllable.endswith("iah") or \
             syllable.endswith("yorh"):
            return "h"
        else:
            # 簡化判斷：如果不是 ng 或 h 結尾，視為開音節
            return "open"


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
            char_dict[char] = prons

        return char_dict


class DictConverter:
    """詞庫轉換器"""

    def __init__(self, cpx_data: Dict[str, List[str]]):
        self.cpx_data = cpx_data
        self.reverser = AssimilationReverser()
        self.warnings = []
        self.stats = {
            'total': 0,
            'success': 0,
            'multiple_matches': 0,
            'no_match': 0,
            'bracketed': 0
        }

    def convert_entry(self, hanzi: str, pinyin: str, weight: Optional[str] = None) -> Optional[Tuple[str, str, Optional[str]]]:
        """
        轉換一個詞條

        Args:
            hanzi: 漢字
            pinyin: 莆仙話拼音
            weight: 詞頻（可選）

        Returns:
            (漢字, 平話字拼音, 詞頻) 或 None
        """
        self.stats['total'] += 1

        # 解析漢字和拼音
        chars, syllables = self.parse_entry(hanzi, pinyin)

        if len(chars) != len(syllables):
            self.warnings.append(f"警告：{hanzi} {pinyin} - 漢字與音節數量不匹配")
            return None

        # 轉換每個音節
        buc_syllables = []
        prev_final_type = "none"

        for i, (char, syl) in enumerate(zip(chars, syllables)):
            is_bracketed = char.startswith('[')
            char_clean = char.strip('[]')

            # 轉換音節
            buc = self.convert_syllable(char_clean, syl, prev_final_type, is_bracketed)

            if buc is None:
                self.warnings.append(f"警告：{hanzi} {pinyin} - 無法轉換音節 {char}={syl}")
                return None

            buc_syllables.append(buc)

            # 更新前一個音節的韻尾類型（用於下一個音節的類化判斷）
            prev_final_type = self.reverser.get_final_type(syl)

        # 組合平話字拼音（用空格連接，符合 Rime 詞庫格式）
        # 注意：平話字書寫時用 - 連接，但 Rime 詞庫必須用空格
        buc_pinyin = ' '.join(buc_syllables)

        self.stats['success'] += 1
        return (hanzi, buc_pinyin, weight)

    def parse_entry(self, hanzi: str, pinyin: str) -> Tuple[List[str], List[str]]:
        """解析詞條的漢字和拼音"""
        # 處理 [括號] 內的合音字
        chars = []
        i = 0
        while i < len(hanzi):
            if hanzi[i] == '[':
                # 找到對應的 ]
                j = hanzi.find(']', i)
                if j != -1:
                    chars.append(hanzi[i:j+1])  # 包含括號
                    i = j + 1
                else:
                    chars.append(hanzi[i])
                    i += 1
            else:
                chars.append(hanzi[i])
                i += 1

        # 分割拼音（可能有 {} 包裹）
        syllables = []
        for syl in pinyin.split():
            # 移除可能的 {}
            syl = syl.strip('{}')
            syllables.append(syl)

        return chars, syllables

    def convert_syllable(self, char: str, psp_syllable: str, prev_final: str, is_bracketed: bool) -> Optional[str]:
        """
        轉換單個音節

        Args:
            char: 漢字
            psp_syllable: 莆仙話拼音音節
            prev_final: 前一個音節的韻尾類型
            is_bracketed: 是否為括號內的合音字

        Returns:
            平話字音節 或 None
        """
        # 如果是括號內的合音字，直接轉換不查字典
        if is_bracketed:
            self.stats['bracketed'] += 1
            candidates = psp_syllable_to_buc(psp_syllable)
            if candidates and not candidates[0].endswith('ERROR'):
                # 移除可能的 * 標記
                result = candidates[0].rstrip('*')
                return result
            else:
                return None

        # 1. 先嘗試直接轉換並查字典
        buc_candidates = psp_syllable_to_buc(psp_syllable)

        if buc_candidates and not buc_candidates[0].endswith('ERROR'):
            # 檢查字典中是否有這個讀音
            if char in self.cpx_data:
                char_prons = self.cpx_data[char]
                # 移除聲調標記進行比較
                for buc in buc_candidates:
                    buc_clean = self.remove_tone_marks(buc).rstrip('*')
                    for pron in char_prons:
                        pron_clean = self.remove_tone_marks(pron)
                        if buc_clean == pron_clean:
                            # 找到匹配，返回字典中的形式（帶正確聲調）
                            return pron

        # 2. 如果直接轉換沒找到，嘗試反推類化前的形式
        if prev_final != "none" and prev_final != "h":
            # 獲取可能的原始音節
            original_syllables = self.reverser.reverse_assimilation(psp_syllable, prev_final)

            for orig_syl in original_syllables:
                if orig_syl == psp_syllable:
                    continue  # 已經嘗試過了

                buc_candidates = psp_syllable_to_buc(orig_syl)
                if buc_candidates and not buc_candidates[0].endswith('ERROR'):
                    if char in self.cpx_data:
                        char_prons = self.cpx_data[char]
                        for buc in buc_candidates:
                            buc_clean = self.remove_tone_marks(buc).rstrip('*')
                            for pron in char_prons:
                                pron_clean = self.remove_tone_marks(pron)
                                if buc_clean == pron_clean:
                                    # 找到匹配
                                    return pron

        # 3. 如果還是沒找到，使用第一個轉換結果並標記
        if buc_candidates and not buc_candidates[0].endswith('ERROR'):
            result = buc_candidates[0].rstrip('*')
            if char in self.cpx_data and len(self.cpx_data[char]) > 1:
                self.stats['multiple_matches'] += 1
                self.warnings.append(f"註：{char}={psp_syllable} 使用自動轉換 {result}（字典有多個讀音：{self.cpx_data[char]}）")
            else:
                self.stats['no_match'] += 1
                self.warnings.append(f"註：{char}={psp_syllable} 使用自動轉換 {result}（字典中未找到）")
            return result

        # 轉換失敗
        return None

    @staticmethod
    def remove_tone_marks(text: str) -> str:
        """移除聲調標記"""
        # 移除所有 combining diacritics
        result = re.sub(r'[́̂̍̄]', '', text)
        return result


def convert_pouleng_dict(pouleng_file: Path, cpx_file: Path, output_file: Path):
    """轉換 Pouleng.dict.yaml 到 borhlang_bannuaci.dict.yaml"""

    print(f"讀取字典資料：{cpx_file}")
    cpx_data = LuaDictParser.parse_lua_dict(cpx_file)
    print(f"已載入 {len(cpx_data)} 個漢字的讀音資料")

    print(f"\n讀取詞庫：{pouleng_file}")
    converter = DictConverter(cpx_data)

    # 讀取原始詞庫
    with open(pouleng_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 解析 header 和詞條
    header_lines = []
    entries = []
    in_header = True

    for line in lines:
        line = line.rstrip('\n')

        if in_header:
            if line == '...':
                header_lines.append(line)
                in_header = False
            else:
                header_lines.append(line)
        else:
            # 跳過空行和註釋
            if not line.strip() or line.strip().startswith('#'):
                continue

            # 解析詞條：漢字\t拼音[\t詞頻]
            parts = line.split('\t')
            if len(parts) >= 2:
                hanzi = parts[0]
                pinyin = parts[1]
                weight = parts[2] if len(parts) > 2 else None

                result = converter.convert_entry(hanzi, pinyin, weight)
                if result:
                    entries.append(result)

    # 寫入輸出文件
    print(f"\n寫入輸出檔案：{output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        # 寫入 header（修改名稱和版本）
        f.write("# Rime dictionary\n")
        f.write("# encoding: utf-8\n")
        f.write("#\n")
        f.write("# 興化平話字詞庫 Báⁿ-uā-ci̍ Dictionary\n")
        f.write("# 基於莆田城區口音 Based on Putian downtown accent\n")
        f.write("#\n")
        f.write("# 本詞庫由莆仙話拼音詞庫自動轉換而來\n")
        f.write("# Auto-converted from Puxian Pinyin dictionary\n")
        f.write("#\n")
        f.write("---\n")
        f.write("name: borhlang_bannuaci\n")
        f.write('version: "0.1.0"\n')
        f.write("use_preset_vocabulary: false\n")
        f.write("sort: by_weight\n")
        f.write("...\n\n")

        # 寫入詞條
        for hanzi, buc_pinyin, weight in entries:
            if weight:
                f.write(f"{hanzi}\t{buc_pinyin}\t{weight}\n")
            else:
                f.write(f"{hanzi}\t{buc_pinyin}\n")

    # 輸出統計和警告
    print(f"\n轉換完成！")
    print(f"總詞條數：{converter.stats['total']}")
    print(f"成功轉換：{converter.stats['success']}")
    print(f"括號合音字：{converter.stats['bracketed']}")
    print(f"多個匹配：{converter.stats['multiple_matches']}")
    print(f"未找到匹配：{converter.stats['no_match']}")

    # 將警告寫入日誌文件
    log_file = output_file.parent / "conversion_log.txt"
    with open(log_file, 'w', encoding='utf-8') as f:
        for warning in converter.warnings:
            f.write(warning + '\n')

    print(f"\n警告和註記已寫入：{log_file}")
    print(f"共 {len(converter.warnings)} 條")


if __name__ == "__main__":
    # 設定路徑
    project_root = Path(__file__).parent.parent
    pouleng_file = project_root / "hinghwa-ime" / "Pouleng" / "Pouleng.dict.yaml"
    cpx_file = project_root / "data" / "cpx-pron-data.lua"
    output_file = project_root / "bannuaci" / "borhlang_bannuaci.dict.yaml"

    # 執行轉換
    convert_pouleng_dict(pouleng_file, cpx_file, output_file)
