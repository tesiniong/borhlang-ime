#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一鍵更新所有詞表
Build all dictionaries from all data sources

工作流程：
1. 從維基詞典提取詞彙 (docs/puxian_phrases_from_wikt.txt)
2. 從聖經文本提取詞彙 (docs/hinghua_bible.txt)
3. 合併所有詞彙到 pouseng_pinging/borhlang_pouleng.dict.yaml
4. 轉換為平話字詞表 (bannuaci/borhlang_bannuaci.dict.yaml)
5. 生成純平話字詞表 (bannuaci/borhlang_bannuaci.dict.yaml with Lua format)
"""

import sys
import subprocess
from pathlib import Path
from collections import defaultdict
import yaml


def run_script(script_path: Path, description: str):
    """執行 Python 腳本"""
    print("\n" + "=" * 70)
    print(f">>> {description}")
    print("=" * 70)

    try:
        # 使用系統預設編碼（Windows 為 cp950/gbk）
        import locale
        system_encoding = locale.getpreferredencoding()

        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            capture_output=True,
            text=True,
            encoding=system_encoding,
            errors='replace'  # 替換無法解碼的字符
        )
        print(result.stdout)
        if result.stderr:
            print("警告：", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 錯誤：腳本執行失敗")
        print(f"返回碼：{e.returncode}")
        if e.stdout:
            print("標準輸出：", e.stdout)
        if e.stderr:
            print("錯誤輸出：", e.stderr)
        return False


def merge_vocabularies(base_dir: Path):
    """合併所有詞彙來源"""
    print("\n" + "=" * 70)
    print(">>> 合併所有詞彙來源")
    print("=" * 70)

    # 數據源
    sources = {
        'base': base_dir / "pouseng_pinging" / "borhlang_pouleng.dict.yaml",
        'wikt': base_dir / "data" / "vocab_from_wikt.yaml",
        'bible': base_dir / "data" / "vocab_from_bible.yaml",
    }

    # 合併後的輸出
    output_file = base_dir / "pouseng_pinging" / "borhlang_pouleng.dict.yaml"
    backup_file = base_dir / "pouseng_pinging" / "borhlang_pouleng.dict.yaml.backup"

    # 備份原始檔案
    if output_file.exists():
        import shutil
        shutil.copy(output_file, backup_file)
        print(f"[OK] 已備份原始檔案到：{backup_file.name}")

    # 讀取所有詞條
    all_entries = {}  # {(漢字, 拼音): 權重}

    # 讀取基礎詞庫（權重最高）
    print(f"\n讀取基礎詞庫：{sources['base'].name}")
    base_entries = read_dict_entries(sources['base'])
    for (hanzi, pinyin), weight in base_entries.items():
        all_entries[(hanzi, pinyin)] = weight
    print(f"  詞條數：{len(base_entries)}")

    # 讀取維基詞典詞彙
    if sources['wikt'].exists():
        print(f"\n讀取維基詞典詞彙：{sources['wikt'].name}")
        wikt_entries = read_dict_entries(sources['wikt'])
        new_count = 0
        for (hanzi, pinyin), weight in wikt_entries.items():
            if (hanzi, pinyin) not in all_entries:
                all_entries[(hanzi, pinyin)] = weight
                new_count += 1
        print(f"  詞條數：{len(wikt_entries)}")
        print(f"  新增：{new_count}")
    else:
        print(f"\n[WARNING] 找不到：{sources['wikt']}")

    # 讀取聖經詞彙
    if sources['bible'].exists():
        print(f"\n讀取聖經詞彙：{sources['bible'].name}")
        bible_entries = read_dict_entries(sources['bible'])
        new_count = 0
        for (hanzi, pinyin), weight in bible_entries.items():
            if (hanzi, pinyin) not in all_entries:
                # 聖經詞彙權重較低（避免覆蓋標準詞彙）
                all_entries[(hanzi, pinyin)] = min(weight, 300)
                new_count += 1
        print(f"  詞條數：{len(bible_entries)}")
        print(f"  新增：{new_count}")
    else:
        print(f"\n[WARNING] 找不到：{sources['bible']}")

    # 寫入合併後的詞庫
    print(f"\n寫入合併詞庫：{output_file.name}")
    write_dict_file(output_file, all_entries, "borhlang_pouleng", "莆仙話拼音詞庫（莆田話）")
    print(f"[OK] 完成！總詞條數：{len(all_entries)}")


def read_dict_entries(file_path: Path) -> dict:
    """讀取詞典條目"""
    entries = {}

    with open(file_path, 'r', encoding='utf-8') as f:
        in_header = True
        for line in f:
            line = line.strip()

            # 跳過標頭
            if in_header:
                if line == '...':
                    in_header = False
                continue

            # 跳過空行和註釋
            if not line or line.startswith('#'):
                continue

            # 解析詞條
            parts = line.split('\t')
            if len(parts) >= 2:
                hanzi = parts[0]
                pinyin = parts[1]

                # 處理權重（可能是數字、百分比、或空白）
                if len(parts) >= 3:
                    weight_str = parts[2].strip()
                    if weight_str.endswith('%'):
                        # 百分比格式：90% -> 90
                        try:
                            weight = int(weight_str[:-1])
                        except ValueError:
                            weight = 500
                    elif weight_str:
                        try:
                            weight = int(weight_str)
                        except ValueError:
                            weight = 500
                    else:
                        weight = 500
                else:
                    weight = 500

                entries[(hanzi, pinyin)] = weight

    return entries


def write_dict_file(file_path: Path, entries: dict, name: str, description: str):
    """寫入詞典檔案"""
    with open(file_path, 'w', encoding='utf-8') as f:
        # 寫入標頭
        f.write("# Rime dictionary\n")
        f.write("# encoding: utf-8\n")
        f.write("#\n")
        f.write(f"# {description}\n")
        f.write("#\n")
        f.write("# 本詞庫由多個來源合併而成：\n")
        f.write("# - 基礎詞庫（人工整理）\n")
        f.write("# - 維基詞典（自動提取）\n")
        f.write("# - 聖經文本（自動提取）\n")
        f.write("#\n")
        f.write("---\n")
        f.write(f"name: {name}\n")
        f.write('version: "0.4.0"\n')
        f.write("use_preset_vocabulary: false\n")
        f.write("sort: by_weight\n")
        f.write("...\n\n")

        # 按權重排序
        sorted_entries = sorted(entries.items(), key=lambda x: x[1], reverse=True)

        # 寫入詞條
        for (hanzi, pinyin), weight in sorted_entries:
            f.write(f"{hanzi}\t{pinyin}\t{weight}\n")


def main():
    """主函數"""
    base_dir = Path(__file__).parent.parent
    tools_dir = base_dir / "tools"

    print("=" * 70)
    print("  木蘭輸入法詞表一鍵更新工具")
    print("  Borhlang IME - Dictionary Build Tool")
    print("=" * 70)

    steps = [
        # 步驟1：從維基詞典提取
        {
            'script': tools_dir / "extract_vocab_from_wikt.py",
            'description': "步驟 1/5：從維基詞典提取詞彙",
            'optional': True
        },
        # 步驟2：從聖經提取
        {
            'script': tools_dir / "extract_vocab_from_bible.py",
            'description': "步驟 2/5：從聖經文本提取詞彙",
            'optional': True
        },
    ]

    # 執行提取腳本
    for step in steps:
        if step['script'].exists():
            success = run_script(step['script'], step['description'])
            if not success and not step.get('optional', False):
                print(f"\n[ERROR] 關鍵步驟失敗，終止流程")
                return 1
        else:
            print(f"\n[WARNING] 找不到腳本：{step['script']}")
            if not step.get('optional', False):
                return 1

    # 步驟3：合併詞彙
    try:
        merge_vocabularies(base_dir)
    except Exception as e:
        print(f"\n[ERROR] 合併詞彙失敗：{e}")
        import traceback
        traceback.print_exc()
        return 1

    # 步驟4：轉換為平話字詞表（漢字版）
    convert_script = tools_dir / "convert_dict_v3.py"
    if convert_script.exists():
        success = run_script(convert_script, "步驟 4/5：轉換為平話字詞表（漢字版）")
        if not success:
            print(f"\n[ERROR] 轉換失敗")
            return 1
    else:
        print(f"\n[WARNING] 找不到轉換腳本：{convert_script}")

    # 步驟5：生成純平話字詞表（Lua格式）
    generate_script = tools_dir / "generate_pure_bannuaci_dict.py"
    if generate_script.exists():
        success = run_script(generate_script, "步驟 5/5：生成純平話字詞表（Lua格式）")
        if not success:
            print(f"\n[ERROR] 生成失敗")
            return 1
    else:
        print(f"\n[WARNING] 找不到生成腳本：{generate_script}")

    # 完成
    print("\n" + "=" * 70)
    print("[SUCCESS] 所有詞表更新完成！")
    print("=" * 70)
    print("\n生成的檔案：")
    print("  1. pouseng_pipping/borhlang_pouleng.dict.yaml - 莆仙話拼音詞庫（合併版）")
    print("  2. bannuaci/borhlang_bannuaci_han.dict.yaml - 平話字詞庫（漢字版）")
    print("  3. bannuaci/borhlang_bannuaci.dict.yaml - 平話字詞庫（純羅馬字+Lua格式）")
    print("\n請檢查 bannuaci/conversion_log.txt 查看轉換警告")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
