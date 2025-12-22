#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從莆仙語聖經 JSON 提取詞表
Extract vocabulary from Puxian Bible JSON data

輸入：data/bible_data.json (平話字格式)
輸出：data/vocab_from_bible.yaml (輸入式平話字格式，保留鼻化韻)
轉換：平話字 (BUC) -> 輸入式 (Input)
"""

import json
import sys
import re
from pathlib import Path
from collections import Counter
from unicodedata import normalize as norm

# 導入轉換模組（從 data/ 目錄）
sys.path.append(str(Path(__file__).parent.parent / "data"))
from romanization_converter import RomanizationConverter


def extract_multi_syllable_words_from_text(text: str) -> list:
    """
    從文本中提取多音節詞（連字號分隔的詞）

    Args:
        text: 平話字文本

    Returns:
        list: 多音節詞列表（BUC 格式）
    """
    # 正則表達式：匹配連字號分隔的詞
    # 允許的字符：a-z、特殊字母（帶音調符號）、連字號
    pattern = r'[a-zA-Zⁿṳ̤̍̄̂́]+(?:-[a-zA-Zⁿṳ̤̍̄̂́]+)+'

    words = re.findall(pattern, text)

    # 過濾：只保留多音節詞（2個或以上音節）
    multi_syllable_words = []
    for word in words:
        syllables = word.split('-')

        # 過濾掉只有1個音節的
        if len(syllables) < 2:
            continue

        # 過濾掉包含無效音節的（例如只有音調符號的或太短的）
        valid = True
        for syl in syllables:
            # 移除音調符號後，音節應該至少有1個拉丁字母
            cleaned = re.sub(r'[̤̍̄̂́ⁿ]', '', syl)

            # 音節必須非空且包含至少1個拉丁字母
            if not cleaned or not re.search(r'[a-zA-Zṳ]', cleaned):
                valid = False
                break

            # 音節長度檢查：至少2個字符（去除音調符號後）
            # 這樣可以過濾掉 's1'、'h6'、'd1' 等不完整的音節
            if len(cleaned) < 2:
                valid = False
                break

            # 音節必須以拉丁字母開頭（不能以音調符號開頭）
            if not re.match(r'^[a-zA-Zṳ]', syl):
                valid = False
                break

        if valid:
            multi_syllable_words.append(word)

    return multi_syllable_words


def generate_vocab_list(input_file: Path, output_file: Path):
    """
    從莆仙語聖經 JSON 提取詞表

    Args:
        input_file: bible_data.json 路徑
        output_file: 輸出的 YAML 詞典路徑（輸入式格式）
    """

    print("=" * 60)
    print("從聖經 JSON 提取詞彙")
    print("=" * 60)
    print(f"讀取檔案：{input_file}")

    # 使用 Counter 來自動計算詞頻
    # Key 為 (漢字, 輸入式) 的 tuple，Value 為出現次數
    vocab_counter = Counter()

    # 統計資訊
    stats = {
        'total_tokens': 0,
        'valid_tokens': 0,
        'conversion_errors': 0,
        'rom_only_sections': 0,
        'rom_only_multi_syllable': 0,
        'unique_entries': 0
    }

    # 錯誤日誌
    error_log = []

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 開始遍歷 JSON 結構
        # 結構層級: Books -> Chapters -> Sections -> Tokens
        books = data.get("books", [])

        for book in books:
            book_name = book.get("name_rom", "")
            chapters = book.get("chapters", [])

            for chapter in chapters:
                sections = chapter.get("sections", [])
                for section in sections:
                    # 處理 tokens（有漢字和羅馬字的）
                    tokens = section.get("tokens", [])

                    for token in tokens:
                        stats['total_tokens'] += 1

                        han = token.get("han", "").strip()
                        rom_buc = token.get("rom", "").strip()

                        # 過濾：必須同時有漢字和羅馬字
                        if not (han and rom_buc):
                            continue

                        # 轉換平話字 -> 輸入式
                        try:
                            # 處理多音節詞（用連字號分隔）
                            syllables_buc = rom_buc.split('-')
                            syllables_input = []

                            for syl_buc in syllables_buc:
                                # 跳過空音節
                                if not syl_buc:
                                    continue

                                # 處理專有名詞（首字母大寫）
                                if syl_buc and syl_buc[0].isupper():
                                    syl_buc = syl_buc[0].lower() + syl_buc[1:]

                                # 轉換：平話字 -> 輸入式（保留鼻化韻 nn）
                                try:
                                    syl_input = RomanizationConverter.buc_to_input(syl_buc)
                                    syllables_input.append(syl_input)
                                except ValueError as e:
                                    # 無法轉換的音節，記錄但跳過整個詞
                                    raise Exception(f"音節轉換失敗 '{syl_buc}' -> 輸入式: {e}")

                            # 組合音節（用空格分隔）
                            rom_input = ' '.join(syllables_input)

                            # 計數
                            vocab_counter[(han, rom_input)] += 1
                            stats['valid_tokens'] += 1

                        except Exception as e:
                            # 轉換失敗，記錄到日誌
                            stats['conversion_errors'] += 1
                            error_log.append({
                                'han': han,
                                'rom_buc': rom_buc,
                                'error': str(e)
                            })

                    # 處理只有羅馬字沒有漢字的 sections
                    section_rom = section.get("rom", "").strip()
                    section_han = section.get("han", "").strip()

                    if section_rom and not section_han and book_name != "Foreword":
                        stats['rom_only_sections'] += 1

                        # 從 section.rom 中提取多音節詞
                        extracted_words = extract_multi_syllable_words_from_text(section_rom)

                        for word_buc in extracted_words:
                            try:
                                # 轉換 BUC -> Input
                                syllables_buc = word_buc.split('-')
                                syllables_input = []

                                for syl_buc in syllables_buc:
                                    if not syl_buc:
                                        continue

                                    # 處理大寫（專有名詞）
                                    if syl_buc and syl_buc[0].isupper():
                                        syl_buc = syl_buc[0].lower() + syl_buc[1:]

                                    syl_input = RomanizationConverter.buc_to_input(syl_buc)
                                    syllables_input.append(syl_input)

                                rom_input = ' '.join(syllables_input)

                                # 使用特殊標記表示無漢字
                                # 用 ▣ 作為佔位符，數量對應音節數
                                han_placeholder = '▣' * len(syllables_input)

                                # 計數（使用特殊標記來區分無漢字的詞）
                                vocab_counter[(han_placeholder, rom_input)] += 1
                                stats['rom_only_multi_syllable'] += 1

                            except Exception as e:
                                # 轉換失敗，靜默跳過（避免噪音）
                                pass

        stats['unique_entries'] = len(vocab_counter)

        # 打印統計
        print(f"\n統計：")
        for key, value in stats.items():
            print(f"  {key}: {value}")

        # 寫入 YAML 詞典
        print(f"\n寫入輸出檔案：{output_file}")
        write_yaml_dict(output_file, vocab_counter)

        # 寫入錯誤日誌
        if error_log:
            error_log_file = output_file.parent / "bible_conversion_errors.log"
            print(f"\n寫入錯誤日誌：{error_log_file}")
            with open(error_log_file, 'w', encoding='utf-8') as f:
                f.write("# 聖經詞彙轉換錯誤日誌\n")
                f.write(f"# 總錯誤數：{len(error_log)}\n\n")
                for i, err in enumerate(error_log[:50], 1):  # 只記錄前50個
                    f.write(f"{i}. {err['han']} | {err['rom_buc']} | {err['error']}\n")

        print(f"\n[OK] 完成！")
        return 0

    except FileNotFoundError:
        print(f"[ERROR] 找不到檔案：{input_file}")
        return 1
    except json.JSONDecodeError:
        print(f"[ERROR] JSON 格式錯誤：{input_file}")
        return 1
    except Exception as e:
        print(f"[ERROR] 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return 1


def write_yaml_dict(output_file: Path, vocab_counter: Counter):
    """
    寫入 Rime YAML 詞典格式（輸入式平話字）

    權重設定：
    - 基於頻次，但上限 300（聖經術語相對少見）
    - 頻次 1-2 次：權重 50
    - 頻次 3-5 次：權重 100
    - 頻次 6-10 次：權重 150
    - 頻次 11-20 次：權重 200
    - 頻次 21+ 次：權重 250-300
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        # 寫入標頭
        f.write("# Rime dictionary\n")
        f.write("# encoding: utf-8\n")
        f.write("#\n")
        f.write("# 從興化平話字聖經提取的詞彙\n")
        f.write("# Vocabulary extracted from Hinghwa Bible\n")
        f.write("#\n")
        f.write("# 來源：data/bible_data.json (平話字格式)\n")
        f.write("# 格式：漢字 + 輸入式平話字 (Input-form，保留鼻化韻 nn)\n")
        f.write("# 權重上限：300（聖經術語相對少見）\n")
        f.write("#\n")
        f.write("# 注意：本詞表保留輸入式格式而非莆拼，以保留鼻化韻資訊\n")
        f.write("#       供 bannuaci 輸入法直接使用，需用於 pouseng_pinging 時再轉換\n")
        f.write("#\n")
        f.write("---\n")
        f.write("name: vocab_from_bible\n")
        f.write('version: "0.2.0"\n')
        f.write("use_preset_vocabulary: false\n")
        f.write("sort: by_weight\n")
        f.write("...\n\n")

        # 按頻次排序
        sorted_vocab = vocab_counter.most_common()

        for (han, rom_input), count in sorted_vocab:
            # 根據頻次計算權重
            if count <= 2:
                weight = 50
            elif count <= 5:
                weight = 100
            elif count <= 10:
                weight = 150
            elif count <= 20:
                weight = 200
            elif count <= 50:
                weight = 250
            else:
                weight = 300  # 上限

            f.write(f"{han}\t{rom_input}\t{weight}\n")


def main():
    """主函數"""
    base_dir = Path(__file__).parent.parent  # 回到專案根目錄

    input_file = base_dir / "data" / "bible_data.json"
    output_file = base_dir / "data" / "vocab_from_bible.yaml"

    if not input_file.exists():
        print(f"[ERROR] 找不到輸入檔案：{input_file}")
        return 1

    return generate_vocab_list(input_file, output_file)


if __name__ == "__main__":
    sys.exit(main())