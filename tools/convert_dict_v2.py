#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
莆仙話拼音詞庫轉換為興化平話字詞庫（拼式版本）
Convert Puxian Pinyin dictionary to Báⁿ-uā-ci̍ dictionary (romanization version)

本版本輸出拼式（純 ASCII + 聲調數字），而非完整平話字
"""

import re
import sys
from pathlib import Path
from unicodedata import normalize as norm
from typing import List, Dict, Tuple, Optional, Set

# 導入 psp_to_buc 轉換邏輯
sys.path.append(str(Path(__file__).parent.parent / "data"))
from psp_to_buc import buc_initials, buc_finals, buc_tones


class BucRomanizer:
    """平話字拼式轉換器（輸出純 ASCII 拼式）"""

    @staticmethod
    def psp_to_buc_romanization(psp_syllable: str) -> Optional[str]:
        """
        將莆仙話拼音音節轉換為平話字拼式

        Args:
            psp_syllable: 莆仙話拼音音節（如 ka5, yor3）

        Returns:
            平話字拼式（如 ka5, yor3）或 None
        """
        # 驗證輸入格式
        if not psp_syllable or not psp_syllable[-1].isdigit():
            return None

        # 解析聲母和韻母+聲調
        if psp_syllable.startswith("ng") and len(psp_syllable) == 3:
            initial = ""
            finaltone = psp_syllable
        elif psp_syllable.startswith("ng") or psp_syllable.startswith("ch"):
            initial = psp_syllable[:2]
            finaltone = psp_syllable[2:]
        elif psp_syllable[0] in buc_initials:
            initial = psp_syllable[0]
            finaltone = psp_syllable[1:]
        else:
            initial = ""
            finaltone = psp_syllable

        # 分離韻母和聲調
        final = finaltone[:-1]
        tone = finaltone[-1]

        # 驗證聲調
        if tone not in buc_tones:
            return None

        # 轉換聲母
        if initial in buc_initials:
            buc_initial = buc_initials[initial]
        else:
            return None

        # 轉換韻母
        # 處理常見的變體（容錯）
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

        if final in final_map:
            final = final_map[final]

        if final not in buc_finals:
            return None

        # 獲取韻母信息（取第一個候選）
        buc_final_info = buc_finals[final][0]
        buc_final = buc_final_info[0]

        # 處理特殊情況（入聲韻尾）
        # 莆拼中的入聲 h 在平話字中有時也用 h 表示
        if final.endswith("h") and not buc_final.endswith("h"):
            # 某些韻母莆拼有 h 但平話字沒有，需要添加
            pass

        # 構建拼式：聲母 + 韻母拼式 + 聲調數字
        # 韻母拼式：將特殊字元轉為 ASCII
        romanized_final = BucRomanizer.buc_final_to_romanization(buc_final)

        return buc_initial + romanized_final + tone

    @staticmethod
    def buc_final_to_romanization(buc_final: str) -> str:
        """
        將平話字韻母轉換為拼式

        a̤ → aa
        e̤ → ee
        o̤ → oo
        ṳ → y
        ⁿ → nn
        """
        result = buc_final
        result = result.replace('a̤', 'aa')
        result = result.replace('e̤', 'ee')
        result = result.replace('o̤', 'oo')
        result = result.replace('ṳ', 'y')
        result = result.replace('ⁿ', 'nn')
        return result


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
    """詞庫轉換器（拼式版本）"""

    def __init__(self, cpx_data: Dict[str, List[str]]):
        self.cpx_data = cpx_data
        self.romanizer = BucRomanizer()
        self.warnings = []
        self.stats = {
            'total': 0,
            'success': 0,
            'from_dict': 0,
            'from_conversion': 0,
            'failed': 0,
            'bracketed': 0
        }
        self.seen_entries: Set[Tuple[str, str]] = set()  # 用於去重

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

        # 轉換每個音節
        romanized_syllables = []

        for i, (char, psp_syl) in enumerate(zip(chars, syllables)):
            is_bracketed = char.startswith('[')
            char_clean = char.strip('[]')

            # 轉換音節為拼式
            rom_syl = self.convert_syllable(char_clean, psp_syl, is_bracketed)

            if rom_syl is None:
                self.warnings.append(f"警告：{hanzi} {pinyin} - 無法轉換音節 {char}={psp_syl}")
                self.stats['failed'] += 1
                return None

            romanized_syllables.append(rom_syl)

        # 組合拼式（用空格連接）
        romanization = ' '.join(romanized_syllables)

        # 去重檢查
        entry_key = (hanzi, romanization)
        if entry_key in self.seen_entries:
            return None  # 跳過重複項
        self.seen_entries.add(entry_key)

        self.stats['success'] += 1
        return (hanzi, romanization, weight)

    def parse_entry(self, hanzi: str, pinyin: str) -> Tuple[List[str], List[str]]:
        """解析詞條的漢字和拼音"""
        # 處理 [括號] 內的合音字
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

        # 分割拼音
        syllables = []
        for syl in pinyin.split():
            syl = syl.strip('{}')
            syllables.append(syl)

        return chars, syllables

    def convert_syllable(self, char: str, psp_syllable: str, is_bracketed: bool) -> Optional[str]:
        """
        轉換單個音節為拼式

        Returns:
            拼式（如 ka5, yor3）或 None
        """
        # 如果是括號內的合音字，直接轉換
        if is_bracketed:
            self.stats['bracketed'] += 1
            result = self.romanizer.psp_to_buc_romanization(psp_syllable)
            if result:
                self.stats['from_conversion'] += 1
            return result

        # 查字典：將字典中的平話字轉換為拼式進行匹配
        if char in self.cpx_data:
            char_prons_buc = self.cpx_data[char]
            # 將莆拼轉換為平話字拼式
            psp_rom = self.romanizer.psp_to_buc_romanization(psp_syllable)

            if psp_rom:
                # 移除聲調進行匹配
                psp_rom_no_tone = psp_rom[:-1]  # 去掉最後的數字

                for buc_pron in char_prons_buc:
                    # 將字典中的平話字轉換為拼式
                    buc_rom = self.buc_to_romanization(buc_pron)
                    buc_rom_no_tone = re.sub(r'\d$', '', buc_rom)  # 去掉聲調數字

                    if psp_rom_no_tone == buc_rom_no_tone:
                        # 找到匹配！返回帶聲調的拼式
                        self.stats['from_dict'] += 1
                        return buc_rom

        # 字典中未找到，使用直接轉換
        result = self.romanizer.psp_to_buc_romanization(psp_syllable)
        if result:
            self.stats['from_conversion'] += 1
            self.warnings.append(f"註：{char}={psp_syllable} 使用直接轉換 {result}")
        return result

    def buc_to_romanization(self, buc_syllable: str) -> str:
        """
        將平話字音節轉換為拼式

        例如：kā → ka5, sâ̤ → saa3, guáⁿ → guann2
        """
        # 提取聲調
        tone_map = {
            '': '1',      # 無標記 = 第1調
            '́': '2',     # acute
            '̂': '3',     # circumflex
            '̍': '4',     # vertical line
            '̄': '5',     # macron
        }

        syllable = norm('NFD', buc_syllable)  # 分解組合字元

        # 尋找聲調標記
        tone = '1'  # 預設第1調
        for mark, tone_num in tone_map.items():
            if mark and mark in syllable:
                tone = tone_num
                syllable = syllable.replace(mark, '')
                break

        # 處理入聲（第6、7調）
        if syllable.endswith('h'):
            # 檢查是否有聲調標記
            # 如果有 macron (̄) = 第6調，如果有 vertical line (̍) = 第7調
            # 已經在上面處理過了，但入聲需要特殊處理
            if tone == '5':  # macron → 第6調（陰入）
                tone = '6'
            elif tone == '4':  # vertical line → 第7調（陽入）
                tone = '7'
            elif tone == '1':  # 無標記的 -h = 第6調
                tone = '6'

        syllable = norm('NFC', syllable)  # 重新組合

        # 轉換特殊字元為 ASCII
        romanization = self.romanizer.buc_final_to_romanization(syllable)

        return romanization + tone

    def add_cpx_dict_entries(self) -> List[Tuple[str, str, Optional[str]]]:
        """
        從 cpx 字典添加單字詞條

        Returns:
            單字詞條列表
        """
        entries = []
        for char, prons in self.cpx_data.items():
            # 跳過括號內的字（合音字）
            if '[' in char or ']' in char:
                continue

            for pron in prons:
                # 轉換為拼式
                rom = self.buc_to_romanization(pron)

                # 去重檢查
                entry_key = (char, rom)
                if entry_key not in self.seen_entries:
                    self.seen_entries.add(entry_key)
                    entries.append((char, rom, None))

        return entries


def convert_pouleng_dict(pouleng_file: Path, cpx_file: Path, output_file: Path):
    """轉換詞庫（拼式版本）"""

    print(f"讀取字典資料：{cpx_file}")
    cpx_data = LuaDictParser.parse_lua_dict(cpx_file)
    print(f"已載入 {len(cpx_data)} 個漢字的讀音資料")

    print(f"\n讀取詞庫：{pouleng_file}")
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

    # 添加 cpx 字典的單字詞條
    print(f"\n添加 cpx 字典的單字詞條...")
    cpx_entries = converter.add_cpx_dict_entries()
    print(f"從 cpx 字典添加了 {len(cpx_entries)} 個單字詞條")
    entries.extend(cpx_entries)

    # 寫入輸出文件
    print(f"\n寫入輸出檔案：{output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        # 寫入 header
        f.write("# Rime dictionary\n")
        f.write("# encoding: utf-8\n")
        f.write("#\n")
        f.write("# 興化平話字詞庫（拼式版本）Báⁿ-uā-ci̍ Dictionary (Romanization)\n")
        f.write("# 基於莆田城區口音 Based on Putian downtown accent\n")
        f.write("#\n")
        f.write("# 本詞庫儲存純 ASCII 拼式（如 saa3, guann2）\n")
        f.write("# 實際顯示的平話字由 comment_format 動態產生\n")
        f.write("#\n")
        f.write("---\n")
        f.write("name: borhlang_bannuaci\n")
        f.write('version: "0.2.0"\n')
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
    print(f"\n轉換完成！")
    print(f"總詞條數：{converter.stats['total']}")
    print(f"成功轉換：{converter.stats['success']}")
    print(f"  - 從字典匹配：{converter.stats['from_dict']}")
    print(f"  - 從規則轉換：{converter.stats['from_conversion']}")
    print(f"括號合音字：{converter.stats['bracketed']}")
    print(f"轉換失敗：{converter.stats['failed']}")
    print(f"去重後總數：{len(entries)}")

    # 將警告寫入日誌文件
    log_file = output_file.parent / "conversion_log_v2.txt"
    with open(log_file, 'w', encoding='utf-8') as f:
        for warning in converter.warnings:
            f.write(warning + '\n')

    print(f"\n轉換日誌已寫入：{log_file}")
    print(f"共 {len(converter.warnings)} 條")


if __name__ == "__main__":
    # 設定路徑
    project_root = Path(__file__).parent.parent
    pouleng_file = project_root / "hinghwa-ime" / "Pouleng" / "Pouleng.dict.yaml"
    cpx_file = project_root / "data" / "cpx-pron-data.lua"
    output_file = project_root / "bannuaci" / "borhlang_bannuaci.dict.yaml"

    # 執行轉換
    convert_pouleng_dict(pouleng_file, cpx_file, output_file)
